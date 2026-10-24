"""Bot público de Telegram: responde comandos sobre el radar del dólar.

Cualquiera puede escribirle. Responde con datos públicos (mindicador.cl, FRED) y cálculos
descriptivos; nunca con recomendaciones personales.

Privacidad: no se guarda quién escribe. Lo único persistente es el offset de Telegram
(data/bot.json). Los límites por chat viven en memoria durante la corrida.

Ejecución: GitHub Actions cada 30 minutos (`radar bot --una-vez`) o en local (`radar bot`).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from . import almacen, grafico, metricas, reporte, telegram
from .backtest import backtest
from .cli import _avisos
from .senales import SERIES, calcular

ARCHIVO_BOT = Path("data/bot.json")
CONSULTAS_POR_VENTANA = 5  # por chat
VENTANA_SEGUNDOS = 600
MENSAJES_POR_CORRIDA = 100  # tope total: acota el tiempo de Actions
ESPERA_LARGA = 25  # segundos de long polling en modo local

COMANDOS: dict[str, tuple] = {}  # nombre -> (función, descripción)


def comando(nombre: str, descripcion: str):
    def registrar(f):
        COMANDOS[nombre] = (f, descripcion)
        return f
    return registrar


@dataclass
class Respuesta:
    texto: str
    archivos: list[tuple[str, Path]] = field(default_factory=list)  # ("documento" | "foto", ruta)


def interpretar(texto: str) -> tuple[str, str]:
    """'/estado@RadarBot  x' -> ('estado', 'x'). Acepta también la palabra sin barra."""
    primera, _, resto = texto.strip().lstrip("/").partition(" ")
    return primera.split("@")[0].lower(), resto.strip()


def _datos():
    df = almacen.tabla(SERIES)
    if df.empty:
        raise RuntimeError("todavía no hay datos")
    senales = calcular(df)
    return df, senales, reporte.actual(senales, df["usdclp"])


@comando("ayuda", "lista de comandos")
def _ayuda(_args: str) -> Respuesta:
    lineas = ["Radar del dólar en Chile. Datos públicos (mindicador.cl y FRED).",
              "Describe lo que pasó; no es asesoría financiera ni predice con certeza.", ""]
    lineas += [f"/{nombre} — {descripcion}" for nombre, (_, descripcion) in COMANDOS.items()]
    url = os.environ.get("DASHBOARD_URL", "").strip()
    if url:
        lineas += ["", f"Panel completo: {url}"]
    return Respuesta("\n".join(lineas))


@comando("estado", "contexto del semáforo hoy (no es señal)")
def _estado(_args: str) -> Respuesta:
    _, _, a = _datos()
    return Respuesta(reporte.contexto_publico(a, _avisos()))


@comando("historia", "qué hizo el dólar después de cada estado")
def _historia(_args: str) -> Respuesta:
    df, s, _ = _datos()
    cal = metricas.calibracion(df["usdclp"], s["compuesto"])
    lineas = ["Qué hizo el dólar N meses después de días con cada estado.",
              "Porcentaje de días en que estaba más alto. Línea base = cualquier día.", ""]
    for nombre in metricas.HORIZONTES:
        lineas.append(nombre)
        for _, f in cal[cal["horizonte"] == nombre].iterrows():
            etiqueta = "Cualquier día (base)" if f["estado"] == "TODOS" else f["estado"].title()
            lineas.append(f" · {etiqueta}: {f['sube'] * 100:.0f}% subió · {int(f['dias'])} días "
                          f"(≈{int(f['episodios'])} episodios)")
        lineas.append("")
    lineas.append("Pocos episodios = poca evidencia.")
    return Respuesta("\n".join(lineas))


@comando("prediccion", "escenarios históricos desde hoy (rangos, no predicción)")
def _prediccion(_args: str) -> Respuesta:
    df, s, a = _datos()
    actual_estado = a["estado"]
    if actual_estado not in metricas.ESTADOS:
        return Respuesta("Sin estado actual: faltan datos para calcular escenarios.")
    cal = metricas.calibracion(df["usdclp"], s["compuesto"])
    precio = a["precio"]
    lineas = [f"Escenarios desde hoy · estado {actual_estado} · dólar ${reporte.num(precio)}",
              "Lo que pasó en días parecidos del pasado. Es un rango histórico, no una predicción.", ""]
    for nombre in metricas.HORIZONTES:
        f = cal[(cal["horizonte"] == nombre) & (cal["estado"] == actual_estado)]
        base = cal[(cal["horizonte"] == nombre) & (cal["estado"] == "TODOS")]
        if f.empty:
            continue
        f = f.iloc[0]
        lineas.append(f"En {nombre}: mediana ${reporte.num(precio * (1 + f['mediana']))}. "
                      f"El 80% de los casos quedó entre ${reporte.num(precio * (1 + f['p10']))} "
                      f"y ${reporte.num(precio * (1 + f['p90']))}.")
        if not base.empty:
            lineas.append(f"  Subió en {f['sube'] * 100:.0f}% de estos casos "
                          f"(cualquier día: {base.iloc[0]['sube'] * 100:.0f}%). ≈{int(f['episodios'])} episodios.")
    lineas += ["", "Si la probabilidad se parece a la de cualquier día, el estado no aporta información.",
               "Esto describe el pasado; no garantiza el futuro."]
    return Respuesta("\n".join(lineas))


@comando("grafico", "último año del dólar con el semáforo")
def _grafico(_args: str) -> Respuesta:
    df, s, _ = _datos()
    ruta = Path(tempfile.mkdtemp()) / "grafico.png"
    grafico.generar(df, s, ruta)
    return Respuesta("Último año del dólar y del semáforo.", [("foto", ruta)])


@comando("backtest", "radar vs DCA sobre toda la historia")
def _backtest(_args: str) -> Respuesta:
    df, s, _ = _datos()
    bt = backtest(df["usdclp"], s["compuesto"])
    if not bt:
        return Respuesta("Historia insuficiente para el backtest.")
    return Respuesta("\n".join([
        f"Historia {bt.desde} a {bt.hasta} ({bt.meses} meses).",
        f"DCA: {bt.usd_dca:,.2f} USD a ${bt.precio_dca:,.2f} por dólar.",
        f"Radar: {bt.usd_radar:,.2f} USD a ${bt.precio_radar:,.2f} por dólar.",
        f"Diferencia: {bt.mejora_pct:+.3f}% · mejor en {bt.meses_mejor} meses, peor en {bt.meses_peor}.",
        "Una diferencia pequeña no prueba que el radar sea mejor: el dato que importa es el fuera de muestra.",
    ]))


@comando("salud", "frescura y fallas de cada fuente")
def _salud(_args: str) -> Respuesta:
    s = metricas.salud(date.today())
    lineas = ["Estado de las fuentes (huecos = saltos de más de 4 días, feriados largos incluidos):"]
    for _, f in s.iterrows():
        if f["ultimo_dato"] is None:
            lineas.append(f" · {f['serie']}: sin datos")
            continue
        dias = int(f["dias_sin_dato"])
        lineas.append(f" · {f['serie']}: último dato {f['ultimo_dato']} ({dias} día{'s' if dias != 1 else ''}), "
                      f"huecos {int(f['huecos'])}, fallas seguidas {int(f['fallas_consecutivas'])}")
    return Respuesta("\n".join(lineas))


@comando("datos", "CSV de una serie; ejemplo: /datos usdclp")
def _datos_csv(args: str) -> Respuesta:
    serie = (args.split() or ["usdclp"])[0].lower()
    if serie not in SERIES:
        return Respuesta(f"Serie desconocida. Opciones: {', '.join(SERIES)}.")
    ruta = almacen.ruta(serie)
    if not ruta.exists():
        return Respuesta(f"La serie {serie} todavía no tiene datos.")
    return Respuesta(f"Serie {serie}: fecha, valor y fuente.", [("documento", ruta)])


def responder(mensaje: dict) -> Respuesta:
    nombre, args = interpretar(mensaje.get("text") or "")
    if not nombre:
        return Respuesta("Escribe /ayuda para ver los comandos.")
    if nombre in ("start", "help"):
        nombre = "ayuda"
    if nombre not in COMANDOS:
        return Respuesta(f"No conozco '{nombre}'. Escribe /ayuda.")
    try:
        return COMANDOS[nombre][0](args)
    except Exception as e:  # el detalle va al log del run; el chat recibe un texto genérico
        print(f"error en /{nombre}: {type(e).__name__}: {e}", file=sys.stderr)
        return Respuesta("No pude calcular eso ahora. Intenta más tarde.")


def _enviar(chat, r: Respuesta) -> None:
    telegram.mensaje(chat, r.texto)
    for tipo, ruta in r.archivos:
        (telegram.documento if tipo == "documento" else telegram.foto)(chat, ruta)


class Limite:
    """Cuántas consultas por chat en una ventana de tiempo. Solo en memoria."""

    def __init__(self, maximo: int = CONSULTAS_POR_VENTANA, ventana: float = VENTANA_SEGUNDOS):
        self.maximo, self.ventana = maximo, ventana
        self.tiempos: dict = defaultdict(deque)

    def admite(self, chat) -> bool:
        ahora = time.monotonic()
        cola = self.tiempos[chat]
        while cola and ahora - cola[0] > self.ventana:
            cola.popleft()
        if len(cola) >= self.maximo:
            return False
        cola.append(ahora)
        return True


def _leer_offset() -> int:
    return json.loads(ARCHIVO_BOT.read_text(encoding="utf-8")).get("offset", 0) if ARCHIVO_BOT.exists() else 0


def _guardar_offset(offset: int) -> None:
    ARCHIVO_BOT.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVO_BOT.write_text(json.dumps({"offset": offset}) + "\n", encoding="utf-8")


def ciclo(una_vez: bool) -> int:
    """Atiende los mensajes pendientes. Devuelve cuántos se respondieron."""
    offset = _leer_offset()
    limite = Limite()
    avisados: set = set()
    atendidos = 0
    while True:
        updates = telegram.actualizaciones(offset, espera=0 if una_vez else ESPERA_LARGA)
        for u in updates:
            offset = u["update_id"] + 1
            msg = u.get("message") or {}
            chat = (msg.get("chat") or {}).get("id")
            if chat is None or "text" not in msg or (msg.get("from") or {}).get("is_bot"):
                _guardar_offset(offset)
                continue
            if not limite.admite(chat):
                if chat not in avisados:
                    telegram.mensaje(chat, "Muchas consultas seguidas. Vuelve a intentar en unos minutos.")
                    avisados.add(chat)
                _guardar_offset(offset)
                continue
            try:
                _enviar(chat, responder(msg))
                atendidos += 1
            except telegram.TelegramError as e:
                print(f"no se pudo responder: {e}", file=sys.stderr)
            _guardar_offset(offset)
            if atendidos >= MENSAJES_POR_CORRIDA:
                return atendidos
        if una_vez:
            return atendidos

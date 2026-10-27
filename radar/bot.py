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
import subprocess
import sys
import tempfile
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd

from . import almacen, grafico, metricas, reporte, telegram
from .backtest import backtest
from .cli import _avisos
from .senales import SERIES, calcular

ARCHIVO_BOT = Path("data/bot.json")
CONSULTAS_POR_VENTANA = 5  # por chat
VENTANA_SEGUNDOS = 600
MENSAJES_POR_CORRIDA = 1000  # tope por corrida; la cadena de corridas sigue atendiendo
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


def _url() -> str:
    return os.environ.get("DASHBOARD_URL", "").strip()


@comando("ayuda", "lista de comandos")
def _ayuda(_args: str) -> Respuesta:
    lineas = ["Radar del dólar en Chile. Describe el pasado; no es asesoría financiera.", ""]
    lineas += [f"/{nombre} · {descripcion}" for nombre, (_, descripcion) in COMANDOS.items()]
    if _url():
        lineas += ["", f"Panel: {_url()}"]
    return Respuesta("\n".join(lineas))


@comando("estado", "semáforo de hoy y qué dicen los datos")
def _estado(_args: str) -> Respuesta:
    df, s, a = _datos()
    bt = backtest(df["usdclp"], s["compuesto"])
    rendimiento = (bt.precio_radar / bt.precio_dca - 1) * 100 if bt else None
    return Respuesta(reporte.contexto_publico(a, almacen.ultimo_cierre(), rendimiento,
                                              str(bt.desde) if bt else "", _url(), _avisos()))


@comando("historia", "qué pasó 6 meses después de cada estado")
def _historia(_args: str) -> Respuesta:
    df, s, _ = _datos()
    cal = metricas.calibracion(df["usdclp"], s["compuesto"])
    h = cal[cal["horizonte"] == "6 meses"]
    base = h[h["estado"] == "TODOS"].iloc[0]
    lineas = ["A 6 meses, el dólar subió en (según el estado del semáforo ese día):"]
    for e in metricas.ESTADOS:
        f = h[h["estado"] == e]
        if not f.empty:
            f = f.iloc[0]
            lineas.append(f"· {e.title()}: {f['sube'] * 100:.0f}% de los días ({int(f['episodios'])} episodios)")
    lineas.append(f"· Cualquier día: {base['sube'] * 100:.0f}%")
    if int(h[h["estado"] != "TODOS"]["episodios"].min()) < 10:
        lineas += ["", "Hay estados con pocos episodios: no es concluyente."]
    return Respuesta("\n".join(lineas))


@comando("prediccion", "rango histórico a 6 meses desde hoy (no es predicción)")
def _prediccion(_args: str) -> Respuesta:
    df, s, a = _datos()
    cierre = almacen.ultimo_cierre()
    cal = metricas.calibracion(df["usdclp"], s["compuesto"])
    f = cal[(cal["horizonte"] == "6 meses") & (cal["estado"] == a["estado"])]
    if a["estado"] not in metricas.ESTADOS or f.empty or not cierre:
        return Respuesta("No hay casos históricos para el estado de hoy.")
    f, precio = f.iloc[0], cierre[1]
    return Respuesta("\n".join([
        f"Días {a['estado'].title()} como hoy, 6 meses después:",
        f"· Mediana: ${reporte.num(precio * (1 + f['mediana']))}",
        f"· En 8 de cada 10 casos, entre ${reporte.num(precio * (1 + f['p10']))} "
        f"y ${reporte.num(precio * (1 + f['p90']))}",
        "",
        "Es lo que pasó en el pasado, no lo que va a pasar.",
    ]))


@comando("grafico", "último año del dólar con el semáforo")
def _grafico(_args: str) -> Respuesta:
    df, s, _ = _datos()
    ruta = Path(tempfile.mkdtemp()) / "grafico.png"
    grafico.generar(df, s, ruta)
    return Respuesta("Último año del dólar y del semáforo.", [("foto", ruta)])


@comando("backtest", "radar frente a cuota fija mensual, sin costos")
def _backtest(_args: str) -> Respuesta:
    df, s, _ = _datos()
    bt = backtest(df["usdclp"], s["compuesto"])
    if not bt:
        return Respuesta("Historia insuficiente para el backtest.")
    dif = (bt.precio_radar / bt.precio_dca - 1) * 100
    return Respuesta("\n".join([
        f"Desde {reporte.mes_anio(str(bt.desde))} ({bt.meses} meses), sin costos:",
        f"· Radar: ${reporte.num(bt.precio_radar)} por dólar",
        f"· Cuota fija mensual: ${reporte.num(bt.precio_dca)} por dólar",
        f"· El radar pagó {reporte.num(abs(dif), 2)}% {'más' if dif > 0 else 'menos'}.",
        "",
        "No incluye costos de cambio. No prueba ventaja futura.",
    ]))


@comando("salud", "¿están los datos al día?")
def _salud(_args: str) -> Respuesta:
    s = metricas.salud(date.today())
    s = s.assign(limite=s["serie"].map(almacen.antiguedad_max))
    ok = s["dias_sin_dato"].notna() & (s["dias_sin_dato"] <= s["limite"])
    lineas = [f"Fuentes al día: {int(ok.sum())} de {len(s)}."]
    for _, f in s[~ok].iterrows():
        if pd.isna(f["dias_sin_dato"]):
            lineas.append(f"· {f['serie']}: sin datos")
        else:
            lineas.append(f"· {f['serie']}: último dato hace {int(f['dias_sin_dato'])} días "
                          f"(máximo {int(f['limite'])})")
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


def _publicar_offset() -> None:
    """Versiona data/bot.json para que el progreso sea visible en el repo al instante.

    Un commit por consulta. Si el push falla, el offset local queda y el siguiente push lo incluye.
    """
    try:
        subprocess.run(["git", "add", str(ARCHIVO_BOT)], check=True)
        if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode == 0:
            return
        subprocess.run(["git", "commit", "-q", "-m", f"bot: consulta respondida {time.strftime('%Y-%m-%d-%H%M%S')}"],
                       check=True)
        if subprocess.run(["git", "push", "-q"]).returncode != 0:
            subprocess.run(["git", "pull", "--rebase", "-X", "theirs", "-q"], check=True)
            subprocess.run(["git", "push", "-q"], check=True)
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"no se pudo publicar el offset: {e}", file=sys.stderr)


def ciclo(una_vez: bool, durante: float = 0, publicar: bool = False) -> int:
    """Atiende mensajes. Devuelve cuántos se respondieron.

    `durante` (segundos) hace long polling hasta ese plazo: así una corrida responde en segundos
    en lugar de esperar al próximo cron. `una_vez` procesa lo pendiente y termina.
    """
    offset = _leer_offset()
    limite = Limite()
    avisados: set = set()
    atendidos = 0
    fin = time.monotonic() + durante if durante else None
    while True:
        if fin is not None and time.monotonic() >= fin:
            return atendidos
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
            except telegram.TelegramError as e:
                if not e.permanente:
                    # Fallo transitorio: el offset no avanza y el mensaje se reintenta en la próxima corrida.
                    print(f"no se pudo responder al update {u['update_id']}: {e}", file=sys.stderr)
                    return atendidos
                # Error permanente (p. ej. el chat bloqueó al bot): se descarta. Si se reintentara, ese único
                # update frenaría la cola de todos los demás en cada corrida.
                print(f"update {u['update_id']} descartado: {e}", file=sys.stderr)
            else:
                atendidos += 1
                # Registro sin contenido: el log de Actions es público en este repo.
                print(f"update {u['update_id']}: /{interpretar(msg.get('text') or '')[0] or '-'} respondido")
            _guardar_offset(offset)
            if publicar:
                _publicar_offset()
            if atendidos >= MENSAJES_POR_CORRIDA:
                return atendidos
        if una_vez:
            return atendidos

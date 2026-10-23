"""Línea de comandos: radar <actualizar|senales|resumen|alerta|backtest|prueba-telegram>."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from . import almacen, investigacion, reporte, telegram
from .actualizar import actualizar
from .backtest import backtest
from .senales import DEFINICIONES, SERIES, calcular

DIR_REPORTES = Path("reports")


def _cargar():
    df = almacen.tabla(SERIES)
    if df.empty:
        sys.exit("No hay datos: ejecuta primero `radar actualizar`.")
    senales = calcular(df)
    return df, senales, reporte.actual(senales, df["usdclp"])


def _salida(texto: str, enviar: bool, silencioso: bool = False) -> None:
    print(texto)
    if enviar:
        telegram.enviar(texto, silencioso=silencioso)
        print("\n[enviado a Telegram]")


def cmd_actualizar(_: argparse.Namespace) -> int:
    r = actualizar()
    for serie, n in sorted(r.cambios.items()):
        print(f"{serie}: {n} fechas nuevas o revisadas")
    for a in r.avisos:
        print(f"AVISO {a}")
    for e in r.errores:
        print(f"ERROR {e}")
    est = reporte.leer_estado()
    est["ultima_actualizacion"] = {"fecha": date.today().isoformat(), "errores": r.errores, "avisos": r.avisos}
    reporte.guardar_estado(est)
    # Falla el job solo si no se pudo actualizar nada: un error parcial se informa en el resumen.
    return 1 if r.errores and not r.cambios else 0


def _avisos() -> list[str]:
    u = reporte.leer_estado().get("ultima_actualizacion", {})
    return [*u.get("errores", []), *u.get("avisos", [])]


def cmd_senales(_: argparse.Namespace) -> int:
    _, _, a = _cargar()
    print(reporte.resumen(a, None, _avisos()))
    return 0


def cmd_backtest(_: argparse.Namespace) -> int:
    df, senales, _ = _cargar()
    bt = backtest(df["usdclp"], senales["compuesto"])
    if not bt:
        print("Historia insuficiente para el backtest.")
        return 0
    print(f"{bt.desde} a {bt.hasta} · {bt.meses} meses")
    print(f"DCA:   {bt.usd_dca:,.2f} USD · ${bt.precio_dca:,.2f} por dólar")
    print(f"Radar: {bt.usd_radar:,.2f} USD · ${bt.precio_radar:,.2f} por dólar")
    print(f"Mejora: {bt.mejora_pct:+.3f}% · mejor en {bt.meses_mejor} meses, peor en {bt.meses_peor}")
    # Diagnóstico: cada señal sola como compuesto. Sirve para saber cuál aporta; no para elegir pesos
    # con la misma historia (eso sería sobreajustar el backtest).
    print("\nCada señal por sí sola (mismo umbral):")
    for nombre, d in DEFINICIONES.items():
        if nombre in senales:
            r = backtest(df["usdclp"], senales[nombre])
            if r:
                print(f"  {d.titulo:<48} {r.mejora_pct:+.3f}%  ({r.meses} meses, mejor {r.meses_mejor} / peor {r.meses_peor})")
    return 0


def cmd_resumen(args: argparse.Namespace) -> int:
    df, senales, a = _cargar()
    bt = backtest(df["usdclp"], senales["compuesto"])
    wf = investigacion.walk_forward(investigacion.preparar(df["usdclp"], senales))
    base = wf["prueba"]["DCA (todo el día 1)"]
    prueba = [("timing v0.1", investigacion.mejora_pct(wf["prueba"][investigacion.RadarV01.nombre], base)),
              ("acumular si caro", investigacion.mejora_pct(wf["prueba"][wf["elegida"].nombre], base))]
    texto = reporte.resumen(a, bt, _avisos(), prueba)
    DIR_REPORTES.mkdir(exist_ok=True)
    (DIR_REPORTES / "ultimo-resumen.txt").write_text(texto + "\n", encoding="utf-8")
    _salida(texto, args.enviar)
    return 0


def cmd_alerta(args: argparse.Namespace) -> int:
    """Avisa solo si el semáforo cambió respecto de la última vez (o si fallan fuentes por primera vez)."""
    _, _, a = _cargar()
    est = reporte.leer_estado()
    anterior = est.get("estado")
    errores = est.get("ultima_actualizacion", {}).get("errores", [])
    mensajes = []
    if a["estado"] != anterior:
        mensajes.append(reporte.alerta(a, anterior))
    if errores and errores != est.get("errores_avisados"):
        mensajes.append("⚠️ Radar Dólar: fuentes con error\n" + "\n".join(errores))
    if not mensajes:
        print(f"Sin cambios: {a['estado']} ({a['fecha']}).")
    for m in mensajes:
        _salida(m, args.enviar)
    # Se guarda DESPUÉS de enviar: si Telegram falla, el próximo run vuelve a avisar.
    est.update({"estado": a["estado"], "fecha": a["fecha"], "compuesto": a["compuesto"], "errores_avisados": errores})
    reporte.guardar_estado(est)
    return 0


def cmd_investigar(_: argparse.Namespace) -> int:
    """Walk-forward (#9/#10): parámetros elegidos con el diseño, resultado medido en la prueba."""
    df, senales, _ = _cargar()
    wf = investigacion.walk_forward(investigacion.preparar(df["usdclp"], senales))
    lineas = ["# Investigación walk-forward (generado por `radar investigar`)", "",
              f"Corte: diseño < {investigacion.CORTE.date()} <= prueba. Parámetros elegidos solo con diseño.",
              f"Estrategia elegida: **{wf['elegida'].nombre}** (en diseño: {wf['mejora_diseno']:+.3f}% vs DCA)", ""]
    for periodo in ("diseno", "prueba"):
        res = wf[periodo]
        base = next(iter(res.values()))
        lineas += [f"## {'Diseño (sobreajustado por construcción)' if periodo == 'diseno' else 'Prueba (lo que importa)'}"
                   f" · {base.desde} a {base.hasta}, {base.meses} meses", "",
                   "| Estrategia | CLP por dólar | vs DCA | Máx. meses sin comprar | Máx. caja (cuotas) |",
                   "|---|---|---|---|---|"]
        for r in res.values():
            lineas.append(f"| {r.estrategia} | {r.precio_medio:,.2f} | {investigacion.mejora_pct(r, base):+.3f}% "
                          f"| {r.max_meses_sin_comprar} | {r.max_caja_cuotas:.0f} |")
        lineas.append("")
    texto = "\n".join(lineas)
    DIR_REPORTES.mkdir(exist_ok=True)
    (DIR_REPORTES / "investigacion.md").write_text(texto + "\n", encoding="utf-8")
    print(texto)
    return 0


def cmd_prueba(_: argparse.Namespace) -> int:
    telegram.enviar("✅ Radar Dólar Chile: conexión con Telegram funcionando.")
    print("Mensaje de prueba enviado.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="radar", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("actualizar", help="descarga series y guarda data/series/*.csv").set_defaults(f=cmd_actualizar)
    sub.add_parser("senales", help="muestra el estado actual").set_defaults(f=cmd_senales)
    sub.add_parser("backtest", help="radar vs DCA sobre la historia").set_defaults(f=cmd_backtest)
    for nombre, f, ayuda in (("resumen", cmd_resumen, "resumen semanal"), ("alerta", cmd_alerta, "aviso si cambia el estado")):
        sp = sub.add_parser(nombre, help=ayuda)
        sp.add_argument("--enviar", action="store_true", help="enviar a Telegram")
        sp.set_defaults(f=f)
    sub.add_parser("investigar", help="walk-forward: diseño hasta 2019, prueba desde 2020").set_defaults(f=cmd_investigar)
    sub.add_parser("prueba-telegram", help="envía un mensaje de prueba").set_defaults(f=cmd_prueba)
    args = p.parse_args(argv)
    try:
        return args.f(args)
    except telegram.TelegramError as e:
        print(f"ERROR Telegram: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

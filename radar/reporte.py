"""Textos para Telegram y para reports/: resumen semanal y alerta de cambio de estado."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

from .backtest import ResultadoBacktest
from .senales import DEFINICIONES, UMBRAL, estado

ARCHIVO_ESTADO = Path("data/estado.json")

ICONO = {"COMPRAR": "🟢", "NEUTRAL": "🟡", "ESPERAR": "🔴", "SIN DATOS": "⚪"}
CONSEJO = {
    "COMPRAR": "Buen momento: compra ahora la mitad táctica de tu cuota del mes.",
    "NEUTRAL": "Mantén la mitad táctica en pesos; si no aparece COMPRAR, cómprala el último día hábil del mes.",
    "ESPERAR": "Dólar caro según las señales: mantén la mitad táctica en pesos hasta COMPRAR o fin de mes.",
    "SIN DATOS": "Sin señal confiable hoy: sigue tu compra mensual fija.",
}
REGLA = "Regla: 50% de la cuota el primer día hábil del mes; 50% al primer COMPRAR o el último día hábil."
PIE = "Fuentes: mindicador.cl (dólar observado, cobre, TPM) y FRED (DXY, Fed, VIX). Herramienta personal; no es asesoría financiera."


def num(x: float, dec: int = 2) -> str:
    """Formato chileno: 1.234,56"""
    return f"{x:,.{dec}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(x: float, dec: int = 1) -> str:
    return f"{'+' if x >= 0 else '−'}{num(abs(x) * 100, dec)}%"


def _ok(x) -> bool:
    return x is not None and isinstance(x, int | float) and math.isfinite(x)


def explicacion(nombre: str, fila: pd.Series) -> str:
    g = fila.get
    if nombre == "valor_justo" and _ok(g("desvio_pct")):
        caro = "caro" if g("desvio_pct") > 0 else "barato"
        return f"dólar {pct(abs(g('desvio_pct')))} {caro} vs su valor justo de ${num(g('justo'))}"
    if nombre == "valoracion" and _ok(g("percentil_1a")):
        return f"percentil {g('percentil_1a') * 100:.0f} de los últimos 12 meses (0 = mínimo, 100 = máximo)"
    if nombre == "cobre" and _ok(g("cobre_3m")):
        return f"cobre {pct(g('cobre_3m'))} en 3 meses"
    if nombre == "dxy" and _ok(g("dxy_3m")):
        return f"dólar global {pct(g('dxy_3m'))} en 3 meses"
    if nombre == "tasas" and _ok(g("diferencial")) and _ok(g("diferencial_6m")):
        signo = "+" if g("diferencial_6m") >= 0 else "−"
        return f"TPM − Fed = {num(g('diferencial'))} pts ({signo}{num(abs(g('diferencial_6m')))} en 6 meses)"
    if nombre == "riesgo" and _ok(g("vix_z")):
        return f"VIX {'sobre' if g('vix_z') > 0 else 'bajo'} su media anual ({num(g('vix_z'), 1)} desv.)"
    return "sin datos"


def actual(senales: pd.DataFrame, precios: pd.Series) -> dict:
    ultima = senales.dropna(subset=["compuesto"]).index.max() if senales["compuesto"].notna().any() else None
    fila = senales.loc[ultima] if ultima is not None else senales.iloc[-1]
    comp = float(fila["compuesto"]) if ultima is not None else float("nan")
    return {
        "fecha": (ultima or senales.index.max()).date().isoformat(),
        "precio": float(precios.loc[ultima]) if ultima is not None else float(precios.iloc[-1]),
        "compuesto": comp,
        "estado": estado(comp),
        "fila": fila,
    }


def lineas_senales(fila: pd.Series) -> list[str]:
    out = []
    for nombre, d in DEFINICIONES.items():
        p = fila.get(nombre)
        if not _ok(p):
            out.append(f" · ——— {d.titulo}: sin datos")
            continue
        flecha = "▲" if p >= 0.1 else "▼" if p <= -0.1 else "•"
        out.append(f" {flecha} {'+' if p >= 0 else '−'}{num(abs(p))} {d.titulo}: {explicacion(nombre, fila)}")
    return out


def resumen(a: dict, bt: ResultadoBacktest | None, avisos: list[str]) -> str:
    fila = a["fila"]
    n, acuerdo = int(fila.get("n_senales", 0) or 0), int(fila.get("acuerdo", 0) or 0)
    partes = [
        f"💵 Radar Dólar Chile · datos al {a['fecha']}",
        f"Dólar observado: ${num(a['precio'])}",
        "",
        f"{ICONO[a['estado']]} {a['estado']} · puntaje {'+' if a['compuesto'] >= 0 else '−'}{num(abs(a['compuesto']))}"
        f" (umbral ±{num(UMBRAL)}) · {acuerdo} de {n} señales de acuerdo" if _ok(a["compuesto"]) else "⚪ SIN DATOS",
        CONSEJO[a["estado"]],
        "",
        "Señales (+ comprar / − esperar):",
        *lineas_senales(fila),
    ]
    if bt:
        veredicto = "más" if bt.mejora_pct >= 0 else "menos"
        partes += ["", f"📊 Backtest {bt.desde} a {bt.hasta} ({bt.meses} meses): el radar obtuvo "
                       f"{num(abs(bt.mejora_pct), 2)}% {veredicto} dólares que comprar fijo cada mes "
                       f"(mejor en {bt.meses_mejor}, peor en {bt.meses_peor} meses; "
                       f"${num(bt.precio_radar)} vs ${num(bt.precio_dca)} por dólar)."]
    if avisos:
        partes += ["", "⚠️ " + "\n⚠️ ".join(avisos)]
    partes += ["", REGLA, PIE]
    return "\n".join(partes)


def alerta(a: dict, anterior: str | None) -> str:
    return "\n".join([
        f"{ICONO[a['estado']]} Radar Dólar: {anterior or '—'} → {a['estado']}",
        f"Dólar observado ${num(a['precio'])} ({a['fecha']}) · puntaje "
        f"{'+' if a['compuesto'] >= 0 else '−'}{num(abs(a['compuesto']))}" if _ok(a["compuesto"]) else "",
        CONSEJO[a["estado"]],
        "",
        *lineas_senales(a["fila"]),
    ])


def leer_estado(ruta: Path = ARCHIVO_ESTADO) -> dict:
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}


def guardar_estado(datos: dict, ruta: Path = ARCHIVO_ESTADO) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

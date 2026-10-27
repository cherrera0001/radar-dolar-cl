"""Conciliación del dólar observado: BCCh (API oficial) frente a mindicador.cl (la fuente que alimenta las series).

Una diferencia puntual puede ser una revisión de la fuente. Por eso el aviso exige que la divergencia
se repita en los últimos DIAS_SEGUIDOS días comunes: es la señal de que una de las dos fuentes dejó de ser confiable.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from . import almacen
from .fuentes import bcentral

TOLERANCIA = 0.005  # 0,5 % relativo al valor de mindicador
DIAS_SEGUIDOS = 2
VENTANA_DIAS = 10  # días calendario que se consultan a BCCh en cada corrida


def _divergente(bcch: float, mind: float) -> bool:
    return abs(bcch - mind) / mind > TOLERANCIA


def aviso(bcch: dict[date, float], mindicador: dict[date, float]) -> str | None:
    """Aviso si los últimos DIAS_SEGUIDOS días comunes están divergentes. None en cualquier otro caso."""
    comunes = sorted(bcch.keys() & mindicador.keys())[-DIAS_SEGUIDOS:]
    if len(comunes) < DIAS_SEGUIDOS:
        return None
    if not all(_divergente(bcch[d], mindicador[d]) for d in comunes):
        return None
    fechas = ", ".join(d.isoformat() for d in comunes)
    return (f"🟠 usdclp: BCCh y mindicador difieren más de {TOLERANCIA * 100:g} % en {DIAS_SEGUIDOS} días "
            f"seguidos ({fechas}). Revisa cuál fuente tiene el dato correcto.")


def revisar(hoy: date, base: Path = almacen.DIR_SERIES) -> str | None:
    """Consulta BCCh (lanza FuenteError si falla o faltan credenciales) y devuelve el aviso, si lo hay."""
    desde = hoy - timedelta(days=VENTANA_DIAS)
    oficial = {p.fecha: p.valor for p in bcentral.descargar("usdclp", desde, hoy)}
    guardado = almacen.leer("usdclp", base)
    mindicador = {ts.date(): float(v) for ts, v in guardado.items() if ts.date() >= desde}
    return aviso(oficial, mindicador)

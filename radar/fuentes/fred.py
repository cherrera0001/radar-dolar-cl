"""FRED (Reserva Federal de St. Louis): dólar global, tasa de la Fed y VIX.

Contrato medido el 2026-10-23 contra https://fred.stlouisfed.org/graph/fredgraph.csv?id=<ID>
(sin API key):

    observation_date,DTWEXBGS
    2006-01-02,101.4155

Los días sin dato vienen con "." o vacíos y se omiten. Si en vez del CSV llega
una página HTML (mantención, bloqueo), el encabezado no calza y se rechaza.
"""

from __future__ import annotations

import csv
import io
from datetime import date

from .base import FuenteError, Punto, http_get, validar_valor

FUENTE = "FRED"
URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"

# serie interna -> ID en FRED
SERIES: dict[str, str] = {
    "dxy": "DTWEXBGS",  # Nominal Broad U.S. Dollar Index
    "fed_funds": "DFF",  # Federal Funds Effective Rate
    "vix": "VIXCLS",  # CBOE Volatility Index
}


def leer_csv(texto: str, serie: str, desde: date | None = None) -> list[Punto]:
    fred_id = SERIES[serie]
    filas = list(csv.reader(io.StringIO(texto)))
    if not filas or [c.strip() for c in filas[0]] != ["observation_date", fred_id]:
        raise FuenteError(f"{FUENTE}/{fred_id}: encabezado inesperado: {filas[0] if filas else 'vacío'}")
    puntos = []
    for fila in filas[1:]:
        if len(fila) != 2:
            raise FuenteError(f"{FUENTE}/{fred_id}: fila malformada: {fila!r}")
        texto_fecha, texto_valor = fila[0].strip(), fila[1].strip()
        if texto_valor in ("", "."):
            continue
        try:
            dia = date.fromisoformat(texto_fecha)
            valor = float(texto_valor)
        except ValueError as e:
            raise FuenteError(f"{FUENTE}/{fred_id}: fila ilegible: {fila!r}") from e
        if desde and dia < desde:
            continue
        puntos.append(Punto(serie, dia, validar_valor(serie, valor), FUENTE))
    if not puntos:
        raise FuenteError(f"{FUENTE}/{fred_id}: sin observaciones")
    return puntos


def descargar(serie: str, desde: date | None = None) -> list[Punto]:
    crudo = http_get(f"{URL}?id={SERIES[serie]}", timeout=60)
    return leer_csv(crudo.decode("utf-8", errors="replace"), serie, desde)

"""Tipos y utilidades comunes a todas las fuentes."""

from __future__ import annotations

import math
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date

USER_AGENT = "radar-dolar-cl/0.1 (+https://github.com/cherrera0001/radar-dolar-cl)"

# Rangos de cordura por serie. Un valor fuera de rango es un error de la fuente,
# no un dato: es preferible no tener precio a guardar uno imposible.
RANGOS: dict[str, tuple[float, float]] = {
    "usdclp": (300.0, 2500.0),  # pesos por dólar (dólar observado)
    "cobre_lb": (0.3, 30.0),  # dólares por libra
    "tpm": (0.0, 50.0),  # tasa de política monetaria Chile, %
    "dxy": (50.0, 250.0),  # índice amplio del dólar (Fed, ene-2006 = 100)
    "fed_funds": (0.0, 25.0),  # tasa de fondos federales, %
    "vix": (5.0, 150.0),  # volatilidad implícita S&P 500
}


class FuenteError(Exception):
    """La fuente respondió algo que no cumple su contrato."""


@dataclass(frozen=True)
class Punto:
    serie: str
    fecha: date
    valor: float
    fuente: str


def validar_valor(serie: str, valor: object) -> float:
    """Devuelve el valor como float o lanza FuenteError explicando por qué no sirve."""
    if isinstance(valor, bool) or not isinstance(valor, int | float):
        raise FuenteError(f"{serie}: el valor no es numérico: {valor!r}")
    v = float(valor)
    if not math.isfinite(v):
        raise FuenteError(f"{serie}: el valor no es finito: {valor!r}")
    minimo, maximo = RANGOS[serie]
    if not minimo <= v <= maximo:
        raise FuenteError(f"{serie}: {v} fuera del rango de cordura [{minimo}, {maximo}]")
    return v


def http_get(url: str, timeout: float = 30.0) -> bytes:
    """GET simple. Un error HTTP o de red se convierte en FuenteError."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (URLs fijas https)
            return resp.read()
    except (urllib.error.URLError, TimeoutError) as e:
        raise FuenteError(f"no se pudo leer {url.split('?')[0]}: {e}") from e

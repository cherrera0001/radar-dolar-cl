"""Tipos y utilidades comunes a todas las fuentes."""

from __future__ import annotations

import http.client
import math
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date

USER_AGENT = "radar-dolar-cl/0.1 (+https://github.com/cherrera0001/radar-dolar-cl)"
REINTENTOS = 2  # además del primer intento: 3 en total
ESPERA_BASE_SEGUNDOS = 2.0  # 2 s, luego 4 s: el job diario tiene margen de sobra

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
    """GET con reintentos para fallos transitorios (red, 5xx, cortes al leer).

    Un 4xx no se reintenta: la consulta está mal, no es un fallo de disponibilidad. Todo error de red
    o de lectura termina como FuenteError: ninguna excepción de bajo nivel debe escapar y cortar la
    actualización de las demás series.
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for intento in range(REINTENTOS + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (URLs fijas https)
                return resp.read()
        except (OSError, http.client.HTTPException) as e:  # URLError y TimeoutError son subclases de OSError
            reintentable = not (isinstance(e, urllib.error.HTTPError) and e.code < 500)
            if not reintentable or intento == REINTENTOS:
                raise FuenteError(f"no se pudo leer {url.split('?')[0]}: {e}") from e
        time.sleep(ESPERA_BASE_SEGUNDOS * 2 ** intento)
    raise AssertionError("inalcanzable: el bucle siempre devuelve o lanza")

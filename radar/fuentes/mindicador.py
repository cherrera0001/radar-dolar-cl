"""mindicador.cl: dólar observado, libra de cobre y TPM (series diarias por año).

Contrato medido el 2026-10-23 contra https://mindicador.cl/api/<codigo>/<año>:

    {"codigo": "dolar", "unidad_medida": "Pesos",
     "serie": [{"fecha": "2025-12-30T03:00:00.000Z", "valor": 911.18}, ...]}

La serie viene en orden descendente. La fecha es la medianoche de Santiago
expresada en UTC (03:00Z en verano, 04:00Z en invierno): el día UTC es el día
del valor.
"""

from __future__ import annotations

import json
import time
from datetime import datetime

from .base import ESPERA_BASE_SEGUNDOS, REINTENTOS, FuenteError, Punto, http_get, validar_valor

FUENTE = "mindicador.cl"
URL = "https://mindicador.cl/api"

# serie interna -> código en mindicador
SERIES: dict[str, str] = {
    "usdclp": "dolar",
    "cobre_lb": "libra_cobre",
    "tpm": "tpm",
}


def _dia(iso: object):
    if not isinstance(iso, str):
        raise FuenteError(f"fecha ausente o no es texto: {iso!r}")
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).date()
    except ValueError as e:
        raise FuenteError(f"fecha ilegible: {iso!r}") from e


def leer_serie(cuerpo: object, serie: str) -> list[Punto]:
    """Valida la respuesta de /api/<codigo>/<año> y devuelve los puntos.

    El contrato es el cuerpo, no el código HTTP: un 200 con un error dentro
    (como el {"Codigo": -5} del Banco Central) debe fallar aquí.
    """
    codigo = SERIES[serie]
    if not isinstance(cuerpo, dict):
        raise FuenteError(f"{FUENTE}/{codigo}: la respuesta no es un objeto JSON")
    if _error_del_servicio(cuerpo):
        raise FuenteError(f"{FUENTE}/{codigo}: {cuerpo.get('message') or cuerpo.get('error')}")
    if cuerpo.get("codigo") != codigo:
        raise FuenteError(f"{FUENTE}/{codigo}: 'codigo' inesperado: {cuerpo.get('codigo')!r}")
    filas = cuerpo.get("serie")
    if not isinstance(filas, list):
        raise FuenteError(f"{FUENTE}/{codigo}: falta la lista 'serie'")

    puntos = []
    for fila in filas:
        if not isinstance(fila, dict):
            raise FuenteError(f"{FUENTE}/{codigo}: fila que no es objeto: {fila!r}")
        puntos.append(Punto(serie, _dia(fila.get("fecha")), validar_valor(serie, fila.get("valor")), FUENTE))
    return puntos


def _error_del_servicio(cuerpo: dict) -> bool:
    """Un 200 con {"error": ..., "message": ...} en vez de la serie: es transitorio, se reintenta."""
    return "error" in cuerpo and "serie" not in cuerpo


def descargar(serie: str, anio: int) -> list[Punto]:
    for intento in range(REINTENTOS + 1):
        crudo = http_get(f"{URL}/{SERIES[serie]}/{anio}")
        try:
            cuerpo = json.loads(crudo)
        except json.JSONDecodeError as e:
            raise FuenteError(f"{FUENTE}/{SERIES[serie]}/{anio}: la respuesta no es JSON") from e
        if isinstance(cuerpo, dict) and _error_del_servicio(cuerpo) and intento < REINTENTOS:
            time.sleep(ESPERA_BASE_SEGUNDOS * 2 ** intento)
            continue
        return leer_serie(cuerpo, serie)
    raise AssertionError("inalcanzable: el último intento siempre devuelve o lanza")

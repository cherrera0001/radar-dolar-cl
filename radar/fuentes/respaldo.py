"""Respaldo de usdclp cuando mindicador.cl no responde (aprendizaje 2026-10-30).

ExchangeRate-API, capa gratuita sin clave: https://open.er-api.com/v6/latest/USD

    {"result": "success", "base_code": "USD",
     "time_last_update_utc": "Fri, 30 Oct 2026 00:02:31 +0000",
     "rates": {"CLP": 978.5, ...}}

Solo entrega la tasa más reciente (no hay historia en la capa gratuita): sirve para no
congelar la serie cuando mindicador.cl se cae, no para reconstruirla. Es una aproximación
al dólar observado, marcada con su propia fuente en el CSV. Términos:
https://www.exchangerate-api.com/terms — la atribución viaja en el campo fuente de cada punto.

Se desactiva con RADAR_USDCLP_RESPALDO=0 (por ejemplo, para medir solo mindicador en pruebas).
"""

from __future__ import annotations

import json
import os
from datetime import datetime

from .base import FuenteError, Punto, http_get, validar_valor

FUENTE = "er-api.com"
URL = "https://open.er-api.com/v6/latest/USD"


def activado(entorno=os.environ) -> bool:
    return entorno.get("RADAR_USDCLP_RESPALDO", "1") != "0"


def leer_respuesta(cuerpo: object) -> Punto:
    if not isinstance(cuerpo, dict):
        raise FuenteError(f"{FUENTE}: la respuesta no es un objeto JSON")
    if cuerpo.get("result") != "success":
        raise FuenteError(f"{FUENTE}: result inesperado: {cuerpo.get('result')!r}")
    tasas = cuerpo.get("rates")
    if not isinstance(tasas, dict) or not isinstance(tasas.get("CLP"), int | float):
        raise FuenteError(f"{FUENTE}: no viene la tasa CLP: {tasas.get('CLP') if isinstance(tasas, dict) else tasas!r}")
    actualizacion = cuerpo.get("time_last_update_utc")
    if not isinstance(actualizacion, str):
        raise FuenteError(f"{FUENTE}: fecha de actualización ausente: {actualizacion!r}")
    try:
        dia = datetime.strptime(actualizacion, "%a, %d %b %Y %H:%M:%S %z").date()
    except ValueError as e:
        raise FuenteError(f"{FUENTE}: fecha ilegible: {actualizacion!r}") from e
    return Punto("usdclp", dia, validar_valor("usdclp", tasas["CLP"]), FUENTE)


def descargar() -> list[Punto]:
    """El punto más reciente disponible (la capa gratuita no da historia)."""
    return [leer_respuesta(json.loads(http_get(URL)))]

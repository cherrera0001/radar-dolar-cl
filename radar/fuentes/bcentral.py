"""API BDE del Banco Central de Chile (requiere registro gratuito en si3.bcentral.cl).

Fase 2: se activa cuando existen las variables BCCH_USER y BCCH_PASS.

Contrato medido el 2026-10-23: con credenciales inválidas la API responde
HTTP 200 y un cuerpo de error:

    {"Codigo": -5, "Descripcion": "Invalid username or password", "Series": {...}}

Por eso solo `Codigo == 0` es éxito. Un `res.ok` guardaría el error como dato.
"""

from __future__ import annotations

import json
import os
import urllib.parse
from datetime import date, datetime

from .base import FuenteError, Punto, http_get, validar_valor

FUENTE = "bcentral.cl"
URL = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"

# serie interna -> código BDE. Se completa en la fase 2 tras explorar con buscar().
SERIES: dict[str, str] = {
    "usdclp": "F073.TCO.PRE.Z.D",  # dólar observado (contraste con mindicador)
}


def credenciales() -> tuple[str, str] | None:
    user, clave = os.environ.get("BCCH_USER"), os.environ.get("BCCH_PASS")
    return (user, clave) if user and clave else None


def _consultar(params: dict[str, str]) -> dict:
    cred = credenciales()
    if not cred:
        raise FuenteError(f"{FUENTE}: faltan BCCH_USER / BCCH_PASS")
    query = urllib.parse.urlencode({"user": cred[0], "pass": cred[1], **params})
    try:
        cuerpo = json.loads(http_get(f"{URL}?{query}", timeout=60))
    except json.JSONDecodeError as e:
        raise FuenteError(f"{FUENTE}: la respuesta no es JSON") from e
    return validar_cuerpo(cuerpo)


def validar_cuerpo(cuerpo: object) -> dict:
    if not isinstance(cuerpo, dict):
        raise FuenteError(f"{FUENTE}: la respuesta no es un objeto JSON")
    if cuerpo.get("Codigo") != 0:
        raise FuenteError(f"{FUENTE}: Codigo={cuerpo.get('Codigo')!r} {cuerpo.get('Descripcion')!r}")
    return cuerpo


def leer_serie(cuerpo: dict, serie: str) -> list[Punto]:
    obs = (cuerpo.get("Series") or {}).get("Obs")
    if not isinstance(obs, list):
        raise FuenteError(f"{FUENTE}/{SERIES[serie]}: falta Series.Obs")
    puntos = []
    for o in obs:
        if o.get("statusCode") != "OK":  # días sin dato (feriados)
            continue
        try:
            dia = datetime.strptime(o["indexDateString"], "%d-%m-%Y").date()
            valor = float(o["value"])
        except (KeyError, ValueError, TypeError) as e:
            raise FuenteError(f"{FUENTE}/{SERIES[serie]}: observación ilegible: {o!r}") from e
        puntos.append(Punto(serie, dia, validar_valor(serie, valor), FUENTE))
    return puntos


def descargar(serie: str, desde: date, hasta: date) -> list[Punto]:
    cuerpo = _consultar({
        "function": "GetSeries",
        "timeseries": SERIES[serie],
        "firstdate": desde.isoformat(),
        "lastdate": hasta.isoformat(),
    })
    return leer_serie(cuerpo, serie)


def buscar(frecuencia: str = "DAILY") -> list[dict]:
    """Catálogo de series (para elegir códigos en la fase 2)."""
    return _consultar({"function": "SearchSeries", "frequency": frecuencia}).get("SeriesInfos", [])

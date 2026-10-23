"""Series en CSV versionados en el repo: data/series/<serie>.csv (fecha,valor,fuente).

Git es la base de datos: cada actualización queda en el historial y es auditable.
"""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from .fuentes.base import Punto

DIR_SERIES = Path("data/series")

# Antigüedad máxima (días calendario) de un valor para usarlo en una fecha posterior.
# El DXY amplio de la Fed (H.10) sale una vez por semana con ~10 días de rezago.
TOLERANCIA_DIAS: dict[str, int] = {"dxy": 14}
TOLERANCIA_POR_DEFECTO = 7


def ruta(serie: str, base: Path = DIR_SERIES) -> Path:
    return base / f"{serie}.csv"


def leer(serie: str, base: Path = DIR_SERIES) -> pd.Series:
    """Serie diaria indexada por fecha (vacía si aún no existe)."""
    p = ruta(serie, base)
    if not p.exists():
        return pd.Series(dtype=float, name=serie)
    df = pd.read_csv(p, parse_dates=["fecha"])
    return df.set_index("fecha")["valor"].astype(float).rename(serie).sort_index()


def guardar(puntos: Iterable[Punto], base: Path = DIR_SERIES) -> dict[str, int]:
    """Fusiona puntos con lo existente (la fuente puede revisar valores: gana el nuevo).

    Devuelve cuántas fechas nuevas o modificadas hubo por serie.
    """
    por_serie: dict[str, dict] = {}
    for p in puntos:
        por_serie.setdefault(p.serie, {})[p.fecha.isoformat()] = (p.valor, p.fuente)

    cambios: dict[str, int] = {}
    base.mkdir(parents=True, exist_ok=True)
    for serie, nuevos in por_serie.items():
        actual: dict[str, tuple[float, str]] = {}
        p = ruta(serie, base)
        if p.exists():
            with p.open(newline="", encoding="utf-8") as f:
                for fila in csv.DictReader(f):
                    actual[fila["fecha"]] = (float(fila["valor"]), fila["fuente"])
        cambios[serie] = sum(1 for k, v in nuevos.items() if actual.get(k) != v)
        actual.update(nuevos)
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["fecha", "valor", "fuente"])
            for fecha in sorted(actual):
                valor, fuente = actual[fecha]
                w.writerow([fecha, repr(valor), fuente])
    return cambios


def tabla(series: Iterable[str], base: Path = DIR_SERIES) -> pd.DataFrame:
    """Une las series en días hábiles del dólar observado.

    Las demás series se alinean con el último valor conocido dentro de su
    tolerancia (TOLERANCIA_DIAS), para no inventar datos donde la fuente no publicó.
    """
    datos = {s: leer(s, base) for s in series}
    if "usdclp" not in datos or datos["usdclp"].empty:
        return pd.DataFrame()
    indice = datos["usdclp"].index
    return pd.DataFrame({
        s: v.reindex(indice, method="ffill",
                     tolerance=pd.Timedelta(days=TOLERANCIA_DIAS.get(s, TOLERANCIA_POR_DEFECTO)))
        for s, v in datos.items()
    })

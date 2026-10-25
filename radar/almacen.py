"""Series en CSV versionados en el repo: data/series/<serie>.csv (fecha,valor,fuente).

Git es la base de datos: cada actualización queda en el historial y es auditable.
"""

from __future__ import annotations

import csv
from collections.abc import Iterable
from datetime import date
from pathlib import Path

import pandas as pd

from .fuentes.base import Punto

DIR_SERIES = Path("data/series")

# Antigüedad máxima (días calendario) de un valor: se usa para alinear series y para
# avisar datos atrasados (radar/salud.py). Único lugar donde se define.
# El DXY amplio de la Fed (H.10) sale una vez por semana con ~10 días de rezago.
ANTIGUEDAD_MAX_DIAS: dict[str, int] = {"dxy": 14}
ANTIGUEDAD_POR_DEFECTO = 7


def antiguedad_max(serie: str) -> int:
    return ANTIGUEDAD_MAX_DIAS.get(serie, ANTIGUEDAD_POR_DEFECTO)


# Días hábiles entre la fecha con que la fuente guarda el dato y el día de mercado en que se formó
# (issue #19, medido en docs/HISTORICO.md §0):
# - usdclp: el BCCh publica el observado el día hábil anterior al día en que rige.
# - cobre_lb: mindicador lo fecha 2 días hábiles después del mercado (corr con DXY_{t-2}).
# Se usa el calendario hábil genérico (lun-vie): los feriados chilenos introducen error de ±1 día.
DESFASE_MERCADO: dict[str, int] = {"usdclp": 1, "cobre_lb": 2}


def a_fecha_mercado(serie: str, s: pd.Series) -> pd.Series:
    n = DESFASE_MERCADO.get(serie, 0)
    if not n or s.empty:
        return s
    s = s.copy()
    s.index = s.index - pd.offsets.BDay(n)
    return s[~s.index.duplicated(keep="last")]


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


def ultimo_cierre(serie: str = "usdclp", base: Path = DIR_SERIES) -> tuple[date, float] | None:
    """Último valor observado de la serie con su fecha real, sin el rezago de alineación del semáforo."""
    s = leer(serie, base).dropna()
    if s.empty:
        return None
    return s.index.max().date(), float(s.iloc[-1])


def tabla(series: Iterable[str], base: Path = DIR_SERIES) -> pd.DataFrame:
    """Une las series por DÍA DE MERCADO, en los días hábiles del dólar observado.

    Cada serie se reindexa a su fecha de mercado (DESFASE_MERCADO) y luego se alinea
    con el último valor conocido dentro de su antigüedad máxima, para no inventar
    datos donde la fuente no publicó. Una fila t contiene lo que pasó en el mercado
    el día t: quien decide en t solo debería usar filas <= t-1 (ver backtest).
    """
    datos = {s: a_fecha_mercado(s, leer(s, base)) for s in series}
    if "usdclp" not in datos or datos["usdclp"].empty:
        return pd.DataFrame()
    indice = datos["usdclp"].index
    return pd.DataFrame({
        s: v.reindex(indice, method="ffill", tolerance=pd.Timedelta(days=antiguedad_max(s)))
        for s, v in datos.items()
    })

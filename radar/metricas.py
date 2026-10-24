"""Cinco métricas descriptivas para el dashboard. Describen lo que pasó; no predicen.

1. calibracion:          qué hizo el dólar después de cada estado del semáforo, vs. cualquier día.
2. comparacion_acumulada: precio medio pagado por DCA y por el radar, mes a mes, fuera de muestra.
3. estacional:           variación mensual del dólar, año por mes.
4. correlacion:          correlación móvil del dólar con el cobre y con el dólar global (DXY).
5. salud:                frescura, huecos y fallas de cada serie.
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from . import almacen, investigacion
from .reporte import leer_estado
from .senales import DIAS_ANIO, SERIES, estado

HORIZONTES = {"3 meses": 63, "6 meses": 126, "12 meses": 252}  # días hábiles aprox.
ESTADOS = ["BARATO", "NORMAL", "CARO"]


def retornos_futuros(precios: pd.Series, horizonte: int) -> pd.Series:
    p = precios.dropna()
    return (p.shift(-horizonte) / p - 1).dropna()


def calibracion(precios: pd.Series, compuesto: pd.Series) -> pd.DataFrame:
    """Una fila por horizonte y estado, más 'TODOS' como línea base.

    Cada día cuenta como una observación, pero días vecinos comparten ventana de retorno:
    `episodios` (≈ días / horizonte) es el número realista de casos independientes.
    """
    estados = compuesto.dropna().map(estado)
    filas = []
    for nombre, h in HORIZONTES.items():
        j = pd.DataFrame({"estado": estados, "r": retornos_futuros(precios, h)}).dropna()
        for e in [*ESTADOS, "TODOS"]:
            r = j["r"] if e == "TODOS" else j.loc[j["estado"] == e, "r"]
            if r.empty:
                continue
            filas.append({
                "horizonte": nombre, "estado": e, "dias": len(r), "episodios": max(1, round(len(r) / h)),
                "sube": float((r > 0).mean()), "mediana": float(r.median()),
                "p10": float(r.quantile(0.1)), "p90": float(r.quantile(0.9)),
            })
    return pd.DataFrame(filas)


def comparacion_acumulada(preparado: pd.DataFrame, elegida: investigacion.Estrategia,
                          desde: pd.Timestamp = investigacion.CORTE) -> pd.DataFrame:
    """Precio medio (CLP por USD) de cada estrategia al cierre de cada mes del período de prueba.

    Para quien compra, menor es mejor. Cada punto simula desde `desde` hasta ese mes.
    """
    estrategias = [investigacion.DCA(), investigacion.RadarV01(), elegida]
    meses = preparado.loc[preparado.index >= desde].index.to_period("M").unique()
    filas = {}
    for mes in meses:
        hasta = mes.end_time.normalize() + pd.Timedelta(days=1)
        fila = {}
        for e in estrategias:
            r = investigacion.simular(preparado, e, desde=desde, hasta=hasta)
            # Sin compras todavía (período que empieza a mitad de mes): no hay precio medio.
            fila[e.nombre] = r.precio_medio if r and r.usd > 0 else float("nan")
        filas[mes.to_timestamp(how="end").normalize()] = fila
    return pd.DataFrame.from_dict(filas, orient="index")


def estacional(precios: pd.Series) -> pd.DataFrame:
    """Variación % mensual (cierre a cierre), con año en filas y mes en columnas."""
    mensual = precios.dropna().resample("ME").last()
    var = (mensual.pct_change() * 100).dropna()
    t = pd.DataFrame({"var": var, "anio": var.index.year, "mes": var.index.month})
    return t.pivot(index="anio", columns="mes", values="var")


def correlacion(df: pd.DataFrame, ventana: int = DIAS_ANIO) -> pd.DataFrame:
    """Correlación móvil de los retornos diarios del dólar con el cobre y con el DXY."""
    r = df[["usdclp", "cobre_lb", "dxy"]].pct_change(fill_method=None)
    return pd.DataFrame({
        "cobre": r["usdclp"].rolling(ventana).corr(r["cobre_lb"]),
        "dxy": r["usdclp"].rolling(ventana).corr(r["dxy"]),
    }).dropna(how="all")


def salud(hoy: date) -> pd.DataFrame:
    """Frescura, huecos y fallas consecutivas por serie. Los huecos son saltos de más de 4 días."""
    fallas = leer_estado().get("salud", {})
    filas = []
    for serie in SERIES:
        s = almacen.leer(serie)
        if s.empty:
            filas.append({"serie": serie, "ultimo_dato": None, "dias_sin_dato": None, "huecos": None,
                          "fallas_consecutivas": fallas.get(serie, {}).get("fallas", 0)})
            continue
        ultimo = s.index.max().date()
        filas.append({
            "serie": serie,
            "ultimo_dato": ultimo.isoformat(),
            "dias_sin_dato": (hoy - ultimo).days,
            "huecos": int((s.index.to_series().diff().dt.days > 4).sum()),
            "fallas_consecutivas": fallas.get(serie, {}).get("fallas", 0),
        })
    return pd.DataFrame(filas)

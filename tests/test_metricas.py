from datetime import date

import numpy as np
import pandas as pd
import pytest

from radar import investigacion, metricas


def _serie(n=800, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2019-01-01", periods=n)
    return pd.Series(900 * np.exp(np.cumsum(rng.normal(0, 0.006, n))), index=idx, name="usdclp")


def test_calibracion_separa_estados_y_linea_base():
    precios = _serie()
    comp = pd.Series(np.where(np.arange(len(precios)) % 2 == 0, 0.5, -0.5), index=precios.index)
    tabla = metricas.calibracion(precios, comp)
    assert set(tabla["estado"]) == {"BARATO", "CARO", "TODOS"}
    assert set(tabla["horizonte"]) == set(metricas.HORIZONTES)
    assert ((tabla["sube"] >= 0) & (tabla["sube"] <= 1)).all()


def test_retorno_futuro_simple():
    p = pd.Series([100.0, 110.0, 99.0], index=pd.bdate_range("2024-01-01", periods=3))
    r = metricas.retornos_futuros(p, 1)
    assert r.iloc[0] == pytest.approx(0.10)
    assert len(r) == 2


def test_estacional_pivot_año_por_mes():
    precios = _serie(n=900)
    piv = metricas.estacional(precios)
    assert piv.index.name == "anio"
    assert set(piv.columns) <= set(range(1, 13))
    assert piv.notna().any().any()


def test_correlacion_serie_con_si_misma_es_uno():
    df = pd.DataFrame({"usdclp": _serie(600), "cobre_lb": _serie(600, seed=1), "dxy": _serie(600, seed=2)})
    df["cobre_lb"] = df["usdclp"]  # misma serie => correlación 1 con el cobre
    c = metricas.correlacion(df, ventana=60)
    assert c["cobre"].dropna().iloc[-1] == pytest.approx(1.0)


def test_comparacion_acumulada_dos_estrategias_y_radar():
    df = pd.DataFrame({"usdclp": _serie(900)})
    senales = pd.DataFrame({"compuesto": np.zeros(len(df)), "desvio_pct": np.nan}, index=df.index)
    prep = investigacion.preparar(df["usdclp"], senales)
    comp = metricas.comparacion_acumulada(prep, investigacion.RadarV01(), desde=df.index[300])
    assert set(comp.columns) == {investigacion.DCA.nombre, investigacion.RadarV01.nombre}
    assert comp.iloc[-1].notna().all()


def test_salud_reporta_frescura():
    s = metricas.salud(date(2030, 1, 1))
    assert {"serie", "dias_sin_dato", "huecos", "fallas_consecutivas"} <= set(s.columns)

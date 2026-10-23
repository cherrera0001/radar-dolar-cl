import numpy as np
import pandas as pd
import pytest

from radar import investigacion as inv
from radar.backtest import backtest


def datos(semilla=3, desde="2014-01-01", hasta="2024-06-30"):
    rng = np.random.default_rng(semilla)
    idx = pd.bdate_range(desde, hasta)
    precio = pd.Series(800 * np.exp(np.cumsum(rng.normal(0, 0.006, len(idx)))), index=idx)
    senales = pd.DataFrame({"compuesto": rng.uniform(-1, 1, len(idx)),
                            "desvio_pct": rng.normal(0, 0.05, len(idx))}, index=idx)
    return precio, senales


def test_simulador_reproduce_el_backtest_v01_y_dca():
    precio, senales = datos()
    df = inv.preparar(precio, senales)
    bt = backtest(precio, senales["compuesto"])
    assert inv.simular(df, inv.DCA()).usd == pytest.approx(bt.usd_dca)
    assert inv.simular(df, inv.RadarV01()).usd == pytest.approx(bt.usd_radar)


def test_toda_estrategia_gasta_exactamente_el_presupuesto():
    precio, senales = datos()
    df = inv.preparar(precio, senales)
    nunca = inv.Acumulacion(max_cuotas=1000, entrada=-1.0, salida=-2.0)  # siempre "caro": nunca compra
    r = inv.simular(df, nunca)
    assert r.gasto == pytest.approx(inv.PRESUPUESTO * r.meses)  # el cierre convierte la caja


def test_acumulacion_respeta_su_tope_de_meses_sin_comprar():
    precio, senales = datos()
    df = inv.preparar(precio, senales.assign(desvio_pct=0.5))  # dólar siempre muy caro
    r = inv.simular(df, inv.Acumulacion(max_cuotas=3, entrada=0.05, salida=0.0))
    assert r.max_meses_sin_comprar <= 3
    assert r.max_caja_cuotas <= 4  # 3 guardadas + la del mes en que se fuerza la compra


def test_la_eleccion_de_parametros_no_ve_el_periodo_de_prueba():
    precio, senales = datos()
    df = inv.preparar(precio, senales)
    elegida, valor = inv.elegir_parametros(df)
    alterado = df.copy()
    prueba = alterado.index >= inv.CORTE
    alterado.loc[prueba, "precio"] *= np.random.default_rng(9).uniform(0.5, 1.5, prueba.sum())
    alterado.loc[prueba, "desvio"] = -alterado.loc[prueba, "desvio"]
    assert inv.elegir_parametros(alterado) == (elegida, valor)


def test_walk_forward_separa_periodos():
    precio, senales = datos()
    wf = inv.walk_forward(inv.preparar(precio, senales))
    assert all(r.hasta < "2020-01" for r in wf["diseno"].values())
    assert all(r.desde >= "2020-01" for r in wf["prueba"].values())

import pandas as pd
import pytest

from radar.backtest import backtest


def test_precio_constante_empata_con_dca():
    idx = pd.bdate_range("2024-01-01", "2024-12-31")
    precios = pd.Series(900.0, index=idx)
    r = backtest(precios, pd.Series(0.5, index=idx))
    assert r.mejora_pct == pytest.approx(0.0)
    assert r.meses == 11  # diciembre es el mes en curso de la serie: se excluye
    assert r.meses_mejor == r.meses_peor == 0


def test_comprar_en_la_caida_le_gana_a_dca():
    idx = pd.bdate_range("2024-01-01", "2024-03-31")
    precios = pd.Series(1000.0, index=idx)
    compuesto = pd.Series(0.0, index=idx)
    caida = idx[(idx.month == 1) & (idx.day >= 15)][0]
    precios[caida] = 800.0
    compuesto[caida] = 0.5  # la señal aparece justo el día barato
    r = backtest(precios, compuesto)
    # enero: 50 USD (mitad base a 1000) + 62,5 USD (mitad táctica a 800) vs 100 USD en DCA
    assert r.meses_mejor == 1
    assert r.usd_radar - r.usd_dca == pytest.approx(100_000 * 0.5 / 800 - 100_000 * 0.5 / 1000)


def test_sin_senal_compra_la_mitad_tactica_a_fin_de_mes():
    idx = pd.bdate_range("2024-01-01", "2024-02-29")
    precios = pd.Series(1000.0, index=idx)
    precios[idx[(idx.month == 1)][-1]] = 1250.0  # fin de enero caro y sin señal: el radar pierde
    r = backtest(precios, pd.Series(0.0, index=idx))
    assert r.meses == 1 and r.meses_peor == 1
    assert r.mejora_pct < 0


def test_meses_sin_senal_al_inicio_se_excluyen():
    idx = pd.bdate_range("2024-01-01", "2024-04-30")
    compuesto = pd.Series(0.0, index=idx)
    compuesto[idx.month == 1] = float("nan")  # período de calentamiento de las ventanas
    r = backtest(pd.Series(900.0, index=idx), compuesto)
    assert r.desde == "2024-02" and r.meses == 2

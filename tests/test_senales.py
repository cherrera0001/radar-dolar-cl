import numpy as np
import pandas as pd
import pytest

from radar.senales import calcular, estado, valor_justo


def mercado(n=900, semilla=7) -> pd.DataFrame:
    """Mercado sintético donde el dólar es exactamente función del cobre y del DXY."""
    rng = np.random.default_rng(semilla)
    idx = pd.bdate_range("2020-01-01", periods=n)
    cobre = 4.0 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    dxy = 115.0 * np.exp(np.cumsum(rng.normal(0, 0.003, n)))
    ruido = rng.normal(0, 0.002, n)
    usd = np.exp(7.0 - 0.6 * np.log(cobre) + 0.8 * np.log(dxy / 115.0) + ruido) * 1.0
    return pd.DataFrame({
        "usdclp": usd, "cobre_lb": cobre, "dxy": dxy,
        "tpm": 5.0, "fed_funds": 4.0, "vix": 18.0 + rng.normal(0, 1, n),
    }, index=idx)


def test_valor_justo_detecta_dolar_barato_respecto_de_sus_fundamentos():
    df = mercado()
    df.iloc[-1, df.columns.get_loc("usdclp")] *= 0.95  # el dólar cae 5% sin que cambien cobre ni DXY
    vj = valor_justo(df)
    assert vj["desvio_pct"].iloc[-1] == pytest.approx(-0.05, abs=0.01)
    assert calcular(df)["valor_justo"].iloc[-1] == 1.0  # saturado a favor de comprar


def test_valor_justo_es_fuera_de_muestra_y_no_ve_el_futuro():
    df = mercado()
    base = valor_justo(df)["justo"].iloc[:850]
    alterado = df.copy()
    alterado.iloc[850:, alterado.columns.get_loc("usdclp")] *= 1.5  # cambia solo el futuro
    assert valor_justo(alterado)["justo"].iloc[:850].equals(base)


def test_cobre_al_alza_aconseja_esperar_y_dxy_al_alza_aconseja_comprar():
    df = mercado()
    df["cobre_lb"] = np.linspace(3.0, 4.5, len(df))  # +50% sostenido
    df["dxy"] = np.linspace(100.0, 130.0, len(df))
    s = calcular(df)
    assert s["cobre"].iloc[-1] < 0
    assert s["dxy"].iloc[-1] > 0


def test_estrechamiento_del_diferencial_de_tasas_aconseja_comprar():
    df = mercado()
    df["tpm"] = np.linspace(8.0, 4.0, len(df))  # Chile baja tasas mientras la Fed no se mueve
    assert calcular(df)["tasas"].iloc[-1] > 0


def test_dolar_en_minimo_del_anio_aconseja_comprar():
    df = mercado()
    df.iloc[-1, df.columns.get_loc("usdclp")] = df["usdclp"].iloc[-260:].min() * 0.98
    assert calcular(df)["valoracion"].iloc[-1] > 0.95  # percentil mínimo en 252 días = 1/252


def test_compuesto_usa_solo_senales_disponibles_y_exige_un_minimo():
    df = mercado()[["usdclp", "vix"]]  # solo valoración y riesgo: menos de 3 señales
    s = calcular(df)
    assert s["n_senales"].iloc[-1] == 2
    assert np.isnan(s["compuesto"].iloc[-1])
    assert estado(s["compuesto"].iloc[-1]) == "SIN DATOS"


def test_compuesto_acotado_y_estados():
    s = calcular(mercado())
    c = s["compuesto"].dropna()
    assert c.between(-1, 1).all()
    assert estado(0.3) == "BARATO" and estado(-0.3) == "CARO" and estado(0.0) == "NORMAL"

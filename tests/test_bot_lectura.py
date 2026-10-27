"""Comandos de lectura del bot: /porque, /cambios y /glosario. Usan los mismos cálculos que el tablero."""

import re

import numpy as np
import pandas as pd
import pytest

from radar import bot, reporte, senales
from radar.bot import responder

PROHIBIDO = re.compile(r"\b(compre|venda|mantenga|compra tu|vende solo|vende)\b", re.I)


@pytest.fixture
def datos(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2023-01-02", periods=700)
    df = pd.DataFrame({
        "usdclp": 900 + np.cumsum(rng.normal(0, 2, 700)),
        "cobre_lb": 4 + np.cumsum(rng.normal(0, 0.02, 700)),
        "dxy": 110 + np.cumsum(rng.normal(0, 0.2, 700)),
        "tpm": 5.0 + np.zeros(700),
        "fed_funds": 4.0 + np.zeros(700),
        "vix": 18 + np.abs(rng.normal(0, 2, 700)),
    }, index=idx)
    s = senales.calcular(df)
    monkeypatch.setattr(bot, "_datos", lambda: (df, s, reporte.actual(s, df["usdclp"])))
    return tmp_path


def test_porque_explica_el_semaforo_con_su_fecha(datos):
    texto = responder({"text": "/porque"}).texto
    assert "Semáforo" in texto and "con datos al" in texto
    assert "Lo que más pesa" in texto


def test_cambios_sin_lectura_guardada_lo_dice(datos):
    assert "No hay una lectura anterior" in responder({"text": "/cambios"}).texto


def test_cambios_compara_con_la_lectura_guardada(datos):
    (datos / "data").mkdir()
    (datos / "data" / "estado.json").write_text(
        '{"fecha": "2026-10-26", "senales": {"valor_justo": -0.9}}', encoding="utf-8")
    texto = responder({"text": "/cambios"}).texto
    assert "2026-10-26" in texto


def test_glosario_define_los_terminos(datos):
    assert "Puntaje:" in responder({"text": "/glosario"}).texto


@pytest.mark.parametrize("comando", ["/porque", "/cambios", "/glosario"])
def test_textos_de_lectura_no_dan_ordenes(datos, comando):
    assert not PROHIBIDO.search(responder({"text": comando}).texto)

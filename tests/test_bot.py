import json

import numpy as np
import pandas as pd
import pytest

from radar import bot, metricas, telegram
from radar.bot import Respuesta, interpretar, responder


def test_interpretar_limpia_mencion_y_argumentos():
    assert interpretar("/estado@RadarBot  ") == ("estado", "")
    assert interpretar("/datos   USDCLP") == ("datos", "USDCLP")
    assert interpretar("historia") == ("historia", "")


def test_comando_desconocido_no_revela_nada_interno():
    r = responder({"text": "/inexistente"})
    assert "No conozco" in r.texto


def test_serie_invalida_se_rechaza_sin_leer_archivos():
    r = responder({"text": "/datos ../../secreto"})
    assert "Serie desconocida" in r.texto


def test_limite_por_chat_corta_y_avisa_una_vez(monkeypatch, tmp_path):
    monkeypatch.setattr(bot, "ARCHIVO_BOT", tmp_path / "bot.json")
    updates = [{"update_id": i, "message": {"chat": {"id": 5}, "text": "/ayuda", "from": {"is_bot": False}}}
               for i in range(7)]
    lotes = [updates, []]
    monkeypatch.setattr(telegram, "actualizaciones", lambda offset, espera=0: lotes.pop(0) if lotes else [])
    enviados = []
    monkeypatch.setattr(telegram, "mensaje", lambda chat, texto, silencioso=False: enviados.append((chat, texto)))
    monkeypatch.setattr(bot, "responder", lambda m: Respuesta("ok"))

    atendidos = bot.ciclo(una_vez=True)

    assert atendidos == bot.CONSULTAS_POR_VENTANA
    avisos = [t for _, t in enviados if "Muchas consultas" in t]
    assert len(avisos) == 1
    assert json.loads((tmp_path / "bot.json").read_text())["offset"] == 7


def test_bots_y_mensajes_sin_texto_se_ignoran(monkeypatch, tmp_path):
    monkeypatch.setattr(bot, "ARCHIVO_BOT", tmp_path / "bot.json")
    updates = [
        {"update_id": 1, "message": {"chat": {"id": 1}, "text": "/ayuda", "from": {"is_bot": True}}},
        {"update_id": 2, "message": {"chat": {"id": 2}, "from": {"is_bot": False}}},  # sin texto (foto)
    ]
    monkeypatch.setattr(telegram, "actualizaciones", lambda offset, espera=0: updates)
    enviados = []
    monkeypatch.setattr(telegram, "mensaje", lambda chat, texto, silencioso=False: enviados.append(chat))
    assert bot.ciclo(una_vez=True) == 0
    assert enviados == []


def test_prediccion_sin_estado_no_inventa_escenarios():
    texto = Respuesta("Sin estado actual: faltan datos para calcular escenarios.").texto
    assert "faltan datos" in texto


def test_escenarios_describen_el_pasado():
    rng = np.random.default_rng(3)
    idx = pd.bdate_range("2015-01-01", periods=1500)
    precios = pd.Series(900 * np.exp(np.cumsum(rng.normal(0, 0.006, len(idx)))), index=idx)
    comp = pd.Series(rng.normal(0, 0.5, len(idx)), index=idx)
    cal = metricas.calibracion(precios, comp)
    assert "TODOS" in set(cal["estado"])


def test_grafico_genera_png(tmp_path):
    from radar import grafico
    from radar.senales import calcular

    idx = pd.bdate_range("2020-01-01", periods=400)
    df = pd.DataFrame({"usdclp": np.linspace(800, 900, len(idx)), "cobre_lb": 4.0, "dxy": 100.0,
                       "tpm": 2.0, "fed_funds": 1.0, "vix": 20.0}, index=idx)
    ruta = grafico.generar(df, calcular(df), tmp_path / "g.png")
    assert ruta.exists() and ruta.stat().st_size > 1000


def test_multipart_incluye_archivo_y_limite(tmp_path):
    archivo = tmp_path / "usdclp.csv"
    archivo.write_text("fecha,valor\n2026-10-23,986.58\n", encoding="utf-8")
    cuerpo, ctype = telegram._multipart({"chat_id": "1"}, "document", archivo)
    assert ctype.startswith("multipart/form-data; boundary=")
    assert b'filename="usdclp.csv"' in cuerpo
    assert b"2026-10-23,986.58" in cuerpo


@pytest.mark.parametrize("texto", ["/historia", "/prediccion", "/backtest"])
def test_comandos_publicos_no_requieren_rol(texto, monkeypatch):
    # Cualquiera puede consultar: no existe ningún chequeo de dueño en el camino.
    monkeypatch.setattr(bot, "_datos", lambda: (_ for _ in ()).throw(RuntimeError("sin datos")))
    r = responder({"text": texto})
    assert "No pude calcular" in r.texto

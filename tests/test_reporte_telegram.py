import pytest

from radar import telegram
from radar.reporte import num, pct


def test_formato_chileno():
    assert num(986.58) == "986,58"
    assert num(41205.16) == "41.205,16"
    assert pct(-0.0304) == "−3,0%"
    assert pct(0.091) == "+9,1%"


def test_telegram_solo_ok_true_es_exito():
    telegram.validar_respuesta({"ok": True, "result": {}})
    for malo in ({"ok": False, "description": "Bad Request: chat not found"}, {"ok": "true"}, [], None):
        with pytest.raises(telegram.TelegramError):
            telegram.validar_respuesta(malo)


def test_telegram_sin_credenciales_falla_claro(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    with pytest.raises(telegram.TelegramError, match="faltan"):
        telegram.enviar("hola")

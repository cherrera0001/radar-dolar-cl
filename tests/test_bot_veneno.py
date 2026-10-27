"""Un error permanente de Telegram (p. ej. el chat bloqueó al bot) no puede frenar al resto de los usuarios."""

import json

from radar import bot, telegram
from radar.bot import Respuesta


def test_error_permanente_descarta_el_update_y_atiende_el_siguiente(tmp_path, monkeypatch):
    monkeypatch.setattr(bot, "ARCHIVO_BOT", tmp_path / "bot.json")
    updates = [
        {"update_id": 10, "message": {"chat": {"id": 1}, "from": {"is_bot": False}, "text": "/ayuda"}},
        {"update_id": 11, "message": {"chat": {"id": 2}, "from": {"is_bot": False}, "text": "/ayuda"}},
    ]
    lotes = [updates, []]
    monkeypatch.setattr(telegram, "actualizaciones", lambda offset, espera=0: lotes.pop(0) if lotes else [])
    enviados = []

    def mensaje(chat, texto, silencioso=False):
        if chat == 1:
            raise telegram.TelegramError("sendMessage HTTP 403: Forbidden: bot was blocked by the user", codigo=403)
        enviados.append(chat)

    monkeypatch.setattr(telegram, "mensaje", mensaje)
    monkeypatch.setattr(bot, "responder", lambda m: Respuesta("ok"))

    assert bot.ciclo(una_vez=True) == 1
    assert enviados == [2]
    assert json.loads((tmp_path / "bot.json").read_text())["offset"] == 12


def test_solo_los_4xx_que_no_son_429_son_permanentes():
    assert telegram.TelegramError("x", codigo=403).permanente
    assert telegram.TelegramError("x", codigo=400).permanente
    assert not telegram.TelegramError("x", codigo=429).permanente  # límite de tasa: pasa solo
    assert not telegram.TelegramError("x", codigo=502).permanente
    assert not telegram.TelegramError("sin respuesta").permanente

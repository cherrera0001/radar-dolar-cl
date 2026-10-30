"""El ciclo de escucha resiste outages transitorios de Telegram sin disparar la cadena de corridas.

Aprendizaje 2026-10-29: un 502 de Telegram mataba la corrida, el workflow encolaba otra de
inmediato y en 7 minutos hubo 10 corridas falladas en ráfaga. Ahora el ciclo espera con
backoff y solo se rinde tras POLLING_FALLOS_MAX intentos seguidos.
"""

import pytest

from radar import bot, telegram


def _poll_que_falla(monkeypatch, excepciones):
    """Consume una excepción por llamada; cuando se agotan, devuelve listas vacías."""
    llamadas = []
    fallos = list(excepciones)

    def poll(offset, espera=0):
        llamadas.append(1)
        if fallos:
            raise fallos.pop(0)
        return []

    monkeypatch.setattr(telegram, "actualizaciones", poll)
    esperas = []
    monkeypatch.setattr(bot.time, "sleep", lambda s: esperas.append(s))
    return llamadas, esperas


def test_fallo_transitorio_reintenta_con_backoff_y_sobrevive(monkeypatch, tmp_path):
    monkeypatch.setattr(bot, "ARCHIVO_BOT", tmp_path / "bot.json")
    fallos = [telegram.TelegramError("getUpdates HTTP 502", codigo=502) for _ in range(2)]
    llamadas, esperas = _poll_que_falla(monkeypatch, fallos)

    assert bot.ciclo(una_vez=True) == 0

    assert len(llamadas) == 3  # dos fallos y el reintento exitoso
    assert esperas == [bot.ESPERA_TRAS_FALLO_SEG, bot.ESPERA_TRAS_FALLO_SEG * 2]


def test_error_permanente_no_reintenta_y_sale(monkeypatch, tmp_path):
    monkeypatch.setattr(bot, "ARCHIVO_BOT", tmp_path / "bot.json")
    llamadas, esperas = _poll_que_falla(
        monkeypatch, [telegram.TelegramError("HTTP 404", codigo=404)])

    with pytest.raises(telegram.TelegramError):
        bot.ciclo(una_vez=True)

    assert len(llamadas) == 1
    assert esperas == []


def test_se_rinde_tras_n_fallos_seguidos(monkeypatch, tmp_path):
    monkeypatch.setattr(bot, "ARCHIVO_BOT", tmp_path / "bot.json")
    fallos = [telegram.TelegramError("HTTP 502", codigo=502)] * bot.POLLING_FALLOS_MAX
    llamadas, esperas = _poll_que_falla(monkeypatch, fallos)

    with pytest.raises(telegram.TelegramError, match=f"{bot.POLLING_FALLOS_MAX} veces"):
        bot.ciclo(una_vez=True)

    assert len(llamadas) == bot.POLLING_FALLOS_MAX
    assert len(esperas) == bot.POLLING_FALLOS_MAX - 1  # no espera antes de rendirse


def test_un_acierto_reinicia_el_contador_de_fallos(monkeypatch, tmp_path):
    monkeypatch.setattr(bot, "ARCHIVO_BOT", tmp_path / "bot.json")
    t = [0.0]
    monkeypatch.setattr(bot.time, "monotonic", lambda: t[0])
    monkeypatch.setattr(bot.time, "sleep", lambda s: t.__setitem__(0, t[0] + s))
    fallos = iter([telegram.TelegramError("HTTP 502", codigo=502), None] * 3)

    def poll(offset, espera=0):
        item = next(fallos)
        if isinstance(item, Exception):
            raise item
        return []

    monkeypatch.setattr(telegram, "actualizaciones", poll)
    # Con reset, tres fallos aislados nunca alcanzan POLLING_FALLOS_MAX seguidos: no se rinde.
    assert bot.ciclo(una_vez=False, durante=90) == 0

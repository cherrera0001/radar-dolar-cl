"""Un texto más largo que el límite de Telegram se envía en partes: nada se corta en silencio."""

from radar import telegram


def test_texto_largo_se_envia_en_partes_sin_perder_lineas(monkeypatch):
    enviados = []
    monkeypatch.setattr(telegram, "_json", lambda metodo, datos, timeout=30.0: enviados.append(datos["text"]))
    texto = "\n".join(f"línea {i:04d} " + "x" * 50 for i in range(200))

    telegram.mensaje(1, texto)

    assert len(enviados) > 1
    assert all(len(parte) <= telegram.LIMITE_TEXTO for parte in enviados)
    assert "\n".join(enviados) == texto


def test_texto_corto_se_envia_una_vez(monkeypatch):
    enviados = []
    monkeypatch.setattr(telegram, "_json", lambda metodo, datos, timeout=30.0: enviados.append(datos["text"]))
    telegram.mensaje(1, "hola")
    assert enviados == ["hola"]

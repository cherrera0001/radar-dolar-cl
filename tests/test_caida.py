"""`radar caida`: el aviso al dueño cuando un workflow falla, una vez al día por componente."""

import argparse

from radar import cli, envios, telegram


def _args(estado, enviar=False, url=""):
    return argparse.Namespace(componente="diario", estado=estado, url=url, enviar=enviar)


def _espia_de_envios(monkeypatch, tmp_path):
    monkeypatch.setattr(envios, "ARCHIVO_ENVIOS", tmp_path / "envios.json")
    enviados = []
    monkeypatch.setattr(telegram, "enviar", lambda texto, silencioso=False: enviados.append(texto))
    return enviados


def test_corrida_ok_no_envia_nada(monkeypatch, tmp_path, capsys):
    enviados = _espia_de_envios(monkeypatch, tmp_path)
    assert cli.cmd_caida(_args("success")) == 0
    assert enviados == []
    assert "OK" in capsys.readouterr().out


def test_falla_sin_enviar_solo_imprime_el_aviso(monkeypatch, tmp_path, capsys):
    enviados = _espia_de_envios(monkeypatch, tmp_path)
    assert cli.cmd_caida(_args("failure", url="https://corrida/1")) == 0
    assert enviados == []
    salida = capsys.readouterr().out
    assert "falló" in salida and "https://corrida/1" in salida


def test_falla_envia_un_solo_aviso_por_dia(monkeypatch, tmp_path):
    enviados = _espia_de_envios(monkeypatch, tmp_path)
    assert cli.cmd_caida(_args("failure", enviar=True, url="https://corrida/1")) == 0
    assert cli.cmd_caida(_args("failure", enviar=True, url="https://corrida/2")) == 0

    assert len(enviados) == 1  # la segunda corrida fallada del mismo día no repite el aviso
    assert "diario" in enviados[0] and "https://corrida/1" in enviados[0]

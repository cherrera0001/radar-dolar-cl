"""`radar alerta`: el aviso de salud debe llegar con un salto de línea por aviso, no con `\\n` literal."""

import argparse
import json

from radar import cli


def test_aviso_de_salud_tiene_saltos_de_linea_reales(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    avisos = ["🔴 usdclp: la fuente falla hace 3 días hábiles seguidos", "🟠 cobre_lb: datos atrasados"]
    (tmp_path / "data" / "estado.json").write_text(
        json.dumps({"avisos_pendientes": avisos}, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(cli, "_cargar", lambda: (None, None, {
        "estado": "NORMAL", "fecha": "2026-10-27", "compuesto": 0.1, "senales": {}, "fila": {}}))

    cli.cmd_alerta(argparse.Namespace(enviar=False))

    salida = capsys.readouterr().out
    assert "\\n" not in salida
    assert avisos[0] in salida.splitlines()
    assert avisos[1] in salida.splitlines()

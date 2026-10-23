from radar.cli import main


def test_bcch_sin_credenciales_falla_con_mensaje_claro(monkeypatch, capsys):
    monkeypatch.delenv("BCCH_USER", raising=False)
    monkeypatch.delenv("BCCH_PASS", raising=False)
    assert main(["bcch", "prueba"]) == 1
    assert "Faltan BCCH_USER / BCCH_PASS" in capsys.readouterr().err


def test_bcch_credenciales_invalidas_se_reportan_como_error_de_fuente(monkeypatch, capsys):
    monkeypatch.setenv("BCCH_USER", "x")
    monkeypatch.setenv("BCCH_PASS", "y")
    # La API responde HTTP 200 con un error en el cuerpo: debe terminar en error de fuente, no en datos
    monkeypatch.setattr("radar.fuentes.bcentral.http_get",
                        lambda url, timeout=60: b'{"Codigo": -5, "Descripcion": "Invalid username or password"}')
    assert main(["bcch", "prueba"]) == 3
    assert "Codigo=-5" in capsys.readouterr().err

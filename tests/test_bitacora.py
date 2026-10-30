"""Bitácora de ejecuciones: una línea JSON por corrida, con rotación."""

import json

from radar import bitacora


def test_registra_una_linea_por_corrida_con_sus_detalles(tmp_path):
    ruta = tmp_path / "ejecuciones.jsonl"
    b = bitacora.Bitacora("actualizar", ruta)
    b.detalle(errores=2, cambios=14)
    b.registrar(0)

    linea = json.loads(ruta.read_text(encoding="utf-8").splitlines()[0])
    assert linea["comando"] == "actualizar"
    assert linea["codigo"] == 0
    assert linea["errores"] == 2 and linea["cambios"] == 14
    assert "ts" in linea and "duracion_s" in linea


def test_el_error_de_una_excepcion_queda_registrado(tmp_path):
    ruta = tmp_path / "ejecuciones.jsonl"
    b = bitacora.Bitacora("bot", ruta)
    b.registrar(99, error="TelegramError: getUpdates falló 5 veces")

    linea = json.loads(ruta.read_text(encoding="utf-8").splitlines()[0])
    assert linea["codigo"] == 99
    assert "TelegramError" in linea["error"]


def test_la_rotacion_conserva_la_cola_del_log(tmp_path):
    ruta = tmp_path / "ejecuciones.jsonl"
    ruta.write_text("".join(json.dumps({"n": i}) + "\n" for i in range(bitacora.MAX_LINEAS + 20)),
                    encoding="utf-8")

    bitacora.Bitacora("x", ruta).registrar(0)

    lineas = ruta.read_text(encoding="utf-8").splitlines()
    assert len(lineas) == bitacora.MAX_LINEAS // 2
    assert json.loads(lineas[-1])["comando"] == "x"  # la última corrida quedó registrada
    assert json.loads(lineas[0])["n"] == bitacora.MAX_LINEAS + 21 - bitacora.MAX_LINEAS // 2

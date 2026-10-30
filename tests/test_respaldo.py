"""Fuente de respaldo de usdclp (er-api): contrato de su respuesta y su uso desde `radar actualizar`."""

from datetime import date

import pytest

from radar import almacen
from radar.actualizar import actualizar
from radar.fuentes import fred, mindicador, respaldo
from radar.fuentes.base import FuenteError, Punto

CUERPO_OK = {
    "result": "success",
    "base_code": "USD",
    "time_last_update_utc": "Fri, 30 Oct 2026 00:02:31 +0000",
    "rates": {"CLP": 987.65, "EUR": 0.92},
}


def test_leer_respuesta_valida():
    p = respaldo.leer_respuesta(CUERPO_OK)
    assert p == Punto("usdclp", date(2026, 10, 30), 987.65, "er-api.com")


@pytest.mark.parametrize("cuerpo", [
    {"result": "error"},
    {**CUERPO_OK, "rates": {"EUR": 0.92}},
    {**CUERPO_OK, "time_last_update_utc": "fecha rara"},
])
def test_leer_respuesta_rechaza_contrato_roto(cuerpo):
    with pytest.raises(FuenteError):
        respaldo.leer_respuesta(cuerpo)


def test_leer_respuesta_rechaza_valor_fuera_de_rango():
    with pytest.raises(FuenteError, match="rango"):
        respaldo.leer_respuesta({**CUERPO_OK, "rates": {"CLP": 12.0}})


def _actualizar_con_mindicador_caido(monkeypatch, tmp_path, hoy=date(2026, 10, 30)):
    def caida(serie, anio):
        raise FuenteError(f"mindicador.cl/{serie}: reset de conexión")

    monkeypatch.setattr(mindicador, "descargar", caida)
    monkeypatch.setattr(fred, "descargar", lambda serie, desde=None: [])
    return actualizar(hoy=hoy, base=tmp_path)


def test_actualizar_usa_el_respaldo_para_usdclp(monkeypatch, tmp_path):
    monkeypatch.setattr(respaldo, "descargar",
                        lambda: [Punto("usdclp", date(2026, 10, 30), 987.65, respaldo.FUENTE)])
    r = _actualizar_con_mindicador_caido(monkeypatch, tmp_path)

    assert "usdclp" not in r.fallidas  # el dato quedó al día: no es una serie caída
    assert {"cobre_lb", "tpm"} <= r.fallidas
    assert any("respaldo" in a for a in r.avisos)
    guardado = almacen.leer("usdclp", tmp_path)
    assert guardado.iloc[-1] == pytest.approx(987.65)


def test_actualizar_marca_la_fuente_del_respaldo_en_el_csv(monkeypatch, tmp_path):
    monkeypatch.setattr(respaldo, "descargar",
                        lambda: [Punto("usdclp", date(2026, 10, 30), 987.65, respaldo.FUENTE)])
    _actualizar_con_mindicador_caido(monkeypatch, tmp_path)

    texto = (tmp_path / "usdclp.csv").read_text(encoding="utf-8")
    assert "er-api.com" in texto


def test_respaldo_desactivado_deja_la_serie_como_caida(monkeypatch, tmp_path):
    monkeypatch.setenv("RADAR_USDCLP_RESPALDO", "0")
    monkeypatch.setattr(respaldo, "descargar",
                        lambda: [Punto("usdclp", date(2026, 10, 30), 987.65, respaldo.FUENTE)])
    r = _actualizar_con_mindicador_caido(monkeypatch, tmp_path)

    assert "usdclp" in r.fallidas
    assert not any("respaldo" in a for a in r.avisos)


def test_si_el_respaldo_tambien_falla_manda_el_error_original(monkeypatch, tmp_path):
    def caido():
        raise FuenteError("er-api: sin respuesta")

    monkeypatch.setattr(respaldo, "descargar", caido)
    r = _actualizar_con_mindicador_caido(monkeypatch, tmp_path)

    assert "usdclp" in r.fallidas
    assert any("mindicador" in e for e in r.errores)
    assert any("respaldo" in n for n in r.notas)

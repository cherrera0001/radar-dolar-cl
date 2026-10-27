"""mindicador.cl a veces responde 200 con un error dentro del cuerpo. Ese error debe reintentarse y
explicarse con el mensaje de la fuente, no con un "codigo inesperado" que no dice nada."""

import json

import pytest

from radar.fuentes import base, mindicador
from radar.fuentes.base import FuenteError

ERROR_FUENTE = {"error": "500 Internal Server Error", "message": "cursor id 13104071494 not found", "description": None}
SERIE_OK = {"codigo": "dolar", "serie": [{"fecha": "2026-10-23T03:00:00.000Z", "valor": 986.58}]}


@pytest.fixture
def sin_espera(monkeypatch):
    esperas: list[float] = []
    monkeypatch.setattr(base.time, "sleep", esperas.append)
    return esperas


def test_el_error_de_la_fuente_se_explica_con_su_mensaje():
    with pytest.raises(FuenteError, match="cursor id 13104071494 not found"):
        mindicador.leer_serie(ERROR_FUENTE, "usdclp")


def test_un_error_del_servicio_se_reintenta_y_luego_responde_bien(monkeypatch, sin_espera):
    respuestas = [json.dumps(ERROR_FUENTE).encode(), json.dumps(SERIE_OK).encode()]
    llamadas = []

    def fake_get(url, timeout=30.0):
        llamadas.append(url)
        return respuestas.pop(0)

    monkeypatch.setattr(mindicador, "http_get", fake_get)
    puntos = mindicador.descargar("usdclp", 2026)
    assert [p.valor for p in puntos] == [986.58]
    assert len(llamadas) == 2
    assert len(sin_espera) == 1


def test_si_el_error_persiste_se_agotan_los_reintentos(monkeypatch, sin_espera):
    llamadas = []

    def fake_get(url, timeout=30.0):
        llamadas.append(url)
        return json.dumps(ERROR_FUENTE).encode()

    monkeypatch.setattr(mindicador, "http_get", fake_get)
    with pytest.raises(FuenteError, match="cursor id"):
        mindicador.descargar("usdclp", 2026)
    assert len(llamadas) == base.REINTENTOS + 1

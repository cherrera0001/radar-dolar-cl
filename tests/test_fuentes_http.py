"""Reintentos de `http_get`: un fallo transitorio no debe contar como día sin dato, y ningún error de red debe
escapar como excepción que no sea FuenteError (si no, `radar actualizar` muere y no guarda nada)."""

import http.client
import io
import urllib.error

import pytest

from radar.fuentes import base
from radar.fuentes.base import FuenteError


class Respuesta:
    def __init__(self, cuerpo: bytes):
        self._cuerpo = cuerpo

    def read(self) -> bytes:
        return self._cuerpo

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


@pytest.fixture
def sin_espera(monkeypatch):
    esperas: list[float] = []
    monkeypatch.setattr(base.time, "sleep", esperas.append)
    return esperas


def _urlopen_con(monkeypatch, secuencia: list):
    """Cada llamada consume un elemento: una excepción se lanza, un bytes se devuelve como cuerpo."""
    llamadas = []

    def fake(req, timeout):
        llamadas.append(req)
        siguiente = secuencia[len(llamadas) - 1]
        if isinstance(siguiente, BaseException):
            raise siguiente
        return Respuesta(siguiente)

    monkeypatch.setattr(base.urllib.request, "urlopen", fake)
    return llamadas


def test_reintenta_un_fallo_transitorio_y_devuelve_el_cuerpo(monkeypatch, sin_espera):
    llamadas = _urlopen_con(monkeypatch, [ConnectionResetError("reset"), b"ok"])
    assert base.http_get("https://ejemplo.cl/x") == b"ok"
    assert len(llamadas) == 2
    assert len(sin_espera) == 1  # una espera entre los dos intentos


def test_reset_durante_la_lectura_es_fuente_error_y_se_reintenta(monkeypatch, sin_espera):
    class CorteAlLeer(Respuesta):
        def __init__(self):
            super().__init__(b"")
            self._fallos = 1

        def read(self):
            if self._fallos:
                self._fallos -= 1
                raise http.client.RemoteDisconnected("cortada")
            return b"ok"

    primera = iter([CorteAlLeer()])
    llamadas = []

    def fake(req, timeout):
        llamadas.append(req)
        return next(primera) if len(llamadas) == 1 else Respuesta(b"ok")

    monkeypatch.setattr(base.urllib.request, "urlopen", fake)
    assert base.http_get("https://ejemplo.cl/x") == b"ok"
    assert len(llamadas) == 2


def test_no_reintenta_un_404(monkeypatch, sin_espera):
    error = urllib.error.HTTPError("https://ejemplo.cl/x", 404, "No encontrado", {}, io.BytesIO(b""))
    llamadas = _urlopen_con(monkeypatch, [error])
    with pytest.raises(FuenteError):
        base.http_get("https://ejemplo.cl/x")
    assert len(llamadas) == 1
    assert sin_espera == []


def test_agota_los_reintentos_y_lanza_fuente_error(monkeypatch, sin_espera):
    llamadas = _urlopen_con(monkeypatch, [TimeoutError("lento")] * (base.REINTENTOS + 1))
    with pytest.raises(FuenteError, match="no se pudo leer"):
        base.http_get("https://ejemplo.cl/x?user=secreto&pass=secreto")
    assert len(llamadas) == base.REINTENTOS + 1
    assert len(sin_espera) == base.REINTENTOS


def test_el_mensaje_de_error_no_muestra_la_consulta(monkeypatch, sin_espera):
    _urlopen_con(monkeypatch, [TimeoutError("lento")] * (base.REINTENTOS + 1))
    with pytest.raises(FuenteError) as info:
        base.http_get("https://ejemplo.cl/x?user=u&pass=claveSecreta")
    assert "claveSecreta" not in str(info.value)


def test_usa_cabeceras_de_navegador(monkeypatch, sin_espera):
    # mindicador.cl corta conexiones con cara de bot; el cliente debe parecer navegador.
    llamadas = _urlopen_con(monkeypatch, [b"ok"])
    base.http_get("https://ejemplo.cl/x")
    req = llamadas[0]
    assert req.get_header("User-agent").startswith("Mozilla/5.0")
    assert req.get_header("Accept") == base.CABECERAS["Accept"]


def test_el_backoff_tiene_tope_y_jitter():
    esperas = [base.espera_reintento(i) for i in range(12)]
    assert all(base.ESPERA_BASE_SEGUNDOS <= e < base.ESPERA_MAX_SEGUNDOS * 1.5 for e in esperas)
    assert esperas[0] < base.ESPERA_BASE_SEGUNDOS * 1.5  # el primer fallo espera poco
    assert esperas[-1] >= base.ESPERA_MAX_SEGUNDOS  # el tope se alcanza y se mantiene


def test_hay_mas_de_tres_intentos_para_aguantar_outages_cortos():
    # mindicador.cl falló ~4 de cada 5 conexiones el 2026-10-30; con 3 intentos la serie se caía seguido.
    assert base.REINTENTOS >= 4

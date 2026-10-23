"""Contratos de las fuentes: el cuerpo manda, no el código HTTP."""

from datetime import date

import pytest

from radar.fuentes import bcentral, fred, mindicador
from radar.fuentes.base import FuenteError

MINDICADOR_OK = {
    "version": "1.7.0", "autor": "mindicador.cl", "codigo": "dolar", "nombre": "Dólar observado",
    "unidad_medida": "Pesos",
    "serie": [
        {"fecha": "2025-12-30T03:00:00.000Z", "valor": 911.18},
        {"fecha": "2025-07-01T04:00:00.000Z", "valor": 935},
    ],
}


def test_mindicador_lee_serie_y_usa_el_dia_utc():
    puntos = mindicador.leer_serie(MINDICADOR_OK, "usdclp")
    assert [(p.fecha, p.valor) for p in puntos] == [(date(2025, 12, 30), 911.18), (date(2025, 7, 1), 935.0)]
    assert all(p.fuente == "mindicador.cl" and p.serie == "usdclp" for p in puntos)


@pytest.mark.parametrize("cuerpo", [
    {"Codigo": -5, "Descripcion": "Invalid username or password"},  # un 200 con error dentro
    "<html>mantención</html>",
    {"codigo": "euro", "serie": []},  # serie equivocada
    {"codigo": "dolar"},  # sin 'serie'
    {"codigo": "dolar", "serie": [{"fecha": "2025-01-02T03:00:00.000Z", "valor": "996,46"}]},  # texto con coma
    {"codigo": "dolar", "serie": [{"fecha": "2025-01-02T03:00:00.000Z", "valor": 0}]},  # imposible
    {"codigo": "dolar", "serie": [{"fecha": "2025-01-02T03:00:00.000Z", "valor": True}]},
    {"codigo": "dolar", "serie": [{"fecha": "ayer", "valor": 950}]},
    {"codigo": "dolar", "serie": [{"valor": 950}]},
])
def test_mindicador_rechaza_cuerpos_que_mienten(cuerpo):
    with pytest.raises(FuenteError):
        mindicador.leer_serie(cuerpo, "usdclp")


def test_fred_omite_dias_sin_dato_y_filtra_por_fecha():
    texto = "observation_date,VIXCLS\n2011-12-30,23.4\n2012-01-02,.\n2012-01-03,22.97\n2012-01-04,\n"
    puntos = fred.leer_csv(texto, "vix", desde=date(2012, 1, 1))
    assert [(p.fecha, p.valor) for p in puntos] == [(date(2012, 1, 3), 22.97)]


@pytest.mark.parametrize("texto", [
    "<!DOCTYPE html><html>Service unavailable</html>",
    "observation_date,DFF\n2026-01-02,4.33\n",  # encabezado de otra serie
    "observation_date,VIXCLS\n",  # sin observaciones
    "observation_date,VIXCLS\n2026-01-02,999\n",  # fuera de rango
    "observation_date,VIXCLS\n02/01/2026,20\n",  # fecha ilegible
])
def test_fred_rechaza_respuestas_invalidas(texto):
    with pytest.raises(FuenteError):
        fred.leer_csv(texto, "vix")


def test_bcentral_codigo_distinto_de_cero_es_error_aunque_sea_http_200():
    with pytest.raises(FuenteError, match="Codigo=-5"):
        bcentral.validar_cuerpo({"Codigo": -5, "Descripcion": "Invalid username or password"})


def test_bcentral_lee_observaciones_y_omite_feriados():
    cuerpo = bcentral.validar_cuerpo({"Codigo": 0, "Series": {"Obs": [
        {"indexDateString": "02-01-2026", "value": "950.5", "statusCode": "OK"},
        {"indexDateString": "01-01-2026", "value": "NaN", "statusCode": "ND"},
    ]}})
    puntos = bcentral.leer_serie(cuerpo, "usdclp")
    assert [(p.fecha, p.valor) for p in puntos] == [(date(2026, 1, 2), 950.5)]

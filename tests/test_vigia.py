"""Vigía: avisa si la corrida diaria no dejó registro de hoy (cron saltado o retrasado por GitHub)."""

from datetime import date

from radar import salud

MARTES = date(2026, 10, 27)  # días hábiles: lunes a viernes


def test_al_dia_no_avisa():
    assert salud.vigilancia({"ultima_actualizacion": {"fecha": "2026-10-27"}}, MARTES) is None


def test_corrida_de_ayer_avisa_que_hoy_no_corrio():
    aviso = salud.vigilancia({"ultima_actualizacion": {"fecha": "2026-10-26"}}, MARTES)
    assert aviso is not None and "2026-10-27" in aviso


def test_fin_de_semana_espera_la_corrida_del_viernes():
    domingo = date(2026, 10, 25)
    assert salud.vigilancia({"ultima_actualizacion": {"fecha": "2026-10-23"}}, domingo) is None


def test_sin_registro_avisa():
    assert salud.vigilancia({}, MARTES) is not None

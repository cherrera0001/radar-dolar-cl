"""Lectura en lenguaje simple del estado del radar: describe, compara y explica sin dar órdenes."""

import re

import numpy as np
import pandas as pd

from radar import lectura
from radar.senales import DEFINICIONES

# Imperativos de orden (la regla del prompt). El infinitivo "comprar" describe una estrategia: no es una orden.
PROHIBIDO = re.compile(r"\b(compre|venda|mantenga|compra tu|vende solo|vende)\b", re.I)
A = {"estado": "BARATO", "fecha": "2026-10-27", "precio": 950.0, "compuesto": 0.4}


def _fila(**valores):
    base = {k: np.nan for k in DEFINICIONES}
    base.update({"n_senales": 0, "acuerdo": 0, "compuesto": 0.4})
    base.update(valores)
    base["n_senales"] = sum(1 for k in DEFINICIONES if not np.isnan(base[k]))
    return pd.Series(base)


def test_aportes_suman_el_compuesto_y_van_del_mas_fuerte_al_mas_debil():
    puntajes = dict(valor_justo=0.8, valoracion=0.2, cobre=-0.5, dxy=0.1, tasas=0.0, riesgo=0.3)
    fila = _fila(**puntajes)
    compuesto = sum(p * DEFINICIONES[k].peso for k, p in puntajes.items()) / sum(d.peso for d in DEFINICIONES.values())
    aportes = lectura.aportes(fila)
    assert abs(sum(a.contribucion for a in aportes) - compuesto) < 1e-9
    assert [abs(a.contribucion) for a in aportes] == sorted((abs(a.contribucion) for a in aportes), reverse=True)


def test_sin_datos_se_dice_y_no_cuenta_como_cero():
    fila = _fila(valor_justo=0.8, valoracion=0.2, cobre=0.1)
    texto = "\n".join(lectura.explicar(A, fila))
    assert "Sin datos para" in texto
    assert "Tasas" in texto or "Diferencial" in texto


def test_con_menos_de_tres_senales_no_hay_lectura():
    fila = _fila(valor_justo=0.8)
    fila["compuesto"] = np.nan
    texto = "\n".join(lectura.explicar({**A, "estado": "SIN DATOS", "compuesto": float("nan")}, fila))
    assert "no hay suficientes señales" in texto.lower()


def test_cambios_sin_lectura_previa_lo_dice():
    assert lectura.cambios(_fila(valor_justo=0.8), None, None)[0].startswith("No hay una lectura anterior")


def test_cambios_comparan_contra_la_corrida_guardada():
    previas = {"valor_justo": 0.1}
    lineas = lectura.cambios(_fila(valor_justo=0.5), previas, "2026-10-26")
    assert any("2026-10-26" in linea for linea in lineas)
    assert any("valor_justo" in linea or "Valor justo" in linea for linea in lineas)


def test_ningun_texto_da_ordenes():
    fila = _fila(valor_justo=0.8, valoracion=-0.9, cobre=0.5, dxy=-0.3, tasas=0.2, riesgo=-0.6)
    textos = [*lectura.explicar(A, fila), *lectura.cambios(fila, {"valor_justo": -0.5}, "2026-10-26"),
              *lectura.glosario()]
    assert not any(PROHIBIDO.search(t) for t in textos)


def test_un_dato_viejo_se_dice_con_sus_dias_habiles():
    from datetime import date

    a = {**A, "fecha": "2026-10-22"}
    texto = "\n".join(lectura.explicar(a, _fila(valor_justo=0.8, valoracion=0.2, cobre=0.1, compuesto=0.4),
                                      hoy=date(2026, 10, 27)))
    assert "hace 3 días hábiles" in texto


def test_un_dato_de_ayer_no_da_alarma():
    from datetime import date

    a = {**A, "fecha": "2026-10-26"}
    texto = "\n".join(lectura.explicar(a, _fila(valor_justo=0.8, valoracion=0.2, cobre=0.1, compuesto=0.4),
                                      hoy=date(2026, 10, 27)))
    assert "hábiles" not in texto


def test_el_glosario_usa_coma_decimal():
    assert "0,25" in "\n".join(lectura.glosario())

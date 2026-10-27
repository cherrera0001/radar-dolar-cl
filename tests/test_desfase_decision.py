"""La decisión del día d usa la señal de d − DESFASE_DECISION (R-06): el cobre llega con 2 días hábiles de desfase."""

import pandas as pd

from radar import investigacion
from radar.senales import DESFASE_DECISION


def test_el_desfase_cubre_el_insumo_mas_lento():
    assert DESFASE_DECISION == 2  # cobre_lb: almacen.DESFASE_MERCADO


def test_la_decision_del_dia_usa_la_senal_de_dos_dias_antes():
    idx = pd.bdate_range("2020-01-01", "2020-04-30")
    comp = pd.Series(range(len(idx)), index=idx, dtype=float)
    senales = pd.DataFrame({"compuesto": comp, "desvio_pct": comp}, index=idx)
    prep = investigacion.preparar(pd.Series(100.0, index=idx), senales)
    esperado = comp.shift(DESFASE_DECISION).reindex(prep.index)
    assert (prep["compuesto"] == esperado).all()

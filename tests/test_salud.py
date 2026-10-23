from datetime import date, timedelta

from radar.salud import FALLAS_PARA_AVISAR, evaluar

HOY = date(2026, 10, 23)
AL_DIA = {"usdclp": HOY, "dxy": HOY - timedelta(days=10)}  # el DXY semanal tolera 14 días


def correr(dias_con_falla: list[bool], ultimas=AL_DIA):
    estado, todos = {}, []
    for falla in dias_con_falla:
        estado, avisos = evaluar(estado, {"usdclp"} if falla else set(), ultimas, HOY)
        todos.append(avisos)
    return estado, todos


def test_una_falla_aislada_no_avisa():
    estado, avisos = correr([True, False])
    assert avisos == [[], []]
    assert estado["usdclp"]["fallas"] == 0


def test_tres_fallas_seguidas_avisan_una_sola_vez():
    estado, avisos = correr([True] * (FALLAS_PARA_AVISAR + 2))
    con_aviso = [a for a in avisos if a]
    assert len(con_aviso) == 1 and "falla hace 3 días" in con_aviso[0][0]
    assert estado["usdclp"]["fallas"] == FALLAS_PARA_AVISAR + 2


def test_la_recuperacion_se_avisa():
    _, avisos = correr([True] * FALLAS_PARA_AVISAR + [False, False])
    assert any("volvió a responder" in m for m in avisos[FALLAS_PARA_AVISAR])
    assert avisos[-1] == []


def test_serie_congelada_sin_error_avisa_atraso_una_vez_y_luego_recuperacion():
    viejo = {"usdclp": HOY - timedelta(days=12), "dxy": HOY}
    estado, a1 = evaluar({}, set(), viejo, HOY)
    assert any("usdclp: datos atrasados" in m for m in a1)
    estado, a2 = evaluar(estado, set(), viejo, HOY)
    assert a2 == []  # no se repite
    _, a3 = evaluar(estado, set(), {"usdclp": HOY, "dxy": HOY}, HOY)
    assert any("usdclp: datos al día" in m for m in a3)


def test_dxy_dentro_de_su_tolerancia_semanal_no_esta_atrasado():
    _, avisos = evaluar({}, set(), AL_DIA, HOY)
    assert avisos == []

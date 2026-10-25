from datetime import date

import pytest

from radar import decision, envios, reporte
from radar.decision import Perfil

HOY = date(2026, 11, 3)
RECIENTE = date(2026, 9, 1)


def perfil(**cambios):
    base = dict(w_objetivo=40.0, w_actual=38.0, colchon_completo=True, deficit_usd=0.0, confirmado=RECIENTE)
    base.update(cambios)
    return Perfil(**base)


def test_sin_perfil_no_hay_instruccion():
    assert decision.decidir(None, HOY, vigente=True).accion == "SIN SEÑAL"


def test_perfil_no_confirmado_hace_seis_meses_bloquea():
    viejo = perfil(confirmado=date(2026, 3, 1))
    assert decision.decidir(viejo, HOY, vigente=True).codigo == "perfil_vencido"


def test_datos_vencidos_dan_sin_senal_aunque_haya_perfil():
    assert decision.decidir(perfil(), HOY, vigente=False).codigo == "insumo_vencido"


def test_precedencia_venta_gana_a_mantener_y_compra():
    p = perfil(deficit_usd=500.0, colchon_completo=False)
    assert decision.decidir(p, HOY, vigente=True).accion == "VENDER"


def test_mantener_si_colchon_incompleto_o_sobre_banda():
    assert decision.decidir(perfil(colchon_completo=False), HOY, vigente=True).accion == "MANTENER"
    assert decision.decidir(perfil(w_actual=51.0), HOY, vigente=True).accion == "MANTENER"


def test_comprar_si_todo_cuadra_dentro_de_la_banda():
    assert decision.decidir(perfil(w_actual=50.0), HOY, vigente=True).accion == "COMPRAR"


def test_la_banda_es_estricta_en_diez_puntos():
    # w = w* + 10 todavía está dentro de la banda; por encima, MANTENER.
    assert decision.decidir(perfil(w_actual=50.0), HOY, vigente=True).accion == "COMPRAR"
    assert decision.decidir(perfil(w_actual=50.01), HOY, vigente=True).accion == "MANTENER"


def test_perfil_desde_secreto_no_desde_el_repo(tmp_path):
    entorno = {"PERFIL_DUENO": '{"w_objetivo": 40, "w_actual": 38, "colchon_completo": true, '
                               '"confirmado": "2026-09-01"}'}
    p = decision.cargar_perfil(entorno, ruta=tmp_path / "no-existe.json")
    assert p is not None and p.w_objetivo == 40.0


def test_sin_secreto_ni_archivo_local_no_hay_perfil(tmp_path):
    assert decision.cargar_perfil({}, ruta=tmp_path / "perfil.local.json") is None


def test_texto_de_instruccion_usa_formato_chileno_sin_tocar_las_frases():
    instr = decision.Instruccion("VENDER", "necesidad", "Vende solo ese monto, en tramos mensuales.")
    t = decision.texto(instr, HOY, 986.58, "2026-10-23", "CARO")
    assert "Vende solo ese monto, en tramos mensuales." in t
    assert "$986,58" in t


def test_envio_se_registra_y_no_se_repite(tmp_path):
    ruta = tmp_path / "envios.json"
    enviados = []
    assert envios.enviar_una_vez("accion:2026-11", "VENDER|necesidad", enviados.append, ruta)
    assert not envios.enviar_una_vez("accion:2026-11", "VENDER|necesidad", enviados.append, ruta)
    assert len(enviados) == 1


def test_cambio_de_instruccion_si_se_reenvia(tmp_path):
    ruta = tmp_path / "envios.json"
    enviados = []
    envios.enviar_una_vez("accion:2026-11", "MANTENER|colchon_o_banda", enviados.append, ruta)
    assert envios.enviar_una_vez("accion:2026-11", "COMPRAR|cuota", enviados.append, ruta)
    assert len(enviados) == 2


def test_envio_fallido_no_se_registra_y_se_reintenta(tmp_path):
    ruta = tmp_path / "envios.json"

    def falla(_):
        raise RuntimeError("Telegram caído")

    with pytest.raises(RuntimeError):
        envios.enviar_una_vez("salud", "aviso", falla, ruta)
    assert not ruta.exists()
    enviados = []
    assert envios.enviar_una_vez("salud", "aviso", enviados.append, ruta)


def test_contexto_publico_no_tiene_iconos_de_color_ni_instrucciones():
    import pandas as pd

    fila = pd.Series({"valor_justo": -0.5, "cobre": 0.1})
    a = {"estado": "CARO", "precio": 990.0, "fecha": "2026-10-23", "compuesto": -0.6, "fila": fila}
    texto = reporte.contexto_publico(a, [])
    assert "Contexto (no es señal)" in texto
    assert "🔴" not in texto and "🟢" not in texto
    assert not any(palabra in texto for palabra in ("MANTENER", "VENDER", "COMPRAR"))
    assert "Recomendación" not in texto and "compra tu" not in texto.lower()

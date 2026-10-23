from datetime import date

from radar import almacen
from radar.fuentes.base import Punto


def test_guardar_fusiona_y_cuenta_solo_lo_nuevo_o_revisado(tmp_path):
    a = [Punto("usdclp", date(2026, 1, 2), 950.0, "x"), Punto("usdclp", date(2026, 1, 5), 955.0, "x")]
    assert almacen.guardar(a, tmp_path) == {"usdclp": 2}
    # mismo dato -> 0 cambios; revisión de un valor -> 1 cambio; fecha nueva -> 1 cambio
    b = [Punto("usdclp", date(2026, 1, 2), 950.0, "x"), Punto("usdclp", date(2026, 1, 5), 956.0, "x"),
         Punto("usdclp", date(2026, 1, 6), 960.0, "x")]
    assert almacen.guardar(b, tmp_path) == {"usdclp": 2}
    s = almacen.leer("usdclp", tmp_path)
    assert s.tolist() == [950.0, 956.0, 960.0]
    assert s.index.is_monotonic_increasing


def test_tabla_alinea_a_dias_del_dolar_sin_inventar_mas_de_7_dias(tmp_path):
    almacen.guardar([Punto("usdclp", date(2026, 3, d), 900.0 + d, "x") for d in (2, 3, 4, 20)], tmp_path)
    almacen.guardar([Punto("vix", date(2026, 3, 2), 20.0, "x")], tmp_path)
    t = almacen.tabla(["usdclp", "vix"], tmp_path)
    assert t["vix"].tolist()[:3] == [20.0, 20.0, 20.0]
    assert t["vix"].isna().iloc[-1]  # el 20-03 está a 18 días del último VIX: no se arrastra

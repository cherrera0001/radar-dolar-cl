from datetime import date

import pandas as pd

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
    # usdclp fechado 3, 4, 5 y 20-mar corresponde al mercado del 2, 3, 4 y 19-mar (desfase 1)
    almacen.guardar([Punto("usdclp", date(2026, 3, d), 900.0 + d, "x") for d in (3, 4, 5, 20)], tmp_path)
    almacen.guardar([Punto("vix", date(2026, 3, 2), 20.0, "x")], tmp_path)
    t = almacen.tabla(["usdclp", "vix"], tmp_path)
    assert [d.day for d in t.index] == [2, 3, 4, 19]
    assert t["vix"].tolist()[:3] == [20.0, 20.0, 20.0]
    assert t["vix"].isna().iloc[-1]  # el 19-03 está a 17 días del último VIX: no se arrastra


def test_tabla_pone_cada_serie_en_su_dia_de_mercado(tmp_path):
    """Mercado sintético: el valor de cada día es su número de día. Las fuentes lo publican
    desfasado (usdclp +1 hábil, cobre +2 hábiles); tras alinear, la fila t debe traer el día t."""
    mercado = pd.bdate_range("2026-03-02", "2026-03-31")
    publica = lambda serie, n: [Punto(serie, (d + pd.offsets.BDay(n)).date(), 900.0 + d.day, "x") for d in mercado]  # noqa: E731
    almacen.guardar(publica("usdclp", 1), tmp_path)
    almacen.guardar([Punto("cobre_lb", p.fecha, p.valor - 896.0, "x") for p in publica("cobre_lb", 2)], tmp_path)
    t = almacen.tabla(["usdclp", "cobre_lb"], tmp_path)
    assert (t.index == mercado).all()
    assert (t["usdclp"] - 900.0 == t.index.day).all()
    assert (t["cobre_lb"] - 4.0 == t.index.day).all()

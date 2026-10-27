"""Conciliación BCCh vs mindicador en el dólar observado: avisa solo si la divergencia se repite."""

from datetime import date

from radar import conciliacion

D = [date(2026, 10, dia) for dia in (20, 21, 22, 23)]


def test_valores_iguales_no_avisan():
    bcch = {d: 900.0 for d in D}
    assert conciliacion.aviso(bcch, dict(bcch)) is None


def test_divergencia_en_los_dos_ultimos_dias_avisa_con_las_fechas():
    mind = {d: 900.0 for d in D}
    bcch = {**mind, D[2]: 905.0, D[3]: 906.0}  # +0,56 % y +0,67 %
    aviso = conciliacion.aviso(bcch, mind)
    assert aviso is not None and "2026-10-22" in aviso and "2026-10-23" in aviso


def test_una_divergencia_aislada_no_avisa():
    mind = {d: 900.0 for d in D}
    bcch = {**mind, D[3]: 910.0}  # solo el último día
    assert conciliacion.aviso(bcch, mind) is None


def test_fechas_en_comun_insuficientes_no_avisan():
    assert conciliacion.aviso({D[0]: 900.0}, {D[0]: 950.0}) is None


def test_sin_credenciales_la_actualizacion_lo_dice_y_sigue(tmp_path, monkeypatch):
    from radar import actualizar
    from radar.fuentes import bcentral, fred, mindicador
    from radar.fuentes.base import Punto

    monkeypatch.delenv("BCCH_USER", raising=False)
    monkeypatch.delenv("BCCH_PASS", raising=False)
    hoy = date(2026, 10, 27)
    monkeypatch.setattr(mindicador, "descargar", lambda serie, anio: [Punto(serie, hoy, 950.0, "mindicador.cl")])
    monkeypatch.setattr(fred, "descargar", lambda serie, desde: [])
    r = actualizar.actualizar(hoy=hoy, base=tmp_path)
    assert any("faltan BCCH_USER" in e for e in r.errores)
    assert r.cambios.get("usdclp", 0) == 1
    assert bcentral.credenciales() is None

from datetime import date

from radar import actualizar, almacen
from radar.fuentes import fred, mindicador
from radar.fuentes.base import Punto


def test_descarta_datos_con_fecha_futura(tmp_path, monkeypatch):
    hoy = date(2026, 10, 24)

    def fake(serie, anio):
        return [Punto(serie, date(2026, 10, 23), 986.58, "mindicador.cl"),
                Punto(serie, date(2026, 10, 26), 990.35, "mindicador.cl")]

    monkeypatch.setattr(mindicador, "descargar", fake)
    monkeypatch.setattr(fred, "descargar", lambda serie, desde: [])
    actualizar.actualizar(hoy=hoy, base=tmp_path)
    assert almacen.leer("usdclp", tmp_path).index.max().date() == date(2026, 10, 23)

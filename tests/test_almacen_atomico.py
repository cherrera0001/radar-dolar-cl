"""`almacen.guardar` no debe dejar un CSV truncado si la escritura muere a mitad."""

import csv
from datetime import date

import pytest

from radar import almacen
from radar.fuentes.base import Punto


def test_un_fallo_al_escribir_no_toca_el_csv_existente(tmp_path, monkeypatch):
    almacen.guardar([Punto("usdclp", date(2026, 10, 1), 900.0, "mindicador.cl")], tmp_path)
    original = almacen.ruta("usdclp", tmp_path).read_text(encoding="utf-8")

    escritor_real = csv.writer

    def escritor_que_muere_con_el_encabezado(f, **kwargs):
        w = escritor_real(f, **kwargs)

        class Interrumpido:
            def writerow(self, fila):
                if fila[0] == "fecha":
                    raise OSError("el job murió a mitad de la escritura")
                w.writerow(fila)

        return Interrumpido()

    monkeypatch.setattr(almacen.csv, "writer", escritor_que_muere_con_el_encabezado)
    with pytest.raises(OSError):
        almacen.guardar([Punto("usdclp", date(2026, 10, 2), 901.0, "mindicador.cl")], tmp_path)

    assert almacen.ruta("usdclp", tmp_path).read_text(encoding="utf-8") == original
    assert not list(tmp_path.glob("*.tmp"))

import pandas as pd

from radar import reporte


def test_alerta_explica_que_movio_el_puntaje():
    fila = pd.Series({"valor_justo": -0.9, "cobre": 0.1, "dxy": -0.5})
    previas = {"valor_justo": -0.2, "cobre": 0.1, "dxy": -0.5}
    a = {"estado": "CARO", "precio": 990.0, "fecha": "2026-10-23", "compuesto": -0.6, "fila": fila}
    texto = reporte.alerta(a, "NORMAL", previas)
    assert "Qué cambió" in texto
    assert "→" in texto and "-0,20 → -0,90" in texto
    assert reporte.valores_senales(fila)["dxy"] == -0.5

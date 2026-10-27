"""R-07: los textos públicos describen, no ordenan. Las órdenes (COMPRAR/VENDER/MANTENER) viven solo en decision.py
y solo se envían al chat del dueño (constitución I y VI)."""

import re

import pandas as pd
import pytest

from radar import reporte

PROHIBIDO = re.compile(r"\b(compre|venda|mantenga|compra tu|vende solo|vende|compra)\b", re.IGNORECASE)


@pytest.mark.parametrize("estado", ["BARATO", "NORMAL", "CARO", "SIN DATOS"])
def test_contexto_publico_no_da_ordenes(estado):
    a = {"estado": estado, "fecha": "2026-10-27", "precio": 950.0, "compuesto": 0.1}
    texto = reporte.contexto_publico(a, (pd.Timestamp("2026-10-27").date(), 950.0), 0.5, "2012-11", "", [])
    assert not PROHIBIDO.search(texto), texto


def test_alerta_publica_no_da_ordenes():
    fila = pd.Series({"compuesto": 0.3, "valor_justo": 0.3})
    a = {"estado": "BARATO", "fecha": "2026-10-27", "precio": 950.0, "compuesto": 0.3, "fila": fila}
    assert not PROHIBIDO.search(reporte.alerta(a, "NORMAL"))

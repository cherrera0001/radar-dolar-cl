"""Prueba de humo del tablero: abre sin excepciones y muestra sus cinco pestañas."""

from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

PESTANAS = ["Calibración", "Radar vs DCA", "Estacionalidad", "Correlación", "Salud de datos"]


def test_tablero_abre_sin_excepciones_y_con_sus_pestanas():
    at = AppTest.from_file(str(Path(__file__).parents[1] / "streamlit_app.py"), default_timeout=240).run()
    assert not at.exception, [e.value for e in at.exception]
    assert not at.error, [e.value for e in at.error]
    assert [t.label for t in at.tabs] == PESTANAS
    assert len(at.metric) >= 3

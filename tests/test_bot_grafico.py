"""El gráfico del bot usa un único archivo temporal: no se acumula un directorio por consulta (R-15)."""

from pathlib import Path

import numpy as np
import pandas as pd

from radar import bot, senales


def test_consultas_repetidas_del_grafico_no_crean_directorios_nuevos(monkeypatch, tmp_path):
    monkeypatch.setattr(bot.tempfile, "gettempdir", lambda: str(tmp_path))
    idx = pd.bdate_range("2024-01-01", periods=300)
    df = pd.DataFrame({"usdclp": np.linspace(900, 950, 300)}, index=idx)
    monkeypatch.setattr(bot, "_datos", lambda: (df, senales.calcular(df), None))

    primera = bot._grafico("").archivos[0][1]
    segunda = bot._grafico("").archivos[0][1]

    assert primera == segunda == Path(tmp_path) / "radar-grafico.png"
    assert [p for p in tmp_path.iterdir() if p.is_dir()] == []

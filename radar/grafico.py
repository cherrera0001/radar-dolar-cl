"""Gráfico PNG del último año: precio del dólar y puntaje del semáforo. Descriptivo."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .reporte import num
from .senales import UMBRAL, estado

COLORES = {"BARATO": "#2e7d32", "NORMAL": "#f9a825", "CARO": "#c62828", "SIN DATOS": "#9e9e9e"}


def generar(df: pd.DataFrame, senales: pd.DataFrame, destino: Path, dias: int = 365) -> Path:
    # Importación diferida: matplotlib solo hace falta cuando alguien pide el gráfico.
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    precio = df["usdclp"].dropna().tail(dias)
    comp = senales["compuesto"].reindex(precio.index)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    ax1.plot(precio.index, precio.values, color="#1f4e79", lw=1.6)
    ax1.set_title(f"Dólar observado, último año · hoy ${num(precio.iloc[-1])}")
    ax1.grid(alpha=0.3)
    ax2.bar(comp.index, comp.fillna(0).values, color=[COLORES[estado(v)] for v in comp.values], width=1.0)
    ax2.axhline(UMBRAL, ls="--", color=COLORES["BARATO"], lw=1)
    ax2.axhline(-UMBRAL, ls="--", color=COLORES["CARO"], lw=1)
    ax2.set_ylabel("puntaje")
    ax2.grid(alpha=0.3)
    fig.text(0.01, 0.01, "Descriptivo, no es asesoría. Fuentes: mindicador.cl, FRED.", fontsize=8)
    fig.tight_layout()
    fig.savefig(destino, dpi=110)
    plt.close(fig)
    return destino

"""¿Las señales le ganan a comprar lo mismo todos los meses (DCA)?

Ambas estrategias gastan exactamente el mismo presupuesto mensual:

- DCA:   todo el presupuesto el primer día hábil del mes.
- Radar: 50% el primer día hábil; el otro 50% el primer día del mes en que el
         compuesto llega a COMPRAR, o el último día hábil si eso no ocurre.

Se compara cuántos dólares obtuvo cada una. Solo se usan meses completos y con
señal disponible desde el inicio del mes. Si el radar no le gana a DCA, el
reporte lo dice: esa es la prueba de que las señales aportan algo.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .senales import UMBRAL


@dataclass(frozen=True)
class ResultadoBacktest:
    desde: str
    hasta: str
    meses: int
    usd_dca: float
    usd_radar: float
    precio_dca: float  # CLP pagados por dólar en promedio
    precio_radar: float
    meses_mejor: int
    meses_peor: int

    @property
    def mejora_pct(self) -> float:
        return (self.usd_radar / self.usd_dca - 1.0) * 100.0


def backtest(precios: pd.Series, compuesto: pd.Series, presupuesto: float = 100_000.0,
             umbral: float = UMBRAL) -> ResultadoBacktest | None:
    df = pd.DataFrame({"p": precios, "c": compuesto}).dropna(subset=["p"])
    if df.empty:
        return None
    ultimo_mes = df.index.max().to_period("M")
    usd_dca = usd_radar = 0.0
    meses = mejor = peor = 0
    usados = []
    for periodo, g in df.groupby(df.index.to_period("M")):
        if periodo == ultimo_mes or g["c"].isna().iloc[0]:
            continue  # mes en curso o sin señal desde el primer día
        p0 = g["p"].iloc[0]
        senal = g.index[g["c"] >= umbral]
        p_tactico = g["p"].loc[senal[0]] if len(senal) else g["p"].iloc[-1]
        u_dca = presupuesto / p0
        u_radar = 0.5 * presupuesto / p0 + 0.5 * presupuesto / p_tactico
        usd_dca += u_dca
        usd_radar += u_radar
        meses += 1
        mejor += u_radar > u_dca
        peor += u_radar < u_dca
        usados.append(periodo)
    if not meses:
        return None
    gasto = presupuesto * meses
    return ResultadoBacktest(
        desde=str(usados[0]), hasta=str(usados[-1]), meses=meses,
        usd_dca=usd_dca, usd_radar=usd_radar,
        precio_dca=gasto / usd_dca, precio_radar=gasto / usd_radar,
        meses_mejor=mejor, meses_peor=peor,
    )

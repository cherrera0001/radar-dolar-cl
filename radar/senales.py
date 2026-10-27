"""Señales para ahorro de largo plazo en dólares.

Cada señal produce un puntaje en [-1, 1]:  +1 = dólar BARATO frente a lo que lo mueve,
-1 = dólar CARO. Todas son causales: el valor de una fecha solo usa datos
hasta esa fecha (ventanas móviles y desplazamientos hacia atrás), así el backtest
no ve el futuro.

Los pesos son una hipótesis a priori, no se optimizan con la historia: optimizarlos
sobre el mismo período que se evalúa sobreajustaría el backtest.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

DIAS_ANIO = 252
UMBRAL = 0.25  # |compuesto| >= UMBRAL -> BARATO / CARO
MIN_SENALES = 3  # con menos señales disponibles no se emite compuesto
# Días hábiles de desfase entre el compuesto y la decisión: la decisión del día d usa la señal de d − 2.
# El insumo más lento es el cobre (2 días hábiles, almacen.DESFASE_MERCADO). Antes era 1 (#19, R-06).
DESFASE_DECISION = 2

SERIES = ["usdclp", "cobre_lb", "dxy", "tpm", "fed_funds", "vix"]


@dataclass(frozen=True)
class Definicion:
    titulo: str
    peso: float
    idea: str


DEFINICIONES: dict[str, Definicion] = {
    "valor_justo": Definicion(
        "Valor justo (cobre + dólar global)", 0.30,
        "Modelo móvil de 2 años: log(dólar) ~ log(cobre) + log(DXY). Dólar bajo su valor justo -> comprar."),
    "valoracion": Definicion(
        "Posición en el último año", 0.25,
        "Percentil del dólar observado en 12 meses. Cerca del mínimo -> comprar; del máximo -> esperar."),
    "cobre": Definicion(
        "Tendencia del cobre (3 meses)", 0.15,
        "Cobre al alza trae dólares al país y presiona el tipo de cambio a la baja -> esperar."),
    "dxy": Definicion(
        "Tendencia del dólar global (3 meses)", 0.10,
        "Dólar fortaleciéndose en el mundo suele arrastrar al dólar en Chile al alza -> comprar antes."),
    "tasas": Definicion(
        "Diferencial de tasas Chile - EE.UU. (6 meses)", 0.10,
        "Si el diferencial TPM - Fed se estrecha, el peso pierde atractivo y el dólar tiende a subir -> comprar."),
    "riesgo": Definicion(
        "Aversión al riesgo (VIX)", 0.10,
        "En pánicos globales el dólar se dispara y suele devolverse -> esperar."),
}


def _clip(s: pd.Series) -> pd.Series:
    return s.clip(-1.0, 1.0)


def _cambio(s: pd.Series, dias: int) -> pd.Series:
    return s / s.shift(dias) - 1.0


def valor_justo(df: pd.DataFrame, ventana: int = 2 * DIAS_ANIO, minimo: int = 400) -> pd.DataFrame:
    """Regresión móvil fuera de muestra: se ajusta con los días [t-ventana, t-1] y se predice t.

    Devuelve columnas: justo (CLP), desvio_pct (dólar/justo - 1), z (residuo estandarizado).
    """
    y = np.log(df["usdclp"].to_numpy(dtype=float))
    x1 = np.log(df["cobre_lb"].to_numpy(dtype=float))
    x2 = np.log(df["dxy"].to_numpy(dtype=float))
    n = len(df)
    justo = np.full(n, np.nan)
    z = np.full(n, np.nan)
    validos = np.isfinite(y) & np.isfinite(x1) & np.isfinite(x2)
    for t in range(n):
        if not validos[t]:
            continue
        ini = max(0, t - ventana)
        m = validos[ini:t]
        if m.sum() < minimo:
            continue
        X = np.column_stack([np.ones(m.sum()), x1[ini:t][m], x2[ini:t][m]])
        yy = y[ini:t][m]
        coef, *_ = np.linalg.lstsq(X, yy, rcond=None)
        resid = yy - X @ coef
        sd = resid.std(ddof=3)
        pred = coef[0] + coef[1] * x1[t] + coef[2] * x2[t]
        justo[t] = np.exp(pred)
        z[t] = (y[t] - pred) / sd if sd > 0 else np.nan
    out = pd.DataFrame({"justo": justo, "z": z}, index=df.index)
    out["desvio_pct"] = df["usdclp"] / out["justo"] - 1.0
    return out


def calcular(df: pd.DataFrame) -> pd.DataFrame:
    """Puntajes por señal + compuesto + variables auxiliares para explicar."""
    s = pd.DataFrame(index=df.index)
    disponibles = set(df.columns)

    if {"usdclp", "cobre_lb", "dxy"} <= disponibles:
        vj = valor_justo(df)
        s["justo"], s["desvio_pct"] = vj["justo"], vj["desvio_pct"]
        s["valor_justo"] = _clip(-vj["z"] / 2.0)

    if "usdclp" in disponibles:
        pct = df["usdclp"].rolling(DIAS_ANIO, min_periods=200).rank(pct=True)
        s["percentil_1a"] = pct
        s["valoracion"] = _clip(1.0 - 2.0 * pct)

    if "cobre_lb" in disponibles:
        s["cobre_3m"] = _cambio(df["cobre_lb"], 63)
        s["cobre"] = _clip(-s["cobre_3m"] / 0.15)

    if "dxy" in disponibles:
        s["dxy_3m"] = _cambio(df["dxy"], 63)
        s["dxy"] = _clip(s["dxy_3m"] / 0.05)

    if {"tpm", "fed_funds"} <= disponibles:
        dif = df["tpm"] - df["fed_funds"]
        s["diferencial"] = dif
        s["diferencial_6m"] = dif - dif.shift(126)
        s["tasas"] = _clip(-s["diferencial_6m"] / 1.5)

    if "vix" in disponibles:
        media = df["vix"].rolling(DIAS_ANIO, min_periods=200).mean()
        desv = df["vix"].rolling(DIAS_ANIO, min_periods=200).std()
        s["vix_z"] = (df["vix"] - media) / desv
        s["riesgo"] = _clip(-s["vix_z"] / 2.0)

    nombres = [k for k in DEFINICIONES if k in s.columns]
    puntajes = s[nombres]
    pesos = pd.Series({k: DEFINICIONES[k].peso for k in nombres})
    presentes = puntajes.notna()
    suma_pesos = presentes.mul(pesos, axis=1).sum(axis=1)
    compuesto = puntajes.fillna(0.0).mul(pesos, axis=1).sum(axis=1) / suma_pesos
    s["n_senales"] = presentes.sum(axis=1)
    s["compuesto"] = compuesto.where(s["n_senales"] >= MIN_SENALES)
    signo = np.sign(s["compuesto"])
    s["acuerdo"] = (np.sign(puntajes).eq(signo, axis=0) & presentes).sum(axis=1)
    return s


def estado(compuesto: float) -> str:
    """Estado descriptivo del precio. No es una orden: ninguna regla de timing le ha ganado
    a DCA fuera de muestra (docs/INVESTIGACION.md)."""
    if not np.isfinite(compuesto):
        return "SIN DATOS"
    if compuesto >= UMBRAL:
        return "BARATO"
    if compuesto <= -UMBRAL:
        return "CARO"
    return "NORMAL"

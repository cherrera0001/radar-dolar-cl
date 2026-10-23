"""Evaluación walk-forward de estrategias de compra (issues #9 y #10).

Separación fija: los parámetros se eligen SOLO con el período de diseño (hasta 2019-12)
y cada estrategia se evalúa UNA vez en el período de prueba (desde 2020-01). El
resultado que importa es el de prueba; el de diseño está sobreajustado por construcción.

Simulador: cada mes entra una cuota de pesos a una caja. Cada día la estrategia decide
cuántos pesos de la caja convertir a dólares. El último día del período la caja se
convierte entera, así todas las estrategias gastan exactamente lo mismo.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import pandas as pd

from .senales import UMBRAL

CORTE = pd.Timestamp("2020-01-01")  # diseño < CORTE <= prueba
PRESUPUESTO = 100_000.0


@dataclass(frozen=True)
class Dia:
    fecha: pd.Timestamp
    precio: float
    primer_dia_mes: bool
    ultimo_dia_mes: bool
    compuesto: float
    desvio: float  # dólar / valor justo - 1 (NaN si no hay modelo)


class Estrategia:
    nombre = "base"

    def reiniciar(self) -> None:
        pass

    def decidir(self, dia: Dia, caja: float, presupuesto: float) -> float:
        """Pesos a convertir hoy (se acota a [0, caja])."""
        raise NotImplementedError


class DCA(Estrategia):
    nombre = "DCA (todo el día 1)"

    def decidir(self, dia, caja, presupuesto):
        return caja if dia.primer_dia_mes else 0.0


class RadarV01(Estrategia):
    """50% el día 1; 50% al primer BARATO del mes o el último día hábil."""
    nombre = "Radar v0.1 (media cuota táctica)"

    def reiniciar(self):
        self.pendiente = 0.0

    def decidir(self, dia, caja, presupuesto):
        gasto = 0.0
        if dia.primer_dia_mes:
            gasto += 0.5 * presupuesto
            self.pendiente = 0.5 * presupuesto
        if self.pendiente and (dia.compuesto >= UMBRAL or dia.ultimo_dia_mes):
            gasto += self.pendiente
            self.pendiente = 0.0
        return gasto


@dataclass
class Acumulacion(Estrategia):
    """#10: si el dólar está caro frente a su valor justo, guardar la cuota (hasta `max_cuotas`)
    y convertir toda la caja cuando el desvío vuelve bajo `salida`."""
    max_cuotas: int
    entrada: float  # desvío sobre el cual se guarda la cuota (dólar caro)
    salida: float  # desvío bajo el cual se convierte la caja

    @property
    def nombre(self) -> str:
        return f"Acumulación (≤{self.max_cuotas} cuotas, guarda si caro >{self.entrada:.0%}, compra si ≤{self.salida:.0%})"

    def decidir(self, dia, caja, presupuesto):
        if pd.isna(dia.desvio):
            return caja if dia.primer_dia_mes else 0.0  # sin modelo: se comporta como DCA
        if dia.primer_dia_mes:
            if caja > self.max_cuotas * presupuesto + 1e-6:
                return caja  # tope de riesgo: nunca más de max_cuotas sin comprar
            return 0.0 if dia.desvio > self.entrada else caja
        return caja if dia.desvio <= self.salida else 0.0


@dataclass(frozen=True)
class Resultado:
    estrategia: str
    desde: str
    hasta: str
    meses: int
    usd: float
    gasto: float
    max_meses_sin_comprar: int
    max_caja_cuotas: float

    @property
    def precio_medio(self) -> float:
        return self.gasto / self.usd


def preparar(precios: pd.Series, senales: pd.DataFrame) -> pd.DataFrame:
    """Días con precio, marcando inicio/fin de mes. Solo meses completos con señal desde el día 1.

    Las señales se desplazan 1 día (#19): la decisión del día d usa lo conocido hasta d-1.
    """
    df = pd.DataFrame({
        "precio": precios,
        "compuesto": senales["compuesto"].shift(1),
        "desvio": senales.get("desvio_pct", pd.Series(float("nan"), index=senales.index)).shift(1),
    }).dropna(subset=["precio"])
    mes = df.index.to_period("M")
    df["primer"] = ~mes.duplicated(keep="first")
    df["ultimo"] = ~mes.duplicated(keep="last")
    primeros = df[df["primer"]]
    validos = set(primeros.index[primeros["compuesto"].notna()].to_period("M")) - {df.index.max().to_period("M")}
    return df[mes.isin(validos)]


def simular(df: pd.DataFrame, estrategia: Estrategia, desde=None, hasta=None,
            presupuesto: float = PRESUPUESTO) -> Resultado | None:
    tramo = df.loc[(df.index >= (desde or df.index.min())) & (df.index < (hasta or df.index.max() + pd.Timedelta(days=1)))]
    if tramo.empty:
        return None
    estrategia.reiniciar()
    caja = usd = gasto_total = 0.0
    sin_comprar = max_sin_comprar = 0
    compro_mes = False
    max_caja = 0.0
    filas = list(tramo.itertuples())
    for i, f in enumerate(filas):
        if f.primer:
            if i > 0:
                sin_comprar = 0 if compro_mes else sin_comprar + 1
                max_sin_comprar = max(max_sin_comprar, sin_comprar)
            compro_mes = False
            caja += presupuesto
            max_caja = max(max_caja, caja / presupuesto)
        dia = Dia(f.Index, f.precio, f.primer, f.ultimo, f.compuesto, f.desvio)
        gasto = min(max(estrategia.decidir(dia, caja, presupuesto), 0.0), caja)
        if i == len(filas) - 1:
            gasto = caja  # cierre: lo que quede se convierte hoy
        if gasto > 0:
            usd += gasto / f.precio
            caja -= gasto
            gasto_total += gasto
            compro_mes = True
    sin_comprar = 0 if compro_mes else sin_comprar + 1
    max_sin_comprar = max(max_sin_comprar, sin_comprar)
    meses = int(tramo["primer"].sum())
    return Resultado(estrategia.nombre, str(tramo.index.min().to_period("M")), str(tramo.index.max().to_period("M")),
                     meses, usd, gasto_total, max_sin_comprar, max_caja)


def mejora_pct(r: Resultado, base: Resultado) -> float:
    return (r.usd / base.usd - 1.0) * 100.0


GRILLA = {"max_cuotas": (2, 3, 6), "entrada": (0.02, 0.05, 0.08), "salida": (0.0, 0.02)}


def elegir_parametros(df: pd.DataFrame, corte: pd.Timestamp = CORTE) -> tuple[Acumulacion, float]:
    """Mejor combinación de la grilla usando SOLO el período de diseño (< corte)."""
    base = simular(df, DCA(), hasta=corte)
    mejor, mejor_valor = None, float("-inf")
    for n, e, s in itertools.product(*GRILLA.values()):
        if s >= e:
            continue
        estrategia = Acumulacion(n, e, s)
        valor = mejora_pct(simular(df, estrategia, hasta=corte), base)
        if valor > mejor_valor:
            mejor, mejor_valor = estrategia, valor
    return mejor, mejor_valor


def walk_forward(df: pd.DataFrame, corte: pd.Timestamp = CORTE) -> dict:
    elegida, en_diseno = elegir_parametros(df, corte)
    estrategias = [DCA(), RadarV01(), elegida]
    diseno = {e.nombre: simular(df, e, hasta=corte) for e in estrategias}
    prueba = {e.nombre: simular(df, e, desde=corte) for e in estrategias}
    return {"elegida": elegida, "mejora_diseno": en_diseno, "diseno": diseno, "prueba": prueba}

"""Lectura en lenguaje simple del estado del radar. Funciones puras: reciben la fila de señales y devuelven texto.

Reglas de esta capa:
- Describe, no aconseja: ningún texto da órdenes de compra, venta ni mantención.
- Sin datos no es cero: una señal ausente se nombra como "sin datos" y no entra en el promedio.
- Con menos de MIN_SENALES no hay lectura: se dice, en vez de inventar un semáforo.
- Toda cifra va con su fecha, para que quien lee sepa qué tan viejo es el dato.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from . import reporte
from .senales import DEFINICIONES, MIN_SENALES, UMBRAL

CAMBIO_MINIMO = 0.1  # diferencia en el puntaje de una señal que se considera cambio


@dataclass(frozen=True)
class Aporte:
    nombre: str  # clave en DEFINICIONES
    titulo: str
    puntaje: float  # en [-1, 1]: + barato, - caro
    contribucion: float  # su parte del compuesto: suman el compuesto


def _ok(x) -> bool:
    return x is not None and isinstance(x, int | float) and math.isfinite(x)


def aportes(fila: pd.Series) -> list[Aporte]:
    """Qué aporta cada señal disponible al compuesto, del que más pesa al que menos."""
    disponibles = {k: d for k, d in DEFINICIONES.items() if _ok(fila.get(k))}
    total = sum(d.peso for d in disponibles.values())
    if not disponibles or total == 0:
        return []
    out = [Aporte(k, d.titulo, float(fila[k]), float(fila[k]) * d.peso / total) for k, d in disponibles.items()]
    return sorted(out, key=lambda a: abs(a.contribucion), reverse=True)


def _direccion(puntaje: float) -> str:
    if abs(puntaje) < CAMBIO_MINIMO:
        return "neutral"
    return "barato" if puntaje > 0 else "caro"


ATRASO_TOLERADO_DIAS_HABILES = 1  # el dato de ayer es normal: el dólar observado se publica con un día de rezago


def _atraso(fecha_dato: str, hoy: date) -> str | None:
    dias = int(np.busday_count(date.fromisoformat(fecha_dato), hoy))
    if dias <= ATRASO_TOLERADO_DIAS_HABILES:
        return None
    return (f"Atención: el último dato es del {fecha_dato}, hace {dias} días hábiles. "
            "Puede que la actualización de hoy no haya llegado.")


def explicar(a: dict, fila: pd.Series, hoy: date | None = None) -> list[str]:
    """Lectura del estado de hoy, en frases cortas. `hoy` activa el aviso de datos atrasados."""
    compuesto = fila.get("compuesto")
    if not _ok(compuesto):
        n = int(fila.get("n_senales", 0) or 0)
        return [f"No hay suficientes señales para una lectura: hay {n} y se necesitan al menos {MIN_SENALES}."]

    lineas = [f"Semáforo {a['estado']} con datos al {a['fecha']}. Dólar observado: ${reporte.num(a['precio'])}."]
    atraso = _atraso(a["fecha"], hoy) if hoy else None
    if atraso:
        lineas.append(atraso)
    lineas += [
        f"Puntaje {reporte.num(compuesto, 2)}; el semáforo cambia de color a partir de ±{reporte.num(UMBRAL, 2)}.",
        "",
        "Lo que más pesa:",
    ]
    for ap in aportes(fila)[:3]:
        detalle = reporte.explicacion(ap.nombre, fila)
        lineas.append(f" · {ap.titulo}: {_direccion(ap.puntaje)}. {detalle[:1].upper()}{detalle[1:]}.")

    n = int(fila.get("n_senales", 0) or 0)
    acuerdo = int(fila.get("acuerdo", 0) or 0)
    lineas += ["", f"{acuerdo} de {n} señales apuntan en la misma dirección que el puntaje."]

    sin_datos = [d.titulo for k, d in DEFINICIONES.items() if not _ok(fila.get(k))]
    if sin_datos:
        lineas += ["", "Sin datos para: " + "; ".join(sin_datos) + ". No cuentan en el puntaje."]
    return lineas


def cambios(fila: pd.Series, previas: dict[str, float] | None, fecha_previa: str | None) -> list[str]:
    """Qué señales cambiaron desde la última corrida guardada (data/estado.json)."""
    if not previas or not fecha_previa:
        return ["No hay una lectura anterior guardada para comparar."]
    lineas = [f"Comparado con la lectura del {fecha_previa}:"]
    movidas = []
    for k, d in DEFINICIONES.items():
        ahora, antes = fila.get(k), previas.get(k)
        if _ok(ahora) and _ok(antes) and abs(ahora - antes) >= CAMBIO_MINIMO:
            movidas.append(f" · {d.titulo}: {reporte.num(antes)} → {reporte.num(ahora)}")
    if not movidas:
        return [*lineas, " · Ninguna señal cambió de forma notoria."]
    return [*lineas, *movidas]


def glosario() -> list[str]:
    return [
        "Puntaje: resumen de las señales, entre −1 y +1. Positivo = dólar barato frente a lo que lo mueve.",
        f"Semáforo: BARATO si el puntaje es ≥ {reporte.num(UMBRAL, 2)}, CARO si es ≤ −{reporte.num(UMBRAL, 2)}, "
        "NORMAL entre ambos.",
        "Señal sin datos: no cuenta en el puntaje. Nunca se trata como neutra.",
        "Percentil 1 año: dónde está el dólar entre sus precios de los últimos 12 meses (0 = mínimo, 100 = máximo).",
        "Valor justo: precio que el dólar tendría según el cobre y el dólar global, en los últimos 2 años.",
        "DCA: comprar la misma cantidad de dólares cada mes. Es la referencia que el radar debe superar.",
        "Dato con fecha: el dólar observado se publica con un día de rezago; cada respuesta indica su fecha.",
    ]

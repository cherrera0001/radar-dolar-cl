"""Motor de decisión v1 (concilio 2026-10-23_220000): instrucciones del plan del dueño.

Precedencia: SIN SEÑAL > VENDER > MANTENER > COMPRAR.
La instrucción depende del perfil, del calendario y de la vigencia de los datos. No depende de predecir el
precio. El perfil personal NUNCA se versiona (constitución V): viene de la variable PERFIL_DUENO (secreto de
GitHub Actions) o de perfil.local.json (ignorado por git).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from . import almacen, metricas, reporte

PERFIL_LOCAL = Path("perfil.local.json")
VENTANA_COMPRA = range(1, 6)  # días del mes de cobro en que se emite COMPRAR
DIAS_CONFIRMACION = 180  # el perfil se confirma cada 6 meses
TOLERANCIA_BANDA = 10.0  # puntos porcentuales sobre w*


@dataclass(frozen=True)
class Perfil:
    w_objetivo: float  # w* en %, sobre patrimonio financiero
    w_actual: float  # peso actual del dólar en %
    colchon_completo: bool  # 6 meses de gasto + 100% de necesidades con fecha ≤ 12 meses
    deficit_usd: float  # necesidades ≤ 12 meses no cubiertas por el colchón; 0 si no hay
    confirmado: date  # última confirmación del perfil

    @classmethod
    def desde_dict(cls, d: dict) -> Perfil:
        return cls(
            w_objetivo=float(d["w_objetivo"]),
            w_actual=float(d["w_actual"]),
            colchon_completo=bool(d["colchon_completo"]),
            deficit_usd=float(d.get("deficit_usd", 0.0)),
            confirmado=date.fromisoformat(d["confirmado"]),
        )


@dataclass(frozen=True)
class Instruccion:
    accion: str  # SIN SEÑAL | VENDER | MANTENER | COMPRAR
    codigo: str  # estable: entra en la huella de deduplicación
    motivo: str  # texto para el dueño


def cargar_perfil(entorno=os.environ, ruta: Path = PERFIL_LOCAL) -> Perfil | None:
    crudo = entorno.get("PERFIL_DUENO") or (ruta.read_text(encoding="utf-8") if ruta.exists() else None)
    return Perfil.desde_dict(json.loads(crudo)) if crudo else None


def frescura_ok(hoy: date) -> bool:
    """Todas las series están dentro de su antigüedad máxima (constitución IV)."""
    tabla = metricas.salud(hoy)
    return all(
        fila["ultimo_dato"] is not None and fila["dias_sin_dato"] <= almacen.antiguedad_max(fila["serie"])
        for _, fila in tabla.iterrows()
    )


def decidir(perfil: Perfil | None, hoy: date, vigente: bool) -> Instruccion:
    """Llamar solo dentro de la ventana de compra (días 1 a 5). COMPRAR asume esa ventana."""
    if perfil is None:
        return Instruccion("SIN SEÑAL", "perfil_ausente", "No hay perfil configurado: no hay instrucción.")
    if (hoy - perfil.confirmado).days > DIAS_CONFIRMACION:
        return Instruccion("SIN SEÑAL", "perfil_vencido",
                           "El perfil no se confirma hace más de 6 meses: confírmalo antes de actuar.")
    if not vigente:
        return Instruccion("SIN SEÑAL", "insumo_vencido",
                           "Hay datos vencidos o sin datos: no se emite acción sobre datos viejos.")
    if perfil.deficit_usd > 0:
        return Instruccion("VENDER", "necesidad",
                           f"Necesidad a ≤ 12 meses no cubierta por el colchón: US$ {reporte.num(perfil.deficit_usd, 0)}. "
                           "Vende solo ese monto, en tramos mensuales, sin mirar el precio.")
    if not perfil.colchon_completo or perfil.w_actual > perfil.w_objetivo + TOLERANCIA_BANDA:
        return Instruccion("MANTENER", "colchon_o_banda",
                           "Colchón incompleto o dólar sobre tu peso objetivo: la cuota de este mes va a pesos.")
    return Instruccion("COMPRAR", "cuota",
                       "Compra tu cuota completa en el canal más barato verificado hoy, "
                       "nunca entre el comunicado de la RPM (18:00) y la apertura siguiente.")


def texto(instr: Instruccion, hoy: date, precio: float, fecha_dato: str, estado_actual: str) -> str:
    return "\n".join([
        f"Instrucción {hoy:%Y-%m} · {instr.accion}",
        instr.motivo,
        "",
        f"Contexto (no es señal): dólar observado ${reporte.num(precio)} ({fecha_dato}); semáforo {estado_actual}.",
        "Instrucción personal generada por el plan del dueño; no es asesoría para terceros.",
    ])

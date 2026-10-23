"""Descarga las series y las guarda. Una fuente que falla no detiene a las demás."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from . import almacen
from .fuentes import fred, mindicador
from .fuentes.base import FuenteError

ANIO_INICIO = 2012  # historia suficiente para ventanas de 2 años + backtest de ~12 años
MAX_ATRASO_DIAS = 7  # el dólar observado más reciente no debería tener más de esto


@dataclass
class Resultado:
    cambios: dict[str, int] = field(default_factory=dict)
    errores: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)


def actualizar(hoy: date | None = None, base: Path = almacen.DIR_SERIES) -> Resultado:
    hoy = hoy or date.today()
    r = Resultado()

    for serie in mindicador.SERIES:
        existe = almacen.ruta(serie, base).exists()
        # Sin historia: rellenar desde ANIO_INICIO. Con historia: año actual (y el anterior en enero).
        anios = range(ANIO_INICIO, hoy.year + 1) if not existe else sorted({hoy.year, (hoy - timedelta(days=31)).year})
        puntos = []
        try:
            for anio in anios:
                puntos += mindicador.descargar(serie, anio)
        except FuenteError as e:
            r.errores.append(str(e))
            continue
        r.cambios[serie] = almacen.guardar(puntos, base).get(serie, 0)

    for serie in fred.SERIES:
        try:
            puntos = fred.descargar(serie, desde=date(ANIO_INICIO, 1, 1))
        except FuenteError as e:
            r.errores.append(str(e))
            continue
        r.cambios[serie] = almacen.guardar(puntos, base).get(serie, 0)

    usd = almacen.leer("usdclp", base)
    if usd.empty:
        r.errores.append("usdclp: sin datos")
    else:
        atraso = (hoy - usd.index.max().date()).days
        if atraso > MAX_ATRASO_DIAS:
            r.avisos.append(f"usdclp: último dato del {usd.index.max().date()} ({atraso} días de atraso)")
    return r

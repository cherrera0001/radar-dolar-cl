"""Descarga las series y las guarda. Una fuente que falla no detiene a las demás."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from . import almacen, conciliacion
from .fuentes import bcentral, fred, mindicador, respaldo
from .fuentes.base import FuenteError

ANIO_INICIO = 2012  # historia suficiente para ventanas de 2 años + backtest de ~12 años


def _hasta(puntos, hoy: date):
    """Descarta datos con fecha posterior a hoy: no se pueden haber observado.

    mindicador.cl devolvió un dólar fechado 2026-10-26 el 2026-10-24.
    """
    return [p for p in puntos if p.fecha <= hoy]


@dataclass
class Resultado:
    cambios: dict[str, int] = field(default_factory=dict)
    errores: list[str] = field(default_factory=list)
    fallidas: set[str] = field(default_factory=set)  # series cuya descarga falló (para radar/salud.py)
    avisos: list[str] = field(default_factory=list)  # divergencias entre fuentes y respaldos en uso
    notas: list[str] = field(default_factory=list)  # informativo: va al log, no cuenta para el exit code


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
            puntos = _respaldo_usdclp(serie, r, e)
            if puntos is None:
                r.errores.append(str(e))
                r.fallidas.add(serie)
                continue
        r.cambios[serie] = almacen.guardar(_hasta(puntos, hoy), base).get(serie, 0)

    for serie in fred.SERIES:
        try:
            puntos = fred.descargar(serie, desde=date(ANIO_INICIO, 1, 1))
        except FuenteError as e:
            r.errores.append(str(e))
            r.fallidas.add(serie)
            continue
        r.cambios[serie] = almacen.guardar(_hasta(puntos, hoy), base).get(serie, 0)
    _conciliar(hoy, base, r)
    return r


def _respaldo_usdclp(serie: str, r: Resultado, original: FuenteError) -> list | None:
    """Si mindicador.cl falla para usdclp, completa con el respaldo en vez de congelar la serie.

    Devuelve los puntos del respaldo o None si no aplica (otra serie, respaldo desactivado o
    el respaldo también falló: en ese caso manda el error original, que es el dato relevante).
    La serie NO entra a `fallidas`: el dato quedó al día. El aviso tiene texto estable para que
    la deduplicación de envíos no lo repita mientras la situación no cambie; el error concreto
    va a las notas del log.
    """
    if serie != "usdclp" or not respaldo.activado():
        return None
    try:
        puntos = respaldo.descargar()
    except FuenteError as e:
        r.notas.append(f"usdclp: el respaldo {respaldo.FUENTE} tampoco respondió: {e}")
        return None
    r.notas.append(f"usdclp: mindicador.cl falló ({original}); se completó con {respaldo.FUENTE}")
    r.avisos.append(f"🟠 usdclp: mindicador.cl no respondió; se usa el respaldo {respaldo.FUENTE} "
                    f"(aproximado al dólar observado)")
    return puntos


def _conciliar(hoy: date, base: Path, r: Resultado) -> None:
    """Contrasta el dólar con BCCh. Si no se puede, lo deja dicho en los errores: nunca calla."""
    if bcentral.credenciales() is None:
        r.errores.append("conciliación BCCh no disponible: faltan BCCH_USER / BCCH_PASS")
        return
    try:
        aviso = conciliacion.revisar(hoy, base)
    except FuenteError as e:
        r.errores.append(f"conciliación BCCh no disponible: {e}")
        return
    if aviso:
        r.avisos.append(aviso)

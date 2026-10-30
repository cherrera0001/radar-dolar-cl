"""Bitácora de ejecuciones: una línea JSON por corrida en data/ejecuciones.jsonl.

Los logs de GitHub Actions caducan a los 90 días y solo se ven con `gh`; este archivo queda
versionado en el repo, así cualquiera puede auditar qué corrió, cuándo, cuánto duró y con qué
resultado sin salir de git. Rotación simple: al pasar de MAX_LINEAS se conserva la mitad final.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

ARCHIVO = Path("data/ejecuciones.jsonl")
MAX_LINEAS = 2000

_ACTUAL: Bitacora | None = None


class Bitacora:
    def __init__(self, comando: str, ruta: Path = ARCHIVO):
        self.comando = comando
        self.ruta = ruta
        self.inicio = datetime.now(UTC)
        self._t0 = time.monotonic()
        self._detalles: dict = {}

    def detalle(self, **campos) -> None:
        """Campos extra para la línea del log (p. ej. errores=3, atendidos=12)."""
        self._detalles.update(campos)

    def registrar(self, codigo: int, error: str = "") -> None:
        linea = {
            "ts": self.inicio.isoformat(timespec="seconds"),
            "comando": self.comando,
            "codigo": codigo,
            "duracion_s": round(time.monotonic() - self._t0, 2),
            "commit": _commit(),
            **self._detalles,
        }
        if error:
            linea["error"] = error
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with self.ruta.open("a", encoding="utf-8") as f:
            f.write(json.dumps(linea, ensure_ascii=False) + "\n")
        _rotar(self.ruta)


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              timeout=5).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return ""


def _rotar(ruta: Path) -> None:
    try:
        lineas = ruta.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    if len(lineas) <= MAX_LINEAS:
        return
    tmp = ruta.with_name(ruta.name + ".tmp")
    tmp.write_text("\n".join(lineas[-(MAX_LINEAS // 2):]) + "\n", encoding="utf-8")
    os.replace(tmp, ruta)


def iniciar(comando: str, ruta: Path = ARCHIVO) -> Bitacora:
    global _ACTUAL
    _ACTUAL = Bitacora(comando, ruta)
    return _ACTUAL


def actual() -> Bitacora | None:
    return _ACTUAL

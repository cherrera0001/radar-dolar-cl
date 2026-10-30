"""Registro de envíos (constitución VIII): un mensaje con la misma clave y el mismo contenido no se reenvía.

La clave identifica el mensaje (tipo y período). El contenido es la instrucción, no los números de contexto:
si la clave incluyera el precio, la misma instrucción se reenviaría cada día. Un envío fallido no se registra,
para reintentarlo en la siguiente corrida.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path

ARCHIVO_ENVIOS = Path("data/envios.json")
MAXIMO_CLAVES = 120  # ~10 años de mensajes mensuales


def huella(contenido: str) -> str:
    return hashlib.sha256(contenido.encode("utf-8")).hexdigest()[:16]


def _leer(ruta: Path) -> dict:
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}


def _ruta(ruta: Path | None) -> Path:
    # Se resuelve en la llamada (no como default) para que los tests puedan redirigir el archivo.
    return ruta if ruta is not None else ARCHIVO_ENVIOS


def ya_enviado(clave: str, contenido: str, ruta: Path | None = None) -> bool:
    return _leer(_ruta(ruta)).get(clave) == huella(contenido)


def registrar(clave: str, contenido: str, ruta: Path | None = None) -> None:
    destino = _ruta(ruta)
    datos = _leer(destino)
    datos[clave] = huella(contenido)
    while len(datos) > MAXIMO_CLAVES:
        datos.pop(next(iter(datos)))  # conserva las claves más recientes (orden de inserción)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def enviar_una_vez(clave: str, contenido: str, enviar: Callable[[str], None],
                   ruta: Path | None = None) -> bool:
    """Envía si no se envió antes con el mismo contenido. Devuelve True si envió."""
    if ya_enviado(clave, contenido, ruta):
        return False
    enviar(contenido)  # si falla, la excepción sale antes de registrar: se reintenta
    registrar(clave, contenido, ruta)
    return True

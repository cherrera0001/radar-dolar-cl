"""Telegram Bot API: envío y lectura de mensajes. El token viene de TELEGRAM_BOT_TOKEN.

El token nunca aparece en los errores. Los textos se envían sin formato: vienen de usuarios
y no deben interpretarse como Markdown ni HTML.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
import uuid
from pathlib import Path

API = "https://api.telegram.org/bot"
LIMITE_TEXTO = 4000  # Telegram admite 4096; margen para no cortar caracteres


class TelegramError(Exception):
    def __init__(self, mensaje: str, codigo: int | None = None):
        super().__init__(mensaje)
        self.codigo = codigo

    @property
    def permanente(self) -> bool:
        """Un 4xx (salvo 429) no cambia al reintentar: el chat bloqueó al bot, no existe o el texto es inválido."""
        return self.codigo is not None and 400 <= self.codigo < 500 and self.codigo != 429


def _llamar(metodo: str, cuerpo: bytes, ctype: str, timeout: float = 30.0):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise TelegramError("faltan TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID")
    req = urllib.request.Request(f"{API}{token}/{metodo}", data=cuerpo, headers={"Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (URL fija https)
            respuesta = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        # Telegram explica el error en el cuerpo (p. ej. "chat not found"); el token nunca se muestra.
        detalle = e.read().decode("utf-8", errors="replace")[:200]
        raise TelegramError(f"{metodo} HTTP {e.code}: {detalle}", codigo=e.code) from e
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise TelegramError(f"{metodo}: sin respuesta válida de Telegram ({type(e).__name__})") from e
    validar_respuesta(respuesta)
    return respuesta["result"]


def _json(metodo: str, datos: dict, timeout: float = 30.0):
    cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
    return _llamar(metodo, cuerpo, "application/json", timeout)


def mensaje(chat, texto: str, silencioso: bool = False):
    return _json("sendMessage", {
        "chat_id": chat,
        "text": texto[:LIMITE_TEXTO],
        "disable_web_page_preview": True,
        "disable_notification": silencioso,
    })


def enviar(texto: str, silencioso: bool = False) -> None:
    """Alerta al dueño del radar (TELEGRAM_CHAT_ID)."""
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not os.environ.get("TELEGRAM_BOT_TOKEN") or not chat:
        raise TelegramError("faltan TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID")
    mensaje(chat, texto, silencioso)


def _multipart(campos: dict, campo_archivo: str, ruta: Path) -> tuple[bytes, str]:
    limite = uuid.uuid4().hex
    partes = [f'--{limite}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
              for k, v in campos.items()]
    cabecera = (f'--{limite}\r\nContent-Disposition: form-data; name="{campo_archivo}"; '
                f'filename="{ruta.name}"\r\nContent-Type: application/octet-stream\r\n\r\n')
    partes.append(cabecera.encode("utf-8") + ruta.read_bytes() + b"\r\n")
    partes.append(f"--{limite}--\r\n".encode())
    return b"".join(partes), f"multipart/form-data; boundary={limite}"


def documento(chat, ruta: Path, leyenda: str = ""):
    cuerpo, ctype = _multipart({"chat_id": str(chat), "caption": leyenda[:1000]}, "document", ruta)
    return _llamar("sendDocument", cuerpo, ctype, timeout=60)


def foto(chat, ruta: Path, leyenda: str = ""):
    cuerpo, ctype = _multipart({"chat_id": str(chat), "caption": leyenda[:1000]}, "photo", ruta)
    return _llamar("sendPhoto", cuerpo, ctype, timeout=60)


def actualizaciones(offset: int, espera: int = 0) -> list[dict]:
    """Mensajes pendientes desde `offset`. Con `espera` > 0 hace long polling."""
    return _json("getUpdates", {"offset": offset, "timeout": espera, "allowed_updates": ["message"]},
                 timeout=espera + 15)


def validar_respuesta(respuesta: object) -> None:
    """El contrato es el cuerpo: solo {"ok": true} es éxito."""
    if not isinstance(respuesta, dict) or respuesta.get("ok") is not True:
        descripcion = respuesta.get("description") if isinstance(respuesta, dict) else respuesta
        raise TelegramError(f"Telegram rechazó el mensaje: {descripcion!r}")

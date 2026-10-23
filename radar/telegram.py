"""Envío a Telegram (Bot API). Credenciales en TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


class TelegramError(Exception):
    pass


def enviar(texto: str, silencioso: bool = False) -> None:
    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        raise TelegramError("faltan TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID")
    cuerpo = json.dumps({
        "chat_id": chat,
        "text": texto[:4000],
        "disable_web_page_preview": True,
        "disable_notification": silencioso,
    }).encode("utf-8")
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=cuerpo,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310 (URL fija https)
            respuesta = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        # Telegram explica el error en el cuerpo (p. ej. "chat not found"); el token nunca se muestra.
        detalle = e.read().decode("utf-8", errors="replace")[:200]
        raise TelegramError(f"HTTP {e.code}: {detalle}") from e
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise TelegramError(f"sin respuesta válida de Telegram: {type(e).__name__}") from e
    validar_respuesta(respuesta)


def validar_respuesta(respuesta: object) -> None:
    """El contrato es el cuerpo: solo {"ok": true} es éxito."""
    if not isinstance(respuesta, dict) or respuesta.get("ok") is not True:
        descripcion = respuesta.get("description") if isinstance(respuesta, dict) else respuesta
        raise TelegramError(f"Telegram rechazó el mensaje: {descripcion!r}")

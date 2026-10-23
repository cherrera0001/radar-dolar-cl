"""Salud de las fuentes (#4): un aviso al empezar un problema y otro al resolverse, no uno por día.

Dos problemas distintos:
- falla:  la fuente respondió fuera de contrato o no respondió, N corridas seguidas.
- atraso: la fuente responde bien pero el último dato es más viejo que su antigüedad máxima
          (una serie congelada no da error y pasaría inadvertida).
"""

from __future__ import annotations

from datetime import date

from .almacen import antiguedad_max

FALLAS_PARA_AVISAR = 3  # corridas diarias (días hábiles) seguidas


def evaluar(previo: dict, fallidas: set[str], ultimas: dict[str, date], hoy: date) -> tuple[dict, list[str]]:
    """Devuelve el nuevo estado de salud por serie y los avisos a enviar.

    previo:  {serie: {"fallas": int, "aviso_falla": bool, "aviso_atraso": bool}}
    fallidas: series cuya descarga falló en esta corrida
    ultimas:  fecha del último dato guardado por serie
    """
    nuevo: dict[str, dict] = {}
    avisos: list[str] = []
    for serie in sorted(set(previo) | fallidas | set(ultimas)):
        p = previo.get(serie, {})
        fallas = p.get("fallas", 0) + 1 if serie in fallidas else 0
        aviso_falla = p.get("aviso_falla", False)
        if fallas >= FALLAS_PARA_AVISAR and not aviso_falla:
            avisos.append(f"🔴 {serie}: la fuente falla hace {fallas} días hábiles seguidos")
            aviso_falla = True
        elif fallas == 0 and aviso_falla:
            avisos.append(f"🟢 {serie}: la fuente volvió a responder")
            aviso_falla = False

        ultima = ultimas.get(serie)
        atraso = (hoy - ultima).days if ultima else None
        atrasada = atraso is None or atraso > antiguedad_max(serie)
        aviso_atraso = p.get("aviso_atraso", False)
        if atrasada and not aviso_atraso:
            detalle = f"último dato del {ultima} ({atraso} días)" if ultima else "sin datos"
            avisos.append(f"🟠 {serie}: datos atrasados, {detalle}; máximo {antiguedad_max(serie)} días")
            aviso_atraso = True
        elif not atrasada and aviso_atraso:
            avisos.append(f"🟢 {serie}: datos al día otra vez (último {ultima})")
            aviso_atraso = False

        nuevo[serie] = {"fallas": fallas, "aviso_falla": aviso_falla, "aviso_atraso": aviso_atraso}
    return nuevo, avisos

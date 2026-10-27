"""Contratos de los workflows de GitHub Actions. Se leen como texto: el proyecto no depende de PyYAML."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WORKFLOWS = RAIZ / ".github" / "workflows"


def _paso(workflow: str, nombre: str) -> str:
    """Devuelve el bloque YAML del paso cuyo `name:` es `nombre`."""
    texto = (WORKFLOWS / workflow).read_text(encoding="utf-8")
    for bloque in texto.split("\n      - "):
        if bloque.startswith(f"name: {nombre}\n") or bloque.startswith(f"name: {nombre}\r\n"):
            return bloque
    raise AssertionError(f"{workflow}: no existe el paso {nombre!r}")


def test_aviso_de_salud_corre_aunque_falle_la_actualizacion():
    # `radar actualizar` sale con 1 si ninguna fuente responde; el aviso de caída total debe enviarse igual.
    assert "if: always()" in _paso("diario.yml", "Avisos de salud de fuentes")

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


def test_todo_push_de_datos_reintenta_tras_rebase():
    # Dos workflows distintos (bot y diario) escriben a main; sin rebase, el segundo push falla y se pierde el día.
    for workflow in ["bcch.yml", "bot.yml", "diario.yml", "semanal.yml"]:
        pushes = [linea for linea in (WORKFLOWS / workflow).read_text(encoding="utf-8").splitlines()
                  if "git push" in linea]
        assert pushes, f"{workflow}: sin git push"
        for linea in pushes:
            assert "pull --rebase" in linea, f"{workflow}: {linea.strip()}"

"""Contratos de los workflows de GitHub Actions. Se leen como texto: el proyecto no depende de PyYAML."""

import re
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


def test_las_acciones_externas_estan_fijadas_por_sha():
    # Una etiqueta (@v4) puede moverse; un SHA no. Se exige en todos los `uses:` del repo.
    for archivo in sorted(WORKFLOWS.glob("*.yml")):
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            if linea.strip().startswith("- uses:") or linea.strip().startswith("uses:"):
                ref = linea.split("@", 1)[1].split()[0]
                assert re.fullmatch(r"[0-9a-f]{40}", ref), f"{archivo.name}: {linea.strip()}"


def test_el_vigia_tiene_su_paso_de_aviso():
    assert "radar vigia --enviar" in _paso("vigia.yml", "Revisar la corrida diaria")

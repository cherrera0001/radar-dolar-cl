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


def test_la_actualizacion_recibe_las_credenciales_de_bcch():
    for workflow in ["diario.yml", "semanal.yml"]:
        paso = _paso(workflow, "Actualizar series")
        assert "BCCH_USER: ${{ secrets.BCCH_USER }}" in paso, workflow
        assert "BCCH_PASS: ${{ secrets.BCCH_PASS }}" in paso, workflow


def test_todo_workflow_que_escribe_datos_comparte_el_grupo_de_concurrencia():
    # data/envios.json y data/estado.json se escriben sin bloqueo: solo el grupo de Actions los protege.
    for workflow in ["diario.yml", "semanal.yml", "bcch.yml", "vigia.yml"]:
        assert "group: radar-datos" in (WORKFLOWS / workflow).read_text(encoding="utf-8"), workflow


def test_cada_job_avisa_su_caida_con_el_outcome_del_paso_critico():
    # Un job en rojo solo se ve entrando a Actions; el paso avisa al dueño una vez al día.
    casos = {"diario.yml": ("job", "diario"), "bot.yml": ("bot", "bot"),
             "vigia.yml": ("vigía", "vigia"), "semanal.yml": ("resumen", "semanal")}
    for workflow, (nombre, componente) in casos.items():
        paso = _paso(workflow, f"Aviso de caída del {nombre}")
        assert "if: always()" in paso, workflow
        assert f"radar caida --componente {componente}" in paso, workflow
        assert "--estado ${{ steps." in paso, workflow


def test_el_bot_espera_antes_de_reencolar_tras_una_caida():
    # Reencolar de inmediato tras un fallo amplifica el outage en una ráfaga de corridas (2026-10-29).
    paso = _paso("bot.yml", "Encadenar la siguiente corrida")
    assert "steps.escuchar.outcome" in paso
    assert "sleep 240" in paso


def test_los_avisos_de_salud_llevan_la_url_de_la_corrida():
    assert "RADAR_RUN_URL" in _paso("diario.yml", "Avisos de salud de fuentes")

"""Guardas de privacidad (constitución V): ningún perfil personal puede versionarse en data/ o reports/."""

from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
PUBLICADOS = [RAIZ / "data", RAIZ / "reports"]
PALABRAS_PERFIL = ("perfil", "profile", "patrimonio", "colchon", "custodia", "necesidad")


def _archivos():
    for carpeta in PUBLICADOS:
        if carpeta.exists():
            yield from (p for p in carpeta.rglob("*") if p.is_file())


def test_no_hay_archivos_de_perfil_en_datos_ni_reportes():
    sospechosos = [p.relative_to(RAIZ).as_posix() for p in _archivos()
                   if any(palabra in p.name.lower() for palabra in PALABRAS_PERFIL)]
    assert sospechosos == [], f"Archivo de perfil versionado en un directorio público: {sospechosos}"


@pytest.mark.parametrize("texto", ["MANTENER", "VENDER", "COMPRAR", "w*", "saldo"])
def test_reportes_publicos_no_contienen_perfil_del_dueno(texto):
    # Los reportes son públicos: la instrucción personal nunca se guarda en ellos.
    for p in _archivos():
        if p.suffix in {".txt", ".md", ".json"} and "reports" in p.parts:
            contenido = p.read_text(encoding="utf-8", errors="replace")
            assert texto not in contenido, f"{p.name} contiene '{texto}'"

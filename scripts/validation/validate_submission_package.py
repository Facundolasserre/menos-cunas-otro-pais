#!/usr/bin/env python3
"""Validate the copy-ready submission fields and anonymity constraints."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "docs" / "submission-package.md"
SVG = ROOT / "design" / "exports" / "prototype-v0.5.svg"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    require(PACKAGE.exists() and SVG.exists(), "Submission package and v0.5 must exist")
    package = PACKAGE.read_text(encoding="utf-8")
    svg = SVG.read_text(encoding="utf-8")
    normalized_package = " ".join(package.split())

    match = re.search(
        r"<!-- BEGIN FORM DESCRIPTION -->\s*(.*?)\s*<!-- END FORM DESCRIPTION -->",
        package,
        flags=re.DOTALL,
    )
    require(match is not None, "Methodological description markers are missing")
    description = match.group(1)
    word_count = len(description.split())
    require(120 <= word_count <= 200, f"Methodological description has {word_count} words")
    require(f"**Conteo validado:** {word_count} palabras." in package, "Displayed word count is stale")

    required_package_text = [
        "**Categoría:** Historia visual.",
        "**Título:** Menos cunas, otro país.",
        "**Seudónimo:** Umbral Sur.",
        "OpenAI Codex",
        "No se utilizaron generadores de imágenes",
        "https://www.argentina.gob.ar/salud/deis/datos/nacidosvivos",
        "serie_5_nro_68_anuario_vitales_v4_revisada_ok.pdf",
        "natalidad_y_educacion_en_argentina._perspectivas_a_futuro._-_2025.pdf",
    ]
    for text in required_package_text:
        require(text in normalized_package, f"Required submission text is missing: {text}")

    anonymous_material = package + "\n" + svg
    for identifying_text in ("Facundo", "Lasserre"):
        require(
            identifying_text.casefold() not in anonymous_material.casefold(),
            "Personal identity leaked into anonymous material",
        )

    require("UMBRAL SUR" in svg, "Pseudonym is missing from v0.5 artwork")
    require("SEUDÓNIMO PENDIENTE" not in svg, "Pseudonym placeholder remains in v0.5 artwork")

    print(f"OK: submission description contains {word_count}/200 words.")
    print("OK: category, title, pseudonym, open sources and AI disclosure are present.")
    print("OK: no participant name appears in the copy-ready package.")


if __name__ == "__main__":
    main()

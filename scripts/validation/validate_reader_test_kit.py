#!/usr/bin/env python3
"""Validate the printable v0.6 reader-test kit."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "output" / "pdf" / "reader-test-kit-v0.6.pdf"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def embedded_font_status(reader: PdfReader) -> tuple[int, int]:
    seen: set[int] = set()
    total = 0
    embedded = 0
    for page in reader.pages:
        fonts = page.get("/Resources", {}).get("/Font", {})
        for reference in fonts.values():
            identity = reference.idnum if hasattr(reference, "idnum") else id(reference)
            if identity in seen:
                continue
            seen.add(identity)
            font = reference.get_object()
            total += 1
            candidates = [font]
            candidates.extend(item.get_object() for item in font.get("/DescendantFonts", []))
            if any(
                descriptor_ref is not None
                and any(
                    key in descriptor_ref.get_object()
                    for key in ("/FontFile", "/FontFile2", "/FontFile3")
                )
                for candidate in candidates
                if (descriptor_ref := candidate.get("/FontDescriptor")) is not None
            ):
                embedded += 1
    return total, embedded


def main() -> None:
    require(PDF.exists(), "Reader-test kit must be built first")
    reader = PdfReader(PDF)
    require(not reader.is_encrypted, "Reader-test kit must not be encrypted")
    require(len(reader.pages) == 4, "Reader-test kit must contain four pages")

    a4_width_mm = 210
    a4_height_mm = 297
    for page_number, page in enumerate(reader.pages, start=1):
        width_mm = float(page.mediabox.width) * 25.4 / 72
        height_mm = float(page.mediabox.height) * 25.4 / 72
        require(abs(width_mm - a4_width_mm) <= 0.2, f"Page {page_number} width is not A4")
        require(abs(height_mm - a4_height_mm) <= 0.2, f"Page {page_number} height is not A4")
        require(page.cropbox == page.mediabox, f"Page {page_number} CropBox differs from MediaBox")

    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    required = [
        "Prueba física y de comprensión",
        "Pieza v0.6 en color, A3, una cara, escala 100%.",
        "SESIÓN 1 DE 3",
        "SESIÓN 2 DE 3",
        "SESIÓN 3 DE 3",
        "Exposición de 5 segundos",
        "Lectura de 30 segundos",
        "Lectura libre de 2 minutos",
        "No registrar nombre, correo ni datos de contacto.",
    ]
    for label in required:
        require(label in text, f"Required extractable text missing: {label}")
    for identifying_text in ("Facundo", "Lasserre"):
        require(identifying_text.casefold() not in text.casefold(), "Personal identity leaked into kit")

    fonts, embedded = embedded_font_status(reader)
    require(fonts > 0 and embedded == fonts, f"Only {embedded} of {fonts} fonts are embedded")
    metadata = reader.metadata or {}
    require(metadata.get("/Author") == "UMBRAL SUR", "Pseudonym missing from PDF metadata")

    print("OK: four-page A4 reader-test kit is complete and anonymous.")
    print(f"OK: {fonts}/{fonts} fonts embedded; all required text is extractable.")


if __name__ == "__main__":
    main()

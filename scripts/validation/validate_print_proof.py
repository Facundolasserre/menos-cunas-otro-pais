#!/usr/bin/env python3
"""Validate physical dimensions, content and vector integrity of the A3 PDF."""

from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
VERSION = "v0.5"
PDF = ROOT / "output" / "pdf" / f"prototype-{VERSION}-print-proof.pdf"
MANIFEST = ROOT / "design" / "exports" / f"prototype-{VERSION}-manifest.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def count_raster_images(page: object) -> int:
    resources = page.get("/Resources", {})
    xobjects = resources.get("/XObject", {})
    count = 0
    for reference in xobjects.values():
        item = reference.get_object()
        if item.get("/Subtype") == "/Image":
            count += 1
    return count


def embedded_font_status(page: object) -> tuple[int, int]:
    resources = page.get("/Resources", {})
    fonts = resources.get("/Font", {})
    total = 0
    embedded = 0
    for reference in fonts.values():
        font = reference.get_object()
        total += 1
        candidates = [font]
        descendants = font.get("/DescendantFonts", [])
        candidates.extend(item.get_object() for item in descendants)
        for candidate in candidates:
            descriptor_ref = candidate.get("/FontDescriptor")
            if descriptor_ref is None:
                continue
            descriptor = descriptor_ref.get_object()
            if any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3")):
                embedded += 1
                break
    return total, embedded


def main() -> None:
    require(PDF.exists() and MANIFEST.exists(), f"The {VERSION} print proof must be built first")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest["prototype"] == VERSION, "Unexpected print-proof manifest version")

    reader = PdfReader(PDF)
    require(not reader.is_encrypted, "Print proof must not be encrypted")
    require(len(reader.pages) == 1, "Print proof must contain exactly one page")
    page = reader.pages[0]

    width_mm = float(page.mediabox.width) * 25.4 / 72
    height_mm = float(page.mediabox.height) * 25.4 / 72
    require(abs(width_mm - 297) <= 0.2, f"Unexpected PDF width: {width_mm:.2f} mm")
    require(abs(height_mm - 420) <= 0.2, f"Unexpected PDF height: {height_mm:.2f} mm")
    require(page.cropbox == page.mediabox, "CropBox must match MediaBox")

    text = page.extract_text() or ""
    required_text = [
        "PROTOTIPO 0.5",
        "PRUEBA DE IMPRESIÓN",
        "NO PRESENTAR",
        "Menos cunas, otro país",
        "777.012",
        "413.135",
        "Formosa",
        "Ciudad Aut. de Buenos Aires",
        "Proyección externa DNP/RENAPER",
        "UMBRAL SUR",
    ]
    for label in required_text:
        require(label in text, f"Text is not extractable from PDF: {label}")

    raster_images = count_raster_images(page)
    require(raster_images == 0, f"PDF contains {raster_images} raster image(s)")
    fonts, embedded_fonts = embedded_font_status(page)
    require(fonts > 0, "PDF does not declare fonts")
    require(embedded_fonts == fonts, f"Only {embedded_fonts} of {fonts} PDF fonts are embedded")

    metadata = reader.metadata or {}
    require(VERSION in str(metadata.get("/Title", "")), "PDF title metadata is incomplete")

    print(f"OK: one-page A3 PDF measures {width_mm:.2f} × {height_mm:.2f} mm.")
    print(f"OK: {fonts}/{fonts} fonts embedded; text extractable; no raster images.")


if __name__ == "__main__":
    main()

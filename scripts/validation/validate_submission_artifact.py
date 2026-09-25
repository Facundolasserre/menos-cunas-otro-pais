#!/usr/bin/env python3
"""Validate the exact visual artifact prepared for contest submission."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageChops
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
STEM = "menos-cunas-otro-pais-umbral-sur"
SVG = ROOT / "design" / "exports" / f"{STEM}.svg"
PNG = ROOT / "output" / "png" / f"{STEM}.png"
PDF = ROOT / "output" / "pdf" / f"{STEM}.pdf"
MANIFEST = ROOT / "design" / "exports" / f"{STEM}-manifest.json"
PROTOTYPE_PNG = ROOT / "design" / "exports" / "prototype-v0.6.png"
FORBIDDEN = [
    "PROTOTIPO",
    "PRUEBA DE IMPRESIÓN",
    "NO PRESENTAR",
    "Facundo",
    "Lasserre",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_raster_images(page: object) -> int:
    resources = page.get("/Resources", {})
    count = 0
    for reference in resources.get("/XObject", {}).values():
        if reference.get_object().get("/Subtype") == "/Image":
            count += 1
    return count


def embedded_font_status(page: object) -> tuple[int, int]:
    fonts = page.get("/Resources", {}).get("/Font", {})
    total = 0
    embedded = 0
    for reference in fonts.values():
        font = reference.get_object()
        total += 1
        candidates = [font]
        candidates.extend(item.get_object() for item in font.get("/DescendantFonts", []))
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
    require(all(path.exists() for path in (SVG, PNG, PDF, MANIFEST)), "Submission outputs are incomplete")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest["artifact"] == "submission-v1", "Unexpected artifact identifier")
    require(manifest["status"] == "ready_for_submission", "Artifact is not marked ready")
    require(manifest["source_prototype"] == "v0.6", "Unexpected source prototype")
    require(manifest["category"] == "Historia visual", "Unexpected contest category")
    require(manifest["pseudonym"] == "UMBRAL SUR", "Unexpected pseudonym")

    for item in manifest["files"].values():
        path = ROOT / item["path"]
        require(path.exists(), f"Manifest output missing: {path}")
        require(path.stat().st_size == item["bytes"], f"Size mismatch: {path.name}")
        require(sha256(path) == item["sha256"], f"Checksum mismatch: {path.name}")

    with Image.open(PNG) as image:
        expected_size = (
            manifest["canvas"]["png_width_px"],
            manifest["canvas"]["png_height_px"],
        )
        require(image.size == expected_size, f"Unexpected PNG dimensions: {image.size}")
        require(image.size == (2806, 3968), "PNG does not match A3 at 240 dpi")
        require(image.mode in {"RGB", "RGBA"}, f"Unexpected PNG mode: {image.mode}")
        dpi = image.info.get("dpi", (0, 0))
        require(all(abs(value - 240) <= 0.5 for value in dpi), f"Unexpected PNG resolution: {dpi}")
        png_metadata = "\n".join(str(value) for value in image.info.values())
        for forbidden in FORBIDDEN:
            require(forbidden.casefold() not in png_metadata.casefold(), f"Forbidden PNG metadata: {forbidden}")

    require(PROTOTYPE_PNG.exists(), "Source prototype PNG is missing")
    with Image.open(PROTOTYPE_PNG) as prototype_image, Image.open(PNG) as final_image:
        prototype_rgb = prototype_image.convert("RGB")
        final_rgb = final_image.convert("RGB")
        require(prototype_rgb.size == final_rgb.size, "Final and prototype dimensions differ")
        difference_box = ImageChops.difference(prototype_rgb, final_rgb).getbbox()
        require(difference_box is not None, "Final image still matches the marked prototype")
        require(
            difference_box[3] <= final_rgb.height * 0.03,
            f"Final composition changed outside the prototype-warning area: {difference_box}",
        )

    svg = SVG.read_text(encoding="utf-8")
    require("<image" not in svg.lower(), "SVG embeds a raster image")
    sizes = [float(value) for value in re.findall(r"font-size:\s*([0-9.]+)px", svg)]
    require(sizes and min(sizes) >= 8, "SVG typography falls below 8 pt")
    require("UMBRAL SUR" in svg, "Pseudonym is missing from SVG")
    for forbidden in FORBIDDEN:
        require(forbidden.casefold() not in svg.casefold(), f"Forbidden SVG content: {forbidden}")

    require(PDF.stat().st_size < 10 * 1024 * 1024, "Submission PDF exceeds 10 MB")
    reader = PdfReader(PDF)
    require(not reader.is_encrypted, "Submission PDF must not be encrypted")
    require(len(reader.pages) == 1, "Submission PDF must contain exactly one page")
    root = reader.trailer["/Root"]
    require("/AcroForm" not in root and not reader.get_fields(), "Submission PDF contains a form")
    names = root.get("/Names", {})
    require("/JavaScript" not in names, "Submission PDF contains JavaScript")
    page = reader.pages[0]
    annotations = page.get("/Annots", [])
    if hasattr(annotations, "get_object"):
        annotations = annotations.get_object()
    require(not annotations, "Submission PDF contains annotations")
    width_mm = float(page.mediabox.width) * 25.4 / 72
    height_mm = float(page.mediabox.height) * 25.4 / 72
    require(abs(width_mm - 297) <= 0.2, f"Unexpected PDF width: {width_mm:.2f} mm")
    require(abs(height_mm - 420) <= 0.2, f"Unexpected PDF height: {height_mm:.2f} mm")
    require(page.cropbox == page.mediabox, "CropBox must match MediaBox")
    require(count_raster_images(page) == 0, "Submission PDF contains raster images")
    fonts, embedded_fonts = embedded_font_status(page)
    require(fonts > 0 and fonts == embedded_fonts, f"Only {embedded_fonts} of {fonts} fonts are embedded")

    text = page.extract_text() or ""
    required_text = [
        "Menos cunas, otro país",
        "777.012",
        "413.135",
        "20–24  →  25–29",
        "Formosa",
        "Ciudad Aut. de Buenos Aires",
        "Proyección externa DNP/RENAPER",
        "UMBRAL SUR",
    ]
    for label in required_text:
        require(label in text, f"Required extractable text missing: {label}")
    metadata = reader.metadata or {}
    anonymous_content = text + "\n" + "\n".join(str(value) for value in metadata.values())
    for forbidden in FORBIDDEN:
        require(forbidden.casefold() not in anonymous_content.casefold(), f"Forbidden PDF content: {forbidden}")
    require(metadata.get("/Title") == "Menos cunas, otro país", "Unexpected PDF title metadata")
    require(metadata.get("/Author") == "UMBRAL SUR", "Unexpected PDF author metadata")

    print(f"OK: final A3 PDF measures {width_mm:.2f} × {height_mm:.2f} mm and is under 10 MB.")
    print(f"OK: {fonts}/{fonts} fonts embedded; text extractable; no raster images.")
    print("OK: final PDF, PNG and SVG are anonymous and contain no prototype markers.")


if __name__ == "__main__":
    main()

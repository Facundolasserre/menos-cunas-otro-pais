#!/usr/bin/env python3
"""Validate every versioned visual-story prototype and its manifest."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
EXPORTS = ROOT / "design" / "exports"
VERSIONS = {"v0.1": None, "v0.2": 7.5, "v0.3": 8.0}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def channel(value: int) -> float:
    normalized = value / 255
    return normalized / 12.92 if normalized <= 0.04045 else ((normalized + 0.055) / 1.055) ** 2.4


def luminance(color: str) -> float:
    clean = color.removeprefix("#")
    red, green, blue = (int(clean[index : index + 2], 16) for index in (0, 2, 4))
    return 0.2126 * channel(red) + 0.7152 * channel(green) + 0.0722 * channel(blue)


def contrast(first: str, second: str) -> float:
    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def validate_version(version: str, minimum_font_size: float | None) -> None:
    svg_path = EXPORTS / f"prototype-{version}.svg"
    png_path = EXPORTS / f"prototype-{version}.png"
    manifest_path = EXPORTS / f"prototype-{version}-manifest.json"
    require(
        svg_path.exists() and png_path.exists() and manifest_path.exists(),
        f"Prototype outputs are incomplete: {version}",
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest["prototype"] == version, f"Manifest version mismatch: {version}")
    require(manifest["status"] == "not_for_submission", "Prototype status must remain explicit")

    for filename, expected in manifest["files"].items():
        path = ROOT / expected["path"] if "path" in expected else EXPORTS / filename
        require(path.exists(), f"Manifest output is missing: {path.relative_to(ROOT)}")
        require(path.stat().st_size == expected["bytes"], f"Size mismatch: {path.name}")
        require(sha256(path) == expected["sha256"], f"Checksum mismatch: {path.name}")

    with Image.open(png_path) as image:
        expected_size = (
            manifest["canvas"]["png_width_px"],
            manifest["canvas"]["png_height_px"],
        )
        require(image.size == expected_size, f"Unexpected PNG dimensions: {image.size}")
        require(image.mode in {"RGB", "RGBA"}, f"Unexpected PNG mode: {image.mode}")
        background = tuple(int(manifest["palette"]["background"][index : index + 2], 16) for index in (1, 3, 5))
        require(image.convert("RGB").getpixel((0, 0)) == background, "PNG background mismatch")

    expected_ratio = 297 / 420
    actual_ratio = manifest["canvas"]["png_width_px"] / manifest["canvas"]["png_height_px"]
    require(abs(actual_ratio - expected_ratio) < 0.001, "Canvas does not preserve A-series ratio")

    palette = manifest["palette"]
    require(contrast(palette["ink"], palette["background"]) >= 7, "Ink contrast below AAA")
    require(contrast(palette["accent_2024"], palette["background"]) >= 4.5, "Accent contrast below AA")
    require(contrast(palette["neutral_2014"], palette["background"]) >= 4.5, "Neutral contrast below AA")

    svg = svg_path.read_text(encoding="utf-8")
    lower_svg = svg.lower()
    require("<image" not in lower_svg and "data:image" not in lower_svg, "SVG embeds a raster image")
    display_version = version.removeprefix("v")
    require(f"prototipo {display_version}" in lower_svg, f"Prototype version warning is missing: {version}")
    require("no presentar" in lower_svg, f"Prototype status warning is missing: {version}")
    require("seudónimo pendiente" in lower_svg, "Pseudonym placeholder is missing")
    for color in palette.values():
        require(color.lower() in lower_svg, f"Palette color missing from SVG: {color}")

    required_labels = [
        "Menos cunas, otro país",
        "777.012",
        "413.135",
        "20–24  →  25–29",
        "Formosa",
        "Tierra del Fuego",
        "Ciudad Aut. de Buenos Aires",
        "Proyección externa DNP/RENAPER",
    ]
    for label in required_labels:
        require(label in svg, f"Required visible label missing: {label}")

    if minimum_font_size is not None:
        sizes = [float(value) for value in re.findall(r"font-size:\s*([0-9.]+)px", svg)]
        require(sizes, f"No SVG font sizes found: {version}")
        require(
            min(sizes) >= minimum_font_size,
            f"Minimum font size is {min(sizes):.1f}px, expected {minimum_font_size:.1f}px: {version}",
        )

    print(f"OK: {version} matches its manifest and preserves vector text.")


def main() -> None:
    for version, minimum_font_size in VERSIONS.items():
        validate_version(version, minimum_font_size)

    print("OK: A3 ratio, palette semantics, typography and contrast thresholds verified.")


if __name__ == "__main__":
    main()

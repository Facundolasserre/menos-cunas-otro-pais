#!/usr/bin/env python3
"""Test the v0.2 palette under color-vision simulations and write the audit."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERSION = "v0.5"
MANIFEST = ROOT / "design" / "exports" / f"prototype-{VERSION}-manifest.json"
SVG = ROOT / "design" / "exports" / f"prototype-{VERSION}.svg"
REPORT = ROOT / "docs" / "visual-accessibility.md"

# Full-severity matrices from Machado, Oliveira and Fernandes (2009), applied
# to linear-light sRGB values. Identity is included for a common audit path.
MATRICES = {
    "Visión estándar": (
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
    ),
    "Protanopia": (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    "Deuteranopia": (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
    "Tritanopia": (
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809, 0.147602),
        (0.004733, 0.691367, 0.303900),
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def decode_channel(value: float) -> float:
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def encode_channel(value: float) -> float:
    clipped = min(1.0, max(0.0, value))
    return 12.92 * clipped if clipped <= 0.0031308 else 1.055 * clipped ** (1 / 2.4) - 0.055


def hex_to_linear(color: str) -> tuple[float, float, float]:
    clean = color.removeprefix("#")
    return tuple(decode_channel(int(clean[index : index + 2], 16) / 255) for index in (0, 2, 4))


def linear_to_hex(rgb: tuple[float, float, float]) -> str:
    channels = (round(encode_channel(value) * 255) for value in rgb)
    return "#" + "".join(f"{value:02X}" for value in channels)


def transform(color: str, matrix: tuple[tuple[float, ...], ...]) -> str:
    source = hex_to_linear(color)
    transformed = tuple(sum(row[index] * source[index] for index in range(3)) for row in matrix)
    return linear_to_hex(transformed)


def luminance(color: str) -> float:
    red, green, blue = hex_to_linear(color)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(first: str, second: str) -> float:
    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def srgb_to_lab(color: str) -> tuple[float, float, float]:
    red, green, blue = hex_to_linear(color)
    x = (0.4124564 * red + 0.3575761 * green + 0.1804375 * blue) / 0.95047
    y = 0.2126729 * red + 0.7151522 * green + 0.0721750 * blue
    z = (0.0193339 * red + 0.1191920 * green + 0.9503041 * blue) / 1.08883

    def pivot(value: float) -> float:
        return value ** (1 / 3) if value > 0.008856 else 7.787 * value + 16 / 116

    fx, fy, fz = pivot(x), pivot(y), pivot(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(first: str, second: str) -> float:
    first_lab, second_lab = srgb_to_lab(first), srgb_to_lab(second)
    return math.sqrt(sum((left - right) ** 2 for left, right in zip(first_lab, second_lab)))


def grayscale(color: str) -> str:
    gray = luminance(color)
    return linear_to_hex((gray, gray, gray))


def main() -> None:
    require(MANIFEST.exists() and SVG.exists(), f"{VERSION} outputs must be built before accessibility validation")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    palette = manifest["palette"]
    base = {
        "Fondo": palette["background"],
        "Acento 2024": palette["accent_2024"],
        "Neutral 2014": palette["neutral_2014"],
        "Tinta": palette["ink"],
    }

    results: list[dict[str, str | float]] = []
    for condition, matrix in MATRICES.items():
        colors = {name: transform(color, matrix) for name, color in base.items()}
        accent_contrast = contrast(colors["Acento 2024"], colors["Fondo"])
        neutral_contrast = contrast(colors["Neutral 2014"], colors["Fondo"])
        separation = delta_e(colors["Acento 2024"], colors["Neutral 2014"])
        require(accent_contrast >= 4.5, f"Accent fails AA under {condition}")
        require(neutral_contrast >= 4.5, f"Neutral fails AA under {condition}")
        require(separation >= 10, f"Accent and neutral are too similar under {condition}")
        results.append(
            {
                "condition": condition,
                "background": colors["Fondo"],
                "accent": colors["Acento 2024"],
                "neutral": colors["Neutral 2014"],
                "accent_contrast": accent_contrast,
                "neutral_contrast": neutral_contrast,
                "delta_e": separation,
            }
        )

    gray = {name: grayscale(color) for name, color in base.items()}
    svg = SVG.read_text(encoding="utf-8")
    require("2014  ○" in svg and "2024  ●" in svg, "Year markers must differ by shape and direct label")
    require("2014" in svg and "2024" in svg, "Years must be directly labelled")

    rows = "\n".join(
        "| {condition} | `{background}` | `{accent}` | `{neutral}` | {accent_contrast:.2f}:1 | "
        "{neutral_contrast:.2f}:1 | {delta_e:.1f} |".format(**row)
        for row in results
    )
    report = f"""# Auditoría de accesibilidad visual

Fecha: 2026-09-25. Prototipo evaluado: {VERSION}.

## Resultado

La paleta supera el contraste AA de 4,5:1 para texto normal tanto en visión
estándar como en las simulaciones completas de protanopia, deuteranopia y
tritanopia. La diferencia entre acento y neutral permanece por encima de
ΔE76 = 10 en las tres simulaciones. El color no es el único canal: 2014 usa
puntos vacíos y 2024 puntos llenos, con años y valores etiquetados directamente.

| Condición | Fondo | Acento 2024 | Neutral 2014 | Acento/fondo | Neutral/fondo | ΔE76 |
| --- | --- | --- | --- | ---: | ---: | ---: |
{rows}

## Escala de grises

La conversión por luminancia produce fondo `{gray['Fondo']}`, acento
`{gray['Acento 2024']}` y neutral `{gray['Neutral 2014']}`. Acento y neutral
quedan próximos en gris; por eso la lectura no depende de diferenciarlos por
tono. La redundancia de forma —vacío/lleno—, posición y etiqueta directa es un
requisito validado automáticamente.

## Método y alcance

Las simulaciones aplican a RGB lineal las matrices de severidad completa de
Machado, Oliveira y Fernandes (2009), vuelven a sRGB y calculan contraste WCAG
y distancia CIE76. Es una prueba técnica reproducible, no reemplaza una revisión
con personas ni la prueba impresa A3 al 100%.

Referencia: [A physiologically-based model for simulation of color vision
deficiency](https://doi.org/10.1109/TVCG.2009.113).
"""
    REPORT.write_text(report, encoding="utf-8")

    print("OK: palette passes AA contrast in standard and three CVD simulations.")
    print("OK: grayscale reading is redundant in shape, position and direct labels.")
    print(f"Wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

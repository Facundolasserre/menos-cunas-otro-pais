#!/usr/bin/env python3
"""Build the exact PDF and PNG files prepared for contest submission."""

from __future__ import annotations

from datetime import UTC, datetime
import json
import build_storyboard_prototype as storyboard
import matplotlib.pyplot as plt
import pandas as pd


ROOT = storyboard.ROOT
PROCESSED = storyboard.PROCESSED
EXPORTS = storyboard.EXPORTS
OUTPUT = ROOT / "output"
PDF_OUTPUT = OUTPUT / "pdf" / "menos-cunas-otro-pais-umbral-sur.pdf"
PNG_OUTPUT = OUTPUT / "png" / "menos-cunas-otro-pais-umbral-sur.png"
SVG_OUTPUT = EXPORTS / "menos-cunas-otro-pais-umbral-sur.svg"
MANIFEST_OUTPUT = EXPORTS / "menos-cunas-otro-pais-umbral-sur-manifest.json"
ARTIFACT_ID = "submission-v1"
ARTIFACT_TIMESTAMP = datetime(2026, 9, 25, 15, tzinfo=UTC)


def write_manifest() -> None:
    from PIL import Image

    with Image.open(PNG_OUTPUT) as image:
        width, height = image.size
    files = {}
    for path in (SVG_OUTPUT, PNG_OUTPUT, PDF_OUTPUT):
        files[path.name] = {
            "path": str(path.relative_to(ROOT)),
            "bytes": path.stat().st_size,
            "sha256": storyboard.sha256(path),
        }
    payload = {
        "artifact": ARTIFACT_ID,
        "status": "ready_for_submission",
        "source_prototype": storyboard.VERSION,
        "category": "Historia visual",
        "title": "Menos cunas, otro país",
        "pseudonym": storyboard.PSEUDONYM,
        "canvas": {
            "format": "A3 portrait",
            "width_mm": storyboard.A3_WIDTH_MM,
            "height_mm": storyboard.A3_HEIGHT_MM,
            "png_width_px": width,
            "png_height_px": height,
        },
        "files": files,
        "palette": {
            "background": storyboard.BG,
            "ink": storyboard.INK,
            "accent_2024": storyboard.ACCENT,
            "neutral_2014": storyboard.NEUTRAL,
            "grid": storyboard.GRID,
        },
    }
    MANIFEST_OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    national = pd.read_csv(PROCESSED / "national_trend.csv").set_index("year")
    age = pd.read_csv(PROCESSED / "age_change_2014_2024.csv")
    province = pd.read_csv(PROCESSED / "province_age_shift_2014_2024.csv")

    EXPORTS.mkdir(parents=True, exist_ok=True)
    PDF_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    PNG_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "tmp" / "matplotlib").mkdir(parents=True, exist_ok=True)

    plt.rcParams.update(
        {
            "font.family": storyboard.FONT,
            "text.color": storyboard.INK,
            "axes.labelcolor": storyboard.INK,
            "axes.edgecolor": storyboard.GRID,
            "xtick.color": storyboard.NEUTRAL,
            "ytick.color": storyboard.NEUTRAL,
            "svg.fonttype": "none",
            "svg.hashsalt": "menos-cunas-otro-pais-umbral-sur",
            "pdf.fonttype": 42,
        }
    )
    figure = plt.figure(
        figsize=(storyboard.A3_WIDTH_MM / 25.4, storyboard.A3_HEIGHT_MM / 25.4),
        facecolor=storyboard.BG,
    )
    hero_arrow, hero_numbers = storyboard.draw_header(
        figure,
        national,
        show_prototype_warning=False,
    )
    storyboard.figure_rule(figure, 0.795)
    timeline_line, timeline_annotations = storyboard.draw_timeline(figure, national)
    storyboard.figure_rule(figure, 0.628)
    storyboard.draw_age_shift(figure, age)
    storyboard.figure_rule(figure, 0.464)
    storyboard.draw_province_shift(figure, province)
    storyboard.figure_rule(figure, 0.124)
    storyboard.draw_context_and_footer(figure)
    figure.canvas.draw()
    storyboard.validate_header_clearance(figure, hero_arrow, hero_numbers)
    storyboard.validate_timeline_clearance(
        figure,
        timeline_line,
        timeline_annotations,
    )

    description = (
        "Historia visual sobre la caída de nacimientos registrados y el "
        "desplazamiento de la composición por edad materna en Argentina."
    )
    svg_metadata = {
        "Title": "Menos cunas, otro país",
        "Description": description,
        "Creator": "UMBRAL SUR",
        "Date": "2026-09-25",
    }
    figure.savefig(SVG_OUTPUT, format="svg", facecolor=storyboard.BG, metadata=svg_metadata)
    storyboard.normalize_svg(SVG_OUTPUT)
    figure.savefig(
        PNG_OUTPUT,
        format="png",
        dpi=240,
        facecolor=storyboard.BG,
        metadata={
            "Title": svg_metadata["Title"],
            "Description": description,
            "Author": storyboard.PSEUDONYM,
            "Software": "Matplotlib 3.11.2",
        },
    )
    figure.savefig(
        PDF_OUTPUT,
        format="pdf",
        facecolor=storyboard.BG,
        metadata={
            "Title": svg_metadata["Title"],
            "Author": storyboard.PSEUDONYM,
            "Subject": description,
            "Creator": "Matplotlib 3.11.2",
            "Producer": "UMBRAL SUR",
            "CreationDate": ARTIFACT_TIMESTAMP,
            "ModDate": ARTIFACT_TIMESTAMP,
        },
    )
    plt.close(figure)
    write_manifest()
    print(SVG_OUTPUT.relative_to(ROOT))
    print(PNG_OUTPUT.relative_to(ROOT))
    print(PDF_OUTPUT.relative_to(ROOT))
    print(MANIFEST_OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()

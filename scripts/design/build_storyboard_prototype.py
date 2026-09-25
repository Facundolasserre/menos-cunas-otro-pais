#!/usr/bin/env python3
"""Build the current data-bound visual-story prototype as SVG, PNG and PDF."""

from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "tmp" / "matplotlib"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402
from matplotlib.text import Text  # noqa: E402


PROCESSED = ROOT / "data" / "processed"
EXPORTS = ROOT / "design" / "exports"
PDF_EXPORTS = ROOT / "output" / "pdf"
VERSION = "v0.6"
PSEUDONYM = "UMBRAL SUR"
SVG_OUTPUT = EXPORTS / f"prototype-{VERSION}.svg"
PNG_OUTPUT = EXPORTS / f"prototype-{VERSION}.png"
PDF_OUTPUT = PDF_EXPORTS / f"prototype-{VERSION}-print-proof.pdf"
MANIFEST_OUTPUT = EXPORTS / f"prototype-{VERSION}-manifest.json"

BG = "#F7F4EC"
INK = "#1C252B"
ACCENT = "#0F6370"
NEUTRAL = "#6B665E"
GRID = "#D8D2C7"
A3_WIDTH_MM = 297
A3_HEIGHT_MM = 420

LEFT = 0.075
RIGHT = 0.935
FONT = "DejaVu Sans"
FONT_BOLD = "DejaVu Sans"


def format_int_es(value: float | int) -> str:
    return f"{int(round(value)):,}".replace(",", ".")


def format_pct_es(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}".replace(".", ",") + "%"


def figure_rule(fig: plt.Figure, y: float) -> None:
    fig.add_artist(
        Line2D(
            [LEFT, RIGHT],
            [y, y],
            transform=fig.transFigure,
            color=GRID,
            linewidth=0.8,
        )
    )


def style_axis(axis: plt.Axes) -> None:
    axis.set_facecolor(BG)
    for spine in axis.spines.values():
        spine.set_visible(False)
    axis.tick_params(length=0, colors=NEUTRAL, labelsize=8)


def draw_year_key(fig: plt.Figure, y: float) -> None:
    fig.text(
        0.865,
        y,
        "2014  ○",
        color=NEUTRAL,
        fontsize=8.5,
        family=FONT,
        ha="right",
    )
    fig.text(
        RIGHT,
        y,
        "2024  ●",
        color=ACCENT,
        fontsize=8.5,
        family=FONT,
        ha="right",
    )


def draw_header(
    fig: plt.Figure,
    national: pd.DataFrame,
    *,
    show_prototype_warning: bool = True,
) -> tuple[FancyArrowPatch, tuple[Text, Text]]:
    first = int(national.loc[2014, "registered_births"])
    last = int(national.loc[2024, "registered_births"])
    change = last - first
    change_pct = change / first * 100

    if show_prototype_warning:
        fig.text(
            LEFT,
            0.976,
            "PROTOTIPO 0.6 · PRUEBA DE IMPRESIÓN · NO PRESENTAR",
            color=NEUTRAL,
            fontsize=8,
            fontweight="bold",
            family=FONT,
        )
    fig.text(
        LEFT,
        0.942,
        "Menos cunas, otro país",
        color=INK,
        fontsize=31,
        fontweight="bold",
        family=FONT_BOLD,
        va="top",
    )
    fig.text(
        LEFT,
        0.903,
        "En diez años, Argentina registró 46,8% menos nacimientos. A la vez, la composición\n"
        "se desplazó hacia edades maternas mayores en las 24 jurisdicciones.",
        color=INK,
        fontsize=12.5,
        family=FONT,
        linespacing=1.35,
        va="top",
    )

    y_number = 0.837
    left_number = fig.text(
        LEFT,
        y_number,
        format_int_es(first),
        color=INK,
        fontsize=37,
        fontweight="bold",
        family=FONT_BOLD,
        va="center",
    )
    fig.text(
        LEFT,
        y_number - 0.031,
        "2014",
        color=NEUTRAL,
        fontsize=9,
        family=FONT,
    )
    right_number = fig.text(
        RIGHT,
        y_number,
        format_int_es(last),
        color=ACCENT,
        fontsize=37,
        fontweight="bold",
        family=FONT_BOLD,
        ha="right",
        va="center",
    )
    fig.text(
        RIGHT,
        y_number - 0.031,
        "2024",
        color=NEUTRAL,
        fontsize=9,
        family=FONT,
        ha="right",
    )

    # Let the rendered numerals—not hard-coded guesses—set the arrow span. The
    # 12 pt optical gap keeps both the shaft and arrowhead clear of the figures.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    figure_coordinates = fig.transFigure.inverted()
    left_box = left_number.get_window_extent(renderer=renderer).transformed(
        figure_coordinates
    )
    right_box = right_number.get_window_extent(renderer=renderer).transformed(
        figure_coordinates
    )
    optical_gap = (12 / 72) / fig.get_figwidth()
    arrow_start = left_box.x1 + optical_gap
    arrow_end = right_box.x0 - optical_gap
    if arrow_start >= arrow_end:
        raise RuntimeError("Hero numbers leave no safe horizontal span for the arrow")

    arrow = FancyArrowPatch(
        (arrow_start, y_number),
        (arrow_end, y_number),
        transform=fig.transFigure,
        arrowstyle="-|>",
        mutation_scale=13,
        linewidth=1.8,
        color=GRID,
        shrinkA=0,
        shrinkB=0,
    )
    fig.add_artist(arrow)
    fig.text(
        0.50,
        y_number + 0.019,
        format_pct_es(change_pct),
        color=ACCENT,
        fontsize=15,
        fontweight="bold",
        family=FONT_BOLD,
        ha="center",
    )
    fig.text(
        0.50,
        y_number - 0.027,
        f"{format_int_es(abs(change))} nacimientos registrados menos",
        color=NEUTRAL,
        fontsize=8.5,
        family=FONT,
        ha="center",
    )

    return arrow, (left_number, right_number)


def validate_header_clearance(
    fig: plt.Figure,
    arrow: FancyArrowPatch,
    number_texts: tuple[Text, Text],
    minimum_gap_points: float = 8,
) -> None:
    """Fail when the hero arrow crowds either headline number."""
    renderer = fig.canvas.get_renderer()
    arrow_box = arrow.get_window_extent(renderer=renderer)
    left_box, right_box = (
        text.get_window_extent(renderer=renderer) for text in number_texts
    )
    minimum_gap_pixels = minimum_gap_points * fig.dpi / 72
    left_gap = arrow_box.x0 - left_box.x1
    right_gap = right_box.x0 - arrow_box.x1
    if left_gap < minimum_gap_pixels or right_gap < minimum_gap_pixels:
        raise RuntimeError(
            "Hero arrow clearance below "
            f"{minimum_gap_points:g} pt: left={left_gap * 72 / fig.dpi:.1f} pt, "
            f"right={right_gap * 72 / fig.dpi:.1f} pt"
        )


def draw_timeline(fig: plt.Figure, national: pd.DataFrame) -> tuple[Line2D, list[object]]:
    fig.text(
        LEFT,
        0.772,
        "La caída ya estaba en marcha antes de 2020",
        color=INK,
        fontsize=16.5,
        fontweight="bold",
        family=FONT_BOLD,
    )
    fig.text(
        RIGHT,
        0.772,
        "Nacimientos registrados por año",
        color=NEUTRAL,
        fontsize=8,
        family=FONT,
        ha="right",
    )

    axis = fig.add_axes([LEFT, 0.653, RIGHT - LEFT, 0.098])
    style_axis(axis)
    years = national.index.to_numpy()
    births = national["registered_births"].to_numpy() / 1_000
    axis.set_xlim(2013.75, 2024.25)
    axis.set_ylim(375, 825)
    for value in (400, 600, 800):
        axis.axhline(value, color=GRID, linewidth=0.65, zorder=0)
    (timeline_line,) = axis.plot(years, births, color=ACCENT, linewidth=2.4, zorder=2)
    axis.scatter(years, births, s=18, color=ACCENT, zorder=3)
    axis.set_xticks([2014, 2016, 2018, 2020, 2022, 2024])
    axis.set_xticklabels(["2014", "2016", "2018", "2020", "2022", "2024"])
    axis.set_yticks([400, 600, 800])
    axis.set_yticklabels(["400 mil", "600 mil", "800 mil"])

    annotation_specs = {
        2014: ("777.012", (4, 12), "left", False),
        2019: ("625.441\n−19,5% desde 2014", (-8, 24), "right", True),
        2020: ("533.299\n−14,7% en un año", (8, -20), "left", True),
        2024: ("413.135\n−46,8% desde 2014", (-8, 24), "right", True),
    }
    annotations = []
    for year, (label, offset, alignment, add_leader) in annotation_specs.items():
        annotation = axis.annotate(
            label,
            xy=(year, float(national.loc[year, "registered_births"]) / 1_000),
            xytext=offset,
            textcoords="offset points",
            ha=alignment,
            va="bottom" if offset[1] >= 0 else "top",
            color=INK if year != 2024 else ACCENT,
            fontsize=8.5,
            fontweight="bold" if year in {2014, 2024} else "normal",
            family=FONT,
            linespacing=1.25,
            arrowprops=(
                {
                    "arrowstyle": "-",
                    "color": NEUTRAL,
                    "linewidth": 0.7,
                    "shrinkA": 3,
                    "shrinkB": 4,
                }
                if add_leader
                else None
            ),
        )
        annotations.append(annotation)

    return timeline_line, annotations


def validate_timeline_clearance(
    fig: plt.Figure,
    timeline_line: Line2D,
    annotations: list[object],
) -> None:
    """Fail when the data line enters any annotation's padded text box."""
    renderer = fig.canvas.get_renderer()
    coordinates = np.column_stack((timeline_line.get_xdata(), timeline_line.get_ydata()))
    display_points = timeline_line.get_transform().transform(coordinates)

    for annotation in annotations:
        box = Text.get_window_extent(annotation, renderer=renderer).padded(2.5)
        for start, end in zip(display_points[:-1], display_points[1:], strict=True):
            samples = np.linspace(start, end, 101)
            if any(box.contains(float(x), float(y)) for x, y in samples):
                raise RuntimeError(
                    f"Timeline line overlaps annotation: {annotation.get_text()!r}"
                )


def draw_age_shift(fig: plt.Figure, age: pd.DataFrame) -> None:
    fig.text(
        LEFT,
        0.607,
        "El centro de la distribución también se movió",
        color=INK,
        fontsize=16.5,
        fontweight="bold",
        family=FONT_BOLD,
    )
    draw_year_key(fig, 0.607)

    known = age.loc[age["mother_age_label"].ne("Sin especificar")].copy()
    known = known.sort_values("mother_age_code")
    labels = ["<15", "15–19", "20–24", "25–29", "30–34", "35–39", "40–44", "45+"]
    share_2014 = known["share_of_known_age_births_2014"].to_numpy() * 100
    share_2024 = known["share_of_known_age_births_2024"].to_numpy() * 100
    positions = np.arange(len(known))

    axis = fig.add_axes([0.115, 0.489, 0.49, 0.095])
    style_axis(axis)
    axis.set_xlim(0, 28)
    axis.set_ylim(-0.7, len(known) - 0.3)
    for value in (0, 10, 20):
        axis.axvline(value, color=GRID, linewidth=0.65, zorder=0)
    for y, old, new in zip(positions, share_2014, share_2024, strict=True):
        axis.plot([old, new], [y, y], color=GRID, linewidth=1.7, zorder=1)
    axis.scatter(
        share_2014,
        positions,
        s=32,
        facecolor=BG,
        edgecolor=NEUTRAL,
        linewidth=1.2,
        zorder=2,
    )
    axis.scatter(share_2024, positions, s=38, color=ACCENT, zorder=3)
    axis.set_yticks(positions)
    axis.set_yticklabels(labels, color=INK, fontsize=8.3)
    axis.set_xticks([0, 10, 20])
    axis.set_xticklabels(["0%", "10%", "20%"])
    axis.invert_yaxis()

    fig.text(
        0.655,
        0.557,
        "20–24  →  25–29",
        color=ACCENT,
        fontsize=17,
        fontweight="bold",
        family=FONT_BOLD,
    )
    fig.text(
        0.655,
        0.535,
        "grupo con más nacimientos",
        color=NEUTRAL,
        fontsize=8,
        family=FONT,
    )
    fig.text(
        0.655,
        0.505,
        "Menores de 25     40,3%  →  30,8%\n"
        "30 años o más      36,6%  →  43,6%",
        color=INK,
        fontsize=9.2,
        family=FONT,
        linespacing=1.5,
    )
    fig.text(
        RIGHT,
        0.478,
        "Participaciones sobre nacimientos con edad materna conocida.",
        color=NEUTRAL,
        fontsize=8,
        family=FONT,
        ha="right",
    )


def draw_province_shift(fig: plt.Figure, province: pd.DataFrame) -> None:
    fig.text(
        LEFT,
        0.447,
        "El desplazamiento alcanzó a las 24 jurisdicciones",
        color=INK,
        fontsize=16.5,
        fontweight="bold",
        family=FONT_BOLD,
    )
    fig.text(
        LEFT,
        0.424,
        "En todas aumentó el peso de nacimientos de madres de 30 años o más. "
        "Formosa registra 32,6%; CABA, 69,2% en 2024.",
        color=INK,
        fontsize=8.7,
        family=FONT,
    )
    draw_year_key(fig, 0.447)

    ordered = province.sort_values("age_30_plus_share_2024").reset_index(drop=True)
    old = ordered["age_30_plus_share_2014"].to_numpy() * 100
    new = ordered["age_30_plus_share_2024"].to_numpy() * 100
    positions = np.arange(len(ordered))

    axis = fig.add_axes([0.22, 0.158, 0.665, 0.247])
    style_axis(axis)
    axis.set_xlim(20, 74)
    axis.set_ylim(-0.8, len(ordered) - 0.2)
    for value in (20, 30, 40, 50, 60, 70):
        axis.axvline(value, color=GRID, linewidth=0.6, zorder=0)
    for y, old_value, new_value in zip(positions, old, new, strict=True):
        axis.plot(
            [old_value, new_value],
            [y, y],
            color=GRID,
            linewidth=1.5,
            zorder=1,
            solid_capstyle="round",
        )
    axis.scatter(
        old,
        positions,
        s=24,
        facecolor=BG,
        edgecolor=NEUTRAL,
        linewidth=1.0,
        zorder=2,
    )
    axis.scatter(new, positions, s=29, color=ACCENT, zorder=3)
    axis.set_yticks(positions)
    axis.set_yticklabels(ordered["province_label"], fontsize=8.2, color=INK)
    axis.set_xticks([20, 30, 40, 50, 60, 70])
    axis.set_xticklabels(["20%", "30%", "40%", "50%", "60%", "70%"])
    axis.xaxis.tick_top()
    axis.tick_params(axis="x", pad=3)
    axis.invert_yaxis()

    for y, value in zip(positions, new, strict=True):
        axis.text(
            value + 0.65,
            y,
            format_pct_es(value),
            color=ACCENT,
            fontsize=8,
            family=FONT,
            va="center",
            fontweight="bold",
        )

    lookup = ordered.set_index("province_label")
    tf_shift = float(lookup.loc["Tierra del Fuego", "age_30_plus_share_change_pp"])
    sj_shift = float(lookup.loc["San Juan", "age_30_plus_share_change_pp"])
    fig.text(
        LEFT,
        0.139,
        "Mayor aumento: Tierra del Fuego, +"
        f"{format_pct_es(tf_shift).removesuffix('%')} pp.  "
        "Menor: San Juan, +"
        f"{format_pct_es(sj_shift).removesuffix('%')} pp.  "
        "En las 24 también cayó la participación de menores de 25.",
        color=NEUTRAL,
        fontsize=8,
        family=FONT,
    )


def draw_context_and_footer(fig: plt.Figure) -> None:
    fig.text(
        LEFT,
        0.108,
        "El cambio ya forma parte de la planificación pública",
        color=INK,
        fontsize=15.5,
        fontweight="bold",
        family=FONT_BOLD,
    )
    fig.text(
        LEFT,
        0.071,
        "−27%",
        color=INK,
        fontsize=29,
        fontweight="bold",
        family=FONT_BOLD,
        va="center",
    )
    fig.text(
        0.205,
        0.079,
        "estudiantes de primaria proyectados entre 2025 y 2030\n"
        "—1,17 millones menos—",
        color=INK,
        fontsize=10.2,
        family=FONT,
        linespacing=1.35,
        va="center",
    )
    fig.text(
        RIGHT,
        0.073,
        "Proyección externa DNP/RENAPER (2025).\nNo se empalma con la serie DEIS.",
        color=NEUTRAL,
        fontsize=8,
        family=FONT,
        ha="right",
        linespacing=1.35,
        va="center",
    )

    figure_rule(fig, 0.049)
    footer = (
        "Fuente principal: DEIS, Nacidos vivos 2014–2024. Año de registro, no necesariamente de ocurrencia.\n"
        "Edad desconocida excluida de porcentajes etarios: 1,16% (2014) y 0,26% (2024). "
        "Son conteos y composiciones, no tasas de fecundidad."
    )
    fig.text(
        LEFT,
        0.038,
        footer,
        color=NEUTRAL,
        fontsize=8,
        family=FONT,
        va="top",
        linespacing=1.25,
    )
    fig.text(
        LEFT,
        0.012,
        "Datos: argentina.gob.ar/salud/deis/datos/nacidosvivos   ·   Contexto educativo: argentina.gob.ar/node/477046",
        color=NEUTRAL,
        fontsize=8,
        family=FONT,
    )
    fig.text(
        RIGHT,
        0.012,
        PSEUDONYM,
        color=NEUTRAL,
        fontsize=8,
        fontweight="bold",
        family=FONT,
        ha="right",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_svg(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    normalized = "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
    path.write_text(normalized, encoding="utf-8")


def write_manifest() -> None:
    from PIL import Image

    with Image.open(PNG_OUTPUT) as image:
        width, height = image.size
    payload = {
        "prototype": VERSION,
        "status": "not_for_submission",
        "canvas": {
            "format": "A3 portrait",
            "width_mm": A3_WIDTH_MM,
            "height_mm": A3_HEIGHT_MM,
            "png_width_px": width,
            "png_height_px": height,
        },
        "files": {
            SVG_OUTPUT.name: {
                "bytes": SVG_OUTPUT.stat().st_size,
                "sha256": sha256(SVG_OUTPUT),
            },
            PNG_OUTPUT.name: {
                "bytes": PNG_OUTPUT.stat().st_size,
                "sha256": sha256(PNG_OUTPUT),
            },
            PDF_OUTPUT.name: {
                "path": str(PDF_OUTPUT.relative_to(ROOT)),
                "bytes": PDF_OUTPUT.stat().st_size,
                "sha256": sha256(PDF_OUTPUT),
            },
        },
        "palette": {
            "background": BG,
            "ink": INK,
            "accent_2024": ACCENT,
            "neutral_2014": NEUTRAL,
            "grid": GRID,
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
    PDF_EXPORTS.mkdir(parents=True, exist_ok=True)
    (ROOT / "tmp" / "matplotlib").mkdir(parents=True, exist_ok=True)

    plt.rcParams.update(
        {
            "font.family": FONT,
            "text.color": INK,
            "axes.labelcolor": INK,
            "axes.edgecolor": GRID,
            "xtick.color": NEUTRAL,
            "ytick.color": NEUTRAL,
            "svg.fonttype": "none",
            "svg.hashsalt": f"menos-cunas-prototype-{VERSION}",
            "pdf.fonttype": 42,
        }
    )
    figure = plt.figure(
        figsize=(A3_WIDTH_MM / 25.4, A3_HEIGHT_MM / 25.4),
        facecolor=BG,
    )
    hero_arrow, hero_numbers = draw_header(figure, national)
    figure_rule(figure, 0.795)
    timeline_line, timeline_annotations = draw_timeline(figure, national)
    figure_rule(figure, 0.628)
    draw_age_shift(figure, age)
    figure_rule(figure, 0.464)
    draw_province_shift(figure, province)
    figure_rule(figure, 0.124)
    draw_context_and_footer(figure)
    figure.canvas.draw()
    validate_header_clearance(figure, hero_arrow, hero_numbers)
    validate_timeline_clearance(figure, timeline_line, timeline_annotations)

    metadata = {
        "Title": f"Menos cunas, otro país — prototipo {VERSION}",
        "Description": (
            "Historia visual sobre la caída de nacimientos registrados y el "
            "desplazamiento de la composición por edad materna en Argentina."
        ),
        "Creator": "Proyecto Contar con Datos 2026",
        "Date": "2026-09-25",
    }
    figure.savefig(SVG_OUTPUT, format="svg", facecolor=BG, metadata=metadata)
    normalize_svg(SVG_OUTPUT)
    png_metadata = {
        "Title": metadata["Title"],
        "Description": metadata["Description"],
        "Software": "Matplotlib 3.11.2",
    }
    figure.savefig(
        PNG_OUTPUT,
        format="png",
        dpi=240,
        facecolor=BG,
        metadata=png_metadata,
    )
    pdf_metadata = {
        "Title": metadata["Title"],
        "Author": "Proyecto Contar con Datos 2026",
        "Subject": metadata["Description"],
        "Creator": "Matplotlib 3.11.2",
        "Producer": "Proyecto Contar con Datos 2026",
        "CreationDate": datetime(2026, 9, 25, tzinfo=UTC),
        "ModDate": datetime(2026, 9, 25, tzinfo=UTC),
    }
    figure.savefig(
        PDF_OUTPUT,
        format="pdf",
        facecolor=BG,
        metadata=pdf_metadata,
    )
    plt.close(figure)
    write_manifest()
    print(SVG_OUTPUT.relative_to(ROOT))
    print(PNG_OUTPUT.relative_to(ROOT))
    print(PDF_OUTPUT.relative_to(ROOT))
    print(MANIFEST_OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()

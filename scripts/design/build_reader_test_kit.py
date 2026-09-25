#!/usr/bin/env python3
"""Build the printable facilitator kit for the v0.6 reader test."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "pdf" / "reader-test-kit-v0.6.pdf"
FONT_DIR = ROOT / ".venv" / "lib" / "python3.12" / "site-packages" / "matplotlib" / "mpl-data" / "fonts" / "ttf"
FONT_REGULAR = FONT_DIR / "DejaVuSans.ttf"
FONT_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"

INK = HexColor("#1C252B")
ACCENT = HexColor("#0F6370")
NEUTRAL = HexColor("#6B665E")
GRID = HexColor("#D8D2C7")
PAPER = HexColor("#FFFFFF")

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT = 18 * mm
RIGHT = PAGE_WIDTH - 18 * mm
TOP = PAGE_HEIGHT - 16 * mm
BOTTOM = 15 * mm


def register_fonts() -> None:
    if not FONT_REGULAR.exists() or not FONT_BOLD.exists():
        raise FileNotFoundError("Bundled DejaVu fonts are missing")
    pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_REGULAR)))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONT_BOLD)))


def wrap(text: str, font: str, size: float, width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if not current or pdfmetrics.stringWidth(candidate, font, size) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    canvas: Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    *,
    font: str = "DejaVu",
    size: float = 9.2,
    leading: float = 12,
    color=INK,
) -> float:
    canvas.setFillColor(color)
    canvas.setFont(font, size)
    for line in wrap(text, font, size, width):
        canvas.drawString(x, y, line)
        y -= leading
    return y


def rule(canvas: Canvas, y: float) -> None:
    canvas.setStrokeColor(GRID)
    canvas.setLineWidth(0.7)
    canvas.line(LEFT, y, RIGHT, y)


def checkbox(canvas: Canvas, x: float, y: float, label: str, size: float = 8.7) -> None:
    side = 3.4 * mm
    canvas.setStrokeColor(NEUTRAL)
    canvas.setLineWidth(0.8)
    canvas.rect(x, y - side + 1.5, side, side, stroke=1, fill=0)
    canvas.setFillColor(INK)
    canvas.setFont("DejaVu", size)
    canvas.drawString(x + side + 4, y, label)


def answer_lines(canvas: Canvas, y: float, count: int = 2) -> float:
    canvas.setStrokeColor(GRID)
    canvas.setLineWidth(0.6)
    for _ in range(count):
        y -= 8 * mm
        canvas.line(LEFT, y, RIGHT, y)
    return y


def section_title(canvas: Canvas, title: str, y: float) -> float:
    canvas.setFillColor(ACCENT)
    canvas.setFont("DejaVu-Bold", 11.5)
    canvas.drawString(LEFT, y, title)
    return y - 6 * mm


def page_header(canvas: Canvas, label: str) -> None:
    canvas.setFillColor(NEUTRAL)
    canvas.setFont("DejaVu-Bold", 7.5)
    canvas.drawString(LEFT, TOP, "MENOS CUNAS, OTRO PAÍS · PRUEBA DE LECTURA V0.6")
    canvas.drawRightString(RIGHT, TOP, label)
    rule(canvas, TOP - 4 * mm)


def page_footer(canvas: Canvas, page: int, total: int = 4) -> None:
    rule(canvas, BOTTOM + 5 * mm)
    canvas.setFillColor(NEUTRAL)
    canvas.setFont("DejaVu", 7.2)
    canvas.drawString(LEFT, BOTTOM, "No registrar nombre, correo ni datos de contacto.")
    canvas.drawRightString(RIGHT, BOTTOM, f"UMBRAL SUR · {page}/{total}")


def facilitator_page(canvas: Canvas) -> None:
    page_header(canvas, "GUÍA DEL FACILITADOR")
    y = TOP - 15 * mm
    canvas.setFillColor(INK)
    canvas.setFont("DejaVu-Bold", 22)
    canvas.drawString(LEFT, y, "Prueba física y de comprensión")
    y -= 8 * mm
    y = draw_wrapped(
        canvas,
        "Objetivo: comprobar qué entiende una persona sin explicación previa y detectar problemas de legibilidad antes de generar la entrega final.",
        LEFT,
        y,
        RIGHT - LEFT,
        size=10.2,
        leading=14,
    )

    y -= 4 * mm
    y = section_title(canvas, "1. Qué imprimir", y)
    checkbox(canvas, LEFT, y, "Pieza v0.6 en color, A3, una cara, escala 100%.")
    y -= 7 * mm
    checkbox(canvas, LEFT, y, "Este kit en A4, una cara. Una ficha por sesión.")
    y -= 7 * mm
    checkbox(canvas, LEFT, y, "Desactivar 'ajustar', 'encoger' y cualquier reescalado.")
    y -= 10 * mm

    y = section_title(canvas, "2. Control de la copia A3", y)
    checks = [
        "La regla de control de impresión confirma 100% de escala.",
        "No hay bordes, rótulos ni fuentes cortados.",
        "Los textos del pie se leen a 40-50 cm con luz normal.",
        "El contraste entre gris, petróleo y fondo se conserva.",
    ]
    for label in checks:
        checkbox(canvas, LEFT, y, label)
        y -= 7 * mm
    y -= 3 * mm

    y = section_title(canvas, "3. Selección y encuadre", y)
    y = draw_wrapped(
        canvas,
        "Realizar tres sesiones individuales de 5 a 8 minutos. Buscar, si es posible: una persona familiarizada con datos, una sin formación estadística y una de 45 años o más. No explicar la pieza, no corregir respuestas y no sugerir palabras clave.",
        LEFT,
        y,
        RIGHT - LEFT,
        size=9.2,
        leading=12,
    )
    y -= 3 * mm

    y = section_title(canvas, "4. Secuencia exacta", y)
    steps = [
        ("5 segundos", "Mostrar, retirar y registrar mensaje principal y dato recordado."),
        ("30 segundos", "Volver a mostrar y preguntar por inicio de la caída, edad materna y alcance territorial."),
        ("2 minutos", "Permitir lectura libre y preguntar por símbolos, CABA, proyección educativa y dudas."),
    ]
    for title, body in steps:
        canvas.setFillColor(INK)
        canvas.setFont("DejaVu-Bold", 9.2)
        canvas.drawString(LEFT, y, title)
        y = draw_wrapped(canvas, body, LEFT + 30 * mm, y, RIGHT - LEFT - 30 * mm)
        y -= 3 * mm

    y -= 2 * mm
    y = section_title(canvas, "5. Regla de aprobación", y)
    y = draw_wrapped(
        canvas,
        "Avanza si las tres personas identifican la caída de nacimientos; al menos dos responden correctamente las tres preguntas de 30 segundos; no se repite una confusión crítica; y ningún texto es señalado como ilegible por dos personas.",
        LEFT,
        y,
        RIGHT - LEFT,
        size=9.2,
        leading=12,
    )
    y -= 4 * mm
    canvas.setFillColor(ACCENT)
    canvas.setFont("DejaVu-Bold", 9.2)
    canvas.drawString(LEFT, y, "No retirar la marca NO PRESENTAR hasta completar y revisar las tres fichas.")
    page_footer(canvas, 1)
    canvas.showPage()


def session_page(canvas: Canvas, session: int) -> None:
    page_header(canvas, f"SESIÓN {session} DE 3")
    y = TOP - 13 * mm
    canvas.setFillColor(INK)
    canvas.setFont("DejaVu-Bold", 19)
    canvas.drawString(LEFT, y, f"Ficha anónima · sesión {session}")
    canvas.setFont("DejaVu", 8.5)
    canvas.setFillColor(NEUTRAL)
    canvas.drawRightString(RIGHT, y, "Fecha: ____ / ____ / ______")
    y -= 10 * mm

    checkbox(canvas, LEFT, y, "Familiaridad con datos")
    checkbox(canvas, LEFT + 58 * mm, y, "Sin formación estadística")
    checkbox(canvas, LEFT + 126 * mm, y, "45 años o más")
    y -= 9 * mm
    checkbox(canvas, LEFT, y, "Copia A3 a 100% verificada")
    checkbox(canvas, LEFT + 74 * mm, y, "Iluminación normal")
    y -= 11 * mm

    y = section_title(canvas, "Exposición de 5 segundos", y)
    y = draw_wrapped(canvas, "¿Cuál te parece que es el mensaje principal?", LEFT, y, RIGHT - LEFT)
    y = answer_lines(canvas, y, 2) - 5 * mm
    y = draw_wrapped(canvas, "¿Qué número o frase recordás?", LEFT, y, RIGHT - LEFT)
    y = answer_lines(canvas, y, 1) - 5 * mm
    checkbox(canvas, LEFT, y, "Reconoce la caída")
    checkbox(canvas, LEFT + 55 * mm, y, "Recuerda 46,8%, 777 mil o 413 mil")
    y -= 11 * mm

    y = section_title(canvas, "Lectura de 30 segundos", y)
    questions = [
        ("1. ¿La caída empezó antes o después de 2020?", "Esperado: antes"),
        ("2. ¿Qué cambió respecto de la edad de las madres?", "Esperado: edades mayores"),
        ("3. ¿Ocurre en algunas o en las 24 jurisdicciones?", "Esperado: las 24"),
    ]
    for question, expected in questions:
        canvas.setFillColor(INK)
        canvas.setFont("DejaVu", 8.8)
        canvas.drawString(LEFT, y, question)
        canvas.setFillColor(NEUTRAL)
        canvas.setFont("DejaVu", 7.3)
        canvas.drawRightString(RIGHT - 18 * mm, y, expected)
        checkbox(canvas, RIGHT - 13 * mm, y, "OK", size=7.5)
        y -= 8 * mm
    canvas.setFillColor(INK)
    canvas.setFont("DejaVu-Bold", 8.8)
    canvas.drawString(LEFT, y, "Resultado de esta sección: ____ / 3")
    y -= 11 * mm

    y = section_title(canvas, "Lectura libre de 2 minutos", y)
    questions = [
        ("1. ¿Qué representan el punto vacío y el lleno?", "2014 / 2024"),
        ("2. ¿Qué jurisdicción tiene la mayor proporción en 2024?", "CABA"),
        ("3. ¿La cifra educativa es observada o proyectada?", "Proyectada"),
    ]
    for question, expected in questions:
        canvas.setFillColor(INK)
        canvas.setFont("DejaVu", 8.8)
        canvas.drawString(LEFT, y, question)
        canvas.setFillColor(NEUTRAL)
        canvas.setFont("DejaVu", 7.3)
        canvas.drawRightString(RIGHT - 18 * mm, y, expected)
        checkbox(canvas, RIGHT - 13 * mm, y, "OK", size=7.5)
        y -= 8 * mm

    y -= 1 * mm
    y = draw_wrapped(canvas, "¿Qué texto o dato resultó más difícil de leer?", LEFT, y, RIGHT - LEFT)
    y = answer_lines(canvas, y, 1) - 4 * mm
    y = draw_wrapped(canvas, "¿Qué conclusión se llevaría después de verla una sola vez?", LEFT, y, RIGHT - LEFT)
    y = answer_lines(canvas, y, 1) - 4 * mm
    y = draw_wrapped(canvas, "Interpretación equivocada o comentario espontáneo:", LEFT, y, RIGHT - LEFT)
    y = answer_lines(canvas, y, 1) - 5 * mm

    checkbox(canvas, LEFT, y, "Sin confusión crítica")
    checkbox(canvas, LEFT + 55 * mm, y, "Confusión crítica")
    checkbox(canvas, LEFT + 105 * mm, y, "Señala texto ilegible")
    page_footer(canvas, session + 1)
    canvas.showPage()


def main() -> None:
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(
        str(OUTPUT),
        pagesize=A4,
        pageCompression=1,
        invariant=1,
        initialFontName="DejaVu",
        initialFontSize=9,
    )
    canvas.setTitle("Kit de prueba de lectura v0.6")
    canvas.setAuthor("UMBRAL SUR")
    canvas.setSubject("Validación física y de comprensión del prototipo v0.6")
    canvas.setCreator("Proyecto Contar con Datos 2026")
    facilitator_page(canvas)
    for session in range(1, 4):
        session_page(canvas, session)
    canvas.save()
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()

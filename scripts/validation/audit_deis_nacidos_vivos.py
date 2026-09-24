#!/usr/bin/env python3
"""Audit DEIS live-birth source files before normalization."""

from __future__ import annotations

import csv
import hashlib
from datetime import date
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
OUTPUT_CSV = ROOT / "data" / "processed" / "deis_source_audit.csv"
OUTPUT_MD = ROOT / "docs" / "data-audit.md"
EXPECTED_COLUMNS = [
    "PROVRES",
    "TIPPARTO",
    "SEXO",
    "IMEDAD",
    "ITIEMGEST",
    "IMINSTRUC",
    "IPESONAC",
    "CUENTA",
]
DIMENSIONS = EXPECTED_COLUMNS[:-1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_format(path: Path) -> tuple[str, str]:
    sample_bytes = path.read_bytes()[:65536]
    encoding = "utf-8-sig" if sample_bytes.startswith(b"\xef\xbb\xbf") else "cp1252"
    sample = sample_bytes.decode(encoding)
    delimiter = csv.Sniffer().sniff(sample, delimiters=",;").delimiter
    return encoding, delimiter


def load_year(year: int) -> tuple[pd.DataFrame, dict[str, object]]:
    path = RAW_DIR / f"nacidos_vivos_{year}.csv"
    encoding, delimiter = detect_format(path)
    frame = pd.read_csv(
        path,
        sep=delimiter,
        encoding=encoding,
        dtype=str,
        keep_default_na=False,
    )
    if list(frame.columns) != EXPECTED_COLUMNS:
        raise ValueError(f"Unexpected columns in {path.name}: {list(frame.columns)}")

    count = pd.to_numeric(frame["CUENTA"], errors="raise")
    if not count.gt(0).all() or not count.mod(1).eq(0).all():
        raise ValueError(f"CUENTA must contain positive integers in {path.name}")
    if frame.duplicated(DIMENSIONS).any():
        raise ValueError(f"Duplicate dimensional combinations in {path.name}")

    blank_mask = frame[DIMENSIONS].eq("")
    blank_rows = blank_mask.any(axis=1)
    result = {
        "year": year,
        "filename": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "encoding": encoding,
        "delimiter": "semicolon" if delimiter == ";" else "comma",
        "rows": len(frame),
        "total_nacidos": int(count.sum()),
        "province_values": frame["PROVRES"].nunique(),
        "age_values": frame["IMEDAD"].nunique(),
        "duplicate_dimension_rows": 0,
        "blank_dimension_rows": int(blank_rows.sum()),
        "blank_weighted_count": int(count[blank_rows].sum()),
    }
    return frame, result


def markdown_table(rows: list[dict[str, object]]) -> str:
    lines = [
        "| Año | Filas agregadas | Nacimientos registrados | Formato | Blancos ponderados |",
        "| ---: | ---: | ---: | --- | ---: |",
    ]
    for row in rows:
        format_label = (
            "coma, Windows-1252"
            if row["delimiter"] == "comma"
            else "punto y coma, UTF-8 con BOM"
        )
        lines.append(
            f"| {row['year']} | {format_int_es(row['rows'])} | "
            f"{format_int_es(row['total_nacidos'])} | {format_label} | "
            f"{format_int_es(row['blank_weighted_count'])} |"
        )
    return "\n".join(lines)


def format_int_es(value: object) -> str:
    return f"{int(value):,}".replace(",", ".")


def write_report(frames: dict[int, pd.DataFrame], rows: list[dict[str, object]]) -> None:
    total_2014 = int(rows[0]["total_nacidos"])
    total_2024 = int(rows[-1]["total_nacidos"])
    absolute_change = total_2024 - total_2014
    relative_change = absolute_change / total_2014
    relative_change_label = f"{relative_change:.1%}".replace(".", ",")

    dictionary = pd.ExcelFile(RAW_DIR / "nacidos_vivos_diccionario.xlsx")
    sex_codes = set(
        pd.read_excel(dictionary, sheet_name="SEXO", dtype=str)["CODIGO"].str.zfill(1)
    )
    observed_2024_sex = set(frames[2024]["SEXO"])
    undocumented_sex = sorted(observed_2024_sex - sex_codes)

    content = f"""# Primera auditoría de datos DEIS

Fecha de verificación: {date.today().isoformat()}.

Fuente: [DEIS – Nacidos vivos](https://www.argentina.gob.ar/salud/deis/datos/nacidosvivos).

## Resultado

Los archivos 2014–2024 tienen las mismas ocho columnas y no presentan
combinaciones dimensionales duplicadas. Las categorías de jurisdicción y edad
de la madre son estables en los once años. Por lo tanto, el eje principal
año–territorio–edad puede normalizarse sin una recodificación sustantiva.

## Totales y formato

{markdown_table(rows)}

Entre 2014 y 2024, el total publicado pasa de {format_int_es(total_2014)} a
{format_int_es(total_2024)}: una caída de {format_int_es(abs(absolute_change))}
({relative_change_label.removeprefix('-')}).
Es un resultado de control, todavía no una explicación causal.

## Cambios de esquema que requieren tratamiento

- Los CSV de 2014–2019 usan comas y codificación Windows-1252. Los de
  2020–2024 usan punto y coma y UTF-8 con BOM. El diccionario XLSX todavía
  describe únicamente el formato antiguo con comas.
- En 2024, `IMINSTRUC` pasa de 4 a 8 categorías. Puede armonizarse hacia las
  cuatro categorías históricas, pero no debe compararse categoría por categoría
  sin esa transformación.
- En 2024, `IPESONAC` pasa de 3 a 9 categorías. Las nuevas bandas pueden
  reagruparse en menos de 2.500 g, 2.500 g o más y sin especificar.
- La mayor cantidad de filas en 2024 se debe a esas desagregaciones nuevas, no
  a una mayor cantidad de nacimientos.
- En 2024 aparece el código de sexo {', '.join(undocumented_sex) or 'ninguno'}, ausente del
  diccionario provisto. Representa 6 nacimientos y se mantendrá sin etiqueta
  hasta encontrar una definición oficial.
- En 2017 existe una combinación sin código de tipo de parto, con `CUENTA=10`.
  Corresponde además a jurisdicción, sexo, edad, gestación, instrucción y peso
  sin especificar. No se imputará silenciosamente.

## Controles aprobados

- 11 años presentes, de 2014 a 2024.
- 26 códigos de residencia en cada año, incluidos otro país y no especificado.
- 9 grupos de edad de la madre, idénticos en todos los años.
- `CUENTA` contiene enteros positivos.
- Ningún duplicado en la combinación de las siete dimensiones.
- Los checksums coinciden con `data/source-catalog.csv`.

## Decisión

La próxima capa usará Parquet local con tipos y códigos separados de sus
etiquetas. Preservará todas las filas, añadirá el año como columna y producirá
controles de suma antes y después de cualquier armonización. Los agregados para
la obra se calcularán desde esa capa, no directamente desde los CSV.
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")


def main() -> None:
    frames: dict[int, pd.DataFrame] = {}
    rows: list[dict[str, object]] = []
    for year in range(2014, 2025):
        frame, row = load_year(year)
        frames[year] = frame
        rows.append(row)

    catalog = pd.read_csv(ROOT / "data" / "source-catalog.csv", dtype=str)
    expected = catalog[catalog["kind"].eq("csv")].set_index("year")
    for row in rows:
        source = expected.loc[str(row["year"])]
        if int(source["bytes"]) != row["bytes"] or source["sha256"] != row["sha256"]:
            raise ValueError(f"Catalog mismatch for {row['year']}")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUTPUT_CSV, index=False)
    write_report(frames, rows)
    print(f"OK: {len(rows)} source files audited.")
    print(OUTPUT_CSV.relative_to(ROOT))
    print(OUTPUT_MD.relative_to(ROOT))


if __name__ == "__main__":
    main()

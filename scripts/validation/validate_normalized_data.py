#!/usr/bin/env python3
"""Independently validate the normalized DEIS registered-birth dataset."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
PARQUET = ROOT / "data" / "interim" / "nacidos_vivos_2014_2024.parquet"
SOURCE_AUDIT = ROOT / "data" / "processed" / "deis_source_audit.csv"
CONTROLS = ROOT / "data" / "mappings" / "deis_2024_official_controls.csv"
OUTPUT_DIR = ROOT / "data" / "processed"
REPORT = ROOT / "docs" / "data-quality.md"

EXPECTED_FIELDS = [
    ("year", pa.int16(), False),
    ("source_file", pa.string(), False),
    ("source_row", pa.int32(), False),
    ("province_code", pa.string(), False),
    ("province_label", pa.string(), False),
    ("residence_scope", pa.string(), False),
    ("birth_type_code", pa.int8(), True),
    ("birth_type_label", pa.string(), True),
    ("sex_code", pa.int8(), False),
    ("sex_label", pa.string(), False),
    ("mother_age_code", pa.int8(), False),
    ("mother_age_label", pa.string(), False),
    ("gestation_code", pa.int8(), False),
    ("gestation_label", pa.string(), False),
    ("education_source_code", pa.int8(), False),
    ("education_source_label", pa.string(), False),
    ("education_harmonized_code", pa.int8(), False),
    ("education_harmonized_label", pa.string(), False),
    ("weight_source_code", pa.int8(), False),
    ("weight_source_label", pa.string(), False),
    ("weight_harmonized_code", pa.int8(), False),
    ("weight_harmonized_label", pa.string(), False),
    ("count", pa.int64(), False),
    ("flag_missing_birth_type", pa.bool_(), False),
    ("flag_undocumented_sex", pa.bool_(), False),
    ("flag_implausible_gestation_weight", pa.bool_(), False),
    ("quality_flags", pa.string(), True),
]

DIMENSION_COLUMNS = [
    "year",
    "province_code",
    "birth_type_code",
    "sex_code",
    "mother_age_code",
    "gestation_code",
    "education_source_code",
    "weight_source_code",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def format_int_es(value: object) -> str:
    return f"{int(value):,}".replace(",", ".")


def validate_schema(schema: pa.Schema) -> None:
    actual = [(field.name, field.type, field.nullable) for field in schema]
    require(actual == EXPECTED_FIELDS, f"Unexpected Parquet schema: {actual!r}")
    metadata = schema.metadata or {}
    for key in (b"pipeline_version", b"source_url", b"row_grain", b"coverage"):
        require(key in metadata, f"Missing schema metadata: {key.decode()}")


def validate_domains(frame: pd.DataFrame) -> None:
    expected_provinces = {
        "02", "06", "10", "14", "18", "22", "26", "30", "34", "38",
        "42", "46", "50", "54", "58", "62", "66", "70", "74", "78",
        "82", "86", "90", "94", "98", "99",
    }
    domains = {
        "province_code": expected_provinces,
        "birth_type_code": {1, 2, 9},
        "sex_code": {1, 2, 3, 9},
        "mother_age_code": set(range(1, 10)),
        "gestation_code": set(range(1, 9)),
        "education_harmonized_code": set(range(1, 5)),
        "weight_harmonized_code": set(range(1, 4)),
    }
    for column, expected in domains.items():
        observed = set(frame[column].dropna().tolist())
        require(observed <= expected, f"Invalid values in {column}: {sorted(observed - expected)}")
    require(
        set(frame["residence_scope"]) == {"argentina_province", "other_country", "unspecified"},
        "Invalid residence_scope domain",
    )
    require(frame["count"].gt(0).all(), "Counts must be positive")


def validate_source_identity(frame: pd.DataFrame) -> None:
    expected_filename = frame["year"].map(lambda year: f"nacidos_vivos_{year}.csv")
    require(
        frame["source_file"].eq(expected_filename).all(),
        "source_file does not agree with year",
    )
    for filename, source in frame.groupby("source_file", sort=False):
        expected_rows = list(range(2, len(source) + 2))
        require(
            sorted(source["source_row"].tolist()) == expected_rows,
            f"Missing or unexpected source-row positions in {filename}",
        )


def validate_label_relationships(frame: pd.DataFrame) -> None:
    stable_pairs = [
        ("province_code", "province_label"),
        ("birth_type_code", "birth_type_label"),
        ("sex_code", "sex_label"),
        ("mother_age_code", "mother_age_label"),
        ("gestation_code", "gestation_label"),
        ("education_harmonized_code", "education_harmonized_label"),
        ("weight_harmonized_code", "weight_harmonized_label"),
    ]
    for code, label in stable_pairs:
        pairs = frame[[code, label]].dropna()
        require(
            pairs.groupby(code)[label].nunique().le(1).all(),
            f"One {code} maps to multiple {label} values",
        )
        require(
            pairs.groupby(label)[code].nunique().le(1).all(),
            f"One {label} maps to multiple {code} values",
        )
    for code, label in (
        ("education_source_code", "education_source_label"),
        ("weight_source_code", "weight_source_label"),
    ):
        pairs = frame.assign(
            scheme=frame["year"].where(frame["year"].eq(2024), 2023)
        )[["scheme", code, label]]
        require(
            pairs.groupby(["scheme", code])[label].nunique().le(1).all(),
            f"One scheme/{code} maps to multiple labels",
        )
        require(
            pairs.groupby(["scheme", label])[code].nunique().le(1).all(),
            f"One scheme/{label} maps to multiple codes",
        )


def require_equal_series(actual: pd.Series, expected: pd.Series, label: str) -> None:
    if pd.api.types.is_numeric_dtype(actual.dtype):
        matches = actual.astype("Int64").reset_index(drop=True).equals(
            expected.astype("Int64").reset_index(drop=True)
        )
    else:
        matches = actual.astype("string").reset_index(drop=True).equals(
            expected.astype("string").reset_index(drop=True)
        )
    require(matches, f"Row-level source mismatch in {label}")


def validate_against_raw(frame: pd.DataFrame) -> None:
    """Re-read every raw row and compare source fields independently."""
    source_formats = pd.read_csv(SOURCE_AUDIT).set_index("year")
    workbook = ROOT / "data" / "raw" / "nacidos_vivos_diccionario.xlsx"

    def read_dictionary(sheet: str, pad: int | None = None) -> dict[str, str]:
        dictionary = pd.read_excel(workbook, sheet_name=sheet, dtype=str)
        codes = dictionary["CODIGO"].str.strip()
        if pad is not None:
            codes = codes.str.zfill(pad)
        return dict(zip(codes, dictionary["VALOR"].str.strip(), strict=True))

    province_labels = read_dictionary("PROVRES", 2)
    birth_type_labels = read_dictionary("TIPPARTO")
    sex_labels = read_dictionary("SEXO")
    education_mapping = pd.read_csv(ROOT / "data" / "mappings" / "education_harmonization.csv")
    weight_mapping = pd.read_csv(ROOT / "data" / "mappings" / "weight_harmonization.csv")

    for year in range(2014, 2025):
        info = source_formats.loc[year]
        raw = pd.read_csv(
            ROOT / "data" / "raw" / info["filename"],
            sep=";" if info["delimiter"] == "semicolon" else ",",
            encoding=info["encoding"],
            dtype=str,
            keep_default_na=False,
        )
        normalized = frame.loc[frame["year"].eq(year)].sort_values("source_row")
        require(len(raw) == len(normalized), f"Row-level length mismatch in {year}")

        age = raw["IMEDAD"].str.split(".", n=1, expand=True)
        gestation = raw["ITIEMGEST"].str.split(".", n=1, expand=True)
        education = raw["IMINSTRUC"].str.split(".", n=1, expand=True)
        weight = raw["IPESONAC"].str.split(".", n=1, expand=True)
        birth_type = pd.to_numeric(raw["TIPPARTO"].replace("", pd.NA))

        comparisons = {
            "province_code": raw["PROVRES"],
            "province_label": raw["PROVRES"].map(province_labels),
            "birth_type_code": birth_type,
            "birth_type_label": raw["TIPPARTO"].map(birth_type_labels),
            "sex_code": pd.to_numeric(raw["SEXO"]),
            "sex_label": raw["SEXO"].map(sex_labels).fillna("Código 3 no documentado"),
            "mother_age_code": pd.to_numeric(age[0]),
            "mother_age_label": age[1],
            "gestation_code": pd.to_numeric(gestation[0]),
            "gestation_label": gestation[1],
            "education_source_code": pd.to_numeric(education[0]),
            "education_source_label": education[1],
            "weight_source_code": pd.to_numeric(weight[0]),
            "weight_source_label": weight[1],
            "count": pd.to_numeric(raw["CUENTA"]),
        }
        scope = pd.Series("argentina_province", index=raw.index, dtype="string")
        scope = scope.mask(raw["PROVRES"].eq("98"), "other_country")
        comparisons["residence_scope"] = scope.mask(
            raw["PROVRES"].eq("99"), "unspecified"
        )

        for mapping, prefix, source_codes in (
            (education_mapping, "education", pd.to_numeric(education[0])),
            (weight_mapping, "weight", pd.to_numeric(weight[0])),
        ):
            active = mapping.loc[
                mapping["source_year_start"].le(year)
                & mapping["source_year_end"].ge(year)
            ].set_index("source_code")
            comparisons[f"{prefix}_harmonized_code"] = source_codes.map(
                active["harmonized_code"]
            )
            comparisons[f"{prefix}_harmonized_label"] = source_codes.map(
                active["harmonized_label"]
            )

        for column, expected in comparisons.items():
            require_equal_series(normalized[column], expected, f"{year}/{column}")


def validate_text(frame: pd.DataFrame) -> None:
    text_columns = [
        column
        for column in frame.columns
        if column.endswith("_label") or column in {"source_file", "quality_flags"}
    ]
    bad_pattern = re.compile(r"\ufffd|Ã|Â|â|[\x00-\x08\x0b\x0c\x0e-\x1f]")
    for column in text_columns:
        bad = frame[column].dropna().astype(str).str.contains(bad_pattern, regex=True)
        require(not bad.any(), f"Encoding/control-character issue in {column}")


def recompute_flags(frame: pd.DataFrame) -> dict[str, pd.Series]:
    return {
        "missing_birth_type": frame["birth_type_code"].isna(),
        "undocumented_sex_code": frame["sex_code"].eq(3),
        "implausible_gestation_weight": (
            frame["gestation_code"].eq(1) & frame["weight_harmonized_code"].eq(2)
        ),
    }


def expected_quality_string(masks: dict[str, pd.Series]) -> pd.Series:
    output = pd.Series(pd.NA, index=next(iter(masks.values())).index, dtype="string")
    for name, mask in masks.items():
        output = output.mask(mask & output.isna(), name)
        output = output.mask(mask & output.notna() & ~output.str.contains(name, na=False), output + "|" + name)
    return output


def validate_flags(frame: pd.DataFrame) -> dict[str, pd.Series]:
    masks = recompute_flags(frame)
    require(
        frame["flag_missing_birth_type"].equals(masks["missing_birth_type"]),
        "Incorrect missing-birth-type flags",
    )
    require(
        frame["flag_undocumented_sex"].equals(masks["undocumented_sex_code"]),
        "Incorrect undocumented-sex flags",
    )
    require(
        frame["flag_implausible_gestation_weight"].equals(
            masks["implausible_gestation_weight"]
        ),
        "Incorrect gestation/weight flags",
    )
    expected_strings = expected_quality_string(masks)
    require(
        frame["quality_flags"].astype("string").equals(expected_strings),
        "quality_flags does not match the independent masks",
    )
    expected_counts = {
        "missing_birth_type": (1, 10),
        "undocumented_sex_code": (6, 6),
        "implausible_gestation_weight": (43, 48),
    }
    for name, mask in masks.items():
        actual = (int(mask.sum()), int(frame.loc[mask, "count"].sum()))
        require(actual == expected_counts[name], f"Unexpected {name} count: {actual}")
    return masks


def reconcile_sources(frame: pd.DataFrame, masks: dict[str, pd.Series]) -> pd.DataFrame:
    source = pd.read_csv(SOURCE_AUDIT)
    observed = (
        frame.groupby("year", as_index=False)
        .agg(normalized_rows=("count", "size"), normalized_total=("count", "sum"))
    )
    result = source[["year", "rows", "total_nacidos"]].merge(
        observed, on="year", validate="one_to_one"
    )
    result = result.rename(
        columns={"rows": "source_rows", "total_nacidos": "source_total"}
    )
    any_flag = pd.concat(masks.values(), axis=1).any(axis=1)
    flags = (
        frame.assign(_flag=any_flag)
        .loc[lambda data: data["_flag"]]
        .groupby("year")
        .agg(flagged_rows=("count", "size"), flagged_count=("count", "sum"))
        .reindex(result["year"], fill_value=0)
        .reset_index()
    )
    result = result.merge(flags, on="year", validate="one_to_one")
    result["row_difference"] = result["normalized_rows"] - result["source_rows"]
    result["count_difference"] = result["normalized_total"] - result["source_total"]
    result["passed"] = result["row_difference"].eq(0) & result["count_difference"].eq(0)
    require(result["passed"].all(), "Normalized rows/totals do not match source audit")
    require(len(frame) == int(source["rows"].sum()), "Grand row count mismatch")
    require(int(frame["count"].sum()) == int(source["total_nacidos"].sum()), "Grand total mismatch")
    return result[
        [
            "year", "source_rows", "normalized_rows", "row_difference",
            "source_total", "normalized_total", "count_difference",
            "flagged_rows", "flagged_count", "passed",
        ]
    ]


def missingness_table(frame: pd.DataFrame) -> pd.DataFrame:
    definitions = {
        "province": frame["province_code"].eq("99"),
        "birth_type": frame["birth_type_code"].isna() | frame["birth_type_code"].eq(9),
        "sex_unspecified": frame["sex_code"].eq(9),
        "sex_undocumented_code_3": frame["sex_code"].eq(3),
        "mother_age": frame["mother_age_code"].eq(9),
        "gestation": frame["gestation_code"].eq(8),
        "education_harmonized": frame["education_harmonized_code"].eq(4),
        "weight_harmonized": frame["weight_harmonized_code"].eq(3),
    }
    rows: list[dict[str, object]] = []
    for year, yearly in frame.groupby("year", sort=True):
        total = int(yearly["count"].sum())
        for variable, full_mask in definitions.items():
            mask = full_mask.loc[yearly.index]
            unspecified = int(yearly.loc[mask, "count"].sum())
            rows.append(
                {
                    "year": int(year),
                    "variable": variable,
                    "unspecified_count": unspecified,
                    "total_count": total,
                    "share": unspecified / total,
                }
            )
    return pd.DataFrame(rows)


def quality_issues(frame: pd.DataFrame, masks: dict[str, pd.Series]) -> pd.DataFrame:
    descriptions = {
        "missing_birth_type": "Código de tipo de parto vacío en la fuente",
        "undocumented_sex_code": "Código de sexo 3 ausente del diccionario DEIS provisto",
        "implausible_gestation_weight": "Gestación menor de 22 semanas con peso de 2500 g o más",
    }
    handling = {
        "missing_birth_type": "Conservar; excluir sólo del análisis por tipo de parto",
        "undocumented_sex_code": "Conservar separado; agrupar con no especificado sólo al conciliar el anuario 2024",
        "implausible_gestation_weight": "Conservar; excluir del análisis conjunto gestación-peso o mostrar sensibilidad",
    }
    rows: list[dict[str, object]] = []
    for issue, mask in masks.items():
        affected = frame.loc[mask]
        for year, yearly in affected.groupby("year", sort=True):
            rows.append(
                {
                    "issue": issue,
                    "description": descriptions[issue],
                    "year": int(year),
                    "source_rows": int(len(yearly)),
                    "registered_births": int(yearly["count"].sum()),
                    "handling": handling[issue],
                }
            )
    return pd.DataFrame(rows)


def official_2024_reconciliation(frame: pd.DataFrame) -> pd.DataFrame:
    year = frame.loc[frame["year"].eq(2024)].copy()
    observed: list[dict[str, object]] = [
        {"dimension": "total", "category_key": "all", "observed_count": int(year["count"].sum())}
    ]
    groupings = {
        "mother_age": "mother_age_code",
        "education_source": "education_source_code",
        "weight_source": "weight_source_code",
        "gestation": "gestation_code",
        "birth_type": "birth_type_code",
    }
    for dimension, column in groupings.items():
        totals = year.groupby(column, dropna=False)["count"].sum()
        for key, value in totals.items():
            observed.append(
                {
                    "dimension": dimension,
                    "category_key": str(int(key)) if pd.notna(key) else "missing",
                    "observed_count": int(value),
                }
            )
    sex_key = year["sex_code"].astype(str).where(year["sex_code"].isin([1, 2]), "unspecified")
    for key, value in year.assign(_key=sex_key).groupby("_key")["count"].sum().items():
        observed.append(
            {"dimension": "sex_published", "category_key": key, "observed_count": int(value)}
        )

    controls = pd.read_csv(CONTROLS, dtype={"category_key": str})
    result = controls.merge(
        pd.DataFrame(observed),
        on=["dimension", "category_key"],
        how="outer",
        validate="one_to_one",
        indicator=True,
    )
    require(result["_merge"].eq("both").all(), "Official control categories do not align")
    result["difference"] = result["observed_count"] - result["expected_count"]
    result["passed"] = result["difference"].eq(0)
    require(result["passed"].all(), "2024 values do not match the official annual report")
    return result.drop(columns="_merge")


def plausibility_checks_2024(frame: pd.DataFrame) -> pd.DataFrame:
    year = frame.loc[frame["year"].eq(2024)]
    checks = [
        (
            "gestation_lt22_weight_ge2500",
            year["gestation_code"].eq(1) & year["weight_source_code"].isin([6, 7, 8]),
            1,
            "Se conserva con bandera de calidad",
        ),
        (
            "gestation_lt22_weight_ge3500",
            year["gestation_code"].eq(1) & year["weight_source_code"].eq(8),
            0,
            "Sin casos",
        ),
        (
            "gestation_22_23_weight_ge2500",
            year["gestation_code"].eq(2) & year["weight_source_code"].isin([6, 7, 8]),
            0,
            "Sin casos",
        ),
        (
            "gestation_24_27_weight_ge3500",
            year["gestation_code"].eq(3) & year["weight_source_code"].eq(8),
            0,
            "Sin casos",
        ),
        (
            "gestation_42plus_weight_lt500",
            year["gestation_code"].eq(7) & year["weight_source_code"].eq(1),
            0,
            "Sin casos",
        ),
        (
            "mother_under15_tertiary_education",
            year["mother_age_code"].eq(1) & year["education_source_code"].isin([6, 7]),
            0,
            "Sin casos",
        ),
    ]
    rows = []
    for name, mask, expected_rows, handling in checks:
        actual_rows = int(mask.sum())
        rows.append(
            {
                "check": name,
                "source_rows": actual_rows,
                "registered_births": int(year.loc[mask, "count"].sum()),
                "expected_rows": expected_rows,
                "handling": handling,
                "passed": actual_rows == expected_rows,
            }
        )
    result = pd.DataFrame(rows)
    require(result["passed"].all(), "Unexpected result in 2024 plausibility screening")
    return result


def write_report(
    source_reconciliation: pd.DataFrame,
    issues: pd.DataFrame,
    official: pd.DataFrame,
    missingness: pd.DataFrame,
    plausibility: pd.DataFrame,
) -> None:
    issue_lines = [
        "| Hallazgo | Año | Filas | Nacimientos | Tratamiento |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in issues.itertuples(index=False):
        issue_lines.append(
            f"| {row.description} | {row.year} | {format_int_es(row.source_rows)} | "
            f"{format_int_es(row.registered_births)} | {row.handling} |"
        )
    birth_type_2019 = missingness.query(
        "year == 2019 and variable == 'birth_type'"
    ).iloc[0]
    sex_2017 = missingness.query("year == 2017 and variable == 'sex_unspecified'").iloc[0]
    sex_2018 = missingness.query("year == 2018 and variable == 'sex_unspecified'").iloc[0]
    plausibility_births = int(
        plausibility.loc[
            plausibility["check"].eq("gestation_lt22_weight_ge2500"),
            "registered_births",
        ].iloc[0]
    )
    content = f"""# Validación de la capa normalizada

## Resultado

La capa Parquet conserva las {format_int_es(source_reconciliation['source_rows'].sum())} filas
agregadas y los {format_int_es(source_reconciliation['source_total'].sum())} nacimientos
registrados de los once CSV originales. Las diferencias por año son cero. Los
{len(official)} controles extraídos del Anuario DEIS 2024 también tienen diferencia
cero. Una segunda lectura de los archivos crudos reproduce fila por fila todos
los códigos, etiquetas fuente, frecuencias y armonizaciones del Parquet.

No se detectaron conteos nulos o negativos, combinaciones dimensionales duplicadas,
códigos fuera de los dominios admitidos, etiquetas incompatibles con sus códigos,
caracteres de control ni indicios de texto mal decodificado. El Parquet tiene un
esquema tipado y metadatos de procedencia.

El detalle adicional de peso publicado en 2024 permitió seis controles de
plausibilidad predefinidos. Cinco no tienen casos. El restante recupera el único
registro ya señalado de menos de 22 semanas y 2.500 g o más
({plausibility_births} nacimiento). Estas reglas son un tamiz conservador, no una certificación clínica
de cada registro.

## Hallazgos preservados y señalados

{chr(10).join(issue_lines)}

Estas observaciones no se borraron ni se imputaron. Los 48 nacimientos con una
combinación gestación-peso físicamente muy improbable permanecen en totales por
año, territorio y edad. No deben utilizarse sin advertencia en un análisis conjunto
de gestación y peso.

El código de sexo `3` no aparece en el diccionario entregado por DEIS. En 2024,
sus 6 nacimientos más los 29 con código `9` reproducen exactamente los 35 casos
publicados como “sin especificar” en la tabla 13. Esta conciliación es evidencia
para agruparlos al reproducir esa tabla, pero **no define el significado propio del
código 3**; por eso se conserva por separado.

## Faltantes y comparabilidad

Los valores no especificados se reportan en `missingness_by_year.csv`; no se tratan
como registros inválidos. Hay saltos que pueden afectar comparaciones: el tipo de
parto no especificado llega a {format_int_es(birth_type_2019.unspecified_count)} casos
({birth_type_2019.share:.2%}) en 2019, y el sexo no especificado a
{format_int_es(sex_2017.unspecified_count)} ({sex_2017.share:.2%}) en 2017 y
{format_int_es(sex_2018.unspecified_count)} ({sex_2018.share:.2%}) en 2018.

Educación y peso cambiaron de categorización en 2024. La capa mantiene las
categorías originales y añade versiones armonizadas hacia el esquema histórico;
nunca reemplaza los códigos fuente.

## Alcance del control externo

La conciliación 2024 usa las tablas 1, 2, 3, 5, 7 y 13 del
[Anuario de Estadísticas Vitales 2024](https://www.argentina.gob.ar/sites/default/files/serie_5_nro_68_anuario_vitales_v4_revisada_ok.pdf).
El propio anuario advierte demoras o dificultades provinciales en el procesamiento
y envío de información, y un cambio de proyecciones poblacionales basado en el
Censo 2022. Esas advertencias se mantendrán al interpretar cobertura o tasas.

## Regla de uso

- `count` es una frecuencia de nacimientos registrados, no una fila individual.
- El registro sin tipo de parto se excluye sólo de análisis por tipo de parto.
- El código de sexo 3 se mantiene separado salvo conciliación explícita con la
  categoría publicada “sin especificar”.
- Las combinaciones gestación-peso señaladas se excluyen del cruce entre ambas
  variables o se incluyen únicamente con un análisis de sensibilidad.
- Ningún hallazgo autoriza por sí solo una interpretación causal.
"""
    REPORT.write_text(content, encoding="utf-8")


def main() -> None:
    require(PARQUET.exists(), f"Missing normalized dataset: {PARQUET}")
    parquet_file = pq.ParquetFile(PARQUET)
    validate_schema(parquet_file.schema_arrow)
    frame = parquet_file.read().to_pandas()

    require(
        not frame.duplicated(["source_file", "source_row"]).any(),
        "Duplicate source-row identities",
    )
    require(
        not frame.duplicated(DIMENSION_COLUMNS).any(),
        "Duplicate source-dimensional combinations",
    )
    validate_domains(frame)
    validate_source_identity(frame)
    validate_label_relationships(frame)
    validate_against_raw(frame)
    validate_text(frame)
    masks = validate_flags(frame)

    source_reconciliation = reconcile_sources(frame, masks)
    missingness = missingness_table(frame)
    issues = quality_issues(frame, masks)
    official = official_2024_reconciliation(frame)
    plausibility = plausibility_checks_2024(frame)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    source_reconciliation.to_csv(OUTPUT_DIR / "normalization_audit.csv", index=False)
    missingness.to_csv(OUTPUT_DIR / "missingness_by_year.csv", index=False, float_format="%.10f")
    issues.to_csv(OUTPUT_DIR / "data_quality_issues.csv", index=False)
    official.to_csv(OUTPUT_DIR / "official_2024_reconciliation.csv", index=False)
    plausibility.to_csv(OUTPUT_DIR / "plausibility_checks_2024.csv", index=False)
    write_report(source_reconciliation, issues, official, missingness, plausibility)

    print(
        f"OK: {len(frame):,} rows and {int(frame['count'].sum()):,} registered births validated."
    )
    print(f"OK: {len(official)} official 2024 controls matched exactly.")
    print(REPORT.relative_to(ROOT))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Normalize the 2014–2024 DEIS registered-live-birth extracts.

The output preserves every source row and its weighted count. Source categories
are never overwritten: harmonized education and weight fields are added beside
the original values, and questionable records receive explicit quality flags.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
MAPPING_DIR = ROOT / "data" / "mappings"
OUTPUT = ROOT / "data" / "interim" / "nacidos_vivos_2014_2024.parquet"
SOURCE_URL = "https://www.argentina.gob.ar/salud/deis/datos/nacidosvivos"

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

AGE_LABELS = {
    1: "Menor de 15",
    2: "15 a 19",
    3: "20 a 24",
    4: "25 a 29",
    5: "30 a 34",
    6: "35 a 39",
    7: "40 a 44",
    8: "De 45 y más",
    9: "Sin especificar",
}
GESTATION_LABELS = {
    1: "Menos de 22",
    2: "22 a 23",
    3: "24 a 27",
    4: "28 a 31",
    5: "32 a 36",
    6: "37 a 41",
    7: "42 y más",
    8: "Sin especificar",
}

SCHEMA = pa.schema(
    [
        pa.field("year", pa.int16(), nullable=False),
        pa.field("source_file", pa.string(), nullable=False),
        pa.field("source_row", pa.int32(), nullable=False),
        pa.field("province_code", pa.string(), nullable=False),
        pa.field("province_label", pa.string(), nullable=False),
        pa.field("residence_scope", pa.string(), nullable=False),
        pa.field("birth_type_code", pa.int8(), nullable=True),
        pa.field("birth_type_label", pa.string(), nullable=True),
        pa.field("sex_code", pa.int8(), nullable=False),
        pa.field("sex_label", pa.string(), nullable=False),
        pa.field("mother_age_code", pa.int8(), nullable=False),
        pa.field("mother_age_label", pa.string(), nullable=False),
        pa.field("gestation_code", pa.int8(), nullable=False),
        pa.field("gestation_label", pa.string(), nullable=False),
        pa.field("education_source_code", pa.int8(), nullable=False),
        pa.field("education_source_label", pa.string(), nullable=False),
        pa.field("education_harmonized_code", pa.int8(), nullable=False),
        pa.field("education_harmonized_label", pa.string(), nullable=False),
        pa.field("weight_source_code", pa.int8(), nullable=False),
        pa.field("weight_source_label", pa.string(), nullable=False),
        pa.field("weight_harmonized_code", pa.int8(), nullable=False),
        pa.field("weight_harmonized_label", pa.string(), nullable=False),
        pa.field("count", pa.int64(), nullable=False),
        pa.field("flag_missing_birth_type", pa.bool_(), nullable=False),
        pa.field("flag_undocumented_sex", pa.bool_(), nullable=False),
        pa.field("flag_implausible_gestation_weight", pa.bool_(), nullable=False),
        pa.field("quality_flags", pa.string(), nullable=True),
    ],
    metadata={
        b"pipeline_version": b"1.0.0",
        b"source_url": SOURCE_URL.encode(),
        b"row_grain": (
            b"Aggregated source cell; count is the number of registered live births"
        ),
        b"coverage": b"Argentina, registration years 2014-2024",
    },
)


def detect_format(path: Path) -> tuple[str, str]:
    sample_bytes = path.read_bytes()[:65536]
    encoding = "utf-8-sig" if sample_bytes.startswith(b"\xef\xbb\xbf") else "cp1252"
    sample = sample_bytes.decode(encoding)
    delimiter = csv.Sniffer().sniff(sample, delimiters=",;").delimiter
    return encoding, delimiter


def read_source(year: int) -> pd.DataFrame:
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
    frame.insert(0, "source_row", range(2, len(frame) + 2))
    frame.insert(0, "source_file", path.name)
    frame.insert(0, "year", year)
    return frame


def dictionary_map(sheet: str, *, pad: int | None = None) -> dict[str, str]:
    frame = pd.read_excel(
        RAW_DIR / "nacidos_vivos_diccionario.xlsx", sheet_name=sheet, dtype=str
    )
    codes = frame["CODIGO"].str.strip()
    if pad is not None:
        codes = codes.str.zfill(pad)
    return dict(zip(codes, frame["VALOR"].str.strip(), strict=True))


def split_coded_label(series: pd.Series, field: str) -> tuple[pd.Series, pd.Series]:
    parts = series.str.split(".", n=1, expand=True)
    if parts.shape[1] != 2 or parts.isna().any(axis=None):
        raise ValueError(f"Malformed coded labels in {field}")
    codes = pd.to_numeric(parts[0], errors="raise").astype("int8")
    labels = parts[1].str.strip()
    return codes, labels


def validate_fixed_labels(
    codes: pd.Series, labels: pd.Series, expected: dict[int, str], field: str
) -> None:
    observed = set(zip(codes.astype(int), labels, strict=True))
    expected_pairs = set(expected.items())
    if observed != expected_pairs:
        raise ValueError(
            f"Unexpected {field} code/label pairs: "
            f"observed={sorted(observed)!r}, expected={sorted(expected_pairs)!r}"
        )


def apply_harmonization(
    frame: pd.DataFrame,
    *,
    year: int,
    source_code: pd.Series,
    source_label: pd.Series,
    mapping_filename: str,
    field: str,
) -> tuple[pd.Series, pd.Series]:
    mapping = pd.read_csv(MAPPING_DIR / mapping_filename)
    mapping = mapping[
        mapping["source_year_start"].le(year)
        & mapping["source_year_end"].ge(year)
    ].copy()
    mapping["source_code"] = mapping["source_code"].astype("int8")
    source_pairs = set(zip(source_code.astype(int), source_label, strict=True))
    expected_pairs = set(
        zip(
            mapping["source_code"].astype(int),
            mapping["source_label_expected"],
            strict=True,
        )
    )
    if source_pairs != expected_pairs:
        raise ValueError(
            f"{field} labels do not match the versioned mapping for {year}: "
            f"observed={sorted(source_pairs)!r}, expected={sorted(expected_pairs)!r}"
        )
    lookup = mapping.set_index("source_code")
    harmonized_code = source_code.map(lookup["harmonized_code"]).astype("int8")
    harmonized_label = source_code.map(lookup["harmonized_label"]).astype("string")
    if harmonized_code.isna().any() or harmonized_label.isna().any():
        raise ValueError(f"Incomplete {field} harmonization for {year}")
    return harmonized_code, harmonized_label


def normalize_year(
    year: int,
    province_labels: dict[str, str],
    birth_type_labels: dict[str, str],
    sex_labels: dict[str, str],
) -> pd.DataFrame:
    raw = read_source(year)
    count = pd.to_numeric(raw["CUENTA"], errors="raise")
    if not count.gt(0).all() or not count.mod(1).eq(0).all():
        raise ValueError(f"CUENTA must contain positive integers in {year}")

    province_label = raw["PROVRES"].map(province_labels)
    if province_label.isna().any():
        raise ValueError(f"Unknown province code in {year}")

    birth_type_numeric = pd.to_numeric(
        raw["TIPPARTO"].replace("", pd.NA), errors="raise"
    ).astype("Int8")
    birth_type_label = raw["TIPPARTO"].map(birth_type_labels).astype("string")

    sex_code = pd.to_numeric(raw["SEXO"], errors="raise").astype("int8")
    sex_label = raw["SEXO"].map(sex_labels).astype("string")
    undocumented_sex = ~raw["SEXO"].isin(sex_labels)
    sex_label = sex_label.mask(undocumented_sex, "Código 3 no documentado")

    age_code, age_label = split_coded_label(raw["IMEDAD"], "IMEDAD")
    validate_fixed_labels(age_code, age_label, AGE_LABELS, "IMEDAD")
    gestation_code, gestation_label = split_coded_label(raw["ITIEMGEST"], "ITIEMGEST")
    validate_fixed_labels(gestation_code, gestation_label, GESTATION_LABELS, "ITIEMGEST")

    education_code, education_label = split_coded_label(raw["IMINSTRUC"], "IMINSTRUC")
    education_h_code, education_h_label = apply_harmonization(
        raw,
        year=year,
        source_code=education_code,
        source_label=education_label,
        mapping_filename="education_harmonization.csv",
        field="education",
    )
    weight_code, weight_label = split_coded_label(raw["IPESONAC"], "IPESONAC")
    weight_h_code, weight_h_label = apply_harmonization(
        raw,
        year=year,
        source_code=weight_code,
        source_label=weight_label,
        mapping_filename="weight_harmonization.csv",
        field="weight",
    )

    missing_birth_type = raw["TIPPARTO"].eq("")
    implausible_combo = gestation_code.eq(1) & weight_h_code.eq(2)
    flags = pd.Series(pd.NA, index=raw.index, dtype="string")
    flag_names = (
        (missing_birth_type, "missing_birth_type"),
        (undocumented_sex, "undocumented_sex_code"),
        (implausible_combo, "implausible_gestation_weight"),
    )
    for mask, name in flag_names:
        flags = flags.mask(mask & flags.isna(), name)
        flags = flags.mask(mask & flags.notna() & ~flags.str.contains(name, na=False), flags + "|" + name)

    residence_scope = pd.Series("argentina_province", index=raw.index, dtype="string")
    residence_scope = residence_scope.mask(raw["PROVRES"].eq("98"), "other_country")
    residence_scope = residence_scope.mask(raw["PROVRES"].eq("99"), "unspecified")

    return pd.DataFrame(
        {
            "year": pd.Series(year, index=raw.index, dtype="int16"),
            "source_file": raw["source_file"].astype("string"),
            "source_row": raw["source_row"].astype("int32"),
            "province_code": raw["PROVRES"].astype("string"),
            "province_label": province_label.astype("string"),
            "residence_scope": residence_scope,
            "birth_type_code": birth_type_numeric,
            "birth_type_label": birth_type_label,
            "sex_code": sex_code,
            "sex_label": sex_label,
            "mother_age_code": age_code,
            "mother_age_label": age_label.astype("string"),
            "gestation_code": gestation_code,
            "gestation_label": gestation_label.astype("string"),
            "education_source_code": education_code,
            "education_source_label": education_label.astype("string"),
            "education_harmonized_code": education_h_code,
            "education_harmonized_label": education_h_label,
            "weight_source_code": weight_code,
            "weight_source_label": weight_label.astype("string"),
            "weight_harmonized_code": weight_h_code,
            "weight_harmonized_label": weight_h_label,
            "count": count.astype("int64"),
            "flag_missing_birth_type": missing_birth_type.astype("bool"),
            "flag_undocumented_sex": undocumented_sex.astype("bool"),
            "flag_implausible_gestation_weight": implausible_combo.astype("bool"),
            "quality_flags": flags,
        }
    )


def main() -> None:
    province_labels = dictionary_map("PROVRES", pad=2)
    birth_type_labels = dictionary_map("TIPPARTO")
    sex_labels = dictionary_map("SEXO")
    frames = [
        normalize_year(year, province_labels, birth_type_labels, sex_labels)
        for year in range(2014, 2025)
    ]
    normalized = pd.concat(frames, ignore_index=True).sort_values(
        ["year", "source_row"], kind="stable"
    )
    table = pa.Table.from_pandas(normalized, schema=SCHEMA, preserve_index=False, safe=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        table,
        OUTPUT,
        compression="zstd",
        compression_level=9,
        use_dictionary=True,
        write_statistics=True,
    )
    print(
        f"OK: {table.num_rows:,} aggregate rows, "
        f"{normalized['count'].sum():,} registered births."
    )
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()

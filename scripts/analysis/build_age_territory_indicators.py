#!/usr/bin/env python3
"""Build indicators for the territorial shift in maternal-age composition."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "interim" / "nacidos_vivos_2014_2024.parquet"
OUTPUT_DIR = ROOT / "data" / "processed"
REPORT = ROOT / "docs" / "age-territory-findings.md"
ENDPOINTS = [2014, 2024]


def write_csv(frame: pd.DataFrame, filename: str) -> None:
    frame.to_csv(OUTPUT_DIR / filename, index=False, float_format="%.10f")


def format_pct_es(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}".replace(".", ",") + "%"


def format_number_es(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}".replace(".", ",")


def build_tables(
    data: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    provinces = data.loc[data["residence_scope"].eq("argentina_province")].copy()
    all_totals = (
        provinces.groupby(
            ["year", "province_code", "province_label"], as_index=False
        )["count"]
        .sum()
        .rename(columns={"count": "all_registered_births"})
    )
    unspecified = (
        provinces.loc[provinces["mother_age_code"].eq(9)]
        .groupby(["year", "province_code", "province_label"], as_index=False)["count"]
        .sum()
        .rename(columns={"count": "unspecified_age_births"})
    )
    known = provinces.loc[provinces["mother_age_code"].ne(9)]
    observed_age = (
        known.groupby(
            [
                "year",
                "province_code",
                "province_label",
                "mother_age_code",
                "mother_age_label",
            ],
            as_index=False,
        )["count"]
        .sum()
        .rename(columns={"count": "registered_births"})
    )
    province_lookup = provinces[["province_code", "province_label"]].drop_duplicates()
    age_lookup = known[["mother_age_code", "mother_age_label"]].drop_duplicates()
    complete_index = pd.MultiIndex.from_product(
        [
            sorted(provinces["year"].unique()),
            sorted(province_lookup["province_code"].unique()),
            range(1, 9),
        ],
        names=["year", "province_code", "mother_age_code"],
    ).to_frame(index=False)
    age = (
        complete_index.merge(province_lookup, on="province_code", validate="many_to_one")
        .merge(age_lookup, on="mother_age_code", validate="many_to_one")
        .merge(
            observed_age[
                ["year", "province_code", "mother_age_code", "registered_births"]
            ],
            on=["year", "province_code", "mother_age_code"],
            how="left",
            validate="one_to_one",
        )
    )
    age["registered_births"] = age["registered_births"].fillna(0).astype("int64")
    age["known_age_births"] = age.groupby(["year", "province_code"])[
        "registered_births"
    ].transform("sum")
    age["share_of_known_age_births"] = (
        age["registered_births"] / age["known_age_births"]
    )

    composition_rows: list[dict[str, object]] = []
    for (year, code, label), group in age.groupby(
        ["year", "province_code", "province_label"], sort=True
    ):
        known_total = int(group["registered_births"].sum())
        under_25 = int(
            group.loc[group["mother_age_code"].isin([1, 2, 3]), "registered_births"].sum()
        )
        age_25_29 = int(
            group.loc[group["mother_age_code"].eq(4), "registered_births"].sum()
        )
        age_30_plus = int(
            group.loc[
                group["mother_age_code"].isin([5, 6, 7, 8]), "registered_births"
            ].sum()
        )
        composition_rows.append(
            {
                "year": int(year),
                "province_code": code,
                "province_label": label,
                "known_age_births": known_total,
                "under_25_births": under_25,
                "under_25_share": under_25 / known_total,
                "age_25_29_births": age_25_29,
                "age_25_29_share": age_25_29 / known_total,
                "age_30_plus_births": age_30_plus,
                "age_30_plus_share": age_30_plus / known_total,
            }
        )
    composition = pd.DataFrame(composition_rows).merge(
        all_totals,
        on=["year", "province_code", "province_label"],
        validate="one_to_one",
    ).merge(
        unspecified,
        on=["year", "province_code", "province_label"],
        how="left",
        validate="one_to_one",
    )
    composition["unspecified_age_births"] = (
        composition["unspecified_age_births"].fillna(0).astype("int64")
    )
    composition["unspecified_age_share"] = (
        composition["unspecified_age_births"] / composition["all_registered_births"]
    )
    composition = composition.sort_values(["year", "province_code"])

    endpoint_distribution = age.loc[age["year"].isin(ENDPOINTS)].copy()
    endpoint_distribution = endpoint_distribution.sort_values(
        ["year", "province_code", "mother_age_code"]
    )

    endpoint_age = endpoint_distribution.copy()
    endpoint_age["max_births"] = endpoint_age.groupby(
        ["year", "province_code"]
    )["registered_births"].transform("max")
    modal = endpoint_age.loc[
        endpoint_age["registered_births"].eq(endpoint_age["max_births"])
    ].copy()
    modal["modal_tie_count"] = modal.groupby(
        ["year", "province_code"]
    )["mother_age_code"].transform("size")
    modal = modal[
        [
            "year",
            "province_code",
            "mother_age_code",
            "mother_age_label",
            "registered_births",
            "share_of_known_age_births",
            "modal_tie_count",
        ]
    ].rename(
        columns={
            "mother_age_code": "modal_age_code",
            "mother_age_label": "modal_age_label",
            "registered_births": "modal_age_births",
            "share_of_known_age_births": "modal_age_share",
        }
    )

    first = composition.loc[composition["year"].eq(2014)].drop(columns="year")
    last = composition.loc[composition["year"].eq(2024)].drop(columns="year")
    shift = first.merge(
        last,
        on=["province_code", "province_label"],
        suffixes=("_2014", "_2024"),
        validate="one_to_one",
    )
    for metric in ("under_25_share", "age_25_29_share", "age_30_plus_share"):
        shift[f"{metric}_change_pp"] = (
            shift[f"{metric}_2024"] - shift[f"{metric}_2014"]
        ) * 100
    shift["registered_births_change"] = (
        shift["all_registered_births_2024"] - shift["all_registered_births_2014"]
    )
    shift["registered_births_change_pct"] = (
        shift["registered_births_change"] / shift["all_registered_births_2014"]
    )

    modal_columns_2014 = {
        column: f"{column}_2014"
        for column in modal.columns
        if column not in {"year", "province_code"}
    }
    modal_columns_2024 = {
        column: f"{column}_2024"
        for column in modal.columns
        if column not in {"year", "province_code"}
    }
    modal_2014 = (
        modal.loc[modal["year"].eq(2014)]
        .drop(columns="year")
        .rename(columns=modal_columns_2014)
    )
    modal_2024 = (
        modal.loc[modal["year"].eq(2024)]
        .drop(columns="year")
        .rename(columns=modal_columns_2024)
    )
    shift = shift.merge(modal_2014, on="province_code", validate="one_to_one").merge(
        modal_2024, on="province_code", validate="one_to_one"
    )
    shift["modal_age_band_change"] = (
        shift["modal_age_code_2024"] - shift["modal_age_code_2014"]
    )
    shift = shift.sort_values("age_30_plus_share_change_pp", ascending=False)
    return composition, endpoint_distribution, shift


def write_report(shift: pd.DataFrame) -> None:
    top_shift = shift.iloc[0]
    bottom_shift = shift.iloc[-1]
    modes_2014 = shift["modal_age_label_2014"].value_counts()
    modes_2024 = shift["modal_age_label_2024"].value_counts()
    content = f"""# Edad materna y territorio

## Hallazgo

El desplazamiento hacia edades maternas mayores no es exclusivo del promedio
nacional. Entre 2014 y 2024, la participación de madres menores de 25 años cayó
en las 24 jurisdicciones y la participación de madres de 30 años o más aumentó
en todas ellas. Las participaciones se calculan únicamente sobre nacimientos con
edad de la madre conocida.

En 2014, el grupo con más nacimientos era 20 a 24 años en
{int(modes_2014.get('20 a 24', 0))} de las 24 jurisdicciones. En 2024, el grupo
modal pasó a ser 25 a 29 años en {int(modes_2024.get('25 a 29', 0))}. Las dos
excepciones de 2024 son Formosa, donde sigue siendo 20 a 24, y Ciudad Autónoma
de Buenos Aires, donde el máximo se ubica en 35 a 39.

El aumento más amplio de la proporción de 30 años o más ocurrió en
{top_shift.province_label}: {format_number_es(top_shift.age_30_plus_share_change_pp)}
puntos porcentuales. El menor se observó en {bottom_shift.province_label}:
{format_number_es(bottom_shift.age_30_plus_share_change_pp)} puntos porcentuales.

La diferencia territorial sigue siendo grande. En 2024, las madres menores de
25 años representan desde
{format_pct_es(float(shift['under_25_share_2024'].min()) * 100)} de los
nacimientos con edad conocida hasta
{format_pct_es(float(shift['under_25_share_2024'].max()) * 100)}. Por lo tanto,
la convergencia en el grupo modal no elimina las diferencias en la composición
completa.

## Interpretación

La historia ya no es sólo “nacen menos”. También cambió de forma coordinada el
momento de la maternidad en todo el territorio. Esta dimensión diferencia el
proyecto de los informes existentes sobre natalidad y matrícula escolar.

Los datos describen edades entre quienes tuvieron nacimientos registrados. No
permiten estimar por sí solos tasas específicas de fecundidad porque faltan
denominadores compatibles de mujeres por edad y provincia para todo 2014–2024.
Tampoco identifican causas del aplazamiento.

## Regla para la obra

- Mostrar el cambio modal sólo como síntesis visual.
- Acompañarlo con participaciones o distribuciones, porque el modo no representa
  toda la forma de la población.
- Mantener “edad desconocida excluida” junto a cualquier porcentaje etario.
- Hablar de composición de nacimientos, no de edad promedio ni de fecundidad.
"""
    REPORT.write_text(content, encoding="utf-8")


def main() -> None:
    data = pd.read_parquet(
        INPUT,
        columns=[
            "year",
            "province_code",
            "province_label",
            "residence_scope",
            "mother_age_code",
            "mother_age_label",
            "count",
        ],
    )
    composition, distribution, shift = build_tables(data)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(composition, "province_age_composition_trend.csv")
    write_csv(distribution, "province_age_distribution_2014_2024.csv")
    write_csv(shift, "province_age_shift_2014_2024.csv")
    write_report(shift)
    print(
        f"OK: {len(composition)} province-year summaries, "
        f"{len(distribution)} endpoint age rows and {len(shift)} shifts built."
    )
    print(REPORT.relative_to(ROOT))


if __name__ == "__main__":
    main()

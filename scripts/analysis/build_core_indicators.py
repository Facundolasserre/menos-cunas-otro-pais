#!/usr/bin/env python3
"""Build the first descriptive indicators for the visual story."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "interim" / "nacidos_vivos_2014_2024.parquet"
OUTPUT_DIR = ROOT / "data" / "processed"
REPORT = ROOT / "docs" / "exploratory-findings.md"
FIRST_YEAR = 2014
LAST_YEAR = 2024


def write_csv(frame: pd.DataFrame, filename: str) -> None:
    frame.to_csv(OUTPUT_DIR / filename, index=False, float_format="%.10f")


def format_int_es(value: object) -> str:
    return f"{int(value):,}".replace(",", ".")


def format_pct_es(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}".replace(".", ",") + "%"


def national_trend(data: pd.DataFrame) -> pd.DataFrame:
    result = (
        data.groupby("year", as_index=False)["count"]
        .sum()
        .rename(columns={"count": "registered_births"})
        .sort_values("year")
    )
    result["annual_change"] = result["registered_births"].diff().astype("Int64")
    result["annual_change_pct"] = result["registered_births"].pct_change()
    baseline = int(result.loc[result["year"].eq(FIRST_YEAR), "registered_births"].iloc[0])
    result["index_2014"] = result["registered_births"] / baseline * 100
    result["change_since_2014"] = result["registered_births"] - baseline
    result["change_since_2014_pct"] = result["registered_births"] / baseline - 1
    return result


def age_tables(
    data: pd.DataFrame, national: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    trend = (
        data.groupby(
            ["year", "mother_age_code", "mother_age_label"], as_index=False
        )["count"]
        .sum()
        .rename(columns={"count": "registered_births"})
        .sort_values(["year", "mother_age_code"])
    )
    national_totals = national.set_index("year")["registered_births"]
    known_totals = (
        trend.loc[trend["mother_age_code"].ne(9)]
        .groupby("year")["registered_births"]
        .sum()
    )
    trend["share_of_all_births"] = (
        trend["registered_births"] / trend["year"].map(national_totals)
    )
    trend["share_of_known_age_births"] = pd.NA
    known_mask = trend["mother_age_code"].ne(9)
    trend.loc[known_mask, "share_of_known_age_births"] = (
        trend.loc[known_mask, "registered_births"]
        / trend.loc[known_mask, "year"].map(known_totals)
    )
    trend["share_of_known_age_births"] = pd.to_numeric(
        trend["share_of_known_age_births"]
    )

    first = trend.loc[trend["year"].eq(FIRST_YEAR)].drop(columns="year")
    last = trend.loc[trend["year"].eq(LAST_YEAR)].drop(columns="year")
    change = first.merge(
        last,
        on=["mother_age_code", "mother_age_label"],
        suffixes=("_2014", "_2024"),
        validate="one_to_one",
    )
    change["absolute_change"] = (
        change["registered_births_2024"] - change["registered_births_2014"]
    )
    change["percent_change"] = (
        change["absolute_change"] / change["registered_births_2014"]
    )
    total_decline = int(national_totals.loc[FIRST_YEAR] - national_totals.loc[LAST_YEAR])
    known_decline = int(known_totals.loc[FIRST_YEAR] - known_totals.loc[LAST_YEAR])
    change["contribution_to_total_decline"] = -change["absolute_change"] / total_decline
    change["contribution_to_known_age_decline"] = pd.NA
    known_change = change["mother_age_code"].ne(9)
    change.loc[known_change, "contribution_to_known_age_decline"] = (
        -change.loc[known_change, "absolute_change"] / known_decline
    )
    change["contribution_to_known_age_decline"] = pd.to_numeric(
        change["contribution_to_known_age_decline"]
    )
    return trend, change


def residence_tables(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    trend = (
        data.groupby(
            ["year", "province_code", "province_label", "residence_scope"],
            as_index=False,
        )["count"]
        .sum()
        .rename(columns={"count": "registered_births"})
        .sort_values(["year", "province_code"])
    )
    totals = trend.groupby("year")["registered_births"].sum()
    trend["share_of_national_births"] = (
        trend["registered_births"] / trend["year"].map(totals)
    )

    provinces = trend.loc[trend["residence_scope"].eq("argentina_province")]
    first = provinces.loc[provinces["year"].eq(FIRST_YEAR)].drop(columns="year")
    last = provinces.loc[provinces["year"].eq(LAST_YEAR)].drop(columns="year")
    change = first.merge(
        last,
        on=["province_code", "province_label", "residence_scope"],
        suffixes=("_2014", "_2024"),
        validate="one_to_one",
    )
    change["absolute_change"] = (
        change["registered_births_2024"] - change["registered_births_2014"]
    )
    change["percent_change"] = (
        change["absolute_change"] / change["registered_births_2014"]
    )
    provincial_decline = int(-change["absolute_change"].sum())
    change["contribution_to_provincial_decline"] = (
        -change["absolute_change"] / provincial_decline
    )
    change["rank_percent_decline"] = (
        change["percent_change"].rank(method="min", ascending=True).astype("int8")
    )
    change["rank_absolute_decline"] = (
        (-change["absolute_change"]).rank(method="min", ascending=False).astype("int8")
    )
    return trend, change.sort_values("rank_percent_decline")


def write_report(
    national: pd.DataFrame,
    age_trend: pd.DataFrame,
    age_change: pd.DataFrame,
    residence_trend: pd.DataFrame,
    province_change: pd.DataFrame,
) -> None:
    national_by_year = national.set_index("year")
    first_total = int(national_by_year.loc[FIRST_YEAR, "registered_births"])
    last_total = int(national_by_year.loc[LAST_YEAR, "registered_births"])
    decline = first_total - last_total
    decline_pct = decline / first_total * 100
    pre_2020_decline = (
        national_by_year.loc[2019, "registered_births"] / first_total - 1
    ) * 100
    post_2020_decline = (
        last_total / national_by_year.loc[2020, "registered_births"] - 1
    ) * 100

    known_age = age_change.loc[age_change["mother_age_code"].ne(9)].copy()
    under_25 = known_age.loc[known_age["mother_age_code"].isin([1, 2, 3])]
    age_decline_known = int(
        known_age["registered_births_2014"].sum()
        - known_age["registered_births_2024"].sum()
    )
    under_25_decline = int(-under_25["absolute_change"].sum())
    under_25_contribution = under_25_decline / age_decline_known * 100

    shares = age_trend.pivot(
        index="mother_age_code", columns="year", values="share_of_known_age_births"
    )
    under_25_share_2014 = float(shares.loc[[1, 2, 3], FIRST_YEAR].sum() * 100)
    under_25_share_2024 = float(shares.loc[[1, 2, 3], LAST_YEAR].sum() * 100)
    age_30_plus_share_2014 = float(shares.loc[[5, 6, 7, 8], FIRST_YEAR].sum() * 100)
    age_30_plus_share_2024 = float(shares.loc[[5, 6, 7, 8], LAST_YEAR].sum() * 100)
    age_45 = age_change.loc[age_change["mother_age_code"].eq(8)].iloc[0]

    most_relative = province_change.iloc[0]
    least_relative = province_change.iloc[-1]
    largest_absolute = province_change.sort_values("rank_absolute_decline").iloc[0]
    non_province = (
        residence_trend.loc[
            residence_trend["residence_scope"].ne("argentina_province")
        ]
        .groupby("year")["registered_births"]
        .sum()
    )
    unknown_age = age_trend.loc[age_trend["mother_age_code"].eq(9)].set_index("year")

    content = f"""# Primer análisis exploratorio

## Hallazgo central

Argentina pasó de {format_int_es(first_total)} nacimientos vivos registrados en
{FIRST_YEAR} a {format_int_es(last_total)} en {LAST_YEAR}. Son
{format_int_es(decline)} menos, una caída de {format_pct_es(decline_pct)}. La
serie ya había descendido {format_pct_es(abs(pre_2020_decline))} entre 2014 y
2019. En 2020 cayó otro {format_pct_es(abs(float(national_by_year.loc[2020, 'annual_change_pct']) * 100))}
interanual y entre 2020 y 2024 descendió {format_pct_es(abs(post_2020_decline))}
adicional. La pandemia coincide con el salto más fuerte, pero no inicia ni
explica por sí sola la tendencia.

## El cambio por edad

Entre las edades conocidas, los grupos menores de 25 años explican
{format_pct_es(under_25_contribution)} de la reducción: registraron
{format_int_es(under_25_decline)} nacimientos menos. Su participación pasó de
{format_pct_es(under_25_share_2014)} a {format_pct_es(under_25_share_2024)}.

En sentido composicional, los nacimientos de madres de 30 años o más pasaron de
{format_pct_es(age_30_plus_share_2014)} a {format_pct_es(age_30_plus_share_2024)}
de los casos con edad conocida. Esto no significa que hayan aumentado en
cantidad: todos los grupos entre 30 y 44 años también descendieron. El único
grupo que creció fue 45 años o más, con {format_int_es(age_45.absolute_change)}
casos adicionales, pero representa sólo
{format_pct_es(float(age_45.share_of_known_age_births_2024) * 100, 2)} de 2024.

El mayor aporte individual a la reducción provino de 20 a 24 años
({format_int_es(-age_change.loc[age_change['mother_age_code'].eq(3), 'absolute_change'].iloc[0])}
casos menos), seguido por 15 a 19 años
({format_int_es(-age_change.loc[age_change['mother_age_code'].eq(2), 'absolute_change'].iloc[0])}
menos).

## El cambio territorial

Las 24 jurisdicciones argentinas registraron menos nacimientos en 2024 que en
2014. La variación va desde {format_pct_es(abs(float(most_relative.percent_change) * 100))}
en {most_relative.province_label} hasta
{format_pct_es(abs(float(least_relative.percent_change) * 100))} en
{least_relative.province_label}. Buenos Aires concentra la mayor reducción
absoluta: {format_int_es(-largest_absolute.absolute_change)} nacimientos menos,
equivalentes al
{format_pct_es(float(largest_absolute.contribution_to_provincial_decline) * 100)}
de la caída entre residencias provinciales.

Estas son variaciones de conteos dentro de cada provincia, no tasas de natalidad.
No controlan cambios de población ni migración y no deben presentarse como una
comparación de “desempeño” provincial.

## Sensibilidad y valores no especificados

- Edad sin especificar: {format_int_es(unknown_age.loc[FIRST_YEAR, 'registered_births'])}
  casos en 2014 ({format_pct_es(float(unknown_age.loc[FIRST_YEAR, 'share_of_all_births']) * 100, 2)})
  y {format_int_es(unknown_age.loc[LAST_YEAR, 'registered_births'])} en 2024
  ({format_pct_es(float(unknown_age.loc[LAST_YEAR, 'share_of_all_births']) * 100, 2)}).
  Por eso el cambio de composición etaria se calcula sobre edades conocidas.
- Otro país o residencia sin especificar: {format_int_es(non_province.loc[FIRST_YEAR])}
  casos en 2014 y {format_int_es(non_province.loc[LAST_YEAR])} en 2024. Se incluyen
  en el total nacional y se excluyen del ranking de provincias.
- Las anomalías de tipo de parto, sexo y gestación-peso no afectan estos tres
  ejes porque ninguna de esas variables interviene en los indicadores.

## Lectura editorial provisional

La evidencia sostiene una tesis descriptiva fuerte: **en una década, los
nacimientos registrados en Argentina cayeron casi a la mitad; la reducción
alcanzó a todas las provincias y estuvo acompañada por un desplazamiento de la
composición hacia edades maternas mayores**.

Todavía no se atribuyen causas ni consecuencias. Para convertir esta descripción
en una historia de alto impacto falta contrastarla con denominadores poblacionales
compatibles y con una consecuencia pública verificable, sin mezclar series de
población construidas con proyecciones incompatibles.
"""
    REPORT.write_text(content, encoding="utf-8")


def main() -> None:
    data = pd.read_parquet(INPUT)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    national = national_trend(data)
    age_trend, age_change = age_tables(data, national)
    residence_trend, province_change = residence_tables(data)

    write_csv(national, "national_trend.csv")
    write_csv(age_trend, "age_trend.csv")
    write_csv(age_change, "age_change_2014_2024.csv")
    write_csv(residence_trend, "residence_trend.csv")
    write_csv(province_change, "province_change_2014_2024.csv")
    write_report(
        national, age_trend, age_change, residence_trend, province_change
    )

    print(
        f"OK: {len(national)} national, {len(age_trend)} age and "
        f"{len(residence_trend)} residence-year rows built."
    )
    print(REPORT.relative_to(ROOT))


if __name__ == "__main__":
    main()

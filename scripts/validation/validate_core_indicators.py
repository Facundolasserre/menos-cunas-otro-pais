#!/usr/bin/env python3
"""Validate the first descriptive indicator tables independently."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed"
SOURCE_AUDIT = DATA / "deis_source_audit.csv"
NORMALIZED = ROOT / "data" / "interim" / "nacidos_vivos_2014_2024.parquet"
FIRST_YEAR = 2014
LAST_YEAR = 2024


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def close(left: pd.Series, right: pd.Series, tolerance: float = 1e-9) -> bool:
    left = left.reset_index(drop=True)
    right = right.reset_index(drop=True)
    if len(left) != len(right) or not left.isna().equals(right.isna()):
        return False
    present = left.notna()
    return bool((left[present].sub(right[present]).abs() <= tolerance).all())


def reconcile_grouped(
    output: pd.DataFrame, source: pd.DataFrame, keys: list[str], label: str
) -> None:
    control = output[keys + ["registered_births"]].merge(
        source,
        on=keys,
        how="outer",
        validate="one_to_one",
        indicator=True,
        suffixes=("_output", "_source"),
    )
    require(control["_merge"].eq("both").all(), f"{label} categories do not align")
    require(
        control["registered_births_output"].eq(
            control["registered_births_source"]
        ).all(),
        f"{label} values differ from the normalized source",
    )


def main() -> None:
    national = pd.read_csv(DATA / "national_trend.csv")
    age = pd.read_csv(DATA / "age_trend.csv")
    age_change = pd.read_csv(DATA / "age_change_2014_2024.csv")
    residence = pd.read_csv(DATA / "residence_trend.csv", dtype={"province_code": str})
    province_change = pd.read_csv(
        DATA / "province_change_2014_2024.csv", dtype={"province_code": str}
    )
    source = pd.read_csv(SOURCE_AUDIT)[["year", "total_nacidos"]]
    normalized = pd.read_parquet(
        NORMALIZED,
        columns=[
            "year", "mother_age_code", "mother_age_label", "province_code",
            "province_label", "residence_scope", "count",
        ],
    )

    require(list(national["year"]) == list(range(2014, 2025)), "National years are incomplete")
    require(len(age) == 99, "Age table must have 9 categories x 11 years")
    require(len(residence) == 286, "Residence table must have 26 categories x 11 years")
    require(len(province_change) == 24, "Province comparison must contain 24 jurisdictions")
    require(len(age_change) == 9, "Age comparison must contain 9 categories")

    source_age = (
        normalized.groupby(
            ["year", "mother_age_code", "mother_age_label"], as_index=False
        )["count"]
        .sum()
        .rename(columns={"count": "registered_births"})
    )
    reconcile_grouped(
        age,
        source_age,
        ["year", "mother_age_code", "mother_age_label"],
        "Age",
    )
    source_residence = (
        normalized.groupby(
            ["year", "province_code", "province_label", "residence_scope"],
            as_index=False,
        )["count"]
        .sum()
        .rename(columns={"count": "registered_births"})
    )
    reconcile_grouped(
        residence,
        source_residence,
        ["year", "province_code", "province_label", "residence_scope"],
        "Residence",
    )

    national_control = national[["year", "registered_births"]].merge(
        source, on="year", validate="one_to_one"
    )
    require(
        national_control["registered_births"].eq(national_control["total_nacidos"]).all(),
        "National totals differ from the audited sources",
    )
    require(
        close(national["annual_change"], national["registered_births"].diff()),
        "National annual changes are incorrect",
    )
    require(
        close(national["annual_change_pct"], national["registered_births"].pct_change()),
        "National annual percentage changes are incorrect",
    )
    baseline = int(
        national.loc[national["year"].eq(FIRST_YEAR), "registered_births"].iloc[0]
    )
    require(
        close(national["index_2014"], national["registered_births"] / baseline * 100),
        "National index is incorrect",
    )
    age_totals = age.groupby("year", as_index=False)["registered_births"].sum()
    residence_totals = residence.groupby("year", as_index=False)["registered_births"].sum()
    require(
        age_totals["registered_births"].equals(national["registered_births"]),
        "Age totals do not reconcile to national totals",
    )
    require(
        residence_totals["registered_births"].equals(national["registered_births"]),
        "Residence totals do not reconcile to national totals",
    )
    require(
        close(age.groupby("year")["share_of_all_births"].sum(), pd.Series(1.0, index=national["year"])),
        "Age shares do not sum to one",
    )
    require(
        close(
            residence.groupby("year")["share_of_national_births"].sum(),
            pd.Series(1.0, index=national["year"]),
        ),
        "Residence shares do not sum to one",
    )

    known_age = age.loc[age["mother_age_code"].ne(9)]
    require(
        close(
            known_age.groupby("year")["share_of_known_age_births"].sum(),
            pd.Series(1.0, index=national["year"]),
        ),
        "Known-age shares do not sum to one",
    )
    require(
        age.loc[age["mother_age_code"].eq(9), "share_of_known_age_births"].isna().all(),
        "Unspecified age must not have a known-age share",
    )
    require(
        age_change["absolute_change"].eq(
            age_change["registered_births_2024"]
            - age_change["registered_births_2014"]
        ).all(),
        "Age absolute changes are incorrect",
    )
    require(
        close(
            age_change["percent_change"],
            age_change["absolute_change"] / age_change["registered_births_2014"],
        ),
        "Age percentage changes are incorrect",
    )

    for prefix in ("registered_births", "share_of_all_births", "share_of_known_age_births"):
        first = age.loc[age["year"].eq(FIRST_YEAR)].set_index("mother_age_code")[prefix]
        last = age.loc[age["year"].eq(LAST_YEAR)].set_index("mother_age_code")[prefix]
        require(
            close(
                age_change[f"{prefix}_2014"],
                age_change["mother_age_code"].map(first),
            ),
            f"Age 2014 mismatch for {prefix}",
        )
        require(
            close(
                age_change[f"{prefix}_2024"],
                age_change["mother_age_code"].map(last),
            ),
            f"Age 2024 mismatch for {prefix}",
        )

    province_rows = residence.loc[residence["residence_scope"].eq("argentina_province")]
    first_province = province_rows.loc[
        province_rows["year"].eq(FIRST_YEAR), ["province_code", "registered_births"]
    ].set_index("province_code")["registered_births"]
    last_province = province_rows.loc[
        province_rows["year"].eq(LAST_YEAR), ["province_code", "registered_births"]
    ].set_index("province_code")["registered_births"]
    require(
        province_change["registered_births_2014"].eq(
            province_change["province_code"].map(first_province)
        ).all(),
        "Province 2014 values do not reconcile",
    )
    require(
        province_change["registered_births_2024"].eq(
            province_change["province_code"].map(last_province)
        ).all(),
        "Province 2024 values do not reconcile",
    )
    require(
        province_change["absolute_change"].eq(
            province_change["registered_births_2024"]
            - province_change["registered_births_2014"]
        ).all(),
        "Province absolute changes are incorrect",
    )
    require(
        close(
            province_change["percent_change"],
            province_change["absolute_change"]
            / province_change["registered_births_2014"],
        ),
        "Province percentage changes are incorrect",
    )

    require(national["registered_births"].gt(0).all(), "National totals must be positive")
    require(province_change["percent_change"].lt(0).all(), "Not all provinces declined")
    require(
        province_change["rank_percent_decline"].nunique() == 24,
        "Relative province ranks are not unique",
    )
    require(
        province_change["rank_absolute_decline"].nunique() == 24,
        "Absolute province ranks are not unique",
    )
    require(
        abs(province_change["contribution_to_provincial_decline"].sum() - 1) < 1e-9,
        "Province contributions do not sum to one",
    )
    require(
        abs(age_change["contribution_to_total_decline"].sum() - 1) < 1e-9,
        "Age contributions do not sum to one",
    )
    require(
        abs(
            age_change.loc[
                age_change["mother_age_code"].ne(9),
                "contribution_to_known_age_decline",
            ].sum()
            - 1
        )
        < 1e-9,
        "Known-age contributions do not sum to one",
    )
    require(
        int(national.loc[national["year"].eq(2014), "registered_births"].iloc[0]) == 777_012
        and int(national.loc[national["year"].eq(2024), "registered_births"].iloc[0]) == 413_135,
        "Headline endpoints changed unexpectedly",
    )

    print("OK: five core indicator tables reconcile with the audited sources.")
    print("OK: all 24 provinces declined between 2014 and 2024.")


if __name__ == "__main__":
    main()

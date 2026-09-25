#!/usr/bin/env python3
"""Validate maternal-age composition indicators by province."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
PARQUET = ROOT / "data" / "interim" / "nacidos_vivos_2014_2024.parquet"


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


def main() -> None:
    composition = pd.read_csv(
        PROCESSED / "province_age_composition_trend.csv",
        dtype={"province_code": str},
    )
    distribution = pd.read_csv(
        PROCESSED / "province_age_distribution_2014_2024.csv",
        dtype={"province_code": str},
    )
    shift = pd.read_csv(
        PROCESSED / "province_age_shift_2014_2024.csv",
        dtype={"province_code": str},
    )
    source = pd.read_parquet(
        PARQUET,
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
    source = source.loc[source["residence_scope"].eq("argentina_province")]

    require(len(composition) == 264, "Expected 24 provinces x 11 years")
    require(len(distribution) == 384, "Expected 24 provinces x 2 years x 8 ages")
    require(len(shift) == 24, "Expected one shift row per province")
    require(
        not composition.duplicated(["year", "province_code"]).any(),
        "Duplicate province-year summaries",
    )
    require(
        not distribution.duplicated(
            ["year", "province_code", "mother_age_code"]
        ).any(),
        "Duplicate endpoint age rows",
    )

    source_distribution = (
        source.loc[
            source["year"].isin([2014, 2024]) & source["mother_age_code"].ne(9)
        ]
        .groupby(
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
        .rename(columns={"count": "source_births"})
    )
    control = distribution.merge(
        source_distribution,
        on=[
            "year", "province_code", "province_label", "mother_age_code",
            "mother_age_label",
        ],
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    require(
        control["_merge"].isin(["both", "left_only"]).all(),
        "Endpoint age categories do not align",
    )
    control["source_births"] = control["source_births"].fillna(0).astype("int64")
    require(
        control["registered_births"].eq(control["source_births"]).all(),
        "Endpoint age counts differ from normalized data",
    )
    require(
        close(
            distribution["share_of_known_age_births"],
            distribution["registered_births"] / distribution["known_age_births"],
        ),
        "Endpoint age shares are incorrect",
    )
    require(
        close(
            distribution.groupby(["year", "province_code"])[
                "share_of_known_age_births"
            ].sum(),
            pd.Series(1.0, index=range(48)),
        ),
        "Endpoint age shares do not sum to one",
    )

    bucket_sum = (
        composition["under_25_births"]
        + composition["age_25_29_births"]
        + composition["age_30_plus_births"]
    )
    require(
        bucket_sum.eq(composition["known_age_births"]).all(),
        "Age buckets do not sum to known-age births",
    )
    require(
        (
            composition["known_age_births"]
            + composition["unspecified_age_births"]
        ).eq(composition["all_registered_births"]).all(),
        "Known and unspecified age do not sum to all births",
    )
    require(
        close(
            composition["under_25_share"]
            + composition["age_25_29_share"]
            + composition["age_30_plus_share"],
            pd.Series(1.0, index=range(len(composition))),
        ),
        "Composition shares do not sum to one",
    )

    for year in (2014, 2024):
        endpoint = composition.loc[composition["year"].eq(year)].set_index(
            "province_code"
        )
        for metric in (
            "known_age_births", "under_25_births", "under_25_share",
            "age_25_29_births", "age_25_29_share", "age_30_plus_births",
            "age_30_plus_share", "all_registered_births",
            "unspecified_age_births", "unspecified_age_share",
        ):
            require(
                close(
                    shift[f"{metric}_{year}"],
                    shift["province_code"].map(endpoint[metric]),
                ),
                f"Shift table differs from composition for {metric}/{year}",
            )

    require(
        shift["under_25_share_change_pp"].lt(0).all(),
        "Under-25 share did not fall everywhere",
    )
    require(
        shift["age_30_plus_share_change_pp"].gt(0).all(),
        "Age-30-plus share did not rise everywhere",
    )
    require(shift["modal_tie_count_2014"].eq(1).all(), "Tied modal age in 2014")
    require(shift["modal_tie_count_2024"].eq(1).all(), "Tied modal age in 2024")
    require(
        shift["modal_age_label_2014"].value_counts().to_dict()
        == {"20 a 24": 22, "25 a 29": 1, "30 a 34": 1},
        "Unexpected 2014 modal-age pattern",
    )
    require(
        shift["modal_age_label_2024"].value_counts().to_dict()
        == {"25 a 29": 22, "20 a 24": 1, "35 a 39": 1},
        "Unexpected 2024 modal-age pattern",
    )
    require(shift["registered_births_change"].lt(0).all(), "Not all provinces declined")

    print("OK: age-territory indicators reconcile with normalized data.")
    print("OK: under-25 share fell and age-30-plus share rose in all 24 jurisdictions.")


if __name__ == "__main__":
    main()

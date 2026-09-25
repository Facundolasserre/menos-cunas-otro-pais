#!/usr/bin/env python3
"""Validate the quantitative claims selected for the visual storyboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
STORYBOARD = ROOT / "design" / "storyboard.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def approx(actual: float, expected: float, tolerance: float = 0.05) -> None:
    require(abs(actual - expected) <= tolerance, f"Expected {expected}, got {actual}")


def main() -> None:
    national = pd.read_csv(PROCESSED / "national_trend.csv").set_index("year")
    age = pd.read_csv(PROCESSED / "age_change_2014_2024.csv")
    province = pd.read_csv(PROCESSED / "province_age_shift_2014_2024.csv")

    total_2014 = int(national.loc[2014, "registered_births"])
    total_2024 = int(national.loc[2024, "registered_births"])
    require(total_2014 == 777_012, "Unexpected 2014 national total")
    require(total_2024 == 413_135, "Unexpected 2024 national total")
    require(total_2024 - total_2014 == -363_877, "Unexpected national change")
    approx((total_2024 / total_2014 - 1) * 100, -46.8)
    approx(
        (national.loc[2019, "registered_births"] / total_2014 - 1) * 100,
        -19.5,
    )
    approx(national.loc[2020, "annual_change_pct"] * 100, -14.7)
    approx(
        (
            national.loc[2024, "registered_births"]
            / national.loc[2020, "registered_births"]
            - 1
        )
        * 100,
        -22.5,
    )

    known = age.loc[age["mother_age_label"].ne("Sin especificar")].copy()
    mode_2014 = known.loc[known["registered_births_2014"].idxmax()]
    mode_2024 = known.loc[known["registered_births_2024"].idxmax()]
    require(mode_2014["mother_age_label"] == "20 a 24", "Unexpected 2014 mode")
    require(mode_2024["mother_age_label"] == "25 a 29", "Unexpected 2024 mode")

    under_25 = known.loc[known["mother_age_code"].isin([1, 2, 3])]
    age_30_plus = known.loc[known["mother_age_code"].isin([5, 6, 7, 8])]
    approx(under_25["share_of_known_age_births_2014"].sum() * 100, 40.3)
    approx(under_25["share_of_known_age_births_2024"].sum() * 100, 30.8)
    approx(age_30_plus["share_of_known_age_births_2014"].sum() * 100, 36.6)
    approx(age_30_plus["share_of_known_age_births_2024"].sum() * 100, 43.6)

    require(len(province) == 24, "Expected 24 jurisdictions")
    require(
        province["under_25_share_change_pp"].lt(0).all(),
        "Under-25 share did not fall in every jurisdiction",
    )
    require(
        province["age_30_plus_share_change_pp"].gt(0).all(),
        "Age-30-plus share did not rise in every jurisdiction",
    )
    top = province.loc[province["age_30_plus_share_change_pp"].idxmax()]
    bottom = province.loc[province["age_30_plus_share_change_pp"].idxmin()]
    require(top["province_label"] == "Tierra del Fuego", "Unexpected largest shift")
    require(bottom["province_label"] == "San Juan", "Unexpected smallest shift")
    approx(top["age_30_plus_share_change_pp"], 13.4)
    approx(bottom["age_30_plus_share_change_pp"], 2.9)

    modes_2024 = province.set_index("province_label")["modal_age_label_2024"]
    require(modes_2024["Formosa"] == "20 a 24", "Unexpected Formosa mode")
    require(
        modes_2024["Ciudad Aut. de Buenos Aires"] == "35 a 39",
        "Unexpected CABA mode",
    )

    text = STORYBOARD.read_text(encoding="utf-8")
    expected_fragments = [
        "777.012",
        "413.135",
        "−363.877 / −46,8%",
        "−19,5%",
        "−14,7%",
        "−22,5%",
        "40,3% → 30,8%",
        "36,6% → 43,6%",
        "+13,4 puntos",
        "+2,9",
    ]
    missing = [fragment for fragment in expected_fragments if fragment not in text]
    require(not missing, f"Storyboard is missing validated claims: {missing}")

    print("OK: storyboard claims reconcile with processed indicators.")
    print("OK: all 24 jurisdictional directions and selected exceptions verified.")


if __name__ == "__main__":
    main()

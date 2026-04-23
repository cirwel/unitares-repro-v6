"""Reproduce Table 5 (paper §11.6) from the submission snapshot,
then compare against the 2026-04-23 snapshot to show fleet drift.

Usage:  python analysis.py
Requires: pandas, matplotlib
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA = Path(__file__).parent / "data"
SUBMISSION = DATA / "verdict_counterfactual_v6_submission.csv"
CURRENT = DATA / "verdict_counterfactual_2026-04-23.csv"


def per_class_summary(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("class", observed=True)
    out = pd.DataFrame({
        "N": g.size(),
        "Flips": g["flipped"].sum(),
    })
    out["Flip %"] = (100.0 * out["Flips"] / out["N"]).round(1)
    out["Δc mean"] = (df.assign(dc=df["c_grounded"] - df["c_legacy"])
                      .groupby("class", observed=True)["dc"].mean().round(4))
    return out.sort_values("N", ascending=False)


def transition_counts(df: pd.DataFrame) -> pd.Series:
    flipped = df[df["flipped"] == 1]
    return (flipped["basin_legacy"] + "→" + flipped["basin_grounded"]).value_counts()


def main() -> None:
    sub = pd.read_csv(SUBMISSION)
    cur = pd.read_csv(CURRENT)

    print("=" * 78)
    print("SUBMISSION SNAPSHOT (paper §11.6 Table 5 equivalent)")
    print(f"window end: 2026-04-18 21:00 MDT   rows: {len(sub):,}   "
          f"flips: {int(sub['flipped'].sum()):,} "
          f"({100.0 * sub['flipped'].mean():.1f}%)")
    print("=" * 78)
    print(per_class_summary(sub).to_string())
    print()
    print("Basin transitions (submission):")
    print(transition_counts(sub).to_string())
    print()

    print("=" * 78)
    print("CURRENT SNAPSHOT (2026-04-23)")
    print(f"window end: 2026-04-23   rows: {len(cur):,}   "
          f"flips: {int(cur['flipped'].sum()):,} "
          f"({100.0 * cur['flipped'].mean():.1f}%)")
    print("=" * 78)
    print(per_class_summary(cur).to_string())
    print()
    print("Basin transitions (current):")
    print(transition_counts(cur).to_string())
    print()

    print("=" * 78)
    print("DRIFT:  submission → current,  same rolling window length, same")
    print("        frozen v6.8 class-conditional calibration constants.")
    print("=" * 78)
    sub_by_class = per_class_summary(sub)[["N", "Flip %"]].rename(
        columns={"N": "N_sub", "Flip %": "flip%_sub"})
    cur_by_class = per_class_summary(cur)[["N", "Flip %"]].rename(
        columns={"N": "N_cur", "Flip %": "flip%_cur"})
    drift = sub_by_class.join(cur_by_class, how="outer")
    drift["Δflip pp"] = (drift["flip%_cur"] - drift["flip%_sub"]).round(1)
    print(drift.to_string())


if __name__ == "__main__":
    main()

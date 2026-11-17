"""Segment profile on the train split (US-13, issue #13).

Describes each customer segment (A, B, C, D) with the demographic variables
available in the dataset, and counts the high spenders per segment, so that
the business questions N1 (who is each segment) and N2 (which one to
prioritise) can be answered with figures from a recorded run.

Reads ``data/train_70.csv`` only. The validation and test splits are never
read: describing the segments is part of the analysis, and every analysis
decision uses the train split (AGENTS.md section 1).

Writes two files, both deterministic (running the script twice gives
byte-identical files, so a change in Git means the figures really changed):

  - reports/segment_profile_train_70.csv
        One row per segment plus an ``All`` row for comparison.
  - reports/segment_distributions_train_70.csv
        Long table with every level of every categorical variable:
        count and share within each segment.

Conventions:

  - Percentages of a categorical variable are computed over the customers
    who have a value for it (missing values are excluded from the
    denominator). The number of missing values is reported next to them.
  - ``Spending_Score`` is a proxy of customer value, not income or revenue.
  - The figures describe the customers; they do not imply causality.

Usage (from the repository root):

    python -m src.segment_profile
"""

from __future__ import annotations

import argparse
import hashlib
import platform
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import TARGET

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Reference values from D-013 (item 1): the script stops if the file it reads
# is not the shared partition.
EXPECTED_ROWS = 5647
EXPECTED_SHA256_LF = "58da50146ebd3ceaff7ac539f4a9c1c1cb21f7055f3d2262b923feaf3e49e754"

NUMERIC_VARIABLES = ("Age", "Work_Experience", "Family_Size")
# Categorical variables listed in the acceptance criteria of US-13.
CATEGORICAL_VARIABLES = (
    "Gender",
    "Ever_Married",
    "Graduated",
    "Profession",
    "Spending_Score",
)
# For the yes/no style variables the summary table keeps one percentage:
# the share of this level.
SUMMARY_LEVELS = {
    "Gender": "Male",
    "Ever_Married": "Yes",
    "Graduated": "Yes",
}
SPENDING_LEVELS = ("Low", "Average", "High")
ALL_LABEL = "All"


def sha256_lf(path: Path) -> str:
    """SHA-256 of the file content with line endings normalised to LF (D-013)."""
    content = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()


def pct(part: float, total: float) -> float:
    """Percentage rounded to one decimal; 0.0 when there is nothing to divide."""
    if total == 0:
        return 0.0
    return round(part / total * 100, 1)


def profile_group(group: pd.DataFrame, total_rows: int, total_high: int) -> dict:
    """Summary of one group of customers (one segment, or the whole split)."""
    row: dict = {
        "n_customers": len(group),
        "pct_of_train": pct(len(group), total_rows),
    }

    for variable in NUMERIC_VARIABLES:
        values = group[variable].dropna()
        name = variable.lower()
        row[f"{name}_median"] = float(values.median())
        row[f"{name}_mean"] = round(float(values.mean()), 2)
        row[f"{name}_missing"] = int(group[variable].isna().sum())

    for variable, level in SUMMARY_LEVELS.items():
        values = group[variable].dropna()
        name = f"{variable.lower()}_{level.lower()}"
        row[f"pct_{name}"] = pct((values == level).sum(), len(values))
        row[f"{variable.lower()}_missing"] = int(group[variable].isna().sum())

    professions = group["Profession"].dropna().value_counts()
    row["top_profession"] = professions.index[0]
    row["pct_top_profession"] = pct(professions.iloc[0], professions.sum())
    row["profession_missing"] = int(group["Profession"].isna().sum())

    # Missing values are excluded from the denominator, like the other
    # categorical percentages (train_70 has none in this column).
    spending = group["Spending_Score"].dropna()
    for level in SPENDING_LEVELS:
        row[f"pct_spending_{level.lower()}"] = pct((spending == level).sum(), len(spending))
    n_high = int((spending == "High").sum())
    row["n_spending_high"] = n_high
    # Share of all the high spenders of the split that belong to this group.
    row["pct_of_all_high"] = pct(n_high, total_high)
    return row


def build_profile_table(df: pd.DataFrame) -> pd.DataFrame:
    """One row per segment (alphabetical order) plus an ``All`` row."""
    total_rows = len(df)
    total_high = int((df["Spending_Score"] == "High").sum())
    rows = []
    for segment, group in df.groupby(TARGET, sort=True):
        rows.append({"segment": segment, **profile_group(group, total_rows, total_high)})
    rows.append({"segment": ALL_LABEL, **profile_group(df, total_rows, total_high)})
    return pd.DataFrame(rows)


def build_distribution_table(df: pd.DataFrame) -> pd.DataFrame:
    """Long table: count and share of every categorical level within each segment."""
    groups = [(segment, group) for segment, group in df.groupby(TARGET, sort=True)]
    groups.append((ALL_LABEL, df))
    rows = []
    for variable in CATEGORICAL_VARIABLES:
        levels = sorted(df[variable].dropna().unique())
        for segment, group in groups:
            values = group[variable].dropna()
            counts = values.value_counts()
            for level in levels:
                count = int(counts.get(level, 0))
                rows.append(
                    {
                        "variable": variable,
                        "level": level,
                        "segment": segment,
                        "count": count,
                        "pct_within_segment": pct(count, len(values)),
                    }
                )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="US-13 segment profile on train_70.")
    parser.add_argument("--train", default="data/train_70.csv")
    parser.add_argument("--reports-dir", default="reports")
    args = parser.parse_args()

    train_path = (PROJECT_ROOT / args.train).resolve()
    reports_dir = (PROJECT_ROOT / args.reports_dir).resolve()
    reports_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(train_path)
    checksum = sha256_lf(train_path)
    if len(df) != EXPECTED_ROWS or checksum != EXPECTED_SHA256_LF:
        raise SystemExit(
            f"{train_path} is not the shared train partition of D-013: "
            f"{len(df)} rows (expected {EXPECTED_ROWS}), SHA-256 {checksum}."
        )

    profile = build_profile_table(df)
    distributions = build_distribution_table(df)

    profile_path = reports_dir / "segment_profile_train_70.csv"
    distributions_path = reports_dir / "segment_distributions_train_70.csv"
    profile.to_csv(profile_path, index=False, lineterminator="\n")
    distributions.to_csv(distributions_path, index=False, lineterminator="\n")

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"run:      {generated_at}")
    print(f"python:   {platform.python_version()}, pandas {pd.__version__}")
    print(f"read:     {train_path} ({len(df):,} rows)")
    print(f"sha256:   {checksum} (matches D-013)")
    print(f"written:  {profile_path}")
    print(f"written:  {distributions_path}")
    print()
    print(profile.set_index("segment").T.to_string())


if __name__ == "__main__":
    main()

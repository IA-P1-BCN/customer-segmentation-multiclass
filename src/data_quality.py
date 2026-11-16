"""Data-quality diagnosis for the Customer Segmentation project (US-04).

Reads the train split to build the missing-value table and reads `Train.csv`
only to check for duplicated IDs. Writes:

  - reports/nulls_train_70.csv  (machine-readable null table)
  - reports/data_quality.md     (report with the proposed imputation strategy)

The train split is the only source of statistics: imputation values must be
computed from `train_70` so that no information leaks from validation or test
(AGENTS.md sections 1 and 5).

Usage (from the repository root):

    python src/data_quality.py

Optional:

    python src/data_quality.py --train data/train_70.csv --ids data/Train.csv
"""

from __future__ import annotations

import argparse
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Strategy proposed in D-011. "none" means the variable has no missing values
# and needs no imputation step.
IMPUTATION_STRATEGY: dict[str, tuple[str, str]] = {
    "ID": ("none", "Identifier, never a feature."),
    "Gender": ("none", "No missing values."),
    "Ever_Married": ("mode", "Binary categorical; mode is stable and interpretable."),
    "Age": ("none", "No missing values."),
    "Graduated": ("mode", "Binary categorical; mode is stable and interpretable."),
    "Profession": (
        "constant:Unknown",
        "9 categories; the mode (Artist, ~31 %) would invent a profession, "
        "so an explicit 'Unknown' level is safer.",
    ),
    "Work_Experience": (
        "median + missing indicator",
        "Numeric, 10 % missing and right-skewed; the median is robust and the "
        "indicator keeps the missingness signal (~10 % is too much to ignore).",
    ),
    "Spending_Score": ("none", "No missing values."),
    "Family_Size": (
        "median + missing indicator",
        "Numeric, 4 % missing; same reasoning as Work_Experience.",
    ),
    "Var_1": ("mode", "Categorical with 7 levels; missingness is under 1 %."),
    "Segmentation": ("none", "Target variable; never imputed."),
}


def build_null_table(df: pd.DataFrame) -> pd.DataFrame:
    """Return one row per column with counts, percentage and strategy."""
    rows = []
    total = len(df)
    for column in df.columns:
        series = df[column]
        null_count = int(series.isna().sum())
        strategy, reason = IMPUTATION_STRATEGY.get(
            column, ("UNKNOWN", "No strategy defined; review before US-05.")
        )
        rows.append(
            {
                "column": column,
                "dtype": str(series.dtype),
                "non_null": int(series.notna().sum()),
                "null_count": null_count,
                "null_pct": round(null_count / total * 100, 2),
                "unique_non_null": int(series.nunique(dropna=True)),
                "imputation": strategy,
                "reason": reason,
            }
        )
    return pd.DataFrame(rows)


def describe_column(df: pd.DataFrame, column: str) -> str:
    """Short evidence string used to justify the chosen imputation value."""
    series = df[column].dropna()
    if series.empty:
        return "no values"
    if pd.api.types.is_numeric_dtype(series):
        return f"median = {series.median():g} (min {series.min():g}, max {series.max():g})"
    counts = series.value_counts()
    top = counts.index[0]
    share = counts.iloc[0] / len(series) * 100
    return f"mode = {top} ({counts.iloc[0]:,} rows, {share:.1f} % of non-null)"


def duplicate_ids_report(path: Path) -> tuple[int, int, int, list[int]]:
    """Check duplicated IDs in the full source file."""
    ids = pd.read_csv(path, usecols=["ID"])
    duplicated_mask = ids["ID"].duplicated(keep="first")
    duplicated_values = ids.loc[duplicated_mask, "ID"].tolist()
    return (
        len(ids),
        int(ids["ID"].nunique()),
        int(duplicated_mask.sum()),
        duplicated_values,
    )


def fmt_pct(value: float) -> str:
    return f"{value:.2f} %"


def repo_relative(path: Path) -> str:
    """Return the path relative to the repository root when possible."""
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def build_markdown(
    train: pd.DataFrame,
    null_table: pd.DataFrame,
    train_path: Path,
    ids_path: Path,
    ids_rows: int,
    ids_unique: int,
    ids_duplicated: int,
    duplicated_values: list[int],
    generated_at: str,
) -> str:
    total_rows = len(train)
    with_nulls = null_table[null_table["null_count"] > 0].sort_values(
        "null_pct", ascending=False
    )

    lines: list[str] = []
    lines.append("# Data quality report (US-04)")
    lines.append("")
    lines.append(f"Generated on {generated_at} by `src/data_quality.py`.")
    lines.append("")

    # --- Reproduction -----------------------------------------------------
    lines.append("## How to reproduce")
    lines.append("")
    lines.append("```")
    lines.append("python src/data_quality.py")
    lines.append("```")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("|---|---|")
    lines.append(f"| Interpreter | `{sys.executable}` |")
    lines.append(f"| Python | {platform.python_version()} |")
    lines.append(f"| pandas | {pd.__version__} |")
    lines.append(f"| Platform | {platform.platform()} |")
    lines.append(f"| Train split | `{repo_relative(train_path)}` ({total_rows:,} rows) |")
    lines.append(f"| ID source | `{repo_relative(ids_path)}` ({ids_rows:,} rows) |")
    lines.append("")

    # --- Missing values ---------------------------------------------------
    lines.append("## 1. Missing values per variable (train split)")
    lines.append("")
    lines.append(
        f"Computed on `{train_path.name}` only ({total_rows:,} rows, "
        f"{len(null_table)} columns). The validation and test splits are not used."
    )
    lines.append("")
    if with_nulls.empty:
        lines.append("No missing values found.")
    else:
        lines.append("| Variable | Type | Missing | Missing % | Unique (non-null) |")
        lines.append("|---|---|---:|---:|---:|")
        for _, row in with_nulls.iterrows():
            lines.append(
                f"| `{row['column']}` | {row['dtype']} | {row['null_count']:,} | "
                f"{fmt_pct(row['null_pct'])} | {row['unique_non_null']} |"
            )
        lines.append("")
        lines.append(
            "Variables without missing values: "
            + ", ".join(
                f"`{c}`"
                for c in null_table.loc[null_table["null_count"] == 0, "column"]
            )
            + "."
        )
    lines.append("")

    # --- Full table -------------------------------------------------------
    lines.append("## 2. Full table")
    lines.append("")
    lines.append("| # | Variable | Type | Missing | Missing % |")
    lines.append("|---:|---|---|---:|---:|")
    for position, (_, row) in enumerate(null_table.iterrows(), start=1):
        lines.append(
            f"| {position} | `{row['column']}` | {row['dtype']} | "
            f"{row['null_count']:,} | {fmt_pct(row['null_pct'])} |"
        )
    lines.append("")
    lines.append("Machine-readable version: `reports/nulls_train_70.csv`.")
    lines.append("")

    # --- Duplicate IDs ----------------------------------------------------
    lines.append("## 3. Duplicated IDs in `Train.csv`")
    lines.append("")
    lines.append(f"- Rows: {ids_rows:,}")
    lines.append(f"- Unique `ID` values: {ids_unique:,}")
    lines.append(f"- Duplicated `ID` values (rows after the first): {ids_duplicated:,}")
    lines.append("")
    if ids_duplicated == 0:
        lines.append(
            "**Result:** no duplicated IDs. The source file can be split and "
            "joined by `ID` safely."
        )
    else:
        preview = ", ".join(str(v) for v in duplicated_values[:20])
        lines.append(
            f"**Result:** {ids_duplicated:,} duplicated ID row(s) found. "
            f"First values: {preview}. Review before using `ID` as a key."
        )
    lines.append("")

    # --- Strategy ---------------------------------------------------------
    lines.append("## 4. Proposed imputation strategy (D-011, pending approval)")
    lines.append("")
    lines.append(
        "All values (median, mode and the `Unknown` level) must be computed with "
        "`train_70` only and applied inside the Pipeline (`SimpleImputer` fitted on "
        "the training fold), never on the full dataset."
    )
    lines.append("")
    lines.append("| Variable | Missing % | Strategy | Evidence in train |")
    lines.append("|---|---:|---|---|")
    for _, row in null_table.iterrows():
        if row["null_count"] == 0:
            continue
        evidence = describe_column(train, row["column"])
        lines.append(
            f"| `{row['column']}` | {fmt_pct(row['null_pct'])} | "
            f"{row['imputation']} | {evidence} |"
        )
    lines.append("")
    lines.append("Notes:")
    lines.append("")
    lines.append(
        "- Missing indicators are binary columns added per variable "
        "(`<variable>_was_missing`); they keep the information contained in the "
        "fact that the value was absent."
    )
    lines.append(
        "- Variables with 0 % missing get no imputation step, which keeps the "
        "Pipeline simple and avoids unnecessary transformed columns."
    )
    lines.append(
        "- `ID` and `Segmentation` are never imputed: the first is an identifier "
        "and the second is the target."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="US-04 data-quality report.")
    parser.add_argument("--train", default="data/train_70.csv")
    parser.add_argument("--ids", default="data/Train.csv")
    parser.add_argument("--reports-dir", default="reports")
    args = parser.parse_args()

    train_path = (PROJECT_ROOT / args.train).resolve()
    ids_path = (PROJECT_ROOT / args.ids).resolve()
    reports_dir = (PROJECT_ROOT / args.reports_dir).resolve()
    reports_dir.mkdir(parents=True, exist_ok=True)

    train = pd.read_csv(train_path)
    null_table = build_null_table(train)

    ids_rows, ids_unique, ids_duplicated, duplicated_values = duplicate_ids_report(
        ids_path
    )

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    csv_path = reports_dir / "nulls_train_70.csv"
    null_table[["column", "dtype", "non_null", "null_count", "null_pct", "imputation"]].to_csv(
        csv_path, index=False, lineterminator="\n"
    )

    markdown = build_markdown(
        train=train,
        null_table=null_table,
        train_path=train_path,
        ids_path=ids_path,
        ids_rows=ids_rows,
        ids_unique=ids_unique,
        ids_duplicated=ids_duplicated,
        duplicated_values=duplicated_values,
        generated_at=generated_at,
    )
    md_path = reports_dir / "data_quality.md"
    md_path.write_text(markdown + "\n", encoding="utf-8", newline="\n")

    print(f"train split: {train_path} ({len(train):,} rows)")
    print(f"ID source:   {ids_path} ({ids_rows:,} rows, {ids_duplicated} duplicated)")
    print(f"written:     {csv_path}")
    print(f"written:     {md_path}")
    print()
    print("Missing values (train split):")
    print(
        null_table.loc[null_table["null_count"] > 0, ["column", "null_count", "null_pct"]]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()

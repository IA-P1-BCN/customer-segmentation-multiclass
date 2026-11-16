from __future__ import annotations

import argparse
import math
import os
import sys
import tempfile
from pathlib import Path

import pandas as pd

RANDOM_STATE = 42
TARGET_COLUMN = "Segmentation"
ID_COLUMN = "ID"
TRAIN_PATH = Path("data/Train.csv")
OUTPUT_PATHS = {
    "train_70": Path("data/train_70.csv"),
    "val_15": Path("data/val_15.csv"),
    "test_15": Path("data/test_15.csv"),
}
TRAIN_RATIO = 0.70
FIRST_TEST_SIZE = 1.0 - TRAIN_RATIO
SECOND_TEST_SIZE = 0.50
# Maximum absolute difference of 1 percentage point between class proportions.
PROPORTION_TOLERANCE = 0.01


def expected_sizes(total_rows: int) -> dict[str, int]:
    remaining_rows = math.ceil(total_rows * FIRST_TEST_SIZE)
    test_rows = math.ceil(remaining_rows * SECOND_TEST_SIZE)
    return {
        "train_70": total_rows - remaining_rows,
        "val_15": remaining_rows - test_rows,
        "test_15": test_rows,
    }


def split_dataframe(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    try:
        from sklearn.model_selection import train_test_split
    except ImportError as exc:
        raise RuntimeError(
            "scikit-learn is required to generate the split. "
            "Install scikit-learn in the active Python environment."
        ) from exc

    train_70, remaining = train_test_split(
        df,
        test_size=FIRST_TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=df[TARGET_COLUMN],
    )
    val_15, test_15 = train_test_split(
        remaining,
        test_size=SECOND_TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=remaining[TARGET_COLUMN],
    )
    return {"train_70": train_70, "val_15": val_15, "test_15": test_15}


def print_summary(splits: dict[str, pd.DataFrame]) -> None:
    for name, df in splits.items():
        proportions = (
            df[TARGET_COLUMN].value_counts(normalize=True).sort_index() * 100
        )
        distribution = ", ".join(
            f"{segment}={value:.2f}%" for segment, value in proportions.items()
        )
        print(
            f"{name}: rows={len(df)}, columns={df.shape[1]}, "
            f"nulls={int(df.isna().sum().sum())}"
        )
        print(f"  Segmentation: {distribution}")


def validate_splits(
    source: pd.DataFrame, splits: dict[str, pd.DataFrame]
) -> list[str]:
    errors: list[str] = []
    expected = expected_sizes(len(source))

    if source[ID_COLUMN].isna().any():
        errors.append("Train.csv contains null IDs.")
    if source[ID_COLUMN].duplicated().any():
        errors.append("Train.csv contains duplicated IDs.")
    if source[TARGET_COLUMN].isna().any():
        errors.append("Train.csv contains missing target values.")

    for name, df in splits.items():
        if len(df) != expected[name]:
            errors.append(
                f"{name}: expected {expected[name]} rows, got {len(df)}."
            )
        if df[ID_COLUMN].isna().any():
            errors.append(f"{name}: null IDs found.")
        if df[ID_COLUMN].duplicated().any():
            errors.append(f"{name}: duplicated IDs found.")
        if df[TARGET_COLUMN].isna().any():
            errors.append(f"{name}: missing target values found.")

        source_proportions = source[TARGET_COLUMN].value_counts(normalize=True)
        split_proportions = df[TARGET_COLUMN].value_counts(normalize=True)
        aligned = split_proportions.reindex(source_proportions.index, fill_value=0.0)
        max_deviation = (aligned - source_proportions).abs().max()
        if max_deviation > PROPORTION_TOLERANCE:
            errors.append(
                f"{name}: class proportions deviate by {max_deviation:.4f} "
                f"(tolerance {PROPORTION_TOLERANCE})."
            )

    names = list(splits)
    for index, first in enumerate(names):
        for second in names[index + 1 :]:
            overlap = set(splits[first][ID_COLUMN]) & set(splits[second][ID_COLUMN])
            if overlap:
                errors.append(f"{first} and {second} share {len(overlap)} IDs.")

    split_ids = set().union(*(set(df[ID_COLUMN]) for df in splits.values()))
    source_ids = set(source[ID_COLUMN])
    if split_ids != source_ids:
        errors.append(
            "Union of split IDs does not equal Train.csv IDs "
            f"({len(split_ids)} vs {len(source_ids)})."
        )

    source_nulls = source.isna().sum()
    split_nulls = pd.Series(0, index=source.columns)
    for df in splits.values():
        split_nulls = split_nulls + df.isna().sum()
    if not split_nulls.equals(source_nulls):
        errors.append("Null counts by column do not match Train.csv.")

    return errors


def _sorted(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(ID_COLUMN).reset_index(drop=True)


def compare_with_existing(splits: dict[str, pd.DataFrame]) -> list[str]:
    mismatches: list[str] = []
    for name, generated in splits.items():
        path = OUTPUT_PATHS[name]
        if not path.exists():
            mismatches.append(f"{path} does not exist.")
            continue

        existing = pd.read_csv(path)
        if list(generated.columns) != list(existing.columns):
            mismatches.append(f"{path}: column order or names differ.")
            continue
        if generated.shape != existing.shape:
            mismatches.append(
                f"{path}: shape differs "
                f"(generated {generated.shape}, existing {existing.shape})."
            )
            continue
        if set(generated[ID_COLUMN]) != set(existing[ID_COLUMN]):
            mismatches.append(f"{path}: ID sets differ.")
            continue

        generated_sorted = _sorted(generated)
        existing_sorted = _sorted(existing)
        for column in generated.columns:
            try:
                pd.testing.assert_series_equal(
                    generated_sorted[column],
                    existing_sorted[column],
                    check_dtype=False,
                    check_names=False,
                )
            except AssertionError:
                mismatches.append(f"{path}: values differ in column '{column}'.")
    return mismatches


def write_splits(splits: dict[str, pd.DataFrame]) -> None:
    """Write all splits to temporary files before replacing the final files."""
    temp_paths: dict[str, Path] = {}
    try:
        for name, df in splits.items():
            path = OUTPUT_PATHS[name]
            descriptor, temp_name = tempfile.mkstemp(
                prefix=f".{path.name}.",
                suffix=".tmp",
                dir=path.parent,
            )
            os.close(descriptor)
            temp_path = Path(temp_name)
            temp_paths[name] = temp_path
            df.to_csv(temp_path, index=False)
            if not temp_path.exists() or temp_path.stat().st_size == 0:
                raise OSError(
                    f"Temporary file for {path} was not written correctly."
                )

        for name, temp_path in temp_paths.items():
            path = OUTPUT_PATHS[name]
            os.replace(temp_path, path)
            print(f"Wrote {path}")
    except Exception:
        for temp_path in temp_paths.values():
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate or check the stratified 70/15/15 split of data/Train.csv."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare the generated split with the existing CSV files without writing.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing CSV files after validation.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not TRAIN_PATH.exists():
        print(f"ERROR: {TRAIN_PATH} does not exist.", file=sys.stderr)
        return 2

    source = pd.read_csv(TRAIN_PATH)
    try:
        splits = split_dataframe(source)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print_summary(splits)
    errors = validate_splits(source, splits)
    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("Validation passed.")

    if args.check:
        mismatches = compare_with_existing(splits)
        if mismatches:
            print(
                "Generated split does not match the existing CSV files:",
                file=sys.stderr,
            )
            for mismatch in mismatches:
                print(f"  - {mismatch}", file=sys.stderr)
            return 1
        print("Generated split matches the existing CSV files.")
        return 0

    existing_paths = [path for path in OUTPUT_PATHS.values() if path.exists()]
    if existing_paths and not args.force:
        mismatches = compare_with_existing(splits)
        if mismatches:
            print(
                "Existing CSV files differ or are incomplete. "
                "Nothing was overwritten; use --force to regenerate.",
                file=sys.stderr,
            )
            for mismatch in mismatches:
                print(f"  - {mismatch}", file=sys.stderr)
            return 1
        print("Existing CSV files already match; nothing written.")
        return 0

    try:
        write_splits(splits)
    except OSError as exc:
        print(f"ERROR: failed to write split files: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

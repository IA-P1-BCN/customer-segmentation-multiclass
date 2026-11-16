"""US-09 - Boosting (XGBoost): baseline and improvement.

The model is XGBoost 3.4.1 (D-0xx, pending record). This script keeps the
shared preprocessing from US-05 as the only transformation step: it imports
``build_preprocessing()`` and fills its parameters with the choices fixed by
D-011 (imputation) and D-014 (encoding). Nothing is transformed by hand and
nothing is fitted outside a training split (D-013, item 3).

Partitions (D-013):

- ``train_70``: fit and 5-fold stratified cross-validation (D-010, item 6).
- ``val_15``: overfitting check and comparison (gap < 5 accuracy points).
- ``test_15``: never used here. It is opened once in US-12 with the frozen
  model. This script only reads its IDs to verify there is no overlap.

Usage (from the repository root):

    python src/train_boosting.py --check      # partition verification only
    python src/train_boosting.py --dry-run    # build the matrix, no training
    python src/train_boosting.py --baseline   # baseline: CV + train + val_15
    python src/train_boosting.py --grid       # the 18 candidate configurations
    python src/train_boosting.py --refine     # second stage around max_depth=3
    python src/train_boosting.py --baseline --grid --refine

Every executed run appends rows to ``results/boosting.csv`` following the
convention in ``results/README.md`` (append-only, one file per model).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import datetime, timezone
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# Allow both `python src/train_boosting.py` and `python -m src.train_boosting`.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RANDOM_STATE  # noqa: E402
from src.preprocessing import build_preprocessing, make_features_target  # noqa: E402

MODEL_NAME = "boosting"
OUTPUT_CSV = "results/boosting.csv"

# Row counts fixed by D-013. A mismatch means the script is reading a different
# partition and the results would not be comparable in US-11.
EXPECTED_ROWS = {"train_70": 5_647, "val_15": 1_210, "test_15": 1_211}

# Reference checksums recorded in D-013, computed over the content with line
# endings normalised to LF. A mismatch aborts the run before any metric is
# recorded: numbers obtained on different data are not comparable in US-11
# (D-013, item 6).
REFERENCE_SHA256_LF = {
    "train_70": "58da50146ebd3ceaff7ac539f4a9c1c1cb21f7055f3d2262b923feaf3e49e754",
    "val_15": "f7243496ce9a93cdfb9104e6e6d7fb045c50788bdf5fd70f7586e5045bcb2db1",
    "test_15": "33427fa164216da231584cabf690528de7c84145dfdb4b9fe273d201edfdbf86",
}

# Columns of results/README.md, in the documented order.
RESULTS_COLUMNS = [
    "run_timestamp_utc",
    "seed",
    "model",
    "config",
    "partition",
    "accuracy",
    "macro_f1",
    "f1_A",
    "f1_B",
    "f1_C",
    "f1_D",
    "notes",
]

# ---------------------------------------------------------------------------
# PROVISIONAL PIPELINE
# ---------------------------------------------------------------------------
# ``build_preprocessing()`` (US-05, phase 1) has a single ``nominal_imputer``
# for ``Gender``, ``Profession`` and ``Var_1``, but D-011 (approved) asks for a
# constant ``Unknown`` level in ``Profession`` and the mode in ``Var_1``. With
# one slot only, the configuration below imputes the three columns with
# ``Unknown``, which adds a ``Var_1_Unknown`` column that D-011 does not
# contemplate.
#
# Consequences: the code, the cross-validation harness and the partition
# verification are final; the recorded metrics are provisional until US-05
# phase 2 lands. Set this flag to False in the same PR that starts using the
# corrected module, and re-run before comparing models in US-11.
PIPELINE_IS_PROVISIONAL = True
PROVISIONAL_NOTE = (
    "provisional pipeline: single nominal_imputer pending US-05 phase 2 "
    "(Unknown also applied to Var_1)"
)

# Baseline: XGBoost with a neutral, untuned configuration.
BASELINE_PARAMS = {
    "n_estimators": 300,
    "max_depth": 4,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
}

# Improvement grid: 3 x 3 x 2 = 18 configurations (18 runs x 5 folds).
GRID_SPACE = {
    "learning_rate": (0.05, 0.1, 0.2),
    "max_depth": (3, 5, 7),
    "subsample": (0.8, 1.0),
}

# Second stage. The grid showed that depth 3 is the only family that stays
# inside the D-010 overfitting limit on train_70/val_15, so the refinement
# explores capacity and minimum leaf size around that depth instead of growing
# the trees. 2 x 2 x 2 = 8 configurations.
REFINE_BASE = {"max_depth": 3, "subsample": 1.0, "colsample_bytree": 0.8}
REFINE_SPACE = {
    "n_estimators": (300, 600),
    "learning_rate": (0.05, 0.1),
    "min_child_weight": (1, 5),
}


# --- Data -------------------------------------------------------------------
def load_partitions() -> dict[str, pd.DataFrame]:
    """Read the three committed partitions from ``data/``."""
    return {
        name: pd.read_csv(PROJECT_ROOT / "data" / f"{name}.csv")
        for name in EXPECTED_ROWS
    }


def sha256_lf(path: Path) -> str:
    """SHA-256 of the file content with line endings normalised to LF.

    D-013 fixes the checksum over the LF version so the value is identical on
    Windows, macOS and Linux; hashing the raw bytes would only match on the
    operating system that produced the file.
    """
    content = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()


def verify_partitions(datasets: dict[str, pd.DataFrame]) -> None:
    """Check row counts, ID overlap and report the reference checksums.

    Raises ``SystemExit`` when the partitions do not match D-013, so a run
    never records metrics on the wrong data.
    """
    problems: list[str] = []
    id_sets: dict[str, set[int]] = {}

    for name, df in datasets.items():
        expected = EXPECTED_ROWS[name]
        status = "ok" if len(df) == expected else "MISMATCH"
        print(f"  {name:<9} rows={len(df):>5,} (expected {expected:,}) {status}")
        if len(df) != expected:
            problems.append(f"{name} has {len(df):,} rows, expected {expected:,}")
        if "ID" not in df.columns:
            problems.append(f"{name} has no ID column")
        else:
            id_sets[name] = set(df["ID"])

    for first, second in [("train_70", "val_15"), ("train_70", "test_15"), ("val_15", "test_15")]:
        if first in id_sets and second in id_sets:
            overlap = id_sets[first] & id_sets[second]
            print(f"  overlap {first}/{second}: {len(overlap)} IDs")
            if overlap:
                problems.append(f"{first} and {second} share {len(overlap)} IDs")

    print("  SHA-256 (LF), reference values recorded in D-013:")
    for name in datasets:
        digest = sha256_lf(PROJECT_ROOT / "data" / f"{name}.csv")
        expected = REFERENCE_SHA256_LF.get(name)
        if expected is None:
            print(f"    {name:<9} {digest}  (no reference recorded)")
            continue
        status = "ok" if digest == expected else "MISMATCH"
        print(f"    {name:<9} {digest}  {status}")
        if digest != expected:
            problems.append(
                f"{name} SHA-256 (LF) is {digest}, D-013 records {expected}"
            )

    if problems:
        print("\nPartition verification FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        raise SystemExit(1)
    print("  partition verification: passed")


# --- Pipeline ---------------------------------------------------------------
def build_preprocessor():
    """Return the shared preprocessor wired with D-011 and D-014.

    D-011 (approved): median plus missing indicators for the numeric columns,
    mode for the binary ones, constant ``Unknown`` for ``Profession``.
    D-014 (proposed): one-hot for binary and nominal columns, with
    ``drop="if_binary"`` so a two-level column contributes a single 0/1 column,
    and one-hot for ``Spending_Score`` (the ordinal order is not monotone with
    the segment, so it is not imposed). ``handle_unknown="ignore"`` keeps the
    prediction app from failing on unseen levels.

    Scaling is intentionally absent: tree-based models do not need it.
    """
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import OneHotEncoder

    return build_preprocessing(
        numeric_imputer=SimpleImputer(strategy="median", add_indicator=True),
        binary_imputer=SimpleImputer(strategy="most_frequent"),
        nominal_imputer=SimpleImputer(strategy="constant", fill_value="Unknown"),
        ordinal_imputer=SimpleImputer(strategy="most_frequent"),
        binary_encoder=OneHotEncoder(drop="if_binary", handle_unknown="ignore"),
        nominal_encoder=OneHotEncoder(drop="if_binary", handle_unknown="ignore"),
        ordinal_encoder=OneHotEncoder(handle_unknown="ignore"),
    )


def build_model(params: dict[str, object]):
    """Return an ``XGBClassifier`` with the given hyperparameters."""
    try:
        from xgboost import XGBClassifier
    except ImportError as exc:  # pragma: no cover - environment problem
        raise RuntimeError(
            "xgboost is required for US-09. Install the pinned version with "
            "`python -m pip install -r requirements.txt`."
        ) from exc

    return XGBClassifier(
        random_state=RANDOM_STATE,
        tree_method="hist",
        verbosity=0,
        **params,
    )


def build_pipeline(params: dict[str, object]):
    """Preprocessing + model, so preprocessing is fitted inside each fold."""
    from sklearn.pipeline import Pipeline

    return Pipeline(
        [("preprocessing", build_preprocessor()), ("model", build_model(params))]
    )


# --- Metrics ----------------------------------------------------------------
def encode_target(y: pd.Series):
    """XGBoost needs numeric labels; the mapping is kept to decode predictions."""
    from sklearn.preprocessing import LabelEncoder

    encoder = LabelEncoder().fit(y)
    return encoder, encoder.transform(y), list(encoder.classes_)


def compute_metrics(y_true, y_pred, classes: list[str]) -> dict[str, float]:
    """Accuracy, macro-F1 and per-class F1 (D-010)."""
    from sklearn.metrics import accuracy_score, f1_score

    per_class = f1_score(
        y_true, y_pred, labels=classes, average=None, zero_division=0
    )
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(
            f1_score(y_true, y_pred, labels=classes, average="macro", zero_division=0)
        ),
    }
    for label, value in zip(classes, per_class):
        metrics[f"f1_{label}"] = float(value)
    return metrics


def cross_validate(
    X: pd.DataFrame, y: pd.Series, params: dict[str, object], folds: int
) -> dict[str, object]:
    """Stratified k-fold CV on ``train_70`` (D-010, item 6).

    Preprocessing is rebuilt and fitted inside every fold, so the imputer and
    the encoders never see the validation part of the fold.
    """
    from sklearn.model_selection import StratifiedKFold

    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=RANDOM_STATE)
    classes = sorted(y.unique())
    out_of_fold = pd.Series(index=y.index, dtype=object)
    fold_accuracy: list[float] = []
    fold_macro_f1: list[float] = []
    fold_train_accuracy: list[float] = []

    for fold, (train_idx, valid_idx) in enumerate(splitter.split(X, y), start=1):
        X_train, X_valid = X.iloc[train_idx], X.iloc[valid_idx]
        y_train, y_valid = y.iloc[train_idx], y.iloc[valid_idx]

        encoder, y_train_encoded, _ = encode_target(y_train)
        pipeline = build_pipeline(params).fit(X_train, y_train_encoded)

        predictions = encoder.inverse_transform(pipeline.predict(X_valid))
        out_of_fold.iloc[valid_idx] = predictions
        train_predictions = encoder.inverse_transform(pipeline.predict(X_train))

        fold_accuracy.append(float(np.mean(predictions == y_valid)))
        fold_macro_f1.append(
            compute_metrics(y_valid, predictions, classes)["macro_f1"]
        )
        fold_train_accuracy.append(float(np.mean(train_predictions == y_train)))
        print(
            f"      fold {fold}/{folds}: accuracy={fold_accuracy[-1]:.4f} "
            f"macro_f1={fold_macro_f1[-1]:.4f}"
        )

    global_metrics = compute_metrics(y, out_of_fold, classes)
    return {
        "classes": classes,
        "accuracy_mean": float(np.mean(fold_accuracy)),
        "accuracy_sd": float(np.std(fold_accuracy)),
        "macro_f1_mean": float(np.mean(fold_macro_f1)),
        "macro_f1_sd": float(np.std(fold_macro_f1)),
        "accuracy_train_mean": float(np.mean(fold_train_accuracy)),
        "per_class_f1": global_metrics,  # out-of-fold, all rows
    }


def fit_and_evaluate(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_valid: pd.DataFrame,
    y_valid: pd.Series,
    params: dict[str, object],
) -> dict[str, float]:
    """Fit on the whole train split and score a given partition."""
    encoder, y_train_encoded, classes = encode_target(y_train)
    pipeline = build_pipeline(params).fit(X_train, y_train_encoded)
    predictions = encoder.inverse_transform(pipeline.predict(X_valid))
    return compute_metrics(y_valid, predictions, classes)


# --- Runs -------------------------------------------------------------------
def environment_note() -> str:
    """Versions that produced the row, so any result can be reproduced.

    AGENTS.md section 5 asks every recorded figure to be reproducible; the
    results convention has no version column, so the versions travel in
    ``notes`` next to the metric they explain.
    """
    import platform as _platform

    try:
        import xgboost

        xgboost_version = xgboost.__version__
    except ImportError:  # pragma: no cover - environment problem
        xgboost_version = "not installed"

    import sklearn

    return (
        f"python={_platform.python_version()}; "
        f"sklearn={sklearn.__version__}; "
        f"xgboost={xgboost_version}"
    )


def result_row(
    timestamp: str,
    config: str,
    partition: str,
    metrics: dict[str, float],
    notes: str,
) -> dict[str, object]:
    """Build one row with the exact column order of results/README.md."""
    row = {
        "run_timestamp_utc": timestamp,
        "seed": RANDOM_STATE,
        "model": MODEL_NAME,
        "config": config,
        "partition": partition,
        "accuracy": round(metrics.get("accuracy", float("nan")), 4),
        "macro_f1": round(metrics.get("macro_f1", float("nan")), 4),
        "f1_A": round(metrics.get("f1_A", float("nan")), 4),
        "f1_B": round(metrics.get("f1_B", float("nan")), 4),
        "f1_C": round(metrics.get("f1_C", float("nan")), 4),
        "f1_D": round(metrics.get("f1_D", float("nan")), 4),
        "notes": notes,
    }
    return row


def run_config(
    config: str,
    params: dict[str, object],
    datasets: dict[str, pd.DataFrame],
    folds: int,
) -> list[dict[str, object]]:
    """Cross-validate, refit on train_70 and score train_70 and val_15."""
    X_train, y_train = make_features_target(datasets["train_70"])
    X_val, y_val = make_features_target(datasets["val_15"])

    print(f"  {config}: {params}")
    cv = cross_validate(X_train, y_train, params, folds)

    on_train = fit_and_evaluate(X_train, y_train, X_train, y_train, params)
    on_val = fit_and_evaluate(X_train, y_train, X_val, y_val, params)
    gap_pp = (on_train["accuracy"] - on_val["accuracy"]) * 100

    notes_suffix = f" | {environment_note()}"
    if PIPELINE_IS_PROVISIONAL:
        notes_suffix += f" | {PROVISIONAL_NOTE}"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Two different overfitting signals: inside the cross-validation (in-fold
    # accuracy against the cross-validated accuracy) and on the refitted model
    # (train_70 against val_15, the pair D-010 uses for the 5-point limit).
    cv_gap_pp = (cv["accuracy_train_mean"] - cv["accuracy_mean"]) * 100

    cv_notes = (
        f"{folds}-fold stratified CV on train_70; "
        f"mean accuracy across folds={cv['accuracy_mean']:.4f} "
        f"(sd {cv['accuracy_sd']:.4f}); "
        f"mean macro_f1 across folds={cv['macro_f1_mean']:.4f} "
        f"(sd {cv['macro_f1_sd']:.4f}); "
        f"in-fold train accuracy={cv['accuracy_train_mean']:.4f}; "
        f"gap in-fold vs CV={cv_gap_pp:.2f} pp; "
        f"row metrics are out-of-fold predictions{notes_suffix}"
    )

    rows = [
        result_row(timestamp, config, "cv5fold", cv["per_class_f1"], cv_notes),
        result_row(
            timestamp,
            config,
            "train_70",
            on_train,
            f"refit on the full train_70{split_notes(gap_pp)}{notes_suffix}",
        ),
        result_row(
            timestamp,
            config,
            "val_15",
            on_val,
            f"evaluated with the model fitted on train_70{split_notes(gap_pp)}"
            f"{notes_suffix}",
        ),
    ]

    print(
        f"      cv macro_f1={cv['macro_f1_mean']:.4f} | "
        f"val accuracy={on_val['accuracy']:.4f} | gap={gap_pp:.2f} pp"
    )
    return rows


def split_notes(gap_pp: float) -> str:
    """D-010 overfitting verdict, recorded next to the numbers."""
    verdict = "within" if abs(gap_pp) < 5 else "ABOVE"
    return f"; train-val accuracy gap={gap_pp:.2f} pp ({verdict} the 5 pp limit)"


def append_results(rows: list[dict[str, object]], output_path: Path) -> None:
    """Append rows to the model CSV, creating it with the header if needed."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows, columns=RESULTS_COLUMNS)
    expected_header = ",".join(RESULTS_COLUMNS)

    write_header = True
    if output_path.exists() and output_path.stat().st_size > 0:
        first_line = output_path.read_text(encoding="utf-8").splitlines()[0].strip()
        if first_line != expected_header:
            # Appending under a different header would silently misalign every
            # column of the log, which is append-only (results/README.md, rule 1).
            raise SystemExit(
                f"{output_path} has a different column set.\n"
                f"  found:    {first_line}\n"
                f"  expected: {expected_header}\n"
                "Fix the file or use another --output path."
            )
        write_header = False

    frame.to_csv(
        output_path,
        mode="a",
        header=write_header,
        index=False,
        lineterminator="\n",
        encoding="utf-8",
    )
    print(f"\nappended {len(frame)} row(s) to {output_path}")


def grid_configurations() -> dict[str, dict[str, object]]:
    """Expand ``GRID_SPACE`` into 18 named configurations."""
    keys = list(GRID_SPACE)
    configs: dict[str, dict[str, object]] = {}
    for values in product(*(GRID_SPACE[key] for key in keys)):
        params = dict(BASELINE_PARAMS)
        params.update(dict(zip(keys, values)))
        name = "grid_" + "_".join(f"{key}={value}" for key, value in zip(keys, values))
        configs[name] = params
    return configs


def refine_configurations() -> dict[str, dict[str, object]]:
    """Expand ``REFINE_SPACE`` into 8 configurations around ``REFINE_BASE``."""
    keys = list(REFINE_SPACE)
    configs: dict[str, dict[str, object]] = {}
    for values in product(*(REFINE_SPACE[key] for key in keys)):
        params = {**BASELINE_PARAMS, **REFINE_BASE}
        params.update(dict(zip(keys, values)))
        name = "refine_" + "_".join(f"{key}={value}" for key, value in zip(keys, values))
        configs[name] = params
    return configs


def dry_run(datasets: dict[str, pd.DataFrame]) -> None:
    """Fit only the preprocessing and report the shape of the feature matrix."""
    X_train, y_train = make_features_target(datasets["train_70"])
    preprocessor = build_preprocessor()
    matrix = preprocessor.fit_transform(X_train, y_train)
    dense = matrix.toarray() if hasattr(matrix, "toarray") else np.asarray(matrix)
    names = list(preprocessor.get_feature_names_out())

    print(f"\nfeatures before: {X_train.shape[1]} columns")
    print(f"features after:  {dense.shape[1]} columns")
    print(f"NaN in matrix:   {int(pd.isna(dense).sum())}")
    print(f"dtype:           {dense.dtype}")
    print("\ncolumns:")
    for name in names:
        print(f"  {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="US-09 boosting with XGBoost.")
    parser.add_argument("--check", action="store_true", help="verify partitions only")
    parser.add_argument("--dry-run", action="store_true", help="build the matrix only")
    parser.add_argument("--baseline", action="store_true", help="run the baseline")
    parser.add_argument("--grid", action="store_true", help="run the 18 configurations")
    parser.add_argument(
        "--refine", action="store_true", help="run the 8 refinement configurations"
    )
    parser.add_argument("--folds", type=int, default=5, help="CV folds (D-010: 5)")
    parser.add_argument("--output", default=OUTPUT_CSV, help="results CSV path")
    args = parser.parse_args()

    if not (args.check or args.dry_run or args.baseline or args.grid or args.refine):
        parser.print_help()
        return

    if args.folds < 2:
        raise SystemExit("--folds must be at least 2")

    if args.folds != 5:
        print(
            "WARNING: D-010 fixes 5 folds. The rows are still labelled `cv5fold`\n"
            "         because that is the partition value defined in\n"
            "         results/README.md; use another value only for a sensitivity\n"
            "         analysis and explain it in the notes.\n"
        )

    print("Partition verification (D-013):")
    datasets = load_partitions()
    verify_partitions(datasets)

    if PIPELINE_IS_PROVISIONAL:
        print(
            "\nWARNING: the shared preprocessing cannot yet apply D-011 in full\n"
            "         (single nominal_imputer for Gender/Profession/Var_1).\n"
            "         Metrics from this run are PROVISIONAL until US-05 phase 2.\n"
        )

    if args.check:
        return

    if args.dry_run:
        dry_run(datasets)
        return

    configs: dict[str, dict[str, object]] = {}
    if args.baseline:
        configs["baseline"] = dict(BASELINE_PARAMS)
    if args.grid:
        configs.update(grid_configurations())
    if args.refine:
        configs.update(refine_configurations())

    print(f"\nRunning {len(configs)} configuration(s) with {args.folds} folds:")
    rows: list[dict[str, object]] = []
    for name, params in configs.items():
        rows.extend(run_config(name, params, datasets, args.folds))

    output_path = (PROJECT_ROOT / args.output).resolve()
    append_results(rows, output_path)


if __name__ == "__main__":
    main()

"""Random forest for customer segmentation: baseline and improvement (US-08, issue #20).

Run from the repository root:

    python -m src.train_random_forest --stage baseline
    python -m src.train_random_forest --stage tune

Stages
------
baseline
    Fits ``RandomForestClassifier`` with scikit-learn defaults (only the seed
    is fixed) on ``train_70`` and evaluates it on ``train_70`` and ``val_15``.
tune
    Compares a grid of configurations with 5-fold stratified cross-validation
    on ``train_70`` (D-010 item 6), passing the full Pipeline so imputation and
    encoding are fitted inside each fold. The selected configuration is the
    best CV macro-F1 among those whose train - CV accuracy gap is below
    5 points; it is then refitted on ``train_70`` and evaluated on ``val_15``
    (official overfitting check, D-010 item 3). ``val_15`` is never used to
    choose between configurations.

Every run appends rows to ``results/random_forest.csv`` following
``results/README.md`` (append-only). ``test_15`` is never read.

Preprocessing follows D-011 (imputation, Approved) and D-014 (encoding,
Proposed at the time of writing), wired through the parameters of
``src.preprocessing.build_preprocessing`` without modifying that module
(D-014 item 5). If D-014 changes, re-run both stages (D-013, Consequences).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.config import ID_COLUMN, RANDOM_STATE
from src.preprocessing import build_preprocessing, make_features_target

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RESULTS_PATH = ROOT / "results" / "random_forest.csv"
MODEL_NAME = "random_forest"
CLASSES = ("A", "B", "C", "D")
MAX_ACCURACY_GAP = 0.05  # D-010 item 3: train - validation accuracy < 5 points

# D-013 item 1: expected rows and SHA-256 of each partition. The hashes are
# computed after normalising line endings to LF, which is how Git stores the
# files. D-013 lists the hashes of a Windows (CRLF) checkout; both describe
# the same content.
PARTITIONS = {
    "train_70": (5647, "58da50146ebd3ceaff7ac539f4a9c1c1cb21f7055f3d2262b923feaf3e49e754"),
    "val_15": (1210, "f7243496ce9a93cdfb9104e6e6d7fb045c50788bdf5fd70f7586e5045bcb2db1"),
}

RESULT_COLUMNS = [
    "run_timestamp_utc", "seed", "model", "config", "partition",
    "accuracy", "macro_f1", "f1_A", "f1_B", "f1_C", "f1_D", "notes",
]

# Improvement grid (issue #20: number of trees, maximum depth, minimum
# samples per leaf). max_features is added because it is the other main
# lever against overfitting in a random forest.
TUNING_GRID = {
    "n_estimators": [300],
    "max_depth": [4, 6, 8, 10, 12, None],
    "min_samples_leaf": [1, 5, 10, 20, 40],
    "max_features": ["sqrt", 0.5],
}


# --- Data -------------------------------------------------------------------

def _sha256_lf(path: Path) -> str:
    """SHA-256 of the file with line endings normalised to LF."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_partitions() -> dict[str, pd.DataFrame]:
    """Load train_70 and val_15 and run the D-013 item 6 checks."""
    frames = {}
    for name, (rows, sha) in PARTITIONS.items():
        path = DATA_DIR / f"{name}.csv"
        actual_sha = _sha256_lf(path)
        df = pd.read_csv(path)
        if len(df) != rows or actual_sha != sha:
            raise RuntimeError(
                f"{name}: expected {rows} rows and SHA-256 {sha[:12]}..., "
                f"got {len(df)} rows and {actual_sha[:12]}... (D-013)."
            )
        frames[name] = df
        print(f"{name}: {len(df)} rows, SHA-256 (LF) {actual_sha[:12]}... OK")
    overlap = set(frames["train_70"][ID_COLUMN]) & set(frames["val_15"][ID_COLUMN])
    if overlap:
        raise RuntimeError(f"{len(overlap)} IDs appear in both train_70 and val_15.")
    print("No ID overlap between train_70 and val_15.")
    return frames


# --- Model ------------------------------------------------------------------

def build_preprocessor() -> ColumnTransformer:
    """Shared preprocessing with D-011 imputation and D-014 encoding."""
    nominal_imputer = ColumnTransformer(
        [
            ("profession", SimpleImputer(strategy="constant", fill_value="Unknown"), ["Profession"]),
            ("mode", SimpleImputer(strategy="most_frequent"), ["Gender", "Var_1"]),
        ],
        verbose_feature_names_out=False,
    ).set_output(transform="pandas")
    return build_preprocessing(
        numeric_imputer=SimpleImputer(strategy="median", add_indicator=True),
        binary_imputer=SimpleImputer(strategy="most_frequent"),
        nominal_imputer=nominal_imputer,
        binary_encoder=OneHotEncoder(drop="if_binary", handle_unknown="ignore", sparse_output=False),
        nominal_encoder=OneHotEncoder(handle_unknown="ignore", sparse_output=False),
        ordinal_encoder=OneHotEncoder(handle_unknown="ignore", sparse_output=False),
    )


def build_model(**params: Any) -> Pipeline:
    """Full Pipeline: shared preprocessing + random forest with the global seed."""
    forest = RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1, **params)
    return Pipeline([("preprocessing", build_preprocessor()), ("model", forest)])


def evaluate(model: Pipeline, X: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    """Accuracy, macro-F1 and per-class F1 (D-010)."""
    pred = model.predict(X)
    per_class = f1_score(y, pred, labels=list(CLASSES), average=None)
    metrics = {
        "accuracy": accuracy_score(y, pred),
        "macro_f1": f1_score(y, pred, average="macro"),
    }
    metrics.update({f"f1_{c}": v for c, v in zip(CLASSES, per_class)})
    return metrics


# --- Recording --------------------------------------------------------------

def append_results(rows: list[dict[str, Any]]) -> None:
    """Append rows to results/random_forest.csv (append-only, results/README.md)."""
    RESULTS_PATH.parent.mkdir(exist_ok=True)
    new_file = not RESULTS_PATH.exists()
    with RESULTS_PATH.open("a", newline="", encoding="utf-8") as fh:
        # LF line endings on every platform, so the file is identical on Windows and macOS.
        writer = csv.DictWriter(fh, fieldnames=RESULT_COLUMNS, lineterminator="\n")
        if new_file:
            writer.writeheader()
        for row in rows:
            writer.writerow({k: _fmt(row.get(k, "")) for k in RESULT_COLUMNS})
    print(f"Appended {len(rows)} rows to {RESULTS_PATH.relative_to(ROOT)}")


def _fmt(value: Any) -> Any:
    return round(float(value), 4) if isinstance(value, (float, np.floating)) else value


def _config_str(label: str, params: dict[str, Any]) -> str:
    return f"{label} {json.dumps(params, sort_keys=True)}"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def train_and_validate(label: str, params: dict[str, Any], frames, timestamp: str,
                       extra_note: str = "") -> list[dict[str, Any]]:
    """Fit on train_70, evaluate on train_70 and val_15, print the D-010 report."""
    X_train, y_train = make_features_target(frames["train_70"])
    X_val, y_val = make_features_target(frames["val_15"])
    model = build_model(**params).fit(X_train, y_train)
    train_m = evaluate(model, X_train, y_train)
    val_m = evaluate(model, X_val, y_val)
    gap = train_m["accuracy"] - val_m["accuracy"]
    f1_gap = train_m["macro_f1"] - val_m["macro_f1"]
    passed = gap < MAX_ACCURACY_GAP
    print(f"\n[{label}] {params}")
    print(f"  accuracy  train {train_m['accuracy']:.4f} | val {val_m['accuracy']:.4f} | "
          f"gap {gap * 100:.2f} points ({gap / train_m['accuracy'] * 100:.1f} % relative) -> "
          f"{'meets' if passed else 'DOES NOT meet'} the < 5 points limit")
    print(f"  macro-F1  train {train_m['macro_f1']:.4f} | val {val_m['macro_f1']:.4f} | gap {f1_gap:.4f}")
    print("  Per-class report on val_15:")
    print(classification_report(y_val, model.predict(X_val), digits=3))
    note = (f"accuracy gap {gap * 100:.2f} pts ({'meets' if passed else 'fails'} < 5); "
            f"macro-F1 gap {f1_gap:.4f}; preprocessing D-011 + D-014 (Proposed)")
    if extra_note:
        note = f"{extra_note}; {note}"
    common = {"run_timestamp_utc": timestamp, "seed": RANDOM_STATE, "model": MODEL_NAME,
              "config": _config_str(label, params)}
    return [
        {**common, "partition": "train_70", **train_m, "notes": note},
        {**common, "partition": "val_15", **val_m, "notes": note},
    ]


# --- Stages -----------------------------------------------------------------

def run_baseline(frames, record: bool) -> None:
    rows = train_and_validate("baseline", {}, frames, _now(),
                              extra_note="scikit-learn defaults (n_estimators=100, max_depth=None)")
    if record:
        append_results(rows)


def run_tuning(frames, record: bool) -> None:
    X_train, y_train = make_features_target(frames["train_70"])
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    keys = list(TUNING_GRID)
    configs = [dict(zip(keys, values)) for values in itertools.product(*TUNING_GRID.values())]
    timestamp = _now()
    print(f"\nCross-validating {len(configs)} configurations (5-fold stratified on train_70)...")

    cv_rows, summary = [], []
    for i, params in enumerate(configs, start=1):
        scores = cross_validate(build_model(**params), X_train, y_train, cv=cv,
                                scoring=["accuracy", "f1_macro"], return_train_score=True)
        acc, acc_sd = scores["test_accuracy"].mean(), scores["test_accuracy"].std()
        f1, f1_sd = scores["test_f1_macro"].mean(), scores["test_f1_macro"].std()
        train_acc = scores["train_accuracy"].mean()
        gap = train_acc - acc
        summary.append({**params, "cv_accuracy": acc, "cv_macro_f1": f1, "train_cv_gap": gap})
        cv_rows.append({
            "run_timestamp_utc": timestamp, "seed": RANDOM_STATE, "model": MODEL_NAME,
            "config": _config_str(f"tune-{i:02d}", params), "partition": "cv5fold",
            "accuracy": acc, "macro_f1": f1,
            "notes": (f"mean of 5 folds; sd accuracy {acc_sd:.4f}, sd macro-F1 {f1_sd:.4f}; "
                      f"train accuracy {train_acc:.4f}; train - CV gap {gap * 100:.2f} pts"),
        })
        print(f"  {i:02d}/{len(configs)} {params} -> CV macro-F1 {f1:.4f}, "
              f"CV accuracy {acc:.4f}, train-CV gap {gap * 100:.2f} pts")

    table = pd.DataFrame(summary)
    eligible = table[table["train_cv_gap"] < MAX_ACCURACY_GAP]
    if eligible.empty:
        print("\nNo configuration meets the < 5 points train - CV gap; selecting the smallest gap.")
        best = table.sort_values("train_cv_gap").iloc[0]
        reason = "no config met the CV gap limit; smallest train-CV gap"
    else:
        best = eligible.sort_values("cv_macro_f1", ascending=False).iloc[0]
        reason = (f"selected: best CV macro-F1 among {len(eligible)}/{len(table)} configs "
                  f"with train-CV gap < 5 pts")
    best_params = {k: _py(best[k]) for k in keys}
    print(f"\n{reason}: {best_params}")

    final_rows = train_and_validate("tuned", best_params, frames, timestamp, extra_note=reason)
    if record:
        append_results(cv_rows + final_rows)


def _py(value: Any) -> Any:
    """Convert numpy / NaN values from the summary table back to plain Python."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return int(value) if float(value).is_integer() and value > 1 else float(value)
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--stage", choices=["baseline", "tune"], required=True)
    parser.add_argument("--no-record", action="store_true",
                        help="Print the results without appending them to results/random_forest.csv.")
    args = parser.parse_args(argv)

    frames = load_partitions()
    if args.stage == "baseline":
        run_baseline(frames, record=not args.no_record)
    else:
        run_tuning(frames, record=not args.no_record)
    return 0


if __name__ == "__main__":
    sys.exit(main())

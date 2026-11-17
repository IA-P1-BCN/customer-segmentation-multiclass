"""Support vector machine for customer segmentation: baseline and improvement (US-10, issue #22).

Run from the repository root:

    python -m src.train_svm --stage baseline
    python -m src.train_svm --stage tune --rule cv

Stages
------
baseline
    Fits ``SVC`` with scikit-learn defaults on ``train_70`` (only the seed is
    fixed) and evaluates it on ``train_70`` and ``val_15``.
tune
    Fits a small grid of configurations, compares them with 5-fold stratified
    cross-validation on ``train_70`` (D-010 item 6, full Pipeline inside every
    fold) and also records their train/validation results, because issue #22
    asks for every configuration's macro-F1, train/val gap and training time.
    The final configuration is chosen with ``--rule`` (see ``select_cv`` and
    ``select_val``), refitted on ``train_70`` and evaluated on ``val_15``.

Selection rule (``--rule``)
---------------------------
``cv`` (default)
    Cross-validation only: among the configurations whose train - CV accuracy
    gap is below 5 points, those within one standard error of the best CV
    macro-F1 are tied, and the smallest gap wins. This is the rule proposed in
    D-015 (still ``Proposed``), the one already followed by the random forest
    (``src/train_random_forest.py``) and the one voted for by Brian on PR #68.
``val``
    Best ``val_15`` macro-F1 among the configurations whose train - validation
    gap is below 5 points. This is how the logistic regression and the XGBoost
    PRs chose (US-07, US-09), so it keeps the model comparable with them if the
    team approves option A of D-015.
The rule in force is written in the ``notes`` of every recorded row, so a run
can never be mistaken for the other rule.

Scaling
-------
SVM needs scaled features, so ``StandardScaler`` is a step of this model's
Pipeline, after the shared preprocessing and before the estimator (D-013 item
3; D-014 item 6 draws the same line for logistic regression). The shared
``src/preprocessing.py`` is not modified.

Every run appends rows to ``results/svm.csv`` following ``results/README.md``
(append-only). ``test_15`` is never read: it is opened once in US-12 with the
frozen model. Training time is recorded in ``notes`` (issue #22 criterion) so
the common 12-column results header stays unchanged.

Preprocessing follows D-011 (imputation, Approved) and D-014 (encoding,
Approved on 2026-11-16) and yields 28 columns on ``train_70``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC

from src.config import ID_COLUMN, RANDOM_STATE
from src.preprocessing import build_preprocessing, make_features_target

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RESULTS_PATH = ROOT / "results" / "svm.csv"
MODEL_NAME = "svm"
CLASSES = ("A", "B", "C", "D")
MAX_ACCURACY_GAP = 0.05  # D-010 item 3: train - validation accuracy < 5 points
CV_FOLDS = 5  # D-010 item 6

# D-013 item 1: expected rows and SHA-256 of each partition, computed over the
# content with line endings normalised to LF.
PARTITIONS = {
    "train_70": (5647, "58da50146ebd3ceaff7ac539f4a9c1c1cb21f7055f3d2262b923feaf3e49e754"),
    "val_15": (1210, "f7243496ce9a93cdfb9104e6e6d7fb045c50788bdf5fd70f7586e5045bcb2db1"),
}

RESULT_COLUMNS = [
    "run_timestamp_utc", "seed", "model", "config", "partition",
    "accuracy", "macro_f1", "f1_A", "f1_B", "f1_C", "f1_D", "notes",
]

# Improvement grid (issue #22: C and kernel). `gamma` only applies to the RBF
# kernel, so the grid is written as explicit configurations instead of a
# product of independent lists.
TUNING_GRID: list[dict[str, Any]] = [
    {"kernel": "linear", "C": 0.1},
    {"kernel": "linear", "C": 1.0},
    {"kernel": "linear", "C": 10.0},
    *[
        {"kernel": "rbf", "C": c, "gamma": gamma}
        for c in (0.1, 1.0, 10.0)
        for gamma in ("scale", 0.01)
    ],
]

# Configuration chosen by the run recorded on 2026-11-17 in results/svm.csv
# (selection rule cv, D-015 option B). US-11 imports this instead of copying
# the hyperparameters by hand, so the frozen model cannot drift from the
# recorded run.
SELECTED_PARAMS: dict[str, Any] = {"kernel": "rbf", "C": 1.0, "gamma": 0.01}


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
        nominal_encoder=OneHotEncoder(drop="if_binary", handle_unknown="ignore", sparse_output=False),
        ordinal_encoder=OneHotEncoder(handle_unknown="ignore", sparse_output=False),
    )


def build_model(**params: Any) -> Pipeline:
    """Full Pipeline: shared preprocessing, scaler, SVM with the global seed."""
    svm = SVC(random_state=RANDOM_STATE, **params)
    return Pipeline(
        [
            ("preprocessing", build_preprocessor()),
            ("scaler", StandardScaler()),
            ("model", svm),
        ]
    )


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
    """Append rows to results/svm.csv (append-only, results/README.md)."""
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


def _gap_note(train_acc: float, val_acc: float) -> str:
    """Absolute and relative train/validation accuracy gap (issue #22)."""
    absolute = (train_acc - val_acc) * 100
    relative = (train_acc - val_acc) / train_acc * 100
    verdict = "meets" if train_acc - val_acc < MAX_ACCURACY_GAP else "fails"
    return f"accuracy gap {absolute:.2f} pts ({relative:.1f} % relative, {verdict} < 5)"


def train_and_validate(label: str, params: dict[str, Any], frames, timestamp: str,
                       extra_note: str = "", selected: bool = False) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Fit on train_70, evaluate on train_70 and val_15, print the D-010 report."""
    X_train, y_train = make_features_target(frames["train_70"])
    X_val, y_val = make_features_target(frames["val_15"])
    model = build_model(**params)
    started = time.perf_counter()
    model.fit(X_train, y_train)
    fit_time = time.perf_counter() - started
    train_m = evaluate(model, X_train, y_train)
    val_m = evaluate(model, X_val, y_val)
    f1_gap = train_m["macro_f1"] - val_m["macro_f1"]
    print(f"\n[{label}] {params}")
    print(f"  accuracy  train {train_m['accuracy']:.4f} | val {val_m['accuracy']:.4f} | "
          f"gap {_gap_note(train_m['accuracy'], val_m['accuracy'])}")
    print(f"  macro-F1  train {train_m['macro_f1']:.4f} | val {val_m['macro_f1']:.4f} | "
          f"gap {f1_gap:.4f}")
    print(f"  fit time  {fit_time:.2f} s")
    print("  Per-class report on val_15:")
    print(classification_report(y_val, model.predict(X_val), digits=3))
    note = (f"{_gap_note(train_m['accuracy'], val_m['accuracy'])}; "
            f"macro-F1 gap {f1_gap:.4f}; fit time {fit_time:.2f} s; "
            f"preprocessing D-011 + D-014 (Approved, 28 columns)")
    if extra_note:
        note = f"{extra_note}; {note}"
    if selected:
        note = f"SELECTED; {note}"
    common = {"run_timestamp_utc": timestamp, "seed": RANDOM_STATE, "model": MODEL_NAME,
              "config": _config_str(label, params)}
    rows = [
        {**common, "partition": "train_70", **train_m, "notes": note},
        {**common, "partition": "val_15", **val_m, "notes": note},
    ]
    summary = {
        "params": params,
        "label": label,
        "train_accuracy": train_m["accuracy"],
        "val_accuracy": val_m["accuracy"],
        "val_macro_f1": val_m["macro_f1"],
        "train_val_gap": train_m["accuracy"] - val_m["accuracy"],
        "fit_time": fit_time,
        "passed": train_m["accuracy"] - val_m["accuracy"] < MAX_ACCURACY_GAP,
    }
    return rows, summary


# --- Selection --------------------------------------------------------------

def select_cv(table: pd.DataFrame) -> tuple[pd.Series, str]:
    """Choose one row of the CV summary table with the rule proposed in D-015.

    1. Keep the configurations whose train - CV accuracy gap is below the
       D-010 limit (5 points).
    2. Among them, treat as tied those whose CV macro-F1 is within one standard
       error of the best one (fold standard deviation of the best / sqrt(folds)).
    3. Among the tied ones, select the smallest gap; if equal, the highest CV
       macro-F1. If none meets the gap limit, the smallest gap is selected and
       the record says so.
    """
    eligible = table[table["train_cv_gap"] < MAX_ACCURACY_GAP]
    if eligible.empty:
        best = table.sort_values("train_cv_gap").iloc[0]
        return best, "no config met the CV gap limit; smallest train-CV gap (D-015 item 6)"
    top = eligible.sort_values("cv_macro_f1", ascending=False).iloc[0]
    std_error = top["cv_macro_f1_sd"] / np.sqrt(CV_FOLDS)
    tied = eligible[eligible["cv_macro_f1"] >= top["cv_macro_f1"] - std_error]
    best = tied.sort_values(["train_cv_gap", "cv_macro_f1"], ascending=[True, False]).iloc[0]
    reason = (f"selected with CV (D-015 proposed): smallest train-CV gap among {len(tied)} configs "
              f"within one standard error ({std_error:.4f}) of the best CV macro-F1 "
              f"({top['cv_macro_f1']:.4f}); {len(eligible)}/{len(table)} configs with gap < 5 pts")
    return best, reason


def select_val(table: pd.DataFrame) -> tuple[pd.Series, str]:
    """Choose the best ``val_15`` macro-F1 among the admissible configurations.

    This mirrors how US-07 and US-09 chose (option A of D-015). ``val_15`` is
    used to choose, so the recorded figure is optimistic; the rule is written
    in every row to make that visible.
    """
    eligible = table[table["train_val_gap"] < MAX_ACCURACY_GAP]
    if eligible.empty:
        best = table.sort_values("train_val_gap").iloc[0]
        return best, ("no config met the val gap limit; smallest train-val gap "
                      "(declared, issue #22)")
    best = eligible.sort_values("val_macro_f1", ascending=False).iloc[0]
    reason = (f"selected on val_15 (option A of D-015): highest val macro-F1 "
              f"({best['val_macro_f1']:.4f}) among {len(eligible)}/{len(table)} configs "
              f"with train-val gap < 5 pts")
    return best, reason


SELECTORS = {"cv": select_cv, "val": select_val}


# --- Stages -----------------------------------------------------------------

def run_baseline(frames, record: bool) -> None:
    rows, _ = train_and_validate(
        "baseline", {}, frames, _now(),
        extra_note="scikit-learn defaults (kernel=rbf, C=1.0, gamma=scale)",
    )
    if record:
        append_results(rows)


def run_tuning(frames, record: bool, rule: str) -> None:
    X_train, y_train = make_features_target(frames["train_70"])
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    timestamp = _now()
    print(f"\nCross-validating {len(TUNING_GRID)} configurations "
          f"(5-fold stratified on train_70, selection rule: {rule})...")

    cv_rows, cv_summary = [], []
    for i, params in enumerate(TUNING_GRID, start=1):
        scores = cross_validate(build_model(**params), X_train, y_train, cv=cv,
                                scoring=["accuracy", "f1_macro"], return_train_score=True)
        acc, acc_sd = scores["test_accuracy"].mean(), scores["test_accuracy"].std()
        f1, f1_sd = scores["test_f1_macro"].mean(), scores["test_f1_macro"].std()
        train_acc = scores["train_accuracy"].mean()
        gap = train_acc - acc
        cv_summary.append({**params, "cv_accuracy": acc, "cv_macro_f1": f1,
                           "cv_macro_f1_sd": f1_sd, "train_cv_gap": gap})
        cv_rows.append({
            "run_timestamp_utc": timestamp, "seed": RANDOM_STATE, "model": MODEL_NAME,
            "config": _config_str(f"grid-{i:02d}", params), "partition": "cv5fold",
            "accuracy": acc, "macro_f1": f1,
            "notes": (f"mean of 5 folds; sd accuracy {acc_sd:.4f}, sd macro-F1 {f1_sd:.4f}; "
                      f"in-fold train accuracy {train_acc:.4f}; train - CV gap {gap * 100:.2f} pts; "
                      f"selection rule: {rule}"),
        })
        print(f"  {i:02d}/{len(TUNING_GRID)} {params} -> CV macro-F1 {f1:.4f}, "
              f"CV accuracy {acc:.4f}, train-CV gap {gap * 100:.2f} pts")

    # Issue #22 asks for every configuration's macro-F1, train/val gap and
    # training time, so each configuration is also fitted on the full train_70
    # and evaluated on val_15 (recorded always; used to choose only for --rule val).
    full_rows, full_summary = [], []
    for i, params in enumerate(TUNING_GRID, start=1):
        rows, summary = train_and_validate(f"grid-{i:02d}", params, frames, timestamp)
        full_rows.extend(rows)
        summary["cv_macro_f1"] = cv_summary[i - 1]["cv_macro_f1"]
        summary["cv_macro_f1_sd"] = cv_summary[i - 1]["cv_macro_f1_sd"]
        summary["train_cv_gap"] = cv_summary[i - 1]["train_cv_gap"]
        full_summary.append(summary)

    table = pd.DataFrame(full_summary)
    best, reason = SELECTORS[rule](table)
    best_params = best["params"]
    print(f"\n{reason}: {best_params}")

    # Mark the selected configuration in the rows already fitted above and add
    # a dedicated pair of rows so the choice is explicit in the results file.
    selected_rows, _ = train_and_validate("tuned", best_params, frames, timestamp,
                                          extra_note=reason, selected=True)
    if record:
        append_results(cv_rows + full_rows + selected_rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--stage", choices=["baseline", "tune"], required=True)
    parser.add_argument("--rule", choices=sorted(SELECTORS), default="cv",
                        help="Selection rule for --stage tune: 'cv' (D-015 proposed, "
                             "default) or 'val' (option A, as US-07/US-09 did).")
    parser.add_argument("--no-record", action="store_true",
                        help="Print the results without appending them to results/svm.csv.")
    args = parser.parse_args(argv)

    frames = load_partitions()
    if args.stage == "baseline":
        run_baseline(frames, record=not args.no_record)
    else:
        run_tuning(frames, record=not args.no_record, rule=args.rule)
    return 0


if __name__ == "__main__":
    sys.exit(main())

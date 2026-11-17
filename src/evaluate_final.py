"""Final evaluation of the frozen model (US-12, issue #29).

Two runs, and the second one happens exactly once:

    python -m src.evaluate_final --model models/final_model.joblib --partition val_15
    python -m src.evaluate_final --model models/final_model.joblib --partition test_15 --allow-test

What it reports
---------------
- Accuracy, macro-F1 and per-class precision, recall and F1 (D-010).
- Confusion matrix in counts and normalised by row (issue #29).
- Comparison with the majority-class baseline and, when the partition is
  ``test_15``, the difference against ``val_15`` (accuracy and macro-F1).
- Permutation importance of the **original variables** on the chosen partition.
  Permuting the raw columns of the Pipeline groups the one-hot columns of a
  variable by construction, so ``Profession`` weighs as one variable instead of
  ten, and the numbers are not affected by which category the encoder kept.

``test_15`` is refused unless ``--allow-test`` is passed, and that flag is meant
to be used once, after D-011/US-11 freeze the model (D-012 item 4). Running it
twice would turn the test split into another tuning set.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)

from src.config import ID_COLUMN, RANDOM_STATE, TARGET
from src.preprocessing import make_features_target

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
CLASSES = ("A", "B", "C", "D")

# D-013 item 1: reference row counts and SHA-256 with line endings normalised to LF.
PARTITIONS = {
    "train_70": (5647, "58da50146ebd3ceaff7ac539f4a9c1c1cb21f7055f3d2262b923feaf3e49e754"),
    "val_15": (1210, "f7243496ce9a93cdfb9104e6e6d7fb045c50788bdf5fd70f7586e5045bcb2db1"),
    "test_15": (1211, "33427fa164216da231584cabf690528de7c84145dfdb4b9fe273d201edfdbf86"),
}


def _sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_partition(name: str) -> pd.DataFrame:
    """Load a partition and verify it against D-013 before using it."""
    rows, expected = PARTITIONS[name]
    path = DATA_DIR / f"{name}.csv"
    digest = _sha256_lf(path)
    df = pd.read_csv(path)
    if len(df) != rows or digest != expected:
        raise RuntimeError(f"{name}: expected {rows} rows and SHA-256 {expected[:12]}..., "
                           f"got {len(df)} rows and {digest[:12]}... (D-013).")
    return df


def metrics(y_true: pd.Series, y_pred: Any) -> dict[str, float]:
    """Accuracy, macro-F1 and per-class precision, recall and F1."""
    labels = list(CLASSES)
    out = {"accuracy": accuracy_score(y_true, y_pred),
           "macro_f1": f1_score(y_true, y_pred, average="macro")}
    for prefix, values in (
        ("precision", precision_score(y_true, y_pred, labels=labels, average=None, zero_division=0)),
        ("recall", recall_score(y_true, y_pred, labels=labels, average=None, zero_division=0)),
        ("f1", f1_score(y_true, y_pred, labels=labels, average=None, zero_division=0)),
    ):
        out.update({f"{prefix}_{c}": float(v) for c, v in zip(CLASSES, values)})
    return out


def confusion(y_true: pd.Series, y_pred: Any) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Confusion matrix in counts and normalised by row (rows sum to 1)."""
    labels = list(CLASSES)
    counts = confusion_matrix(y_true, y_pred, labels=labels)
    row_sums = counts.sum(axis=1, keepdims=True)
    normalised = np.divide(counts, row_sums, out=np.zeros_like(counts, dtype=float),
                           where=row_sums != 0)
    return (pd.DataFrame(counts, index=labels, columns=labels),
            pd.DataFrame(normalised, index=labels, columns=labels))


def importance(model: Any, X: pd.DataFrame, y: pd.Series, repeats: int = 5) -> pd.DataFrame:
    """Permutation importance of the original variables (macro-F1 drop)."""
    result = permutation_importance(model, X, y, scoring="f1_macro", n_repeats=repeats,
                                    random_state=RANDOM_STATE, n_jobs=-1)
    return (pd.DataFrame({"variable": X.columns, "importance_mean": result.importances_mean,
                          "importance_sd": result.importances_std})
            .sort_values("importance_mean", ascending=False).reset_index(drop=True))


def baseline_metrics(df: pd.DataFrame) -> dict[str, float]:
    """Majority-class baseline on the same partition (D-010 item 4)."""
    _, y = make_features_target(df)
    return metrics(y, np.full(len(y), y.mode().iloc[0]))


def evaluate(model_path: Path, partition: str, allow_test: bool, repeats: int,
             write: bool) -> dict[str, float]:
    if partition == "test_15" and not allow_test:
        raise SystemExit("test_15 is opened once, in US-12. Pass --allow-test when the model "
                         "is frozen; otherwise evaluate val_15 (D-012 item 4).")

    payload = __import__("joblib").load(model_path)
    model = payload["model"] if isinstance(payload, dict) else payload

    df = load_partition(partition)
    X, y = make_features_target(df)
    pred = model.predict(X)
    scores = metrics(y, pred)

    counts, normalised = confusion(y, pred)
    print(f"\n{partition}: {len(df)} rows, model {model_path.name}")
    print(f"accuracy {scores['accuracy']:.4f} | macro-F1 {scores['macro_f1']:.4f}")
    print(counts.to_string())
    print("\nnormalised by row:")
    print(normalised.round(3).to_string())

    baseline = baseline_metrics(df)
    print(f"\nbaseline (most frequent): accuracy {baseline['accuracy']:.4f} | "
          f"macro-F1 {baseline['macro_f1']:.4f}")

    if partition == "test_15":
        val = load_partition("val_15")
        X_val, y_val = make_features_target(val)
        val_scores = metrics(y_val, model.predict(X_val))
        print(f"\nvalidation reference: accuracy {val_scores['accuracy']:.4f} | "
              f"macro-F1 {val_scores['macro_f1']:.4f}")
        print(f"test - validation: accuracy {scores['accuracy'] - val_scores['accuracy']:+.4f} | "
              f"macro-F1 {scores['macro_f1'] - val_scores['macro_f1']:+.4f}")

    importance_table = importance(model, X, y, repeats=repeats)
    print("\npermutation importance (original variables, macro-F1 drop):")
    print(importance_table.round(4).to_string(index=False))

    if write:
        REPORTS_DIR.mkdir(exist_ok=True)
        scores_df = pd.DataFrame([{"partition": partition, **scores}])
        scores_df.to_csv(REPORTS_DIR / f"final_metrics_{partition}.csv", index=False)
        counts.to_csv(REPORTS_DIR / f"confusion_counts_{partition}.csv")
        normalised.to_csv(REPORTS_DIR / f"confusion_normalised_{partition}.csv")
        importance_table.to_csv(REPORTS_DIR / f"feature_importance_{partition}.csv", index=False)
        print(f"\nwritten to {REPORTS_DIR.relative_to(ROOT)}/ (metrics, confusion, importance)")
    return scores


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--model", type=Path, required=True,
                        help="joblib file written by src.compare_models --stage freeze")
    parser.add_argument("--partition", choices=["val_15", "test_15"], required=True)
    parser.add_argument("--allow-test", action="store_true",
                        help="required to evaluate test_15; use it once, after the freeze")
    parser.add_argument("--repeats", type=int, default=5, help="permutation repeats")
    parser.add_argument("--no-write", action="store_true",
                        help="print the results without writing the report files")
    args = parser.parse_args(argv)

    if not args.model.exists():
        print(f"error: {args.model} not found; freeze the model first "
              "(python -m src.compare_models --stage freeze --model <name>)", file=sys.stderr)
        return 2
    evaluate(args.model, args.partition, args.allow_test, args.repeats, write=not args.no_write)
    return 0


if __name__ == "__main__":
    sys.exit(main())

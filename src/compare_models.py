"""Compare the four models and freeze the winner (US-11, issue #27).

Two stages, run from the repository root:

    python -m src.compare_models --stage table
    python -m src.compare_models --stage freeze --model svm

Stage ``table``
    Reads the recorded results files, keeps the rows each owner marked as the
    chosen configuration (``tuned``/``SELECTED``/``CANDIDATO``) of the last
    batch, and prints the D-010 comparison table: accuracy and macro-F1 on
    ``train_70`` and ``val_15``, the train - validation gap in points and the
    per-class F1 on validation. The model with the highest validation macro-F1
    among those whose gap is below 5 points is the winner (D-010 Consequences
    read as the comparison **between** models; the choice of configuration
    inside each model follows D-015).
Stage ``freeze``
    Refits the winner with its frozen configuration on ``train_70`` (or on
    ``train_70 + val_15`` with ``--train-with train_and_val``), serialises the
    whole Pipeline with joblib, reloads it in a fresh object and predicts one
    row, as US-11 requires. The file is written to ``models/``.

The comparison is only as good as the results files: a model whose file has no
marked chosen configuration is skipped with a message, because US-11 must be
auditable and the registry is append-only. At the time of writing only the SVM
module exposes ``SELECTED_PARAMS``; the registry grows as the other model PRs
merge.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.preprocessing import LabelEncoder

from src.config import TARGET
from src.frozen import FrozenPipeline
from src.preprocessing import make_features_target

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
MODELS_DIR = ROOT / "models"
COMPARISON_PATH = RESULTS_DIR / "model_comparison.csv"
MAX_ACCURACY_GAP = 0.05  # D-010 item 3
CLASSES = ("A", "B", "C", "D")

# Results files of the project, in the order they are reported.
RESULTS_FILES = {
    "logistic_regression": "logistic_regression.csv",
    "svm": "svm.csv",
    "random_forest": "random_forest.csv",
    "boosting": "boosting.csv",
}

# A row is the chosen configuration when its label starts with "tuned" (random
# forest, SVM) or its notes mark it. The logistic regression labels the chosen
# configuration with its hyperparameters (`C=1_l2_balanced`) and writes
# "D-015 selected configuration" / "seleccionada" in the notes.
CHOSEN_PREFIXES = ("tuned",)
CHOSEN_NOTES = ("SELECTED", "selected", "seleccionada", "CANDIDATO")

# model name -> how to build its Pipeline. ``call`` is "kwargs" when the
# builder takes keyword arguments and "dict" when it takes one parameter dict.
# Every module must expose ``SELECTED_PARAMS`` so the frozen model cannot drift
# from the recorded run; the SVM does, and the other three add it when their PR
# merges (the comparison reports which ones are ready).
FROZEN_MODELS = {
    "svm": {"module": "src.train_svm", "builder": "build_model", "call": "kwargs"},
    "boosting": {"module": "src.train_boosting", "builder": "build_pipeline", "call": "dict"},
    "random_forest": {"module": "src.train_random_forest", "builder": "build_model", "call": "kwargs"},
    "logistic_regression": {"module": "src.model_logreg", "builder": "build_logreg_pipeline",
                           "call": "kwargs"},
}

TABLE_COLUMNS = [
    "model", "config", "accuracy_train", "accuracy_val", "macro_f1_train",
    "macro_f1_val", "gap_pp", "f1_A", "f1_B", "f1_C", "f1_D", "source",
]


# --- Table -------------------------------------------------------------------

def _is_chosen(row: pd.Series) -> bool:
    config = str(row.get("config", ""))
    notes = str(row.get("notes", ""))
    if "fallback" in config.lower() or "fallback" in notes.lower():
        return False  # D-015 item 7 reserves "tuned-fallback-N" for a failed official check
    return config.startswith(CHOSEN_PREFIXES) or any(mark in notes for mark in CHOSEN_NOTES)


def load_selected_rows(path: Path) -> tuple[pd.Series, pd.Series] | None:
    """Return the chosen configuration's train_70 and val_15 rows, or None.

    Of the last batch, the **last** marked configuration that has both rows is
    used, so a fallback left in the file cannot be mistaken for the choice.
    """
    df = pd.read_csv(path)
    chosen = df[df.apply(_is_chosen, axis=1)]
    if chosen.empty:
        return None
    batch = chosen["run_timestamp_utc"].max()
    chosen = chosen[chosen["run_timestamp_utc"] == batch]
    for config in chosen["config"].drop_duplicates().tolist()[::-1]:
        rows = chosen[chosen["config"] == config]
        partitions = dict(zip(rows["partition"], rows.index))
        if "train_70" in partitions and "val_15" in partitions:
            return rows.loc[partitions["train_70"]], rows.loc[partitions["val_15"]]
    return None


def model_row(name: str, path: Path) -> dict[str, Any] | None:
    """One comparison row for a model, or None when the file cannot provide it."""
    rows = load_selected_rows(path)
    if rows is None:
        return None
    train_row, val_row = rows
    row = {
        "model": name,
        "config": train_row["config"],
        "accuracy_train": float(train_row["accuracy"]),
        "accuracy_val": float(val_row["accuracy"]),
        "macro_f1_train": float(train_row["macro_f1"]),
        "macro_f1_val": float(val_row["macro_f1"]),
        "gap_pp": (float(train_row["accuracy"]) - float(val_row["accuracy"])) * 100,
        "source": path.name,
    }
    row.update({f"f1_{c}": float(val_row[f"f1_{c}"]) for c in CLASSES})
    return row


def baseline_row(results_dir: Path) -> dict[str, Any] | None:
    """Majority-class baseline (D-010 item 4), read from any file that records it."""
    for name in RESULTS_FILES.values():
        path = results_dir / name
        if not path.exists():
            continue
        df = pd.read_csv(path)
        dummy = df[(df["config"].astype(str).str.startswith("baseline_dummy"))
                   & (df["partition"] == "val_15")]
        if dummy.empty:
            continue
        val = dummy.iloc[-1]
        return {"model": "baseline_dummy", "config": "most_frequent",
                "accuracy_val": float(val["accuracy"]), "macro_f1_val": float(val["macro_f1"]),
                "source": path.name}
    return None


def build_table(results_dir: Path) -> tuple[pd.DataFrame, list[str]]:
    """Comparison table plus the list of skipped models with their reason."""
    rows, skipped = [], []
    for name, filename in RESULTS_FILES.items():
        path = results_dir / filename
        if not path.exists():
            skipped.append(f"{name}: {filename} not found")
            continue
        row = model_row(name, path)
        if row is None:
            skipped.append(f"{name}: no chosen configuration marked in {filename} "
                           "(add a `tuned`/`SELECTED` pair of rows)")
            continue
        rows.append(row)
    table = pd.DataFrame(rows, columns=[c for c in TABLE_COLUMNS if c in (rows[0] if rows else {})])
    return table, skipped


def choose_model(table: pd.DataFrame) -> tuple[pd.Series, str]:
    """Best validation macro-F1 among the models whose gap is below 5 points."""
    eligible = table[table["gap_pp"] < MAX_ACCURACY_GAP * 100]
    if eligible.empty:
        raise SystemExit("no model meets the 5-point gap; declare it before US-11 (issue #27)")
    best = eligible.sort_values("macro_f1_val", ascending=False).iloc[0]
    reason = (f"{best['model']} has the highest val_15 macro-F1 ({best['macro_f1_val']:.4f}) "
              f"among {len(eligible)}/{len(table)} models with gap < 5 points")
    return best, reason


# --- Freeze ------------------------------------------------------------------

def frozen_pipeline(model: str) -> Any:
    """Build the winner's Pipeline with its frozen configuration."""
    if model not in FROZEN_MODELS:
        raise SystemExit(f"unknown model '{model}'; known: {sorted(FROZEN_MODELS)}")
    spec = FROZEN_MODELS[model]
    try:
        module = __import__(spec["module"], fromlist=[spec["builder"]])
    except ImportError:
        raise SystemExit(
            f"cannot freeze '{model}': {spec['module']} is not in develop yet; "
            "merge its PR first."
        ) from None
    if not hasattr(module, "SELECTED_PARAMS"):
        raise SystemExit(
            f"cannot freeze '{model}': {spec['module']} does not expose SELECTED_PARAMS. "
            "The owner adds the constant with the configuration recorded in their results "
            "file (see src/train_svm.py), so the frozen model cannot drift from the run."
        )
    params = dict(getattr(module, "SELECTED_PARAMS"))
    builder = getattr(module, spec["builder"])
    return builder(**params) if spec["call"] == "kwargs" else builder(params)


def freeze(model: str, output: Path, train_with: str = "train_70") -> Path:
    """Fit, serialise and reload the Pipeline; return the written path."""
    import joblib

    frames = {"train_70": pd.read_csv(ROOT / "data" / "train_70.csv")}
    if train_with == "train_and_val":
        frames["val_15"] = pd.read_csv(ROOT / "data" / "val_15.csv")
    data = pd.concat(frames.values(), ignore_index=True)
    X, y = make_features_target(data)

    pipeline = FrozenPipeline(frozen_pipeline(model)).fit(X, y)
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": pipeline, "frozen_params": _params_of(model),
                 "trained_on": train_with, "rows": len(data)}, output)

    reloaded = joblib.load(output)["model"]
    sample = X.iloc[[0]]
    print(f"frozen {model} -> {output.relative_to(ROOT)} "
          f"({len(data)} rows, target={TARGET})")
    print(f"reloaded prediction for the first row: {reloaded.predict(sample)[0]}")
    return output


def _params_of(model: str) -> dict[str, Any]:
    spec = FROZEN_MODELS[model]
    module = __import__(spec["module"], fromlist=[spec["builder"]])
    return dict(getattr(module, "SELECTED_PARAMS"))


# --- CLI ---------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--stage", choices=["table", "freeze"], required=True)
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    parser.add_argument("--write", action="store_true",
                        help="write the table to results/model_comparison.csv")
    parser.add_argument("--model", help="model to freeze (stage freeze)")
    parser.add_argument("--output", type=Path, default=MODELS_DIR / "final_model.joblib")
    parser.add_argument("--train-with", choices=["train_70", "train_and_val"],
                        default="train_70",
                        help="fit only on train_70 (default) or on train_70 + val_15 "
                             "(the team decides; issue #27)")
    args = parser.parse_args(argv)

    if args.stage == "freeze":
        if not args.model:
            parser.error("--model is required with --stage freeze")
        freeze(args.model, args.output, args.train_with)
        return 0

    table, skipped = build_table(args.results_dir)
    for note in skipped:
        print(f"skipped -> {note}")
    if table.empty:
        print("no model could be compared yet", file=sys.stderr)
        return 2

    pd.set_option("display.width", 200)
    print("\n" + table.to_string(index=False, float_format=lambda value: f"{value:.4f}"))

    baseline = baseline_row(args.results_dir)
    if baseline:
        print(f"\nreference: {baseline['model']} -> accuracy {baseline['accuracy_val']:.4f}, "
              f"macro-F1 {baseline['macro_f1_val']:.4f}")

    best, reason = choose_model(table)
    print(f"\nwinner: {reason}")

    if args.write:
        COMPARISON_PATH.parent.mkdir(exist_ok=True)
        table.to_csv(COMPARISON_PATH, index=False)
        print(f"table written to {COMPARISON_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

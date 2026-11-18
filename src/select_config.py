"""Common configuration-selection rule (D-015, US-11 issue #27).

D-015 (Approved by Brian on 2026-11-17) fixes one rule for the four models:

1. Compare configurations with 5-fold stratified cross-validation on
   ``train_70``, passing the full Pipeline inside every fold (D-010 item 6).
2. Admissible: train - CV accuracy gap below 5 points.
3. Tie band: every admissible configuration whose CV macro-F1 is within one
   standard error of the best one (fold standard deviation / sqrt(5), computed
   as NumPy's ``std`` does) is treated as tied.
4. Among the tied ones, the smallest train - CV gap wins; if equal, the highest
   CV macro-F1.
5. If no configuration is admissible, the smallest gap is chosen and the record
   states it (D-015 item 6).

The rule only needs the cross-validation rows of a model's results file, which
D-015 item 8 requires to carry the fold standard deviation and the train - CV
gap in ``notes``. This module reads those notes, so any model owner can re-derive
their selection with one command:

    python -m src.select_config results/boosting.csv

It prints the chosen configuration and the reason, or a clear error when the
file does not carry the fields D-015 item 8 requires.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

__all__ = ["cv_table", "select_configuration", "rederive", "MAX_ACCURACY_GAP", "CV_FOLDS"]

MAX_ACCURACY_GAP = 0.05  # D-010 item 3, applied to the train - CV gap (D-015 item 2)
CV_FOLDS = 5  # D-010 item 6

# Notes formats in use: the SVM and random forest write "sd macro-F1 0.0081;
# ... train - CV gap 1.70 pts", the boosting file writes "mean macro_f1 across
# folds=0.5015 (sd 0.0091); ... gap in-fold vs CV=17.89 pp".
_SD_PATTERNS = (
    r"sd macro-F1 ([\d.]+)",
    r"mean macro_f1 across folds=[\d.]+ \(sd ([\d.]+)\)",
    r"sd macro[- ]?f1[=: ]([\d.]+)",
    r"macro_f1_std\s*=\s*([+-]?[\d.]+)",
)
_GAP_PATTERNS = (
    r"train - CV gap ([\d.]+) pts",
    r"train-CV gap ([\d.]+) pts",
    r"gap in-fold vs CV=([\d.]+) pp",
    r"gap in-fold vs CV=([\d.]+) pts",
    r"train_cv_acc_gap\s*=\s*([+-]?[\d.]+)\s*pp",
)


def parse_cv_notes(notes: str) -> dict[str, float]:
    """Extract the fold standard deviation and the train - CV gap from ``notes``.

    Raises ``ValueError`` with an actionable message when either number is
    missing, because D-015 cannot be applied without them (item 8).
    """
    text = "" if notes is None or (isinstance(notes, float) and np.isnan(notes)) else str(notes)
    sd = _first_number(text, _SD_PATTERNS)
    gap = _first_number(text, _GAP_PATTERNS)
    missing = [name for name, value in (("fold sd of macro-F1", sd),
                                        ("train - CV gap in points", gap)) if value is None]
    if missing:
        raise ValueError(
            "the cv5fold row does not record " + " and ".join(missing)
            + " in `notes`; D-015 item 8 requires them (see the wording used by "
              "src/train_svm.py). Re-run the CV and record them before re-deriving."
        )
    return {"cv_macro_f1_sd": sd, "train_cv_gap": gap / 100.0}


def _first_number(text: str, patterns: tuple[str, ...]) -> float | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def _fold_mean(notes: str) -> float | None:
    """Mean macro-F1 across folds, when ``notes`` record it (D-015 item 2)."""
    if notes is None or (isinstance(notes, float) and np.isnan(notes)):
        return None
    return _first_number(str(notes), (r"mean macro_f1 across folds=([\d.]+)",
                                      r"mean of \d+ folds[^;]*macro-F1 ([\d.]+)"))


def cv_table(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-validation table of one model: last row per configuration.

    Two hygiene rules, both from the review of PR #72:

    * the ``baseline`` rows are not candidate configurations, so they are left
      out of the table (they made the SVM report 6/10 instead of 6/9);
    * when the ``notes`` carry the mean of the fold scores, that mean is used
      instead of the row's ``macro_f1`` column, because D-015 item 2 asks for
      the mean of the five folds and some files store the pooled out-of-fold
      score in the column (the boosting file does).

    Files are append-only and may hold several batches; keeping the last row of
    each configuration makes a re-run supersede the earlier one.
    """
    cv = df[df["partition"] == "cv5fold"].copy()
    if cv.empty:
        raise ValueError("the results file has no cv5fold rows")
    cv = cv[~cv["config"].astype(str).str.startswith("baseline")]
    if cv.empty:
        raise ValueError("the results file only has baseline cv5fold rows")
    cv = cv.sort_values("run_timestamp_utc").drop_duplicates(subset=["config"], keep="last")
    parsed = cv["notes"].map(parse_cv_notes).apply(pd.Series).reset_index(drop=True)
    fold_mean = pd.to_numeric(cv["notes"].map(_fold_mean), errors="coerce").reset_index(drop=True)
    table = pd.concat([cv[["config", "accuracy", "macro_f1"]].reset_index(drop=True), parsed], axis=1)
    table = table.rename(columns={"accuracy": "cv_accuracy", "macro_f1": "cv_macro_f1"})
    has_mean = fold_mean.notna()
    if has_mean.any():
        table.loc[has_mean.to_numpy(), "cv_macro_f1"] = fold_mean[has_mean].astype(float).to_numpy()
    return table


def select_configuration(table: pd.DataFrame) -> tuple[pd.Series, str]:
    """Apply D-015 to a CV table; return the chosen row and the reason."""
    eligible = table[table["train_cv_gap"] < MAX_ACCURACY_GAP]
    if eligible.empty:
        best = table.sort_values("train_cv_gap").iloc[0]
        return best, ("no configuration meets the 5-point gap in cross-validation; "
                      "the smallest train - CV gap is chosen and the limitation is declared "
                      "(D-015 item 6)")
    top = eligible.sort_values("cv_macro_f1", ascending=False).iloc[0]
    std_error = top["cv_macro_f1_sd"] / np.sqrt(CV_FOLDS)
    tied = eligible[eligible["cv_macro_f1"] >= top["cv_macro_f1"] - std_error]
    best = tied.sort_values(["train_cv_gap", "cv_macro_f1"], ascending=[True, False]).iloc[0]
    word = "configuration" if len(tied) == 1 else "configurations"
    reason = (f"smallest train - CV gap among {len(tied)} {word} within one standard error "
              f"({std_error:.4f}) of the best CV macro-F1 ({top['cv_macro_f1']:.4f}); "
              f"{len(eligible)}/{len(table)} admissible with gap < 5 points")
    return best, reason


def rederive(results_path: str | Path) -> tuple[pd.Series, str]:
    """Read a model's results file and apply D-015 to its CV rows."""
    df = pd.read_csv(results_path)
    return select_configuration(cv_table(df))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("results", type=Path, help="model results file, e.g. results/boosting.csv")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    try:
        best, reason = rederive(args.results)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"config": best["config"], "reason": reason,
                          "cv_macro_f1": float(best["cv_macro_f1"]),
                          "cv_macro_f1_sd": float(best["cv_macro_f1_sd"]),
                          "train_cv_gap": float(best["train_cv_gap"])}, indent=2))
    else:
        print(f"file:   {args.results}")
        print(f"chosen: {best['config']}")
        print(f"CV macro-F1 {best['cv_macro_f1']:.4f} (sd {best['cv_macro_f1_sd']:.4f}), "
              f"train - CV gap {best['train_cv_gap'] * 100:.2f} points")
        print(f"reason: {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

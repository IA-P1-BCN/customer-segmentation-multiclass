"""Tests for the common D-015 selection rule (US-11, issue #27).

Run from the repository root:

    python -m pytest tests/test_select_config.py
"""

from __future__ import annotations

import pandas as pd
import pytest

from src import select_config as sc

SVM_NOTES = ("mean of 5 folds; sd accuracy 0.0149, sd macro-F1 0.0173; "
             "in-fold train accuracy 0.5151; train - CV gap 1.38 pts; "
             "selection rule: D-015 (approved 2026-11-17)")
BOOSTING_NOTES = ("5-fold stratified CV on train_70; mean accuracy across folds=0.5215 "
                  "(sd 0.0111); mean macro_f1 across folds=0.5045 (sd 0.0091); "
                  "in-fold train accuracy=0.5834; gap in-fold vs CV=6.19 pp; "
                  "row metrics are out-of-fold predictions")


@pytest.mark.parametrize("notes,sd,gap", [
    (SVM_NOTES, 0.0173, 0.0138),
    (BOOSTING_NOTES, 0.0091, 0.0619),
])
def test_parse_cv_notes_reads_both_formats_in_use(notes, sd, gap):
    parsed = sc.parse_cv_notes(notes)
    assert parsed["cv_macro_f1_sd"] == pytest.approx(sd)
    assert parsed["train_cv_gap"] == pytest.approx(gap)


def test_parse_cv_notes_reads_the_logistic_format():
    """The logistic notebook records macro_f1_std= and train_cv_acc_gap= in points."""
    note = ("PROVISIONAL | D-015 cv5fold media de 5 scores de fold; accuracy_std=0.010500; "
            "macro_f1_std=0.010076; train_cv_acc_gap=+1.38 pp")
    parsed = sc.parse_cv_notes(note)
    assert parsed["cv_macro_f1_sd"] == pytest.approx(0.010076)
    assert parsed["train_cv_gap"] == pytest.approx(0.0138)


def test_parse_cv_notes_explains_what_is_missing():
    with pytest.raises(ValueError, match="fold sd of macro-F1"):
        sc.parse_cv_notes("OOF StratifiedKFold(5, seed src.config)")


def _file(rows):
    return pd.DataFrame(rows, columns=["run_timestamp_utc", "config", "partition",
                                       "accuracy", "macro_f1", "notes"])


def test_cv_table_keeps_the_last_batch_of_each_configuration():
    df = _file([
        ("2026-11-16T10:00:00Z", "a", "cv5fold", 0.50, 0.40, SVM_NOTES),
        ("2026-11-17T10:00:00Z", "a", "cv5fold", 0.52, 0.48, SVM_NOTES),
        ("2026-11-17T10:00:00Z", "b", "cv5fold", 0.51, 0.47, SVM_NOTES),
        ("2026-11-17T10:00:00Z", "a", "val_15", 0.50, 0.45, "other"),
    ])
    table = sc.cv_table(df)
    assert len(table) == 2
    assert table.loc[table["config"] == "a", "cv_macro_f1"].iloc[0] == pytest.approx(0.48)


def test_cv_table_leaves_the_baseline_out():
    """The baseline is a reference, not a candidate configuration (review of PR #72)."""
    df = _file([
        ("2026-11-17T10:00:00Z", "baseline {}", "cv5fold", 0.51, 0.49, SVM_NOTES),
        ("2026-11-17T10:00:00Z", "grid-01", "cv5fold", 0.50, 0.48, SVM_NOTES),
    ])
    table = sc.cv_table(df)
    assert list(table["config"]) == ["grid-01"]


def test_cv_table_prefers_the_fold_mean_over_the_pooled_oof_column():
    """D-015 item 2: mean of the folds, not the pooled out-of-fold score."""
    df = _file([
        ("2026-11-17T10:00:00Z", "refine_x", "cv5fold", 0.5215, 0.5049, BOOSTING_NOTES),
    ])
    table = sc.cv_table(df)
    assert table["cv_macro_f1"].iloc[0] == pytest.approx(0.5045)


def test_selection_breaks_ties_by_smallest_gap():
    table = pd.DataFrame([
        ("overfits", 0.5300, 0.0100, 0.0800),
        ("best", 0.5100, 0.0100, 0.0490),
        ("tied", 0.5070, 0.0100, 0.0300),
        ("too_low", 0.5000, 0.0100, 0.0100),
    ], columns=["config", "cv_macro_f1", "cv_macro_f1_sd", "train_cv_gap"])
    best, reason = sc.select_configuration(table)
    assert best["config"] == "tied"
    assert "2 configurations within one standard error" in reason
    assert "3/4 admissible" in reason


def test_selection_declares_when_nothing_is_admissible():
    table = pd.DataFrame([
        ("a", 0.5200, 0.0050, 0.0900),
        ("b", 0.5000, 0.0050, 0.0600),
    ], columns=["config", "cv_macro_f1", "cv_macro_f1_sd", "train_cv_gap"])
    best, reason = sc.select_configuration(table)
    assert best["config"] == "b"
    assert "no configuration meets" in reason


def test_rederive_reads_a_results_file(tmp_path):
    path = tmp_path / "svm.csv"
    _file([
        ("2026-11-17T10:00:00Z", "grid-01", "cv5fold", 0.50, 0.48, SVM_NOTES),
        ("2026-11-17T10:00:00Z", "grid-02", "cv5fold", 0.49, 0.47, SVM_NOTES),
    ]).to_csv(path, index=False)
    best, reason = sc.rederive(path)
    assert best["config"] == "grid-01"
    assert "admissible" in reason


def test_rederive_reports_missing_fields(tmp_path):
    path = tmp_path / "logistic.csv"
    _file([("2026-11-17T10:00:00Z", "C=0.1_l2", "cv5fold", 0.50, 0.48,
            "OOF StratifiedKFold(5, seed src.config)")]).to_csv(path, index=False)
    with pytest.raises(ValueError, match="D-015 item 8"):
        sc.rederive(path)

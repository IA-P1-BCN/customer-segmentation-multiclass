"""Tests for the model comparison and freeze script (US-11, issue #27).

Run from the repository root:

    python -m pytest tests/test_compare_models.py
"""

from __future__ import annotations

import pandas as pd
import pytest

from src import compare_models as cm

COLUMNS = ["run_timestamp_utc", "config", "partition", "accuracy", "macro_f1",
           "f1_A", "f1_B", "f1_C", "f1_D", "notes"]


def _write(path, rows):
    pd.DataFrame(rows, columns=COLUMNS).to_csv(path, index=False)


def _chosen(timestamp, prefix="tuned", notes="SELECTED; ok"):
    return [
        (timestamp, f"{prefix} {{}}", "train_70", 0.55, 0.52, 0.4, 0.3, 0.5, 0.7, notes),
        (timestamp, f"{prefix} {{}}", "val_15", 0.52, 0.49, 0.4, 0.3, 0.5, 0.7, notes),
    ]


def test_load_selected_rows_takes_the_last_batch(tmp_path):
    path = tmp_path / "svm.csv"
    rows = [
        ("2026-11-16T10:00:00Z", "tuned {}", "train_70", 0.50, 0.47, 0.4, 0.3, 0.5, 0.7, "old"),
        ("2026-11-16T10:00:00Z", "tuned {}", "val_15", 0.48, 0.45, 0.4, 0.3, 0.5, 0.7, "old"),
        ("2026-11-17T10:00:00Z", "tuned {}", "train_70", 0.55, 0.52, 0.4, 0.3, 0.5, 0.7, "SELECTED"),
        ("2026-11-17T10:00:00Z", "tuned {}", "val_15", 0.52, 0.49, 0.4, 0.3, 0.5, 0.7, "SELECTED"),
    ]
    _write(path, rows)
    train, val = cm.load_selected_rows(path)
    assert train["accuracy"] == pytest.approx(0.55)
    assert val["partition"] == "val_15"


def test_load_selected_rows_returns_none_without_a_marker(tmp_path):
    path = tmp_path / "boosting.csv"
    _write(path, [("2026-11-16T10:00:00Z", "grid_a", "val_15", 0.5, 0.48, 0.4, 0.3, 0.5, 0.7, "plain")])
    assert cm.load_selected_rows(path) is None


def test_model_row_computes_the_gap_in_points(tmp_path):
    path = tmp_path / "svm.csv"
    _write(path, _chosen("2026-11-17T10:00:00Z"))
    row = cm.model_row("svm", path)
    assert row["model"] == "svm"
    assert row["gap_pp"] == pytest.approx(3.0)
    assert set(row) >= {"f1_A", "f1_B", "f1_C", "f1_D"}


def test_build_table_skips_missing_and_unmarked_files(tmp_path):
    _write(tmp_path / "svm.csv", _chosen("2026-11-17T10:00:00Z"))
    _write(tmp_path / "boosting.csv",
           [("2026-11-16T10:00:00Z", "grid_a", "val_15", 0.5, 0.48, 0.4, 0.3, 0.5, 0.7, "plain")])
    table, skipped = cm.build_table(tmp_path)
    assert list(table["model"]) == ["svm"]
    assert any("boosting: no chosen configuration" in note for note in skipped)
    assert any("logistic_regression" in note for note in skipped)


def test_load_selected_rows_accepts_the_logistic_marker(tmp_path):
    """The logistic labels the choice with its hyperparameters and a D-015 note."""
    path = tmp_path / "logistic_regression.csv"
    note = "D-015 selected configuration; official check on the val_15 row of this run"
    rows = [
        ("2026-11-17T11:15:23Z", "C=1_l2_balanced", "train_70", 0.51, 0.50, 0.4, 0.3, 0.5, 0.7, note),
        ("2026-11-17T11:15:23Z", "C=1_l2_balanced", "val_15", 0.50, 0.48, 0.4, 0.3, 0.5, 0.7, note),
    ]
    _write(path, rows)
    train, val = cm.load_selected_rows(path)
    assert train["config"] == "C=1_l2_balanced"
    assert val["partition"] == "val_15"


def test_choose_model_ignores_the_overfit_model(tmp_path):
    table = pd.DataFrame([
        {"model": "a", "gap_pp": 12.0, "macro_f1_val": 0.60},
        {"model": "b", "gap_pp": 2.0, "macro_f1_val": 0.49},
    ])
    best, reason = cm.choose_model(table)
    assert best["model"] == "b"
    assert "1/2 models with gap < 5" in reason


def test_choose_model_stops_when_nothing_is_admissible():
    table = pd.DataFrame([{"model": "a", "gap_pp": 9.0, "macro_f1_val": 0.60}])
    with pytest.raises(SystemExit, match="no model meets"):
        cm.choose_model(table)


def test_frozen_pipeline_explains_which_modules_are_ready():
    with pytest.raises(SystemExit, match="unknown model"):
        cm.frozen_pipeline("nope")
    # The boosting module is not in develop yet, so the registry knows it but
    # cannot import it: the message says so instead of failing with an ImportError.
    with pytest.raises(SystemExit, match="is not in develop yet"):
        cm.frozen_pipeline("boosting")


def test_fallback_rows_are_not_mistaken_for_the_choice(tmp_path):
    path = tmp_path / "random_forest.csv"
    rows = [
        ("2026-11-17T10:00:00Z", "tuned-fallback-1 {}", "train_70", 0.60, 0.55, 0.4, 0.3, 0.5, 0.7, "failed the official check"),
        ("2026-11-17T10:00:00Z", "tuned-fallback-1 {}", "val_15", 0.55, 0.50, 0.4, 0.3, 0.5, 0.7, "failed the official check"),
        ("2026-11-17T10:00:00Z", "tuned {}", "train_70", 0.54, 0.51, 0.4, 0.3, 0.5, 0.7, "SELECTED"),
        ("2026-11-17T10:00:00Z", "tuned {}", "val_15", 0.52, 0.49, 0.4, 0.3, 0.5, 0.7, "SELECTED"),
    ]
    _write(path, rows)
    train, _ = cm.load_selected_rows(path)
    assert train["config"] == "tuned {}"

"""Structural tests for the SVM training script (US-10, issue #22).

They check the wiring (data checks, preprocessing width, scaler, seed, results
format, selection rules), not model quality: metrics are recorded by executed
runs in ``results/svm.csv``.

Run from the repository root:

    python -m pytest tests/test_train_svm.py
"""

from __future__ import annotations

import csv

import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import StratifiedKFold

from src import train_svm as svm
from src.config import RANDOM_STATE
from src.preprocessing import make_features_target


@pytest.fixture(scope="module")
def frames():
    return svm.load_partitions()


def test_partitions_have_expected_rows(frames):
    assert len(frames["train_70"]) == 5647
    assert len(frames["val_15"]) == 1210
    assert "test_15" not in frames  # the test split is never loaded here


def test_sha256_ignores_line_endings(tmp_path):
    lf, crlf = tmp_path / "lf.csv", tmp_path / "crlf.csv"
    lf.write_bytes(b"a,b\n1,2\n")
    crlf.write_bytes(b"a,b\r\n1,2\r\n")
    assert svm._sha256_lf(lf) == svm._sha256_lf(crlf)


def test_preprocessor_output_is_numeric_and_complete(frames):
    X_train, _ = make_features_target(frames["train_70"])
    X_val, _ = make_features_target(frames["val_15"])
    prep = svm.build_preprocessor()
    train_t = prep.fit_transform(X_train)
    val_t = prep.transform(X_val)
    # D-011 + D-014 on train_70: 3 numeric + 2 missing indicators + 2 binary
    # + 1 Gender + 10 Profession (with "Unknown") + 7 Var_1 + 3 Spending_Score.
    assert train_t.shape == (5647, 28)
    assert val_t.shape == (1210, 28)
    assert not np.isnan(np.asarray(train_t, dtype=float)).any()
    assert not np.isnan(np.asarray(val_t, dtype=float)).any()


def test_profession_unknown_level_is_created(frames):
    X_train, _ = make_features_target(frames["train_70"])
    names = svm.build_preprocessor().fit(X_train).get_feature_names_out()
    assert "Profession_Unknown" in names


def test_pipeline_scales_before_the_estimator_and_uses_the_global_seed():
    model = svm.build_model(C=3.0)
    assert [name for name, _ in model.steps] == ["preprocessing", "scaler", "model"]
    assert model.named_steps["model"].random_state == RANDOM_STATE
    assert model.named_steps["model"].C == 3.0


def test_grid_declares_kernels_and_gamma_only_for_rbf():
    kernels = {config["kernel"] for config in svm.TUNING_GRID}
    assert kernels == {"linear", "rbf"}
    for config in svm.TUNING_GRID:
        assert ("gamma" in config) == (config["kernel"] == "rbf")
        assert "C" in config


def test_evaluate_returns_d010_metrics(frames):
    sample = frames["train_70"].sample(n=300, random_state=RANDOM_STATE)
    X, y = make_features_target(sample)
    model = svm.build_model(kernel="linear", C=1.0).fit(X, y)
    metrics = svm.evaluate(model, X, y)
    assert set(metrics) == {"accuracy", "macro_f1", "f1_A", "f1_B", "f1_C", "f1_D"}
    assert all(0.0 <= value <= 1.0 for value in metrics.values())


def test_append_results_is_append_only(tmp_path, monkeypatch):
    path = tmp_path / "results" / "svm.csv"
    monkeypatch.setattr(svm, "RESULTS_PATH", path)
    monkeypatch.setattr(svm, "ROOT", tmp_path)
    row = {"run_timestamp_utc": "2026-01-01T00:00:00Z", "seed": RANDOM_STATE,
           "model": "svm", "config": "x", "partition": "train_70",
           "accuracy": 0.123456, "macro_f1": 0.5}
    svm.append_results([row])
    svm.append_results([{**row, "partition": "val_15"}])
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert list(rows[0]) == svm.RESULT_COLUMNS
    assert [r["partition"] for r in rows] == ["train_70", "val_15"]
    assert rows[0]["accuracy"] == "0.1235"  # rounded to 4 decimals
    assert b"\r" not in path.read_bytes()  # LF line endings on every platform


def _cv_table(rows):
    return pd.DataFrame(
        rows,
        columns=["name", "cv_macro_f1", "cv_macro_f1_sd", "train_cv_gap"],
    )


def test_cv_selection_breaks_ties_by_smallest_gap():
    # Standard error of the best = 0.0100 / sqrt(5) = 0.0045 -> tie threshold 0.5055.
    table = _cv_table([
        ("overfits", 0.5300, 0.0100, 0.0800),  # best score but gap above the limit
        ("best", 0.5100, 0.0100, 0.0490),
        ("tied", 0.5070, 0.0100, 0.0300),      # within one standard error, smaller gap
        ("too_low", 0.5000, 0.0100, 0.0100),   # smallest gap but clearly worse
    ])
    best, reason = svm.select_cv(table)
    assert best["name"] == "tied"
    assert "2 configs within one standard error" in reason
    assert "3/4 configs" in reason


def test_cv_selection_keeps_best_when_nothing_is_tied():
    table = _cv_table([("best", 0.5200, 0.0050, 0.0400), ("worse", 0.5000, 0.0050, 0.0100)])
    assert svm.select_cv(table)[0]["name"] == "best"


def test_cv_selection_falls_back_to_smallest_gap():
    table = _cv_table([("a", 0.5200, 0.0050, 0.0900), ("b", 0.5000, 0.0050, 0.0600)])
    best, reason = svm.select_cv(table)
    assert best["name"] == "b"
    assert "no config met" in reason


def test_per_class_note_has_precision_recall_and_f1(frames):
    """D-010 Consequences: precision, recall and F1 per class on validation."""
    sample = frames["train_70"].sample(n=300, random_state=RANDOM_STATE)
    X, y = make_features_target(sample)
    model = svm.build_model(kernel="linear", C=1.0).fit(X, y)
    note = svm._per_class_note(y, model.predict(X))
    assert note.startswith("per-class val A P=")
    assert "R=" in note and "F1=" in note
    assert len(note.split(";")) == 4  # one block per class


def test_cv_helper_returns_a_cv5fold_row(frames):
    """The baseline records its CV row, so its train-CV gap is checkable."""
    sample = frames["train_70"].sample(n=300, random_state=RANDOM_STATE)
    X, y = make_features_target(sample)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
    row, summary = svm._cross_validate_config("baseline", {}, X, y, cv, "2026-01-01T00:00:00Z")
    assert row["partition"] == "cv5fold"
    assert row["notes"].startswith("mean of 3 folds")
    assert "train - CV gap" in row["notes"]
    assert {"cv_macro_f1", "cv_macro_f1_sd", "train_cv_gap"} <= set(summary)


def test_selected_params_come_from_the_grid():
    """The frozen configuration must be one of the recorded grid configurations."""
    assert svm.SELECTED_PARAMS in svm.TUNING_GRID
    model = svm.build_model(**svm.SELECTED_PARAMS)
    assert model.named_steps["model"].kernel == "rbf"


def test_cli_rejects_the_rejected_rule(monkeypatch):
    """Option A of D-015 is rejected, so --rule must not be accepted."""
    monkeypatch.setattr(svm, "load_partitions", lambda: {"train_70": None, "val_15": None})
    with pytest.raises(SystemExit):
        svm.main(["--stage", "tune", "--rule", "val"])


def test_cli_runs_tuning_without_a_rule_flag(monkeypatch):
    captured = {}
    monkeypatch.setattr(svm, "load_partitions", lambda: {"train_70": None, "val_15": None})
    monkeypatch.setattr(svm, "run_tuning", lambda frames, record: captured.update(ran=True))
    svm.main(["--stage", "tune", "--no-record"])
    assert captured["ran"]

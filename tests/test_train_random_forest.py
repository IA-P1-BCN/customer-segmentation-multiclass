"""Structural tests for the random forest training script (US-08, issue #20).

They check the wiring (data checks, preprocessing width, seed, results
format), not model quality: metrics are recorded by executed runs in
``results/random_forest.csv``.

Run from the repository root:

    python -m pytest tests/test_train_random_forest.py
"""

from __future__ import annotations

import csv

import numpy as np
import pytest

from src import train_random_forest as rf
from src.config import RANDOM_STATE
from src.preprocessing import make_features_target


@pytest.fixture(scope="module")
def frames():
    return rf.load_partitions()


def test_partitions_have_expected_rows(frames):
    assert len(frames["train_70"]) == 5647
    assert len(frames["val_15"]) == 1210
    assert "test_15" not in frames  # the test split is never loaded here


def test_sha256_ignores_line_endings(tmp_path):
    lf, crlf = tmp_path / "lf.csv", tmp_path / "crlf.csv"
    lf.write_bytes(b"a,b\n1,2\n")
    crlf.write_bytes(b"a,b\r\n1,2\r\n")
    assert rf._sha256_lf(lf) == rf._sha256_lf(crlf)


def test_preprocessor_output_is_numeric_and_complete(frames):
    X_train, _ = make_features_target(frames["train_70"])
    X_val, _ = make_features_target(frames["val_15"])
    prep = rf.build_preprocessor()
    train_t = prep.fit_transform(X_train)
    val_t = prep.transform(X_val)
    # D-011 + D-014 on train_70: 3 numeric + 2 missing indicators + 2 binary
    # + 2 Gender + 10 Profession (with "Unknown") + 7 Var_1 + 3 Spending_Score.
    assert train_t.shape == (5647, 29)
    assert val_t.shape == (1210, 29)
    assert not np.isnan(np.asarray(train_t, dtype=float)).any()
    assert not np.isnan(np.asarray(val_t, dtype=float)).any()


def test_profession_unknown_level_is_created(frames):
    X_train, _ = make_features_target(frames["train_70"])
    names = rf.build_preprocessor().fit(X_train).get_feature_names_out()
    assert "Profession_Unknown" in names


def test_model_uses_global_seed():
    model = rf.build_model(max_depth=3)
    assert model.named_steps["model"].random_state == RANDOM_STATE
    assert model.named_steps["model"].max_depth == 3


def test_evaluate_returns_d010_metrics(frames):
    X_train, y_train = make_features_target(frames["train_70"])
    model = rf.build_model(n_estimators=10, max_depth=3).fit(X_train, y_train)
    metrics = rf.evaluate(model, X_train, y_train)
    assert set(metrics) == {"accuracy", "macro_f1", "f1_A", "f1_B", "f1_C", "f1_D"}
    assert all(0.0 <= v <= 1.0 for v in metrics.values())


def test_append_results_is_append_only(tmp_path, monkeypatch):
    path = tmp_path / "results" / "random_forest.csv"
    monkeypatch.setattr(rf, "RESULTS_PATH", path)
    monkeypatch.setattr(rf, "ROOT", tmp_path)
    row = {"run_timestamp_utc": "2026-01-01T00:00:00Z", "seed": RANDOM_STATE,
           "model": "random_forest", "config": "x", "partition": "train_70",
           "accuracy": 0.123456, "macro_f1": 0.5}
    rf.append_results([row])
    rf.append_results([{**row, "partition": "val_15"}])
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert list(rows[0]) == rf.RESULT_COLUMNS
    assert [r["partition"] for r in rows] == ["train_70", "val_15"]
    assert rows[0]["accuracy"] == "0.1235"  # rounded to 4 decimals
    assert b"\r" not in path.read_bytes()  # LF line endings on every platform

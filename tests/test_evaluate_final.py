"""Tests for the final evaluation script (US-12, issue #29).

Run from the repository root:

    python -m pytest tests/test_evaluate_final.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression

from src import evaluate_final as ev


def test_partitions_match_d013_reference_values():
    assert ev.PARTITIONS["test_15"] == (
        1211, "33427fa164216da231584cabf690528de7c84145dfdb4b9fe273d201edfdbf86")
    assert set(ev.PARTITIONS) == {"train_70", "val_15", "test_15"}


def test_metrics_report_every_class():
    y = pd.Series(list("ABCD") * 5)
    scores = ev.metrics(y, y)
    assert scores["accuracy"] == 1.0
    assert set(scores) == ({"accuracy", "macro_f1"} |
                           {f"{p}_{c}" for p in ("precision", "recall", "f1") for c in "ABCD"})


def test_confusion_matrix_normalises_by_row():
    y = pd.Series(list("AABBC"))
    pred = np.array(list("AABBD"))
    counts, normalised = ev.confusion(y, pred)
    assert counts.loc["A", "A"] == 2
    assert normalised.loc["C", "D"] == 1.0
    assert np.allclose(normalised.loc[["A", "B", "C"]].sum(axis=1).values, 1.0)
    assert normalised.loc["D"].sum() == 0.0  # class absent from y: zeros, not NaN


def test_partition_is_refused_without_the_flag():
    with pytest.raises(SystemExit, match="--allow-test"):
        ev.evaluate(Path("unused.joblib"), "test_15", allow_test=False, repeats=1, write=False)


def test_load_partition_verifies_the_checksum(monkeypatch):
    monkeypatch.setitem(ev.PARTITIONS, "val_15", (1210, "0" * 64))
    with pytest.raises(RuntimeError, match="D-013"):
        ev.load_partition("val_15")


def test_importance_ranks_the_original_variables():
    rng = np.random.RandomState(0)
    X = pd.DataFrame(rng.rand(200, 4),
                     columns=["Age", "Work_Experience", "Family_Size", "Spending_Score"])
    y = pd.Series(np.where(X["Age"] > 0.5, "A", "B"))
    model = LogisticRegression(max_iter=300).fit(X, y)
    table = ev.importance(model, X, y, repeats=2)
    assert set(table["variable"]) == set(X.columns)  # one row per original variable
    assert table["importance_mean"].is_monotonic_decreasing
    assert "Age" == table["variable"].iloc[0]


def test_baseline_is_the_majority_class():
    df = pd.DataFrame({
        "Segmentation": list("AAAAB"),
        "Age": [1, 2, 3, 4, 5],
        "Work_Experience": [1.0] * 5,
        "Family_Size": [1.0] * 5,
        "Ever_Married": ["Yes"] * 5,
        "Graduated": ["Yes"] * 5,
        "Gender": ["Male"] * 5,
        "Profession": ["Doctor"] * 5,
        "Var_1": ["Cat_6"] * 5,
        "Spending_Score": ["Low"] * 5,
    })
    scores = ev.baseline_metrics(df)
    assert scores["accuracy"] == pytest.approx(0.8)


def test_importance_runs_on_validation_and_not_on_test_by_default():
    assert ev.wants_importance("val_15", False) is True
    assert ev.wants_importance("test_15", False) is False
    assert ev.wants_importance("test_15", True) is True


def test_a_second_test_evaluation_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(ev, "REPORTS_DIR", tmp_path)
    (tmp_path / "final_metrics_test_15_20261117T090000Z.csv").write_text("partition\n")
    with pytest.raises(SystemExit, match="previous evaluation of test_15"):
        ev.evaluate(Path("unused.joblib"), "test_15", allow_test=True, repeats=1, write=False)


def test_a_model_fitted_on_train_and_val_cannot_be_scored_on_val(tmp_path):
    import joblib
    model_path = tmp_path / "final_model.joblib"
    joblib.dump({"model": LogisticRegression(), "trained_on": "train_and_val"}, model_path)
    with pytest.raises(SystemExit, match="not held out"):
        ev.evaluate(model_path, "val_15", allow_test=False, repeats=1, write=False)

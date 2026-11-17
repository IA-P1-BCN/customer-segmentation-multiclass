"""Tests for the reusable logistic regression pipeline (US-07)."""

from pathlib import Path

import pandas as pd
import pytest

from src import model_logreg
from src.model_logreg import build_logreg_pipeline, load_partitions
from src.preprocessing import make_features_target

ROOT = Path(__file__).resolve().parents[1]


def test_feature_names_have_no_internal_imputer_prefixes():
    df = pd.read_csv(ROOT / "data" / "train_70.csv")
    X, y = make_features_target(df)

    model = build_logreg_pipeline()
    model.fit(X, y)

    names = list(model.named_steps["preprocessing"].get_feature_names_out())
    assert len(names) == 28
    assert "Gender_Male" in names
    assert "Profession_Artist" in names
    assert not any("__" in name for name in names)


def test_load_partitions_checks_d013_and_never_loads_test():
    frames = load_partitions()
    assert set(frames) == {"train_70", "val_15"}  # test_15 is never read here
    assert len(frames["train_70"]) == 5647
    assert len(frames["val_15"]) == 1210


def test_load_partitions_fails_on_a_checksum_mismatch(monkeypatch):
    monkeypatch.setitem(model_logreg.PARTITIONS, "val_15", (1210, "0" * 64))
    with pytest.raises(RuntimeError, match="D-013"):
        load_partitions()

"""Tests for the reusable logistic regression pipeline (US-07)."""

from pathlib import Path

import pandas as pd

from src.model_logreg import build_logreg_pipeline
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

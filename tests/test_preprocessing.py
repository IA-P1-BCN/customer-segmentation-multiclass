"""Structural tests for the shared preprocessing (US-05, issue #17).

Run from the repository root with:

    python -m pytest tests/test_preprocessing.py

These tests cover the approved structure only: X/target separation, ID
exclusion, column-group consistency, immutability of the input dataframe and
the basic shape and integration of the preprocessor. The concrete imputation
and encoding strategies remain pending (D-011 Proposed; encoding candidate
D-014 not yet recorded) and are deliberately not asserted here.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

from src import preprocessing
from src.config import (
    BINARY_COLS,
    FEATURE_COLUMNS,
    ID_COLUMN,
    NOMINAL_COLS,
    NUMERIC_COLS,
    ORDINAL_COLS,
    RANDOM_STATE,
    TARGET,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAIN_PATH = PROJECT_ROOT / "data" / "train_70.csv"
VAL_PATH = PROJECT_ROOT / "data" / "val_15.csv"

COLUMN_GROUPS = {
    "numeric": NUMERIC_COLS,
    "binary": BINARY_COLS,
    "nominal": NOMINAL_COLS,
    "ordinal": ORDINAL_COLS,
}


def _sklearn_available() -> bool:
    return importlib.util.find_spec("sklearn") is not None


requires_sklearn = pytest.mark.skipif(
    not _sklearn_available(),
    reason="scikit-learn is not installed in this environment",
)


@pytest.fixture(scope="session")
def train_df() -> pd.DataFrame:
    return pd.read_csv(TRAIN_PATH)


@pytest.fixture(scope="session")
def val_df() -> pd.DataFrame:
    return pd.read_csv(VAL_PATH)


# --- Column-group consistency (pandas only) ---------------------------------


def test_column_groups_cover_every_feature_exactly_once():
    members = [column for group in COLUMN_GROUPS.values() for column in group]
    assert sorted(members) == sorted(FEATURE_COLUMNS)
    assert len(members) == len(set(members))


def test_id_and_target_are_not_features():
    assert ID_COLUMN not in FEATURE_COLUMNS
    assert TARGET not in FEATURE_COLUMNS
    for group in COLUMN_GROUPS.values():
        assert ID_COLUMN not in group
        assert TARGET not in group


def test_train_schema_matches_configuration(train_df):
    assert set(train_df.columns) == set(FEATURE_COLUMNS) | {ID_COLUMN, TARGET}


def test_val_schema_matches_configuration(val_df):
    assert set(val_df.columns) == set(FEATURE_COLUMNS) | {ID_COLUMN, TARGET}


# --- make_features_target ----------------------------------------------------


def test_returns_features_and_target(train_df):
    X, y = preprocessing.make_features_target(train_df)
    assert list(X.columns) == list(FEATURE_COLUMNS)
    assert (y == train_df[TARGET]).all()
    assert len(X) == len(y) == len(train_df)


def test_id_is_excluded_from_features(train_df):
    X, _ = preprocessing.make_features_target(train_df)
    assert ID_COLUMN not in X.columns
    assert set(X.columns) == set(FEATURE_COLUMNS)


def test_extra_columns_are_ignored(train_df):
    decorated = train_df.assign(some_extra_column="noise")
    X, y = preprocessing.make_features_target(decorated)
    assert list(X.columns) == list(FEATURE_COLUMNS)
    assert "some_extra_column" not in X.columns


def test_input_dataframe_is_not_modified(train_df):
    snapshot = train_df.copy(deep=True)
    X, _ = preprocessing.make_features_target(train_df)
    pd.testing.assert_frame_equal(train_df, snapshot)
    X.iloc[0, 0] = -999.0  # mutating the output must not leak into the input
    pd.testing.assert_frame_equal(train_df, snapshot)


def test_missing_feature_columns_raise(train_df):
    with pytest.raises(KeyError, match="missing feature columns"):
        preprocessing.make_features_target(train_df.drop(columns=[NUMERIC_COLS[0]]))


def test_missing_target_raises(train_df):
    with pytest.raises(KeyError, match="target column"):
        preprocessing.make_features_target(train_df.drop(columns=[TARGET]))


# --- Preprocessor structure (requires scikit-learn) --------------------------


@requires_sklearn
class TestPreprocessorStructure:
    def test_returns_column_transformer_with_four_groups(self):
        from sklearn.compose import ColumnTransformer
        from sklearn.pipeline import Pipeline

        prep = preprocessing.build_preprocessing()
        assert isinstance(prep, ColumnTransformer)
        assert [name for name, _, _ in prep.transformers] == [
            "numeric",
            "binary",
            "nominal",
            "ordinal",
        ]
        assert prep.remainder == "drop"
        for name, _, _ in prep.transformers:
            sub_pipeline = dict((n, t) for n, t, _ in prep.transformers)[name]
            assert isinstance(sub_pipeline, Pipeline)

    def test_group_columns_match_configuration(self):
        prep = preprocessing.build_preprocessing()
        for name, _, columns in prep.transformers:
            assert list(columns) == list(COLUMN_GROUPS[name])

    def test_subpipeline_layout(self):
        from sklearn.pipeline import Pipeline

        prep = preprocessing.build_preprocessing()
        for name, sub_pipeline, _ in prep.transformers:
            assert isinstance(sub_pipeline, Pipeline)
            if name == "numeric":
                assert [step_name for step_name, _ in sub_pipeline.steps] == [
                    "imputer"
                ]
            else:
                assert [step_name for step_name, _ in sub_pipeline.steps] == [
                    "imputer",
                    "encoder",
                ]
            for _, transformer in sub_pipeline.steps:
                assert transformer == "passthrough"  # pending D-011 / D-014

    def test_fit_transform_train_and_transform_val(self, train_df, val_df):
        X_train, y_train = preprocessing.make_features_target(train_df)
        X_val, _ = preprocessing.make_features_target(val_df)
        prep = preprocessing.build_preprocessing()
        out_train = prep.fit_transform(X_train, y_train)
        out_val = prep.transform(X_val)  # validation is transformed, never fitted
        assert out_train.shape[1] == len(FEATURE_COLUMNS)
        assert out_val.shape[1] == len(FEATURE_COLUMNS)
        assert list(prep.get_feature_names_out()) == list(FEATURE_COLUMNS)

    def test_strategies_are_parametrizable_without_rewriting(self, train_df):
        # Mechanism validation only: proves the parameter seam accepts a real
        # transformer. It does NOT implement any pending D-011/D-014 decision.
        from sklearn.impute import SimpleImputer

        prep = preprocessing.build_preprocessing(
            numeric_imputer=SimpleImputer(strategy="median"),
        )
        X, y = preprocessing.make_features_target(train_df)
        out = prep.fit_transform(X, y)
        assert out.shape[1] == len(FEATURE_COLUMNS)
        numeric_out = out[:, : len(NUMERIC_COLS)]
        assert not pd.isna(numeric_out).any()  # the imputer filled the gaps
        binary_out = out[:, len(NUMERIC_COLS) : len(NUMERIC_COLS) + len(BINARY_COLS)]
        assert pd.isna(binary_out).any()  # the other groups stay passthrough

    def test_integrates_into_a_model_pipeline(self, train_df):
        # A DummyClassifier (strategy="prior") ignores feature values, so the
        # pipeline plumbing is validated without implementing any pending
        # encoding decision.
        from sklearn.dummy import DummyClassifier
        from sklearn.pipeline import Pipeline

        X, y = preprocessing.make_features_target(train_df)
        model = Pipeline(
            [
                ("prep", preprocessing.build_preprocessing()),
                (
                    "model",
                    DummyClassifier(strategy="prior", random_state=RANDOM_STATE),
                ),
            ]
        )
        model.fit(X, y)
        assert model.predict(X.head(5)).shape == (5,)

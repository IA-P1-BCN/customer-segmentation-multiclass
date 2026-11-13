"""Shared preprocessing structure for the Customer Segmentation project.

Implements the structural part of US-05 (issue #17): one common pipeline
layout that the four models (US-07 to US-10) and the prediction app import,
so they all receive exactly the same transformed features. Column roles live
in ``src.config`` and each group gets its own sub-pipeline inside a
``ColumnTransformer``.

The concrete strategies are not implemented in this structural phase and are
therefore exposed as parameters instead of being wired in:

- Imputation: D-011 (Approved by Brian, 2026-11-13) — median plus missing
  indicators for ``Work_Experience``/``Family_Size``, mode for
  ``Ever_Married``/``Graduated``/``Var_1``, and a constant ``Unknown`` level
  for ``Profession``. The strategies are approved but their implementation is
  deferred to the next phase.
- Encoding: the proposal recorded in issue #17, whose decision record
  (candidate ``D-014``) is still pending team approval — one-hot for the
  nominal columns and the ordinal order ``Low < Average < High`` for
  ``Spending_Score``.

Until the strategies are wired in, every strategy parameter defaults to
``"passthrough"``: the pipeline keeps its shape and runs without errors, but
it performs no imputation and no encoding. Passing real transformers (for
example ``SimpleImputer`` or ``OneHotEncoder``) fills in the behaviour
without rewriting this module.

Usage (from the repository root):

    from src.preprocessing import build_preprocessing, make_features_target
    X, y = make_features_target(df)
    prep = build_preprocessing()

Fit the returned preprocessor only on ``train_70``; transform ``val_15`` and
``test_15`` with it, never fit on them (D-006, AGENTS.md section 5). Scaling
is deliberately not part of this shared structure: tree-based models do not
need it and the models that do (logistic regression, SVM) add
``StandardScaler`` in their own pipeline step.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.config import (
    BINARY_COLS,
    FEATURE_COLUMNS,
    NOMINAL_COLS,
    NUMERIC_COLS,
    ORDINAL_COLS,
    TARGET,
)

__all__ = ["make_features_target", "build_preprocessing", "PENDING_DECISIONS"]

PENDING_DECISIONS = {
    "imputation": "D-011 (Approved by Brian, 2026-11-13) — strategies approved, implementation deferred to phase 2",
    "encoding": "not yet recorded; candidate identifier D-014, pending team approval",
}


def make_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Return ``(X, y)``: the feature columns and the target series.

    Features are selected by name from ``src.config.FEATURE_COLUMNS``, so
    ``ID`` (an identifier, never a feature) and any other column not declared
    in the configuration are excluded. The target is returned separately and
    never enters the preprocessing pipeline. The input dataframe is not
    modified.
    """
    missing = [column for column in FEATURE_COLUMNS if column not in df.columns]
    if missing:
        raise KeyError(f"Input dataframe is missing feature columns: {missing}")
    if TARGET not in df.columns:
        raise KeyError(f"Input dataframe is missing the target column {TARGET!r}.")
    X = df.loc[:, list(FEATURE_COLUMNS)].copy()
    y = df[TARGET]
    return X, y


def build_preprocessing(
    numeric_imputer: Any = "passthrough",
    binary_imputer: Any = "passthrough",
    nominal_imputer: Any = "passthrough",
    ordinal_imputer: Any = "passthrough",
    binary_encoder: Any = "passthrough",
    nominal_encoder: Any = "passthrough",
    ordinal_encoder: Any = "passthrough",
) -> Any:
    """Build the shared preprocessing ``ColumnTransformer`` (structure only).

    Parameters
    ----------
    numeric_imputer:
        Transformer for the numeric columns. D-011 (approved) assigns the
        median imputer here; its missing indicators can ride on the same step
        (``SimpleImputer(add_indicator=True)``).
    binary_imputer, nominal_imputer, ordinal_imputer:
        Transformers for each categorical group. D-011 proposes mode
        imputation for the binary and ``Var_1`` columns and a constant
        ``Unknown`` level for ``Profession``.
    binary_encoder, nominal_encoder, ordinal_encoder:
        Encoders for each categorical group; D-014 (pending) will fix the
        one-hot and ordinal choices.
    numeric_* groups have no encoder slot: numeric features are passed
        through after imputation.

    Notes
    -----
    * ``remainder="drop"`` guarantees that any column not declared in
      ``src.config`` (including ``ID``) never reaches the output, even if a
      full raw dataframe is passed by mistake.
    * Scaling is intentionally not included here (see module docstring).
    """
    try:
        from sklearn.compose import ColumnTransformer
        from sklearn.pipeline import Pipeline
    except ImportError as exc:
        raise RuntimeError(
            "scikit-learn is required to build the preprocessing pipeline. "
            "Install scikit-learn in the active Python environment."
        ) from exc

    numeric = Pipeline([("imputer", numeric_imputer)])
    binary = Pipeline([("imputer", binary_imputer), ("encoder", binary_encoder)])
    nominal = Pipeline([("imputer", nominal_imputer), ("encoder", nominal_encoder)])
    ordinal = Pipeline([("imputer", ordinal_imputer), ("encoder", ordinal_encoder)])

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric, list(NUMERIC_COLS)),
            ("binary", binary, list(BINARY_COLS)),
            ("nominal", nominal, list(NOMINAL_COLS)),
            ("ordinal", ordinal, list(ORDINAL_COLS)),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )

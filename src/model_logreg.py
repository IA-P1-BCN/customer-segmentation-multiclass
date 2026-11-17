"""Reusable multinomial logistic regression model (M1) for US-07 (issue #19).

Per D-013 item 3, a model owns only the steps it needs: this module builds
the full M1 Pipeline by connecting the approved D-011 imputers and — once
approved — the D-014 encoders through the parameter seam of
``build_preprocessing()`` (the shared preprocessing module is never
modified), plus the ``StandardScaler`` logistic regression needs (D-014
item 6: after the shared preprocessing, before the estimator).

Preprocessing status wired by this module:

- Imputation — D-011 (Approved by Brian, 2026-11-13): median plus missing
  indicators for ``Work_Experience``/``Family_Size``, mode for
  ``Ever_Married``/``Graduated``/``Var_1`` and a constant ``Unknown`` level
  for ``Profession``. Wired through ``build_preprocessing()`` parameters.
- Encoding — D-014 (Approved by Brian, 2026-11-16): one-hot with
  ``drop="if_binary"`` for the binary columns (item 1) and the nominal
  columns (item 2, wording corrected in PR #61), and one-hot without any
  ordinal order for ``Spending_Score`` (item 4, the measured segment mix is
  not monotone). ``handle_unknown="ignore"`` everywhere the decision
  requires. Wired through the ``build_preprocessing()`` parameter seam —
  the shared module is not modified (D-014 item 5).
- Provisional metrics — US-05 phase 2 (the D-011/D-014 configuration as
  the shared module's defaults) is not integrated in ``develop`` yet. This
  module wires the full approved D-011 + D-014 configuration through the
  parameter seam, so recorded metrics are marked provisional until phase 2
  lands (D-013 Consequences: re-run before the final US-11 comparison).

Metrics follow D-010: macro-F1 is the primary metric, accuracy is always
reported, and the overfitting check is ``accuracy(train_70) -
accuracy(val_15) < 5`` percentage points, absolute (exactly 5 does not
pass). Candidate configurations are compared with 5-fold stratified CV on
``train_70`` passing the full Pipeline (D-010 item 6), and the final
configuration is chosen with the common rule of D-015: highest mean CV
macro-F1 among the configurations whose mean train - CV accuracy gap is
below 5 points, using the standard-error tie rule and then the smallest
train - CV gap.

Usage (from the repository root):

    from src.model_logreg import build_logreg_pipeline, CANDIDATE_CONFIGS
    model = build_logreg_pipeline()   # baseline: C=1.0, penalty=l2, solver=lbfgs
    # Fit only on train_70; val_15 is only transformed (D-012, D-013).
"""

from __future__ import annotations

from typing import Any

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import RANDOM_STATE
from src.preprocessing import build_preprocessing

__all__ = ["build_logreg_pipeline", "CANDIDATE_CONFIGS", "D014_ENCODER_PARAMS"]

# --- Approved preprocessing: D-011 imputers (Approved by Brian, 2026-11-13) ---

# The nominal group needs two different strategies (D-011): mode for
# `Gender` and `Var_1`, constant "Unknown" for `Profession`. A small
# ColumnTransformer inside the "imputer" slot of build_preprocessing()
# applies them per column; the encoder that follows it is unaffected.
_D011_NOMINAL_IMPUTER = ColumnTransformer(
    transformers=[
        ("mode", SimpleImputer(strategy="most_frequent"), ["Gender", "Var_1"]),
        (
            "unknown",
            SimpleImputer(strategy="constant", fill_value="Unknown"),
            ["Profession"],
        ),
    ],
    remainder="drop",
    # Keep the final names aligned with the random forest and XGBoost
    # pipelines (`Gender_Male`, `Profession_*`) instead of prefixing them
    # with the imputer branch (`mode__`, `unknown__`). US-12 groups feature
    # importances by name, so the four models must expose the same labels.
    verbose_feature_names_out=False,
)

D011_IMPUTER_PARAMS = {
    # Median + missing indicators; `Age` has no missing values, so it adds
    # no indicator (A-011: 0.00 %) and D-011 asks for no imputation there.
    "numeric_imputer": SimpleImputer(strategy="median", add_indicator=True),
    "binary_imputer": SimpleImputer(strategy="most_frequent"),
    "nominal_imputer": _D011_NOMINAL_IMPUTER,
    "ordinal_imputer": "passthrough",  # Spending_Score: no missing values (A-011)
}

# --- Approved preprocessing: D-014 encoders (Approved by Brian, 2026-11-16) ---

D014_ENCODER_PARAMS = {
    # Ever_Married / Graduated: one 0/1 column each (D-014 item 1).
    "binary_encoder": OneHotEncoder(drop="if_binary", handle_unknown="ignore"),
    # Gender / Profession / Var_1: one column per level; `drop="if_binary"`
    # only affects Gender (D-014 item 2, wording corrected in PR #61).
    "nominal_encoder": OneHotEncoder(drop="if_binary", handle_unknown="ignore"),
    # Spending_Score: one column per level (Low/Average/High), no ordinal
    # order (D-014 item 4), passed through the existing ordinal slot (item 5).
    "ordinal_encoder": OneHotEncoder(handle_unknown="ignore"),
}

# --- Candidate configurations for the improvement phase (D-010 item 6) --------

# Compared with 5-fold stratified CV on train_70 (full Pipeline), selected
# with D-015 and evaluated officially on val_15 (D-010). Labels match the
# `config` column of results/logistic_regression.csv (US-03 convention).
CANDIDATE_CONFIGS = (
    {"config": "baseline", "C": 1.0, "penalty": "l2", "solver": "lbfgs", "class_weight": None},
    {"config": "C=0.01_l2", "C": 0.01, "penalty": "l2", "solver": "lbfgs", "class_weight": None},
    {"config": "C=0.1_l2", "C": 0.1, "penalty": "l2", "solver": "lbfgs", "class_weight": None},
    {"config": "C=10_l2", "C": 10.0, "penalty": "l2", "solver": "lbfgs", "class_weight": None},
    {"config": "C=1_l1_saga", "C": 1.0, "penalty": "l1", "solver": "saga", "class_weight": None},
    {
        "config": "C=1_l2_balanced",
        "C": 1.0,
        "penalty": "l2",
        "solver": "lbfgs",
        "class_weight": "balanced",
    },
)


def build_logreg_pipeline(
    C: float = 1.0,
    penalty: str = "l2",
    solver: str = "lbfgs",
    class_weight: Any = None,
    max_iter: int = 1000,
) -> Pipeline:
    """Build the full M1 pipeline: shared preprocessing, scaler, estimator.

    The shared preprocessing wires the approved D-011 imputers and the
    approved D-014 encoders through parameters (the shared module is never
    modified). ``StandardScaler`` is a model-specific step of logistic
    regression (D-014 item 6): it lives here — after the shared
    preprocessing and before the estimator — never inside
    ``src/preprocessing.py``. The estimator is multinomial by default in
    scikit-learn 1.9 (the old ``multi_class`` parameter no longer exists).
    """

    preprocessing = build_preprocessing(
        **D011_IMPUTER_PARAMS,
        **D014_ENCODER_PARAMS,
    )

    return Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    C=C,
                    penalty=penalty,
                    solver=solver,
                    class_weight=class_weight,
                    max_iter=max_iter,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )

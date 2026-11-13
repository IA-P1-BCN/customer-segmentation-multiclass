"""Central project configuration (US-03, issue #15).

``RANDOM_STATE`` is the single source of truth for every stochastic step of
the project (data splits, cross-validation, resampling and models), so that
any run can be repeated exactly (AGENTS.md section 5).

Usage:

    from src.config import RANDOM_STATE

Never hardcode ``42`` elsewhere; import this constant instead.
"""

RANDOM_STATE = 42

# --- Column roles (US-05, issue #17) ----------------------------------------
# Shared by src/preprocessing.py; based on the schema audited in Train.csv
# and its splits (11 columns: ID + 9 features + Segmentation).
TARGET = "Segmentation"
ID_COLUMN = "ID"
NUMERIC_COLS = ("Age", "Work_Experience", "Family_Size")
BINARY_COLS = ("Ever_Married", "Graduated")
NOMINAL_COLS = ("Gender", "Profession", "Var_1")
ORDINAL_COLS = ("Spending_Score",)
# Every predictor, grouped by role. The order defines the layout of the
# transformed feature matrix. ID is never a feature (D-006/D-012) and the
# target is never preprocessed with the features.
FEATURE_COLUMNS = NUMERIC_COLS + BINARY_COLS + NOMINAL_COLS + ORDINAL_COLS

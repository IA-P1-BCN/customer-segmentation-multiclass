"""Tests for the US-09 boosting script (``src/train_boosting.py``).

Run from the repository root with:

    python -m pytest tests/test_train_boosting.py

The tests cover the parts that must not drift silently: partition
verification against D-013, the results-log convention of
``results/README.md``, the configuration spaces and the metric helpers.
They deliberately do not train XGBoost: a real fit belongs to an executed,
recorded run, not to the test suite.
"""

from __future__ import annotations

import hashlib
import importlib.util
from itertools import product
from pathlib import Path

import pandas as pd
import pytest

from src import train_boosting
from src.config import RANDOM_STATE

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

CONVENTION_COLUMNS = [
    "run_timestamp_utc",
    "seed",
    "model",
    "config",
    "partition",
    "accuracy",
    "macro_f1",
    "f1_A",
    "f1_B",
    "f1_C",
    "f1_D",
    "notes",
]

requires_sklearn = pytest.mark.skipif(
    importlib.util.find_spec("sklearn") is None,
    reason="scikit-learn is not installed in this environment",
)
requires_xgboost = pytest.mark.skipif(
    importlib.util.find_spec("xgboost") is None,
    reason="xgboost is not installed in this environment",
)


def _result_row(partition: str = "cv5fold", config: str = "baseline") -> dict:
    metrics = {
        "accuracy": 0.5,
        "macro_f1": 0.4,
        "f1_A": 0.1,
        "f1_B": 0.2,
        "f1_C": 0.3,
        "f1_D": 0.4,
    }
    return train_boosting.result_row(
        "2026-11-15T00:00:00Z", config, partition, metrics, "test row"
    )


# --- Partition verification (D-013) -----------------------------------------


def test_expected_rows_cover_the_three_partitions():
    assert set(train_boosting.EXPECTED_ROWS) == {"train_70", "val_15", "test_15"}
    assert train_boosting.EXPECTED_ROWS == {
        "train_70": 5_647,
        "val_15": 1_210,
        "test_15": 1_211,
    }


def test_reference_checksums_cover_the_three_partitions():
    assert set(train_boosting.REFERENCE_SHA256_LF) == set(train_boosting.EXPECTED_ROWS)
    for value in train_boosting.REFERENCE_SHA256_LF.values():
        assert len(value) == 64
        int(value, 16)  # hexadecimal


def test_sha256_lf_normalises_line_endings(tmp_path):
    path = tmp_path / "sample.csv"
    path.write_bytes(b"a,b\r\n1,2\r\n")
    expected = hashlib.sha256(b"a,b\n1,2\n").hexdigest()
    assert train_boosting.sha256_lf(path) == expected


def test_sha256_lf_is_independent_of_crlf(tmp_path):
    lf_path = tmp_path / "lf.csv"
    crlf_path = tmp_path / "crlf.csv"
    lf_path.write_bytes(b"x,y\n1,2\n3,4\n")
    crlf_path.write_bytes(b"x,y\r\n1,2\r\n3,4\r\n")
    assert train_boosting.sha256_lf(lf_path) == train_boosting.sha256_lf(crlf_path)


def test_committed_partitions_match_the_d013_checksums():
    for name, expected in train_boosting.REFERENCE_SHA256_LF.items():
        digest = train_boosting.sha256_lf(DATA_DIR / f"{name}.csv")
        assert digest == expected, f"{name} no longer matches D-013"


def test_verify_partitions_accepts_the_committed_files():
    datasets = train_boosting.load_partitions()
    train_boosting.verify_partitions(datasets)  # must not raise


def test_verify_partitions_detects_a_wrong_row_count(capsys):
    datasets = {
        "train_70": pd.DataFrame({"ID": [1, 2, 3]}),
        "val_15": pd.DataFrame({"ID": [4, 5]}),
        "test_15": pd.DataFrame({"ID": [6, 7]}),
    }
    with pytest.raises(SystemExit):
        train_boosting.verify_partitions(datasets)
    captured = capsys.readouterr().out
    assert "has 3 rows, expected 5,647" in captured


def test_verify_partitions_detects_id_overlap(capsys):
    datasets = {
        "train_70": pd.DataFrame({"ID": [1, 2, 3]}),
        "val_15": pd.DataFrame({"ID": [3, 4]}),
        "test_15": pd.DataFrame({"ID": [5, 6]}),
    }
    with pytest.raises(SystemExit):
        train_boosting.verify_partitions(datasets)
    captured = capsys.readouterr().out
    assert "share 1 IDs" in captured


def test_verify_partitions_detects_a_missing_id_column(capsys):
    datasets = {
        "train_70": pd.DataFrame({"other": [1, 2]}),
        "val_15": pd.DataFrame({"ID": [3]}),
        "test_15": pd.DataFrame({"ID": [4]}),
    }
    with pytest.raises(SystemExit):
        train_boosting.verify_partitions(datasets)
    assert "has no ID column" in capsys.readouterr().out


# --- Results log (results/README.md) ----------------------------------------


def test_results_columns_match_the_documented_convention():
    assert train_boosting.RESULTS_COLUMNS == CONVENTION_COLUMNS


def test_result_row_follows_the_convention_order_and_rounds():
    row = _result_row()
    assert list(row) == CONVENTION_COLUMNS
    assert row["model"] == "boosting"
    assert row["seed"] == RANDOM_STATE
    assert row["accuracy"] == 0.5
    assert row["f1_C"] == 0.3


def test_append_results_writes_header_once_then_appends(tmp_path):
    path = tmp_path / "boosting.csv"
    train_boosting.append_results([_result_row()], path)
    train_boosting.append_results([_result_row(partition="val_15")], path)

    raw = path.read_bytes()
    assert b"\r\n" not in raw  # LF only, same rule as the data files (D-013)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == ",".join(CONVENTION_COLUMNS)
    assert len(lines) == 3


def test_append_results_rejects_a_different_header(tmp_path):
    path = tmp_path / "boosting.csv"
    path.write_text("a,b\n1,2\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        train_boosting.append_results([_result_row()], path)


# --- Configuration spaces ---------------------------------------------------


def test_grid_expands_to_18_complete_configurations():
    configs = train_boosting.grid_configurations()
    assert len(configs) == 18
    assert len(set(configs)) == 18

    keys = list(train_boosting.GRID_SPACE)
    expected = set(product(*(train_boosting.GRID_SPACE[key] for key in keys)))
    found = {tuple(params[key] for key in keys) for params in configs.values()}
    assert found == expected

    for name, params in configs.items():
        assert name.startswith("grid_")
        assert set(train_boosting.BASELINE_PARAMS) <= set(params)


def test_refine_expands_to_8_configurations_at_depth_3():
    configs = train_boosting.refine_configurations()
    assert len(configs) == 8
    assert len(set(configs)) == 8
    for name, params in configs.items():
        assert name.startswith("refine_")
        assert params["max_depth"] == 3
        assert params["subsample"] == 1.0
        assert params["n_estimators"] in train_boosting.REFINE_SPACE["n_estimators"]


def test_baseline_is_not_part_of_the_grid():
    assert "baseline" not in train_boosting.grid_configurations()
    assert "baseline" not in train_boosting.refine_configurations()


# --- Metrics and labels -----------------------------------------------------


def test_compute_metrics_on_perfect_predictions():
    labels = ["A", "B", "C", "D"]
    metrics = train_boosting.compute_metrics(labels, labels, labels)
    assert metrics["accuracy"] == 1.0
    assert metrics["macro_f1"] == 1.0
    for label in labels:
        assert metrics[f"precision_{label}"] == 1.0
        assert metrics[f"recall_{label}"] == 1.0
        assert metrics[f"f1_{label}"] == 1.0


def test_compute_metrics_reports_every_class_even_if_absent():
    metrics = train_boosting.compute_metrics(["A", "A"], ["A", "A"], ["A", "B"])
    # zero_division=0, not NaN
    assert metrics["f1_B"] == 0.0
    assert metrics["precision_B"] == 0.0
    assert metrics["recall_B"] == 0.0


def test_per_class_report_contains_every_class_and_the_three_metrics():
    labels = ["A", "B", "C", "D"]
    metrics = train_boosting.compute_metrics(labels, labels, labels)
    report = train_boosting.per_class_report(metrics, labels)
    assert report.startswith("per-class val ")
    for label in labels:
        assert f"{label} P=1.000 R=1.000 F1=1.000" in report


def test_encode_target_round_trips_string_labels():
    y = pd.Series(["B", "A", "D", "C", "A"])
    encoder, encoded, classes = train_boosting.encode_target(y)
    assert classes == ["A", "B", "C", "D"]
    assert sorted(set(encoded)) == [0, 1, 2, 3]
    assert list(encoder.inverse_transform(encoded)) == list(y)


# --- Pipeline wiring (requires scikit-learn) --------------------------------


@requires_sklearn
def test_build_preprocessor_returns_the_d011_d014_matrix():
    # D-011 + D-014 fix the width on train_70: 3 numeric + 2 missing
    # indicators + 2 binary + 1 Gender + 10 Profession (9 levels + Unknown)
    # + 7 Var_1 + 3 Spending_Score = 28. Var_1 keeps the mode, so there is no
    # Var_1_Unknown column: that column only appeared with the provisional
    # single nominal_imputer.
    from src.preprocessing import make_features_target

    df = pd.read_csv(DATA_DIR / "train_70.csv")
    X, y = make_features_target(df)
    preprocessor = train_boosting.build_preprocessor()
    matrix = preprocessor.fit_transform(X, y)
    dense = matrix.toarray() if hasattr(matrix, "toarray") else matrix

    assert dense.shape == (len(X), 28)
    assert not pd.isna(dense).any()
    names = list(preprocessor.get_feature_names_out())
    assert "ID" not in names
    assert "Segmentation" not in names
    assert "Gender_Male" in names
    assert sum(name.startswith("Gender_") for name in names) == 1
    assert "Profession_Unknown" in names
    assert sum(name.startswith("Profession_") for name in names) == 10
    assert sum(name.startswith("Var_1_") for name in names) == 7
    assert "Var_1_Unknown" not in names


@requires_sklearn
def test_preprocessing_is_fitted_only_on_the_given_split():
    # Transforming val_15 must not change what was learnt on train_70: the
    # matrix is identical whether the validation rows are seen or not.
    from src.preprocessing import make_features_target

    def as_dense(matrix):
        return matrix.toarray() if hasattr(matrix, "toarray") else matrix

    train = make_features_target(pd.read_csv(DATA_DIR / "train_70.csv"))[0]
    val = make_features_target(pd.read_csv(DATA_DIR / "val_15.csv"))[0]

    preprocessor = train_boosting.build_preprocessor().fit(train)
    alone = as_dense(preprocessor.transform(val))
    together = as_dense(preprocessor.transform(pd.concat([train, val])))

    # The val block is the tail of the concatenation, not the head.
    pd.testing.assert_frame_equal(
        pd.DataFrame(alone),
        pd.DataFrame(together[train.shape[0] :]),
        check_dtype=False,
    )


# --- Model (requires xgboost) -----------------------------------------------


@requires_xgboost
def test_build_model_uses_the_global_seed_and_the_given_params():
    model = train_boosting.build_model({"n_estimators": 10, "max_depth": 3})
    params = model.get_params()
    assert params["random_state"] == RANDOM_STATE
    assert params["n_estimators"] == 10
    assert params["max_depth"] == 3


# --- Selection rule (D-015) --------------------------------------------------


def _cv_table(rows):
    """Build the CV summary table consumed by ``select_cv`` (no training)."""
    return pd.DataFrame(
        [
            {
                "config": name,
                "params": {"max_depth": 3},
                "cv_accuracy": accuracy,
                "cv_macro_f1": macro_f1,
                "cv_macro_f1_sd": sd,
                "train_cv_gap": gap,
            }
            for name, accuracy, macro_f1, sd, gap in rows
        ]
    )


def test_select_cv_prefers_the_smallest_gap_within_one_standard_error():
    # The best CV macro-F1 is cfg_a, but cfg_b is inside one standard error of
    # it and has a smaller train-CV gap, so the rule picks cfg_b. cfg_c has the
    # smallest gap of all and must be ignored: it lies outside the tie.
    table = _cv_table(
        [
            ("cfg_a", 0.52, 0.5200, 0.0200, 0.020),
            ("cfg_b", 0.51, 0.5150, 0.0100, 0.005),
            ("cfg_c", 0.50, 0.4900, 0.0100, 0.001),
        ]
    )
    best, reason = train_boosting.select_cv(table)
    assert best["config"] == "cfg_b"
    assert "D-015" in reason
    assert "configurations with gap < 5 pts" in reason


def test_select_cv_declares_the_limitation_when_none_meets_the_gap():
    table = _cv_table(
        [
            ("cfg_x", 0.52, 0.5200, 0.0100, 0.090),
            ("cfg_y", 0.51, 0.5100, 0.0100, 0.060),
        ]
    )
    best, reason = train_boosting.select_cv(table)
    assert best["config"] == "cfg_y"
    assert "no configuration met the CV gap limit" in reason


def test_selected_params_is_one_of_the_recorded_candidates():
    # The recorded choice feeds US-11, so it must be a configuration this
    # script actually evaluated and not a hand-written hyperparameter set.
    grid = train_boosting.grid_configurations()
    refine = train_boosting.refine_configurations()
    assert train_boosting.SELECTED_PARAMS in [*grid.values(), *refine.values()]

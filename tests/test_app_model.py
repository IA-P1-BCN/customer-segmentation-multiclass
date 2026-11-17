"""Tests for the frozen-model seam (US-15, issue #35)."""

from __future__ import annotations

import pandas as pd
import pytest

from app.utils.model import (
    ModelArtifactError,
    PredictionError,
    load_predictor,
    predict_segment,
)
from app.utils.validation import build_feature_frame


class FakePredictor:
    def __init__(self, predictions):
        self.predictions = predictions
        self.seen = None

    def predict(self, features):
        self.seen = features
        return self.predictions


class FailingPredictor:
    def predict(self, features):
        raise RuntimeError("boom")


def feature_frame() -> pd.DataFrame:
    return build_feature_frame(
        {"Age": 35, "Gender": "Female", "Spending_Score": "Low"}
    )


def test_predict_segment_returns_single_label():
    predictor = FakePredictor(["B"])
    features = feature_frame()
    assert predict_segment(predictor, features) == "B"
    assert predictor.seen is features


def test_predict_segment_accepts_a_plain_string():
    assert predict_segment(FakePredictor("C"), feature_frame()) == "C"


def test_predict_segment_rejects_multiple_predictions():
    with pytest.raises(PredictionError, match="exactamente una etiqueta"):
        predict_segment(FakePredictor(["A", "B"]), feature_frame())


def test_predict_segment_rejects_unknown_labels():
    with pytest.raises(PredictionError, match="no válida"):
        predict_segment(FakePredictor(["E"]), feature_frame())


def test_predict_segment_rejects_wrong_columns():
    features = feature_frame().drop(columns=["Var_1"])
    with pytest.raises(PredictionError, match="FEATURE_COLUMNS"):
        predict_segment(FakePredictor(["A"]), features)


def test_predict_segment_requires_exactly_one_row():
    features = pd.concat([feature_frame(), feature_frame()], ignore_index=True)
    with pytest.raises(PredictionError, match="exactamente una fila"):
        predict_segment(FakePredictor(["A", "B"]), features)


def test_predict_segment_requires_a_dataframe():
    with pytest.raises(PredictionError, match="DataFrame"):
        predict_segment(FakePredictor(["A"]), [{"Age": 35}])


def test_predictor_errors_are_wrapped():
    with pytest.raises(PredictionError, match="no pudo generar"):
        predict_segment(FailingPredictor(), feature_frame())


def test_load_predictor_rejects_a_missing_artifact(tmp_path):
    with pytest.raises(ModelArtifactError, match="No se encontró"):
        load_predictor(tmp_path / "missing.joblib")


def test_load_predictor_loads_direct_model_artifact(tmp_path):
    joblib = pytest.importorskip("joblib")
    path = tmp_path / "direct_model.joblib"
    joblib.dump(FakePredictor(["D"]), path)
    loaded = load_predictor(path)
    assert predict_segment(loaded, feature_frame()) == "D"


def test_load_predictor_loads_dict_payload_and_predicts(tmp_path):
    joblib = pytest.importorskip("joblib")
    path = tmp_path / "final_model.joblib"
    payload = {
        "model": FakePredictor(["B"]),
        "frozen_params": {"C": 1.0, "kernel": "rbf"},
        "trained_on": "train_70",
        "rows": 5647,
    }
    joblib.dump(payload, path)
    loaded = load_predictor(path)
    assert predict_segment(loaded, feature_frame()) == "B"


def test_load_predictor_rejects_dict_missing_model_key(tmp_path):
    joblib = pytest.importorskip("joblib")
    path = tmp_path / "invalid_dict.joblib"
    payload = {
        "frozen_params": {"C": 1.0},
        "trained_on": "train_70",
        "rows": 5647,
    }
    joblib.dump(payload, path)
    with pytest.raises(ModelArtifactError, match="clave requerida 'model'"):
        load_predictor(path)


def test_load_predictor_rejects_object_without_predict_method(tmp_path):
    joblib = pytest.importorskip("joblib")
    path_direct = tmp_path / "not_a_model.joblib"
    joblib.dump("not_a_model", path_direct)
    with pytest.raises(ModelArtifactError, match="no tiene un método 'predict'"):
        load_predictor(path_direct)

    path_dict = tmp_path / "dict_not_a_model.joblib"
    joblib.dump({"model": 12345}, path_dict)
    with pytest.raises(ModelArtifactError, match="no tiene un método 'predict'"):
        load_predictor(path_dict)

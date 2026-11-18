"""Frozen-model adapter for the prediction application (US-15, issue #35).

Phase 1 only defines the seam: the application can receive any object with a
``predict`` method, and tests use a fake predictor. The real artefact is
produced by US-11 (issue #27), so no model is trained or loaded here.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Protocol

import pandas as pd

from src.config import FEATURE_COLUMNS

__all__ = [
    "DEFAULT_MODEL_PATH",
    "ModelArtifactError",
    "ModelArtifactNotFoundError",
    "PredictionError",
    "Predictor",
    "SEGMENT_LABELS",
    "load_predictor",
    "predict_segment",
]

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "final_model.joblib"

SEGMENT_LABELS = frozenset({"A", "B", "C", "D"})


class Predictor(Protocol):
    """Minimal interface required from the frozen model or a test double."""

    def predict(self, features: pd.DataFrame) -> Sequence[Any]:
        """Return one predicted label per input row."""


class ModelArtifactError(RuntimeError):
    """Raised when the frozen model artefact cannot be loaded or is invalid."""


class ModelArtifactNotFoundError(ModelArtifactError, FileNotFoundError):
    """Raised when the frozen model artefact cannot be located."""


class PredictionError(RuntimeError):
    """Raised when the predictor does not return a single valid segment."""


def load_predictor(path: str | Path | None = None) -> Predictor:
    """Load a joblib-serialised predictor from ``path``.

    If ``path`` is ``None``, ``DEFAULT_MODEL_PATH`` is used.
    US-11 owns the artefact contract and its location; this function provides
    the loading seam. It accepts either a directly serialised pipeline/predictor
    or a dictionary payload containing the model under the ``"model"`` key.
    """
    artifact_path = DEFAULT_MODEL_PATH if path is None else Path(path)
    if not artifact_path.is_file():
        raise ModelArtifactNotFoundError(
            f"No se encontró el artefacto del modelo en {artifact_path}."
        )
    try:
        import joblib
    except ImportError as exc:
        raise ModelArtifactError(
            "joblib no está instalado; es necesario para cargar el modelo congelado."
        ) from exc
    try:
        payload = joblib.load(artifact_path)
    except Exception as exc:
        raise ModelArtifactError(
            f"No se pudo cargar el artefacto del modelo en {artifact_path}: {exc}"
        ) from exc

    if isinstance(payload, dict):
        if "model" not in payload:
            raise ModelArtifactError(
                f"El artefacto en {artifact_path} no contiene la clave requerida 'model'."
            )
        model = payload["model"]
    else:
        model = payload

    if not hasattr(model, "predict") or not callable(getattr(model, "predict")):
        raise ModelArtifactError(
            f"El modelo cargado desde {artifact_path} no tiene un método 'predict'."
        )

    return model


def predict_segment(predictor: Predictor, features: pd.DataFrame) -> str:
    """Return the single segment label predicted for one feature row."""
    if not isinstance(features, pd.DataFrame):
        raise PredictionError("Las features deben ser un DataFrame de pandas.")
    if list(features.columns) != list(FEATURE_COLUMNS):
        raise PredictionError(
            "Las columnas de las features no coinciden con FEATURE_COLUMNS."
        )
    if len(features) != 1:
        raise PredictionError("La predicción debe recibir exactamente una fila.")

    try:
        raw_predictions = predictor.predict(features)
    except Exception as exc:
        raise PredictionError(f"El modelo no pudo generar la predicción: {exc}") from exc

    if isinstance(raw_predictions, str):
        predictions = [raw_predictions]
    else:
        try:
            predictions = list(raw_predictions)
        except TypeError as exc:
            raise PredictionError(
                "El modelo devolvió una predicción que no se puede interpretar."
            ) from exc

    if len(predictions) != 1:
        raise PredictionError(
            "El modelo debe devolver exactamente una etiqueta para una fila."
        )

    label = str(predictions[0]).strip()
    if label not in SEGMENT_LABELS:
        raise PredictionError(
            f"Etiqueta de segmento no válida: {label!r}; se esperaba A, B, C o D."
        )
    return label

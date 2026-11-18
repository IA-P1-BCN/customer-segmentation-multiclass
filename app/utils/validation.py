"""Input validation for the prediction application (US-15, issue #35).

The Streamlit form produces a single customer record. This module normalises it
into the feature layout defined by ``src.config`` so the frozen model receives
exactly the same columns and order used during training.

``Age``, ``Gender`` and ``Spending_Score`` are required. The remaining fields
are optional and default to missing (``None``), leaving the approved
imputation steps of the shared Pipeline to handle them.
"""

from __future__ import annotations

from collections.abc import Mapping
from math import isnan
from typing import Any

import pandas as pd

from src.config import FEATURE_COLUMNS

__all__ = [
    "CATEGORY_OPTIONS",
    "FIELD_LABELS",
    "INTEGER_RANGES",
    "OPTIONAL_FIELDS",
    "REQUIRED_FIELDS",
    "ValidationError",
    "build_feature_frame",
    "validate_payload",
]

REQUIRED_FIELDS = ("Age", "Gender", "Spending_Score")

FIELD_LABELS = {
    "Age": "Edad",
    "Work_Experience": "Experiencia laboral",
    "Family_Size": "Tamaño del hogar",
    "Ever_Married": "Estado civil",
    "Graduated": "Graduado/a",
    "Gender": "Género",
    "Profession": "Profesión",
    "Var_1": "Var_1",
    "Spending_Score": "Nivel de gasto",
}

CATEGORY_OPTIONS = {
    "Gender": ("Female", "Male"),
    "Ever_Married": ("Yes", "No"),
    "Graduated": ("Yes", "No"),
    "Profession": (
        "Artist",
        "Doctor",
        "Engineer",
        "Entertainment",
        "Executive",
        "Healthcare",
        "Homemaker",
        "Lawyer",
        "Marketing",
    ),
    "Var_1": ("Cat_1", "Cat_2", "Cat_3", "Cat_4", "Cat_5", "Cat_6", "Cat_7"),
    "Spending_Score": ("Low", "Average", "High"),
}

INTEGER_RANGES = {
    "Age": (18, 89),
    "Work_Experience": (0, 14),
    "Family_Size": (1, 9),
}

OPTIONAL_FIELDS = tuple(
    column for column in FEATURE_COLUMNS if column not in REQUIRED_FIELDS
)


class ValidationError(ValueError):
    """Raised when one or more form values are invalid."""

    def __init__(self, errors: Mapping[str, str]) -> None:
        self.errors = dict(errors)
        detail = "; ".join(
            f"{field}: {message}" for field, message in self.errors.items()
        )
        super().__init__(detail)


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if value is pd.NA:
        return True
    if isinstance(value, float) and isnan(value):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _validate_category(field: str, value: Any, errors: dict[str, str]) -> str | None:
    if _is_missing(value):
        return None
    if not isinstance(value, str):
        errors[field] = "Debe ser una categoría de texto."
        return None
    cleaned = value.strip()
    options = CATEGORY_OPTIONS[field]
    if cleaned not in options:
        errors[field] = (
            f"Valor no válido: {cleaned!r}. Opciones: {', '.join(options)}."
        )
        return None
    return cleaned


def _validate_integer(field: str, value: Any, errors: dict[str, str]) -> int | None:
    if _is_missing(value):
        return None
    if isinstance(value, bool):
        errors[field] = "Debe ser un número entero."
        return None
    if isinstance(value, float):
        if not value.is_integer():
            errors[field] = "Debe ser un número entero."
            return None
        number = int(value)
    elif isinstance(value, int):
        number = value
    elif isinstance(value, str):
        try:
            number = int(value.strip())
        except ValueError:
            errors[field] = "Debe ser un número entero."
            return None
    else:
        errors[field] = "Debe ser un número entero."
        return None

    lower, upper = INTEGER_RANGES[field]
    if not lower <= number <= upper:
        errors[field] = f"Debe estar entre {lower} y {upper}."
        return None
    return number


def validate_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalise one customer record.

    Returns a dictionary in ``FEATURE_COLUMNS`` order. Optional missing values
    are returned as ``None``; required missing or invalid values raise
    ``ValidationError`` with one message per affected field.
    """
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be a mapping of feature names to values")

    errors: dict[str, str] = {}
    row: dict[str, Any] = {}
    for column in FEATURE_COLUMNS:
        value = payload.get(column)
        if column in INTEGER_RANGES:
            row[column] = _validate_integer(column, value, errors)
        else:
            row[column] = _validate_category(column, value, errors)
        if (
            column in REQUIRED_FIELDS
            and row[column] is None
            and column not in errors
        ):
            errors[column] = "Campo obligatorio."

    if errors:
        raise ValidationError(errors)
    return row


def build_feature_frame(payload: Mapping[str, Any]) -> pd.DataFrame:
    """Return a one-row DataFrame ready for the frozen model Pipeline."""
    row = validate_payload(payload)
    return pd.DataFrame([row], columns=list(FEATURE_COLUMNS))

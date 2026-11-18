"""Tests for the prediction-app input validation (US-15, issue #35)."""

from __future__ import annotations

import pandas as pd
import pytest

from app.utils.validation import (
    CATEGORY_OPTIONS,
    FIELD_LABELS,
    INTEGER_RANGES,
    OPTIONAL_FIELDS,
    REQUIRED_FIELDS,
    ValidationError,
    build_feature_frame,
    validate_payload,
)
from src.config import FEATURE_COLUMNS


def valid_payload() -> dict[str, object]:
    return {"Age": 35, "Gender": "Female", "Spending_Score": "Low"}


def test_field_configuration_covers_every_feature_exactly_once():
    assert REQUIRED_FIELDS == ("Age", "Gender", "Spending_Score")
    assert set(INTEGER_RANGES) | set(CATEGORY_OPTIONS) == set(FEATURE_COLUMNS)
    assert set(REQUIRED_FIELDS) <= set(FEATURE_COLUMNS)
    assert OPTIONAL_FIELDS == tuple(
        column for column in FEATURE_COLUMNS if column not in REQUIRED_FIELDS
    )


def test_valid_required_payload_builds_one_row_in_feature_order():
    frame = build_feature_frame(valid_payload())
    assert isinstance(frame, pd.DataFrame)
    assert list(frame.columns) == list(FEATURE_COLUMNS)
    assert len(frame) == 1
    assert frame.loc[0, "Age"] == 35
    assert frame.loc[0, "Gender"] == "Female"
    assert frame.loc[0, "Spending_Score"] == "Low"


def test_optional_fields_default_to_missing():
    frame = build_feature_frame(valid_payload())
    for column in OPTIONAL_FIELDS:
        assert pd.isna(frame.loc[0, column])


def test_optional_values_are_preserved():
    payload = {
        **valid_payload(),
        "Ever_Married": "Yes",
        "Graduated": "No",
        "Profession": "Engineer",
        "Work_Experience": 4,
        "Family_Size": 3,
        "Var_1": "Cat_2",
    }
    row = validate_payload(payload)
    assert row["Ever_Married"] == "Yes"
    assert row["Graduated"] == "No"
    assert row["Profession"] == "Engineer"
    assert row["Work_Experience"] == 4
    assert row["Family_Size"] == 3
    assert row["Var_1"] == "Cat_2"


def test_empty_optional_string_is_treated_as_missing():
    payload = {**valid_payload(), "Ever_Married": "  ", "Profession": ""}
    row = validate_payload(payload)
    assert row["Ever_Married"] is None
    assert row["Profession"] is None


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_missing_required_field_is_rejected(field):
    payload = valid_payload()
    payload.pop(field)
    with pytest.raises(ValidationError) as exc_info:
        validate_payload(payload)
    assert field in exc_info.value.errors
    assert "obligatorio" in exc_info.value.errors[field].lower()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("Gender", "Other"),
        ("Spending_Score", "Very high"),
        ("Ever_Married", "Maybe"),
        ("Profession", "Unknown profession"),
        ("Var_1", "Cat_8"),
    ],
)
def test_invalid_category_is_rejected(field, value):
    payload = {**valid_payload(), field: value}
    with pytest.raises(ValidationError) as exc_info:
        validate_payload(payload)
    assert field in exc_info.value.errors
    assert "no válido" in exc_info.value.errors[field].lower()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("Age", 17),
        ("Age", 90),
        ("Work_Experience", -1),
        ("Work_Experience", 15),
        ("Family_Size", 0),
        ("Family_Size", 10),
    ],
)
def test_numeric_values_outside_the_observed_range_are_rejected(field, value):
    payload = {**valid_payload(), field: value}
    with pytest.raises(ValidationError) as exc_info:
        validate_payload(payload)
    assert field in exc_info.value.errors
    assert "entre" in exc_info.value.errors[field].lower()


def test_numeric_strings_are_accepted():
    payload = {**valid_payload(), "Age": "35", "Work_Experience": "4"}
    row = validate_payload(payload)
    assert row["Age"] == 35
    assert row["Work_Experience"] == 4


def test_boolean_is_rejected_for_a_numeric_field():
    payload = {**valid_payload(), "Age": True}
    with pytest.raises(ValidationError) as exc_info:
        validate_payload(payload)
    assert "Age" in exc_info.value.errors
    assert "entero" in exc_info.value.errors["Age"].lower()


def test_fractional_number_is_rejected_for_a_numeric_field():
    payload = {**valid_payload(), "Family_Size": 2.5}
    with pytest.raises(ValidationError) as exc_info:
        validate_payload(payload)
    assert "Family_Size" in exc_info.value.errors
    assert "entero" in exc_info.value.errors["Family_Size"].lower()


def test_invalid_category_does_not_add_a_duplicate_required_error():
    payload = {**valid_payload(), "Gender": "Other"}
    with pytest.raises(ValidationError) as exc_info:
        validate_payload(payload)
    assert len(exc_info.value.errors) == 1
    assert "Gender" in exc_info.value.errors


def test_payload_is_not_mutated():
    payload = {**valid_payload(), "Ever_Married": "Yes"}
    snapshot = dict(payload)
    validate_payload(payload)
    assert payload == snapshot


def test_non_mapping_payload_is_rejected():
    with pytest.raises(TypeError):
        validate_payload(["Age", 35])


def test_field_labels_cover_every_feature_in_order():
    assert tuple(FIELD_LABELS.keys()) == FEATURE_COLUMNS
    for column, label in FIELD_LABELS.items():
        assert isinstance(label, str) and label.strip()


@pytest.mark.parametrize("missing_value", [None, pd.NA, float("nan")])
@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_missing_values_rejected_for_required_fields(missing_value, field):
    payload = {**valid_payload(), field: missing_value}
    with pytest.raises(ValidationError) as exc_info:
        validate_payload(payload)
    assert field in exc_info.value.errors
    assert "obligatorio" in exc_info.value.errors[field].lower()


@pytest.mark.parametrize("missing_value", [None, pd.NA, float("nan")])
@pytest.mark.parametrize("field", OPTIONAL_FIELDS)
def test_missing_values_accepted_for_optional_fields(missing_value, field):
    payload = {**valid_payload(), field: missing_value}
    row = validate_payload(payload)
    assert row[field] is None

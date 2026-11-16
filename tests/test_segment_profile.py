"""Tests for the segment profile (US-13, issue #13).

Run from the repository root with:

    python -m pytest tests/test_segment_profile.py

Most tests use a tiny invented dataset (8 customers, 2 segments) whose
figures can be checked by hand, so a failure points at the calculation and
not at the data. The invented values are not project results.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

from src import segment_profile
from src.config import TARGET

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAIN_PATH = PROJECT_ROOT / "data" / "train_70.csv"


@pytest.fixture
def toy() -> pd.DataFrame:
    """8 invented customers: 4 in segment A (with some missing values), 4 in B."""
    return pd.DataFrame(
        {
            "ID": range(1, 9),
            "Gender": ["Male", "Male", "Male", "Female"] + ["Female"] * 4,
            "Ever_Married": ["Yes", "Yes", "No", None] + ["Yes"] * 4,
            "Age": [20, 30, 40, 50] + [60] * 4,
            "Graduated": ["Yes", "No", "No", "No"] + ["Yes"] * 4,
            "Profession": ["Artist", "Artist", "Doctor", None] + ["Doctor"] * 4,
            "Work_Experience": [1.0, 1.0, 3.0, None] + [0.0] * 4,
            "Spending_Score": ["High", "Low", "Low", "Low"]
            + ["High", "High", "High", "Average"],
            "Family_Size": [2.0] * 4 + [4.0] * 4,
            TARGET: ["A"] * 4 + ["B"] * 4,
        }
    )


@pytest.fixture
def profile(toy: pd.DataFrame) -> pd.DataFrame:
    return segment_profile.build_profile_table(toy).set_index("segment")


def test_one_row_per_segment_plus_all(profile: pd.DataFrame) -> None:
    assert list(profile.index) == ["A", "B", "All"]
    assert profile.loc["A", "n_customers"] == 4
    assert profile.loc["All", "n_customers"] == 8
    assert profile.loc["A", "pct_of_train"] == 50.0
    assert profile.loc["All", "pct_of_train"] == 100.0


def test_numeric_summaries_ignore_missing_values(profile: pd.DataFrame) -> None:
    assert profile.loc["A", "age_median"] == 35.0
    # Work_Experience in A: 1, 1, 3 and one missing -> median 1, mean 5/3.
    assert profile.loc["A", "work_experience_median"] == 1.0
    assert profile.loc["A", "work_experience_mean"] == 1.67
    assert profile.loc["A", "work_experience_missing"] == 1
    assert profile.loc["B", "work_experience_missing"] == 0


def test_percentages_exclude_missing_from_the_denominator(profile: pd.DataFrame) -> None:
    # Ever_Married in A: Yes, Yes, No and one missing -> 2 of 3, not 2 of 4.
    assert profile.loc["A", "pct_ever_married_yes"] == 66.7
    assert profile.loc["A", "ever_married_missing"] == 1
    assert profile.loc["A", "pct_gender_male"] == 75.0
    assert profile.loc["A", "pct_graduated_yes"] == 25.0
    assert profile.loc["B", "pct_ever_married_yes"] == 100.0


def test_top_profession(profile: pd.DataFrame) -> None:
    assert profile.loc["A", "top_profession"] == "Artist"
    assert profile.loc["A", "pct_top_profession"] == 66.7
    assert profile.loc["A", "profession_missing"] == 1
    assert profile.loc["B", "top_profession"] == "Doctor"


def test_high_spenders_per_segment(profile: pd.DataFrame) -> None:
    assert profile.loc["A", "n_spending_high"] == 1
    assert profile.loc["B", "n_spending_high"] == 3
    assert profile.loc["A", "pct_spending_high"] == 25.0
    assert profile.loc["B", "pct_spending_high"] == 75.0
    # The 4 high spenders are split 1 / 3 between the segments.
    assert profile.loc["A", "pct_of_all_high"] == 25.0
    assert profile.loc["B", "pct_of_all_high"] == 75.0
    assert profile.loc["All", "pct_of_all_high"] == 100.0


def test_spending_shares_add_up_to_100(profile: pd.DataFrame) -> None:
    columns = ["pct_spending_low", "pct_spending_average", "pct_spending_high"]
    assert profile[columns].sum(axis=1).tolist() == pytest.approx([100.0] * 3, abs=0.2)


def test_distribution_table_keeps_levels_absent_from_a_segment(toy: pd.DataFrame) -> None:
    table = segment_profile.build_distribution_table(toy)
    assert list(table.columns) == [
        "variable",
        "level",
        "segment",
        "count",
        "pct_within_segment",
    ]
    # Nobody in B is an Artist: the row exists with a zero, it is not dropped.
    row = table[
        (table["variable"] == "Profession")
        & (table["level"] == "Artist")
        & (table["segment"] == "B")
    ]
    assert len(row) == 1
    assert row["count"].item() == 0
    assert row["pct_within_segment"].item() == 0.0


def test_distribution_shares_add_up_to_100(toy: pd.DataFrame) -> None:
    table = segment_profile.build_distribution_table(toy)
    totals = table.groupby(["variable", "segment"])["pct_within_segment"].sum()
    assert totals.tolist() == pytest.approx([100.0] * len(totals), abs=0.2)


def test_input_dataframe_is_not_modified(toy: pd.DataFrame) -> None:
    before = toy.copy(deep=True)
    segment_profile.build_profile_table(toy)
    segment_profile.build_distribution_table(toy)
    pd.testing.assert_frame_equal(toy, before)


def test_checksum_is_the_same_with_lf_and_crlf(tmp_path: Path) -> None:
    lf = tmp_path / "lf.csv"
    crlf = tmp_path / "crlf.csv"
    lf.write_bytes(b"ID,Age\n1,20\n")
    crlf.write_bytes(b"ID,Age\r\n1,20\r\n")
    assert segment_profile.sha256_lf(lf) == segment_profile.sha256_lf(crlf)


def test_main_stops_if_the_file_is_not_the_shared_partition(
    toy: pd.DataFrame, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    other = tmp_path / "other.csv"
    toy.to_csv(other, index=False)
    out_dir = tmp_path / "reports"
    monkeypatch.setattr(
        sys,
        "argv",
        ["segment_profile", "--train", str(other), "--reports-dir", str(out_dir)],
    )
    with pytest.raises(SystemExit, match="not the shared train partition"):
        segment_profile.main()
    # Nothing is written when the check fails.
    assert not list(out_dir.glob("*.csv"))


def test_profile_on_the_real_train_split() -> None:
    """Structure only: the figures themselves live in the recorded CSV."""
    train = pd.read_csv(TRAIN_PATH)
    table = segment_profile.build_profile_table(train).set_index("segment")
    assert list(table.index) == ["A", "B", "C", "D", "All"]
    segments = table.drop(index="All")
    assert segments["n_customers"].sum() == segment_profile.EXPECTED_ROWS
    assert segments["n_spending_high"].sum() == table.loc["All", "n_spending_high"]
    assert not table.isna().any().any()

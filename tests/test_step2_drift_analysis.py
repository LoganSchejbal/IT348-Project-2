"""Tests for Step 2 (Handle Data Drift).

These tests check what the assignment and PLAN.md say Step 2 should do:
measure feature drift between years with the two-sample Kolmogorov-Smirnov
test, keep the KS statistic bounded in [0, 1], detect a clearly shifted
feature while not flagging identical distributions, rank features and
year-pairs by drift, and specifically compare the earliest and latest
year rather than an arbitrary pair. Most tests use small synthetic data
so they run in seconds; tests that need the real dataset use the
`real_data_dir` fixture and are skipped when input_data/ is empty.
"""

import numpy as np
import pandas as pd
import pytest

from drift_analysis import (
    compare_earliest_latest_year,
    compute_drift_across_years,
    compute_drift_between_years,
    ks_test_feature,
    most_different_year_pairs,
    top_drifting_features,
)

try:
    from data_loader import get_feature_columns, load_all_years
except ImportError:  # pragma: no cover - only needed for real-data tests
    get_feature_columns = None
    load_all_years = None


RNG_SEED = 42


def _make_year_data(n_rows: int = 200) -> dict[int, pd.DataFrame]:
    """Build a small synthetic year_data dict shaped like Step 1's output.

    Three years, two features: `stable` is drawn from the same distribution
    in every year, `shifted` is drawn from a clearly different distribution
    in the latest year, so drift-detection behavior can be checked against
    a known ground truth.

    Args:
        n_rows: Number of synthetic rows per year.

    Returns:
        A dict mapping year to a dataframe with columns `stable`, `shifted`,
        `label`, `year`, matching the shape `load_all_years` produces.
    """
    rng = np.random.default_rng(RNG_SEED)
    years = [2014, 2015, 2016]
    year_data = {}
    for i, year in enumerate(years):
        stable = rng.normal(loc=0.0, scale=1.0, size=n_rows)
        # Only the final year's "shifted" feature comes from a different
        # distribution, so (2014, 2016) should show far more drift than
        # (2014, 2015).
        shift_amount = 10.0 if year == years[-1] else 0.0
        shifted = rng.normal(loc=shift_amount, scale=1.0, size=n_rows)
        year_data[year] = pd.DataFrame(
            {
                "stable": stable,
                "shifted": shifted,
                "label": rng.integers(0, 2, size=n_rows),
                "year": year,
            }
        )
    return year_data


@pytest.fixture
def synthetic_year_data():
    """A 3-year synthetic year_data dict with one stable and one drifting feature."""
    return _make_year_data()


FEATURE_COLS = ["stable", "shifted"]


# --- KS statistic is bounded in [0, 1] --------------------------------------


def test_ks_test_feature_statistic_in_unit_interval():
    """The KS statistic returned for any two samples must lie in [0, 1]."""
    rng = np.random.default_rng(RNG_SEED)
    series_a = pd.Series(rng.normal(0, 1, 100))
    series_b = pd.Series(rng.normal(5, 2, 100))
    statistic, p_value = ks_test_feature(series_a, series_b)
    assert 0.0 <= statistic <= 1.0
    assert 0.0 <= p_value <= 1.0


def test_compute_drift_between_years_statistics_in_unit_interval(synthetic_year_data):
    """Every per-feature statistic from compute_drift_between_years must be in [0, 1]."""
    drift_df = compute_drift_between_years(synthetic_year_data, 2014, 2016, FEATURE_COLS)
    assert (drift_df["statistic"] >= 0.0).all()
    assert (drift_df["statistic"] <= 1.0).all()


# --- Identical distributions produce no (or negligible) drift ---------------


def test_ks_test_feature_identical_distribution_near_zero_statistic():
    """Two samples drawn from the same distribution should show ~no drift."""
    rng = np.random.default_rng(RNG_SEED)
    series_a = pd.Series(rng.normal(0, 1, 500))
    series_b = pd.Series(rng.normal(0, 1, 500))
    statistic, _ = ks_test_feature(series_a, series_b)
    assert statistic < 0.15


def test_ks_test_feature_same_values_statistic_is_zero():
    """Comparing a sample to an exact copy of itself must give statistic 0."""
    series_a = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0] * 20)
    series_b = series_a.copy()
    statistic, p_value = ks_test_feature(series_a, series_b)
    assert statistic == 0.0
    assert p_value == 1.0


def test_compute_drift_between_years_stable_feature_low_statistic(synthetic_year_data):
    """The feature with no real shift between years should report low drift."""
    drift_df = compute_drift_between_years(synthetic_year_data, 2014, 2015, FEATURE_COLS)
    assert drift_df.loc["stable", "statistic"] < 0.3


# --- A clearly shifted synthetic feature is detected -------------------------


def test_ks_test_feature_shifted_distribution_detected():
    """A clearly shifted synthetic feature must produce a high KS statistic."""
    rng = np.random.default_rng(RNG_SEED)
    series_a = pd.Series(rng.normal(0, 1, 300))
    series_b = pd.Series(rng.normal(10, 1, 300))
    statistic, p_value = ks_test_feature(series_a, series_b)
    assert statistic > 0.9
    assert p_value < 0.01


def test_compute_drift_between_years_shifted_feature_detected(synthetic_year_data):
    """The deliberately shifted feature must show much more drift than the stable one."""
    drift_df = compute_drift_between_years(synthetic_year_data, 2014, 2016, FEATURE_COLS)
    assert drift_df.loc["shifted", "statistic"] > drift_df.loc["stable", "statistic"]
    assert drift_df.loc["shifted", "statistic"] > 0.8


def test_compute_drift_between_years_one_row_per_feature(synthetic_year_data):
    """compute_drift_between_years must return exactly one row per requested feature."""
    drift_df = compute_drift_between_years(synthetic_year_data, 2014, 2015, FEATURE_COLS)
    assert set(drift_df.index) == set(FEATURE_COLS)
    assert len(drift_df) == len(FEATURE_COLS)
    assert list(drift_df.columns) == ["statistic", "p_value"]


# --- compute_drift_across_years covers consecutive year pairs ---------------


def test_compute_drift_across_years_covers_consecutive_pairs(synthetic_year_data):
    """compute_drift_across_years must produce one row per (consecutive year pair, feature)."""
    drift_df = compute_drift_across_years(synthetic_year_data, FEATURE_COLS)
    pairs = set(zip(drift_df["year_a"], drift_df["year_b"]))
    assert pairs == {(2014, 2015), (2015, 2016)}
    assert len(drift_df) == 2 * len(FEATURE_COLS)


# --- top_drifting_features sorts descending by statistic --------------------


def test_top_drifting_features_sorted_descending(synthetic_year_data):
    """top_drifting_features must return rows sorted descending by statistic."""
    drift_df = compute_drift_between_years(synthetic_year_data, 2014, 2016, FEATURE_COLS)
    top = top_drifting_features(drift_df, top_n=2)
    assert list(top["statistic"]) == sorted(top["statistic"], reverse=True)
    assert top.iloc[0].name == "shifted"


def test_top_drifting_features_respects_top_n(synthetic_year_data):
    """top_drifting_features must cap the number of rows returned at top_n."""
    drift_df = compute_drift_between_years(synthetic_year_data, 2014, 2016, FEATURE_COLS)
    top = top_drifting_features(drift_df, top_n=1)
    assert len(top) == 1


# --- compare_earliest_latest_year picks min/max years, not any other pair ---


def test_compare_earliest_latest_year_uses_min_and_max_years(synthetic_year_data):
    """compare_earliest_latest_year must compare min(years) vs max(years), not a middle pair."""
    result = compare_earliest_latest_year(synthetic_year_data, FEATURE_COLS)
    direct = compute_drift_between_years(synthetic_year_data, 2014, 2016, FEATURE_COLS)
    pd.testing.assert_frame_equal(result, direct)


def test_compare_earliest_latest_year_not_equal_to_consecutive_pair(synthetic_year_data):
    """The earliest-vs-latest comparison should differ from a consecutive-year comparison here."""
    earliest_latest = compare_earliest_latest_year(synthetic_year_data, FEATURE_COLS)
    consecutive = compute_drift_between_years(synthetic_year_data, 2014, 2015, FEATURE_COLS)
    assert earliest_latest.loc["shifted", "statistic"] != consecutive.loc["shifted", "statistic"]


# --- most_different_year_pairs ranks pairs by aggregated drift --------------


def test_most_different_year_pairs_ranks_descending_by_mean(synthetic_year_data):
    """most_different_year_pairs must rank year pairs descending by mean_statistic."""
    across = compute_drift_across_years(synthetic_year_data, FEATURE_COLS)
    ranked = most_different_year_pairs(across)
    assert list(ranked["mean_statistic"]) == sorted(
        ranked["mean_statistic"], reverse=True
    )
    # (2015, 2016) has the shifted feature changing; it should outrank (2014, 2015).
    top_pair = (ranked.iloc[0]["year_a"], ranked.iloc[0]["year_b"])
    assert top_pair == (2015, 2016)


def test_most_different_year_pairs_has_mean_and_max_columns(synthetic_year_data):
    """most_different_year_pairs must report both mean_statistic and max_statistic."""
    across = compute_drift_across_years(synthetic_year_data, FEATURE_COLS)
    ranked = most_different_year_pairs(across)
    assert {"year_a", "year_b", "mean_statistic", "max_statistic"}.issubset(ranked.columns)
    assert len(ranked) == 2  # (2014,2015) and (2015,2016)


# --- Real dataset checks (skipped if input_data/ is empty) ------------------


def test_real_data_drift_statistics_in_unit_interval(real_data_dir):
    """On the real dataset, every KS statistic between the earliest and latest year must be in [0, 1]."""
    if load_all_years is None or get_feature_columns is None:
        pytest.skip("data_loader module not available")
    year_data = load_all_years(real_data_dir)
    if not year_data:
        pytest.skip("No dataset files found in input_data/")
    feature_cols = get_feature_columns(next(iter(year_data.values())))
    result = compare_earliest_latest_year(year_data, feature_cols)
    assert (result["statistic"] >= 0.0).all()
    assert (result["statistic"] <= 1.0).all()

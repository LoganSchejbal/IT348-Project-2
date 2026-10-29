"""Tests for Step 3 (Preprocess Data for Model Training).

These tests check what the assignment and PLAN.md say Step 3 should do:
split years into a training half and a testing half with no overlap,
concatenate per-year data into train/test dataframes without crossing the
year boundary, fit the StandardScaler on training years only (so training
columns have mean ~0 after transform and test data is only ever
transformed, never refit), and keep train/test feature columns identical
and in the same order. Most tests use small synthetic data so they run in
seconds; a test that needs the real dataset uses the `real_data_dir`
fixture and is skipped when input_data/ is empty.
"""

import numpy as np
import pandas as pd
import pytest

from preprocessing import (
    fit_scaler,
    prepare_train_test,
    scale_features,
    split_by_year,
    split_years_in_half,
)

try:
    from data_loader import get_feature_columns, load_all_years
except ImportError:  # pragma: no cover - only needed for real-data tests
    get_feature_columns = None
    load_all_years = None


RNG_SEED = 42
FEATURE_COLS = ["feat_a", "feat_b"]


def _make_year_data(years: list[int], n_rows: int = 50) -> dict[int, pd.DataFrame]:
    """Build a small synthetic year_data dict shaped like Step 1's output.

    Each year's features are drawn from a distribution that shifts with
    the year, so a scaler fit on only some years should not produce a
    mean of ~0 on the other years (used to confirm leakage would be
    detectable if it happened).

    Args:
        years: Years to generate data for.
        n_rows: Number of synthetic rows per year.

    Returns:
        A dict mapping year to a dataframe with columns `feat_a`,
        `feat_b`, `label`, `year`, matching the shape `load_all_years`
        produces.
    """
    rng = np.random.default_rng(RNG_SEED)
    year_data = {}
    for i, year in enumerate(years):
        shift = float(i) * 5.0
        year_data[year] = pd.DataFrame(
            {
                "feat_a": rng.normal(loc=shift, scale=1.0, size=n_rows),
                "feat_b": rng.normal(loc=shift * 2.0, scale=2.0, size=n_rows),
                "label": rng.integers(0, 2, size=n_rows),
                "year": year,
            }
        )
    return year_data


@pytest.fixture
def synthetic_year_data():
    """A 4-year synthetic year_data dict with per-year distribution shift."""
    return _make_year_data([2014, 2015, 2016, 2017])


# --- split_years_in_half divides into (near-)equal halves, no overlap ------


def test_split_years_in_half_even_count_equal_halves():
    """An even number of years must split into two equal, non-overlapping halves."""
    train_years, test_years = split_years_in_half([2014, 2015, 2016, 2017])
    assert train_years == [2014, 2015]
    assert test_years == [2016, 2017]
    assert set(train_years).isdisjoint(set(test_years))


def test_split_years_in_half_odd_count_extra_year_in_train():
    """An odd number of years must give the earlier half the extra year."""
    train_years, test_years = split_years_in_half([2014, 2015, 2016])
    assert train_years == [2014, 2015]
    assert test_years == [2016]
    assert set(train_years).isdisjoint(set(test_years))


def test_split_years_in_half_sorts_unordered_input():
    """The split must be chronological regardless of input order."""
    train_years, test_years = split_years_in_half([2017, 2014, 2016, 2015])
    assert train_years == [2014, 2015]
    assert test_years == [2016, 2017]


def test_split_years_in_half_every_year_assigned_exactly_once():
    """Every input year must appear in exactly one of the two output lists."""
    years = [2014, 2015, 2016, 2017, 2018]
    train_years, test_years = split_years_in_half(years)
    assert sorted(train_years + test_years) == sorted(years)
    assert len(set(train_years) & set(test_years)) == 0


def test_split_years_in_half_too_few_years_raises():
    """Fewer than 2 distinct years cannot be split into train and test."""
    with pytest.raises(ValueError):
        split_years_in_half([2014])


# --- split_by_year raises on unknown years, respects the year boundary -----


def test_split_by_year_raises_on_unknown_year(synthetic_year_data):
    """Requesting a year not present in year_data must raise ValueError."""
    with pytest.raises(ValueError):
        split_by_year(synthetic_year_data, train_years=[2014, 2099], test_years=[2016])


def test_split_by_year_no_shared_years_between_train_and_test(synthetic_year_data):
    """Train and test dataframes must be built from disjoint sets of years."""
    train_df, test_df = split_by_year(
        synthetic_year_data, train_years=[2014, 2015], test_years=[2016, 2017]
    )
    assert set(train_df["year"].unique()).isdisjoint(set(test_df["year"].unique()))
    assert set(train_df["year"].unique()) == {2014, 2015}
    assert set(test_df["year"].unique()) == {2016, 2017}


def test_split_by_year_row_counts_match_requested_years(synthetic_year_data):
    """The concatenated frames must contain exactly the rows of the requested years."""
    train_df, test_df = split_by_year(
        synthetic_year_data, train_years=[2014, 2015], test_years=[2016, 2017]
    )
    assert len(train_df) == len(synthetic_year_data[2014]) + len(synthetic_year_data[2015])
    assert len(test_df) == len(synthetic_year_data[2016]) + len(synthetic_year_data[2017])


# --- The scaler is fit on training years only -------------------------------


def test_fit_scaler_mean_matches_manual_training_mean(synthetic_year_data):
    """The scaler's learned mean must match a hand-computed mean of only the training years."""
    train_df, _ = split_by_year(
        synthetic_year_data, train_years=[2014, 2015], test_years=[2016, 2017]
    )
    scaler = fit_scaler(train_df, FEATURE_COLS)
    expected_mean = train_df[FEATURE_COLS].mean().to_numpy()
    assert np.allclose(scaler.mean_, expected_mean)


def test_fit_scaler_ignores_test_year_distribution(synthetic_year_data):
    """The scaler's mean must not be influenced by the (differently-shifted) test years."""
    train_df, test_df = split_by_year(
        synthetic_year_data, train_years=[2014, 2015], test_years=[2016, 2017]
    )
    scaler = fit_scaler(train_df, FEATURE_COLS)
    test_only_mean = test_df[FEATURE_COLS].mean().to_numpy()
    # Train and test years were generated with a clear distribution shift,
    # so a scaler that leaked test-year data would not match this closely.
    assert not np.allclose(scaler.mean_, test_only_mean, atol=1.0)


def test_scaled_training_columns_have_mean_near_zero(synthetic_year_data):
    """Transforming the training data with its own fitted scaler must give ~0 mean columns."""
    train_df, _ = split_by_year(
        synthetic_year_data, train_years=[2014, 2015], test_years=[2016, 2017]
    )
    scaler = fit_scaler(train_df, FEATURE_COLS)
    X_train = scale_features(train_df, FEATURE_COLS, scaler)
    assert np.allclose(X_train.mean(axis=0), 0.0, atol=1e-8)


def test_scale_features_never_refits_scaler(synthetic_year_data):
    """Scaling the test set must not change the scaler's learned mean/scale."""
    train_df, test_df = split_by_year(
        synthetic_year_data, train_years=[2014, 2015], test_years=[2016, 2017]
    )
    scaler = fit_scaler(train_df, FEATURE_COLS)
    mean_before = scaler.mean_.copy()
    scale_before = scaler.scale_.copy()
    scale_features(test_df, FEATURE_COLS, scaler)
    assert np.array_equal(scaler.mean_, mean_before)
    assert np.array_equal(scaler.scale_, scale_before)


def test_scaled_test_columns_not_necessarily_mean_zero(synthetic_year_data):
    """Transformed test data, scaled with the training scaler, should reflect the drift (not be re-centered to 0)."""
    train_df, test_df = split_by_year(
        synthetic_year_data, train_years=[2014, 2015], test_years=[2016, 2017]
    )
    scaler = fit_scaler(train_df, FEATURE_COLS)
    X_test = scale_features(test_df, FEATURE_COLS, scaler)
    # Since test years were generated with a deliberate distribution shift
    # relative to train years, a scaler fit only on train should leave the
    # transformed test data noticeably off-center.
    assert not np.allclose(X_test.mean(axis=0), 0.0, atol=0.5)


# --- Training and test sets share no years ----------------------------------


def test_prepare_train_test_shares_no_years(synthetic_year_data):
    """The years used to build X_train/y_train and X_test/y_test must not overlap."""
    train_years = [2014, 2015]
    test_years = [2016, 2017]
    assert set(train_years).isdisjoint(set(test_years))
    X_train, X_test, y_train, y_test, scaler = prepare_train_test(
        synthetic_year_data, FEATURE_COLS, train_years, test_years
    )
    assert X_train.shape[0] == len(y_train)
    assert X_test.shape[0] == len(y_test)


# --- Train and test have identical columns in the same order ----------------


def test_prepare_train_test_same_number_of_feature_columns(synthetic_year_data):
    """X_train and X_test must have the same number of feature columns."""
    X_train, X_test, _, _, _ = prepare_train_test(
        synthetic_year_data, FEATURE_COLS, [2014, 2015], [2016, 2017]
    )
    assert X_train.shape[1] == X_test.shape[1] == len(FEATURE_COLS)


def test_scale_features_preserves_feature_cols_order(synthetic_year_data):
    """Scaling with a reversed feature_cols order must change which column holds which feature."""
    train_df, test_df = split_by_year(
        synthetic_year_data, train_years=[2014, 2015], test_years=[2016, 2017]
    )
    scaler = fit_scaler(train_df, FEATURE_COLS)
    X_test_forward = scale_features(test_df, FEATURE_COLS, scaler)

    reversed_cols = list(reversed(FEATURE_COLS))
    scaler_reversed = fit_scaler(train_df, reversed_cols)
    X_test_reversed = scale_features(test_df, reversed_cols, scaler_reversed)

    # Column 0 under the forward order is feat_a; column 0 under the
    # reversed order is feat_b. They must disagree, proving scale_features
    # keeps whatever column order feature_cols specifies rather than some
    # fixed internal order.
    assert not np.allclose(X_test_forward[:, 0], X_test_reversed[:, 0])


def test_prepare_train_test_output_shapes_match_row_counts(synthetic_year_data):
    """X_train/X_test/y_train/y_test shapes must match the row counts of the requested years."""
    train_years = [2014, 2015]
    test_years = [2016, 2017]
    X_train, X_test, y_train, y_test, scaler = prepare_train_test(
        synthetic_year_data, FEATURE_COLS, train_years, test_years
    )
    expected_train_rows = sum(len(synthetic_year_data[y]) for y in train_years)
    expected_test_rows = sum(len(synthetic_year_data[y]) for y in test_years)
    assert X_train.shape == (expected_train_rows, len(FEATURE_COLS))
    assert X_test.shape == (expected_test_rows, len(FEATURE_COLS))
    assert len(y_train) == expected_train_rows
    assert len(y_test) == expected_test_rows


def test_prepare_train_test_returns_fitted_scaler(synthetic_year_data):
    """prepare_train_test must return a scaler already fit (mean_ present) on train years only."""
    train_years = [2014, 2015]
    X_train, X_test, y_train, y_test, scaler = prepare_train_test(
        synthetic_year_data, FEATURE_COLS, train_years, [2016, 2017]
    )
    train_df, _ = split_by_year(synthetic_year_data, train_years, [2016, 2017])
    assert np.allclose(scaler.mean_, train_df[FEATURE_COLS].mean().to_numpy())


# --- Real dataset checks (skipped if input_data/ is empty) ------------------


def test_real_data_train_test_share_no_years_and_same_columns(real_data_dir):
    """On the real dataset, split_years_in_half's halves share no years and prepare_train_test gives matching column counts for train/test."""
    if load_all_years is None or get_feature_columns is None:
        pytest.skip("data_loader module not available")
    year_data = load_all_years(real_data_dir)
    if not year_data:
        pytest.skip("No dataset files found in input_data/")
    years = list(year_data.keys())
    train_years, test_years = split_years_in_half(years)
    assert set(train_years).isdisjoint(set(test_years))

    feature_cols = get_feature_columns(next(iter(year_data.values())))
    X_train, X_test, y_train, y_test, scaler = prepare_train_test(
        year_data, feature_cols, train_years, test_years
    )
    assert X_train.shape[1] == X_test.shape[1] == len(feature_cols)
    # The scaler was fit on training years only, so the training data it
    # transformed should be centered near 0.
    assert np.allclose(X_train.mean(axis=0), 0.0, atol=1e-6)

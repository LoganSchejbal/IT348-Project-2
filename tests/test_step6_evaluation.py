"""Tests for Step 6 (Test Data Prediction).

These tests check what the assignment and PLAN.md say `evaluate_by_year`
(src/evaluation.py) should do: predict with each trained classifier on
each individual test year separately, returning one row per
(year, classifier) with accuracy/precision/recall/F1 all in [0, 1], using
the already-fit StandardScaler only to `.transform()` each year's
features -- never to re-fit it, since re-fitting on a test year would
leak that year into the scaler (PLAN.md Step 6 and the leakage-prevention
section). All tests use small synthetic data or fake stand-ins, so they
run in seconds; one additionally exercises the real pipeline when
input_data/ is present, via the `real_data_dir` fixture.
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.preprocessing import StandardScaler

from evaluation import evaluate_by_year


class _FixedPredictModel:
    """A fake classifier stand-in that always returns a fixed prediction array.

    Mirrors the stand-in used in test_step5_evaluation.py so Step 6 tests
    can hand-check results without depending on real estimator training.
    """

    def __init__(self, fixed_predictions: np.ndarray):
        """Store the predictions `.predict()` will always return.

        Args:
            fixed_predictions: The array `.predict()` returns regardless
                of the input passed to it.
        """
        self.fixed_predictions = np.asarray(fixed_predictions)

    def predict(self, X):
        """Ignore `X` and return the stored fixed predictions."""
        return self.fixed_predictions

    def fit(self, X, y):
        """Should never be called by evaluation code; included so a stray
        call fails loudly rather than raising AttributeError."""
        raise AssertionError("evaluate_by_year must never call .fit() on a model")


class _RecordingFitScaler:
    """A StandardScaler-like stand-in that flags if `.fit()` is ever called.

    `.transform()` behaves like an already-fit `StandardScaler` (returns
    the input unchanged, as if mean=0/scale=1), while `.fit()` records
    that it was invoked so a test can assert it never is.
    """

    def __init__(self):
        """Start with no recorded fit calls."""
        self.fit_called = False

    def transform(self, X):
        """Return `X` as a plain numpy array, unchanged."""
        return np.asarray(X)

    def fit(self, X):
        """Record that fitting was attempted; evaluate_by_year must not do this."""
        self.fit_called = True
        return self


def _make_year_df(feature_cols: list[str], labels: list[int]) -> pd.DataFrame:
    """Build a tiny synthetic per-year dataframe with the given labels.

    Args:
        feature_cols: Names of the feature columns to fill with zeros.
        labels: The `label` column values; the row count is `len(labels)`.

    Returns:
        A dataframe with one row per label, zero-valued feature columns,
        and a `label` column.
    """
    data = {col: np.zeros(len(labels)) for col in feature_cols}
    data["label"] = labels
    return pd.DataFrame(data)


FEATURE_COLS = ["f1", "f2"]


# --- evaluate_by_year returns one row per (year, classifier) combination


def test_evaluate_by_year_returns_one_row_per_year_classifier_combination():
    """Output must have exactly len(years) * len(models) rows."""
    year_data = {
        2018: _make_year_df(FEATURE_COLS, [0, 1, 0, 1]),
        2019: _make_year_df(FEATURE_COLS, [1, 0, 1, 0]),
        2020: _make_year_df(FEATURE_COLS, [0, 0, 1, 1]),
    }
    models = {
        "a": _FixedPredictModel([0, 1, 0, 1]),
        "b": _FixedPredictModel([1, 1, 0, 0]),
    }
    scaler = _RecordingFitScaler()
    years = [2018, 2019, 2020]

    result = evaluate_by_year(models, year_data, FEATURE_COLS, scaler, years)

    assert len(result) == len(years) * len(models)
    seen = set(zip(result["year"], result["classifier"]))
    expected = {(year, name) for year in years for name in models}
    assert seen == expected


def test_evaluate_by_year_only_covers_requested_years():
    """Years present in year_data but not in `years` must be excluded."""
    year_data = {
        2018: _make_year_df(FEATURE_COLS, [0, 1]),
        2019: _make_year_df(FEATURE_COLS, [1, 0]),
        2020: _make_year_df(FEATURE_COLS, [0, 0]),
    }
    models = {"a": _FixedPredictModel([0, 1])}
    scaler = _RecordingFitScaler()

    result = evaluate_by_year(models, year_data, FEATURE_COLS, scaler, years=[2018, 2020])

    assert set(result["year"]) == {2018, 2020}


def test_evaluate_by_year_columns_are_correct():
    """Output must contain exactly year, classifier, and the four metrics."""
    year_data = {2018: _make_year_df(FEATURE_COLS, [0, 1, 0, 1])}
    models = {"a": _FixedPredictModel([0, 1, 1, 1])}
    scaler = _RecordingFitScaler()

    result = evaluate_by_year(models, year_data, FEATURE_COLS, scaler, years=[2018])

    assert set(result.columns) == {"year", "classifier", "accuracy", "precision", "recall", "f1"}


# --- all metric values are between 0 and 1


def test_evaluate_by_year_metrics_are_within_unit_interval():
    """Every accuracy/precision/recall/f1 value must lie in [0, 1]."""
    year_data = {
        2018: _make_year_df(FEATURE_COLS, [0, 1, 0, 1, 1, 0]),
        2019: _make_year_df(FEATURE_COLS, [1, 1, 1, 0, 0, 0]),
    }
    models = {
        "always_benign": _FixedPredictModel([0, 0, 0, 0, 0, 0]),
        "always_malware": _FixedPredictModel([1, 1, 1, 1, 1, 1]),
        "mixed": _FixedPredictModel([1, 0, 1, 1, 0, 0]),
    }
    scaler = _RecordingFitScaler()

    result = evaluate_by_year(models, year_data, FEATURE_COLS, scaler, years=[2018, 2019])

    metric_cols = ["accuracy", "precision", "recall", "f1"]
    for _, row in result.iterrows():
        for metric in metric_cols:
            value = row[metric]
            assert 0.0 <= value <= 1.0, f"{metric} out of [0, 1] for {row['year']}/{row['classifier']}: {value}"


def test_evaluate_by_year_perfect_and_worst_case_metrics_at_the_boundaries():
    """A perfect predictor scores 1.0 on every metric; an always-wrong,
    always-benign predictor against an all-malware year scores 0.0 on
    precision/recall/f1 and accuracy, bounding the metrics at both ends."""
    year_data = {2018: _make_year_df(FEATURE_COLS, [1, 1, 1, 1])}
    models = {
        "perfect": _FixedPredictModel([1, 1, 1, 1]),
        "always_benign": _FixedPredictModel([0, 0, 0, 0]),
    }
    scaler = _RecordingFitScaler()

    result = evaluate_by_year(models, year_data, FEATURE_COLS, scaler, years=[2018])

    perfect_row = result[result["classifier"] == "perfect"].iloc[0]
    for metric in ("accuracy", "precision", "recall", "f1"):
        assert perfect_row[metric] == pytest.approx(1.0)

    worst_row = result[result["classifier"] == "always_benign"].iloc[0]
    for metric in ("accuracy", "precision", "recall", "f1"):
        assert worst_row[metric] == pytest.approx(0.0)


# --- evaluate_by_year never re-fits the scaler


def test_evaluate_by_year_never_calls_scaler_fit():
    """The scaler must only be `.transform()`-ed, never `.fit()`-ed."""
    year_data = {
        2018: _make_year_df(FEATURE_COLS, [0, 1, 0, 1]),
        2019: _make_year_df(FEATURE_COLS, [1, 0, 1, 0]),
    }
    models = {"a": _FixedPredictModel([0, 1, 0, 1])}
    scaler = _RecordingFitScaler()

    evaluate_by_year(models, year_data, FEATURE_COLS, scaler, years=[2018, 2019])

    assert scaler.fit_called is False


def test_evaluate_by_year_does_not_change_a_real_scalers_learned_parameters():
    """With a real fitted StandardScaler, mean_/scale_ must be unchanged
    before and after calling evaluate_by_year on other years' data."""
    train_df = _make_year_df(FEATURE_COLS, [0, 1, 0, 1])
    train_df["f1"] = [1.0, 2.0, 3.0, 4.0]
    train_df["f2"] = [10.0, 20.0, 30.0, 40.0]
    scaler = StandardScaler()
    scaler.fit(train_df[FEATURE_COLS])
    mean_before = scaler.mean_.copy()
    scale_before = scaler.scale_.copy()

    year_data = {
        2018: _make_year_df(FEATURE_COLS, [0, 1, 0, 1]),
        2019: _make_year_df(FEATURE_COLS, [1, 0, 1, 0]),
    }
    models = {"a": _FixedPredictModel([0, 1, 0, 1])}

    evaluate_by_year(models, year_data, FEATURE_COLS, scaler, years=[2018, 2019])

    np.testing.assert_array_equal(scaler.mean_, mean_before)
    np.testing.assert_array_equal(scaler.scale_, scale_before)


# --- evaluate_by_year scores each year against that year's own true labels


def test_evaluate_by_year_scores_each_year_against_its_own_labels():
    """Metrics must reflect each year's own labels, not another year's --
    a model predicting the same fixed array scores differently across
    two years with different true labels."""
    year_data = {
        2018: _make_year_df(FEATURE_COLS, [0, 1, 0, 1]),  # matches the prediction
        2019: _make_year_df(FEATURE_COLS, [1, 0, 1, 0]),  # mismatches the prediction
    }
    models = {"a": _FixedPredictModel([0, 1, 0, 1])}
    scaler = _RecordingFitScaler()

    result = evaluate_by_year(models, year_data, FEATURE_COLS, scaler, years=[2018, 2019])

    acc_2018 = result[result["year"] == 2018].iloc[0]["accuracy"]
    acc_2019 = result[result["year"] == 2019].iloc[0]["accuracy"]
    assert acc_2018 == pytest.approx(1.0)
    assert acc_2019 == pytest.approx(0.0)


# --- Integration: real pipeline


def test_evaluate_by_year_on_real_pipeline(real_data_dir):
    """End-to-end on the real dataset: one row per (test year, classifier),
    all metrics in [0, 1], and the scaler's fitted parameters unchanged
    after evaluating every test year."""
    from data_loader import get_feature_columns, load_all_years
    from models import get_classifiers, train_classifiers
    from preprocessing import prepare_train_test, split_years_in_half

    year_data = load_all_years(real_data_dir)
    years = sorted(year_data.keys())
    if len(years) < 2:
        pytest.skip("Need at least 2 years in input_data/ to split train/test")

    train_years, test_years = split_years_in_half(years)
    feature_cols = get_feature_columns(next(iter(year_data.values())))
    X_train, _X_test, y_train, _y_test, scaler = prepare_train_test(
        year_data, feature_cols, train_years, test_years
    )
    classifiers = train_classifiers(get_classifiers(), X_train, y_train)

    mean_before = scaler.mean_.copy()
    scale_before = scaler.scale_.copy()

    result = evaluate_by_year(classifiers, year_data, feature_cols, scaler, test_years)

    assert len(result) == len(test_years) * len(classifiers)
    assert set(result["year"]) == set(test_years)
    assert set(result["classifier"]) == set(classifiers.keys())

    metric_cols = ["accuracy", "precision", "recall", "f1"]
    for _, row in result.iterrows():
        for metric in metric_cols:
            assert 0.0 <= row[metric] <= 1.0

    np.testing.assert_array_equal(scaler.mean_, mean_before)
    np.testing.assert_array_equal(scaler.scale_, scale_before)

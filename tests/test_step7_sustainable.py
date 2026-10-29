"""Tests for Step 7 (Sustainable ML Approach).

These tests check what the assignment and PLAN.md say `src/sustainable.py`
should do:

- No model is ever trained on a year at or after the year it is tested on
  (`retraining_trajectory` must only fold a test year into the training
  pool *after* it has been scored, PLAN.md's Step 7 section and the
  leakage-prevention section).
- The retrained model actually incorporates newer data each round -- the
  training pool and the labels fit on must grow to include previously
  scored test years.
- The baseline ("static") model is never updated: `static_model_trajectory`
  must never call `.fit()` on a model or its scaler.

All tests use small synthetic data with fake classifier/scaler stand-ins,
so they run in seconds. One integration test additionally exercises the
real pipeline when input_data/ is present, via the `real_data_dir` fixture.
"""

import numpy as np
import pandas as pd
import pytest

from sustainable import (
    compare_static_vs_retrained,
    retraining_trajectory,
    run_sustainability_comparison,
    static_model_trajectory,
)


def _make_year_df(feature_cols: list[str], labels: list[int], feature_value: float = 0.0) -> pd.DataFrame:
    """Build a tiny synthetic per-year dataframe.

    Args:
        feature_cols: Names of the feature columns to fill.
        labels: The `label` column values; the row count is `len(labels)`.
        feature_value: Constant value every feature cell is filled with,
            so different years can be given visibly different feature
            values if a test needs that.

    Returns:
        A dataframe with one row per label, constant-valued feature
        columns, and a `label` column.
    """
    data = {col: np.full(len(labels), feature_value) for col in feature_cols}
    data["label"] = labels
    return pd.DataFrame(data)


FEATURE_COLS = ["f1", "f2"]


class _RecordingClassifier:
    """A fake classifier that records every `.fit()` call's inputs.

    Lets a test inspect exactly how many rows, and which labels, each
    retrain round actually trained on -- without depending on a real
    estimator's internals.
    """

    def __init__(self):
        """Start with no recorded fit calls."""
        self.fit_rows = None
        self.fit_labels = None

    def fit(self, X, y):
        """Record the number of rows and the label sequence trained on."""
        self.fit_rows = len(y)
        self.fit_labels = list(y)
        self.classes_ = np.unique(y)
        return self

    def predict(self, X):
        """Return an arbitrary, fixed-shape prediction (content unused)."""
        return np.zeros(len(X), dtype=int)


class _FitRaisingModel:
    """A fake fitted model whose `.fit()` raises if ever called.

    Used to prove a "static"/baseline model is never retrained by the
    function under test; a stray `.fit()` call fails loudly instead of
    passing silently.
    """

    def __init__(self, fixed_predictions: np.ndarray):
        """Store the predictions `.predict()` will always return."""
        self.fixed_predictions = np.asarray(fixed_predictions)

    def predict(self, X):
        """Ignore `X` and return the stored fixed predictions."""
        return self.fixed_predictions

    def fit(self, X, y):
        """Fail loudly: the static baseline must never be updated."""
        raise AssertionError("static_model_trajectory must never call .fit() on a model")


class _FitRaisingScaler:
    """A StandardScaler-like stand-in whose `.fit()` raises if ever called."""

    def transform(self, X):
        """Return `X` as a plain numpy array, unchanged."""
        return np.asarray(X)

    def fit(self, X):
        """Fail loudly: the static baseline's scaler must never be refit."""
        raise AssertionError("static_model_trajectory must never call .fit() on the scaler")


# --- No model is ever trained on a year at or after the year it is tested on


def test_retraining_trajectory_never_includes_the_current_or_future_test_year():
    """Each retrain round's training pool must contain exactly the rows of
    train_years plus the *already-scored* test years -- never the year
    about to be scored, and never a later one. Years are given distinct
    row counts so the pool size uniquely identifies which years were
    included; if the about-to-be-scored year had leaked in, every pool
    size below would be larger than expected."""
    year_data = {
        2018: _make_year_df(FEATURE_COLS, [0, 1, 0, 1]),           # 4 rows
        2019: _make_year_df(FEATURE_COLS, [1, 0, 1, 0, 1]),        # 5 rows
        2020: _make_year_df(FEATURE_COLS, [0, 1, 0, 1, 0, 1]),     # 6 rows
        2021: _make_year_df(FEATURE_COLS, [1, 0, 1, 0, 1, 0, 1]),  # 7 rows
    }
    recorded_instances = []

    def factory():
        clf = _RecordingClassifier()
        recorded_instances.append(clf)
        return clf

    retraining_trajectory(
        factory,
        year_data,
        FEATURE_COLS,
        train_years=[2018],
        test_years=[2019, 2020, 2021],
    )

    assert len(recorded_instances) == 3
    # Round 1 (scoring 2019): pool is only 2018 (4 rows) -- 2019 must not
    # have leaked in yet.
    assert recorded_instances[0].fit_rows == 4
    # Round 2 (scoring 2020): pool is 2018+2019 (4+5=9) -- 2020 must not
    # have leaked in yet.
    assert recorded_instances[1].fit_rows == 9
    # Round 3 (scoring 2021): pool is 2018+2019+2020 (4+5+6=15) -- 2021
    # must not have leaked in yet.
    assert recorded_instances[2].fit_rows == 15


def test_retraining_trajectory_processes_years_chronologically_regardless_of_input_order():
    """Passing test_years out of order must not change the training
    pools: 2020 must never be scored (or trained toward) before 2019,
    even if the caller lists 2020 first."""
    year_data = {
        2018: _make_year_df(FEATURE_COLS, [0, 1, 0]),       # 3 rows
        2019: _make_year_df(FEATURE_COLS, [1, 0, 1, 0]),    # 4 rows
        2020: _make_year_df(FEATURE_COLS, [0, 1, 0, 1, 0]),  # 5 rows
    }
    recorded_instances = []

    def factory():
        clf = _RecordingClassifier()
        recorded_instances.append(clf)
        return clf

    result = retraining_trajectory(
        factory,
        year_data,
        FEATURE_COLS,
        train_years=[2018],
        test_years=[2020, 2019],  # deliberately out of order
    )

    assert list(result["year"]) == [2019, 2020]
    assert recorded_instances[0].fit_rows == 3      # scoring 2019: pool is just 2018
    assert recorded_instances[1].fit_rows == 3 + 4  # scoring 2020: pool is 2018+2019


def test_retraining_trajectory_raises_on_year_missing_from_year_data():
    """A requested train or test year absent from year_data must raise,
    not silently skip, since that would hide a leakage-relevant mistake."""
    year_data = {2018: _make_year_df(FEATURE_COLS, [0, 1])}

    with pytest.raises(ValueError):
        retraining_trajectory(
            lambda: _RecordingClassifier(),
            year_data,
            FEATURE_COLS,
            train_years=[2018],
            test_years=[2099],
        )


# --- The updated model actually uses the newer data


def test_retraining_trajectory_each_round_uses_a_freshly_built_classifier():
    """The factory must be called once per test year, each round yielding
    a distinct instance, so a later round's model is actually retrained
    rather than reusing an earlier round's fitted object."""
    year_data = {
        2018: _make_year_df(FEATURE_COLS, [0, 1, 0, 1]),
        2019: _make_year_df(FEATURE_COLS, [1, 0, 1, 0]),
        2020: _make_year_df(FEATURE_COLS, [0, 1, 1, 0]),
    }
    recorded_instances = []

    def factory():
        clf = _RecordingClassifier()
        recorded_instances.append(clf)
        return clf

    retraining_trajectory(
        factory, year_data, FEATURE_COLS, train_years=[2018], test_years=[2019, 2020]
    )

    assert len(recorded_instances) == 2
    assert recorded_instances[0] is not recorded_instances[1]


def test_retraining_trajectory_labels_grow_to_include_previously_scored_years():
    """Each round's fit labels must be exactly the concatenation of the
    original training years' labels plus every test year already scored,
    in chronological order -- proof the "updated" model is actually
    trained on the newer data, not just on a same-size resampling of the
    original pool."""
    year_data = {
        2018: _make_year_df(FEATURE_COLS, [0, 0]),
        2019: _make_year_df(FEATURE_COLS, [1, 1, 1]),
        2020: _make_year_df(FEATURE_COLS, [0, 0, 0, 0]),
    }
    recorded_instances = []

    def factory():
        clf = _RecordingClassifier()
        recorded_instances.append(clf)
        return clf

    retraining_trajectory(
        factory, year_data, FEATURE_COLS, train_years=[2018], test_years=[2019, 2020]
    )

    # Round scoring 2019: pool is just 2018's labels.
    assert recorded_instances[0].fit_labels == [0, 0]
    # Round scoring 2020: pool must now additionally include 2019's labels,
    # proving 2019's newer data was folded in after being scored.
    assert recorded_instances[1].fit_labels == [0, 0, 1, 1, 1]


def test_retraining_trajectory_fits_a_distinct_scaler_each_round():
    """Each round must fit a brand-new StandardScaler on the current pool
    (never reuse a prior round's scaler), since the growing pool can
    shift feature means/scales too. Scaled output for an added feature
    value should differ from an all-zero pool once a nonzero year joins."""
    year_data = {
        2018: _make_year_df(FEATURE_COLS, [0, 1], feature_value=0.0),
        2019: _make_year_df(FEATURE_COLS, [1, 0], feature_value=10.0),
        2020: _make_year_df(FEATURE_COLS, [0, 1], feature_value=10.0),
    }

    captured_test_inputs = []

    class _CapturingClassifier(_RecordingClassifier):
        def predict(self, X):
            captured_test_inputs.append(np.asarray(X).copy())
            return super().predict(X)

    retraining_trajectory(
        _CapturingClassifier, year_data, FEATURE_COLS, train_years=[2018], test_years=[2019, 2020]
    )

    # Round 1 scores 2019 with a scaler fit only on 2018 (all zeros), so
    # 2019's constant, nonzero raw feature value must scale to something
    # other than 0 (a scaler fit on an all-zero pool has scale_ == 0,
    # which StandardScaler maps to an unscaled value of 10.0, not 0).
    assert not np.allclose(captured_test_inputs[0], 0.0)
    # Round 2 scores 2020 with a scaler refit on 2018+2019 (now including
    # a nonzero year); since 2020 has the same raw value as 2019, a
    # distinct (updated) scaler should transform it differently than the
    # first round's scaler did -- the two transformed outputs differ.
    assert not np.allclose(captured_test_inputs[0], captured_test_inputs[1])


# --- The baseline model is never updated


def test_static_model_trajectory_never_calls_fit_on_the_model_or_scaler():
    """static_model_trajectory must only `.predict()`/`.transform()`; any
    `.fit()` call on the model or scaler must raise immediately."""
    year_data = {
        2018: _make_year_df(FEATURE_COLS, [0, 1, 0, 1]),
        2019: _make_year_df(FEATURE_COLS, [1, 0, 1, 0]),
    }
    models = {"a": _FitRaisingModel([0, 1, 0, 1])}
    scaler = _FitRaisingScaler()

    # Should not raise -- if it does, static_model_trajectory tried to fit.
    result = static_model_trajectory(models, year_data, FEATURE_COLS, scaler, test_years=[2018, 2019])

    assert set(result["year"]) == {2018, 2019}


def test_static_model_trajectory_uses_the_same_fitted_parameters_across_every_year():
    """A real, already-fit StandardScaler's mean_/scale_ must be identical
    before and after scoring multiple years -- the baseline's fitted
    state never changes as it is scored on more and more drifted years."""
    from sklearn.preprocessing import StandardScaler

    train_df = _make_year_df(FEATURE_COLS, [0, 1, 0, 1], feature_value=0.0)
    train_df["f1"] = [1.0, 2.0, 3.0, 4.0]
    train_df["f2"] = [10.0, 20.0, 30.0, 40.0]
    scaler = StandardScaler()
    scaler.fit(train_df[FEATURE_COLS])
    mean_before = scaler.mean_.copy()
    scale_before = scaler.scale_.copy()

    year_data = {
        2018: _make_year_df(FEATURE_COLS, [0, 1, 0, 1]),
        2019: _make_year_df(FEATURE_COLS, [1, 0, 1, 0]),
        2020: _make_year_df(FEATURE_COLS, [0, 0, 1, 1]),
    }
    models = {"a": _FitRaisingModel([0, 1, 0, 1])}

    static_model_trajectory(models, year_data, FEATURE_COLS, scaler, test_years=[2018, 2019, 2020])

    np.testing.assert_array_equal(scaler.mean_, mean_before)
    np.testing.assert_array_equal(scaler.scale_, scale_before)


# --- compare_static_vs_retrained alignment


def test_compare_static_vs_retrained_aligns_every_year_and_classifier_without_dropping_or_duplicating():
    """The merged comparison must have exactly one row per (year,
    classifier) pair present in both inputs -- none dropped, none
    duplicated."""
    static_df = pd.DataFrame(
        {
            "year": [2019, 2020, 2019, 2020],
            "classifier": ["lr", "lr", "rf", "rf"],
            "accuracy": [0.9, 0.8, 0.85, 0.75],
            "precision": [0.9, 0.8, 0.85, 0.75],
            "recall": [0.9, 0.8, 0.85, 0.75],
            "f1": [0.9, 0.8, 0.85, 0.75],
        }
    )
    retrained_df = pd.DataFrame(
        {
            "year": [2019, 2020, 2019, 2020],
            "classifier": ["lr", "lr", "rf", "rf"],
            "accuracy": [0.91, 0.88, 0.86, 0.82],
            "precision": [0.91, 0.88, 0.86, 0.82],
            "recall": [0.91, 0.88, 0.86, 0.82],
            "f1": [0.91, 0.88, 0.86, 0.82],
        }
    )

    merged = compare_static_vs_retrained(static_df, retrained_df)

    assert len(merged) == 4
    seen = set(zip(merged["year"], merged["classifier"]))
    assert seen == {(2019, "lr"), (2020, "lr"), (2019, "rf"), (2020, "rf")}
    assert {"accuracy_static", "accuracy_retrained"} <= set(merged.columns)


def test_compare_static_vs_retrained_raises_when_year_classifier_pairs_differ():
    """A dropped or extra (year, classifier) pair in either input must
    raise rather than silently merging a mismatched comparison."""
    static_df = pd.DataFrame(
        {
            "year": [2019, 2020],
            "classifier": ["lr", "lr"],
            "accuracy": [0.9, 0.8],
            "precision": [0.9, 0.8],
            "recall": [0.9, 0.8],
            "f1": [0.9, 0.8],
        }
    )
    retrained_df = pd.DataFrame(
        {
            "year": [2019],
            "classifier": ["lr"],
            "accuracy": [0.91],
            "precision": [0.91],
            "recall": [0.91],
            "f1": [0.91],
        }
    )

    with pytest.raises(ValueError):
        compare_static_vs_retrained(static_df, retrained_df)


# --- run_sustainability_comparison covers every classifier


def test_run_sustainability_comparison_includes_both_classifiers():
    """The full comparison must include every classifier name present in
    classifier_factories (and matching models), not just one."""
    year_data = {
        2018: _make_year_df(FEATURE_COLS, [0, 1, 0, 1, 0, 1], feature_value=0.0),
        2019: _make_year_df(FEATURE_COLS, [1, 0, 1, 0, 1, 0], feature_value=1.0),
        2020: _make_year_df(FEATURE_COLS, [0, 1, 0, 1, 0, 1], feature_value=2.0),
    }
    from sklearn.preprocessing import StandardScaler

    train_df = year_data[2018]
    scaler = StandardScaler().fit(train_df[FEATURE_COLS])

    models = {
        "clf_a": _FitRaisingModel([0, 1, 0, 1, 0, 1]),
        "clf_b": _FitRaisingModel([1, 0, 1, 0, 1, 0]),
    }
    classifier_factories = {
        "clf_a": lambda: _RecordingClassifier(),
        "clf_b": lambda: _RecordingClassifier(),
    }

    result = run_sustainability_comparison(
        classifier_factories,
        models,
        year_data,
        FEATURE_COLS,
        scaler,
        train_years=[2018],
        test_years=[2019, 2020],
    )

    assert set(result["classifier"]) == {"clf_a", "clf_b"}
    assert set(result["year"]) == {2019, 2020}


def test_run_sustainability_comparison_raises_when_factories_and_models_disagree():
    """classifier_factories and models must name the same classifiers;
    a mismatch must raise rather than silently comparing the wrong pair."""
    year_data = {2018: _make_year_df(FEATURE_COLS, [0, 1]), 2019: _make_year_df(FEATURE_COLS, [1, 0])}
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler().fit(year_data[2018][FEATURE_COLS])

    with pytest.raises(ValueError):
        run_sustainability_comparison(
            classifier_factories={"clf_a": lambda: _RecordingClassifier()},
            models={"clf_b": _FitRaisingModel([0, 1])},
            year_data=year_data,
            feature_cols=FEATURE_COLS,
            scaler=scaler,
            train_years=[2018],
            test_years=[2019],
        )


# --- Integration: real pipeline


def test_sustainable_pipeline_on_real_data_never_leaks_future_years(real_data_dir):
    """End-to-end on the real dataset: retraining_trajectory's training
    pool size for each round must equal the row count of train_years plus
    every already-scored test year -- never the about-to-be-scored year
    or a later one -- and the static baseline must never be refit."""
    from data_loader import get_feature_columns, load_all_years
    from models import get_classifier_factories
    from preprocessing import split_years_in_half

    year_data = load_all_years(real_data_dir)
    years = sorted(year_data.keys())
    if len(years) < 3:
        pytest.skip("Need at least 3 years in input_data/ for a meaningful retraining trajectory")

    train_years, test_years = split_years_in_half(years)
    feature_cols = get_feature_columns(next(iter(year_data.values())))

    factories = get_classifier_factories()
    lr_factory = factories["logistic_regression"]  # fastest of the two for this integration check

    recorded_instances = []

    def recording_factory():
        clf = lr_factory()
        original_fit = clf.fit

        def fit_and_record(X, y):
            recorded_instances.append(len(y))
            return original_fit(X, y)

        clf.fit = fit_and_record
        return clf

    retraining_trajectory(recording_factory, year_data, feature_cols, train_years, test_years)

    expected_pool_size = sum(len(year_data[y]) for y in train_years)
    for i, scored_year in enumerate(sorted(test_years)):
        assert recorded_instances[i] == expected_pool_size
        expected_pool_size += len(year_data[scored_year])

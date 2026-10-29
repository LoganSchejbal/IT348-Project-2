"""Tests for Step 5 (Evaluate Classifier Performance).

These tests check what the assignment and PLAN.md say Step 5 should do:
each classifier is scored with accuracy, precision, recall, and F1-score,
with malware (label == 1) as the positive class, computed against
scikit-learn's own metric functions on a small hand-checked example, and
only ever against a held-out test set that is distinct from whatever the
classifier was fitted on. All tests use small synthetic data or fake
model stand-ins, so they run in seconds; none require the real dataset.
Two tests additionally exercise the real pipeline (data_loader ->
preprocessing -> models -> evaluation) when input_data/ is present, via
the `real_data_dir` fixture.
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from evaluation import evaluate_all, evaluate_classifier


class _FixedPredictModel:
    """A fake classifier stand-in that always returns a fixed prediction array.

    Used to hand-check `evaluate_classifier` against known predictions
    without depending on any real scikit-learn estimator's training
    behavior. Also records whether `.fit()` was ever called, so tests can
    assert that evaluation never trains on the data it is scoring.
    """

    def __init__(self, fixed_predictions: np.ndarray):
        """Store the predictions this stand-in will always return.

        Args:
            fixed_predictions: The array `.predict()` returns regardless
                of the input passed to it.
        """
        self.fixed_predictions = np.asarray(fixed_predictions)
        self.fit_called = False

    def predict(self, X):
        """Ignore `X` and return the stored fixed predictions."""
        return self.fixed_predictions

    def fit(self, X, y):
        """Record that fitting was attempted; should never be called by evaluation code."""
        self.fit_called = True
        return self


# --- evaluate_classifier matches scikit-learn on a small hand-checked example


def test_evaluate_classifier_matches_sklearn_hand_checked_example():
    """Metrics must match sklearn's own functions on a known small example.

    y_test and the fixed predictions are chosen so every one of TP/FP/FN/TN
    is nonzero, giving a non-trivial, hand-checkable case:
    y_test     = [1, 1, 1, 0, 0, 0, 0, 0]
    y_pred     = [1, 1, 0, 1, 0, 0, 0, 0]
    -> TP=2, FN=1, FP=1, TN=4
    accuracy  = 6/8   = 0.75
    precision = 2/3   ~ 0.6667
    recall    = 2/3   ~ 0.6667
    f1        = 2/3   ~ 0.6667
    """
    y_test = pd.Series([1, 1, 1, 0, 0, 0, 0, 0])
    y_pred = np.array([1, 1, 0, 1, 0, 0, 0, 0])
    model = _FixedPredictModel(y_pred)

    result = evaluate_classifier(model, X_test=np.zeros((len(y_test), 3)), y_test=y_test)

    expected_accuracy = accuracy_score(y_test, y_pred)
    expected_precision = precision_score(y_test, y_pred, pos_label=1, zero_division=0)
    expected_recall = recall_score(y_test, y_pred, pos_label=1, zero_division=0)
    expected_f1 = f1_score(y_test, y_pred, pos_label=1, zero_division=0)

    assert result["accuracy"] == pytest.approx(expected_accuracy)
    assert result["precision"] == pytest.approx(expected_precision)
    assert result["recall"] == pytest.approx(expected_recall)
    assert result["f1"] == pytest.approx(expected_f1)

    # Hand-computed values, independent of sklearn, as a second check.
    assert result["accuracy"] == pytest.approx(0.75)
    assert result["precision"] == pytest.approx(2 / 3)
    assert result["recall"] == pytest.approx(2 / 3)
    assert result["f1"] == pytest.approx(2 / 3)


def test_evaluate_classifier_matches_sklearn_for_always_benign_dummy():
    """A classifier that always predicts benign (0) must score as sklearn does.

    With malware as the positive class, a dummy that always predicts 0
    has zero true positives, so precision/recall/f1 should be 0.0
    (via zero_division=0) while accuracy equals the benign fraction.
    """
    y_test = pd.Series([0, 0, 0, 1, 1])
    y_pred = np.zeros(len(y_test), dtype=int)
    model = _FixedPredictModel(y_pred)

    result = evaluate_classifier(model, X_test=np.zeros((len(y_test), 2)), y_test=y_test)

    assert result["accuracy"] == pytest.approx(accuracy_score(y_test, y_pred))
    assert result["precision"] == pytest.approx(0.0)
    assert result["recall"] == pytest.approx(0.0)
    assert result["f1"] == pytest.approx(0.0)
    assert result["accuracy"] == pytest.approx(3 / 5)


def test_evaluate_classifier_matches_sklearn_for_perfect_predictions():
    """A classifier that predicts perfectly must score 1.0 on every metric."""
    y_test = pd.Series([0, 1, 1, 0, 1, 0])
    y_pred = y_test.to_numpy().copy()
    model = _FixedPredictModel(y_pred)

    result = evaluate_classifier(model, X_test=np.zeros((len(y_test), 4)), y_test=y_test)

    for metric in ("accuracy", "precision", "recall", "f1"):
        assert result[metric] == pytest.approx(1.0)


def test_evaluate_classifier_uses_malware_as_positive_class():
    """Precision/recall/F1 must treat label 1 (malware) as positive, not label 0.

    Chosen so that swapping which class is "positive" changes the result:
    with pos_label=1 precision is 1/2, but with pos_label=0 it would be
    1/1 = 1.0, so this distinguishes a correct implementation from one
    that silently used the wrong positive label.
    """
    y_test = pd.Series([1, 0, 0])
    y_pred = np.array([1, 1, 0])
    model = _FixedPredictModel(y_pred)

    result = evaluate_classifier(model, X_test=np.zeros((len(y_test), 2)), y_test=y_test)

    assert result["precision"] == pytest.approx(
        precision_score(y_test, y_pred, pos_label=1, zero_division=0)
    )
    assert result["precision"] == pytest.approx(0.5)
    assert result["precision"] != pytest.approx(
        precision_score(y_test, y_pred, pos_label=0, zero_division=0)
    )


# --- evaluate_classifier returns the required keys, all in [0, 1]


def test_evaluate_classifier_returns_required_metric_keys():
    """The result must have exactly accuracy, precision, recall, and f1."""
    y_test = pd.Series([0, 1, 0, 1])
    model = _FixedPredictModel(np.array([0, 1, 1, 1]))

    result = evaluate_classifier(model, X_test=np.zeros((4, 2)), y_test=y_test)

    assert set(result.keys()) == {"accuracy", "precision", "recall", "f1"}
    for metric_name, value in result.items():
        assert 0.0 <= value <= 1.0, f"{metric_name} out of [0, 1]: {value}"


# --- evaluate_classifier only scores the held-out data it is given; it never fits


def test_evaluate_classifier_never_calls_fit():
    """Evaluation must only call .predict(); it must never fit a model.

    If evaluation ever fit the model (e.g. on the data being scored),
    that model would stop being "trained on the training split and
    evaluated on the held-out split" per the assignment. `_FixedPredictModel`
    records whether `.fit()` was invoked so this is checked directly.
    """
    y_test = pd.Series([0, 1, 0, 1])
    model = _FixedPredictModel(np.array([0, 1, 0, 1]))

    evaluate_classifier(model, X_test=np.zeros((4, 2)), y_test=y_test)

    assert model.fit_called is False


def test_evaluate_classifier_scores_the_exact_data_passed_in():
    """Metrics must reflect the X_test/y_test actually passed, not some other set.

    Same fitted model, two different held-out sets: the metrics must
    differ accordingly, confirming the function evaluates whatever test
    data it is given each call rather than some cached or default split.
    """
    model = _FixedPredictModel(np.array([1, 1, 0, 0]))

    y_test_a = pd.Series([1, 1, 0, 0])  # perfect match
    y_test_b = pd.Series([0, 0, 1, 1])  # complete mismatch

    result_a = evaluate_classifier(model, X_test=np.zeros((4, 2)), y_test=y_test_a)
    result_b = evaluate_classifier(model, X_test=np.zeros((4, 2)), y_test=y_test_b)

    assert result_a["accuracy"] == pytest.approx(1.0)
    assert result_b["accuracy"] == pytest.approx(0.0)


def test_evaluate_classifier_distinguishes_held_out_set_from_training_set():
    """A classifier fitted on one distribution must be scored on the held-out
    set it is given, not on data resembling what it was trained on.

    A logistic regression is trained on a cleanly separable dataset (so it
    fits ~perfectly on that training data), then evaluated via
    `evaluate_classifier` on a held-out set drawn from a shifted, harder
    distribution. The reported accuracy must reflect performance on the
    held-out set (and therefore be noticeably below the near-perfect
    training-set accuracy), proving the held-out data -- not the training
    data -- is what gets scored.
    """
    from sklearn.linear_model import LogisticRegression

    rng = np.random.default_rng(0)
    n = 200

    # Training data: well-separated clusters, easy to fit perfectly.
    X_train = np.vstack(
        [rng.normal(-3, 0.5, size=(n // 2, 2)), rng.normal(3, 0.5, size=(n // 2, 2))]
    )
    y_train = pd.Series([0] * (n // 2) + [1] * (n // 2))

    model = LogisticRegression()
    model.fit(X_train, y_train)
    train_accuracy = (model.predict(X_train) == y_train.to_numpy()).mean()
    assert train_accuracy > 0.95  # sanity check: training data is easy

    # Held-out ("test") data: classes overlap heavily, so a model fit on
    # the easy training clusters cannot score as well here.
    X_test = np.vstack(
        [rng.normal(0, 3.0, size=(n // 2, 2)), rng.normal(0.5, 3.0, size=(n // 2, 2))]
    )
    y_test = pd.Series([0] * (n // 2) + [1] * (n // 2))

    result = evaluate_classifier(model, X_test, y_test)

    assert result["accuracy"] == pytest.approx(
        accuracy_score(y_test, model.predict(X_test))
    )
    assert result["accuracy"] < train_accuracy - 0.1


# --- evaluate_all returns one row per classifier with all four metric columns


def test_evaluate_all_returns_one_row_per_classifier():
    """evaluate_all must produce exactly one row per input classifier."""
    y_test = pd.Series([0, 1, 0, 1])
    models = {
        "always_benign": _FixedPredictModel(np.array([0, 0, 0, 0])),
        "always_malware": _FixedPredictModel(np.array([1, 1, 1, 1])),
        "perfect": _FixedPredictModel(np.array([0, 1, 0, 1])),
    }

    result = evaluate_all(models, X_test=np.zeros((4, 2)), y_test=y_test)

    assert len(result) == len(models)
    assert set(result["classifier"]) == set(models.keys())


def test_evaluate_all_includes_all_four_metric_columns():
    """evaluate_all's output must include classifier plus all four metrics."""
    y_test = pd.Series([0, 1, 1, 0])
    models = {"m": _FixedPredictModel(np.array([0, 1, 0, 0]))}

    result = evaluate_all(models, X_test=np.zeros((4, 3)), y_test=y_test)

    assert set(result.columns) == {"classifier", "accuracy", "precision", "recall", "f1"}


def test_evaluate_all_rows_match_individual_evaluate_classifier_calls():
    """Each row of evaluate_all's output must match a direct evaluate_classifier call."""
    y_test = pd.Series([1, 0, 1, 0, 1])
    models = {
        "a": _FixedPredictModel(np.array([1, 0, 0, 0, 1])),
        "b": _FixedPredictModel(np.array([0, 0, 0, 0, 0])),
    }
    X_test = np.zeros((5, 2))

    result = evaluate_all(models, X_test, y_test)

    for name, model in models.items():
        expected = evaluate_classifier(model, X_test, y_test)
        row = result[result["classifier"] == name].iloc[0]
        for metric in ("accuracy", "precision", "recall", "f1"):
            assert row[metric] == pytest.approx(expected[metric])


# --- Integration: real pipeline, evaluation only ever touches the test-year split


def test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years(real_data_dir):
    """End-to-end on the real dataset: models trained on train_years only must
    be scored by evaluate_all using exactly the test_years split, with no
    overlap between the two, and metrics must match sklearn computed
    directly on (model.predict(X_test), y_test).
    """
    from data_loader import get_feature_columns, load_all_years
    from models import get_classifiers, train_classifiers
    from preprocessing import prepare_train_test, split_years_in_half

    year_data = load_all_years(real_data_dir)
    years = sorted(year_data.keys())
    if len(years) < 2:
        pytest.skip("Need at least 2 years in input_data/ to split train/test")

    train_years, test_years = split_years_in_half(years)
    assert not set(train_years) & set(test_years)

    feature_cols = get_feature_columns(next(iter(year_data.values())))
    X_train, X_test, y_train, y_test, _scaler = prepare_train_test(
        year_data, feature_cols, train_years, test_years
    )

    classifiers = train_classifiers(get_classifiers(), X_train, y_train)
    result = evaluate_all(classifiers, X_test, y_test)

    assert len(result) == len(classifiers)
    for name, model in classifiers.items():
        row = result[result["classifier"] == name].iloc[0]
        expected_accuracy = accuracy_score(y_test, model.predict(X_test))
        assert row["accuracy"] == pytest.approx(expected_accuracy)

    # The held-out set passed to evaluation must be built strictly from
    # test_years' row counts, not the training years' (which would
    # indicate the wrong split reached evaluation).
    assert len(y_test) == sum(len(year_data[year]) for year in test_years)
    assert len(y_train) == sum(len(year_data[year]) for year in train_years)

"""Tests for Step 4 (Apply Machine Learning Classifiers).

These tests check what the assignment and PLAN.md say Step 4 should do:
at least two distinct scikit-learn classifiers are available via factories,
each classifier fits and predicts on data, predictions only ever use the
two class labels (0 = benign, 1 = malware), and fixing `random_state`
makes training and predictions reproducible across runs. All tests use
small synthetic data so they run in seconds; none require the real
dataset.
"""

import numpy as np
import pandas as pd
import pytest

from models import get_classifier_factories, get_classifiers, train_classifiers


RNG_SEED = 42
N_SAMPLES = 60
N_FEATURES = 10


def _make_synthetic_dataset(
    n_samples: int = N_SAMPLES, n_features: int = N_FEATURES, seed: int = RNG_SEED
) -> tuple[np.ndarray, pd.Series]:
    """Build a small, linearly-separable-ish binary classification dataset.

    Args:
        n_samples: Number of rows to generate.
        n_features: Number of feature columns to generate.
        seed: Seed for the random generator, for reproducible synthetic data.

    Returns:
        A tuple `(X, y)` where `X` is an `(n_samples, n_features)` array of
        scaled-looking features and `y` is a `pandas.Series` of 0/1 labels
        with both classes present.
    """
    rng = np.random.default_rng(seed)
    # Half the rows are drawn from a "benign" cluster, half from a
    # "malware" cluster shifted away from it, so classifiers have a
    # learnable signal instead of pure noise.
    half = n_samples // 2
    benign = rng.normal(loc=0.0, scale=1.0, size=(half, n_features))
    malware = rng.normal(loc=3.0, scale=1.0, size=(n_samples - half, n_features))
    X = np.vstack([benign, malware])
    y = pd.Series([0] * half + [1] * (n_samples - half))
    return X, y


@pytest.fixture
def synthetic_dataset():
    """A small synthetic (X, y) binary classification dataset."""
    return _make_synthetic_dataset()


# --- get_classifier_factories returns at least two distinct, callable factories


def test_get_classifier_factories_returns_at_least_two():
    """At least two classifiers must be implemented, per the assignment."""
    factories = get_classifier_factories()
    assert len(factories) >= 2


def test_get_classifier_factories_values_are_callable():
    """Every entry must be a zero-argument factory, not an instance."""
    factories = get_classifier_factories()
    for factory in factories.values():
        assert callable(factory)


def test_get_classifier_factories_produce_distinct_classifier_types():
    """The classifiers must be of genuinely different types, not duplicates."""
    factories = get_classifier_factories()
    instances = [factory() for factory in factories.values()]
    types_seen = {type(instance) for instance in instances}
    assert len(types_seen) >= 2


def test_get_classifier_factories_each_call_returns_unfitted_estimator():
    """Each factory call must return a fresh, unfitted estimator."""
    factories = get_classifier_factories()
    for factory in factories.values():
        instance = factory()
        assert not hasattr(instance, "classes_")


def test_get_classifier_factories_repeated_calls_give_equal_but_distinct_objects():
    """Two calls to the same factory must give equal-config but separate instances."""
    factories = get_classifier_factories()
    for factory in factories.values():
        first = factory()
        second = factory()
        assert first is not second
        assert first.get_params() == second.get_params()


def test_get_classifier_factories_use_requested_random_state():
    """Classifiers built from the factories must honor the given random_state."""
    factories = get_classifier_factories(random_state=7)
    for factory in factories.values():
        instance = factory()
        assert instance.get_params().get("random_state") == 7


# --- get_classifiers returns at least two distinct classifier instances


def test_get_classifiers_returns_at_least_two_distinct_types():
    """get_classifiers must build at least two distinct, unfitted classifier types."""
    classifiers = get_classifiers()
    assert len(classifiers) >= 2
    types_seen = {type(c) for c in classifiers.values()}
    assert len(types_seen) >= 2


def test_get_classifiers_use_random_state_42_by_default():
    """Per PLAN.md, classifiers should default to random_state=42 for reproducibility."""
    classifiers = get_classifiers()
    for classifier in classifiers.values():
        assert classifier.get_params().get("random_state") == 42


# --- Each classifier fits and predicts on a small synthetic dataset


def test_train_classifiers_returns_fitted_estimators(synthetic_dataset):
    """After training, every classifier must expose classes_ (i.e., be fitted)."""
    X, y = synthetic_dataset
    classifiers = get_classifiers()
    trained = train_classifiers(classifiers, X, y)
    for model in trained.values():
        assert hasattr(model, "classes_")


def test_each_classifier_fits_and_predicts_on_synthetic_data(synthetic_dataset):
    """Each trained classifier must predict one label per input row."""
    X, y = synthetic_dataset
    classifiers = get_classifiers()
    trained = train_classifiers(classifiers, X, y)
    for name, model in trained.items():
        predictions = model.predict(X)
        assert len(predictions) == len(X), f"{name} did not predict one label per row"


def test_each_classifier_learns_the_synthetic_signal(synthetic_dataset):
    """Each classifier must do meaningfully better than chance on learnable synthetic data."""
    X, y = synthetic_dataset
    classifiers = get_classifiers()
    trained = train_classifiers(classifiers, X, y)
    for name, model in trained.items():
        accuracy = (model.predict(X) == y.to_numpy()).mean()
        assert accuracy > 0.8, f"{name} accuracy too low on separable synthetic data: {accuracy}"


# --- Predictions use only the two class labels


def test_predictions_use_only_the_two_class_labels(synthetic_dataset):
    """Predicted labels must be a subset of {0, 1}, matching benign=0/malware=1."""
    X, y = synthetic_dataset
    classifiers = get_classifiers()
    trained = train_classifiers(classifiers, X, y)
    for name, model in trained.items():
        predictions = set(np.unique(model.predict(X)))
        assert predictions.issubset({0, 1}), f"{name} predicted an unexpected label: {predictions}"


def test_classifier_classes_attribute_matches_two_labels(synthetic_dataset):
    """The fitted classes_ attribute must be exactly {0, 1} after training on both classes."""
    X, y = synthetic_dataset
    classifiers = get_classifiers()
    trained = train_classifiers(classifiers, X, y)
    for name, model in trained.items():
        assert set(model.classes_.tolist()) == {0, 1}, f"{name} classes_ was {model.classes_}"


# --- Results are identical across two runs with the same random_state


def test_same_random_state_gives_identical_predictions_across_runs(synthetic_dataset):
    """Two independently-trained runs with the same random_state must predict identically."""
    X, y = synthetic_dataset

    classifiers_run1 = train_classifiers(get_classifiers(random_state=42), X, y)
    classifiers_run2 = train_classifiers(get_classifiers(random_state=42), X, y)

    for name in classifiers_run1:
        predictions_1 = classifiers_run1[name].predict(X)
        predictions_2 = classifiers_run2[name].predict(X)
        assert np.array_equal(predictions_1, predictions_2), (
            f"{name} predictions differed across runs with the same random_state"
        )


def test_same_random_state_gives_identical_fitted_parameters(synthetic_dataset):
    """Two runs of logistic regression with the same random_state must fit identical coefficients."""
    X, y = synthetic_dataset
    factories = get_classifier_factories(random_state=42)
    assert "logistic_regression" in factories, (
        "Expected a 'logistic_regression' factory per PLAN.md's Step 4 description"
    )

    model_1 = factories["logistic_regression"]()
    model_1.fit(X, y)
    model_2 = factories["logistic_regression"]()
    model_2.fit(X, y)

    assert np.allclose(model_1.coef_, model_2.coef_)


def test_different_random_state_is_accepted_without_error(synthetic_dataset):
    """Factories must accept an arbitrary random_state without raising."""
    X, y = synthetic_dataset
    classifiers = get_classifiers(random_state=123)
    trained = train_classifiers(classifiers, X, y)
    for model in trained.values():
        assert hasattr(model, "classes_")

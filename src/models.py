"""Step 4: construct and train the project's scikit-learn classifiers.

Defines the two classifiers used throughout the rest of the pipeline --
Logistic Regression and Random Forest -- as a single source-of-truth
factory dict (`get_classifier_factories`), so Steps 4-6 and the
retraining loop in Step 7 all build fresh, identically-configured
classifiers from one place instead of duplicating hyperparameters.
"""

from typing import Callable

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression


def get_classifier_factories(
    random_state: int = 42,
) -> dict[str, Callable[[], object]]:
    """Return zero-argument factories for each classifier used in this project.

    Each factory builds a brand-new, unfitted estimator with fixed
    hyperparameters when called. Keeping factories (rather than instances)
    here lets Step 7's retraining loop build a fresh, never-fitted
    classifier for every retrain round without reaching into this module
    again or risking reuse of an already-fitted estimator.

    Args:
        random_state: Seed passed to every classifier that accepts one, so
            runs are reproducible.

    Returns:
        A dict mapping classifier name to a zero-argument callable that
        constructs a fresh, unfitted instance of that classifier:
        - "logistic_regression": a linear baseline (`LogisticRegression`
          with L2 regularization, `max_iter` raised so it reliably
          converges on 1,848 scaled features).
        - "random_forest": a non-linear ensemble (`RandomForestClassifier`)
          that can capture feature interactions the linear model cannot.
    """
    return {
        "logistic_regression": lambda: LogisticRegression(
            random_state=random_state,
            max_iter=1000,
        ),
        "random_forest": lambda: RandomForestClassifier(
            random_state=random_state,
            n_estimators=100,
        ),
    }


def get_classifiers(random_state: int = 42) -> dict[str, object]:
    """Build one fresh, unfitted instance of every project classifier.

    Calls every factory from `get_classifier_factories` exactly once. Use
    this when a caller (Steps 4-6) only needs a single trained instance of
    each classifier and will not need to reset or rebuild it later; Step
    7's retraining loop uses `get_classifier_factories` directly instead,
    since it needs a fresh instance per retrain round.

    Args:
        random_state: Seed forwarded to `get_classifier_factories`.

    Returns:
        A dict mapping classifier name to an unfitted estimator instance.
    """
    factories = get_classifier_factories(random_state=random_state)
    return {name: factory() for name, factory in factories.items()}


def train_classifiers(
    classifiers: dict[str, object],
    X_train: np.ndarray,
    y_train: pd.Series,
) -> dict[str, object]:
    """Fit every classifier in a dict on the same training data.

    Args:
        classifiers: Mapping of classifier name to an unfitted (or
            previously fitted) estimator, e.g. from `get_classifiers`.
        X_train: Scaled training features, as produced by
            `preprocessing.prepare_train_test`.
        y_train: Training labels aligned with `X_train`.

    Returns:
        The same dict, with every estimator fitted in place on
        `(X_train, y_train)`.
    """
    for classifier in classifiers.values():
        classifier.fit(X_train, y_train)
    return classifiers

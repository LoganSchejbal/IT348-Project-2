"""Step 5: evaluate trained classifiers on the pooled test set.

Scores each classifier from Step 4 (`src/models.py`) on the already-scaled
test features from Step 3 (`src/preprocessing.py`), computing accuracy,
precision, recall, and F1-score with malware (`label == 1`) as the positive
class, per AGENTS.md. Only `.predict()` is ever called on the test data here;
nothing in this module fits anything, so Step 5 cannot introduce leakage on
its own.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# Malware is the positive class for precision/recall/F1 per AGENTS.md.
_POSITIVE_LABEL = 1


def evaluate_classifier(model: object, X_test: np.ndarray, y_test: pd.Series) -> dict[str, float]:
    """Score one fitted classifier on a test set.

    Args:
        model: A fitted scikit-learn classifier (e.g. from
            `models.train_classifiers`). Only `.predict()` is called.
        X_test: Scaled test features, as produced by
            `preprocessing.prepare_train_test` or `preprocessing.scale_features`.
        y_test: True labels aligned with `X_test` (1 = malware, 0 = benign).

    Returns:
        A dict with keys "accuracy", "precision", "recall", "f1", each a
        float in [0, 1]. Precision/recall/F1 treat malware (label 1) as the
        positive class and are 0.0 (rather than raising) if the model never
        predicts the positive class, via `zero_division=0`.
    """
    y_pred = model.predict(X_test)
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(
            y_test, y_pred, pos_label=_POSITIVE_LABEL, average="binary", zero_division=0
        ),
        "recall": recall_score(
            y_test, y_pred, pos_label=_POSITIVE_LABEL, average="binary", zero_division=0
        ),
        "f1": f1_score(
            y_test, y_pred, pos_label=_POSITIVE_LABEL, average="binary", zero_division=0
        ),
    }


def evaluate_all(
    models: dict[str, object], X_test: np.ndarray, y_test: pd.Series
) -> pd.DataFrame:
    """Score every classifier in a dict on the same test set.

    Args:
        models: Mapping of classifier name to a fitted estimator, e.g. from
            `models.train_classifiers`.
        X_test: Scaled test features shared by every model.
        y_test: True labels aligned with `X_test`.

    Returns:
        A dataframe with one row per classifier, a "classifier" column
        naming it, and "accuracy", "precision", "recall", "f1" columns from
        `evaluate_classifier`.
    """
    columns = ["classifier", "accuracy", "precision", "recall", "f1"]
    rows = []
    for name, model in models.items():
        metrics = evaluate_classifier(model, X_test, y_test)
        rows.append({"classifier": name, **metrics})
    return pd.DataFrame(rows, columns=columns)

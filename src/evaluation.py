"""Step 5-6: evaluate trained classifiers on the pooled test set and by year.

Scores each classifier from Step 4 (`src/models.py`) on the already-scaled
test features from Step 3 (`src/preprocessing.py`), computing accuracy,
precision, recall, and F1-score with malware (`label == 1`) as the positive
class, per AGENTS.md. Step 6 (`evaluate_by_year`) extends this to score each
test year individually, using the same already-fit `StandardScaler` from
Step 3 so the drift effect on each later year can be seen as the gap from
the training years grows. Only `.predict()`/`.transform()` are ever called
on test data here; nothing in this module fits anything, so Steps 5-6 cannot
introduce leakage on their own.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.preprocessing import StandardScaler

from src.preprocessing import scale_features

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


def evaluate_by_year(
    models: dict[str, object],
    year_data: dict[int, pd.DataFrame],
    feature_cols: list[str],
    scaler: StandardScaler,
    years: list[int],
) -> pd.DataFrame:
    """Score every classifier on each requested year individually.

    For each year in `years`, scales that year's features with the
    already-fit `scaler` (never re-fit here) and scores every model in
    `models` on it, so performance can be compared year-by-year instead of
    only on the pooled test set from Step 5. Intended for the test years
    (e.g. the later half from `preprocessing.split_years_in_half`), to show
    how performance changes as the gap from the training years grows.

    Args:
        models: Mapping of classifier name to a fitted estimator, e.g. from
            `models.train_classifiers`.
        year_data: Mapping of year to that year's combined dataframe, as
            returned by `data_loader.load_all_years`.
        feature_cols: Feature column names, as returned by
            `data_loader.get_feature_columns`.
        scaler: A `StandardScaler` already fit on the training years (see
            `preprocessing.fit_scaler`). Only `.transform()` is called on
            it here; it is never re-fit, so evaluating by year introduces
            no leakage from any of `years` back into the scaler.
        years: The years to evaluate, e.g. the test years.

    Returns:
        A dataframe with one row per `(year, classifier)` combination, with
        columns "year", "classifier", "accuracy", "precision", "recall",
        "f1". Each metric is a float in [0, 1].
    """
    columns = ["year", "classifier", "accuracy", "precision", "recall", "f1"]
    rows = []
    for year in years:
        year_df = year_data[year]
        X_year = scale_features(year_df, feature_cols, scaler)
        y_year = year_df["label"]
        for name, model in models.items():
            metrics = evaluate_classifier(model, X_year, y_year)
            rows.append({"year": year, "classifier": name, **metrics})
    return pd.DataFrame(rows, columns=columns)

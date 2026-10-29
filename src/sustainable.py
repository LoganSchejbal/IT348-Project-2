"""Step 7: compare a static model against periodic retraining under drift.

Builds on Steps 1-6 (`data_loader`, `preprocessing`, `models`, `evaluation`)
to answer the question Step 7 asks: does periodically retraining on newly
labeled years help compared with a model trained once and never updated?

Two trajectories are computed across the test years, in chronological
order, for each classifier from `models.get_classifier_factories`:

- **Static**: the already-fitted Step 4/6 model and Step 3 scaler, scored
  on each test year via `evaluation.evaluate_by_year` (`static_model_trajectory`).
- **Periodic retraining**: a fresh classifier (never the already-fitted
  Step 4 instance) and a fresh `StandardScaler`, refit from scratch on the
  growing training pool after each test year is scored, then used to score
  the next test year (`retraining_trajectory`).

A test year is only ever added to the retraining pool *after* it has been
scored once as unseen data, so neither the retrained classifier nor its
scaler ever sees a year before it is scored on that year -- the same
leakage guarantee Steps 3 and 6 rely on (see PLAN.md's leakage-prevention
section).
"""

from typing import Callable

import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.evaluation import evaluate_by_year, evaluate_classifier
from src.preprocessing import fit_scaler, scale_features

_TRAJECTORY_COLUMNS = ["year", "accuracy", "precision", "recall", "f1"]


def static_model_trajectory(
    models: dict[str, object],
    year_data: dict[int, pd.DataFrame],
    feature_cols: list[str],
    scaler: StandardScaler,
    test_years: list[int],
) -> pd.DataFrame:
    """Score the never-updated Step 4/6 models on each test year.

    Thin wrapper around `evaluation.evaluate_by_year`: the models and the
    scaler are exactly the ones already fit once on the training years and
    are never refit here, so this is the "static" baseline Step 7 compares
    periodic retraining against.

    Args:
        models: Mapping of classifier name to a fitted estimator trained
            once on the original training years (e.g. from
            `models.train_classifiers`).
        year_data: Mapping of year to that year's combined dataframe, as
            returned by `data_loader.load_all_years`.
        feature_cols: Feature column names, as returned by
            `data_loader.get_feature_columns`.
        scaler: The `StandardScaler` the models were trained with (fit once
            on the training years). Only `.transform()` is called on it.
        test_years: The years to score, e.g. the later half from
            `preprocessing.split_years_in_half`.

    Returns:
        A dataframe with one row per `(year, classifier)`, columns "year",
        "classifier", "accuracy", "precision", "recall", "f1" -- identical
        in shape to `evaluation.evaluate_by_year`'s output.
    """
    return evaluate_by_year(models, year_data, feature_cols, scaler, test_years)


def retraining_trajectory(
    classifier_factory: Callable[[], object],
    year_data: dict[int, pd.DataFrame],
    feature_cols: list[str],
    train_years: list[int],
    test_years: list[int],
) -> pd.DataFrame:
    """Score a single classifier under periodic retraining across test years.

    Processes `test_years` in chronological order. For each test year: a
    fresh `StandardScaler` is fit from scratch on the current training
    pool, a fresh classifier is built from `classifier_factory` and fit on
    that pool, and the pair is scored on the current test year (which is
    not yet in the pool). Only after scoring is that year's data added to
    the pool for the next round, so no test year is ever scored by a model
    or scaler that has already seen it.

    Args:
        classifier_factory: A zero-argument callable that returns a fresh,
            unfitted estimator, e.g. one value from
            `models.get_classifier_factories()`. Called once per test year
            so every round trains a brand-new instance, never reusing a
            previously fitted classifier.
        year_data: Mapping of year to that year's combined dataframe.
        feature_cols: Feature column names, as returned by
            `data_loader.get_feature_columns`.
        train_years: The initial training years (before any test year has
            been folded in).
        test_years: The years to score and then retrain on, in the order
            they become available. Sorted ascending here so retraining is
            always chronological regardless of input order.

    Returns:
        A dataframe with one row per year in `test_years`, columns "year",
        "accuracy", "precision", "recall", "f1" (no "classifier" column --
        callers comparing multiple classifiers, e.g.
        `run_sustainability_comparison`, add that themselves).

    Raises:
        ValueError: If `train_years` or `test_years` is empty, or if any
            year in either is missing from `year_data`.
    """
    if not train_years or not test_years:
        raise ValueError("train_years and test_years must both be non-empty")
    ordered_test_years = sorted(set(test_years))
    missing = [
        year for year in (*train_years, *ordered_test_years) if year not in year_data
    ]
    if missing:
        raise ValueError(f"year(s) not found in year_data: {missing}")

    current_years = sorted(set(train_years))
    rows = []
    for year in ordered_test_years:
        # Refit scaler and classifier from scratch on the current pool --
        # neither is reused across rounds, since the growing pool changes
        # feature means/scales as well as the decision boundary.
        train_df = pd.concat(
            [year_data[y] for y in current_years], ignore_index=True
        )
        round_scaler = fit_scaler(train_df, feature_cols)
        X_train = scale_features(train_df, feature_cols, round_scaler)
        y_train = train_df["label"]

        round_classifier = classifier_factory()
        round_classifier.fit(X_train, y_train)

        test_df = year_data[year]
        X_test = scale_features(test_df, feature_cols, round_scaler)
        y_test = test_df["label"]
        metrics = evaluate_classifier(round_classifier, X_test, y_test)
        rows.append({"year": year, **metrics})

        # Only now does this year join the pool, so it was scored as
        # unseen data before ever contributing to a fit.
        current_years.append(year)

    return pd.DataFrame(rows, columns=_TRAJECTORY_COLUMNS)


def compare_static_vs_retrained(
    static_df: pd.DataFrame, retrained_df: pd.DataFrame
) -> pd.DataFrame:
    """Align the static and retraining trajectories for side-by-side comparison.

    Args:
        static_df: Output of `static_model_trajectory` (or
            `evaluation.evaluate_by_year`), with columns "year",
            "classifier", and the four metrics.
        retrained_df: Output of `retraining_trajectory` calls concatenated
            across classifiers, with a "classifier" column added by the
            caller (see `run_sustainability_comparison`), and the same
            "year" and metric columns.

    Returns:
        A dataframe with one row per `(year, classifier)`, with the static
        metrics suffixed "_static" and the retrained metrics suffixed
        "_retrained".

    Raises:
        ValueError: If `static_df` and `retrained_df` do not cover exactly
            the same set of `(year, classifier)` pairs, which would mean a
            year or classifier was dropped or duplicated when merging.
    """
    static_keys = set(zip(static_df["year"], static_df["classifier"]))
    retrained_keys = set(zip(retrained_df["year"], retrained_df["classifier"]))
    if static_keys != retrained_keys:
        raise ValueError(
            "static_df and retrained_df must cover the same (year, classifier) "
            f"pairs; static-only={sorted(static_keys - retrained_keys)}, "
            f"retrained-only={sorted(retrained_keys - static_keys)}"
        )

    merged = pd.merge(
        static_df,
        retrained_df,
        on=["year", "classifier"],
        suffixes=("_static", "_retrained"),
        validate="one_to_one",
    )
    if len(merged) != len(static_df):
        raise ValueError(
            "merge produced a different row count than the inputs -- "
            "(year, classifier) pairs were not unique in one of them"
        )
    return merged.sort_values(["classifier", "year"]).reset_index(drop=True)


def run_sustainability_comparison(
    classifier_factories: dict[str, Callable[[], object]],
    models: dict[str, object],
    year_data: dict[int, pd.DataFrame],
    feature_cols: list[str],
    scaler: StandardScaler,
    train_years: list[int],
    test_years: list[int],
) -> pd.DataFrame:
    """Run the full static-vs-retrained comparison for every classifier.

    Args:
        classifier_factories: Mapping of classifier name to a zero-argument
            factory, as returned by `models.get_classifier_factories`. Used
            to build a fresh classifier each retraining round, for every
            classifier in the project (not just one).
        models: Mapping of classifier name to the fitted, never-updated
            instance of that classifier (e.g. from
            `models.train_classifiers`), matching the keys of
            `classifier_factories`.
        year_data: Mapping of year to that year's combined dataframe.
        feature_cols: Feature column names.
        scaler: The `StandardScaler` the `models` were trained with.
        train_years: The initial training years.
        test_years: The years to score, in chronological order.

    Returns:
        The output of `compare_static_vs_retrained`: one row per
        `(year, classifier)` with both trajectories' metrics side by side,
        covering every classifier in `classifier_factories`.

    Raises:
        ValueError: If `classifier_factories` and `models` do not share the
            same set of classifier names.
    """
    if set(classifier_factories) != set(models):
        raise ValueError(
            "classifier_factories and models must have the same classifier "
            f"names; factories-only={sorted(set(classifier_factories) - set(models))}, "
            f"models-only={sorted(set(models) - set(classifier_factories))}"
        )

    static_df = static_model_trajectory(models, year_data, feature_cols, scaler, test_years)

    retrained_frames = []
    for name, factory in classifier_factories.items():
        trajectory = retraining_trajectory(
            factory, year_data, feature_cols, train_years, test_years
        )
        retrained_frames.append(trajectory.assign(classifier=name))
    retrained_df = pd.concat(retrained_frames, ignore_index=True)

    return compare_static_vs_retrained(static_df, retrained_df)

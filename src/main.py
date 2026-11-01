"""Orchestration for the Post Step 7 console driver.

Owns pipeline orchestration only: calls the Step 1-7 functions already
implemented in `src/data_loader.py`, `src/drift_analysis.py`,
`src/preprocessing.py`, `src/models.py`, `src/evaluation.py`, and
`src/sustainable.py`, and formats their output for the console. This
module never parses `sys.argv` itself (see `src/cli.py`), so adding a
console flag never touches this file, and adding a pipeline step never
touches argument parsing (see PLAN.md's "Post Step 7: Project
adjustments" section).
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.cli import parse_args
from src.data_loader import discover_dataset_files, get_feature_columns, load_all_years
from src.drift_analysis import compute_drift_across_years, top_drifting_features
from src.evaluation import evaluate_all, evaluate_by_year
from src.models import get_classifier_factories, get_classifiers, train_classifiers
from src.preprocessing import prepare_train_test, split_years_in_half
from src.sustainable import run_sustainability_comparison


@dataclass
class PipelineContext:
    """Holds pipeline state as it is computed, step by step.

    Fields start unset (`None`) and are filled in by the `ensure_*`
    functions below, each of which checks whether its target field is
    already set before recomputing it. This lets a console user request a
    single step (e.g. `--step sustainable`) and still get correct results,
    because the prerequisite steps it depends on run automatically and
    only once.

    Attributes:
        data_dir: Directory containing the dataset CSV files.
        year_data: Mapping of year to that year's combined dataframe, from
            `data_loader.load_all_years`.
        feature_cols: Feature column names, from `data_loader.get_feature_columns`.
        train_years: Years used for training, from `preprocessing.split_years_in_half`.
        test_years: Years used for testing, from `preprocessing.split_years_in_half`.
        X_train: Scaled training features, from `preprocessing.prepare_train_test`.
        X_test: Scaled testing features, from `preprocessing.prepare_train_test`.
        y_train: Training labels, from `preprocessing.prepare_train_test`.
        y_test: Testing labels, from `preprocessing.prepare_train_test`.
        scaler: The `StandardScaler` fit on `train_years`, from
            `preprocessing.prepare_train_test`.
        classifiers: Mapping of classifier name to a fitted estimator,
            from `models.train_classifiers`.
        classifier_factories: Mapping of classifier name to a zero-argument
            factory, from `models.get_classifier_factories`.
    """

    data_dir: str = "input_data"
    year_data: dict[int, pd.DataFrame] | None = None
    feature_cols: list[str] | None = None
    train_years: list[int] | None = None
    test_years: list[int] | None = None
    X_train: np.ndarray | None = None
    X_test: np.ndarray | None = None
    y_train: pd.Series | None = None
    y_test: pd.Series | None = None
    scaler: StandardScaler | None = None
    classifiers: dict[str, object] | None = None
    classifier_factories: dict[str, Callable[[], object]] | None = field(default=None)


def ensure_data_loaded(context: PipelineContext) -> None:
    """Load the dataset and compute the train/test year split, once.

    No-op if `context.year_data` is already set. Before calling
    `load_all_years`, checks that `context.data_dir` exists and contains
    at least one `sampled_*_api.csv` file -- this check is needed here
    (not left to `data_loader.py`) because neither
    `discover_dataset_files` (a `glob`, which simply returns an empty list
    for a missing or empty directory) nor `load_all_years` raises on a
    missing/empty `data_dir` today. Without this check, an empty
    `year_data` dict would flow silently into every later step and fail
    far from the real cause.

    Args:
        context: The pipeline state to fill in.

    Raises:
        FileNotFoundError: If `context.data_dir` does not exist or
            contains no `sampled_*_api.csv` files.
    """
    if context.year_data is not None:
        return
    data_dir = Path(context.data_dir)
    if not data_dir.is_dir() or not discover_dataset_files(data_dir):
        raise FileNotFoundError(
            f"No 'sampled_*_api.csv' files found in {data_dir}; check --data-dir"
        )
    context.year_data = load_all_years(data_dir)
    context.feature_cols = get_feature_columns(next(iter(context.year_data.values())))
    context.train_years, context.test_years = split_years_in_half(
        list(context.year_data.keys())
    )


def ensure_preprocessed(context: PipelineContext) -> None:
    """Scale the train/test features, once.

    No-op if `context.X_train` is already set. Calls `ensure_data_loaded`
    first so this step's prerequisites are computed automatically.

    Args:
        context: The pipeline state to fill in.
    """
    if context.X_train is not None:
        return
    ensure_data_loaded(context)
    (
        context.X_train,
        context.X_test,
        context.y_train,
        context.y_test,
        context.scaler,
    ) = prepare_train_test(
        context.year_data, context.feature_cols, context.train_years, context.test_years
    )


def ensure_trained(context: PipelineContext) -> None:
    """Build and fit the project's classifiers, once.

    No-op if `context.classifiers` is already set. Calls
    `ensure_preprocessed` first so this step's prerequisites are computed
    automatically.

    Args:
        context: The pipeline state to fill in.
    """
    if context.classifiers is not None:
        return
    ensure_preprocessed(context)
    context.classifier_factories = get_classifier_factories()
    context.classifiers = train_classifiers(
        get_classifiers(), context.X_train, context.y_train
    )


def summarize_loaded_years(
    year_data: dict[int, pd.DataFrame], feature_cols: list[str]
) -> pd.DataFrame:
    """Summarize the loaded dataset, one row per year.

    Args:
        year_data: Mapping of year to that year's combined dataframe, from
            `data_loader.load_all_years`.
        feature_cols: Feature column names, from `data_loader.get_feature_columns`.

    Returns:
        A dataframe with columns "year", "rows", "n_features", "n_malware",
        "n_benign", one row per year present in `year_data`, sorted by year.
    """
    rows = []
    for year in sorted(year_data):
        df = year_data[year]
        rows.append(
            {
                "year": year,
                "rows": len(df),
                "n_features": len(feature_cols),
                "n_malware": int((df["label"] == 1).sum()),
                "n_benign": int((df["label"] == 0).sum()),
            }
        )
    return pd.DataFrame(
        rows, columns=["year", "rows", "n_features", "n_malware", "n_benign"]
    )


def summarize_preprocessing(
    train_years: list[int],
    test_years: list[int],
    X_train: np.ndarray,
    X_test: np.ndarray,
) -> pd.DataFrame:
    """Summarize the train/test split, one row for train and one for test.

    Args:
        train_years: Years used for training.
        test_years: Years used for testing.
        X_train: Scaled training features.
        X_test: Scaled testing features.

    Returns:
        A dataframe with columns "split", "years", "shape": one row for
        `"train"` and one for `"test"`, with their years joined as a
        string and their array's shape.
    """
    return pd.DataFrame(
        [
            {
                "split": "train",
                "years": ", ".join(str(year) for year in train_years),
                "shape": str(X_train.shape),
            },
            {
                "split": "test",
                "years": ", ".join(str(year) for year in test_years),
                "shape": str(X_test.shape),
            },
        ],
        columns=["split", "years", "shape"],
    )


def summarize_classifiers(classifiers: dict[str, object]) -> pd.DataFrame:
    """Summarize each classifier's name and hyperparameters.

    Args:
        classifiers: Mapping of classifier name to a fitted estimator.

    Returns:
        A dataframe with columns "classifier", "params": one row per
        classifier, with `params` read from each estimator's own
        `get_params()` (every scikit-learn estimator already exposes
        this) rather than duplicated from `models.py`.
    """
    rows = [
        {"classifier": name, "params": str(model.get_params())}
        for name, model in classifiers.items()
    ]
    return pd.DataFrame(rows, columns=["classifier", "params"])

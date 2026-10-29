"""Step 3: preprocess the per-year data for model training.

Combines the per-year dataframes from Step 1 (`src/data_loader.py`) into a
single training dataframe and a single test dataframe, split by year, and
scales the features with a `StandardScaler` fit only on the training
dataframe. Test-year data is only ever transformed, never used to fit the
scaler, so no information from the test years leaks into the fitted
scaler (see PLAN.md's leakage-prevention section).

`split_years_in_half`, also defined here, decides the train/test year
boundary itself (earlier half trains, later half tests); it is the most
leakage-sensitive function in this module since every other function's
notion of "training years" traces back to its output.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


def split_years_in_half(years: list[int]) -> tuple[list[int], list[int]]:
    """Split a list of years into an earlier training half and a later testing half.

    The years are sorted first so the split is always chronological
    regardless of the input order. When the count is odd, the earlier
    half receives the extra year.

    Args:
        years: The years to split, e.g. the keys of `load_all_years`'s
            return value.

    Returns:
        A tuple `(train_years, test_years)`, each a sorted list of years,
        with no overlap and every input year assigned to exactly one.

    Raises:
        ValueError: If `years` has fewer than 2 distinct years, since
            there would be nothing left to test on.
    """
    distinct_years = sorted(set(years))
    if len(distinct_years) < 2:
        raise ValueError(
            f"need at least 2 distinct years to split, got {len(distinct_years)}"
        )
    midpoint = (len(distinct_years) + 1) // 2
    return distinct_years[:midpoint], distinct_years[midpoint:]


def split_by_year(
    year_data: dict[int, pd.DataFrame],
    train_years: list[int],
    test_years: list[int],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Concatenate per-year dataframes into a training set and a testing set.

    Args:
        year_data: Mapping of year to that year's combined dataframe, as
            returned by `load_all_years`.
        train_years: Years whose data should form the training dataframe.
        test_years: Years whose data should form the testing dataframe.

    Returns:
        A tuple `(train_df, test_df)` built by concatenating the requested
        years' dataframes, in the order given. Row order within each year
        is preserved; years are never shuffled across the train/test
        boundary.

    Raises:
        ValueError: If `train_years` or `test_years` is empty, if any year
            in either is not a key of `year_data`, or if the two lists
            share a year (which would leak that year's rows into both the
            training and testing dataframes).
    """
    if not train_years or not test_years:
        raise ValueError("train_years and test_years must both be non-empty")
    missing = [year for year in (*train_years, *test_years) if year not in year_data]
    if missing:
        raise ValueError(f"year(s) not found in year_data: {missing}")
    overlap = set(train_years) & set(test_years)
    if overlap:
        raise ValueError(f"year(s) in both train_years and test_years: {sorted(overlap)}")
    train_df = pd.concat([year_data[year] for year in train_years], ignore_index=True)
    test_df = pd.concat([year_data[year] for year in test_years], ignore_index=True)
    return train_df, test_df


def _validate_feature_cols(df: pd.DataFrame, feature_cols: list[str]) -> None:
    """Check that `feature_cols` is non-empty and present in `df`.

    Shared by `fit_scaler` and `scale_features` so a typo'd or empty
    `feature_cols` (e.g. from a future change to `get_feature_columns`)
    fails with an explicit, attributable message instead of a raw
    pandas `KeyError` or a silently empty `(n, 0)` array.

    Args:
        df: The dataframe `feature_cols` will be indexed into.
        feature_cols: Feature column names to validate.

    Raises:
        ValueError: If `feature_cols` is empty or contains names that
            are not columns of `df`.
    """
    if not feature_cols:
        raise ValueError("feature_cols must be non-empty")
    missing = set(feature_cols) - set(df.columns)
    if missing:
        raise ValueError(f"feature_cols not found in df columns: {sorted(missing)}")


def fit_scaler(train_df: pd.DataFrame, feature_cols: list[str]) -> StandardScaler:
    """Fit a `StandardScaler` on the training dataframe's features only.

    Args:
        train_df: The training dataframe, e.g. from `split_by_year`.
        feature_cols: Feature column names to fit on, as returned by
            `get_feature_columns`.

    Returns:
        A `StandardScaler` fit on `train_df[feature_cols]`. Never called
        with test-year data, so no test-year statistics are learned.

    Raises:
        ValueError: If `feature_cols` is empty or not a subset of
            `train_df`'s columns (see `_validate_feature_cols`).
    """
    _validate_feature_cols(train_df, feature_cols)
    scaler = StandardScaler()
    scaler.fit(train_df[feature_cols])
    return scaler


def scale_features(
    df: pd.DataFrame, feature_cols: list[str], scaler: StandardScaler
) -> np.ndarray:
    """Transform a dataframe's features with an already-fit scaler.

    Args:
        df: The dataframe to transform (training or testing).
        feature_cols: Feature column names to transform, in the same order
            the scaler was fit with.
        scaler: A `StandardScaler` already fit by `fit_scaler`. Only
            `.transform()` is called here; the scaler is never re-fit, so
            this is safe to call on test-year data.

    Returns:
        The scaled feature values as a numpy array of shape
        `(len(df), len(feature_cols))`.

    Raises:
        ValueError: If `feature_cols` is empty or not a subset of `df`'s
            columns (see `_validate_feature_cols`).
    """
    _validate_feature_cols(df, feature_cols)
    return scaler.transform(df[feature_cols])


def prepare_train_test(
    year_data: dict[int, pd.DataFrame],
    feature_cols: list[str],
    train_years: list[int],
    test_years: list[int],
) -> tuple[np.ndarray, np.ndarray, pd.Series, pd.Series, StandardScaler]:
    """Build scaled train/test arrays and labels from per-year data.

    Combines `split_by_year`, `fit_scaler`, and `scale_features`: the
    scaler is fit on `train_years` only and then used to transform both
    the training and testing features, so the two sets are scaled
    consistently without the scaler ever seeing test-year rows.

    Args:
        year_data: Mapping of year to that year's combined dataframe.
        feature_cols: Feature column names, as returned by
            `get_feature_columns`.
        train_years: Years to use for training.
        test_years: Years to use for testing.

    Returns:
        A tuple `(X_train, X_test, y_train, y_test, scaler)`:
        - `X_train`, `X_test`: scaled feature arrays.
        - `y_train`, `y_test`: the corresponding `label` columns.
        - `scaler`: the `StandardScaler` fit on the training data, for
          reuse on additional data (e.g. per-year evaluation in Step 6).
    """
    train_df, test_df = split_by_year(year_data, train_years, test_years)
    scaler = fit_scaler(train_df, feature_cols)
    X_train = scale_features(train_df, feature_cols, scaler)
    X_test = scale_features(test_df, feature_cols, scaler)
    return X_train, X_test, train_df["label"], test_df["label"], scaler

"""Step 2: measure feature drift between years with the KS test.

Uses the two-sample Kolmogorov-Smirnov test to compare each feature's
distribution between pairs of years. This is purely descriptive: nothing
computed here is fit to the data, so it cannot leak test-year information
into any model fit in later steps (see PLAN.md's leakage-prevention
section).
"""

import pandas as pd
from scipy import stats


def ks_test_feature(series_a: pd.Series, series_b: pd.Series) -> tuple[float, float]:
    """Run a two-sample Kolmogorov-Smirnov test on one feature.

    Args:
        series_a: Feature values from the first sample (e.g. one year).
        series_b: Feature values from the second sample (e.g. another year).

    Returns:
        A tuple (statistic, p_value) from `scipy.stats.ks_2samp`. The
        statistic is in [0, 1]; larger means the two samples' distributions
        differ more.
    """
    result = stats.ks_2samp(series_a, series_b)
    return float(result.statistic), float(result.pvalue)


def compute_drift_between_years(
    year_data: dict[int, pd.DataFrame],
    year_a: int,
    year_b: int,
    feature_cols: list[str],
) -> pd.DataFrame:
    """Run the KS test on every feature between two years.

    Args:
        year_data: Mapping of year to that year's combined dataframe, as
            returned by `load_all_years`.
        year_a: The first year to compare.
        year_b: The second year to compare.
        feature_cols: Feature column names to test, as returned by
            `get_feature_columns`.

    Returns:
        A dataframe indexed by feature name with columns `statistic` and
        `p_value`, one row per feature in `feature_cols`.
    """
    df_a = year_data[year_a]
    df_b = year_data[year_b]
    rows = {
        feature: ks_test_feature(df_a[feature], df_b[feature])
        for feature in feature_cols
    }
    return pd.DataFrame.from_dict(
        rows, orient="index", columns=["statistic", "p_value"]
    ).rename_axis("feature")


def compute_drift_across_years(
    year_data: dict[int, pd.DataFrame], feature_cols: list[str]
) -> pd.DataFrame:
    """Run the KS test on every feature between each consecutive year pair.

    Args:
        year_data: Mapping of year to that year's combined dataframe.
        feature_cols: Feature column names to test.

    Returns:
        A dataframe with one row per (year_pair, feature), and columns
        `year_a`, `year_b`, `feature`, `statistic`, `p_value`. Consecutive
        pairs are formed from the sorted years present in `year_data`.
    """
    years = sorted(year_data.keys())
    pieces = []
    for year_a, year_b in zip(years[:-1], years[1:]):
        pair_df = compute_drift_between_years(year_data, year_a, year_b, feature_cols)
        pair_df = pair_df.reset_index()
        pair_df.insert(0, "year_b", year_b)
        pair_df.insert(0, "year_a", year_a)
        pieces.append(pair_df)
    return pd.concat(pieces, ignore_index=True)


def compare_earliest_latest_year(
    year_data: dict[int, pd.DataFrame], feature_cols: list[str]
) -> pd.DataFrame:
    """Run the KS test on every feature between the earliest and latest year.

    Args:
        year_data: Mapping of year to that year's combined dataframe.
        feature_cols: Feature column names to test.

    Returns:
        The `compute_drift_between_years` result for (min(years), max(years)),
        i.e. the single comparison with the largest time gap.
    """
    years = sorted(year_data.keys())
    return compute_drift_between_years(year_data, years[0], years[-1], feature_cols)


def top_drifting_features(drift_df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Return the features with the largest KS statistic.

    Args:
        drift_df: A dataframe with a `statistic` column, such as the output
            of `compute_drift_between_years` or `compare_earliest_latest_year`.
        top_n: Number of rows to return.

    Returns:
        The top `top_n` rows of `drift_df`, sorted descending by `statistic`.
    """
    return drift_df.sort_values("statistic", ascending=False).head(top_n)


def most_different_year_pairs(drift_df: pd.DataFrame) -> pd.DataFrame:
    """Rank consecutive year pairs by how much their features drifted.

    Args:
        drift_df: The output of `compute_drift_across_years`, with columns
            `year_a`, `year_b`, `feature`, `statistic`, `p_value`.

    Returns:
        A dataframe with one row per (year_a, year_b), columns `mean_statistic`
        and `max_statistic` aggregated over all features, sorted descending
        by `mean_statistic`.
    """
    grouped = drift_df.groupby(["year_a", "year_b"])["statistic"].agg(
        mean_statistic="mean", max_statistic="max"
    )
    return grouped.sort_values("mean_statistic", ascending=False).reset_index()

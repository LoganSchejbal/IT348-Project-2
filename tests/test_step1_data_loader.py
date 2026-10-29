"""Tests for Step 1 (Prepare the Data).

These tests check what the assignment and PLAN.md say Step 1 should do:
drop the first column, extract a binary label from the filename, keep
year grouping, combine benign/malware per year, and produce clean data
with no missing values. Most tests use small synthetic CSVs so they run
in seconds; tests that need the real dataset use the `real_data_dir`
fixture and are skipped when input_data/ is empty.
"""

from pathlib import Path

import pandas as pd
import pytest

from data_loader import (
    discover_dataset_files,
    extract_label_from_filename,
    get_feature_columns,
    load_all_years,
    load_single_file,
    load_year_data,
)


def _write_csv(path: Path, n_rows: int, n_feature_cols: int) -> None:
    """Write a small synthetic dataset file shaped like the real ones.

    Args:
        path: Destination CSV path (filename encodes year/class).
        n_rows: Number of app rows to write.
        n_feature_cols: Number of API-call feature columns (not counting
            the identifier column that is dropped on load).
    """
    columns = ["app_id"] + [f"api_call_{i}" for i in range(n_feature_cols)]
    data = {"app_id": [f"app_{i}" for i in range(n_rows)]}
    for i in range(n_feature_cols):
        data[f"api_call_{i}"] = [0] * n_rows
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(path, index=False)


@pytest.fixture
def synthetic_data_dir(tmp_path):
    """A tiny synthetic input_data/-like directory with two years of data."""
    for year in (2014, 2015):
        _write_csv(tmp_path / f"sampled_{year}_benign_api.csv", n_rows=5, n_feature_cols=4)
        _write_csv(tmp_path / f"sampled_{year}_malware_api.csv", n_rows=5, n_feature_cols=4)
    return tmp_path


# --- Label extraction from filenames -------------------------------------


def test_extract_label_from_filename_malware():
    """A filename containing 'malware' must map to label 1."""
    assert extract_label_from_filename("sampled_2014_malware_api.csv") == 1


def test_extract_label_from_filename_benign():
    """A filename containing 'benign' must map to label 0."""
    assert extract_label_from_filename("sampled_2014_benign_api.csv") == 0


def test_extract_label_from_filename_invalid_raises():
    """A filename with neither token should not silently default to a label."""
    with pytest.raises(ValueError):
        extract_label_from_filename("sampled_2014_unknown_api.csv")


# --- First column dropped --------------------------------------------------


def test_load_single_file_drops_first_column(synthetic_data_dir):
    """The identifier column (first column in the raw CSV) must not survive loading."""
    path = synthetic_data_dir / "sampled_2014_benign_api.csv"
    df = load_single_file(path)
    assert "app_id" not in df.columns


def test_load_single_file_feature_count_preserved(synthetic_data_dir):
    """Dropping the first column should leave exactly the feature columns plus label/year."""
    path = synthetic_data_dir / "sampled_2014_benign_api.csv"
    df = load_single_file(path)
    feature_cols = get_feature_columns(df)
    assert len(feature_cols) == 4  # n_feature_cols from _write_csv
    assert set(df.columns) == set(feature_cols) | {"label", "year"}


# --- Labels match filenames and contain only two classes -------------------


def test_load_single_file_label_matches_filename(synthetic_data_dir):
    """load_single_file must attach the label implied by the filename, uniformly for every row."""
    benign_df = load_single_file(synthetic_data_dir / "sampled_2014_benign_api.csv")
    malware_df = load_single_file(synthetic_data_dir / "sampled_2014_malware_api.csv")
    assert (benign_df["label"] == 0).all()
    assert (malware_df["label"] == 1).all()


def test_load_year_data_labels_only_two_classes(synthetic_data_dir):
    """Combined per-year data must contain only labels 0 and 1, nothing else."""
    combined = load_year_data(synthetic_data_dir, 2014)
    assert set(combined["label"].unique()) == {0, 1}


# --- Row counts: each file and each combined year ---------------------------


def test_load_single_file_row_count(synthetic_data_dir):
    """Loading one file must not add or drop rows."""
    df = load_single_file(synthetic_data_dir / "sampled_2014_benign_api.csv")
    assert len(df) == 5  # n_rows from _write_csv


def test_load_year_data_combines_both_classes(synthetic_data_dir):
    """A year's combined dataframe must have benign rows + malware rows."""
    combined = load_year_data(synthetic_data_dir, 2014)
    assert len(combined) == 10  # 5 benign + 5 malware


def test_load_year_data_missing_file_raises(synthetic_data_dir):
    """If a class file for the requested year is missing, loading must fail loudly, not silently return partial data."""
    (synthetic_data_dir / "sampled_2015_malware_api.csv").unlink()
    with pytest.raises(FileNotFoundError):
        load_year_data(synthetic_data_dir, 2015)


def test_load_all_years_discovers_every_year(synthetic_data_dir):
    """load_all_years must return one entry per year actually present in the directory."""
    year_data = load_all_years(synthetic_data_dir)
    assert set(year_data.keys()) == {2014, 2015}
    assert all(len(df) == 10 for df in year_data.values())


def test_discover_dataset_files_finds_all_class_files(synthetic_data_dir):
    """discover_dataset_files must find every sampled_*_api.csv file, not just one class."""
    files = discover_dataset_files(synthetic_data_dir)
    assert len(files) == 4  # 2 years x 2 classes


# --- No missing values after loading ----------------------------------------


def test_load_year_data_has_no_missing_values(synthetic_data_dir):
    """Loaded data must not contain NaNs introduced by the loading/concat process."""
    combined = load_year_data(synthetic_data_dir, 2014)
    assert not combined.isna().any().any()


# --- Real dataset checks (skipped if input_data/ is empty) ------------------


def test_real_data_file_has_expected_row_count(real_data_dir):
    """Per the assignment, each real dataset file has 1,500 rows."""
    path = real_data_dir / "sampled_2014_benign_api.csv"
    if not path.exists():
        pytest.skip("sampled_2014_benign_api.csv not found in input_data/")
    df = load_single_file(path)
    assert len(df) == 1500


def test_real_data_year_has_expected_combined_row_count(real_data_dir):
    """Per the assignment, a year's combined benign+malware data should have 3,000 rows (1,500 each)."""
    years_present = {
        int(p.name.split("_")[1]) for p in discover_dataset_files(real_data_dir)
    }
    if not years_present:
        pytest.skip("No dataset files found in input_data/")
    year = sorted(years_present)[0]
    combined = load_year_data(real_data_dir, year)
    assert len(combined) == 3000


def test_real_data_has_no_missing_values(real_data_dir):
    """The real dataset, once loaded, should contain no missing values."""
    years_present = {
        int(p.name.split("_")[1]) for p in discover_dataset_files(real_data_dir)
    }
    if not years_present:
        pytest.skip("No dataset files found in input_data/")
    year = sorted(years_present)[0]
    combined = load_year_data(real_data_dir, year)
    assert not combined.isna().any().any()

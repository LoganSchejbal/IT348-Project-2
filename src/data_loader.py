"""Step 1: load the Android API-call dataset and attach labels/years.

Reads the ``sampled_<year>_<class>_api.csv`` files from a data directory,
drops the identifier column, and attaches a binary ``label`` (1 = malware,
0 = benign) and an integer ``year`` column parsed from each filename. Years
and files present are discovered at runtime; nothing about the dataset is
hard-coded here.
"""

import re
import warnings
from pathlib import Path

import pandas as pd

# Matches filenames like "sampled_2014_malware_api.csv" and captures the
# year and class-label token so both can be parsed in one place. Matched
# case-insensitively so this stays consistent with
# extract_label_from_filename, which also lowercases before matching.
_FILENAME_PATTERN = re.compile(r"sampled_(\d{4})_(benign|malware)_api\.csv$", re.IGNORECASE)

# Expected shape (rows, columns) of a raw dataset file before the first
# column is dropped, per AGENTS.md/ASSIGNMENT.md. A column-count mismatch
# only triggers a warning (files are not rejected), but a row count above
# this is truncated to the expected row count (see load_single_file) so
# every file contributes the documented sample size.
_EXPECTED_RAW_SHAPE = (1500, 1849)


def extract_label_from_filename(filename: str) -> int:
    """Parse the binary label out of a dataset filename.

    Args:
        filename: A filename such as "sampled_2014_malware_api.csv". Only
            the "benign" or "malware" token is required to be present;
            the full naming scheme is not enforced here.

    Returns:
        1 if the filename contains "malware", 0 if it contains "benign".

    Raises:
        ValueError: If neither "benign" nor "malware" appears in filename.
    """
    name = Path(filename).name.lower()
    if "malware" in name:
        return 1
    if "benign" in name:
        return 0
    raise ValueError(
        f"Could not find 'benign' or 'malware' token in filename: {filename}"
    )


def _extract_year_from_filename(filename: str) -> int:
    """Parse the four-digit year out of a dataset filename.

    Args:
        filename: A filename such as "sampled_2014_malware_api.csv".

    Returns:
        The year as an int.

    Raises:
        ValueError: If the filename does not match the expected
            "sampled_<year>_<class>_api.csv" naming scheme.
    """
    match = _FILENAME_PATTERN.match(Path(filename).name)
    if not match:
        raise ValueError(
            f"Filename does not match 'sampled_<year>_<benign|malware>_api.csv': "
            f"{filename}"
        )
    return int(match.group(1))


def discover_dataset_files(data_dir: Path) -> list[Path]:
    """List all dataset CSV files present in a directory.

    Args:
        data_dir: Directory to search, e.g. the project's input_data/.

    Returns:
        A sorted list of paths matching "sampled_*_api.csv", so the set of
        files (and therefore years/classes) is determined at run time
        rather than assumed in advance.
    """
    return sorted(Path(data_dir).glob("sampled_*_api.csv"))


def load_single_file(path: Path) -> pd.DataFrame:
    """Load one dataset CSV file and attach its label and year.

    Drops the first column (an app identifier, not a feature) and adds a
    `label` column (from the filename's benign/malware token) and a `year`
    column (from the filename's year token).

    Args:
        path: Path to a single "sampled_<year>_<class>_api.csv" file.

    Returns:
        A dataframe with the identifier column removed and `label`/`year`
        columns appended to the original API-call feature columns.
    """
    df = pd.read_csv(path)
    # Flag unexpected shapes (e.g. a differently-sampled file) before the
    # first column is dropped, so anomalies surface automatically instead
    # of relying on manual inspection when writing docs/step1_data_summary.md.
    if df.shape != _EXPECTED_RAW_SHAPE:
        warnings.warn(
            f"{path.name}: expected raw shape {_EXPECTED_RAW_SHAPE}, got {df.shape}",
            stacklevel=2,
        )
    # Some real files (2014-2018) contain more rows than AGENTS.md's stated
    # 1,500 per file. Take the first N rows deterministically so every file
    # contributes the documented sample size instead of over-representing
    # years that happen to have extra rows.
    expected_rows = _EXPECTED_RAW_SHAPE[0]
    if len(df) > expected_rows:
        df = df.iloc[:expected_rows].reset_index(drop=True)
    # The first column is an app identifier (e.g. "apkname"), not a feature.
    df = df.drop(columns=df.columns[0])
    # label/year are added below; if either name already exists among the
    # feature columns, assign() would silently overwrite it and
    # get_feature_columns would then silently lose a real feature.
    collisions = {"label", "year"} & set(df.columns)
    if collisions:
        raise ValueError(
            f"{path.name}: feature column(s) {sorted(collisions)} collide with "
            "reserved 'label'/'year' column names"
        )
    # Assign both columns together (rather than one at a time) to avoid
    # repeated in-place inserts on a wide dataframe.
    return df.assign(
        label=extract_label_from_filename(path.name),
        year=_extract_year_from_filename(path.name),
    )


def load_year_data(data_dir: Path, year: int) -> pd.DataFrame:
    """Load and combine the benign and malware files for a single year.

    Args:
        data_dir: Directory containing the dataset CSV files.
        year: The year to load, e.g. 2014.

    Returns:
        A dataframe combining that year's benign and malware rows.

    Raises:
        FileNotFoundError: If either the benign or malware file for `year`
            is missing from `data_dir`.
    """
    data_dir = Path(data_dir)
    class_files = {
        "benign": data_dir / f"sampled_{year}_benign_api.csv",
        "malware": data_dir / f"sampled_{year}_malware_api.csv",
    }
    frames = []
    for class_name, file_path in class_files.items():
        if not file_path.exists():
            raise FileNotFoundError(
                f"Missing {class_name} file for year {year}: {file_path}"
            )
        frames.append(load_single_file(file_path))
    return pd.concat(frames, ignore_index=True)


def load_all_years(data_dir: Path) -> dict[int, pd.DataFrame]:
    """Discover and load every year present in a data directory.

    Args:
        data_dir: Directory containing the dataset CSV files.

    Returns:
        A dict mapping each discovered year to its combined
        (benign + malware) dataframe, as produced by `load_year_data`.
    """
    data_dir = Path(data_dir)
    years = sorted({_extract_year_from_filename(p.name) for p in discover_dataset_files(data_dir)})
    return {year: load_year_data(data_dir, year) for year in years}


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return the API-call feature column names of a loaded dataframe.

    Excludes the `label` and `year` columns added during loading, so later
    steps always derive the feature list from the data rather than
    hard-coding it.

    Args:
        df: A dataframe produced by `load_single_file`/`load_year_data`/
            `load_all_years`.

    Returns:
        The list of feature column names, in their original order.
    """
    return [col for col in df.columns if col not in ("label", "year")]

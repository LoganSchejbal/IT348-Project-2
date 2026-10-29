# Step 1 Test Log: Prepare the Data

- Tester transcript: transcripts/06_2026-10-28_tester_step1.md

## Tests written (tester)

One row per test function.

| Test | What it checks (from the assignment or plan) |
| --- | --- |
| `test_extract_label_from_filename_malware` | A filename containing "malware" is labeled 1 (ASSIGNMENT.md: labeling comes from the filename). |
| `test_extract_label_from_filename_benign` | A filename containing "benign" is labeled 0. |
| `test_extract_label_from_filename_invalid_raises` | A filename with neither token does not silently get a default label. |
| `test_load_single_file_drops_first_column` | The first column of each file is discarded (ASSIGNMENT.md). |
| `test_load_single_file_feature_count_preserved` | After dropping the first column, the remaining columns are exactly the feature columns plus `label`/`year` — nothing else is lost or added. |
| `test_load_single_file_label_matches_filename` | Every row in a loaded file gets the label implied by that file's name, uniformly. |
| `test_load_year_data_labels_only_two_classes` | Combined per-year data contains only the two label values 0 and 1 (binary target class, ASSIGNMENT.md). |
| `test_load_single_file_row_count` | Loading a file does not add or drop rows. |
| `test_load_year_data_combines_both_classes` | Combining files per year (ASSIGNMENT.md step 4) concatenates benign + malware rows into one dataset. |
| `test_load_year_data_missing_file_raises` | A missing class file for a requested year fails loudly instead of returning partial/silent data. |
| `test_load_all_years_discovers_every_year` | `load_all_years` returns one entry per year actually present in the directory, not a hard-coded list (PLAN.md: years discovered at runtime). |
| `test_discover_dataset_files_finds_all_class_files` | File discovery finds every `sampled_*_api.csv` file, not just one class. |
| `test_load_year_data_has_no_missing_values` | Loaded data contains no missing values after loading/concatenation. |
| `test_real_data_file_has_expected_row_count` | Each real dataset file has 1,500 rows (ASSIGNMENT.md: "Each file has 1,500 rows and 1,849 columns"). Skipped if input_data/ is empty. |
| `test_real_data_year_has_expected_combined_row_count` | A real year's combined benign+malware data has 3,000 rows (1,500 each). Skipped if input_data/ is empty. |
| `test_real_data_has_no_missing_values` | The real dataset, once loaded, has no missing values. |

## Failures and decisions (student)

One row per failing test. Decision is "Accepted" (the test is right; the builder fixes the code) or "Rejected" (the test is wrong; the tester fixes the test). Add the commit with the fix.

| Test | Cause | Decision | Fixed in commit |
| --- | --- | --- | --- |

## Runs (added by `python harness.py test N`; do not edit)

### Run 1: FAILED

- Time: 2026-10-28T22:38:00-05:00
- Commit: bd0cb4e
- Result: 2 failed, 14 passed in 7.96s
- Files: test_step1_data_loader.py

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.7.0 -- C:\Program Files\Python314\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\logan\Documents\IT348\Project 2
configfile: pytest.ini
collecting ... collected 16 items

tests/test_step1_data_loader.py::test_extract_label_from_filename_malware PASSED [  6%]
tests/test_step1_data_loader.py::test_extract_label_from_filename_benign PASSED [ 12%]
tests/test_step1_data_loader.py::test_extract_label_from_filename_invalid_raises PASSED [ 18%]
tests/test_step1_data_loader.py::test_load_single_file_drops_first_column PASSED [ 25%]
tests/test_step1_data_loader.py::test_load_single_file_feature_count_preserved PASSED [ 31%]
tests/test_step1_data_loader.py::test_load_single_file_label_matches_filename PASSED [ 37%]
tests/test_step1_data_loader.py::test_load_year_data_labels_only_two_classes PASSED [ 43%]
tests/test_step1_data_loader.py::test_load_single_file_row_count PASSED  [ 50%]
tests/test_step1_data_loader.py::test_load_year_data_combines_both_classes PASSED [ 56%]
tests/test_step1_data_loader.py::test_load_year_data_missing_file_raises PASSED [ 62%]
tests/test_step1_data_loader.py::test_load_all_years_discovers_every_year PASSED [ 68%]
tests/test_step1_data_loader.py::test_discover_dataset_files_finds_all_class_files PASSED [ 75%]
tests/test_step1_data_loader.py::test_load_year_data_has_no_missing_values PASSED [ 81%]
tests/test_step1_data_loader.py::test_real_data_file_has_expected_row_count FAILED [ 87%]
tests/test_step1_data_loader.py::test_real_data_year_has_expected_combined_row_count FAILED [ 93%]
tests/test_step1_data_loader.py::test_real_data_has_no_missing_values PASSED [100%]

================================== FAILURES ===================================
_________________ test_real_data_file_has_expected_row_count __________________

real_data_dir = WindowsPath('C:/Users/logan/Documents/IT348/Project 2/input_data')

    def test_real_data_file_has_expected_row_count(real_data_dir):
        """Per the assignment, each real dataset file has 1,500 rows."""
        path = real_data_dir / "sampled_2014_benign_api.csv"
        if not path.exists():
            pytest.skip("sampled_2014_benign_api.csv not found in input_data/")
        df = load_single_file(path)
>       assert len(df) == 1500
E       assert 9000 == 1500
E        +  where 9000 = len(      Landroid/accounts/AbstractAccountAuthenticator;.getAccountRemovalAllowed:(Landroid/accounts/AccountAuthenticatorResponse;Landroid/accounts/Account;)Landroid/os/Bundle;  ...  year\n0                                                     0                                                                                                                        ...  2014\n1                                                     0                                                                                                                        ...  2014\n2                                                     0                                                                                                                        ...  2014\n3                                                     0                                                                                                                        ...  2014\n4                                                     0                                                                                                                        ...  2014\n...                                                 ...                                                                                                                        ...   ...\n8995                                                  0                                                                                                                        ...  2014\n8996                                                  0                                                                                                                        ...  2014\n8997                                                  0                                                                                                                        ...  2014\n8998                                                  0                                                                                                                        ...  2014\n8999                                                  0                                                                                                                        ...  2014\n\n[9000 rows x 1850 columns])

tests\test_step1_data_loader.py:160: AssertionError
_____________ test_real_data_year_has_expected_combined_row_count _____________

real_data_dir = WindowsPath('C:/Users/logan/Documents/IT348/Project 2/input_data')

    def test_real_data_year_has_expected_combined_row_count(real_data_dir):
        """Per the assignment, a year's combined benign+malware data should have 3,000 rows (1,500 each)."""
        years_present = {
            int(p.name.split("_")[1]) for p in discover_dataset_files(real_data_dir)
        }
        if not years_present:
            pytest.skip("No dataset files found in input_data/")
        year = sorted(years_present)[0]
        combined = load_year_data(real_data_dir, year)
>       assert len(combined) == 3000
E       assert 18000 == 3000
E        +  where 18000 = len(       Landroid/accounts/AbstractAccountAuthenticator;.getAccountRemovalAllowed:(Landroid/accounts/AccountAuthenticatorResponse;Landroid/accounts/Account;)Landroid/os/Bundle;  ...  year\n0                                                      0                                                                                                                        ...  2014\n1                                                      0                                                                                                                        ...  2014\n2                                                      0                                                                                                                        ...  2014\n3                                                      0                                                                                                                        ...  2014\n4                                                      0                                                                                                                        ...  2014\n...                                                  ...                                                                                                                        ...   ...\n17995                                                  0                                                                                                                        ...  2014\n17996                                                  0                                                                                                                        ...  2014\n17997                                                  0                                                                                                                        ...  2014\n17998                                                  0                                                                                                                        ...  2014\n17999                                                  0                                                                                                                        ...  2014\n\n[18000 rows x 1850 columns])

tests\test_step1_data_loader.py:172: AssertionError
=================================== PASSES ====================================
=========================== short test summary info ===========================
PASSED tests/test_step1_data_loader.py::test_extract_label_from_filename_malware
PASSED tests/test_step1_data_loader.py::test_extract_label_from_filename_benign
PASSED tests/test_step1_data_loader.py::test_extract_label_from_filename_invalid_raises
PASSED tests/test_step1_data_loader.py::test_load_single_file_drops_first_column
PASSED tests/test_step1_data_loader.py::test_load_single_file_feature_count_preserved
PASSED tests/test_step1_data_loader.py::test_load_single_file_label_matches_filename
PASSED tests/test_step1_data_loader.py::test_load_year_data_labels_only_two_classes
PASSED tests/test_step1_data_loader.py::test_load_single_file_row_count
PASSED tests/test_step1_data_loader.py::test_load_year_data_combines_both_classes
PASSED tests/test_step1_data_loader.py::test_load_year_data_missing_file_raises
PASSED tests/test_step1_data_loader.py::test_load_all_years_discovers_every_year
PASSED tests/test_step1_data_loader.py::test_discover_dataset_files_finds_all_class_files
PASSED tests/test_step1_data_loader.py::test_load_year_data_has_no_missing_values
PASSED tests/test_step1_data_loader.py::test_real_data_has_no_missing_values
FAILED tests/test_step1_data_loader.py::test_real_data_file_has_expected_row_count
FAILED tests/test_step1_data_loader.py::test_real_data_year_has_expected_combined_row_count
======================== 2 failed, 14 passed in 7.96s =========================
```

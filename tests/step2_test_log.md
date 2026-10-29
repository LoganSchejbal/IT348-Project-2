# Step 2 Test Log: Handle Data Drift

- Tester transcript: transcripts/13_2026-10-29_tester_step2.md

## Tests written (tester)

One row per test function.

| Test | What it checks (from the assignment or plan) |
| --- | --- |
| test_ks_test_feature_statistic_in_unit_interval | KS statistic and p-value are both in [0, 1] |
| test_compute_drift_between_years_statistics_in_unit_interval | Every per-feature statistic from compute_drift_between_years is in [0, 1] |
| test_ks_test_feature_identical_distribution_near_zero_statistic | Two samples from the same distribution show ~no drift |
| test_ks_test_feature_same_values_statistic_is_zero | Comparing a sample to an exact copy of itself gives statistic 0, p-value 1 |
| test_compute_drift_between_years_stable_feature_low_statistic | A feature with no real shift between years reports low drift |
| test_ks_test_feature_shifted_distribution_detected | A clearly shifted synthetic feature produces a high KS statistic and low p-value |
| test_compute_drift_between_years_shifted_feature_detected | The deliberately shifted feature shows much more drift than the stable one |
| test_compute_drift_between_years_one_row_per_feature | compute_drift_between_years returns exactly one row per requested feature, with statistic/p_value columns |
| test_compute_drift_across_years_covers_consecutive_pairs | compute_drift_across_years produces one row per (consecutive year pair, feature) |
| test_top_drifting_features_sorted_descending | top_drifting_features sorts rows descending by statistic |
| test_top_drifting_features_respects_top_n | top_drifting_features caps the number of rows returned at top_n |
| test_compare_earliest_latest_year_uses_min_and_max_years | compare_earliest_latest_year compares min(years) vs max(years), matching a direct call with those years |
| test_compare_earliest_latest_year_not_equal_to_consecutive_pair | The earliest-vs-latest comparison differs from a consecutive-year comparison when they should differ |
| test_most_different_year_pairs_ranks_descending_by_mean | most_different_year_pairs ranks year pairs descending by mean_statistic, with the most-shifted pair on top |
| test_most_different_year_pairs_has_mean_and_max_columns | most_different_year_pairs reports year_a, year_b, mean_statistic, and max_statistic columns, one row per pair |
| test_real_data_drift_statistics_in_unit_interval | On the real dataset, every KS statistic between the earliest and latest year is in [0, 1] (skipped if input_data/ is empty) |

## Failures and decisions (student)

One row per failing test. Decision is "Accepted" (the test is right; the builder fixes the code) or "Rejected" (the test is wrong; the tester fixes the test). Add the commit with the fix.

| Test | Cause | Decision | Fixed in commit |
| --- | --- | --- | --- |

## Runs (added by `python harness.py test N`; do not edit)

### Run 1: PASSED

- Time: 2026-10-29T00:23:42-05:00
- Commit: ddce36d
- Result: 16 passed, 12 warnings in 8.72s
- Files: test_step2_drift_analysis.py

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.7.0 -- C:\Users\logan\Documents\IT348\Project 2\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\logan\Documents\IT348\Project 2
configfile: pytest.ini
collecting ... collected 16 items

tests/test_step2_drift_analysis.py::test_ks_test_feature_statistic_in_unit_interval PASSED [  6%]
tests/test_step2_drift_analysis.py::test_compute_drift_between_years_statistics_in_unit_interval PASSED [ 12%]
tests/test_step2_drift_analysis.py::test_ks_test_feature_identical_distribution_near_zero_statistic PASSED [ 18%]
tests/test_step2_drift_analysis.py::test_ks_test_feature_same_values_statistic_is_zero PASSED [ 25%]
tests/test_step2_drift_analysis.py::test_compute_drift_between_years_stable_feature_low_statistic PASSED [ 31%]
tests/test_step2_drift_analysis.py::test_ks_test_feature_shifted_distribution_detected PASSED [ 37%]
tests/test_step2_drift_analysis.py::test_compute_drift_between_years_shifted_feature_detected PASSED [ 43%]
tests/test_step2_drift_analysis.py::test_compute_drift_between_years_one_row_per_feature PASSED [ 50%]
tests/test_step2_drift_analysis.py::test_compute_drift_across_years_covers_consecutive_pairs PASSED [ 56%]
tests/test_step2_drift_analysis.py::test_top_drifting_features_sorted_descending PASSED [ 62%]
tests/test_step2_drift_analysis.py::test_top_drifting_features_respects_top_n PASSED [ 68%]
tests/test_step2_drift_analysis.py::test_compare_earliest_latest_year_uses_min_and_max_years PASSED [ 75%]
tests/test_step2_drift_analysis.py::test_compare_earliest_latest_year_not_equal_to_consecutive_pair PASSED [ 81%]
tests/test_step2_drift_analysis.py::test_most_different_year_pairs_ranks_descending_by_mean PASSED [ 87%]
tests/test_step2_drift_analysis.py::test_most_different_year_pairs_has_mean_and_max_columns PASSED [ 93%]
tests/test_step2_drift_analysis.py::test_real_data_drift_statistics_in_unit_interval PASSED [100%]

============================== warnings summary ===============================
tests/test_step2_drift_analysis.py::test_real_data_drift_statistics_in_unit_interval
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2014_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step2_drift_analysis.py::test_real_data_drift_statistics_in_unit_interval
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2014_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step2_drift_analysis.py::test_real_data_drift_statistics_in_unit_interval
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2015_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step2_drift_analysis.py::test_real_data_drift_statistics_in_unit_interval
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2015_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step2_drift_analysis.py::test_real_data_drift_statistics_in_unit_interval
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2016_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step2_drift_analysis.py::test_real_data_drift_statistics_in_unit_interval
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2016_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step2_drift_analysis.py::test_real_data_drift_statistics_in_unit_interval
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2017_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step2_drift_analysis.py::test_real_data_drift_statistics_in_unit_interval
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2017_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step2_drift_analysis.py::test_real_data_drift_statistics_in_unit_interval
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2018_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step2_drift_analysis.py::test_real_data_drift_statistics_in_unit_interval
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2018_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step2_drift_analysis.py::test_real_data_drift_statistics_in_unit_interval
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:133: PerformanceWarning: DataFrame is highly fragmented.  This is usually the result of calling `frame.insert` many times, which has poor performance.  Consider joining all columns at once using pd.concat(axis=1) instead. To get a de-fragmented frame, use `newframe = frame.copy()`
    return df.assign(

tests/test_step2_drift_analysis.py::test_real_data_drift_statistics_in_unit_interval
  C:\Users\logan\Documents\IT348\Project 2\.venv\Lib\site-packages\numpy\lib\_function_base_impl.py:2611: RuntimeWarning: ks_2samp: Exact calculation unsuccessful. Switching to method=asymp.
    outputs = ufunc(*args, out=...)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=================================== PASSES ====================================
=========================== short test summary info ===========================
PASSED tests/test_step2_drift_analysis.py::test_ks_test_feature_statistic_in_unit_interval
PASSED tests/test_step2_drift_analysis.py::test_compute_drift_between_years_statistics_in_unit_interval
PASSED tests/test_step2_drift_analysis.py::test_ks_test_feature_identical_distribution_near_zero_statistic
PASSED tests/test_step2_drift_analysis.py::test_ks_test_feature_same_values_statistic_is_zero
PASSED tests/test_step2_drift_analysis.py::test_compute_drift_between_years_stable_feature_low_statistic
PASSED tests/test_step2_drift_analysis.py::test_ks_test_feature_shifted_distribution_detected
PASSED tests/test_step2_drift_analysis.py::test_compute_drift_between_years_shifted_feature_detected
PASSED tests/test_step2_drift_analysis.py::test_compute_drift_between_years_one_row_per_feature
PASSED tests/test_step2_drift_analysis.py::test_compute_drift_across_years_covers_consecutive_pairs
PASSED tests/test_step2_drift_analysis.py::test_top_drifting_features_sorted_descending
PASSED tests/test_step2_drift_analysis.py::test_top_drifting_features_respects_top_n
PASSED tests/test_step2_drift_analysis.py::test_compare_earliest_latest_year_uses_min_and_max_years
PASSED tests/test_step2_drift_analysis.py::test_compare_earliest_latest_year_not_equal_to_consecutive_pair
PASSED tests/test_step2_drift_analysis.py::test_most_different_year_pairs_ranks_descending_by_mean
PASSED tests/test_step2_drift_analysis.py::test_most_different_year_pairs_has_mean_and_max_columns
PASSED tests/test_step2_drift_analysis.py::test_real_data_drift_statistics_in_unit_interval
======================= 16 passed, 12 warnings in 8.72s =======================
```

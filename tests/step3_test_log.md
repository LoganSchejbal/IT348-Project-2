# Step 3 Test Log: Preprocess Data for Model Training

- Tester transcript: transcripts/18_2026-10-29_tester_step3.md

## Tests written (tester)

One row per test function.

| Test | What it checks (from the assignment or plan) |
| --- | --- |
| test_split_years_in_half_even_count_equal_halves | An even number of years splits into two equal, non-overlapping halves |
| test_split_years_in_half_odd_count_extra_year_in_train | An odd number of years gives the earlier half the extra year |
| test_split_years_in_half_sorts_unordered_input | The split is chronological regardless of input order |
| test_split_years_in_half_every_year_assigned_exactly_once | Every input year appears in exactly one of the two output lists, with no overlap |
| test_split_years_in_half_too_few_years_raises | Fewer than 2 distinct years raises ValueError |
| test_split_by_year_raises_on_unknown_year | Requesting a year not present in year_data raises ValueError |
| test_split_by_year_no_shared_years_between_train_and_test | Train and test dataframes are built from disjoint sets of years |
| test_split_by_year_row_counts_match_requested_years | The concatenated frames contain exactly the rows of the requested years |
| test_fit_scaler_mean_matches_manual_training_mean | The scaler's learned mean matches a hand-computed mean of only the training years |
| test_fit_scaler_ignores_test_year_distribution | The scaler's mean is not influenced by the (differently-shifted) test years |
| test_scaled_training_columns_have_mean_near_zero | Transforming the training data with its own fitted scaler gives ~0 mean columns |
| test_scale_features_never_refits_scaler | Scaling the test set does not change the scaler's learned mean/scale |
| test_scaled_test_columns_not_necessarily_mean_zero | Transformed test data (scaled with the training scaler) reflects the drift instead of being re-centered to 0 |
| test_prepare_train_test_shares_no_years | X_train/y_train and X_test/y_test come from disjoint, non-overlapping years |
| test_prepare_train_test_same_number_of_feature_columns | X_train and X_test have the same number of feature columns |
| test_scale_features_preserves_feature_cols_order | Scaling with a reversed feature_cols order changes which column holds which feature, proving column order is preserved from the input |
| test_prepare_train_test_output_shapes_match_row_counts | X_train/X_test/y_train/y_test shapes match the row counts of the requested years |
| test_prepare_train_test_returns_fitted_scaler | prepare_train_test returns a scaler already fit (mean_ matches) on train years only |
| test_real_data_train_test_share_no_years_and_same_columns | On the real dataset, split_years_in_half's halves share no years, and prepare_train_test gives matching train/test column counts with a near-zero training mean (skipped if input_data/ is empty) |

## Failures and decisions (student)

One row per failing test. Decision is "Accepted" (the test is right; the builder fixes the code) or "Rejected" (the test is wrong; the tester fixes the test). Add the commit with the fix.

| Test | Cause | Decision | Fixed in commit |
| --- | --- | --- | --- |

## Runs (added by `python harness.py test N`; do not edit)

### Run 1: PASSED

- Time: 2026-10-29T00:59:30-05:00
- Commit: 1fa1cdc
- Result: 19 passed, 11 warnings in 8.56s
- Files: test_step3_preprocessing.py

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.7.0 -- C:\Users\logan\Documents\IT348\Project 2\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\logan\Documents\IT348\Project 2
configfile: pytest.ini
collecting ... collected 19 items

tests/test_step3_preprocessing.py::test_split_years_in_half_even_count_equal_halves PASSED [  5%]
tests/test_step3_preprocessing.py::test_split_years_in_half_odd_count_extra_year_in_train PASSED [ 10%]
tests/test_step3_preprocessing.py::test_split_years_in_half_sorts_unordered_input PASSED [ 15%]
tests/test_step3_preprocessing.py::test_split_years_in_half_every_year_assigned_exactly_once PASSED [ 21%]
tests/test_step3_preprocessing.py::test_split_years_in_half_too_few_years_raises PASSED [ 26%]
tests/test_step3_preprocessing.py::test_split_by_year_raises_on_unknown_year PASSED [ 31%]
tests/test_step3_preprocessing.py::test_split_by_year_no_shared_years_between_train_and_test PASSED [ 36%]
tests/test_step3_preprocessing.py::test_split_by_year_row_counts_match_requested_years PASSED [ 42%]
tests/test_step3_preprocessing.py::test_fit_scaler_mean_matches_manual_training_mean PASSED [ 47%]
tests/test_step3_preprocessing.py::test_fit_scaler_ignores_test_year_distribution PASSED [ 52%]
tests/test_step3_preprocessing.py::test_scaled_training_columns_have_mean_near_zero PASSED [ 57%]
tests/test_step3_preprocessing.py::test_scale_features_never_refits_scaler PASSED [ 63%]
tests/test_step3_preprocessing.py::test_scaled_test_columns_not_necessarily_mean_zero PASSED [ 68%]
tests/test_step3_preprocessing.py::test_prepare_train_test_shares_no_years PASSED [ 73%]
tests/test_step3_preprocessing.py::test_prepare_train_test_same_number_of_feature_columns PASSED [ 78%]
tests/test_step3_preprocessing.py::test_scale_features_preserves_feature_cols_order PASSED [ 84%]
tests/test_step3_preprocessing.py::test_prepare_train_test_output_shapes_match_row_counts PASSED [ 89%]
tests/test_step3_preprocessing.py::test_prepare_train_test_returns_fitted_scaler PASSED [ 94%]
tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns PASSED [100%]

============================== warnings summary ===============================
tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2014_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2014_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2015_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2015_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2016_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2016_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2017_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2017_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2018_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2018_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:133: PerformanceWarning: DataFrame is highly fragmented.  This is usually the result of calling `frame.insert` many times, which has poor performance.  Consider joining all columns at once using pd.concat(axis=1) instead. To get a de-fragmented frame, use `newframe = frame.copy()`
    return df.assign(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=================================== PASSES ====================================
=========================== short test summary info ===========================
PASSED tests/test_step3_preprocessing.py::test_split_years_in_half_even_count_equal_halves
PASSED tests/test_step3_preprocessing.py::test_split_years_in_half_odd_count_extra_year_in_train
PASSED tests/test_step3_preprocessing.py::test_split_years_in_half_sorts_unordered_input
PASSED tests/test_step3_preprocessing.py::test_split_years_in_half_every_year_assigned_exactly_once
PASSED tests/test_step3_preprocessing.py::test_split_years_in_half_too_few_years_raises
PASSED tests/test_step3_preprocessing.py::test_split_by_year_raises_on_unknown_year
PASSED tests/test_step3_preprocessing.py::test_split_by_year_no_shared_years_between_train_and_test
PASSED tests/test_step3_preprocessing.py::test_split_by_year_row_counts_match_requested_years
PASSED tests/test_step3_preprocessing.py::test_fit_scaler_mean_matches_manual_training_mean
PASSED tests/test_step3_preprocessing.py::test_fit_scaler_ignores_test_year_distribution
PASSED tests/test_step3_preprocessing.py::test_scaled_training_columns_have_mean_near_zero
PASSED tests/test_step3_preprocessing.py::test_scale_features_never_refits_scaler
PASSED tests/test_step3_preprocessing.py::test_scaled_test_columns_not_necessarily_mean_zero
PASSED tests/test_step3_preprocessing.py::test_prepare_train_test_shares_no_years
PASSED tests/test_step3_preprocessing.py::test_prepare_train_test_same_number_of_feature_columns
PASSED tests/test_step3_preprocessing.py::test_scale_features_preserves_feature_cols_order
PASSED tests/test_step3_preprocessing.py::test_prepare_train_test_output_shapes_match_row_counts
PASSED tests/test_step3_preprocessing.py::test_prepare_train_test_returns_fitted_scaler
PASSED tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
======================= 19 passed, 11 warnings in 8.56s =======================
```

### Run 2: PASSED

- Time: 2026-10-29T01:04:22-05:00
- Commit: b7ad374
- Result: 19 passed, 11 warnings in 4.51s
- Files: test_step3_preprocessing.py

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.7.0 -- C:\Users\logan\Documents\IT348\Project 2\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\logan\Documents\IT348\Project 2
configfile: pytest.ini
collecting ... collected 19 items

tests/test_step3_preprocessing.py::test_split_years_in_half_even_count_equal_halves PASSED [  5%]
tests/test_step3_preprocessing.py::test_split_years_in_half_odd_count_extra_year_in_train PASSED [ 10%]
tests/test_step3_preprocessing.py::test_split_years_in_half_sorts_unordered_input PASSED [ 15%]
tests/test_step3_preprocessing.py::test_split_years_in_half_every_year_assigned_exactly_once PASSED [ 21%]
tests/test_step3_preprocessing.py::test_split_years_in_half_too_few_years_raises PASSED [ 26%]
tests/test_step3_preprocessing.py::test_split_by_year_raises_on_unknown_year PASSED [ 31%]
tests/test_step3_preprocessing.py::test_split_by_year_no_shared_years_between_train_and_test PASSED [ 36%]
tests/test_step3_preprocessing.py::test_split_by_year_row_counts_match_requested_years PASSED [ 42%]
tests/test_step3_preprocessing.py::test_fit_scaler_mean_matches_manual_training_mean PASSED [ 47%]
tests/test_step3_preprocessing.py::test_fit_scaler_ignores_test_year_distribution PASSED [ 52%]
tests/test_step3_preprocessing.py::test_scaled_training_columns_have_mean_near_zero PASSED [ 57%]
tests/test_step3_preprocessing.py::test_scale_features_never_refits_scaler PASSED [ 63%]
tests/test_step3_preprocessing.py::test_scaled_test_columns_not_necessarily_mean_zero PASSED [ 68%]
tests/test_step3_preprocessing.py::test_prepare_train_test_shares_no_years PASSED [ 73%]
tests/test_step3_preprocessing.py::test_prepare_train_test_same_number_of_feature_columns PASSED [ 78%]
tests/test_step3_preprocessing.py::test_scale_features_preserves_feature_cols_order PASSED [ 84%]
tests/test_step3_preprocessing.py::test_prepare_train_test_output_shapes_match_row_counts PASSED [ 89%]
tests/test_step3_preprocessing.py::test_prepare_train_test_returns_fitted_scaler PASSED [ 94%]
tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns PASSED [100%]

============================== warnings summary ===============================
tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2014_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2014_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2015_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2015_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2016_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2016_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2017_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2017_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2018_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2018_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:133: PerformanceWarning: DataFrame is highly fragmented.  This is usually the result of calling `frame.insert` many times, which has poor performance.  Consider joining all columns at once using pd.concat(axis=1) instead. To get a de-fragmented frame, use `newframe = frame.copy()`
    return df.assign(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=================================== PASSES ====================================
=========================== short test summary info ===========================
PASSED tests/test_step3_preprocessing.py::test_split_years_in_half_even_count_equal_halves
PASSED tests/test_step3_preprocessing.py::test_split_years_in_half_odd_count_extra_year_in_train
PASSED tests/test_step3_preprocessing.py::test_split_years_in_half_sorts_unordered_input
PASSED tests/test_step3_preprocessing.py::test_split_years_in_half_every_year_assigned_exactly_once
PASSED tests/test_step3_preprocessing.py::test_split_years_in_half_too_few_years_raises
PASSED tests/test_step3_preprocessing.py::test_split_by_year_raises_on_unknown_year
PASSED tests/test_step3_preprocessing.py::test_split_by_year_no_shared_years_between_train_and_test
PASSED tests/test_step3_preprocessing.py::test_split_by_year_row_counts_match_requested_years
PASSED tests/test_step3_preprocessing.py::test_fit_scaler_mean_matches_manual_training_mean
PASSED tests/test_step3_preprocessing.py::test_fit_scaler_ignores_test_year_distribution
PASSED tests/test_step3_preprocessing.py::test_scaled_training_columns_have_mean_near_zero
PASSED tests/test_step3_preprocessing.py::test_scale_features_never_refits_scaler
PASSED tests/test_step3_preprocessing.py::test_scaled_test_columns_not_necessarily_mean_zero
PASSED tests/test_step3_preprocessing.py::test_prepare_train_test_shares_no_years
PASSED tests/test_step3_preprocessing.py::test_prepare_train_test_same_number_of_feature_columns
PASSED tests/test_step3_preprocessing.py::test_scale_features_preserves_feature_cols_order
PASSED tests/test_step3_preprocessing.py::test_prepare_train_test_output_shapes_match_row_counts
PASSED tests/test_step3_preprocessing.py::test_prepare_train_test_returns_fitted_scaler
PASSED tests/test_step3_preprocessing.py::test_real_data_train_test_share_no_years_and_same_columns
======================= 19 passed, 11 warnings in 4.51s =======================
```

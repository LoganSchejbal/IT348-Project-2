# Step 6 Test Log: Test Data Prediction

- Tester transcript: transcripts/30_2026-10-29_tester_step6.md

## Tests written (tester)

One row per test function.

| Test | What it checks (from the assignment or plan) |
| --- | --- |
| test_evaluate_by_year_returns_one_row_per_year_classifier_combination | `evaluate_by_year` returns exactly `len(years) * len(models)` rows, one per (year, classifier) pair. |
| test_evaluate_by_year_only_covers_requested_years | Years present in `year_data` but not passed in `years` are excluded from the output. |
| test_evaluate_by_year_columns_are_correct | Output has exactly the columns `year`, `classifier`, `accuracy`, `precision`, `recall`, `f1`. |
| test_evaluate_by_year_metrics_are_within_unit_interval | All four metric values are in `[0, 1]` across multiple years and classifiers. |
| test_evaluate_by_year_perfect_and_worst_case_metrics_at_the_boundaries | A perfect predictor scores 1.0 on all metrics; an always-wrong predictor against an all-malware year scores 0.0, bounding metrics at both ends of `[0, 1]`. |
| test_evaluate_by_year_never_calls_scaler_fit | The scaler passed in is only `.transform()`-ed, never `.fit()`-ed (checked with a recording stand-in). |
| test_evaluate_by_year_does_not_change_a_real_scalers_learned_parameters | A real fitted `StandardScaler`'s `mean_`/`scale_` are unchanged before vs. after `evaluate_by_year` is called, confirming no re-fit/leakage from test years. |
| test_evaluate_by_year_scores_each_year_against_its_own_labels | A fixed-prediction model scores differently on two years with different true labels, confirming each year is scored against its own `label` column, not a mixed or wrong one. |
| test_evaluate_by_year_on_real_pipeline | End-to-end on the real dataset (skipped if `input_data/` is empty): one row per (test year, classifier), all metrics in `[0, 1]`, and the scaler's fitted parameters unchanged after evaluating every test year. |

## Failures and decisions (student)

One row per failing test. Decision is "Accepted" (the test is right; the builder fixes the code) or "Rejected" (the test is wrong; the tester fixes the test). Add the commit with the fix.

| Test | Cause | Decision | Fixed in commit |
| --- | --- | --- | --- |

## Runs (added by `python harness.py test N`; do not edit)

### Run 1: PASSED

- Time: 2026-10-29T15:04:23-05:00
- Commit: 02855c4
- Result: 9 passed, 11 warnings in 7.25s
- Files: test_step6_evaluation.py

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.7.0 -- C:\Program Files\Python314\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\logan\Documents\IT348\Project 2
configfile: pytest.ini
collecting ... collected 9 items

tests/test_step6_evaluation.py::test_evaluate_by_year_returns_one_row_per_year_classifier_combination PASSED [ 11%]
tests/test_step6_evaluation.py::test_evaluate_by_year_only_covers_requested_years PASSED [ 22%]
tests/test_step6_evaluation.py::test_evaluate_by_year_columns_are_correct PASSED [ 33%]
tests/test_step6_evaluation.py::test_evaluate_by_year_metrics_are_within_unit_interval PASSED [ 44%]
tests/test_step6_evaluation.py::test_evaluate_by_year_perfect_and_worst_case_metrics_at_the_boundaries PASSED [ 55%]
tests/test_step6_evaluation.py::test_evaluate_by_year_never_calls_scaler_fit PASSED [ 66%]
tests/test_step6_evaluation.py::test_evaluate_by_year_does_not_change_a_real_scalers_learned_parameters PASSED [ 77%]
tests/test_step6_evaluation.py::test_evaluate_by_year_scores_each_year_against_its_own_labels PASSED [ 88%]
tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline PASSED [100%]

============================== warnings summary ===============================
tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2014_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2014_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2015_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2015_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2016_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2016_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2017_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2017_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2018_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2018_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:133: PerformanceWarning: DataFrame is highly fragmented.  This is usually the result of calling `frame.insert` many times, which has poor performance.  Consider joining all columns at once using pd.concat(axis=1) instead. To get a de-fragmented frame, use `newframe = frame.copy()`
    return df.assign(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=================================== PASSES ====================================
=========================== short test summary info ===========================
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_returns_one_row_per_year_classifier_combination
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_only_covers_requested_years
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_columns_are_correct
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_metrics_are_within_unit_interval
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_perfect_and_worst_case_metrics_at_the_boundaries
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_never_calls_scaler_fit
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_does_not_change_a_real_scalers_learned_parameters
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_scores_each_year_against_its_own_labels
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
======================= 9 passed, 11 warnings in 7.25s ========================
```

### Run 2: PASSED

- Time: 2026-10-29T15:07:17-05:00
- Commit: cfe1da7
- Result: 9 passed, 11 warnings in 6.40s
- Files: test_step6_evaluation.py

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.7.0 -- C:\Program Files\Python314\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\logan\Documents\IT348\Project 2
configfile: pytest.ini
collecting ... collected 9 items

tests/test_step6_evaluation.py::test_evaluate_by_year_returns_one_row_per_year_classifier_combination PASSED [ 11%]
tests/test_step6_evaluation.py::test_evaluate_by_year_only_covers_requested_years PASSED [ 22%]
tests/test_step6_evaluation.py::test_evaluate_by_year_columns_are_correct PASSED [ 33%]
tests/test_step6_evaluation.py::test_evaluate_by_year_metrics_are_within_unit_interval PASSED [ 44%]
tests/test_step6_evaluation.py::test_evaluate_by_year_perfect_and_worst_case_metrics_at_the_boundaries PASSED [ 55%]
tests/test_step6_evaluation.py::test_evaluate_by_year_never_calls_scaler_fit PASSED [ 66%]
tests/test_step6_evaluation.py::test_evaluate_by_year_does_not_change_a_real_scalers_learned_parameters PASSED [ 77%]
tests/test_step6_evaluation.py::test_evaluate_by_year_scores_each_year_against_its_own_labels PASSED [ 88%]
tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline PASSED [100%]

============================== warnings summary ===============================
tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2014_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2014_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2015_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2015_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2016_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2016_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2017_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2017_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2018_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2018_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:133: PerformanceWarning: DataFrame is highly fragmented.  This is usually the result of calling `frame.insert` many times, which has poor performance.  Consider joining all columns at once using pd.concat(axis=1) instead. To get a de-fragmented frame, use `newframe = frame.copy()`
    return df.assign(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=================================== PASSES ====================================
=========================== short test summary info ===========================
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_returns_one_row_per_year_classifier_combination
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_only_covers_requested_years
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_columns_are_correct
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_metrics_are_within_unit_interval
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_perfect_and_worst_case_metrics_at_the_boundaries
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_never_calls_scaler_fit
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_does_not_change_a_real_scalers_learned_parameters
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_scores_each_year_against_its_own_labels
PASSED tests/test_step6_evaluation.py::test_evaluate_by_year_on_real_pipeline
======================= 9 passed, 11 warnings in 6.40s ========================
```

# Step 7 Test Log: Sustainable ML Approach

- Tester transcript: transcripts/34_2026-10-29_tester_step7.md

## Tests written (tester)

One row per test function.

| Test | What it checks (from the assignment or plan) |
| --- | --- |
| test_retraining_trajectory_never_includes_the_current_or_future_test_year | A retrain round's training pool size equals only train_years plus already-scored test years -- the about-to-be-scored year (and later years) never leak in. |
| test_retraining_trajectory_processes_years_chronologically_regardless_of_input_order | Passing test_years out of order still processes/trains them chronologically, so a later year is never folded in before an earlier one is scored. |
| test_retraining_trajectory_raises_on_year_missing_from_year_data | A train or test year absent from year_data raises instead of silently skipping. |
| test_retraining_trajectory_each_round_uses_a_freshly_built_classifier | The classifier factory is called once per test year, producing a distinct instance each round (never reusing a previous round's fitted model). |
| test_retraining_trajectory_labels_grow_to_include_previously_scored_years | Each round's fit labels are exactly train_years' labels plus every already-scored test year's labels, in order -- proof the retrained model actually trains on the newer data. |
| test_retraining_trajectory_fits_a_distinct_scaler_each_round | Each retrain round fits a brand-new StandardScaler on the current pool rather than reusing a prior round's scaler, so transformed values change as the pool grows. |
| test_static_model_trajectory_never_calls_fit_on_the_model_or_scaler | static_model_trajectory never calls .fit() on the model or scaler (stand-ins raise if fit is attempted) -- the baseline is never updated. |
| test_static_model_trajectory_uses_the_same_fitted_parameters_across_every_year | A real StandardScaler's mean_/scale_ are unchanged before and after scoring multiple years with the static baseline. |
| test_compare_static_vs_retrained_aligns_every_year_and_classifier_without_dropping_or_duplicating | The merged comparison has exactly one row per (year, classifier) pair present in both trajectories -- none dropped, none duplicated. |
| test_compare_static_vs_retrained_raises_when_year_classifier_pairs_differ | A mismatched set of (year, classifier) pairs between the two trajectories raises instead of merging silently. |
| test_run_sustainability_comparison_includes_both_classifiers | The full comparison's output covers every classifier name in classifier_factories, not just one. |
| test_run_sustainability_comparison_raises_when_factories_and_models_disagree | A mismatch between classifier_factories' and models' keys raises instead of comparing the wrong pair. |
| test_sustainable_pipeline_on_real_data_never_leaks_future_years | End-to-end on the real dataset (skipped if input_data/ is empty): each retrain round's training row count equals train_years plus already-scored test years, confirming no future-year leakage on real data. |

## Failures and decisions (student)

One row per failing test. Decision is "Accepted" (the test is right; the builder fixes the code) or "Rejected" (the test is wrong; the tester fixes the test). Add the commit with the fix.

| Test | Cause | Decision | Fixed in commit |
| --- | --- | --- | --- |

## Runs (added by `python harness.py test N`; do not edit)

### Run 1: PASSED

- Time: 2026-10-29T15:22:37-05:00
- Commit: 57468ff
- Result: 13 passed, 11 warnings in 15.65s
- Files: test_step7_sustainable.py

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.7.0 -- C:\Program Files\Python314\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\logan\Documents\IT348\Project 2
configfile: pytest.ini
collecting ... collected 13 items

tests/test_step7_sustainable.py::test_retraining_trajectory_never_includes_the_current_or_future_test_year PASSED [  7%]
tests/test_step7_sustainable.py::test_retraining_trajectory_processes_years_chronologically_regardless_of_input_order PASSED [ 15%]
tests/test_step7_sustainable.py::test_retraining_trajectory_raises_on_year_missing_from_year_data PASSED [ 23%]
tests/test_step7_sustainable.py::test_retraining_trajectory_each_round_uses_a_freshly_built_classifier PASSED [ 30%]
tests/test_step7_sustainable.py::test_retraining_trajectory_labels_grow_to_include_previously_scored_years PASSED [ 38%]
tests/test_step7_sustainable.py::test_retraining_trajectory_fits_a_distinct_scaler_each_round PASSED [ 46%]
tests/test_step7_sustainable.py::test_static_model_trajectory_never_calls_fit_on_the_model_or_scaler PASSED [ 53%]
tests/test_step7_sustainable.py::test_static_model_trajectory_uses_the_same_fitted_parameters_across_every_year PASSED [ 61%]
tests/test_step7_sustainable.py::test_compare_static_vs_retrained_aligns_every_year_and_classifier_without_dropping_or_duplicating PASSED [ 69%]
tests/test_step7_sustainable.py::test_compare_static_vs_retrained_raises_when_year_classifier_pairs_differ PASSED [ 76%]
tests/test_step7_sustainable.py::test_run_sustainability_comparison_includes_both_classifiers PASSED [ 84%]
tests/test_step7_sustainable.py::test_run_sustainability_comparison_raises_when_factories_and_models_disagree PASSED [ 92%]
tests/test_step7_sustainable.py::test_sustainable_pipeline_on_real_data_never_leaks_future_years PASSED [100%]

============================== warnings summary ===============================
tests/test_step7_sustainable.py::test_sustainable_pipeline_on_real_data_never_leaks_future_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2014_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step7_sustainable.py::test_sustainable_pipeline_on_real_data_never_leaks_future_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2014_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step7_sustainable.py::test_sustainable_pipeline_on_real_data_never_leaks_future_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2015_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step7_sustainable.py::test_sustainable_pipeline_on_real_data_never_leaks_future_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2015_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step7_sustainable.py::test_sustainable_pipeline_on_real_data_never_leaks_future_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2016_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step7_sustainable.py::test_sustainable_pipeline_on_real_data_never_leaks_future_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2016_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step7_sustainable.py::test_sustainable_pipeline_on_real_data_never_leaks_future_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2017_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step7_sustainable.py::test_sustainable_pipeline_on_real_data_never_leaks_future_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2017_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step7_sustainable.py::test_sustainable_pipeline_on_real_data_never_leaks_future_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2018_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step7_sustainable.py::test_sustainable_pipeline_on_real_data_never_leaks_future_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2018_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step7_sustainable.py::test_sustainable_pipeline_on_real_data_never_leaks_future_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:133: PerformanceWarning: DataFrame is highly fragmented.  This is usually the result of calling `frame.insert` many times, which has poor performance.  Consider joining all columns at once using pd.concat(axis=1) instead. To get a de-fragmented frame, use `newframe = frame.copy()`
    return df.assign(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=================================== PASSES ====================================
=========================== short test summary info ===========================
PASSED tests/test_step7_sustainable.py::test_retraining_trajectory_never_includes_the_current_or_future_test_year
PASSED tests/test_step7_sustainable.py::test_retraining_trajectory_processes_years_chronologically_regardless_of_input_order
PASSED tests/test_step7_sustainable.py::test_retraining_trajectory_raises_on_year_missing_from_year_data
PASSED tests/test_step7_sustainable.py::test_retraining_trajectory_each_round_uses_a_freshly_built_classifier
PASSED tests/test_step7_sustainable.py::test_retraining_trajectory_labels_grow_to_include_previously_scored_years
PASSED tests/test_step7_sustainable.py::test_retraining_trajectory_fits_a_distinct_scaler_each_round
PASSED tests/test_step7_sustainable.py::test_static_model_trajectory_never_calls_fit_on_the_model_or_scaler
PASSED tests/test_step7_sustainable.py::test_static_model_trajectory_uses_the_same_fitted_parameters_across_every_year
PASSED tests/test_step7_sustainable.py::test_compare_static_vs_retrained_aligns_every_year_and_classifier_without_dropping_or_duplicating
PASSED tests/test_step7_sustainable.py::test_compare_static_vs_retrained_raises_when_year_classifier_pairs_differ
PASSED tests/test_step7_sustainable.py::test_run_sustainability_comparison_includes_both_classifiers
PASSED tests/test_step7_sustainable.py::test_run_sustainability_comparison_raises_when_factories_and_models_disagree
PASSED tests/test_step7_sustainable.py::test_sustainable_pipeline_on_real_data_never_leaks_future_years
====================== 13 passed, 11 warnings in 15.65s =======================
```

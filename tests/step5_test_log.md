# Step 5 Test Log: Evaluate Classifier Performance

- Tester transcript: transcripts/26_2026-10-29_tester_step5.md

## Tests written (tester)

One row per test function.

| Test | What it checks (from the assignment or plan) |
| --- | --- |
| test_evaluate_classifier_matches_sklearn_hand_checked_example | Metrics match sklearn's own accuracy/precision/recall/f1 functions, and hand-computed values, on a small example with every TP/FP/FN/TN nonzero |
| test_evaluate_classifier_matches_sklearn_for_always_benign_dummy | A dummy always predicting benign (0) scores 0 precision/recall/f1 and the correct accuracy, matching sklearn |
| test_evaluate_classifier_matches_sklearn_for_perfect_predictions | A classifier with perfect predictions scores 1.0 on every metric |
| test_evaluate_classifier_uses_malware_as_positive_class | Precision/recall/F1 treat label 1 (malware) as the positive class, not label 0, per AGENTS.md |
| test_evaluate_classifier_returns_required_metric_keys | Result has exactly accuracy/precision/recall/f1, each in [0, 1] |
| test_evaluate_classifier_never_calls_fit | Evaluation only calls .predict(); it never fits the model on the data being scored |
| test_evaluate_classifier_scores_the_exact_data_passed_in | Metrics reflect whichever X_test/y_test is actually passed, not a cached or default split |
| test_evaluate_classifier_distinguishes_held_out_set_from_training_set | A model fit on easy training data is scored on a harder held-out set, confirming evaluation uses the held-out split and not training-set performance |
| test_evaluate_all_returns_one_row_per_classifier | evaluate_all produces exactly one row per input classifier |
| test_evaluate_all_includes_all_four_metric_columns | evaluate_all's output has the classifier column plus all four metric columns |
| test_evaluate_all_rows_match_individual_evaluate_classifier_calls | Each row of evaluate_all matches a direct evaluate_classifier call for that model |
| test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years | End-to-end on the real dataset (skipped if input_data/ is empty): train/test years are disjoint, evaluate_all's metrics match sklearn computed directly on the held-out predictions, and the test/train row counts match the test_years/train_years split exactly |

## Failures and decisions (student)

One row per failing test. Decision is "Accepted" (the test is right; the builder fixes the code) or "Rejected" (the test is wrong; the tester fixes the test). Add the commit with the fix.

| Test | Cause | Decision | Fixed in commit |
| --- | --- | --- | --- |

## Runs (added by `python harness.py test N`; do not edit)

### Run 1: PASSED

- Time: 2026-10-29T14:46:15-05:00
- Commit: add2fd4
- Result: 12 passed, 11 warnings in 6.51s
- Files: test_step5_evaluation.py

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.7.0 -- C:\Users\logan\Documents\IT348\Project 2\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\logan\Documents\IT348\Project 2
configfile: pytest.ini
collecting ... collected 12 items

tests/test_step5_evaluation.py::test_evaluate_classifier_matches_sklearn_hand_checked_example PASSED [  8%]
tests/test_step5_evaluation.py::test_evaluate_classifier_matches_sklearn_for_always_benign_dummy PASSED [ 16%]
tests/test_step5_evaluation.py::test_evaluate_classifier_matches_sklearn_for_perfect_predictions PASSED [ 25%]
tests/test_step5_evaluation.py::test_evaluate_classifier_uses_malware_as_positive_class PASSED [ 33%]
tests/test_step5_evaluation.py::test_evaluate_classifier_returns_required_metric_keys PASSED [ 41%]
tests/test_step5_evaluation.py::test_evaluate_classifier_never_calls_fit PASSED [ 50%]
tests/test_step5_evaluation.py::test_evaluate_classifier_scores_the_exact_data_passed_in PASSED [ 58%]
tests/test_step5_evaluation.py::test_evaluate_classifier_distinguishes_held_out_set_from_training_set PASSED [ 66%]
tests/test_step5_evaluation.py::test_evaluate_all_returns_one_row_per_classifier PASSED [ 75%]
tests/test_step5_evaluation.py::test_evaluate_all_includes_all_four_metric_columns PASSED [ 83%]
tests/test_step5_evaluation.py::test_evaluate_all_rows_match_individual_evaluate_classifier_calls PASSED [ 91%]
tests/test_step5_evaluation.py::test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years PASSED [100%]

============================== warnings summary ===============================
tests/test_step5_evaluation.py::test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2014_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step5_evaluation.py::test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2014_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step5_evaluation.py::test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2015_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step5_evaluation.py::test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2015_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step5_evaluation.py::test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2016_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step5_evaluation.py::test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2016_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step5_evaluation.py::test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2017_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step5_evaluation.py::test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2017_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step5_evaluation.py::test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2018_benign_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step5_evaluation.py::test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:164: UserWarning: sampled_2018_malware_api.csv: expected raw shape (1500, 1849), got (9000, 1849)
    frames.append(load_single_file(file_path))

tests/test_step5_evaluation.py::test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years
  C:\Users\logan\Documents\IT348\Project 2\src\data_loader.py:133: PerformanceWarning: DataFrame is highly fragmented.  This is usually the result of calling `frame.insert` many times, which has poor performance.  Consider joining all columns at once using pd.concat(axis=1) instead. To get a de-fragmented frame, use `newframe = frame.copy()`
    return df.assign(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=================================== PASSES ====================================
=========================== short test summary info ===========================
PASSED tests/test_step5_evaluation.py::test_evaluate_classifier_matches_sklearn_hand_checked_example
PASSED tests/test_step5_evaluation.py::test_evaluate_classifier_matches_sklearn_for_always_benign_dummy
PASSED tests/test_step5_evaluation.py::test_evaluate_classifier_matches_sklearn_for_perfect_predictions
PASSED tests/test_step5_evaluation.py::test_evaluate_classifier_uses_malware_as_positive_class
PASSED tests/test_step5_evaluation.py::test_evaluate_classifier_returns_required_metric_keys
PASSED tests/test_step5_evaluation.py::test_evaluate_classifier_never_calls_fit
PASSED tests/test_step5_evaluation.py::test_evaluate_classifier_scores_the_exact_data_passed_in
PASSED tests/test_step5_evaluation.py::test_evaluate_classifier_distinguishes_held_out_set_from_training_set
PASSED tests/test_step5_evaluation.py::test_evaluate_all_returns_one_row_per_classifier
PASSED tests/test_step5_evaluation.py::test_evaluate_all_includes_all_four_metric_columns
PASSED tests/test_step5_evaluation.py::test_evaluate_all_rows_match_individual_evaluate_classifier_calls
PASSED tests/test_step5_evaluation.py::test_evaluate_all_on_real_pipeline_uses_only_held_out_test_years
======================= 12 passed, 11 warnings in 6.51s =======================
```

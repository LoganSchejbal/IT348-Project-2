# Step 7 Test Log: Post Step 7 -- Project Adjustments (console driver)

- Tester transcript: transcripts/41_2026-11-01_tester_step7.md

## Tests written (tester)

One row per test function.

| Test | What it checks (from the assignment or plan) |
| --- | --- |
| test_parse_args_rejects_unknown_step | `--step` outside the fixed choice set must error (argparse `SystemExit`), per PLAN.md's Post Step 7 Testing bullet. |
| test_parse_args_accepts_every_documented_step_choice | Every step name PLAN.md documents (`all`, `load`, `drift`, `preprocess`, `train`, `evaluate`, `evaluate-by-year`, `sustainable`) is a valid `--step` value. |
| test_parse_args_defaults_to_all_and_input_data | With no arguments, `--step` defaults to `"all"` and `--data-dir` defaults to `"input_data"`, matching AGENTS.md's documented run command. |
| test_build_arg_parser_step_choices_match_step_choices_constant | The parser's `--step` choices are exactly `cli.STEP_CHOICES`, so the two can't silently drift apart. |
| test_ensure_data_loaded_raises_for_nonexistent_data_dir | `ensure_data_loaded` raises `FileNotFoundError` (mentioning `--data-dir`) for a `data_dir` that does not exist, per PLAN.md. |
| test_ensure_data_loaded_raises_for_empty_data_dir | `ensure_data_loaded` raises `FileNotFoundError` for a `data_dir` that exists but has no `sampled_*_api.csv` files. |
| test_ensure_data_loaded_never_calls_load_all_years_for_empty_dir | For an empty `data_dir`, `load_all_years` must never even be called, not just that an exception eventually surfaces. |
| test_ensure_data_loaded_is_a_noop_once_year_data_is_set | `ensure_data_loaded` does not recompute `year_data` once it is already set (no-op prerequisite pattern from PLAN.md). |
| test_ensure_preprocessed_is_a_noop_once_x_train_is_set | `ensure_preprocessed` does not recompute `X_train` once it is already set. |
| test_ensure_trained_is_a_noop_once_classifiers_are_set | `ensure_trained` does not recompute `classifiers` once it is already set. |
| test_ensure_preprocessed_does_not_reload_already_loaded_data | Once `year_data` is loaded, calling `ensure_preprocessed` must not trigger another full `load_all_years` reload. |
| test_run_step1_load_returns_a_single_dataframe | `run_step1_load` returns a single `pd.DataFrame` summarizing every loaded year, per PLAN.md. |
| test_run_step3_preprocess_returns_a_single_dataframe | `run_step3_preprocess` returns a single `pd.DataFrame` with one row for "train" and one for "test". |
| test_run_step4_train_returns_a_single_dataframe | `run_step4_train` returns a single `pd.DataFrame` with one row per trained classifier. |
| test_run_selected_step_all_populates_context_exactly_once | `run_selected_step(context, "all")` computes `load_all_years`/`prepare_train_test`/`train_classifiers` exactly once each, even though multiple steps depend on them, per PLAN.md. |
| test_run_selected_step_single_step_only_runs_that_step | Requesting a single `--step` only prints that step's section header, not every step's. |
| test_main_with_no_arguments_runs_full_pipeline | `main([])` runs the full seven-step pipeline with no arguments, matching AGENTS.md's documented `python -m src.main`. |
| test_main_with_explicit_step_runs_only_that_step | `main()` correctly threads an explicit `--step`/`--data-dir` combination through to `run_selected_step`. |
| test_full_pipeline_on_real_dataset | Integration smoke test: the full driver runs end-to-end on the real dataset (when present) with all metrics in `[0, 1]`. Skipped when `input_data/` is empty. |

## Failures and decisions (student)

One row per failing test. Decision is "Accepted" (the test is right; the builder fixes the code) or "Rejected" (the test is wrong; the tester fixes the test). Add the commit with the fix.

| Test | Cause | Decision | Fixed in commit |
| --- | --- | --- | --- |
| 1 | Error in test | Rejected | Commit |

## Runs (added by `python harness.py test N`; do not edit)

### Run 1: FAILED

- Time: 2026-11-01T17:20:54-06:00
- Commit: ef5d1d8
- Result: 1 failed, 31 passed, 79 warnings in 67.17s (0:01:07)
- Files: test_step7_driver.py, test_step7_sustainable.py

```
... (268 earlier lines omitted)
 year          classifier  accuracy  precision  recall     f1
 2016 logistic_regression     0.625     0.6000    0.75 0.6667
 2016       random_forest     0.625     0.6667    0.50 0.5714
 2017 logistic_regression     0.625     0.6000    0.75 0.6667
 2017       random_forest     0.625     0.6667    0.50 0.5714

=== sustainable ===
 year          classifier  accuracy_static  precision_static  recall_static  f1_static  accuracy_retrained  precision_retrained  recall_retrained  f1_retrained
 2016 logistic_regression            0.625            0.6000           0.75     0.6667               0.625               0.6000              0.75        0.6667
 2017 logistic_regression            0.625            0.6000           0.75     0.6667               0.625               0.6000              0.75        0.6667
 2016       random_forest            0.625            0.6667           0.50     0.5714               0.625               0.6667              0.50        0.5714
 2017       random_forest            0.625            0.6667           0.50     0.5714               0.625               0.6667              0.50        0.5714

_____________________ test_full_pipeline_on_real_dataset ______________________
---------------------------- Captured stdout call -----------------------------
=== load ===
 year  rows  n_features  n_malware  n_benign
 2014  3000        1848       1500      1500
 2015  3000        1848       1500      1500
 2016  3000        1848       1500      1500
 2017  3000        1848       1500      1500
 2018  3000        1848       1500      1500
 2019  3000        1848       1500      1500
 2020  3000        1848       1500      1500
 2021  3000        1848       1500      1500

=== drift ===
 year_a  year_b                                                                                                                                                                                       feature  statistic  p_value
   2020    2021                                    Landroid/content/ContentResolver;.openFileDescriptor:(Landroid/net/Uri;Ljava/lang/String;Landroid/os/CancellationSignal;)Landroid/os/ParcelFileDescriptor;     0.3563      0.0
   2018    2019                                Landroid/content/ContentResolver;.query:(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;     0.3520      0.0
   2018    2019 Landroid/content/ContentResolver;.query:(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;Landroid/os/CancellationSignal;)Landroid/database/Cursor;     0.3370      0.0
   2019    2020                                                                                                                                             Ljava/lang/String;.valueOf:([C)Ljava/lang/String;     0.3170      0.0
   2020    2021                                                                                                                                          Ljava/lang/System;.loadLibrary:(Ljava/lang/String;)V     0.3153      0.0
   2015    2016                                                                                                                                                                Landroid/os/Process;.myPid:()I     0.2897      0.0
   2020    2021                                                                                                        Ljava/lang/StringBuilder;.append:(Ljava/lang/CharSequence;II)Ljava/lang/StringBuilder;     0.2890      0.0
   2019    2020                                                                                                                                          Ljava/lang/System;.loadLibrary:(Ljava/lang/String;)V     0.2753      0.0
   2020    2021                                                                                                                             Ljava/net/URLConnection;.getOutputStream:()Ljava/io/OutputStream;     0.2717      0.0
   2015    2016                                                                                                                Landroid/os/Handler;.obtainMessage:(IIILjava/lang/Object;)Landroid/os/Message;     0.2710      0.0
   2017    2018                                                                                                                                    Landroid/webkit/WebView;.draw:(Landroid/graphics/Canvas;)V     0.2703      0.0
   2020    2021                                                                                                                                             Ljava/lang/String;.indexOf:(Ljava/lang/String;I)I     0.2693      0.0
   2020    2021                                                                                                                                                Landroid/os/PowerManager$WakeLock;.release:()V     0.2690      0.0
   2017    2018                                                                                                                                                        Landroid/webkit/WebView;.measure:(II)V     0.2670      0.0
   2015    2016                                                                                                                                  Landroid/os/Handler;.obtainMessage:(III)Landroid/os/Message;     0.2650      0.0
   2020    2021                                                                                                          Ljava/lang/StringBuilder;.append:(Ljava/lang/CharSequence;)Ljava/lang/StringBuilder;     0.2640      0.0
   2014    2015                                                                                               Landroid/webkit/WebView;.evaluateJavascript:(Ljava/lang/String;Landroid/webkit/ValueCallback;)V     0.2627      0.0
   2020    2021                                                                                                 Ljavax/crypto/Cipher;.getInstance:(Ljava/lang/String;Ljava/lang/String;)Ljavax/crypto/Cipher;     0.2617      0.0
   2017    2018                                                                                                                                                       Landroid/webkit/WebView;.invalidate:()V     0.2613      0.0
   2017    2018                                                                                                                                                       Landroid/webkit/WebView;.layout:(IIII)V     0.2603      0.0

=== preprocess ===
split                  years         shape
train 2014, 2015, 2016, 2017 (12000, 1848)
 test 2018, 2019, 2020, 2021 (12000, 1848)

=== train ===
         classifier                                                                                                                                                                                                                                                                                                                                                                                                                      params
logistic_regression                                                                                                                                                         {'C': 1.0, 'class_weight': None, 'dual': False, 'fit_intercept': True, 'intercept_scaling': 1, 'l1_ratio': 0.0, 'max_iter': 1000, 'n_jobs': None, 'penalty': 'deprecated', 'random_state': 42, 'solver': 'lbfgs', 'tol': 0.0001, 'verbose': 0, 'warm_start': False}
      random_forest {'bootstrap': True, 'ccp_alpha': 0.0, 'class_weight': None, 'criterion': 'gini', 'max_depth': None, 'max_features': 'sqrt', 'max_leaf_nodes': None, 'max_samples': None, 'min_impurity_decrease': 0.0, 'min_samples_leaf': 1, 'min_samples_split': 2, 'min_weight_fraction_leaf': 0.0, 'monotonic_cst': None, 'n_estimators': 100, 'n_jobs': -1, 'oob_score': False, 'random_state': 42, 'verbose': 0, 'warm_start': False}

=== evaluate ===
         classifier  accuracy  precision  recall     f1
logistic_regression    0.6166     0.5762  0.8812 0.6968
      random_forest    0.6602     0.5971  0.9857 0.7437

=== evaluate-by-year ===
 year          classifier  accuracy  precision  recall     f1
 2018 logistic_regression    0.9547     0.9355  0.9767 0.9556
 2018       random_forest    0.9567     0.9408  0.9747 0.9574
 2019 logistic_regression    0.5730     0.5398  0.9900 0.6987
 2019       random_forest    0.5807     0.5442  0.9927 0.7030
 2020 logistic_regression    0.5477     0.5261  0.9613 0.6800
 2020       random_forest    0.5540     0.5286  0.9973 0.6910
 2021 logistic_regression    0.3910     0.4228  0.5967 0.4949
 2021       random_forest    0.5497     0.5268  0.9780 0.6847

=== sustainable ===
 year          classifier  accuracy_static  precision_static  recall_static  f1_static  accuracy_retrained  precision_retrained  recall_retrained  f1_retrained
 2018 logistic_regression           0.9547            0.9355         0.9767     0.9556              0.9547               0.9355            0.9767        0.9556
 2019 logistic_regression           0.5730            0.5398         0.9900     0.6987              0.5743               0.5405            0.9927        0.6999
 2020 logistic_regression           0.5477            0.5261         0.9613     0.6800              0.9120               0.9093            0.9153        0.9123
 2021 logistic_regression           0.3910            0.4228         0.5967     0.4949              0.9067               0.9111            0.9013        0.9062
 2018       random_forest           0.9567            0.9408         0.9747     0.9574              0.9567               0.9408            0.9747        0.9574
 2019       random_forest           0.5807            0.5442         0.9927     0.7030              0.5747               0.5409            0.9867        0.6988
 2020       random_forest           0.5540            0.5286         0.9973     0.6910              0.9413               0.9636            0.9173        0.9399
 2021       random_forest           0.5497            0.5268         0.9780     0.6847              0.9443               0.9912            0.8967        0.9415

=========================== short test summary info ===========================
PASSED tests/test_step7_driver.py::test_parse_args_rejects_unknown_step
PASSED tests/test_step7_driver.py::test_parse_args_accepts_every_documented_step_choice
PASSED tests/test_step7_driver.py::test_parse_args_defaults_to_all_and_input_data
PASSED tests/test_step7_driver.py::test_build_arg_parser_step_choices_match_step_choices_constant
PASSED tests/test_step7_driver.py::test_ensure_data_loaded_raises_for_nonexistent_data_dir
PASSED tests/test_step7_driver.py::test_ensure_data_loaded_raises_for_empty_data_dir
PASSED tests/test_step7_driver.py::test_ensure_data_loaded_never_calls_load_all_years_for_empty_dir
PASSED tests/test_step7_driver.py::test_ensure_data_loaded_is_a_noop_once_year_data_is_set
PASSED tests/test_step7_driver.py::test_ensure_preprocessed_is_a_noop_once_x_train_is_set
PASSED tests/test_step7_driver.py::test_ensure_trained_is_a_noop_once_classifiers_are_set
PASSED tests/test_step7_driver.py::test_ensure_preprocessed_does_not_reload_already_loaded_data
PASSED tests/test_step7_driver.py::test_run_step1_load_returns_a_single_dataframe
PASSED tests/test_step7_driver.py::test_run_step3_preprocess_returns_a_single_dataframe
PASSED tests/test_step7_driver.py::test_run_step4_train_returns_a_single_dataframe
PASSED tests/test_step7_driver.py::test_run_selected_step_all_populates_context_exactly_once
PASSED tests/test_step7_driver.py::test_run_selected_step_single_step_only_runs_that_step
PASSED tests/test_step7_driver.py::test_main_with_no_arguments_runs_full_pipeline
PASSED tests/test_step7_driver.py::test_full_pipeline_on_real_dataset
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
FAILED tests/test_step7_driver.py::test_main_with_explicit_step_runs_only_that_step
============ 1 failed, 31 passed, 79 warnings in 67.17s (0:01:07) =============
```

### Run 2: PASSED

- Time: 2026-11-01T17:37:37-06:00
- Commit: aa04ece
- Result: 32 passed, 87 warnings in 58.28s
- Files: test_step7_driver.py, test_step7_sustainable.py

```
... (232 earlier lines omitted)
 year          classifier  accuracy  precision  recall     f1
 2016 logistic_regression     0.625     0.6000    0.75 0.6667
 2016       random_forest     0.625     0.6667    0.50 0.5714
 2017 logistic_regression     0.625     0.6000    0.75 0.6667
 2017       random_forest     0.625     0.6667    0.50 0.5714

=== sustainable ===
 year          classifier  accuracy_static  precision_static  recall_static  f1_static  accuracy_retrained  precision_retrained  recall_retrained  f1_retrained
 2016 logistic_regression            0.625            0.6000           0.75     0.6667               0.625               0.6000              0.75        0.6667
 2017 logistic_regression            0.625            0.6000           0.75     0.6667               0.625               0.6000              0.75        0.6667
 2016       random_forest            0.625            0.6667           0.50     0.5714               0.625               0.6667              0.50        0.5714
 2017       random_forest            0.625            0.6667           0.50     0.5714               0.625               0.6667              0.50        0.5714

_____________________ test_full_pipeline_on_real_dataset ______________________
---------------------------- Captured stdout call -----------------------------
=== load ===
 year  rows  n_features  n_malware  n_benign
 2014  3000        1848       1500      1500
 2015  3000        1848       1500      1500
 2016  3000        1848       1500      1500
 2017  3000        1848       1500      1500
 2018  3000        1848       1500      1500
 2019  3000        1848       1500      1500
 2020  3000        1848       1500      1500
 2021  3000        1848       1500      1500

=== drift ===
 year_a  year_b                                                                                                                                                                                       feature  statistic  p_value
   2020    2021                                    Landroid/content/ContentResolver;.openFileDescriptor:(Landroid/net/Uri;Ljava/lang/String;Landroid/os/CancellationSignal;)Landroid/os/ParcelFileDescriptor;     0.3563      0.0
   2018    2019                                Landroid/content/ContentResolver;.query:(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;     0.3520      0.0
   2018    2019 Landroid/content/ContentResolver;.query:(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;Landroid/os/CancellationSignal;)Landroid/database/Cursor;     0.3370      0.0
   2019    2020                                                                                                                                             Ljava/lang/String;.valueOf:([C)Ljava/lang/String;     0.3170      0.0
   2020    2021                                                                                                                                          Ljava/lang/System;.loadLibrary:(Ljava/lang/String;)V     0.3153      0.0
   2015    2016                                                                                                                                                                Landroid/os/Process;.myPid:()I     0.2897      0.0
   2020    2021                                                                                                        Ljava/lang/StringBuilder;.append:(Ljava/lang/CharSequence;II)Ljava/lang/StringBuilder;     0.2890      0.0
   2019    2020                                                                                                                                          Ljava/lang/System;.loadLibrary:(Ljava/lang/String;)V     0.2753      0.0
   2020    2021                                                                                                                             Ljava/net/URLConnection;.getOutputStream:()Ljava/io/OutputStream;     0.2717      0.0
   2015    2016                                                                                                                Landroid/os/Handler;.obtainMessage:(IIILjava/lang/Object;)Landroid/os/Message;     0.2710      0.0
   2017    2018                                                                                                                                    Landroid/webkit/WebView;.draw:(Landroid/graphics/Canvas;)V     0.2703      0.0
   2020    2021                                                                                                                                             Ljava/lang/String;.indexOf:(Ljava/lang/String;I)I     0.2693      0.0
   2020    2021                                                                                                                                                Landroid/os/PowerManager$WakeLock;.release:()V     0.2690      0.0
   2017    2018                                                                                                                                                        Landroid/webkit/WebView;.measure:(II)V     0.2670      0.0
   2015    2016                                                                                                                                  Landroid/os/Handler;.obtainMessage:(III)Landroid/os/Message;     0.2650      0.0
   2020    2021                                                                                                          Ljava/lang/StringBuilder;.append:(Ljava/lang/CharSequence;)Ljava/lang/StringBuilder;     0.2640      0.0
   2014    2015                                                                                               Landroid/webkit/WebView;.evaluateJavascript:(Ljava/lang/String;Landroid/webkit/ValueCallback;)V     0.2627      0.0
   2020    2021                                                                                                 Ljavax/crypto/Cipher;.getInstance:(Ljava/lang/String;Ljava/lang/String;)Ljavax/crypto/Cipher;     0.2617      0.0
   2017    2018                                                                                                                                                       Landroid/webkit/WebView;.invalidate:()V     0.2613      0.0
   2017    2018                                                                                                                                                       Landroid/webkit/WebView;.layout:(IIII)V     0.2603      0.0

=== preprocess ===
split                  years         shape
train 2014, 2015, 2016, 2017 (12000, 1848)
 test 2018, 2019, 2020, 2021 (12000, 1848)

=== train ===
         classifier                                                                                                                                                                                                                                                                                                                                                                                                                      params
logistic_regression                                                                                                                                                         {'C': 1.0, 'class_weight': None, 'dual': False, 'fit_intercept': True, 'intercept_scaling': 1, 'l1_ratio': 0.0, 'max_iter': 1000, 'n_jobs': None, 'penalty': 'deprecated', 'random_state': 42, 'solver': 'lbfgs', 'tol': 0.0001, 'verbose': 0, 'warm_start': False}
      random_forest {'bootstrap': True, 'ccp_alpha': 0.0, 'class_weight': None, 'criterion': 'gini', 'max_depth': None, 'max_features': 'sqrt', 'max_leaf_nodes': None, 'max_samples': None, 'min_impurity_decrease': 0.0, 'min_samples_leaf': 1, 'min_samples_split': 2, 'min_weight_fraction_leaf': 0.0, 'monotonic_cst': None, 'n_estimators': 100, 'n_jobs': -1, 'oob_score': False, 'random_state': 42, 'verbose': 0, 'warm_start': False}

=== evaluate ===
         classifier  accuracy  precision  recall     f1
logistic_regression    0.6166     0.5762  0.8812 0.6968
      random_forest    0.6602     0.5971  0.9857 0.7437

=== evaluate-by-year ===
 year          classifier  accuracy  precision  recall     f1
 2018 logistic_regression    0.9547     0.9355  0.9767 0.9556
 2018       random_forest    0.9567     0.9408  0.9747 0.9574
 2019 logistic_regression    0.5730     0.5398  0.9900 0.6987
 2019       random_forest    0.5807     0.5442  0.9927 0.7030
 2020 logistic_regression    0.5477     0.5261  0.9613 0.6800
 2020       random_forest    0.5540     0.5286  0.9973 0.6910
 2021 logistic_regression    0.3910     0.4228  0.5967 0.4949
 2021       random_forest    0.5497     0.5268  0.9780 0.6847

=== sustainable ===
 year          classifier  accuracy_static  precision_static  recall_static  f1_static  accuracy_retrained  precision_retrained  recall_retrained  f1_retrained
 2018 logistic_regression           0.9547            0.9355         0.9767     0.9556              0.9547               0.9355            0.9767        0.9556
 2019 logistic_regression           0.5730            0.5398         0.9900     0.6987              0.5743               0.5405            0.9927        0.6999
 2020 logistic_regression           0.5477            0.5261         0.9613     0.6800              0.9120               0.9093            0.9153        0.9123
 2021 logistic_regression           0.3910            0.4228         0.5967     0.4949              0.9067               0.9111            0.9013        0.9062
 2018       random_forest           0.9567            0.9408         0.9747     0.9574              0.9567               0.9408            0.9747        0.9574
 2019       random_forest           0.5807            0.5442         0.9927     0.7030              0.5747               0.5409            0.9867        0.6988
 2020       random_forest           0.5540            0.5286         0.9973     0.6910              0.9413               0.9636            0.9173        0.9399
 2021       random_forest           0.5497            0.5268         0.9780     0.6847              0.9443               0.9912            0.8967        0.9415

=========================== short test summary info ===========================
PASSED tests/test_step7_driver.py::test_parse_args_rejects_unknown_step
PASSED tests/test_step7_driver.py::test_parse_args_accepts_every_documented_step_choice
PASSED tests/test_step7_driver.py::test_parse_args_defaults_to_all_and_input_data
PASSED tests/test_step7_driver.py::test_build_arg_parser_step_choices_match_step_choices_constant
PASSED tests/test_step7_driver.py::test_ensure_data_loaded_raises_for_nonexistent_data_dir
PASSED tests/test_step7_driver.py::test_ensure_data_loaded_raises_for_empty_data_dir
PASSED tests/test_step7_driver.py::test_ensure_data_loaded_never_calls_load_all_years_for_empty_dir
PASSED tests/test_step7_driver.py::test_ensure_data_loaded_is_a_noop_once_year_data_is_set
PASSED tests/test_step7_driver.py::test_ensure_preprocessed_is_a_noop_once_x_train_is_set
PASSED tests/test_step7_driver.py::test_ensure_trained_is_a_noop_once_classifiers_are_set
PASSED tests/test_step7_driver.py::test_ensure_preprocessed_does_not_reload_already_loaded_data
PASSED tests/test_step7_driver.py::test_run_step1_load_returns_a_single_dataframe
PASSED tests/test_step7_driver.py::test_run_step3_preprocess_returns_a_single_dataframe
PASSED tests/test_step7_driver.py::test_run_step4_train_returns_a_single_dataframe
PASSED tests/test_step7_driver.py::test_run_selected_step_all_populates_context_exactly_once
PASSED tests/test_step7_driver.py::test_run_selected_step_single_step_only_runs_that_step
PASSED tests/test_step7_driver.py::test_main_with_no_arguments_runs_full_pipeline
PASSED tests/test_step7_driver.py::test_main_with_explicit_step_runs_only_that_step
PASSED tests/test_step7_driver.py::test_full_pipeline_on_real_dataset
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
====================== 32 passed, 87 warnings in 58.28s =======================
```

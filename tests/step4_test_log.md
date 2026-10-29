# Step 4 Test Log: Apply Machine Learning Classifiers

- Tester transcript: transcripts/22_2026-10-29_tester_step4.md

## Tests written (tester)

One row per test function.

| Test | What it checks (from the assignment or plan) |
| --- | --- |
| test_get_classifier_factories_returns_at_least_two | At least two classifiers are implemented, per the assignment |
| test_get_classifier_factories_values_are_callable | Every factory entry is callable (a zero-argument factory, not an instance) |
| test_get_classifier_factories_produce_distinct_classifier_types | The classifiers are genuinely different types, not duplicates |
| test_get_classifier_factories_each_call_returns_unfitted_estimator | Each factory call returns a fresh, unfitted estimator (no classes_ yet) |
| test_get_classifier_factories_repeated_calls_give_equal_but_distinct_objects | Two calls to the same factory give equal-config but separate (non-identical) instances |
| test_get_classifier_factories_use_requested_random_state | Classifiers built from the factories honor the given random_state |
| test_get_classifiers_returns_at_least_two_distinct_types | get_classifiers builds at least two distinct, unfitted classifier types |
| test_get_classifiers_use_random_state_42_by_default | Classifiers default to random_state=42, per PLAN.md |
| test_train_classifiers_returns_fitted_estimators | After training, every classifier exposes classes_ (i.e., is fitted) |
| test_each_classifier_fits_and_predicts_on_synthetic_data | Each classifier fits and predicts one label per row on a small synthetic dataset |
| test_each_classifier_learns_the_synthetic_signal | Each classifier does meaningfully better than chance on learnable synthetic data |
| test_predictions_use_only_the_two_class_labels | Predicted labels are a subset of {0, 1} (benign=0/malware=1) |
| test_classifier_classes_attribute_matches_two_labels | The fitted classes_ attribute is exactly {0, 1} after training on both classes |
| test_same_random_state_gives_identical_predictions_across_runs | Two independently-trained runs with the same random_state predict identically |
| test_same_random_state_gives_identical_fitted_parameters | Two logistic regression runs with the same random_state fit identical coefficients |
| test_different_random_state_is_accepted_without_error | Factories accept an arbitrary random_state without raising |

## Failures and decisions (student)

One row per failing test. Decision is "Accepted" (the test is right; the builder fixes the code) or "Rejected" (the test is wrong; the tester fixes the test). Add the commit with the fix.

| Test | Cause | Decision | Fixed in commit |
| --- | --- | --- | --- |

## Runs (added by `python harness.py test N`; do not edit)

### Run 1: PASSED

- Time: 2026-10-29T14:26:23-05:00
- Commit: b771e8b
- Result: 16 passed in 21.12s
- Files: test_step4_models.py

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.7.0 -- C:\Users\logan\Documents\IT348\Project 2\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\logan\Documents\IT348\Project 2
configfile: pytest.ini
collecting ... collected 16 items

tests/test_step4_models.py::test_get_classifier_factories_returns_at_least_two PASSED [  6%]
tests/test_step4_models.py::test_get_classifier_factories_values_are_callable PASSED [ 12%]
tests/test_step4_models.py::test_get_classifier_factories_produce_distinct_classifier_types PASSED [ 18%]
tests/test_step4_models.py::test_get_classifier_factories_each_call_returns_unfitted_estimator PASSED [ 25%]
tests/test_step4_models.py::test_get_classifier_factories_repeated_calls_give_equal_but_distinct_objects PASSED [ 31%]
tests/test_step4_models.py::test_get_classifier_factories_use_requested_random_state PASSED [ 37%]
tests/test_step4_models.py::test_get_classifiers_returns_at_least_two_distinct_types PASSED [ 43%]
tests/test_step4_models.py::test_get_classifiers_use_random_state_42_by_default PASSED [ 50%]
tests/test_step4_models.py::test_train_classifiers_returns_fitted_estimators PASSED [ 56%]
tests/test_step4_models.py::test_each_classifier_fits_and_predicts_on_synthetic_data PASSED [ 62%]
tests/test_step4_models.py::test_each_classifier_learns_the_synthetic_signal PASSED [ 68%]
tests/test_step4_models.py::test_predictions_use_only_the_two_class_labels PASSED [ 75%]
tests/test_step4_models.py::test_classifier_classes_attribute_matches_two_labels PASSED [ 81%]
tests/test_step4_models.py::test_same_random_state_gives_identical_predictions_across_runs PASSED [ 87%]
tests/test_step4_models.py::test_same_random_state_gives_identical_fitted_parameters PASSED [ 93%]
tests/test_step4_models.py::test_different_random_state_is_accepted_without_error PASSED [100%]

=================================== PASSES ====================================
=========================== short test summary info ===========================
PASSED tests/test_step4_models.py::test_get_classifier_factories_returns_at_least_two
PASSED tests/test_step4_models.py::test_get_classifier_factories_values_are_callable
PASSED tests/test_step4_models.py::test_get_classifier_factories_produce_distinct_classifier_types
PASSED tests/test_step4_models.py::test_get_classifier_factories_each_call_returns_unfitted_estimator
PASSED tests/test_step4_models.py::test_get_classifier_factories_repeated_calls_give_equal_but_distinct_objects
PASSED tests/test_step4_models.py::test_get_classifier_factories_use_requested_random_state
PASSED tests/test_step4_models.py::test_get_classifiers_returns_at_least_two_distinct_types
PASSED tests/test_step4_models.py::test_get_classifiers_use_random_state_42_by_default
PASSED tests/test_step4_models.py::test_train_classifiers_returns_fitted_estimators
PASSED tests/test_step4_models.py::test_each_classifier_fits_and_predicts_on_synthetic_data
PASSED tests/test_step4_models.py::test_each_classifier_learns_the_synthetic_signal
PASSED tests/test_step4_models.py::test_predictions_use_only_the_two_class_labels
PASSED tests/test_step4_models.py::test_classifier_classes_attribute_matches_two_labels
PASSED tests/test_step4_models.py::test_same_random_state_gives_identical_predictions_across_runs
PASSED tests/test_step4_models.py::test_same_random_state_gives_identical_fitted_parameters
PASSED tests/test_step4_models.py::test_different_random_state_is_accepted_without_error
============================= 16 passed in 21.12s =============================
```

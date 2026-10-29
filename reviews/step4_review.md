# Step 4 Review: Apply Machine Learning Classifiers

- Reviewer transcript: transcripts/21_2026-10-29_reviewer_step4.md
- What was reviewed: the diff from step4-start to the latest commit (src/models.py, new file)

## Comments (reviewer)

One row per issue. Number the rows 1, 2, 3, ...

| # | Severity | Location | Issue | Suggested fix |
| --- | --- | --- | --- | --- |
| 1 | Low | `src/models.py`, `get_classifier_factories` (lines 48-57) | Neither classifier sets `class_weight`, and nothing in this file documents whether the training data is balanced. As built, this is correct — each `sampled_<year>_<class>_api.csv` pair contributes 1,500 benign + 1,500 malware rows, so any concatenation of full years stays 50/50 and `class_weight='balanced'` is unnecessary. But that fact lives in the dataset, not in this code, so the assumption is easy to silently break (e.g., if `main.py` or a later step ever subsets rows, or if `load_year_data` is changed to drop rows). | Add a one-line comment in `get_classifier_factories` noting that `class_weight` is intentionally left at default because the per-year class counts are balanced by construction (per AGENTS.md), and have `docs/step4_models.md` state this explicitly so it isn't missed. |
| 2 | Low | `src/models.py`, `get_classifier_factories`, `random_forest` factory (lines 53-56) | `RandomForestClassifier` doesn't set `n_jobs`, so it defaults to 1 (single-threaded) training 100 trees on 1,848 features. This isn't a correctness bug, but it's a significant avoidable slowdown on every call to `get_classifiers`/`train_classifiers`, and especially in Step 7's retraining loop where a fresh Random Forest is refit from scratch each round. | Set `n_jobs=-1` on the `RandomForestClassifier` factory; it doesn't change `random_state`-driven reproducibility of the fitted model. |

## Decision log (student)

One row per comment above, with the same number. Decision is Accepted or Rejected. For accepted comments, add the commit that fixed it.

| # | Decision | Reason | Fixed in commit |
| --- | --- | --- | --- |
| 1 | Accepted | Reasonable doc | 4291a5b |
| 2 | Accepted | More threads should be used | 4291a5b |
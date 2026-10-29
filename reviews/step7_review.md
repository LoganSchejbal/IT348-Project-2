# Step 7 Review: Sustainable ML Approach

- Reviewer transcript: transcripts/33_2026-10-29_reviewer_step7.md
- What was reviewed: the diff from step7-start to commit 003aa76 (`src/sustainable.py`), against AGENTS.md and PLAN.md's Step 7 section.

## Comments (reviewer)

One row per issue. Number the rows 1, 2, 3, ...

| # | Severity | Location | Issue | Suggested fix |
| --- | --- | --- | --- | --- |
| 1 | Medium | `src/sustainable.py`, `retraining_trajectory` (lines 112-119) | The function validates that every year in `train_years`/`test_years` exists in `year_data`, but never checks that `train_years` and `test_years` are disjoint. If a caller accidentally passes a year in both (e.g. a bug in how `train_years`/`test_years` are computed upstream), that year is already inside `current_years` on the very first round, so it is used to fit the first round's scaler/classifier *and* then "scored" on itself — silent leakage with no error raised. `evaluation.evaluate_by_year` has an analogous optional `train_years` parameter specifically added (per the Step 6 review) to catch this class of mistake, but `retraining_trajectory` has no equivalent guard. | Add a check such as `overlap = set(train_years) & set(ordered_test_years); if overlap: raise ValueError(...)`, mirroring the guard in `evaluate_by_year`. |
| 2 | Medium | `src/sustainable.py`, `static_model_trajectory` (line 67) | `static_model_trajectory` calls `evaluate_by_year(models, year_data, feature_cols, scaler, test_years)` without passing `train_years`, so the overlap-detection guard that was added to `evaluate_by_year` in Step 6 (in response to review comments #1/#2) is never exercised for the Step 7 baseline. Since Step 7 is specifically about leakage-sensitive comparisons, this is the one place in the codebase where that guard would be most useful, and it's unused. | Add a `train_years` parameter to `static_model_trajectory` (and thread it through from `run_sustainability_comparison`), and forward it to `evaluate_by_year(..., train_years=train_years)`. |
| 3 | Low | `src/sustainable.py`, `retraining_trajectory` line 114 vs. `static_model_trajectory`/`evaluate_by_year` | `retraining_trajectory` de-duplicates and sorts its years (`ordered_test_years = sorted(set(test_years))`), but `static_model_trajectory` (via `evaluate_by_year`) iterates `years` as given, with no sorting or de-duplication. If `test_years` ever contained a duplicate, `retrained_df` would have one row per year while `static_df` would have two — `compare_static_vs_retrained`'s key-set check uses `set(...)`, which wouldn't catch the duplication, but the later `pd.merge(..., validate="one_to_one")` would then raise on the duplicate key, with an error message that doesn't point at the real cause. Not currently triggered since `test_years` comes from `split_years_in_half` (always unique), but it's a latent inconsistency between the two trajectory builders. | Normalize `test_years` (sort + de-duplicate) once in `run_sustainability_comparison` before passing it to either `static_model_trajectory` or `retraining_trajectory`, so both paths see identical input. |
| 4 | Low | `src/sustainable.py`, `run_sustainability_comparison` (lines 240-248) | If `classifier_factories`/`models` are passed in as empty dicts, the name-set check at the top passes trivially (both empty sets are equal), and execution proceeds to `pd.concat(retrained_frames, ignore_index=True)` with an empty list, which raises pandas' generic `ValueError: No objects to concatenate` rather than a clear, project-specific error. | Add an explicit check (e.g. `if not classifier_factories: raise ValueError("classifier_factories must be non-empty")`) near the top of the function, consistent with how other Step 7 functions validate their inputs up front. |

## Decision log (student)

One row per comment above, with the same number. Decision is Accepted or Rejected. For accepted comments, add the commit that fixed it.

| # | Decision | Reason | Fixed in commit |
| --- | --- | --- | --- |
| 1 | Accepted | Needed safety mechanism | 2aff05f |
| 2 | Accepted | Should implement guard | 2aff05f |
| 3 | Accepted | Should be consistent | 2aff05f |
| 4 | Accepted | Should have a specific error, not generic | 2aff05f |
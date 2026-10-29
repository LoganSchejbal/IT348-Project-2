# Step 3 Review: Preprocess Data for Model Training

- Reviewer transcript: transcripts/17_2026-10-29_reviewer_step3.md
- What was reviewed: the diff from step3-start to commit 936b1e5 (src/preprocessing.py)

## Comments (reviewer)

| # | Severity | Location | Issue | Suggested fix |
| --- | --- | --- | --- | --- |
| 1 | Medium | `split_by_year` (src/preprocessing.py) | The function checks that every requested year exists in `year_data`, but never checks that `train_years` and `test_years` are disjoint. If a caller accidentally passes an overlapping year to both lists (e.g. a typo in a future step that builds `test_years`), that year's rows end up in both `train_df` and `test_df`, which is exactly the train/test leakage PLAN.md says must be prevented, and nothing in this code would catch it. | Add a check such as `overlap = set(train_years) & set(test_years)` and raise `ValueError` if non-empty, alongside the existing missing-year check. |
| 2 | Low | `fit_scaler` / `scale_features` (src/preprocessing.py) | Neither function validates that `feature_cols` is non-empty or that all of its entries are actual columns of `df`/`train_df`. A typo'd or empty `feature_cols` list (e.g. from a future change to `get_feature_columns`) would currently fail with a raw pandas `KeyError` or silently produce a `(n, 0)` array instead of a clear, attributable error. | Either document that this is intentionally left to pandas, or add an explicit check (e.g. `missing = set(feature_cols) - set(df.columns)`) with a clearer `ValueError` message, consistent with the explicit error handling already done in `split_by_year`. |
| 3 | Low | `prepare_train_test` (src/preprocessing.py) | The docstring for `prepare_train_test` doesn't mention what happens if `train_years` or `test_years` is empty (e.g. `split_years_in_half` could theoretically be bypassed and an empty list passed directly). `pd.concat([])` on an empty list raises a `ValueError` from pandas with a fairly opaque message. | Not blocking, but worth a one-line note in the docstring, or let `split_by_year`'s existing missing-year check also cover the empty-list case explicitly. |
| 4 | Low | Module docstring vs. `split_years_in_half` | The module docstring states Step 3's scope in terms of `prepare_train_test`/scaling only; it doesn't mention `split_years_in_half`, which is also defined in this file and is arguably the most leakage-sensitive function (it decides what counts as "training years" at all). This is just about discoverability, not correctness. | Minor: add one sentence to the module docstring noting that `split_years_in_half` here also determines the train/test year boundary used by Step 3-5. |

### What looked correct

- The scaler is fit only on `train_df` (`fit_scaler` calls `.fit()` once, on the training dataframe only); `scale_features` only ever calls `.transform()`, matching PLAN.md's requirement that nothing fitted touches test-year rows.
- `split_by_year` builds `train_df` and `test_df` strictly from the `train_years`/`test_years` lists passed in, with no row shuffling across the boundary, and raises `ValueError` on any year not present in `year_data`.
- `prepare_train_test` passes the same `feature_cols` list, in the same order, to both the `X_train` and `X_test` calls to `scale_features`, so train and test columns are guaranteed to line up — there's no way for them to drift apart given the current signature.
- `split_years_in_half` sorts and de-duplicates years before splitting and raises on fewer than 2 distinct years, matching PLAN.md's description of the primary split.

## Decision log (student)

One row per comment above, with the same number. Decision is Accepted or Rejected. For accepted comments, add the commit that fixed it.

| # | Decision | Reason | Fixed in commit |
| --- | --- | --- | --- |

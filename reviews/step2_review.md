# Step 2 Review: Handle Data Drift

- Reviewer transcript: transcripts/12_2026-10-28_reviewer_step2.md
- What was reviewed: the diff from step2-start to commit f4b949c (src/drift_analysis.py only)

## Comments (reviewer)

One row per issue. Number the rows 1, 2, 3, ...

| # | Severity | Location | Issue | Suggested fix |
| --- | --- | --- | --- | --- |
| 1 | Medium | `compute_drift_across_years` (src/drift_analysis.py, ~lines 55-74) | `pd.concat(pieces, ...)` is called unconditionally. If `year_data` has fewer than 2 years, `pieces` is empty and `pd.concat([])` raises `ValueError: No objects to concatenate`. The plan assumes 8 years will always be present, but nothing in Step 1 or Step 2 enforces a minimum, so a filtered or future `input_data/` with a single year would crash this function with an unhelpful error. | Guard with an explicit check (e.g. `if len(years) < 2: raise ValueError("need at least 2 years to compute drift")`) so the failure is clear instead of a generic pandas error. |
| 2 | Low | `ks_test_feature` (src/drift_analysis.py, ~lines 13-26) | No handling for NaNs in a feature column. I verified empirically that `scipy.stats.ks_2samp` silently returns `(nan, nan)` when a series contains `NaN`, rather than raising — so a feature with missing values would silently produce a `nan` statistic that sorts to the bottom of `top_drifting_features` with no warning that anything went wrong. The current dataset has no NaNs (verified), so this isn't live today, but there's no defensive check if that changes. | Either assert/raise on NaN input, or document that callers must pass NaN-free feature columns. |
| 3 | Low | Module docstring / overall | The plan's review checklist specifically asks whether constant or all-zero features are handled so the test doesn't fail or mislead. I tested this directly: in the real 2014 data, 868 of 1,848 features (~47%) are entirely zero for that year, and `ks_2samp` on two all-zero/constant series returns `statistic=0.0, p_value=1.0` with no warning or error — so the implementation is correct and non-misleading in practice. However, this is never stated anywhere in the code (no comment, no test, no mention in the module docstring) even though it's explicitly called out as a risk in PLAN.md's testing section. A future reader has to verify this themselves (as I just did) rather than being told it was considered. | Add a short comment or docstring note confirming constant/all-zero features are safe to pass through unmodified, so a future reader doesn't have to re-derive this. |
| 4 | Low | `compute_drift_between_years` / `compare_earliest_latest_year` (src/drift_analysis.py) | No validation that `year_a`/`year_b` are actually present as keys in `year_data`, or that every name in `feature_cols` is a column in both years' dataframes. A typo or a year missing from `year_data` currently surfaces as a raw `KeyError` from the dict/dataframe lookup rather than a clear, function-specific error message (compare to `split_by_year` in the Step 3 plan, which is specified to raise `ValueError` on an unknown year). | Not strictly required since the plan doesn't ask for this, but for consistency with the leakage-prevention error handling elsewhere in the plan, consider raising a clearer `ValueError` with the missing year/feature named. |

## Decision log (student)

One row per comment above, with the same number. Decision is Accepted or Rejected. For accepted comments, add the commit that fixed it.

| # | Decision | Reason | Fixed in commit |
| --- | --- | --- | --- |
| 1 | Accepted | Good safeguard | 98055d2 |
| 2 | Accepted | Valid check | beccbf9 |
| 3 | Accepted | Always good to be precise in documentation | 06f2cf8 |
| 4 | Accepted | Should definetly check - mistakes happen | 3fa542 |

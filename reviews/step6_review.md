# Step 6 Review: Test Data Prediction

- Reviewer transcript: transcripts/29_2026-10-29_reviewer_step6.md
- What was reviewed: the diff from step6-start to the latest commit (`src/evaluation.py`, adding `evaluate_by_year`)

## Comments (reviewer)

One row per issue. Number the rows 1, 2, 3, ...

| # | Severity | Location | Issue | Suggested fix |
| --- | --- | --- | --- | --- |
| 1 | Medium | `src/evaluation.py`, `evaluate_by_year`, line `year_df = year_data[year]` | If a requested year is missing from `year_data`, this raises a bare `KeyError` with no context. `split_by_year` in `src/preprocessing.py` (Step 3) handles the same situation by raising an explicit `ValueError` with a clear message, so this is inconsistent with the rest of the codebase and harder to debug. | Check `year not in year_data` and raise a `ValueError` naming the missing year, matching `split_by_year`'s pattern. |
| 2 | Low | `src/evaluation.py`, `evaluate_by_year` | The function has no guard against being called with training years instead of test years — it will happily "evaluate" a model on data it was trained on, silently producing misleadingly optimistic metrics. The docstring says it is "intended for the test years" but nothing enforces that. This is exactly the leakage question AGENTS.md/PLAN.md ask reviewers to check, so it is worth calling out even though the function itself cannot leak the scaler (it only ever calls `.transform()`). | Consider accepting `train_years` as well and asserting `set(years) & set(train_years) == set()`, or at minimum a comment noting this is caller-enforced; the current docstring wording ("e.g. the later half from `split_years_in_half`") is a hint but not a safeguard. |
| 3 | Low | Step 6 scope / `src/main.py` | There is no orchestration code yet (`src/main.py` does not exist) that actually calls `evaluate_by_year`. Based on this diff alone, it is impossible to confirm that only test years (not train years) are ever passed to it in practice, since nothing in `src/` calls the function yet. Not a bug in this diff, but it's an open item that should be verified once `main.py` is written, per PLAN.md's Orchestration section. | When `main.py` is added, confirm it calls `evaluate_by_year(..., years=test_years)` only, and add a test asserting this if feasible. |

## Decision log (student)

One row per comment above, with the same number. Decision is Accepted or Rejected. For accepted comments, add the commit that fixed it.

| # | Decision | Reason | Fixed in commit |
| --- | --- | --- | --- |
| 1 | Accepted | Consistency should be maintaned | e48e974 |
| 2 | Accepted | Necessary safeguard | e48e974 |
| 3 | Rejected | Too early to do anything about it | None | 

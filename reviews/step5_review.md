# Step 5 Review: Evaluate Classifier Performance

- Reviewer transcript: transcripts/25_2026-10-29_reviewer_step5.md
- What was reviewed: the diff from step5-start to the latest commit (src/evaluation.py, new file)

## Comments (reviewer)

One row per issue. Number the rows 1, 2, 3, ...

| # | Severity | Location | Issue | Suggested fix |
| --- | --- | --- | --- | --- |
| 1 | Low | `src/evaluation.py`, `evaluate_classifier` (lines 38-44) | `precision_score`, `recall_score`, and `f1_score` are called with `pos_label=1` but no explicit `average` argument, so they rely on scikit-learn's default (`average='binary'`). This is correct for the current binary malware/goodware labeling, but the correctness is implicit rather than stated, so a future change (e.g. a multi-class label) could silently change behavior without anything in this file flagging it. | Pass `average='binary'` explicitly alongside `pos_label=_POSITIVE_LABEL` so the binary-classification assumption is visible in the code, not just in the docstring. |
| 2 | Low | `src/evaluation.py`, `evaluate_all` (lines 48-68) | If `models` is empty, `evaluate_all` returns `pd.DataFrame([])`, an empty dataframe with no columns at all (not even `classifier`/`accuracy`/`precision`/`recall`/`f1`). Any caller that assumes those columns exist (e.g. for concatenation in Step 6/7 or for building the Step 5 report table) would get a `KeyError` instead of a clear failure at this function. | Either raise a `ValueError` for an empty `models` dict (consistent with how `split_by_year` in Step 3 raises on bad input) or construct the empty dataframe with explicit `columns=["classifier", "accuracy", "precision", "recall", "f1"]` so downstream code fails predictably either way. |

No other issues found. Malware (label 1) is used as the positive class consistently across `precision_score`, `recall_score`, and `f1_score`; `accuracy_score` correctly needs no `pos_label`. The module only calls `.predict()`, never `.fit()`, so it introduces no leakage on its own — leakage prevention still depends on the caller passing a true held-out test set from Step 3, which is outside this diff's scope. `zero_division=0` is a reasonable, documented choice matching the Step 5 test plan (e.g. a dummy classifier that always predicts 0).

## Decision log (student)

One row per comment above, with the same number. Decision is Accepted or Rejected. For accepted comments, add the commit that fixed it.

| # | Decision | Reason | Fixed in commit |
| --- | --- | --- | --- |

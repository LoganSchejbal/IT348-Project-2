# Step N Review: Post Step 7 — Project Adjustments (Console Driver)

- Reviewer transcript: transcripts/40_2026-11-01_reviewer_step7.md
- What was reviewed: the diff from step7-start to the latest commit (`.harness/diffs/step7_diff.patch`), covering new files `src/cli.py`, `src/main.py`, `src/sustainable.py`, against `PLAN.md`'s "Post Step 7: Project adjustments" section and `AGENTS.md`.

## Comments (reviewer)

| # | Severity | Location | Issue | Suggested fix |
| --- | --- | --- | --- | --- |
| 1 | Medium | `src/main.py`, `main()` (~lines 480-490) | `main()` calls `parse_args` and `run_selected_step` with no exception handling. PLAN.md's rationale for `ensure_data_loaded` raising `FileNotFoundError` is explicitly "so the console user sees one actionable message... instead of a stack trace from deep inside drift analysis or preprocessing." As written, that `FileNotFoundError` (and any `ValueError` from `evaluate_by_year`/`retraining_trajectory`/`run_sustainability_comparison`) still propagates all the way out of `main()` as an uncaught exception, so the console user gets a full Python traceback rather than the clean, actionable message the plan intended. | Catch the relevant exceptions in `main()` (or in `run_selected_step`) and print just the message (e.g. to `stderr`), optionally exiting with a non-zero status, instead of letting them propagate raw. |
| 2 | Low | `src/main.py`, `PipelineContext.classifier_factories` (~line 150) | `classifier_factories` is declared with `field(default=None)` while every other optional field in the same dataclass (`year_data`, `feature_cols`, `X_train`, etc.) uses a plain `= None`. There's no functional difference here since no `default_factory`/mutable default is involved, so the inconsistency is purely stylistic and slightly confusing to a reader trying to figure out why this one field is special. | Use `classifier_factories: dict[str, Callable[[], object]] | None = None` for consistency with the rest of the class, and drop the now-unused `field` import if nothing else needs it. |
| 3 | Low | `src/main.py`, `run_step2_drift` (~lines 330-344) | The `drift` console step only surfaces `top_drifting_features(compute_drift_across_years(...))`. PLAN.md's Step 2 "Approach" treats ranking *year pairs* by drift (`most_different_year_pairs`) as an equally core deliverable ("rank features... and rank year-pairs... to find which years differ most"), but `most_different_year_pairs` is never called from the driver, so a user running `--step drift` only sees per-feature drift, not which year pairs differ most. This is a minor completeness gap, not a bug — `year_a`/`year_b` columns are still present in the returned table, and PLAN.md's Post-Step-7 section does not spell out `run_step2_drift`'s internals the way it does for `run_step1_load`/`run_step3_preprocess`/`run_step4_train`, so this may have been an intentional simplification to keep the step to a single printable `DataFrame`. | If full Step 2 coverage from the console is wanted, either print a second table for `most_different_year_pairs` under the `drift` step, or note in `docs/post_step7_project_adjustments.md` that the console view is intentionally a subset of the full Step 2 report. |
| 4 | Low | `src/main.py`, `ensure_data_loaded` (~lines 153-184) | `context.feature_cols` is derived from an arbitrary year's dataframe (`next(iter(context.year_data.values()))`), relying on every year having the identical 1,848 feature columns. This matches AGENTS.md's stated dataset shape and isn't a bug today, but if a future `input_data/` year ever had a different column set (e.g. a partial/corrupted file), this would silently pick whichever year's columns happened to be iterated first with no check that other years match, rather than raising near the real cause the way `ensure_data_loaded`'s other check does. | Optional: assert (or at least note in the docstring) that all years are expected to share the same feature columns, or validate it explicitly if this is considered a real risk given AGENTS.md's "do not hard-code dataset assumptions" guidance. |

## Decision log (student)

One row per comment above, with the same number. Decision is Accepted or Rejected. For accepted comments, add the commit that fixed it.

| # | Decision | Reason | Fixed in commit |
| --- | --- | --- | --- |
| 1 | Accepted | This error should be caught | ec97403 |
| 2 | Accepted | Consistency standard | ec97403 |
| 3 | Accepted | Should at least note rationale | fa9e78f |
| 4 | Accepted | Should validate | ec97403 |
# Post Step 7 Report: Project Adjustments

Written by the builder agent.

- Builder transcript: transcripts/36_2026-11-01_builder_step7.md
- What this covers: a planning-only addition to `PLAN.md` (section "Post
  Step 7: Project adjustments") for a console driver that exposes all of
  Steps 1-7. No code was written in this session; this report records what
  was planned and why, for the builder session that implements it next.

## Why this was needed

AGENTS.md documents `python -m src.main` as the way to run the project, but
no `src/main.py` exists yet — `src/` only has the Step 1-7 library modules
(`data_loader.py`, `drift_analysis.py`, `preprocessing.py`, `models.py`,
`evaluation.py`, `sustainable.py`). There was nothing a grader, or the
instructor during the live check-in, could actually run from the console
to see the project work end to end, or to re-run a single step (e.g. just
the drift analysis, or just the sustainability comparison) without writing
a one-off script. The task was to close that gap at the planning level
first, so the next builder session has an unambiguous spec to implement
against.

## Decisions and reasoning

| # | Decision | Reasoning |
| --- | --- | --- |
| 1 | Split the driver into two new modules, `src/cli.py` (argument parsing) and `src/main.py` (orchestration), instead of one file. | AGENTS.md requires code to be "decoupled and modular" and that "changing one thing should generally not cause more changes to occur whenever possible." Argument parsing and pipeline orchestration are the two concerns a driver has; keeping them in separate modules means adding a console flag later never touches orchestration code, and adding a new pipeline step never touches argument parsing. |
| 2 | Add a `--step` option (`all`, `load`, `drift`, `preprocess`, `train`, `evaluate`, `evaluate-by-year`, `sustainable`) rather than only a no-argument "run everything" mode. | The task requires that "all necessary functions of the program should be accessible/implemented in this driver," not just the full pipeline. A single flag with one value per Step 1-7 function family satisfies that without growing into a large set of separate scripts. |
| 3 | Introduce a `PipelineContext` dataclass with `ensure_*` helper functions that compute a prerequisite only if it is not already set, instead of requiring the console user to run earlier steps first. | Later steps depend on earlier steps' outputs (e.g. Step 7's sustainability comparison needs the Step 3 scaler and Step 4 classifiers). Without this, `--step sustainable` alone would either crash or silently skip the dependency. The `ensure_*` pattern makes every step independently runnable while computing each prerequisite at most once, which also keeps the plan testable (a test can assert an `ensure_*` call is a no-op the second time). |
| 4 | Keep `python -m src.main` with no arguments running the full pipeline, matching what AGENTS.md already documents, rather than changing the default behavior. | AGENTS.md is the shared context file all three agents (and the grader) rely on for "how to run the code." Changing the no-argument behavior would silently invalidate that documentation; defaulting `--step` to `"all"` keeps the documented command correct while still adding the new capability. |
| 5 | Do not introduce a new `results/`-style folder for saving CSV output; print formatted tables to the console instead. | The task specifically asks for a program that "run[s] in the console." Writing output files would also require editing AGENTS.md's folder layout section, which is out of scope for a planning-only task — printing keeps this adjustment self-contained to `PLAN.md` and the new `src/` modules. |
| 6 | Write no code in this session; only add a PLAN.md section and this report. | Explicitly required by the task instructions for this session. The plan is detailed enough (function names, signatures, and responsibilities) that a later builder session can implement it without re-deriving the design. |

## What was changed

- `PLAN.md`: added a new "Post Step 7: Project adjustments" section
  describing `src/cli.py` and `src/main.py` — their functions, signatures,
  and responsibilities — and why no new top-level folder is needed.
  Commit: `47a20fd`.
- `docs/post_step7_project_adjustments.md` (this file): recorded the
  reasoning above. Commit: see below.

## Verification

Not applicable to this session: no code was written or run, only `PLAN.md`
prose and this report. The next builder session that implements
`src/cli.py` and `src/main.py` will need to verify the driver against the
existing Step 1-7 functions and the tester's forthcoming tests for this
section.

## Fix-mode update (reviews/post_step7_review_1.md)

A reviewer session reviewed this PLAN.md section and `src/sustainable.py`
(`reviews/post_step7_review_1.md`). The student accepted comments #1 and
#2 (both about this section) and rejected #3 and #4 (about
`src/sustainable.py`, out of scope for this planning-only task). Fixed in
commit `670296c`:

| # | Comment | Fix |
| --- | --- | --- |
| 1 | `format_dataframe_for_console` only accepts one `pd.DataFrame`, but `run_step1_load` was planned to return `dict[int, pd.DataFrame]`, `run_step4_train` a `dict[str, object]` of classifiers, and `run_step3_preprocess` `None` — none fit the shared formatter. | Added three display-only helpers (`summarize_loaded_years`, `summarize_preprocessing`, `summarize_classifiers`) so those three `run_stepN_*` functions each return a single summary `pd.DataFrame` instead. `PipelineContext` still holds the full, unsummarized data for later steps that need it; only the console-facing return value changed. |
| 2 | The plan didn't say what happens when `--data-dir` points to a missing or empty directory; `discover_dataset_files`/`load_all_years` don't raise on that today, so an empty `year_data` would flow silently into later steps. | `ensure_data_loaded` now checks `data_dir` exists and contains at least one `sampled_*_api.csv` file before calling `load_all_years`, raising a clear `FileNotFoundError` that names `--data-dir` as the thing to check. |

Comments #3 and #4 were rejected by the student as out of scope for this
task (they concern `src/sustainable.py`, not the Post Step 7 plan), so no
change was made for them here.

## Left unfinished

- `src/cli.py` and `src/main.py` are planned but not implemented.
- This section's tests (listed under "Testing" in `PLAN.md`) have not been
  written; that is the tester's task once the driver exists.
- Comments #3 and #4 in `reviews/post_step7_review_1.md` remain open
  against `src/sustainable.py`; they were rejected by the student, not
  addressed by this session.

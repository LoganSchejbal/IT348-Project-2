# Post Step 7 Report: Project Adjustments

Written by the builder agent.

- Builder transcripts: transcripts/36_2026-11-01_builder_step7.md (planning
  session), transcripts/39_2026-11-01_builder_step7.md (implementation
  session, this update)
- What this covers: a planning-only addition to `PLAN.md` (section "Post
  Step 7: Project adjustments") for a console driver that exposes all of
  Steps 1-7, plus the implementation of that plan (`src/cli.py`,
  `src/main.py`) and its results on the real dataset. The "Decisions and
  reasoning" and initial "What was changed"/"Verification" sections below
  are from the planning session; "Implementation (this session)" and
  "Results" below are from the implementation session.

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

## Implementation (this session)

This session implemented the driver planned above, exactly as specified
in PLAN.md's "Post Step 7: Project adjustments" section (including the
comment #1/#2 fixes already folded into that section):

- `src/cli.py` (commit `0d3b367`): `build_arg_parser`/`parse_args` and the
  `--data-dir`/`--step` options, with `STEP_CHOICES` restricted to
  `{"all", "load", "drift", "preprocess", "train", "evaluate",
  "evaluate-by-year", "sustainable"}`. Imports nothing from `pandas`,
  `scikit-learn`, or any other `src/` module.
- `src/main.py`:
  - `PipelineContext` and `ensure_data_loaded`/`ensure_preprocessed`/
    `ensure_trained` (commit `809f99b`). `ensure_data_loaded` raises
    `FileNotFoundError` naming `--data-dir` when the directory is missing
    or has no `sampled_*_api.csv` files, per the comment #2 fix.
  - `summarize_loaded_years`/`summarize_preprocessing`/
    `summarize_classifiers` (commit `bbe8123`), per the comment #1 fix, so
    `run_step1_load`, `run_step3_preprocess`, and `run_step4_train` each
    return a single `pd.DataFrame`.
  - `run_step1_load` through `run_step7_sustainable`,
    `format_dataframe_for_console`, `run_selected_step`, and `main`
    (commit `04b94a7`).

No function signature or behavior differs from the plan; nothing in
`PLAN.md` needed further revision during implementation.

## Results (real run, `input_data/`)

Run with `python -m src.main` (no arguments, i.e. `--step all`) against
the full 2014-2021 dataset. All numbers below are from that run, not
estimated.

**`--step load`** — `summarize_loaded_years`, one row per discovered year:

| year | rows | n_features | n_malware | n_benign |
| --- | --- | --- | --- | --- |
| 2014 | 3000 | 1848 | 1500 | 1500 |
| 2015 | 3000 | 1848 | 1500 | 1500 |
| 2016 | 3000 | 1848 | 1500 | 1500 |
| 2017 | 3000 | 1848 | 1500 | 1500 |
| 2018 | 3000 | 1848 | 1500 | 1500 |
| 2019 | 3000 | 1848 | 1500 | 1500 |
| 2020 | 3000 | 1848 | 1500 | 1500 |
| 2021 | 3000 | 1848 | 1500 | 1500 |

**`--step preprocess`** — `summarize_preprocessing`:

| split | years | shape |
| --- | --- | --- |
| train | 2014, 2015, 2016, 2017 | (12000, 1848) |
| test | 2018, 2019, 2020, 2021 | (12000, 1848) |

**`--step train`** — `summarize_classifiers` confirms both classifiers
from Step 4 (`logistic_regression`, `random_forest`) are built with
`random_state=42`, read directly from each fitted estimator's own
`get_params()`.

**`--step evaluate`** — pooled test set (2018-2021):

| classifier | accuracy | precision | recall | f1 |
| --- | --- | --- | --- | --- |
| logistic_regression | 0.6166 | 0.5762 | 0.8812 | 0.6968 |
| random_forest | 0.6602 | 0.5971 | 0.9857 | 0.7437 |

**`--step evaluate-by-year`** — matches the Step 6 trajectory already
reported in `docs/step6_test_results.md`:

| year | classifier | accuracy | precision | recall | f1 |
| --- | --- | --- | --- | --- | --- |
| 2018 | logistic_regression | 0.9547 | 0.9355 | 0.9767 | 0.9556 |
| 2018 | random_forest | 0.9567 | 0.9408 | 0.9747 | 0.9574 |
| 2019 | logistic_regression | 0.5730 | 0.5398 | 0.9900 | 0.6987 |
| 2019 | random_forest | 0.5807 | 0.5442 | 0.9927 | 0.7030 |
| 2020 | logistic_regression | 0.5477 | 0.5261 | 0.9613 | 0.6800 |
| 2020 | random_forest | 0.5540 | 0.5286 | 0.9973 | 0.6910 |
| 2021 | logistic_regression | 0.3910 | 0.4228 | 0.5967 | 0.4949 |
| 2021 | random_forest | 0.5497 | 0.5268 | 0.9780 | 0.6847 |

**`--step sustainable`** — matches the Step 7 trajectory already reported
in `docs/step7_sustainable_approach.md` (static vs. periodic retraining,
both classifiers):

| year | classifier | accuracy_static | f1_static | accuracy_retrained | f1_retrained |
| --- | --- | --- | --- | --- | --- |
| 2018 | logistic_regression | 0.9547 | 0.9556 | 0.9547 | 0.9556 |
| 2019 | logistic_regression | 0.5730 | 0.6987 | 0.5743 | 0.6999 |
| 2020 | logistic_regression | 0.5477 | 0.6800 | 0.9120 | 0.9123 |
| 2021 | logistic_regression | 0.3910 | 0.4949 | 0.9067 | 0.9062 |
| 2018 | random_forest | 0.9567 | 0.9574 | 0.9567 | 0.9574 |
| 2019 | random_forest | 0.5807 | 0.7030 | 0.5747 | 0.6988 |
| 2020 | random_forest | 0.5540 | 0.6910 | 0.9413 | 0.9399 |
| 2021 | random_forest | 0.5497 | 0.6847 | 0.9443 | 0.9415 |

Full output (including `--step drift`'s top-20 drifting features, which
is wide and omitted here) is reproducible with `python -m src.main`.

`python -m src.main --data-dir does_not_exist` was also run to confirm
`ensure_data_loaded` raises
`FileNotFoundError: No 'sampled_*_api.csv' files found in does_not_exist; check --data-dir`
and never reaches `load_all_years`, matching the comment #2 fix.

## Left unfinished

- This section's tests (listed under "Testing" in `PLAN.md`) have not
  been written; that is the tester's task now that the driver exists and
  has been run successfully against `input_data/`.
- Comments #3 and #4 in `reviews/post_step7_review_1.md` remain open
  against `src/sustainable.py`; they were rejected by the student, not
  addressed by this session.

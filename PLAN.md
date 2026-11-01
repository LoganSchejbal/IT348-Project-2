# PLAN.md

Plan for Steps 1-7 of Project 2 (Android malware classification under data drift). Written by the builder agent in Step 0. All code lives in `src/`; each step also produces a report in `docs/` (templates already exist there) and is reviewed/tested by separate agents.

## Train/test split by year and leakage prevention

The dataset currently covers 8 years: 2014-2021 (one `sampled_<year>_benign_api.csv` and one `sampled_<year>_malware_api.csv` per year, in `input_data/`), but the exact years are never hard-coded in code or in this plan — they are discovered at runtime from `load_all_years` (Step 1) and the split is always computed relative to whatever years are discovered.

- **Primary split (used for Steps 3-5):** `split_years_in_half(years: list[int]) -> tuple[list[int], list[int]]` (added to `src/preprocessing.py`) sorts the discovered years and returns `(train_years, test_years)` as the earlier half and later half (with the earlier half getting the extra year on an odd count). With the current 8 years this yields train = **2014-2017**, test = **2018-2021**, but the split follows automatically if years are added or removed from `input_data/`. This simulates a model trained once on historical data and deployed into the future, which is the realistic drift scenario the assignment asks about.
- **Per-year split (used for Steps 2, 6, and 7):** every year is also kept as its own labeled dataframe so drift can be measured year-to-year and performance can be reported year-by-year on the test years individually, not just on the pooled test set.
- **Leakage prevention:**
  - Any object that is *fit* (the `StandardScaler`, and the classifiers themselves) is fit only on rows from `train_years`. Test-year data is only ever passed through `.transform()` or `.predict()`, never `.fit()`.
  - Year boundaries are respected when concatenating: `split_by_year` (see Step 3) builds the train dataframe strictly from `train_years` and the test dataframe strictly from `test_years`; rows are never shuffled across that boundary before the split.
  - Drift statistics in Step 2 are descriptive (comparing year distributions to each other) and do not feed into any fitted object, so computing them does not leak test-year information into the model.
  - For Step 7 (sustainable approach), when a model is retrained on a later year, that year's data is added to the training pool *only after* it has first been used once as an unseen test year, so every year is scored by a model that has never seen it before being folded into training for subsequent years. The scaler is also refit from scratch on the current training pool before each retrain round (see Step 7), so it never sees the not-yet-scored year either.
  - No feature-selection step is used anywhere in the pipeline: with two classifiers that natively tolerate 1,848 features (L2-regularized Logistic Regression, and Random Forest's per-tree feature subsampling), feature selection is not needed for correctness, so there is nothing fit-to-data in this category to leak. If a later step found it necessary, it would be fit on `train_years` only, same as the scaler.

## Step 1: Prepare the Data

**Approach:** Read each `sampled_<year>_<class>_api.csv` file, drop its first column (an identifier, not a feature), attach a label parsed from the filename (`malware` -> 1, `benign` -> 0), and concatenate the two classes for each year into one dataframe per year. Years are discovered from the filenames present in `input_data/` rather than hard-coded, so the pipeline keeps working if years are added or removed.

**Files and functions (`src/data_loader.py`):**
- `extract_label_from_filename(filename: str) -> int` — parses the class token (`benign`/`malware`) out of a filename like `sampled_2014_malware_api.csv` and returns `1` for malware, `0` for benign. Raises `ValueError` if neither token is found.
- `discover_dataset_files(data_dir: Path) -> list[Path]` — lists all `sampled_*_api.csv` files in `data_dir`.
- `load_single_file(path: Path) -> pd.DataFrame` — reads one CSV, drops the first column, adds a `label` column from `extract_label_from_filename`, and adds a `year` column parsed from the filename.
- `load_year_data(data_dir: Path, year: int) -> pd.DataFrame` — loads and concatenates the benign and malware files for one year.
- `load_all_years(data_dir: Path) -> dict[int, pd.DataFrame]` — discovers every year present in `data_dir` and returns `{year: dataframe}` via `load_year_data`.
- `get_feature_columns(df: pd.DataFrame) -> list[str]` — returns all column names except `label` and `year`, used by every later step so the feature list is derived, not hard-coded.

**Report:** `docs/step1_data_summary.md` — files loaded per year, shape after dropping the first column, malware/goodware counts per year, and any anomalies (missing files, unexpected row/column counts).

**Testing:** tester can check `extract_label_from_filename` on known filenames, that `load_single_file` drops exactly one column and adds `label`/`year`, that `load_year_data` returns 3,000 rows (1,500 benign + 1,500 malware) with the expected number of feature columns, and that `load_all_years` returns one entry per year found in `input_data/`.

## Step 2: Handle Data Drift

**Approach:** Measure feature drift between years with the two-sample Kolmogorov-Smirnov test, applied per feature between consecutive years and between the earliest and latest year. Rank features by KS statistic to find which drift most, and rank year-pairs by mean/max KS statistic to find which years differ most.

**Files and functions (`src/drift_analysis.py`):**
- `ks_test_feature(series_a: pd.Series, series_b: pd.Series) -> tuple[float, float]` — runs `scipy.stats.ks_2samp`, returns `(statistic, p_value)` for one feature between two samples.
- `compute_drift_between_years(year_data: dict[int, pd.DataFrame], year_a: int, year_b: int, feature_cols: list[str]) -> pd.DataFrame` — applies `ks_test_feature` to every feature between the two years' dataframes, returns a dataframe indexed by feature with columns `statistic`, `p_value`.
- `compute_drift_across_years(year_data: dict[int, pd.DataFrame], feature_cols: list[str]) -> pd.DataFrame` — runs `compute_drift_between_years` on every consecutive year pair, returns one row per `(year_pair, feature, statistic, p_value)`.
- `compare_earliest_latest_year(year_data: dict[int, pd.DataFrame], feature_cols: list[str]) -> pd.DataFrame` — calls `compute_drift_between_years` on `(min(years), max(years))` specifically, giving the single comparison with the largest time gap, separately from the consecutive-year pairs above.
- `top_drifting_features(drift_df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame` — sorts by `statistic` descending and returns the top-N rows.
- `most_different_year_pairs(drift_df: pd.DataFrame) -> pd.DataFrame` — groups `compute_drift_across_years` output by year pair, aggregates (mean and max statistic), sorted descending.

**Report:** `docs/step2_drift_analysis.md` — method, table of top drifting features, which year pairs differ most, and what this implies for the models in later steps.

**Testing:** tester can check `ks_test_feature` against two synthetic distributions with a known difference, that `compute_drift_between_years` returns one row per feature with statistics in `[0, 1]`, that `top_drifting_features` returns rows sorted descending by statistic, and that `compare_earliest_latest_year` picks the min and max year keys out of `year_data` rather than any other pair.

## Step 3: Preprocess Data for Model Training

**Approach:** Combine the per-year dataframes from Step 1 into a single training dataframe (train years) and a single test dataframe (test years), fit a `StandardScaler` on the training dataframe's features only, and transform both sets with it.

**Files and functions (`src/preprocessing.py`):**
- `split_years_in_half(years: list[int]) -> tuple[list[int], list[int]]` — sorts the given years and splits them into `(train_years, test_years)` at the midpoint (earlier half trains, later half tests), so the primary split is always derived from whatever years are discovered rather than hard-coded.
- `split_by_year(year_data: dict[int, pd.DataFrame], train_years: list[int], test_years: list[int]) -> tuple[pd.DataFrame, pd.DataFrame]` — concatenates the dataframes for `train_years` into one dataframe and for `test_years` into another; raises `ValueError` if a requested year is missing from `year_data`.
- `fit_scaler(train_df: pd.DataFrame, feature_cols: list[str]) -> StandardScaler` — fits a `StandardScaler` on `train_df[feature_cols]` only.
- `scale_features(df: pd.DataFrame, feature_cols: list[str], scaler: StandardScaler) -> np.ndarray` — transforms (never fits) using an already-fit scaler.
- `prepare_train_test(year_data: dict[int, pd.DataFrame], feature_cols: list[str], train_years: list[int], test_years: list[int]) -> tuple[np.ndarray, np.ndarray, pd.Series, pd.Series, StandardScaler]` — runs `split_by_year`, `fit_scaler`, and `scale_features` and returns `X_train, X_test, y_train, y_test, scaler`.

No feature-selection step is included in this step (or anywhere in the plan) — see the note at the end of the leakage-prevention section above for why.

**Report:** `docs/step3_preprocessing.md` — scaling method and confirmation it was fit on training years only, which years are train/test (and that they come from `split_years_in_half`, not a literal), how leakage is prevented (cross-referenced to the section above), and a note that feature selection is intentionally not used.

**Testing:** tester can check that `split_years_in_half` divides a list of years into two halves of (near-)equal size with no overlap, that `split_by_year` raises on an unknown year, that the scaler's learned mean/scale come only from the training dataframe (e.g., compare `scaler.mean_` to a manually computed mean of just the training years), and that `prepare_train_test` output shapes match the row counts of the requested years.

## Step 4: Apply Machine Learning Classifiers

**Approach:** Train at least two scikit-learn classifiers — Logistic Regression (simple, interpretable linear baseline) and Random Forest (non-linear, handles the high-dimensional binary API-call features well) — on the Step 3 training data. All classifiers use `random_state=42` for reproducibility.

**Files and functions (`src/models.py`):**
- `get_classifier_factories(random_state: int = 42) -> dict[str, Callable[[], object]]` — returns `{"logistic_regression": lambda: LogisticRegression(...), "random_forest": lambda: RandomForestClassifier(...)}`, i.e. zero-argument factories that each construct a fresh, unfitted classifier with fixed hyperparameters. This is the single source of truth for classifier hyperparameters; both `get_classifiers` and Step 7's `retraining_trajectory` build on it.
- `get_classifiers(random_state: int = 42) -> dict[str, object]` — calls every factory from `get_classifier_factories` once and returns `{name: classifier_instance}`, for callers (Steps 4-6) that only need one trained instance of each classifier and never need to reset it.
- `train_classifiers(classifiers: dict[str, object], X_train: np.ndarray, y_train: pd.Series) -> dict[str, object]` — calls `.fit()` on each classifier with the training data and returns the same dict with fitted models.

**Report:** `docs/step4_models.md` — which classifiers, why, and a table of their hyperparameters (including `random_state`).

**Testing:** tester can check `get_classifier_factories` returns at least two distinct, callable factories that each produce an unfitted estimator on every call (two calls to the same factory give `==`-equal but not identical, unfitted objects), that `get_classifiers` returns at least two distinct classifier types each using `random_state=42`, and that `train_classifiers` returns fitted estimators (e.g., `hasattr(model, "coef_")` or `"classes_"` present after fitting).

## Step 5: Evaluate Classifier Performance

**Approach:** Evaluate each trained classifier on the pooled test set (test years combined) using accuracy, precision, recall, and F1-score, with malware (`label == 1`) as the positive class.

**Files and functions (`src/evaluation.py`):**
- `evaluate_classifier(model: object, X_test: np.ndarray, y_test: pd.Series) -> dict[str, float]` — predicts on `X_test` and returns `{"accuracy": ..., "precision": ..., "recall": ..., "f1": ...}` computed with `pos_label=1`.
- `evaluate_all(models: dict[str, object], X_test: np.ndarray, y_test: pd.Series) -> pd.DataFrame` — runs `evaluate_classifier` for every model, returns one row per classifier.

**Report:** `docs/step5_evaluation.md` — table of accuracy/precision/recall/F1 per classifier on the pooled test set, and observations about which classifier does better and why that might be.

**Testing:** tester can check `evaluate_classifier` against a classifier with known predictions (e.g., a dummy classifier that always predicts 0) to confirm the metrics match a hand-computed value, and that `evaluate_all` returns one row per input classifier with all four metric columns.

## Step 6: Test Data Prediction

**Approach:** Reuse the trained classifiers from Step 4 and predict on each individual test year separately (not just the pooled test set), to see how performance changes as the gap between training years and the predicted year grows.

**Files and functions (`src/evaluation.py`, extended):**
- `evaluate_by_year(models: dict[str, object], year_data: dict[int, pd.DataFrame], feature_cols: list[str], scaler: StandardScaler, years: list[int]) -> pd.DataFrame` — for each year in `years`, scales that year's features with the already-fit `scaler` (never re-fit), predicts with each model, and returns one row per `(year, classifier)` with accuracy/precision/recall/F1.

**Report:** `docs/step6_test_results.md` — table of year x classifier metrics, and a description of how performance changes as the data drifts further from the training years (2014-2017).

**Testing:** tester can check `evaluate_by_year` returns one row per `(year, classifier)` combination for the requested years, that it never calls `.fit()` on the scaler (e.g., by asserting `scaler.mean_` is unchanged before/after the call), and that metrics are in `[0, 1]`.

## Step 7: Sustainable ML Approach

**Approach:** Compare two strategies across the test years (the later half from `split_years_in_half`) in chronological order, run separately for **both** classifiers from Step 4 (logistic regression and random forest) — neither is dropped, since Steps 5-6 evaluate both and Step 7 should show whether retraining helps each one:
1. **Static model:** trained once on `train_years`, never updated, evaluated on each test year as in Step 6.
2. **Periodic retraining:** after each test year is scored, that year's labeled data is added to the training pool and a *fresh* classifier (from `get_classifier_factories`, never the already-fitted Step 4 instance) is retrained before scoring the next year (e.g., score the first test year with the model trained on `train_years`, then retrain on `train_years + [first test year]` before scoring the second test year, and so on). Before each retrain, a **new `StandardScaler` is fit from scratch on the current (growing) training pool** — the scaler is not reused across rounds — because the drift motivating this step can shift feature means/scales too, and refitting still never touches the not-yet-scored year.

This directly answers whether periodic retraining helps and avoids leakage, since a year is only added to the training pool (for both the classifier and the scaler) after it has been scored once as unseen data.

**Files and functions (`src/sustainable.py`):**
- `static_model_trajectory(models: dict[str, object], year_data: dict[int, pd.DataFrame], feature_cols: list[str], scaler: StandardScaler, test_years: list[int]) -> pd.DataFrame` — thin wrapper around `evaluate_by_year` representing the never-updated baseline for all classifiers in `models` at once (one row per `(year, classifier)`, matching `evaluate_by_year`'s output).
- `retraining_trajectory(classifier_factory: Callable[[], object], year_data: dict[int, pd.DataFrame], feature_cols: list[str], train_years: list[int], test_years: list[int]) -> pd.DataFrame` — implements the year-by-year retrain loop described above for a **single** classifier factory (fitting a new scaler each round internally; no `scaler` parameter, since none is reused across rounds), returns one row per `(year, metric)` for that retrained model.
- `run_sustainability_comparison(classifier_factories: dict[str, Callable[[], object]], models: dict[str, object], year_data: dict[int, pd.DataFrame], feature_cols: list[str], scaler: StandardScaler, train_years: list[int], test_years: list[int]) -> pd.DataFrame` — loops `retraining_trajectory` over every entry in `classifier_factories` (i.e., both classifiers), calls `static_model_trajectory` once for the matching `models`, and concatenates everything into one table with a `classifier` column so both classifiers' static-vs-retrained comparisons are in a single dataframe.
- `compare_static_vs_retrained(static_df: pd.DataFrame, retrained_df: pd.DataFrame) -> pd.DataFrame` — merges the two trajectories into one table keyed by `(year, classifier)` for side-by-side comparison; used internally by `run_sustainability_comparison`.

**Report:** `docs/step7_sustainable_approach.md` — the retraining approach tried, a table comparing it with the static model across test years **for both classifiers**, and conclusions for `REPORT.md`.

**Testing:** tester can check `retraining_trajectory` grows its training set by one year after each scored year (e.g., by inspecting the size of the training data passed to each refit) and that each round's scaler is a distinct, newly-fit object (not the same instance reused), that `compare_static_vs_retrained` aligns rows by `(year, classifier)` without dropping or duplicating any test year, and that `run_sustainability_comparison`'s output contains both classifier names from `classifier_factories`.

## Orchestration

`src/main.py` — a `main() -> None` function (invoked by `python -m src.main`) that calls the functions above in order (load data -> drift analysis -> preprocess -> train -> evaluate -> evaluate by year -> sustainable comparison) and prints/saves the results used to fill in the `docs/` reports. No step's hard-coded assumptions (years present, number of classifiers, feature count) belong in `main.py`; those are all derived from `input_data/` and the dicts returned by the functions above.

## Post Step 7: Project adjustments

Steps 1-7 are implemented as library functions in `src/`, but no driver file
exists yet — there is nothing a grader or the live check-in can actually run
from the console to see the project work end to end. This section plans a
console driver that wires the existing Step 1-7 functions together and
exposes every one of them as a runnable action, without duplicating any of
their logic. This is a planning-only addition: no code is written under
this section; it describes what the builder will implement next.

**Approach:** Split the driver into two new, decoupled modules so that
argument parsing (how the console is driven) stays independent of
orchestration (what each step does), matching the existing one-module-per-
concern layout of `src/`:

- `src/cli.py` — owns the console interface only; knows nothing about
  pandas, scikit-learn, or any Step 1-7 function.
- `src/main.py` — owns orchestration only; calls the Step 1-7 functions
  already planned above (`data_loader`, `drift_analysis`, `preprocessing`,
  `models`, `evaluation`, `sustainable`) and formats their output for the
  console. `main.py` never parses `sys.argv` itself, so the two concerns
  can change independently (e.g. adding a new console flag never touches
  the orchestration code, and adding a new pipeline step never touches
  argument parsing).

**Files and functions:**

- `src/cli.py`:
  - `build_arg_parser() -> argparse.ArgumentParser` — defines one
    `argparse` parser with a `--data-dir` option (default `input_data`,
    so the dataset location is still determined at run time per AGENTS.md,
    never hard-coded) and a `--step` option restricted to
    `{"all", "load", "drift", "preprocess", "train", "evaluate",
    "evaluate-by-year", "sustainable"}` (default `"all"`), so every
    Step 1-7 function family is individually reachable from the console
    as well as runnable together.
  - `parse_args(argv: list[str] | None = None) -> argparse.Namespace` —
    thin wrapper around `build_arg_parser().parse_args(argv)`, kept
    separate so tests can call it directly with a list of strings instead
    of patching `sys.argv`.
- `src/main.py`:
  - `PipelineContext` (a small `dataclass`) — holds whatever state later
    steps need that earlier steps produced: `data_dir`, `year_data`,
    `feature_cols`, `train_years`, `test_years`, `X_train`, `X_test`,
    `y_train`, `y_test`, `scaler`, `classifiers`, `classifier_factories`.
    Fields start unset (`None`) and are filled in by the step-runner
    functions below, so each runner can check "has this already been
    computed by an earlier call?" instead of recomputing it.
  - `ensure_data_loaded(context: PipelineContext) -> None` — before calling
    `load_all_years`, checks `Path(context.data_dir).is_dir()` and that
    `discover_dataset_files(context.data_dir)` returns at least one file;
    this check is needed here (not left to `data_loader.py`) because
    neither `discover_dataset_files` (a `glob`, which simply returns an
    empty list for a missing or empty directory) nor `load_all_years`
    raises on a missing/empty `data_dir` today — an empty `year_data` dict
    would otherwise flow silently into every later step and fail far from
    the real cause. If the check fails, raises
    `FileNotFoundError(f"No 'sampled_*_api.csv' files found in {data_dir}; "
    f"check --data-dir")` so the console user sees one actionable message
    pointing at the flag that controls it, instead of a stack trace from
    deep inside drift analysis or preprocessing. Only then does it call
    `load_all_years` + `get_feature_columns` + `split_years_in_half`, if
    `context.year_data` is still unset.
  - `ensure_preprocessed(context: PipelineContext) -> None`,
    `ensure_trained(context: PipelineContext) -> None` — same
    already-set/no-op pattern as `ensure_data_loaded`, calling
    `prepare_train_test`, and `get_classifiers` + `get_classifier_factories`
    + `train_classifiers` respectively, only if the corresponding
    `PipelineContext` fields are still unset. This is what lets a console
    user request a single step (e.g. `--step sustainable`) and still get
    correct results, because the prerequisite steps it depends on
    (including the `ensure_data_loaded` validation above) run
    automatically and only once.
  - `summarize_loaded_years(year_data: dict[int, pd.DataFrame], feature_cols: list[str]) -> pd.DataFrame`,
    `summarize_preprocessing(train_years: list[int], test_years: list[int], X_train: np.ndarray, X_test: np.ndarray) -> pd.DataFrame`,
    `summarize_classifiers(classifiers: dict[str, object]) -> pd.DataFrame` —
    three small, display-only helpers added so that every `run_stepN_*`
    function below can return a single `pd.DataFrame`, resolving the
    mismatch between `format_dataframe_for_console`'s single-dataframe
    signature and steps whose underlying Step 1/3/4 functions don't
    themselves return one printable frame:
    - `summarize_loaded_years` returns one row per year already present in
      `year_data` with `year`, `rows`, `n_features` (`len(feature_cols)`),
      `n_malware`, `n_benign` (the last two from `(df["label"] == 1/0).sum()`).
    - `summarize_preprocessing` returns one row for `"train"` and one for
      `"test"`, each with its years (joined as a string) and its array's
      shape (`X_train.shape`/`X_test.shape`).
    - `summarize_classifiers` returns one row per classifier with its name
      and `model.get_params()` (every scikit-learn estimator already
      exposes this), so hyperparameters are read from the fitted objects
      rather than duplicated from `models.py`.
    None of these inspect anything beyond objects the Step 1/3/4 functions
    already produced, so this stays a console-formatting concern, not new
    modeling or data logic.
  - `run_step1_load(context) -> pd.DataFrame`,
    `run_step2_drift(context) -> pd.DataFrame`,
    `run_step3_preprocess(context) -> pd.DataFrame`,
    `run_step4_train(context) -> pd.DataFrame`,
    `run_step5_evaluate(context) -> pd.DataFrame`,
    `run_step6_evaluate_by_year(context) -> pd.DataFrame`,
    `run_step7_sustainable(context) -> pd.DataFrame` — one function per
    step, each calling `ensure_*` for whatever it needs first, then
    calling only the already-planned Step 1-7 functions (no new modeling
    or data logic lives here). `run_step1_load`, `run_step3_preprocess`,
    and `run_step4_train` call the matching `summarize_*` helper above on
    their way out so every one of the seven functions returns a single
    `pd.DataFrame`; the other four already produce one directly from their
    underlying Step 2/5/6/7 functions. `PipelineContext` still holds the
    full, unsummarized `year_data`/`classifiers`/etc. for later steps to
    consume — only the console-facing return value is a summary.
  - `format_dataframe_for_console(df: pd.DataFrame) -> str` — a single
    shared helper (so every step prints tables the same way, now that
    every `run_stepN_*` function returns one `pd.DataFrame`) that calls
    `pandas.DataFrame.to_string(index=False)` and rounds floats for
    readability.
  - `run_selected_step(context, step: str) -> None` — maps the `--step`
    string from `parse_args` onto the `run_stepN_*` functions above
    (`"all"` runs all seven in order), printing each result with
    `format_dataframe_for_console`.
  - `main(argv: list[str] | None = None) -> None` — calls
    `parse_args(argv)`, builds a `PipelineContext` from `args.data_dir`,
    and calls `run_selected_step(context, args.step)`. This is the
    function `python -m src.main` invokes, keeping AGENTS.md's documented
    run command correct while adding the `--step` option as a console
    convenience, not a replacement for it (running with no arguments
    still runs everything, exactly as AGENTS.md describes today).

**Why no new top-level folder:** results are printed to the console, not
written to a new `results/`-style folder, so this change needs no edit to
AGENTS.md's folder layout section.

**Report:** `docs/post_step7_project_adjustments.md` — what was planned
here and why, written by the builder once this section existed (this
section is also referenced, not duplicated, by that report).

**Testing:** once implemented, the tester can check that `parse_args`
rejects a `--step` value outside the fixed set, that each `ensure_*`
helper is a no-op (does not recompute) when its `PipelineContext` fields
are already set, that `ensure_data_loaded` raises `FileNotFoundError`
(and never calls `load_all_years`) for a `data_dir` that does not exist
or contains no `sampled_*_api.csv` files, that `run_step1_load`,
`run_step3_preprocess`, and `run_step4_train` each return a single
`pd.DataFrame` (via `summarize_loaded_years`/`summarize_preprocessing`/
`summarize_classifiers`) so `format_dataframe_for_console` can render
every step's output the same way, that `run_selected_step(context, "all")`
populates every `PipelineContext` field exactly once even though multiple
`run_stepN_*` functions depend on the same prerequisite, and that
`main([])` (no arguments) runs the full pipeline, matching today's
documented `python -m src.main` behavior.

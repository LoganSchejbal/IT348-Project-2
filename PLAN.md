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

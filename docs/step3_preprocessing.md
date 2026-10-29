# Step 3 Report: Preprocessing

Written by the builder agent.

## Scaling

Features are scaled with scikit-learn's `StandardScaler` (zero mean, unit variance), via `fit_scaler`/`scale_features` in `src/preprocessing.py`. The scaler is fit only on the training dataframe's features (`fit_scaler(train_df, feature_cols)`, called internally by `prepare_train_test`); the test dataframe is only ever passed through `scaler.transform()`, never `scaler.fit()`.

Verified on the real dataset:

- `scaler.mean_` matches a manual mean computed directly from the training-years dataframe only (`np.allclose(scaler.mean_, train_df[feature_cols].mean())` is `True`).
- `scaler.mean_` is *different* from the mean computed over the full training+testing data, confirming the test years did not influence the fitted mean.
- After transforming, `X_train`'s per-feature mean is ~0 (e.g. first 5 features: `[-5.3e-18, 9.5e-18, -2.4e-17, -1.9e-17, -2.4e-18]`), as expected for data a `StandardScaler` was fit on.
- `X_test`'s per-feature mean is *not* 0 (e.g. first 5 features: `[0.016, 0.442, -0.021, -0.016, -0.050]`) — it is scaled with the training-years' mean/scale, so any drift between train and test years shows up as a nonzero mean on the test set rather than being hidden by a scaler that saw the test data.
- For zero-variance (constant) features, `StandardScaler` sets `scale_ = 1.0` by convention (sklearn's documented behavior for avoiding division by zero), rather than leaving the feature unscaled or raising an error.

No feature-selection step is used in this step or anywhere in the pipeline, per PLAN.md: Logistic Regression (L2-regularized) and Random Forest (per-tree feature subsampling), the two classifiers planned for Step 4, both natively tolerate the full 1,848-feature space, so there is nothing fit-to-data in this category that could leak test-year information.

## Train/test split

Years are discovered at runtime from `input_data/` (via `load_all_years`, Step 1) and split with `split_years_in_half`, which sorts the discovered years and divides them at the midpoint — never a literal list of years in code.

On the current dataset, 8 years are present: 2014-2021. `split_years_in_half` produces:

- **Train years:** 2014, 2015, 2016, 2017
- **Test years:** 2018, 2019, 2020, 2021

Resulting shapes after `split_by_year` and scaling:

| Set | Rows | Features | Malware (label=1) | Benign (label=0) |
| --- | --- | --- | --- | --- |
| Train | 12,000 | 1,848 | 6,000 | 6,000 |
| Test | 12,000 | 1,848 | 6,000 | 6,000 |

(Each year contributes 1,500 benign + 1,500 malware rows per AGENTS.md, and `load_single_file` truncates any file with extra rows to the documented 1,500 — see Step 1 — so 4 years x 3,000 rows = 12,000 rows per set.)

If years are added to or removed from `input_data/`, `split_years_in_half` recomputes the split automatically; no code change is needed.

## Leakage prevention

- The `StandardScaler` is fit exclusively on `train_df` (built from `train_years`) inside `fit_scaler`. `scale_features` and `prepare_train_test` only ever call `scaler.transform()` on the test dataframe, never `scaler.fit()` or `scaler.fit_transform()`.
- `split_by_year` concatenates each set strictly from the year keys requested (`train_years` for the training frame, `test_years` for the testing frame); rows from different years are never shuffled together before the split, and `split_by_year` raises `ValueError` if a requested year is missing from `year_data`, so a typo can't silently pull in the wrong year.
- `split_years_in_half` itself only looks at the sorted list of years and splits by position; it never inspects feature values, so it cannot leak anything about the test-year distributions into the split decision.
- This matches PLAN.md's leakage-prevention section: anything *fit* to data (the scaler, and the classifiers in later steps) is fit on `train_years` only, and year boundaries are respected whenever dataframes are concatenated.
- Verified directly: `scaler.mean_` equals the mean computed from `train_df[feature_cols]` alone, and differs from the mean computed over `train_df` and `test_df` combined (see Scaling section above) — i.e., the fitted scaler provably never saw the test years' values.

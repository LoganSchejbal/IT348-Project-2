# Step 6 Report: Test Results

Written by the builder agent.

## Approach

`evaluate_by_year` (added to `src/evaluation.py`) reuses the Step 4
classifiers (`logistic_regression`, `random_forest`, both trained once on
train years 2014-2017) and the Step 3 `StandardScaler` (also fit only on
2014-2017). For each test year individually, it transforms that year's
features with the already-fit scaler (`.transform()` only, never `.fit()`)
and scores every model with `evaluate_classifier` from Step 5. This breaks
the pooled test-set numbers from `docs/step5_evaluation.md` down into one
row per `(year, classifier)`, so performance can be tracked as the gap
between the training years and the predicted year grows.

Ran the full Step 1-6 pipeline on the real data in `input_data/`:
`load_all_years` -> `split_years_in_half` (train years 2014-2017, test years
2018-2021) -> `prepare_train_test` -> `get_classifiers` + `train_classifiers`
-> `evaluate_by_year` on the four test years.

## Results by test year

| Year | Classifier | Accuracy | Precision | Recall | F1-score |
| --- | --- | --- | --- | --- | --- |
| 2018 | `logistic_regression` | 0.9547 | 0.9355 | 0.9767 | 0.9556 |
| 2018 | `random_forest` | 0.9567 | 0.9408 | 0.9747 | 0.9574 |
| 2019 | `logistic_regression` | 0.5730 | 0.5398 | 0.9900 | 0.6987 |
| 2019 | `random_forest` | 0.5807 | 0.5442 | 0.9927 | 0.7030 |
| 2020 | `logistic_regression` | 0.5477 | 0.5261 | 0.9613 | 0.6800 |
| 2020 | `random_forest` | 0.5540 | 0.5286 | 0.9973 | 0.6910 |
| 2021 | `logistic_regression` | 0.3910 | 0.4228 | 0.5967 | 0.4949 |
| 2021 | `random_forest` | 0.5497 | 0.5268 | 0.9780 | 0.6847 |

(Each row: 3,000 rows for that year, 1,500 benign / 1,500 malware, scaled
with the `StandardScaler` fit on train years 2014-2017 in Step 3; malware =
positive class. Pooled test-set accuracy from `docs/step5_evaluation.md`
(0.6166 / 0.6603) is the row-weighted average of these four years' accuracy
for each classifier, confirming the two reports agree.)

## Effect of drift

- **2018 (one year after the training window) is scored almost as well as
  the training years themselves** (~0.955 accuracy for both classifiers,
  comparable to the ~0.98-0.996 train accuracy from `docs/step4_models.md`).
  Both models generalize well to the year immediately following 2014-2017.
- **Performance drops sharply starting at 2019** and stays low through
  2020-2021: accuracy falls from ~0.955 (2018) to ~0.55-0.58 (2019-2020),
  near the ~0.5 a model gets by always predicting one class on this
  balanced data. This is a much larger, more sudden drop than a gradual
  one-year-at-a-time decline, suggesting the API-call feature distributions
  shift significantly starting around 2019 rather than drifting smoothly
  year over year — consistent with Step 2's drift analysis
  (`docs/step2_drift_analysis.md`) showing the largest KS-statistic gaps
  between non-adjacent year pairs.
- **Recall stays high (0.90-0.99) in every year except Logistic
  Regression on 2021 (0.597)**, while precision stays low (0.42-0.54)
  everywhere except 2018. Both models keep flagging most malware
  correctly, but after 2018 they also misclassify roughly half of benign
  apps as malware, which is what drags accuracy down to near-chance even
  though recall looks fine in isolation.
- **Random Forest is more robust to drift than Logistic Regression**,
  especially in the worst year: on 2021, Random Forest still scores 0.5497
  accuracy / 0.9780 recall, while Logistic Regression collapses to 0.3910
  accuracy / 0.5967 recall — its decision boundary degrades the most on the
  year furthest from training. On 2018-2020 the two classifiers are close
  (within ~0.01 accuracy of each other), so the gap only shows up once the
  drift is severe enough.
- Taken together, a model trained once on 2014-2017 is only reliable for
  about one year past its training window on this dataset; by two years
  out it is close to useless, which motivates Step 7's comparison of this
  static approach against periodic retraining.

## Verification

- Ran the Step 1-6 pipeline end-to-end against the real CSVs in
  `input_data/` (not synthetic data) via a one-off script calling
  `load_all_years`, `get_feature_columns`, `split_years_in_half`,
  `prepare_train_test`, `get_classifiers`, `train_classifiers`, and
  `evaluate_by_year`; the table above is copied directly from that script's
  printed output.
- Cross-checked internal consistency: computing the row-weighted average
  of the four per-year accuracy values above (each year has an equal 3,000
  rows, so a simple mean) reproduces the pooled test-set accuracy already
  reported in `docs/step5_evaluation.md` for both classifiers
  (logistic_regression: mean of 0.9547/0.5730/0.5477/0.3910 = 0.6166;
  random_forest: mean of 0.9567/0.5807/0.5540/0.5497 = 0.6603), confirming
  `evaluate_by_year` and `evaluate_all` are consistent with each other on
  the same underlying predictions.
- Confirmed every metric value in the table is a float in `[0, 1]` and
  that `evaluate_by_year`'s output has exactly one row per
  `(year, classifier)` combination (4 years x 2 classifiers = 8 rows).

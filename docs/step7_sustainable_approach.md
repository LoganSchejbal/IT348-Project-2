# Step 7 Report: Sustainable Approach

Written by the builder agent.

## Approach

Compared two strategies across the four test years (2018-2021, the later
half of the 8 discovered years from `preprocessing.split_years_in_half`),
run separately for both Step 4 classifiers (`logistic_regression`,
`random_forest`), per PLAN.md:

1. **Static model** (`sustainable.static_model_trajectory`, a thin wrapper
   around `evaluation.evaluate_by_year`): the Step 4 classifiers and the
   Step 3 `StandardScaler`, both fit once on 2014-2017 and never updated,
   scored on each test year.
2. **Periodic retraining** (`sustainable.retraining_trajectory`): processes
   the test years in chronological order. Before scoring each test year, a
   **fresh** classifier is built from `models.get_classifier_factories`
   (never the already-fitted Step 4 instance) and a **fresh**
   `StandardScaler` is fit from scratch, both on the current training
   pool. The test year is scored with that fresh pair, and only afterward
   is it added to the pool for the next round -- so a year is always
   scored before it is ever used to fit anything, and the scaler and
   classifier of each round are distinct, newly created objects, never
   reused from a previous round.

`sustainable.run_sustainability_comparison` runs step 2 once per
classifier in `models.get_classifier_factories`, runs step 1 once across
all classifiers at once (`evaluate_by_year` already scores every model in
a `models` dict), and `sustainable.compare_static_vs_retrained` merges the
two trajectories on `(year, classifier)` into one side-by-side table,
raising if either side is missing a year/classifier the other has.

Ran the full Step 1-7 pipeline on the real data in `input_data/`:
`load_all_years` -> `split_years_in_half` (train years 2014-2017, test
years 2018-2021) -> `prepare_train_test` -> `get_classifiers` +
`train_classifiers` (static models) -> `get_classifier_factories`
(retraining) -> `run_sustainability_comparison`.

## Comparison with a never-updated model

| Year | Classifier | Accuracy (static) | Accuracy (retrained) | Precision (static) | Precision (retrained) | Recall (static) | Recall (retrained) | F1 (static) | F1 (retrained) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2018 | `logistic_regression` | 0.9547 | 0.9547 | 0.9355 | 0.9355 | 0.9767 | 0.9767 | 0.9556 | 0.9556 |
| 2019 | `logistic_regression` | 0.5730 | 0.5743 | 0.5398 | 0.5405 | 0.9900 | 0.9927 | 0.6987 | 0.6999 |
| 2020 | `logistic_regression` | 0.5477 | 0.9120 | 0.5261 | 0.9093 | 0.9613 | 0.9153 | 0.6800 | 0.9123 |
| 2021 | `logistic_regression` | 0.3910 | 0.9067 | 0.4228 | 0.9111 | 0.5967 | 0.9013 | 0.4949 | 0.9062 |
| 2018 | `random_forest` | 0.9567 | 0.9567 | 0.9408 | 0.9408 | 0.9747 | 0.9747 | 0.9574 | 0.9574 |
| 2019 | `random_forest` | 0.5807 | 0.5747 | 0.5442 | 0.5409 | 0.9927 | 0.9867 | 0.7030 | 0.6988 |
| 2020 | `random_forest` | 0.5540 | 0.9413 | 0.5286 | 0.9636 | 0.9973 | 0.9173 | 0.6910 | 0.9399 |
| 2021 | `random_forest` | 0.5497 | 0.9443 | 0.5268 | 0.9912 | 0.9780 | 0.8967 | 0.6847 | 0.9415 |

Mean accuracy across the 4 test years:

| Classifier | Mean accuracy (static) | Mean accuracy (retrained) |
| --- | --- | --- |
| `logistic_regression` | 0.6166 | 0.8369 |
| `random_forest` | 0.6603 | 0.8542 |

(`accuracy_static` reproduces `docs/step6_test_results.md` exactly, as
expected since both come from the same `evaluate_by_year` call on the same
fitted models/scaler.)

## Conclusions for REPORT.md

- **2018 is identical for both strategies**, as it must be: it is the
  first test year, so the "retrained" model's training pool is still just
  2014-2017 -- no retraining has happened yet. This is the expected
  boundary case, not a bug.
- **2019 shows almost no benefit from retraining** (0.573 -> 0.574 for
  logistic regression, 0.581 -> 0.575 for random forest, essentially
  within noise): the pool has only gained one extra year (2018), which
  Step 6 showed is not where the drift happens, so there is little new
  information for the retrained model to learn from yet.
- **Retraining pays off sharply from 2020 onward**, right where Step 6
  found the static models collapsed toward chance accuracy: once 2019 (a
  post-drift year) joins the training pool, accuracy jumps from ~0.55 to
  ~0.91-0.94 for both classifiers on 2020 and 2021, versus the static
  models staying stuck at ~0.39-0.55. This matches Step 2/6's finding that
  the drift is a sudden shift rather than a smooth year-over-year change:
  the static model is blind to it because it never sees post-2017 data,
  while the retrained model recovers as soon as it has even one
  drifted year in its training pool.
- **Random Forest benefits slightly more than Logistic Regression** in the
  worst drifted years (2020: 0.941 vs. 0.912 accuracy; 2021: 0.944 vs.
  0.907), consistent with Step 6's observation that Random Forest degrades
  more gracefully under drift -- the gap persists even after retraining,
  though it shrinks a lot compared to the static-model gap Step 6 found
  (e.g. 2021 static accuracy gap was 0.550 vs. 0.391, a 0.159 difference;
  retrained it is 0.944 vs. 0.907, a 0.037 difference).
- **Overall conclusion**: a model trained once and never updated is not a
  sustainable approach for this dataset -- it loses more than a third of
  its accuracy within two years of the training window. Periodic
  retraining recovers most of that loss as soon as drifted data is
  available to retrain on, at the cost of needing labeled data from each
  new year and refitting both the scaler and the classifier from scratch
  periodically. This supports retraining (rather than a single static
  deployment) as the sustainable strategy for keeping this malware
  classifier accurate as the data drifts.

## Verification

- Ran the Step 1-7 pipeline end-to-end against the real CSVs in
  `input_data/` (not synthetic data) via a one-off script calling
  `load_all_years`, `get_feature_columns`, `split_years_in_half`,
  `prepare_train_test`, `get_classifiers`, `train_classifiers`,
  `get_classifier_factories`, and `run_sustainability_comparison`; the
  tables above are copied directly from that script's printed/saved
  output.
- Confirmed `accuracy_static` in the comparison table matches
  `docs/step6_test_results.md`'s per-year accuracy exactly for both
  classifiers and all four years (e.g. 2021 logistic_regression: 0.3910 in
  both reports), confirming `static_model_trajectory` is consistent with
  Step 6's `evaluate_by_year` results.
- Confirmed the 2018 row is byte-for-byte identical between the static and
  retrained columns, which must hold since the retraining pool for the
  first test year is exactly the original `train_years` -- a built-in
  sanity check on the retraining loop's leakage boundary.
- Confirmed every metric value in the table is a float in `[0, 1]` and
  that the comparison table has exactly one row per `(year, classifier)`
  combination (4 years x 2 classifiers = 8 rows), with no missing or
  duplicated pairs (enforced by `compare_static_vs_retrained`'s key check).

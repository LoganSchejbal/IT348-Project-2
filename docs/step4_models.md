# Step 4 Report: Models

Written by the builder agent.

## Classifiers

Two scikit-learn classifiers are trained in `src/models.py`, chosen so one is a
simple linear baseline and the other is a non-linear model that can capture
feature interactions:

- **Logistic Regression** (`sklearn.linear_model.LogisticRegression`): a
  linear, L2-regularized baseline. It is fast to train and easy to interpret
  (each of the 1,848 API-call features gets a single coefficient), which
  makes it a useful reference point for how much the non-linear model gains.
- **Random Forest** (`sklearn.ensemble.RandomForestClassifier`): an ensemble
  of decision trees that can model non-linear relationships and interactions
  between API calls that a linear model cannot, and tolerates the
  high-dimensional (1,848-feature), mostly binary/count-valued feature space
  without needing feature selection (each tree only splits on a random subset
  of features at each node).

`class_weight` is intentionally left at its default (`None`, i.e. equal
weight) for both classifiers. Per `AGENTS.md`, every
`sampled_<year>_<class>_api.csv` file pair contributes exactly 1,500 benign +
1,500 malware rows, so any concatenation of full years (as Step 1 does) stays
balanced 50/50 and reweighting is unnecessary. This assumption lives in the
dataset, not in `models.py`, so it is noted here and as a comment in
`get_classifier_factories` in case a later step ever subsets or drops rows
before training.

Both are built from `get_classifier_factories()` in `src/models.py`, which is
the single source of truth for their hyperparameters: it returns
zero-argument factories (not instances), so Step 7's retraining loop can ask
for a brand-new, unfitted classifier for every retrain round instead of
reusing an already-fitted one. `get_classifiers()` calls each factory once
for callers (Steps 4-6) that only need one trained instance.

Both classifiers were fit with `train_classifiers()` on the scaled Step 3
training data (`X_train`, `y_train`), built from `train_years = [2014, 2015,
2016, 2017]` via `preprocessing.prepare_train_test` (12,000 rows, 1,848
features, balanced 6,000/6,000 benign/malware).

## Hyperparameters

| Classifier | Key hyperparameters | `random_state` |
| --- | --- | --- |
| `logistic_regression` | `max_iter=1000` (raised from the default 100 so `lbfgs` reliably converges on 1,848 scaled features); all other parameters left at scikit-learn defaults (`penalty` defaults to L2, `C=1.0`, `solver="lbfgs"`) | 42 |
| `random_forest` | `n_estimators=100`, `n_jobs=-1` (parallelizes tree training across all available cores; does not affect reproducibility, which is still controlled by `random_state`); all other parameters left at scikit-learn defaults (`max_depth=None`, `max_features="sqrt"`, `criterion="gini"`) | 42 |

`random_state=42` is passed to `get_classifier_factories` (and defaulted
there) so both classifiers are reproducible across runs.

## Verification

Ran the full Step 1-4 pipeline on the real data in `input_data/` (8 years,
2014-2021) via a one-off script calling `load_all_years`,
`split_years_in_half`, `prepare_train_test`, `get_classifiers`, and
`train_classifiers`:

- Both classifiers fit without errors and expose `classes_ == [0, 1]` after
  training, confirming they were actually fitted (not left as the unfitted
  objects `get_classifiers` returns).
- Training time for both classifiers combined on 12,000 rows x 1,848 features
  was about 5.8 seconds.
- As a sanity check (not a Step 5 formal evaluation, which uses
  `src/evaluation.py`), `.score()` on the scaled train/test data from Step 3
  (`train_years = [2014-2017]`, `test_years = [2018-2021]`) gave:

  | Classifier | Train accuracy | Test accuracy |
  | --- | --- | --- |
  | `logistic_regression` | 0.9815 | 0.6166 |
  | `random_forest` | 0.9959 | 0.6603 |

  The large gap between train and test accuracy is expected here and is the
  data-drift effect the assignment asks about (Step 2); it is not a bug in
  Step 4. Formal precision/recall/F1 evaluation is Step 5's job.
- Confirmed `get_classifier_factories()["logistic_regression"]` returns a new
  object each call (`a is not b`) with equal hyperparameters
  (`a.get_params() == b.get_params()`), and that the fresh instance has no
  `classes_` attribute until fit, matching PLAN.md's testing notes for this
  step.

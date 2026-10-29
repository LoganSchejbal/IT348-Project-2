# Step 5 Report: Evaluation

Written by the builder agent.

## Approach

`src/evaluation.py` scores each Step 4 classifier on the pooled test set
(all test years concatenated, as produced by
`preprocessing.prepare_train_test`), using scikit-learn's `accuracy_score`,
`precision_score`, `recall_score`, and `f1_score`:

- `evaluate_classifier(model, X_test, y_test)` calls `model.predict(X_test)`
  once and returns `{"accuracy", "precision", "recall", "f1"}`. Malware
  (`label == 1`) is the positive class for precision/recall/F1
  (`pos_label=1`), per AGENTS.md. `zero_division=0` is passed so a
  classifier that never predicts malware would score 0.0 on
  precision/recall/F1 instead of raising/warning.
- `evaluate_all(models, X_test, y_test)` runs `evaluate_classifier` for every
  classifier in a dict and returns one row per classifier with a
  `classifier` name column.

Only `.predict()` is called on `X_test`/`y_test` here; nothing in this module
fits a scaler or a model, so Step 5 cannot introduce leakage beyond what
Steps 3-4 already prevent.

## Metrics

Ran the full Step 1-5 pipeline on the real data in `input_data/` (8 years,
2014-2021): `load_all_years` -> `split_years_in_half` (train years
2014-2017, test years 2018-2021) -> `prepare_train_test` -> `get_classifiers`
+ `train_classifiers` -> `evaluate_all`. Results on the pooled test set
(12,000 rows: 2018-2021, 6,000 benign / 6,000 malware):

| Classifier | Accuracy | Precision | Recall | F1-score |
| --- | --- | --- | --- | --- |
| `logistic_regression` | 0.6166 | 0.5762 | 0.8812 | 0.6968 |
| `random_forest` | 0.6603 | 0.5971 | 0.9857 | 0.7437 |

(Data: pooled test set, test years 2018-2021 combined, scaled with the
`StandardScaler` fit on train years 2014-2017 in Step 3; malware = positive
class.)

## Observations

- **Random Forest outperforms Logistic Regression on every metric**,
  including the primary accuracy metric (0.6603 vs. 0.6166) and F1
  (0.7437 vs. 0.6968). This matches the train/test `.score()` sanity check
  already reported in `docs/step4_models.md` (0.6603 vs. 0.6166 test
  accuracy), confirming those two numbers were in fact accuracy.
- **Recall is very high for both classifiers (0.88-0.99) while precision is
  much lower (0.58-0.60).** Both classifiers lean heavily toward predicting
  malware: they catch most real malware (few false negatives) but also flag
  a large share of benign apps as malware (many false positives). Random
  Forest's recall (0.9857) is close to catching every malware sample in the
  test years, but its precision (0.5971) is barely better than guessing on
  a balanced test set, meaning roughly 40% of its "malware" predictions are
  actually benign apps.
- **Why might this be happening:** the train/test split is also the
  drift split (train = 2014-2017, test = 2018-2021), so these are not
  independent-and-identically-distributed train/test sets — API-call
  patterns for both benign and malicious apps in 2018-2021 differ from what
  either model learned on 2014-2017. Step 2's drift analysis
  (`docs/step2_drift_analysis.md`) already shows measurable feature drift
  across these years; the accuracy drop from the ~0.98-0.996 train accuracy
  reported in Step 4 to 0.62-0.66 test accuracy here is consistent with that
  drift degrading both models' ability to separate the two classes on
  unseen years, rather than a bug in this step's metrics.
- **Random Forest's advantage is consistent with Step 4's reasoning for
  choosing it**: as a non-linear ensemble that can model feature
  interactions and is less sensitive to shifts in individual feature
  distributions than a single linear decision boundary, it degrades less
  under drift than Logistic Regression, though neither model is close to
  its training-set performance.
- Per-year performance (how far accuracy drops as the gap between training
  years and the predicted year grows) is deferred to Step 6
  (`evaluate_by_year`), which breaks the pooled test set above into its
  four individual years.

## Verification

- Ran the Step 1-5 pipeline end-to-end against the real CSVs in
  `input_data/` (not synthetic data) via a one-off script calling
  `load_all_years`, `get_feature_columns`, `split_years_in_half`,
  `prepare_train_test`, `get_classifiers`, `train_classifiers`, and
  `evaluate_all`; the table above is copied directly from that script's
  printed output.
- Confirmed `evaluate_all`'s two rows correspond to the two classifier
  names from `get_classifiers()` (`logistic_regression`, `random_forest`)
  and that every metric value is a float in `[0, 1]`.
- Cross-checked `random_forest`'s accuracy (0.6603) against the
  `.score()` value already reported in `docs/step4_models.md` for the same
  `X_test`/`y_test` (0.6603) — they match exactly, confirming
  `evaluate_classifier`'s `accuracy_score` computation agrees with
  scikit-learn's own `.score()`.

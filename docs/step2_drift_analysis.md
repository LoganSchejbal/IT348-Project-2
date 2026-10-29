# Step 2 Report: Data Drift Analysis

Written by the builder agent.

## Method

Drift is measured per feature with the two-sample Kolmogorov-Smirnov (KS)
test (`scipy.stats.ks_2samp`), implemented in `src/drift_analysis.py`. The KS
statistic (range `[0, 1]`) measures the maximum distance between two
samples' empirical CDFs for one feature; larger means the feature's
distribution differs more between the two years being compared.

Two comparisons are run over the 8 discovered years (2014-2021), each with
1,848 features:

1. **Consecutive years** (`compute_drift_across_years`): every feature is
   compared between each pair of adjacent years (2014 vs 2015, 2015 vs
   2016, ..., 2020 vs 2021) — 7 year-pairs x 1,848 features = 12,936 rows.
2. **Earliest vs. latest year** (`compare_earliest_latest_year`): every
   feature compared directly between 2014 and 2021, the single comparison
   with the largest time gap.

These are descriptive statistics only (no scaler or model is fit here), so
computing them does not leak test-year information into any later step —
see PLAN.md's leakage-prevention section.

## Features that drift most

**Top 10 features, consecutive-year pairs** (by KS statistic, from the
12,936-row `compute_drift_across_years` table):

| year_a | year_b | feature | statistic | p_value |
|---|---|---|---|---|
| 2020 | 2021 | `Landroid/content/ContentResolver;.openFileDescriptor(...)` | 0.356 | 1.6e-169 |
| 2018 | 2019 | `Landroid/content/ContentResolver;.query(...)` (5-arg) | 0.352 | 2.4e-165 |
| 2018 | 2019 | `Landroid/content/ContentResolver;.query(...)` (6-arg, w/ CancellationSignal) | 0.337 | 2.7e-151 |
| 2019 | 2020 | `Ljava/lang/String;.valueOf([C)` | 0.317 | 1.3e-133 |
| 2020 | 2021 | `Ljava/lang/System;.loadLibrary(String)` | 0.315 | 3.4e-132 |
| 2015 | 2016 | `Landroid/os/Process;.myPid()` | 0.290 | 2.6e-111 |
| 2020 | 2021 | `Ljava/lang/StringBuilder;.append(CharSequence,int,int)` | 0.289 | 8.6e-111 |
| 2019 | 2020 | `Ljava/lang/System;.loadLibrary(String)` | 0.275 | 1.8e-100 |
| 2020 | 2021 | `Ljava/net/URLConnection;.getOutputStream()` | 0.272 | 8.8e-98 |
| 2015 | 2016 | `Landroid/os/Handler;.obtainMessage(int,int,int,Object)` | 0.271 | 2.7e-97 |

**Top 10 features, earliest (2014) vs. latest (2021) year** — the largest
time gap, which shows much larger statistics since drift accumulates:

| feature | statistic | p_value |
|---|---|---|
| `Landroid/content/ContentResolver;.query(...)` (6-arg) | 0.693 | 0.0 |
| `Landroid/content/ContentResolver;.openFileDescriptor(...)` | 0.670 | 0.0 |
| `Landroid/os/Process;.myPid()` | 0.659 | 0.0 |
| `Ljava/lang/String;.getBytes(Charset)` | 0.642 | 0.0 |
| `Landroid/os/PowerManager$WakeLock;.acquire(long)` | 0.627 | 0.0 |
| `Landroid/content/Context;.getApplicationInfo()` | 0.616 | 0.0 |
| `Landroid/os/Handler;.obtainMessage(int,int,int,Object)` | 0.610 | 0.0 |
| `Landroid/app/NotificationManager;.notify(String,int,Notification)` | 0.593 | 0.0 |
| `Landroid/os/Handler;.obtainMessage(int,int,int)` | 0.590 | 0.0 |
| `Ljava/lang/String;.valueOf(Object)` | 0.570 | 0.0 |

The full top-20 tables (consecutive pairs and earliest-vs-latest) are
produced by `top_drifting_features` and can be regenerated with
`python -m src.main`. Reported p-values of `0.0` are values smaller than
floating-point precision can represent given the 3,000-row sample sizes,
not literal zero.

Many of the most-drifting features involve content resolution
(`ContentResolver`), native library loading, and `WakeLock`/notification
APIs — consistent with Android's permission and API surface changing
substantially between 2014 and 2021 (e.g., scoped storage, background
execution limits), which affects how both benign and malicious apps call
these APIs.

## Years that differ most

**Consecutive year pairs**, ranked by mean KS statistic across all 1,848
features (`most_different_year_pairs`):

| year_a | year_b | mean_statistic | max_statistic |
|---|---|---|---|
| 2020 | 2021 | 0.0300 | 0.356 |
| 2018 | 2019 | 0.0175 | 0.352 |
| 2015 | 2016 | 0.0158 | 0.290 |
| 2016 | 2017 | 0.0157 | 0.179 |
| 2019 | 2020 | 0.0142 | 0.317 |
| 2014 | 2015 | 0.0138 | 0.263 |
| 2017 | 2018 | 0.0135 | 0.270 |

The 2020-2021 transition drifts the most on average, followed by
2018-2019. No consecutive pair is close to zero drift, so feature drift is
present throughout the dataset's 8-year span, not just at its edges.

**Earliest vs. latest year (2014 vs. 2021):** mean KS statistic across all
features is 0.0524 and the max is 0.693 (`Landroid/content/ContentResolver;.query`,
6-arg overload) — both well above any single consecutive-year mean, which
confirms that drift compounds over time rather than resetting each year.

## What this means for the models

- Feature drift is real and measurable throughout 2014-2021, so a model
  trained once on early years and evaluated on later years (the Step 3
  train/test split) should be expected to lose accuracy as the gap between
  training and test year grows — this is exactly what Step 6 checks.
- The features that drift most are concentrated in a relatively small set
  of Android system APIs (content resolution, native libraries,
  power/notification management) rather than being spread evenly across
  all 1,848 features. This suggests a model that leans heavily on a few
  of these high-drift features for its decisions is more exposed to drift
  than one that spreads its weight across many stable features — a point
  worth revisiting when comparing Logistic Regression vs. Random Forest in
  Step 5.
- Because drift keeps accumulating year over year (2014 vs. 2021 has a
  higher mean and max statistic than any single consecutive pair), a
  "train once, never retrain" approach is unlikely to be sustainable over
  the full 8-year span, motivating the periodic-retraining comparison in
  Step 7.

# Step 1 Report: Prepare the Data

Written by the builder agent.

## Files loaded

`src/data_loader.py` discovers files at run time with `discover_dataset_files`
(glob `sampled_*_api.csv`) rather than hard-coding years. Running it against
`input_data/` found 16 files, one `benign` and one `malware` file for each of
8 years: 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021.

## Shape after dropping the first column

Every file has 1849 columns before loading; `load_single_file` drops the
first column (`apkname`, an app identifier, not a feature), leaving 1848
feature columns plus the added `label` and `year` columns. Row counts per
file are now **uniform across years** after truncation (see Issues found
below):

| Year | Benign rows | Malware rows | Combined rows (`load_year_data`) | Feature columns |
|------|-------------|--------------|-----------------------------------|------------------|
| 2014 | 1500 | 1500 | 3000 | 1848 |
| 2015 | 1500 | 1500 | 3000 | 1848 |
| 2016 | 1500 | 1500 | 3000 | 1848 |
| 2017 | 1500 | 1500 | 3000 | 1848 |
| 2018 | 1500 | 1500 | 3000 | 1848 |
| 2019 | 1500 | 1500 | 3000 | 1848 |
| 2020 | 1500 | 1500 | 3000 | 1848 |
| 2021 | 1500 | 1500 | 3000 | 1848 |

`load_all_years` returns one dataframe per discovered year (8 entries),
matching this table; combined across all years that is 24000 rows total.

## Class counts per year

| Year | Malware (label=1) | Benign (label=0) |
|------|--------------------|-------------------|
| 2014 | 1500 | 1500 |
| 2015 | 1500 | 1500 |
| 2016 | 1500 | 1500 |
| 2017 | 1500 | 1500 |
| 2018 | 1500 | 1500 |
| 2019 | 1500 | 1500 |
| 2020 | 1500 | 1500 |
| 2021 | 1500 | 1500 |

Every year is exactly balanced (50% malware / 50% benign); counts were
verified with `df["label"].value_counts()` on each year's combined dataframe.

## Issues found

AGENTS.md states each file has 1,500 rows, but the raw CSVs for 2014-2018
actually have 9,000 rows each (1,849 columns matches AGENTS.md in every
file, so only the row count differs). This was confirmed directly against
the CSVs (`wc -l` on each file, one less than the printed line count for the
header), not just through the loader.

`load_single_file` now truncates any file with more than 1,500 rows down to
its first 1,500 rows (deterministic, not a random sample), after warning
about the shape mismatch. This keeps every year's contribution to the
pooled dataset equal to the documented sample size (1,500 benign + 1,500
malware), instead of letting 2014-2018 outweigh 2019-2021 five to one in
later training steps.

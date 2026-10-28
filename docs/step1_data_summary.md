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
file are **not uniform across years** (see Issues found below):

| Year | Benign rows | Malware rows | Combined rows (`load_year_data`) | Feature columns |
|------|-------------|--------------|-----------------------------------|------------------|
| 2014 | 9000 | 9000 | 18000 | 1848 |
| 2015 | 9000 | 9000 | 18000 | 1848 |
| 2016 | 9000 | 9000 | 18000 | 1848 |
| 2017 | 9000 | 9000 | 18000 | 1848 |
| 2018 | 9000 | 9000 | 18000 | 1848 |
| 2019 | 1500 | 1500 | 3000 | 1848 |
| 2020 | 1500 | 1500 | 3000 | 1848 |
| 2021 | 1500 | 1500 | 3000 | 1848 |

`load_all_years` returns one dataframe per discovered year (8 entries),
matching this table; combined across all years that is 99000 rows total.

## Class counts per year

| Year | Malware (label=1) | Benign (label=0) |
|------|--------------------|-------------------|
| 2014 | 9000 | 9000 |
| 2015 | 9000 | 9000 |
| 2016 | 9000 | 9000 |
| 2017 | 9000 | 9000 |
| 2018 | 9000 | 9000 |
| 2019 | 1500 | 1500 |
| 2020 | 1500 | 1500 |
| 2021 | 1500 | 1500 |

Every year is exactly balanced (50% malware / 50% benign); counts were
verified with `df["label"].value_counts()` on each year's combined dataframe.

## Issues found

AGENTS.md states each file has 1,500 rows, but the real files for 2014-2018
have 9,000 rows each (1,849 columns matches AGENTS.md in every file, so only
the row count differs). This was confirmed directly against the CSVs (`wc -l`
on each file, one less than the printed line count for the header), not just
through the loader. The loader itself makes no assumption about row count —
`load_year_data`/`load_all_years` work correctly regardless of how many rows
each file has — so this does not require a code change, only a note that the
2014-2018 years contribute far more rows than 2019-2021 to the pooled
training set used in later steps.

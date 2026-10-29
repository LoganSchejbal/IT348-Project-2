# Step 1 Review: Prepare the Data

- Reviewer transcript: transcripts/05_2026-10-28_reviewer_step1.md
- What was reviewed: the diff from step1-start to the latest commit (src/data_loader.py, src/__init__.py)

## Comments (reviewer)

One row per issue. Number the rows 1, 2, 3, ...

| # | Severity | Location | Issue | Suggested fix |
| --- | --- | --- | --- | --- |
| 1 | Medium | `src/data_loader.py`, `load_single_file` (the `df.assign(label=..., year=...)` call) | If any of the 1,848 original feature columns happens to be named `label` or `year`, `df.assign` silently overwrites it instead of raising an error, and `get_feature_columns` would then silently drop a real feature (or never see the collision). There is no check that these two names are free before they are added. | Before assigning, check `if "label" in df.columns or "year" in df.columns: raise ValueError(...)` (or pick column names that cannot collide, e.g. `_label`/`_year`), so a collision fails loudly instead of corrupting the feature set. |
| 2 | Low | `src/data_loader.py`, `extract_label_from_filename` vs `_extract_year_from_filename` | The two filename parsers are inconsistent about case: `extract_label_from_filename` lowercases the filename before checking for `benign`/`malware`, but `_extract_year_from_filename`'s regex is matched against the filename as-is and only accepts lowercase `benign`/`malware` tokens. A filename with different casing (e.g. `Sampled_2014_Malware_api.csv`) would get a label successfully but then raise `ValueError` when the year is parsed in the same `load_single_file` call, which is a confusing failure mode since one half of the parsing "worked." | Lowercase consistently in both functions (or document that the naming scheme is always lowercase and drop the `.lower()` in `extract_label_from_filename` instead, so both functions make the same assumption). |
| 3 | Low | `src/data_loader.py`, `load_single_file` / `load_year_data` | AGENTS.md/ASSIGNMENT.md specify that each file should have 1,500 rows and 1,849 columns before the drop, and the per-step report is supposed to call out "anomalies (missing files, unexpected row/column counts)." Nothing in the loading code actually checks this — a file with the wrong shape loads silently and the anomaly would only surface if someone manually inspects the resulting dataframe when writing the report. | Add a lightweight shape check in `load_single_file` (e.g. assert/log if `df.shape` isn't `(1500, 1849)` before the drop) so anomalies are caught automatically at load time rather than relying on manual inspection when writing `docs/step1_data_summary.md`. |

## Decision log (student)

One row per comment above, with the same number. Decision is Accepted or Rejected. For accepted comments, add the commit that fixed it.

| # | Decision | Reason | Fixed in commit |
| --- | --- | --- | --- |
| 1 | Accepted | Need to warn when there is an issue | 4d40562 |
| 2 | Accepted | Should account for this issue | 4d40562 | 
| 3 | Accepted | Should validate | 4d40562 |

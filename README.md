# Project 2: Malware Classification Under Data Drift

This program was fully coded by AI. The program itself takes a given dataset over an unspecified span of years and uses machine learning algorithms to identify malicious android applications. The project evaluates API calls between benign and malicious applications to make this determination.

This repository was built with the Project 2 harness. See HARNESS.md for how the builder, reviewer, and tester agents were run.

## Agents used

| Role | Tool | Model |
| --- | --- | --- |
| Builder | Claude Code | Sonnet 5 |
| Reviewer | Claude Code | Sonnet 5 |
| Tester | Claude Code | Sonnet 5 |

## How to run

1. Install packages: `pip install -r requirements.txt`
2. Put the dataset files in `input_data/`.
3. Run the program: `python -m src.main`
4. Run all tests: `python harness.py test all`

## Results

The most effective model was overwhelmingly random forest for each model. The data shows that the majority of malignant applications were caught; however, there was a relatively high amount of false positives. When looking at the year-by-year evaluations, the models preform well on the datasets up until 2019 when the accuracy dips to just above 50%. This is also where false positives begin to see a rise. The full results and analysis can be found in [Step 5 Evaluation](docs/step5_evaluation.md) and [Step 6 Evaluation-by-Year](docs/step6_test_results.md).

## Hand-written code

None

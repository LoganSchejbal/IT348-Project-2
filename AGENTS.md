# AGENTS.md: Project 2 context for all agents

Every agent (builder, reviewer, tester) reads this file first. Fill in the [TODO] parts before Step 0. Keep it short and specific.

## Project goal

Classify Android apps as malware or goodware from their API-call features, and find a sustainable approach that stays accurate as the data drifts over 8 years. The full assignment is in ASSIGNMENT.md.

## Dataset

- Location: input_data/ (not committed to git).
- The dataset files follow the naming scheme of "sampled_[year]_[class]_api.csv", where year is replaced with the year and class is replaced with either benign or malware "sampled_2014_benign_api.csv".
- Each file has 1,500 rows and 1,849 columns. The first column must be dropped; the other 1,848 columns are API-call features.
- Label: The model should label malware with the code "1" and benign or goodware as "0".

## Folder layout

- src/: project code (builder only).
- tests/: pytest tests test_stepN_*.py and test logs stepN_test_log.md (tester only; the student adds failure decisions).
- docs/: one builder report per step.
- reviews/: one review report per step (reviewer writes comments; student writes the decision log).
- transcripts/: saved agent sessions (saved by the harness; agents never edit these).
- PLAN.md: the plan for Steps 1-7. REPORT.md and REFLECTION.md: written by the student.

## Coding conventions

- Python 3, pandas, numpy, scikit-learn, scipy. No other libraries without asking.
- All code must be documented whenever new code is generated. Each method and class should have a docstring following the common format and information included, like a description, parameter values and explanations, and return values.
- Inside the method, code blocks should always have in-depth descriptors, labels, or explanations of the code unless it is trivial. The idea is that code reviewers should be able to quickly and easily understand what is happening.
- All code should be decoupled and modular. Code should follow typical standards and changing one thing should generally not cause more changes to occur whenever possible. 
- Code should not hard-code possible datasets or other information and should instead be determined at the time of running
- Train/test split is by year. Anything fit to data (scalers, feature selection, models) is fit on training years only.
- Malware is the positive class for precision, recall, and F1.

## How to run

- To run the project, enter the command python -m src.main
- Tests: python harness.py test N (one step) or python harness.py test all.

## Commit rules

Every commit message starts with a role tag: [builder], [reviewer], [tester], or [student]. A git hook rejects other messages. Make small commits, one per task. Never rewrite or squash history.

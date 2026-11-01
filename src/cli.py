"""Console argument parsing for the Post Step 7 driver.

Owns the console interface only: this module never imports pandas,
scikit-learn, or any Step 1-7 function from `src/`, so changes to the set
of console flags never touch orchestration code in `src/main.py`, and vice
versa (see PLAN.md's "Post Step 7: Project adjustments" section).
"""

import argparse

# Every Step 1-7 function family reachable individually from the console,
# plus "all" to run the full pipeline (the default, matching AGENTS.md's
# documented `python -m src.main`).
STEP_CHOICES = (
    "all",
    "load",
    "drift",
    "preprocess",
    "train",
    "evaluate",
    "evaluate-by-year",
    "sustainable",
)


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the console argument parser for the project driver.

    Returns:
        An `argparse.ArgumentParser` with two options:
        - `--data-dir` (default `"input_data"`): the dataset directory,
          so the dataset location is determined at run time rather than
          hard-coded, per AGENTS.md.
        - `--step` (default `"all"`, restricted to `STEP_CHOICES`): which
          Step 1-7 function family to run.
    """
    parser = argparse.ArgumentParser(
        description="Run the Android malware classification pipeline (Steps 1-7).",
    )
    parser.add_argument(
        "--data-dir",
        default="input_data",
        help="Directory containing the 'sampled_<year>_<class>_api.csv' files "
        "(default: input_data).",
    )
    parser.add_argument(
        "--step",
        choices=STEP_CHOICES,
        default="all",
        help="Which step to run (default: all).",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse console arguments.

    Kept separate from `build_arg_parser` so tests can call this directly
    with an explicit list of strings instead of patching `sys.argv`.

    Args:
        argv: Argument strings to parse, or `None` to parse `sys.argv[1:]`.

    Returns:
        The parsed `argparse.Namespace` with `data_dir` and `step` fields.
    """
    return build_arg_parser().parse_args(argv)

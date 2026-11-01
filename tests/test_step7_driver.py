"""Tests for the Post Step 7 console driver (src/cli.py, src/main.py).

These tests check what PLAN.md's "Post Step 7: Project adjustments" section
says the driver should do: `parse_args` only accepts the fixed `--step`
choices; each `ensure_*` helper in `src/main.py` is a no-op once its
`PipelineContext` fields are already set; `ensure_data_loaded` raises
`FileNotFoundError` (and never reaches `load_all_years`) for a missing or
empty `--data-dir`; `run_step1_load`/`run_step3_preprocess`/
`run_step4_train` each return a single `pd.DataFrame`; `run_selected_step`
with `"all"` computes every prerequisite exactly once even though several
steps depend on it; and `main([])` runs the full pipeline with no
arguments, matching AGENTS.md's documented `python -m src.main`.

All tests use a small synthetic dataset (a few rows/features, 4 years)
built with the `tmp_path` fixture so they run in seconds and never touch
input_data/.
"""

import math

import pandas as pd
import pytest

from src.cli import STEP_CHOICES, build_arg_parser, parse_args
from src.main import (
    PipelineContext,
    ensure_data_loaded,
    ensure_preprocessed,
    ensure_trained,
    main,
    run_selected_step,
    run_step1_load,
    run_step3_preprocess,
    run_step4_train,
)

# Years/row counts kept tiny so the full pipeline (scaling, training,
# retraining in Step 7) runs in well under a second.
_YEARS = [2014, 2015, 2016, 2017]
_ROWS_PER_CLASS = 4
_FEATURE_COLS = ["api_call_a", "api_call_b", "api_call_c"]


def _make_dataset_dir(tmp_path, years=_YEARS):
    """Write a tiny synthetic dataset directory following the project's
    `sampled_<year>_<class>_api.csv` naming scheme.

    Args:
        tmp_path: pytest's per-test temporary directory fixture.
        years: Years to generate benign/malware files for.

    Returns:
        The `tmp_path` the files were written into.
    """
    for year in years:
        for class_name, label in (("benign", 0), ("malware", 1)):
            rows = []
            for i in range(_ROWS_PER_CLASS):
                row = {"app_id": f"{class_name}_{year}_{i}"}
                row.update({col: float((i + label) % 3) for col in _FEATURE_COLS})
                rows.append(row)
            df = pd.DataFrame(rows)
            df.to_csv(tmp_path / f"sampled_{year}_{class_name}_api.csv", index=False)
    return tmp_path


# --- parse_args rejects a --step value outside the fixed set


def test_parse_args_rejects_unknown_step():
    """An unrecognized --step value must cause argparse to error out
    (SystemExit), not silently fall through to some default behavior."""
    with pytest.raises(SystemExit):
        parse_args(["--step", "not-a-real-step"])


def test_parse_args_accepts_every_documented_step_choice():
    """Every choice PLAN.md documents (all, load, drift, preprocess,
    train, evaluate, evaluate-by-year, sustainable) must be accepted."""
    for step in STEP_CHOICES:
        args = parse_args(["--step", step])
        assert args.step == step


def test_parse_args_defaults_to_all_and_input_data():
    """With no arguments, --step defaults to 'all' and --data-dir defaults
    to 'input_data', per PLAN.md and AGENTS.md's documented run command."""
    args = parse_args([])
    assert args.step == "all"
    assert args.data_dir == "input_data"


def test_build_arg_parser_step_choices_match_step_choices_constant():
    """The parser's --step choices must be exactly STEP_CHOICES, so adding
    a step to one place can't silently drift from the other."""
    parser = build_arg_parser()
    step_action = next(a for a in parser._actions if a.dest == "step")
    assert set(step_action.choices) == set(STEP_CHOICES)


# --- ensure_data_loaded error prevention for a missing/empty data_dir


def test_ensure_data_loaded_raises_for_nonexistent_data_dir(tmp_path):
    """A --data-dir that does not exist at all must raise FileNotFoundError
    with a message that points back at --data-dir, not a stack trace from
    deep inside a later step."""
    missing_dir = tmp_path / "does_not_exist"
    context = PipelineContext(data_dir=str(missing_dir))

    with pytest.raises(FileNotFoundError, match="--data-dir"):
        ensure_data_loaded(context)

    assert context.year_data is None


def test_ensure_data_loaded_raises_for_empty_data_dir(tmp_path):
    """A --data-dir that exists but has no sampled_*_api.csv files must
    also raise FileNotFoundError, per PLAN.md (glob alone would silently
    return an empty list instead of failing loudly)."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    context = PipelineContext(data_dir=str(empty_dir))

    with pytest.raises(FileNotFoundError):
        ensure_data_loaded(context)


def test_ensure_data_loaded_never_calls_load_all_years_for_empty_dir(tmp_path, monkeypatch):
    """load_all_years must not even be reached when the data_dir check
    fails -- not just that an exception eventually surfaces."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    context = PipelineContext(data_dir=str(empty_dir))

    def _fail_if_called(*args, **kwargs):
        raise AssertionError("load_all_years must not be called for an empty data_dir")

    monkeypatch.setattr("src.main.load_all_years", _fail_if_called)

    with pytest.raises(FileNotFoundError):
        ensure_data_loaded(context)


# --- ensure_* helpers are no-ops once their fields are already set


def test_ensure_data_loaded_is_a_noop_once_year_data_is_set():
    """If context.year_data is already populated, ensure_data_loaded must
    not recompute it (and must not even need a real data_dir)."""
    sentinel = {2020: pd.DataFrame({"f1": [0.0], "label": [0], "year": [2020]})}
    context = PipelineContext(data_dir="this/path/does/not/exist", year_data=sentinel)

    ensure_data_loaded(context)

    assert context.year_data is sentinel


def test_ensure_preprocessed_is_a_noop_once_x_train_is_set():
    """If context.X_train is already populated, ensure_preprocessed must
    not recompute it (and must not even need year_data to be set)."""
    sentinel = object()
    context = PipelineContext(X_train=sentinel)

    ensure_preprocessed(context)

    assert context.X_train is sentinel


def test_ensure_trained_is_a_noop_once_classifiers_are_set():
    """If context.classifiers is already populated, ensure_trained must
    not recompute it (and must not even need X_train to be set)."""
    sentinel = {"fake": object()}
    context = PipelineContext(classifiers=sentinel)

    ensure_trained(context)

    assert context.classifiers is sentinel


def test_ensure_preprocessed_does_not_reload_already_loaded_data(tmp_path, monkeypatch):
    """ensure_preprocessed must call ensure_data_loaded (a no-op here)
    rather than skip prerequisite checking entirely, but once year_data is
    set it must not re-trigger a full reload from disk."""
    _make_dataset_dir(tmp_path)
    context = PipelineContext(data_dir=str(tmp_path))
    ensure_data_loaded(context)
    loaded_year_data = context.year_data

    def _fail_if_called(*args, **kwargs):
        raise AssertionError("load_all_years must not be called again")

    monkeypatch.setattr("src.main.load_all_years", _fail_if_called)

    ensure_preprocessed(context)

    assert context.year_data is loaded_year_data
    assert context.X_train is not None


# --- run_step1_load / run_step3_preprocess / run_step4_train each return
# a single pd.DataFrame


def test_run_step1_load_returns_a_single_dataframe(tmp_path):
    """run_step1_load must return one pd.DataFrame summarizing every
    loaded year (so format_dataframe_for_console can render it)."""
    _make_dataset_dir(tmp_path)
    context = PipelineContext(data_dir=str(tmp_path))

    result = run_step1_load(context)

    assert isinstance(result, pd.DataFrame)
    assert set(result["year"]) == set(_YEARS)


def test_run_step3_preprocess_returns_a_single_dataframe(tmp_path):
    """run_step3_preprocess must return one pd.DataFrame with a train row
    and a test row."""
    _make_dataset_dir(tmp_path)
    context = PipelineContext(data_dir=str(tmp_path))

    result = run_step3_preprocess(context)

    assert isinstance(result, pd.DataFrame)
    assert set(result["split"]) == {"train", "test"}


def test_run_step4_train_returns_a_single_dataframe(tmp_path):
    """run_step4_train must return one pd.DataFrame with one row per
    classifier."""
    _make_dataset_dir(tmp_path)
    context = PipelineContext(data_dir=str(tmp_path))

    result = run_step4_train(context)

    assert isinstance(result, pd.DataFrame)
    assert len(result) >= 2  # at least the two classifiers from Step 4


# --- run_selected_step("all") populates every field exactly once


def test_run_selected_step_all_populates_context_exactly_once(tmp_path, monkeypatch, capsys):
    """Running every step should compute each prerequisite exactly once,
    even though train/evaluate/evaluate-by-year/sustainable all depend on
    the same loaded/preprocessed/trained data."""
    _make_dataset_dir(tmp_path)
    context = PipelineContext(data_dir=str(tmp_path))

    call_counts = {"load_all_years": 0, "prepare_train_test": 0, "train_classifiers": 0}

    import src.main as main_module

    original_load_all_years = main_module.load_all_years
    original_prepare_train_test = main_module.prepare_train_test
    original_train_classifiers = main_module.train_classifiers

    def _counting_load_all_years(*args, **kwargs):
        call_counts["load_all_years"] += 1
        return original_load_all_years(*args, **kwargs)

    def _counting_prepare_train_test(*args, **kwargs):
        call_counts["prepare_train_test"] += 1
        return original_prepare_train_test(*args, **kwargs)

    def _counting_train_classifiers(*args, **kwargs):
        call_counts["train_classifiers"] += 1
        return original_train_classifiers(*args, **kwargs)

    monkeypatch.setattr(main_module, "load_all_years", _counting_load_all_years)
    monkeypatch.setattr(main_module, "prepare_train_test", _counting_prepare_train_test)
    monkeypatch.setattr(main_module, "train_classifiers", _counting_train_classifiers)

    run_selected_step(context, "all")

    assert call_counts["load_all_years"] == 1
    assert call_counts["prepare_train_test"] == 1
    assert call_counts["train_classifiers"] == 1


def test_run_selected_step_single_step_only_runs_that_step(tmp_path, capsys):
    """Requesting a single step (e.g. "load") must print only that step's
    header, not every step's."""
    _make_dataset_dir(tmp_path)
    context = PipelineContext(data_dir=str(tmp_path))

    run_selected_step(context, "load")

    out = capsys.readouterr().out
    assert "=== load ===" in out
    assert "=== train ===" not in out


# --- main([]) runs the full pipeline with no arguments


def test_main_with_no_arguments_runs_full_pipeline(tmp_path, monkeypatch, capsys):
    """main([]) must default to --data-dir=input_data and --step=all,
    matching AGENTS.md's documented `python -m src.main`. Since this test
    cannot touch the real input_data/, it monkeypatches the default via
    chdir into a tmp_path that has its own input_data/ directory."""
    data_dir = tmp_path / "input_data"
    data_dir.mkdir()
    _make_dataset_dir(data_dir)
    monkeypatch.chdir(tmp_path)

    main([])

    out = capsys.readouterr().out
    for step_name in ("load", "drift", "preprocess", "train", "evaluate", "evaluate-by-year", "sustainable"):
        assert f"=== {step_name} ===" in out


def test_main_with_explicit_step_runs_only_that_step(tmp_path, monkeypatch, capsys):
    """main() must thread --step through to run_selected_step correctly."""
    monkeypatch.chdir(tmp_path)
    data_dir = tmp_path / "custom_data"
    _make_dataset_dir(data_dir)

    main(["--data-dir", str(data_dir), "--step", "load"])

    out = capsys.readouterr().out
    assert "=== load ===" in out
    assert "=== train ===" not in out


# --- integration smoke test on the real dataset, when present


def test_full_pipeline_on_real_dataset(real_data_dir):
    """End-to-end sanity check against the real data: running every step
    must not raise and must produce metrics in [0, 1] for Step 5."""
    context = PipelineContext(data_dir=str(real_data_dir))

    run_selected_step(context, "all")

    assert context.year_data is not None
    assert context.classifiers is not None
    for name, model in context.classifiers.items():
        from src.evaluation import evaluate_classifier

        metrics = evaluate_classifier(model, context.X_test, context.y_test)
        for value in metrics.values():
            assert 0.0 <= value <= 1.0 or math.isclose(value, 0.0) or math.isclose(value, 1.0)

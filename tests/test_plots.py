import json

from kidextract.evaluation.plots import axis_value, group_by_axis, load_results

RESULTS = [
    {"name": "baseline", "overrides": {}, "eval_loss": 0.5, "trainable_parameters": 4884480},
    {"name": "r=4", "overrides": {"lora.r": 4}, "eval_loss": 0.6, "trainable_parameters": 1221120},
    {"name": "r=64", "overrides": {"lora.r": 64}, "eval_loss": 0.45, "trainable_parameters": 19537920},
    {
        "name": "target_modules=q-v",
        "overrides": {"lora.target_modules": ["q_proj", "v_proj"]},
        "eval_loss": 0.7,
        "trainable_parameters": 811008,
    },
]


def test_grouping_puts_the_baseline_in_every_axis():
    groups = group_by_axis(RESULTS)
    assert set(groups) == {"lora.r", "lora.target_modules"}
    assert all(any(r["name"] == "baseline" for r in records) for records in groups.values())


def test_rank_axis_collects_all_its_points():
    assert len(group_by_axis(RESULTS)["lora.r"]) == 3


def test_axis_value_renders_module_lists_compactly():
    record = RESULTS[3]
    assert axis_value(record, "lora.target_modules", "baseline") == "q+v"


def test_axis_value_falls_back_for_the_baseline():
    assert axis_value(RESULTS[0], "lora.r", 16) == "16"


def test_load_results_round_trip(tmp_path):
    path = tmp_path / "results.json"
    path.write_text(json.dumps(RESULTS))
    assert len(load_results(path)) == 4


def test_plot_sweep_writes_files(tmp_path):
    import pytest

    pytest.importorskip("matplotlib")
    from kidextract.evaluation.plots import plot_sweep

    results = tmp_path / "results.json"
    results.write_text(json.dumps(RESULTS))
    written = plot_sweep(results, tmp_path / "figures")
    assert written and all(path.exists() for path in written)

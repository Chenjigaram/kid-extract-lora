from pathlib import Path

import pytest
import yaml

from kidextract.train.config import ExperimentConfig, load_config
from kidextract.train.sweep import expand_axes, expand_grid, plan_points, slugify, sweep_table

CONFIGS = sorted(Path("configs").glob("*.yaml"))


def test_defaults_are_usable_without_a_file():
    config = load_config()
    assert config.model.name.startswith("HuggingFaceTB/")
    assert config.lora.r > 0


@pytest.mark.parametrize("path", [p for p in CONFIGS if p.name != "sweep.yaml"], ids=lambda p: p.name)
def test_shipped_configs_load(path):
    config = load_config(path)
    assert isinstance(config, ExperimentConfig)
    assert config.model.max_seq_length >= 512


def test_overrides_are_applied_and_typed():
    config = load_config(Path("configs/base.yaml"), {"lora.r": 8, "output.dir": "runs/x"})
    assert config.lora.r == 8
    assert config.output.dir == Path("runs/x")


def test_unknown_option_is_rejected():
    with pytest.raises(ValueError):
        load_config(Path("configs/base.yaml"), {"lora.nonexistent": 1})


def test_unknown_section_is_rejected():
    with pytest.raises(ValueError):
        load_config(Path("configs/base.yaml"), {"nonexistent.value": 1})


def test_config_serialises_paths_as_strings():
    payload = load_config(Path("configs/base.yaml")).to_dict()
    assert isinstance(payload["output"]["dir"], str)


def test_slugify_handles_lists_and_floats():
    assert slugify(["q_proj", "v_proj"]) == "q-v"
    assert slugify(0.05) == "0p05"


def test_axis_expansion_drops_points_equal_to_the_baseline():
    points = expand_axes({"lora.r": 16}, {"lora.r": [8, 16, 32]})
    names = [point["name"] for point in points]
    assert names == ["baseline", "r=8", "r=32"]


def test_grid_expansion_is_the_cartesian_product():
    points = expand_grid({"lora.r": [4, 8], "training.epochs": [1, 2]})
    assert len(points) == 4


def test_shipped_sweep_plan_is_deduplicated():
    spec = yaml.safe_load(Path("configs/sweep.yaml").read_text())
    names = [point["name"] for point in plan_points(spec)]
    assert names[0] == "baseline"
    assert len(names) == len(set(names))


def test_sweep_table_sorts_by_score():
    rows = [
        {"name": "a", "micro_f1": 0.5, "eval_loss": 1.0},
        {"name": "b", "micro_f1": 0.9, "eval_loss": 0.5},
    ]
    table = sweep_table(rows)
    assert table.index("| b ") < table.index("| a ")

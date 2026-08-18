from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ModelConfig:
    name: str = "HuggingFaceTB/SmolLM2-135M-Instruct"
    max_seq_length: int = 1408


@dataclass
class LoraConfig:
    r: int = 16
    alpha: int = 32
    dropout: float = 0.05
    target_modules: list[str] = field(
        default_factory=lambda: ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    )


@dataclass
class TrainingConfig:
    epochs: float = 2
    learning_rate: float = 2e-4
    batch_size: int = 1
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 3
    weight_decay: float = 0.0
    lr_scheduler: str = "cosine"
    logging_steps: int = 20
    eval_steps: int = 200
    save_steps: int = 400
    seed: int = 42


@dataclass
class DataConfig:
    dir: Path = Path("data/processed")
    train_file: str = "train.jsonl"
    validation_file: str = "validation.jsonl"
    max_train_samples: int | None = None
    max_eval_samples: int | None = 200


@dataclass
class OutputConfig:
    dir: Path = Path("runs/default")


@dataclass
class ExperimentConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    lora: LoraConfig = field(default_factory=LoraConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": vars(self.model),
            "lora": vars(self.lora),
            "training": vars(self.training),
            "data": {**vars(self.data), "dir": str(self.data.dir)},
            "output": {"dir": str(self.output.dir)},
        }


def _merge(section: dict[str, Any] | None, target: Any) -> Any:
    for key, value in (section or {}).items():
        if not hasattr(target, key):
            raise ValueError(f"unknown option {key!r} for {type(target).__name__}")
        setattr(target, key, value)
    return target


def load_config(path: Path | None = None, overrides: dict[str, Any] | None = None) -> ExperimentConfig:
    raw: dict[str, Any] = {}
    if path is not None:
        raw = yaml.safe_load(path.read_text()) or {}
    config = ExperimentConfig()
    _merge(raw.get("model"), config.model)
    _merge(raw.get("lora"), config.lora)
    _merge(raw.get("training"), config.training)
    _merge(raw.get("data"), config.data)
    _merge(raw.get("output"), config.output)
    config.data.dir = Path(config.data.dir)
    config.output.dir = Path(config.output.dir)

    for dotted, value in (overrides or {}).items():
        section, _, option = dotted.partition(".")
        if not option or not hasattr(config, section):
            raise ValueError(f"unknown override {dotted!r}")
        _merge({option: value}, getattr(config, section))
    config.data.dir = Path(config.data.dir)
    config.output.dir = Path(config.output.dir)
    return config

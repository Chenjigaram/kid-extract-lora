from __future__ import annotations

import itertools
import json
import time
from pathlib import Path
from typing import Any

import yaml

from ..evaluation.runner import evaluate_system, json_text_extractor
from .config import load_config
from .lora import run as run_training


def slugify(value: Any) -> str:
    if isinstance(value, list):
        return "-".join(str(item).replace("_proj", "") for item in value)
    return str(value).replace(".", "p")


def expand_axes(base: dict[str, Any], axes: dict[str, list]) -> list[dict[str, Any]]:
    points = [{"name": "baseline", "overrides": {}}]
    seen = {json.dumps(base, sort_keys=True, default=str)}
    for option, values in axes.items():
        for value in values:
            candidate = {**base, option: value}
            key = json.dumps(candidate, sort_keys=True, default=str)
            if key in seen:
                continue
            seen.add(key)
            points.append({"name": f"{option.split('.')[-1]}={slugify(value)}", "overrides": {option: value}})
    return points


def expand_grid(axes: dict[str, list]) -> list[dict[str, Any]]:
    options = list(axes)
    points = []
    for combination in itertools.product(*(axes[option] for option in options)):
        overrides = dict(zip(options, combination))
        name = ",".join(f"{option.split('.')[-1]}={slugify(value)}" for option, value in overrides.items())
        points.append({"name": name, "overrides": overrides})
    return points


def plan_points(spec: dict) -> list[dict[str, Any]]:
    axes = spec["axes"]
    if spec.get("mode", "axes") == "grid":
        return expand_grid(axes)
    base_config = load_config(Path(spec["base"]))
    base = {}
    for option in axes:
        section, _, name = option.partition(".")
        base[option] = getattr(getattr(base_config, section), name)
    return expand_axes(base, axes)


def run_point(spec: dict, point: dict, threads: int | None, skip_generation: bool) -> dict:
    output_dir = Path(spec["output_dir"]) / point["name"].replace("/", "_")
    overrides = dict(point["overrides"])
    overrides["output.dir"] = str(output_dir)
    if spec.get("train_samples"):
        overrides["data.max_train_samples"] = spec["train_samples"]

    config = load_config(Path(spec["base"]), overrides)
    started = time.time()
    summary = run_training(config, threads=threads)
    record = {
        "name": point["name"],
        "overrides": point["overrides"],
        "train_loss": summary["train_loss"],
        "eval_loss": summary["eval_loss"],
        "trainable_parameters": summary["trainable_parameters"],
        "trainable_fraction": summary["trainable_fraction"],
        "train_runtime_seconds": summary["train_runtime_seconds"],
    }

    if not skip_generation:
        from ..evaluation.hf_model import CausalExtractor

        model = CausalExtractor(config.model.name, adapter=output_dir / "adapter", threads=threads)
        result = evaluate_system(
            point["name"],
            Path(spec["eval_split"]),
            json_text_extractor(model.generate),
            limit=spec.get("eval_documents"),
        )
        scores = result.summary()
        record.update(
            {
                "micro_f1": scores["micro_f1"],
                "macro_f1": scores["macro_f1"],
                "exact_match": scores["exact_match"],
                "schema_validity": scores["schema_validity"],
                "hallucination_rate": scores["hallucination_rate"],
                "median_latency_seconds": scores["median_latency_seconds"],
            }
        )
    record["total_seconds"] = round(time.time() - started, 1)
    return record


def run_sweep(
    spec_path: Path,
    threads: int | None = None,
    limit: int | None = None,
    skip_generation: bool = False,
) -> list[dict]:
    spec = yaml.safe_load(spec_path.read_text())
    points = plan_points(spec)
    if limit is not None:
        points = points[:limit]

    output_dir = Path(spec["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "results.json"
    results: list[dict] = []
    if results_path.exists():
        results = json.loads(results_path.read_text())
    done = {record["name"] for record in results}

    for index, point in enumerate(points, start=1):
        if point["name"] in done:
            print(f"[{index}/{len(points)}] {point['name']} already done, skipping")
            continue
        print(f"[{index}/{len(points)}] {point['name']}")
        results.append(run_point(spec, point, threads, skip_generation))
        results_path.write_text(json.dumps(results, indent=2))
    return results


def sweep_table(results: list[dict]) -> str:
    columns = [
        ("name", "Run"),
        ("trainable_parameters", "Trainable"),
        ("eval_loss", "Eval loss"),
        ("micro_f1", "Micro F1"),
        ("exact_match", "Exact"),
        ("schema_validity", "Schema OK"),
        ("train_runtime_seconds", "Train s"),
    ]
    lines = [
        "| " + " | ".join(label for _key, label in columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for record in sorted(results, key=lambda r: -(r.get("micro_f1") or 0)):
        cells = []
        for key, _label in columns:
            value = record.get(key)
            if isinstance(value, float):
                cells.append(f"{value:.4f}" if key != "train_runtime_seconds" else f"{value:.0f}")
            else:
                cells.append(str(value) if value is not None else "-")
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)

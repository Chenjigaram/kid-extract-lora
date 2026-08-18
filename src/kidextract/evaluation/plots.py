from __future__ import annotations

import json
from pathlib import Path

AXIS_LABELS = {
    "lora.r": "LoRA rank",
    "lora.alpha": "LoRA alpha",
    "lora.dropout": "LoRA dropout",
    "training.learning_rate": "Learning rate",
    "training.epochs": "Epochs",
    "lora.target_modules": "Target modules",
}


def load_results(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def group_by_axis(results: list[dict]) -> dict[str, list[dict]]:
    baseline = next((r for r in results if r["name"] == "baseline"), None)
    groups: dict[str, list[dict]] = {}
    for record in results:
        for option in record.get("overrides", {}):
            groups.setdefault(option, [])
            if baseline is not None and baseline not in groups[option]:
                groups[option].append(baseline)
            groups[option].append(record)
    return groups


def _metric(record: dict, metric: str) -> float | None:
    value = record.get(metric)
    return float(value) if isinstance(value, (int, float)) else None


def axis_value(record: dict, option: str, baseline_value: object) -> str:
    value = record.get("overrides", {}).get(option, baseline_value)
    if isinstance(value, list):
        return "+".join(item.replace("_proj", "") for item in value)
    return str(value)


def plot_sweep(results_path: Path, output_dir: Path, metric: str = "eval_loss") -> list[Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    results = load_results(results_path)
    groups = group_by_axis(results)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for option, records in sorted(groups.items()):
        points = [(axis_value(r, option, "baseline"), _metric(r, metric)) for r in records]
        points = [(label, value) for label, value in points if value is not None]
        if len(points) < 2:
            continue
        labels = [label for label, _ in points]
        values = [value for _, value in points]

        figure, axes = plt.subplots(figsize=(7, 4))
        bars = axes.bar(range(len(values)), values, color="#4C6EF5")
        best = min(range(len(values)), key=lambda i: values[i]) if metric.endswith("loss") else max(
            range(len(values)), key=lambda i: values[i]
        )
        bars[best].set_color("#E8590C")
        axes.set_xticks(range(len(labels)))
        axes.set_xticklabels(labels, rotation=20, ha="right")
        axes.set_ylabel(metric.replace("_", " "))
        axes.set_title(f"{AXIS_LABELS.get(option, option)} against {metric.replace('_', ' ')}")
        axes.grid(axis="y", alpha=0.3)
        figure.tight_layout()

        path = output_dir / f"sweep_{option.replace('.', '_')}.png"
        figure.savefig(path, dpi=150)
        plt.close(figure)
        written.append(path)

    cost = [(r["name"], r.get("trainable_parameters"), _metric(r, metric)) for r in results]
    cost = [(n, p, v) for n, p, v in cost if p and v is not None]
    if len(cost) >= 2:
        figure, axes = plt.subplots(figsize=(7, 4))
        axes.scatter([p / 1e6 for _n, p, _v in cost], [v for _n, _p, v in cost], color="#4C6EF5")
        for name, params, value in cost:
            axes.annotate(name, (params / 1e6, value), fontsize=7, alpha=0.7)
        axes.set_xlabel("Trainable parameters (millions)")
        axes.set_ylabel(metric.replace("_", " "))
        axes.set_title("Adapter size against quality")
        axes.grid(alpha=0.3)
        figure.tight_layout()
        path = output_dir / "sweep_size_vs_quality.png"
        figure.savefig(path, dpi=150)
        plt.close(figure)
        written.append(path)

    return written

from __future__ import annotations

import json
from pathlib import Path

HEADLINE_COLUMNS = (
    ("system", "System"),
    ("split", "Split"),
    ("documents", "N"),
    ("micro_f1", "Micro F1"),
    ("macro_f1", "Macro F1"),
    ("exact_match", "Exact"),
    ("schema_validity", "Schema OK"),
    ("hallucination_rate", "Halluc."),
    ("median_latency_seconds", "Latency s"),
)


def load_summaries(directory: Path) -> list[dict]:
    summaries = []
    for path in sorted(directory.glob("*.json")):
        if path.name.endswith(".predictions.json"):
            continue
        data = json.loads(path.read_text())
        if "system" in data and "per_field" in data:
            summaries.append(data)
    return summaries


def _row(values: list[str]) -> str:
    return "| " + " | ".join(values) + " |"


def headline_table(summaries: list[dict]) -> str:
    lines = [
        _row([label for _key, label in HEADLINE_COLUMNS]),
        _row(["---"] * len(HEADLINE_COLUMNS)),
    ]
    for summary in sorted(summaries, key=lambda s: (s["split"], -s["micro_f1"])):
        lines.append(_row([str(summary[key]) for key, _label in HEADLINE_COLUMNS]))
    return "\n".join(lines)


def field_table(summary: dict) -> str:
    lines = [
        _row(["Field", "P", "R", "F1", "Null acc.", "Support"]),
        _row(["---"] * 6),
    ]
    for name, score in sorted(summary["per_field"].items(), key=lambda kv: -kv[1]["f1"]):
        lines.append(
            _row(
                [
                    name,
                    f"{score['precision']:.3f}",
                    f"{score['recall']:.3f}",
                    f"{score['f1']:.3f}",
                    f"{score['null_accuracy']:.3f}",
                    str(score["support"]),
                ]
            )
        )
    return "\n".join(lines)


def build_report(directory: Path) -> str:
    summaries = load_summaries(directory)
    if not summaries:
        return "No evaluation summaries found."
    sections = ["# Evaluation results", "", headline_table(summaries), ""]
    for summary in sorted(summaries, key=lambda s: (s["split"], s["system"])):
        sections += [f"## {summary['system']} on {summary['split']}", "", field_table(summary), ""]
    return "\n".join(sections)

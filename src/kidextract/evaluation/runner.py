from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from ..dataset.build import read_jsonl
from ..dataset.prompts import build_messages, parse_prediction
from ..schema import KidRecord
from .grounding import score_grounding
from .metrics import Evaluation, score_document

Extractor = Callable[[str], dict | None]


@dataclass
class SystemResult:
    name: str
    split: str
    evaluation: Evaluation
    predictions: list[dict]

    def summary(self) -> dict:
        e = self.evaluation
        return {
            "system": self.name,
            "split": self.split,
            "documents": e.documents,
            "micro_f1": round(e.micro_f1, 4),
            "macro_f1": round(e.macro_f1, 4),
            "exact_match": round(e.exact_match_rate, 4),
            "schema_validity": round(e.schema_validity, 4),
            "hallucination_rate": round(e.hallucination_rate, 5),
            "parse_failures": e.parse_failures,
            "schema_failures": e.schema_failures,
            "median_latency_seconds": round(e.median_latency, 3),
            "per_field": {
                name: {
                    "precision": round(score.precision, 4),
                    "recall": round(score.recall, 4),
                    "f1": round(score.f1, 4),
                    "null_accuracy": round(score.null_accuracy, 4),
                    "support": score.support,
                }
                for name, score in e.per_field.items()
            },
        }


def evaluate_system(name: str, split_path: Path, extract: Extractor, limit: int | None = None) -> SystemResult:
    rows = read_jsonl(split_path)
    if limit is not None:
        rows = rows[:limit]
    evaluation = Evaluation()
    predictions = []
    for row in rows:
        started = time.perf_counter()
        raw = extract(row["text"])
        evaluation.latencies.append(time.perf_counter() - started)

        prediction = raw
        if prediction is None:
            evaluation.parse_failures += 1
        else:
            try:
                KidRecord.model_validate(prediction)
            except ValidationError:
                evaluation.schema_failures += 1

        score_document(evaluation, row["target"], prediction)
        score_grounding(evaluation, prediction, row["text"])
        predictions.append({"id": row["id"], "layout": row["layout"], "prediction": prediction})

    return SystemResult(name, split_path.stem, evaluation, predictions)


def write_result(result: SystemResult, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{result.name}__{result.split}"
    (output_dir / f"{stem}.json").write_text(json.dumps(result.summary(), indent=2))
    with (output_dir / f"{stem}.predictions.jsonl").open("w", encoding="utf-8") as handle:
        for row in result.predictions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return output_dir / f"{stem}.json"


def json_text_extractor(generate: Callable[[str], str]) -> Extractor:
    def extract(document: str) -> dict | None:
        return parse_prediction(generate(document))

    return extract


def few_shot_examples(path: Path, count: int) -> list[tuple[str, str]]:
    if count <= 0:
        return []
    rows = read_jsonl(path)[:count]
    from ..dataset.prompts import target_json

    return [(row["text"], target_json(KidRecord.model_validate(row["target"]))) for row in rows]


def prompt_for(document: str, examples: list[tuple[str, str]] | None = None) -> list[dict[str, str]]:
    return build_messages(document, examples)

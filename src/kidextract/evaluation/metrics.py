from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..normalize import clean_text
from ..schema import NUMERIC_FIELDS, SCALAR_FIELDS, SCENARIO_NAMES

SCENARIO_FIELDS = tuple(
    f"scenarios.{name}.{part}" for name in SCENARIO_NAMES for part in ("value", "return_pct")
)
ALL_FIELDS = SCALAR_FIELDS + SCENARIO_FIELDS

INTEGER_FIELDS = ("sri", "srri")
TEXT_FIELDS = ("fund_name", "isin", "currency", "investment_objective", "benchmark", "domicile", "management_company")

PERCENT_TOLERANCE = 0.005
MONEY_TOLERANCE = 0.01


def flatten(record: dict | None) -> dict[str, object]:
    if not isinstance(record, dict):
        return {name: None for name in ALL_FIELDS}
    flat: dict[str, object] = {name: record.get(name) for name in SCALAR_FIELDS}
    scenarios = record.get("scenarios")
    for name in SCENARIO_NAMES:
        entry = scenarios.get(name) if isinstance(scenarios, dict) else None
        for part in ("value", "return_pct"):
            flat[f"scenarios.{name}.{part}"] = entry.get(part) if isinstance(entry, dict) else None
    return flat


def _as_number(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", "."))
        except ValueError:
            return None
    return None


def values_match(name: str, gold: object, prediction: object) -> bool:
    if name in INTEGER_FIELDS:
        gold_number, predicted_number = _as_number(gold), _as_number(prediction)
        return gold_number is not None and gold_number == predicted_number
    if name in NUMERIC_FIELDS or name.startswith("scenarios."):
        gold_number, predicted_number = _as_number(gold), _as_number(prediction)
        if gold_number is None or predicted_number is None:
            return False
        tolerance = MONEY_TOLERANCE if name.endswith(".value") else PERCENT_TOLERANCE
        return math.isclose(gold_number, predicted_number, abs_tol=tolerance)
    if not isinstance(gold, str) or not isinstance(prediction, str):
        return False
    left, right = clean_text(gold), clean_text(prediction)
    if left is None or right is None:
        return False
    return left.casefold() == right.casefold()


@dataclass
class FieldScore:
    true_positive: int = 0
    false_positive: int = 0
    false_negative: int = 0
    true_negative: int = 0

    @property
    def precision(self) -> float:
        denominator = self.true_positive + self.false_positive
        return self.true_positive / denominator if denominator else 0.0

    @property
    def recall(self) -> float:
        denominator = self.true_positive + self.false_negative
        return self.true_positive / denominator if denominator else 0.0

    @property
    def f1(self) -> float:
        total = self.precision + self.recall
        return 2 * self.precision * self.recall / total if total else 0.0

    @property
    def null_accuracy(self) -> float:
        denominator = self.true_negative + self.false_positive
        return self.true_negative / denominator if denominator else 1.0

    @property
    def support(self) -> int:
        return self.true_positive + self.false_negative


@dataclass
class Evaluation:
    per_field: dict[str, FieldScore] = field(default_factory=lambda: {n: FieldScore() for n in ALL_FIELDS})
    documents: int = 0
    parse_failures: int = 0
    schema_failures: int = 0
    exact_matches: int = 0
    predicted_values: int = 0
    ungrounded_values: int = 0
    latencies: list[float] = field(default_factory=list)

    @property
    def schema_validity(self) -> float:
        if not self.documents:
            return 0.0
        return 1.0 - (self.parse_failures + self.schema_failures) / self.documents

    @property
    def hallucination_rate(self) -> float:
        return self.ungrounded_values / self.predicted_values if self.predicted_values else 0.0

    @property
    def exact_match_rate(self) -> float:
        return self.exact_matches / self.documents if self.documents else 0.0

    @property
    def macro_f1(self) -> float:
        scored = [s for s in self.per_field.values() if s.support]
        return sum(s.f1 for s in scored) / len(scored) if scored else 0.0

    @property
    def micro_f1(self) -> float:
        total = FieldScore()
        for score in self.per_field.values():
            total.true_positive += score.true_positive
            total.false_positive += score.false_positive
            total.false_negative += score.false_negative
        return total.f1

    @property
    def median_latency(self) -> float:
        if not self.latencies:
            return 0.0
        ordered = sorted(self.latencies)
        middle = len(ordered) // 2
        if len(ordered) % 2:
            return ordered[middle]
        return (ordered[middle - 1] + ordered[middle]) / 2


def score_document(evaluation: Evaluation, gold: dict, prediction: dict | None) -> None:
    evaluation.documents += 1
    gold_flat = flatten(gold)
    predicted_flat = flatten(prediction)
    correct = prediction is not None
    for name in ALL_FIELDS:
        score = evaluation.per_field[name]
        gold_value = gold_flat[name]
        predicted_value = predicted_flat[name]
        if gold_value is None and predicted_value is None:
            score.true_negative += 1
        elif gold_value is None:
            score.false_positive += 1
            correct = False
        elif predicted_value is None:
            score.false_negative += 1
            correct = False
        elif values_match(name, gold_value, predicted_value):
            score.true_positive += 1
        else:
            score.false_positive += 1
            score.false_negative += 1
            correct = False
    if correct:
        evaluation.exact_matches += 1

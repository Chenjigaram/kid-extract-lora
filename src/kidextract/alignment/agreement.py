from __future__ import annotations

from ..evaluation.metrics import ALL_FIELDS, flatten, values_match


def field_matches(prediction_a: dict | None, prediction_b: dict | None, fields=ALL_FIELDS) -> dict[str, bool]:
    left, right = flatten(prediction_a), flatten(prediction_b)
    matches = {}
    for name in fields:
        a, b = left[name], right[name]
        if a is None and b is None:
            matches[name] = True
        elif a is None or b is None:
            matches[name] = False
        else:
            matches[name] = values_match(name, a, b)
    return matches


def strict_agreement(prediction_a: dict | None, prediction_b: dict | None, fields=ALL_FIELDS) -> bool:
    return all(field_matches(prediction_a, prediction_b, fields).values())


def mean_field_agreement(prediction_a: dict | None, prediction_b: dict | None, fields=ALL_FIELDS) -> float:
    matches = field_matches(prediction_a, prediction_b, fields)
    return sum(matches.values()) / len(matches) if matches else 1.0

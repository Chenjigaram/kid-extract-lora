from __future__ import annotations

from ..normalize import clean_text
from .metrics import ALL_FIELDS, INTEGER_FIELDS, TEXT_FIELDS, Evaluation, _as_number, flatten


def numeric_surface_forms(value: float) -> set[str]:
    forms: set[str] = set()
    for text in (f"{value:.2f}", f"{value:.1f}", f"{value:g}"):
        forms.add(text)
        forms.add(text.replace(".", ","))
    if float(value).is_integer():
        whole = str(int(value))
        forms.add(whole)
        forms.add(f"{int(value):,}")
        forms.add(f"{int(value):,}".replace(",", "."))
    basis_points = value * 100
    if abs(basis_points - round(basis_points)) < 1e-6:
        forms.add(str(int(round(basis_points))))
    for grouped in (f"{value:,.2f}",):
        forms.add(grouped)
        forms.add(grouped.replace(",", "#").replace(".", ",").replace("#", "."))
    return {form for form in forms if form}


def is_grounded(name: str, value: object, text: str) -> bool:
    if value is None:
        return True
    haystack = clean_text(text) or ""
    if name in TEXT_FIELDS:
        needle = clean_text(str(value))
        return bool(needle) and needle.casefold() in haystack.casefold()
    number = _as_number(value)
    if number is None:
        return False
    if name in INTEGER_FIELDS:
        return str(int(number)) in haystack
    return any(form in haystack for form in numeric_surface_forms(number))


def score_grounding(evaluation: Evaluation, prediction: dict | None, text: str) -> int:
    if prediction is None:
        return 0
    flat = flatten(prediction)
    ungrounded = 0
    for name in ALL_FIELDS:
        value = flat[name]
        if value is None:
            continue
        evaluation.predicted_values += 1
        if not is_grounded(name, value, text):
            evaluation.ungrounded_values += 1
            ungrounded += 1
    return ungrounded

from __future__ import annotations

import re

from ...corpus.layouts import HEADINGS
from ...corpus.vocabulary import all_labels_for
from ...normalize import (
    clean_text,
    parse_currency,
    parse_isin,
    parse_money,
    parse_number,
    parse_percent,
    parse_years,
)
from ...schema import isin_is_valid

FIELD_BY_LABEL_KEY = {
    "isin": "isin",
    "manufacturer": "management_company",
    "currency": "currency",
    "domicile": "domicile",
    "benchmark": "benchmark",
    "rhp": "recommended_holding_period_years",
    "ongoing": "ongoing_charges_pct",
    "entry": "entry_charge_pct",
    "exit": "exit_charge_pct",
    "transaction": "transaction_costs_pct",
    "performance_fee": "performance_fee_pct",
}

PERCENT_TARGETS = {
    "ongoing_charges_pct",
    "entry_charge_pct",
    "exit_charge_pct",
    "transaction_costs_pct",
    "performance_fee_pct",
}

SCENARIO_KEYS = ("stress", "unfavourable", "moderate", "favourable")

SEPARATORS = (":", " :", " -", " |")


def _label_index() -> list[tuple[str, str]]:
    pairs = []
    for key, field in FIELD_BY_LABEL_KEY.items():
        for label in all_labels_for(key):
            pairs.append((label.casefold(), field))
    return sorted(set(pairs), key=lambda pair: -len(pair[0]))


def _scenario_index() -> list[tuple[str, str]]:
    pairs = []
    for words in HEADINGS.values():
        for key in SCENARIO_KEYS:
            pairs.append((words[key].casefold(), key))
    return sorted(set(pairs), key=lambda pair: -len(pair[0]))


def _objective_headings() -> list[str]:
    return [label.casefold() for label in all_labels_for("objective")]


def _title_map() -> list[tuple[str, str]]:
    pairs = []
    for words in HEADINGS.values():
        pairs.append((words["title_kid"].casefold(), "kid"))
        pairs.append((words["title_kiid"].casefold(), "kiid"))
    return pairs


LABELS = _label_index()
SCENARIO_LABELS = _scenario_index()
OBJECTIVE_HEADINGS = _objective_headings()
TITLES = _title_map()
ALL_HEADINGS = {
    label.casefold()
    for key in ("purpose", "product", "objective", "risk", "scenarios", "costs", "holding", "practical")
    for label in all_labels_for(key)
}


def _strip_bullet(line: str) -> str:
    return line.lstrip().removeprefix("- ").strip()


def build_label_index(vocabulary: str = "known") -> list[tuple[str, str]]:
    pairs = []
    for key, field in FIELD_BY_LABEL_KEY.items():
        for label in all_labels_for(key, vocabulary):
            pairs.append((label.casefold(), field))
    return sorted(set(pairs), key=lambda pair: -len(pair[0]))


def _split_label(line: str, labels: list[tuple[str, str]] | None = None) -> tuple[str, str] | None:
    candidate = _strip_bullet(line)
    lowered = candidate.casefold()
    for label, field in labels or LABELS:
        if lowered.startswith(label):
            remainder = candidate[len(label) :]
            for separator in SEPARATORS:
                if remainder.startswith(separator):
                    remainder = remainder[len(separator) :]
                    break
            return field, remainder.strip()
    return None


def _detect_doc_type(text: str) -> str:
    lowered = text.casefold()
    for title, kind in TITLES:
        if title in lowered:
            return kind
    return "kid"


def _detect_risk(text: str) -> int | None:
    scale = re.search(r"\[([1-7])\]", text)
    if scale:
        return int(scale.group(1))
    out_of = re.search(r"\b([1-7])\s*(?:/|of|von|sur|van|out of)\s*7\b", text, flags=re.IGNORECASE)
    if out_of:
        return int(out_of.group(1))
    sentence = re.search(r"(?:class|klasse|classe|risicoklasse)\s+([1-7])\b", text, flags=re.IGNORECASE)
    return int(sentence.group(1)) if sentence else None


def _detect_fund_name(lines: list[str]) -> str | None:
    for index, line in enumerate(lines[:6]):
        stripped = line.strip()
        if not stripped or stripped.casefold() in ALL_HEADINGS:
            continue
        if any(stripped.casefold().startswith(title) for title, _ in TITLES):
            continue
        if index == 0:
            continue
        return clean_text(stripped)
    return None


def _detect_objective(lines: list[str], labels: list[tuple[str, str]] | None = None) -> str | None:
    for index, line in enumerate(lines):
        if line.strip().casefold() in OBJECTIVE_HEADINGS:
            for candidate in lines[index + 1 :]:
                stripped = candidate.strip()
                if not stripped:
                    return None
                if _split_label(candidate, labels):
                    continue
                return clean_text(stripped)
    return None


def _detect_prose_costs(text: str, found: dict, labels: list[tuple[str, str]] | None = None) -> None:
    connectors = r"(?:amount to|betragen|s'[ée]l[èe]vent [àa]|bedragen)"
    for label, field in labels or LABELS:
        if field not in PERCENT_TARGETS or field in found:
            continue
        pattern = re.compile(
            re.escape(label) + r"\s+" + connectors + r"\s+([\d.,']+\s*(?:%|bps))", re.IGNORECASE
        )
        match = pattern.search(text)
        if match:
            found[field] = parse_percent(match.group(1))


def _detect_scenarios(lines: list[str]) -> dict | None:
    scenarios: dict[str, dict] = {}
    for line in lines:
        candidate = line.strip()
        lowered = candidate.casefold()
        for label, key in SCENARIO_LABELS:
            if not lowered.startswith(label) or key in scenarios:
                continue
            remainder = candidate[len(label) :]
            numbers = re.findall(r"-?\d[\d.,']*\d|-?\d", remainder)
            if len(numbers) >= 2:
                scenarios[key] = {
                    "value": parse_money(numbers[0]),
                    "return_pct": parse_number(numbers[-1]),
                }
            break
    return scenarios or None


def extract(text: str, labels: list[tuple[str, str]] | None = None) -> dict:
    lines = text.split("\n")
    found: dict[str, object] = {}
    for line in lines:
        parsed = _split_label(line, labels)
        if parsed is None:
            continue
        field, raw = parsed
        if not raw or field in found:
            continue
        if field in PERCENT_TARGETS:
            found[field] = parse_percent(raw)
        elif field == "recommended_holding_period_years":
            found[field] = parse_years(raw)
        elif field == "currency":
            found[field] = parse_currency(raw)
        elif field == "isin":
            found[field] = parse_isin(raw)
        else:
            found[field] = clean_text(raw)

    _detect_prose_costs(text, found, labels)
    risk = _detect_risk(text)
    doc_type = _detect_doc_type(text)

    return {
        "fund_name": _detect_fund_name(lines),
        "isin": found.get("isin") or parse_isin(text, validator=isin_is_valid),
        "currency": found.get("currency"),
        "sri": risk if doc_type == "kid" else None,
        "srri": risk if doc_type == "kiid" else None,
        "ongoing_charges_pct": found.get("ongoing_charges_pct"),
        "entry_charge_pct": found.get("entry_charge_pct"),
        "exit_charge_pct": found.get("exit_charge_pct"),
        "transaction_costs_pct": found.get("transaction_costs_pct"),
        "performance_fee_pct": found.get("performance_fee_pct"),
        "recommended_holding_period_years": found.get("recommended_holding_period_years"),
        "investment_objective": _detect_objective(lines, labels),
        "benchmark": found.get("benchmark"),
        "domicile": found.get("domicile"),
        "management_company": found.get("management_company"),
        "scenarios": _detect_scenarios(lines),
    }

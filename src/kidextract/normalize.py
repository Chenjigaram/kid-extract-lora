from __future__ import annotations

import re
import unicodedata

_WHITESPACE = re.compile(r"\s+")
_NUMBER = re.compile("-?\\d[\\d \t .,']*\\d|-?\\d")
_STRIP_FROM_NUMBER = str.maketrans("", "", " \t '")

_YEAR_WORDS = (
    "year", "years", "yr", "yrs", "jahre", "jahr", "ans", "an",
    "jaar", "anni", "anno", "anos", "years.",
)
_MONTH_WORDS = ("month", "months", "monate", "monat", "mois", "maanden", "mesi", "meses")

_CURRENCY_SYMBOLS = {"€": "EUR", "£": "GBP", "$": "USD"}


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = unicodedata.normalize("NFKC", value)
    text = text.replace("­", "").replace("-\n", "")
    text = _WHITESPACE.sub(" ", text).strip()
    return text or None


def parse_number(token: str, grouped: bool = False) -> float | None:
    match = _NUMBER.search(token)
    if match is None:
        return None
    raw = match.group(0).translate(_STRIP_FROM_NUMBER)
    separators = [c for c in raw if c in ".,"]
    if separators:
        if len(set(separators)) == 2:
            decimal = "," if raw.rfind(",") > raw.rfind(".") else "."
            thousands = "." if decimal == "," else ","
            raw = raw.replace(thousands, "").replace(decimal, ".")
        elif len(separators) > 1:
            raw = raw.replace(separators[0], "")
        else:
            sep = separators[0]
            trailing = len(raw) - raw.rfind(sep) - 1
            raw = raw.replace(sep, "" if grouped and trailing == 3 else ".")
    try:
        return float(raw)
    except ValueError:
        return None


def parse_percent(value: str | float | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    lowered = value.lower()
    number = parse_number(lowered)
    if number is None:
        return None
    if "bps" in lowered or "basis point" in lowered:
        return round(number / 100.0, 6)
    if "%" not in lowered and 0 < number < 0.2:
        return round(number * 100.0, 6)
    return round(number, 6)


def parse_money(value: str | float | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return parse_number(value, grouped=True)


def parse_years(value: str | float | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    lowered = value.lower()
    number = parse_number(lowered)
    if number is None:
        return None
    if any(word in lowered for word in _MONTH_WORDS):
        return round(number / 12.0, 4)
    return float(number)


def parse_risk_level(value: str | int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value if 1 <= value <= 7 else None
    match = re.search(r"\b([1-7])\b", value)
    return int(match.group(1)) if match else None


def parse_currency(value: str | None) -> str | None:
    if value is None:
        return None
    for symbol, code in _CURRENCY_SYMBOLS.items():
        if symbol in value:
            return code
    match = re.search(r"\b([A-Z]{3})\b", value.upper())
    return match.group(1) if match else None


def parse_isin(value: str | None) -> str | None:
    if value is None:
        return None
    match = re.search(r"\b([A-Z]{2}[A-Z0-9]{9}\d)\b", value.upper().replace(" ", ""))
    return match.group(1) if match else None

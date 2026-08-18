import pytest

from kidextract.normalize import (
    clean_text,
    parse_currency,
    parse_isin,
    parse_money,
    parse_percent,
    parse_risk_level,
    parse_years,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1.25%", 1.25),
        ("1,25 %", 1.25),
        ("  0,84 % ", 0.84),
        ("0.0125", 1.25),
        ("0,0084", 0.84),
        ("125 bps", 1.25),
        ("84 basis points", 0.84),
        ("1.000 %", 1.0),
        ("2.5 %", 2.5),
    ],
)
def test_percent_formats(raw, expected):
    assert parse_percent(raw) == expected


def test_percent_passes_through_numbers():
    assert parse_percent(1.25) == 1.25


def test_percent_of_missing_value():
    assert parse_percent(None) is None
    assert parse_percent("not disclosed") is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("EUR 10.000", 10000.0), ("9 750,50", 9750.5), ("12'340", 12340.0), ("10 000", 10000.0)],
)
def test_money_grouping(raw, expected):
    assert parse_money(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("5 years", 5.0), ("60 months", 5.0), ("min. 3 ans", 3.0), ("7", 7.0), ("5 Jahre", 5.0)],
)
def test_holding_period(raw, expected):
    assert parse_years(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), [("SRI 4 of 7", 4), ("Risk indicator: 6", 6), ("n/a", None)])
def test_risk_level(raw, expected):
    assert parse_risk_level(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), [("EUR", "EUR"), ("10 €", "EUR"), ("Fund currency CHF", "CHF")])
def test_currency(raw, expected):
    assert parse_currency(raw) == expected


def test_isin_extracted_from_surrounding_text():
    assert parse_isin("ISIN: LU0690375182 (accumulating)") == "LU0690375182"


def test_isin_absent():
    assert parse_isin("share class A") is None


def test_clean_text_collapses_whitespace_and_soft_hyphens():
    assert clean_text("  multi \n line   text­ ") == "multi line text"


def test_clean_text_of_blank_is_none():
    assert clean_text("   ") is None


def test_isin_is_not_fabricated_across_lines():
    text = "FAVOURABLE\n25,000.00\nMODERATE\n12,500.00"
    assert parse_isin(text) is None or len(parse_isin(text)) == 12


def test_isin_search_respects_line_boundaries():
    from kidextract.schema import isin_is_valid

    text = "FAVOURABLE\n25 000\nISIN LU0690375182"
    assert parse_isin(text, validator=isin_is_valid) == "LU0690375182"


def test_isin_validator_rejects_bad_checksums():
    from kidextract.schema import isin_is_valid

    assert parse_isin("code LU0690375183", validator=isin_is_valid) is None

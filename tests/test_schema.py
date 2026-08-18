import pytest
from pydantic import ValidationError

from kidextract.schema import KidRecord, isin_is_valid, json_schema


@pytest.mark.parametrize("code", ["LU0690375182", "IE00B4L5Y983", "FR0010315770"])
def test_accepts_valid_isin(code):
    assert isin_is_valid(code)


@pytest.mark.parametrize("code", ["LU0690375183", "XX123", "", "LU069037518A"])
def test_rejects_invalid_isin(code):
    assert not isin_is_valid(code)


def test_all_fields_default_to_none():
    record = KidRecord()
    assert set(record.model_dump().values()) == {None}


def test_currency_is_upper_cased():
    assert KidRecord(currency="eur").currency == "EUR"


def test_non_iso_currency_becomes_none():
    assert KidRecord(currency="euro").currency is None


def test_blank_strings_become_none():
    assert KidRecord(fund_name="   ", benchmark="").fund_name is None


def test_risk_level_outside_scale_is_rejected():
    with pytest.raises(ValidationError):
        KidRecord(sri=8)


def test_negative_charge_is_rejected():
    with pytest.raises(ValidationError):
        KidRecord(ongoing_charges_pct=-1.0)


def test_unknown_field_is_rejected():
    with pytest.raises(ValidationError):
        KidRecord(total_expense_ratio=1.2)


def test_schema_exposes_every_field():
    assert "ongoing_charges_pct" in json_schema()["properties"]

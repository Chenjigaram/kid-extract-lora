from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

RiskLevel = Literal[1, 2, 3, 4, 5, 6, 7]

SCENARIO_NAMES = ("stress", "unfavourable", "moderate", "favourable")

SCALAR_FIELDS = (
    "fund_name",
    "isin",
    "currency",
    "sri",
    "srri",
    "ongoing_charges_pct",
    "entry_charge_pct",
    "exit_charge_pct",
    "transaction_costs_pct",
    "performance_fee_pct",
    "recommended_holding_period_years",
    "investment_objective",
    "benchmark",
    "domicile",
    "management_company",
)

NUMERIC_FIELDS = (
    "ongoing_charges_pct",
    "entry_charge_pct",
    "exit_charge_pct",
    "transaction_costs_pct",
    "performance_fee_pct",
    "recommended_holding_period_years",
)

TEXT_FIELDS = (
    "fund_name",
    "isin",
    "currency",
    "investment_objective",
    "benchmark",
    "domicile",
    "management_company",
)


def isin_is_valid(value: str) -> bool:
    if len(value) != 12 or not value[:2].isalpha() or not value.isalnum():
        return False
    expanded = "".join(str(int(c, 36)) if c.isalpha() else c for c in value.upper())
    total = 0
    for index, digit in enumerate(reversed(expanded)):
        n = int(digit)
        if index % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: float | None = None
    return_pct: float | None = None


class PerformanceScenarios(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stress: Scenario | None = None
    unfavourable: Scenario | None = None
    moderate: Scenario | None = None
    favourable: Scenario | None = None


class KidRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    fund_name: str | None = None
    isin: str | None = None
    currency: str | None = None
    sri: RiskLevel | None = None
    srri: RiskLevel | None = None
    ongoing_charges_pct: float | None = Field(default=None, ge=0, le=100)
    entry_charge_pct: float | None = Field(default=None, ge=0, le=100)
    exit_charge_pct: float | None = Field(default=None, ge=0, le=100)
    transaction_costs_pct: float | None = Field(default=None, ge=0, le=100)
    performance_fee_pct: float | None = Field(default=None, ge=0, le=100)
    recommended_holding_period_years: float | None = Field(default=None, ge=0, le=50)
    investment_objective: str | None = None
    benchmark: str | None = None
    domicile: str | None = None
    management_company: str | None = None
    scenarios: PerformanceScenarios | None = None

    @field_validator("currency")
    @classmethod
    def _upper_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        code = value.strip().upper()
        return code if len(code) == 3 and code.isalpha() else None

    @field_validator("isin")
    @classmethod
    def _clean_isin(cls, value: str | None) -> str | None:
        if value is None:
            return None
        code = value.strip().upper().replace(" ", "")
        return code or None

    @field_validator(*TEXT_FIELDS, mode="before")
    @classmethod
    def _blank_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    def to_json(self, indent: int | None = None) -> str:
        return json.dumps(self.model_dump(mode="json"), ensure_ascii=False, indent=indent)


def empty_record() -> KidRecord:
    return KidRecord()


def json_schema() -> dict:
    return KidRecord.model_json_schema()

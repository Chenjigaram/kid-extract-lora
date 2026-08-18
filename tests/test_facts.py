import random

import pytest

from kidextract.corpus.facts import HOLDING_PERIOD_BY_RISK, isin_check_digit, synthesise_fund
from kidextract.schema import isin_is_valid

SCENARIO_ORDER = ("stress", "unfavourable", "moderate", "favourable")


@pytest.fixture
def funds():
    rng = random.Random(11)
    return [synthesise_fund(rng) for _ in range(300)]


def test_generated_isins_pass_checksum(funds):
    assert all(isin_is_valid(fund.isin) for fund in funds)


def test_check_digit_matches_known_isin():
    assert isin_check_digit("LU069037518") == "2"


def test_risk_level_within_regulatory_scale(funds):
    assert all(1 <= fund.risk_level <= 7 for fund in funds)


def test_holding_period_follows_risk(funds):
    assert all(
        fund.recommended_holding_period_years == HOLDING_PERIOD_BY_RISK[fund.risk_level]
        for fund in funds
    )


def test_scenarios_are_monotonically_ordered(funds):
    for fund in funds:
        values = [fund.scenarios[name][0] for name in SCENARIO_ORDER]
        assert values == sorted(values)


def test_charges_are_plausible(funds):
    assert all(0.0 < fund.ongoing_charges_pct < 3.0 for fund in funds)


def test_generation_is_reproducible():
    assert synthesise_fund(random.Random(4)) == synthesise_fund(random.Random(4))


def test_different_seeds_give_different_funds():
    assert synthesise_fund(random.Random(1)) != synthesise_fund(random.Random(2))

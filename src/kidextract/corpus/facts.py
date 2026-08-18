from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

DOMICILES = {
    "LU": "Luxembourg",
    "IE": "Ireland",
    "FR": "France",
    "DE": "Germany",
    "NL": "Netherlands",
}

CURRENCIES = ("EUR", "EUR", "EUR", "USD", "GBP", "CHF")

MANAGERS = (
    "Amundi Asset Management",
    "BlackRock (Netherlands) B.V.",
    "DWS Investment S.A.",
    "Robeco Institutional Asset Management",
    "NN Investment Partners",
    "Candriam Luxembourg",
    "Schroder Investment Management (Europe) S.A.",
    "BNP Paribas Asset Management",
    "Nordea Investment Funds S.A.",
    "Pictet Asset Management (Europe) S.A.",
)

STRATEGIES = (
    ("Global Equity", "MSCI World Net Return", 5),
    ("European Equity", "MSCI Europe Net Return", 5),
    ("Emerging Markets Equity", "MSCI Emerging Markets Net Return", 6),
    ("Euro Government Bond", "Bloomberg Euro Aggregate Treasury", 2),
    ("Euro Corporate Bond", "Bloomberg Euro Aggregate Corporate", 3),
    ("Global High Yield", "ICE BofA Global High Yield", 4),
    ("Sustainable Global Equity", "MSCI World SRI Net Return", 5),
    ("Multi-Asset Balanced", "50% MSCI World / 50% Bloomberg Euro Aggregate", 3),
    ("Short Duration Bond", "Bloomberg Euro Aggregate 1-3 Year", 2),
    ("Technology Equity", "MSCI World Information Technology", 6),
    ("Real Estate Equity", "FTSE EPRA Nareit Developed Europe", 5),
    ("Money Market", "Euro Short-Term Rate", 1),
)

SHARE_CLASSES = ("A", "B", "C", "I", "R", "N", "P")
DISTRIBUTION = ("Acc", "Dist", "Cap", "Inc")

HOLDING_PERIOD_BY_RISK = {1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0, 5: 5.0, 6: 6.0, 7: 7.0}


def isin_check_digit(body: str) -> str:
    expanded = "".join(str(int(c, 36)) if c.isalpha() else c for c in body.upper())
    total = 0
    for index, digit in enumerate(reversed(expanded)):
        n = int(digit)
        if index % 2 == 0:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return str((10 - total % 10) % 10)


def make_isin(rng: random.Random, country: str) -> str:
    body = country + "".join(rng.choice("0123456789") for _ in range(9))
    return body + isin_check_digit(body)


@dataclass(frozen=True)
class FundFacts:
    fund_name: str
    isin: str
    currency: str
    risk_level: int
    ongoing_charges_pct: float
    entry_charge_pct: float
    exit_charge_pct: float
    transaction_costs_pct: float
    performance_fee_pct: float
    recommended_holding_period_years: float
    investment_objective: str
    benchmark: str
    domicile: str
    management_company: str
    scenarios: dict[str, tuple[float, float]] = field(default_factory=dict)


def _objective(strategy: str, benchmark: str, rng: random.Random) -> str:
    openings = (
        "The Fund aims to achieve long-term capital growth by investing",
        "The objective of the Fund is to provide a total return by investing",
        "The Fund seeks to outperform its benchmark over the recommended holding period by investing",
        "This Fund is actively managed and invests",
    )
    holdings = {
        "Global Equity": "in a diversified portfolio of equities of companies worldwide",
        "European Equity": "primarily in equities of companies domiciled in Europe",
        "Emerging Markets Equity": "in equities of companies located in emerging market countries",
        "Euro Government Bond": "in bonds issued by euro area governments",
        "Euro Corporate Bond": "in investment grade bonds issued by companies in the euro area",
        "Global High Yield": "in sub-investment grade corporate bonds issued worldwide",
        "Sustainable Global Equity": "in equities of companies worldwide that meet the Fund's sustainability criteria",
        "Multi-Asset Balanced": "across equities, bonds and money market instruments",
        "Short Duration Bond": "in bonds with a residual maturity of less than three years",
        "Technology Equity": "in equities of companies active in the information technology sector",
        "Real Estate Equity": "in listed real estate companies and REITs in developed Europe",
        "Money Market": "in high quality short-term money market instruments",
    }
    closing = rng.choice(
        (
            f" The Fund is managed with reference to the {benchmark} index.",
            f" Performance is compared against the {benchmark}.",
            " The Fund does not track any index.",
            "",
        )
    )
    return f"{rng.choice(openings)} {holdings[strategy]}.{closing}"


def _scenarios(risk_level: int, years: float, rng: random.Random) -> dict[str, tuple[float, float]]:
    volatility = 0.02 + 0.035 * risk_level
    drift = 0.005 + 0.012 * risk_level
    outcomes = {}
    for name, quantile in (("stress", -2.4), ("unfavourable", -1.0), ("moderate", 0.15), ("favourable", 1.3)):
        annual = drift + quantile * volatility + rng.uniform(-0.004, 0.004)
        value = 10000 * (1 + annual) ** years
        outcomes[name] = (round(value, 2), round(annual * 100, 2))
    return outcomes


def synthesise_fund(rng: random.Random) -> FundFacts:
    strategy, benchmark, base_risk = rng.choice(STRATEGIES)
    country = rng.choice(list(DOMICILES))
    currency = rng.choice(CURRENCIES)
    manager = rng.choice(MANAGERS)
    house = manager.split()[0]
    share_class = f"{rng.choice(SHARE_CLASSES)}{rng.choice(DISTRIBUTION)}"
    risk_level = min(7, max(1, base_risk + rng.choice((-1, 0, 0, 0, 1))))
    years = HOLDING_PERIOD_BY_RISK[risk_level]
    is_passive = "does not" not in benchmark and rng.random() < 0.3
    ongoing = round(rng.uniform(0.07, 0.35) if is_passive else rng.uniform(0.55, 2.1), 2)

    return FundFacts(
        fund_name=f"{house} {strategy} Fund {share_class} {currency}",
        isin=make_isin(rng, country),
        currency=currency,
        risk_level=risk_level,
        ongoing_charges_pct=ongoing,
        entry_charge_pct=round(rng.choice((0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 5.0)), 2),
        exit_charge_pct=round(rng.choice((0.0, 0.0, 0.0, 0.0, 0.5, 1.0)), 2),
        transaction_costs_pct=round(rng.uniform(0.0, 0.45), 2),
        performance_fee_pct=round(rng.choice((0.0, 0.0, 0.0, 10.0, 15.0, 20.0)), 2),
        recommended_holding_period_years=years,
        investment_objective=_objective(strategy, benchmark, rng),
        benchmark=benchmark,
        domicile=DOMICILES[country],
        management_company=manager,
        scenarios=_scenarios(risk_level, years, rng),
    )


MORNINGSTAR_COLUMNS = {
    "fund_name": ("name", "fund_name"),
    "isin": ("isin",),
    "currency": ("fund_trailing_return_currency", "currency", "fund_currency"),
    "ongoing_charges_pct": ("ongoing_cost", "management_fees", "ongoing_charge"),
    "risk_level": ("risk_rating", "srri"),
    "benchmark": ("fund_benchmark", "benchmark"),
    "management_company": ("management_company", "company"),
    "domicile": ("domicile", "country"),
}


def _first_present(frame: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    for name in candidates:
        if name in frame.columns:
            return name
    return None


def load_reference_funds(csv_path: Path, limit: int | None = None) -> pd.DataFrame:
    frame = pd.read_csv(csv_path, low_memory=False, nrows=limit)
    mapping = {
        target: _first_present(frame, candidates)
        for target, candidates in MORNINGSTAR_COLUMNS.items()
    }
    missing = [target for target, source in mapping.items() if source is None]
    if "fund_name" in missing or "isin" in missing:
        raise ValueError(f"reference CSV is missing required columns: {missing}")
    selected = {target: frame[source] for target, source in mapping.items() if source}
    return pd.DataFrame(selected)


def facts_from_reference(row: pd.Series, rng: random.Random) -> FundFacts:
    template = synthesise_fund(rng)
    name = str(row.get("fund_name") or template.fund_name).strip()
    isin = str(row.get("isin") or template.isin).strip().upper()
    risk = row.get("risk_level")
    risk_level = int(risk) if pd.notna(risk) and 1 <= float(risk) <= 7 else template.risk_level
    ongoing = row.get("ongoing_charges_pct")
    ongoing_pct = round(float(ongoing), 2) if pd.notna(ongoing) and 0 < float(ongoing) < 20 else template.ongoing_charges_pct
    years = HOLDING_PERIOD_BY_RISK[risk_level]
    benchmark = row.get("benchmark")
    manager = row.get("management_company")
    domicile = row.get("domicile")

    return FundFacts(
        fund_name=name,
        isin=isin,
        currency=str(row.get("currency") or template.currency)[:3].upper(),
        risk_level=risk_level,
        ongoing_charges_pct=ongoing_pct,
        entry_charge_pct=template.entry_charge_pct,
        exit_charge_pct=template.exit_charge_pct,
        transaction_costs_pct=template.transaction_costs_pct,
        performance_fee_pct=template.performance_fee_pct,
        recommended_holding_period_years=years,
        investment_objective=template.investment_objective,
        benchmark=str(benchmark) if pd.notna(benchmark) else template.benchmark,
        domicile=str(domicile) if pd.notna(domicile) else template.domicile,
        management_company=str(manager) if pd.notna(manager) else template.management_company,
        scenarios=_scenarios(risk_level, years, rng),
    )

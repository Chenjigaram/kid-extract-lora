from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..normalize import clean_text
from ..schema import KidRecord, PerformanceScenarios, Scenario
from .facts import FundFacts
from .layouts import Layout
from .objectives import objective_text
from .vocabulary import build_labels

YEAR_WORD = {"en": "years", "de": "Jahre", "fr": "ans", "nl": "jaar"}

COST_SENTENCE = {
    "en": "{label} amount to {value}.",
    "de": "{label} betragen {value}.",
    "fr": "{label} s'élèvent à {value}.",
    "nl": "{label} bedragen {value}.",
}

DROPOUT = {
    "isin": 0.05,
    "currency": 0.15,
    "benchmark": 0.25,
    "domicile": 0.30,
    "management_company": 0.20,
    "entry_charge_pct": 0.15,
    "exit_charge_pct": 0.15,
    "transaction_costs_pct": 0.10,
    "performance_fee_pct": 0.35,
}

DISTRACTORS = {
    "en": [
        "Past performance is shown for the last 10 years where available.",
        "The depositary charges a fee of up to 0.02% of net assets.",
        "Investors may switch between share classes subject to a charge of up to 1%.",
        "Tax legislation in the fund's home country may have an impact on your personal tax position.",
    ],
    "de": [
        "Die Wertentwicklung der letzten 10 Jahre ist auf der Website verfügbar.",
        "Die Verwahrstelle berechnet eine Gebühr von bis zu 0,02 % des Nettovermögens.",
        "Ein Umtausch zwischen Anteilklassen kann mit bis zu 1 % belastet werden.",
        "Die Steuergesetzgebung des Fondsdomizils kann Ihre persönliche Steuersituation beeinflussen.",
    ],
    "fr": [
        "Les performances passées sont présentées sur 10 ans lorsqu'elles sont disponibles.",
        "Le dépositaire perçoit une commission pouvant atteindre 0,02 % de l'actif net.",
        "Le passage d'une catégorie de parts à une autre peut être facturé jusqu'à 1 %.",
        "La législation fiscale du pays de domiciliation peut avoir une incidence sur votre situation.",
    ],
    "nl": [
        "In het verleden behaalde resultaten worden over 10 jaar getoond indien beschikbaar.",
        "De bewaarder brengt een vergoeding van maximaal 0,02% van het nettovermogen in rekening.",
        "Wisselen tussen aandelenklassen kan tot 1% kosten met zich meebrengen.",
        "De belastingwetgeving van het vestigingsland kan uw persoonlijke situatie beïnvloeden.",
    ],
}


@dataclass(frozen=True)
class GeneratedDocument:
    text: str
    record: KidRecord
    layout: str
    doc_type: str
    language: str
    labels: dict[str, str] = field(default_factory=dict)


def format_percent(value: float, style: str, allow_bps: bool = False) -> str:
    if style == "bps" and allow_bps:
        return f"{round(value * 100)} bps"
    if style == "comma":
        return f"{value:.2f}".replace(".", ",") + " %"
    return f"{value:.2f}%"


def format_money(value: float, style: str) -> str:
    if style == "comma":
        whole = f"{value:,.2f}"
        return whole.replace(",", "#").replace(".", ",").replace("#", ".")
    return f"{value:,.2f}"


def format_years(value: float, language: str) -> str:
    number = int(value) if float(value).is_integer() else value
    return f"{number} {YEAR_WORD[language]}"


def _heading(text: str, layout: Layout) -> str:
    return text.upper() if layout.heading_case == "upper" else text


def _kv(label: str, value: str, layout: Layout) -> str:
    return f"{label}{layout.key_separator} {value}"


def _render_header(facts: FundFacts, layout: Layout, shown: set[str], words: dict[str, str]) -> list[str]:
    title = words["title_kid"] if layout.doc_type == "kid" else words["title_kiid"]
    lines = [title, "", facts.fund_name, ""]
    if layout.doc_type == "kid":
        lines += [_heading(words["purpose"], layout), words["purpose_body"], ""]
    if "isin" in shown:
        lines.append(_kv(words["isin"], facts.isin, layout))
    if "management_company" in shown:
        lines.append(_kv(words["manufacturer"], facts.management_company, layout))
    if "currency" in shown:
        lines.append(_kv(words["currency"], facts.currency, layout))
    if "domicile" in shown:
        lines.append(_kv(words["domicile"], facts.domicile, layout))
    return lines


def _render_objective(
    layout: Layout, shown: set[str], facts: FundFacts, objective: str, words: dict[str, str]
) -> list[str]:
    lines = [_heading(words["objective"], layout), objective]
    if "benchmark" in shown:
        lines.append(_kv(words["benchmark"], facts.benchmark, layout))
    return lines


def _render_risk(facts: FundFacts, layout: Layout, words: dict[str, str]) -> list[str]:
    level = facts.risk_level
    lines = [_heading(words["risk"], layout)]
    if layout.risk_style == "scale":
        scale = " ".join(f"[{n}]" if n == level else str(n) for n in range(1, 8))
        lines += [f"{words['lower_risk']}  {scale}  {words['higher_risk']}"]
    elif layout.risk_style == "outof":
        lines.append(f"{words['risk']}{layout.key_separator} {level} / 7")
    else:
        template = {
            "en": f"We have classified this product as risk class {level} on a scale from 1 to 7.",
            "de": f"Wir haben dieses Produkt in die Risikoklasse {level} von 7 eingestuft.",
            "fr": f"Nous avons classé ce produit dans la classe de risque {level} sur 7.",
            "nl": f"Wij hebben dit product ingedeeld in risicoklasse {level} van 7.",
        }
        lines.append(template[layout.language])
    return lines


def _render_scenarios(facts: FundFacts, layout: Layout, words: dict[str, str]) -> list[str]:
    lines = [_heading(words["scenarios"], layout), f"{words['scenario_intro']} {facts.currency}"]
    for name in ("stress", "unfavourable", "moderate", "favourable"):
        value, annual = facts.scenarios[name]
        money = format_money(value, layout.number_style)
        percent = format_percent(annual, layout.number_style)
        if layout.scenario_style == "prose":
            lines.append(f"{words[name]}{layout.key_separator} you could get back {money} ({percent} per year).")
        else:
            lines.append(f"{words[name]:<28}{money:>14}{percent:>12}")
    return lines


def _render_costs(facts: FundFacts, layout: Layout, shown: set[str], words: dict[str, str]) -> list[str]:
    style = layout.number_style
    items: list[tuple[str, str]] = []
    if "entry_charge_pct" in shown:
        items.append((words["entry"], format_percent(facts.entry_charge_pct, style)))
    if "exit_charge_pct" in shown:
        items.append((words["exit"], format_percent(facts.exit_charge_pct, style)))
    items.append((words["ongoing"], format_percent(facts.ongoing_charges_pct, style, allow_bps=True)))
    if "transaction_costs_pct" in shown:
        items.append((words["transaction"], format_percent(facts.transaction_costs_pct, style, allow_bps=True)))
    if "performance_fee_pct" in shown:
        items.append((words["performance_fee"], format_percent(facts.performance_fee_pct, style)))

    lines = [_heading(words["costs"], layout)]
    if layout.charge_style == "table":
        lines += [f"{label:<32}{value:>12}" for label, value in items]
    elif layout.charge_style == "bullets":
        lines += [f"- {label}{layout.key_separator} {value}" for label, value in items]
    else:
        sentence = COST_SENTENCE[layout.language]
        lines.append(" ".join(sentence.format(label=label, value=value) for label, value in items))
    return lines


def _render_holding(facts: FundFacts, layout: Layout, words: dict[str, str]) -> list[str]:
    period = format_years(facts.recommended_holding_period_years, layout.language)
    return [_heading(words["holding"], layout), _kv(words["rhp"], period, layout)]


def _render_practical(layout: Layout, rng: random.Random, words: dict[str, str]) -> list[str]:
    pool = DISTRACTORS[layout.language]
    return [_heading(words["practical"], layout), *rng.sample(pool, k=rng.randint(2, len(pool)))]


def choose_shown_fields(
    facts: FundFacts, layout: Layout, rng: random.Random, dropout: dict[str, float] | None = None
) -> set[str]:
    shown = set()
    for name, probability in (dropout or DROPOUT).items():
        if rng.random() >= probability:
            shown.add(name)
    if layout.doc_type == "kiid":
        shown.discard("transaction_costs_pct")
        shown.discard("performance_fee_pct")
    if facts.performance_fee_pct == 0.0 and rng.random() < 0.7:
        shown.discard("performance_fee_pct")
    return shown


def build_record(
    facts: FundFacts, layout: Layout, shown: set[str], sections: set[str], objective: str
) -> KidRecord:
    is_kid = layout.doc_type == "kid"
    scenarios = None
    if "scenarios" in sections:
        scenarios = PerformanceScenarios(
            **{
                name: Scenario(value=facts.scenarios[name][0], return_pct=facts.scenarios[name][1])
                for name in ("stress", "unfavourable", "moderate", "favourable")
            }
        )
    return KidRecord(
        fund_name=facts.fund_name,
        isin=facts.isin if "isin" in shown else None,
        currency=facts.currency if "currency" in shown else None,
        sri=facts.risk_level if is_kid else None,
        srri=facts.risk_level if not is_kid else None,
        ongoing_charges_pct=facts.ongoing_charges_pct if "costs" in sections else None,
        entry_charge_pct=facts.entry_charge_pct if "entry_charge_pct" in shown and "costs" in sections else None,
        exit_charge_pct=facts.exit_charge_pct if "exit_charge_pct" in shown and "costs" in sections else None,
        transaction_costs_pct=(
            facts.transaction_costs_pct if "transaction_costs_pct" in shown and "costs" in sections else None
        ),
        performance_fee_pct=(
            facts.performance_fee_pct if "performance_fee_pct" in shown and "costs" in sections else None
        ),
        recommended_holding_period_years=(
            facts.recommended_holding_period_years if "holding" in sections else None
        ),
        investment_objective=clean_text(objective) if "objective" in sections else None,
        benchmark=facts.benchmark if "benchmark" in shown else None,
        domicile=facts.domicile if "domicile" in shown else None,
        management_company=facts.management_company if "management_company" in shown else None,
        scenarios=scenarios,
    )


def render(
    facts: FundFacts,
    layout: Layout,
    rng: random.Random,
    vocabulary: str = "known",
    dropout: dict[str, float] | None = None,
) -> GeneratedDocument:
    shown = choose_shown_fields(facts, layout, rng, dropout)
    words = build_labels(layout.language, rng, vocabulary)
    sections = set(layout.sections)
    objective = objective_text(facts.strategy, facts.benchmark, layout.language, rng)
    blocks: list[list[str]] = []
    for section in layout.sections:
        if section == "header":
            blocks.append(_render_header(facts, layout, shown, words))
        elif section == "objective":
            blocks.append(_render_objective(layout, shown, facts, objective, words))
        elif section == "risk":
            blocks.append(_render_risk(facts, layout, words))
        elif section == "scenarios":
            blocks.append(_render_scenarios(facts, layout, words))
        elif section == "costs":
            blocks.append(_render_costs(facts, layout, shown, words))
        elif section == "holding":
            blocks.append(_render_holding(facts, layout, words))
        elif section == "practical":
            blocks.append(_render_practical(layout, rng, words))

    text = "\n\n".join("\n".join(block) for block in blocks)
    record = build_record(facts, layout, shown, sections, objective)
    return GeneratedDocument(
        text=text,
        record=record,
        layout=layout.name,
        doc_type=layout.doc_type,
        language=layout.language,
        labels=words,
    )

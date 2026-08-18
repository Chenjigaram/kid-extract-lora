import random

from kidextract.corpus.facts import synthesise_fund
from kidextract.corpus.layouts import LAYOUTS
from kidextract.corpus.noise import inject_noise
from kidextract.corpus.render import format_percent, render
from kidextract.schema import TEXT_FIELDS

BPS_CAPABLE_FIELDS = ("ongoing_charges_pct", "transaction_costs_pct")
PLAIN_PERCENT_FIELDS = ("entry_charge_pct", "exit_charge_pct", "performance_fee_pct")


def protected_values(doc, layout):
    values = [getattr(doc.record, name) for name in TEXT_FIELDS]
    for name in BPS_CAPABLE_FIELDS:
        value = getattr(doc.record, name)
        if value is not None:
            values.append(format_percent(value, layout.number_style, allow_bps=True))
    for name in PLAIN_PERCENT_FIELDS:
        value = getattr(doc.record, name)
        if value is not None:
            values.append(format_percent(value, layout.number_style))
    return [value for value in values if value]


def noisy_corpus(rate=0.05, count=6):
    rng = random.Random(33)
    out = []
    for layout in LAYOUTS:
        for _ in range(count):
            doc = render(synthesise_fund(rng), layout, rng)
            guards = protected_values(doc, layout)
            text = inject_noise(doc.text, guards, doc.record.fund_name, doc.language, rng, rate=rate)
            out.append((doc, layout, text, guards))
    return out


def test_protected_values_survive_noise():
    for doc, _layout, text, guards in noisy_corpus():
        for guard in guards:
            assert guard in text, f"{guard!r} destroyed in {doc.layout}"


def test_noise_actually_changes_the_document():
    changed = sum(1 for doc, _l, text, _g in noisy_corpus() if text != doc.text)
    assert changed > 0


def test_zero_rate_still_adds_only_layout_noise():
    for doc, _layout, text, guards in noisy_corpus(rate=0.0):
        for guard in guards:
            assert guard in text


def test_noise_is_reproducible():
    doc = render(synthesise_fund(random.Random(2)), LAYOUTS[0], random.Random(2))
    a = inject_noise(doc.text, [], doc.record.fund_name, "en", random.Random(5))
    b = inject_noise(doc.text, [], doc.record.fund_name, "en", random.Random(5))
    assert a == b

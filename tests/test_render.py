import random

import pytest

from kidextract.corpus.facts import synthesise_fund
from kidextract.corpus.layouts import LAYOUTS, LAYOUTS_BY_NAME
from kidextract.corpus.render import format_percent, render
from kidextract.corpus.vocabulary import all_labels_for

SCALAR_TEXT_FIELDS = ("fund_name", "isin", "currency", "benchmark", "domicile", "management_company")
PERCENT_FIELDS = ("entry_charge_pct", "exit_charge_pct", "performance_fee_pct")
BPS_CAPABLE_FIELDS = ("ongoing_charges_pct", "transaction_costs_pct")


def documents(count=8):
    rng = random.Random(21)
    return [render(synthesise_fund(rng), layout, rng) for layout in LAYOUTS for _ in range(count)]


@pytest.fixture(scope="module")
def corpus():
    return documents()


def test_text_values_appear_in_the_document(corpus):
    for doc in corpus:
        for field in SCALAR_TEXT_FIELDS:
            value = getattr(doc.record, field)
            if value is not None:
                assert value in doc.text, f"{field} missing from {doc.layout}"


def test_objective_appears_verbatim(corpus):
    for doc in corpus:
        if doc.record.investment_objective is not None:
            assert doc.record.investment_objective in doc.text


def test_percentages_appear_in_the_layout_notation(corpus):
    for doc in corpus:
        layout = LAYOUTS_BY_NAME[doc.layout]
        for field in PERCENT_FIELDS:
            value = getattr(doc.record, field)
            if value is not None:
                assert format_percent(value, layout.number_style) in doc.text
        for field in BPS_CAPABLE_FIELDS:
            value = getattr(doc.record, field)
            if value is not None:
                assert format_percent(value, layout.number_style, allow_bps=True) in doc.text


def test_risk_field_matches_document_type(corpus):
    for doc in corpus:
        if doc.doc_type == "kid":
            assert doc.record.sri is not None and doc.record.srri is None
        else:
            assert doc.record.srri is not None and doc.record.sri is None


def test_kiid_documents_carry_no_priips_scenarios(corpus):
    for doc in corpus:
        if doc.doc_type == "kiid":
            assert doc.record.scenarios is None


def test_absent_cost_labels_are_not_rendered(corpus):
    for doc in corpus:
        for field, key in (("exit_charge_pct", "exit"), ("transaction_costs_pct", "transaction")):
            if getattr(doc.record, field) is None:
                assert doc.labels[key] not in doc.text


def test_label_wording_varies_between_documents(corpus):
    wordings = {doc.labels["ongoing"] for doc in corpus}
    assert len(wordings) > 1
    assert wordings <= all_labels_for("ongoing")


def test_every_layout_produces_a_substantial_document(corpus):
    assert all(len(doc.text) > 500 for doc in corpus)


def test_rendering_is_reproducible():
    a = render(synthesise_fund(random.Random(9)), LAYOUTS[0], random.Random(9))
    b = render(synthesise_fund(random.Random(9)), LAYOUTS[0], random.Random(9))
    assert a.text == b.text and a.record == b.record


def test_all_layouts_are_exercised(corpus):
    assert {doc.layout for doc in corpus} == {layout.name for layout in LAYOUTS}

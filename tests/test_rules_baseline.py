import random

import pytest

from kidextract.corpus.facts import synthesise_fund
from kidextract.corpus.layouts import LAYOUTS
from kidextract.corpus.render import render
from kidextract.evaluation.baselines.rules import extract
from kidextract.schema import KidRecord


@pytest.fixture(scope="module")
def pairs():
    rng = random.Random(77)
    out = []
    for layout in LAYOUTS:
        for _ in range(4):
            doc = render(synthesise_fund(rng), layout, rng)
            out.append((doc, extract(doc.text)))
    return out


def test_output_always_validates_against_the_schema(pairs):
    for _doc, prediction in pairs:
        KidRecord.model_validate(prediction)


def test_risk_indicator_is_recovered(pairs):
    for doc, prediction in pairs:
        expected = doc.record.sri if doc.doc_type == "kid" else doc.record.srri
        actual = prediction["sri"] if doc.doc_type == "kid" else prediction["srri"]
        assert actual == expected, doc.layout


def test_ongoing_charges_are_recovered(pairs):
    for doc, prediction in pairs:
        assert prediction["ongoing_charges_pct"] == doc.record.ongoing_charges_pct, doc.layout


def test_isin_is_recovered(pairs):
    for doc, prediction in pairs:
        assert prediction["isin"] == doc.record.isin, doc.layout


def test_scenarios_are_recovered_when_present(pairs):
    for doc, prediction in pairs:
        if doc.record.scenarios is None:
            continue
        for name in ("stress", "unfavourable", "moderate", "favourable"):
            gold = getattr(doc.record.scenarios, name)
            assert prediction["scenarios"][name]["value"] == pytest.approx(gold.value, abs=0.01), doc.layout


def test_empty_input_does_not_crash():
    prediction = extract("")
    KidRecord.model_validate(prediction)
    assert prediction["isin"] is None

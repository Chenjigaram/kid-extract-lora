import random

import pytest

from kidextract.corpus.facts import synthesise_fund
from kidextract.corpus.layouts import LAYOUTS
from kidextract.corpus.render import render
from kidextract.corpus.vocabulary import HELD_OUT, KNOWN, VARIANTS, all_labels_for, build_labels

VARIABLE_KEYS = tuple(VARIANTS["en"])


def test_all_languages_define_the_same_keys():
    keys = {frozenset(variants) for variants in VARIANTS.values()}
    assert len(keys) == 1


@pytest.mark.parametrize("key", VARIABLE_KEYS)
def test_known_and_held_out_pools_are_disjoint(key):
    assert not all_labels_for(key) & all_labels_for(key, "held_out")


@pytest.mark.parametrize("key", VARIABLE_KEYS)
def test_both_pools_are_non_empty(key):
    assert all_labels_for(key) and all_labels_for(key, "held_out")


def test_known_pool_excludes_the_reserved_variant():
    for language, variants in VARIANTS.items():
        for key, options in variants.items():
            assert options[-1] in HELD_OUT[language][key]
            assert options[-1] not in KNOWN[language][key]


def test_labels_are_drawn_from_the_requested_pool():
    rng = random.Random(6)
    for _ in range(40):
        labels = build_labels("de", rng, "held_out")
        assert labels["ongoing"] in all_labels_for("ongoing", "held_out")


def test_documents_use_the_requested_vocabulary():
    rng = random.Random(12)
    doc = render(synthesise_fund(rng), LAYOUTS[0], rng, vocabulary="held_out")
    assert doc.labels["ongoing"] in all_labels_for("ongoing", "held_out")
    assert doc.labels["ongoing"] in doc.text


def test_held_out_wordings_never_appear_in_known_documents():
    rng = random.Random(13)
    reserved = all_labels_for("ongoing", "held_out")
    for _ in range(60):
        doc = render(synthesise_fund(rng), LAYOUTS[0], rng, vocabulary="known")
        assert doc.labels["ongoing"] not in reserved

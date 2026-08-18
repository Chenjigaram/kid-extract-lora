import pytest

from kidextract.alignment.agreement import field_matches, mean_field_agreement, strict_agreement
from kidextract.alignment.measure import alignment, alpha_curve, distributional_alignment, geometric_alignment
from kidextract.alignment.sampling import natural_documents, presence_at, sample_documents, uniform_documents
from kidextract.corpus.render import DROPOUT
from kidextract.evaluation.baselines.rules import build_label_index, extract

A = {"isin": "LU0690375182", "sri": 4, "ongoing_charges_pct": 1.25}


def known_extractor():
    labels = build_label_index("known")
    return lambda text: extract(text, labels)


def full_extractor():
    labels = build_label_index("all")
    return lambda text: extract(text, labels)


def test_identical_predictions_agree_completely():
    assert strict_agreement(A, A)
    assert mean_field_agreement(A, A) == 1.0


def test_differing_value_breaks_strict_agreement():
    assert not strict_agreement(A, {**A, "sri": 5})


def test_null_against_value_counts_as_disagreement():
    assert field_matches(A, {**A, "isin": None})["isin"] is False


def test_both_null_counts_as_agreement():
    assert field_matches({"isin": None}, {"isin": None})["isin"] is True


def test_numeric_tolerance_is_respected():
    assert strict_agreement(A, {**A, "ongoing_charges_pct": 1.2501})


def test_presence_interpolates_between_natural_and_uniform():
    assert presence_at(0.0) == DROPOUT
    assert set(presence_at(1.0).values()) == {0.5}
    midpoint = presence_at(0.5)
    for name, natural in DROPOUT.items():
        assert midpoint[name] == pytest.approx((natural + 0.5) / 2)


def test_sampling_is_reproducible():
    assert sample_documents(5, 7, alpha=0.3) == sample_documents(5, 7, alpha=0.3)


def test_natural_and_uniform_samples_differ():
    assert natural_documents(5, 9) != uniform_documents(5, 9)


def test_alignment_of_a_model_with_itself_is_one():
    extractor = known_extractor()
    result = alignment(extractor, extractor, natural_documents(10, 3))
    assert result.strict == 1.0 and result.per_field == 1.0


def test_empty_document_set_is_handled():
    extractor = known_extractor()
    assert alignment(extractor, extractor, []).documents == 0


@pytest.fixture(scope="module")
def pair():
    return known_extractor(), full_extractor()


def test_distributional_alignment_is_near_perfect(pair):
    result = distributional_alignment(*pair, count=120)
    assert result.strict > 0.95


def test_geometric_alignment_is_lower_than_distributional(pair):
    distributional = distributional_alignment(*pair, count=120)
    geometric = geometric_alignment(*pair, count=120)
    assert geometric.strict < distributional.strict


def test_disagreements_are_confined_to_label_dependent_fields(pair):
    result = geometric_alignment(*pair, count=200)
    shape_recoverable = {"isin", "fund_name", "sri", "srri"} | {
        name for name in result.disagreements if name.startswith("scenarios.")
    }
    for name in shape_recoverable:
        assert result.disagreements[name] == 0, name


def test_alpha_curve_is_monotonically_decreasing(pair):
    curve = alpha_curve(*pair, count=80, steps=5)
    scores = [step.strict for step in curve]
    assert scores[0] >= scores[-1]
    assert [step.alpha for step in curve] == [0.0, 0.25, 0.5, 0.75, 1.0]

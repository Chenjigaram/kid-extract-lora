import pytest

from kidextract.evaluation.grounding import is_grounded, numeric_surface_forms, score_grounding
from kidextract.evaluation.metrics import (
    ALL_FIELDS,
    Evaluation,
    FieldScore,
    flatten,
    score_document,
    values_match,
)

GOLD = {
    "fund_name": "Amundi Global Equity Fund",
    "isin": "LU0690375182",
    "sri": 4,
    "ongoing_charges_pct": 1.25,
    "entry_charge_pct": None,
    "scenarios": {"moderate": {"value": 12500.0, "return_pct": 4.6}},
}


def test_flatten_expands_scenarios():
    flat = flatten(GOLD)
    assert flat["scenarios.moderate.value"] == 12500.0
    assert flat["scenarios.stress.value"] is None


def test_flatten_of_garbage_gives_all_nulls():
    assert set(flatten(None).values()) == {None}
    assert set(flatten("not a dict").values()) == {None}


@pytest.mark.parametrize(
    ("name", "gold", "prediction", "expected"),
    [
        ("ongoing_charges_pct", 1.25, 1.2501, True),
        ("ongoing_charges_pct", 1.25, 1.3, False),
        ("scenarios.moderate.value", 12500.0, 12500.005, True),
        ("sri", 4, 4.0, True),
        ("sri", 4, 5, False),
        ("fund_name", "Amundi  Fund ", "amundi fund", True),
        ("isin", "LU0690375182", "LU0690375183", False),
        ("currency", "EUR", 3, False),
    ],
)
def test_value_matching(name, gold, prediction, expected):
    assert values_match(name, gold, prediction) is expected


def test_perfect_prediction_scores_one():
    evaluation = Evaluation()
    score_document(evaluation, GOLD, GOLD)
    assert evaluation.exact_match_rate == 1.0
    assert evaluation.micro_f1 == 1.0


def test_missing_value_is_a_false_negative():
    evaluation = Evaluation()
    score_document(evaluation, GOLD, {**GOLD, "isin": None})
    assert evaluation.per_field["isin"].false_negative == 1
    assert evaluation.exact_match_rate == 0.0


def test_inventing_a_value_is_a_false_positive():
    evaluation = Evaluation()
    score_document(evaluation, GOLD, {**GOLD, "entry_charge_pct": 2.0})
    assert evaluation.per_field["entry_charge_pct"].false_positive == 1
    assert evaluation.per_field["entry_charge_pct"].null_accuracy == 0.0


def test_wrong_value_counts_against_both_precision_and_recall():
    evaluation = Evaluation()
    score_document(evaluation, GOLD, {**GOLD, "sri": 6})
    score = evaluation.per_field["sri"]
    assert score.false_positive == 1 and score.false_negative == 1 and score.true_positive == 0


def test_unparsed_prediction_scores_zero_without_crashing():
    evaluation = Evaluation()
    score_document(evaluation, GOLD, None)
    assert evaluation.micro_f1 == 0.0
    assert evaluation.documents == 1


def test_empty_field_score_is_safe():
    score = FieldScore()
    assert score.precision == score.recall == score.f1 == 0.0
    assert score.null_accuracy == 1.0


def test_every_field_is_scored():
    evaluation = Evaluation()
    assert set(evaluation.per_field) == set(ALL_FIELDS)


@pytest.mark.parametrize(
    ("value", "form"),
    [(1.25, "1,25"), (1.25, "1.25"), (0.09, "9"), (12500.0, "12.500,00"), (5.0, "5")],
)
def test_numeric_surface_forms(value, form):
    assert form in numeric_surface_forms(value)


def test_grounding_accepts_values_present_in_the_document():
    text = "Ongoing charges 1,25 % ISIN: LU0690375182 risk 4 of 7"
    assert is_grounded("ongoing_charges_pct", 1.25, text)
    assert is_grounded("isin", "LU0690375182", text)
    assert is_grounded("sri", 4, text)


def test_grounding_rejects_invented_values():
    text = "Ongoing charges 1,25 %"
    assert not is_grounded("ongoing_charges_pct", 2.4, text)
    assert not is_grounded("isin", "LU0690375182", text)


def test_null_predictions_are_always_grounded():
    assert is_grounded("isin", None, "")


def test_hallucination_rate_counts_only_predicted_values():
    evaluation = Evaluation()
    score_grounding(evaluation, {"fund_name": "Ghost Fund", "isin": None}, "A real document")
    assert evaluation.predicted_values == 1
    assert evaluation.hallucination_rate == 1.0

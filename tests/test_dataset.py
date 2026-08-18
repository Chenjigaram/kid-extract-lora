import pytest

from kidextract.dataset.build import (
    HELD_OUT_LAYOUTS,
    TRAINING_LAYOUTS,
    build_all,
    default_plans,
    generate_split,
    read_jsonl,
    write_jsonl,
)
from kidextract.dataset.prompts import build_messages, parse_prediction, target_json
from kidextract.schema import KidRecord


@pytest.fixture(scope="module")
def splits(tmp_path_factory):
    directory = tmp_path_factory.mktemp("dataset")
    counts = build_all(directory, train=90, validation=30, test=30)
    data = {name: read_jsonl(directory / f"{name}.jsonl") for name in counts}
    return data


def test_every_split_has_the_requested_size(splits):
    assert [len(rows) for rows in splits.values()] == [90, 30, 30, 30]


def test_training_layouts_exclude_the_held_out_ones(splits):
    assert {row["layout"] for row in splits["train"]} <= set(TRAINING_LAYOUTS)


def test_unseen_split_uses_only_held_out_layouts(splits):
    assert {row["layout"] for row in splits["test_unseen_layout"]} <= set(HELD_OUT_LAYOUTS)


def test_layout_sets_do_not_overlap():
    assert not set(TRAINING_LAYOUTS) & set(HELD_OUT_LAYOUTS)


@pytest.mark.parametrize("other", ["validation", "test_seen", "test_unseen_layout"])
def test_no_fund_appears_in_training_and_evaluation(splits, other):
    def isins(name):
        return {row["target"]["isin"] for row in splits[name] if row["target"]["isin"]}

    assert not isins("train") & isins(other)


def test_every_target_validates_against_the_schema(splits):
    for rows in splits.values():
        for row in rows:
            KidRecord.model_validate(row["target"])


def test_ids_are_unique(splits):
    for name, rows in splits.items():
        assert len({row["id"] for row in rows}) == len(rows), name


def test_targets_round_trip_through_the_parser(splits):
    for row in splits["train"][:20]:
        record = KidRecord.model_validate(row["target"])
        assert parse_prediction(target_json(record)) == row["target"]


def test_prompt_contains_the_document(splits):
    row = splits["train"][0]
    messages = build_messages(row["text"])
    assert row["text"] in messages[-1]["content"]
    assert messages[0]["role"] == "system"


def test_few_shot_prompt_alternates_roles(splits):
    rows = splits["train"][:2]
    examples = [(r["text"], target_json(KidRecord.model_validate(r["target"]))) for r in rows]
    roles = [m["role"] for m in build_messages("doc", examples)]
    assert roles == ["system", "user", "assistant", "user", "assistant", "user"]


def test_jsonl_round_trip(tmp_path):
    plan = default_plans(5, 1, 1)[0]
    path = tmp_path / "rows.jsonl"
    written = write_jsonl(path, generate_split(plan))
    assert written == len(read_jsonl(path)) == 5


def test_generation_is_deterministic():
    plan = default_plans(6, 1, 1)[0]
    assert list(generate_split(plan)) == list(generate_split(plan))

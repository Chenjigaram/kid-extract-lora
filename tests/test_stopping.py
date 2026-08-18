import pytest

torch = pytest.importorskip("torch")


class FakeTokenizer:
    def __init__(self, pieces):
        self.pieces = pieces

    def decode(self, ids, skip_special_tokens=True):
        return "".join(self.pieces[int(i)] for i in ids)


def criterion(pieces, prompt_length):
    from kidextract.evaluation.hf_model import ClosedJsonObject

    return ClosedJsonObject(FakeTokenizer(pieces), prompt_length)


def ids(values):
    return torch.tensor([values])


def test_stops_when_the_object_closes():
    pieces = {0: "P", 1: "{", 2: '"a":1', 3: "}"}
    stop = criterion(pieces, prompt_length=1)
    assert stop(ids([0, 1, 2, 3]), None) is True


def test_does_not_stop_while_the_object_is_open():
    pieces = {0: "P", 1: "{", 2: '"a":1'}
    stop = criterion(pieces, prompt_length=1)
    assert stop(ids([0, 1, 2]), None) is False


def test_handles_nested_objects():
    pieces = {0: "P", 1: "{", 2: '"s":{', 3: '"v":1}', 4: "}"}
    stop = criterion(pieces, prompt_length=1)
    assert stop(ids([0, 1, 2, 3]), None) is False
    assert stop(ids([0, 1, 2, 3, 4]), None) is True


def test_ignores_text_before_the_first_brace():
    pieces = {0: "P", 1: "here you go: ", 2: "{", 3: "}"}
    stop = criterion(pieces, prompt_length=1)
    assert stop(ids([0, 1, 2, 3]), None) is True


def test_does_not_stop_without_any_brace():
    pieces = {0: "P", 1: "no json at all"}
    stop = criterion(pieces, prompt_length=1)
    assert stop(ids([0, 1]), None) is False

import json

import pytest

from kidextract.cli.label import strip_comments, ungrounded_fields
from kidextract.ingest.pdf import normalise_document


def test_normalise_collapses_blank_runs():
    assert normalise_document("A\n\n\n\nB") == "A\n\nB"


def test_normalise_strips_soft_hyphens_and_padding():
    assert normalise_document("  spa­ced   out  ") == "spaced out"


def test_normalise_of_empty_input():
    assert normalise_document("") == ""


def test_strip_comments_removes_annotation_lines():
    body = '// note\n{"a": 1}\n  // indented note'
    assert json.loads(strip_comments(body)) == {"a": 1}


def test_strip_comments_keeps_urls_inside_values():
    body = '{"a": "https://example.com"}'
    assert json.loads(strip_comments(body)) == {"a": "https://example.com"}


def test_ungrounded_fields_flags_invented_values():
    text = "Ongoing charges 1.25% ISIN LU0690375182"
    prediction = {"ongoing_charges_pct": 1.25, "isin": "LU0690375182", "fund_name": "Invented Fund"}
    assert ungrounded_fields(prediction, text) == ["fund_name"]


def test_ungrounded_fields_ignores_nulls():
    assert ungrounded_fields({"isin": None}, "anything") == []


@pytest.mark.parametrize("engine", ["pdfplumber", "pypdf"])
def test_missing_pdf_raises_a_clear_error(tmp_path, engine):
    from kidextract.ingest.pdf import extract_text

    with pytest.raises(RuntimeError, match="could not read"):
        extract_text(tmp_path / "nope.pdf", engine)

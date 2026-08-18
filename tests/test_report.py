import json

from kidextract.evaluation.report import build_report, field_table, headline_table

SUMMARY = {
    "system": "rules",
    "split": "test_seen",
    "documents": 10,
    "micro_f1": 0.9,
    "macro_f1": 0.85,
    "exact_match": 0.4,
    "schema_validity": 1.0,
    "hallucination_rate": 0.0,
    "median_latency_seconds": 0.004,
    "per_field": {
        "isin": {"precision": 1.0, "recall": 1.0, "f1": 1.0, "null_accuracy": 1.0, "support": 10},
        "sri": {"precision": 0.5, "recall": 0.5, "f1": 0.5, "null_accuracy": 1.0, "support": 10},
    },
}


def test_headline_table_has_a_row_per_system():
    table = headline_table([SUMMARY])
    assert table.count("\n") == 2
    assert "rules" in table


def test_field_table_sorts_by_f1_descending():
    table = field_table(SUMMARY)
    assert table.index("isin") < table.index("sri")


def test_build_report_reads_summaries_from_disk(tmp_path):
    (tmp_path / "rules__test_seen.json").write_text(json.dumps(SUMMARY))
    report = build_report(tmp_path)
    assert "# Evaluation results" in report
    assert "## rules on test_seen" in report


def test_build_report_handles_an_empty_directory(tmp_path):
    assert "No evaluation summaries" in build_report(tmp_path)


def test_build_report_ignores_unrelated_json(tmp_path):
    (tmp_path / "notes.json").write_text(json.dumps({"hello": "world"}))
    assert "No evaluation summaries" in build_report(tmp_path)

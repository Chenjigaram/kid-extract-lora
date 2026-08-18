#!/usr/bin/env bash
set -euo pipefail

PYTHON="${PYTHON:-.venv/bin/python}"
SPLIT="${SPLIT:-data/processed/test_unseen_layout.jsonl}"
ADAPTER="${ADAPTER:-runs/smollm2-135m-r16/adapter}"
LIMIT="${LIMIT:-40}"
THREADS="${THREADS:-4}"
OUT="${OUT:-reports}"

echo "benchmark on $(basename "$SPLIT"), $LIMIT documents, $THREADS threads"

$PYTHON -m kidextract.cli.evaluate --split "$SPLIT" --system rules --out "$OUT"

$PYTHON -m kidextract.cli.evaluate --split "$SPLIT" --system zero-shot \
    --threads "$THREADS" --limit "$LIMIT" --out "$OUT"

$PYTHON -m kidextract.cli.evaluate --split "$SPLIT" --system few-shot --shots 2 \
    --threads "$THREADS" --limit "$LIMIT" --out "$OUT"

if [ -d "$ADAPTER" ]; then
    $PYTHON -m kidextract.cli.evaluate --split "$SPLIT" --system finetuned --adapter "$ADAPTER" \
        --threads "$THREADS" --limit "$LIMIT" --out "$OUT"
else
    echo "no adapter at $ADAPTER, skipping the fine-tuned system"
fi

$PYTHON -m kidextract.cli.report --dir "$OUT" --out "$OUT/RESULTS.md"

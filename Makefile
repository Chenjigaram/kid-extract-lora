PYTHON ?= .venv/bin/python
THREADS ?= 4
DATA ?= data/processed
SPLIT ?= $(DATA)/test_unseen_layout.jsonl
ADAPTER ?= runs/smollm2-135m-r16/adapter

.PHONY: install test lint data rules zero-shot few-shot finetuned train sweep report clean

install:
	uv venv --python 3.12 .venv
	uv pip install --python $(PYTHON) -e ".[dev,plots,hub]"

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check src tests

data:
	$(PYTHON) -m kidextract.cli.build_dataset --out $(DATA) --train 1500 --validation 300 --test 300

rules:
	$(PYTHON) -m kidextract.cli.evaluate --split $(SPLIT) --system rules

zero-shot:
	$(PYTHON) -m kidextract.cli.evaluate --split $(SPLIT) --system zero-shot --threads $(THREADS) --limit 100

few-shot:
	$(PYTHON) -m kidextract.cli.evaluate --split $(SPLIT) --system few-shot --shots 2 --threads $(THREADS) --limit 100

train:
	$(PYTHON) -m kidextract.cli.train --config configs/base.yaml --threads $(THREADS)

finetuned:
	$(PYTHON) -m kidextract.cli.evaluate --split $(SPLIT) --system finetuned --adapter $(ADAPTER) --threads $(THREADS) --limit 100

sweep:
	$(PYTHON) -m kidextract.cli.sweep --spec configs/sweep.yaml --threads $(THREADS) --skip-generation --table reports/SWEEP.md

report:
	$(PYTHON) -m kidextract.cli.report --dir reports --out reports/RESULTS.md

clean:
	rm -rf runs reports/*.json reports/*.jsonl

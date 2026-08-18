PYTHON ?= .venv/bin/python
THREADS ?= 4
DATA ?= data/processed
SPLIT ?= $(DATA)/test_unseen_layout.jsonl
ADAPTER ?= runs/smollm2-135m-r16/adapter

.PHONY: install test lint smoke data rules zero-shot few-shot finetuned train sweep benchmark plots report clean

install:
	uv venv --python 3.12 .venv
	uv pip install --python $(PYTHON) -e ".[dev,plots,hub]"

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check src tests

smoke:
	$(PYTHON) -m kidextract.cli.build_dataset --out /tmp/kid-smoke --train 60 --validation 20 --test 40
	$(PYTHON) -m kidextract.cli.evaluate --split /tmp/kid-smoke/test_unseen_layout.jsonl --system rules --out /tmp/kid-smoke/reports

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

benchmark:
	PYTHON=$(PYTHON) THREADS=$(THREADS) SPLIT=$(SPLIT) ADAPTER=$(ADAPTER) scripts/benchmark.sh

plots:
	$(PYTHON) -m kidextract.cli.plot --results runs/sweep/results.json --out reports/figures

report:
	$(PYTHON) -m kidextract.cli.report --dir reports --out reports/RESULTS.md

clean:
	rm -rf runs reports/*.json reports/*.jsonl

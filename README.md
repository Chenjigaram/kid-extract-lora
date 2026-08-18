# kid-extract

Structured extraction from European fund disclosure documents — PRIIPs Key Information
Documents and UCITS Key Investor Information Documents — using a small language model
fine-tuned with LoRA and run entirely on CPU.

## Why fine-tune instead of retrieve

Retrieval answers questions the model does not know the answer to. That is not the problem
here. The document is already in the context window; nothing is missing. What goes wrong
with a prompted small model is behaviour, not knowledge:

- it drifts on JSON structure, closing an object early or emitting prose around it
- it renames fields between documents, so downstream code cannot rely on the keys
- it guesses when a field is absent instead of returning null, which is the expensive
  failure mode when the output feeds a risk or cost calculation

Those are format and behaviour problems, and they are what supervised fine-tuning fixes.
The task also runs over thousands of documents, so cost and latency per document dominate
the decision. A knowledge gap points to retrieval; a format-and-behaviour problem at volume
points to fine-tuning. This is the second case.

## Why the documents are generated

There is no public corpus of KIDs. ESMA states that where a member state does not require
KID notification, no central European database of these documents exists, and no dataset on
Hugging Face or Kaggle fills the gap. Collecting a few thousand would mean scraping fifty
provider websites.

So the corpus is generated instead, from real fund attributes. The generator renders fund
facts into documents across twelve provider layouts and four languages, and the ground truth
falls out of the rendering rather than being annotated afterwards. Labels are therefore exact
by construction, at any volume, with no annotation cost and no teacher model.

The cost of that choice is honest and stated: generated documents are more regular than real
ones, so absolute scores here are optimistic relative to production. Two things address it.
First, the evaluation split holds back both layouts and vocabulary (below). Second, the
project reserves a slot for a hand-labelled set of real documents, which is the number that
should be believed.

## The part that makes the evaluation mean something

A hand-written regular expression extractor scores **0.978 micro F1** on documents whose
layouts and label wordings it already knows. On generated data, rules are extremely strong,
and a benchmark that only reported that number would be measuring template memorisation.

Real providers do not agree on what to call a field. Ongoing charges appear as *ongoing
costs*, *running costs*, *laufende Gebühren*, *frais courants*, *beheerkosten*. So each
document samples its own label wording, and the pools are split: the last wording of every
field is reserved and appears **only** in the evaluation split, alongside three layouts held
out of training entirely.

Against layouts and wordings it has never seen, the same rule extractor scores:

| Split | Micro F1 | Macro F1 | Exact match |
| --- | --- | --- | --- |
| `test_seen` — known layouts and wordings | 0.978 | 0.975 | 0.650 |
| `test_unseen_layout` — new layouts, new wordings | 0.683 | 0.486 | 0.000 |

Every label-dependent field drops to zero. Only ISIN, the risk scale and the scenario table
survive, because those are recoverable by shape rather than by name. That collapse is the
gap the fine-tuned model exists to close, and it mirrors exactly what happens to a hand-built
extractor when a new provider appears.

## What is measured

- field-level precision, recall and F1 over 23 fields
- null accuracy per field — the share of genuinely absent fields correctly left empty
- schema validity — the share of outputs that parse and validate
- hallucination rate — predicted values whose notation appears nowhere in the source
- exact match over the whole record
- median latency and cost per document

A wrong value counts as both a false positive and a false negative, so guessing is never
cheaper than abstaining.

## Systems compared

| System | What it is |
| --- | --- |
| `rules` | Hand-written multilingual label matching. The floor. |
| `zero-shot` | Base SmolLM2 with the schema in the prompt. |
| `few-shot` | Base SmolLM2 with worked examples in the prompt. |
| `finetuned` | The same base model with a LoRA adapter. |

All four run on CPU and are scored by identical code on identical splits.

## Running it

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e ".[dev,plots,hub]"

python -m kidextract.cli.build_dataset --out data/processed --train 6000 --validation 500 --test 500
python -m kidextract.cli.evaluate --split data/processed/test_unseen_layout.jsonl --system rules
python -m kidextract.cli.train --config configs/base.yaml --threads 4
python -m kidextract.cli.evaluate --split data/processed/test_unseen_layout.jsonl \
    --system finetuned --adapter runs/smollm2-135m-r16/adapter
python -m kidextract.cli.report --dir reports --out reports/RESULTS.md
```

Grounding the generated funds in real data is optional. Download the Morningstar European
funds dataset from Kaggle and pass `--reference-csv`; real names, ISINs, charges and risk
ratings are used where present and only the missing attributes are synthesised.

## Layout

```
src/kidextract/
  schema.py          the extraction target, validated with pydantic
  normalize.py       parsing the value notations providers actually use
  corpus/            fund facts, layouts, vocabulary, rendering, noise
  dataset/           prompt format and split construction
  train/             LoRA configuration, training, hyperparameter sweep
  evaluation/        metrics, grounding, baselines, reporting
```

## Licence

MIT. The generated corpus contains no proprietary or confidential material.

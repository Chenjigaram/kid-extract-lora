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

A hand-written regular expression extractor scores **0.983 micro F1** on documents whose
layouts and label wordings it already knows. On generated data, rules are extremely strong,
and a benchmark that only reported that number would be measuring template memorisation.

Real providers do not agree on what to call a field. Ongoing charges appear as *ongoing
costs*, *running costs*, *laufende Gebühren*, *frais courants*, *beheerkosten*. So each
document samples its own label wording, and the pools are split: the last wording of every
field is reserved and appears **only** in the evaluation split, alongside four layouts held
out of training entirely, one per language.

Against layouts and wordings it has never seen, the same rule extractor scores:

| Split | Micro F1 | Macro F1 | Exact match |
| --- | --- | --- | --- |
| `test_seen` — known layouts and wordings | 0.983 | 0.982 | 0.720 |
| `test_unseen_layout` — new layouts, new wordings | 0.643 | 0.514 | 0.000 |

Both rows are 50 documents, the same 50 every other system is scored on. Holding out one layout
per language means the split tests generalisation to unfamiliar layouts and wordings rather than
to an unfamiliar language.

Every label-dependent field drops to zero. Only ISIN, the risk scale and the scenario table
survive, because those are recoverable by shape rather than by name. That collapse is the
gap the fine-tuned model exists to close, and it mirrors exactly what happens to a hand-built
extractor when a new provider appears.

## What this actually costs on a laptop

Measured on an Intel i5-8365U, 4 cores, 4 threads, no GPU. These are the real numbers, not
estimates, and they are the constraint that shapes the whole project.

| Operation | Cost |
| --- | --- |
| Training, per example (135M, LoRA, ~850 tokens) | ~14 s |
| Evaluation forward pass, per example | ~2.2 s |
| Generation, per document (400 new tokens) | ~28 s |
| Peak resident memory during training | ~1.5 GB |
| Trainable parameters | 4.88 M of 139 M (3.5%) |

Two consequences follow, and both are designed around rather than ignored:

**A training run is an overnight job, not a coffee break.** 1500 examples for two epochs is
roughly twelve hours. `configs/base.yaml` is sized accordingly; increasing the corpus beyond
a few thousand examples is not useful on this hardware.

**The sweep cannot generate.** Seventeen configurations, each scored by generating on sixty
documents, is over eight hours of generation alone. So `make sweep` ranks configurations by
validation loss with `--skip-generation`, and only the winner is scored end to end with the
full metric suite. This is stated because ranking by loss and reporting F1 are not the same
thing, and pretending otherwise would be dishonest.

If you have a free Kaggle or Colab GPU, the same commands run there unchanged and roughly two
orders of magnitude faster. Nothing in this repository requires one.

### Sizing a run

Wall clock is set by the number of training examples; quality is set by the number of weight
updates. With `gradient_accumulation_steps: 4`, 1500 examples for one epoch is 375 updates and
about six hours — an overnight job.

A first run at 38 updates was measurably undertrained. Of four sampled documents one was
correct, one stopped early with unbalanced JSON, and two generated to the token cap without
ever closing the object. Raising the cap from 400 to 640 tokens changed nothing, which ruled
out truncation and left undertraining as the cause. If you shorten a run, expect schema
validity to be the first thing that suffers.

Generation stops as soon as brace depth returns to zero, so a well-formed object costs only
the tokens it needs and a runaway is bounded by the cap rather than always reaching it.

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

An early probe is worth stating up front: the base 135M model, prompted zero-shot with the
full field specification, produced **no parseable JSON at all** on the first four documents
tried. Micro F1 0.000, schema validity 0.000, at 28 seconds per document. That is the exact
failure mode fine-tuning is supposed to fix, and it is why the comparison table below is
worth building rather than assuming.

## Results

All systems scored on the same 50 documents, same code, same splits.

### Unseen layouts and unseen label wordings

| System | Micro F1 | Macro F1 | Exact | Schema valid | Hallucination | Latency |
| --- | --- | --- | --- | --- | --- | --- |
| **fine-tuned 135M** | **0.858** | **0.830** | 0.02 | 0.88 | 0.005 | 21.3 s |
| rules | 0.643 | 0.514 | 0.00 | 1.00 | 0.000 | 0.001 s |
| few-shot 135M | 0.169 | 0.155 | 0.00 | 0.50 | 0.491 | 40.0 s |
| zero-shot 135M | 0.000 | 0.000 | 0.00 | 0.00 | — | 28.1 s |

### Known layouts and wordings

| System | Micro F1 | Macro F1 | Exact | Schema valid | Latency |
| --- | --- | --- | --- | --- | --- |
| fine-tuned 135M | 0.988 | 0.988 | 0.82 | 1.00 | 21.1 s |
| rules | 0.983 | 0.982 | 0.72 | 1.00 | 0.001 s |

Fine-tuning takes the same 135M model from **producing no valid JSON at all** to 0.858 micro F1
on documents whose layout and vocabulary it has never seen. Prompting does not get there: the
base model zero-shot never closed a single object, and few-shot reached only half its outputs
being parseable while inventing **49% of the values it emitted**. That is the format-and-behaviour
argument, measured rather than asserted.

### Where each approach wins

The per-field split is the interesting part, and it does not favour one side everywhere.

| Fields where the fine-tune wins | F1 gain over rules |
| --- | --- |
| `recommended_holding_period_years` | +0.980 |
| `entry_charge_pct` | +0.945 |
| `management_company` | +0.941 |
| `benchmark` | +0.822 |
| `exit_charge_pct` | +0.810 |
| `investment_objective` | +0.796 |
| `ongoing_charges_pct` | +0.735 |
| `currency` | +0.508 |

Every one of those is a field the extractor finds by reading a label. When the wording changes,
regex scores exactly zero and the model keeps working.

| Fields where rules win | F1 gap |
| --- | --- |
| `isin` | −0.083 |
| `fund_name` | −0.061 |
| `scenarios.*.value` | −0.04 to 0.00 |
| `sri` | −0.014 |

Every one of those is recoverable by *shape* rather than by name: a checksummed identifier, the
line under the title, a numeric table, a bracketed digit on a 1-to-7 scale. A regular expression
is exact at those and the model merely near-exact. **A hybrid that takes ISIN and the risk scale
from rules and everything else from the model would beat both**, and that is a more useful
conclusion than declaring a winner.

### What the fine-tune is still bad at

`transaction_costs_pct` scores 0.078 and `domicile` 0.350 on unseen wordings. Schema validity
also drops from 1.00 to 0.88 once the layout is unfamiliar, so roughly one output in eight still
needs a retry. Exact match over all 23 fields at once is 0.02 — per-field accuracy of 0.86 does
not mean whole-record accuracy, and any pipeline built on this needs field-level validation
rather than trusting a record wholesale.

### Cost

Rules run in 1 ms per document; the model takes 21 s on four CPU threads — about 20,000× more
expensive. Where a hand-written extractor covers your providers, it is unbeatable on cost. The
model earns its keep exactly when a new provider appears and the regex silently returns nothing.

## Hyperparameter sweep

Seventeen configurations, one axis at a time against a fixed baseline, 200 training examples and
50 optimiser steps each — about 15 hours on four CPU threads. Ranked by validation loss, then the
five most informative adapters were scored by generation on 30 held-out documents.

| Axis | Spread in eval loss | Verdict |
| --- | --- | --- |
| epochs 1 to 3 | 0.079 | largest effect, but it is simply more steps |
| learning rate 5e-5 to 5e-4 | 0.295 | large, monotonic |
| alpha 8 to 64 | 0.208 | large, monotonic |
| target modules q,v to all seven | 0.186 | large, monotonic |
| **rank 4 to 64** | **0.005** | **no detectable effect across 16x the parameters** |
| dropout 0 to 0.1 | 0.003 | no detectable effect |

### Coverage beats width

The two ways to spend a parameter budget do not cost the same:

| Configuration | Trainable parameters | Eval loss | Micro F1 |
| --- | --- | --- | --- |
| rank 4, **all seven modules** | **1.22 M** | 0.0994 | 0.252 |
| rank 16, `q,k,v,o` only | 1.84 M | 0.2022 | - |
| rank 16, `q,v` only | 0.92 M | 0.2896 | **0.007** |
| rank 16, all seven (baseline) | 4.88 M | 0.1036 | 0.179 |

Rank sets the width of the adapter bottleneck; target modules decide which parts of the network
are adapted at all. Width does nothing here — rank 4 and rank 64 are indistinguishable across a
16x parameter range. Coverage does almost everything, and the MLP projections are where it comes
from.

Attention-only LoRA, the configuration from the original paper, is the worst tested: 0.007 micro
F1, **no valid JSON at all**, and half of every value it emitted absent from the source document.
Adapting attention alone cannot learn this task.

The practical result is that the smallest adapter is the right one — **rank 4 across all seven
modules**, 1.22 M parameters and roughly 5 MB, matching the 19.5 M-parameter rank 64 configuration
and beating the 4x larger baseline on real extraction.

### Validation loss ranked the configurations correctly

| Configuration | Eval loss | Micro F1 | Schema valid | Hallucination |
| --- | --- | --- | --- | --- |
| epochs=3 | 0.0241 | 0.800 | 0.90 | 0.028 |
| alpha=64 | 0.0566 | 0.459 | 0.33 | 0.109 |
| rank=4 | 0.0994 | 0.252 | 0.30 | 0.141 |
| baseline | 0.1036 | 0.179 | 0.20 | 0.140 |
| target modules q,v | 0.2896 | 0.007 | 0.00 | 0.500 |

The two rankings agree on all five. Skipping generation during the sweep and ranking by loss was
therefore sound for this task, which is worth knowing because generation costs eight hours across
seventeen runs and loss costs nothing.

### What the sweep cannot tell you

Every configuration that raises effective learning within 50 steps wins monotonically — learning
rate, alpha, and epochs are all the same lever. So the sweep ranks configurations by **how fast
they learn**, not by how good they end up. `alpha=64` and `lr=5e-4` may well overshoot at full
length.

The structural findings are more trustworthy than the scaling ones. Rank not mattering, and
coverage mattering a great deal, are properties of the task rather than of the budget.

Single seed throughout, so only large gaps mean anything. The 0.005 spread across the rank axis is
noise; the 0.186 across target modules is not.

## Running it

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e ".[dev,plots,hub]"

python -m kidextract.cli.build_dataset --out data/processed --train 6000 --validation 500 --test 500
python -m kidextract.cli.evaluate --split data/processed/test_unseen_layout.jsonl --system rules
python -m kidextract.cli.train --config configs/base.yaml --threads 4
scripts/benchmark.sh
```

`scripts/benchmark.sh` scores all four systems on the same split with the same document limit
and writes `reports/RESULTS.md`. Running them by hand invites comparing a hundred-document
baseline against a forty-document fine-tune.

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

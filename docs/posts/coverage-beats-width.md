# Where you attach a LoRA adapter matters more than how wide you make it

Most LoRA configurations start life copied from somewhere. `r=8` or `r=16` because that is what
the tutorial used, and `target_modules=["q_proj", "v_proj"]` because that is what the original
paper adapted. Then people tune the rank, because rank is the knob that looks like capacity.

I ran a seventeen-configuration ablation on a structured-extraction task and got the opposite
result on both counts. Rank did nothing at all. Target modules did almost everything.

## The setup

The task is extracting a fixed 23-field JSON schema from European fund disclosure documents —
PRIIPs KIDs and UCITS KIIDs — across four languages and twelve provider layouts. The base model
is `SmolLM2-135M-Instruct`. Everything trained on four CPU threads of a 2019 laptop; no GPU was
involved at any point.

Each configuration got 200 training examples and 50 optimiser steps, varying one axis at a time
against a fixed baseline. Ranked by validation loss, then the five most informative adapters were
re-scored by actually generating on 30 held-out documents — documents whose layout *and* label
wording were held out of training.

## Rank does nothing

| Rank | Trainable parameters | Eval loss |
| --- | --- | --- |
| 4 | 1,221,120 | 0.0994 |
| 8 | 2,442,240 | 0.1046 |
| 16 | 4,884,480 | 0.1036 |
| 32 | 9,768,960 | 0.1037 |
| 64 | 19,537,920 | 0.1037 |

Sixteen times the trainable parameters, from 1.2M to 19.5M. Total spread: **0.0052**. The ordering
is not even monotonic — rank 8 is worst and rank 4 is nominally best, which is what noise looks
like. Rank 16 and rank 32 agree to four decimal places while one has twice the parameters of the
other.

## Target modules do almost everything

| Target modules | Trainable parameters | Eval loss |
| --- | --- | --- |
| `q_proj, v_proj` | 921,600 | 0.2896 |
| `q_proj, k_proj, v_proj, o_proj` | 1,843,200 | 0.2022 |
| all seven, including MLP | 4,884,480 | 0.1036 |

Spread: **0.1860**, roughly thirty-six times the rank axis, and cleanly monotonic. Adapting the
MLP projections — `gate_proj`, `up_proj`, `down_proj` — is where the improvement comes from.

## The comparison that makes the point

Two ways to spend roughly the same parameter budget:

| Configuration | Trainable parameters | Eval loss |
| --- | --- | --- |
| **rank 4, all seven modules** | **1,221,120** | **0.0994** |
| rank 16, attention only (`q k v o`) | 1,843,200 | 0.2022 |

A third fewer parameters, less than half the loss. Width and coverage are not interchangeable
ways of buying capacity, and coverage is the one that pays.

## Attention-only LoRA did not merely score worse — it failed completely

Validation loss understates what happens. Generating on 30 held-out documents:

| Configuration | Micro F1 | Schema valid | Hallucination rate |
| --- | --- | --- | --- |
| `q_proj, v_proj` | **0.007** | **0.00** | **0.50** |
| rank 16, all seven | 0.179 | 0.20 | 0.14 |
| rank 4, all seven | 0.252 | 0.30 | 0.14 |

The attention-only adapter produced **no parseable JSON at all** across thirty documents, and half
of every value it emitted appeared nowhere in the source. It had not learned a worse version of
the task. It had not learned the task.

## Why this is plausible rather than surprising

Rank sets the width of the low-rank bottleneck — how much capacity the adapter has. Target modules
decide which parts of the network are adapted at all.

This task is one rigid schema with fixed field names. That is a low-complexity function, so even a
rank-4 bottleneck has ample capacity and adding more buys nothing. But producing a specific output
format is not something attention alone controls. The MLP blocks are where the token-level output
distribution gets shaped, and if you never touch them, no amount of attention-adapter width will
teach the model to emit a closing brace in the right place.

The corollary is that this result should generalise to format- and behaviour-shaped tasks, and
generalise less to tasks that genuinely need capacity.

## What this does not show

- **One task, one base model.** A 135M model on rigid structured output. Do not read this as a
  universal claim about LoRA.
- **One seed per configuration.** Only large gaps mean anything. The 0.005 rank spread is noise;
  the 0.186 coverage spread is not.
- **50 optimiser steps.** Short runs favour whatever learns fastest. The structural findings —
  rank not mattering, coverage mattering — are properties of the task rather than the budget, and
  I trust them more than the scaling results from the same sweep.
- **Synthetic documents.** The corpus is generated, because no public corpus of these documents
  exists. Absolute scores are optimistic; the comparison between configurations is not affected.

## Practical takeaway

If your task is about output format or behaviour rather than knowledge, adapt the MLP projections
and stop tuning rank. Start at `r=4` across all seven linear layers, spend the parameters you save
on more steps, and check the result by generating rather than by watching validation loss alone.

Code, data generator and the full seventeen-run ablation:
[github.com/Chenjigaram/kid-extract-lora](https://github.com/Chenjigaram/kid-extract-lora) ·
[results and charts](https://chenjigaram.github.io/kid-extract-lora/)

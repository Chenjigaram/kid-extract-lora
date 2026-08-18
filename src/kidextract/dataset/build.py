from __future__ import annotations

import json
import random
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ..corpus.facts import facts_from_reference, synthesise_fund
from ..corpus.layouts import LAYOUTS, LAYOUTS_BY_NAME, Layout
from ..corpus.noise import inject_noise
from ..corpus.render import format_percent, render
from ..schema import TEXT_FIELDS

HELD_OUT_LAYOUTS = ("amsterdam-bullets", "institutional-bps", "reordered-kid")
TRAINING_LAYOUTS = tuple(l.name for l in LAYOUTS if l.name not in HELD_OUT_LAYOUTS)

BPS_CAPABLE_FIELDS = ("ongoing_charges_pct", "transaction_costs_pct")
PLAIN_PERCENT_FIELDS = ("entry_charge_pct", "exit_charge_pct", "performance_fee_pct")


@dataclass(frozen=True)
class SplitPlan:
    name: str
    layouts: tuple[str, ...]
    size: int
    seed: int
    noise_rate: float = 0.02
    vocabulary: str = "known"


def default_plans(train: int, validation: int, test: int) -> tuple[SplitPlan, ...]:
    return (
        SplitPlan("train", TRAINING_LAYOUTS, train, seed=1001),
        SplitPlan("validation", TRAINING_LAYOUTS, validation, seed=2002),
        SplitPlan("test_seen", TRAINING_LAYOUTS, test, seed=3003),
        SplitPlan("test_unseen_layout", HELD_OUT_LAYOUTS, test, seed=4004, vocabulary="held_out"),
    )


def _protected_values(record, layout: Layout) -> list[str]:
    values = [getattr(record, name) for name in TEXT_FIELDS]
    for name in BPS_CAPABLE_FIELDS:
        value = getattr(record, name)
        if value is not None:
            values.append(format_percent(value, layout.number_style, allow_bps=True))
    for name in PLAIN_PERCENT_FIELDS:
        value = getattr(record, name)
        if value is not None:
            values.append(format_percent(value, layout.number_style))
    return [value for value in values if value]


def generate_split(
    plan: SplitPlan,
    reference: pd.DataFrame | None = None,
    reference_offset: int = 0,
) -> Iterator[dict]:
    rng = random.Random(plan.seed)
    layouts = [LAYOUTS_BY_NAME[name] for name in plan.layouts]
    for index in range(plan.size):
        layout = layouts[index % len(layouts)]
        if reference is not None and reference_offset + index < len(reference):
            facts = facts_from_reference(reference.iloc[reference_offset + index], rng)
        else:
            facts = synthesise_fund(rng)
        document = render(facts, layout, rng, plan.vocabulary)
        text = inject_noise(
            document.text,
            _protected_values(document.record, layout),
            document.record.fund_name,
            document.language,
            rng,
            rate=plan.noise_rate,
        )
        yield {
            "id": f"{plan.name}-{index:06d}",
            "layout": document.layout,
            "doc_type": document.doc_type,
            "language": document.language,
            "text": text,
            "target": document.record.model_dump(mode="json"),
        }


def write_jsonl(path: Path, rows: Iterator[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_all(
    output_dir: Path,
    train: int,
    validation: int,
    test: int,
    reference: pd.DataFrame | None = None,
) -> dict[str, int]:
    counts = {}
    offset = 0
    for plan in default_plans(train, validation, test):
        rows = generate_split(plan, reference, reference_offset=offset)
        counts[plan.name] = write_jsonl(output_dir / f"{plan.name}.jsonl", rows)
        offset += plan.size
    return counts

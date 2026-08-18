from __future__ import annotations

from pathlib import Path

from datasets import Dataset

from ..dataset.build import read_jsonl
from ..dataset.prompts import FIELD_SPEC, SYSTEM_PROMPT, USER_TEMPLATE, target_json
from ..schema import KidRecord


def to_prompt_completion(row: dict) -> dict:
    record = KidRecord.model_validate(row["target"])
    return {
        "prompt": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE.format(fields=FIELD_SPEC, document=row["text"])},
        ],
        "completion": [{"role": "assistant", "content": target_json(record)}],
    }


def load_split(path: Path, limit: int | None = None) -> Dataset:
    rows = read_jsonl(path)
    if limit is not None:
        rows = rows[:limit]
    return Dataset.from_list([to_prompt_completion(row) for row in rows])

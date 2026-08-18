from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

from pydantic import ValidationError

from ..dataset.build import read_jsonl
from ..evaluation.baselines.rules import extract
from ..evaluation.grounding import is_grounded
from ..evaluation.metrics import ALL_FIELDS, flatten
from ..schema import KidRecord

INSTRUCTIONS = """// Correct every field against the document text shown below, then save and close.
// Use null for anything the document does not state. Do not infer or calculate.
// Lines beginning with // are ignored.
"""


def ungrounded_fields(prediction: dict, text: str) -> list[str]:
    flat = flatten(prediction)
    return [name for name in ALL_FIELDS if flat[name] is not None and not is_grounded(name, flat[name], text)]


def strip_comments(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//"))


def edit_json(payload: dict, document: str, editor: str) -> dict | None:
    commented_document = "\n".join(f"// {line}" for line in document.splitlines())
    body = INSTRUCTIONS + json.dumps(payload, indent=2, ensure_ascii=False) + "\n\n" + commented_document + "\n"
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False, encoding="utf-8") as handle:
        handle.write(body)
        path = Path(handle.name)
    try:
        subprocess.run([*editor.split(), str(path)], check=True)
        return json.loads(strip_comments(path.read_text(encoding="utf-8")))
    except (subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"could not read your edit: {error}")
        return None
    finally:
        path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Hand-label real documents, pre-filled by the rule baseline")
    parser.add_argument("--documents", type=Path, default=Path("data/real/documents.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("data/real/test_real.jsonl"))
    parser.add_argument("--editor", default=os.environ.get("EDITOR", "nano"))
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    documents = read_jsonl(args.documents)
    labelled = {row["id"]: row for row in read_jsonl(args.out)} if args.out.exists() else {}
    pending = [row for row in documents if row["id"] not in labelled]
    if args.limit:
        pending = pending[: args.limit]

    print(f"{len(labelled)} already labelled, {len(pending)} to go")
    for index, row in enumerate(pending, start=1):
        print(f"\n[{index}/{len(pending)}] {row.get('source', row['id'])}")
        prefill = extract(row["text"])
        edited = edit_json(prefill, row["text"], args.editor)
        if edited is None:
            print("skipped")
            continue
        try:
            record = KidRecord.model_validate(edited)
        except ValidationError as error:
            print(f"invalid, skipped: {error.error_count()} problem(s)")
            continue
        target = record.model_dump(mode="json")
        for name in ungrounded_fields(target, row["text"]):
            print(f"  warning: {name} does not appear in the document text")
        labelled[row["id"]] = {**row, "target": target}
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8") as handle:
            for entry in labelled.values():
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"  saved ({len(labelled)} total)")


if __name__ == "__main__":
    main()

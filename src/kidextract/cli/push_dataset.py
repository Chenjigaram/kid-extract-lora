from __future__ import annotations

import argparse
import json
from pathlib import Path

FRONT_MATTER = """---
license: mit
task_categories:
  - text-generation
language:
  - en
  - de
  - fr
  - nl
tags:
  - structured-extraction
  - json
  - finance
  - synthetic
configs:
  - config_name: default
    data_files:
      - split: train
        path: train.jsonl
      - split: validation
        path: validation.jsonl
      - split: test_seen
        path: test_seen.jsonl
      - split: test_unseen_layout
        path: test_unseen_layout.jsonl
---

"""

SPLITS = ("train", "validation", "test_seen", "test_unseen_layout")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish the generated corpus to the Hub")
    parser.add_argument("--data-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--card", type=Path, default=Path("docs/DATASET_CARD.md"))
    parser.add_argument("--private", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    missing = [name for name in SPLITS if not (args.data_dir / f"{name}.jsonl").exists()]
    if missing:
        raise SystemExit(f"missing splits in {args.data_dir}: {', '.join(missing)}")

    sizes = {name: (args.data_dir / f"{name}.jsonl").stat().st_size for name in SPLITS}
    card = FRONT_MATTER + args.card.read_text()

    if args.dry_run:
        print(json.dumps({"repo_id": args.repo_id, "bytes": sizes, "card_bytes": len(card)}, indent=2))
        return

    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(args.repo_id, repo_type="dataset", private=args.private, exist_ok=True)
    api.upload_file(
        path_or_fileobj=card.encode(),
        path_in_repo="README.md",
        repo_id=args.repo_id,
        repo_type="dataset",
    )
    for name in SPLITS:
        api.upload_file(
            path_or_fileobj=str(args.data_dir / f"{name}.jsonl"),
            path_in_repo=f"{name}.jsonl",
            repo_id=args.repo_id,
            repo_type="dataset",
        )
    print(f"published https://huggingface.co/datasets/{args.repo_id}")


if __name__ == "__main__":
    main()

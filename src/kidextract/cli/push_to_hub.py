from __future__ import annotations

import argparse
import json
from pathlib import Path


EXCLUDE = ("training_args.bin", "optimizer.pt", "scheduler.pt", "rng_state.pth")


def read_card(path: Path, repo_id: str, base_model: str) -> str:
    body = path.read_text()
    front_matter = "\n".join(
        [
            "---",
            "license: mit",
            f"base_model: {base_model}",
            "library_name: peft",
            "tags:",
            "  - lora",
            "  - structured-extraction",
            "  - json",
            "  - finance",
            "language:",
            "  - en",
            "  - de",
            "  - fr",
            "  - nl",
            "---",
            "",
        ]
    )
    return front_matter + body


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish the adapter and its card to the Hub")
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--card", type=Path, default=Path("docs/MODEL_CARD.md"))
    parser.add_argument("--base-model", default="HuggingFaceTB/SmolLM2-135M-Instruct")
    parser.add_argument("--private", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.adapter.exists():
        raise SystemExit(f"adapter not found: {args.adapter}")

    card = read_card(args.card, args.repo_id, args.base_model)
    files = sorted(p.name for p in args.adapter.iterdir() if p.name not in EXCLUDE)
    if args.dry_run:
        print(json.dumps({"repo_id": args.repo_id, "files": files, "card_bytes": len(card)}, indent=2))
        return

    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(args.repo_id, private=args.private, exist_ok=True)
    (args.adapter / "README.md").write_text(card)
    api.upload_folder(
        folder_path=str(args.adapter),
        repo_id=args.repo_id,
        commit_message="Publish adapter",
        ignore_patterns=list(EXCLUDE),
    )
    print(f"published https://huggingface.co/{args.repo_id}")


if __name__ == "__main__":
    main()

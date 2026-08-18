from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..evaluation.runner import evaluate_system, few_shot_examples, json_text_extractor, write_result

SYSTEMS = ("rules", "zero-shot", "few-shot", "finetuned")


def build_extractor(args: argparse.Namespace):
    if args.system == "rules":
        from ..evaluation.baselines.rules import extract

        return extract

    from ..evaluation.hf_model import CausalExtractor

    examples = []
    if args.system == "few-shot":
        examples = few_shot_examples(args.shots_from, args.shots)
    adapter = Path(args.adapter) if args.system == "finetuned" and args.adapter else None
    model = CausalExtractor(
        args.model,
        adapter=adapter,
        max_new_tokens=args.max_new_tokens,
        threads=args.threads,
        examples=examples,
    )
    return json_text_extractor(model.generate)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate an extraction system on a split")
    parser.add_argument("--split", type=Path, required=True)
    parser.add_argument("--system", choices=SYSTEMS, required=True)
    parser.add_argument("--model", default="HuggingFaceTB/SmolLM2-135M-Instruct")
    parser.add_argument("--adapter", default=None)
    parser.add_argument("--shots", type=int, default=2)
    parser.add_argument("--shots-from", type=Path, default=Path("data/processed/train.jsonl"))
    parser.add_argument("--max-new-tokens", type=int, default=400)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--name", default=None)
    parser.add_argument("--out", type=Path, default=Path("reports"))
    args = parser.parse_args()

    extractor = build_extractor(args)
    name = args.name or args.system
    result = evaluate_system(name, args.split, extractor, limit=args.limit)
    path = write_result(result, args.out)
    summary = result.summary()
    summary.pop("per_field")
    print(json.dumps(summary, indent=2))
    print(f"written to {path}")


if __name__ == "__main__":
    main()

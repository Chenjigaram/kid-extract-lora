from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_override(text: str) -> tuple[str, object]:
    key, _, raw = text.partition("=")
    try:
        return key, json.loads(raw)
    except json.JSONDecodeError:
        return key, raw


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune a small model with LoRA")
    parser.add_argument("--config", type=Path, default=Path("configs/base.yaml"))
    parser.add_argument("--set", action="append", default=[], metavar="section.option=value")
    parser.add_argument("--threads", type=int, default=None)
    args = parser.parse_args()

    from ..train.config import load_config
    from ..train.lora import run

    overrides = dict(parse_override(item) for item in args.set)
    config = load_config(args.config, overrides)
    summary = run(config, threads=args.threads)
    print(json.dumps({k: v for k, v in summary.items() if k != "config"}, indent=2))


if __name__ == "__main__":
    main()

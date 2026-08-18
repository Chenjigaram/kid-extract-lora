from __future__ import annotations

import argparse
from pathlib import Path

from ..corpus.facts import load_reference_funds
from ..dataset.build import build_all


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the KID extraction dataset")
    parser.add_argument("--out", type=Path, default=Path("data/processed"))
    parser.add_argument("--train", type=int, default=6000)
    parser.add_argument("--validation", type=int, default=500)
    parser.add_argument("--test", type=int, default=500)
    parser.add_argument("--reference-csv", type=Path, default=None)
    args = parser.parse_args()

    reference = None
    if args.reference_csv is not None:
        total = args.train + args.validation + 2 * args.test
        reference = load_reference_funds(args.reference_csv, limit=total).sample(
            frac=1.0, random_state=7
        ).reset_index(drop=True)
        print(f"loaded {len(reference)} reference funds from {args.reference_csv}")

    counts = build_all(args.out, args.train, args.validation, args.test, reference)
    for name, count in counts.items():
        print(f"{name:20} {count}")


if __name__ == "__main__":
    main()

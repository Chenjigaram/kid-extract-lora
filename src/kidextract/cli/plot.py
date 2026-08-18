from __future__ import annotations

import argparse
from pathlib import Path

from ..evaluation.plots import plot_sweep


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot sweep results")
    parser.add_argument("--results", type=Path, default=Path("runs/sweep/results.json"))
    parser.add_argument("--out", type=Path, default=Path("reports/figures"))
    parser.add_argument("--metric", default="eval_loss")
    args = parser.parse_args()

    if not args.results.exists():
        raise SystemExit(f"no sweep results at {args.results}")
    for path in plot_sweep(args.results, args.out, args.metric):
        print(path)


if __name__ == "__main__":
    main()

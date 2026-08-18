from __future__ import annotations

import argparse
from pathlib import Path

from ..train.sweep import plan_points, run_sweep, sweep_table


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a LoRA hyperparameter sweep")
    parser.add_argument("--spec", type=Path, default=Path("configs/sweep.yaml"))
    parser.add_argument("--threads", type=int, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--skip-generation", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--table", type=Path, default=None)
    args = parser.parse_args()

    if args.dry_run:
        import yaml

        points = plan_points(yaml.safe_load(args.spec.read_text()))
        for index, point in enumerate(points, start=1):
            print(f"{index:3} {point['name']:<40} {point['overrides']}")
        print(f"\n{len(points)} runs planned")
        return

    results = run_sweep(args.spec, args.threads, args.limit, args.skip_generation)
    table = sweep_table(results)
    print(table)
    if args.table:
        args.table.parent.mkdir(parents=True, exist_ok=True)
        args.table.write_text(table)


if __name__ == "__main__":
    main()

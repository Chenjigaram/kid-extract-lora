from __future__ import annotations

import argparse
from pathlib import Path

from ..evaluation.report import build_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Collate evaluation summaries into a markdown report")
    parser.add_argument("--dir", type=Path, default=Path("reports"))
    parser.add_argument("--out", type=Path, default=Path("reports/RESULTS.md"))
    args = parser.parse_args()

    report = build_report(args.dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report)
    print(report)


if __name__ == "__main__":
    main()

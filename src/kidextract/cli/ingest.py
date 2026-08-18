from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..ingest.pdf import extract_text, normalise_document


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text from a directory of real KID PDFs")
    parser.add_argument("--pdf-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("data/real/documents.jsonl"))
    parser.add_argument("--engine", choices=["auto", "pdfplumber", "pypdf"], default="auto")
    parser.add_argument("--min-chars", type=int, default=400)
    args = parser.parse_args()

    paths = sorted(p for p in args.pdf_dir.rglob("*.pdf"))
    if not paths:
        raise SystemExit(f"no PDFs found under {args.pdf_dir}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    kept = skipped = 0
    with args.out.open("w", encoding="utf-8") as handle:
        for path in paths:
            try:
                document = extract_text(path, args.engine)
            except RuntimeError as error:
                print(f"skip {path.name}: {error}")
                skipped += 1
                continue
            text = normalise_document(document.text)
            if len(text) < args.min_chars:
                print(f"skip {path.name}: only {len(text)} characters, likely a scan needing OCR")
                skipped += 1
                continue
            if document.checksum in seen:
                print(f"skip {path.name}: duplicate of an earlier file")
                skipped += 1
                continue
            seen.add(document.checksum)
            handle.write(
                json.dumps(
                    {
                        "id": f"real-{document.checksum}",
                        "source": document.source,
                        "pages": document.pages,
                        "text": text,
                        "target": None,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            kept += 1
    print(f"kept {kept}, skipped {skipped}, written to {args.out}")


if __name__ == "__main__":
    main()

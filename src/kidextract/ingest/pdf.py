from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from ..normalize import clean_text


@dataclass(frozen=True)
class ExtractedDocument:
    source: str
    checksum: str
    pages: int
    text: str


def _read_with_pdfplumber(path: Path) -> tuple[list[str], int]:
    import pdfplumber

    with pdfplumber.open(str(path)) as document:
        pages = [page.extract_text() or "" for page in document.pages]
    return pages, len(pages)


def _read_with_pypdf(path: Path) -> tuple[list[str], int]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return pages, len(reader.pages)


def extract_text(path: Path, engine: str = "auto") -> ExtractedDocument:
    readers = {"pdfplumber": _read_with_pdfplumber, "pypdf": _read_with_pypdf}
    order = [engine] if engine in readers else ["pdfplumber", "pypdf"]

    errors = []
    for name in order:
        try:
            pages, count = readers[name](path)
            break
        except ImportError as error:
            errors.append(f"{name}: {error}")
        except Exception as error:
            errors.append(f"{name}: {error}")
    else:
        raise RuntimeError(f"could not read {path}: {'; '.join(errors)}")

    body = "\n\n".join(page.strip() for page in pages if page.strip())
    return ExtractedDocument(
        source=path.name,
        checksum=hashlib.sha256(path.read_bytes()).hexdigest()[:16],
        pages=count,
        text=body,
    )


def normalise_document(text: str) -> str:
    lines = [clean_text(line) or "" for line in text.split("\n")]
    output: list[str] = []
    for line in lines:
        if not line and output and not output[-1]:
            continue
        output.append(line)
    return "\n".join(output).strip()

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from rashomon_align import alignment as generic_alignment

from ..evaluation.metrics import ALL_FIELDS
from .agreement import field_matches, mean_field_agreement
from .sampling import natural_documents, sample_documents, uniform_documents

Extractor = Callable[[str], dict | None]


@dataclass
class Alignment:
    documents: int
    strict: float
    per_field: float
    alpha: float
    disagreements: dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "documents": self.documents,
            "alpha": self.alpha,
            "strict": round(self.strict, 4),
            "per_field": round(self.per_field, 4),
            "disagreements": {k: v for k, v in sorted(self.disagreements.items(), key=lambda kv: -kv[1]) if v},
        }


def alignment(
    extract_a: Extractor,
    extract_b: Extractor,
    documents: list[str],
    fields=ALL_FIELDS,
    alpha: float = 0.0,
) -> Alignment:
    if not documents:
        return Alignment(0, 1.0, 1.0, alpha)
    strict_hits = 0
    disagreements = dict.fromkeys(fields, 0)
    for text in documents:
        matches = field_matches(extract_a(text), extract_b(text), fields)
        strict_hits += all(matches.values())
        for name, ok in matches.items():
            if not ok:
                disagreements[name] += 1
    count = len(documents)
    per_field = generic_alignment(
        lambda texts: [extract_a(text) for text in texts],
        lambda texts: [extract_b(text) for text in texts],
        documents,
        agree=lambda a, b: mean_field_agreement(a, b, fields),
    )
    return Alignment(count, strict_hits / count, per_field, alpha, disagreements)


def distributional_alignment(a: Extractor, b: Extractor, count: int = 400, seed: int = 1) -> Alignment:
    return alignment(a, b, natural_documents(count, seed), alpha=0.0)


def geometric_alignment(a: Extractor, b: Extractor, count: int = 400, seed: int = 2) -> Alignment:
    return alignment(a, b, uniform_documents(count, seed), alpha=1.0)


def alpha_curve(a: Extractor, b: Extractor, count: int = 300, seed: int = 100, steps: int = 11) -> list[Alignment]:
    results = []
    for index in range(steps):
        alpha = index / (steps - 1)
        documents = sample_documents(count, seed + index, alpha=alpha)
        results.append(alignment(a, b, documents, alpha=alpha))
    return results

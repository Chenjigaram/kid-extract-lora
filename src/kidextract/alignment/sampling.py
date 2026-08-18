from __future__ import annotations

import random

from ..corpus.facts import synthesise_fund
from ..corpus.layouts import LAYOUTS
from ..corpus.render import DROPOUT, render

UNIFORM_PRESENCE = 0.5


def presence_at(alpha: float) -> dict[str, float]:
    return {name: (1 - alpha) * natural + alpha * UNIFORM_PRESENCE for name, natural in DROPOUT.items()}


def sample_documents(count: int, seed: int, alpha: float = 0.0, layouts=LAYOUTS) -> list[str]:
    rng = random.Random(seed)
    dropout = presence_at(alpha)
    documents = []
    for _ in range(count):
        vocabulary = "all" if rng.random() < alpha else "known"
        layout = rng.choice(list(layouts))
        document = render(synthesise_fund(rng), layout, rng, vocabulary=vocabulary, dropout=dropout)
        documents.append(document.text)
    return documents


def natural_documents(count: int, seed: int, layouts=LAYOUTS) -> list[str]:
    return sample_documents(count, seed, alpha=0.0, layouts=layouts)


def uniform_documents(count: int, seed: int, layouts=LAYOUTS) -> list[str]:
    return sample_documents(count, seed, alpha=1.0, layouts=layouts)

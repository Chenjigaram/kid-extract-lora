import random
import statistics
import sys

from kidextract.corpus import render as render_module
from kidextract.corpus.facts import synthesise_fund
from kidextract.corpus.layouts import LAYOUTS
from kidextract.corpus.render import render
from kidextract.evaluation.metrics import ALL_FIELDS, flatten, values_match

from alignment_first_look import ALL_LABELS, KNOWN_LABELS, extract_with

N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
NATURAL = dict(render_module.DROPOUT)


def documents_at(alpha, n, seed):
    rng = random.Random(seed)
    for key, natural in NATURAL.items():
        render_module.DROPOUT[key] = (1 - alpha) * natural + alpha * 0.5
    try:
        out = []
        for _ in range(n):
            vocabulary = "all" if rng.random() < alpha else "known"
            out.append(render(synthesise_fund(rng), rng.choice(LAYOUTS), rng, vocabulary=vocabulary).text)
        return out
    finally:
        render_module.DROPOUT.update(NATURAL)


def agreement(documents):
    strict, per_field = [], []
    for text in documents:
        a = flatten(extract_with(KNOWN_LABELS, text))
        b = flatten(extract_with(ALL_LABELS, text))
        matches = []
        for name in ALL_FIELDS:
            if a[name] is None and b[name] is None:
                matches.append(True)
            elif a[name] is None or b[name] is None:
                matches.append(False)
            else:
                matches.append(values_match(name, a[name], b[name]))
        per_field.append(statistics.mean(matches))
        strict.append(all(matches))
    return statistics.mean(strict), statistics.mean(per_field)


print("alpha  0 = natural (dRA)   1 = uniform (gRA)")
print(f"{'alpha':>6}{'strict':>9}{'per-field':>11}")
for step in range(0, 11):
    alpha = step / 10
    strict, field = agreement(documents_at(alpha, N, 100 + step))
    print(f"{alpha:>6.1f}{strict:>9.3f}{field:>11.3f}")

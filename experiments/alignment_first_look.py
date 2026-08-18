import random
import statistics
import sys

from kidextract.corpus.facts import synthesise_fund
from kidextract.corpus.layouts import LAYOUTS
from kidextract.corpus.render import render
from kidextract.corpus.vocabulary import all_labels_for
from kidextract.evaluation.baselines import rules
from kidextract.evaluation.metrics import ALL_FIELDS, flatten, values_match

N = int(sys.argv[1]) if len(sys.argv) > 1 else 400


def label_index(vocabulary):
    pairs = []
    for key, field in rules.FIELD_BY_LABEL_KEY.items():
        for label in all_labels_for(key, vocabulary):
            pairs.append((label.casefold(), field))
    return sorted(set(pairs), key=lambda pair: -len(pair[0]))


KNOWN_LABELS = label_index("known")
ALL_LABELS = label_index("all")


def extract_with(labels, text):
    saved = rules.LABELS
    rules.LABELS = labels
    try:
        return rules.extract(text)
    finally:
        rules.LABELS = saved


def natural_documents(n, seed):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        layout = rng.choice(LAYOUTS)
        out.append(render(synthesise_fund(rng), layout, rng, vocabulary="known").text)
    return out


def uniform_documents(n, seed):
    rng = random.Random(seed)
    saved = dict(rules.__dict__.get("DROPOUT", {}))
    from kidextract.corpus import render as render_module

    original = dict(render_module.DROPOUT)
    for key in render_module.DROPOUT:
        render_module.DROPOUT[key] = 0.5
    try:
        out = []
        for _ in range(n):
            layout = rng.choice(LAYOUTS)
            facts = synthesise_fund(rng)
            out.append(render(facts, layout, rng, vocabulary="all").text)
        return out
    finally:
        render_module.DROPOUT.update(original)
        del saved


def agreement(documents):
    strict = []
    per_field = []
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


print(f"comparing rules(known vocabulary) against rules(full vocabulary), n={N}")
for name, documents in (
    ("dRA  natural", natural_documents(N, 1)),
    ("gRA  uniform", uniform_documents(N, 2)),
):
    strict, field = agreement(documents)
    print(f"{name}: strict={strict:.3f}  per-field={field:.3f}")


def field_breakdown(documents):
    disagree = {name: 0 for name in ALL_FIELDS}
    for text in documents:
        a = flatten(extract_with(KNOWN_LABELS, text))
        b = flatten(extract_with(ALL_LABELS, text))
        for name in ALL_FIELDS:
            if a[name] is None and b[name] is None:
                continue
            if a[name] is None or b[name] is None or not values_match(name, a[name], b[name]):
                disagree[name] += 1
    return sorted(disagree.items(), key=lambda kv: -kv[1])


print()
print("where they disagree, uniform sample:")
for name, count in field_breakdown(uniform_documents(N, 2)):
    if count:
        print(f"  {name:<34} {count:>4} / {N}  ({100*count/N:.0f}%)")

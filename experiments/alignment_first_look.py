import sys

from kidextract.alignment.measure import distributional_alignment, geometric_alignment
from kidextract.evaluation.baselines.rules import build_label_index, extract

N = int(sys.argv[1]) if len(sys.argv) > 1 else 400

known = build_label_index("known")
every = build_label_index("all")

print(f"rules(known vocabulary) against rules(full vocabulary), n={N}")
for name, result in (
    ("dRA  natural", distributional_alignment(lambda t: extract(t, known), lambda t: extract(t, every), N)),
    ("gRA  uniform", geometric_alignment(lambda t: extract(t, known), lambda t: extract(t, every), N)),
):
    print(f"{name}: strict={result.strict:.3f}  per-field={result.per_field:.3f}")

result = geometric_alignment(lambda t: extract(t, known), lambda t: extract(t, every), N)
print("\nwhere they disagree, uniform sample:")
for field, count in result.as_dict()["disagreements"].items():
    print(f"  {field:<34} {count:>4} / {N}  ({100 * count / N:.0f}%)")

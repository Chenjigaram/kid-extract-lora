import sys

from kidextract.alignment.measure import alpha_curve
from kidextract.evaluation.baselines.rules import build_label_index, extract

N = int(sys.argv[1]) if len(sys.argv) > 1 else 300

known = build_label_index("known")
every = build_label_index("all")

print("alpha  0 = natural (dRA)   1 = uniform (gRA)")
print(f"{'alpha':>6}{'strict':>9}{'per-field':>11}")
for step in alpha_curve(lambda t: extract(t, known), lambda t: extract(t, every), count=N):
    print(f"{step.alpha:>6.1f}{step.strict:>9.3f}{step.per_field:>11.3f}")

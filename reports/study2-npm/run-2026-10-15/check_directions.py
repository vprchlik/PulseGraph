r"""The direction of each family test, recomputed from inference/paired_entities.csv.

Usage, from the repository root:
    .\.venv\Scripts\python.exe reports\study2-npm\run-2026-10-15\check_directions.py
        reports\study2-npm\run-2026-10-15\inference

The CSVs are read with exact float parsing. For each comparison it checks that the saved
differences are model minus reference, ranks the absolute nonzero differences (average ranks for
ties) and prints the rank sums of the negative differences (favoring the model) and of the
positive ones (favoring the reference), the side the larger sum points to, and the two-sided
approximate Wilcoxon p recomputed with SciPy beside the saved one. It changes no file.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8", newline="\n")
inf = Path(sys.argv[1])
pairs = pd.read_csv(
    inf / "paired_entities.csv",
    keep_default_na=False,
    na_values=[""],
    float_precision="round_trip",
)
family = pd.read_csv(inf / "inference.csv", float_precision="round_trip").set_index("id")
print(
    "| ID | Nonzero | Rank sum, model lower | Rank sum, reference lower | Larger sum favors "
    "| Raw p recomputed | Raw p saved |"
)
print("|---|---|---|---|---|---|---|")
for cid in family.index:
    pair = pairs[pairs.id.eq(cid)]
    diff = (pair.model_score - pair.reference_score).to_numpy(dtype=float)
    if not np.array_equal(diff, pair.difference.to_numpy(dtype=float)):
        raise SystemExit(f"{cid}: saved differences are not model minus reference")
    nonzero = diff[diff != 0]
    ranks = stats.rankdata(np.abs(nonzero))
    below, above = ranks[nonzero < 0].sum(), ranks[nonzero > 0].sum()
    side = "model" if below > above else "reference" if above > below else "neither"
    p = stats.wilcoxon(diff, zero_method="wilcox", alternative="two-sided", method="approx").pvalue
    print(
        f"| {cid} | {len(nonzero)} | {below:,.1f} | {above:,.1f} | {side} | {p:.3g} | "
        f"{family.loc[cid, 'wilcoxon_p']:.3g} |"
    )

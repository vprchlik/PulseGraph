r"""Print the tables of RESULTS-synthetic.md as Markdown from the synthetic inference directory.

Usage, from the repository root:
    .\.venv\Scripts\python.exe reports\study2-synthetic-2026-10-15\make_tables.py
        reports\study2-synthetic-2026-10-15\inference

The layout was written before the inference ran. It only reads the inference outputs: it selects
rows, formats values to four significant digits and, for the oracle per cell, names the lowest
other model and counts the models below the oracle. It computes no new statistic.
"""

import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", newline="\n")
inf = Path(sys.argv[1])
VARIANTS = (
    "chronos2_raw chronos2_completed chronos2_hurdle timesfm3_raw timesfm3_completed "
    "timesfm3_hurdle timesfm2p5_raw timesfm2p5_completed timesfm2p5_hurdle local_mean_28 "
    "autoets_weekly nb_local_level_28 poisson_28 hurdle_count_28 hurdle_empirical_28 "
    "dynamic_count"
).split()
FAMILY_MODELS = [
    "chronos2_hurdle",
    "chronos2_completed",
    "timesfm3_hurdle",
    "timesfm3_completed",
    "timesfm2p5_hurdle",
    "timesfm2p5_completed",
    "hurdle_count_28",
    "oracle",
]


def g(x, d=4):
    return "" if pd.isna(x) else f"{x:.{d}g}"


def contrast_rows(table, bh):
    head = (
        "| ID | Model variant | Reference | Model mean | Reference mean | Mean difference "
        "| 95% interval | Median difference | Lower / tied / higher (of 30) | Raw p |"
        + (" BH p | BH rejects at 0.05 |" if bh else "")
    )
    print(head)
    print("|" + "---|" * (head.count("|") - 1))
    for r in table.itertuples():
        cells = [
            r.id,
            f"`{r.model}`",
            f"`{r.reference}`",
            g(r.model_mean),
            g(r.reference_mean),
            g(r.mean_diff),
            f"[{g(r.mean_diff_ci_low)}, {g(r.mean_diff_ci_high)}]",
            g(r.median_diff),
            f"{r.wins} / {r.ties} / {r.losses}",
            g(r.wilcoxon_p, 3),
        ]
        if bh:
            cells += [g(r.wilcoxon_p_bh, 3), "yes" if r.reject_bh_005 else "no"]
        print("| " + " | ".join(str(c) for c in cells) + " |")
    print()


family = pd.read_csv(inf / "inference.csv")
print("## Confirmatory family (horizon 30, n = 30 replicate blocks)\n")
contrast_rows(family, bh=True)

secondary = pd.read_csv(inf / "secondary_contrasts.csv")
h7 = secondary[secondary.metric.eq("qscore9") & secondary.horizon.eq(7)]
print("## Horizon 7 (secondary, unadjusted)\n")
contrast_rows(h7, bh=False)

print("## Other secondary metrics, horizon 30 (unadjusted)\n")
other = secondary[secondary.horizon.eq(30) & ~secondary.metric.eq("qscore9")]
print(
    "| ID | Metric | Entities | Unavailable | Mean difference | 95% interval "
    "| Lower / tied / higher | Raw p | Status |"
)
print("|---|---|---|---|---|---|---|---|---|")
for r in other.itertuples():
    ok = r.status == "secondary"
    print(
        f"| {r.id} | {r.metric} | {r.n_entities} | {r.n_entities_unavailable} | "
        f"{g(r.mean_diff) if ok else ''} | "
        f"{f'[{g(r.mean_diff_ci_low)}, {g(r.mean_diff_ci_high)}]' if ok else ''} | "
        f"{f'{r.wins} / {r.ties} / {r.losses}' if ok else ''} | "
        f"{g(r.wilcoxon_p, 3) if ok else ''} | {r.status} |"
    )
print()

cells = pd.read_csv(inf / "secondary_cells_contrasts.csv")
for horizon in (30, 7):
    sub = cells[cells.metric.eq("qscore9") & cells.horizon.eq(horizon)]
    ids = sorted(sub.id.unique())
    print(
        f"## Per cell, horizon {horizon}: mean difference (cells where the model is lower, of 30)\n"
    )
    print("| Cell | Zero probability | Positive mean | Persistence | " + " | ".join(ids) + " |")
    print("|---|---|---|---|" + "---|" * len(ids))
    for cell, block in sub.groupby("cell_id", sort=True):
        first = block.iloc[0]
        values = [
            f"{g(b.mean_diff)} ({b.wins})" for b in block.set_index("id").loc[ids].itertuples()
        ]
        print(
            f"| {cell} | {first.zero_probability:g} | {first.positive_mean:g} | "
            f"{first.persistence:g} | " + " | ".join(values) + " |"
        )
    print()

scores = pd.read_csv(inf / "secondary_scores.csv")
print("## Mean scores per model (equal replicate blocks; the oracle is a diagnostic)\n")
print(
    "| Model | QScore9 h7 | QScore9 h30 | Brier h30 | CRPS h30 "
    "| CRPS certified / with law / all, h30 |"
)
print("|---|---|---|---|---|---|")
for model in [*VARIANTS, "oracle"]:
    a = scores[scores.model.eq(model) & scores.horizon.eq(7)].iloc[0]
    b = scores[scores.model.eq(model) & scores.horizon.eq(30)].iloc[0]
    print(
        f"| `{model}` | {g(a.qscore9)} | {g(b.qscore9)} | {g(b.occurrence_brier)} | "
        f"{g(b.discrete_crps)} | {b.crps_certified} / {b.crps_with_count_distribution} / "
        f"{b.crps_forecasts} |"
    )
print()

cell_scores = pd.read_csv(inf / "secondary_cells.csv")
print("## The oracle per cell, horizon 30 (QScore9, equal replicates within the cell)\n")
print(
    "| Cell | Zero probability | Positive mean | Persistence | Oracle | Lowest other model "
    "| Its mean | Models below the oracle (of 16) |"
)
print("|---|---|---|---|---|---|---|---|")
for cell, block in cell_scores[cell_scores.horizon.eq(30)].groupby("cell_id", sort=True):
    oracle = block[block.model.eq("oracle")].iloc[0]
    others = block[~block.model.eq("oracle")]
    best = others.loc[others.qscore9.idxmin()]
    below = int((others.qscore9 < oracle.qscore9).sum())
    print(
        f"| {cell} | {oracle.zero_probability:g} | {oracle.positive_mean:g} | "
        f"{oracle.persistence:g} | {g(oracle.qscore9)} | `{best.model}` | {g(best.qscore9)} | "
        f"{below} |"
    )
print()

acc = pd.read_csv(inf / "secondary_accounting.csv")
print("## QScore9 accounting, horizon 30 (equal replicate blocks; parts sum to the score)\n")
print("| Model | QScore9 | Zero days | Positive, over | Positive, under |")
print("|---|---|---|---|---|")
for model in FAMILY_MODELS:
    r = acc[acc.model.eq(model) & acc.horizon.eq(30)].iloc[0]
    print(
        f"| `{model}` | {g(r.qscore9)} | {g(r.zero)} | {g(r.positive_over)} | "
        f"{g(r.positive_under)} |"
    )
print()

pit = pd.read_csv(inf / "pit_histograms.csv")
print("## Randomized PIT, horizon 30: fraction of target days per tenth\n")
print("| Model | " + " | ".join(f"{b / 10:.1f}–{(b + 1) / 10:.1f}" for b in range(10)) + " |")
print("|---|" + "---|" * 10)
for model in FAMILY_MODELS:
    r = pit[pit.model.eq(model) & pit.horizon.eq(30)].iloc[0]
    if r.status != "available":
        print(f"| `{model}` | unavailable |" + " |" * 9)
        continue
    print(
        f"| `{model}` | "
        + " | ".join(f"{getattr(r, f'fraction{b + 1:02}'):.3f}" for b in range(10))
        + " |"
    )
print()

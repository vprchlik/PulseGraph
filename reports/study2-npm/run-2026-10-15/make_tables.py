r"""Print the tables of RESULTS-npm.md as Markdown from the npm external inference directory.

Usage, from the repository root:
    .\.venv\Scripts\python.exe reports\study2-npm\run-2026-10-15\make_tables.py
        reports\study2-npm\run-2026-10-15\inference

The layout was written before the run and the inference. It only reads the inference outputs: it
selects rows, counts the series of each stratum and formats values (four significant digits,
whole numbers with separators from 10,000 up, p-values to three). One table is computed here, from
inference/paired_entities.csv: the skill and concentration descriptors the protocol declares
secondary, with Study 1's definitions (pulsegraph/evaluation/reviews.py, review_scale): skill
1 - model / reference, undefined where the reference is zero; the share of the positive gains
(reference minus model, where positive) held by the five largest; and the range of the mean
difference with one series left out, with the series whose omission moves the mean most.
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
    "chronos2_raw",
    "timesfm3_hurdle",
    "timesfm3_completed",
    "timesfm3_raw",
    "timesfm2p5_hurdle",
    "timesfm2p5_completed",
    "timesfm2p5_raw",
    "hurdle_count_28",
    "local_mean_28",
]
STRATA = ["dense", "sparse", "very_sparse"]


def g(x, d=4):
    if pd.isna(x):
        return ""
    return f"{x:,.0f}" if abs(x) >= 10000 else f"{x:.{d}g}"


def p(x):
    return "" if pd.isna(x) else f"{x:.3g}"


def c(x):
    return "" if pd.isna(x) else str(int(x))


series = pd.read_csv(inf / "series_scores.csv")
counts = series.drop_duplicates("series_id").stratum.value_counts()
n = int(counts.sum())
sizes = {name: int(counts.get(name, 0)) for name in STRATA}

print("## Panel strata (series in the run)\n")
print("| Stratum | Series |")
print("|---|---|")
for name in STRATA:
    print(f"| {name} | {sizes[name]} |")
print(f"| all | {n} |")
print()

family = pd.read_csv(inf / "inference.csv")
print(f"## Confirmatory family E01 to E18 (n = {n} series)\n")
head = (
    "| ID | Model variant | Reference | Horizon | Model mean | Reference mean | Mean difference "
    f"| 95% interval | Median difference | Lower / tied / higher (of {n}) | Raw p | BH p "
    "| BH rejects at 0.05 |"
)
print(head)
print("|" + "---|" * (head.count("|") - 1))
for r in family.itertuples():
    cells = [
        r.id,
        f"`{r.model}`",
        f"`{r.reference}`",
        r.horizon,
        g(r.model_mean),
        g(r.reference_mean),
        g(r.mean_diff),
        f"[{g(r.mean_diff_ci_low)}, {g(r.mean_diff_ci_high)}]",
        g(r.median_diff),
        f"{r.wins} / {r.ties} / {r.losses}",
        p(r.wilcoxon_p),
        p(r.wilcoxon_p_bh),
        "yes" if r.reject_bh_005 else "no",
    ]
    print("| " + " | ".join(str(cell) for cell in cells) + " |")
print()

pairs = pd.read_csv(inf / "paired_entities.csv", keep_default_na=False, na_values=[""])
print("## Skill and concentration, the family's comparisons (secondary, descriptive)\n")
print(
    "| ID | Mean skill | Median skill | Skill defined (of n) | Top-five share of positive gains "
    "| Mean difference, one series left out: range | Series whose omission moves the mean most "
    "| Its difference |"
)
print("|---|---|---|---|---|---|---|---|")
for cid in family.id:
    pair = pairs[pairs.id.eq(cid)].set_index("entity")
    diff = pair.model_score - pair.reference_score
    skill = 1 - pair.model_score / pair.reference_score.where(pair.reference_score != 0)
    gain = (-diff).clip(lower=0)
    top5 = gain.nlargest(5).sum() / gain.sum() if gain.sum() else float("nan")
    loo = (diff.sum() - diff) / (len(diff) - 1)
    moved = (loo - diff.mean()).abs().idxmax()
    print(
        f"| {cid} | {g(skill.mean())} | {g(skill.median())} | {c(skill.notna().sum())} "
        f"of {len(pair)} | {g(top5, 3)} | [{g(loo.min())}, {g(loo.max())}] | `{moved}` | "
        f"{g(diff[moved])} |"
    )
print()

secondary = pd.read_csv(inf / "secondary_contrasts.csv")
for horizon in (7, 30):
    print(f"## Other secondary metrics, horizon {horizon} (unadjusted)\n")
    print(
        "| ID | Metric | Entities | Unavailable | Mean difference | 95% interval "
        "| Median difference | Lower / tied / higher | Raw p | Status |"
    )
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in secondary[secondary.horizon.eq(horizon)].itertuples():
        ok = r.status == "secondary"
        status = r.status if ok else f"{r.status} ({r.unavailable_reason})"
        print(
            f"| {r.id} | {r.metric} | {c(r.n_entities)} | {c(r.n_entities_unavailable)} | "
            f"{g(r.mean_diff) if ok else ''} | "
            f"{f'[{g(r.mean_diff_ci_low)}, {g(r.mean_diff_ci_high)}]' if ok else ''} | "
            f"{g(r.median_diff) if ok else ''} | "
            f"{f'{c(r.wins)} / {c(r.ties)} / {c(r.losses)}' if ok else ''} | "
            f"{p(r.wilcoxon_p) if ok else ''} | {status} |"
        )
    print()

strata = pd.read_csv(inf / "secondary_strata_contrasts.csv")
for metric in ("qscore9", "context_scaled_qscore9"):
    print(
        f"## Per stratum, {metric}: mean difference / median difference "
        "(series where the model is lower)\n"
    )
    print(
        "| ID | Horizon | Model variant | Reference | "
        + " | ".join(f"{name} (n = {sizes[name]})" for name in STRATA)
        + " |"
    )
    print("|---|---|---|---|" + "---|" * len(STRATA))
    sub = strata[strata.metric.eq(metric)]
    for cid in family.id:
        block = sub[sub.id.eq(cid)].set_index("stratum")
        first = block.iloc[0]
        values = []
        for name in STRATA:
            b = block.loc[name]
            values.append(
                f"{g(b.mean_diff)} / {g(b.median_diff)} ({c(b.wins)} of {c(b.n_entities)})"
            )
        print(
            f"| {cid} | {first.horizon} | `{first.model}` | `{first.reference}` | "
            + " | ".join(values)
            + " |"
        )
    print()

scores = pd.read_csv(inf / "secondary_scores.csv")
print(f"## Mean scores per model (equal series, n = {n})\n")
print(
    "| Model | QScore9 h7 | QScore9 h30 | Scaled QScore9 h30 | Brier h30 | CRPS h30 "
    "| CRPS series defined, h30 | CRPS certified / with law / all, h30 |"
)
print("|---|---|---|---|---|---|---|---|")
for model in VARIANTS:
    a = scores[scores.model.eq(model) & scores.horizon.eq(7)].iloc[0]
    b = scores[scores.model.eq(model) & scores.horizon.eq(30)].iloc[0]
    print(
        f"| `{model}` | {g(a.qscore9)} | {g(b.qscore9)} | {g(b.context_scaled_qscore9)} | "
        f"{g(b.occurrence_brier)} | {g(b.discrete_crps)} | {c(b.discrete_crps_n_entities)} | "
        f"{b.crps_certified} / {b.crps_with_count_distribution} / {b.crps_forecasts} |"
    )
print()

stratum_scores = pd.read_csv(inf / "secondary_strata.csv")
for horizon in (30, 7):
    print(f"## Mean QScore9 per model and stratum, horizon {horizon} (equal series)\n")
    print("| Model | " + " | ".join(f"{name} (n = {sizes[name]})" for name in STRATA) + " |")
    print("|---|" + "---|" * len(STRATA))
    sub = stratum_scores[stratum_scores.horizon.eq(horizon)]
    for model in VARIANTS:
        block = sub[sub.model.eq(model)].set_index("stratum")
        print(f"| `{model}` | " + " | ".join(g(block.loc[name].qscore9) for name in STRATA) + " |")
    print()

acc = pd.read_csv(inf / "secondary_accounting.csv")
for horizon in (30, 7):
    print(f"## QScore9 accounting, horizon {horizon} (equal series; parts sum to the score)\n")
    print("| Model | QScore9 | Zero days | Positive, over | Positive, under | Largest residual |")
    print("|---|---|---|---|---|---|")
    for model in FAMILY_MODELS:
        r = acc[acc.model.eq(model) & acc.horizon.eq(horizon)].iloc[0]
        print(
            f"| `{model}` | {g(r.qscore9)} | {g(r.zero)} | {g(r.positive_over)} | "
            f"{g(r.positive_under)} | {r.max_abs_window_residual:.2g} |"
        )
    print()

pit = pd.read_csv(inf / "pit_histograms.csv")
print("## Randomized PIT, horizon 30: fraction of target days per tenth\n")
print("| Model | " + " | ".join(f"{b / 10:.1f}–{(b + 1) / 10:.1f}" for b in range(10)) + " |")
print("|---|" + "---|" * 10)
for model in VARIANTS:
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

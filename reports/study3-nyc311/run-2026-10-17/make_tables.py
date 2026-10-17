r"""Print the tables of RESULTS-nyc311.md as Markdown from the Study 3 NYC 311 run directory.

Usage, from the repository root:
    .\.venv\Scripts\python.exe reports\study3-nyc311\run-2026-10-17\make_tables.py
        reports\study3-nyc311\run-2026-10-17

The layout was written before the run and the inference and dry-run on toy runs only. It reads
the run's run.json (for the readiness's panel entries), the inference outputs under
<run>/inference, the frozen manifest and the target signals of the pull, whose first 275 days are
the frozen context; each file named by the readiness is checked against its SHA-256 first. It
fits nothing and tests nothing. It selects rows and formats values (four significant digits,
whole numbers with separators from 10,000 up, p-values to three significant digits). Two things
are counted here, neither a score: per stratum and origin, the series whose context is all zero,
has no request day in its last 28 days, or has fewer than two (where dynamic_count falls back to
hurdle_count_28, so hurdle_dynamic equals hurdle_fixed); and, per family row, the rank sums of the
nonzero series differences in inference/paired_entities.csv, with the two-sided approximate
Wilcoxon p recomputed by SciPy beside the saved one, so each direction is read from the paired
table. A median difference of exactly zero has no sign and is reported as neither direction.
CSVs are read with round-trip float parsing.
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8", newline="\n")
run = Path(sys.argv[1])
inf = run / "inference"
MODELS = ("chronos2", "timesfm3", "timesfm2p5")
MODEL_NAMES = dict(chronos2="Chronos-2", timesfm3="TimesFM 3", timesfm2p5="TimesFM 2.5")
STRATA = ("dense", "sparse", "very_sparse")
STRATUM_NAMES = dict(dense="dense", sparse="sparse", very_sparse="very sparse", all="all")
CUTOFFS = ("2026-06-03", "2026-07-03", "2026-08-02")
CONTEXT_START, STRATA_START = "2025-09-01", "2026-03-05"
VARIANTS = [
    f"{m}_{v}"
    for m in MODELS
    for v in ("raw", "completed", "hurdle", "hurdle_dynamic", "occurrence_model_size_count")
] + [
    "local_mean_28",
    "autoets_weekly",
    "nb_local_level_28",
    "poisson_28",
    "hurdle_count_28",
    "hurdle_empirical_28",
    "dynamic_count",
]
ACCOUNTED = [
    f"{m}_{v}"
    for m in MODELS
    for v in ("completed", "hurdle", "hurdle_dynamic", "occurrence_model_size_count")
] + ["hurdle_count_28", "hurdle_empirical_28", "dynamic_count"]


def g(x, d=4):
    if pd.isna(x):
        return ""
    return f"{x:,.0f}" if abs(x) >= 10000 else f"{x:.{d}g}"


def p(x):
    return "" if pd.isna(x) else f"{x:.3g}"


def c(x):
    return "" if pd.isna(x) else f"{int(x):,}"


def interval(r):
    return f"[{g(r.mean_diff_ci_low)}, {g(r.mean_diff_ci_high)}]"


def sign(x):
    return "none (0)" if x == 0 else "negative" if x < 0 else "positive"


def csv(name):
    return pd.read_csv(
        inf / name, keep_default_na=False, na_values=[""], float_precision="round_trip"
    )


def checked(entry):
    path = Path(entry["path"])
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
        raise SystemExit(f"{path}: SHA-256 differs from the readiness")
    return path


def table(head, rows):
    print("| " + " | ".join(head) + " |")
    print("|" + "---|" * len(head))
    for row in rows:
        print("| " + " | ".join(str(cell) for cell in row) + " |")
    print()


state = json.loads((run / "run.json").read_text(encoding="utf-8"))
panel = state["metadata"]["readiness"]["panels"]["nyc311"]
manifest = json.loads(checked(panel["manifest"]).read_text(encoding="utf-8"))
signals = pd.read_parquet(checked(panel["signals"]))
stratum_of = {row["series_id"]: row["stratum"] for row in manifest["series"]}
sizes = {s: sum(1 for v in stratum_of.values() if v == s) for s in STRATA}
n = len(stratum_of)
family = csv("inference.csv")
series = csv("series_scores.csv")
if set(series.series_id) != set(stratum_of) or len(family) != 36:
    raise SystemExit("The inference does not cover the manifest's series or the 36 rows")


def label(stratum):
    return f"{STRATUM_NAMES[stratum]} (n = {sizes[stratum] if stratum in sizes else n})"


# 1. Strata and zero contexts, from the manifest and the signals' context prefix.
signals["date"] = pd.to_datetime(signals["date"])
wide = signals.pivot(index="date", columns="series_id", values="count").sort_index()
if list(wide.columns.sort_values()) != sorted(stratum_of) or wide.isna().any().any():
    raise SystemExit("The signals do not hold every manifest series on every day")
days = wide.index
strata_window = wide[(days >= STRATA_START) & (days < CUTOFFS[0])]
if len(strata_window) != 90:
    raise SystemExit("The strata window must hold 90 days")
zero_strata = (strata_window == 0).all()
manifest_zero = {r["series_id"]: r["zero_fraction"] == 1.0 for r in manifest["series"]}
if any(bool(zero_strata[k]) != manifest_zero[k] for k in stratum_of):
    raise SystemExit("The signals' strata window disagrees with the manifest's zero fractions")
profile = []
for cutoff in CUTOFFS:
    context = wide[(days >= CONTEXT_START) & (days < cutoff)]
    last = context.iloc[-28:]
    profile.append(
        dict(
            cutoff=cutoff,
            days=len(context),
            all_zero=(context == 0).all(),
            none_28=(last == 0).all(),
            under_two_28=(last > 0).sum() < 2,
        )
    )

print("## The panel's strata and their zero contexts\n")
print(
    f"The frozen manifest holds {n} series; every stratum table below states its n. The strata "
    "window is 2026-03-05 to 2026-06-02 (90 days) and the context at the first origin is "
    f"2025-09-01 to 2026-06-02 ({profile[0]['days']} days).\n"
)
table(
    [
        "Stratum",
        "Series",
        "All-zero strata window",
        f"All-zero context at the first origin ({profile[0]['days']} days)",
    ],
    [
        [
            STRATUM_NAMES[s],
            sizes[s],
            int(sum(bool(zero_strata[k]) for k, v in stratum_of.items() if v == s)),
            int(sum(bool(profile[0]["all_zero"][k]) for k, v in stratum_of.items() if v == s)),
        ]
        for s in STRATA
    ]
    + [
        [
            "all",
            n,
            int(zero_strata.sum()),
            int(profile[0]["all_zero"].sum()),
        ]
    ],
)
print("## The contexts at each origin: request days in the last 28 days\n")
print(
    "With fewer than two request days in the last 28 days of a context, dynamic_count takes "
    "hurdle_count_28's law, so hurdle_dynamic equals hurdle_fixed for that window by the "
    "registered fallback. Counted from the signals, before and apart from any score.\n"
)
rows = []
for s in STRATA:
    keys = [k for k, v in stratum_of.items() if v == s]
    for item in profile:
        rows.append(
            [
                label(s),
                item["cutoff"],
                item["days"],
                int(item["all_zero"][keys].sum()),
                int(item["none_28"][keys].sum()),
                int(item["under_two_28"][keys].sum()),
            ]
        )
table(
    [
        "Stratum",
        "Origin",
        "Context days",
        "All-zero context",
        "No request day in the last 28",
        "Fewer than two request days in the last 28",
    ],
    rows,
)

# 2. The family.
print(f"## The confirmatory family R01 to R36 ({n} series; BH once at q = 0.05)\n")
available = family.status.eq("available")
print(
    f"{int(available.sum())} of 36 tests available; BH over {int(family.bh_count.iloc[0])}. "
    "Differences are hurdle_dynamic minus the reference, in QScore9; negative favors "
    "hurdle_dynamic. Lower / tied / higher counts the series whose difference is below, exactly "
    "at and above zero; ties are omitted by the Wilcoxon test. H3 predicts a positive T1 median "
    "in the dense stratum and a negative one in the sparse and very sparse strata, and nothing "
    "for T2.\n"
)
rows = []
for r in family.itertuples():
    reference = f"`{r.reference}`"
    head = [r.id, label(r.stratum), MODEL_NAMES[r.model], r.horizon, f"{r.contrast} {reference}"]
    if r.status != "available":
        rows.append(head + ["unavailable (fewer than ten series)"] + [""] * 11)
        continue
    predicted = r.predicted_sign if r.contrast == "T1" else "none"
    if r.contrast != "T1":
        as_predicted = "n/a"
    elif r.median_diff == 0:
        as_predicted = "neither (median 0)"
    else:
        as_predicted = "yes" if sign(r.median_diff) == r.predicted_sign else "no"
    rows.append(
        head
        + [
            g(r.variant_mean),
            g(r.reference_mean),
            g(r.mean_diff),
            interval(r),
            g(r.median_diff),
            f"{c(r.wins)} / {c(r.ties)} / {c(r.losses)}",
            p(r.wilcoxon_p),
            p(r.wilcoxon_p_bh),
            "yes" if r.reject_bh_005 else "no",
            predicted,
            sign(r.median_diff),
            as_predicted,
        ]
    )
table(
    [
        "ID",
        "Stratum",
        "Model",
        "h",
        "Contrast, reference",
        "hurdle_dynamic mean",
        "Reference mean",
        "Mean difference",
        "95% interval",
        "Median difference",
        "Lower / tied / higher",
        "Raw p",
        "BH p",
        "BH rejects",
        "H3's sign",
        "Median's sign",
        "Median as H3 predicts",
    ],
    rows,
)

# 3. Directions from the paired table.
pairs = csv("paired_entities.csv")
print("## The direction of each family test, from the paired table\n")
print(
    "Rank sums of the absolute nonzero series differences (average ranks for ties), split by "
    "sign; the larger sum names the side the signed-rank test leans to. The p-value is "
    "recomputed with SciPy (two-sided, approximate, zero differences omitted) beside the saved "
    "one.\n"
)
rows = []
for r in family.itertuples():
    if r.status != "available":
        rows.append([r.id, label(r.stratum), "unavailable", "", "", "", "", "", ""])
        continue
    pair = pairs[pairs.id.eq(r.id)]
    diff = (pair.variant_score - pair.reference_score).to_numpy(dtype=float)
    if not np.array_equal(diff, pair.difference.to_numpy(dtype=float)) or len(diff) != r.n_entities:
        raise SystemExit(f"{r.id}: saved differences are not variant minus reference")
    nonzero = diff[diff != 0]
    ranks = stats.rankdata(np.abs(nonzero))
    below, above = ranks[nonzero < 0].sum(), ranks[nonzero > 0].sum()
    side = "hurdle_dynamic" if below > above else "reference" if above > below else "neither"
    recomputed = (
        stats.wilcoxon(nonzero, alternative="two-sided", method="approx").pvalue
        if len(nonzero)
        else 1.0
    )
    rows.append(
        [
            r.id,
            label(r.stratum),
            len(diff) - len(nonzero),
            len(nonzero),
            f"{below:,.1f}",
            f"{above:,.1f}",
            side,
            p(recomputed),
            p(r.wilcoxon_p),
        ]
    )
table(
    [
        "ID",
        "Stratum",
        "Exact ties",
        "Nonzero",
        "Rank sum, hurdle_dynamic lower",
        "Rank sum, reference lower",
        "Larger sum favors",
        "Raw p recomputed",
        "Raw p saved",
    ],
    rows,
)

# 4. Descriptors of the family rows.
descriptors = csv("family_descriptors.csv")
print("## Skill and concentration of the family's comparisons (secondary, descriptive)\n")
print(
    "Study 1's definitions: skill 1 - hurdle_dynamic / reference per series, undefined where the "
    "reference is zero; the share of the positive gains held by the five largest; the range of "
    "the mean difference with one series left out, and the series whose omission moves it most.\n"
)
table(
    [
        "ID",
        "Stratum",
        "Mean skill",
        "Median skill",
        "Skill defined",
        "Top-five share of positive gains",
        "Mean difference, one series left out: range",
        "Series whose omission moves the mean most",
        "Its difference",
    ],
    [
        [
            r.id,
            label(r.stratum),
            g(r.mean_skill),
            g(r.median_skill),
            f"{c(r.skill_defined)} of {r.n_entities}",
            g(r.top_five_share_of_positive_gains, 3),
            f"[{g(r.leave_one_out_min)}, {g(r.leave_one_out_max)}]",
            f"`{r.most_influential_series}`",
            g(r.most_influential_difference),
        ]
        for r in descriptors.itertuples()
    ],
)

# 5. Per stratum, the other variants' QScore9 contrasts.
strata_rows = csv("secondary_strata_contrasts.csv")
in_family = {(r.stratum, r.variant, r.reference, r.horizon): r.id for r in family.itertuples()}
print(
    "## Per stratum: hurdle_fixed and occurrence_model_size_count, QScore9 "
    "(secondary, unadjusted)\n"
)
print(
    "hurdle_fixed is the run's `<model>_hurdle` (Study 2's hurdle); negative favors the variant "
    "named first.\n"
)
sub = strata_rows[
    strata_rows.metric.eq("qscore9")
    & ~strata_rows.variant.str.endswith("_hurdle_dynamic")
    & strata_rows.status.eq("secondary")
]
for s in STRATA:
    block = sub[sub.stratum.eq(s)]
    if block.empty:
        continue
    print(f"### {label(s)}\n")
    table(
        [
            "Variant",
            "Reference",
            "h",
            "Variant mean",
            "Reference mean",
            "Mean difference",
            "95% interval",
            "Median difference",
            "Lower / tied / higher",
            "Raw p",
        ],
        [
            [
                f"`{r.variant}`",
                f"`{r.reference}`",
                r.horizon,
                g(r.variant_mean),
                g(r.reference_mean),
                g(r.mean_diff),
                interval(r),
                g(r.median_diff),
                f"{c(r.wins)} / {c(r.ties)} / {c(r.losses)}",
                p(r.wilcoxon_p),
            ]
            for r in block.itertuples()
        ],
    )

# 6. The family's pairs on the other metrics, per stratum.
print("## The family's pairs on the other scores, per stratum (secondary, unadjusted)\n")
sub = strata_rows[strata_rows.metric.ne("qscore9")].copy()
sub["family_id"] = [
    in_family.get((r.stratum, r.variant, r.reference, r.horizon)) for r in sub.itertuples()
]
sub = sub[sub.family_id.notna()]
for metric, name in (
    ("context_scaled_qscore9", "Context-scaled QScore9"),
    ("occurrence_brier", "Occurrence Brier score"),
    ("discrete_crps", "Discrete CRPS (available where both forecasts carry a certified law)"),
):
    print(f"### {name}\n")
    rows = []
    for r in sub[sub.metric.eq(metric)].sort_values("family_id").itertuples():
        ok = r.status == "secondary"
        rows.append(
            [
                r.family_id,
                label(r.stratum),
                c(r.n_entities),
                c(r.n_entities_unavailable),
                g(r.mean_diff) if ok else "",
                interval(r) if ok else "",
                g(r.median_diff) if ok else "",
                f"{c(r.wins)} / {c(r.ties)} / {c(r.losses)}" if ok else "",
                p(r.wilcoxon_p) if ok else "",
                "secondary" if ok else f"{r.status} ({r.unavailable_reason})",
            ]
        )
    table(
        [
            "ID",
            "Stratum",
            "Series",
            "Unavailable",
            "Mean difference",
            "95% interval",
            "Median difference",
            "Lower / tied / higher",
            "Raw p",
            "Status",
        ],
        rows,
    )

# 7. Pooled tables.
form = csv("secondary_pooled_study2_form.csv")
print(f"## Pooled over all {n} series, in Study 2's form (P01 to P18; secondary)\n")
print(
    "Study 2's eighteen contrasts in its order, every series weighted equally across strata; the "
    "BH column is within this table only and is not confirmatory.\n"
)
table(
    [
        "ID",
        "Variant",
        "Reference",
        "h",
        "Variant mean",
        "Reference mean",
        "Mean difference",
        "95% interval",
        "Median difference",
        "Lower / tied / higher",
        "Raw p",
        "BH p within the table",
    ],
    [
        [
            r.id,
            f"`{r.variant}`",
            f"`{r.reference}`",
            r.horizon,
            g(r.variant_mean),
            g(r.reference_mean),
            g(r.mean_diff),
            interval(r),
            g(r.median_diff),
            f"{c(r.wins)} / {c(r.ties)} / {c(r.losses)}",
            p(r.wilcoxon_p),
            p(r.wilcoxon_p_bh_within_table),
        ]
        for r in form[form.metric.eq("qscore9")].itertuples()
    ],
)
pooled = csv("secondary_pooled_contrasts.csv")
print(f"## Pooled over all {n} series, Study 3's pairs, QScore9 (secondary, unadjusted)\n")
table(
    [
        "Variant",
        "Reference",
        "h",
        "Variant mean",
        "Reference mean",
        "Mean difference",
        "95% interval",
        "Median difference",
        "Lower / tied / higher",
        "Raw p",
    ],
    [
        [
            f"`{r.variant}`",
            f"`{r.reference}`",
            r.horizon,
            g(r.variant_mean),
            g(r.reference_mean),
            g(r.mean_diff),
            interval(r),
            g(r.median_diff),
            f"{c(r.wins)} / {c(r.ties)} / {c(r.losses)}",
            p(r.wilcoxon_p),
        ]
        for r in pooled[pooled.metric.eq("qscore9") & pooled.status.eq("secondary")].itertuples()
    ],
)

# 8. Mean scores per model and stratum.
scores = csv("secondary_scores.csv")
for horizon in (7, 30):
    print(f"## Mean QScore9 per model and stratum, horizon {horizon} (equal series)\n")
    sub = scores[scores.horizon.eq(horizon)]
    table(
        ["Model", *(label(s) for s in (*STRATA, "all"))],
        [
            [f"`{m}`"]
            + [
                g(sub[sub.model.eq(m) & sub.stratum.eq(s)].qscore9.iloc[0])
                if len(sub[sub.model.eq(m) & sub.stratum.eq(s)])
                else ""
                for s in (*STRATA, "all")
            ]
            for m in VARIANTS
        ],
    )
for s in (*STRATA, "all"):
    sub = scores[scores.stratum.eq(s)]
    if sub.empty:
        continue
    print(f"## Other scores per model, {label(s)} (equal series)\n")
    rows = []
    for m in VARIANTS:
        a = sub[sub.model.eq(m) & sub.horizon.eq(7)].iloc[0]
        b = sub[sub.model.eq(m) & sub.horizon.eq(30)].iloc[0]
        rows.append(
            [
                f"`{m}`",
                g(a.context_scaled_qscore9),
                g(b.context_scaled_qscore9),
                g(a.occurrence_brier),
                g(b.occurrence_brier),
                g(b.discrete_crps),
                c(b.discrete_crps_n_entities),
                f"{c(b.crps_certified)} / {c(b.crps_with_count_distribution)} / "
                f"{c(b.crps_forecasts)}",
            ]
        )
    table(
        [
            "Model",
            "Scaled QScore9 h7",
            "Scaled QScore9 h30",
            "Brier h7",
            "Brier h30",
            "CRPS h30",
            "CRPS series defined, h30",
            "CRPS certified / with law / all, h30",
        ],
        rows,
    )

# 9. Accounting.
accounting = csv("secondary_accounting.csv")
for s in (*STRATA, "all"):
    for horizon in (30, 7):
        sub = accounting[accounting.stratum.eq(s) & accounting.horizon.eq(horizon)]
        if sub.empty:
            continue
        print(
            f"## QScore9 accounting, {label(s)}, horizon {horizon} "
            "(equal series; the parts sum to the score)\n"
        )
        rows = []
        for m in ACCOUNTED:
            r = sub[sub.model.eq(m)].iloc[0]
            rows.append(
                [
                    f"`{m}`",
                    g(r.qscore9),
                    g(r.zero),
                    g(r.positive_over),
                    g(r.positive_under),
                    f"{r.max_abs_window_residual:.2g}",
                ]
            )
        table(
            [
                "Model",
                "QScore9",
                "Zero days",
                "Positive, over",
                "Positive, under",
                "Largest residual",
            ],
            rows,
        )

# 10. PIT.
pit = csv("pit_histograms.csv")
for s in (*STRATA, "all"):
    sub = pit[pit.stratum.eq(s) & pit.horizon.eq(30)]
    if sub.empty:
        continue
    print(f"## Randomized PIT, {label(s)}, horizon 30: fraction of target days per tenth\n")
    rows = []
    for m in VARIANTS:
        r = sub[sub.model.eq(m)].iloc[0]
        if r.status != "available":
            rows.append([f"`{m}`", "unavailable"] + [""] * 9)
            continue
        rows.append([f"`{m}`"] + [f"{getattr(r, f'fraction{b + 1:02}'):.3f}" for b in range(10)])
    table(["Model", *(f"{b / 10:.1f}-{(b + 1) / 10:.1f}" for b in range(10))], rows)

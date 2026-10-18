"""Figures for the Study 1 report and the paper, drawn from the saved files only.

Reads the evidence package under reports/registered-2026-09-13/ for the report's three figures,
the
two Study 2 runs and the Study 3 run under reports/ for the paper's appendix figures, and, for the
paper's four body figures, the panel status files under study/, the three runs' per-series scores
and
the two panel manifests. The completion-floor figure is drawn from the registered completion formula
alone and needs no asset. Writes PDF and PNG figures beside this script. No model is loaded, nothing
is
fitted, no test is run. Run from the repository root:

    .\\.venv\\Scripts\\python.exe paper/figures/make_figures.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports" / "registered-2026-09-13"
NPM = ROOT / "reports" / "study2-npm" / "run-2026-10-15"
NPM_PANEL = ROOT / "reports" / "study2-npm" / "panel"
SYNTHETIC = ROOT / "reports" / "study2-synthetic-2026-10-15"
NYC311 = ROOT / "reports" / "study3-nyc311" / "run-2026-10-17"
NYC311_PANEL = ROOT / "reports" / "study3-nyc311" / "panel"
STUDY = ROOT / "study"
OUT = Path(__file__).resolve().parent

INFERENCE = REPORT / "inference" / "inference.csv"
CURVES = REPORT / "posthoc" / "posthoc-contribution-curves.csv"
PAIRED = REPORT / "posthoc" / "posthoc-paired-repositories.csv"
NPM_PAIRED = NPM / "inference" / "paired_entities.csv"
NPM_INFERENCE = NPM / "inference" / "inference.csv"
SYNTHETIC_CELLS = SYNTHETIC / "inference" / "secondary_cells_contrasts.csv"
NYC311_INFERENCE = NYC311 / "inference" / "inference.csv"

MODELS = ["chronos2", "timesfm3", "timesfm2p5"]
MODEL_LABEL = {"chronos2": "Chronos-2", "timesfm3": "TimesFM 3", "timesfm2p5": "TimesFM 2.5"}
MODEL_COLOR = {"chronos2": "#0072B2", "timesfm3": "#D55E00", "timesfm2p5": "#009E73"}
REFERENCES = ["local_mean_28", "autoets_weekly"]
REFERENCE_LABEL = {"local_mean_28": "28-day local mean", "autoets_weekly": "weekly AutoETS"}
HORIZONS = [7, 30, 90]
STRATA = ["20-99", "100-999", "1000+"]
STRATUM_COLOR = {"20-99": "#0072B2", "100-999": "#D55E00", "1000+": "#009E73"}
PARTS = ["qscore9", "zero", "positive_over", "positive_under"]
PART_COLOR = {
    "qscore9": "black",
    "zero": "#0072B2",
    "positive_over": "#D55E00",
    "positive_under": "#009E73",
}
PART_LABEL = {
    "qscore9": "total",
    "zero": "zero days",
    "positive_over": "positive days, overprediction",
    "positive_under": "positive days, underprediction",
}
DOMINANT = "aggregate-error"
CONTRAST_LABEL = {
    "_completed": "hurdle vs its completed control",
    "hurdle_count_28": "hurdle vs the count hurdle",
    "local_mean_28": "raw deciles vs the local mean",
}
Z_COLOR = {0.2: "#0072B2", 0.8: "#D55E00", 0.95: "#009E73"}
# The zero-fraction bins of the signature figure, the ones the step-back read of 2026-10-17 used.
BINS = [0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.97, 1.0001]
ROUND_TRIP = {"float_precision": "round_trip"}

plt.rcParams.update({"font.size": 8, "axes.titlesize": 9, "legend.fontsize": 7})


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def select(frame, reference, model, horizon):
    mask = (frame["reference"] == reference) & (frame["model"] == model)
    return frame[mask & (frame["horizon"] == horizon)]


def figure_paired_differences(inference):
    """Mean difference with its pointwise 95% interval, the median and the win count."""
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.0), constrained_layout=True)
    for ax, reference in zip(axes, REFERENCES):
        positions, labels = [], []
        for h_index, horizon in enumerate(HORIZONS):
            for m_index, model in enumerate(MODELS):
                row = select(inference, reference, model, horizon).iloc[0]
                x = h_index * 4 + m_index
                positions.append(x)
                labels.append(MODEL_LABEL[model])
                low = row["mean_diff"] - row["mean_diff_ci_low"]
                high = row["mean_diff_ci_high"] - row["mean_diff"]
                ax.errorbar(
                    x,
                    row["mean_diff"],
                    yerr=[[low], [high]],
                    fmt="o",
                    color="black",
                    markersize=3.5,
                    capsize=2,
                    linewidth=0.9,
                    label="mean difference with 95% interval" if x == 0 else None,
                )
                ax.plot(
                    x,
                    row["median_diff"],
                    marker="D",
                    markerfacecolor="white",
                    markeredgecolor="#D55E00",
                    markersize=4,
                    linestyle="none",
                    label="median difference" if x == 0 else None,
                )
                wins = int(round(row["repo_win_rate"] * row["n_repos"]))
                ax.annotate(
                    f"{wins}",
                    (x, row["mean_diff_ci_low"]),
                    textcoords="offset points",
                    xytext=(0, -9),
                    ha="center",
                    fontsize=6,
                    color="#444444",
                )
        ax.axhline(0, color="#888888", linewidth=0.7)
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=6.5)
        for h_index, horizon in enumerate(HORIZONS):
            ax.text(
                h_index * 4 + 1,
                1.02,
                f"{horizon} days",
                transform=ax.get_xaxis_transform(),
                ha="center",
                fontsize=7,
            )
        ax.set_title(f"against {REFERENCE_LABEL[reference]}", pad=12)
        ax.set_ylabel("QScore9, model minus reference")
        ax.grid(axis="y", linewidth=0.3, alpha=0.6)
        ymin, ymax = ax.get_ylim()
        ax.set_ylim(ymin - 0.12 * (ymax - ymin), ymax)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=2, frameon=False)
    save(fig, "fig-paired-differences")


def figure_cumulative(curves, horizon=30):
    """Signed cumulative contribution curves of the post-hoc accounting (the report's figure)."""
    fig, axes = plt.subplots(2, 3, figsize=(6.6, 4.4), sharex=True, constrained_layout=True)
    for r_index, reference in enumerate(REFERENCES):
        for m_index, model in enumerate(MODELS):
            ax = axes[r_index, m_index]
            rows = select(curves, reference, model, horizon).sort_values("rank")
            fraction = np.r_[0, rows["repository_fraction"].to_numpy()]
            for part in PARTS:
                y = np.r_[0, rows[f"cumulative_{part}_difference"].to_numpy()]
                ax.plot(
                    fraction,
                    y,
                    color=PART_COLOR[part],
                    linewidth=1.2 if part == "qscore9" else 0.9,
                    label=PART_LABEL[part],
                )
            ax.axhline(0, color="#888888", linewidth=0.6)
            if r_index == 0:
                ax.set_title(MODEL_LABEL[model])
            ax.grid(linewidth=0.3, alpha=0.6)
            if m_index == 0:
                ax.set_ylabel(f"vs {REFERENCE_LABEL[reference]}\ncumulative mean difference")
            if r_index == 1:
                ax.set_xlabel("repository fraction (sorted)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=4, frameon=False)
    save(fig, f"fig-posthoc-cumulative-h{horizon}")


def figure_zero_fraction(paired, horizon=30):
    """Paired difference against the context zero fraction, by sampling stratum."""
    fig, axes = plt.subplots(2, 3, figsize=(6.6, 4.4), sharex=True, constrained_layout=True)
    for r_index, reference in enumerate(REFERENCES):
        for m_index, model in enumerate(MODELS):
            ax = axes[r_index, m_index]
            rows = select(paired, reference, model, horizon)
            for stratum in STRATA:
                part = rows[rows["sampling_stratum"] == stratum]
                ax.scatter(
                    part["context_zero_fraction"],
                    part["qscore9_difference"],
                    s=7,
                    color=STRATUM_COLOR[stratum],
                    alpha=0.7,
                    linewidths=0,
                    label=f"day-90 stratum {stratum}",
                )
            ax.axhline(0, color="#888888", linewidth=0.6)
            ax.set_yscale("symlog", linthresh=0.01)
            if r_index == 0:
                ax.set_title(MODEL_LABEL[model])
            ax.grid(linewidth=0.3, alpha=0.6)
            if m_index == 0:
                ax.set_ylabel(f"vs {REFERENCE_LABEL[reference]}\nQScore9 difference (symlog)")
            if r_index == 1:
                ax.set_xlabel("context zero fraction")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=3, frameon=False)
    save(fig, f"fig-posthoc-zero-fraction-h{horizon}")


def symlog_pad(value, direction, factor=2.5):
    """Push an axis limit one step outward on a symmetric log scale (linear below 0.01)."""
    if abs(value) < 0.01:
        return direction * 0.02
    return value * factor if (value > 0) == (direction > 0) else value / factor


def contrast_kind(reference):
    return "_completed" if reference.endswith("_completed") else reference


def figure_npm_paired(paired, inference):
    """Study 2 on npm: the 209 paired differences of each of the 18 rows, dominant series marked."""
    fig, axes = plt.subplots(1, 3, figsize=(6.6, 3.2), constrained_layout=True)
    kinds = list(CONTRAST_LABEL)
    rng = np.random.default_rng(20260916)
    for ax, kind in zip(axes, kinds):
        rows = inference[inference["reference"].map(contrast_kind) == kind].sort_values("id")
        positions, labels = [], []
        for x, (_, row) in enumerate(rows.iterrows()):
            series = paired[paired["id"] == row["id"]]
            others = series[series["entity"] != DOMINANT]
            dominant = series[series["entity"] == DOMINANT]
            jitter = rng.uniform(-0.22, 0.22, size=len(others))
            ax.scatter(
                x + jitter,
                others["difference"],
                s=4,
                color="#0072B2",
                alpha=0.45,
                linewidths=0,
                label="one of the other 208 series" if (ax is axes[0] and x == 0) else None,
            )
            ax.scatter(
                [x],
                dominant["difference"],
                s=22,
                color="#C00000",
                marker="o",
                clip_on=False,
                zorder=3,
                label=DOMINANT if (ax is axes[0] and x == 0) else None,
            )
            ax.hlines(
                row["median_diff"],
                x - 0.3,
                x + 0.3,
                color="black",
                linewidth=1.1,
                zorder=4,
                label="median difference" if (ax is axes[0] and x == 0) else None,
            )
            positions.append(x)
            model = row["model"].split("_")[0]
            labels.append(f"{row['id']} {MODEL_LABEL[model]} h{row['horizon']}")
        ax.axhline(0, color="#888888", linewidth=0.6)
        ax.set_yscale("symlog", linthresh=0.01)
        low, high = ax.get_ylim()
        ax.set_ylim(symlog_pad(low, -1), symlog_pad(high, 1))
        ax.set_xlim(-0.6, len(positions) - 0.4)
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, rotation=70, ha="right", fontsize=5.5)
        ax.set_title(CONTRAST_LABEL[kind])
        ax.grid(axis="y", linewidth=0.3, alpha=0.6)
        if ax is axes[0]:
            ax.set_ylabel("QScore9, variant minus reference (symlog)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=3, frameon=False)
    save(fig, "fig-s2-npm-paired-differences")


def figure_synthetic_cells(cells, horizon=30):
    """Study 2 on the grid: the mean paired difference of each contrast in each of the 18 cells."""
    rows = cells[(cells["metric"] == "qscore9") & (cells["horizon"] == horizon)]
    ids = ["S01", "S02", "S03", "S04", "S05", "S06"]
    fig, axes = plt.subplots(2, 3, figsize=(6.6, 4.6), sharey=True, constrained_layout=True)
    order = rows.drop_duplicates("cell_id").sort_values("cell_id")
    cell_labels = [
        f"z={r.zero_probability:g}, μ+={int(r.positive_mean)}, ρ={r.persistence:g}"
        for r in order.itertuples()
    ]
    for ax, cid in zip(axes.ravel(), ids):
        part = rows[rows["id"] == cid].set_index("cell_id").loc[order["cell_id"]]
        colors = [Z_COLOR[z] for z in part["zero_probability"]]
        y = np.arange(len(part))
        ax.barh(y, part["mean_diff"], color=colors, height=0.7)
        ax.axvline(0, color="#888888", linewidth=0.6)
        ax.set_yticks(y)
        ax.set_yticklabels(cell_labels, fontsize=5.5)
        ax.invert_yaxis()
        ax.set_xscale("symlog", linthresh=0.01)
        ax.set_xticks([-1, -0.1, 0, 0.1, 1])
        ax.set_xticklabels(["-1", "-0.1", "0", "0.1", "1"], fontsize=6)
        ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        first = part.iloc[0]
        model = MODEL_LABEL[first["model"].split("_")[0]]
        reference = "control" if first["reference"].endswith("_completed") else "count hurdle"
        ax.set_title(f"{cid}: {model} hurdle vs {reference}", fontsize=7)
        ax.grid(axis="x", linewidth=0.3, alpha=0.6)
    for ax in axes[1]:
        ax.set_xlabel("mean difference (symlog)", fontsize=7)
    handles = [plt.Rectangle((0, 0), 1, 1, color=Z_COLOR[z]) for z in Z_COLOR]
    fig.legend(
        handles,
        [f"zero probability z = {z:g}" for z in Z_COLOR],
        loc="outside lower center",
        ncol=3,
        frameon=False,
    )
    save(fig, "fig-s2-synthetic-cells")


def figure_nyc311_family(inference):
    """Study 3 on NYC 311: the 36 mean differences with intervals and medians, by stratum."""
    strata = ["dense", "sparse", "very_sparse"]
    stratum_label = {"dense": "dense", "sparse": "sparse", "very_sparse": "very sparse"}
    predicted = {"dense": 1, "sparse": -1, "very_sparse": -1}
    fig, axes = plt.subplots(1, 3, figsize=(6.6, 3.4), constrained_layout=True)
    for ax, stratum in zip(axes, strata):
        rows = inference[inference["stratum"] == stratum].sort_values("id")
        positions, labels = [], []
        for x, (_, row) in enumerate(rows.iterrows()):
            is_t1 = row["contrast"] == "T1"
            color = "#0072B2" if is_t1 else "#D55E00"
            rejects = bool(row["reject_bh_005"])
            low = row["mean_diff"] - row["mean_diff_ci_low"]
            high = row["mean_diff_ci_high"] - row["mean_diff"]
            ax.errorbar(
                x,
                row["mean_diff"],
                yerr=[[low], [high]],
                fmt="o",
                color=color,
                markerfacecolor=color if rejects else "white",
                markersize=3.5,
                capsize=1.5,
                linewidth=0.8,
                label=(
                    "T1, mean with 95% interval (filled: rejects)"
                    if (ax is axes[0] and row["id"] == "R01")
                    else "T2, mean with 95% interval (filled: rejects)"
                    if (ax is axes[0] and row["id"] == "R02")
                    else None
                ),
            )
            ax.plot(
                x,
                row["median_diff"],
                marker="_",
                color="black",
                markersize=7,
                markeredgewidth=1.2,
                linestyle="none",
                label="median difference" if (ax is axes[0] and row["id"] == "R01") else None,
            )
            positions.append(x)
            labels.append(f"{row['id']} {MODEL_LABEL[row['model']]} h{row['horizon']}")
        ax.axhline(0, color="#888888", linewidth=0.6)
        ax.set_yscale("symlog", linthresh=0.001)
        low, high = ax.get_ylim()
        ax.set_ylim(symlog_pad(low, -1), symlog_pad(high, 1))
        ax.set_xlim(-0.6, len(positions) - 0.4)
        # The half-plane of H3's predicted T1 sign is shaded.
        if predicted[stratum] > 0:
            ax.axhspan(0, ax.get_ylim()[1], color="#0072B2", alpha=0.06, linewidth=0)
        else:
            ax.axhspan(ax.get_ylim()[0], 0, color="#0072B2", alpha=0.06, linewidth=0)
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, rotation=70, ha="right", fontsize=5.5)
        ax.set_title(f"{stratum_label[stratum]}, n = 100")
        ax.grid(axis="y", linewidth=0.3, alpha=0.6)
        if ax is axes[0]:
            ax.set_ylabel("QScore9, hurdle_dynamic minus reference (symlog)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=3, frameon=False)
    save(fig, "fig-s3-nyc311-family")


# --- the paper's four body figures ---------------------------------------------------------------


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def box(ax, x, y, w, h, title, lines, face="#F4F4F4", edge="#444444"):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.01,rounding_size=0.015",
            linewidth=0.8,
            edgecolor=edge,
            facecolor=face,
        )
    )
    ax.text(x + w / 2, y + h - 0.04, title, ha="center", va="top", fontsize=7.2, weight="bold")
    for i, line in enumerate(lines):
        ax.text(
            x + w / 2,
            y + h - 0.105 - 0.05 * i,
            line,
            ha="center",
            va="top",
            fontsize=5.8,
            family="monospace" if line.startswith(" ") else None,
            color="#333333",
        )


def figure_design():
    """The design at a glance: the two-by-two of forecasters and the three panels."""
    s1_strata = pd.read_csv(REPORT / "evidence" / "panel-diagnostic" / "strata.csv")
    s1_panel = load_json(REPORT / "evidence" / "panel" / "panel-summary.json")
    npm_status = load_json(STUDY / "study2" / "npm_panel_status.json")
    nyc_status = load_json(STUDY / "study3" / "nyc311_panel_status.json")
    grid = load_json(STUDY / "study2" / "grid_manifest.json")
    s1_frame = int(s1_strata.frame_size.sum())
    npm_strata = npm_status["achieved_strata"]
    nyc_frame = nyc_status["frame"]["eligible_frame_size"]
    nyc_series = sum(v["achieved"] for v in nyc_status["achieved_strata"].values())

    fig = plt.figure(figsize=(7.0, 3.6))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    # Left: the two-by-two, occurrence source (rows) by positive-law source (columns).
    ax.text(
        0.25,
        0.965,
        "The forecasters: where each part comes from",
        ha="center",
        fontsize=8,
        weight="bold",
    )
    ax.text(0.18, 0.905, "positive law from the model", ha="center", fontsize=6.5)
    ax.text(0.385, 0.905, "positive law from a count law", ha="center", fontsize=6.5)
    ax.text(0.035, 0.74, "occurrence\nfrom the\nmodel", ha="center", va="center", fontsize=6.5)
    ax.text(0.035, 0.37, "occurrence\nfrom the\ncontext", ha="center", va="center", fontsize=6.5)
    box(
        ax,
        0.08,
        0.61,
        0.195,
        0.27,
        "completed (control)",
        ["nine deciles completed", "into a count law", " <m>_completed"],
    )
    box(
        ax,
        0.29,
        0.61,
        0.195,
        0.27,
        "fourth cell",
        [
            "model's 1 - F(0) with the",
            "shifted-Poisson law",
            " <m>_occurrence_",
            " model_size_count",
        ],
        face="#FBF3E6",
    )
    box(
        ax,
        0.08,
        0.12,
        0.195,
        0.43,
        "hurdle",
        [
            "28-day Jeffreys p (fixed)",
            " <m>_hurdle",
            "",
            "discounted Beta-",
            "Bernoulli p (dynamic)",
            " <m>_hurdle_dynamic",
        ],
    )
    box(
        ax,
        0.29,
        0.12,
        0.195,
        0.43,
        "count baselines",
        [
            "Jeffreys p, shifted Poisson",
            " hurdle_count_28",
            "Jeffreys p, empirical law",
            " hurdle_empirical_28",
            "discounted p and size",
            " dynamic_count",
        ],
    )
    ax.text(
        0.28,
        0.055,
        "Also scored: the raw nine deciles (<m>_raw), the 28-day local mean and weekly AutoETS;\n"
        "the TSB hurdle (post hoc) is the count hurdle with TSB's two estimates.",
        ha="center",
        va="center",
        fontsize=5.8,
        color="#333333",
    )
    # Right: the panels as three columns, and the grid.
    ax.text(0.76, 0.965, "The panels", ha="center", fontsize=8, weight="bold")
    cols = [
        (
            "GitHub stars",
            [
                f"frame {s1_frame:,}",
                "repositories",
                "seeded order in three",
                "day-90 activity strata",
                f"{s1_panel['n_accepted']} series",
                "horizons 7, 30, 90",
            ],
        ),
        (
            "npm downloads",
            [
                f"inventory {npm_status['inventory']['names']:,}",
                "names; hash order to",
                f"{npm_status['candidate_pool_size']:,} eligible",
                "zero-fraction strata",
                f"{npm_status['series']} series ({npm_strata['dense']['achieved']}, "
                f"{npm_strata['sparse']['achieved']}, {npm_strata['very_sparse']['achieved']})",
                "horizons 7, 30",
            ],
        ),
        (
            "NYC 311 requests",
            [
                f"frame {nyc_frame:,} problem-",
                "by-board cells, hash order",
                "zero-fraction strata",
                f"{nyc_series} series",
                "100 per stratum",
                "horizons 7, 30",
            ],
        ),
    ]
    for i, (title, lines) in enumerate(cols):
        box(ax, 0.52 + 0.16 * i, 0.45, 0.15, 0.44, title, lines, face="#EEF3F8")
    box(
        ax,
        0.52,
        0.12,
        0.47,
        0.27,
        "synthetic grid",
        [
            f"{grid['n_cells']} cells: z in {{0.2, 0.8, 0.95}}, positive mean in {{1, 5, 25}},",
            f"persistence in {{0, 0.8}}; {grid['replicates_per_cell']} replicates per cell, "
            f"{grid['n_series']} series",
            f"of {grid['observations']} days; origins "
            f"{', '.join(str(o) for o in grid['origins'])}; the positive law is",
            "the count hurdle's own family; an oracle is a diagnostic",
        ],
        face="#EEF3F8",
    )
    save(fig, "fig-design")


def load_scores_with_zero_fraction(scores, manifest):
    d = pd.read_csv(scores, **ROUND_TRIP)
    z = {s["series_id"]: s["zero_fraction"] for s in load_json(manifest)["series"]}
    return d.assign(zf=d.series_id.map(z))


def binned_shares(d, variant, horizon, score):
    """Per zero-fraction bin, over the three models' series pairs: n, lower, tied, higher."""
    parts = []
    for m in MODELS:
        a = d[(d.model == f"{m}_{variant}") & (d.horizon == horizon)].set_index("series_id")
        b = d[(d.model == f"{m}_completed") & (d.horizon == horizon)].set_index("series_id")
        parts.append(pd.DataFrame(dict(diff=a[score] - b[score], zf=a.zf)).dropna())
    c = pd.concat(parts)
    groups = c.groupby(pd.cut(c.zf, BINS, right=False), observed=True)["diff"]
    rows = []
    for k, x in groups:
        rows.append(
            dict(
                low=k.left,
                high=k.right,
                n=len(x),
                lower=int((x < 0).sum()),
                tied=int((x == 0).sum()),
                higher=int((x > 0).sum()),
            )
        )
    return pd.DataFrame(rows)


def grid_shares(grid, cells, horizon, score):
    """Per zero probability, over the three models' series pairs on the grid."""
    z_of = cells.drop_duplicates("cell_id").set_index("cell_id").zero_probability
    g = grid[grid.horizon == horizon].assign(z=lambda f: f.cell_id.map(z_of))
    rows = []
    for z in sorted(Z_COLOR):
        n = lower = tied = 0
        for m in MODELS:
            a = g[(g.model == f"{m}_hurdle") & (g.z == z)].set_index("series_id")[score]
            b = g[(g.model == f"{m}_completed") & (g.z == z)].set_index("series_id")[score]
            d = (a - b).dropna()
            n += len(d)
            lower += int((d < 0).sum())
            tied += int((d == 0).sum())
        rows.append(dict(z=z, n=n, lower=lower, tied=tied, higher=n - lower - tied))
    return pd.DataFrame(rows)


def figure_signature(npm, nyc, grid, cells):
    """The occurrence substitution against the context zero fraction: shares lower and tied per "
    "bin."""
    domains = [
        ("npm, fixed hurdle", npm, "hurdle", "#0072B2"),
        ("NYC 311, dynamic hurdle", nyc, "hurdle_dynamic", "#D55E00"),
    ]
    scores = [
        ("qscore9", "QScore9 (registered primary)"),
        ("occurrence_brier", "occurrence Brier score (declared secondary)"),
    ]
    fig, axes = plt.subplots(
        2, 2, figsize=(6.6, 4.6), sharex=True, sharey=True, constrained_layout=True
    )
    for r, (score, score_label) in enumerate(scores):
        for c, horizon in enumerate((7, 30)):
            ax = axes[r, c]
            for name, d, variant, color in domains:
                s = binned_shares(d, variant, horizon, score)
                mid = (s.low + s.high.clip(upper=1.0)) / 2
                ax.plot(
                    mid,
                    s.lower / s.n,
                    color=color,
                    marker="o",
                    markersize=3.5,
                    linewidth=1.1,
                    label=f"{name}: share lower" if (r == 0 and c == 0) else None,
                )
                ax.plot(
                    mid,
                    s.tied / s.n,
                    color=color,
                    marker="o",
                    markersize=3.5,
                    linewidth=0.9,
                    linestyle=":",
                    markerfacecolor="white",
                    label=f"{name}: share tied" if (r == 0 and c == 0) else None,
                )
                for x, row in zip(mid, s.itertuples()):
                    if r == 0 and c == 0:
                        ax.annotate(
                            f"{row.n}",
                            (x, -0.03),
                            fontsize=4.8,
                            ha="center",
                            va="top",
                            color=color,
                            xytext=(0, -2 - 6 * domains.index((name, d, variant, color))),
                            textcoords="offset points",
                        )
            gs = grid_shares(grid, cells, horizon, score)
            ax.scatter(
                gs.z,
                gs.lower / gs.n,
                color="#009E73",
                marker="s",
                s=22,
                zorder=3,
                label="grid, fixed hurdle, by zero probability: share lower"
                if (r == 0 and c == 0)
                else None,
            )
            ax.scatter(
                gs.z,
                gs.tied / gs.n,
                color="#009E73",
                marker="s",
                s=22,
                facecolors="white",
                zorder=3,
                label="grid: share tied" if (r == 0 and c == 0) else None,
            )
            ax.axhline(0.5, color="#888888", linewidth=0.6, linestyle="--")
            for edge in BINS[1:-1]:
                ax.axvline(edge, color="#DDDDDD", linewidth=0.5)
            ax.set_ylim(-0.02, 1.02)
            ax.set_xlim(-0.02, 1.02)
            ax.set_title(f"{score_label}, horizon {horizon}", fontsize=7.5)
            if c == 0:
                ax.set_ylabel("share of series pairs")
            if r == 1:
                ax.set_xlabel("context zero fraction (bins of the stratum window)")
            ax.grid(axis="y", linewidth=0.3, alpha=0.6)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=2, frameon=False)
    save(fig, "fig-signature")


def figure_floor():
    """The completion floor, from the registered completion formula alone."""
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.7), constrained_layout=True)
    # Left: the completed quantile function and count law for all-zero deciles (q9 = 0).
    ax = axes[0]
    u = np.linspace(0.0005, 0.9995, 2000)
    q9, s = 0.0, 1.0
    q = np.where(u <= 0.9, 0.0, q9 + s * np.log(0.1 / (1 - u)))
    ax.plot(u, q, color="#0072B2", linewidth=1.2, label="completed quantile function Q(u)")
    ax.plot(
        u,
        np.maximum(0, np.floor(q + 0.5)),
        color="#D55E00",
        linewidth=1.0,
        drawstyle="steps-post",
        label="rounded count floor(Q(u) + 0.5)",
    )
    ax.axhline(0.5, color="#888888", linewidth=0.6, linestyle="--")
    ax.axvline(0.9, color="#888888", linewidth=0.6, linestyle=":")
    u_star = 1 - 0.1 * np.exp(-0.5)
    ax.axvline(u_star, color="#009E73", linewidth=0.8)
    ax.annotate(
        f"P(Y > 0) = 1 - u* = {0.1 * np.exp(-0.5):.4f}",
        (u_star, 2.6),
        fontsize=6.5,
        ha="right",
        xytext=(-4, 0),
        textcoords="offset points",
        color="#009E73",
    )
    ax.set_xlim(0.8, 1.0)
    ax.set_ylim(-0.2, 4.5)
    ax.set_xlabel("u")
    ax.set_ylabel("quantile / count")
    ax.set_title("every decile zero: the exponential tail alone\nputs mass above 0.5", fontsize=7.5)
    ax.legend(fontsize=6, loc="upper left", frameon=False)
    # Right: the floor as a function of the ninth decile, with the Jeffreys estimates for 0, 1 and 2
    # positives.
    ax = axes[1]
    q9 = np.linspace(0, 0.4999, 500)
    ax.plot(
        q9,
        0.1 * np.exp(-(0.5 - q9)),
        color="#0072B2",
        linewidth=1.2,
        label="completed P(Y > 0) = 0.1 exp(-(0.5 - q9))",
    )
    for k, style in ((0, "-"), (1, "--"), (2, ":")):
        p = (k + 0.5) / 29
        ax.axhline(
            p,
            color="#D55E00",
            linewidth=0.8,
            linestyle=style,
            label=f"Jeffreys p, {k} positive day{'s' if k != 1 else ''} in 28: {p:.4f}",
        )
    ax.set_xlim(0, 0.5)
    ax.set_ylim(0, 0.11)
    ax.set_xlabel("ninth repaired decile q9 (every decile below 0.5)")
    ax.set_ylabel("probability of a positive day")
    ax.set_title("the floor: between 0.0607 and 0.1\nwhatever the model forecast", fontsize=7.5)
    ax.legend(fontsize=6, loc="lower right", frameon=False)
    ax.grid(linewidth=0.3, alpha=0.6)
    save(fig, "fig-floor")


def cumulative_curve(diff):
    d = np.sort(np.asarray(diff))
    return np.r_[0, np.arange(1, len(d) + 1) / len(d)], np.r_[0, np.cumsum(d) / len(d)]


def figure_mean_typical(curves, npm, nyc, horizon=30):
    """The mean and the typical series: signed cumulative contribution curves, raw vs local mean."""
    fig, axes = plt.subplots(1, 3, figsize=(6.6, 2.6), constrained_layout=True)
    # GitHub, from the post-hoc contribution curves of the Study 1 run.
    ax = axes[0]
    for model in MODELS:
        rows = select(curves, "local_mean_28", model, horizon).sort_values("rank")
        ax.plot(
            np.r_[0, rows["repository_fraction"].to_numpy()],
            np.r_[0, rows["cumulative_qscore9_difference"].to_numpy()],
            color=MODEL_COLOR[model],
            linewidth=1.1,
            label=MODEL_LABEL[model],
        )
    ax.set_title("GitHub stars, 300 repositories", fontsize=7.5)
    ax.set_ylabel(f"cumulative mean difference, horizon {horizon}")
    for ax, (title, d, n, symlog) in zip(
        axes[1:],
        [
            ("npm downloads, 209 series", npm, 209, True),
            ("NYC 311 requests, 300 series", nyc, 300, False),
        ],
    ):
        for model in MODELS:
            a = (
                d[(d.model == f"{model}_raw") & (d.horizon == horizon)]
                .set_index("series_id")
                .qscore9
            )
            b = (
                d[(d.model == "local_mean_28") & (d.horizon == horizon)]
                .set_index("series_id")
                .qscore9
            )
            diff = (a - b).dropna()
            assert len(diff) == n
            x, y = cumulative_curve(diff)
            ax.plot(x, y, color=MODEL_COLOR[model], linewidth=1.1)
        if symlog:
            ax.set_yscale("symlog", linthresh=0.01)
        ax.set_title(title, fontsize=7.5)
    for ax in axes:
        ax.axhline(0, color="#888888", linewidth=0.6)
        ax.axvline(0.5, color="#BBBBBB", linewidth=0.6, linestyle=":")
        ax.set_xlabel("series fraction, sorted by difference")
        ax.grid(linewidth=0.3, alpha=0.6)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=3, frameon=False)
    save(fig, "fig-mean-typical")


def main():
    inference = pd.read_csv(INFERENCE)
    curves = pd.read_csv(CURVES)
    paired = pd.read_csv(PAIRED)
    figure_paired_differences(inference)
    figure_cumulative(curves)
    figure_zero_fraction(paired)
    npm_paired = pd.read_csv(NPM_PAIRED, **ROUND_TRIP)
    npm_inference = pd.read_csv(NPM_INFERENCE, **ROUND_TRIP)
    figure_npm_paired(npm_paired, npm_inference)
    cells = pd.read_csv(SYNTHETIC_CELLS, **ROUND_TRIP)
    figure_synthetic_cells(cells)
    nyc311_inference = pd.read_csv(NYC311_INFERENCE, **ROUND_TRIP)
    figure_nyc311_family(nyc311_inference)
    # The paper's body figures.
    figure_design()
    npm = load_scores_with_zero_fraction(
        NPM / "inference" / "series_scores.csv", NPM_PANEL / "manifest.json"
    )
    nyc = load_scores_with_zero_fraction(
        NYC311 / "inference" / "series_scores.csv", NYC311_PANEL / "manifest.json"
    )
    grid = pd.read_csv(SYNTHETIC / "inference" / "series_scores.csv", **ROUND_TRIP)
    figure_signature(npm, nyc, grid, cells)
    figure_floor()
    figure_mean_typical(curves, npm, nyc)
    for name in sorted(OUT.glob("fig-*")):
        print(name.relative_to(ROOT), name.stat().st_size)


if __name__ == "__main__":
    main()

"""Figures for the Study 1 report and the paper, drawn from the saved files only.

Reads the evidence package under reports/registered-2026-09-13/ for the report's three figures, the
two Study 2 runs and the Study 3 run under reports/ for the paper's appendix figures, and, for the
paper's plotted body figures, the three runs' per-series scores and the two panel manifests. The
completion-floor figure is drawn from the registered completion formula alone and needs no asset.
The design at a glance (the paper's Figure 1) is typeset in sections/03-design.tex, not drawn here.
Writes PDF and PNG figures beside this script. No model is loaded, nothing is fitted, no test is
run. Run from the repository root:

    .\\.venv\\Scripts\\python.exe paper/figures/make_figures.py

The drawing functions take their values from the saved files; how the figures look (typeface, sizes,
colors, line weights, legends, ticks) is set in the style block below and nowhere else.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports" / "registered-2026-09-13"
NPM = ROOT / "reports" / "study2-npm" / "run-2026-10-15"
NPM_PANEL = ROOT / "reports" / "study2-npm" / "panel"
SYNTHETIC = ROOT / "reports" / "study2-synthetic-2026-10-15"
NYC311 = ROOT / "reports" / "study3-nyc311" / "run-2026-10-17"
NYC311_PANEL = ROOT / "reports" / "study3-nyc311" / "panel"
OUT = Path(__file__).resolve().parent

INFERENCE = REPORT / "inference" / "inference.csv"
CURVES = REPORT / "posthoc" / "posthoc-contribution-curves.csv"
PAIRED = REPORT / "posthoc" / "posthoc-paired-repositories.csv"
NPM_PAIRED = NPM / "inference" / "paired_entities.csv"
NPM_INFERENCE = NPM / "inference" / "inference.csv"
SYNTHETIC_CELLS = SYNTHETIC / "inference" / "secondary_cells_contrasts.csv"
NYC311_INFERENCE = NYC311 / "inference" / "inference.csv"

# --- the style: one typeface, one size scheme, one palette for every figure -----------------------
# The page is Computer Modern at 10 pt in both documents. Every figure is drawn at the text width of
# both (A4 with 24 mm margins: 162 mm) and saved at that size, so \includegraphics[width=\textwidth]
# prints it unscaled: text at 8 pt, tick labels and legends at 7 pt, small annotations at 6 pt, in
# Computer Modern (cmr10, with formulas in mathtext's Computer Modern). The fonts are embedded as
# TrueType (Type 42), so no Type 3 font reaches either PDF. cmr10 keeps TeX's old text encoding, in
# which <, > and _ are other glyphs: every formula is written as mathtext, and no plain label holds
# those characters. The three series colors differ in lightness (CIE L* 27, 49 and 70), so they stay
# apart in grayscale and for color-blind readers; black is the total, the mean or the median, gray
# the reference lines.
WIDTH = 162 / 25.4
DARK, MID, LIGHT = "#003F7F", "#C45100", "#56B4E9"
INK, REFLINE, GRIDLINE = "black", "#7F7F7F", "#D9D9D9"
RED = "#C00000"
LINE, BOLD, THIN = 1.0, 1.4, 0.6
SIZE, SMALL, TINY = 8, 7, 6
plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["cmr10"],
        "mathtext.fontset": "cm",
        "axes.formatter.use_mathtext": True,
        "axes.unicode_minus": True,
        "font.size": SIZE,
        "axes.titlesize": SIZE,
        "axes.labelsize": SIZE,
        "xtick.labelsize": SMALL,
        "ytick.labelsize": SMALL,
        "legend.fontsize": SMALL,
        "axes.titlepad": 4,
        "axes.labelpad": 3,
        "axes.linewidth": THIN,
        "axes.edgecolor": INK,
        "xtick.major.width": THIN,
        "ytick.major.width": THIN,
        "xtick.minor.width": 0.4,
        "ytick.minor.width": 0.4,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "xtick.minor.size": 1.5,
        "ytick.minor.size": 1.5,
        "lines.linewidth": LINE,
        "lines.markersize": 3.5,
        "grid.color": GRIDLINE,
        "grid.linewidth": 0.4,
        "legend.frameon": False,
        "legend.handlelength": 2.2,
        "legend.columnspacing": 1.6,
        "legend.borderaxespad": 0.2,
        "figure.constrained_layout.use": True,
        "figure.constrained_layout.h_pad": 0.03,
        "figure.constrained_layout.w_pad": 0.03,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

MODELS = ["chronos2", "timesfm3", "timesfm2p5"]
MODEL_LABEL = {"chronos2": "Chronos-2", "timesfm3": "TimesFM 3", "timesfm2p5": "TimesFM 2.5"}
MODEL_COLOR = {"chronos2": DARK, "timesfm3": MID, "timesfm2p5": LIGHT}
MODEL_DASH = {"chronos2": "-", "timesfm3": "--", "timesfm2p5": "-."}
REFERENCES = ["local_mean_28", "autoets_weekly"]
REFERENCE_LABEL = {"local_mean_28": "28-day local mean", "autoets_weekly": "weekly AutoETS"}
HORIZONS = [7, 30, 90]
STRATA = ["20-99", "100-999", "1000+"]
STRATUM_COLOR = {"20-99": DARK, "100-999": MID, "1000+": LIGHT}
PARTS = ["qscore9", "zero", "positive_over", "positive_under"]
PART_COLOR = {
    "qscore9": INK,
    "zero": DARK,
    "positive_over": MID,
    "positive_under": LIGHT,
}
PART_DASH = {"qscore9": "-", "zero": "--", "positive_over": "-.", "positive_under": "-"}
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
Z_COLOR = {0.2: DARK, 0.8: MID, 0.95: LIGHT}
# The zero-fraction bins of the signature figure, the ones the step-back read of 2026-10-17 used.
BINS = [0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.97, 1.0001]
ROUND_TRIP = {"float_precision": "round_trip"}


def save(fig, name):
    # The figure keeps its own size (no tight bounding box), and the PDF carries no creation date,
    # so that a rerun writes the same bytes.
    fig.savefig(OUT / f"{name}.pdf", metadata={"CreationDate": None})
    fig.savefig(OUT / f"{name}.png", dpi=200)
    plt.close(fig)


def legend_below(fig, ax, ncol):
    """The figure's legend, outside every panel, centered under the figure."""
    handles, labels = ax.get_legend_handles_labels()
    return fig.legend(handles, labels, loc="outside lower center", ncol=ncol)


def thin_symlog(axis, base=100):
    """Major ticks every second decade on a symmetric log axis, the others as minor ticks."""
    linthresh = axis.get_transform().linthresh
    axis.set_major_locator(matplotlib.ticker.SymmetricalLogLocator(base=base, linthresh=linthresh))
    axis.set_minor_locator(
        matplotlib.ticker.SymmetricalLogLocator(base=10, linthresh=linthresh, subs=[1.0])
    )


def select(frame, reference, model, horizon):
    mask = (frame["reference"] == reference) & (frame["model"] == model)
    return frame[mask & (frame["horizon"] == horizon)]


def figure_paired_differences(inference):
    """Mean difference with its pointwise 95% interval, the median and the win count."""
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 3.0))
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
                    color=INK,
                    markersize=3.5,
                    capsize=2,
                    linewidth=THIN,
                    label="mean difference with 95% interval" if x == 0 else None,
                )
                ax.plot(
                    x,
                    row["median_diff"],
                    marker="D",
                    markerfacecolor="white",
                    markeredgecolor=MID,
                    markeredgewidth=0.9,
                    markersize=4,
                    linestyle="none",
                    label="median difference" if x == 0 else None,
                )
                wins = int(round(row["repo_win_rate"] * row["n_repos"]))
                ax.annotate(
                    f"{wins}",
                    (x, row["mean_diff_ci_low"]),
                    textcoords="offset points",
                    xytext=(0, -4),
                    ha="center",
                    va="top",
                    fontsize=TINY,
                    color=INK,
                )
        ax.axhline(0, color=REFLINE, linewidth=THIN)
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, rotation=45, ha="right", rotation_mode="anchor")
        for h_index, horizon in enumerate(HORIZONS):
            ax.text(
                h_index * 4 + 1,
                1.02,
                f"{horizon} days",
                transform=ax.get_xaxis_transform(),
                ha="center",
                va="bottom",
                fontsize=SMALL,
            )
        ax.set_title(f"against {REFERENCE_LABEL[reference]}", pad=12)
        ax.set_ylabel("QScore9 difference, model minus reference")
        ax.grid(axis="y")
        ymin, ymax = ax.get_ylim()
        ax.set_ylim(ymin - 0.12 * (ymax - ymin), ymax)
    legend_below(fig, axes[0], ncol=2)
    save(fig, "fig-paired-differences")


def figure_cumulative(curves, horizon=30):
    """Signed cumulative contribution curves of the post-hoc accounting (the report's figure)."""
    fig, axes = plt.subplots(2, 3, figsize=(WIDTH, 4.3), sharex=True)
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
                    linestyle=PART_DASH[part],
                    linewidth=BOLD if part == "qscore9" else LINE,
                    label=PART_LABEL[part],
                )
            ax.axhline(0, color=REFLINE, linewidth=THIN)
            if r_index == 0:
                ax.set_title(MODEL_LABEL[model])
            ax.grid()
            if m_index == 0:
                ax.set_ylabel(f"vs {REFERENCE_LABEL[reference]}\ncumulative mean difference")
            if r_index == 1:
                ax.set_xlabel("repository fraction (sorted)")
    legend_below(fig, axes[0, 0], ncol=4)
    save(fig, f"fig-posthoc-cumulative-h{horizon}")


def figure_zero_fraction(paired, horizon=30):
    """Paired difference against the context zero fraction, by sampling stratum."""
    fig, axes = plt.subplots(2, 3, figsize=(WIDTH, 4.3), sharex=True)
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
                    alpha=0.8,
                    linewidths=0,
                    label=f"day-90 stratum {stratum}",
                )
            ax.axhline(0, color=REFLINE, linewidth=THIN)
            ax.set_yscale("symlog", linthresh=0.01)
            if r_index == 0:
                ax.set_title(MODEL_LABEL[model])
            ax.grid()
            if m_index == 0:
                ax.set_ylabel(f"vs {REFERENCE_LABEL[reference]}\nQScore9 difference")
            if r_index == 1:
                ax.set_xlabel("context zero fraction")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=3, markerscale=2)
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
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH, 3.3))
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
                color=LIGHT,
                alpha=0.7,
                linewidths=0,
                label="one of the other 208 series" if (ax is axes[0] and x == 0) else None,
            )
            ax.scatter(
                [x],
                dominant["difference"],
                s=18,
                color=RED,
                marker="o",
                clip_on=False,
                zorder=3,
                label=DOMINANT if (ax is axes[0] and x == 0) else None,
            )
            ax.hlines(
                row["median_diff"],
                x - 0.3,
                x + 0.3,
                color=INK,
                linewidth=BOLD,
                zorder=4,
                label="median difference" if (ax is axes[0] and x == 0) else None,
            )
            positions.append(x)
            model = row["model"].split("_")[0]
            labels.append(f"{row['id']} {MODEL_LABEL[model]} h{row['horizon']}")
        ax.axhline(0, color=REFLINE, linewidth=THIN)
        ax.set_yscale("symlog", linthresh=0.01)
        low, high = ax.get_ylim()
        ax.set_ylim(symlog_pad(low, -1), symlog_pad(high, 1))
        thin_symlog(ax.yaxis)
        ax.set_xlim(-0.6, len(positions) - 0.4)
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, rotation=60, ha="right", rotation_mode="anchor")
        ax.set_title(CONTRAST_LABEL[kind])
        ax.grid(axis="y")
        if ax is axes[0]:
            ax.set_ylabel("QScore9 difference, variant minus reference")
    legend = legend_below(fig, axes[0], ncol=3)
    # The legend draws the small, faint dot larger and opaque, so that it can be seen.
    legend.legend_handles[0].set_sizes([12])
    legend.legend_handles[0].set_alpha(1)
    save(fig, "fig-s2-npm-paired-differences")


def figure_synthetic_cells(cells, horizon=30):
    """Study 2 on the grid: the mean paired difference of each contrast in each of the 18 cells."""
    rows = cells[(cells["metric"] == "qscore9") & (cells["horizon"] == horizon)]
    ids = ["S01", "S02", "S03", "S04", "S05", "S06"]
    fig, axes = plt.subplots(2, 3, figsize=(WIDTH, 5.0), sharey=True)
    order = rows.drop_duplicates("cell_id").sort_values("cell_id")
    cell_labels = [
        f"$z={r.zero_probability:g}$, $\\mu_+={int(r.positive_mean)}$, $\\rho={r.persistence:g}$"
        for r in order.itertuples()
    ]
    for ax, cid in zip(axes.ravel(), ids):
        part = rows[rows["id"] == cid].set_index("cell_id").loc[order["cell_id"]]
        colors = [Z_COLOR[z] for z in part["zero_probability"]]
        y = np.arange(len(part))
        ax.barh(y, part["mean_diff"], color=colors, height=0.7)
        ax.axvline(0, color=REFLINE, linewidth=THIN)
        ax.set_yticks(y)
        ax.set_yticklabels(cell_labels)
        ax.tick_params(axis="y", length=0)
        ax.invert_yaxis()
        ax.set_xscale("symlog", linthresh=0.01)
        ax.set_xticks([-1, -0.1, 0, 0.1, 1])
        ax.set_xticklabels(["$-1$", "$-0.1$", "$0$", "$0.1$", "$1$"])
        ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        first = part.iloc[0]
        model = MODEL_LABEL[first["model"].split("_")[0]]
        reference = "control" if first["reference"].endswith("_completed") else "count hurdle"
        ax.set_title(f"{cid}: {model} hurdle\nvs {reference}")
        ax.grid(axis="x")
    for ax in axes[1]:
        ax.set_xlabel("mean difference,\nsymmetric log scale")
    fig.get_layout_engine().set(wspace=0.04)
    handles = [plt.Rectangle((0, 0), 1, 1, color=Z_COLOR[z]) for z in Z_COLOR]
    fig.legend(
        handles,
        [f"zero probability $z = {z:g}$" for z in Z_COLOR],
        loc="outside lower center",
        ncol=3,
    )
    save(fig, "fig-s2-synthetic-cells")


def figure_nyc311_family(inference):
    """Study 3 on NYC 311: the 36 mean differences with intervals and medians, by stratum."""
    strata = ["dense", "sparse", "very_sparse"]
    stratum_label = {"dense": "dense", "sparse": "sparse", "very_sparse": "very sparse"}
    predicted = {"dense": 1, "sparse": -1, "very_sparse": -1}
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH, 3.6))
    for ax, stratum in zip(axes, strata):
        rows = inference[inference["stratum"] == stratum].sort_values("id")
        positions, labels = [], []
        for x, (_, row) in enumerate(rows.iterrows()):
            is_t1 = row["contrast"] == "T1"
            color = DARK if is_t1 else MID
            rejects = bool(row["reject_bh_005"])
            low = row["mean_diff"] - row["mean_diff_ci_low"]
            high = row["mean_diff_ci_high"] - row["mean_diff"]
            ax.errorbar(
                x,
                row["mean_diff"],
                yerr=[[low], [high]],
                fmt="o" if is_t1 else "s",
                color=color,
                markerfacecolor=color if rejects else "white",
                markersize=3.5 if is_t1 else 3.2,
                markeredgewidth=0.9,
                capsize=1.5,
                linewidth=THIN,
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
                color=INK,
                markersize=7,
                markeredgewidth=BOLD,
                linestyle="none",
                label="median difference" if (ax is axes[0] and row["id"] == "R01") else None,
            )
            positions.append(x)
            labels.append(f"{row['id']} {MODEL_LABEL[row['model']]} h{row['horizon']}")
        ax.axhline(0, color=REFLINE, linewidth=THIN)
        ax.set_yscale("symlog", linthresh=0.001)
        low, high = ax.get_ylim()
        ax.set_ylim(symlog_pad(low, -1), symlog_pad(high, 1))
        ax.set_xlim(-0.6, len(positions) - 0.4)
        # The half-plane of H3's predicted T1 sign is shaded.
        if predicted[stratum] > 0:
            ax.axhspan(0, ax.get_ylim()[1], color=DARK, alpha=0.07, linewidth=0)
        else:
            ax.axhspan(ax.get_ylim()[0], 0, color=DARK, alpha=0.07, linewidth=0)
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, rotation=60, ha="right", rotation_mode="anchor")
        ax.set_title(f"{stratum_label[stratum]}, n = 100")
        ax.grid(axis="y")
        if ax is axes[0]:
            ax.set_ylabel("QScore9 difference,\ndynamic hurdle minus reference")
    legend_below(fig, axes[0], ncol=3)
    save(fig, "fig-s3-nyc311-family")


# --- the paper's three plotted body figures -------------------------------------------------------


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


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
    """The occurrence substitution against the context zero fraction: shares lower and tied."""
    domains = [
        ("npm, fixed hurdle", npm, "hurdle", DARK),
        ("NYC 311, dynamic hurdle", nyc, "hurdle_dynamic", MID),
    ]
    marker = {DARK: "o", MID: "^"}
    scores = [
        ("qscore9", "QScore9 (registered primary)"),
        ("occurrence_brier", "occurrence Brier score (declared secondary)"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(WIDTH, 4.6), sharex=True, sharey=True)
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
                    marker=marker[color],
                    markersize=3.5,
                    linewidth=LINE,
                    label=f"{name}: share lower" if (r == 0 and c == 0) else None,
                )
                ax.plot(
                    mid,
                    s.tied / s.n,
                    color=color,
                    marker=marker[color],
                    markersize=3.5,
                    linewidth=LINE,
                    linestyle=":",
                    markerfacecolor="white",
                    label=f"{name}: share tied" if (r == 0 and c == 0) else None,
                )
                # The pairs in each bin, in a row under the top left panel (npm above NYC 311); the
                # two narrow bins at the right are set apart so that their numbers do not touch.
                for x, row in zip(mid, s.itertuples()):
                    if r == 0 and c == 0:
                        ax.annotate(
                            f"{row.n}",
                            (x, -0.03),
                            fontsize=TINY,
                            ha="right" if 0.9 < x < 0.97 else "left" if x >= 0.97 else "center",
                            va="top",
                            color=color,
                            xytext=(
                                -1 if 0.9 < x < 0.97 else 1 if x >= 0.97 else 0,
                                -5 - 7 * domains.index((name, d, variant, color)),
                            ),
                            textcoords="offset points",
                            annotation_clip=False,
                        )
            gs = grid_shares(grid, cells, horizon, score)
            ax.scatter(
                gs.z,
                gs.lower / gs.n,
                color=LIGHT,
                marker="s",
                s=20,
                zorder=3,
                label="grid, fixed hurdle, by zero probability: share lower"
                if (r == 0 and c == 0)
                else None,
            )
            ax.scatter(
                gs.z,
                gs.tied / gs.n,
                color=LIGHT,
                marker="s",
                s=20,
                facecolors="white",
                linewidths=1.0,
                zorder=3,
                label="grid: share tied" if (r == 0 and c == 0) else None,
            )
            ax.axhline(0.5, color=REFLINE, linewidth=THIN, linestyle="--")
            for edge in BINS[1:-1]:
                ax.axvline(edge, color=GRIDLINE, linewidth=0.4)
            ax.set_ylim(-0.02, 1.02)
            ax.set_xlim(-0.02, 1.02)
            ax.set_title(f"{score_label}, horizon {horizon}")
            if c == 0:
                ax.set_ylabel("share of series pairs")
            if r == 1:
                ax.set_xlabel("context zero fraction (bins of the stratum window)")
            ax.grid(axis="y")
    legend_below(fig, axes[0, 0], ncol=2)
    save(fig, "fig-signature")


def figure_floor():
    """The completion floor, from the registered completion formula alone."""
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 3.0))
    # Left: the completed quantile function and count law for all-zero deciles (q9 = 0).
    ax = axes[0]
    u = np.linspace(0.0005, 0.9995, 2000)
    q9, s = 0.0, 1.0
    q = np.where(u <= 0.9, 0.0, q9 + s * np.log(0.1 / (1 - u)))
    ax.plot(u, q, color=DARK, linewidth=LINE, label="completed quantile function $Q(u)$")
    ax.plot(
        u,
        np.maximum(0, np.floor(q + 0.5)),
        color=MID,
        linewidth=LINE,
        drawstyle="steps-post",
        label=r"rounded count $\lfloor Q(u) + 0.5 \rfloor$",
    )
    ax.axhline(0.5, color=REFLINE, linewidth=THIN, linestyle="--")
    ax.axvline(0.9, color=REFLINE, linewidth=THIN, linestyle=":")
    u_star = 1 - 0.1 * np.exp(-0.5)
    # The line at u* is named in the legend, so that no text sits in the plot.
    ax.axvline(
        u_star,
        color=INK,
        linewidth=THIN,
        label=rf"$P(Y > 0) = 1 - u^{{\!\!*}} = {0.1 * np.exp(-0.5):.4f}$",
    )
    ax.set_xlim(0.8, 1.0)
    ax.set_ylim(-0.2, 4.5)
    ax.set_xticks([0.8, 0.85, 0.9, 0.95, 1.0])
    ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.2f"))
    ax.set_xlabel("quantile level $u$")
    ax.set_ylabel("quantile / count")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1)
    ax.grid()
    # Right: the floor as a function of the ninth decile, with the Jeffreys estimates for 0, 1 and 2
    # positives.
    ax = axes[1]
    q9 = np.linspace(0, 0.4999, 500)
    ax.plot(
        q9,
        0.1 * np.exp(-(0.5 - q9)),
        color=DARK,
        linewidth=LINE,
        label=r"completed $P(Y > 0) = 0.1\, e^{-(0.5 - q_{0.9})}$",
    )
    for k, style in ((0, "-"), (1, "--"), (2, ":")):
        p = (k + 0.5) / 29
        ax.axhline(
            p,
            color=MID,
            linewidth=LINE,
            linestyle=style,
            label=f"Jeffreys $p$, {k} positive day{'s' if k != 1 else ''} in 28: {p:.4f}",
        )
    ax.set_xlim(0, 0.5)
    ax.set_ylim(0, 0.11)
    ax.set_xlabel("ninth repaired decile $q_{0.9}$ (every decile below 0.5)")
    ax.set_ylabel("probability of a positive day")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1)
    ax.grid()
    save(fig, "fig-floor")


def cumulative_curve(diff):
    d = np.sort(np.asarray(diff))
    return np.r_[0, np.arange(1, len(d) + 1) / len(d)], np.r_[0, np.cumsum(d) / len(d)]


def figure_mean_typical(curves, npm, nyc, horizon=30):
    """The mean and the typical series: signed cumulative contribution curves, raw vs local mean."""
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH, 2.6))
    # GitHub, from the post-hoc contribution curves of the Study 1 run.
    ax = axes[0]
    for model in MODELS:
        rows = select(curves, "local_mean_28", model, horizon).sort_values("rank")
        ax.plot(
            np.r_[0, rows["repository_fraction"].to_numpy()],
            np.r_[0, rows["cumulative_qscore9_difference"].to_numpy()],
            color=MODEL_COLOR[model],
            linestyle=MODEL_DASH[model],
            linewidth=LINE,
            label=MODEL_LABEL[model],
        )
    ax.set_title("GitHub stars, 300 repositories")
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
            ax.plot(x, y, color=MODEL_COLOR[model], linestyle=MODEL_DASH[model], linewidth=LINE)
        if symlog:
            ax.set_yscale("symlog", linthresh=0.01)
        ax.set_title(title)
    for ax in axes:
        ax.axhline(0, color=REFLINE, linewidth=THIN)
        ax.axvline(0.5, color=REFLINE, linewidth=THIN, linestyle=":")
        ax.set_xlabel("series fraction, sorted by difference")
        ax.grid()
    legend_below(fig, axes[0], ncol=3)
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
    # The paper's plotted body figures.
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

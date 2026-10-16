"""Figures for the Study 1 report and the paper, drawn from the saved CSVs only.

Reads three files under reports/registered-2026-09-13/ for the report's three figures, and two
files under reports/study2-npm/run-2026-10-15/ and reports/study2-synthetic-2026-10-15/ for the
paper's two Study 2 figures, and writes PDF and PNG figures beside this script. No model is loaded,
nothing is fitted, no test is run. Run from the repository root:

    .\\.venv\\Scripts\\python.exe paper/figures/make_figures.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports" / "registered-2026-09-13"
NPM = ROOT / "reports" / "study2-npm" / "run-2026-10-15"
SYNTHETIC = ROOT / "reports" / "study2-synthetic-2026-10-15"
OUT = Path(__file__).resolve().parent

INFERENCE = REPORT / "inference" / "inference.csv"
CURVES = REPORT / "posthoc" / "posthoc-contribution-curves.csv"
PAIRED = REPORT / "posthoc" / "posthoc-paired-repositories.csv"
NPM_PAIRED = NPM / "inference" / "paired_entities.csv"
NPM_INFERENCE = NPM / "inference" / "inference.csv"
SYNTHETIC_CELLS = SYNTHETIC / "inference" / "secondary_cells_contrasts.csv"

MODELS = ["chronos2", "timesfm3", "timesfm2p5"]
MODEL_LABEL = {"chronos2": "Chronos-2", "timesfm3": "TimesFM 3", "timesfm2p5": "TimesFM 2.5"}
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
    """Signed cumulative contribution curves of the post-hoc accounting."""
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
                color="#D55E00",
                marker="o",
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


def main():
    inference = pd.read_csv(INFERENCE)
    curves = pd.read_csv(CURVES)
    paired = pd.read_csv(PAIRED)
    figure_paired_differences(inference)
    figure_cumulative(curves)
    figure_zero_fraction(paired)
    npm_paired = pd.read_csv(NPM_PAIRED, float_precision="round_trip")
    npm_inference = pd.read_csv(NPM_INFERENCE, float_precision="round_trip")
    figure_npm_paired(npm_paired, npm_inference)
    cells = pd.read_csv(SYNTHETIC_CELLS, float_precision="round_trip")
    figure_synthetic_cells(cells)
    for name in sorted(OUT.glob("fig-*")):
        print(name.relative_to(ROOT), name.stat().st_size)


if __name__ == "__main__":
    main()

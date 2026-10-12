"""Figures for the Study 1 report, drawn from the saved CSVs only.

Reads three files under reports/registered-2026-09-13/ and writes PDF and PNG
figures beside this script. No model is loaded, nothing is fitted, no test is
run. Run from the repository root:

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
OUT = Path(__file__).resolve().parent

INFERENCE = REPORT / "inference" / "inference.csv"
CURVES = REPORT / "posthoc" / "posthoc-contribution-curves.csv"
PAIRED = REPORT / "posthoc" / "posthoc-paired-repositories.csv"

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


def main():
    inference = pd.read_csv(INFERENCE)
    curves = pd.read_csv(CURVES)
    paired = pd.read_csv(PAIRED)
    figure_paired_differences(inference)
    figure_cumulative(curves)
    figure_zero_fraction(paired)
    for name in sorted(OUT.glob("fig-*")):
        print(name.relative_to(ROOT), name.stat().st_size)


if __name__ == "__main__":
    main()

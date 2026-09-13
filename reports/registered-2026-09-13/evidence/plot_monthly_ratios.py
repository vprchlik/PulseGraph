"""Plot the saved calendar-matched monthly ratios; no fitted trend or inferential test."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pulsegraph.provenance import read_json

folder = Path(__file__).resolve().parent / "comparison"
data = pd.read_csv(folder / "monthly_ratios_largest_eight.csv")
selected = read_json(folder / "ratio-report.json")["largest_eight"]
fig, axes = plt.subplots(2, 4, figsize=(12, 5.8), sharex=True, sharey=True)
for ax, item in zip(axes.flat, selected, strict=True):
    frame = data[data.repo_id.eq(item["repo_id"])].sort_values("month")
    ax.plot(range(1, 13), frame.api_to_archive_ratio, color="#25659a", marker="o", markersize=3, linewidth=1.5)
    ax.axhline(1, color="#777777", linestyle="--", linewidth=0.8)
    ax.set_title(item["repo_name"], fontsize=10, loc="left")
    ax.set_ylim(0.55, 1.05)
    ax.set_xticks([1, 3, 5, 7, 9, 12], ["Jan", "Mar", "May", "Jul", "Sep", "Dec*"])
    ax.grid(axis="y", alpha=0.18)
    ax.spines[["top", "right"]].set_visible(False)
fig.supylabel("API history / GH Archive WatchEvents", fontsize=11)
fig.suptitle("2024 monthly ratios for the eight largest validation repositories", fontsize=13, x=0.07, ha="left")
fig.text(0.07, 0.035, "Los Angeles calendar with DST. *December 1–30 only for equal exposure. Largest by saved metadata star count.\n"
         "Descriptive ratios; the monthly variation does not identify when removals occurred.", fontsize=9, color="#444444")
fig.tight_layout(rect=(0.015, 0.105, 1, 0.96))
fig.savefig(folder / "monthly-ratios.png", dpi=180)
fig.savefig(folder / "monthly-ratios.svg")
plt.close(fig)
print("Saved PNG and SVG from the eight-repository monthly table.")

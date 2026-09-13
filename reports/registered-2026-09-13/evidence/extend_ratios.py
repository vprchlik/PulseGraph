"""Calendar-matched totals and monthly survivor/archive ratios from saved validation captures."""
from pathlib import Path
import numpy as np
import pandas as pd
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes

base = Path(__file__).resolve().parent
folder = base / "comparison"
daily = pd.read_csv(folder / "daily_comparison.csv")
la = daily[daily.hypothesis.eq("America/Los_Angeles")].copy()
common = la[la.scored].copy()
raw = base.parents[1] / "raw/validation-2026-09-13"
validation = read_json(raw / "validation.json")
metadata = []
for item in validation["repositories"]:
    if item["status"] != "complete":
        continue
    path = raw / item["capture"] / "repository.json"
    value = read_json(path)
    metadata.append({"repo_id": item["repo_id"], "validation_name": item["repo_name"],
                     "metadata_stars_at_capture": value["stargazers_count"],
                     "metadata_sha256": sha256_bytes(path.read_bytes())})
metadata = pd.DataFrame(metadata)
totals = common.groupby(["repo_id", "repo_name"], as_index=False).agg(
    n_matched_days=("stars", "size"), api_matched_total=("stars", "sum"),
    archive_matched_total=("watch_events", "sum"))
totals["api_to_archive_ratio"] = totals.api_matched_total / totals.archive_matched_total
totals["matched_start"] = "2024-01-01"
totals["matched_end"] = "2024-12-30"
full = la.groupby("repo_id", as_index=False).agg(
    api_full_2024_total=("stars", "sum"),
    archive_observed_2024_total_partial_dec31=("observed_watch_events", "sum"),
    archive_observed_hours=("observed_hours", "sum"))
totals = totals.merge(full, on="repo_id", validate="one_to_one").merge(
    metadata, on="repo_id", validate="one_to_one")
assert len(totals) == len(metadata) == 20
totals = totals.sort_values(["metadata_stars_at_capture", "repo_id"], ascending=[False, True])
totals.to_csv(folder / "repository_2024_totals.csv", index=False)
largest = totals.head(8).repo_id.tolist()
selected = common[common.repo_id.isin(largest)].copy()
selected["month"] = selected.event_date.str[:7]
monthly = selected.groupby(["repo_id", "repo_name", "month"], as_index=False).agg(
    n_matched_days=("stars", "size"), api_total=("stars", "sum"), archive_total=("watch_events", "sum"))
monthly["api_to_archive_ratio"] = monthly.api_total / monthly.archive_total
monthly["period_note"] = np.where(monthly.month.eq("2024-12"), "December 1-30 only; equal exposure", "complete calendar month")
assert len(monthly) == 8 * 12 and monthly.api_to_archive_ratio.notna().all()
monthly.to_csv(folder / "monthly_ratios_largest_eight.csv", index=False)
trends = []
for name, frame in monthly.groupby("repo_name"):
    values = frame.sort_values("month").api_to_archive_ratio.to_numpy()
    trends.append({"repo_name": name, "linear_ratio_slope_per_month_descriptive": float(np.polyfit(np.arange(1, 13), values, 1)[0]),
                   "minimum_monthly_ratio": float(values.min()), "maximum_monthly_ratio": float(values.max()),
                   "january_ratio": float(values[0]), "december_1_30_ratio": float(values[-1])})
report = {
    "calendar": "America/Los_Angeles", "comparison_sha256": sha256_bytes((folder / "comparison.json").read_bytes()),
    "matching_rule": "Ratios use January 1-December 30: the export lacks the last eight hours of LA December 31. No boundary counts are imputed. Full 366-day API totals and observed partial archive totals are separately recorded, without a full-year matched ratio.",
    "largest_eight_rule": "Largest current stargazers_count in metadata saved with the original validation capture; stable repo ID breaks ties. No new API request or selection by ratio.",
    "largest_eight": totals.head(8)[["repo_id", "repo_name", "metadata_stars_at_capture"]].to_dict("records"),
    "n_api_below_archive": int((totals.api_matched_total < totals.archive_matched_total).sum()),
    "n_api_equal_archive": int((totals.api_matched_total == totals.archive_matched_total).sum()),
    "n_api_above_archive": int((totals.api_matched_total > totals.archive_matched_total).sum()),
    "descriptive_monthly_slopes": trends,
    "outputs": {n: sha256_bytes((folder / n).read_bytes()) for n in ("repository_2024_totals.csv", "monthly_ratios_largest_eight.csv")},
}
atomic_json(folder / "ratio-report.json", report)
lines = ["# Validation totals and monthly ratios", "", report["matching_rule"], "", report["largest_eight_rule"], "",
         "Ratio means API divided by archive. All tables use Los Angeles with DST.", "",
         "| Repository | API, matched 365 days | Archive, matched 365 days | Ratio | API, full 366-day 2024 |", "|---|---:|---:|---:|---:|"]
for r in totals.to_dict("records"):
    lines.append(f"| {r['repo_name']} | {r['api_matched_total']:,} | {int(r['archive_matched_total']):,} | {r['api_to_archive_ratio']:.4f} | {r['api_full_2024_total']:,} |")
lines += ["", "| Repository | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec 1–30 |", "|---|" + "---:|" * 12]
for repo_id in largest:
    frame = monthly[monthly.repo_id.eq(repo_id)].sort_values("month")
    lines.append("| " + frame.repo_name.iloc[0] + " | " + " | ".join(f"{r:.3f}" for r in frame.api_to_archive_ratio) + " |")
lines += ["", "These are descriptive calendar-matched ratios. Their variation does not by itself identify removal timing or establish an age-invariant removal mechanism. "
          "The author's accepted endpoint interpretation is stored separately, verbatim, in readiness.json.", ""]
(folder / "totals-and-monthly-ratios.md").write_text("\n".join(lines), encoding="utf-8")
calendar = read_json(folder / "calendar-summary.json")
combined = ["# Star-history validation comparison", "", "All 20 repositories were attempted and captured completely; zero failures. "
    "The export contains 175,680 repository-hours including zeros. Comparison uses the same 365 nominal dates under all three hypotheses. "
    "This is endpoint validation, not forecast evaluation or an additional confirmatory test.", "",
    "| Calendar | Mean absolute difference | Exact daily agreement |", "|---|---:|---:|"]
for row in calendar["calendar_summary"]["all_scored"]:
    combined.append(f"| {row['hypothesis']} | {row['mean_absolute_difference']:.6f} | {row['exact_agreement']:.3%} |")
combined += ["", "| DST span | LA/DST MAD | Fixed UTC−8 MAD | UTC MAD |", "|---|---:|---:|---:|"]
for key, label in [("spring_15_days", "March 3–17"), ("spring_transition_day", "March 10 only"),
                   ("fall_15_days", "October 27–November 10"), ("fall_transition_day", "November 3 only")]:
    values = {r["hypothesis"]: r["mean_absolute_difference"] for r in calendar["calendar_summary"][key]}
    combined.append(f"| {label} | {values['America/Los_Angeles']:.3f} | {values['UTC-08:00']:.3f} | {values['UTC']:.3f} |")
combined += ["", "Flask on March 10: API 8, LA 9, fixed UTC−8 10, UTC 5. On November 3: API 10, LA 10, fixed UTC−8 10, UTC 9. "
    "LA transition bins contain 23 and 25 hours. The exact transition dates do not uniformly favor LA across repositories; the full-year and transition-window evidence is retained.", "",
    "| Repository | LA MAD / agreement | Fixed UTC−8 MAD / agreement | UTC MAD / agreement |", "|---|---:|---:|---:|"]
repository_comparison = pd.read_csv(folder / "repository_comparison.csv")
for name, group in repository_comparison.groupby("repo_name", sort=True):
    row = group.set_index("hypothesis")
    cells = [f"{row.loc[h, 'mean_absolute_difference']:.4f} / {row.loc[h, 'fraction_equal']:.2%}"
             for h in ("America/Los_Angeles", "UTC-08:00", "UTC")]
    combined.append("| " + name + " | " + " | ".join(cells) + " |")
combined += ["", "\n".join(lines), "", "![Monthly ratios](monthly-ratios.png)", ""]
(folder / "validation-report.md").write_text("\n".join(combined), encoding="utf-8")
print(totals[["repo_name", "api_matched_total", "archive_matched_total", "api_to_archive_ratio"]].to_string(index=False))
print(pd.DataFrame(trends).to_string(index=False))

"""Reproduce descriptive calendar evidence from the saved hourly comparison."""
import json
from pathlib import Path
import pandas as pd
from pulsegraph.provenance import atomic_json, sha256_bytes

base = Path(__file__).resolve().parent
folder = base / "comparison"
daily = pd.read_csv(folder / "daily_comparison.csv")
scored = daily[daily.scored].copy()
repositories = pd.read_csv(folder / "repository_comparison.csv")
def summary(frame):
    return frame.groupby("hypothesis").agg(
        n_repository_days=("absolute_difference", "size"),
        mean_absolute_difference=("absolute_difference", "mean"),
        exact_agreement=("equal", "mean"),
        api_total=("stars", "sum"), archive_total=("watch_events", "sum"),
    ).reset_index().to_dict("records")
windows = {
    "all_scored": scored,
    "spring_15_days": scored[scored.event_date.between("2024-03-03", "2024-03-17")],
    "fall_15_days": scored[scored.event_date.between("2024-10-27", "2024-11-10")],
    "spring_transition_day": scored[scored.event_date.eq("2024-03-10")],
    "fall_transition_day": scored[scored.event_date.eq("2024-11-03")],
    "daylight_days": scored[scored.event_date.between("2024-03-10", "2024-11-02")],
    "standard_days_excluding_transition": scored[
        ~scored.event_date.between("2024-03-10", "2024-11-03")],
}
pivot = repositories.pivot(index="repo_id", columns="hypothesis", values="mean_absolute_difference")
output = {
    "status": "descriptive_pre_freeze_validation_not_forecast_inference",
    "source_sha256": sha256_bytes((folder / "comparison.json").read_bytes()),
    "attempted": 20, "complete": 20, "failed": 0,
    "calendar_summary": {name: summary(frame) for name, frame in windows.items()},
    "repository_wins_by_mad": {
        other: {"LA_lower": int((pivot["America/Los_Angeles"] < pivot[other]).sum()),
                "tied": int((pivot["America/Los_Angeles"] == pivot[other]).sum()),
                "LA_higher": int((pivot["America/Los_Angeles"] > pivot[other]).sum())}
        for other in ("UTC", "UTC-08:00")},
    "flask": repositories[repositories.repo_name.eq("pallets/flask")].to_dict("records"),
    "flask_transition_days": daily[daily.repo_name.eq("pallets/flask") &
        daily.event_date.isin(["2024-03-10", "2024-11-03"])].to_dict("records"),
    "partial_end_day": "December 31 omitted from all scores because local calendars lack the last eight UTC hours of 2025; no zero fill",
}
atomic_json(folder / "calendar-summary.json", output)
print(json.dumps(output, indent=2))

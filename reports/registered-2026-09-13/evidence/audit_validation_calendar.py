"""Audit complete saved endpoint responses under the proposed calendar without new requests."""
from pathlib import Path
import pandas as pd
from pulsegraph.data.calendars import creation_day
from pulsegraph.data.star_history import read_capture, decode_weeks
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes

base = Path(__file__).resolve().parent
raw = base.parents[1] / "raw/validation-2026-09-13"
validation = read_json(raw / "validation.json")
rows = []
for item in validation["repositories"]:
    if item["status"] != "complete":
        continue
    folder = raw / item["capture"]
    capture, _ = read_capture(folder)
    weeks = []
    for entry in capture["responses"]:
        if entry["file"].startswith("history_"):
            weeks.extend(read_json(folder / entry["file"]))
    daily = decode_weeks(weeks)
    birth = creation_day(capture["created_at"], "America/Los_Angeles")
    expected = pd.date_range(birth, "2026-08-31")
    selected = daily[daily.nominal_date.between(birth, "2026-08-31")]
    metadata = read_json(folder / "repository.json")
    rows.append({
        "repo_id": capture["repo_id"], "repo_name": capture["repo_name"],
        "created_at": capture["created_at"], "utc_creation_date": capture["observation_start"],
        "local_creation_date": birth, "n_days": len(selected),
        "missing_days": [d.date().isoformat() for d in expected.difference(pd.to_datetime(selected.nominal_date))],
        "duplicate_days": int(selected.nominal_date.duplicated().sum()),
        "nonzero_counts_before_local_creation": int(daily[daily.nominal_date.lt(birth)].stars.sum()),
        "counts_before_utc_creation": int(daily[daily.nominal_date.lt(capture["observation_start"])].stars.sum()),
        "full_history_total": int(daily.stars.sum()), "metadata_star_count": metadata["stargazers_count"],
        "history_minus_metadata": int(daily.stars.sum()) - metadata["stargazers_count"],
        "capture_sha256": sha256_bytes((folder / "capture.json").read_bytes()),
    })
report = {
    "calendar_convention": "America/Los_Angeles", "status": "proposed, pending author sign-off",
    "nominal_label_rule": "UTC date of week timestamp plus zero-based day index; interpret this label as an LA calendar date, not an instant to convert",
    "validation_sha256": sha256_bytes((raw / "validation.json").read_bytes()),
    "repositories": rows,
}
atomic_json(base / "comparison/validation-calendar-audit.json", report)
print({"complete_captures": len(rows), "missing_days": sum(len(r["missing_days"]) for r in rows),
       "duplicate_days": sum(r["duplicate_days"] for r in rows),
       "nonzero_counts_before_local_creation": sum(r["nonzero_counts_before_local_creation"] for r in rows)})

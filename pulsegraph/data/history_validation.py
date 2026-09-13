"""External validation captures and a full 2024 daily comparison, never model evaluation."""

from pathlib import Path

import pandas as pd

from pulsegraph.data.star_history import HistoryError, read_capture
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes


def validation_status_counts(report):
    """Require all selected repositories attempted, with explicit failure accounting."""
    names = report.get("selected_repositories", [])
    entries = report.get("repositories", [])
    if (
        len(names) != 20
        or len(set(names)) != 20
        or len(entries) != 20
        or {r.get("repo_name") for r in entries} != set(names)
        or any(r.get("status") not in {"complete", "failed"} for r in entries)
    ):
        raise ValueError("All 20 selected validation repositories must be attempted")
    failures = report.get("failures")
    if not isinstance(failures, list) or any(
        f.get("repo_name") not in names
        or not isinstance(f.get("reason"), str)
        or not f["reason"].strip()
        or not isinstance(f.get("capture"), str)
        or not f["capture"].strip()
        for f in failures
    ):
        raise ValueError("Every validation failure requires an identifier, capture and reason")
    for row in entries:
        if row["status"] == "failed" and not any(
            all(f.get(key) == row.get(key) for key in ("repo_name", "capture", "reason"))
            for f in failures
        ):
            raise ValueError(
                "Every failed repository must appear in the failure log with its reason"
            )
    complete = [r for r in entries if r["status"] == "complete"]
    ids = [r.get("repo_id") for r in complete]
    if any(not isinstance(i, int) or isinstance(i, bool) or i < 0 for i in ids) or len(
        set(ids)
    ) != len(ids):
        raise ValueError("Complete validation captures require unique stable repository IDs")
    counts = {
        "n_attempted": 20,
        "n_complete": len(complete),
        "n_failed": 20 - len(complete),
        "n_failures": len(failures),
    }
    if any(report.get(key) != value for key, value in counts.items()):
        raise ValueError("Validation report counts disagree with recorded attempts and failures")
    return counts


def _save_report(path, report):
    report["n_attempted"] = len(report["repositories"])
    report["n_complete"] = sum(r["status"] == "complete" for r in report["repositories"])
    report["n_failed"] = report["n_attempted"] - report["n_complete"]
    report["n_failures"] = len(report["failures"])
    atomic_json(path, report)


def fetch_validation(client, selection_path, output_dir):
    selection = read_json(selection_path)
    entries = selection["repositories"]
    if len(entries) != 20 or len({r["repo_name"] for r in entries}) != 20:
        raise ValueError("Validation selection must contain 20 distinct repositories")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    selection_hash = sha256_bytes(Path(selection_path).read_bytes())
    report_path = output / "validation.json"
    previous = read_json(report_path) if report_path.exists() else {}
    if previous and previous["selection_sha256"] != selection_hash:
        raise ValueError("Cannot resume validation with a different selection")
    report = {
        "selection_sha256": selection_hash,
        "purpose": "endpoint_validation_not_evaluation",
        "timezone_conclusion": "unverified",
        "unstar_conclusion": "unresolved",
        "selected_repositories": [r["repo_name"] for r in entries],
        "failures": previous.get("failures", []),
        "repositories": [],
    }

    def record_failure(name, attempt, reason):
        failure = {"repo_name": name, "capture": str(attempt.relative_to(output)), "reason": reason}
        if failure not in report["failures"]:
            report["failures"].append(failure)

    for entry in entries:
        name = entry["repo_name"]
        repo_dir = output / name.replace("/", "__")
        attempts = sorted(repo_dir.glob("attempt_*")) if repo_dir.exists() else []
        capture, chosen = None, None
        for attempt in attempts[::-1]:
            saved = (
                read_json(attempt / "capture.json") if (attempt / "capture.json").exists() else {}
            )
            if saved.get("complete"):
                try:
                    candidate, _ = read_capture(attempt)
                except HistoryError as error:
                    record_failure(name, attempt, str(error))
                else:
                    if capture is None:
                        capture, chosen = candidate, attempt
            else:
                record_failure(name, attempt, saved.get("error") or "interrupted_capture")
        if capture is None:
            chosen = repo_dir / f"attempt_{len(attempts) + 1:03d}"
            try:
                capture = client.fetch(
                    name, chosen, observation_end="2026-08-31", created_before="2023-01-01"
                )
            except HistoryError as error:
                record_failure(name, chosen, str(error))
                report["repositories"].append(
                    {
                        "repo_name": name,
                        "status": "failed",
                        "reason": str(error),
                        "capture": str(chosen.relative_to(output)),
                    }
                )
                _save_report(report_path, report)
                continue
        report["repositories"].append(
            {
                "repo_name": name,
                "status": "complete",
                "capture": str(chosen.relative_to(output)),
                "repo_id": capture["repo_id"],
                "created_at": capture["created_at"],
                "week_utc_seconds": capture["week_utc_seconds"],
                "week_utc_weekdays": capture["week_utc_weekdays"],
                "missing_days": capture["nominal_missing_days"],
                "duplicate_days": capture["nominal_duplicate_days"],
            }
        )
        _save_report(report_path, report)
    validation_status_counts(report)
    return report


def compare_validation(validation_dir, archive_csv, output_dir):
    """Archive export must contain all 366 days per successful repository, including zeros."""
    base = Path(validation_dir)
    report = read_json(base / "validation.json")
    counts = validation_status_counts(report)
    complete = [r for r in report["repositories"] if r["status"] == "complete"]
    if not complete:
        raise ValueError("No complete validation captures are available for comparison")
    archive = pd.read_csv(archive_csv)
    required = {"repo_id", "event_date", "watch_events"}
    if not required.issubset(archive) or archive[list(required)].isna().any().any():
        raise ValueError("Archive comparison requires repo_id, event_date and watch_events")
    archive["event_date"] = pd.to_datetime(archive.event_date, errors="raise").dt.strftime(
        "%Y-%m-%d"
    )
    values = archive.watch_events
    if (
        (values < 0).any()
        or (values % 1 != 0).any()
        or archive.duplicated(["repo_id", "event_date"]).any()
    ):
        raise ValueError("Invalid or duplicate archive daily counts")
    days = pd.date_range("2024-01-01", "2024-12-31").strftime("%Y-%m-%d")
    complete_ids = {r["repo_id"] for r in complete}
    excluded_ids = set(archive.repo_id) - complete_ids
    archive = archive[archive.repo_id.isin(complete_ids)]
    expected = {(r["repo_id"], day) for r in complete for day in days}
    if set(archive[["repo_id", "event_date"]].itertuples(index=False, name=None)) != expected:
        raise ValueError("Archive export must cover the complete repository/2024-day grid")
    frames = []
    for entry in complete:
        _, daily = read_capture(base / entry["capture"])
        selected = daily[daily.nominal_date.isin(days)].rename(
            columns={"nominal_date": "event_date"}
        )
        if len(selected) != len(days) or selected.event_date.duplicated().any():
            raise ValueError("Endpoint nominal day mapping is incomplete; resolve timezone first")
        frames.append(selected[["repo_id", "repo_name", "event_date", "stars"]])
    paired = pd.concat(frames).merge(
        archive[list(required)], on=["repo_id", "event_date"], validate="one_to_one"
    )
    paired["difference"] = paired.stars - paired.watch_events
    paired["absolute_difference"] = paired.difference.abs()
    paired["equal"] = paired.difference.eq(0)
    summary = paired.groupby(["repo_id", "repo_name"], as_index=False).agg(
        api_total=("stars", "sum"),
        archive_total=("watch_events", "sum"),
        mean_absolute_difference=("absolute_difference", "mean"),
        fraction_equal=("equal", "mean"),
    )
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)
    paired.to_csv(output / "daily_comparison.csv", index=False)
    summary.to_csv(output / "repository_comparison.csv", index=False)
    atomic_json(
        output / "comparison.json",
        {
            "archive_sha256": sha256_bytes(Path(archive_csv).read_bytes()),
            "validation_sha256": sha256_bytes((base / "validation.json").read_bytes()),
            "alignment": "API nominal versus archive UTC dates; equivalence is unverified",
            "unstar_conclusion": "Differences may reflect unstars, archive misses or revisions",
            "n_rows": len(paired),
            **counts,
            "compared_repo_ids": sorted(complete_ids),
            "failures": report["failures"],
            "n_archive_repositories_excluded": len(excluded_ids),
        },
    )
    return summary

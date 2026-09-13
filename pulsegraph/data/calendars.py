"""Explicit calendar hypotheses for hourly validation and nominal endpoint bins."""

from datetime import timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

CALENDAR_HYPOTHESES = ("UTC", "America/Los_Angeles", "UTC-08:00")


def calendar_timezone(name):
    if name not in CALENDAR_HYPOTHESES:
        raise ValueError("Unknown calendar hypothesis")
    return timezone(timedelta(hours=-8)) if name == "UTC-08:00" else ZoneInfo(name)


def creation_day(created_at, calendar):
    instant = pd.Timestamp(created_at)
    if instant.tzinfo is None:
        raise ValueError("Repository creation must have an explicit timezone")
    return instant.tz_convert(calendar_timezone(calendar)).date().isoformat()


def bin_archive_hours(archive, repo_ids):
    """Require the complete UTC-year grid; expose partial local days instead of imputing."""
    required = {"repo_id", "hour_start", "watch_events"}
    if not required.issubset(archive) or archive[list(required)].isna().any().any():
        raise ValueError("Archive comparison requires repo_id, hour_start and watch_events")
    archive = archive[list(required)].copy()
    values = archive.watch_events
    if not np.isfinite(values).all() or (values < 0).any() or (values % 1 != 0).any():
        raise ValueError("Invalid archive hourly counts")
    archive["hour_start"] = pd.to_datetime(archive.hour_start, utc=True, errors="raise")
    if (
        not archive.hour_start.eq(archive.hour_start.dt.floor("h")).all()
        or archive.duplicated(["repo_id", "hour_start"]).any()
    ):
        raise ValueError("Invalid or duplicate repository-hour rows")
    excluded_ids = sorted(set(archive.repo_id) - set(repo_ids))
    archive = archive[archive.repo_id.isin(repo_ids)].sort_values(["repo_id", "hour_start"])
    hours = pd.date_range("2024-01-01", "2025-01-01", freq="h", inclusive="left", tz="UTC")
    if set(archive.repo_id) != set(repo_ids) or any(
        not pd.DatetimeIndex(group.hour_start).equals(hours)
        for _, group in archive.groupby("repo_id")
    ):
        raise ValueError("Archive export must cover the complete repository/2024-hour grid")
    days = pd.date_range("2024-01-01", "2024-12-31")
    frames = []
    for hypothesis in CALENDAR_HYPOTHESES:
        zone = calendar_timezone(hypothesis)
        local = archive.assign(
            event_date=archive.hour_start.dt.tz_convert(zone).dt.strftime("%Y-%m-%d")
        )
        grouped = local.groupby(["repo_id", "event_date"], as_index=False).agg(
            observed_watch_events=("watch_events", "sum"), observed_hours=("watch_events", "size")
        )
        boundaries = pd.date_range("2024-01-01", "2025-01-01", tz=zone)
        expected_hours = np.diff(boundaries.tz_convert("UTC").as_unit("s").asi8) // 3600
        grid = pd.MultiIndex.from_product(
            [sorted(repo_ids), days.strftime("%Y-%m-%d")], names=["repo_id", "event_date"]
        ).to_frame(index=False)
        grid["expected_hours"] = np.tile(expected_hours, len(repo_ids))
        grid = grid.merge(grouped, on=["repo_id", "event_date"], how="left", validate="one_to_one")
        grid["complete_archive_day"] = grid.observed_hours.eq(grid.expected_hours)
        grid["watch_events"] = grid.observed_watch_events.where(grid.complete_archive_day)
        grid["hypothesis"] = hypothesis
        # Same complete nominal dates for all three comparisons, declared before extraction.
        grid["scored"] = grid.event_date.le("2024-12-30") & grid.complete_archive_day
        frames.append(grid)
    return pd.concat(frames, ignore_index=True), excluded_ids

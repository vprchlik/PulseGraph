import numpy as np
import pandas as pd
import pytest

from pulsegraph.data.calendars import bin_archive_hours, creation_day


def hourly():
    return pd.DataFrame(
        {
            "repo_id": 1,
            "hour_start": pd.date_range(
                "2024-01-01", "2025-01-01", freq="h", inclusive="left", tz="UTC"
            ),
            "watch_events": 0,
        }
    )


def test_dst_binning_repeated_hour_and_partial_year_boundary():
    frame = hourly()
    for date, count in (
        ("2024-03-10T09:00Z", 1),
        ("2024-03-10T10:00Z", 2),
        ("2024-03-11T07:00Z", 5),
        ("2024-11-03T08:00Z", 4),
        ("2024-11-03T09:00Z", 8),
    ):
        frame.loc[frame.hour_start.eq(pd.Timestamp(date)), "watch_events"] = count
    bins, excluded = bin_archive_hours(frame, {1})
    assert excluded == [] and len(bins) == 366 * 3
    indexed = bins.set_index(["hypothesis", "event_date"])
    spring = indexed.loc[("America/Los_Angeles", "2024-03-10")]
    fall = indexed.loc[("America/Los_Angeles", "2024-11-03")]
    assert spring.expected_hours == spring.observed_hours == 23
    assert fall.expected_hours == fall.observed_hours == 25
    assert spring.watch_events == 3 and fall.watch_events == 12
    assert indexed.loc[("America/Los_Angeles", "2024-03-11"), "watch_events"] == 5
    assert indexed.loc[("UTC-08:00", "2024-03-10"), "watch_events"] == 8
    for hypothesis in ("America/Los_Angeles", "UTC-08:00"):
        end = indexed.loc[(hypothesis, "2024-12-31")]
        assert end.observed_hours == 16 and end.expected_hours == 24
        assert not end.scored and not end.complete_archive_day
        assert np.isnan(end.watch_events)
    assert indexed.loc[("UTC", "2024-12-31"), "complete_archive_day"]
    assert bins.groupby("hypothesis").scored.sum().tolist() == [365] * 3


@pytest.mark.parametrize(
    "bad", ["missing", "duplicate", "negative", "fraction", "infinite", "subhour"]
)
def test_hour_grid_corruption_rejected(bad):
    frame = hourly()
    if bad == "missing":
        frame = frame.iloc[1:]
    elif bad == "duplicate":
        frame = pd.concat([frame, frame.iloc[:1]])
    elif bad == "subhour":
        frame.loc[0, "hour_start"] += pd.Timedelta(minutes=1)
    else:
        frame["watch_events"] = frame.watch_events.astype(float)
        frame.loc[0, "watch_events"] = {"negative": -1, "fraction": 0.5, "infinite": np.inf}[bad]
    with pytest.raises(ValueError):
        bin_archive_hours(frame, {1})


def test_creation_calendar_distinguishes_dst_and_fixed_offset():
    instant = "2024-07-02T07:30:00Z"
    assert creation_day(instant, "UTC") == "2024-07-02"
    assert creation_day(instant, "America/Los_Angeles") == "2024-07-02"
    assert creation_day(instant, "UTC-08:00") == "2024-07-01"
    with pytest.raises(ValueError):
        creation_day("2024-07-02", "UTC")

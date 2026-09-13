import re
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from pulsegraph.data.bigquery_dry_run import dry_run_queries
from pulsegraph.data.frame import freeze_frame_order, walk_frame
from pulsegraph.data.star_history import HistoryError


def test_dry_run_never_fetches_results_or_submits_billable_job():
    jobs = []

    class Client:
        def query(self, sql, *, job_config, location):
            assert job_config.dry_run is True
            assert not job_config.use_query_cache and not job_config.use_legacy_sql
            assert location == "US"
            jobs.append((sql, job_config))
            return SimpleNamespace(total_bytes_processed=2**40, job_id=f"dry-{len(jobs)}")

    report = dry_run_queries(
        Client(), query_config_factory=SimpleNamespace, array_parameter_factory=lambda *args: args
    )
    assert len(jobs) == 2
    assert report["estimated_usd"] == 12.50
    assert not report["billable_execution_authorized"]
    assert len(jobs[0][1].query_parameters[0][2]) == 20
    assert report["proposed_total_billing_cap_bytes"] > 2 * 2**40


def test_sql_declares_date_bounds_without_watch_action_scan():
    study = Path(__file__).resolve().parents[1] / "study"
    frame = (study / "frame.sql").read_text()
    assert "DATE '2025-02-21'" in frame and "DATE '2025-05-21'" in frame
    star_section = frame.split("), stars AS (")[1]
    assert "payload" not in star_section
    assert "type = 'WatchEvent'" in star_section
    assert "INTERVAL 89 DAY" in frame
    validation = (study / "validation_2024.sql").read_text()
    assert "GENERATE_TIMESTAMP_ARRAY" in validation and "COALESCE" in validation
    assert "JSON_VALUE" not in validation

    def table_days(section):
        assert "`githubarchive.day.*`" not in section  # Also matches day.yesterday view.
        spans = re.findall(
            r"`githubarchive.day.(\d{4})\*`\s+WHERE _TABLE_SUFFIX BETWEEN '(\d{4})' AND '(\d{4})'",
            section,
        )
        return [
            day for year, first, last in spans for day in pd.date_range(year + first, year + last)
        ]

    assert table_days(frame.split("), stars AS (")[0]) == list(
        pd.date_range("2023-01-01", "2025-02-21")
    )
    assert table_days(star_section) == list(pd.date_range("2023-01-01", "2025-05-21"))
    assert table_days(validation) == list(pd.date_range("2024-01-01", "2024-12-31")) * 2


def test_seeded_frame_walk_records_all_skips_and_never_reorders():
    frame = pd.DataFrame(
        {
            "repo_id": range(9),
            "repo_name": [f"a/r{i}" for i in range(9)],
            "creation_date": "2024-01-01",
            "day90_stars": [20] * 3 + [100] * 3 + [1000] * 3,
        }
    )
    ordered = freeze_frame_order(frame)
    pd.testing.assert_frame_equal(ordered, freeze_frame_order(frame.sample(frac=1, random_state=1)))
    observed = []

    def retrieve(row):
        observed.append(row["repo_id"])
        if row["selection_rank"] == 1:
            raise HistoryError("http_404")
        return {"repo_id": row["repo_id"], "repo_name": row["repo_name"], "complete": True}

    result = walk_frame(ordered, retrieve, per_stratum=1)
    assert len(result["accepted"]) == 3 and len(result["skipped"]) == 3
    assert all(r["skip_count"] == 1 for r in result["strata"])
    assert observed == ordered[ordered.selection_rank.le(2)].repo_id.tolist()
    with pytest.raises(ValueError):
        freeze_frame_order(frame.assign(creation_date="2025-02-22"))


def test_day90_eligibility_ignores_action_and_future_perturbations():
    from pulsegraph.data.frame import day90_watch_counts

    events = pd.DataFrame(
        {
            "repo_id": [1] * 150,
            "id": range(150),
            "created_at": pd.date_range("2023-01-01", periods=150),
            "type": ["WatchEvent"] * 150,
            "action": ["arbitrary-fixture"] * 150,
        }
    )
    baseline = day90_watch_counts(events, repo_id=1, creation="2023-01-01")
    changed = events.copy()
    changed.loc[90:, "type"] = "CreateEvent"
    extended = pd.concat(
        [
            changed,
            events.iloc[:10],
            pd.DataFrame(
                {
                    "repo_id": [1],
                    "id": [999],
                    "created_at": [pd.Timestamp("2026-01-01")],
                    "type": ["WatchEvent"],
                    "action": ["started"],
                }
            ),
        ]
    )
    assert baseline == 90
    assert (
        day90_watch_counts(
            extended.sample(frac=1, random_state=123), repo_id=1, creation="2023-01-01"
        )
        == baseline
    )

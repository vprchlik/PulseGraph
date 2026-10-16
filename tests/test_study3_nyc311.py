"""NYC 311 for Study 3: the resumable per-day census over a fake Socrata endpoint; no network."""

import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
import requests

from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json
from pulsegraph.study2 import ingestion
from pulsegraph.study2.constants import CONTEXT_END, CONTEXT_START, STRATA_START, STUDY3_SEEDS
from pulsegraph.study2.ingestion import (
    TARGET_END,
    TARGET_START,
    CaptureClient,
    NYCSource,
    RequestBudget,
    SourceFailure,
    build_panel,
    hash_key,
)

DAY = re.compile(
    r"created_date between '(\d{4}-\d{2}-\d{2})T00:00:00\.000'"
    r" and '(\d{4}-\d{2}-\d{2})T23:59:59\.999'"
)
CONTEXT_DAYS = [d.date().isoformat() for d in pd.date_range(CONTEXT_START, CONTEXT_END)]
TARGET_DAYS = [d.date().isoformat() for d in pd.date_range(TARGET_START, TARGET_END)]
# Frame cells by the share of days with a request; the last very sparse cell never has one.
CELLS = {
    ("Noise - Residential", "01 BRONX"): 1.0,
    ("Noise - Residential", "12 MANHATTAN"): 0.9,
    ("Illegal Parking", "05 BROOKLYN"): 0.8,
    ("Heat/Hot Water", "03 STATEN ISLAND"): 0.7,
    ("Graffiti", "14 QUEENS"): 0.3,
    ("Graffiti", "02 BRONX"): 0.25,
    ("Dead Animal", "18 BROOKLYN"): 0.2,
    ("Dead Animal", "07 QUEENS"): 0.15,
    ("Abandoned Bike", "01 BROOKLYN"): 0.04,
    ("Abandoned Bike", "11 MANHATTAN"): 0.02,
    ("Squeegee", "09 QUEENS"): 0.0,
}
UNRECOGNIZED = [("Noise - Residential", "Unspecified QUEENS"), ("Noise - Residential", "")]
OUTSIDE = [("New Problem", "02 BRONX")]


def series_id(problem, board):
    return json.dumps([problem, board], ensure_ascii=False, separators=(",", ":"))


def fixture_data(days, seed=5, start_key=40000000):
    """Requests by creation day; the first cell has at least one request every day."""
    rng = np.random.default_rng(seed)
    data, key = {}, start_key
    for day in days:
        rows = []
        for (problem, board), share in [
            *CELLS.items(),
            *((c, 0.3) for c in UNRECOGNIZED + OUTSIDE),
        ]:
            n = int(rng.poisson(2.0)) if rng.random() < share else 0
            if (problem, board) == next(iter(CELLS)):
                n = max(n, 1)
            for _ in range(n):
                key += 1
                second = int(rng.integers(0, 86400))
                row = dict(
                    unique_key=str(key),
                    created_date=f"{day}T{second // 3600:02}:{second // 60 % 60:02}:"
                    f"{second % 60:02}.000",
                    complaint_type=problem,
                )
                if board:
                    row["community_board"] = board
                rows.append(row)
        data[day] = rows
    return data


def inventory_document(path):
    entries = [
        dict(
            series_id=series_id(*cell),
            problem=cell[0],
            board=cell[1],
            frame_year=2024,
            frame_count=10,
            excluded_reason=None,
        )
        for cell in CELLS
    ]
    entries.append(
        dict(
            series_id=series_id(*UNRECOGNIZED[0]),
            problem=UNRECOGNIZED[0][0],
            board=UNRECOGNIZED[0][1],
            frame_year=2024,
            frame_count=3,
            excluded_reason="unspecified_geography_or_problem",
        )
    )
    atomic_json(
        path,
        dict(
            domain="nyc311",
            acquired_at="2026-09-14T17:08:16+00:00",
            complete=True,
            source_evidence=[dict(path="inventory-capture", sha256="0" * 64)],
            entries=entries,
            frame_kind="current_public_inventory",
        ),
    )
    return path


class Socrata:
    """The erm2-nwe9 resource over fixture requests; a day named in `faults` fails that way."""

    def __init__(self, data, faults=None):
        self.data, self.faults, self.headers, self.calls = data, dict(faults or {}), {}, []

    def get(self, url, params=None, timeout=None, allow_redirects=None):
        assert url == NYCSource.URL and allow_redirects is False
        self.calls.append(dict(params))
        match = DAY.fullmatch(params["$where"])
        assert match and match[1] == match[2], params["$where"]
        day, fault = match[1], self.faults.get(match[1])
        if fault == "transport_failure":
            raise requests.ConnectionError("connection reset by peer")
        if fault in ("http_503", "http_500"):
            return SimpleNamespace(
                status_code=int(fault[5:]), content=b"", headers={"Retry-After": "0"}
            )
        if fault == "http_400":
            return SimpleNamespace(status_code=400, content=b"{}", headers={})
        assert params["$order"] == "unique_key" and params["$select"] == ingestion.NYC_FIELDS
        rows = sorted(self.data.get(day, []), key=lambda r: r["unique_key"])
        offset, limit = int(params["$offset"]), int(params["$limit"])
        body = json.dumps(rows[offset : offset + limit]).encode()
        return SimpleNamespace(status_code=200, content=body, headers={})

    def days(self):
        return [DAY.fullmatch(call["$where"])[1] for call in self.calls]


@pytest.fixture(autouse=True)
def clock(monkeypatch):
    """A clock that ticks one second per reading, from 2026-10-16 00:00 UTC."""
    state = dict(now=datetime(2026, 10, 16, tzinfo=timezone.utc))

    def now():
        state["now"] += timedelta(seconds=1)
        return state["now"]

    monkeypatch.setattr(ingestion, "utc_now", now)
    return state


def client_for(tmp_path, session, folder="captures", **limits):
    return CaptureClient(
        tmp_path / folder, session=session, sleep=lambda seconds: None, root=tmp_path, **limits
    )


def expected_counts(data, days):
    """Per-cell daily counts straight from the fixture, every identifier once."""
    counts = Counter()
    for day in days:
        for row in data.get(day, []):
            counts[(row["complaint_type"], row.get("community_board", ""), day)] += 1
    return counts


@pytest.fixture
def context_data():
    return fixture_data(CONTEXT_DAYS)


def build(tmp_path, data, *, faults=None, folder="captures", out="panel", **limits):
    session = Socrata(data, faults)
    source = NYCSource(client_for(tmp_path, session, folder, **limits))
    inventory = tmp_path / "inventory.json"
    if not inventory.exists():
        inventory_document(inventory)
    manifest = build_panel(
        inventory, source.context, tmp_path / out, seed=STUDY3_SEEDS["selection"]
    )
    return manifest, session, source


def test_the_census_counts_requests_by_local_day_from_one_query_per_day(tmp_path, context_data):
    manifest, session, _ = build(tmp_path, context_data)
    assert session.days() == CONTEXT_DAYS
    assert all(call["$limit"] == 50000 and call["$offset"] == 0 for call in session.calls)
    named = set(re.findall(r"\d{4}-\d{2}-\d{2}", json.dumps(session.calls)))
    assert max(named) == CONTEXT_END < TARGET_START
    census = read_json(tmp_path / "panel" / "census.json")
    assert manifest["census_sha256"] == file_hash(tmp_path / "panel" / "census.json")
    counts = expected_counts(context_data, CONTEXT_DAYS)
    context = pd.read_parquet(tmp_path / "panel" / "context.parquet")
    for row in manifest["series"]:
        mine = context[context.series_id.eq(row["series_id"])].set_index("date")["count"]
        assert len(mine) == 275
        assert mine.tolist() == [counts[(row["problem"], row["board"], d)] for d in CONTEXT_DAYS]
    frame_cells = set(CELLS)
    for day, entry in zip(CONTEXT_DAYS, census["per_day"], strict=True):
        rows = context_data[day]
        cells = [(r["complaint_type"], r.get("community_board", "")) for r in rows]
        assert entry["day"] == day and entry["requests"] == entry["captured_rows"] == len(rows)
        assert entry["frame_requests"] == sum(cell in frame_cells for cell in cells)
        assert entry["unrecognized_requests"] == sum(cell in UNRECOGNIZED for cell in cells)
        assert entry["outside_frame_requests"] == sum(cell in OUTSIDE for cell in cells)
        assert entry["pages"] == 1 and entry["superseded_rows"] == 0
    assert census["gap_days"] == [] and census["frame_cells"] == len(CELLS)
    assert census["calendar"] == "America/New_York" and census["days"] == 275
    assert len(census["response_evidence"]) == 275
    assert manifest["report"]["census"]["requests"] == census["requests"]
    ledger = read_json(tmp_path / "panel" / "census_ledger.json")
    assert ledger["complete"] is True and ledger["failures"] == []
    assert [i["status"] for i in ledger["invocations"]] == ["complete"]
    assert ledger["invocations"][0]["attempts"] == 275


def test_the_panel_is_the_whole_frame_selected_with_study3s_seed(tmp_path, context_data):
    manifest, _, _ = build(tmp_path, context_data)
    report = manifest["report"]
    assert report["selection_seed"] == STUDY3_SEEDS["selection"] == 20261001
    assert report["eligible_frame_size"] == report["candidate_pool_size"] == len(CELLS)
    assert [s["reason"] for s in report["skipped"]] == ["unspecified_geography_or_problem"]
    counts = expected_counts(context_data, CONTEXT_DAYS)
    late = [d for d in CONTEXT_DAYS if d >= STRATA_START]
    strata = {}
    for problem, board in CELLS:
        z = np.mean([counts[(problem, board, d)] == 0 for d in late])
        strata[series_id(problem, board)] = (
            "dense" if z < 0.5 else "sparse" if z < 0.9 else "very_sparse"
        )
    assert {r["series_id"]: r["stratum"] for r in manifest["series"]} == strata
    assert set(strata.values()) == {"dense", "sparse", "very_sparse"}
    for row in manifest["series"]:
        assert row["selection_hash"] == hash_key("nyc311", "selection", row["series_id"], 20261001)
        assert row["selection_hash"] != hash_key("nyc311", "selection", row["series_id"])
    for stratum in set(strata.values()):
        mine = [r for r in manifest["series"] if r["stratum"] == stratum]
        assert mine == sorted(mine, key=lambda r: (r["selection_hash"], r["series_id"].encode()))
    assert report["target_values_opened"] is False


def test_paging_past_the_page_size_counts_the_same_requests(tmp_path, context_data, monkeypatch):
    reference, _, _ = build(tmp_path, context_data, folder="whole", out="whole-panel")
    monkeypatch.setattr(ingestion, "NYC_PAGE", 5)
    data = dict(context_data)
    exact = CONTEXT_DAYS[10]
    data[exact] = sorted(data[exact], key=lambda r: r["unique_key"])[:5]
    manifest, session, _ = build(
        tmp_path, data, folder="paged", out="paged-panel", max_requests=5000
    )
    days = Counter(session.days())
    assert days[exact] == 2  # five rows, then the empty page that exhausts the day
    for day in CONTEXT_DAYS:
        assert days[day] == len(data[day]) // 5 + 1
    offsets = [c["$offset"] for c in session.calls if DAY.fullmatch(c["$where"])[1] == exact]
    assert offsets == [0, 5]
    census = read_json(tmp_path / "paged-panel" / "census.json")
    assert sum(e["pages"] for e in census["per_day"]) == len(session.calls)
    whole = pd.read_parquet(tmp_path / "whole-panel" / "context.parquet")
    paged = pd.read_parquet(tmp_path / "paged-panel" / "context.parquet")
    changed = {
        series_id(r["complaint_type"], r.get("community_board", "")) for r in context_data[exact]
    }
    keep = ~whole.series_id.isin(changed) | whole.date.ne(pd.Timestamp(exact))
    assert paged[keep].reset_index(drop=True).equals(whole[keep].reset_index(drop=True))
    assert manifest["report"]["selection_seed"] == reference["report"]["selection_seed"]


@pytest.mark.parametrize("fault", ["transport_failure", "http_503", "http_500"])
def test_a_failure_mid_pull_stops_with_nothing_partial_and_resumes_from_captures(
    tmp_path, context_data, fault
):
    failed = CONTEXT_DAYS[100]
    reason = "transport_failure" if fault == "transport_failure" else "retry_exhausted"
    with pytest.raises(SourceFailure, match=reason):
        build(tmp_path, context_data, faults={failed: fault})
    panel = tmp_path / "panel"
    assert sorted(p.name for p in panel.iterdir()) == ["census_ledger.json"]
    ledger = read_json(panel / "census_ledger.json")
    assert ledger["complete"] is False
    stop = dict(ledger["failures"][0])
    stop.pop("at")
    assert stop == dict(day=failed, reason=reason, kind="outage")
    assert ledger["invocations"][0]["days_exhausted"] == 100
    assert ledger["invocations"][0]["attempts"] == 100 + (1 if fault == "transport_failure" else 3)
    if fault == "transport_failure":
        record = [read_json(p) for p in (tmp_path / "captures").glob("*.failure.json")]
        assert [r["transport"] for r in record] == ["ConnectionError"]
    # The resume requests only the failed day and the days after it.
    manifest, session, _ = build(tmp_path, context_data)
    assert session.days() == CONTEXT_DAYS[100:]
    ledger = read_json(panel / "census_ledger.json")
    assert [i["status"] for i in ledger["invocations"]] == ["SourceFailure", "complete"]
    assert ledger["complete"] is True and len(ledger["failures"]) == 1
    reference, _, _ = build(tmp_path, context_data, folder="uninterrupted", out="reference")
    assert manifest["series"] == reference["series"]
    assert manifest["report"] == reference["report"]
    assert pd.read_parquet(panel / "context.parquet").equals(
        pd.read_parquet(tmp_path / "reference" / "context.parquet")
    )
    census, again = (read_json(p / "census.json") for p in (panel, tmp_path / "reference"))
    assert census["per_day"] == again["per_day"]


def test_a_budget_stop_writes_only_the_ledger_and_resumes(tmp_path, context_data):
    with pytest.raises(RequestBudget, match="acquisition_budget_reached"):
        build(tmp_path, context_data, max_requests=40)
    panel = tmp_path / "panel"
    assert sorted(p.name for p in panel.iterdir()) == ["census_ledger.json"]
    ledger = read_json(panel / "census_ledger.json")
    assert (
        ledger["failures"][0]["kind"] == "budget"
        and ledger["failures"][0]["day"] == CONTEXT_DAYS[40]
    )
    with pytest.raises(RequestBudget):
        build(tmp_path, context_data, max_requests=100)
    assert read_json(panel / "census_ledger.json")["invocations"][1]["days_exhausted"] == 140
    manifest, session, _ = build(tmp_path, context_data)
    assert session.days() == CONTEXT_DAYS[140:]
    assert len(manifest["series"]) == len(CELLS)


def test_a_day_without_a_frame_request_is_a_source_gap_that_stops_the_domain(
    tmp_path, context_data
):
    gap = CONTEXT_DAYS[200]
    data = dict(context_data)
    # Only a request outside the frame that day: the source answered, the frame did not.
    data[gap] = [
        dict(unique_key="99999999", created_date=f"{gap}T08:00:00.000", complaint_type="Noise")
    ]
    with pytest.raises(SourceFailure, match="source_gap_day"):
        build(tmp_path, data)
    panel = tmp_path / "panel"
    assert sorted(p.name for p in panel.iterdir()) == ["census_ledger.json"]
    ledger = read_json(panel / "census_ledger.json")
    assert ledger["gap_days"] == [gap] and ledger["failures"][0]["kind"] == "source_gap"
    # Restoring the same snapshot stops again, without a request.
    with pytest.raises(SourceFailure, match="source_gap_day"):
        build(tmp_path, data)
    second = read_json(panel / "census_ledger.json")["invocations"][1]
    assert second["status"] == "source_gap" and second["attempts"] == 0


def test_an_identifier_keeps_its_latest_captured_revision(tmp_path, context_data):
    data = {day: [dict(r) for r in rows] for day, rows in context_data.items()}
    early, late = CONTEXT_DAYS[30], CONTEXT_DAYS[31]
    moved = dict(data[early][0])
    # The request was captured on the earlier day, then again, revised, on the later one.
    data[late].append(
        dict(
            moved,
            created_date=f"{late}T09:00:00.000",
            complaint_type="Graffiti",
            community_board="14 QUEENS",
        )
    )
    build(tmp_path, data)
    census = read_json(tmp_path / "panel" / "census.json")
    assert census["superseded_rows"] == 1 and census["captured_rows"] == census["requests"] + 1
    entry = census["per_day"][30]
    assert entry["superseded_rows"] == 1 and entry["requests"] == len(data[early]) - 1
    context = pd.read_parquet(tmp_path / "panel" / "context.parquet").set_index(
        ["series_id", "date"]
    )
    counts = expected_counts(context_data, CONTEXT_DAYS)
    cell = (moved["complaint_type"], moved.get("community_board", ""))
    if cell in CELLS:
        assert (
            context.loc[(series_id(*cell), pd.Timestamp(early)), "count"]
            == counts[(*cell, early)] - 1
        )
    graffiti = series_id("Graffiti", "14 QUEENS")
    assert (
        context.loc[(graffiti, pd.Timestamp(late)), "count"]
        == counts[("Graffiti", "14 QUEENS", late)] + 1
    )


@pytest.mark.parametrize(
    "change,reason",
    [
        ("duplicate", "duplicate_request_identifier"),
        ("outside", "request_outside_its_day"),
        ("unidentified", "request_identifier_missing"),
    ],
)
def test_a_capture_that_breaks_the_source_contract_stops_the_domain(
    tmp_path, context_data, change, reason
):
    data = {day: [dict(r) for r in rows] for day, rows in context_data.items()}
    day = CONTEXT_DAYS[50]
    if change == "duplicate":
        data[day].append(dict(data[day][0]))
    elif change == "outside":
        data[day][0]["created_date"] = f"{CONTEXT_DAYS[51]}T00:00:00.000"
    else:
        data[day][0].pop("unique_key")
        data[day][0]["unique_key"] = ""
    with pytest.raises(SourceFailure, match=reason):
        build(tmp_path, data)
    ledger = read_json(tmp_path / "panel" / "census_ledger.json")
    assert ledger["failures"][0] | dict(at=None) == dict(
        at=None, day=day, reason=reason, kind="source"
    )
    assert not (tmp_path / "panel" / "manifest.json").exists()


def test_no_request_names_a_target_day_before_the_gate(tmp_path, context_data):
    session = Socrata(fixture_data(TARGET_DAYS))
    source = NYCSource(client_for(tmp_path, session))
    frame = [dict(series_id=series_id(*c), problem=c[0], board=c[1]) for c in CELLS]
    with pytest.raises(ValueError, match="2026-06-03"):
        source.census(TARGET_START, TARGET_END, frame)
    with pytest.raises(ValueError, match="2026-06-03"):
        source.day("2026-06-03")
    with pytest.raises(ValueError, match="2026-06-03"):
        source._get({"$where": "created_date < '2026-06-03T00:00:00'"})
    with pytest.raises(ValueError, match="target days"):
        source.context(frame[0], CONTEXT_START, "2026-06-03")
    with pytest.raises(ValueError, match="after the gate"):
        source.targets(frame[0], TARGET_START, TARGET_END)
    with pytest.raises(ValueError, match="census"):
        source.context(frame[0], CONTEXT_START, CONTEXT_END)
    assert session.calls == []
    # Even with the gate open, the target window is exactly the registered one.
    source.targets_open, source.target_series = True, frozenset([frame[0]["series_id"]])
    for start, end in ((CONTEXT_START, TARGET_END), (TARGET_START, "2026-09-01")):
        with pytest.raises(ValueError, match="exactly 2026-06-03 to 2026-08-31"):
            source.targets(frame[0], start, end)


def test_the_census_ledger_refuses_another_window_or_frame(tmp_path, context_data):
    with pytest.raises(SourceFailure):
        build(tmp_path, context_data, faults={CONTEXT_DAYS[3]: "transport_failure"})
    session = Socrata(context_data)
    source = NYCSource(client_for(tmp_path, session))
    frame = [dict(series_id=series_id(*c), problem=c[0], board=c[1]) for c in list(CELLS)[:3]]
    with pytest.raises(ValueError, match="another window or frame"):
        source.census(
            CONTEXT_START, CONTEXT_END, frame, ledger=tmp_path / "panel" / "census_ledger.json"
        )
    assert session.calls == []

import bisect
import inspect
import json
import re
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import unquote

import numpy as np
import pandas as pd
import pytest
import requests

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json
from pulsegraph.study2.constants import CONTEXT_END, CONTEXT_START, STRATA_START
from pulsegraph.study2.ingestion import (
    CANDIDATE_POOL,
    CaptureClient,
    NpmSource,
    RequestBudget,
    SourceFailure,
    build_panel,
    candidate_walk,
    context_days,
    freeze_inventory,
    hash_key,
    walk_ledger_path,
)

REGISTRY = "https://registry.npmjs.org/"
DOWNLOADS = "https://api.npmjs.org/downloads/range/"
OLD, NEW = "2020-01-01T00:00:00.000Z", "2025-10-01T00:00:00.000Z"


def _serve(frame, url, params):
    """The npm feed, packuments and download ranges over a frame of name -> fields or status."""
    if url == NpmSource.ALL_DOCS:
        names = sorted(frame)
        after = json.loads(params["startkey"]) if "startkey" in params else None
        at = 0 if after is None else bisect.bisect_left(names, after)
        rows = [dict(id=n, key=n, value=dict(rev="1-a")) for n in names[at : at + params["limit"]]]
        return 200, dict(total_rows=len(names), offset=at, rows=rows)
    if url.startswith(REGISTRY):
        name = unquote(url[len(REGISTRY) :])
        spec = frame.get(name, dict(status=404))
        if spec.get("status", 200) != 200:
            return spec["status"], dict(error="Not found")
        times = {"created": spec["created"]} if "created" in spec else {}
        return 200, dict(name=spec.get("name", name), _rev="1-a", time=times)
    period, quoted = url[len(DOWNLOADS) :].split("/", 1)
    start, end = period.split(":")
    name, days = unquote(quoted), pd.date_range(start, end)
    late = (days >= STRATA_START).argmax()
    zeros = (0, 45, 81)[len(name) % 3]
    downloads = [
        dict(day=d.date().isoformat(), downloads=0 if late <= i < late + zeros else 1)
        for i, d in enumerate(days)
    ]
    return 200, dict(package=name, start=start, end=end, downloads=downloads)


class FakeClient:
    """Client double that fails as CaptureClient does and counts every request."""

    def __init__(self, frame, budget=None):
        self.frame, self.budget = frame, budget
        self.requests, self.evidence = [], []

    def get(self, url, params=None):
        if self.budget is not None and len(self.requests) >= self.budget:
            raise RequestBudget("acquisition_budget_reached")
        self.requests.append((url, dict(params or {})))
        status, body = _serve(self.frame, url, params or {})
        if status != 200:
            raise SourceFailure(f"http_{status}")
        self.evidence.append(
            dict(sha256=hash_key("npm", "fixture", url), acquired_at="2026-10-13T00:00:00+00:00")
        )
        return body


class FakeSession:
    def __init__(self, frame):
        self.frame, self.headers, self.requests = frame, {}, []

    def get(self, url, params=None, timeout=None, allow_redirects=None):
        self.requests.append((url, dict(params or {})))
        status, body = _serve(self.frame, url, params or {})
        return SimpleNamespace(status_code=status, content=json.dumps(body).encode(), headers={})


class FlakySession(FakeSession):
    """Answers one package's download range with a fault while `fault` is set."""

    def __init__(self, frame, package, fault):
        super().__init__(frame)
        self.package, self.fault = package, fault

    def get(self, url, params=None, timeout=None, allow_redirects=None):
        target = url.startswith(DOWNLOADS) and unquote(url.rsplit("/", 1)[1]) == self.package
        if self.fault is None or not target:
            return super().get(url, params, timeout, allow_redirects)
        self.requests.append((url, dict(params or {})))
        if self.fault == "transport_failure":
            raise requests.ConnectionError("connection reset")
        body = _serve(self.frame, url, {})[1]
        if self.fault == "download_identity_or_bounds_mismatch":
            body = dict(body, package="other")
        elif self.fault == "missing_context_day":
            body = dict(body, downloads=body["downloads"][1:])
        content = b"<html></html>" if self.fault == "invalid_json" else json.dumps(body).encode()
        status = {"retry_exhausted": 503, "http_404": 404, "http_501": 501}
        status.update({f"http_{code}": code for code in (401, 403, 407)})
        return SimpleNamespace(
            status_code=status.get(self.fault, 200), content=content, headers={"Retry-After": "0"}
        )


def _capture_client(tmp_path, session, folder="captures"):
    """The real capture client over a fake session; store and evidence paths under tmp_path."""
    return CaptureClient(
        tmp_path / folder, session=session, sleep=lambda seconds: None, root=tmp_path
    )


def _frame(n):
    frame = {}
    for i in range(n):
        name = f"@s{i % 7}/p{i}" if i % 5 == 0 else f"p{i}"
        if i % 97 == 0:
            frame[name] = dict(status=404)
        elif i % 89 == 0:
            frame[name] = dict(created=OLD, name=name + "-other")
        else:
            frame[name] = dict(created=NEW if i % 10 < 3 else OLD)
    return frame


def _eligible(frame, name):
    spec = frame[name]
    return (
        spec.get("status", 200) == 200
        and spec.get("name", name) == name
        and spec["created"] < "2025-09-01"
    )


def _hash_order(names):
    return sorted(names, key=lambda n: (hash_key("npm", "candidate", n), n.encode()))


def _small_frame():
    frame = {f"p{i}": dict(created=OLD) for i in range(12)}
    frame.update({f"@s/q{i}": dict(created=OLD) for i in range(6)})
    frame.update(
        {
            "_design/app": dict(created=OLD),
            "edge-old": dict(created="2025-08-31T23:59:59.999Z"),
            "edge-new": dict(created="2025-09-01T00:00:00.000Z"),
            "gone": dict(status=404),
            "renamed": dict(created=OLD, name="other"),
            "undated": dict(),
            "naive": dict(created="2020-01-01T00:00:00"),
        }
    )
    return frame


def _walked(tmp_path):
    """A frozen name inventory over the small frame and its complete walk."""
    inventory = tmp_path / "inventory.json"
    source = NpmSource(_capture_client(tmp_path, FakeSession(_small_frame())))
    source.inventory(inventory)
    return inventory, candidate_walk(inventory, source.metadata)["pool"]


def test_hash_encoding_is_registered():
    from hashlib import sha256

    assert (
        hash_key("npm", "selection", "@scope/café")
        == sha256('[20260914,"npm","selection","@scope/café"]'.encode()).hexdigest()
    )


def test_panel_strata_leakage_and_shortage(tmp_path):
    inventory = tmp_path / "inventory.json"
    freeze_inventory(
        "npm",
        [dict(series_id=str(i), created_at="2020-01-01T00:00:00Z") for i in range(6)],
        [{"fixture": True}],
        inventory,
    )
    dates = pd.date_range(CONTEXT_START, "2026-12-31")
    base = {str(i): pd.DataFrame(dict(date=dates, count=np.ones(len(dates)))) for i in range(6)}
    for i in range(6):
        mask = base[str(i)].date.between("2026-03-05", CONTEXT_END)
        values = np.ones(90)
        values[: (0, 45, 81)[i % 3]] = 0
        base[str(i)].loc[mask, "count"] = values
    seen = []

    def fetch(row, start, end):
        seen.append((start, end))
        return base[row["series_id"]].to_dict("records")

    first = build_panel(inventory, fetch, tmp_path / "first")
    for frame in base.values():
        future = frame.date > CONTEXT_END
        frame.loc[future, "count"] = np.nan
        frame.sort_values("date", ascending=False, inplace=True)
    second = build_panel(inventory, fetch, tmp_path / "second")
    assert first["series"] == second["series"]
    assert all(pair == (CONTEXT_START, CONTEXT_END) for pair in seen)
    assert all(
        s["achieved"] == 2 and s["unfilled"] == 98 for s in first["report"]["strata"].values()
    )
    assert first["report"]["target_values_opened"] is False


def test_incomplete_and_budget_are_distinct(tmp_path):
    inventory = tmp_path / "inventory.json"
    freeze_inventory(
        "npm",
        [dict(series_id="a", created_at="2020-01-01T00:00:00Z")],
        [{"fixture": True}],
        inventory,
    )

    def budget(*args):
        raise RequestBudget("stop")

    with pytest.raises(RequestBudget):
        build_panel(inventory, budget, tmp_path / "budget")
    result = build_panel(inventory, lambda *args: [], tmp_path / "missing")
    assert result["report"]["skipped"][0]["reason"] == "missing_context_day"
    with pytest.raises(SourceFailure):
        context_days([{"date": CONTEXT_START, "count": 0}] * 2)


def test_npm_scope_and_bounds():
    class Client:
        def get(self, url):
            # The download API's documented form: "@" as is, the slash percent-encoded.
            assert url == DOWNLOADS + "2025-09-01:2026-06-02/@scope%2Fa"
            assert requests.Request("GET", url).prepare().url == url
            return dict(package="@scope/a", start=CONTEXT_START, end=CONTEXT_END, downloads=[])

    source = NpmSource(Client())
    assert source.context({"series_id": "@scope/a"}, CONTEXT_START, CONTEXT_END) == []
    with pytest.raises(ValueError, match="target"):
        source.context({}, CONTEXT_START, "2026-08-31")


def test_partial_inventory_cannot_select(tmp_path):
    p = tmp_path / "partial.json"
    atomic_json(p, dict(acquired_at="2026-09-14T00:00:00Z", complete=False))
    with pytest.raises(SourceFailure, match="incomplete"):
        build_panel(p, None, tmp_path / "out")


def test_npm_inventory_freezes_names_only_and_retains_scopes(tmp_path):
    client = FakeClient(dict(_frame(2500), **{"_design/app": dict(created=OLD)}))
    result = NpmSource(client).inventory(tmp_path / "inventory.json")
    assert result["names"] == sorted(_frame(2500)) and result["complete"] is True
    assert result["design_documents_excluded"] == 1 and result["pages"] == len(client.requests)
    assert any(name.startswith("@") for name in result["names"])
    assert all(url == NpmSource.ALL_DOCS for url, _ in client.requests)
    assert all("skip" not in p and "include_docs" not in p for _, p in client.requests)
    with pytest.raises(FileExistsError):
        NpmSource(FakeClient({})).inventory(tmp_path / "inventory.json")


def test_inventory_budget_stop_is_never_complete(tmp_path):
    with pytest.raises(RequestBudget):
        NpmSource(FakeClient(_frame(2500), budget=2)).inventory(tmp_path / "inventory.json")
    assert not (tmp_path / "inventory.json").exists()


def test_walk_stops_at_pool_and_equals_full_hash_order_prefix(tmp_path):
    frame = _frame(16000)
    inventory = tmp_path / "inventory.json"
    NpmSource(FakeClient(frame)).inventory(inventory)
    client = FakeClient(frame)
    ledger = candidate_walk(inventory, NpmSource(client).metadata)
    order = _hash_order(frame)
    expected = [name for name in order if _eligible(frame, name)][:CANDIDATE_POOL]
    visited = order.index(expected[-1]) + 1
    assert CANDIDATE_POOL == 10000 and len(expected) == 10000
    assert sum(_eligible(frame, name) for name in frame) > 10000
    assert ledger["complete"] is True and ledger["stop_reason"] == "pool_full"
    assert ledger["pool"] == expected and ledger["eligible"] == 10000
    assert [v["series_id"] for v in ledger["visits"]] == order[:visited]
    assert len(client.requests) == ledger["visited"] == visited < len(frame)
    assert ledger["visited"] == ledger["eligible"] + ledger["ineligible"] + ledger["excluded"]
    assert ledger["frame"]["eligible_frame_size"] is None
    assert ledger["frame"]["candidate_inclusion_probability_estimate"] == pytest.approx(
        visited / len(frame)
    )
    low, high = ledger["frame"]["candidate_inclusion_probability_bounds"]
    assert low <= 10000 / sum(_eligible(frame, n) for n in frame) <= high


def test_budget_stop_never_produces_a_shorter_complete_pool(tmp_path):
    frame = _frame(16000)
    inventory = tmp_path / "inventory.json"
    NpmSource(FakeClient(frame)).inventory(inventory)
    with pytest.raises(RequestBudget):
        candidate_walk(inventory, NpmSource(FakeClient(frame, budget=5000)).metadata)
    partial = read_json(walk_ledger_path(inventory))
    assert partial["complete"] is False and partial["pool"] == [] and partial["visited"] == 5000

    def unreachable(*args):
        raise AssertionError("context requested before a complete pool")

    stopped = NpmSource(FakeClient(frame, budget=10)).metadata
    with pytest.raises(RequestBudget):
        build_panel(inventory, unreachable, tmp_path / "panel", fetch_metadata=stopped)
    assert not (tmp_path / "panel").exists()
    resumed = candidate_walk(inventory, NpmSource(FakeClient(frame)).metadata)
    expected = [name for name in _hash_order(frame) if _eligible(frame, name)][:10000]
    assert resumed["complete"] is True and resumed["pool"] == expected
    idle = FakeClient(frame, budget=0)
    assert candidate_walk(inventory, NpmSource(idle).metadata)["pool"] == expected
    assert idle.requests == []
    ledger = read_json(walk_ledger_path(inventory))
    atomic_json(walk_ledger_path(inventory), dict(ledger, inventory_sha256="0" * 64))
    with pytest.raises(SourceFailure, match="walk_inventory_mismatch"):
        candidate_walk(inventory, NpmSource(idle).metadata)


@pytest.mark.parametrize("reason", ["http_403", "http_429", "transport_failure", "retry_exhausted"])
def test_access_and_transport_failures_interrupt_the_walk(tmp_path, reason):
    inventory = tmp_path / "inventory.json"
    NpmSource(FakeClient(_small_frame())).inventory(inventory)

    class Failing(FakeClient):
        def get(self, url, params=None):
            raise SourceFailure(reason)

    with pytest.raises(SourceFailure, match=reason):
        candidate_walk(inventory, NpmSource(Failing({})).metadata)
    ledger = read_json(walk_ledger_path(inventory))
    assert ledger["complete"] is False and ledger["stop_reason"] == reason
    assert ledger["visited"] == 0 and ledger["pool"] == []


def test_walk_and_panel_record_exclusions_and_request_no_target_day(tmp_path):
    session = FakeSession(_small_frame())
    source = NpmSource(_capture_client(tmp_path, session))
    inventory = tmp_path / "inventory.json"
    assert "_design/app" not in source.inventory(inventory)["names"]
    manifest = build_panel(
        inventory, source.context, tmp_path / "panel", fetch_metadata=source.metadata
    )
    requested = " ".join(url + json.dumps(params) for url, params in session.requests)
    dates = re.findall(r"\d{4}-\d{2}-\d{2}", requested)
    assert dates and max(dates) == CONTEXT_END < "2026-06-03"
    urls = [url for url, _ in session.requests]
    assert any(url.endswith("/@s%2Fq0") for url in urls if DOWNLOADS in url)
    assert REGISTRY + "%40s%2Fq0" in urls
    visits = read_json(walk_ledger_path(inventory))["visits"]
    verdicts = {v["series_id"]: (v["verdict"], v["reason"]) for v in visits}
    assert verdicts["edge-old"] == ("eligible", None)
    assert verdicts["edge-new"] == ("ineligible", None)
    assert verdicts["gone"] == ("excluded", "http_404")
    assert verdicts["renamed"] == ("excluded", "package_identity_mismatch")
    assert verdicts["undated"] == ("excluded", "creation_time_missing")
    assert verdicts["naive"] == ("excluded", "creation_time_invalid")
    assert all(v["metadata_sha256"] for v in visits if v["verdict"] != "excluded")
    report = manifest["report"]
    assert {s["series_id"]: s["reason"] for s in report["skipped"]} == {
        name: reason or "creation_or_frame_ineligible"
        for name, (verdict, reason) in verdicts.items()
        if verdict != "eligible"
    }
    assert report["candidate_walk"]["stop_reason"] == "inventory_exhausted"
    assert report["eligible_frame_size"] == report["candidate_pool_size"] == 19
    assert report["candidate_inclusion_probability"] == 1.0
    assert manifest["candidate_walk_sha256"] == file_hash(walk_ledger_path(inventory))
    assert len(manifest["context_evidence"]) == 19
    assert all((tmp_path / e["path"]).is_file() for e in manifest["context_evidence"])
    local = (str(tmp_path), tmp_path.as_posix(), json.dumps(str(tmp_path))[1:-1])
    for written in (inventory, tmp_path / "panel" / "manifest.json"):
        assert not any(path in written.read_text(encoding="utf-8") for path in local)
    context = pd.read_parquet(tmp_path / "panel" / "context.parquet")
    assert context.date.max() == pd.Timestamp(CONTEXT_END) and context.series_id.nunique() == 19


def test_capture_evidence_paths_are_relative_to_the_repository(tmp_path):
    assert inspect.signature(CaptureClient).parameters["root"].default == ROOT_DIR
    with pytest.raises(ValueError, match="repository root"):
        CaptureClient(tmp_path / "captures", root=tmp_path / "repository")
    assert not (tmp_path / "captures").exists()
    session = FakeSession(_small_frame())
    client = _capture_client(tmp_path, session, Path("data", "captures"))
    client.get(REGISTRY + "p0")
    client.get(REGISTRY + "p0")
    first, replay = client.evidence
    assert first == replay and len(session.requests) == 1
    assert re.fullmatch(r"data/captures/[0-9a-f]{64}\.response", first["path"])
    assert first["metadata_path"] == first["path"].removesuffix(".response") + ".json"
    assert file_hash(tmp_path / first["path"]) == first["sha256"]
    assert read_json(tmp_path / first["metadata_path"])["sha256"] == first["sha256"]
    assert set(first) == {"path", "sha256", "metadata_path", "acquired_at"}


@pytest.mark.parametrize(
    "fault",
    ["transport_failure", "retry_exhausted", "http_501", "http_401", "http_403", "http_407"],
)
def test_context_outage_stops_the_pull_and_resumes_from_captures(tmp_path, fault):
    inventory, pool = _walked(tmp_path)
    session = FlakySession(_small_frame(), pool[5], fault)
    source = NpmSource(_capture_client(tmp_path, session))
    with pytest.raises(SourceFailure, match=fault):
        build_panel(inventory, source.context, tmp_path / "panel", fetch_metadata=source.metadata)
    assert not (tmp_path / "panel").exists()
    before, failed = [url for url, _ in session.requests], session.requests[-1][0]
    assert all(url.startswith(DOWNLOADS) for url in before) and len(set(before)) == 6
    assert unquote(failed.rsplit("/", 1)[1]) == pool[5]
    session.fault, session.requests = None, []
    source = NpmSource(_capture_client(tmp_path, session))
    resumed = build_panel(
        inventory, source.context, tmp_path / "panel", fetch_metadata=source.metadata
    )
    again = [url for url, _ in session.requests]
    assert again[0] == failed and len(again) == len(pool) - 5
    assert set(again).isdisjoint(set(before) - {failed})
    assert len(resumed["context_evidence"]) == len(pool)
    assert not any(s["stage"] == "context" for s in resumed["report"]["skipped"])
    fresh = NpmSource(_capture_client(tmp_path, FakeSession(_small_frame()), "uninterrupted"))
    reference = build_panel(
        inventory, fresh.context, tmp_path / "reference", fetch_metadata=fresh.metadata
    )
    assert resumed["series"] == reference["series"] and resumed["report"] == reference["report"]
    assert pd.read_parquet(tmp_path / "panel" / "context.parquet").equals(
        pd.read_parquet(tmp_path / "reference" / "context.parquet")
    )


@pytest.mark.parametrize(
    "fault",
    [
        "http_404",
        "download_identity_or_bounds_mismatch",
        "invalid_json",
        "missing_context_day",
    ],
)
def test_context_failures_of_one_candidate_exclude_it(tmp_path, fault):
    inventory, pool = _walked(tmp_path)
    source = NpmSource(_capture_client(tmp_path, FlakySession(_small_frame(), pool[5], fault)))
    manifest = build_panel(
        inventory, source.context, tmp_path / "panel", fetch_metadata=source.metadata
    )
    skipped = [s for s in manifest["report"]["skipped"] if s["stage"] == "context"]
    assert skipped == [dict(series_id=pool[5], stage="context", reason=fault)]
    assert sorted(s["series_id"] for s in manifest["series"]) == sorted(set(pool) - {pool[5]})


def test_corrupt_capture_stops_the_context_pull(tmp_path):
    inventory, pool = _walked(tmp_path)
    source = NpmSource(_capture_client(tmp_path, FakeSession(_small_frame())))
    source.context(dict(series_id=pool[5]), CONTEXT_START, CONTEXT_END)
    (tmp_path / source.client.evidence[-1]["path"]).write_bytes(b"{}")
    with pytest.raises(SourceFailure, match="capture_hash_mismatch"):
        build_panel(inventory, source.context, tmp_path / "panel", fetch_metadata=source.metadata)
    assert not (tmp_path / "panel").exists()


def test_nyc_context_comes_from_an_exhausted_daily_census_with_explicit_zero_days():
    from pulsegraph.study2.ingestion import NYCSource

    class Client:
        """One request per day; a request on 2026-03-05 for Noise, one per day for Heat."""

        def __init__(self):
            self.evidence, self.params = [], []

        def get(self, url, params):
            self.params.append(params)
            day = re.search(r"(\d{4}-\d{2}-\d{2})T00:00:00\.000", params["$where"])[1]
            assert params["$where"].count(day) == 2 and day < "2026-06-03"
            self.evidence.append(dict(acquired_at="2026-10-16T00:00:00+00:00", sha256=day))
            rows = [
                dict(
                    unique_key=f"h{day}",
                    created_date=f"{day}T10:00:00.000",
                    complaint_type="Heat",
                    community_board="02 BRONX",
                )
            ]
            if day == "2026-03-05":
                rows += [
                    dict(
                        unique_key=f"n{i}",
                        created_date=f"{day}T0{i}:00:00.000",
                        complaint_type="Noise",
                        community_board="01 BRONX",
                    )
                    for i in range(2)
                ]
            return rows

    client = Client()
    source = NYCSource(client)
    frame = [
        dict(series_id=json.dumps([p, b]), problem=p, board=b)
        for p, b in (("Noise", "01 BRONX"), ("Heat", "02 BRONX"), ("Other", "01 BRONX"))
    ]
    census = source.census(CONTEXT_START, CONTEXT_END, frame)
    assert len(client.params) == 275 and census["gap_days"] == []
    rows = source.context(frame[0], CONTEXT_START, CONTEXT_END)
    assert len(rows) == 275 and sum(r["count"] for r in rows) == 2
    assert [r["date"] for r in rows if r["count"]] == ["2026-03-05"]
    empty = source.context(frame[2], CONTEXT_START, CONTEXT_END)
    assert sum(r["count"] for r in empty) == 0
    assert all(r["count"] == 1 for r in source.context(frame[1], CONTEXT_START, CONTEXT_END))

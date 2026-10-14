"""Frozen metadata frames and context-only balanced panels. No target retrieval."""

import json
import time
from collections import Counter
from pathlib import Path
from urllib.parse import quote, urlparse

import numpy as np
import pandas as pd
import requests

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes
from pulsegraph.study2.constants import CONTEXT_END, CONTEXT_START, SEEDS, STRATA_START
from pulsegraph.study2.holdout import timestamp, utc_now

CANDIDATE_POOL = 10000
NAME_INVENTORY = "registry_name_inventory"


class SourceFailure(RuntimeError):
    """Sanitized source or completeness failure; never a zero count."""


class RequestBudget(SourceFailure):
    """An incomplete acquisition must resume explicitly, never truncate the frame."""


class CaptureClient:
    """Bounded, serial, cached GETs. Raw responses live under ignored data/raw/."""

    HOSTS = {
        "replicate.npmjs.com",
        "registry.npmjs.org",
        "api.npmjs.org",
        "data.cityofnewyork.us",
        "en.wikipedia.org",
        "wikimedia.org",
    }

    def __init__(
        self,
        directory,
        *,
        session=None,
        max_requests=500,
        max_seconds=3300,
        interval=1.0,
        sleep=time.sleep,
        monotonic=time.monotonic,
        root=ROOT_DIR,
    ):
        # Evidence names captures relative to the repository, never by a local absolute path.
        self.directory, self.root = Path(directory), Path(root).resolve()
        if not self.directory.resolve().is_relative_to(self.root):
            raise ValueError("Captures must live under the repository root")
        self.directory.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session() if session is None else session
        self.session.headers.update(
            {"User-Agent": "PulseGraph-study/2 (https://github.com/vprchlik/PulseGraph)"}
        )
        self.max_requests, self.max_seconds = max_requests, max_seconds
        self.sleep, self.monotonic, self.interval = sleep, monotonic, interval
        self.started = monotonic()
        self.requests = 0
        self.evidence = []

    def get(self, url, params=None):
        if urlparse(url).scheme != "https" or urlparse(url).hostname not in self.HOSTS:
            raise ValueError("Unapproved public source host")
        request = {"url": url, "params": params or {}}
        key = sha256_bytes(json.dumps(request, sort_keys=True).encode())
        meta, raw = self.directory / f"{key}.json", self.directory / f"{key}.response"
        if meta.exists():
            record = read_json(meta)
            if record["request"] != request or file_hash(raw) != record["sha256"]:
                raise SourceFailure("capture_hash_mismatch")
        else:
            for attempt in range(3):
                if (
                    self.requests >= self.max_requests
                    or self.monotonic() - self.started >= self.max_seconds
                ):
                    raise RequestBudget("acquisition_budget_reached")
                self.sleep(self.interval)
                self.requests += 1
                try:
                    response = self.session.get(
                        url, params=params, timeout=45, allow_redirects=False
                    )
                except requests.RequestException:
                    raise SourceFailure("transport_failure") from None
                if response.status_code in (429, 500, 502, 503, 504):
                    wait = response.headers.get("Retry-After", "10")
                    wait = float(wait) if wait.replace(".", "", 1).isdigit() else 60.0
                    if wait > 60 or self.monotonic() - self.started + wait >= self.max_seconds:
                        raise RequestBudget("server_retry_requires_later_resume")
                    self.sleep(wait)
                    continue
                if response.status_code != 200:
                    atomic_json(
                        self.directory / f"{key}.failure.json",
                        dict(
                            request=request, at=utc_now().isoformat(), status=response.status_code
                        ),
                    )
                    raise SourceFailure(f"http_{response.status_code}")
                raw.write_bytes(response.content)
                record = dict(
                    request=request,
                    acquired_at=utc_now().isoformat(),
                    sha256=file_hash(raw),
                    status=200,
                )
                atomic_json(meta, record)
                break
            else:
                raise SourceFailure("retry_exhausted")
        self.evidence.append(
            dict(
                path=raw.resolve().relative_to(self.root).as_posix(),
                sha256=file_hash(raw),
                metadata_path=meta.resolve().relative_to(self.root).as_posix(),
                acquired_at=record["acquired_at"],
            )
        )
        try:
            return json.loads(raw.read_bytes())
        except (ValueError, UnicodeError):
            raise SourceFailure("invalid_json") from None


def hash_key(domain, stage, stable_key):
    return sha256_bytes(
        json.dumps(
            [SEEDS["selection"], domain, stage, stable_key],
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def context_days(rows, *, start=CONTEXT_START, end=CONTEXT_END):
    frame = pd.DataFrame(rows, columns=["date", "count"])
    frame["date"] = pd.to_datetime(frame.date)
    # Filter before touching values: callers may pass metadata-aligned later rows;
    # source adapters themselves never request those rows.
    frame = frame.loc[frame.date.between(pd.Timestamp(start), pd.Timestamp(end))].copy()
    if frame.date.duplicated().any():
        raise SourceFailure("duplicate_context_day")
    frame = frame.sort_values("date")
    if not pd.DatetimeIndex(frame.date).equals(pd.date_range(start, end)):
        raise SourceFailure("missing_context_day")
    y = frame["count"].to_numpy(float)
    if not np.isfinite(y).all() or (y < 0).any() or (y != np.floor(y)).any():
        raise SourceFailure("invalid_context_count")
    return frame


def freeze_inventory(domain, entries, evidence, output):
    """Caller must have exhausted the source inventory; pagination failures never arrive here."""
    if not evidence:
        raise SourceFailure("inventory_evidence_missing")
    ids = [row["series_id"] for row in entries]
    if len(set(ids)) != len(ids):
        raise SourceFailure("duplicate_inventory_id")
    document = dict(
        domain=domain,
        acquired_at=utc_now().isoformat(),
        complete=True,
        source_evidence=evidence,
        entries=entries,
        frame_kind="current_public_inventory",
    )
    output = Path(output)
    if output.exists():
        raise FileExistsError("Frozen inventory is immutable")
    atomic_json(output, document)
    return document


def walk_ledger_path(inventory):
    inventory = Path(inventory)
    return inventory.with_name(inventory.stem + ".walk.json")


def key_failure(reason):
    """A failure that describes the requested key; any other failure interrupts a walk."""
    if reason in ("invalid_json", "invalid_metadata_document"):
        return True
    access = ("http_401", "http_403", "http_407", "http_429")
    return reason.startswith("http_4") and reason not in access


def outage(reason):
    """A failure of the source or the capture store; a context pull stops on it, never excludes."""
    if reason in ("transport_failure", "retry_exhausted", "capture_hash_mismatch"):
        return True
    return reason.startswith("http_") and not reason.startswith("http_4")


def walk_frame(size, visited, eligible, ineligible, excluded, exhausted):
    """The registered inclusion probability is pool/N over the eligible frame N.

    N is exact only when the walk exhausts the inventory. Otherwise only the visited
    candidate-hash prefix has known eligibility: that prefix is a uniform sample of the
    inventory, so N is estimated as size * eligible / visited and bounded by the verdicts.
    """
    pool = min(eligible, CANDIDATE_POOL)
    if exhausted:
        return dict(
            inventory_size=size,
            eligible_frame_size=eligible,
            eligible_frame_size_bounds=[eligible, eligible],
            eligible_frame_size_estimate=eligible,
            candidate_pool_size=pool,
            candidate_inclusion_probability=pool / eligible if eligible else 0,
            candidate_inclusion_probability_bounds=[1.0, 1.0] if eligible else [0, 0],
            candidate_inclusion_probability_estimate=pool / eligible if eligible else 0,
            candidate_inclusion_probability_basis="exact: the walk exhausted the inventory",
        )
    upper = size - ineligible - excluded
    estimate = size * eligible / visited
    return dict(
        inventory_size=size,
        eligible_frame_size=None,
        eligible_frame_size_bounds=[eligible, upper],
        eligible_frame_size_estimate=estimate,
        candidate_pool_size=pool,
        candidate_inclusion_probability=None,
        candidate_inclusion_probability_bounds=[pool / upper, 1.0],
        candidate_inclusion_probability_estimate=pool / estimate,
        candidate_inclusion_probability_basis=(
            "estimated: eligible frame size = inventory_size * eligible / visited over the "
            "visited candidate-hash prefix; bounds from the visited verdicts"
        ),
    )


def candidate_walk(inventory, fetch_metadata, document=None):
    """Creation metadata in candidate-hash order until CANDIDATE_POOL keys are eligible.

    A complete ledger is frozen beside the inventory and reused without requests. An
    interrupted walk saves an incomplete ledger and re-raises: a budget stop, outage or
    access failure never yields a shorter pool.
    """
    inventory_path = Path(inventory)
    ledger_path = walk_ledger_path(inventory_path)
    inventory_sha256 = file_hash(inventory_path)
    if ledger_path.exists():
        ledger = read_json(ledger_path)
        if ledger.get("complete") is True:
            if ledger["inventory_sha256"] != inventory_sha256:
                raise SourceFailure("walk_inventory_mismatch")
            return ledger
    document = read_json(inventory_path) if document is None else document
    if document.get("frame_kind") != NAME_INVENTORY or document.get("complete") is not True:
        raise SourceFailure("incomplete_inventory")
    domain, names = document["domain"], document["names"]
    if len(set(names)) != len(names):
        raise SourceFailure("duplicate_inventory_id")
    order = sorted(names, key=lambda n: (hash_key(domain, "candidate", n), n.encode()))
    start = pd.Timestamp(CONTEXT_START).date()
    visits = []

    def save(complete, stop_reason):
        counts = Counter(v["verdict"] for v in visits)
        ledger = dict(
            domain=domain,
            inventory_sha256=inventory_sha256,
            inventory_acquired_at=document["acquired_at"],
            inventory_size=len(names),
            pool_cap=CANDIDATE_POOL,
            complete=complete,
            stop_reason=stop_reason,
            written_at=utc_now().isoformat(),
            visited=len(visits),
            eligible=counts["eligible"],
            ineligible=counts["ineligible"],
            excluded=counts["excluded"],
            excluded_reasons=dict(
                Counter(v["reason"] for v in visits if v["verdict"] == "excluded")
            ),
            frame=walk_frame(
                len(names),
                len(visits),
                counts["eligible"],
                counts["ineligible"],
                counts["excluded"],
                stop_reason == "inventory_exhausted",
            )
            if complete
            else None,
            pool=[v["series_id"] for v in visits if v["verdict"] == "eligible"] if complete else [],
            visits=visits,
        )
        atomic_json(ledger_path, ledger)
        return ledger

    eligible = 0
    for name in order:
        visit = dict(series_id=name, candidate_hash=hash_key(domain, "candidate", name))
        try:
            record = fetch_metadata(name)
        except SourceFailure as error:
            reason = str(error)
            if isinstance(error, RequestBudget) or not key_failure(reason):
                save(False, reason)
                raise
            visits.append(
                dict(
                    visit,
                    verdict="excluded",
                    reason=reason,
                    created_at=None,
                    revision=None,
                    unpublished=None,
                    metadata_sha256=None,
                    acquired_at=None,
                )
            )
            continue
        created, reason = record.get("created_at"), None
        if record.get("name") != name:
            verdict, reason = "excluded", "package_identity_mismatch"
        elif not isinstance(created, str) or not created:
            verdict, reason = "excluded", "creation_time_missing"
        else:
            try:
                day = timestamp(created).date()
            except ValueError:
                verdict, reason = "excluded", "creation_time_invalid"
            else:
                verdict = "eligible" if day < start else "ineligible"
        visits.append(
            dict(
                visit,
                verdict=verdict,
                reason=reason,
                created_at=created,
                revision=record.get("revision"),
                unpublished=record.get("unpublished"),
                metadata_sha256=record.get("sha256"),
                acquired_at=record.get("acquired_at"),
            )
        )
        if verdict == "eligible":
            eligible += 1
            if eligible == CANDIDATE_POOL:
                return save(True, "pool_full")
    return save(True, "inventory_exhausted")


def build_panel(inventory, fetch_context, output, fetch_metadata=None):
    """All selection reads end at c1-1; strata use precisely its final 90 days."""
    inventory_path = Path(inventory)
    document = read_json(inventory_path)
    timestamp(document["acquired_at"])
    if document.get("complete") is not True or not document.get("source_evidence"):
        raise SourceFailure("incomplete_inventory")
    domain, walk = document["domain"], None
    if document.get("frame_kind") == NAME_INVENTORY:
        if fetch_metadata is None:
            raise ValueError("A name inventory needs its creation-metadata source")
        walk = candidate_walk(inventory_path, fetch_metadata, document)
        del document  # The full name list is not needed for the context pull.
        candidates = [
            dict(
                series_id=v["series_id"],
                created_at=v["created_at"],
                revision=v["revision"],
                metadata_sha256=v["metadata_sha256"],
            )
            for v in walk["visits"]
            if v["verdict"] == "eligible"
        ]
        skipped = [
            dict(
                series_id=v["series_id"],
                stage="metadata",
                reason=v["reason"] or "creation_or_frame_ineligible",
            )
            for v in walk["visits"]
            if v["verdict"] != "eligible"
        ]
        sampling = dict(
            walk["frame"],
            candidate_walk=dict(
                ledger_sha256=file_hash(walk_ledger_path(inventory_path)),
                stop_reason=walk["stop_reason"],
                visited=walk["visited"],
                eligible=walk["eligible"],
                ineligible=walk["ineligible"],
                excluded=walk["excluded"],
                excluded_reasons=walk["excluded_reasons"],
            ),
        )
    else:
        entries = document["entries"]
        if len({e["series_id"] for e in entries}) != len(entries):
            raise SourceFailure("duplicate_inventory_id")
        eligible, skipped = [], []
        for row in entries:
            if domain == "nyc311":
                valid = row.get("frame_year") == 2024 and row.get("frame_count", 0) > 0
            else:
                valid = (
                    bool(row.get("created_at"))
                    and timestamp(row["created_at"]).date() < pd.Timestamp(CONTEXT_START).date()
                )
            if valid and not row.get("excluded_reason"):
                eligible.append(row)
            else:
                skipped.append(
                    dict(
                        series_id=row["series_id"],
                        stage="metadata",
                        reason=row.get("excluded_reason") or "creation_or_frame_ineligible",
                    )
                )
        order = sorted(
            eligible,
            key=lambda r: (hash_key(domain, "candidate", r["series_id"]), r["series_id"].encode()),
        )
        candidates = order if domain == "nyc311" else order[:CANDIDATE_POOL]
        sampling = dict(
            inventory_size=len(entries),
            eligible_frame_size=len(eligible),
            candidate_pool_size=len(candidates),
            candidate_inclusion_probability=len(candidates) / len(eligible) if eligible else 0,
        )
    groups = {s: [] for s in ("dense", "sparse", "very_sparse")}
    context = {}
    owner = getattr(fetch_context, "__self__", None)
    client = getattr(owner, "client", None)
    first_evidence = len(client.evidence) if client is not None else 0
    if domain == "nyc311" and candidates:
        # A failure of the shared event census is a domain failure, not an entity exclusion.
        fetch_context(candidates[0], CONTEXT_START, CONTEXT_END)
    for row in candidates:
        key = row["series_id"]
        try:
            frame = context_days(fetch_context(row, CONTEXT_START, CONTEXT_END))
        except RequestBudget:
            raise  # Never turn an exhausted acquisition budget into a selection exclusion.
        except SourceFailure as error:
            if outage(str(error)):
                raise  # Nor an outage: the pull stops and resumes from cached captures.
            skipped.append(dict(series_id=key, stage="context", reason=str(error)))
            continue
        z = float((frame.loc[frame.date >= STRATA_START, "count"] == 0).mean())
        stratum = "dense" if z < 0.5 else "sparse" if z < 0.9 else "very_sparse"
        groups[stratum].append(
            {
                **row,
                "zero_fraction": z,
                "stratum": stratum,
                "selection_hash": hash_key(domain, "selection", key),
                "context_start": CONTEXT_START,
            }
        )
        context[key] = frame.assign(series_id=key)
    accepted = []
    reserves = []
    for stratum, group in groups.items():
        ranked = sorted(group, key=lambda r: (r["selection_hash"], r["series_id"].encode()))
        reserves.extend(ranked)
        accepted.extend(ranked[:100])
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    if (out / "manifest.json").exists():
        raise FileExistsError("Achieved panels are immutable")
    signals = (
        pd.concat([context[r["series_id"]] for r in accepted], ignore_index=True)
        if accepted
        else pd.DataFrame(columns=["date", "count", "series_id"])
    )
    signals.to_parquet(out / "context.parquet", index=False)
    report = dict(
        domain=domain,
        data_kind="context_only",
        **sampling,
        strata={
            s: dict(
                complete_candidates=len(g), achieved=min(100, len(g)), unfilled=max(0, 100 - len(g))
            )
            for s, g in groups.items()
        },
        skipped=skipped,
        context_start=CONTEXT_START,
        context_end=CONTEXT_END,
        strata_start=STRATA_START,
        selection_seed=SEEDS["selection"],
        target_values_opened=False,
    )
    atomic_json(out / "selection.json", dict(report=report, reserve_order=reserves))
    manifest = dict(
        domain=domain,
        series=accepted,
        verified_at=utc_now().isoformat(),
        inventory_sha256=file_hash(inventory_path),
        selection_sha256=file_hash(out / "selection.json"),
        context_sha256=file_hash(out / "context.parquet"),
        report=report,
    )
    if walk is not None:
        manifest["candidate_walk_sha256"] = sampling["candidate_walk"]["ledger_sha256"]
    manifest["context_evidence"] = (
        list(client.evidence[first_evidence:]) if client is not None else []
    )
    atomic_json(out / "manifest.json", manifest)
    return manifest


class NpmSource:
    ALL_DOCS = "https://replicate.npmjs.com/registry/_all_docs"

    def __init__(self, client):
        self.client = client

    def inventory(self, output):
        """Freeze every replication-feed name, scopes included; complete only when exhausted.

        No creation metadata and no popularity search: the candidate walk requests metadata.
        """
        output = Path(output)
        if output.exists():
            raise FileExistsError("Frozen inventory is immutable")
        first, names, after, totals = len(self.client.evidence), [], None, []
        while True:
            params = {"limit": 1000}
            if after is not None:
                params.update(startkey=json.dumps(after))
            response = self.client.get(self.ALL_DOCS, params)
            totals.append(response.get("total_rows"))
            rows = response["rows"]
            if not rows:
                break
            ids = [r["id"] for r in rows]
            if after is not None and ids[0] == after:
                ids = ids[1:]
            if not ids:
                break
            if (after is not None and ids[0] <= after) or len(set(ids)) != len(ids):
                raise SourceFailure("inventory_pagination_not_advancing")
            names.extend(ids)
            after = ids[-1]
        if len(names) != len(set(names)):
            raise SourceFailure("duplicate_inventory_name")
        pages = self.client.evidence[first:]
        if not pages:
            raise SourceFailure("inventory_evidence_missing")
        kept = [name for name in names if not name.startswith("_design/")]
        document = dict(
            domain="npm",
            frame_kind=NAME_INVENTORY,
            acquired_at=utc_now().isoformat(),
            complete=True,
            source=self.ALL_DOCS,
            page_limit=1000,
            pages=len(pages),
            first_page_acquired_at=pages[0]["acquired_at"],
            last_page_acquired_at=pages[-1]["acquired_at"],
            total_rows_first_page=totals[0],
            total_rows_last_page=totals[-1],
            design_documents_excluded=len(names) - len(kept),
            source_evidence=pages,
            names=kept,
        )
        atomic_json(output, document)
        return document

    def metadata(self, name):
        """Creation time and identity from the full registry document."""
        document = self.client.get("https://registry.npmjs.org/" + quote(name, safe=""))
        if not isinstance(document, dict):
            raise SourceFailure("invalid_metadata_document")
        evidence = self.client.evidence[-1]
        times = document.get("time")
        times = times if isinstance(times, dict) else {}
        return dict(
            name=document.get("name"),
            created_at=times.get("created"),
            unpublished="unpublished" in times,
            revision=document.get("_rev"),
            sha256=evidence["sha256"],
            acquired_at=evidence["acquired_at"],
        )

    def context(self, row, start, end):
        if start != CONTEXT_START or end != CONTEXT_END:
            raise ValueError("Selection endpoint cannot access target days")
        key = row["series_id"]
        result = self.client.get(
            # The download API's documented form for a scoped name: "@" as is, "/" encoded.
            f"https://api.npmjs.org/downloads/range/{start}:{end}/" + quote(key, safe="@")
        )
        if result.get("package") != key or result.get("start") != start or result.get("end") != end:
            raise SourceFailure("download_identity_or_bounds_mismatch")
        return [{"date": r["day"], "count": r["downloads"]} for r in result["downloads"]]


class NYCSource:
    URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

    def __init__(self, client):
        self.client = client
        self._context = None

    def _pages(self, params):
        offset = 0
        while True:
            rows = self.client.get(self.URL, {**params, "$limit": 50000, "$offset": offset})
            if not isinstance(rows, list):
                raise SourceFailure("invalid_socrata_result")
            yield from rows
            if len(rows) < 50000:
                return
            offset += len(rows)

    def inventory(self, output):
        params = {
            "$select": "complaint_type,community_board,count(distinct unique_key) as n",
            "$where": (
                "created_date >= '2024-01-01T00:00:00' AND created_date < '2025-01-01T00:00:00'"
            ),
            "$group": "complaint_type,community_board",
            "$order": "complaint_type,community_board",
        }
        entries = []
        import re

        for row in self._pages(params):
            problem, board = row.get("complaint_type", ""), row.get("community_board", "")
            valid = bool(
                problem
                and re.fullmatch(r"\d{2} (BRONX|BROOKLYN|MANHATTAN|QUEENS|STATEN ISLAND)", board)
            )
            if valid:
                number, borough = board.split(" ", 1)
                valid = (
                    1
                    <= int(number)
                    <= {
                        "BRONX": 12,
                        "BROOKLYN": 18,
                        "MANHATTAN": 12,
                        "QUEENS": 14,
                        "STATEN ISLAND": 3,
                    }[borough]
                )
            entries.append(
                dict(
                    series_id=json.dumps(
                        [problem, board], ensure_ascii=False, separators=(",", ":")
                    ),
                    problem=problem,
                    board=board,
                    frame_year=2024,
                    frame_count=int(row["n"]),
                    excluded_reason=None if valid else "unspecified_geography_or_problem",
                )
            )
        return freeze_inventory("nyc311", entries, self.client.evidence, output)

    def context(self, row, start, end):
        if start != CONTEXT_START or end != CONTEXT_END:
            raise ValueError("Selection endpoint cannot access target days")
        if self._context is None:
            where = f"created_date >= '{start}T00:00:00' AND created_date < '2026-06-03T00:00:00'"
            counts = self.client.get(
                self.URL,
                {"$select": "count(*) as rows,count(distinct unique_key) as keys", "$where": where},
            )
            if len(counts) != 1 or counts[0]["rows"] != counts[0]["keys"]:
                raise SourceFailure("source_has_duplicate_request_versions")
            params = {
                "$select": (
                    "complaint_type,community_board,"
                    "date_trunc_ymd(created_date) as day,count(*) as n"
                ),
                "$where": where,
                "$group": "complaint_type,community_board,day",
                "$order": "complaint_type,community_board,day",
            }
            captured, total = {}, 0
            for month in pd.period_range(start, end, freq="M"):
                lower = month.start_time.date().isoformat()
                upper = (month + 1).start_time.date().isoformat()
                monthly = {
                    **params,
                    "$where": where
                    + f" AND created_date >= '{lower}T00:00:00'"
                    + f" AND created_date < '{upper}T00:00:00'",
                }
                for item in self._pages(monthly):
                    key = (item.get("complaint_type", ""), item.get("community_board", ""))
                    day = pd.Timestamp(item["day"]).date().isoformat()
                    group = captured.setdefault(key, {})
                    if day in group or not start <= day <= end or not lower <= day < upper:
                        raise SourceFailure("duplicate_or_out_of_bounds_aggregate_day")
                    group[day] = int(item["n"])
                    total += int(item["n"])
            if total != int(counts[0]["rows"]):
                raise SourceFailure("aggregate_enumeration_changed_or_incomplete")
            self._context = captured
        observed = self._context.get((row["problem"], row["board"]), {})
        # Exhausted, bounded event enumeration establishes zero requests for absent groups.
        return [
            {"date": d.date().isoformat(), "count": observed.get(d.date().isoformat(), 0)}
            for d in pd.date_range(start, end)
        ]

"""Auditable context plans and deadline-enforced prospective prediction snapshots.

Preparing a plan never loads models. The public freeze command additionally invokes
the Study 2 gate; the internal writer accepts injectable predictors for offline tests.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import perf_counter
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes
from pulsegraph.study2.constants import (
    CALENDARS,
    FREEZE_AT,
    GITHUB_MANIFEST_SHA256,
    MODEL_PINS,
    NPM_READY_BY,
    PROTOCOL_COMMIT,
    PROTOCOL_SHA256,
    SEEDS,
    VARIANTS,
)


def utc_now():
    return datetime.now(timezone.utc)


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("UTC acquisition/approval timestamp required")
    return result.astimezone(timezone.utc)


def identity(value):
    return sha256_bytes(json.dumps(value, sort_keys=True, allow_nan=False).encode())


def evidence_file(entry):
    path = Path(entry["path"])
    if file_hash(path) != entry["sha256"]:
        raise ValueError("Evidence hash mismatch")
    return path


def read_context(source, now):
    """Require a complete explicitly verified calendar for every frozen series."""
    domain = source["domain"]
    if domain not in ("github", "npm"):
        raise ValueError("Holdout permits GitHub and npm only")
    manifest_path = evidence_file(source["manifest"])
    signal_path = evidence_file(source["signals"])
    evidence = read_json(evidence_file(source["completeness"]))
    if (
        evidence.get("calendar") != CALENDARS[domain]
        or evidence.get("verified") is not True
        or not evidence.get("method")
        or not evidence.get("response_evidence")
    ):
        raise ValueError("Verified source day convention and completeness evidence required")
    for entry in evidence["response_evidence"]:
        evidence_file(entry)
    if evidence.get("signals_sha256") != file_hash(signal_path):
        raise ValueError("Completeness evidence belongs to different signals")
    verified = timestamp(evidence["verified_at"])
    last = pd.Timestamp(evidence["last_complete_day"])
    if last.tzinfo or last != last.normalize():
        raise ValueError("Last complete day must be a nominal calendar date")
    if verified > now or last.date() >= verified.astimezone(ZoneInfo(CALENDARS[domain])).date():
        raise ValueError("Last complete day is not fully elapsed at verification")
    manifest = read_json(manifest_path)
    if domain == "github":
        if file_hash(manifest_path) != GITHUB_MANIFEST_SHA256 or len(manifest) != 300:
            raise ValueError("GitHub panel must be the unchanged Study 1 manifest")
        entries = [
            {
                "series_id": str(row["repo_id"]),
                "context_start": row.get("observation_start", row["creation_date"]),
            }
            for row in manifest
        ]
    else:
        entries = manifest["series"]
        if timestamp(manifest["verified_at"]) > NPM_READY_BY:
            raise ValueError("npm panel was not verified by September 26")
    ids = [row["series_id"] for row in entries]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("Empty or duplicate panel IDs")
    frame = pd.read_parquet(signal_path)
    if set(frame.columns) != {"series_id", "date", "count"}:
        raise ValueError("Unexpected signal schema")
    frame["date"] = pd.to_datetime(frame.date)
    if set(frame.series_id) != set(ids) or frame.duplicated(["series_id", "date"]).any():
        raise ValueError("Signals do not match the frozen panel")
    if frame.date.max() != last or frame.date.gt(last).any():
        raise ValueError("Signals must stop at the verified last complete day")
    values = frame["count"].to_numpy(float)
    if not np.isfinite(values).all() or (values < 0).any() or (values != np.floor(values)).any():
        raise ValueError("Invalid daily integer counts")
    dataset = {}
    for entry in entries:
        group = frame[frame.series_id == entry["series_id"]].sort_values("date")
        dates = pd.date_range(entry["context_start"], last)
        if len(dates) < 28 or not pd.DatetimeIndex(group.date).equals(dates):
            raise ValueError("Incomplete context: zero filling is not evidence")
        dataset[entry["series_id"]] = group["count"].to_numpy(float)
    bridge = (pd.Timestamp("2026-10-01") - last).days - 1
    if not 0 <= bridge or bridge + 30 > 128:
        raise ValueError("Bridge exceeds registered model lead support")
    return dataset, dict(
        last_complete_day=last.date().isoformat(),
        bridge_days=bridge,
        forecast_leads=bridge + 30,
        panel_size=len(ids),
        maximum_context_days=max(map(len, dataset.values())),
    )


def prepare_plan(sources, timing_evidence, *, npm_unavailable_reason=None, now=None):
    now = utc_now() if now is None else now
    if now > FREEZE_AT:
        raise ValueError("Holdout freeze deadline has passed")
    domains = [s["domain"] for s in sources]
    if len(set(domains)) != len(domains) or "github" not in domains:
        raise ValueError("Unique sources including GitHub required")
    timings = read_json(evidence_file(timing_evidence))
    if timings.get("data_kind") != "synthetic" or timings.get("passed") is not True:
        raise ValueError("Synthetic timing evidence required")
    details = {}
    for source in sources:
        _, details[source["domain"]] = read_context(source, now)
    npm_status = "available" if "npm" in domains else "pending"
    if "npm" not in domains and now > NPM_READY_BY and npm_unavailable_reason:
        npm_status = "unavailable"
    seconds = {}
    for model in (*MODEL_PINS, *VARIANTS[9:]):
        fit = timings["per_model"][model]
        seconds[model] = float(fit["load_seconds"]) + sum(
            d["panel_size"]
            * float(fit["forecast_seconds"])
            * max(1.0, d["maximum_context_days"] / fit["context_days"])
            * max(1.0, d["forecast_leads"] / fit["leads"])
            for d in details.values()
        )
        if not np.isfinite(seconds[model]) or seconds[model] <= 0:
            raise ValueError("Invalid runtime estimate")
    return dict(
        protocol_commit=PROTOCOL_COMMIT,
        protocol_sha256=PROTOCOL_SHA256,
        prepared_at=now.isoformat(),
        freeze_deadline=FREEZE_AT.isoformat(),
        sources=sources,
        source_details=details,
        timing_evidence=timing_evidence,
        npm_status=npm_status,
        npm_unavailable_reason=npm_unavailable_reason,
        comparison_count=9 if npm_status == "unavailable" else 18,
        seeds=SEEDS,
        variants=list(VARIANTS),
        seconds_per_model=seconds,
        estimated_seconds=sum(seconds.values()),
        approval_required=True,
    )


def _write_predictions(plan, output, predictor, *, clock=utc_now, runtime_metadata=None):
    """Internal, gated by the CLI. Atomic whole-series checkpoints; never skip failures."""
    if plan["npm_status"] == "pending":
        raise ValueError("npm decision is pending until its readiness deadline")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    state_path = output / "freeze.json"
    if not state_path.exists() and any(output.iterdir()):
        raise ValueError("Freeze directory has files but no owning state")
    run_id = identity({"plan": plan, "runtime": runtime_metadata})
    state = (
        read_json(state_path)
        if state_path.exists()
        else dict(
            identity=run_id,
            plan=plan,
            runtime=runtime_metadata,
            status="running",
            started_at=clock().isoformat(),
            completed={},
            failures=[],
            resumes=[],
        )
    )
    if state["identity"] != run_id or state["status"] == "complete":
        raise ValueError("Immutable completed freeze or changed resume inputs")
    if state_path.exists():
        state["resumes"].append(clock().isoformat())
    atomic_json(state_path, state)
    try:
        for source in plan["sources"]:
            dataset, details = read_context(source, clock())
            if details != plan["source_details"][source["domain"]]:
                raise ValueError("Context changed since author review")
            for entry in ("manifest", "signals", "completeness"):
                src = evidence_file(source[entry])
                dest = output / f"context-{source['domain']}-{entry}{src.suffix}"
                if dest.exists() and file_hash(dest) != file_hash(src):
                    raise ValueError("Frozen context snapshot changed")
                dest.write_bytes(src.read_bytes())
            for key, context in dataset.items():
                if clock() > FREEZE_AT:
                    raise ValueError("Holdout freeze deadline has passed")
                label = f"{source['domain']}:{key}"
                filename = sha256_bytes(label.encode()) + ".json"
                target = output / filename
                if label in state["completed"]:
                    if file_hash(target) != state["completed"][label]:
                        raise ValueError("Checkpoint hash mismatch")
                    continue
                start = perf_counter()
                forecasts = predictor(context, details["forecast_leads"], label)
                if set(forecasts) != set(VARIANTS):
                    raise ValueError("Missing registered forecast variant")
                for name, forecast in forecasts.items():
                    q = np.asarray(forecast["deciles"], float)
                    if (
                        q.shape != (details["forecast_leads"], 9)
                        or not np.isfinite(q).all()
                        or (q < 0).any()
                        or (np.diff(q, axis=1) < 0).any()
                    ):
                        raise ValueError(f"Invalid forecast: {name}")
                if clock() > FREEZE_AT:
                    raise ValueError("Holdout freeze deadline passed during forecast")
                atomic_json(
                    target,
                    dict(
                        domain=source["domain"],
                        series_id=key,
                        details=details,
                        forecasts=forecasts,
                        seconds=perf_counter() - start,
                        generated_at=clock().isoformat(),
                        identity=run_id,
                    ),
                )
                state["completed"][label] = file_hash(target)
                atomic_json(state_path, state)
        state["status"] = "complete"
        state["completed_at"] = clock().isoformat()
        state["prediction_files"] = {
            p.name: file_hash(p)
            for p in output.glob("*.json")
            if len(p.stem) == 64 and all(c in "0123456789abcdef" for c in p.stem)
        }
        state["context_files"] = {p.name: file_hash(p) for p in output.glob("context-*")}
        atomic_json(state_path, state)
    except BaseException as error:
        state["status"] = "failed"
        state["failures"].append(dict(at=clock().isoformat(), reason=type(error).__name__))
        atomic_json(state_path, state)
        raise
    return state


def verify_predictions(directory):
    directory = Path(directory)
    state = read_json(directory / "freeze.json")
    plan = state["plan"]
    if (
        state.get("status") != "complete"
        or plan.get("protocol_commit") != PROTOCOL_COMMIT
        or plan.get("protocol_sha256") != PROTOCOL_SHA256
        or state.get("identity") != identity({"plan": plan, "runtime": state["runtime"]})
        or timestamp(state["completed_at"]) > FREEZE_AT
    ):
        raise ValueError("Invalid or late frozen prediction record")
    expected = set()
    for source in plan["sources"]:
        domain = source["domain"]
        manifest_file = directory / f"context-{domain}-manifest.json"
        if file_hash(manifest_file) != source["manifest"]["sha256"]:
            raise ValueError("Frozen manifest hash mismatch")
        manifest = read_json(manifest_file)
        keys = (
            [str(r["repo_id"]) for r in manifest]
            if domain == "github"
            else [r["series_id"] for r in manifest["series"]]
        )
        expected.update(f"{domain}:{key}" for key in keys)
    if set(state["completed"]) != expected:
        raise ValueError("Frozen panel is incomplete")
    for filename, digest in state["context_files"].items():
        if Path(filename).name != filename or file_hash(directory / filename) != digest:
            raise ValueError("Frozen context hash mismatch")
    expected_files = {sha256_bytes(label.encode()) + ".json" for label in expected}
    if set(state["prediction_files"]) != expected_files:
        raise ValueError("Frozen prediction file set differs from the panel")
    for label in sorted(expected):
        path = directory / (sha256_bytes(label.encode()) + ".json")
        if (
            file_hash(path) != state["completed"][label]
            or file_hash(path) != state["prediction_files"][path.name]
        ):
            raise ValueError("Prediction hash mismatch")
        record = read_json(path)
        details = plan["source_details"][record["domain"]]
        if (
            record["identity"] != state["identity"]
            or record["details"] != details
            or f"{record['domain']}:{record['series_id']}" != label
            or timestamp(record["generated_at"]) > FREEZE_AT
            or set(record["forecasts"]) != set(VARIANTS)
        ):
            raise ValueError("Prediction identity or model family mismatch")
        for forecast in record["forecasts"].values():
            q = np.asarray(forecast["deciles"], float)
            if (
                q.shape != (details["forecast_leads"], 9)
                or not np.isfinite(q).all()
                or (q < 0).any()
                or (np.diff(q, axis=1) < 0).any()
            ):
                raise ValueError("Invalid saved prediction")
    return dict(
        passed=True,
        series=len(expected),
        variants=len(VARIANTS),
        freeze_sha256=file_hash(directory / "freeze.json"),
    )


def settlement_start(horizon):
    return {
        7: datetime(2026, 10, 15, 18, tzinfo=timezone.utc),
        30: datetime(2026, 11, 7, 18, tzinfo=timezone.utc),
    }[horizon]


def settlement_attempts(horizon):
    return tuple(settlement_start(horizon) + timedelta(hours=h) for h in range(0, 73, 12))

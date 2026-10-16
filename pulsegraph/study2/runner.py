"""Whole-series checkpoints for authorized Study 2 components; failures never drop windows."""

import json
from pathlib import Path
from time import perf_counter

import pandas as pd

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes
from pulsegraph.study2.constants import CALENDARS, CONTEXT_START, CUTOFFS, ENDPOINT, VARIANTS
from pulsegraph.study2.gate import target_completeness
from pulsegraph.study2.holdout import evidence_file, identity, utc_now
from pulsegraph.study2.ingestion import context_days
from pulsegraph.study2.scores import score

# The free GPU memory at start and the allocator budget derived from it differ between
# invocations on one machine. Each invocation records them; the resume identity leaves them out.
VOLATILE_HARDWARE = ("gpu_free_at_start_bytes", "allocator_limit_bytes")


def external_dataset(readiness, *, root=ROOT_DIR):
    """Only the public run entry point calls this, after target-access authorization.

    Each panel's signals are read only through the verified completeness document of their
    target pull, and their prefix must reproduce the frozen selection context.
    """
    dataset = {}
    for domain, panel in readiness["panels"].items():
        calendar = CALENDARS.get(
            readiness.get("package_domain") if domain == "packages" else domain
        )
        signals_path, _ = target_completeness(panel, calendar, root=root)
        manifest = read_json(evidence_file(panel["manifest"]))
        signals = pd.read_parquet(signals_path)
        context_path = evidence_file(panel["context"])
        if file_hash(context_path) != manifest["context_sha256"]:
            raise ValueError("Selection context snapshot changed")
        frozen_context = pd.read_parquet(context_path)
        keys = [row["series_id"] for row in manifest["series"]]
        if not keys or len(keys) != len(set(keys)) or set(signals.series_id) != set(keys):
            raise ValueError("Achieved panel and target snapshot differ")
        for key in keys:
            raw = signals.loc[signals.series_id == key, ["date", "count"]]
            frame = context_days(raw.to_dict("records"), start=CONTEXT_START, end=ENDPOINT)
            prefix = context_days(raw.to_dict("records"))
            previous = context_days(
                frozen_context.loc[frozen_context.series_id == key, ["date", "count"]].to_dict(
                    "records"
                )
            )
            if not prefix.equals(previous):
                raise ValueError("Run signals changed the frozen selection context")
            dataset[(domain, key)] = frame.set_index("date")["count"]
    return dataset


def resume_identity(metadata):
    """The run's identity: every metadata field except the per-invocation GPU memory figures."""
    hardware = metadata.get("hardware")
    if isinstance(hardware, dict):
        metadata = dict(
            metadata,
            hardware={k: v for k, v in hardware.items() if k not in VOLATILE_HARDWARE},
        )
    return identity(metadata)


def _add_timings(totals, timings):
    """Accumulate one completed pool call's per-model timings."""
    for name, entry in timings.items():
        total = totals.setdefault(
            name, dict(calls=0, load_seconds=0.0, forecast_seconds=0.0, max_forecast_seconds=0.0)
        )
        total["calls"] += 1
        total["load_seconds"] += float(entry["load_seconds"])
        total["forecast_seconds"] += float(entry["forecast_seconds"])
        total["max_forecast_seconds"] = max(
            total["max_forecast_seconds"], float(entry["forecast_seconds"])
        )


def _final_memory(memory):
    if memory is None:
        return None
    try:
        return memory()
    except Exception as error:  # A failed snapshot is recorded; it never masks the run's outcome.
        return dict(unavailable=f"{type(error).__name__}: {error}")


def _evaluate(dataset, output, pool, *, metadata, synthetic=False, memory=None, variants=VARIANTS):
    """`variants` is the registered variant list of the component's study; Study 3 adds two."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    state_path = output / "run.json"
    run_id = resume_identity(metadata)
    state = (
        read_json(state_path)
        if state_path.exists()
        else dict(
            identity=run_id,
            metadata=metadata,
            status="running",
            completed={},
            resumes=[],
            failures=[],
            invocations=[],
            started_at=utc_now().isoformat(),
        )
    )
    if state["identity"] != run_id or state["status"] == "complete":
        raise ValueError("Immutable completed run or changed resume identity")
    if state_path.exists():
        state["resumes"].append(utc_now().isoformat())
    hardware = metadata.get("hardware") if isinstance(metadata.get("hardware"), dict) else {}
    timings = {}
    invocation = dict(
        started_at=utc_now().isoformat(),
        hardware={k: hardware[k] for k in VOLATILE_HARDWARE if k in hardware},
        series_completed=0,
        timings=timings,
    )
    state.setdefault("invocations", []).append(invocation)
    state["status"] = "running"
    atomic_json(state_path, state)
    started = perf_counter()
    try:
        for (domain, key), series in dataset.items():
            label = json.dumps([domain, key], separators=(",", ":"))
            path = output / (sha256_bytes(label.encode()) + ".json")
            if label in state["completed"]:
                if file_hash(path) != state["completed"][label]:
                    raise ValueError("Checkpoint hash mismatch")
                continue
            rows = []
            for cutoff in (180, 210, 240) if synthetic else CUTOFFS:
                context = series.iloc[:cutoff] if synthetic else series.loc[series.index < cutoff]
                target = (
                    series.iloc[cutoff : cutoff + 30]
                    if synthetic
                    else series.loc[
                        (series.index >= cutoff)
                        & (series.index < pd.Timestamp(cutoff) + pd.Timedelta(days=30))
                    ]
                )
                if len(target) != 30:
                    raise ValueError("Incomplete target window")
                for horizon in (7, 30):
                    forecasts = pool.forecast(context.to_numpy(), horizon, f"{label}:{cutoff}")
                    _add_timings(timings, getattr(pool, "timings", {}))
                    if set(forecasts) != set(variants):
                        raise ValueError("Incomplete model family")
                    if synthetic:
                        from pulsegraph.study2.synthetic import oracle_forecast

                        forecasts["oracle"] = oracle_forecast(key, context.to_numpy(), horizon)
                    for name, forecast in forecasts.items():
                        rows.append(
                            dict(
                                domain=domain,
                                series_id=key,
                                cutoff=str(cutoff),
                                horizon=horizon,
                                model=name,
                                forecast=forecast,
                                target=target.iloc[:horizon].tolist(),
                                context_mean=float(context.mean()),
                                scores=score(
                                    target.iloc[:horizon].tolist(), forecast, context.to_numpy()
                                ),
                            )
                        )
            atomic_json(path, dict(rows=rows, identity=run_id))
            state["completed"][label] = file_hash(path)
            invocation["series_completed"] += 1
            atomic_json(state_path, state)
        state.update(status="complete", completed_at=utc_now().isoformat())
    except BaseException as error:
        state["status"] = "failed"
        state["failures"].append(dict(at=utc_now().isoformat(), reason=type(error).__name__))
        raise
    finally:
        invocation.update(
            ended_at=utc_now().isoformat(),
            wall_seconds=perf_counter() - started,
            memory=_final_memory(memory),
        )
        atomic_json(state_path, state)
    return state

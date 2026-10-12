"""Whole-series checkpoints for authorized Study 2 components; failures never drop windows."""

import json
from pathlib import Path

import pandas as pd

from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes
from pulsegraph.study2.constants import CONTEXT_START, CUTOFFS, ENDPOINT, VARIANTS
from pulsegraph.study2.holdout import evidence_file, identity, utc_now
from pulsegraph.study2.ingestion import context_days
from pulsegraph.study2.scores import score


def external_dataset(readiness):
    """Only the public run entry point calls this, after target-access authorization."""
    dataset = {}
    for domain, panel in readiness["panels"].items():
        manifest = read_json(evidence_file(panel["manifest"]))
        signals = pd.read_parquet(evidence_file(panel["signals"]))
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


def _evaluate(dataset, output, pool, *, metadata, synthetic=False):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    state_path = output / "run.json"
    run_id = identity(metadata)
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
            started_at=utc_now().isoformat(),
        )
    )
    if state["identity"] != run_id or state["status"] == "complete":
        raise ValueError("Immutable completed run or changed resume identity")
    if state_path.exists():
        state["resumes"].append(utc_now().isoformat())
    state["status"] = "running"
    atomic_json(state_path, state)
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
                    if set(forecasts) != set(VARIANTS):
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
            atomic_json(state_path, state)
        state.update(status="complete", completed_at=utc_now().isoformat())
        atomic_json(state_path, state)
    except BaseException as error:
        state["status"] = "failed"
        state["failures"].append(dict(at=utc_now().isoformat(), reason=type(error).__name__))
        atomic_json(state_path, state)
        raise
    return state

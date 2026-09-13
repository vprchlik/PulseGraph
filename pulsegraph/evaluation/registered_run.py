"""Registered runner: gate first, atomic checkpoints at whole-repository boundaries."""

import json
import os
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import pandas as pd

from pulsegraph.data.regimes import context_regime
from pulsegraph.evaluation.artifacts import ARTIFACT_FILES, file_hash, validate_results
from pulsegraph.evaluation.backtest import rolling_backtest, summarize_backtest
from pulsegraph.evaluation.registration import real_run_gate
from pulsegraph.forecast.hardware import configure_gpu, memory_snapshot
from pulsegraph.forecast.registered import make_registered_model, release_model
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes


def _now():
    return datetime.now(timezone.utc).isoformat()


def _atomic_parquet(frame, path):
    temporary = path.with_suffix(".partial.parquet")
    frame.to_parquet(temporary, index=False)
    os.replace(temporary, path)


def _identity(metadata):
    keys = (
        "protocol_commit",
        "protocol_sha256",
        "implementation_commit",
        "source_sha256",
        "packages",
        "config",
        "models",
        "repositories",
        "input_sha256",
        "readiness_sha256",
        "comparison_family",
    )
    return sha256_bytes(
        json.dumps({k: metadata[k] for k in keys}, sort_keys=True, allow_nan=False).encode()
    )


def _checkpointed_run(output_dir, *, metadata, dataset, config, model_factory, release, measure):
    """Internal engine; public entry point below always obtains these inputs from the gate."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoints = output_dir / "checkpoints"
    checkpoints.mkdir(exist_ok=True)
    state_path = output_dir / "run.json"
    identity = _identity(metadata)
    if state_path.exists():
        state = read_json(state_path)
        if state.get("status") == "complete":
            raise ValueError("Completed runs are immutable; use a new linked directory")
        if state.get("run_identity") != identity:
            raise ValueError("Resume inputs, implementation, runtime or declarations changed")
        state["resumes"].append(
            {
                "at": _now(),
                "previous_status": state["status"],
                "command": metadata["command"],
                "hardware": metadata["hardware"],
            }
        )
    else:
        if any(checkpoints.iterdir()):
            raise ValueError("Checkpoint directory has no owning run.json")
        state = {
            **metadata,
            "run_identity": identity,
            "started_at": _now(),
            "status": "running",
            "resumes": [],
            "failures": [],
            "completed_repositories": [],
            "checkpoint_sha256": {},
        }
    # Persist ownership/resume before examining or evaluating any window.
    state["status"] = "running"
    atomic_json(state_path, state)
    completed = {}
    for marker in sorted(checkpoints.glob("*.json")):
        entry = read_json(marker)
        name = entry["repo_name"]
        if name not in dataset or entry.get("run_identity") != identity or name in completed:
            raise ValueError("Checkpoint identity mismatch")
        basename = sha256_bytes(name.encode())
        if marker.name != f"{basename}.json":
            raise ValueError("Checkpoint name mismatch")
        parquet = checkpoints / f"{basename}.parquet"
        if file_hash(parquet) != entry["sha256"]:
            raise ValueError("Checkpoint hash mismatch")
        previous_hash = state["checkpoint_sha256"].get(name)
        if previous_hash is not None and previous_hash != entry["sha256"]:
            raise ValueError("Checkpoint differs from the recorded completed repository")
        rows = pd.read_parquet(parquet)
        validate_results(rows, {**metadata, "repositories": [name]}, {name: dataset[name]})
        completed[name] = rows
        state["checkpoint_sha256"][name] = entry["sha256"]
    missing = set(state["completed_repositories"]) - set(completed)
    if missing:
        raise ValueError("Previously completed checkpoint is missing")
    if state["resumes"]:
        state["resumes"][-1]["completed_repositories_reused"] = sorted(completed)
    state["completed_repositories"] = sorted(completed)
    atomic_json(state_path, state)
    models = {}
    with ExitStack() as lifecycle:
        for name in metadata.get("repository_order", sorted(dataset)):
            if name in completed:
                continue
            started = perf_counter()
            try:
                rows = []
                for model_name in metadata["models"]:
                    if model_name not in models:
                        models[model_name] = model_factory(model_name)
                        lifecycle.callback(release, models[model_name])
                    model = models[model_name]
                    start_model = perf_counter()
                    result = rolling_backtest(
                        dataset[name], model, config, repo_name=name, labeler=context_regime
                    )
                    result["model_repository_seconds"] = perf_counter() - start_model
                    result["hardware_memory"] = json.dumps(measure(model_name), sort_keys=True)
                    rows.append(result)
                results = pd.concat(rows, ignore_index=True)
                validate_results(
                    results, {**metadata, "repositories": [name]}, {name: dataset[name]}
                )
                basename = sha256_bytes(name.encode())
                parquet = checkpoints / f"{basename}.parquet"
                _atomic_parquet(results, parquet)
                entry = {
                    "repo_name": name,
                    "run_identity": identity,
                    "sha256": file_hash(parquet),
                    "completed_at": _now(),
                    "seconds": perf_counter() - started,
                }
                atomic_json(checkpoints / f"{basename}.json", entry)
                completed[name] = results
                state["completed_repositories"] = sorted(completed)
                state["checkpoint_sha256"][name] = entry["sha256"]
                atomic_json(state_path, state)
            except BaseException as error:
                state["status"] = "failed"
                state["failures"].append(
                    {
                        "repo_name": name,
                        "at": _now(),
                        "error_type": type(error).__name__,
                        "completed_windows_are_not_skipped": True,
                    }
                )
                atomic_json(state_path, state)
                raise
        results = pd.concat([completed[name] for name in sorted(completed)], ignore_index=True)
        validate_results(results, metadata, dataset)
        return results, state


def run_registered(
    *, output_dir, readiness_path, signals_path, manifest_path, implementation_commit, command
):
    metadata, config, signals, manifest, dataset, _ = real_run_gate(
        readiness_path=readiness_path,
        signals_path=signals_path,
        manifest_path=manifest_path,
        implementation_commit=implementation_commit,
    )
    output_dir = Path(output_dir)
    if (
        output_dir.exists()
        and not (output_dir / "run.json").is_file()
        and any(output_dir.iterdir())
    ):
        raise ValueError("Output directory contains unrelated files")
    metadata["command"] = command
    metadata["hardware"] = configure_gpu()
    metadata["repository_order"] = manifest.sort_values("repo_id").repo_name.tolist()
    results, state = _checkpointed_run(
        output_dir,
        metadata=metadata,
        dataset=dataset,
        config=config,
        model_factory=lambda name: make_registered_model(name, metadata["specification"]),
        release=release_model,
        measure=lambda name: (
            memory_snapshot()
            if name in {"chronos2", "timesfm3", "timesfm2p5"}
            else {"device": "cpu"}
        ),
    )
    _atomic_parquet(results, output_dir / "results.parquet")
    _atomic_parquet(signals, output_dir / "signals.parquet")
    atomic_json(output_dir / "manifest.json", manifest.to_dict("records"))
    temporary = output_dir / "summary.partial.csv"
    summarize_backtest(results).to_csv(temporary, index=False)
    os.replace(temporary, output_dir / "summary.csv")
    state["artifact_sha256"] = {
        name: file_hash(output_dir / name) for name in sorted(ARTIFACT_FILES)
    }
    state["status"], state["finished_at"] = "complete", _now()
    atomic_json(output_dir / "run.json", state)
    return state

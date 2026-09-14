"""Entire gate/artifact/inference path with synthetic data and mocked Git/GPU/models."""

from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pulsegraph.config import ROOT_DIR
from pulsegraph.data.frame import freeze_frame_order, walk_frame
from pulsegraph.evaluation.artifacts import file_hash, read_run_artifact
from pulsegraph.evaluation.confirmatory import confirmatory_tables
from pulsegraph.evaluation.registered_run import run_registered
from pulsegraph.evaluation.registration import (
    MODEL_PINS,
    PROTOCOL_COMMIT,
    PROTOCOL_SHA256,
    RUNTIME_PACKAGES,
    _git,
    real_run_gate,
)
from pulsegraph.forecast.output import COMMON_QUANTILES, ForecastOutput
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes


@pytest.fixture
def ready(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    (root / "study").mkdir(parents=True)
    for name in ("PROTOCOL.md", "study/run_spec.json", "study/comparisons.json"):
        (root / name).write_bytes((ROOT_DIR / name).read_bytes())
    spec = read_json(root / "study/run_spec.json")
    implementation = "a" * 40
    registered_blob = _git(ROOT_DIR, "show", f"{PROTOCOL_COMMIT}:PROTOCOL.md")
    assert sha256_bytes(registered_blob) == PROTOCOL_SHA256
    assert (root / "PROTOCOL.md").read_bytes().startswith(registered_blob)

    def git(_, *args):
        if args[0] == "rev-parse":
            return implementation.encode()
        if args[0] == "show":
            assert args == ("show", f"{PROTOCOL_COMMIT}:PROTOCOL.md")
            return registered_blob
        if args[0] == "status":
            return b""
        if args[0] == "ls-files":
            return b"PROTOCOL.md\nstudy/run_spec.json\nstudy/comparisons.json\n"
        pytest.fail("Unexpected Git command")

    monkeypatch.setattr("pulsegraph.evaluation.registration._git", git)
    versions = {name: "1.0.0" for name in RUNTIME_PACKAGES} | spec["package_pins"]
    monkeypatch.setattr("pulsegraph.evaluation.registration.installed_versions", lambda: versions)
    frame = pd.DataFrame(
        [
            dict(
                repo_id=i,
                repo_name=f"synthetic/repo-{i}",
                creation_date="2025-01-01",
                day90_stars=20,
            )
            for i in (1, 2)
        ]
    )
    order = freeze_frame_order(frame)
    order.to_csv(root / "order.csv", index=False)
    log = walk_frame(
        order,
        lambda row: {"complete": True, "repo_id": row["repo_id"], "repo_name": row["repo_name"]},
    )
    atomic_json(root / "sampling.json", log)
    manifest = order.drop(columns=["selection_rank", "selection_seed"]).assign(
        observation_start="2025-01-01",
        coverage_complete=True,
        repository_created_at="2025-01-01T12:00:00Z",
    )
    atomic_json(root / "manifest.json", manifest.to_dict("records"))
    dates = pd.date_range("2025-01-01", "2026-08-31")
    signals = pd.DataFrame(
        [
            dict(repo_name=name, event_date=day, stars=idx % 4)
            for name in manifest.repo_name
            for idx, day in enumerate(dates)
        ]
    )
    signals.to_parquet(root / "signals.parquet", index=False)
    validation = {
        "selected_repositories": [f"synthetic/validation-{i}" for i in range(20)],
        "repositories": [
            {"repo_name": f"synthetic/validation-{i}", "repo_id": i, "status": "complete"}
            for i in range(19)
        ],
        "failures": [
            {
                "repo_name": "synthetic/validation-19",
                "capture": "synthetic-failed-attempt",
                "reason": "http_404",
            }
        ],
        "n_attempted": 20,
        "n_complete": 19,
        "n_failed": 1,
        "n_failures": 1,
    }
    validation["repositories"].append({**validation["failures"][0], "status": "failed"})
    atomic_json(root / "validation.json", validation)
    documents = {
        "comparison": {
            "n_rows": 19 * 366 * 3,
            "hypotheses": ["UTC", "America/Los_Angeles", "UTC-08:00"],
            "n_hourly_rows": 19 * 366 * 24,
            "n_scored_days_per_repository_hypothesis": 365,
            "validation_sha256": file_hash(root / "validation.json"),
            "n_attempted": 20,
            "n_complete": 19,
            "n_failed": 1,
            "n_failures": 1,
            "failures": validation["failures"],
            "compared_repo_ids": list(range(19)),
        },
        "frame_coverage": {"complete": True, "evidence": "synthetic test only"},
        "cost_approval": {"author": "synthetic test only"},
        "query_provenance": {"jobs": "synthetic test only; no jobs executed"},
        "smoke": {
            "passed": True,
            "models": list(MODEL_PINS) + spec["baselines"],
            "peak_vram_bytes": 2_000_000_000,
            "median_checks": {
                name: {"passed": True}
                for name in ("autoets_weekly", "autoarima_weekly", "autotheta_weekly")
            },
            "runtime_versions": versions,
            "implementation_commit": implementation,
        },
    }
    for name, doc in documents.items():
        atomic_json(root / f"{name}.json", doc)
    readiness = read_json(ROOT_DIR / "study/readiness.example.json")
    for key, value in list(readiness.items()):
        if value is None:
            readiness[key] = "synthetic fixture only"
    readiness.update(
        calendar_convention="UTC",
        implementation_commit=implementation,
        main_study_resolved=True,
        runtime_versions=versions,
        signals_sha256=file_hash(root / "signals.parquet"),
        manifest_sha256=file_hash(root / "manifest.json"),
    )
    for name in readiness["evidence"]:
        filename = {"candidate_order": "order.csv", "sampling_log": "sampling.json"}.get(
            name, f"{name}.json"
        )
        readiness["evidence"][name] = {"path": filename, "sha256": file_hash(root / filename)}
    atomic_json(root / "readiness.json", readiness)
    args = dict(
        root=root,
        readiness_path=root / "readiness.json",
        signals_path=root / "signals.parquet",
        manifest_path=root / "manifest.json",
        implementation_commit=implementation,
    )
    return args


def test_gate_real_writer_reader_and_confirmatory_family_with_synthetic_fixtures(
    ready, monkeypatch
):
    bundle = real_run_gate(**ready)
    metadata = bundle[0]
    assert len(bundle[4]) == 2 and metadata["comparison_count"] == 18
    monkeypatch.setattr(
        "pulsegraph.evaluation.registered_run.real_run_gate", lambda **kwargs: deepcopy(bundle)
    )
    monkeypatch.setattr(
        "pulsegraph.evaluation.registered_run.configure_gpu",
        lambda: {
            "gpu_model": "mock",
            "gpu_driver": "mock",
            "cuda_version": "mock",
            "pytorch_version": "mock",
        },
    )

    class Fake:
        def __init__(self, name):
            self.name = name

        def forecast(self, context, horizon, repo_name):
            details = {"seed": 20260912}
            if self.name in MODEL_PINS:
                details.update(zip(("model_id", "revision"), MODEL_PINS[self.name]))
            return ForecastOutput(
                repo_name,
                self.name,
                horizon,
                len(context),
                np.array(COMMON_QUANTILES),
                np.ones((horizon, 9)),
                metadata=details,
            )

    monkeypatch.setattr(
        "pulsegraph.evaluation.registered_run.make_registered_model", lambda name, spec: Fake(name)
    )
    monkeypatch.setattr("pulsegraph.evaluation.registered_run.release_model", lambda _: None)
    monkeypatch.setattr(
        "pulsegraph.evaluation.registered_run.memory_snapshot", lambda: {"mock": True}
    )
    out = Path(ready["root"]) / "output"
    run_args = {k: v for k, v in ready.items() if k != "root"}
    state = run_registered(output_dir=out, command=["synthetic-test"], **run_args)
    assert state["status"] == "complete" and state["protocol_commit"].startswith("5f01769")
    rows, saved, _ = read_run_artifact(out)
    assert len(rows) == 2 * 18 * 3 * 3
    inference, pairs = confirmatory_tables(rows, saved["specification"], saved["comparison_family"])
    assert len(inference) == 18 and len(pairs) == 36
    assert (inference.wilcoxon_p_bh == 1).all()
    assert (inference.mean_diff == 0).all()
    assert inference.calendar_conditional.all()
    with pytest.raises(ValueError, match="Completed runs"):
        run_registered(output_dir=out, command=["synthetic-test"], **run_args)


@pytest.mark.parametrize(
    "mutation",
    [
        "evidence",
        "missing_day",
        "sampling",
        "runtime",
        "protocol",
        "validation_unattempted",
        "validation_reason",
        "validation_count",
        "comparison_count",
        "comparison_identity",
        "comparison_failure",
    ],
)
def test_gate_rejects_changed_provenance_and_data(ready, mutation):
    root = ready["root"]
    readiness = read_json(root / "readiness.json")
    if mutation == "evidence":
        readiness["evidence"]["validation"]["sha256"] = "0" * 64
    elif mutation == "runtime":
        readiness["runtime_versions"]["torch"] = "different"
    elif mutation == "protocol":
        (root / "PROTOCOL.md").write_text("changed", encoding="utf-8")
    elif mutation == "missing_day":
        path = root / "signals.parquet"
        pd.read_parquet(path).iloc[1:].to_parquet(path, index=False)
        readiness["signals_sha256"] = file_hash(path)
    elif mutation == "sampling":
        path = root / "sampling.json"
        doc = read_json(path)
        doc["accepted"] = doc["accepted"][:1]
        atomic_json(path, doc)
        readiness["evidence"]["sampling_log"]["sha256"] = file_hash(path)
    elif mutation.startswith("validation_"):
        path = root / "validation.json"
        doc = read_json(path)
        if mutation == "validation_unattempted":
            doc["repositories"].pop()
            doc["n_attempted"] = 19
        elif mutation == "validation_reason":
            doc["repositories"][-1]["reason"] = ""
            doc["failures"][0]["reason"] = ""
        else:
            doc["n_complete"] = 20
        atomic_json(path, doc)
        readiness["evidence"]["validation"]["sha256"] = file_hash(path)
        comparison = read_json(root / "comparison.json")
        comparison["validation_sha256"] = file_hash(path)
        atomic_json(root / "comparison.json", comparison)
        readiness["evidence"]["comparison"]["sha256"] = file_hash(root / "comparison.json")
    elif mutation.startswith("comparison_"):
        path = root / "comparison.json"
        doc = read_json(path)
        if mutation == "comparison_count":
            doc["n_complete"] = 20
        elif mutation == "comparison_identity":
            doc["compared_repo_ids"][-1] = 99
        else:
            doc["failures"] = []
        atomic_json(path, doc)
        readiness["evidence"]["comparison"]["sha256"] = file_hash(path)
    atomic_json(root / "readiness.json", readiness)
    with pytest.raises((ValueError, AssertionError)):
        real_run_gate(**ready)

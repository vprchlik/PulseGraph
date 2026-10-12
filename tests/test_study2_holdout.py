from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json
from pulsegraph.study2.constants import PROTOCOL_COMMIT, PROTOCOL_SHA256, VARIANTS
from pulsegraph.study2.holdout import (
    _write_predictions,
    prepare_plan,
    settlement_attempts,
    verify_predictions,
)


def test_study2_identity_is_separate():
    import subprocess

    from pulsegraph.config import ROOT_DIR
    from pulsegraph.provenance import sha256_bytes

    blob = subprocess.check_output(["git", "show", f"{PROTOCOL_COMMIT}:PROTOCOL.md"], cwd=ROOT_DIR)
    assert sha256_bytes(blob) == PROTOCOL_SHA256
    assert (ROOT_DIR / "PROTOCOL.md").read_bytes().startswith(blob)


@pytest.fixture
def holdout(tmp_path, monkeypatch):
    def entry(path):
        return dict(path=str(path), sha256=file_hash(path))

    manifest = tmp_path / "manifest.json"
    atomic_json(manifest, [dict(repo_id=i, creation_date="2025-09-01") for i in range(300)])
    monkeypatch.setattr("pulsegraph.study2.holdout.GITHUB_MANIFEST_SHA256", file_hash(manifest))
    signals = tmp_path / "signals.parquet"
    pd.DataFrame(
        [(str(i), d, i % 3) for i in range(300) for d in pd.date_range("2025-09-01", "2026-09-27")],
        columns=["series_id", "date", "count"],
    ).to_parquet(signals, index=False)
    evidence = tmp_path / "evidence.json"
    response = tmp_path / "response.json"
    atomic_json(response, {"fixture": "synthetic only"})
    atomic_json(
        evidence,
        dict(
            calendar="America/Los_Angeles",
            verified=True,
            verified_at="2026-09-28T16:00:00Z",
            last_complete_day="2026-09-27",
            method="synthetic complete enumeration",
            response_evidence=[entry(response)],
            signals_sha256=file_hash(signals),
        ),
    )
    timing = tmp_path / "timing.json"
    from pulsegraph.study2.constants import BASELINES, MODEL_PINS

    atomic_json(
        timing,
        dict(
            data_kind="synthetic",
            passed=True,
            per_model={
                n: dict(load_seconds=1, forecast_seconds=0.01, context_days=400, leads=33)
                for n in (*MODEL_PINS, *BASELINES)
            },
        ),
    )
    now = datetime(2026, 9, 28, 17, tzinfo=timezone.utc)
    source = dict(
        domain="github",
        manifest=entry(manifest),
        signals=entry(signals),
        completeness=entry(evidence),
    )
    plan = prepare_plan(
        [source], entry(timing), npm_unavailable_reason="not verified by deadline", now=now
    )
    return plan, now


def test_bridge_plan_and_settlement(holdout):
    plan, _ = holdout
    assert plan["comparison_count"] == 9
    assert plan["source_details"]["github"]["bridge_days"] == 3
    assert plan["source_details"]["github"]["forecast_leads"] == 33
    assert len(settlement_attempts(30)) == 7


def test_deadline_and_checkpoint_resume(holdout, tmp_path):
    plan, now = holdout
    calls = []

    def predict(context, leads, label):
        calls.append(label)
        if label == "github:1" and len(calls) == 2:
            raise RuntimeError("synthetic failure")
        return {n: dict(deciles=np.zeros((leads, 9)).tolist()) for n in VARIANTS}

    out = tmp_path / "out"
    with pytest.raises(RuntimeError):
        _write_predictions(plan, out, predict, clock=lambda: now)
    assert len(read_json(out / "freeze.json")["completed"]) == 1
    state = _write_predictions(plan, out, predict, clock=lambda: now)
    assert state["status"] == "complete" and len(state["completed"]) == 300
    assert calls.count("github:0") == 1 and len(state["resumes"]) == 1
    assert verify_predictions(out)["series"] == 300
    (out / "context-github-signals.parquet").write_bytes(b"changed")
    with pytest.raises(ValueError, match="context hash"):
        verify_predictions(out)
    late = datetime(2026, 9, 28, 18, 0, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="deadline"):
        _write_predictions(plan, tmp_path / "late", predict, clock=lambda: late)


def test_context_and_evidence_tampering_fail(holdout):
    plan, now = holdout
    path = plan["sources"][0]["signals"]["path"]
    with open(path, "ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="hash"):
        prepare_plan(plan["sources"], plan["timing_evidence"], now=now)

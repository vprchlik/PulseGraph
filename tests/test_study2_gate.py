from copy import deepcopy
from datetime import datetime, timezone

import pytest

from pulsegraph.config import ROOT_DIR
from pulsegraph.provenance import read_json
from pulsegraph.study2.declarations import comparisons, specification, validate
from pulsegraph.study2.gate import authorize_holdout


@pytest.mark.parametrize(
    "component,count",
    [("external", 54), ("external_packages", 18), ("synthetic", 6), ("holdout", 18)],
)
def test_full_families_match_protocol_tables_and_committed_json(component, count):
    family = comparisons(component)
    assert len(family["comparisons"]) == count
    assert family == read_json(ROOT_DIR / f"study/study2/{component}_comparisons.json")
    assert specification(component) == read_json(ROOT_DIR / f"study/study2/{component}_spec.json")
    protocol = (ROOT_DIR / "PROTOCOL.md").read_text(encoding="utf-8")
    for row in family["comparisons"]:
        assert (
            f"| {row['id']} | {row['domain']} | {row['model']} | "
            f"{row['reference']} | {row['horizon']} |" in protocol
        )
    assert validate(specification(component), family) == component


@pytest.mark.parametrize(
    "field", ["seeds", "foundation_models", "comparison_count", "calendar", "crps", "variants"]
)
def test_gate_rejects_any_changed_declaration(field):
    spec = deepcopy(specification("external"))
    spec[field] = None
    with pytest.raises(ValueError, match="declaration"):
        validate(spec, comparisons("external"))


def test_missing_or_late_freeze_approval_precedes_all_file_and_gpu_access(tmp_path):
    with pytest.raises(ValueError, match="confirm"):
        authorize_holdout(
            tmp_path / "no-plan", None, now=datetime(2026, 9, 14, tzinfo=timezone.utc)
        )
    with pytest.raises(ValueError, match="deadline"):
        authorize_holdout(
            tmp_path / "no-plan",
            tmp_path / "no-approval",
            now=datetime(2026, 9, 29, tzinfo=timezone.utc),
        )


def test_family_cannot_be_reduced_or_duplicated():
    for mutation in ("duplicate", "drop", "count"):
        family = comparisons("holdout")
        if mutation == "duplicate":
            family["comparisons"][0] = family["comparisons"][1]
        elif mutation == "drop":
            family["comparisons"] = family["comparisons"][:9]
        else:
            family["comparison_count"] = 9
        with pytest.raises(ValueError):
            validate(specification("holdout"), family)


def test_registration_checks_the_study2_blob_and_clean_sources(tmp_path, monkeypatch):
    import subprocess

    from pulsegraph.study2.constants import PROTOCOL_COMMIT
    from pulsegraph.study2.gate import verify_registration

    blob = subprocess.check_output(["git", "show", f"{PROTOCOL_COMMIT}:PROTOCOL.md"], cwd=ROOT_DIR)
    (tmp_path / "PROTOCOL.md").write_bytes(blob + b"\nDated appendix\n")
    (tmp_path / "pyproject.toml").write_text("")
    implementation = "a" * 40
    dirty = []

    def git(root, *args):
        if args[0] == "show":
            assert args[1] == f"{PROTOCOL_COMMIT}:PROTOCOL.md"
            return blob
        if args[0] == "status":
            return b"?? new-source.py" if dirty else b""
        return implementation.encode()

    monkeypatch.setattr("pulsegraph.study2.gate.git", git)
    assert "PROTOCOL.md" in verify_registration(implementation, root=tmp_path)
    dirty.append(True)
    with pytest.raises(ValueError, match="clean"):
        verify_registration(implementation, root=tmp_path)
    dirty.clear()
    (tmp_path / "PROTOCOL.md").write_bytes(b"X" + blob[1:])
    with pytest.raises(ValueError, match="registration bytes"):
        verify_registration(implementation, root=tmp_path)


def test_study2_runner_preserves_cutoffs_and_resumes_whole_entities(tmp_path):
    import numpy as np
    import pandas as pd

    from pulsegraph.study2.constants import VARIANTS
    from pulsegraph.study2.runner import _evaluate

    series = pd.Series(np.ones(365), index=pd.date_range("2025-09-01", "2026-08-31"))
    dataset = {("packages", key): series for key in ("a", "b")}

    class Pool:
        calls = []
        failed = False

        def forecast(self, context, horizon, key):
            self.calls.append((key, len(context), horizon))
            assert len(context) in (275, 305, 335)
            if '"b"' in key and not self.failed:
                self.failed = True
                raise RuntimeError("synthetic failure")
            return {
                n: dict(deciles=np.zeros((horizon, 9)).tolist(), distributions=None)
                for n in VARIANTS
            }

    pool = Pool()
    with pytest.raises(RuntimeError):
        _evaluate(dataset, tmp_path, pool, metadata={"fixture": True})
    state = _evaluate(dataset, tmp_path, pool, metadata={"fixture": True})
    assert len(state["completed"]) == 2 and len(state["resumes"]) == 1
    assert sum('"a"' in c[0] for c in pool.calls) == 6


def _run_metadata(free, *, hardware=None, **changes):
    """Run metadata as the run entry point builds it, with the free GPU memory of one invocation."""
    gpu = dict(
        gpu_model="NVIDIA GeForce RTX 4070 SUPER",
        gpu_driver="580.97",
        cuda_version="12.8",
        pytorch_version="2.11.0+cu128",
        platform="Windows-11-10.0.26200-SP0",
        gpu_total_bytes=12_878_086_144,
        gpu_free_at_start_bytes=free,
        allocator_limit_bytes=min(7_000_000_000, free - 1_000_000_000),
        peak_vram_limit_bytes=8_000_000_000,
        batch_size=1,
    )
    gpu.update(hardware or {})
    metadata = dict(
        readiness=dict(action="external_packages"),
        spec=specification("external_packages"),
        family=comparisons("external_packages"),
        metadata=dict(implementation_commit="a" * 40, smoke_sha256="b" * 64),
        readiness_sha256="c" * 64,
        hardware=gpu,
    )
    metadata.update(changes)
    return metadata


class _StoppingPool:
    """Stops once on series b, then forecasts; records each call's timings like ModelPool."""

    def __init__(self):
        self.stopped, self.timings = False, {}

    def forecast(self, context, horizon, key):
        import numpy as np

        from pulsegraph.study2.constants import VARIANTS

        if '"b"' in key and not self.stopped:
            self.stopped = True
            raise RuntimeError("stopped")
        self.timings = {"timesfm3": dict(load_seconds=0.0, forecast_seconds=0.5)}
        return {
            n: dict(deciles=np.zeros((horizon, 9)).tolist(), distributions=None) for n in VARIANTS
        }


def _two_series():
    import numpy as np
    import pandas as pd

    series = pd.Series(np.ones(365), index=pd.date_range("2025-09-01", "2026-08-31"))
    return {("packages", key): series for key in ("a", "b")}


def test_resume_takes_new_free_gpu_memory_and_refuses_a_changed_declaration(tmp_path):
    from pulsegraph.study2.runner import _evaluate, resume_identity

    dataset, pool, run = _two_series(), _StoppingPool(), tmp_path / "run"
    with pytest.raises(RuntimeError, match="stopped"):
        _evaluate(dataset, run, pool, metadata=_run_metadata(11_400_000_000))
    stopped = read_json(run / "run.json")
    assert stopped["status"] == "failed" and len(stopped["completed"]) == 1
    assert resume_identity(_run_metadata(11_400_000_000)) == resume_identity(
        _run_metadata(9_100_000_000)
    )
    family = dict(comparisons("external_packages"), comparison_count=17)
    for changed in (
        _run_metadata(9_100_000_000, family=family),
        _run_metadata(9_100_000_000, spec=specification("external")),
        _run_metadata(9_100_000_000, readiness_sha256="d" * 64),
        _run_metadata(9_100_000_000, metadata=dict(implementation_commit="e" * 40)),
        _run_metadata(9_100_000_000, hardware=dict(gpu_driver="581.15")),
        _run_metadata(9_100_000_000, hardware=dict(gpu_model="NVIDIA GeForce RTX 4090")),
    ):
        with pytest.raises(ValueError, match="changed resume identity"):
            _evaluate(dataset, run, pool, metadata=changed)
        assert read_json(run / "run.json") == stopped
    state = _evaluate(dataset, run, pool, metadata=_run_metadata(9_100_000_000))
    assert state["status"] == "complete" and len(state["completed"]) == 2
    assert len(state["resumes"]) == 1 and len(state["failures"]) == 1
    assert [i["hardware"]["gpu_free_at_start_bytes"] for i in state["invocations"]] == [
        11_400_000_000,
        9_100_000_000,
    ]
    assert state["metadata"] == _run_metadata(11_400_000_000)
    with pytest.raises(ValueError, match="Immutable completed run"):
        _evaluate(dataset, run, pool, metadata=_run_metadata(9_100_000_000))


def test_each_invocation_records_its_timings_and_final_memory_snapshot(tmp_path):
    from pulsegraph.study2.runner import _evaluate

    dataset, pool, run = _two_series(), _StoppingPool(), tmp_path / "run"
    snapshots = iter([dict(peak_reserved_bytes=2_948_595_712)])

    def broken():
        raise RuntimeError("CUDA context lost")

    with pytest.raises(RuntimeError, match="stopped"):
        _evaluate(dataset, run, pool, metadata={"fixture": True}, memory=lambda: next(snapshots))
    state = _evaluate(dataset, run, pool, metadata={"fixture": True}, memory=broken)
    first, second = state["invocations"]
    assert first["memory"] == dict(peak_reserved_bytes=2_948_595_712)
    assert second["memory"] == dict(unavailable="RuntimeError: CUDA context lost")
    # Series a's six windows in the first invocation; series b's six in the resume.
    for invocation in (first, second):
        assert invocation["series_completed"] == 1
        assert invocation["timings"]["timesfm3"] == dict(
            calls=6, load_seconds=0.0, forecast_seconds=3.0, max_forecast_seconds=0.5
        )
    assert read_json(run / "run.json") == state

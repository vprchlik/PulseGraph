from copy import deepcopy
from datetime import datetime, timezone

import pytest

from pulsegraph.config import ROOT_DIR
from pulsegraph.provenance import read_json
from pulsegraph.study2.declarations import comparisons, specification, validate
from pulsegraph.study2.gate import authorize_holdout


@pytest.mark.parametrize("component,count", [("external", 54), ("synthetic", 6), ("holdout", 18)])
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

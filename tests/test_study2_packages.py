"""The packages-only external component of the dated addition of 2026-10-12 and its target pull."""

import json
import re
import subprocess
from datetime import datetime, timezone
from types import SimpleNamespace
from urllib.parse import unquote

import numpy as np
import pandas as pd
import pytest
import requests

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes
from pulsegraph.study2.constants import (
    CONTEXT_END,
    CONTEXT_START,
    PROTOCOL_COMMIT,
    PROTOCOL_SHA256,
    SEEDS,
    VARIANTS,
)
from pulsegraph.study2.declarations import (
    PACKAGES_AUTHORITY,
    comparisons,
    specification,
    validate,
)
from pulsegraph.study2.gate import ADDITION_HEADING, authorize_component
from pulsegraph.study2.ingestion import (
    TARGET_END,
    TARGET_START,
    CaptureClient,
    NpmSource,
    SourceFailure,
    context_days,
    pull_targets,
)
from pulsegraph.study2.runner import external_dataset

NOW = datetime(2026, 10, 16, tzinfo=timezone.utc)
HEAD = "a" * 40
DOWNLOADS = "https://api.npmjs.org/downloads/range/"
SERIES = ["p0", "@s/q0", "p1", "p2"]
PINS = {
    "timesfm": "3.0.2",
    "statsforecast": "2.1.1",
    "torch": "2.11.0+cu128",
    "chronos-forecasting": "2.2.0",
    "scipy": "1.16.0",
    "numpy": "2.3.0",
    "pandas": "2.3.0",
}


def _entry(path, value):
    atomic_json(path, value)
    return dict(path=str(path), sha256=file_hash(path))


class Repository:
    """A clean checkout at HEAD carrying the addition, with a current smoke and a frozen panel."""

    def __init__(self, root, monkeypatch):
        self.root, self.dirty, self.ancestor = root, False, True
        self.blob = subprocess.check_output(
            ["git", "show", f"{PROTOCOL_COMMIT}:PROTOCOL.md"], cwd=ROOT_DIR
        )
        self.added = self.blob + f"\n{ADDITION_HEADING}\n\nItems 1 to 3.\n".encode()
        self.current = self.added
        (root / "PROTOCOL.md").write_bytes(self.current)
        (root / "pyproject.toml").write_text("")
        (root / "tests").mkdir()
        sources = {}
        for name in (
            "pulsegraph/study2/distributions.py",
            "pulsegraph/study2/scores.py",
            "scripts/study2_run.py",
        ):
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(f"# {name}\n")
            sources[name] = file_hash(root / name)
        study = root / "study/study2"
        for component in ("external", "external_packages"):
            atomic_json(study / f"{component}_spec.json", specification(component))
            atomic_json(study / f"{component}_comparisons.json", comparisons(component))
        atomic_json(
            study / "crps_resolution.json",
            dict(
                passed=True,
                crps=dict(tolerance=1e-8, max_k=1000000, maximum_residual_bound=1e-12),
                source_sha256={k: v for k, v in sources.items() if k.startswith("pulsegraph")},
            ),
        )
        self.sources = sources
        self.smoke = self.write_smoke()
        self.panel = self.write_panel(root / "panel")
        atomic_json(study / "npm_panel_status.json", dict(panel=self.panel))
        monkeypatch.setattr("pulsegraph.study2.gate.git", self.git)
        monkeypatch.setattr("pulsegraph.study2.gate.installed_versions", lambda: dict(PINS))

    def write_smoke(self, **changes):
        smoke = dict(
            passed=True,
            data_kind="synthetic",
            implementation_commit=HEAD,
            protocol_commit=PROTOCOL_COMMIT,
            protocol_sha256=PROTOCOL_SHA256,
            seeds=SEEDS,
            variants=list(VARIANTS),
            source_sha256=dict(self.sources),
            packages=dict(PINS),
            memory=dict(peak_reserved_bytes=2948595712),
            hardware=dict(gpu_model="NVIDIA GeForce RTX 4070 SUPER"),
        )
        smoke.update(changes)
        smokes = len(list((self.root / "evidence").glob("smoke-*.json")))
        return _entry(self.root / f"evidence/smoke-{smokes}.json", smoke)

    @staticmethod
    def write_panel(directory):
        dates = pd.date_range(CONTEXT_START, CONTEXT_END)
        frames = [
            context_days(
                [
                    dict(date=day.date().isoformat(), count=(j + i) % 3)
                    for j, day in enumerate(dates)
                ]
            ).assign(series_id=key)
            for i, key in enumerate(SERIES)
        ]
        directory.mkdir(parents=True)
        pd.concat(frames, ignore_index=True).to_parquet(directory / "context.parquet", index=False)
        context = dict(path=str(directory / "context.parquet"))
        context["sha256"] = file_hash(directory / "context.parquet")
        selection = _entry(directory / "selection.json", dict(report={}, reserve_order=[]))
        manifest = _entry(
            directory / "manifest.json",
            dict(
                domain="npm",
                series=[dict(series_id=key) for key in SERIES],
                context_sha256=context["sha256"],
                selection_sha256=selection["sha256"],
            ),
        )
        return dict(manifest=manifest, selection=selection, context=context)

    def git(self, root, *args):
        if args[0] == "rev-parse":
            return HEAD.encode() + b"\n"
        if args[0] == "status":
            return b"?? stray.py\n" if self.dirty else b""
        if args[0] == "merge-base":
            if not self.ancestor:
                raise subprocess.CalledProcessError(1, "git")
            return b""
        return {
            f"{PROTOCOL_COMMIT}:PROTOCOL.md": self.blob,
            f"{PACKAGES_AUTHORITY['commit']}:PROTOCOL.md": self.added,
            "HEAD:PROTOCOL.md": self.current,
        }[args[1]]

    def readiness(self, **changes):
        document = dict(
            action="external_packages",
            approved_at="2026-10-15T12:00:00+00:00",
            approved_by="The author",
            confirmed=True,
            estimated_seconds=100,
            runtime_budget_seconds=200,
            evidence=[self.panel["manifest"]],
            implementation_commit=HEAD,
            package_domain="npm",
            panels=dict(packages=dict(self.panel)),
            protocol_commit=PROTOCOL_COMMIT,
            protocol_sha256=PROTOCOL_SHA256,
            smoke=self.smoke,
            source_semantics_resolved=True,
            target_access_approved=True,
        )
        document.update(changes)
        path = self.root / "readiness.json"
        atomic_json(path, document)
        return path


class TargetSession:
    """The download API over the fixture panel; a package named in `faults` fails that way."""

    def __init__(self, faults=None):
        self.faults, self.headers, self.requests = dict(faults or {}), {}, []

    def get(self, url, params=None, timeout=None, allow_redirects=None):
        self.requests.append(url)
        period, quoted = url[len(DOWNLOADS) :].split("/", 1)
        start, end = period.split(":")
        name, fault = unquote(quoted), self.faults.get(unquote(quoted))
        if fault == "transport_failure":
            raise requests.ConnectionError("connection reset")
        if fault == "http_404":
            return SimpleNamespace(status_code=404, content=b"{}", headers={})
        downloads = [
            dict(day=day.date().isoformat(), downloads=(7 * i + len(name)) % 5)
            for i, day in enumerate(pd.date_range(start, end))
        ]
        if fault == "missing_target_day":
            downloads = downloads[:40] + downloads[41:]
        body = dict(package=name, start=start, end=end, downloads=downloads)
        return SimpleNamespace(status_code=200, content=json.dumps(body).encode(), headers={})


@pytest.fixture
def repository(tmp_path, monkeypatch):
    return Repository(tmp_path, monkeypatch)


def _source(repository, session):
    client = CaptureClient(
        repository.root / "targets/captures",
        session=session,
        sleep=lambda seconds: None,
        root=repository.root,
    )
    return NpmSource(client)


def test_packages_family_is_e01_to_e18_cited_to_the_addition():
    family, full = comparisons("external_packages"), comparisons("external")
    assert [row["id"] for row in family["comparisons"]] == [f"E{i:02}" for i in range(1, 19)]
    assert family["comparisons"] == full["comparisons"][:18]
    assert {row["domain"] for row in family["comparisons"]} == {"packages"}
    assert family["comparison_count"] == 18 and full["comparison_count"] == 54
    assert family["authority"] == dict(
        addition="PROTOCOL.md, dated addition of 2026-10-12, item 3",
        commit="8db0d73381e89a61b0ea22e6a8cb2b6e569725c9",
    )
    shared = ("adjustment", "q", "test", "bootstrap_replicates", "bootstrap_seed", "metric")
    assert all(family[key] == full[key] for key in shared)
    spec = specification("external_packages")
    assert spec["comparison_count"] == 18 and spec["component"] == "external_packages"
    assert {k: v for k, v in spec.items() if k not in ("component", "comparison_count")} == {
        k: v
        for k, v in specification("external").items()
        if k not in ("component", "comparison_count")
    }
    assert validate(spec, family) == "external_packages"
    assert validate(specification("external"), full) == "external"
    for wrong in (
        dict(family, comparisons=full["comparisons"][:17], comparison_count=17),
        dict(family, comparisons=full["comparisons"][18:36]),
        dict(family, authority=None),
        full,
    ):
        with pytest.raises(ValueError, match="declaration"):
            validate(spec, wrong)
    with pytest.raises(ValueError, match="declaration"):
        validate(specification("external"), family)


def test_gate_accepts_packages_only_readiness_without_a_holdout_freeze(repository):
    readiness = repository.readiness()
    assert "holdout_freeze" not in read_json(readiness)
    result = authorize_component(readiness, "external_packages", root=repository.root, now=NOW)
    assert result["family"]["comparison_count"] == 18
    assert result["metadata"]["authority"] == dict(
        addition="PROTOCOL.md, dated addition of 2026-10-12, items 1 and 3",
        addition_commit=PACKAGES_AUTHORITY["commit"],
        addition_protocol_sha256=sha256_bytes(repository.added),
        protocol_sha256_at_head=sha256_bytes(repository.current),
    )
    assert result["metadata"]["implementation_commit"] == HEAD


def test_gate_rejects_packages_only_readiness_for_the_registered_external_component(repository):
    with pytest.raises(ValueError, match="signed author approval"):
        authorize_component(repository.readiness(), "external", root=repository.root, now=NOW)
    readiness = repository.readiness(action="external")
    with pytest.raises(ValueError, match="All three external domain slots"):
        authorize_component(readiness, "external", root=repository.root, now=NOW)


@pytest.mark.parametrize(
    "changes,message",
    [
        (dict(confirmed=False), "signed author approval"),
        (dict(approved_by=None), "signed author approval"),
        (dict(approved_at="2026-10-17T00:00:00+00:00"), "future"),
        (dict(protocol_commit=HEAD), "bound to Study 2"),
        (dict(target_access_approved=False), "approved separately"),
        (dict(package_domain="pypi"), "frozen npm panel"),
        (dict(runtime_budget_seconds=50), "budget"),
        (dict(evidence=[]), "evidence"),
    ],
)
def test_gate_rejects_unsigned_or_unbounded_readiness(repository, changes, message):
    readiness = repository.readiness(**changes)
    with pytest.raises(ValueError, match=message):
        authorize_component(readiness, "external_packages", root=repository.root, now=NOW)


def test_gate_takes_only_the_frozen_npm_panel(repository):
    panels = dict(packages=repository.panel, nyc311=repository.panel)
    with pytest.raises(ValueError, match="packages panel alone"):
        authorize_component(
            repository.readiness(panels=panels), "external_packages", root=repository.root, now=NOW
        )
    for name in ("manifest", "selection", "context"):
        changed = repository.root / f"changed-{name}.json"
        atomic_json(changed, dict(changed=name))
        for entry, message in (
            (dict(path=str(changed), sha256=file_hash(changed)), "frozen npm panel"),
            (dict(repository.panel[name], path=str(changed)), "Evidence hash mismatch"),
        ):
            panel = dict(repository.panel, **{name: entry})
            readiness = repository.readiness(panels=dict(packages=panel))
            with pytest.raises(ValueError, match=message):
                authorize_component(readiness, "external_packages", root=repository.root, now=NOW)


def test_gate_rejects_a_stale_smoke_and_a_dirty_tree(repository):
    for smoke in (
        repository.write_smoke(implementation_commit="b" * 40),
        repository.write_smoke(
            source_sha256=dict(repository.sources, **{"scripts/study2_run.py": "0" * 64})
        ),
    ):
        readiness = repository.readiness(smoke=smoke)
        with pytest.raises(ValueError, match="(?i)smoke"):
            authorize_component(readiness, "external_packages", root=repository.root, now=NOW)
    readiness = repository.readiness(smoke=repository.write_smoke())
    repository.dirty = True
    with pytest.raises(ValueError, match="committed and clean"):
        authorize_component(readiness, "external_packages", root=repository.root, now=NOW)


def test_gate_requires_the_committed_addition_at_head(repository):
    readiness = repository.readiness()
    repository.ancestor = False
    with pytest.raises(ValueError, match="history of HEAD"):
        authorize_component(readiness, "external_packages", root=repository.root, now=NOW)
    repository.ancestor = True
    repository.added = repository.blob
    with pytest.raises(ValueError, match="dated addition"):
        authorize_component(readiness, "external_packages", root=repository.root, now=NOW)


def test_target_pull_opens_only_the_window_for_the_manifest_and_joins_the_frozen_context(
    repository,
):
    session = TargetSession()
    readiness = repository.readiness()
    output = repository.root / "targets"
    document = pull_targets(
        readiness, _source(repository, session), output, root=repository.root, now=NOW
    )
    assert len(session.requests) == len(SERIES)
    assert [unquote(url.rsplit("/", 1)[1]) for url in session.requests] == SERIES
    assert DOWNLOADS + "2026-06-03:2026-08-31/@s%2Fq0" in session.requests
    dates = re.findall(r"\d{4}-\d{2}-\d{2}", " ".join(session.requests))
    assert set(dates) == {TARGET_START, TARGET_END} == {"2026-06-03", "2026-08-31"}
    signals = pd.read_parquet(output / "signals.parquet")
    assert list(signals.columns) == ["series_id", "date", "count"]
    assert signals.groupby("series_id").size().to_dict() == {key: 365 for key in SERIES}
    assert signals.date.min() == pd.Timestamp(CONTEXT_START)
    assert signals.date.max() == pd.Timestamp("2026-08-31")
    assert document["calendar"] == "UTC" and document["verified"] is True and document["method"]
    assert document["last_complete_day"] == "2026-08-31" and document["series"] == len(SERIES)
    assert document["signals_sha256"] == file_hash(output / "signals.parquet")
    assert document["ledger_failures"] == []
    assert len(document["response_evidence"]) == len(SERIES)
    for entry in document["response_evidence"]:
        assert file_hash(repository.root / entry["path"]) == entry["sha256"]
    assert read_json(output / "completeness.json") == document
    ledger = read_json(output / "pull.json")
    assert [i["status"] for i in ledger["invocations"]] == ["complete"]
    assert ledger["invocations"][0]["attempts"] == len(SERIES)
    panel = dict(
        repository.panel,
        signals=dict(path=str(output / "signals.parquet"), sha256=document["signals_sha256"]),
        completeness=dict(
            path=str(output / "completeness.json"), sha256=file_hash(output / "completeness.json")
        ),
    )
    dataset = external_dataset(
        dict(package_domain="npm", panels=dict(packages=panel)), root=repository.root
    )
    assert sorted(dataset) == sorted(("packages", key) for key in SERIES)
    assert all(len(series) == 365 for series in dataset.values())
    with pytest.raises(FileExistsError):
        pull_targets(readiness, _source(repository, session), output, root=repository.root, now=NOW)
    assert len(session.requests) == len(SERIES)


@pytest.mark.parametrize(
    "changes,message",
    [
        (dict(target_access_approved=False), "approved separately"),
        (dict(confirmed=False), "signed author approval"),
        (dict(action="external"), "signed author approval"),
    ],
)
def test_target_pull_refuses_without_the_signed_target_approval(repository, changes, message):
    session = TargetSession()
    with pytest.raises(ValueError, match=message):
        pull_targets(
            repository.readiness(**changes),
            _source(repository, session),
            repository.root / "targets/out",
            root=repository.root,
            now=NOW,
        )
    assert session.requests == [] and not (repository.root / "targets/out").exists()


def test_target_pull_refuses_a_manifest_other_than_the_frozen_one(repository):
    session = TargetSession()
    other = repository.root / "other-manifest.json"
    atomic_json(other, dict(domain="npm", series=[dict(series_id="p9")]))
    for manifest, message in (
        (dict(path=str(other), sha256=file_hash(other)), "frozen npm panel"),
        (dict(repository.panel["manifest"], path=str(other)), "Evidence hash mismatch"),
    ):
        panels = dict(packages=dict(repository.panel, manifest=manifest))
        with pytest.raises(ValueError, match=message):
            pull_targets(
                repository.readiness(panels=panels),
                _source(repository, session),
                repository.root / "out",
                root=repository.root,
                now=NOW,
            )
    assert session.requests == [] and not (repository.root / "out").exists()


def test_target_pull_refuses_when_the_full_gate_fails(repository):
    session = TargetSession()
    readiness = repository.readiness()
    repository.dirty = True
    with pytest.raises(ValueError, match="committed and clean"):
        pull_targets(
            readiness,
            _source(repository, session),
            repository.root / "out",
            root=repository.root,
            now=NOW,
        )
    assert session.requests == []


def test_target_requests_never_leave_the_window_or_the_authorized_manifest(repository):
    source = _source(repository, TargetSession())
    with pytest.raises(ValueError, match="frozen npm manifest"):
        source.targets(dict(series_id="p0"), TARGET_START, TARGET_END)
    source.target_series = frozenset(SERIES)
    for start, end in (
        (CONTEXT_START, TARGET_END),
        ("2026-06-02", TARGET_END),
        (TARGET_START, "2026-09-01"),
        (TARGET_START, "2026-08-30"),
    ):
        with pytest.raises(ValueError, match="exactly 2026-06-03 to 2026-08-31"):
            source.targets(dict(series_id="p0"), start, end)
    with pytest.raises(ValueError, match="target days"):
        source.context(dict(series_id="p0"), CONTEXT_START, TARGET_END)
    assert source.client.session.requests == []


@pytest.mark.parametrize("fault", ["missing_target_day", "http_404"])
def test_an_incomplete_target_range_is_recorded_and_stops_the_domain(repository, fault):
    readiness, output = repository.readiness(), repository.root / "targets"
    session = TargetSession({SERIES[2]: fault})
    with pytest.raises(SourceFailure, match=fault):
        pull_targets(readiness, _source(repository, session), output, root=repository.root, now=NOW)
    assert len(session.requests) == 3
    assert not (output / "signals.parquet").exists() and not (output / "completeness.json").exists()
    ledger = read_json(output / "pull.json")
    failure = dict(ledger["failures"][0])
    failure.pop("at")
    assert failure == dict(series_id=SERIES[2], position=2, reason=fault, kind="series")
    assert ledger["invocations"][0]["answered"] == 2
    if fault == "missing_target_day":
        # The saved answer is the source snapshot: a resume reads it again, never replaces it.
        session = TargetSession()
        with pytest.raises(SourceFailure, match=fault):
            pull_targets(
                readiness, _source(repository, session), output, root=repository.root, now=NOW
            )
        assert session.requests == []
        assert len(read_json(output / "pull.json")["failures"]) == 2


def test_a_target_outage_stops_the_pull_and_resumes_from_captures(repository):
    readiness, output = repository.readiness(), repository.root / "targets"
    session = TargetSession({SERIES[2]: "transport_failure"})
    with pytest.raises(SourceFailure, match="transport_failure"):
        pull_targets(readiness, _source(repository, session), output, root=repository.root, now=NOW)
    assert read_json(output / "pull.json")["failures"][0]["kind"] == "outage"
    session = TargetSession()
    document = pull_targets(
        readiness, _source(repository, session), output, root=repository.root, now=NOW
    )
    assert [unquote(url.rsplit("/", 1)[1]) for url in session.requests] == SERIES[2:]
    assert len(document["response_evidence"]) == len(SERIES)
    assert [f["kind"] for f in document["ledger_failures"]] == ["outage"]
    statuses = [i["status"] for i in read_json(output / "pull.json")["invocations"]]
    assert statuses == ["SourceFailure", "complete"]


def _pull(repository):
    """The fixture pull with string paths, as the command line passes them."""
    output = repository.root / "targets"
    document = pull_targets(
        str(repository.readiness()),
        _source(repository, TargetSession()),
        str(output),
        root=repository.root,
        now=NOW,
    )
    panel = dict(
        repository.panel,
        signals=dict(path=str(output / "signals.parquet"), sha256=document["signals_sha256"]),
        completeness=dict(
            path=str(output / "completeness.json"), sha256=file_hash(output / "completeness.json")
        ),
    )
    return output, document, panel


def _completeness(output, **changes):
    document = dict(read_json(output / "completeness.json"), **changes)
    path = output / f"completeness-{len(list(output.glob('completeness-*.json')))}.json"
    return _entry(path, document)


def test_target_pull_takes_the_readiness_and_output_as_strings(repository):
    output, document, _ = _pull(repository)
    ledger = read_json(output / "pull.json")
    assert ledger["invocations"][0]["readiness_sha256"] == file_hash(
        repository.root / "readiness.json"
    )
    assert document["signals_sha256"] == file_hash(output / "signals.parquet")


def test_run_entry_point_takes_string_paths_and_records_timings_and_memory(repository, monkeypatch):
    import functools
    import sys

    import scripts.study2_run as study2_run

    _, _, panel = _pull(repository)
    readiness = repository.readiness(panels=dict(packages=panel))
    calls = []

    class Pool:
        timings = {}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def forecast(self, context, horizon, key):
            calls.append(key)
            self.timings = {
                name: dict(load_seconds=0.5 if not calls[:-1] else 0.0, forecast_seconds=0.25)
                for name in ("chronos2", "poisson_28")
            }
            return {
                n: dict(deciles=np.zeros((horizon, 9)).tolist(), distributions=None)
                for n in VARIANTS
            }

    gate = functools.partial(authorize_component, root=repository.root, now=NOW)
    monkeypatch.setattr(study2_run, "authorize_component", gate)
    monkeypatch.setattr(
        study2_run, "external_dataset", functools.partial(external_dataset, root=repository.root)
    )
    hardware = dict(
        gpu_model="NVIDIA GeForce RTX 4070 SUPER",
        gpu_free_at_start_bytes=11_000_000_000,
        allocator_limit_bytes=7_000_000_000,
    )
    monkeypatch.setattr(study2_run, "configure_gpu", lambda: dict(hardware))
    snapshot = dict(peak_allocated_bytes=2_000_000_000, peak_reserved_bytes=2_900_000_000)
    monkeypatch.setattr(study2_run, "memory_snapshot", lambda: dict(snapshot))
    monkeypatch.setattr(study2_run, "ModelPool", Pool)
    run = repository.root / "run"
    argv = ["study2_run.py", "external_packages", "--readiness", str(readiness), "--out", str(run)]
    monkeypatch.setattr(sys, "argv", argv)
    study2_run.main()
    state = read_json(run / "run.json")
    assert state["status"] == "complete" and len(state["completed"]) == len(SERIES)
    assert state["metadata"]["readiness_sha256"] == file_hash(readiness)
    assert len(calls) == len(SERIES) * 3 * 2
    (invocation,) = state["invocations"]
    assert invocation["memory"] == snapshot and invocation["series_completed"] == len(SERIES)
    assert invocation["hardware"] == dict(
        gpu_free_at_start_bytes=11_000_000_000, allocator_limit_bytes=7_000_000_000
    )
    assert invocation["timings"]["chronos2"] == dict(
        calls=len(calls),
        load_seconds=0.5,
        forecast_seconds=0.25 * len(calls),
        max_forecast_seconds=0.25,
    )
    assert invocation["wall_seconds"] >= 0 and invocation["ended_at"]


def test_gate_admits_target_signals_only_with_their_completeness_document(repository):
    output, _, panel = _pull(repository)
    for changed in (
        panel,
        {k: v for k, v in panel.items() if k not in ("signals", "completeness")},
    ):
        result = authorize_component(
            repository.readiness(panels=dict(packages=changed)),
            "external_packages",
            root=repository.root,
            now=NOW,
        )
        assert result["family"]["comparison_count"] == 18
    for changed, message in (
        ({k: v for k, v in panel.items() if k != "completeness"}, "completeness document"),
        ({k: v for k, v in panel.items() if k != "signals"}, "completeness document"),
        (dict(panel, extra=panel["signals"]), "unregistered entry"),
        (dict(panel, completeness=_completeness(output, verified=False)), "not verified"),
        (dict(panel, completeness=_completeness(output, signals_sha256="0" * 64)), "signals"),
    ):
        readiness = repository.readiness(panels=dict(packages=changed))
        with pytest.raises(ValueError, match=message):
            authorize_component(readiness, "external_packages", root=repository.root, now=NOW)


@pytest.mark.parametrize(
    "changes,message",
    [
        (dict(verified=False), "not verified"),
        (dict(calendar="America/New_York"), "not verified"),
        (dict(signals_sha256="0" * 64), "different signals"),
        (dict(manifest_sha256="0" * 64), "different panel"),
        (dict(context_sha256="0" * 64), "different panel"),
        (dict(last_complete_day="2026-08-30"), "before the registered endpoint"),
        (dict(last_complete_day=None), "last complete day"),
        (dict(verified_at="2026-08-31T12:00:00+00:00"), "not fully elapsed"),
        (dict(response_evidence=[]), "no response captures"),
    ],
)
def test_the_run_reads_target_signals_only_through_their_verified_completeness(
    repository, changes, message
):
    output, _, panel = _pull(repository)
    readiness = dict(package_domain="npm", panels=dict(packages=panel))
    assert len(external_dataset(readiness, root=repository.root)) == len(SERIES)
    later = _completeness(output, last_complete_day="2026-09-15")
    assert len(external_dataset(_with(readiness, completeness=later), root=repository.root)) == 4
    changed = _with(readiness, completeness=_completeness(output, **changes))
    with pytest.raises(ValueError, match=message):
        external_dataset(changed, root=repository.root)


def _with(readiness, **entries):
    return dict(readiness, panels=dict(packages=dict(readiness["panels"]["packages"], **entries)))


def test_the_run_refuses_targets_without_their_document_or_captures(repository):
    _, document, panel = _pull(repository)
    readiness = dict(package_domain="npm", panels=dict(packages=panel))
    without = {k: v for k, v in panel.items() if k != "completeness"}
    with pytest.raises(ValueError, match="completeness document"):
        external_dataset(dict(readiness, panels=dict(packages=without)), root=repository.root)
    with pytest.raises(ValueError, match="not verified"):
        external_dataset(dict(panels=dict(packages=panel)), root=repository.root)
    capture = repository.root / document["response_evidence"][1]["path"]
    capture.write_bytes(capture.read_bytes() + b" ")
    with pytest.raises(ValueError, match="missing or changed"):
        external_dataset(readiness, root=repository.root)
    capture.unlink()
    with pytest.raises(ValueError, match="missing or changed"):
        external_dataset(readiness, root=repository.root)

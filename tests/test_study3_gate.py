"""Study 3's declarations, its single-domain gate and the gated NYC 311 target pull; no network."""

import copy
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest
from test_study3_nyc311 import (
    CELLS,
    CONTEXT_DAYS,
    TARGET_DAYS,
    Socrata,
    client_for,
    fixture_data,
    inventory_document,
)

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes
from pulsegraph.study2 import ingestion
from pulsegraph.study2.constants import (
    CONTEXT_START,
    MODEL_PINS,
    PROTOCOL_COMMIT,
    PROTOCOL_SHA256,
    SEEDS,
    STUDY3_FILES,
    STUDY3_HEADING,
    STUDY3_PROTOCOL_SHA256,
    STUDY3_SEEDS,
    STUDY3_VARIANTS,
    VARIANTS,
)
from pulsegraph.study2.declarations import (
    study3_comparisons,
    study3_registered_variants,
    study3_run_name,
    validate_study3,
)
from pulsegraph.study2.gate import authorize_component, verify_study3_addition
from pulsegraph.study2.ingestion import (
    TARGET_END,
    TARGET_START,
    NYCSource,
    SourceFailure,
    build_panel,
    pull_nyc_targets,
)
from pulsegraph.study2.runner import external_dataset

NOW = datetime(2026, 10, 17, tzinfo=timezone.utc)
HEAD, ADDITION = "a" * 40, "c" * 40
STUDY3_BYTES = 71635  # PROTOCOL.md as the addition left it, SHA-256 05c7617b...
PINS = {
    "timesfm": "3.0.2",
    "statsforecast": "2.1.1",
    "torch": "2.11.0+cu128",
    "chronos-forecasting": "2.2.0",
    "scipy": "1.16.0",
    "numpy": "2.3.0",
    "pandas": "2.3.0",
}


def _entry(path, value=None):
    if value is not None:
        atomic_json(path, value)
    return dict(path=str(path), sha256=file_hash(path))


def _declarations():
    return {name: (ROOT_DIR / name).read_bytes() for name in STUDY3_FILES}


@pytest.fixture(autouse=True)
def clock(monkeypatch):
    state = dict(now=datetime(2026, 10, 16, tzinfo=timezone.utc))

    def now():
        state["now"] += timedelta(seconds=1)
        return state["now"]

    monkeypatch.setattr(ingestion, "utc_now", now)
    return state


class Repository:
    """A clean checkout at HEAD over the addition's commit, with a Study 3 smoke and an NYC 311
    panel built through the census over the fake Socrata endpoint."""

    def __init__(self, root, monkeypatch):
        self.root, self.dirty, self.ancestor = root, False, True
        self.study2 = subprocess.check_output(
            ["git", "show", f"{PROTOCOL_COMMIT}:PROTOCOL.md"], cwd=ROOT_DIR
        )
        self.added = (ROOT_DIR / "PROTOCOL.md").read_bytes()[:STUDY3_BYTES]
        assert sha256_bytes(self.added) == STUDY3_PROTOCOL_SHA256
        self.parent = self.added[: self.added.index(STUDY3_HEADING.encode())]
        self.current = self.added
        (root / "PROTOCOL.md").write_bytes(self.current)
        (root / "pyproject.toml").write_text("")
        (root / "tests").mkdir()
        self.at_addition = _declarations()
        self.at_head = dict(self.at_addition)
        for name, data in self.at_addition.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_bytes(data)
        sources = {}
        for name in (
            "pulsegraph/study2/distributions.py",
            "pulsegraph/study2/scores.py",
            "scripts/study2_run.py",
            "scripts/study3_inference.py",
        ):
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(f"# {name}\n")
            sources[name] = file_hash(root / name)
        atomic_json(
            root / "study/study2/crps_resolution.json",
            dict(
                passed=True,
                crps=dict(tolerance=1e-8, max_k=1000000, maximum_residual_bound=1e-12),
                source_sha256={k: v for k, v in sources.items() if k.startswith("pulsegraph")},
            ),
        )
        self.sources = sources
        self.smoke = self.write_smoke()
        self.context_data = fixture_data(CONTEXT_DAYS)
        self.panel = self.write_panel()
        # The fixture's frame stands in for the registered 2024 inventory.
        monkeypatch.setattr(
            "pulsegraph.study2.gate.STUDY3_INVENTORY_SHA256", file_hash(root / "inventory.json")
        )
        monkeypatch.setattr("pulsegraph.study2.gate.git", self.git)
        monkeypatch.setattr("pulsegraph.study2.gate.installed_versions", lambda: dict(PINS))

    def write_smoke(self, **changes):
        smoke = dict(
            passed=True,
            data_kind="synthetic",
            implementation_commit=HEAD,
            component="study3",
            protocol_sha256=STUDY3_PROTOCOL_SHA256,
            seeds=STUDY3_SEEDS,
            variants=list(STUDY3_VARIANTS),
            source_sha256=dict(self.sources),
            packages=dict(PINS),
            memory=dict(peak_reserved_bytes=2948595712),
            hardware=dict(gpu_model="NVIDIA GeForce RTX 4070 SUPER"),
        )
        smoke.update(changes)
        count = len(list((self.root / "evidence").glob("smoke-*.json")))
        return _entry(self.root / f"evidence/smoke-{count}.json", smoke)

    def write_panel(self):
        inventory = inventory_document(self.root / "inventory.json")
        source = NYCSource(client_for(self.root, Socrata(self.context_data), "panel-captures"))
        build_panel(inventory, source.context, self.root / "panel", seed=STUDY3_SEEDS["selection"])
        panel = {
            name: _entry(self.root / "panel" / file)
            for name, file in (
                ("manifest", "manifest.json"),
                ("selection", "selection.json"),
                ("context", "context.parquet"),
                ("census", "census.json"),
            )
        }
        atomic_json(self.root / "study/study3/nyc311_panel_status.json", dict(panel=panel))
        return panel

    def git(self, root, *args):
        if args[0] == "rev-parse":
            return HEAD.encode() + b"\n"
        if args[0] == "status":
            return b"?? stray.py\n" if self.dirty else b""
        if args[0] == "merge-base":
            if not self.ancestor:
                raise subprocess.CalledProcessError(1, "git")
            return b""
        known = {
            f"{PROTOCOL_COMMIT}:PROTOCOL.md": self.study2,
            f"{ADDITION}:PROTOCOL.md": self.added,
            f"{ADDITION}^:PROTOCOL.md": self.parent,
            "HEAD:PROTOCOL.md": self.current,
            **{f"{ADDITION}:{name}": data for name, data in self.at_addition.items()},
            **{f"HEAD:{name}": data for name, data in self.at_head.items()},
        }
        if args[1] not in known:
            raise subprocess.CalledProcessError(128, "git")
        return known[args[1]]

    def readiness(self, **changes):
        document = dict(
            action="study3",
            approved_at="2026-10-16T12:00:00+00:00",
            approved_by="The author",
            confirmed=True,
            estimated_seconds=100,
            runtime_budget_seconds=200,
            evidence=[self.panel["manifest"]],
            implementation_commit=HEAD,
            addition_commit=ADDITION,
            protocol_sha256=STUDY3_PROTOCOL_SHA256,
            domain="nyc311",
            panels=dict(nyc311=dict(self.panel)),
            smoke=self.smoke,
            source_semantics_resolved=True,
            target_access_approved=True,
        )
        document.update(changes)
        path = self.root / "readiness.json"
        atomic_json(path, document)
        return path


@pytest.fixture
def repository(tmp_path, monkeypatch):
    return Repository(tmp_path, monkeypatch)


def test_the_committed_declarations_are_the_registered_family_and_specification():
    spec, family = (read_json(ROOT_DIR / name) for name in STUDY3_FILES)
    assert validate_study3(spec, family) == "study3"
    rows = family["comparisons"]
    assert rows == study3_comparisons() and len(rows) == family["comparison_count"] == 36
    assert [r["id"] for r in rows] == [f"R{i:02}" for i in range(1, 37)]
    order = [(r["stratum"], r["model"], r["horizon"], r["contrast"]) for r in rows]
    assert order == [
        (s, m, h, c)
        for s in ("dense", "sparse", "very_sparse")
        for m in MODEL_PINS
        for h in (7, 30)
        for c in ("T1", "T2")
    ]
    for row in rows:
        assert row["variant"] == f"{row['model']}_hurdle_dynamic"
        assert row["reference"] == (
            f"{row['model']}_completed" if row["contrast"] == "T1" else "hurdle_empirical_28"
        )
        assert row["variant"] in STUDY3_VARIANTS and row["reference"] in STUDY3_VARIANTS
    assert spec["variants"] == study3_registered_variants()
    saved = [study3_run_name(name) for name in spec["variants"]]
    assert set(saved) | {f"{m}_raw" for m in MODEL_PINS} == set(STUDY3_VARIANTS)
    assert "chronos2_hurdle" in saved and "chronos2_hurdle_fixed" not in STUDY3_VARIANTS
    assert spec["seeds"] == STUDY3_SEEDS != SEEDS
    assert (
        family["bootstrap_seed"] == 20261004 and spec["protocol_sha256"] == STUDY3_PROTOCOL_SHA256
    )
    protocol = (ROOT_DIR / "PROTOCOL.md").read_bytes()
    assert protocol.count(STUDY3_HEADING.encode()) == 1


def _mutate(document, path, value):
    document = copy.deepcopy(document)
    target = document
    for key in path[:-1]:
        target = target[key]
    if value is KeyError:
        del target[path[-1]]
    else:
        target[path[-1]] = value
    return document


@pytest.mark.parametrize(
    "which,path,value",
    [
        ("spec", ("seeds", "selection"), 20260914),
        ("spec", ("seeds", "bootstrap"), 20260917),
        ("spec", ("comparison_count",), 35),
        ("spec", ("variants",), list(VARIANTS)),
        ("spec", ("protocol_sha256",), PROTOCOL_SHA256),
        ("spec", ("calendar", "cutoffs"), ["2026-06-03", "2026-07-03"]),
        ("spec", ("calendar", "panel_deadline"), "2026-10-28T23:59:59+00:00"),
        ("spec", ("strata", "definitions", 1, "upper"), 0.8),
        ("spec", ("strata", "minimum_complete_series_for_tests"), 5),
        ("spec", ("strata", "selection_seed"), 20260914),
        ("spec", ("domain", "primary", "inventory", "sha256"), "0" * 64),
        ("spec", ("domain", "fallback", "name"), "rubygems"),
        ("spec", ("crps", "resolution"), "study/study3/crps_resolution.json"),
        ("spec", ("dynamic_count", "discount"), 0.95),
        ("spec", ("gate",), ""),
        ("spec", ("extra",), "a new key"),
        ("spec", ("secondary",), KeyError),
        ("spec", ("authority", "commit"), ADDITION),
        ("family", ("q",), 0.1),
        ("family", ("bootstrap_replicates",), 2000),
        ("family", ("minimum_complete_series_per_stratum",), 5),
        ("family", ("comparisons", 3, "reference"), "hurdle_count_28"),
        ("family", ("comparisons", 35, "stratum"), "sparse"),
        ("family", ("comparisons", 0, "id"), "R00"),
        ("family", ("predicted_t1_sign", "dense"), "negative"),
        ("family", ("strata", 2, "upper_inclusive"), False),
        ("family", ("hypothesis",), KeyError),
        ("family", ("zero_method",), "pratt"),
    ],
)
def test_any_changed_declaration_is_refused(which, path, value):
    spec, family = (read_json(ROOT_DIR / name) for name in STUDY3_FILES)
    if which == "spec":
        spec = _mutate(spec, path, value)
    else:
        family = _mutate(family, path, value)
    with pytest.raises(ValueError, match="declaration"):
        validate_study3(spec, family)
    reduced = dict(family, comparisons=family["comparisons"][:24], comparison_count=24)
    with pytest.raises(ValueError, match="declaration"):
        validate_study3(read_json(ROOT_DIR / STUDY3_FILES[0]), reduced)


def test_the_gate_accepts_the_signed_single_domain_readiness(repository):
    result = authorize_component(repository.readiness(), "study3", root=repository.root, now=NOW)
    assert result["family"]["comparison_count"] == 36 and result["spec"]["component"] == "study3"
    authority = result["metadata"]["authority"]
    assert authority["addition_commit"] == ADDITION
    assert authority["addition_protocol_sha256"] == STUDY3_PROTOCOL_SHA256
    assert authority["declaration_sha256"] == {
        name: sha256_bytes(data) for name, data in repository.at_addition.items()
    }
    assert result["metadata"]["implementation_commit"] == HEAD
    assert "holdout_freeze" not in result["readiness"]


@pytest.mark.parametrize(
    "changes,message",
    [
        (dict(confirmed=False), "signed author approval"),
        (dict(action="external_packages"), "signed author approval"),
        (dict(approved_at="2026-10-18T00:00:00+00:00"), "future"),
        (dict(addition_commit=None), "bound to the Study 3 addition"),
        (dict(addition_commit="c" * 39), "bound to the Study 3 addition"),
        (dict(protocol_sha256=PROTOCOL_SHA256), "bound to the Study 3 addition"),
        (dict(protocol_commit=PROTOCOL_COMMIT, protocol_sha256=PROTOCOL_SHA256), "Study 3"),
        (dict(target_access_approved=False), "approved separately"),
        (dict(domain="npm"), "one panel"),
        (dict(domain="pypi"), "one panel"),
        (dict(runtime_budget_seconds=50), "budget"),
        (dict(evidence=[]), "evidence"),
        (dict(source_semantics_resolved=False), "evidence"),
    ],
)
def test_the_gate_refuses_unsigned_unbound_or_unbounded_readiness(repository, changes, message):
    with pytest.raises(ValueError, match=message):
        authorize_component(
            repository.readiness(**changes), "study3", root=repository.root, now=NOW
        )


def test_the_gate_takes_only_the_frozen_panel_selected_with_study3s_seed(repository):
    panel = repository.panel
    with pytest.raises(ValueError, match="one panel"):
        authorize_component(
            repository.readiness(panels=dict(nyc311=panel, packages=panel)),
            "study3",
            root=repository.root,
            now=NOW,
        )
    for name in ("manifest", "selection", "context", "census"):
        changed = repository.root / f"changed-{name}.json"
        atomic_json(changed, dict(changed=name))
        for entry, message in (
            (_entry(changed), "frozen Study 3 panel"),
            (dict(panel[name], path=str(changed)), "Evidence hash mismatch"),
        ):
            readiness = repository.readiness(panels=dict(nyc311=dict(panel, **{name: entry})))
            with pytest.raises(ValueError, match=message):
                authorize_component(readiness, "study3", root=repository.root, now=NOW)
    readiness = repository.readiness(panels=dict(nyc311=dict(panel, extra=panel["manifest"])))
    with pytest.raises(ValueError, match="unregistered entry"):
        authorize_component(readiness, "study3", root=repository.root, now=NOW)
    # A panel selected with Study 2's seed, drawn from another inventory, or verified after the
    # deadline is not Study 3's.
    manifest = read_json(repository.root / "panel" / "manifest.json")
    for changes, message in (
        (dict(report=dict(manifest["report"], selection_seed=SEEDS["selection"])), "seed"),
        (dict(inventory_sha256="0" * 64), "registered 2024 inventory"),
        (dict(verified_at="2026-10-28T00:00:00+00:00"), "deadline"),
    ):
        other = _entry(repository.root / "other-manifest.json", dict(manifest, **changes))
        atomic_json(
            repository.root / "study/study3/nyc311_panel_status.json",
            dict(panel=dict(panel, manifest=other)),
        )
        readiness = repository.readiness(panels=dict(nyc311=dict(panel, manifest=other)))
        with pytest.raises(ValueError, match=message):
            authorize_component(readiness, "study3", root=repository.root, now=NOW)


def test_the_pypi_fallback_needs_its_predeclared_operational_record(repository):
    directory = repository.root / "pypi"
    context = directory / "context.parquet"
    directory.mkdir()
    pd.DataFrame(dict(series_id=["a"], date=[pd.Timestamp(CONTEXT_START)], count=[1])).to_parquet(
        context
    )
    panel = dict(
        manifest=_entry(
            directory / "manifest.json",
            dict(domain="pypi", report=dict(selection_seed=20261001), series=[]),
        ),
        selection=_entry(directory / "selection.json", dict(report={})),
        context=_entry(context),
    )
    atomic_json(repository.root / "study/study3/pypi_panel_status.json", dict(panel=panel))
    stop = _entry(repository.root / "nyc-stop.json", dict(reason="source_gap_day"))
    record = dict(
        reason="NYC 311 census stopped on a source gap day before any target scoring",
        declared_before_scoring=True,
        declared_at="2026-10-16T18:00:00+00:00",
        evidence=[stop],
    )
    readiness = dict(domain="pypi", panels=dict(pypi=panel))
    result = authorize_component(
        repository.readiness(**readiness, nyc311_fallback=record),
        "study3",
        root=repository.root,
        now=NOW,
    )
    assert result["readiness"]["domain"] == "pypi"
    for changes in (
        dict(reason=""),
        dict(declared_before_scoring=False),
        dict(evidence=[]),
        dict(declared_at="2026-10-18T00:00:00+00:00"),
        dict(declared_at=None),
    ):
        with pytest.raises(ValueError, match="operational failure"):
            authorize_component(
                repository.readiness(**readiness, nyc311_fallback=dict(record, **changes)),
                "study3",
                root=repository.root,
                now=NOW,
            )
    with pytest.raises(ValueError, match="operational failure"):
        authorize_component(
            repository.readiness(**readiness), "study3", root=repository.root, now=NOW
        )


def test_the_gate_requires_a_current_study3_smoke_and_a_clean_tree(repository):
    for smoke in (
        repository.write_smoke(seeds=SEEDS),
        repository.write_smoke(variants=list(VARIANTS)),
        repository.write_smoke(component=None, protocol_commit=PROTOCOL_COMMIT),
        repository.write_smoke(protocol_sha256=PROTOCOL_SHA256),
        repository.write_smoke(implementation_commit="b" * 40),
        repository.write_smoke(
            source_sha256=dict(repository.sources, **{"scripts/study3_inference.py": "0" * 64})
        ),
    ):
        with pytest.raises(ValueError, match="(?i)smoke"):
            authorize_component(
                repository.readiness(smoke=smoke), "study3", root=repository.root, now=NOW
            )
    readiness = repository.readiness(smoke=repository.write_smoke())
    repository.dirty = True
    with pytest.raises(ValueError, match="committed and clean"):
        authorize_component(readiness, "study3", root=repository.root, now=NOW)


def test_the_gate_binds_the_addition_commit_and_its_declarations(repository):
    readiness = repository.readiness()
    root = repository.root
    repository.ancestor = False
    with pytest.raises(ValueError, match="history of HEAD"):
        authorize_component(readiness, "study3", root=root, now=NOW)
    repository.ancestor = True
    repository.added = repository.parent  # the named commit's protocol lacks the addition
    with pytest.raises(ValueError, match="does not carry the Study 3 addition"):
        authorize_component(readiness, "study3", root=root, now=NOW)
    repository.added = repository.current
    repository.parent = repository.current  # the heading was already there before the commit
    with pytest.raises(ValueError, match="not the commit that added Study 3"):
        authorize_component(readiness, "study3", root=root, now=NOW)
    repository.parent = repository.current[: repository.current.index(STUDY3_HEADING.encode())]
    name = STUDY3_FILES[1]
    family = json.loads(repository.at_addition[name])
    edited = json.dumps(dict(family, q=0.1), indent=2, sort_keys=True).encode() + b"\n"
    repository.at_head[name] = edited
    with pytest.raises(ValueError, match="differ from those of the addition's commit"):
        verify_study3_addition(ADDITION, root=root)
    repository.at_head[name] = repository.at_addition[name]
    (root / name).write_bytes(repository.at_addition[name] + b" ")
    with pytest.raises(ValueError, match="differ from those of the addition's commit"):
        verify_study3_addition(ADDITION, root=root)
    (root / name).write_bytes(repository.at_addition[name])
    del repository.at_addition[name]
    with pytest.raises(ValueError, match="not committed with the addition"):
        verify_study3_addition(ADDITION, root=root)
    with pytest.raises(ValueError, match="full commit"):
        verify_study3_addition("c" * 12, root=root)


def _target_source(repository, faults=None, data=None):
    session = Socrata(data or fixture_data(TARGET_DAYS, seed=9, start_key=60000000), faults)
    return session, NYCSource(client_for(repository.root, session, "targets/captures"))


def _with_targets(repository, document, output):
    return dict(
        repository.panel,
        signals=_entry(output / "signals.parquet"),
        completeness=_entry(output / "completeness.json"),
    )


def test_the_target_pull_opens_only_the_target_days_and_joins_the_frozen_context(repository):
    session, source = _target_source(repository)
    readiness, output = repository.readiness(), repository.root / "targets"
    document = pull_nyc_targets(readiness, source, output, root=repository.root, now=NOW)
    assert session.days() == TARGET_DAYS
    named = set(re.findall(r"\d{4}-\d{2}-\d{2}", json.dumps(session.calls)))
    assert min(named) == TARGET_START and max(named) == TARGET_END
    assert document["calendar"] == "America/New_York" and document["verified"] is True
    assert document["last_complete_day"] == TARGET_END and document["series"] == len(CELLS)
    assert document["signals_sha256"] == file_hash(output / "signals.parquet")
    assert document["census_sha256"] == repository.panel["census"]["sha256"]
    assert document["target_census"]["days"] == 90 and document["target_census"]["gap_days"] == []
    assert len(document["response_evidence"]) == 90 and document["ledger_failures"] == []
    signals = pd.read_parquet(output / "signals.parquet")
    assert signals.groupby("series_id").size().to_dict() == {
        json.dumps(list(c), separators=(",", ":")): 365 for c in CELLS
    }
    frozen = pd.read_parquet(repository.root / "panel" / "context.parquet")
    for key, part in signals.groupby("series_id"):
        early = part[part.date < pd.Timestamp(TARGET_START)].reset_index(drop=True)
        mine = frozen[frozen.series_id.eq(key)][["series_id", "date", "count"]]
        assert early.equals(mine.reset_index(drop=True))
    panel = _with_targets(repository, document, output)
    dataset = external_dataset(
        dict(domain="nyc311", panels=dict(nyc311=panel)), root=repository.root
    )
    assert len(dataset) == len(CELLS) and all(len(s) == 365 for s in dataset.values())
    gated = repository.readiness(panels=dict(nyc311=panel))
    assert authorize_component(gated, "study3", root=repository.root, now=NOW)["family"]
    with pytest.raises(FileExistsError):
        pull_nyc_targets(readiness, source, output, root=repository.root, now=NOW)


def test_a_target_outage_stops_the_pull_and_resumes_from_captures(repository):
    readiness, output = repository.readiness(), repository.root / "targets"
    session, source = _target_source(repository, faults={TARGET_DAYS[40]: "transport_failure"})
    with pytest.raises(SourceFailure, match="transport_failure"):
        pull_nyc_targets(readiness, source, output, root=repository.root, now=NOW)
    assert sorted(p.name for p in output.iterdir()) == ["captures", "pull.json"]
    assert read_json(output / "pull.json")["failures"][0]["kind"] == "outage"
    session, source = _target_source(repository)
    document = pull_nyc_targets(readiness, source, output, root=repository.root, now=NOW)
    assert session.days() == TARGET_DAYS[40:]
    assert [f["kind"] for f in document["ledger_failures"]] == ["outage"]
    assert len(document["response_evidence"]) == 90


def test_a_target_source_gap_stops_the_domain(repository):
    data = fixture_data(TARGET_DAYS, seed=9, start_key=60000000)
    data[TARGET_DAYS[60]] = []
    _, source = _target_source(repository, data=data)
    output = repository.root / "targets"
    with pytest.raises(SourceFailure, match="source_gap_day"):
        pull_nyc_targets(repository.readiness(), source, output, root=repository.root, now=NOW)
    assert not (output / "signals.parquet").exists() and not (output / "completeness.json").exists()
    assert read_json(output / "pull.json")["gap_days"] == [TARGET_DAYS[60]]


@pytest.mark.parametrize(
    "changes,message",
    [
        (dict(target_access_approved=False), "approved separately"),
        (dict(confirmed=False), "signed author approval"),
        (dict(addition_commit=None), "Study 3 addition"),
    ],
)
def test_the_target_pull_makes_no_request_without_the_signed_gate(repository, changes, message):
    session, source = _target_source(repository)
    with pytest.raises(ValueError, match=message):
        pull_nyc_targets(
            repository.readiness(**changes),
            source,
            repository.root / "out",
            root=repository.root,
            now=NOW,
        )
    assert session.calls == [] and not (repository.root / "out").exists()
    repository.dirty = True
    with pytest.raises(ValueError, match="committed and clean"):
        pull_nyc_targets(
            repository.readiness(), source, repository.root / "out", root=repository.root, now=NOW
        )
    assert session.calls == [] and source.targets_open is False

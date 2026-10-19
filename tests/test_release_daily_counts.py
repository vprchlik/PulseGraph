"""The committed daily counts of the npm and NYC 311 panels: rebuilt byte for byte from their inputs
when the inputs are present, and the builder's checks on toy panels."""

import hashlib
import importlib.util
import json

import pandas as pd
import pytest

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.study2.ingestion import SourceFailure

SCRIPT = ROOT_DIR / "reports/release/build_daily_counts.py"
_spec = importlib.util.spec_from_file_location("build_daily_counts", SCRIPT)
daily = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(daily)

DOMAINS = sorted(daily.PANELS)
CONTEXT = pd.date_range("2025-09-01", "2026-06-02")
ALL_DAYS = pd.date_range("2025-09-01", "2026-08-31")


def _committed(domain):
    out = ROOT_DIR / daily.PANELS[domain]["out"]
    provenance = json.loads((out / "daily_counts.provenance.json").read_text(encoding="utf-8"))
    return out / "daily_counts.csv", provenance


@pytest.mark.parametrize("domain", DOMAINS)
def test_committed_counts_match_their_provenance(domain):
    path, provenance = _committed(domain)
    data = path.read_bytes()
    output = provenance["output"]
    assert output["path"] == f"{daily.PANELS[domain]['out']}/daily_counts.csv"
    assert (output["bytes"], output["sha256"]) == (len(data), hashlib.sha256(data).hexdigest())
    assert b"\r" not in data and data.endswith(b"\n") and not data.startswith(b"\xef\xbb\xbf")
    header, *lines = data.decode("utf-8").split("\n")[:-1]
    assert header.split(",") == list(daily.PANELS[domain]["columns"]) == output["columns"]
    assert len(lines) == output["rows"] == output["series"] * len(ALL_DAYS)
    for name in ("manifest", "run_json"):
        entry = provenance["inputs"][name]
        assert file_hash(ROOT_DIR / entry["path"]) == entry["sha256"]
    state = json.loads((ROOT_DIR / provenance["inputs"]["run_json"]["path"]).read_text("utf-8"))
    panel = state["metadata"]["readiness"]["panels"][daily.PANELS[domain]["panel"]]
    for name in ("manifest", "context", "signals"):
        assert provenance["inputs"][name]["sha256"] == panel[name]["sha256"]
    assert provenance["builder_sha256"] == file_hash(SCRIPT)


@pytest.mark.parametrize("domain", DOMAINS)
@pytest.mark.parametrize("context", [True, False], ids=["with_context", "signals_only"])
def test_counts_rebuild_byte_for_byte(domain, context, tmp_path):
    path, provenance = _committed(domain)
    for name in ("signals", "context") if context else ("signals",):
        entry = provenance["inputs"][name]
        if not (ROOT_DIR / entry["path"]).is_file():
            asset = entry.get("release_asset", "not a release asset")
            pytest.skip(f"{entry['path']} is not present ({asset})")
    daily.build(domain, context=context, out=tmp_path)
    assert (tmp_path / "daily_counts.csv").read_bytes() == path.read_bytes()
    if context:
        committed = path.with_name("daily_counts.provenance.json").read_bytes()
        assert (tmp_path / "daily_counts.provenance.json").read_bytes() == committed


def _toy(root, domain, series, counts):
    """A toy panel at the registered relative paths: run.json, manifest, context and signals."""
    spec = daily.PANELS[domain]
    paths = dict(
        manifest=root / spec["out"] / "manifest.json",
        context=root / "data/raw/toy/context.parquet",
        signals=root / "data/raw/toy/signals.parquet",
    )
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(
        [
            dict(series_id=row["series_id"], date=day, count=counts(i, j))
            for i, row in enumerate(series)
            for j, day in enumerate(ALL_DAYS)
        ]
    )
    frame.loc[frame.date.isin(CONTEXT)].to_parquet(paths["context"], index=False)
    frame.to_parquet(paths["signals"], index=False)
    manifest = dict(series=series, context_sha256=file_hash(paths["context"]))
    paths["manifest"].write_text(json.dumps(manifest), encoding="utf-8")
    panel = {
        name: dict(path=path.relative_to(root).as_posix(), sha256=file_hash(path))
        for name, path in paths.items()
    }
    run = root / spec["run"] / "run.json"
    run.parent.mkdir(parents=True, exist_ok=True)
    state = dict(metadata=dict(readiness=dict(panels={spec["panel"]: panel})))
    run.write_text(json.dumps(state), encoding="utf-8")
    return paths, frame


NPM_SERIES = [
    dict(series_id="zeta", created_at="2019-01-02T03:04:05.678Z"),
    dict(series_id="@scope/pkg", created_at="2024-05-06T07:08:09.000Z"),
    dict(series_id="alpha", created_at="2014-07-16T11:01:19.518Z"),
]
NYC_SERIES = [
    dict(series_id=json.dumps([p, b], separators=(",", ":")), problem=p, board=b)
    for p, b in (("Noise", "12 BRONX"), ("Graffiti", "01 QUEENS"), ("Noise", "01 BRONX"))
]


def test_toy_npm_counts_are_sorted_lf_and_deterministic(tmp_path):
    paths, frame = _toy(tmp_path, "npm", NPM_SERIES, lambda i, j: (i * 7 + j) % 5)
    first = daily.build("npm", root=tmp_path)
    out = tmp_path / daily.PANELS["npm"]["out"]
    data = (out / "daily_counts.csv").read_bytes()
    lines = data.decode("utf-8").split("\n")
    assert lines[0] == "package,created_at,day,count" and lines[-1] == ""
    assert lines[1] == "@scope/pkg,2024-05-06T07:08:09.000Z,2025-09-01,2"
    assert lines[len(ALL_DAYS) + 1].startswith("alpha,2014-07-16T11:01:19.518Z,2025-09-01,")
    assert len(lines) == 2 + 3 * len(ALL_DAYS) and b"\r" not in data
    rows = pd.read_csv(out / "daily_counts.csv", dtype={"count": "int64"})
    assert rows["count"].sum() == frame["count"].sum()
    assert first["output"]["sha256"] == hashlib.sha256(data).hexdigest()
    daily.build("npm", root=tmp_path, out=tmp_path / "again")
    daily.build("npm", root=tmp_path, out=tmp_path / "signals-only", context=False)
    assert (tmp_path / "again/daily_counts.csv").read_bytes() == data
    assert (tmp_path / "signals-only/daily_counts.csv").read_bytes() == data
    again = (tmp_path / "again/daily_counts.provenance.json").read_bytes()
    assert again == (out / "daily_counts.provenance.json").read_bytes()


def test_toy_nyc311_counts_name_problem_and_board(tmp_path):
    _toy(tmp_path, "nyc311", NYC_SERIES, lambda i, j: i + (j % 2))
    daily.build("nyc311", root=tmp_path)
    out = tmp_path / daily.PANELS["nyc311"]["out"] / "daily_counts.csv"
    rows = pd.read_csv(out, dtype=str)
    assert list(rows.columns) == ["problem", "board", "day", "count"]
    assert list(dict.fromkeys(zip(rows.problem, rows.board))) == [
        ("Graffiti", "01 QUEENS"),
        ("Noise", "01 BRONX"),
        ("Noise", "12 BRONX"),
    ]
    assert rows.day.iloc[0] == "2025-09-01" and rows.day.iloc[-1] == "2026-08-31"


def _rehash(root, domain, name, path):
    run = root / daily.PANELS[domain]["run"] / "run.json"
    state = json.loads(run.read_text(encoding="utf-8"))
    state["metadata"]["readiness"]["panels"][daily.PANELS[domain]["panel"]][name]["sha256"] = (
        file_hash(path)
    )
    run.write_text(json.dumps(state), encoding="utf-8")


def test_toy_inputs_that_differ_from_the_run_are_refused(tmp_path):
    paths, frame = _toy(tmp_path, "npm", NPM_SERIES, lambda i, j: j % 3)
    changed = frame.copy()
    changed.loc[changed.date == ALL_DAYS[-1], "count"] += 1
    changed.to_parquet(paths["signals"], index=False)
    with pytest.raises(SystemExit, match="signals: .* the run recorded"):
        daily.build("npm", root=tmp_path)
    # A signals file the run did record, but whose context days differ from the frozen context.
    changed.loc[changed.date == CONTEXT[10], "count"] += 1
    changed.to_parquet(paths["signals"], index=False)
    _rehash(tmp_path, "npm", "signals", paths["signals"])
    with pytest.raises(SystemExit, match="changed the frozen context"):
        daily.build("npm", root=tmp_path)
    # A signals file missing one target day.
    frame.loc[frame.date != ALL_DAYS[-5]].to_parquet(paths["signals"], index=False)
    _rehash(tmp_path, "npm", "signals", paths["signals"])
    with pytest.raises(SourceFailure, match="missing_context_day"):
        daily.build("npm", root=tmp_path)
    # A signals file with a series the manifest does not hold.
    extra = pd.concat([frame, frame.loc[frame.series_id == "alpha"].assign(series_id="beta")])
    extra.to_parquet(paths["signals"], index=False)
    _rehash(tmp_path, "npm", "signals", paths["signals"])
    with pytest.raises(SystemExit, match="different series"):
        daily.build("npm", root=tmp_path)
    assert not (tmp_path / daily.PANELS["npm"]["out"] / "daily_counts.csv").exists()

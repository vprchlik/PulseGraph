"""The release asset manifest, the deterministic archives and the verifier: on a toy run directory,
and on the real manifest against the runs' records (and the built assets when they are present)."""

import hashlib
import importlib.util
import json
import shutil
import zipfile

import pytest

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT_DIR / f"reports/release/{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build = _load("build_assets")
verify = _load("verify_assets")
RELEASE = ROOT_DIR / "data/release"


def _posix(text):
    return text.replace("\\", "/").strip("/")


def test_manifest_rows_agree_with_the_runs_records():
    assets = {asset["file"]: asset for asset in verify.read_assets()}
    assert set(assets) == {*build.ARCHIVES, *build.SIGNALS, "results.parquet"}
    for name, run in build.ARCHIVES.items():
        assert assets[name]["archive"] and _posix(assets[name]["place"]) == run
        assert len(verify.expected_checkpoints(ROOT_DIR / run)) in (540, 209, 300)
    for name, (run, panel) in build.SIGNALS.items():
        state = json.loads((ROOT_DIR / run / "run.json").read_text(encoding="utf-8"))
        entry = state["metadata"]["readiness"]["panels"][panel]["signals"]
        assert assets[name]["sha256"] == entry["sha256"]
        assert _posix(assets[name]["place"]) == entry["path"]
    state = json.loads((ROOT_DIR / build.RESULTS / "run.json").read_text(encoding="utf-8"))
    results = assets["results.parquet"]
    assert results["sha256"] == state["artifact_sha256"]["results.parquet"]
    assert results["bytes"] == 433_172_286
    assert _posix(results["place"]) == f"{build.RESULTS}/results.parquet"
    assert all(asset["bytes"] < build.LIMIT for asset in assets.values())


@pytest.mark.skipif(not RELEASE.is_dir(), reason="the assets are not built here (data/release)")
def test_built_assets_match_the_manifest(capsys):
    assert verify.main([str(RELEASE)]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 6 and all(line.startswith("OK") for line in lines)


@pytest.mark.skipif(
    not (RELEASE / "study2-npm-run-2026-10-15-checkpoints.zip").is_file(),
    reason="the npm archive is not built here (data/release)",
)
def test_npm_archive_restores_its_run_directory(tmp_path, capsys):
    for directory in build.ARCHIVES.values():
        (tmp_path / directory).mkdir(parents=True)
        shutil.copyfile(ROOT_DIR / directory / "run.json", tmp_path / directory / "run.json")
    run = "reports/study2-npm/run-2026-10-15"
    name = "study2-npm-run-2026-10-15-checkpoints.zip"
    assert verify.main([str(RELEASE), "--unpack", name], root=tmp_path) == 0
    restored = verify.present_checkpoints(tmp_path / run)
    assert restored == verify.present_checkpoints(ROOT_DIR / run) and len(restored) == 209
    expected = verify.expected_checkpoints(ROOT_DIR / run)
    assert all(file_hash(tmp_path / run / entry) == expected[entry] for entry in restored)
    assert "Unpacked 209 checkpoints" in capsys.readouterr().out


def _toy_run(root, labels=("toy/a", "toy/b", "toy/c")):
    """A run directory with three checkpoints, named and hashed as the runner does."""
    run = root / "reports/toy-run"
    run.mkdir(parents=True)
    completed = {}
    for i, label in enumerate(labels):
        name = hashlib.sha256(label.encode()).hexdigest() + ".json"
        (run / name).write_bytes(json.dumps(dict(rows=[i] * (50 + i), identity="x")).encode())
        completed[label] = file_hash(run / name)
    (run / "run.json").write_text(json.dumps(dict(completed=completed)), encoding="utf-8")
    return run


def _manifest(path, rows):
    """A toy ASSETS.md: some prose, the heading, the table, and prose after it."""
    lines = [
        "# Toy assets",
        "",
        "## The assets",
        "",
        "| File | Bytes | SHA-256 | What it holds | Place after download | URL |",
        "|---|---:|---|---|---|---|",
    ]
    for name, size, digest, place in rows:
        lines.append(f"| `{name}` | {size:,} | `{digest}` | toy | {place} | to be filled |")
    lines += ["", "Text after the table.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _toy(tmp_path):
    root = tmp_path / "tree"
    run = _toy_run(root)
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    archive = downloads / "toy-checkpoints.zip"
    assert build.write_archive(run, archive) == 3
    copy = downloads / "toy-signals.parquet"
    copy.write_bytes(b"toy signals")
    rows = [
        (
            "toy-checkpoints.zip",
            archive.stat().st_size,
            file_hash(archive),
            "unpack into `reports\\toy-run\\`",
        ),
        (
            "toy-signals.parquet",
            copy.stat().st_size,
            file_hash(copy),
            "copy to `data\\raw\\toy\\signals.parquet`",
        ),
        ("absent.parquet", 1, "0" * 64, "copy to `data\\raw\\toy\\absent.parquet`"),
    ]
    assets = _manifest(tmp_path / "ASSETS.md", rows)
    originals = {p.name: p.read_bytes() for p in run.iterdir() if p.name != "run.json"}
    return root, run, downloads, assets, originals


def test_toy_archive_is_deterministic(tmp_path):
    run = _toy_run(tmp_path)
    build.write_archive(run, tmp_path / "one.zip")
    build.write_archive(run, tmp_path / "two.zip")
    assert (tmp_path / "one.zip").read_bytes() == (tmp_path / "two.zip").read_bytes()
    with zipfile.ZipFile(tmp_path / "one.zip") as archive:
        infos = archive.infolist()
    assert [info.filename for info in infos] == sorted(verify.expected_checkpoints(run))
    assert {info.date_time for info in infos} == {(1980, 1, 1, 0, 0, 0)}
    assert {info.compress_type for info in infos} == {zipfile.ZIP_DEFLATED}
    (run / "stray.json").write_bytes(b"{}")
    build.write_archive(run, tmp_path / "three.zip")  # not a checkpoint name: left out
    assert (tmp_path / "three.zip").read_bytes() == (tmp_path / "one.zip").read_bytes()
    extra = hashlib.sha256(b"not in run.json").hexdigest() + ".json"
    (run / extra).write_bytes(b"{}")
    with pytest.raises(SystemExit, match="not in run.json"):
        build.write_archive(run, tmp_path / "four.zip")


def test_toy_check_unpack_and_refusals(tmp_path, capsys):
    root, run, downloads, assets, originals = _toy(tmp_path)
    for name in originals:
        (run / name).unlink()
    assert verify.main([str(downloads)], root=root, assets_path=assets) == 0
    out = capsys.readouterr().out
    assert "ABSENT  absent.parquet" in out and "3 entries are the checkpoints" in out
    assert "not yet placed" in out

    assert verify.main([str(downloads), "--unpack", "all"], root=root, assets_path=assets) == 0
    assert {p.name: p.read_bytes() for p in run.iterdir() if p.name != "run.json"} == originals
    assert "Unpacked 3 checkpoints into reports\\toy-run\\" in capsys.readouterr().out

    # A populated checkpoint set is refused, and nothing is touched.
    with pytest.raises(SystemExit, match="already holds 3 checkpoint files"):
        verify.main(
            [str(downloads), "--unpack", "toy-checkpoints.zip"], root=root, assets_path=assets
        )
    (run / sorted(originals)[0]).unlink()
    with pytest.raises(SystemExit, match="already holds 2 checkpoint files"):
        verify.main([str(downloads), "--unpack", "all"], root=root, assets_path=assets)

    # A placed copy that differs fails the check.
    (root / "data/raw/toy").mkdir(parents=True)
    (root / "data/raw/toy/signals.parquet").write_bytes(b"other bytes")
    assert verify.main([str(downloads)], root=root, assets_path=assets) == 1
    assert "FAIL    toy-signals.parquet: the file at" in capsys.readouterr().out


def test_toy_tampered_archives_are_not_unpacked(tmp_path, capsys):
    root, run, downloads, assets, originals = _toy(tmp_path)
    for name in originals:
        (run / name).unlink()
    archive = downloads / "toy-checkpoints.zip"
    data = bytearray(archive.read_bytes())
    data[40] ^= 1
    archive.write_bytes(bytes(data))
    assert verify.main([str(downloads), "--unpack", "all"], root=root, assets_path=assets) == 1
    out = capsys.readouterr().out
    assert "FAIL    toy-checkpoints.zip: SHA-256" in out and "Not unpacked" in out
    assert verify.present_checkpoints(run) == []

    # Right names, one entry's bytes not the run's: the manifest's hash matches, the unpack refuses.
    with zipfile.ZipFile(archive, "w") as forged:
        for name, content in sorted(originals.items()):
            forged.writestr(name, content if name != sorted(originals)[1] else b"{}")
    rows = [
        (
            "toy-checkpoints.zip",
            archive.stat().st_size,
            file_hash(archive),
            "unpack into `reports\\toy-run\\`",
        )
    ]
    _manifest(assets, rows)
    with pytest.raises(SystemExit, match="differs from run.json"):
        verify.main([str(downloads), "--unpack", "all"], root=root, assets_path=assets)
    assert verify.present_checkpoints(run) == []

    # An archive with an entry the run does not name fails the check.
    with zipfile.ZipFile(archive, "a") as forged:
        forged.writestr("0" * 64 + ".json", b"{}")
    rows = [
        (
            "toy-checkpoints.zip",
            archive.stat().st_size,
            file_hash(archive),
            "unpack into `reports\\toy-run\\`",
        )
    ]
    _manifest(assets, rows)
    assert verify.main([str(downloads)], root=root, assets_path=assets) == 1
    assert "its entries are not the checkpoints" in capsys.readouterr().out


def test_toy_manifest_errors(tmp_path):
    root, run, downloads, assets, _ = _toy(tmp_path)
    archive = downloads / "toy-checkpoints.zip"
    wrong_size = [
        ("toy-checkpoints.zip", 1, file_hash(archive), "unpack into `reports\\toy-run\\`")
    ]
    _manifest(assets, wrong_size)
    assert verify.main([str(downloads)], root=root, assets_path=assets) == 1
    copy = downloads / "toy-signals.parquet"
    listed = [("toy-signals.parquet", copy.stat().st_size, file_hash(copy), "copy to `data\\x`")]
    _manifest(assets, listed)
    with pytest.raises(SystemExit):  # not an archive: an argument error
        verify.main(
            [str(downloads), "--unpack", "toy-signals.parquet"], root=root, assets_path=assets
        )
    outside = [("toy-checkpoints.zip", 1, file_hash(archive), "unpack into `..\\elsewhere\\`")]
    _manifest(assets, outside)
    with pytest.raises(ValueError, match="not a path inside the repository"):
        verify.read_assets(assets)
    assets.write_text("# No table here\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no heading"):
        verify.read_assets(assets)

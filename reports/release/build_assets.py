r"""The release assets, built deterministically under the ignored `data\release\`.

From the repository root, PowerShell:

    .\.venv\Scripts\python.exe reports\release\build_assets.py --out data\release

Six files. Three archives, one per run directory, each holding that run's whole-series checkpoints
(the `<SHA-256 of the series label>.json` files its `.gitignore` keeps out of the tree) and nothing
else. Two copies of the target signals the npm and NYC 311 runs read. One copy of Study 1's
`results.parquet`. Before an entry is written, the run directory must hold exactly the checkpoints
`run.json` names (a file name is the SHA-256 of a completed label) and each must hash to the value
`run.json` recorded for its label; each copy must hash to the value its run recorded.

The archives are deterministic: entries sorted by name, at the archive's root, every timestamp
1980-01-01 00:00:00, Unix permissions 0644, no directory entry, no comment, every entry deflated at
level 6. The same checkpoints and the same zlib give the same bytes; the zlib version is printed and
recorded. Each archive is read back and every entry's bytes are hashed against `run.json`. Every
file must be under 2,000,000,000 bytes, below the 2 GiB per-file limit of a GitHub release. The
command prints each file's bytes, SHA-256 and entry count and writes them to `<out>\assets.json`,
and it writes `<out>\.gitignore` holding `*`, so that the directory ignores itself.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVES = {
    "study2-synthetic-2026-10-15-checkpoints.zip": "reports/study2-synthetic-2026-10-15",
    "study2-npm-run-2026-10-15-checkpoints.zip": "reports/study2-npm/run-2026-10-15",
    "study3-nyc311-run-2026-10-17-checkpoints.zip": "reports/study3-nyc311/run-2026-10-17",
}
SIGNALS = {
    "study2-npm-targets-signals.parquet": ("reports/study2-npm/run-2026-10-15", "packages"),
    "study3-nyc311-targets-signals.parquet": ("reports/study3-nyc311/run-2026-10-17", "nyc311"),
}
RESULTS = "reports/registered-2026-09-13/run"
LIMIT = 2_000_000_000
LEVEL = 6
EPOCH = (1980, 1, 1, 0, 0, 0)
CHECKPOINT = re.compile(r"^[0-9a-f]{64}\.json$")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_checkpoints(run):
    """The run's checkpoint names and their recorded SHA-256 values; the directory must agree."""
    state = json.loads((Path(run) / "run.json").read_text(encoding="utf-8"))
    expected = {
        sha256_bytes(label.encode()) + ".json": digest
        for label, digest in state["completed"].items()
    }
    present = {p.name for p in Path(run).iterdir() if p.is_file() and CHECKPOINT.match(p.name)}
    if present != set(expected):
        raise SystemExit(
            f"{run}: {len(set(expected) - present)} checkpoints missing, "
            f"{len(present - set(expected))} not in run.json"
        )
    return expected


def write_archive(run, path):
    """One deterministic archive of the run's checkpoints; returns its entry count."""
    run, path = Path(run), Path(path)
    expected = run_checkpoints(run)
    temporary = path.with_name(path.name + ".tmp")
    with zipfile.ZipFile(temporary, "w") as archive:
        for name in sorted(expected):
            data = (run / name).read_bytes()
            if sha256_bytes(data) != expected[name]:
                raise SystemExit(f"{run / name}: SHA-256 differs from run.json")
            info = zipfile.ZipInfo(name, date_time=EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=LEVEL)
    with zipfile.ZipFile(temporary) as archive:
        infos = archive.infolist()
        if [info.filename for info in infos] != sorted(expected):
            raise SystemExit(f"{temporary}: entries differ from run.json")
        for info in infos:
            if sha256_bytes(archive.read(info)) != expected[info.filename]:
                raise SystemExit(f"{temporary}: {info.filename} reads back differently")
    os.replace(temporary, path)
    return len(infos)


def copy_checked(source, path, digest):
    if sha256_file(source) != digest:
        raise SystemExit(f"{source}: SHA-256 differs from the run's record")
    temporary = Path(path).with_name(Path(path).name + ".tmp")
    shutil.copyfile(source, temporary)
    if sha256_file(temporary) != digest:
        raise SystemExit(f"{temporary}: the copy differs from its source")
    os.replace(temporary, path)


def build(out, *, root=ROOT, archives=ARCHIVES, signals=SIGNALS, results=RESULTS):
    out, root = Path(out), Path(root)
    out.mkdir(parents=True, exist_ok=True)
    (out / ".gitignore").write_bytes(
        b"# Release assets, built by reports/release/build_assets.py\n*\n"
    )
    record = {}
    for name, run in archives.items():
        record[name] = dict(source=run, entries=write_archive(root / run, out / name))
    for name, (run, panel) in signals.items():
        state = json.loads((root / run / "run.json").read_text(encoding="utf-8"))
        entry = state["metadata"]["readiness"]["panels"][panel]["signals"]
        copy_checked(root / entry["path"], out / name, entry["sha256"])
        record[name] = dict(source=entry["path"])
    if results is not None:
        state = json.loads((root / results / "run.json").read_text(encoding="utf-8"))
        source = f"{results}/results.parquet"
        copy_checked(
            root / source, out / "results.parquet", state["artifact_sha256"]["results.parquet"]
        )
        record["results.parquet"] = dict(source=source)
    for name, entry in record.items():
        size = (out / name).stat().st_size
        if size >= LIMIT:
            raise SystemExit(f"{name}: {size:,} bytes is not under {LIMIT:,}")
        entry.update(bytes=size, sha256=sha256_file(out / name))
    summary = dict(
        assets=record,
        zlib=zlib.ZLIB_RUNTIME_VERSION,
        python=sys.version.split()[0],
        deflate_level=LEVEL,
        timestamp="1980-01-01 00:00:00",
    )
    text = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    (out / "assets.json").write_bytes(text.encode("utf-8"))
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    summary = build(args.out)
    print(f"zlib {summary['zlib']}, Python {summary['python']}, deflate level {LEVEL}")
    for name, entry in summary["assets"].items():
        entries = f", {entry['entries']} entries" if "entries" in entry else ""
        print(f"{name}: {entry['bytes']:,} bytes, SHA-256 {entry['sha256']}{entries}")


if __name__ == "__main__":
    main()

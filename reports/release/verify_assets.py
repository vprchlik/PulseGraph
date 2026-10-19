r"""Check downloaded release assets against `reports\release\ASSETS.md`, and unpack checkpoints.

From the repository root, PowerShell, after downloading the assets into one directory:

    .\.venv\Scripts\python.exe reports\release\verify_assets.py <directory>
    .\.venv\Scripts\python.exe reports\release\verify_assets.py <directory> --unpack all
    .\.venv\Scripts\python.exe reports\release\verify_assets.py <directory> --unpack <archive>

The check reads the table under "The assets" in `ASSETS.md`. For every asset found in the directory
it compares the size and the SHA-256 with the table; for an archive it also requires the entries to
be exactly the checkpoint names that the run's `run.json` implies (the SHA-256 of each completed
label, plus `.json`). For a copied file it reports whether the file at its place in the tree
matches. An asset missing from the directory is reported as absent and is not an error; any
mismatch is, and the command then exits with status 1.

`--unpack` writes an archive's checkpoints into its run directory, the place `ASSETS.md` names. It
does so only after the archive has passed the check, and only when the run directory holds no
checkpoint yet: a run directory holding any `<64 hex>.json` file is refused and nothing is written.
Every entry is hashed against `run.json` before the first file is written; files are created, never
overwritten; and every written file is hashed again on disk against `run.json`.

Standard library only; any Python 3.10 or later.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "reports" / "release" / "ASSETS.md"
HEADING = "## The assets"
CHECKPOINT = re.compile(r"^[0-9a-f]{64}\.json$")
TICKED = re.compile(r"`([^`]+)`")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _cells(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _ticked(cell, what, name):
    found = TICKED.findall(cell)
    if not found:
        raise ValueError(f"ASSETS.md: no {what} in backticks for {name}")
    return found[0]


def tree_path(root, text):
    """A path as ASSETS.md writes it (Windows separators, relative to the root) under `root`."""
    parts = [part for part in text.replace("\\", "/").split("/") if part]
    if not parts or any(part in (".", "..") for part in parts) or ":" in text:
        raise ValueError(f"ASSETS.md: {text} is not a path inside the repository")
    return Path(root, *parts)


def read_assets(path=ASSETS):
    """The rows of the first table under the heading "The assets": file, bytes, SHA-256, place."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == HEADING)
    except StopIteration:
        raise ValueError(f"ASSETS.md: no heading {HEADING!r}") from None
    table = []
    for line in lines[start + 1 :]:
        if line.startswith("|"):
            table.append(line)
        elif table:
            break
    if len(table) < 3:
        raise ValueError("ASSETS.md: the assets table is missing")
    header = _cells(table[0])
    try:
        column = {
            key: next(i for i, name in enumerate(header) if name.startswith(key))
            for key in ("File", "Bytes", "SHA-256", "Place")
        }
    except StopIteration:
        raise ValueError(f"ASSETS.md: the assets table's header is {header}") from None
    assets = []
    for line in table[2:]:
        cells = _cells(line)
        name = _ticked(cells[column["File"]], "file name", line)
        digest = _ticked(cells[column["SHA-256"]], "SHA-256", name)
        if not HEX64.match(digest) or "/" in name or "\\" in name:
            raise ValueError(f"ASSETS.md: the row for {name} is malformed")
        place = _ticked(cells[column["Place"]], "place", name)
        tree_path(".", place)
        assets.append(
            dict(
                file=name,
                bytes=int(cells[column["Bytes"]].replace(",", "")),
                sha256=digest,
                place=place,
                archive=name.endswith(".zip"),
            )
        )
    if len({asset["file"] for asset in assets}) != len(assets):
        raise ValueError("ASSETS.md: a file is listed twice")
    return assets


def expected_checkpoints(run):
    state = json.loads((Path(run) / "run.json").read_text(encoding="utf-8"))
    return {
        hashlib.sha256(label.encode()).hexdigest() + ".json": digest
        for label, digest in state["completed"].items()
    }


def present_checkpoints(run):
    return sorted(p.name for p in Path(run).iterdir() if p.is_file() and CHECKPOINT.match(p.name))


def _archive_names(path):
    with zipfile.ZipFile(path) as archive:
        return [info.filename for info in archive.infolist()]


def check_asset(directory, asset, root):
    """(ok, message) for one asset in the download directory."""
    path = Path(directory) / asset["file"]
    if not path.is_file():
        return True, f"ABSENT  {asset['file']}: not in {directory}"
    size = path.stat().st_size
    if size != asset["bytes"]:
        return False, f"FAIL    {asset['file']}: {size:,} bytes, ASSETS.md says {asset['bytes']:,}"
    digest = sha256_file(path)
    if digest != asset["sha256"]:
        return False, f"FAIL    {asset['file']}: SHA-256 {digest}, ASSETS.md says {asset['sha256']}"
    place = tree_path(root, asset["place"])
    if asset["archive"]:
        if not (place / "run.json").is_file():
            return (
                False,
                f"FAIL    {asset['file']}: no run.json at {asset['place']} (run from the root)",
            )
        names = _archive_names(path)
        expected = expected_checkpoints(place)
        if len(names) != len(set(names)) or set(names) != set(expected):
            return False, f"FAIL    {asset['file']}: its entries are not the checkpoints of {place}"
        present = len(present_checkpoints(place))
        return True, (
            f"OK      {asset['file']}: {size:,} bytes, SHA-256 matches; {len(names)} entries are "
            f"the checkpoints of {asset['place']} ({present} already there)"
        )
    if not place.is_file():
        where = "not yet placed"
    elif sha256_file(place) == asset["sha256"]:
        where = "the placed copy matches"
    else:
        return False, f"FAIL    {asset['file']}: the file at {asset['place']} differs"
    return True, f"OK      {asset['file']}: {size:,} bytes, SHA-256 matches; {where}"


def unpack(directory, asset, root):
    """Write the archive's checkpoints into its run directory; return the number written."""
    path = Path(directory) / asset["file"]
    run = tree_path(root, asset["place"])
    expected = expected_checkpoints(run)
    present = present_checkpoints(run)
    if present:
        raise SystemExit(
            f"Refused: {asset['place']} already holds {len(present)} checkpoint files; "
            "unpack only into an empty checkpoint set"
        )
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or set(names) != set(expected):
            raise SystemExit(
                f"Refused: the entries of {asset['file']} are not the run's checkpoints"
            )
        for info in infos:
            if hashlib.sha256(archive.read(info)).hexdigest() != expected[info.filename]:
                raise SystemExit(
                    f"Refused: {info.filename} in {asset['file']} differs from run.json"
                )
        for info in infos:
            data = archive.read(info)
            if hashlib.sha256(data).hexdigest() != expected[info.filename]:
                raise SystemExit(f"Stopped: {info.filename} read back differently")
            target = run / info.filename
            temporary = target.with_name(target.name + ".part")
            try:
                with temporary.open("xb") as stream:
                    stream.write(data)
            except FileExistsError:
                raise SystemExit(f"Stopped: {temporary} is left from an earlier attempt") from None
            if target.exists():
                temporary.unlink()
                raise SystemExit(f"Stopped: {target} appeared while unpacking")
            os.rename(temporary, target)
    wrong = [name for name in names if sha256_file(run / name) != expected[name]]
    if wrong:
        raise SystemExit(f"Stopped: {len(wrong)} written checkpoints differ from run.json")
    return len(names)


def main(argv=None, *, root=ROOT, assets_path=ASSETS):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("directory", type=Path, help="the directory holding the downloaded assets")
    parser.add_argument(
        "--unpack",
        action="append",
        default=[],
        metavar="ARCHIVE",
        help="an archive to unpack into its run directory, or 'all'; may be repeated",
    )
    args = parser.parse_args(argv)
    assets = read_assets(assets_path)
    by_name = {asset["file"]: asset for asset in assets}
    wanted = [a["file"] for a in assets if a["archive"]] if "all" in args.unpack else args.unpack
    unknown = [name for name in wanted if name not in by_name or not by_name[name]["archive"]]
    if unknown:
        parser.error(f"not an archive listed in ASSETS.md: {', '.join(unknown)}")
    results = {asset["file"]: check_asset(args.directory, asset, root) for asset in assets}
    for ok, message in results.values():
        print(message)
    failed = [name for name, (ok, _) in results.items() if not ok]
    for name in wanted:
        if name in failed or not (args.directory / name).is_file():
            print(f"Not unpacked: {name} is absent or failed the check")
            failed.append(name)
            continue
        written = unpack(args.directory, by_name[name], root)
        print(
            f"Unpacked {written} checkpoints into {by_name[name]['place']}; each matches run.json"
        )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

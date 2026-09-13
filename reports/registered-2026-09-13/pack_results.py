"""Store oversized completed results as byte-exact parts and verify reconstruction."""

import argparse
import hashlib
from pathlib import Path

from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json

PART_BYTES = 40 * 1024 * 1024
BASE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("pack", "restore"))
    args = parser.parse_args()
    target = BASE / "run/results.parquet"
    index_path = BASE / "run/results-parts.json"
    if args.action == "restore":
        index = read_json(index_path)
        if target.exists():
            if file_hash(target) != index["sha256"]:
                raise ValueError("Existing results differ; refusing to overwrite")
            print("Results already match the saved hash")
            return
        partial = target.with_suffix(".restoring")
        with partial.open("xb") as output:
            for part in index["parts"]:
                path = BASE / "run" / part["path"]
                if file_hash(path) != part["sha256"]:
                    raise ValueError("Part hash mismatch")
                output.write(path.read_bytes())
        if file_hash(partial) != index["sha256"]:
            raise ValueError("Reconstructed results hash mismatch")
        partial.rename(target)
        print("Restored byte-exact results.parquet")
        return
    state = read_json(BASE / "run/run.json")
    assert state["status"] == "complete"
    assert file_hash(target) == state["artifact_sha256"]["results.parquet"]
    # Recovery checkpoints duplicate the completed result rows and remain local.
    (BASE / ".gitignore").write_text("run/checkpoints/\n", encoding="utf-8")
    if target.stat().st_size <= PART_BYTES:
        print("Results fit in one tracked file; no packing needed")
        return
    if index_path.exists():
        raise FileExistsError("Results have already been packed")
    folder = BASE / "run/results-parts"
    folder.mkdir()
    parts = []
    combined = hashlib.sha256()
    with target.open("rb") as source:
        for number, chunk in enumerate(iter(lambda: source.read(PART_BYTES), b"")):
            part = folder / f"part-{number:03d}.data"
            part.write_bytes(chunk)
            combined.update(part.read_bytes())
            parts.append(
                {
                    "path": "results-parts/" + part.name,
                    "bytes": len(chunk),
                    "sha256": file_hash(part),
                }
            )
    assert combined.hexdigest() == file_hash(target)
    atomic_json(
        index_path,
        {
            "format": "ordered raw byte chunks; concatenate in listed order",
            "bytes": target.stat().st_size,
            "sha256": file_hash(target),
            "parts": parts,
            "restore_command": (
                ".\\.venv\\Scripts\\python.exe "
                "reports/registered-2026-09-13/pack_results.py restore"
            ),
        },
    )
    (BASE / ".gitignore").write_text("run/checkpoints/\nrun/results.parquet\n", encoding="utf-8")
    print(f"Packed {target.stat().st_size} bytes into {len(parts)} verified parts")


if __name__ == "__main__":
    main()

"""Verify actual reconstruction in a separate workspace directory."""

import argparse
import importlib.util
import os
import shutil
import sys
from pathlib import Path

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    out = args.out.resolve()
    out.relative_to(ROOT_DIR.resolve())
    if out.exists():
        raise FileExistsError("Use a new reconstruction directory")
    index = read_json(base / "run/results-parts.json")
    (out / "run/results-parts").mkdir(parents=True)
    shutil.copyfile(base / "run/results-parts.json", out / "run/results-parts.json")
    for part in index["parts"]:
        os.link(base / "run" / part["path"], out / "run" / part["path"])
    spec = importlib.util.spec_from_file_location(
        "pack_results_verification", base / "pack_results.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.BASE = out
    sys.argv = [str(base / "pack_results.py"), "restore"]
    module.main()
    restored = out / "run/results.parquet"
    assert file_hash(restored) == index["sha256"]
    assert restored.stat().st_size == index["bytes"]
    report = {
        "status": "pass",
        "bytes": index["bytes"],
        "parts": len(index["parts"]),
        "sha256": file_hash(restored),
        "verified_actual_restoration": True,
        "method": "Run the published restore function with linked input parts in a new directory",
        "command": (
            ".\\.venv\\Scripts\\python.exe reports/registered-2026-09-13/verify_packaging.py "
            "--out data/cache/packaging-check-2026-09-13"
        ),
        "script_sha256": file_hash(Path(__file__)),
    }
    atomic_json(base / "packaging-verification.json", report)
    print(report)


if __name__ == "__main__":
    main()

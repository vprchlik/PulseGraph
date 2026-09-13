"""Write the 18 confirmatory QScore9 comparisons without refitting models."""

import argparse
import sys
from pathlib import Path

from pulsegraph.evaluation.artifacts import file_hash, read_run_artifact
from pulsegraph.evaluation.confirmatory import confirmatory_tables
from pulsegraph.provenance import atomic_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("Choose a new inference directory")
    results, metadata, _ = read_run_artifact(args.run)
    if metadata["data_kind"] != "real" or metadata.get("status") != "complete":
        raise ValueError("Confirmatory reporting requires a complete registered run")
    inference, pairs = confirmatory_tables(
        results, metadata["specification"], metadata["comparison_family"]
    )
    args.out.mkdir(parents=True)
    inference.to_csv(args.out / "inference.csv", index=False)
    pairs.to_csv(args.out / "paired_repositories.csv", index=False)
    atomic_json(
        args.out / "inference.json",
        {
            "analysis": "registered_confirmatory",
            "protocol_commit": metadata["protocol_commit"],
            "source_run_sha256": file_hash(args.run / "run.json"),
            "comparison_family": metadata["comparison_family"],
            "command": [sys.executable, *sys.argv],
            "artifact_sha256": {
                name: file_hash(args.out / name)
                for name in ("inference.csv", "paired_repositories.csv")
            },
        },
    )


if __name__ == "__main__":
    main()

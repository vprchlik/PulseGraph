"""Report registered execution and inference without interpreting the comparisons."""

from datetime import datetime
from pathlib import Path

import pandas as pd
from summarize_descriptives import write_results

from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json


def main():
    base = Path(__file__).resolve().parent
    run = read_json(base / "run/run.json")
    gate = read_json(base / "gate.json")
    assert run["status"] == "complete" and gate["status"] == "pass"
    assert gate["readiness_sha256"] == run["readiness_sha256"]
    assert file_hash(base / "evidence/readiness.json") == run["readiness_sha256"]
    integrity = pd.read_csv(base / "integrity.csv")
    assert integrity.status.tolist() == ["pass"]
    inference = pd.read_csv(base / "inference/inference.csv")
    assert len(inference) == 18
    checkpoints = []
    for marker in sorted((base / "run/checkpoints").glob("*.json")):
        record = read_json(marker)
        assert record["run_identity"] == run["run_identity"]
        assert file_hash(marker.with_suffix(".parquet")) == record["sha256"]
        assert run["checkpoint_sha256"][record["repo_name"]] == record["sha256"]
        checkpoints.append(record)
    assert len(checkpoints) == 300
    pd.DataFrame(checkpoints).to_csv(base / "repository-timings.csv", index=False)
    seconds = (
        datetime.fromisoformat(run["finished_at"]) - datetime.fromisoformat(run["started_at"])
    ).total_seconds()
    report = {
        "gate": "pass",
        "run_status": run["status"],
        "started_at": run["started_at"],
        "finished_at": run["finished_at"],
        "elapsed_seconds_including_resumes": seconds,
        "failures": run["failures"],
        "resumes": run["resumes"],
        "integrity": integrity.to_dict("records"),
        "checkpoint_integrity": "pass",
        "checkpoint_count": len(checkpoints),
        "comparison_count": len(inference),
        "run_sha256": file_hash(base / "run/run.json"),
        "inference_sha256": file_hash(base / "inference/inference.csv"),
        "repository_timings_sha256": file_hash(base / "repository-timings.csv"),
        "mean_difference_definition": "model minus reference QScore9",
        "interval_definition": "pointwise 95% repository-cluster percentile bootstrap",
    }
    atomic_json(base / "execution-summary.json", report)
    write_results(base)
    print(report)
    print(inference.to_string(index=False))


if __name__ == "__main__":
    main()

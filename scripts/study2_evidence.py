"""Summarize saved metadata and synthetic smoke without reading any target values."""

import argparse
from datetime import date
from pathlib import Path

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json
from pulsegraph.study2.constants import PROTOCOL_COMMIT, PROTOCOL_SHA256


def reference(path):
    return dict(path=path.relative_to(ROOT_DIR).as_posix(), sha256=file_hash(path))


def summarize(smoke_path):
    raw = ROOT_DIR / "data/raw/study2"
    preflight = read_json(raw / "preflight/report.json")
    inventory = read_json(raw / "nyc311/inventory.json")
    failure = read_json(raw / "nyc311/incomplete.json")
    github_path = ROOT_DIR / "reports/registered-2026-09-13/run/manifest.json"
    github = read_json(github_path)
    endpoints = {r["observation_end"] for r in github}
    if len(endpoints) != 1:
        raise ValueError("Saved GitHub manifest has inconsistent endpoints")
    endpoint = endpoints.pop()
    bridge = (date(2026, 10, 1) - date.fromisoformat(endpoint)).days - 1
    smoke = read_json(smoke_path)
    if smoke.get("passed") is not True or smoke.get("data_kind") != "synthetic":
        raise ValueError("Synthetic smoke evidence required")
    seconds = {
        name: fit["load_seconds"] + len(github) * fit["forecast_seconds"]
        for name, fit in smoke["per_model"].items()
    }
    captures = []
    for directory in (raw / "preflight/captures", raw / "nyc311/captures"):
        for path in sorted(directory.glob("*.json")):
            record = read_json(path)
            if "request" not in record or not path.with_suffix(".response").exists():
                continue
            response = path.with_suffix(".response")
            if file_hash(response) != record["sha256"]:
                raise ValueError("Acquisition capture hash mismatch")
            captures.append(dict(metadata=reference(path), response=reference(response)))
    return dict(
        status="blocked_before_freeze",
        protocol_commit=PROTOCOL_COMMIT,
        protocol_sha256=PROTOCOL_SHA256,
        target_values_opened=False,
        real_forecasts_generated=False,
        sources=dict(
            github=dict(
                frozen_panel_size=len(github),
                manifest=reference(github_path),
                saved_snapshot_endpoint=endpoint,
                verified_freeze_source_day=None,
                bridge_if_using_saved_snapshot=bridge,
                leads_if_using_saved_snapshot=bridge + 30,
                status="fresh_source_completeness_evidence_required",
            ),
            npm=dict(
                probed_registry_documents=preflight["npm"]["inventory_size"],
                eligible_frame_size=None,
                achieved_strata=None,
                unfilled_strata=None,
                status="complete_creation_metadata_inventory_not_acquired",
                serial_spacing_days_lower_bound=preflight["npm"]["inventory_size"] / 86400,
                holdout_status="pending_readiness_deadline",
            ),
            nyc311=dict(
                inventory=reference(raw / "nyc311/inventory.json"),
                inventory_cells=len(inventory["entries"]),
                recognized_board_frame=sum(
                    not r.get("excluded_reason") for r in inventory["entries"]
                ),
                achieved_strata=None,
                unfilled_strata=None,
                status="context_acquisition_incomplete",
                failure=failure,
            ),
            wikipedia=dict(status="complete_inventory_not_acquired", achieved_strata=None),
        ),
        acquisition_evidence=captures,
        preflight=reference(raw / "preflight/report.json"),
        smoke=reference(smoke_path),
        smoke_hardware=smoke["hardware"],
        smoke_memory=smoke["memory"],
        per_model_synthetic_timing=smoke["per_model"],
        github_300_synthetic_projection_seconds=seconds,
        github_300_synthetic_projection_total_seconds=sum(seconds.values()),
        runtime_limitation=(
            "One synthetic series per model; excludes capture, JSON I/O and real-series fitting "
            "variability. Re-estimate from the final verified plan before author approval."
        ),
        gate_limitations=[
            "Implementation must be committed and smoke repeated at that HEAD",
            "Fresh complete source context snapshots required",
            "npm panel unresolved until its readiness deadline",
            "Separate signed freeze plan approval required",
            "External target access and evaluation require later separate readiness approval",
        ],
        regeneration_command=(
            ".\\.venv\\Scripts\\python.exe scripts\\study2_evidence.py "
            "--smoke study\\study2\\smoke_2026-09-14.json "
            "--out data\\cache\\study2-acquisition-status-reproduced.json"
        ),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("Evidence is immutable; choose a new output path")
    atomic_json(args.out, summarize(args.smoke.resolve()))


if __name__ == "__main__":
    main()

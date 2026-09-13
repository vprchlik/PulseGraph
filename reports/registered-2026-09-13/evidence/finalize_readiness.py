"""Assemble STOP 3 evidence after capture and committed-HEAD synthetic smoke. Never evaluate."""
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.registration import verify_source_registration, installed_versions, MODEL_PINS
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes

BASE = Path(__file__).resolve().parent
PANEL = BASE / "panel"


def evidence(path):
    return {"path": os.path.relpath(path, BASE).replace("\\", "/"), "sha256": sha256_bytes(path.read_bytes())}


def main():
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    source_error = None
    try:
        source_hashes = verify_source_registration(ROOT_DIR, head)
    except ValueError as error:
        if str(error) != "Implementation and study declarations must be committed and clean":
            raise
        source_hashes = None
        source_error = str(error)
    source_clean = source_hashes is not None
    smoke_path = BASE / ("runtime-smoke-final-" + head[:7] + ".json")
    smoke = read_json(smoke_path)
    assert smoke["implementation_commit"] == head and smoke["passed"]
    if source_clean:
        assert smoke["source_sha256"] == source_hashes
    else:
        assert (BASE / "smoke-source-provenance-final.json").exists()
    assert smoke["runtime_versions"] == installed_versions()
    summary = read_json(PANEL / "panel-summary.json")
    for name, digest in summary["artifacts"].items():
        assert sha256_bytes((PANEL / name).read_bytes()) == digest
    assert summary["n_accepted"] == 300
    assert all(s["sample_size"] == 100 for s in summary["strata"])
    original_comparison = BASE / "comparison/comparison.json"
    comparison = read_json(original_comparison)
    comparison["original_comparison_sha256"] = sha256_bytes(original_comparison.read_bytes())
    comparison["supplementary_outputs"] = {
        name: sha256_bytes((BASE / "comparison" / name).read_bytes())
        for name in ("repository_2024_totals.csv", "monthly_ratios_largest_eight.csv", "ratio-report.json",
                     "totals-and-monthly-ratios.md", "monthly-ratios.png", "monthly-ratios.svg",
                     "calendar-summary.json", "validation-calendar-audit.json", "validation-report.md")
    }
    atomic_json(BASE / "comparison/comparison-with-ratios.json", comparison)
    validation_provenance = read_json(BASE / "validation_2024/provenance.json")
    frame_path = BASE / "frame-retry-001/frame/provenance.json"
    frame_provenance = read_json(frame_path)
    assert frame_provenance["status"] == validation_provenance["status"] == "complete"
    queries = {
        "status": "both_exports_complete", "validation": evidence(BASE / "validation_2024/provenance.json"),
        "frame": evidence(frame_path), "original_failed_frame": evidence(BASE / "frame/provenance.json"),
        "failed_frame_reconciliation": evidence(BASE / "frame/job-reconciliation.json"),
        "frame_retry_authorization": evidence(BASE / "frame-retry-001/retry-authorization.json"),
        "cost_approval": evidence(BASE / "cost-approval.json"),
        "validation_export": evidence(BASE / "validation_2024/rows.csv"),
        "frame_export": evidence(BASE / "frame-retry-001/frame/rows.csv"),
        "completed_jobs_total_bytes_billed": sum(p["total_bytes_billed"] for p in (validation_provenance, frame_provenance)),
        "completed_jobs_cost_usd_before_credits": sum(p["query_charge_usd_from_billed_bytes_before_credits"] for p in (validation_provenance, frame_provenance)),
        "failed_job_billed_bytes": None, "failed_job_billing_note": "BigQuery supplied no processed/billed bytes for the quota-rejected job; not inferred as zero",
    }
    atomic_json(BASE / "query-provenance-final.json", queries)
    author = read_json(BASE / "author-interpretations.json")
    readiness = read_json(ROOT_DIR / "study/readiness.example.json")
    readiness.update(
        status=("Complete evidence; awaiting author signature; no real evaluation has run" if source_clean
                else "Data evidence complete and unsigned; local implementation commit still not visible; real-run gate remains blocked"),
        assembled_at=datetime.now(timezone.utc).isoformat(), implementation_commit=head,
        approved_by=None, approved_at=None, main_study_resolved=source_clean,
        implementation_working_tree_clean=source_clean,
        incomplete_reasons=[] if source_clean else [source_error + ". Author reports a commit, but this checkout still contains the hourly-validation changes at HEAD " + head],
        calendar_convention="America/Los_Angeles",
        bin_to_calendar_mapping=("Decode the UTC date label of each week timestamp and add the zero-based index in days[7]. "
            "Interpret the unchanged nominal label as an America/Los_Angeles calendar date with daylight saving. "
            "Do not convert the week timestamp to local time before labeling. The daily signal starts at created_at converted to the Los Angeles date "
            "and ends on 2026-08-31. Preserve the frame UTC creation_date and gross day-90 count separately. "
            "Build from complete raw weeks, retaining local birth-day counts before UTC creation midnight. Missing endpoint bins are never zero-filled."),
        timezone_evidence=author["timezone_evidence"], unstar_interpretation=author["unstar_interpretation"],
        later_information_limitation=("The target is surviving-star daily history as retrieved in September 2026. "
            "Stars subsequently removed, account removals and retrospective revisions can change historical measurements. "
            "Context-only forecasts use prefixes of this saved survivor history; they do not reconstruct gross additions or the counts known at historical cutoffs. "
            "The leakage tests prevent access to later rows in the saved snapshot, while this measurement limitation remains. "
            "Frame eligibility uses gross GH Archive counts and is not recomputed from endpoint survivors."),
        long_run_approval=("The author approved a two-to-eight-hour run budget on 2026-09-13. "
            "Foundation models run on the RTX 4070 SUPER GPU, batch size 1, and remain resident until the run ends; baselines run on CPU. "
            "The allocator budget is 7 GB and the operational peak ceiling is 8 GB. "
            "The real run starts only after the author supplies both signature fields and the registered gate passes. "
            "Per-repository checkpoints support resume; any failed window stops the run and is never skipped."),
        runtime_versions=smoke["runtime_versions"], signals_sha256=summary["artifacts"]["signals.parquet"],
        manifest_sha256=summary["artifacts"]["manifest.json"],
        run_spec_sha256=sha256_bytes((ROOT_DIR / "study/run_spec.json").read_bytes()),
        comparison_declaration_sha256=sha256_bytes((ROOT_DIR / "study/comparisons.json").read_bytes()),
        frame_sizes_and_skips=summary["strata"], skip_reasons=summary["skip_reasons"],
        signal_rows=summary["n_signal_rows"], model_pins=MODEL_PINS, hardware=smoke["hardware"],
    )
    role_paths = {
        "validation": ROOT_DIR / "data/raw/validation-2026-09-13/validation.json",
        "comparison": BASE / "comparison/comparison-with-ratios.json",
        "frame_coverage": BASE / "frame-coverage.json", "candidate_order": PANEL / "candidate-order.csv",
        "sampling_log": PANEL / "sampling-log.json", "cost_approval": BASE / "cost-approval.json",
        "query_provenance": BASE / "query-provenance-final.json", "smoke": smoke_path,
    }
    readiness["evidence"] = {role: evidence(path) for role, path in role_paths.items()}
    readiness["supplementary_evidence"] = {
        "author_interpretations": evidence(BASE / "author-interpretations.json"),
        "frame_freeze": evidence(PANEL / "freeze.json"), "panel_summary": evidence(PANEL / "panel-summary.json"),
        "request_log": evidence(PANEL / "request-log.jsonl"), "decisions": evidence(PANEL / "decisions.json"),
        "collection_script": evidence(BASE / "collect_panel.py"), "collection_helper_tests": evidence(BASE / "test_panel_helpers.py"),
        "ratios_script": evidence(BASE / "extend_ratios.py"), "plot_script": evidence(BASE / "plot_monthly_ratios.py"),
        "readiness_script": evidence(Path(__file__)),
        "name_lookup_audit": evidence(PANEL / "name-lookup-audit.json"),
        "acquisition_audit": evidence(PANEL / "acquisition-audit.json"),
    }
    if not source_clean:
        readiness["supplementary_evidence"]["smoke_source"] = evidence(BASE / "smoke-source-provenance-final.json")
        readiness["supplementary_evidence"]["pending_source"] = evidence(BASE / "pending-source.json")
    atomic_json(BASE / "readiness.json", readiness)
    assert readiness["timezone_evidence"] == author["timezone_evidence"]
    assert readiness["unstar_interpretation"] == author["unstar_interpretation"]

    fits = pd.DataFrame(smoke["fits"])
    warm = fits[fits.model.isin(MODEL_PINS) & fits["case"].gt(0)]
    timing = warm.groupby("model").seconds.agg(["count", "mean", "sum"]).reset_index()
    timing.to_csv(BASE / "smoke-foundation-timings-final.csv", index=False)
    lines = ["# PulseGraph readiness evidence", "",
             ("Evidence is complete. approved_by and approved_at are the only unsigned fields. No real-target evaluation has run." if source_clean else
              "All data evidence and hashes are complete, but this document is not yet signable. The reported hourly-validation commit is not visible in this checkout. "
              "approved_by and approved_at remain blank; main_study_resolved is false. No real-target evaluation has run."), "",
             f"Protocol: {readiness['protocol_commit']}. Protocol SHA-256: {readiness['protocol_sha256']}.", "",
             f"Implementation and synthetic smoke: {head}. " + ("Source and declarations are committed and clean." if source_clean else
              "Smoke ran from an exact clean archive of this HEAD; pending hourly-validation edits were excluded. "
              "A visible implementation commit and a refreshed smoke for that commit are still required."), "",
             "The registered selection seed is 20260913. The full eligible frame was ordered and hashed before the first target history request. "
             "The achieved panel is defined by public availability at fetch time and complete retrievable histories. Stable IDs preserve rename mappings. "
             "Every candidate encountered before each stratum's stop is logged as accepted or skipped with a reason.", "",
             "| Day-90 stratum | Eligible frame | Accepted | Skipped |", "|---|---:|---:|---:|"]
    for row in summary["strata"]:
        lines.append(f"| {row['sampling_stratum']} | {row['frame_size']:,} | {row['sample_size']} | {row['skip_count']} |")
    lines += ["", "| Stratum | Skip reason | Count |", "|---|---|---:|"]
    for row in summary["skip_reasons"]:
        lines.append(f"| {row['sampling_stratum']} | {row['reason']} | {row['count']} |")
    lines += ["", f"The manifest contains 300 stable repository IDs. The daily signal contains {summary['n_signal_rows']:,} rows, "
              "with every local-calendar day from repository creation through 2026-08-31 explicitly observed. No missing bins were imputed. "
              "The seeded walk replay, capture response hashes, identity/creation checks and observation-calendar checks passed.", "",
              f"Both completed queries billed {queries['completed_jobs_total_bytes_billed']:,} bytes, "
              f"approximately ${queries['completed_jobs_cost_usd_before_credits']:.4f} before credits at $6.25/TiB. "
              "Validation ran first; frame ran under its approved cap after the quota-rejected attempt. "
              "Both successful exports and the original rejected job retain provenance. Invoice credits are not inferred. "
              "All 872 expected physical daily tables were present and nonempty; this is table coverage, not proof that GH Archive captured every event.", "",
              "All 18 models passed synthetic smoke with batch size 1 and all three foundation models resident. "
              f"Peak reserved VRAM: {smoke['peak_vram_bytes']:,} bytes; peak allocated: {smoke['memory']['peak_allocated_bytes']:,} bytes. "
              "These are PyTorch allocator measurements with a 7 GB budget, 1 GB reserved for other CUDA overhead and an 8 GB operational ceiling. "
              f"Hardware: {smoke['hardware']['gpu_model']}; driver {smoke['hardware']['gpu_driver']}; "
              f"CUDA {smoke['hardware']['cuda_version']}; PyTorch {smoke['hardware']['pytorch_version']}.", "",
              "| Foundation model | Mean seconds per warm synthetic forecast |", "|---|---:|"]
    for row in timing.to_dict("records"):
        lines.append(f"| {row['model']} | {row['mean']:.4f} |")
    lines += ["", "The full-run planning estimate remains 2–8 hours. Six warm synthetic forecasts per foundation model support the GPU timing; "
              "CPU AutoARIMA search and shared hardware activity dominate uncertainty. No target forecasts informed this estimate.", "",
              "All 20 validation repositories were captured completely. The original hourly comparisons and DST transition detail are retained. "
              "The totals and monthly ratios below use equal exposure: January 1–December 30. December 31 lacks eight archive hours in the fixed 2024 UTC export.", "",
              "Author-accepted timezone_evidence (verbatim):", "", author["timezone_evidence"], "",
              "Author-accepted unstar_interpretation (verbatim):", "", author["unstar_interpretation"], "",
              (BASE / "comparison/totals-and-monthly-ratios.md").read_text(encoding="utf-8"), "",
              "Monthly-ratio figure: comparison/monthly-ratios.png (also saved as SVG).", "",
              "bin_to_calendar_mapping: " + readiness["bin_to_calendar_mapping"], "",
              "later_information_limitation: " + readiness["later_information_limitation"], "",
              "long_run_approval: " + readiness["long_run_approval"], "",
              "| Required evidence | SHA-256 |", "|---|---|"]
    for role, item in readiness["evidence"].items():
        lines.append(f"| {role} | {item['sha256']} |")
    lines += ["", "Manifest SHA-256: " + readiness["manifest_sha256"], "",
              "Signals SHA-256: " + readiness["signals_sha256"], "",
              "The machine-readable readiness.json records every evidence path, exact runtime versions, model revisions, source declarations and hardware. "
              "The raw captures are under ignored data/raw and staging evidence under ignored data/cache. The manifest and aggregate signals are saved and hash-frozen locally; "
              "their deliberate inclusion in the repository remains an author-performed commit.", "",
              "approved_by: unsigned", "", "approved_at: unsigned", ""]
    (BASE / "readiness-review.md").write_text("\n".join(lines), encoding="utf-8")
    print("Readiness evidence assembled; source clean=" + str(source_clean) + "; no evaluation invoked.")


if __name__ == "__main__":
    main()

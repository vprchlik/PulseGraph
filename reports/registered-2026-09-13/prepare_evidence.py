"""Freeze a portable evidence package and record the author's explicit signature."""

import shutil
from datetime import datetime, timezone
from pathlib import Path

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.registration import verify_readiness
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes

BASE = ROOT_DIR / "data/cache/stop3-2026-09-13"
OUT = Path(__file__).resolve().parent / "evidence"


def main():
    if (OUT / "readiness.json").exists():
        raise FileExistsError("Signed readiness is immutable; do not replace it")
    readiness = read_json(BASE / "readiness.json")
    assert readiness["implementation_working_tree_clean"] is True
    names = [
        "author-interpretations.json",
        "cost-approval.json",
        "frame-coverage.json",
        "query-provenance-final.json",
        "collect_panel.py",
        "test_panel_helpers.py",
        "extend_ratios.py",
        "plot_monthly_ratios.py",
        "finalize_readiness.py",
        "smoke-foundation-timings-final.csv",
        "audit_frame_coverage.py",
        "audit_validation_calendar.py",
        "summarize_comparison.py",
        readiness["evidence"]["smoke"]["path"],
        "frame-retry-001/retry-authorization.json",
    ]
    for folder in ("comparison", "panel", "validation_2024", "frame-retry-001/frame", "frame"):
        names.extend(str(p.relative_to(BASE)) for p in (BASE / folder).iterdir() if p.is_file())
    for name in sorted(set(names)):
        target = OUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(BASE / name, target)
    validation = OUT / "validation-capture/validation.json"
    validation.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT_DIR / "data/raw/validation-2026-09-13/validation.json", validation)
    readiness["evidence"]["validation"]["path"] = "validation-capture/validation.json"
    diagnostic = OUT / "panel-diagnostic/diagnostic.json"
    readiness["supplementary_evidence"].update(
        {
            "panel_diagnostic": {
                "path": "panel-diagnostic/diagnostic.json",
                "sha256": sha256_bytes(diagnostic.read_bytes()),
            },
            "panel_diagnostic_script": {
                "path": "../panel_diagnostic.py",
                "sha256": sha256_bytes((OUT.parent / "panel_diagnostic.py").read_bytes()),
            },
            "evidence_packaging_script": {
                "path": "../prepare_evidence.py",
                "sha256": sha256_bytes(Path(__file__).read_bytes()),
            },
        }
    )
    readiness["panel_diagnostic"] = read_json(diagnostic)
    readiness.update(
        status="Signed by explicit author instruction before the registered real run",
        approved_by="Victor Prchlik",
        approved_at=datetime.now(timezone.utc).isoformat(),
        main_study_resolved=True,
        calendar_convention="America/Los_Angeles",
        signature_authorization="Author's STOP 4 instruction: sign with Victor Prchlik and the UTC time of writing, then run the gate and registered evaluation if it passes.",
        raw_capture_location="Raw response bytes remain excluded under data/raw; the signed validation index and response hashes are retained. Aggregated inputs and query exports are included in this package.",
    )
    for group in ("evidence", "supplementary_evidence"):
        for role, item in readiness[group].items():
            assert sha256_bytes((OUT / item["path"]).read_bytes()) == item["sha256"], role
    verify_readiness(readiness, OUT, read_json(ROOT_DIR / "study/run_spec.json"))
    atomic_json(OUT / "readiness.json", readiness)
    report = (BASE / "readiness-review.md").read_text(encoding="utf-8")
    report = report.replace(
        "Evidence is complete. approved_by and approved_at are the only unsigned fields. No real-target evaluation has run.",
        "Evidence is complete and signed below by explicit author instruction. This signature precedes the registered run.",
    )
    report = report.replace("approved_by: unsigned", "approved_by: Victor Prchlik")
    report = report.replace("approved_at: unsigned", "approved_at: " + readiness["approved_at"])
    report = report.replace(
        "The raw captures are under ignored data/raw and staging evidence under ignored data/cache. The manifest and aggregate signals are saved and hash-frozen locally; their deliberate inclusion in the repository remains an author-performed commit.",
        "Raw captures remain under ignored data/raw. This package contains the frozen manifest, aggregate signals, query exports, comparison outputs and evidence hashes for the author-performed artifact commit.",
    )
    report += "\n" + (OUT / "panel-diagnostic/diagnostic.md").read_text(encoding="utf-8").replace(
        "reports/registered-2026-09-13/evidence/panel-diagnostic/diagnostic.json",
        "panel-diagnostic/diagnostic.json",
    )
    report += (
        "\nSigned readiness SHA-256: " + sha256_bytes((OUT / "readiness.json").read_bytes()) + "\n"
    )
    (OUT / "readiness-review.md").write_text(report, encoding="utf-8")
    print("Signed readiness at " + readiness["approved_at"])
    print("Implementation: " + readiness["implementation_commit"])
    print("Readiness SHA-256: " + sha256_bytes((OUT / "readiness.json").read_bytes()))


if __name__ == "__main__":
    main()

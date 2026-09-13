"""Regenerate descriptive diagnostics from the frozen achieved panel; never select."""

import argparse
from pathlib import Path

import pandas as pd

from pulsegraph.provenance import atomic_json, read_json, sha256_bytes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    manifest = pd.DataFrame(read_json(args.panel / "manifest.json"))
    signals = pd.read_parquet(args.panel / "signals.parquet")
    signals["event_date"] = pd.to_datetime(signals.event_date)
    rows = []
    for record in manifest.sort_values("repo_id").to_dict("records"):
        series = signals[signals.repo_id.eq(record["repo_id"])].set_index("event_date").stars
        birth = pd.Timestamp(record["observation_start"])
        frame_birth = pd.Timestamp(record["creation_date"])
        first90 = series.reindex(pd.date_range(birth, periods=90))
        nominal90 = series.reindex(pd.date_range(frame_birth, periods=90))
        last90 = series.reindex(pd.date_range(end="2026-08-31", periods=90))
        assert not first90.isna().any() and not nominal90.isna().any() and not last90.isna().any()
        assert record["day90_stars"] >= 20
        rows.append(
            {
                "repo_id": record["repo_id"],
                "repo_name": record["repo_name"],
                "sampling_stratum": record["sampling_stratum"],
                "local_creation_date": birth.date().isoformat(),
                "frame_utc_creation_date": frame_birth.date().isoformat(),
                "archive_day90_stars": record["day90_stars"],
                "surviving_day90_stars": int(first90.sum()),
                "surviving_to_archive_day90_ratio": float(first90.sum() / record["day90_stars"]),
                "surviving_frame_nominal90_stars": int(nominal90.sum()),
                "frame_nominal90_ratio": float(nominal90.sum() / record["day90_stars"]),
                "local_birth_precedes_utc_birth": bool(birth < frame_birth),
                "last90_stars": int(last90.sum()),
            }
        )
    detail = pd.DataFrame(rows)
    assert len(detail) == 300 and detail.repo_id.nunique() == 300
    panel = read_json(args.panel / "panel-summary.json")
    summaries = []
    for stratum in ("20-99", "100-999", "1000+"):
        subset = detail[detail.sampling_stratum.eq(stratum)]
        assert len(subset) == 100
        ratio = subset.surviving_to_archive_day90_ratio
        frame = next(item for item in panel["strata"] if item["sampling_stratum"] == stratum)
        summaries.append(
            {
                **frame,
                "ratio_median": float(ratio.median()),
                "ratio_p10": float(ratio.quantile(0.1, interpolation="linear")),
                "ratio_p90": float(ratio.quantile(0.9, interpolation="linear")),
                "ratio_below_0_5": int(ratio.lt(0.5).sum()),
                "last90_stars_median": float(subset.last90_stars.median()),
                "last90_zero_repositories": int(subset.last90_stars.eq(0).sum()),
                "local_birth_precedes_utc_birth": int(subset.local_birth_precedes_utc_birth.sum()),
            }
        )
    args.out.mkdir(parents=True, exist_ok=True)
    detail.to_csv(args.out / "repositories.csv", index=False)
    pd.DataFrame(summaries).to_csv(args.out / "strata.csv", index=False)
    pd.DataFrame(panel["skip_reasons"]).to_csv(args.out / "skip-reasons.csv", index=False)
    description = (
        "Descriptive diagnostic of the frozen achieved panel, not a selection criterion. "
        "The numerator sums the first 90 Los Angeles calendar days, beginning on local creation day; "
        "the denominator retains gross archive eligibility over the UTC creation date and next 89 UTC days. "
        "These are different calendar boundaries, so the ratio is not an exact unstar-retention probability. "
        "For boundary sensitivity, the per-repository table also sums survivor bins with nominal dates equal "
        "to the archive's 90 date labels; it does not reconstruct UTC-hour totals. "
        "The final 90 days are 2026-06-03 through 2026-08-31 inclusive in Los Angeles. "
        "Percentiles use linear interpolation across all 100 accepted repositories per stratum. "
        "No repository is removed, replaced or reweighted."
    )
    files = ("repositories.csv", "strata.csv", "skip-reasons.csv")
    atomic_json(
        args.out / "diagnostic.json",
        {
            "analysis_status": "descriptive_not_selection",
            "definition": description,
            "n_repositories": 300,
            "calendar_convention": "America/Los_Angeles",
            "input_sha256": {
                name: sha256_bytes((args.panel / name).read_bytes())
                for name in ("manifest.json", "signals.parquet", "panel-summary.json")
            },
            "script_sha256": sha256_bytes(Path(__file__).read_bytes()),
            "artifact_sha256": {
                name: sha256_bytes((args.out / name).read_bytes()) for name in files
            },
            "strata": summaries,
            "skip_reasons": panel["skip_reasons"],
            "regeneration": ".\\.venv\\Scripts\\python.exe reports/registered-2026-09-13/panel_diagnostic.py --panel reports/registered-2026-09-13/evidence/panel --out reports/registered-2026-09-13/evidence/panel-diagnostic",
        },
    )
    lines = [
        "## Descriptive panel diagnostic",
        "",
        description,
        "",
        "| Stratum | Accepted | Ratio median | P10 | P90 | Ratio <0.5 | Last-90 total median | Zero last-90 | Skipped |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| {row['sampling_stratum']} | {row['sample_size']} | {row['ratio_median']:.4f} | {row['ratio_p10']:.4f} | {row['ratio_p90']:.4f} | {row['ratio_below_0_5']} | {row['last90_stars_median']:.1f} | {row['last90_zero_repositories']} | {row['skip_count']} |"
        )
    lines.extend(["", "| Stratum | Skip reason | Count |", "|---|---|---:|"])
    for row in panel["skip_reasons"]:
        lines.append(f"| {row['sampling_stratum']} | {row['reason']} | {row['count']} |")
    lines.extend(
        [
            "",
            "Per-repository values, exact summaries and hashes are in [the diagnostic evidence](reports/registered-2026-09-13/evidence/panel-diagnostic/diagnostic.json).",
            "",
        ]
    )
    (args.out / "diagnostic.md").write_text("\n".join(lines), encoding="utf-8")
    print(pd.DataFrame(summaries).to_string(index=False))


if __name__ == "__main__":
    main()

"""Read-only check that every number in paper/main.tex and paper/SUMMARY.md matches its saved file.

Loads the CSV and JSON files under reports/registered-2026-09-13/, formats each figure the way the
report prints it, and asserts that the formatted text appears in main.tex or SUMMARY.md (whitespace
collapsed, so line wrapping does not matter). Version 1 numbers are checked against the preserved
documents under v1_reference/ when that local folder exists; otherwise they are listed as skipped.
Nothing is written. Run from the repository root:

    .\\.venv\\Scripts\\python.exe paper/check_numbers.py
"""

import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "registered-2026-09-13"
PAPER = ROOT / "paper"
MAIN = PAPER / "main.tex"
SUMMARY = PAPER / "SUMMARY.md"

MODELS = ["chronos2", "timesfm3", "timesfm2p5"]
LABEL = {"chronos2": "Chronos-2", "timesfm3": "TimesFM 3", "timesfm2p5": "TimesFM 2.5"}
HORIZONS = [7, 30, 90]
STRATA = ["20-99", "100-999", "1000+"]

failures = []
checks = 0
skipped = []


def text(path):
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


TEXT = {"main.tex": text(MAIN), "SUMMARY.md": text(SUMMARY)}


def expect(label, needle, files=("main.tex",)):
    """Assert that `needle` (whitespace collapsed) appears in each named file."""
    global checks
    needle = re.sub(r"\s+", " ", needle)
    for name in files:
        checks += 1
        if needle not in TEXT[name]:
            failures.append(f"{name}: {label}: expected text not found: {needle!r}")


def sci(p):
    mantissa, exponent = f"{p:.1e}".split("e")
    return f"${mantissa} \\times 10^{{{int(exponent)}}}$"


def fmt(value, places):
    return f"{value:.{places}f}"


# --- inference.csv: the 18 declared comparisons -----------------------
inference = pd.read_csv(REPORT / "inference" / "inference.csv")
assert len(inference) == 18 and inference["declared_count"].eq(18).all()
for reference in ["local_mean_28", "autoets_weekly"]:
    for model in MODELS:
        for horizon in HORIZONS:
            row = inference[
                (inference.model == model)
                & (inference.reference == reference)
                & (inference.horizon == horizon)
            ].iloc[0]
            wins = int(round(row.repo_win_rate * row.n_repos))
            line = (
                f"{LABEL[model]} & {horizon} & {fmt(row.mean_diff, 3)} & "
                f"[{fmt(row.mean_diff_ci_low, 3)}, {fmt(row.mean_diff_ci_high, 3)}] & "
                f"{fmt(row.median_diff, 4)} & {wins} & {fmt(row.repo_win_rate, 3)} & "
                f"{sci(row.wilcoxon_p_bh)} \\\\"
            )
            expect(f"inference row {model} {reference} {horizon}", line)

lm = inference[inference.reference == "local_mean_28"]
ae = inference[inference.reference == "autoets_weekly"]
lm_wins = (lm.repo_win_rate * lm.n_repos).round().astype(int)
ae_wins = (ae.repo_win_rate * ae.n_repos).round().astype(int)
expect(
    "wins range vs local mean",
    f"{lm_wins.min()} to {lm_wins.max()} of 300",
    ("main.tex", "SUMMARY.md"),
)
expect(
    "wins range vs autoets",
    f"{ae_wins.min()} to {ae_wins.max()} of 300",
    ("main.tex", "SUMMARY.md"),
)
excluding = int(((lm.mean_diff_ci_high < 0) | (lm.mean_diff_ci_low > 0)).sum())
assert excluding == 5, excluding
expect("intervals excluding zero", "excludes zero in five", ("main.tex", "SUMMARY.md"))
assert (lm.mean_diff < 0).all() and (lm.median_diff > 0).all()
assert (ae.mean_diff < 0).all() and (ae.median_diff < 0).all()
assert (inference.reject_bh_005).all()
expect("largest BH p vs local mean", f"{lm.wilcoxon_p_bh.max():.4f}", ("main.tex", "SUMMARY.md"))
expect("mean range vs local mean, low", f"{fmt(lm.mean_diff.max(), 3)}", ("main.tex", "SUMMARY.md"))
expect(
    "mean range vs local mean, high", f"{fmt(lm.mean_diff.min(), 3)}", ("main.tex", "SUMMARY.md")
)
ae7 = ae[ae.horizon == 7].mean_diff
ae90 = ae[ae.horizon == 90].mean_diff
expect(
    "autoets 7-day mean range", f"from $-{abs(ae7.max()):.2f}$ to $-{abs(ae7.min()):.2f}$ at 7 days"
)
expect(
    "autoets 90-day mean range", f"to $-{abs(ae90.max()):.2f}$ to $-{abs(ae90.min()):.2f}$ at 90"
)
expect(
    "summary autoets means",
    f"{fmt(ae7.max(), 2)} (Chronos-2, 7 days) to {fmt(ae90.min(), 2)}",
    ("SUMMARY.md",),
)
assert inference.n_bootstrap.eq(20000).all() and inference.seed.eq(20260914).all()
expect("bootstrap replicates", "20,000", ("main.tex", "SUMMARY.md"))

# --- post-hoc accounting ----------------------------------------------
posthoc = pd.read_csv(REPORT / "posthoc" / "posthoc-paired-summary.csv")
assert posthoc.analysis_status.eq("post_hoc").all()
fm_lm = posthoc[(posthoc.reference == "local_mean_28") & posthoc.model.isin(MODELS)]
for model in MODELS:
    for horizon in HORIZONS:
        row = fm_lm[(fm_lm.model == model) & (fm_lm.horizon == horizon)].iloc[0]
        parts = [
            row.qscore9_difference,
            row.zero_difference,
            row.positive_over_difference,
            row.positive_under_difference,
        ]
        assert abs(parts[0] - sum(parts[1:])) < 1e-9
        expect(
            f"post-hoc row {model} {horizon}",
            f"{LABEL[model]} & {horizon} & " + " & ".join(fmt(v, 3) for v in parts) + " \\\\",
        )
assert (fm_lm.zero_difference > 0).all() and (fm_lm.positive_over_difference < 0).all()
expect("zero-day part max", f"{fmt(fm_lm.zero_difference.max(), 3)}", ("main.tex", "SUMMARY.md"))
expect("zero-day part min", f"{fmt(fm_lm.zero_difference.min(), 3)}", ("SUMMARY.md",))
expect(
    "overprediction range",
    f"{fmt(fm_lm.positive_over_difference.max(), 3)} to "
    f"{fmt(fm_lm.positive_over_difference.min(), 3)}",
    ("SUMMARY.md",),
)
expect(
    "overprediction range (tex)",
    f"from ${fmt(fm_lm.positive_over_difference.max(), 3)}$ to "
    f"${fmt(fm_lm.positive_over_difference.min(), 3)}$",
)
under7 = fm_lm[fm_lm.horizon == 7].positive_under_difference
under90 = fm_lm[fm_lm.horizon == 90].positive_under_difference
assert (under7 < 0).all() and (under90 > 0).all()
for model in ["timesfm3", "timesfm2p5"]:
    row = fm_lm[(fm_lm.model == model) & (fm_lm.horizon == 7)].iloc[0]
    assert abs(row.positive_under_difference) > abs(row.positive_over_difference)
fm_ae30 = posthoc[
    (posthoc.reference == "autoets_weekly") & posthoc.model.isin(MODELS) & (posthoc.horizon == 30)
]
expect(
    "autoets h30 zero-day part range",
    f"between ${fmt(fm_ae30.zero_difference.max(), 3)}$ and "
    f"${fmt(fm_ae30.zero_difference.min(), 3)}$",
)
provenance = json.loads((REPORT / "posthoc" / "provenance.json").read_text(encoding="utf-8"))
assert (
    provenance["original_18_mean_differences_match"] and provenance["confirmatory_tests_added"] == 0
)
assert provenance["date"] == "2026-09-14"
expect("post-hoc date", "2026-09-14")

# --- the achieved panel -----------------------------------------------
strata = pd.read_csv(REPORT / "evidence" / "panel-diagnostic" / "strata.csv")
skips = pd.read_csv(REPORT / "evidence" / "panel-diagnostic" / "skip-reasons.csv")
panel = json.loads(
    (REPORT / "evidence" / "panel" / "panel-summary.json").read_text(encoding="utf-8")
)
assert int(strata.frame_size.sum()) == 148550
expect("eligible frame", "148,550", ("main.tex", "SUMMARY.md"))
assert panel["n_accepted"] == 300 and panel["n_skipped"] == 470
expect("skipped", "470", ("main.tex", "SUMMARY.md"))
expect("signal rows", f"{panel['n_signal_rows']:,}")
assert panel["calendar_convention"] == "America/Los_Angeles" and panel["selection_seed"] == 20260913
for stratum in STRATA:
    row = strata[strata.sampling_stratum == stratum].iloc[0]
    line = (
        f"{stratum.replace('-', '--')} & {int(row.frame_size):,} & {int(row.sample_size)} & "
        f"{int(row.skip_count)} & "
        f"{fmt(row.ratio_median, 3)} & {fmt(row.ratio_p10, 3)} & {fmt(row.ratio_p90, 3)} & "
        f"{int(row.last90_zero_repositories)} & {int(row.last90_stars_median)} \\\\"
    )
    expect(f"panel row {stratum}", line)
expect(
    "http 404 skips",
    f"{int(skips[skips.reason == 'id_resolver_http_404']['count'].sum())} with HTTP 404",
)
expect(
    "http 403 skips",
    f"{int(skips[skips.reason == 'id_resolver_http_403']['count'].sum())} with HTTP 403",
)
zeros = {
    s: int(strata[strata.sampling_stratum == s].last90_zero_repositories.iloc[0]) for s in STRATA
}
expect(
    "zero last-90 counts",
    f"{zeros['20-99']}, {zeros['100-999']} and {zeros['1000+']}",
    ("SUMMARY.md",),
)

regime = pd.read_csv(REPORT / "descriptive" / "qscore9-regime.csv")
one = regime[regime.model_name == "chronos2"].drop_duplicates("regime").set_index("regime")
for name, phrase in [
    ("Inactive recently", "320 windows from 140 repositories"),
    ("Other active", "572 windows from 228 repositories"),
    ("Recent surge", "8 windows from 7 repositories"),
]:
    assert (one.loc[name, "n_windows"], one.loc[name, "n_repos"]) == tuple(
        int(x) for x in re.findall(r"\d+", phrase)
    )
    expect(f"regime {name}", phrase)
expect("summary surge", "Eight windows from seven repositories", ("SUMMARY.md",))
expect("summary inactive", "320 windows from 140 repositories", ("SUMMARY.md",))

# --- the run ----------------------------------------------------------
execution = json.loads((REPORT / "execution-summary.json").read_text(encoding="utf-8"))
run = json.loads((REPORT / "run" / "run.json").read_text(encoding="utf-8"))
assert execution["gate"] == "pass" and execution["failures"] == [] and execution["resumes"] == []
assert execution["integrity"][0]["n_rows"] == 48600 and execution["checkpoint_count"] == 300
expect("forecast rows", "48,600", ("main.tex", "SUMMARY.md"))
seconds = execution["elapsed_seconds_including_resumes"]
assert int(seconds) == 18662 and int(seconds // 3600) == 5 and int(seconds % 3600 // 60) == 11
expect("elapsed", "18,662 seconds (5 hours and 11 minutes)")
expect("summary elapsed", "5 hours 11 minutes", ("SUMMARY.md",))
assert run["started_at"].startswith("2026-09-13T07:54") and run["finished_at"].startswith(
    "2026-09-13T13:05"
)
expect("run start", "2026-09-13 07:54 UTC")
assert run["implementation_commit"] == "ca67dd22ea49377ee1fd074aed57b4b7460c84f1"
expect("implementation commit", run["implementation_commit"])
expect("protocol commit", run["protocol_commit"], ("main.tex",))
expect("protocol sha", run["protocol_sha256"], ("main.tex",))
hw = run["hardware"]
expect("gpu", hw["gpu_model"])
expect("driver", hw["gpu_driver"])
expect("cuda", f"CUDA {hw['cuda_version']}")
expect("pytorch", f"PyTorch {hw['pytorch_version'].split('+')[0]}")
expect(
    "chronos package", f"\\texttt{{chronos-forecasting}} {run['packages']['chronos-forecasting']}"
)
expect("timesfm package", f"\\texttt{{timesfm}} {run['packages']['timesfm']}")
expect("statsforecast package", f"\\texttt{{statsforecast}} {run['packages']['statsforecast']}")
for fm in run["specification"]["foundation_models"]:
    expect(f"revision {fm['name']}", fm["revision"])
    expect(f"model id {fm['name']}", fm["model_id"].replace("_", "\\_"))
assert run["seeds"] == {"bootstrap": 20260914, "forecast": 20260912, "selection": 20260913}
expect("seeds", "selection 20260913, forecast 20260912, bootstrap 20260914")
cfg = run["config"]
assert cfg["cutoffs"] == ["2025-12-05", "2026-03-05", "2026-06-03"] and cfg["horizons"] == [
    7,
    30,
    90,
]
expect("cutoffs", "2025-12-05, 2026-03-05 and 2026-06-03")
assert run["observation_end"] == "2026-08-31" and run["comparison_count"] == 18
assert (
    run["artifact_sha256"]["results.parquet"]
    == "53ff5a5316fd43dd898866c4fc54edf913b080a32cbd696d7e3b3fc528f62df6"
)
expect("results.parquet sha", run["artifact_sha256"]["results.parquet"])

# --- readiness, validation and cost -----------------------------------
readiness = json.loads((REPORT / "evidence" / "readiness.json").read_text(encoding="utf-8"))
tz = re.sub(r"\s+", " ", readiness["timezone_evidence"])
assert "20 of 20 repositories against UTC and 18 of 20 against fixed UTC-8" in tz
expect("calendar evidence", "20 of 20 repositories against UTC and 18 of 20 against fixed UTC$-$8")
unstar = re.sub(r"\s+", " ", readiness["unstar_interpretation"])
assert "below the archive for 17 of 20 repositories" in unstar
expect("17 of 20", "17 of 20 repositories")
review = (REPORT / "evidence" / "readiness-review.md").read_text(encoding="utf-8")
assert "12,510,623,170,560 bytes, approximately $71.1147" in review
expect("bigquery bytes", "12,510,623,170,560 bytes")
expect("bigquery dollars", "\\$71.11")
validation = (REPORT / "evidence" / "comparison" / "validation-report.md").read_text(
    encoding="utf-8"
)
mad = {}
for calendar in ["America/Los_Angeles", "UTC", "UTC-08:00"]:
    mad[calendar] = float(
        re.search(rf"\| {re.escape(calendar)} \| ([0-9.]+) \|", validation).group(1)
    )
expect(
    "pooled MAD",
    f"{mad['America/Los_Angeles']:.3f} against {mad['UTC-08:00']:.3f} and {mad['UTC']:.3f}",
)
totals = pd.read_csv(REPORT / "evidence" / "comparison" / "repository_2024_totals.csv")
assert len(totals) == 20 and totals.n_matched_days.eq(365).all()
large = totals[totals.metadata_stars_at_capture >= 1000].api_to_archive_ratio
assert len(large) == 15 and (large < 1).all()
expect("large ratio range", f"from {large.min():.3f} to {large.max():.3f}")
below5 = int((large <= 0.95).sum())
expect("13 of 15", f"{below5} of 15", ("main.tex", "SUMMARY.md"))
assert int((totals.api_to_archive_ratio < 1).sum()) == 17

# --- descriptive tables -----------------------------------------------
stratum_table = pd.read_csv(REPORT / "descriptive" / "qscore9-sampling_stratum.csv")
for stratum in STRATA:
    for horizon in HORIZONS:
        vals = [
            stratum_table[
                (stratum_table.sampling_stratum == stratum)
                & (stratum_table.model_name == m)
                & (stratum_table.horizon == horizon)
            ].qscore9.iloc[0]
            for m in MODELS + ["local_mean_28", "autoets_weekly"]
        ]
        expect(
            f"stratum row {stratum} {horizon}",
            f"{stratum} & {horizon} & " + " & ".join(fmt(v, 3) for v in vals) + " \\\\",
        )
        if stratum == "1000+":
            assert all(v < vals[3] for v in vals[:3])
        if stratum == "20-99":
            assert all(v > vals[3] for v in vals[:3])
        if stratum == "100-999":
            assert max(vals[:4]) - min(vals[:4]) < 0.012
        assert vals[4] > max(vals[:4])

coverage = pd.read_csv(REPORT / "descriptive" / "autoets-coverage.csv")
widths = pd.read_csv(REPORT / "descriptive" / "autoets-widths-90.csv")
for stratum in STRATA:
    cov = [
        coverage[(coverage.sampling_stratum == stratum) & (coverage.horizon == h)].coverage_80.iloc[
            0
        ]
        for h in HORIZONS
    ]
    w = widths[widths.sampling_stratum == stratum].iloc[0]
    expect(
        f"autoets row {stratum}",
        f"{stratum.replace('-', '--')} & "
        + " & ".join(fmt(v, 3) for v in cov)
        + f" & {fmt(w.median_daily_width_80, 2)} & {fmt(w.median_fit_mean_width_80, 2)} & "
        + f"{int(w.multiplicative_seasonality_fits)} \\\\",
    )
assert int(widths.multiplicative_seasonality_fits.sum()) == 6
expect("multiplicative fits", "six fits that selected multiplicative seasonality")
daily = {s: widths[widths.sampling_stratum == s].median_daily_width_80.iloc[0] for s in STRATA}
expect(
    "autoets widths in text",
    f"{daily['20-99']:.2f} stars per day in the smallest stratum, {daily['100-999']:.2f} in the "
    f"middle one and {daily['1000+']:.2f} in the top one",
)
expect(
    "summary autoets top width",
    f"about {widths[widths.sampling_stratum == '1000+'].median_fit_mean_width_80.iloc[0]:.0f} "
    "stars per day",
    ("SUMMARY.md",),
)

calibration = pd.read_csv(REPORT / "descriptive" / "calibration.csv")
ranges = {}
for model in MODELS + ["local_mean_28", "autoets_weekly"]:
    cov = [
        calibration[
            (calibration.model_name == model) & (calibration.horizon == h)
        ].coverage_80.iloc[0]
        for h in HORIZONS
    ]
    expect(
        f"calibration row {model}",
        f"{model.replace('_', chr(92) + '_')} & " + " & ".join(fmt(v, 3) for v in cov) + " \\\\",
    )
    ranges[model] = (min(cov), max(cov))
expect(
    "coverage chronos2",
    f"{fmt(ranges['chronos2'][0], 3)} to {fmt(ranges['chronos2'][1], 3)} for Chronos-2",
)
expect(
    "coverage timesfm3",
    f"{fmt(ranges['timesfm3'][0], 3)} to {fmt(ranges['timesfm3'][1], 3)} for TimesFM 3",
)
expect(
    "coverage timesfm2p5",
    f"{fmt(ranges['timesfm2p5'][0], 3)} to {fmt(ranges['timesfm2p5'][1], 3)} for TimesFM 2.5",
)
expect(
    "coverage local mean",
    f"{fmt(ranges['local_mean_28'][0], 3)} to {fmt(ranges['local_mean_28'][1], 3)} "
    "for the local mean",
)
expect(
    "coverage autoets",
    f"{fmt(ranges['autoets_weekly'][0], 3)} to {fmt(ranges['autoets_weekly'][1], 3)} for AutoETS",
)
ae_pct = (ranges["autoets_weekly"][0] * 100, ranges["autoets_weekly"][1] * 100)
expect(
    "autoets coverage percent",
    f"{ae_pct[0]:.1f} to {ae_pct[1]:.1f} percent",
    ("main.tex", "SUMMARY.md"),
)

scale = pd.read_csv(REPORT / "descriptive" / "scale-local_mean_28.csv")
fm_scale = scale[scale.model_name.isin(MODELS)]
for model in MODELS:
    for horizon in HORIZONS:
        row = fm_scale[(fm_scale.model_name == model) & (fm_scale.horizon == horizon)].iloc[0]
        expect(
            f"scale row {model} {horizon}",
            f"{LABEL[model]} & {horizon} & {fmt(row.top5_positive_gain_share, 3)} & "
            f"{int(row.n_defined_skill)} & "
            f"[{fmt(row.leave_one_out_min_gain, 3)}, {fmt(row.leave_one_out_max_gain, 3)}] \\\\",
        )
assert (fm_scale.leave_one_out_min_gain > 0).all()
expect(
    "top-five share range",
    f"{fm_scale.top5_positive_gain_share.min() * 100:.1f} to "
    f"{fm_scale.top5_positive_gain_share.max() * 100:.1f} percent",
    ("main.tex", "SUMMARY.md"),
)
defined = [int(fm_scale[fm_scale.horizon == h].n_defined_skill.iloc[0]) for h in HORIZONS]
assert all(
    fm_scale[fm_scale.horizon == h].n_defined_skill.eq(defined[i]).all()
    for i, h in enumerate(HORIZONS)
)
expect("defined skill counts", f"{defined[0]}, {defined[1]} and {defined[2]} of 300")

# --- registration text: README.md and PROTOCOL.md ---------------------
readme = (ROOT / "README.md").read_text(encoding="utf-8")
protocol = re.sub(r"\s+", " ", (ROOT / "PROTOCOL.md").read_text(encoding="utf-8"))
for needle in [
    "df55867c982dfe2bb6e1152ec8ae93e3cd228c45",
    "33cefd8e34fea973e6747d1ba3fe565051e215c5d1b7f6553b266c1be7a66360",
    "433,172,286",
    "53ff5a5316fd43dd898866c4fc54edf913b080a32cbd696d7e3b3fc528f62df6",
]:
    assert needle in readme, needle
    expect(f"README value {needle[:12]}", needle)
assert "Freeze at 2026-09-28 18:00 UTC" in protocol
expect("holdout freeze", "2026-09-28 18:00 UTC")
assert "54 external, 6 synthetic and 18 prospective" in protocol
expect("study 2 families", "54 external tests")
expect("study 2 synthetic", "6 synthetic tests")
expect("study 2 prospective", "18 prospective tests")
addition = "dated addition, 2026-10-12" in protocol
if addition:
    assert "by 2026-10-20 23:59 UTC" in protocol and "E01 to E18" in protocol
    expect("dated addition cited", "dated addition of 2026-10-12")
else:
    skipped.append(
        "PROTOCOL.md has no dated addition of 2026-10-12; the report's citation of it is pending"
    )
registered_bytes = 18435
assert f"preceding {registered_bytes:,} bytes remain the registered Study 1 text" in protocol

# --- version 1, quoted from the preserved documents -------------------
v1 = ROOT / "v1_reference"
v1_rows = [
    ("breakout-selected", 7, "7.77", "6.43", "6.23"),
    ("breakout-selected", 30, "8.77", "7.90", "7.68"),
    ("breakout-selected", 90, "9.41", "8.52", "8.20"),
    ("steady-selected", 7, "1.66", "1.46", "1.44"),
    ("steady-selected", 30, "2.26", "2.04", "2.02"),
    ("steady-selected", 90, "2.42", "2.21", "2.22"),
    ("dead-selected", 7, "2.75", "2.43", "2.35"),
    ("dead-selected", 30, "2.64", "2.47", "2.39"),
    ("dead-selected", 90, "2.85", "2.73", "2.67"),
]
for cohort, horizon, local, chronos, timesfm in v1_rows:
    expect(
        f"v1 row {cohort} {horizon}", f"{cohort} & {horizon} & {local} & {chronos} & {timesfm} \\\\"
    )
v1_facts = [
    "208",
    "414,271",
    "2008-11-13",
    "2026-06-22",
    "179",
    "41",
    "69",
    "180 days",
    "40.6",
    "80.5",
    "5.02",
    "7.7",
    "78.0",
    "12.2",
    "2026-07-12",
]
if v1.exists():
    v1_results = (v1 / "RESULTS.md").read_text(encoding="utf-8")
    v1_audit = (v1 / "STUDY_AUDIT.md").read_text(encoding="utf-8")
    for cohort, horizon, local, chronos, timesfm in v1_rows:
        pattern = (
            rf"\| {cohort} \| {horizon} \| {re.escape(local)} \| "
            rf"\**{re.escape(chronos)}\** \| \**{re.escape(timesfm)}\** \|"
        )
        checks += 1
        if not re.search(pattern, v1_results):
            failures.append(f"v1 RESULTS.md: row {cohort} {horizon} not found")
    for fact in v1_facts:
        checks += 1
        if fact not in v1_results and fact not in v1_audit:
            failures.append(f"v1 documents: {fact} not found")
    checks += 1
    if "30–77%" not in v1_audit and "30-77%" not in v1_audit:
        failures.append("v1 audit: top-five share 30 to 77 percent not found")
else:
    skipped.append(
        "v1_reference/ is not present (local, gitignored); version 1 numbers not checked against it"
    )

# --- report -----------------------------------------------------------
for line in failures:
    print("FAIL", line)
for line in skipped:
    print("SKIP", line)
print(f"{checks} checks, {len(failures)} failures, {len(skipped)} skipped")
sys.exit(1 if failures else 0)

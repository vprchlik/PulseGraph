"""Read-only check that every number in paper/main.tex and paper/SUMMARY.md matches its saved file.

Loads the CSV and JSON files under reports/registered-2026-09-13/, formats each figure the way the
report prints it, and asserts that the formatted text appears in main.tex or SUMMARY.md (whitespace
collapsed, so line wrapping does not matter). The Study 2 sections under paper/sections/ are read
the same way and checked against study/study2/, reports/study2-npm/panel/, PROTOCOL.md and the
dated documents, as sources.md lists. Version 1 numbers are checked against the preserved
documents under v1_reference/ when that local folder exists; otherwise they are listed as skipped.
Nothing is written. Run from the repository root:

    .\\.venv\\Scripts\\python.exe paper/check_numbers.py
"""

import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "registered-2026-09-13"
PAPER = ROOT / "paper"
MAIN = PAPER / "main.tex"
SUMMARY = PAPER / "SUMMARY.md"
RECHECK = ROOT / "docs" / "research" / "2026-10-11-literature-recheck.md"

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


def whole_months(start, end):
    """Whole calendar months from `start` to `end` (both dates)."""
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return months


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
expect("intervals excluding zero", "excludes zero in five of nine", ("main.tex", "SUMMARY.md"))
assert (lm.mean_diff < 0).all() and (lm.median_diff > 0).all()
assert (ae.mean_diff < 0).all() and (ae.median_diff < 0).all()
assert (inference.reject_bh_005).all()
expect("largest BH p vs local mean", f"{lm.wilcoxon_p_bh.max():.4f}", ("main.tex", "SUMMARY.md"))
expect("mean range vs local mean, low", f"{fmt(lm.mean_diff.max(), 3)}", ("main.tex", "SUMMARY.md"))
expect(
    "mean range vs local mean, high", f"{fmt(lm.mean_diff.min(), 3)}", ("main.tex", "SUMMARY.md")
)
expect(
    "median range vs local mean",
    f"{fmt(lm.median_diff.min(), 4)} to {fmt(lm.median_diff.max(), 4)}",
    ("main.tex", "SUMMARY.md"),
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
expect(
    "zero-day part range",
    f"{fmt(fm_lm.zero_difference.min(), 3)} to {fmt(fm_lm.zero_difference.max(), 3)}",
    ("main.tex", "SUMMARY.md"),
)
# The zero-day part is small beside the mean gain and, cell by cell, exceeds the median (review 32).
cellwise = fm_lm.merge(lm, on=["model", "horizon"])
assert (cellwise.zero_difference > cellwise.median_diff).all()
assert (cellwise.zero_difference < cellwise.mean_diff.abs()).all()
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

# The post-hoc figures' descriptions (review 3): cumulative curves and the zero-fraction scatter.
curves = pd.read_csv(REPORT / "posthoc" / "posthoc-contribution-curves.csv")
paired = pd.read_csv(REPORT / "posthoc" / "posthoc-paired-repositories.csv")
for model in MODELS:
    rows = curves[
        (curves.reference == "local_mean_28") & (curves.model == model) & (curves.horizon == 30)
    ].sort_values("rank")
    total = rows.cumulative_qscore9_difference.to_numpy()
    fraction = rows.repository_fraction.to_numpy()
    # The total is at its final level within the first few percent of repositories (at 3 percent it
    # is already at or below its end value), bottoms out in the first half, then drifts upward.
    assert total[fraction <= 0.03][-1] <= total[-1] < 0, (model, total[fraction <= 0.03][-1])
    assert fraction[total.argmin()] < 0.5 and total[-1] > total.min()
    rows = curves[
        (curves.reference == "autoets_weekly") & (curves.model == model) & (curves.horizon == 30)
    ].sort_values("rank")
    # Against AutoETS the gain accrues across most of the panel: it still falls past 90 percent.
    total = rows.cumulative_qscore9_difference.to_numpy()
    fraction = rows.repository_fraction.to_numpy()
    assert total[fraction <= 0.9].min() > total.min() and (
        rows.cumulative_positive_over_difference.iloc[-1] < rows.cumulative_zero_difference.iloc[-1]
    )
    scatter = paired[
        (paired.reference == "local_mean_28") & (paired.model == model) & (paired.horizon == 30)
    ]
    gains = scatter.nsmallest(10, "qscore9_difference")
    losses = scatter[scatter.qscore9_difference > 0]
    assert gains.context_zero_fraction.max() < scatter.context_zero_fraction.median()
    assert losses.context_zero_fraction.median() > scatter.context_zero_fraction.median()
    scatter_ae = paired[
        (paired.reference == "autoets_weekly") & (paired.model == model) & (paired.horizon == 30)
    ]
    assert (scatter_ae.qscore9_difference < 0).mean() > 0.95
checks += 1

# The typical repository by stratum: a post-hoc reading of the per-repository file (review 31).
assert paired.analysis_status.eq("post_hoc").all()
by_stratum = paired[(paired.reference == "local_mean_28") & paired.model.isin(MODELS)]
grouped = by_stratum.groupby(["sampling_stratum", "model", "horizon"]).qscore9_difference
lower = grouped.apply(lambda s: int((s < 0).sum()))
medians = grouped.median()
assert (medians > 0).all() and grouped.size().eq(100).all()
stratum_lower = {s: (lower.loc[s].min(), lower.loc[s].max()) for s in STRATA}
expect(
    "typical repository by stratum",
    f"{stratum_lower['20-99'][0]} to {stratum_lower['20-99'][1]} of 100 repositories in the "
    f"smallest stratum, {stratum_lower['100-999'][0]} to {stratum_lower['100-999'][1]} in the "
    f"middle one and {stratum_lower['1000+'][0]} to {stratum_lower['1000+'][1]} in the top one",
    ("main.tex", "SUMMARY.md"),
)

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

# The creation dates and the mature-phase months, from the frozen manifest (review 3).
manifest = pd.DataFrame(
    json.loads((REPORT / "run" / "manifest.json").read_text(encoding="utf-8-sig"))
)
assert len(manifest) == 300 and manifest.coverage_complete.all()
created = pd.to_datetime(manifest.creation_date).dt.date
starts = pd.to_datetime(manifest.observation_start)
assert int(((pd.Timestamp("2026-08-31") - starts).dt.days + 1).sum()) == panel["n_signal_rows"]
expect("creation date range", f"{created.min()} to {created.max()}")
months_min = whole_months(created.max(), date(2025, 12, 5))
months_max = whole_months(created.min(), date(2026, 6, 3))
assert (months_min, months_max) == (9, 41), (months_min, months_max)
expect("mature phase, least", "at least nine months before the first cutoff")
expect("mature phase, range", "between nine and 41 months after creation")

regime = pd.read_csv(REPORT / "descriptive" / "qscore9-regime.csv")
one = regime[regime.model_name == "chronos2"].drop_duplicates("regime").set_index("regime")
assert int(one.n_windows.sum()) == 900
expect("window count", "900 repository-cutoff windows")
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
# The inference settings and the baseline count (review 3).
spec = run["specification"]
assert spec["inference"]["max_context"] == 2048 and spec["inference"]["n_samples"] == 200
expect("maximum context", f"{spec['inference']['max_context']:,}-day maximum context")
expect("context-level draws", f"{spec['inference']['n_samples']} empirical context-level draws")
expect("empirical quantile draws", f"quantiles of {spec['inference']['n_samples']} draws")
primary = {"local_mean_28", "autoets_weekly"}
assert primary <= set(spec["baselines"]) and len(spec["baselines"]) == 15
assert len(spec["baselines"]) - len(primary) == 13
expect("secondary baseline count", "Thirteen secondary baselines")
expect("secondary baseline count, body", "thirteen secondary baselines")

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
# The per-repository calendar table: LA MAD / agreement, fixed UTC-8, UTC (review 5).
per_repo = re.findall(
    r"^\| ([^|]+?) \| ([0-9.]+) / [0-9.]+% \| ([0-9.]+) / [0-9.]+% \| ([0-9.]+) / [0-9.]+% \|$",
    validation,
    flags=re.M,
)
assert len(per_repo) == 20, len(per_repo)
la_vs_utc = sum(float(la) < float(utc) for _, la, _, utc in per_repo)
la_vs_fixed = sum(float(la) < float(fixed) for _, la, fixed, _ in per_repo)
ties = sum(float(la) == float(fixed) for _, la, fixed, _ in per_repo)
assert (la_vs_utc, la_vs_fixed, ties) == (20, 18, 2), (la_vs_utc, la_vs_fixed, ties)
expect("calendar ties", "two repositories tied between the Los Angeles and fixed-offset calendars")
totals = pd.read_csv(REPORT / "evidence" / "comparison" / "repository_2024_totals.csv")
assert len(totals) == 20 and totals.n_matched_days.eq(365).all()
large = totals[totals.metadata_stars_at_capture >= 1000].api_to_archive_ratio
assert len(large) == 15 and (large < 1).all()
expect("large ratio range", f"from {large.min():.3f} to {large.max():.3f}")
below5 = int((large <= 0.95).sum())
expect("13 of 15", f"{below5} of 15", ("main.tex", "SUMMARY.md"))
percent_below = 100 * (1 - large[large <= 0.95])
expect(
    "summary survivor percent range",
    f"{percent_below.min():.0f} to {percent_below.max():.0f} percent below",
    ("SUMMARY.md",),
)
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
# The multiplicative fits, from the per-fit file: six per horizon, two repositories (review 28).
fits = pd.read_csv(REPORT / "descriptive" / "autoets-fits.csv")
mult = fits[fits.multiplicative_seasonality]
assert len(mult) == 18 and mult.groupby("horizon").size().eq(6).all()
assert mult.repo_name.nunique() == 2 and set(mult.sampling_stratum) == {"1000+"}
expect("multiplicative fits", "Six fits at each horizon, from two repositories")
daily = {s: widths[widths.sampling_stratum == s].median_daily_width_80.iloc[0] for s in STRATA}
expect(
    "autoets widths in text",
    f"{daily['20-99']:.2f} stars per day in the smallest stratum, {daily['100-999']:.2f} in the "
    f"middle one and {daily['1000+']:.2f} in the top one",
)
expect(
    "summary autoets top width",
    f"median 90-day daily interval width in the top stratum is {daily['1000+']:.2f} stars per day",
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
assert round(ae_pct[0]) == 99 and round(ae_pct[1]) == 99
expect("autoets coverage rounded", "about 99 percent", ("main.tex", "SUMMARY.md"))

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

# --- registration text: README.md, PROTOCOL.md and the literature re-check -------------
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
assert "to be filled" in readme
expect("release asset pending", "is to be published as a GitHub release asset")
assert "Freeze at 2026-09-28 18:00 UTC" in protocol
expect("holdout freeze", "2026-09-28 18:00 UTC")
assert "54 external, 6 synthetic and 18 prospective" in protocol
expect("study 2 families", "54 external tests")
expect("study 2 synthetic", "6 synthetic tests")
expect("study 2 prospective", "18 prospective tests")
assert "repositories created on or after 2026-09-13" in protocol
expect("study 1 follow-up", "repositories created on or after 2026-09-13")
addition = "dated addition, 2026-10-12" in protocol
if addition:
    assert "by 2026-10-20 23:59 UTC" in protocol and "E01 to E18" in protocol
    expect("dated addition cited", "dated addition of 2026-10-12")
    expect("dated addition commit", "committed at \\texttt{8db0d73}")
    try:
        git = subprocess.run(
            ["git", "-C", str(ROOT), "log", "--format=%h %s", "-n", "100"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        skipped.append(
            "git log unavailable; the commit 8db0d73 of the dated addition not confirmed"
        )
    else:
        checks += 1
        if not any(line.startswith("8db0d73") for line in git.splitlines()):
            failures.append("git log: commit 8db0d73 (the dated addition of 2026-10-12) not found")
else:
    skipped.append(
        "PROTOCOL.md has no dated addition of 2026-10-12; the report's citation of it is pending"
    )
registered_bytes = 18435
assert f"preceding {registered_bytes:,} bytes remain the registered Study 1 text" in protocol
expect("study 2 status date", "As of 2026-10-12")
status = json.loads(
    (ROOT / "study" / "study2" / "acquisition_status.json").read_text(encoding="utf-8")
)
assert not status["target_values_opened"] and not status["real_forecasts_generated"]

# The pinned revision dates, from the literature re-check's model-card table (review 19).
recheck = RECHECK.read_text(encoding="utf-8")
cards = recheck[recheck.index("## Model cards and training data") :]
for revision, dated in [
    ("1d95242", "2025-10-02"),
    ("43046b8", "2026-09-02"),
    ("29ec376", "2026-06-05"),
]:
    line = next(line for line in cards.splitlines() if f"`{revision}`" in line)
    assert dated in line, (revision, dated)
    expect(f"revision date {revision}", f"dated {dated}")
assert "weights uploaded 2026-08-24" in recheck
expect("timesfm3 weights upload", "weights uploaded 2026-08-24")

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
expect("v1 headline", "6.2 to 8.5 against 11.2 to 28.0")
expect("v1 concentration", "roughly 30 to 77 percent")
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
    # The headline range from the Section 4.1 table: breakout rows, four baselines and two models.
    section = v1_results[v1_results.index("### 4.1") : v1_results.index("### 4.2")]
    breakout = re.findall(r"^\| breakout \| \d+ +\| (.+) \|$", section, flags=re.M)
    assert len(breakout) == 3, breakout
    cells = [[float(c.strip().strip("*")) for c in row.split("|")] for row in breakout]
    baselines = [v for row in cells for v in row[:4]]
    models = [v for row in cells for v in row[4:6]]
    checks += 1
    headline = (
        f"{min(models):.1f} to {max(models):.1f} against "
        f"{min(baselines):.1f} to {max(baselines):.1f}"
    )
    if headline != "6.2 to 8.5 against 11.2 to 28.0":
        failures.append(f"v1 RESULTS.md Section 4.1: headline range is {headline}")
else:
    skipped.append(
        "v1_reference/ is not present (local, gitignored); version 1 numbers not checked against it"
    )

# --- the Study 2 sections under paper/sections/ (added 2026-10-15) ------------------------------
# The four section files are read like main.tex. Each figure in them traces to a file under
# study/study2/, reports/study2-npm/panel/, PROTOCOL.md or a dated document, as sources.md lists.
SECTIONS = PAPER / "sections"
S2 = ROOT / "study" / "study2"
NPM = ROOT / "reports" / "study2-npm" / "panel"
QUESTION, DESIGN, PANEL, PLACEHOLDER = (
    "study2-question.tex",
    "study2-design.tex",
    "study2-panel.tex",
    "study2-results-placeholder.tex",
)
for name in (QUESTION, DESIGN, PANEL, PLACEHOLDER):
    TEXT[name] = text(SECTIONS / name)
Q, D, P, R = (QUESTION,), (DESIGN,), (PANEL,), (PLACEHOLDER,)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def esc(name):
    return name.replace("_", "\\_")


# The public boundary: no operating-layer vocabulary in a committed section.
for name in (QUESTION, DESIGN, PANEL, PLACEHOLDER):
    checks += 1
    hits = [
        w
        for w in ("Claude", "Opus", "Fable", "Anthropic", "OpenAI", "session", "chat")
        if w in TEXT[name]
    ]
    if hits:
        failures.append(f"{name}: operating-layer vocabulary {hits}")

# Registration identity, shared by the four files and the two declarations.
pkg_spec = load(S2 / "external_packages_spec.json")
syn_spec = load(S2 / "synthetic_spec.json")
assert pkg_spec["protocol_commit"] == syn_spec["protocol_commit"]
assert pkg_spec["protocol_commit"] == "df55867c982dfe2bb6e1152ec8ae93e3cd228c45"
assert (
    pkg_spec["protocol_sha256"]
    == "33cefd8e34fea973e6747d1ba3fe565051e215c5d1b7f6553b266c1be7a66360"
)
expect("study 2 registration commit", pkg_spec["protocol_commit"], Q)
expect("study 2 registration sha", pkg_spec["protocol_sha256"], Q)
expect("study 2 registration commit, short", "\\texttt{df55867}", D)
assert "Study 2 — dated addition, 2026-09-14" in protocol
expect("study 2 registration date", "registered on 2026-09-14", Q + D)
try:
    git_protocol = subprocess.run(
        ["git", "-C", str(ROOT), "log", "--format=%h %cs", "--", "PROTOCOL.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
except (OSError, subprocess.CalledProcessError):
    git_protocol = None
    skipped.append(
        "git log unavailable; the protocol commits df55867, 8db0d73 and 5be2ce9 not confirmed"
    )
else:
    checks += 1
    dated = {line.split()[0]: line.split()[1] for line in git_protocol}
    for short, day in [
        ("df55867", "2026-09-14"),
        ("8db0d73", "2026-10-12"),
        ("5be2ce9", "2026-10-15"),
    ]:
        if dated.get(short) != day:
            failures.append(
                f"git log -- PROTOCOL.md: commit {short} not dated {day}: {dated.get(short)}"
            )
expect("addition 2026-10-12 commit", "committed at \\texttt{8db0d73}", D)
expect("addition 2026-10-15 commit", "committed at \\texttt{5be2ce9}", D)
assert "Discrete CRPS availability — dated addition, 2026-10-15" in protocol
expect("addition 2026-10-15 named", "the addition of 2026-10-15", D)

# The question section reuses three Study 1 figures already asserted above.
expect(
    "question: zero-day range",
    f"{fmt(fm_lm.zero_difference.min(), 3)} to {fmt(fm_lm.zero_difference.max(), 3)}",
    Q,
)
expect(
    "question: median range", f"{fmt(lm.median_diff.min(), 4)} to {fmt(lm.median_diff.max(), 4)}", Q
)
expect("question: wins range", f"{lm_wins.min()} to {lm_wins.max()} of 300", Q)
assert "Searches run 2026-10-12" in recheck
expect("question: re-check date", "run on 2026-10-12", Q)
expect("question: as-of date", "as of 2026-10-12", Q)
assert "This hypothesis arose after Study 1 and is tested on separately declared data" in protocol
assert (
    "Completion below is a Study 2 assumption, never attributed retrospectively to Study 1"
    in protocol
)

# Every citation key in the sections has a bib entry, and the re-check holds each item's identifier.
bib = (PAPER / "references.bib").read_text(encoding="utf-8")
bib_keys = set(re.findall(r"^@\w+\{([^,]+),", bib, flags=re.M))
cited = set()
for name in (QUESTION, DESIGN, PANEL, PLACEHOLDER):
    for group in re.findall(r"\\citep\{([^}]*)\}", TEXT[name]):
        cited.update(k.strip() for k in group.split(","))
checks += 1
missing = sorted(cited - bib_keys)
if missing:
    failures.append(f"sections cite keys absent from references.bib: {missing}")
for key, marker in [
    ("schoess2026", "2609.39386"),
    ("chin2026", "2609.13840"),
    ("ebrahim2026", "2610.00589"),
    ("islam2026", "2609.27867"),
    ("moghadasi2026", "2609.10357"),
    ("garza2026", "2603.08707"),
    ("kim2026", "10.13106/jidb.2026.vol17.no3.89"),
    ("tsantilis2025", "10.1109/ICTMOD66732.2025.11371783"),
    ("zodiac2026", "zodiac-zero-inflated-overshoot-controlled-dual-head-integration"),
    ("meyer2025", "2510.13654"),
    ("damato2026", "2609.28607"),
    ("bai2026", "2511.12749"),
    ("exaone2026", "2609.30880"),
    ("fevbench2026", "2509.26468"),
]:
    checks += 1
    assert key in cited, key
    if marker not in recheck or marker not in bib:
        failures.append(f"citation {key}: identifier {marker} not in both the re-check and the bib")

# --- the design -------------------------------------------------------
assert (
    "Each aims at 300 series: 100 in each context-zero-fraction stratum [0,0.5), [0.5,0.9), [0.9,1]"
    in protocol
)
expect(
    "design: strata",
    "300 series, 100 in each of three context-zero-fraction strata, $[0, 0.5)$, $[0.5, 0.9)$ and "
    "$[0.9, 1]$",
    D,
)
assert "the first min(10000,N) metadata-eligible keys" in protocol
expect("design: pool", "$\\min(10{,}000, N)$", D)
seeds = pkg_spec["seeds"]
assert (
    seeds
    == syn_spec["seeds"]
    == {
        "bootstrap": 20260917,
        "forecast": 20260915,
        "pit": 20260916,
        "prospective": 20260919,
        "selection": 20260914,
        "synthetic": 20260918,
    }
)
expect(
    "design: seeds",
    f"selection {seeds['selection']}, forecasts {seeds['forecast']}, PIT {seeds['pit']}, bootstrap "
    f"{seeds['bootstrap']}, synthetic {seeds['synthetic']} and prospective {seeds['prospective']}",
    D,
)
expect("design: selection seed", f"selection seed {seeds['selection']}", D)
cal = pkg_spec["calendar"]
assert cal == syn_spec["calendar"]
endpoint = date.fromisoformat(cal["endpoint"])
cutoffs = [str(endpoint - timedelta(days=30 * j - 1)) for j in (3, 2, 1)]
assert cutoffs == cal["cutoffs"] == ["2026-06-03", "2026-07-03", "2026-08-02"], cutoffs
start = date.fromisoformat(cal["context_start"])
context_days = [(date.fromisoformat(c) - start).days for c in cal["cutoffs"]]
assert context_days == [275, 305, 335], context_days
assert cal["strata_start"] == "2026-03-05" and cal["horizons"] == [7, 30]
assert (date.fromisoformat(cal["cutoffs"][0]) - date.fromisoformat(cal["strata_start"])).days == 90
expect(
    "design: A and E", f"$A$ = {cal['context_start']}, common endpoint $E$ = {cal['endpoint']}", D
)
expect(
    "design: cutoffs",
    f"{cutoffs[0]}, {cutoffs[1]} and {cutoffs[2]}, with {context_days[0]}, {context_days[1]} and "
    f"{context_days[2]} context days",
    D,
)
expect(
    "design: strata window",
    f"{cal['strata_start']} through {date.fromisoformat(cal['cutoffs'][0]) - timedelta(days=1)}",
    D,
)
for fm in pkg_spec["foundation_models"]:
    expect(f"design: revision {fm['name']}", fm["revision"], D)
    expect(f"design: model id {fm['name']}", esc(fm["model_id"]), D)
comp = pkg_spec["completion"]
assert comp["tail_scale"] == "max(1,q0.9-q0.8)" and comp["rounding"] == "floor(Q(U)+0.5)"
assert (
    comp["interpolation"] == "linear"
    and comp["lower_knot"] == [0, 0]
    and comp["fm_fallback"] == "F0_equals_one_only"
)
expect("design: tail scale", "$s = \\max(1, q_{0.9} - q_{0.8})$", D)
expect("design: rounding", "\\lfloor Q(U) + 0.5 \\rfloor", D)
hurdles = pkg_spec["count_hurdles"]
assert hurdles == {
    "fallback": "delta_1",
    "lookback": 28,
    "minimum_positives": 2,
    "occurrence": "(n_positive+0.5)/29",
}
expect("design: jeffreys", "$p = (n_{+} + 1/2) / 29$", D)
expect("design: lookback", "last 28 context days", D)
dyn = pkg_spec["dynamic_count"]
assert dyn["discount"] == 0.98 and dyn["initial_parameters"] == [0.5] * 4
assert dyn["fallback"] == "hurdle_count_28_if_fewer_than_two_recent_positives"
expect("design: discount", "multiplied by $0.98$", D)
assert len(pkg_spec["baselines"]) == 7 and pkg_spec["baselines"] == syn_spec["baselines"]
expect("design: baseline count", "Seven baselines", D)
for baseline in pkg_spec["baselines"]:
    expect(f"design: baseline {baseline}", esc(baseline), D)
crps = pkg_spec["crps"]
assert crps["tolerance"] == 1e-8 and crps["max_k"] == 1000000
expect("design: crps tolerance", "below $10^{-8}$", D)
expect("design: crps limit", "$k = 1{,}000{,}000$", D)
assert "has its discrete CRPS recorded as unavailable" in protocol

external54 = load(S2 / "external_comparisons.json")
assert external54["comparison_count"] == 54 and len(external54["comparisons"]) == 54
expect("design: 54", "one external family of 54 tests", D)
expect("design: 54 product", "$3 \\times 3 \\times 2 \\times 3 = 54$", D)
family = load(S2 / "external_packages_comparisons.json")
assert family["comparison_count"] == 18 and len(family["comparisons"]) == 18
assert family["comparisons"] == external54["comparisons"][:18]
assert family["authority"]["commit"].startswith("8db0d73")
assert family["q"] == 0.05 and family["adjustment"] == "BH" and family["alternative"] == "two-sided"
assert family["bootstrap_replicates"] == 20000 and family["bootstrap_seed"] == seeds["bootstrap"]
assert (
    family["test"] == "wilcoxon" and family["all_zero_p"] == 1.0 and family["metric"] == "qscore9"
)
expect("design: BH", "one Benjamini-Hochberg adjustment at $q = 0.05$", D)
expect("design: bootstrap", f"{family['bootstrap_replicates']:,} bootstrap replicates", D)
expect("design: bootstrap seed", f"bootstrap seed {family['bootstrap_seed']}", D)
expect("design: later family", "one family of 36", D)


def family_row(row):
    return (
        f"{row['id']} & {row['domain']} & {esc(row['model'])} & {esc(row['reference'])} & "
        f"{row['horizon']} \\\\"
    )


for row in family["comparisons"]:
    expect(f"design: family row {row['id']}", family_row(row), D)
synthetic = load(S2 / "synthetic_comparisons.json")
assert synthetic["comparison_count"] == 6 and len(synthetic["comparisons"]) == 6
assert all(
    row["horizon"] == 30 and row["domain"] == "synthetic" for row in synthetic["comparisons"]
)
assert synthetic["q"] == 0.05 and synthetic["bootstrap_replicates"] == 20000
for row in synthetic["comparisons"]:
    expect(f"design: synthetic row {row['id']}", family_row(row), D)
expect("design: synthetic family", "six tests at horizon 30, S01 to S06", D)

grid = load(S2 / "grid_manifest.json")
assert grid["n_cells"] == 18 and len(grid["cells"]) == 18 and grid["replicates_per_cell"] == 30
assert grid["n_series"] == 540 and len(grid["series"]) == 540 and grid["observations"] == 270
assert (
    grid["origins"] == [180, 210, 240]
    and grid["horizons"] == [7, 30]
    and grid["seed"] == seeds["synthetic"]
)
assert sorted({c["zero_probability"] for c in grid["cells"]}) == [0.2, 0.8, 0.95]
assert sorted({c["positive_mean"] for c in grid["cells"]}) == [1, 5, 25]
assert sorted({c["persistence"] for c in grid["cells"]}) == [0.0, 0.8]
assert (
    len({(c["zero_probability"], c["positive_mean"], c["persistence"]) for c in grid["cells"]})
    == 18
)
assert (
    len(grid["streams"]) == 30
    and len(
        {s["occurrence_seed"] for s in grid["streams"]} | {s["size_seed"] for s in grid["streams"]}
    )
    == 60
)
assert grid["common_random_numbers"].startswith(
    "same occurrence and size uniforms across cells within replicate"
)
expect(
    "design: grid levels",
    "$z \\in \\{0.2, 0.8, 0.95\\}$, $\\mu_{+} \\in \\{1, 5, 25\\}$ and $\\rho \\in \\{0, 0.8\\}$",
    D,
)
expect(
    "design: grid size",
    f"{grid['n_cells']} cells, each with {grid['replicates_per_cell']} independent replicates of "
    f"{grid['observations']} observations",
    D,
)
expect(
    "design: grid origins",
    f"origins at indices {grid['origins'][0]}, {grid['origins'][1]} and {grid['origins'][2]}",
    D,
)
expect("design: grid series", f"so {grid['n_series']} series in all", D)
expect("design: synthetic seed", f"synthetic root seed {grid['seed']}", D)
holdout = load(S2 / "holdout_comparisons.json")
assert holdout["comparison_count"] == 18
assert "Freeze at 2026-09-28 18:00 UTC" in protocol
assert "2026-10-15 18:00 UTC for the seven-day block and 2026-11-07 18:00 UTC" in protocol
assert "by 2026-10-20 23:59 UTC" in protocol
expect("design: holdout freeze", "2026-09-28 18:00 UTC", D)
expect("design: holdout family", "18 tests H01 to H18", D)
expect("design: settlements", "2026-10-15 and 2026-11-07", D)
expect("design: npm clock", "2026-10-20 23:59 UTC", D + P)
expect("design: pyPI clause", "inactivity is not the source failure", D)
assert "Inactivity is not the source failure the rule names" in protocol
for revision, dated in [
    ("1d95242", "2025-10-02"),
    ("43046b8", "2026-09-02"),
    ("29ec376", "2026-06-05"),
]:
    assert dated in next(line for line in cards.splitlines() if f"`{revision}`" in line)
expect("design: targets window", "2026-06-03 to 2026-08-31", D + P)

# --- the achieved npm panel --------------------------------------------
status = load(S2 / "npm_panel_status.json")
assert (
    status["status"] == "verified_achieved_panel"
    and status["deadline_met"]
    and not status["target_values_opened"]
)
assert status["protocol_rule"] == "PROTOCOL.md, dated addition of 2026-10-12, item 2"
assert status["readiness_deadline"] == "2026-10-20T23:59:00+00:00"
assert status["panel_written_at"].startswith("2026-10-15T01:57") and status[
    "panel_verified_at"
].startswith("2026-10-15T02:00")
expect("panel: frozen", "frozen on 2026-10-15 01:57 UTC and verified at 02:00 UTC", P)
expect("panel: as-of", "as of 2026-10-15", P)
inv = status["inventory"]
assert (
    inv["source"] == "https://replicate.npmjs.com/registry/_all_docs" and inv["page_limit"] == 1000
)
assert inv["first_page_acquired_at"].startswith("2026-10-14T00:23") and inv[
    "last_page_acquired_at"
].startswith("2026-10-14T02:04")
expect(
    "panel: inventory",
    f"{inv['pages']:,} pages of at most {inv['page_limit']:,} names between 2026-10-14 00:23 and "
    f"02:04 UTC: {inv['names']:,} package names",
    P,
)
walk = status["candidate_walk"]
assert walk["stop_reason"] == "pool_full" and walk["excluded_reasons"] == {
    "http_404": walk["excluded"]
}
assert walk["visited"] == walk["eligible"] + walk["ineligible"] + walk["excluded"]
assert status["candidate_pool_size"] == walk["eligible"] == 10000
expect("panel: walk", f"visited the first {walk['visited']:,} names", P)
expect("panel: eligible", f"{walk['eligible']:,} were eligible", P)
expect("panel: ineligible", f"{walk['ineligible']:,} were ineligible", P)
expect(
    "panel: excluded", f"{walk['excluded']} were excluded because the registry answered HTTP 404", P
)
frame = status["frame"]
estimate = inv["names"] * walk["eligible"] / walk["visited"]
assert abs(frame["eligible_frame_size_estimate"] - estimate) < 1e-6
assert frame["eligible_frame_size_bounds"] == [
    walk["eligible"],
    inv["names"] - walk["ineligible"] - walk["excluded"],
]
assert abs(frame["candidate_inclusion_probability_estimate"] - walk["eligible"] / estimate) < 1e-12
assert (
    abs(
        frame["candidate_inclusion_probability_bounds"][0]
        - walk["eligible"] / frame["eligible_frame_size_bounds"][1]
    )
    < 1e-12
)
assert frame["candidate_inclusion_probability_bounds"][1] == 1.0
expect(
    "panel: frame estimate",
    f"about {round(estimate):,} packages, with exact bounds of "
    f"{frame['eligible_frame_size_bounds'][0]:,} and {frame['eligible_frame_size_bounds'][1]:,}",
    P,
)
expect(
    "panel: inclusion probability",
    f"about {frame['candidate_inclusion_probability_estimate']:.4f}, with bounds "
    f"{frame['candidate_inclusion_probability_bounds'][0]:.4f} and 1",
    P,
)
ctx = status["context"]
assert (
    ctx["keys"] == 10000
    and ctx["complete_candidates"] == 9998
    and ctx["exclusions"] == {"http_404": 2}
)
assert ctx["window"] == ["2025-09-01", "2026-06-02"] and ctx["strata_window_start"] == "2026-03-05"
by_status = ctx["http_attempts_by_status"]
assert (
    sum(by_status.values()) == ctx["http_attempts"]
    and by_status["200"] == ctx["complete_candidates"]
)
expect("panel: context window", "2025-09-01 to 2026-06-02", P)
expect(
    "panel: complete",
    f"{ctx['complete_candidates']:,} answered completely and {ctx['exclusions']['http_404']} "
    "were excluded",
    P,
)
for key in ctx["excluded_keys"]:
    expect(f"panel: excluded key {key}", f"\\texttt{{{esc(key)}}}", P)
expect(
    "panel: statuses",
    f"Of the {ctx['http_attempts']:,} attempts to that host, {by_status['200']:,} returned the "
    f"range, {by_status['404']} returned 404, {by_status['429']:,} returned 429, "
    f"{by_status['504']} returned 504 and {by_status['ReadTimeout']} timed out",
    P,
)
expect("panel: stratum window", "2026-03-05 to 2026-06-02", P)
strata2 = status["achieved_strata"]
assert strata2 == load(NPM / "selection.json")["report"]["strata"]
label = {
    "dense": ("dense", "$[0, 0.5)$"),
    "sparse": ("sparse", "$[0.5, 0.9)$"),
    "very_sparse": ("very sparse", "$[0.9, 1]$"),
}
for key, (name, bounds) in label.items():
    s = strata2[key]
    assert (
        s["achieved"] == min(100, s["complete_candidates"]) and s["unfilled"] == 100 - s["achieved"]
    )
    expect(
        f"panel: stratum row {key}",
        f"{name} & {bounds} & {s['complete_candidates']:,} & {s['achieved']} & "
        f"{s['unfilled']} \\\\",
        P,
    )
expect(
    "panel: candidates by stratum",
    f"{strata2['dense']['complete_candidates']:,} in the dense stratum",
    P,
)
expect(
    "panel: sparse candidates",
    f"{strata2['sparse']['complete_candidates']:,} in the\nsparse stratum",
    P,
)
expect(
    "panel: very sparse",
    f"{strata2['very_sparse']['complete_candidates']} in the very sparse stratum",
    P,
)
expect("panel: unfilled", f"{strata2['very_sparse']['unfilled']} very-sparse slots unfilled", P)
expect(
    "panel: only nine",
    f"Only {strata2['very_sparse']['complete_candidates']} of "
    f"{sum(s['complete_candidates'] for s in strata2.values()):,} complete candidates",
    P,
)
assert sum(s["complete_candidates"] for s in strata2.values()) == ctx["complete_candidates"]
assert status["series"] == sum(s["achieved"] for s in strata2.values()) == 209
expect(
    "panel: series",
    f"{status['series']} series: {strata2['dense']['achieved']} dense, "
    f"{strata2['sparse']['achieved']} sparse and {strata2['very_sparse']['achieved']} very sparse",
    P,
)
expect("placeholder: 209", "of 209", R)
npm_manifest = load(NPM / "manifest.json")
series = npm_manifest["series"]
assert len(series) == status["series"]
counts = {k: sum(s["stratum"] == k for s in series) for k in strata2}
assert counts == {k: strata2[k]["achieved"] for k in strata2}
zf = {k: [s["zero_fraction"] for s in series if s["stratum"] == k] for k in strata2}
assert (
    max(zf["dense"]) < 0.5
    and 0.5 <= min(zf["sparse"])
    and max(zf["sparse"]) < 0.9
    and min(zf["very_sparse"]) >= 0.9
)
reserve = load(NPM / "selection.json")["reserve_order"]
assert len(reserve) == ctx["complete_candidates"]
for key in strata2:
    ordered = [r for r in reserve if r["stratum"] == key]
    hashes = [r["selection_hash"] for r in ordered]
    assert hashes == sorted(hashes) and len(ordered) == strata2[key]["complete_candidates"]
    taken = [s["series_id"] for s in series if s["stratum"] == key]
    assert [r["series_id"] for r in ordered[: len(taken)]] == taken
created = sorted(s["created_at"][:10] for s in series)
assert created[-1] < cal["context_start"]
expect("panel: creation range", f"created\nbetween {created[0]} and {created[-1]}", P)
scoped = sum(s["series_id"].startswith("@") for s in series)
expect("panel: scoped", f"{scoped} of them are scoped names", P)
big = next(s for s in series if s["series_id"] == "aggregate-error")
assert big["stratum"] == "dense" and big["zero_fraction"] == 0.0
assert "aggregate-error, last-28-day context mean 7,637,136" in protocol
expect("panel: dominant series", "\\texttt{aggregate-error}", P)
expect("panel: dominant mean", "7,637,136 downloads a\nday", P)
review2 = text(ROOT / "docs" / "research" / "2026-10-15-study2-run-path-review.md")
assert "the next largest mean before the first cutoff is about 13,000" in review2
expect("panel: next largest", "about 13,000", P)
acq = status["acquisition"]
assert sum(acq["http_attempts_by_host"].values()) == acq["http_attempts"]
hosts = acq["http_attempts_by_host"]
assert (
    hosts["registry.npmjs.org"] == walk["visited"]
    and hosts["api.npmjs.org"] == ctx["http_attempts"]
    and hosts["replicate.npmjs.com"] == inv["pages"]
)
expect(
    "panel: attempts",
    f"{acq['http_attempts']:,} HTTP attempts: {hosts['registry.npmjs.org']:,} to\nthe registry "
    f"host, {hosts['api.npmjs.org']:,} to the download-counts host and "
    f"{hosts['replicate.npmjs.com']:,} to the replication host",
    P,
)
secs = acq["invocation_seconds"]
assert int(secs // 3600) == 12 and int(secs % 3600 // 60) == 38
expect(
    "panel: invocations",
    f"over {acq['invocations']}\ninvocations totalling {int(secs):,} seconds "
    "(12 hours and 38 minutes)",
    P,
)
assert acq["first_attempt_at"].startswith("2026-10-14T00:23") and acq["last_attempt_at"].startswith(
    "2026-10-15T01:57"
)
expect("panel: span", "from 2026-10-14 00:23 UTC to 2026-10-15 01:57\nUTC", P)
assert (
    "at least 1 s between attempts" in acq["request_spacing"]
    and "at least 3 s from 2026-10-14T22:51:36Z" in acq["request_spacing"]
)
assert "about 20 requests a minute" in acq["request_spacing"]
expect("panel: spacing", "at least three seconds from 2026-10-14 22:51 UTC", P)
expect("panel: rate", "about 20 requests a minute", P)
interruptions = " ".join(acq["interruptions"])
assert (
    "From 2026-10-14T08:44Z" in interruptions
    and "until at least 10:25Z" in interruptions
    and "again at 21:37Z" in interruptions
)
assert "Three 429 answers in a row for one key stop an invocation" in interruptions
expect(
    "panel: outage",
    "From 2026-10-14 08:44 UTC the download API timed out or answered 504 until at least "
    "10:25 UTC and answered\nagain at 21:37 UTC",
    P,
)
expect("panel: 429 count", f"returned 429 to {by_status['429']:,}\nattempts", P)
approval = status["approval"]
assert approval["http_attempt_ceiling"] == 36000 and approval["invocation_seconds_ceiling"] == 46800
assert approval["words"] == "the pull of 36,000 requests and 13 hours"
assert (
    acq["http_attempts"] <= approval["http_attempt_ceiling"]
    and secs <= approval["invocation_seconds_ceiling"]
)
expect("panel: approval", "36,000 requests and 13 hours", P)
redistribution = text(ROOT / "docs" / "research" / "2026-10-15-npm-redistribution-review.md")
for needle in [
    "30,198 attempts in about 26 hours",
    "five million requests to npm Services in a single month",
    "2,708 times",
    "2022-03-10",
    "npm is a registered trademark of npm, Inc.",
]:
    assert needle in redistribution, needle
expect("panel: 26 hours", "about 26 hours", P)
expect("panel: five million", "five million requests a month", P)
expect(
    "panel: rate limit honoured",
    f"reached npm's rate limit {by_status['429']:,} times and honoured it",
    P,
)
expect("panel: terms date", "Open-Source Terms of 2022-03-10", P)
expect("panel: trademark", "npm is a registered trademark of npm, Inc.", P)

# --- the results placeholder --------------------------------------------
tbd = "\\tbd & [\\tbd, \\tbd] & \\tbd & \\tbd & \\tbd & \\tbd \\\\"
for row in family["comparisons"] + synthetic["comparisons"]:
    expect(
        f"placeholder row {row['id']}",
        f"{row['id']} & {esc(row['model'])} & {esc(row['reference'])} & {row['horizon']} & {tbd}",
        R,
    )
checks += 1
# The only decimal in the placeholder is the BH level q = 0.05; no result figure appears.
decimals = [d for d in re.findall(r"\b\d+\.\d+\b", TEXT[PLACEHOLDER]) if d != "0.05"]
if decimals:
    failures.append(f"placeholder holds decimal figures: {decimals}")
assert len(pkg_spec["variants"]) == 16
expect("placeholder: forecasts per origin", f"{len(pkg_spec['variants'])} forecasts per origin", R)
expect("placeholder: replicates", f"of {grid['replicates_per_cell']}", R)
expect("placeholder: synthetic series", f"over {grid['n_series']} series", R)
expect("placeholder: 18 tests", f"over the {family['comparison_count']} tests", R)
expect("placeholder: 6 tests", f"over the {synthetic['comparison_count']} tests", R)

# --- report -----------------------------------------------------------
for line in failures:
    print("FAIL", line)
for line in skipped:
    print("SKIP", line)
print(f"{checks} checks, {len(failures)} failures, {len(skipped)} skipped")
sys.exit(1 if failures else 0)

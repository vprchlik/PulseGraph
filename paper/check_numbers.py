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

import numpy as np
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


INPUT = re.compile(r"^\\input\{([^}]+)\}$", re.M)


def expand(path):
    """The file's text with every \\input{...} line replaced by that file's text, recursively."""
    raw = path.read_text(encoding="utf-8")
    return INPUT.sub(lambda m: expand(PAPER / (m.group(1) + ".tex")).rstrip("\n"), raw)


def text(path):
    return re.sub(r"\s+", " ", expand(path))


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
QUESTION, DESIGN, PANEL, RESULTS = (
    "study2-question.tex",
    "study2-design.tex",
    "study2-panel.tex",
    "study2-results.tex",
)
DETAIL, PANEL_DETAIL, APPENDIX = (
    "study2-design-detail.tex",
    "study2-panel-detail.tex",
    "study2-appendix.tex",
)
SECTION_FILES = (QUESTION, DESIGN, PANEL, RESULTS, DETAIL, PANEL_DETAIL, APPENDIX)
for name in SECTION_FILES:
    TEXT[name] = text(SECTIONS / name)
# Since 2026-10-16 the design and panel sections are each split into a body file and a detail file
# (the paper's appendix); the needles asserted in D and P below appear in one of the two.
TEXT[DESIGN] = TEXT[DESIGN] + " " + TEXT[DETAIL]
TEXT[PANEL] = TEXT[PANEL] + " " + TEXT[PANEL_DETAIL]
Q, D, P, R = (QUESTION,), (DESIGN,), (PANEL,), (RESULTS,)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def esc(name):
    return name.replace("_", "\\_")


# The public boundary: no operating-layer vocabulary in a committed section.
for name in SECTION_FILES:
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
for name in SECTION_FILES:
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
expect("results: 209", "(of 209)", R)
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

# --- the results file, which replaced the placeholder on 2026-10-16 ---------------------------
checks += 1
if (SECTIONS / "study2-results-placeholder.tex").exists():
    failures.append("study2-results-placeholder.tex still exists beside study2-results.tex")
checks += 1
if re.search(r"\btbd\b", TEXT[RESULTS]):
    failures.append("study2-results.tex: a 'tbd' remains")
assert len(pkg_spec["variants"]) == 16
expect("results: variants", f"2 horizons, {len(pkg_spec['variants'])} variants)", R)
expect("results: replicates", f"blocks (of {grid['replicates_per_cell']})", R)
expect("results: synthetic series", f"({grid['n_series']} series, 3 origins", R)
expect("results: 18 tests", f"over the {family['comparison_count']} tests", R)
expect("results: 6 tests", f"over the {synthetic['comparison_count']} tests", R)

# --- the paper: paper.tex, the Study 2 results and the paper's summary (added 2026-10-16) --------
# paper.tex is read with its \input files expanded, like main.tex. The Study 2 results trace to the
# inference, secondary, integrity, run and post-hoc files of the two run directories under reports/.
NPM_RUN = ROOT / "reports" / "study2-npm" / "run-2026-10-15"
SYN_RUN = ROOT / "reports" / "study2-synthetic-2026-10-15"
PAPER_TEX = PAPER / "paper.tex"
PAPER_SUMMARY = PAPER / "PAPER-SUMMARY.md"
TEXT["paper.tex"] = text(PAPER_TEX)
TEXT["PAPER-SUMMARY.md"] = text(PAPER_SUMMARY)
PT, RS, AP, PS = ("paper.tex",), (RESULTS,), (APPENDIX,), ("PAPER-SUMMARY.md",)
ROUND_TRIP = {"float_precision": "round_trip"}


def g(x, d=4):
    """Four significant figures; thousands separators from 1,000 up, as the results documents."""
    if pd.isna(x):
        return ""
    if abs(x) >= 10000:
        return f"{x:,.0f}"
    s = f"{x:.{d}g}"
    if "e" in s:
        return s
    v = float(s)
    return f"{v:,.0f}" if abs(v) >= 1000 else s


def pval(x):
    """Three significant figures; small values as the TeX power of ten."""
    s = f"{x:.3g}"
    if "e" in s:
        m, e = s.split("e")
        return f"${m} \\times 10^{{{int(e)}}}$"
    return s


def family_line(r):
    return (
        f"{r.id} & {esc(r.model)} & {esc(r.reference)} & {r.horizon} & {g(r.mean_diff)} & "
        f"[{g(r.mean_diff_ci_low)}, {g(r.mean_diff_ci_high)}] & {g(r.median_diff)} & "
        f"{int(r.wins)} / {int(r.ties)} / {int(r.losses)} & {pval(r.wilcoxon_p_bh)} \\\\"
    )


# The public boundary, for the new files and the expanded paper.
for name in (RESULTS, APPENDIX, DETAIL, PANEL_DETAIL, "paper.tex", "PAPER-SUMMARY.md"):
    checks += 1
    hits = [
        w
        for w in ("Claude", "Opus", "Fable", "Anthropic", "OpenAI", "session", "chat")
        if re.search(rf"\b{w}\b", TEXT[name])
    ]
    if hits:
        failures.append(f"{name}: operating-layer vocabulary {hits}")

# The report's text is reused unchanged: every shared file is in both main.tex and paper.tex.
for shared in sorted((PAPER / "shared").glob("*.tex")):
    expect(f"shared {shared.name} in both documents", text(shared), ("main.tex", "paper.tex"))
for name in (QUESTION, DESIGN, PANEL, RESULTS, APPENDIX, DETAIL, PANEL_DETAIL):
    expect(f"section {name} in paper.tex", text(SECTIONS / name), PT)
checks += 1
if re.search(r"\btbd\b", TEXT["paper.tex"]):
    failures.append("paper.tex: a 'tbd' remains")

# --- the two families ----------------------------------------------------
npm_inf = pd.read_csv(NPM_RUN / "inference" / "inference.csv", **ROUND_TRIP)
syn_inf = pd.read_csv(SYN_RUN / "inference" / "inference.csv", **ROUND_TRIP)
assert len(npm_inf) == 18 and npm_inf.declared_count.eq(18).all()
assert len(syn_inf) == 6 and syn_inf.declared_count.eq(6).all()
assert npm_inf.n_entities.eq(209).all() and syn_inf.n_entities.eq(30).all()
assert npm_inf.n_bootstrap.eq(20000).all() and npm_inf.bootstrap_root.eq(20260917).all()
assert syn_inf.n_bootstrap.eq(20000).all() and syn_inf.bootstrap_root.eq(20260917).all()
assert list(npm_inf.id) == [r["id"] for r in family["comparisons"]]
assert list(syn_inf.id) == [r["id"] for r in synthetic["comparisons"]]
for r in npm_inf.itertuples():
    expect(f"npm family row {r.id}", family_line(r), RS)
for r in syn_inf.itertuples():
    expect(f"synthetic family row {r.id}", family_line(r), RS)
hc = npm_inf[npm_inf.reference.str.endswith("_completed")]
hk = npm_inf[npm_inf.reference == "hurdle_count_28"]
rl = npm_inf[npm_inf.reference == "local_mean_28"]
sc = syn_inf[syn_inf.reference.str.endswith("_completed")]
sk = syn_inf[syn_inf.reference == "hurdle_count_28"]
# Counts of rejections and their sides.
assert int(npm_inf.reject_bh_005.sum()) == 12 and int(syn_inf.reject_bh_005.sum()) == 5
assert int((npm_inf.reject_bh_005 & (npm_inf.mean_diff < 0)).sum()) == 10
assert (syn_inf.mean_diff > 0).all() and (syn_inf[syn_inf.reject_bh_005].mean_diff > 0).all()
expect(
    "twelve of eighteen",
    "Twelve of the eighteen external tests and five of the six synthetic tests",
    RS,
)
expect("ten and two", "ten reject for the model variant and two against it", RS)
expect("paper: two of six", "two of six reject against it", PT + PS)
expect("paper: five of six", "five of six tests reject, all against the substitution", PT + PS)
# Hurdle against its completed control.
assert (hc.mean_diff > 0).all() and (hc.mean_diff_ci_low > 0).all()
assert hc.median_diff.abs().max() < 0.014
assert int((hc.median_diff < 0).sum()) == 3 and int((hc.median_diff > 0).sum()) == 3
assert (
    hc[hc.reject_bh_005].id.tolist() == ["E10", "E16"]
    and (hc[hc.reject_bh_005].median_diff > 0).all()
)
expect(
    "hurdle means",
    f"from {g(hc.mean_diff.min())} to {g(hc.mean_diff.max())}, with every interval above zero",
    RS,
)
expect("hurdle medians", "the medians lie within 0.014 of zero, three below it and three above", RS)
expect(
    "hurdle wins",
    f"the hurdle scores lower on {hc.wins.min()} to {hc.wins.max()} of the 209 series",
    RS,
)
e10, e16 = hc[hc.id == "E10"].iloc[0], hc[hc.id == "E16"].iloc[0]
expect(
    "E10 and E16",
    f"(E10, with the hurdle higher on {int(e10.losses)} of 209 series and adjusted $p$ "
    f"{pval(e10.wilcoxon_p_bh)}; E16, higher on {int(e16.losses)}, adjusted "
    f"$p$ {pval(e16.wilcoxon_p_bh)})",
    RS,
)
nonreject = hc[~hc.reject_bh_005].wilcoxon_p_bh
expect(
    "hurdle non-rejects",
    f"adjusted $p$ from {pval(nonreject.min())} to {pval(nonreject.max())}",
    RS,
)
assert (sc.mean_diff_ci_low > 0).all() and sc.reject_bh_005.all()
expect(
    "synthetic hurdle means",
    f"from {g(sc.mean_diff.min())} to {g(sc.mean_diff.max())}, with every interval above zero",
    RS,
)
expect(
    "synthetic hurdle medians",
    f"medians of {g(sc.median_diff.min())} to {g(sc.median_diff.max())}",
    RS,
)
assert sorted(sc.wins.unique()) == [5, 6]
expect("synthetic hurdle wins", "lower on 5 or 6 of the 30 replicate blocks", RS)
expect(
    "synthetic hurdle p",
    f"adjusted $p$ from {pval(sc.wilcoxon_p_bh.min())} to {pval(sc.wilcoxon_p_bh.max())}",
    RS,
)
# Hurdle against the count hurdle.
assert hk.reject_bh_005.all() and (hk.mean_diff_ci_high < 0).all() and (hk.median_diff < 0).all()
expect(
    "count hurdle p",
    f"adjusted $p$ from {pval(hk.wilcoxon_p_bh.max())} to {pval(hk.wilcoxon_p_bh.min())}",
    RS,
)
expect(
    "count hurdle means",
    f"from {g(hk.mean_diff.max())} to {g(hk.mean_diff.min())}, with every interval below zero",
    RS,
)
expect("count hurdle medians", f"from {g(hk.median_diff.max())} to {g(hk.median_diff.min())}", RS)
expect("count hurdle wins", f"lower on {hk.wins.min()} to {hk.wins.max()} of the 209 series", RS)
s02, s04, s06 = (sk[sk.id == i].iloc[0] for i in ("S02", "S04", "S06"))
assert s02.reject_bh_005 and s06.reject_bh_005 and not s04.reject_bh_005
assert (
    s02.mean_diff_ci_low > 0
    and s06.mean_diff_ci_low > 0
    and s04.mean_diff_ci_low < 0 < s04.mean_diff_ci_high
)
expect(
    "S02 S06",
    f"by {g(s02.mean_diff)} and {g(s06.mean_diff)} with intervals above zero (adjusted $p$ "
    f"{pval(s02.wilcoxon_p_bh)} and {pval(s06.wilcoxon_p_bh)}, lower on {int(s02.wins)} of "
    "30 blocks each)",
    RS,
)
assert s02.wins == s06.wins
expect(
    "S04",
    f"differs by {g(s04.mean_diff)} with an interval that includes zero "
    f"(adjusted $p$ {pval(s04.wilcoxon_p_bh)}, "
    f"lower on {int(s04.wins)} of 30)",
    RS,
)
# Raw deciles against the local mean.
assert rl[rl.reject_bh_005].id.tolist() == ["E06", "E09", "E12", "E18"]
assert (rl.mean_diff_ci_high < 0).all()
e03, e15 = rl[rl.id == "E03"].iloc[0], rl[rl.id == "E15"].iloc[0]
expect(
    "raw non-rejects", f"adjusted $p$ {pval(e03.wilcoxon_p_bh)} and {pval(e15.wilcoxon_p_bh)}", RS
)
expect(
    "raw means",
    f"from {g(rl.mean_diff.max())} to {g(rl.mean_diff.min())}, with every interval below zero",
    RS,
)
expect("raw wins", f"lower on {rl.wins.min()} to {rl.wins.max()} of the 209 series", RS)
assert (
    e03.median_diff > 0
    and e15.median_diff > 0
    and (rl[~rl.id.isin(["E03", "E15"])].median_diff < 0).all()
)
expect("raw medians positive", f"({g(e03.median_diff)} and {g(e15.median_diff)})", RS)
neg = rl[~rl.id.isin(["E03", "E15"])].median_diff
expect("raw medians negative", f"({g(neg.max())} to {g(neg.min())})", RS)

# --- the one series behind every npm mean (leave-one-out and top-five share, paired file) ---
paired_npm = pd.read_csv(NPM_RUN / "inference" / "paired_entities.csv", **ROUND_TRIP)
assert paired_npm.groupby("id").size().eq(209).all()
loo_without = {}
top5 = {}
for cid, grp in paired_npm.groupby("id"):
    d = grp.difference.to_numpy()
    names = grp.entity.to_numpy()
    loo = (d.sum() - d) / (len(d) - 1)
    k = int(abs(loo - d.mean()).argmax())
    assert names[k] == "aggregate-error" and (d[k] > 0) == (d.mean() > 0), cid
    loo_without[cid] = loo[k]
    gains = -d[d < 0]
    top5[cid] = float(np.sort(gains)[-5:].sum() / gains.sum())
    assert abs(d.mean() - npm_inf[npm_inf.id == cid].mean_diff.iloc[0]) < 1e-9
loo_hc = [loo_without[c] for c in hc.id]
expect(
    "without the dominant series",
    f"fall from {g(hc.mean_diff.min())} to {g(hc.mean_diff.max())} to {g(min(loo_hc))} to "
    f"{g(max(loo_hc))}",
    RS,
)
share = [top5[c] for c in list(hk.id) + list(rl.id)]
expect("top-five share", f"hold {min(share):.3f} to {max(share):.3f} of all positive gain", RS)
expect(
    "paper: top-five share", f"{min(share):.3f} to {max(share):.3f} of it by five series on npm", PT
)
expect("dominant mean", "7,637,136 downloads a day", RS)
expect("paper: 7.6 million", "7.6 million downloads a day", PT + PS)

# --- the accounting parts (Table tab:s2parts) ---------------------------------
npm_acc = pd.read_csv(NPM_RUN / "inference" / "secondary_accounting.csv", **ROUND_TRIP).set_index(
    ["horizon", "model"]
)
syn_acc = pd.read_csv(SYN_RUN / "inference" / "secondary_accounting.csv", **ROUND_TRIP).set_index(
    ["horizon", "model"]
)
for study, acc, horizons in (("npm", npm_acc, (7, 30)), ("synthetic", syn_acc, (30,))):
    for h in horizons:
        for m in MODELS:
            a, b = acc.loc[(h, f"{m}_hurdle")], acc.loc[(h, f"{m}_completed")]
            parts = [
                a.qscore9 - b.qscore9,
                a.zero - b.zero,
                a.positive_over - b.positive_over,
                a.positive_under - b.positive_under,
            ]
            assert (
                abs(parts[0] - sum(parts[1:])) < 1e-6
                and parts[0] > 0 > parts[1]
                and parts[2] < 0 < parts[3]
            )
            assert parts[3] > -parts[1] - parts[2]
            assert abs(a.parts_sum - a.qscore9) < 1e-6 and a.max_abs_window_residual < 1e-8
            expect(
                f"parts row {study} {m} {h}",
                f"{study} & {LABEL[m]} & {h} & " + " & ".join(g(v) for v in parts) + " \\\\",
                RS,
            )
syn_h = [syn_acc.loc[(30, f"{m}_hurdle")] for m in MODELS]
syn_c = [syn_acc.loc[(30, f"{m}_completed")] for m in MODELS]
expect(
    "synthetic zero parts",
    f"{g(min(r.zero for r in syn_h))} to {g(max(r.zero for r in syn_h))} "
    f"against {g(min(r.zero for r in syn_c))} "
    f"to {g(max(r.zero for r in syn_c))} for their controls",
    RS,
)
expect(
    "synthetic under parts",
    f"{g(min(r.positive_under for r in syn_h))} to {g(max(r.positive_under for r in syn_h))} "
    f"against {g(min(r.positive_under for r in syn_c))} "
    f"to {g(max(r.positive_under for r in syn_c))}",
    RS,
)

# --- the secondary contrasts: the scaled score and the Brier score ------------
npm_con = pd.read_csv(NPM_RUN / "inference" / "secondary_contrasts.csv", **ROUND_TRIP)
syn_con = pd.read_csv(SYN_RUN / "inference" / "secondary_contrasts.csv", **ROUND_TRIP)


def scaled_line(r):
    return (
        f"{r.id} & {esc(r.model)} & {esc(r.reference)} & {r.horizon} & {g(r.mean_diff)} & "
        f"[{g(r.mean_diff_ci_low)}, {g(r.mean_diff_ci_high)}] & {g(r.median_diff)} & "
        f"{int(r.wins)} / {int(r.ties)} / {int(r.losses)} \\\\"
    )


npm_sc = npm_con[npm_con.metric == "context_scaled_qscore9"]
syn_sc = syn_con[syn_con.metric == "context_scaled_qscore9"]
assert len(npm_sc) == 18 and len(syn_sc) == 12
for r in npm_sc.itertuples():
    expect(f"scaled row {r.id}", scaled_line(r), AP)
for r in syn_sc.itertuples():
    expect(f"scaled row {r.id}", scaled_line(r), AP)
sc_by = npm_sc.set_index("id")
for cid in ("E01", "E07", "E13"):
    assert sc_by.loc[cid].mean_diff_ci_high < 0
for cid in ("E04", "E10", "E16"):
    assert sc_by.loc[cid].mean_diff_ci_low < 0 < sc_by.loc[cid].mean_diff_ci_high
expect(
    "scaled h7",
    f"{g(sc_by.loc['E01'].mean_diff)} for Chronos-2, {g(sc_by.loc['E07'].mean_diff)} for TimesFM "
    f"3 and {g(sc_by.loc['E13'].mean_diff)} for TimesFM 2.5",
    AP,
)
expect(
    "scaled h30",
    f"({g(sc_by.loc['E04'].mean_diff)}, {g(sc_by.loc['E10'].mean_diff)} "
    f"and {g(sc_by.loc['E16'].mean_diff)})",
    AP,
)
sc_hk = sc_by.loc[list(hk.id)]
assert (sc_hk.mean_diff_ci_high < 0).all()
expect(
    "scaled vs count hurdle", f"{g(sc_hk.mean_diff.max())} to {g(sc_hk.mean_diff.min())}", RS + AP
)
for cid in ("E06", "E09", "E12", "E18"):
    assert sc_by.loc[cid].mean_diff_ci_high < 0
for cid in ("E03", "E15"):
    assert sc_by.loc[cid].mean_diff_ci_low < 0 < sc_by.loc[cid].mean_diff_ci_high
syn_sc30 = syn_sc[syn_sc.horizon == 30]
assert ((syn_sc30.mean_diff_ci_low < 0) & (syn_sc30.mean_diff_ci_high > 0)).all()
expect("synthetic scaled", "on the grid every scaled interval includes zero", RS)
brier_hk = npm_con[
    (npm_con.metric == "occurrence_brier") & (npm_con.reference == "hurdle_count_28")
]
assert len(brier_hk) == 6 and (brier_hk.mean_diff == 0).all() and (brier_hk.ties == 209).all()
expect(
    "brier zero",
    "The occurrence Brier difference is exactly zero for every series in these six rows",
    RS,
)
brier_hc = npm_con[
    (npm_con.metric == "occurrence_brier") & npm_con.reference.str.endswith("_completed")
].set_index("id")
assert all(brier_hc.loc[c].mean_diff_ci_high < 0 for c in ("E01", "E04", "E13"))
assert all(
    brier_hc.loc[c].mean_diff_ci_low < 0 < brier_hc.loc[c].mean_diff_ci_high
    for c in ("E07", "E10", "E16")
)
expect(
    "brier vs completed",
    "with an interval below zero in E01, E04 and E13 and includes zero in E07, E10 and E16",
    AP,
)
# CRPS availability.
npm_scores = pd.read_csv(NPM_RUN / "inference" / "secondary_scores.csv", **ROUND_TRIP)
assert int(npm_scores.crps_unavailable_bound_not_certified.sum()) == 66
assert (
    int(npm_scores.crps_certified.sum()) == 13728
    and int(npm_scores.crps_with_count_distribution.sum()) == 13794
)
assert int(npm_scores.crps_unavailable_no_count_distribution.sum()) == 6270
assert 66 == 11 * 3 * 2 and 13728 + 66 == 13794 and 13794 + 6270 == 20064
expect(
    "crps unavailable",
    "for 66 npm forecasts, all of them on \\texttt{aggregate-error} (11 variants with a count "
    "law, 3 origins, 2 horizons); the other 13,728 forecasts with a count law are certified, "
    "and the 6,270 without one",
    RS,
)
syn_scores = pd.read_csv(SYN_RUN / "inference" / "secondary_scores.csv", **ROUND_TRIP)
assert int(syn_scores.crps_unavailable_bound_not_certified.sum()) == 0
assert int(syn_scores.crps_certified.sum()) == int(syn_scores.crps_with_count_distribution.sum())

# --- model scores (Tables tab:s2scores and tab:s2synscores) ------------------
VARIANTS = (
    "chronos2_raw chronos2_completed chronos2_hurdle timesfm3_raw timesfm3_completed "
    "timesfm3_hurdle "
    "timesfm2p5_raw timesfm2p5_completed timesfm2p5_hurdle local_mean_28 "
    "autoets_weekly nb_local_level_28 "
    "poisson_28 hurdle_count_28 hurdle_empirical_28 dynamic_count"
).split()
assert len(VARIANTS) == len(pkg_spec["variants"]) == 16
n7, n30 = (npm_scores[npm_scores.horizon == h].set_index("model") for h in (7, 30))
for m in VARIANTS:
    expect(
        f"npm score row {m}",
        f"{esc(m)} & {g(n7.loc[m].qscore9)} & {g(n30.loc[m].qscore9)} "
        f"& {g(n30.loc[m].context_scaled_qscore9)} "
        f"& {g(n30.loc[m].occurrence_brier)} & {g(n30.loc[m].discrete_crps)} \\\\",
        AP,
    )
s7, s30 = (syn_scores[syn_scores.horizon == h].set_index("model") for h in (7, 30))
for m in VARIANTS + ["oracle"]:
    expect(
        f"synthetic score row {m}",
        f"{esc(m)} & {g(s7.loc[m].qscore9)} & {g(s30.loc[m].qscore9)} "
        f"& {g(s30.loc[m].occurrence_brier)} "
        f"& {g(s30.loc[m].discrete_crps)} \\\\",
        AP,
    )
assert s7.qscore9.idxmin() == s30.qscore9.idxmin() == "oracle"
assert s30.occurrence_brier.idxmin() == s30.discrete_crps.idxmin() == "oracle"
expect(
    "oracle means",
    f"({g(s7.loc['oracle'].qscore9)} at horizon 7 and {g(s30.loc['oracle'].qscore9)} at horizon "
    f"30), the lowest occurrence Brier score ({g(s30.loc['oracle'].occurrence_brier)}) and "
    f"the lowest discrete CRPS ({g(s30.loc['oracle'].discrete_crps)})",
    AP,
)
assert n30.loc["autoets_weekly"].qscore9 > 70000
# The oracle per cell.
syn_cells = pd.read_csv(SYN_RUN / "inference" / "secondary_cells.csv", **ROUND_TRIP)
c30 = syn_cells[syn_cells.horizon == 30]
lowest = 0
not_lowest = {}
for cell, grp in c30.groupby("cell_id"):
    o = grp[grp.model == "oracle"].qscore9.iloc[0]
    others = grp[grp.model != "oracle"]
    if o <= others.qscore9.min():
        lowest += 1
    else:
        not_lowest[cell] = (sorted(others[others.qscore9 < o].qscore9.tolist()), o)
assert lowest == 17 and list(not_lowest) == ["cell00"]
below, o = not_lowest["cell00"]
expect("oracle 17 of 18", "the lowest cell mean in 17 of the 18 cells at horizon 30", AP)
expect("oracle cell00", f"({g(below[0])} and {g(below[1])} against {g(o)})", AP)
expect("paper: oracle 17 of 18", "the lowest cell mean in 17 of the 18 cells", RS)
# PIT.
syn_pit = pd.read_csv(SYN_RUN / "inference" / "pit_histograms.csv", **ROUND_TRIP)
p30 = syn_pit[(syn_pit.horizon == 30) & (syn_pit.status != "unavailable")]
fractions = [c for c in syn_pit.columns if c.startswith("fraction")]
oracle_pit = p30[p30.model == "oracle"]
assert int(oracle_pit.n_values.iloc[0]) == 48600
o_frac = oracle_pit[fractions].to_numpy().ravel()
expect(
    "oracle pit",
    f"each tenth holding {o_frac.min():.3f} to {o_frac.max():.3f} of its 48,600 target days",
    AP,
)
shown = p30[
    p30.model.isin(
        [f"{m}_{v}" for m in MODELS for v in ("hurdle", "completed")] + ["hurdle_count_28"]
    )
][fractions].to_numpy()
expect("shown pit", f"place {shown.min():.3f} to {shown.max():.3f} of theirs in a tenth", AP)
npm_pit = pd.read_csv(NPM_RUN / "inference" / "pit_histograms.csv", **ROUND_TRIP)
q30 = npm_pit[(npm_pit.horizon == 30) & (npm_pit.status != "unavailable")]
hur = q30[q30.model.str.endswith("_hurdle")][fractions].to_numpy()
com = q30[q30.model.str.endswith("_completed")][fractions].to_numpy()
expect(
    "npm pit",
    f"places {hur.min():.3f} to {hur.max():.3f} of its horizon-30 target days in a tenth, "
    f"against {com.min():.3f} to {com.max():.3f} for its completed control",
    AP,
)

# --- per stratum (Table tab:s2strata) ------------------------------------
strata_con = pd.read_csv(NPM_RUN / "inference" / "secondary_strata_contrasts.csv", **ROUND_TRIP)
strata_q = strata_con[strata_con.metric == "qscore9"]
for cid in npm_inf.id:
    cells = []
    for s in ("dense", "sparse", "very_sparse"):
        r = strata_q[(strata_q.id == cid) & (strata_q.stratum == s)].iloc[0]
        assert r.n_entities == {"dense": 100, "sparse": 100, "very_sparse": 9}[s]
        cells.append(f"{g(r.mean_diff)} & {g(r.median_diff)} & {int(r.wins)}")
    expect(f"stratum row {cid}", f"{cid} & " + " & ".join(cells) + " \\\\", AP)


def stratum_wins(ids, s):
    w = strata_q[strata_q.id.isin(ids) & (strata_q.stratum == s)]
    return int(w.wins.min()), int(w.wins.max()), int((w.median_diff == 0).sum())


d_hc, s_hc, v_hc = (stratum_wins(hc.id, s) for s in ("dense", "sparse", "very_sparse"))
d_hk, s_hk, v_hk = (stratum_wins(hk.id, s) for s in ("dense", "sparse", "very_sparse"))
d_rl, s_rl, v_rl = (stratum_wins(rl.id, s) for s in ("dense", "sparse", "very_sparse"))
assert v_hc[2] == 5 and v_hk == (4, 4, 6)
expect(
    "strata hurdle vs control",
    f"on {d_hc[0]} to {d_hc[1]} of the 100 dense series across the six cells, on {s_hc[0]} "
    f"to {s_hc[1]} of the 100 sparse series, and on {v_hc[0]} to {v_hc[1]} of the 9 very sparse "
    "series, where the median difference is exactly 0 in five of the six cells",
    AP,
)
expect(
    "strata hurdle vs count",
    f"on {d_hk[0]} to {d_hk[1]} of the 100 dense series, on {s_hk[0]} to {s_hk[1]} of the "
    "100 sparse series and on 4 of the 9 very sparse series in every cell",
    AP,
)
expect(
    "strata raw",
    f"on {d_rl[0]} to {d_rl[1]} dense, {s_rl[0]} to {s_rl[1]} sparse and {v_rl[0]} or {v_rl[1]} "
    "very sparse series",
    AP,
)
expect(
    "summary strata",
    f"on {d_hc[0]} to {d_hc[1]} of the 100 dense series, on {s_hc[0]} to {s_hc[1]} of the "
    f"100 sparse series and on {v_hc[0]} to {v_hc[1]} of the 9 very sparse series, and lower "
    f"than \\hc{{}} on {d_hk[0]} to {d_hk[1]} dense, {s_hk[0]} to {s_hk[1]} sparse and 4 of "
    "9 very sparse",
    RS,
)

# --- per cell (Table tab:s2cells, Figure fig:s2cells) ----------------------
cells_con = pd.read_csv(SYN_RUN / "inference" / "secondary_cells_contrasts.csv", **ROUND_TRIP)
cq = cells_con[(cells_con.metric == "qscore9") & (cells_con.horizon == 30)]
assert cq.n_entities.eq(30).all() and cq.cell_id.nunique() == 18
for cell, grp in cq.groupby("cell_id", sort=True):
    r0 = grp.iloc[0]
    vals = [
        f"{g(grp[grp.id == sid].mean_diff.iloc[0])} ({int(grp[grp.id == sid].wins.iloc[0])})"
        for sid in ["S01", "S02", "S03", "S04", "S05", "S06"]
    ]
    expect(
        f"cell row {cell}",
        f"{cell} & {r0.zero_probability} & {int(r0.positive_mean)} & {r0.persistence} & "
        + " & ".join(vals)
        + " \\\\",
        AP,
    )
z95 = cq[(cq.zero_probability == 0.95) & (cq.positive_mean >= 5)]
assert len(z95) == 24 and int((z95.mean_diff < 0).sum()) == 23
expect("z=0.95 cells", "23 of the 24 differences are negative", AP)
big = cq[
    (cq.zero_probability == 0.2)
    & (cq.positive_mean == 25)
    & (cq.persistence == 0.8)
    & cq.reference.str.endswith("_completed")
]
assert len(big) == 3 and cq.nlargest(3, "mean_diff").mean_diff.min() == big.mean_diff.min()
expect(
    "largest cells",
    f"the hurdle scores {g(big.mean_diff.min())} to {g(big.mean_diff.max())} above its control "
    "at $\\rho = 0.8$",
    AP,
)
mu1 = cq[(cq.positive_mean == 1) & (cq.persistence == 0) & (cq.reference == "hurdle_count_28")]
mu1_all = cq[(cq.positive_mean == 1) & (cq.reference == "hurdle_count_28")]
assert len(mu1_all) == 18 and (mu1_all.wins == 0).all()
assert (mu1[mu1.zero_probability != 0.8].mean_diff == 0).all()

# --- the runs: run.json, integrity, recomputation, readiness ---------------
npm_run = load(NPM_RUN / "run.json")
syn_run = load(SYN_RUN / "run.json")
for run, commit, n_series, wall, est, budget in (
    (npm_run, "3057b16dbd2f9b218449352717ef4adabc2f72f7", 209, 692, 1741, 3600),
    (syn_run, "3fc3411f7c683aaf98e6fad28b26aa9c92ab00b9", 540, 1317, 1539, 2400),
):
    assert run["status"] == "complete" and run["failures"] == [] and run["resumes"] == []
    assert len(run["invocations"]) == 1 and run["invocations"][0]["series_completed"] == n_series
    assert int(run["invocations"][0]["wall_seconds"]) == wall
    assert run["metadata"]["metadata"]["implementation_commit"] == commit
    assert run["metadata"]["readiness"]["estimated_seconds"] == est
    assert run["metadata"]["readiness"]["approved_by"] == "Victor Prchlik"
    hw = run["metadata"]["hardware"]
    assert hw["gpu_model"] == "NVIDIA GeForce RTX 4070 SUPER" and hw["gpu_driver"] == "610.88"
    assert (
        hw["cuda_version"] == "12.8"
        and hw["pytorch_version"] == "2.11.0+cu128"
        and hw["batch_size"] == 1
    )
    assert run["invocations"][0]["memory"]["peak_reserved_bytes"] == 2948595712
    expect(f"run commit {commit[:7]}", f"implementation commit \\texttt{{{commit}}}", RS)
    expect(f"run estimate {est}", f"an estimate of {est:,}", RS)
assert npm_run["metadata"]["readiness"]["approved_at"] == "2026-10-15T23:09:06Z"
assert syn_run["metadata"]["readiness"]["approved_at"] == "2026-10-15T20:13:56Z"
assert npm_run["started_at"].startswith("2026-10-15T23:27") and npm_run["completed_at"].startswith(
    "2026-10-15T23:38"
)
assert syn_run["started_at"].startswith("2026-10-15T20:16") and syn_run["completed_at"].startswith(
    "2026-10-15T20:38"
)
expect("npm run start", "The npm run started 2026-10-15 23:27 UTC", RS)
expect("synthetic run start", "The synthetic run started 2026-10-15 20:16 UTC", RS)
expect("npm wall", "in 692 seconds (699 for the whole process)", RS)
expect("synthetic wall", "in 1,317 seconds (1,323 for the whole process)", RS)
expect("npm forecasts", "20,064 forecasts (209 series, 3 origins, 2 horizons, 16 variants)", RS)
expect(
    "synthetic forecasts",
    "55,080 forecasts (540 series, 3 origins, 2 horizons, the 16 variants and the oracle)",
    RS,
)
assert 209 * 3 * 2 * 16 == 20064 and 540 * 3 * 2 * 17 == 55080
expect("hardware", "NVIDIA GeForce RTX 4070 SUPER (driver 610.88, CUDA 12.8, PyTorch 2.11.0)", RS)
expect("peak memory", "2,948,595,712 bytes", RS)
results_npm = (NPM_RUN / "RESULTS-npm.md").read_text(encoding="utf-8")
results_syn = (SYN_RUN / "RESULTS-synthetic.md").read_text(encoding="utf-8")
assert "692 seconds inside the\nrun and 699 for the whole process" in results_npm
assert "1,317 seconds inside the run\nand 1,323 seconds for the whole process" in results_syn
assert (
    "from 23:14:58 to 23:26:22 UTC, 3 seconds apart: 209 attempts and 209 answers, with no "
    "retry\nand no failure" in results_npm
)
expect(
    "targets requested",
    "between 23:14 and 23:26 UTC, 209 attempts and 209 answers, with no retry and no failure",
    RS,
)
npm_integrity = load(NPM_RUN / "integrity" / "integrity.json")
assert npm_integrity["status"] == "pass" and npm_integrity["failed_forecasts"] == 0
for key in (
    "qscore9",
    "context_scaled_qscore9",
    "occurrence_brier",
    "zero",
    "positive_over",
    "positive_under",
):
    chk = npm_integrity["checks"][key]
    assert chk["disagreements"] == 0, key
assert npm_integrity["checks"]["qscore9"]["compared"] == 20064
assert (
    npm_integrity["run"]["checkpoints_verified"] == 209
    if "checkpoints_verified" in npm_integrity["run"]
    else True
)
expect(
    "npm integrity",
    "for all 20,064 forecasts from the saved deciles, targets and laws, with 0 disagreements",
    RS,
)
recompute = load(SYN_RUN / "score-recompute.json")
assert recompute["series"] == 540 and recompute["windows"] == 55080
assert all(v == 0.0 for v in recompute["max_abs_difference"].values())
expect(
    "synthetic recompute", "for all 55,080 forecasts with a largest absolute difference of 0.0", RS
)
syn_prov = load(SYN_RUN / "inference" / "provenance.json")
npm_prov = load(NPM_RUN / "inference" / "provenance.json")
assert (
    len(syn_prov["run"]["checkpoint_sha256"]) == 540
    and len(npm_prov["run"]["checkpoint_sha256"]) == 209
)
assert npm_prov["implementation_commit_at_inference"] == "3057b16dbd2f9b218449352717ef4adabc2f72f7"
assert (
    npm_prov["uncommitted_changes_at_inference"] == ""
    and syn_prov["uncommitted_changes_at_inference"] == ""
)
assert (
    npm_prov["packages"]
    == syn_prov["packages"]
    == {"numpy": "2.5.3", "pandas": "2.3.3", "scipy": "1.18.1"}
)
expect("packages", "NumPy 2.5.3, SciPy 1.18.1 and pandas 2.3.3", PT)
expect(
    "checkpoints",
    "The 540 synthetic checkpoints (about 0.9 GB) and the 209 npm checkpoints (338 MB)",
    PT,
)
assert "338 MB)" in results_npm and "about 0.9 GB)" in results_syn

# --- the three zero days (daily_summary.csv) and the post-hoc sensitivity ---------------------
daily = pd.read_csv(NPM_RUN / "target-pull" / "daily_summary.csv", **ROUND_TRIP).set_index("date")
assert len(daily) == 365 and daily.series.eq(209).all()
for day in ("2026-07-12", "2026-08-14"):
    assert daily.loc[day].series_zero == 209 and daily.loc[day].total_downloads == 0
assert (
    daily.loc["2026-06-25"].largest_series_count == 0 and daily.loc["2026-06-25"].series_zero == 92
)
tot = lambda d: f"{int(daily.loc[d].total_downloads):,}"  # noqa: E731
expect(
    "zero days neighbours",
    f"between neighbours of {tot('2026-07-11')} and {tot('2026-07-13')} "
    f"downloads, and {tot('2026-08-13')} "
    f"and {tot('2026-08-15')}",
    RS,
)
expect(
    "june 25",
    f"between {int(daily.loc['2026-06-24'].largest_series_count):,} and "
    f"{int(daily.loc['2026-06-26'].largest_series_count):,}, "
    f"when {int(daily.loc['2026-06-25'].series_zero)} of the 209 series "
    f"read 0 against {int(daily.loc['2026-06-24'].series_zero)} "
    f"and {int(daily.loc['2026-06-26'].series_zero)}",
    RS,
)
context_days = daily.loc[:"2026-06-02"]
assert len(context_days) == 275 and len(daily.loc["2026-06-03":]) == 90
expect(
    "context zeros",
    f"No day of the 275-day context reads 0 for more than {int(context_days.series_zero.max())} "
    "of the 209 series, and the largest series "
    f"never reads below {int(context_days.largest_series_count.min()):,} "
    "there",
    RS,
)
for day, block in (
    ("2026-06-25", "2026-06-03+30"),
    ("2026-07-12", "2026-07-03+30"),
    ("2026-08-14", "2026-08-02+30"),
):
    assert daily.loc[day].windows == block
assert "npm zero days — dated addition, 2026-10-16" in protocol and "### 6." in protocol
expect("addition 6", "dated addition of 2026-10-16 to the protocol, item 6", RS)
sens = pd.read_csv(NPM_RUN / "posthoc" / "sensitivity_inference.csv", **ROUND_TRIP)
three = sens[sens.scenario == "three_days"].set_index("id")
two = sens[sens.scenario == "two_panel_wide_days"].set_index("id")
assert len(three) == 18 and len(two) == 18
assert three.forecasts_rescored.eq(10032).all() and two.forecasts_rescored.eq(6688).all()
assert (
    not three.mean_sign_changes.any()
    and not three.larger_sum_changes.any()
    and not three.rejection_changes.any()
)
assert int(three.reject_bh_005.sum()) == 12
assert not two.mean_sign_changes.any() and not two.larger_sum_changes.any()
assert two[two.rejection_changes].index.tolist() == ["E06"] and int(two.reject_bh_005.sum()) == 11
e06 = two.loc["E06"]
assert e06.larger_sum_favors == "model" and not e06.reject_bh_005
expect(
    "sensitivity three", "re-scores 10,032 forecasts, none of the eighteen conclusions changes", RS
)
expect("sensitivity two", "re-scores 6,688 forecasts, one conclusion changes", RS)
expect(
    "E06 sensitivity",
    f"with adjusted $p$ {g(e06.wilcoxon_p_bh, 3)} and raw $p$ {g(e06.wilcoxon_p, 3)} against "
    f"{g(e06.registered_wilcoxon_p_bh, 3)} and {g(e06.registered_wilcoxon_p, 3)} registered",
    RS,
)
expect("E06 wins", f"the model lower on {int(e06.wins)} of 209 series", RS)
for cid in ("E04", "E10", "E16"):
    r = three.loc[cid]
    expect(
        f"sensitivity {cid} grows",
        f"{cid} from {g(r.registered_mean_diff)} to {g(r.mean_diff)}",
        RS,
    )
for cid in npm_inf.id:
    a, b = three.loc[cid], two.loc[cid]
    yn = lambda v: "yes" if v else "no"  # noqa: E731
    expect(
        f"sensitivity row {cid}",
        f"{cid} & {g(a.registered_mean_diff)} & {pval(a.registered_wilcoxon_p_bh)} "
        f"& {yn(a.registered_reject_bh_005)} "
        f"& {g(a.mean_diff)} & {pval(a.wilcoxon_p_bh)} & {yn(a.reject_bh_005)} & {g(b.mean_diff)} "
        f"& {pval(b.wilcoxon_p_bh)} & {yn(b.reject_bh_005)} & {a.larger_sum_favors} \\\\",
        AP,
    )
    assert a.larger_sum_favors == b.larger_sum_favors == a.registered_larger_sum_favors
    assert a.registered_reject_bh_005 == npm_inf[npm_inf.id == cid].reject_bh_005.iloc[0]
h7 = [c for c in npm_inf.id if npm_inf[npm_inf.id == c].horizon.iloc[0] == 7]
for cid in h7:
    for df in (three, two):
        r = df.loc[cid]
        assert (
            r.mean_diff == r.registered_mean_diff
            and r.median_diff == r.registered_median_diff
            and r.wilcoxon_p == r.registered_wilcoxon_p
        )
sens_json = load(NPM_RUN / "posthoc" / "sensitivity.json")
assert sens_json["head"].startswith("e41fdf2") and sens_json["uncommitted_changes"] == ""
assert sens_json["started_at"].startswith("2026-10-16")
expect("sensitivity head", "at HEAD \\texttt{e41fdf2}", PT)
expect("sensitivity date", "computed on 2026-10-16", RS)
expect(
    "paper: sensitivity",
    "none of the eighteen conclusions changes without all three, and one row, E06, stops "
    "rejecting without the two panel-wide days",
    PT,
)
expect("summary: sensitivity", "none of the eighteen conclusions changes", PS)

# --- the paper's summary page ------------------------------------------------
expect("summary: npm panel", "209 series", PS + PT)
expect("summary: 540", "540", PS + PT)
expect("summary: twelve", "twelve of the eighteen", PS)
assert "Study 2, synthetic component" in (ROOT / "RESULTS.md").read_text(encoding="utf-8")

# --- report -----------------------------------------------------------
for line in failures:
    print("FAIL", line)
for line in skipped:
    print("SKIP", line)
print(f"{checks} checks, {len(failures)} failures, {len(skipped)} skipped")
sys.exit(1 if failures else 0)

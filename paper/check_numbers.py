"""Read-only check that every number in paper/main.tex and paper/SUMMARY.md matches its saved file.

Loads the CSV and JSON files under reports/registered-2026-09-13/, formats each figure the way the
report prints it, and asserts that the formatted text appears in main.tex or SUMMARY.md (whitespace
collapsed, so line wrapping does not matter). The Study 2 and Study 3 sections under paper/sections/
are read the same way and checked against study/study2/, study/study3/, the panel and run
directories under reports/, PROTOCOL.md and the dated documents, as sources.md lists. Version 1
numbers are checked against the preserved
documents under v1_reference/ when that local folder exists; otherwise they are listed as skipped.
Nothing in the tree is written; when pdflatex and bibtex are on PATH, paper.tex is built into the
ignored folder data/cache/build/check/ and its log is read, and otherwise that check is listed as
skipped. Run from the repository root:

    .\\.venv\\Scripts\\python.exe paper/check_numbers.py
"""

import hashlib
import json
import os
import re
import shutil
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
PAPER_TEX = PAPER / "paper.tex"
# Since 2026-10-17 the paper is organized by question: its body is sections/01-introduction.tex to
# 09-reproducibility.tex, the appendix adds app-study1.tex, the Study 2 and Study 3 detail and table
# files and app-runs.tex, and paper.tex is read with every \input expanded. A sentence that may sit
# anywhere in the paper is checked against the expanded paper; the appendix files are also checked
# on their own where a table belongs to one of them.
BODY_FILES = (
    "01-introduction.tex",
    "02-related-work.tex",
    "03-design.tex",
    "04-models-add.tex",
    "05-occurrence.tex",
    "06-positive-law.tex",
    "07-discussion.tex",
    "08-limitations.tex",
    "09-reproducibility.tex",
    "app-study1.tex",
    "app-runs.tex",
)
DETAIL, PANEL_DETAIL, APPENDIX = (
    "study2-design-detail.tex",
    "study2-panel-detail.tex",
    "study2-appendix.tex",
)
SECTION_FILES = BODY_FILES + (DETAIL, PANEL_DETAIL, APPENDIX)
for name in SECTION_FILES:
    TEXT[name] = text(SECTIONS / name)
TEXT["paper.tex"] = text(PAPER_TEX)
QUESTION = DESIGN = PANEL = RESULTS = "paper.tex"
Q = D = P = R = ("paper.tex",)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def esc(name):
    return name.replace("_", "\\_")


# The public boundary: no operating-layer vocabulary in a committed file. The words are read from
# local/boundary-words.txt (one per line; the local folder is never committed); without the file the
# check is skipped, so that this committed script never spells the words it forbids.
BOUNDARY_WORDS_FILE = ROOT / "local" / "boundary-words.txt"
BOUNDARY_WORDS = (
    [w.strip() for w in BOUNDARY_WORDS_FILE.read_text(encoding="utf-8").splitlines() if w.strip()]
    if BOUNDARY_WORDS_FILE.exists()
    else None
)


def boundary(names):
    global checks
    if BOUNDARY_WORDS is None:
        skipped.append(
            "local/boundary-words.txt absent; the public-boundary word check was skipped"
        )
        return
    for name in names:
        checks += 1
        hits = [w for w in BOUNDARY_WORDS if re.search(rf"\b{re.escape(w)}\b", TEXT[name])]
        if hits:
            failures.append(
                f"{name}: operating-layer vocabulary, {len(hits)} word(s) from the local list"
            )


boundary(SECTION_FILES)

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
expect("addition 2026-10-12 commit", "\\texttt{8db0d73}", D)
expect("addition 2026-10-15 commit", "\\texttt{5be2ce9}", D)
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
    for group in re.findall(r"\\cite[pt]?\{([^}]*)\}", TEXT[name]):
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
for stale in (
    "study2-results-placeholder.tex",
    "study2-question.tex",
    "study2-design.tex",
    "study2-panel.tex",
    "study2-results.tex",
    "study3-question.tex",
    "study3-design.tex",
    "study3-panel.tex",
    "study3-results.tex",
):
    if (SECTIONS / stale).exists():
        failures.append(f"{stale} still exists; the paper no longer reads it")
assert len(pkg_spec["variants"]) == 16
expect("results: replicates", f"blocks (of {grid['replicates_per_cell']})", R)
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
        m, e = s.split("e")
        return f"${m} \\times 10^{{{int(e)}}}$"
    v = float(s)
    return f"{v:,.0f}" if abs(v) >= 1000 else s


def pval(x):
    """Three significant figures; small values as the TeX power of ten."""
    s = f"{x:.3g}"
    if "e" in s:
        m, e = s.split("e")
        return f"${m} \\times 10^{{{int(e)}}}$"
    return s


def contrast(model, reference):
    if reference.endswith("_completed"):
        return "hurdle vs completed"
    if reference == "hurdle_count_28":
        return "hurdle vs count hurdle"
    if reference == "local_mean_28":
        return "raw vs local mean"
    raise ValueError(reference)


def family_line(r):
    return (
        f"{r.id} & {LABEL[r.model.split('_')[0]]} & {contrast(r.model, r.reference)} & "
        f"{r.horizon} & {g(r.mean_diff)} & [{g(r.mean_diff_ci_low)}, {g(r.mean_diff_ci_high)}] & "
        f"{g(r.median_diff)} & "
        f"{int(r.wins)} / {int(r.ties)} / {int(r.losses)} & {pval(r.wilcoxon_p_bh)} \\\\"
    )


# The public boundary, for the new files and the expanded paper.
boundary((RESULTS, APPENDIX, DETAIL, PANEL_DETAIL, "paper.tex", "PAPER-SUMMARY.md"))

# The report's shared files that the paper still reads are in both documents unchanged: the author's
# statement, Study 1's limitation items and the report's four appendix files. The report's own
# sections are condensed in the paper's Appendix A and are read by main.tex alone.
for shared_name in (
    "author-statement.tex",
    "s1-limitations-items.tex",
    "app-design.tex",
    "app-v1.tex",
    "app-tables.tex",
    "app-repro.tex",
):
    shared = PAPER / "shared" / shared_name
    expect(f"shared {shared.name} in both documents", text(shared), ("main.tex", "paper.tex"))
for name in SECTION_FILES:
    expect(f"section {name} in paper.tex", text(SECTIONS / name), PT)
checks += 1
if re.search(r"\btbd\b", TEXT["paper.tex"]):
    failures.append("paper.tex: a 'tbd' remains")

expect("results: variants", f"2 horizons, {len(pkg_spec['variants'])} variants)", PT)
expect("results: synthetic series", f"({grid['n_series']} series, 3 origins", PT)
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
expect(
    "paper: two of six and three",
    "two of six npm tests and all three grid tests reject against it",
    PT + PS,
)
expect("paper: no pooled test", "No pooled test favors the substitution at $q = 0.05$", PT)
expect("summary: no pooled test", "No pooled test favors the substitution at q = 0.05", PS)
expect("results: five against", "all five synthetic rejections are against the hurdle variant", RS)
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
    f"from {g(hc.mean_diff.min())} to {g(hc.mean_diff.max())} "
    "(carried by \\texttt{aggregate-error}), "
    "with every interval above zero",
    RS,
)
e01, e04, e13 = (hc[hc.id == i].iloc[0] for i in ("E01", "E04", "E13"))
assert e01.median_diff < 0 and e01.wins > e01.losses
assert (
    e04.wins > e04.losses and e04.median_diff < 0 and e13.wins > e13.losses and e13.median_diff < 0
)
expect(
    "E01 typical series",
    f"in E01 the typical series leans to the hurdle, lower on {int(e01.wins)} of 209 series with a "
    f"median of {g(e01.median_diff)}",
    RS,
)
e10, e16 = hc[hc.id == "E10"].iloc[0], hc[hc.id == "E16"].iloc[0]
nonreject = hc[~hc.reject_bh_005].wilcoxon_p_bh
assert (sc.mean_diff_ci_low > 0).all() and sc.reject_bh_005.all()
expect(
    "synthetic hurdle means",
    f"from {g(sc.mean_diff.min())} to {g(sc.mean_diff.max())}, with every interval above zero",
    RS,
)
assert sorted(sc.wins.unique()) == [5, 6]
expect("synthetic hurdle wins", "lower on 5 or 6 of the 30 replicate blocks", RS)
# Hurdle against the count hurdle.
assert hk.reject_bh_005.all() and (hk.mean_diff_ci_high < 0).all() and (hk.median_diff < 0).all()
expect(
    "count hurdle p",
    f"adjusted $p$ from {pval(hk.wilcoxon_p_bh.max())} to {pval(hk.wilcoxon_p_bh.min())}",
    RS,
)
expect(
    "count hurdle means",
    f"from {g(hk.mean_diff.max())} to {g(hk.mean_diff.min())} "
    "(carried by \\texttt{aggregate-error}), "
    "with every interval below zero",
    RS,
)
expect("count hurdle medians", f"from {g(hk.median_diff.max())} to {g(hk.median_diff.min())}", RS)
s02, s04, s06 = (sk[sk.id == i].iloc[0] for i in ("S02", "S04", "S06"))
assert s02.reject_bh_005 and s06.reject_bh_005 and not s04.reject_bh_005
assert (
    s02.mean_diff_ci_low > 0
    and s06.mean_diff_ci_low > 0
    and s04.mean_diff_ci_low < 0 < s04.mean_diff_ci_high
)
assert s02.wins == s06.wins
# Raw deciles against the local mean.
assert rl[rl.reject_bh_005].id.tolist() == ["E06", "E09", "E12", "E18"]
assert (rl.mean_diff_ci_high < 0).all()
e03, e15 = rl[rl.id == "E03"].iloc[0], rl[rl.id == "E15"].iloc[0]
expect(
    "raw non-rejects", f"adjusted $p$ {pval(e03.wilcoxon_p_bh)} and {pval(e15.wilcoxon_p_bh)}", RS
)
expect(
    "raw means",
    f"from {g(rl.mean_diff.max())} to {g(rl.mean_diff.min())} "
    "(carried by \\texttt{aggregate-error}), "
    "with every interval below zero",
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
expect("dominant mean", "7,637,136 downloads a day", P)
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
syn_c = [syn_acc.loc[(30, f"{m}_completed")] for m in MODELS]
# The typical npm series and the trade: the median series' zero-day difference (hurdle minus
# completed) is positive in every cell, so the typical series does not follow the mean's trade.
npm_series = pd.read_csv(NPM_RUN / "inference" / "series_scores.csv", **ROUND_TRIP)


def series_paired(df, a, b, h, col="qscore9"):
    x = df[(df.model == a) & (df.horizon == h)].set_index("series_id")[col]
    y = df[(df.model == b) & (df.horizon == h)].set_index("series_id")[col]
    return (x - y).dropna()


zero_medians = [
    float(series_paired(npm_series, f"{m}_hurdle", f"{m}_completed", h, "zero").median())
    for h in (7, 30)
    for m in MODELS
]
assert min(zero_medians) > 0
expect(
    "typical series zero-day trade",
    f"positive, against the hurdle, in all six cells ({min(zero_medians):.3f} to "
    f"{max(zero_medians):.3f})",
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
expect("scaled vs count hurdle", f"{g(sc_hk.mean_diff.max())} to {g(sc_hk.mean_diff.min())}", AP)
for cid in ("E06", "E09", "E12", "E18"):
    assert sc_by.loc[cid].mean_diff_ci_high < 0
for cid in ("E03", "E15"):
    assert sc_by.loc[cid].mean_diff_ci_low < 0 < sc_by.loc[cid].mean_diff_ci_high
syn_sc30 = syn_sc[syn_sc.horizon == 30]
assert ((syn_sc30.mean_diff_ci_low < 0) & (syn_sc30.mean_diff_ci_high > 0)).all()
expect("synthetic scaled", "On the grid every scaled interval includes zero", AP)
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
    PT,
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
tied_cells = sorted(
    cell
    for cell, grp in c30.groupby("cell_id")
    if (
        grp[grp.model == "dynamic_count"].qscore9.iloc[0]
        == grp[grp.model == "oracle"].qscore9.iloc[0]
    )
)
assert tied_cells == ["cell12", "cell14", "cell16"], tied_cells
expect("oracle 17 of 18", "no forecaster scores below it in 17 of the 18 cells at horizon 30", AP)
expect(
    "oracle ties",
    "(\\texttt{cell12}, \\texttt{cell14} and \\texttt{cell16}, with $z = 0.95$ and $\\rho = 0$) "
    "\\texttt{dynamic\\_count} ties it exactly",
    AP,
)
expect("oracle cell00", f"({g(below[0])} and {g(below[1])} against {g(o)})", AP)
expect("paper: oracle 17 of 18", "which no forecaster scores below in 17 of the 18 cells", RS)
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
# The regime reading (the referee's W1): the declared secondary strata, cell by cell.
sparse_w = {
    cid: int(strata_q[(strata_q.id == cid) & (strata_q.stratum == "sparse")].wins.iloc[0])
    for cid in hc.id
}
assert [sparse_w[c] for c in ("E01", "E07", "E13")] == [81, 60, 66]
expect(
    "regime: sparse h7",
    f"lower on {sparse_w['E01']}, {sparse_w['E07']} and {sparse_w['E13']} of the 100 sparse "
    "series at horizon 7, for Chronos-2, TimesFM 3 and TimesFM 2.5",
    RS,
)
expect(
    "regime: sparse h30",
    f"and on {sparse_w['E04']}, {sparse_w['E10']} and {sparse_w['E16']} of them at horizon 30",
    RS,
)
expect("regime: dense", f"it scores lower on {d_hc[0]} to {d_hc[1]} of 100 in every cell", RS)
d_hc7 = stratum_wins(hc[hc.horizon == 7].id, "dense")
expect(
    "abstract: regime",
    f"it scores lower for {sparse_w['E01']}, {sparse_w['E07']} and {sparse_w['E13']} of 100 sparse "
    f"series and {d_hc7[0]} to {d_hc7[1]} of 100 dense ones",
    PT + PS,
)
expect(
    "regime: dense vs count hurdle",
    f"on {d_hk[0]} to {d_hk[1]} of the 100 dense series and on {s_hk[0]} to {s_hk[1]} of the "
    "100 sparse ones",
    RS,
)
# The post-hoc stratum tests, the empirical hurdle and the dynamic count, recomputed from the
# saved per-series scores (series_scores.csv of each run).
from scipy import stats  # noqa: E402

strat_of = (
    npm_series[(npm_series.horizon == 7) & (npm_series.model == "chronos2_raw")]
    .set_index("series_id")
    .stratum
)


def summ(d):
    nz = d[d != 0]
    return (
        int((d < 0).sum()),
        int((d == 0).sum()),
        int((d > 0).sum()),
        float(d.median()),
        float(stats.wilcoxon(nz).pvalue),
    )


regime_rows, sparse_p7, sparse_p30, dense_p7 = [], [], [], []
for h in (7, 30):
    for m in MODELS:
        d = series_paired(npm_series, f"{m}_hurdle", f"{m}_completed", h)
        parts = []
        for s in ("dense", "sparse", "very_sparse"):
            w, ti, lo, med, pv = summ(d[strat_of.loc[d.index] == s])
            parts.append(f"{w} / {ti} / {lo} & {g(med)} & {pval(pv)}")
            if s == "sparse":
                (sparse_p7 if h == 7 else sparse_p30).append(pv)
                assert (
                    w
                    == sparse_w[
                        {7: "E01", 30: "E04"}[h]
                        if m == "chronos2"
                        else {7: "E07", 30: "E10"}[h]
                        if m == "timesfm3"
                        else {7: "E13", 30: "E16"}[h]
                    ]
                )
            if s == "dense" and h == 7:
                dense_p7.append((w, lo, pv))
        expect(f"regime row {m} {h}", f"{LABEL[m]} & {h} & " + " & ".join(parts) + " \\\\", AP)
assert max(sparse_p7) < 0.002 and all(lo > w and pv < 0.05 for w, lo, pv in dense_p7)
expect(
    "regime: sparse p",
    "raw $p$ below 0.002 for all three sparse-stratum contrasts at horizon 7",
    AP,
)
expect(
    "regime: sparse p h30",
    f"from {g(min(sparse_p30), 2)} to {g(max(sparse_p30), 3)} at horizon 30",
    AP,
)
assert abs(28.5 / 29 - 0.9828) < 5e-5 and abs(1 - 28.5 / 29 - 0.0172) < 5e-5
expect(
    "regime: jeffreys",
    "gets $p = 28.5 / 29$, so the hurdle forces about 1.7 percent of mass onto zero",
    AP,
)
emp_rows, emp_dense, emp_sparse, emp_vs = [], [], [], []
comp_vs_emp = {}
for h in (7, 30):
    for m in MODELS:
        d = series_paired(npm_series, f"{m}_hurdle", "hurdle_empirical_28", h)
        parts = []
        for s in ("dense", "sparse", "very_sparse"):
            w, ti, lo, med, pv = summ(d[strat_of.loc[d.index] == s])
            parts.append(f"{w} / {ti} / {lo}")
            {"dense": emp_dense, "sparse": emp_sparse, "very_sparse": emp_vs}[s].append(w)
        dc = series_paired(npm_series, f"{m}_completed", "hurdle_empirical_28", h)
        w, ti, lo, med, pv = summ(dc)
        comp_vs_emp[(m, h)] = w
        expect(
            f"empirical row {m} {h}",
            f"{LABEL[m]} & {h} & "
            + " & ".join(parts)
            + f" & {w} / {ti} / {lo} & {g(med)} & {pval(pv)} \\\\",
            AP,
        )
expect(
    "empirical: hurdle by stratum",
    f"lower on {min(emp_dense)} to {max(emp_dense)} of the 100 dense series and on "
    f"{min(emp_sparse)} to {max(emp_sparse)} of the 100 sparse",
    RS,
)
c30v = [comp_vs_emp[(m, 30)] for m in MODELS]
syn_series = pd.read_csv(SYN_RUN / "inference" / "series_scores.csv", **ROUND_TRIP)
blk = syn_series[syn_series.horizon == 30].groupby(["model", "replicate"]).qscore9.mean().unstack(0)
dyn_lower = [int((blk["dynamic_count"] < blk[f"{m}_completed"]).sum()) for m in MODELS]
expect(
    "discussion: dynamic count blocks",
    f"lower than each completed model in {min(dyn_lower)} to {max(dyn_lower)} of 30 blocks",
    PT,
)
assert (
    int((blk["dynamic_count"] < blk["hurdle_count_28"]).sum())
    == int((blk["dynamic_count"] < blk["local_mean_28"]).sum())
    == 26
)
comp_lower = [
    summ(series_paired(npm_series, f"{m}_completed", "dynamic_count", h))[0]
    for m in MODELS
    for h in (7, 30)
]
expect(
    "dynamic count: npm",
    f"the completed models are lower on {min(comp_lower)} to {max(comp_lower)} of 209 series",
    RS,
)
dyn30 = s30.loc["dynamic_count"].qscore9
comp30 = [s30.loc[f"{m}_completed"].qscore9 for m in MODELS]
assert (
    dyn30 < min(comp30)
    and dyn30 < s30.loc["hurdle_count_28"].qscore9
    and dyn30 > s30.loc["oracle"].qscore9
)
assert dyn30 == s30.drop("oracle").qscore9.min()
expect(
    "dynamic count: means",
    f"is {g(dyn30)} against {g(min(comp30))} to {g(max(comp30))} for the three completed models, "
    f"{g(s30.loc['hurdle_count_28'].qscore9)} for the count hurdle and "
    f"{g(s30.loc['oracle'].qscore9)} for the oracle",
    RS,
)
cmeta = (
    pd.read_csv(SYN_RUN / "inference" / "secondary_cells_contrasts.csv", **ROUND_TRIP)
    .drop_duplicates("cell_id")
    .set_index("cell_id")
)
c30s = syn_series[syn_series.horizon == 30].copy()
c30s["z"] = c30s.cell_id.map(cmeta.zero_probability)
by_z = {}
for z in (0.2, 0.8, 0.95):
    sub = c30s[c30s.z == z]
    by_z[z] = [
        int(
            (
                sub[sub.model == f"{m}_hurdle"].groupby("replicate").qscore9.mean()
                - sub[sub.model == f"{m}_completed"].groupby("replicate").qscore9.mean()
                < 0
            ).sum()
        )
        for m in MODELS
    ]
expect(
    "regime: grid by z",
    f"in {min(by_z[0.2])} to {max(by_z[0.2])} of 30 replicate blocks at $z = 0.2$, in "
    f"{min(by_z[0.8])} to {max(by_z[0.8])} at $z = 0.8$ and in {min(by_z[0.95])} to "
    f"{max(by_z[0.95])} at $z = 0.95$",
    AP,
)
expect(
    "regime: grid by z, body",
    f"in {min(by_z[0.2])} to {max(by_z[0.2])} of 30 replicate blocks at $z = 0.2$ against "
    f"{min(by_z[0.95])} to {max(by_z[0.95])} at $z = 0.95$",
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
    expect(f"run commit {commit[:7]}", f"implementation commit \\texttt{{{commit}}}", PT)
    expect(f"run estimate {est}", f"an estimate of {est:,}", PT)
assert npm_run["metadata"]["readiness"]["approved_at"] == "2026-10-15T23:09:06Z"
assert syn_run["metadata"]["readiness"]["approved_at"] == "2026-10-15T20:13:56Z"
assert npm_run["started_at"].startswith("2026-10-15T23:27") and npm_run["completed_at"].startswith(
    "2026-10-15T23:38"
)
assert syn_run["started_at"].startswith("2026-10-15T20:16") and syn_run["completed_at"].startswith(
    "2026-10-15T20:38"
)
expect("npm run start", "The npm run started 2026-10-15 23:27 UTC", PT)
expect("synthetic run start", "The synthetic run started 2026-10-15 20:16 UTC", PT)
expect("npm wall", "in 692 seconds (699 for the whole process)", PT)
expect("synthetic wall", "in 1,317 seconds (1,323 for the whole process)", PT)
expect("npm forecasts", "20,064 forecasts (209 series, 3 origins, 2 horizons, 16 variants)", PT)
expect(
    "synthetic forecasts",
    "55,080 forecasts (540 series, 3 origins, 2 horizons, the 16 variants and the oracle)",
    PT,
)
assert 209 * 3 * 2 * 16 == 20064 and 540 * 3 * 2 * 17 == 55080
expect("hardware", "NVIDIA GeForce RTX 4070 SUPER (driver 610.88, CUDA 12.8, PyTorch 2.11.0)", PT)
expect("peak memory", "2,948,595,712 bytes", PT)
results_npm = (NPM_RUN / "RESULTS-npm.md").read_text(encoding="utf-8")
results_syn = (SYN_RUN / "RESULTS-synthetic.md").read_text(encoding="utf-8")
assert "692 seconds inside the\nrun and 699 for the whole process" in results_npm
assert "1,317 seconds inside the run\nand 1,323 seconds for the whole process" in results_syn
assert (
    "from 23:14:58 to 23:26:22 UTC, 3 seconds apart: 209 attempts and 209 answers, with no "
    "retry\nand no failure" in results_npm
)
pull = load(NPM_RUN / "target-pull" / "pull.json")
first_request = min(inv["started_at"] for inv in pull["invocations"])
assert first_request.startswith("2026-10-15T23:15"), first_request
expect(
    "targets requested",
    "between 23:15 and 23:26 UTC, 209 attempts and 209 answers, with no retry and no failure",
    PT,
)
expect("panel: first target request", "first requested on 2026-10-15 at 23:15 UTC", P)
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
    PT,
)
recompute = load(SYN_RUN / "score-recompute.json")
assert recompute["series"] == 540 and recompute["windows"] == 55080
assert all(v == 0.0 for v in recompute["max_abs_difference"].values())
expect(
    "synthetic recompute", "for all 55,080 forecasts with a largest absolute difference of 0.0", PT
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
    AP,
)
expect(
    "june 25",
    f"between {int(daily.loc['2026-06-24'].largest_series_count):,} and "
    f"{int(daily.loc['2026-06-26'].largest_series_count):,}, "
    f"when {int(daily.loc['2026-06-25'].series_zero)} of the 209 series "
    f"read 0 against {int(daily.loc['2026-06-24'].series_zero)} "
    f"and {int(daily.loc['2026-06-26'].series_zero)}",
    AP,
)
context_days = daily.loc[:"2026-06-02"]
assert len(context_days) == 275 and len(daily.loc["2026-06-03":]) == 90
expect(
    "context zeros",
    f"No day of the 275-day context reads 0 for more than {int(context_days.series_zero.max())} "
    "of the 209 series, and the largest series "
    f"never reads below {int(context_days.largest_series_count.min()):,} "
    "there",
    AP,
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
    "changes no conclusion without all three days and one row, E06, without the two panel-wide "
    "days",
    PT,
)
# The order of the sensitivity and addition 6 (review item 23).
assert sens_json["started_at"].startswith("2026-10-16T03:21")
assert "Appended at 2026-10-16 03:28 UTC" in protocol
expect(
    "sensitivity before addition",
    "computed at 03:21 UTC on 2026-10-16 before the addition was written at 03:28 UTC",
    RS,
)
expect("summary: sensitivity", "none of the eighteen conclusions changes", PS)

# --- the post-hoc dynamic-occurrence analysis (reports/study2-posthoc-dynamic-occurrence/) -------
DYN = ROOT / "reports" / "study2-posthoc-dynamic-occurrence"
dn = pd.read_csv(DYN / "npm_inference.csv", **ROUND_TRIP)
ds = pd.read_csv(DYN / "synthetic_inference.csv", **ROUND_TRIP)
assert (
    len(dn) == 24
    and len(ds) == 12
    and dn.declared_count.eq(24).all()
    and ds.declared_count.eq(12).all()
)
assert (
    dn.n_entities.eq(209).all() and ds.n_entities.eq(30).all() and (dn.status == "post-hoc").all()
)
assert dn.n_bootstrap.eq(20000).all() and dn.bootstrap_root.eq(20260917).all()


def dyn_ref(reference):
    if reference.endswith("_completed"):
        return "completed"
    if reference.endswith("_hurdle"):
        return "fixed hurdle"
    if reference == "dynamic_count":
        return "dynamic count"
    if reference == "hurdle_count_28":
        return "count hurdle"
    raise ValueError(reference)


def dyn_line(r):
    return (
        f"{r.id} & {LABEL[r.model.split('_')[0]]} & {dyn_ref(r.reference)} & {r.horizon} & "
        f"{g(r.mean_diff)} & "
        f"[{g(r.mean_diff_ci_low)}, {g(r.mean_diff_ci_high)}] & {g(r.median_diff)} & "
        f"{int(r.wins)} / {int(r.ties)} / {int(r.losses)} & {pval(r.wilcoxon_p_bh)} \\\\"
    )


for df in (dn, ds):
    for r in df.itertuples():
        main_table = r.reference.endswith("_completed") or r.reference.endswith("_hurdle")
        expect(f"dynamic row {r.id}", dyn_line(r), AP)
        assert main_table or not main_table
d_comp = dn[dn.reference.str.endswith("_completed")]
d_fix = dn[dn.reference.str.endswith("_hurdle")]
d_dyn = dn[dn.reference == "dynamic_count"]
d_hk = dn[dn.reference == "hurdle_count_28"]
s_comp = ds[ds.reference.str.endswith("_completed")]
s_fix = ds[ds.reference.str.endswith("_hurdle")]
s_dyn = ds[ds.reference == "dynamic_count"]
s_hk = ds[ds.reference == "hurdle_count_28"]
# Four of the five registered rejections against the substitution are gone; the fifth (S05, now
# DS09) stays.
assert not d_comp.reject_bh_005.any() and (d_comp.mean_diff > 0).all()
assert s_comp[s_comp.reject_bh_005].id.tolist() == ["DS09"] and (s_comp.mean_diff > 0).all()
assert int(hc.reject_bh_005.sum()) + int(sc.reject_bh_005.sum()) == 5
expect("dynamic: four of five", "removes four of the five rejections against the substitution", RS)
expect(
    "dynamic: npm vs completed p",
    f"no npm row rejects, with adjusted $p$ from {g(d_comp.wilcoxon_p_bh.min(), 3)} to "
    f"{g(d_comp.wilcoxon_p_bh.max(), 3)}",
    AP,
)
expect(
    "dynamic: npm vs completed means",
    f"{g(d_comp.mean_diff.min())} to {g(d_comp.mean_diff.max())} against "
    f"{g(hc.mean_diff.min())} to {g(hc.mean_diff.max())} for the registered hurdle",
    AP,
)
de01, de05 = (d_comp[d_comp.id == i].iloc[0] for i in ("DE01", "DE05"))
assert de01.larger_sum_favors == de05.larger_sum_favors == "model"
assert (d_comp[~d_comp.id.isin(["DE01", "DE05"])].larger_sum_favors == "reference").all()
expect(
    "dynamic: chronos leans", f"lower on {int(de01.wins)} and {int(de05.wins)} of 209 series", AP
)
ds01, ds05, ds09 = (s_comp[s_comp.id == i].iloc[0] for i in ("DS01", "DS05", "DS09"))
assert ds01.wilcoxon_p_bh == ds05.wilcoxon_p_bh and not ds01.reject_bh_005 and ds09.reject_bh_005
assert ((s_comp.mean_diff_ci_low < 0) & (s_comp.mean_diff_ci_high > 0)).all()
expect(
    "dynamic: grid vs completed",
    f"(DS01 and DS05, adjusted $p$ {g(ds01.wilcoxon_p_bh, 3)}) and the third, TimesFM 2.5 "
    f"(DS09, adjusted $p$ {g(ds09.wilcoxon_p_bh, 3)})",
    AP,
)
expect(
    "dynamic: grid vs completed means",
    f"the means are {g(s_comp.mean_diff.min())} to {g(s_comp.mean_diff.max())} against "
    f"{g(sc.mean_diff.min())} to {g(sc.mean_diff.max())} registered",
    AP,
)
d_fix30 = d_fix[d_fix.horizon == 30]
d_fix7 = d_fix[d_fix.horizon == 7]
assert (
    d_fix30.reject_bh_005.all() and (d_fix30.mean_diff < 0).all() and not d_fix7.reject_bh_005.any()
)
expect(
    "dynamic: vs fixed npm",
    f"lower on {d_fix30.wins.min()} to {d_fix30.wins.max()} of 209 series",
    AP,
)
assert (
    s_fix.reject_bh_005.all()
    and s_fix.wilcoxon_p_bh.nunique() == 1
    and sorted(s_fix.wins.unique()) == [20, 21]
)
expect(
    "dynamic: vs fixed grid",
    f"lower in 20 or 21 of 30 blocks (adjusted $p$ {g(s_fix.wilcoxon_p_bh.iloc[0], 3)})",
    AP,
)
assert d_dyn.reject_bh_005.all() and (d_dyn.mean_diff < 0).all()
assert s_dyn.reject_bh_005.all() and (s_dyn.mean_diff > 0).all()
expect(
    "dynamic: vs dynamic count grid",
    f"\\texttt{{dynamic\\_count}} being lower in {int(s_dyn.losses.min())} to "
    f"{int(s_dyn.losses.max())} of 30 blocks",
    AP,
)
assert d_hk.reject_bh_005.all() and (d_hk.mean_diff < 0).all() and not s_hk.reject_bh_005.any()
expect(
    "dynamic: vs count hurdle",
    "against \\hc{} all six npm rows reject in the wrapper's favor and on the grid none of the "
    "three rejects",
    AP,
)
dyn_acc = pd.read_csv(DYN / "synthetic_accounting.csv", **ROUND_TRIP).set_index("model")
for r in dyn_acc.reset_index().itertuples():
    expect(
        f"dynamic parts row {r.model}",
        f"{esc(r.model)} & {g(r.qscore9)} & {g(r.zero)} & {g(r.positive_over)} & "
        f"{g(r.positive_under)} \\\\",
        AP,
    )
wrap = [dyn_acc.loc[f"{m}_dyn"] for m in MODELS]
compl = [dyn_acc.loc[f"{m}_completed"] for m in MODELS]
assert min(r.zero for r in wrap) == dyn_acc.zero.min()
expect(
    "dynamic: zero parts",
    f"lowest zero-day part of every forecaster, {g(min(r.zero for r in wrap))} to "
    f"{g(max(r.zero for r in wrap))}",
    AP,
)
expect(
    "dynamic: under parts",
    f"stays at {g(min(r.positive_under for r in wrap))} to "
    f"{g(max(r.positive_under for r in wrap))} against "
    f"{g(min(r.positive_under for r in compl))} to {g(max(r.positive_under for r in compl))} "
    f"for the completed controls and {g(dyn_acc.loc['dynamic_count'].positive_under)} for "
    "\\texttt{dynamic\\_count}",
    AP,
)
dyn_prov = load(DYN / "provenance.json")
assert dyn_prov["head"].startswith("ff8c5e8") and dyn_prov["uncommitted_changes"] == ""
assert dyn_prov["started_at"].startswith("2026-10-16T05:29") and dyn_prov["written_at"].startswith(
    "2026-10-16T05:37"
)
expect("dynamic: head", "from 05:29 to 05:37 UTC at HEAD \\texttt{ff8c5e8}", PT)
occ = pd.read_csv(DYN / "npm_occurrence.csv", **ROUND_TRIP)
socc = pd.read_csv(DYN / "synthetic_occurrence.csv", **ROUND_TRIP)
npm_all = occ[(occ.stratum == "all") & (occ.horizon == 7)].iloc[0]
grid_all = socc[(socc.cell_id == "all") & (socc.horizon == 30)].iloc[0]
assert int(npm_all.windows) == 627 and int(grid_all.windows) == 1620
expect(
    "dynamic: fallback windows",
    f"in {int(npm_all.occurrence_fallback_windows)} of the {int(npm_all.windows):,} npm windows "
    "at each horizon and "
    f"{int(grid_all.occurrence_fallback_windows)} of the {int(grid_all.windows):,} grid windows",
    AP,
)

# --- the new citations of 2026-10-16: keys cited, entries present, identifiers in the record ---
referee = (ROOT / "docs" / "research" / "2026-10-16-standing-and-referee-read.md").read_text(
    encoding="utf-8"
)
cited_paper = set()
for group in re.findall(r"\\cite[pt]?\{([^}]*)\}", TEXT["paper.tex"]):
    cited_paper.update(k.strip() for k in group.split(","))
checks += 1
missing = sorted(cited_paper - bib_keys)
if missing:
    failures.append(f"paper.tex cites keys absent from references.bib: {missing}")
checks += 1
uncited = sorted(
    bib_keys - cited_paper - set(re.findall(r"\\cite[pt]?\{([^}]*)\}", TEXT["main.tex"]))
)
for key, marker in [
    ("adler2025", "2510.16060"),
    ("wen2026", "2608.17299"),
    ("corani2026", "2606.24715"),
    ("brini2026", "2607.05291"),
    ("cherif2026", "2607.19383"),
    ("li2026", "2605.26161"),
    ("qiao2026", "2602.12147"),
    ("ebrahim2026zenodo", "10.5281/zenodo.22681072"),
    ("npm-community-150808", "discussions/150808"),
]:
    checks += 1
    assert key in cited_paper, key
    if marker not in referee or marker not in bib:
        failures.append(
            f"citation {key}: identifier {marker} not in both the referee's read and the bib"
        )
    checks += 1
    if "read" not in bib.split(f"@misc{{{key},")[1].split("}\n\n")[0]:
        failures.append(f"citation {key}: the entry does not record a read date")
expect("design: pins date", "pinned on 2026-09-12", D + PT)
assert "pinned 2026-09-12" in bib
try:
    git_all = subprocess.run(
        ["git", "-C", str(ROOT), "log", "--format=%h %s", "-n", "200"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
except (OSError, subprocess.CalledProcessError):
    skipped.append("git log unavailable; the commit 1c09ac8 of addition 6 not confirmed")
else:
    checks += 1
    if not any(line.startswith("1c09ac8") for line in git_all.splitlines()):
        failures.append("git log: commit 1c09ac8 (the dated addition of 2026-10-16) not found")
expect("design: addition 6 commit", "\\texttt{1c09ac8}", D)

# --- the report still expands to its committed text, apart from the one dated sentence --------
# and one layout line (added 2026-10-19): \sloppy after \begin{document}, so that the hashes and
# paths of the frozen text stay inside the margin. No word of the report changes.
REPORT_LAYOUT_OLD = "\\begin{document}\n\\maketitle\n"
REPORT_LAYOUT_NEW = "\\begin{document}\n\\sloppy\n\\maketitle\n"
REPORT_SENTENCE_OLD = (
    "Benjamini-Hochberg correction. As of 2026-10-12, a statement to be re-checked on the posting "
    "day, no Study 2\ntarget value, forecast or score exists; nothing is claimed about its outcome."
)
REPORT_SENTENCE_NEW = (
    "Benjamini-Hochberg correction. As of 2026-10-12 no Study 2 target value, forecast or score "
    "existed; both\ncomponents fixed for the October 2026 paper, the synthetic grid and the npm "
    "external run, ran on 2026-10-15\nand are reported in the paper that extends this report. "
    "Nothing is claimed here about their outcome."
)
try:
    committed_report = subprocess.run(
        ["git", "-C", str(ROOT), "show", "f325a67:paper/main.tex"],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    ).stdout
except (OSError, subprocess.CalledProcessError):
    skipped.append("git show unavailable; the report's expansion against f325a67 not checked")
else:
    checks += 1
    assert committed_report.count(REPORT_SENTENCE_OLD) == 1
    assert committed_report.count(REPORT_LAYOUT_OLD) == 1
    allowed_report = committed_report.replace(REPORT_SENTENCE_OLD, REPORT_SENTENCE_NEW).replace(
        REPORT_LAYOUT_OLD, REPORT_LAYOUT_NEW
    )
    if expand(MAIN) != allowed_report:
        failures.append(
            "main.tex expanded differs from f325a67:paper/main.tex beyond the one dated sentence "
            "and the \\sloppy line"
        )
expect(
    "report: runs made", "ran on 2026-10-15 and are reported in the paper that extends this report"
)
for run_dir in (SYN_RUN, NPM_RUN):
    assert load(run_dir / "run.json")["started_at"].startswith("2026-10-15")

# --- the abstract: at most 300 words, identical in paper.tex and PAPER-SUMMARY.md --------------
abstract_tex = re.search(
    r"\\begin\{abstract\}(.*?)\\end\{abstract\}", expand(PAPER_TEX), re.S
).group(1)
plain_abstract = re.sub(r"\\texttt\{([^}]*)\}", r"\1", abstract_tex)
plain_abstract = re.sub(r"\$q = 0\.05\$", "q = 0.05", plain_abstract)
plain_abstract = re.sub(r"\s+", " ", plain_abstract).strip()
summary_md = PAPER_SUMMARY.read_text(encoding="utf-8")
summary_abstract = re.search(r"## Abstract\n\n(.*?)\n\n## ", summary_md, re.S).group(1)
summary_abstract = re.sub(r"\s+", " ", summary_abstract).strip()
checks += 1
if plain_abstract != summary_abstract:
    failures.append("the abstract in PAPER-SUMMARY.md differs from the paper's")
checks += 1
if len(plain_abstract.split()) > 300:
    failures.append(f"the abstract has {len(plain_abstract.split())} words, more than 300")

# --- the paper's summary page ------------------------------------------------
expect("summary: npm panel", "209 series", PS + PT)
expect("summary: 540", "540", PS + PT)
expect("summary: twelve", "twelve of the eighteen", PS)
expect("summary: removes four", "removes four of the five rejections", PS)
expect("summary: never beats", "never beats the model's own zero mass", PS)
assert "Study 2, synthetic component" in (ROOT / "RESULTS.md").read_text(encoding="utf-8")

# --- Study 3: the regime family on NYC 311 (added 2026-10-17) ----------------------------------
# The six section files are read like the Study 2 ones. Every figure traces to study/study3/, the
# panel directory, the run directory under reports/study3-nyc311/ or PROTOCOL.md, as sources.md
# lists.
S3_RUN = ROOT / "reports" / "study3-nyc311" / "run-2026-10-17"
S3_PANEL = ROOT / "reports" / "study3-nyc311" / "panel"
S3 = ROOT / "study" / "study3"
S3_FILES = (
    "study3-detail.tex",
    "study3-appendix.tex",
)
for name in S3_FILES:
    TEXT[name] = text(SECTIONS / name)
    expect(f"section {name} in paper.tex", text(SECTIONS / name), PT)
boundary(S3_FILES)
# The Study 3 question, design, panel and results prose is in the paper's body since 2026-10-17.
Q3 = D3 = P3 = R3 = ("paper.tex",)
DET3, AP3 = ("study3-detail.tex",), ("study3-appendix.tex",)
S3LABEL = {"dense": "dense", "sparse": "sparse", "very_sparse": "very sparse"}
S3STRATA = ["dense", "sparse", "very_sparse"]
s3_spec = load(S3 / "spec.json")
s3_fam = load(S3 / "regime_comparisons.json")
s3_prov = load(S3_RUN / "results-provenance.json")
s3_status = load(S3 / "nyc311_panel_status.json")
s3_manifest = load(S3_PANEL / "manifest.json")
s3_run = load(S3_RUN / "run.json")
s3_integ = load(S3_RUN / "integrity" / "integrity.json")
s3_inf_prov = load(S3_RUN / "inference" / "provenance.json")
s3_smoke = load(S3 / "smoke_2026-10-17_00fd91d.json")
s3_results = re.sub(r"\s+", " ", (S3_RUN / "RESULTS-nyc311.md").read_text(encoding="utf-8"))
s3_terms = re.sub(r"\s+", " ", (S3_PANEL / "source-terms.md").read_text(encoding="utf-8"))
protocol_flat = re.sub(r"\s+", " ", protocol)


def in_record(label, needle, record):
    global checks
    checks += 1
    if re.sub(r"\s+", " ", needle) not in record:
        failures.append(f"record: {label}: expected text not found: {needle!r}")


# The registration.
auth = s3_prov["authority"]
assert auth["addition_commit"] == "3357d779db28cffa4048e7e333fd02b9434b4b6d"
assert s3_spec["protocol_sha256"] == auth["addition_protocol_sha256"] == s3_fam["protocol_sha256"]
assert s3_spec["authority"]["appended_on_commit"].startswith("04e92c19")
assert s3_spec["study2_registration"]["protocol_commit"].startswith("df55867")
assert s3_run["metadata"]["metadata"]["authority"]["addition_commit"] == auth["addition_commit"]
expect("s3: addition commit", f"at commit \\texttt{{{auth['addition_commit']}}}", Q3)
expect("s3: addition sha", f"\\texttt{{{auth['addition_protocol_sha256']}}}", Q3)
expect("s3: appended on", "appended on top of commit \\texttt{04e92c1}", Q3)
expect("s3: short commit, summary", "3357d77", PS)
expect("s3: registered date", "registered on 2026-10-16 as item 7", Q3)
assert "### 7. Study 3" in protocol and "Appended at 2026-10-16 06:16 UTC" in protocol
in_record(
    "H3 in the protocol",
    "Hypothesis H3: on series whose context zero fraction is at least 0.5, the substitution with a "
    "dynamic occurrence lowers QScore9 relative to the model's own completed forecast; on "
    "series below "
    "0.5 it raises it. Each stratum is tested on its own; nothing is pooled across strata for "
    "confirmation. Null, adverse, mixed and imprecise results receive the same reporting.",
    protocol_flat,
)
expect(
    "s3: H3",
    "on series whose context zero fraction is at least 0.5, the substitution with a dynamic "
    "occurrence "
    "lowers \\qs{} relative to the model's own completed forecast; on series below 0.5 it "
    "raises it",
    Q3,
)
expect("s3: study 2 registration", "Study 2's registration at \\texttt{df55867}", Q3)
assert s3_spec["domain"]["primary"]["inventory"]["captured_at"].startswith("2026-09-14")
expect("s3: inventory date", "captured on 2026-09-14", Q3 + D3)

# The design.
inv3 = s3_spec["domain"]["primary"]["inventory"]
assert inv3["cells"] == 9496 and inv3["recognized_board_frame"] == 8469
expect(
    "s3: frame",
    f"{inv3['cells']:,} cells captured on 2026-09-14, of which {inv3['recognized_board_frame']:,}",
    D3,
)
st3 = s3_spec["strata"]
assert (
    st3["zero_fraction_window"] == ["2026-03-05", "2026-06-02"]
    and st3["selection_seed"] == 20261001
)
assert st3["context_inspected"] == ["2025-09-01", "2026-06-02"] and st3["per_stratum"] == 100
assert [d["bounds"] for d in st3["definitions"]] == ["[0, 0.5)", "[0.5, 0.9)", "[0.9, 1]"]
expect("s3: stratum window", "2026-03-05 through 2026-06-02", D3)
expect("s3: selection seed", f"selection seed {st3['selection_seed']}", D3)
expect("s3: strata bounds", "$[0, 0.5)$ dense, $[0.5, 0.9)$ sparse, $[0.9, 1]$ very sparse", D3)
expect("s3: context inspected", "2025-09-01 through 2026-06-02", D3)
cal3 = s3_spec["calendar"]
assert cal3["cutoffs"] == ["2026-06-03", "2026-07-03", "2026-08-02"] and cal3["horizons"] == [7, 30]
assert cal3["endpoint"] == "2026-08-31" and cal3["panel_deadline"].startswith("2026-10-27T23:59:59")
assert cal3["context_start"] == "2025-09-01" and cal3["strata_start"] == "2026-03-05"
expect(
    "s3: cutoffs",
    "cutoffs 2026-06-03, 2026-07-03 and 2026-08-02 with 275, 305 and 335 context days",
    D3,
)
expect("s3: horizons", "horizons 7 and 30, endpoint 2026-08-31", D3)
expect("s3: deadline", "2026-10-27", D3 + P3)
expect("s3: deadline full", "2026-10-27 23:59 UTC", DET3)
assert s3_spec["domain"]["fallback"]["name"] == "pypi"
dyn3 = s3_spec["dynamic_count"]
assert dyn3["discount"] == 0.98 and dyn3["initial_parameters"] == [0.5, 0.5, 0.5, 0.5]
expect("s3: discount", "discount 0.98 started at $a_B = b_B = 0.5$", D3)
assert s3_fam["comparison_count"] == 36 and s3_fam["q"] == 0.05
assert s3_fam["bootstrap_replicates"] == 20000 and s3_fam["bootstrap_seed"] == 20261004
assert s3_fam["minimum_complete_series_per_stratum"] == 10 and s3_fam["method"] == "approx"
assert s3_fam["zero_method"] == "wilcox" and s3_fam["all_zero_p"] == 1.0
assert s3_fam["predicted_t1_sign"] == {
    "dense": "positive",
    "sparse": "negative",
    "very_sparse": "negative",
}
expect("s3: 36", "$3 \\times 3 \\times 2 \\times 2 = 36$", D3)
expect("s3: replicates", "20,000 replicates", D3)
expect("s3: bootstrap seed", "bootstrap seed 20261004", D3)
expect("s3: q", "$q = 0.05$ over the 36", D3)
expect("s3: ten", "fewer than ten complete series", D3)
seeds3 = s3_spec["seeds"]
expect(
    "s3: seeds",
    f"selection {seeds3['selection']}, forecasts {seeds3['forecast']}, PIT {seeds3['pit']} and "
    f"bootstrap {seeds3['bootstrap']}",
    DET3,
)
for s in S3STRATA:
    for m in MODELS:
        ids = [c["id"] for c in s3_fam["comparisons"] if c["stratum"] == s and c["model"] == m]
        kinds = [(c["horizon"], c["contrast"]) for c in s3_fam["comparisons"] if c["id"] in ids]
        assert kinds == [(7, "T1"), (7, "T2"), (30, "T1"), (30, "T2")]
        expect(
            f"s3: structure {s} {m}",
            f"{S3LABEL[s]} & {LABEL[m]} & " + " & ".join(ids) + " \\\\",
            D3,
        )

# The panel: the context pull, the strata, the frame.
acq3 = s3_status["acquisition"]
assert acq3["http_attempts"] == 276 and acq3["http_attempts_by_kind"] == {
    "census": 275,
    "metadata": 1,
}
assert acq3["invocations"] == 2 and acq3["anonymous"] and acq3["dollars"] == 0
expect(
    "s3: context attempts",
    f"{acq3['http_attempts']} attempts, {acq3['http_attempts_by_kind']['census']} census days "
    "and one "
    f"metadata read, in two invocations over {round(acq3['seconds_used']):,} seconds",
    P3,
)
appr3 = s3_status["approval"]
assert appr3["http_attempt_ceiling"] == 330 and appr3["invocation_seconds_ceiling"] == 10800
expect("s3: context approval", "330 attempts and 3 hours", P3)
expect("s3: context approval words", appr3["words"].replace("approved: ", ""), AP3)
cen3 = s3_status["census"]
assert cen3["requests"] == 2959469 and cen3["frame_requests"] == 2902433 and cen3["gap_days"] == []
assert cen3["days"] == cen3["pages"] == 275 and cen3["superseded_rows"] == 0
expect(
    "s3: context census",
    f"{cen3['requests']:,} requests, {cen3['frame_requests']:,} of them in frame cells",
    P3,
)
expect(
    "s3: context census detail",
    f"{cen3['days']} days on {cen3['pages']} pages and captured {cen3['requests']:,} requests: "
    f"{cen3['frame_requests']:,} in frame cells, {cen3['unrecognized_requests']:,} with a "
    "missing or "
    f"unrecognized board or problem and {cen3['outside_frame_requests']:,} in recognized cells "
    "outside "
    "the frame",
    DET3,
)
expect(
    "s3: smallest and largest day",
    f"{cen3['smallest_day'][1]:,} requests, on {cen3['smallest_day'][0]}, and the largest "
    f"{cen3['largest_day'][1]:,}, on {cen3['largest_day'][0]}",
    DET3,
)
assert s3_status["panel_verified_at"].startswith("2026-10-16T08:04")
assert s3_status["deadline_met"] and not s3_status["target_values_opened"]
assert s3_status["status"] == "verified_achieved_panel"
expect("s3: frozen", "frozen and verified on 2026-10-16 at 08:04 UTC", P3)
ach3 = s3_status["achieved_strata"]
assert all(ach3[s]["achieved"] == 100 and ach3[s]["unfilled"] == 0 for s in ach3)
assert sum(ach3[s]["complete_candidates"] for s in ach3) == 8469
assert (
    s3_status["frame"]["eligible_frame_size"] == 8469 == s3_status["frame"]["candidate_pool_size"]
)
assert (
    s3_status["frame"]["inventory_size"] == 9496
    and s3_status["frame"]["excluded_at_metadata"] == 1027
)
expect(
    "s3: candidates",
    f"{ach3['dense']['complete_candidates']:,} dense, "
    f"{ach3['sparse']['complete_candidates']:,} sparse "
    f"and {ach3['very_sparse']['complete_candidates']:,} very sparse",
    P3,
)
expect(
    "s3: excluded at metadata",
    "9,496 problem-by-board cells; 1,027 were excluded at metadata",
    DET3,
)
desc3 = s3_status["selected_context_descriptors"]
assert desc3["very_sparse"] == {"context_total_zero": 19, "zero_fraction_one": 39}
assert desc3["dense"] == desc3["sparse"] == {"context_total_zero": 0, "zero_fraction_one": 0}
expect("s3: all-zero", "39 have no request in the 90 stratum days and 19 none", P3)
s3_series = pd.DataFrame(s3_manifest["series"])
assert s3_series.stratum.value_counts().to_dict() == {
    "dense": 100,
    "sparse": 100,
    "very_sparse": 100,
}
assert (
    int((s3_series.zero_fraction == 1).sum()) == 39
    and s3_manifest["report"]["selection_seed"] == 20261001
)
for s, bounds in (
    ("dense", "$[0, 0.5)$"),
    ("sparse", "$[0.5, 0.9)$"),
    ("very_sparse", "$[0.9, 1]$"),
):
    expect(
        f"s3: panel row {s}",
        f"{S3LABEL[s]} & {bounds} & {ach3[s]['complete_candidates']:,} & {ach3[s]['achieved']} & "
        f"{ach3[s]['unfilled']} & {desc3[s]['zero_fraction_one']} & "
        f"{desc3[s]['context_total_zero']} \\\\",
        DET3,
    )
expect("s3: panel row all", "all & & 8,469 & 300 & 0 & 39 & 19 \\\\", DET3)
# The contexts at each origin, from the results page (the signals are not in the tree).
context_rows = [
    ("dense", "2026-06-03", 275, 0, 0, 0),
    ("dense", "2026-07-03", 305, 0, 0, 0),
    ("dense", "2026-08-02", 335, 0, 0, 0),
    ("sparse", "2026-06-03", 275, 0, 1, 4),
    ("sparse", "2026-07-03", 305, 0, 3, 7),
    ("sparse", "2026-08-02", 335, 0, 1, 8),
    ("very_sparse", "2026-06-03", 275, 19, 58, 74),
    ("very_sparse", "2026-07-03", 305, 18, 54, 74),
    ("very_sparse", "2026-08-02", 335, 15, 54, 72),
]
for s, o, days, az, nr, lt in context_rows:
    in_record(
        f"context row {s} {o}",
        f"| {S3LABEL[s]} (n = 100) | {o} | {days} | {az} | {nr} | {lt} |",
        s3_results,
    )
    expect(
        f"s3: context row {s} {o}", f"{S3LABEL[s]} & {o} & {days} & {az} & {nr} & {lt} \\\\", DET3
    )
sp_lt = [r[5] for r in context_rows if r[0] == "sparse"]
vs_lt = [r[5] for r in context_rows if r[0] == "very_sparse"]
vs_nr = [r[4] for r in context_rows if r[0] == "very_sparse"]
vs_az = [r[3] for r in context_rows if r[0] == "very_sparse"]
assert all(r[3] == r[4] == r[5] == 0 for r in context_rows if r[0] == "dense")
expect(
    "s3: fallback at first origin",
    f"{vs_lt[0]} of the 100 very sparse series and {sp_lt[0]} of the 100 sparse series have "
    "fewer than "
    "two request days",
    P3,
)
expect(
    "s3: fallback ranges",
    f"{min(sp_lt)} to {max(sp_lt)} of the 100 sparse series, and {min(vs_lt)} to {max(vs_lt)} "
    "of the "
    f"100 very sparse series, of which {min(vs_nr)} to {max(vs_nr)} have no request day in the "
    "last 28 "
    f"and {min(vs_az)} to {max(vs_az)} none in the whole context",
    DET3,
)

# The target pull.
pull3 = s3_prov["pull"]
pj3 = load(S3_RUN / "target-pull" / "pull.json")
cj3 = load(S3_RUN / "target-pull" / "completeness.json")
assert pull3["attempts"] == 106 and pull3["captures"] == 90 and pj3["complete"]
assert cj3["verified"]
inv0, inv1 = pj3["invocations"]
assert inv0["attempts"] == 100 and inv0["days_exhausted"] == 84
assert inv1["attempts"] == 6 and inv1["days_exhausted"] == 90
assert inv0["started_at"].startswith("2026-10-17T03:16") and inv0["ended_at"].startswith(
    "2026-10-17T03:32"
)
assert inv1["started_at"].startswith("2026-10-17T03:45:06")
assert inv1["ended_at"].startswith("2026-10-17T03:45:43")
assert "120 in all" in s3_prov["readiness"]["approval"][1]["words"]
expect("s3: pull attempts", "106 attempts of an approved 120", P3)
expect("s3: pull first", "100 attempts one second apart exhausted 84 days, 16 of them repeats", P3)
expect("s3: pull second", "6 attempts three seconds apart exhausted the last 6 days", P3)
expect("s3: pull detail", "from 03:16 to 03:32 UTC on 2026-10-17", DET3)
expect("s3: pull detail 2", "100 attempts, 84 days", DET3)
expect("s3: pull detail 3", "the 16 extra attempts", DET3)
expect("s3: pull detail 4", "from 03:45:06 to 03:45:43 UTC: 6 attempts for the last 6 days", DET3)
tc3 = pull3["target_census"]
assert tc3["requests"] == tc3["captured_rows"] == 983482 and tc3["frame_requests"] == 947751
assert tc3["unrecognized_requests"] == 18660 and tc3["outside_frame_requests"] == 17071
assert tc3["gap_days"] == [] and tc3["superseded_rows"] == 0 and tc3["days"] == 90
assert (
    tc3["frame_requests"] + tc3["unrecognized_requests"] + tc3["outside_frame_requests"] == 983482
)
expect(
    "s3: target census",
    f"{tc3['requests']:,} requests, {tc3['frame_requests']:,} in frame cells, "
    f"{tc3['unrecognized_requests']:,} with a missing or unrecognized board or problem and "
    f"{tc3['outside_frame_requests']:,} in recognized cells outside the 2024 frame",
    P3,
)
assert "fewest frame requests 8,849 on 2026-08-16" in pull3["verification"]
expect("s3: fewest", "8,849 on 2026-08-16", P3)
assert (date(2026, 10, 17) - date(2026, 8, 31)).days == 47
expect("s3: 47 days", "47 days after the last target day", P3 + PT)

# The terms and the time basis.
src3 = s3_status["source"]
assert src3["license"] is None and src3["attribution"] == "311" and src3["terms_link"] is None
assert src3["created_date_type"] == "calendar_date"
for label, needle in (
    ("metadata read", "2026-10-16 07:44:21 UTC"),
    ("title", '"311 Service Requests from 2020 to Present"'),
    ("browser read 1", "2026-10-17 04:48:40"),
    ("browser read 2", "2026-10-17 04:49:11"),
    ("terms page", "Terms of Use - nyc.gov"),
    ("silent", "no license, no attribution requirement"),
    ("law not read", "was not read"),
    ("spring forward", "the hour holds 1 request, against 197 and 225"),
    ("fall back", "the hour holds 796 requests, against 528 and 339"),
    ("fewest hour", "on 251 of the 275 days"),
):
    in_record(f"source-terms {label}", needle, s3_terms)
expect("s3: metadata read", "read on 2026-10-16 at 07:44 UTC", DET3)
expect("s3: browser reads", "04:48 and 04:49 UTC", DET3)
expect(
    "s3: dst spring", "2026-03-08, the hour from 02:00 holds 1 request against 197 and 225", DET3
)
expect("s3: dst fall", "2025-11-02, the hour from 01:00 holds 796 against 528 and 339", DET3)
expect("s3: fewest hour", "251 of the 275 context days", DET3)
expect("s3: terms read date", "read on 2026-10-17", P3 + PT)
in_record("checkpoint size", "645 MB", s3_results)
expect("s3: 645 MB", "645 MB", DET3 + PT)

# The run, the integrity check, the gate and the smoke.
inv3r = s3_run["invocations"][0]
assert s3_run["status"] == "complete" and s3_run["failures"] == [] and s3_run["resumes"] == []
assert len(s3_run["invocations"]) == 1 and inv3r["series_completed"] == 300
assert round(inv3r["wall_seconds"]) == 939 and round(s3_prov["run"]["process_seconds"]) == 956
assert s3_run["started_at"].startswith("2026-10-17T03:47")
assert s3_run["completed_at"].startswith("2026-10-17T04:03")
rd3 = s3_run["metadata"]["readiness"]
assert rd3["estimated_seconds"] == 1080 and s3_prov["readiness"]["runtime_budget_seconds"] == 3600
assert rd3["approved_by"] == "Victor Prchlik" and rd3["approved_at"] == "2026-10-17T03:12:50Z"
S3_COMMIT = "00fd91dccfc86b1e4bbd2f0cb44a47052937458d"
assert s3_run["metadata"]["metadata"]["implementation_commit"] == S3_COMMIT
assert s3_prov["implementation_commit"] == S3_COMMIT == s3_smoke["implementation_commit"]
assert s3_inf_prov["implementation_commit_at_inference"] == S3_COMMIT
assert s3_integ["implementation_commit_at_check"] == S3_COMMIT
expect("s3: implementation commit", f"\\texttt{{{S3_COMMIT}}}", DET3)
hw3 = s3_run["metadata"]["hardware"]
assert hw3["gpu_model"] == "NVIDIA GeForce RTX 4070 SUPER" and hw3["gpu_driver"] == "610.88"
assert hw3["cuda_version"] == "12.8" and hw3["pytorch_version"] == "2.11.0+cu128"
assert hw3["batch_size"] == 1 and inv3r["memory"]["peak_reserved_bytes"] == 2948595712
assert s3_smoke["memory"]["peak_reserved_bytes"] == 2948595712
assert s3_prov["smoke"]["at"].startswith("2026-10-17T01:56")
expect("s3: run start 2", "started 2026-10-17 03:47 UTC", AP3)
expect("s3: run end", "at\n04:03 UTC", AP3)
expect("s3: run seconds", "939 seconds inside the run and 956 for the whole process", R3 + AP3)
expect(
    "s3: readiness",
    "approved at 03:12 UTC with a runtime budget of 3,600 seconds against an estimate of 1,080",
    DET3,
)
expect(
    "s3: hardware", "NVIDIA GeForce RTX 4070 SUPER (driver 610.88, CUDA 12.8, PyTorch 2.11.0)", AP3
)
expect("s3: peak", "2,948,595,712 bytes", AP3)
expect(
    "s3: smoke",
    "on 2026-10-17 at 01:56 UTC with a peak reserved memory of 2,948,595,712 bytes",
    DET3,
)
gate3 = s3_prov["gate"]
assert [x["at"][11:16] for x in gate3] == ["03:15", "03:44", "03:46"]
expect(
    "s3: gate",
    "at 03:15 UTC before the first target request, at 03:44 UTC before the pull resumed, and "
    "at 03:46 "
    "UTC before the run",
    DET3,
)
grid3 = s3_integ["grid"]
assert grid3["forecasts"] == 39600 == 300 * 3 * 2 * 22 and len(grid3["models"]) == 22
assert len(s3_spec["variants"]) + 3 == 22
expect(
    "s3: forecasts", "39,600 forecasts (300 series, 3 origins, 2 horizons, 22 variants)", R3 + AP3
)
expect("s3: 22 variants", "all 22 registered variants", D3)
assert s3_integ["status"] == "pass" and s3_integ["failed_forecasts"] == 0
chk3 = s3_integ["checks"]
for key in ("qscore9", "context_scaled_qscore9", "zero", "positive_over", "positive_under"):
    assert chk3[key]["compared"] == 39600 and chk3[key]["disagreements"] == 0, key
assert (
    chk3["occurrence_brier"]["compared"] == 30600 and chk3["occurrence_brier"]["disagreements"] == 0
)
assert (
    chk3["qscore9"]["max_abs_residual"] == 0.0 == chk3["context_scaled_qscore9"]["max_abs_residual"]
)
parts_res = max(chk3[k]["max_abs_residual"] for k in ("zero", "positive_over", "positive_under"))
assert f"{parts_res:.1e}" == "7.1e-15"
assert f"{chk3['occurrence_brier']['max_abs_residual']:.1e}" == "2.8e-16"
assert (
    len(s3_integ["run"]["checkpoint_sha256"]) == 300 == len(s3_inf_prov["run"]["checkpoint_sha256"])
)
expect("s3: 0 disagreements", "0 disagreements", R3 + AP3)
expect(
    "s3: residuals",
    "0.0 for \\qs{} and the scaled score, $7.1 \\times 10^{-15}$ for the parts and "
    "$2.8 \\times 10^{-16}$ for the Brier score",
    AP3,
)
expect("s3: checkpoints", "all 300 checkpoint hashes", AP3)
expect("s3: brier count", "for the 30,600 that carry a count law", AP3)
in_record("structure windows", "on every target day of all 10,800 of their windows", s3_results)
assert 10800 == 300 * 3 * 2 * 6
expect("s3: structure windows", "all 10,800 of their windows", AP3)
s3_scores = pd.read_csv(S3_RUN / "inference" / "secondary_scores.csv", **ROUND_TRIP)
s3_all = s3_scores[s3_scores.stratum == "all"]
assert int(s3_all.crps_certified.sum()) == 30600 == int(s3_all.crps_with_count_distribution.sum())
assert int(s3_all.crps_unavailable_no_count_distribution.sum()) == 9000
assert int(s3_all.crps_unavailable_bound_not_certified.sum()) == 0 and 30600 + 9000 == 39600
expect("s3: crps", "all 30,600 forecasts with a count law; the 9,000 without one", AP3)
assert s3_prov["inference"]["started_at"][11:16] == "04:03"
assert s3_prov["inference"]["ended_at"][11:16] == "04:04"
assert s3_prov["integrity"]["started_at"][11:16] == "04:04"
assert s3_prov["integrity"]["ended_at"][11:16] == "04:05"
expect("s3: inference time", "from 04:03 to 04:04 UTC", AP3)
expect("s3: integrity time", "from 04:04 to 04:05 UTC", AP3)
assert s3_inf_prov["packages"] == {"numpy": "2.5.3", "pandas": "2.3.3", "scipy": "1.18.1"}
assert s3_inf_prov["uncommitted_changes_at_inference"] == ""
assert s3_integ["packages"] == s3_inf_prov["packages"]
expect("s3: packages", "NumPy 2.5.3, SciPy 1.18.1 and pandas 2.3.3", AP3)
for a in s3_prov["readiness"]["approval"]:
    assert a["by"] == "Victor Prchlik"
    expect(f"s3: approval {a['words'][:20]}", a["words"], AP3)
assert s3_prov["readiness"]["approval"][0]["at"] == "2026-10-17T03:12:50Z"
assert s3_prov["readiness"]["approval"][1]["at"] == "2026-10-17T03:43:55Z"
assert s3_prov["readiness"]["approval"][2]["before"] == "2026-10-17T04:48:29Z"

# The family.
s3_inf = pd.read_csv(S3_RUN / "inference" / "inference.csv", **ROUND_TRIP)
assert list(s3_inf.id) == [c["id"] for c in s3_fam["comparisons"]] and len(s3_inf) == 36
assert s3_inf.n_entities.eq(100).all() and s3_inf.declared_count.eq(36).all()
assert s3_inf.bh_count.eq(36).all() and (s3_inf.status == "available").all()
assert s3_inf.n_bootstrap.eq(20000).all() and s3_inf.bootstrap_root.eq(20261004).all()
assert s3_inf.calendar_conditional.all()


def s3_verdict(r):
    return "yes" if r.reject_bh_005 else "no"


def s3_predicted(r):
    if r.contrast == "T2":
        return "--"
    if r.median_diff == 0:
        return "zero"
    return "yes" if r.median_as_predicted else "no"


def s3_row(r):
    return (
        f"{r.id} & {S3LABEL[r.stratum]} & {LABEL[r.model]} & {r.horizon} & {r.contrast} & "
        f"{g(r.variant_mean)} & {g(r.reference_mean)} & {g(r.mean_diff)} & "
        f"[{g(r.mean_diff_ci_low)}, {g(r.mean_diff_ci_high)}] & {g(r.median_diff)} & "
        f"{int(r.wins)} / {int(r.ties)} / {int(r.losses)} & {pval(r.wilcoxon_p_bh)} & "
        f"{s3_verdict(r)} & {s3_predicted(r)} \\\\"
    )


for r in s3_inf.itertuples():
    expect(f"s3 family row {r.id}", s3_row(r), R3)
t1 = s3_inf[s3_inf.contrast == "T1"]
t2 = s3_inf[s3_inf.contrast == "T2"]
rej3 = s3_inf[s3_inf.reject_bh_005]
assert len(rej3) == 21
assert int((rej3.contrast.eq("T1") & rej3.stratum.eq("dense")).sum()) == 6
assert int((rej3.contrast.eq("T1") & rej3.stratum.eq("sparse")).sum()) == 1
assert int((rej3.contrast.eq("T1") & rej3.stratum.eq("very_sparse")).sum()) == 0
assert int(rej3.contrast.eq("T2").sum()) == 14 and (rej3[rej3.contrast == "T2"].mean_diff < 0).all()
for r in t1.itertuples():
    if r.median_diff != 0:
        assert (r.median_diff > 0) == (r.predicted_sign == "positive"), r.id
    if r.reject_bh_005:
        assert r.median_as_predicted, r.id
expect("s3: 21 of 36", "Twenty-one of the\nthirty-six tests reject", R3)
expect("s3: six one fourteen", "six are T1 tests in the dense stratum", R3)
expect("s3: one sparse", "one is a T1 test in the sparse stratum", R3)
expect(
    "s3: fourteen T2",
    "fourteen are T2 tests, all for the dynamic hurdle, three of them with a median of exactly "
    "zero",
    R3,
)
expect("s3: 14 of 18", "14 of the 18 T2 tests reject", R3)
expect("s3: 14 of 18, elsewhere", "14 of 18", PT + PS)
expect("abstract: s3 family", "a per-stratum family of 36 tests", PT + PS)
expect("abstract: s3 panel", "300 NYC 311 series in three strata", PT + PS)
expect("abstract: s3 dense", "all six tests reject as predicted", PT + PS)
expect(
    "abstract: s3 sparse",
    "on the sparse and very sparse strata one of twelve does, and ten of twelve medians are "
    "exactly zero",
    PT + PS,
)
d1, s1, v1 = (t1[t1.stratum == s] for s in S3STRATA)
d2, s2, v2 = (t2[t2.stratum == s] for s in S3STRATA)
assert d1.reject_bh_005.all() and (d1.mean_diff_ci_low > 0).all() and (d1.median_diff > 0).all()
expect(
    "s3: dense higher",
    f"higher than the completed control on {d1.losses.min()} to {d1.losses.max()} of the 100 "
    "series",
    R3,
)
expect(
    "s3: dense medians and means",
    f"the medians run from {g(d1.median_diff.min())} to {g(d1.median_diff.max())} and the "
    "means from "
    f"{g(d1.mean_diff.min())} to {g(d1.mean_diff.max())}",
    R3,
)
assert (
    0.005 < (d1.mean_diff / d1.reference_mean).min()
    and (d1.mean_diff / d1.reference_mean).max() < 0.015
)
# Sparse.
r21, r23 = (s1[s1.id == i].iloc[0] for i in ("R21", "R23"))
assert r21.reject_bh_005 and not r23.reject_bh_005 and r21.median_diff < 0 and r23.median_diff < 0
assert int(s1.reject_bh_005.sum()) == 1 and int((s1.median_diff == 0).sum()) == 4
expect(
    "s3: R21",
    f"R21, TimesFM 2.5 at horizon 7, with a median of {g(r21.median_diff)}, {int(r21.wins)} series "
    f"lower, {int(r21.ties)} tied and {int(r21.losses)} higher, and adjusted $p$ "
    f"{pval(r21.wilcoxon_p_bh)}",
    R3,
)
s1z = s1[s1.median_diff == 0]
expect("s3: sparse zero ties", f"with {s1z.ties.min()} to {s1z.ties.max()} series tied exactly", R3)
# Very sparse.
assert not v1.reject_bh_005.any() and (v1.median_diff == 0).all() and (v1.mean_diff > 0).all()
assert ((v1.mean_diff_ci_low < 0) & (v1.mean_diff_ci_high > 0)).all()
assert v1.loc[v1.wilcoxon_p_bh.idxmin()].id == "R25"
expect("s3: vs ties", f"{v1.ties.min()} to {v1.ties.max()} of the 100 series", R3 + PT)
expect("s3: vs means", f"from {g(v1.mean_diff.min())} to {g(v1.mean_diff.max())}", R3)
expect("s3: vs nonzero", f"{100 - v1.ties.max()} to {100 - v1.ties.min()} series", PT)
s3_desc = pd.read_csv(S3_RUN / "inference" / "family_descriptors.csv", **ROUND_TRIP).set_index("id")
assert (
    s3_desc.loc[list(v1.id)].most_influential_series == '["Sewer Maintenance","09 QUEENS"]'
).all()
assert (
    s3_series[s3_series.series_id == '["Sewer Maintenance","09 QUEENS"]'].stratum.iloc[0]
    == "very_sparse"
)
expect("s3: sewer", "\\texttt{Sewer Maintenance} in community\nboard \\texttt{09 QUEENS}", R3)
expect(
    "s3: sewer, limitations",
    "\\texttt{Sewer Maintenance} in community board\n  \\texttt{09 QUEENS}",
    PT,
)
# T2.
assert d2.reject_bh_005.all() and (d2.median_diff < 0).all()
expect(
    "s3: T2 dense",
    f"lower on {d2.wins.min()} to\n{d2.wins.max()} of the 100 series and medians from "
    f"{g(d2.median_diff.max())} to {g(d2.median_diff.min())}",
    R3,
)
s2r = s2[s2.reject_bh_005]
r14 = s2[s2.id == "R14"].iloc[0]
assert list(s2r.id) == ["R16", "R18", "R20", "R22", "R24"] and r14.median_diff == 0
v2r = v2[v2.reject_bh_005]
v2n = v2[~v2.reject_bh_005]
assert list(v2r.id) == ["R28", "R32", "R36"] and list(v2n.id) == ["R26", "R30", "R34"]
assert (v2r.wins == 22).all() and (v2r.ties == 77).all() and (v2r.losses == 1).all()
assert (v2r.median_diff == 0).all()
expect("s3: T2 very sparse", "each with 22 series lower, 77 tied and 1 higher", R3)
# The direction from the paired table: rank sums and the recomputed raw p.
s3_pe = pd.read_csv(S3_RUN / "inference" / "paired_entities.csv", **ROUND_TRIP)
assert s3_pe.groupby("id").size().eq(100).all()
favors = {}
for r in s3_inf.itertuples():
    d = s3_pe[s3_pe.id == r.id].difference.to_numpy()
    nz = d[d != 0]
    assert len(nz) == r.n_nonzero and int((d == 0).sum()) == r.ties
    assert int((d < 0).sum()) == r.wins and int((d > 0).sum()) == r.losses
    assert abs(d.mean() - r.mean_diff) < 1e-12 and abs(np.median(d) - r.median_diff) < 1e-12
    ranks = stats.rankdata(np.abs(nz))
    lower, higher = float(ranks[nz < 0].sum()), float(ranks[nz > 0].sum())
    favors[r.id] = "hurdle_dynamic" if lower > higher else "reference"
    p_re = float(stats.wilcoxon(nz, method="approx").pvalue) if len(nz) else 1.0
    assert abs(p_re - r.wilcoxon_p) < 1e-9, r.id
    expect(
        f"s3 direction row {r.id}",
        f"{r.id} & {S3LABEL[r.stratum]} & {int(r.ties)} & {int(r.n_nonzero)} & {lower:,.1f} & "
        f"{higher:,.1f} & {esc(favors[r.id])} & {pval(r.wilcoxon_p)} \\\\",
        AP3,
    )
    if r.id in ("R28", "R32", "R36"):
        assert (lower, higher) == (253.0, 23.0)
assert all(favors[i] == "reference" for i in ("R01", "R03", "R05", "R07", "R09", "R11"))
assert (
    all(favors[i] == "hurdle_dynamic" for i in ("R13", "R15", "R17"))
    and favors["R19"] == "reference"
)
assert all(favors[i] == "reference" for i in ("R25", "R29", "R33"))
assert all(favors[i] == "hurdle_dynamic" for i in ("R27", "R31", "R35"))
assert all(favors[i] == "hurdle_dynamic" for i in rej3[rej3.contrast == "T2"].id)
# The ties, classified from the checkpoints when they are present (they are not in the tree).
s3_ckpts = sorted(p for p in S3_RUN.glob("*.json") if len(p.stem) == 64)
if len(s3_ckpts) == 300:
    by_window = {}
    for p in s3_ckpts:
        for row in json.loads(p.read_text(encoding="utf-8"))["rows"]:
            by_window[(row["series_id"], row["model"], row["horizon"], row["cutoff"])] = np.array(
                row["forecast"]["deciles"], dtype=float
            )
    cutoffs3 = cal3["cutoffs"]
    allzero_tied = {}
    for r in t1.itertuples():
        d = s3_pe[s3_pe.id == r.id]
        tied = d[d.difference == 0].series_id
        allzero_tied[r.id] = sum(
            all(
                (by_window[(sid, r.variant, r.horizon, c)] == 0).all()
                and (by_window[(sid, r.reference, r.horizon, c)] == 0).all()
                for c in cutoffs3
            )
            for sid in tied
        )
    vs_az = [allzero_tied[i] for i in v1.id]
    sp_az = [allzero_tied[i] for i in s1.id]
    expect("s3: ties all zero", f"{min(vs_az)} to {max(vs_az)} of the tied series", R3 + PT)
    vs_ids = sorted(set(s3_pe[s3_pe.stratum == "very_sparse"].series_id))
    comp_az, dyn_az = [], []
    for m in MODELS:
        for h in (7, 30):
            comp_az.append(
                sum(
                    all((by_window[(sid, f"{m}_completed", h, c)] == 0).all() for c in cutoffs3)
                    for sid in vs_ids
                )
            )
            dyn_az.append(
                sum(
                    all(
                        (by_window[(sid, f"{m}_hurdle_dynamic", h, c)] == 0).all() for c in cutoffs3
                    )
                    for sid in vs_ids
                )
            )
    assert len(set(dyn_az)) == 1
else:
    skipped.append(
        "the 300 NYC 311 checkpoints are absent; the tie classification was not recomputed"
    )
# The secondary tables: the Brier score, the fixed hurdle and the fourth cell, the pooled rows.
s3_sc = pd.read_csv(S3_RUN / "inference" / "secondary_strata_contrasts.csv", **ROUND_TRIP)
s3_sq = s3_sc[s3_sc.metric == "qscore9"]
s3_sb = s3_sc[s3_sc.metric == "occurrence_brier"]
brier = {}
for r in s3_inf.itertuples():
    b = s3_sb[
        (s3_sb.stratum == r.stratum)
        & (s3_sb.horizon == r.horizon)
        & (s3_sb.variant == r.variant)
        & (s3_sb.reference == r.reference)
    ].iloc[0]
    brier[r.id] = b
    expect(
        f"s3 brier row {r.id}",
        f"{r.id} & {S3LABEL[r.stratum]} & {LABEL[r.model]} & {r.horizon} & {r.contrast} & "
        f"{g(b.mean_diff)} & [{g(b.mean_diff_ci_low)}, {g(b.mean_diff_ci_high)}] & "
        f"{g(b.median_diff)} & "
        f"{int(b.wins)} / {int(b.ties)} / {int(b.losses)} & {pval(b.wilcoxon_p)} \\\\",
        AP3,
    )
bd = pd.DataFrame([brier[i] for i in d1.id])
bv = pd.DataFrame([brier[i] for i in v1.id])
assert (bd.mean_diff_ci_low > 0).all() and (bd.ties == 0).all() and (bv.ties == 0).all()
expect(
    "s3: brier dense",
    f"by {g(bd.mean_diff.min())} to {g(bd.mean_diff.max())} on the mean with every interval "
    "above zero",
    R3,
)
assert (
    (bv.mean_diff_ci_low < 0) & (bv.mean_diff_ci_high > 0)
).all() and bv.mean_diff.abs().max() < 0.0013
assert (bv.median_diff < 0).all()
expect(
    "s3: brier very sparse",
    f"lower Brier score on {int(bv.wins.min())} to {int(bv.wins.max())} of the 100 series in "
    "every T1 "
    f"row, with medians from {g(bv.median_diff.min())} to {g(bv.median_diff.max())} and raw "
    "$p$ at most "
    f"{pval(bv.wilcoxon_p.max())}",
    R3,
)
expect("s3: brier within", "within 0.0013 of zero", R3 + AP3)
expect("s3: brier 68 to 82", f"{int(bv.wins.min())} to {int(bv.wins.max())} of the 100", AP3 + PT)
# The fixed hurdle and the fourth cell against the control per stratum.
fx = s3_sq[s3_sq.variant.str.endswith("_hurdle") & s3_sq.reference.str.endswith("_completed")]
fc = s3_sq[
    s3_sq.variant.str.endswith("occurrence_model_size_count")
    & s3_sq.reference.str.endswith("_completed")
]
for s in S3STRATA:
    for h in (7, 30):
        for m in MODELS:
            for var, name in (
                ("hurdle", "fixed hurdle"),
                ("occurrence_model_size_count", "fourth cell"),
            ):
                r = s3_sq[
                    (s3_sq.stratum == s)
                    & (s3_sq.horizon == h)
                    & (s3_sq.variant == f"{m}_{var}")
                    & (s3_sq.reference == f"{m}_completed")
                ].iloc[0]
                assert r.n_entities == 100 and r.status == "secondary"
                expect(
                    f"s3 variant row {s} {m} {name} {h}",
                    f"{S3LABEL[s]} & {LABEL[m]} & {name} & {h} & {g(r.mean_diff)} & "
                    f"[{g(r.mean_diff_ci_low)}, {g(r.mean_diff_ci_high)}] & {g(r.median_diff)} & "
                    f"{int(r.wins)} / {int(r.ties)} / {int(r.losses)} & {pval(r.wilcoxon_p)} \\\\",
                    AP3,
                )
fxd, fxs, fxv = (fx[fx.stratum == s] for s in S3STRATA)
fcd, fcs, fcv = (fc[fc.stratum == s] for s in S3STRATA)
assert (fxd.mean_diff > 0).all() and (fxv.mean_diff > 0).all()
expect(
    "s3: fourth dense",
    f"mean differences of\n{g(fcd.mean_diff.min())} to {g(fcd.mean_diff.max())} and higher on "
    f"{int(fcd.losses.min())} to {int(fcd.losses.max())} of the 100",
    R3,
)
expect(
    "s3: fourth dense, discussion",
    f"by {g(fcd.mean_diff.min())} to {g(fcd.mean_diff.max())} on the mean",
    PT,
)
assert max(fcs.mean_diff.abs().max(), fcv.mean_diff.abs().max()) < 0.004
fck = s3_sq[
    s3_sq.variant.str.endswith("occurrence_model_size_count")
    & (s3_sq.reference == "hurdle_count_28")
    & (s3_sq.stratum == "dense")
]
assert (fck.mean_diff < 0).all() and len(fck) == 6
expect(
    "s3: fourth vs count hurdle",
    f"lower on the dense series by {g(-fck.mean_diff.max())} to {g(-fck.mean_diff.min())} on "
    "the mean "
    f"and on {int(fck.wins.min())} to {int(fck.wins.max())} of the 100",
    R3,
)
expect(
    "s3: fourth vs count hurdle, discussion",
    f"on {int(fck.wins.min())} to {int(fck.wins.max())} of the 100 dense series",
    PT,
)
# Pooled, in Study 2's form.
pf = pd.read_csv(S3_RUN / "inference" / "secondary_pooled_study2_form.csv", **ROUND_TRIP)
pf = pf[pf.metric == "qscore9"].reset_index(drop=True)
assert (
    len(pf) == 18
    and pf.n_entities.eq(300).all()
    and list(pf.id) == [f"P{i:02d}" for i in range(1, 19)]
)
for r in pf.itertuples():
    expect(
        f"s3 pooled row {r.id}",
        f"{r.id} & {esc(r.variant)} & {esc(r.reference)} & {r.horizon} & {g(r.variant_mean)} & "
        f"{g(r.reference_mean)} & {g(r.mean_diff)} & [{g(r.mean_diff_ci_low)}, "
        f"{g(r.mean_diff_ci_high)}] & "
        f"{g(r.median_diff)} & {int(r.wins)} / {int(r.ties)} / {int(r.losses)} & "
        f"{pval(r.wilcoxon_p_bh_within_table)} \\\\",
        AP3,
    )
pa = pf[pf.reference.str.endswith("_completed")]
pb = pf[pf.reference == "hurdle_count_28"]
pc = pf[pf.reference == "local_mean_28"]
assert (pa.mean_diff > 0).all() and (pa.losses > pa.wins).all()
assert (pb.mean_diff < 0).all() and (pb.wins > pb.losses).all()
assert (pc.mean_diff < 0).all() and pf.wilcoxon_p_bh_within_table.max() < 0.005
expect(
    "s3: pooled raw split",
    f"{int(pc.wins.min())} to {int(pc.wins.max())} lower against {int(pc.losses.min())} to "
    f"{int(pc.losses.max())} higher",
    R3 + PT,
)
expect("s3: pooled bh", "below 0.005", R3)
# The accounting of the T1 difference per stratum.
s3_acc = pd.read_csv(S3_RUN / "inference" / "secondary_accounting.csv", **ROUND_TRIP).set_index(
    ["stratum", "horizon", "model"]
)
zero_dense, parts_vs = [], []
for s in S3STRATA:
    for h in (7, 30):
        for m in MODELS:
            a, b = s3_acc.loc[(s, h, f"{m}_hurdle_dynamic")], s3_acc.loc[(s, h, f"{m}_completed")]
            parts = [
                a.qscore9 - b.qscore9,
                a.zero - b.zero,
                a.positive_over - b.positive_over,
                a.positive_under - b.positive_under,
            ]
            assert abs(parts[0] - sum(parts[1:])) < 1e-9 and a.max_abs_window_residual < 1e-8
            assert abs(a.parts_sum - a.qscore9) < 1e-9
            expect(
                f"s3 parts row {s} {m} {h}",
                f"{S3LABEL[s]} & {LABEL[m]} & {h} & " + " & ".join(g(v) for v in parts) + " \\\\",
                AP3,
            )
            if s == "dense":
                zero_dense.append(parts[1])
            if s == "sparse":
                assert (parts[1] > 0) == (m == "chronos2") and (parts[3] > 0) != (parts[1] > 0)
            if s == "very_sparse":
                parts_vs.extend(abs(v) for v in parts[1:])
assert min(zero_dense) > 0 and max(parts_vs) < 0.006
expect("s3: zero-day dense", f"{g(min(zero_dense))} to {g(max(zero_dense))}", AP3)
expect("s3: very sparse parts", "within 0.006 of zero", AP3)
# The PIT.
s3_pit = pd.read_csv(S3_RUN / "inference" / "pit_histograms.csv", **ROUND_TRIP)
p30 = s3_pit[(s3_pit.horizon == 30) & (s3_pit.status != "unavailable")]
fr = [c for c in s3_pit.columns if c.startswith("fraction")]
shown, last_c, last_d = [], [], []
for s in S3STRATA:
    for m in MODELS:
        for var in ("completed", "hurdle_dynamic"):
            r = p30[(p30.stratum == s) & (p30.model == f"{m}_{var}")].iloc[0]
            assert int(r.n_values) == 9000
            expect(
                f"s3 pit row {s} {m} {var}",
                f"{S3LABEL[s]} & {esc(m + '_' + var)} & "
                + " & ".join(f"{r[c]:.3f}" for c in fr)
                + " \\\\",
                AP3,
            )
            shown.extend(r[c] for c in fr)
            if s == "very_sparse":
                (last_c if var == "completed" else last_d).append(r.fraction10)
expect("s3: pit range", f"{min(shown):.3f} to {max(shown):.3f} of its target\ndays in a tenth", AP3)
expect("s3: pit last tenth", f"{min(last_c):.3f} to {max(last_c):.3f},\nwhere", AP3)
expect(
    "s3: pit last tenth dynamic",
    f"\\emph{{hurdle\\_dynamic}}'s is {min(last_d):.3f} to {max(last_d):.3f}",
    AP3,
)
# The summary page.
expect("summary: s3 run", "956 seconds", PS)
expect("summary: s3 ties", "72 to 88", PS)
expect("summary: s3 reject", "21 of 36", PS)

# --- the paper organized by question (2026-10-17): the body tables, the completion floor, the
# --- secondary scores beside the primary, the post-hoc benchmark's rows, the ledger, the run record
# --- and the length.
# Every figure stated in the body that was not already asserted above is asserted here against the
# file it comes from; the three body tables are regenerated row by row from the saved per-series
# scores, the
# inference tables and the benchmark's contrast tables.
import importlib.util  # noqa: E402

BENCH = ROOT / "reports" / "study2-posthoc-intermittent-baselines"
S3_SERIES = pd.read_csv(S3_RUN / "inference" / "series_scores.csv", **ROUND_TRIP)
s3_strat = (
    S3_SERIES[(S3_SERIES.horizon == 7) & (S3_SERIES.model == "chronos2_raw")]
    .set_index("series_id")
    .stratum
)
FIG = PAPER / "figures" / "make_figures.py"


def pair_of(df, a, b, h, col, s=None, strat=None):
    d = series_paired(df, a, b, h, col)
    if s is not None:
        d = d[strat.loc[d.index] == s]
    return d


def blocks_of(a, b, h, col):
    gg = syn_series[syn_series.horizon == h]
    x = gg[gg.model == a].groupby("replicate")[col].mean()
    y = gg[gg.model == b].groupby("replicate")[col].mean()
    return (x - y).dropna()


def lth(d):
    return f"{int((d < 0).sum())} / {int((d == 0).sum())} / {int((d > 0).sum())}"


def rank_side(d):
    d = np.asarray(d)
    nz = d[d != 0]
    rk = stats.rankdata(np.abs(nz))
    return "model" if rk[nz < 0].sum() > rk[nz > 0].sum() else "reference"


def rng_text(vals):
    lo, hi = min(vals), max(vals)
    return f"{lo}" if lo == hi else f"{lo} to {hi}"


def med_text(meds):
    """Ranges of medians; a median within 1e-9 of zero is floating residue and prints as 0."""
    meds = [0.0 if abs(v) < 1e-9 else v for v in meds]
    lo, hi = g(min(meds)), g(max(meds))
    return lo if lo == hi else f"{lo} to {hi}"


# Table tab:raw: the raw deciles against the local mean on the three natural panels.
for m in MODELS:
    for h in HORIZONS:
        r = lm[(lm.model == m) & (lm.horizon == h)].iloc[0]
        wins = int(round(r.repo_win_rate * r.n_repos))
        assert r.median_diff > 0 and r.reject_bh_005
        expect(
            f"raw table github {m} {h}",
            f"GitHub stars & {LABEL[m]} & {h} & {fmt(r.mean_diff, 3)} & {fmt(r.median_diff, 4)} & "
            f"{wins} of 300 & reference, rejects \\\\",
            PT,
        )
for r in rl.itertuples():
    side = rank_side(paired_npm[paired_npm.id == r.id].difference.to_numpy())
    verdict = "rejects" if r.reject_bh_005 else "no"
    expect(
        f"raw table npm {r.id}",
        f"npm downloads & {LABEL[r.model.split('_')[0]]} & {r.horizon} & {g(r.mean_diff)} & "
        f"{g(r.median_diff)} & {int(r.wins)} / {int(r.ties)} / {int(r.losses)} & {side}, "
        f"{verdict} \\\\",
        PT,
    )
pooled3 = pd.read_csv(S3_RUN / "inference" / "secondary_pooled_study2_form.csv", **ROUND_TRIP)
pq3 = pooled3[(pooled3.reference == "local_mean_28") & (pooled3.metric == "qscore9")]
assert len(pq3) == 6 and (pq3.wilcoxon_p_bh_within_table < 0.005).all()
for m in MODELS:
    for h in (7, 30):
        r = pq3[(pq3.variant == f"{m}_raw") & (pq3.horizon == h)].iloc[0]
        side = rank_side(pair_of(S3_SERIES, f"{m}_raw", "local_mean_28", h, "qscore9").to_numpy())
        assert side == "model" and r.mean_diff < 0
        expect(
            f"raw table nyc311 {m} {h}",
            f"NYC 311 requests & {LABEL[m]} & {h} & {g(r.mean_diff)} & {g(r.median_diff)} & "
            f"{int(r.wins)} / {int(r.ties)} / {int(r.losses)} & model, within-table $p$ "
            f"{pval(r.wilcoxon_p_bh_within_table)} \\\\",
            PT,
        )
expect("raw: pooled lower", f"{int(pq3.wins.min())} to {int(pq3.wins.max())} lower", PT)
expect(
    "raw: pooled higher", f"against {int(pq3.losses.min())} to {int(pq3.losses.max())} higher", PT
)


# Table tab:occ: the substitution against the completed control under the three scores.
def occ_row(stratum, h, name, qd, bd, cd, status, qmed=None):
    return (
        f"{stratum} & {h} & {name} & {lth(qd)} & {g(np.median(qd)) if qmed is None else qmed} & "
        f"{status} & {lth(bd)} & {g(np.median(bd), 3)} & {lth(cd)} & {g(np.median(cd), 3)} \\\\"
    )


brier_sparse7, crps_sparse7, brier_dense7, brier_dense30 = [], [], [], []
for s in ("dense", "sparse"):
    for h in (7, 30):
        for m in MODELS:
            qd = pair_of(npm_series, f"{m}_hurdle", f"{m}_completed", h, "qscore9", s, strat_of)
            bd = pair_of(
                npm_series, f"{m}_hurdle", f"{m}_completed", h, "occurrence_brier", s, strat_of
            )
            cd = pair_of(
                npm_series, f"{m}_hurdle", f"{m}_completed", h, "discrete_crps", s, strat_of
            )
            assert len(qd) == len(bd) == 100 and len(cd) == (99 if s == "dense" else 100)
            expect(
                f"occ table npm {s} {h} {m}", occ_row(s, h, LABEL[m], qd, bd, cd, "secondary"), PT
            )
            if s == "sparse" and h == 7:
                brier_sparse7.append(int((bd < 0).sum()))
                crps_sparse7.append(int((cd < 0).sum()))
            if s == "dense":
                (brier_dense7 if h == 7 else brier_dense30).append(int((bd < 0).sum()))
expect(
    "occ: npm sparse brier h7",
    f"lower on {', '.join(map(str, brier_sparse7[:2]))} and {brier_sparse7[2]} at horizon 7",
    PT,
)
expect(
    "occ: npm sparse crps h7",
    f"on the discrete CRPS on {crps_sparse7[0]}, {crps_sparse7[1]} and {crps_sparse7[2]}",
    PT,
)
assert max(brier_dense7) < 50 < min(brier_dense30)
expect(
    "occ: npm dense brier h30",
    f"lower than the control's on {min(brier_dense30)} to {max(brier_dense30)} of the 100 dense "
    f"series at horizon 30",
    PT,
)
expect(
    "occ: npm dense brier h7",
    f"at horizon 7 it is lower on only {min(brier_dense7)} to {max(brier_dense7)}",
    PT,
)
crps_dense, crps_vs = [], []
for s in S3STRATA:
    for h in (7, 30):
        for m in MODELS:
            rid = s3_inf[
                (s3_inf.stratum == s)
                & (s3_inf.horizon == h)
                & (s3_inf.model == m)
                & (s3_inf.contrast == "T1")
            ].iloc[0]
            qd = pair_of(
                S3_SERIES, f"{m}_hurdle_dynamic", f"{m}_completed", h, "qscore9", s, s3_strat
            )
            assert (int((qd < 0).sum()), int((qd == 0).sum()), int((qd > 0).sum())) == (
                int(rid.wins),
                int(rid.ties),
                int(rid.losses),
            )
            bd = pair_of(
                S3_SERIES,
                f"{m}_hurdle_dynamic",
                f"{m}_completed",
                h,
                "occurrence_brier",
                s,
                s3_strat,
            )
            cd = pair_of(
                S3_SERIES, f"{m}_hurdle_dynamic", f"{m}_completed", h, "discrete_crps", s, s3_strat
            )
            assert len(bd) == len(cd) == 100
            status = f"{rid.id}: " + ("yes" if rid.reject_bh_005 else "no")
            expect(
                f"occ table nyc311 {s} {h} {m}",
                occ_row(S3LABEL[s], h, LABEL[m], qd, bd, cd, status, qmed=g(rid.median_diff)),
                PT,
            )
            if s == "dense":
                crps_dense.append(int((cd > 0).sum()))
            if s == "very_sparse":
                crps_vs.append(int((cd < 0).sum()))
for m in MODELS:
    sid = syn_inf[(syn_inf.model == f"{m}_hurdle") & (syn_inf.reference == f"{m}_completed")].iloc[
        0
    ]
    qd = blocks_of(f"{m}_hurdle", f"{m}_completed", 30, "qscore9")
    assert (int((qd < 0).sum()), int((qd == 0).sum()), int((qd > 0).sum())) == (
        int(sid.wins),
        int(sid.ties),
        int(sid.losses),
    )
    bd = blocks_of(f"{m}_hurdle", f"{m}_completed", 30, "occurrence_brier")
    cd = blocks_of(f"{m}_hurdle", f"{m}_completed", 30, "discrete_crps")
    expect(
        f"occ table grid {m}",
        occ_row(
            "all cells",
            30,
            LABEL[m],
            qd,
            bd,
            cd,
            f"{sid.id}: " + ("yes" if sid.reject_bh_005 else "no"),
            qmed=g(sid.median_diff),
        ),
        PT,
    )
# The grid's very sparse cells: ties and the untied series at a month, and the Brier score there.
ties95, lean95, brier95 = [], [], []
for h in (7, 30):
    for m in MODELS:
        gz = syn_series[
            (syn_series.horizon == h) & (syn_series.cell_id.map(cmeta.zero_probability) == 0.95)
        ]
        a = gz[gz.model == f"{m}_hurdle"].set_index("series_id")
        b = gz[gz.model == f"{m}_completed"].set_index("series_id")
        d = (a.qscore9 - b.qscore9).dropna()
        assert len(d) == 180
        ties95.append(int((d == 0).sum()))
        if h == 30:
            lean95.append(int((d < 0).sum()) > int((d > 0).sum()))
            brier95.append(int(((a.occurrence_brier - b.occurrence_brier).dropna() < 0).sum()))
assert all(lean95) and min(brier95) == 120 and max(brier95) == 139
fixed_sparse7 = [
    int(
        s3_sc[
            (s3_sc.stratum == "sparse") & (s3_sc.variant == f"{m}_hurdle") & (s3_sc.horizon == 7)
        ].wins.iloc[0]
    )
    for m in MODELS
]
expect(
    "occ: fixed hurdle nyc sparse week",
    f"lower on {fixed_sparse7[0]}, {fixed_sparse7[1]} and {fixed_sparse7[2]} of the 100 at "
    f"horizon 7 against 81, 60 and 66 on npm",
    PT,
)


# The post-hoc benchmark: the TSB hurdle's rows against each completed control, and the numbers
# quoted.
def bench(panel):
    return pd.read_csv(BENCH / f"{panel}_contrasts.csv", **ROUND_TRIP)


bench_npm, bench_nyc, bench_grid = bench("npm"), bench("nyc311"), bench("grid")
for df in (bench_npm, bench_nyc, bench_grid):
    assert (df.source == "post hoc").sum() > 0 and df.status.isin(
        ["descriptive", "secondary"]
    ).all()


def tsb_cells(df, group, h, ref, metric):
    r = df[
        (df.variant == "tsb_hurdle")
        & (df.group == group)
        & (df.horizon == h)
        & (df.reference == ref)
        & (df.metric == metric)
    ]
    assert len(r) == 1, (group, h, ref, metric)
    return r.iloc[0]


tsb_dense_npm7, tsb_dense_npm30, tsb_dense_nyc7, tsb_dense_nyc30, tsb_med_npm, tsb_med_nyc = (
    [],
    [],
    [],
    [],
    [],
    [],
)
tsb_sparse_npm7, tsb_vs_ties, tsb_vs_brier = [], [], []
for panel, df, groups, stratum_name in (
    ("npm", bench_npm, ("dense", "sparse"), None),
    ("nyc311", bench_nyc, S3STRATA, None),
    ("grid", bench_grid, ("all",), None),
):
    for s in groups:
        for h in (7, 30) if panel != "grid" else (30,):
            for m in MODELS:
                cells = []
                for met in ("qscore9", "occurrence_brier", "discrete_crps"):
                    r = tsb_cells(df, s, h, f"{m}_completed", met)
                    cells.append(f"{int(r.wins)} / {int(r.ties)} / {int(r.losses)}")
                    cells.append(g(r.median_diff, 3 if met != "qscore9" else 4))
                label = {
                    "all": "all cells",
                    "dense": "dense",
                    "sparse": "sparse",
                    "very_sparse": "very sparse",
                }[s]
                expect(
                    f"occ table tsb {panel} {s} {h} {m}",
                    f"{label} & {h} & TSB vs {LABEL[m]} & {cells[0]} & {cells[1]} & post hoc & "
                    f"{cells[2]} & "
                    f"{cells[3]} & {cells[4]} & {cells[5]} \\\\",
                    PT,
                )
                q = tsb_cells(df, s, h, f"{m}_completed", "qscore9")
                if panel == "npm" and s == "dense":
                    (tsb_dense_npm7 if h == 7 else tsb_dense_npm30).append(int(q.wins))
                    tsb_med_npm.append(float(q.median_diff))
                if panel == "nyc311" and s == "dense":
                    (tsb_dense_nyc7 if h == 7 else tsb_dense_nyc30).append(int(q.wins))
                    tsb_med_nyc.append(float(q.median_diff))
                if panel == "npm" and s == "sparse" and h == 7:
                    tsb_sparse_npm7.append(int(q.wins))
                if panel == "nyc311" and s == "very_sparse":
                    tsb_vs_ties.append(int(q.ties))
                    tsb_vs_brier.append(
                        int(tsb_cells(df, s, h, f"{m}_completed", "occurrence_brier").wins)
                    )
assert sorted(set(tsb_dense_npm7)) == [18, 19]
expect(
    "tsb: sparse npm week",
    f"lower than the completed controls on {tsb_sparse_npm7[0]}, {tsb_sparse_npm7[1]} and "
    f"{tsb_sparse_npm7[2]} of 100 and level with the count hurdle",
    PT,
)
hc_sparse7 = tsb_cells(bench_npm, "sparse", 7, "hurdle_count_28", "qscore9")
expect(
    "tsb: level with count hurdle",
    f"level with the count hurdle, {int(hc_sparse7.wins)} lower against {int(hc_sparse7.losses)} "
    f"higher",
    PT,
)
hc_rows = {
    (panel, s, h): tsb_cells(df, s, h, "hurdle_count_28", "qscore9")
    for panel, df, groups in (
        ("npm", bench_npm, ("dense", "sparse")),
        ("nyc311", bench_nyc, S3STRATA),
        ("grid", bench_grid, ("all",)),
    )
    for s in groups
    for h in (7, 30)
}
assert max(abs(hc_rows[k].median_diff) for k in hc_rows if k[1] == "dense") < 0.032
tsb_dyn = [int(tsb_cells(bench_grid, "all", h, "dynamic_count", "qscore9").losses) for h in (7, 30)]
expect(
    "tsb: vs dynamic count grid",
    f"beaten by the dynamic count on the grid in {tsb_dyn[0]} and {tsb_dyn[1]} of 30 blocks",
    PT,
)
for panel, df, groups in (
    ("npm", bench_npm, ("dense", "sparse")),
    ("NYC 311", bench_nyc, S3STRATA),
    ("grid", bench_grid, ("all",)),
):
    for s in groups:
        for h in (7, 30):
            r = hc_rows[({"npm": "npm", "NYC 311": "nyc311", "grid": "grid"}[panel], s, h)]
            label = {
                "all": "all cells",
                "dense": "dense",
                "sparse": "sparse",
                "very_sparse": "very sparse",
            }[s]
            expect(
                f"pos table tsb {panel} {s} {h}",
                f"{label} & {h} & TSB vs count hurdle & {int(r.n_entities)} & {int(r.wins)} / "
                f"{int(r.ties)} / {int(r.losses)} & {g(r.median_diff)} & post hoc \\\\",
                PT,
            )


# Table tab:pos: the positive-law contrasts as ranges over the three models.
def pos_row(stratum, h, what, ds, status):
    return (
        f"{stratum} & {h} & {what} & {len(ds[0])} & {rng_text([int((d < 0).sum()) for d in ds])} / "
        f"{rng_text([int((d == 0).sum()) for d in ds])} / "
        f"{rng_text([int((d > 0).sum()) for d in ds])} & "
        f"{med_text([float(np.median(d)) for d in ds])} & {status} \\\\"
    )


for h in (7, 30):
    ids = [i for i in hk.id if hk[hk.id == i].horizon.iloc[0] == h]
    ds = [series_paired(npm_series, f"{m}_hurdle", "hurdle_count_28", h) for m in MODELS]
    expect(
        f"pos table npm all {h}",
        pos_row("all", h, "law: model vs Poisson", ds, f"{', '.join(ids)}: 3 reject"),
        PT,
    )
    for s in ("dense", "sparse"):
        expect(
            f"pos table npm poisson {s} {h}",
            pos_row(
                s,
                h,
                "law: model vs Poisson",
                [
                    pair_of(npm_series, f"{m}_hurdle", "hurdle_count_28", h, "qscore9", s, strat_of)
                    for m in MODELS
                ],
                "secondary",
            ),
            PT,
        )
        expect(
            f"pos table npm empirical {s} {h}",
            pos_row(
                s,
                h,
                "law: model vs empirical",
                [
                    pair_of(
                        npm_series, f"{m}_hurdle", "hurdle_empirical_28", h, "qscore9", s, strat_of
                    )
                    for m in MODELS
                ],
                "post hoc",
            ),
            PT,
        )
        expect(
            f"pos table npm dynamic {s} {h}",
            pos_row(
                s,
                h,
                "dynamic count vs control",
                [
                    pair_of(
                        npm_series, "dynamic_count", f"{m}_completed", h, "qscore9", s, strat_of
                    )
                    for m in MODELS
                ],
                "secondary",
            ),
            PT,
        )
expect(
    "pos table grid poisson",
    pos_row(
        "all cells",
        30,
        "law: model vs Poisson",
        [blocks_of(f"{m}_hurdle", "hurdle_count_28", 30, "qscore9") for m in MODELS],
        "S02, S04, S06: 2 reject",
    ),
    PT,
)
expect(
    "pos table grid dynamic",
    pos_row(
        "all cells",
        30,
        "dynamic count vs control",
        [blocks_of("dynamic_count", f"{m}_completed", 30, "qscore9") for m in MODELS],
        "secondary",
    ),
    PT,
)
for s in S3STRATA:
    for h in (7, 30):
        ids = [
            i
            for i in s3_inf.id
            if s3_inf[s3_inf.id == i].stratum.iloc[0] == s
            and s3_inf[s3_inf.id == i].horizon.iloc[0] == h
            and s3_inf[s3_inf.id == i].contrast.iloc[0] == "T2"
        ]
        nrej = int(s3_inf[s3_inf.id.isin(ids)].reject_bh_005.sum())
        ds = [
            pair_of(
                S3_SERIES, f"{m}_hurdle_dynamic", "hurdle_empirical_28", h, "qscore9", s, s3_strat
            )
            for m in MODELS
        ]
        expect(
            f"pos table nyc T2 {s} {h}",
            pos_row(
                S3LABEL[s],
                h,
                "T2: dynamic vs empirical",
                ds,
                f"{', '.join(ids)}: {nrej} reject",
            ),
            PT,
        )
        expect(
            f"pos table nyc empirical {s} {h}",
            pos_row(
                S3LABEL[s],
                h,
                "law: model vs empirical",
                [
                    pair_of(
                        S3_SERIES, f"{m}_hurdle", "hurdle_empirical_28", h, "qscore9", s, s3_strat
                    )
                    for m in MODELS
                ],
                "secondary",
            ),
            PT,
        )
        expect(
            f"pos table nyc fourth {s} {h}",
            pos_row(
                S3LABEL[s],
                h,
                "law: Poisson vs model",
                [
                    pair_of(
                        S3_SERIES,
                        f"{m}_occurrence_model_size_count",
                        f"{m}_completed",
                        h,
                        "qscore9",
                        s,
                        s3_strat,
                    )
                    for m in MODELS
                ],
                "secondary",
            ),
            PT,
        )
        expect(
            f"pos table nyc occurrence {s} {h}",
            pos_row(
                S3LABEL[s],
                h,
                "occurrence: model vs Jeffreys",
                [
                    pair_of(
                        S3_SERIES,
                        f"{m}_occurrence_model_size_count",
                        "hurdle_count_28",
                        h,
                        "qscore9",
                        s,
                        s3_strat,
                    )
                    for m in MODELS
                ],
                "secondary",
            ),
            PT,
        )
        expect(
            f"pos table nyc dynamic {s} {h}",
            pos_row(
                S3LABEL[s],
                h,
                "dynamic count vs control",
                [
                    pair_of(S3_SERIES, "dynamic_count", f"{m}_completed", h, "qscore9", s, s3_strat)
                    for m in MODELS
                ],
                "secondary",
            ),
            PT,
        )


def bench_pos_rows(panel, df, groups, suffix, ref, what):
    out = {}
    for s in groups:
        for h in (7, 30):
            rows = df[
                df.variant.str.endswith(suffix)
                & ((df.reference == ref) if ref else df.reference.str.endswith("_completed"))
                & (df.metric == "qscore9")
                & (df.group == s)
                & (df.horizon == h)
            ]
            assert len(rows) == 3, (panel, s, h, len(rows))
            rows = rows.set_index(rows.variant.str.split("_").str[0]).loc[MODELS]
            label = {"all": "all cells", "dense": "dense", "sparse": "sparse"}[s]
            expect(
                f"pos table {panel} {what} {s} {h}",
                f"{label} & {h} & {what} & {int(rows.n_entities.iloc[0])} & "
                f"{rng_text(rows.wins.astype(int).tolist())} / "
                f"{rng_text(rows.ties.astype(int).tolist())} / "
                f"{rng_text(rows.losses.astype(int).tolist())} & "
                f"{med_text(rows.median_diff.tolist())} & post hoc \\\\",
                PT,
            )
            out[(s, h)] = rows
    return out


f_npm_c = bench_pos_rows(
    "npm",
    bench_npm,
    ("dense", "sparse"),
    "occurrence_model_size_count",
    None,
    "law: Poisson vs model",
)
f_npm_h = bench_pos_rows(
    "npm",
    bench_npm,
    ("dense", "sparse"),
    "occurrence_model_size_count",
    "hurdle_count_28",
    "occurrence: model vs Jeffreys",
)
f_grid_c = bench_pos_rows(
    "grid", bench_grid, ("all",), "occurrence_model_size_count", None, "law: Poisson vs model"
)
f_grid_h = bench_pos_rows(
    "grid",
    bench_grid,
    ("all",),
    "occurrence_model_size_count",
    "hurdle_count_28",
    "occurrence: model vs Jeffreys",
)
dense_losses = [int(v) for h in (7, 30) for v in f_npm_c[("dense", h)].losses]
dense_meds = [float(v) for h in (7, 30) for v in f_npm_c[("dense", h)].median_diff]
expect(
    "fourth: npm dense",
    f"higher than the control on {min(dense_losses)} to {max(dense_losses)} of the 100 dense npm "
    f"series with medians of {min(dense_meds):.2f} to {max(dense_meds):.2f}",
    PT,
)
grid_losses = [int(v) for h in (7, 30) for v in f_grid_c[("all", h)].losses]
expect(
    "fourth: grid", f"higher on {min(grid_losses)} to {max(grid_losses)} of the 30 grid blocks", PT
)
s7 = f_npm_h[("sparse", 7)].wins.astype(int).tolist()


def fourth_brier(df, group, h):
    rows = df[
        df.variant.str.endswith("occurrence_model_size_count")
        & (df.reference == "hurdle_count_28")
        & (df.metric == "occurrence_brier")
        & (df.group == group)
        & (df.horizon == h)
    ]
    return rows.set_index(rows.variant.str.split("_").str[0]).loc[MODELS].wins.astype(int).tolist()


b7, b30, bg7, bg30 = (
    fourth_brier(bench_npm, "dense", 7),
    fourth_brier(bench_npm, "dense", 30),
    fourth_brier(bench_grid, "all", 7),
    fourth_brier(bench_grid, "all", 30),
)
expect(
    "fourth: brier week",
    f"on {b7[0]}, {b7[1]} and {b7[2]} of 100 dense npm series and {bg7[0]}, {bg7[1]} and {bg7[2]} "
    f"of 30 blocks",
    PT,
)
expect(
    "fourth: brier month",
    f"the model's zero mass lower on only {b30[0]}, {b30[1]} and {b30[2]} of 100 and {bg30[0]}, "
    f"{bg30[1]} and {bg30[2]} of 30",
    PT,
)
# The discussion's second-reading numbers: the fixed hurdle against the control at a month.
dense_h30 = [
    int(
        pair_of(npm_series, f"{m}_hurdle", f"{m}_completed", 30, "qscore9", "dense", strat_of)
        .gt(0)
        .sum()
    )
    for m in MODELS
]
grid_h30 = [
    int(blocks_of(f"{m}_hurdle", f"{m}_completed", 30, "qscore9").gt(0).sum()) for m in MODELS
]
assert sorted(set(grid_h30)) == [24, 25]
expect(
    "discussion: second reading",
    f"on {min(dense_h30)} to {max(dense_h30)} of the 100 dense npm series and on 24 or 25 of the "
    f"30 grid blocks",
    PT,
)

# The completion floor, from the 300 NYC 311 checkpoints when they are present (a release asset).
floor_files = sorted(S3_RUN.glob("[0-9a-f]*.json"))
if len(floor_files) == 300:
    floor, every, total, occ_floor, occ_dyn, fallback = {}, {}, {}, {}, {}, {}
    strata_of = {s["series_id"]: s["stratum"] for s in s3_manifest["series"]}
    first_cutoff = min(cal3["cutoffs"])
    for path in floor_files:
        for row in load(path)["rows"]:
            base = next((f for f in MODELS if row["model"].startswith(f + "_")), None)
            variant = row["model"][len(base) + 1 :] if base else None
            if variant not in ("completed", "hurdle_dynamic"):
                continue
            key = (strata_of[row["series_id"]], base)
            laws = row["forecast"]["distributions"]
            law = laws[0]
            if variant == "completed":
                assert (
                    abs(law["tail_scale"] - max(1, law["deciles"][-1] - law["deciles"][-2])) < 1e-9
                )
                on = law["deciles"][-1] < 0.5
                floor[key] = floor.get(key, 0) + on
                every[key] = every.get(key, 0) + all(x["deciles"][-1] < 0.5 for x in laws)
                total[key] = total.get(key, 0) + 1
                if on:
                    occ_floor.setdefault(key, []).append(
                        0.1 * np.exp(-(0.5 - law["deciles"][-1]) / law["tail_scale"])
                    )
            else:
                occ_dyn.setdefault(key, []).append(law["p"])
                if (
                    row["cutoff"] == first_cutoff
                    and row["horizon"] == 7
                    and key[0] == "very_sparse"
                ):
                    fallback.setdefault(key, []).append(law["p"])
    assert all(v == 600 for v in total.values())
    vs_floor = [floor[("very_sparse", m)] for m in MODELS]
    expect(
        "floor: very_sparse",
        f"{vs_floor[0]}, {vs_floor[1]} and {vs_floor[2]} sit on the floor at their first lead",
        PT,
    )
    vs_every = [every[("very_sparse", m)] for m in MODELS]
    expect(
        "floor: every lead", f"and {vs_every[0]}, {vs_every[1]} and {vs_every[2]} at every lead", PT
    )
    sp_floor = [floor[("sparse", m)] for m in MODELS]
    expect(
        "floor: sparse",
        f"{sp_floor[0]}, {sp_floor[1]} and {sp_floor[2]} of 600 do at the first lead",
        PT,
    )
    de_floor = [floor[("dense", m)] for m in MODELS]
    expect("floor: dense", f"dense stratum {de_floor[0]}, {de_floor[1]} and {de_floor[2]}", PT)
    med_floor = [float(np.median(occ_floor[("very_sparse", m)])) for m in MODELS]
    med_dyn = [float(np.median(occ_dyn[("very_sparse", m)])) for m in MODELS]
    assert all(0.06 <= v <= 0.1 for v in med_floor) and max(med_dyn) - min(med_dyn) < 5e-5
    expect(
        "floor: medians",
        f"median occurrence probability of {min(med_floor):.4f} to {max(med_floor):.4f} against "
        f"{med_dyn[0]:.4f} for the dynamic hurdle",
        PT,
    )
    # The dynamic hurdle's median above is the registered fallback: with fewer than two positive
    # days in the last 28 the dynamic count falls back to the count hurdle, whose occurrence is the
    # Jeffreys estimate 0.5/29 (no positive day) or 1.5/29 (one), the same for all three models.
    assert abs(med_dyn[0] - 0.5 / 29) < 5e-5
    fb0 = [sum(abs(p - 0.5 / 29) < 1e-9 for p in fallback[("very_sparse", m)]) for m in MODELS]
    fb1 = [sum(abs(p - 1.5 / 29) < 1e-9 for p in fallback[("very_sparse", m)]) for m in MODELS]
    assert len(set(fb0)) == len(set(fb1)) == 1
    assert all(len(fallback[("very_sparse", m)]) == 100 for m in MODELS)
    expect(
        "floor: fallback",
        f"which {fb0[0]} of the 100 very sparse series take at the first origin",
        PT,
    )
    expect(
        "floor: fallback before the run",
        f"counted {fb0[0] + fb1[0]} of 100 very sparse series on the Jeffreys fallback",
        PT,
    )
    assert abs(0.1 * np.exp(-0.5) - 0.0607) < 5e-5
else:
    skipped.append(
        "the 300 NYC 311 checkpoints are absent (a release asset); the completion-floor counts "
        "not recomputed"
    )
expect("floor: formula", "0.1 e^{-0.5} = 0.0607", PT)

# The signature figure's binned shares, from the figure script's own function.
spec = importlib.util.spec_from_file_location("make_figures", FIG)
mkfig = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mkfig)
npm_z = mkfig.load_scores_with_zero_fraction(
    NPM_RUN / "inference" / "series_scores.csv", NPM / "manifest.json"
)
nyc_z = mkfig.load_scores_with_zero_fraction(
    S3_RUN / "inference" / "series_scores.csv", S3_PANEL / "manifest.json"
)
b_npm = mkfig.binned_shares(npm_z, "hurdle", 7, "qscore9").set_index("low")
b_nyc = mkfig.binned_shares(nyc_z, "hurdle_dynamic", 7, "qscore9").set_index("low")
b_nyc_brier = mkfig.binned_shares(nyc_z, "hurdle_dynamic", 7, "occurrence_brier").set_index("low")
expect(
    "signature: npm bins",
    f"lower on {int(b_npm.loc[0.5].lower)} of {int(b_npm.loc[0.5].n)} and "
    f"{int(b_npm.loc[0.7].lower)} of {int(b_npm.loc[0.7].n)} pairs in the two bins",
    PT,
)
expect(
    "signature: nyc bins",
    f"lower on {int(b_nyc.loc[0.5].lower)} of {int(b_nyc.loc[0.5].n)} and "
    f"{int(b_nyc.loc[0.7].lower)} of {int(b_nyc.loc[0.7].n)} with {int(b_nyc.loc[0.5].tied)} "
    f"and {int(b_nyc.loc[0.7].tied)} tied",
    PT,
)
expect(
    "signature: nyc top bin",
    f"{int(b_nyc.loc[0.97].tied)} of {int(b_nyc.loc[0.97].n)} pairs tie exactly under \\qs{{}} "
    f"while the Brier score favors the substitution on {int(b_nyc_brier.loc[0.97].lower)}",
    PT,
)

# Figure 1, the design at a glance, is typeset in 03-design.tex since 2026-10-20; its numbers are
# asserted against the files its drawing function read: the Study 1 strata and panel summary, the
# npm and NYC 311 panel status files and the grid manifest.
f1_strata = pd.read_csv(REPORT / "evidence" / "panel-diagnostic" / "strata.csv")
f1_s1_frame = int(f1_strata.frame_size.sum())
f1_s1_panel = load(REPORT / "evidence" / "panel" / "panel-summary.json")
f1_npm = load(S2 / "npm_panel_status.json")
f1_npm_strata = f1_npm["achieved_strata"]
f1_nyc = load(S3 / "nyc311_panel_status.json")
f1_grid = load(S2 / "grid_manifest.json")
for label, needle in (
    ("figure 1: GitHub frame", f"frame {f1_s1_frame:,} repositories"),
    ("figure 1: GitHub series", f"{f1_s1_panel['n_accepted']} series & {f1_npm['series']} series"),
    (
        "figure 1: npm inventory",
        f"inventory {f1_npm['inventory']['names']:,} names; hash order to "
        f"{f1_npm['candidate_pool_size']:,} eligible",
    ),
    (
        "figure 1: npm strata",
        f"{f1_npm['series']} series \\mbox{{({f1_npm_strata['dense']['achieved']}, "
        f"{f1_npm_strata['sparse']['achieved']}, {f1_npm_strata['very_sparse']['achieved']})}}",
    ),
    (
        "figure 1: NYC 311 frame",
        f"frame {f1_nyc['frame']['eligible_frame_size']:,} problem-by-board cells, hash order",
    ),
    (
        "figure 1: NYC 311 series",
        f"{sum(v['achieved'] for v in f1_nyc['achieved_strata'].values())} series\\newline 100 per "
        "stratum",
    ),
    (
        "figure 1: grid",
        f"{f1_grid['n_cells']} cells: $z$ in $\\{{0.2, 0.8, 0.95\\}}$, positive mean in "
        f"$\\{{1, 5, 25\\}}$, persistence in $\\{{0, 0.8\\}}$; {f1_grid['replicates_per_cell']} "
        f"replicates per cell, {f1_grid['n_series']} series of {f1_grid['observations']} days; "
        f"origins {', '.join(str(o) for o in f1_grid['origins'])};",
    ),
):
    expect(label, needle, ("03-design.tex",))
checks += 1
if (FIG.parent / "fig-design.pdf").exists() or "fig-design" in TEXT["03-design.tex"]:
    failures.append("figure 1: the drawn fig-design is still in the tree or still included")

# The ledger: dates and commits of the protocol's dated additions, from git.
try:
    ledger_log = subprocess.run(
        ["git", "-C", str(ROOT), "log", "--format=%h %cs", "--", "PROTOCOL.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
except (OSError, subprocess.CalledProcessError):
    skipped.append("git log unavailable; the ledger's commits not confirmed")
else:
    dated = {line.split()[0]: line.split()[1] for line in ledger_log}
    for short, day in (
        ("5f01769", "2026-09-12"),
        ("df55867", "2026-09-14"),
        ("8db0d73", "2026-10-12"),
        ("5be2ce9", "2026-10-15"),
        ("1c09ac8", "2026-10-16"),
        ("3357d77", "2026-10-16"),
    ):
        checks += 1
        if dated.get(short) != day:
            failures.append(
                f"ledger: commit {short} not dated {day} in git log -- PROTOCOL.md: "
                f"{dated.get(short)}"
            )
for row in (
    "Study 1 & 2026-09-12 & \\texttt{5f01769} &",
    "Study 2 & 2026-09-14 & \\texttt{df55867} &",
    "1 & 2026-10-12 & \\texttt{8db0d73} &",
    "5 & 2026-10-15 & \\texttt{5be2ce9} &",
    "6 & 2026-10-16 & \\texttt{1c09ac8} &",
    "7 & 2026-10-16 & \\texttt{3357d77} &",
):
    expect(f"ledger row {row[:8]}", row, PT)
assert "no work was done in this repository between 2026-09-14 and 2026-10-11" in protocol
checks += 1
if TEXT["paper.tex"].count("between 2026-09-14 and 2026-10-11") != 1:
    failures.append(
        "the sentence on the four weeks without work must appear exactly once in the paper"
    )

# The run record table.
s1_run = load(REPORT / "run" / "run.json") if (REPORT / "run" / "run.json").exists() else None
expect(
    "run record github",
    "GitHub stars & 2026-09-13 07:54 & \\texttt{ca67dd2} & 300 & 48,600 & 18,662 &",
    PT,
)
expect(
    "run record grid",
    f"Synthetic grid & 2026-10-15 20:16 & \\texttt{{3fc3411}} & 540 & 55,080 & 1,317 (1,323) & "
    f"2,400 / {syn_run['metadata']['readiness']['estimated_seconds']:,} &",
    PT,
)
expect(
    "run record npm",
    f"npm downloads & 2026-10-15 23:27 & \\texttt{{3057b16}} & 209 & 20,064 & 692 (699) & 3,600 / "
    f"{npm_run['metadata']['readiness']['estimated_seconds']:,} &",
    PT,
)
expect(
    "run record nyc311",
    "NYC 311 requests & 2026-10-17 03:47 & \\texttt{00fd91d} & 300 & 39,600 & 939 (956) & 3,600 / "
    "1,080 &",
    PT,
)
assert round(inv3r["wall_seconds"]) == 939 and S3_COMMIT.startswith("00fd91d")

# The citations added on 2026-10-17: each entry records the page read.
for key in (
    "croston1972",
    "syntetos2005",
    "teunter2011",
    "nikolopoulos2011",
    "svetunkov2023",
    "shenstone2005",
    "snyder2012",
    "kolassa2016",
    "makridakis2022",
    "ziel2022",
    "wang2024",
    "damato2025",
    "tichy2025",
    "woo2024",
    "aksu2024",
    "ghoroghchian2026",
    "musat2026",
    "hyndman2010",
    "preregister2021",
):
    checks += 1
    assert key in cited_paper, key
    entry = bib.split("{" + key + ",")[1].split("}\n\n")[0]
    if "read 2026-10-17" not in entry:
        failures.append(f"citation {key}: the entry does not record the page read on 2026-10-17")

# --- the fixes of 2026-10-18 from the review of the reorganized paper -----------------------
# The rewritten sentences' numbers, each from the saved files. The grid's cells with z = 0.95: the
# fixed hurdle against its control by replicate block under the three scores and by series pair.
S2AP = ("study2-appendix.tex",)
z_of_cell = (
    pd.read_csv(SYN_RUN / "inference" / "secondary_cells.csv", **ROUND_TRIP)
    .drop_duplicates("cell_id")
    .set_index("cell_id")
    .zero_probability
)
syn_z = syn_series.cell_id.map(z_of_cell)


def z_blocks(m, h, col, zp):
    gg = syn_series[(syn_series.horizon == h) & (syn_z == zp)]
    x = gg[gg.model == f"{m}_hurdle"].groupby("replicate")[col].mean()
    y = gg[gg.model == f"{m}_completed"].groupby("replicate")[col].mean()
    return (x - y).dropna()


z95 = {
    col: [int(z_blocks(m, 30, col, 0.95).lt(0).sum()) for m in MODELS]
    for col in ("qscore9", "occurrence_brier", "discrete_crps")
}
z95_7 = [int(z_blocks(m, 7, "qscore9", 0.95).lt(0).sum()) for m in MODELS]
assert all(len(z_blocks(m, 30, "qscore9", 0.95)) == 30 for m in MODELS)
lo95, hi95 = min(min(v) for v in z95.values()), max(max(v) for v in z95.values())
expect("z95: dense paragraph", f"against {lo95} to {hi95} at $z = 0.95$", PT)
expect(
    "z95: appendix blocks",
    f"in {z95['qscore9'][0]}, {z95['qscore9'][1]} and {z95['qscore9'][2]} of the 30 replicate "
    f"blocks under \\qs{{}}, in {z95['occurrence_brier'][0]}, {z95['occurrence_brier'][1]} and "
    f"{z95['occurrence_brier'][2]} under the occurrence Brier score and in "
    f"{z95['discrete_crps'][0]}, {z95['discrete_crps'][1]} and {z95['discrete_crps'][2]} under the "
    "discrete CRPS",
    S2AP,
)
expect(
    "z95: week blocks",
    f"the blocks split {z95_7[0]}, {z95_7[1]} and {z95_7[2]} of 30 under \\qs{{}}",
    S2AP,
)
cell_of_series = syn_series.drop_duplicates("series_id").set_index("series_id").cell_id
pairs95 = pd.concat(
    [pair_of(syn_series, f"{m}_hurdle", f"{m}_completed", 30, "qscore9") for m in MODELS]
)
pairs95 = pairs95[cell_of_series.reindex(pairs95.index).map(z_of_cell).to_numpy() == 0.95]
n_tie, n_low, n_high = (
    int((pairs95 == 0).sum()),
    int((pairs95 < 0).sum()),
    int((pairs95 > 0).sum()),
)
assert n_tie + n_low + n_high == 540 and n_low > n_high
expect(
    "z95: pairs",
    f"ties exactly on {n_tie} and favors the hurdle on {n_low} of the other {n_low + n_high}",
    S2AP,
)
# NYC 311's sparse stratum: its six T1 tests, their rejections and their zero medians.
assert len(s1) == 6 and int(s1.reject_bh_005.sum()) == 1 and int((s1.median_diff == 0).sum()) == 4
expect("sparse T1: introduction", "one registered test of six on NYC 311's sparse stratum", PT)
expect(
    "sparse T1: discussion",
    "one of six T1 tests favors it and four of six medians are exactly zero",
    PT,
)
# Sparse npm at a month: the within-stratum test is null, and Chronos-2's hurdle still wins the
# typical series.
c30 = pair_of(
    npm_series, "chronos2_hurdle", "chronos2_completed", 30, "qscore9", "sparse", strat_of
)
assert int(c30.lt(0).sum()) > 50 and c30.median() < 0
expect("sparse npm month: chronos2", "Chronos-2's hurdle still wins the typical series there", PT)
# The dynamic count is the best forecaster after the oracle at a month only: at a week five model
# variants have a lower mean on the grid.
s7_means = syn_series[syn_series.horizon == 7].groupby("model").qscore9.mean()
assert int((s7_means.drop("oracle") < s7_means.loc["dynamic_count"]).sum()) == 5
expect("dynamic count: week", "at a week five model variants have a lower mean", PT)
# On npm and NYC 311 the dynamic count loses to every completed model on the mean and by count.
for df, n in ((npm_series, 209), (S3_SERIES, 300)):
    for m in MODELS:
        for h in (7, 30):
            d = pair_of(df, "dynamic_count", f"{m}_completed", h, "qscore9")
            assert len(d) == n and d.mean() > 0 and int(d.lt(0).sum()) < n / 2
expect(
    "dynamic count: natural panels",
    "loses to them on npm and NYC 311, on the mean and by count",
    PT,
)
# Table 3's NYC 311 rows: the rank test's side and the medians' signs; P03's median is a value
# shared by several series, not residue.
nyc_med = [
    float(pair_of(S3_SERIES, f"{m}_raw", "local_mean_28", h, "qscore9").median())
    for m in MODELS
    for h in (7, 30)
]
assert (sum(v < 0 for v in nyc_med), sum(v > 0 for v in nyc_med), sum(v == 0 for v in nyc_med)) == (
    3,
    2,
    1,
)
expect("nyc raw: medians", "with three medians below zero, two above and one exactly zero", PT)
p03 = pair_of(S3_SERIES, "chronos2_raw", "local_mean_28", 7, "qscore9")
assert 0 < p03.median() < 1e-8 and int((p03 == p03.median()).sum()) >= 2
expect("median residue", "a near-zero score difference repeated across series, not a tie", S2AP)
# The context-scaled mean on npm (E03 and E15 asserted above: mean below zero, interval across it).
expect(
    "scaled: E03 and E15",
    "still favors the model on npm, with an interval that includes zero in E03 and E15, where the "
    "medians favor the reference",
    PT,
)
# Figure 3 on npm: the first series sets the level; the other 208 move it by less than one percent.
for m in MODELS:
    x = np.sort(pair_of(npm_series, f"{m}_raw", "local_mean_28", 30, "qscore9").to_numpy())
    assert len(x) == 209 and abs(x[0] / len(x) - x.mean()) < 0.01 * abs(x.mean())
expect(
    "figure 3: npm",
    "the first series sets the level and the other 208 move it by less than one percent",
    PT,
)
# The second reading on npm at a month holds on the Brier score, not under the count law.
fc30 = bench_npm[
    bench_npm.variant.str.endswith("occurrence_model_size_count")
    & (bench_npm.reference == "hurdle_count_28")
    & (bench_npm.group == "dense")
    & (bench_npm.horizon == 30)
    & (bench_npm.metric == "qscore9")
].set_index("variant")
fc_w = [int(fc30.loc[f"{m}_occurrence_model_size_count"].wins) for m in MODELS]
assert len(fc30) == 3 and (fc30.mean_diff < 0).all()
expect(
    "two readings: npm under the count law",
    f"lower on {fc_w[0]}, {fc_w[1]} and {fc_w[2]} of the 100 dense series at a month with every "
    "mean in its favor",
    AP3,
)
# The accounting of the raw deciles against the local mean on npm and NYC 311, from the saved
# per-series parts: the parts sum to the score, and the mean of each part over the series.


def part_means(df, col):
    return [
        float(pair_of(df, f"{m}_raw", "local_mean_28", h, col).mean())
        for m in MODELS
        for h in (7, 30)
    ]


PARTS = ("qscore9", "positive_over", "positive_under", "zero")
npm_tot, npm_over, npm_under, npm_zero = (part_means(npm_series, c) for c in PARTS)
assert all(o < u < 0 for o, u in zip(npm_over, npm_under))
npm_zero_bound = int(np.ceil(max(abs(z) for z in npm_zero)))
expect(
    "accounting: npm",
    f"the overprediction part carries {max(npm_over):,.0f} to {min(npm_over):,.0f} of mean gains "
    f"of {max(npm_tot):,.0f} to {min(npm_tot):,.0f}, the underprediction part "
    f"{max(npm_under):,.0f} to {min(npm_under):,.0f} and the zero-day part less than "
    f"{npm_zero_bound} either way",
    AP3,
)
nyc_tot, nyc_over, nyc_under, nyc_zero = (part_means(S3_SERIES, c) for c in PARTS)
assert all(u < z < 0 and u < o < 0 for u, z, o in zip(nyc_under, nyc_zero, nyc_over))
nyc_shares = [z / t for z, t in zip(nyc_zero, nyc_tot)]
pct_lo, pct_hi = int(round(100 * min(nyc_shares))), int(round(100 * max(nyc_shares)))
expect(
    "accounting: nyc311",
    f"underpredicts, {max(nyc_under):.3f} to {min(nyc_under):.3f} of totals of {max(nyc_tot):.3f} "
    f"to {min(nyc_tot):.3f}, with {max(nyc_zero):.3f} to {min(nyc_zero):.3f} on zero days, "
    f"{pct_lo} to {pct_hi} percent of the total, and {max(nyc_over):.3f} to {min(nyc_over):.3f} on "
    "overprediction",
    AP3,
)
expect(
    "accounting: introduction", f"with {pct_lo} to {pct_hi} percent of that gain on zero days", PT
)
expect("accounting: section 4", f"{pct_lo} to {pct_hi} percent of it on zero days", PT)
# The TSB hurdle against the count hurdle on dense series: level on NYC 311, ahead on npm.
tsb_hc_nyc = [
    int(tsb_cells(bench_nyc, "dense", h, "hurdle_count_28", "qscore9").wins) for h in (7, 30)
]
tsb_hc_npm = [
    int(tsb_cells(bench_npm, "dense", h, "hurdle_count_28", "qscore9").wins) for h in (7, 30)
]
assert all(45 <= w <= 55 for w in tsb_hc_nyc) and all(w > 55 for w in tsb_hc_npm)
expect(
    "tsb: dense by panel",
    "level with the count hurdle on dense NYC 311 series and ahead of it on dense npm series",
    PT,
)
# The exclusion of Croston and TSB is by name, without a reason, in the protocol; the TSB hurdle's
# weight and rules are the benchmark specification's.
assert "No PyBATS, Croston, TSB or new GBM is included." in protocol
expect(
    "related work: exclusion", "The protocol excludes Croston and TSB by name without a reason", PT
)
expect("design: TSB analogue", "a discounted Bayesian analogue of TSB \\citep{teunter2011}", PT)
expect(
    "related work: found",
    "No evaluation was found that wraps a frozen model's output in a hurdle under a proper score",
    PT,
)
assert "(a_p, a_z) = (0.1, 0.1)" in (BENCH / "SPEC.md").read_text(encoding="utf-8")
expect("appendix: TSB weight", "with weight 0.1 from their first context values", PT)
# No eaten command. A `\r` read as a carriage return once turned `\ref` into a line break and a
# line that began with `ef{`. Every file under paper/ is free of control bytes other than the line
# feed, no .tex line starts with the remainder of a command, and no line ends with a lone backslash
# before a letter.
EATEN = re.compile(
    r"^(ef|ite[pt]?|extbf|extit|extt|mph|egin|nd|ewcommand|rovidecommand|abel|aption|ulticolumn|"
    r"idrule|oprule|ottomrule|nput|ection|aragraph|ncludegraphics|entering)\{",
    re.M,
)
for p in sorted(PAPER.rglob("*")):
    if p.suffix not in (".tex", ".bib", ".md", ".py") or not p.is_file():
        continue
    checks += 1
    data = p.read_bytes()
    bad = sorted({b for b in data if b < 0x20 and b != 0x0A})
    if bad:
        failures.append(f"{p.relative_to(ROOT).as_posix()}: control bytes {bad}")
    if p.suffix == ".tex":
        tex = data.decode("utf-8")
        for m in EATEN.finditer(tex):
            failures.append(f"{p.relative_to(ROOT).as_posix()}: a line starts with {m.group(0)!r}")
        if re.search(r"(?<!\\)\\\n(?=[A-Za-z])", tex):
            failures.append(
                f"{p.relative_to(ROOT).as_posix()}: a lone backslash before a line break"
            )

# The length, by the revision's method: the running text before \appendix with comments, tables and
# figures removed, and the captions apart. PAPER-SUMMARY.md states the counts.
full = expand(PAPER_TEX)
body_src = full.split("\\appendix")[0]
no_comments = re.sub(r"(?m)^%.*\n", "", body_src)
no_comments = re.sub(r"(?<!\\)%.*", "", no_comments)
floats = [
    m.group(0)
    for m in re.finditer(
        r"\\begin\{(table|figure|sidewaystable)\}.*?\\end\{\1\}", no_comments, re.S
    )
]
captions = []
for f in floats:
    m = re.search(r"\\caption\{(.*)\}\s*\\label", f, re.S)
    captions.append(m.group(1) if m else "")
running = re.sub(
    r"\\begin\{(table|figure|sidewaystable)\}.*?\\end\{\1\}", " ", no_comments, flags=re.S
)
running = re.sub(r"\\begin\{abstract\}.*?\\end\{abstract\}", " ", running, flags=re.S)
running = re.sub(
    r"\\(documentclass|usepackage|newcommand|providecommand|graphicspath|title|author|date|label|input|bibliographystyle|bibliography)(\[[^\]]*\])?\{[^}]*\}(\{[^}]*\})?",
    " ",
    running,
)
running = re.sub(r"\\(section|paragraph)\*?\{", " ", running)
running = re.sub(r"\\[a-zA-Z]+\*?", " ", running)
running = re.sub(r"[{}$\\~]", " ", running)
body_words = len(running.split())
caption_words = len(re.sub(r"\\[a-zA-Z]+\*?|[{}$\\~]", " ", " ".join(captions)).split())
n_tables = sum(
    1 for f in floats if f.startswith("\\begin{table") or f.startswith("\\begin{sidewaystable")
)
n_figures = sum(1 for f in floats if f.startswith("\\begin{figure"))
summary_len = re.search(
    r"the body holds ([\d,]+) words of running text, ([\d,]+) words of captions, (\w+) tables and "
    r"(\w+) figures",
    re.sub(r"\s+", " ", summary_md),
)
checks += 1
if summary_len is None:
    failures.append("PAPER-SUMMARY.md does not state the length by the method")
else:
    stated = int(summary_len.group(1).replace(",", ""))
    if abs(stated - body_words) > 25 or int(summary_len.group(2).replace(",", "")) != caption_words:
        failures.append(
            f"PAPER-SUMMARY.md states {summary_len.group(1)} body words and "
            f"{summary_len.group(2)} of captions; counted {body_words} and {caption_words}"
        )
    words = {"four": 4, "five": 5, "six": 6, "seven": 7}
    if words.get(summary_len.group(3)) != n_tables or words.get(summary_len.group(4)) != n_figures:
        failures.append(
            f"PAPER-SUMMARY.md states {summary_len.group(3)} tables and {summary_len.group(4)} "
            f"figures; counted {n_tables} and {n_figures}"
        )
checks += 1
if body_words > 9000 or n_tables > 5 or n_figures > 4:
    failures.append(
        f"the body has {body_words} words, {n_tables} tables and {n_figures} figures; the ceiling "
        f"is 9,000, five and four"
    )
print(
    f"body: {body_words} words of running text, {caption_words} words of captions, {n_tables} "
    f"tables, {n_figures} figures"
)

# The summary's sentences to read: at most eight, each quoted word for word from the paper (a
# quotation may end at a colon where the paper's sentence continues).
quoted = re.search(r"### Sentences to read\n(.*?)\n## ", summary_md, re.S)
paper_flat = re.sub(r"\s+", " ", full)
quotes = re.findall(r'"([^"]+)"', quoted.group(1)) if quoted else []
for q in quotes:
    checks += 1
    if re.sub(r"\s+", " ", q).strip() not in paper_flat:
        failures.append(f"PAPER-SUMMARY.md quotes a sentence the paper does not hold: {q[:70]!r}")
checks += 1
if not 1 <= len(quotes) <= 8:
    failures.append(f"PAPER-SUMMARY.md quotes {len(quotes)} sentences; one to eight expected")

# --- the data statement (added 2026-10-19) -----------------------------------------------------
# The npm and NYC 311 daily counts are committed beside their panels: each file must exist with the
# byte count and SHA-256 its provenance records, and the paper names it by path. The checkpoints,
# the target signals and Study 1's results file are the release assets of reports/release/ASSETS.md.
ASSETS_MD = ROOT / "reports" / "release" / "ASSETS.md"
assets_md = ASSETS_MD.read_text(encoding="utf-8")
for panel_dir, files in (
    (NPM, (PANEL_DETAIL, "09-reproducibility.tex")),
    (S3_PANEL, ("09-reproducibility.tex",)),
):
    counts_prov = load(panel_dir / "daily_counts.provenance.json")["output"]
    counts_path = ROOT / counts_prov["path"]
    checks += 1
    if counts_path != panel_dir / "daily_counts.csv" or not counts_path.is_file():
        failures.append(
            f"{counts_prov['path']}: the daily counts named by the paper are not in the tree"
        )
    elif counts_path.stat().st_size != counts_prov["bytes"]:
        failures.append(
            f"{counts_prov['path']}: {counts_path.stat().st_size} bytes, its provenance records "
            f"{counts_prov['bytes']}"
        )
    elif hashlib.sha256(counts_path.read_bytes()).hexdigest() != counts_prov["sha256"]:
        failures.append(f"{counts_prov['path']}: its SHA-256 differs from its provenance")
    expect(
        f"data statement: {counts_prov['path']}", f"\\texttt{{{esc(counts_prov['path'])}}}", files
    )
    assert f"`{counts_prov['path']}` | {counts_prov['bytes']:,} |" in assets_md
release_checkpoints = sum(
    len(load(r / "run.json")["completed"]) for r in (SYN_RUN, NPM_RUN, S3_RUN)
)
assert release_checkpoints == 540 + 209 + 300
expect(
    "data statement: release checkpoints",
    f"the {release_checkpoints:,} checkpoints",
    ("09-reproducibility.tex",),
)
expect(
    "data statement: npm checkpoints",
    f"the {len(load(NPM_RUN / 'run.json')['completed'])} checkpoints",
    (PANEL_DETAIL,),
)
for name in (
    "results.parquet",
    "study2-synthetic-2026-10-15-checkpoints.zip",
    "study2-npm-run-2026-10-15-checkpoints.zip",
    "study2-npm-targets-signals.parquet",
    "study3-nyc311-run-2026-10-17-checkpoints.zip",
    "study3-nyc311-targets-signals.parquet",
):
    assert re.search(
        rf"^\| `{re.escape(name)}` \| [\d,]+ \| `[0-9a-f]{{64}}` \|", assets_md, re.M
    ), name
for files in (("09-reproducibility.tex",), (PANEL_DETAIL,)):
    expect("data statement: the asset list", "\\texttt{reports/release/ASSETS.md}", files)
for old in ("are to be released as release assets", "are to be published with the paper"):
    checks += 1
    if old in TEXT["paper.tex"]:
        failures.append(f"paper.tex: the data statement still says the daily counts {old}")

# --- the build (added 2026-10-18) --------------------------------------------------------------
# With a TeX engine on PATH, paper.tex is built from a clean folder under the ignored
# data/cache/build/ (pdflatex, bibtex, then pdflatex until the log asks for no rerun) and its log
# must hold no error, no undefined reference or citation, no overfull box above 5 pt and no float
# taller than the page; the page count must be the one PAPER-SUMMARY.md states. Without an engine
# the check is skipped.
PDFLATEX, BIBTEX = shutil.which("pdflatex"), shutil.which("bibtex")
if PDFLATEX is None or BIBTEX is None:
    skipped.append("pdflatex or bibtex not on PATH; the build of paper.tex was not checked")
else:
    BUILD = ROOT / "data" / "cache" / "build" / "check"
    shutil.rmtree(BUILD, ignore_errors=True)
    BUILD.mkdir(parents=True)
    latex = [
        PDFLATEX,
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"-output-directory={BUILD}",
        "paper.tex",
    ]
    # bibtex runs in the build folder and finds references.bib through BIBINPUTS.
    bib_env = dict(os.environ, BIBINPUTS=str(PAPER) + os.pathsep)
    codes = [subprocess.run(latex, cwd=PAPER, capture_output=True).returncode]
    codes.append(
        subprocess.run([BIBTEX, "paper"], cwd=BUILD, env=bib_env, capture_output=True).returncode
    )
    build_log = ""
    for passes in range(1, 6):
        codes.append(subprocess.run(latex, cwd=PAPER, capture_output=True).returncode)
        raw_log = (BUILD / "paper.log").read_text(encoding="utf-8", errors="replace")
        # TeX wraps its log at 79 characters; a line of exactly 79 continues on the next.
        joined = [""]
        for line in raw_log.split("\n"):
            joined[-1] += line
            if len(line) != 79:
                joined.append("")
        build_log = "\n".join(joined)
        if passes >= 2 and not re.search(r"Rerun to get|Label\(s\) may have changed", build_log):
            break
    checks += 1
    if any(codes):
        failures.append(f"build: a step exited nonzero ({codes}); see {BUILD}")
    errors = re.findall(r"(?m)^(?:! .*|\S+\.tex:\d+: .*)$", build_log)
    undefined = re.findall(
        r"(?:Reference|Citation) `[^']+' on page \d+ undefined|There were undefined \w+", build_log
    )
    overfull = [
        float(a)
        for a in re.findall(r"(?m)^Overfull \\[hv]box \(([\d.]+)pt too (?:wide|high)\)", build_log)
    ]
    too_large = re.findall(r"Float too large for page by ([\d.]+)pt", build_log)
    for label, found in (
        ("errors", errors),
        ("undefined references or citations", undefined),
        ("overfull boxes above 5 pt", [a for a in overfull if a > 5]),
        ("floats taller than the page", too_large),
    ):
        checks += 1
        if found:
            failures.append(f"build: {len(found)} {label}: {found[:3]}")
    pages_built = re.search(r"Output written on .*? \((\d+) pages?", build_log, re.S)
    pages_stated = re.search(
        r"builds with pdfLaTeX to (\d+) pages", re.sub(r"\s+", " ", summary_md)
    )
    checks += 1
    if pages_built is None or pages_stated is None:
        failures.append("build: no page count in the log or none stated in PAPER-SUMMARY.md")
    elif pages_built.group(1) != pages_stated.group(1):
        failures.append(
            f"build: {pages_built.group(1)} pages, PAPER-SUMMARY.md states {pages_stated.group(1)}"
        )
    print(
        f"build: {pages_built.group(1) if pages_built else '?'} pages, {len(overfull)} overfull "
        f"boxes, largest {max(overfull, default=0):.2f} pt, {passes + 1} pdflatex passes"
    )

# --- report -----------------------------------------------------------
for line in failures:
    print("FAIL", line)
for line in skipped:
    print("SKIP", line)
print(f"{checks} checks, {len(failures)} failures, {len(skipped)} skipped")
sys.exit(1 if failures else 0)

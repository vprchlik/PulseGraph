"""Regenerate the results document and descriptive tables from saved forecasts."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.evaluation.reviews import review_scale
from pulsegraph.provenance import atomic_json, read_json

BASE = Path(__file__).resolve().parent
KEY = ["repo_name", "model_name", "horizon", "cutoff_date"]


def macro_table(frame, groups, metric):
    """Average eligible windows within repository, then weight repositories equally."""
    per_repo = frame.groupby(groups + ["repo_name"], as_index=False)[metric].mean()
    values = per_repo.groupby(groups, as_index=False).agg(
        **{metric: (metric, "mean")},
        n_repos=("repo_name", "size"),
        n_valid_repos=(metric, "count"),
    )
    counts = frame.groupby(groups, as_index=False).agg(
        n_windows=("repo_name", "size"), n_valid_windows=(metric, "count")
    )
    return values.merge(counts, on=groups, validate="one_to_one")


def markdown_table(frame, columns):
    def cell(value):
        if pd.isna(value):
            return "NaN"
        if isinstance(value, (float, np.floating)):
            return f"{value:.6g}"
        return str(value)

    return [
        "| " + " | ".join(columns.values()) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
        *[
            "| " + " | ".join(cell(v) for v in row) + " |"
            for row in frame[list(columns)].itertuples(index=False, name=None)
        ],
        "",
    ]


def write_results(base=BASE):
    output = base / "descriptive"
    output.mkdir(exist_ok=True)
    state = read_json(base / "run/run.json")
    execution = read_json(base / "execution-summary.json")
    result_path = base / "run/results.parquet"
    assert file_hash(result_path) == state["artifact_sha256"]["results.parquet"]
    columns = KEY + ["stratum", "qscore9", "coverage_80"]
    scores = pd.read_parquet(result_path, columns=columns)
    assert len(scores) == 48600 and not scores.duplicated(KEY).any()
    assert scores.model_name.nunique() == 18 and scores.repo_name.nunique() == 300
    assert np.isfinite(scores.qscore9).all()
    manifest = pd.DataFrame(read_json(base / "run/manifest.json"))
    scores = scores.merge(
        manifest[["repo_name", "sampling_stratum"]], on="repo_name", validate="many_to_one"
    )
    assert len(scores) == 48600 and scores.sampling_stratum.notna().all()
    scores["regime"] = scores.stratum
    inference = pd.read_csv(base / "inference/inference.csv")
    pairs = pd.read_csv(base / "inference/paired_repositories.csv")
    assert len(inference) == 18
    inference["n_model_lower"] = np.rint(inference.n_repos * inference.repo_win_rate).astype(int)
    for row in inference.itertuples(index=False):
        group = pairs[
            pairs.model.eq(row.model)
            & pairs.reference.eq(row.reference)
            & pairs.horizon.eq(row.horizon)
        ]
        difference = group.model_score - group.reference_score
        assert len(group) == row.n_repos == 300
        assert int((difference < 0).sum()) == row.n_model_lower
        np.testing.assert_allclose(difference.median(), row.median_diff, rtol=1e-10)
        np.testing.assert_allclose((difference < 0).mean(), row.repo_win_rate, rtol=1e-10)
    inference["interval"] = inference.apply(
        lambda r: f"[{r.mean_diff_ci_low:.6g}, {r.mean_diff_ci_high:.6g}]", axis=1
    )
    lines = [
        "# PulseGraph v2 registered results",
        "",
        f"Protocol: {state['protocol_commit']}. Implementation: {state['implementation_commit']}.",
        "",
        "Gate: pass. Run: complete in "
        f"{execution['elapsed_seconds_including_resumes'] / 3600:.4f} hours, including resumes.",
        f"Failures: {len(state['failures'])}. Resumes: {len(state['resumes'])}.",
        "Integrity: pass for the 48,600-row grid and all 300 checkpoint hashes.",
        "",
        "Differences are model minus reference QScore9. Intervals are pointwise 95%",
        "percentile intervals from 20,000 repository-cluster bootstrap replicates.",
        "Raw p-values are two-sided Wilcoxon signed-rank p-values; BH adjustment covers",
        "the declared 18 comparisons. Each comparison includes 300 repositories.",
        "Inference is conditional on the fixed evaluation calendar. Strict wins count",
        "only negative differences; the strict win fraction has all 300 repositories",
        "in its denominator. Median differences and win fractions come from inference.csv;",
        "win counts equal n_repos times that fraction, verified against the paired scores.",
        "",
    ]
    lines += markdown_table(
        inference,
        {
            "model": "Model",
            "reference": "Reference",
            "horizon": "Horizon",
            "mean_diff": "Mean difference",
            "median_diff": "Median difference",
            "n_model_lower": "Model lower (of 300)",
            "repo_win_rate": "Strict win fraction",
            "interval": "95% interval",
            "wilcoxon_p": "Raw p",
            "wilcoxon_p_bh": "BH p",
        },
    )
    lines += [
        "For the descriptive tables, scores are averaged within repository/horizon",
        "before averaging across repositories. Within a regime, only its windows are",
        "averaged for each represented repository. Sampling strata come from the frozen",
        "manifest; regimes are the saved context labels. Window counts count",
        "repository/cutoff/horizon rows for the named model. Horizons are in days.",
        "NaN denotes an undefined statistic; valid denominators are retained in the CSVs.",
        "",
    ]
    saved = []

    def add_table(title, frame, filename, display, declaration):
        path = output / filename
        frame.to_csv(path, index=False)
        saved.append(path)
        lines.extend([f"## {title}", "", declaration, ""])
        lines.extend(markdown_table(frame, display))
        lines.extend(
            [f"[Full precision CSV](reports/registered-2026-09-13/descriptive/{filename}).", ""]
        )

    for reference in ["local_mean_28", "autoets_weekly"]:
        scale = review_scale(scores.assign(stratum="all"), reference=reference, metric="qscore9")
        assert len(scale) == 51 and scale.n_repos.eq(300).all()
        scale["leave_one_out_range"] = scale.apply(
            lambda r: f"[{r.leave_one_out_min_gain:.6g}, {r.leave_one_out_max_gain:.6g}]", axis=1
        )
        add_table(
            f"Scale review against {reference}",
            scale,
            f"scale-{reference}.csv",
            {
                "model_name": "Model",
                "horizon": "Horizon",
                "mean_skill": "Mean skill",
                "median_skill": "Median skill",
                "n_defined_skill": "Defined skill (of 300)",
                "top5_positive_gain_share": "Top-five positive-gain share",
                "leave_one_out_range": "Leave-one-out mean-gain range",
            },
            "This is a declared secondary scale review, not a confirmatory test. "
            "Skill is 1-model/reference, undefined at reference zero; gain is reference-model. "
            "The top-five share divides the five largest positive repository gains by all "
            "positive gains; the range removes each repository in turn from the mean gain.",
        )
    score_display = {
        "model_name": "Model",
        "horizon": "Horizon",
        "n_repos": "Repositories",
        "n_windows": "Windows",
        "qscore9": "Mean QScore9",
    }
    pooled = macro_table(scores, ["model_name", "horizon"], "qscore9")
    assert len(pooled) == 54 and pooled.n_windows.eq(900).all()
    add_table(
        "Pooled QScore9",
        pooled,
        "qscore9-pooled.csv",
        score_display,
        "This is a declared secondary model summary, not a confirmatory test.",
    )
    for column, title in [("sampling_stratum", "sampling stratum"), ("regime", "regime")]:
        table = macro_table(scores, [column, "model_name", "horizon"], "qscore9")
        assert len(table) == 162 and table.n_windows.sum() == 48600
        add_table(
            f"QScore9 by {title}",
            table,
            f"qscore9-{column}.csv",
            {column: title.capitalize(), **score_display},
            f"This is a declared secondary {title} summary, not a confirmatory test.",
        )
    lookbacks = pooled[pooled.model_name.isin([f"local_mean_{n}" for n in [7, 14, 28, 56, 90]])]
    lookbacks = lookbacks.assign(
        lookback=lookbacks.model_name.str.rsplit("_", n=1).str[-1].astype(int)
    )
    lookbacks = lookbacks.sort_values(["lookback", "horizon"])
    add_table(
        "Local-mean lookback grid",
        lookbacks,
        "local-mean-lookbacks.csv",
        {"lookback": "Lookback (days)", **score_display},
        "This is the declared secondary lookback sensitivity table, not a confirmatory test.",
    )
    calibration = macro_table(scores, ["model_name", "horizon"], "coverage_80")
    add_table(
        "Calibration coverage",
        calibration,
        "calibration.csv",
        {
            "model_name": "Model",
            "horizon": "Horizon",
            "coverage_80": "coverage_80",
            "n_valid_repos": "Valid repositories",
            "n_windows": "Windows",
            "n_valid_windows": "Valid windows",
        },
        "This is a declared secondary calibration summary, not a confirmatory test. "
        "coverage_80 is inclusive coverage of the saved repaired 0.1-0.9 quantiles, "
        "averaged within repository and then across repositories.",
    )

    auto = pd.read_parquet(
        result_path,
        columns=KEY + ["quantile_levels", "quantiles", "model_metadata"],
        filters=[("model_name", "==", "autoets_weekly")],
    )
    auto = auto.merge(
        scores[KEY + ["sampling_stratum", "coverage_80"]], on=KEY, validate="one_to_one"
    )
    fit_records = []
    width_records = []
    for row in auto.itertuples(index=False):
        metadata = json.loads(row.model_metadata)
        specification = metadata["selected_specification"]
        levels = np.asarray(row.quantile_levels, dtype=float)
        quantiles = np.vstack(row.quantiles)
        assert quantiles.shape == (row.horizon, len(levels))
        lower = np.flatnonzero(np.isclose(levels, 0.1, rtol=0, atol=1e-12))
        upper = np.flatnonzero(np.isclose(levels, 0.9, rtol=0, atol=1e-12))
        assert len(lower) == len(upper) == 1
        width = quantiles[:, upper[0]] - quantiles[:, lower[0]]
        assert np.isfinite(width).all() and (width >= 0).all()
        fit_records.append(
            {
                "repo_name": row.repo_name,
                "cutoff_date": row.cutoff_date,
                "horizon": row.horizon,
                "sampling_stratum": row.sampling_stratum,
                "coverage_80": row.coverage_80,
                "mean_daily_interval_width_80": width.mean(),
                "median_daily_interval_width_80": np.median(width),
                "selected_method": specification["method"],
                "components": specification["components"],
                "multiplicative_seasonality": specification["components"][2] == "M",
            }
        )
        if row.horizon == 90:
            width_records.append((row.sampling_stratum, width))
    fits = pd.DataFrame(fit_records)
    assert len(fits) == 2700
    fits.to_csv(output / "autoets-fits.csv", index=False)
    saved.append(output / "autoets-fits.csv")
    auto_coverage = macro_table(auto, ["sampling_stratum", "horizon"], "coverage_80")
    specifications = fits.groupby(["sampling_stratum", "horizon"], as_index=False).agg(
        n_fits=("repo_name", "size"),
        multiplicative_seasonality_fits=("multiplicative_seasonality", "sum"),
    )
    auto_coverage = auto_coverage.merge(
        specifications, on=["sampling_stratum", "horizon"], validate="one_to_one"
    )
    add_table(
        "AutoETS interval coverage and specifications",
        auto_coverage,
        "autoets-coverage.csv",
        {
            "sampling_stratum": "Sampling stratum",
            "horizon": "Horizon",
            "coverage_80": "coverage_80",
            "n_valid_windows": "Valid windows",
            "n_fits": "Fits",
            "multiplicative_seasonality_fits": "Multiplicative-seasonality fits",
        },
        "Coverage is a declared secondary calibration summary, not a confirmatory test; "
        "the specification counts are a secondary diagnostic requested after the run. "
        "Each saved repository/cutoff/horizon row is a separate fit.",
    )
    widths = (
        fits[fits.horizon.eq(90)]
        .groupby("sampling_stratum", as_index=False)
        .agg(
            n_fits=("repo_name", "size"),
            median_fit_mean_width_80=("mean_daily_interval_width_80", "median"),
            multiplicative_seasonality_fits=("multiplicative_seasonality", "sum"),
        )
    )
    widths["median_daily_width_80"] = widths.sampling_stratum.map(
        {
            stratum: float(np.median(np.concatenate([w for s, w in width_records if s == stratum])))
            for stratum in widths.sampling_stratum
        }
    )
    widths["n_target_days"] = widths.n_fits * 90
    add_table(
        "AutoETS 90-day interval widths",
        widths,
        "autoets-widths-90.csv",
        {
            "sampling_stratum": "Sampling stratum",
            "n_fits": "90-day fits",
            "n_target_days": "Forecast days",
            "median_daily_width_80": "Median daily 80% width",
            "median_fit_mean_width_80": "Median fit-mean 80% width",
        },
        "This secondary interval-width diagnostic was requested after the run within "
        "the declared secondary calibration analysis; it is not a confirmatory test. "
        "The daily median pools all 90 target days of all fits in the stratum; the "
        "fit-mean median first averages q0.9-q0.1 over each fit's 90 days. "
        "Both use saved intervals after clipping and crossing repair.",
    )
    lines += [
        "[Execution evidence](reports/registered-2026-09-13/execution-summary.json),",
        "[signed readiness](reports/registered-2026-09-13/evidence/readiness.json),",
        "[full inference table](reports/registered-2026-09-13/inference/inference.csv),",
        "[paired scores](reports/registered-2026-09-13/inference/paired_repositories.csv),",
        "[descriptive provenance](reports/registered-2026-09-13/descriptive/provenance.json).",
        "",
        "Regenerate this document and its descriptive CSVs from the saved release asset",
        "without refitting or recomputing confirmatory tests:",
        "",
        "```powershell",
        ".\\.venv\\Scripts\\python.exe reports/registered-2026-09-13/summarize_descriptives.py",
        "```",
        "",
        "Release asset location and SHA-256 are documented in README.md. Raw captures,",
        "weights and duplicate recovery checkpoints are excluded from the tree.",
        "",
    ]
    document = base.parents[1] / "RESULTS.md"
    document.write_text("\n".join(lines), encoding="utf-8")
    atomic_json(
        output / "provenance.json",
        {
            "analysis_status": "declared_secondary",
            "post_run_requested_details": [
                "AutoETS interval widths",
                "AutoETS specification counts",
            ],
            "confirmatory_tests_added": 0,
            "command": (
                ".\\.venv\\Scripts\\python.exe "
                "reports/registered-2026-09-13/summarize_descriptives.py"
            ),
            "protocol_commit": state["protocol_commit"],
            "inputs": {
                name: file_hash(base / name)
                for name in [
                    "run/results.parquet",
                    "run/run.json",
                    "run/manifest.json",
                    "execution-summary.json",
                    "inference/inference.csv",
                    "inference/paired_repositories.csv",
                ]
            },
            "script_sha256": file_hash(Path(__file__)),
            "review_scale_source_sha256": file_hash(
                base.parents[1] / "pulsegraph/evaluation/reviews.py"
            ),
            "outputs": {path.name: file_hash(path) for path in saved},
            "results_document_sha256": file_hash(document),
            "aggregation": "mean within repository/horizon/group, then equal repository mean",
            "rows": {path.name: len(pd.read_csv(path)) for path in saved},
        },
    )
    print(f"Wrote {len(saved)} descriptive CSVs and RESULTS.md; no fits or new tests")


if __name__ == "__main__":
    write_results()

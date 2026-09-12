"""The seven v1 audit concerns, adapted to declared v2 artifact keys.

These routines inspect saved outputs only. They never add a baseline, choose a
winning lookback, change labels, or fit a model after seeing results. CLI review
outputs are explicitly post-hoc until an analysis is registered in the protocol.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from pulsegraph.evaluation.backtest import WINDOW_KEY, summarize_backtest
from pulsegraph.random import derived_seed, validate_seed
from pulsegraph.validation import positive_int


def repository_scores(results: pd.DataFrame, metric: str) -> pd.DataFrame:
    if metric not in results.columns or not np.isfinite(results[metric]).all():
        raise ValueError("Chosen comparison metric must exist and be finite for every row")
    if results.duplicated(WINDOW_KEY + ["model_name"]).any():
        raise ValueError("Duplicate model/window rows")
    return results.groupby(["stratum", "horizon", "repo_name", "model_name"], as_index=False)[
        metric
    ].mean()


def paired_repository_scores(results, *, model: str, reference: str, metric: str):
    if model == reference:
        raise ValueError("Comparison model and reference must differ")
    selected = results[results.model_name.isin([model, reference])]
    if set(selected.model_name) != {model, reference}:
        raise ValueError("Both named models must be present")
    key_sets = [
        set(group[WINDOW_KEY].itertuples(index=False, name=None))
        for _, group in selected.groupby("model_name")
    ]
    if key_sets[0] != key_sets[1]:
        raise ValueError("Paired models must share every window")
    repo = repository_scores(selected, metric)
    wide = repo.pivot(
        index=["stratum", "horizon", "repo_name"], columns="model_name", values=metric
    )
    if wide.isna().any().any():
        raise ValueError("Missing repository-level pairs")
    return wide


def review_scale(results, *, reference: str, metric: str) -> pd.DataFrame:
    rows = []
    for model in sorted(set(results.model_name) - {reference}):
        wide = paired_repository_scores(results, model=model, reference=reference, metric=metric)
        for (stratum, horizon), group in wide.groupby(level=["stratum", "horizon"]):
            gain = group[reference] - group[model]
            positive = gain.clip(lower=0)
            total_positive = positive.sum()
            skill = 1 - group[model] / group[reference].replace(0, np.nan)
            loo = (gain.sum() - gain) / (len(gain) - 1) if len(gain) > 1 else pd.Series(dtype=float)
            rows.append(
                {
                    "stratum": stratum,
                    "horizon": horizon,
                    "model_name": model,
                    "reference": reference,
                    "metric": metric,
                    "n_repos": len(group),
                    "model_macro": group[model].mean(),
                    "reference_macro": group[reference].mean(),
                    "mean_gain": gain.mean(),
                    "median_gain": gain.median(),
                    "repo_win_rate": (gain > 0).mean(),
                    "mean_skill": skill.mean(),
                    "median_skill": skill.median(),
                    "n_defined_skill": int(skill.notna().sum()),
                    "top5_positive_gain_share": positive.nlargest(5).sum() / total_positive
                    if total_positive
                    else np.nan,
                    "leave_one_out_min_gain": loo.min(),
                    "leave_one_out_max_gain": loo.max(),
                }
            )
    if not rows:
        raise ValueError("Scale review needs a reference and at least one comparison model")
    return pd.DataFrame(rows)


def review_windows(results: pd.DataFrame, dataset: dict[str, pd.Series]) -> pd.DataFrame:
    rows = []
    for window in results.drop_duplicates(WINDOW_KEY).itertuples(index=False):
        series = dataset[window.repo_name]
        start, end = window.cutoff_idx, window.cutoff_idx + window.horizon
        target = series.iloc[start:end].to_numpy()
        # Outcome-based descriptors are post-hoc diagnostics only, never forecast-time labels.
        peak = int(np.argmax(series.to_numpy()))
        rows.append(
            {
                "repo_name": window.repo_name,
                "cutoff_date": window.cutoff_date,
                "horizon": window.horizon,
                "stratum": window.stratum,
                "target_end": window.target_end,
                "eval_fraction_zero": np.mean(target == 0),
                "eval_mean": np.mean(target),
                "eval_max": np.max(target),
                "global_peak_date": series.index[peak].date().isoformat(),
                "global_peak_position": "context"
                if peak < start
                else "target"
                if peak < end
                else "after_target",
                "descriptor_scope": "post_hoc_full_observation",
            }
        )
    return pd.DataFrame(rows)


def review_censoring(dataset: dict[str, pd.Series]) -> pd.DataFrame:
    rows = []
    for repo, series in sorted(dataset.items()):
        positive = np.flatnonzero(series.to_numpy() > 0)
        rows.append(
            {
                "repo_name": repo,
                "observation_start": series.index[0].date().isoformat(),
                "observation_end": series.index[-1].date().isoformat(),
                "n_observed_days": len(series),
                "all_zero": not positive.size,
                "leading_zero_days": int(positive[0]) if positive.size else len(series),
                "trailing_zero_days": len(series) - 1 - int(positive[-1])
                if positive.size
                else len(series),
                "zero_days_preserved": int((series == 0).sum()),
            }
        )
    return pd.DataFrame(rows)


def review_strong_baselines(results, *, baseline_names: list[str]) -> pd.DataFrame:
    if not baseline_names or len(set(baseline_names)) != len(baseline_names):
        raise ValueError("Provide distinct baseline names from the original run manifest")
    if not set(baseline_names).issubset(set(results.model_name)):
        raise ValueError("Review cannot add a baseline absent from the saved run")
    return summarize_backtest(results[results.model_name.isin(baseline_names)])


def review_local_mean_lookbacks(results, *, lookbacks: list[int]) -> pd.DataFrame:
    names = [f"local_mean_{positive_int(value, 'lookback')}" for value in lookbacks]
    return review_strong_baselines(results, baseline_names=names)


@dataclass(frozen=True)
class Comparison:
    model: str
    reference: str
    horizon: int
    stratum: str


def benjamini_hochberg(pvalues) -> np.ndarray:
    pvalues = np.asarray(pvalues, dtype=float)
    if pvalues.ndim != 1 or not pvalues.size or not np.isfinite(pvalues).all():
        raise ValueError("Every declared comparison must supply a finite p-value")
    if ((pvalues < 0) | (pvalues > 1)).any():
        raise ValueError("p-values must be in [0, 1]")
    order = np.argsort(pvalues)
    ranked = pvalues[order] * len(pvalues) / np.arange(1, len(pvalues) + 1)
    adjusted = np.empty_like(ranked)
    adjusted[order] = np.minimum(1, np.minimum.accumulate(ranked[::-1])[::-1])
    return adjusted


def review_cluster_inference(
    results,
    *,
    comparisons: list[Comparison],
    declared_count: int,
    metric: str,
    seed: int,
    n_bootstrap: int,
    confidence: float,
) -> pd.DataFrame:
    positive_int(declared_count, "declared_count")
    positive_int(n_bootstrap, "n_bootstrap")
    validate_seed(seed)
    if len(comparisons) != declared_count or len(set(comparisons)) != declared_count:
        raise ValueError("Comparison family must match the declared count without duplicates")
    if not 0 < confidence < 1:
        raise ValueError("Confidence level must be in (0, 1)")
    rows = []
    for comparison in comparisons:
        selected = results[
            results.horizon.eq(comparison.horizon) & results.stratum.eq(comparison.stratum)
        ]
        wide = paired_repository_scores(
            selected, model=comparison.model, reference=comparison.reference, metric=metric
        )
        diff = (wide[comparison.model] - wide[comparison.reference]).to_numpy()
        if len(diff) < 2:
            raise ValueError("Repository-clustered inference requires at least two repositories")
        bootstrap_seed = derived_seed(seed, comparison.__dict__, metric)
        rng = np.random.default_rng(bootstrap_seed)
        means = np.empty(n_bootstrap)
        # Bound memory even for a large panel. Resample repositories, not windows.
        for start in range(0, n_bootstrap, 256):
            stop = min(start + 256, n_bootstrap)
            means[start:stop] = diff[
                rng.integers(0, len(diff), size=(stop - start, len(diff)))
            ].mean(axis=1)
        alpha = 1 - confidence
        pvalue = 1.0 if np.all(diff == 0) else float(stats.wilcoxon(diff, method="approx").pvalue)
        rows.append(
            {
                **comparison.__dict__,
                "metric": metric,
                "n_repos": len(diff),
                "mean_diff": diff.mean(),
                "median_diff": np.median(diff),
                "repo_win_rate": np.mean(diff < 0),
                "mean_diff_ci_low": np.quantile(means, alpha / 2),
                "mean_diff_ci_high": np.quantile(means, 1 - alpha / 2),
                "wilcoxon_p": pvalue,
                "seed": seed,
                "bootstrap_seed": bootstrap_seed,
                "n_bootstrap": n_bootstrap,
                "confidence": confidence,
                "declared_count": declared_count,
            }
        )
    output = pd.DataFrame(rows)
    output["wilcoxon_p_bh"] = benjamini_hochberg(output.wilcoxon_p)
    return output

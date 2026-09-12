"""Explicit common-calendar backtests. Every requested window must succeed."""

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

import numpy as np
import pandas as pd

from pulsegraph.evaluation.metrics import evaluate_forecast
from pulsegraph.forecast.output import ForecastOutput
from pulsegraph.random import derived_seed, validate_seed
from pulsegraph.validation import daily_series, positive_int, utc_day

SCORE_COLUMNS = (
    "crps_mean",
    "mean_pinball_loss",
    "wql",
    "mae",
    "mase",
    "rmsse",
    "coverage_80",
    "coverage_95",
    "interval_score_80",
)
WINDOW_KEY = ["repo_name", "cutoff_date", "horizon"]


class Forecaster(Protocol):
    name: str

    def forecast(self, series, horizon: int, repo_name: str) -> ForecastOutput: ...


@dataclass(frozen=True)
class BacktestConfig:
    horizons: tuple[int, ...]
    cutoffs: tuple[str, ...]  # first forecasted dates; context ends the previous day
    min_context_days: int
    quantile_levels: tuple[float, ...]
    seasonal_period: int
    seed: int

    def __post_init__(self):
        if not self.horizons or not self.cutoffs:
            raise ValueError("Declare horizons and a nonempty cutoff calendar")
        horizons = tuple(positive_int(h, "horizon") for h in self.horizons)
        if tuple(sorted(set(horizons))) != horizons:
            raise ValueError("Horizons must be unique and increasing")
        dates = tuple(utc_day(c) for c in self.cutoffs)
        if any((later - earlier).days < max(horizons) for earlier, later in zip(dates, dates[1:])):
            raise ValueError("Cutoffs must increase with non-overlapping maximum-horizon targets")
        levels = np.asarray(self.quantile_levels, dtype=float)
        if levels.ndim != 1 or not levels.size or not np.isfinite(levels).all():
            raise ValueError("Declare a nonempty common quantile grid")
        if (levels <= 0).any() or (levels >= 1).any() or (np.diff(levels) <= 0).any():
            raise ValueError("Common quantile levels must increase strictly within (0, 1)")
        positive_int(self.min_context_days, "min_context_days")
        positive_int(self.seasonal_period, "seasonal_period")
        validate_seed(self.seed)
        object.__setattr__(self, "horizons", horizons)
        object.__setattr__(self, "cutoffs", tuple(day.date().isoformat() for day in dates))
        object.__setattr__(self, "quantile_levels", tuple(float(q) for q in levels))


def rolling_backtest(
    series: pd.Series,
    forecaster: Forecaster,
    config: BacktestConfig,
    *,
    repo_name: str,
    labeler: Callable[[pd.Series], str] | None = None,
) -> pd.DataFrame:
    daily_series(series)
    rows = []
    for cutoff in config.cutoffs:
        day = utc_day(cutoff)
        idx = int(series.index.searchsorted(day))
        if idx >= len(series) or series.index[idx] != day:
            raise ValueError(f"{repo_name}: cutoff {cutoff} is outside observed dates")
        if idx < config.min_context_days or idx + max(config.horizons) > len(series):
            raise ValueError(f"{repo_name}: incomplete context or target interval at {cutoff}")
        context = series.iloc[:idx].copy(deep=True)
        # Labels have the same information boundary as models. No ingestion-time strata.
        stratum = labeler(context.copy(deep=True)) if labeler else "all"
        if not isinstance(stratum, str) or not stratum:
            raise ValueError("Context labeler must return a nonempty string")
        for horizon in config.horizons:
            actuals = series.iloc[idx : idx + horizon].to_numpy(dtype=float, copy=True)
            forecast = forecaster.forecast(context.copy(deep=True), horizon, repo_name)
            if forecast.model_name != forecaster.name or forecast.repo_name != repo_name:
                raise ValueError("Forecast identity does not match the requested model/repository")
            if not 0 < forecast.context_length <= len(context):
                raise ValueError("Model reported an invalid used context length")
            metric_seed = derived_seed(
                config.seed, "pit", repo_name, cutoff, horizon, forecaster.name
            )
            scores = evaluate_forecast(
                forecast,
                actuals,
                context=context,
                quantile_levels=config.quantile_levels,
                seasonal_period=config.seasonal_period,
                seed=metric_seed,
            )
            rows.append(
                {
                    "repo_name": repo_name,
                    "model_name": forecaster.name,
                    "horizon": horizon,
                    "cutoff_idx": idx,
                    "cutoff_date": cutoff,
                    "context_start": context.index[0].date().isoformat(),
                    "context_end": context.index[-1].date().isoformat(),
                    "target_end": series.index[idx + horizon - 1].date().isoformat(),
                    "observation_end": series.index[-1].date().isoformat(),
                    "context_length": len(context),
                    "model_context_length": forecast.context_length,
                    "stratum": stratum,
                    "context": context.tolist(),
                    "actuals": actuals.tolist(),
                    "quantile_levels": forecast.quantile_levels.tolist(),
                    "quantiles": forecast.quantiles.tolist(),
                    "samples": None if forecast.samples is None else forecast.samples.tolist(),
                    "model_metadata": json.dumps(
                        forecast.metadata, sort_keys=True, allow_nan=False
                    ),
                    **scores,
                }
            )
    return pd.DataFrame(rows)


def run_backtest_suite(
    dataset: dict[str, pd.Series],
    forecasters: dict[str, Forecaster],
    config: BacktestConfig,
    *,
    labeler: Callable[[pd.Series], str] | None = None,
) -> pd.DataFrame:
    if not dataset or not forecasters:
        raise ValueError("A backtest requires repositories and explicitly selected models")
    for series in dataset.values():
        daily_series(series)
    if len({series.index[-1] for series in dataset.values()}) != 1:
        raise ValueError("Every repository must share the observation endpoint")
    if any(name != model.name for name, model in forecasters.items()):
        raise ValueError("Forecaster mapping keys must equal model identities")
    results = []
    for repo_name, series in sorted(dataset.items()):
        for model in forecasters.values():
            results.append(
                rolling_backtest(
                    series,
                    model,
                    config,
                    repo_name=repo_name,
                    labeler=labeler,
                )
            )
    return pd.concat(results, ignore_index=True)


def summarize_backtest(results: pd.DataFrame) -> pd.DataFrame:
    """Window means plus valid-score counts; macro inference is computed separately."""
    if results.empty:
        raise ValueError("Cannot summarize an empty backtest")
    groups = ["model_name", "horizon", "stratum"]
    aggregations = {score: (score, "mean") for score in SCORE_COLUMNS}
    aggregations.update({f"{score}_n_valid": (score, "count") for score in SCORE_COLUMNS})
    aggregations.update(n_windows=("repo_name", "size"), n_repos=("repo_name", "nunique"))
    return results.groupby(groups, as_index=False, dropna=False).agg(**aggregations)

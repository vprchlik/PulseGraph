"""Scores with explicit shapes, quantile support and zero-denominator handling.

Full CRPS and randomized empirical PIT require IID marginal samples. Native
quantiles are scored directly; no extrapolated tails or pseudo-samples are used.
MASE/RMSSE denominators use only context and the caller's seasonal period.
"""

import numpy as np

from pulsegraph.forecast.output import ForecastOutput
from pulsegraph.random import validate_seed
from pulsegraph.validation import counts, positive_int


def _paired(first, second):
    first, second = np.asarray(first, dtype=float), np.asarray(second, dtype=float)
    if first.ndim != 1 or first.shape != second.shape or not first.size:
        raise ValueError("Metric vectors must have identical nonempty one-dimensional shapes")
    return first, second


def crps_empirical(samples: np.ndarray, observation: float) -> float:
    """Fair finite-sample energy estimator, for >=2 IID draws from a distribution."""
    samples = counts(samples, name="samples")
    if len(samples) < 2 or not np.isfinite(observation):
        raise ValueError("Fair CRPS requires at least two draws and a finite observation")
    n = len(samples)
    weights = 2 * np.arange(n) + 1 - n
    dispersion = np.dot(weights, np.sort(samples)) / (n * (n - 1))
    return float(np.mean(np.abs(samples - observation)) - dispersion)


def mae(predicted, actuals) -> float:
    predicted, actuals = _paired(predicted, actuals)
    if not np.isfinite(predicted).all() or not np.isfinite(actuals).all():
        raise ValueError("MAE requires finite values")
    return float(np.mean(np.abs(actuals - predicted)))


def coverage(lower, upper, actuals) -> float:
    lower, upper = _paired(lower, upper)
    _, actuals = _paired(lower, actuals)
    valid = np.isfinite(lower) & np.isfinite(upper) & np.isfinite(actuals)
    if (lower[valid] > upper[valid]).any():
        raise ValueError("Interval bounds are reversed")
    if not valid.any():
        return float("nan")
    return float(np.mean((actuals[valid] >= lower[valid]) & (actuals[valid] <= upper[valid])))


def interval_score(lower, upper, actuals, *, alpha: float) -> float:
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    lower, upper = _paired(lower, upper)
    _, actuals = _paired(lower, actuals)
    if not (np.isfinite(lower) & np.isfinite(upper) & np.isfinite(actuals)).all():
        return float("nan")
    if (lower > upper).any():
        raise ValueError("Interval bounds are reversed")
    score = (
        upper
        - lower
        + (2 / alpha) * (np.maximum(lower - actuals, 0) + np.maximum(actuals - upper, 0))
    )
    return float(score.mean())


def quantile_losses(quantiles, levels, actuals) -> np.ndarray:
    actuals = counts(actuals, name="actuals")
    levels = np.asarray(levels, dtype=float)
    quantiles = np.asarray(quantiles, dtype=float)
    if levels.ndim != 1 or not levels.size or not np.isfinite(levels).all():
        raise ValueError("Quantile levels must be a nonempty finite vector")
    if (levels <= 0).any() or (levels >= 1).any() or (np.diff(levels) <= 0).any():
        raise ValueError("Quantile levels must increase strictly within (0, 1)")
    if quantiles.shape != (len(actuals), len(levels)) or not np.isfinite(quantiles).all():
        raise ValueError("All requested quantiles must be supported for every target day")
    error = actuals[:, None] - quantiles
    return np.maximum(levels * error, (levels - 1) * error)


def weighted_quantile_loss(quantiles, levels, actuals) -> float:
    """Mean across levels of 2*sum_t pinball / sum_t |actual|; NaN if all zero."""
    losses = quantile_losses(quantiles, levels, actuals)
    denominator = np.abs(actuals).sum()
    return float(2 * losses.sum(axis=0).mean() / denominator) if denominator else float("nan")


def scaled_errors(predicted, actuals, context, *, seasonal_period: int) -> tuple[float, float]:
    positive_int(seasonal_period, "seasonal_period")
    predicted, actuals = _paired(predicted, actuals)
    context = counts(context, name="context")
    if len(context) <= seasonal_period:
        return float("nan"), float("nan")
    differences = context[seasonal_period:] - context[:-seasonal_period]
    absolute_scale = np.mean(np.abs(differences))
    squared_scale = np.mean(differences**2)
    mase = mae(predicted, actuals) / absolute_scale if absolute_scale else float("nan")
    rmsse = (
        np.sqrt(np.mean((predicted - actuals) ** 2) / squared_scale)
        if squared_scale
        else float("nan")
    )
    return float(mase), float(rmsse)


def pit_values(samples, actuals, *, seed: int) -> np.ndarray:
    """F(y-) + U * mass(y), with an explicit seed for ties in empirical draws."""
    samples = np.asarray(samples, dtype=float)
    actuals = counts(actuals, name="actuals")
    if samples.ndim != 2 or samples.shape[1] != len(actuals) or not samples.shape[0]:
        raise ValueError("Sample horizon must equal the full actual horizon")
    counts(samples.ravel(), name="samples")
    lower = np.mean(samples < actuals, axis=0)
    mass = np.mean(samples == actuals, axis=0)
    return lower + np.random.default_rng(validate_seed(seed)).random(len(actuals)) * mass


def evaluate_forecast(
    forecast: ForecastOutput, actuals, *, context, quantile_levels, seasonal_period: int, seed: int
) -> dict:
    actuals = counts(actuals, name="actuals")
    if len(actuals) != forecast.horizon:
        raise ValueError("Forecast and actual horizons differ; truncating would drop targets")
    requested = np.column_stack([forecast.quantile(level) for level in quantile_levels])
    losses = quantile_losses(requested, quantile_levels, actuals)
    mase, rmsse = scaled_errors(forecast.median, actuals, context, seasonal_period=seasonal_period)
    crps = float("nan")
    pit = []
    if forecast.samples is not None:
        crps = float(
            np.mean(
                [crps_empirical(forecast.samples[:, i], actual) for i, actual in enumerate(actuals)]
            )
        )
        pit = pit_values(forecast.samples, actuals, seed=seed).tolist()
    return {
        "crps_mean": crps,
        "crps_method": "fair_iid_samples" if forecast.samples is not None else "unavailable",
        "mean_pinball_loss": float(losses.mean()),
        "qscore9": (
            float(2 * losses.mean())
            if np.array_equal(np.asarray(quantile_levels), np.arange(1, 10) / 10)
            else float("nan")
        ),
        "wql": weighted_quantile_loss(requested, quantile_levels, actuals),
        "mae": mae(forecast.median, actuals),
        "mase": mase,
        "rmsse": rmsse,
        "coverage_80": coverage(forecast.lower_80, forecast.upper_80, actuals),
        "coverage_95": coverage(forecast.lower_95, forecast.upper_95, actuals),
        "interval_score_80": interval_score(
            forecast.lower_80,
            forecast.upper_80,
            actuals,
            alpha=0.2,
        ),
        "pit_values": pit,
        "pit_method": "randomized_empirical" if forecast.samples is not None else "unavailable",
        "pit_seed": validate_seed(seed),
    }

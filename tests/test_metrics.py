import numpy as np
import pytest

from pulsegraph.evaluation.metrics import (
    coverage,
    crps_empirical,
    evaluate_forecast,
    interval_score,
    mae,
    pit_values,
    scaled_errors,
    weighted_quantile_loss,
)
from pulsegraph.forecast.output import COMMON_QUANTILES, ForecastOutput


def test_fair_crps_matches_pairwise_definition():
    values = np.array([0, 0, 1, 3, 10.0])
    expected = np.abs(values - 2).mean() - np.abs(values[:, None] - values).sum() / (2 * 5 * 4)
    assert crps_empirical(values, 2) == pytest.approx(expected)
    assert crps_empirical(np.full(100, 5), 5) == 0
    with pytest.raises(ValueError):
        crps_empirical([1], 2)


def test_mae_and_interval_scores_have_known_values():
    assert mae([10, 20], [12, 18]) == 2
    assert interval_score([1, 1], [3, 3], [0, 4], alpha=0.2) == 12
    assert coverage([1, 1], [3, 3], [0, 2]) == 0.5
    assert np.isnan(coverage([np.nan], [np.nan], [1]))
    with pytest.raises(ValueError):
        coverage([3], [1], [2])


def test_native_wql_convention_and_all_zero_denominator():
    assert weighted_quantile_loss([[1]], [0.5], [2]) == 0.5
    assert np.isnan(weighted_quantile_loss([[1]], [0.5], [0]))


def test_scaled_errors_use_context_seasonality_and_report_undefined_scale():
    assert scaled_errors([4], [6], [0, 1, 2, 3], seasonal_period=1) == (2, 2)
    assert all(np.isnan(v) for v in scaled_errors([4], [6], [0, 0, 0], seasonal_period=1))


def test_randomized_pit_handles_ties_and_seed():
    values = np.zeros((100, 8))
    pit = pit_values(values, np.zeros(8), seed=42)
    np.testing.assert_array_equal(pit, np.random.default_rng(42).random(8))
    assert np.all((pit > 0) & (pit < 1))
    assert len(set(pit)) == 8
    np.testing.assert_array_equal(pit_values(np.ones((100, 2)), [0, 2], seed=42), [0, 1])


def test_quantile_only_forecast_does_not_claim_full_crps_pit_or_95_interval():
    output = ForecastOutput(
        repo_name="a/b",
        model_name="native",
        horizon=2,
        context_length=30,
        quantile_levels=np.array(COMMON_QUANTILES),
        quantiles=np.ones((2, 9)),
    )
    metrics = evaluate_forecast(
        output,
        [1, 2],
        context=np.arange(30),
        quantile_levels=COMMON_QUANTILES,
        seasonal_period=7,
        seed=0,
    )
    assert np.isnan(metrics["crps_mean"])
    assert metrics["pit_values"] == []
    assert metrics["pit_method"] == "unavailable"
    assert np.isnan(metrics["coverage_95"])
    assert metrics["coverage_80"] == 0.5
    assert np.isfinite(metrics["mean_pinball_loss"])
    with pytest.raises(ValueError, match="horizons"):
        evaluate_forecast(
            output,
            [1],
            context=np.arange(30),
            quantile_levels=COMMON_QUANTILES,
            seasonal_period=7,
            seed=0,
        )


def test_shape_mismatch_does_not_broadcast_or_truncate():
    with pytest.raises(ValueError):
        mae([1], [1, 2])
    with pytest.raises(ValueError):
        pit_values(np.ones((3, 2)), [1], seed=0)

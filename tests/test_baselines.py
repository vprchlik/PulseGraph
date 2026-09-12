import numpy as np
import pytest

from pulsegraph.forecast.baselines import (
    BASELINE_FORECASTERS,
    LightGBMForecaster,
    LocalMeanForecaster,
    WeeklySeasonalNaiveForecaster,
)


@pytest.fixture
def sample_series():
    return np.random.default_rng(42).poisson(6, 100).astype(float)


@pytest.mark.parametrize("name", BASELINE_FORECASTERS)
def test_baseline_forecasts_are_reproducible_finite_and_ordered(name, sample_series):
    model = BASELINE_FORECASTERS[name](seed=42, n_samples=30)
    first = model.forecast(sample_series, 7, "a/b")
    second = model.forecast(sample_series, 7, "a/b")
    assert first.model_name == name
    assert first.samples.shape == (30, 7)
    assert np.isfinite(first.samples).all() and (first.samples >= 0).all()
    assert (np.diff(first.quantiles, axis=1) >= 0).all()
    np.testing.assert_array_equal(first.samples, second.samples)
    assert first.metadata["seed"] == 42
    assert isinstance(first.metadata["forecast_seed"], int)


def test_weekly_period_is_fixed_across_horizons():
    model = WeeklySeasonalNaiveForecaster(seed=1, n_samples=20)
    context = np.tile(np.arange(7), 10)
    for horizon in (7, 30, 90):
        np.testing.assert_array_equal(
            model.forecast(context, horizon).median, np.resize(np.arange(7), horizon)
        )


def test_zero_series_remains_zero_for_empirical_local_mean():
    output = LocalMeanForecaster(seed=1).forecast(np.zeros(80), 7)
    assert np.count_nonzero(output.samples) == 0


def test_seed_and_lookback_are_recorded_and_affect_forecast(sample_series):
    first = LocalMeanForecaster(seed=1).forecast(sample_series, 7)
    second = LocalMeanForecaster(seed=2).forecast(sample_series, 7)
    assert not np.array_equal(first.samples, second.samples)
    assert LocalMeanForecaster(seed=1, lookback=14).name == "local_mean_14"
    assert first.metadata["parameters"]["lookback"] == 28


def test_lightgbm_features_exclude_current_and_future_values(sample_series):
    first = LightGBMForecaster._build_features(sample_series, 70)
    sample_series[70:] = 1_000_000
    assert LightGBMForecaster._build_features(sample_series, 70) == first


@pytest.mark.parametrize("values", [[], [-1], [np.nan], [[1, 2]]])
def test_invalid_context_fails(values):
    with pytest.raises(ValueError):
        LocalMeanForecaster(seed=0).forecast(values, 7)


def test_invalid_sizes_and_seed_fail():
    for kwargs in ({"seed": -1}, {"seed": 0, "n_samples": 1}, {"seed": 0, "lookback": 0}):
        with pytest.raises(ValueError):
            LocalMeanForecaster(**kwargs)

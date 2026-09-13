import json

import numpy as np
import pytest

from pulsegraph.forecast.statsforecast_forecaster import (
    CLASSES,
    StatsForecastForecaster,
    native_deciles,
)


def test_native_decile_mapping():
    prediction = {"mean": [5.0]}
    for level in [20, 40, 60, 80]:
        prediction[f"lo-{level}"] = [5 - level / 20]
        prediction[f"hi-{level}"] = [5 + level / 20]
    np.testing.assert_array_equal(native_deciles(prediction), [np.arange(1, 10)])


def test_independent_native_median_smoke():
    pytest.importorskip("statsforecast")
    from pulsegraph.forecast.statsforecast_forecaster import verify_classical_medians

    checks = verify_classical_medians()
    assert len(checks) == 3 and all(c["passed"] for c in checks.values())


@pytest.mark.parametrize("name", CLASSES)
def test_zero_context_native_forecasts(name):
    pytest.importorskip("statsforecast")
    result = StatsForecastForecaster(name, seed=20260912).forecast(np.zeros(90), 7)
    assert np.isfinite(result.quantiles).all()
    np.testing.assert_allclose(result.median, 0, atol=1e-8)


@pytest.mark.parametrize("name", CLASSES)
@pytest.mark.parametrize("zeros", [False, True])
def test_native_runtime_smoke_specification_median_and_repeatability(name, zeros):
    pytest.importorskip("statsforecast")
    y = np.tile([1.0, 2.0, 3.0, 5.0, 3.0, 2.0, 4.0], 16) + np.random.default_rng(1).random(112)
    if zeros:
        y[::7] = 0
    model = StatsForecastForecaster(name, seed=20260912)
    first, second = model.forecast(y, 7, "a/b"), model.forecast(y, 7, "a/b")
    np.testing.assert_array_equal(first.quantiles, second.quantiles)
    np.testing.assert_allclose(first.median, np.maximum(0, first.metadata["point_forecast"]))
    assert first.samples is None and np.isnan(first.lower_95).all()
    spec = first.metadata["selected_specification"]
    assert spec and spec["distribution"] == "normal"
    json.dumps(first.metadata, allow_nan=False)
    if name == "autoets_weekly" and zeros:
        assert spec["components"][0] != "M" and spec["components"][2] != "M"
    if name in {"autoets_weekly", "autoarima_weekly"}:
        # For these synthetic fits analytic Gaussian intervals center on the point.
        unclipped = first.lower_80 > 0
        assert unclipped.any()
        np.testing.assert_allclose(
            ((first.lower_80 + first.upper_80) / 2)[unclipped],
            first.median[unclipped],
            atol=1e-5,
        )
    else:
        # Native Theta intervals are finite Monte Carlo quantiles, not exactly symmetric.
        assert first.metadata["native_interval_seed"] == 0
        assert first.metadata["native_interval_draws"] == 200

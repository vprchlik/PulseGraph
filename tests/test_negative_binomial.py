import numpy as np
import pytest
from scipy.stats import nbinom, poisson

from pulsegraph.forecast.negative_binomial import NegativeBinomialForecaster


def test_overdispersion_full_context_moments_and_local_mean():
    values = np.r_[np.tile([0.0, 0.0, 0.0, 40.0], 20), np.full(28, 2.0)]
    result = NegativeBinomialForecaster(seed=1).forecast(values, 90, "a/b")
    metadata = result.metadata
    alpha = (np.var(values, ddof=1) - np.mean(values)) / np.mean(values) ** 2
    assert metadata["mu"] == 2 and metadata["alpha"] == alpha
    expected = nbinom.ppf(result.quantile_levels, 1 / alpha, 1 / (1 + alpha * 2))
    np.testing.assert_array_equal(result.quantiles, np.tile(expected, (90, 1)))
    # Inverse CDF inequalities validate the actual count distribution, not interpolation.
    assert (
        nbinom.cdf(expected, 1 / alpha, metadata["probability"]) >= result.quantile_levels
    ).all()
    assert result.samples is None


def test_poisson_and_zero_limits():
    model = NegativeBinomialForecaster(seed=1)
    result = model.forecast(np.full(90, 3.0), 7)
    assert result.metadata["alpha"] == 0 and result.metadata["distribution"] == "poisson"
    np.testing.assert_array_equal(result.quantiles[0], poisson.ppf(result.quantile_levels, 3))
    for values in (np.zeros(90), np.r_[np.full(62, 100.0), np.zeros(28)]):
        result = model.forecast(values, 7)
        assert result.metadata["distribution"] == "point_mass_zero"
        assert not result.quantiles.any()
    with pytest.raises(ValueError, match="28 context"):
        model.forecast(np.ones(27), 7)

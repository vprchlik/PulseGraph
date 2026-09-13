"""Registered NB local-level distribution, including exact Poisson and zero limits."""

import numpy as np
from scipy.stats import nbinom, poisson

from pulsegraph.forecast.output import COMMON_QUANTILES, ForecastOutput
from pulsegraph.random import validate_seed
from pulsegraph.validation import counts, positive_int


class NegativeBinomialForecaster:
    name = "nb_local_level_28"

    def __init__(self, *, seed: int):
        self.seed = validate_seed(seed)

    def forecast(self, series, horizon: int, repo_name=""):
        values = counts(series, name="context")
        positive_int(horizon, "horizon")
        if len(values) < 28:
            raise ValueError("nb_local_level_28 requires 28 context days")
        mu = float(values[-28:].mean())
        mean = float(values.mean())
        variance = float(values.var(ddof=1))
        alpha = max((variance - mean) / mean**2, 0.0) if mean > 0 else 0.0
        levels = np.array(COMMON_QUANTILES)
        size = probability = None
        if mu == 0:
            distribution, deciles = "point_mass_zero", np.zeros(9)
        elif alpha == 0:
            distribution, deciles = "poisson", poisson.ppf(levels, mu)
        else:
            size = 1 / alpha
            probability = size / (size + mu)
            distribution, deciles = "negative_binomial", nbinom.ppf(levels, size, probability)
        return ForecastOutput(
            repo_name,
            self.name,
            horizon,
            len(values),
            levels,
            np.tile(deciles, (horizon, 1)),
            metadata={
                "seed": self.seed,
                "lookback": 28,
                "mu": mu,
                "context_mean": mean,
                "context_unbiased_variance": variance,
                "alpha": alpha,
                "size": size,
                "probability": probability,
                "predictive_variance": mu + alpha * mu**2,
                "distribution": distribution,
                "quantile_method": "analytic_inverse_cdf",
                "native_quantile_levels": levels.tolist(),
                "quantile_values_changed": 0,
            },
        )

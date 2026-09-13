"""Registered weekly StatsForecast models and their native central intervals."""

from importlib.metadata import version

import numpy as np

from pulsegraph.forecast.output import COMMON_QUANTILES, ForecastOutput
from pulsegraph.random import validate_seed
from pulsegraph.validation import counts, positive_int

VERSION = "2.1.1"
CLASSES = {
    "autoets_weekly": "AutoETS",
    "autoarima_weekly": "AutoARIMA",
    "autotheta_weekly": "AutoTheta",
}
INTERVAL_LEVELS = [20, 40, 60, 80]


def _json_value(value):
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    if isinstance(value, (tuple, list, np.ndarray)):
        return [_json_value(v) for v in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None  # Unused parameters, e.g. ETS trend, are explicitly absent.
    return value


def selected_specification(model):
    fitted = model.model_
    keys = (
        "method",
        "components",
        "m",
        "par",
        "sigma2",
        "arma",
        "coef",
        "code",
        "modeltype",
        "decompose",
        "decomposition_type",
        "distribution",
        "aicc",
    )
    return _json_value({key: fitted[key] for key in keys if key in fitted})


def native_deciles(prediction):
    return np.column_stack(
        [
            *(prediction[f"lo-{level}"] for level in [80, 60, 40, 20]),
            prediction["mean"],
            *(prediction[f"hi-{level}"] for level in INTERVAL_LEVELS),
        ]
    ).astype(float)


def verify_classical_medians():
    """Independent synthetic checks before clipping, including native Theta simulation."""
    from statsforecast import models

    if version("statsforecast") != VERSION:
        raise ValueError("StatsForecast smoke requires 2.1.1")
    values = np.tile([1.0, 2.0, 3.0, 5.0, 3.0, 2.0, 4.0], 16) + np.random.default_rng(1).random(112)
    checks = {}
    for name, classname in CLASSES.items():
        model = getattr(models, classname)(season_length=7).fit(values)
        prediction = model.predict(7, level=INTERVAL_LEVELS)
        point = np.asarray(prediction["mean"])
        if name == "autotheta_weekly":
            paths = model.simulate(7, 20000, seed=20260912)
            standard_error = 1.253314 * np.std(paths, axis=0) / np.sqrt(20000)
            deviations = np.abs(np.median(paths, axis=0) - point) / standard_error
            if not np.isfinite(deviations).all() or (deviations > 5).any():
                raise ValueError("Theta median smoke disagrees with the point forecast")
            checks[name] = {
                "passed": True,
                "method": "native normal simulation median within five MC standard errors",
                "simulation_seed": 20260912,
                "simulation_paths": 20000,
                "maximum_standard_errors": float(deviations.max()),
            }
        else:
            for level in INTERVAL_LEVELS:
                middle = (
                    np.asarray(prediction[f"lo-{level}"]) + np.asarray(prediction[f"hi-{level}"])
                ) / 2
                if not np.allclose(middle, point, rtol=1e-6, atol=1e-6):
                    raise ValueError("Gaussian interval center disagrees with point forecast")
            checks[name] = {
                "passed": True,
                "method": "native Gaussian central intervals centered on point before clipping",
            }
    return checks


class StatsForecastForecaster:
    def __init__(self, name: str, *, seed: int):
        if name not in CLASSES:
            raise ValueError("Unknown registered StatsForecast baseline")
        self.name = name
        self.seed = validate_seed(seed)

    def forecast(self, series, horizon: int, repo_name=""):
        from statsforecast import models

        if version("statsforecast") != VERSION:
            raise ValueError("StatsForecast must be exactly 2.1.1")
        values = counts(series, name="context")
        positive_int(horizon, "horizon")
        if len(values) < 28:
            raise ValueError("Weekly classical models require 28 context days")
        model = getattr(models, CLASSES[self.name])(season_length=7)
        model.fit(values.copy())
        specification = selected_specification(model)
        contains_zero = bool((values == 0).any())
        if self.name == "autoets_weekly" and contains_zero:
            components = specification["components"]
            if components[0] == "M" or components[2] == "M":
                raise ValueError("AutoETS selected multiplicative components with zeros")
        prediction = model.predict(horizon, level=INTERVAL_LEVELS)
        deciles = native_deciles(prediction)
        repaired = np.maximum.accumulate(np.maximum(0, deciles), axis=1)
        return ForecastOutput(
            repo_name,
            self.name,
            horizon,
            len(values),
            np.array(COMMON_QUANTILES),
            repaired,
            metadata={
                "seed": self.seed,
                "statsforecast_version": VERSION,
                "season_length": 7,
                "selected_specification": specification,
                "contains_zero": contains_zero,
                "native_interval_levels": INTERVAL_LEVELS,
                "native_quantile_levels": list(COMMON_QUANTILES),
                "distribution": "native_quantiles",
                "error_distribution": "normal",
                "median_source": "point_forecast",
                "point_forecast": np.asarray(prediction["mean"]).tolist(),
                # Native Theta intervals use 200 simulations, fixed seed 0 in 2.1.1.
                # ETS analytic intervals may internally simulate for some specifications.
                "native_interval_seed": 0
                if self.name == "autotheta_weekly"
                else (1 if self.name == "autoets_weekly" else None),
                "native_interval_draws": 200 if self.name == "autotheta_weekly" else None,
                "quantile_repair": "clip_then_cummax",
                "quantile_values_changed": int(np.count_nonzero(deciles != repaired)),
                "negative_quantile_values": int(np.count_nonzero(deciles < 0)),
                "crossing_quantile_values": int(
                    np.count_nonzero(repaired != np.maximum(0, deciles))
                ),
            },
        )

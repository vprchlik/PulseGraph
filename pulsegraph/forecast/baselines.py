"""V1 baseline families, ported as development candidates.

Residual draws are marginal samples around a deterministic path. Linear, ETS
and LightGBM use in-sample residuals; this is not rolling calibration. The
legacy horizon-dependent seasonal naive and nonseasonal ETS are retained for
continuity, not presented as the stronger v2 baselines still to be specified.
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from pulsegraph.forecast.output import ForecastOutput
from pulsegraph.random import derived_seed, validate_seed
from pulsegraph.validation import counts, positive_int


class _ResidualForecaster:
    name = ""
    residual_method = "in_sample_residual_bootstrap"

    def __init__(self, *, seed: int, n_samples: int = 200):
        self.seed = validate_seed(seed)
        self.n_samples = positive_int(n_samples, "n_samples")
        if n_samples < 2:
            raise ValueError("n_samples must be at least two")

    def parameters(self):
        return {"n_samples": self.n_samples}

    def point_and_residuals(self, values, horizon):
        raise NotImplementedError

    def forecast(self, series, horizon: int, repo_name: str = "") -> ForecastOutput:
        values = counts(series, name="context")
        positive_int(horizon, "horizon")
        seed = derived_seed(
            self.seed, self.name, repo_name, horizon, self.parameters(), values=values
        )
        point, residuals = self.point_and_residuals(values, horizon)
        point = counts(point, name="point forecast")
        residuals = np.asarray(residuals, dtype=np.float64)
        if len(point) != horizon or residuals.ndim != 1 or not residuals.size:
            raise ValueError("Invalid point forecast or empty residual distribution")
        if not np.isfinite(residuals).all():
            raise ValueError("Nonfinite residuals; fitting must not silently fall back")
        noise = np.random.default_rng(seed).choice(residuals, size=(self.n_samples, horizon))
        samples = np.maximum(0, point[None, :] + noise)
        return ForecastOutput.from_samples(
            repo_name=repo_name,
            model_name=self.name,
            horizon=horizon,
            context_length=len(values),
            samples=samples,
            metadata={
                "seed": self.seed,
                "forecast_seed": seed,
                "parameters": self.parameters(),
                "distribution": self.residual_method,
                "nonnegative_clipping": True,
            },
        )


class NaiveSeasonalForecaster(_ResidualForecaster):
    """Legacy v1 period=min(horizon, context length); not weekly seasonal naive."""

    name = "naive_seasonal"
    residual_method = "recent_first_difference_bootstrap"

    def point_and_residuals(self, values, horizon):
        period = min(horizon, len(values))
        residuals = np.diff(values[-90:]) if len(values) > 1 else np.array([0.0])
        return np.resize(values[-period:], horizon), residuals


class LastValueForecaster(_ResidualForecaster):
    name = "last_value"
    residual_method = "recent_first_difference_bootstrap"

    def point_and_residuals(self, values, horizon):
        residuals = np.diff(values[-91:]) if len(values) > 1 else np.array([0.0])
        return np.full(horizon, values[-1]), residuals


class WeeklySeasonalNaiveForecaster(_ResidualForecaster):
    name = "weekly_naive"
    residual_method = "recent_weekly_difference_bootstrap"

    def point_and_residuals(self, values, horizon):
        if len(values) < 7:
            raise ValueError("Weekly seasonal naive requires at least seven observations")
        residuals = (values[7:] - values[:-7])[-90:] if len(values) > 7 else np.array([0.0])
        return np.resize(values[-7:], horizon), residuals


class LocalMeanForecaster(_ResidualForecaster):
    residual_method = "recent_empirical_distribution"

    def __init__(self, *, seed: int, lookback: int = 28, n_samples: int = 200):
        super().__init__(seed=seed, n_samples=n_samples)
        self.lookback = positive_int(lookback, "lookback")
        self.name = f"local_mean_{lookback}"

    def parameters(self):
        return {**super().parameters(), "lookback": self.lookback}

    def point_and_residuals(self, values, horizon):
        tail = values[-self.lookback :]
        level = float(np.mean(tail))
        return np.full(horizon, level), tail - level


class LinearForecaster(_ResidualForecaster):
    def __init__(self, *, seed: int, lookback: int = 30, n_samples: int = 200):
        super().__init__(seed=seed, n_samples=n_samples)
        self.lookback = positive_int(lookback, "lookback")
        if self.lookback < 2:
            raise ValueError("Linear lookback must be at least two")
        self.name = f"linear_{lookback}"

    def parameters(self):
        return {**super().parameters(), "lookback": self.lookback}

    def point_and_residuals(self, values, horizon):
        tail = values[-self.lookback :]
        if len(tail) < 2:
            raise ValueError("Linear extrapolation requires two observations")
        x = np.arange(len(tail))
        slope, intercept, *_ = stats.linregress(x, tail)
        point = np.maximum(0, slope * np.arange(len(tail), len(tail) + horizon) + intercept)
        return point, tail - (slope * x + intercept)


class ETSForecaster(_ResidualForecaster):
    """V1 damped additive trend with no seasonality; not AutoETS."""

    name = "ets"

    def point_and_residuals(self, values, horizon):
        if len(values) < 3:
            raise ValueError("Damped ETS requires at least three observations")
        # Retained v1 offset, recorded as part of this candidate implementation.
        shifted = values + 0.01
        fit = ExponentialSmoothing(
            shifted,
            trend="add",
            damped_trend=True,
            seasonal=None,
            initialization_method="estimated",
        ).fit(optimized=True)
        return np.maximum(0, fit.forecast(horizon)), shifted - fit.fittedvalues

    def parameters(self):
        return {
            **super().parameters(),
            "trend": "add",
            "damped_trend": True,
            "seasonal": None,
            "offset": 0.01,
        }


class LightGBMForecaster(_ResidualForecaster):
    """V1 lag features with deterministic native LightGBM, no sklearn dependency."""

    name = "lightgbm"

    @staticmethod
    def _build_features(values: np.ndarray, idx: int) -> dict:
        features = {
            f"lag_{lag}": values[idx - lag] if idx >= lag else 0.0 for lag in (1, 2, 3, 7, 14, 30)
        }
        for window in (7, 14, 30):
            tail = values[max(0, idx - window) : idx] if idx else np.array([0.0])
            for name, function in (
                ("mean", np.mean),
                ("std", np.std),
                ("min", np.min),
                ("max", np.max),
            ):
                features[f"{name}_{window}"] = function(tail)
        features["trend_7"] = (
            float(np.polyfit(np.arange(7), values[idx - 7 : idx], 1)[0]) if idx >= 7 else 0.0
        )
        # A fixed weekly phase from the observation start, not a calendar weekday claim.
        features["weekly_phase"] = idx % 7
        return features

    def parameters(self):
        return {
            **super().parameters(),
            "num_boost_round": 100,
            "max_depth": 5,
            "learning_rate": 0.1,
            "min_data_in_leaf": 5,
            "num_threads": 1,
        }

    def point_and_residuals(self, values, horizon):
        import lightgbm as lgb

        start = max(60, len(values) // 2)
        if start >= len(values):
            raise ValueError("LightGBM requires more than 60 context observations")
        features = pd.DataFrame(
            [self._build_features(values, i) for i in range(start, len(values))]
        )
        targets = values[start:]
        fit = lgb.train(
            {
                "objective": "regression",
                "max_depth": 5,
                "learning_rate": 0.1,
                "min_data_in_leaf": 5,
                "verbosity": -1,
                "seed": self.seed % (2**31),
                "deterministic": True,
                "force_col_wise": True,
                "num_threads": 1,
            },
            lgb.Dataset(features, label=targets),
            num_boost_round=100,
        )
        residuals = targets - fit.predict(features, num_threads=1)
        extended = np.concatenate([values, np.zeros(horizon)])
        for step in range(horizon):
            idx = len(values) + step
            row = pd.DataFrame([self._build_features(extended, idx)])
            extended[idx] = max(0.0, float(fit.predict(row, num_threads=1)[0]))
        return extended[len(values) :], residuals


BASELINE_FORECASTERS = {
    "naive_seasonal": NaiveSeasonalForecaster,
    "linear_30": LinearForecaster,
    "ets": ETSForecaster,
    "lightgbm": LightGBMForecaster,
    "last_value": LastValueForecaster,
    "weekly_naive": WeeklySeasonalNaiveForecaster,
    "local_mean_28": LocalMeanForecaster,
}

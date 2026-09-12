"""Forecast representation shared by sample and native-quantile models."""

from dataclasses import dataclass, field

import numpy as np

from pulsegraph.validation import counts, positive_int

COMMON_QUANTILES = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
SAMPLE_QUANTILES = (0.025, *COMMON_QUANTILES, 0.975)


@dataclass
class ForecastOutput:
    repo_name: str
    model_name: str
    horizon: int
    context_length: int
    quantile_levels: np.ndarray
    quantiles: np.ndarray  # (horizon, n_quantiles)
    samples: np.ndarray | None = None  # IID marginal draws, never pseudo-samples
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        positive_int(self.horizon, "horizon")
        positive_int(self.context_length, "context_length")
        self.quantile_levels = np.asarray(self.quantile_levels, dtype=np.float64).copy()
        q = self.quantile_levels
        if q.ndim != 1 or q.size < 2 or not np.isfinite(q).all():
            raise ValueError("At least two finite quantile levels are required")
        if (q <= 0).any() or (q >= 1).any() or (np.diff(q) <= 0).any():
            raise ValueError("Quantile levels must increase strictly within (0, 1)")
        self.quantiles = np.asarray(self.quantiles, dtype=np.float64).copy()
        if self.quantiles.shape != (self.horizon, len(q)):
            raise ValueError("Quantile forecast shape does not match horizon and levels")
        if not np.isfinite(self.quantiles).all() or (self.quantiles < 0).any():
            raise ValueError("Forecast quantiles must be finite and nonnegative")
        if (np.diff(self.quantiles, axis=1) < 0).any():
            raise ValueError("Forecast quantiles cross")
        if not q[0] <= 0.5 <= q[-1]:
            raise ValueError("Forecast quantiles must support the median")
        if self.samples is not None:
            self.samples = np.asarray(self.samples, dtype=np.float64).copy()
            if self.samples.ndim != 2 or self.samples.shape[1] != self.horizon:
                raise ValueError("Sample shape must be (n_samples, horizon)")
            if self.samples.shape[0] < 2:
                raise ValueError("Fair sample CRPS requires at least two IID draws")
            counts(self.samples.ravel(), name="forecast samples")
            expected = np.quantile(self.samples, q, axis=0).T
            if not np.allclose(self.quantiles, expected, rtol=1e-10, atol=1e-12):
                raise ValueError("Sample-derived quantiles disagree with the saved draws")

    def quantile(self, level: float) -> np.ndarray:
        if not 0 < level < 1:
            raise ValueError("Quantile level must be in (0, 1)")
        if not self.quantile_levels[0] <= level <= self.quantile_levels[-1]:
            return np.full(self.horizon, np.nan)
        return np.array([np.interp(level, self.quantile_levels, row) for row in self.quantiles])

    @property
    def median(self):
        return self.quantile(0.5)

    @property
    def lower_80(self):
        return self.quantile(0.1)

    @property
    def upper_80(self):
        return self.quantile(0.9)

    @property
    def lower_95(self):
        return self.quantile(0.025)

    @property
    def upper_95(self):
        return self.quantile(0.975)

    @classmethod
    def from_samples(cls, *, samples, **kwargs):
        samples = np.asarray(samples, dtype=np.float64)
        if samples.ndim != 2 or samples.shape[0] < 2:
            raise ValueError("At least two sample rows are required")
        return cls(
            samples=samples,
            quantile_levels=np.array(SAMPLE_QUANTILES),
            quantiles=np.quantile(samples, SAMPLE_QUANTILES, axis=0).T,
            **kwargs,
        )

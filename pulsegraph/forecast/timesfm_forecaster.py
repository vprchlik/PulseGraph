"""TimesFM-2.5 native deciles. Unsupported 95% intervals remain NaN."""

import numpy as np

from pulsegraph.forecast.output import ForecastOutput
from pulsegraph.forecast.runtime import as_numpy, load_snapshot, validate_revision
from pulsegraph.random import validate_seed
from pulsegraph.validation import counts, positive_int


class TimesFMForecaster:
    name = "timesfm2p5"
    native_levels = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])

    def __init__(
        self,
        *,
        revision: str,
        seed: int,
        max_context: int,
        max_horizon: int,
        model_id: str = "google/timesfm-2.5-200m-pytorch",
        threads: int = 4,
    ):
        self.revision = validate_revision(revision)
        self.seed = validate_seed(seed)
        self.max_context = positive_int(max_context, "max_context")
        self.max_horizon = positive_int(max_horizon, "max_horizon")
        self.threads = positive_int(threads, "threads")
        self.model_id = model_id
        self._model = None

    @property
    def model(self):
        if self._model is None:
            import timesfm

            path = load_snapshot(self.model_id, self.revision, seed=self.seed, threads=self.threads)
            model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(path)
            model.compile(
                timesfm.ForecastConfig(
                    max_context=self.max_context,
                    max_horizon=self.max_horizon,
                    normalize_inputs=True,
                    use_continuous_quantile_head=True,
                    fix_quantile_crossing=True,
                )
            )
            self._model = model
        return self._model

    def forecast(self, series, horizon: int, repo_name: str = "") -> ForecastOutput:
        values = counts(series, name="context")
        positive_int(horizon, "horizon")
        if horizon > self.max_horizon:
            raise ValueError("Requested horizon exceeds configured TimesFM horizon")
        context = values[-self.max_context :].astype(np.float32)
        _, output = self.model.forecast(horizon=horizon, inputs=[context])
        quantiles = as_numpy(output[0])
        if quantiles.shape != (horizon, 10):
            raise ValueError("Expected TimesFM-2.5 point forecast plus nine deciles")
        deciles = quantiles[:, 1:10]
        repaired = np.maximum.accumulate(np.maximum(0, deciles), axis=1)
        return ForecastOutput(
            repo_name=repo_name,
            model_name=self.name,
            horizon=horizon,
            context_length=len(context),
            quantile_levels=self.native_levels,
            quantiles=repaired,
            metadata={
                "seed": self.seed,
                "model_id": self.model_id,
                "revision": self.revision,
                "threads": self.threads,
                "max_context": self.max_context,
                "max_horizon": self.max_horizon,
                "available_context": len(values),
                "distribution": "native_quantiles",
                "supported_interval_levels": [0.8],
                "quantile_repair": "clip_then_cummax",
                "quantile_values_changed": int(np.count_nonzero(repaired != deciles)),
            },
        )

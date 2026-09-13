"""TimesFM 3 via timesfm==3.0.2; source API: https://pypi.org/project/timesfm/3.0.2/."""

import numpy as np

from pulsegraph.forecast.output import ForecastOutput
from pulsegraph.forecast.runtime import as_numpy, load_snapshot
from pulsegraph.forecast.timesfm_forecaster import TimesFMForecaster
from pulsegraph.validation import counts, positive_int


class TimesFM3Forecaster(TimesFMForecaster):
    name = "timesfm3"

    def __init__(self, *, device="cuda", **kwargs):
        kwargs.setdefault("model_id", "google/timesfm-3.0-pytorch")
        super().__init__(**kwargs)
        if self.max_context > 15360:
            raise ValueError("TimesFM 3 context exceeds native capacity")
        self.device = device

    @property
    def model(self):
        if self._model is None:
            from timesfm3 import ModelConfig, TimesFM3Evaluator

            path = load_snapshot(self.model_id, self.revision, seed=self.seed, threads=self.threads)
            self._model = TimesFM3Evaluator(
                ModelConfig(checkpoint_path=path, per_core_batch_size=1, device=self.device)
            )
        return self._model

    def forecast(self, series, horizon: int, repo_name: str = "") -> ForecastOutput:
        values = counts(series, name="context")
        positive_int(horizon, "horizon")
        if horizon > self.max_horizon:
            raise ValueError("Requested horizon exceeds configured TimesFM horizon")
        context = values[-self.max_context :].astype(np.float32)
        model = self.model
        levels = np.asarray(model.config.quantiles, dtype=float)
        if not np.array_equal(levels, self.native_levels):
            raise ValueError("TimesFM 3 checkpoint must expose the nine native deciles")
        output = list(
            model.predict_batch(
                [context],
                horizon=horizon,
                return_quantiles=True,
                use_symmetric_averaging=False,
            )
        )
        if len(output) != 1:
            raise ValueError("TimesFM 3 returned an unexpected batch size")
        deciles = as_numpy(output[0].quantiles)
        if deciles.shape != (horizon, 9):
            raise ValueError("Expected TimesFM 3 nine deciles")
        repaired = np.maximum.accumulate(np.maximum(0, deciles), axis=1)
        return ForecastOutput(
            repo_name,
            self.name,
            horizon,
            len(context),
            levels,
            repaired,
            metadata={
                "seed": self.seed,
                "model_id": self.model_id,
                "revision": self.revision,
                "threads": self.threads,
                "max_context": self.max_context,
                "max_horizon": self.max_horizon,
                "available_context": len(values),
                "device": self.device,
                "batch_size": 1,
                "timesfm_version": "3.0.2",
                "native_quantile_levels": levels.tolist(),
                "distribution": "native_quantiles",
                "supported_interval_levels": [0.8],
                "use_symmetric_averaging": False,
                "backend": "timesfm3.TimesFM3Evaluator",
                "return_quantiles": True,
                "quantile_repair": "clip_then_cummax",
                "quantile_values_changed": int(np.count_nonzero(repaired != deciles)),
                "negative_quantile_values": int(np.count_nonzero(deciles < 0)),
                "crossing_quantile_values": int(
                    np.count_nonzero(repaired != np.maximum(0, deciles))
                ),
            },
        )

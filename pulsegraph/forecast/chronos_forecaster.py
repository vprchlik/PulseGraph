"""Chronos-2 adapter preserving native quantiles rather than inventing tails."""

import numpy as np

from pulsegraph.forecast.output import ForecastOutput
from pulsegraph.forecast.runtime import as_numpy, load_snapshot, validate_revision
from pulsegraph.random import validate_seed
from pulsegraph.validation import counts, positive_int


class ChronosForecaster:
    name = "chronos2"
    native_levels = np.array(
        [
            0.01,
            0.05,
            0.10,
            0.15,
            0.20,
            0.25,
            0.30,
            0.35,
            0.40,
            0.45,
            0.50,
            0.55,
            0.60,
            0.65,
            0.70,
            0.75,
            0.80,
            0.85,
            0.90,
            0.95,
            0.99,
        ]
    )

    def __init__(
        self,
        *,
        revision: str,
        seed: int,
        max_context: int,
        model_id: str = "amazon/chronos-2",
        device: str = "cpu",
        threads: int = 4,
    ):
        self.revision = validate_revision(revision)
        self.seed = validate_seed(seed)
        self.max_context = positive_int(max_context, "max_context")
        self.threads = positive_int(threads, "threads")
        self.model_id, self.device = model_id, device
        self._pipeline = None

    @property
    def pipeline(self):
        if self._pipeline is None:
            from chronos import Chronos2Pipeline

            path = load_snapshot(self.model_id, self.revision, seed=self.seed, threads=self.threads)
            self._pipeline = Chronos2Pipeline.from_pretrained(path, device_map=self.device)
        return self._pipeline

    def forecast(self, series, horizon: int, repo_name: str = "") -> ForecastOutput:
        values = counts(series, name="context")
        positive_int(horizon, "horizon")
        context = values[-self.max_context :].astype(np.float32)
        output, _ = self.pipeline.predict_quantiles(
            [context],
            prediction_length=horizon,
            quantile_levels=self.native_levels.tolist(),
        )
        quantiles = as_numpy(output[0])
        if quantiles.shape == (1, horizon, len(self.native_levels)):
            quantiles = quantiles[0]
        if quantiles.shape != (horizon, len(self.native_levels)):
            raise ValueError("Unexpected Chronos-2 output shape")
        repaired = np.maximum.accumulate(np.maximum(0, quantiles), axis=1)
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
                "device": self.device,
                "threads": self.threads,
                "max_context": self.max_context,
                "available_context": len(values),
                "distribution": "native_quantiles",
                "quantile_repair": "clip_then_cummax",
                "quantile_values_changed": int(np.count_nonzero(repaired != quantiles)),
            },
        )

import sys
from types import SimpleNamespace

import numpy as np
import pytest

from pulsegraph.forecast.timesfm3_forecaster import TimesFM3Forecaster


def test_timesfm3_pinned_load_native_deciles_and_no_tails(monkeypatch):
    calls = []
    seen = []
    revision = "43046b85ec22d584a13f8098c2ed39c889e129c2"
    monkeypatch.setattr(
        "pulsegraph.forecast.timesfm3_forecaster.load_snapshot",
        lambda *a, **kw: calls.append((a, kw)) or "local-snapshot",
    )

    def predict(contexts, horizon, return_quantiles, use_symmetric_averaging):
        assert return_quantiles is True and use_symmetric_averaging is False
        seen.append(contexts)
        return [SimpleNamespace(quantiles=np.tile([-1, 2, 1, 3, 4, 5, 6, 7, 8], (horizon, 1)))]

    native = SimpleNamespace(
        config=SimpleNamespace(quantiles=TimesFM3Forecaster.native_levels), predict_batch=predict
    )

    def model_config(*, checkpoint_path, per_core_batch_size, device):
        assert checkpoint_path == "local-snapshot"
        assert per_core_batch_size == 1 and device == "cuda"
        return SimpleNamespace(
            checkpoint_path=checkpoint_path, per_core_batch_size=per_core_batch_size, device=device
        )

    def evaluator(config):
        assert config.checkpoint_path == "local-snapshot"
        return native

    monkeypatch.setitem(
        sys.modules,
        "timesfm3",
        SimpleNamespace(ModelConfig=model_config, TimesFM3Evaluator=evaluator),
    )
    model = TimesFM3Forecaster(revision=revision, seed=123, max_context=64, max_horizon=128)
    result = model.forecast(np.arange(100), 7, "a/b")
    assert calls[0][0] == ("google/timesfm-3.0-pytorch", revision)
    np.testing.assert_array_equal(seen[0][0], np.arange(36, 100))
    np.testing.assert_array_equal(result.median, np.full(7, 4))
    assert np.isnan(result.lower_95).all() and result.samples is None
    assert result.metadata["native_quantile_levels"] == TimesFM3Forecaster.native_levels.tolist()
    np.testing.assert_array_equal(result.quantiles[0], [0, 2, 2, 3, 4, 5, 6, 7, 8])
    assert result.metadata["negative_quantile_values"] == 7
    assert result.metadata["crossing_quantile_values"] == 7
    assert result.metadata["quantile_repair"] == "clip_then_cummax"
    with pytest.raises(ValueError, match="horizon"):
        model.forecast([1], 129)
    native.config.quantiles = [0.05, 0.5, 0.95]
    with pytest.raises(ValueError, match="native deciles"):
        model.forecast([1], 1)

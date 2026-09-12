import sys
from types import SimpleNamespace

import numpy as np
import pytest

from pulsegraph.forecast.chronos_forecaster import ChronosForecaster
from pulsegraph.forecast.output import ForecastOutput
from pulsegraph.forecast.timesfm_forecaster import TimesFMForecaster

REVISION = "a" * 40  # Synthetic revision used only by mocked loaders.


def chronos(**overrides):
    return ChronosForecaster(**(dict(revision=REVISION, seed=42, max_context=16) | overrides))


def timesfm(**overrides):
    return TimesFMForecaster(
        **(dict(revision=REVISION, seed=42, max_context=16, max_horizon=32) | overrides)
    )


@pytest.mark.parametrize("revision", ["main", "v2", "123abcd", "", None, "A" * 40])
def test_unpinned_revision_is_rejected_without_model_import(revision):
    with pytest.raises(ValueError, match="revision hash"):
        chronos(revision=revision)
    with pytest.raises(ValueError, match="revision hash"):
        timesfm(revision=revision)


def test_chronos_shape_native_quantiles_and_context_truncation():
    model = chronos()
    seen = []

    def predict(inputs, prediction_length, quantile_levels):
        seen.append(inputs[0])
        return [np.tile(np.asarray(quantile_levels) * 10, (1, prediction_length, 1))], None

    model._pipeline = SimpleNamespace(predict_quantiles=predict)
    result = model.forecast(np.arange(50), 7, "a/b")
    np.testing.assert_array_equal(seen[0], np.arange(34, 50))
    assert result.context_length == 16
    assert result.samples is None
    np.testing.assert_allclose(result.median, 5)
    np.testing.assert_allclose(result.lower_95, 0.25)
    assert result.metadata["revision"] == REVISION


def test_timesfm_uses_deciles_not_point_column_and_95_is_unsupported():
    model = timesfm()
    output = np.tile(np.arange(10), (1, 7, 1)).astype(float)
    output[:, :, 0] = 999
    model._model = SimpleNamespace(forecast=lambda **kwargs: (None, output))
    result = model.forecast(np.arange(50), 7, "a/b")
    np.testing.assert_array_equal(result.median, np.full(7, 5))
    np.testing.assert_array_equal(result.lower_80, np.ones(7))
    np.testing.assert_array_equal(result.upper_80, np.full(7, 9))
    assert np.isnan(result.lower_95).all() and np.isnan(result.upper_95).all()
    assert result.samples is None
    assert result.metadata["supported_interval_levels"] == [0.8]
    with pytest.raises(ValueError, match="horizon"):
        model.forecast(np.arange(50), 33)


def test_quantile_repair_is_recorded_and_bad_shapes_fail():
    model = timesfm()
    output = np.array([[[0, -1, 3, 2, 4, 5, 6, 7, 8, 9]]], dtype=float)
    model._model = SimpleNamespace(forecast=lambda **kwargs: (None, output))
    result = model.forecast([1, 2], 1)
    assert result.metadata["quantile_values_changed"] == 2
    assert result.quantiles[0].tolist() == [0, 3, 3, 4, 5, 6, 7, 8, 9]
    with pytest.raises(ValueError, match="deciles"):
        model.forecast([1, 2], 2)


def test_model_loaders_use_pinned_local_snapshot(monkeypatch, tmp_path):
    requests = []

    def snapshot_download(**kwargs):
        requests.append(kwargs)
        return str(tmp_path)

    torch = SimpleNamespace(
        manual_seed=lambda *_: None,
        set_num_threads=lambda *_: None,
        use_deterministic_algorithms=lambda *_: None,
    )
    monkeypatch.setitem(sys.modules, "torch", torch)
    monkeypatch.setitem(
        sys.modules, "huggingface_hub", SimpleNamespace(snapshot_download=snapshot_download)
    )
    loads = []

    def pretrained(path, **kwargs):
        loads.append((path, kwargs))
        return SimpleNamespace(compile=lambda *_: None)

    monkeypatch.setitem(
        sys.modules,
        "chronos",
        SimpleNamespace(Chronos2Pipeline=SimpleNamespace(from_pretrained=pretrained)),
    )
    monkeypatch.setitem(
        sys.modules,
        "timesfm",
        SimpleNamespace(
            TimesFM_2p5_200M_torch=SimpleNamespace(from_pretrained=pretrained),
            ForecastConfig=lambda **kwargs: kwargs,
        ),
    )
    _ = chronos().pipeline
    _ = timesfm().model
    assert len(requests) == 2
    assert all(request["revision"] == REVISION for request in requests)
    assert all(path == str(tmp_path) for path, _ in loads)


def test_forecast_container_rejects_crossed_or_nonfinite_quantiles():
    for quantiles in ([[2, 1, 3]], [[1, np.nan, 3]]):
        with pytest.raises(ValueError):
            ForecastOutput("a/b", "bad", 1, 30, np.array([0.1, 0.5, 0.9]), quantiles)


def test_saved_samples_and_quantiles_cannot_describe_different_forecasts():
    with pytest.raises(ValueError, match="disagree"):
        ForecastOutput(
            "a/b",
            "bad",
            1,
            30,
            np.array([0.1, 0.5, 0.9]),
            [[2, 2, 2]],
            samples=np.ones((20, 1)),
        )

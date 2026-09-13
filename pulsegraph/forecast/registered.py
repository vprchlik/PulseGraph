"""Construct exactly the registered candidates, one model at a time."""

import gc

from pulsegraph.forecast.baselines import BASELINE_FORECASTERS, LocalMeanForecaster
from pulsegraph.forecast.chronos_forecaster import ChronosForecaster
from pulsegraph.forecast.negative_binomial import NegativeBinomialForecaster
from pulsegraph.forecast.statsforecast_forecaster import CLASSES, StatsForecastForecaster
from pulsegraph.forecast.timesfm3_forecaster import TimesFM3Forecaster
from pulsegraph.forecast.timesfm_forecaster import TimesFMForecaster


def make_registered_model(name, spec):
    seed = spec["seeds"]["forecast"]
    settings = spec["inference"]
    if name in CLASSES:
        return StatsForecastForecaster(name, seed=seed)
    if name == "nb_local_level_28":
        return NegativeBinomialForecaster(seed=seed)
    if name.startswith("local_mean_") and name in spec["baselines"]:
        return LocalMeanForecaster(seed=seed, lookback=int(name.rsplit("_", 1)[1]), n_samples=200)
    if name in BASELINE_FORECASTERS:
        return BASELINE_FORECASTERS[name](seed=seed, n_samples=200)
    pin = next((m for m in spec["foundation_models"] if m["name"] == name), None)
    if pin is None:
        raise ValueError("Unregistered model")
    common = dict(
        revision=pin["revision"],
        seed=seed,
        max_context=settings["max_context"],
        model_id=pin["model_id"],
        threads=settings["threads"],
    )
    if name == "chronos2":
        return ChronosForecaster(**common, device="cuda")
    cls = TimesFM3Forecaster if name == "timesfm3" else TimesFMForecaster
    return cls(**common, max_horizon=settings["max_horizon"])


def release_model(model):
    for attribute in ("_model", "_pipeline"):
        if hasattr(model, attribute):
            setattr(model, attribute, None)
    gc.collect()
    import torch

    torch.cuda.empty_cache()

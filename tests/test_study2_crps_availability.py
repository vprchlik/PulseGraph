"""Uncertified discrete CRPS is unavailable and counted, never a stop (dated addition 5)."""

import json

import numpy as np
import pandas as pd
import pytest

from pulsegraph.config import ROOT_DIR
from pulsegraph.forecast.output import COMMON_QUANTILES
from pulsegraph.provenance import read_json
from pulsegraph.study2.constants import VARIANTS
from pulsegraph.study2.distributions import CountLaw, complete, discrete_crps
from pulsegraph.study2.models import law_forecast
from pulsegraph.study2.runner import _evaluate
from pulsegraph.study2.scores import (
    CRPS_UNCERTIFIED,
    NO_DISTRIBUTION,
    UNCERTIFIED_ERROR,
    crps_denominators,
    score,
)

DISTRIBUTION_VARIANTS = [name for name in VARIANTS if name.endswith(("_completed", "_hurdle"))] + [
    "nb_local_level_28",
    "poisson_28",
    "hurdle_count_28",
    "hurdle_empirical_28",
    "dynamic_count",
]


def _huge():
    return complete(np.floor(np.linspace(9.5e6, 1.05e7, 9)))


def test_uncertified_crps_is_unavailable_with_its_reason_and_does_not_raise():
    law = _huge()
    with pytest.raises(ValueError) as error:
        discrete_crps(law, 10_000_000)
    assert str(error.value) == UNCERTIFIED_ERROR
    for target in ([10_000_000, 9_900_000], [0, 0]):
        result = score(target, law_forecast([law] * 2), np.full(28, 1e7))
        assert result["discrete_crps"] is None and result["crps_max_residual_bound"] is None
        assert result["crps_unavailable_reason"] == CRPS_UNCERTIFIED
        assert result["crps_last_k"] is None
        assert np.isfinite(result["qscore9"])
        expected = np.mean([(law.sf(0) - (y > 0)) ** 2 for y in target])
        assert result["occurrence_brier"] == pytest.approx(expected)


def test_certified_crps_is_unchanged():
    resolution = read_json(ROOT_DIR / "study/study2/crps_resolution.json")["crps"]
    for case in resolution["cases"]:
        law = CountLaw(case["distribution"])
        forecast = dict(deciles=[law.ppf(COMMON_QUANTILES).tolist()], distributions=[law.spec])
        result = score([case["target"]], forecast, np.zeros(28))
        assert result["discrete_crps"] == case["value"]
        assert result["crps_max_residual_bound"] == case["residual_bound"]
        assert result["crps_last_k"] == case["last_k"]
        assert result["crps_unavailable_reason"] is None
    law, target = CountLaw(dict(kind="poisson", mu=3.0)), [0, 2, 5, 11]
    result = score(target, law_forecast([law] * 4), np.full(28, 3.0))
    assert result["discrete_crps"] == float(
        np.mean([discrete_crps(law, y)["value"] for y in target])
    )


def test_other_crps_errors_still_stop_scoring():
    forecast = dict(deciles=[list(range(9))], distributions=[dict(kind="unregistered")])
    with pytest.raises(ValueError, match="Unknown count distribution"):
        score([1], forecast, np.zeros(28))
    result = score([1], dict(deciles=[list(range(9))], distributions=None), np.zeros(28))
    assert result["crps_unavailable_reason"] == NO_DISTRIBUTION


def test_run_completes_with_an_uncertified_series_and_counts_it(tmp_path):
    dates = pd.date_range("2025-09-01", "2026-08-31")
    dataset = {
        ("packages", "small"): pd.Series(3.0, index=dates),
        ("packages", "huge"): pd.Series(1e7, index=dates),
    }

    class Pool:
        def forecast(self, context, horizon, key):
            level = float(context[-1])
            deciles = np.floor(level * np.linspace(0.5, 1.5, 9))
            forecasts = {
                name: dict(deciles=np.tile(deciles, (horizon, 1)).tolist(), distributions=None)
                for name in VARIANTS
            }
            for name in DISTRIBUTION_VARIANTS:
                forecasts[name] = law_forecast([complete(deciles)] * horizon)
            return forecasts

    state = _evaluate(dataset, tmp_path, Pool(), metadata={"fixture": True})
    assert state["status"] == "complete" and len(state["completed"]) == 2
    rows = [
        row
        for path in tmp_path.glob("*.json")
        if path.name != "run.json"
        for row in json.loads(path.read_text(encoding="utf-8"))["rows"]
    ]
    assert len(rows) == 2 * 3 * 2 * len(VARIANTS)
    for row in rows:
        reason = row["scores"]["crps_unavailable_reason"]
        if row["model"] not in DISTRIBUTION_VARIANTS:
            assert reason == NO_DISTRIBUTION
        elif row["series_id"] == "huge":
            assert reason == CRPS_UNCERTIFIED and row["scores"]["discrete_crps"] is None
            assert row["scores"]["occurrence_brier"] is not None
        else:
            assert reason is None and row["scores"]["discrete_crps"] is not None
    with_distribution = 2 * 3 * 2 * len(DISTRIBUTION_VARIANTS)
    assert crps_denominators([row["scores"] for row in rows]) == dict(
        forecasts=len(rows),
        with_count_distribution=with_distribution,
        certified=with_distribution // 2,
        unavailable={
            CRPS_UNCERTIFIED: with_distribution // 2,
            NO_DISTRIBUTION: len(rows) - with_distribution,
        },
    )

import numpy as np
import pandas as pd
import pytest

from pulsegraph.data.regimes import assert_eligibility_precedes_cutoff, context_regime
from pulsegraph.evaluation.backtest import BacktestConfig, rolling_backtest
from pulsegraph.forecast.baselines import LocalMeanForecaster


def test_label_boundaries():
    index = pd.date_range("2024-01-01", periods=90)
    values = np.ones(90)
    assert context_regime(pd.Series(values, index=index)) == "Other active"
    values[-7:] = 3
    assert context_regime(pd.Series(values, index=index)) == "Recent surge"
    values[-7:] = 2
    assert context_regime(pd.Series(values, index=index)) == "Other active"
    values[-28:] = 0
    assert context_regime(pd.Series(values, index=index)) == "Inactive recently"
    assert_eligibility_precedes_cutoff("2024-01-01", "2024-03-31")
    with pytest.raises(ValueError, match="b\\+89 < c"):
        assert_eligibility_precedes_cutoff("2024-01-01", "2024-03-30")


def test_actual_labeler_cannot_observe_perturbed_permuted_or_extended_targets():
    cutoff = pd.Timestamp("2024-04-01")
    original = pd.Series(np.arange(130) % 5, index=pd.date_range("2024-01-01", periods=130))
    config = BacktestConfig((7,), ("2024-04-01",), 90, tuple(np.arange(1, 10) / 10), 7, 123)
    observed = []

    def spy(context):
        observed.extend(context.index)
        assert (context.index < cutoff).all()
        assert_eligibility_precedes_cutoff(context.index[0], cutoff)
        return context_regime(context)

    variants = [original.copy() for _ in range(3)]
    variants[0].loc[cutoff:] = 100000
    variants[1].loc[cutoff:] = np.random.default_rng(1).permutation(original.loc[cutoff:])
    variants[2] = pd.concat(
        [
            variants[2],
            pd.Series(
                999, index=pd.date_range(original.index[-1] + pd.Timedelta(days=1), periods=100)
            ),
        ]
    )
    labels = []
    for series in [original, *variants]:
        result = rolling_backtest(
            series, LocalMeanForecaster(seed=123), config, repo_name="test/repo", labeler=spy
        )
        labels.append(result.stratum.tolist())
    assert all(label == labels[0] for label in labels)
    assert observed and max(observed) < cutoff

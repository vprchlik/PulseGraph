import numpy as np
import pandas as pd
import pytest

from pulsegraph.evaluation.backtest import BacktestConfig, run_backtest_suite, summarize_backtest
from pulsegraph.forecast.baselines import LastValueForecaster
from pulsegraph.forecast.output import COMMON_QUANTILES


def config(**overrides):
    values = dict(
        horizons=(3, 7),
        cutoffs=("2022-03-01", "2022-03-08"),
        min_context_days=30,
        quantile_levels=COMMON_QUANTILES,
        seasonal_period=7,
        seed=42,
    )
    return BacktestConfig(**(values | overrides))


def series():
    return pd.Series(np.arange(80) % 7, index=pd.date_range("2022-01-01", periods=80))


class Spy(LastValueForecaster):
    def __init__(self, *, mutate=False):
        super().__init__(seed=42, n_samples=20)
        self.contexts = []
        self.mutate = mutate

    def forecast(self, context, horizon, repo_name):
        self.contexts.append(context.copy())
        result = super().forecast(context, horizon, repo_name)
        if self.mutate:
            context.iloc[:] = 999
        return result


def test_models_and_labels_see_only_context_and_future_changes_cannot_affect_them():
    observed = series()
    labels_seen = []

    def label(context):
        labels_seen.append(context.copy())
        return "nonzero" if context.sum() else "zero"

    first_model = Spy()
    first = run_backtest_suite(
        {"a/b": observed},
        {"last_value": first_model},
        config(cutoffs=("2022-03-01",)),
        labeler=label,
    )
    changed = observed.copy()
    changed.loc["2022-03-01":] = 1_000_000
    second_model = Spy()
    second = run_backtest_suite(
        {"a/b": changed},
        {"last_value": second_model},
        config(cutoffs=("2022-03-01",)),
        labeler=label,
    )
    for context in first_model.contexts + second_model.contexts + labels_seen:
        pd.testing.assert_series_equal(context, observed.loc[:"2022-02-28"])
    assert first.stratum.tolist() == second.stratum.tolist()
    assert first.samples.tolist() == second.samples.tolist()
    assert first.pit_seed.tolist() == second.pit_seed.tolist()
    assert first.mae.tolist() != second.mae.tolist()


def test_calendar_and_copy_isolation():
    observed = series()
    original = observed.copy()
    model = Spy(mutate=True)
    rows = run_backtest_suite({"a/b": observed}, {"last_value": model}, config())
    assert len(rows) == 4
    assert set(rows.context_end) == {"2022-02-28", "2022-03-07"}
    assert set(rows.target_end) == {"2022-03-03", "2022-03-07", "2022-03-10", "2022-03-14"}
    pd.testing.assert_series_equal(observed, original)
    assert all(not (context == 999).any() for context in model.contexts)


def test_failures_are_not_silently_dropped():
    class Failing(Spy):
        def forecast(self, *args):
            raise RuntimeError("fit failed")

    with pytest.raises(RuntimeError, match="fit failed"):
        run_backtest_suite({"a/b": series()}, {"last_value": Failing()}, config())


@pytest.mark.parametrize(
    "overrides",
    [
        {"cutoffs": ("2022-03-01", "2022-03-02")},
        {"horizons": (7, 3)},
        {"cutoffs": ()},
        {"horizons": ()},
        {"quantile_levels": (0.9, 0.1)},
    ],
)
def test_invalid_calendar_or_quantiles_rejected(overrides):
    with pytest.raises(ValueError):
        config(**overrides)


def test_missing_dates_endpoints_and_short_context_rejected():
    model = {"last_value": Spy()}
    with pytest.raises(ValueError, match="contiguous"):
        run_backtest_suite({"a/b": series().iloc[::2]}, model, config())
    with pytest.raises(ValueError, match="endpoint"):
        run_backtest_suite({"a/b": series(), "c/d": series().iloc[:-1]}, model, config())
    with pytest.raises(ValueError, match="incomplete"):
        run_backtest_suite({"a/b": series()}, model, config(min_context_days=70))


def test_summary_counts_windows_and_defined_scores():
    rows = run_backtest_suite({"a/b": series()}, {"last_value": Spy()}, config())
    rows["wql"] = np.nan
    summary = summarize_backtest(rows)
    assert summary.n_windows.tolist() == [2, 2]
    assert summary.n_repos.tolist() == [1, 1]
    assert summary.wql_n_valid.tolist() == [0, 0]
    assert summary.wql.isna().all()

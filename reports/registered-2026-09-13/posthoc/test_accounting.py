"""Offline checks of post-hoc accounting identities and aggregation boundaries."""

import numpy as np
import pandas as pd
import pytest
from accounting import LEVELS, PARTS, VALUES, contribution_curves, decompose, pair_repositories


def test_known_zero_over_under_and_tie_accounting():
    # A degenerate forecast at 2 has QScore9 equal to absolute error.
    result, deciles = decompose([0, 1, 3, 2], np.full((4, 9), 2.0), LEVELS)
    assert result["qscore9"] == pytest.approx(1)
    assert result["zero"] == pytest.approx(0.5)
    assert result["positive_over"] == pytest.approx(0.25)
    assert result["positive_under"] == pytest.approx(0.25)
    assert result["positive_conditional_mean"] == pytest.approx(2 / 3)
    for name in VALUES:
        assert sum(deciles[name]) == pytest.approx(result[name])


@pytest.mark.parametrize("actual", [0, 4])
def test_empty_partition_is_undefined_without_changing_unconditional_loss(actual):
    result, _ = decompose([actual, actual], np.full((2, 9), 2.0), LEVELS)
    empty = "positive" if actual == 0 else "zero"
    assert result[empty] == 0
    assert np.isnan(result[empty + "_conditional_mean"])
    assert result["qscore9"] == pytest.approx(sum(result[p] for p in PARTS))


def test_extra_native_tails_do_not_enter_decile_accounting():
    levels = np.r_[0.025, LEVELS, 0.975]
    quantiles = np.array([[0, *range(1, 10), 1e8]], dtype=float)
    first, _ = decompose([3], quantiles, levels)
    second, _ = decompose([3], quantiles[:, 1:-1], LEVELS)
    for name in VALUES:
        assert first[name] == pytest.approx(second[name])


def test_negative_quantiles_and_missing_decile_support_are_rejected():
    with pytest.raises(ValueError):
        decompose([0], np.full((1, 9), -1), LEVELS)
    with pytest.raises(ValueError):
        decompose([0], np.zeros((1, 8)), LEVELS[1:])


def test_averages_windows_then_repositories_without_weighting_by_target_positives():
    records = []
    for repo_id in [1, 2]:
        for window in [0, 1, 2]:
            for model, magnitude in [
                ("fm", 3 * repo_id),
                ("local_mean_28", 2),
                ("autoets_weekly", 1),
            ]:
                records.append(
                    {
                        "repo_name": str(repo_id),
                        "repo_id": repo_id,
                        "sampling_stratum": "20-99",
                        "model_name": model,
                        "horizon": 7,
                        "cutoff_date": str(window),
                        "qscore9": magnitude + window,
                        "zero": magnitude,
                        "positive_over": window,
                        "positive_under": 0,
                        "positive": window,
                        "context_mean": repo_id + window,
                        "context_zero_fraction": window / 3,
                    }
                )
    pairs = pair_repositories(pd.DataFrame(records))
    chosen = pairs[pairs.model.eq("fm") & pairs.reference.eq("local_mean_28")]
    assert chosen.n_windows.tolist() == [3, 3]
    assert chosen.qscore9_difference.tolist() == [1, 4]
    assert chosen.qscore9_difference.mean() == 2.5
    assert chosen.context_mean.tolist() == [2, 3]
    assert chosen.zero_difference.mean() + chosen.positive_difference.mean() == 2.5


def test_signed_curve_retains_losses_and_stable_id_ties_and_ends_at_mean():
    pairs = pd.DataFrame(
        {
            "model": ["fm"] * 3,
            "reference": ["ref"] * 3,
            "horizon": [7] * 3,
            "repo_id": [9, 5, 2],
            **{name + "_difference": [-4, 2, 2] for name in VALUES},
        }
    )
    curve = contribution_curves(pairs)
    assert curve.repo_id.tolist() == [9, 2, 5]
    assert curve.cumulative_qscore9_difference.tolist() == pytest.approx([-4 / 3, -2 / 3, 0])
    assert curve.repository_fraction.iloc[-1] == 1

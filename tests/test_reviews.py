import numpy as np
import pandas as pd
import pytest

from pulsegraph.evaluation.calibration import compute_pit_histogram
from pulsegraph.evaluation.reviews import (
    Comparison,
    benjamini_hochberg,
    review_censoring,
    review_cluster_inference,
    review_local_mean_lookbacks,
    review_scale,
)


def results():
    return pd.DataFrame(
        [
            {
                "repo_name": f"repo/{repo}",
                "horizon": 7,
                "cutoff_date": cutoff,
                "stratum": "all",
                "model_name": model,
                "mae": repo + value + offset,
            }
            for repo in range(1, 7)
            for cutoff, offset in (("2022-03-01", 1), ("2022-03-08", 3))
            for model, value in (("candidate", 1), ("reference", 2))
        ]
    )


def infer(frame, **overrides):
    options = dict(
        comparisons=[Comparison("candidate", "reference", 7, "all")],
        declared_count=1,
        metric="mae",
        seed=42,
        n_bootstrap=200,
        confidence=0.95,
    )
    return review_cluster_inference(frame, **(options | overrides))


def test_repository_bootstrap_preserves_pairing_and_equal_repository_weight():
    first = infer(results())
    assert first.mean_diff.tolist() == [-1]
    assert first.n_repos.tolist() == [6]
    assert first.mean_diff_ci_low.tolist() == [-1]
    assert first.mean_diff_ci_high.tolist() == [-1]
    copied = results().assign(cutoff_date=lambda frame: frame.cutoff_date.str.replace("03-", "04-"))
    second = infer(pd.concat([results(), copied], ignore_index=True))
    pd.testing.assert_frame_equal(first, second)


def test_all_zero_paired_differences_produce_p_one():
    frame = results()
    frame.loc[frame.model_name.eq("candidate"), "mae"] += 1
    assert infer(frame).wilcoxon_p_bh.tolist() == [1]


def test_declared_comparison_family_cannot_shrink_or_silently_drop_missing_pairs():
    with pytest.raises(ValueError, match="declared count"):
        infer(results(), declared_count=2)
    with pytest.raises(ValueError, match="every window"):
        infer(results().iloc[1:])
    with pytest.raises(ValueError):
        infer(results(), comparisons=[Comparison("missing", "reference", 7, "all")])


def test_bh_adjustment_matches_known_values_and_rejects_missing_tests():
    np.testing.assert_allclose(benjamini_hochberg([0.01, 0.04, 0.03]), [0.03, 0.04, 0.04])
    with pytest.raises(ValueError):
        benjamini_hochberg([0.01, np.nan])


def test_scale_review_uses_explicit_reference_and_counts_undefined_skill():
    output = review_scale(results(), reference="reference", metric="mae")
    assert output.repo_win_rate.tolist() == [1]
    assert output.mean_gain.tolist() == [1]
    assert output.n_defined_skill.tolist() == [6]
    frame = results().assign(mae=0)
    output = review_scale(frame, reference="reference", metric="mae")
    assert output.n_defined_skill.tolist() == [0]
    assert output.mean_skill.isna().all()


def test_lookback_review_does_not_add_or_fit_new_models():
    with pytest.raises(ValueError, match="absent"):
        review_local_mean_lookbacks(results(), lookbacks=[14, 28])


def test_censoring_uses_observed_endpoint_even_for_all_zero_repositories():
    calendar = pd.date_range("2022-01-01", periods=7)
    output = review_censoring(
        {
            "a/b": pd.Series([0, 0, 1, 0, 0, 0, 0], index=calendar),
            "c/d": pd.Series(np.zeros(7), index=calendar),
        }
    )
    assert output.trailing_zero_days.tolist() == [4, 7]
    assert output.leading_zero_days.tolist() == [2, 7]
    assert output.observation_end.tolist() == ["2022-01-07"] * 2


def test_descriptive_pit_histogram_includes_endpoints_and_rejects_missing_values():
    fractions, _ = compute_pit_histogram([[0, 0.5, 1]], n_bins=2)
    np.testing.assert_allclose(fractions, [1 / 3, 2 / 3])
    for values in ([], [[]], [[np.nan]], [[-0.1]]):
        with pytest.raises(ValueError):
            compute_pit_histogram(values)

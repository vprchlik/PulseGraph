import numpy as np
import pandas as pd
import pytest

from pulsegraph.data.ingest import aggregate_star_timestamps
from pulsegraph.data.loader import (
    build_dataset_for_forecasting,
    generate_synthetic_data,
    prepare_star_series,
)


def sparse():
    return pd.DataFrame({"repo_name": ["a/b"], "event_date": ["2022-01-03"], "stars": [3]})


def prepare(frame=None, **kwargs):
    options = dict(
        observation_start="2022-01-01", observation_end="2022-01-07", coverage_complete=True
    )
    return prepare_star_series(sparse() if frame is None else frame, "a/b", **(options | kwargs))


def test_leading_internal_and_trailing_zeros_are_preserved():
    series = prepare()
    assert series.tolist() == [0, 0, 3, 0, 0, 0, 0]
    assert series.index[-1] == pd.Timestamp("2022-01-07")


def test_all_zero_manifest_repository_is_retained():
    empty = sparse().iloc[:0]
    assert prepare(empty).tolist() == [0] * 7
    manifest = pd.DataFrame(
        {"repo_name": ["a/b"], "observation_start": ["2022-01-01"], "coverage_complete": [True]}
    )
    dataset = build_dataset_for_forecasting(empty, manifest, observation_end="2022-01-07")
    assert len(dataset["a/b"]) == 7


@pytest.mark.parametrize("complete", [False, None, "true", 1])
def test_missing_coverage_cannot_be_treated_as_zero(complete):
    with pytest.raises(ValueError, match="coverage"):
        prepare(coverage_complete=complete)


@pytest.mark.parametrize("count", [-1, np.nan, np.inf, 0.5])
def test_invalid_counts_rejected(count):
    with pytest.raises(ValueError):
        prepare(sparse().assign(stars=count))


def test_duplicate_days_and_out_of_interval_events_rejected():
    with pytest.raises(ValueError, match="Duplicate"):
        prepare(pd.concat([sparse(), sparse()]))
    with pytest.raises(ValueError, match="outside"):
        prepare(observation_start="2022-01-04")


def test_history_eligibility_uses_observation_days():
    assert prepare(min_history_days=8) is None
    assert prepare(min_history_days=7) is not None


def test_synthetic_data_reproducible_and_dataset_complete():
    first = generate_synthetic_data(n_repos=3, n_days=100, seed=42)
    pd.testing.assert_frame_equal(first, generate_synthetic_data(n_repos=3, n_days=100, seed=42))
    manifest = pd.DataFrame(
        {
            "repo_name": sorted(first.repo_name.unique()),
            "observation_start": "2022-01-01",
            "coverage_complete": True,
        }
    )
    dataset = build_dataset_for_forecasting(first, manifest, observation_end="2022-04-10")
    assert len(dataset) == 3
    assert {len(series) for series in dataset.values()} == {100}


def test_timestamp_aggregation_uses_utc_and_explicit_endpoint():
    frame = aggregate_star_timestamps(
        {"a/b": ["2022-01-01T23:30:00-02:00", "2022-01-02T03:00:00Z", "2022-01-03T03:00:00Z"]},
        observation_end="2022-01-02",
    )
    assert frame.stars.tolist() == [2]
    assert frame.event_date.tolist() == [pd.Timestamp("2022-01-02")]
    with pytest.raises(ValueError, match="timezone"):
        aggregate_star_timestamps({"a/b": ["2022-01-01"]}, observation_end="2022-01-02")

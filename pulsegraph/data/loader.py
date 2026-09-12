"""Daily counts on explicitly observed UTC calendars.

Missing event rows mean zero only after the caller has confirmed complete
coverage of the requested interval. Never infer that interval from star dates.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from pulsegraph.random import validate_seed
from pulsegraph.validation import counts, positive_int, utc_day


def load_daily_signals(path: Path) -> pd.DataFrame:
    return validate_signals(pd.read_parquet(path))


def validate_signals(signals: pd.DataFrame) -> pd.DataFrame:
    required = {"repo_name", "event_date", "stars"}
    if not required.issubset(signals.columns):
        raise ValueError(f"Daily counts require columns {sorted(required)}")
    frame = signals.loc[:, ["repo_name", "event_date", "stars"]].copy()
    if (
        frame.repo_name.isna().any()
        or not frame.repo_name.map(
            lambda value: isinstance(value, str) and bool(value.strip())
        ).all()
    ):
        raise ValueError("Repository names must be nonempty strings")
    frame["event_date"] = pd.to_datetime(frame.event_date, utc=True).dt.tz_localize(None)
    if (
        frame.event_date.isna().any()
        or not frame.event_date.eq(frame.event_date.dt.normalize()).all()
    ):
        raise ValueError("Daily counts must use whole UTC dates")
    values = counts(frame.stars, allow_empty=True)
    if not np.equal(values, np.floor(values)).all():
        raise ValueError("Daily star counts must be integers")
    if frame.duplicated(["repo_name", "event_date"]).any():
        raise ValueError("Duplicate repository/day rows; aggregate events before loading")
    frame["stars"] = values
    return frame.sort_values(["repo_name", "event_date"]).reset_index(drop=True)


def prepare_star_series(
    signals_df: pd.DataFrame,
    repo_name: str,
    *,
    observation_start,
    observation_end,
    coverage_complete: bool,
    min_history_days: int = 1,
) -> pd.Series | None:
    positive_int(min_history_days, "min_history_days")
    if not isinstance(coverage_complete, (bool, np.bool_)) or not coverage_complete:
        raise ValueError("Complete observation coverage is required before zero filling")
    start, end = utc_day(observation_start), utc_day(observation_end)
    if start > end:
        raise ValueError("Observation start must not follow observation end")
    frame = validate_signals(signals_df)
    selected = frame.loc[frame.repo_name.eq(repo_name)].set_index("event_date").stars
    if ((selected.index < start) | (selected.index > end)).any():
        raise ValueError(f"Counts for {repo_name} lie outside its observation interval")
    calendar = pd.date_range(start, end, freq="D", name="date")
    series = selected.reindex(calendar, fill_value=0.0).astype(np.float64)
    series.name = "stars"
    return series if len(series) >= min_history_days else None


def build_dataset_for_forecasting(
    signals_df: pd.DataFrame,
    manifest: pd.DataFrame,
    *,
    observation_end,
    min_history_days: int = 1,
) -> dict[str, pd.Series]:
    required = {"repo_name", "observation_start", "coverage_complete"}
    if manifest.empty or not required.issubset(manifest.columns):
        raise ValueError(f"A nonempty manifest requires {sorted(required)}")
    if manifest.repo_name.isna().any() or manifest.repo_name.duplicated().any():
        raise ValueError("Manifest repository names must be present and unique")
    frame = validate_signals(signals_df)
    if not set(frame.repo_name).issubset(set(manifest.repo_name)):
        raise ValueError("Daily counts contain repositories outside the manifest")
    dataset = {}
    for row in manifest.sort_values("repo_name").itertuples(index=False):
        series = prepare_star_series(
            frame,
            row.repo_name,
            observation_start=row.observation_start,
            observation_end=observation_end,
            coverage_complete=row.coverage_complete,
            min_history_days=min_history_days,
        )
        if series is None:
            raise ValueError(f"Manifest repository {row.repo_name} has insufficient history")
        dataset[row.repo_name] = series
    return dataset


def generate_synthetic_data(
    *, n_repos: int, n_days: int, seed: int, start="2022-01-01"
) -> pd.DataFrame:
    """Seeded synthetic counts for software checks, not experimental targets."""
    positive_int(n_repos, "n_repos")
    positive_int(n_days, "n_days")
    rng = np.random.default_rng(validate_seed(seed))
    dates = pd.date_range(utc_day(start), periods=n_days, freq="D")
    records = []
    for repo in range(n_repos):
        rate = rng.exponential(5)
        values = rng.poisson(rate, n_days)
        for _ in range(rng.poisson(3)):
            peak = rng.integers(0, n_days)
            end = min(peak + int(rng.integers(1, 14)), n_days)
            values[peak:end] += (
                rng.exponential(max(rate, 1) * 10) * np.exp(-np.arange(end - peak) * 0.3)
            ).astype(int)
        records.extend(
            {"repo_name": f"synthetic/repo-{repo:04d}", "event_date": day, "stars": int(value)}
            for day, value in zip(dates, values, strict=True)
        )
    return pd.DataFrame(records)

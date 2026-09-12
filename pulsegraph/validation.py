"""Input checks shared by data construction, models and evaluation."""

import numpy as np
import pandas as pd


def positive_int(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


def counts(values, *, name: str = "counts", allow_empty: bool = False) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1 or (not allow_empty and not array.size):
        raise ValueError(f"{name} must be a nonempty one-dimensional array")
    if not np.isfinite(array).all() or (array < 0).any():
        raise ValueError(f"{name} must be finite and nonnegative")
    return array.copy()


def utc_day(value) -> pd.Timestamp:
    day = pd.Timestamp(value)
    if pd.isna(day):
        raise ValueError("Observation dates cannot be missing")
    if day.tzinfo is not None:
        day = day.tz_convert("UTC").tz_localize(None)
    if day != day.normalize():
        raise ValueError("Observation boundaries must be whole UTC dates")
    return day


def daily_series(series: pd.Series) -> None:
    if not isinstance(series, pd.Series) or not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("Expected a Series with a daily DatetimeIndex")
    counts(series)
    if series.index.tz is not None or series.index.hasnans:
        raise ValueError("Dates must be timezone-naive UTC days without missing dates")
    expected = pd.date_range(utc_day(series.index[0]), periods=len(series), freq="D")
    if not series.index.equals(expected):
        raise ValueError("Dates must be unique, ordered and contiguous daily observations")

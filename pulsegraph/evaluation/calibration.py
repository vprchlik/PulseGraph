"""Descriptive randomized-PIT histograms; no IID calibration significance claim."""

import numpy as np
import pandas as pd

from pulsegraph.validation import positive_int


def compute_pit_histogram(pit_values, *, n_bins: int = 10):
    positive_int(n_bins, "n_bins")
    if not pit_values:
        raise ValueError("No PIT values supplied")
    values = np.concatenate([np.asarray(value, dtype=float) for value in pit_values])
    if not values.size or not np.isfinite(values).all() or ((values < 0) | (values > 1)).any():
        raise ValueError("PIT values must be nonempty, finite and in [0, 1]")
    bins, edges = np.histogram(values, bins=n_bins, range=(0, 1))
    return bins / bins.sum(), edges


def calibration_summary(results: pd.DataFrame, *, n_bins: int = 10) -> pd.DataFrame:
    rows = []
    for (model, horizon, stratum), group in results.groupby(["model_name", "horizon", "stratum"]):
        arrays = group.loc[group.pit_method.eq("randomized_empirical"), "pit_values"].tolist()
        if not arrays:
            continue
        histogram, edges = compute_pit_histogram(arrays, n_bins=n_bins)
        for low, high, fraction in zip(edges[:-1], edges[1:], histogram, strict=True):
            rows.append(
                {
                    "model_name": model,
                    "horizon": horizon,
                    "stratum": stratum,
                    "bin_lower": low,
                    "bin_upper": high,
                    "fraction": fraction,
                    "n_forecasts": len(arrays),
                    "interpretation": "descriptive_only",
                }
            )
    return pd.DataFrame(rows)

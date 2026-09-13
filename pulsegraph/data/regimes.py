"""Registered context-only labels; cutoff is the first forecasted UTC date."""

import pandas as pd

from pulsegraph.validation import daily_series, utc_day

INACTIVE_DAYS = 28
SURGE_DAYS = 7
REFERENCE_DAYS = 28
SURGE_MINIMUM = 7
SURGE_MULTIPLIER = 3


def assert_eligibility_precedes_cutoff(creation, cutoff):
    if utc_day(creation) + pd.Timedelta(days=89) >= utc_day(cutoff):
        raise ValueError("Eligibility must satisfy b+89 < c")


def context_regime(context: pd.Series) -> str:
    daily_series(context)
    if len(context) < SURGE_DAYS + REFERENCE_DAYS:
        raise ValueError("Regime labeling needs at least 35 context days")
    if context.iloc[-INACTIVE_DAYS:].sum() == 0:
        return "Inactive recently"
    recent = float(context.iloc[-SURGE_DAYS:].sum())
    reference = float(context.iloc[-(SURGE_DAYS + REFERENCE_DAYS) : -SURGE_DAYS].sum())
    if recent >= SURGE_MINIMUM and recent / SURGE_DAYS >= SURGE_MULTIPLIER * max(
        reference / REFERENCE_DAYS, 1
    ):
        return "Recent surge"
    return "Other active"

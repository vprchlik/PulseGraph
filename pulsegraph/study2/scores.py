"""Equal-day QScore9 and exact zero/positive over/under accounting for Study 2."""

from collections import Counter

import numpy as np

from pulsegraph.forecast.output import COMMON_QUANTILES
from pulsegraph.study2.distributions import CountLaw, discrete_crps

# The certification failure of discrete_crps; every other error still stops the run.
UNCERTIFIED_ERROR = "CRPS residual bound not attained within the registered work limit"
CRPS_UNCERTIFIED = "crps_bound_not_certified"
NO_DISTRIBUTION = "no_count_distribution"


def accounting(target, deciles):
    y, q = np.asarray(target, float), np.asarray(deciles, float)
    if (
        y.ndim != 1
        or not len(y)
        or q.shape != (len(y), 9)
        or not np.isfinite(q).all()
        or not np.isfinite(y).all()
        or (q < 0).any()
        or (y < 0).any()
        or (np.diff(q, axis=1) < 0).any()
        or (y != np.floor(y)).any()
    ):
        raise ValueError("Invalid scoring arrays")
    error = y[:, None] - q
    loss = 2 * np.maximum(
        np.array(COMMON_QUANTILES) * error, (np.array(COMMON_QUANTILES) - 1) * error
    )
    zero = y[:, None] == 0
    parts = dict(
        zero=float(np.mean(np.where(zero, loss, 0))),
        positive_over=float(np.mean(np.where(~zero & (error < 0), loss, 0))),
        positive_under=float(np.mean(np.where(~zero & (error >= 0), loss, 0))),
    )
    return dict(
        qscore9=float(loss.mean()),
        contributions=parts,
        residual=float(loss.mean() - sum(parts.values())),
        n_zero=int((y == 0).sum()),
        n_positive=int((y > 0).sum()),
    )


def certified_crps(laws, target):
    """Certified discrete CRPS for every day, or None once one day is not certified.

    PROTOCOL.md, dated addition of 2026-10-15, item 5: the forecast's CRPS is then unavailable;
    the work limit, tolerance and certification are unchanged and nothing is truncated.
    """
    values = []
    for law, y in zip(laws, target, strict=True):
        try:
            values.append(discrete_crps(law, y))
        except ValueError as error:
            if str(error) != UNCERTIFIED_ERROR:
                raise
            return None
    return values


def score(target, forecast, context):
    result = accounting(target, forecast["deciles"])
    result["context_scaled_qscore9"] = result["qscore9"] / max(1.0, float(np.mean(context)))
    result.update(
        occurrence_brier=None,
        discrete_crps=None,
        crps_max_residual_bound=None,
        crps_unavailable_reason=NO_DISTRIBUTION,
    )
    if forecast.get("distributions") is not None:
        if len(forecast["distributions"]) != len(target):
            raise ValueError("Distribution/target length mismatch")
        laws = [CountLaw(s) for s in forecast["distributions"]]
        values = certified_crps(laws, target)
        result["occurrence_brier"] = float(
            np.mean([(law.sf(0) - (y > 0)) ** 2 for law, y in zip(laws, target, strict=True)])
        )
        if values is None:
            result.update(crps_unavailable_reason=CRPS_UNCERTIFIED, crps_last_k=None)
        else:
            result["discrete_crps"] = float(np.mean([v["value"] for v in values]))
            result["crps_max_residual_bound"] = max(v["residual_bound"] for v in values)
            result["crps_last_k"] = max(v["last_k"] for v in values)
            result["crps_unavailable_reason"] = None
    return result


def crps_denominators(scores):
    """Valid CRPS denominators: all forecasts, those with a count distribution, those certified,
    and every unavailable one by its reason."""
    reasons = Counter(s["crps_unavailable_reason"] for s in scores)
    return dict(
        forecasts=len(scores),
        with_count_distribution=len(scores) - reasons[NO_DISTRIBUTION],
        certified=sum(s["discrete_crps"] is not None for s in scores),
        unavailable={reason: reasons[reason] for reason in sorted(set(reasons) - {None})},
    )

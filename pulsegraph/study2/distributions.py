"""Registered integer laws and analytic completion, with bounded discrete CRPS."""

from dataclasses import dataclass

import numpy as np
from scipy.stats import nbinom, poisson


@dataclass
class CountLaw:
    """Serializable count law. Survival calculations avoid subtracting tiny tails from one."""

    spec: dict

    def sf(self, k):
        k = np.floor(np.asarray(k, float))
        s = self.spec
        kind = s["kind"]
        if kind == "point":
            return (k < s["value"]).astype(float)
        if kind == "poisson":
            return poisson.sf(k - s.get("shift", 0), s["mu"])
        if kind == "nb":
            return nbinom.sf(k - s.get("shift", 0), s["shape"], s["probability"])
        if kind == "empirical":
            values = np.asarray(s["values"])
            return np.mean(values[:, None] > k.ravel(), axis=0).reshape(k.shape)
        if kind == "completed":
            knots = np.r_[0.0, s["deciles"]]
            levels = np.arange(10) / 10
            x = k + 0.5
            index = np.searchsorted(knots, x, side="left")
            right = np.clip(index, 1, 9)
            left = right - 1
            width = knots[right] - knots[left]
            with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
                u = levels[left] + 0.1 * (x - knots[left]) / np.where(width > 0, width, 1)
                tail = 0.1 * np.exp(-np.maximum(0, x - knots[-1]) / s["tail_scale"])
            return np.where(k < 0, 1.0, np.where(index > 9, tail, np.clip(1 - u, 0, 1)))
        if kind == "positive":
            base = CountLaw(s["base"])
            return np.where(k < 1, 1.0, base.sf(k) / base.sf(0))
        if kind == "hurdle":
            return np.where(k < 0, 1.0, s["p"] * CountLaw(s["positive"]).sf(k))
        raise ValueError("Unknown count distribution")

    def cdf(self, k):
        return 1 - self.sf(k)

    def ppf(self, probabilities):
        p = np.asarray(probabilities, float)
        if not np.isfinite(p).all() or (p <= 0).any() or (p >= 1).any():
            raise ValueError("Quantile probabilities must be strictly between zero and one")
        low = np.full(p.shape, -1, dtype=np.int64)
        high = np.ones(p.shape, dtype=np.int64)
        for _ in range(53):
            mask = self.sf(high) > (1 - p)
            if not mask.any():
                break
            high[mask] *= 2
        else:
            raise ValueError("Count quantile exceeds exact integer range")
        while np.any(high - low > 1):
            mid = (high + low) // 2
            below = self.sf(mid) > (1 - p)
            low = np.where(below, mid, low)
            high = np.where(below, high, mid)
        return high.astype(float)

    def tail_bound(self, last):
        """Upper bound on sum_{k>last} SF(k)^2 for last >= observed y.

        For count families use SF(last) * E[Y 1(Y>last)], which bounds
        SF(last) * E[(Y-last-1)+]. Completed tails are an exact geometric sum.
        """
        s, k = self.spec, int(last)
        kind = s["kind"]
        if kind == "point":
            return float(max(0, s["value"] - k - 1))
        if kind == "empirical":
            top = max(s["values"])
            return float(np.sum(self.sf(np.arange(k + 1, top + 1)) ** 2)) if top > k else 0.0
        if kind == "completed":
            q, scale = s["deciles"][-1], s["tail_scale"]
            if k + 1.5 < q:
                return float("inf")
            return float(0.01 * np.exp(-2 * (k + 1.5 - q) / scale) / -np.expm1(-2 / scale))
        if kind == "positive":
            base = CountLaw(s["base"])
            return float(base.tail_bound(k) / base.sf(0) ** 2)
        if kind == "hurdle":
            return s["p"] ** 2 * CountLaw(s["positive"]).tail_bound(k)
        shift = s.get("shift", 0)
        m = k - shift
        if kind == "poisson":
            moment = s["mu"] * poisson.sf(m - 1, s["mu"])
        elif kind == "nb":
            mean = s["shape"] * (1 - s["probability"]) / s["probability"]
            moment = mean * nbinom.sf(m - 1, s["shape"] + 1, s["probability"])
        else:
            raise ValueError("Unknown tail law")
        moment += shift * self.sf(k)
        return float(self.sf(k) * moment)


def complete(deciles):
    q = np.asarray(deciles, float)
    if q.shape != (9,) or not np.isfinite(q).all() or (q < 0).any() or (np.diff(q) < 0).any():
        raise ValueError("Completion requires nine repaired deciles")
    return CountLaw(
        dict(
            kind="completed",
            deciles=q.tolist(),
            tail_scale=max(1.0, q[-1] - q[-2]),
            integer_mapping="floor(Q(U)+0.5)",
            tail="exponential_quantile",
        )
    )


def fm_hurdle(base, p):
    if not 0 <= p <= 1:
        raise ValueError("Invalid occurrence probability")
    # The completed law's exponential tail remains positive even on an all-zero context.
    survival = float(base.sf(0))
    positive = (
        dict(kind="positive", base=base.spec) if survival > 0 else dict(kind="point", value=1)
    )
    return CountLaw(
        dict(
            kind="hurdle",
            p=p,
            positive=positive,
            fallback="F0_equals_one" if survival == 0 else None,
        )
    )


def discrete_crps(law, y, *, tolerance=1e-8, max_k=1000000):
    if not np.isfinite(y) or y < 0 or y != int(y):
        raise ValueError("CRPS requires a nonnegative integer target")
    if tolerance <= 0 or max_k < 0:
        raise ValueError("Invalid CRPS numerical settings")
    total, start, bound = 0.0, 0, float("inf")
    while start <= max_k:
        stop = min(max_k, start + 1023)
        k = np.arange(start, stop + 1)
        survival = law.sf(k)
        total += float(np.sum(np.where(k < y, 1 - survival, survival) ** 2))
        if stop >= y:
            bound = law.tail_bound(stop)
            if bound < tolerance:
                return dict(value=total, residual_bound=bound, last_k=stop)
        start = stop + 1
    raise ValueError("CRPS residual bound not attained within the registered work limit")

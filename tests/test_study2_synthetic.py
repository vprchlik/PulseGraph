import numpy as np
import pytest
from scipy.stats import poisson

from pulsegraph.config import ROOT_DIR
from pulsegraph.forecast.output import COMMON_QUANTILES
from pulsegraph.provenance import read_json
from pulsegraph.study2.synthetic import (
    cells,
    generate,
    grid_manifest,
    oracle_forecast,
    oracle_laws,
    streams,
)


def test_full_grid_and_independent_replicate_streams():
    manifest = grid_manifest()
    assert manifest == read_json(ROOT_DIR / "study/study2/grid_manifest.json")
    assert len(cells()) == 18 and len(manifest["series"]) == 540
    seeds = [s[k] for s in manifest["streams"] for k in ("occurrence_seed", "size_seed")]
    assert len(set(seeds)) == 60
    occurrence, size = streams(0)
    assert not np.array_equal(occurrence, size)
    assert not np.array_equal(occurrence, streams(1)[0])
    assert np.array_equal(occurrence, streams(0)[0])


def test_common_random_numbers_and_positive_sizes():
    base = next(
        c
        for c in cells()
        if c["zero_probability"] == 0.8 and c["positive_mean"] == 1 and c["persistence"] == 0.8
    )
    bigger = {**base, "cell_id": "cell09", "positive_mean": 5}
    assert bigger in cells()
    a, b = generate(base, 0), generate(bigger, 0)
    assert np.array_equal(a > 0, b > 0)
    assert np.all(b >= a) and np.all(a <= 1)
    for cell in cells():
        y = generate(cell, 3)
        assert y.shape == (270,) and np.all(y >= 0)


def test_oracle_uses_only_last_observed_state_and_known_parameters():
    cell = cells()[1]
    context = np.array([0, 2, 0, 1])
    laws = oracle_laws(cell, context, 7)
    assert laws[0].sf(0) == pytest.approx(0.8 + 0.8 * (1 - 0.8))
    assert laws[-1].sf(0) == pytest.approx(0.8 + 0.8**7 * (1 - 0.8))
    assert [law.spec for law in laws] == [law.spec for law in oracle_laws(cell, [99, 0, 1], 7)]


@pytest.mark.parametrize("cell", cells())
def test_oracle_quantiles_minimize_expected_pinball(cell):
    law = oracle_laws(cell, [0, 1], 7)[0]
    support = np.arange(201)
    mass = law.cdf(support) - law.cdf(support - 1)
    assert mass.sum() == pytest.approx(1.0, abs=1e-12)
    for tau in (0.1, 0.5, 0.9):
        optimum = int(law.ppf([tau])[0])
        losses = []
        for q in range(0, 80):
            error = support - q
            losses.append(np.dot(mass, np.maximum(tau * error, (tau - 1) * error)))
        assert losses[optimum] <= min(losses) + 1e-12


@pytest.mark.parametrize("cell", cells())
def test_oracle_matches_known_law_inverts_and_minimizes_known_expected_pinball(cell):
    # The known law is built from the generator's parameters with scipy, not through CountLaw.
    pi, rho, mu = 1 - cell["zero_probability"], cell["persistence"], cell["positive_mean"]
    support = np.arange(301)
    error = support[:, None] - support[None, :]
    pinball = {tau: np.maximum(tau * error, (tau - 1) * error) for tau in COMMON_QUANTILES}
    levels = np.linspace(0.005, 0.995, 199)
    for context in ([1, 0], [0, 3]):
        forecast = oracle_forecast(f"{cell['cell_id']}/rep00", context, 30)
        for lead, law in enumerate(oracle_laws(cell, context, 30), start=1):
            p = pi + rho**lead * (float(context[-1] > 0) - pi)
            known = np.r_[1 - p, p * poisson.pmf(support[:-1], mu - 1)]
            known_cdf = np.cumsum(known)
            assert known.sum() == pytest.approx(1, abs=1e-12)
            assert law.cdf(-1) == 0
            assert np.allclose(law.cdf(support), known_cdf, rtol=0, atol=1e-12)
            q = law.ppf(levels).astype(int)
            assert np.all(known_cdf[q] >= levels - 1e-12)
            assert np.all((q == 0) | (known_cdf[np.maximum(q - 1, 0)] < levels + 1e-12))
            deciles = np.asarray(forecast["deciles"][lead - 1])
            assert np.array_equal(deciles, law.ppf(COMMON_QUANTILES))
            for tau, value in zip(COMMON_QUANTILES, deciles.astype(int)):
                losses = known @ pinball[tau]
                assert losses[value] <= losses.min() + 1e-12

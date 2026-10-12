import numpy as np
import pytest

from pulsegraph.config import ROOT_DIR
from pulsegraph.provenance import read_json
from pulsegraph.study2.synthetic import cells, generate, grid_manifest, oracle_laws, streams


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

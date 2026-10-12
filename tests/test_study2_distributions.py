import numpy as np
import pytest
from scipy.stats import poisson

from pulsegraph.study2.distributions import CountLaw, complete, discrete_crps, fm_hurdle
from pulsegraph.study2.models import count_laws, occurrence
from pulsegraph.study2.scores import accounting, score


@pytest.mark.parametrize(
    "deciles", [np.zeros(9), np.arange(9), np.full(9, 0.5), np.arange(9) * 100]
)
def test_completion_mass_monotonicity_rounding_and_inversion(deciles):
    law = complete(deciles)
    k = np.arange(-1, 20001)
    cdf = law.cdf(k)
    assert cdf[0] == 0 and cdf[-1] == pytest.approx(1)
    assert np.min(np.diff(cdf)) >= 0
    p = np.linspace(0.001, 0.999, 501)
    q = law.ppf(p)
    assert np.all(law.cdf(q) + 1e-14 >= p)
    assert np.all(law.cdf(q - 1) < p + 1e-14)
    assert np.sum(np.diff(cdf)) == pytest.approx(1)
    if np.all(deciles == 0.5):
        # The plateau at Q=.5 maps to count one, not zero.
        assert law.cdf(0) == pytest.approx(0.1)


def test_tail_formula_and_fm_positive_rule_do_not_force_ties():
    law = complete(np.zeros(9))
    assert law.sf(2) == pytest.approx(0.1 * np.exp(-2.5))
    p = occurrence(np.zeros(28))
    wrapped = fm_hurdle(law, p)
    assert wrapped.spec["fallback"] is None
    assert wrapped.sf(1) > 0
    count = count_laws("hurdle_count_28", np.zeros(28), 1)[0]
    assert count.sf(1) == 0
    assert fm_hurdle(CountLaw(dict(kind="point", value=0)), p).spec["fallback"] == "F0_equals_one"


@pytest.mark.parametrize(
    "name", ["poisson_28", "hurdle_count_28", "hurdle_empirical_28", "dynamic_count"]
)
def test_count_limits_and_distributions(name):
    zero = count_laws(name, np.zeros(90), 3)
    assert np.isfinite(zero[0].ppf([0.1, 0.9])).all()
    if name == "poisson_28":
        assert zero[0].cdf(0) == 1
        law = count_laws(name, np.ones(90) * 3, 1)[0]
        assert np.allclose(law.ppf([0.1, 0.5, 0.9]), poisson.ppf([0.1, 0.5, 0.9], 3))
    else:
        assert zero[0].sf(0) == pytest.approx(0.5 / 29)
    laws = count_laws(name, np.tile([0, 0, 2, 5, 1, 0, 4], 15), 30)
    for law in laws:
        assert law.cdf(-1) == 0 and law.cdf(10000) == pytest.approx(1)
        assert np.all(np.diff(law.cdf(np.arange(100))) >= 0)


def test_dynamic_discount_matches_hand_calculation():
    y = np.ones(28) * 2
    laws = count_laws("dynamic_count", y, 2)
    weight = sum(0.98**i for i in range(28))
    a = 0.5 * 0.98**28 + weight
    b = 0.5 * 0.98**28
    assert laws[0].spec["p"] == pytest.approx(a / (a + b))
    assert laws[1].spec["positive"]["shape"] == pytest.approx(0.98 * a)
    assert laws[1].spec["positive"]["probability"] == pytest.approx(0.98 * a / (1 + 0.98 * a))


def test_crps_certified_tail_and_work_failure():
    laws = [
        complete(np.arange(9) * 400),
        CountLaw(dict(kind="nb", shape=0.2, probability=0.003)),
        CountLaw(dict(kind="poisson", mu=100)),
        fm_hurdle(complete(np.zeros(9)), 0.1),
    ]
    for law in laws:
        result = discrete_crps(law, 17)
        k = np.arange(result["last_k"] + 1, result["last_k"] + 100000)
        omitted = float(np.sum(law.sf(k) ** 2))
        assert omitted <= result["residual_bound"] + 1e-15
        assert result["residual_bound"] < 1e-8
    with pytest.raises(ValueError, match="residual"):
        discrete_crps(laws[0], 17, max_k=10)


def test_exact_accounting_includes_zero_and_both_positive_directions():
    y = [0, 1, 100]
    q = np.tile(np.arange(9), (3, 1))
    parts = accounting(y, q)
    assert sum(parts["contributions"].values()) == pytest.approx(parts["qscore9"])
    assert all(v > 0 for v in parts["contributions"].values())
    result = score(y, dict(deciles=q, distributions=None), np.zeros(28))
    assert result["context_scaled_qscore9"] == result["qscore9"]
    assert result["discrete_crps"] is None


def test_model_pool_reuses_each_base_once_and_shares_completed_control():
    from pulsegraph.forecast.negative_binomial import NegativeBinomialForecaster
    from pulsegraph.forecast.output import COMMON_QUANTILES, ForecastOutput
    from pulsegraph.study2.constants import BASELINES, MODEL_PINS, VARIANTS
    from pulsegraph.study2.models import ModelPool

    constructed, calls, released = [], [], []

    class Model:
        def __init__(self, name):
            self.name = name

        def forecast(self, context, horizon, key):
            calls.append((self.name, key))
            if self.name == "nb_local_level_28":
                return NegativeBinomialForecaster(seed=self.seed).forecast(context, horizon, key)
            return ForecastOutput(
                key,
                self.name,
                horizon,
                len(context),
                np.array(COMMON_QUANTILES),
                np.tile(np.arange(9), (horizon, 1)),
            )

    def factory(name, spec):
        constructed.append(name)
        return Model(name)

    with ModelPool(factory=factory, release=lambda m: released.append(m.name)) as pool:
        for key in ("a", "b"):
            output = pool.forecast(np.ones(28), 3, key)
            assert set(output) == set(VARIANTS)
            assert not released
            for model in MODEL_PINS:
                completed = output[model + "_completed"]["distributions"][0]
                positive = output[model + "_hurdle"]["distributions"][0]["positive"]
                assert positive["base"] == completed
    assert constructed == [*MODEL_PINS, *BASELINES[:3]]
    assert len(calls) == 12 and len(released) == 6

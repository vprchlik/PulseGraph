"""Study 2 count baselines and shared-base FM variants; no implicit evaluation."""

from contextlib import ExitStack
from copy import deepcopy
from time import perf_counter

import numpy as np

from pulsegraph.config import ROOT_DIR
from pulsegraph.forecast.output import COMMON_QUANTILES
from pulsegraph.forecast.registered import make_registered_model, release_model
from pulsegraph.provenance import read_json
from pulsegraph.random import derived_seed
from pulsegraph.study2.constants import BASELINES, MODEL_PINS, SEEDS, STUDY3_SEEDS
from pulsegraph.study2.distributions import CountLaw, complete, fm_hurdle


def validate_context(context):
    y = np.asarray(context, float)
    if (
        y.ndim != 1
        or len(y) < 28
        or not np.isfinite(y).all()
        or (y < 0).any()
        or (y != np.floor(y)).any()
    ):
        raise ValueError("At least 28 complete integer context days required")
    return y


def occurrence(context):
    return (float(np.count_nonzero(context[-28:])) + 0.5) / 29


def count_laws(name, context, horizon):
    y = validate_context(context)
    if horizon < 1 or int(horizon) != horizon:
        raise ValueError("Positive integer horizon required")
    recent = y[-28:]
    positive = recent[recent > 0]
    p = occurrence(y)
    if name == "poisson_28":
        mu = float(recent.mean())
        law = CountLaw(dict(kind="poisson", mu=mu))
        return [law] * horizon
    if name in ("hurdle_count_28", "hurdle_empirical_28"):
        fallback = len(positive) < 2
        size = (
            dict(kind="point", value=1)
            if fallback
            else dict(kind="empirical", values=positive.tolist())
            if name == "hurdle_empirical_28"
            else dict(kind="poisson", mu=float((positive - 1).mean()), shift=1)
        )
        law = CountLaw(
            dict(
                kind="hurdle",
                p=p,
                positive=size,
                fallback="fewer_than_two_positives" if fallback else None,
            )
        )
        return [law] * horizon
    if name == "dynamic_count":
        if len(positive) < 2:
            return count_laws("hurdle_count_28", y, horizon)
        a_b = b_b = a_p = b_p = 0.5
        for value in y:
            a_b, b_b, a_p, b_p = (v * 0.98 for v in (a_b, b_b, a_p, b_p))
            a_b += value > 0
            b_b += value == 0
            if value > 0:
                a_p += value - 1
                b_p += 1
        result = []
        for lead in range(horizon):
            discount = 0.98**lead
            size = dict(
                kind="nb",
                shape=float(discount * a_p),
                probability=float(discount * b_p / (1 + discount * b_p)),
                shift=1,
            )
            result.append(
                CountLaw(
                    dict(
                        kind="hurdle",
                        p=float(a_b / (a_b + b_b)),
                        positive=size,
                        discount=0.98,
                        fallback=None,
                    )
                )
            )
        return result
    raise ValueError("Unregistered count baseline")


def law_forecast(laws, metadata=None):
    return dict(
        deciles=[law.ppf(COMMON_QUANTILES).tolist() for law in laws],
        distributions=[law.spec for law in laws],
        metadata=metadata or {},
    )


def dynamic_occurrence(context, horizon):
    """P(Y > 0) of the registered dynamic_count law at each lead, its registered fallback to
    hurdle_count_28 included; the discounted Beta-Bernoulli occurrence is constant over leads."""
    return [float(law.sf(0)) for law in count_laws("dynamic_count", context, horizon)]


def model_size_count(base, count):
    """The model's own completed occurrence 1 - F(0) with a count hurdle's positive law.

    `count` is the saved spec of hurdle_count_28 for the same context: its positive law is
    1 + Poisson(mean(y - 1)) over the last 28 days' positive values, or delta_1 with fewer than
    two of them, and that fallback is recorded.
    """
    if count.get("kind") != "hurdle":
        raise ValueError("The count positive law comes from hurdle_count_28's hurdle")
    return CountLaw(
        dict(
            kind="hurdle",
            p=float(base.sf(0)),
            positive=count["positive"],
            fallback=count["fallback"],
        )
    )


def study3_variants(completed, context, metadata=None):
    """Study 3's two new variants from a model's completed laws (PROTOCOL.md, dated addition of
    2026-10-16, item 7), built from the same saved base forecast as the registered three.

    hurdle_dynamic: the registered FM hurdle (fm_hurdle) with dynamic_count's occurrence at each
    lead in place of the 28-day Jeffreys p; delta_1 only when F(0) = 1.
    occurrence_model_size_count: the completed law's own 1 - F(0) with hurdle_count_28's
    positive law. Neither is fitted or selected on targets.
    """
    horizon = len(completed)
    p_dynamic = dynamic_occurrence(context, horizon)
    count = count_laws("hurdle_count_28", context, 1)[0].spec
    return dict(
        hurdle_dynamic=law_forecast(
            [fm_hurdle(law, p) for law, p in zip(completed, p_dynamic, strict=True)],
            dict(base_metadata=metadata, occurrence=p_dynamic, occurrence_source="dynamic_count"),
        ),
        occurrence_model_size_count=law_forecast(
            [model_size_count(law, count) for law in completed],
            dict(base_metadata=metadata, positive_source="hurdle_count_28"),
        ),
    )


def fm_variants(output, context, *, study3=False):
    q = np.column_stack([output.quantile(t) for t in COMMON_QUANTILES])
    if not all(
        np.any(np.isclose(output.quantile_levels, t, atol=1e-12, rtol=0)) for t in COMMON_QUANTILES
    ):
        raise ValueError("Native FM decile missing; no invented raw tails")
    completed = [complete(row) for row in q]
    p = occurrence(context)
    variants = dict(
        raw=dict(deciles=q.tolist(), distributions=None, metadata=output.metadata),
        completed=law_forecast(completed, dict(base_metadata=output.metadata)),
        hurdle=law_forecast(
            [fm_hurdle(law, p) for law in completed],
            dict(base_metadata=output.metadata, occurrence=p),
        ),
    )
    if study3:
        variants.update(study3_variants(completed, context, output.metadata))
    return variants


class ModelPool:
    def __init__(
        self,
        *,
        prospective=False,
        study3=False,
        factory=make_registered_model,
        release=release_model,
    ):
        if prospective and study3:
            raise ValueError("Study 3 registers no prospective forecasts")
        self.spec = deepcopy(read_json(ROOT_DIR / "study/run_spec.json"))
        self.spec["seeds"]["forecast"] = (
            STUDY3_SEEDS["forecast"]
            if study3
            else SEEDS["prospective"]
            if prospective
            else SEEDS["forecast"]
        )
        # The forecast seeds are derived with the component name of the study they belong to.
        self.study3, self.component = study3, "study3" if study3 else "study2"
        self.factory, self.release = factory, release
        self.models = {}
        self.timings = {}
        self.lifecycle = ExitStack()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.lifecycle.__exit__(*args)

    def forecast(self, context, horizon, key):
        context = validate_context(context)
        if not 1 <= horizon <= 128:
            raise ValueError("Forecast lead count exceeds frozen model support")
        forecasts = {}
        for name in (*MODEL_PINS, *BASELINES):
            started = perf_counter()
            seed = derived_seed(
                self.spec["seeds"]["forecast"], self.component, name, key, horizon, values=context
            )
            if name in BASELINES[3:]:
                forecasts[name] = law_forecast(count_laws(name, context, horizon), dict(seed=seed))
                self.timings[name] = dict(
                    load_seconds=0.0,
                    forecast_seconds=perf_counter() - started,
                    context_days=len(context),
                    leads=horizon,
                )
                continue
            if name not in self.models:
                self.models[name] = self.factory(name, self.spec)
                self.lifecycle.callback(self.release, self.models[name])
            model = self.models[name]
            model.seed = seed
            load_seconds = 0.0
            if self.factory is make_registered_model and name in MODEL_PINS:
                import torch

                torch.manual_seed(seed)
                torch.cuda.manual_seed_all(seed)
                loading = perf_counter()
                getattr(model, "pipeline" if name == "chronos2" else "model")
                load_seconds = perf_counter() - loading
                started = perf_counter()
            output = model.forecast(context, horizon, key)
            if self.factory is make_registered_model and name in MODEL_PINS:
                from pulsegraph.forecast.hardware import memory_snapshot

                memory_snapshot()
            if name in MODEL_PINS:
                forecasts.update(
                    {
                        f"{name}_{v}": f
                        for v, f in fm_variants(output, context, study3=self.study3).items()
                    }
                )
            elif name == "nb_local_level_28":
                m = output.metadata
                law = (
                    CountLaw(dict(kind="point", value=0))
                    if m["mu"] == 0
                    else CountLaw(dict(kind="poisson", mu=m["mu"]))
                    if m["alpha"] == 0
                    else CountLaw(dict(kind="nb", shape=m["size"], probability=m["probability"]))
                )
                forecasts[name] = law_forecast([law] * horizon, m)
            else:
                forecasts[name] = dict(
                    deciles=np.column_stack(
                        [output.quantile(t) for t in COMMON_QUANTILES]
                    ).tolist(),
                    distributions=None,
                    metadata=output.metadata,
                    samples=None if output.samples is None else output.samples.tolist(),
                )
            self.timings[name] = dict(
                load_seconds=load_seconds,
                forecast_seconds=perf_counter() - started,
                context_days=len(context),
                leads=horizon,
            )
        return forecasts

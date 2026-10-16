"""Study 3's two new variants (PROTOCOL.md, dated addition of 2026-10-16, item 7); no model."""

import importlib.util
import json

import numpy as np
import pandas as pd
import pytest
from test_study2_dynamic_occurrence import Output, RegisteredPool
from test_study2_inference import DATES, STRATA, _write_family

import scripts.study2_inference as inference_command
from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.forecast.output import COMMON_QUANTILES
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes
from pulsegraph.random import derived_seed
from pulsegraph.study2.constants import (
    BASELINES,
    MODEL_PINS,
    SEEDS,
    STUDY3_SEEDS,
    STUDY3_VARIANTS,
    VARIANTS,
)
from pulsegraph.study2.declarations import comparisons, specification
from pulsegraph.study2.distributions import CountLaw, complete
from pulsegraph.study2.models import (
    ModelPool,
    count_laws,
    dynamic_occurrence,
    fm_variants,
    model_size_count,
    occurrence,
    study3_variants,
)
from pulsegraph.study2.runner import _evaluate

SCRIPT = ROOT_DIR / "reports/study2-posthoc-dynamic-occurrence/dynamic_occurrence.py"
_spec = importlib.util.spec_from_file_location("dynamic_occurrence_study3", SCRIPT)
dynamic = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dynamic)

TAU = np.asarray(COMMON_QUANTILES)
NEW = ("hurdle_dynamic", "occurrence_model_size_count")


def _contexts():
    """Dense, sparse, all-zero and fewer-than-two-recent-positives contexts of 275 days."""
    rng = np.random.default_rng(3)
    dense = rng.poisson(6.0, 275).astype(float)
    sparse = (rng.random(275) < 0.2) * rng.poisson(3.0, 275).astype(float)
    sparse[-28:][[3, 17]] = [2.0, 5.0]
    zeros = np.zeros(275)
    lonely = rng.poisson(2.0, 275).astype(float)
    lonely[-28:] = 0.0
    lonely[-9] = 4.0
    return dict(dense=dense, sparse=sparse, zeros=zeros, lonely=lonely)


def _output(context, horizon, index=0):
    level = float(np.mean(context[-28:]))
    shape = level * np.linspace(0.1 + 0.1 * index, 1.6 + 0.2 * index, 9)
    return Output(np.floor(np.outer(1 + 0.03 * np.arange(horizon), shape) * 4) / 4)


def _beta_bernoulli(context):
    a, b = 0.5, 0.5
    for value in context:
        a, b = 0.98 * a + (value > 0), 0.98 * b + (value == 0)
    return a / (a + b)


def test_the_wrapper_with_the_jeffreys_p_reproduces_the_registered_hurdle(monkeypatch):
    for name, context in _contexts().items():
        for horizon in (7, 30):
            variants = fm_variants(_output(context, horizon), context, study3=True)
            assert set(variants) == {"raw", "completed", "hurdle", *NEW}
            # Study 2's three are unchanged by the Study 3 flag.
            study2 = fm_variants(_output(context, horizon), context)
            assert {k: variants[k] for k in study2} == study2
            completed = [CountLaw(spec) for spec in variants["completed"]["distributions"]]
            # The new wrapper is fm_hurdle; with the Jeffreys p it is the registered hurdle.
            jeffreys = [occurrence(context)] * horizon
            monkeypatch.setattr(
                "pulsegraph.study2.models.dynamic_occurrence", lambda c, h, p=jeffreys: p
            )
            rebuilt = study3_variants(completed, context)["hurdle_dynamic"]
            monkeypatch.undo()
            assert rebuilt["deciles"] == variants["hurdle"]["deciles"]
            assert rebuilt["distributions"] == variants["hurdle"]["distributions"]
    # Where dynamic_count falls back to hurdle_count_28 (fewer than two positives in the last 28
    # days), its occurrence is the Jeffreys p and hurdle_dynamic is the registered hurdle.
    lonely = _contexts()["lonely"]
    assert np.count_nonzero(lonely[-28:]) == 1
    variants = fm_variants(_output(lonely, 30), lonely, study3=True)
    assert variants["hurdle_dynamic"]["deciles"] == variants["hurdle"]["deciles"]
    assert variants["hurdle_dynamic"]["distributions"] == variants["hurdle"]["distributions"]


def test_hurdle_dynamic_occurrence_equals_dynamic_counts_on_every_day():
    for name, context in _contexts().items():
        for horizon in (1, 7, 30):
            variants = fm_variants(_output(context, horizon), context, study3=True)
            dynamic_laws = count_laws("dynamic_count", context, horizon)
            mine = [CountLaw(s) for s in variants["hurdle_dynamic"]["distributions"]]
            assert len(mine) == horizon
            for law, reference in zip(mine, dynamic_laws, strict=True):
                assert float(law.sf(0)) == float(reference.sf(0)) == reference.spec["p"]
            assert dynamic_occurrence(context, horizon) == [float(r.sf(0)) for r in dynamic_laws]
            if np.count_nonzero(context[-28:]) >= 2:
                assert float(mine[0].sf(0)) == pytest.approx(_beta_bernoulli(context), rel=1e-12)
            else:
                assert float(mine[0].sf(0)) == occurrence(context)
            # Its positive law is the model's completed law conditioned on Y >= 1.
            for spec, base in zip(
                variants["hurdle_dynamic"]["distributions"],
                variants["completed"]["distributions"],
                strict=True,
            ):
                assert spec["positive"] == dict(kind="positive", base=base)
                assert spec["fallback"] is None
            meta = variants["hurdle_dynamic"]["metadata"]
            assert meta["occurrence_source"] == "dynamic_count"
            assert meta["occurrence"] == dynamic_occurrence(context, horizon)


def test_the_fourth_cells_occurrence_is_the_completed_laws_and_its_size_the_count_hurdles():
    for name, context in _contexts().items():
        count = count_laws("hurdle_count_28", context, 1)[0].spec
        for horizon in (7, 30):
            variants = fm_variants(_output(context, horizon), context, study3=True)
            specs = variants["occurrence_model_size_count"]["distributions"]
            for spec, base in zip(specs, variants["completed"]["distributions"], strict=True):
                law, base = CountLaw(spec), CountLaw(base)
                assert float(law.sf(0)) == float(base.sf(0)) == spec["p"]
                assert spec["positive"] == count["positive"]
                assert spec["fallback"] == count["fallback"]
                # Its positive law is hurdle_count_28's: P(Y = k | Y > 0) agrees for small k.
                k = np.arange(1, 25)
                assert np.allclose(
                    law.sf(k) / law.sf(0),
                    CountLaw(count).sf(k) / CountLaw(count).sf(0),
                    rtol=1e-12,
                    atol=1e-15,
                )
            assert variants["occurrence_model_size_count"]["deciles"] == [
                CountLaw(s).ppf(TAU).tolist() for s in specs
            ]
    # Fewer than two recent positives: the count hurdle's delta_1, recorded as its fallback.
    lonely = _contexts()["lonely"]
    variants = fm_variants(_output(lonely, 7), lonely, study3=True)
    spec = variants["occurrence_model_size_count"]["distributions"][0]
    assert spec["positive"] == dict(kind="point", value=1)
    assert spec["fallback"] == "fewer_than_two_positives"


def test_delta_1_only_when_the_completed_law_has_f0_equal_to_one():
    context = _contexts()["dense"]
    zero = CountLaw(dict(kind="point", value=0))
    variants = study3_variants([zero] * 7, context)
    p = dynamic_occurrence(context, 7)[0]
    for spec in variants["hurdle_dynamic"]["distributions"]:
        assert spec["positive"] == dict(kind="point", value=1)
        assert spec["fallback"] == "F0_equals_one"
    # Zero for tau <= 1 - p, one above, as the registered inversion compares it.
    assert variants["hurdle_dynamic"]["deciles"][0] == [0.0 if p <= 1 - t else 1.0 for t in TAU]
    # The fourth cell takes the model's own occurrence, here zero: a point mass at zero.
    for spec in variants["occurrence_model_size_count"]["distributions"]:
        assert spec["p"] == 0.0 and float(CountLaw(spec).sf(0)) == 0.0
    assert variants["occurrence_model_size_count"]["deciles"] == [[0.0] * 9] * 7
    # A completed law always keeps its own positive law: its tail leaves F(0) < 1.
    kept = study3_variants([complete(np.zeros(9))] * 3, context)["hurdle_dynamic"]
    assert all(s["positive"]["kind"] == "positive" for s in kept["distributions"])
    assert all(s["fallback"] is None for s in kept["distributions"])
    with pytest.raises(ValueError, match="hurdle_count_28"):
        model_size_count(complete(np.zeros(9)), dict(kind="poisson", mu=1.0))


class Model:
    """A frozen model double: nine native deciles per lead, recording its seed."""

    def __init__(self, name):
        self.name, self.seeds = name, []

    def forecast(self, context, horizon, key):
        self.seeds.append(self.seed)
        return _output(np.asarray(context), horizon, list(MODEL_PINS).index(self.name))


class Baseline:
    def __init__(self, name):
        self.name, self.seeds = name, []

    def forecast(self, context, horizon, key):
        from types import SimpleNamespace

        self.seeds.append(self.seed)
        level = float(np.mean(context[-28:]))
        q = np.tile(np.floor(level * np.linspace(0.5, 1.5, 9)), (horizon, 1))
        meta = dict(mu=level, alpha=0, size=None, probability=None)
        return SimpleNamespace(
            quantile=lambda t: q[:, int(np.argmin(np.abs(TAU - t)))],
            metadata=meta,
            samples=None,
        )


def _factory(created):
    def factory(name, spec):
        created[name] = (Model if name in MODEL_PINS else Baseline)(name)
        return created[name]

    return factory


def test_the_study3_pool_saves_the_sixteen_and_the_two_new_variants_with_study3_seeds():
    context = _contexts()["sparse"]
    for study3, variants, root, component in (
        (False, VARIANTS, SEEDS["forecast"], "study2"),
        (True, STUDY3_VARIANTS, STUDY3_SEEDS["forecast"], "study3"),
    ):
        created = {}
        with ModelPool(study3=study3, factory=_factory(created), release=lambda m: None) as pool:
            forecasts = pool.forecast(context, 7, "label:2026-06-03")
        assert set(forecasts) == set(variants)
        assert len(variants) == (16 if not study3 else 22)
        for name, model in created.items():
            assert model.seeds == [
                derived_seed(root, component, name, "label:2026-06-03", 7, values=context)
            ]
    assert STUDY3_VARIANTS[:16] == VARIANTS
    assert STUDY3_VARIANTS[16:] == tuple(f"{m}_{v}" for m in MODEL_PINS for v in NEW)
    with pytest.raises(ValueError, match="prospective"):
        ModelPool(study3=True, prospective=True)


@pytest.mark.parametrize("mutation", ["perturb", "permute", "extend"])
def test_the_study3_forecasts_ignore_every_day_on_or_after_the_cutoff(tmp_path, mutation):
    cutoff = "2026-07-03"
    rng = np.random.default_rng(8)
    baseline = pd.Series(rng.poisson(1.5, len(DATES)).astype(float), index=DATES)
    changed = baseline.copy()
    later = changed.index >= cutoff
    if mutation == "perturb":
        changed[later] += 50
    elif mutation == "permute":
        changed[later] = changed[later].to_numpy()[::-1]
    else:
        changed = pd.concat(
            [changed, pd.Series(77.0, index=pd.date_range("2026-09-01", "2026-12-31"))]
        )
    forecasts = []
    for series, name in ((baseline, "first"), (changed, "second")):
        created = {}
        with ModelPool(study3=True, factory=_factory(created), release=lambda m: None) as pool:
            _evaluate(
                {("nyc311", "a"): series},
                tmp_path / name,
                pool,
                metadata={},
                variants=STUDY3_VARIANTS,
            )
        forecasts.append(
            {
                key[1:]: row["forecast"]
                for key, row in _rows(tmp_path / name).items()
                if key[1] <= cutoff or mutation == "extend"
            }
        )
    assert forecasts[0] == forecasts[1]
    windows = 2 * 2 if mutation != "extend" else 3 * 2
    assert len(forecasts[0]) == windows * len(STUDY3_VARIANTS)


class Study3Pool(RegisteredPool):
    """The post-hoc test's registered pool with Study 3's two new variants added."""

    def forecast(self, context, horizon, key):
        forecasts = super().forecast(context, horizon, key)
        for name in MODEL_PINS:
            completed = [CountLaw(s) for s in forecasts[f"{name}_completed"]["distributions"]]
            for variant, forecast in study3_variants(completed, context).items():
                forecasts[f"{name}_{variant}"] = forecast
        return forecasts


def _truth():
    rng = np.random.default_rng(11)
    truth = {
        ("packages", key): pd.Series(rng.poisson(rate, len(DATES)).astype(float), index=DATES)
        for key, rate in zip(STRATA, (6.0, 3.0, 1.5, 1.0, 0.7), strict=True)
    }
    sparse = truth[("packages", "p3")]
    sparse[(sparse.index >= "2026-05-06") & (sparse.index < "2026-06-03")] = 0.0
    sparse[pd.Timestamp("2026-05-20")] = 1.0
    return truth


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    """A toy Study 2 npm run with its registered inference, and the same series run with the
    Study 3 variants; both from the same registered forecast shapes."""
    root = tmp_path_factory.mktemp("study3-variants")
    _write_family(root, "external_packages")
    truth = _truth()
    manifest = root / "manifest.json"
    atomic_json(
        manifest,
        dict(series=[dict(series_id=key, stratum=stratum) for key, stratum in STRATA.items()]),
    )
    readiness = dict(
        action="external_packages",
        panels=dict(packages=dict(manifest=dict(path=str(manifest), sha256=file_hash(manifest)))),
    )
    metadata = dict(
        readiness=readiness,
        spec=specification("external_packages"),
        family=comparisons("external_packages"),
        metadata=dict(implementation_commit="a" * 40),
        readiness_sha256="b" * 64,
    )
    study2_run = root / "study2"
    _evaluate(truth, study2_run, RegisteredPool(), metadata=metadata)
    inference_command.run_inference(
        "external_packages", study2_run, out=study2_run / "inference", root=root
    )
    study3_run = root / "study3"
    _evaluate(truth, study3_run, Study3Pool(), metadata=metadata, variants=STUDY3_VARIANTS)
    return root, study2_run, study3_run


def _rows(run):
    state = read_json(run / "run.json")
    rows = {}
    for label in state["completed"]:
        for row in read_json(run / (sha256_bytes(label.encode()) + ".json"))["rows"]:
            rows[(row["series_id"], row["cutoff"], row["horizon"], row["model"])] = row
    return rows


def test_the_posthoc_npm_numbers_are_reproduced_by_the_registered_variant(runs):
    root, study2_run, study3_run = runs
    posthoc = dynamic.run_component("external_packages", study2_run, root=root)
    saved, again = _rows(study3_run), _rows(study2_run)
    # Study 2's sixteen are the same forecasts and scores in both runs.
    for key, row in again.items():
        assert saved[key]["forecast"] == row["forecast"] and saved[key]["scores"] == row["scores"]
    windows = posthoc["tables"]["window_scores.csv"]
    assert len(windows) == len(STRATA) * 3 * 2 * len(MODEL_PINS)
    for row in windows.itertuples():
        model = row.model.removesuffix("_dyn")
        mine = saved[(row.series_id, row.cutoff, row.horizon, f"{model}_hurdle_dynamic")]
        scores = mine["scores"]
        assert scores["qscore9"] == row.qscore9
        assert scores["context_scaled_qscore9"] == row.context_scaled_qscore9
        assert scores["occurrence_brier"] == row.occurrence_brier
        for part in ("zero", "positive_over", "positive_under"):
            assert scores["contributions"][part] == getattr(row, part)
        rebuilt, _ = dynamic.wrap_window(
            saved[(row.series_id, row.cutoff, row.horizon, f"{model}_completed")],
            [row.p_dyn] * row.horizon,
        )
        assert mine["forecast"]["deciles"] == rebuilt["deciles"]
        assert mine["forecast"]["distributions"] == rebuilt["distributions"]
    # The post-hoc family's numbers, DE01 to DE24, from the registered variant's saved scores.
    frame = pd.DataFrame(
        [
            dict(
                series_id=r["series_id"],
                horizon=r["horizon"],
                model=r["model"].replace("_hurdle_dynamic", "_dyn"),
                qscore9=r["scores"]["qscore9"],
            )
            for r in saved.values()
            if r["model"] in VARIANTS or r["model"].endswith("_hurdle_dynamic")
        ]
    )
    means = frame.groupby(["horizon", "model", "series_id"]).qscore9.mean()
    entities = means.to_frame()
    table = posthoc["tables"]["inference.csv"]
    for row in table.itertuples():
        pair = inference_command.paired(entities, row.model, row.reference, row.horizon, "qscore9")
        diff = (pair.model_score - pair.reference_score).to_numpy()
        seed = derived_seed(
            20260917,
            "external_packages",
            row.id,
            row.domain,
            row.model,
            row.reference,
            int(row.horizon),
            "qscore9",
        )
        result = inference_command.cluster_contrast(
            diff, seed=seed, family=comparisons("external_packages")
        )
        assert row.bootstrap_seed == seed
        for name in ("mean_diff", "median_diff", "wins", "ties", "losses", "wilcoxon_p"):
            assert getattr(row, name) == result[name]
        assert row.mean_diff_ci_low == result["mean_diff_ci_low"]
        assert row.mean_diff_ci_high == result["mean_diff_ci_high"]


def test_the_new_variants_are_saved_with_their_laws_in_every_window(runs):
    _, _, study3_run = runs
    saved = _rows(study3_run)
    names = {key[3] for key in saved}
    assert names == set(STUDY3_VARIANTS)
    for (series, cutoff, horizon, name), row in saved.items():
        if not name.endswith(NEW):
            continue
        model = name.split("_", 1)[0]
        dynamic_law = saved[(series, cutoff, horizon, "dynamic_count")]["forecast"]
        completed = saved[(series, cutoff, horizon, f"{model}_completed")]["forecast"]
        count = saved[(series, cutoff, horizon, "hurdle_count_28")]["forecast"]
        for day, spec in enumerate(row["forecast"]["distributions"]):
            law = CountLaw(spec)
            if name.endswith("hurdle_dynamic"):
                assert float(law.sf(0)) == float(CountLaw(dynamic_law["distributions"][day]).sf(0))
            else:
                assert float(law.sf(0)) == float(CountLaw(completed["distributions"][day]).sf(0))
                assert spec["positive"] == count["distributions"][day]["positive"]
        assert row["scores"]["occurrence_brier"] is not None
    assert json.dumps(sorted(BASELINES)) == json.dumps(sorted(STUDY3_VARIANTS[9:16]))

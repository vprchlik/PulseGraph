"""The post-hoc intermittent-demand baselines and the fourth cell on toy runs of the three panels
and on synthetic series; no model is loaded."""

import importlib.util
import json
import shutil
import sys

import numpy as np
import pandas as pd
import pytest
from statsforecast.models import _ses_forecast
from test_study2_dynamic_occurrence import RegisteredPool
from test_study2_inference import (
    DATES,
    _copy_run,
    _rewrite_checkpoint,
    _rows,
    _toy_grid,
    _write_family,
)
from test_study3_variants import Study3Pool

import scripts.study2_inference as study2_inference
import scripts.study3_inference as study3_inference
from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.forecast.output import COMMON_QUANTILES
from pulsegraph.provenance import atomic_json, read_json
from pulsegraph.random import derived_seed
from pulsegraph.study2.constants import MODEL_PINS, STUDY3_FILES, STUDY3_VARIANTS
from pulsegraph.study2.declarations import comparisons, specification
from pulsegraph.study2.distributions import CountLaw, complete, fm_hurdle
from pulsegraph.study2.models import count_laws, law_forecast, occurrence
from pulsegraph.study2.runner import _evaluate
from pulsegraph.study2.scores import score
from pulsegraph.study2.synthetic import cells, generate

SCRIPT = ROOT_DIR / "reports/study2-posthoc-intermittent-baselines/intermittent_baselines.py"
_spec = importlib.util.spec_from_file_location("intermittent_baselines", SCRIPT)
ib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ib)

TAU = np.asarray(COMMON_QUANTILES)
NPM_STRATA = {
    "p0": "dense",
    "@s/q0": "dense",
    "p1": "sparse",
    "p2": "sparse",
    "p3": "very_sparse",
    "p4": "very_sparse",
}
NYC_SIZES = dict(dense=10, sparse=3, very_sparse=2)
ALPHAS = (0.05, 0.1, 0.2)


def _contexts(count=300, seed=5):
    """Synthetic count contexts from dense to all-zero, with lengths of the registered calendars."""
    rng = np.random.default_rng(seed)
    contexts = [np.zeros(275), np.r_[np.zeros(274), 3.0], np.r_[2.0, np.zeros(209)]]
    for _ in range(count):
        length = int(rng.choice([180, 210, 240, 275, 305, 335]))
        rate, density = rng.uniform(0.2, 30), rng.uniform(0.01, 1)
        y = rng.poisson(rate, length) * (rng.random(length) < density)
        contexts.append(y.astype(float))
    return contexts


def _mass(law, top=None):
    """The probability mass function of a count law on 0..top from its CDF."""
    if top is None:
        top = int(law.ppf(np.array([1 - 1e-9]))[0]) * 4 + 50
    k = np.arange(-1, top + 1)
    cdf = law.cdf(k)
    return np.diff(cdf), cdf


@pytest.fixture(scope="module", autouse=True)
def toy_grid_manifest():
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(study2_inference, "grid_manifest", _toy_grid)
        yield


def _metadata(component, readiness):
    return dict(
        readiness=readiness,
        spec=specification(component),
        family=comparisons(component),
        metadata=dict(implementation_commit="a" * 40),
        readiness_sha256="b" * 64,
    )


@pytest.fixture(scope="module")
def toy(tmp_path_factory):
    """Toy npm, grid and NYC 311 runs, each with its registered inference in the run directory."""
    root = tmp_path_factory.mktemp("intermittent-baselines")
    for component in ("external_packages", "synthetic"):
        _write_family(root, component)
    for name in STUDY3_FILES:
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT_DIR / name, root / name)
    atomic_json(root / "study/study2/grid_manifest.json", _toy_grid())
    rng = np.random.default_rng(17)
    npm = {
        ("packages", key): pd.Series(rng.poisson(rate, len(DATES)).astype(float), index=DATES)
        for key, rate in zip(NPM_STRATA, (6.0, 3.0, 1.5, 1.0, 0.7, 0.5), strict=True)
    }
    sparse = npm[("packages", "p3")]
    sparse[(sparse.index >= "2026-05-06") & (sparse.index < "2026-06-03")] = 0.0
    sparse[pd.Timestamp("2026-05-20")] = 1.0
    # No positive context day before the first cutoff; positive days in its targets.
    silent = npm[("packages", "p4")]
    silent[silent.index < "2026-06-03"] = 0.0
    manifest = root / "npm-manifest.json"
    atomic_json(
        manifest,
        dict(series=[dict(series_id=key, stratum=stratum) for key, stratum in NPM_STRATA.items()]),
    )
    readiness = dict(
        action="external_packages",
        panels=dict(packages=dict(manifest=dict(path=str(manifest), sha256=file_hash(manifest)))),
    )
    runs = dict(npm=root / "npm", grid=root / "grid", nyc311=root / "nyc311")
    _evaluate(
        npm, runs["npm"], RegisteredPool(), metadata=_metadata("external_packages", readiness)
    )
    study2_inference.run_inference(
        "external_packages", runs["npm"], out=runs["npm"] / "inference", root=root
    )
    lookup = {c["cell_id"]: c for c in cells()}
    grid = {
        ("synthetic", row["series_id"]): pd.Series(
            generate(lookup[row["cell_id"]], row["replicate"]).astype(float)
        )
        for row in _toy_grid()["series"]
    }
    _evaluate(
        grid,
        runs["grid"],
        RegisteredPool(),
        metadata=_metadata("synthetic", dict(action="synthetic")),
        synthetic=True,
    )
    study2_inference.run_inference(
        "synthetic", runs["grid"], out=runs["grid"] / "inference", root=root
    )
    strata = {f"{s[0]}{i:02}": s for s, n in NYC_SIZES.items() for i in range(n)}
    rates = dict(dense=5.0, sparse=0.8, very_sparse=0.08)
    nyc = {}
    for key, stratum in strata.items():
        values = rng.poisson(rates[stratum] * (0.6 + 0.8 * rng.random()), len(DATES)).astype(float)
        if stratum != "dense":
            values[DATES.get_loc(pd.Timestamp("2026-05-20"))] = 2.0
        nyc[("nyc311", key)] = pd.Series(values, index=DATES)
    nyc_manifest = root / "nyc-manifest.json"
    atomic_json(
        nyc_manifest,
        dict(
            domain="nyc311",
            series=[dict(series_id=key, stratum=stratum) for key, stratum in strata.items()],
        ),
    )
    spec, family = (read_json(root / name) for name in STUDY3_FILES)
    nyc_metadata = dict(
        readiness=dict(
            action="study3",
            domain="nyc311",
            panels=dict(
                nyc311=dict(manifest=dict(path=str(nyc_manifest), sha256=file_hash(nyc_manifest)))
            ),
        ),
        spec=spec,
        family=family,
        metadata=dict(implementation_commit="a" * 40),
        readiness_sha256="b" * 64,
    )
    _evaluate(nyc, runs["nyc311"], Study3Pool(), metadata=nyc_metadata, variants=STUDY3_VARIANTS)
    study3_inference.run_inference(runs["nyc311"], out=runs["nyc311"] / "inference", root=root)
    return root, runs, dict(npm=npm, grid=grid, nyc311=nyc)


@pytest.fixture(scope="module")
def results(toy):
    root, runs, datasets = toy
    return {
        panel: ib.run_panel(panel, runs[panel], root=root, dataset=datasets[panel])
        for panel in ib.PANELS
    }


# The forecasts -----------------------------------------------------------------------------------


def test_the_specification_is_the_one_fixed_before_any_score():
    assert file_hash(ib.SPEC) == ib.SPEC_SHA256
    assert b"\r" not in ib.SPEC.read_bytes()
    assert ib.SMOOTHING == dict(tsb_hurdle=0.1, tsb_hurdle_a005=0.05, tsb_hurdle_a020=0.2)
    assert ib.SEED_ROOT == 20261017


def test_the_tsb_recursions_match_statsforecasts_point_forecast():
    for context in _contexts():
        for alpha in ALPHAS:
            p, z = ib.tsb_levels(context, alpha, alpha)
            reference = ib.statsforecast_tsb(context, alpha, 7)
            product = 0.0 if z is None else p * z
            assert np.allclose(reference, product, rtol=1e-12, atol=1e-12)
            if z is None:
                assert p == 0.0 and not np.any(context > 0)
                continue
            # Each level separately against statsforecast's own smoothing of its sequence.
            assert p == pytest.approx(_ses_forecast((context > 0).astype(float), alpha)[0], 1e-12)
            assert z == pytest.approx(_ses_forecast(context[context > 0], alpha)[0], rel=1e-12)
            # Levels started at the first value: one positive day gives that day's size.
            assert 0 < p <= 1 and z >= 1


def test_the_tsb_levels_follow_the_stated_formulas_by_hand():
    y = np.array([0.0, 3, 0, 0, 5, 1, 0])
    p, z = ib.tsb_levels(y, 0.1, 0.2)
    level = 0.0
    for d in [1.0, 0, 0, 1, 1, 0]:
        level = 0.1 * d + 0.9 * level
    assert p == pytest.approx(level, rel=1e-15)
    assert z == pytest.approx(0.2 * 1 + 0.8 * (0.2 * 5 + 0.8 * 3), rel=1e-15)


def test_a_last_28_days_of_zeros_decay_the_occurrence_as_the_formula_says():
    rng = np.random.default_rng(3)
    for _ in range(50):
        head = rng.poisson(rng.uniform(1, 9), int(rng.integers(150, 300))).astype(float)
        head[-1] = 1 + head[-1]  # a positive day just before the zeros
        context = np.r_[head, np.zeros(28)]
        for alpha in ALPHAS:
            before, size_before = ib.tsb_levels(head, alpha, alpha)
            after, size_after = ib.tsb_levels(context, alpha, alpha)
            assert after == pytest.approx((1 - alpha) ** 28 * before, rel=1e-12)
            assert size_after == size_before  # the size level moves on demand days only
            law, p, _ = ib.tsb_hurdle(context, alpha)
            assert float(law.sf(0)) == p == after
    # At the primary constant the last 28 zero days leave 0.9^28, about 0.0523, of the level.
    assert 0.9**28 == pytest.approx(0.05233476330273609, rel=1e-12)


def test_the_tsb_hurdle_with_the_jeffreys_occurrence_and_28_day_size_is_hurdle_count_28():
    checked = 0
    rng = np.random.default_rng(9)
    for context in _contexts():
        positive = context[-28:][context[-28:] > 0]
        if len(positive) < 2:
            continue
        law = ib.tsb_law(occurrence(context), float((positive - 1).mean()))
        registered = count_laws("hurdle_count_28", context, 1)[0]
        assert law.spec == registered.spec
        for horizon in (7, 30):
            target = rng.poisson(max(1.0, float(context[-28:].mean())), horizon).tolist()
            mine = score(target, ib.flat_forecast(law, horizon), context)
            theirs = score(target, law_forecast([registered] * horizon), context)
            assert mine == theirs
        checked += 1
    assert checked > 100


def test_the_toy_runs_reproduce_hurdle_count_28s_saved_scores_through_the_tsb_law(toy):
    _, runs, datasets = toy
    for panel in ("npm", "nyc311"):
        for row in _rows(runs[panel]):
            if row["model"] != "hurdle_count_28" or row["forecast"]["distributions"][0]["fallback"]:
                continue
            key = (ib.DOMAIN[panel], row["series_id"])
            context, _ = ib.context_and_target(panel, datasets[panel][key], row["cutoff"], 7)
            y = context.to_numpy()
            positive = y[-28:][y[-28:] > 0]
            law = ib.tsb_law(occurrence(y), float((positive - 1).mean()))
            forecast = ib.flat_forecast(law, row["horizon"])
            assert forecast["distributions"] == row["forecast"]["distributions"]
            assert score(row["target"], forecast, y) == row["scores"]


def test_the_fourth_cell_with_the_completed_positive_law_is_the_completed_control(toy):
    _, runs, datasets = toy
    checked = 0
    for panel in ib.PANELS:
        for row in _rows(runs[panel]):
            if not row["model"].endswith("_completed"):
                continue
            key = (ib.DOMAIN[panel], row["series_id"])
            context, _ = ib.context_and_target(
                panel, datasets[panel][key], row["cutoff"], row["horizon"]
            )
            laws = []
            for spec in row["forecast"]["distributions"]:
                base = CountLaw(spec)
                # The registered positive law of the completed law (delta_1 only if F(0) = 1).
                positive = fm_hurdle(base, 0.5).spec["positive"]
                laws.append(
                    ib.fourth_cell(spec, dict(kind="hurdle", positive=positive, fallback=None))
                )
            forecast = law_forecast(laws)
            assert forecast["deciles"] == row["forecast"]["deciles"]
            assert (
                score(row["target"], forecast, context.to_numpy())["qscore9"]
                == (row["scores"]["qscore9"])
            )
            checked += 1
    assert checked == sum(len(s) for s in datasets.values()) * 3 * 2 * len(MODEL_PINS)


def test_the_fourth_cell_is_the_models_zero_mass_with_the_count_positive_law(toy, results):
    _, runs, _ = toy
    saved = {(r["series_id"], r["cutoff"], r["horizon"], r["model"]): r for r in _rows(runs["npm"])}
    windows = results["npm"]["tables"]["window_scores.csv"]
    mine = windows[windows.model.str.endswith(ib.FOURTH)]
    assert len(mine) == 6 * 3 * 2 * len(MODEL_PINS)
    for row in mine.itertuples():
        model = row.model.removesuffix(ib.FOURTH)
        completed = saved[(row.series_id, row.cutoff, row.horizon, f"{model}_completed")]
        count = saved[(row.series_id, row.cutoff, row.horizon, "hurdle_count_28")]
        laws = [
            CountLaw(
                dict(
                    kind="hurdle",
                    p=float(CountLaw(c).sf(0)),
                    positive=k["positive"],
                    fallback=k["fallback"],
                )
            )
            for c, k in zip(
                completed["forecast"]["distributions"],
                count["forecast"]["distributions"],
                strict=True,
            )
        ]
        expected = score(completed["target"], law_forecast(laws), np.zeros(1))
        assert row.qscore9 == expected["qscore9"]
        assert row.occurrence_brier == completed["scores"]["occurrence_brier"]
        assert row.occurrence_p == float(CountLaw(completed["forecast"]["distributions"][0]).sf(0))


def test_every_law_integrates_to_one():
    laws = []
    for context in _contexts(count=60):
        for alpha in ALPHAS:
            laws.append(ib.tsb_hurdle(context, alpha))
    laws.append((ib.tsb_law(0.4, 0.0), 0.4, 1.0))  # every positive size one
    for law, p, z in laws:
        mass, cdf = _mass(law)
        assert cdf[0] == 0.0 and (mass >= -1e-15).all()
        assert mass.sum() == pytest.approx(1.0, abs=1e-12)
        assert mass[0] == pytest.approx(1 - p, abs=1e-15)
        mean = float(np.dot(np.arange(len(mass)), mass))
        assert mean == pytest.approx(0.0 if z is None else p * z, rel=1e-9, abs=1e-12)
    for c in (0, 1, 7, 250):
        mass, cdf = _mass(CountLaw(dict(kind="point", value=c)), top=300)
        assert mass.sum() == 1.0 and mass[c] == 1.0
    rng = np.random.default_rng(2)
    count = count_laws("hurdle_count_28", rng.poisson(3, 275).astype(float), 1)[0].spec
    sparse = count_laws("hurdle_count_28", np.r_[np.zeros(274), 2.0], 1)[0].spec
    for deciles in (np.zeros(9), np.sort(rng.gamma(2, 4, 9)), np.r_[np.zeros(5), 1, 2, 4, 9]):
        for k in (count, sparse):
            law = ib.fourth_cell(complete(deciles).spec, k)
            mass, cdf = _mass(law)
            assert cdf[0] == 0.0 and (mass >= -1e-15).all()
            assert mass.sum() == pytest.approx(1.0, abs=1e-12)
            assert mass[0] == pytest.approx(float(complete(deciles).cdf(0)), abs=1e-15)


def test_the_point_methods_are_statsforecasts_scored_as_a_degenerate_law():
    from statsforecast.models import ADIDA, CrostonClassic, CrostonSBA

    rng = np.random.default_rng(4)
    for context in _contexts(count=40):
        for name, model in (
            ("croston_classic", CrostonClassic),
            ("croston_sba", CrostonSBA),
            ("adida", ADIDA),
        ):
            f, c = ib.point_method(name, context, 7)
            assert f == model().forecast(y=context, h=7)["mean"][0]
            assert c == int(np.floor(f + 0.5))
            target = rng.poisson(max(f, 0.1), 7)
            result = score(
                target.tolist(), ib.flat_forecast(CountLaw(dict(kind="point", value=c)), 7), context
            )
            assert result["qscore9"] == pytest.approx(np.mean(np.abs(target - c)), rel=1e-12)
            assert result["discrete_crps"] == pytest.approx(np.mean(np.abs(target - c)), 1e-12)
            assert result["occurrence_brier"] == np.mean((float(c > 0) - (target > 0)) ** 2)
    assert ib.point_method("adida", np.zeros(200), 30) == (0.0, 0)
    assert ib.point_method("croston_classic", np.zeros(200), 30) == (0.0, 0)


def test_the_flat_forecast_is_the_registered_inversion_of_every_day():
    for context in _contexts(count=30):
        law, _, _ = ib.tsb_hurdle(context, 0.1)
        for horizon in (7, 30):
            assert ib.flat_forecast(law, horizon) == law_forecast([law] * horizon)


# The toy runs ------------------------------------------------------------------------------------


def test_the_registered_families_are_reproduced_and_every_window_is_checked(results):
    for panel, result in results.items():
        checks = result["checks"]
        assert checks["registered_family_reproduced_byte_for_byte"] == {
            "inference.csv": True,
            "paired_entities.csv": True,
        }
        series = dict(npm=6, grid=12, nyc311=sum(NYC_SIZES.values()))[panel]
        assert checks["windows"] == series * 3 * 2
        assert checks["tsb_recursions_equal_statsforecast"] == series * 3 * 2 * 3
        new = 6 if panel == "nyc311" else 9
        assert checks["new_forecast_windows"] == series * 3 * 2 * new
        assert len(result["tables"]["window_scores.csv"]) == series * 3 * 2 * new
    assert results["npm"]["checks"]["context_all_zero_windows"] == 2
    assert results["nyc311"]["checks"]["saved_fourth_cell_laws_rebuilt"] == 15 * 6 * 3


def test_an_all_zero_context_gives_a_point_mass_at_zero(results):
    windows = results["npm"]["tables"]["window_scores.csv"]
    silent = windows[windows.series_id.eq("p4") & windows.cutoff.eq("2026-06-03")]
    tsb = silent[silent.model.isin(ib.TSB_NAMES)]
    assert len(tsb) == 6 and (tsb.occurrence_p == 0).all() and tsb.size_level.isna().all()
    assert (tsb.fallback == "no_positive_context_day").all()
    points = silent[silent.model.isin(list(ib.POINT))]
    assert (points.point_value == 0).all()


def test_the_contrasts_are_the_specified_ones_with_the_declared_seeds(results):
    for panel, result in results.items():
        table = result["tables"]["contrasts.csv"]
        mine = table[table.source.eq(ib.POSTHOC)]
        groups = 1 + dict(npm=3, grid=3, nyc311=3)[panel]
        references = 11 if panel == "nyc311" else 8
        per_group = 2 * (3 * references + (0 if panel == "nyc311" else 6) + 3 * 6)
        assert len(mine) == groups * per_group * 4
        assert not mine.duplicated(["group", "variant", "reference", "horizon", "metric"]).any()
        assert "wilcoxon_p_bh" not in table.columns and "reject_bh_005" not in table.columns
        available = mine[mine.status.eq("descriptive")]
        for row in available.itertuples():
            assert row.id == f"{row.group}/{row.variant}/{row.reference}/h{row.horizon}"
            seed = derived_seed(
                20261017,
                panel,
                row.id,
                row.group,
                row.variant,
                row.reference,
                int(row.horizon),
                row.metric,
            )
            assert row.bootstrap_seed == seed and row.bootstrap_root == 20261017
            assert row.median_sign == (
                "negative" if row.median_diff < 0 else "positive" if row.median_diff > 0 else "zero"
            )
            assert row.wins + row.ties + row.losses == row.n_entities
        assert set(available.metric) == set(ib.METRICS)


def test_the_aggregation_is_the_registered_one(toy, results):
    _, runs, _ = toy
    for panel in ("npm", "nyc311"):
        saved = pd.DataFrame(
            [
                dict(
                    series_id=r["series_id"],
                    cutoff=r["cutoff"],
                    horizon=r["horizon"],
                    model=r["model"],
                    qscore9=r["scores"]["qscore9"],
                )
                for r in _rows(runs[panel])
            ]
        )
        windows = results[panel]["tables"]["window_scores.csv"]
        both = pd.concat([saved, windows[saved.columns]], ignore_index=True)
        means = both.groupby(["horizon", "model", "series_id"]).qscore9.mean()
        table = results[panel]["tables"]["contrasts.csv"]
        rows = table[table.metric.eq("qscore9") & table.source.eq(ib.POSTHOC)]
        labels = windows.drop_duplicates("series_id").set_index("series_id").stratum
        for row in rows.itertuples():
            diff = means.loc[(row.horizon, row.variant)] - means.loc[(row.horizon, row.reference)]
            if row.group != ib.ALL:
                diff = diff[labels.loc[diff.index].eq(row.group).to_numpy()]
            assert row.n_entities == len(diff)
            assert row.mean_diff == pytest.approx(diff.mean(), rel=1e-12, abs=1e-15)
            assert row.median_diff == pytest.approx(diff.median(), rel=1e-12, abs=1e-15)
            assert row.wins == int((diff < 0).sum()) and row.ties == int((diff == 0).sum())
    # The grid pooled: origins within replicate and cell, cells within replicate, 4 blocks here.
    windows = results["grid"]["tables"]["window_scores.csv"]
    saved = pd.DataFrame(
        [
            dict(
                series_id=r["series_id"],
                horizon=r["horizon"],
                model=r["model"],
                qscore9=r["scores"]["qscore9"],
            )
            for r in _rows(runs["grid"])
        ]
    )
    both = pd.concat([saved, windows[saved.columns]], ignore_index=True)
    both["replicate"] = both.series_id.str[-2:].astype(int)
    both["cell"] = both.series_id.str.split("/").str[0]
    blocks = both.groupby(["horizon", "model", "replicate", "cell"]).qscore9.mean()
    blocks = blocks.groupby(["horizon", "model", "replicate"]).mean()
    table = results["grid"]["tables"]["contrasts.csv"]
    pooled = table[table.group.eq(ib.ALL) & table.metric.eq("qscore9")]
    assert (pooled.entity == "replicate").all() and (pooled.n_entities == 4).all()
    for row in pooled.itertuples():
        diff = blocks.loc[(row.horizon, row.variant)] - blocks.loc[(row.horizon, row.reference)]
        assert row.mean_diff == pytest.approx(diff.mean(), rel=1e-12, abs=1e-15)


def test_the_nyc311_fourth_cell_rows_are_the_runs_own(toy, results):
    _, runs, _ = toy
    table = results["nyc311"]["tables"]["contrasts.csv"]
    own = table[table.source.eq(ib.RUNS_OWN)]
    assert len(own) == 4 * len(MODEL_PINS) * 2 * 2 * 4
    assert not table[table.source.eq(ib.POSTHOC)].variant.str.endswith(ib.FOURTH).any()
    saved = pd.concat(
        [
            pd.read_csv(
                runs["nyc311"] / "inference" / name,
                keep_default_na=False,
                na_values=[""],
                float_precision="round_trip",
            )
            for name in ("secondary_strata_contrasts.csv", "secondary_pooled_contrasts.csv")
        ]
    ).set_index("id")
    for row in own.itertuples():
        theirs = saved[saved.metric.eq(row.metric)].loc[row.id]
        assert row.group == theirs.stratum
        for name in ("mean_diff", "median_diff", "wins", "ties", "losses", "bootstrap_seed"):
            assert getattr(row, name) == theirs[name]
    sizes = own.drop_duplicates("group").set_index("group").group_series.to_dict()
    assert sizes == dict(all=15, dense=10, sparse=3, very_sparse=2)
    assert (own.below_ten_series == own.group.isin(["sparse", "very_sparse"])).all()


def test_a_changed_checkpoint_or_context_is_refused(toy, tmp_path):
    root, runs, datasets = toy

    def change_count(rows):
        row = next(r for r in rows if r["model"] == "hurdle_count_28")
        row["forecast"]["distributions"][0]["p"] = 0.5
        return rows

    copy = _copy_run(runs["npm"], tmp_path / "count")
    _rewrite_checkpoint(copy, change_count)
    with pytest.raises(ValueError, match="not reproduced"):
        ib.run_panel("npm", copy, root=root, dataset=datasets["npm"])
    changed = dict(datasets["npm"])
    key = next(iter(changed))
    changed[key] = changed[key].copy()
    changed[key].iloc[3] += 1
    with pytest.raises(ValueError, match="Rebuilt context"):
        ib.run_panel("npm", runs["npm"], root=root, dataset=changed)
    copy = _copy_run(runs["npm"], tmp_path / "hash")
    state = read_json(copy / "run.json")
    state["completed"][sorted(state["completed"])[0]] = "0" * 64
    atomic_json(copy / "run.json", state)
    with pytest.raises(ValueError, match="hash mismatch"):
        ib.run_panel("npm", copy, root=root, dataset=datasets["npm"])


def test_the_command_writes_its_outputs_once(toy, tmp_path, monkeypatch, capsys):
    root, runs, datasets = toy
    monkeypatch.setattr(ib, "load_dataset", lambda panel, state, root=None: datasets[panel])
    argv = ["intermittent_baselines.py"]
    for panel in ib.PANELS:
        argv += [f"--{panel}", str(runs[panel])]
    argv += ["--out", str(tmp_path), "--root", str(root)]
    monkeypatch.setattr(sys, "argv", argv)
    ib.main()
    printed = capsys.readouterr().out
    for heading in (
        "## npm: tsb_hurdle against every reference, four scores",
        "## grid cells: tsb_hurdle, qscore9, h = 30",
        "## nyc311: the fourth cell, four scores",
        "## grid: the point methods, QScore9",
        "## nyc311: occurrence descriptors",
    ):
        assert heading in printed
    assert "| very_sparse (n = 2) †" in printed and "run's own" in printed
    document = read_json(tmp_path / "provenance.json")
    assert document["status"].startswith("post hoc and descriptive")
    assert document["specification"]["sha256"] == ib.SPEC_SHA256
    assert document["script"]["sha256"] == file_hash(SCRIPT)
    assert set(document["runs"]) == set(ib.PANELS)
    assert len(document["outputs"]) == 9
    for name, digest in document["outputs"].items():
        assert file_hash(tmp_path / name) == digest
        assert b"\r" not in (tmp_path / name).read_bytes()
    for panel in ib.PANELS:
        recorded = document["runs"][panel]["checkpoint_sha256"]
        assert recorded == read_json(runs[panel] / "run.json")["completed"]
    contrasts = pd.read_csv(tmp_path / "npm_contrasts.csv")
    assert set(contrasts.source) == {ib.POSTHOC}
    assert json.loads(json.dumps(document["inference"]))["adjustment"] == "none"
    with pytest.raises(SystemExit, match="refusing to overwrite"):
        ib.main()

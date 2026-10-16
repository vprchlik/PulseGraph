"""The post-hoc dynamic-occurrence wrapper on toy runs of both components; no model is loaded."""

import importlib.util
import json
import sys

import numpy as np
import pandas as pd
import pytest
from test_study2_inference import (
    DATES,
    STRATA,
    TOY_REPLICATES,
    _copy_run,
    _rewrite_checkpoint,
    _rows,
    _toy_grid,
    _write_family,
)

import scripts.study2_inference as inference_command
from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.evaluation.reviews import benjamini_hochberg
from pulsegraph.forecast.output import COMMON_QUANTILES
from pulsegraph.provenance import atomic_json, read_json
from pulsegraph.random import derived_seed
from pulsegraph.study2.constants import BASELINES, MODEL_PINS
from pulsegraph.study2.declarations import comparisons, specification
from pulsegraph.study2.distributions import CountLaw, complete, fm_hurdle
from pulsegraph.study2.models import count_laws, fm_variants, law_forecast, occurrence
from pulsegraph.study2.runner import _evaluate
from pulsegraph.study2.scores import accounting
from pulsegraph.study2.synthetic import cells, generate

SCRIPT = ROOT_DIR / "reports/study2-posthoc-dynamic-occurrence/dynamic_occurrence.py"
_spec = importlib.util.spec_from_file_location("dynamic_occurrence", SCRIPT)
dynamic = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dynamic)

DEGENERATE = ("p1", "timesfm2p5")  # this toy completed law has F(0) = 1 in every window
SPARSE = ("p3", "2026-06-03")  # one positive day among the 28 before this cutoff
TAU = np.asarray(COMMON_QUANTILES)


class Output:
    """A frozen model's native output: nine deciles per lead, read by the registered fm_variants."""

    def __init__(self, deciles):
        self.quantile_levels = TAU
        self.deciles = np.asarray(deciles, dtype=float)
        self.metadata = {}

    def quantile(self, level):
        return self.deciles[:, int(np.argmin(np.abs(TAU - level)))]


class RegisteredPool:
    """Every foundation model variant built by the registered fm_variants, with deciles that vary
    by lead; one model's completed law is a point mass at zero on one series."""

    def forecast(self, context, horizon, key):
        series_id = json.loads(key.rsplit(":", 1)[0])[1]
        level = float(np.mean(context[-28:]))
        forecasts = {}
        for index, name in enumerate(MODEL_PINS):
            shape = level * np.linspace(0.1 + 0.1 * index, 1.6 + 0.2 * index, 9)
            deciles = np.floor(np.outer(1 + 0.03 * np.arange(horizon), shape) * 4) / 4
            forecasts.update(
                {f"{name}_{v}": f for v, f in fm_variants(Output(deciles), context).items()}
            )
            if (series_id, name) == DEGENERATE:
                zero = CountLaw(dict(kind="point", value=0))
                forecasts[f"{name}_completed"] = law_forecast([zero] * horizon)
                forecasts[f"{name}_hurdle"] = law_forecast(
                    [fm_hurdle(zero, occurrence(context))] * horizon
                )
        for name in ("local_mean_28", "autoets_weekly"):
            forecasts[name] = dict(
                deciles=np.tile(np.floor(level * np.linspace(0.5, 1.5, 9)), (horizon, 1)).tolist(),
                distributions=None,
                samples=None,
            )
        forecasts["nb_local_level_28"] = law_forecast(
            [CountLaw(dict(kind="poisson", mu=level))] * horizon
        )
        for name in BASELINES[3:]:
            forecasts[name] = law_forecast(count_laws(name, context, horizon))
        return forecasts


@pytest.fixture(scope="module", autouse=True)
def toy_grid_manifest():
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inference_command, "grid_manifest", _toy_grid)
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
    """A toy npm run and a toy grid run, each with its registered inference beside it."""
    root = tmp_path_factory.mktemp("dynamic-occurrence")
    for component in ("external_packages", "synthetic"):
        _write_family(root, component)
    atomic_json(root / "study/study2/grid_manifest.json", _toy_grid())
    rng = np.random.default_rng(11)
    truth = {
        ("packages", key): pd.Series(rng.poisson(rate, len(DATES)).astype(float), index=DATES)
        for key, rate in zip(STRATA, (6.0, 3.0, 1.5, 1.0, 0.7), strict=True)
    }
    sparse = truth[("packages", SPARSE[0])]
    sparse[(sparse.index >= "2026-05-06") & (sparse.index < SPARSE[1])] = 0.0
    sparse[pd.Timestamp("2026-05-20")] = 1.0
    manifest = root / "manifest.json"
    atomic_json(
        manifest,
        dict(series=[dict(series_id=key, stratum=stratum) for key, stratum in STRATA.items()]),
    )
    npm = root / "npm"
    readiness = dict(
        action="external_packages",
        panels=dict(packages=dict(manifest=dict(path=str(manifest), sha256=file_hash(manifest)))),
    )
    _evaluate(truth, npm, RegisteredPool(), metadata=_metadata("external_packages", readiness))
    inference_command.run_inference("external_packages", npm, out=npm / "inference", root=root)
    lookup = {c["cell_id"]: c for c in cells()}
    grid_truth = {
        ("synthetic", row["series_id"]): pd.Series(
            generate(lookup[row["cell_id"]], row["replicate"]).astype(float)
        )
        for row in _toy_grid()["series"]
    }
    grid = root / "grid"
    _evaluate(
        grid_truth,
        grid,
        RegisteredPool(),
        metadata=_metadata("synthetic", dict(action="synthetic")),
        synthetic=True,
    )
    inference_command.run_inference("synthetic", grid, out=grid / "inference", root=root)
    return root, npm, grid, truth


@pytest.fixture(scope="module")
def results(toy):
    root, npm, grid, _ = toy
    return {
        component: dynamic.run_component(component, run, root=root)
        for component, run in (("external_packages", npm), ("synthetic", grid))
    }


def _saved(run):
    return {(r["series_id"], r["cutoff"], r["horizon"], r["model"]): r for r in _rows(run)}


def test_the_wrapper_with_the_jeffreys_p_reproduces_the_registered_hurdle_exactly(toy):
    root, npm, grid, _ = toy
    for run in (npm, grid):
        saved = _saved(run)
        for (key, cutoff, horizon, model), row in saved.items():
            if not model.endswith("_completed"):
                continue
            hurdle = saved[(key, cutoff, horizon, model.replace("_completed", "_hurdle"))]
            jeffreys = [spec["p"] for spec in hurdle["forecast"]["distributions"]]
            forecast, result = dynamic.wrap_window(row, jeffreys)
            assert forecast["deciles"] == hurdle["forecast"]["deciles"]
            assert forecast["distributions"] == hurdle["forecast"]["distributions"]
            assert result["qscore9"] == hurdle["scores"]["qscore9"]
    # The whole analysis with hurdle_count_28's p, which is the Jeffreys p, in place of p_dyn.
    for component, run in (("external_packages", npm), ("synthetic", grid)):
        outcome = dynamic.run_component(component, run, root=root, source="hurdle_count_28")
        windows = outcome["tables"]["window_scores.csv"]
        assert (windows.qscore9 == windows.registered_hurdle_qscore9).all()
        assert windows.equals_registered_hurdle.all()
        table = outcome["tables"]["inference.csv"].set_index("id")
        against_hurdle = table[table.reference.str.endswith("_hurdle")]
        assert (against_hurdle.ties == against_hurdle.n_entities).all()
        assert (against_hurdle.wilcoxon_p == 1.0).all()
        beside = table[table.registered_id.notna()]
        assert len(beside) == len(table) // 2
        for name in ("mean_diff", "median_diff", "wins", "ties", "losses"):
            assert (beside[name] == beside[f"registered_{name}"]).all()
        registered = pd.read_csv(
            run / "inference" / "inference.csv", float_precision="round_trip"
        ).set_index("id")
        raw = registered.loc[beside.registered_id, "wilcoxon_p"].to_numpy()
        assert np.array_equal(beside.wilcoxon_p.to_numpy(), raw)


def test_a_window_with_f0_equal_to_one_uses_delta_1(toy, results):
    law = dynamic.wrapper(dict(kind="point", value=0), 0.3)
    assert law.spec["positive"] == dict(kind="point", value=1)
    assert law.spec["fallback"] == "F0_equals_one"
    assert law.ppf(TAU).tolist() == [0.0] * 7 + [1.0] * 2
    assert law.cdf(np.array([0, 1, 5])).tolist() == pytest.approx([0.7, 1.0, 1.0], abs=1e-15)
    # A completed law always keeps its own positive law: its tail leaves F(0) < 1.
    kept = dynamic.wrapper(complete(np.zeros(9)).spec, 0.3)
    assert kept.spec["positive"]["kind"] == "positive" and kept.spec["fallback"] is None
    _, npm, _, _ = toy
    windows = results["external_packages"]["tables"]["window_scores.csv"]
    degenerate = windows.series_id.eq(DEGENERATE[0]) & windows.model.eq(DEGENERATE[1] + "_dyn")
    assert (
        windows.loc[degenerate, "f0_equals_one_days"] == windows.loc[degenerate, "horizon"]
    ).all()
    assert windows.loc[~degenerate, "f0_equals_one_days"].eq(0).all()
    saved = _saved(npm)
    for row in windows[degenerate].itertuples():
        target = saved[(row.series_id, row.cutoff, row.horizon, "dynamic_count")]["target"]
        # Zero for tau <= 1 - p, as the registered inversion compares it; one otherwise.
        deciles = [[0.0 if row.p_dyn <= 1 - tau else 1.0 for tau in TAU]] * row.horizon
        assert row.qscore9 == accounting(target, deciles)["qscore9"]


def test_p_dyn_is_dynamic_counts_discounted_occurrence(toy, results):
    _, npm, _, truth = toy
    windows = results["external_packages"]["tables"]["window_scores.csv"]
    assert windows.p_dyn_constant.all() and windows.p_jeffreys_constant.all()
    for row in windows.itertuples():
        series = truth[("packages", row.series_id)]
        context = series[series.index < row.cutoff].to_numpy()
        assert row.p_jeffreys == occurrence(context)
        if row.occurrence_fallback:
            # Fewer than two positives in the last 28 days: dynamic_count is hurdle_count_28.
            assert np.count_nonzero(context[-28:]) < 2
            assert row.p_dyn == row.p_jeffreys
            assert row.qscore9 == row.registered_hurdle_qscore9
            continue
        a, b = 0.5, 0.5
        for value in context:
            a, b = 0.98 * a + (value > 0), 0.98 * b + (value == 0)
        assert row.p_dyn == pytest.approx(a / (a + b), rel=1e-12)
    fallback = windows[windows.occurrence_fallback]
    assert set(zip(fallback.series_id, fallback.cutoff)) == {SPARSE}
    assert len(fallback) == len(MODEL_PINS) * 2
    occurrence_table = results["external_packages"]["tables"]["occurrence.csv"]
    everything = occurrence_table[occurrence_table.stratum.eq("all")].set_index("horizon")
    assert everything.occurrence_fallback_windows.tolist() == [1, 1]
    assert (everything.windows == len(STRATA) * 3).all()


def test_the_wrapper_quantiles_follow_the_registered_inversion(toy, results):
    _, npm, _, _ = toy
    saved = _saved(npm)
    windows = results["external_packages"]["tables"]["window_scores.csv"]
    for row in windows[windows.horizon.eq(7)].itertuples():
        model = row.model.removesuffix("_dyn")
        if (row.series_id, model) == DEGENERATE:
            continue  # F(0) = 1 there: delta_1, tested above
        completed = saved[(row.series_id, row.cutoff, 7, f"{model}_completed")]
        deciles = []
        for spec in completed["forecast"]["distributions"]:
            base, p, day = CountLaw(spec), row.p_dyn, []
            for tau in TAU:
                # Zero for tau <= 1 - p; otherwise G+ inverted at (tau - 1 + p) / p.
                k = 0
                while p * (base.sf(k) / base.sf(0) if k else 1.0) > 1 - tau:
                    k += 1
                day.append(float(k))
            deciles.append(day)
        target = np.asarray(completed["target"], dtype=float)
        error = target[:, None] - np.asarray(deciles)
        pinball = 2 * np.maximum(TAU * error, (TAU - 1) * error)
        assert row.qscore9 == pytest.approx(pinball.mean(), rel=1e-12, abs=1e-15)
        assert row.qscore9 == accounting(target, deciles)["qscore9"]


def test_the_registered_families_are_reproduced_byte_for_byte(results):
    for component, result in results.items():
        checks = result["checks"]
        assert checks["registered_family_reproduced_byte_for_byte"] == {
            "inference.csv": True,
            "paired_entities.csv": True,
        }
        windows = result["tables"]["window_scores.csv"]
        assert checks["windows"] == len(windows)
        assert checks["jeffreys_wrapper_reproduces_registered_hurdle"] == len(windows)


def test_the_posthoc_families_use_the_registered_settings(toy, results):
    for component, count in (("external_packages", 24), ("synthetic", 12)):
        family = results[component]["family"]
        table = results[component]["tables"]["inference.csv"]
        prefix = dict(external_packages="DE", synthetic="DS")[component]
        assert family["comparison_count"] == count == len(table)
        assert table.id.tolist() == [f"{prefix}{i:02}" for i in range(1, count + 1)]
        assert family["status"].startswith("post-hoc") and set(table.status) == {"post-hoc"}
        horizons = (7, 30) if component == "external_packages" else (30,)
        expected = [
            (f"{m}_dyn", reference, h)
            for m in MODEL_PINS
            for h in horizons
            for reference in (f"{m}_completed", "hurdle_count_28", "dynamic_count", f"{m}_hurdle")
        ]
        assert list(zip(table.model, table.reference, table.horizon)) == expected
        registered = comparisons(component)
        for name in ("bootstrap_replicates", "zero_method", "method", "alternative", "q"):
            assert family[name] == registered[name]
        assert (table.n_bootstrap == 20000).all() and (table.declared_count == count).all()
        # BH once over the post-hoc family alone.
        assert np.array_equal(table.wilcoxon_p_bh, benjamini_hochberg(table.wilcoxon_p))
        assert (table.reject_bh_005 == (table.wilcoxon_p_bh <= 0.05)).all()
        for row in table.itertuples():
            seed = derived_seed(
                20260917,
                component,
                row.id,
                row.domain,
                row.model,
                row.reference,
                int(row.horizon),
                "qscore9",
            )
            assert row.bootstrap_seed == seed
    # Model minus reference, origins averaged within series, series weighed equally (npm).
    _, npm, grid, _ = toy
    saved = pd.DataFrame(
        [
            dict(
                series_id=r["series_id"],
                cutoff=r["cutoff"],
                horizon=r["horizon"],
                model=r["model"],
                qscore9=r["scores"]["qscore9"],
            )
            for r in _rows(npm)
        ]
    )
    windows = results["external_packages"]["tables"]["window_scores.csv"]
    both = pd.concat([saved, windows[saved.columns]], ignore_index=True)
    means = both.groupby(["horizon", "model", "series_id"]).qscore9.mean()
    pairs = results["external_packages"]["tables"]["paired_entities.csv"]
    for row in results["external_packages"]["tables"]["inference.csv"].itertuples():
        diff = means.loc[(row.horizon, row.model)] - means.loc[(row.horizon, row.reference)]
        mine = pairs[pairs.id.eq(row.id)].set_index("entity").difference
        assert np.allclose(mine.loc[diff.index], diff, rtol=1e-12, atol=1e-15)
        assert row.mean_diff == pytest.approx(diff.mean(), rel=1e-12, abs=1e-15)
    # Grid: origins within replicate and cell, then cells within replicate, replicates as entities.
    rows = pd.DataFrame(
        [
            dict(
                replicate=int(r["series_id"][-2:]),
                cell=r["series_id"].split("/")[0],
                horizon=r["horizon"],
                model=r["model"],
                qscore9=r["scores"]["qscore9"],
            )
            for r in _rows(grid)
        ]
    )
    windows = results["synthetic"]["tables"]["window_scores.csv"]
    mine = windows.assign(cell=windows.cell_id)[rows.columns]
    both = pd.concat([rows, mine], ignore_index=True)
    blocks = (
        both[both.horizon.eq(30)]
        .groupby(["model", "replicate", "cell"])
        .qscore9.mean()
        .groupby(["model", "replicate"])
        .mean()
    )
    pairs = results["synthetic"]["tables"]["paired_entities.csv"]
    for row in results["synthetic"]["tables"]["inference.csv"].itertuples():
        diff = blocks[row.model] - blocks[row.reference]
        found = pairs[pairs.id.eq(row.id)].set_index("entity").difference
        assert list(found.index) == list(TOY_REPLICATES)
        assert np.allclose(found.to_numpy(), diff.to_numpy(), rtol=1e-12, atol=1e-15)


def test_the_wrapper_shares_dynamic_counts_occurrence_and_the_models_positive_law(toy, results):
    _, npm, _, _ = toy
    saved = _saved(npm)
    windows = results["external_packages"]["tables"]["window_scores.csv"]
    for row in windows.itertuples():
        brier = saved[(row.series_id, row.cutoff, row.horizon, "dynamic_count")]["scores"]
        assert row.occurrence_brier == brier["occurrence_brier"]
    for component, result in results.items():
        accounting_table = result["tables"]["accounting.csv"]
        assert np.allclose(
            accounting_table.parts_sum, accounting_table.qscore9, rtol=1e-12, atol=1e-12
        )
        assert {f"{m}_dyn" for m in MODEL_PINS} <= set(accounting_table.model)
    groups = results["external_packages"]["tables"]["groups.csv"]
    counts = groups.drop_duplicates("stratum").set_index("stratum").n_entities.to_dict()
    assert counts == dict(dense=2, sparse=2, very_sparse=1)
    assert len(groups) == 3 * 24 * 2
    cells_table = results["synthetic"]["tables"]["groups.csv"]
    assert (cells_table.n_entities == len(TOY_REPLICATES)).all()
    assert len(cells_table) == 3 * 12 * 2 and "zero_probability" in cells_table.columns


def test_a_changed_checkpoint_is_refused(toy, tmp_path):
    root, npm, _, _ = toy

    def change_occurrence(rows):
        row = next(r for r in rows if r["model"] == "dynamic_count")
        row["forecast"]["distributions"][0]["p"] = 0.5
        return rows

    def change_hurdle(rows):
        row = next(r for r in rows if r["model"] == "chronos2_hurdle")
        row["forecast"]["deciles"][0][-1] += 1
        return rows

    for name, change, message in (
        ("occurrence", change_occurrence, "occurrence differs|P\\(Y > 0\\)"),
        ("hurdle", change_hurdle, "does not reproduce the hurdle"),
    ):
        copy = _copy_run(npm, tmp_path / name)
        _rewrite_checkpoint(copy, change)
        with pytest.raises(ValueError, match=message):
            dynamic.run_component("external_packages", copy, root=root)
    copy = _copy_run(npm, tmp_path / "hash")
    state = read_json(copy / "run.json")
    state["completed"][sorted(state["completed"])[0]] = "0" * 64
    atomic_json(copy / "run.json", state)
    with pytest.raises(ValueError, match="identity|hash mismatch"):
        dynamic.run_component("external_packages", copy, root=root)


def test_the_command_writes_its_outputs_once(toy, tmp_path, monkeypatch, capsys):
    root, npm, grid, _ = toy
    argv = ["dynamic_occurrence.py", "--npm", str(npm), "--synthetic", str(grid)]
    argv += ["--out", str(tmp_path), "--root", str(root)]
    monkeypatch.setattr(sys, "argv", argv)
    dynamic.main()
    printed = capsys.readouterr().out
    assert "## npm: the post-hoc family" in printed and "## synthetic: occurrence" in printed
    document = read_json(tmp_path / "provenance.json")
    assert document["status"].startswith("post-hoc")
    assert document["script"]["sha256"] == file_hash(SCRIPT)
    assert set(document["runs"]) == {"npm", "synthetic"}
    assert document["runs"]["npm"]["checks"]["registered_family_reproduced_byte_for_byte"] == {
        "inference.csv": True,
        "paired_entities.csv": True,
    }
    assert len(document["outputs"]) == 12
    for name, digest in document["outputs"].items():
        assert file_hash(tmp_path / name) == digest
        assert b"\r" not in (tmp_path / name).read_bytes()
    assert b"\r" not in (tmp_path / "provenance.json").read_bytes()
    table = pd.read_csv(tmp_path / "npm_inference.csv")
    assert len(table) == 24 and set(table.status) == {"post-hoc"}
    with pytest.raises(SystemExit, match="refusing to overwrite"):
        dynamic.main()

"""The Study 2 inference command on toy run directories of both components; no model is loaded."""

import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.stats import poisson

import scripts.study2_inference as inference_command
from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.evaluation.reviews import benjamini_hochberg
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes
from pulsegraph.study2.constants import BASELINES, MODEL_PINS, SEEDS, VARIANTS
from pulsegraph.study2.declarations import comparisons, specification
from pulsegraph.study2.distributions import CountLaw, complete, fm_hurdle
from pulsegraph.study2.models import count_laws, law_forecast, occurrence
from pulsegraph.study2.runner import _evaluate
from pulsegraph.study2.synthetic import cells, generate, grid_manifest

DATES = pd.date_range("2025-09-01", "2026-08-31")
STRATA = {"p0": "dense", "@s/q0": "dense", "p1": "sparse", "p2": "sparse", "p3": "very_sparse"}


class Pool:
    """Registered forecast shapes. chronos2_hurdle sees the truth (so it must win E01 and E02);
    timesfm3_hurdle is its own completed control (so E07 and E10 tie at every entity)."""

    def __init__(self, truth):
        self.truth = truth

    def forecast(self, context, horizon, key):
        label, cutoff = key.rsplit(":", 1)
        series = self.truth[tuple(json.loads(label))]
        start = int(cutoff) if cutoff.isdigit() else series.index.get_loc(pd.Timestamp(cutoff))
        target = np.asarray(series.iloc[start : start + horizon], dtype=float)
        level = float(np.mean(context[-28:]))
        deciles = np.floor(level * np.linspace(0.25, 1.75, 9))
        completed = complete(deciles)
        forecasts = {}
        for name in MODEL_PINS:
            forecasts[f"{name}_raw"] = dict(
                deciles=np.tile(deciles, (horizon, 1)).tolist(), distributions=None, metadata={}
            )
            forecasts[f"{name}_completed"] = law_forecast([completed] * horizon)
            forecasts[f"{name}_hurdle"] = law_forecast(
                [fm_hurdle(completed, occurrence(context))] * horizon
            )
        forecasts["timesfm3_hurdle"] = forecasts["timesfm3_completed"]
        forecasts["chronos2_hurdle"] = law_forecast(
            [CountLaw(dict(kind="point", value=int(y))) for y in target]
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


def _write_family(root, component):
    for kind in ("comparisons", "spec"):
        source = ROOT_DIR / f"study/study2/{component}_{kind}.json"
        (root / "study/study2").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, root / f"study/study2/{component}_{kind}.json")


@pytest.fixture(scope="module")
def external_run(tmp_path_factory):
    root = tmp_path_factory.mktemp("external")
    rng = np.random.default_rng(7)
    truth = {
        ("packages", key): pd.Series(rng.poisson(rate, len(DATES)).astype(float), index=DATES)
        # Every target week holds positive days, so no reference is perfect on a whole series.
        for key, rate in zip(STRATA, (6.0, 3.0, 1.5, 1.0, 0.7), strict=True)
    }
    manifest = root / "manifest.json"
    atomic_json(
        manifest,
        dict(series=[dict(series_id=key, stratum=stratum) for key, stratum in STRATA.items()]),
    )
    metadata = dict(
        readiness=dict(
            action="external_packages",
            panels=dict(
                packages=dict(manifest=dict(path=str(manifest), sha256=file_hash(manifest)))
            ),
        ),
        spec=specification("external_packages"),
        family=comparisons("external_packages"),
        metadata=dict(implementation_commit="a" * 40),
        readiness_sha256="b" * 64,
    )
    run = root / "run"
    _evaluate(truth, run, Pool(truth), metadata=metadata)
    return root, run, truth


@pytest.fixture(scope="module")
def external_outputs(external_run, tmp_path_factory):
    root, run, _ = external_run
    out = tmp_path_factory.mktemp("external-inference") / "inference"
    inference_command.run_inference("external_packages", run, out=out, root=ROOT_DIR)
    return out


TOY_CELLS = [c["cell_id"] for c in cells()[:3]]
TOY_REPLICATES = range(4)


def _toy_grid():
    manifest = grid_manifest()
    return dict(
        manifest,
        cells=[c for c in manifest["cells"] if c["cell_id"] in TOY_CELLS],
        series=[
            row
            for row in manifest["series"]
            if row["cell_id"] in TOY_CELLS and row["replicate"] in TOY_REPLICATES
        ],
    )


@pytest.fixture(scope="module")
def synthetic_run(tmp_path_factory):
    root = tmp_path_factory.mktemp("synthetic")
    _write_family(root, "synthetic")
    atomic_json(root / "study/study2/grid_manifest.json", _toy_grid())
    lookup = {c["cell_id"]: c for c in cells()}
    truth = {
        ("synthetic", row["series_id"]): pd.Series(
            generate(lookup[row["cell_id"]], row["replicate"]).astype(float)
        )
        for row in _toy_grid()["series"]
    }
    metadata = dict(
        readiness=dict(action="synthetic"),
        spec=specification("synthetic"),
        family=comparisons("synthetic"),
        metadata=dict(implementation_commit="a" * 40),
        readiness_sha256="b" * 64,
    )
    run = root / "run"
    _evaluate(truth, run, Pool(truth), metadata=metadata, synthetic=True)
    return root, run


@pytest.fixture(scope="module")
def synthetic_outputs(synthetic_run, tmp_path_factory):
    root, run = synthetic_run
    out = tmp_path_factory.mktemp("synthetic-inference") / "inference"
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inference_command, "grid_manifest", _toy_grid)
        inference_command.run_inference("synthetic", run, out=out, root=root)
    return out


def _rows(run):
    state = read_json(run / "run.json")
    return [
        row
        for label in state["completed"]
        for row in read_json(run / (sha256_bytes(label.encode()) + ".json"))["rows"]
    ]


def test_the_external_family_is_e01_to_e18_with_one_bh_and_the_series_as_entity(
    external_outputs,
):
    table = pd.read_csv(external_outputs / "inference.csv")
    assert list(table.id) == [f"E{i:02}" for i in range(1, 19)]
    assert (table.declared_count == 18).all() and (table.n_entities == len(STRATA)).all()
    assert set(table.entity) == {"series"} and (table.n_bootstrap == 20000).all()
    family = comparisons("external_packages")["comparisons"]
    assert table[["id", "domain", "model", "reference", "horizon"]].to_dict("records") == family
    pairs = pd.read_csv(external_outputs / "paired_entities.csv", keep_default_na=False)
    assert len(pairs) == 18 * len(STRATA) and set(pairs.entity_kind) == {"series"}
    assert sorted(pairs.entity.unique()) == sorted(STRATA)
    assert np.allclose(pairs.difference, pairs.model_score - pairs.reference_score)
    document = read_json(external_outputs / "inference.json")
    assert document["comparison_family"] == comparisons("external_packages")
    assert document["settings"]["interval"]["numpy_quantile_method"] == "linear"
    assert len(document["confirmatory"]) == 18


def test_differences_are_model_minus_reference_and_ties_are_exact_zeros(external_outputs):
    table = pd.read_csv(external_outputs / "inference.csv").set_index("id")
    n = len(STRATA)
    # chronos2_hurdle forecasts the truth, so it beats both references at every series.
    for test in ("E01", "E02", "E04", "E05"):
        row = table.loc[test]
        assert row.mean_diff < 0 and row.model_mean == 0 and row.reference_mean > 0
        assert (row.wins, row.ties, row.losses) == (n, 0, 0)
        assert row.mean_diff_ci_high < 0 and row.median_diff < 0
    # timesfm3_hurdle is its own completed control: every difference is exactly zero.
    for test in ("E07", "E10"):
        row = table.loc[test]
        assert (row.wins, row.ties, row.losses, row.n_nonzero) == (0, n, 0, 0)
        assert row.mean_diff == row.mean_diff_ci_low == row.mean_diff_ci_high == 0
        assert row.wilcoxon_p == 1.0


def test_aggregation_averages_origins_within_series_then_weighs_series_equally(
    external_run, external_outputs
):
    _, run, _ = external_run
    rows = pd.DataFrame(
        [
            dict(series_id=r["series_id"], horizon=r["horizon"], model=r["model"], **r["scores"])
            for r in _rows(run)
        ]
    )
    table = pd.read_csv(external_outputs / "inference.csv").set_index("id")
    for comparison in comparisons("external_packages")["comparisons"]:
        selected = rows[rows.horizon.eq(comparison["horizon"])]
        per = selected.groupby(["model", "series_id"]).qscore9.mean()
        diff = per[comparison["model"]] - per[comparison["reference"]]
        assert len(diff) == len(STRATA)
        row = table.loc[comparison["id"]]
        assert row.mean_diff == pytest.approx(diff.mean(), rel=1e-12, abs=1e-15)
        assert row.median_diff == pytest.approx(diff.median(), rel=1e-12, abs=1e-15)
        assert row.wins == (diff < 0).sum() and row.losses == (diff > 0).sum()
        p = inference_command.cluster_contrast(
            diff.sort_index().to_numpy(),
            seed=inference_command.bootstrap_seed("external_packages", comparison, "qscore9"),
            family=comparisons("external_packages"),
        )["wilcoxon_p"]
        assert row.wilcoxon_p == pytest.approx(p, rel=1e-12)


def test_bh_is_applied_once_over_the_whole_family(external_outputs):
    table = pd.read_csv(external_outputs / "inference.csv")
    p = table.wilcoxon_p.to_numpy()
    m, order = len(p), np.argsort(p)
    expected = np.empty(m)
    for position, index in enumerate(order):
        expected[index] = min(
            1.0, min(p[j] * m / (k + 1) for k, j in enumerate(order[position:], position))
        )
    assert np.allclose(table.wilcoxon_p_bh, expected, rtol=1e-12, atol=0)
    assert (table.reject_bh_005 == (table.wilcoxon_p_bh <= 0.05)).all()
    assert np.allclose(
        benjamini_hochberg([0.01, 0.04, 0.03, 0.5]), [0.04, 0.16 / 3, 0.16 / 3, 0.5], rtol=1e-12
    )


def test_seeds_are_derived_from_the_roots_by_the_declared_sha256_rule(external_outputs):
    def derived(*parts):
        payload = json.dumps(list(parts), sort_keys=True, allow_nan=False).encode("utf-8")
        return int.from_bytes(hashlib.sha256(payload).digest()[:4], "little")

    family = comparisons("external_packages")
    # Fixed before any Study 2 score exists; any change to the derivation changes these numbers.
    assert (
        inference_command.bootstrap_seed("external_packages", family["comparisons"][0], "qscore9")
        == derived(
            20260917,
            "external_packages",
            "E01",
            "packages",
            "chronos2_hurdle",
            "chronos2_completed",
            7,
            "qscore9",
        )
        == 4064020396
    )
    synthetic = comparisons("synthetic")["comparisons"][0]
    assert inference_command.bootstrap_seed("synthetic", synthetic, "qscore9") == 3742483908
    table = pd.read_csv(external_outputs / "inference.csv")
    for row, comparison in zip(table.to_dict("records"), family["comparisons"], strict=True):
        assert row["bootstrap_root"] == SEEDS["bootstrap"] == 20260917
        assert row["bootstrap_seed"] == derived(
            20260917,
            "external_packages",
            comparison["id"],
            comparison["domain"],
            comparison["model"],
            comparison["reference"],
            comparison["horizon"],
            "qscore9",
        )
    assert table.bootstrap_seed.is_unique
    assert (
        inference_command.pit_seed("synthetic", "synthetic", "cell00/rep00", "180", 30, "oracle")
        == derived(20260916, "synthetic", "synthetic", "cell00/rep00", "180", 30, "oracle")
        == 114759717
    )
    provenance = read_json(external_outputs / "provenance.json")
    assert provenance["seeds"]["bootstrap_root"] == 20260917
    assert provenance["seeds"]["pit_root"] == 20260916
    assert "SHA-256" in provenance["seeds"]["bootstrap_derivation"]
    assert provenance["seeds"]["comparison_seeds"] == dict(zip(table.id, table.bootstrap_seed))
    secondary = pd.read_csv(external_outputs / "secondary_contrasts.csv")
    seeds = secondary.bootstrap_seed.dropna().astype(int)
    assert seeds.is_unique and not set(seeds) & set(table.bootstrap_seed)


def test_a_hand_checkable_bootstrap_and_signed_rank_case():
    family = comparisons("synthetic")
    result = inference_command.cluster_contrast([-3, -1, 2, 0, -4], seed=1, family=family)
    # Zeros omitted: |d| = 3, 1, 2, 4 ranks 3, 1, 2, 4; T = min(2, 8) = 2, n = 4.
    z = (2 - 4 * 5 / 4) / math.sqrt(4 * 5 * 9 / 24)
    assert result["wilcoxon_p"] == pytest.approx(math.erfc(abs(z) / math.sqrt(2)), rel=1e-12)
    assert (result["wins"], result["ties"], result["losses"], result["n_nonzero"]) == (3, 1, 1, 4)
    assert result["mean_diff"] == -1.2 and result["median_diff"] == -1.0
    # The percentile interval, recomputed from the declared draws and NumPy's linear quantile.
    diff = np.array([-3.0, -1.0, 2.0, 0.0, -4.0])
    rng = np.random.default_rng(1)
    means = np.concatenate(
        [
            diff[rng.integers(0, 5, size=(min(256, 20000 - start), 5))].mean(axis=1)
            for start in range(0, 20000, 256)
        ]
    )
    assert result["mean_diff_ci_low"] == np.quantile(means, (1 - 0.95) / 2)
    assert result["mean_diff_ci_high"] == np.quantile(means, 1 - (1 - 0.95) / 2)
    # Two entities, 0 and 1: the bootstrap mean is 0, 1/2 or 1 with mass 1/4, 1/2, 1/4.
    two = inference_command.cluster_contrast([0.0, 1.0], seed=5, family=family)
    assert (two["mean_diff_ci_low"], two["mean_diff_ci_high"]) == (0.0, 1.0)
    constant = inference_command.cluster_contrast([0.5] * 4, seed=5, family=family)
    assert constant["mean_diff_ci_low"] == constant["mean_diff_ci_high"] == 0.5
    # Four tied |d| share rank 2.5: the variance loses (4**3 - 4) / 48, so z = -5 / 2.5 = -2.
    z = (0 - 4 * 5 / 4) / math.sqrt(4 * 5 * 9 / 24 - (4**3 - 4) / 48)
    assert z == -2.0
    assert constant["wilcoxon_p"] == pytest.approx(math.erfc(2 / math.sqrt(2)), rel=1e-12)
    zeros = inference_command.cluster_contrast([0.0] * 6, seed=5, family=family)
    assert zeros["wilcoxon_p"] == 1.0 and zeros["ties"] == 6 and zeros["n_nonzero"] == 0
    with pytest.raises(ValueError, match="at least two"):
        inference_command.cluster_contrast([0.3], seed=5, family=family)
    with pytest.raises(ValueError, match="finite"):
        inference_command.cluster_contrast([0.3, np.nan], seed=5, family=family)


def test_the_synthetic_family_pairs_replicate_blocks_with_equal_cell_weight(
    synthetic_run, synthetic_outputs
):
    _, run = synthetic_run
    table = pd.read_csv(synthetic_outputs / "inference.csv").set_index("id")
    assert list(table.index) == [f"S0{i}" for i in range(1, 7)]
    assert set(table.entity) == {"replicate"} and (table.declared_count == 6).all()
    assert (table.n_entities == len(TOY_REPLICATES)).all() and set(table.horizon) == {30}
    rows = pd.DataFrame(
        [
            dict(
                cell=r["series_id"].split("/")[0],
                replicate=int(r["series_id"][-2:]),
                cutoff=r["cutoff"],
                horizon=r["horizon"],
                model=r["model"],
                qscore9=r["scores"]["qscore9"],
            )
            for r in _rows(run)
        ]
    )
    assert set(rows.cutoff) == {"180", "210", "240"} and "oracle" in set(rows.model)
    pairs = pd.read_csv(synthetic_outputs / "paired_entities.csv")
    for comparison in comparisons("synthetic")["comparisons"]:
        h30 = rows[rows.horizon.eq(30)]
        cell = h30.groupby(["model", "replicate", "cell"]).qscore9.mean()
        block = cell.groupby(["model", "replicate"]).mean()
        diff = block[comparison["model"]] - block[comparison["reference"]]
        mine = pairs[pairs.id.eq(comparison["id"])].set_index("entity").difference
        assert list(mine.index) == list(TOY_REPLICATES)
        assert np.allclose(mine.to_numpy(), diff.to_numpy(), rtol=1e-12, atol=1e-15)
        assert table.loc[comparison["id"]].mean_diff == pytest.approx(diff.mean(), rel=1e-12)
    for test in ("S01", "S02"):
        assert table.loc[test].wins == len(TOY_REPLICATES)
    assert table.loc["S03"].ties == len(TOY_REPLICATES) and table.loc["S03"].wilcoxon_p == 1.0


def test_the_registered_grid_has_thirty_blocks_of_all_eighteen_cells():
    labels = inference_command.expected_series("synthetic", {}, ROOT_DIR)
    assert len(labels) == 540
    blocks = {}
    for label in labels.values():
        blocks.setdefault(label["replicate"], set()).add(label["cell_id"])
    assert sorted(blocks) == list(range(30))
    assert all(len(cells_) == 18 for cells_ in blocks.values())


def test_synthetic_secondary_tables_hold_horizon_7_per_cell_and_the_oracle(synthetic_outputs):
    contrasts = pd.read_csv(synthetic_outputs / "secondary_contrasts.csv")
    h7 = contrasts[contrasts.metric.eq("qscore9")]
    assert sorted(h7.id) == sorted(f"S0{i}-h7" for i in range(1, 7)) and set(h7.horizon) == {7}
    assert set(contrasts.metric) == {
        "qscore9",
        "context_scaled_qscore9",
        "occurrence_brier",
        "discrete_crps",
    }
    assert (contrasts.status == "secondary").all()
    cell_scores = pd.read_csv(synthetic_outputs / "secondary_cells.csv")
    assert set(cell_scores.cell_id) == set(TOY_CELLS)
    assert (cell_scores.n_entities == len(TOY_REPLICATES)).all()
    assert "oracle" in set(cell_scores.model)
    cell_contrasts = pd.read_csv(synthetic_outputs / "secondary_cells_contrasts.csv")
    assert len(cell_contrasts) == len(TOY_CELLS) * 12 * 2
    assert (cell_contrasts.wins + cell_contrasts.ties + cell_contrasts.losses == 4).all()
    scores = pd.read_csv(synthetic_outputs / "secondary_scores.csv")
    oracle = scores[scores.model.eq("oracle")]
    assert len(oracle) == 2 and (oracle.discrete_crps_n_entities == len(TOY_REPLICATES)).all()


def test_external_secondary_tables_report_availability_and_strata_with_n(external_outputs):
    scores = pd.read_csv(external_outputs / "secondary_scores.csv")
    assert len(scores) == 2 * len(VARIANTS)
    windows = len(STRATA) * 3
    assert (scores.crps_forecasts == windows).all()
    raw = scores[scores.model.isin(["chronos2_raw", "local_mean_28", "autoets_weekly"])]
    assert (raw.crps_unavailable_no_count_distribution == windows).all()
    assert (raw.occurrence_brier_n_entities == 0).all() and raw.occurrence_brier.isna().all()
    laws = scores[scores.model.isin(["poisson_28", "chronos2_hurdle"])]
    assert (laws.crps_certified + laws.crps_unavailable_bound_not_certified == windows).all()
    contrasts = pd.read_csv(external_outputs / "secondary_contrasts.csv")
    assert len(contrasts) == 18 * 3 and "qscore9" not in set(contrasts.metric)
    raw_brier = contrasts[
        contrasts.model.str.endswith("_raw") & contrasts.metric.eq("occurrence_brier")
    ]
    assert (raw_brier.status == "unavailable").all()
    assert (raw_brier.unavailable_reason == "no_count_distribution").all()
    accounting = pd.read_csv(external_outputs / "secondary_accounting.csv")
    assert np.allclose(accounting.parts_sum, accounting.qscore9, rtol=1e-12, atol=1e-12)
    perfect = accounting[accounting.model.eq("chronos2_hurdle")]
    assert (perfect.qscore9 == 0).all() and (perfect.zero_conditional_mean == 0).all()
    strata = pd.read_csv(external_outputs / "secondary_strata.csv")
    counts = strata.drop_duplicates("stratum").set_index("stratum").n_entities.to_dict()
    assert counts == dict(dense=2, sparse=2, very_sparse=1)
    strata_contrasts = pd.read_csv(external_outputs / "secondary_strata_contrasts.csv")
    assert len(strata_contrasts) == 3 * 18 * 2
    assert set(strata_contrasts.n_entities) == {1, 2}


def test_randomized_pit_draws_recorded_uniforms_within_the_cdf_jumps(
    external_run, external_outputs
):
    _, run, _ = external_run
    values = pd.read_parquet(external_outputs / "pit_values.parquet")
    law_models = [n for n in VARIANTS if n.endswith(("_completed", "_hurdle"))] + list(
        BASELINES[2:]
    )
    assert set(values.model) == set(law_models)
    assert len(values) == len(law_models) * len(STRATA) * 3 * (7 + 30)
    assert ((values.pit >= values.cdf_below) & (values.pit <= values.cdf_at)).all()
    row = next(
        r
        for r in _rows(run)
        if r["model"] == "poisson_28" and r["series_id"] == "p1" and r["horizon"] == 7
    )
    mu, y = row["forecast"]["distributions"][0]["mu"], np.asarray(row["target"], dtype=float)
    seed = int.from_bytes(
        hashlib.sha256(
            json.dumps(
                [20260916, "external_packages", "packages", "p1", row["cutoff"], 7, "poisson_28"]
            ).encode()
        ).digest()[:4],
        "little",
    )
    v = np.random.default_rng(seed).random(7)
    expected = poisson.cdf(y - 1, mu) + v * (poisson.cdf(y, mu) - poisson.cdf(y - 1, mu))
    mine = values[
        values.model.eq("poisson_28")
        & values.series_id.eq("p1")
        & values.cutoff.eq(row["cutoff"])
        & values.horizon.eq(7)
    ].sort_values("lead")
    assert np.allclose(mine.v, v, rtol=0, atol=0) and (mine.seed == seed).all()
    assert np.allclose(mine.pit, expected, rtol=1e-12, atol=1e-12)
    perfect = values[values.model.eq("chronos2_hurdle")]
    assert np.array_equal(perfect.pit.to_numpy(), perfect.v.to_numpy())
    histograms = pd.read_csv(external_outputs / "pit_histograms.csv")
    available = histograms[histograms.status.eq("available")]
    bins = [f"bin{b:02}" for b in range(1, 11)]
    assert (available[bins].sum(axis=1) == available.n_values).all()
    assert set(histograms.loc[histograms.status.eq("unavailable"), "model"]) == {
        "chronos2_raw",
        "timesfm3_raw",
        "timesfm2p5_raw",
        "local_mean_28",
        "autoets_weekly",
    }


def _copy_run(run, destination):
    shutil.copytree(run, destination)
    return destination


def _rewrite_checkpoint(run, change, label=None):
    state = read_json(run / "run.json")
    label = sorted(state["completed"])[0] if label is None else label
    path = run / (sha256_bytes(label.encode()) + ".json")
    document = read_json(path)
    document["rows"] = change(document["rows"])
    atomic_json(path, document)
    state["completed"][label] = file_hash(path)
    atomic_json(run / "run.json", state)


def test_refuses_a_comparison_file_with_a_missing_or_extra_comparison(external_run, tmp_path):
    _, run, _ = external_run
    family = comparisons("external_packages")
    extra = dict(family["comparisons"][0], id="E19")
    for rows in (family["comparisons"][:17], family["comparisons"] + [extra]):
        for count in (len(rows), 18):
            path = tmp_path / f"family-{len(rows)}-{count}.json"
            atomic_json(path, dict(family, comparisons=rows, comparison_count=count))
            with pytest.raises(ValueError, match="declaration"):
                inference_command.run_inference(
                    "external_packages", run, out=tmp_path / "out", comparisons=path
                )
    assert not (tmp_path / "out").exists()


def test_refuses_a_run_whose_family_or_grid_differs(external_run, tmp_path):
    root, run, truth = external_run
    family = comparisons("external_packages")
    short = dict(family, comparisons=family["comparisons"][:17], comparison_count=17)
    state = read_json(run / "run.json")
    other = tmp_path / "other"
    _evaluate(
        {key: truth[key] for key in list(truth)},
        other,
        Pool(truth),
        metadata=dict(state["metadata"], family=short),
    )
    cases = [(other, "registered family")]
    missing = _copy_run(run, tmp_path / "missing")
    _rewrite_checkpoint(missing, lambda rows: [r for r in rows if r["model"] != "poisson_28"])
    cases.append((missing, "incomplete"))
    duplicate = _copy_run(run, tmp_path / "duplicate")
    _rewrite_checkpoint(duplicate, lambda rows: rows + rows[:1])
    cases.append((duplicate, "incomplete or has duplicate"))
    changed = _copy_run(run, tmp_path / "changed")
    label = sorted(read_json(changed / "run.json")["completed"])[0]
    with (changed / (sha256_bytes(label.encode()) + ".json")).open("a") as stream:
        stream.write(" ")
    cases.append((changed, "Checkpoint hash mismatch"))
    failed = _copy_run(run, tmp_path / "failed")
    atomic_json(failed / "run.json", dict(read_json(run / "run.json"), status="failed"))
    cases.append((failed, "complete run"))
    for directory, message in cases:
        with pytest.raises(ValueError, match=message):
            inference_command.run_inference(
                "external_packages", directory, out=tmp_path / "out", root=ROOT_DIR
            )
    with pytest.raises(ValueError, match="registered family|differs from registration"):
        inference_command.run_inference("synthetic", run, out=tmp_path / "out", root=ROOT_DIR)
    assert not (tmp_path / "out").exists()


def test_refuses_a_run_missing_a_registered_series(external_run, tmp_path):
    _, run, truth = external_run
    state = read_json(run / "run.json")
    partial = tmp_path / "partial"
    keys = list(truth)[:-1]
    _evaluate({k: truth[k] for k in keys}, partial, Pool(truth), metadata=state["metadata"])
    with pytest.raises(ValueError, match="checkpoints differ"):
        inference_command.run_inference(
            "external_packages", partial, out=tmp_path / "out", root=ROOT_DIR
        )


def test_outputs_are_immutable_and_hashed_in_the_provenance(external_run, external_outputs):
    _, run, _ = external_run
    with pytest.raises(FileExistsError):
        inference_command.run_inference("external_packages", run, out=external_outputs)
    provenance = read_json(external_outputs / "provenance.json")
    names = sorted(p.name for p in external_outputs.iterdir() if p.name != "provenance.json")
    assert sorted(provenance["artifact_sha256"]) == names
    for name, digest in provenance["artifact_sha256"].items():
        assert file_hash(external_outputs / name) == digest
    assert provenance["run"]["run_json_sha256"] == file_hash(run / "run.json")
    assert provenance["run"]["checkpoints"] == len(STRATA)
    assert provenance["inference_script_sha256"] == file_hash(
        ROOT_DIR / "scripts/study2_inference.py"
    )
    for name in names:
        if name.endswith((".csv", ".json")):
            assert b"\r" not in (external_outputs / name).read_bytes()


def test_command_line_writes_under_the_run_directory(external_run, tmp_path, monkeypatch):
    _, run, _ = external_run
    copy = _copy_run(run, tmp_path / "run")
    monkeypatch.setattr(
        sys, "argv", ["study2_inference.py", "external_packages", "--run", str(copy)]
    )
    inference_command.main()
    assert (copy / "inference" / "inference.csv").exists()
    assert read_json(copy / "inference" / "provenance.json")["command"][-3:] == [
        "external_packages",
        "--run",
        str(copy),
    ]
    result = subprocess.run(
        [sys.executable, "-m", "scripts.study2_inference", "--help"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=Path(__file__).resolve().parents[1],
    )
    assert result.returncode == 0 and "usage:" in result.stdout


def test_uncertified_crps_is_counted_and_leaves_the_family_unchanged(
    external_run, external_outputs, tmp_path
):
    _, run, _ = external_run
    copy = _copy_run(run, tmp_path / "run")

    def uncertify(rows):
        # As scores.py records a forecast whose CRPS bound is not certified by k = 1,000,000.
        for row in rows:
            if row["forecast"].get("distributions") is not None and row["cutoff"] == "2026-07-03":
                row["scores"].update(
                    discrete_crps=None,
                    crps_max_residual_bound=None,
                    crps_last_k=None,
                    crps_unavailable_reason="crps_bound_not_certified",
                )
        return rows

    _rewrite_checkpoint(
        copy, uncertify, label=json.dumps(["packages", "p0"], separators=(",", ":"))
    )
    out = tmp_path / "inference"
    inference_command.run_inference("external_packages", copy, out=out, root=ROOT_DIR)
    pd.testing.assert_frame_equal(
        pd.read_csv(out / "inference.csv"), pd.read_csv(external_outputs / "inference.csv")
    )
    scores = pd.read_csv(out / "secondary_scores.csv")
    laws = scores[scores.crps_with_count_distribution > 0]
    assert len(laws) == 2 * 11
    assert (laws.crps_unavailable_bound_not_certified == 1).all()
    assert (laws.crps_certified == len(STRATA) * 3 - 1).all()
    assert (laws.discrete_crps_n_entities == len(STRATA) - 1).all()
    assert (laws.occurrence_brier_n_entities == len(STRATA)).all()
    contrasts = pd.read_csv(out / "secondary_contrasts.csv")
    crps = contrasts[contrasts.metric.eq("discrete_crps") & contrasts.status.eq("secondary")]
    assert len(crps) == 12
    assert (crps.n_entities == len(STRATA) - 1).all() and (crps.n_entities_unavailable == 1).all()

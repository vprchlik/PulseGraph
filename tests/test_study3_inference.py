"""Study 3's per-stratum inference and integrity on a toy run with three strata, one short."""

import json
import shutil
import sys

import numpy as np
import pandas as pd
import pytest
from test_study2_inference import DATES
from test_study3_variants import Study3Pool

import scripts.study2_inference as study2_inference
import scripts.study3_inference as inference_command
import scripts.study3_integrity as integrity_command
from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.evaluation.reviews import benjamini_hochberg
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes
from pulsegraph.random import derived_seed
from pulsegraph.study2.constants import MODEL_PINS, STUDY3_FILES, STUDY3_VARIANTS
from pulsegraph.study2.runner import _evaluate

SIZES = dict(dense=10, sparse=10, very_sparse=3)
RATES = dict(dense=5.0, sparse=0.8, very_sparse=0.08)


def _strata():
    return {f"{s[0]}{i:02}": s for s, n in SIZES.items() for i in range(n)}


@pytest.fixture(scope="module")
def toy(tmp_path_factory):
    """A complete toy Study 3 run: ten dense, ten sparse and three very sparse series."""
    root = tmp_path_factory.mktemp("study3-run")
    strata = _strata()
    rng = np.random.default_rng(23)
    truth = {}
    for key, stratum in strata.items():
        rate = RATES[stratum] * (0.6 + 0.8 * rng.random())
        values = rng.poisson(rate, len(DATES)).astype(float)
        if stratum != "dense":
            values[DATES.get_loc(pd.Timestamp("2026-05-20"))] = 2.0
        truth[("nyc311", key)] = pd.Series(values, index=DATES)
    manifest = root / "manifest.json"
    atomic_json(
        manifest,
        dict(
            domain="nyc311",
            series=[dict(series_id=key, stratum=stratum) for key, stratum in strata.items()],
        ),
    )
    spec, family = (read_json(ROOT_DIR / name) for name in STUDY3_FILES)
    metadata = dict(
        readiness=dict(
            action="study3",
            domain="nyc311",
            panels=dict(nyc311=dict(manifest=dict(path=str(manifest), sha256=file_hash(manifest)))),
        ),
        spec=spec,
        family=family,
        metadata=dict(implementation_commit="a" * 40),
        readiness_sha256="b" * 64,
    )
    run = root / "run"
    _evaluate(truth, run, Study3Pool(), metadata=metadata, variants=STUDY3_VARIANTS)
    out = root / "inference"
    inference_command.run_inference(run, out=out, root=ROOT_DIR)
    return root, run, out, family


def _saved(run):
    state = read_json(run / "run.json")
    rows = []
    for label in state["completed"]:
        rows.extend(read_json(run / (sha256_bytes(label.encode()) + ".json"))["rows"])
    return rows


def _means(run, metric="qscore9"):
    strata = _strata()
    frame = pd.DataFrame(
        [
            dict(
                stratum=strata[r["series_id"]],
                series_id=r["series_id"],
                horizon=r["horizon"],
                model=r["model"],
                value=r["scores"][metric]
                if metric != "zero"
                else r["scores"]["contributions"]["zero"],
            )
            for r in _saved(run)
        ]
    )
    return frame.groupby(["stratum", "horizon", "model", "series_id"]).value.mean()


def _read(out, name):
    return pd.read_csv(
        out / name, keep_default_na=False, na_values=[""], float_precision="round_trip"
    )


def test_the_family_is_tested_within_strata_and_a_short_stratum_is_unavailable(toy):
    _, run, out, family = toy
    table = _read(out, "inference.csv").set_index("id")
    assert list(table.index) == [f"R{i:02}" for i in range(1, 37)]
    short = [f"R{i:02}" for i in range(25, 37)]
    assert set(table.loc[short, "stratum"]) == {"very_sparse"}
    assert (table.loc[short, "status"] == "unavailable").all()
    assert (table.loc[short, "unavailable_reason"] == "fewer_than_ten_complete_series").all()
    assert table.loc[short, ["wilcoxon_p", "wilcoxon_p_bh", "mean_diff"]].isna().all().all()
    assert table.loc[short, "reject_bh_005"].isna().all()
    assert (table.loc[short, "n_entities"] == 3).all()
    available = table[table.status.eq("available")]
    assert (
        len(available) == 24 and (table.bh_count == 24).all() and (table.declared_count == 36).all()
    )
    # BH once over the 24 available tests, never over the 36.
    assert np.allclose(
        available.wilcoxon_p_bh, benjamini_hochberg(available.wilcoxon_p), rtol=0, atol=0
    )
    assert (available.reject_bh_005 == (available.wilcoxon_p_bh <= 0.05)).all()
    means = _means(run)
    for cid, row in available.iterrows():
        assert row.n_entities == SIZES[row.stratum]
        variant = means.loc[(row.stratum, row.horizon, row.variant)]
        reference = means.loc[(row.stratum, row.horizon, row.reference)]
        diff = (variant - reference).sort_index().to_numpy()
        seed = derived_seed(
            20261004,
            "study3",
            cid,
            row.stratum,
            row.variant,
            row.reference,
            int(row.horizon),
            "qscore9",
        )
        assert row.bootstrap_seed == seed
        result = study2_inference.cluster_contrast(diff, seed=seed, family=family)
        for name in (
            "mean_diff",
            "median_diff",
            "wilcoxon_p",
            "mean_diff_ci_low",
            "mean_diff_ci_high",
        ):
            assert row[name] == pytest.approx(result[name], rel=1e-12, abs=1e-15)
        assert (row.wins, row.ties, row.losses) == (
            result["wins"],
            result["ties"],
            result["losses"],
        )
        assert row.median_sign == (
            "negative" if row.median_diff < 0 else "positive" if row.median_diff > 0 else "zero"
        )
        if row.contrast == "T1":
            expected = family["predicted_t1_sign"][row.stratum]
            assert row.predicted_sign == expected
            assert bool(row.median_as_predicted) == (row.median_sign == expected)
        else:
            assert pd.isna(row.predicted_sign)
    pairs = _read(out, "paired_entities.csv")
    assert len(pairs) == 12 * 10 + 12 * 10
    assert set(pairs.id) == set(available.index)
    assert np.allclose(pairs.difference, pairs.variant_score - pairs.reference_score)


def test_the_inference_document_records_the_rule_and_the_seeds(toy):
    _, run, out, family = toy
    document = read_json(out / "inference.json")
    assert document["comparison_family"] == family
    assert document["settings"]["strata_sizes"] == SIZES
    assert document["settings"]["adjustment"]["available"] == 24
    assert document["settings"]["adjustment"]["declared"] == 36
    assert document["pit"]["root"] == 20261003
    provenance = read_json(out / "provenance.json")
    assert provenance["inference_script_sha256"] == file_hash(
        ROOT_DIR / "scripts/study3_inference.py"
    )
    assert provenance["study2_functions_sha256"] == file_hash(
        ROOT_DIR / "scripts/study2_inference.py"
    )
    assert provenance["run"]["checkpoints"] == sum(SIZES.values())
    for name, digest in provenance["artifact_sha256"].items():
        assert file_hash(out / name) == digest
        if not name.endswith(".parquet"):
            assert b"\r" not in (out / name).read_bytes()
    values = pd.read_parquet(out / "pit_values.parquet")
    row = values.iloc[0]
    assert row.seed == derived_seed(
        20261003, "study3", "nyc311", row.series_id, row.cutoff, int(row.horizon), row.model
    )
    assert set(values.domain) == {"nyc311"}


def test_the_secondary_tables_are_declared_and_unadjusted(toy):
    _, run, out, _ = toy
    strata = _read(out, "secondary_strata_contrasts.csv")
    assert set(strata.stratum) == {"dense", "sparse", "very_sparse"}
    for model in MODEL_PINS:
        for variant in (f"{model}_hurdle", f"{model}_occurrence_model_size_count"):
            pairs = set(strata.loc[strata.variant.eq(variant), "reference"])
            assert pairs == {f"{model}_completed", "hurdle_count_28", "hurdle_empirical_28"}
    family_pairs = strata.variant.str.endswith("_hurdle_dynamic")
    assert "qscore9" not in set(strata.loc[family_pairs, "metric"])  # the family's own metric
    assert set(strata.metric) == {
        "qscore9",
        "context_scaled_qscore9",
        "occurrence_brier",
        "discrete_crps",
    }
    assert "wilcoxon_p_bh" not in strata.columns
    means = _means(run)
    row = strata[
        strata.stratum.eq("very_sparse")
        & strata.variant.eq("chronos2_occurrence_model_size_count")
        & strata.reference.eq("hurdle_count_28")
        & strata.horizon.eq(30)
        & strata.metric.eq("qscore9")
    ].iloc[0]
    diff = (
        means.loc[("very_sparse", 30, row.variant)] - means.loc[("very_sparse", 30, row.reference)]
    )
    assert row.n_entities == 3 and row.mean_diff == pytest.approx(diff.mean(), rel=1e-12)
    form = _read(out, "secondary_pooled_study2_form.csv")
    qscore = form[form.metric.eq("qscore9")]
    assert list(qscore.id) == [f"P{i:02}" for i in range(1, 19)]
    assert set(qscore.stratum) == {"all"} and (qscore.n_entities == sum(SIZES.values())).all()
    assert np.allclose(
        qscore.wilcoxon_p_bh_within_table, benjamini_hochberg(qscore.wilcoxon_p), rtol=0, atol=0
    )
    assert set(qscore.reference) == {"local_mean_28", "hurdle_count_28"} | {
        f"{m}_completed" for m in MODEL_PINS
    }
    pooled = _read(out, "secondary_pooled_contrasts.csv")
    assert set(pooled.stratum) == {"all"} and (pooled.n_entities == 23).any()
    scores = _read(out, "secondary_scores.csv")
    assert set(scores.stratum) == {"dense", "sparse", "very_sparse", "all"}
    assert set(scores.model) == set(STUDY3_VARIANTS)
    accounting = _read(out, "secondary_accounting.csv")
    assert np.allclose(accounting.parts_sum, accounting.qscore9, rtol=1e-12, atol=1e-12)
    histograms = _read(out, "pit_histograms.csv")
    raw = histograms[histograms.model.str.endswith("_raw")]
    assert (raw.status == "unavailable").all()
    new = histograms[histograms.model.str.endswith(("_hurdle_dynamic", "_size_count"))]
    assert (new.status == "available").all() and (new.n_values > 0).all()


def test_the_family_descriptors_cover_every_stratum_with_two_series(toy):
    _, run, out, _ = toy
    descriptors = _read(out, "family_descriptors.csv").set_index("id")
    assert len(descriptors) == 36
    short = descriptors[descriptors.stratum.eq("very_sparse")]
    assert (short.n_entities == 3).all() and (~short.tests_available.astype(bool)).all()
    means = _means(run)
    family = read_json(ROOT_DIR / STUDY3_FILES[1])["comparisons"]
    for comparison in family:
        row = descriptors.loc[comparison["id"]]
        key = (comparison["stratum"], comparison["horizon"])
        variant = means.loc[(*key, comparison["variant"])]
        reference = means.loc[(*key, comparison["reference"])]
        diff = variant - reference
        loo = (diff.sum() - diff) / (len(diff) - 1)
        assert row.leave_one_out_min == pytest.approx(loo.min(), rel=1e-12, abs=1e-15)
        assert row.leave_one_out_max == pytest.approx(loo.max(), rel=1e-12, abs=1e-15)
        assert row.most_influential_series == (loo - diff.mean()).abs().idxmax()
        gain = (-diff).clip(lower=0)
        if gain.sum():
            share = gain.nlargest(5).sum() / gain.sum()
            assert row.top_five_share_of_positive_gains == pytest.approx(share, rel=1e-12)


def test_the_family_rule_covers_every_availability_case():
    family = read_json(ROOT_DIR / STUDY3_FILES[1])
    rng = np.random.default_rng(4)
    for sizes, available in (
        (dict(dense=12, sparse=10, very_sparse=11), 36),
        (dict(dense=12, sparse=9, very_sparse=10), 24),
        (dict(dense=10, sparse=0, very_sparse=2), 12),
        (dict(dense=9, sparse=9, very_sparse=9), 0),
    ):
        index = [
            (stratum, horizon, model, f"{stratum}{i}")
            for stratum, n in sizes.items()
            for horizon in (7, 30)
            for model in STUDY3_VARIANTS
            for i in range(n)
        ]
        values = {name: rng.random(len(index)) for name in inference_command.VALUES}
        entities = pd.DataFrame(
            values,
            index=pd.MultiIndex.from_tuples(
                index, names=["stratum", "horizon", "model", "series_id"]
            ),
        ).sort_index()
        table, pairs = inference_command.family_table(family, entities, sizes)
        assert len(table) == 36 and int(table.status.eq("available").sum()) == available
        assert (table.bh_count == available).all()
        ok = table.status.eq("available")
        for stratum, n in sizes.items():
            assert set(table.loc[table.stratum.eq(stratum), "status"]) == {
                "available" if n >= 10 else "unavailable"
            }
        if available:
            assert np.array_equal(
                table.loc[ok, "wilcoxon_p_bh"], benjamini_hochberg(table.loc[ok, "wilcoxon_p"])
            )
        assert table.loc[~ok, "wilcoxon_p_bh"].isna().all()


def test_inference_refuses_an_incomplete_run_a_changed_family_and_an_existing_output(toy, tmp_path):
    root, run, out, _ = toy
    with pytest.raises(FileExistsError):
        inference_command.run_inference(run, out=out, root=ROOT_DIR)
    copy = tmp_path / "run"
    shutil.copytree(run, copy)
    state = read_json(copy / "run.json")
    state["status"] = "running"
    atomic_json(copy / "run.json", state)
    with pytest.raises(ValueError, match="complete run"):
        inference_command.run_inference(copy, out=tmp_path / "a", root=ROOT_DIR)
    other = tmp_path / "root"
    for name in STUDY3_FILES:
        (other / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT_DIR / name, other / name)
    family = read_json(other / STUDY3_FILES[1])
    family["comparisons"] = family["comparisons"][:24]
    family["comparison_count"] = 24
    atomic_json(other / STUDY3_FILES[1], family)
    with pytest.raises(ValueError, match="declaration"):
        inference_command.run_inference(run, out=tmp_path / "b", root=other)


def test_the_integrity_recomputation_covers_the_new_variants(toy, tmp_path):
    _, run, _, _ = toy
    summary = integrity_command.check_run(run, out=tmp_path / "integrity", root=ROOT_DIR)
    assert summary["status"] == "pass" and summary["failed_forecasts"] == 0
    assert summary["grid"]["models"] == list(STUDY3_VARIANTS)
    assert summary["grid"]["forecasts"] == sum(SIZES.values()) * 3 * 2 * 22
    windows = sum(SIZES.values()) * 3 * 2 * len(MODEL_PINS) * 2
    assert summary["checks"]["new_variant_structure"] == dict(windows_checked=windows, failures=0)
    for name in ("qscore9", "occurrence_brier", "context_scaled_qscore9"):
        assert summary["checks"][name]["disagreements"] == 0
    table = pd.read_csv(tmp_path / "integrity" / "integrity.csv")
    new = table[table.model.str.endswith(("_hurdle_dynamic", "_occurrence_model_size_count"))]
    assert len(new) == windows and new.passed.all() and new.has_law.all()


def _tampered(run, tmp_path, name, change):
    copy = tmp_path / name
    shutil.copytree(run, copy)
    state = read_json(copy / "run.json")
    label = sorted(state["completed"])[0]
    path = copy / (sha256_bytes(label.encode()) + ".json")
    document = read_json(path)
    window = change(document["rows"])
    atomic_json(path, document)
    state["completed"][label] = file_hash(path)
    atomic_json(copy / "run.json", state)
    return copy, window


@pytest.mark.parametrize(
    "variant,field,message",
    [
        ("chronos2_hurdle_dynamic", "p", "differs from dynamic_count's"),
        ("timesfm3_occurrence_model_size_count", "p", "differs from the completed's"),
        ("timesfm2p5_occurrence_model_size_count", "positive", "not hurdle_count_28's"),
        ("timesfm3_hurdle_dynamic", "positive", "not the completed law's"),
    ],
)
def test_the_integrity_recomputation_catches_a_changed_new_variant(
    toy, tmp_path, variant, field, message
):
    _, run, _, _ = toy

    def change(rows):
        row = next(r for r in rows if r["model"] == variant and r["horizon"] == 7)
        law = row["forecast"]["distributions"][2]
        if field == "p":
            law["p"] = law["p"] * 0.5
        else:
            law["positive"] = dict(kind="point", value=2)
        return (row["series_id"], row["cutoff"], row["horizon"], row["model"])

    copy, window = _tampered(run, tmp_path, "tampered", change)
    summary = integrity_command.check_run(copy, out=tmp_path / "integrity", root=ROOT_DIR)
    assert summary["status"] == "fail" and summary["failed_forecasts"] == 1
    assert summary["checks"]["new_variant_structure"]["failures"] == 1
    (failure,) = summary["failures"]
    assert (failure["series_id"], failure["cutoff"], failure["horizon"], failure["model"]) == window
    assert message in failure["reasons"]


def test_the_study3_commands_run_from_the_command_line(toy, tmp_path, monkeypatch, capsys):
    _, run, _, _ = toy
    argv = ["study3_inference.py", "--run", str(run), "--out", str(tmp_path / "inference")]
    monkeypatch.setattr(sys, "argv", argv)
    inference_command.main()
    assert "36 comparisons, 24 available" in capsys.readouterr().out
    argv = ["study3_integrity.py", "--run", str(run), "--out", str(tmp_path / "integrity")]
    monkeypatch.setattr(sys, "argv", argv)
    assert integrity_command.main() == 0
    assert json.loads((tmp_path / "integrity" / "integrity.json").read_text())["status"] == "pass"

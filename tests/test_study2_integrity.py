"""The Study 2 per-forecast score recomputation on the inference tests' toy run directories."""

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from test_study2_inference import (
    DATES,
    STRATA,
    TOY_CELLS,
    TOY_REPLICATES,
    Pool,
    _copy_run,
    _rewrite_checkpoint,
    _toy_grid,
)

import scripts.study2_inference as inference_command
import scripts.study2_integrity as integrity_command
from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes
from pulsegraph.study2.constants import VARIANTS
from pulsegraph.study2.declarations import comparisons, specification
from pulsegraph.study2.distributions import CountLaw, complete, fm_hurdle
from pulsegraph.study2.runner import _evaluate
from pulsegraph.study2.scores import accounting
from pulsegraph.study2.synthetic import cells, generate

SCORES = integrity_command.SCORES
PARTS = integrity_command.PARTS
WINDOW = integrity_command.WINDOW
LAW_VARIANTS = 11  # every variant but the three _raw deciles, local_mean_28 and autoets_weekly
EPS = np.finfo(float).eps


@pytest.fixture(scope="module")
def external_run(tmp_path_factory):
    """The inference tests' external toy run: five series, the truth-seeing chronos2_hurdle."""
    root = tmp_path_factory.mktemp("integrity-external")
    rng = np.random.default_rng(7)
    truth = {
        ("packages", key): pd.Series(rng.poisson(rate, len(DATES)).astype(float), index=DATES)
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


def _snapshot(run):
    """Every file of a run directory outside integrity/, by its SHA-256."""
    return {
        path.relative_to(run).as_posix(): file_hash(path)
        for path in sorted(run.rglob("*"))
        if path.is_file() and path.relative_to(run).parts[0] != "integrity"
    }


@pytest.fixture(scope="module")
def external_integrity(external_run, tmp_path_factory):
    _, run, _ = external_run
    copy = _copy_run(run, tmp_path_factory.mktemp("integrity-external-copy") / "run")
    before = _snapshot(copy)
    summary = integrity_command.check_run("external_packages", copy)
    return copy, summary, before


@pytest.fixture(scope="module")
def synthetic_integrity(tmp_path_factory):
    """The inference tests' synthetic toy run: three cells, four replicates, with the oracle."""
    root = tmp_path_factory.mktemp("integrity-synthetic")
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
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(integrity_command, "grid_manifest", _toy_grid)
        summary = integrity_command.check_run("synthetic", run, root=root)
    return run, summary


def _table(run):
    return pd.read_csv(run / "integrity" / "integrity.csv")


def _assert_floating_point_residuals(table, summary):
    for name in SCORES:
        compared = table[f"{name}_saved"].notna()
        residual = table.loc[compared, f"{name}_residual"].abs()
        scale = table.loc[compared, f"{name}_recomputed"].abs().clip(lower=1)
        assert (residual <= 8 * EPS * scale).all(), name
        check = summary["checks"][name]
        assert check["compared"] == compared.sum() and check["disagreements"] == 0
        assert check["max_residual_over_tolerance"] < 1e-3


def test_a_clean_external_run_passes_with_residuals_at_floating_point_size(external_integrity):
    run, summary, _ = external_integrity
    n = len(STRATA) * 3 * 2 * len(VARIANTS)
    assert summary["status"] == "pass" and summary["failed_forecasts"] == 0
    assert summary["failures"] == []
    assert summary["grid"] == dict(
        series=len(STRATA),
        origins=["2026-06-03", "2026-07-03", "2026-08-02"],
        horizons=[7, 30],
        models=list(VARIANTS),
        registered_forecasts=n,
        forecasts=n,
        with_count_law=len(STRATA) * 3 * 2 * LAW_VARIANTS,
        without_count_law=len(STRATA) * 3 * 2 * (len(VARIANTS) - LAW_VARIANTS),
    )
    table = _table(run)
    assert len(table) == n and not table.duplicated(WINDOW).any()
    assert table.passed.all() and table.reasons.isna().all() and table.valid_arrays.all()
    _assert_floating_point_residuals(table, summary)
    # A Brier score is recomputed exactly where a count law is saved, and nowhere else.
    assert (table.occurrence_brier_recomputed.notna() == table.has_law).all()
    assert (table.occurrence_brier_saved.notna() == table.has_law).all()
    assert (table.n_zero_saved == table.n_zero_recomputed).all()
    assert summary["checks"]["day_counts"]["disagreements"] == 0
    assert summary["checks"]["invalid_arrays"] == summary["checks"]["not_recomputed"] == 0


def test_outputs_are_bound_to_the_run_and_nothing_else_in_it_changes(external_integrity):
    run, summary, before = external_integrity
    assert _snapshot(run) == before
    out = run / "integrity"
    assert sorted(p.name for p in out.iterdir()) == [
        "integrity.csv",
        "integrity.json",
        "integrity.log",
    ]
    document = read_json(out / "integrity.json")
    assert document["status"] == "pass" and document["analysis"] == "study2_score_integrity"
    for name, digest in document["outputs"].items():
        assert file_hash(out / name) == digest
    assert document["integrity_script_sha256"] == file_hash(
        ROOT_DIR / "scripts/study2_integrity.py"
    )
    state = read_json(run / "run.json")
    assert document["run"]["checkpoint_sha256"] == state["completed"]
    assert document["run"]["checkpoints"] == len(STRATA)
    assert document["run"]["run_json_sha256"] == file_hash(run / "run.json")
    assert document["run"]["identity"] == state["identity"]
    assert document["tolerance"]["rtol"] == 1e-10 and document["tolerance"]["atol"] == 1e-12
    assert document["written_at"].endswith("+00:00")
    log = (out / "integrity.log").read_text(encoding="utf-8")
    assert "result: pass (0 of 480 forecasts failed)" in log
    for name in ("integrity.csv", "integrity.json", "integrity.log"):
        assert b"\r" not in (out / name).read_bytes()
    with pytest.raises(FileExistsError):
        integrity_command.check_run("external_packages", run)
    assert _snapshot(run) == before


def test_a_clean_synthetic_run_with_the_oracle_passes(synthetic_integrity):
    run, summary = synthetic_integrity
    series = len(TOY_CELLS) * len(TOY_REPLICATES)
    n = series * 3 * 2 * (len(VARIANTS) + 1)
    assert summary["status"] == "pass" and summary["grid"]["forecasts"] == n
    assert summary["grid"]["origins"] == ["180", "210", "240"]
    assert summary["grid"]["models"] == [*VARIANTS, "oracle"]
    table = _table(run)
    assert len(table) == n and table.passed.all()
    _assert_floating_point_residuals(table, summary)
    oracle = table[table.model.eq("oracle")]
    assert len(oracle) == series * 3 * 2 and oracle.has_law.all()
    assert oracle.occurrence_brier_recomputed.notna().all()
    # The registered grid itself: thirty blocks of all eighteen cells.
    assert len(integrity_command.registered_series("synthetic", {}, ROOT_DIR)) == 540


def test_the_accounting_identity_holds_per_row(external_integrity, synthetic_integrity):
    for run in (external_integrity[0], synthetic_integrity[0]):
        table = _table(run)
        for kind in ("recomputed", "saved"):
            parts = sum(table[f"{part}_{kind}"] for part in PARTS)
            scale = table[f"qscore9_{kind}"].abs().clip(lower=1)
            assert ((parts - table[f"qscore9_{kind}"]).abs() <= 8 * EPS * scale).all()
            assert (table[[f"{part}_{kind}" for part in PARTS]] >= 0).all().all()
        assert (
            table.identity_residual.abs() <= 8 * EPS * table.qscore9_recomputed.clip(lower=1)
        ).all()
        assert (table.n_zero_recomputed + table.n_positive_recomputed == table.horizon).all()
        assert (table.zero_recomputed[table.n_zero_recomputed.eq(0)] == 0).all()
        positive = table.positive_over_recomputed + table.positive_under_recomputed
        assert (positive[table.n_positive_recomputed.eq(0)] == 0).all()
        # The truth-seeing forecast scores zero in every part.
        perfect = table[table.model.eq("chronos2_hurdle")]
        assert (perfect[[f"{part}_recomputed" for part in ("qscore9", *PARTS)]] == 0).all().all()


def test_the_formula_by_hand_and_against_the_run_scorer():
    y = [0, 2]
    q = [[0, 0, 0, 0, 0, 1, 1, 1, 2], [1, 1, 1, 2, 2, 2, 3, 3, 3]]
    # Day 1, y = 0: (1 - tau) q for the four deciles above zero, 0.4 + 0.3 + 0.2 + 0.1 x 2 = 1.1.
    # Day 2, y = 2: tau (2 - q) below, 0.1 + 0.2 + 0.3 = 0.6; (1 - tau)(q - 2) above, 0.6.
    result = integrity_command.recompute_qscore9(y, q)
    assert result["qscore9"] == pytest.approx(2 * 2.3 / 18, rel=1e-14)
    assert result["zero"] == pytest.approx(2 * 1.1 / 18, rel=1e-14)
    assert result["positive_over"] == pytest.approx(2 * 0.6 / 18, rel=1e-14)
    assert result["positive_under"] == pytest.approx(2 * 0.6 / 18, rel=1e-14)
    assert (result["n_zero"], result["n_positive"]) == (1, 1)
    rng = np.random.default_rng(20261016)
    for _ in range(200):
        h = int(rng.choice([7, 30]))
        target = rng.poisson(rng.choice([0.2, 2.0, 40.0]), h).astype(float)
        target[rng.random(h) < 0.3] = 0
        deciles = rng.gamma(1.0, rng.choice([0.5, 5.0, 50.0]), (h, 9))
        deciles[rng.random((h, 9)) < 0.2] = 0
        deciles = np.sort(np.floor(deciles * rng.choice([1, 4])) / 4, axis=1)
        mine = integrity_command.recompute_qscore9(target, deciles)
        theirs = accounting(target, deciles)
        assert integrity_command.valid_arrays(target, deciles, h)
        assert mine["qscore9"] == pytest.approx(theirs["qscore9"], rel=1e-13, abs=1e-15)
        for part in PARTS:
            assert mine[part] == pytest.approx(theirs["contributions"][part], rel=1e-13, abs=1e-15)
        assert (mine["n_zero"], mine["n_positive"]) == (theirs["n_zero"], theirs["n_positive"])
    good = np.tile(np.arange(9.0), (2, 1))
    assert integrity_command.valid_arrays([0.0, 3.0], good, 2)
    for target, deciles, horizon in (
        ([0.0, -1.0], good, 2),
        ([0.0, 1.5], good, 2),
        ([0.0, 1.0], good[:, ::-1], 2),
        ([0.0, 1.0], good, 7),
        ([0.0, 1.0], good[:, :8], 2),
        ([0.0, 1.0], [[0.0] * 9, [0.0] * 8], 2),
    ):
        assert not integrity_command.valid_arrays(target, deciles, horizon)
    with pytest.raises(ValueError, match="nine per target day"):
        integrity_command.recompute_qscore9([0.0, 1.0], good[:, :8])


def test_occurrence_probability_follows_every_registered_law():
    shapes = (
        [0.0] * 9,
        [0, 0, 0, 0, 0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0.5, 0.5, 2, 3, 9],
        [0.2] * 9,
        [0, 0, 0, 0, 0, 0, 0, 0, 0.3],
        [3, 4, 5, 6, 7, 8, 9, 10, 40],
        [0, 0, 0.25, 0.75, 1, 1, 2, 2, 6],
    )
    laws = [
        dict(kind="point", value=0),
        dict(kind="point", value=3),
        dict(kind="poisson", mu=0.0),
        dict(kind="poisson", mu=2.5),
        dict(kind="poisson", mu=0.4, shift=1),
        dict(kind="nb", shape=2.0, probability=0.3),
        dict(kind="nb", shape=0.7, probability=0.9, shift=1),
        dict(kind="empirical", values=[1, 1, 4]),
        dict(kind="empirical", values=[0, 2, 0, 5]),
        *(complete(q).spec for q in shapes),
        *(fm_hurdle(complete(q), 0.7).spec for q in shapes),
        dict(kind="hurdle", p=0.3, positive=dict(kind="poisson", mu=1.5, shift=1)),
        dict(kind="hurdle", p=0.45, positive=dict(kind="point", value=1)),
        dict(kind="hurdle", p=0.6, positive=dict(kind="empirical", values=[1, 3])),
        dict(kind="hurdle", p=0.8, positive=dict(kind="nb", shape=1.2, probability=0.4, shift=1)),
    ]
    for spec in laws:
        # The run's distribution code gives the same P(Y > 0) = SF(0) for every registered law.
        assert integrity_command.occurrence_probability(spec) == pytest.approx(
            float(CountLaw(spec).sf(0)), rel=1e-13, abs=1e-15
        ), spec
    probability = integrity_command.occurrence_probability
    # By hand from the registered definitions.
    assert probability(dict(kind="poisson", mu=2.5)) == pytest.approx(1 - math.exp(-2.5))
    assert probability(dict(kind="nb", shape=2.0, probability=0.3)) == pytest.approx(0.91)
    # Q passes 0.5 halfway between u = 0.5 and 0.6, where it rises from 0 to 1.
    assert probability(complete(shapes[1]).spec) == pytest.approx(0.45, rel=1e-14)
    # All nine deciles below 0.5: the exponential tail with s = 1 reaches 0.5.
    assert probability(complete(shapes[0]).spec) == pytest.approx(0.1 * math.exp(-0.5))
    assert probability(fm_hurdle(complete(shapes[2]), 0.7).spec) == 0.7
    with pytest.raises(ValueError, match="Unknown saved count law"):
        probability(dict(kind="lognormal", mu=1.0))
    with pytest.raises(ValueError, match="shift"):
        probability(dict(kind="poisson", mu=1.0, shift=-1))
    with pytest.raises(ValueError, match="one per target day"):
        integrity_command.occurrence_brier([dict(kind="point", value=1)], [1.0, 0.0])


def test_crps_availability_is_counted_from_the_saved_reasons(external_run, tmp_path):
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
    summary = integrity_command.check_run("external_packages", copy)
    assert summary["status"] == "pass"
    windows = len(STRATA) * 3 * 2
    assert summary["crps_availability"]["total"] == dict(
        crps_forecasts=windows * len(VARIANTS),
        crps_with_count_distribution=windows * LAW_VARIANTS,
        crps_certified=(windows - 2) * LAW_VARIANTS,
        crps_unavailable_no_count_distribution=windows * (len(VARIANTS) - LAW_VARIANTS),
        crps_unavailable_bound_not_certified=2 * LAW_VARIANTS,
        crps_inconsistent=0,
    )
    # The same denominators as the inference command's secondary_scores.csv.
    inference_command.run_inference(
        "external_packages", copy, out=tmp_path / "inference", root=ROOT_DIR
    )
    scores = pd.read_csv(tmp_path / "inference" / "secondary_scores.csv")
    mine = pd.DataFrame(summary["crps_availability"]["by_horizon_model"])
    mine = mine.drop(columns="crps_inconsistent")
    pd.testing.assert_frame_equal(mine, scores[mine.columns])

    broken = _copy_run(run, tmp_path / "broken")

    def mislabel(rows):
        row = next(r for r in rows if r["model"] == "poisson_28")
        row["scores"]["crps_unavailable_reason"] = "no_count_distribution"
        return rows

    _rewrite_checkpoint(broken, mislabel)
    summary = integrity_command.check_run("external_packages", broken)
    assert summary["status"] == "fail" and summary["failed_forecasts"] == 1
    assert summary["failures"][0]["model"] == "poisson_28"
    assert summary["failures"][0]["reasons"] == (
        "the saved CRPS availability disagrees with the saved law and value"
    )
    assert summary["crps_availability"]["total"]["crps_inconsistent"] == 1


def _tamper(run, change, label=None):
    """Rewrite one saved forecast and its checkpoint hash in run.json; return its window."""
    window = {}

    def rewrite(rows):
        row = change(rows)
        window.update({key: row[key] for key in WINDOW})
        return rows

    _rewrite_checkpoint(run, rewrite, label=label)
    return window


def test_a_tampered_decile_fails_with_the_reason(external_run, tmp_path):
    _, run, _ = external_run
    copy = _copy_run(run, tmp_path / "run")

    def raise_first_day(rows):
        row = next(r for r in rows if r["model"] == "chronos2_raw")
        row["forecast"]["deciles"][0] = [value + 100 for value in row["forecast"]["deciles"][0]]
        return row

    window = _tamper(copy, raise_first_day)
    summary = integrity_command.check_run("external_packages", copy)
    assert summary["status"] == "fail" and summary["failed_forecasts"] == 1
    [failure] = summary["failures"]
    assert {key: failure[key] for key in WINDOW} == window
    reasons = failure["reasons"].split("; ")
    assert "qscore9 differs from the saved value" in reasons
    assert "context_scaled_qscore9 differs from the saved value" in reasons
    assert not any("count" in reason or "brier" in reason for reason in reasons)
    table = _table(copy)
    row = table[~table.passed].iloc[0]
    assert row.qscore9_residual > 1 and row.valid_arrays
    assert abs(row.identity_residual) <= 8 * EPS * row.qscore9_recomputed
    assert table.passed.sum() == len(table) - 1


def test_a_tampered_target_fails_with_the_reason(external_run, tmp_path):
    _, run, _ = external_run
    copy = _copy_run(run, tmp_path / "run")

    def fill_a_zero_day(rows):
        row = next(r for r in rows if r["model"] == "poisson_28" and 0 in r["target"])
        row["target"][row["target"].index(0)] = 5.0
        return row

    label = json.dumps(["packages", "p3"], separators=(",", ":"))
    window = _tamper(copy, fill_a_zero_day, label=label)
    summary = integrity_command.check_run("external_packages", copy)
    assert summary["status"] == "fail" and summary["failed_forecasts"] == 1
    [failure] = summary["failures"]
    assert {key: failure[key] for key in WINDOW} == window
    reasons = failure["reasons"].split("; ")
    for expected in (
        "qscore9 differs from the saved value",
        "zero differs from the saved value",
        "occurrence_brier differs from the saved value",
        "n_zero differs from the saved count",
        "n_positive differs from the saved count",
    ):
        assert expected in reasons
    assert summary["checks"]["day_counts"]["disagreements"] == 1
    assert summary["checks"]["occurrence_brier"]["disagreements"] == 1


def test_a_missing_duplicated_or_unregistered_forecast_is_refused(external_run, tmp_path):
    _, run, truth = external_run
    cases = []
    missing = _copy_run(run, tmp_path / "missing")
    _rewrite_checkpoint(missing, lambda rows: rows[:-1])
    cases.append((missing, r"incomplete: 1 registered forecasts missing"))
    duplicate = _copy_run(run, tmp_path / "duplicate")
    _rewrite_checkpoint(duplicate, lambda rows: rows + rows[:1])
    cases.append((duplicate, "duplicate forecast"))
    outside = _copy_run(run, tmp_path / "outside")
    _rewrite_checkpoint(outside, lambda rows: [*rows[:-1], dict(rows[-1], model="oracle")])
    cases.append((outside, "outside the registered grid"))
    partial = tmp_path / "partial"
    state = read_json(run / "run.json")
    _evaluate(
        {key: truth[key] for key in list(truth)[:-1]},
        partial,
        Pool(truth),
        metadata=state["metadata"],
    )
    cases.append((partial, "1 registered series missing"))
    for directory, message in cases:
        with pytest.raises(ValueError, match=message):
            integrity_command.check_run("external_packages", directory)
        assert not (directory / "integrity").exists()


def test_a_changed_checkpoint_or_an_unfinished_run_is_refused(external_run, tmp_path):
    _, run, _ = external_run
    label = sorted(read_json(run / "run.json")["completed"])[0]
    name = sha256_bytes(label.encode()) + ".json"
    cases = []
    changed = _copy_run(run, tmp_path / "changed")
    with (changed / name).open("a") as stream:
        stream.write(" ")
    cases.append((changed, "Checkpoint hash mismatch"))
    deleted = _copy_run(run, tmp_path / "deleted")
    (deleted / name).unlink()
    cases.append((deleted, "Checkpoint hash mismatch"))
    for status in ("running", "failed"):
        unfinished = _copy_run(run, tmp_path / status)
        atomic_json(unfinished / "run.json", dict(read_json(run / "run.json"), status=status))
        cases.append((unfinished, "requires a complete run"))
    relabelled = _copy_run(run, tmp_path / "relabelled")
    state = read_json(run / "run.json")
    state["metadata"] = dict(state["metadata"], readiness_sha256="c" * 64)
    atomic_json(relabelled / "run.json", state)
    cases.append((relabelled, "does not match the run identity"))
    for directory, message in cases:
        with pytest.raises(ValueError, match=message):
            integrity_command.check_run("external_packages", directory)
        assert not (directory / "integrity").exists()
    with pytest.raises(ValueError, match="not a run of this component"):
        integrity_command.check_run("synthetic", run, out=tmp_path / "out")
    with pytest.raises(ValueError, match="external_packages and synthetic only"):
        integrity_command.check_run("external", run, out=tmp_path / "out")
    assert not (tmp_path / "out").exists() and not (run / "integrity").exists()


def test_command_line_writes_under_the_run_directory_with_exit_codes(
    external_run, tmp_path, monkeypatch, capsys
):
    _, run, _ = external_run
    copy = _copy_run(run, tmp_path / "run")
    monkeypatch.setattr(
        sys, "argv", ["study2_integrity.py", "external_packages", "--run", str(copy)]
    )
    assert integrity_command.main() == 0
    assert "integrity: pass; 0 of 480 forecasts failed" in capsys.readouterr().out
    document = read_json(copy / "integrity" / "integrity.json")
    assert document["command"][-3:] == ["external_packages", "--run", str(copy)]
    assert integrity_command.main() == 2
    assert "refused" in capsys.readouterr().err
    tampered = _copy_run(run, tmp_path / "tampered")
    _rewrite_checkpoint(
        tampered, lambda rows: [dict(rows[0], target=[y + 1 for y in rows[0]["target"]])] + rows[1:]
    )
    monkeypatch.setattr(
        sys, "argv", ["study2_integrity.py", "external_packages", "--run", str(tampered)]
    )
    assert integrity_command.main() == 1
    assert read_json(tampered / "integrity" / "integrity.json")["status"] == "fail"
    result = subprocess.run(
        [sys.executable, "scripts/study2_integrity.py", "--help"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=Path(__file__).resolve().parents[1],
    )
    assert result.returncode == 0 and "usage:" in result.stdout

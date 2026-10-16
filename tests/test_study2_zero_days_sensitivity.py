"""The post-hoc npm zero-day sensitivity on a toy run directory; no model is loaded."""

import importlib.util
import sys

import numpy as np
import pandas as pd
import pytest
from test_study2_inference import DATES, STRATA, Pool, _copy_run, _rewrite_checkpoint

import scripts.study2_inference as inference_command
from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.evaluation.reviews import benjamini_hochberg
from pulsegraph.provenance import atomic_json, read_json
from pulsegraph.study2.declarations import comparisons, specification
from pulsegraph.study2.runner import _evaluate
from pulsegraph.study2.scores import accounting

SCRIPT = ROOT_DIR / "reports/study2-npm/run-2026-10-15/posthoc/sensitivity_zero_days.py"
_spec = importlib.util.spec_from_file_location("sensitivity_zero_days", SCRIPT)
sensitivity = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sensitivity)

LARGEST = "p0"  # the toy series with the largest rate stands in for aggregate-error
THREE = sensitivity.SCENARIOS["three_days"]
TWO = sensitivity.SCENARIOS["two_panel_wide_days"]
UNCHANGED_COLUMNS = [
    "model_mean",
    "reference_mean",
    "mean_diff",
    "mean_diff_ci_low",
    "mean_diff_ci_high",
    "median_diff",
    "wins",
    "ties",
    "losses",
    "n_nonzero",
    "wilcoxon_p",
    "bootstrap_seed",
]


def _summary(truth, path):
    """A daily_summary.csv for the toy panel, with the columns the check reads."""
    wide = pd.DataFrame({key: series for (_, key), series in truth.items()})
    table = pd.DataFrame(
        dict(
            series=wide.shape[1],
            series_zero=(wide == 0).sum(axis=1),
            total_downloads=wide.sum(axis=1).astype(int),
            largest_series_count=wide[LARGEST].astype(int),
        )
    )
    table.index = [day.date().isoformat() for day in table.index]
    table.index.name = "date"
    path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(path, lineterminator="\n")


@pytest.fixture(scope="module")
def toy_run(tmp_path_factory):
    """Five toy series whose sources read 0 on the npm days: everyone on the two panel-wide
    days, the largest series alone on 2026-06-25; the registered inference beside them."""
    root = tmp_path_factory.mktemp("zero-days")
    rng = np.random.default_rng(7)
    truth = {}
    for key, rate in zip(STRATA, (6.0, 3.0, 1.5, 1.0, 0.7), strict=True):
        series = pd.Series(rng.poisson(rate, len(DATES)).astype(float), index=DATES)
        series[pd.to_datetime(list(TWO))] = 0.0
        if key == LARGEST:
            series[pd.Timestamp("2026-06-25")] = 0.0
        truth[("packages", key)] = series
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
    inference_command.run_inference("external_packages", run, out=run / "inference", root=ROOT_DIR)
    _summary(truth, run / "target-pull" / "daily_summary.csv")
    return run, truth


@pytest.fixture(scope="module")
def outcome(toy_run):
    run, _ = toy_run
    return sensitivity.run_sensitivity(run)


def _day_loss(target, deciles, index):
    """One day's QScore9: its nine-decile mean of 2 x pinball."""
    return accounting([target[index]], [deciles[index]])["qscore9"]


def test_removing_a_day_by_hand():
    y = [0, 2]
    q = [[0, 0, 0, 0, 0, 1, 1, 1, 2], [1, 1, 1, 2, 2, 2, 3, 3, 3]]
    # Day 1, y = 0: (1 - tau) q summed, 0.4 + 0.3 + 0.2 + 0.1 x 2 = 1.1; day 2, y = 2: 1.2.
    assert sensitivity.qscore9(y, q) == pytest.approx(2 * 2.3 / 18, rel=1e-14)
    assert sensitivity.rescore(y, q, [False, True]) == pytest.approx(2 * 1.2 / 9, rel=1e-14)
    assert sensitivity.rescore(y, q, [True, False]) == pytest.approx(2 * 1.1 / 9, rel=1e-14)
    assert sensitivity.rescore(y, q, [True, True]) == sensitivity.qscore9(y, q)
    with pytest.raises(ValueError, match="every day"):
        sensitivity.rescore(y, q, [False, False])
    # The remaining-day mean of a 30-day block: (30 Q - loss of the removed day) / 29.
    rng = np.random.default_rng(20261016)
    for _ in range(50):
        target = rng.poisson(rng.choice([0.5, 5.0, 5e6]), 30).astype(float)
        target[rng.integers(30)] = 0
        deciles = np.sort(np.floor(rng.gamma(1.0, target.mean() + 1, (30, 9))), axis=1)
        index = int(rng.integers(30))
        keep = np.arange(30) != index
        full = sensitivity.qscore9(target, deciles)
        expected = (30 * full - _day_loss(target, deciles, index)) / 29
        assert sensitivity.rescore(target, deciles, keep) == pytest.approx(expected, rel=1e-12)


def test_the_block_days_are_the_registered_calendar():
    assert sensitivity.block_days("2026-07-03", 30)[9] == "2026-07-12"
    assert sensitivity.block_days("2026-08-02", 30)[12] == "2026-08-14"
    assert sensitivity.block_days("2026-06-03", 30)[22] == "2026-06-25"
    assert sensitivity.block_days("2026-06-03", 30)[-1] == "2026-07-02"
    for cutoff in ("2026-06-03", "2026-07-03", "2026-08-02"):
        assert not set(sensitivity.block_days(cutoff, 7)) & set(THREE)


def test_a_removed_day_changes_the_block_and_series_means_by_the_expected_amount(toy_run):
    run, _ = toy_run
    _, _, windows = sensitivity.read_windows(run)
    frame = sensitivity.scenario_frame(windows, THREE).set_index(
        ["series_id", "cutoff", "horizon", "model"]
    )
    expected = {}
    for w in windows:
        key = (w["series_id"], w["cutoff"], w["horizon"], w["model"])
        days = sensitivity.block_days(w["cutoff"], w["horizon"])
        held = [i for i, day in enumerate(days) if day in THREE]
        if w["horizon"] == 30:
            [index] = held
            value = (30 * w["saved"] - _day_loss(w["target"], w["deciles"], index)) / 29
            assert frame.loc[key, "qscore9"] == pytest.approx(value, rel=1e-12, abs=1e-12)
            assert frame.loc[key, "days_removed"] == 1
        else:
            assert held == [] and frame.loc[key, "days_removed"] == 0
            value = w["saved"]
        expected.setdefault((w["series_id"], w["horizon"], w["model"]), []).append(value)
    # Origins are averaged within series and horizon, as registered.
    series = inference_command.series_scores(frame.reset_index(), ["qscore9"])
    for (key, horizon, model), values in expected.items():
        assert series.loc[(horizon, model, key), "qscore9"] == pytest.approx(
            np.mean(values), rel=1e-12, abs=1e-12
        )
    # The two-day scenario leaves the block from 2026-06-03 as saved.
    two = sensitivity.scenario_frame(windows, TWO)
    first = two[two.cutoff.eq("2026-06-03")]
    assert first.days_removed.eq(0).all()
    saved = {(w["series_id"], w["cutoff"], w["horizon"], w["model"]): w["saved"] for w in windows}
    assert all(
        row.qscore9 == saved[(row.series_id, row.cutoff, row.horizon, row.model)]
        for row in first.itertuples()
    )
    assert two.days_removed.sum() == len(STRATA) * 2 * 16


def test_an_untouched_block_is_unchanged_and_only_its_bh_p_can_move(toy_run, outcome):
    run, _ = toy_run
    _, _, windows = sensitivity.read_windows(run)
    frame = sensitivity.scenario_frame(windows, THREE)
    h7 = frame[frame.horizon.eq(7)]
    assert h7.days_removed.eq(0).all()
    saved = [w["saved"] for w in windows if w["horizon"] == 7]
    assert h7.qscore9.tolist() == saved  # exactly the saved values
    registered = pd.read_csv(
        run / "inference" / "inference.csv", float_precision="round_trip"
    ).set_index("id")
    _, _, table, paired = outcome
    pairs = pd.read_csv(run / "inference" / "paired_entities.csv", float_precision="round_trip")
    for name in sensitivity.SCENARIOS:
        rows = table[table.scenario.eq(name)].set_index("id")
        h7_ids = rows.index[rows.horizon.eq(7)]
        pd.testing.assert_frame_equal(
            rows.loc[h7_ids, UNCHANGED_COLUMNS],
            registered.loc[h7_ids, UNCHANGED_COLUMNS],
            check_exact=True,
            check_dtype=False,
        )
        mine = paired[paired.scenario.eq(name) & paired.horizon.eq(7)]
        theirs = pairs[pairs.horizon.eq(7)]
        assert mine.difference.tolist() == theirs.difference.tolist()
        # BH is applied once over the eighteen of the scenario, so a horizon-7 BH p can move.
        assert np.allclose(rows.wilcoxon_p_bh, benjamini_hochberg(rows.wilcoxon_p), rtol=0)
        assert (rows.reject_bh_005 == (rows.wilcoxon_p_bh <= 0.05)).all()
        assert len(rows) == 18 and (rows.bootstrap_seed == registered.bootstrap_seed).all()


def test_no_day_removed_reproduces_the_registered_family_byte_for_byte(toy_run, outcome):
    run, _ = toy_run
    _, reproduced, _, _ = outcome
    assert reproduced == {"inference.csv": True, "paired_entities.csv": True}
    _, reproduced, table, _ = sensitivity.run_sensitivity(run, scenarios={"none": ()})
    registered = pd.read_csv(run / "inference" / "inference.csv", float_precision="round_trip")
    assert all(reproduced.values())
    assert np.array_equal(table.mean_diff, registered.mean_diff)
    assert np.array_equal(table.wilcoxon_p_bh, registered.wilcoxon_p_bh)
    assert not table[["mean_sign_changes", "larger_sum_changes", "rejection_changes"]].any().any()
    assert table.forecasts_rescored.eq(0).all()


def test_the_directions_are_the_larger_rank_sums():
    assert sensitivity.rank_sums([-3.0, -1.0, 2.0, 0.0]) == dict(
        rank_sum_model_lower=4.0, rank_sum_reference_lower=2.0, larger_sum_favors="model"
    )
    assert sensitivity.rank_sums([1.0, -1.0, 0.0])["larger_sum_favors"] == "neither"
    assert sensitivity.rank_sums([5.0, -1.0])["larger_sum_favors"] == "reference"


def test_the_day_labels_are_checked_against_the_daily_summary(toy_run, tmp_path):
    run, truth = toy_run
    _, _, windows = sensitivity.read_windows(run)
    summary = run / "target-pull" / "daily_summary.csv"
    checks = sensitivity.check_day_labels(windows, summary, THREE, LARGEST)
    assert checks["target_days_rebuilt"] == 90
    assert checks["removed_days"]["2026-07-12"]["series_zero"] == len(STRATA)
    assert checks["removed_days"]["2026-07-12"]["blocks"] == ["2026-07-03+30"]
    assert checks["removed_days"]["2026-06-25"]["largest_series_count"] == 0
    # A summary one day out of step with the targets is refused.
    shifted = {key: series.shift(1, fill_value=0.0) for key, series in truth.items()}
    _summary(shifted, tmp_path / "shifted.csv")
    with pytest.raises(ValueError, match="do not rebuild"):
        sensitivity.check_day_labels(windows, tmp_path / "shifted.csv", THREE, LARGEST)
    # A day that does not read zero, or one inside a horizon-7 block, is refused.
    with pytest.raises(ValueError, match="does not read zero"):
        sensitivity.check_day_labels(windows, summary, ("2026-06-26",), LARGEST)
    with pytest.raises(ValueError, match="horizon-7 block"):
        sensitivity.check_day_labels(windows, summary, ("2026-07-05",), LARGEST)


def test_a_changed_checkpoint_is_refused(toy_run, tmp_path):
    run, _ = toy_run
    copy = _copy_run(run, tmp_path / "run")

    def raise_a_target(rows):
        rows[0]["target"][0] += 1
        return rows

    _rewrite_checkpoint(copy, raise_a_target)
    # run.json follows the rewrite, so the bytes agree; the re-score then refuses it.
    _, _, windows = sensitivity.read_windows(copy)
    with pytest.raises(ValueError, match="differs from its re-scored"):
        sensitivity.check_saved_scores(windows)
    state = read_json(copy / "run.json")
    label = sorted(state["completed"])[0]
    state["completed"][label] = "0" * 64
    atomic_json(copy / "run.json", state)
    with pytest.raises(ValueError, match="identity|hash mismatch"):
        sensitivity.read_windows(copy)


def test_the_command_writes_its_outputs_once(toy_run, tmp_path, monkeypatch, capsys):
    run, _ = toy_run
    monkeypatch.setattr(sensitivity, "LARGEST", LARGEST)
    monkeypatch.setattr(sys, "argv", ["sensitivity_zero_days.py", str(run), "--out", str(tmp_path)])
    sensitivity.main()
    printed = capsys.readouterr().out
    assert "### three_days: 2026-06-25 2026-07-12 2026-08-14 removed" in printed
    assert "### two_panel_wide_days: 2026-07-12 2026-08-14 removed" in printed
    document = read_json(tmp_path / "sensitivity.json")
    assert document["status"].startswith("post-hoc")
    assert document["checks"]["registered_family_reproduced_byte_for_byte"] == {
        "inference.csv": True,
        "paired_entities.csv": True,
    }
    assert document["checks"]["saved_qscore9_rescored"]["max_abs_residual"] == 0.0
    for name, digest in document["outputs"].items():
        assert file_hash(tmp_path / name) == digest
    table = pd.read_csv(tmp_path / "sensitivity_inference.csv")
    assert table.groupby("scenario").size().to_dict() == {
        "three_days": 18,
        "two_panel_wide_days": 18,
    }
    for name in sensitivity.OUTPUTS:
        assert b"\r" not in (tmp_path / name).read_bytes()
    with pytest.raises(SystemExit, match="refusing to overwrite"):
        sensitivity.main()

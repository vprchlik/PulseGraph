import importlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pulsegraph.cli import REVIEW_NAMES, ingest_main, review_main, synthetic_main
from pulsegraph.evaluation.artifacts import read_run_artifact, validate_results


@pytest.fixture
def artifact(tmp_path):
    directory = tmp_path / "run"
    synthetic_main(
        [
            "--synthetic",
            "--seed",
            "42",
            "--out",
            str(directory),
            "--n-days",
            "90",
            "--min-context-days",
            "30",
            "--horizons",
            "3",
            "7",
            "--n-samples",
            "20",
            "--local-mean-lookbacks",
            "14",
        ]
    )
    return directory


def test_artifact_round_trip_preserves_full_forecasts_and_provenance(artifact):
    rows, metadata, dataset = read_run_artifact(artifact)
    assert len(rows) == 3 * 4 * 2 * 2
    assert sorted(dataset) == metadata["repositories"]
    assert metadata["data_kind"] == "synthetic" and metadata["protocol_commit"] is None
    assert metadata["config"]["seed"] == 42
    assert metadata["packages"]["numpy"]
    assert "pulsegraph/evaluation/metrics.py" in metadata["source_sha256"]
    assert len(rows.iloc[0].samples) == 20
    assert len(rows.iloc[0].context) == 76


def test_hash_failure_and_overwrite_are_rejected(artifact):
    with pytest.raises(SystemExit):
        synthetic_main(["--synthetic", "--seed", "42", "--out", str(artifact)])
    with (artifact / "summary.csv").open("a", encoding="utf-8") as stream:
        stream.write("tampered\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        read_run_artifact(artifact)


@pytest.mark.parametrize(
    "mutation", ["whole_model", "one_window", "duplicate", "score", "context", "label", "seed"]
)
def test_integrity_detects_missing_keys_bad_scores_and_leakage(artifact, mutation):
    rows, metadata, dataset = read_run_artifact(artifact)
    if mutation == "whole_model":
        rows = rows[~rows.model_name.eq("last_value")]
    elif mutation == "one_window":
        rows = rows.iloc[1:]
    elif mutation == "duplicate":
        rows = pd.concat([rows, rows.iloc[:1]], ignore_index=True)
    elif mutation == "score":
        rows.loc[0, "mae"] += 1
    elif mutation == "context":
        values = rows.at[0, "context"].copy()
        values[-1] = 1_000_000
        rows.at[0, "context"] = values
    elif mutation == "label":
        rows.loc[0, "stratum"] = "future-selected"
    else:
        rows.loc[0, "pit_seed"] += 1
    with pytest.raises(ValueError):
        validate_results(rows, metadata, dataset)


def test_all_seven_reviews_are_offline_and_never_rewrite_input(artifact, tmp_path):
    original = (artifact / "results.parquet").read_bytes()
    comparisons = tmp_path / "comparisons.json"
    comparisons.write_text(
        json.dumps(
            [
                {
                    "model": "weekly_naive",
                    "reference": "local_mean_28",
                    "horizon": 7,
                    "stratum": "all",
                }
            ]
        ),
        encoding="utf-8",
    )
    extras = {
        "scale": ["--reference", "local_mean_28", "--metric", "mean_pinball_loss"],
        "strong_baselines": ["--baselines", "last_value", "weekly_naive", "local_mean_28"],
        "local_mean_lookbacks": ["--lookbacks", "14", "28"],
        "cluster_inference": [
            "--comparisons",
            str(comparisons),
            "--declared-count",
            "1",
            "--metric",
            "mean_pinball_loss",
            "--seed",
            "7",
            "--n-bootstrap",
            "100",
            "--confidence",
            "0.95",
        ],
    }
    for review in REVIEW_NAMES:
        destination = tmp_path / f"{review}.csv"
        review_main(
            review, ["--run", str(artifact), "--out", str(destination), *extras.get(review, [])]
        )
        output = pd.read_csv(destination)
        assert not output.empty
        assert set(output.analysis_status) == {"post_hoc"}
        assert set(output.data_kind) == {"synthetic"}
        provenance = json.loads(destination.with_suffix(".meta.json").read_text(encoding="utf-8"))
        assert provenance["run_metadata_sha256"]
        with pytest.raises(SystemExit):
            review_main(
                review, ["--run", str(artifact), "--out", str(destination), *extras.get(review, [])]
            )
    assert (artifact / "results.parquet").read_bytes() == original


def test_real_run_is_rejected_before_data_generation(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "pulsegraph.cli.generate_synthetic_data", lambda **_: pytest.fail("Data accessed")
    )
    with pytest.raises(SystemExit) as error:
        synthetic_main(["--seed", "42", "--out", str(tmp_path / "real")])
    assert error.value.code == 2
    assert not (tmp_path / "real").exists()


def test_script_entry_points_import_without_running_and_help_works():
    for script in ("run_experiment", "ingest_stars", *(f"review_{name}" for name in REVIEW_NAMES)):
        importlib.import_module(f"scripts.{script}")
        result = subprocess.run(
            [sys.executable, "-m", f"scripts.{script}", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=Path(__file__).resolve().parents[1],
        )
        assert result.returncode == 0, result.stderr
        assert "usage:" in result.stdout


def test_offline_timestamp_ingestion_has_explicit_coverage_and_no_silent_drop(tmp_path):
    timestamps, manifest = tmp_path / "timestamps.json", tmp_path / "manifest.json"
    timestamps.write_text(
        json.dumps({"a/b": [], "c/d": ["2022-01-02T12:00:00Z"]}), encoding="utf-8"
    )
    manifest.write_text(
        json.dumps(
            [
                {"repo_name": name, "observation_start": "2022-01-01", "coverage_complete": True}
                for name in ("a/b", "c/d")
            ]
        ),
        encoding="utf-8",
    )
    output = tmp_path / "counts"
    ingest_main(
        [
            "--timestamps",
            str(timestamps),
            "--manifest",
            str(manifest),
            "--observation-end",
            "2022-01-07",
            "--out",
            str(output),
        ]
    )
    counts = pd.read_parquet(output / "daily_signals.parquet")
    assert counts.stars.tolist() == [1]
    assert json.loads((output / "ingest.json").read_text())["source"] == "rest_surviving_stargazers"


def test_native_quantile_rows_survive_parquet_without_fabricated_samples(artifact, tmp_path):
    rows, _, _ = read_run_artifact(artifact)
    # Exercise Arrow's nullable nested-list column, needed when models are mixed.
    rows.at[0, "samples"] = None
    path = tmp_path / "mixed.parquet"
    rows.to_parquet(path, index=False)
    restored = pd.read_parquet(path)
    assert restored.iloc[0].samples is None
    assert np.asarray(restored.iloc[1].samples.tolist()).ndim == 2

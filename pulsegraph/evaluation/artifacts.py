"""Synthetic artifact writer and shared strict validation for synthetic/registered runs."""

import hashlib
import json
from dataclasses import asdict
from importlib.metadata import distributions
from pathlib import Path

import numpy as np
import pandas as pd

from pulsegraph.config import ROOT_DIR
from pulsegraph.data.loader import build_dataset_for_forecasting
from pulsegraph.evaluation.backtest import (
    SCORE_COLUMNS,
    WINDOW_KEY,
    BacktestConfig,
    summarize_backtest,
)
from pulsegraph.evaluation.metrics import evaluate_forecast
from pulsegraph.forecast.output import ForecastOutput
from pulsegraph.random import derived_seed

ARTIFACT_FILES = {"results.parquet", "summary.csv", "signals.parquet", "manifest.json"}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_run_artifact(
    output_dir: Path,
    *,
    results: pd.DataFrame,
    signals: pd.DataFrame,
    manifest: pd.DataFrame,
    config: BacktestConfig,
    observation_end: str,
    models: list[str],
    data_kind: str,
    command: list[str],
) -> None:
    if data_kind != "synthetic":
        raise ValueError("Real-data runs await the committed protocol and registered runner")
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise FileExistsError("Run output already exists; artifacts must not be overwritten")
    source_files = [ROOT_DIR / "pyproject.toml"] if (ROOT_DIR / "pyproject.toml").is_file() else []
    for directory in ("pulsegraph", "scripts"):
        source_files.extend(sorted((ROOT_DIR / directory).rglob("*.py")))
    # Record all installed versions, including optional runtimes when present.
    versions = {dist.metadata["Name"]: dist.version for dist in distributions()}
    metadata = {
        "schema_version": 2,
        "data_kind": data_kind,
        "protocol_commit": None,
        "config": asdict(config),
        "observation_end": observation_end,
        "models": models,
        "repositories": sorted(manifest.repo_name.tolist()),
        "command": command,
        "packages": dict(sorted(versions.items())),
        "source_sha256": {
            str(path.relative_to(ROOT_DIR)).replace("\\", "/"): file_hash(path)
            for path in source_files
        },
    }
    dataset = build_dataset_for_forecasting(signals, manifest, observation_end=observation_end)
    validate_results(results, metadata, dataset)
    output_dir.mkdir(parents=True)
    results.to_parquet(output_dir / "results.parquet", index=False)
    summarize_backtest(results).to_csv(output_dir / "summary.csv", index=False)
    signals.to_parquet(output_dir / "signals.parquet", index=False)
    records = manifest.assign(
        observation_start=pd.to_datetime(manifest.observation_start).dt.strftime("%Y-%m-%d")
    ).to_dict("records")
    (output_dir / "manifest.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    metadata["artifact_sha256"] = {
        name: file_hash(output_dir / name) for name in sorted(ARTIFACT_FILES)
    }
    (output_dir / "run.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def read_run_artifact(path: Path) -> tuple[pd.DataFrame, dict, dict[str, pd.Series]]:
    path = Path(path)
    metadata = json.loads((path / "run.json").read_text(encoding="utf-8"))
    if (
        metadata.get("schema_version") != 2
        or set(metadata.get("artifact_sha256", {})) != ARTIFACT_FILES
    ):
        raise ValueError("Unknown or incomplete artifact schema")
    for name, expected in metadata["artifact_sha256"].items():
        if file_hash(path / name) != expected:
            raise ValueError(f"Artifact hash mismatch: {name}")
    manifest = pd.DataFrame(json.loads((path / "manifest.json").read_text(encoding="utf-8")))
    dataset = build_dataset_for_forecasting(
        pd.read_parquet(path / "signals.parquet"),
        manifest,
        observation_end=metadata["observation_end"],
    )
    results = pd.read_parquet(path / "results.parquet")
    validate_results(results, metadata, dataset)
    expected = summarize_backtest(results)
    actual = pd.read_csv(path / "summary.csv")
    keys = ["model_name", "horizon", "stratum"]
    try:
        pd.testing.assert_frame_equal(
            actual.sort_values(keys).reset_index(drop=True),
            expected.sort_values(keys).reset_index(drop=True),
            check_dtype=False,
            rtol=1e-10,
            atol=1e-12,
        )
    except AssertionError as error:
        raise ValueError("Saved summary does not match recomputation") from error
    return results, metadata, dataset


def _matrix(values):
    return np.asarray([np.asarray(row, dtype=float) for row in values], dtype=float)


def validate_results(results: pd.DataFrame, metadata: dict, dataset: dict[str, pd.Series]) -> None:
    """Check the declared model/window grid and recompute scores from saved predictions."""
    real = metadata.get("data_kind") == "real"
    if real:
        from pulsegraph.data.regimes import context_regime
        from pulsegraph.evaluation.registration import (
            MODEL_PINS,
            PROTOCOL_COMMIT,
            PROTOCOL_SHA256,
            validate_declarations,
        )

        validate_declarations(metadata["specification"], metadata["comparison_family"])
        if (
            metadata.get("protocol_commit") != PROTOCOL_COMMIT
            or metadata.get("protocol_sha256") != PROTOCOL_SHA256
            or metadata.get("comparison_count") != 18
            or not metadata.get("implementation_commit")
        ):
            raise ValueError("Missing registered artifact provenance")
    config = BacktestConfig(**metadata["config"])
    keys = WINDOW_KEY + ["model_name"]
    if results.empty or results.duplicated(keys).any() or results[keys].isna().any().any():
        raise ValueError("Empty, duplicate or missing model/window keys")
    models = metadata["models"]
    if not models or len(models) != len(set(models)):
        raise ValueError("Model manifest must be nonempty and unique")
    if sorted(dataset) != sorted(metadata["repositories"]):
        raise ValueError("Repository manifest does not match run metadata")
    expected = {
        (repo, cutoff, horizon, model)
        for repo in dataset
        for cutoff in config.cutoffs
        for horizon in config.horizons
        for model in models
    }
    actual = set(results[keys].itertuples(index=False, name=None))
    if expected != actual:
        raise ValueError("Results do not cover every declared repository/model/window")
    if (results.groupby(WINDOW_KEY).stratum.nunique(dropna=False) != 1).any():
        raise ValueError("Context labels disagree across models on the same window")
    if (results.groupby(["repo_name", "cutoff_date"]).stratum.nunique(dropna=False) != 1).any():
        raise ValueError("Context labels disagree across horizons")
    for row in results.itertuples(index=False):
        series = dataset[row.repo_name]
        idx = int(series.index.searchsorted(pd.Timestamp(row.cutoff_date)))
        if (
            idx < config.min_context_days
            or idx + row.horizon > len(series)
            or series.index[idx] != pd.Timestamp(row.cutoff_date)
            or not 0 < row.model_context_length <= idx
        ):
            raise ValueError("Saved window has incomplete context or targets")
        context = series.iloc[:idx].to_numpy(dtype=float)
        actuals = series.iloc[idx : idx + row.horizon].to_numpy(dtype=float)
        if (
            idx != row.cutoff_idx
            or len(context) != row.context_length
            or row.context_start != series.index[0].date().isoformat()
            or row.context_end
            != (pd.Timestamp(row.cutoff_date) - pd.Timedelta(days=1)).date().isoformat()
            or row.target_end != series.index[idx + row.horizon - 1].date().isoformat()
            or row.observation_end != series.index[-1].date().isoformat()
        ):
            raise ValueError("Saved context/target calendar is inconsistent")
        if not np.array_equal(context, row.context) or not np.array_equal(actuals, row.actuals):
            raise ValueError("Saved context/actual values do not match the observation artifact")
        output = ForecastOutput(
            row.repo_name,
            row.model_name,
            row.horizon,
            row.model_context_length,
            row.quantile_levels,
            _matrix(row.quantiles),
            samples=None if row.samples is None else _matrix(row.samples),
            metadata=json.loads(row.model_metadata),
        )
        if real:
            if row.stratum != context_regime(series.iloc[:idx]):
                raise ValueError("Saved regime disagrees with context-only recomputation")
            if output.metadata.get("seed") != config.seed:
                raise ValueError("Missing or changed forecast seed")
            if row.model_name in MODEL_PINS:
                if (output.metadata.get("model_id"), output.metadata.get("revision")) != MODEL_PINS[
                    row.model_name
                ]:
                    raise ValueError("Forecast model pin differs from registration")
        expected_seed = derived_seed(
            config.seed, "pit", row.repo_name, row.cutoff_date, row.horizon, row.model_name
        )
        if row.pit_seed != expected_seed:
            raise ValueError("PIT seed does not match the declared run seed and window")
        metrics = evaluate_forecast(
            output,
            actuals,
            context=context,
            quantile_levels=config.quantile_levels,
            seasonal_period=config.seasonal_period,
            seed=row.pit_seed,
        )
        for metric in SCORE_COLUMNS:
            if not np.isclose(
                getattr(row, metric), metrics[metric], rtol=1e-10, atol=1e-12, equal_nan=True
            ):
                raise ValueError(f"Saved {metric} does not match forecast recomputation")
        if row.pit_method != metrics["pit_method"] or row.crps_method != metrics["crps_method"]:
            raise ValueError("Metric representation labels are inconsistent")
        if not np.array_equal(row.pit_values, metrics["pit_values"]):
            raise ValueError("Saved PIT does not match seeded recomputation")

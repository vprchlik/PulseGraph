"""Offline development commands. Real-target evaluation is not enabled."""

import argparse
import gzip
import json
import sys
from pathlib import Path

import pandas as pd

from pulsegraph.data.ingest import aggregate_star_timestamps
from pulsegraph.data.loader import build_dataset_for_forecasting, generate_synthetic_data
from pulsegraph.evaluation.artifacts import file_hash, read_run_artifact, write_run_artifact
from pulsegraph.evaluation.backtest import BacktestConfig, run_backtest_suite
from pulsegraph.evaluation.reviews import (
    Comparison,
    review_censoring,
    review_cluster_inference,
    review_local_mean_lookbacks,
    review_scale,
    review_strong_baselines,
    review_windows,
)
from pulsegraph.forecast.baselines import BASELINE_FORECASTERS, LocalMeanForecaster
from pulsegraph.forecast.output import COMMON_QUANTILES
from pulsegraph.validation import positive_int


def synthetic_main(argv=None):
    parser = argparse.ArgumentParser(
        description="Synthetic study-code check; no real-data runner yet"
    )
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--n-repos", type=int, default=3)
    parser.add_argument("--n-days", type=int, default=360)
    parser.add_argument("--n-samples", type=int, default=200)
    parser.add_argument("--horizons", type=int, nargs="+", default=[7, 30, 90])
    parser.add_argument("--n-windows", type=int, default=2)
    parser.add_argument("--min-context-days", type=int, default=90)
    parser.add_argument(
        "--models",
        nargs="+",
        choices=sorted(BASELINE_FORECASTERS),
        default=["last_value", "weekly_naive", "local_mean_28"],
    )
    parser.add_argument("--local-mean-lookbacks", nargs="*", type=int, default=[])
    args = parser.parse_args(argv)
    if not args.synthetic:
        parser.error("Only --synthetic is supported before protocol registration")
    positive_int(args.n_windows, "n_windows")
    positive_int(args.n_days, "n_days")
    if not args.horizons or min(args.horizons) < 1:
        parser.error("Horizons must be positive")
    if args.out.exists():
        parser.error("Output directory already exists; choose a new artifact path")
    if len(set(args.models)) != len(args.models):
        parser.error("Duplicate model names")
    forecasters = {
        name: BASELINE_FORECASTERS[name](seed=args.seed, n_samples=args.n_samples)
        for name in args.models
    }
    for lookback in args.local_mean_lookbacks:
        model = LocalMeanForecaster(seed=args.seed, lookback=lookback, n_samples=args.n_samples)
        if model.name in forecasters:
            parser.error("Duplicate local-mean lookback")
        forecasters[model.name] = model
    start = pd.Timestamp("2022-01-01")
    end = start + pd.Timedelta(days=args.n_days - 1)
    max_horizon = max(args.horizons)
    cutoffs = tuple(
        (end - pd.Timedelta(days=window * max_horizon - 1)).date().isoformat()
        for window in range(args.n_windows, 0, -1)
    )
    config = BacktestConfig(
        tuple(args.horizons), cutoffs, args.min_context_days, COMMON_QUANTILES, 7, args.seed
    )
    if args.n_days - args.n_windows * max_horizon < args.min_context_days:
        parser.error("Synthetic calendar leaves insufficient training context")
    signals = generate_synthetic_data(n_repos=args.n_repos, n_days=args.n_days, seed=args.seed)
    manifest = pd.DataFrame(
        {
            "repo_name": sorted(signals.repo_name.unique()),
            "observation_start": start.date().isoformat(),
            "coverage_complete": True,
        }
    )
    dataset = build_dataset_for_forecasting(signals, manifest, observation_end=end)
    results = run_backtest_suite(dataset, forecasters, config)
    write_run_artifact(
        args.out,
        results=results,
        signals=signals,
        manifest=manifest,
        config=config,
        observation_end=end.date().isoformat(),
        models=list(forecasters),
        data_kind="synthetic",
        command=list(sys.argv if argv is None else argv),
    )
    read_run_artifact(args.out)
    print(f"Validated synthetic artifact: {len(results)} windows in {args.out}")


def ingest_main(argv=None):
    parser = argparse.ArgumentParser(description="Aggregate saved REST timestamps offline")
    parser.add_argument(
        "--timestamps",
        type=Path,
        required=True,
        help="JSON or JSON.gz mapping repo_name to timezone-aware timestamp lists",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="JSON records with repo_name, observation_start and coverage_complete",
    )
    parser.add_argument("--observation-end", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out.exists():
        parser.error("Output directory already exists")
    opener = gzip.open if args.timestamps.suffix == ".gz" else open
    with opener(args.timestamps, "rt", encoding="utf-8") as stream:
        histories = json.load(stream)
    manifest = pd.DataFrame(json.loads(args.manifest.read_text(encoding="utf-8")))
    if not isinstance(histories, dict) or set(histories) != set(manifest.repo_name):
        parser.error("Every manifest repository must have a timestamp list, including empty lists")
    daily = aggregate_star_timestamps(histories, observation_end=args.observation_end)
    build_dataset_for_forecasting(daily, manifest, observation_end=args.observation_end)
    args.out.mkdir(parents=True)
    daily.to_parquet(args.out / "daily_signals.parquet", index=False)
    metadata = {
        "source": "rest_surviving_stargazers",
        "observation_end": args.observation_end,
        "timestamps_sha256": file_hash(args.timestamps),
        "manifest_sha256": file_hash(args.manifest),
        "command": list(sys.argv if argv is None else argv),
        "limitation": "Surviving stars only; not the v2 GH Archive population dataset",
    }
    (args.out / "ingest.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(
        f"Aggregated {len(daily)} nonempty repository/day rows; "
        "observation bounds are in the manifest"
    )


REVIEW_NAMES = (
    "integrity",
    "windows",
    "scale",
    "strong_baselines",
    "local_mean_lookbacks",
    "cluster_inference",
    "censoring",
)


def review_main(name: str, argv=None):
    if name not in REVIEW_NAMES:
        raise ValueError("Unknown review")
    parser = argparse.ArgumentParser(description=f"Post-hoc {name} review of a saved artifact")
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    if name in ("scale", "cluster_inference"):
        parser.add_argument("--metric", required=True)
    if name == "scale":
        parser.add_argument("--reference", required=True)
    if name == "strong_baselines":
        parser.add_argument("--baselines", nargs="+", required=True)
    if name == "local_mean_lookbacks":
        parser.add_argument("--lookbacks", nargs="+", type=int, required=True)
    if name == "cluster_inference":
        parser.add_argument(
            "--comparisons",
            type=Path,
            required=True,
            help="JSON list of model, reference, horizon, stratum objects",
        )
        parser.add_argument("--declared-count", type=int, required=True)
        parser.add_argument("--seed", type=int, required=True)
        parser.add_argument("--n-bootstrap", type=int, required=True)
        parser.add_argument("--confidence", type=float, required=True)
    args = parser.parse_args(argv)
    if args.out is not None and (args.out.exists() or args.out.with_suffix(".meta.json").exists()):
        parser.error("Review output or metadata already exists")
    results, metadata, dataset = read_run_artifact(args.run)
    if name == "integrity":
        output = pd.DataFrame(
            [
                {
                    "status": "pass",
                    "n_rows": len(results),
                    "n_models": len(metadata["models"]),
                    "n_repos": len(dataset),
                }
            ]
        )
    elif name == "windows":
        output = review_windows(results, dataset)
    elif name == "censoring":
        output = review_censoring(dataset)
    elif name == "scale":
        output = review_scale(results, reference=args.reference, metric=args.metric)
    elif name == "strong_baselines":
        output = review_strong_baselines(results, baseline_names=args.baselines)
    elif name == "local_mean_lookbacks":
        output = review_local_mean_lookbacks(results, lookbacks=args.lookbacks)
    else:
        comparisons = [
            Comparison(**record)
            for record in json.loads(args.comparisons.read_text(encoding="utf-8"))
        ]
        output = review_cluster_inference(
            results,
            comparisons=comparisons,
            declared_count=args.declared_count,
            metric=args.metric,
            seed=args.seed,
            n_bootstrap=args.n_bootstrap,
            confidence=args.confidence,
        )
    output["analysis_status"] = "post_hoc"
    output["data_kind"] = metadata["data_kind"]
    provenance = {
        "review": name,
        "analysis_status": "post_hoc",
        "data_kind": metadata["data_kind"],
        "run_metadata_sha256": file_hash(args.run / "run.json"),
        "arguments": {
            key: str(value) if isinstance(value, Path) else value
            for key, value in vars(args).items()
        },
    }
    if name == "cluster_inference":
        provenance["comparisons_sha256"] = file_hash(args.comparisons)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        output.to_csv(args.out, index=False, mode="x")
        with args.out.with_suffix(".meta.json").open("x", encoding="utf-8") as stream:
            json.dump(provenance, stream, indent=2)
            stream.write("\n")
    else:
        print(output.to_string(index=False))

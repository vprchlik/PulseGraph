"""Fail-closed registration gate. Git subprocesses here are strictly read-only."""

import re
import subprocess
from importlib.metadata import distributions
from pathlib import Path

import pandas as pd

from pulsegraph.config import ROOT_DIR
from pulsegraph.data.calendars import CALENDAR_HYPOTHESES, creation_day
from pulsegraph.data.history_validation import validation_status_counts
from pulsegraph.data.loader import build_dataset_for_forecasting, validate_signals
from pulsegraph.data.regimes import assert_eligibility_precedes_cutoff
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.evaluation.backtest import BacktestConfig
from pulsegraph.provenance import read_json, sha256_bytes

PROTOCOL_COMMIT = "5f01769b6be4c32814befdd7cc3395b6dcc386ed"
PROTOCOL_SHA256 = "dfe2f4adf5c3fdafaa6f2716ae7c19cd4d52577497041c13b763ba06540f65c5"
MODEL_PINS = {
    "chronos2": ("amazon/chronos-2", "29ec3766d36d6f73f0696f85560a422f50e8498c"),
    "timesfm3": ("google/timesfm-3.0-pytorch", "43046b85ec22d584a13f8098c2ed39c889e129c2"),
    "timesfm2p5": ("google/timesfm-2.5-200m-pytorch", "1d952420fba87f3c6dee4f240de0f1a0fbc790e3"),
}
SEEDS = {"selection": 20260913, "forecast": 20260912, "bootstrap": 20260914}
BASELINES = [
    "naive_seasonal",
    "linear_30",
    "ets",
    "lightgbm",
    "last_value",
    "weekly_naive",
    "local_mean_28",
    "local_mean_7",
    "local_mean_14",
    "local_mean_56",
    "local_mean_90",
    "autoets_weekly",
    "autoarima_weekly",
    "autotheta_weekly",
    "nb_local_level_28",
]
RUNTIME_PACKAGES = {
    "numpy",
    "pandas",
    "pyarrow",
    "scipy",
    "statsmodels",
    "lightgbm",
    "torch",
    "timesfm",
    "chronos-forecasting",
    "huggingface-hub",
    "statsforecast",
}
EVIDENCE_ROLES = {
    "validation",
    "comparison",
    "frame_coverage",
    "candidate_order",
    "sampling_log",
    "cost_approval",
    "query_provenance",
    "smoke",
}


def installed_versions():
    return {
        dist.metadata["Name"].lower().replace("_", "-"): dist.version for dist in distributions()
    }


def _git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.DEVNULL)


def validate_declarations(spec, family):
    if (
        spec.get("protocol_commit") != PROTOCOL_COMMIT
        or spec.get("protocol_sha256") != PROTOCOL_SHA256
    ):
        raise ValueError("Missing or mismatching protocol registration")
    if spec.get("seeds") != SEEDS or spec.get("config", {}).get("seed") != SEEDS["forecast"]:
        raise ValueError("Missing or mismatching registered seeds")
    declared = spec.get("foundation_models", [])
    pins = {m.get("name"): (m.get("model_id"), m.get("revision")) for m in declared}
    if len(declared) != 3 or pins != MODEL_PINS:
        raise ValueError("Unpinned or unregistered foundation model")
    expected = [
        {"model": model, "reference": reference, "horizon": horizon, "stratum": "all"}
        for model in MODEL_PINS
        for reference in ("local_mean_28", "autoets_weekly")
        for horizon in (7, 30, 90)
    ]
    if family.get("comparison_count") != 18 or family.get("comparisons") != expected:
        raise ValueError("Confirmatory family must contain exactly the registered 18 comparisons")
    settings = dict(
        protocol_commit=PROTOCOL_COMMIT,
        metric="qscore9",
        alternative="two-sided",
        adjustment="BH",
        q=0.05,
        bootstrap_replicates=20000,
        bootstrap_seed=20260914,
        regimes="pooled",
        calendar_conditional=True,
    )
    if any(family.get(k) != v for k, v in settings.items()):
        raise ValueError("Confirmatory inference settings differ from registration")
    config = BacktestConfig(**spec["config"])
    if (
        spec.get("baselines") != BASELINES
        or config.min_context_days != 90
        or config.seasonal_period != 7
        or config.quantile_levels != tuple(i / 10 for i in range(1, 10))
    ):
        raise ValueError("Baseline/score declarations differ from registration")
    inference = spec.get("inference", {})
    required_settings = dict(
        max_context=2048,
        max_horizon=128,
        batch_size=1,
        threads=4,
        device="cuda",
        n_samples=200,
        peak_vram_limit_bytes=8_000_000_000,
    )
    if any(inference.get(k) != v for k, v in required_settings.items()):
        raise ValueError("Frozen inference settings differ")
    if spec.get("package_pins") != {"timesfm": "3.0.2", "statsforecast": "2.1.1"}:
        raise ValueError("Registered runtime pins differ")
    endpoint = pd.Timestamp("2026-08-31")
    calendar = tuple(
        (endpoint - pd.Timedelta(days=j * 90 - 1)).date().isoformat() for j in (3, 2, 1)
    )
    if (
        config.cutoffs != calendar
        or config.horizons != (7, 30, 90)
        or spec["observation_end"] != "2026-08-31"
    ):
        raise ValueError("Evaluation calendar differs from registration")
    return config


def verify_source_registration(root, implementation_commit):
    if not isinstance(implementation_commit, str) or not re.fullmatch(
        "[0-9a-f]{40}", implementation_commit
    ):
        raise ValueError("A full non-null implementation commit is required")
    if _git(root, "rev-parse", "HEAD").decode().strip() != implementation_commit:
        raise ValueError("Implementation commit must be the current HEAD")
    blob = _git(root, "show", f"{PROTOCOL_COMMIT}:PROTOCOL.md")
    if sha256_bytes(blob) != PROTOCOL_SHA256 or file_hash(root / "PROTOCOL.md") != PROTOCOL_SHA256:
        raise ValueError("Protocol bytes differ from the registration commit")
    # Include declarations/tests/entry points and packaging; .env stays ignored.
    paths = ["PROTOCOL.md", "pyproject.toml", "pulsegraph", "scripts", "tests", "study"]
    if _git(root, "status", "--porcelain", "--untracked-files=all", "--", *paths).strip():
        raise ValueError("Implementation and study declarations must be committed and clean")
    tracked = set(_git(root, "ls-files").decode().splitlines())
    if not {"study/run_spec.json", "study/comparisons.json"}.issubset(tracked):
        raise ValueError("Run declarations must be tracked")
    return {
        path: file_hash(root / path)
        for path in sorted(tracked)
        if (root / path).is_file()
        and (path in paths[:2] or path.startswith(("pulsegraph/", "scripts/", "tests/", "study/")))
    }


def verify_readiness(readiness, base, spec):
    if (
        readiness.get("protocol_commit") != PROTOCOL_COMMIT
        or readiness.get("protocol_sha256") != PROTOCOL_SHA256
    ):
        raise ValueError("Readiness must identify the registered protocol")
    for key in (
        "approved_by",
        "approved_at",
        "bin_to_calendar_mapping",
        "timezone_evidence",
        "unstar_interpretation",
        "later_information_limitation",
        "long_run_approval",
    ):
        if not isinstance(readiness.get(key), str) or not readiness[key].strip():
            raise ValueError(f"Unresolved main-study readiness: {key}")
    if readiness.get("main_study_resolved") is not True:
        raise ValueError("Main-study freeze requirements are unresolved")
    if readiness.get("calendar_convention") not in CALENDAR_HYPOTHESES:
        raise ValueError("The validated calendar convention is required")
    versions = installed_versions()
    pins = readiness.get("runtime_versions", {})
    if not RUNTIME_PACKAGES.issubset(pins) or any(versions.get(k) != v for k, v in pins.items()):
        raise ValueError("Missing or changed exact runtime versions")
    if any(pins.get(k) != v for k, v in spec["package_pins"].items()):
        raise ValueError("Registered package pins differ")
    evidence = readiness.get("evidence", {})
    if set(evidence) != EVIDENCE_ROLES:
        raise ValueError("Missing pre-run provenance evidence")
    documents = {}
    for role, item in evidence.items():
        path = (base / item["path"]).resolve()
        if file_hash(path) != item["sha256"]:
            raise ValueError(f"Evidence hash mismatch: {role}")
        documents[role] = read_json(path) if path.suffix == ".json" else path
    validation_counts = validation_status_counts(documents["validation"])
    if validation_counts["n_complete"] == 0:
        raise ValueError("At least one complete validation capture is required")
    smoke = documents["smoke"]
    checks = smoke.get("median_checks", {})
    if set(checks) != {"autoets_weekly", "autoarima_weekly", "autotheta_weekly"} or any(
        c.get("passed") is not True for c in checks.values()
    ):
        raise ValueError("Native median/interval smoke checks are missing")
    if (
        smoke.get("passed") is not True
        or smoke.get("models") != list(MODEL_PINS) + spec["baselines"]
    ):
        raise ValueError("All registered models need a successful synthetic preflight smoke")
    peak = smoke.get("peak_vram_bytes")
    if not isinstance(peak, int) or not 0 < peak < spec["inference"]["peak_vram_limit_bytes"]:
        raise ValueError("GPU smoke must demonstrate peak VRAM below 8 GB")
    comparison = documents["comparison"]
    complete_ids = sorted(
        r["repo_id"] for r in documents["validation"]["repositories"] if r["status"] == "complete"
    )
    if (
        comparison.get("n_rows") != validation_counts["n_complete"] * 366 * 3
        or comparison.get("hypotheses") != list(CALENDAR_HYPOTHESES)
        or comparison.get("n_hourly_rows") != validation_counts["n_complete"] * 366 * 24
        or comparison.get("n_scored_days_per_repository_hypothesis") != 365
        or any(comparison.get(k) != v for k, v in validation_counts.items())
        or comparison.get("compared_repo_ids") != complete_ids
        or comparison.get("failures") != documents["validation"]["failures"]
    ):
        raise ValueError(
            "The 2024 comparison must cover all complete captures and report every failure"
        )
    if documents["comparison"].get("validation_sha256") != evidence["validation"]["sha256"]:
        raise ValueError("Comparison does not refer to this validation capture")
    if documents["frame_coverage"].get("complete") is not True:
        raise ValueError("Historical frame coverage is unverified")
    for role in ("cost_approval", "query_provenance"):
        if not isinstance(documents[role], dict) or not documents[role]:
            raise ValueError(f"Missing recorded {role}")
    if smoke.get("runtime_versions") != pins or smoke.get("implementation_commit") != readiness.get(
        "implementation_commit"
    ):
        raise ValueError("Smoke provenance differs from approved runtime/implementation")
    return versions, documents


def real_run_gate(
    *, readiness_path, signals_path, manifest_path, implementation_commit, root=ROOT_DIR
):
    root = Path(root)
    spec, family = (
        read_json(root / "study/run_spec.json"),
        read_json(root / "study/comparisons.json"),
    )
    config = validate_declarations(spec, family)
    source_hashes = verify_source_registration(root, implementation_commit)
    readiness_path, signals_path, manifest_path = map(
        Path, (readiness_path, signals_path, manifest_path)
    )
    readiness = read_json(readiness_path)
    if readiness.get("implementation_commit") != implementation_commit:
        raise ValueError("Readiness was not approved for this implementation commit")
    versions, evidence = verify_readiness(readiness, readiness_path.parent, spec)
    for key, path in (("signals_sha256", signals_path), ("manifest_sha256", manifest_path)):
        if readiness.get(key) != file_hash(path):
            raise ValueError("Inputs differ from the frozen achieved manifest/data")
    signals = validate_signals(pd.read_parquet(signals_path))
    manifest = pd.DataFrame(read_json(manifest_path))
    required = {
        "repo_id",
        "creation_date",
        "day90_stars",
        "sampling_stratum",
        "observation_start",
        "repo_name",
        "coverage_complete",
    }
    if not required.issubset(manifest) or manifest.repo_id.duplicated().any():
        raise ValueError("Incomplete or duplicate achieved manifest")
    from pulsegraph.data.frame import freeze_frame_order

    freeze_frame_order(manifest[list(required)].copy())
    if (manifest.groupby("sampling_stratum").size() > 100).any():
        raise ValueError("Achieved panel exceeds 100 per stratum")
    from pulsegraph.data.frame import validate_sampling_log

    validate_sampling_log(evidence["candidate_order"], evidence["sampling_log"], manifest)
    if "repository_created_at" not in manifest:
        raise ValueError("Manifest requires the endpoint repository creation timestamp")
    for row in manifest.itertuples(index=False):
        if creation_day(row.repository_created_at, "UTC") != str(row.creation_date) or creation_day(
            row.repository_created_at, readiness["calendar_convention"]
        ) != str(row.observation_start):
            raise ValueError("Every observation history must begin at creation in its calendar")
    dataset = build_dataset_for_forecasting(
        signals, manifest, observation_end=spec["observation_end"]
    )
    for name, series in dataset.items():
        # Endpoint histories must explicitly contain every day: never impute exposure here.
        if len(signals[signals.repo_name.eq(name)]) != len(series):
            raise ValueError(
                "Missing observed daily bins; zero filling is forbidden for real inputs"
            )
        assert_eligibility_precedes_cutoff(series.index[0], config.cutoffs[0])
    metadata = {
        "schema_version": 2,
        "data_kind": "real",
        "protocol_commit": PROTOCOL_COMMIT,
        "protocol_sha256": PROTOCOL_SHA256,
        "implementation_commit": implementation_commit,
        "source_sha256": source_hashes,
        "packages": versions,
        "specification": spec,
        "config": spec["config"],
        "observation_end": spec["observation_end"],
        "models": list(MODEL_PINS) + spec["baselines"],
        "repositories": sorted(dataset),
        "comparison_family": family,
        "comparison_count": 18,
        "seeds": SEEDS,
        "readiness": readiness,
        "readiness_sha256": file_hash(readiness_path),
        "input_sha256": {"signals": file_hash(signals_path), "manifest": file_hash(manifest_path)},
    }
    return metadata, config, signals, manifest, dataset, evidence

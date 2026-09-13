"""Synthetic-only runtime/GPU smoke; no input-data argument and no real repositories."""

import argparse
import sys
from pathlib import Path
from time import perf_counter

import numpy as np

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.registration import (
    MODEL_PINS,
    installed_versions,
    validate_declarations,
    verify_source_registration,
)
from pulsegraph.forecast.hardware import configure_gpu, memory_snapshot
from pulsegraph.forecast.registered import make_registered_model, release_model
from pulsegraph.forecast.statsforecast_forecaster import verify_classical_medians
from pulsegraph.provenance import atomic_json, read_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--implementation-commit", required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("Smoke reports must not be overwritten")
    spec = read_json(ROOT_DIR / "study/run_spec.json")
    validate_declarations(spec, read_json(ROOT_DIR / "study/comparisons.json"))
    sources = verify_source_registration(ROOT_DIR, args.implementation_commit)
    hardware = configure_gpu()
    names = list(MODEL_PINS) + spec["baselines"]
    rng = np.random.default_rng(spec["seeds"]["forecast"])
    contexts = [
        np.zeros(90),
        rng.poisson(3, 1350).astype(float),
        np.tile([0.0, 1.0, 3.0, 8.0, 3.0, 1.0, 0.0], 293)[:2048],
    ]
    report = {
        "data_kind": "synthetic",
        "passed": False,
        "models": names,
        "implementation_commit": args.implementation_commit,
        "protocol_commit": spec["protocol_commit"],
        "protocol_sha256": spec["protocol_sha256"],
        "runtime_versions": installed_versions(),
        "source_sha256": sources,
        "hardware": hardware,
        "seed": spec["seeds"]["forecast"],
        "command": [sys.executable, *sys.argv],
        "fits": [],
    }
    atomic_json(args.out, report)
    try:
        report["median_checks"] = verify_classical_medians()
        for name in names:
            model = make_registered_model(name, spec)
            try:
                for case, context in enumerate(contexts):
                    for horizon in (7, 30, 90):
                        start = perf_counter()
                        result = model.forecast(context, horizon, f"synthetic/smoke-{case}")
                        elapsed = perf_counter() - start
                        if not np.isfinite(result.quantiles).all():
                            raise ValueError("Nonfinite smoke forecast")
                        report["fits"].append(
                            {
                                "model": name,
                                "case": case,
                                "context_length": len(context),
                                "horizon": horizon,
                                "seconds": elapsed,
                                "metadata": result.metadata,
                            }
                        )
                        atomic_json(args.out, report)
            finally:
                release_model(model)
        report["memory"] = memory_snapshot()
        report["peak_vram_bytes"] = report["memory"]["peak_reserved_bytes"]
        report["passed"] = True
    except BaseException as error:
        report["error_type"] = type(error).__name__
        raise
    finally:
        atomic_json(args.out, report)


if __name__ == "__main__":
    main()

"""Synthetic-only Study 2 CRPS certification and optional GPU timing, never real panels."""

import argparse
import os
import subprocess
from pathlib import Path

import numpy as np

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.evaluation.registration import installed_versions
from pulsegraph.provenance import atomic_json
from pulsegraph.study2.constants import (
    PROTOCOL_COMMIT,
    PROTOCOL_SHA256,
    SEEDS,
    STUDY3_PROTOCOL_SHA256,
    STUDY3_SEEDS,
    STUDY3_VARIANTS,
    VARIANTS,
)
from pulsegraph.study2.distributions import CountLaw, complete, discrete_crps, fm_hurdle
from pulsegraph.study2.holdout import utc_now


def crps_smoke():
    laws = [
        complete(np.zeros(9)),
        complete(np.arange(9) * 400),
        CountLaw(dict(kind="poisson", mu=0)),
        CountLaw(dict(kind="poisson", mu=100)),
        CountLaw(dict(kind="nb", shape=0.2, probability=0.003)),
        fm_hurdle(complete(np.zeros(9)), 0.5 / 29),
    ]
    cases = []
    for law in laws:
        for y in (0, 1, 17, 1000):
            result = discrete_crps(law, y)
            k = np.arange(result["last_k"] + 1, result["last_k"] + 100000)
            residual = float(np.sum(law.sf(k) ** 2))
            if residual > result["residual_bound"] + 1e-15:
                raise AssertionError("CRPS tail certificate failed independent extended sum")
            cases.append(
                dict(distribution=law.spec, target=y, **result, extended_sum_residual=residual)
            )
    return dict(
        status="resolved_by_offline_smoke",
        tolerance=1e-8,
        max_k=1000000,
        certification="analytic upper bound; completed exponential tail summed geometrically",
        cases=cases,
        maximum_residual_bound=max(c["residual_bound"] for c in cases),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--gpu", action="store_true")
    parser.add_argument("--context-days", type=int, default=1400)
    parser.add_argument("--leads", type=int, default=60)
    parser.add_argument(
        "--study3",
        action="store_true",
        help="Study 3's smoke: its seeds, its 22 variants and the study3 scripts' hashes",
    )
    args = parser.parse_args()
    if args.context_days < 28 or not 1 <= args.leads <= 128:
        parser.error("At least 28 context days and 1 to 128 leads are required")
    if args.out.exists():
        raise FileExistsError("Smoke evidence is immutable")
    paths = [
        *sorted((ROOT_DIR / "pulsegraph/study2").glob("*.py")),
        *sorted((ROOT_DIR / "scripts").glob("study2_*.py")),
        *(sorted((ROOT_DIR / "scripts").glob("study3_*.py")) if args.study3 else []),
    ]
    seeds, variants = (STUDY3_SEEDS, STUDY3_VARIANTS) if args.study3 else (SEEDS, VARIANTS)
    registration = (
        dict(component="study3", protocol_sha256=STUDY3_PROTOCOL_SHA256)
        if args.study3
        else dict(protocol_commit=PROTOCOL_COMMIT, protocol_sha256=PROTOCOL_SHA256)
    )
    report = dict(
        data_kind="synthetic",
        passed=False,
        at=utc_now().isoformat(),
        **registration,
        implementation_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT_DIR)
        .decode()
        .strip(),
        source_sha256={
            str(p.relative_to(ROOT_DIR)).replace("\\", "/"): file_hash(p) for p in paths
        },
        packages=installed_versions(),
        seeds=seeds,
        variants=list(variants),
        crps=crps_smoke(),
    )
    if args.gpu:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        from pulsegraph.forecast.hardware import configure_gpu, memory_snapshot
        from pulsegraph.study2.models import ModelPool

        report["hardware"] = configure_gpu()
        context = np.random.default_rng(seeds["forecast"]).poisson(2, args.context_days)
        pool = ModelPool(study3=True) if args.study3 else ModelPool(prospective=True)
        with pool as models:
            forecasts = models.forecast(context, args.leads, "synthetic/holdout-smoke")
            assert set(forecasts) == set(variants)
            report["per_model"] = models.timings
            report["memory"] = memory_snapshot()
    report["passed"] = True
    atomic_json(args.out, report)


if __name__ == "__main__":
    main()

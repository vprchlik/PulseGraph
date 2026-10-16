"""Study 2 and Study 3 run entry point. Signed component gate always precedes data/model access."""

import argparse
import json
from pathlib import Path

from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.forecast.hardware import configure_gpu, memory_snapshot
from pulsegraph.study2.constants import STUDY3_VARIANTS, VARIANTS
from pulsegraph.study2.gate import authorize_component
from pulsegraph.study2.models import ModelPool
from pulsegraph.study2.runner import _evaluate, external_dataset

TARGET_COMPONENTS = ("external_packages", "study3")


def fetch_targets(args):
    """The target days of the frozen panel (npm, or NYC 311 for Study 3); no model is loaded."""
    from pulsegraph.study2.ingestion import (
        CaptureClient,
        NpmSource,
        NYCSource,
        pull_nyc_targets,
        pull_targets,
    )

    authorize_component(args.readiness, args.component)
    out = Path(args.out)
    client = CaptureClient(
        out / "captures",
        max_requests=args.max_requests,
        interval=args.interval,
        timeout=args.timeout,
    )
    try:
        if args.component == "study3":
            document = pull_nyc_targets(args.readiness, NYCSource(client), out)
        else:
            document = pull_targets(args.readiness, NpmSource(client), out)
    finally:
        print(json.dumps(dict(attempts_this_invocation=client.requests)))
    print(
        json.dumps(
            {
                key: document[key]
                for key in ("series", "first_target_day", "last_complete_day", "signals_sha256")
            }
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "component", choices=("external", "external_packages", "synthetic", "study3")
    )
    parser.add_argument("--readiness", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--fetch-targets",
        action="store_true",
        help="external_packages or study3 only: pull the target days into --out and stop",
    )
    parser.add_argument("--max-requests", type=int, help="the approved HTTP attempts")
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=45, help="seconds to wait for a response")
    args = parser.parse_args()
    if args.fetch_targets:
        if args.component not in TARGET_COMPONENTS or not args.max_requests:
            parser.error("--fetch-targets takes external_packages or study3 and --max-requests")
        fetch_targets(args)
        return
    bundle = authorize_component(args.readiness, args.component)
    if args.component == "synthetic":
        from pulsegraph.study2.synthetic import grid_dataset

        dataset = grid_dataset()
    else:
        dataset = external_dataset(bundle["readiness"])
    metadata = dict(
        **bundle, readiness_sha256=file_hash(Path(args.readiness)), hardware=configure_gpu()
    )
    study3 = args.component == "study3"
    with ModelPool(study3=True) if study3 else ModelPool() as pool:
        _evaluate(
            dataset,
            args.out,
            pool,
            metadata=metadata,
            synthetic=args.component == "synthetic",
            memory=memory_snapshot,
            variants=STUDY3_VARIANTS if study3 else VARIANTS,
        )


if __name__ == "__main__":
    main()

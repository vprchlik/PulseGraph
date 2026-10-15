"""Study 2 run entry point. Signed component gate always precedes data/model access."""

import argparse
import json
from pathlib import Path

from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.forecast.hardware import configure_gpu
from pulsegraph.study2.gate import authorize_component
from pulsegraph.study2.models import ModelPool
from pulsegraph.study2.runner import _evaluate, external_dataset


def fetch_targets(args):
    """The npm target ranges of the frozen panel; no model is loaded."""
    from pulsegraph.study2.ingestion import CaptureClient, NpmSource, pull_targets

    authorize_component(args.readiness, args.component)
    out = Path(args.out)
    client = CaptureClient(out / "captures", max_requests=args.max_requests, interval=args.interval)
    try:
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
    parser.add_argument("component", choices=("external", "external_packages", "synthetic"))
    parser.add_argument("--readiness", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--fetch-targets",
        action="store_true",
        help="external_packages only: pull the npm target ranges into --out and stop",
    )
    parser.add_argument("--max-requests", type=int, help="the approved HTTP attempts")
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    if args.fetch_targets:
        if args.component != "external_packages" or not args.max_requests:
            parser.error("--fetch-targets takes external_packages and --max-requests")
        fetch_targets(args)
        return
    bundle = authorize_component(args.readiness, args.component)
    if args.component == "synthetic":
        from pulsegraph.study2.synthetic import grid_dataset

        dataset = grid_dataset()
    else:
        dataset = external_dataset(bundle["readiness"])
    metadata = dict(**bundle, readiness_sha256=file_hash(args.readiness), hardware=configure_gpu())
    with ModelPool() as pool:
        _evaluate(
            dataset, args.out, pool, metadata=metadata, synthetic=args.component == "synthetic"
        )


if __name__ == "__main__":
    main()

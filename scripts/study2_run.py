"""Study 2 run entry point. Signed component gate always precedes data/model access."""

import argparse

from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.forecast.hardware import configure_gpu
from pulsegraph.study2.gate import authorize_component
from pulsegraph.study2.models import ModelPool
from pulsegraph.study2.runner import _evaluate, external_dataset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("component", choices=("external", "synthetic"))
    parser.add_argument("--readiness", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
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

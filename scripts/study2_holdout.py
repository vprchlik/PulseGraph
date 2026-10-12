"""Prepare a reviewable holdout plan, or freeze only after a separate signed approval."""

import argparse
from pathlib import Path

from pulsegraph.provenance import atomic_json, read_json
from pulsegraph.study2.holdout import _write_predictions, prepare_plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "freeze"))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--approval", type=Path)
    args = parser.parse_args()
    document = read_json(args.input)
    if args.action == "prepare":
        if args.out.exists():
            raise FileExistsError("Plans are immutable; choose a new path")
        atomic_json(args.out, prepare_plan(**document))
    else:
        from pulsegraph.study2.gate import authorize_holdout
        from pulsegraph.study2.models import ModelPool

        metadata = authorize_holdout(args.input, args.approval)
        with ModelPool(prospective=True) as models:
            _write_predictions(document, args.out, models.forecast, runtime_metadata=metadata)


if __name__ == "__main__":
    main()

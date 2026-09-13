"""Run/resume the registered panel only after its fail-closed gate passes."""

import argparse
import sys

from pulsegraph.evaluation.registered_run import run_registered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for argument in ("out", "readiness", "signals", "manifest", "implementation-commit"):
        parser.add_argument(f"--{argument}", required=True)
    args = parser.parse_args()
    run_registered(
        output_dir=args.out,
        readiness_path=args.readiness,
        signals_path=args.signals,
        manifest_path=args.manifest,
        implementation_commit=args.implementation_commit,
        command=[sys.executable, *sys.argv],
    )


if __name__ == "__main__":
    main()

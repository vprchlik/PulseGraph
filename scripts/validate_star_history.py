"""Fetch the fixed external validation set, or compare previously saved 2024 counts."""

import argparse
from pathlib import Path

from pulsegraph.config import ROOT_DIR
from pulsegraph.data.history_validation import compare_validation, fetch_validation
from pulsegraph.data.star_history import StarHistoryClient


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    fetch = sub.add_parser("fetch")
    fetch.add_argument(
        "--selection", type=Path, default=ROOT_DIR / "study/validation_repositories.json"
    )
    fetch.add_argument("--out", type=Path, required=True)
    compare = sub.add_parser("compare")
    compare.add_argument("--validation", type=Path, required=True)
    compare.add_argument("--archive-counts", type=Path, required=True)
    compare.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.action == "fetch":
        client = StarHistoryClient.from_env()
        try:
            report = fetch_validation(client, args.selection, args.out)
        finally:
            client.close()
        print(
            f"Attempted: {report['n_attempted']}/20; complete: {report['n_complete']}; "
            f"failed: {report['n_failed']}; failure records: {report['n_failures']}; "
            "timezone and unstars unverified"
        )
    else:
        print(
            compare_validation(args.validation, args.archive_counts, args.out).to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()

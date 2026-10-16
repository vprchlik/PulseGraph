"""Capture metadata or construct a context-only panel; never request evaluation values."""

import argparse
import json
from pathlib import Path

from pulsegraph.study2.constants import SEEDS, STUDY3_SEEDS
from pulsegraph.study2.ingestion import CaptureClient, NpmSource, NYCSource, build_panel


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("domain", choices=("npm", "nyc311", "wikipedia"))
    parser.add_argument("action", choices=("inventory", "panel"))
    parser.add_argument("--captures", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--max-requests", type=int, default=500)
    parser.add_argument("--max-seconds", type=float, default=3300)
    parser.add_argument("--interval", type=float, default=1.0, help="seconds between requests")
    parser.add_argument("--timeout", type=float, default=45, help="seconds to wait for a response")
    parser.add_argument(
        "--study3",
        action="store_true",
        help="nyc311 panel only: select with Study 3's seed, 20261001 (dated addition 7)",
    )
    args = parser.parse_args()
    if args.study3 and (args.domain, args.action) != ("nyc311", "panel"):
        parser.error("--study3 selects the NYC 311 panel of Study 3")
    client = CaptureClient(
        args.captures,
        max_requests=args.max_requests,
        max_seconds=args.max_seconds,
        interval=args.interval,
        timeout=args.timeout,
    )
    if args.domain == "wikipedia":
        from pulsegraph.study2.wikipedia import WikipediaSource

        source = WikipediaSource(client)
    else:
        source = {"npm": NpmSource, "nyc311": NYCSource}[args.domain](client)
    if args.action == "inventory":
        result = source.inventory(args.out)
        frame = result["names"] if "names" in result else result["entries"]
        print(json.dumps({"domain": args.domain, "frame_size": len(frame)}))
    else:
        metadata = getattr(source, "metadata", None)
        try:
            result = build_panel(
                args.inventory,
                source.context,
                args.out,
                fetch_metadata=metadata,
                seed=STUDY3_SEEDS["selection"] if args.study3 else SEEDS["selection"],
            )
        finally:
            print(json.dumps(dict(attempts_this_invocation=client.requests)))
        print(json.dumps(result["report"], indent=2))


if __name__ == "__main__":
    main()

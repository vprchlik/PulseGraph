"""Capture metadata or construct a context-only panel; never request evaluation values."""

import argparse
import json
from pathlib import Path

from pulsegraph.study2.ingestion import CaptureClient, NpmSource, NYCSource, build_panel


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("domain", choices=("npm", "nyc311", "wikipedia"))
    parser.add_argument("action", choices=("inventory", "panel"))
    parser.add_argument("--captures", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--max-requests", type=int, default=500)
    args = parser.parse_args()
    client = CaptureClient(args.captures, max_requests=args.max_requests)
    if args.domain == "wikipedia":
        from pulsegraph.study2.wikipedia import WikipediaSource

        source = WikipediaSource(client)
    else:
        source = {"npm": NpmSource, "nyc311": NYCSource}[args.domain](client)
    if args.action == "inventory":
        result = source.inventory(args.out)
        print(json.dumps({"domain": args.domain, "frame_size": len(result["entries"])}))
    else:
        result = build_panel(args.inventory, source.context, args.out)
        print(json.dumps(result["report"], indent=2))


if __name__ == "__main__":
    main()

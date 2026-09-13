"""Report combined cost estimates; this command cannot execute billable queries."""

import argparse
from pathlib import Path

from pulsegraph.data.bigquery_dry_run import client_from_env, dry_run_queries
from pulsegraph.provenance import atomic_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--usd-per-tib", type=float, default=6.25)
    args = parser.parse_args(argv)
    if args.out.exists():
        parser.error("Estimate output already exists")
    from google.cloud import bigquery

    try:
        with client_from_env() as client:
            report = dry_run_queries(
                client,
                query_config_factory=bigquery.QueryJobConfig,
                array_parameter_factory=bigquery.ArrayQueryParameter,
                usd_per_tib=args.usd_per_tib,
            )
    except Exception:
        # SDK errors may include credential paths or project details; keep the CLI sanitized.
        raise SystemExit("BigQuery dry run failed; check local credential configuration") from None
    atomic_json(args.out, report)
    for row in report["queries"]:
        print(f"{row['query']}: {row['bytes']:,} bytes; USD {row['estimated_usd']:.4f}")
    print(f"Combined USD {report['estimated_usd']:.4f}; no billable query was run")


if __name__ == "__main__":
    main()

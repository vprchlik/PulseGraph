"""Cost-only BigQuery submission. Every job has dry_run=True; no query result fetch."""

import math
import os
from pathlib import Path

from pulsegraph.config import ROOT_DIR
from pulsegraph.provenance import read_json, sha256_bytes

PRICE_SOURCE = "https://cloud.google.com/bigquery/pricing"


def dry_run_queries(
    client,
    *,
    query_config_factory,
    array_parameter_factory,
    study_dir=ROOT_DIR / "study",
    usd_per_tib=6.25,
):
    if not math.isfinite(usd_per_tib) or usd_per_tib <= 0:
        raise ValueError("A positive finite USD/TiB price is required")
    study = Path(study_dir)
    names = [
        r["repo_name"] for r in read_json(study / "validation_repositories.json")["repositories"]
    ]
    rows = []
    for filename in ("validation_2024.sql", "frame.sql"):
        sql = (study / filename).read_text(encoding="utf-8")
        config = query_config_factory(dry_run=True, use_query_cache=False, use_legacy_sql=False)
        if filename == "validation_2024.sql":
            config.query_parameters = [
                array_parameter_factory("validation_repositories", "STRING", names)
            ]
        job = client.query(sql, job_config=config, location="US")
        amount = job.total_bytes_processed
        if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
            raise ValueError("BigQuery did not return a valid byte estimate")
        rows.append(
            {
                "query": filename,
                "sql_sha256": sha256_bytes(sql.encode()),
                "bytes": amount,
                "estimated_usd": amount / 2**40 * usd_per_tib,
                "job_id": job.job_id,
                "dry_run": True,
            }
        )
    total = sum(row["bytes"] for row in rows)
    return {
        "queries": rows,
        "total_bytes": total,
        "estimated_usd": total / 2**40 * usd_per_tib,
        "usd_per_tib": usd_per_tib,
        "price_source": PRICE_SOURCE,
        "location": "US",
        "free_tier_credit_assumed": 0,
        "storage_export_cost": "not included; no export executed",
        "proposed_total_billing_cap_bytes": math.ceil(total * 1.10),
        "proposed_query_caps_bytes": {r["query"]: math.ceil(r["bytes"] * 1.10) for r in rows},
        "billable_execution_authorized": False,
        "validation_names": names,
        "selection_sha256": sha256_bytes((study / "validation_repositories.json").read_bytes()),
    }


def client_from_env(env_file=ROOT_DIR / ".env"):
    from dotenv import dotenv_values
    from google.auth import load_credentials_from_file
    from google.cloud import bigquery

    values = dotenv_values(env_file)
    project = os.environ.get("BIGQUERY_PROJECT_ID") or values.get("BIGQUERY_PROJECT_ID")
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or values.get(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )
    if not project:
        raise ValueError("BIGQUERY_PROJECT_ID is required")
    credentials = None
    if credentials_path:
        credentials_path = Path(credentials_path)
        if not credentials_path.is_absolute():
            credentials_path = Path(env_file).parent / credentials_path
        credentials, _ = load_credentials_from_file(
            str(credentials_path), scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
    return bigquery.Client(project=project, credentials=credentials)

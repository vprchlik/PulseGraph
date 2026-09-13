"""Metadata-only coverage audit and failed-job reconciliation; no query submission."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
from pulsegraph.data.bigquery_dry_run import client_from_env
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes

base = Path(__file__).resolve().parent
state_path = base / "frame/provenance.json"
state = read_json(state_path)
with client_from_env() as client:
    job = client.get_job(state["job_id"], location="US")
    reconciliation = {
        "job_id": job.job_id, "state": job.state,
        "error_reasons": [e.get("reason") for e in (job.errors or [])],
        "total_bytes_processed": job.total_bytes_processed,
        "total_bytes_billed": job.total_bytes_billed,
        "started_at": job.started.isoformat() if job.started else None,
        "ended_at": job.ended.isoformat() if job.ended else None,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source_provenance_sha256": sha256_bytes(state_path.read_bytes()),
        "operation": "get_job only; no resubmission",
    }
    atomic_json(base / "frame/job-reconciliation.json", reconciliation)
    print(reconciliation, flush=True)
    expected = [d.strftime("%Y%m%d") for d in pd.date_range("2023-01-01", "2025-05-21")]
    listed = {t.table_id: t.table_type for t in client.list_tables("githubarchive.day")}
    def inspect(day):
        if listed.get(day) != "TABLE":
            return {"date": day, "table_type": listed.get(day), "present": False}
        table = client.get_table("githubarchive.day." + day)
        return {
            "date": day, "table_type": table.table_type, "present": True,
            "num_rows": table.num_rows, "num_bytes": table.num_bytes,
            "modified": table.modified.isoformat(),
        }
    with ThreadPoolExecutor(max_workers=8) as pool:
        tables = list(pool.map(inspect, expected))
    complete = all(t["present"] and t["num_rows"] > 0 for t in tables)
    report = {
        "complete": complete, "scope": "Presence and nonempty physical UTC daily tables; not proof of complete GitHub event capture",
        "expected_start": "2023-01-01", "expected_end": "2025-05-21",
        "n_expected": len(expected), "n_present": sum(t["present"] for t in tables),
        "queried_at": datetime.now(timezone.utc).isoformat(),
        "operation": "list_tables and get_table only; zero query jobs submitted",
        "tables": tables,
    }
    atomic_json(base / "frame-coverage.json", report)
    print({k: report[k] for k in ("complete", "n_expected", "n_present")}, flush=True)

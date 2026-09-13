"""Two explicitly approved query exports; durable IDs prevent accidental paid resubmission."""

import csv
import json
import math
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import dotenv_values
from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from pulsegraph.config import ROOT_DIR
from pulsegraph.data.bigquery_dry_run import client_from_env
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes

CAPS = {"validation_2024.sql": 135941596319, "frame.sql": 13625742573438}
base = Path(__file__).parent
query_name = sys.argv[1]
if query_name not in CAPS:
    raise ValueError("Only the two approved queries may run")
approval_path = base / "cost-approval.json"
approval = read_json(approval_path)
assert approval["approved"] is True and approval["query_caps_bytes"] == CAPS
sql = (ROOT_DIR / "study" / query_name).read_text(encoding="utf-8")
sql_hash = sha256_bytes(sql.encode())
assert sql_hash == approval["sql_sha256"][query_name]
names = [r["repo_name"] for r in read_json(ROOT_DIR / "study/validation_repositories.json")["repositories"]]
params = [bigquery.ArrayQueryParameter("validation_repositories", "STRING", names)] if query_name.startswith("validation") else []
output = base / query_name.removesuffix(".sql")
output.mkdir(exist_ok=True)
(output / query_name).write_text(sql, encoding="utf-8")
state_path = output / "provenance.json"
identity = sha256_bytes((sql_hash + sha256_bytes(approval_path.read_bytes()) + str(output.resolve())).encode())
job_id = "pulsegraph_" + query_name.removesuffix(".sql") + "_" + identity[:24]
state = read_json(state_path) if state_path.exists() else {
    "status": "prepared", "job_id": job_id, "query": query_name,
    "sql_sha256": sql_hash, "sql_file": query_name, "location": "US",
    "maximum_bytes_billed": CAPS[query_name],
    "cost_approval_sha256": sha256_bytes(approval_path.read_bytes()),
    "parameters": {"validation_repositories": names} if params else {},
    "command": [sys.executable, str(Path(__file__).resolve()), query_name],
    "script_sha256": sha256_bytes(Path(__file__).read_bytes()),
    "implementation_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    "created_at": datetime.now(timezone.utc).isoformat(),
    "usd_per_tib": 6.25, "free_credit_assumed": 0,
}
assert state["job_id"] == job_id and state["sql_sha256"] == sql_hash
if state["status"] == "complete":
    assert sha256_bytes((output / "rows.csv").read_bytes()) == state["export_sha256"]
    print(f"Reused verified completed {query_name} export; no query submitted")
    raise SystemExit(0)
atomic_json(state_path, state)
try:
    with client_from_env() as client:
        try:
            job = client.get_job(job_id, location="US")
            print(f"Resuming existing job {job_id}", flush=True)
        except NotFound:
            if state.get("submission_attempted"):
                raise RuntimeError("A previously attempted job is absent; require manual reconciliation")
            dry = client.query(sql, location="US", job_config=bigquery.QueryJobConfig(
                dry_run=True, use_query_cache=False, use_legacy_sql=False, query_parameters=params))
            state["dry_run_bytes"] = dry.total_bytes_processed
            assert isinstance(state["dry_run_bytes"], int) and state["dry_run_bytes"] <= CAPS[query_name]
            state["submission_attempted"] = True
            atomic_json(state_path, state)
            job = client.query(sql, job_id=job_id, location="US", job_config=bigquery.QueryJobConfig(
                dry_run=False, use_query_cache=True, use_legacy_sql=False,
                maximum_bytes_billed=CAPS[query_name], query_parameters=params))
            print(f"Submitted {query_name}, cap {CAPS[query_name]:,} bytes, job {job_id}", flush=True)
        state["status"] = "submitted"
        atomic_json(state_path, state)
        rows = job.result(page_size=10000, timeout=2400)
        state.update(total_bytes_processed=job.total_bytes_processed,
                     total_bytes_billed=job.total_bytes_billed,
                     slot_millis=job.slot_millis, cache_hit=job.cache_hit,
                     started_at=job.started.isoformat() if job.started else None,
                     ended_at=job.ended.isoformat() if job.ended else None)
        assert state["total_bytes_billed"] <= CAPS[query_name]
        state["query_charge_usd_from_billed_bytes_before_credits"] = job.total_bytes_billed / 2**40 * 6.25
        state["invoice_charge_usd"] = None
        state["status"] = "exporting"
        atomic_json(state_path, state)
        temporary = output / "rows.partial.csv"
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow([f.name for f in rows.schema])
            count = 0
            for row in rows:
                writer.writerow([value.isoformat() if hasattr(value, "isoformat") else value for value in row.values()])
                count += 1
        os.replace(temporary, output / "rows.csv")
        state.update(status="complete", row_count=count,
                     export_sha256=sha256_bytes((output / "rows.csv").read_bytes()))
        atomic_json(state_path, state)
        print(json.dumps({k:state[k] for k in ("query", "job_id", "row_count", "total_bytes_processed", "total_bytes_billed", "query_charge_usd_from_billed_bytes_before_credits")}), flush=True)
except Exception as error:
    message = str(error)
    for value in sorted((v for v in dotenv_values(ROOT_DIR / ".env").values() if v), key=len, reverse=True):
        message = message.replace(value, "[configured value]")
    message = re.sub(r"[\w.+-]+@[\w.-]+", "[email]", message)
    state.update(status="failed", error_type=type(error).__name__, error=message[:2500])
    atomic_json(state_path, state)
    print(f"{type(error).__name__}: {message[:2500]}", flush=True)
    raise SystemExit(1) from None

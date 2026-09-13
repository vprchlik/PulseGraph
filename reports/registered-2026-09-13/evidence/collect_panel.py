"""Freeze and resume the registered complete-history walk; no model is constructed."""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests

from pulsegraph.config import ROOT_DIR
from pulsegraph.data.calendars import creation_day
from pulsegraph.data.frame import freeze_frame_order, walk_frame, validate_sampling_log
from pulsegraph.data.loader import validate_signals, build_dataset_for_forecasting
from pulsegraph.data.regimes import assert_eligibility_precedes_cutoff
from pulsegraph.data.star_history import StarHistoryClient, HistoryError, read_capture, decode_weeks, valid_repo, SAFE_HEADERS
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes

BASE = Path(__file__).resolve().parent
PANEL = BASE / "panel"
RAW = ROOT_DIR / "data/raw/panel-2026-09-13"
CALENDAR = "America/Los_Angeles"
END = "2026-08-31"


class PacedSession(requests.Session):
    """Serial requests below 3,600/hour; honor reset and secondary-limit backoff."""
    def __init__(self):
        super().__init__()
        self.next_request = 0.0
        self.n_requests = 0
        self.lowest_remaining = None

    def get(self, url, **kwargs):
        if urlparse(url).netloc != "api.github.com":
            raise RuntimeError("Unexpected credential destination")
        for retry in range(6):
            time.sleep(max(0, self.next_request - time.monotonic()))
            self.next_request = time.monotonic() + 1.05
            response = super().get(url, **kwargs)
            self.n_requests += 1
            remaining = int(response.headers.get("x-ratelimit-remaining", "5000"))
            reset = int(response.headers.get("x-ratelimit-reset", "0"))
            self.lowest_remaining = remaining if self.lowest_remaining is None else min(self.lowest_remaining, remaining)
            entry = {"at": datetime.now(timezone.utc).isoformat(), "path": urlparse(url).path,
                     "status": response.status_code, "remaining": remaining, "reset": reset}
            with (PANEL / "request-log.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry) + "\n")
            limited = response.status_code == 429 or (response.status_code == 403 and
                (remaining <= 100 or "Retry-After" in response.headers or "secondary rate limit" in response.text.lower()))
            if remaining <= 100 or limited:
                delay = max(60.0, float(response.headers.get("Retry-After", "60")))
                if remaining <= 100:
                    delay = max(delay, reset - time.time() + 3)
                print(f"Rate-limit pause {delay:.0f}s; remaining {remaining}; no repository skipped for rate limits", flush=True)
                self.next_request = time.monotonic() + delay
            if not limited:
                return response
        raise RuntimeError("Rate limit requires resuming this walk later; candidate not skipped")


def calendar_capture(folder, row):
    capture, _ = read_capture(folder)
    if capture["repo_id"] != row["repo_id"]:
        raise HistoryError("stable_repository_id_mismatch")
    if creation_day(capture["created_at"], "UTC") != row["creation_date"]:
        raise HistoryError("repository_creation_date_mismatch")
    weeks = []
    for response in capture["responses"]:
        if response["file"].startswith("history_"):
            weeks.extend(read_json(folder / response["file"]))
    daily = decode_weeks(weeks)
    birth = creation_day(capture["created_at"], CALENDAR)
    selected = daily[daily.nominal_date.between(birth, END)].copy()
    dates = pd.DatetimeIndex(pd.to_datetime(selected.nominal_date))
    expected = pd.date_range(birth, END)
    if dates.has_duplicates or not dates.equals(expected):
        raise HistoryError("incomplete_local_creation_through_endpoint_history")
    if daily[daily.nominal_date.lt(birth)].stars.sum() != 0:
        raise HistoryError("nonzero_history_before_local_creation")
    return capture, selected, birth


def main():
    PANEL.mkdir(exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    frame_dir = BASE / "frame-retry-001/frame"
    provenance = read_json(frame_dir / "provenance.json")
    assert provenance["status"] == "complete"
    assert sha256_bytes((frame_dir / "rows.csv").read_bytes()) == provenance["export_sha256"]
    order = freeze_frame_order(pd.read_csv(frame_dir / "rows.csv"))
    order_bytes = order.to_csv(index=False, lineterminator="\n").encode()
    order_path = PANEL / "candidate-order.csv"
    freeze_path = PANEL / "freeze.json"
    if order_path.exists():
        assert order_path.read_bytes() == order_bytes
        freeze = read_json(freeze_path)
        assert freeze["candidate_order_sha256"] == sha256_bytes(order_bytes)
    else:
        order_path.write_bytes(order_bytes)
        freeze = {
            "frozen_at": datetime.now(timezone.utc).isoformat(), "before_first_history_request": True,
            "selection_seed": 20260913, "generator": "numpy.random.default_rng / PCG64",
            "frame_export_sha256": provenance["export_sha256"],
            "frame_provenance_sha256": sha256_bytes((frame_dir / "provenance.json").read_bytes()),
            "candidate_order_sha256": sha256_bytes(order_bytes),
            "frame_sizes": order.groupby("sampling_stratum").size().to_dict(),
            "command": [sys.executable, str(Path(__file__).resolve())],
            "script_sha256": sha256_bytes(Path(__file__).read_bytes()),
            "calendar_convention": CALENDAR, "observation_end": END,
        }
        atomic_json(freeze_path, freeze)
    print("Frozen candidate order: " + json.dumps(freeze["frame_sizes"]), flush=True)
    ledger_path = PANEL / "decisions.json"
    ledger = read_json(ledger_path) if ledger_path.exists() else {}
    invocation_path = PANEL / f"invocation-{len(list(PANEL.glob('invocation-*.json'))) + 1:03d}.json"
    invocation = {"started_at": datetime.now(timezone.utc).isoformat(), "prior_decisions": len(ledger),
                  "script_sha256": sha256_bytes(Path(__file__).read_bytes()), "command": [sys.executable, str(Path(__file__).resolve())]}
    atomic_json(invocation_path, invocation)
    session = PacedSession()
    client = StarHistoryClient.from_env(session=session)

    def retrieve(row):
        key = str(row["repo_id"])
        if key in ledger:
            entry = ledger[key]
            if entry["status"] == "skipped":
                raise HistoryError(entry["reason"])
            capture, _, _ = calendar_capture(RAW / entry["capture"], row)
            return capture
        target = RAW / key
        target.mkdir(exist_ok=True)
        folder = None
        try:
            # Recover a complete capture whose ledger write was interrupted.
            for previous in sorted(target.glob("attempt_*/capture.json")):
                if read_json(previous).get("complete"):
                    calendar_capture(previous.parent, row)
                    folder = previous.parent
                    break
            if folder is None:
                response = session.get(f"https://api.github.com/repositories/{row['repo_id']}",
                                       timeout=30, allow_redirects=False)
                if response.status_code != 200:
                    if response.status_code >= 500:
                        raise RuntimeError("Transient resolver server failure; resume without skipping")
                    raise HistoryError(f"id_resolver_http_{response.status_code}")
                metadata = response.json()
                if metadata.get("private") is not False or metadata.get("id") != row["repo_id"]:
                    raise HistoryError("id_resolver_nonpublic_or_mismatched")
                name = valid_repo(metadata["full_name"])
                (target / "resolved-repository.json").write_bytes(response.content)
                atomic_json(target / "resolution.json", {
                    "frame_name": row["repo_name"], "resolved_name": name, "repo_id": row["repo_id"],
                    "at": datetime.now(timezone.utc).isoformat(), "sha256": sha256_bytes(response.content),
                    "headers": {k: response.headers[k] for k in SAFE_HEADERS if k in response.headers},
                })
                if creation_day(metadata["created_at"], "UTC") != row["creation_date"]:
                    raise HistoryError("repository_creation_date_mismatch")
                folder = target / f"attempt_{len(list(target.glob('attempt_*'))) + 1:03d}"
                client.fetch(name, folder, observation_end=END)
            capture, _, _ = calendar_capture(folder, row)
        except requests.RequestException:
            raise RuntimeError("Resolver transport failure; resume without skipping") from None
        except HistoryError as error:
            ledger[key] = {"status": "skipped", "reason": str(error), "frame_row": row,
                           "at": datetime.now(timezone.utc).isoformat(),
                           "attempt_folder": str(folder.relative_to(RAW)) if folder else None}
            atomic_json(ledger_path, ledger)
            print(f"SKIP {row['sampling_stratum']} rank={row['selection_rank']} id={key}: {error}", flush=True)
            raise
        ledger[key] = {"status": "accepted", "capture": str(folder.relative_to(RAW)), "frame_row": row,
                       "at": datetime.now(timezone.utc).isoformat(),
                       "capture_sha256": sha256_bytes((folder / "capture.json").read_bytes())}
        atomic_json(ledger_path, ledger)
        n = sum(e["status"] == "accepted" for e in ledger.values())
        if n % 5 == 0:
            print(f"Accepted {n}/300; decisions {len(ledger)}; requests {session.n_requests}; {row['sampling_stratum']} rank {row['selection_rank']}", flush=True)
        return capture

    try:
        log = walk_frame(order, retrieve)
        atomic_json(PANEL / "sampling-log.json", log)
        manifests, signals = [], []
        for row in log["accepted"]:
            entry = ledger[str(row["repo_id"])]
            folder = RAW / entry["capture"]
            capture, selected, birth = calendar_capture(folder, row)
            item = {**row, "frame_repo_name": row["repo_name"], "repo_name": capture["repo_name"],
                    "repository_created_at": capture["created_at"], "observation_start": birth,
                    "observation_end": END, "coverage_complete": True, "calendar_convention": CALENDAR,
                    "captured_at": capture["retrieved_at"], "capture_path": os.path.relpath(folder, ROOT_DIR).replace("\\", "/"),
                    "capture_sha256": sha256_bytes((folder / "capture.json").read_bytes())}
            manifests.append(item)
            signals.append(pd.DataFrame({"repo_id": row["repo_id"], "repo_name": capture["repo_name"],
                "event_date": pd.to_datetime(selected.nominal_date), "stars": selected.stars.to_numpy(dtype="int64")}))
        manifest = pd.DataFrame(manifests)
        validate_sampling_log(order_path, log, manifest)
        frame = pd.concat(signals, ignore_index=True).sort_values(["repo_name", "event_date"])
        validate_signals(frame)
        dataset = build_dataset_for_forecasting(frame, manifest, observation_end=END)
        for item in manifests:
            assert_eligibility_precedes_cutoff(item["creation_date"], "2025-12-05")
            assert len(dataset[item["repo_name"]]) == len(frame[frame.repo_id.eq(item["repo_id"])])
        atomic_json(PANEL / "manifest.json", manifests)
        frame.to_parquet(PANEL / "signals.parquet", index=False)
        summary = {"strata": log["strata"], "n_accepted": len(manifests), "n_skipped": len(log["skipped"]),
                   "n_signal_rows": len(frame), "calendar_convention": CALENDAR, "population": log["population"],
                   "selection_seed": 20260913, "completed_at": datetime.now(timezone.utc).isoformat(),
                   "skip_reasons": pd.DataFrame(log["skipped"]).groupby(["sampling_stratum", "reason"]).size().reset_index(name="count").to_dict("records") if log["skipped"] else [],
                   "artifacts": {p: sha256_bytes((PANEL / p).read_bytes()) for p in
                       ("candidate-order.csv", "freeze.json", "sampling-log.json", "manifest.json", "signals.parquet", "decisions.json")}}
        atomic_json(PANEL / "panel-summary.json", summary)
        print(json.dumps(summary), flush=True)
        invocation["status"] = "complete"
    except BaseException as error:
        invocation.update(status="interrupted", error_type=type(error).__name__)
        raise
    finally:
        client.close()
        invocation.update(ended_at=datetime.now(timezone.utc).isoformat(), requests=session.n_requests,
                          lowest_remaining=session.lowest_remaining)
        atomic_json(invocation_path, invocation)


if __name__ == "__main__":
    main()

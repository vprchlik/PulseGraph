"""Offline checks for the local extraction orchestration; no network calls."""
import importlib.util
from pathlib import Path
import json

import pandas as pd
import pytest
import requests

from pulsegraph.provenance import atomic_json, sha256_bytes

spec = importlib.util.spec_from_file_location("panel_helper", Path(__file__).with_name("collect_panel.py"))
panel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(panel)


def capture(tmp_path, weeks):
    value = {"complete": True, "repo_id": 123, "repo_name": "test/repo",
             "created_at": "2024-01-02T01:00:00+00:00", "responses": []}
    raw = json.dumps(weeks).encode()
    (tmp_path / "history_001.json").write_bytes(raw)
    value["responses"].append({"file": "history_001.json", "sha256": sha256_bytes(raw)})
    (tmp_path / "daily_nominal.csv").write_text("repo_id,stars\n123,0\n")
    value["daily_sha256"] = sha256_bytes((tmp_path / "daily_nominal.csv").read_bytes())
    atomic_json(tmp_path / "capture.json", value)


def week(day, values):
    return {"week": int(pd.Timestamp(day, tz="UTC").timestamp()), "days": values, "total": sum(values)}


def test_keeps_local_birth_day_before_utc_birth(tmp_path, monkeypatch):
    monkeypatch.setattr(panel, "END", "2024-01-07")
    capture(tmp_path, [week("2024-01-07", [0]*7), week("2023-12-31", [0,2,1,0,0,0,0])])
    _, daily, birth = panel.calendar_capture(tmp_path, {"repo_id": 123, "creation_date": "2024-01-02"})
    assert birth == "2024-01-01" and len(daily) == 7 and daily.stars.sum() == 3


def test_incomplete_birth_coverage_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(panel, "END", "2024-01-07")
    capture(tmp_path, [week("2024-01-07", [0]*7)])
    with pytest.raises(panel.HistoryError, match="incomplete_local"):
        panel.calendar_capture(tmp_path, {"repo_id": 123, "creation_date": "2024-01-02"})


def test_nonzero_before_local_creation_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(panel, "END", "2024-01-07")
    capture(tmp_path, [week("2024-01-07", [0]*7), week("2023-12-31", [1,2,1,0,0,0,0])])
    with pytest.raises(panel.HistoryError, match="nonzero_history_before"):
        panel.calendar_capture(tmp_path, {"repo_id": 123, "creation_date": "2024-01-02"})


def test_rate_limit_retries_without_skipping(tmp_path, monkeypatch):
    monkeypatch.setattr(panel, "PANEL", tmp_path)
    delays = []
    monkeypatch.setattr(panel.time, "sleep", delays.append)
    replies = []
    for status, remaining in [(429, "0"), (200, "4999")]:
        response = requests.Response()
        response.status_code = status
        response._content = b"{}"
        response.headers.update({"x-ratelimit-remaining": remaining, "Retry-After": "60"})
        replies.append(response)
    monkeypatch.setattr(requests.Session, "get", lambda *args, **kwargs: replies.pop(0))
    session = panel.PacedSession()
    assert session.get("https://api.github.com/repositories/123").status_code == 200
    assert session.n_requests == 2 and max(delays) > 59


def test_no_foreign_origin_receives_session_headers(tmp_path, monkeypatch):
    monkeypatch.setattr(panel, "PANEL", tmp_path)
    with pytest.raises(RuntimeError, match="credential destination"):
        panel.PacedSession().get("https://example.com/repositories/123")

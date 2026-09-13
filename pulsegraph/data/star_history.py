"""Privacy-safe aggregate history capture, with auditable pagination and date evidence.

API: https://docs.github.com/en/rest/activity/starring#get-repository-star-history
Nominal dates are diagnostic labels, not a claim that API bins have UTC boundaries.
"""

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests

from pulsegraph.config import ROOT_DIR
from pulsegraph.provenance import atomic_json, read_json, sha256_bytes
from pulsegraph.validation import positive_int, utc_day

API_VERSION = "2026-03-10"
SAFE_HEADERS = (
    "date",
    "etag",
    "last-modified",
    "x-github-request-id",
    "x-ratelimit-limit",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
    "retry-after",
)


class HistoryError(RuntimeError):
    """Only sanitized reason codes and HTTP statuses may escape the client."""


def valid_repo(name):
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", name):
        raise ValueError("Invalid repository name")
    if any(part in (".", "..") for part in name.split("/")):
        raise ValueError("Invalid repository name")
    return name


def _nonnegative_integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def decode_weeks(weeks):
    """Reject malformed/duplicate/missing weeks; retain each original timestamp."""
    rows, timestamps = [], []
    for entry in weeks:
        if not isinstance(entry, dict):
            raise HistoryError("malformed_week")
        stamp, total, days = entry.get("week"), entry.get("total"), entry.get("days")
        if (
            not _nonnegative_integer(stamp)
            or not _nonnegative_integer(total)
            or not isinstance(days, list)
            or len(days) != 7
            or not all(_nonnegative_integer(day) for day in days)
            or sum(days) != total
        ):
            raise HistoryError("malformed_week_counts")
        try:
            start = pd.Timestamp(stamp, unit="s", tz="UTC")
        except (ValueError, OverflowError):
            raise HistoryError("invalid_week_timestamp") from None
        timestamps.append(stamp)
        for index, count in enumerate(days):
            rows.append(
                {
                    "week": stamp,
                    "week_start_utc": start.isoformat(),
                    "day_index": index,
                    "nominal_date": (start.normalize() + pd.Timedelta(days=index))
                    .date()
                    .isoformat(),
                    "stars": count,
                }
            )
    if not timestamps or len(set(timestamps)) != len(timestamps):
        raise HistoryError("empty_or_duplicate_weeks")
    # A DST transition may change the elapsed time between local-calendar weeks.
    if any(
        not 597600 <= earlier - later <= 612000
        for earlier, later in zip(timestamps, timestamps[1:])
    ):
        raise HistoryError("unordered_or_missing_weeks")
    return pd.DataFrame(rows).sort_values(["week", "day_index"]).reset_index(drop=True)


class StarHistoryClient:
    def __init__(self, token="", *, session=None, sleep=time.sleep, attempts=3):
        self.session = requests.Session() if session is None else session
        self.sleep = sleep
        self.attempts = positive_int(attempts, "attempts")
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": API_VERSION,
            }
        )
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    @classmethod
    def from_env(cls, env_file=ROOT_DIR / ".env", **kwargs):
        from dotenv import dotenv_values

        token = os.environ.get("GITHUB_TOKEN")
        if token is None:
            token = dotenv_values(env_file).get("GITHUB_TOKEN") or ""
        return cls(token, **kwargs)

    def close(self):
        self.session.close()

    def _get(self, path, params, output, label, records):
        url = "https://api.github.com" + path
        for attempt in range(self.attempts):
            try:
                response = self.session.get(url, params=params, timeout=30, allow_redirects=False)
            except requests.RequestException:
                if attempt + 1 == self.attempts:
                    raise HistoryError("transport_failure") from None
                self.sleep(2**attempt)
                continue
            # Follow only same-origin repository redirects, never arbitrary URLs with the PAT.
            if response.status_code in (301, 302, 307, 308):
                location = urlparse(response.headers.get("Location", ""))
                suffix = "/stargazers/history" if path.endswith("/stargazers/history") else ""
                if (
                    location.scheme != "https"
                    or location.netloc != "api.github.com"
                    or not re.fullmatch(
                        r"/(repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+|repositories/\d+)" + suffix,
                        location.path,
                    )
                    or location.query
                    or location.fragment
                ):
                    raise HistoryError("unsafe_redirect")
                url = location.geturl()
                continue
            if response.status_code in (429, 500, 502, 503, 504) and attempt + 1 < self.attempts:
                delay = response.headers.get("Retry-After", str(2**attempt))
                try:
                    seconds = float(delay)
                except ValueError:
                    raise HistoryError("retry_requires_later_resume") from None
                if not 0 <= seconds <= 30:
                    raise HistoryError("retry_requires_later_resume")
                self.sleep(seconds)
                continue
            if response.status_code != 200:
                raise HistoryError(f"http_{response.status_code}")
            raw = response.content
            try:
                value = json.loads(raw)
            except (ValueError, UnicodeError):
                raise HistoryError("invalid_json") from None
            filename = f"{label}.json"
            (output / filename).write_bytes(raw)
            records.append(
                {
                    "file": filename,
                    "sha256": sha256_bytes(raw),
                    "path": path,
                    "params": params,
                    "resolved_path": urlparse(url).path,
                    "status": 200,
                    "headers": {
                        k: response.headers[k] for k in SAFE_HEADERS if k in response.headers
                    },
                }
            )
            return value, "next" in response.links
        raise HistoryError("redirect_or_retry_limit")

    def fetch(self, repo_name, output_dir, *, observation_end, created_before=None):
        valid_repo(repo_name)
        end = utc_day(observation_end)
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=False)
        records = []
        capture = {
            "requested_repo": repo_name,
            "api_version": API_VERSION,
            "observation_end": end.date().isoformat(),
            "responses": records,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "complete": False,
        }
        try:
            metadata, _ = self._get(f"/repos/{repo_name}", {}, output, "repository", records)
            try:
                created = pd.Timestamp(metadata["created_at"])
                if (
                    created.tzinfo is None
                    or not _nonnegative_integer(metadata["id"])
                    or metadata["private"] is not False
                ):
                    raise ValueError
                name = valid_repo(metadata["full_name"])
                birth = created.tz_convert("UTC").normalize().tz_localize(None)
            except (KeyError, TypeError, ValueError):
                raise HistoryError("invalid_or_nonpublic_repository") from None
            if created_before is not None and birth >= utc_day(created_before):
                raise HistoryError("validation_repository_not_pre_2023")
            if birth > end:
                raise HistoryError("repository_created_after_endpoint")
            capture.update(
                repo_id=metadata["id"],
                repo_name=name,
                created_at=created.isoformat(),
                observation_start=birth.date().isoformat(),
            )
            weeks, terminal = [], False
            for page in range(1, 101):
                values, has_next = self._get(
                    f"/repos/{name}/stargazers/history",
                    {"per_page": 30, "page": page},
                    output,
                    f"history_{page:03d}",
                    records,
                )
                if not isinstance(values, list) or len(values) > 30:
                    raise HistoryError("malformed_page")
                if not values and has_next:
                    raise HistoryError("empty_page_with_next")
                weeks.extend(values)
                if not has_next and len(values) < 30:
                    terminal = True
                    break
            if not terminal:
                raise HistoryError("pagination_limit")
            daily = decode_weeks(weeks)
            nominal = pd.to_datetime(daily.nominal_date)
            # Tolerance is for unknown bin timezone, never used to invent missing counts.
            if nominal.min() > birth + pd.Timedelta(days=1) or nominal.max() < end:
                raise HistoryError("incomplete_creation_or_endpoint_coverage")
            if nominal.min() < birth - pd.Timedelta(days=7):
                raise HistoryError("history_predates_creation_week")
            selected = daily[nominal.between(birth, end)].copy()
            selected.insert(0, "repo_name", name)
            selected.insert(0, "repo_id", metadata["id"])
            selected.to_csv(output / "daily_nominal.csv", index=False)
            expected = pd.date_range(birth, end)
            capture.update(
                complete=True,
                n_weeks=len(weeks),
                n_pages=page,
                n_days=len(selected),
                nominal_missing_days=[
                    d.date().isoformat()
                    for d in expected.difference(
                        pd.DatetimeIndex(pd.to_datetime(selected.nominal_date))
                    )
                ],
                nominal_duplicate_days=int(selected.nominal_date.duplicated().sum()),
                week_utc_seconds=sorted({int(w["week"] % 86400) for w in weeks}),
                week_utc_weekdays=sorted(
                    {pd.Timestamp(w["week"], unit="s").day_name() for w in weeks}
                ),
                timezone_status="unverified_api_day_boundaries",
                unstar_status="not_identified_by_single_snapshot",
                daily_sha256=sha256_bytes((output / "daily_nominal.csv").read_bytes()),
            )
        except HistoryError as error:
            capture["error"] = str(error)
            raise
        finally:
            atomic_json(output / "capture.json", capture)
        return capture


def read_capture(path):
    path = Path(path)
    capture = read_json(path / "capture.json")
    if not capture.get("complete"):
        raise HistoryError("incomplete_capture")
    for entry in capture["responses"]:
        filename = entry["file"]
        if (
            Path(filename).name != filename
            or sha256_bytes((path / filename).read_bytes()) != entry["sha256"]
        ):
            raise HistoryError("response_hash_mismatch")
    daily_path = path / "daily_nominal.csv"
    if sha256_bytes(daily_path.read_bytes()) != capture["daily_sha256"]:
        raise HistoryError("daily_hash_mismatch")
    return capture, pd.read_csv(daily_path)

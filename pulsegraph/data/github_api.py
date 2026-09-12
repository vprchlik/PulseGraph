"""Supplemental REST stargazer ingestion, not the v2 population selector.

The endpoint lists surviving stars and access may require repository rights.
See https://docs.github.com/en/rest/activity/starring. No search cohorts,
GraphQL, automatic retries, logging of responses, or import-time token reads.
"""

import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from pulsegraph.config import ROOT_DIR
from pulsegraph.validation import positive_int


class GitHubRequestError(RuntimeError):
    """Sanitized request failure; no response body, request headers or token."""


@dataclass(frozen=True)
class StarHistory:
    timestamps: tuple[str, ...]
    pagination_complete: bool
    retrieved_at: str
    source: str = "rest_surviving_stargazers"


class GitHubAPIClient:
    def __init__(self, token: str | None = None, *, session=None):
        self._session = session if session is not None else requests.Session()
        token = os.environ.get("GITHUB_TOKEN", "") if token is None else token
        self._session.headers.update(
            {
                "Accept": "application/vnd.github.star+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        if token:
            self._session.headers["Authorization"] = f"Bearer {token}"

    @classmethod
    def from_env(cls, env_file: Path = ROOT_DIR / ".env", *, session=None):
        """Explicitly read a token; imports never read .env or change os.environ."""
        from dotenv import dotenv_values

        token = os.environ.get("GITHUB_TOKEN")
        if token is None:
            token = dotenv_values(env_file).get("GITHUB_TOKEN") or ""
        return cls(token=token, session=session)

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def get_stargazer_timestamps(self, owner: str, repo: str, *, max_pages: int) -> StarHistory:
        positive_int(max_pages, "max_pages")
        if not all(
            re.fullmatch(r"[A-Za-z0-9_.-]+", part) and part not in (".", "..")
            for part in (owner, repo)
        ):
            raise ValueError("Invalid owner or repository name")
        timestamps, seen_users = [], set()
        complete = False
        for page in range(1, max_pages + 1):
            try:
                response = self._session.get(
                    f"https://api.github.com/repos/{owner}/{repo}/stargazers",
                    params={"per_page": 100, "page": page},
                    timeout=30,
                    allow_redirects=False,
                )
            except requests.RequestException:
                raise GitHubRequestError(
                    "GitHub request failed before a response was received"
                ) from None
            if response.status_code != 200:
                raise GitHubRequestError(
                    f"GitHub stargazer request returned HTTP {response.status_code}"
                )
            try:
                records = response.json()
                if not isinstance(records, list):
                    raise ValueError
                for entry in records:
                    stamp, user_id = entry["starred_at"], entry["user"]["id"]
                    if user_id in seen_users:
                        raise ValueError
                    day = pd.Timestamp(stamp)
                    if pd.isna(day) or day.tzinfo is None:
                        raise ValueError
                    seen_users.add(user_id)
                    timestamps.append(day.tz_convert("UTC").isoformat())
            except (KeyError, TypeError, ValueError):
                raise GitHubRequestError("Malformed or duplicate stargazer records") from None
            has_next = "next" in response.links
            if not records and has_next:
                raise GitHubRequestError("Inconsistent empty pagination response")
            if not has_next:
                complete = True
                break
        return StarHistory(tuple(timestamps), complete, datetime.now(timezone.utc).isoformat())

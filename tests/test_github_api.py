from types import SimpleNamespace

import pandas as pd
import pytest
import requests

from pulsegraph.data.github_api import GitHubAPIClient, GitHubRequestError, StarHistory
from pulsegraph.data.ingest import ingest_daily_stars


def entry(user_id, stamp="2022-01-01T01:00:00Z"):
    return {"user": {"id": user_id}, "starred_at": stamp}


class Session:
    def __init__(self, pages):
        self.headers = {}
        self.pages = iter(pages)
        self.calls = []
        self.closed = False

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return next(self.pages)

    def close(self):
        self.closed = True


def response(records, *, next_page=False, status=200):
    return SimpleNamespace(
        status_code=status,
        json=lambda: records,
        links={"next": {"url": "https://untrusted.example"}} if next_page else {},
    )


def test_pagination_is_complete_only_after_last_link_and_requests_stay_on_github():
    session = Session([response([entry(1)], next_page=True), response([entry(2)])])
    with GitHubAPIClient(token="test-token", session=session) as client:
        result = client.get_stargazer_timestamps("a", "b", max_pages=2)
    assert len(result.timestamps) == 2 and result.pagination_complete
    assert session.closed
    assert session.calls[1][1]["params"]["page"] == 2
    assert all(url.startswith("https://api.github.com/repos/") for url, _ in session.calls)
    assert all(not options["allow_redirects"] for _, options in session.calls)


def test_page_limit_is_not_silent_success():
    client = GitHubAPIClient(token="", session=Session([response([entry(1)], next_page=True)]))
    assert not client.get_stargazer_timestamps("a", "b", max_pages=1).pagination_complete


@pytest.mark.parametrize("status", [302, 403, 404, 422, 429, 500])
def test_http_failures_do_not_become_empty_histories(status):
    client = GitHubAPIClient(token="", session=Session([response([], status=status)]))
    with pytest.raises(GitHubRequestError, match=f"HTTP {status}"):
        client.get_stargazer_timestamps("a", "b", max_pages=2)


def test_malformed_and_duplicate_records_fail():
    for records in ([{"user": {"id": 1}}], [entry(1), entry(1)]):
        client = GitHubAPIClient(token="", session=Session([response(records)]))
        with pytest.raises(GitHubRequestError, match="Malformed"):
            client.get_stargazer_timestamps("a", "b", max_pages=1)


def test_exception_message_cannot_expose_token_or_response_body():
    def fail(*args, **kwargs):
        raise requests.ConnectionError("test-token")

    session = Session([])
    session.get = fail
    client = GitHubAPIClient(token="test-token", session=session)
    with pytest.raises(GitHubRequestError) as error:
        client.get_stargazer_timestamps("a", "b", max_pages=1)
    assert "test-token" not in str(error.value)
    assert error.value.__suppress_context__


def test_explicit_env_file_loading_does_not_mutate_environment(monkeypatch, tmp_path):
    import os

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    path = tmp_path / ".env"
    path.write_text("GITHUB_TOKEN=test-token\n", encoding="utf-8")
    session = Session([])
    GitHubAPIClient.from_env(path, session=session)
    assert session.headers["Authorization"] == "Bearer test-token"
    assert "GITHUB_TOKEN" not in os.environ


def test_empty_complete_history_retains_all_zero_repository_and_metadata():
    manifest = pd.DataFrame(
        {"repo_name": ["a/b"], "observation_start": ["2022-01-01"], "coverage_complete": [True]}
    )
    history = StarHistory((), True, "2022-01-10T00:00:00Z")
    client = SimpleNamespace(get_stargazer_timestamps=lambda *args, **kwargs: history)
    daily, metadata, raw = ingest_daily_stars(
        client, manifest, observation_end="2022-01-07", max_pages=1
    )
    assert daily.empty
    assert metadata.source.tolist() == ["rest_surviving_stargazers"]
    assert raw == {"a/b": []}
    client.get_stargazer_timestamps = lambda *args, **kwargs: StarHistory(
        (), False, history.retrieved_at
    )
    with pytest.raises(ValueError, match="Incomplete"):
        ingest_daily_stars(client, manifest, observation_end="2022-01-07", max_pages=1)

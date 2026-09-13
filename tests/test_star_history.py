import json

import pandas as pd
import pytest
import requests

from pulsegraph.data.history_validation import compare_validation, fetch_validation
from pulsegraph.data.star_history import HistoryError, StarHistoryClient, decode_weeks, read_capture
from pulsegraph.provenance import atomic_json, sha256_bytes


class Response:
    def __init__(self, value, *, status=200, next_page=False, headers=None):
        self.content = json.dumps(value).encode()
        self.status_code = status
        self.links = {"next": {"url": "unused"}} if next_page else {}
        self.headers = headers or {}


class Session:
    def __init__(self, responses):
        self.headers, self.responses, self.calls = {}, iter(responses), []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def weeks(n=35):
    return [
        {
            "week": int((pd.Timestamp("2024-09-01", tz="UTC") - pd.Timedelta(weeks=i)).timestamp()),
            "total": 7,
            "days": [1] * 7,
        }
        for i in range(n)
    ]


def metadata(values):
    return {
        "id": 12,
        "full_name": "a/new",
        "private": False,
        "created_at": pd.Timestamp(values[-1]["week"] + 86400, unit="s", tz="UTC").isoformat(),
    }


def test_complete_pagination_raw_hashes_and_zero_weeks(tmp_path):
    values = weeks()
    values[2].update(total=0, days=[0] * 7)
    session = Session(
        [Response(metadata(values)), Response(values[:30], next_page=True), Response(values[30:])]
    )
    client = StarHistoryClient("SECRET", session=session)
    result = client.fetch("a/old", tmp_path / "capture", observation_end="2024-09-03")
    restored, daily = read_capture(tmp_path / "capture")
    assert result == restored
    assert result["complete"] and result["n_pages"] == 2
    assert len(result["responses"]) == 3
    assert session.calls[1][0].endswith("/a/new/stargazers/history")
    assert session.calls[2][1]["params"]["page"] == 2
    assert result["timezone_status"] == "unverified_api_day_boundaries"
    assert (daily.stars == 0).sum() == 7
    assert not result["nominal_missing_days"]
    assert "SECRET" not in (tmp_path / "capture/capture.json").read_text()
    (tmp_path / "capture/history_001.json").write_text("[]")
    with pytest.raises(HistoryError, match="hash"):
        read_capture(tmp_path / "capture")


@pytest.mark.parametrize("change", ["duplicate", "gap", "order", "negative", "total", "bool"])
def test_reject_bad_weeks(change):
    data = weeks(3)
    if change == "duplicate":
        data.append(data[-1])
    elif change == "gap":
        data.pop(1)
    elif change == "order":
        data.reverse()
    elif change == "negative":
        data[0]["days"][0] = -1
    elif change == "total":
        data[0]["total"] = 8
    else:
        data[0]["days"][0] = True
    with pytest.raises(HistoryError):
        decode_weeks(data)


def test_incomplete_birth_coverage_and_new_validation_repo_rejected(tmp_path):
    values = weeks(3)
    info = metadata(values) | {"created_at": "2020-01-01T00:00:00Z"}
    client = StarHistoryClient(session=Session([Response(info), Response(values)]))
    with pytest.raises(HistoryError, match="coverage"):
        client.fetch("a/b", tmp_path / "short", observation_end="2024-09-03")
    assert not json.loads((tmp_path / "short/capture.json").read_text())["complete"]
    client = StarHistoryClient(session=Session([Response(metadata(values))]))
    with pytest.raises(HistoryError, match="pre_2023"):
        client.fetch(
            "a/b", tmp_path / "young", observation_end="2024-09-03", created_before="2023-01-01"
        )


def test_safe_redirect_retry_and_sanitized_failures(tmp_path):
    values = weeks(3)
    sleeps = []
    session = Session(
        [
            Response(
                {}, status=301, headers={"Location": "https://api.github.com/repositories/12"}
            ),
            Response(metadata(values)),
            Response({}, status=429, headers={"Retry-After": "0"}),
            Response(values),
        ]
    )
    client = StarHistoryClient(session=session, sleep=sleeps.append)
    client.fetch("a/b", tmp_path / "ok", observation_end="2024-09-03")
    assert sleeps == [0]
    session = Session(
        [Response({}, status=301, headers={"Location": "https://evil.example/repos/a/b"})]
    )
    with pytest.raises(HistoryError, match="unsafe_redirect"):
        StarHistoryClient("TOKEN", session=session).fetch(
            "a/b", tmp_path / "bad", observation_end="2024-09-03"
        )
    assert len(session.calls) == 1
    session = Session([requests.RequestException("TOKEN secret response")])
    with pytest.raises(HistoryError, match="transport_failure") as error:
        StarHistoryClient(session=session, attempts=1).fetch(
            "a/b", tmp_path / "error", observation_end="2024-09-03"
        )
    assert "TOKEN" not in str(error.value)
    assert "TOKEN" not in (tmp_path / "error/capture.json").read_text()


def test_maximum_pagination_does_not_succeed(tmp_path):
    values = weeks(3000)
    replies = [Response(metadata(values))] + [
        Response(values[i : i + 30], next_page=True) for i in range(0, 3000, 30)
    ]
    with pytest.raises(HistoryError, match="pagination_limit"):
        StarHistoryClient(session=Session(replies)).fetch(
            "a/b", tmp_path / "cap", observation_end="2024-09-03"
        )


@pytest.mark.parametrize("fail_one", [False, True])
def test_validation_resume_and_full_daily_comparison(tmp_path, fail_one):
    selection = tmp_path / "selection.json"
    atomic_json(selection, {"repositories": [{"repo_name": f"a/r{i}"} for i in range(20)]})

    class FakeClient:
        calls = 0
        fail = fail_one

        def fetch(self, name, path, **kwargs):
            self.calls += 1
            assert kwargs["created_before"] == "2023-01-01"
            path.mkdir(parents=True)
            repo_id = int(name.split("r")[-1])
            if self.fail and repo_id == 19:
                atomic_json(path / "capture.json", {"complete": False, "error": "http_404"})
                raise HistoryError("http_404")
            pd.DataFrame(
                {
                    "repo_id": repo_id,
                    "repo_name": name,
                    "nominal_date": pd.date_range("2024-01-01", "2024-12-31").strftime("%Y-%m-%d"),
                    "stars": 2,
                }
            ).to_csv(path / "daily_nominal.csv", index=False)
            result = {
                "repo_id": repo_id,
                "repo_name": name,
                "complete": True,
                "created_at": "2020-01-01T00:00:00Z",
                "responses": [],
                "week_utc_seconds": [0],
                "week_utc_weekdays": ["Sunday"],
                "nominal_missing_days": [],
                "nominal_duplicate_days": 0,
                "daily_sha256": sha256_bytes((path / "daily_nominal.csv").read_bytes()),
            }
            atomic_json(path / "capture.json", result)
            return result

    client = FakeClient()
    capture = tmp_path / "validation"
    n_complete = 19 if fail_one else 20
    first = fetch_validation(client, selection, capture)
    assert first["n_complete"] == n_complete and first["n_attempted"] == 20
    report = fetch_validation(client, selection, capture)
    assert client.calls == (21 if fail_one else 20)
    assert report["n_failed"] == int(fail_one)
    assert report["n_failures"] == (2 if fail_one else 0)
    archive = tmp_path / "archive.csv"
    pd.DataFrame(
        [
            {"repo_id": i, "event_date": str(d.date()), "watch_events": 1}
            for i in range(20)
            for d in pd.date_range("2024-01-01", "2024-12-31")
        ]
    ).to_csv(archive, index=False)
    summary = compare_validation(capture, archive, tmp_path / "comparison")
    assert summary.api_total.tolist() == [732] * n_complete
    assert summary.mean_absolute_difference.tolist() == [1] * n_complete
    comparison = json.loads((tmp_path / "comparison/comparison.json").read_text())
    assert comparison["n_rows"] == n_complete * 366
    assert comparison["n_attempted"] == 20
    assert comparison["n_complete"] == n_complete
    assert comparison["n_failed"] == int(fail_one)
    assert comparison["failures"] == report["failures"]
    assert comparison["n_archive_repositories_excluded"] == int(fail_one)
    pd.read_csv(archive).iloc[1:].to_csv(archive, index=False)
    with pytest.raises(ValueError, match="complete"):
        compare_validation(capture, archive, tmp_path / "missing")
    if fail_one:
        client.fail = False
        resumed = fetch_validation(client, selection, capture)
        assert resumed["n_complete"] == 20 and resumed["n_failed"] == 0
        assert resumed["n_failures"] == 2
        assert resumed["failures"] == report["failures"]

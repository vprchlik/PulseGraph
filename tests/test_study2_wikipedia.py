import pytest

from pulsegraph.study2.constants import CONTEXT_END, CONTEXT_START
from pulsegraph.study2.ingestion import SourceFailure
from pulsegraph.study2.wikipedia import WikipediaSource


class Client:
    evidence = [{"fixture": True}]
    moved = False
    calls = []

    def get(self, url, params=None):
        self.calls.append((url, params))
        if params and params.get("list") == "allpages":
            return {"query": {"allpages": [{"pageid": 17, "title": "A/B"}]}}
        if params and params.get("prop") == "revisions|info":
            assert params["pageids"] == "17" and "generator" not in params
            return {
                "query": {
                    "pages": [
                        dict(
                            pageid=17,
                            ns=0,
                            title="A/B",
                            revisions=[{"timestamp": "2020-01-01T00:00:00Z"}],
                        )
                    ]
                }
            }
        if params and params.get("prop") == "info":
            return {"query": {"pages": [dict(pageid=17, ns=0, title="A/B")]}}
        if params and params.get("list") == "logevents":
            events = (
                [dict(title="Previous", params={"target_title": "A/B"})]
                if self.moved and params["letype"] == "move"
                else []
            )
            return {"query": {"logevents": events}}
        assert "/user/A%2FB/daily/2025090100/2026060200" in url
        return {
            "items": [
                dict(
                    project="en.wikipedia",
                    article="A/B",
                    access="all-access",
                    agent="user",
                    granularity="daily",
                    timestamp="2025090100",
                    views=0,
                )
            ]
        }


def test_wikipedia_inventory_and_measure(tmp_path):
    source = WikipediaSource(Client())
    inventory = source.inventory(tmp_path / "inventory.json")
    row = inventory["entries"][0]
    assert row["series_id"] == "17" and row["overlap"] == "known_training_source_overlap"
    assert source.context(row, CONTEXT_START, CONTEXT_END) == [{"date": CONTEXT_START, "count": 0}]
    with pytest.raises(ValueError, match="target"):
        source.context(row, CONTEXT_START, "2026-08-31")


def test_ambiguous_history_excludes_before_pageviews_are_requested():
    client = Client()
    client.calls = []
    client.moved = True
    source = WikipediaSource(client)
    with pytest.raises(SourceFailure, match="unresolved_move"):
        source.context(dict(series_id="17", title="A/B"), CONTEXT_START, CONTEXT_END)
    assert not any("pageviews" in url for url, _ in client.calls)


def test_api_warnings_are_not_silent_parameter_fallbacks():
    class Unsupported:
        def get(self, *args):
            return {"warnings": {"query": "unsupported"}}

    with pytest.raises(SourceFailure, match="unsupported"):
        WikipediaSource(Unsupported()).query({})

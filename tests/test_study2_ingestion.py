import numpy as np
import pandas as pd
import pytest

from pulsegraph.provenance import atomic_json
from pulsegraph.study2.constants import CONTEXT_END, CONTEXT_START
from pulsegraph.study2.ingestion import (
    NpmSource,
    RequestBudget,
    SourceFailure,
    build_panel,
    context_days,
    freeze_inventory,
    hash_key,
)


def test_hash_encoding_is_registered():
    from hashlib import sha256

    assert (
        hash_key("npm", "selection", "@scope/café")
        == sha256('[20260914,"npm","selection","@scope/café"]'.encode()).hexdigest()
    )


def test_panel_strata_leakage_and_shortage(tmp_path):
    inventory = tmp_path / "inventory.json"
    freeze_inventory(
        "npm",
        [dict(series_id=str(i), created_at="2020-01-01T00:00:00Z") for i in range(6)],
        [{"fixture": True}],
        inventory,
    )
    dates = pd.date_range(CONTEXT_START, "2026-12-31")
    base = {str(i): pd.DataFrame(dict(date=dates, count=np.ones(len(dates)))) for i in range(6)}
    for i in range(6):
        mask = base[str(i)].date.between("2026-03-05", CONTEXT_END)
        values = np.ones(90)
        values[: (0, 45, 81)[i % 3]] = 0
        base[str(i)].loc[mask, "count"] = values
    seen = []

    def fetch(row, start, end):
        seen.append((start, end))
        return base[row["series_id"]].to_dict("records")

    first = build_panel(inventory, fetch, tmp_path / "first")
    for frame in base.values():
        future = frame.date > CONTEXT_END
        frame.loc[future, "count"] = np.nan
        frame.sort_values("date", ascending=False, inplace=True)
    second = build_panel(inventory, fetch, tmp_path / "second")
    assert first["series"] == second["series"]
    assert all(pair == (CONTEXT_START, CONTEXT_END) for pair in seen)
    assert all(
        s["achieved"] == 2 and s["unfilled"] == 98 for s in first["report"]["strata"].values()
    )
    assert first["report"]["target_values_opened"] is False


def test_incomplete_and_budget_are_distinct(tmp_path):
    inventory = tmp_path / "inventory.json"
    freeze_inventory(
        "npm",
        [dict(series_id="a", created_at="2020-01-01T00:00:00Z")],
        [{"fixture": True}],
        inventory,
    )

    def budget(*args):
        raise RequestBudget("stop")

    with pytest.raises(RequestBudget):
        build_panel(inventory, budget, tmp_path / "budget")
    result = build_panel(inventory, lambda *args: [], tmp_path / "missing")
    assert result["report"]["skipped"][0]["reason"] == "missing_context_day"
    with pytest.raises(SourceFailure):
        context_days([{"date": CONTEXT_START, "count": 0}] * 2)


def test_npm_scope_and_bounds():
    class Client:
        def get(self, url):
            assert url.endswith("%40scope%2Fa")
            assert "2025-09-01:2026-06-02" in url
            return dict(package="@scope/a", start=CONTEXT_START, end=CONTEXT_END, downloads=[])

    source = NpmSource(Client())
    assert source.context({"series_id": "@scope/a"}, CONTEXT_START, CONTEXT_END) == []
    with pytest.raises(ValueError, match="target"):
        source.context({}, CONTEXT_START, "2026-08-31")


def test_partial_inventory_cannot_select(tmp_path):
    p = tmp_path / "partial.json"
    atomic_json(p, dict(acquired_at="2026-09-14T00:00:00Z", complete=False))
    with pytest.raises(SourceFailure, match="incomplete"):
        build_panel(p, None, tmp_path / "out")


def test_npm_pagination_uses_supported_cursor_and_retains_scopes(tmp_path):
    class Client:
        evidence = [{"fixture": True}]

        def get(self, url, params=None):
            if params is not None:
                assert "skip" not in params and "include_docs" not in params
                cursor = params.get("startkey")
                ids = ["@scope/a", "b"] if cursor is None else ["b"]
                return {"rows": [{"id": key} for key in ids]}
            name = "@scope/a" if url.endswith("%40scope%2Fa") else "b"
            return dict(name=name, time={"created": "2020-01-01T00:00:00Z"})

    result = NpmSource(Client()).inventory(tmp_path / "inventory.json")
    assert [r["series_id"] for r in result["entries"]] == ["@scope/a", "b"]


def test_nyc_bulk_context_checks_exhaustion_and_zero_days():
    from pulsegraph.study2.ingestion import NYCSource

    class Client:
        def get(self, url, params):
            assert "2026-06-03" in params["$where"]
            if "as keys" in params["$select"]:
                return [{"rows": "2", "keys": "2"}]
            if "created_date >= '2026-03-01" not in params["$where"]:
                return []
            return [
                dict(
                    complaint_type="Noise",
                    community_board="01 BRONX",
                    day="2026-03-05T00:00:00.000",
                    n="2",
                )
            ]

    source = NYCSource(Client())
    rows = source.context(dict(problem="Noise", board="01 BRONX"), CONTEXT_START, CONTEXT_END)
    assert len(rows) == 275 and sum(r["count"] for r in rows) == 2
    empty = source.context(dict(problem="Other", board="01 BRONX"), CONTEXT_START, CONTEXT_END)
    assert sum(r["count"] for r in empty) == 0

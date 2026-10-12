"""English Wikipedia metadata and bounded user pageviews, explicitly overlap-labelled.

Current titles are used only after auditing move/delete/merge/import logs. A title
whose history cannot be reconciled is excluded before pageview values are requested.
"""

import json
from urllib.parse import quote

import pandas as pd

from pulsegraph.study2.constants import CONTEXT_END, CONTEXT_START
from pulsegraph.study2.holdout import utc_now
from pulsegraph.study2.ingestion import SourceFailure, freeze_inventory


class WikipediaSource:
    API = "https://en.wikipedia.org/w/api.php"

    def __init__(self, client):
        self.client = client
        self._moves = None

    def query(self, params):
        result = self.client.get(
            self.API, {"action": "query", "format": "json", "formatversion": 2, **params}
        )
        if "error" in result or "warnings" in result:
            raise SourceFailure("wikipedia_api_error_or_unsupported_parameter")
        return result

    def pages(self, params, member):
        continuation, seen = {}, set()
        while True:
            result = self.query({**params, **continuation})
            yield from result.get("query", {}).get(member, [])
            if "continue" not in result:
                break
            continuation = result["continue"]
            key = json.dumps(continuation, sort_keys=True)
            if key in seen:
                raise SourceFailure("wikipedia_pagination_not_advancing")
            seen.add(key)

    def inventory(self, output):
        entries = []
        for page in self.pages(
            dict(list="allpages", apnamespace=0, apfilterredir="nonredirects", aplimit=500),
            "allpages",
        ):
            # rvdir=newer is supported for one page only, never a multi-page generator.
            result = self.query(
                dict(
                    prop="revisions|info",
                    pageids=str(page["pageid"]),
                    rvprop="timestamp",
                    rvlimit=1,
                    rvdir="newer",
                )
            )
            records = result.get("query", {}).get("pages", [])
            if len(records) != 1:
                raise SourceFailure("wikipedia_metadata_identity_missing")
            item = records[0]
            if item.get("pageid") != page["pageid"] or item.get("ns") != 0:
                raise SourceFailure("wikipedia_page_identity_changed")
            revision = item.get("revisions", [])
            entries.append(
                dict(
                    series_id=str(page["pageid"]),
                    title=item["title"],
                    created_at=revision[0]["timestamp"] if revision else None,
                    excluded_reason="redirect_at_inventory" if "redirect" in item else None,
                    overlap="known_training_source_overlap",
                )
            )
        return freeze_inventory("wikipedia", entries, self.client.evidence, output)

    def _audit_title(self, row):
        current = self.query(dict(prop="info", pageids=row["series_id"]))
        pages = current.get("query", {}).get("pages", [])
        if (
            len(pages) != 1
            or str(pages[0].get("pageid")) != row["series_id"]
            or pages[0].get("title") != row["title"]
            or "redirect" in pages[0]
            or "missing" in pages[0]
        ):
            raise SourceFailure("wikipedia_identity_reconciliation_failed")
        end = utc_now().isoformat()
        common = dict(
            list="logevents",
            leprop="ids|title|type|timestamp|details",
            lelimit=500,
            ledir="newer",
            lestart=CONTEXT_START + "T00:00:00Z",
            leend=end,
        )
        if self._moves is None:
            self._moves = set()
            for event in self.pages({**common, "letype": "move"}, "logevents"):
                if "actionhidden" in event or "title" not in event:
                    raise SourceFailure("suppressed_move_history")
                self._moves.add(event["title"])
                target = event.get("params", {}).get("target_title")
                if not target:
                    raise SourceFailure("move_target_missing")
                self._moves.add(target)
        if row["title"] in self._moves:
            raise SourceFailure("unresolved_move_or_overlapping_title_alias")
        for event_type in ("delete", "merge", "import"):
            events = list(
                self.pages({**common, "letype": event_type, "letitle": row["title"]}, "logevents")
            )
            if events:
                raise SourceFailure("unresolved_title_exposure_history")

    def context(self, row, start, end):
        if start != CONTEXT_START or end != CONTEXT_END:
            raise ValueError("Selection endpoint cannot access target days")
        self._audit_title(row)
        title = quote(row["title"].replace(" ", "_"), safe="")
        begin, stop = start.replace("-", "") + "00", end.replace("-", "") + "00"
        result = self.client.get(
            "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
            f"en.wikipedia/all-access/user/{title}/daily/{begin}/{stop}"
        )
        rows = []
        for item in result.get("items", []):
            if (
                item.get("project") != "en.wikipedia"
                or item.get("access") != "all-access"
                or item.get("agent") != "user"
                or item.get("granularity") != "daily"
                or item.get("article") != row["title"].replace(" ", "_")
            ):
                raise SourceFailure("pageview_identity_or_measure_mismatch")
            stamp = str(item["timestamp"])
            if len(stamp) != 10 or not stamp.endswith("00"):
                raise SourceFailure("pageview_nonmidnight_label")
            day = pd.to_datetime(stamp[:8], format="%Y%m%d").date().isoformat()
            if not start <= day <= end:
                raise SourceFailure("pageview_outside_requested_context")
            rows.append(dict(date=day, count=item["views"]))
        # Missing records remain missing. build_panel rejects them, never invents zeros.
        return rows

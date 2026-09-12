"""Convert per-star timestamps to daily surviving-star counts on supplied intervals."""

import pandas as pd

from pulsegraph.data.github_api import GitHubAPIClient
from pulsegraph.data.loader import build_dataset_for_forecasting
from pulsegraph.validation import utc_day


def aggregate_star_timestamps(histories: dict[str, list[str]], *, observation_end) -> pd.DataFrame:
    end = utc_day(observation_end)
    rows = []
    for repo_name, timestamps in sorted(histories.items()):
        parsed = []
        for stamp in timestamps:
            day = pd.Timestamp(stamp)
            if pd.isna(day) or day.tzinfo is None:
                raise ValueError("Star timestamps must include a timezone and be nonmissing")
            parsed.append(day.tz_convert("UTC").tz_localize(None).normalize())
        daily = pd.Series(parsed, dtype="datetime64[ns]").value_counts().sort_index()
        rows.extend(
            {"repo_name": repo_name, "event_date": day, "stars": int(count)}
            for day, count in daily.items()
            if day <= end
        )
    return pd.DataFrame(rows, columns=["repo_name", "event_date", "stars"])


def ingest_daily_stars(
    client: GitHubAPIClient,
    manifest: pd.DataFrame,
    *,
    observation_end,
    max_pages: int,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Supplemental ingestion; fail on incomplete pages instead of manufacturing zeros.

    Returns daily rows, retrieval metadata and raw timestamps for deliberate
    storage by the caller. The manifest must describe the observation interval.
    No data or credentials are written by this function.
    """
    # Validate the manifest before any API request, including the all-zero case.
    empty = pd.DataFrame(columns=["repo_name", "event_date", "stars"])
    build_dataset_for_forecasting(empty, manifest, observation_end=observation_end)
    end = utc_day(observation_end)
    histories, metadata = {}, []
    for repo_name in sorted(manifest.repo_name):
        parts = repo_name.split("/")
        if len(parts) != 2:
            raise ValueError("Manifest repositories must use owner/name")
        history = client.get_stargazer_timestamps(*parts, max_pages=max_pages)
        if not history.pagination_complete:
            raise ValueError(f"Incomplete stargazer pagination for {repo_name}")
        if (
            end
            >= pd.Timestamp(history.retrieved_at).tz_convert("UTC").tz_localize(None).normalize()
        ):
            raise ValueError("Observation endpoint must be a completed UTC day before retrieval")
        histories[repo_name] = list(history.timestamps)
        metadata.append(
            {
                "repo_name": repo_name,
                "source": history.source,
                "retrieved_at": history.retrieved_at,
                "pagination_complete": True,
                "observation_end": end.date().isoformat(),
                "n_stars_returned": len(history.timestamps),
            }
        )
    daily = aggregate_star_timestamps(histories, observation_end=end)
    build_dataset_for_forecasting(daily, manifest, observation_end=end)
    return daily, pd.DataFrame(metadata), histories

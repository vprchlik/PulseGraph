"""Freeze seeded frame orders and walk complete, still-public histories without score selection."""

import numpy as np
import pandas as pd

from pulsegraph.random import validate_seed

STRATA = ("20-99", "100-999", "1000+")


def freeze_frame_order(frame, *, seed=20260913):
    frame = frame.copy()
    if not {"repo_id", "repo_name", "creation_date", "day90_stars"}.issubset(frame):
        raise ValueError("Incomplete eligible frame")
    if frame.empty or frame.repo_id.duplicated().any() or frame.isna().any().any():
        raise ValueError("Empty, duplicate or missing frame values")
    birth = pd.to_datetime(frame.creation_date, errors="raise")
    counts = frame.day90_stars
    if (
        not birth.between("2023-01-01", "2025-02-21").all()
        or (counts < 20).any()
        or (counts % 1 != 0).any()
    ):
        raise ValueError("Frame violates registered creation/eligibility bounds")
    expected = np.where(counts < 100, STRATA[0], np.where(counts < 1000, STRATA[1], STRATA[2]))
    if "sampling_stratum" in frame and not np.array_equal(frame.sampling_stratum, expected):
        raise ValueError("Sampling stratum disagrees with day-90 evidence")
    frame["sampling_stratum"] = expected
    rng = np.random.default_rng(validate_seed(seed))
    blocks = []
    for stratum in STRATA:
        block = frame[frame.sampling_stratum.eq(stratum)].sort_values("repo_id").copy()
        block = block.iloc[rng.permutation(len(block))]
        block["selection_rank"] = np.arange(1, len(block) + 1)
        block["selection_seed"] = seed
        blocks.append(block)
    return pd.concat(blocks, ignore_index=True)


def walk_frame(ordered_frame, retrieve, *, per_stratum=100):
    """retrieve(row) returns a checked capture or raises HistoryError; never receives scores."""
    from pulsegraph.data.star_history import HistoryError

    accepted, skipped, sizes = [], [], []
    for stratum in STRATA:
        block = ordered_frame[ordered_frame.sampling_stratum.eq(stratum)].sort_values(
            "selection_rank"
        )
        n_accepted, n_skipped = 0, 0
        for row in block.to_dict("records"):
            if n_accepted == per_stratum:
                break
            try:
                capture = retrieve(row)
                if not capture.get("complete") or capture.get("repo_id") != row["repo_id"]:
                    raise HistoryError("incomplete_or_mismatched_history")
            except HistoryError as error:
                skipped.append({**row, "reason": str(error)})
                n_skipped += 1
                continue
            accepted.append({**row, "fetched_repo_name": capture["repo_name"]})
            n_accepted += 1
        sizes.append(
            {
                "sampling_stratum": stratum,
                "frame_size": len(block),
                "sample_size": n_accepted,
                "skip_count": n_skipped,
            }
        )
    return {
        "accepted": accepted,
        "skipped": skipped,
        "strata": sizes,
        "population": "still_public_at_fetch_time_with_complete_history",
    }


def validate_sampling_log(candidate_path, log, manifest):
    """Reconstruct the seeded walk and verify every acceptance/skip up to its stop."""
    order = pd.read_csv(candidate_path)
    base = order.drop(columns=["selection_rank", "selection_seed"])
    expected = freeze_frame_order(base)
    pd.testing.assert_frame_equal(order.reset_index(drop=True), expected, check_dtype=False)
    accepted, skipped = log["accepted"], log["skipped"]
    accepted_ids = {r["repo_id"] for r in accepted}
    skipped_ids = {r["repo_id"] for r in skipped}
    if (
        len(accepted_ids) != len(accepted)
        or len(skipped_ids) != len(skipped)
        or accepted_ids & skipped_ids
        or accepted_ids != set(manifest.repo_id)
        or any(not r.get("reason") for r in skipped)
    ):
        raise ValueError("Sampling log has missing, duplicate or conflicting identities")

    def replay(row):
        from pulsegraph.data.star_history import HistoryError

        if row["repo_id"] in accepted_ids:
            item = next(r for r in accepted if r["repo_id"] == row["repo_id"])
            saved = manifest[manifest.repo_id.eq(row["repo_id"])].iloc[0]
            if (
                saved.repo_name != item["fetched_repo_name"]
                or saved.day90_stars != row["day90_stars"]
                or saved.sampling_stratum != row["sampling_stratum"]
                or str(saved.creation_date) != str(row["creation_date"])
            ):
                raise ValueError("Achieved manifest differs from the frozen frame walk")
            return {"complete": True, "repo_id": row["repo_id"], "repo_name": saved.repo_name}
        if row["repo_id"] not in skipped_ids:
            raise ValueError("Unlogged candidate before the sampling stop")
        item = next(r for r in skipped if r["repo_id"] == row["repo_id"])
        raise HistoryError(item["reason"])

    replayed = walk_frame(order, replay)
    if replayed != log:
        raise ValueError("Sampling log differs from the seeded complete-history walk")


def day90_watch_counts(events, *, repo_id, creation):
    """Offline reference for the bounded SQL predicate; only WatchEvent IDs count."""
    birth = pd.Timestamp(creation)
    dates = pd.to_datetime(events.created_at, utc=True).dt.tz_localize(None).dt.normalize()
    selected = events[
        events.type.eq("WatchEvent")
        & events.repo_id.eq(repo_id)
        & dates.between(birth, birth + pd.Timedelta(days=89))
    ]
    return selected.id.nunique()

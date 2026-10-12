"""Independent Study 2 registration identity and fixed calendar."""

from datetime import datetime, timezone

from pulsegraph.evaluation.registration import MODEL_PINS

PROTOCOL_COMMIT = "df55867c982dfe2bb6e1152ec8ae93e3cd228c45"
PROTOCOL_SHA256 = "33cefd8e34fea973e6747d1ba3fe565051e215c5d1b7f6553b266c1be7a66360"
GITHUB_MANIFEST_SHA256 = "d33ffbd4a189c10a99679dcb3d2812c8bcc089b0b4c66bf927233e04d0e4fa92"
CONTEXT_START = "2025-09-01"
CONTEXT_END = "2026-06-02"
STRATA_START = "2026-03-05"
CUTOFFS = ("2026-06-03", "2026-07-03", "2026-08-02")
ENDPOINT = "2026-08-31"
FREEZE_AT = datetime(2026, 9, 28, 18, tzinfo=timezone.utc)
NPM_READY_BY = datetime(2026, 9, 26, 23, 59, 59, tzinfo=timezone.utc)
SEEDS = dict(
    selection=20260914,
    forecast=20260915,
    pit=20260916,
    bootstrap=20260917,
    synthetic=20260918,
    prospective=20260919,
)
BASELINES = (
    "local_mean_28",
    "autoets_weekly",
    "nb_local_level_28",
    "poisson_28",
    "hurdle_count_28",
    "hurdle_empirical_28",
    "dynamic_count",
)
VARIANTS = (
    tuple(
        f"{model}_{variant}" for model in MODEL_PINS for variant in ("raw", "completed", "hurdle")
    )
    + BASELINES
)
CALENDARS = {
    "github": "America/Los_Angeles",
    "npm": "UTC",
    "nyc311": "America/New_York",
    "wikipedia": "UTC",
    "pypi": "UTC",
}

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

# PROTOCOL.md, dated addition of 2026-10-16, item 7 (Study 3). The calendar, the completion, the
# count baselines and the scores are Study 2's; the seeds, the two new variants, the regime
# strata and the panel deadline are the addition's.
STUDY3_HEADING = (
    "## Study 3: the occurrence substitution by regime on a second domain"
    " — dated addition, 2026-10-16"
)
STUDY3_SEEDS = dict(selection=20261001, forecast=20261002, pit=20261003, bootstrap=20261004)
STUDY3_NEW_VARIANTS = ("hurdle_dynamic", "occurrence_model_size_count")
# The registered sixteen and, for each foundation model, the two new variants.
STUDY3_VARIANTS = VARIANTS + tuple(
    f"{model}_{variant}" for model in MODEL_PINS for variant in STUDY3_NEW_VARIANTS
)
STUDY3_STRATA = ("dense", "sparse", "very_sparse")
STUDY3_MINIMUM_SERIES = 10
STUDY3_DOMAIN = "nyc311"
STUDY3_FALLBACK_DOMAIN = "pypi"
STUDY3_PANEL_DEADLINE = datetime(2026, 10, 27, 23, 59, 59, tzinfo=timezone.utc)
# The protocol with the addition, as appended on top of 04e92c1 and recorded in both Study 3
# declaration files; the commit containing it is named by the signed readiness document.
STUDY3_PROTOCOL_SHA256 = "05c7617b0391cbcca7bccddb6ff54a763d47ba88e5d31dac4bd98621a9721b29"
STUDY3_APPENDED_ON = "04e92c19c17211891a8307041de61d32ec45a834"
STUDY3_FILES = ("study/study3/spec.json", "study/study3/regime_comparisons.json")
# The frozen NYC 311 cell inventory of 2024, captured 2026-09-14, that the specification names.
STUDY3_INVENTORY_SHA256 = "30f8e4358354e610b10ffdcf64fcad21552811c86e5cf428ecfa0b5111b82fe5"

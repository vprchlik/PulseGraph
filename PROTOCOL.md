# PulseGraph v2 protocol

This is the registered PulseGraph v2 protocol, signed off by the author on 2026-09-12. The commit hash
containing this file is the pre-registration and is recorded in README.md and the write-up. Nothing below
changes after results are seen. Any amendment is a dated addition at the end stating what changed and why.

## Question and confirmatory hypothesis

Do zero-shot foundation models improve probabilistic forecasts of daily GitHub star-history counts relative to
local_mean_28 and weekly AutoETS on a panel selected by day-90 activity and fetch-time availability? H1 predicts
lower repository-level QScore9 for the foundation models. Each model/reference/horizon cell is assessed; the paired
signed-rank null is zero-centered differences under its symmetry assumption. Negative model-minus-reference
differences favor the model. Null, adverse, mixed and imprecise results receive the same reporting. Failure to
reject is not equivalence. H2 is removed from the confirmatory family.

## Count source and validation before freeze

For every sampled repository, retrieve daily counts from creation through the common endpoint 2026-08-31 using
GET /repos/{owner}/{repo}/stargazers/history,
[released 2026-09-04](https://github.blog/changelog/2026-09-04-new-api-endpoint-provides-privacy-safe-star-history-data/).
GH Archive supplies the historical sampling frame, not the forecast counts: WatchEvent capture degraded from
mid-2025 and collapsed subsequently, affecting every evaluation window
([issue 320](https://github.com/igrigorik/gharchive.org/issues/320)). The target is the endpoint's reported
daily history; gross additions, surviving stars and net changes must not be conflated.

Before freeze, select and record about 20 validation repositories created before 2023-01-01, fetch their
histories, and compare each daily count against deduplicated GH Archive WatchEvents over 2024-01-01 through
2024-12-31. These repositories are excluded from the study by construction. Save identifiers, selection
rationale, responses, dates, comparison tables and commands; no forecasting or model tuning uses them. Include
this query in the combined cost estimate below. Record day/week timezone boundaries, alignment
discrepancies, missing days, unstars and historical revisions, distinguishing observed evidence from unknowns.
The [API documentation](https://docs.github.com/en/rest/activity/starring#get-repository-star-history) does not
guarantee UTC boundaries. Resolve and record the bin-to-calendar mapping and unstar interpretation before
freeze; do not relabel non-UTC bins as UTC or claim gross additions without evidence. If removal/revision
semantics use later information, the author must settle the measurement limitation before freeze. This
validation is a required future action, not a completed check.

## Historical frame and sample

Use GH Archive repository CreateEvents and WatchEvents, joined by stable repo ID. Creation dates b are UTC dates
in 2023-01-01 through 2025-02-21 inclusive. Require a repository creation record, with repository rather than
branch/tag creation, and deduplicate event IDs. Day 1 is b; eligibility is at least 20 WatchEvents over b through
b+89 inclusive. Count WatchEvents by event type only, without a payload action filter: the action is always
started for this type ([GitHub event-type documentation](https://docs.github.com/en/rest/using-the-rest-api/github-event-types#watchevent)).
Apply the same count rule to the 2024 validation query. The latest day 90 is 2025-05-21, before 2025-05-23.
Verify historical frame coverage; unknown creation dates or gaps are not inferred from first stars or filled
zeros. Endpoint counts do not retrospectively redefine day-90 eligibility.

The day-90 strata are 20-99, 100-999 and at least 1,000 events. Within each stratum, sort the full eligible
frame by stable ID, then place it in a seeded random order using selection seed 20260913. Freeze and save
these orders before retrieval; walk each in order and stop at 100 repositories whose histories are retrieved
completely, for up to 300 total. Record every skipped identifier and reason, preserving rename mappings. If
the frame is exhausted first, retain all complete histories without transferring unused slots between strata.
Freeze the achieved manifest before forecasting or scoring; retrieval completeness, not later activity or
forecast outcomes, determines acceptance. The achieved panel is sampled from repositories still public at
fetch time and with retrievable complete histories. Report skip counts per stratum with original frame and
achieved sample sizes. Equal repository weighting describes this panel defined by fetch-time availability, not all GitHub.

Combine the 2024 validation query and frame query into one dry-run estimate for the author's written approval,
showing each query's bytes and the total estimated bytes/cost, with a billing cap. Neither billable query runs
before approval. Save exact SQL, parameters, table bounds, estimates, job IDs and actual costs. No BigQuery
cost approval exists yet.

## Registered follow-up after the write-up

Register a separate follow-up for repositories created on or after 2026-09-13, to run after the write-up with
identical eligibility, strata, sample size, model revisions, baselines, scores, regime rules and relative window
calendar. No author-disclosed training cutoff covering the entire training corpus exists for any included model;
source-specific dates do not establish such a bound. This is an availability-bound exclusion based on the
already-existing frozen checkpoints, not a claimed author-disclosed cutoff or proof against every form of
contamination. Preserve dated checkpoint evidence from the research note of 2026-09-12, not in the tree.
The follow-up contributes no tests or results to this write-up's family. Its creation-window closing date,
future endpoint and reliable frame coverage must be registered before follow-up collection; post-2025
WatchEvent coverage cannot be assumed adequate for its eligibility counts. These follow-up details remain open
and do not change the main experiment. Its endpoint must allow every repository 90 context days plus 270 target
days, without shortening the calendar.

## Observation calendar and information boundary

The main observation endpoint E is 2026-08-31 inclusive for every repository. Decode complete endpoint
pagination through creation, sort days chronologically, truncate at E, and preserve leading, intermediate and
trailing zeros. Missing responses or unverified exposure are not zero counts. Save extraction time and the
validated day-boundary convention; calendar labels below use that convention. Use horizons 7, 30 and 90, K=3
cutoffs, maximum horizon H=90, and at least 90 context days. In chronological order, c_j = E - (j × H - 1) days
for j=3,2,1. Context ends at c_j-1; targets are c_j through c_j+h-1 inclusive.

| Cutoff | Context ends | 90-day target ends |
|---|---|---|
| 2025-12-05 | 2025-12-04 | 2026-03-04 |
| 2026-03-05 | 2026-03-04 | 2026-06-02 |
| 2026-06-03 | 2026-06-02 | 2026-08-31 |

Maximum-horizon windows partition the trailing 270 days. Shorter horizons use the same cutoffs without extra
windows. Horizons share targets and are not independent. Every model completes the same
repository/cutoff/horizon grid or the run stops. Refit baselines using context only. Foundation models use only
the repository's target history, without fine-tuning, cross-repository inputs or future covariates. OPEN before
freeze: exact runtime versions, context limits and inference settings. Record available and used context; score
scaling uses the full available context.

## Context regimes and leakage test

Regimes are descriptive, pooled for primary inference, and distinct from sampling strata. At c, R=sum over c-7
through c-1 and B=sum over c-35 through c-8. Apply the following rules in order, identically across models and
horizons:

| Label | Context-only rule |
|---|---|
| Inactive recently | Sum over c-28 through c-1 is zero. |
| Recent surge | Otherwise R >= 7 and R/7 >= 3 × max(B/28,1). |
| Other active | All remaining contexts. |

Keep constants fixed and report empty regimes. No future peak or eventual inactivity defines a label. Test every
rule and threshold boundary with the actual labeler, replacing, permuting and extending data on/after c; labels
must be unchanged and a spy must observe only dates before c. Perturb post-day-90 data to prove eligibility and
sampling strata unchanged, and assert b+89<c throughout. The existing toy-label test establishes the harness
boundary, not these rules.

## Frozen foundation models and licences

| Model | Exact repository revision | Weight licence | Package/source licence |
|---|---|---|---|
| amazon/chronos-2 | 29ec3766d36d6f73f0696f85560a422f50e8498c | Apache-2.0 | Apache-2.0 |
| google/timesfm-3.0-pytorch | 43046b85ec22d584a13f8098c2ed39c889e129c2 | TimesFM Non-Commercial License v1.0 | Apache-2.0 |
| google/timesfm-2.5-200m-pytorch | 1d952420fba87f3c6dee4f240de0f1a0fbc790e3 | Apache-2.0 | Apache-2.0 |

Sources: [Chronos weights](https://huggingface.co/amazon/chronos-2),
[Chronos code](https://github.com/amazon-science/chronos-forecasting/blob/main/LICENSE),
[TimesFM weight/code distinction](https://github.com/google-research/timesfm#license). Record licences with the
exact snapshots and runtimes; TimesFM 3 weights carry noncommercial/nonproduction restrictions. No other
foundation model is added before the write-up. Model pins do not substitute for runtime/configuration pins.

## Baselines

| Baseline | Fixed declaration | Role |
|---|---|---|
| local_mean_28 | Last-28-day mean and existing empirical context-level draws. | Primary reference |
| autoets_weekly | StatsForecast AutoETS, season_length=7, model=ZZZ, native intervals. | Primary reference |
| autoarima_weekly | StatsForecast AutoARIMA, season_length=7, native intervals. | Secondary |
| autotheta_weekly | StatsForecast AutoTheta, season_length=7, native intervals. | Secondary |
| nb_local_level_28 | Last-28-day mean, context moment dispersion, analytic deciles as below. | Secondary |
| Other local means | Lookbacks 7, 14, 56 and 90; full grid is {7,14,28,56,90}. | Secondary sensitivity |
| last_value; weekly_naive | Existing last-value and fixed-seven-day forecasts. | Secondary v1 continuity |
| naive_seasonal; linear_30; ets; lightgbm | Existing horizon-dependent naive, 30-day trend, nonseasonal Holt and lag/rolling-feature GBM. | Secondary v1 continuity |

The author approved [statsforecast==2.1.1](https://pypi.org/project/statsforecast/2.1.1/) (Apache-2.0) on 2026-09-12.
Use its defaults except declared season length, AutoETS model and recorded seeds, with native intervals and
no conformal wrapper. StatsForecast excludes multiplicative error and seasonality whenever context contains a
zero; a series with no zeros may select multiplicative components ([pinned AutoETS source](https://github.com/Nixtla/statsforecast/blob/v2.1.1/python/statsforecast/ets.py)).
Model selection uses context only; save the selected specification and parameters per fit. Native central
coverage levels 20%, 40%, 60%, 80% supply deciles 0.1-0.4 and 0.6-0.9. For these models' Gaussian predictive
distributions, the median is the point forecast; verify this and the decile mapping in the pre-freeze smoke
test. There are 15 baseline variants. No PyBATS, Croston, TSB or new GBM is included. Retained v1 residual
uncertainty and LightGBM's deterministic forecast path remain disclosed limitations. Fit failures do not
activate a new fallback.

For nb_local_level_28, mu is the last-28-day mean; m and s2 are the mean and unbiased variance of the full
context. Set alpha=max((s2-m)/(m × m),0) when m>0, else alpha=0. Predict NB with size r=1/alpha and probability
p=r/(r+mu), so variance is mu+alpha × mu × mu. At alpha=0 use the Poisson limit; at mu=0 use a point mass at
zero. Analytic inverse-CDF deciles are constant over the horizon. Refit at each cutoff; this is a local-level
count distribution, not a fitted latent state-space process. No residual calibration or extra model variant is
added.

## Scores and descriptive analyses

Primary QScore9 = 2 × mean_pinball_loss = 2/(9 × h) times the summed pinball losses over all target days and
deciles {0.1,0.2,...,0.9}; pinball(e,tau)=max(tau × e,(tau-1) × e). It is defined for all-zero targets and is a
mean decile quantile score, not full CRPS. Add and verify this derived field without changing the existing loss
formula. Use native/analytic deciles or NumPy linear empirical quantiles from 200 genuine IID marginal draws per
target day for sampled baselines. Clip negative forecasts to zero and repair crossings by cumulative maxima,
recording both changes. Interpolate only within supported levels; neither TimesFM receives invented 95% tails.

The point metric in the write-up is MASE of the median: MAE divided by the mean absolute seven-day difference in
available context. Zero/unavailable scales give NaN. RMSSE of the median and MAE remain in the artifact; RMSSE
is out of the write-up. Other secondary metrics retain pulsegraph/evaluation/metrics.py definitions: WQL=2 ×
sum(pinball)/(9 × sum(abs(targets))), NaN on zero denominator; IS80 is mean U-L+10 × max(L-y,0)+10 × max(y-U,0),
NaN if any bound/target is nonfinite. Coverage80/95 is inclusive on finite pairs, NaN if none; report valid
counts. Full CRPS is the fair IID-sample score, mean abs(s-y) minus the ordered-pair absolute-distance sum
divided by 2 × n × (n-1), averaged over days; quantile-only outputs remain unavailable. Do not place QScore9 and
full CRPS in one score column. Randomized empirical PIT is F_n(y-)+U × (F_n(y)-F_n(y-)); report ten-bin
histograms for sampled outputs, unavailable for quantile-only outputs, without IID significance claims. No MAPE.
Undefined secondary scores retain NaN and valid denominators.

Average window scores within repository/horizon, then weight repositories equally. For each primary reference,
report QScore9 mean/median difference, strict win fraction, skill=1-model/reference (undefined at reference
zero), mean/median skill, top-five share of positive gains and leave-one-out mean-gain range. Regimes, strata,
other lookbacks, continuity methods and calibration are declared secondary; none changes the primary reference
or adds a confirmatory test.

## Inference: 18 comparisons

Inference is conditional on the fixed evaluation calendar. Pair all three windows, average within
repository/horizon and set d=model-reference. Bootstrap whole repositories with replacement 20,000 times,
preserving paired windows; report mean d with pointwise 95% percentile intervals (2.5th/97.5th). Use two-sided
approximate Wilcoxon signed-rank tests across repository averages, omitting zero differences, with p=1 when all
differences are zero. Its location interpretation requires symmetry; it is not a test of mean differences. Apply
BH once at q=0.05 across these 18 QScore9 tests, with pooled regimes:

| Test | Model | Reference | Horizon |
|---|---|---|---|
| 1 | Chronos-2 | local_mean_28 | 7 |
| 2 | Chronos-2 | local_mean_28 | 30 |
| 3 | Chronos-2 | local_mean_28 | 90 |
| 4 | Chronos-2 | autoets_weekly | 7 |
| 5 | Chronos-2 | autoets_weekly | 30 |
| 6 | Chronos-2 | autoets_weekly | 90 |
| 7 | TimesFM 3 | local_mean_28 | 7 |
| 8 | TimesFM 3 | local_mean_28 | 30 |
| 9 | TimesFM 3 | local_mean_28 | 90 |
| 10 | TimesFM 3 | autoets_weekly | 7 |
| 11 | TimesFM 3 | autoets_weekly | 30 |
| 12 | TimesFM 3 | autoets_weekly | 90 |
| 13 | TimesFM 2.5 | local_mean_28 | 7 |
| 14 | TimesFM 2.5 | local_mean_28 | 30 |
| 15 | TimesFM 2.5 | local_mean_28 | 90 |
| 16 | TimesFM 2.5 | autoets_weekly | 7 |
| 17 | TimesFM 2.5 | autoets_weekly | 30 |
| 18 | TimesFM 2.5 | autoets_weekly | 90 |

The count is exactly 3 models x 2 references x 3 horizons = 18. BH has its usual dependence assumptions;
intervals are pointwise, not simultaneous. Missing pairs, nonfinite primary scores or fewer than two
repositories block inference without shrinking the family. Additional tests are post-hoc and cannot replace
these.

## Seeds, artifacts and registration

Seeds: selection 20260913; forecast/PIT root 20260912; bootstrap root 20260914. Use stable-ID ordering, NumPy's
recorded generator and SHA-256-derived forecast, PIT and comparison seeds; save roots and derived values,
including any internal native-interval simulation seeds. Hardware is not yet supplied; compute budget remains
open. Approve cloud spend and runs longer than about an hour before execution.

Every real run.json requires a non-null full protocol_commit hash pointing to the approved, committed protocol,
its file SHA-256, and the implementation commit. The real-run gate rejects missing/mismatching protocol bytes,
unpinned models, missing seeds, unresolved main-study freeze requirements or a comparison count other than 18.
Follow-up-only open dates do not block the main run. Record the protocol hash in the write-up; the code-port
commit is not registration.

Preserve run.json, results.parquet, summary.csv, signals.parquet and manifest.json, plus the validation report,
frame/coverage evidence, seeded candidate orders and skip logs, exact SQL and cost approval, endpoint requests without credentials, API
version/headers, pagination, extraction times and response hashes. Save per-window contexts/targets, identities,
bounds, labels, available/used context, quantiles/samples, repairs, metric methods and undefined counts. Save
source/package hashes, model revisions, separate weight/package licences, hardware, failures and commands;
reruns use new linked directories. Save paired tables, the 18-item comparison list, bootstrap settings, raw/BH
p-values, calibration and review outputs, figure inputs and regeneration commands in PowerShell. Integrity
checks verify hashes, bounds, seeds and the full grid and recompute scores. Commit manifests, results,
summaries, figures and aggregate data if size permits; otherwise record a durable dataset location/checksum. Raw
timestamps, weights and secrets remain excluded, and README states exactly what a fresh clone contains. After
results, protocol changes are dated, reasoned additions; extra analyses stay post-hoc. The write-up uses
v1_reference documents, tables and figures, discloses unrecomputed v1 numbers, and records artifact recovery as
deferred.

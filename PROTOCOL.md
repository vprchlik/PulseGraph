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

## Study 2 — dated addition, 2026-09-14

This addition registers a separate study of occurrence and positive size in daily count forecasts,
signed off by the author on 2026-09-14. Its registration is the commit containing this addition;
record that full commit and its protocol SHA-256 before any Study 2 evaluation. It adds the
external, synthetic and prospective comparisons specified below following Study 1's results.
It does not amend Study 1's sample, forecasts, scores, comparisons or conclusions. The preceding
18,435 bytes remain the registered Study 1 text, SHA-256
dfe2f4adf5c3fdafaa6f2716ae7c19cd4d52577497041c13b763ba06540f65c5. Study 1 is closed.
The saved-run accounting under reports/registered-2026-09-13/posthoc/ is post-hoc throughout.

Source of the specifications is the research extensions memo of 2026-09-13, not in the tree,
SHA-256 430d0f8ea2d4eb0328c8458a21e5b4b1f45d802ab154f87196d74b9c9feacc5f.
“Memo §1”, “Memo §3” and “Memo §5” identify its population/overlap, mechanism/model and
estimand/reporting sections. Memo §4 additionally supplies the prospective and birth-cohort rationale.
The author's decisions of 2026-09-14 fix the numerical design choices below; those choices are not
attributed to the memo where it supplied no unique rule. Remaining OPEN items are identified
explicitly and block their affected execution or publication until resolved in a dated addition.
Changes after registration are dated additions stating what changed and why, never edits in place.

The question is whether replacing occurrence probability while preserving a foundation model's
positive conditional distribution improves overall QScore9, and whether that positive component
improves on a fixed count hurdle. Lower zero-day loss may coexist with higher positive-day loss;
the net sign, typical-series sign and null outcomes are all reportable. This hypothesis arose after
Study 1 and is tested on separately declared data. Source: Memo §§3,5.

### Domains, frame and selection

The three domain slots are package downloads (npm, with PyPI via ClickPy as its sole operational
fallback), NYC 311 and Wikipedia. Each aims at 300 series: 100 in each context-zero-fraction stratum
[0,0.5), [0.5,0.9), [0.9,1]. All-zero contexts are eligible. This is a balanced stress-test panel,
not an estimate of natural platform prevalence. Source: Memo §§1,5.

| Domain | Series key and metadata frame | Counts and population qualification |
|---|---|---|
| npm, primary external domain | Package name including scope, from a frozen registry replication/metadata inventory; recorded creation must precede context start A. Never use popularity search or download leaders. | Official daily-range downloads, including scoped packages; downloads measure artifact requests, not human adoption. Current metadata conditions the frame on inventory-time survival. |
| PyPI via ClickPy, fallback for npm only | Normalized project name from a frozen project index or distribution metadata, with first release before A; deduplicate normalization aliases before sampling. | Bounded ClickPy daily aggregate queries with source provenance and gap checks. Do not substitute PyPIStats' short history. Current-index and historical-metadata frames have different deletion coverage and must be distinguished. |
| NYC 311, second external domain | Stable problem × community-board key enumerated from at least one request in a fixed pre-context year; freeze taxonomy and geography before sampling. | Created-date daily request counts, deduplicated by request identifier; count requests, not closures. Missing/changed geography or taxonomy is recorded, never silently reassigned. |
| Wikipedia, known training overlap | Stable page ID from namespace-zero articles in a declared language edition, created before A; freeze title/move/redirect mappings. | Daily per-article user pageviews, all-access; current inventory is a surviving-article population. Source overlap is known; exact sampled-entity overlap remains to be matched. |

These source choices follow Memo §1 and its inline references: [npm registry](https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md),
[npm download API](https://github.com/npm/registry/blob/main/docs/download-counts.md),
[PyPA download analysis](https://packaging.python.org/en/latest/guides/analyzing-pypi-package-downloads/),
[ClickPy](https://github.com/ClickHouse/clickpy),
[NYC 311 schema](https://dev.socrata.com/foundry/data.cityofnewyork.us/erm2-nwe9), and
[Wikimedia pageviews](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/concepts/page-views.html).
The memo's access claims are dated 2026-09-13; preflight verifies current schemas and quotas without
opening evaluation values. Data redistribution evidence is required before publication.

Freeze each metadata inventory at its saved UTC acquisition timestamp. Use selection seed 20260914.
Hash UTF-8 canonical JSON [seed,domain,stage,stable_key] with SHA-256, compact separators and no
ASCII escaping; sort ascending digest, then UTF-8 stable key to break ties. For npm, PyPI and
Wikipedia, stage="candidate" selects the first min(10000,N) metadata-eligible keys as a fixed
candidate pool. For NYC 311 use its entire pre-context cell frame. Inspect only A through the day
before the first cutoff for completeness, and its final 90 days for strata. Within each stratum
sort stage="selection" hashes and take the first 100 complete candidates, preserving the full order,
candidate-pool inclusion probability, frame/stratum sizes and every exclusion reason. The cap,
hash encoding and seed are accepted author choices instantiating Memo §1's nested hash sampling.

Retain min(100,N_s) complete series in each stratum with no transfer of unused slots, no larger
candidate pool and no alternative popularity filter. Report empty strata and reduced panels.
Freeze acceptance using context and source-coverage metadata before exposing target values.
A later incomplete target does not trigger replacement or deletion: stop the domain, preserve the
failure and restore the same source snapshot if possible. If complete scoring cannot be recovered,
report the component unavailable and do not silently shrink its family. No external confirmatory
inference runs on a failed or missing domain or fewer than two series. The holdout's predeclared
npm-unavailability rule is the sole permitted domain-based reduction of a comparison family.

Completeness means every required calendar day has verified exposure. Explicit zero counts remain;
missing API records are zero only when a documented and validated source contract or complete event
enumeration establishes zero events. Failures, outages, unknown creation times, unresolved aliases,
duplicate days and unverified exposure are not zero-filled. Keep leading, intermediate and trailing
zeros. Acquisition retries cannot consult scores. Source: Memo §§1,5.

OPEN source details proposed for review: npm and PyPI keep their complete reported download counts,
with no new mirror/installer filtering; PyPI names use lowercase with each run of '-', '_' or '.'
replaced by '-'. Verify the selected ClickPy table implements those count semantics. Use the
2024 calendar year, preceding A=2025-09-01, to enumerate NYC 311 cells. Use the latest captured
revision per request ID, the literal frozen problem label and recognized community-board code; exclude missing/unspecified
board codes with counts of exclusions. Use English Wikipedia, exclude redirects at inventory
freeze, and require a unique auditable title history without overlapping title aliases. Failed
identity reconciliation excludes a candidate before target exposure. These details are not settled
by the memo; exact schema fields, inventory versions and coverage/redistribution evidence remain OPEN.

Use PyPI only if npm cannot provide the bounded metadata/context extraction and verified coverage
under approved quotas within 14 calendar days from the signature date, 2026-09-14: the deadline is
2026-09-28. Decide and record the operational failure before any npm target scoring; source failure,
not unfavorable performance or an unfilled sparsity stratum, triggers substitution. PyPI occupies
the same external package slot and comparison count. No RubyGems or other replacement is permitted.
The October holdout does not substitute PyPI for npm. Source: Memo §1 and the author's choice.

### Calendar and information boundary

Use horizons 7 and 30 with one common observation endpoint E_d per domain. For K cutoffs, in
chronological order c_j=E_d-(30j-1) days for j=K,...,1. Context stops at c_j-1; the target block is
c_j through c_j+h-1. Maximum-horizon blocks do not overlap; seven-day blocks use the same origins.
No model sees another series or future covariates, and no horizon is counted as an independent
entity. Sources: Memo §§1,3,5 and Study 1's declared calendar construction.

The retrospective calendar has A=2025-09-01, E_d=2026-08-31 for every domain, and K=3.
Cutoffs are 2026-06-03, 2026-07-03 and 2026-08-02, with 275, 305 and 335 context days.
Compute selection strata on c_1-90 through c_1-1: 2026-03-05 through 2026-06-02 inclusive.
Freeze those strata for all origins; updated context-zero fractions are secondary descriptors
without resampling. Package/Wikipedia day labels are UTC; NYC 311 creation times use
America/New_York with DST. Validate these source conventions before target exposure. If a source
cannot meet the calendar, report that domain unavailable or register a dated calendar amendment
before accessing its targets. Never choose an endpoint after inspecting forecast performance.

### Models, distributions and controls

Use the same exact revisions, with their existing separate weight/package licences and batch-one
GPU contract. Sources: Memo §3 and Study 1's pins.

| Model | Frozen revision |
|---|---|
| amazon/chronos-2 | 29ec3766d36d6f73f0696f85560a422f50e8498c |
| google/timesfm-3.0-pytorch | 43046b85ec22d584a13f8098c2ed39c889e129c2 |
| google/timesfm-2.5-200m-pytorch | 1d952420fba87f3c6dee4f240de0f1a0fbc790e3 |

For each FM save raw native-decile, completed-unwrapped and hurdle-wrapped forecasts as distinct
variants. Raw outputs retain Study 1's clipping/cummax repair and no invented tails. All three
variants use the same saved base forecast; no refitting selects a successful transformation.
Completion below is a Study 2 assumption, never attributed retrospectively to Study 1. Source: Memo §3.

| Baseline/control | Specification |
|---|---|
| local_mean_28 | Study 1 implementation and 200 genuine empirical marginal draws with recorded seeds. |
| autoets_weekly | StatsForecast 2.1.1, season_length=7, native intervals and median point forecast; save selected specification and repairs per fit. |
| nb_local_level_28 | Study 1's last-28 mean, full-context moment dispersion and analytic NB/Poisson/zero limits, unchanged. |
| poisson_28 | Poisson with last-28-day mean, analytic integer quantiles and point mass at zero when the mean is zero. |
| hurdle_count_28 | Occurrence p=(n_positive+1/2)/29 from the last 28 days, constant over the horizon; positive-size rule below. |
| hurdle_empirical_28 | The same Jeffreys occurrence estimator with a positive empirical distribution, as the matched nonparametric control proposed in Memo §3; declared secondary. |
| dynamic_count | In-repository discounted Beta-Bernoulli/Gamma-Poisson hurdle, discount 0.98; equations and fallback below. |

The occurrence estimator adopts Memo §3's 28-day Jeffreys example. The main calendar has
at least 275 days of context: contexts shorter than 28 days fail that gate, rather than silently
changing the denominator. The separate birth-cohort draft must explicitly settle its shorter rule.

For the fixed count hurdles, use only positive observations in the last 28 days. For the parametric
hurdle let X=Y-1, lambda=mean(X), and G_+ be 1+Poisson(lambda); lambda=0 gives a point mass at one.
The empirical hurdle assigns equal probability to those positive observations. When fewer than
two positives exist, both count hurdles use G_+=delta_1; occurrence remains the Jeffreys estimate.
No target-based fallback or estimated epsilon is allowed. Memo §3 supplies the matched
empirical/shifted-count construction; the numerical rules are author-accepted design choices.

Complete each FM CDF using only the nine repaired native deciles q_0.1,...,q_0.9. Define Q(u) by
linear interpolation through (0,0) and those nine knots for 0<=u<=0.9. For 0.9<u<1 set
Q(u)=q_0.9+s log(0.1/(1-u)), with s=max(1,q_0.9-q_0.8). This exponential upper-quantile tail
has finite first moment. Set Y=max(0,floor(Q(U)+0.5)) for U uniform on (0,1), fixing half-up integer
mapping; define the right-continuous count CDF F(k)=P(Y<=k), including atoms from flat segments.
Compute its masses and inverse CDF analytically or by deterministic inversion, not pseudo-sampling
native tails. The lower interpolation, unit scale floor, rounding and tail are the accepted
completion choices; the memo establishes the need for completion but supplies no formula.

The completed-unwrapped control is exactly this F. Whenever F(0)<1, the FM hurdle uses its own
completed positive conditional distribution G_+(k)=[F(k)-F(0)]/[1-F(0)] for k>=1, H(0)=1-p and
H(k)=1-p+pG_+(k), with the same last-28-day Jeffreys p. Its quantile is zero for tau<=1-p;
otherwise invert G_+ at (tau-1+p)/p. Only when F(0)=1 use G_+=delta_1 and record that condition.
The FM hurdle never uses the count hurdles' fewer-than-two-positives rule; ties are therefore
not forced. Completion is shared by wrapped and completed-unwrapped variants: the wrapper changes
occurrence while retaining the completed positive law whenever it exists. Source: Memo §3.

The registered dynamic_count implementation is the in-repository discounted
Beta-Bernoulli/Gamma-Poisson hurdle. Start a_B=b_B=a_P=b_P=0.5. Before each context observation
multiply all four parameters by 0.98; update a_B+=1[y>0], b_B+=1[y=0], and on positive days
a_P+=y-1, b_P+=1. At lead l use occurrence p=a_B/(a_B+b_B), and positive size
1+NB(shape=0.98^(l-1)a_P, probability=(0.98^(l-1)b_P)/(1+0.98^(l-1)b_P)). This is the
Gamma-Poisson predictive mixture. Use analytic CDFs and quantiles; no regressors, seasonal terms
or target updates. Fewer than two positives in the last 28 context days falls back to
hurdle_count_28. These are the accepted implementation and hyperparameters, not memo-specified
constants. Per-fit numerical failures stop the run, with no opportunistic implementation switch.

### Scores and the single external-domain confirmatory family

QScore9 remains primary, with all target days and all nine deciles included. Average windows
within series/horizon, then give each series equal weight within domain. Report domains separately;
do not pool different count units into a new primary score. Secondary scaled QScore9 is
QScore9/max(1,mean(context)), scaling each window from its full allowed context before the same
averaging. This adopts Memo §5's proposed positive context scale; zero contexts remain defined.

Occurrence Brier score is (p-1[y>0])^2. For an actual integer-supported full distribution with finite
first moment, discrete CRPS=sum_{k>=0}(F(k)-1[y<=k])^2. The k=0 term equals occurrence Brier;
the other terms also depend on occurrence probability. Raw quantile-only FM forecasts have neither
an identified p nor full CDF: their Brier/CRPS/PIT fields are unavailable. Do not apply the integer
sum to AutoETS's continuous native intervals or any continuous empirical forecast unchanged.
Report availability and valid denominators. Sources: Memo §§3,5.

OPEN numerical rule proposed for full count distributions: require a certified residual bound
below 1e-8 for an infinite CRPS sum and stop on failure to achieve it by k=1000000. Do not silently
truncate or substitute fair sample CRPS. Record the bound and work per forecast. For finite-support
integer empirical laws sum through the larger of the observed count and maximum support. Randomized
PIT uses independent recorded uniforms within CDF jumps; its histograms and occurrence/interval
calibration are secondary, with no IID significance claims. Full-distribution numerical settings
must be smoke-tested before freeze. Log score is not included.

One external confirmatory family covers all three domain slots, all registered variants and both
horizons on QScore9 together. For each domain, model and horizon it includes hurdle versus own
completed, hurdle versus hurdle_count_28, and raw native deciles versus local_mean_28. There are
3 domains × 3 models × 2 horizons × 3 contrasts = 54 tests: 36 hurdle contrasts plus 18 raw-model
contrasts. packages denotes npm or its single predeclared PyPI replacement; it is never both.
The full list follows. The suffix _raw always denotes the repaired native nine deciles.

| ID | Domain | Model variant | Reference | Horizon |
|---|---|---|---|---:|
| E01 | packages | chronos2_hurdle | chronos2_completed | 7 |
| E02 | packages | chronos2_hurdle | hurdle_count_28 | 7 |
| E03 | packages | chronos2_raw | local_mean_28 | 7 |
| E04 | packages | chronos2_hurdle | chronos2_completed | 30 |
| E05 | packages | chronos2_hurdle | hurdle_count_28 | 30 |
| E06 | packages | chronos2_raw | local_mean_28 | 30 |
| E07 | packages | timesfm3_hurdle | timesfm3_completed | 7 |
| E08 | packages | timesfm3_hurdle | hurdle_count_28 | 7 |
| E09 | packages | timesfm3_raw | local_mean_28 | 7 |
| E10 | packages | timesfm3_hurdle | timesfm3_completed | 30 |
| E11 | packages | timesfm3_hurdle | hurdle_count_28 | 30 |
| E12 | packages | timesfm3_raw | local_mean_28 | 30 |
| E13 | packages | timesfm2p5_hurdle | timesfm2p5_completed | 7 |
| E14 | packages | timesfm2p5_hurdle | hurdle_count_28 | 7 |
| E15 | packages | timesfm2p5_raw | local_mean_28 | 7 |
| E16 | packages | timesfm2p5_hurdle | timesfm2p5_completed | 30 |
| E17 | packages | timesfm2p5_hurdle | hurdle_count_28 | 30 |
| E18 | packages | timesfm2p5_raw | local_mean_28 | 30 |
| E19 | nyc311 | chronos2_hurdle | chronos2_completed | 7 |
| E20 | nyc311 | chronos2_hurdle | hurdle_count_28 | 7 |
| E21 | nyc311 | chronos2_raw | local_mean_28 | 7 |
| E22 | nyc311 | chronos2_hurdle | chronos2_completed | 30 |
| E23 | nyc311 | chronos2_hurdle | hurdle_count_28 | 30 |
| E24 | nyc311 | chronos2_raw | local_mean_28 | 30 |
| E25 | nyc311 | timesfm3_hurdle | timesfm3_completed | 7 |
| E26 | nyc311 | timesfm3_hurdle | hurdle_count_28 | 7 |
| E27 | nyc311 | timesfm3_raw | local_mean_28 | 7 |
| E28 | nyc311 | timesfm3_hurdle | timesfm3_completed | 30 |
| E29 | nyc311 | timesfm3_hurdle | hurdle_count_28 | 30 |
| E30 | nyc311 | timesfm3_raw | local_mean_28 | 30 |
| E31 | nyc311 | timesfm2p5_hurdle | timesfm2p5_completed | 7 |
| E32 | nyc311 | timesfm2p5_hurdle | hurdle_count_28 | 7 |
| E33 | nyc311 | timesfm2p5_raw | local_mean_28 | 7 |
| E34 | nyc311 | timesfm2p5_hurdle | timesfm2p5_completed | 30 |
| E35 | nyc311 | timesfm2p5_hurdle | hurdle_count_28 | 30 |
| E36 | nyc311 | timesfm2p5_raw | local_mean_28 | 30 |
| E37 | wikipedia | chronos2_hurdle | chronos2_completed | 7 |
| E38 | wikipedia | chronos2_hurdle | hurdle_count_28 | 7 |
| E39 | wikipedia | chronos2_raw | local_mean_28 | 7 |
| E40 | wikipedia | chronos2_hurdle | chronos2_completed | 30 |
| E41 | wikipedia | chronos2_hurdle | hurdle_count_28 | 30 |
| E42 | wikipedia | chronos2_raw | local_mean_28 | 30 |
| E43 | wikipedia | timesfm3_hurdle | timesfm3_completed | 7 |
| E44 | wikipedia | timesfm3_hurdle | hurdle_count_28 | 7 |
| E45 | wikipedia | timesfm3_raw | local_mean_28 | 7 |
| E46 | wikipedia | timesfm3_hurdle | timesfm3_completed | 30 |
| E47 | wikipedia | timesfm3_hurdle | hurdle_count_28 | 30 |
| E48 | wikipedia | timesfm3_raw | local_mean_28 | 30 |
| E49 | wikipedia | timesfm2p5_hurdle | timesfm2p5_completed | 7 |
| E50 | wikipedia | timesfm2p5_hurdle | hurdle_count_28 | 7 |
| E51 | wikipedia | timesfm2p5_raw | local_mean_28 | 7 |
| E52 | wikipedia | timesfm2p5_hurdle | timesfm2p5_completed | 30 |
| E53 | wikipedia | timesfm2p5_hurdle | hurdle_count_28 | 30 |
| E54 | wikipedia | timesfm2p5_raw | local_mean_28 | 30 |

Commit these exact 54 tuples as the comparison JSON declaration before the gate. Apply BH once
at q=0.05 over all 54 two-sided approximate Wilcoxon signed-rank tests on series averages, omitting
zero differences and assigning p=1 if all are zero. Report mean differences with 20,000
entity-cluster bootstrap 95% percentile intervals, medians, wins/ties/losses and complete
denominators. Differences are model minus reference; signed-rank tests do not test mean improvement
and need the usual symmetry interpretation. Inference is conditional on the fixed dates. These
settings carry Study 1's discipline into Memo §5's entity-level reporting; the expanded comparison
allocation is the author's decision, not the memo's illustrative count.

Every contrast outside this list, context strata/regimes, scaled score, Brier, CRPS, PIT, skill,
concentration and zero/positive over/under accounting are declared secondary. They do not replace
the confirmatory endpoint. Report the three exact accounting parts with the full horizon
denominator, as in Memo §3 and the post-hoc Study 1 analysis, retaining undefined conditional means
when a partition is empty.

### Synthetic intervention component

Memo §3 motivates separating occurrence, positive size and persistence. The following generators,
factor levels and replicate count are the author's accepted grid, fixed before any grid outcomes
are generated or scored.

Let pi=1-z and Z_t be a stationary Markov Bernoulli chain with
P(Z_t=1|Z_(t-1)=a)=pi+rho(a-pi), initialized Z_0~Bernoulli(pi).
Independently generate X_t~Poisson(mu_positive-1) and Y_t=Z_t(1+X_t).
Use all 18 Cartesian cells z in {0.2,0.8,0.95}, mu_positive in {1,5,25}, rho in {0,0.8}.
Thus zero frequency, mean positive size and occurrence-burst persistence vary independently in
the generator; this does not identify causal mechanisms in real platforms.

| Zero probability | Positive means | Persistence values | Cells |
|---|---|---|---:|
| 0.2 | 1,5,25 | 0,0.8 | 6 |
| 0.8 | 1,5,25 | 0,0.8 | 6 |
| 0.95 | 1,5,25 | 0,0.8 | 6 |
| Total | | | 18 |

Use 30 independent replicate IDs per cell, 270 observations per series,
first context 180 days, origins at indices 180,210,240 (zero based), horizons 7,30. For each
replicate share base uniforms across its factor cells as common random numbers, with streams
separate for occurrence and size; replicates are independent. Store the full generator manifest
before execution. Apply the same models, completion and metrics as the external study.

The oracle uses known generator parameters and the last observed Z: at lead l its occurrence
probability is pi+rho^l(Z_last-pi) and its positive law is 1+Poisson(mu_positive-1). Verify CDF mass,
quantile inversion and expected pinball optimality against known distributions before model runs.
An oracle need not win every finite realized sample; that alone is not a failing sanity check.
Its score is a diagnostic and it is not a deployable competitor or an extra confirmatory contrast.

The synthetic component has its own six-test family: at horizon 30, each FM hurdle versus its
completed control and hurdle_count_28, pooling all 18 cells with equal cell weight, 3 × 2 = 6
two-sided tests and BH once at q=0.05. The full comparison list is:

| ID | Domain | Model variant | Reference | Horizon |
|---|---|---|---|---:|
| S01 | synthetic | chronos2_hurdle | chronos2_completed | 30 |
| S02 | synthetic | chronos2_hurdle | hurdle_count_28 | 30 |
| S03 | synthetic | timesfm3_hurdle | timesfm3_completed | 30 |
| S04 | synthetic | timesfm3_hurdle | hurdle_count_28 | 30 |
| S05 | synthetic | timesfm2p5_hurdle | timesfm2p5_completed | 30 |
| S06 | synthetic | timesfm2p5_hurdle | hurdle_count_28 | 30 |

Average origins within each replicate/cell, then cells within replicate; bootstrap and paired
tests use the 30 independent replicate blocks, preserving all cells together, with the external
family's test and interval settings. Seven-day scores and individual-cell results are secondary.
Do not choose cells or generators because they reproduce Study 1. Source: Memo §§3,5.

### October prospective calendar holdout

Use the unchanged frozen 300-repository GitHub manifest and the accepted npm panel. Freeze weights,
transformations, baselines, manifests, forecast arrays and hashes before the first target day.
This is a new calendar test on possibly familiar entities, not unseen-entity transfer. It does not
shorten or replace Study 1's separately registered post-2026-09-13 birth follow-up. Sources:
Memo §§1,3,5 and §4's proposed October 1–30 calendar holdout; author instruction of 2026-09-14.

Freeze at 2026-09-28 18:00 UTC. Use only data through the last fully observed calendar day
preceding the freeze, verified by each source; incomplete reporting cannot count as a completed
day. Preserve that exact context snapshot and its UTC retrieval time. Target blocks are
October 1–7 and October 1–30, 2026, using America/Los_Angeles for GitHub and UTC labels for npm.

If C_d is the last complete input day, the forecast begins at C_d+1, while scored blocks begin
October 1. Let g_d be the number of unscored bridge days from C_d+1 through September 30. Generate
g_d+30 leads once and score leads g_d+1 through g_d+7 or g_d+30. For C_d=September 27, g_d=3,
so scored leads are 4–10 and 4–33. No bridge observations can update the frozen forecasts. Save
bridge predictions and actual lead numbers; seven and thirty denote target-block length, not a
claim of zero forecast gap. Freeze compatibility and maximum lead limits before producing files.

Commit the complete prediction files and SHA-256 hashes, or an immutable artifact location plus
their hashes, before either domain's first target day. Record the actual commit, timestamp evidence,
context endpoints and forecast generation times; a late commit fails the prospective gate.
No backdating or reconstruction from October observations is allowed. Fixed settlement retrievals
start at 2026-10-15 18:00 UTC for the seven-day block and 2026-11-07 18:00 UTC for the thirty-day
block, after at least seven complete post-target calendar days in both conventions. Fetch in
frozen stable-ID order and save each response time; preserve both snapshots and revisions between
them. Use the first verified complete capture, retry incomplete retrieval at 12-hour intervals
for at most 72 hours, then report unavailable. Only the thirty-day block is confirmatory, using
the November capture. Never choose the snapshot yielding better scores.

The holdout family has 2 domains × 3 models × 3 contrasts at horizon 30 = 18 QScore9 tests:
12 hurdle contrasts and 6 raw native-decile contrasts against local_mean_28, BH once at q=0.05.
Its full comparison list is:

| ID | Domain | Model variant | Reference | Horizon |
|---|---|---|---|---:|
| H01 | github | chronos2_hurdle | chronos2_completed | 30 |
| H02 | github | chronos2_hurdle | hurdle_count_28 | 30 |
| H03 | github | chronos2_raw | local_mean_28 | 30 |
| H04 | github | timesfm3_hurdle | timesfm3_completed | 30 |
| H05 | github | timesfm3_hurdle | hurdle_count_28 | 30 |
| H06 | github | timesfm3_raw | local_mean_28 | 30 |
| H07 | github | timesfm2p5_hurdle | timesfm2p5_completed | 30 |
| H08 | github | timesfm2p5_hurdle | hurdle_count_28 | 30 |
| H09 | github | timesfm2p5_raw | local_mean_28 | 30 |
| H10 | npm | chronos2_hurdle | chronos2_completed | 30 |
| H11 | npm | chronos2_hurdle | hurdle_count_28 | 30 |
| H12 | npm | chronos2_raw | local_mean_28 | 30 |
| H13 | npm | timesfm3_hurdle | timesfm3_completed | 30 |
| H14 | npm | timesfm3_hurdle | hurdle_count_28 | 30 |
| H15 | npm | timesfm3_raw | local_mean_28 | 30 |
| H16 | npm | timesfm2p5_hurdle | timesfm2p5_completed | 30 |
| H17 | npm | timesfm2p5_hurdle | hurdle_count_28 | 30 |
| H18 | npm | timesfm2p5_raw | local_mean_28 | 30 |

Use entity pairing/bootstrap and the external family's test and reporting rules, conditional on
this single month. The seven-day endpoint and other contrasts are secondary. GitHub targets remain
surviving-star history at the declared settled retrieval, not gross additions; later unstars
remain a measurement limitation.

If npm is unavailable, report GitHub alone: no PyPI or other substitution. Before any holdout
scoring, record the operational reason and declare the reduced family as H01–H09, GitHub's nine
tests, with BH applied once over those nine. This includes npm unavailability following the external
study's switch to PyPI. It never depends on model scores or permits deletion of individual
comparisons. Preserve the unavailable npm rows as status records, outside the declared nine-test
family. If GitHub is unavailable, report the holdout unavailable; no alternative reduction is
registered.

### Contamination ledger

Keep Memo §1's three distinct categories for every domain; source-specific cutoffs are not global
training cutoffs. Exact IDs/date ranges require matching saved manifests to disclosed corpora.

| Domain/component | Known source/entity overlap | Unknown overlap | Targets after frozen checkpoint availability |
|---|---|---|---|
| npm | None established by the reviewed disclosures; package-name familiarity is not numerical-series evidence. | Training overlap remains unknown. | Retrospective blocks are mixed by model availability; no all-model temporal-clean claim. The committed October targets qualify if the prospective gate passes. |
| PyPI via ClickPy | None established by the reviewed disclosures. | Numerical training overlap remains unknown, including broader collection lineage. | No prospective PyPI substitution is registered; retrospective dates require model-specific ledger comparison. |
| NYC 311 | No exact source/entity match established in the memo. | Civic data may occur in broadly described corpora; absence of disclosure is not absence from training. | The retrospective calendar does not certify availability after all three checkpoints. |
| Wikipedia | Known source overlap for all three model families; TimesFM cards name Wikipedia through November 2023 and Chronos includes Wiki sources. | Exact sampled article/history overlap and other corpus lineage remain unresolved. | Later pageviews can be temporally new on known entities; the source-specific 2023 date is not an all-source training cutoff. |
| GitHub October panel | No numerical source/entity overlap established; the same panel was already evaluated in Study 1. | Earlier entity histories and overall training overlap remain unknown. | October outcomes are after the frozen available checkpoints and committed predictions if the gate passes; this does not establish unseen entities or remove survivor measurement. |
| Synthetic intervention | Generic generator families may be familiar; no natural-domain transfer claim. | Familiarity with these mathematical families is not measurable from the memo. | New seeded realizations are generated after frozen weights; preserve generation and registration evidence. |
| Retrospective 2024 GitHub birth draft | Prior exposure to Study 1 prefixes must be disclosed where entities overlap. | Numerical pretraining and author exposure remain unresolved. | 2024 targets do not qualify as an all-model availability-bound holdout. |

Sources retained from Memo §1: [TimesFM 2.5 card](https://huggingface.co/google/timesfm-2.5-200m-pytorch),
[TimesFM 3 card](https://huggingface.co/google/timesfm-3.0-pytorch),
[Chronos](https://arxiv.org/html/2403.07815v2), [Chronos-2](https://arxiv.org/html/2510.15821v1).
No author-disclosed complete-corpus training cutoff has been established for any included model.

### Seeds, provenance and execution gate

Seeds: selection 20260914, forecasts 20260915, PIT 20260916, bootstrap 20260917,
synthetic root 20260918, prospective root 20260919. Use canonical IDs and SHA-256-derived streams;
do not use Python's process-randomized hash. Record each root and derived stream, including any
internal library simulations. Generator/common-random-number construction must be tested for
independence across replicate IDs. Sources: Memo §§3,5 and Study 1's seed/provenance discipline.

Before each component runs, its gate requires the signed Study 2 registration commit and full
protocol file SHA-256 at that commit, immutable Study 1 protocol identity, exact implementation
commit/source hashes, package versions and model revisions, licenses, complete ordered manifest,
seeds, calendar and source semantics, completed applicable OPEN resolutions, approved extraction
costs and runtime budget, and current-implementation CPU/GPU smoke evidence. Validate the full
comparison lists as 54 external, 6 synthetic and 18 prospective, or exactly H01–H09 for the
predeclared npm-unavailable holdout. Each family has one BH correction; no result-dependent family
deletion is permitted. An unresolved family, missing seed, unpinned model, unresolved fallback or
missing registration commit blocks the relevant run.

Study 1's gate verifies that the blob PROTOCOL.md at 5f01769 hashes to its original PROTOCOL_SHA256
and that those exact bytes are a prefix of the current file. It still requires clean committed
implementation files and records the full current source hashes. Appending this separately
registered study does not invalidate or relabel saved Study 1 evidence, change its 18-comparison
declaration or authorize Study 2 through the Study 1 gate. A separate Study 2 gate must enforce
this addition's registration and comparison lists before any Study 2 real-target evaluation.

Freeze context boundaries, identities and strata before targets are revealed; perturb, permute
and extend data on/after every cutoff in leakage tests, asserting unchanged selection, labels,
scales, fitted transformations and forecasts, with observed-date spies. Test score decomposition,
CDF normalization/monotonicity, zero/Poisson limits, rounding/tail inversion, exact counterpart
controls and failed-window handling offline. Models stay resident per invocation; checkpoint whole
completed series, stop on any failed window, and record verified resumes without skipping failures.
Keep the RTX 4070 SUPER batch-one/under-8-GB VRAM discipline, GPU/driver/CUDA/PyTorch evidence and
CPU baseline timing. New paid queries, unusual dependencies and runs longer than an hour need
their own author approvals; Study 1's budget is not reused automatically.

Save lawful aggregate snapshots, source requests/versions, SQL and byte/job provenance, retrieval
and settlement times, source corrections, frame and reserve orders, exclusions, data/forecast
hashes, distribution-completion parameters, every score and undefined denominator, model failures,
paired tables, comparison JSONs, bootstrap configuration and figure inputs. Every reported number
has a regeneration command and file hash. Secrets, raw personal records and model weights stay out
of the tree; release assets have durable locations and checksums. OPEN source-redistribution checks
must precede publication. No hindsight rewriting of Study 1 or of a subsequently signed Study 2.

## Retrospective GitHub birth cohort — 2026-09-14 — census approved; forecasting OPEN

The context-only feasibility census is approved as a census. Its BigQuery query requires a
dry-run estimate and the usual written cost approval before billable execution. The forecasting
study remains separately unregistered; it is not a Study 1 reanalysis or an independent prospective
confirmation. The census uses GH Archive repository CreateEvents
from 2024-01-01 through 2024-12-31, with no WatchEvent eligibility filter. Enumerate stable IDs,
unknown/missing creation coverage, current-public checks, successful histories and failures with
reasons. Count how many births remain public with any endpoint history, distinguishing that from
complete early-day coverage, and how many had fewer than 20 gross archive WatchEvents by day 90,
including zeros. Preserve separate denominators for the full frame, checked subset, current-public
subset and retrievable/complete-history subsets. A budget-limited sample is not called a census.

Only metadata, source completeness and the specified early prefixes may inform feasibility; no
forecast losses or later activity can select entities. The day-90 tally is a descriptive census
quantity, available at day 90, not a label available at day 7 or 30. It must never filter or stratify
the early-cutoff forecasting panel. A separate table may show surviving day-90 counts, explicitly
distinguished from gross archive counts. This avoids recycling Study 1's future-dependent >=20
eligibility at earlier origins. Sources: Memo §1's frame rules, §3's information boundary, §5's
population reporting and §4's launch critique.

Proposed meaning of the cutoffs is seven or thirty completed Los Angeles calendar days beginning
on local creation day b: first forecasted dates b+7 and b+30. Forecast horizons are 7 and 30; the
30-day targets at these two origins overlap, so no independent-window claim is allowed. OPEN:
the precise early information/target snapshot exposure policy, short-context estimator denominator,
sample size and seeds, census access/quota evidence and cost approval, incomplete-history rule,
pairing/family, model minimum context support and the author's prior exposure to these trajectories. Endpoint counts
are surviving stars measured later; prefix slicing cannot reconstruct gross information available
at historical launch. Date conventions, survivor/public availability and unknown training overlap
remain explicit. The approved census does not authorize forecasting; register the latter
separately before model fitting or target scoring.

## Bounded fine-tune — spring plan — OPEN, inactive

The optional adaptation study is inactive and deferred to the spring plan. It has no October
execution condition or authorization. Development and test splits are by stable entity, with every
window of an entity in exactly one split and no development feedback from test scores. Choose one of the three pinned
foundation models before opening its untouched test outcomes; compare adapted and original weights
on identical windows. This is adaptation, not zero-shot forecasting. Sources: Memo §§3,5 on
development separation and the memo's fine-tuning option; the spring deferral is the author's.

OPEN: which model/domain, newly held-out entities not already scored by the external study, split
fractions/hash seeds, context and target calendars, eligible adaptation layers, optimizer, learning
rate, update/token/GPU-hour and VRAM caps, checkpoint-selection criterion restricted to development,
number of attempted configurations, exact test family and failure policy. No test set can consist
of entities whose Study 2 outcomes have already guided these choices. Save development decisions,
training logs, source/weight hashes and the untouched test manifest before training.

Activate this component only after a separate review, dated registration and runtime approval.
Pending outcomes of other components cannot be treated as development evidence from an untouched
test set.

The write-up draft starts on 2026-10-20 regardless of experiment progress. Incomplete components
are reported as incomplete; they do not postpone writing or the 2026-11-15 deadline. These dates
do not authorize scheduled automation or execution beyond the stated gates and approvals.

## Lapses of September 2026 and the families of the October 2026 paper — dated addition, 2026-10-12

Signed off by the author on 2026-10-12; the commit containing this addition is the author's approval. Appended
at 2026-10-12 09:20 UTC on top of commit 54f24db30ebcea87a57b9d52306ae8c5d7152a04. At the time of this addition no Study 2 target value,
forecast or score exists: study/study2/acquisition_status.json records target_values_opened false and
real_forecasts_generated false, and no holdout forecast was produced. Nothing above this heading changes. The
registered Study 1 bytes and the Study 2 registration bytes at df55867 remain prefixes of this file. The cause
of every lapse below is the same: no work was done in this repository between 2026-09-14 and 2026-10-11. Each
item states what changes and why; none depends on any outcome.

### 1. The October prospective holdout was not frozen and is reported as not run

The freeze deadline of 2026-09-28 18:00 UTC passed with no freeze plan prepared, no approval signed, no
forecast generated and no prediction committed. Under the registered rule a late commit fails the prospective
gate and no backdating or reconstruction is allowed, so the holdout family H01 to H18 has no result and the
settlement retrievals declared for 2026-10-15 and 2026-11-07 are not performed. The write-up reports the
holdout as registered and not run. The implementation's requirement that a completed holdout freeze and a
prediction commit precede external evaluation was an implementation ordering, not a rule of this protocol;
with the holdout not run, external evaluation proceeds without it, and the gate code is changed to that effect
in a commit that cites this addition and keeps every other gate requirement.

### 2. The npm readiness clock is reset once

The registered rule substitutes PyPI only when npm cannot provide the bounded metadata and context extraction
and verified coverage under approved quotas within 14 calendar days of 2026-09-14. That date passed with npm
untested: the only npm access was the metadata probe of 2026-09-14, which counted 4,389,348 registry documents
and acquired no creation metadata and no download count. Inactivity is not the source failure the rule names,
so the lapse triggers no substitution. The clock is reset once: npm must have a verified achieved panel
(manifest, selection and context files under the registered rules) by 2026-10-20 23:59 UTC. If it does not,
the registered rule applies unchanged: record the operational failure before any target scoring and
substitute PyPI via ClickPy in the packages slot; if PyPI also fails, report the packages domain unavailable.
No further reset follows. The registered candidate-pool rule is read as written: sort the frozen name inventory
by the candidate hash and walk it in that order, requesting creation metadata only until 10,000 eligible
packages are found. This yields exactly the first min(10000, N) metadata-eligible keys and does not require
creation metadata for every registry document.

### 3. The external confirmatory family of the October 2026 paper is E01 to E18

NYC 311 and Wikipedia are not run before the paper of October 2026 and are deferred to the spring plan, for
calendar and resource reasons, decided before any Study 2 target value was accessed. For that paper the
external confirmatory family is the eighteen packages-domain tests E01 to E18 exactly as registered, with BH
applied once at q=0.05 over those eighteen. Tests E19 to E54 keep their registered definitions and, when NYC
311 and Wikipedia are run, form one family of 36 with its own single BH correction; they are not merged back
into a 54-test correction after the eighteen have been seen. The registered sentence that the holdout's
npm-unavailability rule is the sole permitted domain-based reduction of a comparison family is amended by this
item for this one case. The gate's requirement that all three domain panels be present is changed accordingly
in a commit that cites this addition. The write-up states that the registered design had three domains and
that two were not run.

## Discrete CRPS availability — dated addition, 2026-10-15

Signed off by the author on 2026-10-15; the commit containing this addition is the author's approval.
Appended at 2026-10-15 05:54 UTC on top of commit e5321cd12011d02bb77c6f8ae24b4830823ac43b. Nothing above this heading changes; the
registered Study 1 bytes and the Study 2 registration bytes at df55867 remain prefixes of this file.

### 5. Discrete CRPS when the certified bound is not attained

The registered numerical rule for the discrete CRPS requires a certified residual bound below 1e-8 by
k = 1,000,000 and says to stop on failure to achieve it. For a series whose counts run into the millions a
day, no forecast can be certified within that work limit, and a stop would leave the confirmatory family
E01 to E18, which uses QScore9 alone, unrun because of a secondary score. From this addition, a forecast
whose bound is not certified by k = 1,000,000 has its discrete CRPS recorded as unavailable, with that
reason, and is counted in the valid denominators the protocol already requires for secondary scores; the
run continues. The work limit, the tolerance and the certification are unchanged, and nothing is truncated
or substituted. QScore9, the occurrence Brier score, the randomized PIT and every confirmatory family are
unaffected. Decided on 2026-10-15 from the frozen npm selection context alone, before any Study 2 target
value was accessed: study/study2/npm_panel_status.json records target_values_opened false, and the series
concerned (aggregate-error, last-28-day context mean 7,637,136) was identified by a context-only probe.

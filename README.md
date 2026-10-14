# PulseGraph v2

PulseGraph studies whether zero-shot foundation models improve probabilistic
forecasts of daily GitHub star-history counts relative to classical and
count-aware baselines. The [v1 study and audit](https://github.com/vprchlik/Project-PulseGraph)
found lower mean errors but identified outcome-selected cohorts and windows
dominated by post-peak decay. Version 2 changes the sample, calendar and inference.

## How this project was built

This study exists for three reasons: the question, whether zero-shot time-series foundation models
improve probabilistic forecasts of sparse daily counts; the audit of its first version, which found no
invalidating code defect but two design flaws; and the registered redesign that answers the question
without them. The code in this repository was written with AI coding agents under my direction. I set the
question, registered the protocol before any target data was fetched, ran the studies on my own machine,
and made the decisions that the protocol and the evidence package record as the author's. Every number in
`RESULTS.md` traces to a saved file under `reports/` and to the command that regenerates it, named in this
README and in `RESULTS.md`.

## Registration and evidence

[PROTOCOL.md](PROTOCOL.md) was registered at **5f01769** on 2026-09-12:
`5f01769b6be4c32814befdd7cc3395b6dcc386ed`. Its SHA-256 is
`dfe2f4adf5c3fdafaa6f2716ae7c19cd4d52577497041c13b763ba06540f65c5`.
The write-up must record this commit. `.gitattributes` preserves the protocol's
LF bytes. The implementation does not edit the protocol.

On 2026-09-13, all 20 validation repositories were captured completely and compared
with hourly 2024 GH Archive counts. The author accepted America/Los_Angeles
calendar days. The frame contains 148,550 eligible repositories; the seeded
complete-history walk accepted 100 in each stratum and recorded 470 skips.
The achieved dataset contains 289,316 daily observations. Synthetic GPU smoke
passed against implementation ca67dd22ea49377ee1fd074aed57b4b7460c84f1.
The signed readiness and descriptive diagnostics are in
[the evidence package](reports/registered-2026-09-13/evidence/readiness-review.md).

Recovery of the June/July v1 artifacts is deferred. They are on another computer
the author no longer uses and may be retrieved later. The local, ignored
`v1_reference/` retains documents, tables, metadata and four figures. The write-up
must disclose reliance on those sources and that v1 numbers were not recomputed.

## Files and environment

The tree contains study code (`pulsegraph/`), commands (`scripts/`), offline tests
(`tests/`), the protocol and the contribution rules in `CONTRIBUTING.md`. `study/` contains the exact
18 comparisons, runtime settings/model revisions, 20 validation repositories and
selection rationale, both SQL queries and an unresolved readiness example.
These files are declarations, not experimental results.

The artifact package under `reports/registered-2026-09-13/` contains the achieved
v2 manifest and aggregate signals, full eligible frame and frozen order, skip logs,
query exports and provenance, validation comparisons and figures, signed readiness,
synthetic smoke evidence, registered run metadata and summaries, integrity checks,
confirmatory inference and the declared descriptive tables. The 433,172,286-byte
results.parquet is published as a release asset, URL to be filled after the push,
SHA-256 as recorded in run.json. The parquet and local byte parts are excluded
from the tree; results-parts.json and pack_results.py are retained.
Duplicate recovery checkpoints remain local, with their hashes and completion
times retained in the run metadata and repository timing table.
Raw endpoint responses and weights remain excluded;
their hashes and capture locations are retained. A fresh clone has no v1 data/results,
`v1_reference/`, raw captures or `WRITEUP.md`. There are
no blanket CSV/parquet ignore rules. Raw captures belong under ignored
`data/raw/`, caches under `data/cache/`, and weights under `models/`.
`.env`, `.venv/`, `.pytest_cache/` and private `notes/` are ignored. The research
note of 2026-09-12 is not in the tree. Tokens and credentials are never tracked.

Use Python 3.12 and PowerShell on Windows 11; there is no WSL. From
`C:\Users\piano\projects\PulseGraph`, using the existing environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,classical,ingest]"
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest_cache\tmp
.\.venv\Scripts\python.exe -m ruff check pulsegraph scripts tests
.\.venv\Scripts\python.exe -m ruff format --check pulsegraph scripts tests
```

Extras: `dev` supplies pytest/Ruff/builds; `classical` supplies the approved
`statsforecast==2.1.1`; `ingest` supplies approved `google-cloud-bigquery>=3.25,<4`;
`models` supplies PyTorch, Hugging Face Hub, Chronos and `timesfm[torch]==3.0.2`.
Install a CUDA-capable PyTorch build for the RTX 4070 SUPER before `.[models]`.
Record exact installed runtime versions before evaluation. StatsForecast requires
pandas below 3. Foundation imports are lazy; tests mock them and block HTTP.
Native StatsForecast tests run when the classical extra is installed.

`.env.example` has empty names for `GITHUB_TOKEN`,
`GOOGLE_APPLICATION_CREDENTIALS` and `BIGQUERY_PROJECT_ID`. Actual values belong
only in ignored `.env`; credentials files may be outside the repository.
Saved requests exclude authentication headers.

## Validation and frame

GitHub star history supplies forecast counts. GH Archive supplies repository
creation, day-90 eligibility and the 2024 validation comparison; its WatchEvent
degradation after mid-2025 overlaps all evaluation windows. Sources are cited
in the protocol. The fixed validation selection keeps 15 large projects and
adds five small public repositories with 217–345 stars and no pushes since 2024:
asciidoc-py, imapbox, pyeda, neighbourhood and SolidsPy. Dated metadata checks
and sources are recorded in `study/validation_repositories.json`. Zero days,
low counts and relative discrepancies must be exercised, not only large active
histories. Sparse recent development and low-count star days were checked in the saved
validation captures and calendar comparison. This is a purposive validation set.
Each creation date must precede 2023-01-01, excluding it from the main sample.

After the implementation commit is confirmed:

```powershell
.\.venv\Scripts\python.exe -m scripts.validate_star_history fetch --out data\raw\validation-2026-09-12
.\.venv\Scripts\python.exe -m scripts.dry_run_frame --out data\cache\bigquery-estimate.json
```

The history client saves response bytes/hashes, sanitized headers, stable IDs,
renames, creation/extraction times and pagination evidence. It follows all pages,
detects malformed/overlapping/gapped weeks, bounds retries and rejects foreign
redirects. Repeating validation verifies and reuses complete captures; every
failed attempt retains its reason, including failures followed by a successful
retry. All 20 must be attempted; comparison and readiness use the complete
captures and retain attempted, complete, failed and historical-failure counts.
Missing days are not silently filled.
`daily_nominal.csv` is explicitly unverified, not a UTC evaluation dataset.
Timezone and unstar interpretation require observations and author sign-off;
a single capture cannot establish whether past counts change after unstars.

The queries use bounded daily tables and deduplicated WatchEvent IDs, without
a payload-action filter. Creation spans 2023-01-01 through 2025-02-21; eligibility
ends at b+89, no later than 2025-05-21. `freeze_frame_order` sorts stable IDs
then shuffles with seed 20260913. `walk_frame` logs every skip until 100 complete
histories per stratum or exhaustion. `validate_sampling_log` replays that order.
Unknown historical coverage is not treated as zero activity.

The dry-run command only submits cache-disabled `dry_run=True` jobs. It has no
billable mode. One report gives both query estimates, their combined bytes/cost
and proposed caps with 10% headroom. Its default $6.25/TiB price assumes no free
credit; verify current pricing before approval or supply `--usd-per-tib`.
Written approval precedes either actual query. Preserve exact SQL, parameters,
estimates, job IDs, actual costs and coverage evidence.

The approved 2024 export supplies every UTC hour for all 20 repositories,
including zeros (8,784 hours each). Comparison uses complete captures and bins
hours as UTC days, America/Los_Angeles days with DST, and fixed UTC-8 days.

```powershell
.\.venv\Scripts\python.exe -m scripts.validate_star_history compare --validation data\raw\validation-2026-09-12 --archive-counts data\raw\archive-2024.csv --out data\validation-comparison
```

This saves per-repository daily agreement/MAD under each hypothesis, seasonal
summaries, transition-day details and source hashes. All hypotheses are scored
on January 1 through December 30, the common complete-day span. December 31
is retained with explicit partial-coverage flags for the UTC-8 calendars: the
2024-only export lacks their final eight hours. Partial counts are never scored
as full days. Resolve the calendar mapping before constructing evaluation counts.

## Descriptive panel diagnostic

Descriptive diagnostic of the frozen achieved panel, not a selection criterion. The numerator sums the first 90 Los Angeles calendar days, beginning on local creation day; the denominator retains gross archive eligibility over the UTC creation date and next 89 UTC days. These are different calendar boundaries, so the ratio is not an exact unstar-retention probability. For boundary sensitivity, the per-repository table also sums survivor bins with nominal dates equal to the archive's 90 date labels; it does not reconstruct UTC-hour totals. The final 90 days are 2026-06-03 through 2026-08-31 inclusive in Los Angeles. Percentiles use linear interpolation across all 100 accepted repositories per stratum. No repository is removed, replaced or reweighted.

| Stratum | Accepted | Ratio median | P10 | P90 | Ratio <0.5 | Last-90 total median | Zero last-90 | Skipped |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 20-99 | 100 | 0.9677 | 0.7232 | 1.0747 | 3 | 0.0 | 52 | 98 |
| 100-999 | 100 | 1.0040 | 0.8854 | 1.0789 | 2 | 4.0 | 22 | 348 |
| 1000+ | 100 | 1.0059 | 0.9144 | 1.0491 | 2 | 39.0 | 1 | 24 |

| Stratum | Skip reason | Count |
|---|---|---:|
| 100-999 | id_resolver_http_403 | 3 |
| 100-999 | id_resolver_http_404 | 345 |
| 1000+ | id_resolver_http_403 | 1 |
| 1000+ | id_resolver_http_404 | 23 |
| 20-99 | id_resolver_http_404 | 98 |

Per-repository values, exact summaries and hashes are in [the diagnostic evidence](reports/registered-2026-09-13/evidence/panel-diagnostic/diagnostic.json).

## Models, calendar and scores

The frozen models are Chronos-2, TimesFM 3 and TimesFM 2.5. Exact weight revisions
and separate weight/package licences are in `study/run_spec.json`. All use
univariate context, batch size 1 and a 2,048-day maximum context; TimesFM's
configured maximum horizon is 128. Used and available context are recorded.
TimesFM 3 uses the PyTorch `timesfm3.TimesFM3Evaluator` built from `ModelConfig`
with the pinned local snapshot, batch size 1 and CUDA. Prediction requests only
contexts, horizon, native quantiles and disabled symmetric averaging; the adapter
verifies all nine decile levels and records its own clip-then-cummax repair.
Neither TimesFM receives invented 95% tails; unsupported intervals remain NaN.

The 15 baselines retain the seven v1 families, add local-mean lookbacks 7/14/56/90,
and add weekly AutoETS/AutoARIMA/AutoTheta and `nb_local_level_28`. Primary
references are `local_mean_28` and `autoets_weekly`. V1 horizon-dependent
seasonality, nonseasonal Holt and in-sample residual uncertainty remain limitations.

StatsForecast maps native 20/40/60/80% central intervals to eight outer deciles
and uses the point forecast for the median. Each fit saves its specification
and parameters. AutoETS excludes multiplicative error/seasonality when zeros
occur. AutoTheta uses 200 native simulations with seed 0: finite-sample bounds
are not exactly symmetric, and the method/seed are recorded. The NB mean uses
28 days and dispersion uses unbiased full-context moments, with analytic deciles
and exact Poisson/point-mass-zero limits. No fit failure activates a new fallback.

Primary `qscore9` is twice decile mean pinball loss; it is unavailable for other
scoring grids. MASE of the median is the write-up's point metric. MAE and RMSSE
remain saved; RMSSE stays out of the write-up. WQL is undefined on zero targets.
Fair CRPS and randomized empirical PIT require genuine IID draws and remain
unavailable for native/analytic quantile forecasts. Undefined secondary scores
retain NaN and valid counts. Clipping/crossing repairs are recorded.

Cutoffs are 2025-12-05, 2026-03-05 and 2026-06-03, with horizons 7/30/90 and
common endpoint 2026-08-31. Maximum-horizon targets do not overlap. The actual
regime labeler only receives dates before cutoff; tests perturb, permute and
extend future data and verify eligibility bounds. Regimes are descriptive and
pooled for confirmatory inference.

## Gate, runtime smoke and recovery

`study/readiness.example.json` is unresolved and cannot authorize evaluation.
Completed readiness records identify the author/date, approved calendar mapping,
timezone evidence, unstar interpretation and later-information limitation,
long-run approval, exact runtime versions, frozen input hashes and eight evidence
files with SHA-256 hashes. Evidence paths are relative to the readiness document:

- `validation`: `validation.json` accounting for all 20 attempts and every failure reason.
- `comparison`: 2024 `comparison.json` for every complete capture, retaining counts and failures.
- `frame_coverage`: JSON with `complete: true` and supporting coverage evidence.
- `candidate_order`: full seeded candidate-order CSV.
- `sampling_log`: accepted/skipped/strata JSON returned by `walk_frame`.
- `cost_approval`: author's written query/cap approval saved as JSON.
- `query_provenance`: JSON with SQL, parameters, bounds, job IDs and actual costs.
- `smoke`: synthetic runtime/GPU report for this implementation and environment.

The achieved manifest supplies stable ID, creation date, day-90 count, sampling
stratum, fetched name, observation start, endpoint `repository_created_at` timestamp and
`coverage_complete: true`. The manifest keeps the frame's UTC creation date;
observation start is that creation instant's date in the validated convention.
The readiness field `calendar_convention` identifies UTC, America/Los_Angeles,
or fixed UTC-08:00. Stored daily timestamps are calendar labels, not a claim
that non-UTC bins begin at UTC midnight.
Signals explicitly contain every repository/day's integer count through the
endpoint. Preserve raw capture provenance with these data. The gate rejects
missing daily bins instead of using the synthetic loader's zero-fill option.

```powershell
.\.venv\Scripts\python.exe -m scripts.smoke_registered --implementation-commit <full-implementation-hash> --out data\cache\runtime-smoke.json
.\.venv\Scripts\python.exe -m scripts.run_registered --implementation-commit <full-implementation-hash> --readiness data\readiness.json --signals data\daily-counts.parquet --manifest data\manifest.json --out data\runs\registered-01
```

Replace the hash placeholders before running. The smoke command generates its
own synthetic contexts and accepts no target data. The real gate verifies exact
protocol commit/bytes, current clean implementation, model pins/seeds/settings,
18 comparisons, readiness evidence and frozen inputs before GPU/model access.
`run.json` records GPU model, driver, CUDA/PyTorch versions, package/source hashes
and commands. The GPU allocator is capped at 7 GB, reduced when shared free memory
is lower, reserving 1 GB below the 8 GB limit for CUDA/library overhead. Actual
allocator peaks are saved and checked; GPU smoke must demonstrate the budget.
Each model is constructed once per run invocation. Foundation weights remain
resident across repositories; forecasts run serially and all models are released
at completion or failure. Synthetic GPU smoke uses the same resident-model lifecycle.

Each whole repository writes a hashed atomic checkpoint only after every
model/window succeeds. Any failed window, including OOM, stops and records
failure. Repeat the same command to resume: verified completed repositories
are reused, the failed repository restarts and `run.json` records the resume.
Changed inputs, code, runtime or declarations reject resume. Complete runs
are immutable; deliberate reruns use new linked directories.

Finished runs contain `run.json`, `results.parquet`, `summary.csv`,
`signals.parquet`, `manifest.json` and checkpoints. Integrity checks verify
hashes, the full grid, contexts/targets, labels, seeds and recomputed scores.

```powershell
.\.venv\Scripts\python.exe -m scripts.review_integrity --run data\runs\registered-01
.\.venv\Scripts\python.exe -m scripts.registered_inference --run data\runs\registered-01 --out data\inference\registered-01
```

Confirmatory inference averages windows within repository, pools regimes,
bootstraps repositories 20,000 times and applies BH once over 18 two-sided
Wilcoxon tests. It saves paired tables, raw/adjusted p-values, pointwise intervals,
seeds and provenance. Inference is conditional on the fixed calendar. The seven
general review commands remain post-hoc and never refit models.
`scripts.run_experiment --synthetic` remains available for software checks.

## Saved registered run

The run at implementation `ca67dd22ea49377ee1fd074aed57b4b7460c84f1` completed
on 2026-09-13 in 18,662.063521 seconds (5 hours, 11 minutes, 2 seconds), with
300 repositories, 48,600 forecast rows, no failures and no resumes. The gate
and saved-artifact integrity check passed. [RESULTS.md](RESULTS.md) contains
the 18-row registered inference table and descriptive tables without interpretation.
Full precision inference values, paired repository scores and provenance are under
`reports/registered-2026-09-13/inference/`; descriptive CSVs and their provenance
are under `reports/registered-2026-09-13/descriptive/`.

`results.parquet` is published as a release asset, URL to be filled after the push,
SHA-256 as recorded in `run.json`:
`53ff5a5316fd43dd898866c4fc54edf913b080a32cbd696d7e3b3fc528f62df6`.
Release asset URL: **to be filled after the push**. Place the downloaded file at
`reports/registered-2026-09-13/run/results.parquet`, then verify it and regenerate
inference from saved forecasts. Choose a new output directory for reproduction:

```powershell
.\.venv\Scripts\python.exe -m scripts.review_integrity --run reports/registered-2026-09-13/run
.\.venv\Scripts\python.exe -m scripts.registered_inference --run reports/registered-2026-09-13/run --out data/cache/inference-reproduction
.\.venv\Scripts\python.exe reports/registered-2026-09-13/summarize_descriptives.py
```

`run/results-parts.json` retains the local packaging checksums; its `.data` parts
are ignored and are not required when obtaining the complete release asset.
The package's `.gitattributes` preserves the bytes covered by evidence hashes.
The final results retain every forecast, sample/quantile grid, context, target,
seed and model metadata; duplicate per-repository recovery files are excluded
from the commit. Raw capture locations and hashes remain in the achieved manifest.

## Study 2 implementation and source readiness

Study 2 is registered at `df55867c982dfe2bb6e1152ec8ae93e3cd228c45`.
The full protocol SHA-256 at registration is
`33cefd8e34fea973e6747d1ba3fe565051e215c5d1b7f6553b266c1be7a66360`.
`pulsegraph/study2/constants.py` keeps this identity separate from Study 1.
Both gates verify their own registered Git blob and require those exact bytes
to remain a prefix of the current protocol. Study 1's results remain closed.

`pulsegraph/study2/` contains context-only ingestion, the prospective freeze
writer, count distributions and baselines, a separate execution gate, whole-series
checkpoints and the synthetic generators. `study/study2/` contains the component
specifications, all 54 external, 6 synthetic and 18 holdout comparisons, the
540-series grid manifest, unsigned approval examples and implementation evidence.
Each family has one BH correction. The nine FM variants share three model fits:
native deciles, completed-unwrapped and hurdle for each frozen foundation model.
Seven baselines give 16 forecasts per origin. Models stay resident per invocation;
failed windows stop the run, and verified completed series support resume.

CDF completion, integer rounding and the exponential tail are explicit in saved
distribution specifications. Discrete CRPS stops only with an analytic residual
bound below 1e-8, failing if it cannot certify this by index 1,000,000.
`study/study2/crps_resolution.json` resolves the numerical OPEN item with synthetic
tests and an independent extended tail sum. Every score includes the exact
zero-day/positive-day and positive over/under accounting. No protocol text was
changed to record implementation resolutions.

Selection uses only September 1, 2025 through June 2, 2026. The final 90 days,
March 5 through June 2, define the frozen zero-fraction strata. Package and
Wikipedia metadata frames use a 10,000-entity seeded hash candidate pool;
NYC 311 uses its full eligible frame. Each stratum keeps at most 100 complete
series, reports any shortage and does not transfer slots. Capture exhaustion
is required before zero days can be inferred for NYC event counts. Missing
package/pageview observations remain missing. Selection tests perturb, permute
and extend future data; every origin also has a model-input date-spy test.

Acquisition commands save request bounds, acquisition timestamps and response
hashes. Commands are bounded to 500 requests and 55 minutes by default; a quota
or time limit stops acquisition without declaring a partial inventory complete.
Repeated commands reuse verified response captures. Raw captures and provisional
manifests/signals are under ignored `data/raw/study2/`; no external-domain target
snapshot is in the tree. A completed achieved panel writes `manifest.json`,
`context.parquet` and `selection.json`, including reserve order and skip reasons.
Aggregate publication requires the registered source-redistribution review.

```powershell
.\.venv\Scripts\python.exe scripts\study2_ingest.py npm inventory --captures data\raw\study2\npm\captures --out data\raw\study2\npm\inventory.json
.\.venv\Scripts\python.exe scripts\study2_ingest.py npm panel --captures data\raw\study2\npm\captures --inventory data\raw\study2\npm\inventory.json --out data\raw\study2\npm\panel
.\.venv\Scripts\python.exe scripts\study2_ingest.py nyc311 inventory --captures data\raw\study2\nyc311\captures --out data\raw\study2\nyc311\inventory.json
.\.venv\Scripts\python.exe scripts\study2_ingest.py nyc311 panel --captures data\raw\study2\nyc311\captures --inventory data\raw\study2\nyc311\inventory.json --out data\raw\study2\nyc311\panel
.\.venv\Scripts\python.exe scripts\study2_ingest.py wikipedia inventory --captures data\raw\study2\wikipedia\captures --out data\raw\study2\wikipedia\inventory.json
.\.venv\Scripts\python.exe scripts\study2_ingest.py wikipedia panel --captures data\raw\study2\wikipedia\captures --inventory data\raw\study2\wikipedia\inventory.json --out data\raw\study2\wikipedia\panel
```

The September 14 metadata probe returned 4,389,348 npm registry documents; this
is not an eligible-frame count. `npm inventory` freezes only the names in npm's
supported replication feed (see the
[replication API changes](https://github.com/orgs/community/discussions/152515)),
scopes included; a stop before pagination is exhausted writes no inventory.
`npm panel` then requests each name's registry document in seeded candidate-hash
order until 10,000 packages created before September 1, 2025 (UTC) are found,
and saves every visited name with its verdict and any exclusion reason beside
the inventory as `inventory.walk.json`; an interrupted walk saves no pool and
resumes from the verified captures, and a complete walk is reused without
requests. Unless the walk exhausts the inventory, the eligible-frame size and
the candidate inclusion probability are estimated from the visited prefix and
reported with exact bounds. The context pull and strata then apply to those
10,000 candidates as above; a transport failure, server error or exhausted
retry stops the pull for a later resume instead of excluding a candidate.
`--max-requests` and `--max-seconds` override a command's default bounds of 500
requests and 55 minutes.
The NYC 2024 inventory contains 9,496 problem/board cells, with 8,469 recognized
community-board cells. Its bounded context pull ended with a transport failure;
achieved strata and shortages remain unknown. Wikipedia's complete inventory has
not been acquired. Its adapter checks namespace, redirect status, earliest
revision, stable page ID and title-history ambiguity before requesting pageviews;
unresolved moves/deletions are exclusions. Wikipedia retains the registered
known-training-overlap label. Source status and hashes are in
`study/study2/acquisition_status.json`; these incomplete acquisitions are not
reported as empty achieved panels.

The freeze requires a separate reviewed context snapshot for each source.
The input JSON to `prepare` supplies `sources` and `timing_evidence`. Each source
has `domain`, `manifest`, `signals` and `completeness`; every file reference is
an object with `path` and `sha256`. Signals have exactly `series_id`, `date`,
`count`, one explicit nonnegative integer observation per day. GitHub uses the
unchanged 300-repository Study 1 manifest, with Los Angeles nominal dates.
npm uses its verified achieved manifest and UTC dates.

The completeness document records `calendar`, `verified: true`, `method`,
`verified_at`, `last_complete_day`, `signals_sha256` and hashed `response_evidence`.
Source availability evidence must establish the last complete day; an elapsed
calendar day alone does not establish that the source has finished publishing it.
The preparer checks these evidence files, calendar bounds, all panel IDs and
every daily bin. It reports the bridge from the next context day through
September 30, then forecasts `bridge_days + 30` leads. The writer copies context
files, saves full distributions where available and hashes each prediction file.
`verify_predictions` rechecks the complete panel, context hashes and forecast grid.

```powershell
.\.venv\Scripts\python.exe scripts\study2_smoke.py --gpu --context-days 1400 --leads 60 --out data\raw\study2\smoke-new.json
.\.venv\Scripts\python.exe scripts\study2_holdout.py prepare --input data\raw\study2\holdout-input.json --out data\raw\study2\holdout-plan.json
```

Stop after preparing the plan: report each last complete day, bridge, achieved
panel and model runtime estimate for author confirmation. The unsigned
`study/study2/freeze_approval.example.json` shows the required fields. Only a
separate signed approval bound to the plan hash authorizes the following command.

```powershell
.\.venv\Scripts\python.exe scripts\study2_holdout.py freeze --input data\raw\study2\holdout-plan.json --approval data\raw\study2\freeze-approval.json --out reports\study2-holdout
```

No freeze may begin or continue after September 28, 2026 at 18:00 UTC. npm must
have a verified panel by September 26; until that deadline its status is pending.
If unavailable then, record the reason and freeze GitHub alone, declaring H01-H09
before scoring. No PyPI substitution is permitted in the holdout. Prediction
hashes must be committed before October 1. Settlement attempts are October 15
at 18:00 UTC for horizon 7 and November 7 at 18:00 UTC for horizon 30, with
12-hour retries for at most 72 hours. These are declared retrieval windows,
not scheduled jobs.

The external run has a second approval boundary. Its unsigned example requires
the committed holdout freeze, source evidence, separate target-access approval,
three domain manifests and signals, their original selection contexts, current
implementation smoke and an approved runtime budget. Targets cannot replace the
frozen selection prefixes. `scripts/study2_gate.py` validates readiness;
`scripts/study2_run.py` validates it before opening external target files or
loading models. Synthetic evaluation also requires its own runtime approval.
No Study 2 holdout forecast or external-domain evaluation has run. The current
source evidence is incomplete; the existing GitHub dataset ends August 31 and
is not a newly verified freeze-day snapshot. Repeat GPU smoke after committing
the implementation so its HEAD and source hashes match the eventual gate.

## Licence

PulseGraph code is [MIT](LICENSE). The eventual aggregate dataset and write-up
carry CC BY 4.0. Chronos and TimesFM package/source code is Apache-2.0.
Chronos-2 and TimesFM 2.5 weights are Apache-2.0; TimesFM 3 weights have the
separate TimesFM Non-Commercial License v1.0.

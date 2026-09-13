# PulseGraph v2

PulseGraph studies whether zero-shot foundation models improve probabilistic
forecasts of daily GitHub star-history counts relative to classical and
count-aware baselines. The [v1 study and audit](https://github.com/vprchlik/Project-PulseGraph)
found lower mean errors but identified outcome-selected cohorts and windows
dominated by post-peak decay. Version 2 changes the sample, calendar and inference.

## Registration and evidence

[PROTOCOL.md](PROTOCOL.md) was registered at **5f01769** on 2026-09-12:
`5f01769b6be4c32814befdd7cc3395b6dcc386ed`. Its SHA-256 is
`dfe2f4adf5c3fdafaa6f2716ae7c19cd4d52577497041c13b763ba06540f65c5`.
The write-up must record this commit. `.gitattributes` preserves the protocol's
LF bytes. The implementation does not edit the protocol.

As of 2026-09-12, validation consists of offline tests, mocked foundation-model
APIs and actual synthetic StatsForecast fits. No target histories, BigQuery
jobs, foundation weights, GPU forecasts or v2 results have been obtained.
Empirical endpoint validation and runtime smoke evidence remain required.

Recovery of the June/July v1 artifacts is deferred. They are on another computer
the author no longer uses and may be retrieved later. The local, ignored
`v1_reference/` retains documents, tables, metadata and four figures. The write-up
must disclose reliance on those sources and that v1 numbers were not recomputed.

## Files and environment

The tree contains study code (`pulsegraph/`), commands (`scripts/`), offline tests
(`tests/`), the protocol and working instructions. `study/` contains the exact
18 comparisons, runtime settings/model revisions, 20 validation repositories and
selection rationale, both SQL queries and an unresolved readiness example.
These files are declarations, not experimental results.

A fresh clone has no v1 data/results, `v1_reference/`, achieved v2 manifest,
aggregate dataset, results table, figures, `RESULTS.md` or `WRITEUP.md`.
V2 manifests, results, summaries, figures and aggregate data will be deliberately
tracked; oversized datasets require a durable location and checksum. There are
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
histories. Sparse recent development is observed; star-day sparsity remains to
be checked during retrieval. This is a purposive validation set.
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

## Licence

PulseGraph code is [MIT](LICENSE). The eventual aggregate dataset and write-up
carry CC BY 4.0. Chronos and TimesFM package/source code is Apache-2.0.
Chronos-2 and TimesFM 2.5 weights are Apache-2.0; TimesFM 3 weights have the
separate TimesFM Non-Commercial License v1.0.

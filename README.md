# PulseGraph v2

PulseGraph studies whether zero-shot time-series foundation models improve
probabilistic forecasts of daily new GitHub star counts relative to classical
and count-aware baselines.

The first study found lower mean forecasting error for foundation models. Its
audit found that repository cohorts were selected using information unavailable
at forecast time, and most evaluated windows measured post-peak decay. Version 2
redesigns the population, windows, baselines and inference around those findings.
The v1 findings remain subject to the limitations in the
[original study and audit](https://github.com/vprchlik/Project-PulseGraph).

## Status

As of 2026-09-12, the study library, offline tests and seven review commands
have been ported. Validation uses synthetic counts and mocked model outputs.
No real v2 data have been collected, no model weights have been loaded, and
no v2 experimental results exist.
The experimental design in [HANDOFF.md](HANDOFF.md) is provisional.
`PROTOCOL.md` has not been written or committed. Evaluation on real targets
must wait for the approved, committed protocol with exact model revisions,
seeds, population and window rules, baselines, metrics and comparisons.

Recovery and backup of the v1 data and result artifacts are **deferred**. The
June and July 2026 work ran on another computer that the author no longer uses.
The artifacts are unavailable now and may be retrieved later; they are not
declared lost. For now, v1 is available through its documents, tables, metadata
and four figures in the local `v1_reference/` copy and the original repository.
The write-up will disclose that these results have not been recomputed from
the original artifacts. If those artifacts arrive, their location, inventory
and backup must be verified before claiming reproducibility.

## What is in the tree

The tree contains the study package under `pulsegraph/`, commands under
`scripts/`, tests under `tests/`, and `AGENTS.md`, `HANDOFF.md`, `README.md`,
`pyproject.toml`, `MANIFEST.in`, `.env.example`, `.gitignore` and `LICENSE`.

- `v1_reference/` is a local, read-only copy of the old repository. It is
  gitignored and is absent from a fresh clone of this repository.
- The v1 results parquets, summary CSV, saved review outputs, raw per-star
  timestamps, repository manifests and `data/raw/daily_signals.parquet` are
  unavailable here. Neither repository's committed files reproduce the v1
  numerical results from source data.
- There is no v2 dataset, repository manifest, results table, figure,
  `RESULTS.md` or `WRITEUP.md` yet.
- `.venv/`, `.pytest_cache/`, `.env`, raw data under `data/raw/`, caches under
  `data/cache/`, and model weights are local only and ignored. Tokens belong
  in `.env` and must never be committed or printed. `.env.example` has names
  with empty values only. Test artifacts remain under pytest's temporary path.

For v2, the repository manifest, aggregated daily-count dataset if its size
allows, result tables, summary CSVs and figures will be tracked deliberately.
The README will identify their paths and reproduction commands when they exist.
There are no blanket ignore rules for parquet or CSV files. Raw per-star
timestamps and model weights will remain outside the committed tree.

## Development setup

Use Python 3.12 on Windows with PowerShell; package metadata permits Python
3.10 or later. From `C:\Users\piano\projects\PulseGraph`, create the environment
if needed and install the study and development dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
```

The tests cover observation bounds, all-zero repositories, deterministic
baselines, metric formulas, model quantile shapes and revision loading,
forecast-time information boundaries, artifact recomputation and repository
inference. Tests block network requests. Model adapters are tested with fake
pipelines; this does not validate a real checkpoint or GPU environment.
Test collection, linting and package discovery exclude `v1_reference/`.

```powershell
.\.venv\Scripts\python.exe -m ruff check pulsegraph scripts tests
.\.venv\Scripts\python.exe -m ruff format --check pulsegraph scripts tests
```

The default dependencies cover tables and parquet files, numerical methods,
classical baselines, HTTP ingestion, local environment variables and figures.
The optional `models` extra declares PyTorch,
[Chronos](https://pypi.org/project/chronos-forecasting/) and
[TimesFM with its PyTorch extra](https://pypi.org/project/timesfm/).
These development requirements do not select the final comparison set or pin
model weights. Exact package versions and model revision hashes must be
recorded before evaluation. Model runtimes and checkpoints are not needed for
the offline tests. Both adapters require an explicit 40-character revision hash,
seed and context limit. Loading resolves that revision to a local Hugging Face
snapshot under `models/`. No default revision such as `main` is accepted.

The repository is for study code. Cloud ingestion dependencies will be added
when ingestion is implemented, with cost approval before any paid data pull.
Agent working rules are in [AGENTS.md](AGENTS.md); the experiment background
and design decisions are in [HANDOFF.md](HANDOFF.md).

## Data and forecast contracts

Daily counts use `repo_name`, `event_date` (a whole UTC date), and `stars`
(a finite nonnegative integer). Duplicate repository/day rows are rejected.
The manifest supplies `repo_name`, `observation_start` and a boolean
`coverage_complete` for every repository. The caller must confirm complete
coverage before zero filling; missing observation days must not be presented
as zero activity. All repositories share an explicit observation endpoint.
Leading and trailing zeros, including entirely zero series, are retained.

`BacktestConfig` requires a declared calendar of cutoff dates, horizons,
minimum context length, common quantiles, scaling period and seed. A cutoff
is the **first forecasted date**; models and context labelers receive only
earlier observations. The longest target intervals at successive cutoffs
cannot overlap. Missing history, incomplete targets and model failures stop
the run. The default label is `all`; no future-selected v1 cohorts are carried.

The seven baseline candidates retain the v1 families: `naive_seasonal`,
`linear_30`, `ets`, `lightgbm`, `last_value`, `weekly_naive`, and
`local_mean_28`. Other local-mean lookbacks receive distinct names.
Every sample-producing call records its root seed, derived seed and parameters.
LightGBM uses its native API with one thread and deterministic fitting.

The legacy seasonal naive still depends on the horizon; `ets` is damped,
nonseasonal Holt smoothing, not AutoETS. Linear, ETS and LightGBM retain
in-sample residual uncertainty around a deterministic path. These limitations
are explicit in the code. Seasonal AutoETS, a count-aware model with rolling
calibration, and the final comparator list await the research and protocol.

The two foundation-model adapters cover Chronos-2 and TimesFM-2.5. They retain
native quantiles, clip negative predictions and repair crossing quantiles by
cumulative maxima, recording how many values changed. Context truncation is
explicit and recorded. TimesFM-2.5's 95% interval is unsupported and remains
NaN. Additional models, including TimesFM 3, await the model review.

## Metrics and artifacts

| Output | Definition and limitation |
|---|---|
| `mean_pinball_loss` | Mean pinball loss over all target days and the declared common quantile grid. |
| `wql` | Mean across quantiles of twice summed pinball loss divided by summed absolute targets. Undefined on an all-zero target window. |
| `interval_score_80` | Central interval width plus the standard outside-interval penalty with alpha 0.2. |
| `mae`, `mase`, `rmsse` | Median forecast errors; scaled denominators use context only and the declared seasonal period. Zero or unavailable scales give NaN. |
| `crps_mean` | Fair finite-sample CRPS for IID marginal draws. Unavailable for native-quantile-only forecasts. |
| `coverage_80`, `coverage_95` | Inclusive finite-bound coverage; unsupported intervals give NaN. |
| `pit_values` | Seeded randomized empirical PIT for sampled forecasts; unavailable for native-quantile-only forecasts. Histograms are descriptive. |

Finite quantiles do not identify the full predictive distribution. The port
does not clamp unidentified tails into pseudo-samples or claim a full CRPS
for those outputs. The protocol must resolve the cross-model CRPS definition
before evaluation. Current common-quantile comparisons can use
`mean_pinball_loss`; review functions reject metrics with missing values.
Summaries report valid-score counts alongside window and repository counts,
so undefined WQL, scaled errors or intervals cannot disappear from the record.

The synthetic runner writes a new directory containing `signals.parquet`,
`manifest.json`, `results.parquet`, `summary.csv` and `run.json`. The result
rows retain contexts, actuals, samples where available, native quantiles,
model metadata and metric seeds. `run.json` records the calendar, model and
repository lists, package versions, source-file hashes, artifact hashes and
command. Existing run directories are never overwritten. The integrity check
verifies every declared model/window key, dates and input values, recomputes
metrics from saved forecasts, and compares the summary including missingness.

For a small synthetic check from the repository root, choose a new output path:

```powershell
$smokePath = Join-Path $PWD '.venv\smoke-check'
.\.venv\Scripts\python.exe -m scripts.run_experiment --synthetic --seed 42 --out $smokePath
.\.venv\Scripts\python.exe -m scripts.review_integrity --run $smokePath
.\.venv\Scripts\python.exe -m scripts.review_scale --run $smokePath --reference local_mean_28 --metric mean_pinball_loss
```

These are software checks, not study results or a registered model/window
selection. The experiment command requires `--synthetic`; it cannot load real
targets. The real-data runner will require the registered protocol.

The seven `scripts/review_*.py` commands cover integrity, window placement,
scale, stored strong baselines, stored local-mean lookbacks, repository-clustered
inference and censoring. Use `--help` for their required inputs. They read a
saved run and never fit additional models. Review outputs are labeled
`post_hoc` and retain whether the input is synthetic. `--out` writes a new CSV
and a metadata sidecar without overwriting an existing file.

Clustered inference requires a JSON list of comparisons, each specifying
`model`, `reference`, `horizon` and `stratum`, plus an explicit comparison
count, metric, seed, bootstrap size and confidence level. It averages windows
within repository, bootstraps paired repository differences, and applies
Benjamini-Hochberg adjustment to the complete declared family. Missing pairs
or comparisons fail instead of reducing the family. No model or lookback is
chosen by its observed score.

## Supplemental v1 ingestion

`scripts/ingest_stars.py` converts previously saved JSON or JSON.gz timestamp
lists into daily counts offline, using a supplied manifest and observation
endpoint. The `GitHubAPIClient` library retains timestamp collection for
explicitly named repositories. It fails on HTTP errors, malformed records or
incomplete pagination; it neither searches for cohorts nor retries indefinitely.
`GitHubAPIClient.from_env()` explicitly reads `.env` without changing the process
environment. Imports never read tokens or create directories.

REST counts describe surviving stars and do not supply the proposed GH Archive
population dataset. GitHub's documentation now describes restrictions on
stargazer-list access; data-access details must be checked during the research
session. [GitHub starring API documentation](https://docs.github.com/en/rest/activity/starring).

## Licence

Code is licensed under the [MIT licence](LICENSE). The aggregated dataset and
write-up will carry CC BY 4.0 when published; neither is present yet.

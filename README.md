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

As of 2026-09-12, this repository contains the v2 setup documents and Python
package configuration. Study code and tests have not been ported. No v2 data
have been collected, no models have been evaluated, and no v2 results exist.
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

The files intended for the initial commit are `AGENTS.md`, `HANDOFF.md`,
`README.md`, `pyproject.toml`, `.gitignore` and `LICENSE`.

- `v1_reference/` is a local, read-only copy of the old repository. It is
  gitignored and is absent from a fresh clone of this repository.
- The v1 results parquets, summary CSV, saved review outputs, raw per-star
  timestamps, repository manifests and `data/raw/daily_signals.parquet` are
  unavailable here. Neither repository's committed files reproduce the v1
  numerical results from source data.
- There is no v2 dataset, repository manifest, results table, figure,
  `RESULTS.md` or `WRITEUP.md` yet.
- `.venv/`, `.env`, raw data under `data/raw/`, caches under `data/cache/`, and
  model weights are local only and ignored. Tokens belong in `.env` and must
  never be committed or printed.

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

There are no v2 tests yet. Until the study code is ported, pytest reports no
tests collected (exit code 5); this is not a passing study test suite. Test
collection, linting and package discovery exclude `v1_reference/`.

The default dependencies cover tables and parquet files, numerical methods,
classical baselines, HTTP ingestion, local environment variables and figures.
The optional `models` extra declares PyTorch,
[Chronos](https://pypi.org/project/chronos-forecasting/) and
[TimesFM with its PyTorch extra](https://pypi.org/project/timesfm/).
These development requirements do not select the final comparison set or pin
model weights. Exact package versions and model revision hashes must be
recorded before evaluation. Model runtimes and checkpoints are not needed for
the initial setup.

The repository is for study code. Cloud ingestion dependencies will be added
when ingestion is implemented, with cost approval before any paid data pull.
Agent working rules are in [AGENTS.md](AGENTS.md); the experiment background
and design decisions are in [HANDOFF.md](HANDOFF.md).

## Licence

Code is licensed under the [MIT licence](LICENSE). The aggregated dataset and
write-up will carry CC BY 4.0 when published; neither is present yet.

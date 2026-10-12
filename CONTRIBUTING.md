# Contributing to PulseGraph

These rules bind every change to this repository, whoever or whatever makes it. The protocol (`PROTOCOL.md`)
and the results (`RESULTS.md`) were produced under them. The author alone commits and pushes; a proposed change
is checked against these rules before it is committed.

## Research integrity

- The experiments are pre-registered. `PROTOCOL.md` was written and committed before any evaluation ran on
  real targets, and the commit hash is recorded in the write-up. Nothing in the protocol changes after results
  are seen. An amendment is a dated addition at the end that says what changed and why, signed off by the
  author and committed before the run it affects; never an edit in place.
- No look-ahead. Every model sees only data through the cutoff. Any regime or cohort label must be computable
  from data through the cutoff. A test proves this.
- No selection on outcomes. Baselines, lookbacks, model revisions, metrics, windows and the comparison count are
  declared before the first run. Extra analyses after results are labelled post-hoc and never replace a
  declared one.
- Report either way. A null or negative result is written up with the same care as a positive one.
- Every stochastic path is seeded and the seed recorded. Every model is pinned to an exact revision hash. Every
  number in a write-up is traceable to a saved artifact and a command that regenerates it.
- Suspiciously good results mean a bug until proven otherwise. Hunt for leakage first.

## Repository hygiene

- Study code only. No web app, no API, no database, no frontend, no dependency that exists for something other
  than the study.
- Data and results are tracked deliberately: the repository manifest, the aggregated daily-count dataset (if
  its size allows), the results tables, the summary CSVs and the figures are committed so a fresh clone
  reproduces the numbers. Raw per-star timestamps, raw captures and model weights are not. `README.md` states
  exactly what is and is not in the tree. No blanket `*.parquet` or `*.csv` ignore rules.
- `.env` holds tokens (`GITHUB_TOKEN`, cloud credentials); it is never committed, never logged, never printed.
  `.env.example` has names only.
- Any paid or unusual dependency, any cloud spend, any run longer than about an hour, any access to target data
  and any posting outside the repository needs the author's written approval before it happens; the approvals
  are recorded in the evidence packages.
- Before proposing a change, run the test suite, `ruff check` and `ruff format --check` (the commands are in
  `README.md`). The development host is Windows 11 with PowerShell; paths and commands in the documents follow
  it.

## Writing

- Documents in the repository are plain and specific: what was done, what was found, what it means, what was
  not done. No marketing language, no emoji, no phase roadmaps.
- One README, one protocol, one results document, one write-up. Dated research results and decisions go under
  `docs/research/` and `docs/ideas/`, each with a row in `docs/README.md`.

## Commits

- The author commits and pushes. Commit messages have an imperative subject and no trailers. History is never
  rewritten; a correction is a new commit.

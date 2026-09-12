# PulseGraph v2: rules for any coding agent

These apply in every session, whatever the model or tool. Read `HANDOFF.md`
next; it carries the background, the state of the old repository, and the plan.

## Git: read-only, always

- Never run `git add`, `git commit`, `git push`, `git tag`, `git rebase`,
  `git stash`, `git checkout`, `git switch`, `git reset`, `git restore`,
  `git clean`, `git merge`, or anything else that modifies the index, the
  working tree or history. `git status`, `git diff`, `git log`, `git show`
  and `git branch` (listing only) are fine.
- The user commits by hand. When work reaches a point worth committing: run
  `git status`, confirm no secret or data file is untracked (`.env`, anything
  under `data/`, any parquet or CSV that is not meant to be tracked), then
  print the commit as ONE fenced code block containing every `git add` line
  and the `git commit` line, one command per line, no `&&` and no `;`
  chaining, explicit file paths (never `git add -A`, `git add .` or `git add
  -u`), an imperative message, no trailers of any kind (no `Co-Authored-By`,
  no `Signed-off-by`). Then stop and wait until the user says the commit is
  done. Do not continue with work that assumes the commit happened.
- The same applies to `git init`, `git remote add` and the first push: print
  them for the user, do not run them.

## Research integrity

- The v2 experiment is pre-registered. `PROTOCOL.md` is written and committed
  before any evaluation runs on real targets, and the commit hash is recorded
  in the write-up. Nothing in the protocol changes after results are seen; an
  amendment is a dated addition that says what changed and why, never an
  edit in place.
- No look-ahead. Every model sees only data through the cutoff. Any regime
  or cohort label must be computable from data through the cutoff. A test
  proves this.
- No selection on outcomes. Baselines, lookbacks, model revisions, metrics,
  windows and the comparison count are declared before the first run. Extra
  analyses after results are labelled post-hoc and never replace a declared
  one.
- Report either way. A null or negative result is written up with the same
  care as a positive one.
- Every stochastic path is seeded and the seed recorded. Every model is
  pinned to an exact revision hash. Every number in a write-up is traceable
  to a saved artifact and a command that regenerates it.
- Suspiciously good results mean a bug until proven otherwise. Hunt for
  leakage first.

## Repository hygiene

- Study code only. No web app, no API, no database, no frontend, no
  dependency that exists for something other than the study.
- Data and results are tracked deliberately: the repository manifest, the
  aggregated daily-count dataset (if its size allows), the results tables,
  the summary CSVs and the figures are committed so a fresh clone reproduces
  the numbers. Raw per-star timestamps and model weights are not. State in
  the README exactly what is and is not in the tree.
- `.env` holds tokens (`GITHUB_TOKEN`, cloud credentials); it is never
  committed, never logged, never printed. `.env.example` has names only.
- Ask before adding any paid or unusual dependency, before any cloud spend,
  and before any run that will take more than about an hour.
- Windows 11 host, PowerShell primary; give the user Windows paths and
  PowerShell syntax. There is no WSL on this machine (checked 2026-09-12).
  The old repository's data artifacts are on another computer the author no
  longer uses; their recovery is deferred (see `HANDOFF.md`). Python venv is
  `.venv` in the repo root. Run the test suite after each stage.

## Writing

- Documents in the repo are plain and specific: what was done, what was
  found, what it means, what was not done. No marketing language, no emoji,
  no phase roadmaps. One README, one protocol, one results document, one
  write-up.

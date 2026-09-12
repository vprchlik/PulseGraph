# PulseGraph v2: handoff

Written 2026-09-12 by Claude Code (Fable 5.1) from a session in a different
repository, after reading the old repository's `main` branch and its two audit
documents in full. Read `AGENTS.md` first for the standing rules. This file is
the background, the state of everything that exists, and the plan. Nothing
here was run; every number below is quoted from the old repository's own
documents.

### Status update, 2026-09-12

The author confirmed that the June and July 2026 work ran on another computer
they no longer use. The v1 data and result artifacts are unavailable now and
may be retrieved later. Section 6, step 1 (artifact recovery and backup) is
deferred, not failed, and the author authorized proceeding with step 2 under
the fallback in section 2.2. No artifact backup has been made.

The local `v1_reference/` copy retains the v1 documents, tables, metadata and
four figures. The result parquets, summary CSV, saved review outputs and
`data/raw/` files were not found in either local copy. WSL reports that it is
not installed on this machine; the author has corrected AGENTS.md accordingly.
The write-up must disclose reliance on the preserved
documents and figures and that the original results have not been recomputed.
If the artifacts become available, the author will provide their location;
inventory and backup can then resume. Preserve `v1_reference/` while it is
needed for this fallback, including after the code port.

Git is initialized locally on `main`, with origin
`https://github.com/vprchlik/PulseGraph.git`. The author committed and pushed
step 2 as `79718fb` ("Set up PulseGraph v2 and record deferred v1 artifact
recovery"). The initialization commands in section 7 do not need to be repeated.

During step 2, a Python 3.12 environment was created in `.venv/`; the core
and development dependencies installed successfully. Dependency consistency,
imports, in-memory parquet and figure checks, and source/wheel builds passed.
The built packages contain no legacy code, data, secrets or model weights.
The optional model runtimes were not installed or tested. Pytest ran and
collected no tests (exit code 5), because the v2 code and tests have not yet
been ported at that point. No real-target evaluation was run.

### Study-code port, 2026-09-12

Step 3 ports the data loader and supplemental REST ingestion, seven v1 baseline
families, Chronos-2 and TimesFM-2.5 adapters, metrics, a common-calendar backtest,
artifact storage and the seven review commands. The code and offline tests are
under `pulsegraph/`, `scripts/` and `tests/`. The legacy application, database,
graph, explanation and regime modules are not carried over. `v1_reference/`
remains untouched for the deferred-artifact fallback.

Observation bounds and complete coverage must be supplied explicitly; leading,
trailing and all-zero series survive. Model and label inputs stop before the
first forecasted date. Successive maximum-horizon target intervals cannot
overlap. Missing windows and model errors stop the run instead of silently
dropping observations. The forecast seed and model parameters are recorded.

Model adapters require an exact revision hash and load an immutable snapshot;
they have only been exercised with mocked pipelines, not real weights. No actual
model revisions or final comparison set have been chosen. Native quantiles are
retained. Full CRPS and randomized empirical PIT are available only for sampled
forecasts; they are explicitly unavailable for the quantile-only adapters.
The full-distribution CRPS convention must be resolved before the protocol is
frozen. TimesFM-2.5's unsupported 95% interval stays NaN.

Baseline algorithms retain the v1 family limitations described in the README.
Properly seasonal AutoETS, a count-aware baseline with rolling calibration,
additional model adapters, population selection and the real-data runner depend
on the research and registered protocol. The supplied runner accepts synthetic
data only. Its defaults are software-check settings, not pre-registration.

Saved synthetic artifacts contain data, manifests, forecasts, metrics, seeds,
source/package provenance and hashes. Integrity checks recompute the metrics
and summary and require the complete declared model/window grid. Review commands
read stored forecasts; they do not refit or add post-hoc baselines. Their outputs
are explicitly post-hoc. Repository-clustered inference requires an explicit
comparison family and count, and rejects missing pairs.

While verifying the REST adapter API, the current GitHub documentation showed
new stargazer access restrictions and a star-history endpoint. Check these in
the planned research session; no data were requested from either endpoint.
Source: [GitHub starring API documentation](https://docs.github.com/en/rest/activity/starring).

Validation for this port: 93 offline tests pass on Python 3.12. Ruff checks and
format checks pass. Tests include synthetic artifact round trips, all seven
review commands, deliberate corruption/missing-key cases, seed checks and
future-data perturbations. Editable installation and source/wheel builds pass;
the wheel contains the 21 study modules and the source archive also contains
all nine commands and nine test files. No legacy or data files are packaged.
Test artifacts are under `.pytest_cache/` and are
not study results. No v1 reference files were changed and no live data pull,
model-weight download, GPU run or paid-resource request was made.

## 1. What PulseGraph is and why v2 exists

PulseGraph is an empirical forecasting study: do zero-shot time-series
foundation models (Chronos-2, TimesFM-2.5) improve probabilistic forecasts of
daily new-star counts on GitHub repositories, compared with simple and strong
baselines? The series are bursty, zero-inflated, survivor-biased count data of
a kind underrepresented in public forecasting benchmarks, which is the reason
the question is interesting.

Version 1 was built in June and July 2026 with heavy use of agentic coding
tools (Cursor and Claude), produced a complete study, and was then subjected
to an adversarial audit on 2026-07-12. The audit found no code bug that
invalidates the aggregate comparison, but it found that the study design
answers a narrower question than the one it set out to answer, for reasons
that cannot be fixed by rewriting prose. Version 2 is the redesigned,
pre-registered experiment that fixes those reasons, run and reported
whichever way it comes out, plus a short write-up.

The purpose beyond the science: the author is applying to master's programs
in computer science and applied data science with deadlines from 2026-12-01.
PulseGraph is the third research item on that application, after a systems
paper and a statistical-methods paper from two other projects. The
deliverable that matters is a six-page write-up posted to arXiv (cs.LG or
stat.ML), with the story "first result, audit found a design flaw, redesigned
experiment, revised result." A preprint that exists by mid-November is worth
far more than a better experiment that does not. Hard kill date for the
experiment: 2026-11-15. If the v2 result is not in hand by then, the write-up
goes out on v1 plus the audit plus the registered v2 protocol, and says so.

Priority relative to other work: this project is third. If the author says
one of the other two papers is not done, that comes first.

## 2. The old repository, exactly as it stands

- GitHub: `vprchlik/Project-PulseGraph`, public, `main` at commit `7ef49b8`
  ("docs: rewrite README for external GitHub visitors"). Five commits total.
  MIT licence declared in `pyproject.toml`.
- Local clone on this machine: `C:\Users\piano\projects\Project-PulseGraph`,
  on `main`, unmodified. **A copy of that tree (without `.git`) is inside
  this folder at `v1_reference/`**, gitignored, so the agent can read every
  v1 file without leaving the workspace. Treat both as read-only reference.
  Delete `v1_reference/` once the port is done.
- Two remote branches exist and are irrelevant to v2:
  `cursor/cloud-agent-1785467871073-6p2sz` adds a frontend
  `package-lock.json`; `cursor/setup-dev-environment-509d` adds that plus a
  Cursor Cloud `AGENTS.md` about running the legacy web app (FastAPI backend,
  Next.js frontend, a known `/explain` bug under pandas 3). Neither touches
  the study. Do not merge or carry either.

### 2.1 What the tree contains

Study code worth reading and, in parts, reusing:

- `pulsegraph/data/loader.py`: GitHub ingestion and series construction
  (first star through last star, zero-filled between).
- `pulsegraph/forecast/baselines.py`: naive seasonal (horizon-dependent
  period, a known weakness), linear, damped ETS, lag-feature LightGBM, and
  the audit's additions: last value, fixed weekly seasonal naive, 28-day
  local mean. Deterministic per-forecast seeds were added by the audit.
- `pulsegraph/forecast/chronos_forecaster.py`,
  `pulsegraph/forecast/timesfm_forecaster.py`: zero-shot wrappers; both
  reconstruct 200 pseudo-samples per step by inverse-CDF interpolation of
  the native quantiles (Chronos 0.01 to 0.99; TimesFM 0.1 to 0.9, so no 95%
  interval exists for TimesFM-2.5 and the wrapper now emits NaN for it).
- `pulsegraph/evaluation/backtest.py`: walk-forward rolling origin,
  `context = values[:cutoff]`, evaluated `values[cutoff:cutoff+horizon]`;
  the audit confirmed no direct look-ahead.
- `pulsegraph/evaluation/metrics.py`: empirical CRPS (fair finite-sample
  energy form), MAE, coverage with finite-bound handling, randomized PIT
  (added by the audit; the archived run used ordinary PIT, which is invalid
  for tied discrete counts).
- `scripts/ingest_stars.py`, `scripts/run_experiment.py`,
  `scripts/add_timesfm.py` (the TimesFM run was executed separately and
  stitched onto the primary artifact on verified-identical window keys).
- `scripts/review_*.py` (seven audit scripts: integrity, windows, scale,
  strong baselines, local-mean lookbacks, cluster inference, censoring).
  Read-only analyses of the results parquet. Worth carrying.
- `tests/` (six files, 26 tests at the audit's start).
- `README.md`, `RESULTS.md`, `WRITEUP.md` (a draft technical report),
  `STUDY_AUDIT.md` (the completed audit), `AUDIT_HANDOFF.md` (the
  interrupted first pass at the audit, superseded), and
  `reports/pretraining_overlap_audit.md`.

Legacy that must not be carried: `pulsegraph/api`, `pulsegraph/graph`,
`pulsegraph/explain`, `pulsegraph/regime`, `frontend/`, `alembic/`,
`alembic.ini`, `setup.sh`, and every dependency that exists only for them
(fastapi, uvicorn, sqlalchemy, psycopg2, alembic, faiss-cpu, networkx,
google-cloud-bigquery, db-dtypes, plotly, httpx, pydantic-settings).
`timesfm` is used by the study and is not even listed in `pyproject.toml`.

### 2.2 The data and results are not in the repository

`.gitignore` excludes `*.parquet`, `*.csv`, `*.json.gz` and `data/`. So a
fresh clone has none of: the raw per-star timestamps, the daily-count panel,
`experiment_real_full_results.parquet` (24,732 rows, six models on 4,122
repository x horizon x cutoff keys), `experiment_real_full6_summary.csv`,
or any of the `review_*` outputs. `reports/` in the tree holds three meta
JSONs, four PNG figures and the overlap audit, and that is all. The README's
statement that stored artifacts reproduce the published numbers without
re-ingesting is false for anyone but the original machine.

Per `AUDIT_HANDOFF.md`, the working copy with the artifacts lived at
`/home/vprchlik/projects/PulseGraph` on a Linux environment, with a sibling
worktree `../PulseGraph-kronos` (a separate out-of-domain transfer
experiment using the Kronos model; the audit says to keep it separate from
the main result). **Checked 2026-09-12: no WSL distribution is installed on
this Windows machine**, so that copy is on another machine or a WSL install
that no longer exists. Ask the author where the June and July 2026 work was
done.

**First action of the v2 session, before any code:** with the author, locate
that working copy and confirm which of these exist: the results parquet,
the summary CSV, the seven review outputs, the raw stargazer data under
`data/raw/`, and `data/raw/daily_signals.parquet`. Copy them to a backup
outside any git tree (the author chooses where). They are the only copy of a
study that consumed real GPU time and GitHub API budget, and the v2 write-up
needs them for its v1 half. If they are gone, v1 exists only as its tables and
figures; that is survivable but must be stated in the write-up.

### 2.3 What v1 found

Data: 208 repositories ingested via three GitHub Search API queries
(breakout-selected: recently created and already high-starred;
steady-selected: old, moderate, recently maintained; dead-selected: not pushed
in years), 414,271 daily rows, span 2008-11-13 to 2026-06-22, 179 usable with
at least 270 days (41 / 69 / 69). Backtest: expanding context from 180 days
after the first star, step 30 days, at most eight windows per repository,
horizons 7, 30, 90 days, 200 predictive trajectories per model.

Primary CRPS (lower is better), breakout-selected cohort:

| H | naive | linear | ets | lightgbm | chronos2 | timesfm |
|---|---|---|---|---|---|---|
| 7 | 11.82 | 11.19 | 12.59 | 14.82 | 6.43 | 6.23 |
| 30 | 13.32 | 16.69 | 18.11 | 19.40 | 7.90 | 7.68 |
| 90 | 14.55 | 28.00 | 23.99 | 23.33 | 8.52 | 8.20 |

Both foundation models have lower mean CRPS than every original baseline in
all nine cohort x horizon cells. TimesFM-2.5 has lower CRPS than Chronos-2 in
8 of 9 cells and lower MAE in 9 of 9.

After the audit added a 28-day local-mean baseline on identical windows, the
foundation models still win every cell on the mean, but per-repository win
rates fall to 40.6 to 80.5 percent, and repository-clustered paired tests
with FDR control find reliable typical-repository gains in the
breakout-selected and dead-selected cohorts and none in the steady-selected
cohort. Macro (equal-repository) rankings preserve a foundation-model winner
in every cell; removing any single repository never flips a cell; but the
five largest positive contributors account for 30 to 77 percent of the
positive gain depending on cell. The honest headline: the gain is robustness
against a minority of large misses, not uniform superiority.

### 2.4 What the audit found that v2 must fix

Invalidating for the original claims:

1. Cohorts are outcome-conditioned. Breakout was selected for already having
   high stars; dead for later inactivity; steady for later maintenance. The
   labels are not available at forecast time. Dead-selected evaluation
   windows have a median 5.02 stars per day and only 7.7 percent zero days:
   they are not dead when evaluated.
2. The windows mostly test post-peak decay. The global peak precedes the
   evaluated span for 78.0 percent of breakout-selected repositories; only
   12.2 percent peak inside it. So "foundation models win on breakout series"
   means "they forecast early post-viral decay of repositories selected for
   having already broken out." The study does not test shock prediction.

Must-disclose issues the audit already handled in v1's text and code, which
v2 designs out from the start: the strawman original baseline set; Wilcoxon
tests on overlapping windows treated as independent; untested scale
domination; the TimesFM 95 percent interval mislabel; ordinary PIT on
discrete counts; unseeded baseline sampling; LightGBM's uncertainty from
in-sample residuals around one deterministic path; MAPE as a headline metric
on zero-inflated series; implicit observation endpoints (first star to last
star, so trailing zeros are censored; the stargazers endpoint also omits
stars later removed); and unresolved pretraining contamination (no disclosed
GitHub-derived corpus in either model card, but no clean post-release
holdout either, and no 270-day-eligible repository was created after either
model's release at the time of v1).

The audit's own prescription for a defensible paper, which is the v2 spec:
freeze and pre-register; context-only cohort labels or a formally defined
post-launch-decay task; trailing non-overlapping windows with a common
observation endpoint; strong pre-registered classical and count-aware
baselines; native quantile metrics; repository-clustered inference; a
prospective post-release cohort as the contamination control.

## 3. The new repository

- GitHub: `vprchlik/PulseGraph`, created 2026-09-12, public, empty (no
  README, no `.gitignore`, no licence chosen at creation).
- Licence, decided 2026-09-12: **MIT** for the code (`LICENSE` in this
  folder; continuity with v1 and the licence a reviewer expects). When the
  aggregated dataset and the write-up exist, they carry **CC BY 4.0**, stated
  in the README's licence section; arXiv asks for that choice at submission.
  `pyproject.toml` declares `license = {text = "MIT"}`.
- Local: `C:\Users\piano\projects\PulseGraph` (this folder), the agent's
  workspace. It holds `AGENTS.md`, this file, `LICENSE`, `.gitignore` and the
  gitignored `v1_reference/`. It may not yet be a git repository; the
  initialisation commands are printed for the author at the end of this
  file; do not run them.
- Keep the old repository public and, once v2 has a README, ask the author
  to archive it on GitHub with one line at the top of its README pointing
  here and stating that the v1 artifacts are not in its tree.

## 4. Decisions already taken

- New repository, not a cleanup of the old one: the experiment is a
  redesign, the legacy modules add nothing, model versions have moved, and
  a clean history reads better than one that begins with a full-stack
  scaffold.
- Study code only in the tree. Carry over, after reading and testing:
  the ingestion and series-construction logic, the baseline family, the
  two foundation-model wrappers (re-pinned), the backtest harness, the
  metrics (randomized PIT, finite-bound coverage), the seven review
  scripts adapted to the v2 artifact, and the tests. Rewrite anything
  that carries a legacy import.
- The write-up is the deliverable. Six pages: the v1 result, the audit,
  the v2 protocol, the v2 result, limitations. The v1 audit material is
  already written and only needs condensing.
- A research session (a claude.ai chat with research mode, prompt in the
  appendix) runs before the protocol is frozen, to learn what changed in
  the model landscape since July 2026 (TimesFM 3 is out; Chronos-2 may have
  revisions; other zero-shot models have appeared), what each model's
  disclosed training cutoff is (which sets the prospective cohort date),
  and what the current evaluation standards are. Its output feeds the
  protocol; it does not replace it.

## 5. The v2 design, to be written into PROTOCOL.md before any run

1. **Population, not search results.** Daily star counts for the whole
   population from GH Archive `WatchEvent`s on BigQuery, rather than the
   Search API's ranked, threshold-selected list. This removes the
   outcome-conditioned cohort problem at the source and the survivor bias
   of the stargazers endpoint. Define the universe by a rule stated before
   the pull (for example: repositories created in a fixed window with at
   least N stars by day 90, sampled uniformly within strata defined on
   day-90 data). Confirm BigQuery cost with the author before the pull;
   it is a paid resource.
2. **Context-only regimes at each cutoff**, or drop regimes for a formally
   defined post-launch-decay task. Any label must be computable from data
   through the cutoff date, and a test proves it.
3. **Trailing, non-overlapping windows** with a common observation endpoint
   (the snapshot date) so real zeros survive. Declare the window calendar.
4. **A prospective cohort** of repositories created after every evaluated
   model's disclosed training cutoff, evaluated identically, as the
   contamination control. The research session supplies the dates.
5. **Frozen model revisions**: Chronos-2 (pinned Hugging Face revision),
   TimesFM 3 (pinned), TimesFM-2.5 for continuity with v1, plus whatever
   the research session identifies as the current strong zero-shot models.
   Record exact revision hashes. No model added after results are seen.
6. **Baselines fixed in the protocol**: last value, weekly seasonal naive,
   local mean with the lookback grid declared, properly seasonal AutoETS,
   and one count-aware probabilistic model (negative-binomial state space
   or similar) calibrated on rolling residuals. No post-hoc baselines.
7. **Metrics**: CRPS, weighted quantile loss on common supported quantiles,
   interval score at 80 percent, MASE or RMSSE, per-repository skill;
   randomized PIT for calibration. No MAPE.
8. **Inference**: repository-clustered bootstrap, paired tests across
   repositories, FDR over the declared comparison count. Declare the count.
9. **Report either way.** If the advantage disappears under the corrected
   design, that is the result, and it is a better result for the purpose
   than a confirmed win, because it shows the audit mattered.

Compute: the foundation models on a few hundred repositories x a handful of
windows x three horizons run in hours on a modest GPU and overnight on CPU.
Ask the author what hardware is available before planning the run. Budget:
two to three weeks including the write-up, inside the kill date.

## 6. Suggested order of work

1. Locate and back up the v1 artifacts (section 2.2). Report what exists.
2. Initialise the repository (commands below, printed for the author), add
   `pyproject.toml` with study dependencies only and `README.md` stating the
   project, its status and what is and is not in the tree. `.gitignore`
   exists; extend it rather than replacing it, and never add blanket
   `*.parquet` or `*.csv` rules (that is how v1 lost its artifacts).
3. Port the study code with tests; suite green before anything else.
4. Run the research session; fold its findings into `PROTOCOL.md`; get the
   author's sign-off; commit the protocol; record the hash.
5. Data pull (with cost confirmed), then the frozen experiment, then the
   declared analyses, then the write-up.

## 7. Initialisation commands (for the author to run; the agent prints, never runs)

```powershell
cd C:\Users\piano\projects\PulseGraph
git init
git branch -M main
git remote add origin https://github.com/vprchlik/PulseGraph.git
```

Then, once `README.md` exists and `git status` shows nothing sensitive
(`v1_reference/` must not appear; it is gitignored):

```powershell
git add AGENTS.md
git add HANDOFF.md
git add README.md
git add .gitignore
git add LICENSE
git commit -m "Initialise PulseGraph v2 with the agent rules, the handoff and the MIT licence"
git push -u origin main
```

## Appendix: research prompt for the "what changed" session

Paste into a claude.ai chat with research mode. One run is enough.

---

I ran an empirical study in mid-2026 comparing zero-shot time-series
foundation models (Chronos-2, TimesFM-2.5) against baselines for
probabilistic forecasting of daily GitHub new-star counts: bursty,
zero-inflated, survivor-biased count series. An audit found the cohort design
used future information, and I am redesigning the study as a pre-registered
v2. Before I freeze the protocol I need to know what has changed since about
July 2026 and what the current standard is. Please research the following and
cite sources with dates.

1. **Models.** The current set of zero-shot time-series foundation models
   worth including: TimesFM 3 (release date, sizes, what changed from 2.5,
   whether the quantile head now supports arbitrary quantiles including 0.025
   and 0.975, disclosed training corpora and cutoffs), Chronos-2 (latest
   revision, any post-October-2025 updates, disclosed corpora), and the other
   current contenders (Moirai and Moirai-MoE, Sundial, TiRex, Toto, TabPFN-TS,
   Time-MoE, any 2026 releases). For each: parameters, licence, whether it
   produces quantiles natively, and its position on GIFT-Eval and fev-bench
   leaderboards as of now.
2. **Contamination.** For each model, whether any disclosed training source
   plausibly contains GitHub-derived series (GH Archive, star histories,
   package-download series) and the latest real-data cutoff date stated by
   the authors. I need this to define a prospective cohort of repositories
   created after every model's cutoff.
3. **Data.** The current state of GH Archive on BigQuery (schema for
   WatchEvent, known gaps or outages in 2025-2026, cost of pulling daily star
   counts for all repositories over a multi-year window), and any maintained
   alternative (star-history services, Kaggle or HF datasets of daily star
   counts, the GitHub Innovation Graph). Also whether the stargazers REST
   endpoint still returns per-star timestamps and its current rate limits.
4. **Prior work on this exact task.** Papers on forecasting GitHub stars or
   repository popularity, and on bursty attention dynamics generally (Hawkes
   and self-exciting models, SEISMIC-style cascade prediction, Wikipedia
   pageview forecasting). Has anyone published a benchmark of foundation
   models on bursty or zero-inflated count series, and what did it find?
5. **Methods standards.** The current accepted practice for probabilistic
   evaluation of count forecasts: randomized PIT, weighted quantile loss and
   interval score conventions in GIFT-Eval and fev, MASE and RMSSE
   definitions, and clustered inference for panel backtests. Any 2025-2026
   paper criticizing foundation-model benchmarks for leakage or weak
   baselines, and what baselines it recommends.
6. **Count-aware baselines.** The current best simple probabilistic baselines
   for intermittent or zero-inflated daily counts with available Python
   implementations: negative-binomial state space, Tweedie GBMs, Croston
   variants, AutoETS with weekly seasonality, and whether statsforecast or
   sktime provides them with prediction intervals.

Output: one section per item with sources, then a short "what this changes"
list against the design above: which models to freeze, what the prospective
cutoff date must be, which baselines to declare, and anything in the design
that is now outdated. Flag where the record is thin.

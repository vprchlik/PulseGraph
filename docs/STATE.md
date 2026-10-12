# PulseGraph: the current state

Last rewritten 2026-10-12 21:30 UTC, from the files alone. Two screens at most; history is in
`docs/HISTORY.md` and the dated documents.

## The deliverable

Two steps, in parallel from 2026-10-12. Step one: a small paper-level report of Study 1 posted with a citable
DOI by **2026-10-24**. Step two: the paper proper, the report plus the Study 2 mechanism test on npm and the
registered synthetic grid, posted and submitted to TMLR by **2026-10-31**. 2026-11-15, the old kill date, is
the fallback only if the npm source fails. Anything not run by the paper's date is reported as not run.

## Committed

`main` is at `54f24db` (2026-10-12 04:18 UTC), ten commits, pushed. Since 2026-10-12 the root carries
`CONTRIBUTING.md`, `docs/` holds the project pages, and `README.md` states how the project was built. The tree
holds the ported study code and 170 Study 1 offline tests; the registered protocol (`5f01769`, Study 1; `df55867`,
Study 2 appended); the registered run's evidence package under `reports/registered-2026-09-13/` (manifest,
frame, skips, validation, readiness, run metadata, inference, descriptive tables); `RESULTS.md` with the 18
confirmatory rows and the declared descriptive tables. The 433,172,286-byte `results.parquet` is not in the
tree; `README.md` says its release URL is to be filled, and no release exists yet.

## Verified on 2026-10-12, awaiting the author's commit

Two bodies of work from 2026-09-14, re-verified on 2026-10-12 (every provenance and smoke hash matches; ruff
clean; 241 of 241 tests pass once pytest's temporary directory is moved away from `.pytest_cache`, whose
access list denies access on this machine; the post-hoc directory is 67 MB, 18 MB of it SVG figures):

| Work | Paths | Companion edits |
|---|---|---|
| Post-hoc QScore9 accounting of the saved Study 1 run (zero-day, positive-over, positive-under parts; 102 cells; 36 figures; provenance with hashes) | `reports/registered-2026-09-13/posthoc/` (50 files) | `RESULTS.md` +10 lines |
| Study 2 implementation: ingestion, CDF completion, hurdles, dynamic count, gate, holdout writer, synthetic grid, 71 offline tests, declarations and smoke evidence | `pulsegraph/study2/` (12), `scripts/study2_*.py` (6), `study/study2/` (13), `tests/test_study2_*.py` (7) | `README.md` +124 lines |

Also awaiting the same commit, all written 2026-10-12: the dated protocol addition for the lapses (items 1 to
3, appended 09:20 UTC on top of `54f24db`; the registered prefixes verified twice; 62,111 bytes); the
literature re-check (`docs/research/2026-10-11-literature-recheck.md`); the Study 1 report under `paper/`
(LaTeX source, three figures, the number sources, a checker that passes 181 checks; no PDF, since no TeX is
installed).

## What the protocol allows, and what lapsed

- Study 1 is closed. Anything computed from its saved run is post-hoc and labeled so.
- Study 2 is registered: 54 external tests (three domains), 6 synthetic, 18 prospective; one BH per family;
  no run before a signed gate at the committed implementation with GPU smoke at that HEAD.
- **Lapsed, and recorded by the dated addition of 2026-10-12:** the October holdout (freeze 2026-09-28 passed
  with nothing frozen) is reported as not run; the npm readiness clock is reset once, to 2026-10-20 23:59 UTC,
  with the PyPI rule unchanged after that; the October paper's external family is E01 to E18 with one BH
  correction, E19 to E54 kept whole for a later run. All three were decided before any Study 2 target was
  seen (`study/study2/acquisition_status.json`: targets opened false, forecasts generated false).
- The implementation's external gate still requires a completed holdout freeze and all three domain panels;
  the addition says both change in a commit that cites it. That commit is still to be made.
- The November prospective round was not taken on 2026-10-12; it can still be registered by a separate dated
  addition before 2026-10-28 18:00 UTC.
- The birth-cohort census is approved but needs a BigQuery dry run and cost approval; the fine-tune is
  inactive; the write-up may start before 2026-10-20.

## What the report can say today

Panel: 148,550 eligible repositories created 2023-01-01 to 2025-02-21; 300 accepted, 100 per day-90 stratum;
470 skipped (mostly gone at fetch time); counts from the star-history endpoint through 2026-08-31 in
America/Los_Angeles days, validated hourly against GH Archive 2024. Against `local_mean_28`: the mean
difference favors the models in all nine cells and its bootstrap interval excludes zero in five; the typical
repository favors the reference (models lower on 46 to 89 of 300; the signed-rank test favors the reference in
all nine cells at BH q=0.05). Against `autoets_weekly`: models lower on 293 to 298 of 300, with AutoETS's 80%
intervals covering about 0.99. Post-hoc: the zero-day penalty is small; the mean gain against the local mean
sits on positive days where the local mean overpredicts after bursts. v1 numbers are quoted from the preserved
documents, not recomputed; the v1 artifacts are on a computer the author no longer uses.

## What the Study 2 code has and has not been exercised on

Exercised: 71 offline tests (mocked models, leakage spies, CDF and CRPS checks) as of 2026-09-14; one
synthetic GPU smoke on 2026-09-14 17:31 UTC at HEAD `df55867` (passed; peak reserved VRAM 2.95 GB; about 382
seconds projected for 300 GitHub series at one origin); the CRPS tail certificate. NYC 311: a 2024 inventory
of 9,496 cells captured, context pull failed on transport. npm: a probe counting 4,389,348 registry documents,
no creation metadata, no download request. Wikipedia: nothing acquired. **Never exercised:** any real
forecast, any target value, any achieved external panel, the gate at a committed HEAD.

## What the literature re-check found (2026-10-12)

No published evaluation of the registered construction (a context-only occurrence probability replacing a
frozen model's zero mass, the completed positive law kept, judged by a proper quantile score against a
completed-unwrapped control and matched count hurdles on sparse daily counts) was found. Six items since
September must be cited and narrow the claim: a hurdle on frozen Chronos-2 output for monthly spare parts
(2026-09-12), an event-ranking evaluation of twelve frozen models on sparse daily panels, a simulation with
TimesFM 3 on intermittent demand, an aggregate-versus-per-series ranking study, a temporal-holdout familiarity
study, and a live GitHub-activity benchmark. The paper may claim the registered combination on daily attention
and adoption counts, and nothing broader.

## Next steps

The author's commit of everything above; then, in parallel: the report reviewed by a different reader and
revised with the six citations; the npm panel built under the registered rules (deadline 2026-10-20); the
synthetic grid's smoke, gate and run. Dates and gates are in `docs/PLAN.md`. The machine has no pandoc, TeX
or GitHub CLI; Python 3.12 in `.venv`; 216 GB free.

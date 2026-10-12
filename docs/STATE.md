# PulseGraph: the current state

Last rewritten 2026-10-12 04:10 UTC, from the files alone. Two screens at most; history is in
`docs/HISTORY.md` and the dated documents.

## The deliverable

Two steps, in parallel from 2026-10-12. Step one: a small paper-level report of Study 1 posted with a citable
DOI by **2026-10-24**. Step two: the paper proper, the report plus the Study 2 mechanism test on npm and the
registered synthetic grid, posted and submitted to TMLR by **2026-10-31**. 2026-11-15, the old kill date, is
the fallback only if the npm source fails. Anything not run by the paper's date is reported as not run.

## Committed

`main` is at `df55867` (2026-09-14 16:15 UTC), eight commits, pushed; `origin/main` is equal. The tree holds
the ported study code and 170 Study 1 offline tests; the registered protocol (`5f01769`, Study 1; `df55867`,
Study 2 appended); the registered run's evidence package under `reports/registered-2026-09-13/` (manifest,
frame, skips, validation, readiness, run metadata, inference, descriptive tables); `RESULTS.md` with the 18
confirmatory rows and the declared descriptive tables. The 433,172,286-byte `results.parquet` is not in the
tree; `README.md` says its release URL is to be filled, and no release exists yet.

## Uncommitted, untouched since 2026-09-14 17:32 UTC (27 days)

Two bodies of work, both verified on 2026-09-14 and never committed:

| Work | Paths | Companion edits |
|---|---|---|
| Post-hoc QScore9 accounting of the saved Study 1 run (zero-day, positive-over, positive-under parts; 102 cells; 36 figures; provenance with hashes) | `reports/registered-2026-09-13/posthoc/` (50 files) | `RESULTS.md` +10 lines |
| Study 2 implementation: ingestion, CDF completion, hurdles, dynamic count, gate, holdout writer, synthetic grid, 71 offline tests, declarations and smoke evidence | `pulsegraph/study2/` (12), `scripts/study2_*.py` (6), `study/study2/` (13), `tests/test_study2_*.py` (7) | `README.md` +124 lines |

The whole suite collects 241 tests; none has been run since 2026-09-14. On 2026-10-12 the three root files of
September 2026 (the coding-agent rules, the agent notes and the setup handoff) leave the tree:
`CONTRIBUTING.md` carries the research-integrity and repository rules for anyone who changes the repository,
and `docs/HISTORY.md` the project history.
`README.md` also carries a new section, "How this project was built", awaiting the author's approval before
it is committed.

## What the protocol allows, and what lapsed

- Study 1 is closed. Anything computed from its saved run is post-hoc and labeled so.
- Study 2 is registered: 54 external tests (three domains), 6 synthetic, 18 prospective; one BH per family;
  no run before a signed gate at the committed implementation with GPU smoke at that HEAD.
- **Lapsed:** the October holdout's freeze (2026-09-28 18:00 UTC) passed with nothing frozen; no backdating is
  allowed; it is reported as not run. The npm-or-PyPI decision date (2026-09-28) passed with npm never
  attempted beyond a 2026-09-14 metadata probe; by the rule's own words this is not a source failure.
- Nothing in the protocol lets the external family shrink to one domain except the holdout's npm rule, so
  running npm alone for the paper needs a dated addition made before any Study 2 target is seen. No target
  has been seen (`study/study2/acquisition_status.json`: targets opened false, forecasts generated false).
- The implementation's external gate requires a completed holdout freeze and all three domain panels; the
  protocol text requires neither. Both change in a commit that cites the additions.
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

## Next steps

In order of start, all from 2026-10-12: commit the two uncommitted bodies after their tests run; append the
dated protocol additions for the lapses with the author's sign-off; start the Study 1 report under `paper/`;
repeat the literature search narrowly for work since 2026-09-13; build the npm panel under the registered
rules (deadline 2026-10-20 by the addition); run the registered synthetic grid. Dates and gates are in
`docs/PLAN.md`. The machine has no pandoc, TeX or GitHub CLI; Python 3.12 in `.venv`; 216 GB free.

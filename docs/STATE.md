# PulseGraph: the current state

Last rewritten 2026-10-16 03:40 UTC, from the files alone. Two screens at most; history is in
`docs/HISTORY.md` and the dated documents.

## The deliverable

Two steps, in parallel from 2026-10-12. Step one: a small paper-level report of Study 1 posted with a citable
DOI by **2026-10-24**. Step two: the paper proper, the report plus the Study 2 mechanism test on npm and the
registered synthetic grid, posted and submitted to TMLR by **2026-10-31**. 2026-11-15, the old kill date, is
the fallback only if the npm source fails. Anything not run by the paper's date is reported as not run.

## Committed

`main` is at `f0c28a8` (2026-10-13 05:04 UTC), seventeen commits, pushed. Since 2026-10-12 the root carries
`CONTRIBUTING.md`, `docs/` holds the project pages, and `README.md` states how the project was built. The tree
holds the ported study code and 170 Study 1 offline tests; the registered protocol (`5f01769`, Study 1; `df55867`,
Study 2 appended); the registered run's evidence package under `reports/registered-2026-09-13/` (manifest,
frame, skips, validation, readiness, run metadata, inference, descriptive tables); `RESULTS.md` with the 18
confirmatory rows and the declared descriptive tables. The 433,172,286-byte `results.parquet` is not in the
tree; `README.md` says its release URL is to be filled, and no release exists yet.

## Committed on 2026-10-12 and 2026-10-13

The post-hoc accounting of the Study 1 run (`a3b3098`); the Study 2 implementation and its 71 offline tests
(`fab6f7a`); the dated protocol addition for the lapses (`8db0d73`, items 1 to 3; registered prefixes verified
twice; 62,111 bytes); the literature re-check (`63c2d5f`); the Study 1 report under `paper/` (`c62d0c5`); its
review (`f0c28a8`, 45 verdicts: 18 hold, 26 fixed, 1 did not hold).

## The two Study 2 runs of 2026-10-15

**Synthetic grid** (committed `f950300`): the registered 540-series grid, one invocation at `3fc3411`, every
score recomputed with zero difference, the oracle lowest in 17 of 18 cells. The family S01 to S06 is adverse
to the hurdle: worse than its completed control for all three models (S01, S03, S05) and worse than the count
hurdle for Chronos-2 and TimesFM 2.5 (S02, S06); five of six reject at BH q = 0.05, all against the hurdle.

**npm external run** (awaiting the author's commit): the 209 target ranges were opened 2026-10-15 23:15 UTC
under the signed gate (209 of 300 approved requests, no retry); the run took 699 s of a 3,600 s budget; the
committed inference and the per-row recomputation (0 of 20,064 disagree) ran unchanged. The family E01 to E18:
twelve of eighteen reject, ten for the model variant and two against the hurdle. Hurdle against its completed
control: no row favors the hurdle, two reject against it (TimesFM 3 and TimesFM 2.5 at horizon 30). Hurdle
against the count hurdle: all six favor the foundation model's positive law (lower on 115 to 161 of 209
series). Raw model against the local mean: four of six favor the model. Every mean is carried by one series
(`aggregate-error`, 7.6 million downloads a day); the medians, counts and rank tests describe the typical
series. Results: `reports/study2-npm/run-2026-10-15/RESULTS-npm.md`; the 209 checkpoints stay out of the tree.

**Open: two zero days.** The download API reports 0 for all 209 series on 2026-07-12 and 2026-08-14, and 0 for
the largest series on 2026-06-25, between days of millions; no context day shows this. The registered
completeness rule accepted them as explicit zeros and the run scored them so; each sits in one horizon-30
window, none in a horizon-7 window. The recommendation is to keep the registered analysis as served, record
the decision by a dated addition, and report a post-hoc sensitivity without the three days beside it.

Also awaiting the same commit: the integrity outputs of both runs, the fresh smoke and the signed readiness
copies. The paper's Study 2 design sections are committed (`3652a4a`).

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
intervals covering about 0.99. Post-hoc: the zero-day part is small beside the mean gain (0.004 to 0.015, though larger than every
median difference); the mean gain against the local mean sits on positive days where the local mean
overpredicts. v1 numbers are quoted from the preserved
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

The commit above; the author's decision on the zero days with the source evidence and the post-hoc
sensitivity; the paper's results sections and the extension of the report into the paper; the author's read
of the report's title, abstract and summary; the PDF (no TeX on this machine); the GitHub release and the
release assets for the checkpoints. Dates and gates are in `docs/PLAN.md`.

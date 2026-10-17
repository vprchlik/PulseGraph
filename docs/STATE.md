# PulseGraph: the current state

Last rewritten 2026-10-17 08:35 UTC, from the files alone. Two screens at most; history is in
`docs/HISTORY.md` and the dated documents.

## The deliverable

Two steps, in parallel from 2026-10-12. Step one: a small paper-level report of Study 1 posted with a citable
DOI by **2026-10-24**. Step two: the paper proper, the report plus the Study 2 mechanism test on npm and the
registered synthetic grid, posted and submitted to TMLR by **2026-10-31**. 2026-11-15, the old kill date, is
the fallback only if the npm source fails. Anything not run by the paper's date is reported as not run.

## Committed

`main` is at `2bae238` (2026-10-17 07:31 UTC), 54 commits, pushed. Since 2026-10-12 the root carries
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

**npm external run** (committed `26a8913`): the 209 target ranges were opened 2026-10-15 23:15 UTC
under the signed gate (209 of 300 approved requests, no retry); the run took 699 s of a 3,600 s budget; the
committed inference and the per-row recomputation (0 of 20,064 disagree) ran unchanged. The family E01 to E18:
twelve of eighteen reject, ten for the model variant and two against the hurdle. Hurdle against its completed
control: no row favors the hurdle, two reject against it (TimesFM 3 and TimesFM 2.5 at horizon 30). Hurdle
against the count hurdle: all six favor the foundation model's positive law (lower on 115 to 161 of 209
series). Raw model against the local mean: four of six favor the model. Every mean is carried by one series
(`aggregate-error`, 7.6 million downloads a day); the medians, counts and rank tests describe the typical
series. Results: `reports/study2-npm/run-2026-10-15/RESULTS-npm.md`; the 209 checkpoints stay out of the tree.

**The zero days, settled by dated addition 6 (2026-10-16).** The download API reports 0 for all 209 series
on 2026-07-12 and 2026-08-14, and 0 for the largest series on 2026-06-25, between days of millions; npm's own
records report nothing for those dates, though its forum records two earlier whole-day zeros later restored.
The registered analysis of the data as served stands. A post-hoc sensitivity from the saved forecasts: with
all three days removed none of the eighteen conclusions changes; with the two panel-wide days removed, E06
(Chronos-2 raw against the local mean at horizon 30) no longer rejects (BH p 0.060) and the other seventeen
are unchanged. The mechanism answer does not depend on the days.

Addition 6, the sensitivity and the evidence are committed (`1c09ac8`).

## The paper (committed `c330315`; its review `8250599`; the three reads `04e92c1`; its revision `5720c05`)

`paper/paper.tex`, written 2026-10-16: the report's text, now read from shared files that the report's own
`main.tex` also reads (its expansion equals the committed report byte for byte), extended with the Study 2
question, design, panel, both results, a discussion, limitations and reproducibility; 654 number checks pass;
two new figures from the saved tables; the ten arXiv citations' titles and authors filled from their abstract
pages. Its title, abstract and the three sentences to read are in `paper/PAPER-SUMMARY.md`. No PDF yet: no TeX
on this machine. Its review (45 verdicts: 17 hold, 26 with a fix, 2 do not hold) found every number traced
and no table entry wrong, and sentences that overclaim: "no comparison favors the substitution" is false for
E01, where the typical series favors the hurdle; the claim's scope is npm downloads and the grid, not
"attention and adoption counts"; the dynamic count's occurrence rule is misdescribed; S04 is not a tie. The
standing check and referee's read (2026-10-16) found the tables right and the framing wrong: the confirmatory
families speak for the dense regime, while the declared secondary strata show the substitution lower than its
control on 81, 60 and 66 of the 100 sparse npm series at horizon 7; the positive law is a truncated marginal;
the count-hurdle win is a win over a shifted Poisson; the dynamic count is the best non-oracle forecaster on
the grid. Its verdict: post after named changes. The post-hoc dynamic-occurrence wrapper shrinks the loss,
removes four of five rejections against the substitution, and still never beats the model's own zero mass.
The decision to make the regime reading confirmatory by a third study is in `docs/ideas/2026-10-16-study3-regime-test.md`.

The revision of 2026-10-16 (`5720c05`) applies all three reads. The abstract and the results now
say that no test favors the substitution at q = 0.05, that the typical series in E01 leans to it, and that the answer
depends on the regime: the declared secondary stratum counts are the paper's central descriptive finding, labeled
secondary, with a registered test on a second domain named as the next study. The claim is narrowed to daily npm
download counts and the registered grid; the positive-law result names the shifted Poisson it beats and puts the
empirical hurdle beside it, labeled post hoc; the fourth factorial cell is named as untested; the dynamic count is
read as the best non-oracle forecaster on the grid; the post-hoc dynamic-occurrence analysis has a labeled subsection
with one table. Nine citations were added from their abstract pages. The checker passes 780 checks (654 before) and
reads its boundary vocabulary from a file outside the tree. The report's source still expands to its frozen commit
`f325a67` apart from one dated sentence in Section 8, which now says that both Study 2 components ran on 2026-10-15.
Still no PDF. By word count the body is about seventeen pages before the references against an aim of fourteen; the
next cuts each remove a stated number and are the author's choice (`paper/PAPER-SUMMARY.md`).

**Extended with Study 3 (2026-10-17; committed `6220211`).** The title and abstract name three registered
studies; a Study 3 part (question, design, panel, results) follows Study 2's results, with its detail in two appendix
sections; the discussion is rewritten for three studies: for dense series a context-only or dynamic occurrence estimate
does not improve the model's own completed zero mass under this score, on npm, the grid and NYC 311, confirmatory on two
domains; for sparse series the question is open, with the npm secondary reading on one side and the NYC 311 family on
the other and two readings given equal weight (a smaller benefit, or a score blind to it where both forecasts put every
decile at zero). The fourth factorial cell, run on NYC 311 as a secondary, is far worse than the control on dense series.
The Study 2 post-hoc regime material is compressed to one paragraph each with its tables in the appendix. The checker
passes 1,195 checks (780 before); the report's source still expands to `f325a67` apart from its one dated sentence. By
word count the body is now about 15,800 words with ten tables and four figures, about 24 pages before the references:
the three cuts that remain the author's (the literature paragraph, the Study 2 design section, the Study 2 limitation
items) would bring it to about 13,300 words, and moving the two Study 3 family tables to the appendix beside the figure
to about 12,900.

**Its two reads (2026-10-17).** The line-by-line review (`docs/research/2026-10-17-paper-study3-review.md`): every
number holds and no table entry changed; of 45 verdicts 21 hold, 17 hold with a fix and 7 do not hold, the seven being
sentences, four of them the discussion's claims about Study 3 ("confirmatory on two domains", where npm has no
registered dense test; the two readings "with equal weight", where on NYC 311's sparse stratum the score does separate
the forecasts and the blind-score reading fits the very sparse stratum only; the accounting sentence, wrong for the
TimesFM models; the fourth-cell sentence, which contradicts itself); the family table does not fit the text width.
The step-back read against the field (`docs/research/2026-10-17-paper-shape-review.md`): credible in its record,
not yet comparable in its shape. The intermittent-demand methods are neither run nor cited and the registered
baselines are classical count models under other names; and the completion rule gives every all-zero-decile forecast
an occurrence probability between 0.0607 and 0.1 whatever the model said, with 580, 544 and 588 of the 600 very sparse
completed forecasts on that floor, so the very sparse contrast compares a context estimate with the completion rule,
not with the models. The argument it finds underneath the chronicle: the models' value is in the size of positive
days; their own zero mass is at least as good as a context estimate wherever nine quantiles can express one; and on
series zero nine days in ten neither the models nor the score can say anything about occurrence. Its verdict, adopted:
one paper to TMLR by 2026-10-31 with a body of about twelve pages organized by question; no fourth study as proposed
(its dense half would repeat a confirmed result, its very sparse half would confirm the completion rule, its sparse
half is underpowered on NYC 311), with a narrow npm replication kept in the deferred register; the intermittent-demand
baselines as a post-hoc descriptive benchmark from the saved forecasts, its specification fixed before any score is
read.

**The post-hoc benchmark (2026-10-17 08:01 UTC; awaiting the author's commit).** From the saved forecasts of all
three runs, with its specification fixed at 07:44 UTC before any score existed
(`reports/study2-posthoc-intermittent-baselines/`): a TSB hurdle, the registered count hurdle with TSB's occurrence
and size estimates in place of the 28-day ones, is far behind every model on dense series (lower than the models'
completed forecasts on 18 or 19 of 100 dense npm series at a week and on 19 to 22 on NYC 311), level with the
registered count baselines, ahead of the models for the typical sparse npm series at a week (77, 61 and 74 of 100)
and tied with the count hurdle there, and on the completion floor with everything else on very sparse series. The
field's point methods (Croston, SBA, ADIDA), scored as point masses, lose to every forecast with a law, by
construction. The fourth factorial cell on npm and the grid repeats NYC 311's positive-law result (the shifted
Poisson in place of the model's own positive law is far worse on dense series), while its occurrence result at a
month shows the pattern of the second reading of the accounting trade and at a week on the grid the first. Nothing
confirmatory; no test added to any family; every registered family reproduced byte for byte before anything was
written; 18 new tests, 477 in all.

## Study 3 (dated addition 7 of 2026-10-16, committed `3357d77`; the code `f7a8628`)

The regime hypothesis H3 made confirmatory on a second domain: on series whose context zero fraction is at least 0.5,
the substitution with a dynamic occurrence lowers QScore9 against the model's own completed forecast; below 0.5 it
raises it; each stratum is tested on its own. The domain is NYC 311 as registered for Study 2 (problem type by
community board; the frozen 2024 inventory of 9,496 cells, 8,469 eligible, is the whole frame), selection seed
20261001, Study 2's calendar and strata, a verified panel by 2026-10-27 23:59 UTC with PyPI as the sole fallback.
Four variants per model from the same base forecast: completed, hurdle_fixed, hurdle_dynamic (new) and
occurrence_model_size_count (new, the fourth factorial cell). Thirty-six tests R01 to R36
(`study/study3/regime_comparisons.json`): per stratum, model and horizon, hurdle_dynamic against the completed control
and against hurdle_empirical_28; one BH correction at q = 0.05; a stratum with fewer than ten series has its twelve
tests unavailable. A day with zero requests across the frame is a source gap and stops the domain before scoring. The
addition is appended (`PROTOCOL.md` 71,635 bytes, SHA-256 `05c7617b…`; every registered prefix verified twice) beside
`study/study3/spec.json`. The code holds the two variants, the study3 component and gate (bound to the addition's
commit, the frozen panel and the deadline), the per-stratum inference, the integrity recomputation and a resumable
one-query-per-day NYC 311 census that refuses any request naming a day on or after 2026-06-03; 459 tests pass.

**The NYC 311 panel (frozen 2026-10-16 08:04 UTC; committed `0e70759`).** One anonymous query per calendar
day over the 275 context days, 276 request attempts in all against a ceiling of 330, 19 minutes, no retry, no error, no
request naming a day on or after 2026-06-03. All 8,469 eligible cells have a complete context; the strata hold
2,002 dense, 2,422 sparse and 4,045 very sparse complete series, and each takes its first 100 in selection-hash
order with seed 20261001: 300 series, no stratum reduced, eleven days before the deadline. An independent script
recomputed the census, the strata and the selection from the raw captures with zero mismatches. The source states
no license and links no terms page; `created_date` is a floating timestamp whose daylight-saving pattern places it
in New York local time. Counted apart as registered: 49,356 requests with an unrecognized board code and 7,680 in
cells outside the 2024 frame. Of the very sparse stratum's 100 series, 39 have no request in the 90 strata days and
19 none in the whole context; the selection is as registered. The manifest, selection, census and the source
record are copied under `reports/study3-nyc311/panel/`; `study/study3/nyc311_panel_status.json` binds them for the
gate.

**The run's first stage (2026-10-17 02:05 UTC; no network).** The GPU smoke at `00fd91d` passed in 39 s with a peak
reserved VRAM of 2.95 GB and carries the study3 component, the protocol hash, the four seeds and the 22 variants. The
runtime estimate, from the run's own loop on thirty synthetic series, is 1,080 s for 300 series at three origins
(the 209 npm series took 699 s); the proposed budget is 3,600 s. The readiness draft binds addition 7, the panel's four
entries and the smoke, and the gate refuses it at the unsigned approval and nowhere else. No variant fails on an
all-zero context: with fewer than two request days in the last 28, the dynamic occurrence falls back to the fixed
Jeffreys estimate, so the two hurdles coincide there. At the first origin that holds for 74 of the 100 very sparse
series and 4 of the sparse ones, so the very sparse rows will carry many exact ties, and a median difference of
exactly zero is reported as having no sign.

**The run (2026-10-17 03:47 to 04:03 UTC; committed `4b8851e`).** Under the signed gate (passed before the
target pull, before its resumption and before the run), the 90 target days were pulled in 106 request attempts of 120
approved: the first invocation, one request a second, met 16 throttled answers and stopped at its ceiling of 100 after
84 days; the second, three seconds apart, took the last six. Every day was exhausted on one page, no source gap, and an
independent recomputation from the raw captures matched every count. The run took 956 s of the 3,600 s budget for 300
of 300 series; the committed inference and integrity recomputation ran unchanged (0 of 39,600 forecasts disagree). The
family R01 to R36: 21 of 36 reject at BH q = 0.05, none against H3's predicted direction. Dense, against the completed
control: all six reject with the predicted sign (the dynamic hurdle is worse, higher on 55 to 72 of 100 series, medians
+0.004 to +0.013). Sparse: one of six rejects as predicted (TimesFM 2.5 at horizon 7, lower on 57 of 100); four medians
are exactly zero. Very sparse: none rejects; all six medians are exactly zero, with 72 to 88 of 100 series tied exactly.
Against the empirical hurdle 14 of 18 reject for the dynamic hurdle, three of them with a median of exactly zero and so
no registered sign; on sparse and very sparse series that contrast owes as much to the swapped occurrence as to the
positive law. H3 is confirmed on NYC 311 for dense series
and not confirmed for sparse and very sparse ones. Results: `reports/study3-nyc311/run-2026-10-17/RESULTS-nyc311.md`
and the appended section of `RESULTS.md`; the 300 checkpoints (645 MB) stay out of the tree. The source's terms were
recorded 2026-10-17 04:49 UTC (`reports/study3-nyc311/panel/source-terms.md`): the portal's overview page had moved to
the city's main site, which refused the scripted request and answered a browser; the city site's terms of use state no
license, attribution rule or restriction for the datasets, the dataset's metadata states no license, and the Open Data
Law the page names was not read.

## What the protocol allows, and what lapsed

- Study 1 is closed. Anything computed from its saved run is post-hoc and labeled so.
- Study 2 is registered: 54 external tests (three domains), 6 synthetic, 18 prospective; one BH per family;
  no run before a signed gate at the committed implementation with GPU smoke at that HEAD.
- **Lapsed, and recorded by the dated addition of 2026-10-12:** the October holdout (freeze 2026-09-28 passed
  with nothing frozen) is reported as not run; the npm readiness clock is reset once, to 2026-10-20 23:59 UTC,
  with the PyPI rule unchanged after that; the October paper's external family is E01 to E18 with one BH
  correction, E19 to E54 kept whole for a later run. All three were decided before any Study 2 target was
  seen (`study/study2/acquisition_status.json`: targets opened false, forecasts generated false).
- Study 3 is registered by dated addition 7 (2026-10-16, `3357d77`): the 36-test family R01 to R36 on NYC 311; its
  targets were opened 2026-10-17 under the signed gate and the family has run.
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

The author's commit of the benchmark; the revision that reorganizes the paper by question at about twelve pages with the
two reads and the benchmark applied; its review; the
author's read of both summaries and of the report's title, abstract and summary; the PDF (no TeX on this machine);
the GitHub release and the release assets for the checkpoints; the paper on Zenodo and to TMLR by 2026-10-31. Dates and
gates are in `docs/PLAN.md`.

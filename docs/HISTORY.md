# PulseGraph: how version 2 came to be

Written 2026-10-12 from the setup record of September 2026 and the preserved documents of version 1. Dates are
absolute. The current state is `docs/STATE.md`; the plan is `docs/PLAN.md`; the registered design is
`PROTOCOL.md`.

## The question

PulseGraph is an empirical forecasting study: do zero-shot time-series foundation models improve probabilistic
forecasts of daily new-star counts on GitHub repositories, compared with simple and strong baselines? The
series are bursty, zero-inflated, survivor-biased count data of a kind underrepresented in public forecasting
benchmarks, which is what makes the question interesting.

## Version 1, June and July 2026

Version 1 was built in June and July 2026 with heavy use of AI coding agents under the author's direction. It
is public at `vprchlik/Project-PulseGraph` (`main` at `7ef49b8`, MIT licence). Its study code (ingestion,
seven baseline families, Chronos-2 and TimesFM-2.5 wrappers, a walk-forward backtest, metrics, seven review
scripts and tests) sat beside a legacy web application, database and graph modules that have nothing to do
with the study.

Data: 208 repositories selected by three GitHub Search API queries (recently created and already high-starred;
old, moderate, recently maintained; not pushed in years), 414,271 daily rows from 2008-11-13 to 2026-06-22,
179 repositories with at least 270 days. Backtest: expanding context from 180 days after the first star, step
30 days, at most eight windows per repository, horizons 7, 30 and 90 days, 200 predictive trajectories per
model.

Headline: both foundation models had lower mean CRPS than every original baseline in all nine cohort-by-horizon
cells (for the "breakout" cohort, 6.2 to 8.5 against 11.2 to 28.0). After the audit added a 28-day local-mean
baseline on identical windows, the foundation models still won every cell on the mean, but per-repository win
rates fell to 40.6 to 80.5 percent, and the audit found that the five largest positive contributors accounted
for roughly 30 to 77 percent of the positive gain depending on the cell. The honest headline was robustness against a minority of large
misses, not uniform superiority.

The data and results are not in that repository: its ignore rules excluded every parquet and CSV and the
`data/` folder. The only copy of the result artifacts (the results parquet, the summary CSV, the review
outputs, the raw stargazer data) was on a computer the author no longer uses; their recovery is deferred. A
local, untracked copy of the version 1 tree (`v1_reference/`) retains the documents, tables, metadata and four
figures, and the write-up quotes version 1 numbers from those documents without recomputing them.

## The audit, 2026-07-12

An adversarial audit found no code defect that invalidates the aggregate comparison, but two design flaws that
cannot be fixed by rewriting prose:

1. The cohorts were conditioned on outcomes. "Breakout" was selected for already having many stars, "dead"
   for later inactivity, "steady" for later maintenance. The labels were not available at forecast time; the
   "dead" cohort's evaluation windows had a median of 5.02 stars per day and only 7.7 percent zero days.
2. The windows mostly tested post-peak decay. The global peak preceded the evaluated span for 78.0 percent of
   breakout repositories; only 12.2 percent peaked inside it. The study did not test shock prediction.

The audit also listed what version 1 had to disclose and version 2 had to design out: a weak original baseline
set; Wilcoxon tests on overlapping windows treated as independent; untested scale domination; a mislabelled
95 percent interval for TimesFM; ordinary PIT on discrete counts; unseeded baseline sampling; LightGBM's
uncertainty from in-sample residuals; MAPE as a headline metric on zero-inflated series; implicit observation
endpoints that censored trailing zeros and omitted later-removed stars; and unresolved pretraining
contamination with no clean post-release holdout.

Its prescription became the specification of version 2: freeze and pre-register; context-only cohort labels;
trailing non-overlapping windows with a common observation endpoint; strong pre-registered classical and
count-aware baselines; native quantile metrics; repository-clustered inference; a prospective post-release
cohort as the contamination control.

## Why version 2 is a new repository

Decided 2026-09-12: a new repository rather than a cleanup of the old one, because the experiment is a
redesign, the legacy modules add nothing, model versions had moved, and a clean history reads better than one
that begins with a full-stack scaffold. Study code only in the tree. The code is MIT; the aggregated dataset
and the write-up carry CC BY 4.0. The write-up is the deliverable: the version 1 result, the audit, the
registered protocol, the version 2 result, limitations. A research pass on the model landscape (which models
and revisions exist, what their cards disclose about training data, what the current evaluation standards are)
ran before the protocol was frozen and fed it; it does not replace it.

## The design that became the protocol

Population, not search results: a frame of all repositories created in a fixed window with at least 20
WatchEvents by day 90, from GH Archive, sampled by a seeded rule within three day-90 strata. Daily counts from
GitHub's star-history endpoint, validated hourly against GH Archive for 2024. Trailing, non-overlapping windows
with a common endpoint so real zeros survive. Context-only regime labels, proven by tests. Three frozen model
revisions (Chronos-2, TimesFM 3, TimesFM 2.5) against a 28-day local mean and weekly AutoETS as primary
references, with thirteen secondary baselines. A nine-decile quantile score, repository-clustered bootstrap,
paired signed-rank tests and one BH correction over eighteen declared comparisons. Report either way. The
protocol was registered at commit `5f01769` on 2026-09-12 before any target was fetched; the follow-up cohort
of repositories created after 2026-09-13 was registered as a separate study to run after the write-up.

## Timeline

| Date | Event |
|---|---|
| 2026-09-12 | Repository set up (`79718fb`); study code ported with 93 offline tests (`14d7a4c`); protocol registered (`5f01769`); registered implementation with 147 tests (`4b3b2b3`) |
| 2026-09-13 | Validation histories fetched and compared hourly with GH Archive; America/Los_Angeles days accepted; frame of 148,550 eligible repositories; 300 accepted; the registered run (5 hours 11 minutes, 48,600 forecast rows, no failures); results and inference recorded (`ab2b63e`) |
| 2026-09-14 | Study 2 (occurrence and positive size; three external domains, a synthetic grid, an October prospective holdout) registered as a dated addition (`df55867`); the post-hoc decomposition of Study 1 and the Study 2 implementation written |
| 2026-09-28 | The October holdout's freeze deadline passed with nothing frozen; recorded as not run by a dated addition of 2026-10-12 |
| 2026-10-12 | The project pages under `docs/` started; the root rules replaced by `CONTRIBUTING.md`; the Study 1 report and the paper begun |

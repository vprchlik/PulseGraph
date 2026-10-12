# The Study 1 report: title, abstract and a one-page summary

Written 2026-10-12 for the author's read before anything is posted. Every number below comes from a named
file; `paper/sources.md` gives the row and column and the command that regenerates the file, and
`paper/check_numbers.py` asserts each one. Differences are model minus reference, so a negative number
favors the model.

## Title

Zero-shot foundation models on sparse daily GitHub star counts: a registered re-evaluation after an audit

## Abstract

We revisit a study of whether zero-shot time-series foundation models improve probabilistic forecasts of daily
GitHub star counts, a bursty and zero-inflated kind of count series. A first version, run in June and July
2026, found Chronos-2 and TimesFM-2.5 ahead of four classical baselines on mean CRPS in every cohort-by-horizon
cell. An adversarial audit found no invalidating code defect but two design flaws: cohorts selected on outcomes
not available at forecast time, and evaluation windows dominated by post-peak decay. We pre-registered a
redesign (protocol commit 5f01769, 2026-09-12) and ran it unchanged: a population frame of 148,550
repositories created between 2023-01-01 and 2025-02-21 from GH Archive; 300 repositories sampled by a seeded
rule in three day-90 activity strata; daily counts from GitHub's star-history endpoint through 2026-08-31;
three trailing cutoffs whose 90-day windows do not overlap, evaluated at horizons of 7, 30 and 90 days; three
frozen models (Chronos-2, TimesFM 3, TimesFM 2.5) against a 28-day local mean and weekly AutoETS; a
nine-decile quantile score with repository-clustered inference over 18 declared comparisons. Against the local
mean, the mean difference favors the models in every cell and its bootstrap interval excludes zero in five of
nine, but the typical repository favors the reference: the models score lower on 46 to 89 of 300
repositories, and the paired signed-rank test rejects in all nine cells with the median difference on the
reference's side. Against AutoETS the models score lower on 293 to 298 of 300 repositories, a result
consistent with AutoETS's wide intervals (its 80 percent intervals cover about 99 percent of target days). A
post-hoc accounting locates the mean gain on positive days where the local mean overpredicts, as a trailing
mean does after a burst; the zero-day penalty is small. The result is reported either way, with the
registered second study and the lapsed prospective holdout stated as not run.

## One page for the author

### What was found

The registered run (implementation `ca67dd2`, 2026-09-13, 5 hours 11 minutes, 48,600 forecast rows, no
failures) gives two answers that do not agree, and the report shows both every time it shows either.

Against the 28-day local mean, the three foundation models have lower mean QScore9 in all nine
model-by-horizon cells: the mean difference runs from -0.101 (Chronos-2, 90 days) to -0.258 (TimesFM 3,
7 days), and the 95 percent interval from 20,000 repository-bootstrap replicates excludes zero in five of the
nine cells (the three
30-day cells and the 90-day cells of Chronos-2 and TimesFM 3). But the typical repository is better served by
the local mean: the models score lower on only 46 to 89 of the 300 repositories, every median difference is
positive, and the Wilcoxon signed-rank test rejects in all nine cells after Benjamini-Hochberg adjustment with
the median on the reference's side (largest adjusted p-value 0.0067, TimesFM 3 at 7 days). Nothing in these
two statements contradicts the other. The mean is carried by a minority of large repositories, and the
signed-rank test is not a test of the mean.

Against weekly AutoETS the models win on 293 to 298 of 300 repositories, with mean differences from -1.07
(Chronos-2, 7 days) to -6.75 (TimesFM 3, 90 days). AutoETS's nominal 80 percent intervals cover 98.6 to 98.8
percent of target days, and its median 90-day interval width in the top stratum is about 56 stars per day, so
this is a weak uncertainty reference and the report says so.

The post-hoc accounting (labeled post-hoc, no new test) splits each difference against the local mean into a
zero-day part, a positive-day overprediction part and a positive-day underprediction part. The zero-day part
is small and against the models in every cell (0.004 to 0.015). The overprediction part favors the models in
every cell (-0.088 to -0.209). The underprediction part favors the models at 7 days, where it is the larger of
the two positive-day parts for both TimesFM models, and favors the local mean at 90 days.

### What it changes

Version 1 said foundation models beat classical baselines on daily GitHub stars. The registered redesign
says: on a population-sampled panel with context-only labels and a common endpoint, they beat the classical
reference on the mean and lose to a 28-day moving average on most individual repositories. The mean gain is
real within this panel and calendar, is concentrated (the five largest positive repository gains are 88.5 to
94.3 percent of all positive gain against the local mean), and sits on positive days where the local mean
overpredicts. The audit mattered: the story of the report is first result, audit, registered redesign,
revised result.

### What it does not show

- It does not show that the models forecast bursts. Eight windows from seven repositories meet the surge rule;
  320 windows from 140 repositories meet the inactive rule.
- It does not show anything about new repositories. The panel is the 300 repositories still public in
  September 2026 with complete histories (470 candidates met on the way were skipped because their ID no
  longer resolved publicly), forecast in their mature phase (cutoffs 2025-12-05, 2026-03-05, 2026-06-03), not
  at launch. In the last 90 days before the endpoint, 52, 22 and 1 repositories in the three strata received
  no star at all.
- It does not measure gross star additions. The target is surviving stars as retrieved in September 2026,
  which for 13 of the 15 large validation projects is 5 to 27 percent below the 2024 archive count.
- It does not resolve training contamination. No author-disclosed complete-corpus cutoff exists for any of
  the three models.
- It does not report Study 2 or the October holdout. Study 2 is registered and not run; the holdout's freeze
  lapsed on 2026-09-28 and it is reported as not run by the dated addition of 2026-10-12.
- The version 1 numbers are quoted from the preserved documents and were not recomputed; the version 1
  artifacts are on a computer the author no longer uses.

### What could not be verified

- The dated addition of 2026-10-12 to `PROTOCOL.md` is in the working tree but not committed as of
  2026-10-12 09:21 UTC. The report cites it; the citation holds only once it is committed.
- The release asset URL for `results.parquet` is still "to be filled" in `README.md`; the report leaves the
  same marked place.
- The readiness review's author-accepted text says the endpoint is below the archive "by 5 to 27 percent for
  the large ones"; the saved table gives 0.6 to 27 percent for the 15 large projects, with 13 of 15 at 5
  percent or more. The report uses the table's figures.
- `docs/HISTORY.md` records the holdout as "recorded as not run by a dated addition of 2026-10-12"; the
  addition exists only uncommitted (above).

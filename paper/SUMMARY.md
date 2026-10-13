# The Study 1 report: title, abstract and a one-page summary

Written 2026-10-12 for the author's read before anything is posted, and rewritten the same day after the
report's review (`docs/research/2026-10-12-report-review.md`). Every number below comes from a named file;
`paper/sources.md` gives the row and column and the command that regenerates the file, and
`paper/check_numbers.py` asserts each one. Differences are model minus reference, so a negative number
favors the model. The three sentences the author should read are listed at the end.

## Title

Zero-shot foundation models on sparse daily GitHub star counts: a registered re-evaluation after an audit

## Abstract

We revisit whether zero-shot time-series foundation models improve probabilistic forecasts of daily GitHub
star counts. A first version found Chronos-2 and TimesFM-2.5 ahead of four classical baselines on mean CRPS
in every cell. An audit found no invalidating code defect but two design flaws: cohorts selected on outcomes
unavailable at forecast time, and evaluation windows dominated by post-peak decay. We pre-registered a
redesign (protocol commit 5f01769, 2026-09-12) and ran it unchanged: from 148,550 repositories
created 2023-01-01 to 2025-02-21 with at least 20 archived stars in their first 90 days, 300 sampled by a
seeded rule in three day-90 activity strata; daily counts from GitHub's star-history endpoint through
2026-08-31; three non-overlapping trailing cutoffs, horizons of 7, 30 and 90 days; three frozen models
(Chronos-2, TimesFM 3, TimesFM 2.5) against a 28-day local mean and weekly AutoETS; a nine-decile quantile
score with repository-clustered inference, 18 declared comparisons. Against the local mean the mean
difference favors the models in every cell and its bootstrap interval excludes zero in five of nine, but the
typical repository favors the reference: the models score lower on 46 to 89 of 300 repositories and the
signed-rank test rejects in all nine cells on the reference's side. Against AutoETS both summaries favor the
models, the mean in all nine cells and the win count on 293 to 298 of 300, consistent with its 80 percent
intervals covering about 99 percent of target days. A post-hoc accounting locates the mean gain on positive
days where the local mean overpredicts; the zero-day part is small beside it. The registered second study,
the registered follow-up cohort and the lapsed prospective holdout are stated as not run.

## One page for the author

### What was found

The registered run (implementation `ca67dd2`, 2026-09-13, 5 hours 11 minutes, 48,600 forecast rows, no
failures) gives two answers that do not agree, and the report shows both every time it shows either.

Against the 28-day local mean, the three foundation models have lower mean QScore9 in all nine
model-by-horizon cells: the mean difference runs from -0.101 (Chronos-2, 90 days) to -0.258 (TimesFM 3,
7 days), and the 95 percent interval from 20,000 repository-bootstrap replicates excludes zero in five of
nine cells (the three 30-day cells and the 90-day cells of Chronos-2 and TimesFM 3). But the typical
repository is better served by the local mean: the models score lower on only 46 to 89 of the 300
repositories, every median difference is positive (0.0003 to 0.0041), and the Wilcoxon signed-rank test
rejects in all nine cells after Benjamini-Hochberg adjustment with the median on the reference's side
(largest adjusted p-value 0.0067, TimesFM 3 at 7 days). Nothing in these two statements contradicts the
other. The mean is carried by a minority of large repositories, and the signed-rank test is not a test of
the mean.

Against weekly AutoETS both summaries favor the models: the mean difference is negative in all nine cells,
from -1.07 (Chronos-2, 7 days) to -6.75 (TimesFM 3, 90 days), and the models score lower on 293 to 298 of
300 repositories. AutoETS's nominal 80 percent intervals cover 98.6 to 98.8 percent of target days, about
99 percent, and in a width diagnostic requested after the run its median 90-day daily interval width in the
top stratum is 49.69 stars per day; it is a weak uncertainty reference and the report says so.

By stratum, the declared table holds stratum means only. A post-hoc reading of the saved per-repository
file, labeled as such in the report, gives the typical repository: the median difference against the local
mean favors the reference in every stratum and cell, and the models score lower on 5 to 18 of 100
repositories in the smallest stratum, 10 to 34 in the middle one and 26 to 38 in the top one.

The post-hoc accounting (labeled post-hoc, no new test) splits each difference against the local mean into a
zero-day part, a positive-day overprediction part and a positive-day underprediction part. The zero-day part
is against the models in every cell, 0.004 to 0.015: small beside the mean gain, but in every cell larger
than that cell's median difference. The overprediction part favors the models in every cell (-0.088 to
-0.209). The underprediction part favors the models at 7 days, where it is the larger of the two positive-day
parts for both TimesFM models, and favors the local mean at 90 days.

### What it changes

Version 1 said foundation models beat classical baselines on daily GitHub stars. The registered redesign
says: on a population-sampled panel with context-only labels and a common endpoint, they beat the 28-day
local mean on the mean and lose to the same local mean on most individual repositories. The mean gain against
the local mean excludes zero in five of nine cells, is concentrated (the five largest positive repository
gains are 88.5 to 94.3 percent of all positive gain), and sits on positive days where the local mean
overpredicts. The audit mattered: the story of the report is first result, audit, registered redesign,
revised result.

### What it does not show

- It does not show that the models forecast bursts. Eight windows from seven repositories meet the surge rule;
  320 windows from 140 repositories meet the inactive rule. Why the local mean overpredicts on the days where
  the models gain is not something the accounting tests.
- It does not show anything about new repositories. The panel is the 300 repositories still public in
  September 2026 with complete histories (470 candidates met on the way were skipped because their ID no
  longer resolved publicly), forecast in their mature phase (cutoffs 2025-12-05, 2026-03-05, 2026-06-03), not
  at launch. In the last 90 days before the endpoint, 52, 22 and 1 repositories in the three strata received
  no star at all.
- It does not measure gross star additions. The target is surviving stars as retrieved in September 2026,
  which for 13 of 15 large validation projects is 6 to 27 percent below the 2024 archive count.
- It does not resolve training contamination, and what it can say is bound by availability, per model. No
  author-disclosed complete-corpus cutoff exists for any of the three models. The targets (2025-12-05 to
  2026-08-31) postdate the pinned TimesFM 2.5 revision, dated 2025-10-02, but are not shown to postdate the
  pinned Chronos-2 revision (2026-06-05) or the pinned TimesFM 3 revision (2026-09-02, weights uploaded
  2026-08-24); these are repository revision dates, not training cutoffs, and every repository's earlier
  history may be familiar to all three models. The controls, Study 1's registered follow-up cohort
  (repositories created on or after 2026-09-13) and the lapsed October holdout, have not run.
- It does not report Study 2, its October holdout or the follow-up cohort. Study 2 is registered and not
  run; the holdout's freeze lapsed on 2026-09-28 and it is reported as not run by the dated addition of
  2026-10-12 (committed at `8db0d73`); the follow-up cohort's closing date, endpoint and frame coverage are
  registered as still open.
- The version 1 numbers are quoted from the preserved documents and were not recomputed; the version 1
  artifacts are on a computer the author no longer uses.

### What could not be verified

- The release asset URL for `results.parquet` is still "to be filled" in `README.md`, and no release exists;
  the report says the file "is to be published" as a release asset.
- The readiness review's author-accepted text says the endpoint is below the archive "by 5 to 27 percent for
  the large ones"; the saved table gives 0.6 to 27 percent for the 15 large projects, with 13 of 15 at 5
  percent or more, and 6.3 to 27.2 percent for those 13. The report and this summary use the table's
  figures.
- The six items cited from the literature re-check, and Kim and Song, are recorded there by surname only;
  the bibliography entries carry surnames only. No network was used in this revision.
- "As of 2026-10-12 no Study 2 target value, forecast or score exists" is dated in the report and is to be
  re-checked on posting day against `study/study2/acquisition_status.json`.
- No TeX compiler is on this machine, so there is no PDF and no page count. By word count the body through
  the bibliography is about seven pages and the appendix about three and a half.

### Three sentences to read

1. The contamination sentence (Section 7, "Training contamination unresolved"): "The targets, 2025-12-05 to
   2026-08-31, postdate the pinned TimesFM 2.5 revision, dated 2025-10-02, but are not shown to postdate the
   pinned Chronos-2 revision, dated 2026-06-05, or the pinned TimesFM 3 revision, dated 2026-09-02 with
   weights uploaded 2026-08-24; these are repository revision dates, not training cutoffs."
2. The zero-day sentence (Section 6; the abstract says it in short): "The zero-day part is positive, against
   the models, in every cell, from 0.004 to 0.015: small beside mean differences of -0.101 to -0.258, but in
   every cell larger than that cell's median difference in Table 2, where the medians run from 0.0003 to
   0.0041."
3. The AutoETS sentence (the abstract; Section 5 and the limitations say it at length): "Against AutoETS both
   summaries favor the models, the mean in all nine cells and the win count on 293 to 298 of 300, consistent
   with its 80 percent intervals covering about 99 percent of target days."

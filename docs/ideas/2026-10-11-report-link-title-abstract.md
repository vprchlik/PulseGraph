# The link, title and abstract of the Study 1 report

Written 2026-10-12 03:57 UTC. The author reads the title, the abstract and `paper/SUMMARY.md` before anything
is posted; this document is the proposal the write-up starts from. Every number below is from `RESULTS.md`,
`README.md` and `reports/registered-2026-09-13/posthoc/posthoc-paired-summary.csv`; the write-up re-derives
each one from its file.

## The link

**Recommendation: a Zenodo DOI, minted the day the author publishes the record.** Zenodo gives a DOI at once,
needs only an account (GitHub sign-in works), hosts the PDF and, if wanted, the 433 MB results file, lets the
author reserve the DOI before uploading so the PDF can print its own DOI, and versions the record: version 1
is the Study 1 report (by 2026-10-24), version 2 the paper (by 2026-10-31), each with its own DOI under one
concept DOI. Licence CC BY 4.0, as decided on 2026-09-12. Record type "Report" for version 1, "Preprint" for
version 2. Related identifiers: the GitHub repository and the two protocol commits.

**arXiv** is the better-known home for the paper, not the report. It needs an endorser for cs.LG or stat.ML
for a first submission, and moderation takes one to three working days, so it cannot give a same-day link.
If an endorser is at hand by 2026-10-27, the paper goes to arXiv as well as Zenodo version 2; otherwise Zenodo
version 2 and the TMLR submission (through OpenReview, no fee, no arXiv requirement) are the paper's links.
TMLR allows a prior preprint.

Steps for the author on posting day, in person:

1. Create or sign in to Zenodo; "New upload"; "Reserve DOI"; put the DOI into `paper/main.tex` where marked
   and compile the final PDF.
2. Upload the PDF; type Report; title and abstract from `paper/SUMMARY.md`; author Victor Prchlik; licence
   CC BY 4.0; related identifiers `https://github.com/vprchlik/PulseGraph` and the protocol commit
   `5f01769b6be4c32814befdd7cc3395b6dcc386ed`; publication date the day of posting.
3. Publish. Put the DOI in `README.md`'s first screen.

## Proposed title

Zero-shot foundation models on sparse daily GitHub star counts: a registered re-evaluation after an audit

Alternative, if the question is wanted in the title: Do zero-shot foundation models forecast sparse GitHub
star counts better than a 28-day mean? A pre-registered re-evaluation

## Proposed abstract (about 240 words; the write-up corrects any figure against its file)

We revisit a study of whether zero-shot time-series foundation models improve probabilistic forecasts of daily
GitHub star counts, a bursty and zero-inflated kind of count series. A first version, run in mid-2026, found
Chronos-2 and TimesFM-2.5 ahead of classical baselines on mean CRPS in every cohort. An adversarial audit found
no invalidating code defect but two design flaws: cohorts selected on outcomes not available at forecast time,
and evaluation windows dominated by post-peak decay. We pre-registered a redesign (protocol commit 5f01769,
2026-09-12) and ran it unchanged: a population frame of 148,550 repositories created between 2023-01-01 and
2025-02-21 from GH Archive; 300 repositories sampled in three day-90 activity strata; daily counts from GitHub's
star-history endpoint through 2026-08-31; three non-overlapping trailing windows at horizons of 7, 30 and 90
days; three frozen models (Chronos-2, TimesFM 3, TimesFM 2.5) against a 28-day local mean and weekly AutoETS;
a nine-decile quantile score with repository-clustered inference over 18 declared comparisons. Against the
local mean, the mean difference favors the models in every cell and its bootstrap interval excludes zero in
five of nine, but the typical repository favors the reference: the models score lower on 46 to 89 of 300
repositories, and the paired signed-rank test favors the reference in all nine cells. Against AutoETS the
models score lower on 293 to 298 of 300 repositories, a result that owes to AutoETS's wide intervals (80
percent intervals cover about 99 percent). A post-hoc accounting locates the mean gain on positive days where
the local mean overpredicts after bursts; the zero-day penalty is small. The result is reported either way,
with the registered second study and the lapsed prospective holdout stated as not run.

## A plain paragraph for the author's own use

The first version of this study found that two time-series foundation models beat classical baselines at
forecasting daily GitHub stars. An audit showed the comparison had been set up in a way that favored them:
the groups of repositories were chosen using information from after the forecast date, and most test windows
fell in the quiet period after a repository's peak. I pre-registered a redesign, sampled 300 repositories from
the whole population of new repositories by a fixed rule, and ran it without changes. The models still win on
average, but the average is carried by a few large repositories; on most individual repositories a 28-day
moving average does as well or better. The report says so, with every number traceable to a saved file.

## The README paragraph on how this project was built

Added to `README.md` on 2026-10-12 in the author's voice, for his approval before it is committed. The
write-up prints the same statement. It claims only what the files show: the protocol's sign-off lines, the
approvals recorded in the evidence package, the run metadata, and the regeneration commands.

> This study exists for three reasons: the question, whether zero-shot time-series foundation models improve
> probabilistic forecasts of sparse daily counts; the audit of its first version, which found no invalidating
> code defect but two design flaws; and the registered redesign that answers the question without them. The
> code in this repository was written with AI coding agents under my direction. I set the question,
> registered the protocol before any target data was fetched, ran the studies on my own machine, and made the
> decisions that the protocol and the evidence package record as the author's. Every number in `RESULTS.md`
> traces to a saved file under `reports/` and to the command that regenerates it, named in this README and in
> `RESULTS.md`.

# Review of the Study 1 report

Written 2026-10-12 21:45 UTC. A read-only review of the Study 1 report under `paper/` (`main.tex`,
`SUMMARY.md`, `sources.md`, `check_numbers.py`, `references.bib`, the three figures) as committed in `c62d0c5`,
against the record: `PROTOCOL.md` with its dated additions (the latest committed in `8db0d73`), `RESULTS.md`,
`README.md`, `docs/HISTORY.md`, `docs/STATE.md`, the evidence package under `reports/registered-2026-09-13/`,
the preserved version 1 documents in the local `v1_reference/`, the literature re-check
(`docs/research/2026-10-11-literature-recheck.md`) and the writing rules in `CONTRIBUTING.md`. Nothing under
`paper/` was changed; the fixes below are instructions for the revision.

Each verdict is `holds`, `holds with this fix` or `does not hold`; `does not hold` is used only where a file
contradicts the text. Line numbers refer to `paper/main.tex` unless another file is named. In source order the
compiled table numbers are: Table 1 version 1 (`tab:v1`), Table 2 the panel (`tab:panel`), Tables 3 and 4 the
comparisons against `local_mean_28` and `autoets_weekly` (`tab:lm`, `tab:ae`), Table 5 AutoETS (`tab:autoets`),
Table 6 the post-hoc parts (`tab:posthoc`), Tables 7 to 9 the appendix. `R` stands for
`reports/registered-2026-09-13`. Figures quoted below that are not in the report come from saved files by the
command at the end.

## Numbers

**1. The checker passes.** `holds`. `paper/check_numbers.py`, run at 2026-10-12 21:30 UTC: "181 checks, 0
failures, 0 skipped", exit code 0. Fix: none.

**2. Every number in the abstract and Sections 4 to 6 traces to its file.** `holds`. Traced independently of
the checker: the 18 rows of Tables 3 and 4 from `R/inference/paired_repositories.csv` (means, medians, win
counts, Wilcoxon and BH p-values to a relative 1e-14, and the bootstrap intervals exactly, from the saved
`bootstrap_seed` of each row of `R/inference/inference.csv`); the panel row values and skip reasons from
`R/evidence/panel-diagnostic/strata.csv` and `skip-reasons.csv` (466 HTTP 404, 4 HTTP 403, 470 in all);
289,316 repository-days as the sum over `R/run/manifest.json` of the days from `observation_start` to
2026-08-31; the regime counts from `R/descriptive/qscore9-regime.csv` (320 + 572 + 8 = 900 windows); the run
facts from `R/execution-summary.json`; Table 6 and the post-hoc ranges from
`R/posthoc/posthoc-paired-summary.csv`; the AutoETS zero-day part at 30 days (-0.768 to -0.777) and its
overprediction part (-1.783 to -1.795, the largest of the three parts in every AutoETS row). Fix: none.

**3. Numbers the checker does not assert.** `holds with this fix`. Verified by hand but not asserted: "900"
windows (line 257); "nine months" and "41 months" (lines 237, 479), which follow from the panel's creation
dates 2023-01-02 to 2025-02-19 in `R/run/manifest.json`; "about 99 percent" (lines 42 and 472); "2,048-day"
and "200" draws (lines 200 to 202; `R/run/run.json` `max_context`, `n_samples`); "Thirteen" secondary
baselines (line 202; `PROTOCOL.md` lines 134 to 152); the version 1 headline "6.2 to 8.5 against 11.2 to 28.0"
(lines 91 to 92; `v1_reference/RESULTS.md` Section 4.1, 6.23 to 8.52 and 11.19 to 28.00); the descriptions of
Figures 2 and 3 (lines 442 to 449). Fix: add asserts for these to `check_numbers.py`, the creation-month range
read from `R/run/manifest.json` and the version 1 headline range from the Section 4.1 table.

**4. `sources.md` names the tables wrongly.** `holds with this fix`. `paper/sources.md` lines 23, 37, 50 and 98
call the comparison tables "Tables 2 and 3", the post-hoc table "Table 7", the panel table "Table 1 of the
design" and the stratum table "Appendix Table A1"; compiled, they are Tables 3 and 4, Table 6, Table 2 and
Table 7 (the article class does not prefix appendix tables). Fix: name tables by their labels or by the
compiled numbers.

**5. The calendar counts are traced to prose.** `holds with this fix`. `paper/sources.md` line 87 traces "20 of
20 against UTC and 18 of 20 against fixed UTC-8" to the author-accepted text in `R/evidence/readiness.json`.
The per-repository table in `R/evidence/comparison/validation-report.md` agrees: Los Angeles has a lower mean
absolute difference than UTC for all 20 and than fixed UTC-8 for 18, with asciidoc-py and neighbourhood tied. Fix: trace the counts to that table and note the two ties.

**6. Two statements about the dated addition are stale.** `holds with this fix`. `paper/sources.md` line 113
says the addition of 2026-10-12 is "in the working tree ... awaiting the author's commit", and
`paper/SUMMARY.md` lines 93 to 94 and 100 to 101 list it as uncommitted; it was committed in `8db0d73`
(2026-10-12 21:29 UTC), and `PROTOCOL.md` at `HEAD` contains it. Fix: cite `8db0d73` in both files and drop the
two items from SUMMARY's "What could not be verified".

## Direction

**7. The sign of every comparison.** `holds`. From `R/inference/paired_repositories.csv`, against
`local_mean_28` every mean is negative and every median positive, the models are lower on 46 to 89 of 300
repositories and higher on 211 to 254, with no ties; the positive-rank sum exceeds the negative-rank sum in all
nine cells (for example 33,008 against 12,142 for Chronos-2 at 30 days) and the Hodges-Lehmann shift is
positive in all nine (0.0004 to 0.0067). Against `autoets_weekly` every mean, median and Hodges-Lehmann shift
is negative and the models are lower on 293 to 298. Tables 3 and 4 and Figure 1 agree row by row. Fix: none.

**8. Every sentence that states a direction.** `holds`. The abstract (lines 38 to 42), the introduction
(lines 64 to 66), Section 5 (lines 332 to 354) and `SUMMARY.md` (lines 41 to 55) state each direction as the
paired table gives it; the one place a two-sided p-value is read as favoring a side (lines 336 to 338, "the
location shift the test detects favors the reference") agrees with the sign of every median and of the rank
sums. Fix: none.

## Claims against the record

**9. Protocol commit and SHA-256.** `holds`. The blob of `PROTOCOL.md` at `5f01769` is 18,435 bytes with
SHA-256 `dfe2f4ad...65c5`, and it and the `df55867` blob (SHA-256 `33cefd8e...6360`) are byte prefixes of the
current file; `R/gate.json` records the same hash for the run. The commit is dated 2026-09-12 22:12 Eastern,
02:12 UTC on 2026-09-13; the frame order was frozen at 06:46:57 UTC and the first target history captured at
06:46:58 UTC (`R/evidence/panel/freeze.json`, `R/run/manifest.json`), so "before any target history was
fetched" holds. The report's date 2026-09-12 is the sign-off date in `PROTOCOL.md` line 3 and `README.md`.
Fix: none.

**10. The condensed design.** `holds`. Frame dates, eligibility, the latest day 90, strata, the seeded order and
stopping rule (lines 161 to 167; `PROTOCOL.md` lines 40 to 57); the calendar formula and cutoffs, checked by
arithmetic (lines 181 to 186; `PROTOCOL.md` lines 80 to 98); the regime rules in their order (lines 188 to
192; lines 102 to 116); the three revisions and licences (lines 194 to 200; lines 120 to 124); the two
references and the thirteen secondary baselines (lines 200 to 205; lines 134 to 152); the score, repairs and
the no-invented-tails rule (lines 207 to 216; lines 165 to 170); the inference settings and seeds (lines 218
to 226; lines 189 to 226). The statement that QScore9 equals the weighted interval score at the matching
levels is not in the protocol but is exact: with four central intervals and the median, the weighted interval
score is (2/9) times the summed pinball losses, which is QScore9 for one day. Fix: none.

**11. Validation and calendar.** `holds`. Lines 172 to 179 and 462 to 464 agree with
`R/evidence/comparison/validation-report.md` (365 matched days; pooled mean absolute differences 1.975, 2.065,
2.713; "the exact transition dates do not uniformly favor LA") and `R/evidence/readiness.json`. Fix: none.

**12. The survivor-ratio wording.** `holds with this fix`. The readiness review's author-accepted prose says the
endpoint is below the archive "by 5 to 27 percent for the large ones"; the saved table
`R/evidence/comparison/repository_2024_totals.csv` gives 0.6 to 27.2 percent for the 15 large projects, and
6.3 to 27.2 percent for the 13 that are at least 5 percent below. `main.tex` lines 458 to 459 use the table's
figures. `SUMMARY.md` line 83 says the 13 are "5 to 27 percent below", the prose's range. Fix: write "6 to 27
percent" in `SUMMARY.md`.

**13. The panel.** `holds`. Frame sizes 100,687, 46,811 and 1,052; 100 accepted per stratum; 98, 348 and 24
skips; every skip an identifier that returned HTTP 404 or 403 at fetch time; 289,316 signal rows with
`coverage_complete` true for all 300 (`R/evidence/panel/panel-summary.json`, `R/run/manifest.json`). Fix: none.

**14. The regimes.** `holds`. 320 windows from 140 repositories, 572 from 228, 8 from 7
(`R/descriptive/qscore9-regime.csv`). Fix: none.

**15. The run.** `holds`. Readiness signed 07:52:47 UTC, gate passed 07:53:59, run started 07:54:52 and
finished 13:05:54 UTC on 2026-09-13, 18,662.06 seconds, 48,600 rows, 300 checkpoints, no failure, no resume,
integrity pass (`R/evidence/readiness.json`, `R/gate.json`, `R/execution-summary.json`, `R/integrity.csv`).
Fix: none.

**16. Cost and approvals.** `holds`. The two completed jobs billed 123,584,118,784 and 12,387,039,051,776 bytes,
together 12,510,623,170,560, $71.11 at $6.25/TiB before credits; the written approval is recorded at 06:09:51
UTC, before the validation job (created 06:10:13), and the retry authorization at 06:41:05, before the frame
retry (created 06:41:10) (`R/evidence/cost-approval.json`, `R/evidence/query-provenance-final.json` and the two
job provenance files). Fix: none.

**17. Study 2 and the October holdout.** `holds with this fix`. Every statement in lines 487 to 506 matches
`PROTOCOL.md` (lines 251 to 340, 575 to 642) and the dated addition (lines 763 to 810), and
`study/study2/acquisition_status.json` records `target_values_opened` false and `real_forecasts_generated`
false. But "As of this report no Study 2 target value, forecast or score exists" (line 497) can become false
before posting: `docs/PLAN.md` runs the synthetic grid in parallel, and a November prospective round may still
be registered before 2026-10-28 (`docs/STATE.md`). Fix: date the sentence ("as of 2026-10-12") and re-check
both on posting day.

**18. Section 8 omits Study 1's own registered follow-up.** `holds with this fix`. `PROTOCOL.md` lines 64 to 76
register a follow-up on repositories created on or after 2026-09-13, with identical design, to run after the
write-up, its closing date, endpoint and frame coverage still open; `docs/HISTORY.md` lines 83 to 85 record it
as registered; `PROTOCOL.md` lines 579 to 580 say the October holdout does not replace it. Section 8 ("What
is registered and not run", lines 484 to 506) does not mention it. Fix: add one paragraph on the follow-up to
Section 8.

**19. The training-contamination limitation.** `does not hold`. Lines 475 to 478: "The targets, December 2025
to August 2026, are not shown to postdate the training data of any checkpoint. A prospective holdout was
registered as the control". The pinned TimesFM 2.5 revision is dated 2025-10-02
(`docs/research/2026-10-11-literature-recheck.md` line 112; `paper/references.bib`, `timesfm25-card`), before
the first target day, 2025-12-05, so every target postdates that checkpoint. The protocol's contamination
ledger describes retrospective blocks as "mixed by model availability" (`PROTOCOL.md` line 651, npm row),
registers the follow-up of item 18 as Study 1's availability-bound exclusion (lines 64 to 71), and calls the
holdout "a new calendar test on possibly familiar entities" that does not replace it (lines 579 to 580). Fix:
say that the targets postdate the TimesFM 2.5 checkpoint but are not shown to postdate Chronos-2
(revision dated 2026-06-05) or TimesFM 3 (weights uploaded 2026-08-24), that every repository's history
before the cutoffs may be familiar to all three, and that the registered follow-up and the lapsed holdout are
the controls, neither run.

**20. The audit's prescription, as listed in Section 2.** `holds with this fix`. Lines 114 to 117 list the
prescription that "became the specification of version 2" without the prospective post-release cohort, which
`docs/HISTORY.md` lines 59 to 62 include ("a prospective post-release cohort as the contamination control")
and `v1_reference/STUDY_AUDIT.md` recommends (P1, item 4). Fix: add it to the list and say it is registered and
not yet run.

**21. The release asset.** `holds with this fix`. Line 524 says `results.parquet` "is published as a GitHub
release asset"; `docs/STATE.md` says "no release exists yet", and the repository has no tag. Fix: publish the
release before posting, or write "is to be published".

**22. Section 9.** `holds`. What a fresh clone holds and does not hold (lines 510 to 518; `README.md` lines 50
to 66; `git ls-files` lists the manifest, signals, frame, candidate order and sampling log); the commands
(lines 529 to 533; `README.md` lines 297 to 301); the hardware and packages (`R/run/run.json`); the licences
(`README.md` lines 434 to 439; `LICENSE`). Fix: none.

**23. "The comparison against the local mean is the informative one."** `holds with this fix`. Lines 473 to 474
rank one of the two declared primary references above the other; the coverage evidence supports the reading
(`R/descriptive/calibration.csv`, AutoETS 0.986 to 0.988), but `PROTOCOL.md` lines 9 to 14 declare both, and
the ranking was made after the results. Fix: say it is the reading of the coverage results and that both
comparisons stay reported as registered.

**24. The abstract's frame.** `holds with this fix`. The abstract (line 33) and `SUMMARY.md` line 19 describe "a
population frame of 148,550 repositories created between 2023-01-01 and 2025-02-21"; the frame is only the
repositories with at least 20 archive WatchEvents over their first 90 days (`PROTOCOL.md` lines 42 to 43;
line 163). Fix: add "with at least 20 stars in the archive over their first 90 days".

## Version 1

**25. Every version 1 number and the disclosure.** `holds`. 208 repositories, 414,271 rows, 2008-11-13 to
2026-06-22, 179 usable (41, 69, 69), the backtest settings, the four primary baselines, the breakout ranges,
Table 1 row by row, 40.6 to 80.5 percent, 5.02 stars per day and 7.7 percent zero days, 78.0 and 12.2 percent,
the audit date and its ten must-fix items all match `v1_reference/RESULTS.md` (Sections 2 to 4) and
`v1_reference/STUDY_AUDIT.md`. The report says the numbers are quoted and not recomputed in Table 1's caption,
the disclosure paragraph (lines 142 to 146) and the limitations (line 481). Fix: none.

**26. The version 1 concentration figure.** `holds with this fix`. Lines 113 to 114 tie "the five largest
positive contributors accounted for 30 to 77 percent of the positive gain" to the comparison against the local
mean. `v1_reference/STUDY_AUDIT.md` lines 78 to 86 give roughly 30 to 77 percent under the scale-domination item without
naming a reference, and `v1_reference/RESULTS.md` has no such figure. Fix: quote it as the audit's figure,
"roughly", without naming the local mean, so it is not read beside version 2's 88.5 to 94.3 percent against
the local mean.

## Post-hoc labeling

**27. Section 6 and the post-hoc figures and table.** `holds`. Section 6 opens "This section is post-hoc"; the
captions of Table 6 and Figures 2 and 3 open "Post-hoc."; `R/posthoc/provenance.json` records
`confirmatory_tests_added` 0; Figure 1 is drawn from `R/inference/inference.csv` and is not post-hoc. Fix: none.

**28. AutoETS widths and specification counts.** `holds with this fix`. Table 5's caption (line 358) calls the
table "declared secondary"; `RESULTS.md` lines 660 and 678 say the specification counts and the 90-day widths
were requested after the run. Line 353 says "The six fits that selected multiplicative seasonality";
`R/descriptive/autoets-fits.csv` has 18 such fits, six at each horizon, from six repository-cutoffs of two
repositories, all in the top stratum. Fix: label the widths and counts as requested after the run, and write
"six fits at each horizon, from two repositories".

**29. Positive-gain share against net gain.** `holds`. Every mention reads the five-largest share as a share of
positive gain (lines 341 to 342, Table 9's caption, `SUMMARY.md` lines 68 to 69, and version 1 at lines 113 to
114); Figure 2's caption says each curve ends at its mean. Fix: none.

**30. The mean beside the typical repository against AutoETS.** `holds with this fix`. The abstract (lines 41
to 42, and `SUMMARY.md` lines 28 to 29) and the introduction (line 65) give only the win counts against
AutoETS. Fix: add that the mean difference also favors the models in all nine cells.

**31. The strata are described by their means only.** `holds with this fix`. Lines 374 to 378 say Table 7
"shows the same picture at each scale" and then describe opposite orderings in the smallest and top strata;
the table holds stratum means only. Read from the saved post-hoc file `R/posthoc/posthoc-paired-repositories.csv`
(a post-hoc look by this review), the median repository favors the local mean in every stratum, including the
top one, where the models are lower on 26 to 38 of 100 repositories in each of the nine model-horizon cells.
Fix: replace "the same picture at each scale" with a statement that these are stratum means, and either say
the typical repository by stratum is not in the declared tables or add those counts labeled post-hoc.

**32. "The zero-day penalty is small."** `holds with this fix`. The abstract (line 44), Section 6 (lines 416 to
419) and `SUMMARY.md` lines 31 and 58 to 59. The zero-day part (0.004 to 0.015, Table 6) is small beside the
mean difference (-0.101 to -0.258) but larger than every median difference in Table 3 (0.0003 to 0.0041). Fix:
write "small beside the mean gain".

**33. "As a trailing mean does after a burst."** `holds with this fix`. The abstract (lines 43 to 44), Section 6
(lines 417 to 418) and `SUMMARY.md` line 31 explain the overprediction part by bursts. No saved file
identifies bursts or post-burst windows (`R/posthoc/posthoc-report.md` defines only the three parts; the surge
regime holds 8 windows), and Section 6 itself says the decomposition "says nothing about why". Fix: drop the
clause or mark it as an untested reading.

## Related work

The literature re-check lists six items to cite. None is in `references.bib`.

**34. Islam and Mohammed (arXiv 2609.27867, 2026-08-20): the introduction.** `holds with this fix`. Lines 68 to
70 call Kim and Song "the closest precedent" for an aggregate gain beside a minority win rate; Islam and
Mohammed show aggregate and per-series rankings reversing with five zero-shot foundation models on M5
(re-check line 90). Fix: cite both and drop "closest".

**35. Garza et al., Impermanent (arXiv 2603.08707, 2026-03-10): the introduction.** `holds with this fix`. Lines
75 to 77 position the study against Borges et al. only; Impermanent is a live benchmark of daily new
stargazers on the top 400 repositories by stars (re-check line 92). The contrast the report draws, a seeded
sample from a population rather than the popular, stands. Fix: cite it beside Borges et al. with that contrast.

**36. Schoess and von Wangenheim (arXiv 2609.39386) and Ebrahim, Ali and El-Kotory (arXiv 2610.00589), both
2026-09-30: the introduction.** `holds with this fix`. The first evaluates the same three models among twelve
on sparse daily panels as event ranking, with no proper score; the second reports TimesFM 3's
nine-decile pinball loss on synthetic intermittent counts as no better than the history's empirical deciles,
which is consistent with the typical-repository result against the local mean (re-check lines 66 and 68).
Fix: cite both in the related-work paragraph.

**37. Chin, Cheng and Gunawan (arXiv 2609.13840, 2026-09-12): Section 8; Moghadasi and Ghaderi (arXiv
2609.10357, 2026-09-09): the limitations and Section 8.** `holds with this fix`. Chin et al. applied an
occurrence-times-size hurdle to frozen Chronos-2 output on monthly demand, judged by point and service measures,
which is the nearest precedent for Study 2's construction (re-check line 67). Moghadasi and Ghaderi show that
pretraining familiarity survives a later test set, the distinction the protocol draws for the October holdout
(re-check line 91; `PROTOCOL.md` line 579). Fix: cite Chin et al. in the Study 2 paragraph and Moghadasi and
Ghaderi in the contamination limitation and the holdout paragraph.

**38. Priority wording and what the report may still claim.** `holds`. Neither `main.tex` nor `SUMMARY.md`
has "first", "novel" or "no prior" as a claim; line 68 says the observation is not the first. In the light
of the six items the report may claim a registered, seeded sample from a population of GitHub repositories
stratified by day-90 activity, with a common endpoint, three pinned frozen models against two declared
references under a proper nine-decile quantile score, repository-clustered inference, and the mean and the
typical repository reported side by side, which on this panel disagree against the local mean; it may not
claim to be the first evaluation of frozen foundation models on sparse daily counts, the first forecasting
benchmark on GitHub stargazer series, or the first to show that aggregate and per-series summaries disagree.
Line 77 ("What this report adds ...") stays within that. Fix: none.

**39. The bibliography file.** `holds with this fix`. The header comment of `references.bib` restricts sources
to those in `PROTOCOL.md`, `README.md`, `docs/HISTORY.md`, "the setup record" or the memo; the entry `kim2026`
has authors "Kim and Song" without given names, journal, pages or DOI, which the re-check gives (Journal of
Industrial Distribution and Business 17(3), 89 to 97, DOI 10.13106/jidb.2026.vol17.no3.89). Fix: name the
re-check as a source in the comment, drop "the setup record", and complete `kim2026`.

## Writing and rules

**40. Plain writing.** `holds with this fix`. No marketing language, emoji or phase roadmap in `main.tex` or
`SUMMARY.md` (no non-ASCII character in either). One phrase characterizes other work without a source: "a
stress test for models that claim to forecast anything zero-shot" (lines 55 to 56). Fix: write "a hard case
for zero-shot forecasting" or cite the claim.

**41. The public boundary and Section 10.** `holds`. Outside Section 10, `main.tex` names no prompt, session,
tool or model that produced it; Section 10's quotation equals `README.md` lines 11 to 18 word for word (code
spans set in `\texttt`). `paper/PROGRESS.md` is excluded by the local git exclude list and not tracked. Fix:
none.

**42. `SUMMARY.md` against `main.tex`.** `holds with this fix`. Line 54 gives the top stratum's "median 90-day
interval width" as about 56 stars per day, the median of fit-mean widths, while `main.tex` line 352 gives
49.69, the median daily width (`R/descriptive/autoets-widths-90.csv`); lines 66 to 67 say the models "beat the
classical reference on the mean and lose to a 28-day moving average on most individual repositories", which
reads as two references where one is meant; line 67 says "The mean gain is real", while four of the nine
intervals against the local mean include zero (Table 3). Fix: use 49.69 with its name, name the local mean in
both halves of the sentence, and write "excludes zero in five of nine cells" for "is real".

**43. Length.** `holds with this fix`. No compiler is available (item 45). By count, `main.tex` has about 4,470
words of running text, 530 words of captions, nine tables, three full-width figures and 20 references; at
about 900 words to a page of 10-point text on these margins that is about five pages of prose and three and
a half of floats, about nine to ten pages, against a target of six to eight. The abstract is 288 words. Fix:
move to an appendix the registered design beyond a half-page summary (Section 3's count-source, regime, model,
score and inference detail), the version 1 must-disclose list and Table 1, Table 5, Figure 3, and Section 9
apart from the repository and the release asset with its SHA-256; shorten the abstract to about 240 words.

## LaTeX

**44. Static checks.** `holds`. Standard packages only (geometry, amsmath, booktabs, graphicx, url, natbib,
hyperref); braces balanced; every environment closed in order; the 20 `\cite` keys all in `references.bib`,
and no entry unused; every `\ref` has its `\label` and every label is referenced; the three figure files exist
as PDF and PNG; every tabular row has its specification's column count; the DOI placeholder `\reportdoi` is
present; LF line endings. Fix: none.

**45. Lines and tables likely too wide.** `holds with this fix`. Line 531, the second command in the verbatim
block, is 138 characters; in footnote-size typewriter type that is about 580 points against a 459-point text
width, past the right margin. The headers of Table 2 (line 248, nine columns) and Table 5 (line 365) are at or
past the text width at `\small` by estimate. No TeX compiler (`pdflatex`, `xelatex`, `lualatex`, `latexmk`,
`tectonic`) is on the path, so there is no page count. Fix: break the long command, shorten those headers, and
read the log for overfull boxes on the first build.

## Verdict

Of 45 verdicts, 18 hold, 26 hold with the stated fix and 1 does not hold. Every number in the tables, the
abstract and Sections 4 to 6 traces to its saved file, and the direction of every test agrees with the paired
table. The fixes change claims, not table entries: the contamination limitation (19) is contradicted by the
pinned revision dates; Section 8 omits Study 1's registered follow-up and Section 2 the prospective cohort
(18, 20); the abstract explains the mean gain by bursts no file identifies (33), calls the zero-day penalty
small without saying beside what (32), gives only win counts against AutoETS (30) and leaves out the frame's
eligibility rule (24); the strata, the AutoETS widths and the version 1 concentration figure need their labels
(26, 28, 31); and the six items of the literature re-check must be cited (34 to 37). Two numbers in
`SUMMARY.md` change (12, 42). The report may go to the author's read after the listed fixes, those to the
abstract and `SUMMARY.md` first, since the author reads those. The title holds as written.

## Regeneration

The figures above that are not in the report come from saved files and this command, run from the repository
root in PowerShell:

```powershell
@'
import json, numpy as np, pandas as pd
from scipy import stats
R = "reports/registered-2026-09-13/"
p = pd.read_csv(R + "inference/paired_repositories.csv")
for (m, ref, h), g in p.groupby(["model", "reference", "horizon"], sort=False):
    d = g.difference.to_numpy(); nz = d[d != 0]; rk = stats.rankdata(abs(nz))
    w = (nz[:, None] + nz[None, :]) / 2; hl = np.median(w[np.triu_indices(len(nz))])
    print(m, ref, h, "mean %.3f median %.4f lower %d higher %d ties %d R+ %d R- %d HL %.4f"
          % (d.mean(), np.median(d), (d < 0).sum(), (d > 0).sum(), (d == 0).sum(), rk[nz > 0].sum(), rk[nz < 0].sum(), hl))
q = pd.read_csv(R + "posthoc/posthoc-paired-repositories.csv")
q = q[(q.reference == "local_mean_28") & q.model.isin(["chronos2", "timesfm3", "timesfm2p5"])]
print(q.groupby(["sampling_stratum", "model", "horizon"]).qscore9_difference.agg(
    lower=lambda s: (s < 0).sum(), median="median").round(4).to_string())
f = pd.read_csv(R + "descriptive/autoets-fits.csv"); f = f[f.multiplicative_seasonality]
print("multiplicative fits", len(f), "by horizon", f.groupby("horizon").size().to_dict(),
      "strata", f.sampling_stratum.unique(), "repositories", f.repo_name.nunique())
t = pd.read_csv(R + "evidence/comparison/repository_2024_totals.csv")
b = 100 * (1 - t[t.metadata_stars_at_capture >= 1000].api_to_archive_ratio)
print("large: percent below %.1f to %.1f; at least 5 below: %d, %.1f to %.1f" % (b.min(), b.max(), (b >= 5).sum(), b[b >= 5].min(), b[b >= 5].max()))
m = pd.DataFrame(json.load(open(R + "run/manifest.json", encoding="utf-8-sig")))
s = pd.to_datetime(m.observation_start)
print("creation", m.creation_date.min(), m.creation_date.max(), "days", int(((pd.Timestamp("2026-08-31") - s).dt.days + 1).sum()))
'@ | .\.venv\Scripts\python.exe -
```

The protocol hashes and prefixes come from `git show 5f01769:PROTOCOL.md` and `git show df55867:PROTOCOL.md`
hashed with SHA-256; the job and approval times from the files named in item 16.

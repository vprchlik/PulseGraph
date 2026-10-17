# The paper: title, abstract and a one-page summary

Written 2026-10-16 for the author's read before the paper is posted, rewritten the same day after the paper's
review, the standing check and referee's read and the post-hoc dynamic-occurrence analysis, and rewritten on
2026-10-17 after Study 3 ran. The paper (`paper/paper.tex`) is the Study 1 report (`paper/main.tex`, which
still builds on its own) extended with Study 2's two results, two labeled post-hoc analyses, and Study 3's
registered regime family on NYC 311. Every number below comes from a named file; `paper/sources.md` gives the
row and column and the command that regenerates the file, and `paper/check_numbers.py` asserts each one in the
paper and in this page, the abstract below included. Differences are variant minus reference, so a negative
number favors the variant. The sentences the author should read are listed at the end.

## Title

Zero-shot foundation models on sparse daily counts: a registered re-evaluation on GitHub stars, a registered
occurrence test on npm downloads and a registered regime test on NYC 311 requests

## Abstract

We ask whether zero-shot time-series foundation models improve probabilistic forecasts of sparse daily
counts. The three studies are registered and population-sampled. Study 1 re-evaluates Chronos-2, TimesFM 3
and TimesFM 2.5 on daily GitHub star counts of 300 repositories sampled from 148,550, against a 28-day
local mean and weekly AutoETS under a nine-decile quantile score. The typical repository favors the local
mean, with the models lower on 46 to 89 of 300 and the signed-rank test on the reference's side in all nine
cells, while the equal-weight mean favors the models in every cell, carried by few repositories; against
AutoETS both summaries favor the models. Study 2 asks whether replacing a frozen model's zero mass with a
28-day context-only occurrence probability, keeping its completed positive law, lowers the score, on 209
hash-sampled npm download series and a 540-series synthetic grid. No pooled test favors the substitution
at q = 0.05, and two of six npm tests and all three grid tests reject against it; in the secondary
strata the substitution scores lower for 81, 60 and 66 of the 100 sparse series at horizon 7 and for 32 to
43 of the 100 dense ones. Study 3 registers that reading as a per-stratum family of 36 tests on NYC 311
service requests, 300 series in three strata, with a dynamic occurrence. For dense series the substitution
is worse than the model's own zero
mass: all six tests reject as predicted. The predicted sparse benefit is not established: one of twelve
tests rejects as predicted, and ten of twelve medians are exactly zero, both forecasts putting every decile
at zero on most very sparse series. The dynamic hurdle beats the empirical count hurdle in 14 of 18 tests.
The claim is the registered combination on those three settings, and nothing broader.

## One page for the author

### What the paper says, in seven sentences

1. Study 1 stands as the report gave it: on a population-sampled GitHub panel the three frozen models beat
   the 28-day local mean on the mean in every cell and lose to it on most individual repositories, and they
   beat weekly AutoETS on both summaries because its intervals are far too wide; the one live benchmark on
   the 400 most-starred repositories finds the typical series favoring the models, and the paper says the
   two designs disagree without attributing the difference.
2. Study 2 tested the reading that the models' size forecasts carry the gain and their occurrence forecasts
   carry the loss, by replacing each model's own zero mass with a 28-day context-only occurrence probability
   while keeping the model's completed positive law, on data declared for the purpose; of three registered
   external domains one ran, npm, beside the registered grid of 540 series.
3. On the pooled families the substitution does not help: no test favors it at q = 0.05, two of six npm
   tests and all three grid tests reject against it (twelve of the eighteen npm tests reject in all, ten for
   the model variant), and on the mean it lowers the zero-day loss and raises the positive-day
   underprediction loss by more in all nine cells; but the pooled families speak for the dense regime, and
   the declared secondary strata show the substitution lower for the typical sparse series at horizon 7 (81,
   60 and 66 of 100) and higher for the typical dense series (lower on 32 to 43 of 100), null at 30 days.
4. The model's positive law beats a shifted-Poisson count hurdle with the same occurrence rule in all six
   npm cells, a comparator that cannot fit the dense series; against the registered empirical hurdle, read
   post hoc, its advantage holds at 30 days and on dense series and not in general; on the grid, whose
   generator is the count hurdle's own family, it loses for two models and is not rejected for the third.
5. The registered dynamic count, a four-parameter hurdle with no foundation model, is the best forecaster
   on the grid after the oracle and loses to the models on npm; the post-hoc dynamic-occurrence wrapper
   shrinks the loss, removes four of the five rejections against the substitution, and never beats the
   model's own zero mass at q = 0.05, and on the grid the remaining loss is the positive law.
6. Every npm mean is carried by one series, `aggregate-error`, at 7.6 million downloads a day, so the
   medians, counts and rank tests describe the typical series of the 209 series panel; three zero days
   served by the source are scored as served under dated addition 6, and the post-hoc sensitivity without
   them changes no conclusion (none of the eighteen conclusions changes without all three days; E06 alone
   stops rejecting without the two panel-wide days).
7. Study 3 (dated addition 7, commit 3357d77) registered the regime reading as a per-stratum family of 36
   tests on NYC 311 service requests, 300 series in three strata, with the registered dynamic occurrence in
   place of the fixed one, the empirical hurdle as the count comparator and the fourth factorial cell as a
   declared secondary: 21 of 36 tests reject, the dense half of H3 is confirmed (all six tests reject as
   predicted), the sparse half is not established (one of twelve tests rejects as predicted, and ten of
   twelve medians are exactly zero, with 72 to 88 of the 100 very sparse series tied exactly because both
   forecasts put every decile at zero), and the dynamic hurdle beats the empirical hurdle in 14 of 18 tests.

### What was found

The NYC 311 panel was frozen on 2026-10-16 (276 anonymous requests, one census query per New York calendar
day, 2,959,469 requests captured, 8,469 frame cells, the first 100 complete series of each stratum: 2,002,
2,422 and 4,045 complete candidates, no unfilled slot; 39 very sparse series with no request in the stratum
window and 19 with none in the 275-day context). The targets were counted on 2026-10-17 under the signed
gate in 106 attempts of an approved 120 (983,482 requests, no source gap, a separate recomputation agreeing
with the pipeline). The run at `00fd91d` scored all 300 series in one invocation, 939 seconds inside the run
and 956 seconds for the whole process against a budget of 3,600; 39,600 forecasts, every one recomputed from
the saved deciles, targets and laws with 0 disagreements, and the two new variants' registered structure
verified on all 10,800 of their windows.

The family R01 to R36 (one BH adjustment at q = 0.05): 21 of 36 reject, 6 of them T1 tests in the dense
stratum against the dynamic hurdle as H3 predicts, 1 a T1 test in the sparse stratum for it as H3
predicts (R21, TimesFM 2.5 at horizon 7), and 14 T2 tests, all for the dynamic hurdle; no test rejects in
the direction opposite to H3's prediction and no T1 median has the opposite sign. Dense: the dynamic
hurdle is higher than the control on 55 to 72 of 100, medians 0.004 to 0.013, means 0.015 to 0.022, about
one percent of the control's score, every interval above zero; the secondary occurrence Brier score reads
the same way, and the accounting puts the loss on the zero days themselves, unlike the npm trade. Sparse:
R21 rejects as predicted, R23 leans, four medians are exactly zero. Very sparse: no test rejects, every
median is exactly zero, 72 to 88 of 100 series tie exactly, the means of 0.0005 to 0.003 ride on one series
(`Sewer Maintenance` in `09 QUEENS`); 71 to 87 of the tied series have every decile at zero under both
forecasts in every window, so the nine-decile score cannot see what the secondary Brier score sees, the
dynamic occurrence lower on 68 to 82 of the 100 in every row. T2: the dynamic hurdle beats the empirical
hurdle wherever a test rejects, 14 of 18 (all six dense rows, five of six sparse rows, the three very sparse
rows at horizon 30 by rank sum, 253 against 23). Secondary: the fixed hurdle is worse than the control on
dense and very sparse series and mixed on sparse ones; the fourth cell is far worse on dense series (means
+0.29 to +0.33) and within 0.004 of the control elsewhere; pooled in Study 2's form, every row reads as the
npm family did, and pooling does not test H3.

### What changed in the paper's claims, in five sentences

1. The title and the abstract name three studies, and the abstract states Study 3's result as confirmatory
   for dense series, not established for sparse ones, with the ties named as the reason and the empirical
   hurdle result and the three-setting scope beside it.
2. The regime reading is no longer the paper's central descriptive finding standing on secondary tables:
   its dense half is confirmatory on two domains (npm and the grid through the pooled families, NYC 311
   through the dense stratum's own six tests), and its sparse half is open, with the npm secondary reading on
   one side and the NYC 311 family on the other, and two readings given equal weight (a smaller benefit, or a
   score blind to it on all-zero forecasts).
3. The conditional sentence the paper stands behind is in two parts, dense and sparse; the model's positive
   law keeps its value against a count law on NYC 311 (14 of 18) and the discussion names where it does not
   (R14 and the three very sparse rows at a week, all with medians of exactly zero).
4. The fourth factorial cell is no longer untested: run on NYC 311 as a declared secondary, it is far worse
   than the control on dense series and better than the count hurdle that shares its positive law, so the
   discussion says Study 3 bears on the first reading of the accounting trade (the context occurrence is the
   worse occurrence forecast on dense series) and not on the second, which remains untested on npm.
5. The post-hoc stratum tests of Study 2 and its dynamic-occurrence subsection are each one paragraph with
   their tables and detail in the appendix; the Study 2 secondary counts 81, 60 and 66 stay in the body;
   the limitations add the score's blindness below one decile, the one series behind the very sparse means,
   the signed-rank test with many ties, the targets read once 47 days after the window, the legal basis of
   reuse, what a 311 request measures, what is not in the tree and the NYC 311 contamination categories; the
   claim's scope is the three settings and nothing broader.

### What it does not show

- Nothing about Wikipedia pageviews, which remain registered and not run, nor about Study 2's deferred NYC
  311 tests E19 to E54, which Study 3's own family does not replace; contamination stays unresolved for all
  three models on all three panels.
- Whether the sparse-regime benefit exists: the NYC 311 family cannot tell a small benefit from none on
  series whose deciles are all zero under both forecasts, and the paper gives the two readings equal weight.
- Nothing that separates the two readings of the accounting trade on npm or the grid: the fourth cell ran on
  NYC 311 alone, where it bears on the first reading.
- No Markov occurrence estimate, no overdispersed grid cell, nothing about the days after a release, nothing
  about human adoption; a 311 request is a complaint about a city service, not a measure of the condition.
- The very sparse means are statements about one series; the paper says so where it prints them.

### What could not be verified

- No TeX compiler or pandoc is on this machine, so there is no PDF and no page count. By the revision's
  method (running text with tables, figures and comments removed over the expanded document before the
  appendix) the body holds 15,815 words with 970 words of captions, ten tables and four figures, against
  11,938 words, 761 of captions, eight tables and three figures for the revision of 2026-10-16 counted the
  same way (the revision reported 11,990 and 748 by its own run); the appendix holds 8,446 words, 1,434
  words of captions, 27 tables and two figures. At the review's rate, about 900 words a page of text and
  half a page a float, that is about 23 pages before the references, against about 17 before Study 3. The
  bound the author set, that the body not grow beyond the revision's estimate, is not met: Study 3's four
  sections add 3,077 words and two tables and one figure, the discussion and the limitations add about 970,
  and the two compressions take 454 out. The cuts that remain the author's, because each removes a stated
  number from the body: the literature paragraph of Section 7 (about 400 words), the Study 2 design section
  (1,100 words, of which the calendar and the families could follow the rest into Appendix E), and the Study
  2 limitation items (about 1,000 words); the dynamic-occurrence prose is already cut. Beyond those, the
  36-row family table and the T2 table could move to the appendix with Figure 4 left in the body, and the
  Study 3 design section could keep only its family paragraph.
- The tie classification (71 to 87 of the tied series with all-zero deciles under both forecasts; 2 to 5 in
  the sparse rows) is computed from the 300 checkpoints, which are not in the tree; the checker recomputes
  it when they are present and records a skip otherwise.
- The contexts-at-each-origin table (Table 30) is printed by the run's table script from the target signals,
  which are not in the tree; the checker asserts the results page's rows as text, not a recomputation.
- The source's terms pages were read in a desktop browser on 2026-10-17 and are cited as the record holds
  them (their text hashes are in `source-terms.md`); they were not re-opened for this paper. The Open Data
  Law was not read.
- The 300 checkpoints (645 MB) and the target signals are not published yet; the paper says they are to be
  published as a release asset. The release assets of the two Study 2 runs and the 209 series' daily counts
  are likewise still to be published.

### Sentences to read

1. The regime sentence (Section 10, "The regime reading"): "So the substitution hurts the typical dense
   series and the short-memory cells, helps the typical sparse series at horizon 7, and is null at 30 days.
   This was the paper's central descriptive finding, a reading of declared secondary tables and not a
   confirmatory result; Study 3 registered it as a per-stratum family and tested it on a second domain."
2. The Study 3 verdict (Section 14, "Read together"): "On NYC 311 the half of H3 that concerns dense series
   is confirmed for every model and horizon, and the half that concerns sparse and very sparse series is
   not: of its twelve tests one rejects in the predicted direction and eleven do not, ten of the twelve
   medians are exactly zero, and on the very sparse series the registered score cannot see the difference
   that the secondary occurrence score does."
3. The ties sentence (Section 14, "Very sparse series"): "The ties arise from the score itself: QScore9
   reads nine deciles of a count law, which are integers, so two forecasts whose deciles coincide in every
   window score identically whatever the target is, and a difference in occurrence probability smaller than
   one decile is invisible to it."
4. The conditional sentence (Section 15, "What the three studies say together"): "For dense series, a
   context-only or dynamic occurrence estimate does not improve a frozen model's own completed zero mass
   under this score, on npm, the grid and NYC 311, and this is confirmatory on two domains: on npm and the
   grid through the pooled families, which the dense series decide, and on NYC 311 through the dense
   stratum's own six tests. For sparse series the question is open, with the npm secondary reading on one
   side and the NYC 311 family on the other."
5. The two-readings sentence (Section 15): "Study 3 bears on the first and not on the second. ... On that
   domain the substitution loses on dense series because the context estimate is the worse occurrence
   forecast."
6. The T2 sentence (Section 14, "Against the empirical hurdle"): "H3 predicts nothing for T2; the reading is
   that the model's positive law, carried with the dynamic occurrence, keeps its value on this domain against
   a count law whose positive law can fit a dense series, except in the four rows whose medians are exactly
   zero."
7. The scope sentence (Section 15, "What the paper claims"): "The paper claims the registered combination
   and nothing broader: a context-only or dynamic occurrence probability substituted for the zero mass of
   frozen Chronos-2 and TimesFM forecasts, their completed positive law kept, ... on a hash-sampled panel of
   daily npm download counts, on the registered synthetic grid and, stratum by stratum, on a stratified
   panel of daily NYC 311 service-request counts."
8. The terms sentence (Section 13, "The source, its terms and its time basis"), since the legal basis of
   reuse is the author's call: "The dataset's metadata states no license and links no terms page; the city
   website's terms of use, read on 2026-10-17, ... say nothing specific about datasets, their license or
   attribution; the Open Data Law that the program names as its basis was not read."
9. The report's one changed sentence (`main.tex`, Section 8) is unchanged since the revision: "As of
   2026-10-12 no Study 2 target value, forecast or score existed; both components fixed for the October 2026
   paper, the synthetic grid and the npm external run, ran on 2026-10-15 and are reported in the paper that
   extends this report."

# The paper: title, abstract and a one-page summary

Written 2026-10-16 for the author's read before the paper is posted, and rewritten the same day after the
paper's review, the standing check and referee's read, and the post-hoc dynamic-occurrence analysis. The
paper (`paper/paper.tex`) is the Study 1 report (`paper/main.tex`, which still builds on its own) extended
with Study 2's two results and two labeled post-hoc analyses. Every number below comes from a named file;
`paper/sources.md` gives the row and column and the command that regenerates the file, and
`paper/check_numbers.py` asserts each one in the paper and in this page, the abstract below included.
Differences are model minus reference, so a negative number favors the model. The sentences the author
should read are listed at the end.

## Title

Zero-shot foundation models on sparse daily counts: a registered re-evaluation on GitHub stars and a
registered occurrence test on npm downloads

## Abstract

We ask whether zero-shot time-series foundation models improve probabilistic forecasts of sparse daily
counts, and test one mechanism. Both studies are registered and population-sampled. Study 1 (protocol
commit 5f01769, 2026-09-12) re-evaluates Chronos-2, TimesFM 3 and TimesFM 2.5 on daily GitHub star
counts of 300 repositories sampled from 148,550, against a 28-day local mean and weekly AutoETS under a
nine-decile quantile score. The typical repository favors the local mean: the models score lower on 46 to
89 of 300 and the signed-rank test rejects on the reference's side in all nine cells, while the equal-weight
mean favors the models in every cell, carried by few repositories; against AutoETS both summaries favor the
models. Study 2 (commit df55867, 2026-09-14) asks whether replacing a frozen model's zero mass with
a 28-day context-only occurrence probability, keeping its completed positive law, lowers the score, on an
npm download panel of 209 hash-sampled series and a registered 540-series synthetic grid; two registered
domains are deferred. No pooled test favors the substitution at q = 0.05, and two of six npm tests and
all three grid tests reject against it. The answer depends on the regime: in the declared secondary strata
the substitution scores lower for 81, 60 and 66 of the 100 sparse series at horizon 7 and for 32 to 43 of
the 100 dense ones, so the pooled families speak for the dense regime. The model's positive law beats a
shifted-Poisson count hurdle in all six npm cells, and the registered dynamic count beats every model on
the grid. Every npm mean is carried by one series at 7.6 million downloads a day; the medians, counts and
rank tests describe the typical series. The claim is the registered combination on npm downloads and the
grid, and nothing broader.

## One page for the author

### What the paper says, in six sentences

1. Study 1 stands as the report gave it: on a population-sampled GitHub panel the three frozen models beat
   the 28-day local mean on the mean in every cell and lose to it on most individual repositories, and they
   beat weekly AutoETS on both summaries because its intervals are far too wide; the one live benchmark on
   the 400 most-starred repositories finds the typical series favoring the models, and the paper says the
   two designs disagree without attributing the difference.
2. Study 2 tested the reading that the models' size forecasts carry the gain and their occurrence forecasts
   carry the loss, by replacing each model's own zero mass with a 28-day context-only occurrence probability
   while keeping the model's completed positive law, on data declared for the purpose; of three registered
   external domains one ran, npm, beside the registered grid.
3. On the pooled families the substitution does not help: no test favors it at q = 0.05, two of six npm
   tests and all three grid tests reject against it, and on the mean it lowers the zero-day loss and raises
   the positive-day underprediction loss by more in all nine cells; but the pooled families speak for the
   dense regime, and the declared secondary strata show the substitution lower for the typical sparse series
   at horizon 7 (81, 60 and 66 of 100) and higher for the typical dense series (lower on 32 to 43 of 100),
   null at 30 days.
4. The model's positive law beats a shifted-Poisson count hurdle with the same occurrence rule in all six
   npm cells, a comparator that cannot fit the dense series; against the registered empirical hurdle, read
   post hoc, its advantage holds at 30 days and on dense series and not in general; on the grid, whose
   generator is the count hurdle's own family, it loses for two models and is not rejected for the third.
5. The registered dynamic count, a four-parameter hurdle with no foundation model, is the best forecaster
   on the grid after the oracle and loses to the models on npm; the post-hoc dynamic-occurrence wrapper
   shrinks the loss, removes four of the five rejections against the substitution, and never beats the
   model's own zero mass at q = 0.05, and on the grid the remaining loss is the positive law.
6. Every npm mean is carried by one series, `aggregate-error`, at 7.6 million downloads a day, so the
   medians, counts and rank tests describe the typical series; three zero days served by the source are
   scored as served under dated addition 6, and the post-hoc sensitivity without them changes no conclusion
   (none of the eighteen conclusions changes without all three days; E06 alone stops rejecting without the
   two panel-wide days).

### What was found

The synthetic grid ran on 2026-10-15 at `3fc3411` (540 series, 1,317 seconds, 55,080 forecasts, no failure;
every score recomputed with a largest difference of 0.0). The family S01 to S06: each hurdle variant scores
0.086 to 0.088 above its completed control, every interval above zero, lower on 5 or 6 of 30 blocks, all
three rejecting; the Chronos-2 and TimesFM 2.5 hurdles score 0.052 and 0.061 above the count hurdle and
reject; the TimesFM 3 hurdle differs by 0.022 and leans the same way without rejection. Five of six reject,
all against the hurdle. The oracle, a diagnostic, has the lowest mean score at both horizons, and no
forecaster scores below it in 17 of 18 cells (the dynamic count ties it exactly in three).

The npm run followed the same day at `3057b16` (209 series, 692 seconds, 20,064 forecasts, no failure; the
integrity recomputation found 0 disagreements). The family E01 to E18: twelve of the eighteen reject, ten
for the model variant and two against the hurdle. Hurdle against its control: means +90 to +254 with every
interval above zero (the dominant series), medians within 0.014 of zero, the hurdle lower on 81 to 121 of
209, rejections against it in E10 and E16; in E01 the typical series leans to the hurdle without rejection.
Hurdle against the count hurdle: all six reject for the model's positive law, medians -0.0063 to -0.072, the
Brier difference exactly zero because both sides share the occurrence rule. Raw deciles against the local
mean: four of six reject for the model (E06, E09, E12, E18); Chronos-2 and TimesFM 2.5 at horizon 7 do not.
The context-scaled score, the registered scale-free secondary, favors the hurdle over its control at
horizon 7 for all three models and includes zero at horizon 30, agreeing with the medians.

The three zero days: the download API served 0 for all 209 series on 2026-07-12 and 2026-08-14, and 0 for
`aggregate-error` on 2026-06-25, between days of millions; npm's own records say nothing about them, and a
public thread records two earlier whole-day zeros that were later restored. The registered analysis of the
data as served stands (dated addition 6). Without all three days none of the eighteen conclusions changes;
without the two panel-wide days E06 alone stops rejecting (adjusted p 0.060 against 0.012).

### What changed in the paper's claims, in five sentences

1. The abstract and the results no longer say that no comparison favors the substitution; they say that no
   test favors it at q = 0.05, that in E01 the typical series leans to it, and that the answer depends on
   the regime, with the exact stratum counts and the pooling named as the reason the confirmatory families
   speak for the dense regime.
2. The claim is narrowed to the registered combination on daily npm download counts and the registered
   grid, with Study 1's GitHub star counts entering through the raw comparison alone, and the two deferred
   domains and the lapsed holdout are stated in the abstract and the first paragraph of Section 7.
3. The positive-law result names the shifted Poisson it beats, says that the Poisson cannot fit the dense
   series, and puts the registered empirical hurdle beside it, labeled post hoc, where the advantage holds
   at 30 days and on dense series and not in general; S04 is described as leaning, not tying.
4. The positive law is described as the completed marginal truncated at one rather than a size forecast,
   the double counting of zeros that this implies is stated as a second reading of the accounting trade,
   the accounting trade itself is stated for the means with the typical npm series not following it, and
   the missing fourth factorial cell (the model's own occurrence with a count positive law) is named as
   untested.
5. The dynamic count is read as the best non-oracle forecaster on the grid, the post-hoc dynamic-occurrence
   analysis is reported in a labeled subsection with one table, the oracle's three exact ties are stated,
   the sensitivity is placed before addition 6 in time, the daily counts are said to be to be published,
   and the process paragraphs (the runs, the inventory and pull, the frame, completion and baselines) sit
   in the appendix.

### What it does not show

- Nothing about NYC 311 or Wikipedia, which are registered and not run, nor about the October holdout,
  whose freeze lapsed, nor about Study 1's follow-up cohort, nor about unseen entities: contamination stays
  unresolved for all three models, and the npm targets are mixed by model availability.
- No registered test of the regime dependence: it is read from declared secondary tables and post-hoc
  stratum tests, and a registered test of it on a second domain is named as the natural next study.
- Nothing that separates the two readings of the accounting trade; the fourth factorial cell is untested.
- Nothing about why the positive-law contrast reverses between npm and the grid, beyond what the accounting
  shows; the paper reports the reversal and does not explain it.
- Nothing about human adoption: an npm download is a tarball request, mirrors and automated clients
  included, which is also why only 9 of 9,998 complete candidates were sparse enough for the third stratum.
- The npm means are statements about one series; the paper says so wherever it prints a mean.

### What could not be verified

- No TeX compiler or pandoc is on this machine, so there is no PDF and no page count. By one method, running
  text with tables, figures and comments removed over the expanded document before the appendix, the
  paper's body holds 11,989 words with 748 words of captions, eight tables and three figures, beside the
  report's 4,222 words with 294 words of captions, four tables and two figures; the appendix holds 5,578
  words, eighteen tables and two figures. At the review's rate of about 900 words a page of text and half a
  page a float, that is about seventeen pages before the references, against the aim of fourteen; before
  the revision the estimate was about eighteen with ten tables and four figures in the body. The revision
  moved the process to the appendix and added the regime reading, the empirical hurdle, the dynamic count
  and the post-hoc subsection, which together outweigh the moves. The next cuts, each the author's choice
  because each removes a stated number from the body: the literature paragraph of Section 7 (about 400
  words, which could become five sentences with the citations kept), the Study 2 design section (1,100
  words, of which the calendar and the families could follow the rest into Appendix E), the
  dynamic-occurrence subsection's prose (about 650 words, which could become a paragraph beside its table),
  and the limitation items (1,000 words).
- Whether the three zero days are gaps in npm's counts: no npm record names them; the reading rests on
  npm's earlier episodes, documented in the public thread the paper now cites.
- The release assets (results.parquet, the 540 synthetic checkpoints, the 209 npm checkpoints) and the 209
  series' daily counts do not exist as published files yet; the paper says they are to be published.
- The titles, author lists and version dates of the seven new arXiv items and the Zenodo record were read
  from their abstract pages on 2026-10-16; the npm community thread and the full texts of the Impermanent
  and the marketplace-panel papers were not re-opened and are cited as the standing check of 2026-10-16
  recorded them.
- The post-hoc stratum tests, the empirical-hurdle counts and the dynamic count's block counts are not in
  any saved table of the two runs; the checker recomputes them from the saved per-series score files, and
  they match the standing check's figures.

### Sentences to read

1. The regime sentence (Section 10, "The regime reading"): "So the substitution hurts the typical dense
   series and the short-memory cells, helps the typical sparse series at horizon 7, and is null at 30 days.
   This is the paper's central descriptive finding; it is a reading of declared secondary tables, not a
   confirmatory result, and a registered test of the substitution by regime, on a second domain, is the
   natural next study."
2. The mechanism sentence (Section 11, "What the two studies say together"): "The sentence the paper stands
   behind is therefore conditional: a context-only occurrence estimate does not improve a frozen model's
   own completed zero mass under this score on the pooled npm panel or the pooled grid, hurts the typical
   dense series, and helps the typical sparse series at a week's horizon; a dynamic occurrence estimate
   narrows the gap and does not close it; and a registered test of the regime dependence on a second
   domain is the next study."
3. The two-readings sentence (Section 11, "Two readings of the accounting trade"): "The first reading of
   the net sign, that the context-only occurrence estimate is worse than the model's own zero mass, and the
   second, that the truncated law is not the model's size forecast so that any added zero mass hurts, are
   both consistent with every number here."
4. The positive-law sentence (Section 10, "The model's positive law against a fixed count hurdle"): "So the
   model's completed size forecast beats a shifted Poisson where the Poisson is misspecified and not where
   it is the generator's own law; against an empirical positive law its advantage holds at 30 days and on
   dense series, not in general."
5. The dominant-series sentence (Section 9, "One series at 7.6 million downloads a day"): "This is a
   property of the registered design, not a defect found in it, and the paper names the series wherever it
   prints an unscaled npm mean."
6. The zero-day sentence (Section 10, "Three zero days in the npm targets"): "The registered completeness
   rule, fixed before any target was seen, does not test for a source-wide zero, so the three days were
   scored as served; each falls in one horizon-30 block and in no horizon-7 block."
7. The report's one changed sentence (`main.tex`, Section 8): "As of 2026-10-12 no Study 2 target value,
   forecast or score existed; both components fixed for the October 2026 paper, the synthetic grid and the
   npm external run, ran on 2026-10-15 and are reported in the paper that extends this report."

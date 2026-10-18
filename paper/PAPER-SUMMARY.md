# The paper: title, abstract and a one-page summary

Written 2026-10-16 for the author's read before the paper is posted, rewritten after each read, rewritten on
2026-10-17 when the paper was reorganized by question, and rewritten on 2026-10-18 when the fixes of the
review of the reorganized paper were applied. The paper (`paper/paper.tex`) reports three registered,
population-sampled studies as one design run in three steps; the Study 1 report (`paper/main.tex`) still
builds on its own and is unchanged. Every number below comes from a named file; `paper/sources.md` gives the
row and column and the command that regenerates the file, and `paper/check_numbers.py` asserts each one in
the paper and in this page, the abstract and the quoted sentences included. Differences are variant minus
reference, so a negative number favors the variant. The sentences the author should read are listed at the
end.

## Title

Size, not occurrence: what zero-shot foundation models add on sparse daily counts

## Abstract

We ask where zero-shot time-series foundation models add value on sparse daily counts, in three registered,
population-sampled studies, one design in three steps, on frozen Chronos-2, TimesFM 3 and TimesFM 2.5. On
daily GitHub star counts of 300 repositories sampled from 148,550, the models beat a 28-day local mean on
the mean in every cell and lose on the typical repository, lower on 46 to 89 of 300. Study 2 replaces each
model's zero mass with a 28-day context-only occurrence probability, keeping its completed positive law, on
209 hash-sampled npm download series and a 540-series synthetic grid. No pooled test favors the substitution
at q = 0.05, two of six npm tests and all three grid tests reject against it, and the model's positive law
beats a shifted-Poisson count hurdle in all six npm cells; by stratum, at a week, it scores lower for 81, 60
and 66 of 100 sparse series and 32 to 40 of 100 dense ones. Study 3 registers that reading as a per-stratum
family of 36 tests on 300 NYC 311 series in three strata, with a dynamic occurrence: on dense series all six
tests reject as predicted; on the sparse and very sparse strata one of twelve does, and ten of twelve medians
are exactly zero. On most very sparse series the completion rule fixes the models' occurrence probability
between 0.0607 and 0.1, so nothing about occurrence can be read there. The models' value is in the size of
positive days. Under the registered score their own zero-day probability is at least as good as a context
estimate on dense series in all three settings; a context estimate wins the typical series on sparse npm at
a week, in the grid's sparsest cells at a month and in one registered NYC 311 test.

## One page for the author

### The thesis

The frozen models' value on sparse daily counts is in the size of the positive days: their gain over a
28-day local mean comes from positive days, where the local mean overpredicts on GitHub stars and npm
downloads and underpredicts on NYC 311 requests, with 12 to 29 percent of the NYC 311 gain on zero days.
Under the registered quantile score their own probability of a zero day is at least as good as a
context-only estimate on dense series in all three settings. A context estimate beats the model's own zero
mass on the typical series in four places, each a sparse stratum, a very sparse cell or the month horizon:
the sparse npm stratum at a week (a secondary reading on one domain; the TSB hurdle wins the same series),
the grid's cells with zero probability 0.95 at a month, one registered test of six on NYC 311's sparse
stratum (R21), and dense npm series at a month under the occurrence Brier score alone. On the natural
panels' series that are zero nine days in ten the completion rule, not the model, sets the occurrence
probability (between 0.0607 and 0.1), the quantile score ties, and nothing about occurrence can be read from
the models.

### What the paper says, in six sentences

1. Against a 28-day local mean the frozen models' gain is on positive days, where the local mean
   overpredicts on GitHub stars and npm downloads and underpredicts on NYC 311: the mean favors the models in
   every cell of every panel, carried by few series (one series at 7.6 million downloads a day on npm), while
   the typical series favors the models in four of six npm cells, splits on NYC 311 with three medians below
   zero, two above and one exactly zero, and favors the local mean on GitHub, where the models are lower on
   only 46 to 89 of 300.
2. Replacing a model's own zero mass with a context-only occurrence estimate makes the forecast worse on
   dense series in all three settings under the registered quantile score, and under the occurrence Brier
   score on NYC 311 and at a week on npm but not at a month on npm, where the Jeffreys estimate is the better
   occurrence forecast on 57 to 62 of 100; on NYC 311 this is confirmatory (all six dense tests reject as
   predicted, 21 of 36 tests reject in all, none against the prediction), and on npm and the grid the pooled
   families speak for it (no pooled test favors the substitution at q = 0.05; two of six npm tests and all
   three grid tests reject against it; twelve of the eighteen npm tests reject in all).
3. A context estimate beats the model's own zero mass on the typical series in four places, all sparse
   strata, very sparse cells or the month horizon: the sparse npm stratum at a week under all three scores
   (lower for 81, 60 and 66 of 100; the TSB hurdle wins 77, 61 and 74) and not at a month by the
   within-stratum test; the grid's cells with z = 0.95 at a month (lower in 21 to 26 of 30 replicate blocks
   under all three scores); one registered test of six on NYC 311's sparse stratum, R21, where four of six
   medians are exactly zero; and dense npm at a month under the Brier score alone.
4. On NYC 311's very sparse series the registered construction cannot ask the occurrence question: 72 to 88
   of the 100 series tie exactly, 580, 544 and 588 of the 600 completed forecasts sit on the completion floor
   at their first lead (561, 505 and 572 at every lead), and the Brier score's separation (the dynamic
   occurrence lower on 68 to 82 of 100) compares the Jeffreys fallback near 0.017, which 58 of the 100 series
   take at the first origin, with a constant near 0.061 that the completion formula predicts.
5. The model's positive law beats a shifted-Poisson count law wherever that law is misspecified (all six
   npm cells; the fourth cell far worse than the control on dense series on every panel) and loses to it
   where it is the generator's own (the grid); against an empirical law it keeps its value on dense series
   only, and T2 rejects for the dynamic hurdle against the empirical hurdle in 14 of 18 registered tests on
   NYC 311, three of them by rank sum with a median of exactly zero.
6. The registered dynamic count, a discounted analogue of TSB with no foundation model, is the best
   forecaster on the grid at a month after the oracle, behind five model variants at a week, and loses to
   the models on npm and NYC 311 on the mean and by count; the post-hoc dynamic-occurrence wrapper removes
   four of the five rejections against the substitution and never beats the model's own zero mass at
   q = 0.05.

### What changed against `711e2ff`, in three sentences

1. The thesis names where the gain over the local mean sits on each panel and the four places where a
   context estimate beats the model's own zero mass on the typical series, in place of "the one place",
   restricts the dense claim to the registered score and the interface limit to the natural panels, and the
   grid's z = 0.95 cells at a month are reported as a win for the substitution, not a tie.
2. The two-readings paragraph moved whole to the appendix beside the fourth-cell table, its npm attribution
   at a month corrected to the Brier score (under the count law the model's own zero mass stays ahead) and
   labeled post hoc, with one sentence left in the discussion; the sparse NYC 311 count is one of six T1
   tests with four zero medians, the fourteen T2 rejections are stated as rejections with their three
   zero-median rows, the context-scaled sentence, the exclusion of Croston and TSB, the dynamic count's
   natural-panel sentence, Figure 3's npm caption, the floor counted at every lead, the fallback named, the
   horizons left out, the three redundant labels, the code identifiers in prose, the zero-median rule stated
   once, and the citation fixes (the quantile-drop sentence, the pooled hurdle with forgetting, Chronos
   version 3, the TSB hurdle's weight and rules, the point-method caveat, Chin et al.'s hurdle) were applied.
3. The broken reference to Table 4 in Section 5 was repaired and a check for eaten commands added to the
   checker; Table 4 and Table 5 abbreviate "Lower / tied / higher" to "L / T / H" with the expansion in the
   caption, and the five overflowing appendix tables were narrowed the same way; the body is 7,495 words
   against 7,499.

### What it does not show

- Nothing about Wikipedia pageviews, Study 2's deferred tests E19 to E54, the October holdout or the
  November round, all registered and not run; contamination stays unresolved for all three models.
- Whether a sparse-regime benefit exists beyond the named places: on NYC 311's sparse stratum the record is
  one rejection of six T1 tests, and on very sparse series the registered construction cannot ask the
  question.
- Which reading of the accounting trade operates in general: the record supports the first on dense NYC 311
  series and at a week on the grid, the second at a month on the grid and, on the Brier score, on npm, and
  nothing beyond that.
- Anything about models with another output interface (a mixture, sample paths, Chronos-2's own 21 levels);
  the next study's design is named in the discussion in one sentence, and the deferred npm replication at a
  week is the piece a reviewer could ask for.
- The npm means are statements about one series (7.6 million downloads a day); the very sparse NYC 311
  means ride on one series; the paper says so where it prints them.

### What could not be verified

- No TeX compiler or pandoc is on this machine, so there is no PDF and no page count; the static checks
  (every input present, braces and environments balanced, every label referenced, every citation in the
  bibliography, every tabular row with its column count, every figure file present, no eaten command) passed.
- The table widths are estimates from the Computer Modern metrics, good to a few percent: Table 4 about 416
  pt (433 by the cruder estimate) against 461 after the header change, Table 5 about 442 (460); the five
  appendix tables the review named at 396 (412), 451, 449, 452 and 450; Tables 1 to 3 at 448, 460 and 465,
  the last within the estimate's error; `tab:s2ext`, `tab:s2syn`, `tab:s2cells`, `tab:s3direction` and
  `tab:s3brier` at 466 to 472 by this estimate, also within its error. Table 4 is to be read from the first
  build's log.
- By the revision's method (the expanded paper before `\appendix` with comments, floats and commands removed,
  captions counted apart) the body holds 7,495 words of running text, 1,049 words of captions, five tables and
  four figures; at 900 words a page and half a page a float that is about 12.8 pages, and about 13.8 if the
  two full-page tables are counted as a page each. The move of the two-readings paragraph took about 230
  words out of the body and the review's fixes put about as many back; the aim was about 7,000 words, and the
  cut is the author's.
- The completion-floor counts (580, 544 and 588 at the first lead; 561, 505 and 572 at every lead; 150, 62
  and 230; 2, 0 and 0), the all-zero tie classification (71 to 87) and the dynamic hurdle's fallback counts
  (58 series at 0.5/29 and 16 at 1.5/29 at the first origin) are computed from the 300 NYC 311 checkpoints,
  which are not in the tree; the checker recomputes them when the checkpoints are present and records a skip
  otherwise.
- The Chronos citation now names arXiv 2403.07815 version 3, the version the step-back read of 2026-10-17
  opened; its page was not opened again for this revision (no network).
- The 300, 540, 209 and 300 checkpoints and the daily counts of the npm and NYC 311 series are not released
  yet; the paper says they are to be released as release assets.

### Sentences to read

1. The thesis (Section 1): "This paper's answer is that the value is in the size, not the occurrence."
2. The gain (Section 1): "On sparse daily counts the frozen models' gain over a 28-day local mean comes from
   positive days: where the local mean overpredicts on GitHub stars and npm downloads, and where it
   underpredicts on NYC 311 requests, with 12 to 29 percent of that gain on zero days."
3. The places (Section 1): "A context estimate beats the model's own zero mass on the typical series in four
   places, each a sparse stratum, a very sparse cell or the month horizon: the sparse npm stratum at a week, a
   secondary reading on one domain; the grid's cells with zero probability 0.95 at a month; one registered
   test of six on NYC 311's sparse stratum; and, under the occurrence Brier score alone, dense npm series at
   a month."
4. The exclusion (Section 2): "The protocol excludes Croston and TSB by name without a reason; neither carries
   a predictive law of its own, and the dynamic count, read as such, plays TSB's part."
5. The floor (Section 3): "On a series that is zero nine days in ten the ``model's own zero mass'' is
   therefore set by this rule."
6. The sparse verdict (Section 5): "So on sparse NYC 311 series the score sees the substitution, and the npm
   reading did not carry over."
7. The two readings (Appendix, the Study 3 tables): "Which reading operates depends on the panel and the
   horizon, and nothing beyond that is attributed."
8. The ledger's cause (Section 3): "The three lapses of 2026-10-12 have one cause, that no work was done in
   the repository between 2026-09-14 and 2026-10-11:" ... (the sentence continues).

## The record behind the summary

The NYC 311 run (dated addition 7, commit 3357d77) scored all 300 series in 956 seconds; the family R01 to
R36 has 21 of 36 rejections, none against the predicted direction, with 72 to 88 of the 100 very sparse
series tied exactly in each T1 row. On the npm panel of 209 series, without the three served zero days none
of the eighteen conclusions changes. The post-hoc benchmark of 2026-10-17 placed the TSB hurdle and the fourth
cell on all three panels under a specification fixed before any of its scores existed. The report's source
still expands to its frozen commit apart from its one dated sentence, and no entry of any family table
changed.

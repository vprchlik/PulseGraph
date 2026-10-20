# The paper: title, abstract and a one-page summary

Written 2026-10-16 for the author's read before the paper is posted, rewritten after each read, rewritten on
2026-10-17 when the paper was reorganized by question, on 2026-10-18 when the fixes of the review of the
reorganized paper were applied, and on 2026-10-20 when the body and the abstract were revised for clarity and
then set in a formal academic register. The paper (`paper/paper.tex`) reports three registered, population-sampled studies as one design run
in three steps; the Study 1 report (`paper/main.tex`) still builds on its own and is unchanged. Every number
below comes from a named file; `paper/sources.md` gives the row and column and the command that regenerates
the file, and `paper/check_numbers.py` asserts each one in the paper and in this page, the abstract and the
quoted sentences included. Differences are variant minus reference, so a negative number favors the variant.
The sentences the author should read are listed at the end.

## Title

Size, not occurrence: what zero-shot foundation models add on sparse daily counts

## Abstract

Three registered, population-sampled studies, one design in three steps, ask where frozen zero-shot
time-series foundation models (Chronos-2, TimesFM 3 and TimesFM 2.5) add value on sparse daily counts. On daily
GitHub star counts of 300 repositories sampled from 148,550, the models beat a 28-day local mean on the mean
in every cell but lose on the typical repository, lower on 46 to 89 of 300. Study 2 replaces each model's
zero mass with a 28-day context-only occurrence probability, keeping its completed positive law, on 209
hash-sampled npm download series and a 540-series synthetic grid. No pooled test favors the substitution at
q = 0.05, and two of six npm tests and all three grid tests reject against it. By stratum, at a week, it
scores lower for 81, 60 and 66 of 100 sparse series and 32 to 40 of 100 dense ones. The model's positive law
beats a shifted-Poisson count hurdle in all six npm cells. Study 3 registers the regime reading as a
per-stratum family of 36 tests on 300 NYC 311 series in three strata, with a dynamic occurrence. On dense
series all six tests reject as predicted, but on the sparse and very sparse strata one of twelve does, and
ten of twelve medians are exactly zero. On most very sparse series the completion rule fixes the models'
occurrence probability between 0.0607 and 0.1, so nothing about occurrence can be read there. The models'
value is in the size of positive days. Under the registered score their own zero-day probability is at least
as good as a context estimate on dense series in all three settings. A context estimate wins the typical
series on sparse npm at a week, in the grid's sparsest cells at a month and in one registered NYC 311 test.

## One page for the author

### The thesis

The frozen models' value on sparse daily counts is in the size of the positive days. Their gain over a
28-day local mean comes from positive days, where the local mean overpredicts on GitHub stars and npm
downloads and underpredicts on NYC 311 requests, with 12 to 29 percent of the NYC 311 gain on zero days.
Under the registered quantile score their own probability of a zero day is at least as good as a
context-only estimate on dense series in all three settings. A context estimate beats the model's own zero
mass on the typical series in four places, each a sparse stratum, a very sparse cell or the month horizon.
They are the sparse npm stratum at a week (a secondary reading on one domain, where the TSB hurdle wins the
same series), the grid's cells with zero probability 0.95 at a month, one registered test of six on NYC
311's sparse stratum (R21), and dense npm series at a month under the occurrence Brier score alone. On the
natural panels' series that are zero nine days in ten the completion rule, not the model, sets the
occurrence probability (between 0.0607 and 0.1). There the quantile score ties, and nothing about
occurrence can be read from the models.

### What the paper says, in six points

1. Against a 28-day local mean the frozen models' gain is on positive days. Those are the days where the
   local mean overpredicts on GitHub stars and npm downloads, and where it underpredicts on NYC 311. The
   mean favors the models in every cell of every panel, carried by few series (one series at 7.6 million
   downloads a day on npm). The typical series favors the models in four of six npm cells, splits on NYC
   311 with three medians below zero, two above and one exactly zero, and favors the local mean on GitHub,
   where the models are lower on only 46 to 89 of 300.
2. Replacing a model's own zero mass with a context-only occurrence estimate makes the forecast worse on
   dense series in all three settings under the registered quantile score. Under the occurrence Brier score
   it is worse on NYC 311 and at a week on npm, but not at a month on npm, where the Jeffreys estimate is
   the better occurrence forecast on 57 to 62 of 100. On NYC 311 this is confirmatory, with all six dense
   tests rejecting as predicted and 21 of 36 tests rejecting in all, none against the prediction. On npm and
   the grid the pooled families speak for it. No pooled test favors the substitution at q = 0.05, two of
   six npm tests and all three grid tests reject against it, and twelve of the eighteen npm tests reject in
   all.
3. A context estimate beats the model's own zero mass on the typical series in four places, all sparse
   strata, very sparse cells or the month horizon. The first is the sparse npm stratum at a week under all
   three scores (lower for 81, 60 and 66 of 100, with the TSB hurdle winning 77, 61 and 74), and not at a
   month by the within-stratum test. The others are the grid's cells with z = 0.95 at a month (lower in 21
   to 26 of 30 replicate blocks under all three scores), one registered test of six on NYC 311's sparse
   stratum, R21, where four of six medians are exactly zero, and dense npm at a month under the Brier score
   alone.
4. On NYC 311's very sparse series the registered construction cannot ask the occurrence question. There 72
   to 88 of the 100 series tie exactly, and 580, 544 and 588 of the 600 completed forecasts sit on the
   completion floor at their first lead (561, 505 and 572 at every lead). The Brier score's separation (the
   dynamic occurrence lower on 68 to 82 of 100) compares the Jeffreys fallback near 0.017, which 58 of the
   100 series take at the first origin, with a constant near 0.061 that the completion formula predicts.
5. The model's positive law beats a shifted-Poisson count law wherever that law is misspecified (all six
   npm cells, and the fourth cell far worse than the control on dense series on every panel) and loses to
   it where it is the generator's own (the grid). Against an empirical law it keeps its value on dense
   series only. T2 rejects for the dynamic hurdle against the empirical hurdle in 14 of 18 registered tests
   on NYC 311, three of them by rank sum with a median of exactly zero.
6. The registered dynamic count, a discounted analogue of TSB with no foundation model, is the best
   forecaster on the grid at a month after the oracle and behind five model variants at a week. It loses to
   the models on npm and NYC 311 on the mean and by count. The post-hoc dynamic-occurrence wrapper removes
   four of the five rejections against the substitution and never beats the model's own zero mass at
   q = 0.05.

### What changed in the revision of 2026-10-20, in three sentences

1. The body's sentences were split and linked, one finding to a sentence, with full stops and linking words
   in place of the colons and semicolons that chained them, openers varied, and a sentence after the
   numbers that says in words what they mean.
2. The body and the abstract are set in a formal academic register without the first person: choices are
   stated through the study, the protocol or the design, readings are labeled as readings, registered results
   stay unhedged, and the discussion states what each registration expected, what was observed, what a
   follow-up study would register and the scope of the claim.
3. No number, claim, status label, defined term, citation or cross-reference changed, apart from one
   correction to the record (the ledger paragraph of Section 3 now says that the npm download API served zero
   for every series on two days and for the largest series on the third, as Section 8 and the appendix
   state); the tables, captions, figures and appendix are untouched, and the quoted sentences below appear in
   their new wording.

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
  the next study's design is named in the discussion, and the deferred npm replication at a week is the
  piece a reviewer could ask for.
- The npm means are statements about one series (7.6 million downloads a day); the very sparse NYC 311
  means ride on one series; the paper says so where it prints them.

### The build and the length

- Both documents were built on 2026-10-20 with MiKTeX 25.12 (pdfTeX 1.40.28), each from a clean folder under
  the ignored `data/cache/build/`: `pdflatex`, `bibtex`, then `pdflatex` three times for the paper and twice
  for the report. Neither log holds an error, an undefined reference or citation, or a missing figure.
  MiKTeX fetched 20 packages on first use on 2026-10-18, and the font package cm-super was installed on
  2026-10-19 with the author's approval, for the text-companion symbols.
- The paper builds with pdfLaTeX to 54 pages on A4. The body, Sections 1 to 10, fills pages 1 to 15 and the
  top third of page 16, with Tables 4 and 5 a full page each. The references fill pages 16 to 19 and the
  appendix pages 20 to 54. The Study 1 report builds to 13 pages, as before: body to about two thirds of
  page 8, references to the top of page 10, appendix pages 10 to 13.
- Widths: no line or table of the paper runs past the text width by more than 5 pt. Three run past by less,
  as before this pass: Table 5 by 2.5 pt, `tab:s2cells` by 1.3 pt and `tab:s3direction` by 0.8 pt. The
  report is set with `\sloppy`, one layout line after `\begin{document}`, so the seven lines of its frozen
  text that ran 72 to 172 pt past the margin, each an unbroken commit hash, file hash or path, break inside
  it; its log holds no overfull box and 13 loose lines. Its wording is unchanged: the checker's comparison
  with `f325a67` allows that one line beside the dated sentence. The paper sets the two appendix passages
  it shares with the report in `sloppypar`.
- Layout: the longer body moves the floats. Section 5's heading now falls three lines from the foot of page
  7, Figure 3 is set at the top of page 8 after that heading, and Table 2 sits on page 6, three pages after
  its first mention. No float was moved in this pass; the layout is set again in TMLR's style on posting
  day.
- By the revision's method (the expanded paper before `\appendix` with comments, floats and commands
  removed, captions counted apart) the body holds 8,268 words of running text, 1,049 words of captions, five
  tables and four figures. The method counted 7,556 before the revision of 2026-10-20, so splitting the
  sentences, the linking words, the sentences that say what the numbers mean and the formal register added
  712 words, 9.4 percent. The body
  is about 15.3 pages before the references. The aim was about 7,000 words, and the cut is the author's.
- The itemize bullets and the one dollar sign that were set from a bitmap font are set in Type 1 since
  cm-super was installed. Since 2026-10-20 the figures are set in Computer Modern, 8 pt with 7 pt tick
  labels and legends, and embed it as TrueType (Type 42), so neither PDF holds a Type 3 font.

### What could not be verified

- The page count under TMLR's own style file: its template is on this machine since 2026-10-20, untracked
  under `paper/tmlr/`, and the paper has not been set in it.
- Whether the discussion's passages on what each registration expected, what a follow-up study would
  register and the scope of the claim say what the author judges: they were written from the registered
  hypotheses, the dated additions and the reads, and they are his to confirm or rewrite.
- The completion-floor counts (580, 544 and 588 at the first lead; 561, 505 and 572 at every lead; 150, 62
  and 230; 2, 0 and 0), the all-zero tie classification (71 to 87) and the dynamic hurdle's fallback counts
  (58 series at 0.5/29 and 16 at 1.5/29 at the first origin) are computed from the 300 NYC 311 checkpoints,
  which are not in the tree; the checker recomputes them when the checkpoints are present and records a skip
  otherwise.
- The Chronos citation names arXiv 2403.07815 version 3, the version the step-back read of 2026-10-17
  opened; its page was not opened again (no network).
- Study 1's results file, the 540, 209 and 300 checkpoints and the two target-signals files are the release
  assets listed in `reports/release/ASSETS.md`; their URLs enter the tree on posting day, and this pass did
  not open the release (no network). The daily counts of the npm and NYC 311 series are committed, and the
  paper gives their paths.

### Sentences to read

1. The thesis (Section 1): "This paper's answer is that the value is in the size, not the occurrence."
2. The gain (Section 1): "On sparse daily counts the frozen models' gain over a 28-day local mean comes from
   positive days. These are the days where the local mean overpredicts on GitHub stars and npm downloads,
   and on NYC 311 requests the days where it underpredicts, with 12 to 29 percent of that gain on zero
   days."
3. The places (Section 1): "A context estimate beats the model's own zero mass on the typical series in four
   places, each a sparse stratum, a very sparse cell or the month horizon. The first is the sparse npm
   stratum at a week, a secondary reading on one domain. Next come the cells of the grid with zero
   probability 0.95 at a month and one registered test of six on NYC 311's sparse stratum. Under the
   occurrence Brier score alone, dense npm series at a month are the fourth."
4. The exclusion (Section 2): "The protocol excludes Croston and TSB by name without a reason. Neither
   carries a predictive law of its own, and the dynamic count is read here as playing TSB's part."
5. The floor (Section 3): "On a series that is zero nine days in ten the ``model's own zero mass'' is
   therefore set by this rule."
6. The sparse verdict (Section 5): "Thus, on sparse NYC 311 series the score separates the substitution from
   the control, and the npm reading did not replicate."
7. The two readings (Appendix, the Study 3 tables): "Which reading operates depends on the panel and the
   horizon, and nothing beyond that is attributed."
8. The ledger's cause (Section 3): "The three lapses of 2026-10-12 have one cause. No work was done in the
   repository between 2026-09-14 and 2026-10-11, so the October holdout's freeze passed with nothing frozen,
   the npm readiness clock expired untested, and two of Study 2's three domains were deferred."

## The record behind the summary

The NYC 311 run (dated addition 7, commit 3357d77) scored all 300 series in 956 seconds; the family R01 to
R36 has 21 of 36 rejections, none against the predicted direction, with 72 to 88 of the 100 very sparse
series tied exactly in each T1 row. On the npm panel of 209 series, without the three served zero days none
of the eighteen conclusions changes. The post-hoc benchmark of 2026-10-17 placed the TSB hurdle and the fourth
cell on all three panels under a specification fixed before any of its scores existed. The report's source
still expands to its frozen commit apart from its one dated sentence and one layout line, and no entry of
any family table changed.

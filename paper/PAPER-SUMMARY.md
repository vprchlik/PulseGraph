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

### The build and the length

- Both documents were built on 2026-10-18 and rebuilt on 2026-10-19 with MiKTeX 25.12 (pdfTeX 1.40.28),
  each from a clean folder under the ignored `data/cache/build/`: `pdflatex`, `bibtex`, then `pdflatex`
  three times for the paper and twice for the report. Neither log holds an error, an undefined reference or
  citation, or a missing figure. MiKTeX fetched 20 packages on first use: geometry, booktabs, natbib,
  kvsetkeys, kvdefinekeys, pdfescape, ltxcmds, infwarerr, hycolor, refcount, gettitlestring, kvoptions,
  stringenc, intcalc, bitset, bigintcalc, rerunfilecheck and uniquecounter for the report, and placeins and
  xurl for the paper's layout. The font package cm-super was installed on 2026-10-19 with the author's
  approval, for the text-companion symbols.
- The paper builds with pdfLaTeX to 53 pages on A4: the body, Sections 1 to 10, fills pages 1 to 14 and the
  top fifth of page 15, with Tables 4 and 5 a full page each; the references fill pages 15 to 18; the
  appendix fills pages 19 to 53. The Study 1 report builds to 13 pages: body to about two thirds of page 8,
  references to the top of page 10, appendix pages 10 to 13.
- Widths: no line or table of the paper runs past the text width by more than 5 pt. Three run past by less:
  Table 5 by 2.5 pt, `tab:s2cells` by 1.3 pt and `tab:s3direction` by 0.8 pt. The report is set with
  `\sloppy`, one layout line after `\begin{document}`, so the seven lines of its frozen text that ran 72 to
  172 pt past the margin, each an unbroken commit hash, file hash or path, now break inside it; its log holds
  no overfull box and 13 loose lines, nine in those paragraphs and the four in the bibliography it had
  before. Its wording is unchanged: the checker's comparison with `f325a67` allows that one line beside the
  dated sentence. The paper sets the two appendix passages it shares with the report in `sloppypar`.
- By the revision's method (the expanded paper before `\appendix` with comments, floats and commands removed,
  captions counted apart) the body holds 7,545 words of running text, 1,049 words of captions, five tables and
  four figures; the method counts 7,555, the ten more being tokens of the float settings added to the
  preamble. The running text was 7,495 words until the data statement in Section 9 was rewritten on
  2026-10-19 to name the committed daily counts and the release assets (50 words more). The word-count
  estimate was 12.8 pages, or 13.8 with the two full-page tables counted whole; the build gives about 14.2
  pages before the references. The aim was about 7,000 words, and the cut is the author's.
- The itemize bullets and the one dollar sign that were set from a bitmap font are set in Type 1 since
  cm-super was installed; the only Type 3 fonts left in either PDF are those matplotlib embedded in the
  figures.

### What could not be verified

- The page count under TMLR's own style file: no TMLR template is under `paper/`, so it is unknown until
  the paper is set in it.
- The completion-floor counts (580, 544 and 588 at the first lead; 561, 505 and 572 at every lead; 150, 62
  and 230; 2, 0 and 0), the all-zero tie classification (71 to 87) and the dynamic hurdle's fallback counts
  (58 series at 0.5/29 and 16 at 1.5/29 at the first origin) are computed from the 300 NYC 311 checkpoints,
  which are not in the tree; the checker recomputes them when the checkpoints are present and records a skip
  otherwise.
- The Chronos citation now names arXiv 2403.07815 version 3, the version the step-back read of 2026-10-17
  opened; its page was not opened again for this revision (no network).
- Study 1's results file, the 540, 209 and 300 checkpoints and the two target-signals files are not released
  yet; the paper names them as the release assets listed in `reports/release/ASSETS.md`. The daily counts of
  the npm and NYC 311 series are committed, and the paper gives their paths.

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
still expands to its frozen commit apart from its one dated sentence and one layout line, and no entry of
any family table changed.

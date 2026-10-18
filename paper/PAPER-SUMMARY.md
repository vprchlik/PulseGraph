# The paper: title, abstract and a one-page summary

Written 2026-10-16 for the author's read before the paper is posted, rewritten after each read, and
rewritten on 2026-10-17 when the paper was reorganized by question at a body of about twelve pages with the
two reads of that day and the post-hoc intermittent-demand benchmark applied. The paper (`paper/paper.tex`)
reports three registered, population-sampled studies as one design run in three steps; the Study 1 report
(`paper/main.tex`) still builds on its own and is unchanged. Every number below comes from a named file;
`paper/sources.md` gives the row and column and the command that regenerates the file, and
`paper/check_numbers.py` asserts each one in the paper and in this page, the abstract below included.
Differences are variant minus reference, so a negative number favors the variant. The sentences the author
should read are listed at the end.

## Title

Size, not occurrence: what zero-shot foundation models add on sparse daily counts

## Abstract

We ask where zero-shot time-series foundation models add value on sparse daily counts. Three registered,
population-sampled studies run one design in three steps on frozen Chronos-2, TimesFM 3 and TimesFM 2.5. On
daily GitHub star counts of 300 repositories sampled from 148,550, the models beat a 28-day local mean on the
mean in every cell and lose to it on the typical repository, lower on 46 to 89 of 300. Study 2 replaces each
model's zero mass with a 28-day context-only occurrence probability, keeping its completed positive law, on
209 hash-sampled npm download series and a 540-series synthetic grid. No pooled test favors the substitution
at q = 0.05, two of six npm tests and all three grid tests reject against it, and the model's positive law
beats a shifted-Poisson count hurdle in all six npm cells; in the secondary strata the substitution scores
lower for 81, 60 and 66 of the 100 sparse series at horizon 7 and for 32 to 43 of the 100 dense ones. Study 3
registers that reading as a per-stratum family of 36 tests on NYC 311 service requests, 300 series in three
strata, with a dynamic occurrence: on dense series all six tests reject as predicted; on sparse series one of
twelve tests rejects as predicted, and ten of twelve medians are exactly zero. On most very sparse series
every decile of both forecasts is zero and the completion rule fixes the models' occurrence probability
between 0.0607 and 0.1, so nothing about occurrence can be read there. The models' value is in the size of
positive days; their own probability of a zero day is at least as good as a context estimate wherever nine
quantiles can express one, except for the typical sparse npm series at a week.

## One page for the author

### The thesis

The frozen models' value on sparse daily counts is in the size of the positive days. Their own probability of
a zero day is at least as good as a context-only estimate wherever their nine quantiles can express one: on
dense series in all three settings, and on sparse NYC 311 series, where the two are about level. The one
place where a context estimate beats the model's own zero mass on the typical series is the sparse npm
stratum at a week, a secondary reading on one domain and one horizon; the TSB hurdle wins the same series. On
series that are zero nine days in ten the completion rule, not the model, sets the occurrence probability
(between 0.0607 and 0.1), the quantile score ties, and nothing about occurrence can be read from the models.

### What the paper says, in six sentences

1. Against a 28-day local mean the frozen models' gain is on positive days, where the local mean
   overpredicts: on the mean in every cell of every panel, and on the typical series on npm and NYC 311 but
   not on GitHub, where the typical repository prefers the local mean (lower on only 46 to 89 of 300) while
   the mean favors the models in every cell, carried by few repositories.
2. Replacing a model's own zero mass with a context-only occurrence estimate makes the forecast worse on
   dense series in all three settings under the registered quantile score, and under the occurrence Brier
   score on NYC 311 and at a week on npm; on NYC 311 this is confirmatory (all six dense tests reject as
   predicted, 21 of 36 tests reject in all, none against the prediction), and on npm and the grid the pooled
   families speak for it (No pooled test favors the substitution at q = 0.05; two of six npm tests and all
   three grid tests reject against it; twelve of the eighteen npm tests reject in all).
3. On sparse series the answer depends on the domain: the typical sparse npm series favors the substitution
   at a week under all three scores (lower for 81, 60 and 66 of the 100 sparse series at horizon 7 and for
   32 to 43 of the 100 dense ones; the TSB hurdle wins 77, 61 and 74) and not at a month, while on NYC 311's
   sparse stratum one of twelve tests favors it and ten of twelve medians are exactly zero.
4. On very sparse series the registered construction cannot ask the occurrence question: 72 to 88 of the 100
   NYC 311 series tie exactly, 580, 544 and 588 of the 600 completed forecasts sit on the completion floor,
   and the Brier score's separation (the dynamic occurrence lower on 68 to 82 of 100) compares a context
   estimate near 0.017 with a constant near 0.061 that the completion formula predicts.
5. The model's positive law beats a shifted-Poisson count law wherever that law is misspecified (all six
   npm cells; the fourth cell far worse than the control on dense series on every panel) and loses to it
   where it is the generator's own (the grid); against an empirical law it keeps its value on dense series
   only, and the dynamic hurdle beats the empirical hurdle in 14 of 18 registered tests on NYC 311, three
   with a median of exactly zero.
6. The registered dynamic count, a discounted analogue of TSB with no foundation model, is the best
   forecaster on the grid after the oracle and loses to the models on every natural panel; the post-hoc
   dynamic-occurrence wrapper removes four of the five rejections against the substitution and never beats
   the model's own zero mass at q = 0.05.

### What changed in the claims against `6220211`, in five sentences

1. The paper is one argument organized by question (what the models add; the occurrence substitution by
   regime; the positive law against count laws) at a body of about twelve pages, with the three studies as
   one design in three steps, the full families and the process in the appendix, and a new title that names
   what was found.
2. The very sparse result is no longer two readings given equal weight: it is an interface limit, the
   completion floor stated with its formula and its three counts (post hoc), so the ties and the Brier
   separation compare a context estimate with the completion rule, not with the models.
3. The dense half is confirmatory on NYC 311 only; on npm and the grid the families are pooled and the dense
   reading rests on the declared secondary strata; the accounting sentence is true for all three models (the
   TimesFM models' positive-day underprediction part adds more than the zero-day part at a week); the
   direction rule is the median's, a zero median has no sign, and the fourteen T2 rejections are stated with
   the three zero-median rows named.
4. The intermittent-demand literature and the field's names for the baselines are in (Croston, SBA, TSB,
   ADIDA, iETS, Snyder, Ord and Beaumont, Kolassa, the M5 uncertainty track, the count scores), and the
   post-hoc TSB hurdle and the fourth cell on npm and the grid are in the body, labeled post hoc; the two
   readings of the accounting trade are attributed where the record supports each (the first on dense NYC
   311 and at a week on the grid, the second at a month on npm and the grid).
5. The occurrence Brier score and the discrete CRPS stand beside QScore9 in the body's occurrence table for
   every contrast, labeled as declared secondaries; the ledger is one table with a decided-before-or-after
   column, item 6 flagged as the one change decided after scores; and the writing patterns the step-back
   read named (run logistics, hashes in prose, the scope repeated, review items as motivation, code
   identifiers as names) are gone from the body.

### What it does not show

- Nothing about Wikipedia pageviews, Study 2's deferred tests E19 to E54, the October holdout or the
  November round, all registered and not run; contamination stays unresolved for all three models.
- Whether a sparse-regime benefit exists beyond npm at a week: on NYC 311's sparse stratum the record is one
  rejection of twelve, and on very sparse series the registered construction cannot ask the question.
- Which reading of the accounting trade operates in general: the record supports the first on dense NYC 311
  series and at a week on the grid, the second at a month on npm and the grid, and nothing beyond that.
- Anything about models with another output interface (a mixture, sample paths, Chronos-2's own 21 levels);
  the next study's design is named in the discussion in one sentence, and the deferred npm replication at a
  week is the piece a reviewer could ask for.
- The npm means are statements about one series (7.6 million downloads a day); the very sparse NYC 311
  means ride on one series; the paper says so where it prints them.

### What could not be verified

- No TeX compiler or pandoc is on this machine, so there is no PDF and no page count; the static checks (every
  input present, braces and environments balanced, every label referenced, every citation in the
  bibliography, every tabular row with its column count, every figure file present) passed, and the widths
  below are estimates from the Computer Modern metrics.
- By the revision's method (the expanded paper before `\appendix` with comments, floats and commands removed,
  captions counted apart) the body holds 7,499 words of running text, 1,016 words of captions, five tables and
  four figures; at 900 words a page and half a page a float that is about 12.8 pages, and about 13.5 if the
  two full-page tables are counted as a page each. The appendix holds 13,987 words, 2,536 words of captions,
  37 tables and five figures. The aim was about 7,000 words; the last 500 are the author's cut.
- The completion-floor counts (580, 544 and 588; 150, 62 and 230; 2, 0 and 0) and the all-zero tie
  classification (71 to 87) are computed from the 300 NYC 311 checkpoints, which are not in the tree; the
  checker recomputes them when the checkpoints are present and records a skip otherwise.
- The 300, 540, 209 and 300 checkpoints and the daily counts of the npm and NYC 311 series are not released
  yet; the paper says they are to be released as release assets.

### Sentences to read

1. The thesis (Section 1): "This paper's answer is that the value is in the size, not the occurrence."
2. The exception (Section 1): "The one place where a context estimate beats the model's own zero mass on the
   typical series is the sparse npm stratum at a week, a secondary reading on one domain and one horizon."
3. The floor (Section 3): "On a series that is zero nine days in ten the ``model's own zero mass'' is
   therefore set by this rule."
4. The interface limit (Section 5): "So on series that are zero nine days in ten the registered construction
   cannot ask the occurrence question: the quantile score ties, and the Brier score's separation is the
   dynamic hurdle's estimate against a constant near 0.061, which the formula predicts."
5. The sparse verdict (Section 5): "So on sparse NYC 311 series the score sees the substitution, and the npm
   reading did not carry over."
6. The two readings (Section 7): "Which reading operates depends on the panel and the horizon, and nothing
   beyond that is attributed."
7. What would be done differently (Section 7): "The next study of this question registers the occurrence log
   or Brier score and the discrete ranked probability score as its primaries, keeps a model output that can
   express an occurrence probability below one in ten, such as Chronos-2's own 21 quantile levels, a mixture
   or sample paths, registers TSB and iETS beside the count baselines, chooses the regime threshold from a
   per-series curve, and runs on a prospective window; that is one study, and the one a reader of the
   intermittent-demand literature would ask for."
8. The ledger's cause (Section 3): "The three lapses of 2026-10-12 have one cause, that no work was done in
   the repository between 2026-09-14 and 2026-10-11."

## The record behind the summary

The NYC 311 run (dated addition 7, commit 3357d77) scored all 300 series in 956 seconds; the family R01 to
R36 has 21 of 36 rejections, none against the predicted direction, with 72 to 88 of the 100 very sparse
series tied exactly in each T1 row. On the npm panel of 209 series, without the three served zero days none
of the eighteen conclusions changes. The post-hoc benchmark of 2026-10-17 placed the TSB hurdle and the fourth cell on
all three panels under a specification fixed before any of its scores existed. The report's source still
expands to its frozen commit apart from its one dated sentence, and no entry of any family table changed.

# The paper: title, abstract and a one-page summary

Written 2026-10-16 for the author's read before the paper is posted. The paper (`paper/paper.tex`) is the
Study 1 report (`paper/main.tex`, which still builds on its own) extended with Study 2's two results. Every
number below comes from a named file; `paper/sources.md` gives the row and column and the command that
regenerates the file, and `paper/check_numbers.py` asserts each one in the paper and in this page.
Differences are model minus reference, so a negative number favors the model. The three sentences the
author should read are listed at the end.

## Title

Zero-shot foundation models on sparse daily counts: a registered re-evaluation on GitHub stars and a
registered occurrence test on npm downloads

Alternative, the report's own title, if the paper is to be read as the report's second version: Zero-shot
foundation models on sparse daily GitHub star counts: a registered re-evaluation after an audit

## Abstract

We ask whether zero-shot time-series foundation models improve probabilistic forecasts of sparse daily
counts, and test one mechanism behind the answer. Study 1 is a registered re-evaluation on daily GitHub star
counts after an audit of a first version (protocol commit 5f01769, 2026-09-12): 300 repositories sampled
from a frame of 148,550, three frozen models (Chronos-2, TimesFM 3, TimesFM 2.5) against a 28-day local
mean and weekly AutoETS, a nine-decile quantile score, 18 declared comparisons. Against the local mean the
mean difference favors the models in every cell and its bootstrap interval excludes zero in five of nine,
but the typical repository favors the reference: the models score lower on 46 to 89 of 300 repositories and
the signed-rank test rejects in all nine cells on the reference's side. Against AutoETS both summaries favor
the models, consistent with its 80 percent intervals covering about 99 percent of target days. Study 2,
registered after those results (commit df55867, 2026-09-14), asks whether replacing a frozen model's own
zero mass with a context-only occurrence probability, keeping its completed positive law, lowers the score,
and whether that positive law beats a fixed count hurdle. On a hash-sampled npm download panel of 209 series
(100 dense, 100 sparse and 9 very sparse, the last short) no comparison favors the substitution and two of
six reject against it; the model's positive law beats the count hurdle in all six cells. On a registered
540-series synthetic grid five of six tests reject, all against the substitution. One series at 7.6 million
downloads a day carries every npm mean, so the medians and rank tests describe the typical series; a
post-hoc sensitivity to three zero days served by the source changes no mechanism conclusion. A literature
re-check allows the claim of this registered combination on daily attention and adoption counts, and
nothing broader.

## One page for the author

### What the paper says, in six sentences

1. Study 1 stands as the report gave it: on a population-sampled GitHub panel the three frozen models beat
   the 28-day local mean on the mean in every cell and lose to it on most individual repositories, and they
   beat weekly AutoETS on both summaries because its intervals are far too wide.
2. Study 2 tested the reading that the models' size forecasts carry the gain and their occurrence forecasts
   carry the loss, by replacing each model's own zero mass with a 28-day context-only occurrence probability
   while keeping the model's completed positive law, on data declared for the purpose.
3. The substitution does not help: on the npm panel of 209 series no comparison favors it and two of six
   reject against it (TimesFM 3 and TimesFM 2.5 at horizon 30), and on the 540-series synthetic grid all
   three tests reject against it; in all nine cells it lowers the zero-day loss and raises the positive-day
   underprediction loss by more.
4. The model's positive law is the part that does help on npm: against a fixed count hurdle with the same
   occurrence rule it wins in all six cells (lower on 115 to 161 of 209 series), while on the grid, whose
   generator draws positive sizes from the count hurdle's own family, it loses for two models and ties for
   the third.
5. The raw deciles beat the local mean on npm on the mean in all six cells and on the rank test in four of
   six, where in Study 1 the rank test favored the reference in all nine cells; the paper reports the
   difference between the two panels and does not attribute it.
6. Every npm mean is carried by one series, `aggregate-error`, at 7.6 million downloads a day, so the
   medians, counts and rank tests describe the typical series; three zero days served by the source are
   scored as served under dated addition 6, and the post-hoc sensitivity without them changes no mechanism
   conclusion.

### What was found

The synthetic grid ran on 2026-10-15 at `3fc3411` (540 series, 1,317 seconds, 55,080 forecasts, no failure;
every score recomputed with a largest difference of 0.0). The family S01 to S06: each hurdle variant scores
0.086 to 0.088 above its completed control, every interval above zero, lower on 5 or 6 of 30 blocks, all
three rejecting; the Chronos-2 and TimesFM 2.5 hurdles score 0.052 and 0.061 above the count hurdle and
reject; the TimesFM 3 hurdle differs by 0.022 and does not. Five of six reject, all against the hurdle. The
oracle, a diagnostic, has the lowest mean score at both horizons and the lowest cell mean in 17 of 18 cells.

The npm run followed the same day at `3057b16` (209 series, 692 seconds, 20,064 forecasts, no failure; the
integrity recomputation found 0 disagreements). The family E01 to E18: twelve of the eighteen reject, ten
for the model variant and two against the hurdle. Hurdle against its control: means +90 to +254 with every
interval above zero (the dominant series), medians within 0.014 of zero, the hurdle lower on 81 to 121 of
209, rejections against it in E10 and E16. Hurdle against the count hurdle: all six reject for the model's
positive law, medians -0.0063 to -0.072, the Brier difference exactly zero because both sides share the
occurrence rule. Raw deciles against the local mean: four of six reject for the model (E06, E09, E12, E18);
Chronos-2 and TimesFM 2.5 at horizon 7 do not. The context-scaled score, the registered scale-free
secondary, favors the hurdle over its control at horizon 7 for all three models and includes zero at
horizon 30.

The three zero days: the download API served 0 for all 209 series on 2026-07-12 and 2026-08-14, and 0 for
`aggregate-error` on 2026-06-25, between days of millions; npm's own records say nothing about them, and its
forum records two earlier whole-day zeros that were later restored. The registered analysis of the data as
served stands (dated addition 6). Without all three days none of the eighteen conclusions changes; without
the two panel-wide days E06 alone stops rejecting (adjusted p 0.060 against 0.012).

### What it changes

The report said the models win on the mean and lose on the typical repository, with the zero-day part
against them. The paper adds that the loss on zero days cannot be taken out by a context-only occurrence
estimate without paying more on positive days, on either panel, and that the models' size forecast is what
beats a fixed count hurdle on npm. The claim is the registered combination on daily attention and adoption
counts and nothing broader: not the first evaluation of frozen models on sparse counts, not the first hurdle
on a frozen model's output, not the first to show aggregate and per-series rankings disagreeing.

### What it does not show

- Nothing about NYC 311 or Wikipedia, which are registered and not run, nor about the October holdout,
  whose freeze lapsed, nor about Study 1's follow-up cohort, nor about unseen entities: contamination stays
  unresolved for all three models, and the npm targets are mixed by model availability.
- Nothing about why the positive-law contrast reverses between npm and the grid, beyond what the
  accounting shows; the paper reports the reversal and does not explain it.
- Nothing about human adoption: an npm download is a tarball request, mirrors and automated clients
  included, which is also why only 9 of 9,998 complete candidates were sparse enough for the third stratum.
- The npm means are statements about one series; the paper says so wherever it prints a mean.

### What could not be verified

- No TeX compiler or pandoc is on this machine, so there is no PDF and no page count. By word count the
  paper's body holds about 12,000 words with ten tables and four figures, beside the report's 4,200 words
  with four tables and two figures; at the report's density that is about twenty pages before the
  appendix, against the aim of twelve to fourteen. The design detail, the panel's budget and data
  statement and the secondary readings are already in the appendix. The next cuts, if the author wants
  them, are the Study 2 design section (2,300 words, of which the frame-and-sampling, completion and
  baselines paragraphs could follow the rest into the appendix), the run and zero-day paragraphs of the
  results (about 700 words that could point to the appendix) and the limitation items; each cut removes
  something the paper now states in the body, so it is the author's choice.
- Whether the three zero days are gaps in npm's counts: no npm record names them; the reading rests on
  npm's earlier episodes and one third-party page.
- The 699 and 1,323 seconds for the whole processes are quoted from the two results documents; the run
  files record the 692 and 1,317 seconds inside the runs.
- The release assets (results.parquet, the 540 synthetic checkpoints, the 209 npm checkpoints) do not exist
  yet; the paper says they are to be published.
- The titles and author lists of ten cited arXiv items were read from their abstract pages on 2026-10-16;
  the ICTMOD paper and ZODIAC still carry surnames only, as the record holds them.

### Three sentences to read

1. The zero-day note (Section 10, "Three zero days in the npm targets"): "The registered completeness rule,
   fixed before any target was seen, verifies that every day is present once with a nonnegative integer
   and does not test for a source-wide zero, so the three days entered the run as explicit zeros and were
   scored as served."
2. The dominant-series sentence (Section 10, "The one series behind every npm mean"): "The mean paired
   difference over 209 equally weighted series is, as registered, that series' difference divided by 209
   plus a remainder of a different order, and the reader should take every mean in the external table as a
   statement about that series."
3. The mechanism conclusion (Section 11, "What the two studies say together"): "A context-only occurrence
   estimate does not improve a frozen model's own completed zero mass under this score, on either the npm
   panel or the grid."

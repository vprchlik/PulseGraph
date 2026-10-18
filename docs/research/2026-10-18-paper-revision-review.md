# Review of the reorganized paper

Written 2026-10-18 03:00 UTC. A read-only review of the paper under `paper/` as committed in `711e2ff` (HEAD
`342b3c7`), by a reader other than its writer, before the author reads the title, the abstract and
`paper/PAPER-SUMMARY.md`. The paper was rebuilt on 2026-10-17 from the chronicle of three studies into one
argument in nine sections, titled *Size, not occurrence: what zero-shot foundation models add on sparse daily
counts*, with the families, the detail and the post-hoc analyses in the appendix. It is read against the
record: `paper/paper.tex` with its inputs, `paper/main.tex` and `paper/shared/`, `paper/sources.md`,
`paper/check_numbers.py`, `paper/references.bib`, `paper/figures/make_figures.py`, `PAPER-SUMMARY.md`; the
paper at `6220211` and the report at `f325a67` for comparison; `PROTOCOL.md` with its dated additions;
`RESULTS.md`; the three runs under `reports/` with their `inference/` and `integrity/` directories; the
post-hoc benchmark under `reports/study2-posthoc-intermittent-baselines/` with its `SPEC.md`; the two reads
of 2026-10-17 (`docs/research/2026-10-17-paper-study3-review.md` and
`docs/research/2026-10-17-paper-shape-review.md`); `CONTRIBUTING.md`; `README.md`. Nothing under `paper/`
was changed; the fixes below are instructions for the revision.

Each verdict is `holds`, `holds with this fix` or `does not hold`; `does not hold` is used only where a saved
file contradicts the text. Body tables and figures are numbered as the expanded source orders them: Table 1
the panels (`tab:panels`), 2 the ledger (`tab:ledger`), 3 the raw deciles against the local mean
(`tab:raw`), 4 the occurrence substitution (`tab:occ`), 5 the positive-law contrasts (`tab:pos`); Figure 1
the design, 2 the completion floor, 3 the mean and the typical series, 4 the signature figure. File and line
references are to `paper/sections/` unless another file is named. Every CSV was read with
`float_precision="round_trip"`. Every count below that is not printed in the paper comes from saved files by
the command at the end; it is this review's reading, post hoc, and adds no test.

## In one page

**Verdict.** The paper may go to the author's read after the fixes listed under "The fixes that change a
claim", not as it stands. The record holds: the report still expands to `f325a67` apart from its one dated
passage, no entry of any registered table changed, the checker passes 1,357 checks with none skipped, and
every entry of the five body tables, every plotted value of the four body figures and every registered test's
direction, ties and rank sums reproduce from the saved files by this review's own computation. What does not
hold is in the sentences that state the argument: the thesis paragraph names one exception where the record
has more, its first clause is contradicted on NYC 311, and five sentences of the discussion, Section 4,
Section 5 and the related work say more than their tables. One LaTeX error would print raw text, and Table 4
is wider than the text.

**Counts.** 76 verdicts: 40 hold, 25 hold with a fix, 11 do not hold. No table entry is wrong. Of the eleven
that do not hold, nine are sentences (2.14, 2.15, 4.1 to 4.4, 5.3, 6.5, 8.10), one is Table 4's width (9.2)
and one is a broken reference (10.1); none changes a number in a table.

**The fixes that change a claim, first.**

1. *The thesis's first clause* (01-introduction.tex:15-17, the discussion 07-discussion.tex:10-11,
   PAPER-SUMMARY sentence 1). The gain over the 28-day local mean sits on positive days where the local mean
   overpredicts on GitHub and npm, but on NYC 311 the registered secondary accounting puts it on positive
   days where the local mean *under*predicts (-0.034 to -0.061 of the -0.074 to -0.081 total) and on zero
   days (-0.010 to -0.022), with the overprediction part the smallest (verdict 4.1).
2. *"The one place"* (01-introduction.tex:20-21, the abstract's last sentence, PAPER-SUMMARY's thesis). The
   record has two more places where a context estimate beats the model's own zero mass on the typical
   series: R21, a registered rejection for the dynamic occurrence on NYC 311's sparse stratum at a week, and
   the grid's cells with z = 0.95 at a month, where the fixed hurdle is lower than its control in 21 to 26 of
   30 blocks under every score. On dense npm series at a month the Jeffreys estimate is also the better
   occurrence forecast under the occurrence Brier score (57 to 62 of 100) (verdicts 4.2, 4.3).
3. *The interface limit on the grid* (05-occurrence.tex:80-81). "The same holds ... for the grid's cells with
   z = 0.95" is contradicted at a month: the quantile score ties on 232 of 540 series pairs there and favors
   the substitution on 217 of the other 308 (verdict 4.4).
4. *The NYC 311 sparse stratum* (07-discussion.tex:19-20, PAPER-SUMMARY.md lines 63 and 108). "One of twelve
   registered tests ... ten of twelve medians" counts the T1 tests of the sparse and very sparse strata
   together; the sparse stratum has six T1 tests, one rejecting and four with a median of exactly zero
   (verdict 2.14).
5. *The second reading at a month on npm* (07-discussion.tex:35-36). The Jeffreys estimate is as good on the
   Brier score, not under the count law: there the model's zero mass is lower on 43, 48 and 60 of the 100
   dense series, with every mean below zero (verdict 5.3).
6. *The context-scaled score* (04-models-add.tex:83). It does not "agree with the medians where the unscaled
   mean differs": in E03 and E15 it still favors the model, with an interval that includes zero, where the
   medians favor the reference (verdict 2.15).
7. *Why Croston and TSB were excluded* (02-related-work.tex:20-22). The protocol excludes them by name and
   gives no reason (`PROTOCOL.md` line 152); the reason the paper gives was written after the runs (verdict
   6.5).
8. *The summary's first and third sentences* repeat 1 and 4 and add that the typical series favors the models
   on npm and NYC 311, which three NYC 311 medians and two npm medians contradict (verdict 8.10).
9. *The LaTeX error.* 05-occurrence.tex:55-56 reads `(Table~` and then a line `ef{tab:occ}).`: the `\r` of
   `\ref` became a line break, so the PDF would print "ef" and the label (verdict 10.1).

**Length and widths.** By the stated method the body holds 7,499 words of running text (7,358 by this
review's stricter tokenizer, which counts only tokens with a letter or digit) and 1,016 words of captions,
with five tables and four figures: 12.8 pages at 900 words a page and half a page a float, 13.8 with the two
full-page tables counted as a page each (`PAPER-SUMMARY.md` says 13.5; its own figures give 13.8). Either is
above TMLR's twelve-page line for the standard review period. By the Computer Modern metrics Table 4 does
not fit the text width: about 490 to 533 pt against 461, because each of its three "Lower / tied / higher"
headers is about 31 pt wider than any count under it; Table 5 is at the limit (about 460 to 479 pt); Tables 1
to 3 fit (448 to 459 pt); the two sideways appendix tables fit the landscape width (657 to 683 and 664 to 666
pt against 708). Five appendix tables would also run over (verdict 9.6).

## 1. Nothing registered changed

**1.1. The report's text.** `holds`. `paper/main.tex` with its fourteen `\input{shared/...}` lines replaced by
the files' contents (none nested) is 704 lines against 703 for `git show f325a67:paper/main.tex`, which has no
`\input`, and the two differ in one hunk only, in the Study 2 paragraph of "What is registered and not run"
(`main.tex` lines 82-84): the sentence "As of 2026-10-12, a statement to be re-checked on the posting day, no
Study 2 target value, forecast or score exists; nothing is claimed about its outcome." became "As of
2026-10-12 no Study 2 target value, forecast or score existed; both components fixed for the October 2026
paper, the synthetic grid and the npm external run, ran on 2026-10-15 and are reported in the paper that
extends this report. Nothing is claimed here about their outcome." The passage dates from `5720c05`;
`main.tex` and `paper/shared/` are unchanged since `6220211`. No whitespace-only difference. Fix: none.

**1.2. The family tables.** `holds`. Every header and data row of `tab:s2ext` (E01 to E18), `tab:s2syn` (S01
to S06), `tab:s3family` (R01 to R36), `tab:s2family`, `tab:s2synfamily` and `tab:s3structure`, compared cell
by cell with the paper at `6220211`, is unchanged: 0 cells of 93 rows. The changes are of the float only:
placement `[t]` to `[h]`, `tab:s3family` from `table` to `sidewaystable` with its size and column
specification unchanged, and one caption reference in `tab:s2ext` from "Section" to "Appendix". Fix: none.

**1.3. Study 1's tables.** `holds`. `tab:panel`, `tab:lm`, `tab:ae` and `tab:posthoc` now sit in
`app-study1.tex` and differ from the copies in `shared/s1-panel.tex`, `s1-results.tex` and `s1-posthoc.tex`,
which `main.tex` still reads, in placement only. `paper/shared/` is byte-identical to `6220211` (the same tree
`70fe73d`), so `tab:autoets`, `tab:stratum`, `tab:calibration`, `tab:scale` and `tab:v1` are unchanged. Fix:
none.

## 2. Numbers

**2.1. The checker.** `holds`. `.\.venv\Scripts\python.exe paper\check_numbers.py` prints "1357 checks, 0
failures, 0 skipped" and "body: 7499 words of running text, 1016 words of captions, 5 tables, 4 figures". The
300 NYC 311 checkpoints are on this machine, so the floor counts and the tie classes were recomputed, not
skipped. Fix: none.

**2.2. The abstract.** `holds`. Every number traced: 300 of 148,550 and 46 to 89 of 300 (Study 1's
`inference.csv`); 209 series, 540 series; two of six npm tests against the substitution (E10, E16) and all
three grid tests (S01, S03, S05); the positive law ahead of the count hurdle in all six npm cells (E02, E05,
E08, E11, E14, E17); 81, 60 and 66 sparse and 32 to 43 dense series (the npm per-series scores by stratum);
36 tests, 300 series; all six dense T1 tests rejecting as predicted; one of twelve and ten of twelve (the T1
tests of the sparse and very sparse strata; see 2.14 for the wording); 0.0607 and 0.1 (the formula, 2.9).
Fix: none here (the sentences are taken up in 2.14 and 4.2).

**2.3. Table 1.** `holds`. The frame and series counts match the status files the design figure reads
(148,550 and 300 for GitHub; 4,486,927 names, 10,000 eligible, 209 series of 100, 100 and 9 for npm; 8,469
cells and 300 series for NYC 311; 18 cells of 30 replicates, 540 series of 270 days, origins 180, 210 and 240
for the grid) and the appendix text (470 skipped, 9,998 complete). Fix: none.

**2.4. Table 2.** `holds`. The dates and commits match `git log -- PROTOCOL.md` (`5f01769` 2026-09-12,
`df55867` 2026-09-14, `8db0d73` 2026-10-12, `5be2ce9` 2026-10-15, `1c09ac8` and `3357d77` 2026-10-16); item
4 is absent from `PROTOCOL.md`, whose additions jump from 3 to 5. The "Decided" column is right against the
commit times: item 5 was committed at 06:56 UTC on 2026-10-15, before the grid run (20:16 UTC) and the npm
target pull (23:15 UTC); item 7 at 07:38 UTC on 2026-10-16, before the NYC 311 target pull (03:16 UTC on
2026-10-17); item 6 at 04:03 UTC on 2026-10-16, after the npm scores. Fix: none.

**2.5. Table 3.** `holds`. All 21 rows recomputed: the GitHub rows from
`reports/registered-2026-09-13/inference/paired_repositories.csv` (means to three decimals, medians to four,
the repositories lower, the reference's side by rank sum in all nine); the npm rows from the run's per-series
scores (means, medians, lower / tied / higher, the model's side by rank sum in all six, the four rejections);
the NYC 311 rows from the per-series scores, with the within-table Benjamini-Hochberg $p$ recomputed from the
eighteen raw $p$ of `secondary_pooled_study2_form.csv` and equal to the file's. Fix: none.

**2.6. Table 4.** `holds`. All 66 rows recomputed under the three scores from the runs' `series_scores.csv`
(npm and NYC 311 within the manifests' strata; the grid as replicate blocks with the 18 cells weighted
equally), and the 30 TSB rows from the benchmark's window scores averaged over origins by this review, not
from its contrast tables: every count and median matches, including the 99 dense npm series under the CRPS.
Fix: none.

**2.7. Table 5.** `holds`. All 72 rows recomputed as ranges over the three models, from the per-series scores
of the three runs and the benchmark's window scores (the fourth cell and the TSB hurdle on npm and the grid);
every range, median range and status matches, including the NYC 311 "dynamic count vs control" rows on very
sparse series (3 to 7 / 84 to 88 / 9 to 10), which look like the T1 rows and are the dynamic count's own.
Fix: none.

**2.8. The four body figures.** `holds`. `make_figures.py`, copied with its output redirected to a scratch
folder, regenerates all ten figures pixel for pixel identical to the committed PNG files. Figure 1's numbers
are the status files' (2.3). Figure 2 is the formula alone (2.9) with the Jeffreys estimates 0.5/29, 1.5/29
and 2.5/29. Figure 3's GitHub curves end at the registered means (-0.1320, -0.2012, -0.2007 at horizon 30),
and the npm and NYC 311 curves recomputed from the per-series scores end at -4,733.65, -5,001.11, -5,109.14
and -0.07444, -0.08027, -0.07430. Figure 4's binned shares, recomputed with the script's declared bins (0,
0.1, 0.3, 0.5, 0.7, 0.9, 0.97 and 1) over the manifests' zero fractions, give the caption's 68 of 105 and 139
of 195 (npm), 40 of 84 and 108 of 216 with 6 and 38 tied, and 183 of 186 tied with 148 lower under the Brier
score (NYC 311), all at horizon 7. Fix: none.

**2.9. The completion floor.** `holds`. In `pulsegraph/study2/distributions.py`, `CountLaw.sf` for a
completed law evaluates the survival at $k = 0$ at $x = 0.5$; when every knot is below 0.5 the search index
passes the ninth knot and the survival is the tail, $0.1\exp(-\max(0, 0.5 - q_{0.9})/s)$, and `complete` sets
$s = \max(1, q_{0.9} - q_{0.8}) = 1$ there. Every one of the 2,156 first-lead floor laws in the three strata
carries `tail_scale` 1.0. From the 300 checkpoints: 580, 544 and 588 of 600 very sparse, 150, 62
and 230 sparse and 2, 0 and 0 dense completed forecasts on the floor; medians 0.0607, 0.0607 and 0.0609
against 0.0172; and 87, 81, 87, 82, 71 and 85 of the tied very sparse series with every decile zero under
both forecasts in every window (71 to 87). Fix: none.

**2.10. What "on the floor" counts.** `holds with this fix`. The counts are of each forecast's first lead,
as `paper/sources.md` says and the paper does not. With every lead required they are 561, 505 and 572 of 600;
by lead day, 95, 87 and 96 percent. Fix: at 03-design.tex:53-55 write "whose first lead sits on the floor"
or give the lead-day shares.

**2.11. Figure 3's caption.** `holds with this fix`. "drifts upward over the majority, which lose by small
amounts" (04-models-add.tex:67-68) is true of GitHub, where each curve reaches its final level within 3
percent of the repositories and its minimum at 16 to 25 percent. On npm at horizon 30 the models are lower on
112, 125 and 113 of the 209 series, so the majority gain; the curve keeps falling to 54 to 60 percent of the
series, and on the symmetric log scale it is flat after its first point, `aggregate-error` alone (-4,699,
-4,966 and -5,077 against final means of -4,734, -5,001 and -5,109). Fix: "on npm the first series sets the
level and the other 208 move it by less than one percent."

**2.12. The page arithmetic.** `holds with this fix`. `PAPER-SUMMARY.md` line 126: 7,499 / 900 + 9 × 0.5 =
12.8, and with the two full-page tables at a page each 7,499 / 900 + 7 × 0.5 + 2 = 13.8, not 13.5. Fix: "about
13.8".

**2.13. The discussion's numbers.** `holds`. 62 to 73 of 100 (the fourth cell against the count hurdle,
dense NYC 311), 57 to 66 of 100 and 24 or 25 of 30 (the fixed hurdle against its control at a month), 0.2944
to 0.325, 14 of 18 with three zero medians, 18 to 24 of 30 blocks and 1.721 against 1.754 to 1.792, all
reproduce. Fix: none.

**2.14. The NYC 311 sparse stratum.** `does not hold`. 07-discussion.tex:19-20 says "on NYC 311's sparse
stratum one of twelve registered tests favors it and ten of twelve medians are exactly zero". The sparse
stratum's six T1 tests (R13, R15, R17, R19, R21, R23) have one rejection for the substitution (R21) and four
medians of exactly zero; its twelve tests have six rejections (R21 and five T2) and five zero medians. "One
of twelve" and "ten of twelve" are the T1 tests of the sparse and very sparse strata together. The same
sentence is `PAPER-SUMMARY.md` line 63 and the "one rejection of twelve" of line 108; the abstract's "on
sparse series one of twelve tests ... ten of twelve medians" is right only in H3's grouping (zero fraction at
least 0.5), which its next sentence's "very sparse series" undoes. Fix: "on NYC 311's sparse stratum one of
six T1 tests favors it and four of six medians are exactly zero"; in the abstract, "on the sparse and very
sparse strata one of twelve tests ...".

**2.15. The context-scaled sentence.** `does not hold`. 04-models-add.tex:83: "The context-scaled mean ...
agrees with the medians where the unscaled mean differs". On npm the unscaled mean and the medians differ in
E03 and E15 (medians 0.007856 and 0.01696, for the reference); the scaled means there are -0.01511 and
-0.01512, still for the model, with intervals [-0.03735, 0.004919] and [-0.03593, 0.001938]. On NYC 311 the
scaled means favor the models in all six rows with intervals below zero, while the medians favor the local
mean in P03 and P18 and are exactly zero in P15. Fix: "The context-scaled mean ... still favors the model on
npm, with an interval that includes zero in E03 and E15, where the medians favor the reference."

**2.16. Horizons left out.** `holds with this fix`. Four statements hold at one horizon and are written
without it: (a) 05-occurrence.tex:45-47, the grid's 4 to 6 of 30 blocks at z = 0.2 against 21 to 26 at z =
0.95, is horizon 30 (at horizon 7, 10 to 18 at z = 0.95); (b) Figure 4's "Below a zero fraction of 0.5 the
substitution loses on both natural panels" is horizon 7 (at horizon 30 on npm it is lower on 28 of 54 and 52
of 99 pairs in the bins from 0.1 to 0.5); (c) the abstract's "for 32 to 43 of the 100 dense ones" spans both
horizons (32 to 40 at horizon 7); (d) the dynamic count "is the best forecaster on the grid after the oracle"
(06-positive-law.tex:44-45) and "beats every foundation model on the grid" (07-discussion.tex:51) at horizon
30 only: at horizon 7 five model variants have a lower mean (1.589 to 1.630 against 1.632) and the dynamic
count is lower than the completed controls in 12, 12 and 16 of 30 blocks. The same holds for
`PAPER-SUMMARY.md` sentence 6. Fix: add "at a month" (or "at a week") in each.

**2.17. Smaller descriptions.** `holds with this fix`. (a) 05-occurrence.tex:63-64, "so the reading is null
at a month": under the quantile score and the CRPS; under the Brier score Chronos-2's hurdle is still lower
on 65 of 100 sparse npm series at a month (raw $p$ $3.7 \times 10^{-5}$, post hoc). (b) 06-positive-law.tex:49,
the TSB hurdle "level with the count hurdle on dense series": on NYC 311 (52 and 46 of 100); on npm it is
lower on 61 and 56 of 100 (medians -0.032 and -0.030). (c) 05-occurrence.tex:80, "the dynamic hurdle's
estimate against a constant near 0.061": at the first origin 58 of the 100 very sparse series have the
dynamic occurrence at exactly 0.5/29 and 16 at 1.5/29, the registered fallback to the Jeffreys estimate, so
the 0.0172 of 03-design.tex:56 is that fallback; say so in a clause. Fix: as stated in each.

## 3. Directions and ties

**3.1. Every registered test.** `holds`. For E01 to E18, S01 to S06 and R01 to R36, recomputed from each run's
`paired_entities.csv`: the median and its sign, lower / tied / higher, the rank sums of the absolute nonzero
differences split by sign (average ranks for ties), the two-sided approximate signed-rank $p$ with zeros
omitted (equal to the file's to a relative $10^{-9}$), the Benjamini-Hochberg adjustment over each family
(equal exactly) and the rejections (12, 5 and 21). The appendix direction table (`tab:s3direction`) matches
in ties, nonzero differences, both rank sums and the side in all 36 rows. No T1 test rejects against H3 and
no T1 median has the opposite sign. The fourteen T2 rejections are stated with the three zero-median rows
(R28, R32, R36, each 22 lower, 77 tied, 1 higher, rank sums 253 against 23) at 06-positive-law.tex:35-39, in
the discussion, in the appendix and in the summary. Fix: none.

**3.2. NYC 311 raw rows.** `holds with this fix`. 04-models-add.tex:82, "the signed-rank test, adjusted within
the table, favors the models in all six", is a rank-sum reading: the medians favor the local mean in P03
($1.055 \times 10^{-9}$) and P18 ($7.001 \times 10^{-5}$) and P15's is exactly zero. P03's median is not
rounding: 15 of the 300 series share exactly that difference, so the appendix's sentence that a median "of
order $10^{-9}$ or smaller ... is floating-point residue" (study2-appendix.tex:21-22, said of npm's E03,
whose very sparse median is the same number) is wrong for it. Fix: "favors the models by rank sum in all
six, with three medians below zero, two above and one exactly zero", and in the appendix "a median of order
$10^{-9}$ is a near-zero score repeated across series, not a tie".

**3.3. T2 in the discussion.** `holds with this fix`. 07-discussion.tex:22, "The dynamic hurdle beats the
empirical count hurdle in 14 of 18 registered tests", gives a side to three rows whose median is zero; and
07:23-24 ("owes as much to the swapped occurrence as to the positive law" on sparse and very sparse series)
differs from 06-positive-law.tex:41-42 ("at least as much ... on very sparse series they owe everything to
it"). Fix: "rejects for the dynamic hurdle in 14 of 18, three of them by rank sum with a median of exactly
zero", and Section 6's wording for the rest.

**3.4. The dynamic count on the natural panels.** `holds with this fix`. 07-discussion.tex:51, "loses to them
on every natural panel": the dynamic count was not run on GitHub, and on NYC 311 pooled over the 300 series
its median against each completed control is exactly zero in all six rows (higher on 124 to 143, lower on 66
to 79). Fix: "loses to them on npm and NYC 311, on the mean and by count".

## 4. The thesis against every table

The thesis (01-introduction.tex:15-24), restated in the abstract's last sentence, the discussion's first
paragraph and `PAPER-SUMMARY.md`'s thesis, has four clauses. Each was tested against the three registered
families, the declared secondary tables (QScore9 by stratum, the context-scaled score, the occurrence Brier
score, the discrete CRPS) and the post-hoc tables on GitHub, npm, NYC 311 and the grid.

**4.1. "The gain over a 28-day local mean comes from the days that are not zero, where the local mean
overpredicts."** `does not hold` on NYC 311. On GitHub it is Table `tab:posthoc` (overprediction -0.088 to
-0.209; zero days +0.004 to +0.015). On npm the overprediction part carries -2,452 to -3,769 of the mean gain
of -2,884 to -5,109, the underprediction part -433 to -1,298 and the zero-day part under 61 either way. On NYC
311 the registered secondary accounting (`reports/study3-nyc311/run-2026-10-17/inference/secondary_accounting.csv`,
stratum `all`, reproduced from the per-series parts) has, for the raw deciles minus the local mean,
underprediction -0.034 to -0.061, zero days -0.010 to -0.022 and overprediction -0.002 to -0.027, of totals
-0.074 to -0.081; the dense stratum has the same order (underprediction -0.106 to -0.174, zero days -0.035 to
-0.052, overprediction -0.008 to -0.080). So on NYC 311 the models gain where the local mean is too low on
positive days, and 12 to 29 percent of the gain is on zero days. The paper prints no NYC 311 or npm accounting of the
raw contrast, so the clause generalizes Study 1's post-hoc reading to panels where the saved accounting says
otherwise. Fix: "On GitHub stars and npm downloads the gain comes from positive days where the local mean
overpredicts; on NYC 311 from positive days where it underpredicts, and partly from zero days", in the
introduction, the discussion's first sentence and the summary's first sentence; the title's "size, not
occurrence" still holds on all three panels for the positive days, less cleanly on NYC 311.

**4.2. "Their own probability of a zero day is at least as good as a context-only estimate ... on dense series
in all three settings."** `does not hold` as worded. It holds under the registered quantile score on every
panel (npm dense 32 to 43 of 100 lower for the substitution; the grid at z = 0.2, 4 to 6 of 30; NYC 311 R01
to R11) and under the occurrence Brier score on NYC 311 and at a week on npm. Under the Brier score at a month
the Jeffreys estimate is the better occurrence forecast on dense npm series, lower on 58, 57 and 62 of 100
with every mean below zero (Table 4's own Brier column), and on the grid's z = 0.8 cells at a month, 20, 21
and 25 of 30 blocks. The discussion (07-discussion.tex:12-14) states the limit; the introduction, the
abstract and the summary do not. Fix: "under the registered quantile score" in the clause, or "and under the
Brier score except at a month on npm".

**4.3. "The one place where a context estimate beats the model's own zero mass on the typical series is the
sparse npm stratum at a week."** `does not hold`. Three tables name other places: (a) R21, a registered T1
rejection for the dynamic occurrence on NYC 311's sparse stratum at a week (TimesFM 2.5, median -0.002116,
57 lower, 8 tied, 35 higher, adjusted $p$ 0.00445), with R23 leaning the same way; (b) the grid's six cells
with z = 0.95 at a month, where the fixed hurdle is lower than its completed control in 21, 26 and 23 of 30
replicate blocks under QScore9, 24, 24 and 22 under the Brier score and 25, 26 and 22 under the CRPS, and in
217 of the 540 series pairs against 91 higher (Appendix Table `tab:s2cells` and its text already say 23 of the
24 differences favor the hurdle in the cells with z = 0.95 and $\mu_+$ of 5 or 25); (c) at a month on sparse
npm series Chronos-2's hurdle is still lower on 58 of 100 under QScore9 and 65 under the Brier score, so "and
not at a month" holds for two models of three. Fix: "The places where a context estimate beats the model's
own zero mass on the typical series are the sparse npm stratum at a week, a secondary reading on one domain,
the grid's cells with z = 0.95 at a month, and one registered test on NYC 311's sparse stratum."

**4.4. "On series that are zero nine days in ten ... the quantile score ties, and nothing about occurrence can
be read."** `does not hold` as worded. It holds on NYC 311's very sparse stratum (2.9; 72 to 88 of 100 tied)
and on npm's nine very sparse series. On the grid's z = 0.95 cells at a month the quantile score ties on 232
of 540 series pairs and favors the substitution on 217 of the other 308, although the models' deciles are all
zero on 20 to 100 percent of the target days there (the benchmark's `grid_occurrence.csv`). 05-occurrence.tex:80-81,
"The same holds for the TSB hurdle and for the grid's cells with z = 0.95", holds for the TSB hurdle (66 to 74
of 100 tied) and not for the grid. Fix: restrict the clause to the natural panels and drop the grid from
05:80-81, reporting the grid's z = 0.95 cells under 4.3.

**4.5. The other secondary tables.** `holds`. The context-scaled score follows QScore9 on NYC 311 in every
stratum (dense T1 lower on 28 to 42 of 100 for the substitution; sparse mixed; very sparse 72 to 88 tied) and
on the grid, and on npm favors the hurdle at a week pooled (E01, E07, E13 with intervals below zero), which is
the sparse stratum's exception; the discrete CRPS follows QScore9 on dense series and separates on very
sparse ones as the Brier score does; the npm very sparse stratum's nine series support nothing beyond their
counts, as the appendix says. No other table contradicts a clause. Fix: none.

## 5. The discussion's attributions and its labels

**5.1. The first reading on dense NYC 311.** `holds`. The dynamic occurrence is worse on the Brier score in
all six dense T1 rows (means 0.00668 to 0.009347, every interval above zero), and the fourth cell against
the count hurdle, which differs in the occurrence alone, puts the model's own occurrence ahead on 62 to 73 of
100 (means -0.0359 to -0.0467). Fix: none.

**5.2. The first reading at a week on the grid.** `holds`. For Chronos-2 and TimesFM 3 the model's zero mass
is lower than the Jeffreys estimate under the count law in 18 and 21 of 30 blocks and under the Brier score
in 19 and 23; TimesFM 2.5 splits 15 to 15 under the count law, as the benchmark page says (lines 165-167).
Fix: none.

**5.3. The second reading at a month on npm.** `does not hold` as worded. 07-discussion.tex:35-36 says the
Jeffreys estimate "is as good as or better than the model's zero mass on the Brier score and under the count
law". On the Brier score yes: the model's zero mass is lower on only 42, 43 and 38 of the 100 dense series.
Under the count law no: the fourth cell against the count hurdle at a month is lower on 43, 48 and 60 of the
100 dense series, with medians +0.037, +0.003 and -0.036 and means -0.84, -2.67 and -5.32, every one in the
model's favor (`npm_contrasts.csv`); the benchmark page rests the second reading on the Brier score alone
(lines 155-164). Fix: "where the Jeffreys estimate is as good as or better than the model's zero mass on the
Brier score, and on the grid under the count law too".

**5.4. The second reading at a month on the grid.** `holds`. The model's zero mass is lower in 15, 13 and 12
of 30 blocks on the Brier score and 10, 13 and 7 under the count law, and the Jeffreys estimate laid over the
truncated laws raises QScore9 in 24, 24 and 25 of 30. Fix: none.

**5.5. "Confirmatory", "secondary", "post hoc".** `holds with this fix`. "Confirmatory" appears in the body at
07-discussion.tex:14, for NYC 311's dense stratum, where the registered family rejects as predicted, and at
08-limitations.tex:33 for item 6's registered analysis; the npm and grid dense reading "rests on the declared
secondary strata" (07:16-17), which says what "consistent with" would; "post hoc" is on the floor counts
(03-design.tex:53), the benchmark (02:22, 03:27, the status columns of Tables 4 and 5) and the fourth cell on
npm and the grid (03:22, 06:24, 06:57-58). The two-readings paragraph (07:26-41) rests its npm and grid
attributions on the post-hoc fourth cell and the declared secondary Brier rows and carries neither label.
Fix: one clause there, "post hoc on npm and the grid".

## 6. The field

**6.1. The works the step-back read places.** `holds`. Croston (1972), Syntetos and Boylan (2005), Teunter,
Syntetos and Babai (2011), Shenstone and Hyndman (2005), Snyder, Ord and Beaumont (2012), Svetunkov and Boylan
(2023), Nikolopoulos et al. (2011) and the two Damato papers (2502.19086v5, 2609.28607v3) are in the related
work's first paragraph; Czado, Gneiting and Held (2009), Kolassa (2016), Wang, Kang and Petropoulos
(2304.03092v4; EJOR 315(3)), Gneiting and Raftery (2007), Bracher et al. (2021), the M5 uncertainty paper
(IJF 38(4) 1365-1385) and Ziel (2107.06675v2) in the second; Chronos, TimesFM, Moirai, GIFT-Eval, fev-bench,
Schoess and von Wangenheim (2609.39386v1), Chin, Cheng and Gunawan (2609.13840v1), Kim and Song, Ebrahim et
al. (2610.00589v1), Ghoroghchian et al., Musat and Cabuz and Meyer et al. in the third, each identifier
matching the step-back read where it gives one. All 57 keys the paper cites are in `references.bib` (60
entries, no duplicates); the three it does not cite (`toner2025`, `hewamalage2023`, `borges2016`) are cited
by the report through `shared/s1-introduction.tex`. Fix: none.

**6.2. The quantile-drop sentence.** `holds with this fix`. 02-related-work.tex:32: "Two recent evaluations
drop every quantile level below the median ... \citep{damato2025, damato2026, tichy2025}" names two and cites
three; the step-back read gives Tichy et al. for the discrete RPS separating models poorly on ultra-slow
series, not for dropping levels. Fix: cite the two Damato papers there and give Tichy et al. its own clause.

**6.3. `bai2026`.** `holds with this fix`. 02-related-work.tex:17 counts it among "benchmark suites of
distributional methods"; the literature re-check (`docs/research/2026-10-11-literature-recheck.md` line 70)
describes a hierarchical empirical-Bayes hurdle with one forgetting operator, and study2-design-detail.tex:129-130
calls it "a pooled hurdle with forgetting". Fix: "and pooled hurdles with forgetting \citep{bai2026}".

**6.4. The Chronos version.** `holds with this fix`. `references.bib` cites 2403.07815v2 (2024-05-02); the
step-back read used v3, the version reviewed on OpenReview. Fix: cite v3, or say why v2.

**6.5. Why Croston and TSB were excluded.** `does not hold`. 02-related-work.tex:20-22: "Croston and TSB were
excluded at registration because they carry no predictive law of their own, the dynamic count was registered
to play TSB's part". `PROTOCOL.md` line 152, in Study 1's baselines and unchanged at `df55867`, says only "No
PyBATS, Croston, TSB or new GBM is included"; Study 2's registration (lines 359-421) never names TSB. The
reason and "registered to play TSB's part" first appear in the step-back read's part B4, written after the
three runs. The sentence appears once (every other "Croston" in the body is about the literature). Fix: "The
protocol excludes Croston and TSB by name without giving a reason; neither carries a predictive law of its
own, and the registered dynamic count is a discounted Bayesian analogue of TSB."

**6.6. The baselines' names.** `holds with this fix`. The related work (02:18-20) names the count hurdle, the
empirical hurdle and the dynamic count as the step-back read's table B1 does. The design (03-design.tex:25-26)
cites `teunter2011` directly on the dynamic count's definition, which reads as if it were TSB. Fix: "the
dynamic count, a discounted Bayesian analogue of TSB \citep{teunter2011}, with a Beta-Bernoulli occurrence
and a Gamma-Poisson size forgotten at 0.98 a day".

**6.7. The TSB hurdle.** `holds with this fix`. 03-design.tex:27 ("the count hurdle with TSB's two estimates in
place of the 28-day ones") agrees with `SPEC.md` (lines 49-71: occurrence level and size level smoothed with
weight 0.1 over the whole context from their first values, positive law $1 + \text{Poisson}(z_m - 1)$,
defined from a single positive day without the count hurdle's fewer-than-two rule, and a point mass at zero
when the context has no positive day). app-runs.tex:74-81 gives the two sensitivities at 0.05 and 0.2 but
never the primary weight, 0.1, nor those two rules. Fix: one sentence there with the weight and the two
rules.

**6.8. The point methods.** `holds with this fix`. They appear only in the appendix (the body names Croston,
SBA and ADIDA only as literature, 02:8-20 and 02:44). The caveat app-runs.tex:82-83, "a point mass loses to
every forecast with a law by construction", is false as written: Croston's method is lower than the
completed Chronos-2 forecast on 19 of the 300 NYC 311 series at a week and on 17 of the 100 sparse ones
(`RESULTS-intermittent-baselines.md` lines 1069 and 1093), since a point mass at zero ties a law whose
deciles are all zero. Fix: `SPEC.md`'s own wording (lines 89-92), "a poor probabilistic forecast by
construction ... every proper score penalizes it on each day the target differs from c". The same phrase is
in the benchmark's row of `docs/README.md`.

**6.9. Nothing claimed as first.** `holds with this fix`. The introduction's disclaimer (01:45) is hedged.
02-related-work.tex:48-49, "None wraps a frozen model's output in a hurdle under a proper score or asks
whether the model's own zero mass or a context estimate is the better occurrence forecast", states as a fact
about the literature what the step-back read states as not found (part B3), adds a second clause it does not
have, and Section 2 no longer mentions the hurdle on frozen Chronos-2 output in Chin et al., judged by point
and service measures, on which the introduction's "to wrap one in a hurdle" rests. Fix: "No evaluation found
wraps a frozen model's output in a hurdle under a proper score; the nearest, Chin et al.'s hurdle on frozen
Chronos-2 output, is judged by point and service measures."

## 7. Labels and conventions

**7.1. The secondary convention.** `holds`. Stated once (03-design.tex:81-83); Tables 3, 4 and 5 carry the
status in their captions and columns. Fix: none.

**7.2. The zero-median rule.** `holds with this fix`. Stated three times in the body (03-design.tex:82-83,
03:97-98, 08-limitations.tex:39-40) and again in Table 4's caption. Fix: keep 03:82-83 and the limitation
item; reduce 03:97-98 to its rank-sum clause.

**7.3. The scope.** `holds`. Once, in the discussion's claim paragraph (07:66-71); the introduction's list of
what is not claimed (01:45) is a different statement. Fix: none.

**7.4. The ledger.** `holds`. Complete against `PROTOCOL.md` and correct in its "Decided" column (2.4); item
6 is flagged in its row ("after the npm scores") and in the paragraph (03:123-125); the two open protocol
sections are named once. Fix: none.

**7.5. The no-work sentence.** `holds`. Once (03-design.tex:121-122), matching `PROTOCOL.md` line 770. Fix:
none.

**7.6. The author's statement.** `holds`. `shared/author-statement.tex` equals `README.md`'s paragraph word
for word, with `\texttt` for the backticks. Fix: none.

## 8. Writing

**8.1. `CONTRIBUTING.md`.** `holds`. Plain, specific, no marketing language. Fix: none.

**8.2. Patterns 1, 3, 4, 5 and 7 of the step-back read's part F.** `holds`. No run logistics, no balance where
the record decides, no review items as motivation, the scope once, no hash or clock time in the body's prose
(commits only in the ledger's column). Fix: none.

**8.3. Pattern 2, work history.** `holds with this fix`. 07-discussion.tex:44-45, "the paper's first draft
gave two readings of that outcome with equal weight. Three things in the record changed that." narrates the
paper's drafting. The step-back read also asked that the paper say the very sparse ties were foreseen before
the run: the record of the run's first stage counted 74 of the 100 very sparse series on the fallback at the
first origin and concluded that "the very sparse rows will carry many exact ties" (`docs/STATE.md`, the
first-stage paragraph); the paper says only that the floor was "not seen until the very sparse ties were
counted". Fix: "The design expected the sparse npm reading to reproduce on a second domain; it did not, and
three things in the record explain why", with one clause that many very sparse ties were counted before the
run.

**8.4. Pattern 9, code identifiers.** `holds with this fix`. `\lm{}` (03-design.tex:26, 04-models-add.tex:10),
`\aets{}` (03:27, 04:15) and `\hc{}` (03:23, 06-positive-law.tex:47, 07-discussion.tex:32, and Table 5's
caption, 06:64 and 06:68) print `local_mean_28`, `autoets_weekly` and `hurdle_count_28` in the body. Fix: the
plain names (the 28-day local mean, weekly AutoETS, the count hurdle); the identifiers stay in Figure 1.

**8.5. Pattern 8, labels in sentences.** `holds with this fix` (judgment). About twenty status labels remain
in the body's prose; most separate statuses within one sentence and should stay. Three repeat what the
table beside them carries (04-models-add.tex:80, 05-occurrence.tex:68, 06-positive-law.tex:32). Fix: drop
those three.

**8.6. Pattern 6, range lists.** `holds` (judgment). Ranges follow the finding they support. Fix: none.

**8.7. The boundary.** `holds`. Nothing in the committed files under `paper/` speaks of how the work was
produced beyond the author's statement. `paper/PROGRESS.md`, a working note excluded from git by
`.git/info/exclude`, does; it must also stay out of any source archive built from `paper/` for posting. Fix:
none in the tree.

**8.8. The abstract.** `holds`. 296 words; identical to `PAPER-SUMMARY.md`'s apart from the math delimiters;
the title identical. Fix: none.

**8.9. The quoted sentences.** `holds with this fix`. Seven of the summary's eight quotations are in the
paper word for word; the eighth, "The three lapses ... between 2026-09-14 and 2026-10-11.", ends with a full
stop where the paper's sentence continues after a colon (03-design.tex:121-122). Fix: end the quotation with
the colon and an ellipsis.

**8.10. The six sentences.** `does not hold`. Six numbered sentences, none a quotation. Sentence 1 says the
models' gain is "on positive days, where the local mean overpredicts ... in every cell of every panel, and on
the typical series on npm and NYC 311": 4.1 contradicts the first half on NYC 311, and the second half is
contradicted by the medians (npm E03 and E15 for the reference; NYC 311 P03 and P18 for the local mean, P15
exactly zero). Sentence 3 repeats 2.14. Sentence 6 needs "at a month" (2.16). Sentence 2 opens a
parenthesis with a capital ("(No pooled test"). Fix: rewrite sentences 1 and 3 from the corrected body
sentences.

## 9. Length and widths

Widths were estimated from the advance widths of the Computer Modern fonts that matplotlib ships (cmr10,
cmti10, cmtt10, cmmi10, cmsy10, read with fontTools), scaled to the table's size (`\small` 9 pt,
`\footnotesize` 8 pt, `\scriptsize` 7 pt) with a correction for the wider small design sizes (1.03 at 9 pt,
1.06 at 8 pt, 1.09 at 7 pt, and, as a second estimate, 1.14 at 7 pt from cmr7's quad), typewriter cells at
0.525 em a character, math with TeX's spacing, no kerning; each column at its widest cell, plus twice the
table's `\tabcolsep`. The limits are 461 pt (A4 less two 24 mm margins) and, for a sideways table, the text
height, 708 pt. The estimates are good to a few percent at 8 and 9 pt and less certain at 7 pt; a second,
cruder computation of Table 4 from cmr10 alone, in the command at the end, gives 490 pt.

**9.1. The length.** `holds`. By the stated method (the expanded paper before `\appendix`, comments, floats
and commands removed, captions apart) the body holds 7,499 words of running text and 1,016 of captions, as
the checker and `PAPER-SUMMARY.md` say; counting only tokens that hold a letter or a digit, 7,358 and 1,003,
of which the author's statement is 141. Five tables and four figures. At 900 words a page and half a page a
float that is 12.8 pages (12.7 by the stricter count), and 13.8 with the two full-page tables at a page each
(see 2.12). Either is over twelve pages: at the same rates the body reaches twelve with about 750 fewer
words, or about 1,650 fewer if the two full-page tables count as a page each, and TMLR's own template will
set the real count. Fix: none to the counts; the cut is the author's choice.

**9.2. Table 4's width.** `does not hold`. `tab:occ` (05-occurrence.tex:83-175, `\scriptsize`,
`\tabcolsep` 1.2 pt) is about 511 pt wide by the primary estimate and 533 pt by the second, against 461 pt;
even with no design-size correction it is 468 pt. Its widest columns are the three "Lower / tied / higher"
headers (about 72 pt each, some 31 pt wider than any count under them) and the forecast column ("TSB vs
TimesFM 2.5", 72 pt). `docs/STATE.md` and `PAPER-SUMMARY.md` say no body table exceeds the text width.
Fix: write the three headers as "L / T / H" and define them in the caption (about 38 pt saved each), or set
them on two lines.

**9.3. Table 5's width.** `holds with this fix`. `tab:pos` (06-positive-law.tex:60-153, `\scriptsize`,
`\tabcolsep` 2.5 pt) is 460 pt by the primary estimate and 479 pt by the second: at the limit. Its widest
cells are "T2: dynamic hurdle vs empirical" (109 pt) and "115 to 129 / 7 to 18 / 68 to 87" (103 pt). Fix:
shorten the contrast names (for example "T2: dynamic vs empirical") and check in the PDF.

**9.4. Tables 1 to 3.** `holds`. `tab:panels` 448 pt (its five columns are fixed `p` widths), `tab:ledger`
456 pt, `tab:raw` 458 to 459 pt, the last with 2 to 3 pt to spare because of its rank-test column ("model,
within-table $p$ $1.42 \times 10^{-5}$", 125 pt). Fix: none, though `tab:raw` should be looked at in the PDF.

**9.5. The two sideways appendix tables.** `holds`. `tab:s3family` (study3-appendix.tex:47-101) is 657 to 683
pt and `tab:s3pooled` (study3-appendix.tex:350-380) 664 to 666 pt against the landscape width of 708 pt;
every spanning header fits its span. Fix: none.

**9.6. The other appendix tables.** `holds with this fix`. By the same estimate five run over the text width:
`tab:s2regime` (study2-appendix.tex:217-238, 502 to 522 pt), `tab:s2scaled` (478 pt), `tab:runs`
(app-runs.tex:19-37, 474 pt), `tab:s2dynrest` (474 pt) and `tab:s2dyn` (470 pt); `tab:s2syn`, `tab:s2ext`
and `tab:s3direction` (462 to 468 pt) are within the estimate's error of the limit, and `tab:s3brier`,
`tab:s3variants` and `tab:s2cells` pass it only under the second estimate. Fix: a smaller `\tabcolsep` or
size for the first five, `tab:s2regime` perhaps sideways, and a look at all eight in the PDF.

**9.7. Heights.** `holds`. The two full-page body tables are about 662 to 668 pt (`tab:occ`, 71 rows and an
eight-line caption) and 684 to 687 pt (`tab:pos`, 74 rows) against a float page of 708 pt; they fit, by 3 to
6 percent. No other float exceeds the top-float fraction. Fix: none, but a longer caption on Table 5 would
push it over.

## 10. LaTeX

The static checks ran on `paper.tex` expanded with its 22 inputs (one nested,
`shared/s1-limitations-items.tex` from `app-study1.tex`) and, for comparison, on `main.tex` with its 14.

**10.1. A broken reference.** `does not hold`. 05-occurrence.tex:55-56 is `series (Table~` followed by a line
`ef{tab:occ}).`; at byte 4,304 of the file the bytes are `~`, a line feed and `ef{`. The backslash and the
`r` of `\ref` became the line break, as a `\r` read as a carriage return would. TeX raises no error: the PDF
would print "(Table  eftab:occ)." The checker does not catch it. A scan of every `.tex`, `.bib`, `.md` and
`.py` file under `paper/` for carriage returns, other control bytes, tabs and line-initial remainders of
eaten commands (`ef{`, `ite{`, `extbf`, `egin{`, `ewcommand` and the like) finds no other case. Fix:
`(Table~\ref{tab:occ})`.

**10.2. Packages and commands.** `holds`. `paper.tex` loads geometry, amsmath, booktabs, graphicx,
`rotating`, url, natbib and hyperref (last); every environment used (abstract, figure, table,
`sidewaystable`, tabular, itemize, quote, verbatim) is provided; `\lm`, `\aets`, `\qs`, `\hc` and
`\reportdoi` are defined before use. `main.tex` neither loads `rotating` nor defines `\hc`, and none of its
files needs either. Fix: none.

**10.3. Balance.** `holds`. Braces balance in all 32 `.tex` files (comments and verbatim skipped);
`\begin` and `\end` balance and nest in both expansions; math delimiters balance in every paragraph and every
table cell. Fix: none.

**10.4. Labels and references.** `holds`. 72 labels in `paper.tex`'s expansion, all unique, all referenced,
no reference without a target (18 in `main.tex`'s, likewise). Fix: none.

**10.5. Citation keys.** `holds`. 57 keys cited by `paper.tex`, 26 by `main.tex`, all in `references.bib`;
each of the 60 entries is cited by one of the two; no duplicate key, no unbalanced brace, no entry without a
title, year or author. Fix: none.

**10.6. The nine figure files.** `holds`. The nine `\includegraphics` of `paper.tex` resolve to PDF files in
`paper/figures/`, each with its PNG beside it; `fig-posthoc-cumulative-h30` is used by `main.tex` only; no
figure file is unused. Fix: none.

**10.7. Column counts.** `holds`. Every row of all 42 tabulars in `paper.tex`'s expansion (and the nine in
`main.tex`'s) has the number of cells its column specification gives, `\multicolumn` counted. Fix: none.

**10.8. The DOI placeholder.** `holds`. `\reportdoi` is defined once in each source (paper.tex:23,
main.tex:17) as "DOI to be filled on posting day" and used only in `\date`, so the placeholder prints on the
title page until the author replaces it, as the comment above it says. Fix: none.

**10.9. The removed section files.** `holds with this fix`. None of the eight removed files exists or is
input anywhere; `check_numbers.py` lines 1326-1333 fail if any reappears. `paper/sources.md` still says in the
present tense that `paper.tex` reads them (lines 199-201, 279-281 and 474-475), though line 604 says the
earlier sections describe the files their numbers came from. Fix: past tense in those three places.

**10.10. One cross-reference.** `holds with this fix`. study2-appendix.tex:479-480, "The analysis summarized
in Section~\ref{sec:positive}": Section 6 does not summarize the post-hoc dynamic-occurrence analysis; the
body uses it once, in the discussion (07-discussion.tex:51-53). Fix: refer to Section~\ref{sec:discussion}.

## What could not be verified

- No TeX compiler is on this machine, so there is no PDF, no page count and no overfull-box report; the
  widths are estimates from the Computer Modern metrics, and the page counts are by word count. The
  design-size corrections (1.03, 1.06, 1.09 and 1.14) are approximations, not read from the fonts' metric
  files, and the fuller width model behind the 511 and 533 pt and the other tables' widths is described in
  Section 9 but not reproduced by the command at the end, which gives only the cruder 490 pt for Table 4.
- The floor counts, the tie classes and the dynamic hurdle's occurrence values were recomputed from the 300
  NYC 311 checkpoints, which are on this machine and not in the tree.
- The bibliography's identifiers were checked against the step-back read and the literature re-check, not
  against the pages themselves (no network); in particular the title of Tichy et al.'s version 5 and the
  Chronos version were not opened.
- Whether TMLR's own style file changes the page count was not checked.

## Closing

The paper may go to the author's read after the fixes above, and not as it stands. Every number in it traces
and no registered table changed, so none of the fixes touches a table entry; what must change before the
author reads the title, the abstract and the summary is the thesis paragraph and the sentences that repeat it
(4.1 to 4.4, carried into the abstract's last sentence and the summary), the discussion's NYC 311 sparse
sentence and its npm attribution (2.14, 5.3), the context-scaled sentence (2.15), the exclusion reason
(6.5), the summary's sentences 1 and 3 (8.10), the broken reference (10.1) and Table 4's width (9.2). The
thesis survives those fixes in a narrower form: the models' gain over a trailing mean is mostly on positive
days on all three natural panels, where the local mean overpredicts on GitHub and npm and underpredicts on
NYC 311; their own zero mass is at least as good as a context estimate on dense series under the registered
score;
and the places where a context estimate does better are named, the sparse npm stratum at a week, the grid's
z = 0.95 cells at a month and one registered test on NYC 311's sparse stratum. The other fixes are wording and
can be made in the same pass.

## Regeneration

The counts above that are not printed in the paper come from saved files by this command, run from the
repository root in PowerShell; the last block reads the 300 NYC 311 checkpoints, which are to be released as
an asset. It adds no test.

```powershell
@'
import glob, json
import numpy as np, pandas as pd
from scipy import stats
RT = dict(float_precision="round_trip"); FM = ["chronos2", "timesfm3", "timesfm2p5"]
NPM, NYC, SYN = "reports/study2-npm/run-2026-10-15", "reports/study3-nyc311/run-2026-10-17", "reports/study2-synthetic-2026-10-15"
npm, nyc, syn = (pd.read_csv(f"{r}/inference/series_scores.csv", **RT) for r in (NPM, NYC, SYN))
def diff(d, a, b, h, col, st=None):
    x = d[(d.model == a) & (d.horizon == h)].set_index("series_id")
    y = d[(d.model == b) & (d.horizon == h)].set_index("series_id")
    out = (x[col] - y[col]).dropna()
    return out if st is None else out[x.stratum.reindex(out.index) == st]
def blocks(d, a, b, h, col):
    f = lambda m: d[(d.model == m) & (d.horizon == h)].groupby("replicate")[col].mean()
    return f(a) - f(b)
lth = lambda x: f"{int((x < 0).sum())}/{int((x == 0).sum())}/{int((x > 0).sum())}"
# 1. Raw deciles minus the local mean: the mean of each accounting part, all series (thesis, first clause).
for name, d in (("npm", npm), ("nyc311", nyc)):
    for h in (7, 30):
        print(name, h, [(m, *(round(float(diff(d, f"{m}_raw", "local_mean_28", h, p).mean()), 4)
                              for p in ("qscore9", "zero", "positive_over", "positive_under"))) for m in FM])
# 2. Fixed hurdle minus completed on the grid, replicate blocks within each zero probability.
z = pd.read_csv(f"{SYN}/inference/secondary_cells.csv").drop_duplicates("cell_id").set_index("cell_id").zero_probability
for zp in (0.2, 0.8, 0.95):
    g = syn[syn.cell_id.map(z) == zp]
    for h in (7, 30):
        print("grid z", zp, h, {s: [lth(blocks(g, f"{m}_hurdle", f"{m}_completed", h, s)) for m in FM]
                                for s in ("qscore9", "occurrence_brier", "discrete_crps")})
    pairs = [diff(g, f"{m}_hurdle", f"{m}_completed", 30, "qscore9") for m in FM]
    print("  series pairs at 30:", lth(pd.concat(pairs)))
# 3. Dense npm at a month: the fixed hurdle's Brier score, and the fourth cell against the count hurdle.
print("npm dense 30 brier", [lth(diff(npm, f"{m}_hurdle", f"{m}_completed", 30, "occurrence_brier", "dense")) for m in FM])
ben = pd.read_csv("reports/study2-posthoc-intermittent-baselines/npm_contrasts.csv", **RT)
r = ben[ben.variant.str.endswith("occurrence_model_size_count") & (ben.reference == "hurdle_count_28") & (ben.group == "dense") & (ben.horizon == 30) & (ben.metric == "qscore9")]
print("npm dense 30 fourth cell vs count hurdle", r[["variant", "wins", "ties", "losses", "median_diff", "mean_diff"]].to_string(index=False))
# 4. Sparse npm at a month, Chronos-2, under QScore9 and the Brier score.
print("npm sparse 30 chronos2", [lth(diff(npm, "chronos2_hurdle", "chronos2_completed", 30, s, "sparse")) for s in ("qscore9", "occurrence_brier")])
# 5. Figure 3 on npm (the first point is aggregate-error alone); P03's median; the dynamic count.
for m in FM:
    x = np.sort(diff(npm, f"{m}_raw", "local_mean_28", 30, "qscore9").to_numpy())
    print("npm figure 3", m, "first point", round(float(x[0] / len(x)), 1), "final", round(float(x.mean()), 2), "lower", int((x < 0).sum()))
x = diff(nyc, "chronos2_raw", "local_mean_28", 7, "qscore9")
print("P03 median", float(np.median(x)), "series with exactly that difference", int((x == np.median(x)).sum()))
print("nyc311 pooled dynamic count vs completed", [lth(diff(nyc, "dynamic_count", f"{m}_completed", h, "qscore9")) for h in (7, 30) for m in FM])
print("grid 7 dynamic count vs completed", [lth(blocks(syn, "dynamic_count", f"{m}_completed", 7, "qscore9")) for m in FM])
# 6. Table 4's width, crudely: widest cell per column in cmr10 advance widths at 7 pt times 1.09, plus 2 x 1.2 pt.
import re, matplotlib
from fontTools.ttLib import TTFont
font = TTFont(f"{matplotlib.get_data_path()}/fonts/ttf/cmr10.ttf"); cmap, adv, em = font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm
w = lambda s: sum(adv[cmap[ord(c)]][0] if ord(c) in cmap else em / 2 for c in s) / em * 7 * 1.09
tex = open("paper/sections/05-occurrence.tex", encoding="utf-8").read()
tab = tex[tex.index("\\begin{tabular}{lrlclclclc}") + 27:tex.index("\\end{tabular}")]
cols = {}
for row in tab.split("\\\\"):
    row = re.sub(r"\\(toprule|midrule|bottomrule)|\\cmidrule\(lr\)\{[^}]*\}", "", row)
    for i, c in enumerate(row.split("&") if "&" in row else []):
        if "multicolumn" not in c:
            c = re.sub(r"\$(-?[\d.]+) \\times 10\^\{(-?\d+)\}\$", r"\1x10\2", c.strip()).replace("$", "")
            cols[i] = max(cols.get(i, 0), w(c))
print("table 4 width about", round(sum(cols.values()) + 2.4 * len(cols)), "pt against 461")
# 7. The completion floor (first lead and every lead) and the dynamic hurdle's p, from the 300 checkpoints.
st = {s["series_id"]: s["stratum"] for s in json.load(open("reports/study3-nyc311/panel/manifest.json", encoding="utf-8"))["series"]}
first, every, ps = {}, {}, {}
for path in glob.glob(f"{NYC}/[0-9a-f]*.json"):
    for row in json.load(open(path, encoding="utf-8"))["rows"]:
        if st[row["series_id"]] != "very_sparse":
            continue
        laws = row["forecast"]["distributions"]
        m = row["model"].rsplit("_", 1)[0] if row["model"].endswith("_completed") else None
        if m in FM:
            on = [law["deciles"][-1] < 0.5 for law in laws]
            first[m] = first.get(m, 0) + on[0]; every[m] = every.get(m, 0) + all(on)
        if row["model"] == "chronos2_hurdle_dynamic" and row["cutoff"] == "2026-06-03" and row["horizon"] == 7:
            p = round(laws[0]["p"], 5); ps[p] = ps.get(p, 0) + 1
print("floor, first lead", first, "every lead", every)
print("dynamic p at the first origin, most common", sorted(ps.items(), key=lambda kv: -kv[1])[:3], "0.5/29 =", round(0.5 / 29, 5), "1.5/29 =", round(1.5 / 29, 5))
'@ | .\.venv\Scripts\python.exe -
```

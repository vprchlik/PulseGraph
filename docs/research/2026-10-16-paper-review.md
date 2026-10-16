# Review of the paper

Written 2026-10-16 05:10 UTC. A read-only review of the paper under `paper/` (`paper.tex` with its inputs
under `paper/shared/` and `paper/sections/`, `PAPER-SUMMARY.md`, `sources.md`, `check_numbers.py`,
`references.bib`, the five figures) as committed in `c330315`, by a reader other than its writer, against the
record: `PROTOCOL.md` with its dated additions (2026-10-12 items 1 to 3; 2026-10-15 item 5; 2026-10-16
item 6), `RESULTS.md`, the two Study 2 evidence packages, the six research documents under
`docs/research/` and the writing rules in `CONTRIBUTING.md`. Nothing under `paper/` was changed; the fixes
below are instructions for the revision.

Each verdict is `holds`, `holds with this fix` or `does not hold`; `does not hold` is used only where a file
contradicts the text. `NR` stands for `reports/study2-npm/run-2026-10-15`, `SR` for
`reports/study2-synthetic-2026-10-15`. Line numbers refer to `paper/paper.tex` unless a file is named;
`sections/` and `shared/` are under `paper/`. In the compiled paper Sections 1 to 6 are the report's, 7 to
10 Study 2's question, design, npm panel and results, 11 the discussion, 12 the limitations, 13 what is not
run, 14 reproducibility, 15 the author's statement; Appendices A to D are the report's, E and F the Study 2
design and panel detail, G the Study 2 commands, H the secondary tables. Tables 1 to 4 are the report's,
Table 5 the external family (`tab:s2family`), 6 the synthetic family, 7 the npm panel, 8 and 9 the two
results families (`tab:s2ext`, `tab:s2syn`), 10 the accounting parts (`tab:s2parts`); in the appendix Tables
11 to 15 are the report's Tables 5 to 9, then 16 the scaled score, 17 the strata, 18 the sensitivity
(`tab:s2sens`), 19 the cells, 20 and 21 the model scores. Figures 1 and 2 are the report's, 3 the npm
differences, 4 the synthetic cells, 5 the zero-fraction scatter. Figures quoted below that are not in the
paper come from saved files by the command at the end.

## 1. The report is unchanged

**1. The report's text.** `holds`. `paper/main.tex` with its fourteen `\input` lines expanded is 48,238
bytes and equals `git show f325a67:paper/main.tex` byte for byte (SHA-256 `85b77ce0...1498` for both; LF in
every file, no carriage return). Each of the fourteen shared files appears verbatim in the committed report,
and `paper.tex` reads all fourteen and no edited copy. The three report figures are unchanged since
`f325a67` (`git diff --stat f325a67 HEAD -- paper/figures/` lists only the two new figures and the figure
script). The bibliography entries the report cites for the six re-check items gained given names and notes
since `f325a67`, so the report's compiled reference list changes in those names, not in meaning. Fix: none.

**2. The report's dated Study 2 sentence.** `holds with this fix`. `main.tex` lines 82 to 83 (not a shared
file) say "As of 2026-10-12, a statement to be re-checked on the posting day, no Study 2 target value,
forecast or score exists". Both Study 2 runs have since been made (`f950300`, `26a8913`), so on the report's
posting day the sentence is false as a present statement. Fix: before the report is posted, keep the date
and add that both Study 2 runs have since been made and are reported in the paper; the paper is not
affected, since the sentence is in `main.tex` alone.

## 2. Numbers

**3. The checker passes.** `holds`. `paper/check_numbers.py`, run at 2026-10-16 04:48 UTC: "654 checks, 0
failures, 0 skipped", exit code 0. `ruff check` and `ruff format --check` on `paper/` are clean. Fix: none.

**4. Tables 8 and 9, traced independently.** `holds`. Recomputed from both `inference/paired_entities.csv`
files (parsed with `float_precision="round_trip"`) without the project's inference code: every mean and
median equals `inference.csv` exactly; every interval, redrawn from the row's saved `bootstrap_seed` with the
registered 20,000 whole-entity replicates, agrees to within 3.1e-16; every two-sided approximate Wilcoxon
p-value and every Benjamini-Hochberg p-value (computed independently) agrees to 1e-12; the counts agree
exactly. Every printed cell of the 24 rows, rounded to the digits printed, equals the recomputation. Fix:
none.

**5. Section 10's figures.** `holds`. Traced to their files: the family counts (12 of 18 reject, 10 for the
variant and 2 against it; 5 of 6, all against the hurdle); the hurdle-against-control ranges (means 90.24 to
253.9, every interval above zero, medians within 0.014 of zero, three each side, lower on 81 to 121, E10 and
E16 higher on 120 and 107 with adjusted p 0.00215 and 0.0276, the others 0.203 to 0.628); the count-hurdle
and raw rows; Table 10 cell by cell from `secondary_accounting.csv` (hurdle minus completed), and the
synthetic part ranges 0.3947 to 0.4294 against 0.5798 to 0.624 and 1.316 to 1.39 against 1.029 to 1.085;
`aggregate-error` as the largest leave-one-out mover in all 18 rows with the sign of the mean, the means
without it 0.6334 to 1.599, and the top-five share of positive gain 0.9954 to 0.9981 over the twelve rows;
the runs (`SR/run.json` and `NR/run.json`: 20:16:33 to 20:38:30 and 23:27:10 to 23:38:42 UTC, 1,317.3 and
692.4 seconds, one invocation, no failure or resume, commits `3fc3411` and `3057b16`, readiness 20:13:56 and
23:09:06, estimates 1,539 and 1,741, budgets 2,400 and 3,600, driver 610.88, CUDA 12.8, PyTorch 2.11.0, the
same peak of 2,948,595,712 bytes in both); the integrity log (209 of 209 hashes, 0 of 20,064 disagree, the
Brier score on 13,794) and the synthetic recomputation (largest difference 0.0 over 55,080; the script checks
the 540 hashes); the CRPS counts 66, 13,728, 13,794 and 6,270; the zero days from
`NR/target-pull/daily_summary.csv` (0 of 209 on 2026-07-12 and 2026-08-14 between 4,059,870 and 10,123,968
and between 7,480,108 and 2,560,140; on 2026-06-25 the largest series 0 between 9,475,033 and 7,909,626 with
92 series at 0 against 98 and 121; over the 275 context days at most 153 series at 0 and the largest series
never below 1,109,682); the secondary readings (scaled, Brier, strata, 23 of 24 cells at z = 0.95 and
mu+ of 5 or 25, the largest cell differences at z = 0.2 and mu+ = 25). Fix: none.

**6. The sensitivity table.** `holds`. Every printed cell of Table 18 equals a recomputation from
`NR/posthoc/sensitivity_paired_entities.csv` (means, BH p over the eighteen of each scenario, rejection, the
side of the larger rank sum). Re-running `NR/posthoc/sensitivity_zero_days.py` from the 209 checkpoints
into a scratch directory reproduced `sensitivity_inference.csv` (SHA-256 `1a849c4f...`) and
`sensitivity_paired_entities.csv` (`a35dc542...`) byte for byte. E06 without the two panel-wide days: BH p
0.05988 and raw p 0.03992 against 0.01193 and 0.00663, the model lower on 110 of 209; E04, E10 and E16
without the three days 159.3, 201.2 and 183.4; the horizon-7 rows identical in mean, counts and raw p in both
scenarios; no hurdle-contrast row changes rejection, mean sign or rank side in either. Fix: none.

**7. The abstract's numbers.** `holds`. The Study 1 figures are the report's (traced on 2026-10-12, and
unchanged by item 1); 209 (100, 100, 9), two of six, all six, 540, five of six and 7.6 million trace as in
items 4 to 6 and 8. Fix: none.

**8. The npm panel's figures.** `holds`. Section 9, Table 7 and Appendix F against
`study/study2/npm_panel_status.json` and `reports/study2-npm/panel/manifest.json`: 4,486,927 names in 4,493
pages from 00:23 to 02:04 UTC; 12,943 visited, 10,000 eligible, 2,918 ineligible, 25 excluded on HTTP 404;
the frame estimate 4,486,927 x 10,000 / 12,943 = 3,466,682 with bounds 10,000 and 4,483,984; inclusion
probability 0.0029 with bounds 0.0022 and 1; 9,998 complete and the two named exclusions; 12,762 attempts
(9,998, 40, 2,708, 2, 14); strata 2,431, 7,558 and 9; creation dates 2011-08-26 to 2025-08-08 and 80 scoped
names; frozen 01:57:03 and verified 02:00:20 UTC; the budget figures. The last-28-day means 7,637,136 for
`aggregate-error` and 13,014 for the next series were read from the frozen context file, which is not in the
tree. Fix: none.

**9. "The lowest cell mean in 17 of the 18 cells."** `holds with this fix`. `SR/inference/secondary_cells.csv`
at horizon 30: the oracle is strictly lowest in 14 cells, below two forecasters in `cell00`, and exactly tied
with `dynamic_count` in `cell12`, `cell14` and `cell16` (z = 0.95, rho = 0; in `cell12` also with
`timesfm2p5_completed`). The sentence is at `sections/study2-results.tex` lines 216 to 217,
`sections/study2-appendix.tex` line 40 and `PAPER-SUMMARY.md` line 73. Fix: write "no forecaster scores below
it in 17 of the 18 cells; in three of them `dynamic_count` ties it exactly".

**10. "From two downloads a day to millions."** `holds with this fix`. Line 106. Two downloads a day is the
median series' last-28-day mean (`NR/RESULTS-npm.md` lines 79 to 80); the smallest is 0. Fix: "from a
median of two downloads a day to millions".

**11. The AutoETS horizon-30 mean in Table 20.** `holds with this fix`. The caption
(`sections/study2-appendix.tex` lines 210 to 211) says the 74,699 "comes from the dense stratum". It is
carried by one series, `composer-runtime-pouchdb` (11,155,852, 0.715 of the summed series scores), not by
`aggregate-error`, which holds 0.975 to 0.989 of the summed series scores in each of the other 31 unscaled
rows (`NR/inference/series_scores.csv`). Fix: name `composer-runtime-pouchdb` for the AutoETS row and say
that the other unscaled means are carried by `aggregate-error`.

**12. The time of the first target request.** `holds with this fix`. `sections/study2-panel.tex` line 13
("first requested ... at 23:14 UTC") and `sections/study2-results.tex` line 97 ("between 23:14 and 23:26
UTC"). `NR/target-pull/pull.json` records the requesting invocation from 23:15:02 to 23:26:21 UTC and
`completeness.json` the first answer at 23:15:05. The "23:14:58 to 23:26:22" of `NR/RESULTS-npm.md` line 20,
which `paper/sources.md` line 366 attributes to `pull.json`, is the start and end of the pull process, not
of the requests. Fix: write 23:15 in both places and correct the source row.

**13. Two word counts in the record.** `holds with this fix`. `PAPER-SUMMARY.md` lines 115 to 116 give the
paper's body as about 12,000 words beside the report's 4,200; `sources.md` line 396 gives about 11,000
beside 4,900. By this review's count the body has 11,286 words of running text and 778 of captions, and the
report's body 3,836 of running text (counts depend on the method). Fix: give one pair of figures with its
method in both files.

## 3. Directions

**14. The 24 comparisons.** `holds`. From both `paired_entities.csv` files the sign of every median, every
lower / tied / higher count and the side of the larger signed-rank sum were recomputed (zeros omitted,
average ranks). The lower / tied / higher columns of Tables 8 and 9 and the "Favors" column of Table 18 agree
row by row. In every rejecting row the mean, the median and the larger rank sum point the same way. BH
rejections equal `inference.csv`. Fix: none.

**15. "No comparison favors the substitution."** `does not hold`. The abstract (lines 44 to 45),
`sections/study2-results.tex` line 135 ("No external comparison favors the hurdle variant"), line 264 ("on
npm no cell favors the hurdle"), and `PAPER-SUMMARY.md` lines 32 and 50. In E01 the typical series favors the
hurdle: median -0.01376, the hurdle lower on 121 of 209 series and higher on 86, and the larger signed-rank
sum on the hurdle's side (12,017 against 9,511), which Table 18's own "Favors" column records as "model".
In E04 and E13 the median and the count lean to the hurdle (105 against 102; 109 against 97) while the rank
sums lean to the control (9,997.5 against 11,530.5; 10,203 against 11,118). Only the means favor the
control in all six cells, and the means are `aggregate-error`'s. `NR/RESULTS-npm.md` line 150 has the
qualified form: "No comparison favors the hurdle variant at BH q = 0.05". Line 92's "no test favors it" is
right. Fix: write "no test favors the substitution at q = 0.05" in each place, and add one sentence to
Section 10 that in E01 the typical series leans to the hurdle (not rejected, adjusted p 0.203), as do the
medians and counts of E04 and E13.

**16. "Ties for the third."** `holds with this fix`. Line 101 ("loses for two models and ties for the
third"), `sections/study2-results.tex` line 266 ("loses or ties on the grid") and `PAPER-SUMMARY.md` lines
56 to 57. S04 is not tied: mean 0.0215 against the TimesFM 3 hurdle, median 0.03119, the hurdle lower on 11
of 30 blocks, the larger rank sum on the count hurdle's side (308 against 157), adjusted p 0.12; Section 10
itself says "not rejecting is not equivalence" (line 135). Fix: "and is not rejected for the third, which
leans the same way".

**17. The raw contrast's rank side.** `holds with this fix`. `sections/study2-results.tex` line 195 ("with
the rank test on the model's side in four cells"). The larger rank sum is on the model's side in all six raw
rows, including E03 (11,523 against 10,422) and E15 (11,150 against 10,586), where the medians and counts
favor the reference; four reject. Fix: "rejecting on the model's side in four cells, with the rank sums
leaning that way in the other two while their medians favor the reference".

**18. The Brier sentence of the discussion.** `holds with this fix`. Lines 92 to 96: the occurrence Brier
gain of E01, E04 and E13 "does not carry over to the quantile score". Those are exactly the three rows where
the median QScore9 difference and the win count lean to the hurdle (item 15). Fix: "does not carry over to
the mean quantile score, which `aggregate-error` carries; in those three rows the median and the count lean
to the hurdle, none significantly".

## 4. Claims against the record

**19. The families and their authority.** `holds with this fix`. `sections/study2-design.tex` lines 100 to
118 state the 54 registered tests, the 2026-10-12 addition, item 3 (`8db0d73`), as the authority for E01 to
E18 with one BH, and E19 to E54 as a later family of 36, as `PROTOCOL.md` lines 799 to 810 say; Tables 5 and
6 equal the protocol's tuples (lines 455 to 472 and 563 to 568). Lines 12 to 18 describe the design "as it
stands after two dated additions"; a third, of 2026-10-16 (item 6, `1c09ac8`), now exists, and the paper
names it nowhere by commit. Fix: "after three dated additions; the third, made after the npm scores were
seen, changes nothing in the design (Section 10)", and cite `1c09ac8` where addition 6 is named.

**20. The matched comparators.** `does not hold`. `sections/study2-design.tex` lines 94 to 96: "The count
hurdles and the dynamic count are the registered matched comparators: the same occurrence rule as the
foundation-model hurdle". The dynamic count's occurrence is its discounted Beta-Bernoulli estimate
a_B / (a_B + b_B) (`PROTOCOL.md` lines 413 to 416; the same paragraph's lines 91 to 93), not the 28-day
Jeffreys rule. Fix: "The two count hurdles share the foundation-model hurdle's occurrence rule; the dynamic
count has its own discounted occurrence; none has a positive law from a foundation model."

**21. The reduced stratum.** `holds`. The abstract, Section 9 and Table 7, the secondary paragraph of
Section 10, Appendix H's text and Table 17's caption, and the limitations each state the very sparse stratum
as 9 series. Fix: none.

**22. The dominant series beside every npm mean.** `holds with this fix`. Stated in the abstract, Section 9,
Table 8's and Table 10's captions, Figure 3's caption, Section 10's dominant-series paragraph and the
limitations. Not stated beside the means at `sections/study2-results.tex` lines 129 to 130 (90.24 to 253.9),
175 to 176 (-5,090 to -6,918) and 267 ("beat the local mean on the npm mean"), lines 89 to 92 and 99 to 101 of
the discussion, Table 18's caption and Table 20's caption. Fix: add "(carried by `aggregate-error`)" at each.

**23. The zero days and the order of the sensitivity.** `holds with this fix`. The days are described as
served, the confirmatory analysis is the registered one, the sensitivity is labeled post-hoc in Section 10,
Table 18 and the limitations, and no change in a direction or rejection is hidden. But
`sections/study2-results.tex` line 243 says the sensitivity was computed "under item 6", and lines 122 to 124
that the addition "requires" it. `NR/posthoc/sensitivity.json` records `started_at` 2026-10-16 03:21:52 UTC;
the addition was appended at 03:28 UTC (`PROTOCOL.md` line 835) and both were committed together in
`1c09ac8`. Fix: say that the sensitivity was computed at 03:21 UTC, before addition 6 was written, and
committed with it; the addition keeps the registered analysis, the registered default, so no confirmatory
result depends on the order.

**24. The integrity recomputation.** `holds`. `NR/integrity/integrity.log`: "209 of 209 hashes equal
run.json"; QScore9, the three parts and the scaled score 0 of 20,064 disagree; the Brier score 0 of 13,794;
the CRPS availability counts as printed. `SR/recompute_scores.py` checks each checkpoint against `run.json`
before recomputing. Fix: none.

**25. The oracle.** `holds`. Called a diagnostic, neither a competitor nor a confirmatory contrast, in
Section 8, Appendix H and Table 21's caption, as `PROTOCOL.md` lines 551 to 555 say; for its cell count see
item 9. Fix: none.

**26. What is not run.** `holds with this fix`. Section 13 and Appendix E report the October holdout, NYC
311 and Wikipedia and Study 1's follow-up as registered and not run, matching the 2026-10-12 addition, items
1 and 3, and `PROTOCOL.md` lines 64 to 76. Lines 202 to 203 say the November round "was considered and not
registered", which can become false before posting: it can still be registered by a dated addition before
2026-10-28 18:00 UTC (`docs/STATE.md`). Fix: date the sentence ("as of 2026-10-16") and re-check it on the
posting day.

**27. The contamination categories.** `holds`. Appendix E (`sections/study2-design-detail.tex` lines 59 to
68) and the limitation item (lines 160 to 165) keep the three categories and match the npm and synthetic
rows of `PROTOCOL.md` (lines 651 and 656). Fix: none.

**28. The npm-versus-grid difference.** `holds with this fix`. The discussion (lines 103 to 108) reports the
reversal without attributing it. The limitation item (lines 166 to 168) goes further: "so the grid is a
favorable setting for the count hurdle and an unfavorable one for a foundation model's size forecast". The
first half follows from the generator; nothing in the record measures the second. Fix: "so the count
hurdle's positive law is correctly specified on the grid, up to its estimated mean".

**29. The accounting trade, on the mean and on the typical series.** `holds with this fix`. Table 10 and
`sections/study2-results.tex` lines 139 to 143 give the trade as equal-series and equal-block means, and
those are right. Lines 89 to 92 of the discussion, line 143 ("it goes the same way on both studies") and
`PAPER-SUMMARY.md` lines 52 to 53 state it without that qualifier. A post-hoc look by this review at the
saved per-series parts (`NR/inference/series_scores.csv`, `SR/inference/series_scores.csv`; it adds no test):
the npm means without `aggregate-error` show the same trade in all six cells (zero-day part -0.32 to -0.40,
overprediction -0.18 to -1.15, underprediction +2.10 to +2.34), and on the grid 29, 29 and 30 of the 30
replicate blocks show it; but the median npm series' zero-day difference is positive in all six cells (0.003
to 0.036, the hurdle raising that loss), and only 49 to 84 of 209 series show the trade. Fix: say "on the
mean" in the three places, and that the typical npm series does not follow the trade.

**30. The published daily counts.** `holds with this fix`. Lines 224 to 225 and
`sections/study2-panel-detail.tex` lines 35 to 36 say the aggregated daily counts of the 209 series "are
published with the paper". They are not in the tree (`npm_panel_status.json`: `panel.context.in_tree` false;
the targets are in the ignored raw directory) and no release exists. `CONTRIBUTING.md` asks that the
aggregated daily-count dataset be committed if its size allows; the context and target files are 76 KB and
105 KB. The redistribution review of 2026-10-15 found that the 209 series may be published with the data
statement. Fix: commit the 209 series' daily counts, context and targets, under `reports/study2-npm/` before
posting, or write "are to be published".

**31. "Rank-based and unaffected."** `holds with this fix`. `sections/study2-panel.tex` lines 72 to 73 and
`sections/study2-results.tex` lines 202 to 203 call the medians, counts and signed-rank tests "rank-based and
unaffected" by `aggregate-error`. The series still counts once in each and carries the largest rank in the
signed-rank sums (209 of 21,945 where no difference is zero). Fix: "not dominated by it; it counts once".

## 5. The claim

**32. Priority wording.** `holds`. "First" appears only in ordinary senses or in the negations the
literature re-check requires (`sections/study2-question.tex` lines 71 to 73; lines 124 to 127); no "novel",
"new" or "no prior" as a claim. Fix: none.

**33. The six items, and the rest of the re-check.** `holds with this fix`. Schoess and von Wangenheim and
Ebrahim, Ali and El-Kotory are cited in the introduction, Section 7 and the discussion; Chin, Cheng and
Gunawan in Section 7 and the discussion; Islam and Mohammed beside Kim and Song in the same three places;
Moghadasi and Ghaderi in the Study 1 limitation, the holdout paragraph, Section 7 and the discussion; Garza
et al. in the introduction, Section 7 and the discussion with the popularity-versus-population contrast. The
re-check (lines 146 to 149) puts EXAONE Demand in the limitations; the paper cites it in Section 7
(`sections/study2-question.tex` lines 60 to 61). It calls fable.intermittent and Bai and Chu "reference
points"; the paper calls them "reference implementations" (`sections/study2-question.tex` line 59,
`sections/study2-design.tex` lines 96 to 98), and Bai and Chu is a model, not an implementation. Fix: add
EXAONE Demand to the limitations in one clause, and write "reference points".

**34. The scope of the claim.** `holds with this fix`. The paper claims "the registered combination ... on
daily attention and adoption counts" (lines 49 to 50; `sections/study2-question.tex` lines 68 to 71; lines
119 to 124). The re-check allows that much (its lines 137 to 139), written when three external domains were
to run. The occurrence substitution ran on one adoption-count domain, npm, and on the synthetic grid; no
attention-count series (GitHub stars or Wikipedia pageviews) went through the hurdle construction, and the
GitHub holdout lapsed. Fix: claim the combination on daily npm download counts and the registered grid, with
Study 1's attention counts for the raw comparison only, in all three places.

**35. The titles read from arXiv.** `holds with this fix`. Nine of the ten titles in `references.bib`
equal the re-check's titles for the same identifiers and versions, case aside; the re-check gives no title
for `meyer2025`, and no given names for any of the ten, so those could not be checked without network
access. The header comments (`references.bib` lines 1 to 4 and 227 to 229) still say the entries carry only
what the record holds, surnames where it gives surnames; the entries now carry names read from the abstract
pages on 2026-10-16. Fix: name the arXiv abstract pages of 2026-10-16 as a source in both comments.

## 6. Post-hoc labels and the two summaries

**36. A post-hoc result stated without its label.** `holds with this fix`. Section 6, Figures 2 and 5, the
by-stratum reading of Section 5, Section 10's sensitivity paragraph, Table 18 and the limitation item are
labeled. The discussion's first sentence (lines 85 to 87) states the Study 1 accounting ("Study 1 found the
models' mean gain ... on positive days where the local mean overpredicts, and a zero-day part against the
models") without the label. Fix: "Study 1's post-hoc accounting located ...".

**37. The two summaries together.** `holds with this fix`. The tables and Section 10's three contrast
paragraphs give the mean and the typical series side by side. The direction of the hurdle-against-control
contrast is then summarized by the mean alone in the abstract, Section 10's closing paragraph, the
discussion and `PAPER-SUMMARY.md`. Fix: the fixes of items 15, 18, 22 and 29.

**38. Shares of positive gain.** `holds`. Every share is a share of positive gain (`sections/study2-results.tex`
lines 201 to 202; lines 115 to 116; Table 15), never of net gain. Fix: none.

**39. The signed-rank test.** `holds`. No sentence reads it as a test of the mean; the Study 1 limitation
item says it is not one, and the Study 2 sentences name "the rank test" apart from the mean. Fix: none.

## 7. Writing and the boundary

**40. The writing rules.** `holds with this fix`. Plain and specific; no marketing language, emoji or phase
roadmap; no non-ASCII character in any file under `paper/`. Three things repeat: the dominant-series
explanation is written out in full in Section 9, twice in Section 10, in the limitations and in the captions
of Table 8 and Figure 3; the claim paragraph appears in Section 7 (`sections/study2-question.tex` lines 63 to
73) and in the discussion (lines 119 to 134); Section 10's secondary paragraph repeats Appendix H. Lines 16
to 17 of `sections/study2-results.tex` say the summaries are shown together "because they disagree"; they agree
in most rows; the discussion's "because they can disagree" (line 117) is right. Inside the paper, Sections 1
to 6 keep the report's "this report"; line 55's "This paper extends that report" covers it. Fix: state each
repeated passage once in full and refer to it elsewhere, and write "because they can disagree".

**41. The boundary and the author's statement.** `holds`. Nothing in `paper.tex`, `sections/`, `shared/` or
`PAPER-SUMMARY.md` mentions how the work was produced beyond Section 15, and Section 15's quotation
(`shared/author-statement.tex`) equals `README.md` lines 11 to 18 word for word, with code spans set in
`\texttt`. Fix: none.

**42. The abstract.** `holds with this fix`. 300 words by two counts, at the limit. The copy in
`PAPER-SUMMARY.md` (lines 20 to 38) has 304 words and differs in one phrase ("100 sparse and 9 very sparse,
the last short"). The fixes of items 15 and 34 add words. One version at 300 words: "and test one
mechanism." for "and test one mechanism behind the answer."; "(commit 5f01769, 2026-09-12)"; "on GitHub star
counts" for "on daily GitHub star counts"; "no test favors the substitution at q = 0.05 and two of six reject
against it"; "On a 540-series synthetic grid"; and "A literature re-check allows the claim of this
registered combination, here run on one of three external domains, and nothing broader." Fix: make the two
copies identical, at most 300 words.

**43. Length, and what to move.** `holds with this fix`. No compiler, so no page count. The body has 11,286
words of running text, 778 of captions, ten tables and four full-width figures: at about 900 words a page,
about 12.5 pages of text and 5 to 6 of floats, about 18 pages before the references, against the aim of
twelve to fourteen in `PAPER-SUMMARY.md`. The appendix has 3,424 words, eleven tables and one figure. By
section: Study 2 results 2,395 words, design 1,727, limitations 1,061, question 930, discussion 766, panel
744. Fix, about four pages: move Tables 5 and 6 to Appendix E and name the families in one sentence; move
the frame-and-sampling, completion and baselines paragraphs of Section 8 to Appendix E, leaving a short
summary; move the inventory, walk and context-pull paragraphs of Section 9 to Appendix F; move "The runs" to
Appendix G and Figure 4 to Appendix H; cut Section 10's secondary paragraph to two sentences; keep the claim
paragraph once; shorten the npm contamination and dominant-series limitation items to one sentence each.

## 8. LaTeX

**44. Static checks.** `holds`. Standard packages only (geometry, amsmath, booktabs, graphicx, url, natbib,
hyperref); braces balanced; every environment closed in order; 41 labels, none duplicated, every `\ref`
resolved, one label never referenced (`sec:discussion`); 32 citation keys, all in `references.bib`, and every
entry cited; the five figures present as PDF and PNG; every row of the 21 tabulars has its specification's
column count; the DOI placeholder `\reportdoi` present; LF line endings. The hard-coded section numbers
(lines 55 to 61; "Section~6" at `sections/study2-results.tex` line 140) are right by count. Fix: none.

**45. Widths and figures.** `holds with this fix`. By estimate at `\footnotesize`, Table 8 (about 525 pt),
Table 16 (about 520 pt) and Table 19 (about 515 pt) are wider than the 459 pt text width, and Tables 10 and
18 are at it; the longest verbatim line (100 characters, about 420 pt) fits. In Figure 3 the
`aggregate-error` markers sit on the axes' edge and are cut, and the caption calls them red where they are
orange. In Figure 4 the tick labels -10^-1 and -10^-2 run together. Table 17 prints "1.055e-09" and Table 19
"1.85e-18" where the other tables use a power of ten. No TeX compiler is on this machine (`pdflatex`,
`xelatex`, `lualatex`, `latexmk`, `tectonic`, `bibtex`), so there is no log. Fix: shorten the variant and
reference columns (or drop them from Table 8, which Table 5 already gives), widen the figure limits, thin the
symlog ticks, use one number style, and read the log for overfull boxes on the first build.

## Verdict

Of 45 verdicts, 17 hold, 26 hold with the stated fix and 2 do not hold. Every number in the abstract, the
Study 2 tables and Section 10 traces to its saved file and column, the sensitivity reproduces byte for byte
from the checkpoints, and the direction of every test agrees with the paired tables; no table entry changes.
The fixes change claims and a few figures in prose. Two sentences are contradicted by the files: "no
comparison favors the substitution", which the abstract, Section 10 and `PAPER-SUMMARY.md` state while the
typical series of E01 favors it (item 15), and the dynamic count's occurrence rule (item 20). The claim is
broader than the evidence for the occurrence test, which ran on npm and the grid only (item 34); the
mechanism trade holds on the mean but not for the typical npm series (item 29); S04 is not a tie (item 16);
the sensitivity was computed before addition 6 was written (item 23); the daily counts are not yet published
(item 30); and the oracle's 17 of 18 includes three exact ties (item 9). The paper may go to the author's
read after the listed fixes, those to the abstract and `PAPER-SUMMARY.md` first (items 15, 16, 29, 34, 42),
since the author reads those. The title holds as written.

## Regeneration

The figures above that are not in the paper come from saved files and this command, run from the repository
root in PowerShell:

```powershell
@'
import json, numpy as np, pandas as pd
from scipy import stats
NR = "reports/study2-npm/run-2026-10-15/"; SR = "reports/study2-synthetic-2026-10-15/"; RT = dict(float_precision="round_trip")
for run in (NR, SR):
    p = pd.read_csv(run + "inference/paired_entities.csv", **RT)
    for i, g in p.groupby("id", sort=False):
        d = g.difference.to_numpy(); nz = d[d != 0]; r = stats.rankdata(abs(nz))
        print(i, "median %.4g lower %d tied %d higher %d rank sum variant-lower %.1f reference-lower %.1f"
              % (np.median(d), (d < 0).sum(), (d == 0).sum(), (d > 0).sum(), r[nz < 0].sum(), r[nz > 0].sum()))
c = pd.read_csv(SR + "inference/secondary_cells.csv", **RT); c = c[c.horizon == 30]
for cid, g in c.groupby("cell_id"):
    o = g[g.model == "oracle"].qscore9.iloc[0]; below = g[g.qscore9 < o].model.tolist(); tied = g[(g.qscore9 == o) & (g.model != "oracle")].model.tolist()
    if below or tied: print(cid, "below the oracle", below, "tied with it", tied)
s = pd.read_csv(NR + "inference/series_scores.csv", **RT)
a = s[(s.horizon == 30) & (s.model == "autoets_weekly")].sort_values("qscore9", ascending=False)
print("autoets h30 mean %.0f; largest %s %.0f, share %.3f" % (a.qscore9.mean(), a.series_id.iloc[0], a.qscore9.iloc[0], a.qscore9.iloc[0] / a.qscore9.sum()))
cols = ["qscore9", "zero", "positive_over", "positive_under"]
for h in (7, 30):
    for m in ("chronos2", "timesfm3", "timesfm2p5"):
        A = s[(s.horizon == h) & (s.model == m + "_hurdle")].set_index("series_id")[cols]
        B = s[(s.horizon == h) & (s.model == m + "_completed")].set_index("series_id")[cols]
        D = A - B.loc[A.index]; X = D.drop("aggregate-error"); t = ((D.zero <= 0) & (D.positive_over <= 0) & (D.positive_under >= 0)).sum()
        print("post-hoc", m, h, "means without aggregate-error", X.mean().round(4).to_dict(), "medians", D.median().round(4).to_dict(), "series with the trade", t)
y = pd.read_csv(SR + "inference/series_scores.csv", **RT); y = y[y.horizon == 30]
for m in ("chronos2", "timesfm3", "timesfm2p5"):
    D = y[y.model == m + "_hurdle"].groupby("replicate")[cols].mean() - y[y.model == m + "_completed"].groupby("replicate")[cols].mean()
    print("post-hoc grid", m, "blocks with the trade", ((D.zero <= 0) & (D.positive_over <= 0) & (D.positive_under >= 0)).sum(), "of 30")
print("sensitivity started", json.load(open(NR + "posthoc/sensitivity.json", encoding="utf-8"))["started_at"])
print("pull", json.load(open(NR + "target-pull/pull.json", encoding="utf-8"))["invocations"][0]["started_at"],
      "first answer", min(e["acquired_at"] for e in json.load(open(NR + "target-pull/completeness.json", encoding="utf-8"))["response_evidence"]))
'@ | .\.venv\Scripts\python.exe -
```

The expansion of item 1 compares `paper/main.tex` with its `\input` lines replaced by the files' contents
(each file's final newline dropped) against `git show f325a67:paper/main.tex`. The sensitivity of item 6 is
`.\.venv\Scripts\python.exe reports\study2-npm\run-2026-10-15\posthoc\sensitivity_zero_days.py
reports\study2-npm\run-2026-10-15 --out <new directory>` with the 209 checkpoints in place. The last-28-day
means of item 8 and the scale of item 10 need the frozen context file, which is not in the tree.

# Review of the three-study paper

Written 2026-10-17 07:00 UTC. A read-only review of the paper under `paper/` as committed in `6220211` (HEAD
`da86452`), by a reader other than its writer, before the author reads the title, the abstract and
`paper/PAPER-SUMMARY.md`. It checks the Study 3 part (Sections 11 to 14, Appendices I and J), the rewritten
discussion and limitations, and what the extension did to the report and to Study 2's tables, against the
record: `PROTOCOL.md` item 7 (the dated addition of 2026-10-16, the file's last 6,470 bytes),
`study/study3/spec.json`, `study/study3/regime_comparisons.json`, `study/study3/nyc311_panel_status.json`,
`RESULTS.md`'s Study 3 section, the run under `reports/study3-nyc311/run-2026-10-17/`, the panel under
`reports/study3-nyc311/panel/`, the two Study 2 runs, the research documents under `docs/research/`,
`docs/ideas/2026-10-16-study3-regime-test.md` and `CONTRIBUTING.md`. Nothing under `paper/` was changed; the
fixes below are instructions for the revision.

Each verdict is `holds`, `holds with this fix` or `does not hold`; `does not hold` is used only where a file
contradicts the text. `S3R` stands for `reports/study3-nyc311/run-2026-10-17`, `S3I` for `S3R/inference`.
Line numbers refer to `paper/paper.tex` unless a file is named; `sections/` is under `paper/`. Sections,
appendices, tables and figures are numbered as `paper/sources.md` gives them and as the expanded source
orders them: Section 14 is Study 3's results, 15 the discussion, 16 the limitations; Table 7 is the Study 2
accounting (`tab:s2parts`), 8 the family's structure, 9 the family (`tab:s3family`), 10 the T2 summary
(`tab:s3t2`), 19 the post-hoc Study 2 strata tests (`tab:s2regime`), 30 to 37 the Study 3 appendix tables
(contexts, panel, directions, Brier pairs, fixed hurdle and fourth cell, pooled rows, accounting parts, PIT);
Figure 4 is the family drawn. Every CSV was read with `float_precision="round_trip"`. Figures quoted below
that are not in the paper come from saved files by the command at the end; where a figure is this review's
own computation and not a registered or declared output, it is labeled post hoc.

## 1. The report and Study 2's tables are unchanged

**1. The report's text.** `holds`. `paper/main.tex` with its `\input` lines replaced by the files' contents
(each file's final newline dropped) is 48,365 bytes against 48,238 for `git show f325a67:paper/main.tex`,
and the two differ in one place only: the dated Study 2 sentence of Section 8, two lines in the report
("As of 2026-10-12, a statement to be re-checked on the posting day, ...") replaced by three ("As of
2026-10-12 no Study 2 target value, forecast or score existed; both components ... Nothing is claimed here
about their outcome."). The same expansion at `5720c05` equals HEAD's, so no shared file changed with the
extension. No `.tex` file under `paper/` holds a carriage return. Fix: none.

**2. Study 1's and Study 2's tables.** `holds`. All 26 tables of the paper at `5720c05` are in the paper at
HEAD with every row between `\midrule` and `\bottomrule` identical (Tables 1 to 7 and 11 to 29); 25 are
identical as whole floats, and Table 27 (`tab:s2dyn`) moved from `sections/study2-results.tex` to
`sections/study2-appendix.tex` with its placement changed from `[t]` to `[h]` and nothing else. The eleven
new tables are Study 3's. Fix: none.

**3. The compressed regime paragraph.** `holds with this fix`. `sections/study2-results.tex` lines 142 to
157 state what Tables 19, 22 and 24 show (81, 60 and 66 sparse series lower at horizon 7; 58, 45 and 54 at
30; dense lower on 32 to 43; 4 to 6 against 21 to 26 grid blocks), but lines 150 to 151 say the post-hoc
within-stratum test "rejects for all three sparse-stratum contrasts at horizon 7 and for none at horizon
30" with no level, for tests that have no adjustment and no registered status; Table 19 gives raw $p$ of
$2.47 \times 10^{-11}$, 0.00158 and $9.01 \times 10^{-5}$ at horizon 7 and 0.47, 0.65 and 0.892 at 30. Fix:
restore the revision's wording, "has raw $p$ below 0.002 for all three sparse-stratum contrasts at horizon 7
and of 0.47 or more at horizon 30".

**4. The compressed dynamic-occurrence paragraph.** `holds`. Lines 238 to 255 of the same file state what
Tables 27 to 29 show: no npm row against the control rejects (adjusted $p$ 0.0787 to 0.838) and one grid row
does (DS09, 0.0439); all nine mean differences against the control are positive; the six horizon-30 rows
against the fixed hurdle reject in the wrapper's favor; four of the five registered rejections against the
substitution are gone. Fix: none.

## 2. Numbers

**5. The checker passes.** `holds`. `.\.venv\Scripts\python.exe paper\check_numbers.py` at HEAD `da86452`
on 2026-10-17 at about 06:30 UTC: "1195 checks, 0 failures, 0 skipped", exit code 0. The 300 checkpoints
are on this machine, so the tie classification was recomputed rather than skipped (item 16). Fix: none.

**6. Table 9, traced independently.** `holds`. From `S3I/paired_entities.csv`, without the project's
inference code: every mean, median and lower / tied / higher count equals `S3I/inference.csv` exactly; the
two-sided signed-rank $p$, computed here from the rank sums with average ranks, zero differences omitted, a
normal approximation with the tie correction and no continuity correction, equals SciPy's and the saved
value to $10^{-9}$ relative in all 36 rows; a separate Benjamini-Hochberg over the 36 reproduces
`wilcoxon_p_bh` and the 21 rejections; each row's bootstrap seed, recomputed as the SHA-256 of the canonical
JSON of the root 20261004, `study3` and the row's keys, equals the saved one, and the 20,000-replicate
intervals redrawn from it agree to $2.2 \times 10^{-16}$. Every printed cell of the 36 rows is the
recomputed value rounded to the digits printed. Fix: none.

**7. Table 10 and the T2 paragraph's figures.** `holds`. Dense: six rejections, 72 to 87 lower, medians
-0.05608 to -0.06753. Sparse: R16, R18, R20, R22 and R24 reject, 53 to 58 lower, medians -0.001852 to
-0.002646; R14's median is 0 with adjusted $p$ 0.1376. Very sparse: R28, R32 and R36 with 22 / 77 / 1 and
rank sums 253 against 23; R26, R30 and R34 at 0.1376, 0.2345 and 0.1376. What the T2 rows are read to mean
is items 13, 14 and 32. Fix: none.

**8. Figure 4.** `holds with this fix`. Redrawn from `S3I/inference.csv` by the figure script's own
function into a scratch folder, the PNG is byte-identical to `paper/figures/fig-s3-nyc311-family.png` (the
PDF has the same length and differs only in its embedded metadata); the filled markers are the 21 rejecting
rows, and the very sparse panel shows R28, R32 and R36 filled and R26, R30 and R34 open. The caption
(`sections/study3-results.tex` lines 85 to 86) says "In the T1 panels the shaded half is the sign H3
predicts", but the three panels are strata, each holding T1 and T2 points, and the shading is drawn across
the whole panel. Fix: "In each stratum's panel the shaded half is the sign H3 predicts for its T1 tests
(blue); H3 predicts nothing for T2 (orange)."

**9. The rest of Section 14.** `holds`. Recomputed from `S3I/series_scores.csv` (not from the summary CSVs),
278 checks, 0 failures: the run's 939 and 956 seconds, budget 3,600, estimate 1,080, 39,600 forecasts and
0 disagreements (`S3R/run.json`, `S3R/results-provenance.json`, `S3R/integrity/integrity.json`, whose
largest residuals are 0.0, $7.1 \times 10^{-15}$ and $2.8 \times 10^{-16}$); the dense ranges (55 to 72
higher, medians 0.004074 to 0.0127, means 0.01511 to 0.02219, control means 1.703 to 1.833, ties 0 to 2);
the Brier ranges (dense 0.00668 to 0.009347 with every interval above zero; very sparse lower on 68 to 82 of
100, medians -0.002363 to -0.001625, raw $p$ at most 0.00165, means within 0.0013 of zero); the fixed hurdle
(dense higher on 60 to 70; sparse higher on 45 to 60; very sparse 20 to 23 higher, 5 to 9 lower, 69 to 73
tied, raw $p$ 0.00293 to 0.0254); the fourth cell (dense 0.2944 to 0.325 and higher on 70 to 91; elsewhere
at most 0.0032 from the control, 29 to 98 tied; against `hurdle_count_28` on dense series lower by 0.03591
to 0.0467 on the mean and on 62 to 73 of 100); the pooled rows (every direction as stated; the largest
within-table adjusted $p$ is 0.0046). Fix: none.

**10. Appendix Tables 30 to 37 and the panel's figures.** `holds`. Tables 32 to 37 were recomputed row by
row from `S3I/paired_entities.csv`, `S3I/series_scores.csv` and `S3I/pit_histograms.csv` (9,000 values per
PIT row), the accounting parts also against `S3I/secondary_accounting.csv`. Table 31 and the panel section
from `reports/study3-nyc311/panel/selection.json`: 2,002, 2,422 and 4,045 eligible cells by stratum, the
stratum labels agreeing with the zero fractions, the manifest's 300 equal to the first 100 per stratum in
selection-hash order, 39 very sparse series with a zero fraction of one and 19 with an all-zero context
(`nyc311_panel_status.json`). Table 30 is not recomputable from the tree; from the target signals on this
machine, whose SHA-256 equals `results-provenance.json` `pull.signals`, all nine rows reproduce, and in every
one of the 1,434 windows that fall back (fewer than two request days in the last 28) `hurdle_dynamic`'s
deciles and score equal the fixed hurdle's, as the design says. The census figures (2,959,469 and
2,902,433; 49,356 and 7,680; 6,216 requests on 2025-12-25 and 22,805 on 2026-02-24; 983,482 and 947,751;
18,660 and 17,071; 8,849 frame requests on 2026-08-16) equal `census.json` and
`S3R/target-pull/completeness.json`. Fix: none.

**11. The abstract's and the discussion's figures.** `holds`. "About one percent" is 0.88 to 1.22 percent
of the control's mean; one of twelve, ten of twelve, 72 to 88, 68 to 82, 14 of 18, the four non-rejecting T2
rows with zero medians, 0.009693 to 0.03213, 0.2944 to 0.325, 62 to 73, and 128 to 161 against 124 to 157
(`S3I/secondary_pooled_study2_form.csv`) all trace; the Study 1 and Study 2 figures of the abstract (46 to
89; two of six and three of three; 81, 60 and 66 and 32 to 43, Table 22) are in unchanged tables and
asserted by the checker. What the sentences infer from these figures is Section 5 below. Fix: none.

## 3. Directions and ties

**12. Directions.** `holds`. Every rejecting T1 row has the median sign and the rank-sum side H3 predicts
(six dense positive, R21 negative), no T1 median has the opposite sign, the eleven rejecting T2 rows with a
nonzero median are negative, and the side each row's larger rank sum favors equals Table 32 in all 36. Ten
T1 medians are exactly zero (R13, R15, R17, R19 and the six very sparse rows) and are reported as having no
sign everywhere in the paper. Fix: none.

**13. A median of exactly zero in the T2 count.** `holds with this fix`. Seven T2 medians are exactly zero
(R14, R26, R28, R30, R32, R34, R36), and three of them reject: R28, R32 and R36. The registered rule reads the
direction from the median (`regime_comparisons.json` `direction`; the addition's "with the direction read
from the median"), so those three have no sign; their counts (22 lower, 1 higher) and rank sums (253
against 23) lean to `hurdle_dynamic`. The T2 paragraph says so (`sections/study3-results.tex` lines 135 to
138), but the count of fourteen is stated without it at line 18 ("fourteen are T2 tests, all for
\emph{hurdle\_dynamic}"), lines 130 to 131 ("lower ... wherever a T2 test rejects"), line 181, the abstract
(line 49), the discussion (line 125) and `PAPER-SUMMARY.md` lines 35 and 76; the caption of Table 10 (lines
146 to 147) says "their direction is read from the rank sums". Fix: wherever 14 of 18 appears, add "three of
them with a median of exactly zero, leaning to the dynamic hurdle by rank sum", and in Table 10's caption
say that the three have no sign under the registered rule and lean to the dynamic hurdle by rank sum (the
abstract's version is in item 34).

**14. "The four rows whose medians are exactly zero".** `does not hold`. `sections/study3-results.tex` lines
139 to 141 and `PAPER-SUMMARY.md` lines 198 to 201: the T2 reading holds "except in the four rows whose
medians are exactly zero", but seven T2 medians are exactly zero (`S3I/inference.csv` `median_diff`); the
four meant are the four that do not reject. Fix: "except in the four rows that do not reject, R14, R26, R30
and R34, whose medians are exactly zero; three rows that reject, R28, R32 and R36, also have medians of
exactly zero".

**15. The direction rule in the limitations.** `does not hold`. Lines 255 to 258: "The direction is read
from the rank sums, as registered." The addition and `regime_comparisons.json` say the direction is read
from the median and reported beside the mean; the rank-sum reading is the paper's and the run's table
script's (`S3R/RESULTS-nyc311.md` lines 66 to 68 and 160 to 161), which the registration does not name.
Fix: "The registered direction is the median's sign, and a median of exactly zero has none; the paper
reports beside it the side the rank sums favor, a reading the registration does not make."

**16. The 71 to 87 tied very sparse series.** `holds with this fix`. Recomputed from the 300 checkpoints on
this machine, each of whose SHA-256 equals its value in `S3R/run.json` `completed`: the tied series with
every decile at zero under both forecasts in every window number 87, 82, 81, 71, 87 and 85 in R25, R27, R29,
R31, R33 and R35, and every such series is tied; the control is all zero in every window for 91, 86, 81, 71,
95 and 89 of the 100, `hurdle_dynamic` for 89 in every row; in the sparse rows 4, 3, 2, 2, 5 and 5 of the
tied series. `paper/sources.md` names the checkpoints as the source and the checker recomputes the counts
when they are present, but the paper (`sections/study3-results.tex` lines 119 to 123, lines 248 to 250)
gives no provenance; the checkpoints are not in the tree, no committed file holds the counts, and they were
counted after the run and are not a declared output. `PAPER-SUMMARY.md` lines 75 to 76 (and the index row
of the results page) say 72 to 88 tie "because both forecasts put every decile at zero"; 1 to 3 of the tied
series in each row tie with integer deciles that are not all zero. Fix: add "counted after the run from the
saved deciles of the checkpoints, which are to be released (Section 18); descriptive" where the paper gives
the counts, and say "mostly because" in the summary.

**17. The sparse ties.** `holds`. In the four sparse rows with a zero median the ties number 12 to 23, the
split around them is close to even (46 / 41, 44 / 44, 45 / 32, 35 / 45), and 2 to 5 of the tied series are
all zero; the text's "the rest tie with integer deciles that are not all zero" is right. Fix: none.

## 4. Claims against the registration

**18. H3.** `holds`. `sections/study3-question.tex` lines 14 to 18 state H3 in the addition's words, with
"each stratum is tested on its own; nothing is pooled across strata for confirmation". Fix: none.

**19. The family and its one adjustment.** `holds`. R01 to R36 in `regime_comparisons.json`'s order
(stratum, model, horizon, contrast), all 36 available, one Benjamini-Hochberg at $q = 0.05$, the zero rule
"wilcox" with $p = 1$ when all are zero; Table 8 equals the file. Fix: none.

**20. The fewer-than-ten rule.** `holds with this fix`. `sections/study3-design.tex` lines 50 to 51 state the
rule without its registered last clause, "the BH correction then covers the available tests"
(`regime_comparisons.json` `adjustment_scope`). Fix: add the clause.

**21. The source-gap rule and the fallback.** `holds`. Stated as registered (`sections/study3-design.tex`
lines 20 to 24, `sections/study3-detail.tex` lines 47 to 54); no day was a gap (fewest frame requests 8,849)
and PyPI was not invoked. Fix: none.

**22. Secondary labels.** `holds with this fix`. The fixed hurdle, the fourth cell and the pooled rows are
labeled secondary and "confirm nothing" (`sections/study3-results.tex` lines 160 to 175), and the Brier score
"declared secondary" wherever it is read. The three-part accounting and the PIT are declared secondary by the
addition but are not labeled where the results read the accounting (line 98), in Table 36's caption and
paragraph (`sections/study3-appendix.tex` lines 278 to 290) or in Table 37's (lines 318 to 328). The fourth
cell is read in the discussion as closing a question (item 31). Fix: label the accounting and the PIT
"declared secondary" in those three places.

**23. The selection and the all-zero series.** `holds`. The selection is as registered and reproduces (item
10); the 39 and 19 very sparse series with no request in the stratum window and the context are counted and
stated in Section 13 and Table 31, and the fallback's 74 and 4 at the first origin in Section 13. Fix: none.

**24. The gate, the smoke and the approvals.** `holds`. As `S3R/results-provenance.json` records them: the
smoke at 01:56:50 UTC, the readiness approved at 03:12:50 with a budget of 3,600 seconds against 1,080, the
gate at 03:15:43, 03:44:13 and 03:46:46 UTC, the pull from 03:16:23 to 03:32:12 (100 attempts, 84 days)
and 03:45:06 to 03:45:43 (6 attempts), the run from 03:47:23 to 04:03:01 (938.7 seconds; 955.7 for the
process), the inference and integrity times; the three approvals are quoted word for word, and the context
pull's ("approved: NYC 311 context pull, 330 request attempts and 3 hours") equals
`nyc311_panel_status.json`. Fix: none.

**25. The contamination ledger.** `holds`. The three categories in Section 13 and in the last limitation
equal `S3R/RESULTS-nyc311.md` lines 94 to 103. Fix: none.

**26. The terms.** `holds with this fix`. The paper states the terms as
`reports/study3-nyc311/panel/source-terms.md` records them and makes no claim about the Open Data Law's
text: it says the program's page names the law as its basis and that the law was not read. One phrase is
broader than the record: `sections/study3-panel.tex` line 36, the terms "imply no endorsement", where they
say that links to other sites imply no endorsement by the City. Fix: "and state that links to other sites
imply no endorsement"; optionally carry the record's caution that these pages do not settle whether the
intellectual-property clause reaches the datasets.

## 5. The discussion's inferences

**27. "The dense half ... is confirmatory on two domains".** `does not hold`. Lines 119 to 123 (also line 65
and `PAPER-SUMMARY.md` lines 113 to 115 and 189 to 194): "this is confirmatory on two domains: on npm and the
grid through the pooled families, which the dense series decide, and on NYC 311 through the dense stratum's
own six tests". On NYC 311 the six dense T1 tests (R01, R03, R05, R07, R09, R11) are a registered
per-stratum test of the dynamic occurrence, and all reject as predicted. On npm no dense test is registered:
the confirmatory tests are the six hurdle-against-control tests pooled over 209 series, with the fixed
Jeffreys occurrence; two reject against the hurdle (E10, E16), four do not, and three medians are negative,
the hurdle lower on 121, 105 and 109 of 209 (E01, E04, E13; `reports/study2-npm/run-2026-10-15/inference/inference.csv`).
Reading them as the dense answer rests on the declared secondary strata (dense lower on 32 to 43 of 100), the
pooling that Section 11 (lines 27 to 29, item W1) says a confirmatory answer should not rely on; the grid is
synthetic, not a domain; and the dynamic occurrence on npm is post-hoc only (Table 27, no row against the
control rejects). Fix: "This is confirmatory on NYC 311, through the dense stratum's own six tests of the
dynamic occurrence; on npm and the grid the confirmatory families are pooled, none favors the fixed
substitution and two of six npm tests and all three grid tests reject against it, and their reading as the
dense answer rests on the declared secondary strata", with line 65 saying "confirmed for dense series on NYC
311".

**28. The sparse half and the two readings "with equal weight".** `does not hold`. Lines 111 to 124 (also
`PAPER-SUMMARY.md` lines 115 to 117 and 137 to 138) give two readings, a smaller benefit or a score that
cannot see it on all-zero forecasts, cite the ties and the Brier counts for the second only, and say
"Nothing in the record chooses between the two." By stratum the record does choose:
- The sparse stratum, $[0.5, 0.9)$, is the one npm's 81, 60 and 66 came from. There the score separates the
  two forecasts on 77 to 92 of 100 series (ties 8 to 23, of which 2 to 5 all zero), so the second reading
  covers few of them. The npm-form fixed hurdle, a declared secondary, is lower than the control on 41, 39
  and 43 of 100 at horizon 7 (Table 34; on npm 81, 60 and 66, with 1 to 3 ties, Table 19) and on 26 to 44 at
  both horizons; the dynamic one on 35 to 57. The secondary Brier score is mixed: lower for the dynamic
  occurrence in R21 (60 of 100, raw $p$ 0.0259), higher in R19 with its interval above zero, even in R15 and
  R23. The record favors the first reading here, or a reading the paper does not state: that the benefit
  belongs to npm's sparse series and not to the regime.
- The very sparse stratum, which npm could not test with its nine series, is where the second reading
  applies: 72 to 88 of 100 tie and 71 to 87 are all zero under both forecasts. The Brier score favors the
  dynamic occurrence on 68 to 82 of 100 with medians of about -0.002, but its means are within 0.0013 of zero
  and one is positive (R29); the \qs{} means are positive in all six rows, against H3, and three turn
  negative without `Sewer Maintenance` in `09 QUEENS` (R27 -0.0006784, R31 -0.0002694, R35 -0.0007258); at
  horizon 7 the few untied series lean to the control (R25 2 lower and 10 higher, raw $p$ 0.0342; R33 3 and
  10, 0.0463). The two readings are not exclusive here: a small occurrence benefit that the score cannot see
  fits both.
Fix: replace the two-readings passage with the stratum-by-stratum account above, in two sentences: on the
sparse stratum the score sees the substitution, the npm-form hurdle is lower on 39 to 43 of 100 at horizon 7
against 60 to 81 on npm and the dynamic one on 45 to 57, so the npm reading did not reproduce, whether
because the benefit is smaller or because it belongs to npm; on the very sparse stratum the score ties where
the Brier score shows a small benefit on the typical series and none on the mean, so a small invisible
benefit and none are both consistent with the record.

**29. "Study 3 bears on the first and not on the second."** `holds with this fix`. Lines 135 to 149. Two
comparisons support the first reading, that the context-only occurrence is the worse occurrence forecast,
on NYC 311's dense series: the Brier score, which does not involve the positive law, is worse for the dynamic
occurrence in all six T1 rows with every interval above zero; and the fourth cell against `hurdle_count_28`,
which differ in the occurrence alone under a count positive law, puts the model's own occurrence ahead of the
Jeffreys estimate (lower by 0.03591 to 0.0467 on the mean, on 62 to 73 of 100) where no truncated law can
count zeros twice. Read as a factorial (declared secondary), the Jeffreys occurrence costs 0.02145 to 0.02487
on the mean with the model's positive law (fixed hurdle against control) and 0.03591 to 0.0467 with the
count law, so the harm is not specific to the truncated law that the second reading needs, though the two
positive laws score on different levels. Two sentences go further than this: items 30 and 31. A third, "On
that domain the substitution loses on dense series because the context estimate is the worse occurrence
forecast" (lines 143 to 145), states a cause the record shows only as consistent. The second reading's
status on npm is stated correctly: both readings remain consistent with every Study 2 number and Study 3
does not test it there; but "since the fourth cell was run on NYC 311 alone" implies the cell alone would,
where it is the factorial contrast, and the cell is computable post hoc from npm's and the grid's saved laws
(`docs/research/2026-10-16-standing-and-referee-read.md`, its table of computable analyses). The premise
sentence (lines 147 to 149) holds: on npm at horizon 30 the completed laws' Brier scores are 0.1817, 0.179
and 0.1795 against 0.1785 for the Jeffreys estimate, on the grid 0.1329, 0.1299 and 0.1366 against 0.1325.
Fix: write "is consistent with the context estimate being the worse occurrence forecast there", and "Study 3
does not test the second reading on npm, where the fourth factorial cell was not computed".

**30. The accounting sentence.** `does not hold`. Lines 137 to 139: "the accounting puts the loss on the
zero days, 0.009693 to 0.03213 in every row, with no trade against positive days to explain"; the same
reading is in `sections/study3-results.tex` lines 98 to 101 and `PAPER-SUMMARY.md` line 96. Table 36: the
zero-day part is against the dynamic occurrence in all six dense rows, but for Chronos-2 the positive-day
parts give back 0.0108 and 0.0170 of it (a trade, opposite in sign to npm's), and for the two TimesFM models
the positive-day underprediction part also loses, 0.0187 and 0.01405 at horizon 7, more than their zero-day
parts of 0.009693 and 0.01036, and 0.009417 and 0.005593 at horizon 30. Fix: "the zero-day part is against
the dynamic occurrence in every row, 0.009693 to 0.03213; for Chronos-2 the positive days give part of it
back, and for the two TimesFM models the positive-day underprediction part adds 0.005593 to 0.0187, more
than the zero-day part at horizon 7".

**31. "The fourth cell ... closes the question the second reading left open".** `does not hold`. Lines 139
to 143 say the fourth cell "closes the question the second reading left open, in the direction the
accounting predicted", two sentences after "Study 3 bears on the first and not on the second". The fourth
cell against the control differs in the positive law alone and measures the model's law against a shifted
Poisson, the comparator the paper calls one that cannot win on dense series (lines 152 to 154); it says
nothing about whether $G_+$ sits low on positive days, and "the direction the accounting predicted" names no
prediction. "So the model's value there sits in its positive law" holds only against that comparator. Fix:
delete the clause and say what the cell separates: "against the control, which differs from it in the
positive law alone, it is far worse, by 0.2944 to 0.325 on the mean, a measure of the model's positive law
against a shifted Poisson; against \hc{}, which differs from it in the occurrence alone, the model's own
occurrence is the better one".

**32. "The model's positive law keeps its value against a count law" on NYC 311.** `does not hold` beyond
the dense stratum. Lines 124 to 126 and 164 to 167, `sections/study3-results.tex` lines 138 to 141 and 181,
`sections/study3-question.tex` lines 33 to 36. The registered T2 changes two things at once: the occurrence
(`hurdle_empirical_28` carries the Jeffreys estimate; its Brier score equals the fixed hurdle's on every
series) and the positive law. The declared secondary that holds the occurrence fixed, the fixed hurdle
against `hurdle_empirical_28` (`S3I/secondary_strata_contrasts.csv`), puts the dense advantage on the
positive law (lower on 75 to 88 of 100, means -0.2052 to -0.2129, raw $p$ at most $1.53 \times 10^{-8}$),
but on the sparse series it is mixed (26 to 38 lower, 20 to 47 higher, every median zero; Chronos-2 higher
more often than lower, TimesFM 2.5 at horizon 30 lower on 38 against 20, raw $p$ 0.0276) and on the very
sparse series it ties on 96 to 99 of 100. By difference (post hoc, this review's descriptive computation
from the same scores), the occurrence part of every sparse T2 difference is at least as large on the mean as
the positive-law part and favors `hurdle_dynamic` on more series (lower than the fixed hurdle on 51 to 62 of
100, against 26 to 38 for the positive law), and R28, R32 and R36 come from the occurrence alone: the
occurrence-only difference has the same 22 / 77 / 1 and the same rank sums. Fix: "The model's positive law
keeps its value against a count law on NYC 311's dense series: with the occurrence held at the Jeffreys
estimate, the fixed hurdle is lower than the empirical hurdle on 75 to 88 of 100 (declared secondary). The
registered T2 also changes the occurrence; on sparse series its rejections owe at least as much to the
dynamic occurrence as to the positive law, and on very sparse series they owe everything to it", and the
same restriction in Sections 11 and 14.

**33. The raw contrast pooled on NYC 311.** `holds with this fix`. Lines 173 to 175: the means and the
split (128 to 161 lower, 124 to 157 higher) equal `S3I/secondary_pooled_study2_form.csv` P03 to P18; but
the paragraph, and `sections/study3-results.tex` line 174 ("every row's within-table adjusted $p$ is below
0.005"), leave out the test's direction: in all six raw rows the larger rank sum is the model's (24,324 to
29,482 against 11,273 to 17,366; within-table adjusted $p$ 0.0046 or less), so the pooled typical series on
NYC 311 sides with the models on the rank test, as on four of six npm rows and against Study 1. Fix: add "and
the signed-rank test, adjusted within the table, favors the models in all six" in both places, labeled
secondary.

**34. The abstract's "most very sparse series".** `holds with this fix`. Lines 47 to 49: 71 to 87 of 100 is
most, but the clause is attached to "ten of twelve medians are exactly zero", four of which are sparse
medians whose zeros come from a block of 12 to 23 ties straddling a near-even split, not from all-zero
deciles. Fix, at 299 words in all: "Study 3 registers that reading as 36 per-stratum tests on 300 NYC 311
service-request series in three strata, with a dynamic occurrence. ... and ten of twelve medians are exactly
zero; on most very sparse series both forecasts put every decile at zero. The dynamic hurdle beats the
empirical count hurdle in 14 of 18 tests, three with zero medians."

## 6. The claim's scope

**35. The three settings.** `holds`. The claim is the registered combination on GitHub stars (through the
raw comparison only), npm downloads with the grid, and NYC 311 requests stratum by stratum, and nothing
broader: the abstract (line 50), Section 11 (lines 43 to 45), the discussion (lines 181 to 197) and the
limitation (lines 264 to 265). No sentence claims to be first; lines 188 to 193 disclaim it with the
literature cited, and lines 60 to 62 speak of what was found in the literature, not of the claim. Fix: none.

**36. Attribution.** `holds with this fix`. The ties are attributed to the score, and the checkpoints bear
that out (item 16); the npm results are not attributed beyond the accounting. Two sentences attribute more
than the accounting shows: the dense loss "on the zero days" (item 30) and "because the context estimate is
the worse occurrence forecast" (item 29). Fix: as in items 29 and 30.

**37. Both summaries.** `holds with this fix`. Section 14 gives the mean beside the median in every stratum.
The discussion's sparse half (lines 111 to 118) gives tests, medians and ties but not the very sparse means,
which are positive in all six rows (0.0005086 to 0.002911, against H3) and carried by one series. Fix: add
them, with the series, to the discussion; whether the abstract, at 299 words, carries them is the author's
choice.

**38. Post-hoc labels.** `holds with this fix`. Two readings computed after the run are not labeled: the
classification of the ties by all-zero deciles (item 16) and the side of the rank sums for a zero median
(items 13 and 15). Fix: label the first "counted after the run, descriptive" and the second "a reading beside
the registered median rule".

## 7. Writing, length and the boundary

**39. Writing.** `holds with this fix`. The Study 3 sections and the discussion are plain and specific, with
no marketing language. Three things repeat: the mechanics of the ties (Section 14, 132 words; the limitation,
155; the discussion), the scope sentence (four places), and the terms (Section 13, the limitation,
Appendix I). `sections/study3-question.tex` lines 36 to 37 say what Study 3 does not answer "is fixed by the
same registration", but the addition names no Markov occurrence and no overdispersed cell; those follow from
what it covers. Fix: keep each repeated passage once (item 42 counts the words) and write "follows from what
the registration covers".

**40. The boundary and the author's statement.** `holds`. `paper/shared/author-statement.tex` quotes the
README section "How this project was built" word for word (markup aside), and nothing else in the paper or
`PAPER-SUMMARY.md` speaks of how the work was done. Fix: none.

**41. The abstract.** `holds`. 299 words, identical in `PAPER-SUMMARY.md` once `$q = 0.05$` is read as
text. Fix: none.

**42. The length.** `holds with this fix`. By the revision's method (running text with tables, figures and
comments removed, over the expanded document before `\appendix`, captions counted apart) this count gives
the body 15,654 words and 966 words of captions, ten tables and four figures (`PAPER-SUMMARY.md` gives 15,815
and 970; the difference is in what is counted as a word), and the appendix 8,321 words, 1,490 of captions,
27 tables and two figures. At the rate the summary states, about 900 words a page and half a page a float,
that is about 24.5 pages before the references, not "about 23" (`PAPER-SUMMARY.md` line 153; also
`docs/STATE.md`), which is the figure at 1,000 words a page. The report's Sections 1 to 6 (2,855 words, four
tables, two figures) and the registered families (Tables 5, 6 and 9) stay; the cuts and moves below remove
no registered number from the body, in order of what each costs the reader:
1. Drop Table 10: every number in it is in Table 9 and the T2 paragraph, and it is the widest table (item
   45). One float, 44 words of caption.
2. Move Table 8 to Appendix I; Table 9's ID column gives the order. One float.
3. Move the Study 2 design section to Appendix E, leaving its family paragraph: about 835 of 1,092 words.
4. Move Study 3's domain and calendar paragraphs (206 and 184 words) to Appendix I, leaving two sentences:
   about 330.
5. Move Study 3's target-pull and terms paragraphs (157 and 171) to Appendix I, which already holds their
   detail, leaving a sentence each: about 290.
6. Move the two Study 2 post-hoc paragraphs (222 and 264) to Appendix H with a sentence each, and fold the
   three-zero-days paragraph (185) into its limitation item: about 550.
7. Move the Study 3 secondary paragraph (297) to Appendix J, leaving one sentence on the fourth cell: about
   250.
8. Move the Study 2 and Study 3 reproducibility paragraphs (204 and 167) to Appendices G and J with a
   sentence: about 300.
9. Shorten the Study 2 literature paragraphs (352 and 151) to about 120 words with every citation kept: about
   380.
10. Keep the tie mechanics once, in the limitation: about 130.
11. Shorten Section 11's second paragraph (305) to the four changes in a sentence each: about 150.
12. Halve the Study 2 and Study 3 limitation items that repeat the body (585 and 447 words; the report's 461
    stay): about 500.
13. Shorten the discussion's positive-law paragraph (328), which repeats Section 10: about 150.
14. Move Figure 3 and Table 7 to Appendix H, the discussion citing them there: two floats.
After 1 and 2 the estimate is about 23.4 pages; after 3 to 13 (about 3,865 words) about 19; after 14 about 18.
Fourteen pages at this rate would need the body near 8,100 words with ten floats, a further 3,700 words that
can come only from the Study 2 and Study 3 results prose and the discussion, or from moving Table 9 with
Figure 4 kept in the body, which removes the registered numbers from it. Fix: correct "about 23 pages" and
put the list before the author.

## 8. LaTeX

**43. Static checks.** `holds`. `paper.tex` reads 27 files, all present, none twice, and every `.tex` file
under `paper/sections/` and `paper/shared/` is read; braces balance and environments close in every file;
64 labels, unique, all 134 references resolve and every label is referenced; 41 citation keys, all in
`references.bib`, and every entry cited; the six figure PDFs are present and tracked; every row of every
tabular has its specification's column count; the seven packages cover every command used; the DOI
placeholder `\reportdoi` is defined and used in `\date`; the section numbers written in lines 55 to 61 are
right by count (19 sections; Appendices A to J). Fix: none.

**44. Table 9's width.** `holds with this fix`. No TeX compiler is on this machine (`pdflatex`, `xelatex`,
`lualatex`, `latexmk`, `tectonic`, `pandoc`), so the widths are estimates, measured with the Computer Modern
metrics (`cmr10`, `cmtt10`) at each table's size, within about 5 percent. Table 9's fourteen columns at
`\scriptsize` with `\tabcolsep` 2.4 pt are about 610 pt wide against a 461 pt text width (132 percent): it
cannot fit as set. The headers drive much of it ("Sign as predicted", "Lower / tied / higher", "Reference
mean", "Mean difference" each wider than their cells). Fix: drop the Stratum and Contrast columns for a
spanning row per stratum and "T1"/"T2" in the ID cell, and set the long headers on two lines (about 445 to
470 pt), or set the table on a landscape page with `rotating`'s `sidewaystable`.

**45. The other widths.** `holds with this fix`. By the same estimate Table 10 is about 689 pt (150
percent), and in the appendix Table 35 is 137 percent, Table 30 110, Table 33 109, Table 34 107, and Tables
31, 36 and 37 about 104; Table 19 (`tab:s2regime`), unchanged since `5720c05`, is about 119. Fix: drop Table
10 (item 42), give Table 35 a model column with short variant names, shorten the headers of Tables 30 and 31,
set Tables 33, 34, 36 and 37 at `\tabcolsep` 2.4 pt or `\scriptsize`, and read the log's overfull boxes on the
first build.

## What could not be verified

- The page count and every width: no compiler or pandoc is on this machine, so there is no PDF and no log.
- The 71 to 87 figure and Table 30 rest on files that are not in the tree, the 300 checkpoints and the target
  signals; they reproduce from the copies on this machine, whose hashes equal the run's records, and cannot
  be checked from a fresh clone until the checkpoints are released.
- The terms pages were not re-opened; the review compares the paper with `source-terms.md` as recorded. The
  Open Data Law was not read.
- The fourth cell on npm and the grid is not computed anywhere; whether the second reading of the accounting
  trade operates there is open.

## Verdict

Of 45 verdicts, 21 hold, 17 hold with the stated fix and 7 do not hold. Every number in the abstract, Table
9, Table 10, Figure 4, Section 14, the Study 3 appendix and the discussion traces to its file and column; the
36 tests, their directions, ties, rank sums and raw and adjusted $p$ reproduce from the paired table by an
independent computation; the 71 to 87 figure reproduces from the checkpoints; the report's text and every
Study 1 and Study 2 table are unchanged. No table entry is wrong. The fixes change claims. Seven sentences
are contradicted by the files: the dense half "confirmatory on two domains", where npm has no dense test and
its pooled tests are mixed (item 27); "nothing in the record chooses" between the two sparse readings, where
the sparse stratum's ties and the npm-form hurdle's counts do (item 28); the dense loss "on the zero days ...
with no trade", wrong for the two TimesFM models (item 30); the fourth cell "closes the question" of the
second reading, against the paragraph's own "not on the second" (item 31); the positive law's value "in 14 of
18", which the shared-occurrence comparison supports on dense series only (item 32); "the four rows whose
medians are exactly zero", of seven (item 14); and the direction "read from the rank sums, as registered",
where the registration reads it from the median (item 15). The paper may go to the author's read after the
listed fixes, those to the abstract and `PAPER-SUMMARY.md` first (items 13, 14, 16, 27, 28, 30, 32, 34, 42),
since the author reads those. The title holds as written.

## Regeneration

The figures above that are not in the paper come from the committed inference files and this command, run
from the repository root in PowerShell:

```powershell
@'
import numpy as np, pandas as pd
from scipy import stats
S = "reports/study3-nyc311/run-2026-10-17/inference/"; RT = dict(float_precision="round_trip")
ss = pd.read_csv(S + "series_scores.csv", **RT); pe = pd.read_csv(S + "paired_entities.csv", **RT)
def pair(st, v, r, h):
    x = ss[(ss.horizon == h) & ((ss.stratum == st) if st != "all" else True)]
    a = x[x.model == v].set_index("series_id"); b = x[x.model == r].set_index("series_id").loc[a.index]
    return a, b
def line(d):
    nz = d[d != 0]; rk = stats.rankdata(abs(nz)) if len(nz) else np.array([])
    p = stats.wilcoxon(nz, method="approx").pvalue if len(nz) else 1.0
    return "mean %.4g median %.4g lower/tied/higher %d/%d/%d rank sums %.1f/%.1f raw p %.3g" % (
        d.mean(), np.median(d), (d < 0).sum(), (d == 0).sum(), (d > 0).sum(), rk[nz < 0].sum(), rk[nz > 0].sum(), p)
M = ("chronos2", "timesfm3", "timesfm2p5")
for st in ("dense", "sparse", "very_sparse"):
    for m in M:
        for h in (7, 30):
            a, b = pair(st, m + "_hurdle_dynamic", m + "_completed", h)
            d = a[["zero", "positive_over", "positive_under"]] - b[["zero", "positive_over", "positive_under"]]
            print("T1 parts", st, m, h, d.mean().round(6).to_dict())
            a, b = pair(st, m + "_hurdle_dynamic", m + "_hurdle", h); print("T2 occurrence part", st, m, h, line((a.qscore9 - b.qscore9).to_numpy()))
            a, b = pair(st, m + "_hurdle", "hurdle_empirical_28", h); print("T2 positive-law part", st, m, h, line((a.qscore9 - b.qscore9).to_numpy()))
            a, b = pair(st, m + "_hurdle", m + "_completed", h); print("fixed hurdle vs control", st, m, h, line((a.qscore9 - b.qscore9).to_numpy()))
            a, b = pair(st, m + "_occurrence_model_size_count", "hurdle_count_28", h); print("fourth cell vs hurdle_count_28", st, m, h, line((a.qscore9 - b.qscore9).to_numpy()))
for m in M:
    for h in (7, 30):
        a, b = pair("all", m + "_raw", "local_mean_28", h); print("pooled raw vs local_mean_28", m, h, line((a.qscore9 - b.qscore9).to_numpy()))
for i in ("R25", "R27", "R29", "R31", "R33", "R35"):
    g = pe[pe.id == i].set_index("series_id").difference
    print(i, "mean %.4g; without the most influential series %.4g" % (g.mean(), g.drop('["Sewer Maintenance","09 QUEENS"]').mean()))
'@ | .\.venv\Scripts\python.exe -
```

The expansion of item 1 compares `paper/main.tex`, with its `\input` lines replaced by the files' contents
(each file's final newline dropped), against `git show f325a67:paper/main.tex`, and the tables of item 2 the
rows between `\midrule` and `\bottomrule` of each labeled table in the expanded `paper.tex` at `5720c05` and
at HEAD. The tie classification of item 16 reads `rows[].forecast.deciles` from the 300 checkpoints by series,
variant, horizon and cutoff, and Table 30 of item 10 needs the target signals; neither is in the tree. The
widths of items 44 and 45 sum, per column, the widest cell measured with `matplotlib`'s `cmr10` and `cmtt10`
at the table's size, plus twice `\tabcolsep` per column.

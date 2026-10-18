# Sources of every number in the report

Every number in `paper/main.tex` and `paper/SUMMARY.md`, the file it comes from, the row and column or key,
and the command that regenerates that file. Paths are relative to the repository root; `R` stands for
`reports/registered-2026-09-13`. `paper/check_numbers.py` loads these files and asserts each figure in the
form the report prints it. Version 1 numbers are quoted from the preserved documents in the local, gitignored
`v1_reference/` folder and were not recomputed.

Tables are named by their LaTeX label and their compiled number, in source order (the article class numbers
appendix tables in the same sequence): Table 1 the panel (`tab:panel`), Tables 2 and 3 the comparisons
against `local_mean_28` and `autoets_weekly` (`tab:lm`, `tab:ae`), Table 4 the post-hoc parts
(`tab:posthoc`); in the appendix, Table 5 version 1 (`tab:v1`), Table 6 AutoETS (`tab:autoets`), Table 7
pooled QScore9 by stratum (`tab:stratum`), Table 8 coverage (`tab:calibration`), Table 9 the scale review
(`tab:scale`). Figure 1 is the paired differences (`fig:paired`), Figure 2 the cumulative curves
(`fig:cumulative`), Figure 3, in the appendix, the zero-fraction scatter (`fig:zerofraction`).

## Regeneration commands

| Command | Regenerates |
|---|---|
| `.\.venv\Scripts\python.exe -m scripts.review_integrity --run R/run` | the integrity log and recomputed scores (needs the release asset `results.parquet`) |
| `.\.venv\Scripts\python.exe -m scripts.registered_inference --run R/run --out <dir>` | `R/inference/inference.csv`, `inference.json`, `paired_repositories.csv` (needs the release asset) |
| `.\.venv\Scripts\python.exe R/summarize_descriptives.py` | every CSV under `R/descriptive/` and the tables in `RESULTS.md` (needs the release asset) |
| `.\.venv\Scripts\python.exe R/posthoc/accounting.py --update-results` | every file under `R/posthoc/` (needs the release asset) |
| `.\.venv\Scripts\python.exe R/panel_diagnostic.py` | `R/evidence/panel-diagnostic/` (strata, skip reasons, per-repository ratios) |
| `.\.venv\Scripts\python.exe -m scripts.validate_star_history compare ...` (README) | `R/evidence/comparison/` (hourly validation, totals and ratios) |
| `.\.venv\Scripts\python.exe -m scripts.run_registered ...` (README; the registered run, not to be repeated) | `R/run/run.json`, `R/execution-summary.json` |
| `.\.venv\Scripts\python.exe paper/figures/make_figures.py` | the three figures under `paper/figures/` |
| `.\.venv\Scripts\python.exe paper/check_numbers.py` | nothing; asserts this table against the report |
| the PowerShell block at the end of this file | nothing saved; prints the post-hoc per-stratum reading of Section 5 from `R/posthoc/posthoc-paired-repositories.csv` |

## The 18 declared comparisons (Tables 2 and 3, Figure 1, abstract, Section 5, summary)

File: `R/inference/inference.csv` (18 rows; one row per `model`, `reference`, `horizon`). Columns:
`mean_diff` (mean difference, 3 decimals), `mean_diff_ci_low` and `mean_diff_ci_high` (the 95% interval),
`median_diff` (4 decimals), `repo_win_rate` times `n_repos` rounded (repositories where the model is lower),
`repo_win_rate` (strict win fraction, 3 decimals), `wilcoxon_p_bh` (adjusted p, two significant figures).
Derived statements: "46 to 89 of 300" and "293 to 298 of 300" are the minimum and maximum of the win counts
over the nine `local_mean_28` and the nine `autoets_weekly` rows; "excludes zero in five of nine" counts
`local_mean_28` rows with `mean_diff_ci_high < 0`; "largest adjusted p 0.0067" is the maximum `wilcoxon_p_bh`
over the `local_mean_28` rows (TimesFM 3, horizon 7); "-0.101 to -0.258" are the maximum and minimum
`mean_diff` over those rows; "0.0003 to 0.0041" the minimum and maximum `median_diff` over those rows;
"-1.07 to -1.19 at 7 days" and "-6.72 to -6.75 at 90 days" are the ranges of `mean_diff` over the
`autoets_weekly` rows at those horizons; "the mean difference in all nine cells" against AutoETS is
`mean_diff < 0` on every `autoets_weekly` row; "20,000" is `n_bootstrap`; the bootstrap root seed 20260914 is
`seed`. `inference.json` holds the family declaration (`comparison_count` 18, BH, two-sided).

## The post-hoc accounting (Table 4, Figures 2 and 3, Section 6, summary)

File: `R/posthoc/posthoc-paired-summary.csv`, rows with `reference == local_mean_28` and `model` in
`chronos2`, `timesfm3`, `timesfm2p5`; columns `qscore9_difference`, `zero_difference`,
`positive_over_difference`, `positive_under_difference` (3 decimals). "0.004 to 0.015" is the range of
`zero_difference` over those nine rows; "small beside the mean gain" is `zero_difference` below the absolute
`mean_diff` in every cell; "in every cell larger than that cell's median difference" is `zero_difference`
above `median_diff` of `R/inference/inference.csv` in each of the nine cells (the unrounded minimum
`zero_difference`, 0.0036 for TimesFM 3 at 7 days, is below the largest median, 0.0041 for TimesFM 2.5 at
90 days, so the statement is made cell by cell); "-0.088 to -0.209" the range of `positive_over_difference`;
"between -0.768 and -0.777" the range of `zero_difference` over the three `autoets_weekly` rows at horizon
30. Figure 2 reads `R/posthoc/posthoc-contribution-curves.csv` (columns `rank`, `repository_fraction`,
`cumulative_*_difference`); the sentence describing it (the total at its final level within the first few
percent of repositories, then drifting upward; against AutoETS the gain accruing across most of the panel
with overprediction its largest part) is asserted from that file at horizon 30. Figure 3 reads
`R/posthoc/posthoc-paired-repositories.csv` (columns `context_zero_fraction`, `qscore9_difference`,
`sampling_stratum`); its description (large gains at low zero fractions, losses at high ones; nearly every
repository favoring the model against AutoETS) is asserted from that file at horizon 30.
`R/posthoc/provenance.json`: `date` 2026-09-14, `original_18_mean_differences_match` true,
`confirmatory_tests_added` 0, `max_window_accounting_residual` (floating-point tolerance).

The typical repository by stratum (Section 5, labeled post-hoc; summary): from
`R/posthoc/posthoc-paired-repositories.csv`, rows with `reference == local_mean_28` and the three
foundation models, grouped by `sampling_stratum`, `model`, `horizon` (100 rows each): the median of
`qscore9_difference` is positive in all 27 groups; "5 to 18 of 100", "10 to 34" and "26 to 38" are the
minimum and maximum over the nine groups of each stratum of the count of rows with `qscore9_difference < 0`.
This reading is not in the declared tables; the block at the end of this file prints it.

## The achieved panel (Table 1, Section 4, summary)

| Number | File | Row and column or key |
|---|---|---|
| 100,687; 46,811; 1,052; 148,550 | `R/evidence/panel-diagnostic/strata.csv` | `frame_size` by `sampling_stratum`; their sum |
| 100 accepted per stratum; 300 | same; `R/evidence/panel/panel-summary.json` | `sample_size`; `n_accepted` |
| 98; 348; 24; 470 skipped | same; `panel-summary.json` | `skip_count`; `n_skipped` |
| 466 with HTTP 404; 4 with HTTP 403 | `R/evidence/panel-diagnostic/skip-reasons.csv` | sum of `count` by `reason` |
| Ratio medians 0.968, 1.004, 1.006; P10; P90 | `strata.csv` | `ratio_median`, `ratio_p10`, `ratio_p90` (3 decimals) |
| Zero in last 90: 52, 22, 1 | `strata.csv` | `last90_zero_repositories` |
| Last-90 median 0, 4, 39 | `strata.csv` | `last90_stars_median` |
| 289,316 repository-days | `panel-summary.json`; `R/run/manifest.json` | `n_signal_rows`; the sum over the manifest of the days from `observation_start` to 2026-08-31 |
| Los Angeles calendar; selection seed 20260913 | `panel-summary.json` | `calendar_convention`, `selection_seed` |
| Creation dates 2023-01-02 to 2025-02-19 | `R/run/manifest.json` | minimum and maximum of `creation_date` |
| At least nine months before the first cutoff; nine to 41 months | `R/run/manifest.json` and the cutoffs | whole months from the latest creation date to 2025-12-05 (9) and from the earliest to 2026-06-03 (41) |
| 900 repository-cutoff windows; 320 windows from 140 repositories; 572 from 228; 8 from 7 | `R/descriptive/qscore9-regime.csv` | sum of `n_windows`; `n_windows`, `n_repos` by `regime` (any model row) |

## The run (Section 4, Appendix A, Appendix C, summary)

| Number | File | Key |
|---|---|---|
| 48,600 rows; 300 checkpoints; 18 models; gate pass; no failure; no resume | `R/execution-summary.json` | `integrity[0].n_rows`, `checkpoint_count`, `gate`, `failures`, `resumes` |
| 18,662 seconds; 5 hours 11 minutes | `R/execution-summary.json` | `elapsed_seconds_including_resumes` |
| 2026-09-13 07:54 UTC start; 13:05 finish | `R/run/run.json` | `started_at`, `finished_at` |
| Implementation `ca67dd22...` | `R/run/run.json` | `implementation_commit` |
| Protocol `5f01769b...`; SHA-256 `dfe2f4ad...` | `R/run/run.json` | `protocol_commit`, `protocol_sha256` (also `README.md`, `RESULTS.md`) |
| Model IDs and revisions; licences | `R/run/run.json` | `specification.foundation_models` (also `study/run_spec.json`, `PROTOCOL.md`) |
| RTX 4070 SUPER; driver 610.47; CUDA 12.8; PyTorch 2.11.0 | `R/run/run.json` | `hardware` |
| chronos-forecasting 2.3.2; timesfm 3.0.2; statsforecast 2.1.1 | `R/run/run.json` | `packages` |
| Seeds 20260913, 20260912, 20260914 | `R/run/run.json` | `seeds` |
| Cutoffs; horizons; endpoint 2026-08-31; batch size 1 | `R/run/run.json` | `config`, `observation_end`, `specification.inference` |
| 2,048-day maximum context; 200 draws | `R/run/run.json` | `specification.inference.max_context`, `n_samples` |
| Thirteen secondary baselines | `R/run/run.json`; `PROTOCOL.md` "Baselines" | `specification.baselines` lists 15, of which `local_mean_28` and `autoets_weekly` are the primary references |
| `results.parquet` SHA-256 `53ff5a53...`; 433,172,286 bytes | `R/run/run.json` `artifact_sha256`; `README.md` | the byte count is stated in `README.md` only |

## Validation, readiness and cost (Appendix A, Section 7, Appendix C, summary)

| Number | File | Where |
|---|---|---|
| 20 validation repositories, all complete | `R/evidence/validation-capture/validation.json` | `n_attempted`, `n_complete` |
| Lowest MAD for 20 of 20 against UTC and 18 of 20 against fixed UTC-8; two ties | `R/evidence/comparison/validation-report.md` | the per-repository table (rows `Repository | LA MAD / agreement | Fixed UTC-8 MAD / agreement | UTC MAD / agreement`): LA below UTC on all 20 rows, below fixed UTC-8 on 18, equal to it on 2 (asciidoc-py/asciidoc-py, bwaldvogel/neighbourhood); the same counts are in the author-accepted text of `R/evidence/readiness.json`, `timezone_evidence` |
| Pooled MAD 1.975 (Los Angeles), 2.065 (UTC-8), 2.713 (UTC) | `R/evidence/comparison/validation-report.md` | first table (from `comparison.json`) |
| Endpoint below archive for 17 of 20 | `R/evidence/readiness.json`; `R/evidence/comparison/repository_2024_totals.csv` | `unstar_interpretation`; rows with `api_to_archive_ratio < 1` |
| Large projects' ratio 0.728 to 0.994; 13 of 15 at least 5 percent below; "6 to 27 percent below" (summary) | `R/evidence/comparison/repository_2024_totals.csv` | `api_to_archive_ratio` for the 15 rows with `metadata_stars_at_capture >= 1000`; count at or below 0.95; 100(1 - ratio) over those 13 rows runs from 6.3 to 27.2 |
| BigQuery 12,510,623,170,560 bytes; about $71.11 | `R/evidence/readiness-review.md` | the cost paragraph (also `R/evidence/query-provenance-final.json`) |
| Readiness approved 2026-09-13 | `R/evidence/readiness.json` | `approved_by`, `approved_at` |

## Descriptive tables (Section 5, Appendix D)

| Number | File | Row and column |
|---|---|---|
| Pooled QScore9 by stratum (Table 7) | `R/descriptive/qscore9-sampling_stratum.csv` | `qscore9` by `sampling_stratum`, `model_name`, `horizon` (3 decimals) |
| AutoETS coverage 0.979 to 0.995 by stratum (Table 6); six multiplicative fits per horizon | `R/descriptive/autoets-coverage.csv` | `coverage_80`, `multiplicative_seasonality_fits` |
| "Six fits at each horizon, from two repositories", all in the top stratum | `R/descriptive/autoets-fits.csv` | the 18 rows with `multiplicative_seasonality` true: 6 at each `horizon`, `repo_name` in {OpenHands/OpenHands, coderamp-labs/gitingest}, `sampling_stratum` 1000+; `RESULTS.md` "AutoETS interval coverage and specifications" says the specification counts were requested after the run |
| AutoETS widths 0.79, 3.60, 49.69 (daily); 0.80, 3.71, 55.99 (fit-mean) | `R/descriptive/autoets-widths-90.csv` | `median_daily_width_80`, `median_fit_mean_width_80` (2 decimals); `RESULTS.md` "AutoETS 90-day interval widths" says the widths were requested after the run within the declared secondary calibration analysis; the summary quotes the top-stratum daily width 49.69 |
| Coverage ranges 0.824 to 0.837 (Chronos-2), 0.880 to 0.910 (TimesFM 3), 0.906 to 0.924 (TimesFM 2.5), 0.941 to 0.955 (local mean), 0.986 to 0.988 (AutoETS); "98.6 to 98.8 percent"; "about 99 percent" (both ends round to 99) | `R/descriptive/calibration.csv` | `coverage_80` by `model_name`, `horizon` |
| Top-five share 88.5 to 94.3 percent; skill defined 209, 239, 259; leave-one-out ranges (Table 9) | `R/descriptive/scale-local_mean_28.csv` | `top5_positive_gain_share`, `n_defined_skill`, `leave_one_out_min_gain`, `leave_one_out_max_gain` for the three foundation models |

## Registration and what is not run (Sections 3, 7, 8, 9; Appendix A)

| Number or fact | File |
|---|---|
| Protocol commit `5f01769b6be4c32814befdd7cc3395b6dcc386ed`, SHA-256 `dfe2f4ad...`, registered 2026-09-12 | `README.md` "Registration and evidence"; `PROTOCOL.md` header; `RESULTS.md` line 3 |
| Frame dates, eligibility of 20 WatchEvents by day 90, strata, seeds, calendar formula, regime rules, models, baselines, QScore9, inference settings, licences | `PROTOCOL.md`, Study 1 text (the first 18,435 bytes) |
| Study 1's follow-up cohort: repositories created on or after 2026-09-13, identical design, after the write-up; availability-bound; no test in this family; closing date, endpoint and frame coverage open | `PROTOCOL.md` "Registered follow-up after the write-up" |
| 20 validation repositories selected 2026-09-12 | `study/validation_repositories.json` |
| Study 2 registration `df55867c982dfe2bb6e1152ec8ae93e3cd228c45`; full-protocol SHA-256 `33cefd8e...`; 54 external, 6 synthetic, 18 prospective tests; 3 domains, 300 series, 18 generator cells, 30 replicates | `README.md` "Study 2 implementation and source readiness"; `PROTOCOL.md` Study 2 addition of 2026-09-14 |
| Holdout freeze 2026-09-28 18:00 UTC; "a new calendar test on possibly familiar entities" that does not replace the follow-up | `PROTOCOL.md` "October prospective calendar holdout" |
| Holdout not run; npm clock reset to 2026-10-20; family E01 to E18; two domains deferred to a family of 36 | `PROTOCOL.md` dated addition of 2026-10-12, committed at `8db0d73` (2026-10-12 21:29 UTC); `check_numbers.py` confirms the commit from `git log` |
| "As of 2026-10-12" no Study 2 target value or forecast exists | `study/study2/acquisition_status.json` (`target_values_opened` false, `real_forecasts_generated` false, as quoted by the addition); the sentence carries its date and is re-checked on posting day against the same file |
| Pinned revision dates: TimesFM 2.5 `1d95242` 2025-10-02; TimesFM 3 `43046b8` 2026-09-02, weights uploaded 2026-08-24; Chronos-2 `29ec376` 2026-06-05 (repository revision dates, not training cutoffs) | `docs/research/2026-10-11-literature-recheck.md`, "Model cards and training data" table |
| Release asset "to be published"; URL to be filled | `README.md` "Saved registered run"; `docs/STATE.md` (no release exists) |
| Licences: MIT, CC BY 4.0, Apache-2.0, TimesFM Non-Commercial License v1.0 | `README.md` "Licence"; `PROTOCOL.md` model table |
| The author's statement (Section 10) | `README.md` "How this project was built", verbatim |

## The six citations from the literature re-check (Sections 1, 7, 8)

`docs/research/2026-10-11-literature-recheck.md`, the "Items" table and the table of three items outside
the window; `paper/references.bib` keys: `schoess2026` (arXiv 2609.39386, 2026-09-30), `chin2026` (arXiv
2609.13840, 2026-09-12), `ebrahim2026` (arXiv 2610.00589, 2026-09-30), `islam2026` (arXiv 2609.27867,
2026-08-20), `moghadasi2026` (arXiv 2609.10357, 2026-09-09), `garza2026` (arXiv 2603.08707, v2 2026-03-10).
The `kim2026` journal, volume, pages and DOI come from the same document's "The cited items, re-checked"
table. Author given names are not in the record for these seven items; the entries carry surnames only.

## Version 1 (Section 2 and Appendix B, Table 5), quoted and not recomputed

| Number | File (local, gitignored) | Where |
|---|---|---|
| 208 repositories; 414,271 daily rows; 2008-11-13 to 2026-06-22; 179 usable; 41, 69, 69 | `v1_reference/RESULTS.md` | Section 2, "What was pulled" and the cohort table |
| Expanding context from 180 days after the first star; step 30 days; at most eight windows; horizons 7, 30, 90; 200 trajectories | `v1_reference/RESULTS.md` | Section 3, "Backtest" and "Models" |
| Lower mean CRPS in all nine cells; breakout 6.2 to 8.5 against 11.2 to 28.0 | `v1_reference/RESULTS.md` Section 4.1 table, the three breakout rows: chronos2 and timesfm columns 6.23 to 8.52; naive, linear, ets and lightgbm columns 11.19 to 28.00; `docs/HISTORY.md` | the primary CRPS table |
| Table 5: local mean, Chronos-2, TimesFM-2.5 by cohort and horizon | `v1_reference/RESULTS.md` | Section 4.2 table |
| Win rates 40.6 to 80.5 percent | `v1_reference/STUDY_AUDIT.md` | "Must-fix issues addressed", item 1 |
| "Roughly 30 to 77 percent", the audit's figure, tied to no named reference | `v1_reference/STUDY_AUDIT.md` | "Must-fix issues addressed", item 3 (scale domination), which names no reference; `v1_reference/RESULTS.md` has no such figure |
| Audit date 2026-07-12; no invalidating code defect; median 5.02 stars per day and 7.7 percent zero days; 78.0 percent peaked before, 12.2 percent inside | `v1_reference/STUDY_AUDIT.md` | header; "Executive verdict"; "Invalidating" items 1 and 2 |
| The must-disclose list; the prospective post-release cohort in the prescription | `v1_reference/STUDY_AUDIT.md`; `docs/HISTORY.md` "The audit" | "Must-fix issues addressed", items 1 to 10; P1 item 4; the prescription paragraph |
| v1 artifacts on a computer no longer used; recovery deferred | `README.md` "Registration and evidence"; `docs/HISTORY.md` | text |

## Numbers in `SUMMARY.md` only

All of its numbers are in the tables above. Its "What could not be verified" items cite `README.md` (the
unfilled URL and the release not yet made), `R/evidence/readiness-review.md` against
`R/evidence/comparison/repository_2024_totals.csv` (the "5 to 27 percent" prose against the table's 6.3 to
27.2), the literature re-check (surnames only for seven cited items), and `study/study2/acquisition_status.json`
(the dated Study 2 sentence).

## The post-hoc per-stratum reading, printed

Run from the repository root in PowerShell; it reads one saved file and saves nothing:

```powershell
@'
import pandas as pd
q = pd.read_csv("reports/registered-2026-09-13/posthoc/posthoc-paired-repositories.csv")
q = q[(q.reference == "local_mean_28") & q.model.isin(["chronos2", "timesfm3", "timesfm2p5"])]
g = q.groupby(["sampling_stratum", "model", "horizon"]).qscore9_difference
print(g.agg(lower=lambda s: int((s < 0).sum()), median="median").round(4).to_string())
'@ | .\.venv\Scripts\python.exe -
```

## The Study 2 sections under `paper/sections/` (added 2026-10-15)

The four files `paper/sections/study2-question.tex`, `study2-design.tex`, `study2-panel.tex` and
`study2-results-placeholder.tex` were written to be `\input` by the paper; from 2026-10-16 `paper.tex`
read the first three (each of the design and panel sections split into a body file and a detail file in
the appendix) and `study2-results.tex` in place of the placeholder, and since the reorganization of
2026-10-17 none of the four body files exists (the section on the reorganized paper below).
`check_numbers.py` read them like `main.tex` (whitespace collapsed) and asserts every figure below against
the expanded paper. `S2` stands for `study/study2`, `N` for `reports/study2-npm/panel`. The
results placeholder holds no number from a run: every cell is `tbd`, and the checker asserts that its
table rows are the declared tuples with `tbd` cells and that no decimal figure appears in it.

### The question (`study2-question.tex`)

| Number or fact | File | Where |
|---|---|---|
| Registration 2026-09-14 at `df55867c982dfe2bb6e1152ec8ae93e3cd228c45`; full-protocol SHA-256 `33cefd8e...` | `S2/external_packages_spec.json` `protocol_commit`, `protocol_sha256`; `PROTOCOL.md` "Study 2, dated addition, 2026-09-14"; `git log -- PROTOCOL.md` (`df55867` dated 2026-09-14) | as in `main.tex` Section 8 |
| Zero-day part 0.004 to 0.015, against the models in every cell; medians 0.0003 to 0.0041; models lower on 46 to 89 of 300 | `R/posthoc/posthoc-paired-summary.csv`, `R/inference/inference.csv` | the same rows and columns as the Study 1 tables above |
| "This hypothesis arose after Study 1 and is tested on separately declared data"; completion not attributed to Study 1 | `PROTOCOL.md` Study 2 addition, opening paragraphs and "Models, distributions and controls" | text |
| The re-check run 2026-10-12; the six items, their arXiv identifiers and dates; the memo's items; fable.intermittent, Bai and Chu, EXAONE Demand; "not found" and the failed routes; what may and may not be claimed | `docs/research/2026-10-11-literature-recheck.md` | header; "Items"; the table of three items outside the window; "The cited items, re-checked"; "What the paper may claim"; "What the paper must cite"; "Where the record is thin" |
| Citation keys `schoess2026`, `chin2026`, `ebrahim2026`, `islam2026`, `kim2026`, `moghadasi2026`, `garza2026`, `fevbench2026` (already in the bib); `tsantilis2025`, `zodiac2026`, `meyer2025`, `damato2026`, `bai2026`, `exaone2026` (added 2026-10-15 at the end of `references.bib`) | `paper/references.bib` | the checker asserts that every `\citep` key in the sections has an entry and that each item's identifier is in both the re-check and the bib |

### The design (`study2-design.tex`)

| Number or fact | File | Where |
|---|---|---|
| Dated addition of 2026-10-12 committed at `8db0d73`; of 2026-10-15 at `5be2ce9` | `git log -- PROTOCOL.md` | the two commits after `df55867`; the checker confirms both and their dates |
| Three domains; 300 series, 100 per stratum; strata [0,0.5), [0.5,0.9), [0.9,1]; all-zero contexts eligible; "balanced stress-test panel" | `PROTOCOL.md` "Domains, frame and selection" | the first paragraph and the domain table |
| Candidate pool min(10,000, N); selection seed 20260914; hash of [seed, domain, stage, key]; stages "candidate" and "selection"; no transfer, no larger pool, no popularity filter | `PROTOCOL.md` "Domains, frame and selection"; `S2/external_packages_spec.json` `seeds.selection` | the sampling paragraphs; the addition of 2026-10-12, item 2 (the walk reading) |
| A = 2025-09-01; E = 2026-08-31; K = 3; cutoffs 2026-06-03, 2026-07-03, 2026-08-02; 275, 305, 335 context days; strata window 2026-03-05 to 2026-06-02; horizons 7 and 30; c_j = E - (30j - 1) | `S2/external_packages_spec.json` `calendar`; `PROTOCOL.md` "Calendar and information boundary" | the checker recomputes the cutoffs from the formula and the context days from the dates |
| Model IDs and revisions | `S2/external_packages_spec.json` `foundation_models` (also `PROTOCOL.md`, `R/run/run.json`) | `model_id`, `revision` |
| Completion: linear interpolation through (0,0); tail scale max(1, q0.9 - q0.8); floor(Q(U) + 0.5); F(0) = 1 fallback only | `S2/external_packages_spec.json` `completion`; `PROTOCOL.md` "Models, distributions and controls" | `interpolation`, `lower_knot`, `tail_scale`, `rounding`, `fm_fallback` |
| Jeffreys occurrence (n+ + 1/2)/29; lookback 28; fewer than two positives gives delta_1 | `S2/external_packages_spec.json` `count_hurdles` | `occurrence`, `lookback`, `minimum_positives`, `fallback` |
| Dynamic count: discount 0.98; four parameters start at 0.5; fallback to `hurdle_count_28` | `S2/external_packages_spec.json` `dynamic_count` | `discount`, `initial_parameters`, `fallback` |
| Seven baselines | `S2/external_packages_spec.json` `baselines` | the list of seven |
| CRPS tolerance 1e-8 by k = 1,000,000; the availability rule | `S2/external_packages_spec.json` `crps`; `PROTOCOL.md` "Discrete CRPS availability, dated addition, 2026-10-15" | `tolerance`, `max_k`; item 5 |
| 54 = 3 x 3 x 2 x 3; E01 to E18 (Table `tab:s2family`); one BH at q = 0.05; 20,000 bootstrap replicates; bootstrap seed 20260917; two-sided Wilcoxon; E19 to E54 as a later family of 36 | `S2/external_comparisons.json` (54 rows); `S2/external_packages_comparisons.json` (18 rows, equal to the first 18, `authority` naming item 3 and `8db0d73`); `PROTOCOL.md` addition of 2026-10-12, item 3 | the checker builds each table row from the JSON |
| The synthetic grid: z in {0.2, 0.8, 0.95}, mu+ in {1, 5, 25}, rho in {0, 0.8}; 18 cells; 30 replicates; 270 observations; first context 180; origins 180, 210, 240; horizons 7, 30; 540 series; seed 20260918; common random numbers with separate occurrence and size streams | `S2/grid_manifest.json` `cells`, `n_cells`, `replicates_per_cell`, `observations`, `origins`, `horizons`, `n_series`, `seed`, `common_random_numbers`, `streams`; `PROTOCOL.md` "Synthetic intervention component" | the checker reads the cell parameters and the 30 streams |
| S01 to S06 at horizon 30 (Table `tab:s2synfamily`) | `S2/synthetic_comparisons.json` | the checker builds each table row from the JSON |
| Six seeds 20260914 to 20260919 | `S2/external_packages_spec.json` `seeds` | all six |
| Holdout freeze 2026-09-28 18:00 UTC; targets October 1 to 7 and 1 to 30; settlements 2026-10-15 and 2026-11-07 18:00 UTC; H01 to H18; not run; npm clock reset to 2026-10-20 23:59 UTC | `PROTOCOL.md` "October prospective calendar holdout"; the addition of 2026-10-12, items 1 and 2; `S2/holdout_comparisons.json` | text; `comparison_count` 18 |
| The gate for the packages component: one npm panel bound by hash, no holdout freeze; the 54-test component unchanged | `docs/research/2026-10-15-study2-run-path-review.md` verdict 3; `S2/npm_panel_status.json` `panel` hashes | text |
| Contamination ledger rows for npm and the synthetic component; pinned revision dates | `PROTOCOL.md` "Contamination ledger"; `docs/research/2026-10-11-literature-recheck.md` "Model cards and training data" | the two rows; the card table |

### The achieved npm panel (`study2-panel.tex`)

| Number | File | Key |
|---|---|---|
| Frozen 2026-10-15 01:57 UTC; verified 02:00 UTC; deadline 2026-10-20 23:59 UTC met; targets not opened; rule cited | `S2/npm_panel_status.json` | `panel_written_at`, `panel_verified_at`, `readiness_deadline`, `deadline_met`, `target_values_opened`, `protocol_rule`, `status` |
| 4,486,927 names; 4,493 pages of at most 1,000; 2026-10-14 00:23 to 02:04 UTC; the replication feed | same | `inventory.names`, `pages`, `page_limit`, `first_page_acquired_at`, `last_page_acquired_at`, `source` |
| Walk: 12,943 visited; 10,000 eligible; 2,918 ineligible; 25 excluded (HTTP 404); stopped on a full pool | same; `N/selection.json` `report.candidate_walk` | `candidate_walk.visited`, `eligible`, `ineligible`, `excluded`, `excluded_reasons`, `stop_reason` |
| Eligible frame about 3,466,682, bounds 10,000 and 4,483,984; inclusion probability about 0.0029, bounds 0.0022 and 1 | same; `N/selection.json` `report` | `frame.eligible_frame_size_estimate` (rounded to a whole number), `eligible_frame_size_bounds`, `candidate_inclusion_probability_estimate` (4 decimals), `candidate_inclusion_probability_bounds` (4 decimals; 1.0 printed as 1); the checker recomputes the estimate as inventory size times eligible over visited |
| Context pull: 10,000 keys; 9,998 complete; 2 excluded (HTTP 404) and their names; 12,762 attempts: 9,998 with 200, 40 with 404, 2,708 with 429, 2 with 504, 14 timeouts; window 2025-09-01 to 2026-06-02; strata from 2026-03-05 | same | `context.keys`, `complete_candidates`, `exclusions`, `excluded_keys`, `http_attempts`, `http_attempts_by_status`, `window`, `strata_window_start` |
| Strata: 2,431, 7,558, 9 complete candidates; 100, 100, 9 taken; 0, 0, 91 unfilled (Table `tab:s2panel`); 209 series | same `achieved_strata`, `series`; `N/manifest.json` `series` (stratum counts); `N/selection.json` `report.strata` | the checker counts the manifest's strata and checks the first-in-hash-order property against `reserve_order` |
| Creation dates 2011-08-26 to 2025-08-08; 80 scoped names | `N/manifest.json` | minimum and maximum of `created_at` over the 209 series; count of `series_id` beginning with `@` |
| The approval: 36,000 requests and 13 hours; 30,198 attempts; 12,943, 12,762, 4,493 by host; 52 invocations; 45,508 seconds (12 hours 38 minutes); 2026-10-14 00:23 to 2026-10-15 01:57 UTC; spacing 1 s, then 3 s from 2026-10-14 22:51 UTC at about 20 requests a minute; 2,708 answers of 429; the outage of 08:44 to at least 10:25, answering again 21:37 | `S2/npm_panel_status.json` | `approval.words`, `http_attempt_ceiling`, `invocation_seconds_ceiling`; `acquisition.http_attempts`, `http_attempts_by_host`, `invocations`, `invocation_seconds`, `first_attempt_at`, `last_attempt_at`, `request_spacing`, `interruptions`; `context.http_attempts_by_status["429"]` |
| "About 26 hours"; five million requests a month; no documented quota; 429 answers as reaching the throttle; the data statement and the trademark notice; the Open-Source Terms of 2022-03-10; what stays out | `docs/research/2026-10-15-npm-redistribution-review.md` | "What is to be published"; "What the documents say"; "The five questions"; "Recommendation" items 1 to 5 |
| `aggregate-error`, dense stratum, zero fraction 0; last-28-day context mean 7,637,136 | `N/manifest.json` (the series entry); `PROTOCOL.md` addition of 2026-10-15, item 5 | `stratum`, `zero_fraction`; the closing sentence of item 5 |
| The next largest last-28 mean about 13,000; losses of a different order | `docs/research/2026-10-15-study2-run-path-review.md` verdict 8 | the first paragraph and the first observation (from the frozen context parquet, which is not in the tree) |

### The results placeholder, replaced on 2026-10-16 by `study2-results.tex`

Tables `tab:s2ext` and `tab:s2syn` list the tuples of `S2/external_packages_comparisons.json` and
`S2/synthetic_comparisons.json`, now with the run's values (the paper's heading below); the denominators
209 and 30 are `series` in `S2/npm_panel_status.json` and `replicates_per_cell` in `S2/grid_manifest.json`;
"16 variants" is the count of `variants` in `S2/external_packages_spec.json`; "540 series" is `n_series` in
the grid manifest. The checker asserts that no `tbd` remains and that the placeholder file is gone.

### Regeneration commands for the Study 2 files

| Command | Regenerates |
|---|---|
| `.\.venv\Scripts\python.exe scripts\study2_ingest.py npm inventory ...` and `npm panel ...` (README) | `data\raw\study2\npm\inventory.json`, `inventory.walk.json`, `N\manifest.json`, `N\selection.json`, `S2\npm_panel_status.json` and the ignored `context.parquet` (the frozen pull, not to be repeated; a complete walk and pull are reused from the saved captures without requests) |
| `.\.venv\Scripts\python.exe scripts\study2_evidence.py ...` (README) | `S2\acquisition_status.json` |
| `.\.venv\Scripts\python.exe paper/check_numbers.py` | nothing; asserts this table against the sections |

## The paper: `paper.tex` and the Study 2 results (added 2026-10-16, revised the same day)

`paper/paper.tex` is the report extended with Study 2. Its Sections 1 to 6, the Study 1 limitation items,
the follow-up paragraph, the reproducibility paragraph, the author's statement and Appendices A to D are
read by `\input` from fourteen files under `paper/shared/`, split out of `main.tex` on 2026-10-16;
`main.tex` reads the same files and expands to its committed text (`git show f325a67:paper/main.tex`) byte
for byte apart from one dated sentence in `main.tex` itself, which now says that both Study 2 components
ran on 2026-10-15 (`check_numbers.py` asserts the expansion against the committed file with that one
sentence replaced). The Study 2 sections were the files under `paper/sections/`: `study2-question.tex`,
`study2-design.tex`, `study2-panel.tex`, `study2-results.tex` (the body), `study2-design-detail.tex`,
`study2-panel-detail.tex` and `study2-appendix.tex` (the appendix); the four body files were removed on
2026-10-17 and the three appendix files remain. After the revision of 2026-10-16 the
design section keeps the calendar, the models and variants, the comparators, the families and the grid in
the body and moves the frame-and-sampling rule, the completion, the baselines, the two family tables, the
scores, the seeds, the gate, the holdout and the contamination ledger to Appendix E; the panel section
keeps the strata, the short third stratum and the dominant series and moves the inventory, the walk, the
context pull, the panel table, the budget and the data statement to Appendix F; the results section
moves the runs to Appendix G and the zero-day counts, the secondary readings and the synthetic cell figure
to Appendix H. `check_numbers.py` reads `paper.tex` expanded, the section files and `PAPER-SUMMARY.md` like
`main.tex` and `SUMMARY.md`; the needles of the design and panel sections are asserted against the body
file and its detail file concatenated. `NR` stands for `reports/study2-npm/run-2026-10-15`, `SR` for
`reports/study2-synthetic-2026-10-15`, `DO` for `reports/study2-posthoc-dynamic-occurrence`. Every CSV is
read with `float_precision="round_trip"`, as `RESULTS-npm.md` asks. Values are printed as the two results
documents print them: four significant figures, thousands separators from 1,000 up in the paper (from
10,000 up in the results documents), $p$-values to three significant figures, and any value whose four
significant figures need an exponent as a power of ten (so `1.055e-09` of the strata file prints as
$1.055 \times 10^{-9}$).

Tables of the paper as of the revision of 2026-10-16 (the extension of 2026-10-17 renumbers them; the
numbering in force is in the Study 3 section at the end of this file), in source order: Tables 1 to 4 and
Figures 1 and 2 as in the report; Table 5 the external family's results (`tab:s2ext`), Table 6 the
synthetic family's results (`tab:s2syn`), Table 7 the accounting parts of the hurdle contrast
(`tab:s2parts`), Table 8 the post-hoc dynamic-occurrence rows against the completed control and the fixed
hurdle (`tab:s2dyn`), Figure 3 the npm paired differences (`fig:s2npm`); in the appendix, Tables 9 to 13 as the report's Tables 5 to 9, Figure 4 the zero-fraction
scatter as in the report, then the external family E01 to E18 (`tab:s2family`, Table 14), the synthetic
family (`tab:s2synfamily`, 15), the achieved npm panel (`tab:s2panel`, 16), Figure 5 the synthetic cells
(`fig:s2cells`), the post-hoc stratum tests (`tab:s2regime`, 17), the empirical-hurdle reading
(`tab:s2empirical`, 18), the scaled score (`tab:s2scaled`, 19), the strata (`tab:s2strata`, 20), the
sensitivity (`tab:s2sens`, 21), the cells (`tab:s2cells`, 22), the npm model scores (`tab:s2scores`, 23),
the synthetic model scores (`tab:s2synscores`, 24), the remaining dynamic-occurrence rows
(`tab:s2dynrest`, 25) and the dynamic-occurrence accounting parts (`tab:s2dynparts`, 26). Sections 1 to 6
are the report's, 7 to 10 Study 2's question, design, npm panel and results (with the post-hoc
dynamic-occurrence subsection at the end of 10), 11 the discussion, 12 the limitations, 13 what is not run,
14 reproducibility, 15 the author's statement; Appendices A to D are the report's, E the Study 2 design
detail, F the npm panel detail, G the runs and commands, H the secondary tables and post-hoc readings. In
Tables 5 and 6 the variant and reference names are replaced by the model's name and the contrast
(`hurdle vs completed`, `hurdle vs count hurdle`, `raw vs local mean`); the tuples are in Table 14.

### The two families (Tables 5 and 6, Section 10, the abstract, the discussion, the summary)

| Number | File | Row and column or key |
|---|---|---|
| The 18 npm rows and the 6 synthetic rows: mean, interval, median, lower / tied / higher, adjusted $p$ | `NR/inference/inference.csv`, `SR/inference/inference.csv` | `mean_diff`, `mean_diff_ci_low`, `mean_diff_ci_high`, `median_diff`, `wins`, `ties`, `losses`, `wilcoxon_p_bh`; `n_entities` 209 and 30; `n_bootstrap` 20,000; `bootstrap_root` 20260917; `declared_count` 18 and 6; the row order is the declaration's |
| "Twelve of the eighteen ... five of the six"; "ten ... and two against it"; "all five synthetic rejections are against the hurdle variant"; "No test favors the substitution at $q = 0.05$"; the abstract's "No pooled test favors the substitution at q = 0.05, and two of six npm tests and all three grid tests reject against it" | same | `reject_bh_005` counts; the sign of `mean_diff` on the rejecting rows; no rejecting row of a hurdle-against-control contrast has `mean_diff < 0` |
| Hurdle against control: "from 90.24 to 253.9 (carried by `aggregate-error`), with every interval above zero"; "within 0.014 of zero, three below it and three above"; "lower on 81 to 121 of the 209 series"; E10 and E16 (120 and 107 higher; adjusted $p$ 0.00215 and 0.0276); "from 0.203 to 0.628"; "in E01 the typical series leans to the hurdle, lower on 121 of 209 series with a median of -0.01376" and the lean of E04 and E13 | `NR/inference/inference.csv`, the six rows with a `_completed` reference | `mean_diff`, `mean_diff_ci_low`, `median_diff`, `wins`, `losses`, `wilcoxon_p_bh`, `reject_bh_005`; the rank sums behind "the larger signed-rank sum on its side" are `rank_sum_model_lower` and `rank_sum_reference_lower` in `NR/posthoc/sensitivity_inference.csv` (registered columns) and are reproduced by `NR/check_directions.py` |
| Synthetic hurdle against control: "from 0.08599 to 0.08769, with every interval above zero"; "5 or 6 of the 30"; "from 0.00415 to 0.00676" | `SR/inference/inference.csv`, S01, S03, S05 | the same columns |
| Hurdle against the count hurdle: adjusted $p$ from $2.66 \times 10^{-5}$ to $3.19 \times 10^{-25}$; "from -5,090 to -6,918 (carried by `aggregate-error`)"; "from -0.006349 to -0.0716"; "lower on 115 to 161" | `NR/inference/inference.csv`, the six `hurdle_count_28` rows | the same columns; `reject_bh_005` true on all six |
| S02 and S06 "by 0.05211 and 0.06109 (adjusted $p$ 0.0111 and 0.00798, lower on 9 of 30 blocks each)"; S04 "0.0215 ... 0.12, lower on 11 of 30" | `SR/inference/inference.csv` | the same columns |
| Raw against the local mean: rejects E06, E09, E12, E18; E03 and E15 adjusted $p$ 0.596 and 0.746; "from -2,884 to -5,109 (carried by `aggregate-error`)"; "lower on 84 to 125"; medians 0.007856 and 0.01696 (positive), -0.002297 to -0.005016 (negative); the rank sums on the model's side in all six rows | `NR/inference/inference.csv`, the six `local_mean_28` rows; `NR/posthoc/sensitivity_inference.csv` `registered_larger_sum_favors` | the same columns |

### The regime reading (Section 10, the abstract, the discussion, Appendix Tables 17 and 20)

| Number | File | Row and column |
|---|---|---|
| The hurdle lower than its control on 81, 60 and 66 of the 100 sparse series at horizon 7 (E01, E07, E13) and on 58, 45 and 54 at horizon 30 (E04, E10, E16); on 32 to 43 of the 100 dense series in every cell; the very sparse median exactly 0 in five of six cells; lower than `hurdle_count_28` on 80 to 94 dense and 29 to 63 sparse | `NR/inference/secondary_strata_contrasts.csv`, `metric == qscore9` | `wins`, `median_diff` by `stratum`, `id` (the declared secondary table, Table 20) |
| Table 17: lower / tied / higher, median and raw two-sided signed-rank $p$ of the hurdle against its control within each stratum; "raw $p$ below 0.002 for all three sparse-stratum contrasts at horizon 7 and from 0.47 to 0.892 at horizon 30" | `NR/inference/series_scores.csv` (post-hoc; the checker recomputes every cell: `qscore9` of `<model>_hurdle` minus `<model>_completed` per `series_id`, grouped by `stratum`; `scipy.stats.wilcoxon` on the nonzero differences, two-sided) | the same reading is printed by the command in `docs/research/2026-10-16-standing-and-referee-read.md` |
| On the grid the hurdle lower than its control in 4 to 6 of 30 blocks at $z = 0.2$, 12 to 15 at $z = 0.8$ and 21 to 26 at $z = 0.95$ | `SR/inference/series_scores.csv` (post-hoc; block means of `qscore9` at horizon 30 over the six cells with each zero probability, hurdle minus completed, per `replicate`) | the cell parameters from `SR/inference/secondary_cells_contrasts.csv` |
| "$p = 28.5 / 29$ ... about 1.7 percent" | arithmetic from the registered Jeffreys rule $(n_+ + 1/2) / 29$ with $n_+ = 28$ | asserted by the checker |

### The empirical hurdle and the dynamic count (Section 10, the discussion, Appendix Tables 18, 23 and 24)

| Number | File | Row and column |
|---|---|---|
| Table 18: the foundation-model hurdle against `hurdle_empirical_28` by stratum (lower / tied / higher) and the completed control against it over 209 series (counts, median, raw $p$); "lower on 63 to 72 of the 100 dense series and on 33 to 57 of the 100 sparse"; "lower than the empirical hurdle on 120 to 140 of 209 series at horizon 30"; "on only 88 and 90 of 209 for Chronos-2 and TimesFM 2.5 (117 for TimesFM 3)" | `NR/inference/series_scores.csv` (post-hoc, recomputed by the checker as above) | `qscore9` by `model`, `horizon`, `series_id`, `stratum` |
| The dynamic count's mean QScore9 1.721 at horizon 30 against 1.754 to 1.792 for the completed models, 1.819 for `hurdle_count_28`, 1.648 for the oracle; the lowest of the sixteen variants | `SR/inference/secondary_scores.csv` | `qscore9` by `horizon`, `model` (Table 24) |
| Lower than the completed Chronos-2, TimesFM 3 and TimesFM 2.5 in 21, 18 and 24 of 30 blocks; lower than `hurdle_count_28` and `local_mean_28` in 26 of 30 | `SR/inference/series_scores.csv` (post-hoc; block means at horizon 30 per `replicate`) | `qscore9` |
| On npm the completed models lower than `dynamic_count` on 108 to 146 of 209 series; its means 10,948 and 11,471 against 3,641 to 4,500 | `NR/inference/series_scores.csv` (post-hoc); `NR/inference/secondary_scores.csv` | `qscore9` (Table 23) |
| The typical npm series and the trade: the median series' zero-day difference (hurdle minus completed) positive in all six cells, 0.003 to 0.036 | `NR/inference/series_scores.csv` (post-hoc) | `zero` by `model`, `horizon`, `series_id` |

### The one series behind every npm mean (Sections 9 and 10, the limitations, the summary)

From `NR/inference/paired_entities.csv` (209 rows per comparison id, column `difference`), recomputed by
the checker with Study 1's definitions: the series whose omission moves the mean most is `aggregate-error`
in all 18 rows, with its difference of the mean's sign; "fall from 90.24 to 253.9 to 0.6334 to 1.599" is
the mean without it over the six hurdle-against-control rows; "0.995 to 0.998" is the share of the positive
gains held by the five largest, over the twelve rows against `hurdle_count_28` and `local_mean_28`.
"7,637,136 downloads a day" is in `PROTOCOL.md`, addition of 2026-10-15, and `study/study2/npm_panel_status.json`;
"the next largest last-28 mean ... about 13,000" and "the median series averages two" are in
`docs/research/2026-10-15-study2-run-path-review.md` (verdict 8) and `NR/RESULTS-npm.md` ("The series
differ in scale"), both from the frozen context file, which is not in the tree.

### The accounting parts (Table 7, Section 10, the discussion)

`NR/inference/secondary_accounting.csv` and `SR/inference/secondary_accounting.csv`, rows by `horizon` and
`model`, columns `qscore9`, `zero`, `positive_over`, `positive_under` (equal-entity means over the full
horizon); each table cell is the hurdle variant's part minus its completed control's. The checker asserts
that the parts sum to the total (`parts_sum`, `max_abs_window_residual` below $10^{-8}$) and that the zero
and overprediction differences are negative and the underprediction difference positive and larger than
both in all nine cells.

### The secondary contrasts (Appendix Table 19, Section 10, the appendix text)

| Number | File | Row and column |
|---|---|---|
| The 18 npm and 12 synthetic scaled rows | `NR/inference/secondary_contrasts.csv`, `SR/inference/secondary_contrasts.csv`, `metric == context_scaled_qscore9` | `mean_diff`, `mean_diff_ci_low`, `mean_diff_ci_high`, `median_diff`, `wins`, `ties`, `losses` |
| Scaled at horizon 7: -0.02204, -0.006708, -0.006123 with intervals below zero; at horizon 30: -0.002395, 0.001291, 0.001687 with intervals including zero; against the count hurdle -0.1182 to -0.1466, every interval below zero; below zero in E06, E09, E12, E18 and including zero in E03, E15; every synthetic horizon-30 scaled interval includes zero | same | `mean_diff_ci_low`, `mean_diff_ci_high` |
| The Brier difference exactly zero against `hurdle_count_28` (209 ties in each of six rows); lower for the hurdle with an interval below zero in E01, E04, E13 and including zero in E07, E10, E16 | `NR/inference/secondary_contrasts.csv`, `metric == occurrence_brier` | `mean_diff`, `ties`, `mean_diff_ci_high`, `mean_diff_ci_low` |
| CRPS unavailable for 66 forecasts (11 x 3 x 2); 13,728 certified of 13,794 with a law; 6,270 without a law; none unavailable on the grid (Appendix G) | `NR/inference/secondary_scores.csv`, `SR/inference/secondary_scores.csv` | sums of `crps_unavailable_bound_not_certified`, `crps_certified`, `crps_with_count_distribution`, `crps_unavailable_no_count_distribution` |

### Model scores, the oracle and the PIT (Appendix Tables 23 and 24; the appendix text; Section 10)

| Number | File | Row and column |
|---|---|---|
| The 16 npm rows: QScore9 at both horizons, scaled QScore9, Brier and CRPS at horizon 30; the 17 synthetic rows | `NR/inference/secondary_scores.csv`, `SR/inference/secondary_scores.csv` | `qscore9`, `context_scaled_qscore9`, `occurrence_brier`, `discrete_crps` by `horizon`, `model` |
| The oracle lowest at both horizons (1.514, 1.648), lowest Brier (0.115) and CRPS (1.504) | `SR/inference/secondary_scores.csv` | the `oracle` rows; the checker takes the minimum over models |
| "no forecaster scores below it in 17 of the 18 cells"; the three exact ties with `dynamic_count` in `cell12`, `cell14`, `cell16`; cell00 "0.1759 and 0.1761 against 0.1767" | `SR/inference/secondary_cells.csv`, horizon 30 | `qscore9` by `cell_id`, `model` |
| The horizon-30 mean of `autoets_weekly` on npm carried by `composer-runtime-pouchdb`, the other unscaled means by `aggregate-error` (Table 23's caption) | `NR/inference/series_scores.csv` | `qscore9` by `model`, `series_id` at horizon 30 (the review of 2026-10-16, item 11: 0.715 and 0.975 to 0.989 of the summed series scores) |
| Oracle PIT "0.099 to 0.104 of its 48,600 target days"; the shown models "0.078 to 0.133"; npm hurdle "0.088 to 0.146" against "0.083 to 0.153" | `SR/inference/pit_histograms.csv`, `NR/inference/pit_histograms.csv`, horizon 30 | `fraction01` to `fraction10`, `n_values` |

### Per cell (Appendix Table 22, Figure 5, Section 10)

`SR/inference/secondary_cells_contrasts.csv`, `metric == qscore9`, `horizon == 30`: `mean_diff`, `wins`
by `cell_id`, `id`; `zero_probability`, `positive_mean`, `persistence`. "23 of the 24 differences are
negative" at $z = 0.95$, $\mu_+ \ge 5$; "0.9342 to 0.9766 above its control at $\rho = 0.8$"; the
count-hurdle contrast exactly 0 at $\mu_+ = 1$, $\rho = 0$.

### The runs (Appendix G, Section 10, Section 14)

| Number | File | Key |
|---|---|---|
| Synthetic: started 2026-10-15 20:16 UTC, completed 20:38; 540 series; 1,317 seconds; no failure, no resume; implementation `3fc3411f...`; readiness approved 20:13:56 UTC, estimate 1,539, budget 2,400 | `SR/run.json` | `started_at`, `completed_at`, `invocations[0].series_completed`, `invocations[0].wall_seconds`, `failures`, `resumes`, `metadata.metadata.implementation_commit`, `metadata.readiness.approved_at`, `estimated_seconds`, `runtime_budget_seconds` |
| npm: started 23:27 UTC, completed 23:38; 209 series; 692 seconds; implementation `3057b16d...`; readiness approved 23:09:06 UTC, estimate 1,741, budget 3,600, at most 300 target requests | `NR/run.json` | the same keys |
| 1,323 and 699 seconds "for the whole process"; the two gate times | `SR/RESULTS-synthetic.md`, `NR/RESULTS-npm.md` | the "Run" and "Gate" paragraphs (quoted; the run files hold the in-run seconds) |
| RTX 4070 SUPER, driver 610.88, CUDA 12.8, PyTorch 2.11.0, batch size 1, peak reserved 2,948,595,712 bytes | both `run.json` | `metadata.hardware`, `invocations[0].memory.peak_reserved_bytes` |
| 55,080 = 540 x 3 x 2 x 17; 20,064 = 209 x 3 x 2 x 16 | `SR/score-recompute.json` `windows`; `NR/integrity/integrity.json` `checks.qscore9.compared` | arithmetic asserted by the checker |
| Targets: 209 attempts, 209 answers, requested between 23:15 and 23:26 UTC (the requesting invocation started 23:15:02 UTC in `pull.json` and the completeness document was verified at 23:26:22 UTC; the 23:14:58 of `NR/RESULTS-npm.md` is the start of the pull process, not of the requests), no retry, no failure; 90 days each | `NR/target-pull/pull.json` `invocations`; `NR/target-pull/completeness.json` `series`, `verified`, `verified_at` | text; the checker asserts the invocation start from `pull.json` |
| Integrity: 0 disagreements for all 20,064 forecasts on QScore9, the parts, the scaled score and the Brier score; 209 checkpoints | `NR/integrity/integrity.json` | `status`, `failed_forecasts`, `checks.<score>.disagreements`, `run.checkpoint_sha256` |
| Recomputation: largest absolute difference 0.0 over 55,080 windows; targets and context means equal to the generator | `SR/score-recompute.json` | `max_abs_difference`, `windows`, `series` |
| NumPy 2.5.3, SciPy 1.18.1 and pandas 2.3.3; no uncommitted change; 540 and 209 checkpoint hashes; the inference HEAD | `SR/inference/provenance.json`, `NR/inference/provenance.json` | `packages`, `uncommitted_changes_at_inference`, `run.checkpoint_sha256`, `implementation_commit_at_inference` |
| 338 MB and about 0.9 GB of checkpoints, not in the tree | `NR/RESULTS-npm.md`, `SR/RESULTS-synthetic.md` "Files" | text |

### The three zero days and the post-hoc sensitivity (Section 10, the limitations, Appendix H, Table 21, the summary)

| Number | File | Key |
|---|---|---|
| 0 for all 209 series on 2026-07-12 and 2026-08-14; neighbours 4,059,870 and 10,123,968; 7,480,108 and 2,560,140; 2026-06-25: `aggregate-error` 0 between 9,475,033 and 7,909,626, 92 series at 0 against 98 and 121; no context day above 153 series at 0; the largest series never below 1,109,682; each day in one horizon-30 block | `NR/target-pull/daily_summary.csv` | `series_zero`, `total_downloads`, `largest_series_count`, `windows` by `date` (275 context days, 90 target days) |
| npm's records, the two earlier episodes with the maintainer's confirmation (the thread cited as `npm-community-150808`) | `docs/research/2026-10-16-npm-zero-days.md`; `docs/research/2026-10-16-standing-and-referee-read.md`, Part A, claim 6(d) | "What npm's own records say"; "The two earlier episodes"; the thread's dates |
| Addition 6; appended at 03:28 UTC; the sensitivity started at 03:21 UTC, before it | `PROTOCOL.md`, the heading of the dated addition of 2026-10-16 (npm zero days) and item 6; `NR/posthoc/sensitivity.json` `started_at` | the checker asserts both times |
| The 18 sensitivity rows under both removals; "re-scores 10,032 forecasts, none of the eighteen conclusions changes"; "re-scores 6,688 forecasts, one conclusion changes"; E06 adjusted $p$ 0.0599 and raw $p$ 0.0399 against 0.0119 and 0.00663; "lower on 110 of 209"; E04, E10, E16 from 90.24, 128.5, 110.3 to 159.3, 201.2, 183.4; the horizon-7 rows unchanged except adjusted $p$ | `NR/posthoc/sensitivity_inference.csv` | by `scenario` (`three_days`, `two_panel_wide_days`) and `id`: `mean_diff`, `wilcoxon_p`, `wilcoxon_p_bh`, `reject_bh_005`, `wins`, `larger_sum_favors`, `registered_*`, `mean_sign_changes`, `larger_sum_changes`, `rejection_changes`, `forecasts_rescored` |
| Computed 2026-10-16 at HEAD `e41fdf2`, no uncommitted change | `NR/posthoc/sensitivity.json` | `started_at`, `head`, `uncommitted_changes` |

### The post-hoc dynamic-occurrence analysis (Section 10's subsection, Table 8, Appendix Tables 25 and 26, Appendix G)

| Number | File | Key |
|---|---|---|
| The 24 npm rows DE01 to DE24 and the 12 grid rows DS01 to DS12: mean, interval, median, lower / tied / higher, adjusted $p$ (Table 8 holds the rows against the completed control and the model's registered hurdle; Table 25 the rows against `dynamic_count` and `hurdle_count_28`) | `DO/npm_inference.csv`, `DO/synthetic_inference.csv` | `mean_diff`, `mean_diff_ci_low`, `mean_diff_ci_high`, `median_diff`, `wins`, `ties`, `losses`, `wilcoxon_p_bh`, `reject_bh_005`, `larger_sum_favors`, `registered_id`; `declared_count` 24 and 12; `status` post-hoc |
| "removes four of the five rejections against the substitution" (E10, E16, S01, S03 no longer reject; S05, now DS09, still does); "never beats the model's own zero mass at q = 0.05"; adjusted $p$ 0.0787 to 0.838; means 26.03 to 93.25; Chronos-2 wrapper lower on 116 and 126 of 209; DS01 and DS05 at 0.0959, DS09 at 0.0439; grid means 0.0278 to 0.03462; vs the fixed hurdle lower on 124 to 138 of 209 and in 20 or 21 of 30 blocks at adjusted $p$ 0.00823; `dynamic_count` lower in 26 to 28 of 30 blocks | same | the same columns; `larger_sum_favors` |
| The fallback windows: 10 of 627 npm windows at each horizon, 501 of 1,620 grid windows | `DO/npm_occurrence.csv` (`stratum == all`), `DO/synthetic_occurrence.csv` (`cell_id == all`, horizon 30) | `windows`, `occurrence_fallback_windows` |
| Table 26 and the prose: the wrapper's zero-day part 0.3653 to 0.3879, its underprediction part 1.303 to 1.37 against 1.029 to 1.085 for the completed controls and 1.088 for `dynamic_count` | `DO/synthetic_accounting.csv` | `qscore9`, `zero`, `positive_over`, `positive_under` by `model` |
| Ran 2026-10-16 05:29 to 05:37 UTC at HEAD `ff8c5e8`, no uncommitted change; the checks (every checkpoint hash, both registered families rebuilt byte for byte, the Jeffreys wrapper reproducing the registered hurdle) | `DO/provenance.json`; `DO/RESULTS-dynamic-occurrence.md` "Checks" | `started_at`, `written_at`, `head`, `uncommitted_changes`; text |

### The citations (Section 7, the discussion, the limitations, `references.bib`)

The titles and full author lists of ten arXiv items were read from their abstract pages on 2026-10-16
by the paper's first writing (each entry's `note` says so): `meyer2025`, `schoess2026`, `chin2026`,
`ebrahim2026`, `islam2026`, `moghadasi2026`, `garza2026`, `damato2026`, `bai2026`, `exaone2026`. The
revision of 2026-10-16 added, from their abstract pages read the same day, `adler2025` (arXiv 2510.16060v2),
`wen2026` (2608.17299v1), `corani2026` (2606.24715v2), `brini2026` (2607.05291v1), `cherif2026`
(2607.19383v1), `li2026` (2605.26161v1), `qiao2026` (2602.12147v4, ICML 2026) and, from the Zenodo record
page, `ebrahim2026zenodo` (10.5281/zenodo.22681072, version 1.2.2); the npm community thread
`npm-community-150808` is cited as `docs/research/2026-10-16-standing-and-referee-read.md` records it
(opened 2025-02-06; the maintainer's reply of 2025-02-07), and the full texts of `garza2026` and
`islam2026` as the same document records them. `tsantilis2025` and `zodiac2026` are not on arXiv and keep
the surnames the record holds. The checker asserts that every key cited in `paper.tex` has an entry, that
each new identifier is in both the referee's read and the bib, and that each new entry records a read date.

### Numbers in `PAPER-SUMMARY.md`

All of its numbers are in the tables above or in the report's tables; the checker asserts its key figures
(209 series, 540, twelve of the eighteen, 7.6 million, the regime counts, the sensitivity sentence, the
dynamic-occurrence sentences) and that its abstract is the paper's abstract word for word, at most 300
words. The length figures in `PAPER-SUMMARY.md` and here are one pair by one method: running text with
tables, figures and comments removed, counted as whitespace-separated tokens over the expanded document
before `\appendix`: the paper's body 11,989 words with 748 words of captions, eight tables and three
figures; the report's body 4,222 words with 294 words of captions, four tables and two figures. They are
estimates, not asserted.

### Regeneration commands for the paper

| Command | Regenerates |
|---|---|
| `.\.venv\Scripts\python.exe scripts\study2_inference.py synthetic --run SR --out <dir>` | `SR/inference/` (needs the 540 checkpoints) |
| `.\.venv\Scripts\python.exe SR\recompute_scores.py SR --out <file>` | `SR/score-recompute.json` (needs the checkpoints) |
| `.\.venv\Scripts\python.exe scripts\study2_inference.py external_packages --run NR --out <dir>` | `NR/inference/` (needs the 209 checkpoints) |
| `.\.venv\Scripts\python.exe scripts\study2_integrity.py external_packages --run NR --out <dir>` | `NR/integrity/` (needs the checkpoints) |
| `.\.venv\Scripts\python.exe NR\target_days.py <signals.parquet> reports\study2-npm\panel\manifest.json --out <file>` | `NR/target-pull/daily_summary.csv` (needs the ignored target signals) |
| `.\.venv\Scripts\python.exe NR\posthoc\sensitivity_zero_days.py NR --out <dir>` | `NR/posthoc/sensitivity_*.csv`, `sensitivity.json` (needs the checkpoints) |
| `.\.venv\Scripts\python.exe DO\dynamic_occurrence.py --npm NR --synthetic SR --out <dir>` | the files under `DO/` (needs the 749 checkpoints) |
| `.\.venv\Scripts\python.exe NR\make_tables.py NR\inference`; `SR\make_tables.py SR\inference` | the tables of the two results documents (read-only) |
| `.\.venv\Scripts\python.exe paper/figures/make_figures.py` | the six figures under `paper/figures/` |
| `.\.venv\Scripts\python.exe paper/check_numbers.py` | nothing; asserts this table against the report, the paper and both summaries, recomputing the post-hoc stratum, empirical-hurdle and dynamic-count readings from the two `series_scores.csv` files |

## The paper extended with Study 3: the regime family on NYC 311 (added 2026-10-17)

On 2026-10-17 `paper/paper.tex` read six more files under `paper/sections/`: `study3-question.tex`,
`study3-design.tex`, `study3-panel.tex` and `study3-results.tex` in the body, after `study2-results.tex`, and
`study3-detail.tex` and `study3-appendix.tex` in the appendix, after `study2-appendix.tex`; the four body
files were removed in the reorganization later that day and the two appendix files remain. The regime
reading of `study2-results.tex` and its post-hoc dynamic-occurrence subsection are each one paragraph; their
detail and the dynamic-occurrence table moved to `study2-appendix.tex`, which `check_numbers.py` now reads
for those needles. `S3R` stands for `reports/study3-nyc311/run-2026-10-17`, `S3P` for
`reports/study3-nyc311/panel`, `S3` for `study/study3`. Every CSV is read with
`float_precision="round_trip"`, and values print as the results page prints them, by the same `g` and `pval`
functions as the Study 2 numbers.

Sections, in force: 1 to 6 the report's; 7 to 10 Study 2's question, design, npm panel and results; 11 to
14 Study 3's question, design, NYC 311 panel and results; 15 the discussion; 16 the limitations; 17 what is
registered and not run; 18 reproducibility; 19 the author's statement. Appendices A to D are the report's,
E the Study 2 design detail, F the npm panel detail, G the Study 2 runs and commands, H the Study 2 secondary
tables and post-hoc readings (now with the dynamic-occurrence table), I the Study 3 design and panel detail,
J the Study 3 run, commands and secondary tables. Tables in the body, in source order: 1 to 4 the report's;
5 `tab:s2ext`; 6 `tab:s2syn`; 7 `tab:s2parts`; 8 the family's structure (`tab:s3structure`); 9 the family's
results (`tab:s3family`); 10 the T2 summary (`tab:s3t2`). Figures in the body: 1 and 2 the report's; 3
`fig:s2npm`; 4 the family drawn (`fig:s3family`). In the appendix, Tables 11 to 15 as the report's 5 to 9,
Figure 5 the zero-fraction scatter; 16 `tab:s2family`, 17 `tab:s2synfamily`, 18 `tab:s2panel`, Figure 6
`fig:s2cells`, 19 `tab:s2regime`, 20 `tab:s2empirical`, 21 `tab:s2scaled`, 22 `tab:s2strata`, 23
`tab:s2sens`, 24 `tab:s2cells`, 25 `tab:s2scores`, 26 `tab:s2synscores`, 27 `tab:s2dyn` (moved from the
body), 28 `tab:s2dynrest`, 29 `tab:s2dynparts`; then Study 3: 30 the contexts at each origin
(`tab:s3context`), 31 the panel (`tab:s3panel`), 32 the direction of each test (`tab:s3direction`), 33 the
Brier pairs (`tab:s3brier`), 34 the fixed hurdle and the fourth cell per stratum (`tab:s3variants`), 35 the
pooled rows (`tab:s3pooled`), 36 the accounting parts per stratum (`tab:s3parts`), 37 the PIT
(`tab:s3pit`).

### The registration (Section 11, Section 12, Appendix I, the abstract)

| Number | File | Key |
|---|---|---|
| The addition's commit `3357d779...`, the protocol SHA-256 with the addition `05c7617b...`, "appended on top of commit `04e92c1`", Study 2's registration `df55867` | `S3R/results-provenance.json` `authority`; `S3/spec.json` `authority.appended_on_commit`, `study2_registration`; `S3/regime_comparisons.json` | the checker asserts the three files agree |
| H3's wording; "registered on 2026-10-16 as item 7"; "Appended at 2026-10-16 06:16 UTC" | `PROTOCOL.md`, the dated addition of 2026-10-16, item 7 | the hypothesis sentence is asserted against the protocol's text |
| The inventory of 9,496 cells captured 2026-09-14, 8,469 recognized | `S3/spec.json` `domain.primary.inventory` | `cells`, `recognized_board_frame`, `captured_at` |
| The strata bounds and window, selection seed 20261001, the context inspected | `S3/spec.json` `strata` | `definitions[].bounds`, `zero_fraction_window`, `selection_seed`, `context_inspected` |
| The calendar (cutoffs, 275, 305 and 335 context days, horizons, endpoint), the deadline 2026-10-27 23:59 UTC, the PyPI fallback | `S3/spec.json` `calendar`, `domain.fallback` | `cutoffs`, `horizons`, `endpoint`, `panel_deadline` |
| The dynamic law (discount 0.98, $a_B = b_B = 0.5$), 22 variants, the fourth cell | `S3/spec.json` `dynamic_count`, `variants`, `variant_definitions`; `S3R/integrity/integrity.json` `grid.models` | 19 declared variants plus the three raw deciles make the 22 forecast |
| The family: 36 tests, BH once at $q = 0.05$, 20,000 replicates, bootstrap seed 20261004, the fewer-than-ten rule, the predicted T1 signs, the zero rule | `S3/regime_comparisons.json` | `comparison_count`, `q`, `bootstrap_replicates`, `bootstrap_seed`, `minimum_complete_series_per_stratum`, `predicted_t1_sign`, `zero_method`, `all_zero_p`; Table 8's rows follow `comparisons[]` in order |
| The seeds (selection 20261001, forecasts 20261002, PIT 20261003, bootstrap 20261004) | `S3/spec.json` `seeds` | |

### The panel (Section 13, Appendix I)

| Number | File | Key |
|---|---|---|
| 276 attempts (275 census, 1 metadata), two invocations, 1,124 seconds, anonymous, the approval of 330 attempts and 3 hours in the author's words | `S3/nyc311_panel_status.json` `acquisition`, `approval` | `http_attempts`, `http_attempts_by_kind`, `invocations`, `seconds_used`, `anonymous`, `http_attempt_ceiling`, `invocation_seconds_ceiling`, `words` |
| 2,959,469 requests, 2,902,433 in frame cells, 49,356 unrecognized, 7,680 outside the frame; 275 days on 275 pages; the smallest day 6,216 on 2025-12-25 and the largest 22,805 on 2026-02-24; no gap | same, `census` | `requests`, `frame_requests`, `unrecognized_requests`, `outside_frame_requests`, `days`, `pages`, `smallest_day`, `largest_day`, `gap_days` |
| Frozen and verified 2026-10-16 08:04 UTC, inside the deadline, no target opened; 9,496 cells, 1,027 excluded at metadata, 8,469 eligible | same, `panel_verified_at`, `deadline_met`, `target_values_opened`, `frame` | `inventory_size`, `excluded_at_metadata`, `eligible_frame_size` |
| 2,002, 2,422 and 4,045 complete candidates, 100 taken each, 0 unfilled; 39 all-zero stratum windows and 19 all-zero contexts (Table 31) | same, `achieved_strata`, `selected_context_descriptors`; `S3P/manifest.json` `series[]` | `complete_candidates`, `achieved`, `unfilled`, `zero_fraction_one`, `context_total_zero`; the manifest's `stratum` and `zero_fraction` per series |
| The contexts at each origin (Table 30: all-zero, no request day in the last 28, fewer than two in the last 28) and the sentences read from it (74 and 4 at the first origin; 4 to 8, 72 to 74, 54 to 58, 15 to 19) | `S3R/RESULTS-nyc311.md`, "The contexts at each origin" (printed by `S3R/make_tables.py` from the signals, which are not in the tree) | the checker asserts the page's rows as text and derives the ranges from them |
| The target pull: 106 attempts of an approved 120, two invocations (100 attempts for 84 days from 03:16 to 03:32 UTC; 6 attempts for the last 6 days from 03:45:06 to 03:45:43 UTC), 16 repeats | `S3R/results-provenance.json` `pull`, `readiness.approval[1].words`; `S3R/target-pull/pull.json` `invocations` | `attempts`, `captures`, `days_exhausted`, `started_at`, `ended_at` |
| 983,482 requests, 947,751 in frame, 18,660 unrecognized, 17,071 outside the frame, no gap, fewest 8,849 on 2026-08-16, the separate recomputation | `S3R/results-provenance.json` `pull.target_census`, `pull.verification`; `S3R/target-pull/completeness.json` `target_census`, `verified` | |
| 47 days from 2026-08-31 to 2026-10-17 | arithmetic, asserted | |
| The metadata (read 2026-10-16 07:44 UTC, no license, attribution "311", the title), the redirect and the refusal of 2026-10-17, the two browser reads at 04:48 and 04:49 UTC, the terms in brief, the DST evidence (1 against 197 and 225; 796 against 528 and 339; 251 of 275 days) | `S3P/source-terms.md`; `S3R/results-provenance.json` `terms`; `S3/nyc311_panel_status.json` `source` | the checker asserts the record's phrases as text |
| The contamination ledger's three categories | `S3R/RESULTS-nyc311.md`, "The contamination ledger for NYC 311"; `PROTOCOL.md`, addition 7 | text |

### The run, the integrity check and the approvals (Section 14, Appendix I, Appendix J, Section 18)

| Number | File | Key |
|---|---|---|
| Started 2026-10-17 03:47 UTC, completed 04:03 UTC, 300 series, one invocation, 939 seconds inside the run, 956 for the whole process, budget 3,600, estimate 1,080, no failure, no resume, the implementation commit `00fd91d...` | `S3R/run.json` `started_at`, `completed_at`, `invocations[0]`, `failures`, `resumes`, `metadata.readiness`, `metadata.metadata.implementation_commit`; `S3R/results-provenance.json` `run.process_seconds`, `readiness.runtime_budget_seconds` | |
| RTX 4070 SUPER, driver 610.88, CUDA 12.8, PyTorch 2.11.0, batch size 1, peak reserved 2,948,595,712 bytes (the run and the smoke) | `S3R/run.json` `metadata.hardware`, `invocations[0].memory`; `S3/smoke_2026-10-17_00fd91d.json` `memory`, `at` | |
| 39,600 = 300 x 3 x 2 x 22; 0 disagreements on QScore9, the parts and the scaled score for all 39,600 and on the Brier score for 30,600; residuals 0.0, 7.1e-15, 2.8e-16; 300 checkpoint hashes; 10,800 windows of the two new variants; CRPS 30,600 certified, 9,000 without a law, 0 uncertified | `S3R/integrity/integrity.json` `grid`, `checks`, `run.checkpoint_sha256`, `status`, `failed_forecasts`; `S3R/inference/secondary_scores.csv` (`stratum == all`) `crps_*`; `S3R/RESULTS-nyc311.md` "Integrity" (the 10,800) | |
| The gate at 03:15, 03:44 and 03:46 UTC; the smoke at 01:56 UTC; the readiness approved 03:12:50 UTC; the inference 04:03 to 04:04 UTC and the integrity check 04:04 to 04:05 UTC; NumPy 2.5.3, SciPy 1.18.1, pandas 2.3.3; no uncommitted change | `S3R/results-provenance.json` `gate`, `smoke`, `readiness`, `inference`, `integrity`; `S3R/inference/provenance.json` `packages`, `uncommitted_changes_at_inference` | |
| The three approvals in the author's words, and the context pull's | `S3R/results-provenance.json` `readiness.approval[].words`; `S3/nyc311_panel_status.json` `approval.words` | quoted verbatim |
| 645 MB of checkpoints, not in the tree | `S3R/RESULTS-nyc311.md` "Files" | text |

### The family (Table 9, Figure 4, Table 10, Section 14, the abstract, the discussion, the summary)

| Number | File | Row and column |
|---|---|---|
| The 36 rows: the two means, the difference, the interval, the median, lower / tied / higher, the adjusted $p$, the verdict, the sign as predicted | `S3R/inference/inference.csv` | `variant_mean`, `reference_mean`, `mean_diff`, `mean_diff_ci_low`, `mean_diff_ci_high`, `median_diff`, `wins`, `ties`, `losses`, `wilcoxon_p_bh`, `reject_bh_005`, `median_as_predicted`, `contrast`; `n_entities` 100, `declared_count` and `bh_count` 36, `n_bootstrap` 20,000, `bootstrap_root` 20261004; the row order is the declaration's |
| 21 of 36 reject; 6 dense T1, 1 sparse T1, 0 very sparse T1, 14 T2; none against the prediction; no T1 median of the opposite sign | same | `reject_bh_005` by `stratum` and `contrast`; the sign of `median_diff` against `predicted_sign` |
| Dense: higher on 55 to 72 of 100; medians 0.004074 to 0.0127; means 0.01511 to 0.02219; control means 1.703 to 1.833; ties 0 to 2; "about one percent" (the ratio of the mean difference to the control's mean lies between 0.5 and 1.5 percent in every row) | same, R01, R03, R05, R07, R09, R11 | `losses`, `median_diff`, `mean_diff`, `reference_mean`, `ties` |
| Sparse: R21 (median -0.002116, 57 / 8 / 35, adjusted $p$ 0.00445), R23 (-0.0004938, 53 / 11 / 36, 0.0547), four medians exactly zero with 12 to 23 ties; means -0.004921 to 0.002242 against control means 0.3541 to 0.3668; 8 to 23 ties over the six rows | same, R13 to R23 odd | the same columns |
| Very sparse: 72 to 88 ties, means 0.0005086 to 0.002911, every interval including zero, the smallest adjusted $p$ 0.0547 at R25; 12 to 28 nonzero series | same, R25 to R35 odd | `ties`, `mean_diff`, `mean_diff_ci_low`, `mean_diff_ci_high`, `wilcoxon_p_bh`, `n_nonzero` |
| The one series, `["Sewer Maintenance","09 QUEENS"]`, most influential in all six very sparse T1 rows; its stratum | `S3R/inference/family_descriptors.csv` `most_influential_series`; `S3P/manifest.json` | |
| T2: 14 of 18 reject; dense lower on 72 to 87 with medians -0.05608 to -0.06753; sparse five of six (R16, R18, R20, R22, R24) lower on 53 to 58 with medians -0.001852 to -0.002646, R14 median zero at 0.138; very sparse R28, R32, R36 with 22 / 77 / 1 and median zero, R26, R30, R34 at 0.138 to 0.235 (Table 10) | `S3R/inference/inference.csv`, the T2 rows | the same columns |
| The direction of each test (Table 32): ties, nonzero, the two rank sums, the side favored, the raw $p$ recomputed; the rank sums 253 against 23 of R28, R32 and R36; the leans of R13, R15, R17, R19 and of the very sparse T1 rows | `S3R/inference/paired_entities.csv` `difference` by `id` (the checker ranks the absolute nonzero differences with average ranks and recomputes the two-sided approximate Wilcoxon $p$ with SciPy; every raw $p$ equals the saved one) | |
| The ties: 71 to 87 of the tied very sparse series with every decile at zero under both forecasts in every window; the completed control's deciles all zero in every window for 71 to 95 of the 100 very sparse series, `hurdle_dynamic`'s for 89; 2 to 5 of the tied sparse series all zero | the 300 checkpoints under `S3R/` (not in the tree; `rows[].forecast.deciles` by `series_id`, `model`, `horizon`, `cutoff`); the checker recomputes them when the checkpoints are present and records a skip otherwise | |

### The secondary tables (Section 14, the discussion, the limitations, Appendix J)

| Number | File | Row and column |
|---|---|---|
| The 36 Brier pairs (Table 33); dense T1 higher by 0.00668 to 0.009347 with every interval above zero; very sparse T1 lower on 68 to 82 of 100 with medians -0.002363 to -0.001625, raw $p$ at most 0.00165, means within 0.0013 of zero with every interval including zero; no tie in any T1 row | `S3R/inference/secondary_strata_contrasts.csv`, `metric == occurrence_brier`, matched to the family by `stratum`, `horizon`, `variant`, `reference` | `mean_diff`, `mean_diff_ci_low`, `mean_diff_ci_high`, `median_diff`, `wins`, `ties`, `losses`, `wilcoxon_p` |
| The fixed hurdle and the fourth cell against the control per stratum (Table 34): the fixed hurdle higher on 60 to 70 dense, 45 to 60 sparse, 20 to 23 very sparse against 5 to 9 lower with 69 to 73 tied and raw $p$ 0.00293 to 0.0254; the fourth cell 0.2944 to 0.325 above the control on dense series and higher on 70 to 91, within 0.004 of the control's mean elsewhere with 29 to 98 tied; the fourth cell against `hurdle_count_28` on dense series lower by 0.03591 to 0.0467 and on 62 to 73 of 100 | same, `metric == qscore9`, `variant` `<model>_hurdle` and `<model>_occurrence_model_size_count`, `reference` `<model>_completed` and `hurdle_count_28` | the same columns |
| The pooled rows P01 to P18 (Table 35): the fixed hurdle's mean above its control's with more series higher than lower, below `hurdle_count_28`'s with more lower than higher, each raw model below `local_mean_28` with 128 to 161 lower against 124 to 157 higher; every within-table adjusted $p$ below 0.005 | `S3R/inference/secondary_pooled_study2_form.csv`, `metric == qscore9` | `variant_mean`, `reference_mean`, `mean_diff`, the interval, `median_diff`, `wins`, `ties`, `losses`, `wilcoxon_p_bh_within_table` |
| The accounting of the T1 difference per stratum (Table 36): the dense zero-day part 0.009693 to 0.03213 in every row; the sparse zero-day part positive for Chronos-2 and negative for the TimesFM models with the underprediction part of the opposite sign; every very sparse part within 0.006 of zero | `S3R/inference/secondary_accounting.csv`, rows by `stratum`, `horizon`, `model`: `<model>_hurdle_dynamic` minus `<model>_completed` on `qscore9`, `zero`, `positive_over`, `positive_under` (`parts_sum` and `max_abs_window_residual` asserted) | |
| The PIT at horizon 30 per stratum (Table 37): 0.064 to 0.117 in a tenth; the completed controls' last tenth 0.064 to 0.075 on the very sparse series against 0.097 to 0.099 for `hurdle_dynamic`; 9,000 target days per row | `S3R/inference/pit_histograms.csv`, `horizon == 30` | `fraction01` to `fraction10`, `n_values` |

### Numbers in `PAPER-SUMMARY.md`

Its abstract is the paper's word for word, at most 300 words, and the checker asserts its Study 3 figures
(21 of 36, 72 to 88 ties, 14 of 18, 956 seconds, the per-stratum family of 36 tests, the dense and sparse
sentences, the commit `3357d77`). The length figures there and here are by the revision's method, running
text with tables, figures and comments removed, counted as whitespace-separated tokens over the expanded
document before `\appendix`: the body 15,815 words with 970 words of captions, ten tables and four figures,
against 11,938 words, 761 of captions, eight tables and three figures for the revision of 2026-10-16 by the
same count (that revision reported 11,990 and 748 by its own run of the method); the appendix 8,446 words,
1,434 of captions, 27 tables and two figures; the report's body 4,177 words. They are estimates, not
asserted.

### Regeneration commands for Study 3

| Command | Regenerates |
|---|---|
| `.\.venv\Scripts\python.exe scripts\study3_inference.py --run S3R --out <dir>` | `S3R/inference/` (needs the 300 checkpoints) |
| `.\.venv\Scripts\python.exe scripts\study3_integrity.py --run S3R --out <dir>` | `S3R/integrity/` (needs the checkpoints) |
| `.\.venv\Scripts\python.exe S3R\make_tables.py S3R` | the tables of `S3R/RESULTS-nyc311.md`, the direction check and the zero-context tables (the last need the ignored signals) |
| `.\.venv\Scripts\python.exe paper/figures/make_figures.py` | the six figures under `paper/figures/`, Figure 4 from `S3R/inference/inference.csv` |
| `.\.venv\Scripts\python.exe paper/check_numbers.py` | nothing; asserts every number above against the files named, recomputing the direction table from the paired differences and the tie classification from the checkpoints when they are present |

The pull, the run, the gate and the smoke are not to be repeated; their commands are in Appendix J and in
`S3R/results-provenance.json`.

## The paper organized by question (2026-10-17)

On 2026-10-17 the paper was reorganized by question at a body of about twelve pages. `paper/paper.tex` now
reads nine body sections under `paper/sections/` (`01-introduction.tex` to `09-reproducibility.tex`), the
author's statement from `paper/shared/`, and an appendix made of `sections/app-study1.tex` (Study 1 in
detail, with the report's Tables 1 to 4 unchanged in every entry), the report's frozen appendix files
`shared/app-design.tex`, `shared/app-v1.tex` and `shared/app-tables.tex`, the Study 2 and Study 3 detail and
table files (`study2-design-detail.tex`, `study2-panel-detail.tex`, `study2-appendix.tex`,
`study3-detail.tex`, `study3-appendix.tex`), `sections/app-runs.tex` (the run record and the commands) and
`shared/app-repro.tex`. The report (`main.tex` with its `shared/` files) is unchanged. The body sections
`study2-question.tex`, `study2-design.tex`, `study2-panel.tex`, `study2-results.tex` and the four Study 3
body files were removed; their tables moved whole into the appendix files (the families E01 to E18 and S01
to S06 and the accounting parts into `study2-appendix.tex`; R01 to R36, the family's structure and the
family figure into `study3-appendix.tex`), and their prose was condensed into the body or moved into the
detail appendices. Every section above this one still describes the files its numbers come from; this
section gives the sources of what is new.

The body's tables and figures, in order: Figure 1 the design at a glance (`fig-design`), Figure 2 the
completion floor (`fig-floor`), Table 1 the panels (`tab:panels`), Table 2 the registration ledger
(`tab:ledger`), Table 3 the raw deciles against the local mean (`tab:raw`), Figure 3 the mean and the typical
series (`fig-mean-typical`), Figure 4 the signature figure (`fig-signature`), Table 4 the occurrence
substitution (`tab:occ`), Table 5 the positive-law contrasts (`tab:pos`). The appendix keeps the report's and
the earlier paper's tables under their labels, the Study 3 family as a sideways table, and the five appendix
figures (`fig-paired-differences`, `fig-posthoc-zero-fraction-h30`, `fig-s2-npm-paired-differences`,
`fig-s2-synthetic-cells`, `fig-s3-nyc311-family`). The checker's expanded-paper check now covers the whole
paper, so a sentence that may sit anywhere is asserted against `paper.tex` expanded.

### The completion floor (Section 3, Section 5, the abstract, the discussion)

The formula: `pulsegraph/study2/distributions.py`, `complete`, sets the tail scale to `max(1, q9 - q8)`;
when every repaired decile is below 0.5 the completed law's probability of a positive day is
`0.1 exp(-(0.5 - q9))`, between `0.1 exp(-0.5) = 0.0607` and 0.1. The counts "580, 544 and 588 of the 600",
"150, 62 and 230 of 600", "2, 0 and 0" and "median occurrence probability of 0.0607 to 0.0609 against 0.0172
for the dynamic hurdle" are counted from the 300 NYC 311 checkpoints under `S3R/` (the release asset):
for each row whose model is `<m>_completed`, the first lead's law `rows[].forecast.distributions[0]`, on
the floor when `deciles[-1] < 0.5`, with the occurrence `0.1 * exp(-(0.5 - deciles[-1]) / tail_scale)`; the
dynamic hurdle's `p` is read from the `<m>_hurdle_dynamic` rows' first lead. The checker recomputes them when
the checkpoints are present and records a skip otherwise; the paper states that provenance. Figure 2 is
drawn from the formula alone.

### The body tables (Tables 3, 4 and 5)

Every row of the three tables is regenerated by the checker in the printed form:

- Table 3: the GitHub rows from `R/inference/inference.csv` (`mean_diff` 3 decimals, `median_diff` 4,
  `repo_win_rate` times 300), the npm rows from `reports/study2-npm/run-2026-10-15/inference/inference.csv`
  (E03, E06, E09, E12, E15, E18; the side of the larger rank sum from `paired_entities.csv`), the NYC 311
  rows from `S3R/inference/secondary_pooled_study2_form.csv` (`metric == qscore9`, `reference ==
  local_mean_28`; `wilcoxon_p_bh_within_table`; the rank-sum side from `series_scores.csv`).
- Table 4: for each panel, stratum, horizon and model the paired per-series differences of `qscore9`,
  `occurrence_brier` and `discrete_crps` from the run's `inference/series_scores.csv` (npm: `<m>_hurdle`
  minus `<m>_completed` within the manifest's strata; NYC 311: `<m>_hurdle_dynamic` minus `<m>_completed`,
  with the status from `S3R/inference/inference.csv`; the grid: replicate-block means at horizon 30 of
  `<m>_hurdle` minus `<m>_completed`, with the status from the synthetic `inference.csv`); the TSB rows from
  the benchmark's `npm_contrasts.csv`, `nyc311_contrasts.csv` and `grid_contrasts.csv` (`variant ==
  tsb_hurdle`, `reference == <m>_completed`, the three metrics).
- Table 5: ranges over the three models of the lower / tied / higher counts and the medians, from the
  same `series_scores.csv` files (the model's hurdle against `hurdle_count_28` and `hurdle_empirical_28`; the
  T2 pairs and the fixed hurdle against `hurdle_empirical_28` on NYC 311; the fourth cell against the control
  and against `hurdle_count_28` on NYC 311; `dynamic_count` against each control), from the benchmark's
  contrast tables for the fourth cell on npm and the grid (`variant` ending `occurrence_model_size_count`)
  and for the TSB hurdle against `hurdle_count_28`, and from the registered inference tables for the
  verdicts.

### The secondary scores beside the primary (Sections 5 and 6)

"lower on 85, 64 and 70 at horizon 7" and "on the discrete CRPS on 82, 70 and 70" (npm sparse): the Brier
and CRPS columns of Table 4. "lower than the control's on 57 to 62 of the 100 dense series at horizon 30"
and "at horizon 7 it is lower on only 32 to 46": the npm dense Brier counts of Table 4. "by 0.00668 to
0.009347 on the mean with every interval above zero" (NYC 311 dense Brier): `S3R/inference/`
`secondary_strata_contrasts.csv`, as before. "lower Brier score on 68 to 82 of the 100 series in every T1
row, with medians from -0.002363 to -0.001625 and raw p at most 0.00165" and "within 0.0013 of zero": as
before (Appendix Table of the Brier pairs). The fourth cell's Brier counts "68, 62 and 54 of 100 dense npm
series and 19, 23 and 19 of 30 blocks" (a week) and "42, 43 and 38 of 100 and 15, 13 and 12 of 30" (a
month): the benchmark's contrast tables, `variant` ending `occurrence_model_size_count`, `reference ==
hurdle_count_28`, `metric == occurrence_brier`, `wins`.

### The post-hoc benchmark in the body (Sections 3, 5 and 6, Tables 4 and 5)

From `reports/study2-posthoc-intermittent-baselines/{npm,nyc311,grid}_contrasts.csv`, `variant ==
tsb_hurdle`: "77, 61 and 74 of 100 at a week" (sparse npm, `reference == <m>_completed`, `qscore9`, `wins`);
"level with the count hurdle, 49 lower against 49 higher" (sparse npm at horizon 7, `reference ==
hurdle_count_28`); "beaten by the dynamic count on the grid in 23 and 28 of 30 blocks" (`reference ==
dynamic_count`, `losses` at horizons 7 and 30). The fourth cell on npm and the grid: "higher than the
control on 79 to 94 of the 100 dense npm series with medians of 0.39 to 0.56" and "higher on 19 to 28 of
the 30 grid blocks" (`reference == <m>_completed`, `losses`, `median_diff` to two significant figures).
The discussion's "57 to 66 of the 100 dense npm series and on 24 or 25 of the 30 grid blocks": the fixed
hurdle against the completed control at horizon 30, `losses`, from the npm `series_scores.csv` by stratum
and the synthetic replicate blocks.

### The signature figure (Figure 4, Section 5)

`paper/figures/make_figures.py`, `binned_shares`: per bin of the manifest's `zero_fraction` (bins 0, 0.1,
0.3, 0.5, 0.7, 0.9, 0.97, 1), the pairs (three models times the series) where the substitution's score is
below, equal to or above the control's, from the two runs' `series_scores.csv`; the grid by zero
probability from the synthetic `series_scores.csv` and `secondary_cells_contrasts.csv`. The caption's
"68 of 105 and 139 of 195", "40 of 84 and 108 of 216 with 6 and 38 tied" and "183 of 186 ... on 148" are the
function's values at horizon 7, asserted by the checker through the same function.

### The ledger, the run record and the length (Tables 2 and the appendix)

The ledger's dates and commits: `git log --format=%h %cs -- PROTOCOL.md` (`5f01769` 2026-09-12, `df55867`
2026-09-14, `8db0d73` 2026-10-12, `5be2ce9` 2026-10-15, `1c09ac8` and `3357d77` 2026-10-16); the sentence
on the four weeks without work: `PROTOCOL.md`, the addition of 2026-10-12, stated once in the paper. The
run record: `R/run/run.json` and the three runs' `run.json` and readiness records, as before. The citations
added on 2026-10-17 record in `references.bib` the page read and its date. The length by the revision's
method (the expanded paper before `\appendix`, comments, floats and commands removed, captions counted
apart) is computed by the checker and must agree with `PAPER-SUMMARY.md` within 25 words.

### Regeneration

| Command | Regenerates |
|---|---|
| `.\.venv\Scripts\python.exe paper\figures\make_figures.py` | all nine figures under `paper/figures/`, the four body figures from the panel status files, the per-series scores and the completion formula |
| `.\.venv\Scripts\python.exe paper\check_numbers.py` | nothing; asserts every number in the paper, regenerating the three body tables and recomputing the floor counts from the checkpoints when present |

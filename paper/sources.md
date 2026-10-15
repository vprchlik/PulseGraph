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
`study2-results-placeholder.tex` are written to be `\input` by `main.tex` in the paper's extension; until
then `main.tex` does not read them. `check_numbers.py` reads them like `main.tex` (whitespace collapsed)
and asserts every figure below. `S2` stands for `study/study2`, `N` for `reports/study2-npm/panel`. The
results placeholder holds no number from a run: every cell is `tbd`, and the checker asserts that its
table rows are the declared tuples with `tbd` cells and that no decimal figure appears in it.

### The question (`study2-question.tex`)

| Number or fact | File | Where |
|---|---|---|
| Registration 2026-09-14 at `df55867c982dfe2bb6e1152ec8ae93e3cd228c45`; full-protocol SHA-256 `33cefd8e...` | `S2/external_packages_spec.json` `protocol_commit`, `protocol_sha256`; `PROTOCOL.md` "Study 2 — dated addition, 2026-09-14"; `git log -- PROTOCOL.md` (`df55867` dated 2026-09-14) | as in `main.tex` Section 8 |
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
| CRPS tolerance 1e-8 by k = 1,000,000; the availability rule | `S2/external_packages_spec.json` `crps`; `PROTOCOL.md` "Discrete CRPS availability — dated addition, 2026-10-15" | `tolerance`, `max_k`; item 5 |
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

### The results placeholder (`study2-results-placeholder.tex`)

Tables `tab:s2ext` and `tab:s2syn` list the tuples of `S2/external_packages_comparisons.json` and
`S2/synthetic_comparisons.json` with every result cell `tbd`; the denominators 209 and 30 are `series` in
`S2/npm_panel_status.json` and `replicates_per_cell` in `S2/grid_manifest.json`; "16 forecasts per origin"
is the count of `variants` in `S2/external_packages_spec.json`; "540 series" is `n_series` in the grid
manifest. No other figure appears; the checker asserts the absence of decimal numbers.

### Regeneration commands for the Study 2 files

| Command | Regenerates |
|---|---|
| `.\.venv\Scripts\python.exe scripts\study2_ingest.py npm inventory ...` and `npm panel ...` (README) | `data\raw\study2\npm\inventory.json`, `inventory.walk.json`, `N\manifest.json`, `N\selection.json`, `S2\npm_panel_status.json` and the ignored `context.parquet` (the frozen pull, not to be repeated; a complete walk and pull are reused from the saved captures without requests) |
| `.\.venv\Scripts\python.exe scripts\study2_evidence.py ...` (README) | `S2\acquisition_status.json` |
| `.\.venv\Scripts\python.exe paper/check_numbers.py` | nothing; asserts this table against the sections |

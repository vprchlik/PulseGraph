# Study 2, external component on npm: the registered family E01 to E18

Protocol: Study 2 registered at `df55867c982dfe2bb6e1152ec8ae93e3cd228c45` (`PROTOCOL.md` at that commit,
SHA-256 `33cefd8e34fea973e6747d1ba3fe565051e215c5d1b7f6553b266c1be7a66360`), sections "Scores and the single
external-domain confirmatory family" and "Calendar and information boundary". The family is E01 to E18 with
one Benjamini-Hochberg correction, by the dated addition of 2026-10-12, items 1 and 3 (commit
`8db0d73381e89a61b0ea22e6a8cb2b6e569725c9`). E19 to E54 (NYC 311 and Wikipedia) are kept whole for a later
run and are not run here. Discrete CRPS availability follows the dated addition of 2026-10-15.
Implementation: `3057b16dbd2f9b218449352717ef4adabc2f72f7`.

Gate: pass, twice, with the author's signed readiness and the GPU smoke at the implementation commit. The
readiness was approved 2026-10-15 23:09:06 UTC, with target access for at most 300 HTTP attempts and a
runtime budget of 3,600 seconds against an estimate of 1,741. The smoke is
`study/study2/smoke_2026-10-15_3057b16.json`: passed, peak reserved VRAM 2,948,595,712 bytes, CRPS maximum
residual bound 4.84e-9. The first gate, at 23:14:15 UTC, came before every target request. The second, at
23:26:40 UTC, admitted the pull's signals only together with their completeness document. The run's
readiness is tracked as `study/study2/external_packages_readiness_2026-10-15.json`.

Targets: the 209 manifest series' download ranges for 2026-06-03 to 2026-08-31 were requested once each from
`api.npmjs.org`, from 23:14:58 to 23:26:22 UTC, 3 seconds apart: 209 attempts and 209 answers, with no retry
and no failure. Every answer names its package and the requested bounds and lists each of the 90 days once
with a nonnegative integer count; nothing is zero-filled. The signals join these days to the frozen context,
unchanged and not re-requested (`target-pull/completeness.json`, `target-pull/pull.json`).

Run: complete. All 209 of 209 series ran in one invocation, 23:27:10 to 23:38:42 UTC: 692 seconds inside the
run and 699 for the whole process, against the budget of 3,600. Failures 0, resumes 0. RTX 4070 SUPER, driver
610.88, CUDA 12.8, PyTorch 2.11.0+cu128, batch size 1, peak reserved VRAM 2,948,595,712 bytes. The weights
were read from the local cache with the Hugging Face offline variables set. 20,064 forecasts: 209 series × 3
origins × 2 horizons × 16 variants.

Integrity: the committed `scripts/study2_integrity.py` passes on this directory. All 209 checkpoints match
the SHA-256 values in `run.json`, and every registered window appears exactly once. For all 20,064 forecasts,
QScore9, its three accounting parts, the context-scaled QScore9 and, where a count law is saved, the
occurrence Brier score were recomputed from the saved deciles, targets and laws, with 0 disagreements. The
largest absolute residuals are 0.0 for QScore9 and the scaled score, 1.9e-9 for the parts (at download scales
in the millions) and 2.8e-16 for the Brier score. `check_directions.py` reproduces all 18 raw p-values exactly
from `inference/paired_entities.csv`, and the direction of each test from its rank sums.

## A note on the source data, made after the run

On two target days, 2026-07-12 and 2026-08-14, the download API reports 0 for every one of the 209 series. The
panel's total on the days either side is 4,059,870 and 10,123,968 for the first, and 7,480,108 and 2,560,140
for the second. On 2026-06-25 the largest series, `aggregate-error`, reads 0 between 9,475,033 and
7,909,626. No day of the 275-day context reads zero for every series. These zeros look like gaps in npm's
own counts rather than days without downloads, but that was not verified against any other source
(`target-pull/daily_summary.csv`, written by `target_days.py`).

The registered completeness check verifies that every day is present once with a nonnegative integer count.
It does not test for a source-wide zero, so these days entered the run as explicit zeros. Each falls in one
horizon-30 target window, one per origin: 2026-06-25 in the window from 2026-06-03, 2026-07-12 in the window
from 2026-07-03, and 2026-08-14 in the window from 2026-08-02. No horizon-7 window contains any of them. The
protocol keeps explicit zero counts but requires verified exposure on every day and does not zero-fill
outages ("Completeness means every required calendar day has verified exposure", section "Domains, frame
and selection").
Whether these days meet that requirement is not decided here. Everything below is the registered analysis of
the data as the source served it, unchanged.

## The design, in brief

The panel is npm's frozen achieved panel: `reports/study2-npm/panel/manifest.json`, `selection.json` and
`study/study2/npm_panel_status.json`. The strata are the context-zero fraction over 2026-03-05 to 2026-06-02:
dense [0, 0.5), sparse [0.5, 0.9) and very sparse [0.9, 1]. The protocol aims at 100 series a stratum and
retains min(100, N_s), with no transfer between strata. Only 9 of the 9,998 complete candidates reach a zero
fraction of 0.9, so the very-sparse stratum has 9 series and the panel 209. Every table that splits by
stratum states its n.

| Stratum (context-zero fraction, 2026-03-05 to 2026-06-02) | Complete candidates | Series in the panel | Unfilled of 100 |
|---|---|---|---|
| dense, [0, 0.5) | 2,431 | 100 | 0 |
| sparse, [0.5, 0.9) | 7,558 | 100 | 0 |
| very sparse, [0.9, 1] | 9 | 9 | 91 |
| all | 9,998 | 209 | 91 |

The calendar is the registered one: context from 2025-09-01, cutoffs 2026-06-03, 2026-07-03 and 2026-08-02
(275, 305 and 335 context days), horizons 7 and 30, and the endpoint 2026-08-31, in UTC day labels. All 16
registered variants were forecast at every origin and horizon. They are the three frozen foundation models
(Chronos-2, TimesFM 3 and TimesFM 2.5), each raw, completed and hurdle-wrapped, and the seven baselines.

The series differ in scale by orders of magnitude. Over the last 28 context days, the median series averages
2.0 downloads a day, the second largest 13,014 and `aggregate-error` 7,637,136. With equal series weights on
the unscaled score, that one series carries every mean difference below. The signed-rank test is
rank-based, and the context-scaled QScore9 is the registered scale-free secondary.

How to read the tables:

- **Differences** are model minus reference QScore9. QScore9 is a loss, so a negative difference favors the
  model variant and a positive one favors the reference.
- **The entity is the series.** Origins are averaged within series and horizon, and the 209 series weigh
  equally.
- **Intervals** are pointwise 95% percentile intervals from 20,000 series bootstrap replicates. The
  per-comparison seeds are in `inference/provenance.json`.
- **Raw p** is from a two-sided approximate Wilcoxon signed-rank test over the 209 series differences, with
  zero differences omitted. **BH p** applies Benjamini-Hochberg once over the eighteen, at q = 0.05. The
  signed-rank test's location reading needs symmetry; it is not a test of the mean difference.
- **"Lower / tied / higher"** counts the series where the model's score is below, equal to or above the
  reference's.
- Inference is conditional on the fixed dates.

## The registered family E01 to E18

| ID | Model variant | Reference | Horizon | Model mean | Reference mean | Mean difference | 95% interval | Median difference | Lower / tied / higher (of 209) | Raw p | BH p | BH rejects at 0.05 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E01 | `chronos2_hurdle` | `chronos2_completed` | 7 | 4652 | 4500 | 152 | [0.1846, 455.2] | -0.01376 | 121 / 2 / 86 | 0.146 | 0.203 | no |
| E02 | `chronos2_hurdle` | `hurdle_count_28` | 7 | 4652 | 9742 | -5090 | [-15,175, -31.08] | -0.01587 | 129 / 12 / 68 | 8.26e-12 | 3.72e-11 | yes |
| E03 | `chronos2_raw` | `local_mean_28` | 7 | 4500 | 7384 | -2884 | [-8601, -17.33] | 0.007856 | 92 / 0 / 117 | 0.529 | 0.596 | no |
| E04 | `chronos2_hurdle` | `chronos2_completed` | 30 | 4316 | 4226 | 90.24 | [0.2273, 269.7] | -0.0002469 | 105 / 2 / 102 | 0.374 | 0.449 | no |
| E05 | `chronos2_hurdle` | `hurdle_count_28` | 30 | 4316 | 10,878 | -6563 | [-19,596, -30.03] | -0.06173 | 150 / 9 / 50 | 1.18e-21 | 7.06e-21 | yes |
| E06 | `chronos2_raw` | `local_mean_28` | 30 | 4226 | 8959 | -4734 | [-14,149, -15.84] | -0.002372 | 112 / 0 / 97 | 0.00663 | 0.0119 | yes |
| E07 | `timesfm3_hurdle` | `timesfm3_completed` | 7 | 4326 | 4149 | 176.9 | [0.2669, 529.4] | 0.001058 | 94 / 8 / 107 | 0.183 | 0.236 | no |
| E08 | `timesfm3_hurdle` | `hurdle_count_28` | 7 | 4326 | 9742 | -5416 | [-16,153, -31.67] | -0.007407 | 116 / 18 / 75 | 1e-08 | 3.61e-08 | yes |
| E09 | `timesfm3_raw` | `local_mean_28` | 7 | 4149 | 7384 | -3235 | [-9650, -18.24] | -0.002297 | 112 / 1 / 96 | 0.0292 | 0.0438 | yes |
| E10 | `timesfm3_hurdle` | `timesfm3_completed` | 30 | 4087 | 3958 | 128.5 | [0.5058, 383.8] | 0.00321 | 81 / 8 / 120 | 0.00108 | 0.00215 | yes |
| E11 | `timesfm3_hurdle` | `hurdle_count_28` | 30 | 4087 | 10,878 | -6792 | [-20,280, -31.3] | -0.0716 | 161 / 17 / 31 | 1.77e-26 | 3.19e-25 | yes |
| E12 | `timesfm3_raw` | `local_mean_28` | 30 | 3958 | 8959 | -5001 | [-14,947, -16.86] | -0.005016 | 125 / 1 / 83 | 1.48e-05 | 3.82e-05 | yes |
| E13 | `timesfm2p5_hurdle` | `timesfm2p5_completed` | 7 | 3895 | 3641 | 253.9 | [0.5046, 759.9] | -0.002116 | 109 / 3 / 97 | 0.593 | 0.628 | no |
| E14 | `timesfm2p5_hurdle` | `hurdle_count_28` | 7 | 3895 | 9742 | -5847 | [-17,446, -30.83] | -0.006349 | 115 / 7 / 87 | 8.87e-06 | 2.66e-05 | yes |
| E15 | `timesfm2p5_raw` | `local_mean_28` | 7 | 3641 | 7384 | -3743 | [-11,179, -17.41] | 0.01696 | 84 / 1 / 124 | 0.746 | 0.746 | no |
| E16 | `timesfm2p5_hurdle` | `timesfm2p5_completed` | 30 | 3960 | 3850 | 110.3 | [0.6883, 328.7] | 0.0009877 | 101 / 1 / 107 | 0.0169 | 0.0276 | yes |
| E17 | `timesfm2p5_hurdle` | `hurdle_count_28` | 30 | 3960 | 10,878 | -6918 | [-20,665, -29.9] | -0.06938 | 160 / 9 / 40 | 1.97e-24 | 1.77e-23 | yes |
| E18 | `timesfm2p5_raw` | `local_mean_28` | 30 | 3850 | 8959 | -5109 | [-15,279, -15.49] | -0.003695 | 113 / 1 / 95 | 0.000905 | 0.00204 | yes |

Twelve of the eighteen tests reject at BH q = 0.05: ten in favor of the model variant and two against it.
The direction of each test is the side with the larger signed-rank sum:

| ID | Nonzero | Rank sum, model lower | Rank sum, reference lower | Larger sum favors | Raw p recomputed | Raw p saved |
|---|---|---|---|---|---|---|
| E01 | 207 | 12,017.0 | 9,511.0 | model | 0.146 | 0.146 |
| E02 | 197 | 15,227.0 | 4,276.0 | model | 8.26e-12 | 8.26e-12 |
| E03 | 209 | 11,523.0 | 10,422.0 | model | 0.529 | 0.529 |
| E04 | 207 | 9,997.5 | 11,530.5 | reference | 0.374 | 0.374 |
| E05 | 200 | 17,885.0 | 2,215.0 | model | 1.18e-21 | 1.18e-21 |
| E06 | 209 | 13,349.0 | 8,596.0 | model | 0.00663 | 0.00663 |
| E07 | 201 | 9,052.0 | 11,249.0 | reference | 0.183 | 0.183 |
| E08 | 191 | 13,551.5 | 4,784.5 | model | 1e-08 | 1e-08 |
| E09 | 208 | 12,763.0 | 8,973.0 | model | 0.0292 | 0.0292 |
| E10 | 201 | 7,450.5 | 12,850.5 | reference | 0.00108 | 0.00108 |
| E11 | 192 | 17,474.0 | 1,054.0 | model | 1.77e-26 | 1.77e-26 |
| E12 | 208 | 14,632.0 | 7,104.0 | model | 1.48e-05 | 1.48e-05 |
| E13 | 206 | 10,203.0 | 11,118.0 | reference | 0.593 | 0.593 |
| E14 | 202 | 13,947.5 | 6,555.5 | model | 8.87e-06 | 8.87e-06 |
| E15 | 208 | 11,150.0 | 10,586.0 | model | 0.746 | 0.746 |
| E16 | 208 | 8,791.0 | 12,945.0 | reference | 0.0169 | 0.0169 |
| E17 | 200 | 18,410.0 | 1,690.0 | model | 1.97e-24 | 1.97e-24 |
| E18 | 208 | 13,752.0 | 7,984.0 | model | 0.000905 | 0.000905 |

The registered question has two parts, and the domain adds a third.

- **Does replacing a foundation model's zero mass with the context-only occurrence probability, keeping its
  positive law, lower QScore9?** These are E01, E04, E07, E10, E13 and E16, each hurdle variant against its
  completed-unwrapped control. No comparison favors the hurdle variant at BH q = 0.05. Two reject against it,
  both at horizon 30: TimesFM 3 (E10; hurdle higher in 120 of 209 series; BH p 0.0022) and TimesFM 2.5 (E16;
  higher in 107; BH p 0.028). The other four are not rejected (BH p 0.20 to 0.63). Not rejecting is not
  equivalence.
  - Every mean difference is positive, +90 to +254, with every interval above zero. The concentration
    table below shows these means belong to the largest series, not to the typical one. Without
    `aggregate-error` they fall to +0.63 to +1.6, and the median differences lie within 0.014 of zero.
  - The context-scaled QScore9, a registered secondary, favors the hurdle variant at horizon 7 for all three
    models (E01 −0.022, E07 −0.0067, E13 −0.0061; every interval below zero). At horizon 30 every interval
    includes zero.
- **Does the foundation model's positive component improve on a fixed count hurdle?** These are E02, E05,
  E08, E11, E14 and E17, each hurdle variant against `hurdle_count_28`. All six reject in favor of the hurdle
  variant (BH p 3.2e-25 to 2.7e-5). The hurdle variant is lower in 115 to 161 of the 209 series, with median
  differences −0.0063 to −0.072. The two sides share the same occurrence probability, and the Brier
  difference is exactly zero for every series. The gain is therefore in the positive law. The context-scaled
  differences are −0.12 to −0.15, every interval below zero. On the synthetic grid, the same comparison went
  against the hurdle variant or did not reject (S02, S04, S06).
- **Does the raw foundation model beat the local mean, Study 1's question, on this domain?** These are E03,
  E06, E09, E12, E15 and E18, each raw variant against `local_mean_28`. Four reject in favor of the model:
  Chronos-2 at horizon 30 (E06), TimesFM 3 at both horizons (E09, E12) and TimesFM 2.5 at horizon 30 (E18).
  Chronos-2 and TimesFM 2.5 at horizon 7 (E03, E15) are not rejected (BH p 0.60 and 0.75). The mean
  differences, −2,884 to −5,109, come almost entirely from `aggregate-error`.

## Secondary results

None of the tables below carries a multiplicity adjustment, and none replaces the family.

### Skill and concentration

| ID | Mean skill | Median skill | Skill defined (of n) | Top-five share of positive gains | Mean difference, one series left out: range | Series whose omission moves the mean most | Its difference |
|---|---|---|---|---|---|---|---|
| E01 | 0.01462 | 0.008364 | 208 of 209 | 0.562 | [0.6334, 152.7] | `aggregate-error` | 31,636 |
| E02 | 0.1029 | 0.02081 | 208 of 209 | 0.995 | [-5114, -58.94] | `aggregate-error` | -1,051,548 |
| E03 | 0.02627 | -0.00659 | 208 of 209 | 0.996 | [-2898, -34.85] | `aggregate-error` | -595,555 |
| E04 | -0.002001 | 2.652e-05 | 208 of 209 | 0.807 | [0.9125, 90.77] | `aggregate-error` | 18,671 |
| E05 | 0.1056 | 0.03989 | 208 of 209 | 0.997 | [-6594, -60.79] | `aggregate-error` | -1,358,931 |
| E06 | 0.03024 | 0.002699 | 208 of 209 | 0.998 | [-4756, -34.65] | `aggregate-error` | -982,126 |
| E07 | -0.005039 | -0.001273 | 208 of 209 | 0.632 | [0.843, 177.8] | `aggregate-error` | 36,796 |
| E08 | 0.09919 | 0.008249 | 208 of 209 | 0.996 | [-5442, -59.73] | `aggregate-error` | -1,119,450 |
| E09 | 0.03866 | 0.005494 | 208 of 209 | 0.996 | [-3250, -35.84] | `aggregate-error` | -668,617 |
| E10 | -0.005812 | -0.00266 | 208 of 209 | 0.772 | [1.236, 129.2] | `aggregate-error` | 26,606 |
| E11 | 0.1124 | 0.04372 | 208 of 209 | 0.997 | [-6824, -61.56] | `aggregate-error` | -1,406,667 |
| E12 | 0.03975 | 0.006496 | 208 of 209 | 0.998 | [-5025, -35.75] | `aggregate-error` | -1,037,796 |
| E13 | 0.001428 | 0.0008161 | 208 of 209 | 0.638 | [1.16, 255.1] | `aggregate-error` | 52,821 |
| E14 | 0.09234 | 0.01102 | 208 of 209 | 0.996 | [-5875, -58.6] | `aggregate-error` | -1,209,862 |
| E15 | 0.02471 | -0.01205 | 208 of 209 | 0.997 | [-3761, -35.03] | `aggregate-error` | -775,054 |
| E16 | -0.004094 | -0.0007762 | 208 of 209 | 0.816 | [1.599, 110.9] | `aggregate-error` | 22,727 |
| E17 | 0.1086 | 0.0484 | 208 of 209 | 0.997 | [-6951, -57.44] | `aggregate-error` | -1,433,906 |
| E18 | 0.02987 | 0.003941 | 208 of 209 | 0.998 | [-5134, -31.98] | `aggregate-error` | -1,061,157 |

Skill is 1 − model / reference per series. It is undefined where the reference score is zero, for one series
in each row.
The top-five share is the share of the positive gains (reference minus model, where positive) held by the
five largest. The leave-one-out range is the family's mean difference with each series left out in turn.
These are the protocol's declared descriptors, with Study 1's definitions
(`pulsegraph/evaluation/reviews.py`), computed by `make_tables.py` from `inference/paired_entities.csv`.

In every row, the series whose omission moves the mean most is `aggregate-error`. Its difference has the sign
of the family's mean in every row. In the comparisons against `hurdle_count_28` and `local_mean_28`, the five
largest gains hold 0.995 to 0.998 of all positive gain.

### Other scores, horizon 7

| ID | Metric | Entities | Unavailable | Mean difference | 95% interval | Median difference | Lower / tied / higher | Raw p | Status |
|---|---|---|---|---|---|---|---|---|---|
| E01 | context_scaled_qscore9 | 209 | 0 | -0.02204 | [-0.03098, -0.01407] | -0.005825 | 122 / 2 / 85 | 1.39e-06 | secondary |
| E01 | occurrence_brier | 209 | 0 | -0.009771 | [-0.01336, -0.006196] | -0.002759 | 121 / 0 / 88 | 3.43e-06 | secondary |
| E01 | discrete_crps | 208 | 1 | 0.4822 | [0.08663, 1.044] | -0.01006 | 123 / 0 / 85 | 0.307 | secondary |
| E02 | context_scaled_qscore9 | 209 | 0 | -0.1311 | [-0.1809, -0.08701] | -0.01058 | 129 / 12 / 68 | 5.29e-11 | secondary |
| E02 | occurrence_brier | 209 | 0 | 0 | [0, 0] | 0 | 0 / 209 / 0 | 1 | secondary |
| E02 | discrete_crps | 208 | 1 | -58.03 | [-100.2, -24.62] | -0.01645 | 140 / 0 / 68 | 4.24e-13 | secondary |
| E03 | context_scaled_qscore9 | 209 | 0 | -0.01511 | [-0.03735, 0.004919] | 0.003944 | 92 / 0 / 117 | 0.794 | secondary |
| E03 | occurrence_brier | 0 | 209 |  |  |  |  |  | unavailable (no_count_distribution) |
| E03 | discrete_crps | 0 | 209 |  |  |  |  |  | unavailable (no_count_distribution) |
| E07 | context_scaled_qscore9 | 209 | 0 | -0.006708 | [-0.01467, -0.0001148] | 0.0008949 | 95 / 8 / 106 | 0.568 | secondary |
| E07 | occurrence_brier | 209 | 0 | -0.001963 | [-0.004954, 0.001004] | -1.935e-05 | 105 / 0 / 104 | 0.283 | secondary |
| E07 | discrete_crps | 208 | 1 | 0.6513 | [0.1107, 1.396] | -0.0001546 | 105 / 0 / 103 | 0.362 | secondary |
| E08 | context_scaled_qscore9 | 209 | 0 | -0.1278 | [-0.1761, -0.08451] | -0.004233 | 116 / 18 / 75 | 3.24e-07 | secondary |
| E08 | occurrence_brier | 209 | 0 | 0 | [0, 0] | 0 | 0 / 209 / 0 | 1 | secondary |
| E08 | discrete_crps | 208 | 1 | -59.08 | [-102.4, -24.6] | -0.007102 | 126 / 0 / 82 | 3.18e-09 | secondary |
| E09 | context_scaled_qscore9 | 209 | 0 | -0.02463 | [-0.04487, -0.007124] | -0.001849 | 112 / 1 / 96 | 0.115 | secondary |
| E09 | occurrence_brier | 0 | 209 |  |  |  |  |  | unavailable (no_count_distribution) |
| E09 | discrete_crps | 0 | 209 |  |  |  |  |  | unavailable (no_count_distribution) |
| E13 | context_scaled_qscore9 | 209 | 0 | -0.006123 | [-0.01111, -0.001495] | -0.001063 | 110 / 2 / 97 | 0.0687 | secondary |
| E13 | occurrence_brier | 209 | 0 | -0.004641 | [-0.007677, -0.001622] | -0.002656 | 120 / 0 / 89 | 0.00272 | secondary |
| E13 | discrete_crps | 208 | 1 | 0.8991 | [0.2707, 1.711] | -0.003395 | 112 / 0 / 96 | 0.668 | secondary |
| E14 | context_scaled_qscore9 | 209 | 0 | -0.1182 | [-0.1673, -0.07431] | -0.004233 | 113 / 7 / 89 | 0.00046 | secondary |
| E14 | occurrence_brier | 209 | 0 | 0 | [0, 0] | 0 | 0 / 209 / 0 | 1 | secondary |
| E14 | discrete_crps | 208 | 1 | -58.03 | [-99.68, -24.32] | -0.005789 | 122 / 0 / 86 | 6.26e-06 | secondary |
| E15 | context_scaled_qscore9 | 209 | 0 | -0.01512 | [-0.03593, 0.001938] | 0.008833 | 82 / 1 / 126 | 0.233 | secondary |
| E15 | occurrence_brier | 0 | 209 |  |  |  |  |  | unavailable (no_count_distribution) |
| E15 | discrete_crps | 0 | 209 |  |  |  |  |  | unavailable (no_count_distribution) |

### Other scores, horizon 30

| ID | Metric | Entities | Unavailable | Mean difference | 95% interval | Median difference | Lower / tied / higher | Raw p | Status |
|---|---|---|---|---|---|---|---|---|---|
| E04 | context_scaled_qscore9 | 209 | 0 | -0.002395 | [-0.006836, 0.00146] | 0.0002262 | 101 / 2 / 106 | 0.752 | secondary |
| E04 | occurrence_brier | 209 | 0 | -0.003203 | [-0.005052, -0.001416] | -0.0008252 | 128 / 0 / 81 | 0.000643 | secondary |
| E04 | discrete_crps | 208 | 1 | 0.6666 | [0.01136, 1.569] | -3.799e-05 | 104 / 0 / 104 | 0.223 | secondary |
| E05 | context_scaled_qscore9 | 209 | 0 | -0.1456 | [-0.1909, -0.1055] | -0.02617 | 150 / 9 / 50 | 2.12e-21 | secondary |
| E05 | occurrence_brier | 209 | 0 | 0 | [0, 0] | 0 | 0 / 209 / 0 | 1 | secondary |
| E05 | discrete_crps | 208 | 1 | -60.26 | [-106.7, -23.72] | -0.06542 | 162 / 0 / 46 | 4.01e-22 | secondary |
| E06 | context_scaled_qscore9 | 209 | 0 | -0.02913 | [-0.04976, -0.01305] | -0.00184 | 112 / 0 / 97 | 0.0101 | secondary |
| E06 | occurrence_brier | 0 | 209 |  |  |  |  |  | unavailable (no_count_distribution) |
| E06 | discrete_crps | 0 | 209 |  |  |  |  |  | unavailable (no_count_distribution) |
| E10 | context_scaled_qscore9 | 209 | 0 | 0.001291 | [-0.001255, 0.003757] | 0.001769 | 80 / 8 / 121 | 0.00947 | secondary |
| E10 | occurrence_brier | 209 | 0 | -0.0005268 | [-0.002183, 0.001062] | -0.0002626 | 110 / 0 / 99 | 0.839 | secondary |
| E10 | discrete_crps | 208 | 1 | 0.9372 | [0.2503, 1.876] | 0.002584 | 88 / 0 / 120 | 0.00289 | secondary |
| E11 | context_scaled_qscore9 | 209 | 0 | -0.1466 | [-0.19, -0.1075] | -0.03038 | 161 / 17 / 31 | 2.8e-26 | secondary |
| E11 | occurrence_brier | 209 | 0 | 0 | [0, 0] | 0 | 0 / 209 / 0 | 1 | secondary |
| E11 | discrete_crps | 208 | 1 | -61.38 | [-109, -24.31] | -0.06016 | 173 / 0 / 35 | 2.93e-27 | secondary |
| E12 | context_scaled_qscore9 | 209 | 0 | -0.03336 | [-0.05248, -0.01843] | -0.003988 | 124 / 1 / 84 | 1.11e-05 | secondary |
| E12 | occurrence_brier | 0 | 209 |  |  |  |  |  | unavailable (no_count_distribution) |
| E12 | discrete_crps | 0 | 209 |  |  |  |  |  | unavailable (no_count_distribution) |
| E16 | context_scaled_qscore9 | 209 | 0 | 0.001687 | [-0.0008144, 0.004384] | 0.0006744 | 101 / 1 / 107 | 0.303 | secondary |
| E16 | occurrence_brier | 209 | 0 | -0.0009753 | [-0.002561, 0.0005924] | -0.0007553 | 114 / 0 / 95 | 0.321 | secondary |
| E16 | discrete_crps | 208 | 1 | 1.299 | [0.3816, 2.52] | 0.001984 | 95 / 0 / 113 | 0.00816 | secondary |
| E17 | context_scaled_qscore9 | 209 | 0 | -0.1402 | [-0.1839, -0.1025] | -0.02686 | 160 / 9 / 40 | 4.58e-24 | secondary |
| E17 | occurrence_brier | 209 | 0 | 0 | [0, 0] | 0 | 0 / 209 / 0 | 1 | secondary |
| E17 | discrete_crps | 208 | 1 | -57.51 | [-100.8, -23.02] | -0.05182 | 170 / 0 / 38 | 2.85e-24 | secondary |
| E18 | context_scaled_qscore9 | 209 | 0 | -0.02597 | [-0.04489, -0.01163] | -0.00242 | 109 / 1 / 99 | 0.0163 | secondary |
| E18 | occurrence_brier | 0 | 209 |  |  |  |  |  | unavailable (no_count_distribution) |
| E18 | discrete_crps | 0 | 209 |  |  |  |  |  | unavailable (no_count_distribution) |

- **Brier:** against `hurdle_count_28`, the differences are exactly zero for every series. The hurdle variants
  and `hurdle_count_28` use the same context-only occurrence probability: the nonzero days among the last
  28, plus 0.5, over 29 (`pulsegraph/study2/models.py`). Against the completed controls, the hurdle's
  occurrence probability has a lower Brier score, with the interval below zero, at horizon 7 for Chronos-2
  and TimesFM 2.5 and at horizon 30 for Chronos-2.
- **Discrete CRPS:** against `hurdle_count_28` it points the same way as QScore9. Against the completed
  controls, its means are positive with intervals above zero.
- **CRPS availability:** `aggregate-error` has no certified discrete CRPS for any forecast with a count law
  (11 variants × 3 origins × 2 horizons = 66 forecasts). By the dated addition of 2026-10-15 these are
  unavailable, so each CRPS contrast has 208 series. Every other forecast with a count law is certified:
  13,728 of 13,794. The 6,270 forecasts without a law are the raw decile variants, `local_mean_28` and
  `autoets_weekly`.

### Per stratum

These subgroup descriptions carry no interval and no test. The very-sparse stratum has 9 series, not 100.
Each cell gives the mean difference, the median difference and, in brackets, the series where the model
variant is lower. Ties and losses are in `inference/secondary_strata_contrasts.csv`.

QScore9:

| ID | Horizon | Model variant | Reference | dense (n = 100) | sparse (n = 100) | very_sparse (n = 9) |
|---|---|---|---|---|---|---|
| E01 | 7 | `chronos2_hurdle` | `chronos2_completed` | 317.7 / 0.0455 (36 of 100) | -0.05531 / -0.03333 (81 of 100) | -0.01752 / 0 (4 of 9) |
| E02 | 7 | `chronos2_hurdle` | `hurdle_count_28` | -10,638 / -0.3217 (85 of 100) | -0.3483 / 0.003175 (40 of 100) | -1.312 / 0 (4 of 9) |
| E03 | 7 | `chronos2_raw` | `local_mean_28` | -6028 / -0.07942 (62 of 100) | -0.001134 / 0.0266 (26 of 100) | 0.0684 / 1.055e-09 (4 of 9) |
| E04 | 30 | `chronos2_hurdle` | `chronos2_completed` | 188.6 / 0.01543 (43 of 100) | -0.01457 / -0.003086 (58 of 100) | -0.01108 / 0 (4 of 9) |
| E05 | 30 | `chronos2_hurdle` | `hurdle_count_28` | -13,715 / -0.6031 (91 of 100) | -0.3834 / -0.001728 (55 of 100) | -1.415 / 0 (4 of 9) |
| E06 | 30 | `chronos2_raw` | `local_mean_28` | -9893 / -0.03933 (61 of 100) | -0.04493 / 0.00175 (46 of 100) | -0.006479 / -0.006837 (5 of 9) |
| E07 | 7 | `timesfm3_hurdle` | `timesfm3_completed` | 369.7 / 0.03386 (32 of 100) | -0.03119 / -0.009524 (60 of 100) | 0.01129 / 0 (2 of 9) |
| E08 | 7 | `timesfm3_hurdle` | `hurdle_count_28` | -11,318 / -0.3767 (80 of 100) | -0.3252 / 0.003175 (32 of 100) | -1.307 / 0 (4 of 9) |
| E09 | 7 | `timesfm3_raw` | `local_mean_28` | -6761 / -0.1083 (70 of 100) | 0.002103 / 0.01057 (38 of 100) | 0.04384 / 0 (4 of 9) |
| E10 | 30 | `timesfm3_hurdle` | `timesfm3_completed` | 268.6 / 0.02173 (34 of 100) | -0.0003926 / 0.0004938 (45 of 100) | 0.02148 / 0 (2 of 9) |
| E11 | 30 | `timesfm3_hurdle` | `hurdle_count_28` | -14,194 / -0.5769 (94 of 100) | -0.3521 / -0.004444 (63 of 100) | -1.39 / 0 (4 of 9) |
| E12 | 30 | `timesfm3_raw` | `local_mean_28` | -10,452 / -0.04297 (70 of 100) | -0.02674 / -0.0006202 (51 of 100) | -0.0149 / 0 (4 of 9) |
| E13 | 7 | `timesfm2p5_hurdle` | `timesfm2p5_completed` | 530.6 / 0.03386 (40 of 100) | -0.01284 / -0.01058 (66 of 100) | -0.003645 / 0.007407 (3 of 9) |
| E14 | 7 | `timesfm2p5_hurdle` | `hurdle_count_28` | -12,220 / -0.3709 (82 of 100) | -0.3162 / 0.01323 (29 of 100) | -1.31 / 0 (4 of 9) |
| E15 | 7 | `timesfm2p5_raw` | `local_mean_28` | -7823 / -0.1053 (61 of 100) | -0.005074 / 0.03205 (19 of 100) | 0.05747 / 0 (4 of 9) |
| E16 | 30 | `timesfm2p5_hurdle` | `timesfm2p5_completed` | 230.6 / 0.02333 (43 of 100) | 0.01899 / -0.0008642 (54 of 100) | -0.003841 / 0 (4 of 9) |
| E17 | 30 | `timesfm2p5_hurdle` | `hurdle_count_28` | -14,458 / -0.5962 (94 of 100) | -0.3428 / -0.003086 (62 of 100) | -1.409 / 0 (4 of 9) |
| E18 | 30 | `timesfm2p5_raw` | `local_mean_28` | -10,678 / -0.05805 (68 of 100) | -0.03236 / 0.004494 (40 of 100) | -0.006367 / -0.003695 (5 of 9) |

Context-scaled QScore9:

| ID | Horizon | Model variant | Reference | dense (n = 100) | sparse (n = 100) | very_sparse (n = 9) |
|---|---|---|---|---|---|---|
| E01 | 7 | `chronos2_hurdle` | `chronos2_completed` | -0.004616 / 0.004909 (37 of 100) | -0.04074 / -0.0304 (81 of 100) | -0.007847 / 0 (4 of 9) |
| E02 | 7 | `chronos2_hurdle` | `hurdle_count_28` | -0.2191 / -0.08535 (85 of 100) | -0.03467 / 0.003175 (40 of 100) | -0.2253 / 0 (4 of 9) |
| E03 | 7 | `chronos2_raw` | `local_mean_28` | -0.06408 / -0.02714 (62 of 100) | 0.03128 / 0.0248 (26 of 100) | 0.01354 / 1.055e-09 (4 of 9) |
| E04 | 30 | `chronos2_hurdle` | `chronos2_completed` | -0.001606 / 0.003202 (39 of 100) | -0.003091 / -0.002963 (58 of 100) | -0.003417 / 0 (4 of 9) |
| E05 | 30 | `chronos2_hurdle` | `hurdle_count_28` | -0.2328 / -0.1197 (91 of 100) | -0.04979 / -0.001728 (55 of 100) | -0.2412 / 0 (4 of 9) |
| E06 | 30 | `chronos2_raw` | `local_mean_28` | -0.06264 / -0.008429 (61 of 100) | 0.001892 / 0.00175 (46 of 100) | -0.001443 / -0.006837 (5 of 9) |
| E07 | 7 | `timesfm3_hurdle` | `timesfm3_completed` | 0.005034 / 0.004578 (32 of 100) | -0.01942 / -0.00732 (61 of 100) | 0.004054 / 0 (2 of 9) |
| E08 | 7 | `timesfm3_hurdle` | `hurdle_count_28` | -0.2206 / -0.08267 (80 of 100) | -0.02628 / 0.003175 (32 of 100) | -0.2241 / 0 (4 of 9) |
| E09 | 7 | `timesfm3_raw` | `local_mean_28` | -0.07473 / -0.02727 (70 of 100) | 0.02279 / 0.01057 (38 of 100) | 0.005153 / 0 (4 of 9) |
| E10 | 30 | `timesfm3_hurdle` | `timesfm3_completed` | 0.003006 / 0.004259 (34 of 100) | -0.0006873 / 0.0004938 (44 of 100) | 0.004207 / 0 (2 of 9) |
| E11 | 30 | `timesfm3_hurdle` | `hurdle_count_28` | -0.2357 / -0.1171 (94 of 100) | -0.04943 / -0.004444 (63 of 100) | -0.2367 / 0 (4 of 9) |
| E12 | 30 | `timesfm3_raw` | `local_mean_28` | -0.07049 / -0.0151 (70 of 100) | 0.001086 / -4.144e-05 (50 of 100) | -0.003466 / 0 (4 of 9) |
| E13 | 7 | `timesfm2p5_hurdle` | `timesfm2p5_completed` | 0.002679 / 0.004957 (40 of 100) | -0.01496 / -0.01005 (67 of 100) | -0.005801 / 0.003879 (3 of 9) |
| E14 | 7 | `timesfm2p5_hurdle` | `hurdle_count_28` | -0.2182 / -0.08182 (81 of 100) | -0.00851 / 0.01323 (28 of 100) | -0.225 / 0 (4 of 9) |
| E15 | 7 | `timesfm2p5_raw` | `local_mean_28` | -0.06988 / -0.02905 (60 of 100) | 0.03712 / 0.0333 (18 of 100) | 0.01284 / 0 (4 of 9) |
| E16 | 30 | `timesfm2p5_hurdle` | `timesfm2p5_completed` | 0.002729 / 0.004963 (43 of 100) | 0.001047 / -0.001111 (54 of 100) | -0.002768 / 0 (4 of 9) |
| E17 | 30 | `timesfm2p5_hurdle` | `hurdle_count_28` | -0.2251 / -0.1165 (94 of 100) | -0.04641 / -0.003086 (62 of 100) | -0.2403 / 0 (4 of 9) |
| E18 | 30 | `timesfm2p5_raw` | `local_mean_28` | -0.05996 / -0.01609 (66 of 100) | 0.005643 / 0.004757 (38 of 100) | 0.000454 / -0.003695 (5 of 9) |

- **Hurdle against completed:** in the dense stratum, the hurdle variant is lower in 32 to 43 of the 100
  series across the three models and two horizons. In the sparse stratum it is lower in 45 to 81. In the
  very-sparse stratum it is lower in 2 to 4 of the 9, and the median difference is exactly 0 in five of the
  six rows.
- **Hurdle against `hurdle_count_28`:** it is lower in 80 to 94 of the 100 dense series and in 29 to 63 of
  the 100 sparse ones. In the very-sparse stratum it is lower in 4 of the 9.

### Model scores

| Model | QScore9 h7 | QScore9 h30 | Scaled QScore9 h30 | Brier h30 | CRPS h30 | CRPS series defined, h30 | CRPS certified / with law / all, h30 |
|---|---|---|---|---|---|---|---|
| `chronos2_raw` | 4500 | 4226 | 0.9315 |  |  | 0 | 0 / 0 / 627 |
| `chronos2_completed` | 4500 | 4226 | 0.9283 | 0.1817 | 57.61 | 208 | 624 / 627 / 627 |
| `chronos2_hurdle` | 4652 | 4316 | 0.9259 | 0.1785 | 58.27 | 208 | 624 / 627 / 627 |
| `timesfm3_raw` | 4149 | 3958 | 0.9273 |  |  | 0 | 0 / 0 / 627 |
| `timesfm3_completed` | 4149 | 3958 | 0.9236 | 0.179 | 56.22 | 208 | 624 / 627 / 627 |
| `timesfm3_hurdle` | 4326 | 4087 | 0.9249 | 0.1785 | 57.15 | 208 | 624 / 627 / 627 |
| `timesfm2p5_raw` | 3641 | 3850 | 0.9347 |  |  | 0 | 0 / 0 / 627 |
| `timesfm2p5_completed` | 3641 | 3850 | 0.9296 | 0.1795 | 59.72 | 208 | 624 / 627 / 627 |
| `timesfm2p5_hurdle` | 3895 | 3960 | 0.9313 | 0.1785 | 61.02 | 208 | 624 / 627 / 627 |
| `local_mean_28` | 7384 | 8959 | 0.9607 |  |  | 0 | 0 / 0 / 627 |
| `autoets_weekly` | 4756 | 74,699 | 291.8 |  |  | 0 | 0 / 0 / 627 |
| `nb_local_level_28` | 7741 | 8739 | 0.9801 | 0.2117 | 99.49 | 208 | 624 / 627 / 627 |
| `poisson_28` | 9630 | 10,642 | 1.132 | 0.2291 | 123.6 | 208 | 624 / 627 / 627 |
| `hurdle_count_28` | 9742 | 10,878 | 1.072 | 0.1785 | 118.5 | 208 | 624 / 627 / 627 |
| `hurdle_empirical_28` | 7348 | 8685 | 0.9565 | 0.1785 | 88.76 | 208 | 624 / 627 / 627 |
| `dynamic_count` | 10,948 | 11,471 | 1.026 | 0.1773 | 124.2 | 208 | 624 / 627 / 627 |

By stratum, horizon 30:

| Model | dense (n = 100) | sparse (n = 100) | very_sparse (n = 9) |
|---|---|---|---|
| `chronos2_raw` | 8830 | 1.544 | 2.825 |
| `chronos2_completed` | 8830 | 1.54 | 2.823 |
| `chronos2_hurdle` | 9018 | 1.525 | 2.812 |
| `timesfm3_raw` | 8271 | 1.562 | 2.816 |
| `timesfm3_completed` | 8271 | 1.557 | 2.815 |
| `timesfm3_hurdle` | 8539 | 1.556 | 2.836 |
| `timesfm2p5_raw` | 8045 | 1.557 | 2.825 |
| `timesfm2p5_completed` | 8045 | 1.547 | 2.822 |
| `timesfm2p5_hurdle` | 8275 | 1.566 | 2.818 |
| `local_mean_28` | 18,723 | 1.589 | 2.831 |
| `autoets_weekly` | 156,118 | 2.338 | 3.326 |
| `nb_local_level_28` | 18,263 | 1.598 | 2.864 |
| `poisson_28` | 22,239 | 2.134 | 4.665 |
| `hurdle_count_28` | 22,733 | 1.908 | 4.227 |
| `hurdle_empirical_28` | 18,151 | 1.563 | 2.852 |
| `dynamic_count` | 23,971 | 1.733 | 3.025 |

By stratum, horizon 7:

| Model | dense (n = 100) | sparse (n = 100) | very_sparse (n = 9) |
|---|---|---|---|
| `chronos2_raw` | 9403 | 1.633 | 0.9125 |
| `chronos2_completed` | 9403 | 1.634 | 0.9098 |
| `chronos2_hurdle` | 9720 | 1.579 | 0.8923 |
| `timesfm3_raw` | 8670 | 1.637 | 0.888 |
| `timesfm3_completed` | 8670 | 1.633 | 0.8856 |
| `timesfm3_hurdle` | 9040 | 1.602 | 0.8969 |
| `timesfm2p5_raw` | 7607 | 1.629 | 0.9016 |
| `timesfm2p5_completed` | 7607 | 1.624 | 0.8981 |
| `timesfm2p5_hurdle` | 8138 | 1.611 | 0.8944 |
| `local_mean_28` | 15,431 | 1.634 | 0.8441 |
| `autoets_weekly` | 9937 | 2.051 | 1.208 |
| `nb_local_level_28` | 16,177 | 1.699 | 0.9677 |
| `poisson_28` | 20,125 | 2.117 | 2.605 |
| `hurdle_count_28` | 20,358 | 1.927 | 2.204 |
| `hurdle_empirical_28` | 15,355 | 1.629 | 0.882 |
| `dynamic_count` | 22,879 | 1.783 | 0.9677 |

`autoets_weekly`'s horizon-30 mean (74,699, scaled 291.8) comes from the dense stratum (156,118). It is in no
family comparison.

### QScore9 accounting

Horizon 30:

| Model | QScore9 | Zero days | Positive, over | Positive, under | Largest residual |
|---|---|---|---|---|---|
| `chronos2_hurdle` | 4316 | 939.7 | 1673 | 1703 | 9.1e-13 |
| `chronos2_completed` | 4226 | 1004 | 1820 | 1402 | 2.3e-10 |
| `chronos2_raw` | 4226 | 1004 | 1820 | 1402 | 9.1e-13 |
| `timesfm3_hurdle` | 4087 | 972.8 | 1439 | 1675 | 1.2e-10 |
| `timesfm3_completed` | 3958 | 1039 | 1552 | 1367 | 2.3e-10 |
| `timesfm3_raw` | 3958 | 1039 | 1552 | 1367 | 2.3e-10 |
| `timesfm2p5_hurdle` | 3960 | 955.2 | 1411 | 1595 | 1.2e-10 |
| `timesfm2p5_completed` | 3850 | 1022 | 1543 | 1285 | 5.8e-11 |
| `timesfm2p5_raw` | 3850 | 1022 | 1543 | 1285 | 1.2e-10 |
| `hurdle_count_28` | 10,878 | 1246 | 6302 | 3329 | 4.7e-10 |
| `local_mean_28` | 8959 | 1064 | 5311 | 2583 | 9.1e-13 |

Horizon 7:

| Model | QScore9 | Zero days | Positive, over | Positive, under | Largest residual |
|---|---|---|---|---|---|
| `chronos2_hurdle` | 4652 | 11.82 | 1638 | 3002 | 2.3e-10 |
| `chronos2_completed` | 4500 | 12.14 | 1800 | 2688 | 9.1e-13 |
| `chronos2_raw` | 4500 | 12.15 | 1800 | 2688 | 2.3e-10 |
| `timesfm3_hurdle` | 4326 | 11.87 | 1561 | 2753 | 2.3e-10 |
| `timesfm3_completed` | 4149 | 12.24 | 1710 | 2426 | 9.1e-13 |
| `timesfm3_raw` | 4149 | 12.25 | 1710 | 2426 | 2.3e-10 |
| `timesfm2p5_hurdle` | 3895 | 11.33 | 1255 | 2628 | 1.2e-10 |
| `timesfm2p5_completed` | 3641 | 11.67 | 1347 | 2282 | 5.8e-11 |
| `timesfm2p5_raw` | 3641 | 11.68 | 1347 | 2282 | 2.3e-10 |
| `hurdle_count_28` | 9742 | 13.56 | 5501 | 4227 | 4.7e-10 |
| `local_mean_28` | 7384 | 11.29 | 4252 | 3121 | 4.7e-10 |

The parts are equal-series means, each over the full horizon, and they sum to QScore9. The largest window
residual is below 1e-9 at these scales.

- **Against the completed controls,** the hurdle variants have lower zero-day loss and lower positive-day
  overprediction, and higher positive-day underprediction, at both horizons. That is the trade the protocol
  anticipated and the synthetic grid showed.
- **Scale:** these are unscaled means, so the largest series dominates them. At horizon 30, the
  zero-day part also carries the three source zero days of the note above, on which `aggregate-error`'s
  deciles are in the millions.

### Randomized PIT, horizon 30

| Model | 0.0–0.1 | 0.1–0.2 | 0.2–0.3 | 0.3–0.4 | 0.4–0.5 | 0.5–0.6 | 0.6–0.7 | 0.7–0.8 | 0.8–0.9 | 0.9–1.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| `chronos2_raw` | unavailable | | | | | | | | | |
| `chronos2_completed` | 0.104 | 0.088 | 0.091 | 0.087 | 0.083 | 0.090 | 0.100 | 0.105 | 0.119 | 0.133 |
| `chronos2_hurdle` | 0.103 | 0.096 | 0.094 | 0.096 | 0.095 | 0.098 | 0.102 | 0.106 | 0.095 | 0.115 |
| `timesfm3_raw` | unavailable | | | | | | | | | |
| `timesfm3_completed` | 0.100 | 0.096 | 0.094 | 0.096 | 0.094 | 0.092 | 0.096 | 0.104 | 0.108 | 0.120 |
| `timesfm3_hurdle` | 0.101 | 0.096 | 0.099 | 0.095 | 0.098 | 0.096 | 0.097 | 0.099 | 0.102 | 0.118 |
| `timesfm2p5_raw` | unavailable | | | | | | | | | |
| `timesfm2p5_completed` | 0.097 | 0.094 | 0.094 | 0.093 | 0.093 | 0.095 | 0.092 | 0.096 | 0.093 | 0.153 |
| `timesfm2p5_hurdle` | 0.102 | 0.096 | 0.093 | 0.099 | 0.096 | 0.096 | 0.091 | 0.092 | 0.088 | 0.146 |
| `local_mean_28` | unavailable | | | | | | | | | |
| `autoets_weekly` | unavailable | | | | | | | | | |
| `nb_local_level_28` | 0.083 | 0.072 | 0.071 | 0.072 | 0.084 | 0.111 | 0.116 | 0.123 | 0.141 | 0.126 |
| `poisson_28` | 0.314 | 0.097 | 0.078 | 0.068 | 0.065 | 0.060 | 0.047 | 0.044 | 0.043 | 0.182 |
| `hurdle_count_28` | 0.173 | 0.104 | 0.099 | 0.097 | 0.093 | 0.089 | 0.072 | 0.065 | 0.051 | 0.158 |
| `hurdle_empirical_28` | 0.113 | 0.098 | 0.104 | 0.097 | 0.098 | 0.089 | 0.092 | 0.093 | 0.098 | 0.117 |
| `dynamic_count` | 0.163 | 0.094 | 0.096 | 0.093 | 0.097 | 0.087 | 0.079 | 0.068 | 0.057 | 0.167 |

The randomized PIT histograms are descriptive and carry no test, because the target days are not
independent.

- Each hurdle variant puts 0.088 to 0.146 of its target days in a tenth, against 0.083 to 0.153 for its
  completed control.
- `poisson_28`, `hurdle_count_28` and `dynamic_count` put the most days in the lowest and highest tenths.

## Files

| File | What it holds |
|---|---|
| `run.json` | The run's state: identity, metadata (readiness, family, specification, implementation commit, the addition's authority, source hashes, packages, hardware), the SHA-256 of each checkpoint, per-model timings, wall time, memory |
| `inference/` | The output of `scripts/study2_inference.py`: `inference.csv` and `inference.json` (the family), `paired_entities.csv`, `series_scores.csv`, `secondary_*.csv`, `pit_histograms.csv`, `pit_values.parquet`, `provenance.json` |
| `integrity/` | The output of `scripts/study2_integrity.py`: `integrity.csv` (every forecast's saved and recomputed scores), `integrity.json`, `integrity.log` |
| `target-pull/pull.json`, `target-pull/completeness.json` | The target pull's ledger and completeness document, byte copies of the files under `data\raw\study2\npm\targets\` |
| `target-pull/daily_summary.csv`, `target_days.py` | Per day, the series reading zero (all and per stratum), the panel's total, the largest series' count and the windows containing the day; and the command that writes it |
| `make_tables.py` | Prints the tables above from `inference/`; written before the run |
| `check_directions.py` | Prints the direction of each family test and its recomputed p from `inference/paired_entities.csv` |
| `results-provenance.json` | The SHA-256 of every file in this directory, the checkpoints included, and of the inputs |
| `.gitattributes`, `.gitignore` | Byte preservation; the checkpoints are kept out of the tree |

The 209 whole-series checkpoints (`<SHA-256 of the series label>.json`, 338 MB) are not in the tree, just as
Study 1's and the synthetic run's are not. Their SHA-256 values are in `run.json`, `inference/provenance.json`,
`integrity/integrity.json` and `results-provenance.json`. The inference and the integrity check read them.
The raw target captures and `signals.parquet` stay under the ignored `data\raw\study2\npm\targets\`. Their
hashes are in the completeness document.

## Regeneration

From the repository root, PowerShell. The gate, the pull and the run pass only at the implementation commit,
with the smoke and the readiness files at the paths the readiness names (`data\raw\study2\`; the tracked
copies are under `study\study2\`). The pull refuses to write a second snapshot, and a completed run directory
is immutable, so a rerun takes new output paths. A new pull opens the targets again and needs its own
approval.

```powershell
.\.venv\Scripts\python.exe scripts\study2_smoke.py --gpu --context-days 1400 --leads 60 --out data\raw\study2\smoke-3057b16.json
.\.venv\Scripts\python.exe scripts\study2_gate.py external_packages --readiness data\raw\study2\external-packages-readiness-3057b16.json
.\.venv\Scripts\python.exe scripts\study2_run.py external_packages --readiness data\raw\study2\external-packages-readiness-3057b16.json --fetch-targets --out data\raw\study2\npm\targets --max-requests 300 --interval 3
.\.venv\Scripts\python.exe scripts\study2_gate.py external_packages --readiness data\raw\study2\external-packages-readiness-3057b16-run.json
$env:HF_HUB_OFFLINE = "1"; $env:TRANSFORMERS_OFFLINE = "1"; .\.venv\Scripts\python.exe scripts\study2_run.py external_packages --readiness data\raw\study2\external-packages-readiness-3057b16-run.json --out reports\study2-npm\run-2026-10-15
.\.venv\Scripts\python.exe scripts\study2_inference.py external_packages --run reports\study2-npm\run-2026-10-15 --out <new directory>
.\.venv\Scripts\python.exe scripts\study2_integrity.py external_packages --run reports\study2-npm\run-2026-10-15 --out <new directory>
.\.venv\Scripts\python.exe reports\study2-npm\run-2026-10-15\make_tables.py reports\study2-npm\run-2026-10-15\inference
.\.venv\Scripts\python.exe reports\study2-npm\run-2026-10-15\check_directions.py reports\study2-npm\run-2026-10-15\inference
.\.venv\Scripts\python.exe reports\study2-npm\run-2026-10-15\target_days.py data\raw\study2\npm\targets\signals.parquet reports\study2-npm\panel\manifest.json --out <new file>
```

The inference ran from 23:39:24 to 23:39:46 UTC and the integrity check from 23:39:53 to 23:39:58 UTC, both
with HEAD at the implementation commit and no uncommitted change under the scripts or `pulsegraph/`. NumPy
2.5.3, SciPy 1.18.1 and pandas 2.3.3 were used. `inference/provenance.json` and `integrity/integrity.json`
record this. A reader of the CSVs who recomputes tests should parse floats exactly (pandas
`float_precision="round_trip"`); the default parser can move a last digit and change rank ties.

# Post-hoc: each foundation model's positive law with `dynamic_count`'s occurrence, on both Study 2 runs

**This is post-hoc.** It was computed on 2026-10-16 from the saved forecasts of the two Study 2 runs of
2026-10-15, the npm external run (`reports/study2-npm/run-2026-10-15/`) and the synthetic grid run
(`reports/study2-synthetic-2026-10-15/`), after both runs' registered scores were seen. It has no registered
status. It adds no test to E01 to E18 or S01 to S06 and replaces nothing in them: the registered results are
each run's `inference/`, which this command read and did not change. No model was run and nothing was
refitted. Nothing in either run directory changed.

## The question

The registered Study 2 hurdle replaces a frozen model's zero mass with a fixed occurrence estimate: the
Jeffreys estimate from the last 28 context days, constant over the horizon. On neither run did any comparison
favor that hurdle over the model's own completed forecast at BH q = 0.05, and five rejected against it:

- npm: E10 and E16;
- the grid: S01, S03 and S05.

The fixed estimate ignores persistence, and half the grid's cells have persistence 0.8. The registered
`dynamic_count` baseline carries a dynamic occurrence estimate: the discounted Beta-Bernoulli, discount 0.98
(`PROTOCOL.md`, "Models, distributions and controls"). The question here: does the model's completed positive
law, wrapped with that dynamic occurrence, do better?

## The wrapper

For each foundation model, each saved window and each target day:

- H_dyn(0) = 1 − p_dyn, and H_dyn(k) = 1 − p_dyn + p_dyn G+(k) for k ≥ 1.
- G+(k) = [F(k) − F(0)] / [1 − F(0)] is the positive conditional law of the model's saved completed law F
  for that day, as the registered hurdle uses it. G+ = delta_1 only when F(0) = 1, as registered.
- p_dyn is P(Y > 0) under `dynamic_count`'s saved law for the same day. That is a_B / (a_B + b_B), the same
  at every lead.

This is the registered FM hurdle (`pulsegraph/study2/distributions.py`, `fm_hurdle`) with the Jeffreys p
replaced by p_dyn. Its deciles come from the registered inversion (`pulsegraph/study2/models.py`,
`law_forecast`). Its QScore9 and accounting parts come from the registered formula
(`pulsegraph/study2/scores.py`, `accounting`). It is named `<model>_dyn` below.

**Where `dynamic_count` falls back.** Where the last 28 context days hold fewer than two positive days,
`dynamic_count` falls back to `hurdle_count_28`, as registered. There p_dyn is the Jeffreys p, and the
wrapper is the registered hurdle exactly. This happens in:

- npm: 10 of the 627 windows at each horizon, all in the very-sparse stratum;
- the grid: 501 of the 1,620 windows at each horizon, mostly in the cells with zero probability 0.95.

**What each comparison isolates.** Every wrapper is compared with four references:

| Reference | What differs from the wrapper |
|---|---|
| the model's completed control | Only the occurrence: p_dyn against the model's own 1 − F(0). This is the registered question with the occurrence estimate replaced. |
| the model's registered hurdle | Only the occurrence: p_dyn against the Jeffreys p. |
| `dynamic_count` | Only the positive law. The occurrence is identical on every day: the occurrence Brier score is equal in every window. |
| `hurdle_count_28` | Both the occurrence and the positive law. |

## Checks

All of these passed before any output was written.

- **The runs.** Each run was read by the registered inference's own reader (`read_run` in
  `scripts/study2_inference.py`): complete, its identity, authorized for the committed family and
  specification, every checkpoint matching the SHA-256 that `run.json` records, every row on the registered
  grid. Both runs passed: 209 and 540 checkpoints. The inference script is byte for byte the one that both
  runs' `inference/provenance.json` record (`fd32d317…`).
- **The registered families.** Rebuilt from the saved scores through the registered functions, they
  reproduce both runs' `inference/inference.csv` and `inference/paired_entities.csv` byte for byte.
- **The Jeffreys p reproduces the registered hurdle.** In all 3,762 npm and 9,720 grid wrapper windows, the
  wrapper built with the saved hurdle's Jeffreys p reproduces the saved hurdle's laws, deciles and QScore9
  exactly.
- **The occurrence is `dynamic_count`'s.** In every window, the wrapper's occurrence Brier score equals
  `dynamic_count`'s saved one exactly. Every saved `dynamic_count` law is a hurdle whose P(Y > 0) is its p,
  and p is the same at every lead of every window.
- **No delta_1.** No saved completed law has F(0) = 1, so delta_1 is never used: 0 days on either run. The
  completed law's exponential tail keeps F(0) below one, even on an all-zero context.
- **The accounting.** The three parts sum to the wrapper's QScore9 within 2.3e-10 on npm and 7.1e-15 on the
  grid.

## The settings

These are the registered settings of each family, applied to post-hoc comparisons.

- **The families.** The npm family has 24 tests, DE01 to DE24: 3 models × 2 horizons × 4 references. The grid
  family has 12 tests, DS01 to DS12: 3 models × 4 references at horizon 30.
- **Aggregation.** On npm, origins are averaged within series and horizon, and the 209 series weigh equally.
  On the grid, origins are averaged within replicate and cell, then the 18 cells within replicate with equal
  weight; the 30 replicate blocks are the entities.
- **Differences** are wrapper minus reference QScore9. QScore9 is a loss, so a negative difference favors the
  wrapper.
- **Intervals** are pointwise 95% percentile intervals from 20,000 entity bootstrap replicates. Each seed
  follows the registered derivation from root 20260917, over the post-hoc id.
- **Tests.** Raw p is a two-sided approximate Wilcoxon signed-rank test over the entities, with zero
  differences omitted. BH p is Benjamini-Hochberg once over each post-hoc family at q = 0.05. Neither family
  shares a correction with a registered family.
- **"Lower / tied / higher"** counts the entities where the wrapper's score is below, equal to or above the
  reference's.
- **Direction** is the side with the larger signed-rank sum.
- **The npm data are as served.** The npm horizon-30 blocks hold the three source zero days of dated
  addition 6, as the registered analysis does. The sensitivity's day removal is not applied here.

## npm: DE01 to DE24

| ID | Model variant | Reference | h | Model mean | Reference mean | Mean difference | 95% interval | Median difference | Lower / tied / higher (of 209) | Raw p | BH p | BH rejects at 0.05 | Larger rank sum favors |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DE01 | `chronos2_dyn` | `chronos2_completed` | 7 | 4577 | 4500 | 77.33 | [-0.008112, 231.6] | -0.009524 | 116 / 5 / 88 | 0.2 | 0.24 | no | model |
| DE02 | `chronos2_dyn` | `hurdle_count_28` | 7 | 4577 | 9742 | -5165 | [-15,402, -32.05] | -0.009524 | 122 / 3 / 84 | 1.01e-08 | 2.69e-08 | yes | model |
| DE03 | `chronos2_dyn` | `dynamic_count` | 7 | 4577 | 10,948 | -6371 | [-19,017, -32.41] | -0.01376 | 123 / 26 / 60 | 9.04e-12 | 3.1e-11 | yes | model |
| DE04 | `chronos2_dyn` | `chronos2_hurdle` | 7 | 4577 | 4652 | -74.67 | [-223.6, -0.148] | -0.001058 | 106 / 6 / 97 | 0.161 | 0.203 | no | model |
| DE05 | `chronos2_dyn` | `chronos2_completed` | 30 | 4252 | 4226 | 26.03 | [-0.05339, 77.77] | -0.005679 | 126 / 4 / 79 | 0.0797 | 0.112 | no | model |
| DE06 | `chronos2_dyn` | `hurdle_count_28` | 30 | 4252 | 10,878 | -6627 | [-19,794, -31.46] | -0.08272 | 176 / 2 / 31 | 5.37e-27 | 6.44e-26 | yes | model |
| DE07 | `chronos2_dyn` | `dynamic_count` | 30 | 4252 | 11,471 | -7219 | [-21,554, -32.27] | -0.02988 | 143 / 18 / 48 | 2.22e-20 | 1.07e-19 | yes | model |
| DE08 | `chronos2_dyn` | `chronos2_hurdle` | 30 | 4252 | 4316 | -64.21 | [-191.9, -0.2468] | -0.007901 | 138 / 3 / 68 | 6.81e-07 | 1.64e-06 | yes | model |
| DE09 | `timesfm3_dyn` | `timesfm3_completed` | 7 | 4242 | 4149 | 93.25 | [-0.0469, 279.4] | 0.004233 | 80 / 15 / 114 | 0.0909 | 0.121 | no | reference |
| DE10 | `timesfm3_dyn` | `hurdle_count_28` | 7 | 4242 | 9742 | -5499 | [-16,403, -32.2] | -0.008466 | 120 / 1 / 88 | 7.6e-07 | 1.66e-06 | yes | model |
| DE11 | `timesfm3_dyn` | `dynamic_count` | 7 | 4242 | 10,948 | -6705 | [-20,020, -32.3] | -0.002116 | 107 / 41 / 61 | 2.27e-09 | 6.81e-09 | yes | model |
| DE12 | `timesfm3_dyn` | `timesfm3_hurdle` | 7 | 4242 | 4326 | -83.65 | [-250.3, -0.2098] | 0 | 102 / 5 / 102 | 0.321 | 0.367 | no | model |
| DE13 | `timesfm3_dyn` | `timesfm3_completed` | 30 | 4012 | 3958 | 54.04 | [-0.09206, 161.8] | -0.0002469 | 106 / 11 / 92 | 0.838 | 0.838 | no | reference |
| DE14 | `timesfm3_dyn` | `hurdle_count_28` | 30 | 4012 | 10,878 | -6866 | [-20,501, -31.93] | -0.09012 | 171 / 5 / 33 | 4.9e-27 | 6.44e-26 | yes | model |
| DE15 | `timesfm3_dyn` | `dynamic_count` | 30 | 4012 | 11,471 | -7458 | [-22,272, -32.36] | -0.03556 | 142 / 36 / 31 | 1.44e-22 | 8.61e-22 | yes | model |
| DE16 | `timesfm3_dyn` | `timesfm3_hurdle` | 30 | 4012 | 4087 | -74.49 | [-222.2, -0.4329] | -0.004938 | 131 / 7 / 71 | 3.44e-06 | 6.88e-06 | yes | model |
| DE17 | `timesfm2p5_dyn` | `timesfm2p5_completed` | 7 | 3723 | 3641 | 82.61 | [0.1723, 247] | 0.002116 | 95 / 6 / 108 | 0.0525 | 0.0787 | no | reference |
| DE18 | `timesfm2p5_dyn` | `hurdle_count_28` | 7 | 3723 | 9742 | -6018 | [-17,965, -32.15] | -0.008466 | 117 / 1 / 91 | 1.72e-05 | 2.94e-05 | yes | model |
| DE19 | `timesfm2p5_dyn` | `dynamic_count` | 7 | 3723 | 10,948 | -7224 | [-21,578, -32.25] | 0 | 95 / 32 / 82 | 1.64e-05 | 2.94e-05 | yes | model |
| DE20 | `timesfm2p5_dyn` | `timesfm2p5_hurdle` | 7 | 3723 | 3895 | -171.3 | [-513, -0.2688] | 0.002116 | 93 / 8 / 108 | 0.761 | 0.794 | no | reference |
| DE21 | `timesfm2p5_dyn` | `timesfm2p5_completed` | 30 | 3879 | 3850 | 28.84 | [0.08909, 85.83] | -5.551e-17 | 105 / 3 / 101 | 0.432 | 0.471 | no | reference |
| DE22 | `timesfm2p5_dyn` | `hurdle_count_28` | 30 | 3879 | 10,878 | -6999 | [-20,911, -30.68] | -0.07654 | 168 / 4 / 37 | 6.44e-25 | 5.15e-24 | yes | model |
| DE23 | `timesfm2p5_dyn` | `dynamic_count` | 30 | 3879 | 11,471 | -7592 | [-22,681, -31.8] | -0.0284 | 135 / 29 / 45 | 1.6e-18 | 6.4e-18 | yes | model |
| DE24 | `timesfm2p5_dyn` | `timesfm2p5_hurdle` | 30 | 3879 | 3960 | -81.49 | [-242.9, -0.5095] | -0.004198 | 124 / 5 / 80 | 0.000401 | 0.000642 | yes | model |

Fifteen of the 24 reject at BH q = 0.05, all in favor of the wrapper. DE21's median of −5.6e-17 is
floating-point residue. Only an exact zero counts as a tie.

Each post-hoc row against the completed control or `hurdle_count_28`, beside the registered row of the
fixed-window hurdle against the same reference. Each cell gives post-hoc / registered.

| Post-hoc row | Registered row | Mean difference | Median difference | Lower-tied-higher | BH p | BH rejects |
|---|---|---|---|---|---|---|
| DE01 | E01 | 77.33 / 152 | -0.009524 / -0.01376 | 116-5-88 / 121-2-86 | 0.24 / 0.203 | no / no |
| DE02 | E02 | -5165 / -5090 | -0.009524 / -0.01587 | 122-3-84 / 129-12-68 | 2.69e-08 / 3.72e-11 | yes / yes |
| DE05 | E04 | 26.03 / 90.24 | -0.005679 / -0.0002469 | 126-4-79 / 105-2-102 | 0.112 / 0.449 | no / no |
| DE06 | E05 | -6627 / -6563 | -0.08272 / -0.06173 | 176-2-31 / 150-9-50 | 6.44e-26 / 7.06e-21 | yes / yes |
| DE09 | E07 | 93.25 / 176.9 | 0.004233 / 0.001058 | 80-15-114 / 94-8-107 | 0.121 / 0.236 | no / no |
| DE10 | E08 | -5499 / -5416 | -0.008466 / -0.007407 | 120-1-88 / 116-18-75 | 1.66e-06 / 3.61e-08 | yes / yes |
| DE13 | E10 | 54.04 / 128.5 | -0.0002469 / 0.00321 | 106-11-92 / 81-8-120 | 0.838 / 0.00215 | no / yes |
| DE14 | E11 | -6866 / -6792 | -0.09012 / -0.0716 | 171-5-33 / 161-17-31 | 6.44e-26 / 3.19e-25 | yes / yes |
| DE17 | E13 | 82.61 / 253.9 | 0.002116 / -0.002116 | 95-6-108 / 109-3-97 | 0.0787 / 0.628 | no / no |
| DE18 | E14 | -6018 / -5847 | -0.008466 / -0.006349 | 117-1-91 / 115-7-87 | 2.94e-05 / 2.66e-05 | yes / yes |
| DE21 | E16 | 28.84 / 110.3 | -5.551e-17 / 0.0009877 | 105-3-101 / 101-1-107 | 0.471 / 0.0276 | no / yes |
| DE22 | E17 | -6999 / -6918 | -0.07654 / -0.06938 | 168-4-37 / 160-9-40 | 5.15e-24 / 1.77e-23 | yes / yes |

The BH p-values come from different families, 24 tests against 18, so they are not directly comparable.

- **Against the completed control** (DE01, DE05, DE09, DE13, DE17, DE21), no row rejects. BH p runs from
  0.079 to 0.84.
  - The two rejections against the registered hurdle at horizon 30, E10 and E16, become DE13 (BH p 0.84) and
    DE21 (BH p 0.47).
  - Every mean difference is still positive: +26 to +93, against +90 to +254 for the registered hurdle.
  - Four of the six intervals include zero. DE17 and DE21 stay above zero.
  - The medians lie within 0.01 of zero.
  - By rank sum, the typical series favors the Chronos-2 wrapper at both horizons (lower in 116 and 126 of
    209). It favors the completed control for both TimesFM models.
- **Against the registered fixed-window hurdle** (DE04, DE08, DE12, DE16, DE20, DE24), every mean difference
  is negative, with the interval below zero.
  - At horizon 30, all three models reject in favor of the wrapper. The wrapper is lower in 124 to 138 of 209
    series, with BH p 1.6e-6 to 6.4e-4.
  - At horizon 7, none rejects (BH p 0.20 to 0.79). For TimesFM 2.5 the rank sum favors the fixed hurdle.
- **Against `dynamic_count`**, with the occurrence identical, all six reject in favor of the wrapper (BH p
  8.6e-22 to 2.9e-5). The wrapper is lower in 95 to 143 series and tied in 18 to 41.
- **Against `hurdle_count_28`**, all six reject in favor of the wrapper, as all six registered rows do. The
  wrapper is lower in 117 to 176 series, against 115 to 161 registered.
- **Scale.** These are unscaled means. As in the registered analysis, they weigh the largest series heavily:
  the dense stratum's means in the per-stratum table below run to the tens of thousands. The medians, the
  counts and the rank tests describe the typical series.

## Synthetic grid: DS01 to DS12 (horizon 30)

| ID | Model variant | Reference | Model mean | Reference mean | Mean difference | 95% interval | Median difference | Lower / tied / higher (of 30) | Raw p | BH p | BH rejects at 0.05 | Larger rank sum favors |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DS01 | `chronos2_dyn` | `chronos2_completed` | 1.813 | 1.785 | 0.0278 | [-0.008979, 0.06239] | 0.04308 | 10 / 0 / 20 | 0.0719 | 0.0959 | no | reference |
| DS02 | `chronos2_dyn` | `hurdle_count_28` | 1.813 | 1.819 | -0.006081 | [-0.06427, 0.05495] | 5.487e-05 | 15 / 0 / 15 | 0.734 | 0.734 | no | model |
| DS03 | `chronos2_dyn` | `dynamic_count` | 1.813 | 1.721 | 0.09152 | [0.05951, 0.131] | 0.08335 | 3 / 0 / 27 | 1.64e-05 | 9.84e-05 | yes | reference |
| DS04 | `chronos2_dyn` | `chronos2_hurdle` | 1.813 | 1.871 | -0.05819 | [-0.09786, -0.02406] | -0.04727 | 21 / 0 / 9 | 0.00411 | 0.00823 | yes | model |
| DS05 | `timesfm3_dyn` | `timesfm3_completed` | 1.782 | 1.754 | 0.02813 | [-0.01113, 0.0638] | 0.02883 | 10 / 0 / 20 | 0.0719 | 0.0959 | no | reference |
| DS06 | `timesfm3_dyn` | `hurdle_count_28` | 1.782 | 1.819 | -0.03699 | [-0.08884, 0.01326] | -0.03181 | 20 / 0 / 10 | 0.106 | 0.128 | no | model |
| DS07 | `timesfm3_dyn` | `dynamic_count` | 1.782 | 1.721 | 0.0606 | [0.03767, 0.08388] | 0.05156 | 4 / 0 / 26 | 7.51e-05 | 0.000301 | yes | reference |
| DS08 | `timesfm3_dyn` | `timesfm3_hurdle` | 1.782 | 1.84 | -0.05849 | [-0.09728, -0.02412] | -0.04468 | 21 / 0 / 9 | 0.00385 | 0.00823 | yes | model |
| DS09 | `timesfm2p5_dyn` | `timesfm2p5_completed` | 1.827 | 1.792 | 0.03462 | [-0.004804, 0.07104] | 0.04275 | 7 / 0 / 23 | 0.0256 | 0.0439 | yes | reference |
| DS10 | `timesfm2p5_dyn` | `hurdle_count_28` | 1.827 | 1.819 | 0.008012 | [-0.04943, 0.06357] | 0.02626 | 14 / 0 / 16 | 0.734 | 0.734 | no | reference |
| DS11 | `timesfm2p5_dyn` | `dynamic_count` | 1.827 | 1.721 | 0.1056 | [0.07495, 0.1372] | 0.09752 | 2 / 0 / 28 | 1.13e-05 | 9.84e-05 | yes | reference |
| DS12 | `timesfm2p5_dyn` | `timesfm2p5_hurdle` | 1.827 | 1.88 | -0.05307 | [-0.0902, -0.02105] | -0.03688 | 20 / 0 / 10 | 0.00385 | 0.00823 | yes | model |

Seven of the twelve reject at BH q = 0.05. Three favor the wrapper, all against the registered hurdle. Four
go against it: three against `dynamic_count` and one against the completed control.

| Post-hoc row | Registered row | Mean difference | Median difference | Lower-tied-higher | BH p | BH rejects |
|---|---|---|---|---|---|---|
| DS01 | S01 | 0.0278 / 0.08599 | 0.04308 / 0.05554 | 10-0-20 / 6-0-24 | 0.0959 / 0.00415 | no / yes |
| DS02 | S02 | -0.006081 / 0.05211 | 5.487e-05 / 0.04737 | 15-0-15 / 9-0-21 | 0.734 / 0.0111 | no / yes |
| DS05 | S03 | 0.02813 / 0.08662 | 0.02883 / 0.06144 | 10-0-20 / 6-0-24 | 0.0959 / 0.00676 | no / yes |
| DS06 | S04 | -0.03699 / 0.0215 | -0.03181 / 0.03119 | 20-0-10 / 11-0-19 | 0.128 / 0.12 | no / no |
| DS09 | S05 | 0.03462 / 0.08769 | 0.04275 / 0.06743 | 7-0-23 / 5-0-25 | 0.0439 / 0.00415 | yes / yes |
| DS10 | S06 | 0.008012 / 0.06109 | 0.02626 / 0.06027 | 14-0-16 / 9-0-21 | 0.734 / 0.00798 | no / yes |

- **Against the completed control** (DS01, DS05, DS09), every mean difference is still positive, +0.028 to
  +0.035, against +0.086 to +0.088 for the registered hurdle.
  - Every interval now includes zero.
  - The wrapper is lower in 7 to 10 of the 30 blocks, against 5 or 6 registered.
  - Two rows no longer reject (BH p 0.096). TimesFM 2.5 (DS09) still rejects against the wrapper, at BH p
    0.044.
- **Against `hurdle_count_28`** (DS02, DS06, DS10), none rejects (BH p 0.13 to 0.73). The registered S02 and
  S06 rejected against the hurdle.
- **Against the registered fixed-window hurdle** (DS04, DS08, DS12), all three reject in favor of the
  wrapper. The wrapper is lower in 20 or 21 of 30 blocks, with mean differences −0.053 to −0.058 and BH p
  0.0082.
- **Against `dynamic_count`**, with the occurrence identical, all three reject against the wrapper.
  `dynamic_count` is lower in 26 to 28 of 30 blocks, by 0.061 to 0.106.
  - At horizon 30, `dynamic_count`'s 1.721 is the lowest mean QScore9 of every forecaster here except the
    oracle (1.648). Among the registered variants it is also the lowest
    (`../study2-synthetic-2026-10-15/RESULTS-synthetic.md`, "Model scores and the oracle"). The wrappers
    score 1.782 to 1.827.

## The accounting parts

The parts are equal-entity means, each over the full horizon, and they sum to QScore9.

npm:

| Model | h | QScore9 | Zero days | Positive, over | Positive, under | Largest residual |
|---|---|---|---|---|---|---|
| `chronos2_dyn` | 7 | 4577 | 12.13 | 1776 | 2789 | 1.2e-10 |
| `chronos2_hurdle` | 7 | 4652 | 11.82 | 1638 | 3002 | 2.3e-10 |
| `chronos2_completed` | 7 | 4500 | 12.14 | 1800 | 2688 | 9.1e-13 |
| `timesfm3_dyn` | 7 | 4242 | 12.15 | 1697 | 2533 | 2.3e-10 |
| `timesfm3_hurdle` | 7 | 4326 | 11.87 | 1561 | 2753 | 2.3e-10 |
| `timesfm3_completed` | 7 | 4149 | 12.24 | 1710 | 2426 | 9.1e-13 |
| `timesfm2p5_dyn` | 7 | 3723 | 11.62 | 1321 | 2391 | 1.2e-10 |
| `timesfm2p5_hurdle` | 7 | 3895 | 11.33 | 1255 | 2628 | 1.2e-10 |
| `timesfm2p5_completed` | 7 | 3641 | 11.67 | 1347 | 2282 | 5.8e-11 |
| `dynamic_count` | 7 | 10,948 | 11.64 | 4198 | 6738 | 4.7e-10 |
| `hurdle_count_28` | 7 | 9742 | 13.56 | 5501 | 4227 | 4.7e-10 |
| `chronos2_dyn` | 30 | 4252 | 984.7 | 1772 | 1494 | 2.3e-10 |
| `chronos2_hurdle` | 30 | 4316 | 939.7 | 1673 | 1703 | 9.1e-13 |
| `chronos2_completed` | 30 | 4226 | 1004 | 1820 | 1402 | 2.3e-10 |
| `timesfm3_dyn` | 30 | 4012 | 1019 | 1530 | 1463 | 1.2e-10 |
| `timesfm3_hurdle` | 30 | 4087 | 972.8 | 1439 | 1675 | 1.2e-10 |
| `timesfm3_completed` | 30 | 3958 | 1039 | 1552 | 1367 | 2.3e-10 |
| `timesfm2p5_dyn` | 30 | 3879 | 1002 | 1498 | 1379 | 2.3e-10 |
| `timesfm2p5_hurdle` | 30 | 3960 | 955.2 | 1411 | 1595 | 1.2e-10 |
| `timesfm2p5_completed` | 30 | 3850 | 1022 | 1543 | 1285 | 5.8e-11 |
| `dynamic_count` | 30 | 11,471 | 1119 | 4819 | 5533 | 4.7e-10 |
| `hurdle_count_28` | 30 | 10,878 | 1246 | 6302 | 3329 | 4.7e-10 |

Synthetic grid, horizon 30:

| Model | QScore9 | Zero days | Positive, over | Positive, under | Largest residual |
|---|---|---|---|---|---|
| `chronos2_dyn` | 1.813 | 0.3682 | 0.0847 | 1.36 | 5.3e-15 |
| `chronos2_hurdle` | 1.871 | 0.4046 | 0.08819 | 1.378 | 3.6e-15 |
| `chronos2_completed` | 1.785 | 0.5798 | 0.1201 | 1.085 | 5.3e-15 |
| `timesfm3_dyn` | 1.782 | 0.3879 | 0.09111 | 1.303 | 3.6e-15 |
| `timesfm3_hurdle` | 1.84 | 0.4294 | 0.09493 | 1.316 | 3.6e-15 |
| `timesfm3_completed` | 1.754 | 0.6014 | 0.1231 | 1.029 | 3.6e-15 |
| `timesfm2p5_dyn` | 1.827 | 0.3653 | 0.09171 | 1.37 | 3.6e-15 |
| `timesfm2p5_hurdle` | 1.88 | 0.3947 | 0.09467 | 1.39 | 5.3e-15 |
| `timesfm2p5_completed` | 1.792 | 0.624 | 0.1334 | 1.035 | 3.6e-15 |
| `dynamic_count` | 1.721 | 0.5214 | 0.1114 | 1.088 | 7.1e-15 |
| `hurdle_count_28` | 1.819 | 0.5923 | 0.118 | 1.108 | 3.6e-15 |
| `oracle` | 1.648 | 0.4817 | 0.1102 | 1.056 | 3.6e-15 |

- **npm.** For all three models at both horizons, each of the wrapper's three parts lies between the
  registered hurdle's and the completed control's.
  - The wrapper loses more on zero days than the fixed hurdle and less than the completed control.
  - On positive days, it loses less through underprediction than the fixed hurdle and more than the
    completed control.
  - These are unscaled means, which the largest series dominates.
- **The grid.** The wrapper has the lowest zero-day part of every model here, 0.37 to 0.39. That is below
  the fixed hurdle's 0.39 to 0.43, the completed controls' 0.58 to 0.62 and the oracle's 0.48.
  - Its loss on positive days through underprediction stays high: 1.30 to 1.37, against 1.03 to 1.09 for
    the completed controls.
  - `dynamic_count` has the same occurrence on every day but a different positive law, and its
    underprediction part is 1.09. With the occurrence held equal, the foundation models' positive laws
    underpredict the grid's positive days more than `dynamic_count`'s does.

## Per stratum (npm) and per cell (grid)

These subgroup descriptions carry no interval and no test.

### npm, by stratum

Each cell gives the mean difference / the median difference, with the series where the wrapper is lower in
brackets. The very-sparse stratum has 9 series. Ties and higher counts are in `npm_groups.csv`.

QScore9:

| ID | h | Model variant | Reference | dense (n = 100) | sparse (n = 100) | very_sparse (n = 9) |
|---|---|---|---|---|---|---|
| DE01 | 7 | `chronos2_dyn` | `chronos2_completed` | 161.7 / 0.03069 (37 of 100) | -0.03623 / -0.02434 (76 of 100) | 0.01658 / 0 (3 of 9) |
| DE02 | 7 | `chronos2_dyn` | `hurdle_count_28` | -10,794 / -0.3804 (84 of 100) | -0.3293 / 0.007407 (32 of 100) | -1.278 / -0.007407 (6 of 9) |
| DE03 | 7 | `chronos2_dyn` | `dynamic_count` | -13,314 / -0.3492 (83 of 100) | -0.1856 / 0 (39 of 100) | -0.04127 / 0 (1 of 9) |
| DE04 | 7 | `chronos2_dyn` | `chronos2_hurdle` | -156.1 / -0.03386 (70 of 100) | 0.01908 / 0.008466 (32 of 100) | 0.0341 / 0 (4 of 9) |
| DE05 | 30 | `chronos2_dyn` | `chronos2_completed` | 54.42 / 0.00679 (45 of 100) | -0.01458 / -0.008395 (77 of 100) | 0.001427 / 0 (4 of 9) |
| DE06 | 30 | `chronos2_dyn` | `hurdle_count_28` | -13,849 / -0.6049 (92 of 100) | -0.3834 / -0.01 (78 of 100) | -1.402 / -0.007407 (6 of 9) |
| DE07 | 30 | `chronos2_dyn` | `dynamic_count` | -15,088 / -0.5331 (93 of 100) | -0.2076 / 0 (49 of 100) | -0.2006 / 0 (1 of 9) |
| DE08 | 30 | `chronos2_dyn` | `chronos2_hurdle` | -134.2 / -0.01543 (65 of 100) | -9.877e-06 / -0.005556 (69 of 100) | 0.01251 / 0 (4 of 9) |
| DE09 | 7 | `timesfm3_dyn` | `timesfm3_completed` | 194.9 / 0.02222 (38 of 100) | -0.02401 / 0.0005291 (38 of 100) | 0.04409 / 0 (4 of 9) |
| DE10 | 7 | `timesfm3_dyn` | `hurdle_count_28` | -11,493 / -0.3735 (80 of 100) | -0.318 / 0.01217 (34 of 100) | -1.275 / -0.007407 (6 of 9) |
| DE11 | 7 | `timesfm3_dyn` | `dynamic_count` | -14,014 / -0.4069 (83 of 100) | -0.1744 / 0 (23 of 100) | -0.03798 / 0 (1 of 9) |
| DE12 | 7 | `timesfm3_dyn` | `timesfm3_hurdle` | -174.8 / -0.0254 (67 of 100) | 0.007175 / 0.009524 (31 of 100) | 0.0328 / 0 (4 of 9) |
| DE13 | 30 | `timesfm3_dyn` | `timesfm3_completed` | 113 / 0.007531 (45 of 100) | -0.008244 / -0.001235 (57 of 100) | 0.01824 / 0 (4 of 9) |
| DE14 | 30 | `timesfm3_dyn` | `hurdle_count_28` | -14,350 / -0.5694 (92 of 100) | -0.3599 / -0.009753 (73 of 100) | -1.394 / -0.007407 (6 of 9) |
| DE15 | 30 | `timesfm3_dyn` | `dynamic_count` | -15,588 / -0.5133 (96 of 100) | -0.1842 / 0 (45 of 100) | -0.1922 / 0 (1 of 9) |
| DE16 | 30 | `timesfm3_dyn` | `timesfm3_hurdle` | -155.7 / -0.01593 (64 of 100) | -0.007852 / -0.002593 (62 of 100) | -0.003237 / -0.0009877 (5 of 9) |
| DE17 | 7 | `timesfm2p5_dyn` | `timesfm2p5_completed` | 172.6 / 0.01958 (39 of 100) | 0.002751 / -0.001058 (53 of 100) | 0.02575 / 0 (3 of 9) |
| DE18 | 7 | `timesfm2p5_dyn` | `hurdle_count_28` | -12,578 / -0.3762 (83 of 100) | -0.3006 / 0.02011 (28 of 100) | -1.281 / -0.007407 (6 of 9) |
| DE19 | 7 | `timesfm2p5_dyn` | `dynamic_count` | -15,099 / -0.4217 (79 of 100) | -0.157 / 0.01693 (15 of 100) | -0.04386 / 0 (1 of 9) |
| DE20 | 7 | `timesfm2p5_dyn` | `timesfm2p5_hurdle` | -358 / -0.01799 (60 of 100) | 0.01559 / 0.008995 (29 of 100) | 0.02939 / 0 (4 of 9) |
| DE21 | 30 | `timesfm2p5_dyn` | `timesfm2p5_completed` | 60.26 / 0.005185 (42 of 100) | 0.01492 / -0.001358 (58 of 100) | 0.005926 / -5.551e-17 (5 of 9) |
| DE22 | 30 | `timesfm2p5_dyn` | `hurdle_count_28` | -14,628 / -0.5832 (93 of 100) | -0.3468 / -0.00679 (69 of 100) | -1.399 / -0.007407 (6 of 9) |
| DE23 | 30 | `timesfm2p5_dyn` | `dynamic_count` | -15,866 / -0.543 (94 of 100) | -0.171 / 0 (40 of 100) | -0.1976 / 0 (1 of 9) |
| DE24 | 30 | `timesfm2p5_dyn` | `timesfm2p5_hurdle` | -170.3 / -0.01062 (63 of 100) | -0.004072 / -0.001852 (57 of 100) | 0.009767 / 0 (4 of 9) |

Context-scaled QScore9:

| ID | h | Model variant | Reference | dense (n = 100) | sparse (n = 100) | very_sparse (n = 9) |
|---|---|---|---|---|---|---|
| DE01 | 7 | `chronos2_dyn` | `chronos2_completed` | -0.006546 / 0.002451 (37 of 100) | -0.03025 / -0.02378 (76 of 100) | -0.002443 / 0 (3 of 9) |
| DE02 | 7 | `chronos2_dyn` | `hurdle_count_28` | -0.221 / -0.085 (84 of 100) | -0.02418 / 0.007407 (32 of 100) | -0.2199 / -0.007407 (6 of 9) |
| DE03 | 7 | `chronos2_dyn` | `dynamic_count` | -0.1671 / -0.07139 (82 of 100) | -0.01325 / 0 (39 of 100) | -0.007162 / 0 (1 of 9) |
| DE04 | 7 | `chronos2_dyn` | `chronos2_hurdle` | -0.001931 / -0.002785 (69 of 100) | 0.01049 / 0.008995 (32 of 100) | 0.005403 / 0 (4 of 9) |
| DE05 | 30 | `chronos2_dyn` | `chronos2_completed` | -0.002855 / 0.001165 (44 of 100) | -0.007975 / -0.007778 (77 of 100) | -0.0033 / 0 (4 of 9) |
| DE06 | 30 | `chronos2_dyn` | `hurdle_count_28` | -0.234 / -0.1271 (92 of 100) | -0.05467 / -0.01 (78 of 100) | -0.2411 / -0.007407 (6 of 9) |
| DE07 | 30 | `chronos2_dyn` | `dynamic_count` | -0.1925 / -0.1092 (92 of 100) | -0.02045 / 0 (49 of 100) | -0.03365 / 0 (1 of 9) |
| DE08 | 30 | `chronos2_dyn` | `chronos2_hurdle` | -0.001249 / -0.0023 (65 of 100) | -0.004885 / -0.005432 (68 of 100) | 0.000117 / 0 (4 of 9) |
| DE09 | 7 | `timesfm3_dyn` | `timesfm3_completed` | 0.003963 / 0.002529 (39 of 100) | -0.01111 / 0.001441 (37 of 100) | 0.008766 / 0 (4 of 9) |
| DE10 | 7 | `timesfm3_dyn` | `hurdle_count_28` | -0.2216 / -0.08705 (80 of 100) | -0.01798 / 0.01217 (34 of 100) | -0.2194 / -0.007407 (6 of 9) |
| DE11 | 7 | `timesfm3_dyn` | `dynamic_count` | -0.1678 / -0.06509 (83 of 100) | -0.00705 / 0 (23 of 100) | -0.006623 / 0 (1 of 9) |
| DE12 | 7 | `timesfm3_dyn` | `timesfm3_hurdle` | -0.001072 / -0.003011 (66 of 100) | 0.008308 / 0.009524 (29 of 100) | 0.004712 / 0 (4 of 9) |
| DE13 | 30 | `timesfm3_dyn` | `timesfm3_completed` | 0.002601 / 0.001553 (45 of 100) | -0.003837 / -0.000918 (56 of 100) | 0.001141 / 0 (4 of 9) |
| DE14 | 30 | `timesfm3_dyn` | `hurdle_count_28` | -0.2361 / -0.1257 (91 of 100) | -0.05258 / -0.009753 (73 of 100) | -0.2397 / -0.007407 (6 of 9) |
| DE15 | 30 | `timesfm3_dyn` | `dynamic_count` | -0.1945 / -0.1136 (96 of 100) | -0.01836 / 0 (45 of 100) | -0.03224 / 0 (1 of 9) |
| DE16 | 30 | `timesfm3_dyn` | `timesfm3_hurdle` | -0.000405 / -0.002754 (64 of 100) | -0.00315 / -0.002419 (61 of 100) | -0.003066 / 0 (4 of 9) |
| DE17 | 7 | `timesfm2p5_dyn` | `timesfm2p5_completed` | 0.00184 / 0.002437 (39 of 100) | -0.004386 / -0.001058 (53 of 100) | -0.001178 / 0 (3 of 9) |
| DE18 | 7 | `timesfm2p5_dyn` | `hurdle_count_28` | -0.219 / -0.08336 (82 of 100) | 0.002059 / 0.01905 (28 of 100) | -0.2204 / -0.007407 (6 of 9) |
| DE19 | 7 | `timesfm2p5_dyn` | `dynamic_count` | -0.1652 / -0.06292 (80 of 100) | 0.01299 / 0.01424 (14 of 100) | -0.007618 / 0 (1 of 9) |
| DE20 | 7 | `timesfm2p5_dyn` | `timesfm2p5_hurdle` | -0.0008395 / -0.001971 (58 of 100) | 0.01057 / 0.008466 (29 of 100) | 0.004622 / 0 (4 of 9) |
| DE21 | 30 | `timesfm2p5_dyn` | `timesfm2p5_completed` | 0.001633 / 0.0009311 (43 of 100) | 0.0004793 / -0.001358 (57 of 100) | -0.003136 / -5.551e-17 (5 of 9) |
| DE22 | 30 | `timesfm2p5_dyn` | `hurdle_count_28` | -0.2261 / -0.1235 (93 of 100) | -0.04697 / -0.00679 (69 of 100) | -0.2406 / -0.007407 (6 of 9) |
| DE23 | 30 | `timesfm2p5_dyn` | `dynamic_count` | -0.1846 / -0.1114 (94 of 100) | -0.01276 / 0 (40 of 100) | -0.03316 / 0 (1 of 9) |
| DE24 | 30 | `timesfm2p5_dyn` | `timesfm2p5_hurdle` | -0.001097 / -0.001976 (61 of 100) | -0.0005672 / -0.001235 (56 of 100) | -0.0003674 / 0 (4 of 9) |

- **Wrapper against the completed control.** The wrapper is lower in:
  - 37 to 45 of the 100 dense series, against 32 to 43 for the registered hurdle;
  - 38 to 77 of the 100 sparse series, against 45 to 81;
  - 3 to 5 of the 9 very-sparse series, against 2 to 4.
- **Wrapper against the registered hurdle.**
  - Dense: the wrapper is lower in 60 to 70 of 100.
  - Sparse: it is lower in 57 to 69 at horizon 30, but in only 29 to 32 at horizon 7.

### Grid, by cell (horizon 30)

Each cell holds 30 replicates. Each entry gives the mean difference, with the replicates where the wrapper is
lower in brackets. The context-scaled readings and the ties are in `synthetic_groups.csv`. A difference of
order 1e-17 or smaller is floating-point residue.

| Cell | Zero probability | Positive mean | Persistence | DS01 | DS02 | DS03 | DS04 | DS05 | DS06 | DS07 | DS08 | DS09 | DS10 | DS11 | DS12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cell00 | 0.2 | 1 | 0 | 0.0002058 (11) | -0.00107 (10) | 0 (0) | -0.00107 (10) | -0.001918 (12) | -0.00107 (10) | 0 (0) | -0.00107 (10) | -0.00107 (19) | -0.00107 (10) | 0 (0) | -0.00107 (10) |
| cell01 | 0.2 | 1 | 0.8 | -0.01517 (15) | -0.03201 (19) | 0.003465 (0) | -0.03608 (19) | -0.004716 (16) | -0.03384 (19) | 0.00163 (0) | -0.03561 (19) | -0.004749 (14) | -0.03366 (19) | 0.001811 (0) | -0.03545 (19) |
| cell02 | 0.2 | 5 | 0 | 0.01994 (8) | 0.01477 (8) | 0.03236 (5) | -0.01725 (17) | 0.01119 (9) | -0.003029 (14) | 0.01456 (9) | -0.01011 (21) | 0.01353 (6) | 0.003374 (14) | 0.02096 (4) | -0.009317 (20) |
| cell03 | 0.2 | 5 | 0.8 | -0.006576 (13) | -0.08752 (19) | 0.06438 (6) | -0.1237 (19) | 0.002584 (14) | -0.09947 (17) | 0.05243 (5) | -0.1244 (19) | 0.0565 (8) | -0.07212 (18) | 0.07978 (5) | -0.1095 (20) |
| cell04 | 0.2 | 25 | 0 | 0.3918 (2) | 0.4415 (1) | 0.5053 (0) | -0.0741 (22) | 0.2668 (1) | 0.2534 (1) | 0.3173 (1) | -0.07386 (20) | 0.3635 (2) | 0.4973 (1) | 0.5612 (0) | -0.07138 (22) |
| cell05 | 0.2 | 25 | 0.8 | 0.384 (10) | -0.06034 (16) | 0.7857 (5) | -0.5926 (20) | 0.321 (8) | -0.3049 (18) | 0.5411 (7) | -0.6132 (22) | 0.3665 (8) | -0.04109 (15) | 0.8049 (6) | -0.6026 (20) |
| cell06 | 0.8 | 1 | 0 | -0.0006008 (12) | -0.0006749 (11) | 0.0002305 (0) | -0.003621 (17) | 0.0006255 (9) | -0.0009053 (11) | 0 (0) | -0.0009053 (11) | -0.003259 (19) | -0.0009053 (11) | 0 (0) | -0.001111 (12) |
| cell07 | 0.8 | 1 | 0.8 | -0.006831 (22) | -0.01461 (17) | 0.001193 (0) | -0.01829 (21) | 0.009572 (12) | -0.01495 (18) | 0.000856 (0) | -0.01758 (19) | 0.002123 (13) | -0.01396 (18) | 0.001844 (0) | -0.01821 (19) |
| cell08 | 0.8 | 5 | 0 | 0.003802 (11) | -0.0005021 (14) | 0.00577 (6) | -0.001243 (16) | -0.003621 (15) | -0.001021 (14) | 0.005251 (9) | -0.001144 (15) | -0.004049 (15) | 0.01752 (9) | 0.02379 (6) | 0.001259 (15) |
| cell09 | 0.8 | 5 | 0.8 | -0.02579 (18) | -0.05557 (17) | 0.006856 (13) | -0.04252 (18) | 0.01176 (15) | -0.05691 (16) | 0.005514 (13) | -0.03838 (17) | -0.000823 (15) | -0.0492 (18) | 0.01323 (13) | -0.02681 (17) |
| cell10 | 0.8 | 25 | 0 | 0.1045 (8) | 0.1185 (9) | 0.1468 (6) | 0.02264 (12) | 0.05479 (11) | 0.05858 (9) | 0.08692 (8) | 0.008502 (13) | -0.00563 (15) | 0.2027 (6) | 0.2311 (6) | 0.01583 (10) |
| cell11 | 0.8 | 25 | 0.8 | -0.005465 (17) | -0.2609 (17) | 0.09422 (11) | -0.1061 (15) | 0.1152 (16) | -0.2898 (17) | 0.06531 (14) | -0.08761 (15) | 0.05653 (15) | -0.1865 (16) | 0.1686 (12) | -0.07137 (14) |
| cell12 | 0.95 | 1 | 0 | -0.000107 (2) | -0.001481 (8) | 0 (0) | -0.001481 (8) | -0.001712 (17) | -0.001481 (8) | 0 (0) | -0.001481 (8) | 0 (0) | -0.001481 (8) | 0 (0) | -0.001481 (8) |
| cell13 | 0.95 | 1 | 0.8 | -0.01184 (9) | -0.004609 (9) | 0 (0) | -0.005004 (9) | -0.00344 (8) | -0.004609 (9) | 0 (0) | -0.005193 (9) | -0.0009136 (3) | -0.004609 (9) | 0 (0) | -0.00516 (9) |
| cell14 | 0.95 | 5 | 0 | -0.001226 (7) | -0.005926 (8) | 0 (0) | -0.001481 (8) | -0.00935 (23) | -0.005926 (8) | 0 (0) | -0.002362 (8) | -0.002379 (14) | -0.005926 (8) | 0 (0) | -0.001481 (8) |
| cell15 | 0.95 | 5 | 0.8 | -0.05691 (14) | -0.01919 (9) | 0.0005679 (5) | -0.01396 (9) | -0.02997 (11) | -0.01963 (9) | 0.0001235 (5) | -0.009597 (9) | -0.02456 (6) | -0.02066 (9) | -0.0009053 (5) | -0.005251 (9) |
| cell16 | 0.95 | 25 | 0 | -0.007383 (23) | -0.03416 (8) | 0 (0) | -0.002165 (8) | -0.05845 (28) | -0.03416 (8) | 0 (0) | -0.01359 (8) | -0.03063 (28) | -0.03416 (8) | 0 (0) | -0.001811 (8) |
| cell17 | 0.95 | 25 | 0.8 | -0.266 (17) | -0.1057 (8) | 0.000428 (5) | -0.02947 (9) | -0.174 (15) | -0.1062 (9) | -0.000107 (5) | -0.02526 (9) | -0.1574 (14) | -0.1114 (9) | -0.005358 (5) | -0.01048 (9) |

- **Where the wrapper stays worst.** The largest positive differences against the completed control remain in
  the cells with zero probability 0.2 and positive mean 25. DS01, DS05 and DS09 give:
  - in `cell04`, with persistence 0: +0.39, +0.27 and +0.36, against +0.47, +0.34 and +0.43 registered;
  - in `cell05`, with persistence 0.8: +0.38, +0.32 and +0.37, against +0.98, +0.93 and +0.97 registered.

  The dynamic occurrence cuts the persistent cell's difference by more than half, and the non-persistent
  cell's by 16 to 22 percent. The registered per-cell values are in
  `../study2-synthetic-2026-10-15/RESULTS-synthetic.md`, "Per cell".
- **Against `dynamic_count`** (DS03, DS07, DS11), the wrapper is worse mostly in the cells with positive mean
  25 and zero probability 0.2 or 0.8.
- **The cells with zero probability 0.95.** Here the differences against `dynamic_count` and the registered
  hurdle are 0 or near it. The mean p_dyn there is 0.034 to 0.048 (table below). Whenever the occurrence
  probability is below 0.1, every decile of every hurdle with that occurrence is 0, whatever its positive
  law. `synthetic_groups.csv` gives the ties per cell: of the 30 replicates, 20 or 21 against the registered
  hurdle, and 24 or 30 against `dynamic_count`.

## The occurrence probabilities

Per stratum and horizon, from `npm_occurrence.csv`:

- the windows in which `dynamic_count` fell back to the Jeffreys p;
- the mean p_dyn and the mean Jeffreys p;
- their mean and largest absolute difference;
- the mean fraction of target days that were positive;
- the windows in which each wrapper's deciles equal the registered hurdle's.

The probabilities do not depend on the foundation model.

| stratum | h | Windows | dynamic_count fell back | Mean p_dyn | Mean Jeffreys p | Mean abs. difference | Largest abs. difference | Positive fraction of target days | Wrapper equals the registered hurdle (chronos2 / timesfm3 / timesfm2p5) |
|---|---|---|---|---|---|---|---|---|---|
| all | 7 | 627 | 10 | 0.534 | 0.553 | 0.051 | 0.323 | 0.600 | 95 / 121 / 131 |
| all | 30 | 627 | 10 | 0.534 | 0.553 | 0.051 | 0.323 | 0.548 | 56 / 90 / 84 |
| dense | 7 | 300 | 0 | 0.805 | 0.795 | 0.044 | 0.174 | 0.812 | 16 / 19 / 17 |
| dense | 30 | 300 | 0 | 0.805 | 0.795 | 0.044 | 0.174 | 0.791 | 3 / 8 / 4 |
| sparse | 7 | 300 | 0 | 0.301 | 0.347 | 0.059 | 0.239 | 0.425 | 62 / 85 / 97 |
| sparse | 30 | 300 | 0 | 0.301 | 0.347 | 0.059 | 0.239 | 0.338 | 36 / 65 / 63 |
| very_sparse | 7 | 27 | 10 | 0.106 | 0.162 | 0.056 | 0.323 | 0.201 | 17 / 17 / 17 |
| very_sparse | 30 | 27 | 10 | 0.106 | 0.162 | 0.056 | 0.323 | 0.185 | 17 / 17 / 17 |

The same, per grid cell at horizon 30, from `synthetic_occurrence.csv`, where horizon 7 also appears.
Within a replicate the occurrence chain is shared by every cell with the same zero probability and
persistence, as common random numbers, so those cells have the same occurrence rows.

| cell_id | h | Windows | dynamic_count fell back | Mean p_dyn | Mean Jeffreys p | Mean abs. difference | Largest abs. difference | Positive fraction of target days | Wrapper equals the registered hurdle (chronos2 / timesfm3 / timesfm2p5) |
|---|---|---|---|---|---|---|---|---|---|
| all | 30 | 1620 | 501 | 0.334 | 0.346 | 0.044 | 0.420 | 0.345 | 750 / 764 / 772 |
| cell00 | 30 | 90 | 0 | 0.798 | 0.791 | 0.034 | 0.096 | 0.802 | 65 / 65 / 65 |
| cell01 | 30 | 90 | 1 | 0.778 | 0.779 | 0.110 | 0.420 | 0.799 | 29 / 28 / 28 |
| cell02 | 30 | 90 | 0 | 0.798 | 0.791 | 0.034 | 0.096 | 0.802 | 10 / 10 / 2 |
| cell03 | 30 | 90 | 1 | 0.778 | 0.779 | 0.110 | 0.420 | 0.799 | 2 / 1 / 1 |
| cell04 | 30 | 90 | 0 | 0.798 | 0.791 | 0.034 | 0.096 | 0.802 | 0 / 0 / 0 |
| cell05 | 30 | 90 | 1 | 0.778 | 0.779 | 0.110 | 0.420 | 0.799 | 1 / 1 / 1 |
| cell06 | 30 | 90 | 2 | 0.192 | 0.206 | 0.036 | 0.147 | 0.196 | 49 / 62 / 61 |
| cell07 | 30 | 90 | 29 | 0.156 | 0.193 | 0.055 | 0.398 | 0.194 | 47 / 48 / 48 |
| cell08 | 30 | 90 | 2 | 0.192 | 0.206 | 0.036 | 0.147 | 0.196 | 6 / 9 / 19 |
| cell09 | 30 | 90 | 29 | 0.156 | 0.193 | 0.055 | 0.398 | 0.194 | 34 / 32 / 39 |
| cell10 | 30 | 90 | 2 | 0.192 | 0.206 | 0.036 | 0.147 | 0.196 | 3 / 4 / 4 |
| cell11 | 30 | 90 | 29 | 0.156 | 0.193 | 0.055 | 0.398 | 0.194 | 30 / 30 / 30 |
| cell12 | 30 | 90 | 58 | 0.048 | 0.060 | 0.012 | 0.065 | 0.046 | 80 / 80 / 80 |
| cell13 | 30 | 90 | 77 | 0.034 | 0.048 | 0.014 | 0.250 | 0.032 | 78 / 78 / 78 |
| cell14 | 30 | 90 | 58 | 0.048 | 0.060 | 0.012 | 0.065 | 0.046 | 80 / 80 / 80 |
| cell15 | 30 | 90 | 77 | 0.034 | 0.048 | 0.014 | 0.250 | 0.032 | 78 / 78 / 78 |
| cell16 | 30 | 90 | 58 | 0.048 | 0.060 | 0.012 | 0.065 | 0.046 | 80 / 80 / 80 |
| cell17 | 30 | 90 | 77 | 0.034 | 0.048 | 0.014 | 0.250 | 0.032 | 78 / 78 / 78 |

- **On average, p_dyn and the Jeffreys p are close.** The mean absolute difference is 0.051 on npm and 0.044
  on the grid. With persistence 0.8 and zero probability 0.2, it rises to 0.110, with differences up to 0.42.
- **The wrapper is often the registered hurdle.**
  - On the grid, the wrapper's deciles equal the registered hurdle's in 750 to 772 of the 1,620 windows at
    horizon 30.
  - In the six cells with zero probability 0.95, they are equal in 78 or 80 of 90 windows. There most
    replicates tie the registered hurdle exactly.
  - On npm they are equal in 56 to 90 of 627 windows at horizon 30.

## What it shows

Post-hoc, and with no registered status, `dynamic_count`'s discounted occurrence improves the foundation-model
hurdle on both runs, but it does not make the hurdle better than the model's own completed forecast. Against
the registered fixed-window hurdle, the dynamic wrapper is lower at horizon 30 for all three models, on npm
(lower in 124 to 138 of 209 series; BH p 1.6e-6 to 6.4e-4) and on the grid (lower in 20 or 21 of 30 blocks;
BH p 0.0082); at horizon 7 on npm no test rejects. Against the completed control, no npm row rejects and only
one of the three grid rows does, where the registered hurdle had two and three rejections against it; but
every mean difference is still positive (+26 to +93 on npm against +90 to +254; +0.028 to +0.035 on the grid
against +0.086 to +0.088), and the one rejection that remains, TimesFM 2.5 on the grid (DS09, BH p 0.044),
goes against the wrapper. The answer to the registered question therefore does not change: under neither
occurrence estimate does any comparison favor the substituted occurrence over the completed control at BH
q = 0.05, though for Chronos-2 on npm the typical series leans to the wrapper by rank sum without rejection.
What changes is the size of the loss, and on the grid no row against `hurdle_count_28` rejects any longer.
With the occurrence held equal, the foundation models' positive laws beat `dynamic_count`'s on npm (all six
reject in their favor) and lose to it on the grid (all three reject against them), where `dynamic_count`
keeps the lowest mean QScore9 after the oracle. In 10 of 627 npm windows and 501 of 1,620 grid windows at
each horizon, `dynamic_count` falls back to the Jeffreys p by its registered rule, and the wrapper there is
the registered hurdle.

## Files and regeneration

| File | What it holds | SHA-256 |
|---|---|---|
| `dynamic_occurrence.py` | The command; its docstring states every rule above | `c95e50e2ef29a17950fc4d3d73c3cca51f1cb90947d73635d9c86274a3c1fccd` |
| `npm_inference.csv` | DE01 to DE24 in `inference.csv`'s columns, with the rank sums and the registered row beside each | `f415826394c6173f4ff439b010ee2fffbc1b2bb48df3ae827aef3f5b3f12c8c1` |
| `npm_paired_entities.csv` | The 209 series differences of every row | `066bacb2db033b6e758e7195db222418de4d713fae6138da0f7db7e049269d3d` |
| `npm_window_scores.csv` | Every wrapper window: p_dyn, the Jeffreys p, the fallback flag, the F(0) = 1 days, QScore9, its parts, the scaled score, the Brier score, the registered hurdle's and the completed control's QScore9 | `5432ccf27555004947900ab8e2d3296d41ab2c76822335f9c9f1c3054fdce48b` |
| `npm_accounting.csv` | The three parts of the wrappers and their references, both horizons | `f56c0f817f83dc7e6551899dfd93ea18ac5c5b257063c7662382a662a3965f23` |
| `npm_groups.csv` | Every row by stratum, on QScore9 and the context-scaled QScore9, with n | `3ee6323b1032090bc3e879219739bfa93e2593047181e910b429e99864ccf69f` |
| `npm_occurrence.csv` | The occurrence table above | `9126f8e34843e48132b6c0c47981ffdf0f1a25d6c445a63216b466b65cdc1c0b` |
| `synthetic_inference.csv` | DS01 to DS12, as `npm_inference.csv` | `baa6c7f965e42236244dda401e8fda0c5a1b9afa1d6273133f80d2562c239cc9` |
| `synthetic_paired_entities.csv` | The 30 replicate-block differences of every row | `20ca3c2fc5c53d12baa75c415404fd111db86eda8bab4b87368bf60a32975e3b` |
| `synthetic_window_scores.csv` | Every wrapper window, both horizons, as `npm_window_scores.csv` | `f524fd6266516446eec2174c29c403954d0bc54da8189081c4d057b528fbe166` |
| `synthetic_accounting.csv` | The three parts at horizon 30, the oracle included | `12e352fd098cce0bebe42268c1e6a00ab32a729883f6acddc431ca2e27217921` |
| `synthetic_groups.csv` | Every row by cell, with the generator's parameters and n | `85f54d755ab59ab1288356b980f0bb6c93f50984e1eaa2dec86ac3be7646bda2` |
| `synthetic_occurrence.csv` | The occurrence table per cell, both horizons | `6337d60d73872c07836b71df46bf003f58656e8d449bb41fd464e8307fc2dc2e` |
| `provenance.json` | The hash of every input and output, of the command and of the code it imports; both families; every check; the package versions and the times | `5b57973895c39c19632c1041865fa7607f6fce9d4b439b5bd61bc7c230df67e7` |
| `.gitattributes` | Byte preservation for the hashes above | `99830dac01accc61f816ec447f93f2458069322411640a6c7c161eb18e49af63` |

`provenance.json` records the inputs:

- for both runs: `run.json`, all 749 checkpoints by name, the registered `inference.csv`,
  `paired_entities.csv` and `provenance.json`, and the committed comparison and specification files;
- for npm, the panel manifest;
- for the grid, the grid manifest. Its hash `65814ced…` is of the file as checked out on this machine, with
  CRLF line endings, as `RESULTS-synthetic.md` explains.

**When and where it ran.** The command ran from 05:29:31 to 05:37:45 UTC on 2026-10-16, on the CPU, at HEAD
`ff8c5e8`. There was no uncommitted change under `scripts/study2_inference.py` or `pulsegraph/`. It used NumPy
2.5.3, SciPy 1.18.1 and pandas 2.3.3.

**Regeneration.** The command needs the 749 checkpoints, which are not in the tree; their SHA-256 values are
in each run's `run.json`. It refuses to overwrite its outputs, so a rerun takes a new directory. From the
repository root, in PowerShell:

```powershell
.\.venv\Scripts\python.exe reports\study2-posthoc-dynamic-occurrence\dynamic_occurrence.py --npm reports\study2-npm\run-2026-10-15 --synthetic reports\study2-synthetic-2026-10-15 --out <new directory>
```

The tables above are what it prints.

**Tests.** `tests/test_study2_dynamic_occurrence.py` runs on toy runs of both components, built by the
registered run path. It checks that:

- the wrapper with p_dyn equal to the Jeffreys p reproduces the registered hurdle's laws, deciles and QScore9
  exactly, window by window and through the whole family;
- a window whose completed law has F(0) = 1 uses delta_1;
- p_dyn is `dynamic_count`'s discounted a_B / (a_B + b_B), recomputed from the context, and equals the
  Jeffreys p where `dynamic_count` falls back;
- the deciles follow the registered inversion, checked by an independent scan;
- the differences, BH and the seeds follow the registered aggregation and derivation;
- a changed checkpoint is refused;
- the command writes its outputs once, with LF line endings, and refuses to overwrite them.

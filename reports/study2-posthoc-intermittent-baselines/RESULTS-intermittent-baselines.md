# Post hoc and descriptive: the intermittent-demand baselines and the fourth factorial cell, scored from the saved forecasts

Everything on this page follows `SPEC.md` beside it (SHA-256
`ca645c02a2576cff174d42a4d2d2089242423d32063ea1cdad39078168687532`), which was fixed at 2026-10-17 07:44 UTC,
after the registered scores of all three runs had been seen and before any score on this page existed. It is
**post hoc and descriptive**. It adds no test to E01 to E18, S01 to S06 or R01 to R36, applies no multiplicity
correction, draws no verdict and replaces nothing registered. No model was run and nothing was refitted to a
target. Every new forecast is built from the context through its origin alone, and every reference score is
the one its run saved. No file in any run directory changed. The command ran on 2026-10-17 from 07:55:09 to
08:01:03 UTC: 353 s by its own clock and 356 s by the shell's, with six processes for the windows.

## What was computed

**The TSB hurdle** (`tsb_hurdle`) is the primary descriptive baseline. TSB (Teunter, Syntetos and Babai, 2011)
smooths the occurrence indicator on every context day and the demand size on demand days only. Each level
starts at its first value, as `statsforecast` 2.1.1 starts it:

- occurrence: p_1 = d_1 and p_t = 0.1 d_t + 0.9 p_(t-1), with d_t = 1[y_t > 0];
- size: z_1 = s_1 and z_j = 0.1 s_j + 0.9 z_(j-1), over the positive values s_j in time order.

The forecast holds the origin values over the horizon. Its law is the registered count hurdle with these two
estimates in place of the 28-day ones: P(Y = 0) = 1 − p_T, and on positive days Y = 1 + Poisson(max(0, z_m −
1)). `hurdle_count_28` has the same form with the 28-day Jeffreys occurrence and the 28-day positive mean. The
two therefore differ in their occurrence and size estimates and in nothing else. A context with no positive day
gives a point mass at zero. The sensitivities `tsb_hurdle_a005` and `tsb_hurdle_a020` set both constants to
0.05 and 0.2. In every window the product p_T z_m equals `statsforecast`'s own TSB forecast.

**The field's point methods** (`croston_classic`, `croston_sba`, `adida`) are `statsforecast` 2.1.1 with its
defaults on the full context. Each is scored as a point mass at its forecast rounded half up. A point mass is a
poor probabilistic forecast by construction: under it, QScore9 and the discrete CRPS both equal the absolute
error. These methods appear in one table per panel and nowhere else.

**The fourth factorial cell** on npm and the grid (`<model>_occurrence_model_size_count`) is built exactly as
Study 3 registered it. For each target day it takes the model's own occurrence 1 − F(0) from its saved
completed law and the saved `hurdle_count_28` positive law. On NYC 311 the run saved this variant, and its
contrasts are the run's own declared secondaries. They are shown below as the run wrote them, not recomputed,
and are marked "run's own".

**What each contrast isolates:**

| Variant | Reference | What differs |
|---|---|---|
| `tsb_hurdle` | `<model>_completed` | Both laws: TSB's occurrence and shifted Poisson against the model's whole completed law |
| `tsb_hurdle` | `<model>_hurdle` | Both: TSB's occurrence and shifted Poisson against the Jeffreys occurrence with the model's positive law |
| `tsb_hurdle` | `<model>_hurdle_dynamic` (NYC 311) | Both: TSB's occurrence and shifted Poisson against the discounted occurrence with the model's positive law |
| `tsb_hurdle` | `hurdle_count_28` | Only the two estimates, occurrence and size level; the form of the law is the same |
| `tsb_hurdle` | `dynamic_count` | The occurrence (TSB at 0.1 against the Beta-Bernoulli discounted at 0.98) and the size law (shifted Poisson against shifted negative binomial) |
| `<model>_occurrence_model_size_count` | `<model>_completed` | Only the positive law: a shifted Poisson against the model's own. The occurrence Brier scores are equal |
| `<model>_occurrence_model_size_count` | `hurdle_count_28` | Only the occurrence: the model's 1 − F(0) against the Jeffreys estimate, under the same count positive law |

## How to read the tables

- **Differences** are variant minus reference. All four scores are losses, so a negative difference favors the
  variant.
- **Aggregation** is the registered one. Origins are averaged within series and horizon. On npm and NYC 311
  the series of a stratum, or of the whole panel (`all`), weigh equally. On the grid each cell has 30 series,
  one per replicate; `all` pools the 18 cells with equal weight within each replicate and has the 30 replicate
  blocks as its entities (all 540 series).
- **Group labels** carry n. The mark † flags npm's very sparse stratum, whose 9 series are below the
  ten-series rule (Study 3's rule for a testable stratum). Its rows are reported like every other row, and
  every row on this page is descriptive.
- **A full cell** reads "mean difference [95% interval]; median difference; lower / tied / higher; raw p":
  - the interval is the 20,000-replicate entity bootstrap;
  - "lower / tied / higher" counts the entities where the variant's score is below, equal to or above the
    reference's;
  - raw p is the two-sided approximate Wilcoxon signed-rank test with zero differences omitted, and p = 1
    when all are zero. There is no adjustment and no verdict;
  - "n 208:" in front of a cell means one entity has no certified discrete CRPS. That entity is the largest npm
    series, `aggregate-error`, whose counts lie beyond the certification limit of k = 1,000,000 (dated
    addition 5).
- **A compact cell** reads "mean difference / median difference (lower / tied / higher)".
- **A grid cell matrix** reads "mean difference / median difference (series lower, of 30)".
- **A median of exactly zero has no sign.** Where a mean and a median disagree in sign, both are shown, and the
  counts say which side the typical series is on.
- **npm means are carried by the largest series**, as in the registered npm results (`aggregate-error`, 7.6
  million downloads a day). The medians and counts describe the typical series.

## Checks

Every check below passed before any output was written.

- **The runs.**
  - Each run was read by its registered inference reader: complete, its identity, authorized for its committed
    family and specification.
  - Every checkpoint matches the SHA-256 its `run.json` records: 209, 540 and 300 checkpoints.
  - The two inference scripts are byte for byte the ones each run's `inference/provenance.json` records.
  - The saved scores, passed through the registered functions, reproduce all three runs'
    `inference/inference.csv` and `inference/paired_entities.csv` byte for byte.
- **The contexts.**
  - npm and NYC 311 contexts were rebuilt by the runner's own loader from the readiness record in `run.json`.
    The target signals are read only through their verified completeness document, every file is checked
    against the hash the record names, and each series' prefix is checked against the frozen
    `context.parquet`.
  - The grid's series were rebuilt by the registered generator, checked against the committed manifest.
  - In all 1,254 npm, 3,240 grid and 1,800 NYC 311 windows, the rebuilt context's mean equals the saved
    `context_mean` exactly and the rebuilt target equals the saved target.
  - `count_laws` on the rebuilt context reproduces the saved `hurdle_count_28` and `dynamic_count` laws exactly.
- **NYC 311's fourth cell.** In all 5,400 NYC 311 model windows, the saved fourth-cell laws equal the ones
  rebuilt from the saved completed and `hurdle_count_28` laws.
- **TSB.** In all 18,882 fits (6,294 windows, three pairs of constants), p_T z_m equals `statsforecast`'s TSB
  forecast within a relative 1e-12. The largest gap is 4.9e-16.
- **The accounting.** The three accounting parts sum to QScore9 within 4.7e-10 on npm and 7.1e-15 on the grid
  and on NYC 311.
- **Contexts with no positive day:** 6 npm windows, 114 grid windows and 104 NYC 311 windows. There TSB is a
  point mass at zero, and so are the three point methods.
- **The NYC 311 rows marked "run's own"** come from the run's `inference/secondary_strata_contrasts.csv` and
  `inference/secondary_pooled_contrasts.csv`. Both files match the hashes in the run's provenance.
- **The tests.** `tests/test_posthoc_intermittent_baselines.py` holds 18 tests on toy runs of all three panels
  and on synthetic series:
  - the TSB recursions against `statsforecast`'s point forecast and against each of its two smoothings;
  - the decay of the TSB occurrence over 28 zero days, (1 − a)^28;
  - the TSB law with the Jeffreys occurrence and the 28-day size reproduces `hurdle_count_28`'s law and every
    score exactly;
  - the fourth cell with the completed positive law in place of the count law reproduces the completed
    control's deciles and QScore9 exactly;
  - every law has total mass one, and the TSB law has mean p_T z_m;
  - a point method's scores are the absolute error.
- **An independent check.** It used a separate script with plain NumPy and SciPy, reading only the written
  windows, the runs' own `inference/series_scores.csv` and the raw signals.
  - 1,200 sampled contrast rows (400 per panel) reproduce their n, mean, median, lower / tied / higher and raw p
    exactly, and their intervals within 4.3e-14.
  - 60 NYC 311 windows of the TSB hurdle, rebuilt by hand from the signals, give the same QScore9 exactly.

## The reading, post hoc and descriptive

The TSB hurdle is not tested here; what follows describes where it stands. On dense series it is far behind
every model's completed forecast on both real panels. It is lower on 18 or 19 of the 100 dense npm series at a
week and 10 to 12 at a month, with medians +0.34 to +0.53. On NYC 311 it is lower on 19 to 22 and 9 to 12 of
100, with medians +0.080 to +0.12. Every one of these means is positive too. On the grid pooled over its cells
it is lower on 6 to 9 of the 30 replicate blocks. Against the registered count baselines, on dense series, it
is about level. It is lower than `hurdle_count_28` on 61 and 56 of the dense npm series and 52 and 46 of the
NYC 311 ones, with medians −0.032, −0.030, −0.0032 and +0.0062. It is lower than `dynamic_count` on 47 and 48
(npm) and 47 and 30 (NYC 311). On the grid, `dynamic_count` beats it in 23 and 28 of the 30 blocks. The
classical method a forecasting reader looks for first thus stands where the registered count baselines stand:
well behind the models on dense series. On sparse npm series at a week it is lower than the models' completed
forecasts for the typical series, on 77, 61 and 74 of 100 with medians −0.029, −0.0058 and −0.027, although
the means, +0.23 to +0.24, are carried by a few series the other way. There it is level with
`hurdle_count_28`: 49 lower, 2 tied, 49 higher, median zero. At a month that advantage is gone: 50, 25 and 41
of 100. On sparse NYC 311 series it is a little behind the models at both horizons, lower on 27 to 46 of 100
with medians 0 to +0.0043 and means +0.0020 to +0.0097, and level with `hurdle_count_28` (medians zero). On
very sparse NYC 311 series, in every row of the TSB hurdle 66 to 76 of the 100 series are exact ties and every
median is zero. This is the blindness the registered family met. On the occurrence Brier score the TSB
occurrence beats the models' completed zero mass there on 65 to 68 of 100. Those completed laws sit on the
completion floor: every decile is zero on 86 to 98 percent of target days, and their mean 1 − F(0) is 0.068 to
0.077 against 0.039 to 0.040 of target days positive and 0.036 for TSB. The slower constant, 0.05, changes
little on dense series and does better where activity is sparse or persistent. On sparse npm series at a month
it is lower than the completed controls on 62, 38 and 49 of 100, against 50, 25 and 41 at 0.1. On the grid at
a month it is lower on 14, 13 and 16 of 30, against 7, 6 and 8. The faster constant, 0.2, loses ground almost
everywhere: on sparse npm at a week it is lower than the completed controls on 63, 46 and 60 of 100. The
fourth cell on npm and the grid repeats NYC 311's positive-law result. With a shifted Poisson in place of its
own positive law the model is far worse on dense series: higher on 79 to 94 of the 100 dense npm series
(medians +0.39 to +0.56), and higher on 19 to 28 of the 30 grid blocks even though the grid's generator draws
positive days from a shifted Poisson. On sparse npm series at a week the count law is lower for the typical
series, on 55, 56 and 61 of 100 with medians −0.0042, −0.0032 and −0.014, while the means, +0.28 to +0.40, go
the other way. Its occurrence contrast does not repeat NYC 311's. On NYC 311, under the count law, the model's
own zero mass was the better occurrence on 62 to 73 of the 100 dense series. On dense npm series it is the
better one on 48, 58 and 62 of 100 at a week and 43, 48 and 60 at a month, with means all below zero and every
interval spanning it. On the grid it is the better one on 18, 21 and 15 of 30 at a week and 10, 13 and 7 at a
month. The Brier score, which reads the occurrence alone, favors the model's zero mass at a week on both
panels: 68, 62 and 54 of 100 on dense npm, 19, 23 and 19 of 30 on the grid. At a month it favors the Jeffreys
estimate: the model's zero mass is lower on only 42, 43 and 38 of 100, and on 15, 13 and 12 of 30. Beside the
registered secondaries this is, at a month, the pattern the second reading of the accounting trade predicts.
There the same Jeffreys estimate, laid over the models' truncated positive laws, raises QScore9 against the
control on 57 to 66 of the 100 dense npm series and on 24 or 25 of the 30 grid blocks, though on the
occurrence itself it is no worse. At a week on the grid, for Chronos-2 and TimesFM 3, both positive laws put
the Jeffreys estimate behind, as the first reading says: 18 and 21 of 30 under the count law, 24 under the
truncated law. For TimesFM 2.5 the count law splits 15 to 15. On sparse npm series at a week the Jeffreys
estimate is the better occurrence under the count law too. The model's zero mass is lower on 21, 49 and 37 of
100, and on the Brier score on 15, 36 and 30. This is consistent with the registered substitution's secondary
gain there (81, 60 and 66 of 100) being an occurrence effect. None of these comparisons is confirmatory; each
is one of many rows read after the registered results were known.

**Two notes on the numbers.**

- **Near-zero differences.** A small number of entity differences are not exactly zero but below 1e-12: 74 of
  80,160 on npm and 138 of 122,400 on NYC 311 among the pooled rows, and 17 medians across all tables (for
  example 6.94e-18). They come from averaging equal window scores in a different order. The registered
  aggregation counts them as lower or higher, and so do these tables; read them as zero.
- **The point methods.** Their QScore9 is the absolute error of a rounded point. That a point mass loses to a
  law is what the score is built to say, and it says nothing about these methods as point forecasts.

## npm

209 series: 100 dense, 100 sparse and 9 very sparse (marked †). Entities are series.

### npm: `tsb_hurdle` against every reference, four scores (full cells)

| Group | h | Reference | QScore9 | Context-scaled QScore9 | Occurrence Brier | Discrete CRPS |
|---|---|---|---|---|---|---|
| all (n = 209) | 7 | `chronos2_completed` | 4669 [29.47, 13,917]; median 0.006349; 99 / 1 / 109; p 3.54e-05 | 0.07968 [0.0466, 0.1144]; median 0.005474; 98 / 1 / 110; p 0.00477 | -0.006721 [-0.01018, -0.003282]; median -0.003124; 115 / 0 / 94; p 0.000155 | n 208: 57.74 [22.95, 101.6]; median 0.01567; 90 / 0 / 118; p 4.8e-07 |
| all (n = 209) | 7 | `timesfm3_completed` | 5020 [29.69, 14,965]; median 0.02116; 80 / 7 / 122; p 3.31e-08 | 0.09167 [0.0621, 0.1232]; median 0.0127; 80 / 7 / 122; p 1.13e-06 | 0.001086 [-0.001845, 0.003942]; median 0.0007572; 93 / 0 / 116; p 0.203 | n 208: 58.95 [23.43, 104.8]; median 0.02115; 70 / 0 / 138; p 5.65e-11 |
| all (n = 209) | 7 | `timesfm2p5_completed` | 5529 [30.06, 16,495]; median 0.008466; 95 / 1 / 113; p 7.87e-05 | 0.08266 [0.05182, 0.1163]; median 0.007407; 95 / 1 / 113; p 0.00766 | -0.001592 [-0.004788, 0.001631]; median 6.9e-05; 101 / 0 / 108; p 0.457 | n 208: 58.15 [23.01, 103.7]; median 0.006729; 95 / 0 / 113; p 4.06e-05 |
| all (n = 209) | 7 | `chronos2_hurdle` | 4517 [29.7, 13,464]; median 0.0254; 67 / 4 / 138; p 6.25e-12 | 0.1017 [0.07094, 0.1356]; median 0.01944; 67 / 4 / 138; p 4.86e-11 | 0.00305 [0.001053, 0.005091]; median 0.001015; 90 / 0 / 119; p 0.0101 | n 208: 57.25 [22.76, 100.3]; median 0.02565; 57 / 0 / 151; p 6.43e-16 |
| all (n = 209) | 7 | `timesfm3_hurdle` | 4843 [29.68, 14,441]; median 0.01481; 72 / 10 / 127; p 5.24e-09 | 0.09838 [0.06867, 0.1316]; median 0.01058; 72 / 10 / 127; p 2.64e-08 | 0.00305 [0.001052, 0.00508]; median 0.001015; 90 / 0 / 119; p 0.0101 | n 208: 58.3 [22.67, 104.5]; median 0.02267; 65 / 0 / 143; p 4.61e-13 |
| all (n = 209) | 7 | `timesfm2p5_hurdle` | 5275 [29.08, 15,736]; median 0.006349; 88 / 5 / 116; p 1.94e-05 | 0.08878 [0.05758, 0.1233]; median 0.005291; 89 / 5 / 115; p 0.000569 | 0.00305 [0.001027, 0.005138]; median 0.001015; 90 / 0 / 119; p 0.0101 | n 208: 57.25 [23.2, 100.2]; median 0.01244; 86 / 0 / 122; p 1.87e-06 |
| all (n = 209) | 7 | `hurdle_count_28` | -572.5 [-1716, 1.674]; median -0.004233; 113 / 6 / 90; p 0.0553 | -0.02938 [-0.05511, -0.008768]; median -0.002116; 112 / 6 / 91; p 0.203 | 0.00305 [0.001046, 0.005135]; median 0.001015; 90 / 0 / 119; p 0.0101 | n 208: -0.7775 [-8.529, 5.819]; median 0.003084; 91 / 0 / 117; p 0.408 |
| all (n = 209) | 7 | `dynamic_count` | -1778 [-5328, -1.428]; median 0; 104 / 6 / 99; p 0.838 | 0.01077 [-0.004076, 0.02747]; median 0; 104 / 6 / 99; p 0.862 | 0.0003021 [-0.002466, 0.002998]; median 0.0001059; 102 / 0 / 107; p 0.558 | n 208: -5.497 [-12.09, -0.5965]; median 0.000506; 103 / 0 / 105; p 0.817 |
| all (n = 209) | 30 | `chronos2_completed` | 6124 [30.43, 18,279]; median 0.04247; 64 / 1 / 144; p 8.83e-17 | 0.1135 [0.08334, 0.1461]; median 0.02539; 65 / 1 / 143; p 4.38e-16 | -0.0005978 [-0.00255, 0.001327]; median -3.688e-05; 106 / 0 / 103; p 0.862 | n 208: 61.09 [23.57, 108.9]; median 0.06381; 56 / 0 / 152; p 9.01e-20 |
| all (n = 209) | 30 | `timesfm3_completed` | 6391 [30.94, 19,082]; median 0.04741; 37 / 8 / 164; p 2.24e-23 | 0.1182 [0.08964, 0.1504]; median 0.02793; 38 / 8 / 163; p 3.28e-23 | 0.002078 [0.000324, 0.003801]; median 0.001682; 79 / 0 / 130; p 0.000163 | n 208: 62.48 [23.75, 111.1]; median 0.05857; 34 / 0 / 174; p 2.44e-25 |
| all (n = 209) | 30 | `timesfm2p5_completed` | 6500 [29.14, 19,409]; median 0.03778; 57 / 1 / 151; p 2.84e-19 | 0.1122 [0.08421, 0.1433]; median 0.02395; 58 / 1 / 150; p 1.22e-18 | 0.00163 [-0.00018, 0.003453]; median 0.001651; 88 / 0 / 121; p 0.0103 | n 208: 58.97 [23.29, 104.3]; median 0.04415; 50 / 0 / 158; p 1.01e-20 |
| all (n = 209) | 30 | `chronos2_hurdle` | 6034 [29.69, 18,011]; median 0.03852; 54 / 5 / 150; p 1.04e-19 | 0.1159 [0.08585, 0.1485]; median 0.02423; 54 / 5 / 150; p 5.42e-20 | 0.002605 [0.001419, 0.003839]; median 0.001291; 65 / 0 / 144; p 3.85e-06 | n 208: 60.42 [23.1, 108.4]; median 0.05228; 42 / 0 / 166; p 1.34e-22 |
| all (n = 209) | 30 | `timesfm3_hurdle` | 6263 [30.63, 18,699]; median 0.0516; 39 / 8 / 162; p 6.57e-24 | 0.1169 [0.08876, 0.1486]; median 0.02459; 39 / 8 / 162; p 6.9e-24 | 0.002605 [0.001396, 0.003803]; median 0.001291; 65 / 0 / 144; p 3.85e-06 | n 208: 61.54 [23.64, 109.1]; median 0.06831; 37 / 0 / 171; p 1.27e-25 |
| all (n = 209) | 30 | `timesfm2p5_hurdle` | 6389 [28.59, 19,077]; median 0.05235; 42 / 6 / 161; p 6.42e-23 | 0.1106 [0.08293, 0.1411]; median 0.01877; 43 / 6 / 160; p 6.34e-22 | 0.002605 [0.001436, 0.003806]; median 0.001291; 65 / 0 / 144; p 3.85e-06 | n 208: 57.67 [22.72, 102.4]; median 0.05473; 44 / 0 / 164; p 2.44e-22 |
| all (n = 209) | 30 | `hurdle_count_28` | -528.8 [-1587, 1.904]; median -0.004938; 113 / 12 / 84; p 0.0134 | -0.02967 [-0.05292, -0.01125]; median -0.002469; 114 / 11 / 84; p 0.0178 | 0.002605 [0.001425, 0.003824]; median 0.001291; 65 / 0 / 144; p 3.85e-06 | n 208: 0.1615 [-6.483, 5.556]; median -0.001884; 115 / 0 / 93; p 0.335 |
| all (n = 209) | 30 | `dynamic_count` | -1121 [-3356, -2.069]; median 0.007407; 70 / 15 / 124; p 0.0246 | 0.0155 [0.003976, 0.02852]; median 0.004938; 71 / 14 / 124; p 0.000617 | 0.003871 [0.002176, 0.005522]; median 0.00207; 52 / 0 / 157; p 3.04e-11 | n 208: -5.476 [-10.7, -1.327]; median 0.005248; 70 / 0 / 138; p 0.00262 |
| dense (n = 100) | 7 | `chronos2_completed` | 9759 [63.85, 29,090]; median 0.3878; 19 / 0 / 81; p 2.37e-12 | 0.1706 [0.1128, 0.2297]; median 0.07872; 18 / 0 / 82; p 2.74e-11 | 0.00384 [-9.448e-05, 0.008021]; median 0.001733; 31 / 0 / 69; p 0.0239 | n 99: 121 [49.42, 209.9]; median 0.3507; 13 / 0 / 86; p 6.7e-14 |
| dense (n = 100) | 7 | `timesfm3_completed` | 10,492 [63.41, 31,286]; median 0.3656; 18 / 0 / 82; p 4.8e-13 | 0.1818 [0.1331, 0.2353]; median 0.07425; 18 / 0 / 82; p 3.18e-12 | 0.004439 [0.001005, 0.007951]; median 0.001795; 36 / 0 / 64; p 0.0111 | n 99: 123.6 [48.62, 218.1]; median 0.3512; 14 / 0 / 85; p 1.07e-14 |
| dense (n = 100) | 7 | `timesfm2p5_completed` | 11,554 [63.05, 34,472]; median 0.3402; 18 / 0 / 82; p 1.68e-12 | 0.177 [0.1276, 0.23]; median 0.08348; 18 / 0 / 82; p 1.88e-11 | 0.001288 [-0.003153, 0.0054]; median 0.0008277; 38 / 0 / 62; p 0.189 | n 99: 121.9 [49.34, 215.1]; median 0.3065; 17 / 0 / 82; p 7.75e-13 |
| dense (n = 100) | 7 | `chronos2_hurdle` | 9441 [63.01, 28,141]; median 0.2884; 18 / 0 / 82; p 2.68e-12 | 0.1752 [0.1236, 0.2308]; median 0.07594; 18 / 0 / 82; p 4.93e-12 | 0.001082 [-0.001483, 0.003797]; median 0.0006104; 45 / 0 / 55; p 0.419 | n 99: 120 [49.73, 209.1]; median 0.3047; 14 / 0 / 85; p 2.13e-13 |
| dense (n = 100) | 7 | `timesfm3_hurdle` | 10,122 [62.82, 30,179]; median 0.3407; 20 / 0 / 80; p 5.98e-12 | 0.1767 [0.1272, 0.2304]; median 0.06422; 20 / 0 / 80; p 9.22e-12 | 0.001082 [-0.001539, 0.003894]; median 0.0006104; 45 / 0 / 55; p 0.419 | n 99: 122.2 [48.75, 214.4]; median 0.3312; 15 / 0 / 84; p 3.24e-13 |
| dense (n = 100) | 7 | `timesfm2p5_hurdle` | 11,024 [61.29, 32,881]; median 0.2704; 21 / 0 / 79; p 1.12e-11 | 0.1744 [0.1263, 0.2278]; median 0.07399; 22 / 0 / 78; p 4.16e-11 | 0.001082 [-0.00156, 0.003811]; median 0.0006104; 45 / 0 / 55; p 0.419 | n 99: 120 [49.31, 211]; median 0.2601; 20 / 0 / 79; p 2.94e-12 |
| dense (n = 100) | 7 | `hurdle_count_28` | -1196 [-3586, 3.892]; median -0.03175; 61 / 0 / 39; p 0.0201 | -0.04383 [-0.08792, -0.01021]; median -0.004056; 60 / 0 / 40; p 0.0559 | 0.001082 [-0.001513, 0.003821]; median 0.0006104; 45 / 0 / 55; p 0.419 | n 99: -1.531 [-17.79, 12.4]; median 0.004655; 49 / 0 / 50; p 0.955 |
| dense (n = 100) | 7 | `dynamic_count` | -3717 [-11,135, -3.182]; median 0.01323; 47 / 1 / 52; p 0.635 | 0.01001 [-0.01322, 0.03604]; median 0.003643; 47 / 1 / 52; p 0.745 | 0.004209 [0.0009329, 0.007626]; median 0.001162; 41 / 0 / 59; p 0.0106 | n 99: -11.64 [-25.29, -1.385]; median 0.02003; 43 / 0 / 56; p 0.944 |
| dense (n = 100) | 30 | `chronos2_completed` | 12,799 [65.14, 38,199]; median 0.4956; 10 / 0 / 90; p 1.58e-14 | 0.1951 [0.1423, 0.2518]; median 0.09999; 10 / 0 / 90; p 1.49e-14 | 0.0006311 [-0.002437, 0.00364]; median 0.0005315; 45 / 0 / 55; p 0.117 | n 99: 128 [49.65, 224.8]; median 0.5254; 8 / 0 / 91; p 1.4e-15 |
| dense (n = 100) | 30 | `timesfm3_completed` | 13,358 [65.9, 39,880]; median 0.5102; 10 / 0 / 90; p 8.58e-16 | 0.2025 [0.1538, 0.2567]; median 0.1024; 10 / 0 / 90; p 4.12e-16 | 0.001052 [-0.001729, 0.003813]; median 0.0005467; 45 / 0 / 55; p 0.136 | n 99: 131 [50.85, 231.2]; median 0.5124; 8 / 0 / 91; p 2.23e-16 |
| dense (n = 100) | 30 | `timesfm2p5_completed` | 13,584 [62.64, 40,564]; median 0.5288; 12 / 0 / 88; p 1.87e-15 | 0.1916 [0.1435, 0.2446]; median 0.1104; 12 / 0 / 88; p 2.28e-15 | -0.0006702 [-0.003826, 0.00242]; median -0.0003265; 53 / 0 / 47; p 0.888 | n 99: 123.6 [49.68, 216.7]; median 0.4908; 9 / 0 / 90; p 4.33e-16 |
| dense (n = 100) | 30 | `chronos2_hurdle` | 12,610 [62.17, 37,640]; median 0.5037; 11 / 0 / 89; p 1.05e-14 | 0.1967 [0.1463, 0.2525]; median 0.1023; 11 / 0 / 89; p 3.74e-15 | 0.002183 [0.0004019, 0.004062]; median 0.0006207; 30 / 0 / 70; p 0.00257 | n 99: 126.6 [49.8, 223.1]; median 0.4607; 8 / 0 / 91; p 9.38e-16 |
| dense (n = 100) | 30 | `timesfm3_hurdle` | 13,089 [62.8, 39,070]; median 0.5325; 9 / 0 / 91; p 1.85e-16 | 0.1995 [0.1509, 0.253]; median 0.1015; 9 / 0 / 91; p 2.76e-16 | 0.002183 [0.000391, 0.004053]; median 0.0006207; 30 / 0 / 70; p 0.00257 | n 99: 129 [51.93, 226.3]; median 0.4626; 7 / 0 / 92; p 5.95e-17 |
| dense (n = 100) | 30 | `timesfm2p5_hurdle` | 13,353 [61.46, 39,874]; median 0.5437; 8 / 0 / 92; p 1.07e-16 | 0.1889 [0.1402, 0.2421]; median 0.1099; 8 / 0 / 92; p 7.25e-16 | 0.002183 [0.0004006, 0.004053]; median 0.0006207; 30 / 0 / 70; p 0.00257 | n 99: 120.9 [48.85, 212.1]; median 0.5002; 8 / 0 / 91; p 1.21e-16 |
| dense (n = 100) | 30 | `hurdle_count_28` | -1105 [-3315, 4.022]; median -0.02963; 56 / 1 / 43; p 0.084 | -0.03613 [-0.07309, -0.00747]; median -0.004845; 57 / 0 / 43; p 0.158 | 0.002183 [0.0004068, 0.004034]; median 0.0006207; 30 / 0 / 70; p 0.00257 | n 99: 0.4558 [-13.39, 11.83]; median -0.002239; 50 / 0 / 49; p 0.856 |
| dense (n = 100) | 30 | `dynamic_count` | -2343 [-7012, -4.544]; median 0.004938; 48 / 0 / 52; p 0.519 | 0.005397 [-0.01441, 0.02868]; median 0.00105; 48 / 0 / 52; p 0.921 | 0.003495 [0.001373, 0.005729]; median 0.001226; 25 / 0 / 75; p 8.37e-05 | n 99: -11.6 [-22.37, -3.021]; median 0.00321; 48 / 0 / 51; p 0.732 |
| sparse (n = 100) | 7 | `chronos2_completed` | 0.2296 [-0.0292, 0.712]; median -0.0291; 77 / 0 / 23; p 9.48e-06 | -0.009389 [-0.03589, 0.02486]; median -0.02857; 77 / 0 / 23; p 1.61e-06 | -0.01733 [-0.02236, -0.01222]; median -0.01611; 78 / 0 / 22; p 2.19e-09 | 0.2261 [-0.01375, 0.6705]; median -0.02266; 72 / 0 / 28; p 0.000153 |
| sparse (n = 100) | 7 | `timesfm3_completed` | 0.2306 [-0.01615, 0.6919]; median -0.00582; 61 / 2 / 37; p 0.0385 | 0.00355 [-0.02054, 0.03425]; median -0.005291; 61 / 2 / 37; p 0.0412 | -0.002718 [-0.007415, 0.001789]; median -0.001623; 54 / 0 / 46; p 0.421 | 0.2194 [-0.009327, 0.6441]; median -0.002739; 54 / 0 / 46; p 0.371 |
| sparse (n = 100) | 7 | `timesfm2p5_completed` | 0.2399 [-0.03246, 0.7396]; median -0.02698; 74 / 0 / 26; p 6.93e-07 | -0.009761 [-0.03912, 0.02877]; median -0.02593; 74 / 0 / 26; p 5.21e-07 | -0.004826 [-0.009756, 4.92e-05]; median -0.00447; 58 / 0 / 42; p 0.0298 | 0.2095 [-0.03652, 0.6642]; median -0.02423; 73 / 0 / 27; p 1.12e-06 |
| sparse (n = 100) | 7 | `chronos2_hurdle` | 0.2849 [0.01491, 0.7809]; median 0.002646; 47 / 0 / 53; p 0.331 | 0.03136 [0.002795, 0.07039]; median 0.002646; 47 / 0 / 53; p 0.364 | 0.005902 [0.002979, 0.008954]; median 0.002928; 38 / 0 / 62; p 0.000624 | 0.2734 [0.02385, 0.7417]; median 0.006617; 37 / 0 / 63; p 0.00149 |
| sparse (n = 100) | 7 | `timesfm3_hurdle` | 0.2618 [0.007164, 0.7327]; median -0.0005291; 50 / 6 / 44; p 0.523 | 0.02297 [-0.004495, 0.06027]; median -0.0005291; 50 / 6 / 44; p 0.583 | 0.005902 [0.00304, 0.008942]; median 0.002928; 38 / 0 / 62; p 0.000624 | 0.2511 [0.01262, 0.6928]; median 0.001805; 44 / 0 / 56; p 0.144 |
| sparse (n = 100) | 7 | `timesfm2p5_hurdle` | 0.2528 [-0.02009, 0.7545]; median -0.01164; 65 / 1 / 34; p 0.000528 | 0.005195 [-0.02617, 0.04729]; median -0.01164; 65 / 1 / 34; p 0.000412 | 0.005902 [0.003005, 0.008932]; median 0.002928; 38 / 0 / 62; p 0.000624 | 0.2237 [-0.02183, 0.6777]; median -0.007896; 60 / 0 / 40; p 0.00943 |
| sparse (n = 100) | 7 | `hurdle_count_28` | -0.06344 [-0.1756, 0.005662]; median 0; 49 / 2 / 49; p 0.576 | -0.003316 [-0.01424, 0.005731]; median 0; 49 / 2 / 49; p 0.559 | 0.005902 [0.002978, 0.008937]; median 0.002928; 38 / 0 / 62; p 0.000624 | -0.03576 [-0.1032, 0.00898]; median 0.003579; 35 / 0 / 65; p 0.0212 |
| sparse (n = 100) | 7 | `dynamic_count` | 0.08021 [-0.002667, 0.228]; median -0.005291; 55 / 3 / 42; p 0.34 | 0.007611 [-0.008717, 0.03042]; median -0.003704; 55 / 3 / 42; p 0.346 | -0.002406 [-0.006377, 0.001358]; median -0.001611; 58 / 0 / 42; p 0.23 | 0.06696 [-0.0002839, 0.1866]; median -0.005227; 57 / 0 / 43; p 0.348 |
| sparse (n = 100) | 30 | `chronos2_completed` | 0.2932 [0.03089, 0.7846]; median -0.0003704; 50 / 0 / 50; p 0.0467 | 0.0349 [0.01222, 0.06512]; median -0.0009877; 51 / 0 / 49; p 0.104 | -0.001586 [-0.004212, 0.001004]; median -0.0008621; 56 / 0 / 44; p 0.171 | 0.2861 [0.03181, 0.766]; median 0.002767; 43 / 0 / 57; p 0.00142 |
| sparse (n = 100) | 30 | `timesfm3_completed` | 0.276 [0.03499, 0.7297]; median 0.007407; 25 / 4 / 71; p 2.22e-07 | 0.03695 [0.01639, 0.0634]; median 0.007407; 26 / 4 / 70; p 1.2e-06 | 0.003233 [0.0008967, 0.005517]; median 0.002812; 30 / 0 / 70; p 0.000225 | 0.2694 [0.03255, 0.7168]; median 0.006318; 21 / 0 / 79; p 5.61e-09 |
| sparse (n = 100) | 30 | `timesfm2p5_completed` | 0.2861 [0.03259, 0.7632]; median 0.003827; 41 / 0 / 59; p 0.000652 | 0.03566 [0.01425, 0.06257]; median 0.00358; 42 / 0 / 58; p 0.00233 | 0.003986 [0.002046, 0.006026]; median 0.003745; 31 / 0 / 69; p 0.000158 | 0.2551 [0.02489, 0.6855]; median 0.003783; 36 / 0 / 64; p 0.000294 |
| sparse (n = 100) | 30 | `chronos2_hurdle` | 0.3077 [0.03037, 0.8341]; median 0.004938; 42 / 1 / 57; p 0.00027 | 0.03799 [0.01402, 0.07076]; median 0.004938; 42 / 1 / 57; p 0.000349 | 0.003564 [0.001992, 0.00519]; median 0.002267; 28 / 0 / 72; p 2.04e-05 | 0.2996 [0.03162, 0.812]; median 0.005418; 28 / 0 / 72; p 2.92e-06 |
| sparse (n = 100) | 30 | `timesfm3_hurdle` | 0.2764 [0.03449, 0.7307]; median 0.005926; 28 / 4 / 68; p 3.12e-07 | 0.03764 [0.01693, 0.06519]; median 0.005679; 28 / 4 / 68; p 6.33e-07 | 0.003564 [0.001966, 0.005185]; median 0.002267; 28 / 0 / 72; p 2.04e-05 | 0.2693 [0.03324, 0.7165]; median 0.007475; 24 / 0 / 76; p 1.27e-08 |
| sparse (n = 100) | 30 | `timesfm2p5_hurdle` | 0.2671 [0.03179, 0.7071]; median 0.004321; 33 / 1 / 66; p 2.09e-05 | 0.03461 [0.01482, 0.06013]; median 0.004198; 34 / 1 / 65; p 9.53e-05 | 0.003564 [0.001994, 0.00517]; median 0.002267; 28 / 0 / 72; p 2.04e-05 | 0.2387 [0.02578, 0.6381]; median 0.004998; 30 / 0 / 70; p 1.52e-05 |
| sparse (n = 100) | 30 | `hurdle_count_28` | -0.07568 [-0.1978, -0.004494]; median -0.002469; 54 / 6 / 40; p 0.0665 | -0.01179 [-0.02359, -0.002295]; median -0.002469; 54 / 6 / 40; p 0.0788 | 0.003564 [0.001967, 0.005187]; median 0.002267; 28 / 0 / 72; p 2.04e-05 | -0.04897 [-0.1168, -0.003995]; median -0.001654; 58 / 0 / 42; p 0.143 |
| sparse (n = 100) | 30 | `dynamic_count` | 0.1001 [0.01422, 0.2597]; median 0.007407; 22 / 11 / 67; p 8.11e-08 | 0.02242 [0.01217, 0.03532]; median 0.007407; 23 / 10 / 67; p 3.11e-08 | 0.005187 [0.002954, 0.007469]; median 0.004214; 24 / 0 / 76; p 3.42e-08 | 0.08286 [0.01444, 0.2082]; median 0.007233; 20 / 0 / 80; p 4.56e-10 |
| very_sparse (n = 9) † | 7 | `chronos2_completed` | 0.3834 [-0.0167, 1.17]; median 0.001058; 3 / 1 / 5; p 1 | 0.05907 [-0.01681, 0.1976]; median 0.001058; 3 / 1 / 5; p 1 | -0.006199 [-0.01687, 0.002961]; median -0.003679; 6 / 0 / 3; p 0.594 | 0.3114 [-0.00898, 0.9414]; median -0.003345; 5 / 0 / 4; p 0.594 |
| very_sparse (n = 9) † | 7 | `timesfm3_completed` | 0.4076 [-0.003998, 1.224]; median 0; 1 / 5 / 3; p 0.273 | 0.06974 [-0.003998, 0.2095]; median 0; 1 / 5 / 3; p 0.273 | 0.006103 [-0.002367, 0.01571]; median 0.004917; 3 / 0 / 6; p 0.214 | 0.3134 [-0.000837, 0.9355]; median 0.004166; 2 / 0 / 7; p 0.139 |
| very_sparse (n = 9) † | 7 | `timesfm2p5_completed` | 0.3952 [-0.01775, 1.206]; median 0.001058; 3 / 1 / 5; p 1 | 0.06079 [-0.01775, 0.2031]; median 0.001058; 3 / 1 / 5; p 1 | 0.002342 [-0.01041, 0.01657]; median -0.002204; 5 / 0 / 4; p 0.594 | 0.301 [-0.009198, 0.9106]; median -0.003425; 5 / 0 / 4; p 0.594 |
| very_sparse (n = 9) † | 7 | `chronos2_hurdle` | 0.4009 [-0.009289, 1.209]; median 0; 2 / 4 / 3; p 0.5 | 0.06692 [-0.009171, 0.2068]; median 0; 2 / 4 / 3; p 0.5 | -0.006784 [-0.0211, 0.005393]; median -0.004496; 7 / 0 / 2; p 0.173 | 0.3274 [-0.006126, 0.9853]; median -0.001142; 6 / 0 / 3; p 0.767 |
| very_sparse (n = 9) † | 7 | `timesfm3_hurdle` | 0.3964 [-0.009641, 1.196]; median 0; 2 / 4 / 3; p 0.686 | 0.06569 [-0.009641, 0.2048]; median 0; 2 / 4 / 3; p 0.686 | -0.006784 [-0.0211, 0.005464]; median -0.004496; 7 / 0 / 2; p 0.173 | 0.3036 [-0.006122, 0.9142]; median -0.001495; 6 / 0 / 3; p 0.767 |
| very_sparse (n = 9) † | 7 | `timesfm2p5_hurdle` | 0.3988 [-0.009289, 1.203]; median 0; 2 / 4 / 3; p 0.5 | 0.06659 [-0.009289, 0.2054]; median 0; 2 / 4 / 3; p 0.5 | -0.006784 [-0.02127, 0.005141]; median -0.004496; 7 / 0 / 2; p 0.173 | 0.3004 [-0.006123, 0.9046]; median -0.001184; 6 / 0 / 3; p 0.767 |
| very_sparse (n = 9) † | 7 | `hurdle_count_28` | -0.9111 [-2.727, 0.00341]; median 0; 3 / 4 / 2; p 0.225 | -0.1584 [-0.4688, 0.00341]; median 0; 3 / 4 / 2; p 0.225 | -0.006784 [-0.02074, 0.005179]; median -0.004496; 7 / 0 / 2; p 0.173 | -0.7291 [-2.186, 0.005085]; median -0.008484; 7 / 0 / 2; p 0.139 |
| very_sparse (n = 9) † | 7 | `dynamic_count` | 0.3256 [-0.006349, 0.9807]; median 0.007407; 2 / 2 / 5; p 0.611 | 0.05435 [-0.006349, 0.1671]; median 0.007407; 2 / 2 / 5; p 0.611 | -0.01303 [-0.04063, 0.003061]; median 0.001032; 3 / 0 / 6; p 0.678 | 0.2484 [-0.00218, 0.7453]; median 0.001302; 3 / 0 / 6; p 0.173 |
| very_sparse (n = 9) † | 30 | `chronos2_completed` | 0.4848 [-0.005158, 1.458]; median 0; 4 / 1 / 4; p 0.889 | 0.08125 [-0.005158, 0.2475]; median 0; 4 / 1 / 4; p 0.889 | -0.003273 [-0.009734, 0.002784]; median -0.003679; 5 / 0 / 4; p 0.515 | 0.4015 [-0.004753, 1.208]; median -0.001043; 5 / 0 / 4; p 0.678 |
| very_sparse (n = 9) † | 30 | `timesfm3_completed` | 0.4931 [-0.001097, 1.478]; median 0; 2 / 4 / 3; p 0.345 | 0.08428 [-0.0009877, 0.2515]; median 0; 2 / 4 / 3; p 0.345 | 0.0006491 [-0.002167, 0.003417]; median 0.0001356; 4 / 0 / 5; p 0.594 | 0.3969 [-0.002444, 1.193]; median -0.0007768; 5 / 0 / 4; p 0.953 |
| very_sparse (n = 9) † | 30 | `timesfm2p5_completed` | 0.4863 [-0.006036, 1.464]; median 0; 4 / 1 / 4; p 0.889 | 0.08092 [-0.006091, 0.2482]; median 0; 4 / 1 / 4; p 0.889 | 0.001003 [-0.004567, 0.00671]; median 0.0006378; 4 / 0 / 5; p 0.678 | 0.3878 [-0.004159, 1.166]; median -0.0004532; 5 / 0 / 4; p 0.678 |
| very_sparse (n = 9) † | 30 | `chronos2_hurdle` | 0.4959 [-0.001866, 1.487]; median 0; 1 / 4 / 4; p 0.225 | 0.08466 [-0.001866, 0.2533]; median 0; 1 / 4 / 4; p 0.225 | -0.003355 [-0.007544, 0.001128]; median -0.003847; 7 / 0 / 2; p 0.214 | 0.4075 [-0.004757, 1.228]; median -0.00141; 6 / 0 / 3; p 0.767 |
| very_sparse (n = 9) † | 30 | `timesfm3_hurdle` | 0.4717 [-0.002332, 1.416]; median 0; 2 / 4 / 3; p 0.5 | 0.08007 [-0.002332, 0.241]; median 0; 2 / 4 / 3; p 0.5 | -0.003355 [-0.007657, 0.001087]; median -0.003847; 7 / 0 / 2; p 0.214 | 0.3753 [-0.005512, 1.133]; median -0.001914; 6 / 0 / 3; p 0.594 |
| very_sparse (n = 9) † | 30 | `timesfm2p5_hurdle` | 0.4901 [-0.00192, 1.47]; median 0; 1 / 5 / 3; p 0.273 | 0.08369 [-0.00192, 0.2505]; median 0; 1 / 5 / 3; p 0.273 | -0.003355 [-0.007606, 0.001091]; median -0.003847; 7 / 0 / 2; p 0.214 | 0.3856 [-0.004726, 1.162]; median -0.001121; 6 / 0 / 3; p 0.767 |
| very_sparse (n = 9) † | 30 | `hurdle_count_28` | -0.9188 [-2.756, 0.002469]; median 0; 3 / 5 / 1; p 0.273 | -0.1566 [-0.4695, 0.002743]; median 0; 3 / 5 / 1; p 0.273 | -0.003355 [-0.007648, 0.001056]; median -0.003847; 7 / 0 / 2; p 0.214 | -0.7371 [-2.206, -0.000407]; median -0.005258; 7 / 0 / 2; p 0.0663 |
| very_sparse (n = 9) † | 30 | `dynamic_count` | 0.2827 [0.001646, 0.8416]; median 0.007407; 0 / 4 / 5; p 0.0422 | 0.0509 [0.001646, 0.1461]; median 0.007407; 0 / 4 / 5; p 0.0422 | -0.00658 [-0.02184, 0.001965]; median 0.001246; 3 / 0 / 6; p 0.594 | 0.1781 [-0.0002476, 0.5333]; median 0.001235; 2 / 0 / 7; p 0.11 |

### npm: the TSB sensitivities, QScore9 (compact cells)

| Group | h | Reference | `tsb_hurdle_a005` | `tsb_hurdle` | `tsb_hurdle_a020` |
|---|---|---|---|---|---|
| all (n = 209) | 7 | `chronos2_completed` | 5247 / 0.006349 (101 / 1 / 107) | 4669 / 0.006349 (99 / 1 / 109) | 4936 / 0.02116 (85 / 5 / 119) |
| all (n = 209) | 7 | `timesfm3_completed` | 5597 / 0.01376 (78 / 11 / 120) | 5020 / 0.02116 (80 / 7 / 122) | 5287 / 0.04127 (69 / 3 / 137) |
| all (n = 209) | 7 | `timesfm2p5_completed` | 6106 / 0.002116 (100 / 2 / 107) | 5529 / 0.008466 (95 / 1 / 113) | 5795 / 0.02328 (84 / 4 / 121) |
| all (n = 209) | 7 | `chronos2_hurdle` | 5095 / 0.02116 (58 / 7 / 144) | 4517 / 0.0254 (67 / 4 / 138) | 4784 / 0.0455 (55 / 2 / 152) |
| all (n = 209) | 7 | `timesfm3_hurdle` | 5421 / 0.01164 (69 / 16 / 124) | 4843 / 0.01481 (72 / 10 / 127) | 5110 / 0.03704 (64 / 2 / 143) |
| all (n = 209) | 7 | `timesfm2p5_hurdle` | 5852 / 0.005291 (85 / 11 / 113) | 5275 / 0.006349 (88 / 5 / 116) | 5541 / 0.03175 (75 / 2 / 132) |
| all (n = 209) | 7 | `hurdle_count_28` | 4.938 / -0.002116 (105 / 11 / 93) | -572.5 / -0.004233 (113 / 6 / 90) | -306 / 0.0127 (82 / 1 / 126) |
| all (n = 209) | 7 | `dynamic_count` | -1201 / 0 (103 / 16 / 90) | -1778 / 0 (104 / 6 / 99) | -1512 / 0.006349 (92 / 6 / 111) |
| all (n = 209) | 30 | `chronos2_completed` | 6567 / 0.04123 (73 / 1 / 135) | 6124 / 0.04247 (64 / 1 / 144) | 6202 / 0.09185 (33 / 4 / 172) |
| all (n = 209) | 30 | `timesfm3_completed` | 6834 / 0.04346 (48 / 11 / 150) | 6391 / 0.04741 (37 / 8 / 164) | 6470 / 0.1007 (22 / 3 / 184) |
| all (n = 209) | 30 | `timesfm2p5_completed` | 6942 / 0.03852 (64 / 1 / 144) | 6500 / 0.03778 (57 / 1 / 151) | 6578 / 0.08025 (28 / 3 / 178) |
| all (n = 209) | 30 | `chronos2_hurdle` | 6477 / 0.0321 (63 / 8 / 138) | 6034 / 0.03852 (54 / 5 / 150) | 6112 / 0.09284 (29 / 1 / 179) |
| all (n = 209) | 30 | `timesfm3_hurdle` | 6706 / 0.03951 (49 / 10 / 150) | 6263 / 0.0516 (39 / 8 / 162) | 6341 / 0.09407 (24 / 3 / 182) |
| all (n = 209) | 30 | `timesfm2p5_hurdle` | 6832 / 0.04593 (60 / 8 / 141) | 6389 / 0.05235 (42 / 6 / 161) | 6467 / 0.08099 (29 / 2 / 178) |
| all (n = 209) | 30 | `hurdle_count_28` | -85.88 / -0.007407 (135 / 15 / 59) | -528.8 / -0.004938 (113 / 12 / 84) | -450.7 / 0.009877 (80 / 5 / 124) |
| all (n = 209) | 30 | `dynamic_count` | -678.1 / 0.002469 (70 / 28 / 111) | -1121 / 0.007407 (70 / 15 / 124) | -1043 / 0.01975 (63 / 7 / 139) |
| dense (n = 100) | 7 | `chronos2_completed` | 10,966 / 0.3307 (18 / 0 / 82) | 9759 / 0.3878 (19 / 0 / 81) | 10,316 / 0.4005 (18 / 0 / 82) |
| dense (n = 100) | 7 | `timesfm3_completed` | 11,699 / 0.3095 (19 / 0 / 81) | 10,492 / 0.3656 (18 / 0 / 82) | 11,049 / 0.3862 (19 / 0 / 81) |
| dense (n = 100) | 7 | `timesfm2p5_completed` | 12,761 / 0.3333 (20 / 0 / 80) | 11,554 / 0.3402 (18 / 0 / 82) | 12,111 / 0.3984 (20 / 0 / 80) |
| dense (n = 100) | 7 | `chronos2_hurdle` | 10,648 / 0.3016 (17 / 0 / 83) | 9441 / 0.2884 (18 / 0 / 82) | 9998 / 0.3587 (19 / 0 / 81) |
| dense (n = 100) | 7 | `timesfm3_hurdle` | 11,329 / 0.3037 (21 / 0 / 79) | 10,122 / 0.3407 (20 / 0 / 80) | 10,679 / 0.3884 (21 / 0 / 79) |
| dense (n = 100) | 7 | `timesfm2p5_hurdle` | 12,231 / 0.2952 (22 / 0 / 78) | 11,024 / 0.2704 (21 / 0 / 79) | 11,581 / 0.372 (18 / 0 / 82) |
| dense (n = 100) | 7 | `hurdle_count_28` | 10.51 / -0.0254 (61 / 1 / 38) | -1196 / -0.03175 (61 / 0 / 39) | -639.3 / 0.01746 (48 / 0 / 52) |
| dense (n = 100) | 7 | `dynamic_count` | -2510 / 0.008466 (44 / 2 / 54) | -3717 / 0.01323 (47 / 1 / 52) | -3160 / 0.004233 (47 / 1 / 52) |
| dense (n = 100) | 30 | `chronos2_completed` | 13,725 / 0.5007 (8 / 0 / 92) | 12,799 / 0.4956 (10 / 0 / 90) | 12,962 / 0.5449 (7 / 0 / 93) |
| dense (n = 100) | 30 | `timesfm3_completed` | 14,284 / 0.4827 (8 / 0 / 92) | 13,358 / 0.5102 (10 / 0 / 90) | 13,521 / 0.6328 (4 / 0 / 96) |
| dense (n = 100) | 30 | `timesfm2p5_completed` | 14,509 / 0.5684 (12 / 0 / 88) | 13,584 / 0.5288 (12 / 0 / 88) | 13,747 / 0.6423 (6 / 0 / 94) |
| dense (n = 100) | 30 | `chronos2_hurdle` | 13,536 / 0.5254 (9 / 0 / 91) | 12,610 / 0.5037 (11 / 0 / 89) | 12,773 / 0.5695 (7 / 0 / 93) |
| dense (n = 100) | 30 | `timesfm3_hurdle` | 14,015 / 0.4919 (4 / 0 / 96) | 13,089 / 0.5325 (9 / 0 / 91) | 13,252 / 0.599 (4 / 0 / 96) |
| dense (n = 100) | 30 | `timesfm2p5_hurdle` | 14,279 / 0.5284 (5 / 0 / 95) | 13,353 / 0.5437 (8 / 0 / 92) | 13,516 / 0.6889 (7 / 0 / 93) |
| dense (n = 100) | 30 | `hurdle_count_28` | -179.3 / -0.01481 (60 / 0 / 40) | -1105 / -0.02963 (56 / 1 / 43) | -941.8 / 0.006173 (46 / 3 / 51) |
| dense (n = 100) | 30 | `dynamic_count` | -1417 / 0.01975 (41 / 2 / 57) | -2343 / 0.004938 (48 / 0 / 52) | -2180 / 0.006173 (49 / 0 / 51) |
| sparse (n = 100) | 7 | `chronos2_completed` | 0.2021 / -0.02804 (80 / 0 / 20) | 0.2296 / -0.0291 (77 / 0 / 23) | 0.2252 / -0.01852 (63 / 1 / 36) |
| sparse (n = 100) | 7 | `timesfm3_completed` | 0.2031 / -0.005291 (58 / 5 / 37) | 0.2306 / -0.00582 (61 / 2 / 37) | 0.2262 / 0.003175 (46 / 2 / 52) |
| sparse (n = 100) | 7 | `timesfm2p5_completed` | 0.2124 / -0.0291 (77 / 1 / 22) | 0.2399 / -0.02698 (74 / 0 / 26) | 0.2355 / -0.0164 (60 / 0 / 40) |
| sparse (n = 100) | 7 | `chronos2_hurdle` | 0.2574 / 0.003175 (40 / 1 / 59) | 0.2849 / 0.002646 (47 / 0 / 53) | 0.2805 / 0.02063 (31 / 1 / 68) |
| sparse (n = 100) | 7 | `timesfm3_hurdle` | 0.2343 / 0 (47 / 10 / 43) | 0.2618 / -0.0005291 (50 / 6 / 44) | 0.2574 / 0.01058 (38 / 1 / 61) |
| sparse (n = 100) | 7 | `timesfm2p5_hurdle` | 0.2253 / -0.0127 (62 / 5 / 33) | 0.2528 / -0.01164 (65 / 1 / 34) | 0.2484 / -0.001587 (52 / 1 / 47) |
| sparse (n = 100) | 7 | `hurdle_count_28` | -0.09091 / 0.002646 (41 / 5 / 54) | -0.06344 / 0 (49 / 2 / 49) | -0.06781 / 0.01852 (28 / 0 / 72) |
| sparse (n = 100) | 7 | `dynamic_count` | 0.05274 / -0.004233 (57 / 12 / 31) | 0.08021 / -0.005291 (55 / 3 / 42) | 0.07584 / 0.007937 (42 / 1 / 57) |
| sparse (n = 100) | 30 | `chronos2_completed` | 0.2625 / -0.00358 (62 / 0 / 38) | 0.2932 / -0.0003704 (50 / 0 / 50) | 0.2948 / 0.02222 (23 / 0 / 77) |
| sparse (n = 100) | 30 | `timesfm3_completed` | 0.2454 / 0.001235 (38 / 6 / 56) | 0.276 / 0.007407 (25 / 4 / 71) | 0.2777 / 0.0279 (14 / 2 / 84) |
| sparse (n = 100) | 30 | `timesfm2p5_completed` | 0.2554 / 0.0004938 (49 / 0 / 51) | 0.2861 / 0.003827 (41 / 0 / 59) | 0.2877 / 0.0221 (17 / 0 / 83) |
| sparse (n = 100) | 30 | `chronos2_hurdle` | 0.2771 / -0.001111 (53 / 3 / 44) | 0.3077 / 0.004938 (42 / 1 / 57) | 0.3094 / 0.02272 (18 / 0 / 82) |
| sparse (n = 100) | 30 | `timesfm3_hurdle` | 0.2458 / 0.001111 (43 / 5 / 52) | 0.2764 / 0.005926 (28 / 4 / 68) | 0.2781 / 0.02519 (16 / 1 / 83) |
| sparse (n = 100) | 30 | `timesfm2p5_hurdle` | 0.2364 / -0.001358 (54 / 2 / 44) | 0.2671 / 0.004321 (33 / 1 / 66) | 0.2688 / 0.02296 (18 / 0 / 82) |
| sparse (n = 100) | 30 | `hurdle_count_28` | -0.1063 / -0.007407 (72 / 9 / 19) | -0.07568 / -0.002469 (54 / 6 / 40) | -0.074 / 0.01605 (28 / 1 / 71) |
| sparse (n = 100) | 30 | `dynamic_count` | 0.06947 / 0 (28 / 23 / 49) | 0.1001 / 0.007407 (22 / 11 / 67) | 0.1018 / 0.02346 (14 / 1 / 85) |
| very_sparse (n = 9) † | 7 | `chronos2_completed` | 0.2093 / 0.007407 (3 / 1 / 5) | 0.3834 / 0.001058 (3 / 1 / 5) | 0.1453 / 0 (4 / 4 / 1) |
| very_sparse (n = 9) † | 7 | `timesfm3_completed` | 0.2335 / 0 (1 / 6 / 2) | 0.4076 / 0 (1 / 5 / 3) | 0.1695 / 0 (4 / 1 / 4) |
| very_sparse (n = 9) † | 7 | `timesfm2p5_completed` | 0.221 / 0.007407 (3 / 1 / 5) | 0.3952 / 0.001058 (3 / 1 / 5) | 0.1571 / 0 (4 / 4 / 1) |
| very_sparse (n = 9) † | 7 | `chronos2_hurdle` | 0.2268 / 0 (1 / 6 / 2) | 0.4009 / 0 (2 / 4 / 3) | 0.1628 / -0.003175 (5 / 1 / 3) |
| very_sparse (n = 9) † | 7 | `timesfm3_hurdle` | 0.2222 / 0 (1 / 6 / 2) | 0.3964 / 0 (2 / 4 / 3) | 0.1583 / -0.003175 (5 / 1 / 3) |
| very_sparse (n = 9) † | 7 | `timesfm2p5_hurdle` | 0.2247 / 0 (1 / 6 / 2) | 0.3988 / 0 (2 / 4 / 3) | 0.1607 / -0.003175 (5 / 1 / 3) |
| very_sparse (n = 9) † | 7 | `hurdle_count_28` | -1.085 / 0 (3 / 5 / 1) | -0.9111 / 0 (3 / 4 / 2) | -1.149 / -0.007407 (6 / 1 / 2) |
| very_sparse (n = 9) † | 7 | `dynamic_count` | 0.1514 / 0.003175 (2 / 2 / 5) | 0.3256 / 0.007407 (2 / 2 / 5) | 0.08748 / 0 (3 / 4 / 2) |
| very_sparse (n = 9) † | 30 | `chronos2_completed` | 0.3545 / 0.002469 (3 / 1 / 5) | 0.4848 / 0 (4 / 1 / 4) | 0.2107 / 0 (3 / 4 / 2) |
| very_sparse (n = 9) † | 30 | `timesfm3_completed` | 0.3628 / 0 (2 / 5 / 2) | 0.4931 / 0 (2 / 4 / 3) | 0.2191 / 0 (4 / 1 / 4) |
| very_sparse (n = 9) † | 30 | `timesfm2p5_completed` | 0.356 / 0.002469 (3 / 1 / 5) | 0.4863 / 0 (4 / 1 / 4) | 0.2122 / -5.551e-17 (5 / 3 / 1) |
| very_sparse (n = 9) † | 30 | `chronos2_hurdle` | 0.3655 / 0 (1 / 5 / 3) | 0.4959 / 0 (1 / 4 / 4) | 0.2218 / 0 (4 / 1 / 4) |
| very_sparse (n = 9) † | 30 | `timesfm3_hurdle` | 0.3413 / 0 (2 / 5 / 2) | 0.4717 / 0 (2 / 4 / 3) | 0.1976 / 0 (4 / 2 / 3) |
| very_sparse (n = 9) † | 30 | `timesfm2p5_hurdle` | 0.3598 / 0 (1 / 6 / 2) | 0.4901 / 0 (1 / 5 / 3) | 0.216 / 0 (4 / 2 / 3) |
| very_sparse (n = 9) † | 30 | `hurdle_count_28` | -1.049 / 0 (3 / 6 / 0) | -0.9188 / 0 (3 / 5 / 1) | -1.193 / -0.007407 (6 / 1 / 2) |
| very_sparse (n = 9) † | 30 | `dynamic_count` | 0.1524 / 0.002469 (1 / 3 / 5) | 0.2827 / 0.007407 (0 / 4 / 5) | 0.008642 / 0 (0 / 6 / 3) |

### npm: the fourth cell, four scores (full cells)

| Group | h | Variant | Reference | Source | QScore9 | Context-scaled QScore9 | Occurrence Brier | Discrete CRPS |
|---|---|---|---|---|---|---|---|---|
| all (n = 209) | 7 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | post hoc | 5241 [31.26, 15,635]; median 0.003175; 73 / 27 / 109; p 1.07e-07 | 0.1231 [0.07677, 0.1735]; median 0.003175; 73 / 27 / 109; p 2.38e-06 | 0 [0, 0]; median 0; 0 / 209 / 0; p 1 | n 208: 61.29 [25.66, 106.4]; median 0.009672; 75 / 0 / 133; p 8.48e-11 |
| all (n = 209) | 7 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -0.5861 [-3.497, 1.508]; median 0.02011; 74 / 3 / 132; p 0.00056 | 0.01401 [-0.000847, 0.02759]; median 0.006993; 71 / 3 / 135; p 1.07e-05 | 0.009771 [0.006173, 0.01339]; median 0.002759; 88 / 0 / 121; p 3.43e-06 | n 208: 2.781 [0.4222, 5.508]; median 0.01978; 70 / 0 / 138; p 8.43e-06 |
| all (n = 209) | 7 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | post hoc | 5591 [31.38, 16,681]; median 0.005291; 75 / 19 / 115; p 1.65e-07 | 0.1189 [0.07693, 0.167]; median 0.003175; 76 / 19 / 114; p 6.73e-06 | 0 [0, 0]; median 0; 0 / 209 / 0; p 1 | n 208: 62.14 [25.12, 109.1]; median 0.007134; 84 / 0 / 124; p 1.67e-08 |
| all (n = 209) | 7 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -1.068 [-2.648, 0.5198]; median -0.002116; 109 / 10 / 90; p 0.479 | -0.002148 [-0.0133, 0.009077]; median -0.001058; 107 / 10 / 92; p 0.35 | 0.001963 [-0.001005, 0.004976]; median 1.935e-05; 104 / 0 / 105; p 0.283 | n 208: 2.417 [0.1411, 5.242]; median 0.005934; 92 / 0 / 116; p 0.0658 |
| all (n = 209) | 7 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | post hoc | 6100 [31.04, 18,210]; median 0; 82 / 26 / 101; p 1.85e-05 | 0.1183 [0.0654, 0.1843]; median 0; 82 / 26 / 101; p 0.00196 | 0 [0, 0]; median 0; 0 / 209 / 0; p 1 | n 208: 61.39 [25.25, 106.7]; median 0.003648; 88 / 0 / 120; p 1.96e-05 |
| all (n = 209) | 7 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -1.01 [-2.498, 0.494]; median 0; 103 / 3 / 103; p 0.327 | 0.006311 [-0.01506, 0.03908]; median 1.852e-05; 102 / 2 / 105; p 0.591 | 0.004641 [0.00162, 0.007711]; median 0.002656; 89 / 0 / 120; p 0.00272 | n 208: 2.459 [0.0563, 5.387]; median 0.005733; 97 / 0 / 111; p 0.499 |
| all (n = 209) | 30 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | post hoc | 6652 [30.81, 19,863]; median 0.02815; 42 / 24 / 143; p 1.22e-20 | 0.136 [0.0967, 0.1795]; median 0.01432; 42 / 24 / 143; p 1.82e-20 | 0 [0, 0]; median 0; 0 / 209 / 0; p 1 | n 208: 63.53 [24.98, 114.1]; median 0.0338; 46 / 0 / 162; p 1.34e-22 |
| all (n = 209) | 30 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -0.4166 [-3.551, 2.176]; median 0.0007407; 99 / 4 / 106; p 0.429 | -0.007192 [-0.02252, 0.006814]; median 5.985e-05; 99 / 4 / 106; p 0.425 | 0.003203 [0.001416, 0.005092]; median 0.0008252; 81 / 0 / 128; p 0.000643 | n 208: 2.599 [0.005494, 5.521]; median 0.002145; 100 / 0 / 108; p 0.221 |
| all (n = 209) | 30 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | post hoc | 6919 [31.34, 20,659]; median 0.03136; 37 / 17 / 155; p 1.15e-23 | 0.1338 [0.09561, 0.1776]; median 0.02147; 37 / 17 / 155; p 1.13e-23 | 0 [0, 0]; median 0; 0 / 209 / 0; p 1 | n 208: 64.25 [25.02, 113.8]; median 0.03315; 38 / 0 / 170; p 1.07e-24 |
| all (n = 209) | 30 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -1.273 [-3.202, 0.8158]; median -0.001728; 109 / 12 / 88; p 0.0954 | -0.01411 [-0.02393, -0.005203]; median -0.001142; 109 / 12 / 88; p 0.00319 | 0.0005268 [-0.001055, 0.002147]; median 0.0002626; 99 / 0 / 110; p 0.839 | n 208: 1.932 [-0.1578, 4.548]; median -0.00125; 113 / 0 / 95; p 0.557 |
| all (n = 209) | 30 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | post hoc | 7026 [28.18, 20,986]; median 0.0521; 35 / 22 / 152; p 1.09e-22 | 0.14 [0.09223, 0.2008]; median 0.02274; 35 / 22 / 152; p 2.68e-22 | 0 [0, 0]; median 0; 0 / 209 / 0; p 1 | n 208: 59.63 [23.59, 104.5]; median 0.03381; 43 / 0 / 165; p 9.81e-22 |
| all (n = 209) | 30 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -2.436 [-5.241, 0.1454]; median -0.005432; 121 / 3 / 85; p 0.00156 | -0.00194 [-0.02081, 0.02605]; median -0.004444; 122 / 3 / 84; p 0.000285 | 0.0009753 [-0.0005885, 0.002558]; median 0.0007553; 95 / 0 / 114; p 0.321 | n 208: 0.8189 [-1.006, 3.054]; median -0.00348; 118 / 0 / 90; p 0.071 |
| dense (n = 100) | 7 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | post hoc | 10,954 [68.33, 32,665]; median 0.4365; 18 / 0 / 82; p 1.76e-12 | 0.2247 [0.141, 0.3147]; median 0.07848; 18 / 0 / 82; p 6.75e-12 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | n 99: 128.3 [54.91, 219.4]; median 0.414; 13 / 0 / 86; p 3.25e-14 |
| dense (n = 100) | 7 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -1.277 [-7.367, 3.13]; median 0.01164; 48 / 0 / 52; p 0.0492 | 0.01027 [-0.00646, 0.02924]; median 0.0001863; 47 / 0 / 53; p 0.826 | -0.002757 [-0.00677, 0.001152]; median -0.001891; 68 / 0 / 32; p 0.00627 | n 99: 5.772 [0.741, 11.53]; median 0.0197; 43 / 0 / 56; p 0.00146 |
| dense (n = 100) | 7 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | post hoc | 11,686 [65.57, 34,859]; median 0.4265; 18 / 0 / 82; p 1.13e-12 | 0.2105 [0.1452, 0.2849]; median 0.07947; 19 / 0 / 81; p 9e-12 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | n 99: 130.2 [53.57, 225.1]; median 0.3848; 14 / 0 / 85; p 3.92e-14 |
| dense (n = 100) | 7 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -2.251 [-5.55, 1.134]; median -0.02222; 58 / 1 / 41; p 0.333 | -0.01506 [-0.03322, 0.001859]; median -0.006615; 58 / 1 / 41; p 0.0105 | -0.003357 [-0.006854, -5.371e-05]; median -0.001576; 62 / 0 / 38; p 0.0372 | n 99: 5.018 [0.1574, 10.99]; median 0.003364; 48 / 0 / 51; p 0.161 |
| dense (n = 100) | 7 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | post hoc | 12,748 [66.03, 38,042]; median 0.3878; 21 / 0 / 79; p 1.13e-11 | 0.1973 [0.1298, 0.2768]; median 0.0738; 21 / 0 / 79; p 2.56e-10 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | n 99: 128.4 [53.29, 220.9]; median 0.3156; 17 / 0 / 82; p 2.24e-12 |
| dense (n = 100) | 7 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -2.337 [-5.402, 0.9528]; median -0.05132; 62 / 1 / 37; p 0.0227 | -0.02353 [-0.04282, -0.003293]; median -0.01072; 62 / 0 / 38; p 0.000139 | -0.0002061 [-0.003999, 0.003701]; median -0.0003181; 54 / 0 / 46; p 0.608 | n 99: 4.894 [-0.1191, 11.12]; median -0.02323; 57 / 0 / 42; p 0.598 |
| dense (n = 100) | 30 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | post hoc | 13,903 [65.18, 41,504]; median 0.5579; 8 / 0 / 92; p 7.04e-16 | 0.242 [0.1726, 0.3169]; median 0.12; 8 / 0 / 92; p 3e-15 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | n 99: 133 [53.14, 235.2]; median 0.5483; 8 / 0 / 91; p 8.14e-16 |
| dense (n = 100) | 30 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -0.8441 [-7.386, 4.57]; median 0.03667; 43 / 1 / 56; p 0.00501 | 0.01076 [-0.00702, 0.03091]; median 0.0003671; 43 / 1 / 56; p 0.459 | 0.001552 [-0.001083, 0.004476]; median 0.0004832; 42 / 0 / 58; p 0.545 | n 99: 5.456 [0.04743, 11.42]; median 0.04899; 40 / 0 / 59; p 9.96e-05 |
| dense (n = 100) | 30 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | post hoc | 14,460 [64.02, 43,174]; median 0.564; 6 / 0 / 94; p 7.56e-17 | 0.2232 [0.1675, 0.2868]; median 0.1215; 6 / 0 / 94; p 1.85e-16 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | n 99: 134.5 [53.21, 236.4]; median 0.6048; 6 / 0 / 93; p 6.7e-17 |
| dense (n = 100) | 30 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -2.668 [-6.672, 1.707]; median 0.00284; 48 / 0 / 52; p 0.812 | -0.01546 [-0.03253, -0.001025]; median 8.302e-05; 48 / 0 / 52; p 0.268 | 0.001131 [-0.001488, 0.00389]; median 0.0004851; 43 / 0 / 57; p 0.481 | n 99: 4.012 [-0.3707, 9.42]; median 0.01568; 46 / 0 / 53; p 0.0659 |
| dense (n = 100) | 30 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | post hoc | 14,683 [61.86, 43,870]; median 0.4772; 6 / 0 / 94; p 1.91e-16 | 0.2076 [0.1493, 0.275]; median 0.1052; 6 / 0 / 94; p 5.46e-16 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | n 99: 124.6 [50.08, 216.8]; median 0.4435; 5 / 0 / 94; p 1.52e-16 |
| dense (n = 100) | 30 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -5.315 [-11.04, 0.1558]; median -0.03642; 60 / 0 / 40; p 0.0057 | -0.02013 [-0.03649, -0.003721]; median -0.007113; 61 / 0 / 39; p 0.00119 | 0.002853 [0.0002331, 0.005559]; median 0.0008149; 38 / 0 / 62; p 0.036 | n 99: 1.458 [-2.355, 6.202]; median -0.01067; 54 / 0 / 45; p 0.764 |
| sparse (n = 100) | 7 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | post hoc | 0.4023 [-0.01314, 1.183]; median -0.004233; 55 / 19 / 26; p 0.00151 | 0.02238 [-0.01119, 0.06771]; median -0.004233; 55 / 19 / 26; p 0.000998 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.3741 [-0.002865, 1.081]; median -0.0009417; 58 / 0 / 42; p 0.177 |
| sparse (n = 100) | 7 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | post hoc | 0.1093 [-0.00254, 0.3144]; median 0.02751; 21 / 2 / 77; p 7.08e-07 | 0.02845 [0.01598, 0.04146]; median 0.02857; 19 / 2 / 79; p 9.33e-09 | 0.02323 [0.01814, 0.02828]; median 0.02443; 15 / 0 / 85; p 4.12e-13 | 0.1123 [0.0009394, 0.3186]; median 0.0249; 22 / 0 / 78; p 2.08e-07 |
| sparse (n = 100) | 7 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | post hoc | 0.2821 [-0.01578, 0.8367]; median -0.003175; 56 / 12 / 32; p 0.00264 | 0.01283 [-0.01454, 0.04989]; median -0.003175; 56 / 12 / 32; p 0.00135 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.277 [-0.01139, 0.8139]; median -0.004224; 67 / 0 / 33; p 0.00152 |
| sparse (n = 100) | 7 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -0.01195 [-0.03869, 0.00928]; median 0; 49 / 4 / 47; p 0.545 | 0.005968 [-0.005082, 0.01762]; median 0; 47 / 4 / 49; p 0.164 | 0.00862 [0.00423, 0.01325]; median 0.005174; 36 / 0 / 64; p 0.000268 | 0.02184 [-0.02024, 0.08691]; median 0.006093; 39 / 0 / 61; p 0.0218 |
| sparse (n = 100) | 7 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | post hoc | 0.3687 [-0.02527, 1.105]; median -0.01376; 61 / 18 / 21; p 3.44e-05 | 0.002638 [-0.03083, 0.04953]; median -0.01376; 61 / 18 / 21; p 2.02e-05 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.3465 [-0.03146, 1.057]; median -0.01021; 67 / 0 / 33; p 4.41e-05 |
| sparse (n = 100) | 7 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | post hoc | 0.0653 [-0.02586, 0.2205]; median 0.006349; 37 / 1 / 62; p 0.0122 | 0.009082 [-0.001967, 0.01873]; median 0.006349; 36 / 1 / 63; p 0.0014 | 0.01073 [0.006614, 0.01502]; median 0.008108; 30 / 0 / 70; p 2.6e-06 | 0.1012 [-0.01793, 0.3155]; median 0.01025; 36 / 0 / 64; p 0.00112 |
| sparse (n = 100) | 30 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | post hoc | 0.402 [0.01384, 1.15]; median 0.0001235; 34 / 16 / 50; p 0.000759 | 0.03103 [0.006289, 0.06781]; median 0.0001235; 34 / 16 / 50; p 0.000878 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.3803 [0.01713, 1.082]; median 0.002175; 36 / 0 / 64; p 9.79e-06 |
| sparse (n = 100) | 30 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | post hoc | 0.03312 [-0.06572, 0.205]; median -0.0004938; 51 / 2 / 47; p 0.075 | -0.01567 [-0.02833, -0.003189]; median -0.0004938; 51 / 2 / 47; p 0.106 | 0.00515 [0.002736, 0.007777]; median 0.004022; 35 / 0 / 65; p 3.69e-05 | 0.04524 [-0.05736, 0.226]; median -0.002492; 55 / 0 / 45; p 0.0256 |
| sparse (n = 100) | 30 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | post hoc | 0.3416 [0.01771, 0.9585]; median 0.002469; 30 / 11 / 59; p 7.53e-06 | 0.03176 [0.008253, 0.06567]; median 0.002469; 30 / 11 / 59; p 1.02e-05 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.3374 [0.01736, 0.9563]; median 0.002881; 30 / 0 / 70; p 1.16e-06 |
| sparse (n = 100) | 30 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -0.01008 [-0.06514, 0.07307]; median -0.004198; 59 / 6 / 35; p 0.00173 | -0.01698 [-0.02704, -0.007429]; median -0.004198; 59 / 6 / 35; p 0.00166 | 0.0003306 [-0.001589, 0.002381]; median -0.000141; 51 / 0 / 49; p 0.509 | 0.01904 [-0.0561, 0.1488]; median -0.00281; 63 / 0 / 37; p 0.000247 |
| sparse (n = 100) | 30 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | post hoc | 0.4459 [0.03264, 1.242]; median 0.002099; 29 / 14 / 57; p 5.32e-05 | 0.03988 [0.01331, 0.07915]; median 0.002099; 29 / 14 / 57; p 5.83e-05 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.4246 [0.02495, 1.196]; median 0.001456; 37 / 0 / 63; p 0.00156 |
| sparse (n = 100) | 30 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | post hoc | 0.08417 [-0.04146, 0.3156]; median -0.002346; 57 / 2 / 41; p 0.0382 | -0.007577 [-0.01943, 0.007276]; median -0.002346; 57 / 2 / 41; p 0.048 | -0.0004224 [-0.002006, 0.001161]; median -0.0006278; 52 / 0 / 48; p 0.675 | 0.1206 [-0.03475, 0.4151]; median -0.003039; 60 / 0 / 40; p 0.00811 |
| very_sparse (n = 9) † | 7 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | post hoc | 0.6622 [0, 1.987]; median 0; 0 / 8 / 1; p 0.317 | 0.1125 [0, 0.3375]; median 0; 0 / 8 / 1; p 0.317 | 0 [0, 0]; median 0; 0 / 9 / 0; p 1 | 0.5798 [-0.0001077, 1.738]; median 0.001751; 4 / 0 / 5; p 0.139 |
| very_sparse (n = 9) † | 7 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -0.6323 [-1.907, 0.01305]; median -0.007407; 5 / 1 / 3; p 0.779 | -0.105 [-0.325, 0.01305]; median -0.007407; 5 / 1 / 3; p 0.779 | -0.0005849 [-0.01219, 0.0121]; median -0.01003; 5 / 0 / 4; p 0.767 | -0.4607 [-1.388, 0.01069]; median -0.01139; 5 / 0 / 4; p 0.594 |
| very_sparse (n = 9) † | 7 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | post hoc | 1.646 [-0.001058, 4.938]; median 0; 1 / 7 / 1; p 0.655 | 0.2792 [-0.001058, 0.8388]; median 0; 1 / 7 / 1; p 0.655 | 0 [0, 0]; median 0; 0 / 9 / 0; p 1 | 1.457 [0.0001668, 4.37]; median 0.002174; 3 / 0 / 6; p 0.0858 |
| very_sparse (n = 9) † | 7 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | post hoc | 0.327 [-0.01693, 0.9979]; median 0; 2 / 5 / 2; p 0.715 | 0.05109 [-0.01634, 0.1702]; median 0; 2 / 5 / 2; p 0.715 | -0.01289 [-0.03488, 0.002686]; median -0.005426; 6 / 0 / 3; p 0.26 | 0.4149 [-0.01047, 1.256]; median -0.001142; 5 / 0 / 4; p 0.953 |
| very_sparse (n = 9) † | 7 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | post hoc | 3.099 [0, 9.297]; median 0; 0 / 8 / 1; p 0.317 | 0.5263 [0, 1.579]; median 0; 0 / 8 / 1; p 0.317 | 0 [0, 0]; median 0; 0 / 9 / 0; p 1 | 2.9 [-0.0001093, 8.699]; median 0.00175; 4 / 0 / 5; p 0.139 |
| very_sparse (n = 9) † | 7 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | post hoc | 1.793 [-0.005761, 5.375]; median 0; 4 / 1 / 4; p 0.4 | 0.3071 [-0.005996, 0.9182]; median 0; 4 / 1 / 4; p 0.4 | -0.009126 [-0.03638, 0.01183]; median -0.01002; 5 / 0 / 4; p 0.594 | 1.87 [-0.008104, 5.612]; median 0.003382; 4 / 0 / 5; p 0.594 |
| very_sparse (n = 9) † | 30 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | post hoc | 0.7384 [0, 2.215]; median 0; 0 / 8 / 1; p 0.317 | 0.1254 [0, 0.3761]; median 0; 0 / 8 / 1; p 0.317 | 0 [0, 0]; median 0; 0 / 9 / 0; p 1 | 0.6733 [0.0002002, 2.019]; median 0.000745; 2 / 0 / 7; p 0.0382 |
| very_sparse (n = 9) † | 30 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -0.6652 [-1.998, 0.00524]; median -0.007407; 5 / 1 / 3; p 0.779 | -0.1124 [-0.3399, 0.005377]; median -0.007407; 5 / 1 / 3; p 0.779 | -8.188e-05 [-0.007496, 0.007036]; median 0.003382; 4 / 0 / 5; p 0.859 | -0.4653 [-1.395, 0.004228]; median -0.007535; 5 / 0 / 4; p 0.441 |
| very_sparse (n = 9) † | 30 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | post hoc | 1.611 [-0.0002195, 4.834]; median 0; 1 / 6 / 2; p 0.285 | 0.2737 [-0.0002195, 0.8211]; median 0; 1 / 6 / 2; p 0.285 | 0 [0, 0]; median 0; 0 / 9 / 0; p 1 | 1.444 [0.0001371, 4.331]; median 0.0006139; 2 / 0 / 7; p 0.0663 |
| very_sparse (n = 9) † | 30 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | post hoc | 0.1993 [-0.004198, 0.6028]; median 0; 2 / 6 / 1; p 1 | 0.03284 [-0.004198, 0.1033]; median 0; 2 / 6 / 1; p 1 | -0.004004 [-0.009907, 0.0008749]; median -0.003982; 5 / 0 / 4; p 0.214 | 0.3101 [-0.004122, 0.9346]; median 0.0006446; 4 / 0 / 5; p 0.953 |
| very_sparse (n = 9) † | 30 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | post hoc | 2.947 [0, 8.84]; median 0; 0 / 8 / 1; p 0.317 | 0.5003 [0, 1.501]; median 0; 0 / 8 / 1; p 0.317 | 0 [0, 0]; median 0; 0 / 9 / 0; p 1 | 2.675 [0.0002284, 8.023]; median 0.0006045; 1 / 0 / 8; p 0.0284 |
| very_sparse (n = 9) † | 30 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | post hoc | 1.542 [-0.003896, 4.625]; median 0; 4 / 1 / 4; p 0.401 | 0.2628 [-0.004115, 0.789]; median 0; 4 / 1 / 4; p 0.401 | -0.004358 [-0.01378, 0.004468]; median -0.007183; 5 / 0 / 4; p 0.515 | 1.55 [-0.007393, 4.655]; median 0.003382; 4 / 0 / 5; p 0.953 |

### npm: the point methods, QScore9 (compact cells)

A point mass is a poor probabilistic forecast by construction. Under it QScore9 is the absolute error of the rounded point, so these rows say how the field's point methods fare under this score, not how good they are as point forecasts.

| Group | h | Reference | `croston_classic` | `croston_sba` | `adida` |
|---|---|---|---|---|---|
| all (n = 209) | 7 | `chronos2_completed` | 4875 / 0.4571 (2 / 6 / 201) | 5439 / 0.4339 (2 / 6 / 201) | 4890 / 0.4571 (1 / 6 / 202) |
| all (n = 209) | 7 | `timesfm3_completed` | 5226 / 0.4466 (4 / 1 / 204) | 5789 / 0.4275 (4 / 1 / 204) | 5241 / 0.436 (5 / 1 / 203) |
| all (n = 209) | 7 | `timesfm2p5_completed` | 5734 / 0.4349 (1 / 7 / 201) | 6298 / 0.4275 (1 / 7 / 201) | 5749 / 0.437 (1 / 7 / 201) |
| all (n = 209) | 7 | `hurdle_count_28` | -366.7 / 0.3735 (21 / 1 / 187) | 196.7 / 0.3735 (20 / 1 / 188) | -352 / 0.3831 (22 / 1 / 186) |
| all (n = 209) | 7 | `dynamic_count` | -1573 / 0.3778 (17 / 4 / 188) | -1009 / 0.381 (14 / 4 / 191) | -1558 / 0.3619 (18 / 4 / 187) |
| all (n = 209) | 7 | `tsb_hurdle` | 205.8 / 0.4349 (11 / 1 / 197) | 769.2 / 0.3979 (14 / 1 / 194) | 220.5 / 0.4328 (11 / 1 / 197) |
| all (n = 209) | 30 | `chronos2_completed` | 6065 / 0.4988 (2 / 6 / 201) | 6461 / 0.4985 (2 / 6 / 201) | 6067 / 0.5281 (1 / 6 / 202) |
| all (n = 209) | 30 | `timesfm3_completed` | 6332 / 0.4933 (3 / 1 / 205) | 6728 / 0.4881 (3 / 1 / 205) | 6334 / 0.516 (3 / 1 / 205) |
| all (n = 209) | 30 | `timesfm2p5_completed` | 6440 / 0.4886 (2 / 5 / 202) | 6836 / 0.481 (2 / 5 / 202) | 6442 / 0.516 (1 / 5 / 203) |
| all (n = 209) | 30 | `hurdle_count_28` | -587.8 / 0.3975 (21 / 1 / 187) | -192 / 0.3975 (20 / 1 / 188) | -585.9 / 0.3975 (21 / 1 / 187) |
| all (n = 209) | 30 | `dynamic_count` | -1180 / 0.3951 (18 / 4 / 187) | -784.3 / 0.3802 (18 / 4 / 187) | -1178 / 0.4025 (17 / 4 / 188) |
| all (n = 209) | 30 | `tsb_hurdle` | -59.04 / 0.4469 (11 / 1 / 197) | 336.7 / 0.4148 (12 / 1 / 196) | -57.14 / 0.4444 (9 / 1 / 199) |
| dense (n = 100) | 7 | `chronos2_completed` | 10,189 / 1.32 (1 / 0 / 99) | 11,366 / 1.247 (1 / 0 / 99) | 10,219 / 1.261 (0 / 0 / 100) |
| dense (n = 100) | 7 | `timesfm3_completed` | 10,921 / 1.285 (0 / 0 / 100) | 12,099 / 1.239 (0 / 0 / 100) | 10,952 / 1.193 (1 / 0 / 99) |
| dense (n = 100) | 7 | `timesfm2p5_completed` | 11,984 / 1.319 (0 / 0 / 100) | 13,161 / 1.269 (0 / 0 / 100) | 12,015 / 1.239 (0 / 0 / 100) |
| dense (n = 100) | 7 | `hurdle_count_28` | -766.8 / 0.6487 (15 / 0 / 85) | 410.7 / 0.628 (14 / 0 / 86) | -736.2 / 0.6206 (16 / 0 / 84) |
| dense (n = 100) | 7 | `dynamic_count` | -3287 / 0.6566 (16 / 0 / 84) | -2110 / 0.5614 (13 / 0 / 87) | -3257 / 0.5587 (17 / 0 / 83) |
| dense (n = 100) | 7 | `tsb_hurdle` | 429.6 / 0.8185 (5 / 0 / 95) | 1607 / 0.6788 (8 / 0 / 92) | 460.2 / 0.7862 (5 / 0 / 95) |
| dense (n = 100) | 30 | `chronos2_completed` | 12,675 / 1.623 (2 / 0 / 98) | 13,502 / 1.442 (2 / 0 / 98) | 12,679 / 1.511 (1 / 0 / 99) |
| dense (n = 100) | 30 | `timesfm3_completed` | 13,234 / 1.632 (0 / 0 / 100) | 14,061 / 1.421 (0 / 0 / 100) | 13,238 / 1.598 (0 / 0 / 100) |
| dense (n = 100) | 30 | `timesfm2p5_completed` | 13,460 / 1.604 (1 / 0 / 99) | 14,287 / 1.426 (1 / 0 / 99) | 13,464 / 1.534 (0 / 0 / 100) |
| dense (n = 100) | 30 | `hurdle_count_28` | -1229 / 0.6481 (15 / 0 / 85) | -401.7 / 0.6222 (14 / 0 / 86) | -1225 / 0.6049 (15 / 0 / 85) |
| dense (n = 100) | 30 | `dynamic_count` | -2467 / 0.6383 (17 / 0 / 83) | -1640 / 0.5642 (17 / 0 / 83) | -2463 / 0.7346 (17 / 0 / 83) |
| dense (n = 100) | 30 | `tsb_hurdle` | -124 / 0.8889 (7 / 0 / 93) | 703.3 / 0.7284 (8 / 0 / 92) | -120 / 0.8185 (6 / 0 / 94) |
| sparse (n = 100) | 7 | `chronos2_completed` | 0.8121 / 0.2302 (1 / 0 / 99) | 0.7592 / 0.2127 (1 / 0 / 99) | 0.8107 / 0.2317 (1 / 0 / 99) |
| sparse (n = 100) | 7 | `timesfm3_completed` | 0.8131 / 0.2481 (1 / 0 / 99) | 0.7602 / 0.2228 (1 / 0 / 99) | 0.8117 / 0.2503 (1 / 0 / 99) |
| sparse (n = 100) | 7 | `timesfm2p5_completed` | 0.8224 / 0.2159 (1 / 1 / 98) | 0.7696 / 0.2011 (1 / 1 / 98) | 0.821 / 0.2159 (1 / 1 / 98) |
| sparse (n = 100) | 7 | `hurdle_count_28` | 0.5191 / 0.2344 (1 / 0 / 99) | 0.4662 / 0.2132 (1 / 0 / 99) | 0.5177 / 0.2503 (1 / 0 / 99) |
| sparse (n = 100) | 7 | `dynamic_count` | 0.6627 / 0.2667 (0 / 0 / 100) | 0.6099 / 0.2323 (0 / 0 / 100) | 0.6613 / 0.2571 (0 / 0 / 100) |
| sparse (n = 100) | 7 | `tsb_hurdle` | 0.5825 / 0.2778 (1 / 0 / 99) | 0.5297 / 0.2323 (1 / 0 / 99) | 0.5811 / 0.2878 (1 / 0 / 99) |
| sparse (n = 100) | 30 | `chronos2_completed` | 0.8981 / 0.3319 (0 / 0 / 100) | 0.8428 / 0.3235 (0 / 0 / 100) | 0.8979 / 0.3486 (0 / 0 / 100) |
| sparse (n = 100) | 30 | `timesfm3_completed` | 0.881 / 0.337 (0 / 0 / 100) | 0.8257 / 0.3269 (0 / 0 / 100) | 0.8808 / 0.3559 (0 / 0 / 100) |
| sparse (n = 100) | 30 | `timesfm2p5_completed` | 0.891 / 0.332 (0 / 0 / 100) | 0.8357 / 0.3202 (0 / 0 / 100) | 0.8908 / 0.3633 (0 / 0 / 100) |
| sparse (n = 100) | 30 | `hurdle_count_28` | 0.5293 / 0.321 (1 / 0 / 99) | 0.474 / 0.3123 (1 / 0 / 99) | 0.5291 / 0.3333 (1 / 0 / 99) |
| sparse (n = 100) | 30 | `dynamic_count` | 0.7051 / 0.3543 (0 / 0 / 100) | 0.6498 / 0.3346 (0 / 0 / 100) | 0.7049 / 0.3642 (0 / 0 / 100) |
| sparse (n = 100) | 30 | `tsb_hurdle` | 0.605 / 0.3259 (0 / 0 / 100) | 0.5497 / 0.316 (0 / 0 / 100) | 0.6048 / 0.3444 (0 / 0 / 100) |
| very_sparse (n = 9) † | 7 | `chronos2_completed` | 0.1061 / 0 (0 / 6 / 3) | 0.09018 / 0 (0 / 6 / 3) | 0.3812 / 0 (0 / 6 / 3) |
| very_sparse (n = 9) † | 7 | `timesfm3_completed` | 0.1303 / 0.02011 (3 / 1 / 5) | 0.1144 / 0.02011 (3 / 1 / 5) | 0.4054 / 0.02011 (3 / 1 / 5) |
| very_sparse (n = 9) † | 7 | `timesfm2p5_completed` | 0.1178 / 0 (0 / 6 / 3) | 0.1019 / 0 (0 / 6 / 3) | 0.3929 / 0 (0 / 6 / 3) |
| very_sparse (n = 9) † | 7 | `hurdle_count_28` | -1.188 / -0.007407 (5 / 1 / 3) | -1.204 / -0.007407 (5 / 1 / 3) | -0.9133 / -0.007407 (5 / 1 / 3) |
| very_sparse (n = 9) † | 7 | `dynamic_count` | 0.04821 / 0 (1 / 4 / 4) | 0.03233 / 0 (1 / 4 / 4) | 0.3233 / 0 (1 / 4 / 4) |
| very_sparse (n = 9) † | 7 | `tsb_hurdle` | -0.2774 / -0.001058 (5 / 1 / 3) | -0.2932 / -0.001058 (5 / 1 / 3) | -0.002234 / -0.001058 (5 / 1 / 3) |
| very_sparse (n = 9) † | 30 | `chronos2_completed` | 0.1706 / 0 (0 / 6 / 3) | 0.146 / 0 (0 / 6 / 3) | 0.5385 / 0 (0 / 6 / 3) |
| very_sparse (n = 9) † | 30 | `timesfm3_completed` | 0.179 / 0.001975 (3 / 1 / 5) | 0.1543 / 0.001975 (3 / 1 / 5) | 0.5469 / 0.001975 (3 / 1 / 5) |
| very_sparse (n = 9) † | 30 | `timesfm2p5_completed` | 0.1722 / 0 (1 / 5 / 3) | 0.1475 / 0 (1 / 5 / 3) | 0.5401 / 0 (1 / 5 / 3) |
| very_sparse (n = 9) † | 30 | `hurdle_count_28` | -1.233 / -0.007407 (5 / 1 / 3) | -1.258 / -0.007407 (5 / 1 / 3) | -0.865 / -0.007407 (5 / 1 / 3) |
| very_sparse (n = 9) † | 30 | `dynamic_count` | -0.03141 / 0 (1 / 4 / 4) | -0.0561 / 0 (1 / 4 / 4) | 0.3365 / 5.551e-17 (0 / 4 / 5) |
| very_sparse (n = 9) † | 30 | `tsb_hurdle` | -0.3141 / 0 (4 / 1 / 4) | -0.3388 / 0 (4 / 1 / 4) | 0.05377 / 5.551e-17 (3 / 1 / 5) |

### npm: occurrence descriptors

| Group | h | Windows | All-zero contexts | Positive target days | TSB p (0.05 / 0.1 / 0.2) | Jeffreys p | `dynamic_count` p | Completed 1 − F(0) (chronos2 / timesfm3 / timesfm2p5) | Days with every decile at zero (chronos2 / timesfm3 / timesfm2p5) |
|---|---|---|---|---|---|---|---|---|---|
| all (n = 209) | 7 | 627 | 3 | 0.600 | 0.549 / 0.550 / 0.554 | 0.553 | 0.534 | 0.516 / 0.543 / 0.530 | 0.050 / 0.018 / 0.067 |
| all (n = 209) | 30 | 627 | 3 | 0.548 | 0.549 / 0.550 / 0.554 | 0.553 | 0.534 | 0.514 / 0.544 / 0.535 | 0.051 / 0.018 / 0.044 |
| dense (n = 100) | 7 | 300 | 0 | 0.812 | 0.809 / 0.809 / 0.813 | 0.795 | 0.805 | 0.816 / 0.816 / 0.800 | 0.000 / 0.000 / 0.000 |
| dense (n = 100) | 30 | 300 | 0 | 0.791 | 0.809 / 0.809 / 0.813 | 0.795 | 0.805 | 0.812 / 0.814 / 0.804 | 0.000 / 0.000 / 0.000 |
| sparse (n = 100) | 7 | 300 | 0 | 0.425 | 0.327 / 0.329 / 0.333 | 0.347 | 0.301 | 0.255 / 0.306 / 0.297 | 0.028 / 0.000 / 0.060 |
| sparse (n = 100) | 30 | 300 | 0 | 0.338 | 0.327 / 0.329 / 0.333 | 0.347 | 0.301 | 0.252 / 0.310 / 0.304 | 0.033 / 0.000 / 0.019 |
| very_sparse (n = 9) | 7 | 27 | 3 | 0.201 | 0.129 / 0.133 / 0.126 | 0.162 | 0.106 | 0.099 / 0.139 / 0.121 | 0.852 / 0.413 / 0.889 |
| very_sparse (n = 9) | 30 | 27 | 3 | 0.185 | 0.129 / 0.133 / 0.126 | 0.162 | 0.106 | 0.100 / 0.141 / 0.124 | 0.807 / 0.409 / 0.812 |

## The grid

540 series: 18 cells of 30 replicates. `all` has the 30 replicate blocks as entities; each cell has its 30 series.

### The grid: `tsb_hurdle` against every reference, four scores (full cells)

| Group | h | Reference | QScore9 | Context-scaled QScore9 | Occurrence Brier | Discrete CRPS |
|---|---|---|---|---|---|---|
| all (n = 30) | 7 | `chronos2_completed` | 0.112 [0.04176, 0.1851]; median 0.09471; 7 / 0 / 23; p 0.00499 | 0.02576 [0.007514, 0.04422]; median 0.02142; 9 / 0 / 21; p 0.0243 | 0.008051 [0.0002963, 0.01595]; median 0.007121; 11 / 0 / 19; p 0.0719 | 0.08439 [0.01795, 0.1528]; median 0.08138; 8 / 0 / 22; p 0.0207 |
| all (n = 30) | 7 | `timesfm3_completed` | 0.1297 [0.06321, 0.2005]; median 0.1418; 7 / 0 / 23; p 0.00159 | 0.03038 [0.01323, 0.04798]; median 0.03014; 6 / 0 / 24; p 0.00171 | 0.008927 [0.002025, 0.01597]; median 0.01089; 9 / 0 / 21; p 0.023 | 0.1038 [0.04042, 0.1686]; median 0.1212; 8 / 0 / 22; p 0.00468 |
| all (n = 30) | 7 | `timesfm2p5_completed` | 0.08904 [0.0252, 0.157]; median 0.06711; 9 / 0 / 21; p 0.0117 | 0.02303 [0.007331, 0.0387]; median 0.01645; 8 / 0 / 22; p 0.00927 | 0.002584 [-0.005052, 0.01036]; median 0.0007903; 15 / 0 / 15; p 0.544 | 0.06222 [0.003529, 0.124]; median 0.03819; 9 / 0 / 21; p 0.0545 |
| all (n = 30) | 7 | `chronos2_hurdle` | -0.08549 [-0.148, -0.02762]; median -0.04979; 18 / 0 / 12; p 0.0256 | -0.01176 [-0.02923, 0.004081]; median -0.005344; 16 / 0 / 14; p 0.441 | -0.003018 [-0.00731, 0.0009494]; median -0.002445; 19 / 0 / 11; p 0.221 | -0.09079 [-0.1517, -0.03547]; median -0.05072; 21 / 0 / 9; p 0.0125 |
| all (n = 30) | 7 | `timesfm3_hurdle` | -0.06399 [-0.1244, -0.009122]; median -0.03457; 17 / 0 / 13; p 0.0937 | -0.009324 [-0.0266, 0.006085]; median 0.002774; 13 / 0 / 17; p 0.845 | -0.003018 [-0.007294, 0.0009651]; median -0.002445; 19 / 0 / 11; p 0.221 | -0.06776 [-0.1273, -0.01333]; median -0.02968; 18 / 0 / 12; p 0.0545 |
| all (n = 30) | 7 | `timesfm2p5_hurdle` | -0.09923 [-0.1615, -0.03995]; median -0.06646; 21 / 0 / 9; p 0.00927 | -0.01351 [-0.03163, 0.002961]; median -0.004921; 16 / 0 / 14; p 0.441 | -0.003018 [-0.007337, 0.0009361]; median -0.002445; 19 / 0 / 11; p 0.221 | -0.1105 [-0.1723, -0.05099]; median -0.07889; 21 / 0 / 9; p 0.00316 |
| all (n = 30) | 7 | `hurdle_count_28` | -0.02001 [-0.06424, 0.01994]; median 0.0006173; 15 / 0 / 15; p 0.544 | -0.01051 [-0.02447, 0.002115]; median -0.003929; 17 / 0 / 13; p 0.262 | -0.003018 [-0.007343, 0.0009153]; median -0.002445; 19 / 0 / 11; p 0.221 | -0.02878 [-0.07071, 0.01008]; median -0.02714; 18 / 0 / 12; p 0.245 |
| all (n = 30) | 7 | `dynamic_count` | 0.08696 [0.03186, 0.1405]; median 0.09588; 7 / 0 / 23; p 0.00773 | 0.007509 [-0.008436, 0.02275]; median 0.01217; 9 / 0 / 21; p 0.102 | 0.006066 [0.0004357, 0.01157]; median 0.008171; 7 / 0 / 23; p 0.0285 | 0.0677 [0.01776, 0.1164]; median 0.08816; 7 / 0 / 23; p 0.0157 |
| all (n = 30) | 30 | `chronos2_completed` | 0.08545 [0.02494, 0.1469]; median 0.0835; 7 / 0 / 23; p 0.00642 | 0.01288 [-0.001445, 0.02648]; median 0.00993; 10 / 0 / 20; p 0.0719 | 0.004481 [-0.001517, 0.01058]; median 0.003103; 10 / 0 / 20; p 0.199 | 0.06433 [0.00927, 0.1184]; median 0.0707; 7 / 0 / 23; p 0.0166 |
| all (n = 30) | 30 | `timesfm3_completed` | 0.1167 [0.0644, 0.1727]; median 0.09576; 6 / 0 / 24; p 0.000332 | 0.02218 [0.01127, 0.03386]; median 0.0164; 9 / 0 / 21; p 0.00138 | 0.007491 [0.002261, 0.01293]; median 0.005231; 8 / 0 / 22; p 0.0148 | 0.09761 [0.05178, 0.1483]; median 0.08744; 7 / 0 / 23; p 0.000453 |
| all (n = 30) | 30 | `timesfm2p5_completed` | 0.07817 [0.03009, 0.1296]; median 0.05822; 8 / 0 / 22; p 0.00499 | 0.01721 [0.006495, 0.02894]; median 0.01154; 9 / 0 / 21; p 0.00984 | 0.0008034 [-0.004956, 0.0068]; median -0.001112; 17 / 0 / 13; p 0.926 | 0.06055 [0.01805, 0.1063]; median 0.05089; 9 / 0 / 21; p 0.00984 |
| all (n = 30) | 30 | `chronos2_hurdle` | -0.0005464 [-0.04088, 0.0411]; median 0.006667; 14 / 0 / 16; p 0.894 | 0.01149 [0.0007564, 0.02402]; median 0.003021; 12 / 0 / 18; p 0.159 | 0.004825 [0.0007721, 0.00919]; median 0.000953; 11 / 0 / 19; p 0.0786 | -0.01148 [-0.0469, 0.02345]; median -0.01035; 17 / 0 / 13; p 0.544 |
| all (n = 30) | 30 | `timesfm3_hurdle` | 0.03006 [-0.006534, 0.06904]; median 0.01596; 13 / 0 / 17; p 0.213 | 0.01503 [0.004496, 0.0269]; median 0.008848; 6 / 0 / 24; p 0.00567 | 0.004825 [0.0007112, 0.009235]; median 0.000953; 11 / 0 / 19; p 0.0786 | 0.02204 [-0.008037, 0.05345]; median 0.01016; 13 / 0 / 17; p 0.262 |
| all (n = 30) | 30 | `timesfm2p5_hurdle` | -0.009523 [-0.04595, 0.02954]; median -0.01327; 18 / 0 / 12; p 0.382 | 0.01067 [-0.0003718, 0.02389]; median 0.005888; 13 / 0 / 17; p 0.199 | 0.004825 [0.000716, 0.009193]; median 0.000953; 11 / 0 / 19; p 0.0786 | -0.02271 [-0.05457, 0.0107]; median -0.02553; 18 / 0 / 12; p 0.125 |
| all (n = 30) | 30 | `hurdle_count_28` | 0.05156 [0.01101, 0.09512]; median 0.0216; 11 / 0 / 19; p 0.0397 | 0.01111 [-0.00131, 0.0253]; median 0.007974; 11 / 0 / 19; p 0.12 | 0.004825 [0.0007737, 0.009144]; median 0.000953; 11 / 0 / 19; p 0.0786 | 0.03952 [0.002542, 0.07848]; median 0.01237; 11 / 0 / 19; p 0.0859 |
| all (n = 30) | 30 | `dynamic_count` | 0.1492 [0.09502, 0.2113]; median 0.09122; 2 / 0 / 28; p 8.47e-06 | 0.03231 [0.0189, 0.04923]; median 0.02239; 2 / 0 / 28; p 1.13e-05 | 0.01378 [0.008617, 0.01957]; median 0.009721; 4 / 0 / 26; p 1.64e-05 | 0.1285 [0.08204, 0.1809]; median 0.09289; 1 / 0 / 29; p 6.34e-06 |

### The grid per cell: `tsb_hurdle`, qscore9, h = 7

Each entry: mean difference / median difference (series lower, of 30).

| Cell (n = 30) | Zero probability | Positive mean | Persistence | `tsb_hurdle` vs `chronos2_completed` | `tsb_hurdle` vs `timesfm3_completed` | `tsb_hurdle` vs `timesfm2p5_completed` | `tsb_hurdle` vs `chronos2_hurdle` | `tsb_hurdle` vs `timesfm3_hurdle` | `tsb_hurdle` vs `timesfm2p5_hurdle` | `tsb_hurdle` vs `hurdle_count_28` | `tsb_hurdle` vs `dynamic_count` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cell00 | 0.2 | 1 | 0 | 0.01143 / 0.008995 (11) | 0.006314 / 0.002116 (9) | 0.00776 / 0.009524 (12) | 0.009489 / 0.004233 (6) | 0.009489 / 0.004233 (6) | 0.009489 / 0.004233 (6) | 0.009489 / 0.004233 (6) | 0.01083 / 0.008466 (8) |
| cell01 | 0.2 | 1 | 0.8 | 0.03235 / 0.02593 (10) | 0.03735 / 0.02011 (8) | 0.03679 / 0.0291 (8) | -0.009771 / -0.01481 (17) | -0.009524 / -0.01111 (16) | -0.01083 / -0.01111 (18) | -0.005679 / -0.007407 (16) | 0.03697 / 0.03651 (9) |
| cell02 | 0.2 | 5 | 0 | 0.04681 / 0.0418 (8) | 0.05005 / 0.03228 (6) | 0.05506 / 0.0254 (5) | -0.001023 / 0.01005 (12) | 0.02265 / 0.01852 (7) | 0.01164 / 0.01164 (10) | 0.04138 / 0.0254 (6) | 0.05347 / 0.03598 (6) |
| cell03 | 0.2 | 5 | 0.8 | 0.1347 / 0.1069 (10) | 0.1375 / 0.128 (10) | 0.1493 / 0.09735 (12) | -0.05933 / -0.07566 (20) | -0.06455 / -0.0619 (22) | -0.08681 / -0.1063 (23) | -0.02071 / -0.0381 (19) | 0.1874 / 0.1878 (9) |
| cell04 | 0.2 | 25 | 0 | 0.1934 / 0.1376 (9) | 0.2277 / 0.1566 (8) | 0.03587 / 0.07989 (13) | -0.3813 / -0.3899 (21) | -0.2186 / -0.191 (19) | -0.4511 / -0.3196 (23) | 0.2247 / 0.1772 (7) | 0.2861 / 0.2275 (4) |
| cell05 | 0.2 | 25 | 0.8 | 0.7818 / 0.4974 (10) | 0.8616 / 0.6989 (10) | 0.7142 / 0.6614 (11) | -0.6583 / -0.4698 (20) | -0.5722 / -0.4619 (22) | -0.7409 / -0.8873 (23) | -0.1391 / -0.1894 (18) | 0.9454 / 1.071 (7) |
| cell06 | 0.8 | 1 | 0 | 0.01023 / 0.003175 (11) | 0.01206 / 0.004762 (8) | -0.0005291 / -0.003175 (16) | 0.006526 / 0 (14) | 0.009559 / 0.002116 (7) | 0.009312 / 0.001058 (7) | 0.009559 / 0.002116 (7) | 0.01034 / 0.003175 (10) |
| cell07 | 0.8 | 1 | 0.8 | 0.02402 / 0.01799 (9) | 0.0284 / 0.006878 (10) | 0.02254 / 0.01534 (8) | -0.02868 / -0.02169 (18) | -0.02758 / -0.02116 (18) | -0.0291 / -0.02169 (18) | -0.02494 / -0.02063 (18) | -0.009312 / -0.007407 (19) |
| cell08 | 0.8 | 5 | 0 | 0.03503 / 0.006878 (14) | 0.03203 / 0.02169 (9) | 0.007584 / -0.001587 (15) | 0.0261 / 0.01376 (12) | 0.0254 / 0.006349 (11) | 0.005256 / -0.01111 (18) | 0.0273 / 0.006349 (12) | 0.03686 / 0.009524 (13) |
| cell09 | 0.8 | 5 | 0.8 | 0.09365 / -0.002646 (15) | 0.0928 / 0.01005 (14) | 0.1045 / 0.0127 (13) | -0.05517 / -0.01111 (19) | -0.06448 / -0.0164 (18) | -0.05319 / -0.003704 (15) | -0.08469 / -0.06878 (18) | -0.01626 / -0.007407 (16) |
| cell10 | 0.8 | 25 | 0 | 0.1823 / 0.02381 (13) | 0.2067 / 0.09101 (10) | -0.04437 / -0.1524 (21) | 0.06099 / -0.04392 (17) | 0.131 / 0.0254 (14) | -0.04586 / -0.1413 (18) | 0.1858 / 0.04815 (9) | 0.2195 / 0.05238 (12) |
| cell11 | 0.8 | 25 | 0.8 | 0.4726 / -0.001058 (15) | 0.5233 / 0.0164 (15) | 0.46 / 0.01799 (15) | -0.4025 / -0.09894 (19) | -0.3823 / -0.04444 (18) | -0.4016 / -0.004233 (16) | -0.5024 / -0.4635 (18) | -0.1483 / -0.1407 (18) |
| cell12 | 0.95 | 1 | 0 | 0.002434 / 0 (3) | 0.001799 / 0 (2) | 0.002434 / 0 (3) | 0.001376 / 0 (4) | 0.001376 / 0 (4) | 0.001376 / 0 (4) | 0.001376 / 0 (4) | 0.002434 / 0 (3) |
| cell13 | 0.95 | 1 | 0.8 | -0.0005996 / 0 (7) | 0.002716 / 0 (2) | 0.0008818 / 0 (2) | -0.004339 / 0 (9) | -0.004409 / 0 (9) | -0.004409 / 0 (9) | -0.003915 / 0 (9) | -0.00388 / 0 (6) |
| cell14 | 0.95 | 5 | 0 | 0.005467 / 0 (4) | 0.003316 / 0 (7) | 0.006631 / 0 (4) | 0.006772 / 0 (5) | 0.006384 / 0 (5) | 0.006772 / 0 (5) | 0.002857 / 0 (6) | 0.007831 / 0 (3) |
| cell15 | 0.95 | 5 | 0.8 | -0.002646 / 0 (8) | 0.02236 / 0 (3) | 0.006737 / 0 (4) | -0.01439 / 0 (9) | -0.009982 / 0 (8) | -0.009347 / 0 (8) | -0.0164 / 0 (9) | -0.01672 / 0 (6) |
| cell16 | 0.95 | 25 | 0 | 0.04272 / 0 (9) | 0.01633 / 0 (12) | 0.02614 / -0.002646 (15) | 0.04646 / 0 (5) | 0.03958 / 0 (5) | 0.04698 / 0 (5) | 0.02056 / 0 (5) | 0.04815 / 0 (3) |
| cell17 | 0.95 | 25 | 0.8 | -0.04882 / 0 (8) | 0.07273 / 0 (8) | 0.01104 / 0 (7) | -0.08166 / 0 (9) | -0.04353 / 0 (9) | -0.04399 / 0 (8) | -0.08526 / 0 (9) | -0.0854 / 0 (6) |

### The grid per cell: `tsb_hurdle`, qscore9, h = 30

Each entry: mean difference / median difference (series lower, of 30).

| Cell (n = 30) | Zero probability | Positive mean | Persistence | `tsb_hurdle` vs `chronos2_completed` | `tsb_hurdle` vs `timesfm3_completed` | `tsb_hurdle` vs `timesfm2p5_completed` | `tsb_hurdle` vs `chronos2_hurdle` | `tsb_hurdle` vs `timesfm3_hurdle` | `tsb_hurdle` vs `timesfm2p5_hurdle` | `tsb_hurdle` vs `hurdle_count_28` | `tsb_hurdle` vs `dynamic_count` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cell00 | 0.2 | 1 | 0 | 0.009424 / 0.008642 (6) | 0.0073 / 0.007407 (3) | 0.008148 / 0.006914 (9) | 0.008148 / 0.006173 (1) | 0.008148 / 0.006173 (1) | 0.008148 / 0.006173 (1) | 0.008148 / 0.006173 (1) | 0.009218 / 0.009877 (5) |
| cell01 | 0.2 | 1 | 0.8 | 0.03215 / 0.01753 (10) | 0.04444 / 0.02605 (8) | 0.04422 / 0.01988 (9) | 0.01123 / -0.003333 (18) | 0.01354 / -0.0004938 (15) | 0.01352 / -0.001358 (16) | 0.01531 / 0 (13) | 0.05078 / 0.0321 (10) |
| cell02 | 0.2 | 5 | 0 | 0.04352 / 0.0479 (7) | 0.05257 / 0.0437 (3) | 0.04851 / 0.04457 (4) | 0.006329 / 0.0137 (13) | 0.03128 / 0.03309 (10) | 0.02566 / 0.03802 (10) | 0.03835 / 0.0284 (6) | 0.05594 / 0.04765 (2) |
| cell03 | 0.2 | 5 | 0.8 | 0.1538 / 0.1527 (10) | 0.1749 / 0.1299 (8) | 0.2015 / 0.1354 (11) | 0.03663 / -0.006049 (17) | 0.04787 / 0.01852 (13) | 0.03547 / -0.01 (16) | 0.07284 / 0.03457 (11) | 0.2247 / 0.1628 (5) |
| cell04 | 0.2 | 25 | 0 | 0.1389 / 0.1011 (9) | 0.2019 / 0.162 (5) | 0.0547 / 0.03494 (14) | -0.327 / -0.3373 (27) | -0.1387 / -0.1157 (18) | -0.3802 / -0.39 (28) | 0.1886 / 0.1852 (5) | 0.2524 / 0.2148 (2) |
| cell05 | 0.2 | 25 | 0.8 | 0.787 / 0.5921 (9) | 0.9686 / 0.4421 (9) | 0.7502 / 0.3888 (10) | -0.1896 / -0.1685 (16) | 0.03439 / -0.1031 (17) | -0.2188 / -0.1231 (18) | 0.3426 / 0.01975 (14) | 1.189 / 0.8272 (4) |
| cell06 | 0.8 | 1 | 0 | 0.007646 / 0.005309 (5) | 0.009103 / 0.009012 (2) | 0.005218 / 0.00358 (10) | 0.004626 / 0.002469 (10) | 0.007572 / 0.007407 (2) | 0.007366 / 0.007284 (3) | 0.007572 / 0.007407 (2) | 0.008477 / 0.006173 (3) |
| cell07 | 0.8 | 1 | 0.8 | 0.008519 / 0.0007407 (14) | 0.02526 / 0.01778 (11) | 0.01682 / 0.009877 (9) | -0.002938 / 0.0007407 (12) | -0.001893 / 0.001235 (12) | -0.003506 / 0 (12) | 0.0007407 / 0.002469 (12) | 0.01654 / 0.008642 (12) |
| cell08 | 0.8 | 5 | 0 | 0.02801 / 0.01691 (4) | 0.0211 / 0.0121 (7) | 0.002132 / -0.0002469 (15) | 0.02296 / 0.01568 (7) | 0.02358 / 0.0158 (5) | 0.00744 / -0.001358 (15) | 0.0237 / 0.02099 (7) | 0.02998 / 0.02469 (4) |
| cell09 | 0.8 | 5 | 0.8 | 0.03612 / -0.00284 (15) | 0.07501 / 0.05049 (11) | 0.05472 / 0.02309 (13) | 0.01939 / 0.009753 (12) | 0.02487 / 0.002099 (13) | 0.02873 / -0.003086 (15) | 0.006337 / 0 (13) | 0.06877 / 0.009877 (11) |
| cell10 | 0.8 | 25 | 0 | 0.1362 / 0.07778 (8) | 0.1464 / 0.1128 (4) | -0.05816 / -0.1062 (21) | 0.05435 / -0.0008642 (15) | 0.1001 / 0.07543 (9) | -0.03671 / -0.0621 (19) | 0.1502 / 0.1494 (6) | 0.1785 / 0.1352 (3) |
| cell11 | 0.8 | 25 | 0.8 | 0.286 / 0.156 (13) | 0.4356 / 0.2667 (13) | 0.2736 / 0.07975 (13) | 0.1854 / 0 (14) | 0.2328 / 0.01259 (12) | 0.1457 / 0.01605 (13) | 0.03062 / 0.003704 (13) | 0.3857 / 0.1491 (12) |
| cell12 | 0.95 | 1 | 0 | 0.002691 / 0 (0) | 0.001086 / 0 (7) | 0.002798 / 0 (0) | 0.001317 / 0 (3) | 0.001317 / 0 (3) | 0.001317 / 0 (3) | 0.001317 / 0 (3) | 0.002798 / 0 (0) |
| cell13 | 0.95 | 1 | 0.8 | -0.006239 / 0 (9) | 0.002156 / 0 (8) | 0.004683 / 0 (2) | 0.0005926 / 0 (7) | 0.0004033 / 0 (7) | 0.0004362 / 0 (7) | 0.0009877 / 0 (7) | 0.005597 / 0 (3) |
| cell14 | 0.95 | 5 | 0 | 0.006757 / 0 (2) | -0.001366 / -0.001111 (17) | 0.005605 / 0 (4) | 0.006502 / 0 (3) | 0.005621 / 0 (3) | 0.006502 / 0 (3) | 0.002058 / 0 (5) | 0.007984 / 0 (0) |
| cell15 | 0.95 | 5 | 0.8 | -0.03673 / 0 (13) | -0.00935 / 0 (10) | -0.002914 / 0 (7) | 0.006214 / 0 (7) | 0.01102 / 0 (6) | 0.0164 / 0 (6) | 0.0009877 / 0 (7) | 0.02074 / 0 (3) |
| cell16 | 0.95 | 25 | 0 | 0.04587 / 0 (12) | -0.005202 / -0.004815 (19) | 0.02262 / -0.004321 (17) | 0.05109 / 0 (3) | 0.03966 / 0 (3) | 0.05144 / 0 (3) | 0.01909 / 0 (5) | 0.05325 / 0 (0) |
| cell17 | 0.95 | 25 | 0.8 | -0.1416 / 0 (14) | -0.04912 / 0 (14) | -0.02732 / 0 (13) | 0.09487 / 0 (6) | 0.09962 / 0 (6) | 0.1197 / 0 (6) | 0.01868 / 0 (7) | 0.1248 / 0 (3) |

### The grid per cell: `tsb_hurdle`, context_scaled_qscore9, h = 7

Each entry: mean difference / median difference (series lower, of 30).

| Cell (n = 30) | Zero probability | Positive mean | Persistence | `tsb_hurdle` vs `chronos2_completed` | `tsb_hurdle` vs `timesfm3_completed` | `tsb_hurdle` vs `timesfm2p5_completed` | `tsb_hurdle` vs `chronos2_hurdle` | `tsb_hurdle` vs `timesfm3_hurdle` | `tsb_hurdle` vs `timesfm2p5_hurdle` | `tsb_hurdle` vs `hurdle_count_28` | `tsb_hurdle` vs `dynamic_count` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cell00 | 0.2 | 1 | 0 | 0.01143 / 0.008995 (11) | 0.006314 / 0.002116 (9) | 0.00776 / 0.009524 (12) | 0.009489 / 0.004233 (6) | 0.009489 / 0.004233 (6) | 0.009489 / 0.004233 (6) | 0.009489 / 0.004233 (6) | 0.01083 / 0.008466 (8) |
| cell01 | 0.2 | 1 | 0.8 | 0.03235 / 0.02593 (10) | 0.03735 / 0.02011 (8) | 0.03679 / 0.0291 (8) | -0.009771 / -0.01481 (17) | -0.009524 / -0.01111 (16) | -0.01083 / -0.01111 (18) | -0.005679 / -0.007407 (16) | 0.03697 / 0.03651 (9) |
| cell02 | 0.2 | 5 | 0 | 0.01173 / 0.009763 (8) | 0.01249 / 0.007644 (7) | 0.01371 / 0.006629 (5) | -0.0001227 / 0.002281 (12) | 0.006 / 0.00409 (7) | 0.002998 / 0.002987 (10) | 0.01037 / 0.006205 (6) | 0.01334 / 0.008457 (6) |
| cell03 | 0.2 | 5 | 0.8 | 0.03395 / 0.02653 (10) | 0.03536 / 0.03489 (10) | 0.03893 / 0.02394 (12) | -0.01554 / -0.01634 (20) | -0.01633 / -0.01615 (22) | -0.02186 / -0.02301 (23) | -0.005248 / -0.008861 (20) | 0.04807 / 0.05189 (9) |
| cell04 | 0.2 | 25 | 0 | 0.009671 / 0.006784 (9) | 0.01138 / 0.008246 (8) | 0.001798 / 0.003999 (13) | -0.01931 / -0.01892 (21) | -0.0111 / -0.009693 (20) | -0.02295 / -0.01646 (23) | 0.01131 / 0.008945 (6) | 0.01426 / 0.01103 (3) |
| cell05 | 0.2 | 25 | 0.8 | 0.04072 / 0.02501 (10) | 0.04431 / 0.03539 (10) | 0.03695 / 0.03511 (11) | -0.03456 / -0.0227 (20) | -0.02981 / -0.023 (22) | -0.03892 / -0.04388 (23) | -0.00704 / -0.009101 (18) | 0.04867 / 0.05671 (7) |
| cell06 | 0.8 | 1 | 0 | 0.01023 / 0.003175 (11) | 0.01206 / 0.004762 (8) | -0.0005291 / -0.003175 (16) | 0.006526 / 0 (14) | 0.009559 / 0.002116 (7) | 0.009312 / 0.001058 (7) | 0.009559 / 0.002116 (7) | 0.01034 / 0.003175 (10) |
| cell07 | 0.8 | 1 | 0.8 | 0.02402 / 0.01799 (9) | 0.0284 / 0.006878 (10) | 0.02254 / 0.01534 (8) | -0.02868 / -0.02169 (18) | -0.02758 / -0.02116 (18) | -0.0291 / -0.02169 (18) | -0.02494 / -0.02063 (18) | -0.009312 / -0.007407 (19) |
| cell08 | 0.8 | 5 | 0 | 0.03282 / 0.006878 (14) | 0.03117 / 0.01874 (9) | 0.006503 / -0.001587 (15) | 0.02424 / 0.01147 (12) | 0.02371 / 0.006128 (11) | 0.003324 / -0.01111 (18) | 0.02573 / 0.006407 (12) | 0.03505 / 0.007525 (13) |
| cell09 | 0.8 | 5 | 0.8 | 0.0803 / -0.002646 (15) | 0.07087 / 0.01005 (14) | 0.08145 / 0.01206 (13) | -0.04572 / -0.01111 (19) | -0.05893 / -0.0164 (18) | -0.05039 / -0.003704 (15) | -0.08042 / -0.06807 (18) | -0.02838 / -0.007407 (16) |
| cell10 | 0.8 | 25 | 0 | 0.03743 / 0.005388 (13) | 0.04319 / 0.01999 (10) | -0.01335 / -0.02919 (21) | 0.009333 / -0.01038 (17) | 0.0243 / 0.004041 (14) | -0.0137 / -0.0328 (18) | 0.03916 / 0.009936 (9) | 0.04558 / 0.01091 (12) |
| cell11 | 0.8 | 25 | 0.8 | 0.08626 / 0.01214 (14) | 0.08829 / 0.004371 (15) | 0.08833 / 0.004794 (15) | -0.09536 / -0.02436 (19) | -0.09767 / -0.02308 (18) | -0.09707 / -0.005428 (17) | -0.1219 / -0.09316 (18) | -0.06636 / -0.03254 (19) |
| cell12 | 0.95 | 1 | 0 | 0.002434 / 0 (3) | 0.001799 / 0 (2) | 0.002434 / 0 (3) | 0.001376 / 0 (4) | 0.001376 / 0 (4) | 0.001376 / 0 (4) | 0.001376 / 0 (4) | 0.002434 / 0 (3) |
| cell13 | 0.95 | 1 | 0.8 | -0.0005996 / 0 (7) | 0.002716 / 0 (2) | 0.0008818 / 0 (2) | -0.004339 / 0 (9) | -0.004409 / 0 (9) | -0.004409 / 0 (9) | -0.003915 / 0 (9) | -0.00388 / 0 (6) |
| cell14 | 0.95 | 5 | 0 | 0.005467 / 0 (4) | 0.003316 / 0 (7) | 0.006631 / 0 (4) | 0.006772 / 0 (5) | 0.006384 / 0 (5) | 0.006772 / 0 (5) | 0.002857 / 0 (6) | 0.007831 / 0 (3) |
| cell15 | 0.95 | 5 | 0.8 | -0.002646 / 0 (8) | 0.02236 / 0 (3) | 0.006737 / 0 (4) | -0.01439 / 0 (9) | -0.009982 / 0 (8) | -0.009347 / 0 (8) | -0.0164 / 0 (9) | -0.01672 / 0 (6) |
| cell16 | 0.95 | 25 | 0 | 0.03218 / 0 (9) | 0.01263 / 0 (12) | 0.01921 / -0.002327 (15) | 0.03526 / 0 (5) | 0.03024 / 0 (5) | 0.03567 / 0 (5) | 0.0167 / 0 (5) | 0.03646 / 0 (3) |
| cell17 | 0.95 | 25 | 0.8 | 0.01587 / 0 (8) | 0.08283 / 0 (8) | 0.05774 / 0 (7) | -0.03686 / 0 (9) | -0.01355 / 0 (9) | -0.01359 / 0 (8) | -0.05016 / 0 (9) | -0.05001 / 0 (6) |

### The grid per cell: `tsb_hurdle`, context_scaled_qscore9, h = 30

Each entry: mean difference / median difference (series lower, of 30).

| Cell (n = 30) | Zero probability | Positive mean | Persistence | `tsb_hurdle` vs `chronos2_completed` | `tsb_hurdle` vs `timesfm3_completed` | `tsb_hurdle` vs `timesfm2p5_completed` | `tsb_hurdle` vs `chronos2_hurdle` | `tsb_hurdle` vs `timesfm3_hurdle` | `tsb_hurdle` vs `timesfm2p5_hurdle` | `tsb_hurdle` vs `hurdle_count_28` | `tsb_hurdle` vs `dynamic_count` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cell00 | 0.2 | 1 | 0 | 0.009424 / 0.008642 (6) | 0.0073 / 0.007407 (3) | 0.008148 / 0.006914 (9) | 0.008148 / 0.006173 (1) | 0.008148 / 0.006173 (1) | 0.008148 / 0.006173 (1) | 0.008148 / 0.006173 (1) | 0.009218 / 0.009877 (5) |
| cell01 | 0.2 | 1 | 0.8 | 0.03215 / 0.01753 (10) | 0.04444 / 0.02605 (8) | 0.04422 / 0.01988 (9) | 0.01123 / -0.003333 (18) | 0.01354 / -0.0004938 (15) | 0.01352 / -0.001358 (16) | 0.01531 / 0 (13) | 0.05078 / 0.0321 (10) |
| cell02 | 0.2 | 5 | 0 | 0.01104 / 0.01157 (7) | 0.01327 / 0.01137 (3) | 0.01229 / 0.01095 (4) | 0.001628 / 0.003233 (13) | 0.008022 / 0.007751 (10) | 0.006504 / 0.008949 (10) | 0.009681 / 0.007379 (6) | 0.0141 / 0.01224 (1) |
| cell03 | 0.2 | 5 | 0.8 | 0.03811 / 0.04369 (10) | 0.0451 / 0.035 (8) | 0.05299 / 0.03149 (11) | 0.008648 / -0.002062 (17) | 0.01246 / 0.004035 (13) | 0.00942 / -0.002028 (18) | 0.01928 / 0.008581 (11) | 0.05722 / 0.04456 (5) |
| cell04 | 0.2 | 25 | 0 | 0.007101 / 0.004944 (9) | 0.01022 / 0.007929 (5) | 0.002865 / 0.001618 (14) | -0.01654 / -0.01629 (27) | -0.007025 / -0.005512 (19) | -0.0193 / -0.01919 (28) | 0.009513 / 0.009378 (5) | 0.01271 / 0.01111 (2) |
| cell05 | 0.2 | 25 | 0.8 | 0.03964 / 0.03093 (9) | 0.0481 / 0.022 (9) | 0.0388 / 0.02153 (11) | -0.01195 / -0.00814 (16) | -3.341e-06 / -0.005333 (17) | -0.01327 / -0.005223 (18) | 0.018 / 0.0008351 (14) | 0.06096 / 0.04208 (4) |
| cell06 | 0.8 | 1 | 0 | 0.007646 / 0.005309 (5) | 0.009103 / 0.009012 (2) | 0.005218 / 0.00358 (10) | 0.004626 / 0.002469 (10) | 0.007572 / 0.007407 (2) | 0.007366 / 0.007284 (3) | 0.007572 / 0.007407 (2) | 0.008477 / 0.006173 (3) |
| cell07 | 0.8 | 1 | 0.8 | 0.008519 / 0.0007407 (14) | 0.02526 / 0.01778 (11) | 0.01682 / 0.009877 (9) | -0.002938 / 0.0007407 (12) | -0.001893 / 0.001235 (12) | -0.003506 / 0 (12) | 0.0007407 / 0.002469 (12) | 0.01654 / 0.008642 (12) |
| cell08 | 0.8 | 5 | 0 | 0.02648 / 0.01684 (4) | 0.02103 / 0.0121 (7) | 0.002357 / -0.0002469 (15) | 0.02122 / 0.01423 (7) | 0.02201 / 0.0121 (5) | 0.005839 / -0.001358 (15) | 0.02227 / 0.01852 (7) | 0.0285 / 0.02334 (4) |
| cell09 | 0.8 | 5 | 0.8 | 0.02783 / -0.00284 (15) | 0.06077 / 0.05106 (11) | 0.04225 / 0.02309 (13) | 0.01878 / 0.009753 (12) | 0.02301 / 0.002143 (12) | 0.02176 / -0.0018 (15) | 0.005323 / 0 (13) | 0.05178 / 0.009877 (12) |
| cell10 | 0.8 | 25 | 0 | 0.02858 / 0.01645 (8) | 0.03318 / 0.0215 (4) | -0.01383 / -0.01973 (21) | 0.007177 / -0.0006452 (16) | 0.01734 / 0.01705 (8) | -0.01274 / -0.0162 (19) | 0.03284 / 0.02901 (6) | 0.0387 / 0.03161 (3) |
| cell11 | 0.8 | 25 | 0.8 | 0.05771 / 0.02798 (14) | 0.08982 / 0.06497 (13) | 0.05074 / 0.02106 (13) | 0.02927 / 0 (14) | 0.04197 / 0.004153 (12) | 0.01596 / 0.004532 (13) | 0.007618 / 0 (14) | 0.06619 / 0.03823 (13) |
| cell12 | 0.95 | 1 | 0 | 0.002691 / 0 (0) | 0.001086 / 0 (7) | 0.002798 / 0 (0) | 0.001317 / 0 (3) | 0.001317 / 0 (3) | 0.001317 / 0 (3) | 0.001317 / 0 (3) | 0.002798 / 0 (0) |
| cell13 | 0.95 | 1 | 0.8 | -0.006239 / 0 (9) | 0.002156 / 0 (8) | 0.004683 / 0 (2) | 0.0005926 / 0 (7) | 0.0004033 / 0 (7) | 0.0004362 / 0 (7) | 0.0009877 / 0 (7) | 0.005597 / 0 (3) |
| cell14 | 0.95 | 5 | 0 | 0.006757 / 0 (2) | -0.001366 / -0.001111 (17) | 0.005605 / 0 (4) | 0.006502 / 0 (3) | 0.005621 / 0 (3) | 0.006502 / 0 (3) | 0.002058 / 0 (5) | 0.007984 / 0 (0) |
| cell15 | 0.95 | 5 | 0.8 | -0.03673 / 0 (13) | -0.00935 / 0 (10) | -0.002914 / 0 (7) | 0.006214 / 0 (7) | 0.01102 / 0 (6) | 0.0164 / 0 (6) | 0.0009877 / 0 (7) | 0.02074 / 0 (3) |
| cell16 | 0.95 | 25 | 0 | 0.03682 / 0 (12) | -0.002901 / -0.003686 (19) | 0.01838 / -0.00416 (17) | 0.04056 / 0 (3) | 0.03221 / 0 (3) | 0.04084 / 0 (3) | 0.01775 / 0 (4) | 0.04213 / 0 (0) |
| cell17 | 0.95 | 25 | 0.8 | -0.06565 / 0 (14) | 0.002014 / 0 (14) | 0.01839 / 0 (13) | 0.07236 / 0 (6) | 0.07478 / 0 (6) | 0.08687 / 0 (6) | 0.02063 / 0 (7) | 0.0872 / 0 (3) |

### The grid per cell: `tsb_hurdle`, occurrence_brier, h = 7

Each entry: mean difference / median difference (series lower, of 30).

| Cell (n = 30) | Zero probability | Positive mean | Persistence | `tsb_hurdle` vs `chronos2_completed` | `tsb_hurdle` vs `timesfm3_completed` | `tsb_hurdle` vs `timesfm2p5_completed` | `tsb_hurdle` vs `chronos2_hurdle` | `tsb_hurdle` vs `timesfm3_hurdle` | `tsb_hurdle` vs `timesfm2p5_hurdle` | `tsb_hurdle` vs `hurdle_count_28` | `tsb_hurdle` vs `dynamic_count` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cell00 | 0.2 | 1 | 0 | 0.009588 / 0.006563 (9) | 0.006413 / 0.005867 (8) | 0.007408 / 0.006083 (9) | 0.007137 / 0.006479 (7) | 0.007137 / 0.006479 (7) | 0.007137 / 0.006479 (7) | 0.007137 / 0.006479 (7) | 0.008875 / 0.008291 (5) |
| cell01 | 0.2 | 1 | 0.8 | 0.03053 / 0.02153 (9) | 0.03662 / 0.02692 (8) | 0.03582 / 0.02368 (9) | -0.005338 / -0.006595 (16) | -0.005338 / -0.006595 (16) | -0.005338 / -0.006595 (16) | -0.005338 / -0.006595 (16) | 0.03197 / 0.03253 (8) |
| cell02 | 0.2 | 5 | 0 | 0.006979 / 0.00323 (12) | 0.007503 / 0.005036 (13) | 0.007559 / 0.002587 (13) | 0.007137 / 0.006479 (7) | 0.007137 / 0.006479 (7) | 0.007137 / 0.006479 (7) | 0.007137 / 0.006479 (7) | 0.008875 / 0.008291 (5) |
| cell03 | 0.2 | 5 | 0.8 | 0.03211 / 0.04209 (8) | 0.03699 / 0.0261 (5) | 0.04254 / 0.03106 (7) | -0.005338 / -0.006595 (16) | -0.005338 / -0.006595 (16) | -0.005338 / -0.006595 (16) | -0.005338 / -0.006595 (16) | 0.03197 / 0.03253 (8) |
| cell04 | 0.2 | 25 | 0 | -0.007883 / -0.01254 (20) | -0.001352 / -0.0007428 (17) | -0.01798 / -0.02103 (20) | 0.007137 / 0.006479 (7) | 0.007137 / 0.006479 (7) | 0.007137 / 0.006479 (7) | 0.007137 / 0.006479 (7) | 0.008875 / 0.008291 (5) |
| cell05 | 0.2 | 25 | 0.8 | 0.04421 / 0.03848 (8) | 0.04094 / 0.03787 (7) | 0.04125 / 0.02627 (7) | -0.005338 / -0.006595 (16) | -0.005338 / -0.006595 (16) | -0.005338 / -0.006595 (16) | -0.005338 / -0.006595 (16) | 0.03197 / 0.03253 (8) |
| cell06 | 0.8 | 1 | 0 | 0.007576 / 0.003075 (11) | 0.009155 / 0.004098 (12) | 0.003899 / 0.002018 (14) | 0.00609 / 0.002092 (10) | 0.00609 / 0.002092 (10) | 0.00609 / 0.002092 (10) | 0.00609 / 0.002092 (10) | 0.008404 / 0.003786 (11) |
| cell07 | 0.8 | 1 | 0.8 | 0.02523 / 0.01179 (13) | 0.02907 / 0.00684 (11) | 0.02492 / 0.01404 (10) | -0.02147 / -0.01338 (19) | -0.02147 / -0.01338 (19) | -0.02147 / -0.01338 (19) | -0.02147 / -0.01338 (19) | -0.009528 / -0.004031 (18) |
| cell08 | 0.8 | 5 | 0 | 0.008053 / 0.003954 (11) | 0.001785 / -4.146e-05 (15) | -0.004886 / -0.006474 (18) | 0.00609 / 0.002092 (10) | 0.00609 / 0.002092 (10) | 0.00609 / 0.002092 (10) | 0.00609 / 0.002092 (10) | 0.008404 / 0.003786 (11) |
| cell09 | 0.8 | 5 | 0.8 | 0.01921 / 0.004716 (14) | 0.01852 / -0.002371 (17) | 0.01993 / 0.00182 (14) | -0.02147 / -0.01338 (19) | -0.02147 / -0.01338 (19) | -0.02147 / -0.01338 (19) | -0.02147 / -0.01338 (19) | -0.009528 / -0.004031 (18) |
| cell10 | 0.8 | 25 | 0 | -0.003934 / -0.00369 (19) | -0.009781 / -0.004727 (19) | -0.05014 / -0.05008 (27) | 0.00609 / 0.002092 (10) | 0.00609 / 0.002092 (10) | 0.00609 / 0.002092 (10) | 0.00609 / 0.002092 (10) | 0.008404 / 0.003786 (11) |
| cell11 | 0.8 | 25 | 0.8 | 0.002635 / -0.006614 (18) | 0.00461 / -0.01608 (18) | -0.02229 / -0.04515 (18) | -0.02147 / -0.01338 (19) | -0.02147 / -0.01338 (19) | -0.02147 / -0.01338 (19) | -0.02147 / -0.01338 (19) | -0.009528 / -0.004031 (18) |
| cell12 | 0.95 | 1 | 0 | 0.000515 / -0.0002944 (17) | 8.793e-05 / -0.0008131 (19) | 0.0004874 / -0.0004432 (17) | -0.0003374 / -0.0008174 (20) | -0.0003374 / -0.0008174 (20) | -0.0003374 / -0.0008174 (20) | -0.0003374 / -0.0008174 (20) | 0.0006839 / 0.000418 (13) |
| cell13 | 0.95 | 1 | 0.8 | -0.003364 / -0.003681 (23) | -0.0004427 / -0.003679 (23) | -0.001979 / -0.003679 (23) | -0.004188 / -0.0002973 (26) | -0.004188 / -0.0002973 (26) | -0.004188 / -0.0002973 (26) | -0.004188 / -0.0002973 (26) | -0.00401 / -0.0002973 (23) |
| cell14 | 0.95 | 5 | 0 | -0.0005238 / -0.0008263 (20) | -0.002142 / -0.003035 (24) | -0.0007658 / -0.001448 (21) | -0.0003374 / -0.0008174 (20) | -0.0003374 / -0.0008174 (20) | -0.0003374 / -0.0008174 (20) | -0.0003374 / -0.0008174 (20) | 0.0006839 / 0.000418 (13) |
| cell15 | 0.95 | 5 | 0.8 | -0.007278 / -0.003707 (25) | -0.002042 / -0.003679 (22) | -0.009123 / -0.003679 (22) | -0.004188 / -0.0002973 (26) | -0.004188 / -0.0002973 (26) | -0.004188 / -0.0002973 (26) | -0.004188 / -0.0002973 (26) | -0.00401 / -0.0002973 (23) |
| cell16 | 0.95 | 25 | 0 | -0.001388 / -0.002721 (23) | -0.006681 / -0.005537 (27) | -0.01528 / -0.01243 (27) | -0.0003374 / -0.0008174 (20) | -0.0003374 / -0.0008174 (20) | -0.0003374 / -0.0008174 (20) | -0.0003374 / -0.0008174 (20) | 0.0006839 / 0.000418 (13) |
| cell17 | 0.95 | 25 | 0.8 | -0.01735 / -0.003852 (26) | -0.008557 / -0.003685 (22) | -0.01486 / -0.003822 (23) | -0.004188 / -0.0002973 (26) | -0.004188 / -0.0002973 (26) | -0.004188 / -0.0002973 (26) | -0.004188 / -0.0002973 (26) | -0.00401 / -0.0002973 (23) |

### The grid per cell: `tsb_hurdle`, occurrence_brier, h = 30

Each entry: mean difference / median difference (series lower, of 30).

| Cell (n = 30) | Zero probability | Positive mean | Persistence | `tsb_hurdle` vs `chronos2_completed` | `tsb_hurdle` vs `timesfm3_completed` | `tsb_hurdle` vs `timesfm2p5_completed` | `tsb_hurdle` vs `chronos2_hurdle` | `tsb_hurdle` vs `timesfm3_hurdle` | `tsb_hurdle` vs `timesfm2p5_hurdle` | `tsb_hurdle` vs `hurdle_count_28` | `tsb_hurdle` vs `dynamic_count` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cell00 | 0.2 | 1 | 0 | 0.008511 / 0.006891 (3) | 0.007044 / 0.006348 (6) | 0.007723 / 0.005722 (5) | 0.006202 / 0.004431 (5) | 0.006202 / 0.004431 (5) | 0.006202 / 0.004431 (5) | 0.006202 / 0.004431 (5) | 0.008419 / 0.00703 (3) |
| cell01 | 0.2 | 1 | 0.8 | 0.03102 / 0.02235 (9) | 0.04265 / 0.03273 (7) | 0.0431 / 0.02899 (9) | 0.0132 / 0.001895 (13) | 0.0132 / 0.001895 (13) | 0.0132 / 0.001895 (13) | 0.0132 / 0.001895 (13) | 0.04332 / 0.02668 (9) |
| cell02 | 0.2 | 5 | 0 | 0.003623 / 0.003478 (12) | 0.006513 / 0.004827 (7) | 0.004602 / 0.003662 (13) | 0.006202 / 0.004431 (5) | 0.006202 / 0.004431 (5) | 0.006202 / 0.004431 (5) | 0.006202 / 0.004431 (5) | 0.008419 / 0.00703 (3) |
| cell03 | 0.2 | 5 | 0.8 | 0.03516 / 0.02847 (11) | 0.04211 / 0.03633 (10) | 0.04891 / 0.02802 (9) | 0.0132 / 0.001895 (13) | 0.0132 / 0.001895 (13) | 0.0132 / 0.001895 (13) | 0.0132 / 0.001895 (13) | 0.04332 / 0.02668 (9) |
| cell04 | 0.2 | 25 | 0 | -0.01469 / -0.01423 (26) | -0.004256 / -0.004854 (19) | -0.02167 / -0.02144 (28) | 0.006202 / 0.004431 (5) | 0.006202 / 0.004431 (5) | 0.006202 / 0.004431 (5) | 0.006202 / 0.004431 (5) | 0.008419 / 0.00703 (3) |
| cell05 | 0.2 | 25 | 0.8 | 0.03672 / 0.0248 (12) | 0.03636 / 0.0193 (11) | 0.03259 / 0.01625 (10) | 0.0132 / 0.001895 (13) | 0.0132 / 0.001895 (13) | 0.0132 / 0.001895 (13) | 0.0132 / 0.001895 (13) | 0.04332 / 0.02668 (9) |
| cell06 | 0.8 | 1 | 0 | 0.00663 / 0.004946 (6) | 0.007195 / 0.006573 (3) | 0.005632 / 0.00368 (7) | 0.005203 / 0.003849 (5) | 0.005203 / 0.003849 (5) | 0.005203 / 0.003849 (5) | 0.005203 / 0.003849 (5) | 0.00702 / 0.0066 (4) |
| cell07 | 0.8 | 1 | 0.8 | 0.01215 / 0.002594 (14) | 0.02648 / 0.01708 (10) | 0.02286 / 0.01142 (7) | 0.002664 / 0.001244 (13) | 0.002664 / 0.001244 (13) | 0.002664 / 0.001244 (13) | 0.002664 / 0.001244 (13) | 0.01656 / 0.008106 (10) |
| cell08 | 0.8 | 5 | 0 | 0.006163 / 0.006099 (8) | -0.0009851 / -0.00119 (15) | -0.0104 / -0.01342 (23) | 0.005203 / 0.003849 (5) | 0.005203 / 0.003849 (5) | 0.005203 / 0.003849 (5) | 0.005203 / 0.003849 (5) | 0.00702 / 0.0066 (4) |
| cell09 | 0.8 | 5 | 0.8 | 0.009067 / 0.003936 (13) | 0.01581 / 0.01304 (11) | 0.00509 / 0.006728 (12) | 0.002664 / 0.001244 (13) | 0.002664 / 0.001244 (13) | 0.002664 / 0.001244 (13) | 0.002664 / 0.001244 (13) | 0.01656 / 0.008106 (10) |
| cell10 | 0.8 | 25 | 0 | -0.006777 / -0.008557 (21) | -0.008927 / -0.008027 (22) | -0.05455 / -0.05762 (30) | 0.005203 / 0.003849 (5) | 0.005203 / 0.003849 (5) | 0.005203 / 0.003849 (5) | 0.005203 / 0.003849 (5) | 0.00702 / 0.0066 (4) |
| cell11 | 0.8 | 25 | 0.8 | -0.009786 / -0.01549 (21) | -0.006895 / -0.0003008 (15) | -0.03365 / -0.03915 (21) | 0.002664 / 0.001244 (13) | 0.002664 / 0.001244 (13) | 0.002664 / 0.001244 (13) | 0.002664 / 0.001244 (13) | 0.01656 / 0.008106 (10) |
| cell12 | 0.95 | 1 | 0 | 0.001606 / 0.0007617 (7) | 0.000608 / 0.0001557 (13) | 0.001614 / 0.0007521 (8) | 0.0007557 / 0.0004454 (13) | 0.0007557 / 0.0004454 (13) | 0.0007557 / 0.0004454 (13) | 0.0007557 / 0.0004454 (13) | 0.001699 / 0.0005553 (6) |
| cell13 | 0.95 | 1 | 0.8 | -0.00589 / -0.003683 (26) | 0.001759 / -0.003679 (22) | 0.003685 / -0.003143 (21) | 0.0009248 / -0.0002973 (21) | 0.0009248 / -0.0002973 (21) | 0.0009248 / -0.0002973 (21) | 0.0009248 / -0.0002973 (21) | 0.005671 / -0.000297 (18) |
| cell14 | 0.95 | 5 | 0 | 0.00089 / 0.0006819 (10) | -0.003748 / -0.003016 (24) | -0.0004044 / -0.0003072 (18) | 0.0007557 / 0.0004454 (13) | 0.0007557 / 0.0004454 (13) | 0.0007557 / 0.0004454 (13) | 0.0007557 / 0.0004454 (13) | 0.001699 / 0.0005553 (6) |
| cell15 | 0.95 | 5 | 0.8 | -0.01115 / -0.00372 (26) | -0.006133 / -0.003679 (25) | -0.007293 / -0.003679 (24) | 0.0009248 / -0.0002973 (21) | 0.0009248 / -0.0002973 (21) | 0.0009248 / -0.0002973 (21) | 0.0009248 / -0.0002973 (21) | 0.005671 / -0.000297 (18) |
| cell16 | 0.95 | 25 | 0 | -0.001446 / -0.0007216 (19) | -0.009034 / -0.008993 (30) | -0.01744 / -0.01542 (29) | 0.0007557 / 0.0004454 (13) | 0.0007557 / 0.0004454 (13) | 0.0007557 / 0.0004454 (13) | 0.0007557 / 0.0004454 (13) | 0.001699 / 0.0005553 (6) |
| cell17 | 0.95 | 25 | 0.8 | -0.02117 / -0.006117 (28) | -0.01171 / -0.003732 (25) | -0.01595 / -0.004146 (26) | 0.0009248 / -0.0002973 (21) | 0.0009248 / -0.0002973 (21) | 0.0009248 / -0.0002973 (21) | 0.0009248 / -0.0002973 (21) | 0.005671 / -0.000297 (18) |

### The grid per cell: `tsb_hurdle`, discrete_crps, h = 7

Each entry: mean difference / median difference (series lower, of 30).

| Cell (n = 30) | Zero probability | Positive mean | Persistence | `tsb_hurdle` vs `chronos2_completed` | `tsb_hurdle` vs `timesfm3_completed` | `tsb_hurdle` vs `timesfm2p5_completed` | `tsb_hurdle` vs `chronos2_hurdle` | `tsb_hurdle` vs `timesfm3_hurdle` | `tsb_hurdle` vs `timesfm2p5_hurdle` | `tsb_hurdle` vs `hurdle_count_28` | `tsb_hurdle` vs `dynamic_count` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cell00 | 0.2 | 1 | 0 | 0.005288 / 0.002258 (14) | 0.002108 / 0.00155 (14) | 0.002583 / 0.001348 (14) | 0.003229 / 0.002394 (11) | 0.002567 / 0.001735 (11) | 0.002999 / 0.002085 (12) | 0.007137 / 0.006479 (7) | 0.008875 / 0.008291 (5) |
| cell01 | 0.2 | 1 | 0.8 | 0.02637 / 0.01742 (10) | 0.03241 / 0.02254 (10) | 0.03167 / 0.01961 (11) | -0.01283 / -0.01502 (20) | -0.01303 / -0.01457 (19) | -0.01368 / -0.01628 (19) | -0.005338 / -0.006595 (16) | 0.03197 / 0.03253 (8) |
| cell02 | 0.2 | 5 | 0 | 0.04842 / 0.03606 (5) | 0.05274 / 0.04149 (4) | 0.05206 / 0.04693 (7) | 0.004087 / 0.01069 (14) | 0.02866 / 0.03106 (9) | 0.01742 / 0.02158 (14) | 0.0348 / 0.02494 (6) | 0.05378 / 0.03681 (2) |
| cell03 | 0.2 | 5 | 0.8 | 0.117 / 0.08014 (8) | 0.1255 / 0.1097 (8) | 0.1338 / 0.08641 (11) | -0.05877 / -0.06777 (19) | -0.05683 / -0.04274 (21) | -0.083 / -0.09159 (23) | -0.01855 / -0.01421 (18) | 0.1704 / 0.1773 (7) |
| cell04 | 0.2 | 25 | 0 | 0.1424 / 0.129 (10) | 0.179 / 0.1149 (6) | -0.000288 / -0.01377 (15) | -0.3515 / -0.3521 (22) | -0.2033 / -0.1822 (20) | -0.4165 / -0.2808 (23) | 0.1791 / 0.1646 (5) | 0.2468 / 0.205 (3) |
| cell05 | 0.2 | 25 | 0.8 | 0.6796 / 0.4278 (10) | 0.7637 / 0.4993 (11) | 0.6154 / 0.5228 (11) | -0.6193 / -0.3769 (20) | -0.5355 / -0.371 (22) | -0.6857 / -0.6627 (23) | -0.1222 / -0.13 (19) | 0.8274 / 0.8665 (6) |
| cell06 | 0.8 | 1 | 0 | 0.003709 / -0.0004126 (16) | 0.005387 / 0.0002052 (15) | 0.002045 / 0.0004487 (14) | -0.0004453 / -0.004802 (18) | 0.002367 / -0.001166 (17) | 0.001497 / -0.001421 (17) | 0.00609 / 0.002092 (10) | 0.008404 / 0.003786 (11) |
| cell07 | 0.8 | 1 | 0.8 | 0.02296 / 0.009651 (13) | 0.0265 / 0.004988 (14) | 0.02303 / 0.01252 (10) | -0.02708 / -0.01795 (21) | -0.02628 / -0.01825 (21) | -0.02822 / -0.01851 (21) | -0.02147 / -0.01338 (19) | -0.009528 / -0.004031 (18) |
| cell08 | 0.8 | 5 | 0 | 0.02953 / 0.009148 (13) | 0.02278 / 0.01147 (9) | -0.008942 / -0.01467 (18) | 0.02008 / 0.01217 (9) | 0.02171 / 0.01211 (9) | -0.01356 / -0.02337 (19) | 0.01957 / 0.008934 (12) | 0.03114 / 0.009353 (10) |
| cell09 | 0.8 | 5 | 0.8 | 0.08126 / -0.003144 (17) | 0.07694 / -0.002735 (16) | 0.08751 / 0.00411 (15) | -0.05384 / -0.02442 (20) | -0.06292 / -0.02221 (19) | -0.06203 / -0.013 (18) | -0.08431 / -0.04928 (20) | -0.02483 / -0.02159 (19) |
| cell10 | 0.8 | 25 | 0 | 0.1111 / -0.01716 (16) | 0.1331 / 0.05256 (12) | -0.121 / -0.1338 (24) | 0.0281 / -0.04641 (18) | 0.1013 / 0.03374 (13) | -0.1654 / -0.3212 (19) | 0.1194 / 0.03328 (12) | 0.1766 / 0.05594 (13) |
| cell11 | 0.8 | 25 | 0.8 | 0.3848 / 0.006015 (15) | 0.4476 / -0.02774 (17) | 0.3716 / -0.01904 (17) | -0.4054 / -0.1346 (18) | -0.3681 / -0.08928 (20) | -0.4253 / 0.008882 (14) | -0.4903 / -0.3689 (20) | -0.1961 / -0.1327 (19) |
| cell12 | 0.95 | 1 | 0 | -7.793e-05 / -0.000876 (19) | -0.0006903 / -0.001493 (20) | -0.0001416 / -0.001067 (19) | -0.001087 / -0.001263 (21) | -0.001076 / -0.001213 (21) | -0.001087 / -0.001263 (21) | -0.0003374 / -0.0008174 (20) | 0.0006839 / 0.000418 (13) |
| cell13 | 0.95 | 1 | 0.8 | -0.004411 / -0.004257 (23) | -0.001232 / -0.004255 (23) | -0.002765 / -0.004255 (23) | -0.005207 / -0.0003438 (26) | -0.005168 / -0.0003438 (26) | -0.005167 / -0.0003438 (26) | -0.004188 / -0.0002973 (26) | -0.00401 / -0.0002973 (23) |
| cell14 | 0.95 | 5 | 0 | 0.0009284 / -0.0006637 (16) | -0.0004676 / 0.0002071 (14) | 0.002002 / 0.0004506 (15) | 0.001787 / 0.001631 (13) | 0.001735 / 0.0009482 (14) | 0.00199 / 0.001631 (13) | -0.003009 / -0.000756 (18) | 0.002174 / 0.0006085 (14) |
| cell15 | 0.95 | 5 | 0.8 | -0.01132 / -0.004287 (24) | 0.01118 / -0.004255 (21) | -0.003129 / -0.004255 (22) | -0.01819 / -0.0003438 (24) | -0.01463 / -0.0003438 (22) | -0.01526 / -0.0003438 (22) | -0.01746 / -0.0002973 (25) | -0.01686 / -0.0002973 (22) |
| cell16 | 0.95 | 25 | 0 | -0.01428 / -0.001298 (15) | -0.02533 / -0.01426 (19) | -0.02632 / -0.01149 (17) | -0.01096 / 0.0006565 (14) | -0.004329 / 0.001985 (14) | -0.009451 / 0.0006582 (14) | -0.02353 / -0.009259 (17) | 0.002534 / 0.0001669 (14) |
| cell17 | 0.95 | 25 | 0.8 | -0.1042 / -0.004476 (25) | 0.01689 / -0.004255 (20) | -0.03919 / -0.004255 (20) | -0.1269 / -0.0003438 (22) | -0.0869 / -0.0003438 (20) | -0.08793 / -0.0003435 (19) | -0.0935 / -0.0002973 (24) | -0.09083 / -0.0002973 (22) |

### The grid per cell: `tsb_hurdle`, discrete_crps, h = 30

Each entry: mean difference / median difference (series lower, of 30).

| Cell (n = 30) | Zero probability | Positive mean | Persistence | `tsb_hurdle` vs `chronos2_completed` | `tsb_hurdle` vs `timesfm3_completed` | `tsb_hurdle` vs `timesfm2p5_completed` | `tsb_hurdle` vs `chronos2_hurdle` | `tsb_hurdle` vs `timesfm3_hurdle` | `tsb_hurdle` vs `timesfm2p5_hurdle` | `tsb_hurdle` vs `hurdle_count_28` | `tsb_hurdle` vs `dynamic_count` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cell00 | 0.2 | 1 | 0 | 0.004208 / 0.002599 (12) | 0.00274 / 0.002059 (11) | 0.003096 / 0.001138 (12) | 0.002234 / 0.0002424 (13) | 0.001604 / -0.0002907 (16) | 0.001921 / 7.876e-05 (15) | 0.006202 / 0.004431 (5) | 0.008419 / 0.00703 (3) |
| cell01 | 0.2 | 1 | 0.8 | 0.0268 / 0.01802 (12) | 0.03833 / 0.02844 (11) | 0.03851 / 0.02382 (12) | 0.005769 / -0.003316 (18) | 0.00736 / -0.003447 (17) | 0.00765 / -0.001355 (17) | 0.0132 / 0.001895 (13) | 0.04332 / 0.02668 (9) |
| cell02 | 0.2 | 5 | 0 | 0.04148 / 0.04393 (6) | 0.04828 / 0.04214 (2) | 0.04298 / 0.03985 (2) | 0.007516 / 0.007351 (14) | 0.02806 / 0.02297 (8) | 0.02009 / 0.02217 (10) | 0.03115 / 0.0242 (6) | 0.05063 / 0.04767 (2) |
| cell03 | 0.2 | 5 | 0.8 | 0.1349 / 0.1125 (9) | 0.1594 / 0.1034 (6) | 0.1825 / 0.1133 (8) | 0.02774 / 0.01839 (13) | 0.03866 / 0.03811 (13) | 0.02314 / 0.009978 (14) | 0.05958 / 0.04137 (10) | 0.1971 / 0.1325 (4) |
| cell04 | 0.2 | 25 | 0 | 0.1026 / 0.05224 (11) | 0.1646 / 0.1124 (4) | 0.02897 / -0.01186 (16) | -0.2986 / -0.2961 (28) | -0.1276 / -0.09299 (20) | -0.3425 / -0.3293 (27) | 0.1548 / 0.1234 (5) | 0.2313 / 0.1908 (1) |
| cell05 | 0.2 | 25 | 0.8 | 0.6869 / 0.4292 (10) | 0.8716 / 0.4445 (9) | 0.6669 / 0.2581 (11) | -0.1962 / -0.05675 (16) | 0.02564 / -0.04191 (15) | -0.2016 / -0.1201 (17) | 0.3023 / 0.1239 (13) | 1.029 / 0.5818 (5) |
| cell06 | 0.8 | 1 | 0 | 0.002493 / 0.001694 (13) | 0.003218 / 0.002334 (10) | 0.003095 / 0.001188 (11) | -0.001413 / -0.001522 (16) | 0.00142 / 0.0001668 (15) | 0.0009763 / 0.0001173 (15) | 0.005203 / 0.003849 (5) | 0.00702 / 0.0066 (4) |
| cell07 | 0.8 | 1 | 0.8 | 0.009486 / 0.0004291 (15) | 0.02297 / 0.01314 (11) | 0.0211 / 0.01026 (9) | -0.003015 / -0.0001391 (15) | -0.002261 / 1.856e-05 (15) | -0.004133 / -0.0001587 (15) | 0.002664 / 0.001244 (13) | 0.01656 / 0.008106 (10) |
| cell08 | 0.8 | 5 | 0 | 0.02026 / 0.01275 (7) | 0.01293 / 0.007336 (10) | -0.007897 / -0.0149 (21) | 0.01526 / 0.00789 (10) | 0.01964 / 0.01635 (5) | -0.004354 / -0.01928 (20) | 0.01666 / 0.01331 (6) | 0.02535 / 0.01985 (3) |
| cell09 | 0.8 | 5 | 0.8 | 0.03019 / -0.02249 (16) | 0.07071 / 0.04885 (13) | 0.04593 / 0.01235 (12) | 0.01298 / 0.0002496 (14) | 0.02137 / -0.0002849 (15) | 0.01567 / -0.005009 (15) | 0.001916 / -0.0007847 (15) | 0.06178 / 0.02328 (10) |
| cell10 | 0.8 | 25 | 0 | 0.06565 / 0.02634 (13) | 0.08018 / 0.07821 (10) | -0.09931 / -0.1299 (25) | 0.02179 / -0.05606 (17) | 0.0834 / 0.05588 (9) | -0.09983 / -0.1698 (23) | 0.1028 / 0.07124 (6) | 0.1469 / 0.128 (4) |
| cell11 | 0.8 | 25 | 0.8 | 0.2113 / 0.001902 (15) | 0.3963 / 0.2005 (13) | 0.2127 / 0.01706 (14) | 0.112 / -0.01483 (16) | 0.2023 / 0.0695 (14) | 0.05204 / 0.003822 (13) | 0.01403 / -0.006118 (15) | 0.3356 / 0.1235 (11) |
| cell12 | 0.95 | 1 | 0 | 0.0009938 / 0.000171 (12) | -0.000329 / -0.0005836 (18) | 0.0009626 / 8.2e-05 (14) | 6.32e-06 / -0.0002607 (16) | 1.3e-05 / -0.0002567 (16) | 6.117e-06 / -0.0002607 (16) | 0.0007557 / 0.0004454 (13) | 0.001699 / 0.0005553 (6) |
| cell13 | 0.95 | 1 | 0.8 | -0.006851 / -0.004259 (26) | 0.0008475 / -0.004255 (23) | 0.002994 / -0.003729 (23) | -4.634e-05 / -0.0003438 (21) | -0.000188 / -0.0003438 (21) | -0.000137 / -0.0003438 (21) | 0.0009248 / -0.0002973 (21) | 0.005671 / -0.000297 (18) |
| cell14 | 0.95 | 5 | 0 | 0.003392 / 0.0009979 (13) | -0.00397 / -0.002231 (24) | 0.002767 / 0.001179 (14) | 0.003279 / -4.124e-05 (15) | 0.00297 / -7.927e-05 (15) | 0.003368 / -3.94e-05 (15) | -0.001134 / -0.0008753 (19) | 0.003572 / 0.0006593 (13) |
| cell15 | 0.95 | 5 | 0.8 | -0.03541 / -0.004362 (26) | -0.009553 / -0.004255 (23) | -0.002144 / -0.004255 (21) | 0.005686 / -0.0003438 (18) | 0.01027 / -0.0003438 (18) | 0.01521 / -0.0003438 (17) | 0.001204 / -0.0002973 (20) | 0.02054 / -0.0002973 (18) |
| cell16 | 0.95 | 25 | 0 | -0.003533 / -0.005088 (18) | -0.04263 / -0.03092 (27) | -0.0209 / -0.02181 (21) | 0.001167 / -0.00628 (16) | 0.004303 / -0.0009478 (15) | 0.003085 / -0.005272 (16) | -0.01029 / -0.008905 (18) | 0.01338 / -0.0006441 (15) |
| cell17 | 0.95 | 25 | 0.8 | -0.1369 / -0.004556 (23) | -0.05853 / -0.004333 (23) | -0.0324 / -0.004255 (20) | 0.07715 / -0.0003435 (17) | 0.07971 / -0.0003436 (18) | 0.1007 / -3.584e-05 (15) | 0.00939 / -0.0002973 (19) | 0.1163 / -0.000297 (17) |

### The grid: the TSB sensitivities, QScore9 (compact cells)

| Group | h | Reference | `tsb_hurdle_a005` | `tsb_hurdle` | `tsb_hurdle_a020` |
|---|---|---|---|---|---|
| all (n = 30) | 7 | `chronos2_completed` | 0.06484 / 0.07422 (12 / 0 / 18) | 0.112 / 0.09471 (7 / 0 / 23) | 0.152 / 0.1201 (6 / 0 / 24) |
| all (n = 30) | 7 | `timesfm3_completed` | 0.08251 / 0.07704 (8 / 0 / 22) | 0.1297 / 0.1418 (7 / 0 / 23) | 0.1697 / 0.1545 (4 / 0 / 26) |
| all (n = 30) | 7 | `timesfm2p5_completed` | 0.04183 / 0.02105 (10 / 0 / 20) | 0.08904 / 0.06711 (9 / 0 / 21) | 0.129 / 0.09156 (5 / 0 / 25) |
| all (n = 30) | 7 | `chronos2_hurdle` | -0.1327 / -0.1053 (24 / 0 / 6) | -0.08549 / -0.04979 (18 / 0 / 12) | -0.04553 / -0.006996 (16 / 0 / 14) |
| all (n = 30) | 7 | `timesfm3_hurdle` | -0.1112 / -0.08307 (24 / 0 / 6) | -0.06399 / -0.03457 (17 / 0 / 13) | -0.02403 / 0.002205 (15 / 0 / 15) |
| all (n = 30) | 7 | `timesfm2p5_hurdle` | -0.1464 / -0.1027 (24 / 0 / 6) | -0.09923 / -0.06646 (21 / 0 / 9) | -0.05927 / -0.01446 (16 / 0 / 14) |
| all (n = 30) | 7 | `hurdle_count_28` | -0.06722 / -0.0776 (22 / 0 / 8) | -0.02001 / 0.0006173 (15 / 0 / 15) | 0.01995 / 0.0127 (15 / 0 / 15) |
| all (n = 30) | 7 | `dynamic_count` | 0.03976 / 0.04536 (9 / 0 / 21) | 0.08696 / 0.09588 (7 / 0 / 23) | 0.1269 / 0.1217 (7 / 0 / 23) |
| all (n = 30) | 30 | `chronos2_completed` | -0.00807 / 0.009335 (14 / 0 / 16) | 0.08545 / 0.0835 (7 / 0 / 23) | 0.1974 / 0.1754 (6 / 0 / 24) |
| all (n = 30) | 30 | `timesfm3_completed` | 0.02317 / 0.0171 (13 / 0 / 17) | 0.1167 / 0.09576 (6 / 0 / 24) | 0.2287 / 0.1995 (4 / 0 / 26) |
| all (n = 30) | 30 | `timesfm2p5_completed` | -0.01535 / -0.008903 (16 / 0 / 14) | 0.07817 / 0.05822 (8 / 0 / 22) | 0.1902 / 0.1724 (4 / 0 / 26) |
| all (n = 30) | 30 | `chronos2_hurdle` | -0.09406 / -0.0916 (26 / 0 / 4) | -0.0005464 / 0.006667 (14 / 0 / 16) | 0.1114 / 0.09736 (8 / 0 / 22) |
| all (n = 30) | 30 | `timesfm3_hurdle` | -0.06345 / -0.06357 (25 / 0 / 5) | 0.03006 / 0.01596 (13 / 0 / 17) | 0.1421 / 0.134 (7 / 0 / 23) |
| all (n = 30) | 30 | `timesfm2p5_hurdle` | -0.103 / -0.1194 (26 / 0 / 4) | -0.009523 / -0.01327 (18 / 0 / 12) | 0.1025 / 0.09091 (8 / 0 / 22) |
| all (n = 30) | 30 | `hurdle_count_28` | -0.04195 / -0.02428 (20 / 0 / 10) | 0.05156 / 0.0216 (11 / 0 / 19) | 0.1636 / 0.1206 (6 / 0 / 24) |
| all (n = 30) | 30 | `dynamic_count` | 0.05564 / 0.03971 (6 / 0 / 24) | 0.1492 / 0.09122 (2 / 0 / 28) | 0.2611 / 0.1823 (2 / 0 / 28) |

### The grid: the fourth cell, four scores (full cells)

| Group | h | Variant | Reference | Source | QScore9 | Context-scaled QScore9 | Occurrence Brier | Discrete CRPS |
|---|---|---|---|---|---|---|---|---|
| all (n = 30) | 7 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | post hoc | 0.01637 [-0.03035, 0.0603]; median 0.03013; 10 / 0 / 20; p 0.254 | 0.005826 [-0.002907, 0.01491]; median 0.004821; 12 / 0 / 18; p 0.213 | 0 [0, 0]; median 0; 0 / 30 / 0; p 1 | 0.02002 [-0.03034, 0.06683]; median 0.04003; 11 / 0 / 19; p 0.229 |
| all (n = 30) | 7 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -0.1157 [-0.2116, -0.0223]; median -0.08175; 18 / 0 / 12; p 0.0387 | -0.03044 [-0.05612, -0.006459]; median -0.01105; 18 / 0 / 12; p 0.0519 | -0.01107 [-0.02014, -0.001915]; median -0.00964; 19 / 0 / 11; p 0.035 | -0.09315 [-0.1805, -0.008335]; median -0.06726; 18 / 0 / 12; p 0.0627 |
| all (n = 30) | 7 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | post hoc | 0.03233 [-0.01333, 0.07641]; median 0.05726; 11 / 0 / 19; p 0.141 | 0.01261 [0.003477, 0.02181]; median 0.01081; 10 / 0 / 20; p 0.0243 | 0 [0, 0]; median 0; 0 / 30 / 0; p 1 | 0.04382 [-0.004299, 0.08932]; median 0.06841; 11 / 0 / 19; p 0.0449 |
| all (n = 30) | 7 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -0.1174 [-0.2128, -0.02543]; median -0.129; 21 / 0 / 9; p 0.0256 | -0.02828 [-0.05307, -0.004562]; median -0.01766; 19 / 0 / 11; p 0.0752 | -0.01195 [-0.02062, -0.003384]; median -0.01391; 23 / 0 / 7; p 0.0207 | -0.08875 [-0.1757, -0.004858]; median -0.0897; 21 / 0 / 9; p 0.0519 |
| all (n = 30) | 7 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | post hoc | 0.09894 [0.0267, 0.1686]; median 0.1027; 9 / 0 / 21; p 0.00927 | 0.0341 [0.01931, 0.04944]; median 0.03243; 6 / 0 / 24; p 0.000453 | 0 [0, 0]; median 0; 0 / 30 / 0; p 1 | 0.1018 [0.0293, 0.1739]; median 0.111; 9 / 0 / 21; p 0.00773 |
| all (n = 30) | 7 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -0.01011 [-0.1168, 0.09004]; median 0.002028; 15 / 0 / 15; p 0.975 | 0.0005599 [-0.02545, 0.02543]; median 0.01735; 13 / 0 / 17; p 0.704 | -0.005602 [-0.01509, 0.003784]; median -0.007672; 19 / 0 / 11; p 0.229 | 0.01077 [-0.08366, 0.1051]; median 0.01582; 13 / 0 / 17; p 0.658 |
| all (n = 30) | 30 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | post hoc | 0.04554 [0.01637, 0.07505]; median 0.04903; 9 / 0 / 21; p 0.0104 | 0.007874 [-0.00147, 0.01703]; median 0.01018; 7 / 0 / 23; p 0.0859 | 0 [0, 0]; median 0; 0 / 30 / 0; p 1 | 0.05485 [0.02234, 0.08714]; median 0.0631; 8 / 0 / 22; p 0.00499 |
| all (n = 30) | 30 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | post hoc | 0.01166 [-0.05014, 0.07156]; median 0.03877; 10 / 0 / 20; p 0.339 | 0.006106 [-0.008106, 0.02128]; median -0.003697; 16 / 0 / 14; p 0.491 | 0.0003448 [-0.005871, 0.006536]; median 0.0007453; 15 / 0 / 15; p 0.877 | 0.03003 [-0.02659, 0.08199]; median 0.05742; 11 / 0 / 19; p 0.131 |
| all (n = 30) | 30 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | post hoc | 0.05877 [0.03058, 0.08652]; median 0.05831; 5 / 0 / 25; p 0.000388 | 0.01469 [0.009389, 0.02036]; median 0.01214; 3 / 0 / 27; p 2.84e-05 | 0 [0, 0]; median 0; 0 / 30 / 0; p 1 | 0.07683 [0.04793, 0.1051]; median 0.07711; 4 / 0 / 26; p 0.000174 |
| all (n = 30) | 30 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | post hoc | -0.006356 [-0.0675, 0.0464]; median 0.0146; 13 / 0 / 17; p 0.719 | 0.003621 [-0.01193, 0.02178]; median 0.004829; 12 / 0 / 18; p 0.453 | -0.002665 [-0.008654, 0.002578]; median 0.001756; 13 / 0 / 17; p 0.644 | 0.01873 [-0.0371, 0.06978]; median 0.03187; 11 / 0 / 19; p 0.213 |
| all (n = 30) | 30 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | post hoc | 0.1462 [0.09638, 0.1964]; median 0.1371; 2 / 0 / 28; p 2.6e-05 | 0.04236 [0.03064, 0.05407]; median 0.04535; 3 / 0 / 27; p 1.02e-05 | 0 [0, 0]; median 0; 0 / 30 / 0; p 1 | 0.1553 [0.1072, 0.2035]; median 0.1468; 2 / 0 / 28; p 2.37e-05 |
| all (n = 30) | 30 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | post hoc | 0.1196 [0.05545, 0.1793]; median 0.1107; 7 / 0 / 23; p 0.000205 | 0.03626 [0.01922, 0.05609]; median 0.03302; 6 / 0 / 24; p 0.000283 | 0.004022 [-0.002172, 0.009516]; median 0.004827; 12 / 0 / 18; p 0.0719 | 0.1343 [0.07581, 0.1901]; median 0.1252; 5 / 0 / 25; p 7.51e-05 |

### The grid per cell: the fourth cell, qscore9, h = 7

Each entry: mean difference / median difference (series lower, of 30).

| Cell (n = 30) | Zero probability | Positive mean | Persistence | `chronos2_occurrence_model_size_count` vs `chronos2_completed` | `chronos2_occurrence_model_size_count` vs `hurdle_count_28` | `timesfm3_occurrence_model_size_count` vs `timesfm3_completed` | `timesfm3_occurrence_model_size_count` vs `hurdle_count_28` | `timesfm2p5_occurrence_model_size_count` vs `timesfm2p5_completed` | `timesfm2p5_occurrence_model_size_count` vs `hurdle_count_28` |
|---|---|---|---|---|---|---|---|---|---|
| cell00 | 0.2 | 1 | 0 | 0 / 0 (0) | -0.00194 / 0.001587 (11) | 0 / 0 (0) | 0.003175 / 0 (10) | 0 / 0 (0) | 0.001728 / 0.002646 (13) |
| cell01 | 0.2 | 1 | 0.8 | 0 / 0 (0) | -0.03802 / -0.01852 (19) | 0 / 0 (0) | -0.04303 / -0.03598 (21) | 0 / 0 (0) | -0.04247 / -0.0254 (19) |
| cell02 | 0.2 | 5 | 0 | 0.01108 / 0.007407 (13) | 0.005644 / -0.004762 (16) | 0.0134 / 0.02116 (12) | 0.004727 / -0.003704 (16) | 0.02219 / 0.03175 (10) | 0.008501 / 0.01958 (10) |
| cell03 | 0.2 | 5 | 0.8 | -0.02293 / -0.01746 (18) | -0.1783 / -0.08942 (22) | -0.03661 / -0.0127 (16) | -0.1949 / -0.1143 (23) | -0.05136 / -0.04709 (20) | -0.2214 / -0.07672 (21) |
| cell04 | 0.2 | 25 | 0 | 0.2357 / 0.3143 (7) | 0.267 / 0.2836 (8) | 0.1528 / 0.2323 (8) | 0.1498 / 0.1513 (10) | 0.2393 / 0.2862 (8) | 0.4281 / 0.4233 (7) |
| cell05 | 0.2 | 25 | 0.8 | -0.3735 / -0.1296 (20) | -1.294 / -0.655 (22) | -0.2428 / -0.1196 (20) | -1.243 / -0.7095 (23) | -0.4242 / -0.2169 (23) | -1.277 / -0.5291 (24) |
| cell06 | 0.8 | 1 | 0 | -0.0001058 / 0 (3) | -0.000776 / -0.0005291 (15) | 0 / 0 (0) | -0.002504 / 0 (11) | 0 / 0 (0) | 0.01009 / 0.01376 (10) |
| cell07 | 0.8 | 1 | 0.8 | -0.0001411 / 0 (3) | -0.0491 / -0.01481 (19) | -0.0001058 / 0 (2) | -0.05344 / -0.02646 (23) | -0.0001058 / 0 (2) | -0.04758 / -0.02963 (21) |
| cell08 | 0.8 | 5 | 0 | 0.003704 / -0.001058 (15) | -0.004021 / -0.001058 (15) | 0.02469 / 0.02011 (9) | 0.01996 / 0.01958 (9) | 0.03453 / 0.03175 (12) | 0.05425 / 0.05661 (8) |
| cell09 | 0.8 | 5 | 0.8 | 0.003915 / 0.001058 (12) | -0.1744 / -0.04815 (18) | 0.0128 / 0 (12) | -0.1647 / -0.03492 (17) | 0.007125 / 0.01323 (11) | -0.1821 / -0.07566 (19) |
| cell10 | 0.8 | 25 | 0 | 0.2226 / 0.1921 (12) | 0.2261 / 0.2608 (7) | 0.3403 / 0.2804 (8) | 0.3194 / 0.245 (9) | 1.102 / 0.9836 (3) | 1.332 / 1.207 (2) |
| cell11 | 0.8 | 25 | 0.8 | 0.2371 / 0.2688 (8) | -0.7379 / -0.218 (17) | 0.247 / 0.2825 (10) | -0.7787 / -0.2762 (18) | 0.648 / 0.7238 (7) | -0.3144 / 0.2016 (13) |
| cell12 | 0.95 | 1 | 0 | 0 / 0 (0) | -0.001058 / 0 (6) | 0 / 0 (0) | -0.0004233 / 0 (6) | 0 / 0 (0) | -0.001058 / 0 (6) |
| cell13 | 0.95 | 1 | 0.8 | -0.0001058 / 0 (2) | -0.003422 / 0 (8) | 0 / 0 (0) | -0.006631 / 0 (8) | 0 / 0 (0) | -0.004797 / 0 (8) |
| cell14 | 0.95 | 5 | 0 | 0.002293 / 0 (0) | -0.0003175 / 0 (5) | 0.007125 / 0 (3) | 0.006667 / 0 (6) | 0.004021 / 0 (0) | 0.0002469 / 0 (6) |
| cell15 | 0.95 | 5 | 0.8 | -0.01164 / 0 (5) | -0.0254 / 0 (7) | 0.00381 / 0 (3) | -0.03496 / 0 (8) | -0.004374 / 0 (4) | -0.02751 / 0 (9) |
| cell16 | 0.95 | 25 | 0 | 0.02586 / 0 (3) | 0.003704 / 0 (4) | 0.083 / 0.08148 (3) | 0.08723 / 0.02963 (4) | 0.2546 / 0.172 (3) | 0.2491 / 0.1587 (2) |
| cell17 | 0.95 | 25 | 0.8 | -0.03915 / 0 (6) | -0.07559 / 0 (7) | -0.02339 / 0 (7) | -0.1814 / 0 (10) | -0.05069 / 0 (4) | -0.147 / 0 (9) |

### The grid per cell: the fourth cell, qscore9, h = 30

Each entry: mean difference / median difference (series lower, of 30).

| Cell (n = 30) | Zero probability | Positive mean | Persistence | `chronos2_occurrence_model_size_count` vs `chronos2_completed` | `chronos2_occurrence_model_size_count` vs `hurdle_count_28` | `timesfm3_occurrence_model_size_count` vs `timesfm3_completed` | `timesfm3_occurrence_model_size_count` vs `hurdle_count_28` | `timesfm2p5_occurrence_model_size_count` vs `timesfm2p5_completed` | `timesfm2p5_occurrence_model_size_count` vs `hurdle_count_28` |
|---|---|---|---|---|---|---|---|---|---|
| cell00 | 0.2 | 1 | 0 | 0 / 0 (0) | -0.001276 / 0 (13) | 0 / 0 (0) | 0.0008477 / 0 (11) | 0 / 0 (0) | -1.85e-18 / 0.001111 (14) |
| cell01 | 0.2 | 1 | 0.8 | 0 / 0 (0) | -0.01684 / -0.01321 (18) | 0 / 0 (0) | -0.02913 / -0.006296 (21) | 0 / 0 (0) | -0.02891 / -0.008889 (17) |
| cell02 | 0.2 | 5 | 0 | 0.02024 / 0.007778 (12) | 0.01507 / 0.004938 (14) | 0.01473 / 0.0184 (10) | 0.0005185 / -0.0004938 (15) | 0.02053 / 0.0142 (10) | 0.01037 / 0.004198 (12) |
| cell03 | 0.2 | 5 | 0.8 | -0.009095 / 0.001728 (14) | -0.09004 / -0.0537 (17) | -0.01678 / -0.01951 (18) | -0.1188 / -0.06185 (19) | -0.01022 / -0.02222 (17) | -0.1388 / -0.08062 (19) |
| cell04 | 0.2 | 25 | 0 | 0.3224 / 0.2472 (1) | 0.3721 / 0.2469 (2) | 0.1958 / 0.1537 (8) | 0.1824 / 0.2104 (11) | 0.3653 / 0.3689 (2) | 0.4992 / 0.4335 (1) |
| cell05 | 0.2 | 25 | 0.8 | -0.1789 / -0.05852 (16) | -0.6232 / -0.207 (18) | -0.02844 / -0.006049 (15) | -0.6544 / -0.09 (16) | -0.1683 / -0.05444 (17) | -0.5759 / -0.2269 (19) |
| cell06 | 0.8 | 1 | 0 | -9.877e-05 / 0 (5) | -0.0001728 / -0.0003704 (16) | 0 / 0 (0) | -0.001531 / 0 (13) | 0 / 0 (0) | 0.002354 / 0.001852 (13) |
| cell07 | 0.8 | 1 | 0.8 | -0.0001235 / 0 (9) | -0.007901 / 0.003827 (13) | -2.469e-05 / 0 (2) | -0.02454 / -0.004074 (16) | -2.469e-05 / 0 (2) | -0.01611 / -0.008765 (17) |
| cell08 | 0.8 | 5 | 0 | 0.002609 / 0.003086 (12) | -0.001695 / -0.001852 (16) | 0.02351 / 0.02296 (5) | 0.02611 / 0.02148 (7) | 0.04645 / 0.05 (5) | 0.06802 / 0.06642 (3) |
| cell09 | 0.8 | 5 | 0.8 | 0.001136 / 0.01272 (9) | -0.02864 / 0.01062 (14) | 0.02174 / 0.01728 (11) | -0.04694 / 0.0121 (13) | 0.03776 / 0.04049 (11) | -0.01062 / 0.009753 (13) |
| cell10 | 0.8 | 25 | 0 | 0.233 / 0.2038 (7) | 0.247 / 0.2021 (7) | 0.2261 / 0.1749 (1) | 0.2299 / 0.1756 (3) | 1.151 / 1.183 (0) | 1.359 / 1.346 (0) |
| cell11 | 0.8 | 25 | 0.8 | 0.4161 / 0.5443 (6) | 0.1607 / 0.2443 (11) | 0.5633 / 0.402 (7) | 0.1583 / 0.1528 (11) | 0.8256 / 1.035 (8) | 0.5826 / 0.7684 (11) |
| cell12 | 0.95 | 1 | 0 | -8.23e-06 / 0 (1) | -0.001383 / 0 (8) | 0 / 0 (0) | 0.0002305 / 0 (5) | 0 / 0 (0) | -0.001481 / 0 (8) |
| cell13 | 0.95 | 1 | 0.8 | -7.407e-05 / 0 (4) | 0.007152 / 0 (6) | -5.761e-05 / 0 (1) | -0.001226 / 0 (8) | 0 / 0 (0) | -0.003695 / 0 (8) |
| cell14 | 0.95 | 5 | 0 | 0.002198 / 0 (0) | -0.002502 / 0 (5) | 0.007514 / 0.001975 (3) | 0.01094 / 0.009383 (1) | 0.004864 / 0 (0) | 0.001317 / 0 (3) |
| cell15 | 0.95 | 5 | 0.8 | -0.01958 / 0 (8) | 0.01814 / 0 (6) | 0.001794 / 0 (4) | 0.01213 / 0 (8) | 0.007317 / 0 (3) | 0.01122 / 0 (8) |
| cell16 | 0.95 | 25 | 0 | 0.0492 / 0.005679 (4) | 0.02243 / 0.002716 (4) | 0.05432 / 0.04099 (9) | 0.07862 / 0.03173 (1) | 0.2758 / 0.253 (4) | 0.2723 / 0.2315 (0) |
| cell17 | 0.95 | 25 | 0.8 | -0.01936 / 0 (10) | 0.1409 / 0 (6) | -0.005679 / 0 (11) | 0.06212 / 0 (9) | 0.07545 / 0 (4) | 0.1214 / 0 (4) |

### The grid: the point methods, QScore9 (compact cells)

A point mass is a poor probabilistic forecast by construction. Under it QScore9 is the absolute error of the rounded point, so these rows say how the field's point methods fare under this score, not how good they are as point forecasts.

| Group | h | Reference | `croston_classic` | `croston_sba` | `adida` |
|---|---|---|---|---|---|
| all (n = 30) | 7 | `chronos2_completed` | 1.041 / 0.9494 (0 / 0 / 30) | 1.042 / 0.9436 (0 / 0 / 30) | 0.8581 / 0.8108 (0 / 0 / 30) |
| all (n = 30) | 7 | `timesfm3_completed` | 1.059 / 1.012 (0 / 0 / 30) | 1.059 / 0.957 (0 / 0 / 30) | 0.8758 / 0.8519 (0 / 0 / 30) |
| all (n = 30) | 7 | `timesfm2p5_completed` | 1.018 / 0.9397 (0 / 0 / 30) | 1.019 / 0.9628 (0 / 0 / 30) | 0.8351 / 0.7898 (0 / 0 / 30) |
| all (n = 30) | 7 | `hurdle_count_28` | 0.9093 / 0.8773 (0 / 0 / 30) | 0.9098 / 0.917 (0 / 0 / 30) | 0.7261 / 0.7085 (0 / 0 / 30) |
| all (n = 30) | 7 | `dynamic_count` | 1.016 / 0.9565 (0 / 0 / 30) | 1.017 / 0.9827 (0 / 0 / 30) | 0.833 / 0.8088 (0 / 0 / 30) |
| all (n = 30) | 7 | `tsb_hurdle` | 0.9293 / 0.8817 (0 / 0 / 30) | 0.9298 / 0.9016 (0 / 0 / 30) | 0.7461 / 0.7114 (0 / 0 / 30) |
| all (n = 30) | 30 | `chronos2_completed` | 0.9016 / 0.8555 (0 / 0 / 30) | 0.9009 / 0.8767 (0 / 0 / 30) | 0.8499 / 0.8309 (0 / 0 / 30) |
| all (n = 30) | 30 | `timesfm3_completed` | 0.9328 / 0.8596 (0 / 0 / 30) | 0.9322 / 0.8944 (0 / 0 / 30) | 0.8811 / 0.8495 (0 / 0 / 30) |
| all (n = 30) | 30 | `timesfm2p5_completed` | 0.8943 / 0.8359 (0 / 0 / 30) | 0.8936 / 0.8464 (0 / 0 / 30) | 0.8426 / 0.8185 (0 / 0 / 30) |
| all (n = 30) | 30 | `hurdle_count_28` | 0.8677 / 0.8484 (0 / 0 / 30) | 0.867 / 0.8516 (0 / 0 / 30) | 0.816 / 0.802 (0 / 0 / 30) |
| all (n = 30) | 30 | `dynamic_count` | 0.9653 / 0.9357 (0 / 0 / 30) | 0.9646 / 0.9307 (0 / 0 / 30) | 0.9136 / 0.8813 (0 / 0 / 30) |
| all (n = 30) | 30 | `tsb_hurdle` | 0.8161 / 0.7977 (0 / 0 / 30) | 0.8155 / 0.7933 (0 / 0 / 30) | 0.7644 / 0.762 (0 / 0 / 30) |

### The grid: occurrence descriptors

| Group | h | Windows | All-zero contexts | Positive target days | TSB p (0.05 / 0.1 / 0.2) | Jeffreys p | `dynamic_count` p | Completed 1 − F(0) (chronos2 / timesfm3 / timesfm2p5) | Days with every decile at zero (chronos2 / timesfm3 / timesfm2p5) |
|---|---|---|---|---|---|---|---|---|---|
| all (n = 30) | 7 | 1620 | 57 | 0.361 | 0.338 / 0.336 / 0.337 | 0.346 | 0.334 | 0.402 / 0.405 / 0.430 | 0.386 / 0.332 / 0.366 |
| all (n = 30) | 30 | 1620 | 57 | 0.345 | 0.338 / 0.336 / 0.337 | 0.346 | 0.334 | 0.400 / 0.404 / 0.430 | 0.352 / 0.272 / 0.319 |
| cell00 (n = 30) | 7 | 90 | 0 | 0.819 | 0.794 / 0.785 / 0.772 | 0.791 | 0.798 | 0.833 / 0.769 / 0.855 | 0.000 / 0.000 / 0.000 |
| cell00 (n = 30) | 30 | 90 | 0 | 0.802 | 0.794 / 0.785 / 0.772 | 0.791 | 0.798 | 0.826 / 0.766 / 0.823 | 0.000 / 0.000 / 0.000 |
| cell01 (n = 30) | 7 | 90 | 0 | 0.851 | 0.783 / 0.784 / 0.792 | 0.779 | 0.778 | 0.808 / 0.774 / 0.816 | 0.035 / 0.030 / 0.065 |
| cell01 (n = 30) | 30 | 90 | 0 | 0.799 | 0.783 / 0.784 / 0.792 | 0.779 | 0.778 | 0.796 / 0.757 / 0.835 | 0.030 / 0.007 / 0.017 |
| cell02 (n = 30) | 7 | 90 | 0 | 0.819 | 0.794 / 0.785 / 0.772 | 0.791 | 0.798 | 0.878 / 0.837 / 0.866 | 0.000 / 0.000 / 0.000 |
| cell02 (n = 30) | 30 | 90 | 0 | 0.802 | 0.794 / 0.785 / 0.772 | 0.791 | 0.798 | 0.874 / 0.834 / 0.862 | 0.000 / 0.000 / 0.000 |
| cell03 (n = 30) | 7 | 90 | 0 | 0.851 | 0.783 / 0.784 / 0.792 | 0.779 | 0.778 | 0.851 / 0.858 / 0.890 | 0.014 / 0.014 / 0.000 |
| cell03 (n = 30) | 30 | 90 | 0 | 0.799 | 0.783 / 0.784 / 0.792 | 0.779 | 0.778 | 0.847 / 0.856 / 0.894 | 0.011 / 0.003 / 0.000 |
| cell04 (n = 30) | 7 | 90 | 0 | 0.819 | 0.794 / 0.785 / 0.772 | 0.791 | 0.798 | 0.954 / 0.920 / 0.985 | 0.000 / 0.000 / 0.000 |
| cell04 (n = 30) | 30 | 90 | 0 | 0.802 | 0.794 / 0.785 / 0.772 | 0.791 | 0.798 | 0.954 / 0.912 / 0.977 | 0.000 / 0.000 / 0.000 |
| cell05 (n = 30) | 7 | 90 | 0 | 0.851 | 0.783 / 0.784 / 0.792 | 0.779 | 0.778 | 0.900 / 0.918 / 0.943 | 0.011 / 0.000 / 0.000 |
| cell05 (n = 30) | 30 | 90 | 0 | 0.799 | 0.783 / 0.784 / 0.792 | 0.779 | 0.778 | 0.900 / 0.915 / 0.959 | 0.010 / 0.000 / 0.000 |
| cell06 (n = 30) | 7 | 90 | 0 | 0.203 | 0.194 / 0.194 / 0.197 | 0.206 | 0.192 | 0.163 / 0.211 / 0.137 | 0.108 / 0.000 / 0.432 |
| cell06 (n = 30) | 30 | 90 | 0 | 0.196 | 0.194 / 0.194 / 0.197 | 0.206 | 0.192 | 0.169 / 0.214 / 0.164 | 0.058 / 0.000 / 0.179 |
| cell07 (n = 30) | 7 | 90 | 0 | 0.208 | 0.180 / 0.181 / 0.185 | 0.193 | 0.156 | 0.210 / 0.217 / 0.180 | 0.605 / 0.478 / 0.767 |
| cell07 (n = 30) | 30 | 90 | 0 | 0.194 | 0.180 / 0.181 / 0.185 | 0.193 | 0.156 | 0.200 / 0.214 / 0.142 | 0.489 / 0.183 / 0.673 |
| cell08 (n = 30) | 7 | 90 | 0 | 0.203 | 0.194 / 0.194 / 0.197 | 0.206 | 0.192 | 0.230 / 0.282 / 0.320 | 0.000 / 0.000 / 0.000 |
| cell08 (n = 30) | 30 | 90 | 0 | 0.196 | 0.194 / 0.194 / 0.197 | 0.206 | 0.192 | 0.232 / 0.282 / 0.327 | 0.000 / 0.000 / 0.000 |
| cell09 (n = 30) | 7 | 90 | 0 | 0.208 | 0.180 / 0.181 / 0.185 | 0.193 | 0.156 | 0.253 / 0.265 / 0.291 | 0.419 / 0.292 / 0.292 |
| cell09 (n = 30) | 30 | 90 | 0 | 0.194 | 0.180 / 0.181 / 0.185 | 0.193 | 0.156 | 0.251 / 0.263 / 0.294 | 0.271 / 0.163 / 0.124 |
| cell10 (n = 30) | 7 | 90 | 0 | 0.203 | 0.194 / 0.194 / 0.197 | 0.206 | 0.192 | 0.304 / 0.329 / 0.449 | 0.000 / 0.000 / 0.000 |
| cell10 (n = 30) | 30 | 90 | 0 | 0.196 | 0.194 / 0.194 / 0.197 | 0.206 | 0.192 | 0.303 / 0.321 / 0.447 | 0.000 / 0.000 / 0.000 |
| cell11 (n = 30) | 7 | 90 | 0 | 0.208 | 0.180 / 0.181 / 0.185 | 0.193 | 0.156 | 0.321 / 0.346 / 0.420 | 0.286 / 0.165 / 0.054 |
| cell11 (n = 30) | 30 | 90 | 0 | 0.194 | 0.180 / 0.181 / 0.185 | 0.193 | 0.156 | 0.318 / 0.341 / 0.422 | 0.193 / 0.076 / 0.033 |
| cell12 (n = 30) | 7 | 90 | 0 | 0.043 | 0.046 / 0.046 / 0.048 | 0.060 | 0.048 | 0.062 / 0.069 / 0.063 | 1.000 / 0.940 / 1.000 |
| cell12 (n = 30) | 30 | 90 | 0 | 0.046 | 0.046 / 0.046 / 0.048 | 0.060 | 0.048 | 0.062 / 0.075 / 0.064 | 0.999 / 0.879 / 1.000 |
| cell13 (n = 30) | 7 | 90 | 19 | 0.043 | 0.032 / 0.028 / 0.027 | 0.048 | 0.034 | 0.095 / 0.087 / 0.087 | 0.910 / 0.963 / 0.959 |
| cell13 (n = 30) | 30 | 90 | 19 | 0.032 | 0.032 / 0.028 / 0.027 | 0.048 | 0.034 | 0.089 / 0.080 / 0.073 | 0.926 / 0.919 / 0.976 |
| cell14 (n = 30) | 7 | 90 | 0 | 0.043 | 0.046 / 0.046 / 0.048 | 0.060 | 0.048 | 0.067 / 0.090 / 0.076 | 0.959 / 0.730 / 0.941 |
| cell14 (n = 30) | 30 | 90 | 0 | 0.046 | 0.046 / 0.046 / 0.048 | 0.060 | 0.048 | 0.068 / 0.105 / 0.083 | 0.961 / 0.600 / 0.862 |
| cell15 (n = 30) | 7 | 90 | 19 | 0.043 | 0.032 / 0.028 / 0.027 | 0.048 | 0.034 | 0.104 / 0.093 / 0.099 | 0.870 / 0.921 / 0.933 |
| cell15 (n = 30) | 30 | 90 | 19 | 0.032 | 0.032 / 0.028 / 0.027 | 0.048 | 0.034 | 0.107 / 0.093 / 0.092 | 0.824 / 0.858 / 0.891 |
| cell16 (n = 30) | 7 | 90 | 0 | 0.043 | 0.046 / 0.046 / 0.048 | 0.060 | 0.048 | 0.080 / 0.116 / 0.154 | 0.879 / 0.563 / 0.300 |
| cell16 (n = 30) | 30 | 90 | 0 | 0.046 | 0.046 / 0.046 / 0.048 | 0.060 | 0.048 | 0.087 / 0.135 / 0.169 | 0.809 / 0.423 / 0.203 |
| cell17 (n = 30) | 7 | 90 | 19 | 0.043 | 0.032 / 0.028 / 0.027 | 0.048 | 0.034 | 0.120 / 0.104 / 0.115 | 0.851 / 0.875 / 0.849 |
| cell17 (n = 30) | 30 | 90 | 19 | 0.032 | 0.032 / 0.028 / 0.027 | 0.048 | 0.034 | 0.122 / 0.107 / 0.115 | 0.762 / 0.789 / 0.785 |

## NYC 311

300 series: 100 per stratum. Entities are series. The fourth-cell rows marked "run's own" are the run's registered secondaries, read from its files.

### NYC 311: `tsb_hurdle` against every reference, four scores (full cells)

| Group | h | Reference | QScore9 | Context-scaled QScore9 | Occurrence Brier | Discrete CRPS |
|---|---|---|---|---|---|---|
| all (n = 300) | 7 | `chronos2_completed` | 0.1058 [0.046, 0.1986]; median 0; 74 / 79 / 147; p 1.95e-10 | 0.02298 [0.01609, 0.03053]; median 0; 75 / 79 / 146; p 9.84e-11 | 0.002643 [0.0004129, 0.00491]; median -0.0003052; 162 / 0 / 138; p 0.301 | 0.1016 [0.04409, 0.1932]; median 0.003383; 129 / 0 / 171; p 1.92e-08 |
| all (n = 300) | 7 | `timesfm3_completed` | 0.1087 [0.04804, 0.2055]; median 0.001058; 64 / 84 / 152; p 9.92e-14 | 0.02406 [0.01748, 0.03143]; median 0.001058; 64 / 84 / 152; p 1.26e-14 | 0.002856 [0.0007808, 0.00488]; median -1.582e-05; 155 / 0 / 145; p 0.0301 | 0.104 [0.04612, 0.1954]; median 0.003194; 125 / 0 / 175; p 6.78e-09 |
| all (n = 300) | 7 | `timesfm2p5_completed` | 0.1075 [0.04748, 0.2018]; median 0; 78 / 79 / 143; p 8.22e-10 | 0.02193 [0.015, 0.02967]; median 0; 78 / 79 / 143; p 6.67e-10 | 0.0019 [-0.0002395, 0.004091]; median -0.0003187; 164 / 0 / 136; p 0.47 | 0.1034 [0.04589, 0.1963]; median 0.001972; 135 / 0 / 165; p 1.84e-07 |
| all (n = 300) | 7 | `chronos2_hurdle` | 0.09647 [0.03793, 0.1908]; median 0; 87 / 77 / 136; p 4.87e-07 | 0.01724 [0.01106, 0.02406]; median 0; 87 / 77 / 136; p 1.16e-06 | -0.001407 [-0.003334, 0.0004305]; median -0.0002973; 180 / 0 / 120; p 0.3 | 0.09224 [0.03604, 0.1833]; median -0.0003312; 153 / 0 / 147; p 0.000455 |
| all (n = 300) | 7 | `timesfm3_hurdle` | 0.09842 [0.03944, 0.1931]; median 0; 79 / 80 / 141; p 1.57e-08 | 0.01834 [0.01222, 0.02529]; median 0; 79 / 80 / 141; p 2.68e-08 | -0.001407 [-0.003296, 0.0004112]; median -0.0002973; 180 / 0 / 120; p 0.3 | 0.09501 [0.03801, 0.1858]; median -7.829e-05; 150 / 0 / 150; p 4.16e-05 |
| all (n = 300) | 7 | `timesfm2p5_hurdle` | 0.09949 [0.04067, 0.1927]; median 0; 74 / 82 / 144; p 1.78e-09 | 0.01819 [0.01198, 0.02508]; median 0; 74 / 82 / 144; p 3.74e-09 | -0.001407 [-0.003329, 0.0004312]; median -0.0002973; 180 / 0 / 120; p 0.3 | 0.09484 [0.03865, 0.1843]; median 6.509e-05; 149 / 0 / 151; p 1.75e-05 |
| all (n = 300) | 7 | `chronos2_hurdle_dynamic` | 0.09977 [0.0416, 0.1928]; median 0; 70 / 81 / 149; p 3.46e-11 | 0.0204 [0.014, 0.02737]; median 0; 70 / 81 / 149; p 6.87e-11 | -0.0003083 [-0.002794, 0.0021]; median -5.394e-06; 159 / 0 / 141; p 0.215 | 0.09478 [0.03829, 0.1845]; median 0.00194; 126 / 0 / 174; p 8.76e-09 |
| all (n = 300) | 7 | `timesfm3_hurdle_dynamic` | 0.1009 [0.04119, 0.1938]; median 0; 66 / 87 / 147; p 2.87e-11 | 0.02041 [0.01389, 0.02763]; median 0; 66 / 87 / 147; p 2.22e-11 | -0.0003083 [-0.002813, 0.002007]; median -5.394e-06; 159 / 0 / 141; p 0.215 | 0.09664 [0.03898, 0.1869]; median 0.001817; 130 / 0 / 170; p 9.15e-09 |
| all (n = 300) | 7 | `timesfm2p5_hurdle_dynamic` | 0.1011 [0.04272, 0.1943]; median 0; 67 / 86 / 147; p 5.23e-11 | 0.01971 [0.01331, 0.02698]; median 0; 67 / 86 / 147; p 4.05e-11 | -0.0003083 [-0.002803, 0.002098]; median -5.394e-06; 159 / 0 / 141; p 0.215 | 0.09615 [0.03968, 0.1873]; median 0.001809; 130 / 0 / 170; p 9.63e-09 |
| all (n = 300) | 7 | `hurdle_count_28` | -0.009012 [-0.02125, 0.001683]; median 0; 111 / 80 / 109; p 0.957 | -0.003352 [-0.007743, 0.0007705]; median 0; 111 / 80 / 109; p 0.827 | -0.001407 [-0.003344, 0.0004109]; median -0.0002973; 180 / 0 / 120; p 0.3 | -0.008165 [-0.01886, 0.002008]; median -0.0002973; 173 / 0 / 127; p 0.333 |
| all (n = 300) | 7 | `dynamic_count` | -0.003446 [-0.02361, 0.01566]; median 0; 91 / 87 / 122; p 0.0376 | 0.002571 [-0.003219, 0.008193]; median 0; 91 / 87 / 122; p 0.0199 | -0.0003083 [-0.002778, 0.002045]; median -5.394e-06; 159 / 0 / 141; p 0.215 | -0.004407 [-0.02314, 0.01332]; median -0.0002972; 155 / 0 / 145; p 0.0918 |
| all (n = 300) | 30 | `chronos2_completed` | 0.1146 [0.05829, 0.2005]; median 0.002346; 66 / 75 / 159; p 3.85e-15 | 0.02471 [0.01826, 0.03186]; median 0.002099; 66 / 75 / 159; p 4.15e-15 | 0.001596 [-0.0001942, 0.003315]; median -4.829e-05; 159 / 0 / 141; p 0.17 | 0.1093 [0.0552, 0.1929]; median 0.001826; 129 / 0 / 171; p 5.37e-10 |
| all (n = 300) | 30 | `timesfm3_completed` | 0.119 [0.06203, 0.2052]; median 0.005309; 51 / 75 / 174; p 5.35e-23 | 0.02748 [0.02132, 0.0345]; median 0.004815; 51 / 75 / 174; p 3.74e-23 | 0.002458 [0.0007227, 0.004137]; median 0.0006516; 135 / 0 / 165; p 9.45e-05 | 0.1132 [0.05767, 0.1983]; median 0.003376; 113 / 0 / 187; p 1.14e-14 |
| all (n = 300) | 30 | `timesfm2p5_completed` | 0.1157 [0.06113, 0.1972]; median 0.002469; 54 / 83 / 163; p 5.9e-19 | 0.02624 [0.01997, 0.03312]; median 0.002469; 54 / 83 / 163; p 5.87e-19 | 0.001866 [7.886e-05, 0.003578]; median 6.383e-05; 149 / 0 / 151; p 0.0143 | 0.1099 [0.0567, 0.1894]; median 0.003477; 114 / 0 / 186; p 4.12e-14 |
| all (n = 300) | 30 | `chronos2_hurdle` | 0.1056 [0.04989, 0.1902]; median 0; 74 / 81 / 145; p 7.38e-13 | 0.02071 [0.0147, 0.02737]; median 0; 74 / 81 / 145; p 3.14e-12 | -0.001058 [-0.002809, 0.0004952]; median -0.0002104; 156 / 0 / 144; p 0.283 | 0.1011 [0.04737, 0.183]; median 0.0007592; 132 / 0 / 168; p 2.84e-08 |
| all (n = 300) | 30 | `timesfm3_hurdle` | 0.1087 [0.053, 0.1943]; median 0.0004938; 64 / 85 / 151; p 1.03e-15 | 0.02205 [0.01611, 0.02865]; median 0.0001235; 65 / 85 / 150; p 5.3e-15 | -0.001058 [-0.002788, 0.0004978]; median -0.0002104; 156 / 0 / 144; p 0.283 | 0.1046 [0.05029, 0.1875]; median 0.001313; 125 / 0 / 175; p 8.78e-12 |
| all (n = 300) | 30 | `timesfm2p5_hurdle` | 0.1067 [0.05261, 0.1891]; median 0.002346; 62 / 84 / 154; p 4.72e-16 | 0.02194 [0.01605, 0.02855]; median 0.002346; 62 / 84 / 154; p 6.63e-16 | -0.001058 [-0.002815, 0.0005096]; median -0.0002104; 156 / 0 / 144; p 0.283 | 0.1016 [0.04946, 0.1818]; median 0.001394; 119 / 0 / 181; p 2.19e-12 |
| all (n = 300) | 30 | `chronos2_hurdle_dynamic` | 0.1099 [0.05422, 0.1942]; median 0.002469; 56 / 87 / 157; p 4.64e-17 | 0.02337 [0.01735, 0.03012]; median 0.002346; 56 / 87 / 157; p 3.87e-17 | -0.0004992 [-0.00286, 0.001657]; median 0.0003678; 133 / 0 / 167; p 0.000147 | 0.1047 [0.05106, 0.1873]; median 0.002508; 110 / 0 / 190; p 7.92e-15 |
| all (n = 300) | 30 | `timesfm3_hurdle_dynamic` | 0.1118 [0.05532, 0.1977]; median 0.002469; 38 / 99 / 163; p 2.26e-19 | 0.02367 [0.01754, 0.03055]; median 0.002469; 39 / 99 / 162; p 1.93e-19 | -0.0004992 [-0.002885, 0.001611]; median 0.0003678; 133 / 0 / 167; p 0.000147 | 0.1073 [0.05282, 0.1902]; median 0.002988; 106 / 0 / 194; p 1.74e-17 |
| all (n = 300) | 30 | `timesfm2p5_hurdle_dynamic` | 0.1092 [0.05546, 0.1926]; median 0.004074; 38 / 96 / 166; p 9.77e-20 | 0.02332 [0.01727, 0.0299]; median 0.002786; 38 / 96 / 166; p 8.76e-20 | -0.0004992 [-0.002849, 0.001622]; median 0.0003678; 133 / 0 / 167; p 0.000147 | 0.1038 [0.05125, 0.185]; median 0.003027; 102 / 0 / 198; p 9.53e-18 |
| all (n = 300) | 30 | `hurdle_count_28` | -0.005103 [-0.01559, 0.00456]; median 0; 100 / 85 / 115; p 0.349 | -0.002227 [-0.006036, 0.001346]; median 0; 100 / 85 / 115; p 0.256 | -0.001058 [-0.002794, 0.000503]; median -0.0002104; 156 / 0 / 144; p 0.283 | -0.004322 [-0.01405, 0.004581]; median 7.446e-05; 149 / 0 / 151; p 0.194 |
| all (n = 300) | 30 | `dynamic_count` | 0.006504 [-0.01297, 0.02321]; median 0; 60 / 101 / 139; p 2.18e-06 | 0.005902 [0.0004494, 0.01107]; median 0; 60 / 101 / 139; p 3.2e-07 | -0.0004992 [-0.002871, 0.001649]; median 0.0003678; 133 / 0 / 167; p 0.000147 | 0.004585 [-0.01382, 0.02061]; median 0.001406; 115 / 0 / 185; p 1.74e-07 |
| dense (n = 100) | 7 | `chronos2_completed` | 0.3103 [0.138, 0.5887]; median 0.08042; 20 / 0 / 80; p 3.17e-10 | 0.06168 [0.04446, 0.08102]; median 0.03153; 21 / 0 / 79; p 2.67e-11 | 0.005785 [0.001224, 0.01032]; median 0.002346; 44 / 0 / 56; p 0.0105 | 0.2993 [0.1342, 0.5723]; median 0.08834; 18 / 0 / 82; p 4.78e-11 |
| dense (n = 100) | 7 | `timesfm3_completed` | 0.3164 [0.1392, 0.5834]; median 0.1032; 19 / 0 / 81; p 4.21e-11 | 0.06257 [0.04546, 0.08222]; median 0.03334; 19 / 0 / 81; p 3.18e-12 | 0.004599 [-0.0004009, 0.009462]; median 0.001896; 47 / 0 / 53; p 0.0182 | 0.3047 [0.134, 0.5732]; median 0.1044; 20 / 0 / 80; p 3.15e-11 |
| dense (n = 100) | 7 | `timesfm2p5_completed` | 0.3197 [0.1475, 0.6033]; median 0.09365; 22 / 0 / 78; p 4.36e-11 | 0.06261 [0.04523, 0.08258]; median 0.03706; 22 / 0 / 78; p 5.7e-12 | 0.005336 [0.0006517, 0.009997]; median 0.001574; 44 / 0 / 56; p 0.01 | 0.307 [0.1404, 0.5729]; median 0.09286; 20 / 0 / 80; p 1.2e-11 |
| dense (n = 100) | 7 | `chronos2_hurdle` | 0.2889 [0.1176, 0.5595]; median 0.06984; 23 / 0 / 77; p 9.07e-09 | 0.05139 [0.03547, 0.06958]; median 0.03085; 23 / 0 / 77; p 1.93e-09 | -0.004497 [-0.009301, -0.0001584]; median -0.0002973; 58 / 0 / 42; p 0.511 | 0.2767 [0.1116, 0.5437]; median 0.06443; 23 / 0 / 77; p 4.29e-09 |
| dense (n = 100) | 7 | `timesfm3_hurdle` | 0.2918 [0.1169, 0.5672]; median 0.08836; 23 / 0 / 77; p 3.24e-09 | 0.05175 [0.03557, 0.0696]; median 0.0295; 23 / 0 / 77; p 8.76e-10 | -0.004497 [-0.00924, -0.0002427]; median -0.0002973; 58 / 0 / 42; p 0.511 | 0.2834 [0.1166, 0.5496]; median 0.08143; 22 / 0 / 78; p 9.76e-10 |
| dense (n = 100) | 7 | `timesfm2p5_hurdle` | 0.2948 [0.1241, 0.5717]; median 0.0873; 21 / 0 / 79; p 1.45e-09 | 0.0511 [0.03512, 0.069]; median 0.02699; 21 / 0 / 79; p 1.3e-09 | -0.004497 [-0.009273, -0.0001726]; median -0.0002973; 58 / 0 / 42; p 0.511 | 0.2829 [0.1184, 0.5455]; median 0.07508; 21 / 0 / 79; p 7.86e-10 |
| dense (n = 100) | 7 | `chronos2_hurdle_dynamic` | 0.2926 [0.1229, 0.5689]; median 0.08307; 17 / 0 / 83; p 8.85e-10 | 0.05474 [0.03885, 0.07266]; median 0.03406; 17 / 0 / 83; p 1.83e-10 | -0.003562 [-0.009368, 0.0018]; median 5.476e-07; 50 / 0 / 50; p 0.708 | 0.28 [0.1148, 0.5426]; median 0.08483; 19 / 0 / 81; p 8.57e-10 |
| dense (n = 100) | 7 | `timesfm3_hurdle_dynamic` | 0.2954 [0.1186, 0.5707]; median 0.09153; 22 / 0 / 78; p 1.44e-09 | 0.05432 [0.03779, 0.0731]; median 0.0336; 22 / 0 / 78; p 1.88e-10 | -0.003562 [-0.009427, 0.001791]; median 5.476e-07; 50 / 0 / 50; p 0.708 | 0.2856 [0.1169, 0.557]; median 0.08412; 22 / 0 / 78; p 4.17e-10 |
| dense (n = 100) | 7 | `timesfm2p5_hurdle_dynamic` | 0.2975 [0.1266, 0.5762]; median 0.08624; 22 / 0 / 78; p 6.19e-10 | 0.05348 [0.03701, 0.07217]; median 0.0305; 22 / 0 / 78; p 1.31e-10 | -0.003562 [-0.009419, 0.001824]; median 5.476e-07; 50 / 0 / 50; p 0.708 | 0.2849 [0.1186, 0.5496]; median 0.08603; 21 / 0 / 79; p 4.97e-10 |
| dense (n = 100) | 7 | `hurdle_count_28` | -0.02914 [-0.06413, 0.002254]; median -0.003175; 52 / 0 / 48; p 0.445 | -0.01199 [-0.0237, -0.001107]; median -0.0009692; 52 / 0 / 48; p 0.339 | -0.004497 [-0.009251, -0.0001986]; median -0.0002973; 58 / 0 / 42; p 0.511 | -0.02387 [-0.05527, 0.005845]; median -0.0006111; 51 / 0 / 49; p 0.375 |
| dense (n = 100) | 7 | `dynamic_count` | -0.01579 [-0.07531, 0.04141]; median 0.009524; 47 / 0 / 53; p 0.438 | 0.00242 [-0.0139, 0.01745]; median 0.001962; 47 / 0 / 53; p 0.325 | -0.003562 [-0.00941, 0.001783]; median 5.476e-07; 50 / 0 / 50; p 0.708 | -0.01623 [-0.07115, 0.03575]; median 0.01231; 45 / 0 / 55; p 0.492 |
| dense (n = 100) | 30 | `chronos2_completed` | 0.3387 [0.1778, 0.5877]; median 0.1219; 12 / 0 / 88; p 6.11e-15 | 0.06872 [0.05307, 0.08617]; median 0.05122; 12 / 0 / 88; p 3.17e-15 | 0.003496 [-0.0003535, 0.007188]; median 0.0005058; 48 / 0 / 52; p 0.0275 | 0.3242 [0.1685, 0.5678]; median 0.1179; 12 / 0 / 88; p 5.48e-15 |
| dense (n = 100) | 30 | `timesfm3_completed` | 0.3446 [0.1813, 0.5985]; median 0.1101; 11 / 0 / 89; p 2.84e-15 | 0.07023 [0.05508, 0.08706]; median 0.04944; 11 / 0 / 89; p 1.59e-15 | 0.002838 [-0.001771, 0.007104]; median 0.002506; 36 / 0 / 64; p 0.000176 | 0.3311 [0.1747, 0.5715]; median 0.1064; 10 / 0 / 90; p 1.63e-15 |
| dense (n = 100) | 30 | `timesfm2p5_completed` | 0.3401 [0.1853, 0.5823]; median 0.1074; 9 / 1 / 90; p 2.13e-15 | 0.07142 [0.05603, 0.08784]; median 0.0488; 9 / 1 / 90; p 6.12e-16 | 0.003351 [-0.001063, 0.007479]; median 0.002016; 40 / 0 / 60; p 0.000852 | 0.324 [0.1732, 0.5562]; median 0.1057; 10 / 0 / 90; p 1.38e-15 |
| dense (n = 100) | 30 | `chronos2_hurdle` | 0.3146 [0.1538, 0.56]; median 0.08272; 12 / 0 / 88; p 7.72e-14 | 0.06006 [0.04499, 0.07689]; median 0.04126; 12 / 0 / 88; p 3.42e-14 | -0.00413 [-0.008691, -3.341e-05]; median 0.0001057; 49 / 0 / 51; p 0.718 | 0.302 [0.1466, 0.5403]; median 0.077; 13 / 0 / 87; p 1e-13 |
| dense (n = 100) | 30 | `timesfm3_hurdle` | 0.3217 [0.1602, 0.5684]; median 0.07988; 12 / 0 / 88; p 3.33e-14 | 0.06181 [0.04686, 0.07878]; median 0.0422; 13 / 0 / 87; p 2.23e-14 | -0.00413 [-0.008763, -0.0001016]; median 0.0001057; 49 / 0 / 51; p 0.718 | 0.3102 [0.1529, 0.5494]; median 0.07478; 12 / 0 / 88; p 5.19e-15 |
| dense (n = 100) | 30 | `timesfm2p5_hurdle` | 0.3159 [0.1604, 0.5552]; median 0.08556; 12 / 0 / 88; p 2.99e-14 | 0.06179 [0.0472, 0.07799]; median 0.04079; 12 / 0 / 88; p 1.08e-14 | -0.00413 [-0.008684, -0.0001216]; median 0.0001057; 49 / 0 / 51; p 0.718 | 0.3018 [0.1517, 0.5419]; median 0.07982; 10 / 0 / 90; p 1.42e-14 |
| dense (n = 100) | 30 | `chronos2_hurdle_dynamic` | 0.3236 [0.1634, 0.5719]; median 0.09222; 13 / 0 / 87; p 3.11e-14 | 0.06394 [0.04939, 0.0801]; median 0.04513; 13 / 0 / 87; p 1.31e-14 | -0.003842 [-0.009543, 0.001248]; median 0.0006159; 45 / 0 / 55; p 0.0591 | 0.3098 [0.1553, 0.5511]; median 0.08079; 14 / 0 / 86; p 5.21e-14 |
| dense (n = 100) | 30 | `timesfm3_hurdle_dynamic` | 0.3282 [0.1657, 0.5813]; median 0.09272; 11 / 0 / 89; p 2.52e-14 | 0.06395 [0.04932, 0.08028]; median 0.04608; 12 / 0 / 88; p 9.44e-15 | -0.003842 [-0.009671, 0.001191]; median 0.0006159; 45 / 0 / 55; p 0.0591 | 0.3168 [0.1594, 0.5612]; median 0.084; 12 / 0 / 88; p 1.45e-14 |
| dense (n = 100) | 30 | `timesfm2p5_hurdle_dynamic` | 0.3215 [0.1663, 0.5615]; median 0.08926; 11 / 0 / 89; p 3.42e-14 | 0.06381 [0.04925, 0.07963]; median 0.04643; 11 / 0 / 89; p 4.78e-15 | -0.003842 [-0.009657, 0.001182]; median 0.0006159; 45 / 0 / 55; p 0.0591 | 0.3074 [0.1572, 0.5408]; median 0.08781; 11 / 0 / 89; p 1.42e-14 |
| dense (n = 100) | 30 | `hurdle_count_28` | -0.01635 [-0.04746, 0.01217]; median 0.006173; 46 / 1 / 53; p 0.804 | -0.007603 [-0.01839, 0.002012]; median 0.001853; 46 / 1 / 53; p 0.708 | -0.00413 [-0.008734, -8.139e-05]; median 0.0001057; 49 / 0 / 51; p 0.718 | -0.01246 [-0.04106, 0.01437]; median 0.005221; 42 / 0 / 58; p 0.487 |
| dense (n = 100) | 30 | `dynamic_count` | 0.01466 [-0.04238, 0.06541]; median 0.03111; 30 / 1 / 69; p 0.00306 | 0.01293 [-0.001595, 0.02642]; median 0.01107; 30 / 1 / 69; p 0.000461 | -0.003842 [-0.009565, 0.001179]; median 0.0006159; 45 / 0 / 55; p 0.0591 | 0.01121 [-0.04428, 0.05891]; median 0.02398; 33 / 0 / 67; p 0.00206 |
| sparse (n = 100) | 7 | `chronos2_completed` | 0.005587 [-0.0007196, 0.01193]; median 0.0005291; 45 / 5 / 50; p 0.202 | 0.005344 [-0.00091, 0.01176]; median 0.0005291; 45 / 5 / 50; p 0.211 | 0.002525 [-0.001989, 0.007105]; median -0.0007868; 51 / 0 / 49; p 0.547 | 0.005622 [2.832e-05, 0.0113]; median 0.003289; 45 / 0 / 55; p 0.0711 |
| sparse (n = 100) | 7 | `timesfm3_completed` | 0.008402 [0.003735, 0.01347]; median 0.003175; 35 / 10 / 55; p 0.00553 | 0.008319 [0.003603, 0.01338]; median 0.003175; 35 / 10 / 55; p 0.00577 | 0.004102 [0.0007458, 0.007555]; median 0.002628; 42 / 0 / 58; p 0.0508 | 0.007252 [0.00299, 0.01166]; median 0.003279; 40 / 0 / 60; p 0.00862 |
| sparse (n = 100) | 7 | `timesfm2p5_completed` | 0.001947 [-0.004296, 0.008148]; median 0; 46 / 6 / 48; p 0.586 | 0.001777 [-0.004307, 0.007905]; median 0; 46 / 6 / 48; p 0.596 | 0.0008756 [-0.003124, 0.004997]; median -0.0008518; 52 / 0 / 48; p 0.91 | 0.003959 [-0.001409, 0.009208]; median 0.001066; 47 / 0 / 53; p 0.163 |
| sparse (n = 100) | 7 | `chronos2_hurdle` | 0.00164 [-0.003407, 0.006646]; median 0; 45 / 11 / 44; p 0.739 | 0.001427 [-0.003541, 0.006445]; median 0; 45 / 11 / 44; p 0.745 | 0.0006414 [-0.002405, 0.003667]; median 0.0002497; 49 / 0 / 51; p 0.823 | 0.001074 [-0.003675, 0.005931]; median -0.001748; 55 / 0 / 45; p 0.797 |
| sparse (n = 100) | 7 | `timesfm3_hurdle` | 0.004212 [-0.0007513, 0.009323]; median 0; 37 / 14 / 49; p 0.155 | 0.00403 [-0.0008572, 0.008936]; median 0; 37 / 14 / 49; p 0.157 | 0.0006414 [-0.002428, 0.003689]; median 0.0002497; 49 / 0 / 51; p 0.823 | 0.002436 [-0.001729, 0.006707]; median -0.000621; 53 / 0 / 47; p 0.611 |
| sparse (n = 100) | 7 | `timesfm2p5_hurdle` | 0.004571 [-0.0006561, 0.00981]; median 0.0005291; 34 / 16 / 50; p 0.058 | 0.00435 [-0.0007979, 0.009469]; median 0.0005291; 34 / 16 / 50; p 0.0598 | 0.0006414 [-0.002393, 0.003669]; median 0.0002497; 49 / 0 / 51; p 0.823 | 0.002811 [-0.001695, 0.007246]; median -0.0003576; 53 / 0 / 47; p 0.492 |
| sparse (n = 100) | 7 | `chronos2_hurdle_dynamic` | 0.007725 [0.001704, 0.01401]; median 0.003175; 42 / 7 / 51; p 0.0402 | 0.007459 [0.001532, 0.0136]; median 0.003175; 42 / 7 / 51; p 0.0417 | 0.002968 [-0.001081, 0.007066]; median 0.001574; 45 / 0 / 55; p 0.162 | 0.005611 [0.0003086, 0.011]; median 0.001934; 44 / 0 / 56; p 0.0801 |
| sparse (n = 100) | 7 | `timesfm3_hurdle_dynamic` | 0.008095 [0.002423, 0.01399]; median 0.003175; 33 / 13 / 54; p 0.00806 | 0.007882 [0.002233, 0.01369]; median 0.003175; 33 / 13 / 54; p 0.00837 | 0.002968 [-0.001059, 0.006981]; median 0.001574; 45 / 0 / 55; p 0.162 | 0.005436 [-2.942e-05, 0.01076]; median 0.00179; 44 / 0 / 56; p 0.0369 |
| sparse (n = 100) | 7 | `timesfm2p5_hurdle_dynamic` | 0.006868 [0.001058, 0.0127]; median 0.003175; 34 / 12 / 54; p 0.0185 | 0.006623 [0.0008834, 0.01237]; median 0.003175; 34 / 12 / 54; p 0.0194 | 0.002968 [-0.001011, 0.006983]; median 0.001574; 45 / 0 / 55; p 0.162 | 0.004923 [-0.001023, 0.01049]; median 0.001605; 45 / 0 / 55; p 0.0469 |
| sparse (n = 100) | 7 | `hurdle_count_28` | 0.003143 [-0.001873, 0.008307]; median 0; 40 / 14 / 46; p 0.319 | 0.002968 [-0.002006, 0.008087]; median 0; 40 / 14 / 46; p 0.321 | 0.0006414 [-0.002359, 0.003672]; median 0.0002497; 49 / 0 / 51; p 0.823 | 0.0004463 [-0.003514, 0.004282]; median 0.0002082; 48 / 0 / 52; p 0.847 |
| sparse (n = 100) | 7 | `dynamic_count` | 0.006942 [0.001217, 0.01275]; median 0.003175; 33 / 13 / 54; p 0.0172 | 0.006786 [0.001108, 0.0125]; median 0.003175; 33 / 13 / 54; p 0.0176 | 0.002968 [-0.00101, 0.007012]; median 0.001574; 45 / 0 / 55; p 0.162 | 0.004537 [-0.0006017, 0.009615]; median 0.001916; 46 / 0 / 54; p 0.0496 |
| sparse (n = 100) | 30 | `chronos2_completed` | 0.00464 [-0.0002569, 0.009748]; median 0.0006173; 44 / 6 / 50; p 0.195 | 0.004498 [-0.000299, 0.009449]; median 0.0006173; 44 / 6 / 50; p 0.202 | 0.002687 [-0.0002983, 0.005578]; median 0.0006871; 44 / 0 / 56; p 0.0862 | 0.0047 [0.0005927, 0.00907]; median 0.001165; 46 / 0 / 54; p 0.0989 |
| sparse (n = 100) | 30 | `timesfm3_completed` | 0.009662 [0.006126, 0.01348]; median 0.004321; 27 / 9 / 64; p 2.25e-06 | 0.009544 [0.005973, 0.01343]; median 0.004321; 27 / 9 / 64; p 2.29e-06 | 0.004872 [0.0028, 0.007075]; median 0.00209; 34 / 0 / 66; p 9.39e-05 | 0.007965 [0.004774, 0.01139]; median 0.003286; 34 / 0 / 66; p 2.11e-05 |
| sparse (n = 100) | 30 | `timesfm2p5_completed` | 0.005684 [0.001849, 0.009756]; median 0.0002469; 39 / 11 / 50; p 0.0262 | 0.005511 [0.001705, 0.009523]; median 0.0002469; 39 / 11 / 50; p 0.0267 | 0.002954 [0.0004433, 0.005506]; median 0.0006565; 44 / 0 / 56; p 0.0504 | 0.006022 [0.002666, 0.009494]; median 0.00198; 37 / 0 / 63; p 0.00104 |
| sparse (n = 100) | 30 | `chronos2_hurdle` | 0.002002 [-0.001748, 0.005872]; median 0; 46 / 13 / 41; p 0.632 | 0.00186 [-0.001898, 0.005649]; median 0; 46 / 13 / 41; p 0.648 | 0.001169 [-0.00081, 0.00316]; median 0.0009254; 43 / 0 / 57; p 0.238 | 0.001261 [-0.001986, 0.004526]; median 9.021e-05; 50 / 0 / 50; p 0.872 |
| sparse (n = 100) | 30 | `timesfm3_hurdle` | 0.004249 [0.0005185, 0.008054]; median 0; 36 / 17 / 47; p 0.0514 | 0.004127 [0.0004897, 0.00789]; median 0; 36 / 17 / 47; p 0.0536 | 0.001169 [-0.0007728, 0.003172]; median 0.0009254; 43 / 0 / 57; p 0.238 | 0.003598 [0.0006701, 0.006622]; median 0.001034; 44 / 0 / 56; p 0.0819 |
| sparse (n = 100) | 30 | `timesfm2p5_hurdle` | 0.004398 [0.0008642, 0.008005]; median 0.0006173; 34 / 16 / 50; p 0.0341 | 0.004242 [0.0006704, 0.00788]; median 0.0006173; 34 / 16 / 50; p 0.0341 | 0.001169 [-0.0007881, 0.00316]; median 0.0009254; 43 / 0 / 57; p 0.238 | 0.003611 [0.0008087, 0.006536]; median 0.001224; 40 / 0 / 60; p 0.027 |
| sparse (n = 100) | 30 | `chronos2_hurdle_dynamic` | 0.006294 [0.002151, 0.01087]; median 6.939e-18; 39 / 11 / 50; p 0.0271 | 0.006187 [0.002014, 0.01076]; median 6.939e-18; 39 / 11 / 50; p 0.0282 | 0.002462 [-0.0003313, 0.005294]; median 0.001643; 38 / 0 / 62; p 0.0314 | 0.004852 [0.0012, 0.008654]; median 0.002411; 41 / 0 / 59; p 0.0237 |
| sparse (n = 100) | 30 | `timesfm3_hurdle_dynamic` | 0.00742 [0.003141, 0.01193]; median 0.002469; 23 / 23 / 54; p 0.000294 | 0.007305 [0.003114, 0.01184]; median 0.002469; 23 / 23 / 54; p 0.000312 | 0.002462 [-0.000364, 0.005363]; median 0.001643; 38 / 0 / 62; p 0.0314 | 0.005504 [0.001799, 0.009401]; median 0.002836; 38 / 0 / 62; p 0.00167 |
| sparse (n = 100) | 30 | `timesfm2p5_hurdle_dynamic` | 0.006669 [0.002415, 0.01104]; median 0.002469; 23 / 20 / 57; p 0.00028 | 0.006539 [0.002373, 0.011]; median 0.002469; 23 / 20 / 57; p 0.00029 | 0.002462 [-0.0003754, 0.005355]; median 0.001643; 38 / 0 / 62; p 0.0314 | 0.004948 [0.001227, 0.008759]; median 0.002514; 36 / 0 / 64; p 0.00175 |
| sparse (n = 100) | 30 | `hurdle_count_28` | 0.001481 [-0.001926, 0.004889]; median 0; 38 / 16 / 46; p 0.392 | 0.001366 [-0.001937, 0.004739]; median 0; 38 / 16 / 46; p 0.412 | 0.001169 [-0.0007679, 0.003127]; median 0.0009254; 43 / 0 / 57; p 0.238 | 0.0004274 [-0.002181, 0.003005]; median 0.0008335; 44 / 0 / 56; p 0.386 |
| sparse (n = 100) | 30 | `dynamic_count` | 0.005788 [0.001551, 0.01023]; median 6.939e-18; 26 / 24 / 50; p 0.00383 | 0.005716 [0.001461, 0.01009]; median 6.939e-18; 26 / 24 / 50; p 0.00373 | 0.002462 [-0.0003661, 0.00532]; median 0.001643; 38 / 0 / 62; p 0.0314 | 0.003813 [-4.206e-05, 0.007742]; median 0.002002; 32 / 0 / 68; p 0.00363 |
| very_sparse (n = 100) | 7 | `chronos2_completed` | 0.001534 [-0.0003492, 0.003545]; median 0; 9 / 74 / 17; p 0.0106 | 0.001902 [0.0002055, 0.003764]; median 0; 9 / 74 / 17; p 0.00329 | -0.0003813 [-0.001997, 0.001258]; median -0.002869; 67 / 0 / 33; p 0.0321 | -0.000293 [-0.002076, 0.00151]; median -0.003406; 66 / 0 / 34; p 0.0421 |
| very_sparse (n = 100) | 7 | `timesfm3_completed` | 0.00128 [-9.524e-05, 0.002762]; median 0; 10 / 74 / 16; p 0.0228 | 0.00128 [-8.466e-05, 0.002751]; median 0; 10 / 74 / 16; p 0.0228 | -0.000133 [-0.001255, 0.001066]; median -0.002795; 66 / 0 / 34; p 0.08 | -0.0001004 [-0.001509, 0.001609]; median -0.003182; 65 / 0 / 35; p 0.024 |
| very_sparse (n = 100) | 7 | `timesfm2p5_completed` | 0.0009947 [-0.0009735, 0.003079]; median 0; 10 / 73 / 17; p 0.0749 | 0.001391 [-0.0003395, 0.003338]; median 0; 10 / 73 / 17; p 0.0322 | -0.0005131 [-0.002251, 0.001216]; median -0.002949; 68 / 0 / 32; p 0.0442 | -0.0007895 [-0.002757, 0.001183]; median -0.003458; 68 / 0 / 32; p 0.0138 |
| very_sparse (n = 100) | 7 | `chronos2_hurdle` | -0.001111 [-0.003534, 0.000709]; median 0; 19 / 66 / 15; p 0.681 | -0.001111 [-0.003566, 0.0006878]; median 0; 19 / 66 / 15; p 0.681 | -0.0003669 [-0.001519, 0.0006802]; median -0.0002973; 73 / 0 / 27; p 0.0155 | -0.001033 [-0.002476, 0.0001367]; median -0.0003438; 75 / 0 / 25; p 0.00114 |
| very_sparse (n = 100) | 7 | `timesfm3_hurdle` | -0.0007725 [-0.002688, 0.0007725]; median 0; 19 / 66 / 15; p 0.706 | -0.0007725 [-0.002698, 0.0007831]; median 0; 19 / 66 / 15; p 0.706 | -0.0003669 [-0.001532, 0.0006692]; median -0.0002973; 73 / 0 / 27; p 0.0155 | -0.0008494 [-0.002055, 0.0002191]; median -0.0003438; 75 / 0 / 25; p 0.00141 |
| very_sparse (n = 100) | 7 | `timesfm2p5_hurdle` | -0.0008889 [-0.003143, 0.0008042]; median 0; 19 / 66 / 15; p 0.719 | -0.0008889 [-0.003175, 0.0008254]; median 0; 19 / 66 / 15; p 0.719 | -0.0003669 [-0.001538, 0.0006771]; median -0.0002973; 73 / 0 / 27; p 0.0155 | -0.001209 [-0.002902, 0.0001446]; median -0.0003438; 75 / 0 / 25; p 0.00138 |
| very_sparse (n = 100) | 7 | `chronos2_hurdle_dynamic` | -0.001005 [-0.004878, 0.001778]; median 0; 11 / 74 / 15; p 0.173 | -0.001005 [-0.004847, 0.001735]; median 0; 11 / 74 / 15; p 0.173 | -0.0003308 [-0.002891, 0.001552]; median -0.0002973; 64 / 0 / 36; p 0.861 | -0.001238 [-0.005092, 0.001266]; median -0.0003438; 63 / 0 / 37; p 0.598 |
| very_sparse (n = 100) | 7 | `timesfm3_hurdle_dynamic` | -0.0009735 [-0.004857, 0.001778]; median 0; 11 / 74 / 15; p 0.158 | -0.0009735 [-0.004804, 0.001788]; median 0; 11 / 74 / 15; p 0.158 | -0.0003308 [-0.002789, 0.001517]; median -0.0002973; 64 / 0 / 36; p 0.861 | -0.001142 [-0.00465, 0.001267]; median -0.0003438; 64 / 0 / 36; p 0.703 |
| very_sparse (n = 100) | 7 | `timesfm2p5_hurdle_dynamic` | -0.000963 [-0.004804, 0.001778]; median 0; 11 / 74 / 15; p 0.158 | -0.000963 [-0.004847, 0.001788]; median 0; 11 / 74 / 15; p 0.158 | -0.0003308 [-0.002887, 0.001536]; median -0.0002973; 64 / 0 / 36; p 0.861 | -0.001398 [-0.00541, 0.001247]; median -0.0003438; 64 / 0 / 36; p 0.611 |
| very_sparse (n = 100) | 7 | `hurdle_count_28` | -0.001037 [-0.003344, 0.0006772]; median 0; 19 / 66 / 15; p 0.608 | -0.001037 [-0.003333, 0.0006984]; median 0; 19 / 66 / 15; p 0.608 | -0.0003669 [-0.001564, 0.0006721]; median -0.0002973; 73 / 0 / 27; p 0.0155 | -0.001072 [-0.00313, 0.0004073]; median -0.0002973; 74 / 0 / 26; p 0.00796 |
| very_sparse (n = 100) | 7 | `dynamic_count` | -0.001492 [-0.006381, 0.001767]; median 0; 11 / 74 / 15; p 0.158 | -0.001492 [-0.006402, 0.001735]; median 0; 11 / 74 / 15; p 0.158 | -0.0003308 [-0.002854, 0.001542]; median -0.0002973; 64 / 0 / 36; p 0.861 | -0.00153 [-0.00612, 0.001382]; median -0.0002973; 64 / 0 / 36; p 0.926 |
| very_sparse (n = 100) | 30 | `chronos2_completed` | 0.0004963 [-0.001346, 0.002212]; median 0; 10 / 69 / 21; p 0.0351 | 0.0009102 [-0.0006997, 0.002446]; median 0; 10 / 69 / 21; p 0.0181 | -0.001397 [-0.00375, 0.0004435]; median -0.001357; 67 / 0 / 33; p 0.0226 | -0.001162 [-0.002567, 0.0001803]; median -0.001889; 71 / 0 / 29; p 0.00399 |
| very_sparse (n = 100) | 30 | `timesfm3_completed` | 0.002664 [0.0007012, 0.005618]; median 0; 13 / 66 / 21; p 0.00453 | 0.002667 [0.0007159, 0.005684]; median 0; 13 / 66 / 21; p 0.00453 | -0.0003358 [-0.001187, 0.0006128]; median -0.001418; 65 / 0 / 35; p 0.00817 | 0.0005753 [-0.001578, 0.004075]; median -0.001929; 69 / 0 / 31; p 0.00054 |
| very_sparse (n = 100) | 30 | `timesfm2p5_completed` | 0.001244 [-0.0004766, 0.002827]; median 0; 6 / 71 / 23; p 0.00245 | 0.001797 [0.0007363, 0.003083]; median 0; 6 / 71 / 23; p 0.000796 | -0.0007073 [-0.002216, 0.0006726]; median -0.001368; 65 / 0 / 35; p 0.0647 | -0.0004109 [-0.002296, 0.001589]; median -0.001782; 67 / 0 / 33; p 0.0297 |
| very_sparse (n = 100) | 30 | `chronos2_hurdle` | 0.0002222 [-0.0008198, 0.00119]; median 0; 16 / 68 / 16; p 0.405 | 0.0002222 [-0.0008247, 0.00119]; median 0; 16 / 68 / 16; p 0.405 | -0.0002126 [-0.001567, 0.0007082]; median -0.0002973; 64 / 0 / 36; p 0.468 | 3.164e-05 [-0.0005238, 0.000704]; median -0.0003438; 69 / 0 / 31; p 0.0127 |
| very_sparse (n = 100) | 30 | `timesfm3_hurdle` | 0.0002 [-0.0009457, 0.001232]; median 0; 16 / 68 / 16; p 0.349 | 0.0002 [-0.0009753, 0.001237]; median 0; 16 / 68 / 16; p 0.349 | -0.0002126 [-0.001552, 0.0007194]; median -0.0002973; 64 / 0 / 36; p 0.468 | -1.067e-05 [-0.0005214, 0.0005365]; median -0.0003438; 69 / 0 / 31; p 0.0184 |
| very_sparse (n = 100) | 30 | `timesfm2p5_hurdle` | -0.0002173 [-0.002523, 0.001348]; median 0; 16 / 68 / 16; p 0.254 | -0.0002173 [-0.002435, 0.001328]; median 0; 16 / 68 / 16; p 0.254 | -0.0002126 [-0.00155, 0.0007146]; median -0.0002973; 64 / 0 / 36; p 0.468 | -0.0005537 [-0.001722, 0.0002928]; median -0.0003438; 69 / 0 / 31; p 0.0124 |
| very_sparse (n = 100) | 30 | `chronos2_hurdle_dynamic` | -1.235e-05 [-0.004121, 0.002519]; median 0; 4 / 76 / 20; p 0.00221 | -1.235e-05 [-0.004057, 0.002519]; median 0; 4 / 76 / 20; p 0.00221 | -0.0001177 [-0.003372, 0.001871]; median -8.268e-05; 50 / 0 / 50; p 0.0156 | -0.0003778 [-0.00385, 0.001702]; median -0.0003288; 55 / 0 / 45; p 0.169 |
| very_sparse (n = 100) | 30 | `timesfm3_hurdle_dynamic` | -0.0002469 [-0.004815, 0.002569]; median 0; 4 / 76 / 20; p 0.00221 | -0.0002469 [-0.00484, 0.002568]; median 0; 4 / 76 / 20; p 0.00221 | -0.0001177 [-0.003372, 0.00188]; median -8.268e-05; 50 / 0 / 50; p 0.0156 | -0.0004364 [-0.004061, 0.001738]; median -0.0003423; 56 / 0 / 44; p 0.181 |
| very_sparse (n = 100) | 30 | `timesfm2p5_hurdle_dynamic` | -0.0003877 [-0.005336, 0.002568]; median 0; 4 / 76 / 20; p 0.00221 | -0.0003877 [-0.005336, 0.002568]; median 0; 4 / 76 / 20; p 0.00221 | -0.0001177 [-0.003335, 0.001873]; median -8.268e-05; 50 / 0 / 50; p 0.0156 | -0.0008457 [-0.005285, 0.001754]; median -0.0003424; 55 / 0 / 45; p 0.165 |
| very_sparse (n = 100) | 30 | `hurdle_count_28` | -0.0004444 [-0.002865, 0.001259]; median 0; 16 / 68 / 16; p 0.33 | -0.0004444 [-0.002864, 0.001235]; median 0; 16 / 68 / 16; p 0.33 | -0.0002126 [-0.001544, 0.000709]; median -0.0002973; 64 / 0 / 36; p 0.468 | -0.0009339 [-0.00338, 0.0005543]; median -0.0002973; 63 / 0 / 37; p 0.31 |
| very_sparse (n = 100) | 30 | `dynamic_count` | -0.0009383 [-0.006914, 0.002568]; median 0; 4 / 76 / 20; p 0.00221 | -0.0009383 [-0.006938, 0.002568]; median 0; 4 / 76 / 20; p 0.00221 | -0.0001177 [-0.003364, 0.001865]; median -8.268e-05; 50 / 0 / 50; p 0.0156 | -0.001272 [-0.00676, 0.00186]; median -5.078e-05; 50 / 0 / 50; p 0.02 |

### NYC 311: the TSB sensitivities, QScore9 (compact cells)

| Group | h | Reference | `tsb_hurdle_a005` | `tsb_hurdle` | `tsb_hurdle_a020` |
|---|---|---|---|---|---|
| all (n = 300) | 7 | `chronos2_completed` | 0.1043 / 0 (79 / 96 / 125) | 0.1058 / 0 (74 / 79 / 147) | 0.1179 / 0.006878 (65 / 75 / 160) |
| all (n = 300) | 7 | `timesfm3_completed` | 0.1071 / 0 (67 / 103 / 130) | 0.1087 / 0.001058 (64 / 84 / 152) | 0.1208 / 0.005291 (69 / 73 / 158) |
| all (n = 300) | 7 | `timesfm2p5_completed` | 0.106 / 0 (73 / 94 / 133) | 0.1075 / 0 (78 / 79 / 143) | 0.1196 / 0.001058 (72 / 75 / 153) |
| all (n = 300) | 7 | `chronos2_hurdle` | 0.09491 / 0 (98 / 95 / 107) | 0.09647 / 0 (87 / 77 / 136) | 0.1085 / 0.0005291 (83 / 67 / 150) |
| all (n = 300) | 7 | `timesfm3_hurdle` | 0.09686 / 0 (87 / 98 / 115) | 0.09842 / 0 (79 / 80 / 141) | 0.1105 / 0 (81 / 71 / 148) |
| all (n = 300) | 7 | `timesfm2p5_hurdle` | 0.09793 / 0 (83 / 100 / 117) | 0.09949 / 0 (74 / 82 / 144) | 0.1116 / 0.001587 (74 / 73 / 153) |
| all (n = 300) | 7 | `chronos2_hurdle_dynamic` | 0.0982 / 0 (64 / 109 / 127) | 0.09977 / 0 (70 / 81 / 149) | 0.1118 / 0.003704 (66 / 75 / 159) |
| all (n = 300) | 7 | `timesfm3_hurdle_dynamic` | 0.09929 / 0 (58 / 115 / 127) | 0.1009 / 0 (66 / 87 / 147) | 0.1129 / 0.003704 (67 / 75 / 158) |
| all (n = 300) | 7 | `timesfm2p5_hurdle_dynamic` | 0.09956 / 0 (61 / 116 / 123) | 0.1011 / 0 (67 / 86 / 147) | 0.1132 / 0.004762 (64 / 76 / 160) |
| all (n = 300) | 7 | `hurdle_count_28` | -0.01057 / 0 (122 / 104 / 74) | -0.009012 / 0 (111 / 80 / 109) | 0.003051 / 0 (96 / 70 / 134) |
| all (n = 300) | 7 | `dynamic_count` | -0.005009 / 0 (85 / 122 / 93) | -0.003446 / 0 (91 / 87 / 122) | 0.008617 / 0 (79 / 75 / 146) |
| all (n = 300) | 30 | `chronos2_completed` | 0.1074 / 0 (73 / 88 / 139) | 0.1146 / 0.002346 (66 / 75 / 159) | 0.1352 / 0.009136 (51 / 68 / 181) |
| all (n = 300) | 30 | `timesfm3_completed` | 0.1117 / 0.001975 (49 / 86 / 165) | 0.119 / 0.005309 (51 / 75 / 174) | 0.1396 / 0.01235 (46 / 64 / 190) |
| all (n = 300) | 30 | `timesfm2p5_completed` | 0.1084 / 0 (60 / 95 / 145) | 0.1157 / 0.002469 (54 / 83 / 163) | 0.1363 / 0.007407 (45 / 73 / 182) |
| all (n = 300) | 30 | `chronos2_hurdle` | 0.09837 / 0 (92 / 95 / 113) | 0.1056 / 0 (74 / 81 / 145) | 0.1262 / 0.005432 (59 / 71 / 170) |
| all (n = 300) | 30 | `timesfm3_hurdle` | 0.1015 / 0 (77 / 101 / 122) | 0.1087 / 0.0004938 (64 / 85 / 151) | 0.1293 / 0.007407 (58 / 71 / 171) |
| all (n = 300) | 30 | `timesfm2p5_hurdle` | 0.09944 / 0 (71 / 102 / 127) | 0.1067 / 0.002346 (62 / 84 / 154) | 0.1273 / 0.007037 (58 / 71 / 171) |
| all (n = 300) | 30 | `chronos2_hurdle_dynamic` | 0.1027 / 0 (50 / 112 / 138) | 0.1099 / 0.002469 (56 / 87 / 157) | 0.1306 / 0.007778 (37 / 80 / 183) |
| all (n = 300) | 30 | `timesfm3_hurdle_dynamic` | 0.1045 / 0 (36 / 125 / 139) | 0.1118 / 0.002469 (38 / 99 / 163) | 0.1324 / 0.009259 (33 / 82 / 185) |
| all (n = 300) | 30 | `timesfm2p5_hurdle_dynamic` | 0.102 / 0 (36 / 122 / 142) | 0.1092 / 0.004074 (38 / 96 / 166) | 0.1299 / 0.01 (33 / 81 / 186) |
| all (n = 300) | 30 | `hurdle_count_28` | -0.01235 / 0 (122 / 116 / 62) | -0.005103 / 0 (100 / 85 / 115) | 0.01551 / 0 (75 / 77 / 148) |
| all (n = 300) | 30 | `dynamic_count` | -0.0007473 / 0 (58 / 134 / 108) | 0.006504 / 0 (60 / 101 / 139) | 0.02711 / 0.003704 (52 / 85 / 163) |
| dense (n = 100) | 7 | `chronos2_completed` | 0.3109 / 0.0672 (27 / 0 / 73) | 0.3103 / 0.08042 (20 / 0 / 80) | 0.3367 / 0.1259 (18 / 0 / 82) |
| dense (n = 100) | 7 | `timesfm3_completed` | 0.317 / 0.07778 (19 / 0 / 81) | 0.3164 / 0.1032 (19 / 0 / 81) | 0.3428 / 0.1217 (19 / 0 / 81) |
| dense (n = 100) | 7 | `timesfm2p5_completed` | 0.3202 / 0.07566 (18 / 0 / 82) | 0.3197 / 0.09365 (22 / 0 / 78) | 0.346 / 0.127 (20 / 0 / 80) |
| dense (n = 100) | 7 | `chronos2_hurdle` | 0.2894 / 0.04497 (26 / 0 / 74) | 0.2889 / 0.06984 (23 / 0 / 77) | 0.3152 / 0.1063 (22 / 0 / 78) |
| dense (n = 100) | 7 | `timesfm3_hurdle` | 0.2924 / 0.05608 (23 / 0 / 77) | 0.2918 / 0.08836 (23 / 0 / 77) | 0.3182 / 0.1138 (25 / 0 / 75) |
| dense (n = 100) | 7 | `timesfm2p5_hurdle` | 0.2954 / 0.06402 (23 / 0 / 77) | 0.2948 / 0.0873 (21 / 0 / 79) | 0.3211 / 0.1148 (22 / 0 / 78) |
| dense (n = 100) | 7 | `chronos2_hurdle_dynamic` | 0.2932 / 0.04709 (18 / 1 / 81) | 0.2926 / 0.08307 (17 / 0 / 83) | 0.3189 / 0.1159 (20 / 0 / 80) |
| dense (n = 100) | 7 | `timesfm3_hurdle_dynamic` | 0.296 / 0.06614 (20 / 0 / 80) | 0.2954 / 0.09153 (22 / 0 / 78) | 0.3218 / 0.1111 (23 / 0 / 77) |
| dense (n = 100) | 7 | `timesfm2p5_hurdle_dynamic` | 0.298 / 0.06772 (21 / 1 / 78) | 0.2975 / 0.08624 (22 / 0 / 78) | 0.3238 / 0.1127 (20 / 0 / 80) |
| dense (n = 100) | 7 | `hurdle_count_28` | -0.02857 / -0.008466 (59 / 0 / 41) | -0.02914 / -0.003175 (52 / 0 / 48) | -0.002794 / 0.03333 (39 / 0 / 61) |
| dense (n = 100) | 7 | `dynamic_count` | -0.01522 / 0 (48 / 4 / 48) | -0.01579 / 0.009524 (47 / 0 / 53) | 0.01056 / 0.03651 (34 / 0 / 66) |
| dense (n = 100) | 30 | `chronos2_completed` | 0.3225 / 0.09704 (14 / 0 / 86) | 0.3387 / 0.1219 (12 / 0 / 88) | 0.3885 / 0.1517 (9 / 0 / 91) |
| dense (n = 100) | 30 | `timesfm3_completed` | 0.3284 / 0.08531 (9 / 0 / 91) | 0.3446 / 0.1101 (11 / 0 / 89) | 0.3944 / 0.1611 (12 / 0 / 88) |
| dense (n = 100) | 30 | `timesfm2p5_completed` | 0.3239 / 0.08704 (10 / 0 / 90) | 0.3401 / 0.1074 (9 / 1 / 90) | 0.3899 / 0.1496 (9 / 0 / 91) |
| dense (n = 100) | 30 | `chronos2_hurdle` | 0.2984 / 0.0679 (14 / 0 / 86) | 0.3146 / 0.08272 (12 / 0 / 88) | 0.3645 / 0.1457 (14 / 0 / 86) |
| dense (n = 100) | 30 | `timesfm3_hurdle` | 0.3055 / 0.07889 (7 / 0 / 93) | 0.3217 / 0.07988 (12 / 0 / 88) | 0.3715 / 0.1377 (14 / 0 / 86) |
| dense (n = 100) | 30 | `timesfm2p5_hurdle` | 0.2997 / 0.07198 (8 / 0 / 92) | 0.3159 / 0.08556 (12 / 0 / 88) | 0.3657 / 0.1337 (15 / 0 / 85) |
| dense (n = 100) | 30 | `chronos2_hurdle_dynamic` | 0.3074 / 0.08062 (10 / 1 / 89) | 0.3236 / 0.09222 (13 / 0 / 87) | 0.3734 / 0.1593 (12 / 0 / 88) |
| dense (n = 100) | 30 | `timesfm3_hurdle_dynamic` | 0.312 / 0.07469 (10 / 0 / 90) | 0.3282 / 0.09272 (11 / 0 / 89) | 0.378 / 0.1562 (12 / 0 / 88) |
| dense (n = 100) | 30 | `timesfm2p5_hurdle_dynamic` | 0.3053 / 0.07704 (8 / 1 / 91) | 0.3215 / 0.08926 (11 / 0 / 89) | 0.3713 / 0.1391 (12 / 0 / 88) |
| dense (n = 100) | 30 | `hurdle_count_28` | -0.03254 / -0.007407 (60 / 5 / 35) | -0.01635 / 0.006173 (46 / 1 / 53) | 0.03351 / 0.04815 (32 / 3 / 65) |
| dense (n = 100) | 30 | `dynamic_count` | -0.001536 / 0.01235 (33 / 4 / 63) | 0.01466 / 0.03111 (30 / 1 / 69) | 0.06451 / 0.06914 (29 / 1 / 70) |
| sparse (n = 100) | 7 | `chronos2_completed` | 8.466e-05 / 0 (46 / 10 / 44) | 0.005587 / 0.0005291 (45 / 5 / 50) | 0.01472 / 0.006878 (39 / 5 / 56) |
| sparse (n = 100) | 7 | `timesfm3_completed` | 0.002899 / 0 (40 / 18 / 42) | 0.008402 / 0.003175 (35 / 10 / 55) | 0.01753 / 0.006349 (39 / 5 / 56) |
| sparse (n = 100) | 7 | `timesfm2p5_completed` | -0.003556 / 0 (49 / 8 / 43) | 0.001947 / 0 (46 / 6 / 48) | 0.01108 / 0.004233 (44 / 3 / 53) |
| sparse (n = 100) | 7 | `chronos2_hurdle` | -0.003862 / -0.002646 (54 / 19 / 27) | 0.00164 / 0 (45 / 11 / 44) | 0.01077 / 0.003175 (42 / 5 / 53) |
| sparse (n = 100) | 7 | `timesfm3_hurdle` | -0.001291 / 0 (46 / 22 / 32) | 0.004212 / 0 (37 / 14 / 49) | 0.01334 / 0.006349 (37 / 9 / 54) |
| sparse (n = 100) | 7 | `timesfm2p5_hurdle` | -0.0009312 / 0 (43 / 23 / 34) | 0.004571 / 0.0005291 (34 / 16 / 50) | 0.0137 / 0.006349 (33 / 11 / 56) |
| sparse (n = 100) | 7 | `chronos2_hurdle_dynamic` | 0.002222 / 0 (39 / 18 / 43) | 0.007725 / 0.003175 (42 / 7 / 51) | 0.01686 / 0.00582 (37 / 4 / 59) |
| sparse (n = 100) | 7 | `timesfm3_hurdle_dynamic` | 0.002593 / 0 (31 / 25 / 44) | 0.008095 / 0.003175 (33 / 13 / 54) | 0.01723 / 0.007937 (35 / 4 / 61) |
| sparse (n = 100) | 7 | `timesfm2p5_hurdle_dynamic` | 0.001365 / 0 (33 / 25 / 42) | 0.006868 / 0.003175 (34 / 12 / 54) | 0.016 / 0.007407 (35 / 5 / 60) |
| sparse (n = 100) | 7 | `hurdle_count_28` | -0.00236 / 0 (46 / 27 / 27) | 0.003143 / 0 (40 / 14 / 46) | 0.01228 / 0.003175 (38 / 8 / 54) |
| sparse (n = 100) | 7 | `dynamic_count` | 0.001439 / 0 (30 / 28 / 42) | 0.006942 / 0.003175 (33 / 13 / 54) | 0.01607 / 0.007407 (36 / 4 / 60) |
| sparse (n = 100) | 30 | `chronos2_completed` | -0.000916 / 0 (48 / 8 / 44) | 0.00464 / 0.0006173 (44 / 6 / 50) | 0.01528 / 0.007407 (32 / 3 / 65) |
| sparse (n = 100) | 30 | `timesfm3_completed` | 0.004106 / 0.002469 (25 / 13 / 62) | 0.009662 / 0.004321 (27 / 9 / 64) | 0.0203 / 0.01235 (23 / 4 / 73) |
| sparse (n = 100) | 30 | `timesfm2p5_completed` | 0.0001284 / 0 (43 / 11 / 46) | 0.005684 / 0.0002469 (39 / 11 / 50) | 0.01633 / 0.005802 (28 / 6 / 66) |
| sparse (n = 100) | 30 | `chronos2_hurdle` | -0.003553 / -0.002469 (57 / 18 / 25) | 0.002002 / 0 (46 / 13 / 41) | 0.01264 / 0.005556 (29 / 8 / 63) |
| sparse (n = 100) | 30 | `timesfm3_hurdle` | -0.001306 / -0.0002469 (50 / 23 / 27) | 0.004249 / 0 (36 / 17 / 47) | 0.01489 / 0.00642 (28 / 8 / 64) |
| sparse (n = 100) | 30 | `timesfm2p5_hurdle` | -0.001158 / 0 (43 / 24 / 33) | 0.004398 / 0.0006173 (34 / 16 / 50) | 0.01504 / 0.007037 (27 / 8 / 65) |
| sparse (n = 100) | 30 | `chronos2_hurdle_dynamic` | 0.0007383 / 0 (38 / 19 / 43) | 0.006294 / 6.939e-18 (39 / 11 / 50) | 0.01694 / 0.007778 (22 / 8 / 70) |
| sparse (n = 100) | 30 | `timesfm3_hurdle_dynamic` | 0.001864 / 0 (24 / 33 / 43) | 0.00742 / 0.002469 (23 / 23 / 54) | 0.01806 / 0.01099 (18 / 10 / 72) |
| sparse (n = 100) | 30 | `timesfm2p5_hurdle_dynamic` | 0.001114 / 0 (26 / 29 / 45) | 0.006669 / 0.002469 (23 / 20 / 57) | 0.01731 / 0.01123 (18 / 9 / 73) |
| sparse (n = 100) | 30 | `hurdle_count_28` | -0.004074 / 0 (43 / 32 / 25) | 0.001481 / 0 (38 / 16 / 46) | 0.01212 / 0.006173 (27 / 11 / 62) |
| sparse (n = 100) | 30 | `dynamic_count` | 0.0002321 / 0 (23 / 38 / 39) | 0.005788 / 6.939e-18 (26 / 24 / 50) | 0.01643 / 0.007407 (20 / 12 / 68) |
| very_sparse (n = 100) | 7 | `chronos2_completed` | 0.001778 / 0 (6 / 86 / 8) | 0.001534 / 0 (9 / 74 / 17) | 0.002243 / 0 (8 / 70 / 22) |
| very_sparse (n = 100) | 7 | `timesfm3_completed` | 0.001524 / 0 (8 / 85 / 7) | 0.00128 / 0 (10 / 74 / 16) | 0.001989 / 0 (11 / 68 / 21) |
| very_sparse (n = 100) | 7 | `timesfm2p5_completed` | 0.001238 / 0 (6 / 86 / 8) | 0.0009947 / 0 (10 / 73 / 17) | 0.001704 / 0 (8 / 72 / 20) |
| very_sparse (n = 100) | 7 | `chronos2_hurdle` | -0.0008677 / 0 (18 / 76 / 6) | -0.001111 / 0 (19 / 66 / 15) | -0.0004021 / 0 (19 / 62 / 19) |
| very_sparse (n = 100) | 7 | `timesfm3_hurdle` | -0.0005291 / 0 (18 / 76 / 6) | -0.0007725 / 0 (19 / 66 / 15) | -6.349e-05 / 0 (19 / 62 / 19) |
| very_sparse (n = 100) | 7 | `timesfm2p5_hurdle` | -0.0006455 / 0 (17 / 77 / 6) | -0.0008889 / 0 (19 / 66 / 15) | -0.0001799 / 0 (19 / 62 / 19) |
| very_sparse (n = 100) | 7 | `chronos2_hurdle_dynamic` | -0.0007619 / 0 (7 / 90 / 3) | -0.001005 / 0 (11 / 74 / 15) | -0.0002963 / 0 (9 / 71 / 20) |
| very_sparse (n = 100) | 7 | `timesfm3_hurdle_dynamic` | -0.0007302 / 0 (7 / 90 / 3) | -0.0009735 / 0 (11 / 74 / 15) | -0.0002646 / 0 (9 / 71 / 20) |
| very_sparse (n = 100) | 7 | `timesfm2p5_hurdle_dynamic` | -0.0007196 / 0 (7 / 90 / 3) | -0.000963 / 0 (11 / 74 / 15) | -0.000254 / 0 (9 / 71 / 20) |
| very_sparse (n = 100) | 7 | `hurdle_count_28` | -0.0007937 / 0 (17 / 77 / 6) | -0.001037 / 0 (19 / 66 / 15) | -0.000328 / 0 (19 / 62 / 19) |
| very_sparse (n = 100) | 7 | `dynamic_count` | -0.001249 / 0 (7 / 90 / 3) | -0.001492 / 0 (11 / 74 / 15) | -0.0007831 / 0 (9 / 71 / 20) |
| very_sparse (n = 100) | 30 | `chronos2_completed` | 0.0004963 / 0 (11 / 80 / 9) | 0.0004963 / 0 (10 / 69 / 21) | 0.00183 / 0 (10 / 65 / 25) |
| very_sparse (n = 100) | 30 | `timesfm3_completed` | 0.002664 / 0 (15 / 73 / 12) | 0.002664 / 0 (13 / 66 / 21) | 0.003998 / 0 (11 / 60 / 29) |
| very_sparse (n = 100) | 30 | `timesfm2p5_completed` | 0.001244 / 0 (7 / 84 / 9) | 0.001244 / 0 (6 / 71 / 23) | 0.002578 / 0 (8 / 67 / 25) |
| very_sparse (n = 100) | 30 | `chronos2_hurdle` | 0.0002222 / 0 (21 / 77 / 2) | 0.0002222 / 0 (16 / 68 / 16) | 0.001556 / 0 (16 / 63 / 21) |
| very_sparse (n = 100) | 30 | `timesfm3_hurdle` | 0.0002 / 0 (20 / 78 / 2) | 0.0002 / 0 (16 / 68 / 16) | 0.001533 / 0 (16 / 63 / 21) |
| very_sparse (n = 100) | 30 | `timesfm2p5_hurdle` | -0.0002173 / 0 (20 / 78 / 2) | -0.0002173 / 0 (16 / 68 / 16) | 0.001116 / 0 (16 / 63 / 21) |
| very_sparse (n = 100) | 30 | `chronos2_hurdle_dynamic` | -1.235e-05 / 0 (2 / 92 / 6) | -1.235e-05 / 0 (4 / 76 / 20) | 0.001321 / 0 (3 / 72 / 25) |
| very_sparse (n = 100) | 30 | `timesfm3_hurdle_dynamic` | -0.0002469 / 0 (2 / 92 / 6) | -0.0002469 / 0 (4 / 76 / 20) | 0.001086 / 0 (3 / 72 / 25) |
| very_sparse (n = 100) | 30 | `timesfm2p5_hurdle_dynamic` | -0.0003877 / 0 (2 / 92 / 6) | -0.0003877 / 0 (4 / 76 / 20) | 0.0009457 / 0 (3 / 72 / 25) |
| very_sparse (n = 100) | 30 | `hurdle_count_28` | -0.0004444 / 0 (19 / 79 / 2) | -0.0004444 / 0 (16 / 68 / 16) | 0.0008889 / 0 (16 / 63 / 21) |
| very_sparse (n = 100) | 30 | `dynamic_count` | -0.0009383 / 0 (2 / 92 / 6) | -0.0009383 / 0 (4 / 76 / 20) | 0.0003951 / 0 (3 / 72 / 25) |

### NYC 311: the fourth cell, four scores (full cells)

| Group | h | Variant | Reference | Source | QScore9 | Context-scaled QScore9 | Occurrence Brier | Discrete CRPS |
|---|---|---|---|---|---|---|---|---|
| all (n = 300) | 7 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | run's own | 0.09838 [0.04023, 0.1885]; median 0; 69 / 136 / 95; p 1.52e-06 | 0.01684 [0.01045, 0.02416]; median 0; 69 / 136 / 95; p 3.79e-07 | 0 [0, 0]; median 0; 0 / 300 / 0; p 1 | 0.09515 [0.03947, 0.1824]; median -0.0005758; 170 / 0 / 130; p 0.000833 |
| all (n = 300) | 7 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.01645 [-0.02498, -0.008882]; median 0; 143 / 79 / 78; p 1.29e-05 | -0.009491 [-0.01348, -0.005708]; median 0; 143 / 79 / 78; p 8.87e-07 | -0.00405 [-0.006519, -0.001657]; median -0.0002555; 153 / 0 / 147; p 0.0428 | -0.01457 [-0.02187, -0.008034]; median -0.001517; 157 / 0 / 143; p 0.000535 |
| all (n = 300) | 7 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | run's own | 0.104 [0.04389, 0.1977]; median 0; 37 / 151 / 112; p 1.64e-11 | 0.02017 [0.01321, 0.02806]; median 0; 37 / 151 / 112; p 9.03e-13 | 0 [0, 0]; median 0; 0 / 300 / 0; p 1 | 0.09983 [0.04292, 0.189]; median -0.0005758; 161 / 0 / 139; p 1.41e-05 |
| all (n = 300) | 7 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.01376 [-0.02056, -0.007577]; median 0; 128 / 91 / 81; p 0.000117 | -0.007235 [-0.01033, -0.004301]; median 0; 128 / 90 / 82; p 2.42e-05 | -0.004263 [-0.00598, -0.002623]; median -0.0002923; 161 / 0 / 139; p 0.00142 | -0.01229 [-0.01847, -0.006773]; median -0.0008018; 156 / 0 / 144; p 0.00158 |
| all (n = 300) | 7 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | run's own | 0.1027 [0.044, 0.1935]; median 0; 36 / 153 / 111; p 8.77e-12 | 0.01888 [0.01217, 0.02678]; median 0; 36 / 153 / 111; p 2.99e-12 | 0 [0, 0]; median 0; 0 / 300 / 0; p 1 | 0.09848 [0.0423, 0.1847]; median -0.0004306; 158 / 0 / 142; p 1.41e-06 |
| all (n = 300) | 7 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.0138 [-0.02113, -0.006984]; median 0; 144 / 80 / 76; p 0.000119 | -0.0064 [-0.009872, -0.00293]; median 0; 145 / 79 / 76; p 6.06e-05 | -0.003307 [-0.005337, -0.001347]; median -0.0002823; 161 / 0 / 139; p 0.0161 | -0.01307 [-0.01972, -0.007065]; median -0.001524; 160 / 0 / 140; p 0.000673 |
| all (n = 300) | 30 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | run's own | 0.1032 [0.04841, 0.1875]; median 0; 55 / 123 / 122; p 4.58e-14 | 0.0183 [0.01246, 0.02504]; median 0; 55 / 123 / 122; p 7.25e-14 | 0 [0, 0]; median 0; 0 / 300 / 0; p 1 | 0.0995 [0.04721, 0.1788]; median 4.051e-05; 149 / 0 / 151; p 1.02e-07 |
| all (n = 300) | 30 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.01653 [-0.02399, -0.009853]; median 0; 146 / 76 / 78; p 6.66e-07 | -0.008638 [-0.01207, -0.005415]; median 0; 146 / 76 / 78; p 3.08e-08 | -0.002654 [-0.004384, -0.0009831]; median -0.000292; 162 / 0 / 138; p 0.032 | -0.01408 [-0.02065, -0.008225]; median -0.0009064; 167 / 0 / 133; p 0.000146 |
| all (n = 300) | 30 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | run's own | 0.11 [0.05406, 0.1936]; median 0; 24 / 147 / 129; p 2.02e-20 | 0.02229 [0.01595, 0.0293]; median 0; 25 / 147 / 128; p 5.96e-21 | 0 [0, 0]; median 0; 0 / 300 / 0; p 1 | 0.1058 [0.05288, 0.1869]; median 4.782e-05; 149 / 0 / 151; p 3.71e-10 |
| all (n = 300) | 30 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.01411 [-0.0202, -0.008773]; median 0; 141 / 87 / 72; p 1.76e-07 | -0.007422 [-0.009962, -0.005079]; median 0; 140 / 87 / 73; p 2.8e-09 | -0.003516 [-0.00473, -0.002383]; median -0.0006953; 180 / 0 / 120; p 2.6e-06 | -0.01171 [-0.01727, -0.006849]; median -0.0009017; 170 / 0 / 130; p 0.000114 |
| all (n = 300) | 30 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | run's own | 0.1057 [0.05269, 0.1873]; median 0; 28 / 147 / 125; p 3.06e-19 | 0.02111 [0.01509, 0.02802]; median 0; 28 / 147 / 125; p 1.58e-19 | 0 [0, 0]; median 0; 0 / 300 / 0; p 1 | 0.1009 [0.04922, 0.178]; median 0.0003129; 138 / 0 / 162; p 1.49e-10 |
| all (n = 300) | 30 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.01504 [-0.02163, -0.009183]; median 0; 141 / 81 / 78; p 1.1e-06 | -0.007356 [-0.01015, -0.004712]; median 0; 141 / 81 / 78; p 6.04e-08 | -0.002924 [-0.004301, -0.001593]; median -0.0005896; 170 / 0 / 130; p 0.000562 | -0.01328 [-0.01938, -0.007924]; median -0.0008843; 167 / 0 / 133; p 0.000246 |
| dense (n = 100) | 7 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | run's own | 0.2944 [0.1243, 0.5658]; median 0.04127; 30 / 0 / 70; p 5.19e-08 | 0.04979 [0.03215, 0.06996]; median 0.01769; 30 / 0 / 70; p 4.86e-09 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.2842 [0.1197, 0.5391]; median 0.0541; 22 / 0 / 78; p 7.21e-10 |
| dense (n = 100) | 7 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.04508 [-0.06839, -0.02455]; median -0.02963; 68 / 1 / 31; p 3.33e-05 | -0.02388 [-0.03323, -0.01493]; median -0.01652; 68 / 1 / 31; p 1.12e-06 | -0.01028 [-0.0158, -0.004999]; median -0.003132; 68 / 0 / 32; p 0.000213 | -0.03902 [-0.05919, -0.0207]; median -0.01773; 68 / 0 / 32; p 7.36e-05 |
| dense (n = 100) | 7 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | run's own | 0.3094 [0.1334, 0.5841]; median 0.0672; 20 / 2 / 78; p 1.83e-10 | 0.058 [0.03921, 0.07955]; median 0.02778; 20 / 2 / 78; p 1.03e-11 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.2973 [0.1307, 0.5499]; median 0.06634; 17 / 0 / 83; p 1.32e-11 |
| dense (n = 100) | 7 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.03621 [-0.05493, -0.01853]; median -0.0127; 62 / 4 / 34; p 0.000285 | -0.01656 [-0.02381, -0.009638]; median -0.006613; 62 / 3 / 35; p 5.33e-05 | -0.009096 [-0.01282, -0.005519]; median -0.003182; 70 / 0 / 30; p 2.14e-05 | -0.03132 [-0.04858, -0.01575]; median -0.01449; 63 / 0 / 37; p 0.000268 |
| dense (n = 100) | 7 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | run's own | 0.3059 [0.1337, 0.5786]; median 0.05503; 19 / 0 / 81; p 1.24e-10 | 0.05442 [0.03611, 0.07607]; median 0.02281; 19 / 0 / 81; p 1.06e-11 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.2928 [0.1292, 0.5519]; median 0.06266; 16 / 0 / 84; p 1.29e-11 |
| dense (n = 100) | 7 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.04294 [-0.06259, -0.02488]; median -0.02646; 73 / 2 / 25; p 5.74e-06 | -0.02018 [-0.02801, -0.01287]; median -0.01146; 74 / 1 / 25; p 4.41e-07 | -0.009833 [-0.01415, -0.005806]; median -0.004898; 72 / 0 / 28; p 1.36e-05 | -0.03801 [-0.05656, -0.02134]; median -0.02296; 71 / 0 / 29; p 8.76e-06 |
| dense (n = 100) | 30 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | run's own | 0.3083 [0.1507, 0.551]; median 0.05938; 11 / 0 / 89; p 3.35e-15 | 0.05371 [0.03825, 0.07139]; median 0.02604; 11 / 0 / 89; p 1.17e-15 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.2967 [0.1452, 0.5313]; median 0.06904; 7 / 0 / 93; p 8.11e-16 |
| dense (n = 100) | 30 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.0467 [-0.06682, -0.02862]; median -0.02543; 71 / 2 / 27; p 5.63e-07 | -0.0226 [-0.03086, -0.01497]; median -0.01333; 71 / 2 / 27; p 1.81e-08 | -0.007626 [-0.01182, -0.003661]; median -0.001804; 70 / 0 / 30; p 7.57e-05 | -0.04003 [-0.05789, -0.02397]; median -0.01876; 71 / 0 / 29; p 1.98e-06 |
| dense (n = 100) | 30 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | run's own | 0.325 [0.1639, 0.5717]; median 0.08185; 10 / 0 / 90; p 3.01e-16 | 0.06204 [0.04557, 0.08119]; median 0.03051; 11 / 0 / 89; p 7.13e-17 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.3132 [0.1594, 0.5503]; median 0.08426; 6 / 0 / 94; p 2.84e-16 |
| dense (n = 100) | 30 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.03591 [-0.05251, -0.02066]; median -0.007778; 63 / 3 / 34; p 1.98e-05 | -0.01579 [-0.02207, -0.01017]; median -0.006076; 62 / 3 / 35; p 1.57e-06 | -0.006968 [-0.00962, -0.004516]; median -0.00338; 79 / 0 / 21; p 1.52e-08 | -0.03037 [-0.04573, -0.0169]; median -0.009781; 70 / 0 / 30; p 2.11e-05 |
| dense (n = 100) | 30 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | run's own | 0.3136 [0.1599, 0.5483]; median 0.07852; 9 / 0 / 91; p 1.75e-16 | 0.05988 [0.04385, 0.07788]; median 0.03137; 9 / 0 / 91; p 3.64e-17 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.2988 [0.1501, 0.5308]; median 0.067; 7 / 0 / 93; p 1.75e-16 |
| dense (n = 100) | 30 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.04287 [-0.06056, -0.02653]; median -0.02444; 68 / 2 / 30; p 4.35e-07 | -0.01915 [-0.02597, -0.01305]; median -0.01218; 68 / 2 / 30; p 3.08e-08 | -0.007481 [-0.01058, -0.004696]; median -0.002389; 75 / 0 / 25; p 5.55e-07 | -0.03768 [-0.05433, -0.02292]; median -0.01665; 69 / 0 / 31; p 1.36e-06 |
| sparse (n = 100) | 7 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | run's own | 0.0002646 [-0.001884, 0.002582]; median 0; 37 / 40 / 23; p 0.561 | 0.0002437 [-0.001916, 0.002519]; median 0; 37 / 40 / 23; p 0.563 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.001104 [-0.001203, 0.003521]; median -0.0006779; 59 / 0 / 41; p 0.97 |
| sparse (n = 100) | 7 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.00218 [-0.00818, 0.003788]; median -0.002646; 53 / 7 / 40; p 0.405 | -0.002133 [-0.008096, 0.003953]; median -0.002646; 53 / 7 / 40; p 0.429 | -0.001884 [-0.006289, 0.002484]; median 0.0002878; 49 / 0 / 51; p 0.67 | -0.004072 [-0.009249, 0.001075]; median -0.002071; 54 / 0 / 46; p 0.176 |
| sparse (n = 100) | 7 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | run's own | 0.001778 [-0.001926, 0.005048]; median 0; 17 / 53 / 30; p 0.064 | 0.001778 [-0.001864, 0.005048]; median 0; 17 / 53 / 30; p 0.061 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.002113 [-0.0003553, 0.004429]; median -0.0005905; 54 / 0 / 46; p 0.302 |
| sparse (n = 100) | 7 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.003481 [-0.008286, 0.001196]; median 0; 47 / 14 / 39; p 0.251 | -0.003573 [-0.008301, 0.001128]; median 0; 47 / 14 / 39; p 0.235 | -0.00346 [-0.006407, -0.0005472]; median -0.001396; 57 / 0 / 43; p 0.0504 | -0.004693 [-0.008462, -0.001059]; median -0.001843; 61 / 0 / 39; p 0.0421 |
| sparse (n = 100) | 7 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | run's own | 0.002455 [-0.0003598, 0.00528]; median 0; 16 / 55 / 29; p 0.0515 | 0.0023 [-0.0004607, 0.005088]; median 0; 16 / 55 / 29; p 0.0542 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.002888 [-2.264e-05, 0.005599]; median -0.0002394; 52 / 0 / 48; p 0.0591 |
| sparse (n = 100) | 7 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | run's own | 0.003651 [-0.002222, 0.009672]; median -0.0005291; 50 / 7 / 43; p 0.465 | 0.003491 [-0.002221, 0.009447]; median -0.0005291; 50 / 7 / 43; p 0.472 | -0.0002343 [-0.00393, 0.003495]; median -0.0004648; 53 / 0 / 47; p 0.687 | -0.0006242 [-0.005034, 0.003866]; median -0.00138; 54 / 0 / 46; p 0.564 |
| sparse (n = 100) | 30 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | run's own | 0.0002444 [-0.0016, 0.001983]; median 0; 41 / 29 / 30; p 0.634 | 0.0002222 [-0.001604, 0.001945]; median 0; 41 / 29 / 30; p 0.602 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.0008942 [-0.001063, 0.002826]; median -8.777e-05; 54 / 0 / 46; p 0.962 |
| sparse (n = 100) | 30 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.002914 [-0.007699, 0.001879]; median -0.002099; 54 / 5 / 41; p 0.164 | -0.00291 [-0.007618, 0.001895]; median -0.002099; 54 / 5 / 41; p 0.159 | -0.001518 [-0.004034, 0.001112]; median -0.0008983; 54 / 0 / 46; p 0.14 | -0.003378 [-0.007427, 0.0007786]; median -0.001694; 58 / 0 / 42; p 0.0256 |
| sparse (n = 100) | 30 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | run's own | 0.003217 [0.001284, 0.005247]; median 0; 14 / 51 / 35; p 0.00083 | 0.003148 [0.00122, 0.005172]; median 0; 14 / 51 / 35; p 0.00083 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.003174 [0.001227, 0.005334]; median -3.552e-05; 51 / 0 / 49; p 0.0439 |
| sparse (n = 100) | 30 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.004963 [-0.008528, -0.001672]; median -0.002469; 58 / 14 / 28; p 0.00646 | -0.00503 [-0.008597, -0.00174]; median -0.002469; 58 / 14 / 28; p 0.00605 | -0.003703 [-0.005544, -0.001893]; median -0.001953; 65 / 0 / 35; p 0.000162 | -0.004363 [-0.007244, -0.0017]; median -0.002113; 65 / 0 / 35; p 0.00257 |
| sparse (n = 100) | 30 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | run's own | 0.003146 [0.0008222, 0.00581]; median 0; 18 / 51 / 31; p 0.0272 | 0.002944 [0.0006801, 0.005467]; median 0; 18 / 51 / 31; p 0.0269 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.003632 [0.001519, 0.005975]; median 0.0003129; 43 / 0 / 57; p 0.012 |
| sparse (n = 100) | 30 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.001057 [-0.004909, 0.002728]; median -0.0001235; 50 / 8 / 42; p 0.47 | -0.001201 [-0.005037, 0.002551]; median -0.0001235; 50 / 8 / 42; p 0.459 | -0.001785 [-0.003794, 0.0002575]; median -0.001044; 56 / 0 / 44; p 0.0428 | -0.001962 [-0.005072, 0.001253]; median -0.0009481; 57 / 0 / 43; p 0.0695 |
| very_sparse (n = 100) | 7 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | run's own | 0.0004762 [-0.0002116, 0.001608]; median 0; 2 / 96 / 2; p 0.465 | 0.0004762 [-0.0002116, 0.001608]; median 0; 2 / 96 / 2; p 0.465 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.0001776 [-0.0004646, 0.001069]; median -0.0005765; 89 / 0 / 11; p 4.43e-08 |
| very_sparse (n = 100) | 7 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.002095 [-0.004296, -0.0002116]; median 0; 22 / 71 / 7; p 0.00444 | -0.002463 [-0.004508, -0.0007814]; median 0; 22 / 71 / 7; p 0.00105 | 1.44e-05 [-0.001461, 0.001489]; median 0.001836; 36 / 0 / 64; p 0.144 | -0.0006015 [-0.002671, 0.001259]; median 0.001836; 35 / 0 / 65; p 0.217 |
| very_sparse (n = 100) | 7 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | run's own | 0.0007407 [1.058e-05, 0.001862]; median 0; 0 / 96 / 4; p 0.0679 | 0.0007407 [1.058e-05, 0.001852]; median 0; 0 / 96 / 4; p 0.0679 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.0001181 [-0.0006164, 0.001207]; median -0.0005762; 90 / 0 / 10; p 1.14e-09 |
| very_sparse (n = 100) | 7 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.001577 [-0.003651, -7.407e-05]; median 0; 19 / 73 / 8; p 0.0486 | -0.001577 [-0.003672, -8.466e-05]; median 0; 19 / 73 / 8; p 0.0486 | -0.0002339 [-0.001623, 0.0009086]; median 0.00199; 34 / 0 / 66; p 0.08 | -0.0008536 [-0.003197, 0.0008217]; median 0.002168; 32 / 0 / 68; p 0.088 |
| very_sparse (n = 100) | 7 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | run's own | -8.466e-05 [-0.0004127, 0.0001587]; median 0; 1 / 98 / 1; p 0.655 | -8.466e-05 [-0.0004127, 0.0001587]; median 0; 1 / 98 / 1; p 0.655 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | -0.0002877 [-0.000924, 0.0003742]; median -0.0005785; 90 / 0 / 10; p 4.02e-08 |
| very_sparse (n = 100) | 7 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.002116 [-0.005026, 0.0001058]; median 0; 21 / 71 / 8; p 0.00972 | -0.002513 [-0.005386, -0.0005331]; median 0; 21 / 71 / 8; p 0.00273 | 0.0001462 [-0.001515, 0.00177]; median 0.001931; 36 / 0 / 64; p 0.134 | -0.0005703 [-0.003209, 0.001546]; median 0.001931; 35 / 0 / 65; p 0.245 |
| very_sparse (n = 100) | 30 | `chronos2_occurrence_model_size_count` | `chronos2_completed` | run's own | 0.0009556 [-5.926e-05, 0.002743]; median 0; 3 / 94 / 3; p 0.6 | 0.0009556 [-6.667e-05, 0.002751]; median 0; 3 / 94 / 3; p 0.6 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.0009314 [-0.0005198, 0.003537]; median -0.0005767; 88 / 0 / 12; p 3.45e-10 |
| very_sparse (n = 100) | 30 | `chronos2_occurrence_model_size_count` | `hurdle_count_28` | run's own | 1.481e-05 [-0.001124, 0.00138]; median 0; 21 / 69 / 10; p 0.136 | -0.0003991 [-0.001309, 0.0005821]; median 0; 21 / 69 / 10; p 0.081 | 0.001184 [2.667e-05, 0.002554]; median 0.00141; 38 / 0 / 62; p 0.00313 | 0.00116 [4.008e-06, 0.002457]; median 0.001603; 38 / 0 / 62; p 0.00313 |
| very_sparse (n = 100) | 30 | `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | run's own | 0.001667 [4.938e-05, 0.004723]; median 0; 0 / 96 / 4; p 0.0679 | 0.001667 [4.938e-05, 0.004612]; median 0; 0 / 96 / 4; p 0.0679 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.001123 [-0.0006415, 0.004335]; median -0.0005762; 92 / 0 / 8; p 8.18e-11 |
| very_sparse (n = 100) | 30 | `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.001442 [-0.003462, -0.0001877]; median 0; 20 / 70 / 10; p 0.023 | -0.001444 [-0.003474, -0.00019]; median 0; 20 / 70 / 10; p 0.023 | 0.0001231 [-0.001219, 0.001095]; median 0.001602; 36 / 0 / 64; p 0.00431 | -0.0003866 [-0.00292, 0.001156]; median 0.001602; 35 / 0 / 65; p 0.00211 |
| very_sparse (n = 100) | 30 | `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | run's own | 0.0004938 [-5.926e-05, 0.001506]; median 0; 1 / 96 / 3; p 0.465 | 0.0005216 [-1.888e-06, 0.001529]; median 0; 1 / 96 / 3; p 0.144 | 0 [0, 0]; median 0; 0 / 100 / 0; p 1 | 0.0003282 [-0.0005845, 0.001956]; median -0.0005773; 88 / 0 / 12; p 4.01e-11 |
| very_sparse (n = 100) | 30 | `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | run's own | -0.001195 [-0.003267, 0.0006099]; median 0; 23 / 71 / 6; p 0.00492 | -0.00172 [-0.00355, -0.0004895]; median 0; 23 / 71 / 6; p 0.00198 | 0.0004946 [-0.0008913, 0.001995]; median 0.001041; 39 / 0 / 61; p 0.0152 | -0.0001947 [-0.002673, 0.001741]; median 0.001007; 41 / 0 / 59; p 0.0384 |

### NYC 311: the point methods, QScore9 (compact cells)

A point mass is a poor probabilistic forecast by construction. Under it QScore9 is the absolute error of the rounded point, so these rows say how the field's point methods fare under this score, not how good they are as point forecasts.

| Group | h | Reference | `croston_classic` | `croston_sba` | `adida` |
|---|---|---|---|---|---|
| all (n = 300) | 7 | `chronos2_completed` | 0.6425 / 0.06772 (19 / 102 / 179) | 0.6023 / 0.0619 (19 / 102 / 179) | 0.33 / 0.0619 (17 / 104 / 179) |
| all (n = 300) | 7 | `timesfm3_completed` | 0.6454 / 0.07725 (32 / 82 / 186) | 0.6052 / 0.06825 (32 / 82 / 186) | 0.3328 / 0.06561 (33 / 84 / 183) |
| all (n = 300) | 7 | `timesfm2p5_completed` | 0.6442 / 0.06243 (12 / 113 / 175) | 0.6041 / 0.05926 (12 / 113 / 175) | 0.3317 / 0.05714 (13 / 115 / 172) |
| all (n = 300) | 7 | `hurdle_count_28` | 0.5277 / 0.06825 (40 / 73 / 187) | 0.4875 / 0.05926 (41 / 73 / 186) | 0.2151 / 0.05503 (42 / 75 / 183) |
| all (n = 300) | 7 | `dynamic_count` | 0.5332 / 0.06243 (26 / 90 / 184) | 0.4931 / 0.06032 (26 / 90 / 184) | 0.2207 / 0.05556 (29 / 92 / 179) |
| all (n = 300) | 7 | `tsb_hurdle` | 0.5367 / 0.0836 (33 / 74 / 193) | 0.4965 / 0.06614 (33 / 74 / 193) | 0.2241 / 0.0582 (34 / 76 / 190) |
| all (n = 300) | 30 | `chronos2_completed` | 0.6486 / 0.0642 (19 / 94 / 187) | 0.6083 / 0.06272 (19 / 94 / 187) | 0.3338 / 0.06185 (18 / 96 / 186) |
| all (n = 300) | 30 | `timesfm3_completed` | 0.653 / 0.07728 (31 / 73 / 196) | 0.6127 / 0.07086 (31 / 73 / 196) | 0.3382 / 0.06741 (32 / 75 / 193) |
| all (n = 300) | 30 | `timesfm2p5_completed` | 0.6497 / 0.07741 (12 / 102 / 186) | 0.6094 / 0.06481 (12 / 102 / 186) | 0.3349 / 0.06481 (12 / 103 / 185) |
| all (n = 300) | 30 | `hurdle_count_28` | 0.5289 / 0.08272 (36 / 80 / 184) | 0.4886 / 0.06543 (36 / 80 / 184) | 0.2141 / 0.05926 (36 / 82 / 182) |
| all (n = 300) | 30 | `dynamic_count` | 0.5405 / 0.06296 (16 / 100 / 184) | 0.5002 / 0.06173 (16 / 100 / 184) | 0.2257 / 0.06049 (17 / 101 / 182) |
| all (n = 300) | 30 | `tsb_hurdle` | 0.534 / 0.07901 (30 / 81 / 189) | 0.4937 / 0.06914 (30 / 81 / 189) | 0.2192 / 0.06049 (30 / 82 / 188) |
| dense (n = 100) | 7 | `chronos2_completed` | 0.8657 / 0.5317 (0 / 0 / 100) | 0.8076 / 0.4915 (0 / 0 / 100) | 0.8524 / 0.5148 (0 / 0 / 100) |
| dense (n = 100) | 7 | `timesfm3_completed` | 0.8718 / 0.5386 (0 / 0 / 100) | 0.8137 / 0.4937 (0 / 0 / 100) | 0.8585 / 0.5005 (1 / 0 / 99) |
| dense (n = 100) | 7 | `timesfm2p5_completed` | 0.8751 / 0.5317 (0 / 0 / 100) | 0.817 / 0.5063 (0 / 0 / 100) | 0.8617 / 0.4915 (1 / 0 / 99) |
| dense (n = 100) | 7 | `hurdle_count_28` | 0.5263 / 0.4122 (0 / 0 / 100) | 0.4682 / 0.3788 (0 / 0 / 100) | 0.5129 / 0.3667 (3 / 0 / 97) |
| dense (n = 100) | 7 | `dynamic_count` | 0.5396 / 0.418 (2 / 0 / 98) | 0.4815 / 0.363 (2 / 0 / 98) | 0.5263 / 0.3751 (4 / 0 / 96) |
| dense (n = 100) | 7 | `tsb_hurdle` | 0.5554 / 0.4101 (0 / 0 / 100) | 0.4973 / 0.3942 (0 / 0 / 100) | 0.5421 / 0.3942 (3 / 0 / 97) |
| dense (n = 100) | 30 | `chronos2_completed` | 0.8948 / 0.5519 (0 / 0 / 100) | 0.8337 / 0.4822 (0 / 0 / 100) | 0.8762 / 0.53 (0 / 0 / 100) |
| dense (n = 100) | 30 | `timesfm3_completed` | 0.9007 / 0.5121 (0 / 0 / 100) | 0.8396 / 0.4805 (0 / 0 / 100) | 0.8821 / 0.5017 (1 / 0 / 99) |
| dense (n = 100) | 30 | `timesfm2p5_completed` | 0.8963 / 0.5365 (0 / 0 / 100) | 0.8351 / 0.4831 (0 / 0 / 100) | 0.8776 / 0.5115 (0 / 0 / 100) |
| dense (n = 100) | 30 | `hurdle_count_28` | 0.5398 / 0.4037 (0 / 0 / 100) | 0.4787 / 0.384 (0 / 0 / 100) | 0.5212 / 0.3864 (1 / 0 / 99) |
| dense (n = 100) | 30 | `dynamic_count` | 0.5708 / 0.4074 (2 / 0 / 98) | 0.5097 / 0.3889 (2 / 0 / 98) | 0.5522 / 0.3901 (2 / 0 / 98) |
| dense (n = 100) | 30 | `tsb_hurdle` | 0.5562 / 0.4025 (0 / 0 / 100) | 0.4951 / 0.379 (0 / 0 / 100) | 0.5375 / 0.4025 (1 / 0 / 99) |
| sparse (n = 100) | 7 | `chronos2_completed` | 0.1264 / 0.05503 (17 / 13 / 70) | 0.114 / 0.05503 (17 / 13 / 70) | 0.1245 / 0.05503 (16 / 13 / 71) |
| sparse (n = 100) | 7 | `timesfm3_completed` | 0.1292 / 0.06032 (22 / 4 / 74) | 0.1168 / 0.0582 (22 / 4 / 74) | 0.1273 / 0.06032 (23 / 4 / 73) |
| sparse (n = 100) | 7 | `timesfm2p5_completed` | 0.1228 / 0.0545 (12 / 21 / 67) | 0.1104 / 0.04497 (12 / 21 / 67) | 0.1209 / 0.05397 (12 / 22 / 66) |
| sparse (n = 100) | 7 | `hurdle_count_28` | 0.124 / 0.05503 (22 / 5 / 73) | 0.1116 / 0.04974 (23 / 5 / 72) | 0.1221 / 0.05397 (22 / 5 / 73) |
| sparse (n = 100) | 7 | `dynamic_count` | 0.1278 / 0.06032 (17 / 5 / 78) | 0.1154 / 0.05873 (17 / 5 / 78) | 0.1259 / 0.05873 (18 / 5 / 77) |
| sparse (n = 100) | 7 | `tsb_hurdle` | 0.1208 / 0.0582 (18 / 4 / 78) | 0.1084 / 0.05344 (18 / 4 / 78) | 0.1189 / 0.05344 (17 / 4 / 79) |
| sparse (n = 100) | 30 | `chronos2_completed` | 0.117 / 0.05 (11 / 11 / 78) | 0.1072 / 0.05 (11 / 11 / 78) | 0.1146 / 0.05469 (11 / 11 / 78) |
| sparse (n = 100) | 30 | `timesfm3_completed` | 0.122 / 0.06086 (12 / 5 / 83) | 0.1123 / 0.05877 (12 / 5 / 83) | 0.1196 / 0.06136 (12 / 5 / 83) |
| sparse (n = 100) | 30 | `timesfm2p5_completed` | 0.1181 / 0.05247 (9 / 14 / 77) | 0.1083 / 0.04914 (9 / 14 / 77) | 0.1156 / 0.05247 (9 / 14 / 77) |
| sparse (n = 100) | 30 | `hurdle_count_28` | 0.1139 / 0.05432 (15 / 9 / 76) | 0.1041 / 0.05309 (15 / 9 / 76) | 0.1114 / 0.05556 (15 / 9 / 76) |
| sparse (n = 100) | 30 | `dynamic_count` | 0.1182 / 0.06049 (9 / 13 / 78) | 0.1084 / 0.05802 (9 / 13 / 78) | 0.1157 / 0.06049 (9 / 13 / 78) |
| sparse (n = 100) | 30 | `tsb_hurdle` | 0.1124 / 0.05556 (11 / 9 / 80) | 0.1026 / 0.05309 (11 / 9 / 80) | 0.1099 / 0.05556 (10 / 9 / 81) |
| very_sparse (n = 100) | 7 | `chronos2_completed` | 0.9354 / 0 (2 / 89 / 9) | 0.8854 / 0 (2 / 89 / 9) | 0.01298 / 0 (1 / 91 / 8) |
| very_sparse (n = 100) | 7 | `timesfm3_completed` | 0.9351 / 0 (10 / 78 / 12) | 0.8851 / 0 (10 / 78 / 12) | 0.01273 / 0 (9 / 80 / 11) |
| very_sparse (n = 100) | 7 | `timesfm2p5_completed` | 0.9348 / 0 (0 / 92 / 8) | 0.8848 / 0 (0 / 92 / 8) | 0.01244 / 0 (0 / 93 / 7) |
| very_sparse (n = 100) | 7 | `hurdle_count_28` | 0.9328 / 0 (18 / 68 / 14) | 0.8828 / 0 (18 / 68 / 14) | 0.01041 / 0 (17 / 70 / 13) |
| very_sparse (n = 100) | 7 | `dynamic_count` | 0.9323 / 0 (7 / 85 / 8) | 0.8823 / 0 (7 / 85 / 8) | 0.009958 / 0 (7 / 87 / 6) |
| very_sparse (n = 100) | 7 | `tsb_hurdle` | 0.9338 / 0 (15 / 70 / 15) | 0.8838 / 0 (15 / 70 / 15) | 0.01145 / 0 (14 / 72 / 14) |
| very_sparse (n = 100) | 30 | `chronos2_completed` | 0.934 / 0 (8 / 83 / 9) | 0.884 / 0 (8 / 83 / 9) | 0.01064 / 0 (7 / 85 / 8) |
| very_sparse (n = 100) | 30 | `timesfm3_completed` | 0.9361 / 0 (19 / 68 / 13) | 0.8861 / 0 (19 / 68 / 13) | 0.01281 / 0 (19 / 70 / 11) |
| very_sparse (n = 100) | 30 | `timesfm2p5_completed` | 0.9347 / 0 (3 / 88 / 9) | 0.8847 / 0 (3 / 88 / 9) | 0.01139 / 0 (3 / 89 / 8) |
| very_sparse (n = 100) | 30 | `hurdle_count_28` | 0.933 / 0 (21 / 71 / 8) | 0.883 / 0 (21 / 71 / 8) | 0.009704 / 0 (20 / 73 / 7) |
| very_sparse (n = 100) | 30 | `dynamic_count` | 0.9325 / 0 (5 / 87 / 8) | 0.8825 / 0 (5 / 87 / 8) | 0.00921 / 0 (6 / 88 / 6) |
| very_sparse (n = 100) | 30 | `tsb_hurdle` | 0.9335 / 0 (19 / 72 / 9) | 0.8835 / 0 (19 / 72 / 9) | 0.01015 / 0 (19 / 73 / 8) |

### NYC 311: occurrence descriptors

| Group | h | Windows | All-zero contexts | Positive target days | TSB p (0.05 / 0.1 / 0.2) | Jeffreys p | `dynamic_count` p | Completed 1 − F(0) (chronos2 / timesfm3 / timesfm2p5) | Days with every decile at zero (chronos2 / timesfm3 / timesfm2p5) |
|---|---|---|---|---|---|---|---|---|---|
| all (n = 300) | 7 | 900 | 52 | 0.368 | 0.369 / 0.369 / 0.367 | 0.378 | 0.363 | 0.356 / 0.386 / 0.371 | 0.398 / 0.330 / 0.433 |
| all (n = 300) | 30 | 900 | 52 | 0.369 | 0.369 / 0.369 / 0.367 | 0.378 | 0.363 | 0.355 / 0.387 / 0.374 | 0.392 / 0.316 / 0.403 |
| dense (n = 100) | 7 | 300 | 0 | 0.789 | 0.798 / 0.795 / 0.790 | 0.790 | 0.791 | 0.765 / 0.791 / 0.789 | 0.000 / 0.000 / 0.000 |
| dense (n = 100) | 30 | 300 | 0 | 0.783 | 0.798 / 0.795 / 0.790 | 0.790 | 0.791 | 0.760 / 0.789 / 0.787 | 0.000 / 0.000 / 0.000 |
| sparse (n = 100) | 7 | 300 | 0 | 0.275 | 0.275 / 0.278 / 0.275 | 0.290 | 0.258 | 0.236 / 0.291 / 0.255 | 0.234 / 0.097 / 0.324 |
| sparse (n = 100) | 30 | 300 | 0 | 0.284 | 0.275 / 0.278 / 0.275 | 0.290 | 0.258 | 0.237 / 0.295 / 0.266 | 0.226 / 0.084 / 0.249 |
| very_sparse (n = 100) | 7 | 300 | 52 | 0.040 | 0.034 / 0.036 / 0.035 | 0.052 | 0.040 | 0.068 / 0.075 / 0.068 | 0.959 / 0.893 / 0.976 |
| very_sparse (n = 100) | 30 | 300 | 52 | 0.039 | 0.034 / 0.036 / 0.035 | 0.052 | 0.040 | 0.069 / 0.077 / 0.070 | 0.950 / 0.863 / 0.960 |

## What this does not show

- No test. Every p-value here is raw and descriptive. No row is confirmatory, and the registered families and
  their conclusions are unchanged.
- No other method. Only the TSB constants fixed in the specification were run, and no other was tried. iETS,
  the Willemain bootstrap and an estimated TSB constant were not run.
- No new grid of origins. The forecasts are judged on the registered windows, with the registered sampling
  strata as regimes, and the strata are frozen on the context.
- The point methods are scored under probabilistic scores, which is not how they are judged as point forecasts.
- The npm data are as served. The three source zero days of dated addition 6 are in the npm targets and later
  contexts, as in the registered analysis.

## Provenance and regeneration

From the repository root, into a new directory:

```
.\.venv\Scripts\python.exe reports\study2-posthoc-intermittent-baselines\intermittent_baselines.py --npm reports\study2-npm\run-2026-10-15 --grid reports\study2-synthetic-2026-10-15 --nyc311 reports\study3-nyc311\run-2026-10-17 --out <new directory> --workers 6
```

The command needs the 1,049 checkpoints, which stay out of the tree, the npm and NYC 311 target signals and
contexts under `data/raw/`, and `statsforecast` 2.1.1. Without `--workers` it runs in one process with the same
outputs. It refuses to run if `SPEC.md` differs from the hash above, and refuses to overwrite an output.
`provenance.json` records:

- the specification's and the script's hashes, and the hashes of the project code it imports;
- for each run, the hash of `run.json` and of every checkpoint as `run.json` records it;
- the readiness entries for the signals, contexts, manifests, selections and completeness documents, each
  with its hash;
- the declarations, the inference files read and the grid manifest;
- the hash of every output, the packages (NumPy 2.5.3, pandas 2.3.3, SciPy 1.18.1, `statsforecast` 2.1.1) and
  the HEAD at the run (`2bae238`, with no uncommitted change under `scripts/` or `pulsegraph/`).

| File | SHA-256 |
|---|---|
| `SPEC.md` | `ca645c02a2576cff174d42a4d2d2089242423d32063ea1cdad39078168687532` |
| `intermittent_baselines.py` | `bb869f1a11fdbf836526584cfd34520ff520b7f7735a3d3f738e4662ce128f6e` |
| `provenance.json` | `43dc95813b1f9befb8faff5fbdd4663f7db91310ce903df4cb89d629f9759c1e` |
| `npm_window_scores.csv` | `601f4d9d6f08bfa7e34d6b272a391374d6971aa02a65c09f4d09bf66d6ef5a02` |
| `npm_contrasts.csv` | `4d5817fcada4d956834c6e6b49473eed9e00d2868cb73524f6955803bb8dc8ee` |
| `npm_occurrence.csv` | `57af6e1ed254783362714f094c00e65bfc22ad54fc77c8b0e39d5674d9838ae9` |
| `grid_window_scores.csv` | `36935492d220b13ec0ce4d2db4bac735031388ecd9826f26368677eda472813d` |
| `grid_contrasts.csv` | `9666fb43585ab4910a19e9ba3a4b516cab39f135f8a68185d6d9dedcd245c836` |
| `grid_occurrence.csv` | `debbec54c7d1ee6f9f96b1503587e39fb420e046263c6d2594ee21c1dbf5c000` |
| `nyc311_window_scores.csv` | `75757cbdb18938b3773b396c0247350cdcc95fdc8d45f674a3170418a3e83fef` |
| `nyc311_contrasts.csv` | `b2e243632aeb7561216af55485156f55d648d438bcbcf491c033200ba4a30dbc` |
| `nyc311_occurrence.csv` | `2c54e92a8a3c6e7bed37e7ca6c28306eb34fe9d451fdd9191404a0b20207c0d0` |

The registered fixed-hurdle rows cited in the reading are the runs' own secondaries:
`reports/study2-npm/run-2026-10-15/inference/secondary_strata_contrasts.csv` (rows E01, E04, E07, E10, E13
and E16 per stratum) and `reports/study2-synthetic-2026-10-15/inference/inference.csv` (S01, S03, S05) with
`secondary_contrasts.csv` (S01-h7, S03-h7, S05-h7).

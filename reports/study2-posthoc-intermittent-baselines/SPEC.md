# Post-hoc specification: intermittent-demand baselines and the fourth factorial cell, from the saved forecasts

Fixed 2026-10-17 07:44 UTC, before any score of the forecasts defined here was computed. The registered
scores of all three runs had been seen and published: the npm external run
(`reports/study2-npm/run-2026-10-15/`), the synthetic grid run (`reports/study2-synthetic-2026-10-15/`) and
the Study 3 run on NYC 311 (`reports/study3-nyc311/run-2026-10-17/`). Everything below is **post hoc and
descriptive**. It adds no test to any registered family (E01 to E18, S01 to S06, R01 to R36), applies no
multiplicity correction, carries no verdict column and replaces nothing registered. The SHA-256 of this file
is recorded before the first score is computed, and this file does not change afterwards. Nothing is selected
after scores are seen: no smoothing constant, forecast, reference, group, horizon or score is added, dropped or
altered. A defect found in the script after scoring is fixed in the script, and the results page states the
fix and its effect; this file stays as written.

## Inputs, read only

- **The checkpoints.** The 209 npm, 540 grid and 300 NYC 311 whole-series checkpoints, each checked against
  the SHA-256 its run's `run.json` records. Each run is read by its registered inference reader (`read_run`
  in `scripts/study2_inference.py` for npm and the grid, in `scripts/study3_inference.py` for NYC 311):
  complete, its identity, authorized for its committed family and specification, every row on the registered
  grid. The two inference scripts must be byte for byte the ones each run's `inference/provenance.json`
  records, and the saved scores passed through the registered functions must reproduce each run's
  `inference/inference.csv` and `inference/paired_entities.csv` byte for byte.
- **The contexts.** npm and NYC 311: the run's own loader, `pulsegraph.study2.runner.external_dataset`, on
  the readiness record saved in `run.json`. It reads `signals.parquet` only through the verified completeness
  document of the target pull, checks every file against the SHA-256 the readiness record names, and checks
  that each series' prefix reproduces the frozen `context.parquet`. The context of a window is every day
  before its cutoff (275, 305 or 335 days). The grid: the registered generator,
  `pulsegraph.study2.synthetic.grid_dataset`, checked against the committed `study/study2/grid_manifest.json`;
  the context is the first 180, 210 or 240 values. The npm data are as served: the three source zero days of
  dated addition 6 stay in, as in the registered analysis.
- **The check before any score.** In every window, the rebuilt context's mean must equal the saved
  `context_mean` exactly, the rebuilt target must equal the saved target, and
  `pulsegraph.study2.models.count_laws` on the rebuilt context must reproduce the saved `hurdle_count_28` and
  `dynamic_count` laws exactly. On NYC 311 the saved `<model>_occurrence_model_size_count` laws must equal the
  ones rebuilt from the saved completed and `hurdle_count_28` laws. Any failure stops the script before
  anything is written.

## The forecasts

All are built from the context through the origin alone, flat over the horizon, and never fitted to a target.
Names in parentheses are the names used in every output.

### 1. The TSB hurdle, the primary descriptive baseline (`tsb_hurdle`)

TSB (Teunter, Syntetos and Babai, 2011) smooths the occurrence indicator on every day and the demand size on
demand days only. For a context y_1, ..., y_T, with d_t = 1[y_t > 0] and s_1, ..., s_m the positive values in
time order:

- occurrence level: p_1 = d_1 and p_t = a_p d_t + (1 - a_p) p_(t-1) for t = 2, ..., T;
- size level: z_1 = s_1 and z_j = a_z s_j + (1 - a_z) z_(j-1) for j = 2, ..., m.

The initialization is `statsforecast` 2.1.1's: simple exponential smoothing starts its level at the first
value of the sequence it smooths, the occurrence indicators of every context day for p and the positive values
alone for z. At every lead l = 1, ..., h the forecast holds the origin values (TSB's forecast is flat):
P(Y > 0) = p_T, size level z_m, point forecast p_T z_m.

The law, for every target day: H(0) = 1 - p_T and H(k) = 1 - p_T + p_T G(k) for k >= 1, where G is the law of
1 + Poisson(lambda) with lambda = max(0, z_m - 1). This is the positive law `hurdle_count_28` builds
(1 + Poisson(mean(y - 1)) over the last 28 days' positive values; `PROTOCOL.md`, "Models, distributions and
controls"), with the TSB size level z_m in place of the 28-day positive mean; lambda = 0 is a point mass at
one, as registered. The saved form is the registered count hurdle, `{"kind": "hurdle", "p": p_T,
"positive": {"kind": "poisson", "mu": lambda, "shift": 1}, "fallback": null}`. The TSB hurdle therefore
differs from `hurdle_count_28` in its occurrence estimate and its size estimate and in nothing else. Two
consequences of TSB's size estimate are part of that difference: it is defined from a single positive context
day (the registered rule of delta_1 with fewer than two positive days in the last 28 does not apply), and its
memory is not limited to 28 days. A context with no positive day gives p_T = 0 and no size level; the law is a
point mass at zero, saved as `{"kind": "hurdle", "p": 0.0, "positive": {"kind": "point", "value": 1},
"fallback": "no_positive_context_day"}`, and `statsforecast`'s TSB forecast is 0 there too.

Smoothing constants fixed here: (a_p, a_z) = (0.1, 0.1) for `tsb_hurdle`; the declared sensitivities are
(0.05, 0.05), named `tsb_hurdle_a005`, and (0.2, 0.2), named `tsb_hurdle_a020`.

`statsforecast`'s `TSB` returns only the product p_T z_m, so the script implements both recursions itself. In
every window and for each pair of constants, p_T z_m must equal `statsforecast.models.TSB(alpha_d=a_z,
alpha_p=a_p).forecast(y, h)["mean"]` at every lead within a relative 1e-12 (an absolute 1e-12 where the
forecast is 0), or the script stops.

### 2. The point methods of the field (`croston_classic`, `croston_sba`, `adida`), one secondary table

`statsforecast` 2.1.1's `CrostonClassic()`, `CrostonSBA()` and `ADIDA()`, each with its defaults, called as
`.forecast(y=context, h=horizon)["mean"]` on the full context: Croston's method smooths the positive sizes and
the intervals between them with constant 0.1 and forecasts their ratio; SBA multiplies that by 0.95; ADIDA
sums the context in non-overlapping buckets whose length is the mean inter-demand interval rounded, aligned to
end at the origin (the oldest incomplete bucket is dropped), smooths the bucket sums with a constant chosen on
[0.1, 0.3] by `statsforecast`'s golden-section search, and divides by the bucket length. Each forecast is
flat; an all-zero context gives 0. Each is scored as a degenerate law at the rounded point c = floor(f + 0.5) (the
completion's half-up integer mapping), saved as `{"kind": "point", "value": c}`.

A degenerate law is a poor probabilistic forecast by construction: it puts probability one on one count, so
every proper score penalizes it on each day the target differs from c. Under it, QScore9 and the discrete CRPS
both equal |y - c| on each day and the occurrence Brier score is (1[c > 0] - 1[y > 0])^2. The table says how
the field's point methods fare under this study's scores. It does not judge them as point forecasts.

### 3. The fourth factorial cell on npm and the grid (`<model>_occurrence_model_size_count`)

For each foundation model, each saved window and each target day:
`pulsegraph.study2.models.model_size_count(CountLaw(saved completed law), saved hurdle_count_28 law)`, exactly
as `study3_variants` builds the Study 3 variant (`PROTOCOL.md`, dated addition 7). Its occurrence is the
model's own 1 - F(0) of its saved completed law for that day; its positive law is `hurdle_count_28`'s for the
window, 1 + Poisson(mean(y - 1)) over the last 28 context days' positive values, with the registered delta_1
when fewer than two of them exist, the fallback recorded. Nothing else enters. On NYC 311 the run saved this
variant; its contrasts are the run's own declared secondaries and are read, not recomputed (below).

### Scores

Every new forecast's deciles come from the registered inversion (`pulsegraph.study2.models.law_forecast`), and
every score from the registered scorer the run used, `pulsegraph.study2.scores.score(target, forecast,
context)`: QScore9 over all nine deciles and all target days; the context-scaled QScore9, QScore9 / max(1,
mean(context)); the occurrence Brier score, the mean over target days of (P(Y > 0) - 1[y > 0])^2; and the
discrete CRPS, available only when its residual bound is certified below 1e-8 by k = 1,000,000 on every day of
the window (dated addition 5). Every reference's scores are the run's saved scores.

## The contrasts

Every difference is variant minus reference; all four scores are losses, so a negative difference favors the
variant. Each contrast is computed for each panel, group, horizon (7 and 30) and score (QScore9, the
context-scaled QScore9, the occurrence Brier score, the discrete CRPS where both laws are certified).

- **The TSB hurdle** (`tsb_hurdle`, and each sensitivity) against: each model's completed control
  (`<model>_completed`, three); each model's registered fixed hurdle (`<model>_hurdle`, three); on NYC 311 each
  model's `<model>_hurdle_dynamic` (three); `hurdle_count_28`; `dynamic_count`. That is 8 references on npm and
  the grid and 11 on NYC 311.
- **The fourth cell** (npm and the grid) against the model's completed control, which differs from it in the
  positive law alone, and against `hurdle_count_28`, which differs from it in the occurrence alone. On NYC 311
  the same two contrasts are the run's registered secondaries: read from the run's
  `inference/secondary_strata_contrasts.csv` (the three strata) and `inference/secondary_pooled_contrasts.csv`
  (all 300), each file checked against the SHA-256 the run's `inference/provenance.json` records, shown in
  the same table and marked as the run's own (their seeds are the run's, root 20261004).
- **The point methods** against: each model's completed control (three), `hurdle_count_28`, `dynamic_count`
  and `tsb_hurdle`.

The groups:

- **npm:** the strata dense (100 series), sparse (100) and very sparse (9), and all 209 series. The very
  sparse stratum is reported but marked as below the ten-series rule (Study 3's rule for a testable stratum).
- **NYC 311:** the strata dense, sparse and very sparse (100 series each), and all 300.
- **The grid:** each of the 18 cells (30 series, one per replicate) and the grid pooled.

## The aggregation

The registered one, through the functions of `scripts/study2_inference.py` imported unchanged:

- origins averaged within series and horizon (`series_scores`; a series' score is undefined when any of its
  windows is undefined);
- within a stratum, a cell or all series of npm or NYC 311, the series are the entities and weigh equally;
- the grid pooled: origins within replicate and cell, then the 18 cells within replicate with equal weight,
  the 30 replicate blocks as entities (`entity_scores`, as for S01 to S06);
- a contrast uses the entities where both sides are defined, and reports how many are not.

For each contrast: n; the variant's and the reference's means; the mean difference with a pointwise 95%
percentile interval from 20,000 entity bootstrap replicates; the median difference; the counts of entities
lower, tied and higher; the raw p of the two-sided approximate Wilcoxon signed-rank test over the entity
differences with zero differences omitted and p = 1 when every difference is zero. The interval and the test
are `cluster_contrast` of `scripts/study2_inference.py` with the registered family settings (20,000
replicates drawn in blocks of 256, NumPy's linear quantile, zero method "wilcox", method "approx",
two-sided). The sign of the median is reported as negative, positive or zero; **a zero median has no sign.**
No BH correction, no rejection or verdict column, no test added to any family.

**Seeds.** Root 20261017. Each contrast's bootstrap seed is `pulsegraph.random.derived_seed(20261017, panel,
id, group, variant, reference, horizon, metric)`, the inference commands' SHA-256 derivation with the panel
(`npm`, `grid` or `nyc311`) in the place of the component and the group (a stratum, a cell or `all`) in the
place of the domain; the id is `<group>/<variant>/<reference>/h<horizon>`, the form of the Study 3 secondary
rows. The generator is `numpy.random.default_rng(seed)`.

## Descriptors, no contrast

Per panel, group and horizon: the number of windows; the mean occurrence probability of each TSB hurdle, of
`hurdle_count_28` (the Jeffreys estimate), of `dynamic_count`, and of each model's completed law (1 - F(0),
averaged over target days); the share of target days on which each model's completed law has all nine deciles
at zero; the windows whose context has no positive day; the mean fraction of positive target days.

## Outputs

Beside the script, refusing to overwrite: for each panel `<panel>_window_scores.csv` (one row per window and
new forecast, with its scores, accounting parts and fitted levels), `<panel>_contrasts.csv` (every contrast
row, the NYC 311 fourth-cell rows marked as the run's own) and `<panel>_occurrence.csv` (the descriptors); and
`provenance.json` with the SHA-256 of every input (each checkpoint against its `run.json`, the signals, the
contexts, the manifests, the declarations, the inference files read), of every output, of this file and of
the script, and the regeneration command. The page `RESULTS-intermittent-baselines.md` says "post hoc" in its
title and gives this file's SHA-256 and the time it was fixed in its first sentence. It prints, with n in
every table and both summaries wherever either appears: every contrast of `tsb_hurdle` under all four scores
(the grid pooled in full, the grid's cells in compact form); the sensitivities and the point methods under
QScore9 in compact form; every fourth-cell contrast under all four scores (the grid's cells under QScore9 in
compact form), beside NYC 311's own rows; the descriptors. Every other number is in the CSVs.

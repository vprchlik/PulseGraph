# Review of the Study 2 run path before the first target evaluation

Written 2026-10-15 11:15 UTC against commit `03f08b3`, with the tree clean. The review reads the Study 2
implementation line by line against the registered text (`PROTOCOL.md`: the Study 2 addition of 2026-09-14 and
the dated additions of 2026-10-12 and 2026-10-15), before any npm target day of 2026-06-03 to 2026-08-31 is
requested and before the synthetic grid is scored. It opened no target value, made no network request and used
no GPU. Its evidence is the code at that commit, the committed declarations under `study/study2/`, the frozen
npm panel (`reports/study2-npm/panel/`, `study/study2/npm_panel_status.json`), the offline tests, and CPU-only
probes of the distribution code on stand-in laws at the scale of the largest npm series. The rule of Study 1
applies: a suspiciously good result is a bug until proven otherwise, so the first question at every step was
whether a target day could reach a model, a transformation, a selection or a fallback, and whether any choice
is left to be made after a score is visible.

The offline suite for Study 2 passes at this commit (138 tests across the nine `tests/test_study2_*.py` files,
run with `.\.venv\Scripts\python.exe -m pytest tests\test_study2_*.py -q --basetemp=data\cache\review2-tmp
-p no:cacheprovider`).

## The verdicts

### 1. The information boundary: holds

Every model input at a cutoff is the frozen context prefix and nothing else.

- The run slices each series at the cutoff before anything sees it: `pulsegraph/study2/runner.py:78` takes
  the days before the cutoff as context and `runner.py:79-86` the thirty days from the cutoff as target; the
  model pool receives only the context (`runner.py:90`), and the scorer receives the context only for the
  secondary scaled score (`runner.py:108`, `pulsegraph/study2/scores.py:68`).
- The Jeffreys occurrence estimate reads the last 28 context days (`pulsegraph/study2/models.py:31-32`); the
  two count hurdles read the positive values among those 28 days (`models.py:39-40, 46-63`); the dynamic count
  runs its discounted recursion over every context observation as the protocol registers it and falls back on
  fewer than two positives in the last 28 context days (`models.py:64-66`). The FM hurdle's occurrence
  probability comes from the same 28 context days (`models.py:114-121`).
- The completion of the nine deciles uses the deciles alone (`pulsegraph/study2/distributions.py:106-118`), and
  the FM hurdle is built from the completed law and the context occurrence (`distributions.py:121-136`).
- Strata and zero fractions are frozen in the manifest from the context window that ends 2026-06-02
  (`pulsegraph/study2/ingestion.py` `build_panel`; the manifest's 209 entries carry `stratum` and
  `zero_fraction`), and the run writes no stratum: any per-stratum table at inference reads the manifest.
- The forecast seeds are derived from the registered root, the model name, the series key, the horizon and the
  context values (`models.py:147-149`), never from a target.
- The signals that hold the targets cannot rewrite the frozen context: `runner.py:33-39` requires the
  2025-09-01 to 2026-06-02 prefix of the run signals to equal the frozen context parquet, and
  `ingestion.py:737` makes the same check when the target snapshot is written.
- The leakage tests cover the run path as it stands. `tests/test_study2_leakage.py:11-45` perturbs, permutes
  and extends every series on and after each of the three cutoffs and asserts, with an observed-date spy,
  that every context the pool sees lies before the cutoff and that forecasts and scales are unchanged;
  `test_study2_leakage.py:48-75` asserts that run signals cannot change the selection context;
  `tests/test_study2_packages.py:447-463` asserts that the target fetch refuses any window other than
  2026-06-03 to 2026-08-31 and any series outside the frozen manifest, and that the selection endpoint refuses
  target days; `test_study2_packages.py:349-388` asserts that a real pull requests exactly that window for
  exactly the manifest series and that `external_dataset` reads its output.

### 2. The registered formulas: holds with this fix

Each formula was checked against the protocol text, and a CPU probe confirmed the CDF, inversion and tail
behaviour of each law at the scale of the largest npm series (see 8).

- Completion: `distributions.py:106-118` builds the law from nine finite, nonnegative, nondecreasing deciles
  with tail scale max(1, q0.9 minus q0.8). The survival function at `distributions.py:28-39` is
  P(Q(U) >= k + 0.5): linear interpolation through (0, 0) and the nine knots for u up to 0.9, with
  `searchsorted` placing x = k + 0.5 so that a flat segment becomes an atom (the plateau test at
  `tests/test_study2_distributions.py:10-26`), and the exponential tail 0.1 exp(-(x - q0.9)/s) above the last
  knot. That is the right-continuous CDF of Y = floor(Q(U) + 0.5). Quantiles come from a deterministic bisection
  on the survival function (`distributions.py:50-68`), not from sampling.
- FM hurdle: `distributions.py:121-136` takes G+ from the completed law whenever F(0) < 1 and delta_1 only when
  F(0) = 1, recording that condition; because the exponential tail always leaves mass above zero, the delta_1
  case cannot arise for a completed law, and the fewer-than-two-positives rule is never applied to it
  (`tests/test_study2_distributions.py:29-38`). The quantile rule (zero for tau at most 1 minus p, otherwise the
  inverse of G+ at (tau minus 1 plus p)/p) is what the bisection on H(k) = 1 minus p plus p G+(k) returns.
- Count hurdles: Jeffreys p = (n_positive + 1/2)/29; the parametric positive law is 1 + Poisson(mean(Y minus 1))
  over the positive values of the last 28 days, the empirical law gives those values equal mass, and both use
  delta_1 under two positives with the occurrence estimate unchanged (`models.py:46-63`). A zero lambda is a
  point mass at one through Poisson(0).
- Dynamic count: the four parameters start at 0.5, every context observation first discounts all four by 0.98
  and then updates them, occurrence is a_B/(a_B + b_B), and lead l uses 1 + NB(shape 0.98^(l-1) a_P,
  probability 0.98^(l-1) b_P/(1 + 0.98^(l-1) b_P)) with scipy's parameterization, which is the Gamma-Poisson
  predictive mixture (`models.py:64-95`; hand calculation at `tests/test_study2_distributions.py:59-67`).
- QScore9: twice the mean pinball loss over all target days and the nine deciles (`scores.py:16-46`), the same
  definition as Study 1's (`pulsegraph/evaluation/metrics.py:141-144`); the three accounting parts sum to it
  exactly. The scaled score divides by max(1, mean of the full allowed context) (`scores.py:68`).
- Brier: (p minus 1[y > 0])^2 with p the law's survival at zero (`scores.py:80-82`); unavailable for the raw
  deciles and the two sample-only baselines, which carry `no_count_distribution`.
- Discrete CRPS: the sum of (F(k) minus 1[y <= k])^2 in blocks of 1,024 terms to k = 1,000,000 at most, certified
  only once k has passed the target and the analytic tail bound is below 1e-8 (`distributions.py:139-155`); the
  bounds are the exact geometric tail of the completion and SF(k) times a first-moment tail for the Poisson and
  negative binomial laws (`distributions.py:70-103`), checked against extended sums
  (`tests/test_study2_distributions.py:70-84`, `study/study2/crps_resolution.json`, 24 cases, maximum bound
  4.84e-9). Under the dated addition of 2026-10-15, `scores.py:49-63` catches exactly the certification failure
  and records the forecast's CRPS as unavailable with reason `crps_bound_not_certified`; every other error still
  stops the run (`tests/test_study2_crps_availability.py:37-49, 69-74`), and `scores.py:93-102` gives the valid
  denominators.
- Randomized PIT: not implemented anywhere in `pulsegraph/study2/` or `scripts/`; the PIT seed root 20260916 is
  declared and unused. The run saves every count law's specification per target day, so the PIT can be computed
  from the saved files afterwards without touching a forecast.

Fix: compute the randomized PIT in the inference command from the saved distributions, drawing one recorded
uniform per target day from a stream derived from the PIT root and the row's identity, and report it as the
secondary calibration output the protocol describes.

### 3. The gate: holds

For `external_packages`, `pulsegraph/study2/gate.py:238-290` requires, in order: a signed approval whose action
is the component, confirmed, with approver and a timestamp not in the future, bound to the Study 2 registration
commit and protocol hash (`gate.py:71-85`); the committed declarations equal to the generated ones
(`gate.py:145-149`, `pulsegraph/study2/declarations.py:151-157`); a positive estimate within the budget;
resolved source semantics and hashed evidence files; the packages readiness (`gate.py:175-198`): target access
approved separately, the panels exactly `{"packages"}`, the package domain npm, and the manifest, selection and
context hashes equal to the frozen panel's hashes in `study/study2/npm_panel_status.json` with the files present
at those hashes; then the runtime check (`gate.py:88-142`): the implementation commit equal to HEAD, the Study 2
registration bytes an unchanged prefix of `PROTOCOL.md`, a clean tree over `PROTOCOL.md`, `pyproject.toml`,
`pulsegraph`, `scripts`, `tests` and `study` including untracked files (`gate.py:42-68`), a passed synthetic smoke
whose implementation commit is that HEAD and whose source hashes equal the current hashes of every
`pulsegraph/study2/` module and every `scripts/study2_*` script, the installed package versions equal to the
smoke's with the two pins, the smoke's peak reserved VRAM under 8 GB on the declared GPU, and the CRPS
resolution file passed with `distributions.py` and `scores.py` at the hashes it records; finally the addition
check (`gate.py:152-172`): commit `8db0d73` is an ancestor of HEAD, its `PROTOCOL.md` carries the addition's
heading and is a byte prefix of HEAD's, and the working file equals HEAD's.

No stale or edited file passes: the panel status file and the declarations are tracked and inside the clean
check; the manifest and selection under `reports/` and the ignored context parquet are pinned by hash in the
tracked status file; the readiness and the smoke are ignored files whose hashes the signature names, and an
edit to either after signing fails the evidence check; a smoke taken before the last commit fails the HEAD
check. The tests at `tests/test_study2_packages.py:262-346` exercise each refusal, including a stale smoke, a
changed source hash, a dirty tree, a missing ancestor and an edited addition. One residual is noted, not a
fix: the smoke's own source list covers the Study 2 modules and scripts, while the Study 1 adapters under
`pulsegraph/forecast/` are bound only through the commit equality and the clean tree, which is sufficient when
the smoke is taken at a clean HEAD.

For `synthetic`, `gate.py:254-258` requires the committed `study/study2/grid_manifest.json` to equal
`grid_manifest()` exactly, and `pulsegraph/study2/synthetic.py:84` repeats the check before generating any
series. The oracle's CDF mass, quantile inversion and expected pinball optimality are verified offline against
the generator's known law built independently with scipy, for all 18 cells, both last states and all 30 leads
(`tests/test_study2_synthetic.py:70-94`), which is what the protocol asks before model runs.

The registered `external` component is unchanged: `study/study2/external_spec.json` and
`external_comparisons.json` have not changed since they were committed (`git log -- study/study2/external_*`
shows one commit), the family still validates as 54 (`tests/test_study2_gate.py:12-27`), and the gate still
requires three panels, a completed holdout freeze and a prediction commit for it (`gate.py:261-286`).

### 4. The target fetch: holds with this fix

- The window and the series: `ingestion.py:625-632` refuses any start other than 2026-06-03 and any end other
  than 2026-08-31 and any series not in the set that `pull_targets` fixes from the frozen manifest
  (`ingestion.py:684`); the URL is the documented range form with the scoped name as `@scope%2Fname`
  (`ingestion.py:611-618`), and each answer must name the package and the requested bounds.
- Unsigned runs: `pull_targets` calls the packages readiness check and then the full gate before any directory
  or request exists (`ingestion.py:652-653`); refusal without the target approval, without the signature, with a
  different action, with a manifest other than the frozen one, or with a dirty tree is tested
  (`tests/test_study2_packages.py:390-444`), each with zero requests sent.
- The frozen context: the signals are the frozen context rows followed by the ninety target days, and the file
  is read back and its prefix compared to the frozen context before it replaces the temporary path
  (`ingestion.py:723-739`); the context is never re-requested.
- Missing or incomplete ranges: `target_days` (`ingestion.py:634-639`) requires each of the ninety days exactly
  once with a nonnegative integer count and never fills; a failure is written to the pull ledger with its
  position and reason and the pull stops with no signals and no completeness document
  (`ingestion.py:690-713`); an outage or a budget stop resumes from the cached captures without excluding a
  series, and a saved incomplete answer stops again on resume (`tests/test_study2_packages.py:465-503`).
- The completeness document records UTC day labels, the method, the verification time, 2026-08-31 as the last
  complete day, the signals hash, the manifest and context hashes, the ledger failures and one hashed response
  capture per series, and every capture must have been acquired after the last target day
  (`ingestion.py:743-767`).

The one gap is at run time, not at fetch time. `external_dataset` (`runner.py:16-41`) takes the signals file
from the readiness and checks only its hash against the readiness entry and its prefix against the frozen
context; it never reads the completeness document, so nothing in the code ties the signals the run scores to the
captured responses the pull verified. The holdout path already has this binding (`pulsegraph/study2/holdout.py`
`read_context`) and the external path does not.

Fix: require a `completeness` entry in the packages panel of the readiness and, in `external_dataset`, verify
that its `signals_sha256` equals the signals file's hash, that its manifest and context hashes equal the frozen
panel's, that `verified` is true with the UTC calendar and 2026-08-31 as the last complete day, and that every
listed response capture is present at its hash.

### 5. The families: holds with this fix

- `study/study2/external_packages_comparisons.json` holds E01 to E18 tuple for tuple as they stand in the
  registered file, in order, with `comparison_count` 18 and the authority naming the dated addition of
  2026-10-12 and commit `8db0d73` (`declarations.py:27-36`; equality with the first eighteen registered rows and
  with the protocol table is tested at `tests/test_study2_packages.py:229-260` and
  `tests/test_study2_gate.py:12-27`). `synthetic_comparisons.json` holds S01 to S06 as registered.
- Both families carry the registered settings: QScore9, two-sided approximate Wilcoxon signed-rank omitting zero
  differences with p = 1 when all are zero, BH once at q = 0.05, 20,000 bootstrap replicates, bootstrap root
  20260917, conditional on the calendar.
- The aggregation is not implemented: no Study 2 inference command exists in `scripts/` or
  `pulsegraph/study2/`. The run writes one row per series, cutoff, horizon and variant with the scores, so the
  registered aggregation (origins within series and horizon, then equal series; for the synthetic, origins within
  replicate and cell, then cells within replicate, with the 30 replicate blocks as the pairing and bootstrap
  units) can be computed from the saved rows exactly as Study 1's module does
  (`pulsegraph/evaluation/confirmatory.py`, `pulsegraph/evaluation/reviews.py:173-232`). The protocol and the
  Study 1 module fix everything except two implementation details that are not outcome-dependent but are not
  written down for Study 2: how each comparison's bootstrap stream is derived from the root
  (`reviews.py:201` derives it from the comparison's fields and the metric, and Study 2's rows carry an id and a
  domain in place of a stratum) and the percentile interval's quantile interpolation (Study 1 uses NumPy's
  default). Written after the run, those details would be chosen with scores in view.

Fix: implement and commit `scripts/study2_inference.py` with its tests before the first target is requested,
reusing Study 1's cluster inference with the comparison row's fields and the metric in the seed derivation and
NumPy's default percentile, so that the run leaves no inference choice open; the smoke's source list already
covers that script, so it has to precede the smoke in any case.

### 6. Seeds and provenance: holds with this fix

- Every stochastic path is seeded from a registered root: the selection hashes from 20260914
  (`ingestion.py` `hash_key`), the forecasts from 20260915 through `derived_seed` per model, series, horizon and
  context (`models.py:147-149`, with the derived value recorded in each forecast's metadata), the synthetic
  streams from 20260918 with one occurrence and one size stream per replicate (`synthetic.py:24-32`,
  independence tested at `tests/test_study2_synthetic.py:18-28`), the bootstrap from 20260917 at inference. The
  local-mean draws use Study 1's seeded empirical sampler.
- The run records the signed readiness and its hash, the declarations, the implementation commit, the hashes of
  every source file, the installed packages, the smoke hash, the addition evidence and the GPU description
  (`scripts/study2_run.py:60`, `gate.py:137-142, 167-172`), and per series a checkpoint file with the forecasts,
  the targets, the context mean and the scores, including the CRPS bound and work per forecast.
- Models stay resident for the invocation (`models.py:159-161`) and are released at exit; a failed window
  raises, the state is marked failed with the reason and the run stops (`runner.py:118-122`); a resume verifies
  every completed checkpoint hash and re-attempts the failed series rather than skipping it
  (`runner.py:71-76`; `tests/test_study2_gate.py:97-127`).
- Two gaps. First, the resume identity is the hash of the whole run metadata (`runner.py:48`), and that metadata
  includes `hardware` from `configure_gpu()` (`scripts/study2_run.py:60`), which carries the free GPU memory at
  start and the allocator budget derived from it (`pulsegraph/forecast/hardware.py:25-29, 38-39`). Those values
  differ between invocations, so after any stop the resume in the same directory fails with "changed resume
  identity" and the run has to start over in a new directory; the resume test passes only because it supplies
  fixed metadata. Second, the per-model timings and the peak GPU memory of the run are measured
  (`models.py:152, 202`; `models.py:178` enforces the 8 GB limit after every FM forecast) but never written: the
  timings are overwritten per call and the snapshot is discarded.

Fix: derive the resume identity from the metadata without the volatile hardware fields (keep the GPU model,
driver, CUDA and PyTorch versions; record the free memory and budget per invocation in the resume log), and
write the pool's timings and a final memory snapshot into each series checkpoint or into `run.json`.

### 7. The reduced panel: holds

The frozen panel has 209 series: 100 dense, 100 sparse, 9 very sparse (`reports/study2-npm/panel/manifest.json`,
`study/study2/npm_panel_status.json`, which also records the 9 complete very-sparse candidates and the 91
unfilled slots). Nothing in the code treats the short stratum specially: selection takes the first min(100, N_s)
of each stratum's hash order with no transfer (`ingestion.py` `build_panel`), the run iterates the manifest and
knows no stratum, the confirmatory family pools all 209 series as the protocol registers (strata are secondary
descriptors), and the stratum label for any secondary table comes from the manifest, so a per-stratum table
will show n = 9 for the very-sparse stratum. Study 1's inference refuses fewer than two entities, which no
stratum here approaches.

### 8. Scale: holds

One series, `aggregate-error`, has a last-28-day context mean of 7,637,136 downloads (`npm_panel_status.json`);
the next largest mean before the first cutoff is about 13,000, and no other series exceeds 100,000 on any day
of that window (from the frozen context parquet and the manifest). A CPU probe built every registered law at
the 7.6 million level from stand-in deciles and a stand-in context: the completion with float32-resolution
deciles, its hurdle, `poisson_28`, both count hurdles, the dynamic count at leads 1 and 30 (shape about
3.7e8), and the negative-binomial local level (size about 49, probability about 7e-6). For each, the nine
quantiles are finite and nondecreasing, the CDF is monotone from zero at k = -1 to one, and quantile inversion
holds; the pinball loss at that level is finite and the accounting parts sum exactly. Every CRPS attempt at that
level ends in the certification failure within a fraction of a second and is recorded as unavailable, so the
run continues as the addition intends; the test at `tests/test_study2_crps_availability.py:77-123` runs a
whole-series fixture at 1e7 to the same effect. The float32 resolution of the FM outputs at that level (one
unit) is immaterial to integer deciles.

Two observations, neither a fix. The equal-series mean difference of the unscaled QScore9 will be dominated by
that one series, whose losses are of order 1e5 to 1e6 while most series' are below ten; the registered primary
is that mean with its series-bootstrap interval, the signed-rank test is rank-based, and the scaled score is
secondary, so this is a property of the registered design to state in the write-up, not a defect. The
empirical hurdle's certification cost grows with the largest positive value when that value is below the work
limit (about 13 seconds per target day at one million in the probe, under 0.2 seconds at 100,000), because the
exact tail sum is recomputed per block; no series in this panel sits in that range before the first cutoff, so
the run is unaffected, but a future domain with daily counts near one million would pay it.

## Closing

As the code stands at `03f08b3`, the information boundary holds, the formulas match the registered text, the
gate and the target fetch cannot be satisfied by an unsigned, stale or edited input, the families are exact,
the reduced stratum is handled as registered and the numerics hold at the largest scale in the panel. The
targets may be opened after the fixes above land in one commit before the smoke that the gate binds to HEAD:
the inference command with the randomized PIT (5, 2), the completeness binding in `external_dataset` (4), and
the resume identity with the persisted timings (6). The first is the one that bears on integrity: with it, no
inference choice remains to be made after a score exists. The order is then the commit, one smoke at that
HEAD, the signed readiness, the gate, the target pull, the gate again with the signals and completeness hashes,
the run, and the inference over E01 to E18.

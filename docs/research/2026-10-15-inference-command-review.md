# Review of the Study 2 inference command before the first real score

Written 2026-10-15 20:30 UTC against commit `3fc3411`, with the tree clean apart from the synthetic run
directory that was being written at the time. `scripts/study2_inference.py` is the code that turns a finished
Study 2 run directory into the confirmatory families E01 to E18 (npm) and S01 to S06 (synthetic). It was
committed before any Study 2 score existed so that every choice in the confirmatory machinery is fixed in
advance. This review reads it line by line against the registered text before the first real result passes
through it: `PROTOCOL.md` ("Inference: 18 comparisons" for Study 1's form; the Study 2 sections "Scores and the
single external-domain confirmatory family", "Synthetic intervention component" and "Seeds, provenance and
execution gate"; the dated additions of 2026-10-12, item 3, and 2026-10-15, item 5), the committed comparison
files under `study/study2/`, Study 1's inference (`pulsegraph/evaluation/confirmatory.py`,
`pulsegraph/evaluation/reviews.py`, `scripts/registered_inference.py`), `pulsegraph/study2/scores.py` and
`runner.py`, and the command's tests. The review used no GPU, no network and no target value; the running
synthetic directory was not opened beyond its list of file names. Line numbers are those of commit `3fc3411`.

## The eight verdicts

### 1. Aggregation: holds

- `series_scores` (`scripts/study2_inference.py:276-281`) takes the mean of every score over the rows of each
  (horizon, model, series_id) group; the rows of a group are exactly the three origins, because `read_run`
  refuses any grid that is not series × 3 origins × 2 horizons × every variant with no duplicate window
  (lines 257-260) and refuses a row whose cutoff, horizon or model is outside the registered sets (lines
  225-234).
- For `external_packages` the entity is the series (`entity_scores`, lines 284-287) and `paired` (lines
  294-299) sets one row per series with equal weight; 209 is whatever the frozen manifest holds, read at its
  readiness hash (lines 181-186), and the test on the toy run recomputes the aggregation independently from
  the checkpoint rows for all 18 comparisons.
- For `synthetic` the series is one (cell, replicate), so the first mean is over origins within replicate and
  cell; `entity_scores` then takes the mean over the rows of each (horizon, model, replicate) group (lines
  288-291), which are the 18 cells, each weighing one, because `expected_series` refuses a grid manifest in
  which any replicate block does not hold every cell exactly once (lines 171-176) and the committed manifest
  must equal the one the code generates (lines 164-166). The replicate blocks are the pairing and bootstrap
  units. Thirty blocks of 18 cells are asserted on the registered grid by the test.
- Horizon 30 only in the synthetic family: every row of `study/study2/synthetic_comparisons.json` has horizon
  30, the generator of that file admits only horizon 30 for the synthetic component
  (`pulsegraph/study2/declarations.py:38-40`), and `confirmatory` takes the horizon from the family row (line
  306). Horizon 7 appears only in `secondary_contrasts.csv` under ids `S01-h7` to `S06-h7`.
- No pooling across domains: the command accepts one domain per component (line 57), refuses a checkpoint row
  of another domain (line 227), and refuses the registered 54-test component (line 616-617), so E19 to E54
  cannot be merged with E01 to E18 after the fact, as the addition of 2026-10-12 requires.

### 2. The statistic and its direction: holds

- `difference = model_score − reference_score` (line 310 for the family table, line 333 for the paired table);
  QScore9 is a loss, so a negative difference favors the model, and the docstring (lines 18-20) and
  `inference.json` (`settings.difference`, line 676) say so.
- Wins, ties and losses are the entities with difference below, exactly at and above zero (lines 140-142),
  over the full entity count (`n_entities`, line 135); a near-zero floating difference is a win or a loss, not
  a tie, which agrees with the test's exact-zero omission.
- The test is `scipy.stats.wilcoxon(diff, zero_method="wilcox", alternative="two-sided", method="approx")`
  (lines 126-131) with the settings read from the committed family file; the continuity correction is SciPy's
  default, off, as in Study 1 (`reviews.py:211`, which passes `method="approx"` alone and so takes the same
  defaults). Zero differences are omitted by `zero_method="wilcox"`; p = 1 when every difference is zero (lines
  122-124, `all_zero_p` 1.0 in both family files).
- Nothing in the outputs calls it a test of the mean: `inference.csv` carries `wilcoxon_p` beside a separate
  bootstrap interval for the mean, and `inference.json` records the test's name, alternative, method, zero
  rule and all-zero rule (lines 692-698) with no interpretation. The protocol's symmetry caveat is not
  restated in the outputs; the write-up must carry it, as Study 1's does.

### 3. The bootstrap: holds

- 20,000 whole-entity replicates with replacement, read from the family file (line 112), drawn in blocks of
  256 as `rng.integers(0, n, size=(block, n))` over the entity differences (lines 116-120); this is Study 1's
  loop verbatim (`reviews.py:203-209`). Pairing is preserved because each entity's difference is formed
  before resampling, and resampling moves whole entities, never windows or cells.
- The interval is the pointwise percentile interval at alpha / 2 and 1 − alpha / 2 with alpha = 1 − 0.95
  (lines 121, 137-138), NumPy's `linear` interpolation stated explicitly (line 65), written into every row of
  `inference.csv` (`quantile_method`) and into `inference.json`. NumPy's default is `linear`, so Study 1's
  unstated interpolation is the same one.
- The seed: `pulsegraph.random.derived_seed(20260917, component, id, domain, model, reference, horizon,
  metric)` (lines 90-100), the first four bytes of the SHA-256 of the canonical JSON of that list, little
  endian (`pulsegraph/random.py:15-21`). The root is the registered bootstrap root (`constants.py:21`). The
  derivation uses `json.dumps(..., sort_keys=True, allow_nan=False)` on integers and strings only, so it has
  no dependence on process hash randomization, dictionary order or platform. Recomputed with `hashlib` and
  `json` alone, outside the project's code: E01 gives 4064020396, S01 gives 3742483908, and the PIT seed of
  (`synthetic`, `cell00/rep00`, origin 180, horizon 30, `oracle`) gives 114759717, the three values the test
  pins.
- Determinism across machines rests on NumPy's guarantee that `default_rng(seed).integers` and `.random`
  produce the same stream for a given NumPy version on every platform; the versions are recorded in
  `provenance.json` (line 742). On this machine, the replay of Study 1 in verdict 4 reproduces the committed
  intervals of 2026-09-13 to within 2e-15.

### 4. Benjamini-Hochberg once over the family: holds

- `benjamini_hochberg` is imported from Study 1 (`reviews.py:160-170`) and applied once to the family table's
  column of raw p-values (line 338); `reject_bh_005` is adjusted p ≤ q with q from the family file (line 339).
  No other table receives an adjustment.
- The family is read from the committed comparison file (lines 622-626); `validate` (line 629,
  `declarations.py:151-157`) refuses any file that is not equal to the registered declaration, so a missing or
  extra comparison, a changed reference or a changed setting is refused before anything is read; the run's own
  recorded family and specification must equal the file (lines 204-209); and the table must have exactly the
  declared count with no duplicate id (lines 336-337). The `--comparisons` option can therefore name only a
  byte-equal copy of the registered family. The test exercises 17- and 19-row files and a run whose recorded
  family differs.
- Study 1's paired table replayed: for each of the 18 rows of
  `reports/registered-2026-09-13/inference/inference.csv`, the differences of
  `paired_repositories.csv` (300 repositories, sorted by name as Study 1's pivot sorts them) were passed to the
  command's `cluster_contrast` with Study 1's recorded per-row `bootstrap_seed` and the Study 2 family
  settings (20,000 replicates, two-sided approximate Wilcoxon, zeros omitted), then to `benjamini_hochberg`
  over the 18. Every column matches the committed Study 1 values: n exactly; mean difference, both interval
  ends, median, win rate, raw p and adjusted p to at most 1.8e-15, which is the CSV round-trip; the 18
  rejections at q = 0.05 are identical. The formats allow it because Study 1's paired table already holds one
  row per repository and comparison. Study 1's seeds were supplied, not rederived: Study 2's seed payload
  (the id and domain in place of Study 1's stratum) differs by design. The replay, from the repository root:

```powershell
.\.venv\Scripts\python.exe -c "import numpy as np, pandas as pd, scripts.study2_inference as cmd; from pulsegraph.evaluation.reviews import benjamini_hochberg; from pulsegraph.study2.declarations import comparisons; b='reports/registered-2026-09-13/inference/'; P=pd.read_csv(b+'paired_repositories.csv', keep_default_na=False); I=pd.read_csv(b+'inference.csv'); F=comparisons('external_packages'); R=[cmd.cluster_contrast((g.model_score-g.reference_score).to_numpy(), seed=int(r.bootstrap_seed), family=F) for r in I.itertuples() for g in [P[(P.model==r.model)&(P.reference==r.reference)&(P.horizon==r.horizon)].sort_values('repo_name')]]; T=pd.DataFrame(R); T['bh']=benjamini_hochberg(T.wilcoxon_p); print({c: float(np.abs(T[a]-I[c]).max()) for a,c in [('mean_diff','mean_diff'),('mean_diff_ci_low','mean_diff_ci_low'),('mean_diff_ci_high','mean_diff_ci_high'),('median_diff','median_diff'),('wilcoxon_p','wilcoxon_p'),('bh','wilcoxon_p_bh')]}, ((T.bh<=0.05)==I.reject_bh_005).all())"
```

### 5. The randomized PIT: holds

- Root 20260916 (`constants.py:20`), derived per saved forecast as
  `derived_seed(20260916, component, domain, series_id, cutoff, horizon, model)` (lines 103-104, 520-522); `V =
  default_rng(seed).random(horizon)` gives one uniform per target day in lead order (line 523), and every
  uniform is recorded with its seed in `pit_values.parquet` (columns `seed`, `v`, lines 538-539).
- The formula: `F(y−) = 1 − SF(y − 1)`, `F(y) = 1 − SF(y)` from the saved law (lines 530-531), `U = F(y−) + V
  (F(y) − F(y−))` (line 545), refusing a law that is not a distribution at its target (lines 532-533). Checked
  by hand on a hurdle law with occurrence 0.7: at y = 0 the jump is [0, 0.3], at y = 1 it is [0.3, 0.4867],
  and the command's `pit` reproduces the independently drawn uniforms and the formula to the last bit.
- Unavailable where no full law exists: rows without `distributions` never enter `pit` (line 254), and a
  (horizon, model) histogram is `unavailable` with reason `no_count_distribution` unless every window of the
  model carries a law (lines 554-563). In the registered variants only the three `_raw` deciles,
  `local_mean_28` and `autoets_weekly` lack a law (`pulsegraph/study2/models.py:116, 194-200`); every
  `_completed`, `_hurdle`, count baseline and the oracle always carries one, so no partial case arises.
- No IID significance claim: `pit_histograms.csv` holds counts and fractions in ten bins and nothing else;
  `inference.json` records the root, the derivation sentence and the bin edges (lines 717-721). The bins are
  `[b/10, (b+1)/10)` with the last closed (line 557, checked at U = 0, 0.1, 0.3, 0.7, 0.9999, 1).

### 6. The secondary outputs: holds

- No multiplicity adjustment anywhere outside `confirmatory`: `secondary_contrasts` (lines 382-415) reports
  the raw Wilcoxon p and the bootstrap interval with `status` `secondary`; the per-stratum and per-cell
  contrasts carry no test and no interval at all (`describe`, lines 148-158; `group_tables`, lines 484-503).
  `inference.json` says so (lines 707-716).
- Every per-stratum and per-cell row carries `n_entities` (lines 425, 151), the strata and cell contrasts
  carry `n_entities`, wins, ties and losses, and the test asserts n of 2, 2 and 1 for the toy strata.
- The CRPS tables carry the availability denominators the addition of 2026-10-15 requires: per (horizon,
  model) the forecasts, those with a count distribution, those certified, and the unavailable ones by reason
  (lines 429-435); each contrast reports `n_entities_unavailable` with a reason (lines 394, 407-413); an
  entity's secondary score is defined only when every window has it (`_strict_mean`, lines 270-273). The
  uncertified case is tested with a rewritten toy checkpoint and leaves `inference.csv` unchanged.
- Nothing feeds back: `confirmatory` (line 635) reads only the QScore9 column of the entity table, which is
  built before any secondary table and never modified; the family table is written first and hashed in
  `provenance.json` with the rest.

### 7. Hand checks: holds

On seven constructed differences d = (−0.30, −0.10, 0.20, 0, −0.45, 0.10, −0.05) with seed 123 and the
external family's settings:

| Quantity | By hand or with SciPy alone | The command |
|---|---|---|
| Wilcoxon p, zero omitted, ranks 1, 2.5, 2.5, 4, 5, 6, R+ = 6.5, tie-corrected variance 22.625 | 0.4003808031520797 | 0.4003808031520797 |
| wins, ties, losses, n nonzero | 4, 1, 2, 6 | 4, 1, 2, 6 |
| mean, median | −0.0857142857142857, −0.05 | the same |
| 95% percentile interval, same draws, `numpy.percentile` at 2.5 and 97.5 | [−0.2428571428571428, 0.0642857142857143] | the same |

BH by hand on (0.01, 0.20, 0.03, 0.04, 0.50, 0.001) gives (0.03, 0.24, 0.06, 0.06, 0.5, 0.006), equal to
`benjamini_hochberg` to the last bit. All-zero differences give p = 1; one difference is refused. The
command's own tests add the cases d = (−3, −1, 2, 0, −4) against the closed-form normal approximation, four
tied |d| giving z = −2 exactly, two entities 0 and 1 giving the interval [0, 1], and the replay of verdict 4.

### 8. Anything a score could influence after the fact: holds

- Every test setting (replicates, alternative, method, zero rule, all-zero p, q, the count) is read from the
  committed family file, which must equal the registered declaration byte for byte and the run's own recorded
  copy. No setting is read from the run directory and none has a data-dependent default. The constants in the
  script (block size, confidence, interpolation, bins, origins, horizons) are module-level literals.
- From the run directory the command takes the scores and, for npm, the manifest path; the manifest is read
  at the hash recorded in the readiness, whose hash is part of the run identity (lines 181-184, 202-203), so a
  swapped manifest is refused. The synthetic grid comes from the code and must equal the committed file.
- No invocation can overwrite another: the output directory is refused if it exists (lines 620-621) and
  created without `exist_ok` (line 654). A second invocation with another `--out` writes a second, identical
  directory whose `provenance.json` names the same run hash, checkpoint hashes and script hash; the script's
  own hash and any uncommitted change to it or to `pulsegraph` at inference time are recorded (lines
  737-741), so an edited script cannot pass as the committed one.
- One gap, not a fix the family needs: the command takes the saved QScore9 on trust and does not recompute it
  from the saved deciles and target, as Study 1's integrity review does for its run. The checkpoints are
  hash-bound and the scorer is tested, so the trust is in committed code; a recomputation of `accounting`
  per row would cost seconds and would close the gap for the paper's integrity statement.

## Tests

`tests/test_study2_inference.py`: 17 passed in 20 s on the CPU, run with `--basetemp=data\cache\review3-tmp
-p no:cacheprovider`, 42 deprecation warnings from the runner's `Timedelta` arithmetic, none from the
inference. SciPy 1.18.1, NumPy 2.5.3, pandas 2.3.3.

## What could not be verified

- Determinism across machines is argued from the derivation (canonical JSON, SHA-256, NumPy's fixed stream),
  not tested on a second machine; the Study 1 replay shows that this machine reproduces values committed on
  2026-09-13.
- The command has run only on toy run directories, on Study 1's paired table and on a stand-in 540-series
  grid; no real Study 2 score has passed through it, by design.
- The paired-table order of Study 1 was taken as the saved file's order, which is sorted by repository name
  within each comparison; the bootstrap reproduces exactly under that order, which confirms it.

## Closing

Real results may pass through the command as it stands. All eight verdicts hold; no fix must land before
results are read. The aggregation, direction, test, bootstrap, seeds, single BH correction, PIT and secondary
tables match the registered text and Study 1's form, the pinned seeds recompute from the hash alone, Study
1's 18 committed rows replay through the new code to machine precision, and no setting can be touched by a
score. The one recommendation is for the integrity statement, not the inference: a recomputation of QScore9
from each saved forecast and target, added beside the command without changing it, so that the paper can say
the scores were recomputed as well as hash-bound.

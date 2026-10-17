# Study 3 on NYC 311: the regime family R01 to R36

Protocol: `PROTOCOL.md`, dated addition of 2026-10-16, item 7 ("Study 3: the occurrence substitution by regime on a
second domain"), committed in `3357d779db28cffa4048e7e333fd02b9434b4b6d`. The protocol carrying the addition has
SHA-256 `05c7617b0391cbcca7bccddb6ff54a763d47ba88e5d31dac4bd98621a9721b29` and is unchanged at the implementation
commit. Where item 7 says "as registered", Study 2's registration at `df55867c982dfe2bb6e1152ec8ae93e3cd228c45`
applies. The family is `study/study3/regime_comparisons.json` (SHA-256
`e86dbd3b8fa4aafcbd115d442046bcabc55449d77a95d468ef16f779d328744c`) and the specification `study/study3/spec.json`
(`0886fcadec7752edea10ca9ba8443abc18320473a23d40cf849c7b326047fe4f`), both committed with the addition.
Implementation: `00fd91dccfc86b1e4bbd2f0cb44a47052937458d`.

Gate: pass, with the author's signed readiness and the GPU smoke at the implementation commit. The author approved
the readiness on 2026-10-17 at 03:12:50 UTC, with target access for 100 HTTP attempts, one request for the source's
terms page, and a runtime budget of 3,600 seconds against an estimate of 1,080. At 03:43 UTC the author approved 20
more target attempts, 120 in all and 3 seconds apart, and two more terms requests on `www.nyc.gov`. After the run,
the author approved up to three page reads on `www.nyc.gov` in a desktop browser, for the terms. The smoke is
`study/study3/smoke_2026-10-17_00fd91d.json`: passed at 01:56:50 UTC, peak reserved VRAM 2,948,595,712 bytes. The
gate (`authorize_study3`) passed three times: at 03:15:43 UTC, before the first target request; at 03:44:13 UTC,
before the pull resumed; and at 03:46:46 UTC, before the run, with the pull's signals admitted only together with
their completeness document. The pull and run commands run it again themselves before any access. The run's
readiness is tracked as `study/study3/study3_readiness_2026-10-17.json`.

Targets: the 90 target days, 2026-06-03 to 2026-08-31, were counted by the registered census over the frozen 2024
frame: one query per New York calendar day to NYC Open Data's SODA endpoint, anonymous. There were 106 attempts in
two invocations, recorded in the ledger (`target-pull/pull.json`):

- 03:16:23 to 03:32:12 UTC, 1 second apart: 100 attempts, 84 days. The invocation stopped at the approved
  ceiling, as the client is built to. Every day was answered on one page, so 16 attempts were repeats after the
  server answered 429 or 5xx and the client waited. The client does not record which.
- 03:45:06 to 03:45:43 UTC, 3 seconds apart: 6 attempts for the last 6 days, each answered at the first attempt.

What the census found:

- Every day was exhausted on one page: 983,482 requests, none superseded.
- 947,751 are in frame cells, 18,660 have a missing or unrecognized board or problem, and 17,071 are in recognized
  cells outside the 2024 frame.
- There is no source gap: the fewest frame requests on any day were 8,849, on 2026-08-16.
- Every capture was acquired after 2026-08-31 had ended in New York.
- The signals join the 90 days to the frozen 275-day context, which was unchanged and not re-requested
  (`target-pull/completeness.json`, whose `target_census` lists each day).
- A separate recomputation from the raw captures, sharing no code with the pipeline, reproduced the census
  totals, every series' 90 target counts and the unchanged context.

Run: complete. All 300 of 300 series ran in one invocation, 03:47:23 to 04:03:02 UTC: 939 seconds inside the run
and 956 for the whole process, against the budget of 3,600 and the estimate of 1,080. Failures 0, resumes 0.

- **Hardware:** RTX 4070 SUPER, driver 610.88, CUDA 12.8, PyTorch 2.11.0+cu128, batch size 1, peak reserved VRAM
  2,948,595,712 bytes.
- **Weights:** read from the local cache with the Hugging Face offline variables set.
- **Forecasts:** 39,600, that is 300 series × 3 origins × 2 horizons × 22 variants.

Integrity: the committed `scripts/study3_integrity.py` passes on this directory.

- **Checkpoints:** all 300 match the SHA-256 values in `run.json`, and every registered window appears exactly once.
- **Recomputation:** for all 39,600 forecasts, QScore9, its three accounting parts and the context-scaled QScore9
  were recomputed from the saved deciles, targets and laws. So was the occurrence Brier score for the 30,600 that
  carry a count law. There were 0 disagreements.
- **Residuals:** the largest absolute residuals are 0.0 for QScore9 and the scaled score, 7.1e-15 for the parts and
  2.8e-16 for the Brier score.
- **The two new variants:** the structure the addition registers holds on every target day of all 10,800 of their
  windows.
  - hurdle_dynamic's P(Y > 0) equals dynamic_count's, and its positive law is the completed law conditioned on
    Y ≥ 1.
  - occurrence_model_size_count's P(Y > 0) equals the completed law's, and its positive law is hurdle_count_28's.
- **Discrete CRPS:** 30,600 certified, 9,000 without a count law, 0 uncertified.
- **Direction check:** `make_tables.py` recomputes every family test's raw p-value from
  `inference/paired_entities.csv` and reproduces all 36 exactly. It also reads the direction of each test from its
  rank sums.

## The source and its terms

The counts are NYC 311 service requests by creation day from NYC Open Data's dataset `erm2-nwe9`, "311 Service
Requests from 2020 to Present". `created_date` is a floating timestamp that behaves as New York wall-clock time, and
the census counts it by New York calendar day (`reports/study3-nyc311/panel/source-terms.md`).

The dataset's metadata states no license and links no terms page. NYC Open Data's overview page now redirects to
`www.nyc.gov`. That page refused the scripted request, but it was read in a desktop browser on 2026-10-17, and its
footer links the city website's terms of use.

What those terms say:

- they govern NYC.gov and its subpages, and allow lawful use only;
- the City's materials are its property, with all rights reserved;
- links imply no endorsement;
- there is no warranty of accuracy, completeness or currency, and no liability for use.

They say nothing specific about Open Data datasets: no license, no attribution requirement, and no rule on publishing
derived figures. The NYC Open Data page names New York City's Open Data Law, under which agency data are open by
default, as the program's basis. The law itself was not read.

The record, with the hash of each page's text, is in `source-terms.md`, section "The terms page, 2026-10-17". This
page names the source as NYC Open Data, dataset `erm2-nwe9`, and claims no endorsement by the City.

## The contamination ledger for NYC 311

Study 2's registration ("Contamination ledger") keeps three categories for every domain. For NYC 311 they are,
unchanged:

- **Known source or entity overlap:** no exact source or entity match is established in the reviewed disclosures.
- **Unknown overlap:** civic data may occur in broadly described training corpora; absence of disclosure is not
  absence from training.
- **Targets after frozen checkpoint availability:** the retrospective calendar does not certify that the 2026 target
  days postdate the availability of all three checkpoints.

## The design, in brief

The panel is NYC 311's frozen achieved panel: `reports/study3-nyc311/panel/` (manifest, selection, census) and
`study/study3/nyc311_panel_status.json`.

- **Series:** 300, each a problem type in a community board.
- **Frame:** drawn from the 8,469 eligible cells of the frozen 2024 inventory, with selection seed 20261001.
- **Strata:** the context zero fraction over 2026-03-05 to 2026-06-02, with the first 100 complete series of each
  stratum in selection-hash order. No stratum is reduced.

| Stratum (context zero fraction, 2026-03-05 to 2026-06-02) | Complete candidates | Series in the panel | Unfilled of 100 |
|---|---|---|---|
| dense, [0, 0.5) | 2,002 | 100 | 0 |
| sparse, [0.5, 0.9) | 2,422 | 100 | 0 |
| very sparse, [0.9, 1] | 4,045 | 100 | 0 |
| all | 8,469 | 300 | 0 |

Of the very sparse stratum's 100 series, 39 have no request in the 90 strata days and 19 none in the whole 275-day
context. No dense or sparse series has either.

The calendar is the registered one:

- context from 2025-09-01;
- cutoffs 2026-06-03, 2026-07-03 and 2026-08-02 (275, 305 and 335 context days);
- horizons 7 and 30;
- endpoint 2026-08-31, in New York calendar days.

All 22 registered variants were forecast at every origin and horizon: Study 2's sixteen and two new variants for each
model. Each of the three frozen foundation models (Chronos-2, TimesFM 3, TimesFM 2.5) has four variants, all from the
same saved base forecast:

- **completed:** the control;
- **hurdle_fixed:** the run's `<model>_hurdle`, Study 2's hurdle with the 28-day Jeffreys occurrence;
- **hurdle_dynamic:** the occurrence of the registered dynamic_count law with the completed positive law;
- **occurrence_model_size_count:** the model's own completed occurrence with hurdle_count_28's positive law.

With fewer than two request days in the last 28 days of a context, dynamic_count takes hurdle_count_28's law. For
that window, hurdle_dynamic then equals hurdle_fixed.

How to read the tables:

- **Differences** are hurdle_dynamic minus the reference, in QScore9. QScore9 is a loss, so a negative difference
  favors hurdle_dynamic and a positive one favors the reference.
- **T1** compares hurdle_dynamic with the model's own completed forecast; **T2** compares it with
  `hurdle_empirical_28`.
- **The entity is the series, within its stratum.** Origins are averaged within series and horizon, and the 100
  series of a stratum weigh equally.
- **Intervals** are pointwise 95% percentile intervals from 20,000 series bootstrap replicates. The per-comparison
  seeds are in `inference/provenance.json`.
- **Raw p** is from a two-sided approximate Wilcoxon signed-rank test over the 100 series differences. Zero
  differences are omitted, and p is 1 when every difference is zero. The test's location reading needs symmetry; it
  is not a test of the mean difference.
- **BH p** applies Benjamini-Hochberg once over the thirty-six, at q = 0.05; all 36 tests are available.
- **"Lower / tied / higher"** counts the series where hurdle_dynamic's score is below, exactly equal to, or above the
  reference's.
- **The direction of a test** is read from the paired table: the median's sign and the rank sums. A median of
  exactly zero has no sign and is reported as neither direction.
- **H3's prediction** is a positive T1 median in the dense stratum and a negative one in the sparse and very sparse
  strata. H3 predicts nothing for T2.
- Inference is conditional on the fixed dates.

## The confirmatory family R01 to R36 (300 series; BH once at q = 0.05)

36 of 36 tests available; BH over 36. Differences are hurdle_dynamic minus the reference, in QScore9; negative favors hurdle_dynamic. Lower / tied / higher counts the series whose difference is below, exactly at and above zero; ties are omitted by the Wilcoxon test. H3 predicts a positive T1 median in the dense stratum and a negative one in the sparse and very sparse strata, and nothing for T2.

| ID | Stratum | Model | h | Contrast, reference | hurdle_dynamic mean | Reference mean | Mean difference | 95% interval | Median difference | Lower / tied / higher | Raw p | BH p | BH rejects | H3's sign | Median's sign | Median as H3 predicts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R01 | dense (n = 100) | Chronos-2 | 7 | T1 `chronos2_completed` | 1.851 | 1.833 | 0.01775 | [0.006084, 0.0302] | 0.01217 | 39 / 1 / 60 | 0.00786 | 0.0167 | yes | positive | positive | yes |
| R02 | dense (n = 100) | Chronos-2 | 7 | T2 `hurdle_empirical_28` | 1.851 | 2.06 | -0.2089 | [-0.3871, -0.08625] | -0.06561 | 75 / 1 / 24 | 5.7e-09 | 4.1e-08 | yes | none | negative | n/a |
| R03 | dense (n = 100) | Chronos-2 | 30 | T1 `chronos2_completed` | 1.724 | 1.709 | 0.01511 | [0.006331, 0.02457] | 0.004074 | 43 / 2 / 55 | 0.0147 | 0.0294 | yes | positive | positive | yes |
| R04 | dense (n = 100) | Chronos-2 | 30 | T2 `hurdle_empirical_28` | 1.724 | 1.939 | -0.2147 | [-0.3923, -0.09954] | -0.06531 | 87 / 0 / 13 | 2.35e-14 | 8.47e-13 | yes | none | negative | n/a |
| R05 | dense (n = 100) | TimesFM 3 | 7 | T1 `timesfm3_completed` | 1.848 | 1.827 | 0.02098 | [0.01196, 0.03057] | 0.01164 | 30 / 2 / 68 | 1.5e-05 | 5.4e-05 | yes | positive | positive | yes |
| R06 | dense (n = 100) | TimesFM 3 | 7 | T2 `hurdle_empirical_28` | 1.848 | 2.06 | -0.2118 | [-0.3953, -0.0842] | -0.05608 | 75 / 0 / 25 | 1.44e-08 | 8.66e-08 | yes | none | negative | n/a |
| R07 | dense (n = 100) | TimesFM 3 | 30 | T1 `timesfm3_completed` | 1.719 | 1.703 | 0.01637 | [0.00961, 0.02362] | 0.008395 | 28 / 0 / 72 | 6.88e-06 | 3.1e-05 | yes | positive | positive | yes |
| R08 | dense (n = 100) | TimesFM 3 | 30 | T2 `hurdle_empirical_28` | 1.719 | 1.939 | -0.2194 | [-0.4047, -0.09995] | -0.06123 | 85 / 0 / 15 | 1.87e-13 | 2.24e-12 | yes | none | negative | n/a |
| R09 | dense (n = 100) | TimesFM 2.5 | 7 | T1 `timesfm2p5_completed` | 1.846 | 1.824 | 0.02219 | [0.0129, 0.03251] | 0.0127 | 32 / 2 / 66 | 1.41e-05 | 5.4e-05 | yes | positive | positive | yes |
| R10 | dense (n = 100) | TimesFM 2.5 | 7 | T2 `hurdle_empirical_28` | 1.846 | 2.06 | -0.2138 | [-0.3964, -0.09041] | -0.05714 | 72 / 0 / 28 | 9.65e-10 | 8.69e-09 | yes | none | negative | n/a |
| R11 | dense (n = 100) | TimesFM 2.5 | 30 | T1 `timesfm2p5_completed` | 1.726 | 1.707 | 0.01862 | [0.01234, 0.02532] | 0.01148 | 30 / 0 / 70 | 5.29e-08 | 2.72e-07 | yes | positive | positive | yes |
| R12 | dense (n = 100) | TimesFM 2.5 | 30 | T2 `hurdle_empirical_28` | 1.726 | 1.939 | -0.2126 | [-0.3846, -0.1013] | -0.06753 | 86 / 0 / 14 | 1.8e-13 | 2.24e-12 | yes | none | negative | n/a |
| R13 | sparse (n = 100) | Chronos-2 | 7 | T1 `chronos2_completed` | 0.361 | 0.3631 | -0.002138 | [-0.007111, 0.002751] | 0 | 46 / 13 / 41 | 0.526 | 0.556 | no | negative | none (0) | neither (median 0) |
| R14 | sparse (n = 100) | Chronos-2 | 7 | T2 `hurdle_empirical_28` | 0.361 | 0.3664 | -0.005418 | [-0.01095, 0.0001481] | 0 | 46 / 15 / 39 | 0.102 | 0.138 | no | none | none (0) | n/a |
| R15 | sparse (n = 100) | Chronos-2 | 30 | T1 `chronos2_completed` | 0.3574 | 0.3591 | -0.001654 | [-0.00497, 0.001657] | 0 | 44 / 12 / 44 | 0.357 | 0.414 | no | negative | none (0) | neither (median 0) |
| R16 | sparse (n = 100) | Chronos-2 | 30 | T2 `hurdle_empirical_28` | 0.3574 | 0.3615 | -0.004047 | [-0.008321, -0.0001752] | -0.001852 | 53 / 15 / 32 | 0.0274 | 0.0471 | yes | none | negative | n/a |
| R17 | sparse (n = 100) | TimesFM 3 | 7 | T1 `timesfm3_completed` | 0.3606 | 0.3603 | 0.0003069 | [-0.003714, 0.004571] | 0 | 45 / 23 / 32 | 0.425 | 0.478 | no | negative | none (0) | neither (median 0) |
| R18 | sparse (n = 100) | TimesFM 3 | 7 | T2 `hurdle_empirical_28` | 0.3606 | 0.3664 | -0.005788 | [-0.01146, -0.0001796] | -0.002116 | 53 / 16 / 31 | 0.0208 | 0.0393 | yes | none | negative | n/a |
| R19 | sparse (n = 100) | TimesFM 3 | 30 | T1 `timesfm3_completed` | 0.3563 | 0.3541 | 0.002242 | [-0.0001507, 0.004805] | 0 | 35 / 20 / 45 | 0.194 | 0.241 | no | negative | none (0) | neither (median 0) |
| R20 | sparse (n = 100) | TimesFM 3 | 30 | T2 `hurdle_empirical_28` | 0.3563 | 0.3615 | -0.005173 | [-0.009237, -0.001407] | -0.002469 | 58 / 18 / 24 | 0.00085 | 0.00219 | yes | none | negative | n/a |
| R21 | sparse (n = 100) | TimesFM 2.5 | 7 | T1 `timesfm2p5_completed` | 0.3618 | 0.3668 | -0.004921 | [-0.009302, -0.0003386] | -0.002116 | 57 / 8 / 35 | 0.00198 | 0.00445 | yes | negative | negative | yes |
| R22 | sparse (n = 100) | TimesFM 2.5 | 7 | T2 `hurdle_empirical_28` | 0.3618 | 0.3664 | -0.004561 | [-0.009979, 0.0009841] | -0.002646 | 55 / 17 / 28 | 0.0275 | 0.0471 | yes | none | negative | n/a |
| R23 | sparse (n = 100) | TimesFM 2.5 | 30 | T1 `timesfm2p5_completed` | 0.3571 | 0.3581 | -0.0009852 | [-0.003595, 0.001825] | -0.0004938 | 53 / 11 / 36 | 0.0349 | 0.0547 | no | negative | negative | yes |
| R24 | sparse (n = 100) | TimesFM 2.5 | 30 | T2 `hurdle_empirical_28` | 0.3571 | 0.3615 | -0.004422 | [-0.00836, -0.0006642] | -0.002469 | 58 / 17 / 25 | 0.00118 | 0.00283 | yes | none | negative | n/a |
| R25 | very sparse (n = 100) | Chronos-2 | 7 | T1 `chronos2_completed` | 0.05527 | 0.05273 | 0.00254 | [-0.0002222, 0.006762] | 0 | 2 / 88 / 10 | 0.0342 | 0.0547 | no | negative | none (0) | neither (median 0) |
| R26 | very sparse (n = 100) | Chronos-2 | 7 | T2 `hurdle_empirical_28` | 0.05527 | 0.0557 | -0.0004339 | [-0.001376, 0.000582] | 0 | 17 / 75 / 8 | 0.103 | 0.138 | no | none | none (0) | n/a |
| R27 | very sparse (n = 100) | Chronos-2 | 30 | T1 `chronos2_completed` | 0.06064 | 0.06013 | 0.0005086 | [-0.001496, 0.003388] | 0 | 11 / 82 / 7 | 0.5 | 0.545 | no | negative | none (0) | neither (median 0) |
| R28 | very sparse (n = 100) | Chronos-2 | 30 | T2 `hurdle_empirical_28` | 0.06064 | 0.06132 | -0.000679 | [-0.001383, 0.0002247] | 0 | 22 / 77 / 1 | 0.000464 | 0.00128 | yes | none | none (0) | n/a |
| R29 | very sparse (n = 100) | TimesFM 3 | 7 | T1 `timesfm3_completed` | 0.05524 | 0.05298 | 0.002254 | [-0.0002857, 0.006667] | 0 | 7 / 84 / 9 | 0.717 | 0.738 | no | negative | none (0) | neither (median 0) |
| R30 | very sparse (n = 100) | TimesFM 3 | 7 | T2 `hurdle_empirical_28` | 0.05524 | 0.0557 | -0.0004656 | [-0.001354, 0.0004868] | 0 | 17 / 75 / 8 | 0.182 | 0.235 | no | none | none (0) | n/a |
| R31 | very sparse (n = 100) | TimesFM 3 | 30 | T1 `timesfm3_completed` | 0.06088 | 0.05797 | 0.002911 | [-0.0005901, 0.009531] | 0 | 18 / 72 / 10 | 0.264 | 0.317 | no | negative | none (0) | neither (median 0) |
| R32 | very sparse (n = 100) | TimesFM 3 | 30 | T2 `hurdle_empirical_28` | 0.06088 | 0.06132 | -0.0004444 | [-0.001432, 0.001012] | 0 | 22 / 77 / 1 | 0.000464 | 0.00128 | yes | none | none (0) | n/a |
| R33 | very sparse (n = 100) | TimesFM 2.5 | 7 | T1 `timesfm2p5_completed` | 0.05523 | 0.05327 | 0.001958 | [-0.0006243, 0.006116] | 0 | 3 / 87 / 10 | 0.0463 | 0.0694 | no | negative | none (0) | neither (median 0) |
| R34 | very sparse (n = 100) | TimesFM 2.5 | 7 | T2 `hurdle_empirical_28` | 0.05523 | 0.0557 | -0.0004762 | [-0.001386, 0.0004868] | 0 | 17 / 75 / 8 | 0.103 | 0.138 | no | none | none (0) | n/a |
| R35 | very sparse (n = 100) | TimesFM 2.5 | 30 | T1 `timesfm2p5_completed` | 0.06102 | 0.05939 | 0.001632 | [-0.001728, 0.007084] | 0 | 7 / 86 / 7 | 0.826 | 0.826 | no | negative | none (0) | neither (median 0) |
| R36 | very sparse (n = 100) | TimesFM 2.5 | 30 | T2 `hurdle_empirical_28` | 0.06102 | 0.06132 | -0.0003037 | [-0.001407, 0.001459] | 0 | 22 / 77 / 1 | 0.000464 | 0.00128 | yes | none | none (0) | n/a |

## What the family says

**Twenty-one of the thirty-six tests reject at BH q = 0.05.**

- **Six are T1 tests in the dense stratum,** against hurdle_dynamic, as H3 predicts.
- **One is a T1 test in the sparse stratum,** for hurdle_dynamic, as H3 predicts.
- **Fourteen are T2 tests,** all for hurdle_dynamic.
- No test rejects in a direction opposite to H3's prediction, and no T1 median has the opposite sign.

**Dense stratum, against the completed control (R01, R03, R05, R07, R09, R11): H3's predicted sign holds, and all six
reject.**

- For all three models at both horizons, the substitution raises QScore9.
- hurdle_dynamic scores higher than the completed control on 55 to 72 of the 100 series.
- The medians run from +0.0041 to +0.0127 and the means from +0.015 to +0.022, about 1% of the control's mean score of
  1.70 to 1.83.
- The rank sums favor the control in every row.

**Sparse stratum, against the completed control (R13, R15, R17, R19, R21, R23): H3's predicted sign is not
established.**

- **One test rejects, in the predicted direction:** R21, TimesFM 2.5 at horizon 7. Its median is -0.0021, with 57
  series lower, 8 tied and 35 higher, BH p 0.0045.
- **One more median is negative without rejecting:** R23, TimesFM 2.5 at horizon 30, median -0.00049, BH p 0.055.
- **The other four medians are exactly zero,** with 12 to 23 series tied exactly and none rejecting. Their rank sums
  lean to hurdle_dynamic for R13, R15 and R17 and to the control for R19.
- **The means** run from -0.0049 to +0.0022, against control means of 0.354 to 0.367.

**Very sparse stratum, against the completed control (R25, R27, R29, R31, R33, R35): no test rejects, and every
median is exactly zero.**

- **Ties:** 72 to 88 of the 100 series score exactly the same under hurdle_dynamic as under the control.
- **The means** are positive, +0.0005 to +0.0029, and every interval includes zero.
- **The rank sums** lean to the control at horizon 7 (R25, R29, R33) and to hurdle_dynamic at horizon 30 (R27, R31,
  R35).
- **The smallest BH p is 0.055** (R25).
- **One series,** `["Sewer Maintenance","09 QUEENS"]`, moves the mean most in all six rows.

So on NYC 311, the half of H3 that concerns dense series is confirmed for every model and horizon. The half that
concerns sparse and very sparse series is not: of its twelve tests, one rejects in the predicted direction and eleven
do not reject. Ten of the twelve medians are exactly zero: between 12 and 88 of the 100 series in each of those rows
score exactly the same under hurdle_dynamic as under the control.

**Against `hurdle_empirical_28` (T2), hurdle_dynamic is lower wherever a test rejects.**

| Stratum | Rows that reject | Series lower | Medians | Rows not rejected |
|---|---|---|---|---|
| dense | all six (R02 to R12) | 72 to 87 of 100 | -0.056 to -0.068 | none |
| sparse | five of six (R16, R18, R20, R22, R24) | 53 to 58 | -0.0019 to -0.0026 | R14, Chronos-2 at horizon 7: median exactly zero, BH p 0.14 |
| very sparse | the three horizon-30 rows (R28, R32, R36) | 22 lower, 77 tied, 1 higher | exactly zero | the three horizon-7 rows (R26, R30, R34): BH p 0.14 to 0.24 |

In the very sparse rows that reject, the direction comes from the rank sums (253 against 23), not from a median.

## The direction of each family test, from the paired table

Rank sums of the absolute nonzero series differences (average ranks for ties), split by sign; the larger sum names the side the signed-rank test leans to. The p-value is recomputed with SciPy (two-sided, approximate, zero differences omitted) beside the saved one.

| ID | Stratum | Exact ties | Nonzero | Rank sum, hurdle_dynamic lower | Rank sum, reference lower | Larger sum favors | Raw p recomputed | Raw p saved |
|---|---|---|---|---|---|---|---|---|
| R01 | dense (n = 100) | 1 | 99 | 1,713.5 | 3,236.5 | reference | 0.00786 | 0.00786 |
| R02 | dense (n = 100) | 1 | 99 | 4,144.0 | 806.0 | hurdle_dynamic | 5.7e-09 | 5.7e-09 |
| R03 | dense (n = 100) | 2 | 98 | 1,737.0 | 3,114.0 | reference | 0.0147 | 0.0147 |
| R04 | dense (n = 100) | 0 | 100 | 4,744.0 | 306.0 | hurdle_dynamic | 2.35e-14 | 2.35e-14 |
| R05 | dense (n = 100) | 2 | 98 | 1,204.0 | 3,647.0 | reference | 1.5e-05 | 1.5e-05 |
| R06 | dense (n = 100) | 0 | 100 | 4,173.5 | 876.5 | hurdle_dynamic | 1.44e-08 | 1.44e-08 |
| R07 | dense (n = 100) | 0 | 100 | 1,217.0 | 3,833.0 | reference | 6.88e-06 | 6.88e-06 |
| R08 | dense (n = 100) | 0 | 100 | 4,665.0 | 385.0 | hurdle_dynamic | 1.87e-13 | 1.87e-13 |
| R09 | dense (n = 100) | 2 | 98 | 1,200.0 | 3,651.0 | reference | 1.41e-05 | 1.41e-05 |
| R10 | dense (n = 100) | 0 | 100 | 4,303.5 | 746.5 | hurdle_dynamic | 9.65e-10 | 9.65e-10 |
| R11 | dense (n = 100) | 0 | 100 | 942.5 | 4,107.5 | reference | 5.29e-08 | 5.29e-08 |
| R12 | dense (n = 100) | 0 | 100 | 4,666.5 | 383.5 | hurdle_dynamic | 1.8e-13 | 1.8e-13 |
| R13 | sparse (n = 100) | 13 | 87 | 2,064.0 | 1,764.0 | hurdle_dynamic | 0.526 | 0.526 |
| R14 | sparse (n = 100) | 15 | 85 | 2,200.5 | 1,454.5 | hurdle_dynamic | 0.102 | 0.102 |
| R15 | sparse (n = 100) | 12 | 88 | 2,179.5 | 1,736.5 | hurdle_dynamic | 0.357 | 0.357 |
| R16 | sparse (n = 100) | 15 | 85 | 2,331.0 | 1,324.0 | hurdle_dynamic | 0.0274 | 0.0274 |
| R17 | sparse (n = 100) | 23 | 77 | 1,658.5 | 1,344.5 | hurdle_dynamic | 0.425 | 0.425 |
| R18 | sparse (n = 100) | 16 | 84 | 2,303.5 | 1,266.5 | hurdle_dynamic | 0.0208 | 0.0208 |
| R19 | sparse (n = 100) | 20 | 80 | 1,349.5 | 1,890.5 | reference | 0.194 | 0.194 |
| R20 | sparse (n = 100) | 18 | 82 | 2,423.0 | 980.0 | hurdle_dynamic | 0.00085 | 0.00085 |
| R21 | sparse (n = 100) | 8 | 92 | 2,933.5 | 1,344.5 | hurdle_dynamic | 0.00198 | 0.00198 |
| R22 | sparse (n = 100) | 17 | 83 | 2,228.5 | 1,257.5 | hurdle_dynamic | 0.0275 | 0.0275 |
| R23 | sparse (n = 100) | 11 | 89 | 2,518.0 | 1,487.0 | hurdle_dynamic | 0.0349 | 0.0349 |
| R24 | sparse (n = 100) | 17 | 83 | 2,457.5 | 1,028.5 | hurdle_dynamic | 0.00118 | 0.00118 |
| R25 | very sparse (n = 100) | 88 | 12 | 12.0 | 66.0 | reference | 0.0342 | 0.0342 |
| R26 | very sparse (n = 100) | 75 | 25 | 223.0 | 102.0 | hurdle_dynamic | 0.103 | 0.103 |
| R27 | very sparse (n = 100) | 82 | 18 | 101.0 | 70.0 | hurdle_dynamic | 0.5 | 0.5 |
| R28 | very sparse (n = 100) | 77 | 23 | 253.0 | 23.0 | hurdle_dynamic | 0.000464 | 0.000464 |
| R29 | very sparse (n = 100) | 84 | 16 | 61.0 | 75.0 | reference | 0.717 | 0.717 |
| R30 | very sparse (n = 100) | 75 | 25 | 212.0 | 113.0 | hurdle_dynamic | 0.182 | 0.182 |
| R31 | very sparse (n = 100) | 72 | 28 | 252.0 | 154.0 | hurdle_dynamic | 0.264 | 0.264 |
| R32 | very sparse (n = 100) | 77 | 23 | 253.0 | 23.0 | hurdle_dynamic | 0.000464 | 0.000464 |
| R33 | very sparse (n = 100) | 87 | 13 | 17.0 | 74.0 | reference | 0.0463 | 0.0463 |
| R34 | very sparse (n = 100) | 75 | 25 | 223.0 | 102.0 | hurdle_dynamic | 0.103 | 0.103 |
| R35 | very sparse (n = 100) | 86 | 14 | 56.0 | 49.0 | hurdle_dynamic | 0.826 | 0.826 |
| R36 | very sparse (n = 100) | 77 | 23 | 253.0 | 23.0 | hurdle_dynamic | 0.000464 | 0.000464 |

## The panel's strata and their zero contexts

The frozen manifest holds 300 series; every stratum table below states its n. The strata window is 2026-03-05 to 2026-06-02 (90 days) and the context at the first origin is 2025-09-01 to 2026-06-02 (275 days).

| Stratum | Series | All-zero strata window | All-zero context at the first origin (275 days) |
|---|---|---|---|
| dense | 100 | 0 | 0 |
| sparse | 100 | 0 | 0 |
| very sparse | 100 | 39 | 19 |
| all | 300 | 39 | 19 |

## The contexts at each origin: request days in the last 28 days

With fewer than two request days in the last 28 days of a context, dynamic_count takes hurdle_count_28's law, so hurdle_dynamic equals hurdle_fixed for that window by the registered fallback. Counted from the signals, before and apart from any score.

| Stratum | Origin | Context days | All-zero context | No request day in the last 28 | Fewer than two request days in the last 28 |
|---|---|---|---|---|---|
| dense (n = 100) | 2026-06-03 | 275 | 0 | 0 | 0 |
| dense (n = 100) | 2026-07-03 | 305 | 0 | 0 | 0 |
| dense (n = 100) | 2026-08-02 | 335 | 0 | 0 | 0 |
| sparse (n = 100) | 2026-06-03 | 275 | 0 | 1 | 4 |
| sparse (n = 100) | 2026-07-03 | 305 | 0 | 3 | 7 |
| sparse (n = 100) | 2026-08-02 | 335 | 0 | 1 | 8 |
| very sparse (n = 100) | 2026-06-03 | 275 | 19 | 58 | 74 |
| very sparse (n = 100) | 2026-07-03 | 305 | 18 | 54 | 74 |
| very sparse (n = 100) | 2026-08-02 | 335 | 15 | 54 | 72 |

## Secondary results

Everything from here on is secondary, as the addition declares it: unadjusted unless a column says otherwise, and
never confirmatory. Every per-stratum table states its n. In brief, from the per-stratum QScore9 tables below:

- **Study 2's hurdle with the fixed 28-day occurrence (hurdle_fixed) against the completed control:**
  - dense: higher for all three models at both horizons, on 60 to 70 of the 100 series;
  - sparse: mixed, higher on 45 to 60 of 100;
  - very sparse: higher in all six rows, on 20 to 23 series against 5 to 9 lower, with 69 to 73 tied, unadjusted p
    0.0029 to 0.025.

  hurdle_dynamic's very sparse T1 rows, by contrast, do not reject.
- **The fourth cell (occurrence_model_size_count), the model's own occurrence with the count positive law:**
  - dense: much higher than the control, with mean differences of +0.29 to +0.33 and higher on 70 to 91 series;
  - sparse and very sparse: within 0.004 of the control's mean, with 29 to 98 of the 100 series tied exactly.
- **Pooled over all 300 series in Study 2's form (P01 to P18):**
  - the fixed hurdle's mean is higher than its completed control's in all six rows, with more series higher than
    lower;
  - its mean is lower than `hurdle_count_28`'s in all six, with more series lower than higher;
  - each raw model's mean is lower than `local_mean_28`'s in all six, while the series split close to evenly (128
    to 161 lower, 124 to 157 higher).

  Every row has a within-table BH p below 0.005. Pooling weights the three strata equally and does not test H3.

## Skill and concentration of the family's comparisons (secondary, descriptive)

Study 1's definitions: skill 1 - hurdle_dynamic / reference per series, undefined where the reference is zero; the share of the positive gains held by the five largest; the range of the mean difference with one series left out, and the series whose omission moves it most.

| ID | Stratum | Mean skill | Median skill | Skill defined | Top-five share of positive gains | Mean difference, one series left out: range | Series whose omission moves the mean most | Its difference |
|---|---|---|---|---|---|---|---|---|
| R01 | dense (n = 100) | -0.01006 | -0.005666 | 100 of 100 | 0.349 | [0.01458, 0.01904] | `["Water System","09 QUEENS"]` | 0.3312 |
| R02 | dense (n = 100) | 0.05663 | 0.05045 | 100 of 100 | 0.584 | [-0.2177, -0.1387] | `["Noise - Residential","12 QUEENS"]` | -7.162 |
| R03 | dense (n = 100) | -0.01146 | -0.00204 | 100 of 100 | 0.336 | [0.01337, 0.01603] | `["Water System","02 BROOKLYN"]` | 0.1879 |
| R04 | dense (n = 100) | 0.06061 | 0.04745 | 100 of 100 | 0.588 | [-0.2192, -0.1434] | `["Noise - Residential","12 QUEENS"]` | -7.28 |
| R05 | dense (n = 100) | -0.01313 | -0.007859 | 100 of 100 | 0.457 | [0.01862, 0.02192] | `["Water System","09 QUEENS"]` | 0.255 |
| R06 | dense (n = 100) | 0.05517 | 0.05114 | 100 of 100 | 0.616 | [-0.2191, -0.1416] | `["Noise - Residential","12 QUEENS"]` | -7.16 |
| R07 | dense (n = 100) | -0.0123 | -0.007537 | 100 of 100 | 0.465 | [0.01507, 0.01704] | `["GENERAL","01 QUEENS"]` | 0.1447 |
| R08 | dense (n = 100) | 0.06167 | 0.05271 | 100 of 100 | 0.589 | [-0.2245, -0.1461] | `["Noise - Residential","12 QUEENS"]` | -7.478 |
| R09 | dense (n = 100) | -0.01344 | -0.008949 | 100 of 100 | 0.408 | [0.01953, 0.02318] | `["GENERAL","01 QUEENS"]` | 0.2857 |
| R10 | dense (n = 100) | 0.0564 | 0.04907 | 100 of 100 | 0.593 | [-0.2223, -0.1431] | `["Noise - Residential","12 QUEENS"]` | -7.218 |
| R11 | dense (n = 100) | -0.01394 | -0.008133 | 100 of 100 | 0.564 | [0.01742, 0.0194] | `["Water System","09 QUEENS"]` | 0.137 |
| R12 | dense (n = 100) | 0.06194 | 0.051 | 100 of 100 | 0.565 | [-0.2168, -0.1442] | `["Noise - Residential","12 QUEENS"]` | -6.986 |
| R13 | sparse (n = 100) | -0.1294 | 0 | 100 of 100 | 0.346 | [-0.002854, -0.001165] | `["Street Light Condition","03 BRONX"]` | -0.09841 |
| R14 | sparse (n = 100) | 0.0169 | 0 | 99 of 100 | 0.322 | [-0.006392, -0.004201] | `["Street Light Condition","03 BRONX"]` | -0.1259 |
| R15 | sparse (n = 100) | -0.03932 | 0 | 100 of 100 | 0.38 | [-0.002255, -0.001013] | `["Drug Activity","11 BRONX"]` | -0.06519 |
| R16 | sparse (n = 100) | 0.01018 | 0.005323 | 100 of 100 | 0.398 | [-0.004619, -0.002863] | `["Encampment","01 BRONX"]` | -0.1212 |
| R17 | sparse (n = 100) | 0.02377 | 0 | 100 of 100 | 0.323 | [-0.0005986, 0.000962] | `["Overgrown Tree/Branches","08 BROOKLYN"]` | 0.08995 |
| R18 | sparse (n = 100) | 0.02297 | 0.00578 | 99 of 100 | 0.3 | [-0.006734, -0.004778] | `["Street Light Condition","03 BRONX"]` | -0.1058 |
| R19 | sparse (n = 100) | 0.0004544 | 0 | 100 of 100 | 0.421 | [0.001698, 0.002594] | `["Noise - Park","07 QUEENS"]` | 0.05605 |
| R20 | sparse (n = 100) | 0.01491 | 0.008265 | 100 of 100 | 0.378 | [-0.005754, -0.004013] | `["Encampment","01 BRONX"]` | -0.12 |
| R21 | sparse (n = 100) | 0.01226 | 0.01282 | 97 of 100 | 0.241 | [-0.005847, -0.004211] | `["Overgrown Tree/Branches","08 BROOKLYN"]` | 0.08677 |
| R22 | sparse (n = 100) | 0.02291 | 0.005319 | 99 of 100 | 0.294 | [-0.005804, -0.003773] | `["Encampment","08 BROOKLYN"]` | 0.1185 |
| R23 | sparse (n = 100) | -0.009441 | 0.002691 | 100 of 100 | 0.269 | [-0.001531, -0.0006584] | `["Dead/Dying Tree","18 BROOKLYN"]` | 0.05309 |
| R24 | sparse (n = 100) | 0.01406 | 0.007661 | 100 of 100 | 0.362 | [-0.004958, -0.003379] | `["Encampment","01 BRONX"]` | -0.1077 |
| R25 | very sparse (n = 100) | -0.1324 | 0 | 44 of 100 | 1 | [0.0007803, 0.002961] | `["Sewer Maintenance","09 QUEENS"]` | 0.1767 |
| R26 | very sparse (n = 100) | 0.09375 | 0 | 46 of 100 | 0.405 | [-0.0007162, -0.0002886] | `["Lot Condition","08 BROOKLYN"]` | 0.02751 |
| R27 | very sparse (n = 100) | 0.03078 | 0 | 67 of 100 | 0.905 | [-0.0006784, 0.0009602] | `["Sewer Maintenance","09 QUEENS"]` | 0.118 |
| R28 | very sparse (n = 100) | 0.02287 | 0 | 65 of 100 | 0.417 | [-0.001018, -0.0005362] | `["Sewer Maintenance","09 QUEENS"]` | 0.03284 |
| R29 | very sparse (n = 100) | 0.007494 | 0 | 43 of 100 | 0.86 | [0.0003527, 0.002426] | `["Sewer Maintenance","09 QUEENS"]` | 0.1905 |
| R30 | very sparse (n = 100) | 0.09403 | 0 | 46 of 100 | 0.405 | [-0.0007055, -0.0003207] | `["Lot Condition","08 BROOKLYN"]` | 0.02328 |
| R31 | very sparse (n = 100) | 0.02016 | 0 | 66 of 100 | 0.515 | [-0.0002694, 0.003015] | `["Sewer Maintenance","09 QUEENS"]` | 0.3178 |
| R32 | very sparse (n = 100) | 0.02285 | 0 | 65 of 100 | 0.405 | [-0.001048, -0.0002993] | `["Sewer Maintenance","09 QUEENS"]` | 0.05926 |
| R33 | very sparse (n = 100) | 0.008712 | 0 | 43 of 100 | 1 | [0.0001603, 0.002405] | `["Sewer Maintenance","09 QUEENS"]` | 0.1799 |
| R34 | very sparse (n = 100) | 0.09406 | 0 | 46 of 100 | 0.405 | [-0.0007162, -0.0003314] | `["Lot Condition","08 BROOKLYN"]` | 0.02328 |
| R35 | very sparse (n = 100) | 0.0273 | 0 | 67 of 100 | 0.969 | [-0.0007258, 0.00224] | `["Sewer Maintenance","09 QUEENS"]` | 0.2351 |
| R36 | very sparse (n = 100) | 0.02274 | 0 | 65 of 100 | 0.405 | [-0.001048, -0.0001571] | `["Sewer Maintenance","09 QUEENS"]` | 0.07333 |

## Per stratum: hurdle_fixed and occurrence_model_size_count, QScore9 (secondary, unadjusted)

hurdle_fixed is the run's `<model>_hurdle` (Study 2's hurdle); negative favors the variant named first.

### dense (n = 100)

| Variant | Reference | h | Variant mean | Reference mean | Mean difference | 95% interval | Median difference | Lower / tied / higher | Raw p |
|---|---|---|---|---|---|---|---|---|---|
| `chronos2_hurdle` | `chronos2_completed` | 7 | 1.854 | 1.833 | 0.02145 | [0.006423, 0.03832] | 0.01058 | 39 / 1 / 60 | 0.00867 |
| `chronos2_hurdle` | `hurdle_count_28` | 7 | 1.854 | 2.172 | -0.318 | [-0.5864, -0.1454] | -0.07566 | 82 / 0 / 18 | 4.31e-10 |
| `chronos2_hurdle` | `hurdle_empirical_28` | 7 | 1.854 | 2.06 | -0.2052 | [-0.3833, -0.08331] | -0.04815 | 78 / 0 / 22 | 1.37e-08 |
| `chronos2_occurrence_model_size_count` | `chronos2_completed` | 7 | 2.127 | 1.833 | 0.2944 | [0.1243, 0.5658] | 0.04127 | 30 / 0 / 70 | 5.19e-08 |
| `chronos2_occurrence_model_size_count` | `hurdle_count_28` | 7 | 2.127 | 2.172 | -0.04508 | [-0.06839, -0.02455] | -0.02963 | 68 / 1 / 31 | 3.33e-05 |
| `chronos2_occurrence_model_size_count` | `hurdle_empirical_28` | 7 | 2.127 | 2.06 | 0.06771 | [0.002751, 0.1645] | -0.01111 | 58 / 0 / 42 | 0.975 |
| `chronos2_hurdle` | `chronos2_completed` | 30 | 1.733 | 1.709 | 0.02404 | [0.0118, 0.04064] | 0.008519 | 30 / 0 / 70 | 8.87e-05 |
| `chronos2_hurdle` | `hurdle_count_28` | 30 | 1.733 | 2.064 | -0.331 | [-0.5674, -0.1729] | -0.08506 | 90 / 0 / 10 | 3.37e-16 |
| `chronos2_hurdle` | `hurdle_empirical_28` | 30 | 1.733 | 1.939 | -0.2058 | [-0.3846, -0.0916] | -0.05346 | 86 / 0 / 14 | 4.82e-14 |
| `chronos2_occurrence_model_size_count` | `chronos2_completed` | 30 | 2.017 | 1.709 | 0.3083 | [0.1507, 0.551] | 0.05938 | 11 / 0 / 89 | 3.35e-15 |
| `chronos2_occurrence_model_size_count` | `hurdle_count_28` | 30 | 2.017 | 2.064 | -0.0467 | [-0.06682, -0.02862] | -0.02543 | 71 / 2 / 27 | 5.63e-07 |
| `chronos2_occurrence_model_size_count` | `hurdle_empirical_28` | 30 | 2.017 | 1.939 | 0.07846 | [0.02511, 0.1501] | -0.0002469 | 50 / 0 / 50 | 0.244 |
| `timesfm3_hurdle` | `timesfm3_completed` | 7 | 1.851 | 1.827 | 0.0246 | [0.01013, 0.04178] | 0.0127 | 37 / 0 / 63 | 0.000406 |
| `timesfm3_hurdle` | `hurdle_count_28` | 7 | 1.851 | 2.172 | -0.321 | [-0.5856, -0.1481] | -0.07302 | 84 / 0 / 16 | 3.71e-11 |
| `timesfm3_hurdle` | `hurdle_empirical_28` | 7 | 1.851 | 2.06 | -0.2082 | [-0.3873, -0.08375] | -0.04709 | 75 / 1 / 24 | 1.53e-08 |
| `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | 7 | 2.136 | 1.827 | 0.3094 | [0.1334, 0.5841] | 0.0672 | 20 / 2 / 78 | 1.83e-10 |
| `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | 7 | 2.136 | 2.172 | -0.03621 | [-0.05493, -0.01853] | -0.0127 | 62 / 4 / 34 | 0.000285 |
| `timesfm3_occurrence_model_size_count` | `hurdle_empirical_28` | 7 | 2.136 | 2.06 | 0.07658 | [0.01243, 0.1716] | 0.008466 | 45 / 0 / 55 | 0.167 |
| `timesfm3_hurdle` | `timesfm3_completed` | 30 | 1.726 | 1.703 | 0.02287 | [0.01218, 0.03763] | 0.009877 | 27 / 3 / 70 | 1.54e-06 |
| `timesfm3_hurdle` | `hurdle_count_28` | 30 | 1.726 | 2.064 | -0.338 | [-0.5785, -0.1793] | -0.09395 | 92 / 1 / 7 | 3.64e-16 |
| `timesfm3_hurdle` | `hurdle_empirical_28` | 30 | 1.726 | 1.939 | -0.2129 | [-0.3935, -0.0956] | -0.05901 | 88 / 0 / 12 | 1.8e-14 |
| `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | 30 | 2.028 | 1.703 | 0.325 | [0.1639, 0.5717] | 0.08185 | 10 / 0 / 90 | 3.01e-16 |
| `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | 30 | 2.028 | 2.064 | -0.03591 | [-0.05251, -0.02066] | -0.007778 | 63 / 3 / 34 | 1.98e-05 |
| `timesfm3_occurrence_model_size_count` | `hurdle_empirical_28` | 30 | 2.028 | 1.939 | 0.08925 | [0.03456, 0.1626] | 0.008519 | 42 / 1 / 57 | 0.0258 |
| `timesfm2p5_hurdle` | `timesfm2p5_completed` | 7 | 1.848 | 1.824 | 0.02487 | [0.01025, 0.04186] | 0.01958 | 37 / 1 / 62 | 0.000246 |
| `timesfm2p5_hurdle` | `hurdle_count_28` | 7 | 1.848 | 2.172 | -0.3239 | [-0.5913, -0.1525] | -0.07196 | 83 / 0 / 17 | 1.2e-11 |
| `timesfm2p5_hurdle` | `hurdle_empirical_28` | 7 | 1.848 | 2.06 | -0.2111 | [-0.3916, -0.08986] | -0.04815 | 76 / 0 / 24 | 1.24e-09 |
| `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | 7 | 2.129 | 1.824 | 0.3059 | [0.1337, 0.5786] | 0.05503 | 19 / 0 / 81 | 1.24e-10 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | 7 | 2.129 | 2.172 | -0.04294 | [-0.06259, -0.02488] | -0.02646 | 73 / 2 / 25 | 5.74e-06 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_empirical_28` | 7 | 2.129 | 2.06 | 0.06985 | [0.005132, 0.1651] | 0.006878 | 48 / 0 / 52 | 0.604 |
| `timesfm2p5_hurdle` | `timesfm2p5_completed` | 30 | 1.732 | 1.707 | 0.0242 | [0.01379, 0.03789] | 0.01284 | 30 / 0 / 70 | 1.36e-06 |
| `timesfm2p5_hurdle` | `hurdle_count_28` | 30 | 1.732 | 2.064 | -0.3322 | [-0.5597, -0.179] | -0.08716 | 93 / 0 / 7 | 1.35e-16 |
| `timesfm2p5_hurdle` | `hurdle_empirical_28` | 30 | 1.732 | 1.939 | -0.2071 | [-0.3774, -0.09732] | -0.0516 | 87 / 0 / 13 | 1.53e-14 |
| `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | 30 | 2.021 | 1.707 | 0.3136 | [0.1599, 0.5483] | 0.07852 | 9 / 0 / 91 | 1.75e-16 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | 30 | 2.021 | 2.064 | -0.04287 | [-0.06056, -0.02653] | -0.02444 | 68 / 2 / 30 | 4.35e-07 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_empirical_28` | 30 | 2.021 | 1.939 | 0.08229 | [0.02727, 0.1538] | 0.00642 | 45 / 0 / 55 | 0.146 |

### sparse (n = 100)

| Variant | Reference | h | Variant mean | Reference mean | Mean difference | 95% interval | Median difference | Lower / tied / higher | Raw p |
|---|---|---|---|---|---|---|---|---|---|
| `chronos2_hurdle` | `chronos2_completed` | 7 | 0.3671 | 0.3631 | 0.003947 | [-0.001926, 0.009884] | 0.001587 | 41 / 7 / 52 | 0.282 |
| `chronos2_hurdle` | `hurdle_count_28` | 7 | 0.3671 | 0.3656 | 0.001503 | [-0.001693, 0.004889] | 0 | 26 / 31 / 43 | 0.139 |
| `chronos2_hurdle` | `hurdle_empirical_28` | 7 | 0.3671 | 0.3664 | 0.0006667 | [-0.001947, 0.003175] | 0 | 26 / 32 / 42 | 0.336 |
| `chronos2_occurrence_model_size_count` | `chronos2_completed` | 7 | 0.3634 | 0.3631 | 0.0002646 | [-0.001884, 0.002582] | 0 | 37 / 40 / 23 | 0.561 |
| `chronos2_occurrence_model_size_count` | `hurdle_count_28` | 7 | 0.3634 | 0.3656 | -0.00218 | [-0.00818, 0.003788] | -0.002646 | 53 / 7 / 40 | 0.405 |
| `chronos2_occurrence_model_size_count` | `hurdle_empirical_28` | 7 | 0.3634 | 0.3664 | -0.003016 | [-0.008773, 0.002603] | -0.001058 | 51 / 7 / 42 | 0.519 |
| `chronos2_hurdle` | `chronos2_completed` | 30 | 0.3617 | 0.3591 | 0.002637 | [-0.002126, 0.00682] | 0.002469 | 39 / 4 / 57 | 0.0384 |
| `chronos2_hurdle` | `hurdle_count_28` | 30 | 0.3617 | 0.3623 | -0.000521 | [-0.00363, 0.002314] | 0 | 23 / 28 / 49 | 0.0716 |
| `chronos2_hurdle` | `hurdle_empirical_28` | 30 | 0.3617 | 0.3615 | 0.0002444 | [-0.00243, 0.002795] | 0 | 26 / 27 / 47 | 0.0936 |
| `chronos2_occurrence_model_size_count` | `chronos2_completed` | 30 | 0.3593 | 0.3591 | 0.0002444 | [-0.0016, 0.001983] | 0 | 41 / 29 / 30 | 0.634 |
| `chronos2_occurrence_model_size_count` | `hurdle_count_28` | 30 | 0.3593 | 0.3623 | -0.002914 | [-0.007699, 0.001879] | -0.002099 | 54 / 5 / 41 | 0.164 |
| `chronos2_occurrence_model_size_count` | `hurdle_empirical_28` | 30 | 0.3593 | 0.3615 | -0.002148 | [-0.00659, 0.002612] | -0.002099 | 53 / 7 / 40 | 0.193 |
| `timesfm3_hurdle` | `timesfm3_completed` | 7 | 0.3645 | 0.3603 | 0.00419 | [-0.0004868, 0.009006] | 0 | 39 / 16 / 45 | 0.194 |
| `timesfm3_hurdle` | `hurdle_count_28` | 7 | 0.3645 | 0.3656 | -0.001069 | [-0.004709, 0.002751] | 0 | 26 / 48 / 26 | 0.433 |
| `timesfm3_hurdle` | `hurdle_empirical_28` | 7 | 0.3645 | 0.3664 | -0.001905 | [-0.004698, 0.0008148] | 0 | 26 / 50 / 24 | 0.302 |
| `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | 7 | 0.3621 | 0.3603 | 0.001778 | [-0.001926, 0.005048] | 0 | 17 / 53 / 30 | 0.064 |
| `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | 7 | 0.3621 | 0.3656 | -0.003481 | [-0.008286, 0.001196] | 0 | 47 / 14 / 39 | 0.251 |
| `timesfm3_occurrence_model_size_count` | `hurdle_empirical_28` | 7 | 0.3621 | 0.3664 | -0.004317 | [-0.009397, 0.0006138] | 0 | 47 / 14 / 39 | 0.244 |
| `timesfm3_hurdle` | `timesfm3_completed` | 30 | 0.3595 | 0.3541 | 0.005412 | [0.002622, 0.00822] | 0.00284 | 26 / 14 / 60 | 8e-05 |
| `timesfm3_hurdle` | `hurdle_count_28` | 30 | 0.3595 | 0.3623 | -0.002768 | [-0.005862, -0.0001727] | 0 | 29 / 48 / 23 | 0.224 |
| `timesfm3_hurdle` | `hurdle_empirical_28` | 30 | 0.3595 | 0.3615 | -0.002002 | [-0.00421, 1.735e-05] | 0 | 31 / 46 / 23 | 0.13 |
| `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | 30 | 0.3573 | 0.3541 | 0.003217 | [0.001284, 0.005247] | 0 | 14 / 51 / 35 | 0.00083 |
| `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | 30 | 0.3573 | 0.3623 | -0.004963 | [-0.008528, -0.001672] | -0.002469 | 58 / 14 / 28 | 0.00646 |
| `timesfm3_occurrence_model_size_count` | `hurdle_empirical_28` | 30 | 0.3573 | 0.3615 | -0.004198 | [-0.00722, -0.001163] | -0.002469 | 58 / 14 / 28 | 0.0029 |
| `timesfm2p5_hurdle` | `timesfm2p5_completed` | 7 | 0.3641 | 0.3668 | -0.002624 | [-0.007789, 0.002286] | 0.001058 | 43 / 6 / 51 | 0.587 |
| `timesfm2p5_hurdle` | `hurdle_count_28` | 7 | 0.3641 | 0.3656 | -0.001429 | [-0.004974, 0.002487] | 0 | 34 / 44 / 22 | 0.0676 |
| `timesfm2p5_hurdle` | `hurdle_empirical_28` | 7 | 0.3641 | 0.3664 | -0.002265 | [-0.004656, 8.466e-05] | 0 | 27 / 48 / 25 | 0.0765 |
| `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | 7 | 0.3692 | 0.3668 | 0.002455 | [-0.0003598, 0.00528] | 0 | 16 / 55 / 29 | 0.0515 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | 7 | 0.3692 | 0.3656 | 0.003651 | [-0.002222, 0.009672] | -0.0005291 | 50 / 7 / 43 | 0.465 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_empirical_28` | 7 | 0.3692 | 0.3664 | 0.002815 | [-0.002603, 0.008328] | 0 | 49 / 6 / 45 | 0.496 |
| `timesfm2p5_hurdle` | `timesfm2p5_completed` | 30 | 0.3593 | 0.3581 | 0.001286 | [-0.001778, 0.004353] | 0 | 44 / 7 / 49 | 0.362 |
| `timesfm2p5_hurdle` | `hurdle_count_28` | 30 | 0.3593 | 0.3623 | -0.002916 | [-0.005647, -0.0004839] | 0 | 38 / 39 / 23 | 0.0301 |
| `timesfm2p5_hurdle` | `hurdle_empirical_28` | 30 | 0.3593 | 0.3615 | -0.002151 | [-0.003956, -0.0004123] | 0 | 38 / 42 / 20 | 0.0276 |
| `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | 30 | 0.3612 | 0.3581 | 0.003146 | [0.0008222, 0.00581] | 0 | 18 / 51 / 31 | 0.0272 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | 30 | 0.3612 | 0.3623 | -0.001057 | [-0.004909, 0.002728] | -0.0001235 | 50 / 8 / 42 | 0.47 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_empirical_28` | 30 | 0.3612 | 0.3615 | -0.0002914 | [-0.003857, 0.003565] | -0.0002469 | 51 / 8 / 41 | 0.56 |

### very sparse (n = 100)

| Variant | Reference | h | Variant mean | Reference mean | Mean difference | 95% interval | Median difference | Lower / tied / higher | Raw p |
|---|---|---|---|---|---|---|---|---|---|
| `chronos2_hurdle` | `chronos2_completed` | 7 | 0.05538 | 0.05273 | 0.002646 | [0.000381, 0.005757] | 0 | 7 / 71 / 22 | 0.00293 |
| `chronos2_hurdle` | `hurdle_count_28` | 7 | 0.05538 | 0.0553 | 7.407e-05 | [-0.0004021, 0.000582] | 0 | 1 / 97 / 2 | 0.593 |
| `chronos2_hurdle` | `hurdle_empirical_28` | 7 | 0.05538 | 0.0557 | -0.000328 | [-0.001524, 0.0005397] | 0 | 1 / 98 / 1 | 0.655 |
| `chronos2_occurrence_model_size_count` | `chronos2_completed` | 7 | 0.05321 | 0.05273 | 0.0004762 | [-0.0002116, 0.001608] | 0 | 2 / 96 / 2 | 0.465 |
| `chronos2_occurrence_model_size_count` | `hurdle_count_28` | 7 | 0.05321 | 0.0553 | -0.002095 | [-0.004296, -0.0002116] | 0 | 22 / 71 / 7 | 0.00444 |
| `chronos2_occurrence_model_size_count` | `hurdle_empirical_28` | 7 | 0.05321 | 0.0557 | -0.002497 | [-0.005746, -6.349e-05] | 0 | 21 / 71 / 8 | 0.0125 |
| `chronos2_hurdle` | `chronos2_completed` | 30 | 0.06041 | 0.06013 | 0.0002741 | [-0.00101, 0.001341] | 0 | 8 / 69 / 23 | 0.0254 |
| `chronos2_hurdle` | `hurdle_count_28` | 30 | 0.06041 | 0.06107 | -0.0006667 | [-0.002174, 0.0002716] | 0 | 2 / 96 / 2 | 0.465 |
| `chronos2_hurdle` | `hurdle_empirical_28` | 30 | 0.06041 | 0.06132 | -0.0009136 | [-0.00317, 0.0003852] | 0 | 1 / 97 / 2 | 1 |
| `chronos2_occurrence_model_size_count` | `chronos2_completed` | 30 | 0.06109 | 0.06013 | 0.0009556 | [-5.926e-05, 0.002743] | 0 | 3 / 94 / 3 | 0.6 |
| `chronos2_occurrence_model_size_count` | `hurdle_count_28` | 30 | 0.06109 | 0.06107 | 1.481e-05 | [-0.001124, 0.00138] | 0 | 21 / 69 / 10 | 0.136 |
| `chronos2_occurrence_model_size_count` | `hurdle_empirical_28` | 30 | 0.06109 | 0.06132 | -0.0002321 | [-0.001294, 0.001047] | 0 | 22 / 69 / 9 | 0.0845 |
| `timesfm3_hurdle` | `timesfm3_completed` | 7 | 0.05504 | 0.05298 | 0.002053 | [0.000381, 0.004688] | 0 | 7 / 73 / 20 | 0.0116 |
| `timesfm3_hurdle` | `hurdle_count_28` | 7 | 0.05504 | 0.0553 | -0.0002646 | [-0.0008254, 0.0001481] | 0 | 2 / 97 / 1 | 0.285 |
| `timesfm3_hurdle` | `hurdle_empirical_28` | 7 | 0.05504 | 0.0557 | -0.0006667 | [-0.002222, 0.0002222] | 0 | 1 / 98 / 1 | 0.655 |
| `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | 7 | 0.05372 | 0.05298 | 0.0007407 | [1.058e-05, 0.001862] | 0 | 0 / 96 / 4 | 0.0679 |
| `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | 7 | 0.05372 | 0.0553 | -0.001577 | [-0.003651, -7.407e-05] | 0 | 19 / 73 / 8 | 0.0486 |
| `timesfm3_occurrence_model_size_count` | `hurdle_empirical_28` | 7 | 0.05372 | 0.0557 | -0.001979 | [-0.005323, 0.0001376] | 0 | 19 / 73 / 8 | 0.0575 |
| `timesfm3_hurdle` | `timesfm3_completed` | 30 | 0.06043 | 0.05797 | 0.002464 | [0.0004296, 0.006044] | 0 | 9 / 70 / 21 | 0.00531 |
| `timesfm3_hurdle` | `hurdle_count_28` | 30 | 0.06043 | 0.06107 | -0.0006444 | [-0.002007, 0.0001259] | 0 | 2 / 96 / 2 | 0.465 |
| `timesfm3_hurdle` | `hurdle_empirical_28` | 30 | 0.06043 | 0.06132 | -0.0008914 | [-0.00303, 0.0002519] | 0 | 1 / 96 / 3 | 0.713 |
| `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | 30 | 0.05963 | 0.05797 | 0.001667 | [4.938e-05, 0.004723] | 0 | 0 / 96 / 4 | 0.0679 |
| `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | 30 | 0.05963 | 0.06107 | -0.001442 | [-0.003462, -0.0001877] | 0 | 20 / 70 / 10 | 0.023 |
| `timesfm3_occurrence_model_size_count` | `hurdle_empirical_28` | 30 | 0.05963 | 0.06132 | -0.001689 | [-0.004491, -1.728e-05] | 0 | 19 / 70 / 11 | 0.0786 |
| `timesfm2p5_hurdle` | `timesfm2p5_completed` | 7 | 0.05515 | 0.05327 | 0.001884 | [-0.0003598, 0.004899] | 0 | 8 / 72 / 20 | 0.0157 |
| `timesfm2p5_hurdle` | `hurdle_count_28` | 7 | 0.05515 | 0.0553 | -0.0001481 | [-0.0004444, 0] | 0 | 1 / 99 / 0 | 0.317 |
| `timesfm2p5_hurdle` | `hurdle_empirical_28` | 7 | 0.05515 | 0.0557 | -0.0005503 | [-0.001651, 0] | 0 | 1 / 99 / 0 | 0.317 |
| `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | 7 | 0.05319 | 0.05327 | -8.466e-05 | [-0.0004127, 0.0001587] | 0 | 1 / 98 / 1 | 0.655 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | 7 | 0.05319 | 0.0553 | -0.002116 | [-0.005026, 0.0001058] | 0 | 21 / 71 / 8 | 0.00972 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_empirical_28` | 7 | 0.05319 | 0.0557 | -0.002519 | [-0.006646, 0.0002116] | 0 | 21 / 71 / 8 | 0.011 |
| `timesfm2p5_hurdle` | `timesfm2p5_completed` | 30 | 0.06085 | 0.05939 | 0.001462 | [-0.0007481, 0.004358] | 0 | 5 / 72 / 23 | 0.00456 |
| `timesfm2p5_hurdle` | `hurdle_count_28` | 30 | 0.06085 | 0.06107 | -0.0002272 | [-0.0006074, 9.877e-06] | 0 | 2 / 97 / 1 | 0.285 |
| `timesfm2p5_hurdle` | `hurdle_empirical_28` | 30 | 0.06085 | 0.06132 | -0.0004741 | [-0.001437, 1.481e-05] | 0 | 1 / 98 / 1 | 0.655 |
| `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | 30 | 0.05988 | 0.05939 | 0.0004938 | [-5.926e-05, 0.001506] | 0 | 1 / 96 / 3 | 0.465 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | 30 | 0.05988 | 0.06107 | -0.001195 | [-0.003267, 0.0006099] | 0 | 23 / 71 / 6 | 0.00492 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_empirical_28` | 30 | 0.05988 | 0.06132 | -0.001442 | [-0.004306, 0.000716] | 0 | 23 / 71 / 6 | 0.00641 |

## The family's pairs on the other scores, per stratum (secondary, unadjusted)

### Context-scaled QScore9

| ID | Stratum | Series | Unavailable | Mean difference | 95% interval | Median difference | Lower / tied / higher | Raw p | Status |
|---|---|---|---|---|---|---|---|---|---|
| R01 | dense (n = 100) | 100 | 0 | 0.006942 | [0.0014, 0.01255] | 0.002244 | 39 / 1 / 60 | 0.0185 | secondary |
| R02 | dense (n = 100) | 100 | 0 | -0.04189 | [-0.05832, -0.027] | -0.02506 | 76 / 0 / 24 | 4.29e-09 | secondary |
| R03 | dense (n = 100) | 100 | 0 | 0.004779 | [0.0002783, 0.009361] | 0.0007201 | 42 / 0 / 58 | 0.0333 | secondary |
| R04 | dense (n = 100) | 100 | 0 | -0.0393 | [-0.05058, -0.02965] | -0.0249 | 87 / 0 / 13 | 1.53e-14 | secondary |
| R05 | dense (n = 100) | 100 | 0 | 0.008251 | [0.004018, 0.01244] | 0.004428 | 29 / 1 / 70 | 3.13e-05 | secondary |
| R06 | dense (n = 100) | 100 | 0 | -0.04147 | [-0.06018, -0.02553] | -0.02292 | 75 / 0 / 25 | 7.87e-09 | secondary |
| R07 | dense (n = 100) | 100 | 0 | 0.006277 | [0.003486, 0.009154] | 0.003643 | 28 / 0 / 72 | 9.26e-06 | secondary |
| R08 | dense (n = 100) | 100 | 0 | -0.03932 | [-0.0505, -0.02953] | -0.0293 | 85 / 0 / 15 | 3.6e-14 | secondary |
| R09 | dense (n = 100) | 100 | 0 | 0.009133 | [0.005143, 0.01314] | 0.004074 | 32 / 0 / 68 | 7.25e-05 | secondary |
| R10 | dense (n = 100) | 100 | 0 | -0.04063 | [-0.05951, -0.02445] | -0.02342 | 72 / 0 / 28 | 2.95e-09 | secondary |
| R11 | dense (n = 100) | 100 | 0 | 0.007606 | [0.004981, 0.01032] | 0.004283 | 30 / 0 / 70 | 5.31e-07 | secondary |
| R12 | dense (n = 100) | 100 | 0 | -0.03918 | [-0.04983, -0.02991] | -0.0279 | 86 / 0 / 14 | 7.3e-15 | secondary |
| R13 | sparse (n = 100) | 100 | 0 | -0.002115 | [-0.007114, 0.002751] | 0 | 47 / 13 / 40 | 0.534 | secondary |
| R14 | sparse (n = 100) | 100 | 0 | -0.005252 | [-0.01085, 0.0001425] | 0 | 46 / 15 / 39 | 0.104 | secondary |
| R15 | sparse (n = 100) | 100 | 0 | -0.001689 | [-0.005014, 0.001597] | 0 | 44 / 12 / 44 | 0.346 | secondary |
| R16 | sparse (n = 100) | 100 | 0 | -0.004033 | [-0.00832, -9.209e-05] | -0.001852 | 53 / 15 / 32 | 0.0256 | secondary |
| R17 | sparse (n = 100) | 100 | 0 | 0.0004373 | [-0.00358, 0.004613] | 0 | 45 / 23 / 32 | 0.44 | secondary |
| R18 | sparse (n = 100) | 100 | 0 | -0.005674 | [-0.01125, -9.685e-06] | -0.002116 | 53 / 16 / 31 | 0.0224 | secondary |
| R19 | sparse (n = 100) | 100 | 0 | 0.002239 | [-0.000169, 0.004781] | 0 | 35 / 20 / 45 | 0.194 | secondary |
| R20 | sparse (n = 100) | 100 | 0 | -0.005151 | [-0.009175, -0.001458] | -0.002469 | 58 / 18 / 24 | 0.00085 | secondary |
| R21 | sparse (n = 100) | 100 | 0 | -0.004846 | [-0.009208, -0.0001991] | -0.002116 | 57 / 8 / 35 | 0.00208 | secondary |
| R22 | sparse (n = 100) | 100 | 0 | -0.004415 | [-0.009761, 0.001145] | -0.002646 | 55 / 17 / 28 | 0.0275 | secondary |
| R23 | sparse (n = 100) | 100 | 0 | -0.001028 | [-0.003637, 0.001732] | -0.0004938 | 53 / 11 / 36 | 0.0339 | secondary |
| R24 | sparse (n = 100) | 100 | 0 | -0.004385 | [-0.008284, -0.000693] | -0.002469 | 58 / 17 / 25 | 0.00124 | secondary |
| R25 | very sparse (n = 100) | 100 | 0 | 0.002907 | [0.0003885, 0.007249] | 0 | 2 / 88 / 10 | 0.00765 | secondary |
| R26 | very sparse (n = 100) | 100 | 0 | -0.0004339 | [-0.001376, 0.0006032] | 0 | 17 / 75 / 8 | 0.103 | secondary |
| R27 | very sparse (n = 100) | 100 | 0 | 0.0009225 | [-0.0006173, 0.003568] | 0 | 11 / 82 / 7 | 0.616 | secondary |
| R28 | very sparse (n = 100) | 100 | 0 | -0.000679 | [-0.001378, 0.0002] | 0 | 22 / 77 / 1 | 0.000464 | secondary |
| R29 | very sparse (n = 100) | 100 | 0 | 0.002254 | [-0.0002751, 0.006603] | 0 | 7 / 84 / 9 | 0.717 | secondary |
| R30 | very sparse (n = 100) | 100 | 0 | -0.0004656 | [-0.001376, 0.0004974] | 0 | 17 / 75 / 8 | 0.182 | secondary |
| R31 | very sparse (n = 100) | 100 | 0 | 0.002913 | [-0.0005831, 0.009531] | 0 | 18 / 72 / 10 | 0.264 | secondary |
| R32 | very sparse (n = 100) | 100 | 0 | -0.0004444 | [-0.001432, 0.001013] | 0 | 22 / 77 / 1 | 0.000464 | secondary |
| R33 | very sparse (n = 100) | 100 | 0 | 0.002354 | [0.0002059, 0.006301] | 0 | 3 / 87 / 10 | 0.0107 | secondary |
| R34 | very sparse (n = 100) | 100 | 0 | -0.0004762 | [-0.001386, 0.0004765] | 0 | 17 / 75 / 8 | 0.103 | secondary |
| R35 | very sparse (n = 100) | 100 | 0 | 0.002184 | [-0.0005212, 0.007149] | 0 | 7 / 86 / 7 | 0.975 | secondary |
| R36 | very sparse (n = 100) | 100 | 0 | -0.0003037 | [-0.001407, 0.001459] | 0 | 22 / 77 / 1 | 0.000464 | secondary |

### Occurrence Brier score

| ID | Stratum | Series | Unavailable | Mean difference | 95% interval | Median difference | Lower / tied / higher | Raw p | Status |
|---|---|---|---|---|---|---|---|---|---|
| R01 | dense (n = 100) | 100 | 0 | 0.009347 | [0.00366, 0.01535] | 0.001222 | 42 / 0 / 58 | 0.00281 | secondary |
| R02 | dense (n = 100) | 100 | 0 | -0.0009351 | [-0.003534, 0.00169] | -0.0002973 | 57 / 0 / 43 | 0.413 | secondary |
| R03 | dense (n = 100) | 100 | 0 | 0.007339 | [0.0031, 0.01212] | 0.0004494 | 46 / 0 / 54 | 0.0126 | secondary |
| R04 | dense (n = 100) | 100 | 0 | -0.0002877 | [-0.002394, 0.001957] | -0.0007675 | 69 / 0 / 31 | 0.00819 | secondary |
| R05 | dense (n = 100) | 100 | 0 | 0.008161 | [0.005026, 0.01149] | 0.003557 | 34 / 0 / 66 | 6.04e-06 | secondary |
| R06 | dense (n = 100) | 100 | 0 | -0.0009351 | [-0.003528, 0.001654] | -0.0002973 | 57 / 0 / 43 | 0.413 | secondary |
| R07 | dense (n = 100) | 100 | 0 | 0.00668 | [0.004291, 0.009265] | 0.001928 | 31 / 0 / 69 | 6e-08 | secondary |
| R08 | dense (n = 100) | 100 | 0 | -0.0002877 | [-0.00244, 0.001987] | -0.0007675 | 69 / 0 / 31 | 0.00819 | secondary |
| R09 | dense (n = 100) | 100 | 0 | 0.008898 | [0.005258, 0.01285] | 0.002921 | 42 / 0 / 58 | 0.000123 | secondary |
| R10 | dense (n = 100) | 100 | 0 | -0.0009351 | [-0.003544, 0.001678] | -0.0002973 | 57 / 0 / 43 | 0.413 | secondary |
| R11 | dense (n = 100) | 100 | 0 | 0.007193 | [0.00457, 0.01013] | 0.001605 | 38 / 0 / 62 | 4.73e-06 | secondary |
| R12 | dense (n = 100) | 100 | 0 | -0.0002877 | [-0.002371, 0.001994] | -0.0007675 | 69 / 0 / 31 | 0.00819 | secondary |
| R13 | sparse (n = 100) | 100 | 0 | -0.0004426 | [-0.003601, 0.002659] | -0.0002044 | 51 / 0 / 49 | 0.826 | secondary |
| R14 | sparse (n = 100) | 100 | 0 | -0.002326 | [-0.005655, 0.000959] | -0.001192 | 59 / 1 / 40 | 0.0952 | secondary |
| R15 | sparse (n = 100) | 100 | 0 | 0.0002249 | [-0.001732, 0.002244] | -5.1e-06 | 50 / 0 / 50 | 0.823 | secondary |
| R16 | sparse (n = 100) | 100 | 0 | -0.001293 | [-0.003594, 0.001094] | -0.0009633 | 62 / 1 / 37 | 0.0222 | secondary |
| R17 | sparse (n = 100) | 100 | 0 | 0.001134 | [-0.001429, 0.003961] | -0.0009403 | 56 / 0 / 44 | 0.698 | secondary |
| R18 | sparse (n = 100) | 100 | 0 | -0.002326 | [-0.005674, 0.0009332] | -0.001192 | 59 / 1 / 40 | 0.0952 | secondary |
| R19 | sparse (n = 100) | 100 | 0 | 0.002409 | [0.0006328, 0.004341] | 0.0006039 | 45 / 0 / 55 | 0.0934 | secondary |
| R20 | sparse (n = 100) | 100 | 0 | -0.001293 | [-0.003566, 0.001067] | -0.0009633 | 62 / 1 / 37 | 0.0222 | secondary |
| R21 | sparse (n = 100) | 100 | 0 | -0.002092 | [-0.005028, 0.0009558] | -0.002082 | 60 / 0 / 40 | 0.0259 | secondary |
| R22 | sparse (n = 100) | 100 | 0 | -0.002326 | [-0.005634, 0.0009471] | -0.001192 | 59 / 1 / 40 | 0.0952 | secondary |
| R23 | sparse (n = 100) | 100 | 0 | 0.0004917 | [-0.001208, 0.002362] | 1.279e-05 | 50 / 0 / 50 | 0.511 | secondary |
| R24 | sparse (n = 100) | 100 | 0 | -0.001293 | [-0.003604, 0.001109] | -0.0009633 | 62 / 1 / 37 | 0.0222 | secondary |
| R25 | very sparse (n = 100) | 100 | 0 | -5.043e-05 | [-0.001732, 0.002215] | -0.001841 | 68 / 0 / 32 | 0.00165 | secondary |
| R26 | very sparse (n = 100) | 100 | 0 | -3.603e-05 | [-0.001177, 0.001488] | 0 | 33 / 56 / 11 | 0.0208 | secondary |
| R27 | very sparse (n = 100) | 100 | 0 | -0.001279 | [-0.002628, 0.0002187] | -0.00163 | 73 / 0 / 27 | 1.59e-07 | secondary |
| R28 | very sparse (n = 100) | 100 | 0 | -9.498e-05 | [-0.001282, 0.001876] | 0 | 39 / 56 / 5 | 1.92e-06 | secondary |
| R29 | very sparse (n = 100) | 100 | 0 | 0.0001979 | [-0.001451, 0.002717] | -0.002363 | 70 / 0 / 30 | 0.000371 | secondary |
| R30 | very sparse (n = 100) | 100 | 0 | -3.603e-05 | [-0.001171, 0.001472] | 0 | 33 / 56 / 11 | 0.0208 | secondary |
| R31 | very sparse (n = 100) | 100 | 0 | -0.0002181 | [-0.001874, 0.002734] | -0.001629 | 82 / 0 / 18 | 1.01e-09 | secondary |
| R32 | very sparse (n = 100) | 100 | 0 | -9.498e-05 | [-0.001271, 0.001876] | 0 | 39 / 56 / 5 | 1.92e-06 | secondary |
| R33 | very sparse (n = 100) | 100 | 0 | -0.0001822 | [-0.001953, 0.002385] | -0.001928 | 68 / 0 / 32 | 0.00108 | secondary |
| R34 | very sparse (n = 100) | 100 | 0 | -3.603e-05 | [-0.001171, 0.001495] | 0 | 33 / 56 / 11 | 0.0208 | secondary |
| R35 | very sparse (n = 100) | 100 | 0 | -0.0005896 | [-0.002743, 0.002484] | -0.001625 | 75 / 0 / 25 | 1.88e-07 | secondary |
| R36 | very sparse (n = 100) | 100 | 0 | -9.498e-05 | [-0.001288, 0.001866] | 0 | 39 / 56 / 5 | 1.92e-06 | secondary |

### Discrete CRPS (available where both forecasts carry a certified law)

| ID | Stratum | Series | Unavailable | Mean difference | 95% interval | Median difference | Lower / tied / higher | Raw p | Status |
|---|---|---|---|---|---|---|---|---|---|
| R01 | dense (n = 100) | 100 | 0 | 0.01936 | [0.009928, 0.02952] | 0.01161 | 34 / 0 / 66 | 0.000225 | secondary |
| R02 | dense (n = 100) | 100 | 0 | -0.1896 | [-0.3516, -0.08093] | -0.05732 | 76 / 0 / 24 | 1.85e-09 | secondary |
| R03 | dense (n = 100) | 100 | 0 | 0.01447 | [0.007006, 0.02247] | 0.00483 | 37 / 0 / 63 | 0.00145 | secondary |
| R04 | dense (n = 100) | 100 | 0 | -0.1968 | [-0.3614, -0.09114] | -0.05979 | 86 / 0 / 14 | 2.48e-14 | secondary |
| R05 | dense (n = 100) | 100 | 0 | 0.01907 | [0.01111, 0.02828] | 0.01027 | 27 / 0 / 73 | 1.67e-06 | secondary |
| R06 | dense (n = 100) | 100 | 0 | -0.1952 | [-0.3508, -0.08208] | -0.05468 | 74 / 0 / 26 | 1.67e-09 | secondary |
| R07 | dense (n = 100) | 100 | 0 | 0.01439 | [0.008755, 0.02068] | 0.005164 | 29 / 0 / 71 | 2.92e-06 | secondary |
| R08 | dense (n = 100) | 100 | 0 | -0.2038 | [-0.3691, -0.09531] | -0.05887 | 89 / 0 / 11 | 3.07e-14 | secondary |
| R09 | dense (n = 100) | 100 | 0 | 0.02205 | [0.01366, 0.03144] | 0.0137 | 25 / 0 / 75 | 1.17e-07 | secondary |
| R10 | dense (n = 100) | 100 | 0 | -0.1945 | [-0.3532, -0.08421] | -0.05458 | 78 / 0 / 22 | 3.06e-10 | secondary |
| R11 | dense (n = 100) | 100 | 0 | 0.01667 | [0.01079, 0.02298] | 0.006744 | 28 / 0 / 72 | 1.61e-07 | secondary |
| R12 | dense (n = 100) | 100 | 0 | -0.1944 | [-0.3531, -0.09373] | -0.06264 | 88 / 0 / 12 | 3.07e-14 | secondary |
| R13 | sparse (n = 100) | 100 | 0 | 1.179e-05 | [-0.003521, 0.003498] | -0.000214 | 53 / 0 / 47 | 0.967 | secondary |
| R14 | sparse (n = 100) | 100 | 0 | -0.005006 | [-0.009252, -0.0008269] | -0.001399 | 62 / 0 / 38 | 0.023 | secondary |
| R15 | sparse (n = 100) | 100 | 0 | -0.0001521 | [-0.002715, 0.002359] | 0.0005232 | 45 / 0 / 55 | 0.744 | secondary |
| R16 | sparse (n = 100) | 100 | 0 | -0.003891 | [-0.007423, -0.0007153] | -0.001309 | 61 / 0 / 39 | 0.033 | secondary |
| R17 | sparse (n = 100) | 100 | 0 | 0.001816 | [-0.001774, 0.005822] | -0.001243 | 57 / 0 / 43 | 0.527 | secondary |
| R18 | sparse (n = 100) | 100 | 0 | -0.004832 | [-0.009339, -0.0002626] | -0.002279 | 63 / 0 / 37 | 0.0158 | secondary |
| R19 | sparse (n = 100) | 100 | 0 | 0.002461 | [0.0001844, 0.005053] | -9.744e-06 | 50 / 0 / 50 | 0.411 | secondary |
| R20 | sparse (n = 100) | 100 | 0 | -0.004542 | [-0.0081, -0.001217] | -0.002665 | 66 / 0 / 34 | 0.000441 | secondary |
| R21 | sparse (n = 100) | 100 | 0 | -0.0009643 | [-0.004617, 0.003024] | -0.001389 | 61 / 0 / 39 | 0.092 | secondary |
| R22 | sparse (n = 100) | 100 | 0 | -0.004319 | [-0.008894, 0.000591] | -0.002012 | 64 / 0 / 36 | 0.00972 | secondary |
| R23 | sparse (n = 100) | 100 | 0 | 0.001073 | [-0.001092, 0.003496] | 0.0002594 | 48 / 0 / 52 | 0.921 | secondary |
| R24 | sparse (n = 100) | 100 | 0 | -0.003987 | [-0.007482, -0.000682] | -0.001977 | 67 / 0 / 33 | 0.000378 | secondary |
| R25 | very sparse (n = 100) | 100 | 0 | 0.000945 | [-0.001912, 0.005234] | -0.002149 | 70 / 0 / 30 | 0.000499 | secondary |
| R26 | very sparse (n = 100) | 100 | 0 | 4.96e-05 | [-0.0011, 0.001566] | 4.653e-05 | 33 / 0 / 67 | 0.97 | secondary |
| R27 | very sparse (n = 100) | 100 | 0 | -0.0007844 | [-0.002948, 0.00251] | -0.002034 | 74 / 0 / 26 | 2.28e-08 | secondary |
| R28 | very sparse (n = 100) | 100 | 0 | -0.0005675 | [-0.001325, 0.0004859] | 4.653e-05 | 39 / 0 / 61 | 0.0657 | secondary |
| R29 | very sparse (n = 100) | 100 | 0 | 0.001042 | [-0.001787, 0.005792] | -0.002769 | 72 / 0 / 28 | 1.49e-05 | secondary |
| R30 | very sparse (n = 100) | 100 | 0 | -4.644e-05 | [-0.001107, 0.001254] | 4.653e-05 | 33 / 0 / 67 | 0.975 | secondary |
| R31 | very sparse (n = 100) | 100 | 0 | 0.001012 | [-0.002359, 0.007398] | -0.002035 | 83 / 0 / 17 | 3.99e-12 | secondary |
| R32 | very sparse (n = 100) | 100 | 0 | -0.0005088 | [-0.001356, 0.0007039] | 4.653e-05 | 39 / 0 / 61 | 0.0651 | secondary |
| R33 | very sparse (n = 100) | 100 | 0 | 0.0006084 | [-0.002319, 0.005346] | -0.002235 | 70 / 0 / 30 | 0.000236 | secondary |
| R34 | very sparse (n = 100) | 100 | 0 | 0.0002095 | [-0.001068, 0.001893] | 4.653e-05 | 33 / 0 / 67 | 0.975 | secondary |
| R35 | very sparse (n = 100) | 100 | 0 | 0.0004347 | [-0.003195, 0.006363] | -0.001959 | 74 / 0 / 26 | 3.66e-08 | secondary |
| R36 | very sparse (n = 100) | 100 | 0 | -9.954e-05 | [-0.001367, 0.001976] | 4.653e-05 | 38 / 0 / 62 | 0.0939 | secondary |

## Pooled over all 300 series, in Study 2's form (P01 to P18; secondary)

Study 2's eighteen contrasts in its order, every series weighted equally across strata; the BH column is within this table only and is not confirmatory.

| ID | Variant | Reference | h | Variant mean | Reference mean | Mean difference | 95% interval | Median difference | Lower / tied / higher | Raw p | BH p within the table |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P01 | `chronos2_hurdle` | `chronos2_completed` | 7 | 0.7589 | 0.7496 | 0.009347 | [0.003757, 0.01565] | 0 | 87 / 79 / 134 | 0.00158 | 0.00177 |
| P02 | `chronos2_hurdle` | `hurdle_count_28` | 7 | 0.7589 | 0.8644 | -0.1055 | [-0.1971, -0.04603] | 0 | 109 / 128 / 63 | 1.06e-07 | 2.12e-07 |
| P03 | `chronos2_raw` | `local_mean_28` | 7 | 0.7568 | 0.8331 | -0.07629 | [-0.1377, -0.03296] | 1.055e-09 | 144 / 0 / 156 | 0.000532 | 0.000684 |
| P04 | `chronos2_hurdle` | `chronos2_completed` | 30 | 0.7183 | 0.7094 | 0.008984 | [0.004368, 0.01474] | 0.0001235 | 77 / 73 / 150 | 5.35e-06 | 8.76e-06 |
| P05 | `chronos2_hurdle` | `hurdle_count_28` | 30 | 0.7183 | 0.8291 | -0.1107 | [-0.1922, -0.0559] | 0 | 115 / 124 / 61 | 7.04e-14 | 4.22e-13 |
| P06 | `chronos2_raw` | `local_mean_28` | 30 | 0.7162 | 0.7906 | -0.07444 | [-0.1358, -0.03425] | -0.0001298 | 151 / 0 / 149 | 9.47e-06 | 1.42e-05 |
| P07 | `timesfm3_hurdle` | `timesfm3_completed` | 7 | 0.757 | 0.7467 | 0.01028 | [0.00497, 0.01625] | 0 | 83 / 89 / 128 | 4.74e-05 | 6.57e-05 |
| P08 | `timesfm3_hurdle` | `hurdle_count_28` | 7 | 0.757 | 0.8644 | -0.1074 | [-0.2, -0.04803] | 0 | 112 / 145 / 43 | 8.94e-12 | 3.22e-11 |
| P09 | `timesfm3_raw` | `local_mean_28` | 7 | 0.7524 | 0.8331 | -0.0807 | [-0.1461, -0.03596] | -0.000948 | 155 / 15 / 130 | 8.45e-08 | 1.9e-07 |
| P10 | `timesfm3_hurdle` | `timesfm3_completed` | 30 | 0.7152 | 0.705 | 0.01025 | [0.00623, 0.01537] | 0.0002469 | 62 / 87 / 151 | 2.67e-11 | 8.01e-11 |
| P11 | `timesfm3_hurdle` | `hurdle_count_28` | 30 | 0.7152 | 0.8291 | -0.1138 | [-0.1966, -0.05842] | 0 | 123 / 145 / 32 | 2.99e-18 | 2.69e-17 |
| P12 | `timesfm3_raw` | `local_mean_28` | 30 | 0.7104 | 0.7906 | -0.08027 | [-0.1427, -0.03882] | -0.0005049 | 161 / 15 / 124 | 6.24e-11 | 1.6e-10 |
| P13 | `timesfm2p5_hurdle` | `timesfm2p5_completed` | 7 | 0.7559 | 0.7478 | 0.008042 | [0.002649, 0.01434] | 0 | 88 / 79 / 133 | 0.00358 | 0.00379 |
| P14 | `timesfm2p5_hurdle` | `hurdle_count_28` | 7 | 0.7559 | 0.8644 | -0.1085 | [-0.1989, -0.04924] | 0 | 118 / 143 / 39 | 1.37e-12 | 6.15e-12 |
| P15 | `timesfm2p5_raw` | `local_mean_28` | 7 | 0.7548 | 0.8331 | -0.07836 | [-0.1403, -0.03456] | 0 | 137 / 15 / 148 | 0.000846 | 0.00101 |
| P16 | `timesfm2p5_hurdle` | `timesfm2p5_completed` | 30 | 0.7173 | 0.7083 | 0.008983 | [0.005159, 0.01377] | 0 | 79 / 79 / 142 | 2.11e-06 | 3.79e-06 |
| P17 | `timesfm2p5_hurdle` | `hurdle_count_28` | 30 | 0.7173 | 0.8291 | -0.1118 | [-0.191, -0.05765] | 0 | 133 / 136 / 31 | 9.08e-20 | 1.64e-18 |
| P18 | `timesfm2p5_raw` | `local_mean_28` | 30 | 0.7163 | 0.7906 | -0.0743 | [-0.1328, -0.03515] | 7.001e-05 | 128 / 15 / 157 | 0.0046 | 0.0046 |

## Pooled over all 300 series, Study 3's pairs, QScore9 (secondary, unadjusted)

| Variant | Reference | h | Variant mean | Reference mean | Mean difference | 95% interval | Median difference | Lower / tied / higher | Raw p |
|---|---|---|---|---|---|---|---|---|---|
| `chronos2_hurdle` | `chronos2_completed` | 7 | 0.7589 | 0.7496 | 0.009347 | [0.003806, 0.01544] | 0 | 87 / 79 / 134 | 0.00158 |
| `chronos2_hurdle` | `hurdle_count_28` | 7 | 0.7589 | 0.8644 | -0.1055 | [-0.1957, -0.04628] | 0 | 109 / 128 / 63 | 1.06e-07 |
| `chronos2_hurdle` | `hurdle_empirical_28` | 7 | 0.7589 | 0.8272 | -0.0683 | [-0.1297, -0.02624] | 0 | 105 / 130 / 65 | 4.17e-07 |
| `chronos2_occurrence_model_size_count` | `chronos2_completed` | 7 | 0.8479 | 0.7496 | 0.09838 | [0.04023, 0.1885] | 0 | 69 / 136 / 95 | 1.52e-06 |
| `chronos2_occurrence_model_size_count` | `hurdle_count_28` | 7 | 0.8479 | 0.8644 | -0.01645 | [-0.02498, -0.008882] | 0 | 143 / 79 / 78 | 1.29e-05 |
| `chronos2_occurrence_model_size_count` | `hurdle_empirical_28` | 7 | 0.8479 | 0.8272 | 0.02073 | [-0.001055, 0.0532] | 0 | 130 / 78 / 92 | 0.196 |
| `chronos2_hurdle_dynamic` | `chronos2_completed` | 7 | 0.7556 | 0.7496 | 0.006049 | [0.001594, 0.01072] | 0 | 87 / 102 / 111 | 0.037 |
| `chronos2_hurdle_dynamic` | `hurdle_empirical_28` | 7 | 0.7556 | 0.8272 | -0.07159 | [-0.1314, -0.02965] | 0 | 138 / 91 / 71 | 1.6e-09 |
| `chronos2_hurdle` | `chronos2_completed` | 30 | 0.7183 | 0.7094 | 0.008984 | [0.004442, 0.01483] | 0.0001235 | 77 / 73 / 150 | 5.35e-06 |
| `chronos2_hurdle` | `hurdle_count_28` | 30 | 0.7183 | 0.8291 | -0.1107 | [-0.1925, -0.05611] | 0 | 115 / 124 / 61 | 7.04e-14 |
| `chronos2_hurdle` | `hurdle_empirical_28` | 30 | 0.7183 | 0.7872 | -0.06883 | [-0.1292, -0.02966] | 0 | 113 / 124 / 63 | 8.02e-11 |
| `chronos2_occurrence_model_size_count` | `chronos2_completed` | 30 | 0.8125 | 0.7094 | 0.1032 | [0.04841, 0.1875] | 0 | 55 / 123 / 122 | 4.58e-14 |
| `chronos2_occurrence_model_size_count` | `hurdle_count_28` | 30 | 0.8125 | 0.8291 | -0.01653 | [-0.02399, -0.009853] | 0 | 146 / 76 / 78 | 6.66e-07 |
| `chronos2_occurrence_model_size_count` | `hurdle_empirical_28` | 30 | 0.8125 | 0.7872 | 0.02536 | [0.007074, 0.04969] | 0 | 125 / 76 / 99 | 0.714 |
| `chronos2_hurdle_dynamic` | `chronos2_completed` | 30 | 0.714 | 0.7094 | 0.004655 | [0.001374, 0.008249] | 0 | 98 / 96 / 106 | 0.246 |
| `chronos2_hurdle_dynamic` | `hurdle_empirical_28` | 30 | 0.714 | 0.7872 | -0.07316 | [-0.1339, -0.03321] | -0.002469 | 162 / 92 / 46 | 4.44e-17 |
| `timesfm3_hurdle` | `timesfm3_completed` | 7 | 0.757 | 0.7467 | 0.01028 | [0.004995, 0.01638] | 0 | 83 / 89 / 128 | 4.74e-05 |
| `timesfm3_hurdle` | `hurdle_count_28` | 7 | 0.757 | 0.8644 | -0.1074 | [-0.1989, -0.0477] | 0 | 112 / 145 / 43 | 8.94e-12 |
| `timesfm3_hurdle` | `hurdle_empirical_28` | 7 | 0.757 | 0.8272 | -0.07025 | [-0.1311, -0.02789] | 0 | 102 / 149 / 49 | 3.95e-09 |
| `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | 7 | 0.8506 | 0.7467 | 0.104 | [0.04389, 0.1977] | 0 | 37 / 151 / 112 | 1.64e-11 |
| `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | 7 | 0.8506 | 0.8644 | -0.01376 | [-0.02056, -0.007577] | 0 | 128 / 91 / 81 | 0.000117 |
| `timesfm3_occurrence_model_size_count` | `hurdle_empirical_28` | 7 | 0.8506 | 0.8272 | 0.02343 | [0.001683, 0.05537] | 0 | 111 / 87 / 102 | 0.933 |
| `timesfm3_hurdle_dynamic` | `timesfm3_completed` | 7 | 0.7545 | 0.7467 | 0.007848 | [0.004254, 0.01178] | 0 | 82 / 109 / 109 | 0.00106 |
| `timesfm3_hurdle_dynamic` | `hurdle_empirical_28` | 7 | 0.7545 | 0.8272 | -0.07268 | [-0.1347, -0.02944] | 0 | 145 / 91 / 64 | 1.22e-09 |
| `timesfm3_hurdle` | `timesfm3_completed` | 30 | 0.7152 | 0.705 | 0.01025 | [0.006313, 0.01545] | 0.0002469 | 62 / 87 / 151 | 2.67e-11 |
| `timesfm3_hurdle` | `hurdle_count_28` | 30 | 0.7152 | 0.8291 | -0.1138 | [-0.1972, -0.05824] | 0 | 123 / 145 / 32 | 2.99e-18 |
| `timesfm3_hurdle` | `hurdle_empirical_28` | 30 | 0.7152 | 0.7872 | -0.07193 | [-0.1328, -0.03179] | 0 | 120 / 142 / 38 | 6.24e-16 |
| `timesfm3_occurrence_model_size_count` | `timesfm3_completed` | 30 | 0.815 | 0.705 | 0.11 | [0.05406, 0.1936] | 0 | 24 / 147 / 129 | 2.02e-20 |
| `timesfm3_occurrence_model_size_count` | `hurdle_count_28` | 30 | 0.815 | 0.8291 | -0.01411 | [-0.0202, -0.008773] | 0 | 141 / 87 / 72 | 1.76e-07 |
| `timesfm3_occurrence_model_size_count` | `hurdle_empirical_28` | 30 | 0.815 | 0.7872 | 0.02779 | [0.009334, 0.05215] | 0 | 119 / 85 / 96 | 0.868 |
| `timesfm3_hurdle_dynamic` | `timesfm3_completed` | 30 | 0.7122 | 0.705 | 0.007174 | [0.004113, 0.01074] | 0 | 81 / 92 / 127 | 2.09e-05 |
| `timesfm3_hurdle_dynamic` | `hurdle_empirical_28` | 30 | 0.7122 | 0.7872 | -0.075 | [-0.1377, -0.03415] | -0.002469 | 165 / 95 / 40 | 9.62e-18 |
| `timesfm2p5_hurdle` | `timesfm2p5_completed` | 7 | 0.7559 | 0.7478 | 0.008042 | [0.002684, 0.01421] | 0 | 88 / 79 / 133 | 0.00358 |
| `timesfm2p5_hurdle` | `hurdle_count_28` | 7 | 0.7559 | 0.8644 | -0.1085 | [-0.2007, -0.0493] | 0 | 118 / 143 / 39 | 1.37e-12 |
| `timesfm2p5_hurdle` | `hurdle_empirical_28` | 7 | 0.7559 | 0.8272 | -0.07132 | [-0.1333, -0.02939] | 0 | 104 / 147 / 49 | 1.35e-10 |
| `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | 7 | 0.8506 | 0.7478 | 0.1027 | [0.044, 0.1935] | 0 | 36 / 153 / 111 | 8.77e-12 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | 7 | 0.8506 | 0.8644 | -0.0138 | [-0.02113, -0.006984] | 0 | 144 / 80 / 76 | 0.000119 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_empirical_28` | 7 | 0.8506 | 0.8272 | 0.02338 | [0.001686, 0.05618] | 0 | 118 / 77 / 105 | 0.799 |
| `timesfm2p5_hurdle_dynamic` | `timesfm2p5_completed` | 7 | 0.7543 | 0.7478 | 0.006409 | [0.0026, 0.01066] | 0 | 92 / 97 / 111 | 0.0629 |
| `timesfm2p5_hurdle_dynamic` | `hurdle_empirical_28` | 7 | 0.7543 | 0.8272 | -0.07295 | [-0.1341, -0.03002] | 0 | 144 / 92 / 64 | 1.69e-10 |
| `timesfm2p5_hurdle` | `timesfm2p5_completed` | 30 | 0.7173 | 0.7083 | 0.008983 | [0.005091, 0.01384] | 0 | 79 / 79 / 142 | 2.11e-06 |
| `timesfm2p5_hurdle` | `hurdle_count_28` | 30 | 0.7173 | 0.8291 | -0.1118 | [-0.1908, -0.05826] | 0 | 133 / 136 / 31 | 9.08e-20 |
| `timesfm2p5_hurdle` | `hurdle_empirical_28` | 30 | 0.7173 | 0.7872 | -0.0699 | [-0.128, -0.03171] | 0 | 126 / 140 / 34 | 4.34e-17 |
| `timesfm2p5_occurrence_model_size_count` | `timesfm2p5_completed` | 30 | 0.814 | 0.7083 | 0.1057 | [0.05269, 0.1873] | 0 | 28 / 147 / 125 | 3.06e-19 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_count_28` | 30 | 0.814 | 0.8291 | -0.01504 | [-0.02163, -0.009183] | 0 | 141 / 81 / 78 | 1.1e-06 |
| `timesfm2p5_occurrence_model_size_count` | `hurdle_empirical_28` | 30 | 0.814 | 0.7872 | 0.02685 | [0.008374, 0.05044] | 0 | 119 / 79 / 102 | 0.838 |
| `timesfm2p5_hurdle_dynamic` | `timesfm2p5_completed` | 30 | 0.7147 | 0.7083 | 0.006421 | [0.003561, 0.009615] | 0 | 90 / 97 / 113 | 0.00174 |
| `timesfm2p5_hurdle_dynamic` | `hurdle_empirical_28` | 30 | 0.7147 | 0.7872 | -0.07246 | [-0.1322, -0.03391] | -0.002469 | 166 / 94 / 40 | 1.13e-17 |

## Mean QScore9 per model and stratum, horizon 7 (equal series)

| Model | dense (n = 100) | sparse (n = 100) | very sparse (n = 100) | all (n = 300) |
|---|---|---|---|---|
| `chronos2_raw` | 1.847 | 0.3687 | 0.05523 | 0.7568 |
| `chronos2_completed` | 1.833 | 0.3631 | 0.05273 | 0.7496 |
| `chronos2_hurdle` | 1.854 | 0.3671 | 0.05538 | 0.7589 |
| `chronos2_hurdle_dynamic` | 1.851 | 0.361 | 0.05527 | 0.7556 |
| `chronos2_occurrence_model_size_count` | 2.127 | 0.3634 | 0.05321 | 0.8479 |
| `timesfm3_raw` | 1.838 | 0.3654 | 0.05381 | 0.7524 |
| `timesfm3_completed` | 1.827 | 0.3603 | 0.05298 | 0.7467 |
| `timesfm3_hurdle` | 1.851 | 0.3645 | 0.05504 | 0.757 |
| `timesfm3_hurdle_dynamic` | 1.848 | 0.3606 | 0.05524 | 0.7545 |
| `timesfm3_occurrence_model_size_count` | 2.136 | 0.3621 | 0.05372 | 0.8506 |
| `timesfm2p5_raw` | 1.835 | 0.3738 | 0.05555 | 0.7548 |
| `timesfm2p5_completed` | 1.824 | 0.3668 | 0.05327 | 0.7478 |
| `timesfm2p5_hurdle` | 1.848 | 0.3641 | 0.05515 | 0.7559 |
| `timesfm2p5_hurdle_dynamic` | 1.846 | 0.3618 | 0.05523 | 0.7543 |
| `timesfm2p5_occurrence_model_size_count` | 2.129 | 0.3692 | 0.05319 | 0.8506 |
| `local_mean_28` | 2.077 | 0.3672 | 0.05534 | 0.8331 |
| `autoets_weekly` | 1.956 | 0.4234 | 0.3414 | 0.907 |
| `nb_local_level_28` | 2.073 | 0.3666 | 0.0563 | 0.832 |
| `poisson_28` | 2.19 | 0.3765 | 0.05599 | 0.8741 |
| `hurdle_count_28` | 2.172 | 0.3656 | 0.0553 | 0.8644 |
| `hurdle_empirical_28` | 2.06 | 0.3664 | 0.0557 | 0.8272 |
| `dynamic_count` | 2.159 | 0.3618 | 0.05576 | 0.8588 |

## Mean QScore9 per model and stratum, horizon 30 (equal series)

| Model | dense (n = 100) | sparse (n = 100) | very sparse (n = 100) | all (n = 300) |
|---|---|---|---|---|
| `chronos2_raw` | 1.722 | 0.3643 | 0.06218 | 0.7162 |
| `chronos2_completed` | 1.709 | 0.3591 | 0.06013 | 0.7094 |
| `chronos2_hurdle` | 1.733 | 0.3617 | 0.06041 | 0.7183 |
| `chronos2_hurdle_dynamic` | 1.724 | 0.3574 | 0.06064 | 0.714 |
| `chronos2_occurrence_model_size_count` | 2.017 | 0.3593 | 0.06109 | 0.8125 |
| `timesfm3_raw` | 1.713 | 0.3591 | 0.05904 | 0.7104 |
| `timesfm3_completed` | 1.703 | 0.3541 | 0.05797 | 0.705 |
| `timesfm3_hurdle` | 1.726 | 0.3595 | 0.06043 | 0.7152 |
| `timesfm3_hurdle_dynamic` | 1.719 | 0.3563 | 0.06088 | 0.7122 |
| `timesfm3_occurrence_model_size_count` | 2.028 | 0.3573 | 0.05963 | 0.815 |
| `timesfm2p5_raw` | 1.721 | 0.367 | 0.06135 | 0.7163 |
| `timesfm2p5_completed` | 1.707 | 0.3581 | 0.05939 | 0.7083 |
| `timesfm2p5_hurdle` | 1.732 | 0.3593 | 0.06085 | 0.7173 |
| `timesfm2p5_hurdle_dynamic` | 1.726 | 0.3571 | 0.06102 | 0.7147 |
| `timesfm2p5_occurrence_model_size_count` | 2.021 | 0.3612 | 0.05988 | 0.814 |
| `local_mean_28` | 1.947 | 0.3634 | 0.06123 | 0.7906 |
| `autoets_weekly` | 1.905 | 0.4161 | 0.5909 | 0.9707 |
| `nb_local_level_28` | 1.949 | 0.3628 | 0.06216 | 0.7914 |
| `poisson_28` | 2.082 | 0.3663 | 0.06191 | 0.8368 |
| `hurdle_count_28` | 2.064 | 0.3623 | 0.06107 | 0.8291 |
| `hurdle_empirical_28` | 1.939 | 0.3615 | 0.06132 | 0.7872 |
| `dynamic_count` | 2.033 | 0.358 | 0.06157 | 0.8175 |

## Other scores per model, dense (n = 100) (equal series)

| Model | Scaled QScore9 h7 | Scaled QScore9 h30 | Brier h7 | Brier h30 | CRPS h30 | CRPS series defined, h30 | CRPS certified / with law / all, h30 |
|---|---|---|---|---|---|---|---|
| `chronos2_raw` | 0.6209 | 0.575 |  |  |  | 0 | 0 / 0 / 300 |
| `chronos2_completed` | 0.6142 | 0.568 | 0.1379 | 0.1421 | 1.571 | 100 | 300 / 300 / 300 |
| `chronos2_hurdle` | 0.6245 | 0.5766 | 0.1482 | 0.1497 | 1.594 | 100 | 300 / 300 / 300 |
| `chronos2_hurdle_dynamic` | 0.6211 | 0.5727 | 0.1473 | 0.1495 | 1.586 | 100 | 300 / 300 / 300 |
| `chronos2_occurrence_model_size_count` | 0.664 | 0.6217 | 0.1379 | 0.1421 | 1.868 | 100 | 300 / 300 / 300 |
| `timesfm3_raw` | 0.6199 | 0.5722 |  |  |  | 0 | 0 / 0 / 300 |
| `timesfm3_completed` | 0.6133 | 0.5664 | 0.1391 | 0.1428 | 1.565 | 100 | 300 / 300 / 300 |
| `timesfm3_hurdle` | 0.6241 | 0.5749 | 0.1482 | 0.1497 | 1.585 | 100 | 300 / 300 / 300 |
| `timesfm3_hurdle_dynamic` | 0.6216 | 0.5727 | 0.1473 | 0.1495 | 1.579 | 100 | 300 / 300 / 300 |
| `timesfm3_occurrence_model_size_count` | 0.6713 | 0.6285 | 0.1391 | 0.1428 | 1.878 | 100 | 300 / 300 / 300 |
| `timesfm2p5_raw` | 0.6193 | 0.5725 |  |  |  | 0 | 0 / 0 / 300 |
| `timesfm2p5_completed` | 0.6133 | 0.5652 | 0.1384 | 0.1423 | 1.572 | 100 | 300 / 300 / 300 |
| `timesfm2p5_hurdle` | 0.6248 | 0.5749 | 0.1482 | 0.1497 | 1.594 | 100 | 300 / 300 / 300 |
| `timesfm2p5_hurdle_dynamic` | 0.6224 | 0.5729 | 0.1473 | 0.1495 | 1.588 | 100 | 300 / 300 / 300 |
| `timesfm2p5_occurrence_model_size_count` | 0.6677 | 0.6251 | 0.1384 | 0.1423 | 1.87 | 100 | 300 / 300 / 300 |
| `local_mean_28` | 0.6692 | 0.6155 |  |  |  | 0 | 0 / 0 / 300 |
| `autoets_weekly` | 0.6584 | 0.6354 |  |  |  | 0 | 0 / 0 / 300 |
| `nb_local_level_28` | 0.6685 | 0.6156 | 0.1562 | 0.1543 | 1.788 | 100 | 300 / 300 / 300 |
| `poisson_28` | 0.6934 | 0.6509 | 0.1587 | 0.1637 | 1.932 | 100 | 300 / 300 / 300 |
| `hurdle_count_28` | 0.6879 | 0.6443 | 0.1482 | 0.1497 | 1.908 | 100 | 300 / 300 / 300 |
| `hurdle_empirical_28` | 0.663 | 0.612 | 0.1482 | 0.1497 | 1.783 | 100 | 300 / 300 / 300 |
| `dynamic_count` | 0.6735 | 0.6237 | 0.1473 | 0.1495 | 1.885 | 100 | 300 / 300 / 300 |

## Other scores per model, sparse (n = 100) (equal series)

| Model | Scaled QScore9 h7 | Scaled QScore9 h30 | Brier h7 | Brier h30 | CRPS h30 | CRPS series defined, h30 | CRPS certified / with law / all, h30 |
|---|---|---|---|---|---|---|---|
| `chronos2_raw` | 0.3649 | 0.3608 |  |  |  | 0 | 0 / 0 / 300 |
| `chronos2_completed` | 0.3594 | 0.3557 | 0.1818 | 0.1826 | 0.3299 | 100 | 300 / 300 / 300 |
| `chronos2_hurdle` | 0.3633 | 0.3583 | 0.1837 | 0.1841 | 0.3334 | 100 | 300 / 300 / 300 |
| `chronos2_hurdle_dynamic` | 0.3573 | 0.354 | 0.1814 | 0.1828 | 0.3298 | 100 | 300 / 300 / 300 |
| `chronos2_occurrence_model_size_count` | 0.3597 | 0.3559 | 0.1818 | 0.1826 | 0.3308 | 100 | 300 / 300 / 300 |
| `timesfm3_raw` | 0.3615 | 0.3556 |  |  |  | 0 | 0 / 0 / 300 |
| `timesfm3_completed` | 0.3565 | 0.3506 | 0.1802 | 0.1804 | 0.3267 | 100 | 300 / 300 / 300 |
| `timesfm3_hurdle` | 0.3607 | 0.356 | 0.1837 | 0.1841 | 0.331 | 100 | 300 / 300 / 300 |
| `timesfm3_hurdle_dynamic` | 0.3569 | 0.3529 | 0.1814 | 0.1828 | 0.3291 | 100 | 300 / 300 / 300 |
| `timesfm3_occurrence_model_size_count` | 0.3582 | 0.3538 | 0.1802 | 0.1804 | 0.3298 | 100 | 300 / 300 / 300 |
| `timesfm2p5_raw` | 0.37 | 0.3635 |  |  |  | 0 | 0 / 0 / 300 |
| `timesfm2p5_completed` | 0.363 | 0.3547 | 0.1835 | 0.1824 | 0.3286 | 100 | 300 / 300 / 300 |
| `timesfm2p5_hurdle` | 0.3604 | 0.3559 | 0.1837 | 0.1841 | 0.331 | 100 | 300 / 300 / 300 |
| `timesfm2p5_hurdle_dynamic` | 0.3582 | 0.3536 | 0.1814 | 0.1828 | 0.3297 | 100 | 300 / 300 / 300 |
| `timesfm2p5_occurrence_model_size_count` | 0.3653 | 0.3576 | 0.1835 | 0.1824 | 0.3322 | 100 | 300 / 300 / 300 |
| `local_mean_28` | 0.3635 | 0.3599 |  |  |  | 0 | 0 / 0 / 300 |
| `autoets_weekly` | 0.419 | 0.4122 |  |  |  | 0 | 0 / 0 / 300 |
| `nb_local_level_28` | 0.3628 | 0.3594 | 0.184 | 0.1858 | 0.334 | 100 | 300 / 300 / 300 |
| `poisson_28` | 0.3719 | 0.3623 | 0.1908 | 0.1887 | 0.3374 | 100 | 300 / 300 / 300 |
| `hurdle_count_28` | 0.3618 | 0.3588 | 0.1837 | 0.1841 | 0.3342 | 100 | 300 / 300 / 300 |
| `hurdle_empirical_28` | 0.3626 | 0.358 | 0.1837 | 0.1841 | 0.3337 | 100 | 300 / 300 / 300 |
| `dynamic_count` | 0.358 | 0.3545 | 0.1814 | 0.1828 | 0.3308 | 100 | 300 / 300 / 300 |

## Other scores per model, very sparse (n = 100) (equal series)

| Model | Scaled QScore9 h7 | Scaled QScore9 h30 | Brier h7 | Brier h30 | CRPS h30 | CRPS series defined, h30 | CRPS certified / with law / all, h30 |
|---|---|---|---|---|---|---|---|
| `chronos2_raw` | 0.05347 | 0.06037 |  |  |  | 0 | 0 / 0 / 300 |
| `chronos2_completed` | 0.05236 | 0.05972 | 0.03664 | 0.03668 | 0.05901 | 100 | 300 / 300 / 300 |
| `chronos2_hurdle` | 0.05538 | 0.06041 | 0.03662 | 0.0355 | 0.05782 | 100 | 300 / 300 / 300 |
| `chronos2_hurdle_dynamic` | 0.05527 | 0.06064 | 0.03659 | 0.0354 | 0.05822 | 100 | 300 / 300 / 300 |
| `chronos2_occurrence_model_size_count` | 0.05284 | 0.06068 | 0.03664 | 0.03668 | 0.05994 | 100 | 300 / 300 / 300 |
| `timesfm3_raw` | 0.0534 | 0.05867 |  |  |  | 0 | 0 / 0 / 300 |
| `timesfm3_completed` | 0.05298 | 0.05796 | 0.03639 | 0.03562 | 0.05727 | 100 | 300 / 300 / 300 |
| `timesfm3_hurdle` | 0.05504 | 0.06043 | 0.03662 | 0.0355 | 0.05786 | 100 | 300 / 300 / 300 |
| `timesfm3_hurdle_dynamic` | 0.05524 | 0.06088 | 0.03659 | 0.0354 | 0.05828 | 100 | 300 / 300 / 300 |
| `timesfm3_occurrence_model_size_count` | 0.05372 | 0.05963 | 0.03639 | 0.03562 | 0.05839 | 100 | 300 / 300 / 300 |
| `timesfm2p5_raw` | 0.05464 | 0.06028 |  |  |  | 0 | 0 / 0 / 300 |
| `timesfm2p5_completed` | 0.05287 | 0.05883 | 0.03677 | 0.03599 | 0.05826 | 100 | 300 / 300 / 300 |
| `timesfm2p5_hurdle` | 0.05515 | 0.06085 | 0.03662 | 0.0355 | 0.0584 | 100 | 300 / 300 / 300 |
| `timesfm2p5_hurdle_dynamic` | 0.05523 | 0.06102 | 0.03659 | 0.0354 | 0.05869 | 100 | 300 / 300 / 300 |
| `timesfm2p5_occurrence_model_size_count` | 0.05279 | 0.05935 | 0.03677 | 0.03599 | 0.05859 | 100 | 300 / 300 / 300 |
| `local_mean_28` | 0.05534 | 0.06123 |  |  |  | 0 | 0 / 0 / 300 |
| `autoets_weekly` | 0.1136 | 0.1518 |  |  |  | 0 | 0 / 0 / 300 |
| `nb_local_level_28` | 0.0563 | 0.06216 | 0.03731 | 0.03635 | 0.0593 | 100 | 300 / 300 / 300 |
| `poisson_28` | 0.05599 | 0.06191 | 0.03687 | 0.03569 | 0.05908 | 100 | 300 / 300 / 300 |
| `hurdle_count_28` | 0.0553 | 0.06107 | 0.03662 | 0.0355 | 0.05878 | 100 | 300 / 300 / 300 |
| `hurdle_empirical_28` | 0.0557 | 0.06132 | 0.03662 | 0.0355 | 0.05879 | 100 | 300 / 300 / 300 |
| `dynamic_count` | 0.05576 | 0.06157 | 0.03659 | 0.0354 | 0.05912 | 100 | 300 / 300 / 300 |

## Other scores per model, all (n = 300) (equal series)

| Model | Scaled QScore9 h7 | Scaled QScore9 h30 | Brier h7 | Brier h30 | CRPS h30 | CRPS series defined, h30 | CRPS certified / with law / all, h30 |
|---|---|---|---|---|---|---|---|
| `chronos2_raw` | 0.3465 | 0.3321 |  |  |  | 0 | 0 / 0 / 900 |
| `chronos2_completed` | 0.342 | 0.3278 | 0.1188 | 0.1205 | 0.6535 | 300 | 900 / 900 / 900 |
| `chronos2_hurdle` | 0.3477 | 0.3318 | 0.1228 | 0.1231 | 0.6616 | 300 | 900 / 900 / 900 |
| `chronos2_hurdle_dynamic` | 0.3446 | 0.3291 | 0.1217 | 0.1226 | 0.658 | 300 | 900 / 900 / 900 |
| `chronos2_occurrence_model_size_count` | 0.3588 | 0.3461 | 0.1188 | 0.1205 | 0.753 | 300 | 900 / 900 / 900 |
| `timesfm3_raw` | 0.345 | 0.3288 |  |  |  | 0 | 0 / 0 / 900 |
| `timesfm3_completed` | 0.3409 | 0.325 | 0.1186 | 0.1196 | 0.6495 | 300 | 900 / 900 / 900 |
| `timesfm3_hurdle` | 0.3466 | 0.3304 | 0.1228 | 0.1231 | 0.6581 | 300 | 900 / 900 / 900 |
| `timesfm3_hurdle_dynamic` | 0.3446 | 0.3288 | 0.1217 | 0.1226 | 0.6555 | 300 | 900 / 900 / 900 |
| `timesfm3_occurrence_model_size_count` | 0.3611 | 0.3473 | 0.1186 | 0.1196 | 0.7553 | 300 | 900 / 900 / 900 |
| `timesfm2p5_raw` | 0.348 | 0.3321 |  |  |  | 0 | 0 / 0 / 900 |
| `timesfm2p5_completed` | 0.343 | 0.3262 | 0.1195 | 0.1202 | 0.6528 | 300 | 900 / 900 / 900 |
| `timesfm2p5_hurdle` | 0.3468 | 0.3306 | 0.1228 | 0.1231 | 0.6611 | 300 | 900 / 900 / 900 |
| `timesfm2p5_hurdle_dynamic` | 0.3453 | 0.3292 | 0.1217 | 0.1226 | 0.6589 | 300 | 900 / 900 / 900 |
| `timesfm2p5_occurrence_model_size_count` | 0.3619 | 0.3474 | 0.1195 | 0.1202 | 0.7538 | 300 | 900 / 900 / 900 |
| `local_mean_28` | 0.3627 | 0.3455 |  |  |  | 0 | 0 / 0 / 900 |
| `autoets_weekly` | 0.397 | 0.3998 |  |  |  | 0 | 0 / 0 / 900 |
| `nb_local_level_28` | 0.3625 | 0.3457 | 0.1258 | 0.1255 | 0.7272 | 300 | 900 / 900 / 900 |
| `poisson_28` | 0.3738 | 0.3584 | 0.1288 | 0.1294 | 0.776 | 300 | 900 / 900 / 900 |
| `hurdle_count_28` | 0.3683 | 0.3547 | 0.1228 | 0.1231 | 0.7671 | 300 | 900 / 900 / 900 |
| `hurdle_empirical_28` | 0.3604 | 0.3438 | 0.1228 | 0.1231 | 0.7251 | 300 | 900 / 900 / 900 |
| `dynamic_count` | 0.3624 | 0.3466 | 0.1217 | 0.1226 | 0.7581 | 300 | 900 / 900 / 900 |

## QScore9 accounting, dense (n = 100), horizon 30 (equal series; the parts sum to the score)

| Model | QScore9 | Zero days | Positive, over | Positive, under | Largest residual |
|---|---|---|---|---|---|
| `chronos2_completed` | 1.709 | 0.168 | 0.5406 | 1 | 1.8e-15 |
| `chronos2_hurdle` | 1.733 | 0.202 | 0.5285 | 1.002 | 1.8e-15 |
| `chronos2_hurdle_dynamic` | 1.724 | 0.2002 | 0.5361 | 0.9877 | 3.6e-15 |
| `chronos2_occurrence_model_size_count` | 2.017 | 0.2177 | 0.6997 | 1.1 | 1.8e-15 |
| `timesfm3_completed` | 1.703 | 0.1874 | 0.5017 | 1.014 | 1.8e-15 |
| `timesfm3_hurdle` | 1.726 | 0.1998 | 0.4903 | 1.036 | 8.9e-16 |
| `timesfm3_hurdle_dynamic` | 1.719 | 0.1973 | 0.4988 | 1.023 | 1.8e-15 |
| `timesfm3_occurrence_model_size_count` | 2.028 | 0.2479 | 0.7041 | 1.076 | 1.8e-15 |
| `timesfm2p5_completed` | 1.707 | 0.1815 | 0.4783 | 1.048 | 1.8e-15 |
| `timesfm2p5_hurdle` | 1.732 | 0.194 | 0.4702 | 1.067 | 1.8e-15 |
| `timesfm2p5_hurdle_dynamic` | 1.726 | 0.1927 | 0.4802 | 1.053 | 1.8e-15 |
| `timesfm2p5_occurrence_model_size_count` | 2.021 | 0.2456 | 0.6984 | 1.077 | 1.8e-15 |
| `hurdle_count_28` | 2.064 | 0.2687 | 0.7033 | 1.092 | 1.8e-15 |
| `hurdle_empirical_28` | 1.939 | 0.222 | 0.5507 | 1.166 | 1.8e-15 |
| `dynamic_count` | 2.033 | 0.2652 | 0.639 | 1.129 | 1.8e-15 |

## QScore9 accounting, dense (n = 100), horizon 7 (equal series; the parts sum to the score)

| Model | QScore9 | Zero days | Positive, over | Positive, under | Largest residual |
|---|---|---|---|---|---|
| `chronos2_completed` | 1.833 | 0.1692 | 0.5846 | 1.079 | 3.6e-15 |
| `chronos2_hurdle` | 1.854 | 0.2019 | 0.5653 | 1.087 | 3.6e-15 |
| `chronos2_hurdle_dynamic` | 1.851 | 0.1977 | 0.5768 | 1.076 | 3.6e-15 |
| `chronos2_occurrence_model_size_count` | 2.127 | 0.2243 | 0.7373 | 1.166 | 7.1e-15 |
| `timesfm3_completed` | 1.827 | 0.1849 | 0.5703 | 1.072 | 7.1e-15 |
| `timesfm3_hurdle` | 1.851 | 0.1983 | 0.5516 | 1.101 | 3.6e-15 |
| `timesfm3_hurdle_dynamic` | 1.848 | 0.1946 | 0.5629 | 1.09 | 3.6e-15 |
| `timesfm3_occurrence_model_size_count` | 2.136 | 0.2503 | 0.7413 | 1.145 | 7.1e-15 |
| `timesfm2p5_completed` | 1.824 | 0.1796 | 0.5433 | 1.101 | 3.6e-15 |
| `timesfm2p5_hurdle` | 1.848 | 0.1932 | 0.5268 | 1.128 | 2.7e-15 |
| `timesfm2p5_hurdle_dynamic` | 1.846 | 0.1899 | 0.5411 | 1.115 | 1.8e-15 |
| `timesfm2p5_occurrence_model_size_count` | 2.129 | 0.2492 | 0.7363 | 1.144 | 5.3e-15 |
| `hurdle_count_28` | 2.172 | 0.2736 | 0.7333 | 1.165 | 3.6e-15 |
| `hurdle_empirical_28` | 2.06 | 0.2291 | 0.5801 | 1.25 | 3.6e-15 |
| `dynamic_count` | 2.159 | 0.2629 | 0.6835 | 1.213 | 3.6e-15 |

## QScore9 accounting, sparse (n = 100), horizon 30 (equal series; the parts sum to the score)

| Model | QScore9 | Zero days | Positive, over | Positive, under | Largest residual |
|---|---|---|---|---|---|
| `chronos2_completed` | 0.3591 | 0.05536 | 0.008405 | 0.2953 | 2.2e-16 |
| `chronos2_hurdle` | 0.3617 | 0.08446 | 0.01111 | 0.2662 | 2.2e-16 |
| `chronos2_hurdle_dynamic` | 0.3574 | 0.0661 | 0.007516 | 0.2838 | 2.2e-16 |
| `chronos2_occurrence_model_size_count` | 0.3593 | 0.05433 | 0.006304 | 0.2987 | 4.4e-16 |
| `timesfm3_completed` | 0.3541 | 0.081 | 0.007726 | 0.2654 | 2.2e-16 |
| `timesfm3_hurdle` | 0.3595 | 0.07952 | 0.008237 | 0.2717 | 2.2e-16 |
| `timesfm3_hurdle_dynamic` | 0.3563 | 0.06198 | 0.005701 | 0.2886 | 2.2e-16 |
| `timesfm3_occurrence_model_size_count` | 0.3573 | 0.08492 | 0.008333 | 0.264 | 2.2e-16 |
| `timesfm2p5_completed` | 0.3581 | 0.06883 | 0.006215 | 0.283 | 2.2e-16 |
| `timesfm2p5_hurdle` | 0.3593 | 0.0772 | 0.006879 | 0.2753 | 2.2e-16 |
| `timesfm2p5_hurdle_dynamic` | 0.3571 | 0.06027 | 0.004627 | 0.2922 | 4.4e-16 |
| `timesfm2p5_occurrence_model_size_count` | 0.3612 | 0.07504 | 0.00824 | 0.2779 | 2.2e-16 |
| `hurdle_count_28` | 0.3623 | 0.0823 | 0.008489 | 0.2715 | 2.2e-16 |
| `hurdle_empirical_28` | 0.3615 | 0.07942 | 0.007094 | 0.275 | 2.2e-16 |
| `dynamic_count` | 0.358 | 0.06281 | 0.005119 | 0.29 | 2.2e-16 |

## QScore9 accounting, sparse (n = 100), horizon 7 (equal series; the parts sum to the score)

| Model | QScore9 | Zero days | Positive, over | Positive, under | Largest residual |
|---|---|---|---|---|---|
| `chronos2_completed` | 0.3631 | 0.05911 | 0.007429 | 0.2966 | 4.4e-16 |
| `chronos2_hurdle` | 0.3671 | 0.08705 | 0.009661 | 0.2704 | 3.3e-16 |
| `chronos2_hurdle_dynamic` | 0.361 | 0.0684 | 0.006444 | 0.2861 | 8.9e-16 |
| `chronos2_occurrence_model_size_count` | 0.3634 | 0.05885 | 0.005048 | 0.2995 | 8.9e-16 |
| `timesfm3_completed` | 0.3603 | 0.08258 | 0.006571 | 0.2712 | 4.4e-16 |
| `timesfm3_hurdle` | 0.3645 | 0.08183 | 0.007058 | 0.2756 | 4.4e-16 |
| `timesfm3_hurdle_dynamic` | 0.3606 | 0.06413 | 0.004942 | 0.2915 | 4.4e-16 |
| `timesfm3_occurrence_model_size_count` | 0.3621 | 0.08728 | 0.006762 | 0.268 | 6.7e-16 |
| `timesfm2p5_completed` | 0.3668 | 0.06697 | 0.004667 | 0.2951 | 4.4e-16 |
| `timesfm2p5_hurdle` | 0.3641 | 0.07775 | 0.005291 | 0.2811 | 4.4e-16 |
| `timesfm2p5_hurdle_dynamic` | 0.3618 | 0.06096 | 0.003386 | 0.2975 | 4.4e-16 |
| `timesfm2p5_occurrence_model_size_count` | 0.3692 | 0.07562 | 0.006667 | 0.2869 | 4.4e-16 |
| `hurdle_count_28` | 0.3656 | 0.08571 | 0.007228 | 0.2726 | 4.4e-16 |
| `hurdle_empirical_28` | 0.3664 | 0.08272 | 0.006222 | 0.2775 | 8.9e-16 |
| `dynamic_count` | 0.3618 | 0.06547 | 0.004476 | 0.2918 | 4.4e-16 |

## QScore9 accounting, very sparse (n = 100), horizon 30 (equal series; the parts sum to the score)

| Model | QScore9 | Zero days | Positive, over | Positive, under | Largest residual |
|---|---|---|---|---|---|
| `chronos2_completed` | 0.06013 | 0.001612 | 0.0002642 | 0.05826 | 8.9e-16 |
| `chronos2_hurdle` | 0.06041 | 0.004052 | 0.000242 | 0.05611 | 1.1e-16 |
| `chronos2_hurdle_dynamic` | 0.06064 | 0.001341 | 9.383e-05 | 0.05921 | 1.1e-16 |
| `chronos2_occurrence_model_size_count` | 0.06109 | 0.001763 | 0.0001481 | 0.05918 | 1.1e-16 |
| `timesfm3_completed` | 0.05797 | 0.003257 | 0.0005136 | 0.0542 | 1.1e-16 |
| `timesfm3_hurdle` | 0.06043 | 0.004057 | 0.0002346 | 0.05614 | 1.1e-16 |
| `timesfm3_hurdle_dynamic` | 0.06088 | 0.001321 | 8.148e-05 | 0.05947 | 8.9e-16 |
| `timesfm3_occurrence_model_size_count` | 0.05963 | 0.003531 | 0.0002395 | 0.05586 | 8.9e-16 |
| `timesfm2p5_completed` | 0.05939 | 0.001452 | 0.000321 | 0.05761 | 8.9e-16 |
| `timesfm2p5_hurdle` | 0.06085 | 0.003941 | 0.0001383 | 0.05677 | 8.9e-16 |
| `timesfm2p5_hurdle_dynamic` | 0.06102 | 0.001316 | 6.914e-05 | 0.05963 | 1.1e-16 |
| `timesfm2p5_occurrence_model_size_count` | 0.05988 | 0.001477 | 0.0002222 | 0.05818 | 1.8e-15 |
| `hurdle_count_28` | 0.06107 | 0.004074 | 0.0001432 | 0.05686 | 8.9e-16 |
| `hurdle_empirical_28` | 0.06132 | 0.003916 | 8.148e-05 | 0.05732 | 8.9e-16 |
| `dynamic_count` | 0.06157 | 0.001306 | 1.728e-05 | 0.06024 | 1.1e-16 |

## QScore9 accounting, very sparse (n = 100), horizon 7 (equal series; the parts sum to the score)

| Model | QScore9 | Zero days | Positive, over | Positive, under | Largest residual |
|---|---|---|---|---|---|
| `chronos2_completed` | 0.05273 | 0.001397 | 0.0003492 | 0.05098 | 2.2e-16 |
| `chronos2_hurdle` | 0.05538 | 0.004021 | 0.0002646 | 0.05109 | 2.2e-16 |
| `chronos2_hurdle_dynamic` | 0.05527 | 0.001365 | 9.524e-05 | 0.05381 | 5.6e-17 |
| `chronos2_occurrence_model_size_count` | 0.05321 | 0.001513 | 0.0001481 | 0.05154 | 2.2e-16 |
| `timesfm3_completed` | 0.05298 | 0.002952 | 0.0004339 | 0.0496 | 4.4e-16 |
| `timesfm3_hurdle` | 0.05504 | 0.004021 | 0.0002011 | 0.05081 | 2.2e-16 |
| `timesfm3_hurdle_dynamic` | 0.05524 | 0.001354 | 7.407e-05 | 0.05381 | 4.4e-16 |
| `timesfm3_occurrence_model_size_count` | 0.05372 | 0.003122 | 0.0002328 | 0.05037 | 2.2e-16 |
| `timesfm2p5_completed` | 0.05327 | 0.001101 | 0.000381 | 0.05179 | 2.2e-16 |
| `timesfm2p5_hurdle` | 0.05515 | 0.003958 | 0.0001058 | 0.05109 | 2.2e-16 |
| `timesfm2p5_hurdle_dynamic` | 0.05523 | 0.001354 | 6.349e-05 | 0.05381 | 5.6e-17 |
| `timesfm2p5_occurrence_model_size_count` | 0.05319 | 0.001069 | 0.0002222 | 0.05189 | 1.4e-17 |
| `hurdle_count_28` | 0.0553 | 0.004106 | 0.0001058 | 0.05109 | 2.2e-16 |
| `hurdle_empirical_28` | 0.0557 | 0.003915 | 9.524e-05 | 0.05169 | 2.2e-16 |
| `dynamic_count` | 0.05576 | 0.001323 | 1.058e-05 | 0.05442 | 5.6e-17 |

## QScore9 accounting, all (n = 300), horizon 30 (equal series; the parts sum to the score)

| Model | QScore9 | Zero days | Positive, over | Positive, under | Largest residual |
|---|---|---|---|---|---|
| `chronos2_completed` | 0.7094 | 0.075 | 0.1831 | 0.4513 | 1.8e-15 |
| `chronos2_hurdle` | 0.7183 | 0.09683 | 0.1799 | 0.4416 | 1.8e-15 |
| `chronos2_hurdle_dynamic` | 0.714 | 0.0892 | 0.1812 | 0.4436 | 3.6e-15 |
| `chronos2_occurrence_model_size_count` | 0.8125 | 0.09126 | 0.2354 | 0.4859 | 1.8e-15 |
| `timesfm3_completed` | 0.705 | 0.09056 | 0.17 | 0.4445 | 1.8e-15 |
| `timesfm3_hurdle` | 0.7152 | 0.09445 | 0.1663 | 0.4545 | 8.9e-16 |
| `timesfm3_hurdle_dynamic` | 0.7122 | 0.08687 | 0.1682 | 0.4571 | 1.8e-15 |
| `timesfm3_occurrence_model_size_count` | 0.815 | 0.1121 | 0.2376 | 0.4653 | 1.8e-15 |
| `timesfm2p5_completed` | 0.7083 | 0.08392 | 0.1616 | 0.4627 | 1.8e-15 |
| `timesfm2p5_hurdle` | 0.7173 | 0.09172 | 0.1591 | 0.4665 | 1.8e-15 |
| `timesfm2p5_hurdle_dynamic` | 0.7147 | 0.08475 | 0.1616 | 0.4683 | 1.8e-15 |
| `timesfm2p5_occurrence_model_size_count` | 0.814 | 0.1074 | 0.2356 | 0.471 | 1.8e-15 |
| `hurdle_count_28` | 0.8291 | 0.1184 | 0.2373 | 0.4734 | 1.8e-15 |
| `hurdle_empirical_28` | 0.7872 | 0.1018 | 0.186 | 0.4994 | 1.8e-15 |
| `dynamic_count` | 0.8175 | 0.1098 | 0.2147 | 0.493 | 1.8e-15 |

## QScore9 accounting, all (n = 300), horizon 7 (equal series; the parts sum to the score)

| Model | QScore9 | Zero days | Positive, over | Positive, under | Largest residual |
|---|---|---|---|---|---|
| `chronos2_completed` | 0.7496 | 0.07656 | 0.1975 | 0.4755 | 3.6e-15 |
| `chronos2_hurdle` | 0.7589 | 0.09765 | 0.1918 | 0.4695 | 3.6e-15 |
| `chronos2_hurdle_dynamic` | 0.7556 | 0.08916 | 0.1944 | 0.472 | 3.6e-15 |
| `chronos2_occurrence_model_size_count` | 0.8479 | 0.09487 | 0.2475 | 0.5056 | 7.1e-15 |
| `timesfm3_completed` | 0.7467 | 0.09015 | 0.1924 | 0.4641 | 7.1e-15 |
| `timesfm3_hurdle` | 0.757 | 0.09473 | 0.1863 | 0.476 | 3.6e-15 |
| `timesfm3_hurdle_dynamic` | 0.7545 | 0.0867 | 0.1893 | 0.4785 | 3.6e-15 |
| `timesfm3_occurrence_model_size_count` | 0.8506 | 0.1136 | 0.2494 | 0.4876 | 7.1e-15 |
| `timesfm2p5_completed` | 0.7478 | 0.08255 | 0.1828 | 0.4825 | 3.6e-15 |
| `timesfm2p5_hurdle` | 0.7559 | 0.09163 | 0.1774 | 0.4869 | 2.7e-15 |
| `timesfm2p5_hurdle_dynamic` | 0.7543 | 0.08408 | 0.1815 | 0.4887 | 1.8e-15 |
| `timesfm2p5_occurrence_model_size_count` | 0.8506 | 0.1086 | 0.2477 | 0.4942 | 5.3e-15 |
| `hurdle_count_28` | 0.8644 | 0.1211 | 0.2469 | 0.4964 | 3.6e-15 |
| `hurdle_empirical_28` | 0.8272 | 0.1052 | 0.1955 | 0.5265 | 3.6e-15 |
| `dynamic_count` | 0.8588 | 0.1099 | 0.2293 | 0.5196 | 3.6e-15 |

## Randomized PIT, dense (n = 100), horizon 30: fraction of target days per tenth

| Model | 0.0-0.1 | 0.1-0.2 | 0.2-0.3 | 0.3-0.4 | 0.4-0.5 | 0.5-0.6 | 0.6-0.7 | 0.7-0.8 | 0.8-0.9 | 0.9-1.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| `chronos2_raw` | unavailable |  |  |  |  |  |  |  |  |  |
| `chronos2_completed` | 0.097 | 0.098 | 0.099 | 0.104 | 0.104 | 0.108 | 0.105 | 0.101 | 0.087 | 0.098 |
| `chronos2_hurdle` | 0.101 | 0.110 | 0.104 | 0.109 | 0.105 | 0.102 | 0.098 | 0.096 | 0.082 | 0.094 |
| `chronos2_hurdle_dynamic` | 0.112 | 0.101 | 0.105 | 0.100 | 0.103 | 0.112 | 0.101 | 0.092 | 0.083 | 0.093 |
| `chronos2_occurrence_model_size_count` | 0.139 | 0.113 | 0.101 | 0.106 | 0.090 | 0.083 | 0.080 | 0.069 | 0.069 | 0.151 |
| `timesfm3_raw` | unavailable |  |  |  |  |  |  |  |  |  |
| `timesfm3_completed` | 0.101 | 0.106 | 0.104 | 0.101 | 0.107 | 0.103 | 0.097 | 0.101 | 0.089 | 0.092 |
| `timesfm3_hurdle` | 0.102 | 0.111 | 0.101 | 0.102 | 0.102 | 0.102 | 0.097 | 0.100 | 0.090 | 0.093 |
| `timesfm3_hurdle_dynamic` | 0.107 | 0.107 | 0.101 | 0.104 | 0.097 | 0.102 | 0.103 | 0.096 | 0.090 | 0.092 |
| `timesfm3_occurrence_model_size_count` | 0.142 | 0.122 | 0.116 | 0.105 | 0.093 | 0.076 | 0.068 | 0.065 | 0.063 | 0.148 |
| `timesfm2p5_raw` | unavailable |  |  |  |  |  |  |  |  |  |
| `timesfm2p5_completed` | 0.095 | 0.103 | 0.110 | 0.101 | 0.101 | 0.103 | 0.096 | 0.097 | 0.090 | 0.103 |
| `timesfm2p5_hurdle` | 0.101 | 0.112 | 0.099 | 0.099 | 0.100 | 0.100 | 0.098 | 0.094 | 0.091 | 0.104 |
| `timesfm2p5_hurdle_dynamic` | 0.110 | 0.106 | 0.098 | 0.094 | 0.102 | 0.102 | 0.100 | 0.095 | 0.087 | 0.105 |
| `timesfm2p5_occurrence_model_size_count` | 0.138 | 0.118 | 0.118 | 0.111 | 0.095 | 0.077 | 0.068 | 0.065 | 0.064 | 0.148 |
| `local_mean_28` | unavailable |  |  |  |  |  |  |  |  |  |
| `autoets_weekly` | unavailable |  |  |  |  |  |  |  |  |  |
| `nb_local_level_28` | 0.088 | 0.091 | 0.090 | 0.099 | 0.109 | 0.102 | 0.115 | 0.115 | 0.098 | 0.094 |
| `poisson_28` | 0.224 | 0.112 | 0.089 | 0.083 | 0.069 | 0.067 | 0.069 | 0.065 | 0.069 | 0.152 |
| `hurdle_count_28` | 0.156 | 0.125 | 0.110 | 0.096 | 0.091 | 0.074 | 0.069 | 0.066 | 0.067 | 0.147 |
| `hurdle_empirical_28` | 0.117 | 0.105 | 0.097 | 0.100 | 0.097 | 0.091 | 0.094 | 0.089 | 0.096 | 0.114 |
| `dynamic_count` | 0.154 | 0.117 | 0.109 | 0.103 | 0.094 | 0.085 | 0.067 | 0.061 | 0.069 | 0.141 |

## Randomized PIT, sparse (n = 100), horizon 30: fraction of target days per tenth

| Model | 0.0-0.1 | 0.1-0.2 | 0.2-0.3 | 0.3-0.4 | 0.4-0.5 | 0.5-0.6 | 0.6-0.7 | 0.7-0.8 | 0.8-0.9 | 0.9-1.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| `chronos2_raw` | unavailable |  |  |  |  |  |  |  |  |  |
| `chronos2_completed` | 0.093 | 0.098 | 0.094 | 0.093 | 0.092 | 0.099 | 0.099 | 0.111 | 0.117 | 0.102 |
| `chronos2_hurdle` | 0.107 | 0.105 | 0.101 | 0.101 | 0.096 | 0.102 | 0.098 | 0.106 | 0.102 | 0.082 |
| `chronos2_hurdle_dynamic` | 0.096 | 0.101 | 0.096 | 0.100 | 0.095 | 0.102 | 0.096 | 0.110 | 0.117 | 0.087 |
| `chronos2_occurrence_model_size_count` | 0.094 | 0.096 | 0.093 | 0.085 | 0.097 | 0.099 | 0.101 | 0.104 | 0.105 | 0.125 |
| `timesfm3_raw` | unavailable |  |  |  |  |  |  |  |  |  |
| `timesfm3_completed` | 0.109 | 0.103 | 0.098 | 0.101 | 0.099 | 0.107 | 0.096 | 0.099 | 0.104 | 0.085 |
| `timesfm3_hurdle` | 0.096 | 0.105 | 0.096 | 0.101 | 0.107 | 0.105 | 0.098 | 0.096 | 0.105 | 0.090 |
| `timesfm3_hurdle_dynamic` | 0.097 | 0.101 | 0.096 | 0.092 | 0.098 | 0.097 | 0.105 | 0.098 | 0.114 | 0.102 |
| `timesfm3_occurrence_model_size_count` | 0.104 | 0.098 | 0.106 | 0.102 | 0.108 | 0.102 | 0.094 | 0.096 | 0.091 | 0.100 |
| `timesfm2p5_raw` | unavailable |  |  |  |  |  |  |  |  |  |
| `timesfm2p5_completed` | 0.094 | 0.101 | 0.105 | 0.098 | 0.099 | 0.096 | 0.094 | 0.097 | 0.098 | 0.117 |
| `timesfm2p5_hurdle` | 0.107 | 0.103 | 0.104 | 0.093 | 0.102 | 0.096 | 0.094 | 0.097 | 0.101 | 0.102 |
| `timesfm2p5_hurdle_dynamic` | 0.096 | 0.096 | 0.094 | 0.096 | 0.095 | 0.097 | 0.106 | 0.101 | 0.109 | 0.111 |
| `timesfm2p5_occurrence_model_size_count` | 0.097 | 0.099 | 0.099 | 0.101 | 0.100 | 0.099 | 0.099 | 0.095 | 0.095 | 0.116 |
| `local_mean_28` | unavailable |  |  |  |  |  |  |  |  |  |
| `autoets_weekly` | unavailable |  |  |  |  |  |  |  |  |  |
| `nb_local_level_28` | 0.098 | 0.090 | 0.095 | 0.096 | 0.092 | 0.096 | 0.098 | 0.113 | 0.106 | 0.117 |
| `poisson_28` | 0.111 | 0.105 | 0.104 | 0.106 | 0.100 | 0.088 | 0.092 | 0.090 | 0.087 | 0.117 |
| `hurdle_count_28` | 0.110 | 0.102 | 0.103 | 0.100 | 0.100 | 0.102 | 0.093 | 0.092 | 0.092 | 0.107 |
| `hurdle_empirical_28` | 0.100 | 0.104 | 0.105 | 0.101 | 0.095 | 0.102 | 0.091 | 0.094 | 0.102 | 0.105 |
| `dynamic_count` | 0.104 | 0.093 | 0.089 | 0.102 | 0.101 | 0.096 | 0.100 | 0.100 | 0.102 | 0.112 |

## Randomized PIT, very sparse (n = 100), horizon 30: fraction of target days per tenth

| Model | 0.0-0.1 | 0.1-0.2 | 0.2-0.3 | 0.3-0.4 | 0.4-0.5 | 0.5-0.6 | 0.6-0.7 | 0.7-0.8 | 0.8-0.9 | 0.9-1.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| `chronos2_raw` | unavailable |  |  |  |  |  |  |  |  |  |
| `chronos2_completed` | 0.106 | 0.107 | 0.100 | 0.104 | 0.098 | 0.104 | 0.103 | 0.104 | 0.100 | 0.075 |
| `chronos2_hurdle` | 0.105 | 0.095 | 0.106 | 0.108 | 0.106 | 0.093 | 0.102 | 0.101 | 0.095 | 0.089 |
| `chronos2_hurdle_dynamic` | 0.101 | 0.096 | 0.100 | 0.100 | 0.099 | 0.103 | 0.098 | 0.103 | 0.102 | 0.097 |
| `chronos2_occurrence_model_size_count` | 0.105 | 0.103 | 0.104 | 0.102 | 0.103 | 0.107 | 0.100 | 0.105 | 0.099 | 0.073 |
| `timesfm3_raw` | unavailable |  |  |  |  |  |  |  |  |  |
| `timesfm3_completed` | 0.102 | 0.103 | 0.100 | 0.110 | 0.105 | 0.106 | 0.099 | 0.107 | 0.104 | 0.064 |
| `timesfm3_hurdle` | 0.103 | 0.100 | 0.105 | 0.100 | 0.102 | 0.100 | 0.100 | 0.098 | 0.103 | 0.088 |
| `timesfm3_hurdle_dynamic` | 0.105 | 0.096 | 0.100 | 0.097 | 0.105 | 0.100 | 0.098 | 0.101 | 0.098 | 0.098 |
| `timesfm3_occurrence_model_size_count` | 0.101 | 0.105 | 0.105 | 0.103 | 0.106 | 0.109 | 0.105 | 0.102 | 0.097 | 0.067 |
| `timesfm2p5_raw` | unavailable |  |  |  |  |  |  |  |  |  |
| `timesfm2p5_completed` | 0.105 | 0.103 | 0.107 | 0.104 | 0.101 | 0.101 | 0.103 | 0.101 | 0.102 | 0.073 |
| `timesfm2p5_hurdle` | 0.097 | 0.103 | 0.100 | 0.099 | 0.106 | 0.101 | 0.104 | 0.097 | 0.104 | 0.088 |
| `timesfm2p5_hurdle_dynamic` | 0.104 | 0.101 | 0.109 | 0.100 | 0.096 | 0.097 | 0.100 | 0.095 | 0.101 | 0.099 |
| `timesfm2p5_occurrence_model_size_count` | 0.105 | 0.101 | 0.104 | 0.105 | 0.110 | 0.104 | 0.105 | 0.097 | 0.098 | 0.072 |
| `local_mean_28` | unavailable |  |  |  |  |  |  |  |  |  |
| `autoets_weekly` | unavailable |  |  |  |  |  |  |  |  |  |
| `nb_local_level_28` | 0.102 | 0.099 | 0.100 | 0.094 | 0.095 | 0.100 | 0.100 | 0.100 | 0.105 | 0.105 |
| `poisson_28` | 0.103 | 0.100 | 0.098 | 0.100 | 0.097 | 0.104 | 0.097 | 0.099 | 0.102 | 0.100 |
| `hurdle_count_28` | 0.100 | 0.098 | 0.102 | 0.105 | 0.104 | 0.098 | 0.106 | 0.102 | 0.096 | 0.088 |
| `hurdle_empirical_28` | 0.099 | 0.103 | 0.105 | 0.098 | 0.100 | 0.108 | 0.099 | 0.099 | 0.101 | 0.088 |
| `dynamic_count` | 0.100 | 0.097 | 0.100 | 0.100 | 0.104 | 0.103 | 0.095 | 0.103 | 0.098 | 0.099 |

## Randomized PIT, all (n = 300), horizon 30: fraction of target days per tenth

| Model | 0.0-0.1 | 0.1-0.2 | 0.2-0.3 | 0.3-0.4 | 0.4-0.5 | 0.5-0.6 | 0.6-0.7 | 0.7-0.8 | 0.8-0.9 | 0.9-1.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| `chronos2_raw` | unavailable |  |  |  |  |  |  |  |  |  |
| `chronos2_completed` | 0.099 | 0.101 | 0.098 | 0.100 | 0.098 | 0.104 | 0.103 | 0.105 | 0.101 | 0.092 |
| `chronos2_hurdle` | 0.104 | 0.103 | 0.103 | 0.106 | 0.102 | 0.099 | 0.099 | 0.101 | 0.093 | 0.088 |
| `chronos2_hurdle_dynamic` | 0.103 | 0.099 | 0.100 | 0.100 | 0.099 | 0.106 | 0.098 | 0.102 | 0.101 | 0.092 |
| `chronos2_occurrence_model_size_count` | 0.113 | 0.104 | 0.099 | 0.098 | 0.096 | 0.096 | 0.094 | 0.092 | 0.091 | 0.116 |
| `timesfm3_raw` | unavailable |  |  |  |  |  |  |  |  |  |
| `timesfm3_completed` | 0.104 | 0.104 | 0.101 | 0.104 | 0.104 | 0.105 | 0.097 | 0.102 | 0.099 | 0.080 |
| `timesfm3_hurdle` | 0.101 | 0.106 | 0.101 | 0.101 | 0.104 | 0.102 | 0.098 | 0.098 | 0.099 | 0.091 |
| `timesfm3_hurdle_dynamic` | 0.103 | 0.101 | 0.099 | 0.098 | 0.100 | 0.100 | 0.102 | 0.098 | 0.101 | 0.097 |
| `timesfm3_occurrence_model_size_count` | 0.116 | 0.109 | 0.109 | 0.103 | 0.102 | 0.095 | 0.089 | 0.088 | 0.084 | 0.105 |
| `timesfm2p5_raw` | unavailable |  |  |  |  |  |  |  |  |  |
| `timesfm2p5_completed` | 0.098 | 0.102 | 0.107 | 0.101 | 0.100 | 0.100 | 0.098 | 0.099 | 0.097 | 0.098 |
| `timesfm2p5_hurdle` | 0.102 | 0.106 | 0.101 | 0.097 | 0.103 | 0.099 | 0.099 | 0.096 | 0.099 | 0.098 |
| `timesfm2p5_hurdle_dynamic` | 0.103 | 0.101 | 0.100 | 0.097 | 0.098 | 0.099 | 0.102 | 0.097 | 0.099 | 0.105 |
| `timesfm2p5_occurrence_model_size_count` | 0.113 | 0.106 | 0.107 | 0.105 | 0.102 | 0.093 | 0.091 | 0.086 | 0.086 | 0.112 |
| `local_mean_28` | unavailable |  |  |  |  |  |  |  |  |  |
| `autoets_weekly` | unavailable |  |  |  |  |  |  |  |  |  |
| `nb_local_level_28` | 0.096 | 0.093 | 0.095 | 0.096 | 0.099 | 0.099 | 0.104 | 0.109 | 0.103 | 0.105 |
| `poisson_28` | 0.146 | 0.105 | 0.097 | 0.096 | 0.089 | 0.087 | 0.086 | 0.085 | 0.086 | 0.123 |
| `hurdle_count_28` | 0.122 | 0.108 | 0.105 | 0.100 | 0.098 | 0.092 | 0.090 | 0.086 | 0.085 | 0.114 |
| `hurdle_empirical_28` | 0.106 | 0.104 | 0.102 | 0.100 | 0.098 | 0.100 | 0.095 | 0.094 | 0.100 | 0.102 |
| `dynamic_count` | 0.119 | 0.102 | 0.100 | 0.102 | 0.100 | 0.095 | 0.087 | 0.088 | 0.090 | 0.117 |

## Files

| File | What it holds |
|---|---|
| `RESULTS-nyc311.md` | This page |
| `run.json` | The run's state: identity, metadata (readiness, family, specification, implementation commit, the addition's authority, source hashes, packages, hardware), the SHA-256 of each checkpoint, per-model timings, wall time, memory |
| `inference/` | The output of `scripts/study3_inference.py`: `inference.csv` and `inference.json` (the family), `paired_entities.csv`, `family_descriptors.csv`, `series_scores.csv`, `secondary_*.csv`, `pit_histograms.csv`, `pit_values.parquet`, `provenance.json` |
| `integrity/` | The output of `scripts/study3_integrity.py`: `integrity.csv` (every forecast's saved and recomputed scores), `integrity.json`, `integrity.log` |
| `target-pull/pull.json`, `target-pull/completeness.json` | The target pull's ledger and completeness document (with the per-day target census), byte copies of the files under `data\raw\study3\nyc311\targets\` |
| `make_tables.py` | Prints the tables above from `inference/`, `run.json`, the manifest and the signals; written before the run and the inference and dry-run on toy runs only |
| `results-provenance.json` | The SHA-256 of every file in this directory, the checkpoints included, and of the inputs; the approvals, the gate, the pull, the run, the inference and the integrity check with their commands and times |
| `.gitattributes`, `.gitignore` | Byte preservation; the checkpoints are kept out of the tree |

The 300 whole-series checkpoints (`<SHA-256 of the series label>.json`, 645 MB) are not in the tree, as Study 1's
and Study 2's are not. Their SHA-256 values are in `run.json`, `inference/provenance.json`, `integrity/integrity.json`
and `results-provenance.json`. The inference and the integrity check read them.

The raw target captures and `signals.parquet` stay under the ignored `data\raw\study3\nyc311\targets\`. Their hashes
are in the completeness document. `make_tables.py` reads the signals for the zero-context counts and checks them
against the readiness's hash.

## Regeneration

From the repository root, PowerShell. The pull and the run pass the gate only at the implementation commit, with the
smoke and the readiness files at the paths the readiness names (`data\raw\study3\`; the tracked copies are under
`study\study3\`). The pull refuses to write a second snapshot, and a completed run directory is immutable, so a
rerun takes new output paths. A new pull opens the targets again and needs its own approval.

```powershell
.\.venv\Scripts\python.exe scripts\study2_smoke.py --study3 --gpu --out data\raw\study3\smoke-00fd91d.json
.\.venv\Scripts\python.exe scripts\study2_run.py study3 --readiness data\raw\study3\study3-readiness-00fd91d.json --out data\raw\study3\nyc311\targets --fetch-targets --max-requests 100 --timeout 120
.\.venv\Scripts\python.exe scripts\study2_run.py study3 --readiness data\raw\study3\study3-readiness-00fd91d.json --out data\raw\study3\nyc311\targets --fetch-targets --max-requests 20 --interval 3 --timeout 120
$env:HF_HUB_OFFLINE = "1"; $env:TRANSFORMERS_OFFLINE = "1"; .\.venv\Scripts\python.exe scripts\study2_run.py study3 --readiness data\raw\study3\study3-readiness-00fd91d-run.json --out reports\study3-nyc311\run-2026-10-17
.\.venv\Scripts\python.exe scripts\study3_inference.py --run reports\study3-nyc311\run-2026-10-17 --out <new directory>
.\.venv\Scripts\python.exe scripts\study3_integrity.py --run reports\study3-nyc311\run-2026-10-17 --out <new directory>
.\.venv\Scripts\python.exe reports\study3-nyc311\run-2026-10-17\make_tables.py reports\study3-nyc311\run-2026-10-17
```

`scripts\study2_gate.py` does not take `study3`. The gate is `pulsegraph.study2.gate.authorize_study3(<readiness>)`,
which the pull and the run call before any access.

The inference ran from 04:03:34 to 04:04:44 UTC and the integrity check from 04:04:49 to 04:05:03 UTC. Both ran
with HEAD at the implementation commit and no uncommitted change under the scripts or `pulsegraph/`, using NumPy
2.5.3, SciPy 1.18.1 and pandas 2.3.3. `inference/provenance.json` and `integrity/integrity.json` record this.

A reader of the CSVs who recomputes tests should parse floats exactly (pandas `float_precision="round_trip"`). The
default parser can move a last digit and change rank ties.

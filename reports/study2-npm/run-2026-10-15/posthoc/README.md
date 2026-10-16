# Post-hoc: the npm family E01 to E18 without three source zero days

**This is post-hoc.** It was computed on 2026-10-16 from the saved forecasts of the npm external run of
2026-10-15, after the registered scores were seen. The registered analysis of the data as served, in
`../inference/`, stays the confirmatory result for E01 to E18 (`PROTOCOL.md`, dated addition of 2026-10-16,
item 6). Nothing in `../inference/` or `../integrity/` changed, and nothing here replaces it.

## What was removed

- **The days.** On 2026-07-12 and 2026-08-14 the download API reports 0 for all 209 series. On 2026-06-25 it
  reports 0 for the largest series, `aggregate-error`, between 9,475,033 and 7,909,626; 92 of the 209
  series read 0 that day, against 98 and 121 on the days either side (`../target-pull/daily_summary.csv`).
- **Where they fall.** Each day lies in one horizon-30 target block: 2026-06-25 in the block from 2026-06-03,
  2026-07-12 in the block from 2026-07-03, and 2026-08-14 in the block from 2026-08-02. No horizon-7 block
  holds any of them, so every horizon-7 score is the saved one.
- **How.** A removed day is dropped from its block for every series and every variant. The block's QScore9
  is then the registered formula averaged over its remaining 29 days and the nine deciles. Two scenarios:
  - all three days, which re-scores 10,032 horizon-30 forecasts;
  - the two panel-wide days only, which re-scores 6,688.
- **The inference.** The registered functions of `scripts/study2_inference.py` run unchanged on the new
  scores:
  - origins averaged within series and horizon, the 209 series weighed equally, model minus reference;
  - the two-sided approximate Wilcoxon signed-rank test, with zero differences omitted;
  - the 20,000-replicate series bootstrap, with the registered seed of each comparison;
  - BH once over the eighteen, at q = 0.05.
- **The checks.** Run first on the saved scores, the same code reproduces `../inference/inference.csv` and
  `../inference/paired_entities.csv` byte for byte. Re-scored on their full blocks, all 20,064 saved forecasts
  match their saved QScore9 exactly (largest residual 0.0). The horizon-30 targets rebuild
  `daily_summary.csv` on all 90 target days.

## What changes

- **Without the three days, none of the eighteen conclusions changes.** No row changes its direction (the
  larger signed-rank sum), the sign of its mean difference or its rejection. Twelve reject, as registered:
  ten for the model variant, and two against the hurdle (E10 and E16).
- **Without the two panel-wide days, one conclusion changes.** E06 (`chronos2_raw` against
  `local_mean_28`, horizon 30) no longer rejects:
  - BH p 0.060 and raw p 0.040, against 0.012 and 0.0066 registered;
  - it still favors the model by rank sum, and the model is lower in 110 of 209 series.
  The other seventeen are unchanged, and eleven reject.
- **The horizon-7 rows.** Their means, intervals, medians, counts and raw p are identical to the registered
  ones. Only their BH p moves, because BH ranks all eighteen together:
  - E01 0.203 to 0.188 and E07 0.236 to 0.220 without the three days;
  - E07 0.236 to 0.230 and E09 0.0438 to 0.0478 without the two days.
- **Hurdle against completed, horizon 30.** The mean differences grow without the three days: E04 from +90 to
  +159, E10 from +129 to +201, E16 from +110 to +183. These means belong to `aggregate-error`. E04's median
  difference goes from −0.00025 to exactly 0 (104 lower, 2 tied, 103 higher).

Each cell gives the mean difference / BH p / BH rejects at 0.05. Differences are model minus reference
QScore9, so a negative value favors the model variant. The last column is the side with the larger
signed-rank sum, which is the same in all three analyses.

| ID | Model variant | Reference | h | Registered | Without the three days | Without the two panel-wide days | Larger rank sum favors |
|---|---|---|---|---|---|---|---|
| E01 | `chronos2_hurdle` | `chronos2_completed` | 7 | 152 / 0.203 / no | 152 / 0.188 / no | 152 / 0.203 / no | model |
| E02 | `chronos2_hurdle` | `hurdle_count_28` | 7 | -5090 / 3.72e-11 / yes | -5090 / 3.72e-11 / yes | -5090 / 3.72e-11 / yes | model |
| E03 | `chronos2_raw` | `local_mean_28` | 7 | -2884 / 0.596 / no | -2884 / 0.596 / no | -2884 / 0.596 / no | model |
| E04 | `chronos2_hurdle` | `chronos2_completed` | 30 | 90.24 / 0.449 / no | 159.3 / 0.188 / no | 143.4 / 0.23 / no | reference |
| E05 | `chronos2_hurdle` | `hurdle_count_28` | 30 | -6563 / 7.06e-21 / yes | -6473 / 2.89e-20 / yes | -6311 / 3.76e-20 / yes | model |
| E06 | `chronos2_raw` | `local_mean_28` | 30 | -4734 / 0.0119 / yes | -4834 / 0.0359 / yes | -4646 / 0.0599 / no | model |
| E07 | `timesfm3_hurdle` | `timesfm3_completed` | 7 | 176.9 / 0.236 / no | 176.9 / 0.22 / no | 176.9 / 0.23 / no | reference |
| E08 | `timesfm3_hurdle` | `hurdle_count_28` | 7 | -5416 / 3.61e-08 / yes | -5416 / 3.61e-08 / yes | -5416 / 3.61e-08 / yes | model |
| E09 | `timesfm3_raw` | `local_mean_28` | 7 | -3235 / 0.0438 / yes | -3235 / 0.0438 / yes | -3235 / 0.0478 / yes | model |
| E10 | `timesfm3_hurdle` | `timesfm3_completed` | 30 | 128.5 / 0.00215 / yes | 201.2 / 0.00179 / yes | 184.9 / 0.00211 / yes | reference |
| E11 | `timesfm3_hurdle` | `hurdle_count_28` | 30 | -6792 / 3.19e-25 / yes | -6744 / 2.33e-24 / yes | -6563 / 1.16e-24 / yes | model |
| E12 | `timesfm3_raw` | `local_mean_28` | 30 | -5001 / 3.82e-05 / yes | -5147 / 5.84e-05 / yes | -4940 / 8.76e-05 / yes | model |
| E13 | `timesfm2p5_hurdle` | `timesfm2p5_completed` | 7 | 253.9 / 0.628 / no | 253.9 / 0.628 / no | 253.9 / 0.628 / no | reference |
| E14 | `timesfm2p5_hurdle` | `hurdle_count_28` | 7 | -5847 / 2.66e-05 / yes | -5847 / 2.66e-05 / yes | -5847 / 2.66e-05 / yes | model |
| E15 | `timesfm2p5_raw` | `local_mean_28` | 7 | -3743 / 0.746 / no | -3743 / 0.746 / no | -3743 / 0.746 / no | model |
| E16 | `timesfm2p5_hurdle` | `timesfm2p5_completed` | 30 | 110.3 / 0.0276 / yes | 183.4 / 0.0257 / yes | 167.1 / 0.0344 / yes | reference |
| E17 | `timesfm2p5_hurdle` | `hurdle_count_28` | 30 | -6918 / 1.77e-23 / yes | -6857 / 4.79e-22 / yes | -6709 / 2.46e-22 / yes | model |
| E18 | `timesfm2p5_raw` | `local_mean_28` | 30 | -5109 / 0.00204 / yes | -5242 / 0.00988 / yes | -5068 / 0.00638 / yes | model |

What npm's own records say about the three days is in `docs/research/2026-10-16-npm-zero-days.md`.

## Files and regeneration

| File | What it holds | SHA-256 |
|---|---|---|
| `sensitivity_zero_days.py` | The command; its docstring states every rule above | `518deaa45b9e75d04ca518feecc1165cba27c8f5f1d07b2bcd85303d2a3d00b0` |
| `sensitivity_inference.csv` | The eighteen rows of each scenario in `inference.csv`'s columns, with the rank sums, the registered row's values and the changes | `1a849c4fa36e301e9e1f2d72d680a2a212b9604067d0e04c1f9d96979e3b650b` |
| `sensitivity_paired_entities.csv` | The 209 series differences of every row of each scenario | `a35dc542d0656580f5d248446714d0e84ef4118ad77a3041b9a4d05c1ef2de77` |
| `sensitivity.json` | The checks, the scenarios, the hashes of the run, the scripts and the outputs, the package versions and the times | `1cc8cf0a65610b47ad3dcd753d3a7798233986e452398ecdf6db7274c9401590` |

The command ran from 03:21:52 to 03:21:59 UTC on 2026-10-16, at HEAD `e41fdf2` with no uncommitted change
under `scripts/study2_inference.py` or `pulsegraph/`, with NumPy 2.5.3, SciPy 1.18.1 and pandas 2.3.3. It
refuses to overwrite its outputs and needs the 209 checkpoints, which are not in the tree (their SHA-256
values are in `../run.json`). From the repository root, PowerShell, writing to a new directory:

```powershell
.\.venv\Scripts\python.exe reports\study2-npm\run-2026-10-15\posthoc\sensitivity_zero_days.py reports\study2-npm\run-2026-10-15 --out <new directory>
```

The table above is the first block it prints, and the per-scenario tables follow. Its tests run on a toy run
directory: `tests/test_study2_zero_days_sensitivity.py`.

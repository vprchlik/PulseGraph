# The release assets

Written 2026-10-18 07:17 UTC. Six files that the documents' numbers trace to are not in the tree: Study 1's
forecast file is 433 MB, the three Study 2 and Study 3 runs keep their 1,049 whole-series checkpoints out of
the tree by their `.gitignore`, and the npm and NYC 311 target signals sit under the ignored `data\raw\`. They
are published as assets of the GitHub release. This page lists each with its size and SHA-256, what it holds,
which numbers trace to it, where it goes after download and the command that then regenerates the numbers.

Every size and hash below was computed from the files themselves on 2026-10-18 by
`reports\release\build_assets.py`, which first matches every checkpoint to its run's `run.json` and every
copy to the hash its run recorded; a second build gave the same bytes. `reports\release\verify_assets.py`
checks a download against this table and unpacks the archives.

- **Release:** to be filled (proposed tag `assets-2026-10-18`).
- **DOI of the Study 1 report and of the paper:** to be filled.

## The assets

| File | Bytes | SHA-256 | What it holds | Numbers that trace to it | Place after download | Then regenerate with | URL |
|---|---:|---|---|---|---|---|---|
| `results.parquet` | 433,172,286 | `53ff5a5316fd43dd898866c4fc54edf913b080a32cbd696d7e3b3fc528f62df6` | Study 1's registered run of 2026-09-13: all 48,600 forecast rows (300 repositories, 3 cutoffs, 3 horizons, 18 models), each with its context, targets, nine deciles, samples, scores and model metadata | `RESULTS.md` (the 18 registered rows and the declared descriptive tables); `reports/registered-2026-09-13/inference/`, `descriptive/` and `posthoc/`; the Study 1 report and the Study 1 numbers of the paper | copy to `reports\registered-2026-09-13\run\results.parquet` | `scripts.review_integrity`, `scripts.registered_inference`, `summarize_descriptives.py` (below) | to be filled |
| `study2-synthetic-2026-10-15-checkpoints.zip` | 53,632,214 | `418297fcd19f2c2f09a6b9ce55a68bbf84669b57d0b3c610e924ff71218f5afa` | The 540 whole-series checkpoints of the registered synthetic grid run (18 cells, 30 replicates), 876,970,456 bytes unpacked: every forecast, target and score of its 55,080 forecasts | `reports/study2-synthetic-2026-10-15/RESULTS-synthetic.md` and S01 to S06 in `RESULTS.md`; the grid tables of the two post-hoc analyses; the grid numbers of the paper | unpack into `reports\study2-synthetic-2026-10-15\` | `scripts\study2_inference.py synthetic` (below) | to be filled |
| `study2-npm-run-2026-10-15-checkpoints.zip` | 25,249,139 | `f460588181d743b484266d7bff2f9ca3a8d534bc795647a7e10f5dbe5746165b` | The 209 whole-series checkpoints of the npm external run, 338,301,244 bytes unpacked: every forecast, target and score of its 20,064 forecasts | `reports/study2-npm/run-2026-10-15/RESULTS-npm.md` and E01 to E18 in `RESULTS.md`; the zero-day sensitivity under `posthoc/`; the npm tables of the two post-hoc analyses; the npm numbers of the paper | unpack into `reports\study2-npm\run-2026-10-15\` | `scripts\study2_inference.py external_packages`, `scripts\study2_integrity.py external_packages` (below) | to be filled |
| `study2-npm-targets-signals.parquet` | 105,460 | `c3f4e5437a21587ad38f37cc5dc709424347e721fa228588db118ed07ea0245c` | The daily download counts the npm run read: 209 series, 2025-09-01 to 2026-08-31, 76,285 rows (`series_id`, `date`, `count`); the 275 context days equal the frozen selection context | the per-day source summary (`target-pull/daily_summary.csv`) behind the zero-day note of `RESULTS-npm.md` and dated addition 6; the committed `reports/study2-npm/panel/daily_counts.csv` | copy to `data\raw\study2\npm\targets\signals.parquet` | `target_days.py`, `build_daily_counts.py npm --no-context` (below) | to be filled |
| `study3-nyc311-run-2026-10-17-checkpoints.zip` | 38,676,505 | `e1a1ea9d01c2d6931d87d65128a7b63791ab08c2e5c8d11f0544323d8bc32825` | The 300 whole-series checkpoints of the Study 3 run on NYC 311, 645,013,954 bytes unpacked: every forecast, target and score of its 39,600 forecasts | `reports/study3-nyc311/run-2026-10-17/RESULTS-nyc311.md` and R01 to R36 in `RESULTS.md`; the NYC 311 tables of the post-hoc benchmark; the completion-floor and tie counts of the paper, which its checker recomputes only when these checkpoints are present | unpack into `reports\study3-nyc311\run-2026-10-17\` | `scripts\study3_inference.py`, `scripts\study3_integrity.py` (below) | to be filled |
| `study3-nyc311-targets-signals.parquet` | 91,655 | `8f85b2e2a90e4ecd81aadf73de753b9d976aeef02ba53039c0d6fc91bb2b02c3` | The daily request counts the NYC 311 run read: 300 problem-by-board series, 2025-09-01 to 2026-08-31, 109,500 rows (`series_id`, `date`, `count`); the 275 context days equal the frozen selection context | the strata, zero-context and request-day tables of `RESULTS-nyc311.md` (`make_tables.py`); the committed `reports/study3-nyc311/panel/daily_counts.csv` | copy to `data\raw\study3\nyc311\targets\signals.parquet` | `make_tables.py`, `build_daily_counts.py nyc311 --no-context` (below) | to be filled |

Every file is under 2,000,000,000 bytes, below the per-file limit of 2 GiB that GitHub states for release assets
(that documentation was not re-read for this page). Study 1's 300 per-repository recovery checkpoints duplicate rows
of `results.parquet` and are not released, as `README.md` says. No model weights and no raw capture are released.

## Committed, not assets

The aggregated daily-count dataset that `CONTRIBUTING.md` commits when its size allows. Each file holds every day
the study used for every series of its frozen panel, sorted, UTF-8 with LF line endings, and sits beside the panel's
manifest with a `daily_counts.provenance.json` that names its inputs by SHA-256, its command and its source
statement. `tests\test_release_daily_counts.py` rebuilds each byte for byte, from the frozen context and the signals
when both are present and from the signals alone.

| File | Bytes | SHA-256 | Rows | Columns | Rebuild |
|---|---:|---|---:|---|---|
| `reports/study2-npm/panel/daily_counts.csv` | 4,591,019 | `45a972dec1c9baeb23177b9dd46080015cc63ee71eb51862b96c379d005b54b4` | 76,285 | `package`, `created_at` (as the manifest records it), `day`, `count` | `reports\release\build_daily_counts.py npm` |
| `reports/study3-nyc311/panel/daily_counts.csv` | 4,505,286 | `88edf554d1d27e3daa6a8bb94c372335eb8b8716b401a3ecea44bb5509977588` | 109,500 | `problem`, `board` (as the manifest names them), `day`, `count` | `reports\release\build_daily_counts.py nyc311` |

## Checking a download and placing it

From the repository root, PowerShell, with the assets downloaded into one directory (here `downloads\`). The first
command checks every asset it finds against the table above and, for each archive, that its entries are exactly the
checkpoints its run's `run.json` names. The second unpacks the archives into their run directories: only into a run
directory that holds no checkpoint yet, after hashing every entry against `run.json`, never overwriting a file, and
hashing every written file again. The copies are placed by hand; a third check then reports each placed copy.

```powershell
.\.venv\Scripts\python.exe reports\release\verify_assets.py downloads
.\.venv\Scripts\python.exe reports\release\verify_assets.py downloads --unpack all
Copy-Item downloads\results.parquet reports\registered-2026-09-13\run\results.parquet
New-Item -ItemType Directory -Force data\raw\study2\npm\targets
Copy-Item downloads\study2-npm-targets-signals.parquet data\raw\study2\npm\targets\signals.parquet
New-Item -ItemType Directory -Force data\raw\study3\nyc311\targets
Copy-Item downloads\study3-nyc311-targets-signals.parquet data\raw\study3\nyc311\targets\signals.parquet
.\.venv\Scripts\python.exe reports\release\verify_assets.py downloads
```

The verifier uses the standard library only. A run directory's checkpoints can also be checked against `run.json`
by the integrity commands below, which read them.

## Regenerating the numbers

The commands are those of `README.md` and the results pages, unchanged. None needs a GPU, a model or the network.
Every command but one writes to the new directory or file it is given, or only prints; the inference commands record
the HEAD they ran at and do not require the implementation commit.

Study 1 (`results.parquet`). The integrity review prints its verdict; the inference writes to a new directory; the
post-hoc accounting, given `--out`, writes there. `summarize_descriptives.py` is the exception: it rewrites
`RESULTS.md` whole and the CSVs under `reports/registered-2026-09-13/descriptive/` in place, as it did when the Study 1
results were written, so on a current clone it drops the sections appended to `RESULTS.md` since. Run it on a
separate clone and compare the Study 1 part of its `RESULTS.md` and its CSVs with the committed ones, or restore both
afterwards with `git checkout -- RESULTS.md reports/registered-2026-09-13/descriptive`.

```powershell
.\.venv\Scripts\python.exe -m scripts.review_integrity --run reports/registered-2026-09-13/run
.\.venv\Scripts\python.exe -m scripts.registered_inference --run reports/registered-2026-09-13/run --out data/cache/inference-reproduction
.\.venv\Scripts\python.exe reports/registered-2026-09-13/posthoc/accounting.py --out data/cache/posthoc-reproduction
.\.venv\Scripts\python.exe reports/registered-2026-09-13/summarize_descriptives.py
```

Study 2, the synthetic grid (its checkpoints):

```powershell
.\.venv\Scripts\python.exe scripts\study2_inference.py synthetic --run reports\study2-synthetic-2026-10-15 --out <new directory>
.\.venv\Scripts\python.exe reports\study2-synthetic-2026-10-15\make_tables.py reports\study2-synthetic-2026-10-15\inference
.\.venv\Scripts\python.exe reports\study2-synthetic-2026-10-15\recompute_scores.py reports\study2-synthetic-2026-10-15 --out <new file>
```

Study 2, npm (its checkpoints; `target_days.py` and the daily counts read the signals):

```powershell
.\.venv\Scripts\python.exe scripts\study2_inference.py external_packages --run reports\study2-npm\run-2026-10-15 --out <new directory>
.\.venv\Scripts\python.exe scripts\study2_integrity.py external_packages --run reports\study2-npm\run-2026-10-15 --out <new directory>
.\.venv\Scripts\python.exe reports\study2-npm\run-2026-10-15\make_tables.py reports\study2-npm\run-2026-10-15\inference
.\.venv\Scripts\python.exe reports\study2-npm\run-2026-10-15\check_directions.py reports\study2-npm\run-2026-10-15\inference
.\.venv\Scripts\python.exe reports\study2-npm\run-2026-10-15\posthoc\sensitivity_zero_days.py reports\study2-npm\run-2026-10-15 --out <new directory>
.\.venv\Scripts\python.exe reports\study2-npm\run-2026-10-15\target_days.py data\raw\study2\npm\targets\signals.parquet reports\study2-npm\panel\manifest.json --out <new file>
.\.venv\Scripts\python.exe reports\release\build_daily_counts.py npm --no-context --out <new directory>
```

Study 3, NYC 311 (its checkpoints; `make_tables.py` and the daily counts read the signals):

```powershell
.\.venv\Scripts\python.exe scripts\study3_inference.py --run reports\study3-nyc311\run-2026-10-17 --out <new directory>
.\.venv\Scripts\python.exe scripts\study3_integrity.py --run reports\study3-nyc311\run-2026-10-17 --out <new directory>
.\.venv\Scripts\python.exe reports\study3-nyc311\run-2026-10-17\make_tables.py reports\study3-nyc311\run-2026-10-17
.\.venv\Scripts\python.exe reports\release\build_daily_counts.py nyc311 --no-context --out <new directory>
```

The post-hoc analyses across runs (the checkpoints of the runs they name):

```powershell
.\.venv\Scripts\python.exe reports\study2-posthoc-dynamic-occurrence\dynamic_occurrence.py --npm reports\study2-npm\run-2026-10-15 --synthetic reports\study2-synthetic-2026-10-15 --out <new directory>
.\.venv\Scripts\python.exe reports\study2-posthoc-intermittent-baselines\intermittent_baselines.py --npm reports\study2-npm\run-2026-10-15 --grid reports\study2-synthetic-2026-10-15 --nyc311 reports\study3-nyc311\run-2026-10-17 --out <new directory> --workers 6
```

A reader of the CSVs who recomputes tests should parse floats exactly (pandas `float_precision="round_trip"`), as
the results pages say.

## How the archives are built

```powershell
.\.venv\Scripts\python.exe reports\release\build_assets.py --out data\release
```

One archive per run directory, holding that run's `<SHA-256 of the series label>.json` checkpoints and nothing else:
the entries at the archive's root, sorted by name, every timestamp 1980-01-01 00:00:00, Unix permissions 0644, no
directory entry and no comment, every entry deflated at level 6 by zlib 1.3.2 (Python 3.12.14). The same checkpoints
and the same zlib give the same bytes; another zlib may compress differently, and then the archive's SHA-256 differs
while every entry's still matches `run.json`. Before writing, the command requires the run directory to hold exactly
the checkpoints `run.json` names, each at its recorded SHA-256; after writing, it reads every entry back and hashes it
again. The two signals files and `results.parquet` are byte copies, each checked against the hash its run recorded.
The command writes `data\release\.gitignore` (`*`), so that the directory, which the root `.gitignore` does not list,
ignores itself.

## Licences

The code is MIT (`LICENSE`). The project's compilation, the selection of series, the derived fields, the
daily-count files as compiled and the documentation, is under CC BY 4.0; that licence is not asserted over the
source counts as such. **npm:** the counts were obtained from `api.npmjs.org/downloads/range` on the dates the
daily-count provenance gives, and the package names and creation timestamps from `registry.npmjs.org` and
`replicate.npmjs.com`; npm, Inc. states no licence for the counts, and its Open-Source Terms of 2022-03-10 contain no
restriction on their redistribution; names are as the registry served them at acquisition and may since have been
removed; the pull reached npm's rate limit 2,708 times and honoured it. npm is a registered trademark of npm, Inc.
(`docs/research/2026-10-15-npm-redistribution-review.md`; no npm logo is used, and no maintainer data or raw response
body is published.) **NYC 311:** the counts are of service requests in NYC Open Data's dataset `erm2-nwe9`, whose
metadata states no licence and gives the attribution "311". The City's website terms of use, read 2026-10-17, require
lawful use, keep the City's materials and their selection and arrangement as its property with all rights reserved,
imply no endorsement by links and give no warranty; they say nothing specific about datasets, their licence or
attribution, and do not settle whether the property clause reaches datasets served from `data.cityofnewyork.us`. The
Open Data Law the program names was not read. No endorsement by the City of New York is claimed
(`reports/study3-nyc311/panel/source-terms.md`). **GitHub stars:** Study 1's package records the counts as surviving
stars from GitHub's star-history endpoint through 2026-08-31, with creation and eligibility from GH Archive, and
`README.md` puts the aggregate dataset under CC BY 4.0; the package records no reading of GitHub's terms for these
counts. **The forecasts** in the checkpoints and in `results.parquet` come from the frozen models whose weight licences
`study/run_spec.json` records (TimesFM 3's weights carry the TimesFM Non-Commercial License v1.0); no weights are
published, and no reading of what those licences say about forecasts is recorded.

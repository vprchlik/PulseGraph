# PulseGraph: the plan

Last rewritten 2026-10-12 04:10 UTC. This page holds only what is current.

## The two steps

| Step | What | Posted by | Where |
|---|---|---|---|
| 1 | The Study 1 report: the v1 result and audit, the registered design, the result against both references with the mean and typical-repository summaries side by side, the post-hoc decomposition, limitations, what is registered and not run | **2026-10-24** | Zenodo DOI, CC BY 4.0 (see `ideas/2026-10-11-report-link-title-abstract.md`) |
| 2 | The paper: step 1 plus the Study 2 mechanism test (hurdle-wrapped and completed-unwrapped model variants against the count hurdles and the dynamic count baseline) on npm, the registered synthetic grid, and the literature re-check | **2026-10-31** | Zenodo (new version) or arXiv if an endorser is at hand; submitted to TMLR |

The steps run in parallel; neither waits for the other. 2026-11-15 is the fallback date only if the npm
source fails. NYC 311 and Wikipedia go to the spring plan. Anything not run by the paper's date is reported as
not run. The author reads the title, abstract and summary before anything is posted. The report and the
paper are one LaTeX source under `paper/`, posted twice.

## The path, with earliest finish dates

Dates assume each step starts on 2026-10-12 where it can and that the author answers each approval the same
day.

| Step | Depends on | Needs from the author | Earliest finish |
|---|---|---|---|
| Verify and commit the uncommitted work of 2026-09-14 (hashes, the full test suite, two commits) | the root files replaced (`CONTRIBUTING.md`, `docs/HISTORY.md`) and the README paragraph approved | the commits | 2026-10-12 |
| Dated protocol additions for the lapses: holdout not run; npm clock reset once to 2026-10-20; packages-only family E01 to E18 for the October paper; the November round optional | nothing | his sign-off in his own words, the commit | 2026-10-12 |
| Literature re-check for work since 2026-09-13 | nothing | nothing | 2026-10-13 |
| Study 1 report: summary with title and abstract first, then the full LaTeX draft, figures, number sources | nothing | reads `paper/SUMMARY.md` | summary 2026-10-13; full draft 2026-10-17 |
| npm, stage 1: frozen name inventory plan, the candidate-hash walk, the request count stated | both commits above | nothing | 2026-10-13 |
| npm, stage 2: the pull (about eight hours of serial requests) and the frozen achieved panel | stage 1 | approval of the stated request count | 2026-10-15 (deadline 2026-10-20) |
| Synthetic grid, stage 1: GPU smoke at the committed HEAD, gate dry run, runtime estimate | the first commit | nothing | 2026-10-13 |
| Synthetic grid, stage 2: the run (under an hour of GPU), inference over S01 to S06, results section | stage 1 | runtime approval | 2026-10-14 |
| Study 2 external run on the npm panel: gate changes citing the additions, run, inference over E01 to E18 | npm stage 2, synthetic stage 1 | target-access and runtime approval | 2026-10-19 |
| Report review by a different reader, the author's read, the PDF, posting | the draft | his read, the posting | review 2026-10-20; posted 2026-10-23 |
| GitHub release with `results.parquet` (433,172,286 bytes; SHA-256 in `README.md`) | nothing | the upload | before 2026-10-23 |
| Paper extension, review, posting, TMLR submission | npm run, synthetic, literature, report | his read, the posting, the submission | 2026-10-31 |

Cut order if slipping: the November round, then the npm external run (reported as not run; the paper keeps
the synthetic grid and the literature re-check), then the synthetic grid. Never the report.

## Spend

Every spend is approved by the author in his own words before it happens. Nothing here is approved yet.

| Resource | Planned use | Estimate | Dollars | Approval |
|---|---|---|---|---|
| npm registry and download API | name inventory; metadata walk to 10,000 eligible packages; context pull for the candidate pool; later 300 target pulls | about 26,000 serial requests at one per second, about eight hours; stage 1 states the exact figure | 0 | the author's words before stage 2 |
| GPU (RTX 4070 SUPER) | synthetic grid run; npm external run; two smokes | under one hour each by the smoke timings; stage 1 of each states the figure | 0 | the author's budget, as the protocol requires for every component |
| BigQuery | none before the paper (the birth-cohort census is deferred) | 0 | 0 | not asked |
| Zenodo, TMLR | posting and submission | 0 | 0 | the author posts |
| PDF build | pandoc and a TeX distribution on this machine, or Overleaf's free tier | 0 | 0 | the author's choice (below) |

## Open with the author

1. **Posting route.** Zenodo gives a DOI the same day and needs only an account (GitHub login works). Is an
   arXiv endorser for cs.LG or stat.ML at hand? If not, the paper goes to Zenodo as a new version and to TMLR,
   which does not require arXiv.
2. **PDF build.** This machine has no pandoc and no TeX. Either install them (one line each, below) or compile
   the LaTeX on Overleaf's free tier by uploading `paper/`.
3. **The v1 computer.** The write-up's first half leans on the preserved v1 documents; the v1 result artifacts
   exist only on the computer no longer in use. Is it reachable before 2026-10-24? If not, the report says the
   v1 numbers were not recomputed, as the protocol already requires.
4. **Addition 4, the November prospective round.** The case both ways and the addition's text are in
   `ideas/2026-10-11-november-prospective-round.md`. Recommendation: register it for GitHub, add npm only if
   its panel is frozen by 2026-10-24.
5. **The README paragraph** "How this project was built", added 2026-10-12 in the author's voice, is committed
   only with his approval. It states the reasons the study exists (the question, the audit of version 1, the
   registered redesign), who directed the work and how every number traces to the files.
6. **The GitHub release** carrying `results.parquet` (the README has promised its URL since 2026-09-13).
7. **The spring plan** lives in gitignored `notes/plan_spring_2027.md`; a fresh clone cannot read it. The
   deferred register carries its items; moving the plan itself to `docs/ideas/` would complete the record.

Install lines, if the PDF is built here (PowerShell, each on its own):

```powershell
winget install --id JohnMacFarlane.Pandoc -e
```

```powershell
winget install --id MiKTeX.MiKTeX -e
```

## Queued

- A visitor's first screen for `README.md`: the question, the headline result in two sentences, the
  registration hashes, where the numbers come from, the release URL and the DOI.
- A one-paragraph plain statement of the result and a two-page excerpt of the registered analysis code, for
  the author's own use (a draft paragraph is in `ideas/2026-10-11-report-link-title-abstract.md`).
- A monthly audit of every claim on these pages against the files, first about 2026-11-11.
- Archiving the v1 repository on GitHub with one line at the top of its README pointing here, once the report
  is posted (`docs/HISTORY.md`).

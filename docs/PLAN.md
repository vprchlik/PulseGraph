# PulseGraph: the plan

Last rewritten 2026-10-16 05:59 UTC. This page holds only what is current.

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
| Verify and commit the uncommitted work of 2026-09-14 | done 2026-10-12: verified, awaiting the commit | the commit | 2026-10-12 |
| Dated protocol addition for the lapses (items 1 to 3; the November round not taken) | done 2026-10-12: appended, awaiting the commit | the commit, which is the sign-off | 2026-10-12 |
| Literature re-check for work since 2026-09-13 | done 2026-10-12 | the commit | 2026-10-12 |
| Study 1 report: summary, LaTeX source, figures, number sources, checker | done 2026-10-12 (about ten pages; no PDF yet) | reads `paper/SUMMARY.md`; the commit | 2026-10-12 |
| Report review by a different reader | done 2026-10-12: 45 verdicts, one did not hold (the contamination sentence), committed | nothing | done |
| Report revision: the 27 fixes, the six citations, the appendix | done 2026-10-12, awaiting the commit | the commit; his read of `paper/SUMMARY.md` | 2026-10-13 |
| npm, stages 1 and 1b: the candidate-hash walk and three fixes in the code | done 2026-10-13, committed (`26fa5e2`) | nothing | done |
| npm, stage 2: the pull and the frozen achieved panel (209 series; the very-sparse stratum has 9) | done 2026-10-15 01:57 UTC, inside the deadline; awaiting the commit | the commit | 2026-10-15 |
| Synthetic grid: smoke, gate, the 540-series run, inference over S01 to S06 | done 2026-10-15: adverse to the hurdle (five of six reject against it); awaiting the commit | the commit | done |
| External run on npm, stage 1: the packages-only gate and family of 18, the target fetch, the inference command, the run-path fixes | done 2026-10-15, committed (`3fc3411`) | nothing | done |
| External run on npm: targets, run, inference over E01 to E18, recomputation | done 2026-10-15 23:55 UTC; awaiting the commit | the commit | done |
| The npm zero days: source evidence, post-hoc sensitivity, dated addition 6 | done 2026-10-16 (no conclusion changes without the three days); awaiting the commit | the commit | done |
| The author's read of title, abstract and summary; the PDF; posting | the revision | his read, the PDF route, the posting | read 2026-10-16; posted 2026-10-20 to 2026-10-23 |
| GitHub release with `results.parquet` (433,172,286 bytes; SHA-256 in `README.md`) | nothing | the upload | before 2026-10-23 |
| The paper (`paper/paper.tex`): the report extended with both Study 2 results, discussion, limitations | done 2026-10-16; awaiting the commit | the commit | done |
| Paper review by a different reader | done 2026-10-16: 45 verdicts, two do not hold (an overclaim in the abstract; a misdescribed baseline) | the commit | done |
| The standing check and referee's read; the post-hoc dynamic-occurrence analysis | done 2026-10-16; awaiting the commit | the commit | done |
| Paper revision: the review's fixes, the referee's changes, the post-hoc table, the length | the three above | nothing | 2026-10-18 |
| The author's read of both summaries, the PDF, posting (Zenodo version 2), TMLR submission | the revision | his read, the posting, the submission | 2026-10-31 |

The November round was not taken on 2026-10-12 and is out of the path unless the author registers it by a
separate dated addition before 2026-10-28 18:00 UTC.

Cut order if slipping: the npm external run (reported as not run; the paper keeps
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

1. **Posting route, decided 2026-10-13.** Zenodo for the report. The paper goes to Zenodo as version 2 and to
   TMLR; arXiv as well only if an endorser is found (the author is asking this week).
2. **PDF build.** This machine has no pandoc and no TeX. Either install them (one line each, below) or compile
   the LaTeX on Overleaf's free tier by uploading `paper/`.
3. **The v1 computer.** The write-up's first half leans on the preserved v1 documents; the v1 result artifacts
   exist only on the computer no longer in use. Is it reachable before 2026-10-24? If not, the report says the
   v1 numbers were not recomputed, as the protocol already requires.
4. **The post-hoc SVG figures.** The post-hoc directory is 67 MB, of which 18 MB are 18 SVG figures that
   `posthoc-report.md` regenerates from the release asset. Recommendation: commit all of it once, so the
   provenance file lists nothing that is not in the tree.
5. **The `.pytest_cache` folder** denies access on this machine, so the test command in
   `README.md` fails at setup until the folder is deleted from the author's own shell (an elevated one if
   needed); pytest recreates it. Until then the tests use another temporary directory.
6. **The GitHub release** carrying `results.parquet` (the README has promised its URL since 2026-09-13).
8. **Study 3.** `ideas/2026-10-16-study3-regime-test.md`: route A (post the paper by 2026-10-31 and submit) or
   route B (post, register the regime test on a second domain, submit with it about 2026-11-15).
   Recommendation: route B.
7. **The spring plan** is in the tree since 2026-10-13 (`ideas/2026-09-14-spring-2027-plan.md`). Its one open
   decision: the follow-up cohort's creation window, recommended to close 2026-10-31, needs a dated addition
   before then or it slides.

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
- Release assets beside `results.parquet`: the 540 synthetic checkpoints (0.9 GB) and, after the npm run, its
  checkpoints, so a fresh clone can rerun the inference; hashes are in each `run.json`.
- A monthly audit of every claim on these pages against the files, first about 2026-11-11.
- `*.py text eol=lf` in `.gitattributes`, so that the Study 2 gate's source hashes survive a checkout on a
  machine that converts line endings (folded into the npm panel work).
- Archiving the v1 repository on GitHub with one line at the top of its README pointing here, once the report
  is posted (`docs/HISTORY.md`).

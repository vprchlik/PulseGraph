# PulseGraph: the plan

Last rewritten 2026-10-20 10:58 UTC. This page holds only what is current.

## The two steps

| Step | What | Posted by | Where |
|---|---|---|---|
| 1 | The Study 1 report: the v1 result and audit, the registered design, the result against both references with the mean and typical-repository summaries side by side, the post-hoc decomposition, limitations, what is registered and not run | **2026-10-24** | Zenodo DOI, CC BY 4.0 (see `ideas/2026-10-11-report-link-title-abstract.md`) |
| 2 | The paper: step 1 plus the Study 2 mechanism test (hurdle-wrapped and completed-unwrapped model variants against the count hurdles and the dynamic count baseline) on npm, the registered synthetic grid, the literature re-check, and Study 3, the registered regime test on NYC 311 | **2026-10-31** | Zenodo (new version) or arXiv if an endorser is at hand; submitted to TMLR |

The steps run in parallel; neither waits for the other. 2026-11-15 is the fallback date only if the npm
source fails. Wikipedia goes to the spring plan; NYC 311 is Study 3's domain. Anything not run by the paper's date is reported as
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
| The paper (`paper/paper.tex`): the report extended with both Study 2 results, discussion, limitations | done 2026-10-16; awaiting the commit | the commit | done |
| Paper review by a different reader | done 2026-10-16: 45 verdicts, two do not hold (an overclaim in the abstract; a misdescribed baseline) | the commit | done |
| The standing check and referee's read; the post-hoc dynamic-occurrence analysis | done 2026-10-16; awaiting the commit | the commit | done |
| Paper revision: the review's fixes, the referee's changes, the post-hoc table, the length | done 2026-10-16: all three reads applied, 780 checks pass, about seventeen pages by word count against an aim of fourteen; awaiting the commit | the commit; his choice of the next cuts | done |
| The author's read of both summaries, the PDF, posting the paper on Zenodo as version 1 | the revision | his read, the posting | 2026-10-31 |
| Study 3: dated addition 7 with the two declaration files; the variants, component, gate, per-stratum inference and resumable NYC 311 ingestion in code | done 2026-10-16, committed (`3357d77`, `f7a8628`) | nothing | done |
| NYC 311 context pull (one request per calendar day) and the frozen Study 3 panel; deadline 2026-10-27 23:59 UTC | done 2026-10-16 08:04 UTC: 276 of 330 approved attempts, 300 series, every stratum full, verified from the raw captures; committed 2026-10-17 (`0e70759`) | nothing | done |
| Study 3 run on NYC 311: smoke, gate, target pull (90 requests), run, per-stratum inference over R01 to R36, recomputation; the source's terms page read once | done 2026-10-17 04:20 UTC: 106 of 120 approved attempts, 956 s of 3,600; 21 of 36 reject, H3 confirmed for dense series and not for sparse or very sparse; the source's terms recorded; committed (`4b8851e`) | nothing | done |
| The paper extended with Study 3: title and abstract for three studies, the Study 3 part, the discussion for three studies, the post-hoc regime material compressed into the appendix | done 2026-10-17 06:03 UTC: 1,195 checks pass, the report frozen; the body about 23 pages by word count; awaiting the commit | the commit | done |
| Review of the three-study paper by a different reader | done 2026-10-17 07:03 UTC: every number holds; 7 of 45 verdicts do not hold, all sentences; awaiting the commit | the commit | done |
| The step-back read against the field: exemplars, baselines and scores, two referees, venue, the fourth study, the shape | done 2026-10-17 07:23 UTC: credible in record, not in shape; the completion floor; TMLR at twelve pages; no fourth study as proposed; awaiting the commit | the commit | done |
| Post-hoc descriptive benchmark from the saved forecasts: the TSB hurdle and the point methods against the models and the registered baselines per regime; the fourth cell on npm and the grid | done 2026-10-17 08:17 UTC: specification fixed before scoring; the TSB hurdle far behind the models on dense series and ahead for the typical sparse npm series at a week; awaiting the commit | the commit | done |
| Revision: the paper reorganized by question at about twelve pages; the seven failed sentences and the seventeen fixes; the completion floor; the intermittent-demand literature and the benchmark; Brier and RPS beside the quantile score; the ledger; the signature figure | done 2026-10-17 10:05 UTC: nine sections, 7,499 words of body text, five tables, four figures, 1,357 checks; awaiting the commit | the commit | done |
| Review of the reorganized paper by a different reader | done 2026-10-18 03:01 UTC: the record holds in full; 11 of 76 verdicts do not hold, nine of them sentences, none changing a table entry; awaiting the commit | the commit | done |
| The review's fixes: the thesis with its exceptions named, the nine sentences, the broken reference, the table widths, the two-readings paragraph to the appendix, the summary | done 2026-10-18 06:00 UTC: every verdict applied, 1,431 checks, no table entry changed; awaiting the commit | the commit | done |
| Both documents built for the first time: the logs read, overfull lines fixed in the source, the page counts recorded | done 2026-10-18 08:06 UTC: the paper 53 pages (body about 14), the report 13; awaiting the commit | the commit | done |
| Release preparation: the asset manifest with hashes and a verifier, the three checkpoint archives, the daily counts committed, README's first screen, the posting checklist | done 2026-10-18 07:40 UTC; awaiting the commit | the commit | done |
| Both documents prepared for posting: the report's layout line, the paper's data statement, the font package, the TMLR count | done 2026-10-19 04:11 UTC: the report's log clean, the data statement true against the tree, the bitmap font gone; no TMLR template on disk; awaiting the commit | the commit | done |
| The figures brought to a published standard and every page read by eye: Figure 1 as typeset tables, the plotted figures redrawn with every value shown identical, five floats moved; no value changes | done 2026-10-20 10:29 UTC; awaiting the commit | the commit | done |
| The body's prose measured against seven published papers and the author's own writing; a style brief | done 2026-10-20 10:53 UTC (local working notes; nothing committed) | nothing | done |
| The body revised for clarity and voice under a claim ledger: one finding per sentence, the author's choices in the first person, every number, claim, term and citation held | the figure commit | his accept-or-reject, section by section; his confirmation of the first-person passages | 2026-10-22 |
| Review of the revised body by a different reader: every ledger entry before and after | the revision's commit | nothing | 2026-10-23 |
| Posting day: the release URLs and the DOIs written into the tree with the checker changed in the same commit, the NYC 311 data statement completed, the anonymous TMLR build beside the Zenodo build, the final builds | the claims review and the report's DOI reserved | the reserved DOI; his word to post | 2026-10-27 |
| The GitHub release: six assets uploaded in the checklist's order | done 2026-10-20: `assets-2026-10-18`, every byte verified after download; the URLs enter the tree on posting day | nothing | done |
| The author's read of `paper/PAPER-SUMMARY.md`, the PDF, the paper on Zenodo and to TMLR | the fixes | his read, the PDF route (the first build's log is the only check on the table widths), the posting and the submission | 2026-10-31 |

The November round was not taken on 2026-10-12 and is out of the path unless the author registers it by a
separate dated addition before 2026-10-28 18:00 UTC.

Cut order if slipping: the npm external run (reported as not run; the paper keeps
the synthetic grid and the literature re-check), then the synthetic grid. Never the report.

## Spend

Every spend is approved by the author in his own words before it happens. Nothing here is approved yet.

| Resource | Planned use | Estimate | Dollars | Approval |
|---|---|---|---|---|
| npm registry and download API | name inventory; metadata walk to 10,000 eligible packages; context pull for the candidate pool; later 300 target pulls | about 26,000 serial requests at one per second, about eight hours; stage 1 states the exact figure | 0 | the author's words before stage 2 |
| GPU (RTX 4070 SUPER) | synthetic grid run; npm external run; the Study 3 run; three smokes | under one hour each by the smoke timings; the Study 3 run 1,080 s estimated, 3,600 s proposed | 0 | the author's budget, as the protocol requires for every component |
| BigQuery | none before the paper (the birth-cohort census is deferred) | 0 | 0 | not asked |
| NYC Open Data (SODA, anonymous) | the Study 3 context pull, done (276 attempts, 19 minutes); the 90 target days, done (106 attempts in two invocations, 17 minutes: 16 throttled answers at one request a second, none at three); the terms, three scripted requests (a redirect, a refusal, one unsent) and two page reads in a browser | done | 0 | the context pull approved 2026-10-16 (330 attempts, 3 hours); the targets 2026-10-17 (100, then 120 attempts); the terms 2026-10-17 (three scripted requests, then three browser reads) |
| Zenodo, TMLR | posting and submission | 0 | 0 | the author posts |
| PDF build | pandoc 3.12.1 and MiKTeX 25.12, installed 2026-10-18; MiKTeX fetched twenty packages on first use and the font package `cm-super` on 2026-10-19 with the author's word | 0 | 0 | done |

## Open with the author

1. **Posting route, decided 2026-10-13.** Zenodo for the report. The paper goes to Zenodo as version 2 and to
   TMLR; arXiv as well only if an endorser is found (the author is asking this week).
2. **PDF build, done 2026-10-18.** pandoc and MiKTeX are installed, both documents build, and the fonts are settled.
   The TMLR template is on this machine since 2026-10-20: it requires an anonymous submission (non-anonymous
   submissions are rejected without review), so the submitted version carries no name, no author's statement and no
   repository link, and the Zenodo version carries all three; its page count is measured on posting day.
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
8. **Study 3, decided 2026-10-16: route B, now ahead of its calendar.** The regime test was registered as dated
   addition 7 on NYC 311 and ran 2026-10-17, two weeks before the panel deadline. So the paper that posts on Zenodo
   and goes to TMLR by 2026-10-31 carries all three studies; no version without Study 3 is posted. A fourth study as
   proposed on 2026-10-17 is not run: its dense half would repeat a confirmed result, its very sparse half would confirm
   the completion rule rather than the models, and its sparse half is underpowered on NYC 311; the narrow npm
   replication it would have carried is in the deferred register.
9. **The paper's length and the daily counts, decided 2026-10-17.** The body is about 15,650 words with ten tables
   and four figures, about 24 pages before the references by word count. The step-back read's outline is adopted: a
   body of about twelve pages organized by question (the introduction and the thesis; related work; the design as a
   two-by-two of occurrence source by positive-law source with the registration ledger; what the models add over a
   trailing mean; the occurrence substitution by regime with one signature figure; the positive law against count
   laws; discussion; limitations; registration and reproducibility), the full families, the process and every
   secondary table in the appendix, the request ledgers and gate records in the repository only. The line-by-line
   review's fourteen cuts and moves are the first pass. The 209 npm series' daily counts and the NYC 311 target
   signals are settled on 2026-10-18: the daily counts committed, the signals and the checkpoints as release assets.
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

- A one-paragraph plain statement of the result and a two-page excerpt of the registered analysis code, for
  the author's own use (a draft paragraph is in `ideas/2026-10-11-report-link-title-abstract.md`).
- A monthly audit of every claim on these pages against the files, first about 2026-11-11.
- A line-ending attribute for the smoke copies under `study/`: the committed copy of the npm smoke is stored with LF
  while the readiness document of 2026-10-15 hashes the file as written on the run machine; Study 3's copies carry
  the attribute from their first commit.
- `*.py text eol=lf` in `.gitattributes`, so that the Study 2 gate's source hashes survive a checkout on a
  machine that converts line endings (folded into the npm panel work).
- Archiving the v1 repository on GitHub with one line at the top of its README pointing here, once the report
  is posted (`docs/HISTORY.md`).

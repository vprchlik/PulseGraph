# PulseGraph documents: the index

One row per document, newest first. The row says what the document holds or found, not only its title. The
standing documents at the root are listed at the end with their status. Read `docs/STATE.md` first, then
`docs/PLAN.md`.

| Date | Document | What it holds or found |
|---|---|---|
| 2026-09-14 | [`ideas/2026-09-14-spring-2027-plan.md`](ideas/2026-09-14-spring-2027-plan.md) | The plan for work after the October paper, moved into the tree 2026-10-13 with a status note: the rolling monthly prospective benchmark, the registered follow-up cohort (window decision due 2026-10-31), the bounded fine-tune, the journal version, the cut order |
| 2026-10-12 | [`research/2026-10-12-report-review.md`](research/2026-10-12-report-review.md) | The review of the Study 1 report under `paper/`: every number and the direction of every test trace to the saved files; of 45 verdicts 18 hold, 26 hold with a fix and one does not (the contamination limitation, contradicted by the pinned TimesFM 2.5 revision date); the fixes add Study 1's registered follow-up, drop the unbacked burst explanation, label the strata and AutoETS widths, cite the six items of the literature re-check, and cut about two pages to the appendix |
| 2026-10-11 | [`research/2026-10-11-literature-recheck.md`](research/2026-10-11-literature-recheck.md) | The literature re-check for work since 2026-09-13: no published test of a context-only occurrence correction on frozen Chronos-2 or TimesFM forecasts under a proper score was found; six items must be cited (a hurdle on frozen Chronos-2 for monthly spare parts, an event-ranking evaluation of twelve frozen models on sparse daily counts, a simulation with TimesFM-3 on intermittent demand, a per-series-versus-aggregate ranking study, a temporal-holdout familiarity study, a live GitHub-activity benchmark); the three pinned model cards are unchanged |
| 2026-10-12 | [`HISTORY.md`](HISTORY.md) | How version 2 came to be: the question, version 1 and its audit, why a new repository, the design that became the protocol, the timeline |
| 2026-10-11 | [`ideas/2026-10-11-report-link-title-abstract.md`](ideas/2026-10-11-report-link-title-abstract.md) | Where the Study 1 report is posted (a Zenodo DOI the same day; arXiv for the paper only with an endorser), the proposed title and abstract, the posting steps, the README paragraph on how the project was built |
| 2026-10-11 | [`ideas/2026-10-11-november-prospective-round.md`](ideas/2026-10-11-november-prospective-round.md) | The case for and against registering a November 2026 prospective round by a dated calendar addition, with the addition's text; recommendation: register it for GitHub, add npm only if its panel is frozen by 2026-10-24 |
| 2026-10-11 | [`ideas/DEFERRED.md`](ideas/DEFERRED.md) | The deferred register: what is parked, where it was written, since when, and what revives it |
| 2026-10-11 | [`PLAN.md`](PLAN.md) | The two deliverables and their dates, the path with earliest finish dates, every spend, the decisions open with the author |
| 2026-10-11 | [`STATE.md`](STATE.md) | The current state in two screens: committed, uncommitted, what the protocol allows, what lapsed, what the report can say, what the Study 2 code has run on |

## Standing documents at the root

| Document | Status |
|---|---|
| `CONTRIBUTING.md` | The research-integrity, hygiene, writing and commit rules for anyone who changes this repository. From 2026-10-12; it carries the rules under which the protocol was registered and run. |
| `PROTOCOL.md` | The registered protocol: Study 1 at `5f01769`, Study 2 appended at `df55867`. Edited only by dated additions at the end. |
| `RESULTS.md` | The registered Study 1 results and declared descriptive tables; a post-hoc accounting section is appended and uncommitted as of 2026-10-12. |
| `README.md` | The repository's own description: registration, evidence, commands, what a fresh clone holds, and how the project was built. Its first screen is written for the people who ran the study, not for a visitor (queued in `PLAN.md`). |
| `notes/` (gitignored) | Private working notes of September 2026, including the research memo of 2026-09-13 that the protocol cites by SHA-256. Not in the tree. |

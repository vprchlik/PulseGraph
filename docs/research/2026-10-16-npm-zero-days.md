# The npm zero days: what npm's own records say, and a post-hoc sensitivity

Pages read 2026-10-16 between 03:22 and 03:28 UTC. The npm external run of 2026-10-15
(`reports/study2-npm/run-2026-10-15/RESULTS-npm.md`) found, after the scores, that the download API reports
0 for all 209 panel series on 2026-07-12 and 2026-08-14, and 0 for the largest series on 2026-06-25. This
document records two things. First, what npm's status history, issue trackers and changelog say about those
days. Second, the post-hoc sensitivity of the family E01 to E18 to them. The decision is recorded in
`PROTOCOL.md` by the dated addition of 2026-10-16, item 6: the registered analysis of the data as served
stays the confirmatory result. No request was made to `api.npmjs.org`, `registry.npmjs.org` or
`replicate.npmjs.com`. Everything else here is a reading of public pages. Sentences marked (judgment) are
judgments.

## The days, from the record

From `reports/study2-npm/run-2026-10-15/target-pull/daily_summary.csv`, which the post-hoc command rebuilds
from the saved targets on all 90 target days:

| Day | Series reading 0 (of 209) | Panel total | `aggregate-error` | The days either side |
|---|---|---|---|---|
| 2026-06-25 (Thursday) | 92 (dense 34) | 42,139 | 0 | totals 9,537,672 and 7,957,538; `aggregate-error` 9,475,033 and 7,909,626; dense zeros 21 and 28 |
| 2026-07-12 (Sunday) | 209 | 0 | 0 | totals 4,059,870 and 10,123,968 |
| 2026-08-14 (Friday) | 209 | 0 | 0 | totals 7,480,108 and 2,560,140 |

- **The context.** No day of the 275-day context reads 0 for more than 153 of the 209 series, and
  `aggregate-error` never reads below 1,109,682.
- **2026-06-25 without `aggregate-error`.** The other 208 series total 42,139, against 62,639 and 47,912 on
  the days either side.
- **The pull.** The targets were requested once, on 2026-10-15 between 23:14 and 23:26 UTC. That is 95, 62
  and 112 days after the three days.

## What npm's own records say

| Page | Its coverage | What it says about the three days |
|---|---|---|
| npm status page, incident history feeds (`status.npmjs.org/history.rss` and `.atom`) | 25 incidents, 2025-12-05 to 2026-10-14 | None on or near the three days. The nearest are 2026-06-12 (publish failures), 2026-07-23 and 2026-07-24 (publish and install failures), 2026-07-30 (publish failures) and 2026-09-03 (publish failures). No incident mentions download counts. |
| npm status page, component list (`status.npmjs.org/api/v2/components.json`) | the six components the page tracks | The website, package installation, publishing, search, security audit and the replication feed. Download counts are not a component, so the status page does not report on them at all. |
| `npm/registry` on GitHub, the registry documentation repository | issues are turned off; last push 2024-06-02 | Two pull requests were touched after 2026-06-01, neither about download counts. A search for "download" over the repository's whole history finds six pull requests to the documentation, from 2020 to 2024, none about missing days. |
| `npm/registry-issue-archive` | archived; last push 2018-08-22 | Holds nothing from 2026. |
| `npm/feedback` | archived on 2024-05-01; its pinned discussion of that day says npm feedback moved to GitHub Community | Holds nothing from 2026. |
| GitHub Community, npm category, discussion 150808 ("Package download count is broken") | opened 2025-02-06; timeline last modified 2026-03-27 21:08 UTC | Nothing on June to August 2026. It records two earlier episodes in which the download counts read 0 for nearly every package on whole days and were later restored (below). |
| GitHub Community, npm category, listing since 2026-06-01 | the pinned posts and the latest discussions | No discussion about download counts. Its search does not apply a query when not signed in, so the category was listed, not searched. |
| npm documentation, `docs/download-counts.md` in `npm/registry` | undated on the page | Days are UTC, and each day is processed once, soon after UTC midnight. Nothing is said about zero days, outages, corrections or backfills. |
| GitHub Changelog, entries matching "npm" since 2026-06-01 | 22 entries, 2026-06-02 to 2026-10-12 | None about download counts. One npm entry is dated 2026-06-25 (account protection for high-impact accounts); nothing connects it to the counts. |
| GitHub Changelog, entries matching "download" since 2026-06-01 | 34 entries | None about npm download counts. One is about download counts of GitHub release assets. |
| GitHub Blog, posts matching "npm" since 2026-06-01 | 13 posts | None about download counts. |

**In three lines:**

- npm's own records report no outage, gap or backfill of download counts on 2026-06-25, 2026-07-12 or
  2026-08-14. Nothing was found.
- npm's status page does not track download counts, so an outage there would not appear on it.
- npm's community forum records two earlier whole-day gaps that read 0 and were later restored.

### The two earlier episodes in discussion 150808

- **2025.** The discussion was opened on 2025-02-06. It reported that every package read 0 for 2025-01-30 to
  2025-02-05. The accepted answer, dated 2025-02-07 and written by an account the forum marks Maintainer,
  says the team had worked on the issue and the weekly counts were back. An edit to it says all the missing
  past counts had been restored.
- **2026.** On 2026-03-23 and 2026-03-24 users reported 0 for most packages on 2026-03-10, 2026-03-17,
  2026-03-18 and 2026-03-20. On 2026-03-24 they reported that all four days now showed counts. Some replies
  on the page are collapsed.
- **What the frozen context shows on those days.** All four days of March 2026 lie in the frozen context
  pulled on 2026-10-14. They read normally: panel totals of 7,460,954, 7,018,733, 7,051,000 and 5,910,878,
  with 104 to 119 series at 0.

### One page outside npm's records

An unaffiliated scraper's listing on the Apify store shows `react`'s daily series reading 0 on
2026-08-14, marked as a missing day. The same series reads 0 on 2026-09-03, 2026-09-07 and 2026-09-08, outside
the target period. `react` is not in the panel, so the 2026-08-14 zero is not specific to the panel or to
this pull. The page is not npm's record. It carries no date of its own, though it cites a measurement made on
2026-09-17, and it does not say how it tells a missing day from a quiet one.

### What it means (judgment)

- **A gap in the counts.** The days look like gaps in npm's counts, not days without downloads. A day on
  which millions of daily downloads drop to exactly 0 for every package matches the two episodes npm restored
  before. It is also seen outside the panel.
- **Not restored by the pull.** npm has not acknowledged these days anywhere that was read. They were still
  0 when the targets were pulled, 95 and 62 days later, while the March 2026 days had been restored by the
  context pull.
- **2026-06-25 is less clear.** Only `aggregate-error` reads 0. The rest of the panel is lower than on
  either neighbour, and more dense series read 0, but nothing shows it to be a gap.
- **What this changes.** Whether npm will restore the days, and when, is unknown. A later re-request would
  need its own approval, and under addition 6 it would not change the registered result.

## The post-hoc sensitivity

**This is post-hoc.** It was computed on 2026-10-16 from the saved forecasts, after the scores were seen. The
command, its outputs and a one-page reading are in `reports/study2-npm/run-2026-10-15/posthoc/`
(`README.md`; `sensitivity_zero_days.py`, SHA-256 `518deaa4…`; `sensitivity_inference.csv`, `1a849c4f…`).

**How.** Each removed day is dropped, for every series and variant, from the one horizon-30 target block that
holds it. That block is then scored by the registered QScore9 over its remaining 29 days. The horizon-7
blocks hold none of the days. The registered aggregation, Wilcoxon, seeded bootstrap and BH over the
eighteen run unchanged. On the saved scores the same code reproduces `inference/inference.csv` and
`inference/paired_entities.csv` byte for byte.

**What changes:**

- **Without all three days:** none of the eighteen conclusions changes in direction (the larger
  signed-rank sum), sign of the mean or rejection. Twelve reject, ten for the model variant and two against
  the hurdle (E10, E16), as registered.
- **Without the two panel-wide days only:** E06 (`chronos2_raw` against `local_mean_28`, horizon 30) no longer
  rejects. Its BH p is 0.060 and its raw p 0.040, against 0.012 and 0.0066 registered. It still favors the
  model by rank sum. The other seventeen are unchanged, and eleven reject.
- **The horizon-7 rows:** they are identical except for BH p, which moves because BH ranks all eighteen
  together. No horizon-7 rejection changes.
- **Hurdle against completed, horizon 30:** without the three days the mean differences grow: E04 from +90
  to +159, E10 from +129 to +201, E16 from +110 to +183. These means belong to `aggregate-error`.

**What it means (judgment).** The registered answer to the mechanism question does not depend on the zero
days. The hurdle is never favored, and E10 and E16 reject against it in every analysis. Neither does the
answer to the count-hurdle question: all six reject for the foundation model's positive law. The
raw-against-local-mean count is the one that moves: four of six reject as registered, and three of six
without the two panel-wide days. E06 is the borderline row.

## What could not be verified

- **Whether the days are source gaps.** No npm record names them. The judgment above rests on npm's
  earlier episodes and on a third-party page.
- **Whether npm restores them later.** That would need a new request to `api.npmjs.org`, which this
  review did not make.
- **The collapsed replies of discussion 150808.** Its timeline was last modified on 2026-03-27, so none of
  them dates from June to October 2026.
- **The npm category of GitHub Community.** Its full text could not be searched without signing in. The
  web searches run for the three dates found no report from npm.
- **The Apify page's date and method.** The page states neither.
- **The status feeds.** They list incidents from 2025-12-05 onward; whether the page ever had a
  download-counts component was not checked.

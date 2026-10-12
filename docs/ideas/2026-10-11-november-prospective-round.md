# Whether to register a November 2026 prospective round

Written 2026-10-12 03:57 UTC, at the author's request for the case both ways. The decision is the author's;
it is calendar-bound, cannot be in the October paper, and must not slow anything.

## What it is

One forecast origin frozen at 2026-10-28 18:00 UTC, targets 2026-11-01 to 2026-11-30, on the frozen panels
(the 300 GitHub repositories; the npm panel if it is frozen by 2026-10-24), with the Study 2 models, variants
and baselines, forecasts committed and pushed before 2026-11-01, scored from 2026-12-15. It is the first round
of the rolling benchmark in the spring plan and the replacement in kind for the October holdout that lapsed.
The text that would be appended to `PROTOCOL.md` is at the end of this document.

## The case for

- It is the one thing that gives the paper's revision a temporally clean result: every target day is after
  every frozen checkpoint and after the committed forecasts, so no model could have seen them. The October
  paper will say the prospective component was registered and not run; a November round lets the journal
  version say it was then run.
- It is cheap. The GitHub panel exists; the smoke of 2026-09-14 projects about 382 seconds of compute for 300
  series at one origin; the context refresh is 300 star-history requests. The author's cost is one approval,
  one commit and one push on 2026-10-28, and one more when it is scored in December.
- The protocol machinery exists: the freeze writer, the bridge-day logic, the settlement rule, the H-family.
  Only the dates change, by a dated addition.
- If it is not registered now, the next clean window is a month later, and the journal revision has one round
  fewer.

## The case against

- It lands in the author's busiest week: the paper is due 2026-10-31, the report is being posted around
  2026-10-23, and the freeze commit must be pushed before 2026-11-01 00:00 UTC by the author's hand. A late
  push fails the gate and the round is reported as not prospective, which is a worse record than not
  registering.
- Its result cannot be in the October paper and arrives after the TMLR submission; for the October
  deliverables it changes nothing.
- The npm half depends on the npm panel being frozen by 2026-10-24; if the pull slips, the round is GitHub
  alone, which repeats Study 1's entities on one more month.
- It adds a protocol addition to approve during the week the write-up most needs the author's reading.

## Recommendation

Register it, for GitHub, with npm added only if its panel is frozen and committed by 2026-10-24 (the addition
says so). Reasons: the compute and the author's steps are small; the machinery exists; the freeze is a single
step on 2026-10-27 or 2026-10-28; and the downside of a missed push is bounded by the rule that reports it
honestly. If the author would rather keep the last week of October for the paper alone, decline it: the
deferred register keeps the rolling benchmark for December with no loss to the October deliverables.

## If taken, what follows

| Step | Date | Who |
|---|---|---|
| Addition 4 appended and committed with the lapses additions | by 2026-10-14 | the author's sign-off and commit |
| Context refresh for GitHub through the last complete day (and npm if frozen); the freeze plan; the stop for approval | 2026-10-25 to 2026-10-27 | the implementation, then the author's approval |
| Forecasts generated; files and hashes committed and pushed | 2026-10-27 to 2026-10-28, before 18:00 UTC on the 28th | the author's paste |
| Settlement retrieval and scoring | from 2026-12-15 18:00 UTC | the implementation |
| Results into the journal revision | early 2027 | the paper |

## The addition as it would be appended (addition 4 of the dated addition of 2026-10-12)

```
### 4. A November 2026 prospective calendar round

This item registers one further prospective round under the October holdout's rules, with these dates and
no others. Freeze at 2026-10-28 18:00 UTC, using only data through the last fully observed calendar day each
source verifies; preserve the context snapshot and its UTC retrieval time. Target blocks are 2026-11-01 to
2026-11-07 (secondary) and 2026-11-01 to 2026-11-30 (confirmatory), with America/Los_Angeles days for GitHub
and UTC days for npm. Bridge days are handled as registered. The GitHub panel is the unchanged frozen
300-repository manifest. The npm panel is the Study 2 achieved panel only if its manifest is frozen and
committed by 2026-10-24 23:59 UTC; otherwise the round is GitHub alone, declared before the freeze, with the
family H01 to H09 and one BH correction over nine. With npm the family is H01 to H18 with the November domain
labels and one BH correction over eighteen. Commit and push the complete prediction files and their SHA-256
hashes before 2026-11-01 00:00 UTC; a later push fails the prospective gate, and no backdating or
reconstruction is allowed. The settlement retrieval begins 2026-12-15 18:00 UTC with the registered 12-hour
retries for at most 72 hours. Models, baselines, variants, scores, seeds (prospective root 20260919 with the
round label 2026-11 in the derived stream) and reporting rules are those of the October holdout. The round's
results are not part of the October 2026 paper and are reported in a later version or the journal revision,
labeled as a new calendar test on possibly familiar entities. The freeze and the run need the author's
separate runtime approval as registered.
```

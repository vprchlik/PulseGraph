# Whether to register a third study: the occurrence substitution by regime, on a second domain

Written 2026-10-16 06:15 UTC. A decision for the author, written after the three reads of the paper on
2026-10-16 (its review, the standing check and referee's read, and the post-hoc dynamic-occurrence
analysis). Nothing here is registered.

## What the record now shows

The registered Study 2 families pool 209 npm series and 18 grid cells with equal weight, so their tests
speak for the dense regime, where the occurrence substitution loses to the model's own zero mass. The
declared secondary stratum tables say something different for sparse series: on the 100 sparse npm series at
horizon 7 the substitution is lower than its completed control on 81, 60 and 66 of 100 for the three models,
and the reverse holds on the 100 dense ones. The post-hoc dynamic-occurrence wrapper shrinks the loss and
removes four of five rejections against the substitution, and still never beats the model's own zero mass at
BH q = 0.05; on the grid the remaining loss is the positive law, which underpredicts positive days more than
the registered dynamic count's does. Against the registered empirical hurdle, the model's positive law wins
by less than against the shifted Poisson.

These readings are secondary or post-hoc. They are the most interesting thing in the paper, and the paper
cannot claim them as results.

## The study that would make them results

A dated addition registering, before any new target is seen:

- **The hypothesis**, stated by regime: the occurrence substitution lowers QScore9 on series whose context
  zero fraction is at least 0.5 and raises it on series below 0.5; tested per stratum as the confirmatory
  family, not pooled.
- **The variants**: the fixed 28-day occurrence (as registered) and the dynamic occurrence (the discounted
  Beta-Bernoulli), each on the model's completed positive law; the fourth factorial cell, the model's own
  occurrence with the count hurdle's size; the empirical hurdle as the primary count comparator beside the
  shifted Poisson.
- **The domain**: one more, so that the regime finding is not an npm fact. Candidates, from the registered
  slots and the research memo: NYC 311 (non-software, counts of real events, the 2024 cell inventory already
  captured; its September context pull failed on transport and must be retried), PyPI via ClickPy (a second
  package domain, cheap SQL, software again), Wikipedia (known training overlap, labeled). Recommendation:
  NYC 311 first, PyPI as the registered fallback.
- **The rest as registered for Study 2**: the same calendar, models, completion, scores, seeds, gate, smoke,
  checkpoints, inference command, integrity recomputation.

## Cost and calendar

| Step | Days | Needs |
|---|---|---|
| The dated addition, signed by the author | 1 | the author's words |
| NYC 311 inventory freeze and context pull (retry of September's), or the PyPI frame | 3 to 5 | the author's words on the spend (free APIs; call ceilings) |
| The gate, the smoke, the target pull, the run (GPU under an hour), inference, recomputation | 2 | runtime and target-access approvals |
| The paper's version 2 with Study 3, its review, posting, the TMLR submission | 4 | the author's read |

About two weeks of work and three of the author's approvals. The npm and synthetic results are not rerun.

## The two routes

**Route A, post now.** Revise the paper with the three reads' changes, post it on Zenodo by 2026-10-31 as
version 1 with the regime reading labeled secondary and the next study named, and submit to TMLR then. A
reviewer will ask for the regime test; the answer is a revision with Study 3.

**Route B, post and strengthen.** The same revision and Zenodo version 1 by 2026-10-31, the Study 3 addition
registered the same week, the run in early November, and the TMLR submission with Study 3 as version 2 about
2026-11-15. The Study 1 report posts on 2026-10-24 either way.

Recommendation: route B. The difference between the two is whether the paper's best finding is confirmatory
or descriptive when a referee first reads it, and the cost is two weeks that the calendar allows.

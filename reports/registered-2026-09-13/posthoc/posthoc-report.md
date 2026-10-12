# Post-hoc QScore9 accounting

Analysis status: post-hoc; no confirmatory tests.

For each decile, zero=(2/9H) sum[y=0](1-tau)q; positive_over=(2/9H) sum[y>0](1-tau)max(q-y,0); positive_under=(2/9H) sum[y>0]tau max(y-q,0). Summing the three parts and nine deciles recovers QScore9. Ties have zero loss. No tails are inferred.

All 18 models and 48,600 saved windows are included. Each of 17 non-self models is paired against each reference at 7/30/90 days: 102 descriptive cells. All parts use the full horizon denominator; conditional means are not substituted.

Context covariates use each saved full context, then the same three-window repository average as paired scores. Scatter colors show frozen sampling strata; window tables retain context regimes. Signed curves order repositories by total model-minus-reference difference ascending, breaking ties by stable ID. Cumulative sums are divided by 300, so the final point is the mean difference, not a share of positive gains. No repository is removed. Symlog axes retain zeros and signed values; curve y-axes are linear and panel scales differ.

Source: research extensions memo of 2026-09-13, sections 3 and 5, not in the tree.

Regenerate these post-hoc outputs after the declared descriptive document:

```powershell
.\.venv\Scripts\python.exe reports/registered-2026-09-13/posthoc/accounting.py --update-results
```

For a separate reproduction directory, omit --update-results and supply --out data/cache/posthoc-reproduction. No model inference is performed.

| Post-hoc figure | PNG | SVG |
|---|---|---|
| posthoc-cumulative-local_mean_28-h7 | [PNG](posthoc-cumulative-local_mean_28-h7.png) | [SVG](posthoc-cumulative-local_mean_28-h7.svg) |
| posthoc-context-mean-local_mean_28-h7 | [PNG](posthoc-context-mean-local_mean_28-h7.png) | [SVG](posthoc-context-mean-local_mean_28-h7.svg) |
| posthoc-context-zero-fraction-local_mean_28-h7 | [PNG](posthoc-context-zero-fraction-local_mean_28-h7.png) | [SVG](posthoc-context-zero-fraction-local_mean_28-h7.svg) |
| posthoc-cumulative-local_mean_28-h30 | [PNG](posthoc-cumulative-local_mean_28-h30.png) | [SVG](posthoc-cumulative-local_mean_28-h30.svg) |
| posthoc-context-mean-local_mean_28-h30 | [PNG](posthoc-context-mean-local_mean_28-h30.png) | [SVG](posthoc-context-mean-local_mean_28-h30.svg) |
| posthoc-context-zero-fraction-local_mean_28-h30 | [PNG](posthoc-context-zero-fraction-local_mean_28-h30.png) | [SVG](posthoc-context-zero-fraction-local_mean_28-h30.svg) |
| posthoc-cumulative-local_mean_28-h90 | [PNG](posthoc-cumulative-local_mean_28-h90.png) | [SVG](posthoc-cumulative-local_mean_28-h90.svg) |
| posthoc-context-mean-local_mean_28-h90 | [PNG](posthoc-context-mean-local_mean_28-h90.png) | [SVG](posthoc-context-mean-local_mean_28-h90.svg) |
| posthoc-context-zero-fraction-local_mean_28-h90 | [PNG](posthoc-context-zero-fraction-local_mean_28-h90.png) | [SVG](posthoc-context-zero-fraction-local_mean_28-h90.svg) |
| posthoc-cumulative-autoets_weekly-h7 | [PNG](posthoc-cumulative-autoets_weekly-h7.png) | [SVG](posthoc-cumulative-autoets_weekly-h7.svg) |
| posthoc-context-mean-autoets_weekly-h7 | [PNG](posthoc-context-mean-autoets_weekly-h7.png) | [SVG](posthoc-context-mean-autoets_weekly-h7.svg) |
| posthoc-context-zero-fraction-autoets_weekly-h7 | [PNG](posthoc-context-zero-fraction-autoets_weekly-h7.png) | [SVG](posthoc-context-zero-fraction-autoets_weekly-h7.svg) |
| posthoc-cumulative-autoets_weekly-h30 | [PNG](posthoc-cumulative-autoets_weekly-h30.png) | [SVG](posthoc-cumulative-autoets_weekly-h30.svg) |
| posthoc-context-mean-autoets_weekly-h30 | [PNG](posthoc-context-mean-autoets_weekly-h30.png) | [SVG](posthoc-context-mean-autoets_weekly-h30.svg) |
| posthoc-context-zero-fraction-autoets_weekly-h30 | [PNG](posthoc-context-zero-fraction-autoets_weekly-h30.png) | [SVG](posthoc-context-zero-fraction-autoets_weekly-h30.svg) |
| posthoc-cumulative-autoets_weekly-h90 | [PNG](posthoc-cumulative-autoets_weekly-h90.png) | [SVG](posthoc-cumulative-autoets_weekly-h90.svg) |
| posthoc-context-mean-autoets_weekly-h90 | [PNG](posthoc-context-mean-autoets_weekly-h90.png) | [SVG](posthoc-context-mean-autoets_weekly-h90.svg) |
| posthoc-context-zero-fraction-autoets_weekly-h90 | [PNG](posthoc-context-zero-fraction-autoets_weekly-h90.png) | [SVG](posthoc-context-zero-fraction-autoets_weekly-h90.svg) |

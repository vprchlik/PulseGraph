## Descriptive panel diagnostic

Descriptive diagnostic of the frozen achieved panel, not a selection criterion. The numerator sums the first 90 Los Angeles calendar days, beginning on local creation day; the denominator retains gross archive eligibility over the UTC creation date and next 89 UTC days. These are different calendar boundaries, so the ratio is not an exact unstar-retention probability. For boundary sensitivity, the per-repository table also sums survivor bins with nominal dates equal to the archive's 90 date labels; it does not reconstruct UTC-hour totals. The final 90 days are 2026-06-03 through 2026-08-31 inclusive in Los Angeles. Percentiles use linear interpolation across all 100 accepted repositories per stratum. No repository is removed, replaced or reweighted.

| Stratum | Accepted | Ratio median | P10 | P90 | Ratio <0.5 | Last-90 total median | Zero last-90 | Skipped |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 20-99 | 100 | 0.9677 | 0.7232 | 1.0747 | 3 | 0.0 | 52 | 98 |
| 100-999 | 100 | 1.0040 | 0.8854 | 1.0789 | 2 | 4.0 | 22 | 348 |
| 1000+ | 100 | 1.0059 | 0.9144 | 1.0491 | 2 | 39.0 | 1 | 24 |

| Stratum | Skip reason | Count |
|---|---|---:|
| 100-999 | id_resolver_http_403 | 3 |
| 100-999 | id_resolver_http_404 | 345 |
| 1000+ | id_resolver_http_403 | 1 |
| 1000+ | id_resolver_http_404 | 23 |
| 20-99 | id_resolver_http_404 | 98 |

Per-repository values, exact summaries and hashes are in [the diagnostic evidence](reports/registered-2026-09-13/evidence/panel-diagnostic/diagnostic.json).

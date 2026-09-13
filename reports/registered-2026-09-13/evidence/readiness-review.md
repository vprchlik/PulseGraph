# PulseGraph readiness evidence

Evidence is complete and signed below by explicit author instruction. This signature precedes the registered run.

Protocol: 5f01769b6be4c32814befdd7cc3395b6dcc386ed. Protocol SHA-256: dfe2f4adf5c3fdafaa6f2716ae7c19cd4d52577497041c13b763ba06540f65c5.

Implementation and synthetic smoke: ca67dd22ea49377ee1fd074aed57b4b7460c84f1. Source and declarations are committed and clean.

The registered selection seed is 20260913. The full eligible frame was ordered and hashed before the first target history request. The achieved panel is defined by public availability at fetch time and complete retrievable histories. Stable IDs preserve rename mappings. Every candidate encountered before each stratum's stop is logged as accepted or skipped with a reason.

| Day-90 stratum | Eligible frame | Accepted | Skipped |
|---|---:|---:|---:|
| 20-99 | 100,687 | 100 | 98 |
| 100-999 | 46,811 | 100 | 348 |
| 1000+ | 1,052 | 100 | 24 |

| Stratum | Skip reason | Count |
|---|---|---:|
| 100-999 | id_resolver_http_403 | 3 |
| 100-999 | id_resolver_http_404 | 345 |
| 1000+ | id_resolver_http_403 | 1 |
| 1000+ | id_resolver_http_404 | 23 |
| 20-99 | id_resolver_http_404 | 98 |

The manifest contains 300 stable repository IDs. The daily signal contains 289,316 rows, with every local-calendar day from repository creation through 2026-08-31 explicitly observed. No missing bins were imputed. The seeded walk replay, capture response hashes, identity/creation checks and observation-calendar checks passed.

Both completed queries billed 12,510,623,170,560 bytes, approximately $71.1147 before credits at $6.25/TiB. Validation ran first; frame ran under its approved cap after the quota-rejected attempt. Both successful exports and the original rejected job retain provenance. Invoice credits are not inferred. All 872 expected physical daily tables were present and nonempty; this is table coverage, not proof that GH Archive captured every event.

All 18 models passed synthetic smoke with batch size 1 and all three foundation models resident. Peak reserved VRAM: 2,948,595,712 bytes; peak allocated: 2,785,613,824 bytes. These are PyTorch allocator measurements with a 7 GB budget, 1 GB reserved for other CUDA overhead and an 8 GB operational ceiling. Hardware: NVIDIA GeForce RTX 4070 SUPER; driver 610.47; CUDA 12.8; PyTorch 2.11.0+cu128.

| Foundation model | Mean seconds per warm synthetic forecast |
|---|---:|
| chronos2 | 0.0194 |
| timesfm2p5 | 0.1094 |
| timesfm3 | 0.1647 |

The full-run planning estimate remains 2–8 hours. Six warm synthetic forecasts per foundation model support the GPU timing; CPU AutoARIMA search and shared hardware activity dominate uncertainty. No target forecasts informed this estimate.

All 20 validation repositories were captured completely. The original hourly comparisons and DST transition detail are retained. The totals and monthly ratios below use equal exposure: January 1–December 30. December 31 lacks eight archive hours in the fixed 2024 UTC export.

Author-accepted timezone_evidence (verbatim):

All 20 validation repositories were captured completely. Against hourly GH Archive WatchEvents for 2024, binned three ways, America/Los_Angeles with daylight saving has the lowest mean absolute daily difference for 20 of 20 repositories against UTC and 18 of 20 against fixed UTC-8. The five small repositories agree exactly on 98 to 99.7 percent of days under Los Angeles; the large repositories' lower exact agreement reflects their volume, not day boundaries. The four repositories created between 01:00 and 05:00 UTC show first-day stars on the prior nominal date, as Los Angeles binning predicts. Week timestamps are Sunday 00:00 UTC labels, not boundary evidence.

Author-accepted unstar_interpretation (verbatim):

The endpoint reports stars that still exist at retrieval, dated by when they were given: full-history totals equal current star counts for 19 of 20 repositories. Over 2024 the endpoint is below the archive for 17 of 20 repositories, by 5 to 27 percent for the large ones and within a few counts for the small ones, consistent with later unstars and removed accounts. The monthly ratio across 2024 shows no trend with star age. The study target is therefore the surviving-star daily history as retrieved in September 2026, not gross additions. Frame eligibility uses gross archive counts; targets use survivors. No correction is applied.

# Validation totals and monthly ratios

Ratios use January 1-December 30: the export lacks the last eight hours of LA December 31. No boundary counts are imputed. Full 366-day API totals and observed partial archive totals are separately recorded, without a full-year matched ratio.

Largest current stargazers_count in metadata saved with the original validation capture; stable repo ID breaks ties. No new API request or selection by ratio.

Ratio means API divided by archive. All tables use Los Angeles with DST.

| Repository | API, matched 365 days | Archive, matched 365 days | Ratio | API, full 366-day 2024 |
|---|---:|---:|---:|---:|
| react/react | 16,080 | 18,907 | 0.8505 | 16,110 |
| vuejs/vue | 4,280 | 5,877 | 0.7283 | 4,282 |
| microsoft/vscode | 12,951 | 15,232 | 0.8502 | 12,977 |
| nodejs/node | 8,672 | 9,975 | 0.8694 | 8,688 |
| django/django | 7,504 | 8,371 | 0.8964 | 7,516 |
| python/cpython | 7,419 | 8,233 | 0.9011 | 7,431 |
| pallets/flask | 3,726 | 4,162 | 0.8952 | 3,728 |
| expressjs/express | 4,015 | 4,567 | 0.8791 | 4,022 |
| scikit-learn/scikit-learn | 4,195 | 4,573 | 0.9173 | 4,201 |
| psf/requests | 1,943 | 2,276 | 0.8537 | 1,946 |
| pandas-dev/pandas | 3,736 | 4,183 | 0.8931 | 3,739 |
| numpy/numpy | 3,318 | 3,688 | 0.8997 | 3,323 |
| matplotlib/matplotlib | 2,025 | 2,161 | 0.9371 | 2,029 |
| pallets/click | 1,357 | 1,365 | 0.9941 | 1,358 |
| scipy/scipy | 1,305 | 1,364 | 0.9567 | 1,306 |
| cjdrake/pyeda | 37 | 32 | 1.1562 | 37 |
| AppliedMechanics-EAFIT/SolidsPy | 35 | 35 | 1.0000 | 35 |
| polo2ro/imapbox | 21 | 22 | 0.9545 | 21 |
| bwaldvogel/neighbourhood | 10 | 8 | 1.2500 | 10 |
| asciidoc-py/asciidoc-py | 16 | 17 | 0.9412 | 16 |

| Repository | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec 1–30 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| react/react | 0.858 | 0.905 | 0.852 | 0.851 | 0.872 | 0.822 | 0.800 | 0.823 | 0.797 | 0.849 | 0.906 | 0.867 |
| vuejs/vue | 0.804 | 0.841 | 0.773 | 0.645 | 0.669 | 0.718 | 0.658 | 0.728 | 0.604 | 0.728 | 0.850 | 0.775 |
| microsoft/vscode | 0.875 | 0.910 | 0.856 | 0.817 | 0.822 | 0.844 | 0.794 | 0.838 | 0.823 | 0.867 | 0.892 | 0.864 |
| nodejs/node | 0.860 | 0.878 | 0.879 | 0.891 | 0.888 | 0.848 | 0.862 | 0.878 | 0.829 | 0.866 | 0.893 | 0.853 |
| django/django | 0.875 | 0.938 | 0.877 | 0.950 | 0.895 | 0.881 | 0.863 | 0.804 | 0.842 | 0.881 | 0.996 | 0.858 |
| python/cpython | 0.882 | 0.948 | 0.929 | 0.900 | 0.893 | 0.914 | 0.888 | 0.883 | 0.894 | 0.928 | 0.919 | 0.859 |
| pallets/flask | 0.861 | 0.902 | 0.919 | 0.897 | 0.924 | 0.866 | 0.901 | 0.853 | 0.895 | 0.900 | 0.928 | 0.901 |
| expressjs/express | 0.827 | 0.893 | 0.921 | 0.899 | 0.922 | 0.809 | 0.776 | 0.841 | 0.906 | 0.896 | 0.915 | 0.902 |

These are descriptive calendar-matched ratios. Their variation does not by itself identify removal timing or establish an age-invariant removal mechanism. The author's accepted endpoint interpretation is stored separately, verbatim, in readiness.json.


Monthly-ratio figure: comparison/monthly-ratios.png (also saved as SVG).

bin_to_calendar_mapping: Decode the UTC date label of each week timestamp and add the zero-based index in days[7]. Interpret the unchanged nominal label as an America/Los_Angeles calendar date with daylight saving. Do not convert the week timestamp to local time before labeling. The daily signal starts at created_at converted to the Los Angeles date and ends on 2026-08-31. Preserve the frame UTC creation_date and gross day-90 count separately. Build from complete raw weeks, retaining local birth-day counts before UTC creation midnight. Missing endpoint bins are never zero-filled.

later_information_limitation: The target is surviving-star daily history as retrieved in September 2026. Stars subsequently removed, account removals and retrospective revisions can change historical measurements. Context-only forecasts use prefixes of this saved survivor history; they do not reconstruct gross additions or the counts known at historical cutoffs. The leakage tests prevent access to later rows in the saved snapshot, while this measurement limitation remains. Frame eligibility uses gross GH Archive counts and is not recomputed from endpoint survivors.

long_run_approval: The author approved a two-to-eight-hour run budget on 2026-09-13. Foundation models run on the RTX 4070 SUPER GPU, batch size 1, and remain resident until the run ends; baselines run on CPU. The allocator budget is 7 GB and the operational peak ceiling is 8 GB. The real run starts only after the author supplies both signature fields and the registered gate passes. Per-repository checkpoints support resume; any failed window stops the run and is never skipped.

| Required evidence | SHA-256 |
|---|---|
| validation | 146bef3a3dec587428956fa244ad33f39b48649b81940972019cdaf7ae56949f |
| comparison | dd22ac6d10d92cddec4a66637733d8060b778a5ae59640cd7eb2d250c15e0e5d |
| frame_coverage | b1819f8ad6bfa802abcfa09a497fd28a8898f46ac9992ff40b7762ae90a41677 |
| candidate_order | 9e985368c907090d5abd4ac97667b4f123c155ae7f1e5bd40a9347d0ba1bdf33 |
| sampling_log | 2f70b50f34e645d4d87e89026b7f4e7f1d4ff2f5f435992707b3d3b23541ec64 |
| cost_approval | 987021d572e72e73894b0f3125b7d30848c89985be33b00cd77bea966421c02e |
| query_provenance | 6bd9e56b5085c68de2fe34114cd4bcbad3eeb492b0518ae1dca1acf007690a4b |
| smoke | 261c033443a5af5c132f15add34e3748346cefcf8f360b06d269f5eb743a3aea |

Manifest SHA-256: d33ffbd4a189c10a99679dcb3d2812c8bcc089b0b4c66bf927233e04d0e4fa92

Signals SHA-256: 7e448d7254fb180f211cb46522f73aeabd2af259003a95be4edfc1901d4d56e1

The machine-readable readiness.json records every evidence path, exact runtime versions, model revisions, source declarations and hardware. Raw captures remain under ignored data/raw. This package contains the frozen manifest, aggregate signals, query exports, comparison outputs and evidence hashes for the author-performed artifact commit.

approved_by: Victor Prchlik

approved_at: 2026-09-13T07:52:47.491478+00:00

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

Per-repository values, exact summaries and hashes are in [the diagnostic evidence](panel-diagnostic/diagnostic.json).

Signed readiness SHA-256: 2a4ecbf99cd8486620ece6613b836837fe2d8e460d067f85b7e14457d5321021

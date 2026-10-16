# Where the paper stands: a literature sweep and a referee's read

Written 2026-10-16. Searches run between 05:04 and 05:30 UTC on 2026-10-16; the paper read is of
`paper/paper.tex` with its inputs as committed in `c330315`, with `PAPER-SUMMARY.md`, `PROTOCOL.md`,
`RESULTS.md`, the two Study 2 results documents under `reports/` and the six research documents under
`docs/research/` beside it. Part A goes wider and more current than the re-check of 2026-10-12
(`2026-10-11-literature-recheck.md`), which this document does not repeat: items that re-check already
holds are named as "known" and not re-described. Part B reads the paper as a TMLR reviewer would. Nothing
under `paper/` was changed. "Not found" means not found by these searches on this date, not that it does not
exist. Dates are each document's own (the arXiv version date, the record's publication date, the thread's
opening date), never an index date. Sentences marked (judgment) are judgments; the rest reports what the
sources say. Every page cited below was opened on 2026-10-16; a page that only appeared in a listing is
marked "listing only" and carries no claim.

## Part A: the sweep

### Routes

Six routes were used. "arXiv API" is `export.arxiv.org/api/query` sorted by submission date, newest first,
25 to 40 entries per query. "Web" is a general web search engine. "OpenReview" is the public notes-search
API (v1 and v2, the latter also restricted to the TMLR group); forum pages themselves sit behind a
verification screen. "HF" is the Hugging Face model listing by creation date and the model cards it names.
Semantic Scholar's API answered HTTP 429 to every call and Google Scholar returned an empty result with its
"can't perform the operation now" banner; both are failed routes, not absence. A six-angle web sweep ran
beside the hand queries (one angle per claim, with claims 1 and 4 together and 6a to 6c together); it opened
23 pages, extracted 111 statements from them and kept the 24 that three independent readings of the page
confirmed; its page list is folded into the items below.

| Route | Search string or page | Result |
|---|---|---|
| arXiv API | all:"foundation model" AND forecasting AND (intermittent OR "zero-inflated" OR hurdle OR sparse OR count) | 62 entries; none dated on or after 2026-10-06; the newest relevant are the items the re-check holds |
| arXiv API | (github AND stars AND forecast) OR (npm AND downloads) OR (pypi AND downloads AND forecast) OR (wikipedia AND pageviews AND forecasting) OR stargazers | Kazemian et al.; Impermanent; nothing forecasting package downloads |
| arXiv API | (preregistered OR pre-registered OR "registered report" OR preregistration) AND (forecasting OR "time series" OR benchmark) | 232 entries; Ebrahim, Ali and El-Kotory; Zatuchin; no other time-series item |
| arXiv API | (Chronos OR TimesFM OR Moirai OR TiRex OR Toto OR Sundial) AND (intermittent OR zero OR count OR demand OR hurdle) | 119 entries; Sridhar et al.; Cherif; Hari et al.; no zero-mass correction |
| arXiv API | ("per-series" OR "win rate" OR "equal weight") AND forecasting AND (leaderboard OR aggregate OR "foundation model") | Corani et al.; Brini; Islam and Mohammed (both items); Wan et al.; fev-bench |
| arXiv API | ("demand size" OR "conditional size" OR "positive demand" OR "nonzero demand") AND ("foundation model" OR Chronos OR TimesFM OR "zero-shot") | 0 entries |
| arXiv API | wikipedia AND pageviews AND (forecast OR forecasting OR prediction) | Moghadasi and Ghaderi; nothing else since 2024 forecasts pageview series |
| arXiv API | github AND (stars OR stargazers OR popularity) AND (predict OR forecast OR forecasting) AND repositories | Impermanent; Kazemian et al.; one 2024 regression of star counts (listing only) |
| arXiv API | (conformal OR calibration OR "post-processing" OR "post-hoc") AND "foundation model" AND (count OR intermittent OR "zero-inflated" OR sparse) AND forecasting | 8 entries; none corrects a frozen model's output on counts |
| OpenReview v1 | time series foundation model intermittent zero-shot | 28 notes, none after 2024 on the topic, no TMLR venue |
| OpenReview v2, group TMLR | foundation model forecasting sparse counts intermittent | TMLR accepted: TabPFN-v2 for time series (2026-01-26), time-aware PFNs (2026-02-16), ViTime, multimodality; under review: a probabilistic-forecasting survey (2026-08-30) naming count-valued series as open; nothing on sparse counts |
| OpenReview v2 | intermittent demand forecasting zero-shot | a hierarchical Bayesian TSB model (archive upload, 2026-03-25; forum behind verification, not opened); nothing with a foundation model |
| HF | models, task time-series-forecasting, by creation date | Timestral (2026-10-14), t0-gamma (2026-10-12), timeh2o, Kronos; cards opened below |
| Web | "time series foundation model" OR "zero-shot forecasting" intermittent OR sparse OR "zero-inflated" counts October 2026 arXiv | nothing new |
| Web | forecasting "GitHub stars" OR "npm downloads" OR "package downloads" OR "Wikipedia pageviews" foundation model zero-shot 2025 2026 | nothing |
| Web | npm download counts API outage zero downloads all packages 2026 restored backfill | a third-party status mirror; nothing for the three days of 2026 |
| Web | GH Archive missing hours data gap 2025 2026 WatchEvent | nothing specific; a GitHub-wide outage of 2026-08-17 in the press |
| Web | Wikimedia pageviews API data gap missing days 2025 2026 | Phabricator T427171 |
| Web | "Falcon-2.0" time series foundation model | Falcon-2.0, arXiv 2608.13262 |
| Semantic Scholar API | one query | HTTP 429; not consulted |
| Google Scholar | "time series foundation model" intermittent OR "zero-inflated" hurdle zero-shot, 2026 onward | empty with an error banner; failed route |
| Sweep, six angles | web queries per claim, then the pages they named | 23 pages opened, 111 statements extracted, 24 confirmed, 1 refuted (a mis-description of Adler et al.'s metrics, corrected below) |

Pages opened by hand beyond the listings: the arXiv abstract pages of 2511.03877, 2607.19383, 2609.23074,
2610.19608, 2505.05897, 2606.24715, 2610.00589, 2607.05291, 2609.27912, 2608.14106, 2608.13262, 2510.16060,
2608.17299, 2512.20761, 2608.26170, 2601.14031; the HTML full texts of 2609.27867, 2510.16060, 2608.17299 and
2603.08707; the Zenodo record 10.5281/zenodo.22681072; the Timestral and t0-gamma model cards and the
Timestral announcement; the lead-lag-forecasting project page; GitHub community discussion 150808 and GH
Archive issue 312; Phabricator T398150 and T427171. The sweep opened, among others, the GIFT-Eval README and
its commit history, arXiv 2311.18807, 2407.12220, 2605.26161, 2602.12147, 2412.13459, 2511.11698 and the
TimesFM announcement of 2024-02-02.

### Claim 1. Frozen foundation models on sparse daily counts under a proper score, with per-series and mean summaries side by side

| Item | Date | What it did | What it measured | Bears on the claim |
|---|---|---|---|---|
| Adler, Chang, Draxler, Abdi and Smyth, *Beyond Accuracy: Are Time-Series Foundation Models Well-Calibrated?*, [arXiv 2510.16060](https://arxiv.org/abs/2510.16060), ICLR 2026 | v1 2025-10-17; v2 2026-05-27 | Five zero-shot models (Chronos-Bolt, TimesFM, Moirai 2.0, TiRex, YingLong) against ARIMA and N-BEATS on hourly review counts, daily M5 sales binned to 70 department-by-store series "to reduce sparsity", daily NYC crime counts by borough, monthly patents with sparse series removed, and two continuous sets | MASE, two calibration errors and interval width; medians across series in one figure, standard errors of the mean elsewhere; no rank test; no count baselines | Frozen models on daily counts with calibration measured, but sparse series are binned away or removed, and no proper score is reported for the paper's own runs |
| Garza et al., *Impermanent*, [arXiv 2603.08707](https://arxiv.org/html/2603.08707v2), full text | v2 2026-03-10 | Daily (and hourly, weekly, monthly) GH Archive series of the 400 repositories with the most stars: issues, pull requests, pushes, new stargazers; Chronos-2, Moirai 2.0-R-Small, TimesFM 2.5 and TiRex against seven classical methods on a snapshot to 2026-02-12 | CRPS from the nine deciles 0.1 to 0.9, scaled by a zero model, computed per series and aggregated by the median and a mean rank; MASE likewise; no test, no win count, no equal-weight mean | The four foundation models hold the top four mean ranks; TimesFM 2.5 leads with median scaled CRPS 1.055 and MASE 0.609, while on median CRPS Chronos-2 (2.341) and TiRex (2.270) trail AutoETS (2.232). The re-check read only the abstract; the full text shows a proper score on daily GitHub star counts, aggregated by the typical series, on a popularity-selected panel |
| Wen, Zhou, Liu, Zhong and Liang, *LiveHouse-TS*, [arXiv 2608.17299](https://arxiv.org/html/2608.17299) | 2026-08-18 | A live benchmark over 11 domains and 17 datasets, one of them daily Wikimedia pageviews of one article and one GDELT event volume; Moirai-2.0, TimesFM-2.5, Chronos-2, TiRex, TabPFN-TS, Sundial, Chronos-Bolt and Toto-1.0 against seasonal naive, moving average, ARIMA and ETS | RMSE or MAE, MAPE, CRPS from the emitted quantiles, average rank, win rate, Elo, temporal stability | Static rankings invert under the live protocol: Moirai-2.0 and Toto-1.0 rise, Chronos-2 and TimesFM-2.5 fall to the bottom. Not a sparse-count study; the attention series is one article |
| Islam and Mohammed, [arXiv 2609.27867](https://arxiv.org/html/2609.27867v1), full text | 2026-08-20 | Six zero-shot models (Chronos-2, Chronos-Bolt, Chronos T5-Large, TimesFM 2.5, Moirai 2.0, FlowState) among 24 methods on a 1,887-customer monthly panel and on M5 | MASE, RMSSE, WAPE, the mean scaled interval score with coverage; medians and "beats" counts beside means; Diebold-Mariano, Friedman and BH; equal and volume-weighted per-series tables | The production baseline is 2nd of 19 at the total and 23rd of 25 per customer; on M5 1st of 7 at the total and 7th of 7 per item-store. Conformal bands on every method's point errors cover about 74 percent on lumpy and intermittent items at a nominal 95. Known to the paper by abstract; the full text has the side-by-side summaries and the weighting sensitivity |
| Schoess and von Wangenheim; Ebrahim, Ali and El-Kotory; Chin, Cheng and Gunawan | known | as in the re-check | | |
| New frozen models not run: Mistral's Timestral family ([card](https://huggingface.co/mistralai/Timestral-209M), [announcement](https://mistral.ai/news/timestral/)), The Forecasting Company's [t0-gamma](https://huggingface.co/theforecastingcompany/t0-gamma), Ant's Falcon-2.0 ([arXiv 2608.13262](https://arxiv.org/abs/2608.13262)) | 2026-10-15; about 2026-10-12; 2026-08-13 | 21-quantile heads throughout; Timestral is trained mostly on synthetic data and claims the top of GIFT-Eval, TIME and fev-bench over Chronos-2 and TimesFM-3; Falcon-2.0 has a missingness-aware tokenizer | General benchmarks | None is evaluated on sparse or count data in its card or report; none has a count or zero-inflated head |

Standing: **partly known.** (judgment) Frozen models have been scored on daily counts with a proper
score (Impermanent, scaled CRPS on GitHub stars; Adler et al. on binned M5 and crime counts), on sparse
daily counts without a proper score (Schoess and von Wangenheim), and on intermittent data with means and
medians side by side under point scores (Islam and Mohammed). Not found: sparse daily counts under a proper
quantile score with the equal-weight mean and a per-series rank test reported together, on a population
sample. The paper may say that, and should now cite Impermanent's full text rather than its abstract: on
a popularity-selected GitHub panel the typical series favors the foundation models on scaled CRPS, where on
the paper's population sample it favors the local mean; the two designs ask different questions and the
paper should say so in one sentence.

### Claim 2. Pre-registered evaluations of foundation models; a public audit and redesign

| Item | Date | What it did | Bears on the claim |
|---|---|---|---|
| Ebrahim, Ali and El-Kotory, [arXiv 2610.00589](https://arxiv.org/abs/2610.00589); [Zenodo 10.5281/zenodo.22681072](https://zenodo.org/doi/10.5281/zenodo.22681072) | arXiv 2026-09-30; Zenodo record published 2026-09-26, versions 1.1.0 to 1.2.2 all September 2026 | The abstract states "a pre-registered protocol with a 12-step horizon"; the Zenodo record holds `PREREGISTRATION.md` with five hypotheses and `DEVIATIONS.md` splitting departures into before and after results, and states the protocol was "frozen before any forecast was produced and never edited afterwards" | A pre-registered evaluation of a frozen foundation model exists, on simulated data, self-archived with no third-party timestamp before the runs. The paper cites this item for its result and not for its registration; it should |
| Meyer, Kaltenpoth, Albers, Zalipski and Mueller, *TS-Arena*, [arXiv 2512.20761](https://arxiv.org/abs/2512.20761), KDD 2026 | v1 2025-12-23; v3 2026-04-24 | A live platform where forecasts must be submitted before the truth exists, on 186 energy series | Pre-registers forecasts, not an analysis protocol; point scores; no counts |
| Shoeibi and Yousefi, [arXiv 2608.26170](https://arxiv.org/abs/2608.26170) | 2026-07-21 | Pre-registered, final-test-once evaluation of three frozen transcriptomic foundation models with the outcome rule, seeds and splits locked before test data; none reliably beat the expression baseline | The same process outside forecasting, with the same kind of result |
| Zatuchin, [arXiv 2610.19608](https://arxiv.org/abs/2610.19608) | 2026-10-14 | An OSF-registered forecast rule for brand mentions, scored by Brier and log loss | Pre-registration with a public registry in a forecasting setting; no time-series model |
| Hofman et al., *Pre-registration for Predictive Modeling*, [arXiv 2311.18807](https://arxiv.org/abs/2311.18807); Leech et al., *Questionable practices in machine learning*, [arXiv 2407.12220](https://arxiv.org/abs/2407.12220) | 2023-11-30; v2 2024-10-30 | A pre-registration template for predictive modeling; a catalogue of 44 practices that recommends pre-registering experiments | The methodological case; neither is a time-series study |
| GIFT-Eval README update log, [GitHub](https://github.com/SalesforceAIResearch/gift-eval/blob/main/README.md) | 2025-07-24, 2025-08-05, 2025-08-25 | Corrected baseline scores (two methods moved two places), added a self-declared test-data-leakage column, redefined zero-shot | A public correction log for a benchmark, not an audit and redesign of an evaluation |
| Li et al., *TSFMAudit*, [arXiv 2605.26161](https://arxiv.org/abs/2605.26161) | 2026-05-24 | Contamination auditing of frozen foundation models through probe-adaptation dynamics, six models, 187 datasets; "the first work to study pretraining contamination auditing" by its own statement | An audit of models, not of an evaluation's design |

Standing: **partly known.** (judgment) One pre-registered evaluation of a frozen time-series foundation
model exists (Ebrahim, Ali and El-Kotory, simulation, self-archived), and pre-registration of frozen-model
evaluations exists outside forecasting. Not found: a registered protocol fixed before access to real data,
with a public audit and redesign of a first version, for any foundation-model forecasting evaluation. That
process is the paper's distinct contribution and should be stated as such, with Ebrahim et al.'s
registration acknowledged.

### Claim 3. Occurrence or hurdle corrections applied to frozen models' outputs

| Item | Date | What it did | Bears on the claim |
|---|---|---|---|
| Schoess and von Wangenheim; Chin, Cheng and Gunawan | known | Linear occurrence probes on frozen backbones; an occurrence-times-size hurdle on re-centred Chronos-2 judged by service measures | The two routes already in the paper |
| Sridhar, Jain, Mandal and Deshpande, *Event Signature Transfer*, [arXiv 2609.23074](https://arxiv.org/abs/2609.23074) | 2026-09-19 | A training-free transform on the output quantiles of Chronos-2, TimesFM-2.5 and Toto-2.0 that transplants a past event's signature onto a forecast; WQL on twelve real episodes | Post-hoc editing of frozen quantile output, aimed at events, not at zeros or occurrence |
| Dewage, *Hybrid Neural-Classical Correction for Frozen Time Series Foundation Models*, arXiv 2608.08825 (listing only) | 2026-08-09 | Residual correction of frozen TimesFM | Listing only; not opened; no zero handling in the abstract summary |
| Falcon-2.0, [arXiv 2608.13262](https://arxiv.org/abs/2608.13262) | 2026-08-13 | A missingness-aware triple-channel tokenizer inside the model | Model-side treatment of missing values, not a correction of outputs |

Standing: **partly known**, as the re-check found, and nothing newer changes it. (judgment) Not found: a
context-only occurrence probability, fixed-window or dynamic, substituted for a frozen model's own zero mass
with its positive law kept, under a proper score; or any learned head that keeps the model's positive law.
Part B (W2) says what the paper's own version of this test can and cannot show.

### Claim 4. The positive-size question

| Item | Date | What it did | Bears on the claim |
|---|---|---|---|
| Damato, Rubattu, Azzimonti and Corani, *Intermittent time series forecasting: local vs global models*, [arXiv 2601.14031](https://arxiv.org/abs/2601.14031) | v1 2026-01-20; v2 2026-06-10 | Local methods (iETS and others) against global neural and tree models carrying negative-binomial, hurdle-shifted-negative-binomial and Tweedie heads, five datasets, over 40,000 series, scaled quantile loss at five upper levels; TiDE with a Tweedie head recommended; the full text says the comparison with pre-trained models is left for future research | The current count-head state of the art without foundation models; no evidence either way on a frozen model's size law |
| Chin, Cheng and Gunawan; fable.intermittent; EXAONE Demand | known | | |
| arXiv API, demand-size terms with foundation-model terms | 2026-10-16 | 0 entries | |

Standing: **new**, with a qualification from Part B. (judgment) No document tests whether a frozen model's
conditional size law beats count baselines under a proper score. The paper's test does, against a shifted
Poisson; W3 shows the answer changes against the registered empirical hurdle, so the claim the paper can make
is narrower than "beats the count hurdle".

### Claim 5. Forecasting attention and adoption counts since 2024; benchmarks that use them

| Item | Date | What it did | Bears on the claim |
|---|---|---|---|
| Impermanent, full text (claim 1 above) | 2026-03-10 | Daily new stargazers of the 400 most-starred repositories, scaled CRPS by median, foundation models top four | GitHub stars are a live benchmark target with a proper score; popularity-selected |
| Kazemian et al., *Benchmark Datasets for Lead-Lag Forecasting on Social Platforms*, [arXiv 2511.03877](https://arxiv.org/abs/2511.03877); [project page](https://lead-lag-forecasting.github.io/) | v1 2025-11-05; v2 2026-06-07 | About 3 million package repositories from GH Archive (2011 to 2025) and 2.3 million arXiv papers; pushes and stars as the lead channel, forks as the lagged outcome; parametric and non-parametric regression baselines | Stars enter as a predictor of forks, not as a forecast target; granularity and metrics not stated on the pages opened; no foundation model |
| LiveHouse-TS (claim 1) | 2026-08-18 | Daily Wikimedia pageviews of one article; GDELT volume | Pageviews as a live-benchmark attention series |
| Moghadasi and Ghaderi; Schoess and von Wangenheim | known | Weekly pageviews; daily web traffic as a sparse-event panel | |
| TimesFM's corpus ([Google Research, 2024-02-02](https://research.google/blog/a-decoder-only-foundation-model-for-time-series-forecasting/)); Moirai 2.0 ([arXiv 2511.11698](https://arxiv.org/pdf/2511.11698), v3 2026-02-03) | 2024-02-02; 2026-02-03 | TimesFM's corpus is mostly Google Trends and Wikipedia pageviews; Moirai 2.0 trains on GIFT-Eval Pretrain, the GIFT-Eval train split, Chronos mixup and internal telemetry, naming no GitHub or download source | Pageviews are a known training source; no corpus manifest opened names stars or downloads |
| He et al., *Six Million (Suspected) Fake Stars on GitHub*, [arXiv 2412.13459](https://arxiv.org/abs/2412.13459), ICSE 2026 | 2024-12 | About 6 million suspected fake stars across 18,617 repositories; campaigns surge from 2024 | A data-quality caveat for any daily star series: non-organic bursts |
| Swierzy, Pohl, Ohm and Meier, *How Reliable Are FOSS Popularity Metrics?*, [arXiv 2505.05897](https://arxiv.org/abs/2505.05897), ARES 2025 | v2 2026-05-20 | Spoofing effort for downloads, commits and issues; a real npm sybil attack of more than 70,000 spam packages | npm download counts can be manipulated at low to moderate effort; bears on "what a download measures" |
| npm, PyPI or crates download forecasting by any method | | not found by any route | |

Standing: **partly known** for GitHub stars (a live benchmark on the most-starred 400, with foundation
models ahead on the typical series), **known** for Wikipedia pageviews as a benchmark and training source,
and **not found** for package downloads. (judgment) The paper's population sample of GitHub and its hash
sample of npm remain the only such panels found.

### Claim 6. The methodological points

**(a) Equal weights and scale domination.**
[Corani, Damato, Azzimonti and Zambon, *Model selection with proper scoring rules on data sets of time
series: prefer the mean scaled score*, arXiv 2606.24715](https://arxiv.org/abs/2606.24715) (v2 2026-06-24)
compares the mean scaled score with mean rank, median and win rate on intermittent demand including M5,
finds that skewness of short test sets can make the non-mean criteria select misspecified models, and
recommends the mean scaled score. [Brini, arXiv 2607.05291](https://arxiv.org/abs/2607.05291) (2026-07-06)
finds the pooled loss of nine zero-shot models over 50 assets "concentrated in a few outlier assets" and
switches to equal-weight per-asset loss ratios, after which one small model beats the benchmark narrowly.
Impermanent scales by a zero model and takes the median; Damato et al. and fev-bench use scaled quantile
losses. Standing: **known** as a problem and as a remedy. (judgment) Corani et al. cut against the paper's
reliance on medians and win counts as the summary of the typical series and for the registered scale-free
secondary, the mean of the context-scaled score; Part B (W7) draws the consequence.

**(b) Aggregate against typical series.** Islam and Mohammed's full text (claim 1) gives medians, "beats"
counts and a weighting sensitivity beside the means; [Cherif, arXiv 2607.19383](https://arxiv.org/abs/2607.19383)
(2026-07-01) shows zero-shot Chronos winning 78 percent of low-trend series and 44 percent of high-trend ones
under one mean MASE headline, with Holm-corrected Wilcoxon tests; Kim and Song is known; [Wan et al.,
*Forecast Collapse in Time-Series Foundation Models*, arXiv 2608.14106](https://arxiv.org/abs/2608.14106)
(2026-08-14) makes the opposite point, that per-series metrics can hide cross-series failure. Standing:
**known.**

**(c) Temporal holdouts against unseen entities.** Moghadasi and Ghaderi is known; the TIME benchmark
([Qiao et al., arXiv 2602.12147](https://arxiv.org/abs/2602.12147), v4 2026-06-03, ICML 2026) argues that
later windows of known series leak through temporal dependence and builds 50 fresh datasets; TSFMAudit
(claim 2) audits contamination; Moirai 2.0 trains on the GIFT-Eval train split, whose test split is the final
tenth of the same series; GIFT-Eval's leakage column is self-declared; TS-Arena removes truth leakage by
forecast commitment and not entity holdout. Standing: **known.**

**(d) Served zeros and gaps in public count APIs.** Three sources, none a forecasting paper:

| Source | Date | What it records |
|---|---|---|
| GitHub community discussion 150808, [*Package download count is broken*](https://github.com/orgs/community/discussions/150808) | opened 2025-02-06 | The download count read 0 for every package from 2025-01-30 to 2025-02-05; an npm maintainer replied on 2025-02-07 that the weekly count was back and, in a later edit, that "all past date missing download counts have been restored". On 2026-03-23 a reader reported zeros for most packages on 2026-03-10, 03-17, 03-18 and 03-20; by 2026-03-24 all four days showed figures; a 2026-03-27 comment says the counter had been unreliable since the second or third week of March. No cause is given in the thread |
| GH Archive issue 312, [*Data size / number of events have dropped 100x since 2025-10-09*](https://github.com/igrigorik/gharchive.org/issues/312) | opened 2025-10-12, closed 2025-10-15 | Daily event rows fell from 2,769,429 on 2025-10-08 to 18,906 on 2025-10-09 and recovered to 3,465,925 on 2025-10-15; GitHub Support wrote that "recent changes did introduce a cache for event data, which unexpectedly led to some users seeing 'stale' events" and disabled it; no backfill is mentioned. Issue 320 (WatchEvent capture below 20 percent in 2026) is already cited by the paper |
| Wikimedia Phabricator [T398150](https://phabricator.wikimedia.org/T398150) and [T427171](https://phabricator.wikimedia.org/T427171) | 2025-06-30 to 07-01; 2026-05-25 to 06-01 | A data-ingestion issue from 2025-06-28, fixed 06-30 and backfilled ("quite some data to backfill"); the API returned 404 from 2026-05-22, data returned by 05-26. The pageviews API serves 404 or blank for a missing day, not zero |

Standing: **partly known.** (judgment) The npm pattern the paper describes, whole days served as zero for
nearly every package and later restored, is documented twice in a public thread with a maintainer's
confirmation of restoration, which the paper's zero-days note (`2026-10-16-npm-zero-days.md`) can cite
beside npm's forum. Nothing found names 2026-06-25, 2026-07-12 or 2026-08-14. No forecasting paper treats
served zeros in these sources as a data defect; Impermanent excludes the latest cutoff and applies hourly
completeness thresholds to its rollups, which is the nearest handling found.

### What is new and what is known, in five lines

1. The registered, audited, population-sampled design and its traceable record: not found elsewhere for any
   foundation-model forecasting evaluation; one pre-registered simulation study exists and should be named.
2. Frozen models on daily GitHub star counts under a proper score: known for the most-starred 400
   (Impermanent), where the typical series favors the models; new for a population sample, where it does not.
3. The occurrence substitution on a frozen model's output under a proper score: not found; its negative
   pooled answer is known in spirit (Chin et al.); its regime dependence (Part B, W1) is the sharper result.
4. The positive-law contrast under a proper score: new; narrower than stated once the empirical hurdle is
   read (W3).
5. The methodological points: known, with the mean scaled score now recommended in print as the summary of
   choice and the npm served-zero episodes documented with a maintainer's confirmation.

## Part B: the referee's read

The paper was read as a TMLR reviewer would read it, against the venue's two criteria: are the claims
supported by accurate, convincing and clear evidence, and would some individuals in TMLR's audience be
interested in the findings. The review of 2026-10-16 (`2026-10-16-paper-review.md`) is taken as given: its
45 verdicts are not repeated, and the fixes it names are assumed made. Section numbers are the compiled
paper's: 1 to 6 the report, 7 the Study 2 question, 8 the design, 9 the npm panel, 10 the results, 11 the
discussion, 12 the limitations, 13 what is not run, 14 reproducibility; Tables 8 and 9 the two families,
Table 10 the accounting parts, Table 16 the scaled score, Table 17 the strata, Table 19 the cells, Tables 20
and 21 the per-variant means. Figures quoted below that are not in the paper come from the saved per-series
score files by the command at the end; each is a post-hoc reading and adds no test.

### 1. The contribution, as a reviewer would state it

The paper reports a pre-registered evaluation of three frozen zero-shot time-series foundation models on
two public daily count panels, GitHub stars and npm downloads, under a proper nine-decile quantile score,
and finds that the models beat a 28-day local mean on the equal-weight mean while the typical series ties or
favors the reference on GitHub and favors the models at 30 days on npm. It then tests one post-hoc
construction, replacing each model's own zero mass with a 28-day context-only occurrence probability while
keeping the model's completed positive law, and finds that the pooled registered tests reject it on both
panels, that the model's completed positive law beats a shifted-Poisson count hurdle on npm, and that both
answers are carried by the dense series and cells.

### 2. Strengths

- **The registration and its record (Sections 2, 3, 8, 14; Appendices A, E, G).** The protocol was fixed
  before any target was fetched, the first version's audit and the lapses are reported rather than hidden,
  the families were fixed before the data were seen, every number traces to a saved file and a command, and
  an independent recomputation of the scores from the checkpoints found zero disagreements. Part A found no
  foundation-model forecasting evaluation that meets this standard; the one pre-registered study found is a
  simulation.
- **A probability sample of a public domain (Sections 3, 4, 9).** Both panels are hash- or seed-ordered
  samples of a frozen frame with every skip logged, not a popularity list. The one GitHub benchmark found
  takes the 400 most-starred repositories, and its typical-series result differs from this paper's.
- **The mean and the typical series side by side, everywhere (Sections 5, 10; Tables 1, 2, 8, 9).** The
  paper never lets one summary stand for the other, names the one series that carries every npm mean, and
  gives the registered scale-free secondary. The reader can see the disagreement rather than be told about it.
- **An exact accounting of where a loss difference arises (Sections 6, 10; Table 10).** The three-part
  decomposition is exact, reproduces the family means, and is the clearest statement in the paper of what
  the occurrence substitution does: it buys zero-day loss with positive-day underprediction.
- **A second domain where the typical-series result reverses (Section 10, raw contrast).** On npm the raw
  deciles beat the local mean on the rank test in four of six cells where on GitHub the local mean won in
  all nine. This is a finding about frozen models on sparse counts that the earlier evaluations did not have,
  and the paper reports it without inventing a cause.
- **Null and adverse results with the same care (Sections 10, 12, 13).** The substitution's failure, the
  reversal of the positive-law contrast on the grid, the lapsed holdout, the deferred domains, the nine-series
  stratum and the three served zeros are all stated where a reader will find them.

### 3. Weaknesses a reviewer would raise

Each is tied to a section and rated: **blocks** means a reviewer would not recommend acceptance without it;
**revision** means a required change to text or analysis without a new run; **noted** means a limitation to
state, not to fix. None blocks.

**W1. The mechanism conclusion is a pooled statement that the paper's own secondary tables contradict in
the sparse regime (abstract; Section 10, "Read together"; Section 11, first paragraph). Revision, the most
important one.** The registered families pool 209 equally weighted series on an unscaled score, and 18
grid cells with equal weight, so the confirmatory answer speaks for whatever dominates that pool: the dense
stratum on npm and the cells with $z = 0.2$ and $\mu_{+} = 25$ on the grid. In the regime the question was
asked about, the picture is the opposite. On npm the hurdle variant scores lower than its control on 45 to
81 of the 100 sparse series and on 32 to 43 of the 100 dense ones (Table 17); on the context-scaled score
the three horizon-7 contrasts favor the hurdle with every interval below zero (Table 16); on the grid 23 of
the 24 differences in the $z = 0.95$ cells favor the hurdle (Table 19). From the saved per-series scores,
restricted to the 100 sparse series at horizon 7, the hurdle is lower on 81, 60 and 66 of 100 for Chronos-2,
TimesFM 3 and TimesFM 2.5, with raw signed-rank $p$ below 0.002 for all three; at horizon 30 the same
restriction gives 58, 45 and 54 of 100 with $p$ from 0.47 to 0.89. On the grid, by zero probability, the
hurdle beats its control in 4 to 6 of 30 blocks at $z = 0.2$, 12 to 15 at $z = 0.8$ and 21 to 26 at
$z = 0.95$. None of these is a registered test and none changes a registered row; they are readings of
tables the paper already prints. But the sentence a reader takes away, "a context-only occurrence estimate
does not improve a frozen model's own completed zero mass under this score, on either the npm panel or the
grid", is true of the pooled families and false of the sparse regime at short horizons. The abstract's "no
comparison favors the substitution" and the discussion should say that the substitution hurts on dense
series and short-memory cells, helps the typical sparse series at horizon 7, and is null at 30 days, and
that the registered pooling makes the confirmatory tests speak for the dense regime. The dense result also
has a mechanical cause the paper should name: with 28 positive context days the Jeffreys rule gives
$p = 28.5/29$, so the hurdle forces about 1.7 percent zero mass onto every dense series on every day, and
the model's own completed law, which puts less there, must win on them.

**W2. The "positive law" is not a conditional-size forecast, so the mechanism reading the test was built
on cannot be separated from a simpler one (Sections 7, 8 "Completion", 11). Revision.** $G_+$ is the
model's completed marginal law truncated at one. A model that handles zero days by pulling its whole
quantile grid down, which is what nine continuous deciles clipped at zero must do, leaves a truncated law
that is biased low on positive days; adding context zero mass on top of it then double-counts the zeros, and
the accounting in Table 10 (zero-day loss down, underprediction up by more) is exactly what that predicts.
The paper reads the net sign as "the context-only occurrence estimate is worse than the model's own zero
mass"; an equally consistent reading is "the model's truncated law is not its size forecast, so any added
zero mass hurts". The design has three of the four cells of the occurrence-by-size factorial (model-model,
context-model, context-count) and lacks the fourth, the model's own occurrence with the count positive law,
which would separate the two readings and is computable from the saved laws. The premise itself is also
weaker than Section 7 makes it: on the occurrence Brier score (Tables 20 and 21) the models' own zero mass is
about as good as the Jeffreys estimate, and per series at horizon 30 the Jeffreys rule is better on 57 to 62
of 100 dense series and on 65, 49 and 48 of 100 sparse ones. Section 11 should present both readings and
say the test does not choose between them.

**W3. The count-hurdle comparator's positive law is a shifted Poisson, which cannot fit a series with
thousands of downloads a day, so "the model's positive law beats the count hurdle in all six cells" is a win
over a comparator that cannot win on dense series (Sections 10 and 11, "The positive law"). Revision.** By
stratum the foundation-model hurdle beats the count hurdle on 80 to 94 of 100 dense series and on 29 to 63
of 100 sparse ones (Table 17). The registered secondary empirical hurdle shares the same occurrence rule and
is the fair positive-law comparator for dense series. From the saved per-series scores, against it the
foundation-model hurdle is lower on 63 to 72 of the 100 dense series, on 33 to 57 of the 100 sparse series and
on 4 to 6 of the 9 very sparse, and against the completed control the empirical hurdle is not beaten on the
typical series at horizon 7 by Chronos-2 or TimesFM 2.5 (88 and 90 of 209 lower, raw $p$ 0.60 and 0.48; TimesFM
3 117 of 209, $p$ 0.008), while at horizon 30 all three are lower on 120 to 140 of 209. The positive-law
sentence should name the Poisson and add the empirical-hurdle reading, labeled post-hoc; the claim that
survives is that the model's completed law beats an empirical 28-day positive law at 30 days and on dense
series, not in general.

**W4. The registered dynamic count baseline is the best non-oracle forecaster on the grid and the paper
never reads it against the models (Section 11; Table 21). Revision, one paragraph.** On the grid the
dynamic count's mean score at horizon 30 is 1.721 against 1.754 to 1.792 for the three completed models,
1.819 for the count hurdle and 1.648 for the oracle, and from the saved block scores it is lower than each
completed model in 21, 18 and 24 of 30 blocks and lower than the count hurdle and the local mean in 26 of
30. A four-parameter discounted Bayesian hurdle beating three foundation models on the grid, and closing most
of the gap to the oracle, is a result a reviewer will find in the appendix table and ask why the discussion
is silent on it. On npm it loses (the completed models lower on 108 to 146 of 209 series). Both facts
belong in Section 11.

**W5. One external domain, and a claim written for three (abstract; Section 7, last paragraph; Section
11, "What the paper claims"). Revision.** The registration's three external domains were part of the
design's case; two were deferred for calendar reasons and the holdout lapsed, so the occurrence test ran on
npm and the grid. The review of 2026-10-16 already narrows "daily attention and adoption counts" to npm and
the grid; a reviewer will also want the deferrals stated in the abstract or the first paragraph of Section
7, not in Section 13.

**W6. The nine-series stratum leaves the regime closest to GitHub stars untested on npm (Sections 9, 10,
12). Noted.** With W1 this means the external mechanism test is informative for dense and moderately sparse
series and says nothing about series that are zero nine days in ten. The paper says so; it should also say
that this is why the npm and GitHub typical-series results need not agree.

**W7. One series carries every npm mean, and the abstract still leads with means (abstract; Section 10).
Revision of presentation.** The registered weights are what they are, and the paper says so wherever a mean
is printed. A reviewer will ask why the unscaled mean is headlined for npm at all when the registered
scale-free secondary exists. Part A adds a second reason: Corani et al. (2026-06-24) recommend the mean
scaled score over medians, ranks and win rates on intermittent data, because short test sets make the
non-mean criteria pick misspecified models. The paper already computes that score, as the registered
secondary, and on the hurdle contrast it reads in the hurdle's favor at horizon 7 and null at 30 (Table 16).
The abstract should give the npm results by the median, the counts, the rank tests and the scaled mean, with
the unscaled means in the table, and the paper should say why the medians and the scaled means agree where
the unscaled mean differs.

**W8. The two zero days (Section 10, "Three zero days"; Table 18). Noted.** The handling is right: the
registered rule kept them, the addition was made after the fact and says so, the sensitivity is complete and
reproduces, and one borderline row (E06) is named. Part A adds a citable source: the public thread in which
an npm maintainer confirms that whole-day zeros of 2025 were later restored and in which the March 2026
zeros are reported and then filled. A reviewer may ask that the sensitivity's columns sit beside the
registered ones in Table 8 rather than in the appendix, and may ask for one sentence on whether
2026-06-25, the day that touches only the largest series, differs in kind from the two panel-wide days.

**W9. The fixed 28-day occurrence ignores persistence, and the dynamic-occurrence analysis now being
computed answers only part of the question (Sections 8, 10, 12). Revision.** On the grid the hurdle loses
most in the $\rho = 0.8$ cells with $z = 0.2$ and $\mu_{+} = 25$ (0.93 to 0.98 above its control), but it
also loses 0.34 to 0.47 in the same cells at $\rho = 0$, so persistence is not the whole cause; W2's double
counting operates at $\rho = 0$. A wrapper that uses the dynamic count's discounted Beta-Bernoulli occurrence
would test whether a slower, smoother estimate helps, and on npm its occurrence Brier score is slightly below
the Jeffreys rule's (0.1773 against 0.1785 at horizon 30, Table 20), so a small gain is plausible there; but a
discount of 0.98 tracks level drift over weeks, not the one-step dependence the oracle uses
($\pi + \rho^{l}(Z_{\text{last}} - \pi)$). The persistence question needs a two-state Markov occurrence
estimated from the context and propagated from the last observed day, which is also computable from the saved
laws and contexts. Neither wrapper resolves W2; the fourth factorial cell does.

**W10. The synthetic generator draws positive sizes from the count hurdle's own family (Section 8; Section
12). Noted.** The paper says that S02, S04 and S06 are uninformative about the positive law by construction;
a reviewer will accept that and ask why no overdispersed cell was registered. That needs a new run and is
outside this paper.

**W11. Study 1's headline is known in spirit (Sections 1, 5, 7). Noted, with a framing change.** That
frozen models beat simple references on the mean and lose on the typical series, and that TimesFM 3's deciles
are no better than empirical history deciles on intermittent counts, were in print before this paper
(Part A, claims 1 and 6b); and on the most-starred 400 repositories the typical series favors the models on
scaled CRPS (Impermanent's full text). What Study 1 adds is the registered population-sampled design on a
public attention domain, the repository-clustered inference, the audit history, and a typical-series result
that differs from the popularity-selected benchmark's. Section 1 says most of this; the abstract's first
half should say it in one clause, and Section 1 should cite Impermanent's leaderboard rather than its abstract,
so that a reviewer does not read Study 1 as the paper's claim to novelty or miss that the two designs
disagree.

**W12. Three origins and one calendar (Sections 3, 8, 12). Noted.** Inference is conditional on three fixed
origins; the bootstrap is over series and captures between-series variation only; the npm targets are one
summer, and two of its 90 days are the served zeros. The paper says so.

**W13. Three models from two families (Sections 3, 8). Noted.** No Moirai, TiRex, Toto, Sundial or
TabPFN-TS, no demand-specialised model, and three models released since the pins (Falcon-2.0 in August,
t0-gamma and Timestral in October 2026) that claim the top of the general benchmarks; the pins are registered
and cannot change without a new run. A reviewer in TMLR's forecasting audience will ask; the limitations
should name the families not run and the date the pins were fixed.

**W14. The 7-day blocks are prefixes of the 30-day blocks (Sections 8, 12). Noted.** The paper states it.

**W15. Process in the body (Sections 8, 9, 10 "The runs", 14). Revision of presentation.** Commit hashes,
UTC times, budgets, request counts and rate-limit tallies are in the running text of four sections. TMLR
readers want the design and the result; the process belongs in Appendices E to G, with one sentence and a
pointer in the body. This is most of the four pages the review of 2026-10-16 already proposes to move.

### 4. What is missing, and what the saved files can answer

A reviewer would ask for the following. The first seven need no new run.

| Ask | Answerable from saved files | Where |
|---|---|---|
| The hurdle contrasts by stratum with medians, counts and rank tests, labeled post-hoc (W1) | Yes | `inference/series_scores.csv` of the npm run; `secondary_strata.csv` |
| The grid contrasts by zero probability with block counts (W1) | Yes | `inference/series_scores.csv` of the synthetic run |
| The fourth factorial cell: the model's own occurrence with the count positive law (W2) | Yes, from the saved laws per target day | the 209 and 540 checkpoints (release assets) |
| The model's positive law against the empirical hurdle's, by stratum and horizon (W3) | Yes | `series_scores.csv`, `hurdle_empirical_28` rows |
| The dynamic count against the models on both panels, by block and by series (W4) | Yes | `series_scores.csv` of both runs |
| A dynamic and a Markov occurrence wrapper on the saved positive laws (W9) | Yes, from the saved laws and the frozen contexts | checkpoints; the context captures in the raw directory |
| Calibration of the hurdle against its control (PIT) by stratum | Yes | `pit_histograms.csv`, `pit_values.parquet` |
| An overdispersed positive law in the grid (W10) | No; a new run | |
| Other model families; a demand-specialised model (W13) | No; a new run | |
| NYC 311 and Wikipedia; the holdout; the follow-up cohort (W5) | No; registered and not run | |
| The published daily counts and the release assets (review item 30) | Yes; a release, not a run | `reports/study2-npm/` |

### 5. The writing and the venue

- **Length.** About 18 pages before references for a result that fits in 12 to 14. The cuts the review of
  2026-10-16 names (item 43) are the right ones; W15 adds the process paragraphs.
- **Clarity.** The prose is exact and the tables are complete. Three things repeat (the dominant-series
  explanation, the claim paragraph, the secondary readings), already noted. The paper's own vocabulary
  ("completed", "hurdle variant", "control", "count hurdle", "dynamic count") is defined once in Section 8
  and used consistently; a reviewer will manage it. The reader is never told in one place what the four
  forecasters in the two Study 2 contrasts are, in words; a two-by-two diagram of occurrence source by
  positive-law source, with the three cells run and the fourth missing, would replace a page of prose.
- **Over-claiming.** Four places: "no comparison favors the substitution" (the abstract and Section 10,
  contradicted by E01's typical series and by the sparse stratum, W1); "on daily attention and adoption
  counts" (W5); "the model's positive law beats the count hurdle in all six cells" without naming the Poisson
  (W3); and the mechanism sentence of Section 11 stated without its regime (W1, W2).
- **Under-claiming.** Three places. The npm raw contrast, where the typical series favors the frozen models
  at horizon 30 after favoring the reference in every GitHub cell, is a result about a second domain and gets
  one paragraph. The sparse-stratum horizon-7 gain from the substitution is the one place the hypothesis's
  reading finds support, and it is in an appendix table with no sentence on it. And the registration itself,
  with an audited first version and a byte-for-byte traceable record, is the thing TMLR's reproducibility
  readers will value most and the one element Part A found nowhere else; the abstract gives it one clause.

### 6. Verdict

Post after named changes; do not hold for new runs. The named changes are W1 to W5, W7 and W15, together
with the review's fixes already listed: restate the mechanism result as regime-dependent and say that the
registered pooling makes the confirmatory tests speak for the dense regime; present the two readings of the
accounting trade and add the fourth factorial cell as a labeled post-hoc analysis; name the Poisson in the
positive-law claim and add the empirical-hurdle reading; read the dynamic count against the models in the
discussion; narrow the claim to npm and the grid and state the deferrals early; lead the npm abstract with
the typical-series summaries and the scaled mean; move the process to the appendix; cite Impermanent's
leaderboard and Ebrahim et al.'s registration. The dynamic-occurrence post-hoc, when it lands, belongs in
the same appendix beside a Markov-occurrence wrapper, each labeled post-hoc. Is the paper a real small
contribution or a well-executed report of a known thing? As the abstract is written, the latter: "frozen
models win on the mean and lose on the typical series" was known in spirit (Part A, claims 1 and 6b), and "a
context-only hurdle on a frozen model's output does not help" was found in spirit on monthly spare parts
(claim 3). With the framing changed, the former, for three reasons a reviewer can check: no other evaluation
of these models on public attention or adoption counts is registered, population-sampled and traceable to
the byte; the typical-series reversal between GitHub and npm, and between this population sample and the
popularity-selected benchmark, is new evidence about where frozen models earn their keep on sparse counts;
and the regime-dependent answer to the occurrence substitution, harmful on dense series and helpful on sparse
ones at short horizons, is a sharper and more useful finding than the pooled negative, and the paper already
holds every number needed to state it. Some individuals in TMLR's audience, those who evaluate foundation
models on count data and those who care about registered evaluation, would want to read it. The claims are
supported once they are the claims the tables support.

## Regeneration

The figures in Part B that are not in the paper come from the two runs' `inference/series_scores.csv`
files and this command, run from the repository root in PowerShell; it adds no test:

```powershell
@'
import numpy as np, pandas as pd
from scipy import stats
RT = dict(float_precision="round_trip"); FM = ["chronos2", "timesfm3", "timesfm2p5"]
n = pd.read_csv("reports/study2-npm/run-2026-10-15/inference/series_scores.csv", **RT)
s = pd.read_csv("reports/study2-synthetic-2026-10-15/inference/series_scores.csv", **RT)
def paired(df, a, b, h, col="qscore9", by=None):
    x = df[(df.model == a) & (df.horizon == h)].set_index("series_id")[col]
    y = df[(df.model == b) & (df.horizon == h)].set_index("series_id")[col]
    d = (x - y).dropna()
    if by is not None:
        g = df[(df.model == a) & (df.horizon == h)].set_index("series_id")[by]
        return {k: (len(d[i]), int((d[i] < 0).sum()), int((d[i] > 0).sum()), float(d[i].median()),
                    float(stats.wilcoxon(d[i][d[i] != 0]).pvalue)) for k, i in g.groupby(g).groups.items()}
    nz = d[d != 0]
    return (len(d), int((d < 0).sum()), int((d > 0).sum()), float(d.median()), float(stats.wilcoxon(nz).pvalue))
for m in FM:
    for h in (7, 30):
        print("W1", m, h, paired(n, m + "_hurdle", m + "_completed", h, by="stratum"))
        print("W3", m, h, paired(n, m + "_hurdle", "hurdle_empirical_28", h, by="stratum"))
        print("W3 all", m, h, paired(n, m + "_completed", "hurdle_empirical_28", h))
        print("W4 npm", m, h, paired(n, m + "_completed", "dynamic_count", h))
    print("W2 Brier", m, paired(n, m + "_completed", m + "_hurdle", 30, col="occurrence_brier", by="stratum"))
blk = s[s.horizon == 30].groupby(["model", "replicate"]).qscore9.mean().unstack(0)
c = s[s.horizon == 30].copy(); c["z"] = c.cell_id.map(lambda x: {0: 0.2, 1: 0.8, 2: 0.95}[int(x[4:]) // 6])
for m in FM:
    print("W4 grid", m, "dynamic lower in", int((blk["dynamic_count"] < blk[m + "_completed"]).sum()), "of 30")
    for z in (0.2, 0.8, 0.95):
        sub = c[c.z == z]
        d = sub[sub.model == m + "_hurdle"].groupby("replicate").qscore9.mean() - sub[sub.model == m + "_completed"].groupby("replicate").qscore9.mean()
        print("W1 grid", m, "z", z, "hurdle lower in", int((d < 0).sum()), "of 30")
print("W4 grid dynamic vs count hurdle / local mean", int((blk["dynamic_count"] < blk["hurdle_count_28"]).sum()), int((blk["dynamic_count"] < blk["local_mean_28"]).sum()))
'@ | .\.venv\Scripts\python.exe -
```

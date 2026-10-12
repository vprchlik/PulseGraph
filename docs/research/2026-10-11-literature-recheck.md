# Literature re-check: work since 2026-09-13 on zero-occurrence corrections of frozen foundation models

Searches run 2026-10-12 between 09:19 and 09:31 UTC. Scope: work first posted, published or revised on or
after 2026-09-13 that bears on the test Study 2 registered (`PROTOCOL.md`, the Study 2 addition at
`df55867`). The research memo of 2026-09-13 (not in the tree; cited in the protocol by SHA-256) searched
2023 to 2026 and found no published evaluation of that test; this document repeats the search narrowly for
the four weeks since. Every item below was opened on 2026-10-12; "not found" means these searches did not
find it, not that it does not exist. Sentences marked (judgment) are judgments; the rest reports what the
sources say.

## The construction being claimed

Study 2 asks whether replacing a frozen time-series foundation model's own zero mass with a context-only
occurrence probability, while keeping the model's completed positive conditional distribution, improves
QScore9 on sparse daily counts. The pieces: three pinned zero-shot models (`amazon/chronos-2` at
`29ec3766`, `google/timesfm-3.0-pytorch` at `43046b85`, `google/timesfm-2.5-200m-pytorch` at `1d952420`);
a fixed CDF completion of the nine native deciles with the completed-unwrapped forecast as the control; a
28-day Jeffreys occurrence estimate; a fixed count hurdle, an empirical hurdle and a discounted
Beta-Bernoulli/Gamma-Poisson hurdle as comparators; QScore9 as the score; typical-series and mean summaries
reported side by side.

## Searches

All run 2026-10-12. "Web" is a general web search engine; "arXiv API" is `export.arxiv.org/api/query`
sorted by submission date, newest first, 40 to 80 entries per query, which in every case reached back past
2026-09-13; "S2 web" is Semantic Scholar's own search page sorted by publication date.

| Route | Search string | Result |
|---|---|---|
| Web | hurdle zero-inflated post-processing frozen time series foundation model intermittent counts arXiv 2026 | Schoess and von Wangenheim; count-model background only otherwise |
| Web | zero-shot Chronos-2 TimesFM intermittent demand evaluation CRPS zero-inflated 2026 | Chin et al.; ISOMORPH; Spoek et al. |
| Web | forecasting GitHub stars npm downloads time series foundation model Chronos TimesFM | nothing on stars or downloads |
| Web | "time series foundation model" intermittent OR sparse OR zero-inflated counts arXiv September October 2026 | Schoess and von Wangenheim; Chin et al.; fable.intermittent |
| Web | new time series foundation model release 2026 discrete count output head negative binomial zero-shot | nothing with a count head |
| Web | arxiv October 2026 "foundation model" forecasting zero-inflated OR hurdle OR intermittent counts probabilistic evaluation | same items |
| Web | Wikipedia pageviews OR "package downloads" OR "GitHub stars" zero-shot forecasting foundation model 2026 arXiv | nothing on those targets |
| Web | OpenReview 2026 "time series foundation model" intermittent OR sparse OR zero-inflated counts submission | no OpenReview submission page |
| Web | huggingface new time series foundation model model card released September 2026 OR October 2026 zero-shot forecasting | TimesFM 3.0 (2026-08-31); nothing later |
| Web | Toto-2 Datadog sparse time series foundation model arXiv paper release date 2026 | Toto 2.0, arXiv 2605.20119, 2026-05-19; before the window |
| Web | "GitHub" repository stars forecasting 2026 arXiv time series "foundation model" OR "zero-shot" | nothing |
| Web | npm OR PyPI package download counts forecasting time series model 2026 paper | nothing |
| Web | "Chronos-3" OR "Moirai 3" OR "TiRex 2" OR "Sundial 2" OR "TabPFN-TS 3" release September 2026 OR October 2026 | no such release found |
| Web | each cited item by title (Kim and Song; the ICTMOD paper; ZODIAC) | publisher pages opened below |
| arXiv API | all:"foundation model" AND (intermittent OR "zero-inflated" OR hurdle OR sparse) AND forecasting | 9 entries on or after 2026-09-13 |
| arXiv API | ("zero-inflated" OR hurdle OR "intermittent demand") AND forecasting | 6 entries on or after 2026-09-13 |
| arXiv API | (Chronos OR TimesFM) AND (count OR intermittent OR zero) | 7 entries on or after 2026-09-13 |
| arXiv API | all:"time series foundation model" AND (pretrained OR "zero-shot") | 38 entries on or after 2026-09-13; 9 introduce a new model |
| arXiv API | (github AND stars AND forecast) OR (npm AND downloads AND forecast) OR (pypi AND downloads AND forecast) OR (wikipedia AND pageviews AND forecast) | 6 entries, none on or after 2026-09-13 |
| arXiv API | ("GitHub stars" OR "npm downloads" OR "package downloads" OR "repository popularity") AND forecasting | 0 entries |
| S2 web | time series foundation model intermittent zero-inflated | newest entry 2026-09-15; nothing new |
| S2 web | intermittent demand foundation model zero-shot Chronos | Chin et al.; EXAONE Demand; t0; nothing new |
| Semantic Scholar API | three queries | HTTP 429 each time; not consulted |
| Google Scholar | "time series foundation model" intermittent hurdle zero-shot, 2026 onward; "foundation model" "intermittent demand" zero-shot, 2026 onward | "did not match any articles" together with "The system can't perform the operation now"; treated as a failed route, not as absence |
| OpenReview API | time series foundation model intermittent zero-inflated | newest note 2025-11-01; forum pages are behind a verification screen |
| Hugging Face | models, task time-series-forecasting, sorted by creation | relative dates only; one new foundation model (EXAONE Demand) |
| Hugging Face | commit histories of the three pinned model cards | below |
| Crossref API | DOI 10.1109/ICTMOD66732.2025.11371783 | below |

## Items

Dates are the document's own, as its page states them. For arXiv items the date is the version date.
"Changes" is the one-sentence effect on the paper's claim.

| Item | Date | What it did | What it measured | Changes (judgment) |
|---|---|---|---|---|
| Schoess and von Wangenheim, *When, Not How Much: Evaluating Time-Series Foundation Models on Sparse Events*, [arXiv 2609.39386](https://arxiv.org/abs/2609.39386) v1 | 2026-09-30 | Twelve zero-shot models (Chronos-2, Chronos-Bolt, Moirai-1.1, Moirai-2.0, Moirai-MoE, Sundial, TimeMoE, Timer, TimesFM-2.5, TimesFM-3, TiRex, Toto-2.0) on five sparse nonnegative panels: Amazon daily purchases (87.5% zeros), Favorita daily sales (45.7%), M5 daily sales (64.1%), NYC taxi hourly pickups (73.7%), Wikipedia daily page views (65.6%); windows of 364 daily context and 64 target positions; the task is ranking which target positions contain an event. Released point forecasts gain little over a seasonal event-rate reference; linear probes on six frozen backbones beat the backbone's own point forecast in 29 of 30 pairs. No hurdle, zero-inflation or occurrence-probability correction is applied to any forecast; an approximate event probability 1−F̂(0) read from the released quantiles ranks worse than the point forecast in 48 of 50 comparisons. The discussion names output heads forecasting both factors of the occurrence-size decomposition as "a direct next step". | Chance-corrected average precision and AUC skill, averaged with equal window weight; equal-series averaging as a sensitivity check; bootstrap over series. No CRPS, pinball or Brier score; the authors state the metrics assess ranking, not calibration. Table 8 marks Chronos-2, TimesFM-2.5 and TimesFM-3 as having disclosed source overlap with the Wikipedia panel. | Must be cited. It narrows the claim: frozen foundation models have now been evaluated on sparse daily counts, including Wikipedia page views. It does not test the registered construction, uses no proper score, and leaves the occurrence-size head to future work. |
| Chin, Cheng and Gunawan, *Accuracy Is Not Service: A Decision-Aware Benchmark for Intermittent-Demand Forecasting*, [arXiv 2609.13840](https://arxiv.org/abs/2609.13840) v1, accepted to IEEE ICDM 2026 | 2026-09-12 (one day before the window; not in the memo) | Monthly spare-parts demand: an industrial panel of 4,021 materials with about 70% zero cells, the RAF panel (90% zeros), an M5 sample (33%), and a certified synthetic panel. 38 methods including Chronos-Bolt, TimesFM and Moirai; zero-shot Chronos-2 as the baseline for a training-free correction that replaces the instance-normalisation mean and standard deviation by those of the positive observations only. Section IV-F tests a hurdle on Chronos-2: occurrence probability from the full history times a conditional size from the re-centred Chronos output, as an expected value or at a size quantile of 0.7 or 0.9, over six-month lead-time demand. The hurdle trails plain re-centring on service (fill proxy 0.791 against 0.924 at the expected setting). | MASE, signed bias, complete-order fill rate and a per-material fill proxy at a 0.90 target; means across materials. No CRPS, pinball, quantile loss or coverage anywhere. | Must be cited. It narrows the claim: an occurrence-times-size hurdle on frozen Chronos-2 output has been tried, on monthly demand, with occurrence from the full history, judged by point and service measures. The registered construction (daily counts, a proper quantile score, a fixed short-window occurrence estimate, the completed-unwrapped control, matched count hurdles) was not tested there. |
| Ebrahim, Ali and El-Kotory, *Foundation or Formula? A Simulation-Based Comparison of Google's TimesFM-3 and Classical Time-Series Models*, [arXiv 2610.00589](https://arxiv.org/abs/2610.00589) v1 | 2026-09-30 | Nine simulated processes, 7,200 series, horizon 12. Scenario D8 is intermittent demand: occurrence probability 0.3, size 1+Poisson(4), about 70% zeros, 200 replications at lengths 24 to 200. TimesFM-3 against Croston variants, SBA, ADIDA, IMAPA, TSB, iETS, an all-zero forecast and a history benchmark (context mean as point, empirical deciles as the distribution). Only TimesFM-3 appears in the D8 tables. Section 9 pins the same revisions as this project: `43046b8`, `1d95242`, `29ec376`. | MASE, RMSSE, scaled bias, and the scaled pinball loss over nine deciles. On D8, TimesFM-3's pinball (0.288 to 0.325) is about 15% below the classical methods but the history's empirical deciles (0.282 to 0.314) score slightly better at every length; the all-zero forecast has the lowest MASE. The authors conclude TimesFM-3 shows no advantage over simple history-based benchmarks on intermittent demand. | Must be cited. It narrows the claim: on synthetic intermittent counts, TimesFM-3's nine-decile pinball loss is already reported as no better than an empirical-decile history forecast. No occurrence correction is applied. |
| Damato, Zambon, Corani and Azzimonti, *fable.intermittent: benchmarking probabilistic forecasting methods for intermittent time series*, [arXiv 2609.28607](https://arxiv.org/abs/2609.28607) v1 to v3, submitted to the International Journal of Forecasting | 2026-09-23; v3 2026-10-01 | An R package with eleven probabilistic methods for intermittent series, among them a hurdle-shifted Poisson smoother, a parametric selector over hurdle-shifted Poisson and negative binomial laws, and a new Tweedie exponential smoother (TWEES); no foundation model. Four panels: Auto (monthly, 22% zeros), Pasta (daily, 24%), RAF (monthly, 90%), TinyM5 (daily, 51%). | RMSSE and scaled quantile scores at five upper levels (0.5 to 0.995), averaged over series; model confidence sets. | Nothing for the novelty claim. May be cited beside the fixed count hurdles as the current reference implementation of hurdle-count smoothers. |
| Bai and Chu, *When Does Pooling Pay? Credibility and Resolution under Forgetting in Intermittent-Demand Forecasting*, [arXiv 2511.12749](https://arxiv.org/abs/2511.12749) v3 | v3 2026-10-02 (v1 2025-11-16) | A hierarchical empirical-Bayes hurdle model with one exponential forgetting operator on item- and group-level statistics; five public intermittent panels, over 19,000 series; no foundation model. Gains from the shared prior concentrate in the occurrence component. | Relative cost against a per-series Gaussian-process model. | Nothing for the novelty claim. It is close in spirit to the registered discounted Beta-Bernoulli/Gamma-Poisson baseline and may be cited there. |
| LG AI Research, *EXAONE Demand 1.0: A Time Series Foundation Model for Demand Forecasting*, [arXiv 2609.30880](https://arxiv.org/abs/2609.30880) v1; weights at [Hugging Face](https://huggingface.co/LG-AI-Research/EXAONE-Forecast-for-Demand-1.0) | 2026-09-25 | A demand-specific corpus (11.3M series, 73 sources, plus synthetic) and low-rank adapter branches per demand class (smooth, intermittent, erratic, lumpy) on a frozen backbone, routed by eight scale-free statistics including zero share. The released checkpoint is the synthetic-only version, 348M parameters, 21 quantile levels, non-commercial licence. | 22 held-out datasets against 36 other foundation models. | Nothing for the claim. The only new zero-shot foundation model since 2026-09-13 built for frequent zeros; it has a quantile head, no count or zero-inflated head, and was not evaluated on daily attention counts. |
| Wu et al., *Aurora-X: Built for Extreme Time Series Forecasting*, [arXiv 2609.31038](https://arxiv.org/abs/2609.31038) v1 | 2026-09-25 | A billion-parameter general forecaster with an implicit quantile network head. | GIFT-Eval, TIME, fev-bench, TFB, DAG-Bench. | Nothing. No count-aware head; sparse data not mentioned. |
| Meyer et al., *t0: A Time-Series Foundation Model for Forecasting with Context*, [arXiv 2609.24559](https://arxiv.org/abs/2609.24559) v1 | 2026-09-21 | Open-weights models (102M and 256M) with covariates; quantile predictions. | GIFT-Eval; calibration; ERCOT prices. | Nothing. No count-aware head. |
| Zhan, Zhang and He, *Fracast-0*, [arXiv 2609.32209](https://arxiv.org/abs/2609.32209) v1 | 2026-09-26 | An 85K-parameter probabilistic forecaster emitting nine quantiles. | GIFT-Eval MASE and WQL. | Nothing. |
| Zhang et al., *Timer-M1*, [arXiv 2610.11734](https://arxiv.org/abs/2610.11734) v1; Wang et al., *QiYao-I*, [arXiv 2610.06936](https://arxiv.org/abs/2610.06936) v1; Cheng et al., *QiYao-M*, [arXiv 2609.34842](https://arxiv.org/abs/2609.34842) v1; Wang et al., *TimeBraid*, [arXiv 2609.29792](https://arxiv.org/abs/2609.29792) v1 | 2026-10-08; 2026-10-03; 2026-09-28; 2026-09-24 | New multivariate, irregular-sampling, multimodal and language-fused foundation models. Their abstract pages do not state the output head; none mentions counts, zeros or intermittent data. | General benchmarks. | Nothing found; the full texts were not opened. |
| Kislinskii and Hameed, *Are Gradient Boosting Models Suitable for Intermittent Demand Forecasting?*, [arXiv 2609.14718](https://arxiv.org/abs/2609.14718) v1 | 2026-09-13 | Statistical, specialised, boosting and ensemble methods on intermittent panels; no foundation model. | Accuracy improvement up to 10% from ensembles; metrics not named on the abstract page. | Nothing. |
| Nie et al., *Beyond Model Ranking: Regime Diagnosis for Distributional-Statistical Misspecification in Industrial Time-Series Forecasting*, [arXiv 2609.40117](https://arxiv.org/abs/2609.40117) v1 | 2026-09-30 | Thirteen loss objectives over 60,000 series (RetailShiftBench, M5); zero-inflation named as a regime where pooled training misallocates bias; no foundation model. | A regime-wise relative bias vector. | Nothing. |
| Hari et al., *How Good Are Time-Series Foundation Models for Pedestrian Crowd Count Forecasting?*, [arXiv 2609.16415](https://arxiv.org/abs/2609.16415) v1 | 2026-09-14 | TimesFM and Chronos-2 among seven methods on 3-minute event and hourly Melbourne pedestrian counts. | MAE and RMSE per sensor; sparsity not addressed. | Nothing. Counts, but not sparse and not probabilistic. |
| Michael, Symeonides and Trihinas, *Evaluating Accuracy and Probabilistic Reliability of Zero-Shot Time Series Foundation Models*, [arXiv 2609.25788](https://arxiv.org/abs/2609.25788) v1, ADBIS 2026 | 2026-09-22 | Six foundation models on energy, traffic and finance; a trade-off between point accuracy and calibration. | Point and calibration metrics; no counts. | Nothing. |
| Kong, Ling, Liu and Li, *Tracing the Evidence Behind Zero-Shot Time-Series Forecasting: A Source-First Taxonomy and Audit Framework*, [arXiv 2609.21425](https://arxiv.org/abs/2609.21425) v1 | 2026-09-18 | A position paper: "zero-shot" as a claim about evidence access; leaderboards should report evidence boundaries. | None. | Nothing for the claim; may be cited where the paper states its overlap labels. |
| Yu et al., *GRAM: Correcting Frozen Time-Series Foundation Models via Graph-Retrieved Amplitude Memory*, [arXiv 2610.04827](https://arxiv.org/abs/2610.04827) v1 | 2026-10-04 | Per-horizon corrections to frozen foundation models from amplitude-normalised recurring error prototypes; models and datasets not named on the abstract page; no zero handling. | Forecast error. | Nothing; another post-hoc correction of frozen models, aimed at amplitude bias, not occurrence. |
| Ghoroghchian et al., *Foundations without Fundamentals: Zero-Shot Blind Spots in Time Series FMs*, [arXiv 2610.02058](https://arxiv.org/abs/2610.02058) v1 | 2026-10-01 | A unit-test suite of trends, periodic signals and leading indicators; Chronos-2, Moirai and Toto often fail zero-shot. | Forecast error. | Nothing; no sparse data. |
| Spoek et al., *Systematic Evaluation of TabPFN-TS and Chronos-2 for Zero-Shot Heat Load Forecasting in District Heating Networks*, [arXiv 2608.20024](https://arxiv.org/abs/2608.20024) v2 | v2 2026-10-06 (v1 2026-08-20) | Heat load; revised after peer review. | CVRMSE and CRPS. | Nothing; not counts. |
| Zhang et al., *ISOMORPH: A Supply Chain Digital Twin for Simulation, Dataset Generation, and Forecasting Benchmarks*, [arXiv 2605.12768](https://arxiv.org/abs/2605.12768) v3 | v3 2026-09-18 (v1 2026-05-12) | Simulated multi-echelon demand; zero-shot Chronos, Moirai and TimesFM against ARIMA, ETS and PatchTST. | The abstract page names no scoring rule; the sparsity of the simulated demand is not stated there. | Nothing established; the full text was not opened. |

Three items outside the window turned up in the same searches and are not in the memo of 2026-09-13:

| Item | Date | What it did and measured | Changes (judgment) |
|---|---|---|---|
| Islam and Mohammed, *Evaluation Choices Decide the Forecasting Leaderboard: Evidence from a Production Marketplace Panel*, [arXiv 2609.27867](https://arxiv.org/abs/2609.27867) v1 | 2026-08-20 | 24 methods plus a reference, including six 2025-era foundation models, on 1,887 business customers over 67 months; replicated on M5 with five zero-shot foundation models. Moving from aggregate to per-series evaluation drops the production baseline from second of nineteen to twenty-third of twenty-five; on M5 the baseline ranks first at the total level and last per series; interval scoring reorders the field with rank correlation 0.02 on intermittent demand. | Must be cited. The paper's side-by-side mean and typical-series summaries have a direct precedent; the claim that aggregate and per-series rankings can disagree is not new. |
| Moghadasi and Ghaderi, *A Later Test Set Is Not a New Domain: Pretraining Familiarity Survives a Contamination-Free Hold-Out*, [arXiv 2609.10357](https://arxiv.org/abs/2609.10357) v1 | 2026-09-09 | Thirteen forecasters, six pretrained (TimesFM and Chronos families), on seven dataset groups published after the last model's release, Wikipedia pageviews among them. The pretrained advantage tracks whether the domain is in the pretraining corpus; the TimesFM family outranks Chronos by 0.53 ranks on Wikipedia data against 0.09 elsewhere. | Must be cited. It states, with evidence, the distinction the protocol draws between a temporal holdout and unseen-entity generalisation, and it bears on the Wikipedia domain. |
| Garza et al., *Impermanent: A Live Benchmark for Temporal Generalization in Time Series Forecasting*, [arXiv 2603.08707](https://arxiv.org/abs/2603.08707) v2 | 2026-03-10 (v1 2026-03-09) | A live, continuously scored benchmark on GitHub activity: the top 400 repositories by star count; daily-updated series of issues opened, pull requests opened, push events and new stargazers. The abstract names no model and no scoring rule. | Must be cited. It is the one benchmark found that forecasts GitHub stargazer series with foundation-style models in view. Its panel is selected by popularity; Study 1's is a probability sample stratified by day-90 count, and the paper should say so. |

## The cited items, re-checked

| Item | Status on 2026-10-12 |
|---|---|
| Kim and Song, [Journal of Industrial Distribution and Business 17(3), 89 to 97](https://www.accesson.kr/jidb/v.17/3/89/59736), DOI 10.13106/jidb.2026.vol17.no3.89 | Received 2026-06-05, revised 2026-07-05, accepted 2026-07-28, published 2026-07-30. No later version, no erratum. |
| Tsantilis, Giannopoulos, Dasaklis and Patsakis, *Forecasting intermittent demand using Large Language Models: Evidence from a real world industrial dataset*, ICTMOD 2025, [DOI 10.1109/ICTMOD66732.2025.11371783](https://doi.org/10.1109/ICTMOD66732.2025.11371783) | Crossref: published 2025-10-20, deposited 2026-02-11, indexed 2026-09-29; no update-to relation. The September index date is a registry event, not a new version. The IEEE page itself returned no readable content. |
| Yakushin, Beathanabhotla, Garg and Rahman, [ZODIAC](https://www.amazon.science/publications/zodiac-zero-inflated-overshoot-controlled-dual-head-integration-for-asymmetric-cross-domain-forecasting), ICLR 2026 workshop on time series in the age of large models | The publisher page shows only the year 2026; no new version. |
| fev-bench, [arXiv 2509.26468](https://arxiv.org/abs/2509.26468) | v4 of 2026-06-30 remains the latest. |
| Meyer, Kaltenpoth, Zalipski and Müller, [arXiv 2510.13654](https://arxiv.org/abs/2510.13654) | v3 of 2026-02-25 remains the latest. |
| Chronos-2, [arXiv 2510.15821](https://arxiv.org/abs/2510.15821) | v1 of 2025-10-17 is the only version. |

## Model cards and training data

The three pinned revisions are the current heads of their repositories, so the cards read on 2026-10-12
are the cards the protocol pinned.

| Card | Head commit on 2026-10-12 | Training-data text |
|---|---|---|
| [`google/timesfm-2.5-200m-pytorch`](https://huggingface.co/google/timesfm-2.5-200m-pytorch) | `1d95242`, 2025-10-02 (the pinned revision) | GiftEvalPretrain; Wikimedia Pageviews, "cutoff Nov 2023"; Google Trends top queries, "cutoff EoY 2022"; synthetic and augmented data. Unchanged from the memo's reading. |
| [`google/timesfm-3.0-pytorch`](https://huggingface.co/google/timesfm-3.0-pytorch) | `43046b8`, 2026-09-02 (the pinned revision); weights uploaded 2026-08-24; licence set to TimesFM Non-Commercial License v1.0 on 2026-08-27 | GiftEvalPretrain "excluding the datasets that overlap with fev-bench"; Wikipedia Pageviews, "cutoff Nov 2023"; Google Trends top queries, "cutoff EoY 2022"; synthetic and augmented data. Unchanged. The project README adds a September 2026 note that commercial and production use is permitted only through Google Cloud services; the weights' licence is unchanged. |
| [`amazon/chronos-2`](https://huggingface.co/amazon/chronos-2) | `29ec376`, 2026-06-05 (the pinned revision) | A subset of the Chronos datasets excluding test portions that overlap GIFT-Eval; a subset of GIFT-Eval Pretrain; synthetic univariate and multivariate data. No date ranges or cutoffs are stated. Unchanged. |

Two external readings bear on the overlap labels. Schoess and von Wangenheim's Table 8 marks Chronos-2,
TimesFM-2.5 and TimesFM-3 as having disclosed source overlap with Wikipedia page views, because GIFT-Eval
Pretrain contains all 145,063 pages of that source over the same dates. Ebrahim, Ali and El-Kotory pin the
same three revisions as this project, which confirms the revisions are the public heads.

## What the paper may claim

As of 2026-10-12, these searches found no published evaluation in which a context-only occurrence
probability replaces the zero mass of frozen Chronos-2 or TimesFM forecasts while their completed positive
conditional distribution is kept, judged by a proper quantile score against a completed-unwrapped control,
matched count hurdles and a dynamic count baseline on sparse daily counts. The closest precedents are Chin,
Cheng and Gunawan (2026-09-12), who mix a full-history occurrence probability with the conditional size of
re-centred Chronos-2 output on monthly spare-parts demand and judge it by point accuracy and service, finding
it below plain re-centring; Schoess and von Wangenheim (2026-09-30), who evaluate twelve frozen models on
five sparse daily and hourly panels as an event-ranking task without any correction and name the
occurrence-size output head as the next step; Ebrahim, Ali and El-Kotory (2026-09-30), who report
TimesFM-3's nine-decile pinball loss on synthetic intermittent counts as no better than the history's
empirical deciles; and the memo's items (Kim and Song, 2026-07-30; Tsantilis et al., 2025-10-20; ZODIAC,
2026). (judgment) The paper may not claim to be the first evaluation of frozen foundation models on sparse
daily counts, the first hurdle applied to a frozen foundation model's output, or the first to show that
aggregate and per-series rankings disagree (Islam and Mohammed, 2026-08-20; Kim and Song, 2026-07-30). It
may claim the particular registered combination: the completed-unwrapped control, the short-window
occurrence estimate, the matched hurdle comparators, the proper score, the probability sample, and the
side-by-side summaries, on daily attention and adoption counts.

## What the paper must cite

Schoess and von Wangenheim (2026-09-30); Chin, Cheng and Gunawan (2026-09-12, ICDM 2026); Ebrahim, Ali and
El-Kotory (2026-09-30); Islam and Mohammed (2026-08-20); Moghadasi and Ghaderi (2026-09-09); Garza et al.,
Impermanent (2026-03-10); and the memo's items already in the protocol's lineage (Kim and Song; Tsantilis et
al.; ZODIAC; fev-bench; Meyer et al.). (judgment) EXAONE Demand 1.0 belongs in the limitations as a
demand-specialised zero-shot model, released 2026-09-25 with a quantile head and no count head, that was not
evaluated. fable.intermittent and Bai and Chu belong beside the count hurdles and the dynamic count
baseline as current reference points for hurdle-count forecasting without foundation models.

## Where the record is thin

- Semantic Scholar's API refused every call (HTTP 429) and Google Scholar returned an error with its empty
  result, so those two routes contributed nothing; Semantic Scholar's own search page, sorted by date, was
  read instead and surfaced no item the other routes had missed.
- OpenReview forum pages sit behind a verification screen; its search API showed nothing after 2025-11-01.
  Papers under review at ICLR 2027 or TMLR are not visible by any route used here.
- The IEEE Xplore page for the ICTMOD paper returned no content; its dates come from Crossref.
- The Hugging Face model listing gives relative dates only, so a new model released since 2026-09-13 that
  has no arXiv report could have been missed.
- Only abstract pages were opened for Timer-M1, QiYao-I, QiYao-M, TimeBraid, ISOMORPH, GRAM, Kislinskii and
  Hameed, Nie et al., Hari et al., Michael et al., Kong et al., Bai and Chu, Impermanent, Moghadasi and
  Ghaderi, and Islam and Mohammed; their output heads, scoring rules or model lists may be stated in full
  texts not read here.
- Chin, Cheng and Gunawan do not state the mixing formula of their hurdle or the window of the occurrence
  estimate; the ICDM proceedings version may differ from arXiv v1.
- The arXiv API queries return the newest entries first and every query reached back past 2026-09-13, but a
  paper whose abstract uses none of the query terms (for example "dormant", "bursty" or "rare") would not
  appear. No search was made on "bursty" or "rare event" forecasting with foundation models.
- Nothing was found on forecasting npm or PyPI download counts by any method, and nothing on GitHub star
  forecasting with named foundation models beyond Impermanent's abstract, which names none.

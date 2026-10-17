# The paper read from outside: exemplars, the field's standards, two referees, the venue, a fourth study and the shape

Written 2026-10-17 07:17 UTC. Literature searches and page reads ran on 2026-10-17 between 06:49 and 07:16
UTC; the paper read is `paper/paper.tex` with its inputs as committed at `da86452`, beside `paper/PAPER-SUMMARY.md`,
`PROTOCOL.md`, `RESULTS.md`, the three results pages under `reports/` and the earlier reads under
`docs/research/`. This document does not repeat the line-by-line review of the three-study paper, which is a
separate read; it asks what a scientist who reads many papers of this kind would make of it. Nothing under
`paper/` was changed. Sentences marked (judgment) are judgments; the rest reports what the sources or the
saved files say. "Not found" means not found by these searches on this date. Every literature page cited was
opened on 2026-10-17; a source known only from a search listing is marked "listing only" and carries no
claim. Section numbers are the compiled paper's: 1 to 6 the Study 1 report, 7 to 10 Study 2, 11 to 14 Study
3, 15 the discussion, 16 the limitations, 17 what is not run, 18 reproducibility.

Three computations below are new. Each is a post-hoc reading of saved files, adds no test and changes no
registered row; the command that regenerates them is at the end. The most consequential of them is the first.

1. **The completion floor.** The registered completion of nine deciles into a count law
   (`pulsegraph/study2/distributions.py`, `complete`) sets the tail scale to `max(1, q9 - q8)`. When every
   repaired decile is below 0.5, the completed law's probability of a positive day is `0.1 exp(-(0.5 - q9))`,
   which lies between 0.0607 and 0.1 whatever the model forecast. In the NYC 311 very sparse stratum 580,
   544 and 588 of the 600 completed forecasts of Chronos-2, TimesFM 3 and TimesFM 2.5 sit on that floor
   (median occurrence 0.0607 to 0.0609), against a median occurrence of 0.0172 for the dynamic hurdle; in the
   sparse stratum 150, 62 and 230 of 600 do; in the dense stratum 2, 0 and 0. So on series that are zero
   nine days in ten, the "model's own zero mass" of the T1 contrast is set by the completion rule, not by the
   model.
2. **The contrast against the context zero fraction.** Read series by series against each series' context
   zero fraction (from the two panel manifests), the occurrence substitution is lower than its completed
   control under QScore9 for 65 to 71 percent of npm series-model pairs with zero fractions from 0.5 to 0.9
   at horizon 7, and for at most half of the NYC 311 pairs in any bin (between 0.5 and 0.9 the untied NYC
   311 pairs split 40 to 38 and 108 to 70 in its favor); above 0.97 on NYC 311, 183 of 186 pairs tie exactly
   under QScore9 while the occurrence Brier score favors the substitution on 148.
3. **Resampled power.** Resampling the 100 NYC 311 per-series differences of each stratum, a per-stratum
   Brier or discrete CRPS test at a Bonferroni level of 0.05/12 would reject with probability 0.35 to 1.00
   on dense series and 0.63 to 1.00 on very sparse ones at 100 series, if the Study 3 effects recur, and
   with probability at most 0.05 on four of the six sparse rows even at 300 series. The same resampling of
   the 100 sparse npm series gives 0.63 to 1.00 at horizon 7 for the fixed hurdle under QScore9 and 0.81 to
   1.00 under the Brier score, if the Study 2 effects recur.

## In one page

(judgment) Read as a scientist in forecasting would read it, the paper is credible in its record and not yet
comparable in its shape. The registration, the population sampling, the independent recomputation and the
mean and the typical series side by side are things none of the ten exemplars below has together, and they
are why a careful reader will trust its numbers. What a reader in the field will not find is the field: the
intermittent-demand literature is absent from the bibliography (no Croston, Syntetos and Boylan, Teunter,
Syntetos and Babai, Snyder, Ord and Beaumont, Kolassa, Svetunkov and Boylan, or the M5 uncertainty papers),
the registered baselines are classical count models under names a reader in the field will not recognise,
and the primary score is one that the nearest literature drops at low quantile levels because every forecast
is zero there. The body, about 15,800 words in ten tables and four figures, reads as a chronicle of three
studies in the order they were run: its first figure is Study 1's eighteen comparisons, its reading guide
maps sections to studies, and the process (commit hashes, request counts, throttled answers, run seconds)
sits in the running text. Underneath it is one argument, and a sharper result than the draft states: the
frozen models' value on sparse daily counts is in the size of the positive days; their own probability of a
zero day is at least as good as a context-only estimate wherever their nine quantiles can express one; and
where they cannot, on series that are zero nine days in ten, both the quantile score and the models' "own"
occurrence are set by the interface, so the very sparse question the paper calls open is not a question the
registered construction can ask.

The five changes that matter most, in order:

1. **Restate the very sparse result as an interface limit.** Replace "two readings with equal weight" in
   Section 15 with the completion floor: on most very sparse series the completed law's occurrence is
   0.0607 to 0.1 by construction, so the QScore9 ties and the Brier separation both compare a context
   estimate with the completion rule, not with the model.
2. **Bring in the field.** Cite and position Croston, SBA, TSB, ADIDA, iETS, the static and dynamic count
   models of Snyder, Ord and Beaumont, Kolassa on count scores, the M5 uncertainty track and its
   commentaries; name the registered baselines by their place in that literature (the count hurdle is a
   hurdle shifted Poisson, the dynamic count is a discounted Bayesian analogue of TSB); say why Croston and
   TSB were excluded by name and what that costs.
3. **Put the count scores beside the registered one in the body.** The occurrence Brier score and the
   discrete CRPS are registered secondaries with saved numbers; for every contrast in the body, show them
   next to QScore9, labelled as registered, and say in one paragraph why a quantile score cannot see an
   occurrence difference below one decile.
4. **Reorganise by question, not by study, at twelve pages.** One thesis, one design section with a
   two-by-two of forecasters, three result sections (what the models add; the occurrence substitution by
   regime; the positive law), one signature figure, the process and the full families in the appendix.
5. **Present the dated additions as one ledger table** with a column that says whether each was decided
   before any target of the study it touches was seen; state once, in plain words, that the lapses of
   September came from four weeks without work, and flag item 6 as the one decision made after scores.

Venue: TMLR, as planned, with the body at twelve pages so the review runs on the standard track; the
International Journal of Forecasting only for a later paper that registers the intermittent-demand baselines
and count scores. The decision is the author's.

Study 4: do not run it as proposed. It would confirm the dense result a second time, would "confirm" on
very sparse series a property of the completion rule, and would most likely leave the NYC 311 sparse
stratum where Study 3 left it, since the effect there is near zero on four of six rows. Its one part with
substance is npm's sparse stratum at a week, where a September replication would very likely confirm the
paper's best secondary finding; keep that narrow family in reserve for the review. Submit by 2026-10-31
with the secondary evidence labelled and the interface limit stated. The study a referee would ask for is a
different one, and it belongs to the next paper (Part E).

## Part A: the exemplars

### Routes

Five search angles ran in parallel (exemplars; intermittent-demand methods; scores for count forecasts;
foundation models on intermittent data; venues), each with its own queries, followed by a fetch of the pages
they named and three independent readings of each extracted statement; hand queries and page reads were
added where a count or a venue was missing. Every query below ran on 2026-10-17.

| Angle | Queries (2026-10-17) |
|---|---|
| Exemplars | M5 uncertainty competition results findings conclusions International Journal of Forecasting 2022 Makridakis Spiliotis Assimakopoulos weighted scaled pinball loss; M5 uncertainty competition critique weighted scaled pinball loss intermittent series zero quantiles; "M5 uncertainty competition: Results, findings and conclusions" pdf benchmarks naive seasonal naive ETS ARIMA kernel quantile WSPL; M5 Competitors Guide uncertainty benchmarks Naive sNaive SES ETS ARIMA Kernel Croston WSPL github Mcompetitions; Kolassa commentary M5 forecasting competition International Journal of Forecasting 2022 uncertainty evaluation pinball intermittent; "Product sales probabilistic forecasting: An empirical evaluation using the M5 competition data" Spiliotis; "Combining probabilistic forecasts of intermittent demand" Wang Kang Petropoulos European Journal of Operational Research; M5 uncertainty competition benchmarks Naive sNaive SES ETS ARIMA Kernel quantiles competitors guide; Transactions on Machine Learning Research time series foundation models zero-shot evaluation benchmark 2025 OpenReview TMLR; "Equal Accuracy, Unequal Cost" Channel Dependence PatchTST Controlled Coupling; "Characterizing Correlation for Time Series Modeling Strategies" SOFTS variants TMLR |
| Intermittent-demand methods | intermittent demand forecasting review Croston SBA TSB ADIDA iETS probabilistic predictive distribution benchmark baselines Syntetos Boylan Kourentzes Petropoulos; Kolassa 2016 evaluating predictive count data distributions retail sales forecasting intermittent; Svetunkov Boylan iETS intermittent state space model predictive distribution; Snyder Ord Beaumont 2012 static dynamic count models; Nikolopoulos 2011 ADIDA; M5 uncertainty competition results Croston SBA TSB ADIDA weighted scaled pinball loss; "Forecasting: theory and practice" intermittent demand section; "The M5 uncertainty competition: Results, findings and conclusions" benchmarks; forecasting-encyclopedia.com intermittent demand; Petropoulos Kourentzes 2015 forecast combinations intermittent demand; Shenstone Hyndman stochastic models underlying Croston; review probabilistic forecasting intermittent demand 2024 2025; M5 competition guidelines benchmarks Croston optCro SBA TSB ADIDA iMAPA Kernel |
| Scores | Kolassa 2016 evaluating predictive count data distributions retail sales forecasting ranked probability score; Czado Gneiting Held 2009 predictive model assessment for count data Biometrics; pinball loss quantile intermittent demand all quantiles zero cannot distinguish forecasts weighted scaled pinball loss criticism M5; quantile loss intermittent demand forecasts zero quantiles discrete distribution pinball loss insensitive probability of zero evaluation; M5 uncertainty competition results weighted scaled pinball loss Makridakis Spiliotis Assimakopoulos IJF 2022; Hewamalage Ackermann Bergmeir forecast evaluation for data scientists common pitfalls intermittent series error measures; Gneiting 2011 quantiles as optimal point forecasts quantile score consistent scoring function discrete distribution; weighted interval score quantile score proper but not strictly proper distributions with same quantiles identical score Bracher Gneiting; Brier score probability of zero demand intermittent forecast evaluation discrete CRPS ranked probability score count forecast low counts; pinball loss intermittent probability of zero quantile forecasts ties identical zero-inflated forecast evaluation scoring rule limitation |
| Foundation models | Chronos TimesFM Moirai zero-shot intermittent demand sparse count series evaluation foundation models 2025 M5 retail spare parts; foundation models intermittent demand forecasting evaluation arXiv 2025 Croston TSB Chronos; "intermittent" "time series foundation models" zero-shot evaluation spare parts arXiv; GIFT-Eval benchmark intermittent series foundation models results Aksu 2024; fev-bench 2025 Shchur realistic benchmark; hurdle zero-inflated wrapper pretrained time series foundation model intermittent demand probability of zero; Chronos TimesFM M5 Walmart intermittent zero-shot evaluation WSPL; "foundation models" "intermittent demand" Croston SBA TSB 2025 2026 |
| Venues | International Journal of Forecasting editorial reproducibility replication negative results policy; TMLR acceptance criteria claims supported by accurate convincing clear evidence; International Journal of Forecasting "reproducibility check" data and code mandatory July 2023 editorial Pinson; Transactions on Machine Learning Research review timeline two months decision reviewers guidelines; International Journal of Forecasting guide for authors article length word limit research paper Elsevier; forecasting journal negative results "replication" editorial Hyndman International Journal of Forecasting encourages; NeurIPS 2025 Datasets and Benchmarks track call for papers benchmarks negative results evaluation reproducibility; International Journal of Forecasting time to first decision review weeks submission to acceptance; Hyndman 2010 "Encouraging replication and reproducible research" International Journal of Forecasting; pre-registration machine learning NeurIPS workshop pre-registered papers negative results proceedings; "registered report" OR "pre-registered" forecasting study International Journal of Forecasting time series evaluation preregistration |
| Verification | M5 uncertainty competition 42,840 time series predictive distributions Walmart; Spiliotis Makridakis Kaltsounis Assimakopoulos 2021 Product sales probabilistic forecasting M5 inventory; Kolassa 2016 Evaluating predictive count data distributions in retail sales forecasting abstract; Czado Gneiting Held 2009 predictive model assessment for count data nonrandomized PIT histogram; pinball loss intermittent demand lower quantiles zero all methods cannot discriminate; "quantile loss" intermittent "lower quantiles" zero forecasts all methods identical evaluation M5 uncertainty; Kolassa 2016 evaluating predictive count data distributions retail sales forecasting quantile loss low volume integer quantiles; Scaling-aware rating of count forecasts Tichy journal; When, Not How Much time-series foundation models sparse events Schoess; Accuracy Is Not Service intermittent-demand forecasting benchmark Chin Cheng Gunawan; When Time-Series Foundation Models Work for Quick-Commerce Demand Forecasting Kim Song; and exact-title searches for Ziel (2022) and for Wang, Kang and Petropoulos (2024) |

Sixty-six queries in all. Six statements extracted from the pages failed the three readings and are not used
here: a reading of the M5 lower quantile levels, two sentences read from a working-paper record of Shenstone
and Hyndman, the scale and the headline finding read from Schoess and von Wangenheim's full text (both re-read
from its abstract page and cited from there), and a Chronos-2 result in Chin et al.

Pages opened, each on 2026-10-17: the IDEAS/RePEc records of the M5 uncertainty paper, Kolassa (2016), Kolassa's M5 commentary, Spiliotis et al. (2021), Czado, Gneiting and Held (2009) and
Shenstone and Hyndman; the INSEAD page of Chen, Gaba, Tsetlin and Winkler; the arXiv full texts of Wang, Kang
and Petropoulos (2304.03092), Ziel (2107.06675), Damato, Azzimonti and Corani (2502.19086), Damato, Zambon,
Corani and Azzimonti (2609.28607), Tichy et al. (2211.16313), Schoess and von Wangenheim (2609.39386), Chin,
Cheng and Gunawan (2609.13840), Ebrahim, Ali and El-Kotory (2610.00589), Ansari et al. (2403.07815, full text
and abstract page), Das et al. (2310.10688), Woo et al. (2402.02592), Aksu et al. (2410.10393), Shchur et al.
(2509.26468), Ghoroghchian et al. (2610.02058), Musat and Cabuz (2602.22685), Meyer et al. (2510.13654,
abstract page), Bracher et al. (2005.12881, abstract page), Hewamalage, Ackermann and Bergmeir (2203.10716),
Damato, Rubattu, Azzimonti and Corani (2601.14031) and the abstract pages of 2609.39386, 2609.13840,
2502.19086 and 2211.16313 (v4 and v5); the Korea Science page of Kim and Song; the iaorifors record of Snyder,
Ord and Beaumont; the IDEAS record of Wang, Kang and Petropoulos in EJOR; the Duke Scholars and UNIC records
of the M5 papers; the author's summary of Svetunkov and Boylan's iETS; the `forecast` package's page for
Croston's model; the tscount scoring and surveillance PIT documentation; TMLR's acceptance criteria, FAQ,
reviewer guide and paper listing; the Elsevier page of the International Journal of Forecasting and its
editor's submission page; the Aston record of Evanschitzky and Armstrong (2010); the NeurIPS 2021
pre-registration workshop page, the 2025 Datasets and Benchmarks call and the track's 2025 blog post; the M5
methods repository README. Routes that failed: ScienceDirect full texts (HTTP 403 for every IJF article
tried), the IJF guide for authors and editor's report (403), Foresight's author guidelines (403), the ZORA
copy of Czado et al. (bot screen), Kolassa's 2016 slides (an undecodable PDF). The figure and table counts of the IJF articles below
could therefore not be read; their page ranges are the journal's.

### The table

| Paper | Venue, year | Body length | Figures, tables in the body | Figure 1 | Baselines and scores | Contribution as the abstract states it | Limitations and negative results |
|---|---|---|---|---|---|---|---|
| Makridakis, Spiliotis, Assimakopoulos, Chen, Gaba, Tsetlin and Winkler, *The M5 uncertainty competition* | IJF 38(4), 2022 | 21 journal pages (1365 to 1385) | not read (full text refused) | not read | 42,840 hierarchical Walmart series; nine quantile levels, 0.005, 0.025, 0.165, 0.25, 0.5, 0.75, 0.835, 0.975, 0.995; six benchmarks (repository README; names not on the pages opened) | Results, the top methods, the major findings and conclusions | not read |
| Kolassa, *Evaluating predictive count data distributions in retail sales forecasting* | IJF 32(3), 2016 | 16 journal pages (788 to 803) | not read | not read | Causal and non-causal models on two daily retail datasets; randomized PIT and proper scoring rules | Fine-grained retail series are low counts that need full discrete predictive distributions; MAD, MASE and wMAPE are unsuitable for count data | not read |
| Snyder, Ord and Beaumont, *Forecasting the intermittent demand for slow-moving inventories* | IJF 28(2), 2012 | 12 journal pages (485 to 496) | not read | not read | Poisson as the benchmark, negative binomial and hurdle shifted Poisson, each with dynamic parameters; measures on the whole prediction distribution; 1,046 monthly car-part series | Inventory planning should use dynamic models with distributions more flexible than the Poisson | not read |
| Wang, Kang and Petropoulos, *Combining probabilistic forecasts of intermittent demand* | EJOR 315(3), 2024 (read as arXiv 2304.03092 v4) | 11 journal pages (1038 to 1048) | 2 figures, 4 tables | 18 randomized PIT histograms with Kolmogorov-Smirnov statistics | Nine distributional methods (Poisson and negative binomial with a damped dynamic mean, two bootstraps, GAM quantile regression, LightGBM, LSTM, ARIMA, ETS) on 28,903 M5 series; log score, discrete RPS, a multi-category Brier score, inventory measures | Combinations improve both accuracy and inventory utility, with a trade-off between them | No limitations section; single dataset and fixed weights acknowledged implicitly; all-zero series excluded and said so |
| Damato, Azzimonti and Corani, *Forecasting intermittent time series with Gaussian processes and Tweedie likelihood* | IJF 2025 (journal reference of arXiv 2502.19086 v5) | not counted | 6 figures, 4 tables | Prior sample paths and credible intervals of the Gaussian process | Empirical quantiles, the Willemain bootstrap, ADIDA with conformal intervals, iETS; scaled quantile loss at levels of 0.5 and above, an RPS-like average, RMSSE, coverage; over 40,000 series | A first fully parameterised Tweedie density for intermittent series, with consistently better probabilistic forecasts | States that CASCaD reproduced its numerical results on 2025-10-15; drops quantile levels below 0.5 because every model forecasts zero there, and because the lower part of the distribution is not relevant to many intermittent applications |
| Damato, Zambon, Corani and Azzimonti, *fable.intermittent* | arXiv 2609.28607 v3, 2026 | not counted | 8 figures (with code listings), 7 tables | Each series by average inter-demand interval against squared coefficient of variation, with the classification cut-offs | Eleven distributional methods (bootstraps, a Bayesian negative binomial with a discounted Beta prior on its probability parameter, hurdle-shifted Poisson and negative binomial smoothers, static empirical and parametric laws, a new Tweedie smoother) on four panels; RMSSE and scaled quantile scores at 0.5 to 0.995, model confidence sets | An R package and benchmark | No method dominates on all four datasets; static methods are hard to beat; lower quantile levels dropped because forecasts are zero there |
| Schoess and von Wangenheim, *When, not how much* | arXiv 2609.39386 v1, 2026 | not counted | not counted | A three-panel schematic: the task, the three questions, the scoring | Twelve frozen foundation models on five sparse datasets against training-free references; chance-corrected average precision and AUC skill; Croston and TSB discussed and deliberately not used | Released point forecasts improve chance-corrected average precision over training-free references by at most 0.031; linear probes on six frozen backbones beat the backbone's point forecast in 29 of 30 pairs | A limitations subsection (five datasets, zeros that are missing values, possible pretraining overlap, intervals not adjusted); negative results stated directly |
| Chin, Cheng and Gunawan, *Accuracy is not service* | arXiv 2609.13840, accepted to IEEE ICDM 2026 | not counted | not counted | not read | 38 methods: Croston, SBA, TSB, ADIDA, a bootstrap, machine-learning and deep models, Chronos-Bolt, TimesFM, Moirai, Chronos-2; MASE and service fill rates; Friedman and Nemenyi tests | Accuracy rank and service rank disagree on intermittent demand (rank correlation -0.555 on the industrial panel) | Restricts its negative finding to intermittent demand in so many words |
| Ebrahim, Ali and El-Kotory, *Foundation or formula?* | arXiv 2610.00589 v1, 2026 | nine sections and eight supplementary sections | 6 figures, 9 tables (in the part read) | One realisation of each of the nine generating processes | TimesFM-3 against seasonal naive, Theta, AutoETS, AutoARIMA and their combination; post-hoc Croston variants, iETS and others; MASE, RMSSE, scaled nine-decile pinball loss | An exploratory description, under controlled conditions, of how TimesFM-3 behaves against classical methods | Protocol frozen before any forecast and held in the replication archive; five hypotheses with a verdict table; deviations in the text; one hypothesis reported as contradicted |
| Ansari et al., *Chronos* | arXiv 2403.07815 v3, 2024; the paper states it was reviewed on OpenReview | Sections 1 to 6 | Figures 1 to 17 and Table 1 in the main text (Tables 2 to 10 and Figures 18 to 24 in the appendix) | A schematic of scaling and quantisation, training and sampling | Six statistical, eight neural and several pretrained baselines on 42 datasets; weighted quantile loss at nine levels and MASE, relative to seasonal naive, geometric mean | A simple framework for pretrained probabilistic time series models | A qualitative-analysis-and-limitations subsection; one dataset's series with fewer than 50 non-zero values removed |

(judgment) The three IJF articles whose page ranges are known run 12 to 21 journal pages; the arXiv
exemplars run from 2 figures and 4 tables (Wang, Kang and Petropoulos) to 17 figures and one table (Chronos).
Of the exemplars whose first figure was read, none opens with its results: the first figures are a design
schematic (Chronos, Schoess and von Wangenheim), the data (Ebrahim et al., fable.intermittent, and Ziel's
M5 commentary, whose first figure plots each item's dispersion coloured by its share of zeros) or a
calibration panel (Wang, Kang and Petropoulos). The paper opens with Study 1's eighteen comparisons.

### What the strongest of them do that this paper does not

(judgment) Four things.

- **They put themselves inside the intermittent-demand literature.** Every exemplar of the forecasting line
  whose text was read names the Croston family or the count models of Snyder, Ord and Beaumont, and either
  runs them or says why not: fable.intermittent benchmarks only methods that give a distribution and says
  the Croston line gives point forecasts; Damato, Azzimonti and Corani run ADIDA with conformal intervals and
  iETS; Wang, Kang and Petropoulos review the Croston family and run distributional methods; Chin et al. run
  Croston, SBA, TSB and ADIDA and Kim and Song run Croston and TSB beside the foundation models; Ebrahim et al.
  add the Croston family post hoc. This paper excludes Croston and TSB by name in its protocol (`PROTOCOL.md`
  line 152) and cites none of that literature.
- **They score count forecasts with count scores, or drop the levels a quantile score cannot use.** Wang,
  Kang and Petropoulos score with the log score, the discrete RPS and a multi-category Brier score; Kolassa argues for
  proper scores on full discrete laws; the two Damato papers drop every quantile level below 0.5 because
  forecasts are zero there. This paper's primary score reads nine deciles, all of which are zero on most of
  its very sparse series.
- **They state one contribution and organise the paper around it.** Ebrahim et al. state theirs as an
  exploratory description and test five named hypotheses with a verdict table; Chin et al. state one
  disagreement (accuracy against service) and bound it. This paper's abstract gives three studies in turn.
- **They lead with the design or the data.** Each first figure tells the reader what is being compared or
  on what; none is a results panel.

### What this paper does that they do not

(judgment) Five things, each checkable in the record.

- **Population sampling from an enumerated frame.** GitHub repositories drawn by seeded order from 148,550,
  npm packages by hash from a frozen inventory, NYC 311 cells from the whole 2024 frame of 8,469. The
  exemplars use benchmark collections (M5, RAF, Auto, car parts), a single company's panel, simulation, or
  the most-starred repositories.
- **Registration verifiable by hash.** The protocol's registered bytes are prefixes of the committed file,
  checked twice per addition; the nearest exemplar, Ebrahim et al., froze its protocol in its own archive
  with no third-party timestamp before the runs.
- **An independent recomputation.** Every score of the three runs recomputed from the saved forecasts with
  zero disagreements, and the NYC 311 census recomputed by a script that shares no code with the pipeline.
  Damato, Azzimonti and Corani state that CASCaD reproduced their numerical results, the nearest analogue
  found.
- **The typical series and the mean side by side, everywhere.** Medians, win counts and rank tests beside
  every mean, with the series that carries each mean named. Corani et al., whom the paper cites, argue for
  the mean of a scaled score; no exemplar prints both throughout.
- **Dated amendments in the open.** Six numbered items and the Study 2 registration, each dated, each saying
  what changed and why; Ebrahim et al. keep their deviations in the text.

## Part B: the field's standards, and whether the paper meets them

### B1. Intermittent-demand methods

What the sources opened say:

- The `forecast` package's documentation computes no prediction interval for Croston's method, because the
  method has no underlying stochastic model; fable.intermittent describes the Croston line (Croston 1972,
  Syntetos and Boylan 2005, Teunter et al. 2011) as giving point forecasts that are insufficient for
  decisions.
- iETS (Svetunkov and Boylan, International Journal of Production Economics, 2023, per the author's summary)
  writes demand as a Bernoulli occurrence with a time-varying probability times a multiplicative ETS size;
  its direct-probability occurrence model underlies TSB and its inverse-odds model underlies Croston; it
  yields full predictive distributions by simulation.
- Snyder, Ord and Beaumont (IJF 2012) compare a Poisson benchmark, a negative binomial and a hurdle shifted
  Poisson that keeps Croston's Bernoulli occurrence, all with dynamic parameters and distribution-based
  measures.
- ADIDA (Nikolopoulos, Syntetos, Boylan, Petropoulos and Assimakopoulos, JORS 2011) forecasts at an
  aggregated level and disaggregates; Damato et al. run it with conformal intervals.
- fable.intermittent benchmarks only methods that give distributions; among them a negative binomial whose
  probability parameter follows a discounted Beta recursion, close in spirit to the registered dynamic
  count, and the plain empirical distribution of the data.
- The M5 uncertainty track had six benchmarks (repository README); their names were not on any page that
  opened, so this document does not list them.

The registered baselines under their names in the field:

| Registered | What it is | Its name in the literature |
|---|---|---|
| `poisson_28` | Poisson with the last-28-day mean | The static Poisson benchmark of Snyder, Ord and Beaumont |
| `nb_local_level_28` | Negative binomial around the 28-day mean, dispersion from the context | A static negative-binomial count model |
| `hurdle_count_28` | Jeffreys occurrence over 28 days, shifted Poisson size | A hurdle shifted Poisson with a fixed-window occurrence estimate |
| `hurdle_empirical_28` | Jeffreys occurrence, empirical size law of the last 28 positive days | A hurdle whose size law is fable.intermittent's static empirical distribution applied to positive days; a bootstrap without Markov occurrence or jitter |
| `dynamic_count` | Beta-Bernoulli occurrence and Gamma-Poisson size, both discounted by 0.98 per day (`pulsegraph/study2/models.py`) | A discounted Bayesian analogue of TSB with occurrence and size smoothing weights of about 0.02; a hurdle shifted negative binomial with dynamic parameters in the Snyder, Ord and Beaumont line; close in spirit to fable.intermittent's negative binomial with a discounted Beta recursion |
| `local_mean_28` | 28-day mean with empirical context-level draws | A short-window empirical forecast, akin to the history's empirical deciles that Ebrahim et al. and Damato et al. use as a benchmark |
| `autoets_weekly` | AutoETS, season 7 | The statistical baseline of Chronos, GIFT-Eval and fev-bench |

Missing, and what each would show that the present baselines do not:

- **Croston and SBA.** No distribution of their own; scored under QScore9 as a point forecast they reduce to
  the absolute error (a degenerate law with all nine quantiles equal to c scores `|y - c|`). They would show
  nothing about the laws but would give the field's reader the reference point they look for first.
- **TSB.** Its probability-updating occurrence is what the dynamic count already does; at the field's usual
  smoothing weights (well above 0.02) it would show whether faster occurrence tracking helps on series whose
  activity changes within a quarter, the persistence question the paper leaves open.
- **iETS.** The one classical model that gives a full predictive law with time-varying occurrence and an ETS
  size; it is the strongest classical comparator for the positive-law contrast, stronger than a 28-day
  empirical law.
- **The Willemain bootstrap.** A Markov occurrence with jittered sizes; it would test the one-step
  persistence that neither registered occurrence estimate models.
- **The history's empirical deciles, named as such.** Ebrahim et al. found TimesFM-3 no better than them on
  simulated intermittent counts; naming the local mean's empirical draws as this benchmark ties Study 1 to
  that result.

### B2. Scores for count forecasts

- **Proper scores for counts.** Czado, Gneiting and Held (2009) is the standard reference for predictive
  assessment of counts; the tscount documentation, which cites it, implements the logarithmic, quadratic
  (Brier), spherical, ranked probability and Dawid-Sebastiani scores as penalties. Kolassa (2016) evaluates
  count distributions by randomized PIT and proper scoring rules and calls MAD, MASE and wMAPE unsuitable for
  counts. Wang, Kang and Petropoulos (EJOR 2024) use the log score, the discrete RPS and a Brier score as
  their scores, with randomized PIT histograms for calibration; their Brier score is the multi-category form
  over the whole mass function, not a score on zero against non-zero, so no source opened uses an occurrence
  Brier score as a primary.
- **The M5 track and its critics.** The track asked for nine quantile levels from 0.005 to 0.995. Its lower
  levels do not help on mostly-zero series (fable.intermittent drops 0.005 to 0.25 because the forecasts
  there are zero); (judgment) its upper levels 0.975 and 0.995 are the ones that can separate two forecasts
  whose zero mass lies between 0.9 and 0.995, which nine deciles cannot. Ziel (IJF 2022) argues that the
  top M5 methods' objective functions failed the data's overdispersion and sporadic zeros and that
  distributional count models do better; he does not discuss ties at zero. Kolassa's
  commentary on M5 is indexed under intermittent demand and quantile forecasts; its text was refused, so
  nothing is cited from it.
- **Quantile losses at zero.** No source opened states that a quantile score at the deciles cannot separate
  two forecasts that both put more than 0.9 of their mass at zero. The nearest statements: Damato,
  Azzimonti and Corani drop every level below 0.5 because those quantiles are "generally zero for all
  models"; fable.intermittent drops its lower levels for the same reason; Schoess and von Wangenheim note
  that the median of a nonnegative sparse target is zero whenever the event probability is below one half;
  Tichy et al. find that even the discrete RPS separates models poorly on ultra-slow series; Bracher et al.
  note that the log score cannot be computed from a quantile format. (judgment) The property follows from
  the definition and the paper can state it as such: a quantile score reads only the scored quantiles, so
  two forecasts with the same quantiles at those levels score the same for every target, and a count law
  with at least 0.9 of its mass at zero has all nine deciles at zero.
- **What a referee would expect for the regime question.** (judgment) For a contrast whose two forecasts
  differ only in the probability of zero, as T1 does, the expected primary is a proper score on the
  occurrence event: the Brier score or the log score of the occurrence. For the full law, the discrete RPS
  (the paper's discrete CRPS). Part E gives the reasons for choosing between them.

### B3. Foundation models on intermittent data

- **The model papers.** Chronos reports no intermittent or count analysis, removes the series of one dataset
  that have fewer than 50 non-zero values, and notes that its mean scaling preserves zeros. The TimesFM paper
  (2024 version) is a point-forecasting paper; its pretraining filters Wikipedia pageview series with
  excessive zeros and takes Google Trends head queries because the rest are more than half sparse. Moirai
  outputs a mixture whose components include a negative binomial for positive counts, but its evaluation
  says nothing about intermittent series.
- **The benchmarks.** GIFT-Eval (four foundation models among 17 models, 23 datasets) names no intermittent or
  count series and no Croston-type baseline. fev-bench (14 models, 100 tasks) notes that its MASE and scaled
  quantile loss can fail numerically on intermittent series and that this does not occur in its tasks; it
  has no intermittent category.
- **Papers since 2024 on foundation models and intermittent demand.** Schoess and von Wangenheim (twelve
  models, five sparse datasets: released point forecasts improve event ranking over training-free references
  by at most 0.031 in chance-corrected average precision); Chin, Cheng and Gunawan (38 methods with Croston,
  SBA, TSB and ADIDA: foundation-model status does not imply low error); Kim and Song (TimesFM and
  Chronos-Bolt against Croston and TSB on more than 25,000 SKUs: on the intermittent segment TSB has the
  lowest RMSE and TimesFM the lowest MAE, neither difference significant); Ebrahim et al. (TimesFM-3 no better
  than the history's empirical deciles on simulated intermittent counts); Ghoroghchian et al. (three models on
  synthetic processes, the intermittent one only in appendix tables); Musat and Cabuz (a hurdle head trained
  end to end, not a wrapper on a frozen model). No paper found wraps a frozen model's output in a hurdle
  under a proper score; the hurdle on frozen Chronos-2 output that the re-check of 2026-10-12 recorded in Chin
  et al. was judged by point and service measures.
- **Scale.** (judgment) Three models from two families on three domains is at the small end of a critical
  evaluation (twelve models in Schoess and von Wangenheim, one in Ebrahim et al., three in Ghoroghchian et
  al.) and within the norm if the claim is about those three and about the nine-quantile interface they
  share. A referee will ask for one model whose output is not nine quantiles: Moirai's mixture with a
  negative-binomial component, or Chronos-2's own 21 levels, which include 0.95 and 0.99 (the saved forecast
  metadata lists them) and which the registered design reduces to nine deciles.

### B4. The cheapest credible fix for each standard not met

| Standard not met | Cheapest credible fix | Would a referee accept it |
|---|---|---|
| The intermittent-demand literature | Cite and position: one paragraph in related work, the table of B1 in the design section, one sentence on why Croston and TSB were excluded (no distribution of their own; the dynamic count plays TSB's part) | Yes for TMLR; for IJF only together with the next row |
| Croston, SBA, TSB, iETS or the bootstrap as baselines | A post-hoc descriptive benchmark from the saved contexts and targets: TSB with a shifted-Poisson or negative-binomial size, or iETS, with parameters fixed from the literature's defaults or estimated on the context alone, its specification and script committed before it is scored, run on every series of every panel, labelled post hoc, no test added to any family | (judgment) Yes, as descriptive evidence of where the registered baselines stand, provided the specification is fixed before scoring and nothing is selected after; not as confirmation. `statsforecast`, already pinned, has TSB and ADIDA; iETS needs R's `smooth`, a dependency outside the study code |
| Count scores as the primaries of the occurrence question | No new numbers: put the registered secondary Brier and discrete CRPS beside QScore9 in the body tables, and state the quantile score's blindness below one decile as a property with the nearest citations | Yes, with the registration saying QScore9 was primary |
| The very sparse reading | No new numbers beyond the completion floor above, which is a reading of saved laws; label it post hoc | Yes; a referee who reads `complete()` will find it anyway |
| Foundation models with other output interfaces | Cite and position (Moirai's mixture, Chronos-2's 21 levels); a new run is a new study | Yes for this paper, if the claim names the nine-quantile interface |

## Part C: two referees

### The International Journal of Forecasting referee

**The contribution, as this referee would state it.** A pre-registered evaluation of three zero-shot
foundation models on sparse daily counts from three public sources, finding that their gain over a 28-day
mean is carried by a few series and by positive days, and that substituting a context-only occurrence
probability for their zero mass does not improve a nine-decile quantile score on dense series. The
intermittent-demand methods the journal's readers use are neither run nor cited, so the paper does not say
where the models stand against them.

**The three most damaging weaknesses.**

1. **No intermittent-demand benchmarks and no intermittent-demand literature (blocks acceptance).** The
   protocol excludes Croston and TSB by name, the bibliography holds none of the field, and the dynamic count,
   which is a discounted Bayesian TSB, is not named as one. This referee will read the exclusion as a design
   choice that needs a reason, and the missing citations as a paper written from outside the field. The fix
   is in B4.
2. **The primary score (needs revision; blocks if left as the only score in the body).** The referee's
   literature scores count forecasts with the RPS, the log score and the Brier score, or drops the quantile
   levels a quantile score cannot use. The paper's own ties confirm the problem, and its sentence "The
   registered score is blind below one decile" (Section 16) is a finding this referee will say was
   foreseeable from the definition, and was in fact foreseen at readiness (the first-stage record of
   2026-10-17 counted 74 of the 100 very sparse series on the fallback before the run).
3. **Aggregation and scale (needs revision).** An unscaled score with equal series weights lets one npm
   series carry every mean; the journal's readers expect scaled measures. The context-scaled QScore9 is a
   registered secondary and agrees with the medians; it should lead.

**An objection to anticipate.** Damato, Azzimonti and Corani drop the lower quantiles also because, for many
intermittent applications, the lower part of the distribution is not decision-relevant. An inventory referee
will ask why the probability of a zero day matters for stars, downloads and service requests. The paper
should answer in two sentences: for these series the zero day is the event of interest (no new star, no
download, no complaint), and a forecaster that cannot say how likely it is cannot be used for alerting or
for detecting a change in activity.

**One argument or a chronicle.** A chronicle: the Study 1 report is carried whole, and each later study is
introduced by what the previous one left open. This referee would accept three studies if the paper said in
its first paragraph that they are one design run in three steps, with the step-by-step reasons in the
appendix.

**Amendments.** (judgment) To this readership the lapses read as project management (a holdout not frozen,
a readiness clock reset, two domains deferred). The paper mentions them in Sections 7, 8 and 17 and never
gives their cause; the protocol's own sentence, that no work was done between 2026-09-14 and 2026-10-11,
belongs once in the ledger, with the lapses beside it, and nowhere else. Item 6, decided
after the npm scores were seen, is the one a forecasting referee will look at hardest; its sensitivity is
complete and should sit next to the registered row.

### The TMLR reviewer

**The contribution, as this reviewer would state it.** A registered, fully reproducible evaluation of three
frozen forecasting models on population-sampled sparse count panels: on GitHub stars the typical series
favors a trailing mean while the equal-weight mean favors the models, and a context-only occurrence
correction of the models' output does not help where their quantiles carry information and cannot be
assessed where they do not. The record (hashes, recomputation, every number traced) is more careful than
any evaluation in this area that Part A found.

**The three most damaging weaknesses.**

1. **The claims run ahead of the evidence on very sparse series (needs revision).** "The record supports
   two readings of that outcome, with equal weight" (Section 15) is not what the saved laws show: the
   completed law's occurrence on those series is the completion floor, so neither the ties nor the Brier
   separation is evidence about the models. Under TMLR's first criterion the remedy is to narrow the claim.
2. **Focus and length (needs revision).** About 23 pages of body by word count against TMLR's 12-page
   threshold, beyond which reviews run on the longer track; three studies told in sequence; the main finding
   in the discussion's middle. The reviewer will ask for one question and one figure that answers it.
3. **Generality of "foundation models" (noted; needs revision of wording).** Three models from two families,
   all reduced to nine deciles; no model whose output is a mixture or a sample. The conclusions are about this
   interface, and the title and abstract should say so.

**One argument or a chronicle.** A chronicle in form, one argument in substance: Study 1 locates the loss
on zero days, Study 2 replaces the occurrence, Study 3 asks it by regime. Told in that order as questions
rather than as studies, it is a single paper.

**Amendments.** (judgment) This audience values the ledger, and will read it as transparency if it is one
table in the design section with a before-or-after column, and as instability if it is spread across the
body as it is now (the design of Study 2 opens with three additions and their commits).

### Where the text narrates process rather than science

| Place | The process in the text |
|---|---|
| Section 1, second paragraph | "The story of this report is in four parts." A reading guide to the work's history |
| After the abstract, the unnumbered paragraph | Sections 1 to 6, 7 to 10, 11 to 14 mapped to the order the studies were run |
| Section 4, last paragraph | Run start time, implementation commit, 18,662 seconds, rows, no resume |
| Section 7, first paragraph | Registration commit and full SHA-256 in the running text |
| Section 8, first paragraph | Three dated additions with their commits before the design is described |
| Section 9, first paragraph | Freeze and verification times to the minute; the reset deadline |
| Section 10, "Three zero days" | The sensitivity computed at 03:21 UTC, the addition written at 03:28 UTC |
| Section 11, second paragraph | Each change in Study 3 tied to an item number of the project's own review document (W1, W9, W2, W4) |
| Section 13, first two paragraphs | 276 attempts, two invocations, 1,124 seconds, an approval of 330 attempts and 3 hours; 106 attempts of 120, 16 repeats after throttling, three seconds apart |
| Section 14, first paragraph | 939 seconds inside the run and 956 for the process against a budget of 3,600 and an estimate of 1,080 |
| Sections 10 and 14, last paragraphs | "Null, adverse, mixed and imprecise outcomes are reported with the same care as a positive one." |
| Section 18 and Appendix G | Run times, approvals and commands, which belong in the appendix and the repository |

### Where the voice lacks the author's judgment

(judgment) The text says what was done and what was found, rarely why or with what expectation. Five places
where a reader wants the author:

- **Why QScore9.** The score is defined and never defended; one sentence on why a nine-decile score was
  registered (the models' native output, continuity with Study 1) and what was given up would change how a
  referee reads the ties.
- **Why 0.5.** H3's threshold is Study 2's registered stratum boundary; on npm the substitution's typical
  series wins from about there, while on NYC 311 it loses below 0.5, about breaks even from 0.5 to 0.9 and
  ties above. The author should say that the threshold was carried from the strata, not derived, and that
  the per-series picture suggests it is domain-specific.
- **What surprised.** The npm sparse reading did not reproduce; the paper gives two readings and no
  reaction. A sentence on what was expected and why it did not come would read as judgment.
- **What was seen coming.** The ties were counted at readiness, before the run. Saying so, and saying that
  amending the primary after registration but before targets was considered or not, is the honest and the
  stronger account.
- **What would be done differently.** Register count scores for the occurrence contrast; keep Chronos-2's
  21 levels; include TSB and iETS. Three sentences in the discussion.

### The amendments: transparency or instability

The record holds seven dated changes: the Study 2 registration (2026-09-14) and items 1, 2 and 3
(2026-10-12), 5 (2026-10-15), 6 and 7 (2026-10-16); item 4, a November round drafted on 2026-10-12, was
never appended, so the numbering has a gap a reader will notice. (judgment) A one-table ledger is the right
form and matches the nearest exemplar's practice (Ebrahim et al. give a hypothesis-verdict table and keep
their deviations in the text; the sweep of 2026-10-16 found their archive separating deviations made before
and after results).
Four columns make it read as transparency: what changed, when, whether it was decided before any target of
the study it touches was seen, and which registered test it touches. Items 1 to 3, 5 and 7 are "before";
item 6 is "after scores, sensitivity reported"; item 4 is "drafted, not appended". One row each, one sentence
each, in the design section; the commits and hashes in a column, not in the prose.

## Part D: the venue

**TMLR.** Its acceptance criteria are two: claims supported by accurate and convincing evidence, the most
important; and interest to some of its audience, which an unsure reviewer is told to assume. Novelty is not
required, and authors may close a gap between claim and evidence by narrowing the claim. The FAQ aims at a
decision about nine weeks after submission, gives reviewers two weeks for a main body of up to twelve pages
and four for longer ones, welcomes replications and asks for shorter manuscripts. Its Reproducibility
Certification is for reproductions of other published work and does not fit here. The portions of the paper
listing read on 2026-10-17 (June to October 2026) show forecasting papers in each of those months (zero-shot
forecasting with prior-fitted networks, multi-horizon forecasting, conformal multi-source forecasting,
probabilistic forecasting), critical and reproducibility papers in other areas, and none on intermittent
demand or count data. (judgment) This audience would credit the registration, the recomputation, the
population sampling and a negative or bounded result stated as such; it would not credit length, a
chronicle, or "foundation models" claimed from two families with one interface.

**The International Journal of Forecasting.** Its scope puts strong emphasis on empirical evaluation,
encourages replication studies, publishes data and code as supplements and reviews double-blind; the
editor's submission page asks that an empirical study's description of method and data be sufficient for
replication and that code and data be submitted. Damato, Azzimonti and Corani (IJF 2025) state that CASCaD
reproduced their numerical results. Its exemplars here run 12 to 21 journal pages. No statement on negative
results or registered reports was found on the pages that opened; Evanschitzky and Armstrong (IJF 2010)
count replications at 8.4 percent of the empirical papers in IJF and the Journal of Forecasting from 1996 to
2008, of which 19.6 percent did not support the original. Review times were not found on any page that
opened. (judgment) This audience would credit the registration and the count-data setting and would not
credit the missing intermittent-demand baselines and literature, the nine-decile primary, or attention
counts as a forecasting application without a decision attached.

**A third venue.** A referee in machine learning would name the NeurIPS Datasets and Benchmarks track, whose
2025 call covers novel benchmarking methodologies and audits that identify problems with existing datasets and
their use, and requires code and data available at submission with Croissant metadata. Its calendar does not
meet 2026-10-31. The 2021 NeurIPS pre-registration workshop is the machine-learning precedent for papers
reviewed on their protocol before results; it is a workshop, not a venue for this paper.

**Recommendation.** (judgment) TMLR, by 2026-10-31 as planned, with the body cut to twelve pages so the
review runs on the standard track. Its criterion is the one this paper meets best once its claims are the
ones the saved files support, and its audience is where frozen-model evaluations are read. The International
Journal of Forecasting is the right venue for the next paper, the one that registers TSB, iETS and a
bootstrap beside the models and makes the RPS and the occurrence score primary; sending this paper there
now invites the first weakness of Part C as a rejection reason. The decision is the author's.

## Part E: the fourth study

The proposal: a registered Study 4 on unseen target days (September 2026, origin 2026-08-31, thirty
target days) on NYC 311 and npm, the same variants, the occurrence Brier score primary for the contrast that
differs only in the probability of zero, the discrete CRPS or log score for the full law, the
intermittent-demand baselines registered beside the present ones, per-stratum tests, and a stopping rule.

**Is the Brier score the right primary for that contrast?** (judgment) It is a right one. For two hurdle
laws that share a positive law, as the completed control and the dynamic hurdle do, the log-score difference
of the full law equals the log-score difference of the occurrence event exactly: at a zero day it is
`log(1 - p) - log F(0)` and at a positive day `log p - log(1 - F(0))`, the positive law cancelling. So the
occurrence log score is at once the occurrence score and the full-law score for T1, and it is the more
principled primary; it is finite here because the Jeffreys and Beta estimates stay inside (0, 1) and the
completed law's zero mass and its complement are both positive. The Brier score is bounded and less
sensitive to probabilities near zero or one; either would be accepted.

**The discrete CRPS or the log score for the full law?** The discrete CRPS (RPS). For contrasts where the
positive law differs, the log score is unusable with the registered empirical hurdle: its positive law puts
mass only on values seen in the last 28 days, so any other positive count scores minus infinity.

**What the Study 3 effect sizes imply for 100 series per stratum.** From the resampling above, if the Study
3 effects recur: dense rows reject on the Brier score with probability 0.35 to 1.00 at 100 series at a
Bonferroni level of 0.05/12, and on the discrete CRPS 0.66 to 1.00; very sparse rows 0.63 to 1.00 and 0.72 to
1.00; sparse rows at most 0.25 on the Brier score and 0.11 on the CRPS at 100 series, and four of the six
sparse rows stay at or below 0.05 even at 300 (their series split close to evenly, 45 to 57 of 100 lower).
So 100 series per stratum settles the dense and very sparse strata and no affordable panel settles the
sparse one on NYC 311.

**What the very sparse rows would confirm.** On 91 to 98 percent of the very sparse completed forecasts
the model's occurrence is the completion floor. A very sparse Brier result is a comparison between a context
estimate near 0.017 and a constant near 0.061, and it would "confirm" what the formula in `complete()`
predicts. (judgment) A referee who reads the completion would not count it as evidence about the models.

**Where it would add substance: npm's sparse stratum at a week.** Resampling the 100 sparse npm series the
same way, if the Study 2 effects recur, a horizon-7 test of the fixed 28-day hurdle against the completed
control rejects at 0.05/12 with probability 1.00, 0.63 and 0.87 under QScore9 (the hurdle lower on 81, 60
and 66 of 100 in Study 2) and 1.00, 0.81 and 0.98 under the occurrence Brier score (lower on 85, 64 and 70);
the post-hoc dynamic hurdle gives 1.00, 0.01 and 0.01 (lower on 76, 38 and 53); at 30 days most rows fall
below 0.25. npm's very sparse stratum holds nine series and would be unavailable under the registered
ten-series rule. (judgment) So the one part of the proposal likely to yield something new is a registered
replication, on September days, of the npm sparse reading at a week: it would turn the paper's best
secondary finding into a confirmatory one and make "the answer depends on the domain" a registered
statement. It is narrow (one domain, one horizon, the same 100 series a month later, the fixed occurrence
rather than the dynamic one Study 3 registered) and it does not change the thesis.

**A retrospective September window or a prospective round?** September 2026 postdates every pinned weight
file (Chronos-2's revision of 2026-06-05, TimesFM 2.5's of 2025-10-02, TimesFM 3's weights uploaded
2026-08-24), so it would be the paper's first window that no checkpoint could have seen, which is a real
gain for the raw comparison, though not for the occurrence question. (judgment) A referee would accept a
retrospective window from a design that commits its specification by hash before the pull, as the earlier
studies did, while noting that the data existed when the study was registered; only a prospective round
(the November freeze of 2026-10-28 18:00 UTC, scored from 2026-12-15) removes that note, and it lands after
the submission date.

**Would a referee read Study 4 as the study they would have asked for?** No. The referee of Part C would ask
for the intermittent-demand baselines, count scores as primaries, and a model output that can express an
occurrence below one in ten. The proposal brings the first two to the same three models and the same nine
deciles, so its dense half repeats a confirmed result, its very sparse half measures the completion rule,
and its NYC 311 sparse half is underpowered; only its npm sparse rows at a week would add a result. As a
whole it would read as one more.

**Verdict.** Submit now, by 2026-10-31, with the secondary evidence labelled, the completion floor stated
and the intermittent-demand literature positioned; register no Study 4 as proposed. If the author wants
numbers for the baselines before submission, the post-hoc descriptive benchmark of B4 is cheaper and is
what a referee would accept. If the author wants one more registered result, keep the narrow npm
replication above in reserve: six tests (three models, one hurdle against its completed control; twelve
with both hurdles), horizon 7, the occurrence Brier score primary, registered by a dated
addition before any September value is read, run only if a reviewer asks for the sparse regime to be
confirmed; TMLR's rolling review allows a revised version. The fourth study worth running is the next paper's: a model output that is not
nine deciles (Chronos-2's 21 levels, a mixture, or sample paths), TSB, iETS and a bootstrap registered as
baselines, the occurrence log score or Brier score and the RPS as primaries, per-stratum tests with a
threshold chosen from a per-series curve rather than carried from npm, and a prospective window.

## Part F: the shape

**The thesis sentence.** Frozen time-series foundation models earn their keep on sparse daily counts in the
size of the days that are not zero: their own probability of a zero day is as good as a context-only
estimate wherever their nine quantiles can express one, and where they cannot, on series that are zero nine
days in ten, neither the models nor a quantile score can say anything about occurrence.

**A title.** *What nine quantiles can say about a zero day: frozen forecasting models on sparse daily counts
in three registered studies.* A plainer alternative: *Size, not occurrence: zero-shot foundation models on
sparse daily counts.*

**Sections, with a page budget (twelve pages of body).**

| Section | Pages | What it holds |
|---|---|---|
| 1. Introduction | 1.25 | The problem in practice; the thesis; the three studies as one design run in three steps; three contributions (the registered, population-sampled record; the occurrence result by regime; the interface limit); what is not claimed |
| 2. Related work | 1.0 | Intermittent-demand methods and count models; count scores and quantile scores on discrete data; foundation models on intermittent data; registered evaluation |
| 3. Design | 2.0 | The forecasters as a two-by-two of occurrence source by positive-law source; the completion, with its floor; the scores (QScore9 primary as registered, Brier and RPS secondary); the three panels in one table; calendar and inference in one paragraph; the registration ledger |
| 4. What the models add over a trailing mean | 1.5 | Study 1 and the raw contrasts on npm and NYC 311 in one table; the accounting's finding in two sentences |
| 5. The occurrence substitution, by regime | 2.5 | The signature figure; dense series (npm pooled, grid, NYC 311 dense: confirmed); sparse series (npm secondary for, NYC 311 against); very sparse series and the interface limit |
| 6. The positive law against count laws | 1.0 | The shifted Poisson, the empirical hurdle, the dynamic count as the grid's best non-oracle forecaster, the fourth cell |
| 7. Discussion | 1.25 | What the three studies say together; what the interface implies for evaluating these models on counts; what surprised; what would be done differently |
| 8. Limitations | 0.75 | Eight items at most: survivor panel, contamination, three origins, three models and one interface, one series behind the npm means, served zero days, what a star, a download and a request measure, the November round not run |
| 9. Registration and reproducibility | 0.5 | Hashes, the recomputation, what is released and where |

**Figures.**

1. *The design at a glance* (Section 3): the two-by-two of forecasters with the registered names under the
   plain ones, and the three panels as three columns (frame, sampling, strata, series). Drawn from the
   protocol and the panel manifests (`reports/registered-2026-09-13/`, `reports/study2-npm/panel/manifest.json`,
   `reports/study3-nyc311/panel/manifest.json`).
2. *The signature figure* (Section 5): for each zero-fraction bin, the share of series where the
   substitution scores lower than its completed control, tied and higher, under QScore9 and under the
   occurrence Brier score, one line per domain, with the grid as three points at its zero probabilities.
   Drawn from `reports/study2-npm/run-2026-10-15/inference/series_scores.csv`,
   `reports/study3-nyc311/run-2026-10-17/inference/series_scores.csv`, the two manifests' `zero_fraction`
   and `reports/study2-synthetic-2026-10-15/inference/series_scores.csv`. (judgment) A per-series contrast
   against the context zero fraction holds up as the signature figure, with one change: on npm the raw
   differences span many orders of magnitude, so the figure should plot shares per bin rather than points.
   Binned this way it shows what the paper says in prose, in one picture: the substitution loses on dense
   series in both domains; on npm it wins the typical series from a zero fraction of about 0.5 at horizon 7
   (lower on 68 and 139 pairs against 35 and 52 higher in the two bins from 0.5 to 0.9); on NYC 311 it about
   breaks even there (40 against 38 and 108 against 70, with up to 18 percent tied); and above 0.9 the
   QScore9 ties take over while the Brier score separates.
3. *The completion floor* (Section 5): the completed law's occurrence probability against the context
   estimate on the very sparse series, with the floor of 0.0607 drawn. Drawn from the saved laws in the 300
   NYC 311 checkpoints (release asset); a one-panel schematic of the completed CDF for all-zero deciles
   is the alternative that needs no asset.
4. *The mean and the typical series* (Section 4): the signed cumulative contribution to the mean difference
   of the raw models against the local mean, series sorted, one panel per domain. Drawn from
   `reports/registered-2026-09-13/inference/paired_repositories.csv` (or the post-hoc
   `posthoc/posthoc-contribution-curves.csv` beside it) and the two runs' `series_scores.csv`.

**Tables.**

1. The three panels and designs (domain, frame, sampling, strata, series, calendar, family, status).
2. The raw models against the local mean in three domains: median, series lower, mean and the rank-test
   verdict per model and horizon.
3. The occurrence substitution by stratum and domain: series lower, tied and higher, median and verdict,
   QScore9 and Brier side by side; the npm rows marked secondary, the NYC 311 rows confirmatory.
4. The positive-law contrasts: against the shifted Poisson, the empirical hurdle and the dynamic count, per
   domain.
5. The registration ledger.

**To the appendix.** The full families E01 to E18, S01 to S06 and R01 to R36 with every column; the
accounting tables; Study 1's tables by stratum, calibration and coverage; the version 1 audit; the npm zero
days and their sensitivity; the post-hoc dynamic-occurrence analysis; the grid cells; the panel details; the
contamination ledger; the run record (times, approvals, budgets) in one table; the commands.

**In the repository only, cited by commit.** The request ledgers and throttle tallies; the readiness and
gate records; the smoke records; the source-terms record; `paper/sources.md` and the number checker; the
per-series CSVs; the project's own review documents, which a paper should not cite by item number.

**The registration ledger.** One table in Section 3, a row per dated change:

| Item | Date | What changed | Decided | Tests touched |
|---|---|---|---|---|
| Study 1 | 2026-09-12 | The protocol, before any target was fetched | before | 18 |
| Study 2 | 2026-09-14 | The occurrence test, three domains, the grid, the holdout | before any Study 2 target | 54 + 6 + 18 |
| 1 | 2026-10-12 | The October holdout reported as not run | before any Study 2 target | H01 to H18 |
| 2 | 2026-10-12 | The npm readiness clock reset once | before | none |
| 3 | 2026-10-12 | The external family fixed at E01 to E18; two domains deferred | before | E19 to E54 deferred |
| 4 | drafted 2026-10-12 | A November round, never appended | not registered | none |
| 5 | 2026-10-15 | Discrete CRPS recorded as unavailable when not certified | before any Study 2 target | none (a secondary) |
| 6 | 2026-10-16 | npm's served zero days scored as served; a sensitivity beside them | after the npm scores | E01 to E18 unchanged |
| 7 | 2026-10-16 | Study 3 | before any Study 3 target | R01 to R36 |

Two further protocol sections, the birth-cohort census of 2026-09-14 and the bounded fine-tune of the spring
plan, are open and touch no test of this paper; one sentence under the table says so.

**Writing patterns to remove.**

1. *Run logistics as results.* "The run started 2026-10-17 at 03:47 UTC and scored all 300 series in one
   invocation, in 939 seconds inside the run and 956 for the whole process against a budget of 3,600 and an
   estimate of 1,080, with no failed window and no resume." Rewrite: "Every one of the 39,600 forecasts was
   scored once and recomputed independently with no disagreement (Appendix I)."
2. *A map of the work's history in place of a statement of contributions.* "Sections 7 to 10 add Study 2,
   registered after Study 1's results were seen and run on data declared for the purpose, with two post-hoc
   analyses labeled as such." Rewrite: "This paper makes three contributions: ..."
3. *Balance where the record decides.* "The record supports two readings of that outcome, with equal
   weight: the benefit on sparse series may be smaller than the npm secondary tables suggested, or the
   registered score may be unable to see it on series whose deciles are all zero under both forecasts."
   Rewrite: "On series that are zero nine days in ten the models' nine deciles are all zero, so the completed
   law's occurrence sits at its floor of 0.061 whatever the model forecast; the quantile score cannot
   separate two such forecasts, and the Brier score's separation compares the context estimate with that
   floor, not with the model."
4. *Internal review items as motivation.* "with four changes from Study 2's construction, each answering a
   question that the standing check of 2026-10-16, recorded in the repository as the referee's read, put to
   the paper." Rewrite: "Study 3 changes four things, each prompted by a Study 2 result: ..."
5. *The scope disclaimer repeated.* "The claim is the registered combination on those three settings, and
   nothing broader." (abstract, and in substance in Sections 7, 11 and 15). Rewrite: state the scope once, in
   the discussion's claim paragraph.
6. *Range lists in place of a finding.* "the medians lie within 0.014 of zero, three below it and three
   above; the hurdle scores lower on 81 to 121 of the 209 series; and the signed-rank test rejects after
   adjustment in two of the six cells". Rewrite: "Against its completed control the substitution is better
   on no npm row at q = 0.05 and worse on two (Table 3)."
7. *Hashes and timestamps in the prose.* "at commit 3357d779db28cffa4048e7e333fd02b9434b4b6d (full protocol
   SHA-256 with the addition 05c7617b...)". Rewrite: "registered as item 7 of the ledger (Table 5)."
8. *Registry labels in every sentence.* "Everything in this paragraph is declared secondary, unadjusted, and
   confirms nothing". Rewrite: one convention sentence in Section 3 ("tables marked secondary add no test"),
   and the label in table captions.
9. *Code identifiers as names.* "\emph{hurdle\_dynamic} is lower than \texttt{hurdle\_empirical\_28}
   wherever a T2 test rejects". Rewrite: "The dynamic hurdle beats the empirical hurdle wherever a test
   rejects", with the identifiers in the two-by-two figure only.

## Regeneration

The post-hoc computations come from the saved files by this command, run from the repository root in
PowerShell. The binned contrasts, the resampled power and the npm rows read only committed files; the
completion-floor count reads the 300 NYC 311 checkpoints, which are not in the tree and are to be published
as a release asset. It adds no test. The resampling uses seed 20261017 and 2,000 draws per row, in the order
the command prints them.

```powershell
@'
import glob, json
import numpy as np, pandas as pd
from scipy import stats
RT = dict(float_precision="round_trip"); FM = ["chronos2", "timesfm3", "timesfm2p5"]
NPM, NYC = "reports/study2-npm", "reports/study3-nyc311"
def load(scores, manifest):
    d = pd.read_csv(scores, **RT)
    z = {s["series_id"]: s["zero_fraction"] for s in json.load(open(manifest, encoding="utf-8"))["series"]}
    return d.assign(zf=d.series_id.map(z))
npm = load(f"{NPM}/run-2026-10-15/inference/series_scores.csv", f"{NPM}/panel/manifest.json")
nyc = load(f"{NYC}/run-2026-10-17/inference/series_scores.csv", f"{NYC}/panel/manifest.json")
def contrast(d, variant, h, score):
    out = []
    for m in FM:
        a = d[(d.model == f"{m}_{variant}") & (d.horizon == h)].set_index("series_id")
        b = d[(d.model == f"{m}_completed") & (d.horizon == h)].set_index("series_id")
        out.append(pd.DataFrame(dict(model=m, diff=a[score] - b[score], zf=a.zf, stratum=a.stratum)).dropna())
    return pd.concat(out)
BINS = [0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.97, 1.0001]
for name, d, v in [("npm", npm, "hurdle"), ("nyc311", nyc, "hurdle_dynamic")]:
    for h in (7, 30):
        for score in ("qscore9", "occurrence_brier"):
            c = contrast(d, v, h, score); g = c.groupby(pd.cut(c.zf, BINS, right=False), observed=True)["diff"]
            print(name, v, h, score, [(str(k), len(x), int((x < 0).sum()), int((x == 0).sum())) for k, x in g])
rng = np.random.default_rng(20261017)
for score in ("occurrence_brier", "discrete_crps"):
    for st in ("dense", "sparse", "very_sparse"):
        for m in FM:
            for h in (7, 30):
                c = contrast(nyc, "hurdle_dynamic", h, score); x = c[(c.model == m) & (c.stratum == st)]["diff"].to_numpy()
                row = []
                for n in (100, 300):
                    p = [stats.wilcoxon(s[s != 0], method="approx").pvalue for s in (rng.choice(x, n) for _ in range(2000))]
                    row.append(round(float(np.mean(np.array(p) < 0.05 / 12)), 2))
                print("power", score, st, m, h, "lower", int((x < 0).sum()), "P(p<0.05/12) at n=100, 300:", row)
strata = {s["series_id"]: s["stratum"] for s in json.load(open(f"{NYC}/panel/manifest.json", encoding="utf-8"))["series"]}
floor, total, occ = {}, {}, {}
for path in glob.glob(f"{NYC}/run-2026-10-17/[0-9a-f]*.json"):
    for r in json.load(open(path, encoding="utf-8"))["rows"]:
        base = next((f for f in FM if r["model"].startswith(f + "_")), None)
        v = r["model"][len(base) + 1:] if base else None
        if v not in ("completed", "hurdle_dynamic"):
            continue
        law, k = r["forecast"]["distributions"][0], (strata[r["series_id"]], base, v)
        if v == "completed":
            on = law["deciles"][-1] < 0.5
            floor[k] = floor.get(k, 0) + on; total[k] = total.get(k, 0) + 1
            if on:
                occ.setdefault(k, []).append(0.1 * np.exp(-(0.5 - law["deciles"][-1]) / law["tail_scale"]))
        else:
            occ.setdefault(k, []).append(law["p"])
for k in sorted(total):
    print("floor", k, floor[k], "of", total[k], "median occurrence on floor", round(float(np.median(occ[k])), 4) if k in occ else None)
for k in sorted(x for x in occ if x[2] == "hurdle_dynamic"):
    print("dynamic", k, "median p", round(float(np.median(occ[k])), 4))
dyn = pd.read_csv("reports/study2-posthoc-dynamic-occurrence/npm_paired_entities.csv", **RT)
dyn = dyn[dyn.reference.str.endswith("_completed")]
stn = {s["series_id"]: s["stratum"] for s in json.load(open(f"{NPM}/panel/manifest.json", encoding="utf-8"))["series"]}
for m in FM:
    for h in (7, 30):
        xs = {"dynamic qscore9": dyn[(dyn.model == f"{m}_dyn") & (dyn.horizon == h) & (dyn.entity.map(stn) == "sparse")]["difference"].to_numpy()}
        for score in ("qscore9", "occurrence_brier"):
            c = contrast(npm, "hurdle", h, score); xs[f"fixed {score}"] = c[(c.model == m) & (c.stratum == "sparse")]["diff"].to_numpy()
        for k, x in xs.items():
            p = [stats.wilcoxon(s[s != 0], method="approx").pvalue for s in (rng.choice(x, 100) for _ in range(2000))]
            print("npm sparse", m, h, k, "lower", int((x < 0).sum()), "of", len(x), "P(p<0.05/12) at n=100:", round(float(np.mean(np.array(p) < 0.05 / 12)), 2))
'@ | .\.venv\Scripts\python.exe -
```

The per-section word counts quoted in Part C come from expanding `paper/paper.tex`'s inputs, removing
comments, floats and commands, and counting the running text before the appendix: 15,501 words by that
rough method against 15,815 by the revision's.

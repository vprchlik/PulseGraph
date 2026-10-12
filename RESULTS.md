# PulseGraph v2 registered results

Protocol: 5f01769b6be4c32814befdd7cc3395b6dcc386ed. Implementation: ca67dd22ea49377ee1fd074aed57b4b7460c84f1.

Gate: pass. Run: complete in 5.1839 hours, including resumes.
Failures: 0. Resumes: 0.
Integrity: pass for the 48,600-row grid and all 300 checkpoint hashes.

Differences are model minus reference QScore9. Intervals are pointwise 95%
percentile intervals from 20,000 repository-cluster bootstrap replicates.
Raw p-values are two-sided Wilcoxon signed-rank p-values; BH adjustment covers
the declared 18 comparisons. Each comparison includes 300 repositories.
Inference is conditional on the fixed evaluation calendar. Strict wins count
only negative differences; the strict win fraction has all 300 repositories
in its denominator. Median differences and win fractions come from inference.csv;
win counts equal n_repos times that fraction, verified against the paired scores.

| Model | Reference | Horizon | Mean difference | Median difference | Model lower (of 300) | Strict win fraction | 95% interval | Raw p | BH p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chronos2 | local_mean_28 | 7 | -0.136907 | 0.00102385 | 79 | 0.263333 | [-0.342077, 0.00936674] | 9.49945e-06 | 1.00582e-05 |
| chronos2 | local_mean_28 | 30 | -0.131984 | 0.00175706 | 59 | 0.196667 | [-0.284598, -0.021734] | 3.97716e-12 | 5.50683e-12 |
| chronos2 | local_mean_28 | 90 | -0.101434 | 0.00227719 | 50 | 0.166667 | [-0.211031, -0.0157161] | 8.47806e-14 | 1.38732e-13 |
| chronos2 | autoets_weekly | 7 | -1.06897 | -0.165794 | 296 | 0.986667 | [-1.45928, -0.699845] | 1.04362e-48 | 2.08723e-48 |
| chronos2 | autoets_weekly | 30 | -2.12675 | -0.212804 | 298 | 0.993333 | [-2.83115, -1.5356] | 1.26904e-49 | 3.26324e-49 |
| chronos2 | autoets_weekly | 90 | -6.72431 | -0.282651 | 298 | 0.993333 | [-13.4237, -2.86795] | 8.5401e-50 | 3.07443e-49 |
| timesfm3 | local_mean_28 | 7 | -0.258439 | 0.000291014 | 89 | 0.296667 | [-0.717951, 0.0120197] | 0.00667671 | 0.00667671 |
| timesfm3 | local_mean_28 | 30 | -0.20122 | 0.000420579 | 75 | 0.25 | [-0.488152, -0.023905] | 7.48654e-07 | 8.42235e-07 |
| timesfm3 | local_mean_28 | 90 | -0.128252 | 0.00323922 | 54 | 0.18 | [-0.295702, -0.015973] | 4.95933e-12 | 6.37628e-12 |
| timesfm3 | autoets_weekly | 7 | -1.1905 | -0.181689 | 297 | 0.99 | [-1.54736, -0.890148] | 4.3055e-50 | 2.24892e-49 |
| timesfm3 | autoets_weekly | 30 | -2.19599 | -0.217118 | 298 | 0.993333 | [-2.9155, -1.58336] | 9.74141e-51 | 8.76727e-50 |
| timesfm3 | autoets_weekly | 90 | -6.75113 | -0.284403 | 293 | 0.976667 | [-13.4758, -2.87093] | 8.66264e-49 | 1.9491e-48 |
| timesfm2p5 | local_mean_28 | 7 | -0.242877 | 0.00154041 | 68 | 0.226667 | [-0.694676, 0.0246318] | 2.69618e-08 | 3.23541e-08 |
| timesfm2p5 | local_mean_28 | 30 | -0.200689 | 0.00276181 | 49 | 0.163333 | [-0.510448, -0.0149052] | 1.61218e-13 | 2.41828e-13 |
| timesfm2p5 | local_mean_28 | 90 | -0.112036 | 0.00412808 | 46 | 0.153333 | [-0.28463, 0.000601546] | 1.07537e-14 | 1.93567e-14 |
| timesfm2p5 | autoets_weekly | 7 | -1.17494 | -0.175453 | 297 | 0.99 | [-1.53378, -0.874305] | 4.9976e-50 | 2.24892e-49 |
| timesfm2p5 | autoets_weekly | 30 | -2.19546 | -0.212141 | 298 | 0.993333 | [-2.93223, -1.57966] | 9.74141e-51 | 8.76727e-50 |
| timesfm2p5 | autoets_weekly | 90 | -6.73492 | -0.280923 | 297 | 0.99 | [-13.3388, -2.87075] | 1.07252e-49 | 3.21757e-49 |

For the descriptive tables, scores are averaged within repository/horizon
before averaging across repositories. Within a regime, only its windows are
averaged for each represented repository. Sampling strata come from the frozen
manifest; regimes are the saved context labels. Window counts count
repository/cutoff/horizon rows for the named model. Horizons are in days.
NaN denotes an undefined statistic; valid denominators are retained in the CSVs.

## Scale review against local_mean_28

This is a declared secondary scale review, not a confirmatory test. Skill is 1-model/reference, undefined at reference zero; gain is reference-model. The top-five share divides the five largest positive repository gains by all positive gains; the range removes each repository in turn from the mean gain.

| Model | Horizon | Mean skill | Median skill | Defined skill (of 300) | Top-five positive-gain share | Leave-one-out mean-gain range |
| --- | --- | --- | --- | --- | --- | --- |
| autoarima_weekly | 7 | -18.7375 | -2.27098 | 209 | 0.998734 | [-1.4216, -1.16095] |
| autoarima_weekly | 30 | -19.4672 | -3.17858 | 239 | 1 | [-1.86292, -1.66301] |
| autoarima_weekly | 90 | -50.3121 | -4.99824 | 259 | 1 | [-4.15083, -2.51809] |
| autoets_weekly | 7 | -21.4737 | -2.26424 | 209 | 0.999965 | [-1.10495, -0.828517] |
| autoets_weekly | 30 | -16.7365 | -3.6764 | 239 | 0.999298 | [-2.03731, -1.79626] |
| autoets_weekly | 90 | -28.7081 | -6.10664 | 259 | 1 | [-6.66755, -3.73575] |
| autotheta_weekly | 7 | -18.8722 | -2.01176 | 209 | 0.999886 | [-0.977494, -0.707546] |
| autotheta_weekly | 30 | -11.7356 | -3.40526 | 239 | 1 | [-1.71596, -1.50545] |
| autotheta_weekly | 90 | -22.583 | -6.31146 | 259 | 1 | [-3.68399, -3.32755] |
| chronos2 | 7 | -0.124158 | -0.0215805 | 209 | 0.902311 | [0.0599954, 0.15162] |
| chronos2 | 30 | -0.0723791 | -0.0490478 | 239 | 0.909722 | [0.0743842, 0.133603] |
| chronos2 | 90 | -0.0981118 | -0.0619965 | 259 | 0.892261 | [0.0680234, 0.104907] |
| ets | 7 | -1.25214 | -0.167237 | 209 | 0.979271 | [-0.03939, 0.088659] |
| ets | 30 | -0.623673 | -0.191352 | 239 | 0.961793 | [-0.211934, -0.0541171] |
| ets | 90 | -0.750917 | -0.246413 | 259 | 0.962248 | [-0.43863, -0.0615686] |
| last_value | 7 | -1.90118 | -0.0444444 | 209 | 0.978714 | [-0.116868, 0.0233639] |
| last_value | 30 | -0.950799 | -0.0214249 | 239 | 0.958936 | [-0.269477, -0.128878] |
| last_value | 90 | -1.25176 | -0.000444444 | 259 | 0.944511 | [-0.491984, -0.129537] |
| lightgbm | 7 | -3.72295 | -0.534644 | 209 | 0.995645 | [-1.53546, -0.541449] |
| lightgbm | 30 | -2.07998 | -0.610767 | 239 | 1 | [-1.30098, -0.955898] |
| lightgbm | 90 | -2.92352 | -0.812877 | 259 | 1 | [-1.67893, -1.36954] |
| linear_30 | 7 | -1.07635 | -0.117042 | 209 | 0.831214 | [-0.844228, -0.0839781] |
| linear_30 | 30 | -1.27221 | -0.225054 | 239 | 0.951637 | [-2.60526, -0.224045] |
| linear_30 | 90 | -1.79062 | -0.550921 | 259 | 0.997255 | [-6.33241, -0.748606] |
| local_mean_14 | 7 | -0.0711051 | 0 | 209 | 0.819278 | [-0.0603989, 0.0139421] |
| local_mean_14 | 30 | -0.0692808 | -0.00551876 | 239 | 0.883302 | [-0.212923, 0.0352512] |
| local_mean_14 | 90 | -0.0327179 | -0.00685015 | 259 | 0.907483 | [-0.304574, 0.0334344] |
| local_mean_56 | 7 | 0.036656 | 0.00488669 | 209 | 0.595596 | [-0.131695, -0.0146071] |
| local_mean_56 | 30 | 0.0114299 | 0 | 239 | 0.731913 | [-0.0505062, 0.0150001] |
| local_mean_56 | 90 | 0.0112976 | 0 | 259 | 0.743476 | [0.00197536, 0.0291544] |
| local_mean_7 | 7 | -0.325694 | -0.0504202 | 209 | 0.889306 | [-0.92664, 0.00542478] |
| local_mean_7 | 30 | -0.162131 | -0.0388372 | 239 | 0.959506 | [-1.37024, 0.0301386] |
| local_mean_7 | 90 | -0.147064 | -0.0257031 | 259 | 0.969592 | [-1.5498, 0.0169061] |
| local_mean_90 | 7 | 0.0059336 | 0 | 209 | 0.457818 | [-0.217775, -0.0732459] |
| local_mean_90 | 30 | 0.0109806 | 0 | 239 | 0.708252 | [-0.0630941, -0.0169423] |
| local_mean_90 | 90 | 0.0107095 | 0 | 259 | 0.833097 | [-0.0132481, 0.0264229] |
| naive_seasonal | 7 | -2.55693 | -0.397516 | 209 | 0.970587 | [-1.73489, -0.130526] |
| naive_seasonal | 30 | -0.910652 | -0.549618 | 239 | 1 | [-1.04501, -0.401426] |
| naive_seasonal | 90 | -0.85374 | -0.752986 | 259 | NaN | [-0.589295, -0.349407] |
| nb_local_level_28 | 7 | -0.0371087 | 0 | 209 | 0.487092 | [-0.367809, -0.283735] |
| nb_local_level_28 | 30 | -0.0880147 | 0 | 239 | 0.540991 | [-0.241435, -0.18211] |
| nb_local_level_28 | 90 | -0.0589852 | 0 | 259 | 0.923025 | [-0.187639, -0.11049] |
| timesfm2p5 | 7 | -0.316992 | -0.0405212 | 209 | 0.942541 | [0.048958, 0.265283] |
| timesfm2p5 | 30 | -0.142649 | -0.0650454 | 239 | 0.942764 | [0.0726885, 0.202646] |
| timesfm2p5 | 90 | -0.23282 | -0.110654 | 259 | 0.884991 | [0.0461191, 0.119786] |
| timesfm3 | 7 | -0.0583838 | -0.00659916 | 209 | 0.932227 | [0.0659233, 0.279615] |
| timesfm3 | 30 | -0.0582294 | -0.0236717 | 239 | 0.928889 | [0.0827605, 0.202668] |
| timesfm3 | 90 | -1.37463 | -0.0569679 | 259 | 0.895171 | [0.0644616, 0.132588] |
| weekly_naive | 7 | -2.55443 | -0.382143 | 209 | 0.984732 | [-1.72635, -0.12971] |
| weekly_naive | 30 | -0.959868 | -0.351626 | 239 | 0.995439 | [-2.07551, -0.129898] |
| weekly_naive | 90 | -0.775118 | -0.326779 | 259 | 0.996992 | [-2.17937, -0.131007] |

[Full precision CSV](reports/registered-2026-09-13/descriptive/scale-local_mean_28.csv).

## Scale review against autoets_weekly

This is a declared secondary scale review, not a confirmatory test. Skill is 1-model/reference, undefined at reference zero; gain is reference-model. The top-five share divides the five largest positive repository gains by all positive gains; the range removes each repository in turn from the mean gain.

| Model | Horizon | Mean skill | Median skill | Defined skill (of 300) | Top-five positive-gain share | Leave-one-out mean-gain range |
| --- | --- | --- | --- | --- | --- | --- |
| autoarima_weekly | 7 | -0.123395 | -0.0129009 | 300 | 0.372894 | [-0.47555, -0.0560006] |
| autoarima_weekly | 30 | -0.375917 | -0.00221761 | 300 | 0.382442 | [0.039533, 0.331387] |
| autoarima_weekly | 90 | -1.38235 | 0.000493394 | 300 | 0.751618 | [-0.311458, 4.11806] |
| autotheta_weekly | 7 | 0.112793 | 0.0624894 | 300 | 0.275837 | [0.118951, 0.179185] |
| autotheta_weekly | 30 | 0.0741186 | 0.102601 | 300 | 0.306021 | [0.290809, 0.349001] |
| autotheta_weekly | 90 | -0.180944 | -0.00807606 | 300 | 0.941476 | [0.245321, 3.02417] |
| chronos2 | 7 | 0.736167 | 0.857145 | 300 | 0.269499 | [0.965086, 1.16495] |
| chronos2 | 30 | 0.738194 | 0.859433 | 300 | 0.288815 | [1.92785, 2.14326] |
| chronos2 | 90 | 0.761595 | 0.888529 | 300 | 0.603097 | [3.83174, 6.7531] |
| ets | 7 | 0.644524 | 0.755349 | 300 | 0.282434 | [0.904721, 1.06556] |
| ets | 30 | 0.665039 | 0.766584 | 300 | 0.302477 | [1.61322, 1.9642] |
| ets | 90 | 0.69681 | 0.804907 | 300 | 0.632791 | [3.32153, 6.39548] |
| last_value | 7 | 0.512578 | 0.807811 | 300 | 0.291549 | [0.835465, 0.988086] |
| last_value | 30 | 0.560468 | 0.811936 | 300 | 0.307925 | [1.55026, 1.88944] |
| last_value | 90 | 0.584242 | 0.858626 | 300 | 0.636062 | [3.26723, 6.32751] |
| lightgbm | 7 | 0.408531 | 0.653219 | 300 | 0.314046 | [-0.686598, 0.563504] |
| lightgbm | 30 | 0.43266 | 0.719724 | 300 | 0.334557 | [0.496962, 1.06242] |
| lightgbm | 90 | 0.393375 | 0.758323 | 300 | 0.669534 | [2.1583, 5.15457] |
| linear_30 | 7 | 0.643808 | 0.793818 | 300 | 0.293107 | [0.00313317, 1.02098] |
| linear_30 | 30 | 0.577012 | 0.788533 | 300 | 0.316861 | [-0.795222, 1.79427] |
| linear_30 | 90 | 0.425034 | 0.79852 | 300 | 0.653037 | [-2.56151, 5.70844] |
| local_mean_14 | 7 | 0.731669 | 0.863495 | 300 | 0.277916 | [0.792977, 1.1189] |
| local_mean_14 | 30 | 0.734614 | 0.857493 | 300 | 0.29844 | [1.61307, 2.05357] |
| local_mean_14 | 90 | 0.760264 | 0.885853 | 300 | 0.62651 | [3.46282, 6.49048] |
| local_mean_28 | 7 | 0.733026 | 0.861713 | 300 | 0.274845 | [0.828517, 1.10495] |
| local_mean_28 | 30 | 0.741408 | 0.86246 | 300 | 0.297179 | [1.79626, 2.03731] |
| local_mean_28 | 90 | 0.767459 | 0.894249 | 300 | 0.609176 | [3.73575, 6.66755] |
| local_mean_56 | 7 | 0.736387 | 0.87237 | 300 | 0.276635 | [0.702001, 1.09035] |
| local_mean_56 | 30 | 0.7446 | 0.866421 | 300 | 0.293672 | [1.76006, 2.03331] |
| local_mean_56 | 90 | 0.771467 | 0.88975 | 300 | 0.606261 | [3.76353, 6.68927] |
| local_mean_7 | 7 | 0.704137 | 0.849071 | 300 | 0.277548 | [-0.0613545, 1.11038] |
| local_mean_7 | 30 | 0.708012 | 0.848111 | 300 | 0.299373 | [0.476545, 2.04845] |
| local_mean_7 | 90 | 0.73417 | 0.879365 | 300 | 0.626746 | [2.23023, 6.47396] |
| local_mean_90 | 7 | 0.73018 | 0.867258 | 300 | 0.283979 | [0.612937, 1.03171] |
| local_mean_90 | 30 | 0.74284 | 0.871929 | 300 | 0.296667 | [1.74666, 2.00137] |
| local_mean_90 | 90 | 0.770623 | 0.890768 | 300 | 0.604641 | [3.76217, 6.69172] |
| naive_seasonal | 7 | 0.551355 | 0.735944 | 300 | 0.30088 | [-0.862706, 0.974428] |
| naive_seasonal | 30 | 0.574601 | 0.76144 | 300 | 0.324575 | [0.75229, 1.61689] |
| naive_seasonal | 90 | 0.616411 | 0.821008 | 300 | 0.649992 | [3.17129, 6.12107] |
| nb_local_level_28 | 7 | 0.701386 | 0.860962 | 300 | 0.294213 | [0.474699, 0.821218] |
| nb_local_level_28 | 30 | 0.721207 | 0.850709 | 300 | 0.315538 | [1.56855, 1.80981] |
| nb_local_level_28 | 90 | 0.758968 | 0.884654 | 300 | 0.611553 | [3.62526, 6.50288] |
| timesfm2p5 | 7 | 0.729124 | 0.850883 | 300 | 0.267527 | [1.0718, 1.18111] |
| timesfm2p5 | 30 | 0.731108 | 0.856709 | 300 | 0.295819 | [1.99737, 2.20291] |
| timesfm2p5 | 90 | 0.748105 | 0.876774 | 300 | 0.604353 | [3.85553, 6.77456] |
| timesfm3 | 7 | 0.740753 | 0.859954 | 300 | 0.265714 | [1.08662, 1.19607] |
| timesfm3 | 30 | 0.741591 | 0.855596 | 300 | 0.29204 | [1.99722, 2.2035] |
| timesfm3 | 90 | 0.727999 | 0.873144 | 300 | 0.604713 | [3.86396, 6.77877] |
| weekly_naive | 7 | 0.549787 | 0.733348 | 300 | 0.299455 | [-0.855064, 0.975243] |
| weekly_naive | 30 | 0.57442 | 0.799807 | 300 | 0.310917 | [-0.237801, 1.88842] |
| weekly_naive | 90 | 0.608618 | 0.849706 | 300 | 0.635214 | [1.59855, 6.32604] |

[Full precision CSV](reports/registered-2026-09-13/descriptive/scale-autoets_weekly.csv).

## Pooled QScore9

This is a declared secondary model summary, not a confirmatory test.

| Model | Horizon | Repositories | Windows | Mean QScore9 |
| --- | --- | --- | --- | --- |
| autoarima_weekly | 7 | 300 | 900 | 2.55138 |
| autoarima_weekly | 30 | 300 | 900 | 3.12138 |
| autoarima_weekly | 90 | 300 | 900 | 5.62336 |
| autoets_weekly | 7 | 300 | 900 | 2.09968 |
| autoets_weekly | 30 | 300 | 900 | 3.27173 |
| autoets_weekly | 90 | 300 | 900 | 8.15269 |
| autotheta_weekly | 7 | 300 | 900 | 1.965 |
| autotheta_weekly | 30 | 300 | 900 | 2.94422 |
| autotheta_weekly | 90 | 300 | 900 | 5.1846 |
| chronos2 | 7 | 300 | 900 | 1.03071 |
| chronos2 | 30 | 300 | 900 | 1.14498 |
| chronos2 | 90 | 300 | 900 | 1.42838 |
| ets | 7 | 300 | 900 | 1.09481 |
| ets | 30 | 300 | 900 | 1.4619 |
| ets | 90 | 300 | 900 | 1.93906 |
| last_value | 7 | 300 | 900 | 1.1634 |
| last_value | 30 | 300 | 900 | 1.52487 |
| last_value | 90 | 300 | 900 | 1.99446 |
| lightgbm | 7 | 300 | 900 | 2.67949 |
| lightgbm | 30 | 300 | 900 | 2.57355 |
| lightgbm | 90 | 300 | 900 | 3.20262 |
| linear_30 | 7 | 300 | 900 | 1.98953 |
| linear_30 | 30 | 300 | 900 | 3.85949 |
| linear_30 | 90 | 300 | 900 | 7.83707 |
| local_mean_14 | 7 | 300 | 900 | 1.20252 |
| local_mean_14 | 30 | 300 | 900 | 1.45884 |
| local_mean_14 | 90 | 300 | 900 | 1.79873 |
| local_mean_28 | 7 | 300 | 900 | 1.16762 |
| local_mean_28 | 30 | 300 | 900 | 1.27696 |
| local_mean_28 | 90 | 300 | 900 | 1.52981 |
| local_mean_56 | 7 | 300 | 900 | 1.29387 |
| local_mean_56 | 30 | 300 | 900 | 1.31286 |
| local_mean_56 | 90 | 300 | 900 | 1.50798 |
| local_mean_7 | 7 | 300 | 900 | 2.05399 |
| local_mean_7 | 30 | 300 | 900 | 2.59154 |
| local_mean_7 | 90 | 300 | 900 | 3.02335 |
| local_mean_90 | 7 | 300 | 900 | 1.38258 |
| local_mean_90 | 30 | 300 | 900 | 1.32623 |
| local_mean_90 | 90 | 300 | 900 | 1.5192 |
| naive_seasonal | 7 | 300 | 900 | 2.85342 |
| naive_seasonal | 30 | 300 | 900 | 2.31845 |
| naive_seasonal | 90 | 300 | 900 | 2.11714 |
| nb_local_level_28 | 7 | 300 | 900 | 1.53325 |
| nb_local_level_28 | 30 | 300 | 900 | 1.5168 |
| nb_local_level_28 | 90 | 300 | 900 | 1.70041 |
| timesfm2p5 | 7 | 300 | 900 | 0.92474 |
| timesfm2p5 | 30 | 300 | 900 | 1.07627 |
| timesfm2p5 | 90 | 300 | 900 | 1.41777 |
| timesfm3 | 7 | 300 | 900 | 0.909178 |
| timesfm3 | 30 | 300 | 900 | 1.07574 |
| timesfm3 | 90 | 300 | 900 | 1.40156 |
| weekly_naive | 7 | 300 | 900 | 2.84584 |
| weekly_naive | 30 | 300 | 900 | 3.30605 |
| weekly_naive | 90 | 300 | 900 | 3.65391 |

[Full precision CSV](reports/registered-2026-09-13/descriptive/qscore9-pooled.csv).

## QScore9 by sampling stratum

This is a declared secondary sampling stratum summary, not a confirmatory test.

| Sampling stratum | Model | Horizon | Repositories | Windows | Mean QScore9 |
| --- | --- | --- | --- | --- | --- |
| 100-999 | autoarima_weekly | 7 | 100 | 300 | 0.553875 |
| 100-999 | autoarima_weekly | 30 | 100 | 300 | 0.919064 |
| 100-999 | autoarima_weekly | 90 | 100 | 300 | 1.60746 |
| 100-999 | autoets_weekly | 7 | 100 | 300 | 0.542238 |
| 100-999 | autoets_weekly | 30 | 100 | 300 | 0.703178 |
| 100-999 | autoets_weekly | 90 | 100 | 300 | 0.967402 |
| 100-999 | autotheta_weekly | 7 | 100 | 300 | 0.492211 |
| 100-999 | autotheta_weekly | 30 | 100 | 300 | 0.625706 |
| 100-999 | autotheta_weekly | 90 | 100 | 300 | 0.982137 |
| 100-999 | chronos2 | 7 | 100 | 300 | 0.217424 |
| 100-999 | chronos2 | 30 | 100 | 300 | 0.217415 |
| 100-999 | chronos2 | 90 | 100 | 300 | 0.233084 |
| 100-999 | ets | 7 | 100 | 300 | 0.247922 |
| 100-999 | ets | 30 | 100 | 300 | 0.273867 |
| 100-999 | ets | 90 | 100 | 300 | 0.307453 |
| 100-999 | last_value | 7 | 100 | 300 | 0.311005 |
| 100-999 | last_value | 30 | 100 | 300 | 0.314356 |
| 100-999 | last_value | 90 | 100 | 300 | 0.335535 |
| 100-999 | lightgbm | 7 | 100 | 300 | 0.314643 |
| 100-999 | lightgbm | 30 | 100 | 300 | 0.404823 |
| 100-999 | lightgbm | 90 | 100 | 300 | 0.517287 |
| 100-999 | linear_30 | 7 | 100 | 300 | 0.242298 |
| 100-999 | linear_30 | 30 | 100 | 300 | 0.338185 |
| 100-999 | linear_30 | 90 | 100 | 300 | 0.538055 |
| 100-999 | local_mean_14 | 7 | 100 | 300 | 0.222097 |
| 100-999 | local_mean_14 | 30 | 100 | 300 | 0.22362 |
| 100-999 | local_mean_14 | 90 | 100 | 300 | 0.244866 |
| 100-999 | local_mean_28 | 7 | 100 | 300 | 0.227988 |
| 100-999 | local_mean_28 | 30 | 100 | 300 | 0.217143 |
| 100-999 | local_mean_28 | 90 | 100 | 300 | 0.235874 |
| 100-999 | local_mean_56 | 7 | 100 | 300 | 0.233867 |
| 100-999 | local_mean_56 | 30 | 100 | 300 | 0.217887 |
| 100-999 | local_mean_56 | 90 | 100 | 300 | 0.230351 |
| 100-999 | local_mean_7 | 7 | 100 | 300 | 0.227292 |
| 100-999 | local_mean_7 | 30 | 100 | 300 | 0.254042 |
| 100-999 | local_mean_7 | 90 | 100 | 300 | 0.290472 |
| 100-999 | local_mean_90 | 7 | 100 | 300 | 0.24765 |
| 100-999 | local_mean_90 | 30 | 100 | 300 | 0.227264 |
| 100-999 | local_mean_90 | 90 | 100 | 300 | 0.237114 |
| 100-999 | naive_seasonal | 7 | 100 | 300 | 0.302359 |
| 100-999 | naive_seasonal | 30 | 100 | 300 | 0.343073 |
| 100-999 | naive_seasonal | 90 | 100 | 300 | 0.359456 |
| 100-999 | nb_local_level_28 | 7 | 100 | 300 | 0.263534 |
| 100-999 | nb_local_level_28 | 30 | 100 | 300 | 0.244037 |
| 100-999 | nb_local_level_28 | 90 | 100 | 300 | 0.248156 |
| 100-999 | timesfm2p5 | 7 | 100 | 300 | 0.22553 |
| 100-999 | timesfm2p5 | 30 | 100 | 300 | 0.22121 |
| 100-999 | timesfm2p5 | 90 | 100 | 300 | 0.235087 |
| 100-999 | timesfm3 | 7 | 100 | 300 | 0.218731 |
| 100-999 | timesfm3 | 30 | 100 | 300 | 0.214982 |
| 100-999 | timesfm3 | 90 | 100 | 300 | 0.230538 |
| 100-999 | weekly_naive | 7 | 100 | 300 | 0.30152 |
| 100-999 | weekly_naive | 30 | 100 | 300 | 0.341931 |
| 100-999 | weekly_naive | 90 | 100 | 300 | 0.375343 |
| 1000+ | autoarima_weekly | 7 | 100 | 300 | 6.95443 |
| 1000+ | autoarima_weekly | 30 | 100 | 300 | 8.27456 |
| 1000+ | autoarima_weekly | 90 | 100 | 300 | 15.0432 |
| 1000+ | autoets_weekly | 7 | 100 | 300 | 5.60889 |
| 1000+ | autoets_weekly | 30 | 100 | 300 | 8.9496 |
| 1000+ | autoets_weekly | 90 | 100 | 300 | 23.3013 |
| 1000+ | autotheta_weekly | 7 | 100 | 300 | 5.26504 |
| 1000+ | autotheta_weekly | 30 | 100 | 300 | 8.06081 |
| 1000+ | autotheta_weekly | 90 | 100 | 300 | 14.3916 |
| 1000+ | chronos2 | 7 | 100 | 300 | 2.79785 |
| 1000+ | chronos2 | 30 | 100 | 300 | 3.13386 |
| 1000+ | chronos2 | 90 | 100 | 300 | 3.96615 |
| 1000+ | ets | 7 | 100 | 300 | 2.93949 |
| 1000+ | ets | 30 | 100 | 300 | 4.01232 |
| 1000+ | ets | 90 | 100 | 300 | 5.40602 |
| 1000+ | last_value | 7 | 100 | 300 | 3.0536 |
| 1000+ | last_value | 30 | 100 | 300 | 4.13131 |
| 1000+ | last_value | 90 | 100 | 300 | 5.52114 |
| 1000+ | lightgbm | 7 | 100 | 300 | 7.54624 |
| 1000+ | lightgbm | 30 | 100 | 300 | 7.14637 |
| 1000+ | lightgbm | 90 | 100 | 300 | 8.9106 |
| 1000+ | linear_30 | 7 | 100 | 300 | 5.6154 |
| 1000+ | linear_30 | 30 | 100 | 300 | 11.1072 |
| 1000+ | linear_30 | 90 | 100 | 300 | 22.763 |
| 1000+ | local_mean_14 | 7 | 100 | 300 | 3.30803 |
| 1000+ | local_mean_14 | 30 | 100 | 300 | 4.07014 |
| 1000+ | local_mean_14 | 90 | 100 | 300 | 5.06545 |
| 1000+ | local_mean_28 | 7 | 100 | 300 | 3.19955 |
| 1000+ | local_mean_28 | 30 | 100 | 300 | 3.53138 |
| 1000+ | local_mean_28 | 90 | 100 | 300 | 4.27041 |
| 1000+ | local_mean_56 | 7 | 100 | 300 | 3.57223 |
| 1000+ | local_mean_56 | 30 | 100 | 300 | 3.63808 |
| 1000+ | local_mean_56 | 90 | 100 | 300 | 4.20985 |
| 1000+ | local_mean_7 | 7 | 100 | 300 | 5.85107 |
| 1000+ | local_mean_7 | 30 | 100 | 300 | 7.4349 |
| 1000+ | local_mean_7 | 90 | 100 | 300 | 8.69094 |
| 1000+ | local_mean_90 | 7 | 100 | 300 | 3.82172 |
| 1000+ | local_mean_90 | 30 | 100 | 300 | 3.66691 |
| 1000+ | local_mean_90 | 90 | 100 | 300 | 4.23544 |
| 1000+ | naive_seasonal | 7 | 100 | 300 | 8.13462 |
| 1000+ | naive_seasonal | 30 | 100 | 300 | 6.48134 |
| 1000+ | naive_seasonal | 90 | 100 | 300 | 5.85676 |
| 1000+ | nb_local_level_28 | 7 | 100 | 300 | 4.25436 |
| 1000+ | nb_local_level_28 | 30 | 100 | 300 | 4.2191 |
| 1000+ | nb_local_level_28 | 90 | 100 | 300 | 4.7659 |
| 1000+ | timesfm2p5 | 7 | 100 | 300 | 2.46961 |
| 1000+ | timesfm2p5 | 30 | 100 | 300 | 2.92275 |
| 1000+ | timesfm2p5 | 90 | 100 | 300 | 3.92997 |
| 1000+ | timesfm3 | 7 | 100 | 300 | 2.43193 |
| 1000+ | timesfm3 | 30 | 100 | 300 | 2.92869 |
| 1000+ | timesfm3 | 90 | 100 | 300 | 3.87355 |
| 1000+ | weekly_naive | 7 | 100 | 300 | 8.11222 |
| 1000+ | weekly_naive | 30 | 100 | 300 | 9.45121 |
| 1000+ | weekly_naive | 90 | 100 | 300 | 10.4587 |
| 20-99 | autoarima_weekly | 7 | 100 | 300 | 0.145819 |
| 20-99 | autoarima_weekly | 30 | 100 | 300 | 0.170524 |
| 20-99 | autoarima_weekly | 90 | 100 | 300 | 0.219469 |
| 20-99 | autoets_weekly | 7 | 100 | 300 | 0.147904 |
| 20-99 | autoets_weekly | 30 | 100 | 300 | 0.162406 |
| 20-99 | autoets_weekly | 90 | 100 | 300 | 0.189329 |
| 20-99 | autotheta_weekly | 7 | 100 | 300 | 0.137759 |
| 20-99 | autotheta_weekly | 30 | 100 | 300 | 0.146128 |
| 20-99 | autotheta_weekly | 90 | 100 | 300 | 0.18008 |
| 20-99 | chronos2 | 7 | 100 | 300 | 0.0768574 |
| 20-99 | chronos2 | 30 | 100 | 300 | 0.0836519 |
| 20-99 | chronos2 | 90 | 100 | 300 | 0.0858898 |
| 20-99 | ets | 7 | 100 | 300 | 0.0970136 |
| 20-99 | ets | 30 | 100 | 300 | 0.0995191 |
| 20-99 | ets | 90 | 100 | 300 | 0.103717 |
| 20-99 | last_value | 7 | 100 | 300 | 0.12561 |
| 20-99 | last_value | 30 | 100 | 300 | 0.128942 |
| 20-99 | last_value | 90 | 100 | 300 | 0.126694 |
| 20-99 | lightgbm | 7 | 100 | 300 | 0.177594 |
| 20-99 | lightgbm | 30 | 100 | 300 | 0.169465 |
| 20-99 | lightgbm | 90 | 100 | 300 | 0.179991 |
| 20-99 | linear_30 | 7 | 100 | 300 | 0.110885 |
| 20-99 | linear_30 | 30 | 100 | 300 | 0.133096 |
| 20-99 | linear_30 | 90 | 100 | 300 | 0.210147 |
| 20-99 | local_mean_14 | 7 | 100 | 300 | 0.0774286 |
| 20-99 | local_mean_14 | 30 | 100 | 300 | 0.0827489 |
| 20-99 | local_mean_14 | 90 | 100 | 300 | 0.0858582 |
| 20-99 | local_mean_28 | 7 | 100 | 300 | 0.0753143 |
| 20-99 | local_mean_28 | 30 | 100 | 300 | 0.0823509 |
| 20-99 | local_mean_28 | 90 | 100 | 300 | 0.0831501 |
| 20-99 | local_mean_56 | 7 | 100 | 300 | 0.0755026 |
| 20-99 | local_mean_56 | 30 | 100 | 300 | 0.0826074 |
| 20-99 | local_mean_56 | 90 | 100 | 300 | 0.0837493 |
| 20-99 | local_mean_7 | 7 | 100 | 300 | 0.0835968 |
| 20-99 | local_mean_7 | 30 | 100 | 300 | 0.0856709 |
| 20-99 | local_mean_7 | 90 | 100 | 300 | 0.0886487 |
| 20-99 | local_mean_90 | 7 | 100 | 300 | 0.0783577 |
| 20-99 | local_mean_90 | 30 | 100 | 300 | 0.0845138 |
| 20-99 | local_mean_90 | 90 | 100 | 300 | 0.0850447 |
| 20-99 | naive_seasonal | 7 | 100 | 300 | 0.123289 |
| 20-99 | naive_seasonal | 30 | 100 | 300 | 0.130948 |
| 20-99 | naive_seasonal | 90 | 100 | 300 | 0.135211 |
| 20-99 | nb_local_level_28 | 7 | 100 | 300 | 0.0818624 |
| 20-99 | nb_local_level_28 | 30 | 100 | 300 | 0.0872716 |
| 20-99 | nb_local_level_28 | 90 | 100 | 300 | 0.0871852 |
| 20-99 | timesfm2p5 | 7 | 100 | 300 | 0.0790825 |
| 20-99 | timesfm2p5 | 30 | 100 | 300 | 0.084846 |
| 20-99 | timesfm2p5 | 90 | 100 | 300 | 0.0882616 |
| 20-99 | timesfm3 | 7 | 100 | 300 | 0.0768765 |
| 20-99 | timesfm3 | 30 | 100 | 300 | 0.0835443 |
| 20-99 | timesfm3 | 90 | 100 | 300 | 0.100586 |
| 20-99 | weekly_naive | 7 | 100 | 300 | 0.123772 |
| 20-99 | weekly_naive | 30 | 100 | 300 | 0.125022 |
| 20-99 | weekly_naive | 90 | 100 | 300 | 0.127667 |

[Full precision CSV](reports/registered-2026-09-13/descriptive/qscore9-sampling_stratum.csv).

## QScore9 by regime

This is a declared secondary regime summary, not a confirmatory test.

| Regime | Model | Horizon | Repositories | Windows | Mean QScore9 |
| --- | --- | --- | --- | --- | --- |
| Inactive recently | autoarima_weekly | 7 | 140 | 320 | 0.390735 |
| Inactive recently | autoarima_weekly | 30 | 140 | 320 | 0.754992 |
| Inactive recently | autoarima_weekly | 90 | 140 | 320 | 1.48206 |
| Inactive recently | autoets_weekly | 7 | 140 | 320 | 0.287847 |
| Inactive recently | autoets_weekly | 30 | 140 | 320 | 0.457045 |
| Inactive recently | autoets_weekly | 90 | 140 | 320 | 0.725765 |
| Inactive recently | autotheta_weekly | 7 | 140 | 320 | 0.191135 |
| Inactive recently | autotheta_weekly | 30 | 140 | 320 | 0.295477 |
| Inactive recently | autotheta_weekly | 90 | 140 | 320 | 0.561388 |
| Inactive recently | chronos2 | 7 | 140 | 320 | 0.0180201 |
| Inactive recently | chronos2 | 30 | 140 | 320 | 0.0248574 |
| Inactive recently | chronos2 | 90 | 140 | 320 | 0.0464875 |
| Inactive recently | ets | 7 | 140 | 320 | 0.028336 |
| Inactive recently | ets | 30 | 140 | 320 | 0.0345136 |
| Inactive recently | ets | 90 | 140 | 320 | 0.0556662 |
| Inactive recently | last_value | 7 | 140 | 320 | 0.0160839 |
| Inactive recently | last_value | 30 | 140 | 320 | 0.0230868 |
| Inactive recently | last_value | 90 | 140 | 320 | 0.0444949 |
| Inactive recently | lightgbm | 7 | 140 | 320 | 0.0456781 |
| Inactive recently | lightgbm | 30 | 140 | 320 | 0.0544352 |
| Inactive recently | lightgbm | 90 | 140 | 320 | 0.0807288 |
| Inactive recently | linear_30 | 7 | 140 | 320 | 0.016309 |
| Inactive recently | linear_30 | 30 | 140 | 320 | 0.0231944 |
| Inactive recently | linear_30 | 90 | 140 | 320 | 0.0447043 |
| Inactive recently | local_mean_14 | 7 | 140 | 320 | 0.0161565 |
| Inactive recently | local_mean_14 | 30 | 140 | 320 | 0.0230556 |
| Inactive recently | local_mean_14 | 90 | 140 | 320 | 0.0445899 |
| Inactive recently | local_mean_28 | 7 | 140 | 320 | 0.0161565 |
| Inactive recently | local_mean_28 | 30 | 140 | 320 | 0.0230556 |
| Inactive recently | local_mean_28 | 90 | 140 | 320 | 0.0445899 |
| Inactive recently | local_mean_56 | 7 | 140 | 320 | 0.0164512 |
| Inactive recently | local_mean_56 | 30 | 140 | 320 | 0.023079 |
| Inactive recently | local_mean_56 | 90 | 140 | 320 | 0.044559 |
| Inactive recently | local_mean_7 | 7 | 140 | 320 | 0.0161565 |
| Inactive recently | local_mean_7 | 30 | 140 | 320 | 0.0230556 |
| Inactive recently | local_mean_7 | 90 | 140 | 320 | 0.0445899 |
| Inactive recently | local_mean_90 | 7 | 140 | 320 | 0.0162336 |
| Inactive recently | local_mean_90 | 30 | 140 | 320 | 0.023114 |
| Inactive recently | local_mean_90 | 90 | 140 | 320 | 0.0444731 |
| Inactive recently | naive_seasonal | 7 | 140 | 320 | 0.0163885 |
| Inactive recently | naive_seasonal | 30 | 140 | 320 | 0.0252209 |
| Inactive recently | naive_seasonal | 90 | 140 | 320 | 0.0578106 |
| Inactive recently | nb_local_level_28 | 7 | 140 | 320 | 0.0161565 |
| Inactive recently | nb_local_level_28 | 30 | 140 | 320 | 0.0230556 |
| Inactive recently | nb_local_level_28 | 90 | 140 | 320 | 0.0445899 |
| Inactive recently | timesfm2p5 | 7 | 140 | 320 | 0.0192478 |
| Inactive recently | timesfm2p5 | 30 | 140 | 320 | 0.0264948 |
| Inactive recently | timesfm2p5 | 90 | 140 | 320 | 0.0488423 |
| Inactive recently | timesfm3 | 7 | 140 | 320 | 0.0174374 |
| Inactive recently | timesfm3 | 30 | 140 | 320 | 0.0245473 |
| Inactive recently | timesfm3 | 90 | 140 | 320 | 0.0560053 |
| Inactive recently | weekly_naive | 7 | 140 | 320 | 0.0163991 |
| Inactive recently | weekly_naive | 30 | 140 | 320 | 0.023022 |
| Inactive recently | weekly_naive | 90 | 140 | 320 | 0.0445395 |
| Other active | autoarima_weekly | 7 | 228 | 572 | 2.31186 |
| Other active | autoarima_weekly | 30 | 228 | 572 | 3.53134 |
| Other active | autoarima_weekly | 90 | 228 | 572 | 7.03609 |
| Other active | autoets_weekly | 7 | 228 | 572 | 2.28953 |
| Other active | autoets_weekly | 30 | 228 | 572 | 3.79219 |
| Other active | autoets_weekly | 90 | 228 | 572 | 10.1585 |
| Other active | autotheta_weekly | 7 | 228 | 572 | 2.10493 |
| Other active | autotheta_weekly | 30 | 228 | 572 | 3.37942 |
| Other active | autotheta_weekly | 90 | 228 | 572 | 6.23127 |
| Other active | chronos2 | 7 | 228 | 572 | 0.703836 |
| Other active | chronos2 | 30 | 228 | 572 | 1.07324 |
| Other active | chronos2 | 90 | 228 | 572 | 1.57272 |
| Other active | ets | 7 | 228 | 572 | 0.877714 |
| Other active | ets | 30 | 228 | 572 | 1.20548 |
| Other active | ets | 90 | 228 | 572 | 1.68253 |
| Other active | last_value | 7 | 228 | 572 | 0.98144 |
| Other active | last_value | 30 | 228 | 572 | 1.30585 |
| Other active | last_value | 90 | 228 | 572 | 1.77315 |
| Other active | lightgbm | 7 | 228 | 572 | 2.95995 |
| Other active | lightgbm | 30 | 228 | 572 | 2.76408 |
| Other active | lightgbm | 90 | 228 | 572 | 3.7588 |
| Other active | linear_30 | 7 | 228 | 572 | 0.853796 |
| Other active | linear_30 | 30 | 228 | 572 | 1.34437 |
| Other active | linear_30 | 90 | 228 | 572 | 2.35569 |
| Other active | local_mean_14 | 7 | 228 | 572 | 0.743872 |
| Other active | local_mean_14 | 30 | 228 | 572 | 1.13877 |
| Other active | local_mean_14 | 90 | 228 | 572 | 1.6186 |
| Other active | local_mean_28 | 7 | 228 | 572 | 0.763125 |
| Other active | local_mean_28 | 30 | 228 | 572 | 1.20692 |
| Other active | local_mean_28 | 90 | 228 | 572 | 1.6887 |
| Other active | local_mean_56 | 7 | 228 | 572 | 0.784311 |
| Other active | local_mean_56 | 30 | 228 | 572 | 1.19707 |
| Other active | local_mean_56 | 90 | 228 | 572 | 1.68201 |
| Other active | local_mean_7 | 7 | 228 | 572 | 0.735055 |
| Other active | local_mean_7 | 30 | 228 | 572 | 1.09566 |
| Other active | local_mean_7 | 90 | 228 | 572 | 1.57816 |
| Other active | local_mean_90 | 7 | 228 | 572 | 0.864026 |
| Other active | local_mean_90 | 30 | 228 | 572 | 1.24135 |
| Other active | local_mean_90 | 90 | 228 | 572 | 1.72474 |
| Other active | naive_seasonal | 7 | 228 | 572 | 0.901257 |
| Other active | naive_seasonal | 30 | 228 | 572 | 1.71216 |
| Other active | naive_seasonal | 90 | 228 | 572 | 2.29072 |
| Other active | nb_local_level_28 | 7 | 228 | 572 | 1.15496 |
| Other active | nb_local_level_28 | 30 | 228 | 572 | 1.5307 |
| Other active | nb_local_level_28 | 90 | 228 | 572 | 1.9642 |
| Other active | timesfm2p5 | 7 | 228 | 572 | 0.718913 |
| Other active | timesfm2p5 | 30 | 228 | 572 | 1.08936 |
| Other active | timesfm2p5 | 90 | 228 | 572 | 1.60951 |
| Other active | timesfm3 | 7 | 228 | 572 | 0.704108 |
| Other active | timesfm3 | 30 | 228 | 572 | 1.07151 |
| Other active | timesfm3 | 90 | 228 | 572 | 1.57488 |
| Other active | weekly_naive | 7 | 228 | 572 | 0.900092 |
| Other active | weekly_naive | 30 | 228 | 572 | 1.27517 |
| Other active | weekly_naive | 90 | 228 | 572 | 1.73233 |
| Recent surge | autoarima_weekly | 7 | 7 | 8 | 101.869 |
| Recent surge | autoarima_weekly | 30 | 7 | 8 | 62.2656 |
| Recent surge | autoarima_weekly | 90 | 7 | 8 | 52.7117 |
| Recent surge | autoets_weekly | 7 | 7 | 8 | 47.2867 |
| Recent surge | autoets_weekly | 30 | 7 | 8 | 56.4007 |
| Recent surge | autoets_weekly | 90 | 7 | 8 | 72.3745 |
| Recent surge | autotheta_weekly | 7 | 7 | 8 | 48.4951 |
| Recent surge | autotheta_weekly | 30 | 7 | 8 | 55.7052 |
| Recent surge | autotheta_weekly | 90 | 7 | 8 | 76.0523 |
| Recent surge | chronos2 | 7 | 7 | 8 | 64.7332 |
| Recent surge | chronos2 | 30 | 7 | 8 | 52.1819 |
| Recent surge | chronos2 | 90 | 7 | 8 | 49.9818 |
| Recent surge | ets | 7 | 7 | 8 | 58.51 |
| Recent surge | ets | 30 | 7 | 8 | 80.1653 |
| Recent surge | ets | 90 | 7 | 8 | 104.482 |
| Recent surge | last_value | 7 | 7 | 8 | 58.4321 |
| Recent surge | last_value | 30 | 7 | 8 | 80.3802 |
| Recent surge | last_value | 90 | 7 | 8 | 104.768 |
| Recent surge | lightgbm | 7 | 7 | 8 | 107.145 |
| Recent surge | lightgbm | 30 | 7 | 8 | 85.3867 |
| Recent surge | lightgbm | 90 | 7 | 8 | 73.997 |
| Recent surge | linear_30 | 7 | 7 | 8 | 173.916 |
| Recent surge | linear_30 | 30 | 7 | 8 | 375.064 |
| Recent surge | linear_30 | 90 | 7 | 8 | 797.785 |
| Recent surge | local_mean_14 | 7 | 7 | 8 | 82.5413 |
| Recent surge | local_mean_14 | 30 | 7 | 8 | 86.9143 |
| Recent surge | local_mean_14 | 90 | 7 | 8 | 93.5369 |
| Recent surge | local_mean_28 | 7 | 7 | 8 | 76.182 |
| Recent surge | local_mean_28 | 30 | 7 | 8 | 57.2964 |
| Recent surge | local_mean_28 | 90 | 7 | 8 | 52.6016 |
| Recent surge | local_mean_56 | 7 | 7 | 8 | 90.5009 |
| Recent surge | local_mean_56 | 30 | 7 | 8 | 63.1891 |
| Recent surge | local_mean_56 | 90 | 7 | 8 | 50.8813 |
| Recent surge | local_mean_7 | 7 | 7 | 8 | 193.088 |
| Recent surge | local_mean_7 | 30 | 7 | 8 | 236.05 |
| Recent surge | local_mean_7 | 90 | 7 | 8 | 253.882 |
| Recent surge | local_mean_90 | 7 | 7 | 8 | 94.4447 |
| Recent surge | local_mean_90 | 30 | 7 | 8 | 60.7843 |
| Recent surge | local_mean_90 | 90 | 7 | 8 | 48.4022 |
| Recent surge | naive_seasonal | 7 | 7 | 8 | 281.242 |
| Recent surge | naive_seasonal | 30 | 7 | 8 | 142.573 |
| Recent surge | naive_seasonal | 90 | 7 | 8 | 75.0659 |
| Recent surge | nb_local_level_28 | 7 | 7 | 8 | 85.7481 |
| Recent surge | nb_local_level_28 | 30 | 7 | 8 | 57.4937 |
| Recent surge | nb_local_level_28 | 90 | 7 | 8 | 48.7511 |
| Recent surge | timesfm2p5 | 7 | 7 | 8 | 49.5653 |
| Recent surge | timesfm2p5 | 30 | 7 | 8 | 42.2001 |
| Recent surge | timesfm2p5 | 90 | 7 | 8 | 45.2489 |
| Recent surge | timesfm3 | 7 | 7 | 8 | 49.2686 |
| Recent surge | timesfm3 | 30 | 7 | 8 | 43.7741 |
| Recent surge | timesfm3 | 90 | 7 | 8 | 45.9187 |
| Recent surge | weekly_naive | 7 | 7 | 8 | 280.347 |
| Recent surge | weekly_naive | 30 | 7 | 8 | 311.333 |
| Recent surge | weekly_naive | 90 | 7 | 8 | 320.773 |

[Full precision CSV](reports/registered-2026-09-13/descriptive/qscore9-regime.csv).

## Local-mean lookback grid

This is the declared secondary lookback sensitivity table, not a confirmatory test.

| Lookback (days) | Model | Horizon | Repositories | Windows | Mean QScore9 |
| --- | --- | --- | --- | --- | --- |
| 7 | local_mean_7 | 7 | 300 | 900 | 2.05399 |
| 7 | local_mean_7 | 30 | 300 | 900 | 2.59154 |
| 7 | local_mean_7 | 90 | 300 | 900 | 3.02335 |
| 14 | local_mean_14 | 7 | 300 | 900 | 1.20252 |
| 14 | local_mean_14 | 30 | 300 | 900 | 1.45884 |
| 14 | local_mean_14 | 90 | 300 | 900 | 1.79873 |
| 28 | local_mean_28 | 7 | 300 | 900 | 1.16762 |
| 28 | local_mean_28 | 30 | 300 | 900 | 1.27696 |
| 28 | local_mean_28 | 90 | 300 | 900 | 1.52981 |
| 56 | local_mean_56 | 7 | 300 | 900 | 1.29387 |
| 56 | local_mean_56 | 30 | 300 | 900 | 1.31286 |
| 56 | local_mean_56 | 90 | 300 | 900 | 1.50798 |
| 90 | local_mean_90 | 7 | 300 | 900 | 1.38258 |
| 90 | local_mean_90 | 30 | 300 | 900 | 1.32623 |
| 90 | local_mean_90 | 90 | 300 | 900 | 1.5192 |

[Full precision CSV](reports/registered-2026-09-13/descriptive/local-mean-lookbacks.csv).

## Calibration coverage

This is a declared secondary calibration summary, not a confirmatory test. coverage_80 is inclusive coverage of the saved repaired 0.1-0.9 quantiles, averaged within repository and then across repositories.

| Model | Horizon | coverage_80 | Valid repositories | Windows | Valid windows |
| --- | --- | --- | --- | --- | --- |
| autoarima_weekly | 7 | 0.986349 | 300 | 900 | 900 |
| autoarima_weekly | 30 | 0.984556 | 300 | 900 | 900 |
| autoarima_weekly | 90 | 0.985358 | 300 | 900 | 900 |
| autoets_weekly | 7 | 0.987143 | 300 | 900 | 900 |
| autoets_weekly | 30 | 0.986481 | 300 | 900 | 900 |
| autoets_weekly | 90 | 0.987926 | 300 | 900 | 900 |
| autotheta_weekly | 7 | 0.98381 | 300 | 900 | 900 |
| autotheta_weekly | 30 | 0.985185 | 300 | 900 | 900 |
| autotheta_weekly | 90 | 0.98821 | 300 | 900 | 900 |
| chronos2 | 7 | 0.831905 | 300 | 900 | 900 |
| chronos2 | 30 | 0.824296 | 300 | 900 | 900 |
| chronos2 | 90 | 0.837272 | 300 | 900 | 900 |
| ets | 7 | 0.696349 | 300 | 900 | 900 |
| ets | 30 | 0.690259 | 300 | 900 | 900 |
| ets | 90 | 0.686148 | 300 | 900 | 900 |
| last_value | 7 | 0.911111 | 300 | 900 | 900 |
| last_value | 30 | 0.906778 | 300 | 900 | 900 |
| last_value | 90 | 0.901877 | 300 | 900 | 900 |
| lightgbm | 7 | 0.633333 | 300 | 900 | 900 |
| lightgbm | 30 | 0.608704 | 300 | 900 | 900 |
| lightgbm | 90 | 0.58321 | 300 | 900 | 900 |
| linear_30 | 7 | 0.709524 | 300 | 900 | 900 |
| linear_30 | 30 | 0.689148 | 300 | 900 | 900 |
| linear_30 | 90 | 0.666568 | 300 | 900 | 900 |
| local_mean_14 | 7 | 0.947143 | 300 | 900 | 900 |
| local_mean_14 | 30 | 0.939778 | 300 | 900 | 900 |
| local_mean_14 | 90 | 0.934 | 300 | 900 | 900 |
| local_mean_28 | 7 | 0.954921 | 300 | 900 | 900 |
| local_mean_28 | 30 | 0.945481 | 300 | 900 | 900 |
| local_mean_28 | 90 | 0.940617 | 300 | 900 | 900 |
| local_mean_56 | 7 | 0.955714 | 300 | 900 | 900 |
| local_mean_56 | 30 | 0.949889 | 300 | 900 | 900 |
| local_mean_56 | 90 | 0.946494 | 300 | 900 | 900 |
| local_mean_7 | 7 | 0.94381 | 300 | 900 | 900 |
| local_mean_7 | 30 | 0.937333 | 300 | 900 | 900 |
| local_mean_7 | 90 | 0.932037 | 300 | 900 | 900 |
| local_mean_90 | 7 | 0.953333 | 300 | 900 | 900 |
| local_mean_90 | 30 | 0.952037 | 300 | 900 | 900 |
| local_mean_90 | 90 | 0.947407 | 300 | 900 | 900 |
| naive_seasonal | 7 | 0.92254 | 300 | 900 | 900 |
| naive_seasonal | 30 | 0.913296 | 300 | 900 | 900 |
| naive_seasonal | 90 | 0.908111 | 300 | 900 | 900 |
| nb_local_level_28 | 7 | 0.942063 | 300 | 900 | 900 |
| nb_local_level_28 | 30 | 0.938148 | 300 | 900 | 900 |
| nb_local_level_28 | 90 | 0.938667 | 300 | 900 | 900 |
| timesfm2p5 | 7 | 0.923968 | 300 | 900 | 900 |
| timesfm2p5 | 30 | 0.905852 | 300 | 900 | 900 |
| timesfm2p5 | 90 | 0.918284 | 300 | 900 | 900 |
| timesfm3 | 7 | 0.88 | 300 | 900 | 900 |
| timesfm3 | 30 | 0.909852 | 300 | 900 | 900 |
| timesfm3 | 90 | 0.888988 | 300 | 900 | 900 |
| weekly_naive | 7 | 0.927302 | 300 | 900 | 900 |
| weekly_naive | 30 | 0.923074 | 300 | 900 | 900 |
| weekly_naive | 90 | 0.917889 | 300 | 900 | 900 |

[Full precision CSV](reports/registered-2026-09-13/descriptive/calibration.csv).

## AutoETS interval coverage and specifications

Coverage is a declared secondary calibration summary, not a confirmatory test; the specification counts are a secondary diagnostic requested after the run. Each saved repository/cutoff/horizon row is a separate fit.

| Sampling stratum | Horizon | coverage_80 | Valid windows | Fits | Multiplicative-seasonality fits |
| --- | --- | --- | --- | --- | --- |
| 100-999 | 7 | 0.991429 | 300 | 300 | 0 |
| 100-999 | 30 | 0.988111 | 300 | 300 | 0 |
| 100-999 | 90 | 0.988704 | 300 | 300 | 0 |
| 1000+ | 7 | 0.991429 | 300 | 300 | 6 |
| 1000+ | 30 | 0.993667 | 300 | 300 | 6 |
| 1000+ | 90 | 0.99463 | 300 | 300 | 6 |
| 20-99 | 7 | 0.978571 | 300 | 300 | 0 |
| 20-99 | 30 | 0.977667 | 300 | 300 | 0 |
| 20-99 | 90 | 0.980444 | 300 | 300 | 0 |

[Full precision CSV](reports/registered-2026-09-13/descriptive/autoets-coverage.csv).

## AutoETS 90-day interval widths

This secondary interval-width diagnostic was requested after the run within the declared secondary calibration analysis; it is not a confirmatory test. The daily median pools all 90 target days of all fits in the stratum; the fit-mean median first averages q0.9-q0.1 over each fit's 90 days. Both use saved intervals after clipping and crossing repair.

| Sampling stratum | 90-day fits | Forecast days | Median daily 80% width | Median fit-mean 80% width |
| --- | --- | --- | --- | --- |
| 100-999 | 300 | 27000 | 3.60224 | 3.70748 |
| 1000+ | 300 | 27000 | 49.6888 | 55.9901 |
| 20-99 | 300 | 27000 | 0.793402 | 0.800171 |

[Full precision CSV](reports/registered-2026-09-13/descriptive/autoets-widths-90.csv).

[Execution evidence](reports/registered-2026-09-13/execution-summary.json),
[signed readiness](reports/registered-2026-09-13/evidence/readiness.json),
[full inference table](reports/registered-2026-09-13/inference/inference.csv),
[paired scores](reports/registered-2026-09-13/inference/paired_repositories.csv),
[descriptive provenance](reports/registered-2026-09-13/descriptive/provenance.json).

Regenerate this document and its descriptive CSVs from the saved release asset
without refitting or recomputing confirmatory tests:

```powershell
.\.venv\Scripts\python.exe reports/registered-2026-09-13/summarize_descriptives.py
```

Release asset location and SHA-256 are documented in README.md. Raw captures,
weights and duplicate recovery checkpoints are excluded from the tree.

<!-- BEGIN POST-HOC QSCORE9 ACCOUNTING -->
## Post-hoc QScore9 accounting (2026-09-14)

This post-hoc diagnostic partitions each saved QScore9 into zero-day, positive-day overprediction and positive-day underprediction contributions, each divided by the full horizon. All 48,600 rows satisfy the accounting identity to floating-point tolerance; the 18 original mean differences are reproduced without changing their tests.

Windows are averaged within repository, then repositories receive equal weight. Empty conditional partitions remain undefined; their unconditional contributions are zero. Outcome-sorted cumulative curves and context scatters are post-hoc descriptions.

[Post-hoc paired tables](reports/registered-2026-09-13/posthoc/posthoc-paired-summary.csv), [post-hoc figure index and regeneration](reports/registered-2026-09-13/posthoc/posthoc-report.md), [post-hoc provenance](reports/registered-2026-09-13/posthoc/provenance.json).
<!-- END POST-HOC QSCORE9 ACCOUNTING -->

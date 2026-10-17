r"""POST HOC, DESCRIPTIVE: intermittent-demand baselines and the fourth cell, from saved forecasts.

Usage, from the repository root:
    .\.venv\Scripts\python.exe
        reports\study2-posthoc-intermittent-baselines\intermittent_baselines.py
        --npm reports\study2-npm\run-2026-10-15 --grid reports\study2-synthetic-2026-10-15
        --nyc311 reports\study3-nyc311\run-2026-10-17 [--out <new directory>] [--workers N]

The specification is SPEC.md beside this script, fixed and hashed before any score below existed;
the command refuses to run if its bytes differ. Everything here is post hoc and descriptive: no
test is added to any registered family, no multiplicity correction is applied, no verdict is drawn.
No model is loaded and nothing is refitted to a target; every reference score is the run's saved
one, every new forecast is built from the context through its origin, and no file under any run
directory changes.

- tsb_hurdle (and the sensitivities tsb_hurdle_a005, tsb_hurdle_a020): TSB's occurrence level
  p_t = a d_t + (1 - a) p_(t-1) over every context day and size level z_j = a s_j + (1 - a) z_(j-1)
  over the positive days, each started at its first value (statsforecast's initialization), held
  flat over the horizon, with the registered count hurdle's positive law 1 + Poisson(max(0, z - 1)).
- croston_classic, croston_sba, adida: statsforecast 2.1.1's point forecasts, scored as a point
  mass at floor(f + 0.5).
- <model>_occurrence_model_size_count on npm and the grid: pulsegraph.study2.models.model_size_count
  on the saved completed and hurdle_count_28 laws, as Study 3 registered it; on NYC 311 its
  contrasts are the run's own declared secondaries, read from the run's inference files.
- Scores by pulsegraph.study2.scores.score, the registered scorer; aggregation, interval and test by
  the functions of scripts/study2_inference.py and scripts/study3_inference.py, imported unchanged.
  Bootstrap seeds: pulsegraph.random.derived_seed(20261017, panel, id, group, variant, reference,
  horizon, metric), id = <group>/<variant>/<reference>/h<horizon>.

Writes, beside the script unless --out names another directory, for each panel (npm, grid,
nyc311): <panel>_window_scores.csv, <panel>_contrasts.csv, <panel>_occurrence.csv; and
provenance.json with the hash of every input, output, the specification and this script. Refuses
to overwrite any of them. Prints the Markdown tables of RESULTS-intermittent-baselines.md.
"""

import argparse
import io
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from statsforecast.models import ADIDA, TSB, CrostonClassic, CrostonSBA

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.evaluation.registration import installed_versions
from pulsegraph.provenance import read_json, sha256_bytes
from pulsegraph.random import derived_seed
from pulsegraph.study2.constants import CUTOFFS, MODEL_PINS, STUDY3_FILES
from pulsegraph.study2.declarations import validate, validate_study3
from pulsegraph.study2.distributions import CountLaw
from pulsegraph.study2.holdout import utc_now
from pulsegraph.study2.models import count_laws, law_forecast, model_size_count
from pulsegraph.study2.runner import external_dataset
from pulsegraph.study2.scores import score
from pulsegraph.study2.synthetic import grid_dataset

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
import scripts.study2_inference as study2  # noqa: E402
import scripts.study3_inference as study3  # noqa: E402

HERE = Path(__file__).resolve().parent
SPEC = HERE / "SPEC.md"
SPEC_SHA256 = "ca645c02a2576cff174d42a4d2d2089242423d32063ea1cdad39078168687532"
SPEC_FIXED_AT = "2026-10-17 07:44 UTC"
SEED_ROOT = 20261017
PANELS = ("npm", "grid", "nyc311")
COMPONENT = dict(npm="external_packages", grid="synthetic", nyc311="study3")
DOMAIN = dict(npm="packages", grid="synthetic", nyc311="nyc311")
GROUP = dict(npm="stratum", grid="cell_id", nyc311="stratum")
ALL = "all"
HORIZONS = (7, 30)
METRICS = study2.SECONDARY_METRICS
PARTS = study2.PARTS
VALUES = [*METRICS, *PARTS]
SMOOTHING = dict(tsb_hurdle=0.1, tsb_hurdle_a005=0.05, tsb_hurdle_a020=0.2)
TSB_NAMES = tuple(SMOOTHING)
PRIMARY = "tsb_hurdle"
POINT = dict(croston_classic=CrostonClassic, croston_sba=CrostonSBA, adida=ADIDA)
FOURTH = "_occurrence_model_size_count"
COUNT, DYNAMIC = "hurdle_count_28", "dynamic_count"
MINIMUM_SERIES = 10
TOLERANCE = 1e-12
POSTHOC, RUNS_OWN = "post hoc", "the run's own declared secondary"
STATUS = (
    "post hoc and descriptive; specified in SPEC.md (SHA-256 "
    + SPEC_SHA256
    + ") at "
    + SPEC_FIXED_AT
    + ", after the registered scores of all three runs were seen and before any score here "
    "existed; no registered status; adds no test to any registered family; no multiplicity "
    "correction; replaces nothing registered"
)
CODE = (
    "scripts/study2_inference.py",
    "scripts/study3_inference.py",
    "pulsegraph/study2/distributions.py",
    "pulsegraph/study2/models.py",
    "pulsegraph/study2/scores.py",
    "pulsegraph/study2/runner.py",
    "pulsegraph/study2/synthetic.py",
)
TABLES = ("window_scores.csv", "contrasts.csv", "occurrence.csv")


# The forecasts -----------------------------------------------------------------------------------


def ses_level(values, alpha):
    """Simple exponential smoothing as statsforecast does it: the level starts at the first value
    and l_t = alpha x_t + (1 - alpha) l_(t-1) after it; the forecast is the last level."""
    level = float(values[0])
    for value in values[1:]:
        level = alpha * float(value) + (1 - alpha) * level
    return level


def tsb_levels(context, alpha_p, alpha_z):
    """TSB's occurrence level over every context day and size level over the positive days.

    Returns (p, z); z is None when the context has no positive day, and p is then 0."""
    y = np.asarray(context, dtype=float)
    positive = y[y > 0]
    if not len(positive):
        return 0.0, None
    return ses_level((y > 0).astype(float), alpha_p), ses_level(positive, alpha_z)


def tsb_law(p, lam):
    """The registered count hurdle's form with occurrence p and positive law 1 + Poisson(lam);
    lam None (no positive context day) gives the point mass at zero."""
    if lam is None:
        if p != 0:
            raise ValueError("A context without a positive day has occurrence zero")
        return CountLaw(
            dict(
                kind="hurdle",
                p=0.0,
                positive=dict(kind="point", value=1),
                fallback="no_positive_context_day",
            )
        )
    return CountLaw(
        dict(
            kind="hurdle",
            p=float(p),
            positive=dict(kind="poisson", mu=float(lam), shift=1),
            fallback=None,
        )
    )


def tsb_hurdle(context, alpha):
    """The TSB hurdle with both smoothing constants equal to alpha: (law, p, z)."""
    p, z = tsb_levels(context, alpha, alpha)
    return tsb_law(p, None if z is None else max(0.0, z - 1)), p, z


def statsforecast_tsb(context, alpha, horizon):
    return TSB(alpha_d=alpha, alpha_p=alpha).forecast(
        y=np.asarray(context, dtype=float), h=horizon
    )["mean"]


def point_method(name, context, horizon):
    """A field point method's flat forecast f and the count c = floor(f + 0.5) it is scored at."""
    mean = POINT[name]().forecast(y=np.asarray(context, dtype=float), h=horizon)["mean"]
    if len(mean) != horizon or not np.isfinite(mean).all() or len(set(mean.tolist())) != 1:
        raise ValueError(f"{name} did not return one finite flat forecast")
    f = float(mean[0])
    return f, int(np.floor(f + 0.5))


def fourth_cell(completed, count):
    """The fourth factorial cell for one target day: Study 3's model_size_count on saved specs."""
    return model_size_count(CountLaw(completed), count)


def flat_forecast(law, horizon, metadata=None):
    """law_forecast([law] * horizon), with the one law inverted once."""
    one = law_forecast([law], metadata)
    return dict(
        deciles=one["deciles"] * horizon,
        distributions=one["distributions"] * horizon,
        metadata=one["metadata"],
    )


def context_and_target(panel, series, cutoff, horizon):
    """The window as the runner cut it (pulsegraph.study2.runner._evaluate)."""
    if panel == "grid":
        cutoff = int(cutoff)
        return series.iloc[:cutoff], series.iloc[cutoff : cutoff + 30].iloc[:horizon]
    context = series.loc[series.index < cutoff]
    target = series.loc[
        (series.index >= cutoff) & (series.index < pd.Timestamp(cutoff) + pd.Timedelta(days=30))
    ]
    return context, target.iloc[:horizon]


def _scored(name, forecast, target, context, **extra):
    result = score(target, forecast, context)
    return dict(
        model=name,
        **{metric: result[metric] for metric in METRICS},
        crps_unavailable_reason=result["crps_unavailable_reason"],
        residual=result["residual"],
        n_zero=result["n_zero"],
        n_positive=result["n_positive"],
        **{part: result["contributions"][part] for part in PARTS},
        **extra,
    )


def series_windows(panel, run, label, expected, identity, series, origins):
    """Every new forecast's windows for one series, after the checks of SPEC.md.

    Returns (rows, descriptors): one row per window and new forecast, one per window."""
    path = Path(run) / (sha256_bytes(label.encode()) + ".json")
    if file_hash(path) != expected:
        raise ValueError(f"Checkpoint hash mismatch: {label}")
    document = read_json(path)
    if document.get("identity") != identity:
        raise ValueError("Checkpoint belongs to a different run")
    saved = {(r["cutoff"], int(r["horizon"]), r["model"]): r for r in document["rows"]}
    rows, descriptors = [], []
    for cutoff in origins:
        for horizon in HORIZONS:
            context, target = context_and_target(panel, series, cutoff, horizon)
            mine = [r for (c, h, _), r in saved.items() if (c, h) == (cutoff, horizon)]
            if not mine:
                raise ValueError("A registered window is missing")
            y, target = context.to_numpy(), target.tolist()
            for row in mine:
                if row["context_mean"] != float(context.mean()):
                    raise ValueError(f"Rebuilt context differs from the saved one: {label}")
                if [float(v) for v in row["target"]] != [float(v) for v in target]:
                    raise ValueError(f"Rebuilt target differs from the saved one: {label}")
            for name in (COUNT, DYNAMIC):
                rebuilt = [law.spec for law in count_laws(name, y, horizon)]
                if rebuilt != saved[(cutoff, horizon, name)]["forecast"]["distributions"]:
                    raise ValueError(f"{name} is not reproduced from the rebuilt context: {label}")
            count_specs = saved[(cutoff, horizon, COUNT)]["forecast"]["distributions"]
            key = dict(series_id=mine[0]["series_id"], cutoff=cutoff, horizon=horizon)
            descriptor = dict(
                key,
                context_all_zero=bool(not np.any(y > 0)),
                positive_target_fraction=float(np.mean(np.asarray(target) > 0)),
                jeffreys_p=float(count_specs[0]["p"]),
                dynamic_p=float(
                    CountLaw(saved[(cutoff, horizon, DYNAMIC)]["forecast"]["distributions"][0]).sf(
                        0
                    )
                ),
            )
            for name, alpha in SMOOTHING.items():
                law, p, z = tsb_hurdle(y, alpha)
                reference = statsforecast_tsb(y, alpha, horizon)
                product = 0.0 if z is None else p * z
                if not np.allclose(reference, product, rtol=TOLERANCE, atol=TOLERANCE):
                    raise ValueError("The TSB recursions differ from statsforecast's TSB forecast")
                descriptor[f"{name}_p"] = p
                forecast = flat_forecast(law, horizon, dict(alpha_p=alpha, alpha_z=alpha))
                rows.append(
                    dict(
                        key,
                        **_scored(
                            name,
                            forecast,
                            target,
                            y,
                            occurrence_p=p,
                            size_level=z,
                            positive_mu=law.spec["positive"].get("mu"),
                            point_forecast=product,
                            statsforecast_point=float(reference[0]),
                            point_value=None,
                            fallback=law.spec["fallback"],
                        ),
                    )
                )
            for name in POINT:
                f, c = point_method(name, y, horizon)
                law = CountLaw(dict(kind="point", value=c))
                rows.append(
                    dict(
                        key,
                        **_scored(
                            name,
                            flat_forecast(law, horizon),
                            target,
                            y,
                            occurrence_p=float(c > 0),
                            size_level=None,
                            positive_mu=None,
                            point_forecast=f,
                            statsforecast_point=f,
                            point_value=c,
                            fallback=None,
                        ),
                    )
                )
            for model in MODEL_PINS:
                completed = saved[(cutoff, horizon, f"{model}_completed")]["forecast"]
                laws = [CountLaw(s) for s in completed["distributions"]]
                zero_mass = [float(law.sf(0)) for law in laws]
                descriptor[f"{model}_completed_p"] = float(np.mean(zero_mass))
                descriptor[f"{model}_all_zero_decile_days"] = int(
                    sum(max(day) == 0 for day in completed["deciles"])
                )
                cells = [
                    fourth_cell(c, k)
                    for c, k in zip(completed["distributions"], count_specs, strict=True)
                ]
                name = model + FOURTH
                if panel == "nyc311":
                    if [cell.spec for cell in cells] != saved[(cutoff, horizon, name)]["forecast"][
                        "distributions"
                    ]:
                        raise ValueError("A saved fourth-cell law is not rebuilt from saved laws")
                    continue
                rows.append(
                    dict(
                        key,
                        **_scored(
                            name,
                            law_forecast(cells),
                            target,
                            y,
                            occurrence_p=zero_mass[0],
                            size_level=None,
                            positive_mu=count_specs[0]["positive"].get("mu"),
                            point_forecast=None,
                            statsforecast_point=None,
                            point_value=None,
                            fallback=count_specs[0]["fallback"],
                        ),
                    )
                )
            descriptors.append(descriptor)
    return rows, descriptors


def _windows_job(arguments):
    return series_windows(*arguments)


# The run, its checks and the contrasts ------------------------------------------------------------


def read_panel(panel, run, root):
    """The registered reader and the byte-for-byte reproduction of the registered family."""
    run, root = Path(run), Path(root)
    provenance = read_json(run / "inference" / "provenance.json")
    if file_hash(Path(study2.__file__)) != provenance.get(
        "inference_script_sha256" if panel != "nyc311" else "study2_functions_sha256"
    ):
        raise ValueError("scripts/study2_inference.py differs from the run's inference")
    if panel == "nyc311":
        if file_hash(Path(study3.__file__)) != provenance["inference_script_sha256"]:
            raise ValueError("scripts/study3_inference.py differs from the run's inference")
        spec_path, comparisons = (root / name for name in STUDY3_FILES)
        spec, family = read_json(spec_path), read_json(comparisons)
        validate_study3(spec, family)
        state, _, frame, _, checkpoints = study3.read_run(run, family, spec, root)
        series = study2.series_scores(frame, study3.VALUES)
        entities = study3.stratum_entities(series)
        sizes = series.reset_index().drop_duplicates("series_id").stratum.value_counts()
        sizes = {s: int(sizes.get(s, 0)) for s in study3.STUDY3_STRATA}
        registered, pairs = study3.family_table(family, entities, sizes)
    else:
        component = COMPONENT[panel]
        comparisons = root / f"study/study2/{component}_comparisons.json"
        spec_path = root / f"study/study2/{component}_spec.json"
        family, spec = read_json(comparisons), read_json(spec_path)
        if validate(spec, family) != component or family["component"] != component:
            raise ValueError("The comparison file is not this component's registered family")
        state, frame, _, checkpoints = study2.read_run(component, run, family, spec, root)
        series = study2.series_scores(frame, [study2.METRIC])
        entities = study2.entity_scores(component, series, [study2.METRIC])
        registered, pairs = study2.confirmatory(component, family, entities)
    reproduced = {
        name: csv_text(table).encode("utf-8") == (run / "inference" / name).read_bytes()
        for name, table in (("inference.csv", registered), ("paired_entities.csv", pairs))
    }
    if not all(reproduced.values()):
        raise ValueError(f"The saved scores do not reproduce the registered family: {reproduced}")
    declarations = {
        _relative(path, root): file_hash(path) for path in (Path(spec_path), Path(comparisons))
    }
    return state, frame, checkpoints, reproduced, declarations, provenance


def load_dataset(panel, state, root=ROOT_DIR):
    """The run's own series: the external loader on the saved readiness record, or the grid."""
    if panel == "grid":
        return grid_dataset()
    return external_dataset(state["metadata"]["readiness"], root=root)


def entities_of(panel, series):
    """Series means indexed by group, horizon, model and entity, the pooled group under 'all'."""
    if panel != "grid":
        return study3.stratum_entities(series)
    flat = series.reset_index()
    cells = flat.set_index(["cell_id", "horizon", "model", "series_id"])[VALUES]
    pooled = study2.entity_scores("synthetic", series, VALUES).reset_index()
    pooled["series_id"] = pooled.replicate.map(lambda r: f"rep{int(r):02}")
    pooled["cell_id"] = ALL
    pooled = pooled.set_index(["cell_id", "horizon", "model", "series_id"])[VALUES]
    return pd.concat([cells, pooled]).sort_index()


def references(panel):
    """The TSB hurdle's references, in table order."""
    names = [f"{m}_completed" for m in MODEL_PINS] + [f"{m}_hurdle" for m in MODEL_PINS]
    if panel == "nyc311":
        names += [f"{m}_hurdle_dynamic" for m in MODEL_PINS]
    return names + [COUNT, DYNAMIC]


def contrast_items(panel, groups):
    """Every contrast of SPEC.md for one panel: (kind, group, variant, reference, horizon)."""
    items = []
    for group in groups:
        for horizon in HORIZONS:
            for name in TSB_NAMES:
                items += [("tsb", group, name, ref, horizon) for ref in references(panel)]
            if panel != "nyc311":
                for model in MODEL_PINS:
                    for ref in (f"{model}_completed", COUNT):
                        items.append(("fourth", group, model + FOURTH, ref, horizon))
            point_references = [f"{m}_completed" for m in MODEL_PINS] + [COUNT, DYNAMIC, PRIMARY]
            for name in POINT:
                items += [("point", group, name, ref, horizon) for ref in point_references]
    return items


def _sign(value):
    return "negative" if value < 0 else "positive" if value > 0 else "zero"


def contrasts(panel, entities, items, sizes):
    rows = []
    for kind, group, variant, reference, horizon in items:
        for metric in METRICS:
            pair = study2.paired(entities, variant, reference, horizon, metric, (group,))
            available = pair.dropna()
            cid = f"{group}/{variant}/{reference}/h{horizon}"
            row = dict(
                panel=panel,
                source=POSTHOC,
                kind=kind,
                id=cid,
                group=group,
                group_series=sizes[group],
                below_ten_series=sizes[group] < MINIMUM_SERIES,
                variant=variant,
                reference=reference,
                horizon=horizon,
                metric=metric,
                entity="replicate" if panel == "grid" and group == ALL else "series",
                n_entities_unavailable=len(pair) - len(available),
            )
            if len(available) >= 2:
                diff = (available.model_score - available.reference_score).to_numpy()
                seed = derived_seed(
                    SEED_ROOT, panel, cid, group, variant, reference, int(horizon), metric
                )
                result = study2.cluster_contrast(diff, seed=seed, family=study3.FAMILY_SETTINGS)
                row.update(
                    status="descriptive",
                    variant_mean=float(available.model_score.mean()),
                    reference_mean=float(available.reference_score.mean()),
                    **result,
                    median_sign=_sign(result["median_diff"]),
                    bootstrap_root=SEED_ROOT,
                    bootstrap_seed=seed,
                )
            else:
                row.update(
                    status="unavailable" if not len(available) else "fewer_than_two_entities",
                    n_entities=len(available),
                )
            rows.append(row)
    return pd.DataFrame(rows)


def runs_own_rows(run, provenance):
    """NYC 311's fourth-cell contrasts as the run's inference wrote them, after its hashes."""
    parts = []
    for name in ("secondary_strata_contrasts.csv", "secondary_pooled_contrasts.csv"):
        path = Path(run) / "inference" / name
        if file_hash(path) != provenance["artifact_sha256"][name]:
            raise ValueError(f"The run's {name} differs from its provenance")
        table = pd.read_csv(
            path, keep_default_na=False, na_values=[""], float_precision="round_trip"
        )
        mine = table.variant.str.endswith(FOURTH) & (
            table.reference.eq(table.variant.str.replace(FOURTH, "_completed", regex=False))
            | table.reference.eq(COUNT)
        )
        parts.append(table[mine])
    table = pd.concat(parts, ignore_index=True).rename(columns=dict(stratum="group"))
    table.insert(0, "kind", "fourth")
    table.insert(0, "source", RUNS_OWN)
    table.insert(0, "panel", "nyc311")
    table["bootstrap_root"] = 20261004
    return table


def occurrence_table(panel, descriptors, labels, sizes):
    group = GROUP[panel]
    frame = descriptors.join(labels, on="series_id")
    rows = []
    for name in [ALL, *sorted(frame[group].unique())]:
        part = frame if name == ALL else frame[frame[group].eq(name)]
        for horizon, block in part.groupby("horizon", sort=True):
            row = dict(
                group=name,
                group_series=sizes[name],
                horizon=int(horizon),
                windows=len(block),
                context_all_zero_windows=int(block.context_all_zero.sum()),
                mean_positive_target_fraction=float(block.positive_target_fraction.mean()),
                **{f"mean_{n}_p": float(block[f"{n}_p"].mean()) for n in TSB_NAMES},
                mean_jeffreys_p=float(block.jeffreys_p.mean()),
                mean_dynamic_p=float(block.dynamic_p.mean()),
            )
            for model in MODEL_PINS:
                row[f"mean_{model}_completed_p"] = float(block[f"{model}_completed_p"].mean())
                row[f"{model}_all_zero_decile_day_share"] = float(
                    block[f"{model}_all_zero_decile_days"].sum() / (len(block) * horizon)
                )
            rows.append(row)
    return pd.DataFrame(rows)


def run_panel(panel, run, *, root=ROOT_DIR, dataset=None, workers=1):
    """Verify one run, build and score the new forecasts, and compute every contrast."""
    run, root = Path(run), Path(root)
    state, frame, checkpoints, reproduced, declarations, provenance = read_panel(panel, run, root)
    dataset = load_dataset(panel, state, root) if dataset is None else dataset
    keyed = {json.dumps(list(key), separators=(",", ":")): value for key, value in dataset.items()}
    if set(keyed) != set(checkpoints) or any(json.loads(k)[0] != DOMAIN[panel] for k in keyed):
        raise ValueError("The rebuilt series are not the run's checkpoints")
    origins = study2.ORIGINS["synthetic"] if panel == "grid" else list(CUTOFFS)
    jobs = [
        (panel, str(run), label, checkpoints[label], state["identity"], keyed[label], origins)
        for label in sorted(checkpoints)
    ]
    started = perf_counter()
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(_windows_job, jobs, chunksize=4))
    else:
        results = [_windows_job(job) for job in jobs]
    seconds = perf_counter() - started
    windows = pd.DataFrame([row for rows, _ in results for row in rows])
    descriptors = pd.DataFrame([row for _, rows in results for row in rows])
    for column in ("occurrence_brier", "discrete_crps"):
        windows[column] = pd.to_numeric(windows[column], errors="raise").astype(float)
    labelled = [c for c in ("stratum", "cell_id", "replicate") if c in frame.columns]
    labels = frame.drop_duplicates("series_id").set_index("series_id")[labelled]
    windows = windows.join(labels, on="series_id")
    order = ["series_id", "cutoff", "horizon", "model"]
    windows = windows.sort_values(order, kind="stable").reset_index(drop=True)
    descriptors = descriptors.sort_values(order[:3], kind="stable").reset_index(drop=True)
    new = len(TSB_NAMES) + len(POINT) + (0 if panel == "nyc311" else len(MODEL_PINS))
    expected = len(checkpoints) * len(origins) * len(HORIZONS)
    if (
        len(windows) != expected * new
        or len(descriptors) != expected
        or windows.duplicated(order).any()
    ):
        raise ValueError("The new forecasts' windows are not the registered grid")

    columns = ["series_id", "cutoff", "horizon", "model", *VALUES, *labelled]
    combined = pd.concat([frame[columns], windows[columns]], ignore_index=True)
    series = study2.series_scores(combined, VALUES)
    entities = entities_of(panel, series)
    group = GROUP[panel]
    counts = labels[group].value_counts()
    sizes = {name: int(n) for name, n in counts.items()}
    sizes[ALL] = len(labels) if panel != "grid" else labels.replicate.nunique()
    groups = [ALL, *sorted(counts.index)]
    table = contrasts(panel, entities, contrast_items(panel, groups), sizes)
    if panel == "nyc311":
        own = runs_own_rows(run, provenance)
        if len(own) != len(groups) * len(MODEL_PINS) * 2 * len(HORIZONS) * len(METRICS):
            raise ValueError("The run's own fourth-cell rows are not one per group and contrast")
        own["group_series"] = own.group.map(sizes)
        own["below_ten_series"] = own.group_series < MINIMUM_SERIES
        table = pd.concat([table, own[[c for c in table.columns if c in own.columns]]])
        table = table.reset_index(drop=True)
    checks = dict(
        registered_family_reproduced_byte_for_byte=reproduced,
        checkpoints_verified=len(checkpoints),
        windows=expected,
        contexts_targets_and_count_laws_reproduced=expected,
        tsb_recursions_equal_statsforecast=expected * len(TSB_NAMES),
        context_all_zero_windows=int(descriptors.context_all_zero.sum()),
        saved_fourth_cell_laws_rebuilt=expected * len(MODEL_PINS) if panel == "nyc311" else 0,
        new_forecast_windows=len(windows),
        crps_unavailable_windows=int(windows.discrete_crps.isna().sum()),
        max_abs_accounting_residual=float(windows.residual.abs().max()),
        largest_tsb_relative_gap=float(
            (
                (windows.point_forecast - windows.statsforecast_point).abs()
                / windows.statsforecast_point.abs().clip(lower=1e-300)
            )[windows.model.isin(TSB_NAMES) & windows.statsforecast_point.ne(0)].max()
        ),
        window_seconds=seconds,
        workers=workers,
    )
    readiness = state["metadata"].get("readiness", {})
    inputs = dict(
        directory=_relative(run, root),
        run_json_sha256=file_hash(run / "run.json"),
        identity=state["identity"],
        implementation_commit=state["metadata"].get("metadata", {}).get("implementation_commit"),
        declarations=declarations,
        inference_files_read={
            name: file_hash(run / "inference" / name)
            for name in (
                "inference.csv",
                "paired_entities.csv",
                "provenance.json",
                *(
                    ("secondary_strata_contrasts.csv", "secondary_pooled_contrasts.csv")
                    if panel == "nyc311"
                    else ()
                ),
            )
        },
        readiness_panels=readiness.get("panels"),
        checkpoints=len(checkpoints),
        checkpoint_sha256=checkpoints,
    )
    if panel == "grid":
        manifest = root / "study/study2/grid_manifest.json"
        inputs["grid_manifest"] = dict(path=_relative(manifest, root), sha256=file_hash(manifest))
    tables = {
        "window_scores.csv": windows,
        "contrasts.csv": table,
        "occurrence.csv": occurrence_table(panel, descriptors, labels, sizes),
    }
    return dict(tables=tables, checks=checks, inputs=inputs, sizes=sizes)


# Outputs ------------------------------------------------------------------------------------------


def csv_text(table):
    """A table as the inference commands write it."""
    buffer = io.StringIO()
    study2._integers(table.copy()).to_csv(buffer, index=False, lineterminator="\n")
    return buffer.getvalue()


def _relative(path, root):
    try:
        return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


def run_all(runs, *, out, root=ROOT_DIR, datasets=None, workers=1, command=None):
    """Every panel, every check, then the outputs; nothing is written unless every check passes."""
    if file_hash(SPEC) != SPEC_SHA256:
        raise ValueError("SPEC.md differs from the specification fixed before any score")
    out, datasets = Path(out), datasets or {}
    names = [f"{panel}_{t}" for panel in runs for t in TABLES] + ["provenance.json"]
    for name in names:
        if (out / name).exists():
            raise FileExistsError("refusing to overwrite " + str(out / name))
    started, clock = utc_now(), perf_counter()
    results = {
        panel: run_panel(panel, run, root=root, dataset=datasets.get(panel), workers=workers)
        for panel, run in runs.items()
    }
    out.mkdir(parents=True, exist_ok=True)
    for panel, result in results.items():
        for name, table in result["tables"].items():
            path = out / f"{panel}_{name}"
            path.write_text(csv_text(table), encoding="utf-8", newline="\n")
    versions = installed_versions()
    script = Path(__file__).resolve()
    study2._write_json(
        out / "provenance.json",
        dict(
            analysis="posthoc_intermittent_baselines",
            status=STATUS,
            specification=dict(
                path=_relative(SPEC, ROOT_DIR), sha256=file_hash(SPEC), fixed_at=SPEC_FIXED_AT
            ),
            started_at=started.isoformat(),
            written_at=utc_now().isoformat(),
            wall_seconds=perf_counter() - clock,
            command=command,
            regeneration=(
                r".\.venv\Scripts\python.exe reports\study2-posthoc-intermittent-baselines"
                r"\intermittent_baselines.py --npm reports\study2-npm\run-2026-10-15 --grid "
                r"reports\study2-synthetic-2026-10-15 --nyc311 reports\study3-nyc311"
                r"\run-2026-10-17 --out <new directory>"
            ),
            script=dict(path=_relative(script, ROOT_DIR), sha256=file_hash(script)),
            code_sha256={name: file_hash(ROOT_DIR / name) for name in CODE},
            head=study2._git("rev-parse", "HEAD"),
            uncommitted_changes=study2._git("status", "--porcelain", "--", "scripts", "pulsegraph"),
            packages={
                name: versions.get(name) for name in ("numpy", "scipy", "pandas", "statsforecast")
            },
            forecasts=dict(
                tsb_hurdle=(
                    "p_1 = d_1, p_t = a d_t + (1 - a) p_(t-1) over every context day; z_1 = s_1, "
                    "z_j = a s_j + (1 - a) z_(j-1) over the positive days; flat; H(0) = 1 - p_T, "
                    "H(k) = 1 - p_T + p_T G(k), G = 1 + Poisson(max(0, z_m - 1)); point mass at "
                    "zero when the context has no positive day"
                ),
                smoothing=SMOOTHING,
                point_methods="statsforecast 2.1.1 CrostonClassic, CrostonSBA, ADIDA with their "
                "defaults; scored as a point mass at floor(f + 0.5)",
                fourth_cell="pulsegraph.study2.models.model_size_count(saved completed law, saved "
                "hurdle_count_28 law), per target day",
            ),
            inference=dict(
                functions="scripts/study2_inference.py: read_run, series_scores, entity_scores, "
                "paired, cluster_contrast, confirmatory; scripts/study3_inference.py: read_run, "
                "stratum_entities, family_table, FAMILY_SETTINGS",
                bootstrap_seeds="pulsegraph.random.derived_seed(20261017, panel, id, group, "
                "variant, reference, horizon, metric), "
                "id = <group>/<variant>/<reference>/h<horizon>",
                test="two-sided approximate Wilcoxon signed-rank, zero differences omitted, p = 1 "
                "when every difference is zero; raw p only",
                adjustment="none",
            ),
            runs={
                panel: dict(r["inputs"], checks=r["checks"], group_series=r["sizes"])
                for panel, r in results.items()
            },
            outputs={name: file_hash(out / name) for name in names[:-1]},
        ),
    )
    return results


# The tables of the results page -------------------------------------------------------------------


def g(x, d=4):
    if x is None or pd.isna(x):
        return ""
    if x == 0:
        return "0"
    return f"{x:,.0f}" if abs(x) >= 10000 else f"{x:.{d}g}"


def p(x):
    return "" if pd.isna(x) else f"{x:.3g}"


def _counts(r):
    return f"{int(r.wins)} / {int(r.ties)} / {int(r.losses)}"


def _full(r):
    """Both summaries, the interval and the raw p of one contrast row."""
    if r.status not in ("descriptive", "secondary"):
        return "unavailable"
    n = "" if not r.n_entities_unavailable else f"n {int(r.n_entities)}: "
    return (
        f"{n}{g(r.mean_diff)} [{g(r.mean_diff_ci_low)}, {g(r.mean_diff_ci_high)}]; "
        f"median {g(r.median_diff)}; {_counts(r)}; p {p(r.wilcoxon_p)}"
    )


def _compact(r):
    if r.status not in ("descriptive", "secondary"):
        return "unavailable"
    return f"{g(r.mean_diff)} / {g(r.median_diff)} ({_counts(r)})"


def _group_label(r):
    mark = " †" if r.below_ten_series else ""
    return f"{r.group} (n = {int(r.group_series)}){mark}"


def _lookup(table):
    keys = ["group", "variant", "reference", "horizon", "metric"]
    return table.set_index(keys, drop=False).sort_index()


def full_table(table, variant, refs, groups, metrics=METRICS):
    """One row per group, horizon and reference; one column per score with both summaries."""
    names = dict(
        qscore9="QScore9",
        context_scaled_qscore9="Context-scaled QScore9",
        occurrence_brier="Occurrence Brier",
        discrete_crps="Discrete CRPS",
    )
    lines = [
        "| Group | h | Reference | " + " | ".join(names[m] for m in metrics) + " |",
        "|---|---|---|" + "---|" * len(metrics),
    ]
    rows = _lookup(table)
    for group in groups:
        for horizon in HORIZONS:
            for ref in refs:
                cells = [rows.loc[(group, variant, ref, horizon, m)] for m in metrics]
                lines.append(
                    f"| {_group_label(cells[0])} | {horizon} | `{ref}` | "
                    + " | ".join(_full(c) for c in cells)
                    + " |"
                )
    return "\n".join(lines)


def fourth_table(table, groups, metrics=METRICS):
    names = dict(
        qscore9="QScore9",
        context_scaled_qscore9="Context-scaled QScore9",
        occurrence_brier="Occurrence Brier",
        discrete_crps="Discrete CRPS",
    )
    lines = [
        "| Group | h | Variant | Reference | Source | "
        + " | ".join(names[m] for m in metrics)
        + " |",
        "|---|---|---|---|---|" + "---|" * len(metrics),
    ]
    rows = _lookup(table[table.kind.eq("fourth")])
    for group in groups:
        for horizon in HORIZONS:
            for model in MODEL_PINS:
                for ref in (f"{model}_completed", COUNT):
                    cells = [rows.loc[(group, model + FOURTH, ref, horizon, m)] for m in metrics]
                    source = "run's own" if cells[0].source == RUNS_OWN else "post hoc"
                    lines.append(
                        f"| {_group_label(cells[0])} | {horizon} | `{model + FOURTH}` | `{ref}` "
                        f"| {source} | " + " | ".join(_full(c) for c in cells) + " |"
                    )
    return "\n".join(lines)


def compact_table(table, variants, refs, groups, metric="qscore9"):
    """Variants as columns: mean / median (lower / tied / higher) for one score."""
    rows = _lookup(table)
    lines = [
        "| Group | h | Reference | " + " | ".join(f"`{v}`" for v in variants) + " |",
        "|---|---|---|" + "---|" * len(variants),
    ]
    for group in groups:
        for horizon in HORIZONS:
            for ref in refs:
                cells = [rows.loc[(group, v, ref, horizon, metric)] for v in variants]
                lines.append(
                    f"| {_group_label(cells[0])} | {horizon} | `{ref}` | "
                    + " | ".join(_compact(c) for c in cells)
                    + " |"
                )
    return "\n".join(lines)


def cell_matrix(table, variant_refs, horizon, metric):
    """The grid's cells as rows, (variant, reference) pairs as columns: mean / median (lower)."""
    rows = _lookup(table)
    cells = {c["cell_id"]: c for c in study2.grid_manifest()["cells"]}
    header = " | ".join(f"`{v}` vs `{r}`" for v, r in variant_refs)
    lines = [
        f"| Cell (n = 30) | Zero probability | Positive mean | Persistence | {header} |",
        "|---|---|---|---|" + "---|" * len(variant_refs),
    ]
    for cell in sorted(set(table.group) - {ALL}):
        entries = []
        for v, r in variant_refs:
            x = rows.loc[(cell, v, r, horizon, metric)]
            entries.append(
                "unavailable"
                if x.status != "descriptive"
                else f"{g(x.mean_diff)} / {g(x.median_diff)} ({int(x.wins)})"
            )
        c = cells[cell]
        lines.append(
            f"| {cell} | {g(c['zero_probability'])} | {g(c['positive_mean'])} "
            f"| {g(c['persistence'])} | " + " | ".join(entries) + " |"
        )
    return "\n".join(lines)


def occurrence_markdown(table):
    models = list(MODEL_PINS)
    lines = [
        "| Group | h | Windows | All-zero contexts | Positive target days "
        "| TSB p (0.05 / 0.1 / 0.2) "
        "| Jeffreys p | `dynamic_count` p | Completed 1 − F(0) (" + " / ".join(models) + ") "
        "| Days with every decile at zero (" + " / ".join(models) + ") |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in table.itertuples():
        tsb = " / ".join(
            f"{getattr(r, f'mean_{n}_p'):.3f}"
            for n in ("tsb_hurdle_a005", "tsb_hurdle", "tsb_hurdle_a020")
        )
        completed = " / ".join(f"{getattr(r, f'mean_{m}_completed_p'):.3f}" for m in models)
        zero = " / ".join(f"{getattr(r, f'{m}_all_zero_decile_day_share'):.3f}" for m in models)
        lines.append(
            f"| {r.group} (n = {r.group_series}) | {r.horizon} | {r.windows} "
            f"| {r.context_all_zero_windows} | {r.mean_positive_target_fraction:.3f} | {tsb} "
            f"| {r.mean_jeffreys_p:.3f} | {r.mean_dynamic_p:.3f} | {completed} | {zero} |"
        )
    return "\n".join(lines)


def print_tables(results):
    for panel, result in results.items():
        table = result["tables"]["contrasts.csv"]
        groups = [ALL] if panel == "grid" else [ALL, *sorted(set(table.group) - {ALL})]
        if panel != "grid":
            groups = [ALL, *(s for s in ("dense", "sparse", "very_sparse") if s in groups)]
        print(f"## {panel}: tsb_hurdle against every reference, four scores\n")
        print(full_table(table, PRIMARY, references(panel), groups))
        if panel == "grid":
            for metric in METRICS:
                for horizon in HORIZONS:
                    print(f"\n## grid cells: tsb_hurdle, {metric}, h = {horizon}\n")
                    pairs = [(PRIMARY, r) for r in references(panel)]
                    print(cell_matrix(table, pairs, horizon, metric))
        print(f"\n## {panel}: the TSB sensitivities, QScore9\n")
        sensitivities = ["tsb_hurdle_a005", PRIMARY, "tsb_hurdle_a020"]
        print(compact_table(table, sensitivities, references(panel), groups))
        print(f"\n## {panel}: the fourth cell, four scores\n")
        print(fourth_table(table, groups))
        if panel == "grid":
            for horizon in HORIZONS:
                print(f"\n## grid cells: the fourth cell, qscore9, h = {horizon}\n")
                pairs = [(m + FOURTH, r) for m in MODEL_PINS for r in (f"{m}_completed", COUNT)]
                print(cell_matrix(table, pairs, horizon, "qscore9"))
        print(f"\n## {panel}: the point methods, QScore9\n")
        point_refs = [f"{m}_completed" for m in MODEL_PINS] + [COUNT, DYNAMIC, PRIMARY]
        print(compact_table(table, list(POINT), point_refs, groups))
        print(f"\n## {panel}: occurrence descriptors\n")
        print(occurrence_markdown(result["tables"]["occurrence.csv"]))
        print(f"\n## {panel}: checks\n")
        for key, value in result["checks"].items():
            print(f"- {key}: {value}")
        print()


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--npm", type=Path, required=True, help="the npm run directory")
    parser.add_argument("--grid", type=Path, required=True, help="the grid run directory")
    parser.add_argument("--nyc311", type=Path, required=True, help="the NYC 311 run directory")
    parser.add_argument("--out", type=Path, default=HERE)
    parser.add_argument("--workers", type=int, default=1, help="processes for the windows")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT_DIR,
        help="the repository whose study/ holds the committed declarations (default: this one)",
    )
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    try:
        results = run_all(
            dict(npm=args.npm, grid=args.grid, nyc311=args.nyc311),
            out=args.out,
            root=args.root,
            workers=args.workers,
            command=[sys.executable, *sys.argv],
        )
    except FileExistsError as error:
        raise SystemExit(str(error)) from None
    print_tables(results)
    for name, digest in read_json(args.out / "provenance.json")["outputs"].items():
        print(name, digest)


if __name__ == "__main__":
    main()

"""Study 2 registered inference from a finished run directory; no model is loaded or refitted.

Reads the run's checkpoints and the component's committed comparison file and writes, under
<run>/inference/ (or a new --out directory), the confirmatory family table (inference.csv,
inference.json), the paired entity table, the per-series scores, the secondary tables, the
randomized PIT and the provenance. Every choice below is fixed in this file before any Study 2
score exists. The registered text is PROTOCOL.md, "Scores and the single external-domain
confirmatory family", "Synthetic intervention component" and "Seeds, provenance and execution
gate", with the dated additions of 2026-10-12 (the family E01 to E18) and 2026-10-15 (CRPS
availability); where it says nothing else, Study 1's confirmatory module is followed exactly
(pulsegraph/evaluation/confirmatory.py, pulsegraph/evaluation/reviews.py).

- Score: QScore9 per window (series, origin, horizon, model), as the run saved it.
- Aggregation: origins averaged within series and horizon. For external_packages the entity is
  the series and series weigh equally. For synthetic, origins are averaged within replicate and
  cell, then the 18 cells within replicate with equal cell weight; the entity is the replicate
  block, and the 30 blocks are the pairing and bootstrap units.
- Direction: difference = model minus reference. QScore9 is a loss, so a negative difference
  favors the model. Wins, ties and losses count entities whose difference is below, exactly at
  and above zero; the denominator is the number of entities.
- Interval: 20,000 entity bootstrap replicates with replacement, drawn in blocks of 256 as
  rng.integers(0, n, size=(block, n)) over the entities in ascending order (series_id in code
  point order; replicate number); pointwise percentile interval at alpha / 2 and 1 - alpha / 2
  with alpha = 1 - 0.95, NumPy quantile method "linear" (NumPy's default).
- Test: two-sided approximate Wilcoxon signed-rank test over the entity differences, omitting
  zero differences (zero_method "wilcox", no continuity correction), p = 1 when every difference
  is zero; Benjamini-Hochberg once over the whole family at q = 0.05.
- Seeds: see BOOTSTRAP_DERIVATION and PIT_DERIVATION; both are written into the provenance.
- Secondary outputs carry no multiplicity adjustment and never replace the family.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.evaluation.registration import installed_versions
from pulsegraph.evaluation.reviews import benjamini_hochberg
from pulsegraph.provenance import read_json, sha256_bytes
from pulsegraph.random import derived_seed
from pulsegraph.study2.constants import CUTOFFS, PROTOCOL_COMMIT, PROTOCOL_SHA256, SEEDS, VARIANTS
from pulsegraph.study2.declarations import validate
from pulsegraph.study2.distributions import CountLaw
from pulsegraph.study2.holdout import utc_now
from pulsegraph.study2.runner import resume_identity
from pulsegraph.study2.scores import CRPS_UNCERTIFIED, NO_DISTRIBUTION
from pulsegraph.study2.synthetic import grid_manifest

COMPONENTS = ("external_packages", "synthetic")
DOMAIN = dict(external_packages="packages", synthetic="synthetic")
ENTITY = dict(external_packages="series", synthetic="replicate")
ORIGINS = dict(external_packages=list(CUTOFFS), synthetic=["180", "210", "240"])
HORIZONS = (7, 30)
METRIC = "qscore9"
SECONDARY_METRICS = ("qscore9", "context_scaled_qscore9", "occurrence_brier", "discrete_crps")
PARTS = ("zero", "positive_over", "positive_under")
CONFIDENCE = 0.95
QUANTILE_METHOD = "linear"
BLOCK = 256
PIT_BINS = 10
BOOTSTRAP_DERIVATION = (
    "Each comparison's bootstrap seed is pulsegraph.random.derived_seed(20260917, component, "
    "comparison id, domain, model, reference, horizon, metric): the first four bytes, read as a "
    "little-endian unsigned 32-bit integer, of the SHA-256 of the UTF-8 bytes of json.dumps("
    "[20260917, component, comparison id, domain, model, reference, horizon, metric], "
    "sort_keys=True, allow_nan=False) with Python's default separators ', ' and ': ' and ASCII "
    "escaping; the root and the horizon are integers, every other field a string. The generator is "
    "numpy.random.default_rng(seed). A secondary contrast reuses a family row's model and "
    "reference with its own horizon and metric in the same derivation; its id is the family id, "
    "or the family id with '-h7' for a horizon outside the family."
)
PIT_DERIVATION = (
    "Each saved forecast with a count law per target day draws its uniforms from "
    "numpy.random.default_rng(pulsegraph.random.derived_seed(20260916, component, domain, "
    "series_id, cutoff, horizon, model)), the same SHA-256 derivation with the cutoff as the run's "
    "string label; V = rng.random(horizon), one uniform per target day in lead order. "
    "U = F(y-) + V (F(y) - F(y-)) with F(y-) = 1 - SF(y - 1) and F(y) = 1 - SF(y) of the saved "
    "law. Ten equal bins on [0, 1], the last closed. Raw native deciles, local_mean_28 and "
    "autoets_weekly have no full count law, and their PIT is unavailable."
)


def bootstrap_seed(component, comparison, metric):
    return derived_seed(
        SEEDS["bootstrap"],
        component,
        comparison["id"],
        comparison["domain"],
        comparison["model"],
        comparison["reference"],
        int(comparison["horizon"]),
        metric,
    )


def pit_seed(component, domain, series_id, cutoff, horizon, model):
    return derived_seed(SEEDS["pit"], component, domain, series_id, cutoff, int(horizon), model)


def cluster_contrast(diff, *, seed, family):
    """Study 1's entity-clustered inference for one comparison, with the family's settings."""
    diff = np.asarray(diff, dtype=float)
    if diff.ndim != 1 or len(diff) < 2 or not np.isfinite(diff).all():
        raise ValueError("Entity-clustered inference requires at least two finite differences")
    n_bootstrap = family["bootstrap_replicates"]
    rng = np.random.default_rng(seed)
    means = np.empty(n_bootstrap)
    # Resample whole entities, never windows or cells.
    for start in range(0, n_bootstrap, BLOCK):
        stop = min(start + BLOCK, n_bootstrap)
        means[start:stop] = diff[rng.integers(0, len(diff), size=(stop - start, len(diff)))].mean(
            axis=1
        )
    alpha = 1 - CONFIDENCE
    pvalue = (
        float(family["all_zero_p"])
        if np.all(diff == 0)
        else float(
            stats.wilcoxon(
                diff,
                zero_method=family["zero_method"],
                alternative=family["alternative"],
                method=family["method"],
            ).pvalue
        )
    )
    return dict(
        n_entities=len(diff),
        mean_diff=float(diff.mean()),
        mean_diff_ci_low=float(np.quantile(means, alpha / 2, method=QUANTILE_METHOD)),
        mean_diff_ci_high=float(np.quantile(means, 1 - alpha / 2, method=QUANTILE_METHOD)),
        median_diff=float(np.median(diff)),
        wins=int(np.sum(diff < 0)),
        ties=int(np.sum(diff == 0)),
        losses=int(np.sum(diff > 0)),
        n_nonzero=int(np.sum(diff != 0)),
        wilcoxon_p=pvalue,
    )


def describe(diff):
    """Descriptive pair summary for a subgroup: no interval, no test."""
    diff = np.asarray(diff, dtype=float)
    return dict(
        n_entities=len(diff),
        mean_diff=float(diff.mean()) if len(diff) else np.nan,
        median_diff=float(np.median(diff)) if len(diff) else np.nan,
        wins=int(np.sum(diff < 0)),
        ties=int(np.sum(diff == 0)),
        losses=int(np.sum(diff > 0)),
    )


def expected_series(component, metadata, root):
    """The registered series of the component, with their entity and descriptor labels."""
    if component == "synthetic":
        manifest = grid_manifest()
        if read_json(root / "study/study2/grid_manifest.json") != manifest:
            raise ValueError("Synthetic grid manifest differs from registration")
        labels = {
            row["series_id"]: dict(cell_id=row["cell_id"], replicate=int(row["replicate"]))
            for row in manifest["series"]
        }
        cells = {row["cell_id"] for row in manifest["cells"]}
        blocks = {}
        for label in labels.values():
            blocks.setdefault(label["replicate"], []).append(label["cell_id"])
        if len(blocks) < 2 or any(sorted(c) != sorted(cells) for c in blocks.values()):
            raise ValueError("Every replicate block must hold every cell exactly once")
        return labels
    panels = metadata["readiness"].get("panels", {})
    if set(panels) != {"packages"}:
        raise ValueError("The packages component takes the packages panel alone")
    entry = panels["packages"]["manifest"]
    path = root / entry["path"]
    if file_hash(path) != entry["sha256"]:
        raise ValueError("The run's manifest changed")
    labels = {
        row["series_id"]: dict(stratum=row.get("stratum")) for row in read_json(path)["series"]
    }
    if len(labels) < 2:
        raise ValueError("Entity-clustered inference requires at least two series")
    return labels


def read_run(component, run, family, spec, root):
    """Verify the run and return its window scores and PIT values, refusing any incomplete grid.

    Checkpoints are read one at a time; each saved law is used for its PIT and then released.
    """
    state = read_json(run / "run.json")
    if state.get("status") != "complete":
        raise ValueError("Inference requires a complete run")
    metadata = state["metadata"]
    if resume_identity(metadata) != state["identity"]:
        raise ValueError("Run metadata does not match the run identity")
    if (
        metadata.get("readiness", {}).get("action") != component
        or metadata.get("family") != family
        or metadata.get("spec") != spec
    ):
        raise ValueError("The run was not authorized for this component's registered family")
    labels = expected_series(component, metadata, root)
    domain = DOMAIN[component]
    keys = {json.dumps([domain, key], separators=(",", ":")): key for key in labels}
    if set(state["completed"]) != set(keys):
        raise ValueError("The run's checkpoints differ from the registered series")
    models = list(VARIANTS) + (["oracle"] if component == "synthetic" else [])
    records, pit_parts, checkpoints = [], [], {}
    for label in sorted(keys):
        path = run / (sha256_bytes(label.encode()) + ".json")
        if file_hash(path) != state["completed"][label]:
            raise ValueError("Checkpoint hash mismatch")
        checkpoints[label] = state["completed"][label]
        document = read_json(path)
        if document.get("identity") != state["identity"]:
            raise ValueError("Checkpoint belongs to a different run")
        for row in document["rows"]:
            if (
                row["domain"] != domain
                or row["series_id"] != keys[label]
                or row["cutoff"] not in ORIGINS[component]
                or row["horizon"] not in HORIZONS
                or row["model"] not in models
                or len(row["target"]) != row["horizon"]
            ):
                raise ValueError("Checkpoint row outside the registered grid")
            scores = row["scores"]
            records.append(
                dict(
                    series_id=row["series_id"],
                    cutoff=row["cutoff"],
                    horizon=int(row["horizon"]),
                    model=row["model"],
                    has_law=row["forecast"].get("distributions") is not None,
                    qscore9=scores["qscore9"],
                    context_scaled_qscore9=scores["context_scaled_qscore9"],
                    occurrence_brier=scores["occurrence_brier"],
                    discrete_crps=scores["discrete_crps"],
                    crps_unavailable_reason=scores["crps_unavailable_reason"],
                    residual=scores["residual"],
                    n_zero=int(scores["n_zero"]),
                    n_positive=int(scores["n_positive"]),
                    **{part: scores["contributions"][part] for part in PARTS},
                )
            )
        with_law = [r for r in document["rows"] if r["forecast"].get("distributions") is not None]
        pit_parts.append(pit(component, with_law))
    frame = pd.DataFrame.from_records(records)
    window = ["series_id", "cutoff", "horizon", "model"]
    expected = len(labels) * len(ORIGINS[component]) * len(HORIZONS) * len(models)
    if frame.duplicated(window).any() or len(frame) != expected:
        raise ValueError("The run's grid is incomplete or has duplicate windows")
    for column in ("occurrence_brier", "discrete_crps"):
        frame[column] = pd.to_numeric(frame[column], errors="raise").astype(float)
    if not np.isfinite(frame[METRIC]).all():
        raise ValueError("Every primary score must be finite")
    descriptors = pd.DataFrame.from_dict(labels, orient="index")
    frame = frame.join(descriptors, on="series_id")
    return state, frame, pd.concat(pit_parts, ignore_index=True), checkpoints


def _strict_mean(frame, keys, value):
    """Group mean that is undefined when any member is undefined."""
    grouped = frame.groupby(keys, sort=True)[value]
    return grouped.mean().where(grouped.count() == grouped.size())


def series_scores(frame, values):
    keys = ["horizon", "model", "series_id"]
    table = pd.DataFrame({value: _strict_mean(frame, keys, value) for value in values})
    descriptors = frame.drop_duplicates("series_id").set_index("series_id")
    labels = [c for c in ("stratum", "cell_id", "replicate") if c in frame.columns]
    return table.join(descriptors[labels], on="series_id")


def entity_scores(component, series, values, keys=("horizon", "model")):
    """Windows within series already averaged; synthetic cells then average within replicate."""
    if component == "external_packages":
        return series.reset_index().set_index([*keys, "series_id"])[list(values)].sort_index()
    flat = series.reset_index()
    return pd.DataFrame(
        {value: _strict_mean(flat, [*keys, "replicate"], value) for value in values}
    )


def paired(entities, model, reference, horizon, value, prefix=()):
    model_scores = entities.loc[(*prefix, horizon, model)][value]
    reference_scores = entities.loc[(*prefix, horizon, reference)][value]
    pair = pd.DataFrame(dict(model_score=model_scores, reference_score=reference_scores))
    pair.index.name = "entity"
    return pair.sort_index()


def confirmatory(component, family, entities):
    rows, pairs = [], []
    for comparison in family["comparisons"]:
        pair = paired(
            entities, comparison["model"], comparison["reference"], comparison["horizon"], METRIC
        )
        if pair.isna().any().any() or len(pair) < 2:
            raise ValueError("Missing pairs block inference without shrinking the family")
        diff = (pair.model_score - pair.reference_score).to_numpy()
        seed = bootstrap_seed(component, comparison, METRIC)
        rows.append(
            dict(
                **{key: comparison[key] for key in ("id", "domain", "model", "reference")},
                horizon=int(comparison["horizon"]),
                metric=METRIC,
                entity=ENTITY[component],
                model_mean=float(pair.model_score.mean()),
                reference_mean=float(pair.reference_score.mean()),
                **cluster_contrast(diff, seed=seed, family=family),
                bootstrap_root=SEEDS["bootstrap"],
                bootstrap_seed=seed,
                n_bootstrap=family["bootstrap_replicates"],
                confidence=CONFIDENCE,
                quantile_method=QUANTILE_METHOD,
                declared_count=family["comparison_count"],
            )
        )
        item = pair.reset_index()
        item.insert(0, "entity_kind", ENTITY[component])
        for key in ("horizon", "reference", "model", "domain", "id"):
            item.insert(0, key, comparison[key])
        item["difference"] = item.model_score - item.reference_score
        pairs.append(item)
    table = pd.DataFrame(rows)
    if len(table) != family["comparison_count"] or table["id"].duplicated().any():
        raise ValueError("The family must be exactly the declared comparisons")
    table["wilcoxon_p_bh"] = benjamini_hochberg(table.wilcoxon_p)
    table["reject_bh_005"] = table.wilcoxon_p_bh <= family["q"]
    table["calendar_conditional"] = bool(family["calendar_conditional"])
    return table, pd.concat(pairs, ignore_index=True)


def contrast_list(family):
    """The family's model/reference pairs at both horizons, with ids for the secondary tables."""
    items = []
    for comparison in family["comparisons"]:
        pair = (comparison["model"], comparison["reference"])
        if any((c["model"], c["reference"]) == pair for c in items):
            continue
        for horizon in HORIZONS:
            match = next(
                (
                    c
                    for c in family["comparisons"]
                    if (c["model"], c["reference"], c["horizon"]) == (*pair, horizon)
                ),
                None,
            )
            items.append(
                dict(
                    id=match["id"] if match else f"{comparison['id']}-h{horizon}",
                    domain=comparison["domain"],
                    model=pair[0],
                    reference=pair[1],
                    horizon=horizon,
                    in_family=match is not None,
                )
            )
    return items


def _unavailable_reason(frame, models, metric):
    if (
        metric in ("occurrence_brier", "discrete_crps")
        and not frame.loc[frame.model.isin(models), "has_law"].all()
    ):
        return NO_DISTRIBUTION
    return CRPS_UNCERTIFIED if metric == "discrete_crps" else "undefined_score"


def secondary_contrasts(component, family, frame, entities):
    rows = []
    for item in contrast_list(family):
        for metric in SECONDARY_METRICS:
            if metric == METRIC and item["in_family"]:
                continue
            pair = paired(entities, item["model"], item["reference"], item["horizon"], metric)
            available = pair.dropna()
            row = dict(
                {k: v for k, v in item.items() if k != "in_family"},
                metric=metric,
                entity=ENTITY[component],
                n_entities_unavailable=len(pair) - len(available),
            )
            if len(available) >= 2:
                diff = (available.model_score - available.reference_score).to_numpy()
                seed = bootstrap_seed(component, item, metric)
                row.update(
                    status="secondary",
                    model_mean=float(available.model_score.mean()),
                    reference_mean=float(available.reference_score.mean()),
                    **cluster_contrast(diff, seed=seed, family=family),
                    bootstrap_seed=seed,
                )
            else:
                row.update(
                    status="unavailable" if not len(available) else "fewer_than_two_entities",
                    n_entities=len(available),
                    unavailable_reason=_unavailable_reason(
                        frame, (item["model"], item["reference"]), metric
                    ),
                )
            rows.append(row)
    return pd.DataFrame(rows)


def score_table(frame, entities, keys=("horizon", "model")):
    """Equal-entity means with their availability, and the forecast-level CRPS denominators."""
    rows = []
    for group, windows in frame.groupby(list(keys), sort=True):
        group = group if isinstance(group, tuple) else (group,)
        block = entities.loc[group]
        reasons = windows.crps_unavailable_reason
        row = dict(zip(keys, group, strict=True), n_entities=len(block))
        for metric in SECONDARY_METRICS:
            row[metric] = float(block[metric].mean()) if block[metric].notna().any() else np.nan
            row[f"{metric}_n_entities"] = int(block[metric].notna().sum())
        row.update(
            crps_forecasts=len(windows),
            crps_with_count_distribution=int((reasons != NO_DISTRIBUTION).sum()),
            crps_certified=int(windows.discrete_crps.notna().sum()),
            crps_unavailable_no_count_distribution=int((reasons == NO_DISTRIBUTION).sum()),
            crps_unavailable_bound_not_certified=int((reasons == CRPS_UNCERTIFIED).sum()),
        )
        rows.append(row)
    return pd.DataFrame(rows)


def accounting_table(frame, entities, keys=("horizon", "model")):
    """The three exact parts with the full horizon denominator, and pooled conditional means."""
    rows = []
    for group, windows in frame.groupby(list(keys), sort=True):
        group = group if isinstance(group, tuple) else (group,)
        block = entities.loc[group]
        horizon = dict(zip(keys, group, strict=True))["horizon"]
        zero_days, positive_days = int(windows.n_zero.sum()), int(windows.n_positive.sum())
        row = dict(zip(keys, group, strict=True), n_entities=len(block))
        row.update({part: float(block[part].mean()) for part in (METRIC, *PARTS)})
        row["parts_sum"] = sum(row[part] for part in PARTS)
        row.update(
            max_abs_window_residual=float(windows.residual.abs().max()),
            n_zero_days=zero_days,
            n_positive_days=positive_days,
            zero_conditional_mean=float(windows.zero.sum() * horizon / zero_days)
            if zero_days
            else np.nan,
            positive_conditional_mean=float(
                (windows.positive_over + windows.positive_under).sum() * horizon / positive_days
            )
            if positive_days
            else np.nan,
        )
        rows.append(row)
    return pd.DataFrame(rows)


def group_tables(component, family, frame, series):
    """Per-stratum (external) or per-cell (synthetic) scores and contrasts, with n."""
    group = "stratum" if component == "external_packages" else "cell_id"
    values = [*SECONDARY_METRICS, *PARTS]
    flat = series.reset_index()
    flat[group] = flat[group].fillna("unlabelled")
    frame = frame.assign(**{group: frame[group].fillna("unlabelled")})
    # Within a stratum the entity is the series; within a cell it is the replicate's one series.
    entities = flat.set_index([group, "horizon", "model", "series_id"])[values].sort_index()
    scores = score_table(frame, entities, keys=(group, "horizon", "model"))
    scores = scores.merge(
        accounting_table(frame, entities, keys=(group, "horizon", "model"))[
            [group, "horizon", "model", *PARTS, "n_zero_days", "n_positive_days"]
        ],
        on=[group, "horizon", "model"],
    )
    rows = []
    for name in sorted(flat[group].unique()):
        for item in contrast_list(family):
            for metric in (METRIC, "context_scaled_qscore9"):
                pair = paired(
                    entities, item["model"], item["reference"], item["horizon"], metric, (name,)
                ).dropna()
                rows.append(
                    {
                        group: name,
                        **{k: v for k, v in item.items() if k != "in_family"},
                        "metric": metric,
                        "model_mean": float(pair.model_score.mean()) if len(pair) else np.nan,
                        "reference_mean": float(pair.reference_score.mean())
                        if len(pair)
                        else np.nan,
                        **describe(pair.model_score - pair.reference_score),
                    }
                )
    contrasts = pd.DataFrame(rows)
    if component == "synthetic":
        generators = pd.DataFrame(grid_manifest()["cells"])
        scores = generators.merge(scores, on="cell_id", validate="one_to_many")
        contrasts = generators.merge(contrasts, on="cell_id", validate="one_to_many")
    return scores, contrasts


def pit(component, rows):
    """Randomized PIT for saved forecasts that carry a count law per target day."""
    columns = dict(series_id=[], cutoff=[], horizon=[], model=[], lead=[], target=[], seed=[], v=[])
    below, at = [], []
    for row in rows:
        y = np.asarray(row["target"], dtype=float)
        specs = row["forecast"]["distributions"]
        if len(specs) != len(y):
            raise ValueError("Distribution/target length mismatch")
        seed = pit_seed(
            component, row["domain"], row["series_id"], row["cutoff"], row["horizon"], row["model"]
        )
        v = np.random.default_rng(seed).random(len(y))
        lower, upper = np.empty(len(y)), np.empty(len(y))
        groups = {}
        for lead, spec in enumerate(specs):
            groups.setdefault(json.dumps(spec, sort_keys=True), []).append(lead)
        for key, leads in groups.items():
            law, leads = CountLaw(json.loads(key)), np.asarray(leads)
            lower[leads] = 1 - law.sf(y[leads] - 1)
            upper[leads] = 1 - law.sf(y[leads])
        if (upper < lower).any() or (lower < 0).any() or (upper > 1).any():
            raise ValueError("A saved count law is not a distribution at its target")
        for name in ("series_id", "cutoff", "horizon", "model"):
            columns[name].extend([row[name]] * len(y))
        columns["lead"].extend(range(1, len(y) + 1))
        columns["target"].extend(y.tolist())
        columns["seed"].extend([seed] * len(y))
        columns["v"].extend(v.tolist())
        below.append(lower)
        at.append(upper)
    values = pd.DataFrame(columns)
    values["cdf_below"] = np.concatenate(below) if below else np.empty(0)
    values["cdf_at"] = np.concatenate(at) if at else np.empty(0)
    values["pit"] = values.cdf_below + values.v * (values.cdf_at - values.cdf_below)
    values.insert(0, "domain", DOMAIN[component])
    return values


def pit_histograms(frame, values):
    rows = []
    for (horizon, model), windows in frame.groupby(["horizon", "model"], sort=True):
        row = dict(horizon=horizon, model=model, n_forecasts=len(windows))
        if windows.has_law.all():
            u = values.loc[values.horizon.eq(horizon) & values.model.eq(model), "pit"].to_numpy()
            counts = np.bincount(
                np.minimum((u * PIT_BINS).astype(int), PIT_BINS - 1), minlength=PIT_BINS
            )
            row.update(status="available", unavailable_reason=None, n_values=len(u))
            row.update({f"bin{b + 1:02}": int(c) for b, c in enumerate(counts)})
            row.update({f"fraction{b + 1:02}": c / len(u) for b, c in enumerate(counts)})
        else:
            row.update(status="unavailable", unavailable_reason=NO_DISTRIBUTION, n_values=0)
        rows.append(row)
    return pd.DataFrame(rows)


def _integers(table):
    """Counts and seeds stay integers in the CSVs, empty where a row has none."""
    names = ("n_entities", "n_entities_unavailable", "wins", "ties", "losses", "n_nonzero")
    for name in table.columns:
        if name in names or name == "bootstrap_seed" or name.startswith("bin"):
            table[name] = table[name].astype("Int64")
    return table


def _plain(value):
    """JSON-ready values: NaN becomes null and NumPy scalars become Python scalars."""
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _write_json(path, value):
    path.write_text(
        json.dumps(_plain(value), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _relative(path, root):
    """A path as the repository names it, never by a local absolute path when avoidable."""
    try:
        return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


def _git(*args):
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT_DIR, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def run_inference(component, run, *, out=None, comparisons=None, root=ROOT_DIR, command=None):
    if component not in COMPONENTS:
        raise ValueError("Inference covers external_packages and synthetic only")
    run, root = Path(run), Path(root)
    out = run / "inference" if out is None else Path(out)
    if out.exists():
        raise FileExistsError("Inference outputs are immutable; choose a new directory")
    comparisons = (
        root / f"study/study2/{component}_comparisons.json"
        if comparisons is None
        else Path(comparisons)
    )
    spec_path = root / f"study/study2/{component}_spec.json"
    family, spec = read_json(comparisons), read_json(spec_path)
    if validate(spec, family) != component or family["component"] != component:
        raise ValueError("The comparison file is not this component's registered family")
    state, frame, pit_values, checkpoints = read_run(component, run, family, spec, root)

    series = series_scores(frame, [*SECONDARY_METRICS, *PARTS])
    entities = entity_scores(component, series, [*SECONDARY_METRICS, *PARTS])
    inference, pairs = confirmatory(component, family, entities)
    contrasts = secondary_contrasts(component, family, frame, entities)
    scores = score_table(frame, entities)
    accounting = accounting_table(frame, entities)
    groups, group_contrasts = group_tables(component, family, frame, series)
    histograms = pit_histograms(frame, pit_values)

    group = "strata" if component == "external_packages" else "cells"
    tables = {
        "inference.csv": inference,
        "paired_entities.csv": pairs,
        "series_scores.csv": series.reset_index(),
        "secondary_contrasts.csv": contrasts,
        "secondary_scores.csv": scores,
        "secondary_accounting.csv": accounting,
        f"secondary_{group}.csv": groups,
        f"secondary_{group}_contrasts.csv": group_contrasts,
        "pit_histograms.csv": histograms,
    }
    out.mkdir(parents=True)
    for name, table in tables.items():
        _integers(table).to_csv(out / name, index=False, lineterminator="\n")
    pit_values.to_parquet(out / "pit_values.parquet", index=False)
    _write_json(
        out / "inference.json",
        dict(
            analysis="study2_registered_inference",
            component=component,
            protocol_commit=PROTOCOL_COMMIT,
            protocol_sha256=PROTOCOL_SHA256,
            comparison_family=family,
            confirmatory=inference.to_dict("records"),
            settings=dict(
                metric=METRIC,
                entity=ENTITY[component],
                aggregation=(
                    "origins within series and horizon, then equal series"
                    if component == "external_packages"
                    else "origins within replicate and cell, then cells within replicate with "
                    "equal cell weight; the replicate blocks are the pairing and bootstrap units"
                ),
                difference="model minus reference; negative favors the model",
                wins_ties_losses="entities with difference < 0, == 0, > 0; denominator n_entities",
                bootstrap=dict(
                    replicates=family["bootstrap_replicates"],
                    unit=ENTITY[component],
                    root=SEEDS["bootstrap"],
                    derivation=BOOTSTRAP_DERIVATION,
                    draws=f"rng.integers(0, n, size=(block, n)) in blocks of {BLOCK}",
                    entity_order="ascending series_id (code point) or replicate number",
                ),
                interval=dict(
                    kind="pointwise percentile",
                    confidence=CONFIDENCE,
                    levels="alpha / 2 and 1 - alpha / 2 with alpha = 1 - 0.95",
                    numpy_quantile_method=QUANTILE_METHOD,
                ),
                test=dict(
                    name=family["test"],
                    alternative=family["alternative"],
                    method=family["method"],
                    zero_method=family["zero_method"],
                    all_zero_p=family["all_zero_p"],
                ),
                adjustment=dict(
                    method=family["adjustment"],
                    q=family["q"],
                    count=family["comparison_count"],
                    scope="once over the whole family",
                ),
                calendar_conditional=family["calendar_conditional"],
            ),
            secondary=dict(
                status="secondary; no multiplicity adjustment; never replaces the family",
                files=sorted(set(tables) - {"inference.csv", "paired_entities.csv"})
                + ["pit_values.parquet"],
                availability=(
                    "a secondary score is defined for an entity only when every one of its "
                    "windows has it; contrasts use the entities where both sides are defined "
                    "and report how many are not"
                ),
            ),
            pit=dict(
                root=SEEDS["pit"],
                derivation=PIT_DERIVATION,
                bins=[[b / PIT_BINS, (b + 1) / PIT_BINS] for b in range(PIT_BINS)],
            ),
        ),
    )
    outputs = sorted(p.name for p in out.iterdir())
    versions = installed_versions()
    _write_json(
        out / "provenance.json",
        dict(
            analysis="study2_registered_inference",
            component=component,
            written_at=utc_now().isoformat(),
            command=command,
            regeneration=(
                r".\.venv\Scripts\python.exe scripts\study2_inference.py "
                + f"{component} --run {Path(_relative(run, root))} --out <new directory>"
            ),
            inference_script_sha256=file_hash(Path(__file__)),
            implementation_commit_at_inference=_git("rev-parse", "HEAD"),
            uncommitted_changes_at_inference=_git(
                "status", "--porcelain", "--", "scripts/study2_inference.py", "pulsegraph"
            ),
            packages={name: versions.get(name) for name in ("numpy", "scipy", "pandas")},
            protocol_commit=PROTOCOL_COMMIT,
            protocol_sha256=PROTOCOL_SHA256,
            comparisons=dict(path=_relative(comparisons, root), sha256=file_hash(comparisons)),
            spec=dict(path=_relative(spec_path, root), sha256=file_hash(spec_path)),
            run=dict(
                directory=_relative(run, root),
                run_json_sha256=file_hash(run / "run.json"),
                identity=state["identity"],
                implementation_commit=state["metadata"]
                .get("metadata", {})
                .get("implementation_commit"),
                readiness_sha256=state["metadata"].get("readiness_sha256"),
                checkpoints=len(checkpoints),
                checkpoint_sha256=checkpoints,
            ),
            seeds=dict(
                bootstrap_root=SEEDS["bootstrap"],
                bootstrap_derivation=BOOTSTRAP_DERIVATION,
                pit_root=SEEDS["pit"],
                pit_derivation=PIT_DERIVATION,
                comparison_seeds={
                    r["id"]: r["bootstrap_seed"] for r in inference.to_dict("records")
                },
            ),
            artifact_sha256={name: file_hash(out / name) for name in outputs},
        ),
    )
    return inference


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("component", choices=COMPONENTS)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="a new directory; default <run>/inference")
    parser.add_argument(
        "--comparisons",
        type=Path,
        help="default study/study2/<component>_comparisons.json",
    )
    args = parser.parse_args()
    inference = run_inference(
        args.component,
        args.run,
        out=args.out,
        comparisons=args.comparisons,
        command=[sys.executable, *sys.argv],
    )
    print(f"Study 2 {args.component} inference written: {len(inference)} comparisons")


if __name__ == "__main__":
    main()

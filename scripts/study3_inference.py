r"""Study 3 registered inference from a finished run directory; no model is loaded or refitted.

Usage, from the repository root:
    .\.venv\Scripts\python.exe scripts\study3_inference.py --run <run directory> [--out <new>]

Reads the run's checkpoints and the committed declarations (study/study3/spec.json and
study/study3/regime_comparisons.json) and writes, under <run>/inference/ (or a new --out
directory), the confirmatory family table (inference.csv, inference.json), the paired entity
table, the family's descriptors, the per-series scores, the secondary tables, the randomized PIT
and the provenance. Every choice below is fixed in this file before any Study 3 score exists.
The registered text is PROTOCOL.md, dated addition of 2026-10-16, item 7, with Study 2's "Scores
and the single external-domain confirmatory family" wherever item 7 says "as registered".
Study 2's functions are imported unchanged from scripts/study2_inference.py, whose bytes the
committed Study 2 post-hoc commands check: the window means, the pairing, the entity-clustered
test and interval, and the score, accounting and PIT-histogram tables.

- Score: QScore9 per window (series, origin, horizon, variant), as the run saved it.
- Family: R01 to R36 as committed, validated field by field against the registration. Within
  each stratum, origins are averaged within series and horizon and series weigh equally; the
  series are the pairing and bootstrap units. Difference = variant minus reference; negative
  favors the variant. Wins, ties and losses count series below, at and above zero.
- Availability: a stratum whose number of complete series (the series of the frozen manifest in
  that stratum, each with the complete registered grid) is below ten has its twelve tests
  reported as unavailable, with no p-value. BH is applied once at q = 0.05 over the available
  tests: all 36 when every stratum holds ten series. No outcome shrinks the family.
- Test and interval: Study 2's, unchanged: two-sided approximate Wilcoxon signed-rank test over
  the series differences, zero differences omitted, p = 1 when every difference is zero; 20,000
  series bootstrap replicates, pointwise 95% percentile interval, NumPy's linear quantile.
- Direction: read from the median (median_sign) and reported beside the mean; for T1 rows the
  sign H3 predicts for the stratum, from the committed file, is reported beside it.
- Seeds: see BOOTSTRAP_DERIVATION and PIT_DERIVATION; both are written into the provenance.
- Secondary, declared, unadjusted unless a column says otherwise, never confirmatory: per
  stratum, hurdle_fixed (the run's <model>_hurdle) and occurrence_model_size_count against the
  completed control and both count hurdles, and the family's pairs on the other metrics; the
  pooled tables over every series in Study 2's form (its eighteen contrasts, with a BH column
  within that table only, as Study 2's table carries one) and the Study 3 pairs pooled; the
  context-scaled QScore9, the occurrence Brier score, the discrete CRPS with its availability
  rule and the randomized PIT; the three-part accounting; and, per stratum, the leave-one-out and
  concentration descriptors of every family row with Study 1's definitions (skill 1 - variant /
  reference, undefined where the reference is zero; the share of the positive gains held by the
  five largest; the range of the mean difference with one series left out, and the series whose
  omission moves it most).
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.evaluation.registration import installed_versions
from pulsegraph.evaluation.reviews import benjamini_hochberg
from pulsegraph.provenance import read_json, sha256_bytes
from pulsegraph.random import derived_seed
from pulsegraph.study2.constants import (
    CUTOFFS,
    MODEL_PINS,
    STUDY3_DOMAIN,
    STUDY3_FALLBACK_DOMAIN,
    STUDY3_FILES,
    STUDY3_MINIMUM_SERIES,
    STUDY3_PROTOCOL_SHA256,
    STUDY3_SEEDS,
    STUDY3_STRATA,
    STUDY3_VARIANTS,
)
from pulsegraph.study2.declarations import study3_comparisons, validate_study3
from pulsegraph.study2.distributions import CountLaw
from pulsegraph.study2.holdout import utc_now
from pulsegraph.study2.runner import resume_identity

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
import scripts.study2_inference as study2  # noqa: E402

COMPONENT = "study3"
HORIZONS = study2.HORIZONS
METRIC = study2.METRIC
SECONDARY_METRICS = study2.SECONDARY_METRICS
PARTS = study2.PARTS
VALUES = [*SECONDARY_METRICS, *PARTS]
UNAVAILABLE = "fewer_than_ten_complete_series"
ALL = "all"
BOOTSTRAP_DERIVATION = (
    "Each comparison's bootstrap seed is pulsegraph.random.derived_seed(20261004, 'study3', "
    "comparison id, stratum, variant, reference, horizon, metric): Study 2's derivation (the "
    "first four bytes, little-endian, of the SHA-256 of json.dumps([root, component, id, ...], "
    "sort_keys=True, allow_nan=False)) with the component name study3, the stratum in the place "
    "of the domain and the variant in the place of the model; the root and the horizon are "
    "integers, every other field a string. A pooled secondary row has the stratum 'all'; a "
    "secondary row's id is 'stratum/variant/reference/h<horizon>', or P01 to P18 for the "
    "pooled table in Study 2's form. The generator is numpy.random.default_rng(seed)."
)
PIT_DERIVATION = (
    "Each saved forecast with a count law per target day draws its uniforms from "
    "numpy.random.default_rng(pulsegraph.random.derived_seed(20261003, 'study3', domain, "
    "series_id, cutoff, horizon, model)); V = rng.random(horizon), one uniform per target day "
    "in lead order; U = F(y-) + V (F(y) - F(y-)) with F(y-) = 1 - SF(y - 1) and F(y) = 1 - SF(y) "
    "of the saved law. Ten equal bins on [0, 1], the last closed. Raw native deciles, "
    "local_mean_28 and autoets_weekly have no full count law, and their PIT is unavailable."
)


def bootstrap_seed(item, metric):
    return derived_seed(
        STUDY3_SEEDS["bootstrap"],
        COMPONENT,
        item["id"],
        item["stratum"],
        item["variant"],
        item["reference"],
        int(item["horizon"]),
        metric,
    )


def pit_seed(domain, series_id, cutoff, horizon, model):
    return derived_seed(
        STUDY3_SEEDS["pit"], COMPONENT, domain, series_id, cutoff, int(horizon), model
    )


def secondary_pairs(model):
    """The declared secondary pairs of one model; the family's two come last."""
    pairs = []
    for variant in (f"{model}_hurdle", f"{model}_occurrence_model_size_count"):
        for reference in (f"{model}_completed", "hurdle_count_28", "hurdle_empirical_28"):
            pairs.append((variant, reference))
    pairs += [(f"{model}_hurdle_dynamic", f"{model}_completed")]
    pairs += [(f"{model}_hurdle_dynamic", "hurdle_empirical_28")]
    return pairs


def study2_form():
    """Study 2's eighteen contrasts, in its order, for the pooled table in Study 2's form."""
    rows = []
    for model in MODEL_PINS:
        for horizon in HORIZONS:
            for variant, reference in (
                (f"{model}_hurdle", f"{model}_completed"),
                (f"{model}_hurdle", "hurdle_count_28"),
                (f"{model}_raw", "local_mean_28"),
            ):
                rows.append(
                    dict(
                        id=f"P{len(rows) + 1:02}",
                        stratum=ALL,
                        variant=variant,
                        reference=reference,
                        horizon=horizon,
                    )
                )
    return rows


def expected_series(metadata, root):
    """The run's one domain and its manifest series with their sampling strata."""
    readiness = metadata.get("readiness", {})
    domain, panels = readiness.get("domain"), readiness.get("panels", {})
    if domain not in (STUDY3_DOMAIN, STUDY3_FALLBACK_DOMAIN) or set(panels) != {domain}:
        raise ValueError("A Study 3 run takes one domain panel")
    entry = panels[domain]["manifest"]
    path = root / entry["path"]
    if file_hash(path) != entry["sha256"]:
        raise ValueError("The run's manifest changed")
    labels = {
        row["series_id"]: dict(stratum=row.get("stratum")) for row in read_json(path)["series"]
    }
    if len(labels) < 2 or any(v["stratum"] not in STUDY3_STRATA for v in labels.values()):
        raise ValueError("A Study 3 panel holds at least two series, each in a sampling stratum")
    return domain, labels


def pit(domain, rows):
    """Randomized PIT for saved forecasts that carry a count law per target day."""
    columns = dict(series_id=[], cutoff=[], horizon=[], model=[], lead=[], target=[], seed=[], v=[])
    below, at = [], []
    for row in rows:
        y = np.asarray(row["target"], dtype=float)
        specs = row["forecast"]["distributions"]
        if len(specs) != len(y):
            raise ValueError("Distribution/target length mismatch")
        seed = pit_seed(domain, row["series_id"], row["cutoff"], row["horizon"], row["model"])
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
    values.insert(0, "domain", domain)
    return values


def read_run(run, family, spec, root):
    """Verify the run and return its window scores and PIT values, refusing any incomplete grid."""
    state = read_json(run / "run.json")
    if state.get("status") != "complete":
        raise ValueError("Inference requires a complete run")
    metadata = state["metadata"]
    if resume_identity(metadata) != state["identity"]:
        raise ValueError("Run metadata does not match the run identity")
    if (
        metadata.get("readiness", {}).get("action") != COMPONENT
        or metadata.get("family") != family
        or metadata.get("spec") != spec
    ):
        raise ValueError("The run was not authorized for Study 3's registered family")
    domain, labels = expected_series(metadata, root)
    keys = {json.dumps([domain, key], separators=(",", ":")): key for key in labels}
    if set(state["completed"]) != set(keys):
        raise ValueError("The run's checkpoints differ from the registered series")
    models = list(STUDY3_VARIANTS)
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
                or row["cutoff"] not in CUTOFFS
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
        pit_parts.append(pit(domain, with_law))
    frame = pd.DataFrame.from_records(records)
    window = ["series_id", "cutoff", "horizon", "model"]
    expected = len(labels) * len(CUTOFFS) * len(HORIZONS) * len(models)
    if frame.duplicated(window).any() or len(frame) != expected:
        raise ValueError("The run's grid is incomplete or has duplicate windows")
    for column in ("occurrence_brier", "discrete_crps"):
        frame[column] = pd.to_numeric(frame[column], errors="raise").astype(float)
    if not np.isfinite(frame[METRIC]).all():
        raise ValueError("Every primary score must be finite")
    frame = frame.join(pd.DataFrame.from_dict(labels, orient="index"), on="series_id")
    return state, domain, frame, pd.concat(pit_parts, ignore_index=True), checkpoints


def stratum_entities(series):
    """Series means indexed by stratum, horizon, model and series; the pooled ones under 'all'."""
    flat = series.reset_index()
    by_stratum = flat.set_index(["stratum", "horizon", "model", "series_id"])[VALUES]
    pooled = flat.assign(stratum=ALL).set_index(["stratum", "horizon", "model", "series_id"])
    return pd.concat([by_stratum, pooled[VALUES]]).sort_index()


def _sign(value):
    return "negative" if value < 0 else "positive" if value > 0 else "zero"


def family_table(family, entities, sizes):
    """R01 to R36 within their strata; a stratum below ten series makes its tests unavailable."""
    rows, pairs = [], []
    minimum = family["minimum_complete_series_per_stratum"]
    for comparison in family["comparisons"]:
        stratum, n = comparison["stratum"], sizes.get(comparison["stratum"], 0)
        row = dict(
            **{k: comparison[k] for k in ("id", "stratum", "model", "variant", "reference")},
            contrast=comparison["contrast"],
            horizon=int(comparison["horizon"]),
            metric=METRIC,
            entity="series",
            n_entities=n,
            predicted_sign=family["predicted_t1_sign"][stratum]
            if comparison["contrast"] == "T1"
            else None,
        )
        if n < minimum:
            rows.append(dict(row, status="unavailable", unavailable_reason=UNAVAILABLE))
            continue
        pair = study2.paired(
            entities,
            comparison["variant"],
            comparison["reference"],
            comparison["horizon"],
            METRIC,
            (stratum,),
        )
        if pair.isna().any().any() or len(pair) != n:
            raise ValueError("Missing pairs block inference without shrinking the family")
        diff = (pair.model_score - pair.reference_score).to_numpy()
        seed = bootstrap_seed(comparison, METRIC)
        result = study2.cluster_contrast(diff, seed=seed, family=family)
        row.update(
            status="available",
            unavailable_reason=None,
            variant_mean=float(pair.model_score.mean()),
            reference_mean=float(pair.reference_score.mean()),
            **result,
            median_sign=_sign(result["median_diff"]),
            bootstrap_root=STUDY3_SEEDS["bootstrap"],
            bootstrap_seed=seed,
            n_bootstrap=family["bootstrap_replicates"],
            confidence=study2.CONFIDENCE,
            quantile_method=study2.QUANTILE_METHOD,
        )
        if row["predicted_sign"] is not None:
            row["median_as_predicted"] = row["median_sign"] == row["predicted_sign"]
        rows.append(row)
        item = pair.reset_index().rename(
            columns=dict(model_score="variant_score", entity="series_id")
        )
        for key in ("horizon", "reference", "variant", "model", "stratum", "id"):
            item.insert(0, key, comparison[key])
        item["difference"] = item.variant_score - item.reference_score
        pairs.append(item)
    table = pd.DataFrame(rows)
    if len(table) != family["comparison_count"] or table["id"].duplicated().any():
        raise ValueError("The family must be exactly the declared comparisons")
    available = table.status.eq("available")
    table["declared_count"] = family["comparison_count"]
    table["bh_count"] = int(available.sum())
    table["wilcoxon_p_bh"] = np.nan
    if available.any():
        table.loc[available, "wilcoxon_p_bh"] = benjamini_hochberg(
            table.loc[available, "wilcoxon_p"]
        )
    table["reject_bh_005"] = pd.array(
        [bool(p <= family["q"]) if ok else pd.NA for p, ok in zip(table.wilcoxon_p_bh, available)],
        dtype="boolean",
    )
    table["calendar_conditional"] = bool(family["calendar_conditional"])
    if "median_as_predicted" in table:
        table["median_as_predicted"] = table.median_as_predicted.astype("boolean")
    columns = pd.concat(pairs, ignore_index=True) if pairs else pd.DataFrame()
    return table, columns


def family_descriptors(family, entities, sizes):
    """Study 1's skill, concentration and leave-one-out descriptors of every family row whose
    stratum holds at least two series, available for testing or not; descriptive only."""
    rows = []
    for comparison in family["comparisons"]:
        stratum = comparison["stratum"]
        row = dict(id=comparison["id"], stratum=stratum, n_entities=sizes.get(stratum, 0))
        if row["n_entities"] < 2:
            rows.append(row)
            continue
        pair = study2.paired(
            entities,
            comparison["variant"],
            comparison["reference"],
            comparison["horizon"],
            METRIC,
            (stratum,),
        )
        diff = pair.model_score - pair.reference_score
        skill = 1 - pair.model_score / pair.reference_score.where(pair.reference_score != 0)
        gain = (-diff).clip(lower=0)
        loo = (diff.sum() - diff) / (len(diff) - 1)
        moved = (loo - diff.mean()).abs().idxmax()
        rows.append(
            dict(
                row,
                tests_available=row["n_entities"] >= family["minimum_complete_series_per_stratum"],
                mean_skill=float(skill.mean()),
                median_skill=float(skill.median()),
                skill_defined=int(skill.notna().sum()),
                top_five_share_of_positive_gains=float(gain.nlargest(5).sum() / gain.sum())
                if gain.sum()
                else np.nan,
                leave_one_out_min=float(loo.min()),
                leave_one_out_max=float(loo.max()),
                most_influential_series=moved,
                most_influential_difference=float(diff[moved]),
            )
        )
    return pd.DataFrame(rows)


def contrasts(entities, frame, items, metrics, *, skip_family=False):
    """Unadjusted secondary contrasts, Study 2's interval and test, where two series have both."""
    rows = []
    for item in items:
        for metric in metrics:
            if skip_family and metric == METRIC and item.get("in_family"):
                continue
            pair = study2.paired(
                entities,
                item["variant"],
                item["reference"],
                item["horizon"],
                metric,
                (item["stratum"],),
            )
            available = pair.dropna()
            row = dict(
                id=item["id"],
                stratum=item["stratum"],
                variant=item["variant"],
                reference=item["reference"],
                horizon=int(item["horizon"]),
                metric=metric,
                entity="series",
                n_entities_unavailable=len(pair) - len(available),
            )
            if len(available) >= 2:
                diff = (available.model_score - available.reference_score).to_numpy()
                seed = bootstrap_seed(item, metric)
                result = study2.cluster_contrast(diff, seed=seed, family=FAMILY_SETTINGS)
                row.update(
                    status="secondary",
                    variant_mean=float(available.model_score.mean()),
                    reference_mean=float(available.reference_score.mean()),
                    **result,
                    median_sign=_sign(result["median_diff"]),
                    bootstrap_seed=seed,
                )
            else:
                row.update(
                    status="unavailable" if not len(available) else "fewer_than_two_entities",
                    n_entities=len(available),
                    unavailable_reason=study2._unavailable_reason(
                        frame, (item["variant"], item["reference"]), metric
                    ),
                )
            rows.append(row)
    return pd.DataFrame(rows)


def secondary_items(strata):
    family = {(c["variant"], c["reference"], c["horizon"]) for c in study3_comparisons()}
    items = []
    for stratum in strata:
        for model in MODEL_PINS:
            for horizon in HORIZONS:
                for variant, reference in secondary_pairs(model):
                    items.append(
                        dict(
                            id=f"{stratum}/{variant}/{reference}/h{horizon}",
                            stratum=stratum,
                            variant=variant,
                            reference=reference,
                            horizon=horizon,
                            in_family=(variant, reference, horizon) in family,
                        )
                    )
    return items


def stratified(function, frame, entities, strata):
    """A Study 2 table per stratum, with the stratum as its first column."""
    parts = []
    for stratum in strata:
        windows = frame[frame.stratum.eq(stratum)] if stratum != ALL else frame
        table = function(windows, entities.loc[stratum])
        table.insert(0, "stratum", stratum)
        parts.append(table)
    return pd.concat(parts, ignore_index=True)


def pit_tables(frame, values, strata):
    parts = []
    for stratum in strata:
        if stratum == ALL:
            windows, mine = frame, values
        else:
            series = set(frame.loc[frame.stratum.eq(stratum), "series_id"])
            windows, mine = (
                frame[frame.series_id.isin(series)],
                values[values.series_id.isin(series)],
            )
        table = study2.pit_histograms(windows, mine)
        table.insert(0, "stratum", stratum)
        parts.append(table)
    return pd.concat(parts, ignore_index=True)


# Study 2's test and interval settings for the secondary rows: the registered family's own.
FAMILY_SETTINGS = dict(
    bootstrap_replicates=20000,
    all_zero_p=1.0,
    zero_method="wilcox",
    alternative="two-sided",
    method="approx",
)


def run_inference(run, *, out=None, root=ROOT_DIR, command=None):
    run, root = Path(run), Path(root)
    out = run / "inference" if out is None else Path(out)
    if out.exists():
        raise FileExistsError("Inference outputs are immutable; choose a new directory")
    spec_path, comparisons_path = (root / name for name in STUDY3_FILES)
    spec, family = read_json(spec_path), read_json(comparisons_path)
    validate_study3(spec, family)
    if any(family[k] != FAMILY_SETTINGS[k] for k in FAMILY_SETTINGS):
        raise ValueError("The secondary settings must be the registered family's")
    state, domain, frame, pit_values, checkpoints = read_run(run, family, spec, root)

    series = study2.series_scores(frame, VALUES)
    entities = stratum_entities(series)
    sizes = series.reset_index().drop_duplicates("series_id").stratum.value_counts().to_dict()
    sizes = {s: int(sizes.get(s, 0)) for s in STUDY3_STRATA}
    inference, pairs = family_table(family, entities, sizes)
    descriptors = family_descriptors(family, entities, sizes)
    # An empty stratum has no series to describe; its family rows are reported unavailable.
    present = [s for s in STUDY3_STRATA if sizes[s]]
    strata = [*present, ALL]
    stratum_rows = contrasts(
        entities, frame, secondary_items(present), SECONDARY_METRICS, skip_family=True
    )
    pooled_rows = contrasts(entities, frame, secondary_items([ALL]), SECONDARY_METRICS)
    study2_rows = contrasts(entities, frame, study2_form(), SECONDARY_METRICS)
    form = study2_rows.metric.eq(METRIC) & study2_rows.status.eq("secondary")
    study2_rows["wilcoxon_p_bh_within_table"] = np.nan
    if form.any():
        study2_rows.loc[form, "wilcoxon_p_bh_within_table"] = benjamini_hochberg(
            study2_rows.loc[form, "wilcoxon_p"]
        )
    scores = stratified(study2.score_table, frame, entities, strata)
    accounting = stratified(study2.accounting_table, frame, entities, strata)
    histograms = pit_tables(frame, pit_values, strata)

    tables = {
        "inference.csv": inference,
        "paired_entities.csv": pairs,
        "family_descriptors.csv": descriptors,
        "series_scores.csv": series.reset_index(),
        "secondary_strata_contrasts.csv": stratum_rows,
        "secondary_pooled_contrasts.csv": pooled_rows,
        "secondary_pooled_study2_form.csv": study2_rows,
        "secondary_scores.csv": scores,
        "secondary_accounting.csv": accounting,
        "pit_histograms.csv": histograms,
    }
    out.mkdir(parents=True)
    for name, table in tables.items():
        study2._integers(table).to_csv(out / name, index=False, lineterminator="\n")
    pit_values.to_parquet(out / "pit_values.parquet", index=False)
    settings = dict(
        metric=METRIC,
        entity="series",
        aggregation="origins within series and horizon, then equal series within the stratum",
        difference="variant minus reference; negative favors the variant",
        availability=(
            f"a stratum with fewer than {STUDY3_MINIMUM_SERIES} complete series has its twelve "
            "tests unavailable; BH once over the available tests"
        ),
        strata_sizes=sizes,
        bootstrap=dict(
            replicates=family["bootstrap_replicates"],
            unit="series",
            root=STUDY3_SEEDS["bootstrap"],
            derivation=BOOTSTRAP_DERIVATION,
            draws=f"rng.integers(0, n, size=(block, n)) in blocks of {study2.BLOCK}",
            entity_order="ascending series_id (code point)",
        ),
        interval=dict(
            kind="pointwise percentile",
            confidence=study2.CONFIDENCE,
            numpy_quantile_method=study2.QUANTILE_METHOD,
        ),
        test={k: family[k] for k in ("test", "alternative", "method", "zero_method", "all_zero_p")},
        adjustment=dict(
            method=family["adjustment"],
            q=family["q"],
            declared=family["comparison_count"],
            available=int(inference.status.eq("available").sum()),
            scope="once over the available tests of the family",
        ),
        direction="the median's sign, reported beside the mean; H3's sign beside T1 rows",
        calendar_conditional=family["calendar_conditional"],
    )
    study2._write_json(
        out / "inference.json",
        dict(
            analysis="study3_registered_inference",
            component=COMPONENT,
            domain=domain,
            protocol_sha256=STUDY3_PROTOCOL_SHA256,
            comparison_family=family,
            confirmatory=inference.astype(object).where(inference.notna(), None).to_dict("records"),
            settings=settings,
            secondary=dict(
                status="secondary; no adjustment except the within-table BH column of the "
                "pooled table in Study 2's form; never replaces the family",
                files=sorted(set(tables) - {"inference.csv", "paired_entities.csv"})
                + ["pit_values.parquet"],
            ),
            pit=dict(root=STUDY3_SEEDS["pit"], derivation=PIT_DERIVATION),
        ),
    )
    outputs = sorted(p.name for p in out.iterdir())
    versions = installed_versions()
    study2._write_json(
        out / "provenance.json",
        dict(
            analysis="study3_registered_inference",
            component=COMPONENT,
            written_at=utc_now().isoformat(),
            command=command,
            regeneration=(
                r".\.venv\Scripts\python.exe scripts\study3_inference.py "
                + f"--run {Path(study2._relative(run, root))} --out <new directory>"
            ),
            inference_script_sha256=file_hash(Path(__file__)),
            study2_functions_sha256=file_hash(Path(study2.__file__)),
            implementation_commit_at_inference=study2._git("rev-parse", "HEAD"),
            uncommitted_changes_at_inference=study2._git(
                "status", "--porcelain", "--", "scripts", "pulsegraph"
            ),
            packages={name: versions.get(name) for name in ("numpy", "scipy", "pandas")},
            protocol_sha256=STUDY3_PROTOCOL_SHA256,
            declarations={
                study2._relative(path, root): file_hash(path)
                for path in (spec_path, comparisons_path)
            },
            run=dict(
                directory=study2._relative(run, root),
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
                bootstrap_root=STUDY3_SEEDS["bootstrap"],
                bootstrap_derivation=BOOTSTRAP_DERIVATION,
                pit_root=STUDY3_SEEDS["pit"],
                pit_derivation=PIT_DERIVATION,
                comparison_seeds={
                    r["id"]: r.get("bootstrap_seed") for r in inference.to_dict("records")
                },
            ),
            artifact_sha256={name: file_hash(out / name) for name in outputs},
        ),
    )
    return inference


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="a new directory; default <run>/inference")
    args = parser.parse_args()
    inference = run_inference(args.run, out=args.out, command=[sys.executable, *sys.argv])
    available = int(inference.status.eq("available").sum())
    print(f"Study 3 inference written: {len(inference)} comparisons, {available} available")


if __name__ == "__main__":
    main()

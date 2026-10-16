r"""POST-HOC: each foundation model's completed positive law with dynamic_count's occurrence.

Usage, from the repository root:
    .\.venv\Scripts\python.exe reports\study2-posthoc-dynamic-occurrence\dynamic_occurrence.py
        --npm reports\study2-npm\run-2026-10-15 --synthetic reports\study2-synthetic-2026-10-15

Written on 2026-10-16, after the registered scores of both Study 2 runs were seen. It is outside
the registered analysis: it has no registered status, adds no test to any registered family and
never replaces one. The confirmatory results are each run's inference/, which this command reads
and does not change. Nothing is refitted and no model is loaded; every number comes from the
saved forecasts.

- The wrapper. For foundation model m and each saved window, on each target day,
  H_dyn(0) = 1 - p_dyn and H_dyn(k) = 1 - p_dyn + p_dyn G+(k) for k >= 1, where
  G+(k) = [F(k) - F(0)] / [1 - F(0)] is the positive conditional law of m's saved completed law F
  for that day and p_dyn is the occurrence probability, P(Y > 0), of dynamic_count's saved law for
  that day. This is the registered FM hurdle (PROTOCOL.md, "Models, distributions and controls";
  pulsegraph.study2.distributions.fm_hurdle) with the last-28-day Jeffreys p replaced by p_dyn;
  G+ = delta_1 only when F(0) = 1, as registered. Its deciles are the registered inversion
  (pulsegraph.study2.models.law_forecast) and its QScore9 and accounting parts the registered
  formula (pulsegraph.study2.scores.accounting). The variant is named <model>_dyn.
- p_dyn. dynamic_count is the registered discounted Beta-Bernoulli/Gamma-Poisson hurdle with
  discount 0.98; its occurrence is a_B / (a_B + b_B) at every lead. Where the last 28 context days
  hold fewer than two positive days it falls back to hurdle_count_28 as registered, so p_dyn is
  then the Jeffreys p and the wrapper equals the registered hurdle in that window. Every saved
  dynamic_count law must be a hurdle whose survival at 0 equals its p.
- Checks, all before anything is written. Each run is read by scripts/study2_inference.py's
  read_run: complete, its identity, authorized for the committed family and specification,
  checkpoints exactly the registered series with the bytes run.json records, rows on the
  registered grid. The inference script must be the one each run's inference/provenance.json
  records. The saved scores, through the registered functions, must reproduce the run's
  inference/inference.csv and inference/paired_entities.csv byte for byte. In every window the
  wrapper built with the saved hurdle's Jeffreys p must reproduce the saved hurdle's laws,
  deciles and QScore9 exactly; the wrapper's occurrence Brier score must equal dynamic_count's
  saved one exactly; and every saved context-scaled QScore9 of the completed controls must equal
  its QScore9 / max(1, saved context mean) exactly, the scale the wrapper uses.
- The post-hoc families. For each model m: m_dyn against m_completed, hurdle_count_28,
  dynamic_count and m_hurdle (the registered fixed-window hurdle). npm: both horizons,
  3 x 2 x 4 = 24 tests, DE01 to DE24. Synthetic grid: horizon 30, 3 x 4 = 12 tests, DS01 to DS12.
  Benjamini-Hochberg once over each family at q = 0.05. Neither family shares a correction with
  E01 to E18 or S01 to S06, and neither has registered status.
- Inference: the registered functions of scripts/study2_inference.py, imported unchanged
  (read_run, series_scores, entity_scores, confirmatory, accounting_table, paired, describe).
  npm: origins averaged within series and horizon, the 209 series weighed equally. Grid: origins
  within replicate and cell, then the 18 cells within replicate with equal weight, the 30
  replicate blocks as entities. Differences are model minus reference; two-sided approximate
  Wilcoxon signed-rank test over the entities, zero differences omitted, p = 1 if all are zero;
  20,000 entity bootstrap replicates, pointwise 95% percentile interval; each bootstrap seed by
  the registered derivation (root 20260917) over its post-hoc id. Direction: the side with the
  larger signed-rank sum of the nonzero differences.
- Secondary, with no adjustment: the three accounting parts with the full horizon denominator;
  per-stratum (npm) and per-cell (grid) readings with n on QScore9 and the context-scaled QScore9;
  per stratum or cell, how far p_dyn lies from the Jeffreys p and in how many windows the wrapper
  is the registered hurdle.

Writes, beside the script unless --out names another directory, for each run (prefix npm_ or
synthetic_): inference.csv, paired_entities.csv, window_scores.csv, accounting.csv, groups.csv,
occurrence.csv; and provenance.json with the hash of every input, output and script. Refuses to
overwrite any of them. Prints the Markdown tables of RESULTS-dynamic-occurrence.md.
"""

import argparse
import io
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.evaluation.registration import installed_versions
from pulsegraph.provenance import read_json, sha256_bytes
from pulsegraph.study2.constants import MODEL_PINS
from pulsegraph.study2.declarations import validate
from pulsegraph.study2.distributions import CountLaw, fm_hurdle
from pulsegraph.study2.holdout import utc_now
from pulsegraph.study2.models import law_forecast
from pulsegraph.study2.scores import accounting

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
import scripts.study2_inference as inference  # noqa: E402

COMPONENTS = dict(external_packages="npm", synthetic="synthetic")
PREFIX = dict(external_packages="DE", synthetic="DS")
HORIZONS = dict(external_packages=(7, 30), synthetic=(30,))
GROUP = dict(external_packages="stratum", synthetic="cell_id")
SUFFIX = "_dyn"
DYNAMIC, COUNT = "dynamic_count", "hurdle_count_28"
SCALED = "context_scaled_qscore9"
VALUES = (inference.METRIC, SCALED, *inference.PARTS)
SETTINGS = (
    "adjustment",
    "all_zero_p",
    "alternative",
    "bootstrap_replicates",
    "bootstrap_seed",
    "calendar_conditional",
    "method",
    "metric",
    "q",
    "test",
    "zero_method",
)
TABLES = (
    "inference.csv",
    "paired_entities.csv",
    "window_scores.csv",
    "accounting.csv",
    "groups.csv",
    "occurrence.csv",
)
STATUS = (
    "post-hoc; computed after the registered scores of both runs were seen; no registered "
    "status; adds no test to any registered family and never replaces inference/"
)
CODE = (
    "scripts/study2_inference.py",
    "pulsegraph/study2/distributions.py",
    "pulsegraph/study2/models.py",
    "pulsegraph/study2/scores.py",
)


def references(model):
    """The four references of model m's wrapper, in family order."""
    return (f"{model}_completed", COUNT, DYNAMIC, f"{model}_hurdle")


def posthoc_family(component, registered):
    """The post-hoc family, in the registered family's test, interval and adjustment settings."""
    comparisons = []
    for model in MODEL_PINS:
        for horizon in HORIZONS[component]:
            for reference in references(model):
                comparisons.append(
                    dict(
                        id=f"{PREFIX[component]}{len(comparisons) + 1:02}",
                        domain=inference.DOMAIN[component],
                        model=model + SUFFIX,
                        reference=reference,
                        horizon=horizon,
                    )
                )
    return dict(
        {key: registered[key] for key in SETTINGS},
        component=component,
        status=STATUS,
        comparison_count=len(comparisons),
        comparisons=comparisons,
    )


def counterpart(comparison):
    """The registered row of the fixed-window hurdle against the same reference, if there is one."""
    model = comparison["model"].removesuffix(SUFFIX)
    if comparison["reference"] in (f"{model}_completed", COUNT):
        return (f"{model}_hurdle", comparison["reference"], int(comparison["horizon"]))
    return None


def occurrence_probability(spec):
    """The occurrence probability of a saved hurdle law: its p, which is its P(Y > 0)."""
    p = spec.get("p") if spec.get("kind") == "hurdle" else None
    if p is None or not 0 <= p <= 1 or float(CountLaw(spec).sf(0)) != p:
        raise ValueError("A saved occurrence law is not a hurdle whose P(Y > 0) is its p")
    return float(p)


def wrapper(completed, p):
    """The registered FM hurdle on a saved completed law with occurrence p; delta_1 if F(0) = 1."""
    return fm_hurdle(CountLaw(completed), p)


def wrap_window(row, occurrence):
    """The wrapper's forecast and scores for one saved completed-control window.

    occurrence holds one probability per target day, in lead order.
    """
    specs, target = row["forecast"]["distributions"], row["target"]
    if specs is None or not len(specs) == len(target) == len(occurrence):
        raise ValueError("A completed law and an occurrence probability per target day required")
    laws = [wrapper(spec, p) for spec, p in zip(specs, occurrence, strict=True)]
    forecast = law_forecast(laws)
    result = accounting(target, forecast["deciles"])
    result[SCALED] = result["qscore9"] / max(1.0, float(row["context_mean"]))
    # The registered occurrence Brier score of scores.score, on the wrapper's laws.
    result["occurrence_brier"] = float(
        np.mean([(law.sf(0) - (y > 0)) ** 2 for law, y in zip(laws, target, strict=True)])
    )
    result["f0_equals_one_days"] = sum(law.spec["fallback"] == "F0_equals_one" for law in laws)
    return forecast, result


def checkpoint_windows(component, run, state, label, source=DYNAMIC):
    """Every foundation model's wrapper on one checkpoint, after the reproduction checks.

    source names the saved law that supplies the occurrence probability. It is dynamic_count
    here; the tests also pass hurdle_count_28, whose p is the registered hurdle's Jeffreys p.
    """
    path = run / (sha256_bytes(label.encode()) + ".json")
    if file_hash(path) != state["completed"][label]:
        raise ValueError(f"Checkpoint hash mismatch: {label}")
    document = read_json(path)
    if document.get("identity") != state["identity"]:
        raise ValueError("Checkpoint belongs to a different run")
    saved = {(r["cutoff"], int(r["horizon"]), r["model"]): r for r in document["rows"]}
    rows = []
    for cutoff in inference.ORIGINS[component]:
        for horizon in inference.HORIZONS:
            source_row = saved[(cutoff, horizon, source)]
            specs = source_row["forecast"]["distributions"]
            p_dyn = [occurrence_probability(spec) for spec in specs]
            for model in MODEL_PINS:
                completed = saved[(cutoff, horizon, f"{model}_completed")]
                hurdle = saved[(cutoff, horizon, f"{model}_hurdle")]
                scores, context_mean = completed["scores"], float(completed["context_mean"])
                if scores[SCALED] != scores["qscore9"] / max(1.0, context_mean):
                    raise ValueError("A saved context-scaled QScore9 is not QScore9 over its scale")
                jeffreys = [occurrence_probability(s) for s in hurdle["forecast"]["distributions"]]
                rebuilt, rescored = wrap_window(completed, jeffreys)
                if (
                    rebuilt["distributions"] != hurdle["forecast"]["distributions"]
                    or rebuilt["deciles"] != hurdle["forecast"]["deciles"]
                    or rescored["qscore9"] != hurdle["scores"]["qscore9"]
                ):
                    raise ValueError(
                        "The wrapper with the Jeffreys p does not reproduce the hurdle"
                    )
                forecast, result = wrap_window(completed, p_dyn)
                if result["occurrence_brier"] != source_row["scores"]["occurrence_brier"]:
                    raise ValueError("The wrapper's occurrence differs from its source law's")
                rows.append(
                    dict(
                        series_id=completed["series_id"],
                        cutoff=cutoff,
                        horizon=horizon,
                        model=model + SUFFIX,
                        p_dyn=p_dyn[0],
                        p_dyn_constant=len(set(p_dyn)) == 1,
                        p_jeffreys=jeffreys[0],
                        p_jeffreys_constant=len(set(jeffreys)) == 1,
                        occurrence_fallback=all("discount" not in spec for spec in specs),
                        f0_equals_one_days=result["f0_equals_one_days"],
                        equals_registered_hurdle=forecast["deciles"]
                        == hurdle["forecast"]["deciles"],
                        qscore9=result["qscore9"],
                        registered_hurdle_qscore9=hurdle["scores"]["qscore9"],
                        completed_qscore9=scores["qscore9"],
                        context_scaled_qscore9=result[SCALED],
                        occurrence_brier=result["occurrence_brier"],
                        residual=result["residual"],
                        n_zero=result["n_zero"],
                        n_positive=result["n_positive"],
                        **{part: result["contributions"][part] for part in inference.PARTS},
                    )
                )
    return rows


def csv_text(table):
    """A table as the inference command writes it."""
    buffer = io.StringIO()
    inference._integers(table.copy()).to_csv(buffer, index=False, lineterminator="\n")
    return buffer.getvalue()


def rank_sums(diff):
    diff = np.asarray(diff, dtype=float)
    nonzero = diff[diff != 0]
    ranks = stats.rankdata(np.abs(nonzero))
    below, above = float(ranks[nonzero < 0].sum()), float(ranks[nonzero > 0].sum())
    side = "model" if below > above else "reference" if above > below else "neither"
    return dict(rank_sum_model_lower=below, rank_sum_reference_lower=above, larger_sum_favors=side)


def family_table(component, family, entities, registered):
    """The post-hoc family through the registered confirmatory function, with the directions and,
    where one exists, the registered row of the fixed-window hurdle against the same reference."""
    table, pairs = inference.confirmatory(component, family, entities)
    directions = pd.DataFrame(
        [rank_sums(pairs.loc[pairs.id.eq(cid), "difference"]) for cid in table.id]
    )
    lookup = registered.set_index(["model", "reference", "horizon"])
    names = ("id", "mean_diff", "median_diff", "wins", "ties", "losses", "wilcoxon_p_bh")
    beside = []
    for comparison in family["comparisons"]:
        key = counterpart(comparison)
        row = None if key is None else lookup.loc[key]
        item = {f"registered_{name}": None if row is None else row[name] for name in names}
        item["registered_reject_bh_005"] = None if row is None else bool(row["reject_bh_005"])
        beside.append(item)
    beside = pd.DataFrame(beside)
    for name in ("registered_wins", "registered_ties", "registered_losses"):
        beside[name] = beside[name].astype("Int64")
    table = pd.concat([table, directions, beside], axis=1)
    table.insert(0, "status", "post-hoc")
    return table, pairs


def group_contrasts(component, family, series):
    """Per-stratum (npm) or per-cell (grid) readings of every family row, with n; no test."""
    group = GROUP[component]
    flat = series.reset_index()
    flat[group] = flat[group].fillna("unlabelled")
    entities = flat.set_index([group, "horizon", "model", "series_id"])[list(VALUES)].sort_index()
    rows = []
    for name in sorted(flat[group].unique()):
        for comparison in family["comparisons"]:
            for metric in (inference.METRIC, SCALED):
                pair = inference.paired(
                    entities,
                    comparison["model"],
                    comparison["reference"],
                    comparison["horizon"],
                    metric,
                    (name,),
                ).dropna()
                rows.append(
                    {
                        group: name,
                        **comparison,
                        "metric": metric,
                        "model_mean": float(pair.model_score.mean()) if len(pair) else np.nan,
                        "reference_mean": float(pair.reference_score.mean())
                        if len(pair)
                        else np.nan,
                        **inference.describe(pair.model_score - pair.reference_score),
                    }
                )
    table = pd.DataFrame(rows)
    if component == "synthetic":
        generators = pd.DataFrame(inference.grid_manifest()["cells"])
        table = generators.merge(table, on="cell_id", validate="one_to_many")
    return table


def accounting_rows(component, frame, entities):
    """The three exact parts with the full horizon denominator for the wrappers and the variants
    they are compared with, at the family's horizons."""
    table = inference.accounting_table(frame, entities)
    models = (
        [
            name
            for model in MODEL_PINS
            for name in (model + SUFFIX, f"{model}_hurdle", f"{model}_completed")
        ]
        + [DYNAMIC, COUNT]
        + (["oracle"] if component == "synthetic" else [])
    )
    table = table[table.model.isin(models) & table.horizon.isin(HORIZONS[component])].copy()
    table["order"] = table.model.map({name: i for i, name in enumerate(models)})
    return table.sort_values(["horizon", "order"]).drop(columns="order").reset_index(drop=True)


def occurrence_summary(component, windows):
    """Per stratum or cell and horizon: how far p_dyn lies from the Jeffreys p, how often
    dynamic_count fell back to it, and in how many windows each wrapper is the registered hurdle."""
    group = GROUP[component]
    windows = windows.assign(
        abs_difference=(windows.p_dyn - windows.p_jeffreys).abs(),
        positive_fraction=windows.n_positive / windows.horizon,
    )
    rows = []
    for name, part in [("all", windows), *sorted(windows.groupby(group), key=lambda x: x[0])]:
        for horizon, block in part.groupby("horizon", sort=True):
            # The occurrence probabilities do not depend on the foundation model.
            first = block[block.model.eq(next(iter(MODEL_PINS)) + SUFFIX)]
            row = {
                group: name,
                "horizon": int(horizon),
                "windows": len(first),
                "occurrence_fallback_windows": int(first.occurrence_fallback.sum()),
                "mean_p_dyn": float(first.p_dyn.mean()),
                "mean_p_jeffreys": float(first.p_jeffreys.mean()),
                "mean_abs_p_difference": float(first.abs_difference.mean()),
                "max_abs_p_difference": float(first.abs_difference.max()),
                "mean_positive_fraction": float(first.positive_fraction.mean()),
            }
            for model in MODEL_PINS:
                mine = block[block.model.eq(model + SUFFIX)]
                row[f"{model}_windows_equal_to_hurdle"] = int(mine.equals_registered_hurdle.sum())
                row[f"{model}_f0_equals_one_windows"] = int((mine.f0_equals_one_days > 0).sum())
            rows.append(row)
    return pd.DataFrame(rows)


def run_component(component, run, *, root=ROOT_DIR, source=DYNAMIC):
    """Verify one run, reproduce its registered family, build the wrappers and their family."""
    run, root = Path(run), Path(root)
    comparisons = root / f"study/study2/{component}_comparisons.json"
    spec_path = root / f"study/study2/{component}_spec.json"
    registered_family, spec = read_json(comparisons), read_json(spec_path)
    if (
        validate(spec, registered_family) != component
        or registered_family["component"] != component
    ):
        raise ValueError("The comparison file is not this component's registered family")
    recorded = read_json(run / "inference" / "provenance.json")["inference_script_sha256"]
    if file_hash(Path(inference.__file__)) != recorded:
        raise ValueError(
            "scripts/study2_inference.py differs from the one the run's inference used"
        )
    state, frame, _, checkpoints = inference.read_run(component, run, registered_family, spec, root)
    windows = []
    for label in sorted(state["completed"]):
        windows.extend(checkpoint_windows(component, run, state, label, source))
    windows = pd.DataFrame(windows)
    descriptors = [c for c in ("stratum", "cell_id", "replicate") if c in frame.columns]
    labels = frame.drop_duplicates("series_id").set_index("series_id")[descriptors]
    windows = windows.join(labels, on="series_id")
    expected = len(checkpoints) * len(inference.ORIGINS[component]) * 2 * len(MODEL_PINS)
    if (
        len(windows) != expected
        or windows.duplicated(["series_id", "cutoff", "horizon", "model"]).any()
    ):
        raise ValueError("The wrapper windows are not the registered grid")

    columns = ["series_id", "cutoff", "horizon", "model", *VALUES, "residual", "n_zero"]
    columns += ["n_positive", *descriptors]
    combined = pd.concat([frame[columns], windows[columns]], ignore_index=True)
    series = inference.series_scores(combined, list(VALUES))
    entities = inference.entity_scores(component, series, list(VALUES))

    registered, registered_pairs = inference.confirmatory(component, registered_family, entities)
    reproduced = {
        name: csv_text(table).encode("utf-8") == (run / "inference" / name).read_bytes()
        for name, table in (
            ("inference.csv", registered),
            ("paired_entities.csv", registered_pairs),
        )
    }
    if not all(reproduced.values()):
        raise ValueError(f"The saved scores do not reproduce the registered family: {reproduced}")

    family = posthoc_family(component, registered_family)
    table, pairs = family_table(component, family, entities, registered)
    window_count = len(windows)
    checks = dict(
        registered_family_reproduced_byte_for_byte=reproduced,
        checkpoints_verified=len(checkpoints),
        windows=window_count,
        jeffreys_wrapper_reproduces_registered_hurdle=window_count,
        wrapper_brier_equals_dynamic_count=window_count,
        context_scale_exact=window_count,
        p_dyn_constant_over_leads=int(windows.p_dyn_constant.sum()),
        p_jeffreys_constant_over_leads=int(windows.p_jeffreys_constant.sum()),
        occurrence_fallback_windows=int(windows.occurrence_fallback.sum()),
        f0_equals_one_days=int(windows.f0_equals_one_days.sum()),
        windows_equal_to_registered_hurdle=int(windows.equals_registered_hurdle.sum()),
        fallback_windows_equal_to_registered_hurdle=int(
            (windows.occurrence_fallback & windows.equals_registered_hurdle).sum()
        ),
        max_abs_accounting_residual=float(windows.residual.abs().max()),
    )
    if (
        checks["fallback_windows_equal_to_registered_hurdle"]
        != checks["occurrence_fallback_windows"]
    ):
        raise ValueError("A fallback window's wrapper differs from the registered hurdle")
    tables = {
        "inference.csv": table,
        "paired_entities.csv": pairs,
        "window_scores.csv": windows,
        "accounting.csv": accounting_rows(component, combined, entities),
        "groups.csv": group_contrasts(component, family, series),
        "occurrence.csv": occurrence_summary(component, windows),
    }
    inputs = dict(
        directory=_relative(run, root),
        run_json_sha256=file_hash(run / "run.json"),
        identity=state["identity"],
        implementation_commit=state["metadata"].get("metadata", {}).get("implementation_commit"),
        comparisons=dict(path=_relative(comparisons, root), sha256=file_hash(comparisons)),
        spec=dict(path=_relative(spec_path, root), sha256=file_hash(spec_path)),
        registered_inference={
            name: file_hash(run / "inference" / name)
            for name in ("inference.csv", "paired_entities.csv", "provenance.json")
        },
        checkpoints=len(checkpoints),
        checkpoint_sha256=checkpoints,
    )
    if component == "synthetic":
        manifest = root / "study/study2/grid_manifest.json"
        inputs["grid_manifest"] = dict(path=_relative(manifest, root), sha256=file_hash(manifest))
    else:
        entry = state["metadata"]["readiness"]["panels"]["packages"]["manifest"]
        inputs["manifest"] = dict(path=entry["path"], sha256=entry["sha256"])
    return dict(family=family, tables=tables, checks=checks, inputs=inputs)


def _relative(path, root):
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


def g(x, d=4):
    return "" if pd.isna(x) else f"{x:,.0f}" if abs(x) >= 10000 else f"{x:.{d}g}"


def p(x):
    return "" if pd.isna(x) else f"{x:.3g}"


def _yes(value):
    return "" if pd.isna(value) else "yes" if value else "no"


def family_markdown(table):
    lines = [
        "| ID | Model variant | Reference | h | Model mean | Reference mean | Mean difference "
        "| 95% interval | Median difference | Lower / tied / higher | Raw p | BH p | BH rejects "
        "| Larger rank sum favors |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in table.itertuples():
        lines.append(
            f"| {r.id} | `{r.model}` | `{r.reference}` | {r.horizon} | {g(r.model_mean)} "
            f"| {g(r.reference_mean)} | {g(r.mean_diff)} "
            f"| [{g(r.mean_diff_ci_low)}, {g(r.mean_diff_ci_high)}] | {g(r.median_diff)} "
            f"| {r.wins} / {r.ties} / {r.losses} | {p(r.wilcoxon_p)} | {p(r.wilcoxon_p_bh)} "
            f"| {_yes(r.reject_bh_005)} | {r.larger_sum_favors} |"
        )
    return "\n".join(lines)


def counterpart_markdown(table):
    lines = [
        "| Post-hoc row | Registered row | Mean difference | Median difference "
        "| Lower / tied / higher | BH p | BH rejects |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in table[table.registered_id.notna()].itertuples():
        lines.append(
            f"| {r.id} | {r.registered_id} | {g(r.mean_diff)} / {g(r.registered_mean_diff)} "
            f"| {g(r.median_diff)} / {g(r.registered_median_diff)} "
            f"| {r.wins}-{r.ties}-{r.losses} / {int(r.registered_wins)}-{int(r.registered_ties)}-"
            f"{int(r.registered_losses)} | {p(r.wilcoxon_p_bh)} / {p(r.registered_wilcoxon_p_bh)} "
            f"| {_yes(r.reject_bh_005)} / {_yes(r.registered_reject_bh_005)} |"
        )
    return "\n".join(lines)


def accounting_markdown(table):
    lines = [
        "| Model | h | QScore9 | Zero days | Positive, over | Positive, under | Largest residual |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in table.itertuples():
        lines.append(
            f"| `{r.model}` | {r.horizon} | {g(r.qscore9)} | {g(r.zero)} | {g(r.positive_over)} "
            f"| {g(r.positive_under)} | {r.max_abs_window_residual:.2g} |"
        )
    return "\n".join(lines)


def groups_markdown(component, table, metric):
    group = GROUP[component]
    table = table[table.metric.eq(metric)]
    names = list(dict.fromkeys(table[group]))
    if component == "external_packages":
        n = table.drop_duplicates(group).set_index(group).n_entities
        lines = [
            "| ID | h | Model variant | Reference | "
            + " | ".join(f"{name} (n = {n[name]})" for name in names)
            + " |",
            "|---|---|---|---|" + "---|" * len(names),
        ]
        for cid, rows in table.groupby("id", sort=True):
            rows = rows.set_index(group)
            first = rows.iloc[0]
            cells = [
                f"{g(rows.loc[name, 'mean_diff'])} / {g(rows.loc[name, 'median_diff'])} "
                f"({rows.loc[name, 'wins']} of {rows.loc[name, 'n_entities']})"
                for name in names
            ]
            lines.append(
                f"| {cid} | {first.horizon} | `{first.model}` | `{first.reference}` | "
                + " | ".join(cells)
                + " |"
            )
        return "\n".join(lines)
    ids = list(dict.fromkeys(table.id))
    lines = [
        "| Cell | Zero probability | Positive mean | Persistence | " + " | ".join(ids) + " |",
        "|---|---|---|---|" + "---|" * len(ids),
    ]
    for name in names:
        rows = table[table[group].eq(name)].set_index("id")
        first = rows.iloc[0]
        cells = [f"{g(rows.loc[i, 'mean_diff'])} ({rows.loc[i, 'wins']})" for i in ids]
        lines.append(
            f"| {name} | {g(first.zero_probability)} | {g(first.positive_mean)} "
            f"| {g(first.persistence)} | " + " | ".join(cells) + " |"
        )
    return "\n".join(lines)


def occurrence_markdown(component, table):
    group = GROUP[component]
    models = list(MODEL_PINS)
    lines = [
        f"| {group} | h | Windows | dynamic_count fell back | Mean p_dyn | Mean Jeffreys p "
        "| Mean abs. difference | Largest abs. difference | Positive fraction of target days "
        "| Wrapper equals the registered hurdle (" + " / ".join(models) + ") |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in table.itertuples():
        same = " / ".join(str(getattr(r, f"{m}_windows_equal_to_hurdle")) for m in models)
        lines.append(
            f"| {getattr(r, group)} | {r.horizon} | {r.windows} | {r.occurrence_fallback_windows} "
            f"| {r.mean_p_dyn:.3f} | {r.mean_p_jeffreys:.3f} | {r.mean_abs_p_difference:.3f} "
            f"| {r.max_abs_p_difference:.3f} | {r.mean_positive_fraction:.3f} | {same} |"
        )
    return "\n".join(lines)


def run_all(npm, synthetic, *, out, root=ROOT_DIR, command=None):
    """Both runs, every check, then the outputs; nothing is written unless every check passes."""
    out = Path(out)
    names = [f"{COMPONENTS[c]}_{t}" for c in COMPONENTS for t in TABLES] + ["provenance.json"]
    for name in names:
        if (out / name).exists():
            raise FileExistsError("refusing to overwrite " + str(out / name))
    started = utc_now()
    results = {
        component: run_component(component, run, root=root)
        for component, run in (("external_packages", npm), ("synthetic", synthetic))
    }
    out.mkdir(parents=True, exist_ok=True)
    for component, result in results.items():
        for name, table in result["tables"].items():
            path = out / f"{COMPONENTS[component]}_{name}"
            path.write_text(csv_text(table), encoding="utf-8", newline="\n")
    versions = installed_versions()
    script = Path(__file__).resolve()
    inference._write_json(
        out / "provenance.json",
        dict(
            analysis="study2_posthoc_dynamic_occurrence",
            status=STATUS,
            started_at=started.isoformat(),
            written_at=utc_now().isoformat(),
            command=command,
            regeneration=(
                r".\.venv\Scripts\python.exe reports\study2-posthoc-dynamic-occurrence"
                r"\dynamic_occurrence.py --npm reports\study2-npm\run-2026-10-15 --synthetic "
                r"reports\study2-synthetic-2026-10-15 --out <new directory>"
            ),
            script=dict(path=_relative(script, ROOT_DIR), sha256=file_hash(script)),
            code_sha256={name: file_hash(ROOT_DIR / name) for name in CODE},
            head=_git("rev-parse", "HEAD"),
            uncommitted_changes=_git(
                "status", "--porcelain", "--", "scripts/study2_inference.py", "pulsegraph"
            ),
            packages={name: versions.get(name) for name in ("numpy", "scipy", "pandas")},
            wrapper=(
                "H_dyn(0) = 1 - p_dyn, H_dyn(k) = 1 - p_dyn + p_dyn G+(k), G+ the positive "
                "conditional law of the model's saved completed law for the target day, p_dyn "
                "the P(Y > 0) of dynamic_count's saved law for that day; G+ = delta_1 when "
                "F(0) = 1; pulsegraph.study2.distributions.fm_hurdle and "
                "pulsegraph.study2.models.law_forecast"
            ),
            inference=dict(
                functions="scripts/study2_inference.py: read_run, series_scores, entity_scores, "
                "confirmatory, accounting_table, paired, describe",
                bootstrap_seeds="pulsegraph.random.derived_seed(20260917, component, id, domain, "
                "model, reference, horizon, 'qscore9'), the registered derivation over the "
                "post-hoc ids",
                adjustment="Benjamini-Hochberg once over each post-hoc family at q = 0.05",
                direction="the side with the larger signed-rank sum of the nonzero differences",
            ),
            runs={
                COMPONENTS[c]: dict(r["inputs"], family=r["family"], checks=r["checks"])
                for c, r in results.items()
            },
            outputs={name: file_hash(out / name) for name in names[:-1]},
        ),
    )
    return results


def print_tables(results):
    for component, result in results.items():
        tables, name = result["tables"], COMPONENTS[component]
        print(f"## {name}: the post-hoc family\n")
        print(family_markdown(tables["inference.csv"]))
        print(f"\n## {name}: beside the registered fixed-window hurdle (post-hoc / registered)\n")
        print(counterpart_markdown(tables["inference.csv"]))
        print(f"\n## {name}: accounting\n")
        print(accounting_markdown(tables["accounting.csv"]))
        for metric in (inference.METRIC, SCALED):
            print(f"\n## {name}: per {GROUP[component]}, {metric}\n")
            print(groups_markdown(component, tables["groups.csv"], metric))
        print(f"\n## {name}: occurrence\n")
        print(occurrence_markdown(component, tables["occurrence.csv"]))
        print(f"\n## {name}: checks\n")
        for key, value in result["checks"].items():
            print(f"- {key}: {value}")
        print()


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--npm", type=Path, required=True, help="the npm run directory")
    parser.add_argument("--synthetic", type=Path, required=True, help="the grid run directory")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT_DIR,
        help="the repository whose study/study2/ holds the committed families (default: this one)",
    )
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    try:
        results = run_all(
            args.npm,
            args.synthetic,
            out=args.out,
            root=args.root,
            command=[sys.executable, *sys.argv],
        )
    except FileExistsError as error:
        raise SystemExit(str(error)) from None
    print_tables(results)
    for name, digest in read_json(args.out / "provenance.json")["outputs"].items():
        print(name, digest)


if __name__ == "__main__":
    main()

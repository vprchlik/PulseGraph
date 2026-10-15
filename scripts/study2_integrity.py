"""Study 2 per-forecast score recomputation from a finished run directory; nothing is refitted.

scripts/study2_inference.py takes each saved QScore9 as the run saved it. This command, run on
the same run directory beside it, recomputes every saved forecast's scores from the saved deciles,
target days and count laws alone and compares them with the saved values, as Study 1's integrity
review does for Study 1 (pulsegraph/evaluation/artifacts.py, validate_results). It writes
<run>/integrity/ (or a new --out directory): integrity.csv, one row per forecast with the saved
and recomputed values and the residual; integrity.json, the result, the grid counts, the maximum
residuals, the CRPS availability counts, this script's hash and the time; integrity.log. Nothing
else in the run directory is changed. The registered text is PROTOCOL.md, "Scores and
descriptive analyses" (QScore9) and "Scores and the single external-domain confirmatory family"
(QScore9 primary, the scaled score, the occurrence Brier score, the three accounting parts,
availability), with the dated addition of 2026-10-15 (CRPS availability).

- Refused before anything is written: a run that is not complete, whose metadata does not give
  its identity, of another component, whose checkpoints are not exactly the registered series,
  whose checkpoint bytes differ from the SHA-256 recorded in run.json, or whose rows are not the
  registered grid (every series, origin, horizon and variant exactly once).
- QScore9 = 2 / (9 h) times the summed pinball losses over the h target days and the deciles
  tau = 0.1, ..., 0.9, pinball(e, tau) = max(tau e, (tau - 1) e) with e = y - q.
- Accounting: the same sum split into zero target days, positive days with the decile above the
  target (positive_over) and positive days with the decile at or below it (positive_under), each
  over the full denominator 9 h, so the three parts sum to QScore9; with the zero and positive
  day counts.
- Scaled score: QScore9 / max(1, context mean), with the context mean as the row saved it.
- Occurrence Brier score, where a count law is saved for every target day: the mean over days of
  (P(Y > 0) - 1[y > 0])^2, with P(Y > 0) evaluated from each saved law's registered definition
  (occurrence_probability), not through the run's distribution code.
- Tolerance: a saved and a recomputed score agree when |saved - recomputed| <= 1e-12 + 1e-10
  |recomputed|, NumPy's isclose with Study 1's settings; day counts must be equal.
- CRPS availability: counted per horizon and model from the saved reasons, and each forecast's
  reason must agree with its saved law and value (no law: no_count_distribution; certified: a
  value with a residual bound below 1e-8; otherwise crps_bound_not_certified). The discrete CRPS
  values themselves are not recomputed.
"""

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.evaluation.registration import installed_versions
from pulsegraph.provenance import read_json, sha256_bytes
from pulsegraph.study2.constants import CUTOFFS, VARIANTS
from pulsegraph.study2.holdout import utc_now
from pulsegraph.study2.runner import resume_identity
from pulsegraph.study2.scores import CRPS_UNCERTIFIED, NO_DISTRIBUTION
from pulsegraph.study2.synthetic import grid_manifest

COMPONENTS = ("external_packages", "synthetic")
DOMAIN = dict(external_packages="packages", synthetic="synthetic")
ORIGINS = dict(external_packages=list(CUTOFFS), synthetic=["180", "210", "240"])
HORIZONS = (7, 30)
TAUS = np.arange(1, 10) / 10
RTOL, ATOL = 1e-10, 1e-12
CRPS_TOLERANCE = 1e-8
PARTS = ("zero", "positive_over", "positive_under")
SCORES = ("qscore9", *PARTS, "context_scaled_qscore9", "occurrence_brier")
DAY_COUNTS = ("n_zero", "n_positive")
WINDOW = ["series_id", "cutoff", "horizon", "model"]
FAILURES_LISTED = 100
COLUMNS = [
    "domain",
    *WINDOW,
    "has_law",
    "valid_arrays",
    *(f"{name}_{kind}" for name in SCORES for kind in ("saved", "recomputed", "residual")),
    *(f"{name}_{kind}" for name in DAY_COUNTS for kind in ("saved", "recomputed")),
    "identity_residual",
    "saved_identity_residual",
    "crps_unavailable_reason",
    "discrete_crps_saved",
    "crps_max_residual_bound_saved",
    "crps_consistent",
    "passed",
    "reasons",
]
DEFINITIONS = dict(
    qscore9=(
        "2 / (9 h) times the sum over the h target days and tau = 0.1, ..., 0.9 of "
        "max(tau e, (tau - 1) e), e = y - q_tau"
    ),
    accounting=(
        "the same sum over zero target days (zero), over positive days with e < 0 "
        "(positive_over) and over positive days with e >= 0 (positive_under), each divided by "
        "the full 9 h; the three parts sum to QScore9"
    ),
    context_scaled_qscore9="QScore9 / max(1, the context mean saved in the row)",
    occurrence_brier=(
        "mean over target days of (P(Y > 0) - 1[y > 0])^2, P(Y > 0) from each saved count "
        "law's registered definition; only where a law is saved for every target day"
    ),
    crps_availability=(
        "counted from the saved reasons; no law requires no_count_distribution and no value, "
        "a certified value requires no reason and a residual bound below 1e-8, otherwise the "
        "reason is crps_bound_not_certified with no value; CRPS values are not recomputed"
    ),
)


def recompute_qscore9(target, deciles):
    """QScore9 and its three exact parts from the registered formula, term by term."""
    y, q = np.asarray(target, dtype=float), np.asarray(deciles, dtype=float)
    if y.ndim != 1 or not len(y) or q.shape != (len(y), 9):
        raise ValueError("Saved deciles are not nine per target day")
    e = y[:, None] - q
    # pinball(e, tau) = max(tau e, (tau - 1) e): tau e when e >= 0, (tau - 1) e when e < 0.
    loss = np.where(e >= 0, TAUS * e, (TAUS - 1) * e)
    zero_day = np.broadcast_to((y == 0)[:, None], e.shape)
    denominator = 9 * len(y)
    return dict(
        qscore9=float(2 * loss.sum() / denominator),
        zero=float(2 * loss[zero_day].sum() / denominator),
        positive_over=float(2 * loss[~zero_day & (e < 0)].sum() / denominator),
        positive_under=float(2 * loss[~zero_day & (e >= 0)].sum() / denominator),
        n_zero=int((y == 0).sum()),
        n_positive=int((y > 0).sum()),
    )


def valid_arrays(target, deciles, horizon):
    """The saved arrays are what the scorer accepts: integer targets and repaired deciles."""
    try:
        y, q = np.asarray(target, dtype=float), np.asarray(deciles, dtype=float)
    except (TypeError, ValueError):
        return False
    return bool(
        y.shape == (horizon,)
        and q.shape == (horizon, 9)
        and np.isfinite(y).all()
        and np.isfinite(q).all()
        and (y >= 0).all()
        and (y == np.floor(y)).all()
        and (q >= 0).all()
        and (np.diff(q, axis=1) >= 0).all()
    )


def occurrence_probability(spec):
    """P(Y > 0) of one saved count law, from the law's registered definition.

    PROTOCOL.md, "Models, distributions and controls" (the count baselines, the completion and
    the FM hurdle) and "Synthetic intervention component" (the oracle). Written apart from
    pulsegraph/study2/distributions.py, so the occurrence Brier score is not recomputed through
    the code that produced it.
    """
    kind = spec["kind"]
    if kind == "point":
        return float(spec["value"] > 0)
    if kind in ("poisson", "nb"):
        # Y = shift + X with X >= 0: positive for every X once shift >= 1, else unless X = 0.
        shift = spec.get("shift", 0)
        if shift >= 1:
            return 1.0
        if shift != 0:
            raise ValueError("Unregistered count-law shift")
        if kind == "poisson":
            return -math.expm1(-spec["mu"])  # 1 - exp(-mu)
        # SciPy's nbinom(n, p) has P(X = 0) = p ** n.
        return -math.expm1(spec["shape"] * math.log(spec["probability"]))
    if kind == "empirical":
        values = spec["values"]
        return sum(value > 0 for value in values) / len(values)
    if kind == "completed":
        knots = [0.0, *spec["deciles"]]
        if len(knots) != 10:
            raise ValueError("A completed law needs nine deciles")
        # Y = max(0, floor(Q(U) + 0.5)) is positive exactly when Q(U) >= 0.5. Q interpolates
        # linearly through (0, 0) and (k / 10, q_k) up to u = 0.9, so it first reaches 0.5 on
        # the first segment whose right knot is at least 0.5.
        for k in range(1, 10):
            if knots[k] >= 0.5:
                u = (k - 1) / 10 + 0.1 * (0.5 - knots[k - 1]) / (knots[k] - knots[k - 1])
                return 1 - u
        # Above u = 0.9, Q(u) = q_0.9 + s log(0.1 / (1 - u)) with s = max(1, q_0.9 - q_0.8)
        # reaches 0.5 where 1 - u = 0.1 exp(-(0.5 - q_0.9) / s).
        scale = max(1.0, knots[9] - knots[8])
        return 0.1 * math.exp(-(0.5 - knots[9]) / scale)
    if kind == "positive":
        return 1.0  # the base law conditioned on Y >= 1
    if kind == "hurdle":
        return spec["p"] * occurrence_probability(spec["positive"])
    raise ValueError("Unknown saved count law")


def occurrence_brier(laws, target):
    if len(laws) != len(target):
        raise ValueError("Saved count laws are not one per target day")
    total = 0.0
    for spec, y in zip(laws, target, strict=True):
        p = occurrence_probability(spec)
        if not 0 <= p <= 1:
            raise ValueError("A saved count law gives no probability of a positive day")
        total += (p - float(y > 0)) ** 2
    return total / len(target)


def crps_consistent(has_law, reason, value, bound):
    """The saved CRPS reason agrees with the saved law and value (dated addition 2026-10-15)."""
    if not has_law:
        return reason == NO_DISTRIBUTION and value is None
    if reason is None:
        return (
            value is not None
            and math.isfinite(value)
            and bound is not None
            and bound < CRPS_TOLERANCE
        )
    return reason == CRPS_UNCERTIFIED and value is None


def forecast_record(row):
    """The saved and the recomputed scores of one saved forecast, before any comparison."""
    scores, forecast = row["scores"], row["forecast"]
    laws = forecast.get("distributions")
    record = dict(
        domain=row["domain"],
        series_id=row["series_id"],
        cutoff=row["cutoff"],
        horizon=row["horizon"],
        model=row["model"],
        has_law=laws is not None,
        valid_arrays=valid_arrays(row["target"], forecast["deciles"], row["horizon"]),
    )
    errors = []
    try:
        mine = recompute_qscore9(row["target"], forecast["deciles"])
    except ValueError as error:
        mine = dict.fromkeys(("qscore9", *PARTS, *DAY_COUNTS), np.nan)
        errors.append(str(error))
    mine["context_scaled_qscore9"] = mine["qscore9"] / max(1.0, float(row["context_mean"]))
    mine["occurrence_brier"] = None
    if laws is not None:
        try:
            mine["occurrence_brier"] = occurrence_brier(laws, row["target"])
        except ValueError as error:
            mine["occurrence_brier"] = np.nan
            errors.append(str(error))
    saved = dict(
        qscore9=scores["qscore9"],
        **{part: scores["contributions"][part] for part in PARTS},
        context_scaled_qscore9=scores["context_scaled_qscore9"],
        occurrence_brier=scores["occurrence_brier"],
    )
    for name in SCORES:
        record[f"{name}_saved"] = np.nan if saved[name] is None else float(saved[name])
        record[f"{name}_recomputed"] = np.nan if mine[name] is None else float(mine[name])
    for name in DAY_COUNTS:
        record[f"{name}_saved"] = int(scores[name])
        record[f"{name}_recomputed"] = mine[name]
    record["saved_identity_residual"] = float(scores["residual"])
    reason, value = scores["crps_unavailable_reason"], scores["discrete_crps"]
    bound = scores.get("crps_max_residual_bound")
    record.update(
        crps_unavailable_reason=reason,
        discrete_crps_saved=value,
        crps_max_residual_bound_saved=bound,
        crps_consistent=crps_consistent(laws is not None, reason, value, bound),
        error="; ".join(errors),
    )
    return record


def judge(table):
    """Residuals, agreement at the stated tolerance, and every failing check named per row."""
    failures = {"saved target or deciles are not valid scoring arrays": ~table.valid_arrays}
    for name in SCORES:
        saved, mine = table[f"{name}_saved"], table[f"{name}_recomputed"]
        table[f"{name}_residual"] = mine - saved
        agree = np.isclose(saved, mine, rtol=RTOL, atol=ATOL) | (saved.isna() & mine.isna())
        failures[f"{name} differs from the saved value"] = ~np.asarray(agree)
    for name in DAY_COUNTS:
        failures[f"{name} differs from the saved count"] = table[f"{name}_saved"].ne(
            table[f"{name}_recomputed"]
        )
    table["identity_residual"] = (
        table.zero_recomputed
        + table.positive_over_recomputed
        + table.positive_under_recomputed
        - table.qscore9_recomputed
    )
    failures["the recomputed parts do not sum to QScore9"] = ~(
        table.identity_residual.abs() <= ATOL + RTOL * table.qscore9_recomputed.abs()
    )
    failures["the saved parts do not sum to the saved QScore9"] = ~(
        table.saved_identity_residual.abs() <= ATOL + RTOL * table.qscore9_saved.abs()
    )
    failures[
        "the saved CRPS availability disagrees with the saved law and value"
    ] = ~table.crps_consistent
    flags = pd.DataFrame({k: np.asarray(v, dtype=bool) for k, v in failures.items()})
    messages = np.asarray(flags.columns)
    table["reasons"] = [
        "; ".join([*filter(None, [error]), *messages[mask]])
        for error, mask in zip(table.error, flags.to_numpy(), strict=True)
    ]
    table["passed"] = table.reasons.eq("")
    flags["the score could not be recomputed"] = table.error.ne("").to_numpy()
    return table, flags


def crps_availability(table):
    """Per horizon and model: forecasts, those with a count law, those certified, and the
    unavailable ones by reason, from the saved reasons alone."""
    rows = []
    for (horizon, model), group in table.groupby(["horizon", "model"], sort=True):
        reasons = group.crps_unavailable_reason
        rows.append(
            dict(
                horizon=int(horizon),
                model=model,
                crps_forecasts=len(group),
                crps_with_count_distribution=int(reasons.ne(NO_DISTRIBUTION).sum()),
                crps_certified=int(group.discrete_crps_saved.notna().sum()),
                crps_unavailable_no_count_distribution=int(reasons.eq(NO_DISTRIBUTION).sum()),
                crps_unavailable_bound_not_certified=int(reasons.eq(CRPS_UNCERTIFIED).sum()),
                crps_inconsistent=int((~group.crps_consistent).sum()),
            )
        )
    total = {
        key: sum(row[key] for row in rows) for key in rows[0] if key not in ("horizon", "model")
    }
    return dict(total=total, by_horizon_model=rows)


def registered_series(component, metadata, root):
    """The component's registered series, read here apart from the inference command."""
    if component == "synthetic":
        manifest = grid_manifest()
        if read_json(root / "study/study2/grid_manifest.json") != manifest:
            raise ValueError("Synthetic grid manifest differs from registration")
        series = [row["series_id"] for row in manifest["series"]]
    else:
        panels = metadata.get("readiness", {}).get("panels", {})
        if set(panels) != {"packages"}:
            raise ValueError("The packages component takes the packages panel alone")
        entry = panels["packages"]["manifest"]
        path = root / entry["path"]
        if file_hash(path) != entry["sha256"]:
            raise ValueError("The run's manifest changed")
        series = [row["series_id"] for row in read_json(path)["series"]]
    if not series or len(series) != len(set(series)):
        raise ValueError("The registered series must be nonempty and unique")
    return sorted(series)


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


def _largest(series):
    return float(series.abs().max()) if series.notna().any() else None


def check_run(component, run, *, out=None, root=ROOT_DIR, command=None):
    if component not in COMPONENTS:
        raise ValueError("The integrity check covers external_packages and synthetic only")
    run, root = Path(run), Path(root)
    out = run / "integrity" if out is None else Path(out)
    if out.exists():
        raise FileExistsError("Integrity outputs are immutable; choose a new directory")
    log = []

    def note(message):
        log.append(f"{utc_now().isoformat(timespec='seconds')} {message}")

    note(f"start: component {component}, run {_relative(run, root)}")
    state = read_json(run / "run.json")
    if state.get("status") != "complete":
        raise ValueError("The integrity check requires a complete run")
    metadata = state["metadata"]
    if resume_identity(metadata) != state["identity"]:
        raise ValueError("Run metadata does not match the run identity")
    if metadata.get("readiness", {}).get("action") != component:
        raise ValueError("The run is not a run of this component")
    series = registered_series(component, metadata, root)
    domain = DOMAIN[component]
    labels = {json.dumps([domain, key], separators=(",", ":")): key for key in series}
    if set(state["completed"]) != set(labels):
        missing = len(set(labels) - set(state["completed"]))
        extra = len(set(state["completed"]) - set(labels))
        raise ValueError(
            "The run's checkpoints differ from the registered series: "
            f"{missing} registered series missing, {extra} not registered"
        )
    models = list(VARIANTS) + (["oracle"] if component == "synthetic" else [])
    expected = {
        (key, cutoff, horizon, model)
        for key in series
        for cutoff in ORIGINS[component]
        for horizon in HORIZONS
        for model in models
    }
    note(
        f"run.json: status complete, identity {state['identity']}; registered grid "
        f"{len(series)} series x {len(ORIGINS[component])} origins x {len(HORIZONS)} horizons "
        f"x {len(models)} variants = {len(expected)} forecasts"
    )

    records, seen, checkpoints = [], set(), {}
    for label in sorted(labels):
        name = sha256_bytes(label.encode()) + ".json"
        path = run / name
        if not path.is_file() or file_hash(path) != state["completed"][label]:
            raise ValueError(f"Checkpoint hash mismatch: {name} ({label})")
        checkpoints[label] = state["completed"][label]
        document = read_json(path)
        if document.get("identity") != state["identity"]:
            raise ValueError(f"Checkpoint belongs to a different run: {name} ({label})")
        for row in document["rows"]:
            window = (row["series_id"], row["cutoff"], row["horizon"], row["model"])
            if row["domain"] != domain or row["series_id"] != labels[label]:
                raise ValueError(f"Checkpoint row outside its series: {window} in {label}")
            if window not in expected:
                raise ValueError(f"Checkpoint row outside the registered grid: {window}")
            if window in seen:
                raise ValueError(f"The run's grid has a duplicate forecast: {window}")
            seen.add(window)
            records.append(forecast_record(row))
    missing = sorted(expected - seen)
    if missing:
        raise ValueError(
            f"The run's grid is incomplete: {len(missing)} registered forecasts missing, "
            f"the first {missing[0]}"
        )
    note(
        f"checkpoints: {len(checkpoints)} of {len(checkpoints)} hashes equal run.json; "
        f"{len(seen)} forecasts, every registered window exactly once"
    )

    table = pd.DataFrame.from_records(records)
    table, flags = judge(table)
    table = table.sort_values(WINDOW, kind="stable").reset_index(drop=True)
    for name in DAY_COUNTS:
        table[f"{name}_recomputed"] = table[f"{name}_recomputed"].astype("Int64")
    checks = {}
    for name in SCORES:
        mine, residual = table[f"{name}_recomputed"], table[f"{name}_residual"]
        compared = table[f"{name}_saved"].notna() | mine.notna()
        allowed = ATOL + RTOL * mine.abs()
        checks[name] = dict(
            compared=int(compared.sum()),
            disagreements=int(flags[f"{name} differs from the saved value"].sum()),
            max_abs_residual=_largest(residual),
            max_residual_over_tolerance=_largest(residual / allowed),
        )
        note(
            f"{name}: {checks[name]['compared']} compared, {checks[name]['disagreements']} "
            f"disagree, max |residual| {checks[name]['max_abs_residual']}"
        )
    checks.update(
        identity=dict(
            max_abs_recomputed=_largest(table.identity_residual),
            max_abs_saved=_largest(table.saved_identity_residual),
            recomputed_failures=int(flags["the recomputed parts do not sum to QScore9"].sum()),
            saved_failures=int(flags["the saved parts do not sum to the saved QScore9"].sum()),
        ),
        day_counts=dict(
            zero_days=int(table.n_zero_saved.sum()),
            positive_days=int(table.n_positive_saved.sum()),
            disagreements=int(
                (
                    flags["n_zero differs from the saved count"]
                    | flags["n_positive differs from the saved count"]
                ).sum()
            ),
        ),
        invalid_arrays=int(flags["saved target or deciles are not valid scoring arrays"].sum()),
        not_recomputed=int(flags["the score could not be recomputed"].sum()),
    )
    availability = crps_availability(table)
    note(f"CRPS availability from the saved reasons: {availability['total']}")
    failed = table[~table.passed]
    status = "pass" if failed.empty else "fail"
    note(f"result: {status} ({len(failed)} of {len(table)} forecasts failed)")

    out.mkdir(parents=True)
    table[COLUMNS].to_csv(out / "integrity.csv", index=False, lineterminator="\n")
    note(f"wrote integrity.csv, sha256 {file_hash(out / 'integrity.csv')}")
    (out / "integrity.log").write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    versions = installed_versions()
    summary = dict(
        analysis="study2_score_integrity",
        component=component,
        status=status,
        written_at=utc_now().isoformat(),
        command=command,
        regeneration=(
            r".\.venv\Scripts\python.exe scripts\study2_integrity.py "
            + f"{component} --run {Path(_relative(run, root))} --out <new directory>"
        ),
        integrity_script_sha256=file_hash(Path(__file__)),
        implementation_commit_at_check=_git("rev-parse", "HEAD"),
        uncommitted_changes_at_check=_git(
            "status", "--porcelain", "--", "scripts/study2_integrity.py", "pulsegraph"
        ),
        packages={name: versions.get(name) for name in ("numpy", "scipy", "pandas")},
        run=dict(
            directory=_relative(run, root),
            run_json_sha256=file_hash(run / "run.json"),
            identity=state["identity"],
            implementation_commit=metadata.get("metadata", {}).get("implementation_commit"),
            readiness_sha256=metadata.get("readiness_sha256"),
            checkpoints=len(checkpoints),
            checkpoint_sha256=checkpoints,
        ),
        grid=dict(
            series=len(series),
            origins=ORIGINS[component],
            horizons=list(HORIZONS),
            models=models,
            registered_forecasts=len(expected),
            forecasts=len(table),
            with_count_law=int(table.has_law.sum()),
            without_count_law=int((~table.has_law).sum()),
        ),
        tolerance=dict(
            rtol=RTOL,
            atol=ATOL,
            rule="numpy.isclose(saved, recomputed, rtol, atol): "
            "|saved - recomputed| <= atol + rtol |recomputed|",
            day_counts="equal",
            source="Study 1's recomputation settings, pulsegraph/evaluation/artifacts.py",
        ),
        definitions=DEFINITIONS,
        checks=checks,
        crps_availability=availability,
        failed_forecasts=len(failed),
        failures=failed[[*WINDOW, "reasons"]].head(FAILURES_LISTED).to_dict("records"),
        outputs={name: file_hash(out / name) for name in ("integrity.csv", "integrity.log")},
    )
    _write_json(out / "integrity.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("component", choices=COMPONENTS)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="a new directory; default <run>/integrity")
    args = parser.parse_args()
    try:
        summary = check_run(
            args.component, args.run, out=args.out, command=[sys.executable, *sys.argv]
        )
    except (ValueError, FileExistsError) as error:
        print(f"Study 2 integrity check refused: {error}", file=sys.stderr)
        return 2
    print(
        f"Study 2 {args.component} integrity: {summary['status']}; "
        f"{summary['failed_forecasts']} of {summary['grid']['forecasts']} forecasts failed"
    )
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

r"""Study 3 per-forecast score recomputation from a finished run directory; nothing is refitted.

Usage, from the repository root:
    .\.venv\Scripts\python.exe scripts\study3_integrity.py --run <run directory> [--out <new>]

Study 2's per-row recomputation (scripts/study2_integrity.py), imported unchanged, on Study 3's
grid: every series of the run's frozen manifest, the three origins, both horizons and the 22
saved variants (Study 2's sixteen and, for each model, hurdle_dynamic and
occurrence_model_size_count). Each saved forecast's QScore9, its three accounting parts, the
context-scaled QScore9 and the occurrence Brier score are recomputed from the saved deciles,
targets and laws, with P(Y > 0) of each saved law from the registered definitions written apart
from pulsegraph/study2/distributions.py, and the CRPS availability is checked from the saved
reasons. For the two new variants the structure PROTOCOL.md's dated addition of 2026-10-16,
item 7, registers is also checked on every target day of every window, from the saved laws:

- <model>_hurdle_dynamic: its P(Y > 0) equals that of dynamic_count's saved law for the same
  window and day, and its positive law is the model's saved completed law conditioned on Y >= 1,
  or delta_1 exactly where that completed law has P(Y > 0) = 0 (F(0) = 1).
- <model>_occurrence_model_size_count: its P(Y > 0) equals that of the model's saved completed
  law, 1 - F(0), and its positive law is hurdle_count_28's for the same window.

Probabilities agree at the script's tolerance (numpy.isclose, rtol 1e-10, atol 1e-12). Writes
<run>/integrity/ (or a new --out directory): integrity.csv, integrity.json, integrity.log.
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
from pulsegraph.provenance import read_json, sha256_bytes
from pulsegraph.study2.constants import (
    CUTOFFS,
    MODEL_PINS,
    STUDY3_DOMAIN,
    STUDY3_FALLBACK_DOMAIN,
    STUDY3_VARIANTS,
)
from pulsegraph.study2.holdout import utc_now
from pulsegraph.study2.runner import resume_identity

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
import scripts.study2_integrity as study2  # noqa: E402

COMPONENT = "study3"
HORIZONS = study2.HORIZONS
COLUMNS = [*study2.COLUMNS, "structure"]
STRUCTURE = dict(
    hurdle_dynamic=(
        "P(Y > 0) equals dynamic_count's on every target day; the positive law is the saved "
        "completed law conditioned on Y >= 1, or delta_1 exactly where that law has P(Y > 0) = 0"
    ),
    occurrence_model_size_count=(
        "P(Y > 0) equals the saved completed law's on every target day; the positive law is "
        "hurdle_count_28's"
    ),
)


def _close(a, b):
    return bool(np.isclose(a, b, rtol=study2.RTOL, atol=study2.ATOL))


def structure(rows):
    """Failures of the two new variants' registered structure in one checkpoint, by window."""
    saved = {(r["cutoff"], r["horizon"], r["model"]): r for r in rows}
    failures, checked = {}, 0
    for (cutoff, horizon, name), row in saved.items():
        for model in MODEL_PINS:
            kind = name.removeprefix(model + "_") if name.startswith(model + "_") else None
            if kind not in STRUCTURE:
                continue
            checked += 1
            laws = row["forecast"].get("distributions") or []
            completed = saved[(cutoff, horizon, f"{model}_completed")]["forecast"]["distributions"]
            source = "dynamic_count" if kind == "hurdle_dynamic" else "hurdle_count_28"
            other = saved[(cutoff, horizon, source)]["forecast"]["distributions"]
            problems = []
            if not len(laws) == len(completed) == len(other) == horizon:
                problems.append(f"{kind} needs a saved law per target day")
            for law, base, reference in zip(laws, completed, other, strict=False):
                p = study2.occurrence_probability(law)
                if law.get("kind") != "hurdle":
                    problems.append(f"{kind} is not a hurdle law")
                    break
                if kind == "hurdle_dynamic":
                    expected = (
                        dict(kind="positive", base=base)
                        if study2.occurrence_probability(base) > 0
                        else dict(kind="point", value=1)
                    )
                    if not _close(p, study2.occurrence_probability(reference)):
                        problems.append("hurdle_dynamic's P(Y > 0) differs from dynamic_count's")
                    if law["positive"] != expected:
                        problems.append("hurdle_dynamic's positive law is not the completed law's")
                else:
                    if not _close(p, study2.occurrence_probability(base)):
                        problems.append(
                            "occurrence_model_size_count's P(Y > 0) differs from the completed's"
                        )
                    if law["positive"] != reference.get("positive"):
                        problems.append(
                            "occurrence_model_size_count's positive law is not hurdle_count_28's"
                        )
            if problems:
                window = (row["series_id"], cutoff, horizon, name)
                failures[window] = sorted(set(problems))
    return failures, checked


def registered_series(metadata, root):
    """The run's one domain and the series of its frozen manifest."""
    readiness = metadata.get("readiness", {})
    domain, panels = readiness.get("domain"), readiness.get("panels", {})
    if domain not in (STUDY3_DOMAIN, STUDY3_FALLBACK_DOMAIN) or set(panels) != {domain}:
        raise ValueError("A Study 3 run takes one domain panel")
    entry = panels[domain]["manifest"]
    path = root / entry["path"]
    if file_hash(path) != entry["sha256"]:
        raise ValueError("The run's manifest changed")
    series = [row["series_id"] for row in read_json(path)["series"]]
    if not series or len(series) != len(set(series)):
        raise ValueError("The registered series must be nonempty and unique")
    return domain, sorted(series)


def check_run(run, *, out=None, root=ROOT_DIR, command=None):
    run, root = Path(run), Path(root)
    out = run / "integrity" if out is None else Path(out)
    if out.exists():
        raise FileExistsError("Integrity outputs are immutable; choose a new directory")
    log = []

    def note(message):
        log.append(f"{utc_now().isoformat(timespec='seconds')} {message}")

    note(f"start: component {COMPONENT}, run {study2._relative(run, root)}")
    state = read_json(run / "run.json")
    if state.get("status") != "complete":
        raise ValueError("The integrity check requires a complete run")
    metadata = state["metadata"]
    if resume_identity(metadata) != state["identity"]:
        raise ValueError("Run metadata does not match the run identity")
    if metadata.get("readiness", {}).get("action") != COMPONENT:
        raise ValueError("The run is not a run of this component")
    domain, series = registered_series(metadata, root)
    labels = {json.dumps([domain, key], separators=(",", ":")): key for key in series}
    if set(state["completed"]) != set(labels):
        raise ValueError("The run's checkpoints differ from the registered series")
    models = list(STUDY3_VARIANTS)
    expected = {
        (key, cutoff, horizon, model)
        for key in series
        for cutoff in CUTOFFS
        for horizon in HORIZONS
        for model in models
    }
    note(
        f"run.json: status complete, identity {state['identity']}; registered grid "
        f"{len(series)} series x {len(CUTOFFS)} origins x {len(HORIZONS)} horizons "
        f"x {len(models)} variants = {len(expected)} forecasts"
    )
    records, seen, checkpoints, failures, checked = [], set(), {}, {}, 0
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
            records.append(study2.forecast_record(row))
        found, count = structure(document["rows"])
        failures.update(found)
        checked += count
    missing = sorted(expected - seen)
    if missing:
        raise ValueError(f"The run's grid is incomplete: {len(missing)} forecasts missing")
    note(f"checkpoints: {len(checkpoints)} hashes equal run.json; {len(seen)} forecasts")

    table = pd.DataFrame.from_records(records)
    table, flags = study2.judge(table)
    table["structure"] = [
        "; ".join(failures.get(tuple(w), []))
        for w in table[["series_id", "cutoff", "horizon", "model"]].itertuples(index=False)
    ]
    broken = table.structure.ne("")
    table.loc[broken, "reasons"] = [
        "; ".join(filter(None, (r, s)))
        for r, s in zip(table.loc[broken, "reasons"], table.loc[broken, "structure"], strict=True)
    ]
    table.loc[broken, "passed"] = False
    table = table.sort_values(study2.WINDOW, kind="stable").reset_index(drop=True)
    for name in study2.DAY_COUNTS:
        table[f"{name}_recomputed"] = table[f"{name}_recomputed"].astype("Int64")
    checks = {}
    for name in study2.SCORES:
        mine, residual = table[f"{name}_recomputed"], table[f"{name}_residual"]
        compared = table[f"{name}_saved"].notna() | mine.notna()
        allowed = study2.ATOL + study2.RTOL * mine.abs()
        checks[name] = dict(
            compared=int(compared.sum()),
            disagreements=int(flags[f"{name} differs from the saved value"].sum()),
            max_abs_residual=study2._largest(residual),
            max_residual_over_tolerance=study2._largest(residual / allowed),
        )
        note(
            f"{name}: {checks[name]['compared']} compared, {checks[name]['disagreements']} disagree"
        )
    checks.update(
        identity=dict(
            recomputed_failures=int(flags["the recomputed parts do not sum to QScore9"].sum()),
            saved_failures=int(flags["the saved parts do not sum to the saved QScore9"].sum()),
        ),
        invalid_arrays=int(flags["saved target or deciles are not valid scoring arrays"].sum()),
        not_recomputed=int(flags["the score could not be recomputed"].sum()),
        new_variant_structure=dict(windows_checked=checked, failures=int(broken.sum())),
    )
    note(f"new-variant structure: {checked} windows checked, {int(broken.sum())} fail")
    availability = study2.crps_availability(table)
    failed = table[~table.passed]
    status = "pass" if failed.empty else "fail"
    note(f"result: {status} ({len(failed)} of {len(table)} forecasts failed)")
    out.mkdir(parents=True)
    table[COLUMNS].to_csv(out / "integrity.csv", index=False, lineterminator="\n")
    (out / "integrity.log").write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    versions = installed_versions()
    summary = dict(
        analysis="study3_score_integrity",
        component=COMPONENT,
        domain=domain,
        status=status,
        written_at=utc_now().isoformat(),
        command=command,
        regeneration=(
            r".\.venv\Scripts\python.exe scripts\study3_integrity.py "
            + f"--run {Path(study2._relative(run, root))} --out <new directory>"
        ),
        integrity_script_sha256=file_hash(Path(__file__)),
        study2_functions_sha256=file_hash(Path(study2.__file__)),
        implementation_commit_at_check=study2._git("rev-parse", "HEAD"),
        packages={name: versions.get(name) for name in ("numpy", "scipy", "pandas")},
        run=dict(
            directory=study2._relative(run, root),
            run_json_sha256=file_hash(run / "run.json"),
            identity=state["identity"],
            implementation_commit=metadata.get("metadata", {}).get("implementation_commit"),
            readiness_sha256=metadata.get("readiness_sha256"),
            checkpoints=len(checkpoints),
            checkpoint_sha256=checkpoints,
        ),
        grid=dict(
            series=len(series),
            origins=list(CUTOFFS),
            horizons=list(HORIZONS),
            models=models,
            registered_forecasts=len(expected),
            forecasts=len(table),
            with_count_law=int(table.has_law.sum()),
            without_count_law=int((~table.has_law).sum()),
        ),
        tolerance=dict(rtol=study2.RTOL, atol=study2.ATOL, day_counts="equal"),
        definitions=dict(study2.DEFINITIONS, new_variant_structure=STRUCTURE),
        checks=checks,
        crps_availability=availability,
        failed_forecasts=len(failed),
        failures=failed[[*study2.WINDOW, "reasons"]]
        .head(study2.FAILURES_LISTED)
        .to_dict("records"),
        outputs={name: file_hash(out / name) for name in ("integrity.csv", "integrity.log")},
    )
    study2._write_json(out / "integrity.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="a new directory; default <run>/integrity")
    args = parser.parse_args()
    try:
        summary = check_run(args.run, out=args.out, command=[sys.executable, *sys.argv])
    except (ValueError, FileExistsError) as error:
        print(f"Study 3 integrity check refused: {error}", file=sys.stderr)
        return 2
    print(
        f"Study 3 integrity: {summary['status']}; "
        f"{summary['failed_forecasts']} of {summary['grid']['forecasts']} forecasts failed"
    )
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

r"""POST-HOC: the npm family E01 to E18 without three source zero days, from the saved forecasts.

Usage, from the repository root:
    .\.venv\Scripts\python.exe reports\study2-npm\run-2026-10-15\posthoc\sensitivity_zero_days.py
        reports\study2-npm\run-2026-10-15

Written on 2026-10-16, after the registered scores were seen. It is outside the registered
analysis and never replaces it: the confirmatory result for E01 to E18 is ../inference/, which
this command reads and does not change. Nothing is refitted and no model is loaded.

The days: on 2026-07-12 and 2026-08-14 the download API reports 0 for every panel series, and on
2026-06-25 it reports 0 for the largest series, aggregate-error (../target-pull/daily_summary.csv).
Two scenarios remove days from every target block that holds them, for every series:
three_days removes all three; two_panel_wide_days removes 2026-07-12 and 2026-08-14 only. Each
day lies in one horizon-30 block (from 2026-06-03, 2026-07-03 and 2026-08-02 in turn) and in no
horizon-7 block, so the horizon-7 scores are the saved ones.

- Refused before anything is written, as in scripts/study2_inference.py and
  scripts/study2_integrity.py: a run that is not complete, whose metadata does not give its
  identity, that is not authorized for the committed packages family and specification, whose
  checkpoints are not exactly the manifest's series, whose checkpoint bytes differ from run.json,
  or whose rows are not the registered grid; an inference script whose SHA-256 differs from the
  one ../inference/provenance.json records; any existing output file.
- Day labels: target position i of the block from cutoff c is the UTC day c + i. Checked here:
  the per-day totals and zero counts of the horizon-30 targets equal daily_summary.csv on all 90
  target days, and every removed day reads 0 where the note says it does.
- Re-scoring: every saved forecast is first re-scored on its full block with the run's scorer
  (pulsegraph.study2.scores.accounting) and must equal the saved QScore9 to the integrity check's
  tolerance. A block holding a removed day is then re-scored on its remaining days: QScore9, the
  registered formula, averaged over the remaining days and the nine deciles.
- Inference: the registered functions of scripts/study2_inference.py, imported unchanged
  (series_scores, entity_scores, confirmatory): origins averaged within series and horizon, the
  209 series weighed equally, model minus reference, the two-sided approximate Wilcoxon over the
  series omitting zero differences, the 20,000-replicate series bootstrap with the same derived
  seeds, BH once over the eighteen at q = 0.05. Run first on the saved scores, it must reproduce
  ../inference/inference.csv and ../inference/paired_entities.csv byte for byte.
- Direction: the side with the larger signed-rank sum (average ranks of the absolute nonzero
  differences), as in ../check_directions.py.

Writes, beside the script unless --out names another directory: sensitivity_inference.csv (the
eighteen rows of each scenario in inference.csv's columns, with the rank sums and the registered
row's values and the changes), sensitivity_paired_entities.csv, sensitivity.json (the checks,
hashes and settings). Prints the Markdown tables of README.md.
"""

import argparse
import io
import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.evaluation.registration import installed_versions
from pulsegraph.provenance import read_json, sha256_bytes
from pulsegraph.study2.declarations import validate
from pulsegraph.study2.holdout import utc_now
from pulsegraph.study2.runner import resume_identity
from pulsegraph.study2.scores import accounting

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
import scripts.study2_inference as inference  # noqa: E402

COMPONENT = "external_packages"
DOMAIN = "packages"
HORIZONS = (7, 30)
SCENARIOS = {
    "three_days": ("2026-06-25", "2026-07-12", "2026-08-14"),
    "two_panel_wide_days": ("2026-07-12", "2026-08-14"),
}
PANEL_WIDE = ("2026-07-12", "2026-08-14")
LARGEST = "aggregate-error"
RTOL, ATOL = 1e-10, 1e-12
OUTPUTS = ("sensitivity_inference.csv", "sensitivity_paired_entities.csv", "sensitivity.json")


def block_days(cutoff, horizon):
    """The UTC day labels of a target block: cutoff, cutoff + 1, ..., cutoff + horizon - 1."""
    start = date.fromisoformat(cutoff)
    return [(start + timedelta(days=i)).isoformat() for i in range(horizon)]


def qscore9(target, deciles):
    """QScore9 by the run's scorer: the mean over days and deciles of 2 x pinball."""
    return accounting(target, deciles)["qscore9"]


def rescore(target, deciles, keep):
    """QScore9 over the kept days alone; keep is a boolean mask over the block's days."""
    keep = np.asarray(keep, dtype=bool)
    if not keep.any():
        raise ValueError("A block cannot lose every day")
    return qscore9(np.asarray(target, float)[keep], np.asarray(deciles, float)[keep])


def read_windows(run, root=ROOT_DIR):
    """Verify the run as the inference command does and return its saved windows with arrays."""
    run, root = Path(run), Path(root)
    family = read_json(root / f"study/study2/{COMPONENT}_comparisons.json")
    spec = read_json(root / f"study/study2/{COMPONENT}_spec.json")
    if validate(spec, family) != COMPONENT or family["component"] != COMPONENT:
        raise ValueError("The comparison file is not the packages component's registered family")
    state = read_json(run / "run.json")
    if state.get("status") != "complete":
        raise ValueError("The sensitivity requires a complete run")
    metadata = state["metadata"]
    if resume_identity(metadata) != state["identity"]:
        raise ValueError("Run metadata does not match the run identity")
    if (
        metadata.get("readiness", {}).get("action") != COMPONENT
        or metadata.get("family") != family
        or metadata.get("spec") != spec
    ):
        raise ValueError("The run was not authorized for the registered packages family")
    labels = inference.expected_series(COMPONENT, metadata, root)
    keys = {json.dumps([DOMAIN, key], separators=(",", ":")): key for key in labels}
    if set(state["completed"]) != set(keys):
        raise ValueError("The run's checkpoints differ from the registered series")
    expected = {
        (key, cutoff, horizon, model)
        for key in labels
        for cutoff in inference.ORIGINS[COMPONENT]
        for horizon in HORIZONS
        for model in inference.VARIANTS
    }
    windows, seen = [], set()
    for label in sorted(keys):
        path = run / (sha256_bytes(label.encode()) + ".json")
        if not path.is_file() or file_hash(path) != state["completed"][label]:
            raise ValueError(f"Checkpoint hash mismatch: {label}")
        document = read_json(path)
        if document.get("identity") != state["identity"]:
            raise ValueError("Checkpoint belongs to a different run")
        for row in document["rows"]:
            window = (row["series_id"], row["cutoff"], int(row["horizon"]), row["model"])
            if (
                row["domain"] != DOMAIN
                or row["series_id"] != keys[label]
                or window not in expected
                or window in seen
                or len(row["target"]) != row["horizon"]
            ):
                raise ValueError(f"Checkpoint row outside the registered grid: {window}")
            seen.add(window)
            windows.append(
                dict(
                    series_id=window[0],
                    cutoff=window[1],
                    horizon=window[2],
                    model=window[3],
                    stratum=labels[window[0]].get("stratum"),
                    target=np.asarray(row["target"], dtype=float),
                    deciles=np.asarray(row["forecast"]["deciles"], dtype=float),
                    saved=float(row["scores"]["qscore9"]),
                )
            )
    if seen != expected:
        raise ValueError("The run's grid is incomplete")
    return state, family, windows


def check_saved_scores(windows):
    """Re-score every full block; the saved QScore9 must agree to the integrity tolerance."""
    residuals = np.array([qscore9(w["target"], w["deciles"]) - w["saved"] for w in windows])
    allowed = ATOL + RTOL * np.abs([w["saved"] for w in windows])
    if (np.abs(residuals) > allowed).any():
        raise ValueError("A saved QScore9 differs from its re-scored full block")
    return dict(forecasts=len(windows), max_abs_residual=float(np.abs(residuals).max()))


def check_day_labels(windows, summary_path, removed_days, largest=LARGEST):
    """The horizon-30 targets rebuild daily_summary.csv; every removed day reads 0 as noted."""
    for w in windows:
        held = set(block_days(w["cutoff"], w["horizon"])) & set(removed_days)
        if w["horizon"] == 7 and held:
            raise ValueError("A removed day lies in a horizon-7 block")
        if w["horizon"] == 30 and len(held) > 1:
            raise ValueError("A horizon-30 block holds more than one removed day")
    totals, zeros, counts = {}, {}, {}
    for w in windows:
        # The three horizon-30 blocks of one variant cover the 90 target days once each.
        if w["horizon"] != 30 or w["model"] != inference.VARIANTS[0]:
            continue
        for day, y in zip(block_days(w["cutoff"], w["horizon"]), w["target"], strict=True):
            totals[day] = totals.get(day, 0) + int(y)
            zeros[day] = zeros.get(day, 0) + int(y == 0)
            if w["series_id"] == largest:
                counts[day] = int(y)
    days = sorted(totals)
    if len(days) != 90 or sorted(counts) != days:
        raise ValueError("The horizon-30 blocks do not cover the 90 target days of every series")
    rebuilt = pd.DataFrame(
        dict(
            total_downloads=[totals[d] for d in days],
            series_zero=[zeros[d] for d in days],
            largest_series_count=[counts[d] for d in days],
        ),
        index=pd.Index(days, name="date"),
    )
    summary = pd.read_csv(summary_path, dtype={"date": str}).set_index("date")
    if not rebuilt.equals(summary.reindex(days)[list(rebuilt.columns)].astype("int64")):
        raise ValueError("The saved targets do not rebuild daily_summary.csv on the target days")
    # Every series reads 0 on the panel-wide days; the largest series reads 0 on every removed day.
    series = len({w["series_id"] for w in windows})
    for day in removed_days:
        if counts[day] != 0 or (day in PANEL_WIDE and zeros[day] != series):
            raise ValueError(f"{day} does not read zero where the note says it does")
    return dict(
        target_days_rebuilt=len(days),
        daily_summary_sha256=file_hash(Path(summary_path)),
        removed_days={
            day: dict(
                series_zero=zeros[day],
                total_downloads=totals[day],
                largest_series_count=counts[day],
                blocks=[
                    f"{c}+{h}"
                    for c in inference.ORIGINS[COMPONENT]
                    for h in HORIZONS
                    if day in block_days(c, h)
                ],
            )
            for day in removed_days
        },
    )


def scenario_frame(windows, removed):
    """One row per window: the saved QScore9, or the re-scored one where a removed day lies."""
    removed, rows = set(removed), []
    for w in windows:
        keep = np.array([d not in removed for d in block_days(w["cutoff"], w["horizon"])])
        rows.append(
            dict(
                series_id=w["series_id"],
                cutoff=w["cutoff"],
                horizon=w["horizon"],
                model=w["model"],
                stratum=w["stratum"],
                days_removed=int((~keep).sum()),
                qscore9=w["saved"] if keep.all() else rescore(w["target"], w["deciles"], keep),
            )
        )
    return pd.DataFrame(rows)


def rank_sums(diff):
    diff = np.asarray(diff, dtype=float)
    nonzero = diff[diff != 0]
    ranks = stats.rankdata(np.abs(nonzero))
    below, above = float(ranks[nonzero < 0].sum()), float(ranks[nonzero > 0].sum())
    side = "model" if below > above else "reference" if above > below else "neither"
    return dict(rank_sum_model_lower=below, rank_sum_reference_lower=above, larger_sum_favors=side)


def family_table(frame, family):
    """The registered aggregation and family, through the inference command's own functions."""
    series = inference.series_scores(frame, [inference.METRIC])
    entities = inference.entity_scores(COMPONENT, series, [inference.METRIC])
    table, pairs = inference.confirmatory(COMPONENT, family, entities)
    directions = pd.DataFrame(
        [rank_sums(pairs.loc[pairs.id.eq(cid), "difference"]) for cid in table.id]
    )
    return table, pairs, directions


def csv_text(table):
    """A table as the inference command writes it."""
    buffer = io.StringIO()
    inference._integers(table.copy()).to_csv(buffer, index=False, lineterminator="\n")
    return buffer.getvalue()


def changes(table, registered):
    """The scenario row against the registered row: mean sign, larger rank sum, rejection."""
    merged = table.merge(registered, on="id", suffixes=("", "_registered"), validate="one_to_one")
    return pd.DataFrame(
        dict(
            id=merged.id,
            registered_mean_diff=merged.mean_diff_registered,
            registered_median_diff=merged.median_diff_registered,
            registered_wilcoxon_p=merged.wilcoxon_p_registered,
            registered_wilcoxon_p_bh=merged.wilcoxon_p_bh_registered,
            registered_reject_bh_005=merged.reject_bh_005_registered,
            registered_larger_sum_favors=merged.larger_sum_favors_registered,
            mean_sign_changes=np.sign(merged.mean_diff) != np.sign(merged.mean_diff_registered),
            larger_sum_changes=merged.larger_sum_favors != merged.larger_sum_favors_registered,
            rejection_changes=merged.reject_bh_005 != merged.reject_bh_005_registered,
        )
    )


def run_sensitivity(run, *, root=ROOT_DIR, scenarios=SCENARIOS, registered_dir=None):
    """Reproduce the registered family from the saved scores, then rerun it for each scenario.

    Returns the reproduction check, the stacked scenario tables and their paired entities.
    """
    run = Path(run)
    registered_dir = run / "inference" if registered_dir is None else Path(registered_dir)
    _, family, windows = read_windows(run, root)
    table, pairs, directions = family_table(scenario_frame(windows, ()), family)
    reproduced = {
        name: csv_text(item).encode("utf-8") == (registered_dir / name).read_bytes()
        for name, item in (("inference.csv", table), ("paired_entities.csv", pairs))
    }
    registered = pd.concat([table, directions], axis=1)
    tables, paired = [], []
    for name, removed in scenarios.items():
        frame = scenario_frame(windows, removed)
        table, pairs, directions = family_table(frame, family)
        table = pd.concat([table, directions], axis=1)
        table = table.merge(changes(table, registered), on="id", validate="one_to_one")
        for item in (table, pairs):
            item.insert(0, "removed_days", " ".join(removed))
            item.insert(0, "scenario", name)
        table["forecasts_rescored"] = int((frame.days_removed > 0).sum())
        tables.append(table)
        paired.append(pairs)
    return windows, reproduced, pd.concat(tables, ignore_index=True), pd.concat(paired)


def g(x, d=4):
    return "" if pd.isna(x) else f"{x:,.0f}" if abs(x) >= 10000 else f"{x:.{d}g}"


def p(x):
    return "" if pd.isna(x) else f"{x:.3g}"


def change_text(row):
    found = []
    if row.rejection_changes:
        found.append(f"rejection {_yes(row.registered_reject_bh_005)} to {_yes(row.reject_bh_005)}")
    if row.larger_sum_changes:
        found.append(f"rank sum {row.registered_larger_sum_favors} to {row.larger_sum_favors}")
    if row.mean_sign_changes:
        found.append("mean difference changes sign")
    return "; ".join(found) or "none"


def _yes(value):
    return "yes" if value else "no"


def markdown(table):
    lines = [
        "| ID | Model variant | Reference | h | Mean difference (registered) | 95% interval "
        "| Median difference | Lower / tied / higher | Raw p | BH p (registered) | BH rejects "
        "| Larger rank sum favors | Change from the registered row |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in table.itertuples():
        lines.append(
            f"| {r.id} | `{r.model}` | `{r.reference}` | {r.horizon} | {g(r.mean_diff)} "
            f"({g(r.registered_mean_diff)}) | [{g(r.mean_diff_ci_low)}, {g(r.mean_diff_ci_high)}] "
            f"| {g(r.median_diff)} | {r.wins} / {r.ties} / {r.losses} | {p(r.wilcoxon_p)} "
            f"| {p(r.wilcoxon_p_bh)} ({p(r.registered_wilcoxon_p_bh)}) | {_yes(r.reject_bh_005)} "
            f"| {r.larger_sum_favors} | {change_text(r)} |"
        )
    return "\n".join(lines)


def compact(table):
    """The registered row beside both scenarios: mean difference / BH p / BH rejects."""
    names = list(SCENARIOS)
    lines = [
        "| ID | Model variant | Reference | h | Registered | Without the three days "
        "| Without the two panel-wide days | Larger rank sum favors |",
        "|---|---|---|---|---|---|---|---|",
    ]
    rows = {name: table[table.scenario.eq(name)].set_index("id") for name in names}
    for cid, r in rows[names[0]].iterrows():
        cells = [
            f"{g(r.registered_mean_diff)} / {p(r.registered_wilcoxon_p_bh)} / "
            f"{_yes(r.registered_reject_bh_005)}"
        ]
        for name in names:
            s = rows[name].loc[cid]
            cells.append(f"{g(s.mean_diff)} / {p(s.wilcoxon_p_bh)} / {_yes(s.reject_bh_005)}")
        sides = {
            r.registered_larger_sum_favors,
            *(rows[n].loc[cid].larger_sum_favors for n in names),
        }
        lines.append(
            f"| {cid} | `{r.model}` | `{r.reference}` | {r.horizon} | {' | '.join(cells)} "
            f"| {' / '.join(sorted(sides))} |"
        )
    return "\n".join(lines)


def _git(*args):
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT_DIR, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    started = utc_now()
    out, run = args.out, args.run
    for name in OUTPUTS:
        if (out / name).exists():
            raise SystemExit("refusing to overwrite " + str(out / name))
    recorded = read_json(run / "inference" / "provenance.json")["inference_script_sha256"]
    if file_hash(Path(inference.__file__)) != recorded:
        raise SystemExit("scripts/study2_inference.py differs from the one the inference used")
    windows, reproduced, table, paired = run_sensitivity(run)
    if not all(reproduced.values()):
        raise SystemExit(f"the saved scores do not reproduce the registered family: {reproduced}")
    saved = check_saved_scores(windows)
    summary_path = run / "target-pull" / "daily_summary.csv"
    labels = check_day_labels(windows, summary_path, SCENARIOS["three_days"], LARGEST)
    out.mkdir(parents=True, exist_ok=True)
    (out / OUTPUTS[0]).write_text(csv_text(table), encoding="utf-8", newline="\n")
    (out / OUTPUTS[1]).write_text(csv_text(paired), encoding="utf-8", newline="\n")
    versions = installed_versions()
    summary = dict(
        analysis="study2_npm_zero_days_sensitivity",
        status="post-hoc; computed after the registered scores were seen; never replaces "
        "inference/, the confirmatory result",
        started_at=started.isoformat(),
        written_at=utc_now().isoformat(),
        command=[sys.executable, *sys.argv],
        script_sha256=file_hash(Path(__file__)),
        inference_script_sha256=file_hash(Path(inference.__file__)),
        head=_git("rev-parse", "HEAD"),
        uncommitted_changes=_git(
            "status", "--porcelain", "--", "scripts/study2_inference.py", "pulsegraph"
        ),
        packages={name: versions.get(name) for name in ("numpy", "scipy", "pandas")},
        run=dict(
            run_json_sha256=file_hash(run / "run.json"),
            identity=read_json(run / "run.json")["identity"],
            checkpoints_verified=len({w["series_id"] for w in windows}),
            forecasts=len(windows),
        ),
        scenarios={name: list(days) for name, days in SCENARIOS.items()},
        removal="each listed day is dropped from every target block that holds it, for every "
        "series and variant; the block's QScore9 is the mean over its remaining days and the nine "
        "deciles; windows are then averaged within series and horizon as registered",
        checks=dict(
            registered_family_reproduced_byte_for_byte=reproduced,
            saved_qscore9_rescored=saved,
            day_labels=labels,
        ),
        inference=dict(
            functions="scripts/study2_inference.py: series_scores, entity_scores, confirmatory",
            bootstrap_seeds="the registered derived seeds, one per comparison id",
            adjustment="Benjamini-Hochberg once over the eighteen of each scenario at q = 0.05",
            direction="the side with the larger signed-rank sum of the nonzero differences",
        ),
        outputs={name: file_hash(out / name) for name in OUTPUTS[:2]},
    )
    inference._write_json(out / OUTPUTS[2], summary)
    print("### Mean difference / BH p / BH rejects at 0.05\n")
    print(compact(table))
    print()
    for name in SCENARIOS:
        print(f"### {name}: {' '.join(SCENARIOS[name])} removed\n")
        print(markdown(table[table.scenario.eq(name)]))
        print()
    for name in OUTPUTS:
        print(name, file_hash(out / name))


if __name__ == "__main__":
    main()

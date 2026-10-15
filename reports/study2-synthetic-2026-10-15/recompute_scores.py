r"""Integrity check of the synthetic run: recompute each saved QScore9 from its forecast and target.

Usage, from the repository root:
    .\.venv\Scripts\python.exe reports\study2-synthetic-2026-10-15\recompute_scores.py
        reports\study2-synthetic-2026-10-15 --out <new file>

For each of the 540 checkpoints, at the hash recorded in run.json, and each saved window, the
pinball loss over the nine deciles is written out here rather than taken from
pulsegraph.study2.scores: QScore9, its three accounting parts (zero days, positive days over and
under, each divided by the horizon) and the context-scaled QScore9 are recomputed from the saved
deciles and target, and each saved target and context mean is compared with the registered
generator's series (pulsegraph.study2.synthetic.grid_dataset). The largest absolute differences
are written as JSON. Nothing in the run directory is changed.
"""

import argparse
import json
from pathlib import Path

import numpy as np

from pulsegraph.provenance import sha256_bytes
from pulsegraph.study2.synthetic import grid_dataset

TAUS = np.arange(1, 10) / 10


def recompute(run):
    state = json.loads((run / "run.json").read_text(encoding="utf-8"))
    if state["status"] != "complete":
        raise ValueError("The run is not complete")
    dataset = grid_dataset()
    labels = {json.dumps(list(key), separators=(",", ":")): key for key in dataset}
    if set(labels) != set(state["completed"]):
        raise ValueError("The run's checkpoints differ from the registered grid")
    worst = dict(qscore9=0.0, parts=0.0, context_scaled_qscore9=0.0, target=0.0, context_mean=0.0)
    windows = 0
    for label in sorted(labels):
        path = run / (sha256_bytes(label.encode()) + ".json")
        if sha256_bytes(path.read_bytes()) != state["completed"][label]:
            raise ValueError(f"Checkpoint hash mismatch: {label}")
        values = dataset[labels[label]].to_numpy()
        for row in json.loads(path.read_text(encoding="utf-8"))["rows"]:
            cutoff, horizon = int(row["cutoff"]), int(row["horizon"])
            y = np.asarray(row["target"], dtype=float)
            q = np.asarray(row["forecast"]["deciles"], dtype=float)
            if y.shape != (horizon,) or q.shape != (horizon, 9):
                raise ValueError(f"Window shape differs: {label} {cutoff} {horizon}")
            worst["target"] = max(
                worst["target"], float(np.abs(y - values[cutoff : cutoff + horizon]).max())
            )
            context_mean = float(values[:cutoff].mean())
            worst["context_mean"] = max(
                worst["context_mean"], abs(row["context_mean"] - context_mean)
            )
            error = y[:, None] - q
            loss = 2 * np.where(error >= 0, TAUS * error, (TAUS - 1) * error)
            qscore9 = float(loss.mean())
            zero = (y == 0)[:, None]
            parts = dict(
                zero=float(np.where(zero, loss, 0).mean()),
                positive_over=float(np.where(~zero & (error < 0), loss, 0).mean()),
                positive_under=float(np.where(~zero & (error >= 0), loss, 0).mean()),
            )
            saved = row["scores"]
            worst["qscore9"] = max(worst["qscore9"], abs(saved["qscore9"] - qscore9))
            worst["parts"] = max(
                worst["parts"],
                *(abs(saved["contributions"][name] - value) for name, value in parts.items()),
            )
            worst["context_scaled_qscore9"] = max(
                worst["context_scaled_qscore9"],
                abs(saved["context_scaled_qscore9"] - qscore9 / max(1.0, context_mean)),
            )
            windows += 1
    return dict(
        check="QScore9, its three parts and the context-scaled QScore9 recomputed from each saved "
        "forecast's deciles and target; saved targets and context means compared with the "
        "registered generator",
        run_json_sha256=sha256_bytes((run / "run.json").read_bytes()),
        series=len(labels),
        windows=windows,
        max_abs_difference=worst,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("Choose a new output file")
    result = recompute(args.run)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(result["max_abs_difference"]), result["windows"])


if __name__ == "__main__":
    main()

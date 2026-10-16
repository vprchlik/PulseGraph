r"""Per-day panel summary of the npm signals, and the days on which the source reads zero.

Usage, from the repository root:
    .\.venv\Scripts\python.exe reports\study2-npm\run-2026-10-15\target_days.py
        data\raw\study2\npm\targets\signals.parquet reports\study2-npm\panel\manifest.json
        --out <new file>

A data description, computed after the run and outside the registered family; it reads no score.
For every day from 2025-09-01 to 2026-08-31 it writes the number of series reading zero (all and per
stratum), the panel's total downloads, the largest series' count (aggregate-error, whose scale
dominates the unscaled means) and the registered windows containing the day. It prints the days on
which every series reads zero and the days on which the largest series reads zero.
"""

import argparse
import hashlib
import json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

CUTOFFS = ("2026-06-03", "2026-07-03", "2026-08-02")
HORIZONS = (7, 30)
LARGEST = "aggregate-error"

parser = argparse.ArgumentParser()
parser.add_argument("signals", type=Path)
parser.add_argument("manifest", type=Path)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()
if args.out.exists():
    raise SystemExit("refusing to overwrite " + str(args.out))
signals = pd.read_parquet(args.signals)
manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
strata = {row["series_id"]: row["stratum"] for row in manifest["series"]}
wide = signals.pivot(index="date", columns="series_id", values="count")
if set(wide.columns) != set(strata) or wide.isna().any().any():
    raise SystemExit("signals and manifest differ")
table = pd.DataFrame(index=wide.index)
table["series"] = wide.shape[1]
table["series_zero"] = (wide == 0).sum(axis=1)
for name in ("dense", "sparse", "very_sparse"):
    columns = [key for key, value in strata.items() if value == name]
    table[f"{name}_zero"] = (wide[columns] == 0).sum(axis=1)
table["total_downloads"] = wide.sum(axis=1)
table["largest_series_count"] = wide[LARGEST]
table.index = [day.date() for day in table.index]
table.index.name = "date"


def windows(day):
    found = []
    for cutoff in CUTOFFS:
        for horizon in HORIZONS:
            start = date.fromisoformat(cutoff)
            if start <= day < start + timedelta(days=horizon):
                found.append(f"{cutoff}+{horizon}")
    return " ".join(found)


table["windows"] = [windows(day) for day in table.index]
table.to_csv(args.out, lineterminator="\n")
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)
shown = ["series_zero", "dense_zero", "total_downloads", "largest_series_count", "windows"]
print("Every series reads zero:")
print(table.loc[table.series_zero == table.series, shown])
print(f"{LARGEST} reads zero:")
print(table.loc[table.largest_series_count == 0, shown])
print(args.out, hashlib.sha256(args.out.read_bytes()).hexdigest())

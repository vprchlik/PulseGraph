r"""The daily counts of the npm and NYC 311 panels, every day the studies used, as committed CSVs.

From the repository root, PowerShell:

    .\.venv\Scripts\python.exe reports\release\build_daily_counts.py npm
    .\.venv\Scripts\python.exe reports\release\build_daily_counts.py nyc311

The series are the frozen manifest's. The days run from 2025-09-01 through 2026-08-31: the 275
context days of the frozen selection snapshot (`context.parquet`) and the 90 target days of the
signals the run read (`signals.parquet`, published as a release asset). Before a row is written,
the manifest, the context and the signals are checked against the SHA-256 values the run recorded
in its `run.json`, the signals must hold every manifest series on every day, and their context days
must equal the frozen context, as the run itself required
(`pulsegraph.study2.runner.external_dataset`). With `--no-context` (a fresh clone holding only the
release asset) every day comes from the signals, whose context days the run verified; the CSV is
the same byte for byte.

Rows are sorted by the series columns and then the day; UTF-8, LF line endings, no index. Beside
each CSV the command writes `daily_counts.provenance.json`: the inputs by path and SHA-256, the
output's bytes, rows and SHA-256, the source statement, and this command. It reads no forecast and
no score.
"""

import argparse
import csv
import hashlib
import io
import json
import os
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from pulsegraph.study2.constants import CONTEXT_END, CONTEXT_START, ENDPOINT
from pulsegraph.study2.ingestion import context_days

ROOT = Path(__file__).resolve().parents[2]
TARGET_START = (date.fromisoformat(CONTEXT_END) + timedelta(days=1)).isoformat()

NPM_STATEMENT = (
    "Daily download counts from the npm download-counts API (api.npmjs.org/downloads/range): "
    "the context days 2025-09-01 to 2026-06-02 retrieved 2026-10-14 to 2026-10-15 UTC, the "
    "target days 2026-06-03 to 2026-08-31 retrieved 2026-10-15 UTC. Package names and creation "
    "timestamps are from the npm public registry (registry.npmjs.org, replicate.npmjs.com) as "
    "served at acquisition; a name may since have been removed. A download is a tarball request "
    "as npm counts it, mirrors, build servers and bots included. npm, Inc. states no licence for "
    "the counts, and its Open-Source Terms of 2022-03-10 contain no restriction on their "
    "redistribution. The context pull reached npm's rate limit 2,708 times and honoured it. The "
    "download API reports 0 for every series on 2026-07-12 and 2026-08-14 and for "
    "aggregate-error on 2026-06-25; the counts are as served (PROTOCOL.md, dated addition 6). "
    "CC BY 4.0 applies to the project's compilation (the selection, the derived fields, the "
    "documentation), not to the counts as such. npm is a registered trademark of npm, Inc."
)
NYC311_STATEMENT = (
    "Daily counts of NYC 311 service requests by New York calendar day of created_date, from NYC "
    "Open Data's dataset erm2-nwe9 (311 Service Requests from 2020 to Present), per problem type "
    "and community board of the frozen 2024 frame, counted by one anonymous query per day: the "
    "context days 2025-09-01 to 2026-06-02 on 2026-10-16 UTC, the target days 2026-06-03 to "
    "2026-08-31 on 2026-10-17 UTC. The dataset's metadata states no licence and gives the "
    "attribution 311. The City's website terms of use, read 2026-10-17, say nothing specific "
    "about datasets (reports/study3-nyc311/panel/source-terms.md). Source: NYC Open Data; no "
    "endorsement by the City of New York is claimed. CC BY 4.0 applies to the project's "
    "compilation (the selection, the derived fields, the documentation), not to the counts as "
    "such."
)

PANELS = dict(
    npm=dict(
        run="reports/study2-npm/run-2026-10-15",
        panel="packages",
        out="reports/study2-npm/panel",
        columns=("package", "created_at", "day", "count"),
        names=lambda row: (row["series_id"], row["created_at"]),
        asset="study2-npm-targets-signals.parquet",
        statement=NPM_STATEMENT,
    ),
    nyc311=dict(
        run="reports/study3-nyc311/run-2026-10-17",
        panel="nyc311",
        out="reports/study3-nyc311/panel",
        columns=("problem", "board", "day", "count"),
        names=lambda row: (row["problem"], row["board"]),
        asset="study3-nyc311-targets-signals.parquet",
        statement=NYC311_STATEMENT,
    ),
)


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _checked(path, expected, what):
    if not Path(path).is_file():
        raise SystemExit(f"{what}: {path} is missing")
    actual = sha256_file(path)
    if actual != expected:
        raise SystemExit(f"{what}: {path} has SHA-256 {actual}, the run recorded {expected}")
    return Path(path)


def _write_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def build(domain, *, root=ROOT, context=True, signals=None, out=None):
    """Write `daily_counts.csv` and its provenance for one panel; return the provenance."""
    spec = PANELS[domain]
    root = Path(root)
    state = json.loads((root / spec["run"] / "run.json").read_text(encoding="utf-8"))
    panel = state["metadata"]["readiness"]["panels"][spec["panel"]]
    manifest_path = _checked(
        root / panel["manifest"]["path"], panel["manifest"]["sha256"], "manifest"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["context_sha256"] != panel["context"]["sha256"]:
        raise SystemExit("The manifest and the run name different context snapshots")
    signals_path = root / panel["signals"]["path"] if signals is None else Path(signals)
    signals_frame = pd.read_parquet(_checked(signals_path, panel["signals"]["sha256"], "signals"))
    frozen = None
    if context:
        context_path = _checked(
            root / panel["context"]["path"], panel["context"]["sha256"], "context"
        )
        frozen = pd.read_parquet(context_path)

    series = manifest["series"]
    keys = [row["series_id"] for row in series]
    if not keys or len(keys) != len(set(keys)) or set(signals_frame.series_id) != set(keys):
        raise SystemExit("The signals and the manifest hold different series")
    if frozen is not None and set(frozen.series_id) != set(keys):
        raise SystemExit("The frozen context and the manifest hold different series")

    rows = []
    for row in series:
        key = row["series_id"]
        raw = signals_frame.loc[signals_frame.series_id == key, ["date", "count"]].to_dict(
            "records"
        )
        days = context_days(raw, start=CONTEXT_START, end=ENDPOINT)
        if frozen is not None:
            previous = context_days(
                frozen.loc[frozen.series_id == key, ["date", "count"]].to_dict("records")
            )
            if not context_days(raw).equals(previous):
                raise SystemExit(f"The signals changed the frozen context of {key}")
            days = pd.concat(
                [previous, days.loc[days.date >= pd.Timestamp(TARGET_START)]], ignore_index=True
            )
        names = spec["names"](row)
        for day, count in zip(days.date, days["count"]):
            rows.append((*names, day.strftime("%Y-%m-%d"), int(count)))
    rows.sort()

    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(spec["columns"])
    writer.writerows(rows)
    data = buffer.getvalue().encode("utf-8")

    out = root / spec["out"] if out is None else Path(out)
    csv_path = out / "daily_counts.csv"
    _write_bytes(csv_path, data)
    inputs = dict(
        manifest=dict(path=panel["manifest"]["path"], sha256=panel["manifest"]["sha256"]),
        signals=dict(
            path=panel["signals"]["path"],
            sha256=panel["signals"]["sha256"],
            release_asset=spec["asset"],
        ),
        run_json=dict(
            path=f"{spec['run']}/run.json", sha256=sha256_file(root / spec["run"] / "run.json")
        ),
    )
    if context:
        inputs["context"] = dict(path=panel["context"]["path"], sha256=panel["context"]["sha256"])
    provenance = dict(
        output=dict(
            path=f"{spec['out']}/daily_counts.csv",
            bytes=len(data),
            sha256=hashlib.sha256(data).hexdigest(),
            rows=len(rows),
            series=len(keys),
            first_day=CONTEXT_START,
            last_day=ENDPOINT,
            columns=list(spec["columns"]),
            order="sorted by " + ", ".join(spec["columns"][:-1]),
        ),
        inputs=inputs,
        days=dict(
            context=f"{CONTEXT_START} to {CONTEXT_END}, from the frozen context"
            if context
            else f"{CONTEXT_START} to {CONTEXT_END}, from the signals (verified by the run)",
            target=f"{TARGET_START} to {ENDPOINT}, from the signals",
        ),
        statement=spec["statement"],
        command=rf".\.venv\Scripts\python.exe reports\release\build_daily_counts.py {domain}",
        builder_sha256=sha256_file(Path(__file__)),
    )
    text = json.dumps(provenance, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    _write_bytes(out / "daily_counts.provenance.json", text.encode("utf-8"))
    return provenance


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("domain", choices=sorted(PANELS))
    parser.add_argument("--signals", type=Path, help="the signals file, if not at the run's path")
    parser.add_argument(
        "--no-context",
        action="store_true",
        help="take the context days from the signals (the frozen context is not in the tree)",
    )
    parser.add_argument("--out", type=Path, help="the output directory, if not the panel's")
    args = parser.parse_args(argv)
    provenance = build(args.domain, context=not args.no_context, signals=args.signals, out=args.out)
    output = provenance["output"]
    print(
        f"{output['path']}: {output['rows']:,} rows, {output['series']} series, "
        f"{output['bytes']:,} bytes, SHA-256 {output['sha256']}"
    )


if __name__ == "__main__":
    main()

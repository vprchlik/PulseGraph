"""Post-hoc QScore9 accounting from saved forecasts; no fitting or hypothesis tests."""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json, read_json

BASE = Path(__file__).resolve().parent
LEVELS = np.arange(1, 10) / 10
PARTS = ["zero", "positive_over", "positive_under"]
VALUES = ["qscore9", *PARTS, "positive"]
KEY = ["repo_name", "model_name", "horizon", "cutoff_date"]
BEGIN = "<!-- BEGIN POST-HOC QSCORE9 ACCOUNTING -->"
END = "<!-- END POST-HOC QSCORE9 ACCOUNTING -->"
COLORS = {"20-99": "#0072B2", "100-999": "#D55E00", "1000+": "#009E73"}


def decompose(actuals, quantiles, levels):
    """Post-hoc unconditional contributions; equal-to-target quantiles contribute zero."""
    y = np.asarray(actuals, dtype=float)
    levels = np.asarray(levels, dtype=float)
    q = np.asarray(quantiles, dtype=float)
    if (
        y.ndim != 1
        or not y.size
        or q.shape != (len(y), len(levels))
        or not np.isfinite(y).all()
        or not np.isfinite(q).all()
        or (y < 0).any()
        or (q < 0).any()
        or (y != np.floor(y)).any()
        or (np.diff(levels) <= 0).any()
        or (np.diff(q, axis=1) < 0).any()
        or levels[0] > 0.1
        or levels[-1] < 0.9
    ):
        raise ValueError(
            "Complete integer targets and nonnegative ordered supported quantiles required"
        )
    q = np.array([np.interp(LEVELS, levels, row) for row in q])
    y = y[:, None]
    zero = np.where(y == 0, 2 * (1 - LEVELS) * q, 0)
    over = np.where(y > 0, 2 * (1 - LEVELS) * np.maximum(q - y, 0), 0)
    under = np.where(y > 0, 2 * LEVELS * np.maximum(y - q, 0), 0)
    direct = 2 * np.maximum(LEVELS * (y - q), (LEVELS - 1) * (y - q))
    np.testing.assert_allclose(zero + over + under, direct, rtol=1e-12, atol=1e-12)
    components = {"zero": zero, "positive_over": over, "positive_under": under}
    result = {name: float(array.mean()) for name, array in components.items()}
    result["positive"] = result["positive_over"] + result["positive_under"]
    result["qscore9"] = float(direct.mean())
    n_zero = int((y == 0).sum())
    result.update(
        n_zero_days=n_zero,
        n_positive_days=len(y) - n_zero,
        zero_conditional_mean=float(direct[(y == 0).ravel()].mean()) if n_zero else np.nan,
        positive_conditional_mean=float(direct[(y > 0).ravel()].mean())
        if n_zero < len(y)
        else np.nan,
    )
    deciles = {name: array.mean(axis=0) / 9 for name, array in components.items()}
    deciles["positive"] = deciles["positive_over"] + deciles["positive_under"]
    deciles["qscore9"] = direct.mean(axis=0) / 9
    return result, deciles


def pair_repositories(windows):
    """Post-hoc pairing with Study 1's equal-window then equal-repository weights."""
    groups = ["repo_name", "repo_id", "sampling_stratum", "model_name", "horizon"]
    repo = windows.groupby(groups, as_index=False)[
        VALUES + ["context_mean", "context_zero_fraction"]
    ].mean()
    counts = windows.groupby(groups, as_index=False).size().rename(columns={"size": "n_windows"})
    repo = repo.merge(counts, on=groups, validate="one_to_one")
    paired = []
    for reference in ["local_mean_28", "autoets_weekly"]:
        ref = repo[repo.model_name.eq(reference)].drop(columns="model_name")
        keys = ["repo_name", "repo_id", "sampling_stratum", "horizon"]
        for model in sorted(set(repo.model_name) - {reference}):
            own = repo[repo.model_name.eq(model)]
            match = own.merge(
                ref, on=keys, suffixes=("_model", "_reference"), validate="one_to_one"
            )
            assert len(match) == len(own) == len(ref)
            for col in ["n_windows", "context_mean", "context_zero_fraction"]:
                np.testing.assert_allclose(match[col + "_model"], match[col + "_reference"])
            item = match[keys].copy()
            item["model"], item["reference"] = model, reference
            item["n_windows"] = match.n_windows_model
            for col in ["context_mean", "context_zero_fraction"]:
                item[col] = match[col + "_model"]
            for col in VALUES:
                item[col + "_model"] = match[col + "_model"]
                item[col + "_reference"] = match[col + "_reference"]
                item[col + "_difference"] = match[col + "_model"] - match[col + "_reference"]
            item["analysis_status"] = "post_hoc"
            paired.append(item)
    return pd.concat(paired, ignore_index=True)


def contribution_curves(pairs):
    rows = []
    for _, group in pairs.groupby(["model", "reference", "horizon"], sort=True):
        ordered = group.sort_values(["qscore9_difference", "repo_id"], kind="stable").copy()
        ordered["rank"] = np.arange(1, len(ordered) + 1)
        ordered["repository_fraction"] = ordered["rank"] / len(ordered)
        for name in VALUES:
            ordered["cumulative_" + name + "_difference"] = ordered[
                name + "_difference"
            ].cumsum() / len(ordered)
        ordered["ordering"] = "ascending signed total difference, stable repo_id tie break"
        rows.append(ordered)
    return pd.concat(rows, ignore_index=True)


def save_parquet(frame, path):
    table = pa.Table.from_pandas(frame, preserve_index=False)
    table = table.replace_schema_metadata(
        {
            **(table.schema.metadata or {}),
            b"analysis_status": b"post_hoc",
            b"interpretation": b"Accounting diagnostic, not a confirmatory test",
        }
    )
    pq.write_table(table, path)


def figures(pairs, curves, out):
    paths = []
    plt.rcParams.update({"font.size": 8, "svg.hashsalt": "pulsegraph-posthoc-accounting-v1"})
    for reference in ["local_mean_28", "autoets_weekly"]:
        for horizon in [7, 30, 90]:
            selected = pairs[pairs.reference.eq(reference) & pairs.horizon.eq(horizon)]
            for kind in ["cumulative", "context-mean", "context-zero-fraction"]:
                fig, axes = plt.subplots(5, 4, figsize=(17, 17), constrained_layout=True)
                for ax, (model, group) in zip(axes.flat, selected.groupby("model"), strict=False):
                    if kind == "cumulative":
                        curve = curves[
                            curves.reference.eq(reference)
                            & curves.model.eq(model)
                            & curves.horizon.eq(horizon)
                        ]
                        for field, color, label in [
                            ("qscore9", "#222222", "Total"),
                            ("zero", "#0072B2", "Zero"),
                            ("positive_over", "#D55E00", "Positive over"),
                            ("positive_under", "#009E73", "Positive under"),
                        ]:
                            ax.plot(
                                np.r_[0, curve.repository_fraction],
                                np.r_[0, curve["cumulative_" + field + "_difference"]],
                                color=color,
                                label=label,
                                linewidth=1.25,
                            )
                        ax.set_xlabel("Repository fraction, sorted by signed difference")
                        ax.set_ylabel("Cumulative contribution to mean difference")
                    else:
                        field = (
                            "context_mean" if kind == "context-mean" else "context_zero_fraction"
                        )
                        for stratum, color in COLORS.items():
                            g = group[group.sampling_stratum.eq(stratum)]
                            ax.scatter(
                                g[field],
                                g.qscore9_difference,
                                s=9,
                                alpha=0.6,
                                color=color,
                                label=stratum,
                                edgecolors="none",
                            )
                        if field == "context_mean":
                            ax.set_xscale("symlog", linthresh=0.1)
                        else:
                            ax.set_xlim(-0.02, 1.02)
                        ax.set_xlabel(
                            "Mean context count (symlog)"
                            if field == "context_mean"
                            else "Context zero fraction"
                        )
                        ax.set_yscale("symlog", linthresh=0.01)
                        ax.set_ylabel("Model minus reference QScore9 (symlog)")
                    ax.axhline(0, linewidth=0.6, color="#777777")
                    ax.set_title(model)
                    ax.grid(alpha=0.2)
                for ax in list(axes.flat)[selected.model.nunique() :]:
                    ax.set_visible(False)
                handles, labels = axes.flat[0].get_legend_handles_labels()
                fig.legend(handles, labels, loc="outside lower center", ncol=4)
                fig.suptitle(
                    f"POST-HOC | {kind} | reference {reference} | horizon {horizon} days\n"
                    "All 300 repositories; 3 windows averaged per repository; no tests",
                    fontsize=14,
                )
                for extension in ["png", "svg"]:
                    path = out / f"posthoc-{kind}-{reference}-h{horizon}.{extension}"
                    metadata = {"Title": "Post-hoc QScore9 accounting", "Creator": "PulseGraph"}
                    if extension == "svg":
                        metadata["Date"] = None
                    fig.savefig(path, dpi=130, metadata=metadata)
                    paths.append(path)
                plt.close(fig)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=BASE)
    parser.add_argument("--update-results", action="store_true")
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    study = BASE.parent
    root = study.parents[1]
    results_file = study / "run/results.parquet"
    state = read_json(study / "run/run.json")
    assert file_hash(results_file) == state["artifact_sha256"]["results.parquet"]
    immutable = [
        study / "run/run.json",
        study / "run/manifest.json",
        *sorted((study / "inference").glob("*")),
    ]
    before = {p.relative_to(root).as_posix(): file_hash(p) for p in immutable}
    manifest = pd.DataFrame(read_json(study / "run/manifest.json")).set_index("repo_name")
    source = pd.read_parquet(
        results_file,
        columns=KEY + ["stratum", "context", "actuals", "quantiles", "quantile_levels", "qscore9"],
    )
    assert len(source) == 48600 and not source.duplicated(KEY).any()
    window_records, decile_records = [], []
    for row in source.itertuples(index=False):
        parts, deciles = decompose(row.actuals, np.vstack(row.quantiles), row.quantile_levels)
        np.testing.assert_allclose(parts["qscore9"], row.qscore9, rtol=1e-12, atol=1e-12)
        identity = {name: getattr(row, name) for name in KEY}
        identity.update(
            repo_id=int(manifest.loc[row.repo_name, "repo_id"]),
            sampling_stratum=manifest.loc[row.repo_name, "sampling_stratum"],
            regime=row.stratum,
            analysis_status="post_hoc",
        )
        window_records.append(
            {
                **identity,
                **parts,
                "stored_qscore9": row.qscore9,
                "context_mean": float(np.mean(row.context)),
                "context_zero_fraction": float(np.mean(row.context == 0)),
            }
        )
        for i, level in enumerate(LEVELS):
            decile_records.append(
                {
                    **identity,
                    "quantile_level": level,
                    **{name: values[i] for name, values in deciles.items()},
                }
            )
    windows = pd.DataFrame(window_records)
    deciles = pd.DataFrame(decile_records)
    windows["accounting_residual"] = windows.qscore9 - windows[PARTS].sum(axis=1)
    save_parquet(windows, out / "posthoc-window-accounting.parquet")
    save_parquet(deciles, out / "posthoc-window-deciles.parquet")
    pairs = pair_repositories(windows)
    assert len(pairs) == 30600 and pairs.n_windows.eq(3).all()
    delta_cols = [name + "_difference" for name in VALUES]
    np.testing.assert_allclose(
        pairs.qscore9_difference,
        pairs[[p + "_difference" for p in PARTS]].sum(axis=1),
        rtol=1e-10,
        atol=1e-12,
    )
    paired_path = out / "posthoc-paired-repositories.csv"
    pairs.to_csv(paired_path, index=False)
    summaries = pairs.groupby(["model", "reference", "horizon"], as_index=False)[delta_cols].mean()
    summaries["n_repositories"] = 300
    summaries["n_windows_per_repository"] = 3
    summaries["analysis_status"] = "post_hoc"
    summaries.to_csv(out / "posthoc-paired-summary.csv", index=False)
    registered = pd.read_csv(study / "inference/inference.csv")
    check = registered.merge(summaries, on=["model", "reference", "horizon"], validate="one_to_one")
    assert len(check) == 18
    np.testing.assert_allclose(check.mean_diff, check.qscore9_difference, rtol=1e-11, atol=1e-12)
    decile_pairs = []
    for level, group in deciles.groupby("quantile_level"):
        expanded = group.merge(
            windows[KEY + ["context_mean", "context_zero_fraction"]], on=KEY, validate="many_to_one"
        )
        dp = pair_repositories(expanded)
        dm = dp.groupby(["model", "reference", "horizon"], as_index=False)[delta_cols].mean()
        dm["quantile_level"], dm["analysis_status"] = level, "post_hoc"
        decile_pairs.append(dm)
    decile_summary = pd.concat(decile_pairs, ignore_index=True)
    decile_summary.to_csv(out / "posthoc-paired-deciles.csv", index=False)
    np.testing.assert_allclose(
        decile_summary.groupby(["model", "reference", "horizon"])[delta_cols].sum(),
        summaries.set_index(["model", "reference", "horizon"])[delta_cols],
        rtol=1e-10,
        atol=1e-12,
    )
    curves = contribution_curves(pairs)
    curves.to_csv(out / "posthoc-contribution-curves.csv", index=False)
    plots = figures(pairs, curves, out)
    section = (
        f"{BEGIN}\n## Post-hoc QScore9 accounting (2026-09-14)\n\n"
        "This post-hoc diagnostic partitions each saved QScore9 into zero-day, positive-day "
        "overprediction and positive-day underprediction contributions, each divided by the "
        "full horizon. All 48,600 rows satisfy the accounting identity to floating-point "
        "tolerance; the 18 original mean differences are reproduced "
        "without changing their tests.\n\n"
        "Windows are averaged within repository, then repositories receive equal weight. "
        "Empty conditional partitions remain undefined; "
        "their unconditional contributions are zero. "
        "Outcome-sorted cumulative curves and context scatters are post-hoc descriptions.\n\n"
        "[Post-hoc paired tables]"
        "(reports/registered-2026-09-13/posthoc/posthoc-paired-summary.csv), "
        "[post-hoc figure index and regeneration]"
        "(reports/registered-2026-09-13/posthoc/posthoc-report.md), "
        "[post-hoc provenance](reports/registered-2026-09-13/posthoc/provenance.json).\n"
        f"{END}\n"
    )
    (out / "posthoc-results-section.md").write_text(section, encoding="utf-8")
    if args.update_results:
        path = root / "RESULTS.md"
        text = path.read_text(encoding="utf-8")
        if BEGIN in text:
            start, stop = text.index(BEGIN), text.index(END) + len(END)
            text = text[:start] + section.rstrip() + text[stop:]
        else:
            text = text.rstrip() + "\n\n" + section
        path.write_text(text, encoding="utf-8")
    command = (
        ".\\.venv\\Scripts\\python.exe "
        "reports/registered-2026-09-13/posthoc/accounting.py --update-results"
    )
    report = [
        "# Post-hoc QScore9 accounting",
        "",
        "Analysis status: post-hoc; no confirmatory tests.",
        "",
        "For each decile, zero=(2/9H) sum[y=0](1-tau)q; "
        "positive_over=(2/9H) sum[y>0](1-tau)max(q-y,0); "
        "positive_under=(2/9H) sum[y>0]tau max(y-q,0). Summing the three parts and nine "
        "deciles recovers QScore9. Ties have zero loss. No tails are inferred.",
        "",
        "All 18 models and 48,600 saved windows are included. Each of 17 non-self "
        "models is paired against each reference at 7/30/90 days: 102 descriptive cells. "
        "All parts use the full horizon denominator; conditional means are not substituted.",
        "",
        "Context covariates use each saved full context, then the same three-window "
        "repository average as paired scores. Scatter colors show frozen sampling strata; "
        "window tables retain context regimes. Signed curves order repositories by total "
        "model-minus-reference difference ascending, breaking ties by stable ID. "
        "Cumulative sums are divided by 300, so the final point is the mean difference, "
        "not a share of positive gains. No repository is removed. Symlog axes retain zeros "
        "and signed values; curve y-axes are linear and panel scales differ.",
        "",
        "Source: research extensions memo of 2026-09-13, sections 3 and 5, not in the tree.",
        "",
        "Regenerate these post-hoc outputs after the declared descriptive document:",
        "",
        "```powershell",
        command,
        "```",
        "",
        "For a separate reproduction directory, omit --update-results and supply "
        "--out data/cache/posthoc-reproduction. No model inference is performed.",
        "",
        "| Post-hoc figure | PNG | SVG |",
        "|---|---|---|",
    ]
    for p in plots[::2]:
        report.append(f"| {p.stem} | [PNG]({p.name}) | [SVG]({p.with_suffix('.svg').name}) |")
    (out / "posthoc-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    assert before == {p.relative_to(root).as_posix(): file_hash(p) for p in immutable}
    outputs = sorted(
        p
        for p in out.iterdir()
        if p.is_file() and p.suffix not in {".py", ".pyc"} and p.name != "provenance.json"
    )
    memo = root / "notes/research/_extensions/_2026-09-13.md"
    atomic_json(
        out / "provenance.json",
        {
            "analysis_status": "post_hoc",
            "date": "2026-09-14",
            "confirmatory_tests_added": 0,
            "command": command,
            "protocol_commit_study1": state["protocol_commit"],
            "source_results_sha256": file_hash(results_file),
            "immutable_inputs": before,
            "memo": {
                "description": "research extensions memo of 2026-09-13, not in the tree",
                "sections": [3, 5],
                "sha256": file_hash(memo) if memo.exists() else None,
            },
            "script_sha256": file_hash(Path(__file__)),
            "aggregation": (
                "three equal windows within repository/horizon, then 300 equal repositories"
            ),
            "seed": None,
            "seed_reason": "deterministic saved-forecast accounting; no random sampling",
            "window_count": len(windows),
            "window_decile_count": len(deciles),
            "paired_repository_count": len(pairs),
            "paired_summary_count": len(summaries),
            "max_window_accounting_residual": float(windows.accounting_residual.abs().max()),
            "original_18_mean_differences_match": True,
            "immutable_input_hashes_unchanged": True,
            "versions": {
                "numpy": np.__version__,
                "pandas": pd.__version__,
                "matplotlib": matplotlib.__version__,
                "pyarrow": pa.__version__,
            },
            "outputs": {
                p.name: {"sha256": file_hash(p), "bytes": p.stat().st_size} for p in outputs
            },
        },
    )
    print(
        json.dumps(
            {
                "analysis_status": "post_hoc",
                "windows": len(windows),
                "pairs": len(pairs),
                "figures": len(plots),
                "max_residual": float(windows.accounting_residual.abs().max()),
            }
        )
    )


if __name__ == "__main__":
    main()

import numpy as np
import pandas as pd
import pytest

from pulsegraph.evaluation.artifacts import file_hash
from pulsegraph.provenance import atomic_json
from pulsegraph.study2.constants import VARIANTS
from pulsegraph.study2.runner import _evaluate, external_dataset


@pytest.mark.parametrize("cutoff", ["2026-06-03", "2026-07-03", "2026-08-02"])
@pytest.mark.parametrize("mutation", ["perturb", "permute", "extend"])
def test_every_origin_forecast_and_scale_ignore_future(tmp_path, cutoff, mutation):
    dates = pd.date_range("2025-09-01", "2026-08-31")
    baseline = pd.Series(np.arange(len(dates), dtype=float), index=dates)
    changed = baseline.copy()
    if mutation == "perturb":
        changed.loc[changed.index >= cutoff] += 10000
    elif mutation == "permute":
        mask = changed.index >= cutoff
        changed.loc[mask] = changed.loc[mask].to_numpy()[::-1]
    else:
        changed = pd.concat(
            [changed, pd.Series(9999.0, index=pd.date_range("2026-09-01", "2026-12-31"))]
        )

    class Pool:
        def __init__(self):
            self.observed = []

        def forecast(self, context, horizon, key):
            if key.endswith(cutoff):
                # Ordinal counts identify every date the model actually observed.
                observed_dates = dates[context.astype(int)]
                assert (observed_dates < pd.Timestamp(cutoff)).all()
                self.observed.append((context.tolist(), float(context.mean()), horizon))
            return {
                n: dict(deciles=np.full((horizon, 9), context.mean()).tolist(), distributions=None)
                for n in VARIANTS
            }

    first, second = Pool(), Pool()
    _evaluate({("packages", "a"): baseline}, tmp_path / "first", first, metadata={})
    _evaluate({("packages", "a"): changed}, tmp_path / "second", second, metadata={})
    assert first.observed == second.observed and len(first.observed) == 2


def test_external_signals_cannot_rewrite_selection_context(tmp_path):
    frame = pd.DataFrame(
        dict(series_id="a", date=pd.date_range("2025-09-01", "2026-08-31"), count=np.ones(365))
    )
    context = tmp_path / "context.parquet"
    frame.loc[frame.date < "2026-06-03"].to_parquet(context, index=False)
    manifest = tmp_path / "manifest.json"
    atomic_json(manifest, dict(series=[dict(series_id="a")], context_sha256=file_hash(context)))
    signals = tmp_path / "signals.parquet"
    frame.to_parquet(signals, index=False)

    def readiness():
        return dict(
            panels=dict(
                packages={
                    name: dict(path=str(path), sha256=file_hash(path))
                    for name, path in dict(
                        manifest=manifest, context=context, signals=signals
                    ).items()
                }
            )
        )

    assert len(external_dataset(readiness())["packages", "a"]) == 365
    frame.loc[0, "count"] = 2
    frame.to_parquet(signals, index=False)
    with pytest.raises(ValueError, match="selection context"):
        external_dataset(readiness())

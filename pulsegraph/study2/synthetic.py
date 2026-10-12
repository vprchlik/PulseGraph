"""Registered 18-cell intervention grid with 30 independent replicate blocks."""

from itertools import product

import numpy as np
import pandas as pd
from scipy.stats import poisson

from pulsegraph.config import ROOT_DIR
from pulsegraph.provenance import read_json
from pulsegraph.random import derived_seed
from pulsegraph.study2.constants import PROTOCOL_COMMIT, PROTOCOL_SHA256, SEEDS
from pulsegraph.study2.distributions import CountLaw
from pulsegraph.study2.models import law_forecast


def cells():
    return [
        dict(cell_id=f"cell{i:02}", zero_probability=z, positive_mean=mu, persistence=rho)
        for i, (z, mu, rho) in enumerate(product((0.2, 0.8, 0.95), (1, 5, 25), (0.0, 0.8)))
    ]


def streams(replicate):
    if not isinstance(replicate, int) or not 0 <= replicate < 30:
        raise ValueError("Registered replicate IDs are 0 through 29")
    arrays = []
    for name in ("occurrence", "size"):
        seed = derived_seed(SEEDS["synthetic"], "replicate", replicate, name)
        rng = np.random.Generator(np.random.PCG64(seed))
        arrays.append(np.maximum(rng.random(270), np.nextafter(0.0, 1.0)))
    return tuple(arrays)


def grid_manifest():
    return dict(
        protocol_commit=PROTOCOL_COMMIT,
        protocol_sha256=PROTOCOL_SHA256,
        component="synthetic",
        seed=SEEDS["synthetic"],
        cells=cells(),
        n_cells=18,
        replicates_per_cell=30,
        n_series=540,
        observations=270,
        origins=[180, 210, 240],
        horizons=[7, 30],
        rng="PCG64",
        zero_uniform_policy="replace_exact_zero_with_nextafter(0,1)",
        streams=[
            dict(
                replicate=r,
                occurrence_seed=derived_seed(SEEDS["synthetic"], "replicate", r, "occurrence"),
                size_seed=derived_seed(SEEDS["synthetic"], "replicate", r, "size"),
            )
            for r in range(30)
        ],
        series=[
            dict(series_id=f"{c['cell_id']}/rep{r:02}", cell_id=c["cell_id"], replicate=r)
            for c in cells()
            for r in range(30)
        ],
        inference_unit="replicate block preserving all 18 cells",
        common_random_numbers="same occurrence and size uniforms across cells within replicate",
        oracle="known Markov occurrence and shifted-Poisson positive law; diagnostic only",
    )


def generate(cell, replicate):
    if cell not in cells():
        raise ValueError("Unregistered generator cell")
    occurrence, size = streams(replicate)
    pi, rho = 1 - cell["zero_probability"], cell["persistence"]
    latent = np.zeros(270, dtype=bool)
    latent[0] = occurrence[0] < pi
    for t in range(1, 270):
        latent[t] = occurrence[t] < pi + rho * (float(latent[t - 1]) - pi)
    positive = 1 + poisson.ppf(size, cell["positive_mean"] - 1).astype(np.int64)
    return latent.astype(np.int64) * positive


def grid_dataset():
    manifest = read_json(ROOT_DIR / "study/study2/grid_manifest.json")
    if manifest != grid_manifest():
        raise ValueError("Synthetic grid declaration changed")
    lookup = {c["cell_id"]: c for c in manifest["cells"]}
    return {
        ("synthetic", row["series_id"]): pd.Series(
            generate(lookup[row["cell_id"]], row["replicate"])
        )
        for row in manifest["series"]
    }


def oracle_laws(cell, context, horizon):
    context = np.asarray(context, float)
    if cell not in cells() or context.ndim != 1 or not len(context) or horizon not in (7, 30):
        raise ValueError("Oracle requires registered cell, observed context and horizon")
    pi, rho = 1 - cell["zero_probability"], cell["persistence"]
    last = float(context[-1] > 0)
    return [
        CountLaw(
            dict(
                kind="hurdle",
                p=pi + rho**lead * (last - pi),
                positive=dict(kind="poisson", mu=cell["positive_mean"] - 1, shift=1),
            )
        )
        for lead in range(1, horizon + 1)
    ]


def oracle_forecast(series_id, context, horizon):
    cell_id = series_id.split("/", 1)[0]
    cell = next(c for c in cells() if c["cell_id"] == cell_id)
    return law_forecast(
        oracle_laws(cell, context, horizon), dict(oracle=True, diagnostic_only=True, generator=cell)
    )

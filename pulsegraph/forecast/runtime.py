"""Lazy loading from immutable model snapshots. No load occurs at import time."""

import re

from pulsegraph.config import MODELS_DIR
from pulsegraph.random import validate_seed
from pulsegraph.validation import positive_int


def validate_revision(revision: str) -> str:
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("An exact 40-character lowercase model revision hash is required")
    return revision


def load_snapshot(model_id: str, revision: str, *, seed: int, threads: int) -> str:
    validate_revision(revision)
    validate_seed(seed)
    positive_int(threads, "threads")
    import torch
    from huggingface_hub import snapshot_download

    torch.manual_seed(seed % (2**63))
    torch.set_num_threads(threads)
    torch.use_deterministic_algorithms(True)
    return snapshot_download(repo_id=model_id, revision=revision, cache_dir=str(MODELS_DIR))


def as_numpy(value):
    import numpy as np

    if hasattr(value, "detach"):
        value = value.detach().cpu().numpy()
    return np.asarray(value, dtype=np.float64)

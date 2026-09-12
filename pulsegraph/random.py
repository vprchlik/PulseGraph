"""Stable seeds independent of process hash randomization and iteration order."""

import hashlib
import json

import numpy as np


def validate_seed(seed: int) -> int:
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)) or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    return int(seed)


def derived_seed(seed: int, *parts, values=None) -> int:
    payload = json.dumps([validate_seed(seed), *parts], sort_keys=True, allow_nan=False)
    digest = hashlib.sha256(payload.encode("utf-8"))
    if values is not None:
        digest.update(np.asarray(values, dtype="<f8").tobytes())
    # uint32 also fits LightGBM and common model-library seed APIs.
    return int.from_bytes(digest.digest()[:4], "little")

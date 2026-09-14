from copy import deepcopy

import numpy as np
import pytest

from pulsegraph.config import ROOT_DIR
from pulsegraph.evaluation.metrics import evaluate_forecast
from pulsegraph.evaluation.registration import (
    PROTOCOL_COMMIT,
    PROTOCOL_SHA256,
    _git,
    validate_declarations,
    verify_readiness,
    verify_source_registration,
)
from pulsegraph.forecast.output import COMMON_QUANTILES, ForecastOutput
from pulsegraph.provenance import read_json, sha256_bytes


def test_registered_protocol_and_full_comparison_declaration():
    spec = read_json(ROOT_DIR / "study/run_spec.json")
    family = read_json(ROOT_DIR / "study/comparisons.json")
    config = validate_declarations(spec, family)
    assert config.cutoffs == ("2025-12-05", "2026-03-05", "2026-06-03")
    blob = _git(ROOT_DIR, "show", f"{PROTOCOL_COMMIT}:PROTOCOL.md")
    assert sha256_bytes(blob) == PROTOCOL_SHA256
    assert (ROOT_DIR / "PROTOCOL.md").read_bytes().startswith(blob)
    assert len(spec["baselines"]) == 15
    assert len(family["comparisons"]) == 18


@pytest.fixture
def source_registration(tmp_path, monkeypatch):
    blob = _git(ROOT_DIR, "show", f"{PROTOCOL_COMMIT}:PROTOCOL.md")
    assert sha256_bytes(blob) == PROTOCOL_SHA256
    implementation = "a" * 40
    responses = {
        "rev-parse": implementation.encode(),
        "show": blob,
        "status": b"",
        "ls-files": b"PROTOCOL.md\nstudy/run_spec.json\nstudy/comparisons.json\n",
    }

    def git(_, *args):
        if args[0] == "show":
            assert args == ("show", f"{PROTOCOL_COMMIT}:PROTOCOL.md")
        return responses[args[0]]

    monkeypatch.setattr("pulsegraph.evaluation.registration._git", git)
    return tmp_path, implementation, blob, responses


@pytest.mark.parametrize("appendix", [b"", b"\n## Dated addition\nRegistered separately.\n"])
def test_registered_prefix_accepts_appendices_and_hashes_entire_file(source_registration, appendix):
    root, implementation, blob, _ = source_registration
    current = blob + appendix
    (root / "PROTOCOL.md").write_bytes(current)
    hashes = verify_source_registration(root, implementation)
    assert hashes["PROTOCOL.md"] == sha256_bytes(current)


@pytest.mark.parametrize("location", ["first", "middle", "last"])
def test_changed_byte_inside_registered_prefix_fails(source_registration, location):
    root, implementation, blob, _ = source_registration
    position = {"first": 0, "middle": len(blob) // 2, "last": -1}[location]
    changed = bytearray(blob)
    changed[position] ^= 1
    (root / "PROTOCOL.md").write_bytes(changed + b"\n## Dated addition\n")
    with pytest.raises(ValueError, match="Protocol bytes"):
        verify_source_registration(root, implementation)


def test_committed_blob_must_match_registered_sha_even_if_it_is_a_prefix(source_registration):
    root, implementation, blob, responses = source_registration
    responses["show"] = blob + b"changed commit blob"
    (root / "PROTOCOL.md").write_bytes(responses["show"] + b"\n## Dated addition\n")
    with pytest.raises(ValueError, match="Protocol bytes"):
        verify_source_registration(root, implementation)


@pytest.mark.parametrize(
    "mutation",
    [
        "protocol_null",
        "protocol_wrong",
        "sha",
        "seed",
        "revision",
        "model",
        "count",
        "duplicate",
        "family_seed",
        "calendar",
    ],
)
def test_invalid_registration_is_rejected(mutation):
    spec = deepcopy(read_json(ROOT_DIR / "study/run_spec.json"))
    family = deepcopy(read_json(ROOT_DIR / "study/comparisons.json"))
    if mutation == "protocol_null":
        spec["protocol_commit"] = None
    elif mutation == "protocol_wrong":
        spec["protocol_commit"] = "a" * 40
    elif mutation == "sha":
        spec["protocol_sha256"] = "a" * 64
    elif mutation == "seed":
        del spec["seeds"]["selection"]
    elif mutation == "revision":
        spec["foundation_models"][0]["revision"] = "main"
    elif mutation == "model":
        spec["foundation_models"][0]["model_id"] = "other/model"
    elif mutation == "count":
        family["comparison_count"] = 17
    elif mutation == "duplicate":
        family["comparisons"][0] = family["comparisons"][1]
    elif mutation == "family_seed":
        family["bootstrap_seed"] = 1
    elif mutation == "calendar":
        spec["config"]["cutoffs"] = ["2025-12-04", "2026-03-05", "2026-06-03"]
    with pytest.raises(ValueError):
        validate_declarations(spec, family)


def test_null_implementation_and_unresolved_readiness_fail_before_runtime(tmp_path):
    with pytest.raises(ValueError, match="implementation commit"):
        verify_source_registration(tmp_path, None)
    with pytest.raises(ValueError, match="readiness"):
        verify_readiness(
            {"protocol_commit": PROTOCOL_COMMIT, "protocol_sha256": PROTOCOL_SHA256}, tmp_path, {}
        )


def test_qscore9_is_twice_decile_loss_even_for_zero_targets():
    output = ForecastOutput(
        "a/b", "model", 2, 90, np.array(COMMON_QUANTILES), np.tile(np.arange(9), (2, 1))
    )
    score = evaluate_forecast(
        output,
        [0, 0],
        context=np.arange(90),
        quantile_levels=COMMON_QUANTILES,
        seasonal_period=7,
        seed=1,
    )
    manual = 2 * np.mean((1 - np.array(COMMON_QUANTILES)) * np.arange(9))
    assert score["qscore9"] == pytest.approx(manual)
    assert score["qscore9"] == 2 * score["mean_pinball_loss"]
    assert np.isnan(score["wql"]) and np.isnan(score["crps_mean"])
    changed_grid = evaluate_forecast(
        output,
        [0, 0],
        context=np.arange(90),
        quantile_levels=[0.1, 0.5, 0.9],
        seasonal_period=7,
        seed=1,
    )
    assert np.isnan(changed_grid["qscore9"])

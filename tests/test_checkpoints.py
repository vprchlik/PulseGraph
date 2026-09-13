from dataclasses import asdict

import numpy as np
import pandas as pd
import pytest

from pulsegraph.evaluation.backtest import BacktestConfig
from pulsegraph.evaluation.registered_run import _checkpointed_run, run_registered
from pulsegraph.forecast.baselines import LastValueForecaster
from pulsegraph.provenance import read_json


def fixture():
    dataset = {
        name: pd.Series(np.arange(110) % 4, index=pd.date_range("2024-01-01", periods=110))
        for name in ["a/one", "b/two", "c/three"]
    }
    config = BacktestConfig((7,), ("2024-04-01",), 90, tuple(np.arange(1, 10) / 10), 7, 123)
    metadata = {
        "data_kind": "synthetic",
        "protocol_commit": None,
        "protocol_sha256": None,
        "implementation_commit": "a" * 40,
        "source_sha256": {},
        "packages": {},
        "config": asdict(config),
        "models": ["last_value"],
        "repositories": sorted(dataset),
        "input_sha256": {},
        "readiness_sha256": "b" * 64,
        "comparison_family": {},
        "command": ["offline-test"],
        "hardware": {"gpu_model": "mock"},
    }
    return dataset, config, metadata


def test_crash_resumes_only_completed_repositories_and_logs_resume(tmp_path):
    dataset, config, metadata = fixture()
    called = []
    fail = True

    class Model(LastValueForecaster):
        def forecast(self, context, horizon, repo_name):
            called.append(repo_name)
            if repo_name == "b/two" and fail:
                raise MemoryError("simulated OOM")
            return super().forecast(context, horizon, repo_name)

    kwargs = dict(
        metadata=metadata,
        dataset=dataset,
        config=config,
        model_factory=lambda _: Model(seed=123),
        release=lambda _: None,
        measure=lambda _: {},
    )
    with pytest.raises(MemoryError):
        _checkpointed_run(tmp_path, **kwargs)
    state = read_json(tmp_path / "run.json")
    assert state["completed_repositories"] == ["a/one"]
    assert state["status"] == "failed" and state["failures"][0]["repo_name"] == "b/two"
    assert called == ["a/one", "b/two"]  # c/three was never reached or skipped.
    fail = False
    rows, state = _checkpointed_run(tmp_path, **kwargs)
    assert called == ["a/one", "b/two", "b/two", "c/three"]
    assert len(rows) == 3
    assert state["resumes"][0]["completed_repositories_reused"] == ["a/one"]
    # Read/validate complete checkpoints without new calls.
    _checkpointed_run(tmp_path, **kwargs)
    assert len(called) == 4
    metadata["implementation_commit"] = "b" * 40
    with pytest.raises(ValueError, match="Resume inputs"):
        _checkpointed_run(tmp_path, **kwargs)


def test_checkpoint_corruption_and_incomplete_repository_fail(tmp_path):
    dataset, config, metadata = fixture()
    kwargs = dict(
        metadata=metadata,
        dataset=dataset,
        config=config,
        model_factory=lambda _: LastValueForecaster(seed=123),
        release=lambda _: None,
        measure=lambda _: {},
    )
    _checkpointed_run(tmp_path, **kwargs)
    path = next((tmp_path / "checkpoints").glob("*.parquet"))
    path.write_bytes(b"corrupted")
    with pytest.raises(ValueError, match="hash mismatch"):
        _checkpointed_run(tmp_path, **kwargs)


@pytest.mark.parametrize("fail", [False, True])
def test_factory_once_per_model_and_release_only_at_end(tmp_path, fail):
    dataset, config, metadata = fixture()
    metadata["models"] = ["chronos2", "timesfm3", "timesfm2p5"]
    created, released, forecasts = [], [], []

    class Model(LastValueForecaster):
        def forecast(self, context, horizon, repo_name):
            assert released == []
            forecasts.append((self.name, repo_name))
            if fail and repo_name == "b/two" and self.name == "timesfm3":
                raise MemoryError("simulated OOM")
            return super().forecast(context, horizon, repo_name)

    def factory(name):
        created.append(name)
        model = Model(seed=123)
        model.name = name
        return model

    def run():
        return _checkpointed_run(
            tmp_path,
            metadata=metadata,
            dataset=dataset,
            config=config,
            model_factory=factory,
            release=lambda model: released.append(model.name),
            measure=lambda _: {},
        )

    if fail:
        with pytest.raises(MemoryError):
            run()
        assert len(forecasts) == 5
        assert read_json(tmp_path / "run.json")["completed_repositories"] == ["a/one"]
    else:
        rows, _ = run()
        assert len(rows) == len(forecasts) == 9
    assert created == metadata["models"]
    assert released == list(reversed(created))


def test_public_runner_checks_gate_before_gpu_or_model_calls(monkeypatch, tmp_path):
    def rejected(**kwargs):
        raise ValueError("gate rejected")

    def forbidden(*args, **kwargs):
        pytest.fail("GPU or model accessed before gate")

    monkeypatch.setattr("pulsegraph.evaluation.registered_run.real_run_gate", rejected)
    monkeypatch.setattr("pulsegraph.evaluation.registered_run.configure_gpu", forbidden)
    monkeypatch.setattr("pulsegraph.evaluation.registered_run.make_registered_model", forbidden)
    with pytest.raises(ValueError, match="gate rejected"):
        run_registered(
            output_dir=tmp_path,
            readiness_path="none",
            signals_path="none",
            manifest_path="none",
            implementation_commit=None,
            command=[],
        )

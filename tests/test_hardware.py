import sys
from types import SimpleNamespace

import pytest

from pulsegraph.forecast.hardware import configure_gpu, memory_snapshot


def test_gpu_budget_versions_and_peak_enforcement(monkeypatch):
    monkeypatch.setattr("pulsegraph.forecast.hardware.platform.platform", lambda: "Windows-fixture")
    limits = []
    cuda = SimpleNamespace(
        is_available=lambda: True,
        get_device_properties=lambda _: SimpleNamespace(
            name="NVIDIA GeForce RTX 4070 SUPER", total_memory=12_000_000_000
        ),
        mem_get_info=lambda _: (10_000_000_000, 12_000_000_000),
        set_per_process_memory_fraction=lambda fraction, device: limits.append((fraction, device)),
        reset_peak_memory_stats=lambda _: None,
        synchronize=lambda _: None,
        max_memory_allocated=lambda _: 3_000_000_000,
        max_memory_reserved=lambda _: 4_000_000_000,
    )
    monkeypatch.setitem(
        sys.modules,
        "torch",
        SimpleNamespace(
            cuda=cuda, version=SimpleNamespace(cuda="fixture-cuda"), __version__="fixture-torch"
        ),
    )

    def driver(command, **kwargs):
        assert command[0] == "nvidia-smi" and "--query-gpu=driver_version" in command
        return "fixture-driver\n"

    monkeypatch.setattr("pulsegraph.forecast.hardware.subprocess.check_output", driver)
    hardware = configure_gpu()
    assert limits == [(7 / 12, 0)]
    assert hardware["gpu_driver"] == "fixture-driver"
    assert (
        hardware["cuda_version"] == "fixture-cuda"
        and hardware["pytorch_version"] == "fixture-torch"
    )
    assert hardware["peak_vram_limit_bytes"] == 8_000_000_000
    assert memory_snapshot()["peak_reserved_bytes"] == 4_000_000_000
    cuda.max_memory_reserved = lambda _: 8_000_000_000
    with pytest.raises(RuntimeError, match="memory exceeded"):
        memory_snapshot()
    cuda.mem_get_info = lambda _: (2_000_000_000, 12_000_000_000)
    with pytest.raises(ValueError, match="Insufficient free"):
        configure_gpu()

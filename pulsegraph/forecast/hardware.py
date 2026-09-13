"""CUDA provenance and a conservative allocator budget; no model loading."""

import os
import platform
import subprocess

VRAM_LIMIT_BYTES = 8_000_000_000
ALLOCATOR_LIMIT_BYTES = 7_000_000_000  # Leave room for CUDA context/library allocations.


def configure_gpu():
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    import torch

    if not torch.cuda.is_available():
        raise ValueError("Registered foundation models require CUDA")
    properties = torch.cuda.get_device_properties(0)
    if "4070 SUPER" not in properties.name.upper():
        raise ValueError("GPU differs from the declared RTX 4070 SUPER")
    driver = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader", "--id=0"],
        stderr=subprocess.DEVNULL,
        text=True,
    ).strip()
    free, total = torch.cuda.mem_get_info(0)
    budget = min(ALLOCATOR_LIMIT_BYTES, free - 1_000_000_000)
    if budget < 2_000_000_000:
        raise ValueError("Insufficient free GPU memory; retry when the shared GPU is available")
    torch.cuda.set_per_process_memory_fraction(budget / properties.total_memory, 0)
    torch.cuda.reset_peak_memory_stats(0)
    return {
        "gpu_model": properties.name,
        "gpu_driver": driver,
        "cuda_version": torch.version.cuda,
        "pytorch_version": torch.__version__,
        "platform": platform.platform(),
        "gpu_total_bytes": total,
        "gpu_free_at_start_bytes": free,
        "allocator_limit_bytes": budget,
        "peak_vram_limit_bytes": VRAM_LIMIT_BYTES,
        "batch_size": 1,
        "baselines_device": "cpu",
        "foundation_device": "cuda:0",
        "memory_measurement": "PyTorch allocator; 1 GB reserved for CUDA/library overhead",
    }


def memory_snapshot():
    import torch

    torch.cuda.synchronize(0)
    snapshot = {
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(0),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(0),
    }
    if snapshot["peak_reserved_bytes"] >= VRAM_LIMIT_BYTES:
        raise RuntimeError("GPU memory exceeded the registered operational limit")
    return snapshot

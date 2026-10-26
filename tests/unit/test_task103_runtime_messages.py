"""TASK-103 CUDA failure-class recovery message coverage."""

import pytest

import ts_runtime


def _runtime(**overrides):
    value = {
        "selected_device": "unavailable",
        "fallback_reason": "cuda_required_but_unavailable",
        "torch_cuda_build": "12.8",
        "cuda_precision_ok": True,
        "cuda_arch_supported": True,
        "cuda_device_capability": "sm_120",
        "torch_cuda_arch_list": ["sm_75", "sm_120"],
    }
    value.update(overrides)
    return value


@pytest.mark.parametrize(
    ("runtime", "failure_class", "message"),
    [
        (
            _runtime(
                cuda_arch_supported=False,
                cuda_device_capability="sm_120",
                torch_cuda_arch_list=["sm_75", "sm_90"],
            ),
            "gpu_newer_than_build",
            "newer than this package's PyTorch build",
        ),
        (
            _runtime(
                cuda_arch_supported=False,
                cuda_device_capability="sm_61",
                torch_cuda_arch_list=["sm_75", "sm_120"],
            ),
            "gpu_older_than_build",
            "not supported by the CUDA 12.8 package",
        ),
        (
            _runtime(torch_cuda_build=None),
            "cpu_only_build",
            "CPU-only PyTorch",
        ),
        (
            _runtime(cuda_precision_ok=False),
            "precision_policy",
            "precision policy could not be enforced",
        ),
        (
            _runtime(),
            "driver_or_container",
            "Confirm NVIDIA container access",
        ),
    ],
)
def test_cuda_failure_class_has_actionable_recovery(runtime, failure_class, message):
    assert ts_runtime._cuda_failure_class(runtime) == failure_class
    assert message in ts_runtime._ml_runtime_recovery_message(runtime)


def test_cpu_fallback_hint_only_appears_for_an_actual_fallback():
    fallback = _runtime(
        selected_device="cpu",
        fallback_reason="cuda_unavailable",
    )
    explicit_cpu = _runtime(
        selected_device="cpu",
        fallback_reason=None,
    )
    cuda = _runtime(
        selected_device="cuda",
        fallback_reason=None,
    )

    assert "selected CPU automatically" in ts_runtime._ml_runtime_recovery_message(
        fallback
    )
    assert ts_runtime._ml_runtime_recovery_message(explicit_cpu) == ""
    assert ts_runtime._ml_runtime_recovery_message(cuda) == ""

"""TASK-103 (N8): IEEE FP32 enforcement, decisive CUDA kernel probe, and arch diagnostics.

No GPU is required: CUDA is simulated with monkeypatched torch.cuda functions and the
torch.backends precision API families are exercised with SimpleNamespace stubs.
"""

import dataclasses
import json
import os
import subprocess
import sys
import warnings
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import torch

import ts_device


WEBAPP_DIR = Path(__file__).resolve().parents[2] / "webapp"
REPO_ROOT = WEBAPP_DIR.parent

# torch 2.6.0+cu126 wheels: SASS for sm_50..sm_90, no PTX -> Blackwell sm_120 unsupported.
CU126_ARCH_LIST = ["sm_50", "sm_60", "sm_70", "sm_75", "sm_80", "sm_86", "sm_90"]
# torch 2.10.0+cu128 wheels (linux x86_64): Turing..Blackwell plus compute_120 PTX.
CU128_ARCH_LIST = ["sm_75", "sm_80", "sm_86", "sm_90", "sm_100", "sm_120", "compute_120"]
NO_KERNEL_IMAGE = "RuntimeError: CUDA error: no kernel image is available for execution on the device"
NEW_FIELDS = (
    "cuda_device_capability",
    "torch_cuda_arch_list",
    "cuda_arch_supported",
    "cudnn_version",
    "cuda_fp32_conv",
    "cuda_fp32_matmul",
    "cuda_precision_ok",
    "cuda_kernel_probe_ok",
)


class _FakeCudaProbe:
    def cpu(self):
        return self


def _ieee_precision():
    return True, {"api": "stub", "conv": "ieee", "matmul": "ieee", "config_error": None}


def _simulate_cuda(
    monkeypatch,
    *,
    capability=(7, 5),
    arch_list=None,
    kernel_probe=lambda: None,
    precision=_ieee_precision,
    cudnn_version=90100,
):
    """Simulate a visible CUDA device whose zeros probe succeeds."""
    monkeypatch.setattr(ts_device.torch.cuda, "is_available", Mock(return_value=True))
    monkeypatch.setattr(ts_device.torch.cuda, "get_device_name", Mock(return_value="NVIDIA Test GPU"))
    monkeypatch.setattr(ts_device.torch.cuda, "get_device_capability", Mock(return_value=capability))
    monkeypatch.setattr(
        ts_device.torch.cuda,
        "get_arch_list",
        Mock(return_value=list(CU128_ARCH_LIST if arch_list is None else arch_list)),
    )
    monkeypatch.setattr(ts_device.torch.backends.cudnn, "version", Mock(return_value=cudnn_version))
    monkeypatch.setattr(ts_device.torch.version, "cuda", "12.8", raising=False)
    monkeypatch.setattr(ts_device.torch, "zeros", Mock(return_value=_FakeCudaProbe()))
    monkeypatch.setattr(ts_device, "_cuda_kernel_probe", Mock(side_effect=kernel_probe))
    monkeypatch.setattr(ts_device, "cuda_precision_ok", precision)


# ---------------------------------------------------------------------------
# Arch suffix parsing and aggregation (advisory diagnostics)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("arch", "major", "minor", "expected"),
    [
        ("sm_75", 7, 5, True),
        ("sm_90", 12, 0, False),
        ("sm_120", 12, 0, True),
        ("sm_120", 12, 1, True),
        ("compute_90", 12, 0, True),
        ("compute_90a", 12, 0, False),
        ("compute_90a", 9, 0, True),
        ("sm_90a", 9, 0, True),
        ("sm_90a", 12, 0, False),
        ("sm_100f", 10, 3, True),
        ("sm_100f", 12, 0, False),
        ("compute_100f", 12, 0, False),
        ("compute_100f", 10, 3, True),
        ("sm_86", 8, 0, False),
        ("sm_80", 8, 6, True),
        ("compute_120", 7, 5, False),
        ("sm_foo", 12, 0, None),
        ("gfx90a", 9, 0, None),
        ("", 7, 5, None),
    ],
)
def test_arch_code_covers_device_suffix_rules(arch, major, minor, expected):
    assert ts_device._arch_code_covers_device(arch, major, minor) is expected


@pytest.mark.parametrize(
    ("verdicts", "expected"),
    [
        ([True, False], True),
        ([None, True], True),
        ([False, False], False),
        ([False], False),
        ([], None),
        ([None], None),
        ([None, False], None),
    ],
)
def test_arch_support_aggregation(verdicts, expected):
    assert ts_device._aggregate_arch_support(verdicts) is expected


@pytest.mark.parametrize(
    ("capability", "arch_list", "expected"),
    [
        ((12, 0), CU126_ARCH_LIST, False),
        ((12, 0), CU128_ARCH_LIST, True),
        ((7, 5), CU128_ARCH_LIST, True),
        ((6, 1), CU128_ARCH_LIST, False),
        ((12, 0), ["sm_foo"], None),
        ((12, 0), [], None),
    ],
)
def test_cuda_arch_diagnostics_classifies_device_against_build(monkeypatch, capability, arch_list, expected):
    monkeypatch.setattr(ts_device.torch.cuda, "get_device_capability", Mock(return_value=capability))
    monkeypatch.setattr(ts_device.torch.cuda, "get_arch_list", Mock(return_value=list(arch_list)))

    details = ts_device._cuda_arch_diagnostics()

    assert details["cuda_device_capability"] == f"sm_{capability[0]}{capability[1]}"
    assert details["torch_cuda_arch_list"] == tuple(arch_list)
    assert details["cuda_arch_supported"] is expected


def test_cuda_arch_diagnostics_tolerates_cpu_only_torch(monkeypatch):
    monkeypatch.setattr(
        ts_device.torch.cuda,
        "get_device_capability",
        Mock(side_effect=AssertionError("Torch not compiled with CUDA enabled")),
    )

    assert ts_device._cuda_arch_diagnostics() == {
        "cuda_device_capability": None,
        "torch_cuda_arch_list": (),
        "cuda_arch_supported": None,
    }


# ---------------------------------------------------------------------------
# Kernel probe is decisive; arch diagnostics are advisory
# ---------------------------------------------------------------------------


def test_arch_mismatch_with_failing_probe_falls_back_to_cpu_under_auto(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "auto")
    _simulate_cuda(
        monkeypatch,
        capability=(12, 0),
        arch_list=CU126_ARCH_LIST,
        kernel_probe=lambda: NO_KERNEL_IMAGE,
    )

    diagnostics = ts_device.build_runtime_diagnostics()

    assert diagnostics["selected_device"] == "cpu"
    assert diagnostics["status"] == "ok"
    assert diagnostics["fallback_reason"] == "cuda_unavailable"
    assert diagnostics["torch_cuda_available"] is False
    assert diagnostics["cuda_device_name"] is None
    assert diagnostics["cuda_arch_supported"] is False
    assert diagnostics["cuda_device_capability"] == "sm_120"
    assert diagnostics["torch_cuda_arch_list"] == CU126_ARCH_LIST
    assert diagnostics["cuda_kernel_probe_ok"] is False
    assert "no kernel image" in diagnostics["cuda_probe_error"]
    assert "[GPU sm_120 is not covered by this PyTorch build's arch list: " in diagnostics["cuda_probe_error"]
    assert "sm_90]" in diagnostics["cuda_probe_error"]

    move_to_cuda = Mock()
    move_to_cpu = Mock()
    selection = ts_device.select_model_device("TestModel", move_to_cuda=move_to_cuda, move_to_cpu=move_to_cpu)

    assert selection.selected_device == "cpu"
    assert selection.fallback_reason == "cuda_unavailable"
    assert selection.cuda_arch_supported is False
    assert "sm_120" in selection.cuda_probe_error
    move_to_cuda.assert_not_called()
    move_to_cpu.assert_called_once()


def test_arch_mismatch_with_failing_probe_is_fatal_under_cuda_policy(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "cuda")
    _simulate_cuda(
        monkeypatch,
        capability=(12, 0),
        arch_list=CU126_ARCH_LIST,
        kernel_probe=lambda: NO_KERNEL_IMAGE,
    )

    diagnostics = ts_device.build_runtime_diagnostics()
    assert diagnostics["selected_device"] == "unavailable"
    assert diagnostics["status"] == "fatal"
    assert diagnostics["fallback_reason"] == "cuda_required_but_unavailable"

    with pytest.raises(ts_device.DevicePolicyError) as error:
        ts_device.select_model_device("TestModel")

    assert "requires CUDA" in str(error.value)
    assert "sm_120" in str(error.value)


def test_arch_mismatch_alone_never_makes_cuda_ineligible(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "auto")
    _simulate_cuda(monkeypatch, capability=(12, 0), arch_list=CU126_ARCH_LIST)

    move_to_cuda = Mock()
    selection = ts_device.select_model_device("TestModel", move_to_cuda=move_to_cuda)

    assert selection.selected_device == "cuda"
    assert selection.fallback_reason is None
    assert selection.cuda_arch_supported is False
    assert selection.cuda_kernel_probe_ok is True
    assert selection.cuda_probe_error is None
    move_to_cuda.assert_called_once()


def test_kernel_probe_failure_makes_cuda_ineligible_even_when_arch_is_supported(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "auto")
    _simulate_cuda(
        monkeypatch,
        capability=(12, 0),
        arch_list=CU128_ARCH_LIST,
        kernel_probe=lambda: "RuntimeError: cuDNN error: CUDNN_STATUS_EXECUTION_FAILED",
    )

    move_to_cuda = Mock()
    selection = ts_device.select_model_device("TestModel", move_to_cuda=move_to_cuda)

    assert selection.selected_device == "cpu"
    assert selection.fallback_reason == "cuda_unavailable"
    assert selection.torch_cuda_available is False
    assert selection.cuda_kernel_probe_ok is False
    assert selection.cuda_arch_supported is True
    assert selection.cuda_probe_error.startswith("CUDA kernel probe failed: RuntimeError: cuDNN error")
    assert "not covered" not in selection.cuda_probe_error
    move_to_cuda.assert_not_called()


def test_zeros_probe_failure_skips_kernel_probe(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "auto")
    _simulate_cuda(monkeypatch)
    monkeypatch.setattr(ts_device.torch, "zeros", Mock(side_effect=RuntimeError("runtime probe failed")))

    diagnostics = ts_device.build_runtime_diagnostics()

    assert diagnostics["selected_device"] == "cpu"
    assert diagnostics["fallback_reason"] == "cuda_unavailable"
    assert diagnostics["cuda_kernel_probe_ok"] is None
    assert "runtime probe failed" in diagnostics["cuda_probe_error"]
    ts_device._cuda_kernel_probe.assert_not_called()


def test_cuda_kernel_probe_computes_expected_result_and_caches_success(monkeypatch):
    real_ones = torch.ones

    def ones_on_cpu(*args, device=None, **kwargs):
        return real_ones(*args, **kwargs)

    monkeypatch.setattr(ts_device, "_cuda_kernel_probe_passed", False)
    monkeypatch.setattr(ts_device.torch, "ones", ones_on_cpu)

    assert ts_device._cuda_kernel_probe() is None
    assert ts_device._cuda_kernel_probe_passed is True

    # Cached once per process: a later call does not touch the device again.
    monkeypatch.setattr(ts_device.torch, "ones", Mock(side_effect=AssertionError("probe re-ran")))
    assert ts_device._cuda_kernel_probe() is None


def test_cuda_kernel_probe_reports_wrong_result(monkeypatch):
    real_ones = torch.ones

    def ones_with_bad_weights(*args, device=None, **kwargs):
        tensor = real_ones(*args, **kwargs)
        return tensor * 2 if tuple(tensor.shape) == (4, 3, 3, 3) else tensor

    monkeypatch.setattr(ts_device, "_cuda_kernel_probe_passed", False)
    monkeypatch.setattr(ts_device.torch, "ones", ones_with_bad_weights)

    error = ts_device._cuda_kernel_probe()

    assert error.startswith("RuntimeError: CUDA kernel probe returned [[11616.0, 11616.0]]")
    assert "5808.0" in error
    assert ts_device._cuda_kernel_probe_passed is False


def test_cuda_kernel_probe_reports_exceptions_without_caching(monkeypatch):
    monkeypatch.setattr(ts_device, "_cuda_kernel_probe_passed", False)
    monkeypatch.setattr(ts_device.torch, "ones", Mock(side_effect=RuntimeError("no kernel image")))

    assert ts_device._cuda_kernel_probe() == "RuntimeError: no kernel image"
    assert ts_device._cuda_kernel_probe_passed is False


def test_cuda_kernel_probe_fails_on_cpu_only_torch(monkeypatch):
    if torch.cuda.is_available():
        pytest.skip("real CUDA device present")
    monkeypatch.setattr(ts_device, "_cuda_kernel_probe_passed", False)

    error = ts_device._cuda_kernel_probe()

    assert error
    assert ts_device._cuda_kernel_probe_passed is False


# ---------------------------------------------------------------------------
# Precision policy: read back at selection time
# ---------------------------------------------------------------------------


def _tf32_conv_readback():
    return {"api": "allow_tf32", "conv": "tf32", "matmul": "ieee"}


def test_precision_readback_failure_falls_back_to_cpu_under_auto(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "auto")
    _simulate_cuda(monkeypatch, precision=ts_device.cuda_precision_ok)
    monkeypatch.setattr(ts_device, "_PRECISION_CONFIG", {"ok": True, "error": None})
    monkeypatch.setattr(ts_device, "current_fp32_precision", _tf32_conv_readback)

    diagnostics = ts_device.build_runtime_diagnostics()

    assert diagnostics["selected_device"] == "cpu"
    assert diagnostics["status"] == "ok"
    assert diagnostics["fallback_reason"] == "cuda_precision_policy_unmet"
    assert diagnostics["torch_cuda_available"] is True
    assert diagnostics["cuda_precision_ok"] is False
    assert diagnostics["cuda_fp32_conv"] == "tf32"
    assert diagnostics["cuda_fp32_matmul"] == "ieee"
    assert diagnostics["cuda_kernel_probe_ok"] is True

    move_to_cuda = Mock()
    move_to_cpu = Mock()
    selection = ts_device.select_model_device("TestModel", move_to_cuda=move_to_cuda, move_to_cpu=move_to_cpu)

    assert selection.selected_device == "cpu"
    assert selection.fallback_reason == "cuda_precision_policy_unmet"
    assert selection.cuda_precision_ok is False
    move_to_cuda.assert_not_called()
    move_to_cpu.assert_called_once()


def test_precision_readback_failure_is_fatal_under_cuda_policy(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "cuda")
    _simulate_cuda(monkeypatch, precision=ts_device.cuda_precision_ok)
    monkeypatch.setattr(ts_device, "_PRECISION_CONFIG", {"ok": True, "error": None})
    monkeypatch.setattr(ts_device, "current_fp32_precision", _tf32_conv_readback)

    diagnostics = ts_device.build_runtime_diagnostics()
    assert diagnostics["selected_device"] == "unavailable"
    assert diagnostics["status"] == "fatal"
    assert diagnostics["fallback_reason"] == "cuda_precision_policy_unmet"

    move_to_cuda = Mock()
    with pytest.raises(ts_device.DevicePolicyError) as error:
        ts_device.select_model_device("TestModel", move_to_cuda=move_to_cuda)

    message = str(error.value)
    assert "requires CUDA" in message
    assert "precision policy" in message
    assert "conv=tf32" in message
    move_to_cuda.assert_not_called()


def test_precision_configuration_failure_blocks_cuda_even_with_ieee_readback(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "cuda")
    _simulate_cuda(monkeypatch, precision=ts_device.cuda_precision_ok)
    monkeypatch.setattr(
        ts_device,
        "_PRECISION_CONFIG",
        {"ok": False, "error": "TORCH_ALLOW_TF32_CUBLAS_OVERRIDE conflicts with TowerScout's IEEE FP32 policy"},
    )
    monkeypatch.setattr(
        ts_device,
        "current_fp32_precision",
        lambda: {"api": "allow_tf32", "conv": "ieee", "matmul": "ieee"},
    )

    ok, details = ts_device.cuda_precision_ok()
    assert ok is False
    assert "TORCH_ALLOW_TF32_CUBLAS_OVERRIDE" in details["config_error"]

    with pytest.raises(ts_device.DevicePolicyError) as error:
        ts_device.select_model_device("TestModel")
    assert "TORCH_ALLOW_TF32_CUBLAS_OVERRIDE" in str(error.value)


def test_precision_is_reevaluated_at_selection_time(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "auto")
    _simulate_cuda(monkeypatch, precision=ts_device.cuda_precision_ok)
    monkeypatch.setattr(ts_device, "_PRECISION_CONFIG", {"ok": True, "error": None})
    readback = {"api": "fp32_precision", "conv": "ieee", "matmul": "ieee"}
    monkeypatch.setattr(ts_device, "current_fp32_precision", lambda: dict(readback))

    assert ts_device.select_model_device("First").selected_device == "cuda"

    # A later import flips matmul to TF32; the next selection must notice.
    readback["matmul"] = "tf32"
    second = ts_device.select_model_device("Second")
    assert second.selected_device == "cpu"
    assert second.fallback_reason == "cuda_precision_policy_unmet"


def test_precision_failure_does_not_affect_cpu_policy(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "cpu")
    monkeypatch.setattr(ts_device.torch.cuda, "is_available", Mock(return_value=True))
    monkeypatch.setattr(ts_device.torch.cuda, "get_device_name", Mock(return_value="NVIDIA Test GPU"))
    monkeypatch.setattr(ts_device, "_PRECISION_CONFIG", {"ok": False, "error": "forced"})
    arch = Mock(side_effect=AssertionError("cpu policy must not query CUDA arch"))
    monkeypatch.setattr(ts_device, "_cuda_arch_diagnostics", arch)
    kernel = Mock(side_effect=AssertionError("cpu policy must not run the kernel probe"))
    monkeypatch.setattr(ts_device, "_cuda_kernel_probe", kernel)

    diagnostics = ts_device.build_runtime_diagnostics()
    selection = ts_device.select_model_device("TestModel")

    assert diagnostics["selected_device"] == "cpu"
    assert diagnostics["status"] == "ok"
    assert diagnostics["fallback_reason"] is None
    assert diagnostics["cuda_precision_ok"] is False
    assert selection.selected_device == "cpu"
    assert selection.fallback_reason is None
    arch.assert_not_called()
    kernel.assert_not_called()


def test_cuda_unavailable_takes_precedence_over_precision_failure(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "auto")
    monkeypatch.setattr(ts_device.torch.cuda, "is_available", Mock(return_value=False))
    monkeypatch.setattr(ts_device, "_PRECISION_CONFIG", {"ok": False, "error": "forced"})

    assert ts_device.build_runtime_diagnostics()["fallback_reason"] == "cuda_unavailable"
    assert ts_device.select_model_device("TestModel").fallback_reason == "cuda_unavailable"


# ---------------------------------------------------------------------------
# configure_cuda_numerics(): legacy vs fp32_precision API families (stubs)
# ---------------------------------------------------------------------------


class _Recorder(SimpleNamespace):
    """SimpleNamespace that records every public attribute read and write."""

    def __init__(self, log, prefix, **attrs):
        object.__setattr__(self, "_log", log)
        object.__setattr__(self, "_prefix", prefix)
        super().__init__(**attrs)

    def __getattribute__(self, name):
        if not name.startswith("_"):
            object.__getattribute__(self, "_log").append(
                ("get", object.__getattribute__(self, "_prefix") + name)
            )
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        object.__getattribute__(self, "_log").append(
            ("set", object.__getattribute__(self, "_prefix") + name)
        )
        object.__setattr__(self, name, value)


def _new_api_torch(log):
    conv = _Recorder(log, "cudnn.conv.", fp32_precision="tf32")
    cudnn = _Recorder(log, "cudnn.", conv=conv, benchmark=True, fp32_precision="none")
    matmul = _Recorder(log, "cuda.matmul.", fp32_precision="none")
    cuda = _Recorder(log, "cuda.", matmul=matmul)
    log.clear()
    return SimpleNamespace(backends=SimpleNamespace(cudnn=cudnn, cuda=cuda))


def _legacy_api_torch(log):
    cudnn = _Recorder(log, "cudnn.", allow_tf32=True, benchmark=True)
    matmul = _Recorder(log, "cuda.matmul.", allow_tf32=True)
    cuda = _Recorder(log, "cuda.", matmul=matmul)
    log.clear()
    return SimpleNamespace(backends=SimpleNamespace(cudnn=cudnn, cuda=cuda))


def test_configure_uses_only_fp32_precision_api_on_new_torch(monkeypatch):
    monkeypatch.delenv(ts_device.TF32_OVERRIDE_ENV, raising=False)
    log = []
    fake_torch = _new_api_torch(log)
    monkeypatch.setattr(ts_device, "torch", fake_torch)

    result = ts_device.configure_cuda_numerics()
    readback = ts_device.current_fp32_precision()

    assert result == {"ok": True, "error": None}
    assert readback == {"api": "fp32_precision", "conv": "ieee", "matmul": "ieee"}
    assert fake_torch.backends.cudnn.benchmark is False
    assert ("set", "cudnn.conv.fp32_precision") in log
    assert ("set", "cuda.matmul.fp32_precision") in log
    assert ("set", "cudnn.benchmark") in log
    assert not [entry for entry in log if "allow_tf32" in entry[1]]


def test_configure_uses_only_legacy_flags_on_old_torch(monkeypatch):
    monkeypatch.delenv(ts_device.TF32_OVERRIDE_ENV, raising=False)
    log = []
    fake_torch = _legacy_api_torch(log)
    monkeypatch.setattr(ts_device, "torch", fake_torch)

    result = ts_device.configure_cuda_numerics()
    readback = ts_device.current_fp32_precision()

    assert result == {"ok": True, "error": None}
    assert readback == {"api": "allow_tf32", "conv": "ieee", "matmul": "ieee"}
    assert fake_torch.backends.cudnn.allow_tf32 is False
    assert fake_torch.backends.cuda.matmul.allow_tf32 is False
    assert fake_torch.backends.cudnn.benchmark is False
    assert not [entry for entry in log if "fp32_precision" in entry[1]]


def test_legacy_readback_reports_tf32_when_flags_allow_it(monkeypatch):
    log = []
    monkeypatch.setattr(ts_device, "torch", _legacy_api_torch(log))

    assert ts_device.current_fp32_precision() == {"api": "allow_tf32", "conv": "tf32", "matmul": "tf32"}


@pytest.mark.parametrize("value", ["1", "true", " 1 "])
def test_configure_refuses_tf32_override_without_touching_flags(monkeypatch, value):
    monkeypatch.setenv(ts_device.TF32_OVERRIDE_ENV, value)
    log = []
    monkeypatch.setattr(ts_device, "torch", _new_api_torch(log))

    result = ts_device.configure_cuda_numerics()

    assert result["ok"] is False
    assert ts_device.TF32_OVERRIDE_ENV in result["error"]
    assert not [entry for entry in log if entry[0] == "set"]


@pytest.mark.parametrize("value", ["", "0", " 0 "])
def test_configure_accepts_empty_or_zero_tf32_override(monkeypatch, value):
    monkeypatch.setenv(ts_device.TF32_OVERRIDE_ENV, value)
    monkeypatch.setattr(ts_device, "torch", _legacy_api_torch([]))

    assert ts_device.configure_cuda_numerics() == {"ok": True, "error": None}


def test_configure_records_backend_errors_instead_of_raising(monkeypatch):
    monkeypatch.delenv(ts_device.TF32_OVERRIDE_ENV, raising=False)

    class _RejectingConv:
        @property
        def fp32_precision(self):
            return "tf32"

        @fp32_precision.setter
        def fp32_precision(self, value):
            raise RuntimeError("mixed legacy and new precision settings")

    fake_torch = SimpleNamespace(
        backends=SimpleNamespace(
            cudnn=SimpleNamespace(conv=_RejectingConv(), benchmark=True),
            cuda=SimpleNamespace(matmul=SimpleNamespace(fp32_precision="none")),
        )
    )
    monkeypatch.setattr(ts_device, "torch", fake_torch)

    result = ts_device.configure_cuda_numerics()

    assert result["ok"] is False
    assert "mixed legacy and new precision settings" in result["error"]


def test_readback_errors_are_reported_not_raised(monkeypatch):
    class _Exploding:
        def __getattr__(self, name):
            raise RuntimeError(f"cannot read {name}")

    fake_torch = SimpleNamespace(backends=SimpleNamespace(cudnn=_Exploding(), cuda=_Exploding()))
    monkeypatch.setattr(ts_device, "torch", fake_torch)
    monkeypatch.setattr(ts_device, "_PRECISION_CONFIG", {"ok": True, "error": None})

    readback = ts_device.current_fp32_precision()
    ok, details = ts_device.cuda_precision_ok()

    assert readback["api"] == "unknown"
    assert readback["conv"] is None
    assert "cannot read" in readback["error"]
    assert ok is False
    assert details["matmul"] is None


def test_configure_on_installed_torch_pins_ieee_without_warnings_or_cuda_init(monkeypatch):
    monkeypatch.delenv(ts_device.TF32_OVERRIDE_ENV, raising=False)
    cuda_initialized_before = torch.cuda.is_initialized()

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        result = ts_device.configure_cuda_numerics()
        readback = ts_device.current_fp32_precision()

    assert result == {"ok": True, "error": None}
    assert readback["conv"] == "ieee"
    assert readback["matmul"] == "ieee"
    assert readback["api"] == ("fp32_precision" if ts_device._uses_fp32_precision_api() else "allow_tf32")
    assert torch.backends.cudnn.benchmark is False
    assert torch.cuda.is_initialized() is cuda_initialized_before


# ---------------------------------------------------------------------------
# TORCH_ALLOW_TF32_CUBLAS_OVERRIDE is evaluated at import: fresh subprocess
# ---------------------------------------------------------------------------


_SUBPROCESS_SCRIPT = r"""
import json
import torch
import ts_device

ok, details = ts_device.cuda_precision_ok()

# Simulate an otherwise-eligible CUDA device so only the precision policy decides.
torch.cuda.is_available = lambda: True
torch.cuda.get_device_name = lambda index=0: "Stub GPU"
ts_device._cuda_arch_diagnostics = lambda: {
    "cuda_device_capability": None, "torch_cuda_arch_list": (), "cuda_arch_supported": None,
}
ts_device._cuda_runtime_probe_detailed = lambda: (None, True)
diagnostics = ts_device.build_runtime_diagnostics("auto")

print("TASK103_RESULT=" + json.dumps({
    "ok": ok,
    "config_error": details.get("config_error"),
    "selected_device": diagnostics["selected_device"],
    "fallback_reason": diagnostics["fallback_reason"],
    "cuda_precision_ok": diagnostics["cuda_precision_ok"],
}))
"""


def _run_fresh_ts_device(override_value):
    env = os.environ.copy()
    env["TORCH_ALLOW_TF32_CUBLAS_OVERRIDE"] = override_value
    env["TOWERSCOUT_DEVICE"] = "auto"
    env["PYTHONPATH"] = os.pathsep.join(
        [str(WEBAPP_DIR)] + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else [])
    )
    completed = subprocess.run(
        [sys.executable, "-c", _SUBPROCESS_SCRIPT],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert completed.returncode == 0, completed.stderr
    result_lines = [line for line in completed.stdout.splitlines() if line.startswith("TASK103_RESULT=")]
    assert result_lines, completed.stdout + completed.stderr
    return json.loads(result_lines[-1].split("=", 1)[1])


def test_tf32_override_env_in_fresh_process_makes_cuda_ineligible():
    result = _run_fresh_ts_device("1")

    assert result["ok"] is False
    assert "TORCH_ALLOW_TF32_CUBLAS_OVERRIDE" in result["config_error"]
    assert result["cuda_precision_ok"] is False
    assert result["selected_device"] == "cpu"
    assert result["fallback_reason"] == "cuda_precision_policy_unmet"


def test_zero_tf32_override_env_in_fresh_process_keeps_cuda_eligible():
    result = _run_fresh_ts_device("0")

    assert result["ok"] is True
    assert result["config_error"] is None
    assert result["selected_device"] == "cuda"
    assert result["fallback_reason"] is None


# ---------------------------------------------------------------------------
# CPU-only torch and the DeviceSelection contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("policy", ["auto", "cpu", "cuda"])
def test_cpu_only_torch_never_raises_in_diagnostics(monkeypatch, policy):
    monkeypatch.setattr(ts_device.torch.cuda, "is_available", Mock(return_value=False))
    monkeypatch.setattr(ts_device.torch.cuda, "get_arch_list", Mock(return_value=[]))
    monkeypatch.setattr(ts_device.torch.version, "cuda", None, raising=False)

    diagnostics = ts_device.build_runtime_diagnostics(policy)

    assert diagnostics["torch_cuda_available"] is False
    assert diagnostics["cuda_device_capability"] is None
    assert diagnostics["torch_cuda_arch_list"] == []
    assert diagnostics["cuda_arch_supported"] is None
    assert diagnostics["cudnn_version"] is None
    assert diagnostics["cuda_kernel_probe_ok"] is None
    # Precision read-back is always populated (cheap; never initializes CUDA).
    assert isinstance(diagnostics["cuda_fp32_conv"], str)
    assert isinstance(diagnostics["cuda_fp32_matmul"], str)
    assert isinstance(diagnostics["cuda_precision_ok"], bool)
    if policy == "auto":
        assert diagnostics["selected_device"] == "cpu"
        assert diagnostics["fallback_reason"] == "cuda_unavailable"
    elif policy == "cpu":
        assert diagnostics["selected_device"] == "cpu"
        assert diagnostics["fallback_reason"] is None
    else:
        assert diagnostics["selected_device"] == "unavailable"
        assert diagnostics["status"] == "fatal"
        assert diagnostics["fallback_reason"] == "cuda_required_but_unavailable"


def test_cpu_only_torch_auto_selection_is_cpu(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "auto")
    monkeypatch.setattr(ts_device.torch.cuda, "is_available", Mock(return_value=False))

    selection = ts_device.select_model_device("TestModel")

    assert selection.selected_device == "cpu"
    assert selection.fallback_reason == "cuda_unavailable"
    assert selection.torch_cuda_arch_list == ()


def test_torch_cuda_diagnostic_keys_are_device_selection_fields(monkeypatch):
    _simulate_cuda(monkeypatch)
    field_names = {field.name for field in dataclasses.fields(ts_device.DeviceSelection)}

    for probe in (False, True):
        diagnostics = ts_device._torch_cuda_diagnostics(probe_cuda_runtime=probe)
        assert set(diagnostics) <= field_names
        ts_device.DeviceSelection(
            requested_policy="auto",
            configured_policy="auto",
            selected_device="cpu",
            **diagnostics,
        )


def test_device_selection_to_dict_includes_new_fields_with_defaults():
    minimal = ts_device.DeviceSelection(
        requested_policy="cpu",
        configured_policy="cpu",
        selected_device="cpu",
        torch_version="2.6.0+cpu",
        torch_cuda_build=None,
        torch_cuda_available=False,
    ).to_dict()

    for key in NEW_FIELDS:
        assert key in minimal
    assert minimal["torch_cuda_arch_list"] == []
    assert minimal["cuda_arch_supported"] is None


def test_runtime_diagnostics_report_new_fields_for_working_cuda(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "auto")
    _simulate_cuda(monkeypatch, capability=(7, 5), arch_list=CU128_ARCH_LIST, cudnn_version=90100)

    diagnostics = ts_device.build_runtime_diagnostics()

    assert diagnostics["selected_device"] == "cuda"
    assert diagnostics["fallback_reason"] is None
    assert diagnostics["cuda_device_capability"] == "sm_75"
    assert diagnostics["torch_cuda_arch_list"] == CU128_ARCH_LIST
    assert isinstance(diagnostics["torch_cuda_arch_list"], list)
    assert diagnostics["cuda_arch_supported"] is True
    assert diagnostics["cudnn_version"] == 90100
    assert diagnostics["cuda_fp32_conv"] == "ieee"
    assert diagnostics["cuda_fp32_matmul"] == "ieee"
    assert diagnostics["cuda_precision_ok"] is True
    assert diagnostics["cuda_kernel_probe_ok"] is True
    assert diagnostics["cuda_probe_error"] is None
    json.dumps(diagnostics)

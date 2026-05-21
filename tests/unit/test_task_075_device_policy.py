"""Task-075 shared ML device policy tests."""

import threading
import time
from unittest.mock import Mock

import pytest

import ts_device
import ts_runtime


class _FakeCudaProbe:
    def cpu(self):
        return self


def test_runtime_diagnostics_cpu_policy_forces_cpu(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "cpu")
    monkeypatch.setattr(ts_device.torch.cuda, "is_available", Mock(return_value=True))
    monkeypatch.setattr(ts_device.torch.cuda, "get_device_name", Mock(return_value="NVIDIA Test GPU"))
    monkeypatch.setattr(ts_device.torch.version, "cuda", "12.1", raising=False)

    diagnostics = ts_device.build_runtime_diagnostics()

    assert diagnostics["requested_policy"] == "cpu"
    assert diagnostics["selected_device"] == "cpu"
    assert diagnostics["torch_cuda_available"] is True
    assert diagnostics["cuda_device_name"] == "NVIDIA Test GPU"
    assert diagnostics["status"] == "ok"


def test_select_model_device_auto_falls_back_after_cuda_transfer_failure(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "auto")
    monkeypatch.setattr(ts_device.torch.cuda, "is_available", Mock(return_value=True))
    monkeypatch.setattr(ts_device.torch.cuda, "get_device_name", Mock(return_value="NVIDIA Test GPU"))
    monkeypatch.setattr(ts_device.torch, "zeros", Mock(return_value=_FakeCudaProbe()))

    move_to_cuda = Mock(side_effect=RuntimeError("cuda transfer failed"))
    move_to_cpu = Mock()

    selection = ts_device.select_model_device(
        "TestModel",
        move_to_cuda=move_to_cuda,
        move_to_cpu=move_to_cpu,
    )

    assert selection.requested_policy == "auto"
    assert selection.selected_device == "cpu"
    assert selection.fallback_reason == "cuda_setup_failed:RuntimeError"
    move_to_cuda.assert_called_once()
    move_to_cpu.assert_called_once()


def test_runtime_diagnostics_auto_falls_back_when_cuda_probe_fails(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "auto")
    monkeypatch.setattr(ts_device.torch.cuda, "is_available", Mock(return_value=True))
    monkeypatch.setattr(ts_device.torch.cuda, "get_device_name", Mock(return_value="NVIDIA Test GPU"))
    monkeypatch.setattr(ts_device.torch, "zeros", Mock(side_effect=RuntimeError("runtime probe failed")))

    diagnostics = ts_device.build_runtime_diagnostics()

    assert diagnostics["requested_policy"] == "auto"
    assert diagnostics["selected_device"] == "cpu"
    assert diagnostics["torch_cuda_available"] is False
    assert diagnostics["cuda_device_name"] is None
    assert diagnostics["fallback_reason"] == "cuda_unavailable"
    assert "runtime probe failed" in diagnostics["cuda_probe_error"]


def test_select_model_device_cuda_required_raises_when_unavailable(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "cuda")
    monkeypatch.setattr(ts_device.torch.cuda, "is_available", Mock(return_value=False))

    with pytest.raises(ts_device.DevicePolicyError) as error:
        ts_device.select_model_device("TestModel")

    assert "requires CUDA" in str(error.value)


def test_gpu_guard_serializes_shared_gpu_work(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_GPU_CONCURRENCY", "1")
    ts_device._reset_gpu_limiter_for_tests()

    entered = []
    first_inside = threading.Event()
    release_first = threading.Event()

    def first_worker():
        with ts_device.gpu_guard(True):
            entered.append("first")
            first_inside.set()
            release_first.wait(timeout=2)

    def second_worker():
        with ts_device.gpu_guard(True):
            entered.append("second")

    first = threading.Thread(target=first_worker)
    second = threading.Thread(target=second_worker)

    try:
        first.start()
        assert first_inside.wait(timeout=2)
        second.start()
        time.sleep(0.05)
        assert entered == ["first"]
        release_first.set()
        first.join(timeout=2)
        second.join(timeout=2)
        assert entered == ["first", "second"]
    finally:
        release_first.set()
        first.join(timeout=2)
        second.join(timeout=2)
        ts_device._reset_gpu_limiter_for_tests()


def test_readiness_payload_includes_ml_runtime_and_fails_when_cuda_required(monkeypatch):
    monkeypatch.setattr(ts_runtime, "_required_paths", lambda: {})
    monkeypatch.setattr(
        ts_runtime,
        "_config_status",
        lambda: {
            "status": "ok",
            "env_path": "test.env",
            "needs_setup": False,
            "secret_key_persisted": True,
            "providers": {
                "google": {"configured": True},
                "azure": {"configured": False},
                "default": "google",
            },
        },
    )
    monkeypatch.setattr(
        ts_runtime,
        "_asset_status",
        lambda: {
            "status": "ok",
            "manifest_version": "test-manifest",
            "assets": [],
            "missing": [],
            "corrupt": [],
            "optional_missing": [],
        },
    )
    monkeypatch.setattr(
        ts_runtime.ts_device,
        "build_runtime_diagnostics",
        lambda: {
            "status": "fatal",
            "requested_policy": "cuda",
            "configured_policy": "cuda",
            "selected_device": "unavailable",
            "torch_version": "2.2.1+cpu",
            "torch_cuda_build": None,
            "torch_cuda_available": False,
            "cuda_device_name": None,
            "fallback_reason": "cuda_required_but_unavailable",
            "cuda_probe_error": None,
        },
    )

    payload = ts_runtime.build_readiness_payload()

    assert payload["state"] == "fatal"
    assert payload["components"]["ml_runtime"]["requested_policy"] == "cuda"
    assert payload["runtime"]["device_policy"] == "cuda"
    assert payload["runtime"]["selected_device"] == "unavailable"
    assert "CPU-only PyTorch" in " ".join(payload["recovery"])
    assert "TOWERSCOUT_DEVICE=auto or cpu" in " ".join(payload["recovery"])


def test_readiness_payload_explains_cuda_runtime_probe_failure(monkeypatch):
    monkeypatch.setattr(ts_runtime, "_required_paths", lambda: {})
    monkeypatch.setattr(
        ts_runtime,
        "_config_status",
        lambda: {
            "status": "ok",
            "env_path": "test.env",
            "needs_setup": False,
            "secret_key_persisted": True,
            "providers": {
                "google": {"configured": True},
                "azure": {"configured": False},
                "default": "google",
            },
        },
    )
    monkeypatch.setattr(
        ts_runtime,
        "_asset_status",
        lambda: {
            "status": "ok",
            "manifest_version": "test-manifest",
            "assets": [],
            "missing": [],
            "corrupt": [],
            "optional_missing": [],
        },
    )
    monkeypatch.setattr(
        ts_runtime.ts_device,
        "build_runtime_diagnostics",
        lambda: {
            "status": "fatal",
            "requested_policy": "cuda",
            "configured_policy": "cuda",
            "selected_device": "unavailable",
            "torch_version": "2.2.1+cu121",
            "torch_cuda_build": "12.1",
            "torch_cuda_available": False,
            "cuda_device_name": None,
            "fallback_reason": "cuda_required_but_unavailable",
            "cuda_probe_error": "RuntimeError: driver not available",
        },
    )

    payload = ts_runtime.build_readiness_payload()

    assert payload["state"] == "fatal"
    assert "CUDA runtime probe" in " ".join(payload["recovery"])
    assert "NVIDIA container access" in " ".join(payload["recovery"])


def test_readiness_payload_fails_for_invalid_device_policy(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_DEVICE", "bananas")
    monkeypatch.setattr(ts_runtime, "_required_paths", lambda: {})
    monkeypatch.setattr(
        ts_runtime,
        "_config_status",
        lambda: {
            "status": "ok",
            "env_path": "test.env",
            "needs_setup": False,
            "secret_key_persisted": True,
            "providers": {
                "google": {"configured": True},
                "azure": {"configured": False},
                "default": "google",
            },
        },
    )
    monkeypatch.setattr(
        ts_runtime,
        "_asset_status",
        lambda: {
            "status": "ok",
            "manifest_version": "test-manifest",
            "assets": [],
            "missing": [],
            "corrupt": [],
            "optional_missing": [],
        },
    )

    payload = ts_runtime.build_readiness_payload()

    assert payload["state"] == "fatal"
    assert payload["components"]["ml_runtime"]["configured_policy"] == "bananas"
    assert payload["components"]["ml_runtime"]["fallback_reason"] == "invalid_device_policy:bananas"
    assert "Check TOWERSCOUT_DEVICE" in " ".join(payload["recovery"])

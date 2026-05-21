"""Shared ML device policy and diagnostics for TowerScout."""

from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple

import torch

from ts_logging import get_ml_logger


DEVICE_POLICY_ENV_VAR = "TOWERSCOUT_DEVICE"
GPU_CONCURRENCY_ENV_VAR = "TOWERSCOUT_GPU_CONCURRENCY"
VALID_DEVICE_POLICIES = {"auto", "cpu", "cuda"}

logger = get_ml_logger()
_gpu_limiter_lock = threading.Lock()
_gpu_limiter: Optional[threading.Semaphore] = None
_gpu_limiter_limit: Optional[int] = None


class DevicePolicyError(RuntimeError):
    """Raised when the requested ML device policy cannot be satisfied."""


@dataclass(frozen=True)
class DeviceSelection:
    """Resolved runtime device selection and non-secret diagnostic context."""

    requested_policy: str
    configured_policy: str
    selected_device: str
    torch_version: str
    torch_cuda_build: Optional[str]
    torch_cuda_available: bool
    cuda_device_name: Optional[str] = None
    fallback_reason: Optional[str] = None
    cuda_probe_error: Optional[str] = None
    status: str = "ok"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requested_policy": self.requested_policy,
            "configured_policy": self.configured_policy,
            "selected_device": self.selected_device,
            "torch_version": self.torch_version,
            "torch_cuda_build": self.torch_cuda_build,
            "torch_cuda_available": self.torch_cuda_available,
            "cuda_device_name": self.cuda_device_name,
            "fallback_reason": self.fallback_reason,
            "cuda_probe_error": self.cuda_probe_error,
            "status": self.status,
        }

    def to_metadata(self, prefix: str) -> Dict[str, Any]:
        return {
            f"{prefix}_device_policy": self.requested_policy,
            f"{prefix}_configured_device_policy": self.configured_policy,
            f"{prefix}_device": self.selected_device,
            f"{prefix}_torch_version": self.torch_version,
            f"{prefix}_torch_cuda_build": self.torch_cuda_build,
            f"{prefix}_cuda_available": self.torch_cuda_available,
            f"{prefix}_cuda_device_name": self.cuda_device_name,
            f"{prefix}_device_fallback_reason": self.fallback_reason,
        }


def _normalize_policy(policy: Optional[str] = None) -> Tuple[str, str, Optional[str]]:
    configured = policy if policy is not None else os.getenv(DEVICE_POLICY_ENV_VAR, "auto")
    configured = str(configured or "auto").strip().lower()
    if configured in {"", "default"}:
        configured = "auto"
    if configured not in VALID_DEVICE_POLICIES:
        return "auto", configured, f"invalid_device_policy:{configured}"
    return configured, configured, None


def _cuda_runtime_probe() -> Optional[str]:
    try:
        probe = torch.zeros(1, device="cuda")
        probe.cpu()
        del probe
        return None
    except Exception as exc:
        return f"{exc.__class__.__name__}: {exc}"


def _torch_cuda_diagnostics(probe_cuda_runtime: bool = False) -> Dict[str, Any]:
    cuda_available = False
    cuda_device_name = None
    cuda_probe_error = None

    try:
        cuda_available = bool(torch.cuda.is_available())
    except Exception as exc:
        cuda_probe_error = f"{exc.__class__.__name__}: {exc}"

    if cuda_available:
        try:
            cuda_device_name = torch.cuda.get_device_name(0)
        except Exception as exc:
            cuda_probe_error = f"{exc.__class__.__name__}: {exc}"
            cuda_available = False
            cuda_device_name = None

    if cuda_available and probe_cuda_runtime:
        cuda_probe_error = _cuda_runtime_probe()
        if cuda_probe_error:
            cuda_available = False
            cuda_device_name = None

    return {
        "torch_version": getattr(torch, "__version__", "unknown"),
        "torch_cuda_build": getattr(torch.version, "cuda", None),
        "torch_cuda_available": cuda_available,
        "cuda_device_name": cuda_device_name,
        "cuda_probe_error": cuda_probe_error,
    }


def build_runtime_diagnostics(policy: Optional[str] = None) -> Dict[str, Any]:
    """Return non-secret ML runtime diagnostics without loading model weights."""
    requested_policy, configured_policy, policy_error = _normalize_policy(policy)
    diagnostics = _torch_cuda_diagnostics(
        probe_cuda_runtime=(policy_error is None and requested_policy != "cpu")
    )

    selected_device = "cpu"
    fallback_reason = policy_error
    status = "ok"

    if policy_error:
        selected_device = "unavailable"
        status = "fatal"
    elif requested_policy == "cpu":
        selected_device = "cpu"
    elif diagnostics["torch_cuda_available"]:
        selected_device = "cuda"
    elif requested_policy == "cuda":
        selected_device = "unavailable"
        fallback_reason = "cuda_required_but_unavailable"
        status = "fatal"
    else:
        selected_device = "cpu"
        fallback_reason = "cuda_unavailable"

    return DeviceSelection(
        requested_policy=requested_policy,
        configured_policy=configured_policy,
        selected_device=selected_device,
        fallback_reason=fallback_reason,
        status=status,
        **diagnostics,
    ).to_dict()


def select_model_device(
    model_name: str,
    move_to_cuda: Optional[Callable[[], Any]] = None,
    move_to_cpu: Optional[Callable[[], Any]] = None,
    policy: Optional[str] = None,
) -> DeviceSelection:
    """Apply the shared device policy to a loaded model."""
    requested_policy, configured_policy, policy_error = _normalize_policy(policy)
    diagnostics = _torch_cuda_diagnostics(
        probe_cuda_runtime=(policy_error is None and requested_policy != "cpu")
    )

    if policy_error:
        raise DevicePolicyError(
            f"{DEVICE_POLICY_ENV_VAR} must be one of auto, cpu, or cuda; got {configured_policy!r}."
        )

    def cpu_selection(fallback_reason: Optional[str] = None) -> DeviceSelection:
        if move_to_cpu is not None:
            move_to_cpu()
        return DeviceSelection(
            requested_policy=requested_policy,
            configured_policy=configured_policy,
            selected_device="cpu",
            fallback_reason=fallback_reason,
            **diagnostics,
        )

    if requested_policy == "cpu":
        return cpu_selection()

    if not diagnostics["torch_cuda_available"]:
        if requested_policy == "cuda":
            details = diagnostics.get("cuda_probe_error")
            suffix = f" CUDA probe failed: {details}" if details else ""
            raise DevicePolicyError(
                f"{model_name} requires CUDA because {DEVICE_POLICY_ENV_VAR}=cuda, "
                f"but PyTorch reports CUDA is unavailable or unusable.{suffix}"
            )
        return cpu_selection("cuda_unavailable")

    try:
        if move_to_cuda is not None:
            move_to_cuda()
        return DeviceSelection(
            requested_policy=requested_policy,
            configured_policy=configured_policy,
            selected_device="cuda",
            **diagnostics,
        )
    except Exception as exc:
        if requested_policy == "cuda":
            raise DevicePolicyError(
                f"{model_name} requires CUDA because {DEVICE_POLICY_ENV_VAR}=cuda, "
                f"but CUDA setup failed: {exc}"
            ) from exc
        logger.warning("%s CUDA setup failed; falling back to CPU: %s", model_name, exc)
        return cpu_selection(f"cuda_setup_failed:{exc.__class__.__name__}")


def _env_int(name: str, default: int, minimum: int = 1) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        logger.warning("%s must be an integer; using %s", name, default)
        return default
    if parsed < minimum:
        logger.warning("%s must be >= %s; using %s", name, minimum, default)
        return default
    return parsed


def gpu_concurrency_limit(default: int = 1) -> int:
    """Return the configured GPU model concurrency limit."""
    return _env_int(GPU_CONCURRENCY_ENV_VAR, default, minimum=1)


def get_gpu_limiter(default: int = 1) -> threading.Semaphore:
    """Return the process-wide semaphore shared by GPU model stages."""
    global _gpu_limiter, _gpu_limiter_limit

    limit = gpu_concurrency_limit(default)
    with _gpu_limiter_lock:
        if _gpu_limiter is None or _gpu_limiter_limit != limit:
            _gpu_limiter = threading.Semaphore(limit)
            _gpu_limiter_limit = limit
        return _gpu_limiter


@contextmanager
def gpu_guard(enabled: bool, default: int = 1):
    """Limit concurrent GPU work across TowerScout model stages."""
    if not enabled:
        yield
        return

    limiter = get_gpu_limiter(default)
    limiter.acquire()
    try:
        yield
    finally:
        limiter.release()


def _reset_gpu_limiter_for_tests() -> None:
    global _gpu_limiter, _gpu_limiter_limit

    with _gpu_limiter_lock:
        _gpu_limiter = None
        _gpu_limiter_limit = None

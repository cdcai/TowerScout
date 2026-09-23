"""Shared ML device policy and diagnostics for TowerScout."""

from __future__ import annotations

import os
import re
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple

import torch

from ts_logging import get_ml_logger


DEVICE_POLICY_ENV_VAR = "TOWERSCOUT_DEVICE"
GPU_CONCURRENCY_ENV_VAR = "TOWERSCOUT_GPU_CONCURRENCY"
VALID_DEVICE_POLICIES = {"auto", "cpu", "cuda"}
TF32_OVERRIDE_ENV = "TORCH_ALLOW_TF32_CUBLAS_OVERRIDE"
CUDA_PRECISION_FALLBACK_REASON = "cuda_precision_policy_unmet"

logger = get_ml_logger()
_gpu_limiter_lock = threading.Lock()
_gpu_limiter: Optional[threading.Semaphore] = None
_gpu_limiter_limit: Optional[int] = None
_PRECISION_CONFIG: Dict[str, Any] = {"ok": False, "error": "not configured"}
_cuda_kernel_probe_passed = False
_ARCH_RE = re.compile(r"^(sm|compute)_(\d+)([af]?)$")
_KERNEL_PROBE_EXPECTED = 5808.0


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
    cuda_device_capability: Optional[str] = None
    torch_cuda_arch_list: Tuple[str, ...] = ()
    cuda_arch_supported: Optional[bool] = None
    cudnn_version: Optional[int] = None
    cuda_fp32_conv: Optional[str] = None
    cuda_fp32_matmul: Optional[str] = None
    cuda_precision_ok: Optional[bool] = None
    cuda_kernel_probe_ok: Optional[bool] = None

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
            "cuda_device_capability": self.cuda_device_capability,
            "torch_cuda_arch_list": list(self.torch_cuda_arch_list),
            "cuda_arch_supported": self.cuda_arch_supported,
            "cudnn_version": self.cudnn_version,
            "cuda_fp32_conv": self.cuda_fp32_conv,
            "cuda_fp32_matmul": self.cuda_fp32_matmul,
            "cuda_precision_ok": self.cuda_precision_ok,
            "cuda_kernel_probe_ok": self.cuda_kernel_probe_ok,
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


def _uses_fp32_precision_api() -> bool:
    """True when this torch exposes the fp32_precision API (torch >= 2.9)."""
    conv = getattr(torch.backends.cudnn, "conv", None)
    return conv is not None and hasattr(conv, "fp32_precision")


def current_fp32_precision() -> Dict[str, Optional[str]]:
    """Read back the effective conv/matmul FP32 precision without touching the other API.

    On torch >= 2.9 reading the legacy allow_tf32 flags emits deprecation warnings, and
    PyTorch rejects mixed legacy/new state, so only the API family in use is read.
    """
    try:
        if _uses_fp32_precision_api():
            return {
                "api": "fp32_precision",
                "conv": str(torch.backends.cudnn.conv.fp32_precision),
                "matmul": str(torch.backends.cuda.matmul.fp32_precision),
            }
        return {
            "api": "allow_tf32",
            "conv": "tf32" if torch.backends.cudnn.allow_tf32 else "ieee",
            "matmul": "tf32" if torch.backends.cuda.matmul.allow_tf32 else "ieee",
        }
    except Exception as exc:
        return {
            "api": "unknown",
            "conv": None,
            "matmul": None,
            "error": f"{exc.__class__.__name__}: {exc}",
        }


def configure_cuda_numerics() -> Dict[str, Any]:
    """Pin IEEE FP32 for cuDNN conv and cuBLAS matmul; never mix legacy and new APIs.

    Only backend flags are set, so this never initializes CUDA and is safe on CPU-only
    torch. Failures are returned (never raised) and make CUDA ineligible at selection time.
    """
    if os.getenv(TF32_OVERRIDE_ENV, "").strip() not in {"", "0"}:
        return {
            "ok": False,
            "error": f"{TF32_OVERRIDE_ENV} conflicts with TowerScout's IEEE FP32 policy",
        }
    try:
        if _uses_fp32_precision_api():
            torch.backends.cudnn.conv.fp32_precision = "ieee"
            torch.backends.cuda.matmul.fp32_precision = "ieee"
        else:
            torch.backends.cudnn.allow_tf32 = False
            torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
    except Exception as exc:
        return {"ok": False, "error": f"{exc.__class__.__name__}: {exc}"}
    return {"ok": True, "error": None}


def _configure_cuda_numerics_at_import() -> Dict[str, Any]:
    try:
        result = configure_cuda_numerics()
    except Exception as exc:  # defensive: import must never fail on numerics setup
        result = {"ok": False, "error": f"{exc.__class__.__name__}: {exc}"}
    if not result.get("ok"):
        logger.warning(
            "CUDA IEEE FP32 precision policy could not be configured; CUDA will be ineligible: %s",
            result.get("error"),
        )
    return result


_PRECISION_CONFIG = _configure_cuda_numerics_at_import()


def cuda_precision_ok() -> Tuple[bool, Dict[str, Any]]:
    """Re-read at selection time (after model imports); required for CUDA eligibility."""
    readback = current_fp32_precision()
    ok = (
        bool(_PRECISION_CONFIG.get("ok"))
        and readback.get("conv") == "ieee"
        and readback.get("matmul") == "ieee"
    )
    return ok, {**readback, "config_error": _PRECISION_CONFIG.get("error")}


def _arch_code_covers_device(arch: str, major: int, minor: int) -> Optional[bool]:
    """Return whether one torch arch-list entry can run on an sm_<major><minor> device.

    None = unknown syntax. 'a' targets run only on that exact arch; 'f' targets only
    within the same major family at or below the device minor; plain sm_XY cubins run
    within the same major at or below the device minor; plain compute_XY PTX is JIT
    forward-compatible to any newer device.
    """
    match = _ARCH_RE.match(str(arch).strip())
    if not match:
        return None
    kind, number, suffix = match.group(1), int(match.group(2)), match.group(3)
    code_major, code_minor = divmod(number, 10)
    if suffix == "a":
        return code_major == major and code_minor == minor
    if suffix == "f":
        return code_major == major and code_minor <= minor
    if kind == "sm":
        return code_major == major and code_minor <= minor
    return (code_major, code_minor) <= (major, minor)


def _aggregate_arch_support(verdicts) -> Optional[bool]:
    verdicts = list(verdicts)
    if any(verdict is True for verdict in verdicts):
        return True
    if verdicts and all(verdict is False for verdict in verdicts):
        return False
    return None


def _cuda_arch_diagnostics() -> Dict[str, Any]:
    """Advisory only: classifies failures for evidence and messages; never decides eligibility."""
    details: Dict[str, Any] = {
        "cuda_device_capability": None,
        "torch_cuda_arch_list": (),
        "cuda_arch_supported": None,
    }
    try:
        major, minor = torch.cuda.get_device_capability(0)
        major, minor = int(major), int(minor)
    except Exception:
        return details
    details["cuda_device_capability"] = f"sm_{major}{minor}"
    try:
        arch_list = tuple(str(arch) for arch in torch.cuda.get_arch_list())
    except Exception:
        arch_list = ()
    details["torch_cuda_arch_list"] = arch_list
    details["cuda_arch_supported"] = _aggregate_arch_support(
        _arch_code_covers_device(arch, major, minor) for arch in arch_list
    )
    return details


def _cudnn_version() -> Optional[int]:
    try:
        version = torch.backends.cudnn.version()
    except Exception:
        return None
    try:
        return int(version) if version is not None else None
    except (TypeError, ValueError):
        return None


def _cuda_kernel_probe() -> Optional[str]:
    """Decisive eligibility probe for cuDNN conv + cuBLAS GEMM (once per process).

    Exact small-integer results cannot distinguish FP32 from TF32; precision is enforced
    by cuda_precision_ok(), not by this probe.
    """
    global _cuda_kernel_probe_passed
    if _cuda_kernel_probe_passed:
        return None
    try:
        x = torch.ones((1, 3, 8, 8), device="cuda")
        w = torch.ones((4, 3, 3, 3), device="cuda")
        y = torch.nn.functional.conv2d(x, w, padding=1).flatten(1)
        result = (y @ torch.ones((y.shape[1], 2), device="cuda")).cpu()  # .cpu() synchronizes
        expected = torch.full((1, 2), _KERNEL_PROBE_EXPECTED)
        matches = bool(torch.equal(result, expected))
    except Exception as exc:
        return f"{exc.__class__.__name__}: {exc}"
    if not matches:
        try:
            observed = result.tolist()
        except Exception:
            observed = repr(result)
        return (
            f"RuntimeError: CUDA kernel probe returned {observed}, "
            f"expected [[{_KERNEL_PROBE_EXPECTED}, {_KERNEL_PROBE_EXPECTED}]]"
        )
    _cuda_kernel_probe_passed = True
    return None


def _cuda_runtime_probe_detailed() -> Tuple[Optional[str], Optional[bool]]:
    """Return (probe_error, kernel_probe_ok); kernel_probe_ok is None if it never ran."""
    try:
        probe = torch.zeros(1, device="cuda")
        probe.cpu()
        del probe
    except Exception as exc:
        return f"{exc.__class__.__name__}: {exc}", None

    kernel_error = _cuda_kernel_probe()
    if kernel_error:
        return f"CUDA kernel probe failed: {kernel_error}", False
    return None, True


def _cuda_runtime_probe() -> Optional[str]:
    """Allocation/copy probe followed by the decisive conv2d + matmul kernel probe."""
    return _cuda_runtime_probe_detailed()[0]


def _torch_cuda_diagnostics(probe_cuda_runtime: bool = False) -> Dict[str, Any]:
    cuda_available = False
    cuda_device_name = None
    cuda_probe_error = None
    cuda_kernel_probe_ok = None
    cudnn_version = None
    arch_details: Dict[str, Any] = {
        "cuda_device_capability": None,
        "torch_cuda_arch_list": (),
        "cuda_arch_supported": None,
    }

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
        # Advisory arch/cuDNN context is gathered before the probe so it is still
        # available to classify a failing probe. It never decides eligibility.
        arch_details = _cuda_arch_diagnostics()
        cudnn_version = _cudnn_version()
        cuda_probe_error, cuda_kernel_probe_ok = _cuda_runtime_probe_detailed()
        if cuda_probe_error:
            if arch_details.get("cuda_arch_supported") is False:
                cuda_probe_error += (
                    f" [GPU {arch_details.get('cuda_device_capability')} is not covered by this "
                    f"PyTorch build's arch list: {' '.join(arch_details.get('torch_cuda_arch_list') or ())}]"
                )
            cuda_available = False
            cuda_device_name = None

    # Precision is re-read here, at selection time (after model imports), and is cheap:
    # it only reads backend flags and never initializes CUDA.
    precision_ok, precision = cuda_precision_ok()

    return {
        "torch_version": getattr(torch, "__version__", "unknown"),
        "torch_cuda_build": getattr(torch.version, "cuda", None),
        "torch_cuda_available": cuda_available,
        "cuda_device_name": cuda_device_name,
        "cuda_probe_error": cuda_probe_error,
        "cuda_device_capability": arch_details.get("cuda_device_capability"),
        "torch_cuda_arch_list": tuple(arch_details.get("torch_cuda_arch_list") or ()),
        "cuda_arch_supported": arch_details.get("cuda_arch_supported"),
        "cudnn_version": cudnn_version,
        "cuda_fp32_conv": precision.get("conv"),
        "cuda_fp32_matmul": precision.get("matmul"),
        "cuda_precision_ok": precision_ok,
        "cuda_kernel_probe_ok": cuda_kernel_probe_ok,
    }


def _precision_failure_details(diagnostics: Dict[str, Any]) -> str:
    details = (
        f"conv={diagnostics.get('cuda_fp32_conv')}, "
        f"matmul={diagnostics.get('cuda_fp32_matmul')}"
    )
    config_error = _PRECISION_CONFIG.get("error")
    if config_error:
        details += f", configuration error: {config_error}"
    return details


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
    elif diagnostics["torch_cuda_available"] and diagnostics["cuda_precision_ok"]:
        selected_device = "cuda"
    elif diagnostics["torch_cuda_available"]:
        # CUDA works, but the IEEE FP32 precision policy could not be enforced.
        fallback_reason = CUDA_PRECISION_FALLBACK_REASON
        if requested_policy == "cuda":
            selected_device = "unavailable"
            status = "fatal"
        else:
            selected_device = "cpu"
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

    if not diagnostics["cuda_precision_ok"]:
        details = _precision_failure_details(diagnostics)
        if requested_policy == "cuda":
            raise DevicePolicyError(
                f"{model_name} requires CUDA because {DEVICE_POLICY_ENV_VAR}=cuda, "
                "but TowerScout's CUDA precision policy (IEEE FP32 for cuDNN convolution "
                f"and cuBLAS matmul) could not be enforced: {details}."
            )
        logger.warning(
            "%s CUDA precision policy (IEEE FP32) could not be enforced; falling back to CPU: %s",
            model_name,
            details,
        )
        return cpu_selection(CUDA_PRECISION_FALLBACK_REASON)

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

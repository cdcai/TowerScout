# Task-079 Follow-Up: Single GPU-Capable Package Plan

**Date**: 2026-05-20
**Status**: Proposed implementation plan, updated after PR #14 review
**Decision Direction**: Move forward with one CUDA-capable TowerScout package/image that still runs on CPU-only machines.
**Owning Follow-Up**: `TASK-075` or a dedicated GPU/CUDA release-package task after Task-079 closeout.

## Executive Summary

Task-079 fixed the largest confirmed CPU secondary-classifier bottleneck, but the latest user run still spent most model time in CPU YOLO inference. The meaningful model-side acceleration path is a CUDA-capable runtime. The preferred direction is a single release package and a single container image that install CUDA-enabled PyTorch, automatically use CUDA when available, and fall back to CPU when CUDA is not available or is explicitly disabled.

The package should not make GPU access mandatory at startup. Default launch must continue to work on CPU-only machines. GPU users should enable a packaged GPU launch overlay, and the app should report exactly why it selected CUDA or CPU.

## PR #14 Review Disposition

The external PR #14 review agrees that Task-079 is mergeable as RC reliability hardening and measurement work, but it should not be treated as the GPU package implementation. I agree with that distinction. PR #14 improves diagnostics and fallback behavior, while `TASK-075` must implement the explicit device policy, package changes, and GPU validation matrix before TowerScout claims GPU support.

Accepted reviewer refinements for `TASK-075`:

- Add a shared device resolver, tentatively `webapp/ts_device.py`, instead of implementing `TOWERSCOUT_DEVICE=auto|cpu|cuda` separately in YOLO and EfficientNet code.
- Emit one structured ML runtime record everywhere support needs it: requested policy, selected device, PyTorch version, CUDA build version, CUDA availability, GPU name, and fallback reason.
- Extend `/api/readiness` with non-secret ML runtime diagnostics that do not require model weights to load.
- Fix EfficientNet candidate batching so tensors are stacked and transferred to CUDA per chunk. `TOWERSCOUT_EN_BATCH_SIZE` must bound peak GPU transfer/forward memory, not only forward-pass chunking after all candidates have already been moved to the GPU.
- Keep `compose.yaml` CPU-safe and use `compose.gpu.yaml` only as an optional overlay.
- Add visible validation artifacts for CPU-only fallback, CUDA-wheel CPU import, GPU overlay execution, image-size impact, and fixed-fixture output parity.
- Keep mixed precision as an optional benchmark candidate, not baseline behavior.
- Do not add distributed training or `DistributedDataParallel` abstractions; TowerScout's near-term GPU work is single-process inference packaging and runtime policy.
- Treat CPU/GPU output parity as tolerance-based fixture validation, not a bit-for-bit promise across devices.

## Source Facts

- PyTorch publishes separate wheel indexes for CPU, CUDA 11.8, and CUDA 12.1 for `torch==2.2.1` and `torchvision==0.17.1`: https://pytorch.org/get-started/previous-versions/
- Docker Desktop GPU support on Windows is WSL2-only and requires an NVIDIA GPU, current Windows, NVIDIA drivers that support WSL2 GPU paravirtualization, an up-to-date WSL2 kernel, and Docker Desktop's WSL2 backend: https://docs.docker.com/desktop/features/gpu/
- Docker Compose GPU access uses device reservations and requires `capabilities: [gpu]`: https://docs.docker.com/compose/how-tos/gpu-support/
- NVIDIA Container Toolkit supports Docker, containerd, CRI-O, and Podman, and Docker needs host runtime configuration through `nvidia-ctk runtime configure --runtime=docker`: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
- NVIDIA recommends CDI for Podman GPU access; an example Podman command uses `--device nvidia.com/gpu=all --security-opt=label=disable`: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/cdi-support.html
- CUDA 12.1 GA requires at least NVIDIA driver `530.30.02` on Linux x86_64 and `531.14` on Windows x86_64 according to NVIDIA's CUDA 12.1 release notes: https://docs.nvidia.com/cuda/archive/12.1.0/cuda-toolkit-release-notes/

## Recommended Package Strategy

Use one image built with the CUDA 12.1 PyTorch wheel index:

```text
PYTORCH_INDEX_URL=https://download.pytorch.org/whl/cu121
torch==2.2.1
torchvision==0.17.1
```

Keep the current CPU-compatible application code path. CUDA-enabled PyTorch wheels should still run CPU tensors when no CUDA device is visible, so the image can remain one package for both machine types. The image will be larger than the CPU-only image, and that size increase must be measured before RC adoption.

Do not put GPU reservations in the default `compose.yaml`, because Compose GPU reservations can fail deployment on machines without GPU support. Instead, ship one image and one release package with:

- `compose.yaml`: default CPU-safe launch, same image.
- `compose.gpu.yaml`: optional Docker GPU overlay for NVIDIA-enabled hosts.
- launcher support: `scripts/launch.ps1 -Gpu auto|on|off`, defaulting to `auto` only after validation; until then default `off` or conservative `auto` that never blocks CPU fallback.

## Runtime Behavior

Add an explicit runtime device policy:

```text
TOWERSCOUT_DEVICE=auto|cpu|cuda
```

- `auto`: current behavior, use CUDA only if PyTorch is CUDA-built, CUDA is available, and model transfer succeeds.
- `cpu`: force CPU even if CUDA is visible. This is important for support cases where a GPU driver is present but unstable.
- `cuda`: require CUDA for detection and fail readiness/detection with actionable guidance if CUDA is not available.

For RC safety, default to `auto` in the container image and allow the launcher to set `cpu` or `auto` depending on the selected GPU mode.

Implement this policy through a shared resolver so YOLO, EfficientNet, readiness, and support diagnostics cannot drift. The resolver should return a small immutable record with at least:

- requested policy: `auto`, `cpu`, or `cuda`
- selected device: `cpu` or `cuda`
- fallback reason, if any
- PyTorch version and CUDA build version
- `torch.cuda.is_available()` result
- lightweight CUDA tensor probe result when CUDA is requested or auto-selected
- CUDA device name when available

Required diagnostics in logs, performance JSON, and readiness/support status:

- `torch.__version__`
- `torch.version.cuda`
- `torch.cuda.is_available()`
- lightweight CUDA tensor allocation/copy probe result
- selected model device: `cpu` or `cuda`
- CUDA device name when available
- fallback reason when CUDA is visible but unusable
- YOLO batch size and EfficientNet batch size
- GPU memory allocation/peak when CUDA is used
- container engine and whether GPU overlay was requested

Task-079 has already started this by adding model-side CUDA build/device metadata to detection performance records.

## Docker And Compose Implementation Plan

1. Keep `Dockerfile` support for `PYTORCH_INDEX_URL`, but make release publication choose an explicit PyTorch flavor (`cpu` or `cuda121`) and publish flavor-specific tags so the pinned image digest is not ambiguous.
2. Build a proof image with:

```powershell
docker build `
  --build-arg PYTORCH_INDEX_URL=https://download.pytorch.org/whl/cu121 `
  -t towerscout:cuda121-poc .
```

3. Validate import and CPU fallback on a non-GPU machine:

```powershell
docker run --rm towerscout:cuda121-poc python - <<'PY'
import torch
print(torch.__version__)
print(torch.version.cuda)
print(torch.cuda.is_available())
PY
```

4. Add `compose.gpu.yaml` for Docker-compatible engines:

```yaml
services:
  towerscout:
    environment:
      TOWERSCOUT_DEVICE: auto
      NVIDIA_VISIBLE_DEVICES: all
      NVIDIA_DRIVER_CAPABILITIES: compute,utility
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

5. Add launcher mode:

```powershell
scripts\launch.ps1 -Gpu off
scripts\launch.ps1 -Gpu on
scripts\launch.ps1 -Gpu auto
```

Initial behavior should be conservative:

- `off`: use only `compose.yaml`, set `TOWERSCOUT_DEVICE=cpu`.
- `on`: include `compose.gpu.yaml`, set `TOWERSCOUT_DEVICE=cuda`, and fail readiness if CUDA is unavailable.
- `auto`: set `TOWERSCOUT_DEVICE=auto`, but include `compose.gpu.yaml` only when `TOWERSCOUT_GPU_AUTO_OVERLAY=1` has been set in the shell or `.env` after Docker GPU validation on that workstation. If validation is absent, start CPU-safe and emit guidance rather than failing launch.

6. Package `compose.gpu.yaml` in `scripts/package-release.ps1` once validated.
7. Add `.env.example` knobs:

```text
TOWERSCOUT_DEVICE=auto
TOWERSCOUT_GPU_MODE=off
TOWERSCOUT_GPU_AUTO_OVERLAY=0
TOWERSCOUT_GPU_CONCURRENCY=1
TOWERSCOUT_YOLO_CPU_BATCH_SIZE=
TOWERSCOUT_YOLO_CUDA_BATCH_SIZE=8
TOWERSCOUT_EN_BATCH_SIZE=8
```

## Podman Position

Podman GPU support should be treated as separate validation inside the same package, not as a blocker for the first CUDA-capable Docker path.

Reason:

- NVIDIA recommends CDI for Podman GPU access.
- The current Windows Podman release path depends on a Compose provider.
- `podman run --device nvidia.com/gpu=all --security-opt=label=disable ...` is documented, but support through `podman compose` or `podman-compose` must be proven with TowerScout's launcher and named volumes.

Plan:

1. Validate Docker Desktop GPU path first because Docker documents Compose GPU reservations directly.
2. Validate Podman CDI direct run separately.
3. Validate Podman Compose provider behavior only after direct Podman CDI works.
4. If Podman Compose GPU support is unreliable, keep Podman supported for CPU and document GPU support as Docker-first until a Podman GPU launch path is proven.

## Application Code Implementation Plan

1. Add shared `TOWERSCOUT_DEVICE=auto|cpu|cuda` parsing and device selection in `webapp/ts_device.py`.
2. Make CUDA setup failure behavior explicit:
   - `auto`: log fallback reason and continue CPU.
   - `cpu`: do not attempt CUDA.
   - `cuda`: raise a structured model/runtime error with support guidance.
3. Reuse the shared resolver from `ts_yolov5.py`, `ts_en.py`, readiness, and future support diagnostics.
4. Record ML runtime metadata in performance logs and readiness:
   - PyTorch version
   - CUDA build version
   - CUDA availability
   - selected device
   - GPU name
   - requested device policy
   - fallback reason
   - batch sizes
5. Add a lightweight runtime diagnostics endpoint or extend `/api/readiness` with an `ml_runtime` component that does not force model weights to load.
6. Fix EfficientNet CUDA batching so candidate tensors are stacked and transferred per `TOWERSCOUT_EN_BATCH_SIZE` chunk. This must make the batch size a real peak-memory bound.
7. Make GPU concurrency explicit with one process-wide limiter shared by YOLO and EfficientNet. Prefer a conservative default for GPU model access and add a configurable `TOWERSCOUT_GPU_CONCURRENCY` only after GPU memory behavior is measured.
8. Keep mixed precision behind an explicit benchmark/feature flag, such as `TOWERSCOUT_AMP=0|1`, and do not enable it by default until fixed-fixture parity and timing evidence support it.
9. Keep model weights, thresholds, detection JSON fields, export behavior, and asset bundle layout unchanged.
10. Add tests for:
   - CPU forced mode.
   - CUDA required but unavailable.
   - CUDA visible but model transfer fails in `auto` and falls back to CPU.
   - Runtime metadata serialization.
   - Readiness/runtime diagnostics with CPU-only PyTorch and CUDA-built PyTorch.
   - EfficientNet chunking that bounds CUDA transfer size by `TOWERSCOUT_EN_BATCH_SIZE`.
   - Shared GPU concurrency behavior across primary and secondary model stages.

## Release Package Changes

Update these files during implementation:

- `Dockerfile`: `PYTORCH_INDEX_URL` and `TOWERSCOUT_PYTORCH_FLAVOR` build args, with publication choosing the release flavor explicitly.
- `compose.yaml`: keep CPU-safe default; add `TOWERSCOUT_DEVICE`.
- `compose.gpu.yaml`: new optional GPU overlay.
- `.env.example`: GPU mode and device policy knobs.
- `scripts/launch.ps1`: `-Gpu` mode and overlay selection.
- `scripts/lib/TowerScoutCompose.ps1`: Compose file selection support if needed.
- `scripts/package-release.ps1`: include `compose.gpu.yaml`.
- `docs/oci-quick-start.md`: CPU-safe default plus GPU enablement.
- `docs/oci-runtime-contract.md`: GPU runtime contract and diagnostics.
- `docs/towerscout-user-guide.md`: user-facing GPU note and troubleshooting.
- `release-manifest.v1.json` or generated package manifest: record CPU versus CUDA-capable image posture and write the chosen PyTorch flavor into the release control package.
- `SBOM.txt` reference: call out CUDA-enabled PyTorch dependency set.

## Validation Matrix

Minimum validation before this can be called RC-ready:

| Environment | Required Result |
| --- | --- |
| CPU-only Windows 11 AMD64, Docker or Podman CPU path | App starts, setup works, readiness works, bounded detection runs on CPU with CUDA-built PyTorch installed. |
| NVIDIA Windows 11 AMD64, Docker Desktop WSL2 | `docker run --gpus all ... nvidia-smi` works, GPU overlay starts TowerScout, `torch.cuda.is_available()` is true in container, YOLO/EfficientNet select CUDA, bounded detection is faster than CPU baseline. |
| NVIDIA Windows 11 AMD64, Docker GPU overlay disabled | Same image starts CPU-only and does not require GPU devices. |
| NVIDIA Windows 11 AMD64, `TOWERSCOUT_DEVICE=cpu` | App forces CPU even when CUDA is visible. |
| NVIDIA Windows 11 AMD64, `TOWERSCOUT_DEVICE=cuda` with GPU unavailable | App fails readiness/detection with actionable guidance, not a generic stack trace. |
| Podman CPU path | Existing CPU package behavior remains intact. |
| Podman GPU path | Validate separately with CDI; do not claim support until proven. |
| Fixed-fixture output parity | CPU, forced CPU on CUDA wheel, and CUDA overlay outputs match within documented score/selection tolerances. |
| EfficientNet high-candidate GPU memory fixture | Peak GPU memory scales with configured batch size, not total candidate count. |
| Concurrent GPU detection requests | Requests serialize or throttle safely without GPU out-of-memory; logs explain queueing/concurrency behavior. |

Performance evidence to capture:

- 8-tile CPU run on CUDA-capable image with GPU disabled.
- Same AOI on GPU overlay.
- YOLO inference seconds, secondary inference seconds, total workflow seconds.
- Geocoding excluded or held constant when comparing model speed.
- Image size delta between CPU-only and CUDA-capable image.
- Fixed-fixture `torch.profiler` output for CPU and CUDA model phases.
- Focused GPU trace, such as Nsight Systems, only around the model-critical section if CUDA bottlenecks remain unclear.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| CUDA-capable image is much larger | Slower download and worse first install experience | Measure image size before RC adoption; document trade-off; retain CPU-only image only if size becomes unacceptable. |
| Default Compose GPU reservation breaks CPU users | Release-blocking startup failure | Keep `compose.yaml` CPU-safe; use optional GPU overlay only. |
| CUDA wheel import fails on CPU-only hosts | Release-blocking | Validate CPU-only import and bounded detection before changing release default. |
| Host GPU exists but container cannot see it | User confusion | Add launcher diagnostics and readiness/runtime metadata; document Docker Desktop WSL2 and driver requirements. |
| Podman GPU support differs from Docker | Support complexity | Treat Podman GPU as separate validation; keep Podman CPU support intact. |
| CUDA setup fails after `torch.cuda.is_available()` | Detection failure or crash | Keep `auto` CPU fallback, add a lightweight CUDA runtime probe before readiness/model selection trusts CUDA, and use `cuda` required mode only when explicitly requested. |
| Larger GPU memory use causes out-of-memory on small GPUs | Detection failure | Keep configurable CUDA batch sizes and fallback guidance. |
| EfficientNet batch size does not bound transfer memory | GPU out-of-memory despite small configured batch size | Stack and transfer EfficientNet tensors per chunk before advertising CUDA support. |
| Concurrent requests oversubscribe one GPU | Runtime failures under multi-client use | Add explicit GPU concurrency policy and conservative default serialization. |
| Mixed precision changes scores or selected detections | Silent result drift | Keep AMP opt-in until fixed-fixture parity and tolerance evidence are captured. |

## Proposed Execution Phases

### Phase 1 - Runtime Policy And GPU Memory Safety

- Add shared `ts_device.py` policy resolver and unit tests.
- Extend readiness/performance metadata with requested policy, selected device, CUDA build, CUDA availability, device name, and fallback reason.
- Fix EfficientNet per-chunk CUDA transfer so `TOWERSCOUT_EN_BATCH_SIZE` bounds peak transfer memory.
- Add explicit shared GPU concurrency configuration and safe defaults.

### Phase 2 - Proof Build

- Build `towerscout:cuda121-poc` using the CUDA 12.1 PyTorch wheel index.
- Validate import, readiness, and CPU fallback on the current CPU-only host.
- Measure image size and startup time delta.

### Phase 3 - Docker GPU Overlay

- Add `compose.gpu.yaml`.
- Add launcher `-Gpu` handling.
- Validate Docker Desktop WSL2 GPU path on an NVIDIA host.

### Phase 4 - Docs And Release Package

- Update package docs, runtime contract, quick start, user guide, `.env.example`, and package script.
- Record CUDA-capable posture in release metadata and SBOM reference.

### Phase 5 - Podman GPU Validation

- Validate direct Podman CDI.
- Validate Podman Compose provider behavior only if direct CDI works.
- Document Podman GPU status honestly.

### Phase 6 - RC Decision Gate

Accept single GPU-capable package only if:

- CPU-only machines still run from the same image.
- GPU machines show material model speedup.
- Default launch does not require GPU.
- Support diagnostics clearly explain CPU fallback.
- Image size and download impact are acceptable for RC users.
- Fixed-fixture parity evidence shows no unacceptable selection drift.
- GPU memory and concurrency behavior are bounded and supportable.

If any gate fails, keep the Task-079 CPU fixes and defer the CUDA-capable package to a later RC while preserving the implementation plan.

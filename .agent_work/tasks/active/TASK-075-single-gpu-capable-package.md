# TASK-075: Single GPU-Capable Package Implementation

**Status**: IN_PROGRESS - PR review hardening implemented; NVIDIA host validation pending
**Priority**: CRITICAL
**Type**: C (Runtime Policy / Hardware Compatibility / Release Packaging)
**Estimated Effort**: 1-3 days (8-24 hours), split by validation availability
**Target Sprint**: Sprint 06 V1 RC1

## Objective

Implement the reviewed single GPU-capable TowerScout package direction while preserving a CPU-safe default release path.

This task starts from the Task-079 plan and PR #14 review disposition. It must not claim GPU support until CPU fallback, Docker GPU overlay behavior, fixed-fixture output parity, image-size impact, and support diagnostics are validated.

## Requirements (EARS Notation)

**R-075-001**: WHEN TowerScout selects an ML runtime device, THE SYSTEM SHALL use one shared `TOWERSCOUT_DEVICE=auto|cpu|cuda` policy resolver for YOLO, EfficientNet, readiness, and support diagnostics.

**R-075-002**: WHEN `TOWERSCOUT_DEVICE=cpu`, THE SYSTEM SHALL force CPU execution even if PyTorch reports CUDA availability.

**R-075-003**: WHEN `TOWERSCOUT_DEVICE=auto`, THE SYSTEM SHALL use CUDA only when PyTorch is CUDA-built, CUDA is available, a lightweight CUDA runtime probe succeeds, and model transfer succeeds; otherwise it shall fall back to CPU with a structured fallback reason.

**R-075-004**: WHEN `TOWERSCOUT_DEVICE=cuda`, THE SYSTEM SHALL fail readiness or detection with actionable guidance if CUDA is unavailable or model transfer fails.

**R-075-005**: WHEN readiness is requested, THE SYSTEM SHALL expose non-secret ML runtime diagnostics, including CUDA runtime-probe status, without requiring model weights to load.

**R-075-006**: WHEN EfficientNet reviews detection candidates on CUDA, THE SYSTEM SHALL stack and transfer candidate tensors per configured batch chunk so `TOWERSCOUT_EN_BATCH_SIZE` bounds peak GPU transfer and forward-pass memory.

**R-075-007**: WHEN TowerScout runs on a shared GPU, THE SYSTEM SHALL enforce one explicit process-wide GPU concurrency policy across YOLO and EfficientNet with a conservative default.

**R-075-008**: WHEN Task-075 changes device selection or batching, THE SYSTEM SHALL preserve model weights, thresholds, detection JSON fields, export behavior, asset paths, and release asset bundle layout.

**R-075-009**: WHEN building the release image, THE PROJECT SHALL keep the default launch path CPU-safe until a CUDA-capable image proves CPU fallback on a non-GPU host.

**R-075-010**: WHEN enabling GPU launch, THE PROJECT SHALL use an optional GPU overlay instead of adding GPU reservations to default `compose.yaml`.

**R-075-011**: WHEN claiming GPU support, THE PROJECT SHALL capture fixed-fixture CPU/GPU parity, model-phase timing, image-size impact, Docker Desktop WSL2 GPU validation, and any Podman GPU status limitations.

**R-075-012**: WHEN publishing a release image, THE PROJECT SHALL explicitly record whether the image was built with CPU or CUDA-capable PyTorch wheels.

**R-075-013**: WHEN publishing CPU and CUDA-capable images, THE PROJECT SHALL use flavor-specific tags so one flavor cannot overwrite or obscure the other.

## Acceptance Criteria

- [x] Shared `webapp/ts_device.py` resolver implemented with `auto`, `cpu`, and `cuda` policies.
- [x] YOLO uses the shared device resolver and records requested policy, selected device, CUDA build, CUDA availability, device name, and fallback reason.
- [x] EfficientNet uses the shared device resolver and records requested policy, selected device, CUDA build, CUDA availability, device name, and fallback reason.
- [x] `/api/readiness` includes an `ml_runtime` component without loading model weights.
- [x] `TOWERSCOUT_DEVICE=cpu` forces CPU in YOLO and EfficientNet.
- [x] `TOWERSCOUT_DEVICE=cuda` fails predictably when CUDA is unavailable.
- [x] `TOWERSCOUT_DEVICE=auto` falls back to CPU when CUDA setup fails and records the fallback reason.
- [x] EfficientNet candidate tensors are stacked and transferred per batch chunk on CUDA.
- [x] GPU concurrency has an explicit process-wide configuration and conservative default shared by YOLO and EfficientNet.
- [x] Focused Python tests cover device policy, readiness diagnostics, CUDA-required failure, CUDA runtime-probe fallback, auto fallback, EfficientNet chunking, shared GPU concurrency, and launcher GPU mode behavior.
- [x] CUDA 12.1 PyTorch proof image builds or its blocker is documented.
- [x] CUDA-capable image CPU fallback is validated on a non-GPU host or explicitly deferred.
- [x] Optional `compose.gpu.yaml` is added only after proof-image readiness.
- [x] Launcher `-Gpu off|auto|on` behavior is added only after overlay behavior is understood.
- [x] Container publication has an explicit CPU/CUDA PyTorch wheel flavor selection.
- [x] Container publication and release package metadata use CPU/CUDA flavor-specific tags and metadata.
- [x] Task-071 and Task-066 receive updated documentation and validation handoff notes.

## Dependencies

- `TASK-079`: accepted reliability fixes, timing instrumentation, secondary-classifier batching, and single GPU-capable package plan.
- `TASK-051`: prior CUDA audit context.
- `TASK-065`: release packaging and runtime support baseline.
- `TASK-071`: user-facing release documentation.
- `TASK-066`: release candidate validation gate.

## Implementation Plan

### Phase 1 - Runtime Policy And GPU Memory Safety

1. Add `webapp/ts_device.py` with the shared device policy resolver and diagnostics record.
2. Extend readiness with `ml_runtime` diagnostics that do not load model weights.
3. Update YOLO to use the shared policy, preserve CPU defaults, and report policy/fallback metadata.
4. Update EfficientNet to use the shared policy, preserve CPU defaults, and report policy/fallback metadata.
5. Fix EfficientNet per-chunk CUDA transfer so `TOWERSCOUT_EN_BATCH_SIZE` bounds peak GPU memory.
6. Add explicit GPU concurrency configuration with conservative defaults.
7. Add focused unit tests and run the existing Task-079 ML/reliability tests.

### Phase 2 - CUDA-Capable Proof Image

1. Build a proof image with `PYTORCH_INDEX_URL=https://download.pytorch.org/whl/cu121`.
2. Validate PyTorch import, readiness, and bounded detection on a non-GPU host.
3. Measure image size and startup impact.
4. Decide whether to make CUDA 12.1 wheels the release build default.

### Phase 3 - GPU Overlay And Launcher

1. Add optional `compose.gpu.yaml` with NVIDIA device reservations.
2. Keep default `compose.yaml` CPU-safe.
3. Add launcher `-Gpu off|auto|on` handling, with `auto` CPU-safe unless an explicit Docker GPU overlay validation override is set in the shell or `.env`.
4. Package the GPU overlay only after local behavior is understood.

### Phase 4 - GPU Host Validation

1. Validate Docker Desktop WSL2 GPU prerequisites on an NVIDIA Windows host.
2. Run a fixed-fixture CPU/GPU parity and timing comparison with geocoding held constant.
3. Capture profiler evidence if model bottlenecks remain unclear.
4. Validate Podman CDI separately before documenting Podman GPU support.

### Phase 5 - Release Documentation And Gate

1. Update release package docs and troubleshooting.
2. Update release manifest/SBOM references for CUDA-capable PyTorch if adopted.
3. Hand final validation requirements to `TASK-066`.

## Known Risks

- CUDA-capable PyTorch wheels may materially increase image size and first-install friction.
- CUDA wheels must be proven to import and run CPU tensors on CPU-only hosts before they become the release default.
- Docker Desktop GPU and Podman GPU have different host/runtime requirements.
- EfficientNet candidate volume can cause GPU memory pressure unless transfer is chunked.
- Concurrent detections can oversubscribe one GPU unless concurrency is explicit.
- Mixed precision may improve speed but can shift outputs; keep it opt-in until benchmarked.

## Implementation Log

### 2026-05-21 - PR Review GPU Supportability Fixes Implemented
**Objective**: Address PR #15 reviewer feedback before NVIDIA host validation.
**Context**: The review identified three RC1 supportability gaps: `-Gpu auto` could request the GPU overlay from a host-side `nvidia-smi` signal even when Docker GPU pass-through was not validated, readiness treated `torch.cuda.is_available()` as sufficient, and GPU concurrency only guarded YOLO while EfficientNet could still overlap GPU work.
**Decision**: Keep GPU support in RC1, but harden it behind CPU-safe defaults. `-Gpu auto` now uses the GPU overlay only when `TOWERSCOUT_GPU_AUTO_OVERLAY=1` is set in the shell or `.env` after workstation-specific Docker GPU validation. Readiness/model selection now performs a lightweight CUDA tensor probe for `auto`/`cuda`. YOLO and EfficientNet now share one process-wide GPU limiter.
**Execution**: Updated `webapp/ts_device.py`, `webapp/ts_yolov5.py`, and `webapp/ts_en.py`; updated `scripts/lib/TowerScoutCompose.ps1`; added launcher/device-policy tests; updated `.env.example`, OCI docs, and the Task-079 GPU package plan.
**Output**: CPU-safe default and `-Gpu auto` are less likely to fail on CPU-only or partially configured GPU hosts. Required GPU mode remains explicit through `-Gpu on` / `TOWERSCOUT_DEVICE=cuda`.
**Validation**: Passed `.venv\Scripts\python.exe -m py_compile webapp\ts_device.py webapp\ts_en.py webapp\ts_yolov5.py webapp\ts_runtime.py tests\unit\test_task_075_device_policy.py tests\unit\test_task_075_launcher_gpu.py`; passed focused tests with `.venv\Scripts\python.exe -m pytest tests\unit\test_task_075_device_policy.py tests\unit\test_task_075_launcher_gpu.py tests\unit\test_ts_en_classifier.py tests\unit\test_yolov5_secondary_metrics.py tests\unit\test_runtime_contract.py tests\unit\test_release_package_script.py tests\unit\test_container_publish_workflow.py -q -p no:cacheprovider`; passed full unit tests with `.venv\Scripts\python.exe -m pytest tests\unit -q -p no:cacheprovider`; passed PowerShell parser validation for `scripts\lib\TowerScoutCompose.ps1`; passed `docker compose -f compose.yaml -f compose.gpu.yaml config`; passed `.agent_work` validation and `git diff --check`.
**Next**: Push the PR update for reviewer follow-up, then validate `-Gpu on` and `TOWERSCOUT_GPU_AUTO_OVERLAY=1` on an NVIDIA Docker Desktop WSL2 host.

### 2026-05-21 - Updated PR Review Follow-Up Fixes Implemented
**Objective**: Address the updated PR #15 review's remaining RC1 supportability fixes before moving to Task-071/Task-066.
**Context**: The reviewer approved the CPU-safe GPU direction but identified four code-level gaps to close: the container publish workflow did not explicitly select CPU versus CUDA PyTorch wheels, readiness guidance did not distinguish CPU-wheel images from Docker GPU pass-through issues, YOLO released the shared GPU guard before result tensor CPU conversion, and EfficientNet loaded checkpoints directly to the selected device.
**Decision**: Keep the Dockerfile default CPU-wheel for local safety, but add an explicit publish/build flavor path for `cpu` versus `cuda121`. Improve readiness recovery messages based on whether CUDA was required with a CPU-only PyTorch build, a CUDA runtime probe failure, or a generic CUDA access failure. Keep YOLO's shared GPU guard through tensor extraction/conversion and load EfficientNet checkpoints on CPU before device selection.
**Execution**: Updated `.github/workflows/container-publish.yml`, `Dockerfile`, `compose.build.yaml`, `scripts/lib/TowerScoutCompose.ps1`, `.env.example`, `webapp/ts_runtime.py`, `webapp/towerscout.py`, `webapp/ts_yolov5.py`, `webapp/ts_en.py`, OCI docs, and focused unit tests.
**Output**: Release publication now has an explicit PyTorch flavor choice and records `pytorch_flavor` in workflow summary output. Runtime readiness gives more actionable CUDA-required guidance. YOLO and EfficientNet now hold GPU memory/concurrency boundaries more conservatively.
**Validation**: Passed `.venv\Scripts\python.exe -m py_compile webapp\ts_runtime.py webapp\ts_device.py webapp\ts_yolov5.py webapp\ts_en.py webapp\towerscout.py tests\unit\test_task_075_device_policy.py tests\unit\test_yolov5_secondary_metrics.py tests\unit\test_ts_en_classifier.py tests\unit\test_container_publish_workflow.py tests\unit\test_task_075_launcher_gpu.py`; passed focused tests with `.venv\Scripts\python.exe -m pytest tests\unit\test_task_075_device_policy.py tests\unit\test_task_075_launcher_gpu.py tests\unit\test_ts_en_classifier.py tests\unit\test_yolov5_secondary_metrics.py tests\unit\test_runtime_contract.py tests\unit\test_release_package_script.py tests\unit\test_container_publish_workflow.py -q -p no:cacheprovider`; passed full unit suite with `.venv\Scripts\python.exe -m pytest tests\unit -q -p no:cacheprovider`; passed PowerShell parser and GPU build-helper validation; passed `docker compose -f compose.yaml -f compose.build.yaml config`; passed `docker compose -f compose.yaml -f compose.gpu.yaml config`; passed container-publish workflow summary inspection; passed `.agent_work` validation and `git diff --check`.
**Next**: Push the PR update, then either merge after review or proceed to NVIDIA-host validation before making GPU-supported release claims.

### 2026-05-21 - Release Flavor Metadata And Tagging Tightened
**Objective**: Resolve the remaining updated PR #15 review concern about ambiguous CPU/CUDA image flavor metadata and tags.
**Context**: The reviewer accepted the runtime fixes but recommended keeping PR #15 in draft until release image flavor tagging and control-package metadata are unambiguous.
**Decision**: Keep one publish workflow but make image tags flavor-specific. Add `-PytorchFlavor cpu|cuda121` support to release package generation and record the selected flavor in `IMAGE.txt`, staged `.env.example`, and `release-manifest.v1.json`.
**Execution**: Updated `.github/workflows/container-publish.yml`, `scripts/package-release.ps1`, `release-manifest.v1.json`, `.env.example`, OCI docs, Task-079 plan notes, and release/package workflow tests.
**Output**: A base workflow tag such as `v0.1.0-rc1` now publishes `v0.1.0-rc1-cpu` or `v0.1.0-rc1-cuda121`, and `push_latest` publishes `latest-cpu` or `latest-cuda121`. Generated release packages now carry the selected PyTorch flavor alongside the pinned digest.
**Validation**: Passed `.venv\Scripts\python.exe -m py_compile tests\unit\test_release_package_script.py tests\unit\test_container_publish_workflow.py tests\unit\release_manifest_contract.py`; passed focused release tests with `.venv\Scripts\python.exe -m pytest tests\unit\test_release_package_script.py tests\unit\test_release_manifest_schema.py tests\unit\test_container_publish_workflow.py -q -p no:cacheprovider`; passed PowerShell parser validation for `scripts\package-release.ps1` and `scripts\lib\TowerScoutCompose.ps1`; passed container publish workflow summary inspection; passed full unit suite with `.venv\Scripts\python.exe -m pytest tests\unit -q -p no:cacheprovider`; passed release-manifest contract inspection with expected template warnings for blank image/source fields; passed `docker compose -f compose.yaml -f compose.build.yaml config`; passed `.agent_work` validation and `git diff --check`.
**Next**: Push the PR update, then update the PR body wording manually because the GitHub connector token is expired.

### 2026-05-20 - Launcher Smoke Retried After Port 5000 Was Cleared
**Objective**: Validate the updated launcher path after the active browser/app session was closed.
**Context**: The browser was closed, but Docker still had the TowerScout Compose service running on port `5000`. To test startup behavior rather than only readiness against an already-running container, the service was stopped with Compose and relaunched through `scripts/launch.ps1`.
**Decision**: Validate the CPU-safe default launcher path first, then validate non-GPU-host `-Gpu auto`, and finally rebuild `towerscout:local` from the current working tree with `-Build -Gpu off`.
**Execution**: Ran `scripts\launch.ps1 -Engine docker -Port 5000 -NoBrowser -TimeoutSeconds 180`; ran `scripts\launch.ps1 -Engine docker -Port 5000 -Gpu auto -NoBrowser -TimeoutSeconds 180`; ran `scripts\launch.ps1 -Engine docker -Port 5000 -Gpu off -Build -NoBrowser -TimeoutSeconds 240`; queried container readiness and checked for `/app/webapp/ts_device.py`.
**Output**: Default `-Gpu off` launcher recreated the service, forced CPU mode, reached readiness `ready`, and skipped browser launch. `-Gpu auto` started without the GPU overlay when no explicit overlay validation override was present and reached readiness `ready`. The rebuilt container includes `ts_device.py`; readiness reports `ml_runtime.requested_policy=cpu`, `selected_device=cpu`, `torch_version=2.2.1+cpu`, and `state=ready`.
**Validation**: Launcher smoke passed for default CPU-safe mode, non-GPU-host `auto`, and current-working-tree rebuild. The explicit `-Gpu on` path still requires NVIDIA Docker Desktop WSL2 host validation and was not run on this CPU-only host.
**Next**: Leave the app available at `http://localhost:5000` for local inspection, then validate `-Gpu auto`/`-Gpu on` on an NVIDIA host before claiming GPU support.

### 2026-05-20 - Phase 3 GPU Overlay And Launcher Implemented
**Objective**: Add the optional GPU launch path without changing the CPU-safe default release launch.
**Context**: Docker's current Compose GPU documentation uses service device reservations under `deploy.resources.reservations.devices` with required `capabilities: [gpu]`. A GPU reservation can fail container creation on hosts without GPU support, so the default Compose file must not request GPU devices.
**Decision**: Add `compose.gpu.yaml` as an optional Docker overlay. Keep `start.bat` / `scripts/launch.ps1` defaulting to `-Gpu off`, which sets `TOWERSCOUT_DEVICE=cpu` and does not include the overlay. Implement `-Gpu auto` conservatively: it sets `TOWERSCOUT_DEVICE=auto` and starts without the overlay unless `TOWERSCOUT_GPU_AUTO_OVERLAY=1` is set in the shell or `.env` after workstation-specific Docker GPU validation; otherwise CPU fallback can work. Implement `-Gpu on` as the explicit require-GPU path using the overlay and `TOWERSCOUT_DEVICE=cuda`.
**Execution**: Added `compose.gpu.yaml`; added `TOWERSCOUT_DEVICE`, `TOWERSCOUT_GPU_CONCURRENCY`, and GPU mode notes to `.env.example`; updated `scripts/lib/TowerScoutCompose.ps1`, `scripts/launch.ps1`, `scripts/start.ps1`, `scripts/import-assets.ps1`, and `scripts/import-tls-ca.ps1` to carry GPU mode consistently; added `compose.gpu.yaml` to release package staging; updated OCI quick-start/runtime-contract notes; and extended the release-package test to assert the GPU overlay is packaged.
**Output**: Release package can now carry a CPU-safe default launch plus an optional Docker GPU overlay. Podman remains CPU-supported only until a separate CDI GPU validation proves otherwise.
**Validation**: PowerShell parser check passed for modified scripts; helper validation confirmed `auto` does not request the overlay on this non-GPU host, `on` does request it, and GPU modes map to `cpu|auto|cuda`; `docker compose -f compose.yaml -f compose.gpu.yaml config` passed; focused tests passed with `.venv\Scripts\python.exe -m pytest tests\unit\test_task_075_device_policy.py tests\unit\test_ts_en_classifier.py tests\unit\test_yolov5_secondary_metrics.py tests\unit\test_runtime_contract.py tests\unit\test_release_package_script.py tests\unit\test_container_publish_workflow.py -q -p no:cacheprovider`; full unit suite passed with `.venv\Scripts\python.exe -m pytest tests\unit -q -p no:cacheprovider`; `.agent_work` validation and `git diff --check` passed.
**Next**: Validate on an NVIDIA Docker Desktop WSL2 host with `-Gpu auto` and `-Gpu on`, then run fixed-fixture CPU/GPU output parity and timing before making GPU support claims in Task-071/Task-066.

### 2026-05-20 - Phase 2 CUDA Proof Images Validated Locally
**Objective**: Validate whether the current Dockerfile can produce a CUDA-capable TowerScout image that still behaves predictably on a CPU-only Docker Desktop host.
**Context**: Docker Desktop was started after the initial daemon blocker. The local engine reports Docker Server `29.4.1`, Linux `x86_64`.
**Decision**: Keep the Dockerfile default CPU-safe for now, but treat the CUDA 12.1 proof image as viable for the single GPU-capable package direction. Do not add `compose.gpu.yaml`, launcher `-Gpu`, or support claims until optional overlay behavior and NVIDIA host validation are completed.
**Execution**: Built `towerscout:cuda121-poc` with `PYTORCH_INDEX_URL=https://download.pytorch.org/whl/cu121`; built current-branch `towerscout:task075-cpu-poc` with the default CPU PyTorch index; ran policy diagnostics and app readiness in both images on this non-GPU host.
**Output**: CUDA proof image imports `torch==2.2.1+cu121` with CUDA build `12.1`; `TOWERSCOUT_DEVICE=auto` selects CPU with `fallback_reason=cuda_unavailable`; `TOWERSCOUT_DEVICE=cpu` selects CPU; `TOWERSCOUT_DEVICE=cuda` returns readiness `state=fatal` with recovery guidance. CPU proof image imports `torch==2.2.1+cpu` and reports CPU fallback through the same diagnostics path. Local image sizes are `7.11GB` for `towerscout:cuda121-poc` and `2.8GB` for `towerscout:task075-cpu-poc`, so the CUDA wheel path adds about `4.31GB`.
**Validation**: `docker build --build-arg PYTORCH_INDEX_URL=https://download.pytorch.org/whl/cu121 -t towerscout:cuda121-poc .` passed; `docker build -t towerscout:task075-cpu-poc .` passed; `docker run --rm` diagnostics passed for CUDA `auto`, `cpu`, and required `cuda`; app readiness in the CUDA image returned `setup_required` for `auto` with CPU fallback and HTTP 503/`state=fatal` for required CUDA; app readiness in the CPU image returned `setup_required` with CPU-only PyTorch diagnostics.
**Next**: Decide whether the size tradeoff is acceptable for the RC package, then implement optional `compose.gpu.yaml` and launcher `-Gpu off|auto|on` behavior behind CPU-safe defaults.

### 2026-05-20 - Phase 2 CUDA Proof Image Blocked Locally
**Objective**: Start CUDA 12.1 proof-image validation after Phase 1 runtime-policy implementation.
**Context**: The proof image needs Docker Desktop or another Docker-compatible daemon to build `towerscout:cuda121-poc` with `PYTORCH_INDEX_URL=https://download.pytorch.org/whl/cu121`.
**Decision**: Do not change Dockerfile defaults, Compose GPU overlays, launcher behavior, release docs, or support claims until a proof image can be built and validated.
**Execution**: Checked local Docker availability.
**Output**: Docker CLI is installed, but the Docker Desktop Linux engine is not running: `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`.
**Validation**: `docker --version` passed; `docker info --format '{{json .ServerVersion}}'` failed because the daemon is unavailable.
**Next**: Start Docker Desktop or provide another Docker-compatible daemon, then build the CUDA 12.1 proof image and validate CPU fallback.

### 2026-05-20 - Phase 1 Runtime Policy And GPU Memory Safety Implemented
**Objective**: Implement the reviewer-approved Phase 1 runtime policy and GPU memory-safety prerequisites before package proof-image work.
**Context**: Task-079 and the PR #14 review identified that implicit `torch.cuda.is_available()` checks were insufficient for a release support contract. EfficientNet also needed per-chunk CUDA tensor transfer so the configured batch size bounds peak GPU memory.
**Decision**: Add a shared device-policy resolver and wire YOLO, EfficientNet, and readiness through it. Keep Docker and launcher packaging unchanged until runtime policy is proven by tests.
**Execution**: Added `webapp/ts_device.py`; updated YOLO and EfficientNet to use `TOWERSCOUT_DEVICE=auto|cpu|cuda`; added readiness `ml_runtime` diagnostics; added `TOWERSCOUT_GPU_CONCURRENCY` for conservative GPU serialization; changed EfficientNet to stack and transfer candidate tensors per chunk; and added focused Task-075 tests.
**Output**: Runtime policy and GPU memory-safety code is ready for CUDA proof-image validation. Default behavior remains CPU-safe on this host.
**Validation**: Passed `.venv\Scripts\python.exe -m py_compile webapp\ts_device.py webapp\ts_runtime.py webapp\ts_en.py webapp\ts_yolov5.py`; passed `.venv\Scripts\python.exe -m pytest tests\unit\test_task_075_device_policy.py tests\unit\test_ts_en_classifier.py tests\unit\test_yolov5_secondary_metrics.py tests\unit\test_runtime_contract.py tests\unit\test_task_079_reliability.py tests\unit\test_geocoding.py -q -p no:cacheprovider`; passed `.venv\Scripts\python.exe -m pytest tests\unit -q -p no:cacheprovider`; passed `python .agent_work\scripts\validate_agent_work.py`; passed `git diff --check`.
**Next**: Start Phase 2 by building the CUDA 12.1 proof image or document the local runtime blocker.

### 2026-05-20 - Task Started
**Objective**: Start Task-075 from the merged Task-079 / PR #14 baseline.
**Context**: PR #14 merged the RC reliability hardening and reviewed single GPU-capable package plan. The next release-blocking decision is whether TowerScout can safely ship one CUDA-capable image/package that still works on CPU-only machines.
**Decision**: Begin with Phase 1 runtime policy and GPU memory safety before Docker image or launcher changes.
**Execution**: Created this active task file and prepared current/backlog synchronization.
**Output**: Task ready for Phase 1 implementation.
**Validation**: Passed `.agent_work` validation after task synchronization.
**Next**: Implement shared device policy, readiness diagnostics, EfficientNet chunk transfer, and focused tests.

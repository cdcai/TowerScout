# TASK-079: RC1 Reliability Fixes And Performance Instrumentation

**Status**: COMPLETED - Phase 3 CPU optimization validated; single GPU-capable package plan handed to TASK-075
**Priority**: CRITICAL
**Type**: C (Release-Critical Reliability / Detection Workflow Hardening)
**Estimated Effort**: Phase 1: 1-2 days (8-16 hours); Phase 2A/2B: 0.5-1 day investigation; Phase 3 follow-up depends on benchmark and GPU/CUDA evidence
**Target Sprint**: Sprint 06 V1 RC1

## Objective

Fix or harden the release-critical issues found during pre-RC application testing: detected-tower addresses not reliably appearing in the right-hand panel, Azure drawing tools sometimes rejecting completed valid shapes, and model detection duration regressing on CPU-only runs.

This task protects the V1 RC1 package path by prioritizing correctness, supportable diagnostics, and low-regression changes before end-user package documentation and clean-machine release-candidate validation are finalized.

## Requirements (EARS Notation)

**R-079-001**: WHEN detected cooling towers are returned to the frontend, THE SYSTEM SHALL provide a displayable address value for every class-0 detection, using provider reverse-geocoded addresses when available and a clear coordinate fallback when provider geocoding is unavailable.

**R-079-002**: IF provider requests cannot run because `REQUESTS_CA_BUNDLE` or `SSL_CERT_FILE` points to a missing or unusable certificate bundle, THEN THE SYSTEM SHALL detect that configuration problem before burning through repeated provider calls or geocoding rate-limit budget.

**R-079-003**: WHEN geocoding cache clustering is enabled, THE SYSTEM SHALL reuse cached results for nearby detections within the configured clustering radius, including detections whose coordinates fall across adjacent internal cache grid cells.

**R-079-004**: WHEN a user completes a valid Azure Maps drawing shape, THE SYSTEM SHALL recognize the shape as a valid pending boundary for search and manual tower workflows.

**R-079-005**: IF an Azure Maps drawing event produces an unsupported, empty, malformed, or invalid shape, THEN THE SYSTEM SHALL reject that shape without retaining it as a valid pending boundary.

**R-079-006**: WHEN Azure search and manual tower save paths inspect pending drawn boundaries, THE SYSTEM SHALL use a consistent shape source so completed shapes are not lost when `newShapes` and the Azure drawing source differ.

**R-079-007**: WHEN a detection request runs, THE SYSTEM SHALL record enough model-phase timing detail to distinguish tile image loading, YOLO inference, result conversion/filtering, secondary classifier work, device selection, and batch size.

**R-079-008**: WHILE preparing V1 RC1, THE SYSTEM SHALL NOT change model weights, asset bundle layout, detection result JSON fields, exported dataset semantics, provider-key storage, health/readiness contracts, or the normal packaged container TLS posture unless explicitly approved.

**R-079-009**: IF Phase 2 performance benchmarks do not show a material, low-risk optimization opportunity, THEN THE PROJECT SHALL defer model optimization to `TASK-026` or another follow-up instead of changing detection behavior before RC1.

**R-079-010**: WHEN `/api/geocode/reverse` or manual tower reverse geocoding hits provider, TLS, rate-limit, or geocoding failures, THE SYSTEM SHALL return or store structured coordinate fallback data instead of a generic internal error for recoverable provider problems.

**R-079-011**: WHEN fallback address text is displayed, THE SYSTEM SHALL use one canonical coordinate display format so right-panel grouping, sorting, export review, and tests do not depend on inconsistent fallback strings.

**R-079-012**: WHEN provider-supplied or fallback address text is rendered in the detection list, THE SYSTEM SHALL escape the address text or insert it through text-node APIs before it reaches the DOM.

**R-079-013**: WHEN validating completed Azure drawing shapes, THE SYSTEM SHALL require at least one extractable polygon, while preserving no-custom-boundary flows where an empty polygon collection is valid because the viewport or another boundary type is used.

**R-079-014**: WHEN model performance metrics are recorded, THE SYSTEM SHALL include additive timing for model initialization and secondary-classifier loading in addition to inference-phase timings.

**R-079-015**: WHEN this task adds logs or support diagnostics, THE SYSTEM SHALL NOT log provider keys, key previews, request headers, `.env` contents, or full provider URLs containing query strings.

**R-079-016**: WHEN Phase 2A evaluates secondary-classifier performance, THE PROJECT SHALL benchmark fixed local inputs so EfficientNet crop, transform, batching, and forward-pass costs can be compared without provider download, geocoding, or map workflow variability.

**R-079-017**: WHEN Phase 2A evaluates a secondary-classifier optimization candidate, THE PROJECT SHALL prove that class-0 detection selection and secondary-classifier outputs are unchanged or explicitly dispositioned before any Phase 3 implementation.

**R-079-018**: WHEN Phase 2B evaluates GPU/CUDA support, THE PROJECT SHALL distinguish application-level CUDA auto-detection from release-package requirements such as CUDA-enabled PyTorch wheels, NVIDIA driver support, container GPU exposure, image size, and Docker/Podman compatibility.

**R-079-019**: IF GPU/CUDA support cannot be packaged, validated, and documented safely for the local end-user RC path, THEN THE PROJECT SHALL keep RC1 CPU-first and route GPU enablement to `TASK-075` or another explicit follow-up.

**R-079-020**: WHEN detections have been classified as outside the requested AOI, THE SYSTEM SHALL NOT spend reverse-geocoding provider calls on those outside detections during automatic detection address attachment.

**R-079-021**: WHEN automatic detection address attachment skips outside-AOI class-0 detections, THE SYSTEM SHALL still attach a canonical coordinate fallback so the detection remains displayable and export-reviewable.

**R-079-022**: WHEN geocoding performance metrics are recorded, THE SYSTEM SHALL distinguish eligible detections, skipped detections, cache hits, cache misses, provider-call attempts, cache lookup time, provider request time, and cache store time.

**R-079-023**: WHEN estimating detection duration, THE SYSTEM SHALL prefer recent observed workflow timing for the selected provider and fall back to a conservative CPU-safe default rather than the obsolete `0.3s/tile` estimate.

**R-079-024**: WHEN YOLO runs on CPU, THE SYSTEM SHALL support a configurable CPU batch size override without changing the default CPU behavior.

**R-079-025**: WHEN planning the single GPU-capable package direction, THE PROJECT SHALL document package, runtime, Compose, Docker Desktop, Podman, driver, diagnostics, fallback, testing, and release-manifest implications before implementation.

## Acceptance Criteria

- [x] Provider TLS bundle validation is shared by provider-key validation, detection reverse geocoding, manual tower reverse geocoding, and in-scope synchronous provider requests that use `requests`.
- [x] Missing or unusable TLS CA bundle paths produce actionable logs/support guidance and do not cause repeated blind reverse-geocode attempts.
- [x] Detection address attachment always returns provider addresses or canonical coordinate fallback text for class-0 detections.
- [x] `/api/geocode/reverse` returns coordinate fallback JSON for provider, TLS, rate-limit, and geocoding failures while preserving 400 responses for malformed coordinates or invalid input.
- [x] Manual tower reverse geocoding stores provider addresses or canonical coordinate fallback data for recoverable provider failures.
- [x] Fallback address text uses one canonical format: `Coordinates: <lat>, <lng>`.
- [x] Address strings rendered in the detection list are HTML-escaped or inserted through `textContent`.
- [x] Geocoding cache clustering returns nearby cached addresses across adjacent grid-cell boundaries while preserving provider isolation.
- [x] Geocoding neighbor-bucket lookup is implemented for file cache and Redis, or Redis neighbor behavior is explicitly deferred for RC1.
- [x] Azure completed polygon and rectangle shapes validate successfully when they contain usable polygon coordinates.
- [x] Azure unsupported, empty, malformed, or self-intersecting shapes fail validation and are not retained as valid pending shapes.
- [x] Empty polygon collections are invalid only in completed drawn-shape validation contexts; no-custom-boundary viewport fallback behavior is not regressed.
- [x] Azure search and manual tower save paths use the same pending-shape retrieval behavior.
- [x] Azure manual tower save works when the completed shape exists in the Azure drawing source but not `newShapes`.
- [x] Model performance logs include additive phase timing details, model initialization timing, and secondary-classifier load timing without breaking existing performance summaries or setup/settings performance displays.
- [x] Older performance log rows remain readable when new timing keys are absent.
- [x] New logs and support messages do not expose provider keys, key previews, request headers, `.env` contents, or full provider request URLs.
- [x] Phase 1 does not alter model thresholds, model assets, detection output schema, export/restore behavior, or release asset/import contracts.
- [x] Phase 2A benchmark evidence isolates secondary-classifier crop/transform/forward-pass cost using fixed local inputs.
- [x] Phase 2A optimization candidates preserve selected detections and secondary-classifier semantics, or their differences are explicitly rejected/deferred.
- [x] Phase 2B documents why `torch.cuda.is_available()` is necessary but not sufficient for RC GPU support when the packaged runtime uses CPU-only PyTorch wheels.
- [x] Phase 2B documents CPU-only, optional GPU-image/overlay, and single universal image trade-offs for local end-user deployment.
- [x] Phase 2B documents Docker Desktop WSL2, Docker Compose GPU reservation, NVIDIA Container Toolkit, and Podman compatibility constraints before any GPU/CUDA implementation decision.
- [x] Phase 3 batches EfficientNet review-band candidates while preserving model weights, confidence thresholds, selected detections, and detection result JSON fields.
- [x] Phase 3 records secondary-classifier candidate count, batch count, batch size, device, subphase timings, and seconds per candidate for future slow-run diagnostics.
- [x] Follow-up slow-run hardening skips provider reverse-geocoding for outside-AOI detections while preserving coordinate fallback text.
- [x] Follow-up slow-run hardening records geocoding cache/provider timing and count metadata.
- [x] Follow-up slow-run hardening replaces stale `0.3s/tile` estimates with recent-history estimates and a conservative fallback.
- [x] Follow-up slow-run hardening adds a configurable YOLO CPU batch-size override and CUDA build/device metadata.
- [x] Single GPU-capable package implementation plan is documented with official source references and RC validation gates.
- [x] Frontend bundle is rebuilt after JavaScript source changes.
- [x] Targeted Python and JavaScript tests cover geocoding, Azure drawing validation, address rendering expectations, performance metric serialization, secondary-classifier batching, and secondary metrics.
- [x] `TASK-071` and `TASK-066` have clear handoff notes for any changed troubleshooting, support evidence, or RC validation expectations.

## Dependencies

- `TASK-065`: release packaging and runtime support follow-through.
- `TASK-069`: AGPL-compliant YOLO release posture and compliance payload.
- `TASK-071`: end-user release package documentation, which should incorporate this task's troubleshooting and validation outcomes.
- `TASK-066`: release candidate validation gate, which should run the corrected bounded detection and Azure drawing smoke paths.
- `TASK-072`: release asset bundle contract, which must remain unchanged by this task.
- Existing provider/detection stabilization from `TASK-053` and runtime responsiveness baseline from `TASK-064`.
- Branch context: the reviewer evaluated the GitHub `docs/task-071-end-user-release-docs` branch, where `TASK-071` is already completed. In this local checkout, `TASK-071` may still appear `NOT_STARTED` until that branch is integrated; either way, this task's docs/support findings must be handed to `TASK-071` docs and `TASK-066` validation.

## Implementation Plan

### Phase 1 - RC1 Correctness And Measurement

1. Add a shared provider-request TLS preflight so missing, non-file, or unusable configured CA bundle paths are caught before in-scope provider calls.
2. Reuse the shared TLS preflight in provider-key validation, detection reverse geocoding, manual tower reverse geocoding, `/api/geocode/reverse`, and in-scope synchronous provider request helpers that use `requests`.
3. Keep the packaged container CA behavior unchanged: the current Compose defaults may point `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` at the container system CA bundle, support may override them with an imported combined local CA bundle, and no custom CA bundle is required for normal use.
4. Preserve TLS verification by default and keep `TOWERSCOUT_ALLOW_INSECURE_TLS=1` as a last-resort support workaround only.
5. Standardize coordinate fallback data for detection address attachment, `/api/geocode/reverse`, and manual tower geocoding. Use `Coordinates: <lat>, <lng>` for display text and carry failure type through `address_provider`, structured route JSON, or sanitized logs.
6. Escape provider-supplied and fallback address text before detection-list rendering, preferably through DOM `textContent`; if the current string builder remains, use a small tested HTML-escape helper.
7. Fix geocoding cache clustering by searching neighboring provider-scoped cache buckets within the configured radius rather than relying on one rounded bucket key.
8. Implement neighbor-bucket lookup for both file and Redis cache backends when practical. If Redis support is not completed in Phase 1, document the Redis-specific behavior as an explicit RC1 deferral.
9. Choose cache hits deterministically when multiple nearby entries match: nearest distance within radius first, then higher confidence, then newest timestamp. Preserve the existing rule that unsuccessful or fallback addresses are not cached.
10. Normalize Azure drawing-complete payload handling so direct shapes and event-wrapped shapes are validated through one extraction path.
11. Make polygon collection validation context-aware, using a require-non-empty mode for completed drawn shapes while preserving empty collections in no-custom-boundary viewport fallback contexts.
12. Validate Azure shapes before retaining them in `newShapes`, or remove invalid shapes immediately after validation failure; for RC1, prefer reject-and-redraw over editable invalid-shape recovery.
13. Align Azure search and manual tower save logic around the same pending-shape source, including the case where the Azure drawing source has a completed shape but `newShapes` is empty.
14. Add additive model-phase timing fields under existing performance metrics without changing public detection results. Include model initialization, device selection, tile image loading, YOLO inference, secondary-classifier loading, secondary-classifier inference, result conversion/filtering, boundary filtering, dedupe, batch size, tile count, and secondary-classifier enabled/disabled metadata where feasible.
15. Keep new logs sanitized: include provider name, env var name, configured CA path, failure class, and support action only; do not log keys, key previews, headers, `.env` contents, or full provider URLs.
16. Rebuild the frontend bundle and run targeted validation.

### Phase 2A - Secondary-Classifier Processing Speed Investigation

1. Build or reuse a fixed local benchmark path that compares model-phase timing without provider download, geocoding, or map workflow variability.
2. Use the Phase 1 timing evidence as the baseline: the 6-tile Azure smoke showed `model_secondary_classifier_inference=69.48s` of `actual_model_time_seconds=85.10s` on CPU.
3. Break EfficientNet secondary-classifier time into crop extraction, image transform, tensor creation/stacking, forward-pass time, and result attachment.
4. Test candidate optimizations in benchmark form first: batching EfficientNet candidate crops, storing device selection once per classifier instance, avoiding repeated CUDA availability checks, reducing unnecessary image copies, and confirming CPU batch-size/threading behavior.
5. Preserve model weights, confidence thresholds, class-0 detection selection semantics, detection JSON fields, and export behavior while benchmarking.
6. Require identical selected detections and secondary-classifier values within an explicitly chosen tolerance before any Phase 3 implementation is considered.
7. Document before/after timing, per-candidate cost, candidate count, CPU thread count, selected batch size, and residual risks.

### Phase 2B - GPU/CUDA RC Feasibility Investigation

1. Confirm the current application behavior: YOLO and EfficientNet already attempt to use CUDA when `torch.cuda.is_available()` returns true, but the current RC container installs CPU-only PyTorch wheels.
2. Research and document the package/runtime requirements for CUDA-enabled PyTorch 2.2.1, including CPU, CUDA 11.8, and CUDA 12.1 wheel indexes.
3. Compare three local deployment strategies:
   - Keep RC1 CPU-only as the default supported path.
   - Add an optional GPU image or GPU overlay that installs CUDA-enabled PyTorch and requires explicit GPU container launch support.
   - Build one universal image with CUDA-enabled PyTorch and CPU fallback, accepting larger image size and more complex support/testing.
4. Validate the container implications for Docker Desktop on Windows with WSL2 GPU support, Docker Compose GPU device reservations, NVIDIA Container Toolkit, and Podman/CDI support.
5. Define the minimum runtime diagnostics needed before any GPU/CUDA enablement: PyTorch build CUDA version, `torch.cuda.is_available()`, selected device, GPU name when available, wheel/runtime type, and CPU fallback reason.
6. Treat GPU enablement as a Phase 3 decision, not a Phase 2 implementation. If the packaging matrix is not reliable for RC1, keep CPU-only guidance and move GPU enablement to `TASK-075`.

### Phase 3 - Conditional Optimization

1. Implement only the optimization candidates that Phase 2 proves are material and low risk.
2. Prefer the secondary-classifier batching path for RC1 only if Phase 2A shows a material speedup with stable detection outputs.
3. Implement GPU/CUDA support for RC1 only if Phase 2B proves the package, runtime, docs, and validation matrix are supportable for local end-user deployment.
4. Keep RC1 CPU-first if GPU/CUDA support is not proven safe; route unselected optimization ideas to `TASK-026` and unselected GPU/CUDA work to `TASK-075`.

## Release And Packaging Constraints

- Do not change the V1 RC1 asset ZIP layout, asset manifest contract, import helper source-root behavior, or named container volume layout.
- Do not require end users to edit source-tree files or use local source-run instructions for the normal package path.
- Do not make insecure TLS the documented release posture.
- Do not require runtime hash verification during routine first launch.
- Keep Podman and Docker package behavior equivalent for these fixes.
- Keep `/api/health` and `/api/readiness` contracts compatible with launchers and support scripts.
- Do not introduce mandatory custom CA-bundle configuration. Keep current valid container trust defaults and only fail early when configured CA bundle paths are missing or unusable.
- Do not change no-custom-boundary viewport fallback behavior while tightening completed Azure drawing validation.
- Do not switch the RC1 package to CUDA-enabled PyTorch or a GPU-required launch path unless Phase 2B proves CPU fallback, Docker/Podman compatibility, image-size impact, and support documentation are acceptable.
- Do not assume host GPU presence is enough for package GPU support; the package must also include CUDA-enabled PyTorch and the container host must expose NVIDIA devices to the running container.

## Validation Plan

1. Run focused Python unit tests for shared TLS handling, geocache clustering, config TLS behavior, `/api/geocode/reverse` fallback behavior, manual tower geocoding fallback behavior, and performance metric serialization.
2. Run focused JavaScript tests for Azure drawing validation, pending-shape source parity, detection list address rendering, and address escaping.
3. Run frontend contract tests and rebuild validation:
   - `node webapp/build.js`
   - `node tests/frontend/test_global_contract.js`
   - `node tests/frontend/test_debug_logging_contract.js`
   - `node tests/integration/test_task_064_provider_state_manager.js`
4. Run existing geocoding/config unit tests:
   - `.venv\Scripts\python.exe -m pytest tests/unit/test_geocoding.py tests/unit/test_config.py -q -p no:cacheprovider`
5. Run broader unit tests before handoff:
   - `.venv\Scripts\python.exe -m pytest tests/unit -q -p no:cacheprovider`
6. Re-run or repair targeted geocoding integration tests so they assert meaningful address/fallback behavior rather than passing on false positives.
7. Verify old performance log rows remain readable when new timing keys are missing.
8. Capture one bounded detection smoke with address display/fallback behavior, Azure completed drawing behavior, and performance phase timings for `TASK-066` evidence.
9. For Phase 2A, run a deterministic secondary-classifier benchmark using fixed local inputs and compare candidate timing against the Phase 1 CPU baseline.
10. For Phase 2A, compare current and candidate secondary-classifier outputs for selected-detection stability before implementation.
11. For Phase 2B, document GPU/CUDA package feasibility from official PyTorch, Docker, and NVIDIA sources before making any RC1 enablement decision.

## Known Findings Driving This Task

- Recent local geocoding failures were caused by Requests using a stale/missing CA bundle path, which made both Azure and Google reverse-geocoding fail before addresses could populate the right-hand panel.
- The packaged container path already defaults to the container CA bundle; the fix must avoid weakening that release posture while improving local/source-run and support diagnostics.
- Current geocoding cache clustering can miss nearby coordinates that fall across adjacent internal cache buckets.
- Azure shape validation can treat unextractable completed shapes as an empty valid collection, and invalid shapes can remain in `newShapes`.
- Phase 1 timing now separates enough model phases to show the first live CPU smoke bottleneck: secondary-classifier inference dominated the 6-tile Azure run (`69.48s` of `85.10s` model time), while YOLO inference was `15.40s`.
- Current YOLO and EfficientNet code already uses CUDA if PyTorch reports CUDA availability, but the current RC package path installs CPU-only PyTorch wheels, so host GPU presence alone is not enough for GPU acceleration.
- Official PyTorch 2.2.1 wheels are split by CPU, CUDA 11.8, and CUDA 12.1 indexes; choosing a CUDA runtime is a packaging decision, not only an application-code decision.
- Docker Desktop GPU support on Windows depends on WSL2 backend, NVIDIA GPU/driver support, and GPU exposure to the container. Docker Compose and Podman have separate GPU device/runtime configuration requirements that must be validated before RC1 support language changes.
- Phase 2A fixed-fixture benchmarks reproduced the same 6-tile Azure smoke inputs with 41 raw detections and 9 secondary-classifier candidates, but measured `model_secondary_classifier_inference` at about `13.8s` rather than the live smoke's `69.48s`. The live result is therefore a serious outlier to explain, not a stable per-run baseline.
- CPU EfficientNet batching is a real but moderate optimization candidate: batch size 8 preserved secondary scores within `1e-6` and improved 9-candidate secondary forward time by about `15-17%`; repeated 36-candidate scaling improved total secondary time by about `20%`.
- CPU thread-count testing did not show a reason to lower the current 10-thread default on this host; 10 threads was fastest among 4, 6, 8, and 10 for the 9-candidate fixture.
- Local Phase 2B checks found the current `.venv` uses `torch==2.2.1+cpu`, `torchvision==0.17.1+cpu`, `torch.cuda.is_available()==False`, no host `nvidia-smi` command was available, Docker CLI was installed but the Docker daemon was not running, and the Podman machine connection was not usable. This host cannot validate GPU acceleration without additional runtime setup.
- A reviewer assessed this plan against the newer GitHub `docs/task-071-end-user-release-docs` branch where `TASK-071` is complete; this local checkout may lag that branch, so implementation handoff should check the current branch state before updating docs.

## Phase 2 Research References

- PyTorch CUDA availability API: https://docs.pytorch.org/docs/2.12/generated/torch.cuda.is_available.html
- PyTorch 2.2.1 CPU/CUDA wheel indexes: https://pytorch.org/get-started/previous-versions/
- Docker Compose GPU device reservations: https://docs.docker.com/compose/how-tos/gpu-support/
- Docker Desktop GPU support on Windows/WSL2: https://docs.docker.com/desktop/features/gpu/
- NVIDIA Container Toolkit overview: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/index.html

---

## Implementation Log

### 2026-05-20 - PR 14 Review Disposition Added To GPU Package Plan
**Objective**: Incorporate the external PR #14 review into the Task-079 single GPU-capable package plan before using it to scope `TASK-075`.
**Context**: The reviewer agreed PR #14 is appropriate RC reliability and measurement work, but emphasized that it is not the GPU package implementation. The strongest gaps were explicit device policy, shared readiness diagnostics, EfficientNet GPU memory-bound chunking, visible validation artifacts, and avoiding unrelated distributed-training abstractions.
**Decision**: Accept the review refinements. `TASK-075` should begin with a shared `TOWERSCOUT_DEVICE=auto|cpu|cuda` resolver, per-chunk EfficientNet CUDA transfer, non-loading readiness diagnostics, explicit GPU concurrency policy, fixed-fixture parity checks, and Docker-first GPU validation while keeping default Compose CPU-safe.
**Execution**: Updated `.agent_work/tasks/completed/TASK-079/task-079-single-gpu-capable-package-plan.md` with a PR #14 review disposition, revised application-code priorities, expanded validation matrix, added risks/mitigations, and reordered implementation phases so runtime policy and GPU memory safety come before proof packaging.
**Output**: `TASK-075` handoff now reflects the reviewer-approved implementation entry criteria rather than treating implicit `torch.cuda.is_available()` behavior as sufficient.
**Validation**: Passed `python .agent_work\scripts\validate_agent_work.py` and `git diff --check`.
**Next**: Commit the plan update and push it to PR #14.

### 2026-05-20 - Post-Completion Slow-Run Follow-Up And GPU Package Plan
**Objective**: Address the remaining slowdown observed after the Phase 3 secondary-classifier optimization and capture the accepted single GPU-capable package direction before moving into `TASK-075`.
**Context**: The May 20 user run showed Task-079's secondary-classifier batching was applied, but the remaining 65.76s workflow was dominated by CPU YOLO inference (`23.25s`), sequential Azure reverse geocoding (`19.89s`), and cold YOLO initialization (`13.80s`). The detection estimate still reported `~2.4s` for an 8-tile run because it used the stale `0.3s/tile` fallback.
**Decision**: Keep this follow-up RC-safe: do not change model weights, thresholds, detection result JSON fields, package asset layout, or default Compose GPU requirements. Reduce unnecessary geocoding work for outside-AOI detections, improve diagnostics, make estimates history-based, expose YOLO CPU batch sizing as configuration, and document the single GPU-capable package as a separate implementation plan.
**Execution**: Added provider-alias normalization and legacy alias reads for geocoding cache keys; changed automatic detection address attachment to reverse-geocode only class-0 detections inside the AOI while assigning coordinate fallback to outside class-0 detections; recorded geocoding cache/provider timing and count metadata; changed performance estimates to use recent provider-specific workflow seconds per tile with conservative fallback and cold-model overhead; added `TOWERSCOUT_YOLO_CPU_BATCH_SIZE` / `TOWERSCOUT_YOLO_CUDA_BATCH_SIZE`; recorded PyTorch CUDA build/device metadata; added focused regression tests; and created `.agent_work/tasks/completed/TASK-079/task-079-single-gpu-capable-package-plan.md`.
**Output**: Expected next bounded run behavior is fewer automatic geocoding provider calls when detections fall outside the drawn AOI, clearer performance JSON metadata for geocoding bottlenecks, a more realistic estimate before detection, and a supportable path to evaluate a single CUDA-capable image with CPU fallback.
**Validation**: Passed `.venv\Scripts\python.exe -m pytest tests\unit\test_geocoding.py tests\unit\test_task_079_reliability.py tests\unit\test_yolov5_secondary_metrics.py -q -p no:cacheprovider`, `.venv\Scripts\python.exe -m py_compile webapp\towerscout.py webapp\ts_geocache.py webapp\ts_performance.py webapp\ts_yolov5.py`, and `python .agent_work\scripts\validate_agent_work.py`.
**Next**: Use the single GPU-capable package plan as the starting point for `TASK-075`.

### 2026-05-19 - Phase 3 CPU Secondary-Classifier Optimization Implemented
**Objective**: Implement the accepted low-risk Phase 3 CPU optimization and diagnostics without changing model weights, thresholds, detection output schema, export behavior, or RC package layout.
**Context**: Phase 2A showed EfficientNet batching could preserve secondary scores within `1e-6` while saving roughly `15-20%` of CPU secondary-classifier time on benchmark fixtures. Phase 2B showed GPU/CUDA should remain a separate package decision, so Task-079 Phase 3 stayed CPU-first.
**Decision**: Batch only EfficientNet review-band detections, defaulting to `TOWERSCOUT_EN_BATCH_SIZE=8`; preserve low-confidence `secondary=0` and high-confidence `secondary=1` branches; cache EfficientNet device selection; harden EfficientNet CUDA setup to fall back to CPU if CUDA is visible but unusable; add candidate/subphase diagnostics through existing performance metadata rather than changing public detection results.
**Execution**: Updated `ts_en.py` to batch candidate tensors, return classifier stats, record `last_classify_stats`, cache `device_label`, and support CPU fallback after CUDA setup failure. Updated `ts_yolov5.py` to accumulate secondary-classifier crop/transform/stack/forward/attach timings plus candidate count, batch count, batch size, device, and seconds-per-candidate metadata. Added focused unit coverage for batched classification, CUDA fallback, and secondary metrics propagation.
**Output**: The fixed 6-tile local benchmark after implementation produced 41 raw detections, 9 EfficientNet candidates, `model_yolo_inference=5.37s`, `model_secondary_classifier_inference=5.77s`, `model_secondary_forward=5.72s`, `secondary_classifier_batches=4`, and `secondary_classifier_seconds_per_candidate=0.6408` on CPU.
**Validation**: Passed Python compile, targeted ML/reliability unit tests, full unit suite, integration end-to-end smoke, fixed local benchmark, `.agent_work` validation, and diff whitespace checks. Validation details are listed in the Validation Results section.
**Next**: Treat `TASK-079` as complete for RC1 reliability/performance instrumentation. Use the accepted single GPU-capable package direction to scope `TASK-075`.

### 2026-05-15 - Phase 2A Secondary-Classifier Benchmark Research
**Objective**: Determine whether the observed slow CPU model run is reproducible and whether EfficientNet batching is a safe RC1 optimization candidate.
**Context**: The 6-tile Azure smoke recorded `actual_model_time_seconds=85.10`, including `model_yolo_inference=15.40` and `model_secondary_classifier_inference=69.48`. Phase 1 evidence pointed at the secondary classifier, but the timing needed a fixed-input benchmark before implementation.
**Decision**: Benchmark against the cached six tile images from the smoke run without provider download, geocoding, address rendering, or Azure drawing variability. Compare current one-by-one EfficientNet scoring with an in-memory batched equivalent, but do not change code yet.
**Execution**: Loaded the local CPU runtime (`torch==2.2.1+cpu`, CUDA unavailable, 10 torch threads), local YOLO weights, local EfficientNet weights, and the six cached tile images. Re-ran YOLO on the fixed cropped tiles to recreate 41 raw detections and 9 EfficientNet review-band candidates. Timed the current classifier loop, batched classifier variants, repeated-candidate scaling, and thread-count sensitivity.
**Output**: The actual `YOLOv5_Detector.detect()` path reproduced 41 raw detections with `model_yolo_inference=14.71s`, `model_secondary_classifier_inference=13.80s`, and `detect_wall_seconds=28.97s`. Direct one-by-one EfficientNet scoring took `13.01s`; batch size 8 took `10.78s` with max score delta `1.79e-7`. For a repeated 36-candidate scaling fixture, current scoring took `52.59s`; batch sizes 8 and 16 took about `41.8-41.9s`, preserving scores within `1e-6`. Thread-count checks did not beat the current 10-thread default on this host.
**Validation**: Output stability was verified by comparing current and batched secondary scores with max absolute deltas below `1e-6`. The live `69.48s` secondary timing was not reproduced, so it should be treated as an outlier or runtime-environment effect until another live run confirms it.
**Next**: For Phase 3, consider a bounded EfficientNet batch implementation with default batch size 8 and explicit candidate-count/per-candidate timing metadata. Do not treat batching alone as a full fix for the 85s smoke outlier.

### 2026-05-15 - Phase 2B GPU/CUDA Package Feasibility Research
**Objective**: Determine whether RC1 can safely offer automatic GPU/CUDA acceleration while preserving CPU fallback for local end-user deployment.
**Context**: The code already calls `torch.cuda.is_available()` in YOLO and EfficientNet paths, but the current RC container installs CPU-only PyTorch wheels through `PYTORCH_INDEX_URL=https://download.pytorch.org/whl/cpu` and Compose does not request GPU devices.
**Decision**: Keep RC1 CPU-first unless Phase 3 intentionally selects and validates a separate GPU package path. A single universal CPU/GPU image is technically plausible but not the recommended RC1 default because it would increase package size and support complexity while still requiring host GPU/container configuration.
**Execution**: Reviewed the local Dockerfile, Compose files, launcher scripts, readiness metadata, and official PyTorch, Docker, and NVIDIA documentation. Checked local runtime visibility: the `.venv` is CPU-only (`torch.version.cuda is None`), `nvidia-smi` is not available on the host path, Docker CLI is installed but the daemon was not running, and Podman exists but its machine connection failed.
**Output**: PyTorch 2.2.1 publishes separate CPU, CUDA 11.8, and CUDA 12.1 wheel indexes, so host GPU presence is not enough; the package must install CUDA-enabled PyTorch. Docker Desktop GPU support on Windows requires the WSL2 backend, NVIDIA GPU/driver support, and GPU exposure to the container. Docker Compose needs GPU device reservations with `capabilities: [gpu]`; Podman GPU support should be treated as a separate CDI/NVIDIA Container Toolkit validation path. Current YOLO has a CUDA setup fallback to CPU, but EfficientNet currently lacks an explicit CPU fallback if CUDA setup fails after `torch.cuda.is_available()` returns true.
**Validation**: Research used official PyTorch, Docker, and NVIDIA sources listed in the Phase 2 research references. Local GPU execution could not be validated on this host without NVIDIA tooling and a working container GPU runtime.
**Next**: If Phase 3 selects GPU work, implement it as an optional GPU image/overlay with explicit runtime diagnostics and a device policy such as `TOWERSCOUT_DEVICE=auto|cpu|cuda`; otherwise keep RC1 CPU-only and move GPU enablement to `TASK-075`.

### 2026-05-15 - Phase 2A/2B Scope Split Planned
**Objective**: Refine the open performance phase so secondary-classifier speed investigation and GPU/CUDA feasibility are evaluated separately before Phase 3 implementation decisions.
**Context**: Phase 1 bounded smoke evidence showed the CPU bottleneck is EfficientNet secondary-classifier inference. The user also asked whether TowerScout can detect CUDA-capable machines and run GPU when available while falling back to CPU otherwise.
**Decision**: Split Phase 2 into Phase 2A for deterministic secondary-classifier benchmarking and Phase 2B for GPU/CUDA RC package feasibility. Keep Phase 3 as the decision point for implementation, preserving CPU-first RC1 guidance unless GPU packaging is proven supportable.
**Execution**: Updated requirements, acceptance criteria, implementation plan, release/package constraints, validation plan, known findings, and research references to reflect the split.
**Output**: Task documentation now distinguishes application-level CUDA auto-detection from release-package GPU support requirements and records the secondary-classifier benchmark as the first optimization target.
**Validation**: Passed `python .agent_work/scripts/validate_agent_work.py` after synchronization with `current-tasks.md`.
**Next**: Begin Phase 2A secondary-classifier investigation, then complete Phase 2B GPU/CUDA feasibility before any Phase 3 code changes.

### 2026-05-15 - Phase 1 Correctness And Instrumentation Implemented
**Objective**: Implement the RC1-critical reliability and measurement fixes without changing release package or model-output contracts.
**Context**: Phase 1 focused on the defects observed during pre-RC testing: missing address display, Azure completed-shape validation reliability, and insufficient model performance breakdown. Redis-specific live validation remains deferred unless Redis is explicitly brought into the RC1 package path.
**Decision**: Keep the release posture unchanged: TLS verification stays enabled by default, insecure TLS remains an explicit support workaround, model weights/thresholds/assets are untouched, and frontend changes flow through source modules plus the generated bundle.
**Execution**: Added shared provider TLS preflight (`ts_tls.py`), reused it in provider-key validation and geocoding, standardized fallback address text as `Coordinates: <lat>, <lng>`, hardened detection/manual/route fallback handling, corrected geocache neighboring bucket lookup for file and Redis backends, tightened Azure drawing validation to require completed extractable shapes only in completed-shape contexts, escaped detection-list address rendering, and added additive model timing/runtime metadata. Rebuilt `webapp/js/towerscout.js` from source.
**Output**: Phase 1 code is implemented with targeted Python and JavaScript coverage. Manual tower and `/api/geocode/reverse` recoverable failures now return/store coordinate fallback data instead of blank addresses or route 500s.
**Validation**: Passed focused backend, frontend, and broader unit validation listed in the Validation Results section.
**Next**: Capture bounded detection smoke evidence for `TASK-066`, then feed any changed troubleshooting/support notes into `TASK-071`.

### 2026-05-15 - Bounded Azure Detection Smoke Backend Evidence
**Objective**: Capture live smoke evidence from the user's 6-tile Azure detection run.
**Context**: The user started the application locally and ran a bounded Azure detection on 6 tiles from `http://localhost:5000`.
**Execution**: Checked `/api/readiness`, `/api/detection/progress`, `webapp/logs/towerscout.log`, `webapp/logs/towerscout_errors.log`, `webapp/logs/performance.log`, and `webapp/logs/performance.jsonl` after the run completed.
**Output**: Readiness was `ready`; progress returned `idle` after completion. The run used Azure, created/downloaded 6 tiles, produced 41 raw detections, retained 34 selected detections after boundary/dedupe filtering, and completed geocoding with Azure Maps provider addresses. The latest performance row includes the new Phase 1 timing keys and runtime metadata.
**Performance Evidence**: `actual_model_time_seconds=85.10`, `total_workflow_time_seconds=104.89`, `tile_download=1.77`, `model_initialization=6.75`, `model_yolo_inference=15.40`, `model_secondary_classifier_inference=69.48`, `geocoding=11.22`, `model_device=cpu`, `model_batch_size=10`, `model_tile_count=6`, `secondary_classifier_enabled=true`.
**Finding**: The first live timing breakdown points to EfficientNet secondary-classifier inference as the dominant model-time cost for this 6-tile CPU run, not tile download, YOLO inference, or post-processing.
**Validation**: Backend smoke evidence passed. Right-panel visual address display and Azure completed-shape UI behavior still require user/browser confirmation.
**Next**: Confirm right-panel address groups in the UI, then run a small Azure drawing tools shape-completion smoke.

### 2026-05-15 - Bounded Azure Browser Smoke Confirmed
**Objective**: Complete the user-visible portion of the 6-tile Azure bounded smoke.
**Context**: Backend logs showed successful Azure detection/geocoding and new performance timing fields. The remaining release-risk checks were visual/browser confirmation of the right-hand panel and Azure drawing tools.
**Execution**: User confirmed that the right-hand detection panel shows address groups correctly and that Azure drawing tools accepted a completed small polygon/rectangle as valid.
**Output**: Phase 1 bounded smoke is complete for the observed RC1 reliability concerns: address display, Azure completed-shape validation, and model timing instrumentation.
**Validation**: PASS for bounded Azure browser smoke. Backend evidence and user-visible UI confirmation are both recorded.
**Next**: Use the Phase 1 timing evidence to run Phase 2A secondary-classifier benchmarking, complete Phase 2B GPU/CUDA feasibility research, and hand TLS/fallback troubleshooting notes to `TASK-071` / `TASK-066`.

### 2026-05-15 - Phase 1 Implementation Started
**Objective**: Start Phase 1 RC1 correctness and measurement implementation.
**Context**: The user approved proceeding with Phase 1, agreed to defer Redis-specific neighbor-cache validation unless Redis is explicitly part of RC1, and confirmed the default approach of correctness/instrumentation before optimization.
**Decision**: Begin with shared TLS/fallback/cache fixes, then Azure drawing/address rendering fixes, then additive performance instrumentation, keeping model behavior and release package contracts unchanged.
**Execution**: Updated `TASK-079` status to `IN_PROGRESS` in the task file and `.agent_work/current-tasks.md`.
**Output**: Task is ready for implementation work.
**Validation**: Pending after implementation and task-state synchronization.
**Next**: Inspect exact code and test surfaces, then implement the first backend slice.

### 2026-05-15 - Plan Review Amendments Incorporated
**Objective**: Incorporate accepted reviewer feedback before implementation begins.
**Context**: The external plan review agreed with the three-phase structure but recommended shared TLS handling, manual reverse-geocode fallback coverage, canonical fallback formatting, context-aware Azure empty-polygon validation, address escaping, Redis/cache clarity, expanded model timing, and sanitized logging guardrails. The reviewer evaluated the `docs/task-071-end-user-release-docs` branch where `TASK-071` is completed, while this local checkout still shows `TASK-071` as not started until branch integration.
**Decision**: Accept the review amendments with one repo-specific clarification: keep the current Compose/container CA defaults valid and avoid introducing mandatory custom CA bundles; fail early only when configured bundle paths are missing or unusable. Treat Redis neighbor lookup as preferred Phase 1 behavior but allow an explicit RC1 deferral if it is not part of the validated release path.
**Execution**: Updated requirements, acceptance criteria, dependencies, Phase 1 implementation plan, release constraints, validation plan, and known findings in this task file.
**Output**: `TASK-079` now records the reviewer refinements as implementation-ready scope.
**Validation**: Pending `.agent_work` validation after this documentation update.
**Next**: Validate `.agent_work`, then start Phase 1 implementation.

### 2026-05-15 - Task Created
**Objective**: Create a release-critical task for the geocoding/address display, Azure drawing validation, and model performance instrumentation fixes identified during pre-RC testing.
**Context**: Sprint 06 is near the V1 RC1 package/docs/validation gate. These findings affect user-visible reliability and supportability, and they need to be resolved or measured before `TASK-071` docs and `TASK-066` clean-machine validation can be trusted.
**Decision**: Split the work into three phases: Phase 1 hardens correctness and adds timing instrumentation for RC1; Phase 2 benchmarks optimization candidates; Phase 3 implements optimization only if Phase 2 proves a material, low-risk win.
**Execution**: Created `.agent_work/tasks/completed/TASK-079-rc1-reliability-fixes.md` and synchronized `.agent_work/current-tasks.md`.
**Output**: Task file ready for intake.
**Validation**: Pending `.agent_work` validation after task synchronization.
**Next**: Start Phase 1 by implementing geocoding TLS preflight, cache clustering correction, Azure drawing validation cleanup, and performance phase timing.

---

## Validation Results

### Test Summary
**Test Date**: 2026-05-19
**Test Environment**: Local Windows workspace, Python virtualenv, Node frontend contract tests
**Test Status**: PHASE_3_PASS; single GPU-capable package implementation handed to `TASK-075`

**Commands Passed**:
- `node webapp/build.js`
- `node tests/frontend/test_task_079_frontend_contract.js`
- `node tests/frontend/test_global_contract.js`
- `node tests/frontend/test_debug_logging_contract.js`
- `node tests/integration/test_task_064_provider_state_manager.js`
- `.venv\Scripts\python.exe -m pytest tests/unit/test_geocoding.py tests/unit/test_task_079_reliability.py tests/unit/test_config.py tests/unit/test_runtime_hardening.py -q -p no:cacheprovider`
- `.venv\Scripts\python.exe -m pytest tests/unit -q -p no:cacheprovider`
- `.venv\Scripts\python.exe -m py_compile webapp\ts_en.py webapp\ts_yolov5.py`
- `.venv\Scripts\python.exe -m py_compile webapp\ts_en.py webapp\ts_yolov5.py tests\unit\test_ts_en_classifier.py tests\unit\test_yolov5_secondary_metrics.py`
- `.venv\Scripts\python.exe -m pytest tests/unit/test_ts_en_classifier.py tests/unit/test_yolov5_secondary_metrics.py tests/unit/test_yolov5_local_loader.py -q -p no:cacheprovider`
- `.venv\Scripts\python.exe -m pytest tests/unit/test_task_079_reliability.py tests/unit/test_config.py tests/unit/test_geocoding.py -q -p no:cacheprovider`
- `.venv\Scripts\python.exe -m pytest tests/integration/test_end_to_end.py -q -p no:cacheprovider`
- `.venv\Scripts\python.exe -m pytest tests/unit -q -p no:cacheprovider`
- `python .agent_work/scripts/validate_agent_work.py`
- `git diff --check -- .agent_work/tasks/completed/TASK-079-rc1-reliability-fixes.md .agent_work/current-tasks.md`

**Fixed Local Benchmark Passed**:
- Cached 6-tile fixture from the Azure smoke run.
- CPU runtime: `torch==2.2.1+cpu`, CUDA unavailable, 10 torch threads.
- Output: 41 raw detections, 9 EfficientNet review-band candidates, 41 retained after secondary threshold review.
- Timing after Phase 3 batching: `detect_wall_seconds=11.32`, `model_yolo_inference=5.37`, `model_secondary_classifier_inference=5.77`, `model_secondary_forward=5.72`, `secondary_classifier_batches=4`, `secondary_classifier_seconds_per_candidate=0.6408`.

### Acceptance Criteria Validation
- [x] Geocoding TLS preflight implemented - shared `ts_tls.py` used by config validation and geocoding
- [x] Address fallback/display behavior verified - canonical coordinate fallback covered by Python and frontend tests
- [x] Geocache clustering corrected - neighboring bucket lookup covered by unit tests
- [x] Azure drawing validation corrected - completed-shape non-empty/unsupported-shape behavior covered by frontend tests
- [x] Performance phase timings added - additive phase timing and runtime metadata covered by unit tests
- [x] Frontend bundle rebuilt - `node webapp/build.js` passed
- [x] Targeted automated tests pass - focused Python/JS tests and unit suite passed
- [x] Bounded detection smoke evidence captured - 6-tile Azure run passed with backend evidence and user-visible UI confirmation
- [x] Phase 2A secondary-classifier benchmark evidence captured - fixed 6-tile fixture, direct classifier benchmark, repeated-candidate scaling, and thread sensitivity completed
- [x] Phase 2B GPU/CUDA package feasibility documented - official PyTorch/Docker/NVIDIA requirements checked against current Dockerfile/Compose/runtime shape
- [x] Phase 3 CPU optimization implemented - EfficientNet review-band candidates are batched without changing thresholds or detection JSON fields
- [x] Phase 3 diagnostics implemented - secondary candidate count, batch count, batch size, device, subphase timings, and seconds per candidate are recorded in existing performance structures

### Issues Identified

- Phase 1 timing evidence showed secondary-classifier inference dominated the live 6-tile CPU model time (`69.48s` of `85.10s` model time), but fixed-input Phase 2A benchmarks reproduced the same 41 raw detections with about `13.8s` secondary time. Phase 3 reduced the fixed local secondary timing further, but the original live outlier was not reproduced.
- EfficientNet batching reduces CPU secondary-classifier time on the benchmark fixture and now emits enough diagnostics to distinguish candidate volume, batch count, and forward-pass time in future slow runs.
- GPU/CUDA use is possible through the existing CUDA auto-detection code path only when the runtime has CUDA-enabled PyTorch and the host/container stack exposes NVIDIA devices. The current package path is still CPU-only until `TASK-075` implements and validates the accepted single GPU-capable package plan.
- EfficientNet now falls back to CPU if CUDA setup fails, but GPU package support still requires `TASK-075` validation because the current package uses CPU-only PyTorch wheels and local GPU execution was not validated on this host.
- Redis neighboring-bucket behavior is implemented in code, but Redis-specific live validation remains deferred unless Redis is explicitly included in the RC1 validation path.

### Remediation Actions

- Carry bounded address/Azure/performance smoke into `TASK-066`.
- Keep the default release path CPU-safe and route single GPU-capable package implementation to `TASK-075` with the May 20 plan as the starting point.
- Feed any changed troubleshooting language for TLS bundle and coordinate fallback behavior into `TASK-071`.

### Sign-off

Phase 1 correctness/instrumentation validated. Phase 2A/2B research complete. Phase 3 CPU secondary-classifier optimization and diagnostics validated. `TASK-079` is complete for RC1 reliability/performance scope; single GPU-capable package implementation moves to `TASK-075`.

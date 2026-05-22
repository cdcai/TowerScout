# Current Tasks - Active Sprint

**Sprint Period**: Sprint 06 planning / V1 RC1 readiness begins May 11, 2026  
**Last Updated**: May 22, 2026
**Focus**: Produce a V1 RC1 / pilot-ready AGPL-compliant YOLO-enabled release path by closing release-support carry-forward work, correcting release compliance artifacts, writing package-based end-user docs, validating the clean-machine release candidate, and preparing pilot / UAT execution.
**Status**: Sprint 06 committed lane selected. `TASK-065`, `TASK-072`, `TASK-079`, and `TASK-071` are completed and remain in the active task folder until sprint closeout; `TASK-069` sign-off is sufficient to merge PR #11 as the internal controlled AGPL-governed RC planning and compliance baseline; `TASK-075` implementation is merged with NVIDIA-host validation still pending before broad GPU support claims; `TASK-066` local package validation passed after targeted script/runtime fixes, with final digest-pinned RC artifact validation still pending; `TASK-073` remains selected for Sprint 06.

---

## Sprint 05 Closeout Summary

Sprint 05 delivered the runtime and release-readiness foundation that Sprint 04 intentionally left open. The completed Sprint 05 task artifacts have been moved from `.agent_work/tasks/active/` to `.agent_work/tasks/completed/`:

- `TASK-051`: runtime dependency verification and split
- `TASK-055`: YOLO Torch Hub pinned-ref hardening
- `TASK-056`: first-run reliability and runtime determinism hardening
- `TASK-057`: local YOLO runtime ownership and Torch Hub independence
- `TASK-052`: current integration smoke-test baseline
- `TASK-062`: pre-Docker runtime cleanup and YOLO loader hardening
- `TASK-063`: pre-Docker release hardening and CI reproducibility gate
- `TASK-064`: targeted runtime responsiveness and inference baseline
- `TASK-025`: Docker-compatible / OCI containerization
- `TASK-054`: local launch UX Phase 1 MVP

`TASK-029` was never started during Sprint 05. Its task artifact has been archived as a not-started planning artifact, and the task remains in the backlog table rather than staying in the active sprint.

---

## Sprint 06 Goal

Produce and internally validate a V1 RC1 / pilot-ready local release package path for Windows 11 AMD64 users, including AGPL-compliant YOLO release notices, asset delivery, end-user documentation, release policy boundaries, and a clean-machine validation gate.

Sprint 06 is not intended to declare final V1 completion. Final V1 completion should wait until pilot/UAT feedback has been triaged, install/launch/setup/detection blockers have been fixed or explicitly accepted, and remaining work has been sorted into V1 patch items or the V2 roadmap.

---

## Active Carry-Forward

### **TASK-065: Release Packaging And Runtime Support Follow-Through**
**Status**: COMPLETED - release-owner support-language review accepted on May 11, 2026  
**Type**: B/C (Release Engineering / Runtime Supportability)  
**Priority**: HIGH  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 06 intake / post-`TASK-054` release-support gate  
**Task File**: `.agent_work/tasks/active/TASK-065-release-packaging-runtime-support.md`

**Objective**: Close the release-support items intentionally deferred from `TASK-025` and informed by `TASK-054`, without reopening the completed OCI/container runtime baseline or launcher MVP.

**Current State**:
- Docker-Desktop-free Podman Compose-provider validation passed with `podman-compose 1.5.0`.
- Hosted asset download/bootstrap is out of scope for the v1 control package.
- Bundled OCI image archive fallback is unsupported for the v1 control package; restricted-network support should use support-managed image preload plus local asset import.
- Broad browser/provider regression passed for Google and Azure after launcher browser targeting was changed to `http://localhost:<port>`.
- Missing TLS CA bundle handling now returns actionable setup/support guidance instead of a generic provider-validation 500.
- Release package assembly validation passed into ignored `dist/towerscout-task065-validation`.
- Reviewer hardening addressed evidence redaction, immutable digest enforcement, provider-aware TLS CA verification, Compose-provider reporting, and focused tests.

**Closeout Status**:
- Release owner accepted the final support language and residual caveats on May 11, 2026.
- Commit checkpoint `2280b68 chore(task-065): complete release support validation` records the release-support updates.
- Follow-up tasks remain in the backlog for clean-machine release-candidate validation, CI gate tightening, Windows/Podman automation, license policy review, and restricted-network package enhancements.

**Validation Notes**:
- `tests/unit/test_config.py tests/unit/test_release_package_script.py` passed after reviewer hardening.
- PowerShell parser checks passed for release helper scripts.
- Podman launcher provider-reporting check passed and reached readiness `ready`.
- `npm.cmd run test:stage-0` remains not runnable in this shell because the Windows `bash.exe` path resolves to WSL without `/bin/bash`.

**User Value**: Turns the completed container and launcher baseline into release-support language and validation evidence that can be trusted by non-technical local users and first-line support.

---

## Sprint 06 Committed Lane

### **TASK-072: Release Asset Bundle Contract**
**Status**: COMPLETED - V1 RC1 asset bundle contract documented
**Type**: C (Release Engineering / Asset Governance)  
**Priority**: CRITICAL  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 06 V1 RC1  
**Task File**: `.agent_work/tasks/active/TASK-072-release-asset-bundle-contract.md`

**Objective**: Define how model weights and ZIP-code data are bundled, versioned, checksummed, distributed, placed next to the release package, imported, verified, and matched to a TowerScout release.

**Dependencies**: `TASK-065`; current `webapp/asset_manifest.v1.json`; release package shape.

**Closeout Status**:
- Durable contract created at `docs/release-asset-bundle-contract.md`.
- Release package generation now includes the asset bundle contract doc.
- Asset ZIP root layout is `model_params/`, `data/`, and `asset_manifest.v1.json`; users extract those entries into the package `assets/` directory before import.
- External asset ZIP publication is allowed only for the accepted `agpl-yolo` release posture when the release manifest and model notices label YOLO weights as YOLO-derived/AGPL-governed unless separate written terms say otherwise.

**User Value**: Removes the largest current ambiguity in the local release path: what non-git assets users need, where those assets come from, and exactly where they go.

### **TASK-069: License And Release Policy Review**
**Status**: SIGN_OFF_RECORDED - sufficient to merge PR #11 as internal Sprint 06 RC baseline
**Type**: C (Legal / Release Policy / Governance)
**Priority**: CRITICAL
**Estimated Effort**: 0.5-1 day technical prep plus owner/legal review
**Target Sprint**: Sprint 06 V1 RC1
**Task Folder**: `.agent_work/tasks/active/TASK-069/`

**Objective**: Convert the prior Apache-only public-release strategy into an AGPL-compliant YOLO-enabled RC/pilot release posture for review, with corrected notices, model/data terms, source-offer requirements, release control package compliance payload, and image generic notices/OCI labels.

**Current Direction**:
- The YOLO-enabled release track is `agpl-yolo`.
- The ONNX/non-Ultralytics runtime migration is no longer a pre-RC blocker; it moves to a later permissive Apache-only release or runtime modernization path.
- TowerScout-authored code may be Apache-2.0 where ownership and relicensing authority are confirmed, but the full YOLO-enabled package/image is not Apache-2.0-only.
- The release control package must include corrected YOLO AGPL attribution, model/data/provider terms, release manifest, checksums, image digest metadata, SBOM reference, source notice, and revocation notes; the image carries generic compliance notices and OCI labels sufficient to match it to the control package by pinned digest.
- Model weights may be published only with AGPL-compatible labeling or separate written terms.
- Formal owner/legal/reviewer approval remains a later gate for broader distribution, model/data/provider publication, and the clean curated public release line; the current development/workshop repository history should not be published as-is without explicit review.

**User Value**: Allows Sprint 06 to target a YOLO-enabled RC/pilot without waiting for detector runtime replacement, while keeping the release honest about AGPL obligations and source availability.

### **TASK-079: RC1 Reliability Fixes And Performance Instrumentation**
**Status**: COMPLETED - Phase 3 CPU optimization validated; single GPU-capable package plan handed to TASK-075
**Type**: C (Release-Critical Reliability / Detection Workflow Hardening)
**Priority**: CRITICAL
**Estimated Effort**: Phase 1: 1-2 days (8-16 hours); Phase 2A/2B: 0.5-1 day investigation; Phase 3 follow-up depends on benchmark and GPU/CUDA evidence
**Target Sprint**: Sprint 06 V1 RC1
**Task File**: `.agent_work/tasks/active/TASK-079-rc1-reliability-fixes.md`

**Objective**: Fix or harden the pre-RC reliability issues affecting detected-tower address display, Azure drawing-shape validation, and model-performance diagnosis without disrupting the V1 RC1 package, asset, provider setup, or readiness contracts.

**Current Direction**:
- Phase 1 code and validation are complete: shared geocoding TLS preflight, canonical coordinate fallback, neighboring geocache bucket lookup, Azure completed-shape validation cleanup, address escaping, additive model phase timing, and a 6-tile Azure bounded smoke with right-panel address and drawing-tool confirmation.
- Phase 2A research is complete: the fixed 6-tile benchmark reproduced 41 raw detections and 9 EfficientNet candidates, but measured secondary-classifier time around `13.8s` rather than the live smoke's `69.48s`. EfficientNet batching is output-stable and can save roughly `15-20%` of CPU secondary time on benchmark fixtures, but it does not fully explain the live outlier.
- Phase 2B research is complete: current code can auto-use CUDA only when CUDA-enabled PyTorch and visible NVIDIA devices are present; the RC package path currently installs CPU-only PyTorch wheels and has no Compose GPU reservation.
- Phase 3 CPU optimization is complete: EfficientNet review-band candidates are batched with default batch size `8`, secondary-classifier subphase/candidate diagnostics are recorded, and EfficientNet now falls back to CPU if CUDA setup is visible but unusable.
- RC1 remains CPU-safe by default. The approved follow-up direction is a single CUDA-capable package/image with CPU fallback, optional GPU launch overlay, explicit runtime diagnostics, and validation gates documented in `.agent_work/context/analysis/task-079-single-gpu-capable-package-plan.md`; the PR #14 review disposition adds shared device-policy resolution, EfficientNet per-chunk CUDA transfer, readiness diagnostics, GPU concurrency, and fixed-fixture parity as `TASK-075` entry criteria.

**Dependencies**: `TASK-065`; `TASK-069`; `TASK-072`; current detection/geocoding/provider workflows. `TASK-071` and `TASK-066` should consume this task's outcomes for docs and clean-machine validation.

**User Value**: Reduces the chance that RC1 pilot users encounter missing addresses, rejected valid Azure shapes, or unexplained slow detections, while keeping the release path supportable and measured.

### **TASK-075: Single GPU-Capable Package Implementation**
**Status**: IN_PROGRESS - Phase 3 GPU overlay and launcher implemented; NVIDIA host validation pending
**Type**: C (Runtime Policy / Hardware Compatibility / Release Packaging)
**Priority**: CRITICAL
**Estimated Effort**: 1-3 days (8-24 hours), split by validation availability
**Target Sprint**: Sprint 06 V1 RC1
**Task File**: `.agent_work/tasks/active/TASK-075-single-gpu-capable-package.md`

**Objective**: Implement the reviewed single GPU-capable TowerScout package direction while preserving a CPU-safe default release path.

**Current Direction**:
- Phase 1 runtime policy is implemented: shared `TOWERSCOUT_DEVICE=auto|cpu|cuda` policy resolution lives in `webapp/ts_device.py`.
- Readiness now includes non-loading `ml_runtime` diagnostics.
- YOLO and EfficientNet report requested policy, selected device, CUDA build, CUDA availability, device name, and fallback reason.
- EfficientNet CUDA batching now stacks and transfers candidate tensors per configured chunk.
- GPU concurrency has an explicit conservative default through `TOWERSCOUT_GPU_CONCURRENCY`.
- CUDA and CPU proof images now build from the current branch. The CUDA image uses `torch==2.2.1+cu121`, preserves CPU fallback on this non-GPU host, and fails closed with readiness guidance when `TOWERSCOUT_DEVICE=cuda` is required without an exposed GPU.
- The local CUDA proof image is `7.11GB`; the current CPU proof image is `2.8GB`, making the size tradeoff about `4.31GB`.
- Optional `compose.gpu.yaml` is implemented and included in release package staging.
- `start.bat` / `scripts/launch.ps1` now support `-Gpu off|auto|on`; default `off` remains CPU-safe, `auto` only requests the overlay when a simple Docker/NVIDIA host preflight detects a GPU, and `on` explicitly requires CUDA.
- GPU support claims remain pending NVIDIA Docker Desktop WSL2 host validation, fixed-fixture CPU/GPU parity, and timing evidence.

**Dependencies**: `TASK-079`; `TASK-051`; `TASK-065`; `TASK-071`; `TASK-066`.

**User Value**: Gives pilot users one package path that can accelerate on supported NVIDIA hosts while still launching predictably on CPU-only machines.

### **TASK-071: End-User Release Package Documentation**
**Status**: COMPLETED - focused validation passed; ready for TASK-066
**Type**: B/C (Documentation / User Enablement)  
**Priority**: CRITICAL  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 06 V1 RC1  
**Task File**: `.agent_work/tasks/active/TASK-071-end-user-release-docs.md`

**Objective**: Produce the package-based quick start and full user guide that tell a non-technical Windows pilot user what to download, where assets go, how to launch, how to configure provider keys, how to validate success, how to find source/license notices, and how to report problems.

**Dependencies**: `TASK-069`; `TASK-072`; `TASK-075`; release package shape; current OCI quick-start/runtime docs.

**Closeout Status**:
- Package-local Quick Start, Package Guide, User Guide, Project Overview, and styled HTML docs were added under `docs/`.
- Settings Resource Links now point to package-local Project Overview, User Guide, Source/licenses, Video Guides, and TowerScout Research Article.
- `/docs/` serves the package-local Quick Start, `/license` serves a styled HTML source/license page, and `/license.txt` remains available for plain-text notices.
- Release package and runtime image assembly now include package-local docs needed by Resource Links.
- Older source/Conda tester guides are labeled as legacy source-install guidance.
- The Quick Start and support docs now explicitly list prerequisite software: Windows 11 AMD64, PowerShell, browser, outbound internet, disk space, one supported container engine, and provider key; they also state Git/Python/Conda/Node/VS Code are not required for the package path.
- Focused Flask route, license, release package, docs-command, and agent-work validation passed with only the known `127.0.0.1` docs warning.

**User Value**: Converts the engineered release package into a self-service pilot path instead of a support-only handoff.

### **TASK-066: Release Candidate Validation Gate**
**Status**: IN_PROGRESS - local package path passed after fixes; final digest-pinned RC artifact validation pending
**Type**: C (Release Engineering / Validation)  
**Priority**: CRITICAL  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 06 V1 RC1  
**Task File**: `.agent_work/tasks/active/TASK-066-release-candidate-validation-gate.md`

**Objective**: Internally prove the release package, asset bundle, docs, setup flow, restart persistence, and bounded detection path from a clean user-facing environment before external pilot/UAT begins. Also evaluate PR16 follow-ups for visible CI/static-analysis release gates and Markdown-to-HTML generation or parity checks for Settings-linked docs.

**Dependencies**: `TASK-065`; `TASK-069`; `TASK-071`; `TASK-072`; agreed release package shape.

**Current State**:
- Local Docker Desktop validation generated RC-style packages, imported all 9 manifest assets with hash verification, reached readiness `ready`, persisted Azure provider setup, and passed a bounded Azure detection smoke on the public local fixture.
- Validation found and fixed three release-path blockers: non-default port asset import, stale model discovery after asset copy, and hidden EfficientNet first-use download.
- Docker Desktop is the validated local engine. Podman image build on this host is blocked by base-image TLS certificate verification before TowerScout code runs.
- Evidence is local-package evidence only because the package used a mutable local image and dirty-tree allowance. Final sign-off still needs the real digest-pinned RC package/image.

**User Value**: Prevents end-user testing from being dominated by known package/docs/asset gaps and produces evidence that the V1 RC1 path is actually usable.

### **TASK-073: Clean-Machine Pilot / UAT Execution Plan**
**Status**: NOT_STARTED - selected for Sprint 06  
**Type**: B/C (User Testing / Release Validation)  
**Priority**: HIGH  
**Estimated Effort**: 0.5-1 day (4-8 hours)  
**Target Sprint**: Sprint 06 V1 RC1  
**Task File**: `.agent_work/tasks/active/TASK-073-clean-machine-uat-plan.md`

**Objective**: Define the controlled pilot/UAT workflow, tester instructions, acceptance checklist, environment capture, issue-report workflow, success criteria, and support escalation path.

**Dependencies**: `TASK-066`; draft user package docs.

**User Value**: Ensures external testing starts from a repeatable, evidence-producing workflow instead of ad hoc feedback collection.

---

## Policy Lane Candidates

These tasks are important for V1 RC1, but they are not yet active task files in this planning update. Pull them into `current-tasks.md` and create active task docs if owner/legal availability or release risk requires formal Sprint 06 commitment.

| Task | Recommended Handling | Reason |
|---|---|---|
| `TASK-076` Provider API Key Exposure And Restriction Policy | Candidate for parallel Sprint 06 work | Browser map SDK keys remain client-visible; v1 needs an approved restriction/support policy or an engineering blocker. AGPL does not change provider/API terms. |
| `TASK-075` Single GPU-Capable Package Implementation | Candidate follow-up after `TASK-079` closeout | `TASK-079` produced the feasibility evidence and a source-backed plan. Start with shared `TOWERSCOUT_DEVICE` policy resolution, EfficientNet memory-bound CUDA chunking, readiness diagnostics, and fixed-fixture parity checks; keep the default launch CPU-safe and require CPU-only plus NVIDIA Docker Desktop WSL2 validation before changing RC support language. |

---

## Backlog Candidates To Watch

Do not forget these follow-through tasks. They are intentionally kept in `.agent_work/task-backlog.md` rather than pulled into the active sprint now, but `TASK-066` findings may justify selecting one or more before external UAT.

| Task | Pull Into Sprint 06 If | Notes |
|---|---|---|
| `TASK-074` Runtime Prerequisite Preflight | Clean-machine validation shows users/support still have to manually reason through Podman/Docker/Compose/ports/assets/TLS. | Conditional but likely. This is the first candidate to pull in if launch friction remains high. |
| `TASK-067` CI Release Gate Tightening | Release-candidate checks become repetitive, fragile, or too easy to skip manually. | Keep scope narrow: package assembly, image digest, manifest/checksum consistency, and launcher smoke behavior. |
| `TASK-068` Windows Test Portability And Script Validation | Script validation remains environment-sensitive or PowerShell/Windows coverage is needed before external UAT. | Useful release-support follow-through, especially around Windows-first helper scripts. |
| `TASK-077` Public Release Manifest And Asset Import Hardening | `TASK-069` AGPL release compliance needs a package payload, or `TASK-066` shows copy-then-verify import is too risky. | Pull forward the narrow compliance-payload slice now: release manifest, source URL/ref, checksums, image digest, SBOM reference, model/data terms, and revocation notes. Keep staged allowlist-only asset activation as follow-up unless validation makes it release-critical. |

---

## Sprint 06 Planning Guardrails

- Treat Sprint 06 as a V1 RC1 / pilot-ready release-readiness sprint, not final V1 completion.
- Do not start broad end-user testing until `TASK-069`, `TASK-072`, `TASK-071`, and `TASK-066` have produced a validated AGPL-compliant package/docs/assets path.
- Do not start V2 work until pilot/UAT blockers are fixed or explicitly accepted.
- Keep architecture follow-on work (`TASK-058`, `TASK-059`) behind release-candidate readiness unless the team intentionally pauses release work.
- Keep parked tail work (`TASK-028`, `TASK-061`, Advanced Filtering, Performance Dashboard, User Preferences) out of Sprint 06 unless new evidence makes one of them release-critical.

---

## Related Documentation

- [Sprint 06 Plan](./context/status/SPRINT-06-PLAN.md)
- [Task Backlog](./task-backlog.md)
- [Sprint 05 Retrospective Analysis](./context/analysis/SPRINT-05-RETROSPECTIVE-ANALYSIS-2026-05-08.md)
- [Completed Tasks](./completed-tasks.md)
- [Archived Sprint 05 Plan](./context/archive/2026-05/status/SPRINT-05-PLAN.md)

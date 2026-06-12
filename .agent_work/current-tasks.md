# Current Tasks - Active Sprint

**Sprint Period**: Sprint 06 planning / V1 RC1 readiness begins May 11, 2026  
**Last Updated**: June 12, 2026
**Focus**: Produce a V1 RC1 / pilot-ready AGPL-compliant YOLO-enabled release path by closing release-support carry-forward work, correcting release compliance artifacts, writing package-based end-user docs, validating the clean-machine release candidate, and preparing pilot / UAT execution.
**Status**: Sprint 06 committed lane selected. `TASK-065`, `TASK-072`, `TASK-079`, `TASK-071`, `TASK-067`, and `TASK-074` are completed and remain in the active task folder until sprint closeout; `TASK-069` sign-off is sufficient to merge PR #11 as the internal controlled AGPL-governed RC planning and compliance baseline; `TASK-075` implementation is merged with NVIDIA-host validation still pending before broad GPU support claims; `TASK-066` post-PR28 final prerelease Docker Desktop package path passed through checksum verification, bootstrap/readiness from the GitHub Release Application Package, Settings-linked docs, `/license`, in-container asset hash verification, and bounded Azure detection smoke on the refreshed final digest, with Podman Docker Hub source-build TLS, Docker-Desktop-free Podman, and NVIDIA GPU evidence still bounded follow-ups; `TASK-073` is active for clean-machine pilot/UAT planning and now has exact refreshed release artifact values, default smoke fixture, support contacts, provider-key evidence boundaries, published rc2/rc3 prereleases, rc2 provider setup / bounded Azure smoke, and rc3 package/downloaded-release setup validation; tester cohort selection and owner/reviewer acceptance remain before external tester launch; `TASK-080` has simplified the first-cohort setup path, produced and locked the consolidated Word guide, verified the Google first-launch TLS support path, and published/validated the refreshed rc3 UAT release package; owner/reviewer signoff and tester/cohort selection remain before external tester send.

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
- The Quick Start and support docs now explicitly list prerequisite software: Windows 11 AMD64, PowerShell, browser, outbound internet, disk space, Docker Desktop/WSL 2 as the primary pilot path, qualified Podman boundaries, and provider key; they also state Git/Python/Conda/Node/VS Code are not required for the package path.
- Focused Flask route, license, release package, docs-command, and agent-work validation passed with only the known `127.0.0.1` docs warning.

**User Value**: Converts the engineered release package into a self-service pilot path instead of a support-only handoff.

### **TASK-066: Release Candidate Validation Gate**
**Status**: IN_PROGRESS - final prerelease Docker Desktop package path and bounded Azure provider smoke passed; Podman source-build TLS, Docker-Desktop-free Podman, and NVIDIA GPU evidence pending
**Type**: C (Release Engineering / Validation)  
**Priority**: CRITICAL  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 06 V1 RC1  
**Task File**: `.agent_work/tasks/active/TASK-066-release-candidate-validation-gate.md`

**Objective**: Internally prove the release package, asset bundle, docs, setup flow, restart persistence, and bounded detection path from a clean user-facing environment before external pilot/UAT begins. Also evaluate PR16 follow-ups for visible CI/static-analysis release gates and Markdown-to-HTML generation or parity checks for Settings-linked docs.

**Dependencies**: `TASK-065`; `TASK-069`; `TASK-071`; `TASK-072`; agreed release package shape.

**Current State**:
- Final Docker Desktop validation generated and published the RC control package with refreshed post-PR28 GHCR digest `sha256:e90524870a279c04f941147fc30328636ac97f75be200fd06c929df83c49d158`, imported all 9 manifest assets with hash verification, reached readiness, served package-local docs and `/license`, and passed the owner-selected bounded Azure detection smoke on the public `200 west st, New York, NY 10282` fixture.
- Validation found and fixed three release-path blockers: non-default port asset import, stale model discovery after asset copy, and hidden EfficientNet first-use download.
- Docker Desktop and Podman package runtime paths are validated for CPU-default launch against the digest-pinned GHCR image. On this host, `podman compose` delegates to Docker Compose v5.1.3 as its external provider.
- `TASK-074` bootstrap/preflight follow-through passed clean post-merge package validation: verify-only asset ZIP checks are non-mutating, asset ZIP staging/import succeeds, packaged Compose entrypoints initialize `.env` from `.env.example`, and readiness reaches `setup_required` with assets `ok`.
- Podman source-build/base-image pulls from Docker Hub still fail TLS certificate verification inside the Podman VM before TowerScout code runs; this does not block the normal GHCR package path but remains a developer/build-path caveat.
- GPU acceleration remains unclaimed until NVIDIA Docker Desktop WSL2 host validation, fixed-fixture parity, and timing evidence pass.
- The non-runtime Flask route-test timeout/isolation gap identified during review was closed by `TASK-067` / PR #19. Focused route/config/runtime tests now run with `pytest-timeout` active and isolated test runtime paths.

**User Value**: Prevents end-user testing from being dominated by known package/docs/asset gaps and produces evidence that the V1 RC1 path is actually usable.

### **TASK-067: CI Release Gate Tightening**
**Status**: COMPLETED - PR #19 merged
**Type**: C (CI / Release Engineering / Test Reliability)
**Priority**: HIGH
**Estimated Effort**: 0.5-1 day (4-8 hours)
**Target Sprint**: Sprint 06 V1 RC1
**Task File**: `.agent_work/tasks/active/TASK-067-ci-release-gate-tightening.md`

**Objective**: Tighten the RC validation baseline where `TASK-066` exposed fragility: pytest route-test collection could hang without diagnostics, Flask route tests could touch local runtime config, and stale legacy `AGENTS.md/` guidance could confuse future agent work.

**Dependencies**: `TASK-066`; current CI workflow; route-test coverage; `.github` guidance baseline.

**Current State**:
- PR #19 merged on May 27, 2026, adding pytest timeout safeguards, CI timeout limits, route-test runtime path isolation, and legacy `AGENTS.md/` removal.
- Focused validation passed for Flask routes, runtime/config path helpers, Task-079 reliability coverage, CI workflow summary, `.agent_work` validation, `git diff --check`, and pytest timeout config recognition.
- This task intentionally keeps broader asset-backed package smoke checks advisory unless a later release-gate ratchet promotes them.

**User Value**: Restores confidence in internal validation before external pilot prep and reduces the chance that future agents follow stale instructions.

### **TASK-073: Clean-Machine Pilot / UAT Execution Plan**
**Status**: IN_PROGRESS - post-PR28 prerelease package refresh and final-digest smoke passed; tester cohort and owner/reviewer acceptance pending
**Type**: B/C (User Testing / Release Validation)  
**Priority**: HIGH  
**Estimated Effort**: 0.5-1 day (4-8 hours)  
**Target Sprint**: Sprint 06 V1 RC1  
**Task File**: `.agent_work/tasks/active/TASK-073-clean-machine-uat-plan.md`

**Objective**: Define the controlled pilot/UAT workflow, tester instructions, bootstrap-first acceptance checklist, environment capture, issue-report workflow, success criteria, support escalation path, and first-launch guidance for users without prior command-line experience.

**Dependencies**: `TASK-066`; `TASK-067`; `TASK-071`; `TASK-074`; RC1 user package docs.

**User Value**: Ensures external testing starts from a repeatable, evidence-producing workflow instead of ad hoc feedback collection.

### **TASK-080: RC1 UAT User Guide And Setup Process Simplification**
**Status**: IN_PROGRESS - rc2 release validation passed earlier; pre-UAT follow-up docs/runtime/status-message changes are implemented with focused coverage; live Google first-launch passed after TLS CA support-path validation; Word visual QA and final pre-package validation passed; refreshed rc3 package/image/GitHub prerelease validation passed; final handoff signoff and tester/cohort selection remain pending before external handoff
**Type**: B/C (User Testing / Documentation / Release UX)
**Priority**: HIGH
**Estimated Effort**: 1-2 days (8-16 hours), plus optional launcher follow-through
**Target Sprint**: Sprint 06 V1 RC1 external UAT readiness
**Task File**: `.agent_work/tasks/active/TASK-080-uat-user-guide-process-simplification.md`

**Objective**: Revise the first-cohort RC1 UAT process so non-technical testers receive one clear, start-to-finish user guide instead of several overlapping technical documents. Produce a Microsoft Word RC1 UAT User Guide, simplify the working-folder/download/extraction flow, move manual checksum work toward support fallback or automated setup verification, and expose Podman/GPU validation only as support-assigned optional tracks after the Docker Desktop CPU baseline.

**Current Direction**:
- Introduce `setup-towerscout.cmd` as the normal first-cohort setup command.
- Default to Docker Desktop and `-Gpu off`.
- Auto-discover the Model & Data Package ZIP from the extracted package folder
  or parent `TowerScoutUAT` folder when exactly one matching ZIP is present.
- Keep `-Engine podman`, `-Gpu auto`, and `-Gpu on` for support-assigned
  validation tracks.
- Keep `bootstrap.cmd` as the advanced explicit-path support helper.
- Consolidated Word guide added at
  `.agent_work/user-testing/instructions/TowerScout_V1_RC1_UAT_User_Guide.docx`.
  Owner review in Microsoft Word is still needed because local render QA could
  not run without `pdf2image`/LibreOffice/Word automation.
- Word guide remains outside the release package for now; package-facing
  Markdown/HTML and UAT handoff docs now use the same
  `Documents\TowerScoutUAT` working-folder model.
- Current refreshed UAT release version is `v0.1.0-rc3`, with source ref
  `8ce6375e7f2b74df773e27e4f081e4199eb54a68` and image digest
  `sha256:796e0a7a03d3000199b3a40cc074fa5ca140232706a8747ff4d0eac0e4d85d5f`.
  The GitHub prerelease at
  `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc3` includes
  the four expected rc3 assets. Application Package checksum:
  `d298607b7d7fd2a3d93c6118994e0e139d32626061e39fb950330ea5388e12f0`.
  Model & Data Package checksum:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
  Local Docker validation used isolated project
  `towerscout-task080-rc3-smoke` on port `5016`, and downloaded-release
  validation used isolated project `towerscout-task080-rc3-download` on port
  `5017`; both reached readiness `setup_required` with assets `ok` and were
  stopped afterward.
- Prior corrected UAT release version was `v0.1.0-rc2`, with source ref
  `4e8054d27faa1f956998f85b665a4ea28fc01ed9` and image digest
  `sha256:f3caa7915f7a8d70326b2fa84d62ec86e142c38c7d22615106e192d7f7821946`.
- Local rc2 package generation produced
  `dist\towerscout-v0.1.0-rc2.zip` and
  `dist\towerscout-v0.1.0-rc2-assets-towerscout-v1-assets-2026-05-05.zip`.
  The GitHub prerelease at
  `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc2` includes
  the four expected rc2 assets. Local Docker validation used isolated project
  `towerscout-task080-rc2` on port `5011`, and downloaded-release validation
  used isolated project `towerscout-task080-rc2-download` on port `5012`; both
  reached readiness `setup_required` with assets `ok`. Provider setup and the
  bounded Azure smoke used isolated project
  `towerscout-task080-rc2-provider` on port `5013`, reached readiness
  `ready` with Azure configured and assets `ok`, and completed the public
  Azure fixture with `48` detection records, `8` tile records, right-panel
  address/provider metadata, and elapsed time about `56.38` seconds.
- First-cohort Google setup validation feedback exposed a generic
  `/api/config/validate-key` 502 in the Setup Wizard. The validation path now
  reports provider network/TLS failures with support-safe guidance, the wizard
  continues checking another entered provider if one provider fails, and
  provider key previews were removed from route/browser logs.
- Pre-UAT follow-up changes added a Docker/Podman-running setup reminder,
  command appendix, corrected PubMed research link, concise email/Teams issue
  form, provider-aware normal-mode output-panel messages, and a 12-hour UAT
  stale-container guard that restarts stopped/unhealthy/stale containers while
  preserving named volumes by default.
- Live Google first-launch Setup Wizard verification passed after importing the
  CDC/Zscaler TLS inspection CA into the isolated Docker stack. This confirms
  the repeated Google failure was a managed-network container trust issue, not
  a bad Google key or unresolved Setup Wizard defect.
- Owner-edited Word UAT guide was integrated on 2026-06-10 with formatting and
  readability changes. After a low-level heading correction triggered a Word
  unreadable-content warning, the guide was restored byte-for-byte from the
  Word-authored edited file and required command/TLS/support-safe evidence
  content was structurally verified. Owner completed Microsoft Word visual QA
  on 2026-06-11 and approved locking the guide for final validation.
- Final pre-package validation passed on 2026-06-11 across focused unit,
  release-package, frontend contract, bundle consistency, docs, agent-work,
  whitespace, and targeted secret-safety checks.
- Refreshed rc3 package, image, GitHub prerelease, and downloaded-release setup
  validation passed on 2026-06-11.
- Remaining approval gates are final handoff signoff and tester/cohort
  selection.

**Dependencies**: `TASK-066`; `TASK-071`; `TASK-073`; `TASK-074`; `TASK-075`; possible `TASK-076` provider-key policy language.

**User Value**: Reduces first-cohort UAT friction by turning the validated release package path into a plain-language walkthrough that explains what users are doing, why each step matters, what success looks like, and how to report safe evidence if blocked.

### **TASK-081: RC3 Runtime Hardening And Podman Independence**
**Status**: IN_PROGRESS - runtime defaults, launcher/import hardening, route safety fixes, docs, focused automated validation, live Podman CPU launch/import validation, and live Docker Desktop CPU launch/import validation passed; GPU validation remains blocked pending suitable NVIDIA runtime evidence
**Type**: C (Runtime Hardening / Podman Support / Release Validation)
**Priority**: HIGH
**Estimated Effort**: 2-4 days (16-32 hours), split between CPU-dev-able fixes and hardware-dependent GPU validation
**Target Sprint**: Sprint 06 V1 RC1 / post-rc3 hardening
**Task File**: `.agent_work/tasks/active/TASK-081-rc3-runtime-hardening-podman-independence.md`

**Objective**: Implement the actionable RC3 runtime hardening, Podman independence, launcher/device-integrity, and reviewer-audit recommendations while preserving the CPU-safe UAT baseline and keeping Podman GPU support gated until hardware evidence exists.

**Current Direction**:
- Treat the empirical GPU/Podman replay as the controlling analysis: the observed Docker GPU, Docker CPU, and Podman CPU outputs matched on the same 25-tile fixture, so no model or TF32 precision change is currently justified as the T1000 fix.
- Fix pre-UAT runtime correctness issues first: default image references, restart policy, liveness-based engine selection, and Podman asset import fallback.
- Make selected runtime/device state unmistakable in launcher, import, readiness, and support output so stale containers or mode changes cannot silently reuse the wrong CPU/GPU path.
- Productize Podman CPU independence through an explicit Compose-provider decision, provider/version reporting, focused tests, and documentation that distinguishes package runtime from source-build/TLS caveats.
- Include the small reviewer-audit hardening items that are low-risk and release-relevant: upload filename sanitization, debug Azure route removal, and a pilot tile cap.
- Keep Podman GPU implementation as a gated validation phase, not a support claim, until WSL2/CDI/preflight, parity, timing, and evidence criteria pass.

**Dependencies**: `TASK-066`; `TASK-073`; `TASK-074`; `TASK-075`; `TASK-080`; owner-provided RC3 GPU/Podman and reviewer-audit documents dated 2026-06-11.

**User Value**: Reduces the chance that external UAT is blocked by runtime ambiguity, stale device mode, Podman provider gaps, or known reviewer-audit quick fixes, while preserving honest support boundaries for GPU and Podman.

### **TASK-074: Runtime Prerequisite Preflight**
**Status**: COMPLETED - post-merge package-artifact bootstrap validation passed
**Type**: B/C (Launcher / Supportability / Release UX)
**Priority**: HIGH
**Estimated Effort**: 1-2 days (8-16 hours) for RC1 MVP
**Target Sprint**: Sprint 06 V1 RC1
**Task File**: `.agent_work/tasks/active/TASK-074-runtime-prerequisite-preflight.md`

**Objective**: Implement a Windows package bootstrap/preflight layer that reduces first-launch friction for V1 RC1 users while preserving the validated release package boundaries.

**Current Direction**:
- Keep Docker Desktop as the primary RC1 pilot path.
- Keep Podman as a qualified support-directed path when a running Podman machine and approved Compose provider are available.
- A top-level `bootstrap.cmd` now delegates to `scripts/bootstrap.ps1`, with reusable helper functions in `scripts/lib/TowerScoutBootstrap.ps1`.
- Bootstrap checks engine readiness, Compose availability, WSL/virtualization hints, disk space, port availability, checksums, release/version matching, asset ZIP layout, readiness state, and support-safe next actions.
- Asset ZIP handling now extracts to temporary staging before final promotion so failed manifest/release validation does not leave final asset entries behind.
- A follow-up patch ensures `-VerifyOnly -AssetZip` checks the ZIP without final asset staging and exits before mutation.
- A follow-up patch also initializes package `.env` from `.env.example` before packaged Compose-entry paths start the stack, preventing fresh packages from falling back to the default `latest` image instead of the pinned package digest.
- Bootstrap reuses existing `scripts/import-assets.ps1 -VerifyHashes` and `scripts/launch.ps1`; `start.bat` remains the direct launch path after setup.
- Do not claim hosted asset download, native installer behavior, OCI image archives, Docker-Desktop-free Podman beyond validated boundaries, or GPU support beyond `TASK-075` evidence.

**Dependencies**: `TASK-071`; `TASK-073`; `TASK-066`; `TASK-075`; current launch/import/status scripts.

**User Value**: Converts the most error-prone first-launch checks into guided, plain-English support output before broad external UAT, reducing the chance that non-command-line users get stuck on engine setup, release-file mismatch, asset layout, or readiness interpretation.

---

## Policy Lane Candidates

These tasks are important for V1 RC1, but they are not yet active task files in this planning update. Pull them into `current-tasks.md` and create active task docs if owner/legal availability or release risk requires formal Sprint 06 commitment.

| Task | Recommended Handling | Reason |
|---|---|---|
| `TASK-076` Provider API Key Exposure And Restriction Policy | Candidate for parallel Sprint 06 work | Browser map SDK keys remain client-visible; v1 needs an approved restriction/support policy or an engineering blocker. AGPL does not change provider/API terms. |

---

## Backlog Candidates To Watch

Do not forget these follow-through tasks. They are intentionally kept in `.agent_work/task-backlog.md` rather than pulled into the active sprint now, but `TASK-066` findings may justify selecting one or more before external UAT.

| Task | Pull Into Sprint 06 If | Notes |
|---|---|---|
| `TASK-068` Windows Test Portability And Script Validation | Script validation remains environment-sensitive, Flask route tests load local runtime config, or PowerShell/Windows coverage is needed before external UAT. | Useful release-support follow-through, especially around Windows-first helper scripts and isolating tests from local `.env`, logs, uploads, sessions, and cache paths. |
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

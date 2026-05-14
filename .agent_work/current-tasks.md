# Current Tasks - Active Sprint

**Sprint Period**: Sprint 06 planning / V1 RC1 readiness begins May 11, 2026  
**Last Updated**: May 14, 2026
**Focus**: Produce a V1 RC1 / pilot-ready AGPL-compliant YOLO-enabled release path by closing release-support carry-forward work, correcting release compliance artifacts, writing package-based end-user docs, validating the clean-machine release candidate, and preparing pilot / UAT execution.
**Status**: Sprint 06 committed lane selected. `TASK-065` and `TASK-072` are completed and remain in the active task folder until sprint closeout; `TASK-069` sign-off is sufficient to merge PR #11 as the internal controlled AGPL-governed RC planning and compliance baseline; `TASK-071` is the next documentation dependency; `TASK-066` and `TASK-073` remain selected for Sprint 06.

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

### **TASK-071: End-User Release Package Documentation**
**Status**: NOT_STARTED - selected for Sprint 06  
**Type**: B/C (Documentation / User Enablement)  
**Priority**: CRITICAL  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 06 V1 RC1  
**Task File**: `.agent_work/tasks/active/TASK-071-end-user-release-docs.md`

**Objective**: Produce the package-based quick start and full user guide that tell a non-technical Windows pilot user what to download, where assets go, how to launch, how to configure provider keys, how to validate success, how to find source/license notices, and how to report problems.

**Dependencies**: `TASK-069`; `TASK-072`; release package shape; current OCI quick-start/runtime docs.

**User Value**: Converts the engineered release package into a self-service pilot path instead of a support-only handoff.

### **TASK-066: Release Candidate Validation Gate**
**Status**: NOT_STARTED - selected for Sprint 06  
**Type**: C (Release Engineering / Validation)  
**Priority**: CRITICAL  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 06 V1 RC1  
**Task File**: `.agent_work/tasks/active/TASK-066-release-candidate-validation-gate.md`

**Objective**: Internally prove the release package, asset bundle, docs, setup flow, restart persistence, and bounded detection path from a clean user-facing environment before external pilot/UAT begins.

**Dependencies**: `TASK-065`; `TASK-069`; `TASK-071`; `TASK-072`; agreed release package shape.

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
| `TASK-075` GPU / CUDA Support Decision | Candidate for early Sprint 06 decision | V1 should explicitly be CPU-only or document a validated CUDA support path. This should stay a decision task unless implementation is intentionally selected. |

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

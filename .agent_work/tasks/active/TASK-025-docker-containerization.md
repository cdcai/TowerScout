# TASK-025: Docker Containerization

**Status**: NOT_STARTED  
**Priority**: HIGH  
**Type**: C (Infrastructure / Deployment Readiness)  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 05 extension after `TASK-063` and `TASK-064`

## Objective

Create the Docker runtime baseline for TowerScout's supported v1 local deployment path on top of the corrected Sprint 05 runtime, smoke-test baseline, pre-Docker release-hardening gate, and targeted responsiveness/performance gate.

`TASK-025` is the container build/run and persistence task. It must not absorb launcher UX, background jobs, native installer work, broad backend decomposition, or release-hardening items owned by `TASK-063`.

## V1 Scope Assumptions

- Single-user local deployment only.
- Windows/AMD64 is the first supported user target.
- Normal outbound internet access is required.
- CPU execution is the supported baseline.
- NVIDIA/CUDA is optional acceleration on compatible AMD64 hosts.
- Docker is the first runtime baseline, not the final managed installer.
- Mac, ARM64, offline, air-gapped, VDI, shared multi-user, and native installer promises are out of scope for this task.

## Requirements (EARS Notation)

**R-025-001**: WHEN Docker work begins, THE PROJECT SHALL have completed `TASK-063` and `TASK-064` or recorded owner-approved risk acceptance for any unresolved pre-Docker gate item.

**R-025-002**: WHEN TowerScout is built as a container, THE SYSTEM SHALL provide a Dockerfile and Compose configuration that run the corrected Flask/Waitress application baseline.

**R-025-003**: WHEN the container is restarted or replaced, THE SYSTEM SHALL preserve required durable state including `webapp/config/`, stable `FLASK_SECRET_KEY`, downloaded runtime assets, user exports/imported datasets, and support-relevant logs.

**R-025-004**: WHEN runtime directories are mounted, THE SYSTEM SHALL classify each path as restart/update-durable, writable runtime state, or cleanup-safe/best-effort state in a versioned v1 runtime/persistence contract.

**R-025-005**: WHEN first-run runtime assets are missing, THE SYSTEM SHALL either bootstrap them into persistent storage or fail with actionable recovery guidance.

**R-025-006**: WHEN Docker validation runs, THE SYSTEM SHALL reuse the `TASK-052` smoke contract against the containerized app rather than creating an unrelated Docker-only validation path.

**R-025-007**: WHEN Setup Wizard or Settings saves configuration in Docker, THE SYSTEM SHALL persist the saved configuration across container restarts.

**R-025-008**: WHEN the launcher task consumes the Docker baseline, THE SYSTEM SHALL expose a clear health/readiness contract suitable for host-side polling.

**R-025-009**: WHEN release documentation describes supported hosts, THE PROJECT SHALL state Windows/AMD64 CPU baseline support and label GPU, Mac, ARM64, offline, and shared-deployment behavior accurately.

**R-025-010**: WHEN cache and geocode data are mapped in Docker, THE PROJECT SHALL explicitly decide whether each cache class is durable, best-effort, or cleanup-safe for v1.

**R-025-011**: WHEN Docker config exposes request-body or upload-size behavior, THE SYSTEM SHALL preserve the upload-limit policy decided in `TASK-063`.

## Acceptance Criteria

- [ ] `TASK-063` and `TASK-064` completed, or unresolved items documented as owner-approved risk acceptances before Docker implementation starts.
- [ ] Dockerfile exists and builds from a clean checkout with documented prerequisites.
- [ ] Compose configuration exists for supported local deployment.
- [ ] Versioned v1 runtime/persistence contract exists and covers config, secret key, assets, exports/imports, logs, sessions, temp, uploads, cache, and geocode data.
- [ ] Cache and geocode data are classified as durable, best-effort, or cleanup-safe for v1.
- [ ] Stable `FLASK_SECRET_KEY` behavior is documented and validated across restart.
- [ ] Setup Wizard works in the container.
- [ ] Settings save/load persists across container restart.
- [ ] First-run asset inventory and bootstrap/recovery behavior are documented.
- [ ] Detection workflow smoke path runs in the container.
- [ ] Container health/readiness behavior is available for `TASK-054`.
- [ ] Unsupported v1 environments are documented and not implied as supported.
- [ ] Docker runtime configuration preserves the upload-limit/request-body policy decided in `TASK-063`.

## Dependencies

- `TASK-052`: Current integration smoke-test baseline
- `TASK-056`: First-run reliability and runtime determinism hardening
- `TASK-057`: Local YOLO runtime ownership and Torch Hub independence
- `TASK-062`: Pre-Docker runtime cleanup and YOLO loader hardening
- `TASK-063`: Pre-Docker release hardening and CI reproducibility gate
- `TASK-064`: Targeted runtime responsiveness and inference baseline

## Implementation Plan

1. Confirm `TASK-063` and `TASK-064` completion/risk-acceptance status, including owner approval for any accepted unresolved item.
2. Write the versioned Docker runtime contract: supported host, persistence map, cache/geocode durability decision, asset strategy, health/readiness behavior, upload-limit behavior, and validation path.
3. Implement Dockerfile and Compose using the normalized `webapp/` runtime contract.
4. Validate Setup Wizard, Settings persistence, stable secret-key behavior, first-run asset behavior, and detection smoke.
5. Document user-facing Docker run/recovery guidance and hand off launcher requirements to `TASK-054`.

---

## Implementation Log

### 2026-04-28 - Task File Creation
**Objective**: Create task-specific documentation for the Docker baseline after the plan sufficiency review.  
**Context**: `TASK-025` existed in `current-tasks.md` but did not have an individual active task file. The latest review confirmed Docker-first sequencing while requiring clearer v1 runtime, persistence, asset, and support contracts.  
**Decision**: Keep `TASK-025` focused on container build/run behavior and require the v1 runtime contract before implementation is considered complete.  
**Execution**: Created this task file with EARS requirements, acceptance criteria, dependencies, and implementation plan.  
**Output**: `TASK-025` now has task-specific active documentation.  
**Validation**: Pending `.agent_work` structure validation.  
**Next**: Start only after `TASK-063` clears or records owner-approved explicit risk acceptance.

### 2026-04-28 - Final Path-Forward Review Expansion
**Objective**: Tighten the Docker runtime contract around persistence versioning, cache/geocode state, and upload limits.  
**Context**: The final path-forward review agreed with Docker sequencing but recommended making the persistence map a formally versioned v1 contract and aligning Docker runtime behavior with upload-limit decisions.  
**Decision**: Keep these requirements in `TASK-025` because they define container runtime behavior after `TASK-063` sets policy.  
**Execution**: Added EARS requirements and acceptance criteria for versioned persistence, cache/geocode classification, and upload-limit preservation.  
**Output**: `TASK-025` now requires Docker to implement the v1 runtime contract explicitly.  
**Validation**: `.agent_work` validation passed after synchronized planning updates.  
**Next**: Start only after `TASK-063` and `TASK-064` clear or record owner-approved explicit risk acceptance.

### 2026-04-28 - Owner Approval Rule
**Objective**: Prevent Docker work from starting on implicit risk acceptance.  
**Context**: The project owner confirmed they will approve risk acceptances when given enough context to understand the decision and consequences.  
**Decision**: Treat owner-approved risk notes as required evidence for any unresolved `TASK-063` or `TASK-064` item before `TASK-025` starts.  
**Execution**: Updated requirements, acceptance criteria, dependencies, and implementation plan to require owner-approved risk acceptance before Docker implementation begins.  
**Output**: Docker start criteria now require either cleared pre-Docker gates or documented owner approval for accepted residual risk.  
**Validation**: `.agent_work` validation passed after synchronized planning updates.  
**Next**: Confirm gate status before starting Docker implementation.

---

## Validation Results

Pending implementation.

# TASK-063: Pre-Docker Release Hardening And CI Reproducibility Gate

**Status**: NOT_STARTED  
**Priority**: CRITICAL  
**Type**: C (Security / Release Engineering / Deployment Readiness)  
**Estimated Effort**: 1-2 days (8-16 hours)

## Objective

Resolve or owner-approve the April 24 senior-review release-hardening findings and the April 28 plan-sufficiency execution gates before `TASK-025` turns the current host runtime into the Docker baseline.

This task exists because the senior reviews found release-quality risks that are adjacent to Docker but should not be folded into Docker implementation itself. The latest sufficiency review confirmed that the plan is sound, but only if the v1 release boundary, CI/security posture, persistence expectations, support diagnostics, and unsupported environments are explicit before Docker work proceeds.

## Requirements (EARS Notation)

**R-063-001**: WHEN TowerScout prepares for Docker baseline work, THE SYSTEM SHALL use dependency versions that have been reviewed for currently flagged security findings.

**R-063-002**: WHEN frontend dependencies are installed for validation or release packaging, THE PROJECT SHALL have an explicit lockfile/reproducibility policy reflected in tracked files or documented as a deliberate exception.

**R-063-003**: WHEN CI security scanning runs, THE WORKFLOW SHALL NOT reference `aquasecurity/trivy-action` through a floating branch such as `@master`.

**R-063-004**: WHEN CI results are used to support release readiness, THE PROJECT SHALL identify which checks are advisory and which checks must block release candidates.

**R-063-005**: WHEN the application is packaged for local users, THE SYSTEM SHALL either disable `.pt` model upload or clearly gate/document it as a trusted local-admin/developer workflow.

**R-063-006**: WHEN TLS verification is disabled through `TOWERSCOUT_ALLOW_INSECURE_TLS`, THE SYSTEM SHALL treat that mode as an explicit local troubleshooting exception, not a normal supported runtime default.

**R-063-007**: WHEN performance metrics are written or read, THE SYSTEM SHALL use one authoritative file-format contract for each performance log file.

**R-063-008**: WHEN third-party GitHub Actions are used in release-relevant workflows, THE WORKFLOW SHALL pin them to reviewed immutable references or record owner-approved explicit risk acceptance.

**R-063-009**: WHEN workflow permissions are evaluated for release readiness, THE PROJECT SHALL document whether permissions are minimal enough for the current CI jobs or record follow-up hardening.

**R-063-010**: WHEN the active YOLO runtime is audited before Docker, THE PROJECT SHALL prove that no supported runtime path falls back to Torch Hub, GitHub bootstrap, or stale legacy inference behavior.

**R-063-011**: WHEN v1 local release scope is documented, THE PROJECT SHALL state the supported and unsupported environments before Docker packaging begins.

**R-063-012**: WHEN support readiness is evaluated, THE PROJECT SHALL define the minimum v1 support contract for log locations, asset/version visibility, startup diagnostics, and sensitive-data handling.

**R-063-013**: WHEN third-party GitHub Actions are pinned to immutable references, THE PROJECT SHALL define a recurring review/update cadence so pinned actions do not silently drift out of maintenance.

**R-063-014**: WHEN provider API keys are documented for v1, THE PROJECT SHALL describe provider-side restriction guidance, including separation of browser-exposed and server-side key usage where applicable.

**R-063-015**: WHEN upload surfaces remain enabled, THE PROJECT SHALL align Flask upload limits, Waitress request-body limits, and the `.pt` upload support boundary.

**R-063-016**: WHEN dependency repeatability is documented, THE PROJECT SHALL decide the immediate Python, frontend, and runtime-asset repeatability policy rather than relying only on top-level version pins.

**R-063-017**: WHEN an unresolved pre-Docker finding is risk-accepted, THE PROJECT SHALL document the issue, deferral rationale, expected user/release impact, mitigation or workaround, review timing, follow-up owner/task, and owner approval before `TASK-025` starts.

## Acceptance Criteria

- [ ] `webapp/requirements.txt` has been reviewed and patched for the currently flagged Pillow/Requests findings, or an explicit risk-acceptance note exists.
- [ ] `package-lock.json` is either committed and used as the frontend install contract, or the repo documents why it remains untracked and what replaces it.
- [ ] `.github/workflows/ci.yml` no longer uses `aquasecurity/trivy-action@master`.
- [ ] Release-relevant third-party GitHub Actions are pinned to reviewed immutable references, or each exception has owner-approved explicit risk acceptance.
- [ ] A recurring review/update cadence exists for pinned third-party GitHub Actions.
- [ ] Workflow permissions have been reviewed and documented for release readiness.
- [ ] The CI workflow has a documented release-candidate interpretation for advisory versus blocking checks.
- [ ] Dependency repeatability policy is documented for Python dependencies, frontend dependencies, and large runtime assets.
- [ ] Residual YOLO/Torch Hub audit proves no supported runtime path falls back to Torch Hub, GitHub bootstrap, or stale legacy inference behavior.
- [ ] The `.pt` model upload route has a documented first-release support boundary and, if needed, a code-side gate or disable path.
- [ ] Flask upload limits, Waitress request-body limits, and `.pt` upload support boundary are aligned or owner-approved as a follow-up risk.
- [ ] Provider API key restriction guidance is documented for Google and Azure, including client/server separation where applicable.
- [ ] Insecure TLS flags remain off by default and are documented as local troubleshooting exceptions.
- [ ] `performance.log` is no longer both a structured logging target and a CSV metrics target.
- [ ] V1 supported and unsupported environments are documented for release planning.
- [ ] Minimum support diagnostics contract is documented for log locations, startup failures, asset/version visibility, and sensitive-data handling.
- [ ] Any unresolved `TASK-063` item has an owner-approved risk note covering impact, mitigation, follow-up timing, and owning task before `TASK-025` starts.
- [ ] Focused validation is recorded in this task file before `TASK-025` starts.

## Dependencies

- `TASK-052`: Current integration smoke-test baseline
- `TASK-062`: Pre-Docker runtime cleanup and YOLO loader hardening

## Implementation Plan

1. Audit the current repo state for the review findings: dependency versions, frontend lockfile policy, dependency repeatability, CI action pinning, pinned-action review cadence, workflow permissions, advisory gates, residual YOLO/Torch Hub behavior, model upload and upload-size limits, provider-key restriction guidance, TLS bypass, performance-log file contract, v1 support boundary, and support diagnostics.
2. Apply minimal fixes where the fix is low risk and clearly bounded.
3. For any item that cannot be fixed safely before Docker work, document the owner-approved risk acceptance, impact, mitigation, follow-up timing, and follow-up task owner.
4. Run focused validation for touched areas.
5. Update `current-tasks.md` / Sprint 05 planning if any acceptance item changes Docker scope or timing.

---

## Implementation Log

### 2026-04-28 - Task Creation
**Objective**: Add a bounded pre-Docker release-hardening gate based on the second senior-engineer review.  
**Context**: The review agreed with Docker-first sequencing but identified release-quality risks around dependency freshness, frontend reproducibility, CI action pinning, advisory CI gates, `.pt` model upload, TLS bypass behavior, and performance-log file ownership.  
**Decision**: Track these as `TASK-063` before `TASK-025` so Docker remains focused on container build/run behavior while release-hardening risks are handled deliberately.  
**Execution**: Created this task file and linked it from `current-tasks.md`, `task-backlog.md`, and the Sprint 05 plan.  
**Output**: `TASK-063` now gates Docker start.  
**Validation**: Planning artifact review pending.  
**Next**: Execute the audit/fix pass and record validation evidence here.

### 2026-04-28 - Sufficiency Review Gate Expansion
**Objective**: Incorporate the April 28 plan sufficiency assessment into the pre-Docker gate.  
**Context**: The sufficiency assessment concluded that the plan is strong enough to proceed if v1 scope stays narrow and operational contracts are explicit before implementation hardens into release artifacts.  
**Decision**: Expand `TASK-063` to include third-party action pinning beyond Trivy, workflow permission review, residual YOLO/Torch Hub audit, v1 supported/unsupported environment documentation, and minimum support diagnostics.  
**Execution**: Updated requirements, acceptance criteria, and implementation plan in this task file.  
**Output**: `TASK-063` now captures the release, security, and support gates that must clear before Docker starts.  
**Validation**: `.agent_work` validation passed after synchronized planning updates.  
**Next**: Execute the audit/fix pass and record concrete validation evidence here.

### 2026-04-28 - Final Path-Forward Review Expansion
**Objective**: Capture the final review's release-engineering and supportability constraints.  
**Context**: The reviewer agreed with the roadmap but identified four additional pre-Docker contract details: pinned-action review cadence, upload-limit alignment, provider-key restriction guidance, and stronger dependency repeatability decisions.  
**Decision**: Keep these in `TASK-063` because they are release/security/support gates, not Docker implementation.  
**Execution**: Added requirements and acceptance criteria for action update cadence, provider-key restrictions, upload limit alignment, and dependency repeatability.  
**Output**: `TASK-063` now reflects the final review's release gate refinements.  
**Validation**: `.agent_work` validation passed after synchronized planning updates.  
**Next**: Execute the audit/fix pass and record concrete validation evidence here.

### 2026-04-28 - Owner Approval Rule
**Objective**: Make pre-Docker risk acceptance governance explicit.  
**Context**: The project owner confirmed they will approve risk acceptances when given enough context to understand the decision and consequences.  
**Decision**: Require owner-approved risk notes for unresolved `TASK-063` findings before Docker starts.  
**Execution**: Added an EARS requirement, acceptance criterion, and implementation-plan language requiring issue, deferral rationale, impact, mitigation, review timing, follow-up owner/task, and owner approval.  
**Output**: `TASK-063` can no longer proceed through implicit risk acceptance.  
**Validation**: Pending `.agent_work` validation after synchronized planning updates.  
**Next**: Apply this rule during the audit/fix pass.

---

## Validation Results

Pending implementation.

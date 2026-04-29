# TASK-054: Local Launch UX

**Status**: NOT_STARTED  
**Priority**: MEDIUM  
**Type**: B (Deployment UX / Local Supportability)  
**Estimated Effort**: 1-2 days (8-12 hours)  
**Target Sprint**: Sprint 05 stretch after `TASK-025`

## Objective

Deliver a launcher-first local startup and support flow over the Docker baseline so a supported Windows/AMD64 local user can start, stop, inspect status/logs, and open TowerScout without relying on raw Docker CLI workflows.

`TASK-054` is the local UX layer over Docker. It must not become Docker implementation, native installer work, cross-platform packaging, or background-job architecture.

## Requirements (EARS Notation)

**R-054-001**: WHEN a supported Windows local user launches TowerScout, THE SYSTEM SHALL provide a host-side launcher path beginning with `start.bat`.

**R-054-002**: WHEN the launcher starts TowerScout, THE SYSTEM SHALL wait for application shell readiness before opening the browser.

**R-054-003**: WHEN Docker is running but the application is not ready, THE SYSTEM SHALL distinguish container startup from application readiness.

**R-054-004**: WHEN first-run asset bootstrap is still in progress or has failed, THE SYSTEM SHALL surface actionable status instead of hiding the delay behind a generic startup wait.

**R-054-005**: WHEN users need routine support actions, THE SYSTEM SHALL provide documented or scripted start, stop, logs, and status paths.

**R-054-006**: WHEN startup fails, THE SYSTEM SHALL provide troubleshooting guidance for Docker not running, port conflicts, startup timeout, failed first-run asset bootstrap, restricted network behavior, and provider-key failures.

**R-054-007**: WHEN support information is requested, THE PROJECT SHALL document log locations and version/asset manifest collection steps.

**R-054-008**: WHEN unsupported environments are discussed, THE PROJECT SHALL state that Mac, ARM64, offline, air-gapped, shared deployment, and native installer behavior are not v1 support promises.

## Acceptance Criteria

- [ ] `start.bat` or equivalent Windows-first launcher exists.
- [ ] Launcher waits for app readiness before opening the browser.
- [ ] Stop/logs/status support exists as scripts or clear user-facing guidance.
- [ ] First-run asset/bootstrap delay and failure handling is visible to users.
- [ ] Troubleshooting docs cover Docker, port, timeout, network, asset, and provider-key failures.
- [ ] Log locations and version/asset manifest collection guidance are documented.
- [ ] Unsupported v1 environments are documented without implying support.
- [ ] Launcher behavior is validated against the Docker baseline from `TASK-025`.

## Dependencies

- `TASK-025`: Docker containerization baseline
- `TASK-063`: Pre-Docker release hardening and CI reproducibility gate

## Implementation Plan

1. Confirm `TASK-025` exposes a stable container start command and readiness behavior.
2. Implement Windows-first launcher script and companion stop/logs/status path.
3. Add browser-open behavior only after readiness succeeds.
4. Add first-run asset/bootstrap status and failure guidance.
5. Document routine startup, shutdown, support-log, and troubleshooting flows.
6. Validate clean first launch, repeat launch, startup timeout, and Docker-not-running behavior.

---

## Implementation Log

### 2026-04-28 - Task File Creation
**Objective**: Create task-specific documentation for the local launcher/support UX layer.  
**Context**: `TASK-054` existed in `current-tasks.md` as a post-Docker stretch task but did not have an individual active task file. The latest review emphasized support diagnostics and operational clarity as v1 success criteria.  
**Decision**: Keep `TASK-054` as the post-Docker local UX/support layer, with explicit boundaries against installer and architecture work.  
**Execution**: Created this task file with EARS requirements, acceptance criteria, dependencies, and implementation plan.  
**Output**: `TASK-054` now has task-specific active documentation.  
**Validation**: Pending `.agent_work` structure validation.  
**Next**: Start only after the Docker baseline is stable enough to target.

---

## Validation Results

Pending implementation.

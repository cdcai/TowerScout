# TASK-064: Targeted Runtime Responsiveness And Inference Baseline

**Status**: NOT_STARTED  
**Priority**: HIGH  
**Type**: B/C (Runtime Responsiveness / Performance Validation)  
**Estimated Effort**: 0.5-1 day (4-8 hours)  
**Target Sprint**: Sprint 05 extension / pre-`TASK-025` sign-off gate

## Objective

Address the final path-forward review's low-cost, high-value runtime concerns before Docker turns the current behavior into the v1 baseline.

This task is intentionally narrow. It is not frontend build modernization, broad CPU optimization, background-job implementation, or backend decomposition. It only covers:

- ProviderStateManager busy-wait / main-thread responsiveness cleanup
- a focused `torch.inference_mode()` benchmark on the active inference path
- a documented apply/defer decision based on measured risk and value

## Requirements (EARS Notation)

**R-064-001**: WHEN ProviderStateManager controls provider switching, THE FRONTEND SHALL avoid main-thread busy-wait locking patterns that can degrade responsiveness or deadlock workflow state.

**R-064-002**: WHEN the provider-switching cleanup lands, THE SYSTEM SHALL preserve current Google/Azure provider switching, map readiness, and user-facing detection behavior.

**R-064-003**: WHEN inference performance is evaluated, THE PROJECT SHALL benchmark the active CPU baseline with and without `torch.inference_mode()` using a bounded under-100-tile workload or an equivalent repeatable local inference fixture.

**R-064-004**: WHEN the inference benchmark completes, THE PROJECT SHALL either apply a low-risk improvement or document why the change is deferred to `TASK-026`.

**R-064-005**: WHEN validation completes, THE PROJECT SHALL record frontend build/provider validation and inference benchmark evidence before `TASK-025` sign-off.

**R-064-006**: WHEN a `TASK-064` finding is risk-accepted instead of fixed, THE PROJECT SHALL document the issue, deferral rationale, expected user/release impact, mitigation or workaround, review timing, follow-up owner/task, and owner approval before `TASK-025` starts.

## Acceptance Criteria

- [ ] ProviderStateManager busy-wait / boolean lock loop behavior is removed, replaced with a bounded event/promise/state transition, or owner-approved with evidence.
- [ ] Current Google and Azure provider switching behavior is preserved.
- [ ] `node webapp/build.js` succeeds after frontend changes.
- [ ] A focused provider/browser smoke or equivalent validation is recorded for the touched frontend path.
- [ ] `torch.inference_mode()` benchmark evidence is recorded against the active inference path.
- [ ] Decision recorded: apply now, defer to `TASK-026`, or reject based on measured behavior.
- [ ] Any unresolved `TASK-064` item has an owner-approved risk note covering impact, mitigation, follow-up timing, and owning task before `TASK-025` starts.
- [ ] Any code changes include focused tests or documented manual validation appropriate to the touched surface.

## Dependencies

- `TASK-052`: Current integration smoke-test baseline
- `TASK-057`: Local YOLO runtime ownership and Torch Hub independence
- `TASK-062`: Pre-Docker runtime cleanup and YOLO loader hardening
- `TASK-063`: Pre-Docker release hardening and CI reproducibility gate

## Implementation Plan

1. Inspect `webapp/js/src/managers/ProviderStateManager.js` and related provider-switch call sites.
2. Replace any true busy-wait locking behavior with bounded state transition logic that does not block the browser main thread.
3. Rebuild frontend assets and validate provider switching behavior.
4. Build a narrow `torch.inference_mode()` benchmark around the active YOLO/EfficientNet inference path or a repeatable local fixture.
5. Record benchmark results and decide whether to apply the optimization immediately or defer it to `TASK-026`.
6. If a finding is accepted rather than fixed, document the owner-approved risk note before `TASK-025` starts.
7. Update task evidence and hand off any remaining performance work to `TASK-026`.

---

## Implementation Log

### 2026-04-28 - Task Creation
**Objective**: Add a bounded runtime responsiveness and inference baseline gate based on the final path-forward review.  
**Context**: The reviewer agreed with the roadmap but identified ProviderStateManager busy-wait behavior and `torch.inference_mode()` validation as low-cost, high-value items that should move earlier than broad frontend modernization or CPU optimization.  
**Decision**: Track this as `TASK-064` so the work does not get hidden inside Docker, `TASK-060`, or `TASK-026`.  
**Execution**: Created this active task file with EARS requirements, acceptance criteria, dependencies, and implementation plan.  
**Output**: `TASK-064` now gates Docker sign-off and is sequenced after `TASK-063` in Sprint 05 planning.  
**Validation**: `.agent_work` validation passed after synchronized planning updates.  
**Next**: Execute after `TASK-063` resolves or explicitly accepts release-hardening findings, before `TASK-025` starts.

### 2026-04-28 - Owner Approval Rule
**Objective**: Make pre-Docker risk acceptance governance explicit for the targeted responsiveness/performance gate.  
**Context**: The project owner confirmed they will approve risk acceptances when given enough context to understand the decision and consequences.  
**Decision**: Require owner-approved risk notes for unresolved `TASK-064` findings before Docker starts.  
**Execution**: Added an EARS requirement, acceptance criterion, and implementation-plan step requiring issue, deferral rationale, impact, mitigation, review timing, follow-up owner/task, and owner approval.  
**Output**: `TASK-064` can no longer proceed through implicit risk acceptance.  
**Validation**: `.agent_work` validation passed after synchronized planning updates.  
**Next**: Apply this rule if either targeted finding is deferred or accepted rather than fixed.

---

## Validation Results

### 2026-04-28 - Planning Documentation Validation

**Command**: `python .agent_work/scripts/validate_agent_work.py`  
**Result**: Passed.  
**Scope**: Confirms the new task file and synchronized planning documentation are structurally valid. Runtime implementation and benchmark validation remain pending.

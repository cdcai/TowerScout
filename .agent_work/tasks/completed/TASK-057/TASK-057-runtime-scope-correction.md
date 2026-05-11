# TASK-057 Runtime Scope Correction

### Decision - 2026-04-13
**Decision**: Narrow `TASK-057` from an "offline readiness" framing to a TowerScout-owned YOLO runtime contract that removes `torch.hub` and GitHub from model initialization at runtime.
**Context**: `TASK-057`, `current-tasks.md`, and the Sprint 05 plan had started to imply that Sprint 05 required TowerScout to work fully offline. That is stronger than the actual product contract. TowerScout's core user workflow still depends on external mapping and geocoding providers, so normal detection runs remain network-dependent even if YOLO initialization becomes fully local. The real blocker before `TASK-052` and `TASK-025` is not full-app offline behavior; it is the remaining structural dependence on Torch Hub cache state, GitHub availability, and upstream bootstrap behavior during YOLO model load.
**Options**:
- Keep the existing offline-readiness framing.
  - Pro: pushes toward a stronger deployment story.
  - Con: overstates the current product requirement and implies guarantees the provider-backed workflow cannot actually meet.
- Defer `TASK-057` and accept the current pinned `torch.hub` path.
  - Pro: avoids a larger runtime change in Sprint 05.
  - Con: leaves Docker and smoke-baseline work tied to a runtime contract TowerScout does not fully own.
- Narrow `TASK-057` to local YOLO runtime ownership and first-run independence from Torch Hub / GitHub.
  - Pro: matches the real engineering blocker, preserves deterministic model initialization as the Sprint 05 gate, and avoids claiming full-offline capability for the whole app.
  - Con: does not solve broader offline deployment goals if those become a future product requirement.
**Rationale**: The third option is the correct Sprint 05 scope. It preserves the important reliability and deployment goal: TowerScout should own the inference code it runs, and YOLO initialization should not depend on Torch Hub cache state or first-run GitHub access. At the same time, it stops the planning artifacts from implying a full-offline application contract that is inconsistent with live provider-backed imagery and geocoding workflows.
**Impact**: `TASK-057`, `current-tasks.md`, and the Sprint 05 plan should describe the task as local YOLO runtime ownership plus Torch Hub / GitHub-independent initialization. Validation should prove that YOLO model load no longer contacts Torch Hub or GitHub. The task should explicitly avoid claiming that TowerScout's end-to-end detection workflow works offline in all contexts. If true offline operation later becomes a product requirement, it should be defined as a separate architectural decision covering provider strategy, cached imagery, geocoding behavior, and deployment constraints beyond YOLO loader ownership.
**Review**: Reassess this decision only if TowerScout adopts an explicit offline or air-gapped deployment target, or if Sprint 05 discovers that Docker or smoke-baseline validation still requires a broader runtime-network decision beyond YOLO initialization.

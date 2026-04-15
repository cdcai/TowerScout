# Sprint 05 Plan - Runtime Determinism, Docker Readiness, and Local Launch Foundations

**Sprint Period**: April 7 - April 25, 2026 (19 days)  
**Planning Date**: April 6, 2026  
**Updated Through**: April 13, 2026  
**Sprint Focus**: Runtime hardening, reproducible inference, Docker readiness, and bounded local launch UX follow-through  
**Target Capacity**: 70-80 hours  
**Expected Bundle Growth**: +10-20 KB (infrastructure-heavy sprint)

---

## Plan Authority

This file is the authoritative Sprint 05 plan.

It supersedes the historical planning snapshot in [SPRINT-PLANNING-SESSION-2026-04-06.md](./SPRINT-PLANNING-SESSION-2026-04-06.md) wherever the two differ.

The main Sprint 05 plan updates since the April 6 planning session are:

1. `TASK-056` now exists as the explicit first-run reliability and runtime-determinism gate before the smoke baseline.
2. `TASK-057` now exists as the explicit local YOLO runtime ownership task before the smoke baseline and Docker work.
3. `TASK-054` remains a post-Docker stretch task for launch UX, and `TASK-029` stays behind it.
4. Runtime path normalization remains pre-sprint closeout work, not active Sprint 05 feature delivery.
5. The detailed Sprint 05 scope is synchronized with [current-tasks.md](../../current-tasks.md).

---

## Sprint Objectives

### Primary Goal

Deliver Docker containerization (`TASK-025`) only after the runtime contract is corrected, locally owned, and validated through a current smoke-test baseline.

### Secondary Goals

1. Keep `TASK-051` and `TASK-055` as the completed Sprint 05 foundation.
2. Complete `TASK-056` first-run reliability and runtime determinism hardening.
3. Complete `TASK-057` local YOLO runtime ownership and Torch Hub independence.
4. Complete `TASK-052` current integration smoke-test baseline on the corrected runtime.
5. Deliver `TASK-054` local launch UX MVP only if Docker baseline work lands cleanly.
6. Consider `TASK-029`, `TASK-026`, or deferred Sprint 04 quick wins only if capacity remains.

### Planning Assumptions

- Plan around a sustainable pace of roughly `3.5-4.0 hrs/day`, not Sprint 03 peak velocity.
- Keep Sprint 05 weighted toward runtime correction, validation, and deployment readiness, not broad frontend feature work.
- Treat smaller bundle growth as the expected outcome unless `TASK-054` expands into frontend warm-start UX.

---

## Scope Boundaries

### What Sprint 05 Must Deliver

- Confirm actual runtime dependencies before containerization.
- Correct the confirmed first-run and runtime-determinism blockers before defining the smoke baseline.
- Replace the remaining Hub/GitHub YOLO runtime dependency with a TowerScout-owned local loader.
- Rebuild the smoke-test baseline around the current live app boot and route surface.
- Deliver Docker build/run behavior with persistent state mounted correctly.
- Preserve Setup Wizard, Settings, and current detection workflow behavior in the Docker environment.

### What Sprint 05 Should Not Quietly Absorb

- Broad architecture rewrite beyond `TASK-056` and `TASK-057`
- Large validation-harness rewrites beyond `TASK-052`
- Startup-pipeline redesign folded into `TASK-025`
- Multi-provider fallback as an assumed in-sprint commitment

### Explicit Scope Boundary

`TASK-056` owns immediate first-run/runtime hardening.  
`TASK-057` owns local YOLO runtime ownership.  
`TASK-025` owns container build/run behavior.  
`TASK-054` owns launcher, browser-open behavior, readiness polling, and any follow-on startup UX.

---

## Prerequisites and Carry-In Context

### Completed Before Sprint 05 Delivery Work

- `PRE-SPRINT-05-01` runtime path normalization is complete.
- Canonical app-anchored runtime directories now exist under `webapp/`.
- Docker mount planning should use normalized `webapp/` paths, not historical mixed root behavior.

### Closeout Still Worth Tracking

- `PRE-SPRINT-05-02` closeout cleanup and validation is complete.
- Its outcomes should stay separate from `TASK-025` so Docker decisions do not get mixed with repo cleanup scope.

### Runtime and Deployment Assumptions

- Canonical runtime writes now live under `webapp/` for config, sessions, logs, uploads, cache, temp/session artifacts, and model-relative assets.
- Filesystem-backed Flask sessions remain a real deployment constraint.
- `webapp/config/.env` persistence is a real runtime requirement.
- Repo-root `logs/` remains only a transitional local compatibility surface for the performance-summary fallback and should not be used as a Docker mount.
- `FLASK_SECRET_KEY` must remain stable across restarts.
- Model-weight handling is still an explicit Docker decision, not a solved assumption.

---

## Planned Task Sequence

### `TASK-051: Runtime Dependency Verification and Split`

**Why first**:
- It lowers Docker risk before image work starts.
- It prevents deployment-sensitive dependency drift from getting hidden inside containerization work.

**Key outputs**:
- Verified runtime dependency set
- CPU/CUDA behavior notes
- Documented keep/remove/reclassify decisions

**Exit criteria**:
- Clean-environment install test
- App startup verification
- CPU path verified
- CUDA path verified where hardware is available

### `TASK-056: First-Run Reliability and Runtime Determinism Hardening`

**Why second**:
- It fixes the confirmed first-run blockers and deployment-hostile runtime defaults before the smoke baseline is defined.

**Key outputs**:
- Deterministic first-run runtime contract
- Download-phase failure signaling
- Stable session identity
- Restored TLS verification defaults
- Updated runtime docs for CPU/CUDA, NumPy baseline, and dependency expectations

**Exit criteria**:
- Clean-environment first detection succeeds without runtime package mutation
- Partial tile-download failures stop during the imagery phase
- `pytest --collect-only tests -q` remains clean

### `TASK-057: Local YOLO Runtime Ownership and Torch Hub Independence`

**Why third**:
- It prevents Docker and the smoke baseline from inheriting the remaining Torch Hub / GitHub runtime dependency.

**Key outputs**:
- TowerScout-owned local YOLO loader path
- First-run detector initialization that no longer depends on Torch Hub / GitHub bootstrap behavior
- Revalidated CPU baseline and documented CUDA path on the local loader contract

**Exit criteria**:
- YOLO initialization no longer depends on `torch.hub`, Torch Hub cache state, or first-run GitHub access
- `webapp/model_params/yolov5/newest.pt` loads successfully through the local loader
- `pytest --collect-only tests -q` remains clean

### `TASK-052: Current Integration Smoke Test Baseline`

**Why fourth**:
- It gives Docker work a current validation target tied to the corrected runtime, not stale legacy assumptions or the older Hub-based YOLO path.

**Key outputs**:
- Current app-boot smoke test
- Core route availability validation
- One bounded detection-readiness path on the corrected runtime contract
- Updated or retired stale validation surfaces

**Exit criteria**:
- `pytest --collect-only tests -q` remains clean
- Current smoke path exists and runs against the corrected live route surface

### `TASK-025: Docker Containerization`

**Why fifth**:
- Docker work should start only after runtime and validation baselines are credible.

**Key outputs**:
- Dockerfile and Compose configuration
- Persistent mount strategy
- Stable runtime environment contract
- Documented model-weight handling strategy

**Required decisions during Phase 1**:
- Model weights in image layer vs runtime download vs host volume
- Minimum supported platform target (`AMD64` required, `ARM64` stretch)
- Container health/readiness approach for later launcher support

**Exit criteria**:
- Container builds successfully
- Setup Wizard works in Docker
- Settings persist across restarts
- Detection workflow validated in container

### `TASK-054: Local Launch UX`

**Why sixth**:
- It depends on a stable Docker baseline.
- It should improve local UX without destabilizing `TASK-025` delivery.

**Phase 1 target**:
- Launcher MVP (`start.bat` first)
- Browser auto-open after readiness wait
- Basic troubleshooting path (`stop` / `logs` guidance or scripts)

**Phase 2 target**:
- Lightweight readiness endpoint or equivalent readiness contract
- Documented first-run / repeat-run behavior

**Phase 3 target**:
- Evaluate deferred warm-start UX for models and ZIP data

**Exit criteria for Sprint 05 success**:
- A local user can launch Docker with minimal or no manual CLI interaction
- Browser opens only after the app shell is reachable

### `TASK-029: Multi-Provider Fallback`

This remains a stretch goal and should only begin after `TASK-054` if capacity remains.

---

## Execution Timeline

### Week 1: April 7-13

**Focus**: complete the dependency / pinned-YOLO foundation and finish the first-run hardening gate

| Date | Tasks | Hours |
|------|-------|-------|
| Apr 7-9 | `TASK-051` runtime dependency verification | 8-12h |
| Apr 9 | `TASK-055` pinned-ref hardening | 6-10h |
| Apr 10-13 | `TASK-056` first-run reliability and runtime determinism hardening | 12-20h |

**Week 1 note**:
- `PRE-SPRINT-05-02` is complete, so all Sprint 05 work should continue from the canonical `webapp/` runtime contract rather than the pre-normalization folder tree.

### Week 2: April 14-20

**Focus**: remove the remaining Hub/GitHub runtime dependency and lock the host smoke baseline

| Date | Tasks | Hours |
|------|-------|-------|
| Apr 14-17 | `TASK-057` local YOLO runtime ownership and Torch Hub independence | 12-20h |
| Apr 18-20 | `TASK-052` current integration smoke-test baseline | 6-10h |

### Week 3: April 21-25

**Focus**: containerize the corrected baseline, then decide whether any launch-UX stretch capacity remains

| Date | Tasks | Hours |
|------|-------|-------|
| Apr 21-23 | `TASK-025` Phase 1-2: Docker strategy, Dockerfile, and Compose configuration | 10-16h |
| Apr 23-24 | `TASK-025` Phase 3-4: volume mounts, validation, and documentation | 8-12h |
| Apr 24-25 | Stretch decision: `TASK-054` Phase 1 only if Docker baseline lands cleanly | 0-8h |
| Apr 25 | Sprint 05 retrospective | 2-4h |

**Total Sprint Effort**: `64-94 hours`  
**Planning Target**: `70-80 hours`

---

## Key Risks and Mitigations

### Risk 1: Docker Scope Expansion

**Risk**:
`TASK-025` grows to absorb runtime hardening, smoke-test work, or launch UX.

**Mitigation**:
- Keep `TASK-056`, `TASK-057`, `TASK-052`, and `TASK-054` explicitly separate.
- Treat any startup-UX redesign as `TASK-054` or Sprint 06 work.

### Risk 2: Persistent-State Misconfiguration

**Risk**:
Config, session, temp, log, cache, or upload paths are not mounted correctly.

**Mitigation**:
- Use normalized `webapp/` runtime paths.
- Validate Setup Wizard save/load and restart persistence explicitly.

### Risk 3: Model-Weight Strategy Ambiguity

**Risk**:
Container delivery stalls because weight handling is not decided early.

**Mitigation**:
- Force the decision in `TASK-025` Phase 1.
- Document the chosen strategy and its tradeoffs in the Docker docs.

### Risk 4: Building Docker On The Wrong YOLO Contract

**Risk**:
The team starts Docker work before the active YOLO runtime is locally owned and independent of Torch Hub / GitHub bootstrap behavior.

**Mitigation**:
- Complete `TASK-057` before `TASK-025`.
- Treat any proposal to defer `TASK-057` as an explicit risk-acceptance decision rather than an implicit shortcut.

### Risk 5: Velocity Drift

**Risk**:
Sprint planning assumes Sprint 03 pace instead of a sustainable infrastructure pace.

**Mitigation**:
- Plan using the `3.5-4.0 hrs/day` assumption.
- Keep `TASK-054`, `TASK-029`, and warm-start work explicitly optional.

### Risk 6: Launch UX Overreach

**Risk**:
`TASK-054` expands from launcher MVP into full runtime warm-start redesign.

**Mitigation**:
- Ship Phase 1 first.
- Defer Phase 3 warm-start UX if Docker baseline or readiness work consumes capacity.

---

## Definition of Done

### Must-Have

- `TASK-051` complete
- `TASK-055` complete
- `TASK-056` complete
- `TASK-057` complete
- `TASK-052` complete
- `TASK-025` Phase 1-3 complete
- Setup Wizard functional in Docker
- Settings save/load validated with persistence
- Detection workflow validated in Docker
- Docker Compose configuration validated
- No regressions against Sprint 04 core behavior

### Should-Have

- `TASK-025` Phase 4 complete
- `AMD64` support validated
- `TASK-054` Phase 1 launcher MVP complete
- Deferred Sprint 04 quick wins reconsidered only if capacity remains

### Nice-to-Have

- `TASK-054` Phase 2 either complete or cleanly deferred with documented readiness approach
- `TASK-029` investigation begins after `TASK-054`
- `ARM64` support validated
- Docker Hub publishing path documented
- Warm-start UX feasibility assessed for Sprint 06

---

## Success Indicators

- A new user can install and run a first detection without in-process package upgrades.
- YOLO initialization works on the validated host baseline without first-run GitHub dependence.
- A new user can run `docker compose up` and complete Setup Wizard.
- Configuration persists across container restarts.
- Detection workflow works end-to-end in the Docker environment.
- A local user can start the app with minimal or no manual CLI interaction once `TASK-054` lands.
- Documentation explains both the container contract and the local launch path clearly.

---

## References

- [Current Tasks](../../current-tasks.md)
- [Sprint Planning Session - 2026-04-06](./SPRINT-PLANNING-SESSION-2026-04-06.md)
- [Metrics Report - 2026-04](./METRICS-REPORT-2026-04.md)
- [Removal Candidates - Containerization](../analysis/REMOVAL-CANDIDATES-CONTAINERIZATION.md)
- [Sprint 04 Retrospective](./SPRINT-04-RETROSPECTIVE.md)

---

**Status**: Sprint 05 plan re-sequenced around runtime hardening, local YOLO ownership, and Docker readiness gates  
**Next Action**: Execute `TASK-056`, then `TASK-057`, then `TASK-052`, then begin `TASK-025` Phase 1

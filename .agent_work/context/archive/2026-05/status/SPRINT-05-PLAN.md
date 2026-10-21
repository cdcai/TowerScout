# Sprint 05 Plan - Runtime Determinism, OCI Release Readiness, and Local Launch Foundations

**Sprint Period**: April 7 - active extension after April 25, 2026
**Planning Date**: April 6, 2026
**Updated Through**: May 5, 2026
**Sprint Focus**: Runtime hardening, reproducible inference, pre-container release gates, OCI/GitHub-first release readiness, and bounded local launch UX follow-through
**Target Capacity**: 76-118 hours after the final review gates (original planning target was 70-80 hours)
**Expected Bundle Growth**: +10-20 KB (infrastructure-heavy sprint)

---

## Plan Authority

This file is the authoritative Sprint 05 plan.

It supersedes the historical planning snapshot in [SPRINT-PLANNING-SESSION-2026-04-06.md](./SPRINT-PLANNING-SESSION-2026-04-06.md) wherever the two differ.

The main Sprint 05 plan updates since the April 6 planning session are:

1. `TASK-056` now exists as the explicit first-run reliability and runtime-determinism gate before the smoke baseline.
2. `TASK-057` now exists as the explicit local YOLO runtime ownership task before the smoke baseline and container work.
3. `TASK-054` remains a post-container stretch task for launch UX, and `TASK-029` stays behind it.
4. Runtime path normalization remains pre-sprint closeout work, not active Sprint 05 feature delivery.
5. The detailed Sprint 05 scope is synchronized with [current-tasks.md](../../current-tasks.md).
6. `TASK-063` is now the pre-container release-hardening gate added from the second senior-engineer review.
7. The April 28 plan sufficiency review confirms the plan is sufficient if v1 scope stays narrow and release, persistence, security, and support contracts are explicit before containerization becomes the baseline.
8. `TASK-064` is now the targeted runtime responsiveness and inference baseline gate added from the final path-forward review.
9. The May 4 open-source deployment review shifts the user-facing path toward GitHub Releases, Podman as the preferred open-source runtime target after validation, and source clone/build as a developer/support path.
10. The May 5 decision lock finalizes the pre-`TASK-025` path: GitHub Release ZIP plus pinned GHCR image digest, optional OCI archive fallback, Podman-first Windows target with a required validation/risk-acceptance gate, Docker-compatible fallback, manifest-managed large assets, split CI/release validation, and structured health/readiness.

---

## Sprint Objectives

### Primary Goal

Deliver Docker-compatible / OCI containerization (`TASK-025`) now that the runtime contract is corrected, locally owned, validated through a current smoke-test baseline, and cleared through the pre-container release-hardening and targeted responsiveness/performance gates.

### Secondary Goals

1. Keep `TASK-051` and `TASK-055` as the completed Sprint 05 foundation.
2. Complete `TASK-056` first-run reliability and runtime determinism hardening.
3. Complete `TASK-057` local YOLO runtime ownership and Torch Hub independence.
4. Complete `TASK-052` current integration smoke-test baseline on the corrected runtime.
5. Complete `TASK-063` pre-container release hardening before container work starts.
6. Complete `TASK-064` targeted runtime responsiveness and inference baseline before container sign-off.
7. Deliver `TASK-054` local launch UX MVP only if the selected container runtime baseline lands cleanly.
8. Consider `TASK-029`, `TASK-026`, or deferred Sprint 04 quick wins only if capacity remains.

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
- Resolve or explicitly accept the second-review release-hardening findings before Docker starts.
- Document the v1 release boundary, supported/unsupported environments, and minimum support diagnostics before Docker starts.
- Deliver Docker build/run behavior with persistent state mounted correctly.
- Preserve Setup Wizard, Settings, and current detection workflow behavior in the selected OCI/container runtime environment.

### What Sprint 05 Should Not Quietly Absorb

- Broad architecture rewrite beyond `TASK-056` and `TASK-057`
- Large validation-harness rewrites beyond `TASK-052`
- Release-hardening and CI policy folded into `TASK-025`
- Startup-pipeline redesign folded into `TASK-025`
- Multi-provider fallback as an assumed in-sprint commitment

### Explicit Scope Boundary

`TASK-056` owns immediate first-run/runtime hardening.  
`TASK-057` owns local YOLO runtime ownership.  
`TASK-063` owns pre-Docker dependency, CI, residual YOLO/Torch Hub audit, upload/TLS, metrics-log, v1 release-boundary, and support-diagnostics gates.  
`TASK-064` owns targeted ProviderStateManager responsiveness cleanup and `torch.inference_mode()` benchmark evidence.  
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
- It gives container work a current validation target tied to the corrected runtime, not stale legacy assumptions or the older Hub-based YOLO path.

**Key outputs**:
- Current app-boot smoke test
- Core route availability validation
- One bounded detection-readiness path on the corrected runtime contract
- Updated or retired stale validation surfaces

**Exit criteria**:
- `pytest --collect-only tests -q` remains clean
- Current smoke path exists and runs against the corrected live route surface

### `TASK-063: Pre-Docker Release Hardening And CI Reproducibility Gate`

**Why fifth**:
- The second senior review identified release-quality risks that should not be normalized into the container baseline.
- These risks are adjacent to Docker but should stay separate from Docker implementation so `TASK-025` remains testable and rollback-friendly.

**Key outputs**:
- Reviewed and patched dependency baseline, or owner-approved explicit risk acceptance where a patch must defer
- Tracked frontend reproducibility policy for the current build pipeline
- CI security action pinning, workflow permission review, and release-candidate gate interpretation
- Pinned third-party GitHub Action review/update cadence
- Dependency repeatability policy for Python, frontend, and large runtime assets
- Residual YOLO/Torch Hub audit proving no supported runtime path falls back to nondeterministic bootstrap behavior
- First-release support boundary for `.pt` model upload and insecure TLS escape hatches
- Upload-limit alignment across Flask, Waitress, and `.pt` support policy
- Provider API key restriction guidance for Google and Azure
- Single authoritative performance-log file contract
- V1 release boundary and minimum support diagnostics contract

**Exit criteria**:
- Trivy action no longer uses floating `@master`
- Release-relevant third-party GitHub Actions are pinned to reviewed immutable references or owner-approved
- Pinned third-party GitHub Actions have a recurring review/update cadence
- Workflow permissions are reviewed for release readiness
- Dependency repeatability policy is documented
- Frontend lockfile/reproducibility decision is reflected in tracked files or documentation
- Residual YOLO/Torch Hub behavior is audited and documented
- `.pt` model upload and insecure TLS behavior are explicitly gated, disabled, or documented as local/trusted exceptions
- Flask upload limits, Waitress request-body limits, and `.pt` upload policy are aligned or owner-approved
- Provider API key restriction guidance is documented
- `performance.log` is no longer both a structured logging target and CSV metrics target
- Supported/unsupported v1 environments and minimum support diagnostics are documented
- Any unresolved item is recorded as an owner-approved explicit risk acceptance before `TASK-025` starts

### `TASK-064: Targeted Runtime Responsiveness And Inference Baseline`

**Why sixth**:
- The final path-forward review identified two low-cost runtime risks that should not wait for broad frontend modernization or CPU optimization.
- Keeping this task separate prevents Docker from absorbing frontend/runtime tuning work while still avoiding normalization of known responsiveness/performance uncertainty.

**Key outputs**:
- ProviderStateManager busy-wait / main-thread locking cleanup or owner-approved explicit risk acceptance
- Preserved Google/Azure provider switching behavior
- `torch.inference_mode()` benchmark evidence against the active inference path
- Apply/defer/reject decision for the benchmarked optimization

**Exit criteria**:
- Frontend build succeeds after any ProviderStateManager changes
- Focused provider/browser validation is recorded
- Inference benchmark evidence is recorded
- Any deferred performance work is linked to `TASK-026`
- Any unresolved targeted finding has an owner-approved risk note covering issue, deferral rationale, user/release impact, mitigation, review timing, and follow-up owner/task

### `TASK-025: Docker / OCI Containerization`

**Current status**: Phase 1 runtime contract is active as of May 5, 2026. `TASK-063` and `TASK-064` are complete, and the May 5 pre-task decision lock is the starting contract.

**Why seventh**:
- Container work should start only after runtime, validation, and release-hardening baselines are credible.

**Key outputs**:
- Dockerfile/Containerfile-compatible image definition and Compose-compatible configuration
- GitHub Release ZIP package contract for the normal end-user path, including a pinned GHCR image reference by digest and optional OCI archive fallback
- Persistent mount strategy
- Stable runtime environment contract
- Versioned v1 runtime/persistence contract
- Documented first-run asset/bootstrap strategy
- `/api/health` and structured `/api/readiness` contract for `TASK-054`
- Podman compatibility spike or explicit owner-approved risk acceptance before Podman is promised as the open-source runtime path

**Required decisions during Phase 1**:
- Large runtime asset strategy and full asset inventory
- Minimum supported platform target (`AMD64` first, CPU baseline, NVIDIA/CUDA accelerated path on compatible `AMD64` hosts)
- Persistence categories and secret-key continuity
- Cache and geocode data durability classification
- Container health/readiness approach for later launcher support
- User-facing distribution shape (GitHub Release ZIP plus pinned GHCR image digest, with optional OCI archive fallback for restricted networks)
- Source clone/build boundary as developer/support path rather than normal-user path
- Default named-volume profile and optional host-visible data-directory profile
- Podman-first open-source runtime target validation, with the adjustment that Podman support cannot be promised until the spike passes or is risk-accepted
- TowerScout application license/open-source suitability clarification
- Upload-limit/request-body behavior inherited from `TASK-063`
- Explicit unsupported-environment wording for Mac, ARM64, offline, air-gapped, VDI, shared deployment, and native installer behavior

**Exit criteria**:
- Container builds successfully
- Setup Wizard works in the selected container runtime
- Settings persist across restarts
- First-run asset bootstrap succeeds or fails with clear recovery guidance after SHA-256 verification and staged activation
- Detection workflow validated in container
- Runtime/persistence/asset contracts are documented and validated against the container
- Cache and geocode data durability classification is documented

### `TASK-054: Local Launch UX`

**Current status**: Phase 1 launcher MVP is complete and merged. Phase 2 readiness UX is cleanly deferred unless release-support validation under `TASK-065` shows the MVP needs more polish.

**Why eighth**:
- It depends on a stable selected container runtime baseline.
- It should improve local UX without destabilizing `TASK-025` delivery.

**Phase 1 target**:
- Launcher MVP (`start.bat` first) for supported Windows-based GitHub Release package deployment
- Browser auto-open after readiness wait
- Basic troubleshooting path (`stop` / `logs` / status guidance or scripts)
- User-visible handling of first-run asset download delays/failures
- Support diagnostics guidance for log locations, startup failures, version/asset visibility, and sensitive local artifact handling

**Phase 2 target**:
- Lightweight readiness endpoint or equivalent readiness contract
- Documented first-run / repeat-run / failure behavior

**Phase 3 target**:
- Evaluate deferred warm-start UX for models and ZIP data

**Exit criteria for Sprint 05 success**:
- A supported local user can start/stop/view logs with minimal or no manual container CLI interaction
- Browser opens only after the app shell is reachable
- First-run asset/bootstrap delays are explained rather than hidden
- Support-log and status collection paths are documented for limited/manual support

### `TASK-065: Release Packaging And Runtime Support Follow-Through`

**Why next**:
- It owns the release-support caveats intentionally deferred from `TASK-025`.
- It consumes the `TASK-054` launcher/support docs and validates the runtime claims those docs depend on.
- It controls whether Podman can be promised broadly on Windows hosts without Docker Desktop installed.

**Initial target**:
- Keep Podman support language aligned with the `TASK-065` validation of `podman-compose 1.5.0` as a Docker-Desktop-free Compose provider.
- Decide final Podman/Docker support language.
- Decide hosted asset download/bootstrap scope.
- Decide optional OCI image archive fallback scope for restricted-network use.
- Follow up on deferred GitHub Actions runtime warnings.
- Run broad release-readiness regression across setup, settings, provider switching, and detection surfaces.

### `TASK-029: Multi-Provider Fallback`

This remains a stretch goal and should only begin after `TASK-065` release-support follow-through if capacity remains.

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

### Week 3 / Sprint Extension: April 21 onward

**Focus**: complete pre-Docker release hardening and the targeted responsiveness/performance gate, then containerize the corrected baseline if both gates clear

| Date | Tasks | Hours |
|------|-------|-------|
| Apr 21 | `TASK-062` pre-Docker runtime cleanup and loader hardening | 6-10h |
| Apr 28-29 | `TASK-063` pre-Docker release hardening and CI reproducibility gate | 8-16h |
| After `TASK-063` | `TASK-064` targeted runtime responsiveness and inference baseline | 4-8h |
| After `TASK-064` | `TASK-025` Phase 1-2: OCI strategy, image definition, Compose-compatible config, and GitHub Release package contract | 10-16h |
| After `TASK-025` Phase 2 | `TASK-025` Phase 3-4: volume mounts, validation, and documentation | 8-12h |
| Stretch after container baseline | `TASK-054` Phase 1 only if selected runtime baseline lands cleanly | 0-8h |
| Closeout | Sprint 05 retrospective / Sprint 06 handoff | 2-4h |

**Total Sprint Effort**: `76-118 hours` after the final-review gates  
**Original Planning Target**: `70-80 hours`

**April 28 replan note**:
- `TASK-063` is now a pre-Docker gate based on the second senior-engineer review.
- The plan sufficiency assessment confirms the sequence is viable only if v1 release boundary, persistence, CI/security, and support contracts are explicit.
- The final path-forward review adds `TASK-064` as a bounded responsiveness/performance gate before Docker starts.
- Docker and launcher work should slip behind that gate rather than compressing validation.

---

## Key Risks and Mitigations

### Risk 1: Docker Scope Expansion

**Risk**:
`TASK-025` grows to absorb runtime hardening, smoke-test work, or launch UX.

**Mitigation**:
- Keep `TASK-056`, `TASK-057`, `TASK-052`, `TASK-063`, `TASK-064`, and `TASK-054` explicitly separate.
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
The team starts container work before the active YOLO runtime is locally owned and independent of Torch Hub / GitHub bootstrap behavior.

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
- Defer Phase 3 warm-start UX if container baseline or readiness work consumes capacity.

### Risk 7: Release-Hardening Drift Into Docker

**Risk**:
Dependency patching, CI policy, upload/TLS gating, and metrics-log cleanup get mixed into `TASK-025`.

**Mitigation**:
- Keep `TASK-063` separate and complete it before Docker starts.
- Record any unresolved `TASK-063` item as owner-approved explicit risk acceptance before `TASK-025`.

### Risk 8: Known Supportability Gaps Become Part Of The Baseline

**Risk**:
The Docker image ships with ambiguous frontend reproducibility, floating CI security action references, unsafe upload assumptions, or ambiguous performance logs.

**Mitigation**:
- Treat `TASK-063` as a release-quality gate, not an optional cleanup.
- Keep Docker validation blocked until the known findings are fixed or owner-approved.

### Risk 9: Operational Contracts Stay Implicit

**Risk**:
The plan proceeds with the right sequence but leaves v1 support boundary, persistence behavior, asset recovery, and diagnostics as assumptions.

**Mitigation**:
- Use the path-forward analysis as the planning contract.
- Require `TASK-063` and `TASK-025` to record the release boundary, persistence map, asset contract, and support diagnostics before Docker is treated as release-ready.

### Risk 10: Targeted Responsiveness Findings Become Docker Noise

**Risk**:
ProviderStateManager locking behavior or a low-cost inference-mode optimization is discovered during Docker validation, creating avoidable confusion about whether the issue is frontend state, ML runtime behavior, or containerization.

**Mitigation**:
- Keep `TASK-064` separate from Docker.
- Resolve, measure, or owner-approve these two targeted findings before `TASK-025` begins.

---

## Definition of Done

### Must-Have

- `TASK-051` complete
- `TASK-055` complete
- `TASK-056` complete
- `TASK-057` complete
- `TASK-052` complete
- `TASK-063` complete
- Trivy action no longer uses floating `@master`
- Release-relevant third-party GitHub Actions pinned to reviewed immutable references or owner-approved
- Pinned third-party GitHub Actions have a recurring review/update cadence
- Workflow permissions reviewed for release readiness
- Frontend lockfile/reproducibility policy decided
- Dependency repeatability policy documented for Python dependencies, frontend dependencies, and runtime assets
- Residual YOLO/Torch Hub behavior audited
- `.pt` model upload and insecure TLS support boundaries decided
- Flask upload limits, Waitress request-body limits, and `.pt` upload policy aligned
- Provider API key restriction guidance documented for Google and Azure
- `performance.log` has one authoritative format contract
- V1 supported/unsupported environment boundary documented
- Minimum support diagnostics contract documented
- `TASK-064` complete
- ProviderStateManager busy-wait / main-thread locking behavior removed or owner-approved
- `torch.inference_mode()` benchmark decision recorded before container sign-off
- Any unresolved `TASK-063` or `TASK-064` finding has owner-approved risk acceptance documenting issue, deferral rationale, user/release impact, mitigation, review timing, and follow-up owner/task
- `TASK-025` Phase 1-3 complete
- Setup Wizard functional in the selected OCI/container runtime
- Settings save/load validated with persistence
- Detection workflow validated in the selected OCI/container runtime
- Durable and writable mount behavior validated and documented
- Cache and geocode data durability classified for v1
- Compose-compatible configuration validated
- First-run asset bootstrap and recovery path validated
- Container readiness/health behavior available for launcher polling
- No regressions against Sprint 04 core behavior

### Should-Have

- `TASK-025` Phase 4 complete
- `AMD64` CPU baseline validated and CUDA-enabled `AMD64` path documented
- `TASK-054` Phase 1 launcher MVP complete
- `TASK-065` release-support follow-through scoped for Sprint 06 intake
- Deferred Sprint 04 quick wins reconsidered only if capacity remains

### Nice-to-Have

- `TASK-054` Phase 2 either complete or cleanly deferred with documented readiness approach
- `TASK-029` investigation begins after `TASK-065`
- `ARM64` / Mac follow-on plan documented
- Container registry publishing path documented
- Warm-start UX feasibility assessed for Sprint 06

---

## Success Indicators

- A new user can install and run a first detection without in-process package upgrades.
- YOLO initialization works on the validated host baseline without first-run GitHub dependence.
- Known release-hardening findings are fixed or owner-approved before Docker starts.
- Targeted responsiveness/performance findings from `TASK-064` are fixed, measured, or owner-approved before Docker starts.
- V1 operational contracts are explicit before Docker becomes the baseline.
- A new user can use the GitHub Release package and selected runtime path to complete Setup Wizard.
- Configuration persists across container restarts.
- Detection workflow works end-to-end in the selected OCI/container runtime environment.
- A local user can start the app with minimal or no manual CLI interaction once `TASK-054` lands.
- Documentation explains both the container contract and the local launch path clearly.

---

## References

- [Current Tasks](../../current-tasks.md)
- [Sprint Planning Session - 2026-04-06](./SPRINT-PLANNING-SESSION-2026-04-06.md)
- [Metrics Report - 2026-04](./METRICS-REPORT-2026-04.md)
- [Removal Candidates - Containerization](../analysis/REMOVAL-CANDIDATES-CONTAINERIZATION.md)
- [Senior Engineering Review Response Memo V2](../analysis/SENIOR-ENGINEERING-REVIEW-RESPONSE-MEMO-V2-2026-04-28.md)
- [TowerScout Path Forward After Plan Sufficiency Review](../analysis/TOWERSCOUT-PATH-FORWARD-POST-SUFFICIENCY-REVIEW-2026-04-28.md)
- [Sprint 04 Retrospective](./SPRINT-04-RETROSPECTIVE.md)

---

**Status**: Sprint 05 plan re-sequenced around runtime hardening, local YOLO ownership, release hardening, targeted responsiveness/performance validation, v1 operational contracts, and Docker readiness gates  
**Next Action**: Execute `TASK-025` Phase 1 by auditing runtime paths, assets, config/secret behavior, persistence classes, upload-limit inheritance, health/readiness states, release-package contents, and engine-aware validation before image-definition implementation

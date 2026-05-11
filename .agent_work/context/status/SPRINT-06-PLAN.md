# Sprint 06 Plan

**Created**: May 11, 2026  
**Sprint Planning Baseline**: Sprint 06 release-readiness planning after Sprint 05 closeout  
**Primary Source Backlog**: `.agent_work/task-backlog.md`  
**Active Carry-Forward**: `TASK-065` remains in `.agent_work/current-tasks.md` pending release-owner support-language review and commit/PR checkpoint  
**Recommended Sprint Theme**: V1 RC1 / pilot-ready release readiness, not final V1 completion or feature expansion

---

## Executive Summary

Sprint 06 should turn the Sprint 05 runtime and release baseline into a V1 release candidate package that a non-technical Windows pilot user can realistically receive, understand, launch, configure, and test.

The sprint should not start with broad end-user testing. It should first settle the asset bundle contract and write package-based end-user documentation. Without those two pieces, testers will mostly discover already-known gaps around what to download, where model/data files go, and how to recognize a successful first run.

The recommended Sprint 06 path is:

1. Close `TASK-065`.
2. Define the release asset bundle contract through `TASK-072`.
3. Write end-user release package documentation through `TASK-071`.
4. Run a clean-machine release-candidate validation gate through `TASK-066`.
5. Prepare pilot / UAT execution through `TASK-073`.
6. Resolve release policy and provider-key exposure boundaries through `TASK-069` and `TASK-076`.
7. Use remaining capacity for preflight, narrow CI release gates, and Windows script validation.

Sprint 06 should be considered successful when TowerScout reaches **V1 RC1 / pilot-ready** status. Final V1 completion should wait until pilot/UAT feedback has been triaged, install/launch/setup/detection blockers have been fixed or explicitly accepted, and remaining work has been sorted into V1 patch items or the V2 roadmap.

---

## Client Outcome

The client's minimum expectation remains the release target:

> Create a way for users to easily deploy the code from GitHub to their laptops, with all appropriate folder structure intact, clear instructions for any other files that are needed, and a simplified way to set up and run the program locally.

For Sprint 06, this means the team should be able to hand a pilot user:

- a GitHub Release control ZIP or release-candidate equivalent
- a clearly versioned asset bundle or precise asset acquisition instructions
- package-based quick-start instructions
- setup/troubleshooting instructions that assume no project tribal knowledge
- a bounded acceptance test flow
- an issue-reporting path

---

## Sprint Goal

**Sprint 06 Goal**: Produce and internally validate a V1 RC1 / pilot-ready local release package path for Windows 11 AMD64 users, including asset delivery, end-user documentation, release policy boundaries, and a clean-machine validation gate.

### Success Criteria

- The release package and asset bundle relationship is documented and testable.
- End-user docs explain exactly what to download, where to place assets, how to launch, how to configure provider keys, and how to verify success.
- A clean-machine validation run proves the package/docs/assets path before external user testing begins.
- Release policy and provider-key exposure risks are explicitly accepted, mitigated, or converted into blockers.
- External pilot testing begins only after the internal release-candidate gate has produced actionable evidence.
- Final V1 completion is explicitly reserved for after pilot/UAT blocker triage.

---

## Milestone Boundary

### Sprint 06 Target: V1 RC1 / Pilot-Ready

Sprint 06 should end with a release candidate that is ready to put in front of controlled pilot users. That means the release package, asset contract, end-user docs, clean-machine validation, policy decisions, and UAT plan are complete enough to test outside the development context.

### Post-Sprint 06 Target: V1 Complete

V1 should be called complete only after pilot/UAT feedback confirms the package path works for intended users or after remaining pilot findings are explicitly dispositioned. The V1 completion gate should require:

- pilot users can install, launch, and configure TowerScout on a supported Windows laptop
- at least one bounded detection workflow succeeds from the packaged path
- install, launch, setup, detection, and documentation blockers are fixed or owner-accepted
- remaining non-blocking issues are assigned to V1 patch work or moved to the V2 roadmap

### V2 Start Gate

V2 work should not begin until V1 release blockers from pilot/UAT are fixed or intentionally accepted. Architecture, performance, broader platform support, and richer workflow features should remain V2 candidates unless they become necessary to satisfy the V1 pilot-release bar.

---

## Non-Goals

Sprint 06 should not attempt to deliver:

- mobile responsiveness
- advanced filtering
- performance dashboard
- user preferences
- broad NumPy 2 migration
- GPU/CUDA implementation unless explicitly chosen after `TASK-075`
- background-job architecture unless the release path intentionally pauses
- backend decomposition unless `TASK-058` has already clarified durable job/state ownership
- full restricted-network / offline package support unless it becomes a hard launch requirement

---

## Proposed Sprint Scope

### Committed Lane

| Order | Task | Purpose | Expected Deliverable |
|---:|---|---|---|
| 0 | `TASK-065` Release Packaging And Runtime Support Follow-Through | Close the active carry-forward release-support item. | Owner-reviewed support language and commit/PR checkpoint. |
| 1 | `TASK-072` Release Asset Bundle Contract | Define how out-of-repo model/data assets are distributed and imported. | Asset bundle layout, naming/version rules, checksum policy, release matching rules, and import instructions. |
| 2 | `TASK-071` End-User Release Package Documentation | Write docs for the actual package path. | User quick start, full package guide, troubleshooting, first-run screenshots/checklist, issue-reporting handoff. |
| 3 | `TASK-066` Release Candidate Validation Gate | Internally prove the package/docs/assets path before external testing. | Clean-machine validation checklist, results, defects, and release-candidate pass/fail recommendation. |
| 4 | `TASK-073` Clean-Machine Pilot / UAT Execution Plan | Prepare external tester workflow after internal validation. | Tester instructions, acceptance checklist, issue capture template, environment capture checklist, support escalation flow. |

### Policy Lane

These tasks should run early enough that they do not block release late. They can proceed in parallel with documentation and validation when the owner/legal inputs are available.

| Task | Purpose | Expected Deliverable |
|---|---|---|
| `TASK-069` License And Release Policy Review | Confirm the repo license, model/data asset distribution rights, runtime-tooling posture, and pilot release boundary. | Release-policy memo with owner/legal decision or explicit blocker. |
| `TASK-076` Provider API Key Exposure And Restriction Policy | Decide whether current browser SDK key exposure is acceptable for v1 with restrictions or needs additional engineering. | Provider-key policy, required key restrictions, user guidance, and go/no-go impact. |
| `TASK-075` GPU / CUDA Support Decision | Decide whether v1 is CPU-only or includes a documented CUDA path. | Written decision and documentation update. Implementation only if explicitly selected later. |

### Follow-Through Lane

Select these only if committed-lane work is complete or if `TASK-066` exposes a need that should be fixed before external UAT.

| Task | Trigger | Expected Deliverable |
|---|---|---|
| `TASK-074` Runtime Prerequisite Preflight | Tester setup still depends too much on manual runtime diagnosis. | Preflight command or launcher-integrated checks for engine, Compose provider, Podman machine, WSL/virtualization hints, ports, disk, assets, TLS bundle, and provider setup state. |
| `TASK-067` CI Release Gate Tightening | Manual release checks become repetitive or high-risk. | Narrow CI/manual gate coverage for package assembly, image digest, manifest/checksum consistency, and launcher smoke behavior. |
| `TASK-068` Windows Test Portability And Script Validation | Script validation remains environment-sensitive. | Windows-first script validation proof and documented handling for PowerShell Core / CI gaps. |

---

## Recommended Sequence

### Phase 0: Close Carry-Forward

**Task**: `TASK-065`  
**Objective**: Close implementation-complete release-support work before taking on new Sprint 06 scope.

Acceptance expectations:

- Release owner reviews support language and residual caveats.
- Commit/PR checkpoint records the final `TASK-065` release-support updates.
- Any unresolved caveat is moved to `TASK-066`, `TASK-067`, `TASK-068`, `TASK-069`, or `TASK-070`.

### Phase 1: Define What Users Receive

**Task**: `TASK-072`  
**Objective**: Make the asset delivery model concrete before docs and testing.

Acceptance expectations:

- Asset bundle layout is defined, including:
  - `assets/model_params/yolov5/newest.pt`
  - `assets/model_params/EN/b5_unweighted_best.pt`
  - `assets/data/tl_2025_us_zcta520/`
- Bundle naming and versioning convention is defined.
- Required and optional files are mapped to `webapp/asset_manifest.v1.json`.
- Checksum verification policy is defined for release-candidate validation and normal user import.
- The relationship between GitHub Release ZIP, GHCR image digest, and asset bundle is explicit.
- The source of each asset is documented, including any distribution constraints.
- Restricted-network handling is either deferred to `TASK-070` or explicitly included if required.

### Phase 2: Write User-Facing Package Docs

**Task**: `TASK-071`  
**Objective**: Replace source-checkout tester guidance with package-based release guidance.

Acceptance expectations:

- A one-page quick start exists for Windows 11 AMD64 pilot users.
- A fuller package guide exists for first-line support and testers.
- Docs cover:
  - prerequisite runtime choices
  - package download
  - asset bundle placement
  - `start.bat`
  - Setup Wizard provider-key entry
  - status/log commands
  - asset import
  - TLS CA import
  - reset/restart/stop
  - common failures
  - what to report back
- Existing older source/Conda user-testing guides are either marked as legacy/source-install guidance or linked carefully so they do not confuse pilot release users.

### Phase 3: Internal Release Candidate Gate

**Task**: `TASK-066`  
**Objective**: Validate the package/docs/assets path internally before external testing.

Acceptance expectations:

- Run from a clean or representative user-facing Windows environment.
- Use only the release package, asset bundle, docs, and normal user/setup inputs.
- Validate:
  - package extraction
  - `.env` creation from `.env.example`
  - pinned image digest behavior
  - engine/Compose startup
  - readiness states
  - asset import
  - optional hash verification
  - provider-key setup
  - TLS CA import path where relevant
  - restart persistence
  - bounded Google or Azure detection smoke
  - status/log support commands
- Record time-to-first-run, manual interventions, confusing steps, and defects.
- Produce a pass/fail release-candidate recommendation.

### Phase 4: Pilot / UAT Preparation

**Task**: `TASK-073`  
**Objective**: Prepare external testing only after the package path has been internally validated.

Acceptance expectations:

- Tester instructions match the validated release-candidate package.
- Acceptance checklist is bounded and realistic.
- Tester issue-report checklist is ready.
- Environment capture includes OS, CPU/GPU, RAM, engine, Compose provider, network/TLS context, provider used, and whether assets were imported successfully.
- Support escalation path is explicit.
- Pilot start criteria and stop criteria are documented.

### Phase 5: Release Policy And Security Decisions

**Tasks**: `TASK-069`, `TASK-076`, `TASK-075`  
**Objective**: Avoid late release blockers and implicit support promises.

Acceptance expectations:

- License/release policy is documented.
- Provider key exposure posture is documented and approved or converted into an engineering blocker.
- GPU/CUDA support is explicitly in scope or out of scope for v1.

---

## Validation Strategy

Sprint 06 validation should focus on user-relevant release confidence.

### Required Validation

- `.agent_work/scripts/validate_agent_work.py`
- release package assembly with immutable image digest
- asset import from the documented bundle layout
- readiness after missing assets, after asset import, and after provider setup
- launcher startup from `start.bat`
- restart persistence for saved provider config and generated `FLASK_SECRET_KEY`
- one bounded detection smoke from the package path
- status/log command output suitable for support

### Conditional Validation

- TLS CA import if the validation environment has TLS inspection or proxy requirements
- Podman-specific validation if Podman remains the preferred runtime target for the pilot group
- Docker validation if Docker is permitted for the pilot group
- CUDA validation only if `TASK-075` decides CUDA is in v1 scope

### Not Required For Sprint 06

- mobile browser testing
- large-area performance optimization
- full offline / air-gapped validation
- multi-user hosting validation
- Mac or ARM64 validation

---

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Asset distribution remains ambiguous | Testers cannot complete setup without support intervention. | Make `TASK-072` first in the committed lane. |
| Docs are written before the package shape is stable | Docs become stale immediately and confuse testers. | Complete asset/package contract before finalizing `TASK-071`. |
| End-user testing starts too early | Feedback is dominated by known package/docs gaps. | Use `TASK-066` as the internal release-candidate gate before `TASK-073` external pilot. |
| Provider SDK keys remain client-visible without policy | Release may expose unsupported security expectations. | Complete `TASK-076` before broad distribution. |
| License/release posture is unresolved | Technical release may be blocked late. | Run `TASK-069` early and in parallel where possible. |
| Runtime prerequisites remain too complex | Non-technical users fail before reaching TowerScout setup. | Add `TASK-074` if `TASK-066` shows prerequisite friction. |
| Sprint expands into architecture and features | Release readiness slips again. | Keep `TASK-058`, `TASK-059`, mobile, filtering, dashboard, and preferences outside Sprint 06 unless the release lane intentionally pauses. |
| GPU expectations remain implicit | Users with CUDA machines may expect acceleration that v1 does not support. | Complete `TASK-075` decision and update docs accordingly. |

---

## Definition Of Done

Sprint 06 can be considered successful if TowerScout reaches V1 RC1 / pilot-ready status and:

- `TASK-065` is closed or intentionally carried with documented owner acceptance.
- `TASK-072` and `TASK-071` are complete enough to give to a pilot user.
- `TASK-066` has produced clean-machine evidence and a release-candidate recommendation.
- `TASK-073` has a ready tester workflow if the release candidate passes.
- `TASK-069` and `TASK-076` are resolved or clearly blocking with owners and next actions.
- The backlog no longer treats parked tail work as active v1 release scope.

Sprint 06 completion does not by itself mean final V1 completion. Final V1 requires pilot/UAT blocker triage after controlled external testing.

---

## Sprint Deliverables

- Release asset bundle contract.
- Package-based end-user quick start.
- Package-based full user guide / support guide.
- Clean-machine release-candidate validation report.
- Pilot / UAT execution checklist.
- License and release policy memo.
- Provider API key exposure/restriction policy memo.
- GPU/CUDA v1 scope decision.
- Optional runtime preflight and release CI/script gate improvements if capacity allows.

---

## Backlog References

Committed release-readiness lane:

- `TASK-072` Release Asset Bundle Contract
- `TASK-071` End-User Release Package Documentation
- `TASK-066` Release Candidate Validation Gate
- `TASK-073` Clean-Machine Pilot / UAT Execution Plan

Policy lane:

- `TASK-069` License And Release Policy Review
- `TASK-076` Provider API Key Exposure And Restriction Policy
- `TASK-075` GPU / CUDA Support Decision

Follow-through lane:

- `TASK-074` Runtime Prerequisite Preflight
- `TASK-067` CI Release Gate Tightening
- `TASK-068` Windows Test Portability And Script Validation

Deferred / parked:

- `TASK-028` Mobile Responsiveness
- `TASK-061` Coordinated NumPy 2 Runtime Migration
- Sprint 04 Deferred Quick Wins
- Advanced Filtering
- Performance Dashboard
- User Preferences

---

## Open Questions

1. What exact release vehicle will pilot users receive first: a GitHub Release draft, a manually shared release-candidate ZIP, or a repo-local validation package?
2. Who owns the asset bundle source of truth and permission to redistribute model weights and ZCTA data with the release materials?
3. Are pilot users expected to use Podman, Docker, or either runtime depending on local policy?
4. Does the pilot cohort include enterprise TLS inspection environments?
5. Are provider keys site-owned, user-owned, or project-provided for pilot testing?
6. Is CUDA acceleration expected by any pilot tester, or should v1 be explicitly CPU-only?
7. What is the minimum detection smoke that proves the package path without creating a long or fragile user test?

---

## Planning Decision

The recommended Sprint 06 planning decision is:

**Run Sprint 06 as a V1 RC1 release-readiness sprint.** Do not start broad end-user testing until the asset contract and package docs are complete and `TASK-066` has validated the clean-machine release-candidate path. Do not start V2 until pilot/UAT blockers are fixed or explicitly accepted.

# Task Backlog - October 2026 Roadmap

**Last Updated**: July 27, 2026
**Planning State**: Fix first while the immutable `v0.1.2` pilot remains in
use. Required release and handoff work takes priority over Task-058/059 stretch
work.
**Hard End**: October 31, 2026; operational closeout October 30

---

## Required Roadmap Work

| Order | Task | Status | Estimate | Dependencies | Required outcome |
| ---: | --- | --- | --- | --- | --- |
| 1 | `TASK-098` Dependency Security Remediation And Release Gate | IN_PROGRESS / PROJECT_LEAD_CHECKOUT_PENDING | Mandatory slices 4-8 days; full coordinated hardening 6-11 days, plus GPU/runtime host availability | Implementation, dependency qualification, Docker CPU/GPU and live Google/Azure smokes, branch security reconciliation, and PR #51 review remediation complete; awaits checkout/sign-off | Patchable mandatory findings pass regression/package validation with no unapproved feature, workflow, output, or performance regression; no unresolved release-blocking critical/high alert |
| 2 | `TASK-096` User-Initiated Exit And Container Stop | NOT_STARTED | 2-4 days | Task-087 helper/security pattern; current stop scripts | Confirmed Exit/Stop works on Docker and Podman without deleting named volumes |
| 3 | `TASK-097` Podman CPU/GPU Final Path Qualification | NOT_STARTED | 3-5 days plus environment validation | Tasks 090, 098, 087, and 096 | Podman CPU and GPU/CDI pass final-package qualification without Docker Desktop |
| 4 | `TASK-091` Owner-Runnable Release Qualification | NOT_STARTED | 3-6 days | Candidate scope stable; fixture/harness custody | cdcai owner can execute or supervise the minimum release gate |
| 5 | `TASK-092` Documentation Currentness And Information Architecture | NOT_STARTED | Stage A 1-2 days; Stage B as approved | Candidate behavior and package shape | Repo docs, user docs, release notes, external Setup Guide, and demo video agree |
| 6 | `TASK-093` Persistent Data Lifecycle And Recovery Rehearsal | NOT_STARTED | 1-2 days minimum | Runtime profiles and package lifecycle stable | Safe owner-run upgrade, rollback, cleanup, and recovery procedure |
| 7 | `TASK-094` Evidence-Gated Support Snapshot | EVIDENCE_GATED | 1-3 days if selected | Pilot/support evidence | Implement only if real feedback shows a support-diagnostics gap |

### Task-098 Boundary

- Task-090 identified five release-blocking alerts, one required-hardening
  alert, and an all-interface Compose port publication that contradicts the
  local-only runtime boundary.
- Do not patch dependency pins ad hoc before Task-090 establishes reachability,
  compatible target versions, and required regression scope.
- Treat Pillow, Waitress, and the client-relevant aiohttp findings as the first
  patch-oriented slice.
- Treat PyTorch/torchvision/CUDA and Fiona/GeoPandas as coordinated
  compatibility decisions, not isolated pin edits.
- Require written owner acceptance for any residual critical/high risk.
- Ratchet CI for new critical/high findings only after the existing baseline is
  classified and the approved remediation lands.
- Proposed scope:
  [`TASK-090/remediation-scope.md`](./tasks/active/TASK-090/remediation-scope.md).

### Task-096 Boundary

- Use a secured host helper or equally constrained host mechanism.
- Support Docker and Podman.
- Require confirmation.
- Preserve named volumes.
- Do not expose runtime sockets or arbitrary commands to the browser.

### Task-097 Boundary

- Qualify Podman CPU and Podman GPU as supported final paths.
- Cover the approved Compose-provider installer and manual fallback.
- Cover setup, start, readiness, providers, detection, assets, persistence,
  status, logs, TLS repair, Exit/Stop, and cleanup.
- Investigate Podman-machine image-pull and source-build TLS separately from
  Task-087.
- Fix packaged-runtime blockers. Document a source-build-only limitation only
  through an explicit owner decision.

### Task-092 Boundary

- Add administrator instructions for the opt-in Model Upload Key before the
  final documentation freeze.
- Cover secure key generation, private storage, enable/disable behavior,
  rotation, the approved SHA-256 allowlist, adding a new approved model, and
  troubleshooting rejected uploads.
- Make clear that normal users do not need the key, the upload feature remains
  disabled by default, and the key must never be committed, logged, placed in
  screenshots, or included in support artifacts.
- Explain that loopback publication blocks other physical devices by default,
  while another locally controlled Docker Desktop container can reach the host
  proxy and is still denied without the key.

---

## Conditional Architecture Work

| Order | Task | Status | Estimate | Start gate |
| ---: | --- | --- | --- | --- |
| 8 | `TASK-058` Background Detection Jobs And Durable Run State | CONDITIONAL | 3-5 days | Tasks 090, 098, 087, 096, and 097 pass; no pilot blocker; September 18 remains credible |
| 9 | `TASK-059` Backend Layer Decomposition And Logging Consolidation | CONDITIONAL | 3-5 days | Task-058 accepted and remaining schedule margin is still safe |

August 28 is the latest responsible Task-058 capacity checkpoint, not an
earliest start date. Task-058 may begin earlier when all gates pass.

---

## Existing Follow-On Backlog

| Priority | Task | Status | Recommended disposition |
| ---: | --- | --- | --- |
| 1 | `TASK-076` Provider API Key Exposure And Restriction Policy | NOT_STARTED | Reassess before final documentation/freeze; include provider-side restriction and ownership guidance |
| 2 | `TASK-068` Windows Test Portability And Script Validation | NOT_STARTED | Pull forward if Tasks 087, 096, or 097 expose repeatable script gaps |
| 3 | `TASK-077` Public Release Manifest And Asset Import Hardening | PARTIAL_FOLLOW_UP | Select only for a demonstrated manifest/import release gap |
| 4 | `TASK-070` Restricted-Network Package Enhancements | NOT_STARTED | Select only if final-package requirements expand beyond managed connected networks |
| 5 | `TASK-027` Enhanced Error Handling | NOT_STARTED | Use for confirmed user-facing error gaps that do not belong to required tasks |
| 6 | `TASK-026` CPU Optimization | NOT_STARTED | Defer unless measured final-candidate CPU performance becomes blocking |
| 7 | `TASK-029` Multi-Provider Fallback | NOT_STARTED | Defer until provider policy and error classification are stable |
| 8 | `TASK-060` Frontend Build Modernization | NOT_STARTED | Maintenance after final release unless current build becomes blocking |
| 9 | `TASK-078` Permissive Apache-Only Runtime Migration | NOT_STARTED | Future release track; not part of October closeout |

Parking lot:

- `TASK-028` Mobile Responsiveness
- `TASK-061` Coordinated NumPy 2 Runtime Migration
- Advanced filtering
- Performance dashboard
- Additional user preferences

---

## Active Elsewhere

| Task | Current state |
| --- | --- |
| `TASK-095` Governance And AI-Ready Handoff Foundation | Active in Sprint 08; Phase A complete, Phase B continues |
| `TASK-090` Runtime, Custom-Image, And Dependency Security Investigation | Completed; Task-098 scope approved |
| `TASK-098` Dependency Security Remediation And Release Gate | In progress; mandatory A-D/G implementation, Docker CPU/GPU compatibility, and live Google/Azure smokes passed; branch security-ratchet closeout pending |
| `TASK-087` Host-Side TLS Repair Control Plane | Reselected in Sprint 08 after the Tasks 090/098 security gate |
| `TASK-089` cdcai Adoption And Ownership Transfer | Owner-gated; preparation only until final qualification and approval |

---

## Milestone Controls

| Date | Control |
| --- | --- |
| August 28 | Required scope and Task-058 capacity checkpoint |
| September 18 | Code complete |
| September 25 | Feature/package/documentation complete |
| October 9 | Final-candidate freeze |
| October 16 | Acceptance complete |
| October 23 | Owner-operated handoff rehearsal complete |
| October 30 | Operational closeout |
| October 31 | Hard project end |

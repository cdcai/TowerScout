# TowerScout Handoff Guide

**Last Updated**: September 22, 2026
**Operational Closeout**: October 30, 2026
**Hard Project End**: October 31, 2026

## Current State

The validated fork-side `v0.1.2` release is the immutable Pilot Package:

`https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.2`

The cdcai owner selected a fix-first path:

- Keep pilot users on unchanged `v0.1.2`.
- Develop and qualify new candidates in `J-Schulein/TowerScout`.
- Name fork candidates `v0.1.3-rc.N`.
- Keep `cdcai/TowerScout` unchanged until owner qualification and explicit
  adoption approval.
- Select the official cdcai tag and display title before the official build.

## Immediate Delivery Direction

Qualify a new Windows 11 release from accepted `main` at
`9276084d91807906c53e00060670692b27e38483` using the existing
PowerShell/Compose package path. PR #67 and the Task-087 launcher redesign are
preserved but deferred: do not merge, reconcile, extend, or repeatedly review
them as prerequisites for deployment.

Read in this order:

1. `.agent_work/context/status/Reprioritization Effort/2026-09-21-windows-deployment-prioritization-v2.md`
2. `.agent_work/context/status/Reprioritization Effort/2026-09-21-windows-deployment-hardening-v2.md`
3. `.agent_work/context/status/Reprioritization Effort/2026-09-21-windows-deployment-hardening-v2-verification.md`
4. `.agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md`

Task status comes from `.agent_work/current-tasks.md`. Full acceptance requires
real YOLO and EfficientNet inference on Docker CPU, Docker NVIDIA, Podman CPU,
and Podman NVIDIA, repeated on independent suitable Windows computers.

The earlier October roadmap is retained as dated context:

- `.agent_work/context/status/Handoff-Planning/2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md`

The current Pilot/cdcai hold is:

- `.agent_work/context/status/Handoff-Planning/PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md`

## Required Final Scope

- Task-090 runtime/custom-image/dependency security investigation: complete
- Task-098 approved dependency remediation and release-risk disposition:
  complete through PR #51 / `e499b50` with its exact July 27 closeout state
- Task-099 August dependency-advisory follow-up: complete through PRs #68/#69
  and `f460445`/`0133b50`; main CI and the root dependency graph passed,
  alert `#74` closed without dismissal, and its August 11 closeout inventory
  contained the eight documented torch residuals
- Task-101 high-severity development-transitive `extract-zip` remediation and
  release-gate disposition: complete on accepted `main`; its former PR #67
  integration gate is superseded, not passed
- Task-087 / PR #67 launcher and guided-repair redesign: preserved and deferred
- Task-096 browser Exit/helper redesign: deferred; use tested command-based
  lifecycle controls
- Task-097 Podman CPU/GPU final-path qualification
- Docker CPU, Docker GPU, Podman CPU, and Podman GPU qualification
- owner-runnable qualification, documentation, recovery, governance, backlog,
  and handoff work
- external Setup Guide and demo video refresh

Task-058/059 are conditional stretch work and cannot displace required scope.

## Reading `.agent_work`

1. `.agent_work/current-tasks.md`
2. the four v2 records under `.agent_work/context/status/Reprioritization Effort/`
3. Pilot/cdcai plan linked above
4. `.agent_work/task-backlog.md`
5. `.agent_work/requirements.md`
6. `.agent_work/design.md`
7. `.agent_work/completed-tasks.md`
8. `.agent_work/tasks/active/` and `.agent_work/tasks/completed/`
9. `.agent_work/decisions/`

Superseded handoff strategies, July roadmap iterations, release checklists, and
external reviews are under
`.agent_work/context/archive/2026-07/Handoff-Planning/`.

The July 23 code-scanning baseline is recorded in
`.agent_work/context/analysis/GITHUB-CODE-SCANNING-READINESS-ASSESSMENT-2026-07-23.md`.
Task-098's merged closeout and the eight documented medium/low torch residuals
are recorded in
`.agent_work/tasks/completed/TASK-098-dependency-security-remediation.md`.
Task-099 records the completed post-closeout advisory remediation, including
the later js-yaml npm audit finding and root graph reconciliation, in
`.agent_work/tasks/active/TASK-099-august-dependency-advisory-follow-up.md`.
Alert `#76` opened after that closeout and its completed remediation record is
`.agent_work/tasks/active/TASK-101-extract-zip-advisory-release-gate.md`.
Task-087 and PR #67 remain preserved historical work. They receive no new
implementation, reconciliation, merge, or review work in the current delivery
window. Package, signing, provider/recovery, Podman, and managed-endpoint gates
are evaluated against the main-based candidate instead.

## Runtime And Package Model

Normal release delivery uses:

- GitHub Release control package
- distinct digest-pinned CPU and CUDA 12.8 GHCR images
- checksummed shared Model & Data Package
- Docker- and Podman-compatible Compose paths

The final support matrix requires:

- Docker CPU
- Docker GPU
- Podman CPU
- Podman GPU/CDI

The existing Pilot validation record remains under
`.agent_work/context/status/Handoff-Planning/v0.1.2-Validation-Evidence/`.
Future candidates require new evidence.

## Runtime Startup Coordination

Before runtime-dependent work, state the engine/profile and verify its observed
availability. When the current session grants W00-W10 implementation scope,
routine validation may continue without repeated confirmation for each command.
An unavailable runtime or required restart is recorded as a blocker while safe
static/planning work continues.

## Safety And Custody

- Do not replace released `v0.1.2` assets.
- Do not publish `v0.1.3` final prematurely.
- Do not modify cdcai without explicit owner authorization.
- Do not mount Docker/Podman sockets into the application container.
- Do not delete named volumes during normal stop or upgrade.
- Do not store provider keys, helper tokens, certificate details, private AOIs,
  raw traces, or unsanitized logs in repository evidence.

The Model & Data Package cannot be reconstructed from source alone. Preserve
release assets, SHA-256 sidecars, `webapp/asset_manifest.v1.json`, and
`docs/release/release-asset-bundle-contract.md`.

## Final Handoff Gate

Before October 30:

- final candidate is qualified and accepted
- official cdcai identity is selected and built consistently
- release, rollback/reject, recovery, and cleanup are rehearsed by the owner
- repository, Actions, package, documentation, video, and backlog custody are
  confirmed
- tool-neutral maintenance guidance is complete
- remaining tasks and risks are explicitly dispositioned
- every code-scanning alert is dispositioned and no release-blocking
  critical/high dependency risk remains unresolved
- no planned work depends on the outgoing developer after October 31

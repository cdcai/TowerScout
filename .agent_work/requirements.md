# TowerScout Requirements

**Last Updated**: August 11, 2026
**Current Planning Horizon**: October 31, 2026 hard project end
**Operational Closeout**: October 30, 2026
**Canonical Roadmap**:
[`2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md`](./context/status/Handoff-Planning/2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md)

This document records the current product, release, and handoff requirements.
The broader prototype-era requirements were archived at
[`2026-07-23-pre-rebaseline-requirements.md`](./context/archive/2026-07/2026-07-23-pre-rebaseline-requirements.md).

## Product Boundary

- TowerScout is a single-user local Windows 11 AMD64 application.
- Google Maps and Azure Maps are first-class supported providers.
- Docker CPU, Docker GPU, Podman CPU, and Podman GPU are equally supported
  final-package profiles when their documented prerequisites are satisfied.
- Mac, ARM64, hosted multi-user deployment, VDI, and fully offline installation
  remain out of scope unless separately validated and approved.
- Detection, manual review, provider switching, export, restore, and setup
  behavior must remain compatible unless an authorized task changes them.

## Pilot And Candidate Requirements

### REL-001: Immutable Pilot Baseline

WHEN development continues during pilot feedback, THE PROJECT SHALL keep the
published fork-side `v0.1.2` pilot assets immutable.

Acceptance:

- The six released assets are not replaced or renamed.
- Pilot users continue to use the existing fork release.
- Any code or package change receives a new version identity.

### REL-002: Fix-First Candidate Line

WHEN owner-requested fixes are implemented, THE PROJECT SHALL produce immutable
fork-side candidates named `v0.1.3-rc.N`.

Acceptance:

- Candidate tags and assets are immutable.
- No `v0.1.3` final release is published before final approval.
- Candidate packages, images, manifests, checksums, source refs, and
  documentation agree on the candidate identity.
- Candidate naming does not reserve or require the final cdcai version.

### REL-003: Final cdcai Identity

WHEN the official cdcai release is prepared, THE cdcai OWNER AND PROJECT LEAD
SHALL select the official tag and display title before the official image and
package are built.

Acceptance:

- The official cdcai package is rebuilt consistently under the chosen version.
- Candidate ZIP files are not merely renamed.
- The cdcai release is published only after owner qualification and adoption
  approval.

### REL-004: Repository Boundary

WHILE the owner-approved feedback and qualification hold is active, THE PROJECT
SHALL NOT overwrite, repoint, or publish the new candidate through
`cdcai/TowerScout`.

Acceptance:

- `J-Schulein/TowerScout` remains the pilot and fix-validation surface.
- `cdcai/TowerScout` remains unchanged until explicit owner authorization.
- Technical access alone is not migration authorization.

## Required Fix And Runtime Requirements

### TLS-001: Guided Provider TLS Repair

WHEN Google Maps or Azure Maps validation encounters a repairable managed-network
certificate trust failure, THE SYSTEM SHALL offer a support-safe guided repair
while retaining the command-based fallback.

Acceptance:

- Google and Azure are supported.
- Docker and Podman are supported.
- The helper remains loopback-only, token-protected, allowlisted, and free of
  arbitrary command execution.
- Provider keys, helper credentials, certificate details, and raw responses are
  not exposed in logs, UI, or evidence.
- Managed-network validation passes before candidate inclusion.

### UX-EXIT-001: User-Initiated Stop

WHEN a user selects Exit/Stop TowerScout and confirms the action, THE SYSTEM
SHALL stop and remove the TowerScout application container without deleting
named volumes.

Acceptance:

- Docker and Podman are supported.
- The UI does not receive unrestricted runtime control.
- Clear success, failure, and manual fallback guidance is provided.
- Persistent configuration, assets, logs, sessions, and user data follow the
  documented lifecycle contract.

### RUNTIME-001: Final Runtime Matrix

WHEN the final candidate is qualified, THE PROJECT SHALL validate all four
advertised profiles:

1. Docker CPU
2. Docker GPU
3. Podman CPU
4. Podman GPU

Acceptance:

- Each profile passes setup, start, readiness, provider configuration,
  detection smoke, persistence, stop, and restart checks appropriate to that
  profile.
- Podman validation uses an approved non-Docker-Desktop Compose provider.
- Podman GPU validates WSL2/NVIDIA CDI prerequisites and CUDA readiness.
- Provider TLS repair and Exit/Stop behavior are exercised on both engines.
- Any remaining limitation is documented and explicitly accepted before
  freeze.

### RUNTIME-002: Podman Trust Separation

IF Podman image-pull or source-build TLS fails, THEN THE PROJECT SHALL treat it
as a Podman-machine/runtime trust issue separate from application-provider TLS.

Acceptance:

- Task-087 is not expanded to silently modify the Podman machine.
- Required final-package blockers are fixed before release.
- Source-build-only limitations may be documented only after an explicit
  Task-097 decision and owner acceptance.

### SEC-001: Dependency Security Baseline And Release Gate

WHEN GitHub code scanning or release validation reports dependency
vulnerabilities, THE PROJECT SHALL classify every finding by package,
call-path reachability, supported runtime impact, fixed-version availability,
and release severity before final-candidate inclusion.

Acceptance:

- Task-090 records a disposition for all 62 Trivy alerts open on `main` as of
  July 23, 2026.
- Approved dependency changes are implemented and validated under Task-098.
- Newly disclosed findings after the completed Task-098 baseline receive a
  unique follow-up task, fixed-version and supported-path classification, and
  proportionate regression evidence before candidate inclusion.
- No release-blocking critical/high finding remains unresolved.
- A residual critical/high finding requires written project-lead/cdcai-owner
  acceptance, compensating controls, and a follow-up disposition.
- The project does not equate a raw zero-alert count with safety; unreachable,
  ambiguous, and no-fix findings require evidence-backed disposition.
- After the baseline is remediated, CI prevents new critical/high findings or
  requires an explicit time-bounded exception.

Current result:

- Task-090 classified the 62-alert baseline and Task-098 implemented the
  approved remediation through PR #51 / merge commit `e499b50`.
- Main CI blocks new or reintroduced critical/high dependency findings while
  retaining all-severity reporting.
- At the July 27 Task-098 closeout, Dependabot reported eight open torch
  advisories—three medium and five low—that are non-reachable on supported
  paths and require a future coordinated torch/torchvision CPU/CUDA
  qualification cycle.
- Four advisories disclosed August 4-5 temporarily raised the inventory to 12:
  two high, five medium, and five low. The August 7 blocking npm audit also
  detected high-severity `js-yaml` advisory `GHSA-5p4m-2wfm-xmqj` before the
  repository inventory assigned it an alert number.
- Task-099 merged the narrow `aiohttp`, transitive `ip-address`, and transitive
  `js-yaml` fixes through PR #68 / `f460445`, then refreshed GitHub's stale
  root dependency snapshot through PR #69 / `0133b50`.
- Root graph run `31510493332` and main CI run `31510488121` passed. Alert
  `#74` closed without dismissal, the SBOM contains only `aiohttp==3.14.3`,
  and the open inventory is exactly the eight documented torch residuals.
- Task-099 is complete and its dependency-security release gate is clear.
  Task-087 signing, candidate inclusion, and final-release qualification
  remain subject to Task-087's own package, signing, and managed-endpoint
  gates.

## Qualification And Handoff Requirements

### QUAL-001: Owner-Runnable Qualification

WHEN a candidate reaches qualification, THE PROJECT SHALL provide a bounded
process the cdcai owner can execute or supervise without the outgoing developer.

### DATA-001: Persistent Data Lifecycle

WHEN the owner rehearses upgrade, rollback, cleanup, or recovery, THE PROJECT
SHALL distinguish container removal from named-volume deletion and require
explicit confirmation for destructive actions.

### DOC-001: Documentation Currentness

WHEN the final candidate is prepared, THE PROJECT SHALL update repository
documentation, release notes, the external Setup Guide, and the demo video to
match the actual package.

Acceptance:

- Administrator documentation explains the opt-in Model Upload Key, including
  secure generation, private storage, rotation, enable/disable behavior, and
  troubleshooting without exposing a real key.
- Approved-model onboarding explains both required controls: the administrator
  key and the model file's approved SHA-256 hash.
- End-user documentation makes clear that normal users do not need the key and
  that model upload remains disabled unless an administrator explicitly
  enables it.

### HANDOFF-001: Tool-Neutral Maintenance Foundation

WHEN ownership transfers, THE PROJECT SHALL provide repository-native,
tool-neutral maintenance procedures and a prioritized Markdown backlog that do
not assume continued Codex or ChatGPT availability.

### HANDOFF-002: Hard Closeout

WHEN October 30, 2026 is reached, THE PROJECT SHALL have completed operational
sign-off, access/custody transfer, task disposition, backlog transfer, and
owner-run release/recovery rehearsal. No planned work may depend on the
outgoing developer after October 31.

## Schedule And Scope Controls

- August 28 is the latest responsible Task-058 capacity checkpoint, not an
  earliest start date.
- September 18 is the internal code-complete target.
- September 25 is the feature/package/documentation-complete target.
- October 9 is the final-candidate freeze target.
- October 16 is the acceptance target.
- October 23 is the owner-operated handoff rehearsal target.
- October 30 is operational closeout.

Task-058 may start early only after Tasks 090, 098, 099, 087, 096, and 097 have
passed their gates. Task-059 remains optional and may start only after Task-058
acceptance without threatening required milestones.

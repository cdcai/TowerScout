# TowerScout October 2026 Fix-First Implementation Roadmap

**Status**: CURRENT - canonical forward execution roadmap
**Approved**: July 23, 2026
**Last Reconciled**: August 6, 2026
**Decision Owners**: Project lead and cdcai owner
**Pilot Baseline**: Immutable fork-side `v0.1.2`
**Candidate Convention**: `v0.1.3-rc.N`
**Operational Closeout**: October 30, 2026
**Hard Project End**: October 31, 2026

## Executive Decision

Use a fix-first approach while pilot users continue testing the unchanged
`v0.1.2` package.

The fork remains the pilot, development, and candidate-validation surface.
`cdcai/TowerScout` remains unchanged until the cdcai owner and project lead
qualify a final candidate and explicitly approve adoption.

Before final-candidate freeze, TowerScout must:

- finish the guided Google/Azure managed-network TLS repair
- add a user-confirmed Exit/Stop TowerScout feature
- qualify Docker CPU, Docker GPU, Podman CPU, and Podman GPU
- clean repository and user-facing documentation
- update the external Setup Guide and demo video
- leave a tool-neutral maintenance and AI-assisted-development foundation
- complete owner-operated qualification, recovery, release, and handoff

Task-058 and Task-059 are stretch work. They cannot displace required release,
runtime, documentation, or handoff work.

## Repository And Release Roles

### `J-Schulein/TowerScout`

- Hosts the immutable `v0.1.2` pilot.
- Hosts development and immutable `v0.1.3-rc.N` candidates.
- Retains pilot, release, and source-provenance history after handoff.

### `cdcai/TowerScout`

- Remains unchanged during the pilot and candidate-development hold.
- Receives only the owner-qualified final baseline.
- Publishes the official final release after the final tag/title decision.

### Release Naming

- Fork candidate tags use `v0.1.3-rc.N`.
- A candidate tag does not reserve or authorize `v0.1.3` final.
- Before official publication, the cdcai owner and project lead select the
  cdcai tag and display title.
- Official images, packages, manifests, checksums, filenames, source refs, and
  documentation are rebuilt consistently for that identity.

## Work Sequence

### Phase 1 - Rebaseline And Investigate

**Target**: July 23-August 14; reforecast after Task-090 classification
**Status**: COMPLETE - Task-090 and Task-098 closed July 27

**August 6 Post-Closeout Amendment**: The July Phase 1 result remains complete
and historical. Four advisories disclosed August 4-5 are owned by the new
Task-099 follow-up rather than reopening Tasks 090/098. Task-099 blocks signing
and candidate inclusion until its critical/high gate and default-branch alert
reconciliation pass; it does not pause ongoing Task-087 non-release work.

1. Task-095 Phase A roadmap/workspace rebaseline and readiness cleanup:
   complete July 23.
2. Task-090 bounded runtime, custom-image, and dependency security
   investigation: complete.
3. The 62-alert baseline was classified and the separate Task-098 scope was
   approved.
4. Task-098 patching, compatibility decisions, regression, and residual
   disposition: complete through PR #51 / `e499b50`.
5. At the July 27 closeout, release-blocking findings were resolved and eight
   non-blocking medium/low torch advisories remained visible for future
   coordinated ML requalification.

July 27 exit evidence:

- One canonical roadmap is active.
- Task state and context navigation are consistent.
- Every open alert has an evidence-backed disposition.
- No unresolved release-blocking critical/high finding remains.
- Any residual critical/high risk has written project-lead/cdcai-owner
  acceptance and compensating controls.
- Required Task-098 remediation is complete.

### Phase 2 - Required Owner Fixes

**Target**: Begin as soon as Phase 1 passes

1. Resume Task-087.
2. Support guided repair for Google and Azure.
3. Support application-provider TLS repair on Docker and Podman.
4. Validate on the available managed CDC network.
5. Complete Task-096 Exit/Stop TowerScout for Docker and Podman.

Exit:

- Guided TLS repair passes security, product, and managed-network gates.
- Exit/Stop safely removes the selected application container while retaining
  named volumes.

### Phase 3 - Podman And Four-Profile Qualification

1. Complete Task-097.
2. Validate Podman without Docker Desktop.
3. Validate approved Compose-provider selection, package-local installer, and
   manual fallback.
4. Validate Podman CPU and GPU/CDI.
5. Validate Task-087 and Task-096 behavior on Podman.
6. Investigate Podman-machine image-pull and source-build TLS separately.

Exit:

- Docker CPU, Docker GPU, Podman CPU, and Podman GPU have defined and passing
  qualification evidence.
- Required packaged-runtime blockers are fixed.
- Any non-blocking source-build limitation is documented and owner-accepted.

### Phase 4 - Conditional Architecture Work

Task-058 may begin immediately when all of the following are true:

- Tasks 090 and 098 are complete.
- Task-099 passes its August dependency-security follow-up gate.
- Task-087 passes managed-network validation.
- Task-096 passes Docker and Podman acceptance.
- Task-097 passes required final-path qualification.
- No pilot blocker requires priority.
- September 18 code complete remains credible.

August 28 is the latest responsible capacity checkpoint, not a wait date.

Task-059 may begin only after Task-058 is accepted and required milestones
remain protected.

### Phase 5 - Qualification, Documentation, And Freeze

Required work:

- Task-091 minimum owner-runnable release qualification
- Task-092 repository/user documentation currentness
- Task-093 persistent-data lifecycle and recovery rehearsal
- Task-094 only when pilot/support evidence justifies it
- Task-095 Phase B governance, backlog, and maintenance handoff

Documentation includes:

- repository README and support docs
- release notes and troubleshooting
- external step-by-step Setup Guide
- replacement demo video
- decision on whether the external guide/video should be linked from README
- public-accessibility checks for linked guide/video when included

Exit:

- September 18: code complete.
- September 25: feature, package, and documentation complete.
- October 9: final candidate frozen; blocker-only change rule begins.

### Phase 6 - Owner Acceptance And Transfer

1. Project lead and cdcai owner qualify the final candidate.
2. Select the official cdcai tag and display title.
3. Build the official cdcai image/package consistently.
4. Exercise release, rollback/reject, recovery, and known-risk procedures.
5. Complete Task-089 only after explicit adoption authorization.
6. Transfer backlog, custody, access, and maintenance procedures.

Exit:

- October 16: acceptance complete.
- October 23: owner-operated handoff rehearsal complete.
- October 30: operational closeout and sign-off complete.
- October 31: no planned work or outgoing-developer dependency remains.

## Task Definitions

| Task | Canonical purpose | Disposition |
| --- | --- | --- |
| `TASK-087` | Universal guided Google/Azure provider TLS repair on Docker/Podman | Required |
| `TASK-088` | Immutable `v0.1.2` pilot distribution and custody | Complete |
| `TASK-089` | Owner-gated cdcai release/adoption and ownership transfer | Required after qualification |
| `TASK-090` | Runtime, custom-image, and dependency-security investigation, including the 62-alert Trivy baseline | Complete July 23 |
| `TASK-091` | Minimum owner-runnable release qualification | Required |
| `TASK-092` | Documentation currentness and information architecture | Required minimum; broader redesign bounded |
| `TASK-093` | Persistent-data lifecycle and recovery rehearsal | Required minimum |
| `TASK-094` | Sanitized support snapshot | Evidence-gated |
| `TASK-095` | Governance and tool-neutral maintenance/handoff foundation | Required; Phase A complete, Phase B through closeout |
| `TASK-096` | User-confirmed Exit/Stop TowerScout | Required |
| `TASK-097` | Podman CPU/GPU final-path hardening and qualification | Required |
| `TASK-098` | Dependency-security remediation, compatibility validation, and release disposition | Complete July 27 |
| `TASK-099` | August dependency-advisory remediation and release-gate reconciliation | Required; in progress |
| `TASK-058` | Background jobs and durable run state | Conditional stretch |
| `TASK-059` | Backend decomposition and logging consolidation | Conditional stretch after Task-058 |

No canonical task file existed for Tasks 090-095 before this rebaseline; their
earlier mentions were provisional planning references. Tasks 096 and 097 were
new unique identifiers at rebaseline. Task-098 was added on July 23 after the
live 62-alert code-scanning inventory established a separate remediation need.
Task-098's project-lead approval gate was satisfied July 23 and the task
completed July 27. cdcai-owner approval remains reserved for residual
critical/high acceptance, changes to `cdcai/TowerScout`, and official
adoption.

Task-099 was added August 6 for alerts `#72-#75`, which GitHub disclosed after
the Task-098 closeout. While it remained active, the August 7 npm audit added
`GHSA-5p4m-2wfm-xmqj`. Its narrow `aiohttp`, transitive `ip-address`, and
transitive `js-yaml` remediation is a required signing/candidate gate and does
not reopen Task-098 or block parallel Task-087 non-release work.

## Stop Rules

Stop or defer optional work when:

- a pilot, security, data-integrity, runtime, or qualification blocker appears
- a critical/high dependency finding remains release-blocking or lacks an
  approved residual-risk disposition
- required work threatens September 18 code complete
- documentation/package work threatens September 25
- a non-blocker change would enter after October 9 freeze
- owner rehearsal or custody work is not on track for October 23

Do not:

- modify released `v0.1.2` bytes
- publish `v0.1.3` final prematurely
- treat candidate naming as the final cdcai decision
- change cdcai without explicit owner authorization
- expose Docker/Podman sockets or arbitrary host commands to the app
- combine application-provider TLS with silent Podman-machine trust changes

## Deferred Decisions With Assigned Gates

These are intentionally not blockers today:

- Final cdcai tag and display title: decide before the official build.
- External guide/video placement in README: decide during Task-092.
- Podman source-build limitation disposition: decide in Task-097 after
  investigation.
- GitHub Issues in addition to the Markdown backlog: decide near handoff.
- Task-094 implementation: decide only from real pilot/support evidence.

## Runtime Startup Coordination

Before runtime-dependent work, the active agent must identify whether Docker
Desktop, Podman, or both are needed and ask the user to start them. Wait for
confirmation before runtime validation because Docker Desktop may require a
workstation restart.

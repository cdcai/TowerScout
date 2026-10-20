# `.agent_work` Workspace Guide

`.agent_work/` is TowerScout's repository-native planning, task, decision, and
handoff workspace. The organization contract is
`.github/instructions/spec-driven-approach.instructions.md`.

## Current Sources

1. [Current tasks](current-tasks.md): remaining delivery and acceptance work.
2. [Owner backlog](task-backlog.md): dated maintenance and optional future work.
3. [Owner maintenance guide](../docs/internal/owner-maintenance.md) and
   [repository map](../docs/internal/repository-map.md): practical navigation.
4. [Handoff navigation](context/status/Handoff-Planning/README.md): accepted
   candidate, operating restrictions, official-delivery work, and dated history.

Acceptance remains defined by the September 21 v2
[prioritization](context/status/Reprioritization%20Effort/2026-09-21-windows-deployment-prioritization-v2.md)
and [work plan](context/status/Reprioritization%20Effort/2026-09-21-windows-deployment-hardening-v2.md),
as amended by ADR-022 through ADR-026. Root AGENTS.md supplies the task-specific
reading order. The accepted exact fork candidate is `v0.1.3-rc5`;
[ADR-026](decisions/026-rc5-bounded-candidate-acceptance.md) records its bounded
acceptance and limitations. Changed official cdcai bytes need their own delta
review, security/integrity checks, and affected qualification.

Chris accepted ownership, Administrative access, delivery direction and the
proposed release name on October 20. Planned delivery is October 27; support
runs October 28-30. Actual adoption, official publication and receipt remain
pending. Historical pilot plans explain earlier decisions; their old holds
and dates do not override the current board or current authorization.

Use [completed tasks](completed-tasks.md) for completed work and the existing
archive for history. Deferred work stays deferred, even when its preserved
record remains under `tasks/active/`; folder location alone is not status.

## Layout

```text
.agent_work/
|-- current-tasks.md
|-- task-backlog.md
|-- completed-tasks.md
|-- requirements.md
|-- design.md
|-- decisions/                 # project-wide numeric ADRs
|-- context/
|   |-- guides/                # small, current evergreen reference set
|   |-- analysis/              # cross-task analysis and retrospectives
|   |-- status/                # current plans and live status
|   `-- archive/YYYY-MM/       # superseded/historical material
|-- tasks/
|   |-- active/                # current sprint task files
|   `-- completed/             # prior-sprint task files
|-- scripts/
|-- tmp/                       # scratch only
`-- pytest-temp/               # scratch only
```

## Task Rules

- `current-tasks.md` is the active sprint source.
- `task-backlog.md` is the future-work source.
- `completed-tasks.md` is the recent completion source.
- Create Type B/C task files when work begins.
- Keep current sprint files in `tasks/active/`.
- Move completed files to `tasks/completed/` at sprint closeout.
- Do not leave task files in the `tasks/` root.
- Do not reuse a task number.

## Context Rules

- Keep active plans in `context/status/`.
- Keep cross-task analysis and retrospectives in `context/analysis/`.
- Keep only current, evergreen references in `context/guides/`; end-user and
  package instructions live under repository-root `docs/`.
- Move superseded drafts, reviews, and snapshots to
  `context/archive/YYYY-MM/`.
- Keep task-local proof and evidence with its task.
- Do not store provider keys, helper tokens, certificate details, private AOIs,
  raw network traces, screenshots, or unsanitized support logs.

Historical RC1 intake material and stale Sprint/source-install guides were
archived under [`context/archive/2026-07/`](./context/archive/2026-07/). Pilot
feedback is maintained externally by the project lead rather than in a live
repository intake workflow.

## Runtime Coordination

Before Docker- or Podman-dependent work, state which runtime/profile will be
used and verify its observed availability. Honor an execution request
authorized in the current session without asking again for each routine
validation step. If a runtime is unavailable or requires a workstation restart,
record that blocker and continue with safe non-runtime work.

## Git Worktree Policy

The root checkout on accepted `main` is the authoritative navigation point for
task state and project-wide planning. A linked worktree is an isolated checkout
of another branch that shares the repository's Git object database; its files
are not an additional source of truth.

- Keep project-wide task state on `main` through reviewed commits. Do not leave
  the only current status update inside a feature worktree.
- Use at most one linked worktree per active branch or pull request, under the
  ignored `.worktrees/` directory.
- Treat planning files visible in a feature worktree as that branch's snapshot,
  not as a synchronized copy of current `main`.
- Before removing a worktree, require a clean status and preserve or push every
  unique commit. Remove the worktree and its branch after the pull request is
  merged or deliberately closed.
- Do not store evidence, caches, environments, or user data in a worktree
  unless the owning task explicitly requires it and its retention is recorded.

## Maintenance

At sprint closeout or material roadmap changes:

1. Reconcile active, backlog, and completed task state.
2. Move completed task files.
3. Archive superseded status material.
4. Update requirements, design, navigation, and handoff sources.
5. Run:

```powershell
python .agents/skills/towerscout-agent-work-hygiene/scripts/check_agent_work_quick.py .
python .agent_work/scripts/validate_agent_work.py
git diff --check
```

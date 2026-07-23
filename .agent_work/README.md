# `.agent_work` Workspace Guide

`.agent_work/` is TowerScout's repository-native planning, task, decision, and
handoff workspace. The organization contract is
`.github/instructions/spec-driven-approach.instructions.md`.

## Current Sources

Read in this order:

1. [`current-tasks.md`](./current-tasks.md)
2. [`context/status/Handoff-Planning/2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md`](./context/status/Handoff-Planning/2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md)
3. [`context/status/Handoff-Planning/PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md`](./context/status/Handoff-Planning/PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md)
4. [`task-backlog.md`](./task-backlog.md)
5. [`requirements.md`](./requirements.md)
6. [`design.md`](./design.md)
7. [`completed-tasks.md`](./completed-tasks.md)

The roadmap controls forward development. The Pilot plan controls the immutable
`v0.1.2` package and cdcai hold.

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

Before Docker- or Podman-dependent work, tell the user which runtime is needed
and ask them to start Docker Desktop and/or Podman. Wait for confirmation
before runtime validation because Docker Desktop may require a workstation
restart.

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

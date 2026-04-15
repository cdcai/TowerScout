# `.agent_work` Workspace Guide

`.agent_work/` is the working documentation area for active planning, sprint tracking, design context, decisions, and validation evidence.

`.github/instructions/spec-driven-approach.instructions.md` is the authoritative source for the organization rules in this folder. This README is the local navigator for humans and agents.

## Layout

```text
.agent_work/
├── current-tasks.md                  # Current sprint source of truth
├── task-backlog.md                   # Future work queue
├── completed-tasks.md                # Historical completion summary
├── requirements.md                   # Structured requirements
├── design.md                         # Current technical design
├── decisions/                        # Project-wide ADRs only (numeric filenames)
├── context/
│   ├── guides/                       # Evergreen how-to and reference docs
│   ├── analysis/                     # Cross-task narrative analysis only
│   ├── status/                       # Active/current sprint status docs
│   └── archive/YYYY-MM/              # Superseded docs and historical snapshots
├── tasks/
│   ├── active/                       # Current sprint task files
│   └── completed/                    # Prior-sprint task files
├── scripts/                          # Reusable workspace utilities
├── tmp/                              # Scratch space, never documentation
└── pytest-temp/                      # Scratch pytest temp area, never documentation
```

## Task Rules

- Keep current sprint task files in `tasks/active/` until sprint closeout, even when their internal status is `COMPLETED`.
- Move finished sprint task files from `tasks/active/` to `tasks/completed/` during sprint closeout.
- Do not leave loose task markdown files at `tasks/` root.
- Keep task-local proof docs, decision memos, scripts, and evidence with the owning task.
- Use same-ID support folders when a task needs extra material, for example `tasks/active/TASK-057/` plus `tasks/active/TASK-057-...md`.

## Decision Rules

- Keep `decisions/` for cross-task or project-wide ADRs only.
- Use numeric ADR filenames such as `014-provider-lock-after-detection.md`.
- Keep task-local decisions out of `decisions/`; store them with the owning task instead.

## Context Rules

- `context/guides/` is for evergreen user or developer guidance.
- `context/analysis/` is for cross-task analysis and reality checks, not task-owned proof artifacts.
- `context/status/` is for active/current sprint plans, retrospectives, live status, and current metrics.
- Archive superseded point-in-time material under `context/archive/YYYY-MM/`.

## Scratch Rules

- `tmp/` and `pytest-temp/` are scratch surfaces only.
- Do not treat scratch folders as durable documentation.
- Remove or refresh scratch contents as needed; they are intentionally ignored from the tracked workflow.

## Maintenance Checklist

1. Move current sprint task docs into `tasks/active/` when sprint planning starts.
2. Re-home task-local memos, proofs, scripts, and raw evidence with the owning task.
3. Archive stale status docs and superseded drafts into `context/archive/YYYY-MM/`.
4. Update this README when the structure changes.
5. Run `python .agent_work/scripts/validate_agent_work.py`.

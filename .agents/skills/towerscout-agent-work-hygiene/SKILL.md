---
name: towerscout-agent-work-hygiene
description: 'Primary skill for TowerScout .agent_work and task-tracking hygiene:
  sprint plans, task files, current/backlog/completed docs, retrospectives, status/context
  docs, decisions, and PR evidence summaries.'
---

# TowerScout Agent Work Hygiene

Use this skill when touching `.agent_work`, task files, sprint plans, backlog/current/completed task docs, context analysis/status/guides/archive, decisions, or PR evidence summaries.

## Goal

Keep TowerScout agent-readable project state accurate, low-noise, and safe to commit.

## Routing rule

Use exactly one TowerScout skill as the primary skill for a task. Add secondary skills only when their specific files or risk surfaces are touched. If the task spans several areas and the primary skill is not obvious, use `$towerscout-skill-router` first.

## Primary versus secondary

Use this as the primary skill for `.agent_work` or planning changes. Use it as a secondary check when a PR adds validation evidence, task summaries, sprint updates, or review artifacts.

## First read

- `.agent_work/README.md`
- `.agent_work/current-tasks.md`
- `.agent_work/task-backlog.md`
- `.agent_work/completed-tasks.md`
- `.agent_work/requirements.md`
- `.agent_work/design.md`
- `.github/instructions/spec-driven-approach.instructions.md` if present
- `.agent_work/scripts/validate_agent_work.py`

## Rules

1. Active sprint work belongs in `.agent_work/current-tasks.md` and `.agent_work/tasks/active/`.
2. Completed prior-sprint task artifacts belong in `.agent_work/tasks/completed/`.
3. Backlog work stays in `.agent_work/task-backlog.md` until selected.
4. Do not put raw logs, screenshots, JSON, TXT, or PNG evidence directly in `context/status/`.
5. Archive superseded status/analysis/guides under `context/archive/` with date scope.
6. Redact provider keys, local AOIs, raw browser-network data, screenshots, and support logs unless explicitly approved.

## Inspect commands (read-only)

```bash
git diff -- .agent_work .github AGENTS.md
python .agents/skills/towerscout-agent-work-hygiene/scripts/check_agent_work_quick.py .
```

## Build/update generated files (mutating)

No standard mutating command. Move/archive task artifacts only when the task explicitly requires that state transition.

## Validation commands

```bash
python .agent_work/scripts/validate_agent_work.py
```

## Output format

Return task-state files changed, validator result, stale or contradictory context found, evidence redaction notes, and suggested commit/PR summary language when useful.

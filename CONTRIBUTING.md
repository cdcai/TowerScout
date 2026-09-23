# Contributing to TowerScout

This repository uses a `main`-only integration workflow with short-lived task branches.

The current delivery effort is defined by the September 21 v2 Windows
deployment [prioritization](.agent_work/context/status/Reprioritization%20Effort/2026-09-21-windows-deployment-prioritization-v2.md)
and [work plan](.agent_work/context/status/Reprioritization%20Effort/2026-09-21-windows-deployment-hardening-v2.md).
PR #67 and the launcher redesign are preserved but deferred and are not release
prerequisites.

## Quick Start

1. Start from the accepted `main` revision selected for the task; freeze that
   revision during release-candidate qualification.
2. Create a focused task branch.
3. Make bounded changes for one task or one task phase.
4. Commit intentional checkpoints as stable slices land.
5. Open a PR against `main`.
6. Squash merge after validation and approval.

For normal task work, update `main` before branching:

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/task-XXX-short-name
```

For release qualification, branch from the accepted SHA recorded by the task
instead of advancing the frozen baseline:

```bash
git fetch origin
git switch -c chore/task-XXX-qualification <accepted-main-sha>
```

## Branch Naming

Use one of these prefixes:

- `feature/task-XXX-short-name`
- `fix/task-XXX-short-name`
- `refactor/task-XXX-short-name`
- `perf/task-XXX-short-name`
- `docs/task-XXX-short-name`
- `chore/task-XXX-short-name`

Examples:

- `feature/task-025-docker-baseline`
- `fix/task-027-error-contract`
- `refactor/task-059-backend-extraction`

## Commit Guidance

- Prefer conventional-commit-style messages when practical.
- Keep each branch readable with 2-4 clean commits instead of one large dump commit.
- Make a commit checkpoint when a bounded slice is working, before switching tasks, and before risky refactors.

Examples:

- `feat(task-025): add Dockerfile and compose baseline`
- `test(task-025): reuse smoke contract in container flow`
- `docs(task-054): document launcher behavior`

## Pull Requests

- Open PRs against `main`.
- Keep PRs focused and reviewable.
- Use stacked PRs only when a child branch truly depends on unmerged parent work.
- Fill out the PR template completely.

PR size guideline:

- small: under about 200 changed lines
- medium: about 200-500 changed lines
- large: about 500-800 changed lines
- oversized: over about 800 changed lines, split unless technically impractical

Generated files, vendor code, binaries, and intentional baseline artifacts do not count the same way as hand-authored reviewable code.

## Validation Expectations

Before requesting review for a code-changing PR:

- run the maintained unit-test baseline
- run the maintained smoke coverage relevant to the touched area
- make sure required CI checks are expected to pass
- document any advisory or skipped validation clearly in the PR

## Review And Merge Policy

- `main` is the only long-lived integration branch.
- Code-changing PRs require 1 approval.
- Required CI checks must pass before merge.
- Resolve review conversations before merge.
- Use `Squash and merge` by default.

## Detailed Policy

See [.github/instructions/github-repo-management.instructions.md](.github/instructions/github-repo-management.instructions.md) for the standing repository workflow policy.

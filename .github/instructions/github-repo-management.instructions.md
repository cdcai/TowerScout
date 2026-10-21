---
applyTo: '**'
---
# GitHub Repo Management Policy

This file defines the standing GitHub branch, PR, and merge policy for TowerScout.

## Core Policy

- `main` is the only long-lived integration branch.
- All new work starts from the latest `main`.
- Do not create or continue work on long-lived sprint branches unless the team explicitly decides to do so for a special transition.
- Open pull requests against `main` by default.
- Use stacked PRs only when a child branch has a real dependency on unmerged parent work.

## Branch Naming

Use short-lived task branches with one of these prefixes:

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

## Pull Request Expectations

- Keep each PR focused on one task or one bounded phase of a task.
- Prefer reviewable PRs over sprint-sized bundles.
- Treat PR size as a heuristic:
  - small: under about 200 changed lines
  - medium: about 200-500 changed lines
  - large: about 500-800 changed lines
  - oversized: over about 800 changed lines, split unless technically impractical
- Generated files, vendor code, binaries, and intentional baseline artifacts do not count the same way as hand-authored reviewable code.
- If a PR is hard to explain in 2-3 sentences, it probably needs to be split.

## Stacked PR Policy

Use stacked PRs only when necessary.

When stacking:

1. Base the child branch on the parent branch.
2. Open the child PR against the parent branch first.
3. Mark the dependency clearly in the PR title or description.
4. Keep the child PR in draft until the parent lands.
5. After the parent merges, rebase the child onto `main`, retarget the PR to `main`, and re-run CI.

Do not stack:

- independent features
- minor follow-up fixes that can wait
- speculative work where the parent may change significantly

## Commit Policy

- Use conventional-commit-style messages with task context when practical.
- Prefer 2-4 clean commits inside a branch rather than one large dump commit.
- A normal branch should usually separate:
  1. prep/docs/task tracker updates
  2. implementation
  3. tests/validation
  4. operator or user docs follow-through
- Avoid mixing unrelated cleanup into task branches.

Examples:

- `feat(task-025): add OCI image and compose baseline`
- `test(task-025): reuse smoke contract in container flow`
- `docs(task-054): document launcher behavior`

## Commit Checkpoint Reminder

- Create an intentional commit checkpoint when a bounded task slice is complete.
- Create a commit checkpoint before switching tasks or starting a risky refactor.
- Agents working in this repo should proactively remind the user when the current work appears commit-ready or branch-ready.

## Merge Policy

- Use `Squash and merge` as the default merge method.
- Do not merge directly into `main`.
- Use merge commits only when preserving branch topology is intentionally valuable.
- Delete a merged head branch only after checking that its commits and
  required evidence are preserved and no other work depends on it. Deferred
  or unmerged branches are not routine cleanup targets.

## Review And Validation Gate

For code-changing PRs to `main`:

- require PR review
- require approval before merge; for cdcai/TowerScout, the user authorized
  Chris's verbal approval instead of a mandatory GitHub approving review
  on October 21, 2026. Record the user's confirmation and approved scope in
  the merge evidence; never imply that a GitHub review occurred. Other
  repositories retain the one-approval policy.
- require required CI checks to pass
- require review conversations to be resolved

Required checks should match the repo's real maintained baseline. These are
review requirements, not proof that GitHub settings enforce them. Inspect the
destination's actual protection/rulesets and checks. Do not change settings
or treat missing enforcement as permission to skip review.

For the one-time fork adoption, compare the whole source delta with cdcai
and record provenance. A large historical adoption diff may be unavoidable;
keep preparation corrections in focused commits and explain review groups.
Do not rewrite or squash historical evidence solely to reduce the file count.

Required:

- lint checks the repo already treats as merge-blocking
- current unit-test baseline
- maintained smoke coverage relevant to the touched area
- the full Docker image build, now blocking before merge as well as on main

Advisory until explicitly promoted:

- Black format check while historical formatting drift remains unresolved
- `mypy`
- `bandit`
- broader integration or browser suites that are still environment-sensitive or non-blocking

Read the current workflows to identify actual blocking steps. Completed
TASK-066/TASK-067 records are historical decisions, not pending promotion work.
An advisory PR check does not waive the accepted security, package or real-
runtime requirements for a release. Do not infer publication readiness from
the CI summary alone.

Validation commands should be bounded. If a pytest module stalls during collection or a runtime smoke can wait indefinitely, split the command, add a timeout or explicit cleanup path, and record the gap instead of repeatedly running broad commands without diagnostics.

## Transition And Baseline Tags

Use annotated milestone tags for major branch and baseline checkpoints.

Format:

- `sprint-XX-milestone-YYYY-MM-DD`

Examples:

- `sprint-04-closeout-2026-04-07`
- `sprint-05-validated-2026-04-15`

Use these tags to preserve important historical checkpoints before deleting transition or sprint branches.

## Required Repo Artifacts

Maintain these repo-level workflow artifacts:

- `.github/PULL_REQUEST_TEMPLATE.md`
- `CONTRIBUTING.md`

Optional later:

- `.github/CODEOWNERS` if reviewer routing becomes necessary

## Contributor Rule Of Thumb

Before starting work:

1. select and record the accepted `main` revision once
2. create a short-lived task branch from that revision
3. keep the branch focused
4. open a PR against `main`
5. make commit checkpoints as the work reaches stable slices
6. merge with squash after validation and approval

For release qualification, freeze the selected source revision and do not pull
or merge newer changes midway through artifact testing. Unmerged PR #67
branches and their evidence are intentionally preserved during the current
main-based delivery window; they are not routine post-merge deletion targets.

If there is any ambiguity, prefer the simpler path:

- branch from `main`
- keep the PR small
- avoid long-lived integration branches

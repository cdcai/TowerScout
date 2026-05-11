# GitHub Repo Management Strategy

**Review Date**: April 15, 2026  
**Version**: v2  
**Purpose**: Document the current GitHub repo/branch state and define a clean repo-management strategy for the remainder of Sprint 5 and into Sprint 6  
**Scope**: GitHub branches, PR flow, branch lifecycle, commit strategy, transition sequencing, and task-to-branch planning  
**Status**: Recommended operating model for post-Sprint-04-closeout and Sprint 5/6 execution

---

## Executive Finding

TowerScout is currently in a transition state between two Git workflows:

- `main` remains the default branch, but it is still effectively at a Sprint 03-era baseline.
- `feature-sprint-04-closeout` exists as a long-lived baseline-preservation branch and has an open draft PR into `main`.
- `feature-sprint-05` was cut directly from that closeout branch and is now the real working branch for current runtime-hardening work.

That structure was reasonable as a temporary safeguard, but it should not remain the long-term operating model. The cleanest path forward is:

1. use `main` as the only long-lived integration branch,
2. merge the validated Sprint 5 baseline back to `main`,
3. retire the sprint branches after merge, and
4. run all remaining Sprint 5 and Sprint 6 work through short-lived task branches and small PRs.

---

## Review Methodology

1. Inspect the live GitHub repository metadata and open PR state.
2. Compare GitHub branch listings to the local branch graph and remote-tracking refs.
3. Review the current repo structure and CI workflow.
4. Map the documented Sprint 5 and Sprint 6 tasks to a sustainable GitHub branching strategy.

---

## Current Repo State

### Repository Facts

- Repository: `J-Schulein/TowerScout`
- Visibility: public
- Default branch: `main`
- Merge methods enabled: merge commit, rebase merge, squash merge
- Auto-merge: disabled
- Update-branch: disabled

### Active/Visible Branches

GitHub currently shows these active branches:

- `main`
- `feature-sprint-04-closeout`
- `feature-sprint-05`
- `improvements`
- `feature/geocoding-system-integration`

Additional local remote-tracking context:

- local refs still show `origin/feature/sprint-03-completion`
- that branch did not appear in the GitHub branch search results used during this review
- this likely means the local remote-tracking refs need a prune/fetch cleanup

### Open Pull Request

There is one open draft PR:

- PR `#2`: `feature-sprint-04-closeout` -> `main`
- Title: `Sprint 04 closeout baseline before Sprint 5`
- State: draft, mergeable

Important nuance:

- the PR body explicitly describes itself as a baseline-preservation PR
- the PR body also explicitly acknowledges known validation debt at that preserved baseline

### Branch Graph Relationship

Current ancestry is straightforward:

- `main` is an ancestor of `feature-sprint-04-closeout`
- `feature-sprint-04-closeout` is an ancestor of `feature-sprint-05`
- `feature-sprint-05` is the real continuation line for current work

This means Sprint 5 is not happening in parallel with Sprint 4 closeout. It is stacked directly on top of it.

---

## Current Structure Assessment

### Strengths

- The repo has a clear default branch and a small enough branch set to clean up without risk.
- Sprint work has been documented carefully in `.agent_work/`, so the history is explainable even if branch names are retired.
- The current task breakdown already separates Docker work from follow-on runtime and architecture work, which maps well to short-lived PR branches.
- The codebase structure is reviewable by subsystem: `webapp/`, `tests/`, `.github/`, and `.agent_work/`.

### Problems

- `main` is lagging behind the branch that represents the actual current project baseline.
- Sprint branches are being used as durable integration branches instead of temporary coordination branches.
- The repo currently has no PR template, no visible contributor workflow doc, and no branch-governance policy document.
- CI still triggers on `improvements`, even though that branch is already fully contained in `main`.
- The open draft PR from `feature-sprint-04-closeout` is useful as historical context, but it is not the best long-term merge artifact if the branch intentionally preserves known test debt.

---

## Key Findings

### Finding 1: `main` Should Become the Only Long-Lived Integration Branch

**Assessment**:
The current sprint-branch flow solved a short-term need, but it creates a confusing repo story if kept indefinitely:

- `main` no longer represents the real project baseline
- Sprint 5 work is effectively hidden behind a branch-on-branch stack
- future tasks would have to choose between stacking on `feature-sprint-05` or diverging from stale `main`

**Recommendation**: HIGH PRIORITY

Use `main` as the only long-lived branch after the current transition.

That means:

1. publish and validate the current Sprint 5 checkpoint,
2. merge the validated Sprint 5 baseline to `main`,
3. delete the sprint branches after merge,
4. branch all new work from `main`.

---

### Finding 2: PR `#2` Should Be Treated as Historical Preservation, Not the Default Merge Vehicle

**Assessment**:
PR `#2` is well-written for historical context, but its own description says:

- it exists to preserve a baseline,
- Sprint 5 already branched from it,
- it carries known validation debt that was intentionally deferred.

That makes it a poor candidate for the definitive path back to `main` unless the team explicitly wants that exact baseline merged unchanged.

**Recommendation**: HIGH PRIORITY

Prefer this sequence:

1. tag the `feature-sprint-04-closeout` baseline commit for historical reference,
2. keep the branch/PR only until that reference is no longer needed,
3. use the validated `feature-sprint-05` state as the real transition PR into `main`.

Suggested tag:

- `sprint-04-closeout-2026-04-07`

### Tag Naming Convention

Use milestone-style annotated tags for major baseline checkpoints, not release-style semantic tags.

Format:

- `sprint-XX-milestone-YYYY-MM-DD`

Examples:

- `sprint-04-closeout-2026-04-07`
- `sprint-05-validated-2026-04-15`
- `sprint-05-docker-baseline-2026-04-XX`

This keeps baseline tags clearly distinct from any future release-version tags.

---

### Finding 3: Older Long-Lived Branches Should Be Retired

**Assessment**:
Both of these branches are already ancestors of `main` and carry no unique commits beyond what `main` already contains:

- `improvements`
- `feature/geocoding-system-integration`

Keeping them active adds noise to the branch list and creates uncertainty about whether they still matter.

**Recommendation**: MEDIUM PRIORITY

Delete those remote branches after confirming there is no external process still depending on their names.

Also prune stale local remote-tracking refs so developers do not keep seeing ghost branches after cleanup.

---

### Finding 4: Sprint 5 and Sprint 6 Work Already Supports a Small-PR Strategy

**Assessment**:
The tracked tasks are already scoped in a way that supports clean PR boundaries.

Sprint 5 remaining work:

- `TASK-025`: Docker containerization
- `TASK-054`: local launch UX
- `TASK-029`: multi-provider fallback (stretch)

Sprint 6 candidates:

- `TASK-058`: background detection jobs and durable run state
- `TASK-059`: backend layer decomposition and logging consolidation
- `TASK-060`: frontend build modernization
- `TASK-061`: coordinated NumPy 2 migration
- `TASK-026`: CPU optimization
- `TASK-027`: enhanced error handling
- `TASK-028`: mobile responsiveness

These should not be merged as sprint-sized mega-branches. They should land as narrow task PRs.

**Recommendation**: HIGH PRIORITY

Adopt one task branch per meaningful unit of delivery, with stacked branches used only when a child task truly depends on an unmerged parent.

---

## Recommended Operating Model

### Branch Model

Use this as the standard model:

- `main`: only long-lived integration branch
- short-lived task branches: all new work starts from `main`
- temporary stacked child branches: only when technically necessary

Do not introduce a long-lived `develop`, `staging`, or sprint branch unless the repo later gains a larger multi-developer release train that truly requires it.

### Merge Strategy

Use `Squash and merge` as the default for all task PRs.

Why:

- it keeps `main` readable
- it avoids preserving noisy fixup commit chains
- it gives each merged PR one clean historical checkpoint tied to one task

Use merge commits only for unusual cases where preserving exact branch topology is materially valuable.

### Review Gate

Recommended minimum gate for code-changing PRs:

- green required CI
- 1 approval
- resolved review comments
- no direct pushes to `main`

For documentation-only PRs, the team can allow a lighter review path if desired, but the default should still be PR-based.

### PR Size Guidance

Treat PR size as a review heuristic, not a rigid rule.

- small: under ~200 changed lines, usually fast review
- medium: ~200-500 changed lines, normal target range
- large: ~500-800 changed lines, acceptable only with clear scope and justification
- oversized: over ~800 changed lines, split unless technically impractical

Exclusions:

- generated bundle output
- vendored third-party code
- binary assets
- intentionally grouped migration or baseline files

If a PR is hard to explain in 2-3 sentences or would take over an hour to review carefully, it should usually be split.

### Stacked PR Protocol

Use stacked PRs only when a child task has a real dependency on unmerged parent work.

Protocol:

1. base the child branch on the parent branch, not `main`
2. open the child PR against the parent branch
3. mark the child PR clearly as dependent in the title or description
4. review the parent first; child review can happen in parallel for early feedback
5. keep child PRs in draft until the parent lands
6. after the parent merges, rebase the child onto `main`, retarget the PR to `main`, and re-run CI

Do not stack:

- independent features
- small follow-up fixes that can wait for the parent to merge
- speculative work where the parent may be rejected or substantially reshaped

---

## Proposed Branch Lifecycle

### Immediate Transition

1. Preserve the Sprint 04 closeout baseline with an annotated tag.
2. Publish the current validated `feature-sprint-05` checkpoint.
3. Run the pre-transition validation checklist on the intended merge head.
4. Tag the validated Sprint 5 checkpoint.
5. Open a transition PR from `feature-sprint-05` into `main`.
6. Merge that transition PR after validation and review.
7. Delete `feature-sprint-05` and `feature-sprint-04-closeout`.
8. Delete stale remote branches already absorbed by `main`.
9. Prune local remotes.

### Normal Ongoing Lifecycle

1. Create a task branch from `main`.
2. Keep the branch focused on one task or one bounded phase of a task.
3. Open the PR early as draft if the work is large.
4. Keep updating the PR as validation evidence lands.
5. Mark ready for review only when the acceptance slice is complete.
6. Squash merge into `main`.
7. Delete the head branch automatically.

### Transition Validation Checklist

Before merging `feature-sprint-05` into `main`, validate the merge head against the current repo reality:

- required: current unit-test baseline passes
- required: current maintained smoke baseline passes
- required: route/config/runtime changes are regression-checked against the core Sprint 4 user flows
- required: known validation debt is either fixed or explicitly documented in the PR
- required: `.agent_work/` status/task docs match the code state being merged
- required: no secrets, temp artifacts, or debug-only files are being introduced
- advisory: broader integration/browser runs if they are available and reliable enough to trust
- advisory: `mypy`, `bandit`, and other currently non-blocking CI checks

Keep this checklist grounded to current CI and validation reality rather than pretending all advisory checks are already mandatory.

### Context Preservation During Cleanup

Do lightweight preservation before deleting sprint branches:

- keep the annotated tag on the Sprint 04 closeout baseline
- keep the merged transition PR as the historical record for the move back to `main`
- add a short transition note under `.agent_work/context/archive/` summarizing why the sprint branches were retired and what validation was performed

Do not over-archive routine GitHub metadata into the repo unless there is a concrete historical need.

---

## Branch Naming Framework

Use consistent prefixes:

- `feature/task-XXX-short-name`
- `fix/task-XXX-short-name`
- `refactor/task-XXX-short-name`
- `perf/task-XXX-short-name`
- `docs/task-XXX-short-name`
- `chore/task-XXX-short-name`

Examples:

- `feature/task-025-docker-baseline`
- `feature/task-025-docker-persistence-smoke`
- `feature/task-054-launcher-mvp`
- `feature/task-029-provider-fallback`
- `refactor/task-058-run-state-foundation`
- `feature/task-058-background-detection`
- `refactor/task-059-backend-extraction`
- `fix/task-059-logging-consolidation`
- `refactor/task-060-frontend-build`
- `chore/task-061-numpy2-upgrade`
- `perf/task-026-cpu-baseline`
- `fix/task-027-error-contract`
- `feature/task-028-mobile-layout`

---

## Commit Framework

### Commit Style

Use conventional-commit style messages with task context.

Examples:

- `feat(task-025): add Dockerfile and compose baseline`
- `test(task-025): reuse host smoke contract in container flow`
- `docs(task-054): document launcher readiness behavior`
- `refactor(task-059): extract detection orchestration helpers`
- `fix(task-027): standardize API error payload handling`

### Commit Boundaries

Prefer 2-4 clean commits inside a branch instead of one large dump commit.

Recommended pattern:

1. design/docs/task tracker prep
2. core code change
3. tests/validation adjustments
4. operator/docs follow-through

Examples:

- simple fix: implementation plus optional docs/test follow-up
- medium feature: implementation, tests, docs
- complex refactor: extraction, call-site migration, tests, architecture docs

Avoid mixing unrelated repo cleanup into task commits.

Before marking a PR ready, collapse obvious fixup commits and review-comment cleanup into a clean, readable history when practical.

---

## PR Framework By Task

### Remaining Sprint 5

#### `TASK-025: Docker Containerization`

Split into two PRs minimum:

**PR 1**  
Branch: `feature/task-025-docker-baseline`

Scope:

- Dockerfile
- compose file
- `.dockerignore`
- model-weight strategy
- runtime env contract

**PR 2**  
Branch: `feature/task-025-docker-persistence-smoke`

Scope:

- volume mounts / persistent directories
- setup/settings persistence verification
- session persistence verification
- reuse of `TASK-052` smoke contract against the containerized app
- CI follow-through for Docker validation as appropriate

#### `TASK-054: Local Launch UX`

**PR 1**  
Branch: `feature/task-054-launcher-mvp`

Scope:

- host launcher
- readiness polling
- browser open behavior
- troubleshooting guidance

Do not merge this into `TASK-025`.

#### `TASK-029: Multi-Provider Fallback`

**PR 1**  
Branch: `feature/task-029-provider-fallback`

Only start after Docker baseline work is stable.

### Sprint 6

#### `TASK-058: Background Detection Jobs and Durable Run State`

Use three PRs:

**PR 1**  
Branch: `docs/task-058-run-model`

Scope:

- design/ADR
- state model
- migration contract

**PR 2**  
Branch: `refactor/task-058-run-state-foundation`

Scope:

- durable run/job primitives
- backend interfaces
- no full frontend cutover yet

**PR 3**  
Branch: `feature/task-058-background-detection`

Scope:

- active detection flow migration
- progress/cancel integration
- end-to-end validation

#### `TASK-059: Backend Layer Decomposition and Logging Consolidation`

Split into two PRs:

- `refactor/task-059-backend-extraction`
- `fix/task-059-logging-consolidation`

#### `TASK-060: Frontend Build Modernization`

Single focused PR:

- `refactor/task-060-frontend-build`

#### `TASK-061: Coordinated NumPy 2 Migration`

Single focused PR:

- `chore/task-061-numpy2-upgrade`

#### `TASK-026: CPU Optimization`

Prefer at least two PRs:

- `perf/task-026-cpu-baseline`
- `perf/task-026-cpu-quantization`

#### `TASK-027: Enhanced Error Handling`

Single focused PR:

- `fix/task-027-error-contract`

#### `TASK-028: Mobile Responsiveness`

Single focused PR:

- `feature/task-028-mobile-layout`

---

## GitHub Configuration Recommendations

### Branch Protection

Apply to `main`:

- require pull request before merge
- require 1 approval
- require required status checks to pass
- require conversation resolution
- restrict direct pushes
- enable automatic branch deletion after merge
- require branches to be up to date before merging when practical
- allow squash merge only
- prefer linear history with squash-only flow

### CI Scope Cleanup

Current CI still includes `improvements`.

Recommended cleanup:

- trigger on `main` for push
- trigger on PRs targeting `main`
- remove `improvements` from workflow triggers

### Required Vs Advisory Checks

Keep the policy aligned to current repo reality:

Required:

- lint/format checks that the team actually expects to block merge
- unit-test baseline
- maintained smoke contract relevant to the touched area

Advisory until deliberately promoted:

- `mypy`
- `bandit`
- broader integration/browser suites that are still non-blocking or environment-sensitive

Do not configure branch protection around aspirational check names that the repo is not consistently producing yet.

### Governance Artifacts

Add these repo-level artifacts:

- `.github/PULL_REQUEST_TEMPLATE.md`
- `CONTRIBUTING.md`

Optional later:

- `.github/CODEOWNERS` if reviewer routing becomes a real team need

### PR Template

Use one standard PR template with these sections:

- Task / issue link
- Summary
- Why
- Validation
- Risk / rollback
- Docs / `.agent_work` updates

### Contributor Workflow Doc

Add a lightweight `CONTRIBUTING.md` that states:

- always branch from `main`
- use the branch naming convention in this document
- open PRs against `main`
- follow the validation and review expectations before merge

### Labels and Milestones

Recommended labels:

- `type:feature`
- `type:fix`
- `type:refactor`
- `type:docs`
- `type:infra`
- `priority:high`
- `priority:medium`
- `priority:low`
- `sprint:05`
- `sprint:06`

Recommended milestones:

- `Sprint 05`
- `Sprint 06`

---

## Recommended Action Plan

### Phase 1: Transition Back To `main`

1. Tag the Sprint 04 closeout baseline.
2. Validate and tag the intended `feature-sprint-05` merge head.
3. Open the transition PR from `feature-sprint-05` to `main`.
4. Merge the validated transition PR.
5. Delete the sprint branches after merge.

### Phase 2: Repo Cleanup

1. Delete `improvements` and `feature/geocoding-system-integration`.
2. Prune local remote-tracking refs.
3. Update CI branch triggers.
4. Add a short transition archive note under `.agent_work/context/archive/`.

### Phase 3: Governance Setup

1. Add branch protection to `main`.
2. Add PR template.
3. Add `CONTRIBUTING.md`.
4. Add labels and milestones.
5. Standardize on squash merge.

### Phase 4: Sprint 5 / Sprint 6 Execution

1. Open one task branch per delivery slice from `main`.
2. Keep large tasks split into reviewable PR phases.
3. Use stacked PRs only when the dependency is real and documented.
4. Keep `.agent_work` task artifacts synchronized with the code PR that implements them.

---

## Success Metrics

- `main` once again reflects the true current project baseline.
- No active work depends on a long-lived sprint branch.
- Every code change lands through a short-lived task PR.
- Old fully-merged branches no longer clutter the branch list.
- Sprint 5 and Sprint 6 work can be reviewed by task slice instead of by sprint-sized bundle.
- Most non-generated PRs stay in a reviewable range and do not routinely exceed the large-PR threshold.

---

## Review Completion Checklist

- [x] GitHub repo metadata reviewed
- [x] Active branch list reviewed
- [x] Open PR state reviewed
- [x] Local branch graph compared to GitHub-visible branches
- [x] Sprint 5 and Sprint 6 tasks mapped to branch/PR strategy
- [x] Recommended long-term branch model defined
- [x] Commit, PR, and transition framework defined

---

**Review Status**: Ready to use as the repo-management strategy reference  
**Next Action**: Convert the current sprint-branch stack back into a `main`-centered PR flow before starting Docker implementation work on the new process

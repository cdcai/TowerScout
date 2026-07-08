# TASK-088: Stable v0.1.0 Release And Handoff Closeout

**Status**: IN_PROGRESS
**Priority**: HIGH
**Type**: C
**Estimated Effort**: 2-4 days
**Target Sprint**: Sprint 07
**Created**: 2026-07-08
**Owner**: TowerScout release owner / active agent support
**Depends On**: `TASK-087` release-boundary decisions; PR #46 merge readiness; stable package validation assets; release-owner disposition on fallback naming and download-home sequencing

## Objective

Execute the bounded work required to cut stable `v0.1.0` from the fork,
validate the rebuilt package set, finalize the user/support handoff material,
and leave a clean release record that can be migrated to `cdcai/TowerScout`
without relying on oral context.

## Canonical Planning Sources

- `.agent_work/context/status/Handoff-Planning/TowerScout-Implementation-Strategy.md`
- `.agent_work/context/status/Handoff-Planning/TowerScout-Handoff-Review-Comprehensive-Analysis.md`

These planning documents remain the detailed evidence base. This task file is
the execution tracker and should record final decisions, scope changes, and
what actually shipped.

## Requirements (EARS Notation)

- WHEN the reviewed handoff work begins, THE SYSTEM SHALL track release and
  handoff execution in formal Sprint 07 task files rather than only in status
  analysis documents.
- WHEN stable `v0.1.0` is cut from the fork, THE SYSTEM SHALL keep the tagged
  source tree, packaged docs, release assets, and published release notes
  internally consistent about the actual download home and runtime image
  namespace used by that fork release.
- WHEN pre-merge and pre-tag cleanup changes are required, THE SYSTEM SHALL
  land them before the stable tag so the published stable release does not rely
  on post-tag corrective edits.
- WHEN stable packages are rebuilt, THE SYSTEM SHALL validate them against the
  replayable fixture baseline and the targeted setup-wizard/manual-smoke checks
  defined in the handoff plan.
- IF stable validation cannot pass by the documented cutoff, THEN THE SYSTEM
  SHALL record an explicit fallback release-identity decision instead of
  silently relabeling RC artifacts.
- WHEN handoff guidance is finalized, THE SYSTEM SHALL capture operator-facing
  release, support, validation, and residual-risk notes in durable repo docs.

## Acceptance Criteria

- [ ] `TASK-088` is reflected in `current-tasks.md` and `task-backlog.md`.
- [ ] The pre-merge cleanup for PR #46 is either completed or explicitly
      dispositioned with evidence.
- [ ] The pre-tag cleanup set is completed and the stable tag/release plan is
      self-consistent for the fork release.
- [ ] Stable `v0.1.0` package validation is recorded with fixture parity,
      readiness, and targeted setup/manual smoke evidence.
- [ ] User/support guides and handoff docs reflect the actual stable release
      path, including explicit handling of fallback naming if fallback is used.
- [ ] Residual decisions from the handoff review are closed or explicitly
      carried forward into `TASK-089` or backlog items.

## Dependencies

- PR #46 must remain mergeable and its reviewed cleanup set must still apply.
- The replayable fixture bundle and validation harness must remain available.
- The stable release needs an explicit decision on fork-versus-cdcai download
  home sequencing before package docs are finalized.
- If fallback is needed, the release owner must approve how RC7.1 identity is
  represented to users.

## Pre-TASK-088 Entry Checklist

This checklist defines what must be true before active fork-side stable-release
execution begins. It is intentionally narrower than the full remaining
`TASK-087` roadmap.

### Must be complete before active TASK-088 execution

- [ ] PR #46 pre-merge cleanup from the handoff strategy is completed or
      explicitly dispositioned, with emphasis on:
      - removing the CI log-publishing residue from
        `task-087-frontend-puppeteer.yml`
      - landing the reviewed coverage-gap fixes that make the dark-gate checks
        meaningful for the served bundle and the setup-wizard contract test
- [ ] PR #46 is merged to `main` and the relevant workflows are green at the
      merge SHA.
- [ ] The release owner confirms the disposition of the optional
      `TOWERSCOUT_SIMULATED_HELPER` cleanup: remove it before tagging, or carry
      it as an explicitly accepted residual risk.

### May land immediately after merge without blocking TASK-088 start

- [ ] Shared rate-limiter key scoping and a non-interference test if the team
      wants that hygiene landed before package validation.

### Explicitly not a TASK-088 start gate

- Simulated-helper `GET /operations/:id` shape alignment. This is required
  before the live helper poll wiring is enabled, not before the dark-helper
  stable release path proceeds.
- Optional helper-unavailable e2e coverage.
- Task-087 enablement work: real helper availability, browser mutation-gate
  opening, live fetch/poll/reconnect wiring, and Gate 4 managed-network helper
  package validation.

## Implementation Plan

1. Translate the reviewed handoff plan into formal task tracking and record any
   remaining strategic gaps discovered during final review.
2. Execute or supervise the fork-side pre-merge and pre-tag cleanup required
   for a trustworthy stable release.
3. Rebuild stable images/packages, validate them, and capture the evidence.
4. Finalize release notes, guidance, and handoff-oriented repo docs.
5. Hand off migration-dependent follow-through to `TASK-089` with the stable
   fork release as the source baseline.

---

## Implementation Log

### 2026-07-08 - Task Creation And Scope Capture
**Objective**: Create a formal task record for the stable release and handoff
closeout work.
**Context**: The reviewed handoff strategy and analysis were detailed and
actionable, but the work itself was only represented in
`.agent_work/context/status/Handoff-Planning/` and not in the sprint task
tracker.
**Decision**: Create `TASK-088` as the active release/handoff execution task,
separate from `TASK-087` control-plane work and from the externally gated
`TASK-089` migration execution task.
**Execution**: Added sprint-tracker entries, created this task file, and folded
the key release/handoff concerns into requirements and acceptance criteria.
**Output**: Formal Sprint 07 task coverage for the stable release and handoff
closeout lane.
**Validation**: Pending `.agent_work` validator run after all task-tracking
edits complete.
**Next**: Create the companion migration task record, then re-review the
Handoff-Planning docs to confirm the task split captures all remaining work.

### 2026-07-08 - Pre-TASK-088 Boundary Clarified
**Objective**: Record exactly which PR #46 and Task-087 items gate the start of
TASK-088.
**Context**: The PR #46 developer packet listed several post-review follow-up
items, but only some of them are true prerequisites for the stable-release and
handoff lane.
**Decision**: Treat the PR #46 release-facing cleanup and merge as the real
entry gate for TASK-088. Keep the rate-limiter scoping issue as optional early
post-merge hygiene, and leave simulated-helper shape alignment, optional helper
unavailable coverage, and live helper enablement work inside the later Task-087
enablement slice.
**Execution**: Added a concrete pre-TASK-088 entry checklist to this task file
and cross-referenced the same boundary in the developer packet.
**Output**: A durable checklist that separates stable-release prerequisites from
later helper-enablement work.
**Validation**: Pending `.agent_work` validator run after this edit.
**Next**: Use this checklist to decide whether PR #46 needs more edits before
merge or can move directly into merge-and-tag preparation.

### 2026-07-08 - PR #46 Merge-Gating Cleanup Applied On Branch
**Objective**: Close the required B1/B3 gaps that were blocking PR #46 from
being treated as merge-ready for TASK-088 entry.
**Context**: The branch still contained CI log-publishing residue and was still
missing the served-bundle freshness check, the setup-wizard contract step in
CI, and the built-bundle dark-gate assertion in the narrow unit test.
**Decision**: Apply the required B1/B3 fixes now and leave the optional
`TOWERSCOUT_SIMULATED_HELPER` decision as the remaining explicit B4
disposition item.
**Execution**: Removed the repo-issue log-publishing steps from
`task-087-frontend-puppeteer.yml`, deleted `scripts/ci_publish_issue.py`, added
the bundle-freshness and setup-wizard contract checks to `ci.yml`, and
strengthened `tests/unit/test_frontend_provider_tls.py` to assert the dark gate
in the built bundle as well as the source file.
**Output**: The branch now satisfies the required B1/B3 checklist items.
**Validation**: `node tests/frontend/test_setup_wizard_validation_contract.js`
passed; `./.venv/Scripts/python -m pytest tests/unit/test_frontend_provider_tls.py -q`
passed; `node webapp/build.js && git diff --exit-code -I "Build Date" webapp/js/towerscout.js`
passed; no remaining `ci_publish_issue.py` references remain under `.github/`
or `scripts/`; touched files reported no editor diagnostics.
**Next**: Get an explicit B4 disposition for `TOWERSCOUT_SIMULATED_HELPER`,
then decide whether PR #46 can move directly into merge preparation.

### 2026-07-08 - B4 Closed By Removing Simulated Helper Routes
**Objective**: Close the remaining B4 disposition item before treating PR #46
as merge-ready for TASK-088 entry.
**Context**: The simulated-helper block was default-off, undocumented,
unsupported in the packaged runtime path, and redundant with the separate
Node-based test helper already used by CI.
**Decision**: Remove the dormant simulated helper endpoints from the shipped
Flask app rather than carrying them as an accepted residual risk.
**Execution**: Deleted the `TOWERSCOUT_SIMULATED_HELPER`-gated block from
`webapp/towerscout.py`.
**Output**: The unsupported unauthenticated test endpoints are no longer part
of the shipped Flask app.
**Validation**: `./.venv/Scripts/python -m pytest tests/unit/test_flask_routes.py -q`
passed; `./.venv/Scripts/python -m pytest tests/unit/test_frontend_provider_tls.py -q`
passed; `node tests/frontend/test_setup_wizard_validation_contract.js` passed;
no editor diagnostics reported for `webapp/towerscout.py`.
**Next**: Treat the pre-merge cleanup gate as complete and decide whether any
additional non-blocking hygiene should land before PR #46 merge preparation.

### 2026-07-08 - Broader Merge-Prep Validation Pass
**Objective**: Increase confidence that the remaining PR-facing cleanup is safe
to carry into PR #46 merge preparation.
**Context**: After the required B1/B3/B4 changes, the branch still needed one
broader focused validation pass over the Task-087 / PR46 unit slices most
likely to reflect cleanup regressions.
**Decision**: Treat the PR-facing code cleanup as merge-prep ready if the
broader focused suite remains green, and classify any `test_config.py` failures
caused by local TLS-bundle environment state as a local environment issue
rather than a blocker for PR #46.
**Execution**: Ran a broader focused suite over `test_config.py`,
`test_geocoding.py`, `test_provider_http.py`, `test_release_package_script.py`,
and `test_task_087_host_helper.py`; reran the failing `test_config.py` slice
with `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` unset to disambiguate local
environment behavior from branch regressions.
**Output**: All focused slices except the first local `test_config.py` run were
green. `test_config.py` passed completely once the TLS-bundle env vars were
unset, so the observed failures were environment-dependent and not caused by
the PR-facing cleanup.
**Validation**: `./.venv/Scripts/python -m pytest tests/unit/test_config.py tests/unit/test_geocoding.py tests/unit/test_provider_http.py tests/unit/test_release_package_script.py tests/unit/test_task_087_host_helper.py -q` -> 62 passed / 6 failed in `test_config.py`; `unset REQUESTS_CA_BUNDLE SSL_CERT_FILE && ./.venv/Scripts/python -m pytest tests/unit/test_config.py -q` -> 16 passed.
**Next**: Keep the PR-facing diff limited to `.github/workflows/ci.yml`, `.github/workflows/task-087-frontend-puppeteer.yml`, `tests/unit/test_frontend_provider_tls.py`, `webapp/towerscout.py`, and deletion of `scripts/ci_publish_issue.py`; manage the `.agent_work` task-tracking edits separately from PR #46 code cleanup.

### 2026-07-08 - PR-Facing Cleanup Isolated For Merge Prep
**Objective**: Separate the PR #46 code/workflow cleanup from the unrelated
handoff and task-tracking documentation work.
**Context**: The branch now contains both merge-prep code changes and separate
`.agent_work` updates for `TASK-088` / `TASK-089` and the handoff planning
record.
**Decision**: Keep the PR-facing cleanup as a self-contained staged set and
leave the `.agent_work` changes unstaged so they can be managed independently.
**Execution**: Staged only `.github/workflows/ci.yml`,
`.github/workflows/task-087-frontend-puppeteer.yml`, deletion of
`scripts/ci_publish_issue.py`, `tests/unit/test_frontend_provider_tls.py`, and
`webapp/towerscout.py`.
**Output**: The staged cleanup set is now limited to the exact PR #46
merge-prep code changes, while task-tracking and handoff files remain outside
that staged set.
**Validation**: `git diff --cached --check` passed; staged diff summary = 5
files changed, 11 insertions, 334 deletions; unstaged tracked changes remain
limited to `.agent_work/current-tasks.md` and `.agent_work/task-backlog.md`.
**Next**: Treat the staged set as commit-ready for PR #46 merge prep and keep
the `.agent_work` task/handoff work as a separate follow-on change set.

---

## Validation Results

### Test Summary
**Test Date**: Pending
**Test Environment**: Pending
**Test Status**: PENDING

### Acceptance Criteria Validation
- [x] **Task tracking created**: Completed 2026-07-08
- [x] **Pre-merge cleanup dispositioned**: Completed 2026-07-08
- [ ] **Pre-tag cleanup completed**: Pending
- [ ] **Stable package validation recorded**: Pending
- [ ] **Guidance and handoff docs finalized**: Pending
- [ ] **Residual decisions closed or delegated**: Pending

### Issues Identified

- The handoff plan still requires explicit resolution of fork-versus-cdcai
  namespace sequencing before the first public stable package is finalized.
- If `rc7.1` fallback is used, release identity must be handled explicitly in
  docs and release notes rather than treated as an invisible relabel.
- Local `test_config.py` runs can fail if the shell carries TLS-bundle
  environment state; unsetting `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` before
  that slice restores the expected local baseline.

### Sign-off

Pending
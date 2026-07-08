# TASK-088: Stable v0.1.0 Release And Handoff Closeout

**Status**: IN_PROGRESS
**Priority**: HIGH
**Type**: C
**Estimated Effort**: 2-4 days
**Target Sprint**: Sprint 07
**Created**: 2026-07-08
**Owner**: TowerScout release owner / active agent support
**Depends On**: `TASK-087` release-boundary decisions; merged `main` baseline at `d148727`; stable package validation assets; release-owner disposition on fallback naming and download-home sequencing

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

- Merged `main` at `d148727` is the baseline for fork-side stable release work.
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

- [x] PR #46 pre-merge cleanup from the handoff strategy is completed or
      explicitly dispositioned, with emphasis on:
      - removing the CI log-publishing residue from
        `task-087-frontend-puppeteer.yml`
      - landing the reviewed coverage-gap fixes that make the dark-gate checks
        meaningful for the served bundle and the setup-wizard contract test
- [x] PR #46 is merged to `main` and the relevant workflows are green at the
      merge SHA.
- [x] The release owner confirms the disposition of the optional
      `TOWERSCOUT_SIMULATED_HELPER` cleanup: remove it before tagging, or carry
      it as an explicitly accepted residual risk.

### May land immediately after merge without blocking TASK-088 start

- [ ] Shared rate-limiter key scoping and a non-interference test if the team
      wants that hygiene landed before package validation.

### Validation Prerequisite

- [ ] The validation cell `.env` is confirmed to carry the post-rotation Azure
  key before the D4 live-smoke and setup-wizard checks begin.

### External Guide Tracking

- [ ] Workstream F guide edits (F1-F9 in the implementation strategy) are
  explicitly tracked to completion, including ownership of the out-of-repo
  deck/docx/html updates.

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
2. Execute the fork-side post-merge pre-tag source pass required for a
  trustworthy stable release.
3. Rebuild stable images/packages, validate them, and capture the evidence.
4. Finalize release notes, guidance, and handoff-oriented repo docs.
5. Hand off migration-dependent follow-through to `TASK-089` with the stable
   fork release as the source baseline.

## Current Execution Slice

The current Task-088 slice is the post-merge pre-tag source pass from the
implementation strategy.

### Immediate Checklist

- [x] Merge upstream `cdcai/main` into the fork branch and resolve the README
    conflict using the reviewed recipe.
- [x] Decide the fork-side stable release download-home wording and keep it
    self-consistent with the actual fork-published `v0.1.0` artifacts.
- [x] Complete the required documentation fixes for host-helper docs,
    provenance, cross-references, and SBOM/HANDOFF posture.
- [x] Decide whether to take any of the optional dead-code deletions before the
  stable tag.
- [x] Remove the stale `v0.1.0` tag and prepare the fresh stable tag flow.

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

### 2026-07-08 - Post-Merge Baseline Established
**Objective**: Transition TASK-088 from pre-merge gating into the active
post-merge release-closeout slice.
**Context**: PR #46 has now merged to `main` as `d148727`, and the helper
control-plane cleanup/hardening needed to start Task-088 is complete.
**Decision**: Treat the pre-merge gate as closed and move Task-088 to the
implementation strategy's Workstream C pre-tag source pass.
**Execution**: Rebased the handoff-tracking work onto fresh `main` via the
`docs/task-088-stable-handoff` branch and preserved the release/handoff task
tracking there.
**Output**: Task-088 now starts from merged `main` instead of the former
Task-087 feature branch state.
**Validation**: Local `main` fast-forwarded to `d148727`; fresh Task-088 branch
created from that baseline; `.agent_work` validation passed on the new branch.
**Next**: Execute the pre-tag source pass checklist, beginning with the
upstream `cdcai/main` merge and the required documentation fixes.

### 2026-07-08 - Upstream Merge And Documentation Slice Started
**Objective**: Begin the post-merge pre-tag source pass with the two lowest-risk
required items: the reviewed upstream merge and the first cluster of required
documentation fixes.
**Context**: Task-088 had transitioned onto fresh `main`, but the upstream
`cdcai/main` merge and several required release docs still needed to be brought
into the branch before tagging work could continue.
**Decision**: Take the reviewed README-only upstream merge first, then land the
host-helper/provenance/cross-reference documentation slice as the first Task-088
content pass.
**Execution**: Merged `upstream/main` into this branch with the reviewed README
resolution; updated `README.md` provenance text; corrected the stale path in
`DATA_LICENSES.md`; corrected the TASK-025 pointer in
`docs/support/oci-runtime-contract.md`; updated the package guide's stale
helper note; and created `docs/support/host-helper.md` documenting the shipped
but disabled helper scaffolding.
**Output**: The branch now includes the required upstream enterprise notice and
the first set of pre-tag documentation fixes needed for the stable release.
**Validation**: `git diff --check` over the touched docs passed; README,
package-guide, runtime-contract, host-helper, and data-license files reported
no editor diagnostics; `.agent_work` validation remained green after the task
tracker update.
**Next**: Continue the documentation cluster with the remaining required items,
especially `HANDOFF.md`, the stale `.github/copilot-instructions.md` decision,
and the SBOM posture decision.

### 2026-07-08 - HANDOFF And SBOM Posture Slice
**Objective**: Land the handoff-facing release documentation and correct the
repo's self-described SBOM posture before package assembly begins.
**Context**: The first documentation slice covered host-helper status and path
fixes, but Task-088 still needed the explicit handoff guide and an honest SBOM
story in both the checked-in files and the package-generation script.
**Decision**: Create `HANDOFF.md` now and soften the SBOM language to an honest
deferred posture rather than falsely claiming automatic release-candidate SBOM
generation.
**Execution**: Added `HANDOFF.md`; updated `SBOM.txt`,
`release-manifest.v1.json`, and `scripts/package-release.ps1`; and preserved
the package-guide/runtime-contract/README/data-license fixes from the current
documentation slice.
**Output**: The handoff notes now document CI gates, automated-vs-manual
verification boundaries, asset-bundle custody, accepted risks, and migration
limits, and the release metadata no longer over-claims automatic SBOM
generation.
**Validation**: `git diff --check` over `HANDOFF.md`, `SBOM.txt`,
`release-manifest.v1.json`, and `scripts/package-release.ps1` passed; those
files reported no editor diagnostics; `./.venv/Scripts/python -m pytest tests/unit/test_release_package_script.py -q` passed.
**Next**: Decide the remaining release-home wording and whether to refresh or
remove `.github/copilot-instructions.md` before starting package assembly.

### 2026-07-08 - Stale `v0.1.0` Tag Removed
**Objective**: Free the stable `v0.1.0` tag name for the real Task-088 release
cut.
**Context**: The old `v0.1.0` tag still pointed at the historical `e78974d`
milestone commit and would have blocked or confused the stable tag cut.
**Decision**: Remove the stale tag locally and on `origin` now, before package
assembly begins.
**Execution**: Deleted local tag `v0.1.0` and pushed the matching tag deletion
 to `origin`.
**Output**: The stable tag name is now free for the real release cut.
**Validation**: `git tag -l v0.1.0` returned nothing and `git ls-remote --tags origin refs/tags/v0.1.0 refs/tags/v0.1.0^{}` returned no matches.
**Next**: Continue the remaining pre-tag documentation decisions, then move to
image/package assembly from the cleaned tag namespace.

### 2026-07-08 - Fork-Side Release-Home Decision Recorded
**Objective**: Close the release-home wording decision for the fork-side stable
release before package assembly begins.
**Context**: The reviewed handoff plan requires the fork-published stable
release to remain self-consistent and explicitly warns against repointing users
at a cdcai release or GHCR namespace that does not yet exist.
**Decision**: Keep the fork-side stable `v0.1.0` package-facing release URLs
and image references on the fork/J-Schulein side for this release cut. Defer
the `cdcai` rewrite to `TASK-089` when the cdcai rebuild/release actually
exists.
**Execution**: Verified that the current package-facing release URLs and image
defaults still consistently point at the fork-side release/registry surfaces.
**Output**: The fork-side stable release wording is now an explicit Task-088
decision rather than an implicit holdover.
**Validation**: Verified current release URLs still point to
`https://github.com/J-Schulein/TowerScout/releases`, and current package-facing
image defaults still point to `ghcr.io/j-schulein/towerscout`.
**Next**: Finish the remaining documentation decisions, especially the stale
`.github/copilot-instructions.md` disposition, before package assembly begins.

### 2026-07-08 - Copilot Instructions Refreshed And Optional Deletions Deferred
**Objective**: Close the last required documentation decision and explicitly
disposition the optional dead-code pass before package assembly begins.
**Context**: The remaining required documentation item was the stale
`.github/copilot-instructions.md` status/path-forward guidance. The optional
dead-code deletions remained available but were not release-blocking.
**Decision**: Refresh `.github/copilot-instructions.md` narrowly to the current
post-merge Task-088/Task-089 state and defer the optional dead-code deletions
to later follow-up so the stable release path stays focused on bounded required
changes.
**Execution**: Updated the stale status/path-forward sections of
`.github/copilot-instructions.md` and explicitly chose not to take the optional
dead-code deletion bundle before the stable tag.
**Output**: The required documentation cluster is complete, and the optional
dead-code question is now an explicit defer rather than an unresolved item.
**Validation**: Targeted grep/readback over `.github/copilot-instructions.md`
confirmed the stale Sprint 06 / RC1 / Task-073 path-forward language was
removed; no editor diagnostics reported for the file; `.agent_work` validation
remained green.
**Next**: Enter release assembly: verify the located asset-bundle ZIP choice,
create the fresh `v0.1.0` tag, and dispatch the CPU/CUDA image builds.

### 2026-07-08 - Asset Bundle Source Verified
**Objective**: Lock the source of the shared Model & Data Package ZIP before
starting stable package assembly.
**Context**: Task-088 package assembly reuses the validated rc7.1 asset bundle
under a renamed stable filename, so the exact source ZIP and checksum needed to
be re-verified on the current workstation.
**Decision**: Use the copy under `../TS Release Packages/TowerScoutRC7.1/` as
the canonical local source for the stable-release asset-bundle rename step.
**Execution**: Verified that the selected ZIP and its `.sha256` sidecar match,
then cross-checked the other discovered local copies in `../Downloads/` and
`../TowerScoutDemo/` to confirm they are byte-identical.
**Output**: A known-good local source exists for the stable asset-bundle rename
and sidecar regeneration step.
**Validation**: The selected ZIP hash is
`00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`, matching
its sidecar and all other discovered local copies.
**Next**: Enter release assembly from a clean git tree: create the fresh
`v0.1.0` tag, dispatch CPU/CUDA image builds, and assemble the release
packages from the returned digests.

### 2026-07-08 - Review-R1 Pre-Tag Guardrails Added
**Objective**: Fold the remaining high/medium review findings into Task-088
before the stable tag exists.
**Context**: External review R1 identified several sequencing and hygiene gaps
that were not large rework, but did need explicit ownership before tag/build.
**Decision**: Address the low-risk repo/package/workflow fixes now, add the
namespace and validation-key tracking rules to the task files, and keep the
manual account-level checks as explicit pending items.
**Execution**: Added the validation `.env` prerequisite and Workstream F guide
tracking to this task file, while related namespace, workflow, package-guide,
and `.gitignore` fixes were applied in the working tree.
**Output**: The pre-tag tracker now covers the reviewer-raised prerequisites
that could otherwise be lost between release assembly and later migration work.
**Validation**: Pending after the current fix batch is validated.
**Next**: Validate the current fix batch, then update the review log/status and
re-check tag/build readiness.

### 2026-07-08 - Settings-Linked Docs Refreshed
**Objective**: Update the docs exposed through the Settings screen so they no
longer present stale release-candidate wording during the stable-release
closeout.
**Context**: The Settings UI links directly to Quick Start, Project Overview,
and User Guide content. Those docs still described the package path as a
release-candidate/RC7 baseline even though Task-088 is preparing the stable
`v0.1.0` cut.
**Decision**: Refresh the Settings-linked docs and their markdown sources to
neutral or stable-closeout wording, but keep the historical `v1-rc1-*` and
`towerscout-user-guide.*` compatibility stubs in place because they are still
publicly served and covered by route tests.
**Execution**: Updated `docs/quick-start.{md,html}`,
`docs/project-overview.{md,html}`, and `docs/user-guide.{md,html}`.
**Output**: The docs reachable from Settings now describe the current package
path more accurately without breaking the compatibility-doc route surface.
**Validation**: `git diff --check` over the six updated docs passed; all six
files reported no editor diagnostics.
**Next**: Checkpoint the completed Task-088 documentation slice, then move into
tag creation and image/package assembly from a clean tree.

---

## Validation Results

### Test Summary
**Test Date**: Pending
**Test Environment**: Pending
**Test Status**: PENDING

### Acceptance Criteria Validation
- [x] **Task tracking created**: Completed 2026-07-08
- [x] **Pre-merge cleanup dispositioned**: Completed 2026-07-08
- [x] **Task-088 entered from merged main baseline**: Completed 2026-07-08
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
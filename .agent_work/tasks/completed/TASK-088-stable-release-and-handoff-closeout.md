# TASK-088: Stable Release And Handoff Closeout

**Status**: COMPLETED - pilot sent, support coverage confirmed, and durable release/evidence custody recorded
**Priority**: HIGH
**Type**: C
**Estimated Effort**: 2-4 days
**Target Sprint**: Sprint 07
**Created**: 2026-07-08
**Owner**: TowerScout release owner / active agent support
**Depends On**: validated `v0.1.2` package assets; completed pilot communication; confirmed support coverage; durable evidence custody; clean fork-side handoff state

## Objective

Close out the validated fork-side `v0.1.2` release as the frozen pilot baseline,
record the completed pilot distribution/support state, and leave a clean
handoff record for the hard 2026-10-31 project end date. Keep
`cdcai/TowerScout` unchanged until its
owner reviews pilot feedback and approves an adoption baseline. `v0.1.0` and
`v0.1.1` remain historical tag/image identities with no final GitHub Release
assets.

## Canonical Planning Sources

- `.agent_work/context/status/Handoff-Planning/PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md`
- `.agent_work/context/archive/2026-07/Handoff-Planning/TowerScout-Implementation-Strategy.md` (historical release execution plan)
- `.agent_work/context/archive/2026-07/Handoff-Planning/TowerScout-Handoff-Review-Comprehensive-Analysis.md` (historical evidence base)

The pilot/adoption plan is the current decision source. The older planning
documents remain evidence for how the release was built and reviewed, but their
immediate-migration dates and version-specific commands are not current
instructions. This task file tracks what actually shipped and what remains for
pilot readiness.

## Requirements (EARS Notation)

- WHEN the reviewed handoff work begins, THE SYSTEM SHALL track release and
  handoff execution in formal Sprint 07 task files rather than only in status
  analysis documents.
- WHEN a stable release identity is cut from the fork, THE SYSTEM SHALL keep the tagged
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
- WHEN the `v0.1.2` pilot is distributed, THE SYSTEM SHALL identify the fork as
  the pilot download, distinguish the unchanged official cdcai repository, and
  name an organization-controlled feedback/support destination.
- WHILE pilot feedback is pending, THE SYSTEM SHALL NOT modify, repoint, or
  publish pilot artifacts through `cdcai/TowerScout` without explicit owner
  approval.
- IF pilot feedback requires a package change, THEN THE SYSTEM SHALL use a new
  version identity and proportionate validation rather than replacing the
  validated `v0.1.2` assets.
- WHEN the project ends on 2026-10-31, THE SYSTEM SHALL leave the cdcai owner
  a durable release, evidence, feedback, backlog, and migration-preparation
  handoff that does not depend on the current developer remaining available.

## Acceptance Criteria

- [x] `TASK-088` is reflected in `current-tasks.md` and `task-backlog.md`.
- [x] The pre-merge cleanup for PR #46 is either completed or explicitly
      dispositioned with evidence.
- [x] The pre-tag cleanup set is completed and the stable tag/release plan is
      self-consistent for the fork release.
- [x] Stable `v0.1.2` package validation is recorded with fixture parity,
      readiness, and targeted setup/manual smoke evidence.
- [x] User/support guides and handoff docs reflect the actual stable release
      path, including explicit handling of fallback naming if fallback is used.
- [x] Residual decisions from the handoff review are closed or explicitly
      carried forward into `TASK-089` or backlog items.
- [x] The `v0.1.2` GitHub Release is promoted/published as the final fork-side
      stable release with the validated six-asset set and final notes.
- [x] Pilot-facing communication identifies the fork-side `v0.1.2` download,
      the unchanged official cdcai repository, and the selected feedback path.
- [x] The external Word-document feedback method and primary/backup support
      coverage are confirmed, with appropriate access.
- [x] Release assets, checksums, validation summary, known findings, and
      troubleshooting material have durable owner-accessible custody.
- [x] The cdcai repository is intentionally unchanged pending feedback review
      and explicit adoption approval.

## Dependencies

- The validated fork baseline is `v0.1.2` at
  `718a56485a59182f060a537e8f11d4ce71a1f0d4`.
- The replayable fixture bundle and validation harness must remain available.
- Pilot feedback is maintained by the project lead in a fillable Word document
  outside the repository; intake and tracking are not duplicated here.
- Primary and backup support contacts are confirmed with appropriate access.
- The existing `v0.1.2` assets remain immutable; fixes require a new version.

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

- [x] The validation cell used the post-rotation Azure key for the D4
  live-smoke and setup-wizard checks; the local secret file was deleted at run
  end and no key value was recorded in evidence.

### Pilot Guide And Support Tracking

- [x] The July 13 pilot email/setup guide uses the current pilot/adoption wording
  and does not direct users to the unchanged cdcai repository for the pilot.
- [x] The sent pilot material was checked against
  the `v0.1.2` filenames, commands, download location, and feedback destination.
- [x] A backup support owner has access to the final guide and support material.

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
4. Finalize release notes, pilot guidance, feedback routing, and handoff docs.
5. Preserve owner-accessible release/evidence custody and a no-extension
   closeout package.
6. Hand migration preparation to `TASK-089`, with execution deferred until
   feedback review and explicit cdcai-owner adoption approval.

## Current Execution Slice

The Task-088 slice is complete. Release build, validation, publication, pilot
distribution, support coverage, and durable custody are recorded. The project
is extended through 2026-10-31; later implementation work is outside this task.

### Immediate Checklist

- [x] Freeze the existing six-asset `v0.1.2` release as the validated pilot
  baseline.
- [x] Finalize the pilot email/setup-guide wording and external feedback method.
- [x] Confirm backup support ownership and owner-accessible artifact/evidence
  custody.
- [x] Reconcile the final Task-088/089 and handoff records on a clean
  `origin/main@718a564` branch without reverting PR #48 runtime/test changes.
- [x] Keep `cdcai/TowerScout` unchanged during the feedback hold.
- [x] Prepare a send-ready pilot message, pre-send gate, structured feedback
  intake/triage template, and owner-custody checklist.

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

### 2026-07-08 - Owner Account Checks Recorded For R1-08
**Objective**: Close the remaining manual fork-repository account checks from
R1-08 before tag/build execution proceeds.
**Context**: External review R1 left the fork homepage field and logged-in
draft-release check as explicit owner-account actions that could not be fully
verified from local git state.
**Decision**: Record the repo-owner confirmation directly in Task-088 and treat
the visible `Pre-release` badges as non-blocking because they are published
releases, not unpublished drafts.
**Execution**: The repo owner updated the repository homepage URL on GitHub to
the correct site location and reviewed the Releases page while logged in. The
visible releases carried `Pre-release` badges only, and no entries were marked
`Draft`.
**Output**: Task-088 now carries explicit evidence that the dead homepage link
was corrected and that no owner-visible draft releases remain.
**Validation**: Owner manual check on github.com: homepage field updated to the
correct live site location; Releases page reviewed while logged in and no
`Draft` badge observed on any release entry.
**Next**: Keep the branch/tag flow on the R1-01 sequencing path, then proceed
with the merge-to-`main`, CI-green, and stable-tag steps.

### 2026-07-08 - Stable Tag, Image Digests, And Control Packages Captured
**Objective**: Cut the stable tag, capture immutable image references, and
assemble the release control packages from the tagged baseline.
**Context**: `main@dfe9e6b` was green and cleared by the external pre-tag
review. The remaining release-assembly gate was to publish the CPU/CUDA images,
capture their digests, and rebuild the control packages from a clean tagged
tree.
**Decision**: Create and push annotated tag `v0.1.0`, use the published GitHub
Actions metadata as the digest source of truth, and build the packages from a
detached `v0.1.0` worktree so the release guardrails see a clean git state.
**Execution**: Created and pushed `v0.1.0`; dispatched `container-publish.yml`
for CPU and CUDA; downloaded `image-metadata.json` artifacts from runs
`28969615686` and `28969617992`; captured digests
`sha256:0c1ea5035acefca81f2c099c65cc89badcbc120c0bbbc2662303233c34f25f5b`
and `sha256:9f1563eb18eee12e0344f43d83a53072f84c9811482915f299e1c87fc5ed9c68`;
created detached worktree `../TowerScout-v0.1.0-build`; built
`towerscout-v0.1.0-cpu.zip` and `towerscout-v0.1.0-cuda121.zip` into
`../TowerScout-v0.1.0-packages/` with the verified asset-bundle checksum
`00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
**Output**: Stable tag `v0.1.0` exists on origin; published images are pinned
to immutable GHCR digests; clean control-package ZIPs and checksum sidecars
exist for both CPU and CUDA variants.
**Validation**: Both workflow runs succeeded; the packaged ZIP sidecars verify
after CRLF normalization; `IMAGE.txt` inside each ZIP carries the expected
digest-pinned image reference; `release-manifest.v1.json` inside each ZIP names
asset bundle `towerscout-v0.1.0-assets-towerscout-v1-assets-2026-05-05.zip`
with the expected SHA-256.
**Next**: Complete the remaining D4 validation pass against the rebuilt stable
packages and capture that evidence before final release publication closes.

### 2026-07-08 - Package Gate Checks And Optional Podman CPU Smoke
**Objective**: Execute the strongest bounded validation available on this host
before the full D4 pass, and determine whether the rebuilt CPU package can
still reach readiness on the Podman path.
**Context**: The archived D4 harness and `fixtures-20260707` bundle referenced
by the handoff docs are not present on this machine, and Docker Desktop was not
running, so the full fixture-parity/live-smoke protocol could not yet be
executed locally.
**Decision**: Run the release-focused unit checks and manifest/package
inspection now, then treat a Podman CPU setup/readiness smoke as the cheapest
additional runtime validation slice available on this host.
**Execution**: Ran the release-focused unit suite; summarized both rebuilt
control ZIPs; validated their packaged manifests; confirmed Docker was
unavailable locally; staged the stable asset ZIP under the stable filename; ran
the packaged Podman compose-provider installer; traced two local-only issues
(`REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` pointing at a dead Git-for-Windows path,
and stale host-shell `TOWERSCOUT_*` overrides that masked the package-local
image settings); reran the Podman CPU package setup from the extracted package
root with explicit environment export; captured readiness and cleaned up the
Podman container.
**Output**: Release-focused tests are green; both rebuilt packages have the
expected file shape and manifest keys; the CPU package reached Podman
`setup_required` readiness with `asset_status=ok`, `container_engine=podman`,
`device_policy=cpu`, `selected_device=cpu`, `pytorch_flavor=cpu`, app version
`v0.1.0`, and image digest
`sha256:0c1ea5035acefca81f2c099c65cc89badcbc120c0bbbc2662303233c34f25f5b`.
**Validation**: `71` release/package unit tests passed; package summary and
manifest checks passed for both ZIPs; the Podman CPU smoke imported all assets,
reported `asset_status=ok`, and reached healthy `setup_required` readiness on
port `5020` before cleanup. Full D4 fixture parity/live smoke remains pending.
**Next**: After host restart, rerun the Docker-side setup/readiness smoke with
Docker Desktop up, then continue into the full D4 harness protocol once the
archived harness/fixture bundle is available on the validation machine.

### 2026-07-08 - Docker CPU Package Smoke Confirmed With Clean Launch Environment
**Objective**: Validate that the rebuilt CPU package reaches Docker readiness
using the pinned GHCR image and imported assets, and distinguish package issues
from host-environment overrides.
**Context**: After Docker Desktop came back up, the first CPU smoke attempt on
port `5021` failed during `docker cp` of the large ZIP-code shapefile and the
status snapshot still showed `IMAGE=towerscout:local`. The extracted package
`.env` already carried the correct pinned GHCR reference, so the remaining
hypothesis was that the host shell environment was overriding the package image
selection.
**Decision**: Repair the incomplete Docker asset import in place, then rerun
the Docker CPU smoke from a clean PowerShell process with the stale
`TOWERSCOUT_*` host overrides and CA-bundle overrides removed.
**Execution**: Confirmed the first Docker setup reached a healthy container but
left `zcta-2025-shp` corrupt and `zcta-2025-shx` missing after a closed-pipe
copy failure; reran `scripts\import-assets.ps1 -Engine docker -Port 5021
-VerifyHashes` from the extracted package to repair the asset volume; observed
that the host shell exported `TOWERSCOUT_IMAGE=towerscout:local`; rendered
`docker compose config` both with and without those shell overrides; reran the
CPU package setup on port `5022` from a clean PowerShell environment so Docker
Compose resolved the pinned GHCR image from the package `.env`.
**Output**: The repaired Docker package imported all assets successfully, and
the clean rerun reached healthy `setup_required` readiness on port `5022` with
`container_engine=docker`, `device_policy=cpu`, `selected_device=cpu`,
`pytorch_flavor=cpu`, app version `v0.1.0`, and image digest
`sha256:0c1ea5035acefca81f2c099c65cc89badcbc120c0bbbc2662303233c34f25f5b`.
**Validation**: `import-assets.ps1` completed with `asset_status=ok` and
`verify_hashes=True`; `status.ps1` after the clean rerun showed the container
running as
`ghcr.io/j-schulein/towerscout:v0.1.0-cpu@sha256:0c1ea5035acefca81f2c099c65cc89badcbc120c0bbbc2662303233c34f25f5b`
with all required and optional assets `ok`; `stop.ps1` removed the container
and network cleanly.
**Next**: Keep the Docker host-shell `TOWERSCOUT_IMAGE=towerscout:local`
override out of future package-smoke shells, then continue to the remaining D4
fixture-parity/live-smoke protocol when the archived harness and fixture bundle
are available.

### 2026-07-08 - Release Package Launch-Environment Hardening
**Objective**: Remove the host-shell override hazard from the packaged launch
path before any GitHub Release assets are published.
**Context**: Docker and Podman CPU package smokes both passed when run from a
clean process, but this workstation exported stale `TOWERSCOUT_*` values that
overrode the package `.env` and could misroute the packaged runtime to
`towerscout:local`.
**Decision**: Fix the shared release-package compose helper rather than rely on
operator discipline, and add a regression test that proves release-package
`.env` values replace stale process overrides.
**Execution**: Updated `scripts/lib/TowerScoutCompose.ps1` so
`Initialize-TowerScoutEnvFile` synchronizes managed release-package environment
variables from `.env` into the process for release-package roots, clearing blank
values instead of preserving stale process overrides; added focused regression
coverage in `tests/unit/test_task_074_bootstrap.py`.
**Output**: Package launcher scripts now prefer the package's pinned image/TLS
settings over stale host-shell values when running from a release package.
**Validation**: `tests/unit/test_task_074_bootstrap.py` plus
`tests/unit/test_import_assets_script.py` passed (`26` tests); additionally,
`tests/unit/test_release_package_script.py` plus
`tests/unit/test_task_081_runtime_hardening.py` passed (`20` tests).
**Next**: Decide release identity before publication: the existing `v0.1.0`
tag predates this launcher hardening, so do not publish final release assets
against that tag unless the source/tag/image story is intentionally updated.

### 2026-07-08 - R3 Review Accepted And v0.1.1 Path Chosen
**Objective**: Close the release-identity question after the external R3
publication-decision review and convert the recommendation into the active
execution path.
**Context**: R3 independently verified the publication-decision memo, confirmed
that the host-drift issue is systemic but latent, and highlighted that the D4
gate needed an engine-level digest cross-check in addition to the launcher
hardening. The review also confirmed that the hardening fix remained local and
therefore could not be treated as part of the already-public `v0.1.0` source
or image identity.
**Decision**: Accept the R3 recommendation. Keep `v0.1.0` as a historical tag
with published images but no final release assets, and shift the fork-side
stable publication target to a follow-on release identifier, currently
`v0.1.1`.
**Execution**: Recorded the decision in the publication memo and sprint task
tracker, implemented the shared launcher hardening in source, and added an
engine-level running-image identity check to the shared compose/status path so
future package validation is not forced to trust readiness JSON alone.
**Output**: The source tree now reflects the agreed release path: launcher
hardening plus digest-cross-check changes are in local source and validated,
but final publication remains intentionally blocked until those changes are
committed, reviewed, merged, and rebuilt into a new stable release identity.
**Validation**: `tests/unit/test_task_074_bootstrap.py`,
`tests/unit/test_import_assets_script.py`,
`tests/unit/test_release_package_script.py`, and
`tests/unit/test_task_081_runtime_hardening.py` all passed after the hardening
and digest-cross-check changes.
**Next**: Prepare the fix branch/commit, run the focused validation slice on
that branch, and then cut the follow-on release build/tag sequence (`v0.1.1`)
only after CI is green at the post-fix merge SHA.

### 2026-07-08 - Post-R4 Windows Validation Re-Run Recorded For PR #47
**Objective**: Close the remaining pre-merge evidence gap identified by the R5
re-review by recording the post-fix Windows validation slice after the R4
blocker fixes landed on PR #47.
**Context**: R5 confirmed that the code/test fixes in PR #47 were merge-ready,
but noted that the repo still lacked an explicit record that the Windows-only
behavioral slices were rerun after the R4 blocker and follow-up fixes.
**Decision**: Record the exact post-fix Windows validation slice in the task
log rather than rely on the PR description alone.
**Execution**: After applying the R4 fixes (`status.ps1` down-state handling,
status env sync, managed NVIDIA variables, `$isMatch` rename, and artifact
cleanup), reran the focused Windows validation slice from the PR branch.
**Output**: TASK-088 now carries the post-fix Windows validation evidence that
R5 asked to see before PR #47 is undrafted and merged.
**Validation**: `./.venv/Scripts/python -m pytest tests/unit/test_task_074_bootstrap.py tests/unit/test_task_081_runtime_hardening.py tests/unit/test_import_assets_script.py tests/unit/test_release_package_script.py -q -p no:cacheprovider` -> `49 passed`; `python .agent_work/scripts/validate_agent_work.py` -> passed; `git diff --check` -> passed.
**Next**: Undraft PR #47 once CI remains green, and merge it with **Squash and merge** so the previously committed artifact debris never lands in `main` history.

### 2026-07-08 - PR #47 Squash Merged And main Freeze Started
**Objective**: Capture the post-merge baseline that the follow-on stable
release must use and explicitly freeze `main` before the `v0.1.1` tag/build
sequence begins.
**Context**: PR #47 (`fix(task-088): harden release package launcher env`) was
reviewed through R5, CI was green, and the branch was squash-merged into
`main`. The merged tip on origin is now `d0ddb49`.
**Decision**: Treat `origin/main@d0ddb49` as the only valid source baseline
for the follow-on stable release path and freeze `main` until the `v0.1.1`
tag is created and pushed.
**Execution**: Verified `origin/main` advanced from `dfe9e6b` to `d0ddb49`
after the squash merge and recorded the no-more-pushes freeze rule for the
tag/build lane.
**Output**: The fork-side stable release path now has a single post-fix merge
baseline for tag, image build, package rebuild, D4 validation, and release
publication.
**Validation**: `git fetch origin --prune` showed `origin/main=d0ddb49` and no
later `main` drift.
**Next**: Execute the `v0.1.1` post-merge checklist from the frozen
`origin/main@d0ddb49` baseline.

### 2026-07-08 - PR #48 Squash Merged And v0.1.2 Path Started
**Objective**: Capture the second frozen main baseline after the Docker
image-identity fix and re-anchor the stable publication path to `v0.1.2`.
**Context**: The local `v0.1.1` package/runtime validation exposed a real
Docker image-identity helper defect, PR #48 fixed it, and that fix was
reviewed, merged, and frozen before any GitHub Release assets were published.
**Decision**: Treat `origin/main@718a564` as the only valid source baseline
for the final follow-on stable publication path, keep `v0.1.1` as a
historical tag with published images but no release assets, and move the active
stable identity to `v0.1.2`.
**Execution**: Squash-merged PR #48, froze `main` again, created and pushed tag
`v0.1.2`, dispatched CPU and CUDA image builds, captured published digests
`sha256:86c54bd723ff970f70f0883397a1f2f804db796507a461a5718aeab57258afe8`
and `sha256:bab2eda26fa6cf0483780cfcdb0a10008fb67fe058ba99a28ebdd6212fda2214`,
rebuilt CPU and CUDA control packages from a clean `v0.1.2` worktree, and
staged the shared asset ZIP under the `v0.1.2` release filename.
**Output**: `v0.1.2` now has a coherent source tag, published GHCR image pair,
rebuilt control packages, and a validated package/runtime baseline to carry
into the remaining D4 and release-publication work.
**Validation**: CPU and CUDA package ZIP sidecars verified; package summary and
manifest validation passed for both packages.
**Next**: Complete the remaining D4 fixture/live-smoke validation and then
publish the final GitHub Release assets for `v0.1.2`.

### 2026-07-08 - v0.1.2 Package Runtime Smokes Passed On Final Artifacts
**Objective**: Validate the final rebuilt `v0.1.2` package artifacts on the
real package/runtime paths before entering the heavier D4 fixture/live-smoke
sequence.
**Context**: The R6 follow-up required the release flow to stop burning tags by
adding a real pre-tag packaged Docker smoke. After `v0.1.2` was tagged and its
images/packages were rebuilt, the same package/runtime surfaces needed to be
rerun against the final artifacts, not just the local pre-tag placeholders.
**Decision**: Treat the final package runtime validation as passed only if the
rebuilt `v0.1.2` package set reaches healthy `setup_required` readiness on the
validated CPU-safe lanes and prints the engine-level running image identity
lines for the final published digests.
**Execution**: Ran the final `v0.1.2` CPU package on Docker and Podman, and ran
the final `v0.1.2` CUDA package on Docker in CPU-safe mode (`-Gpu off`). The
Podman package first required `scripts\install-podman-compose-provider.ps1
-Apply -Force` from the extracted package to restore the approved package-local
provider selection on this host.
**Output**: The final `v0.1.2` package set now has validated CPU-safe runtime
evidence on Docker CPU, Podman CPU, and Docker CUDA-package CPU-safe launch.
**Validation**:
- `v0.1.2-cpu` on Docker (`Port 5027`): `asset_status=ok`,
  `container_engine=docker`, `device_policy=cpu`, `selected_device=cpu`,
  `pytorch_flavor=cpu`, `version.app=v0.1.2`, running image digest
  `sha256:86c54bd723ff970f70f0883397a1f2f804db796507a461a5718aeab57258afe8`.
- `v0.1.2-cpu` on Podman (`Port 5028`): `asset_status=ok`,
  `container_engine=podman`, `device_policy=cpu`, `selected_device=cpu`,
  `pytorch_flavor=cpu`, `version.app=v0.1.2`, running image digest
  `sha256:86c54bd723ff970f70f0883397a1f2f804db796507a461a5718aeab57258afe8`.
- `v0.1.2-cuda121` on Docker with `-Gpu off` (`Port 5029`):
  `asset_status=ok`, `container_engine=docker`, `device_policy=cpu`,
  `selected_device=cpu`, `pytorch_flavor=cuda121`,
  `torch_cuda_build=12.1`, `version.app=v0.1.2`, running image digest
  `sha256:bab2eda26fa6cf0483780cfcdb0a10008fb67fe058ba99a28ebdd6212fda2214`.
**Next**: Move into the remaining D4 fixture/live-smoke validation with the
final `v0.1.2` package set and carry the resulting evidence into final release
publication.

### 2026-07-08 - v0.1.2 Validation Prerelease Published
**Objective**: Publish the exact final `v0.1.2` asset set under a clearly
non-final GitHub prerelease title so the reviewer can run D4 against the real
release artifacts without burning another stable release name.
**Context**: `v0.1.2` source, images, packages, and package/runtime smokes are
in place, but D4 fixture/live-smoke evidence is still pending. The agreed path
was to validate against the real `v0.1.2` assets through a prerelease rather
than introduce another validation-only tag.
**Decision**: Publish a prerelease on tag `v0.1.2` with title
`Validation v0.1.2-1`, upload the six final assets, and keep the release in
prerelease state until D4 passes.
**Execution**: Created the GitHub prerelease from tag `v0.1.2` with notes file
`2026-07-08-v0.1.2-validation-prerelease-notes.md` and uploaded:
`towerscout-v0.1.2-cpu.zip`, `towerscout-v0.1.2-cpu.zip.sha256`,
`towerscout-v0.1.2-cuda121.zip`, `towerscout-v0.1.2-cuda121.zip.sha256`,
`towerscout-v0.1.2-assets-towerscout-v1-assets-2026-05-05.zip`, and
`towerscout-v0.1.2-assets-towerscout-v1-assets-2026-05-05.zip.sha256`.
**Output**: A public validation prerelease now exists at the `v0.1.2` tag with
the exact six assets that should be used for the remaining D4 validation.
**Validation**: `gh release view v0.1.2 --repo J-Schulein/TowerScout` showed
title `Validation v0.1.2-1`, prerelease status, and all six uploaded assets.
**Next**: Hand the prerelease assets to the reviewer for D4 execution, then
promote the release in place only if the remaining D4 gate passes.

### 2026-07-09 - v0.1.2 Full Matrix Validation Passed
**Objective**: Record the completed D4/full-matrix validation evidence against
the exact assets published in the `Validation v0.1.2-1` prerelease.
**Context**: The validation prerelease existed specifically so the final
six-asset `v0.1.2` set could be validated before stable publication. The
reviewer ran the expanded four-cell matrix on a Windows validation workstation
with Docker 29.6.1, Podman 5.8.x, and an NVIDIA T1000 8GB GPU.
**Decision**: Treat the D4/full-matrix release gate as passed and keep final
publication as the remaining Task-088 action. Non-blocking product findings
are recorded for release notes and backlog follow-up rather than blocking the
stable release.
**Execution**: Reviewed the evidence copied into
`.agent_work/context/status/Handoff-Planning/v0.1.2-Validation-Evidence/`,
including `RUNLOG.md`,
`V012-FULL-MATRIX-QA-2026-07-09.md`, and
`V012-Validation-Methodology-and-Reproduction-Guide.md`.
**Output**: All four cells passed: Docker CPU, Docker CUDA, Podman CPU, and
Podman CUDA. Each cell passed package integrity, setup, readiness identity,
engine-level anti-spoof status, fixture parity, live provider smokes,
Google/Azure detection-to-export workflows, and required stopped-status
contracts. Six-way per-tile fixture parity matched the rc7.1 baseline exactly:
`0,0,13,8,0,4,6,11,2,4,5,0` for `53` total detections in every run.
**Validation**: Evidence verdict is PASS. CPU image digest
`sha256:86c54bd723ff970f70f0883397a1f2f804db796507a461a5718aeab57258afe8`
and CUDA image digest
`sha256:bab2eda26fa6cf0483780cfcdb0a10008fb67fe058ba99a28ebdd6212fda2214`
matched package pins and engine inspection. Wizard S1-S7 passed in the deep
Docker CPU cell. Provider keys were deleted from the validation secret file at
run end and were not printed in evidence.
**Next**: Promote the existing `v0.1.2` validation prerelease in place with the
final title/notes, mark it latest, and preserve the validation evidence as the
release archive.

### 2026-07-09 - v0.1.2 Stable Release Published
**Objective**: Promote the validated `v0.1.2` prerelease in place as the final
fork-side stable GitHub Release.
**Context**: The exact six prerelease assets passed the full validation matrix,
so creating a second release record or re-uploading assets would add ambiguity
without improving traceability.
**Decision**: Promote the existing `v0.1.2` release in place by retitling it,
replacing the notes with the final release notes, clearing prerelease status,
and marking it latest.
**Execution**: Ran `gh release edit v0.1.2 --repo J-Schulein/TowerScout
--title "TowerScout v0.1.2" --notes-file
.agent_work\context\status\Handoff-Planning\2026-07-08-v0.1.2-release-notes-draft.md
--prerelease=false --latest`.
**Output**: GitHub release URL:
`https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.2`.
**Validation**: `gh release view v0.1.2 --repo J-Schulein/TowerScout --json
tagName,name,isDraft,isPrerelease,url,assets,publishedAt` returned
`name=TowerScout v0.1.2`, `isDraft=false`, `isPrerelease=false`, tag
`v0.1.2`, and the six validated assets. `gh release list --repo
J-Schulein/TowerScout --limit 5` listed `TowerScout v0.1.2` as `Latest`.
**Next**: Preserve the final URL/checksums in TASK-089 and carry the remaining
owner-gated migration work there.

### 2026-07-10 - Pilot-First Closeout And Feedback Hold Adopted
**Objective**: Reconcile Task-088 with the cdcai owner's decision to keep the
official repository unchanged until user feedback is reviewed.
**Context**: The validated `v0.1.2` package is scheduled for pilot distribution
on Monday, the project may end on 2026-07-15 or receive a three-month extension,
and immediate cdcai migration would change an official repository before the
owner knows whether the pilot baseline needs fixes.
**Decision**: Freeze `v0.1.2` as the fork-side validated pilot release. Keep
`cdcai/TowerScout` unchanged during the feedback hold. Finish Task-088 by
making the pilot download, guide wording, organization-controlled feedback
channel, backup support ownership, evidence custody, and no-extension handoff
explicit. Any package fix receives a new version identity.
**Execution**: Added the canonical pilot/adoption plan and revised the current
sprint, backlog, Task-088, Task-089, HANDOFF, and agent context to use the same
feedback-gated decision.
**Output**: Release publication remains complete, but Task-088 now tracks the
real remaining pilot-readiness and continuity work instead of implying that
immediate cdcai migration is next.
**Validation**: On `docs/task-088-pilot-feedback-handoff` from
`origin/main@718a564`, `.agent_work` validation passed, `git diff --check`
passed, the runtime/test diff remained clean, and
`tests/unit/test_flask_routes.py` passed (`57 passed`).
**Next**: Select and record the feedback/support destination, confirm the backup
owner and evidence custody, then land the final documentation safely from the
`v0.1.2` main baseline.

### 2026-07-12 - Pilot Operations Packet Prepared
**Objective**: Complete the pilot work that does not depend on the pending
feedback/support-channel decision.
**Context**: The validated release and guides are ready, but Monday execution
still needed one concise operational packet that another owner can use without
reconstructing the handoff history.
**Decision**: Prepare the outbound wording, pre-send checks, feedback schema,
severity rules, daily register, and custody checklist now. Leave only the
organization-controlled destination, backup owner, coordinator, and response
window as explicit human-confirmed fields.
**Execution**: Added
`PILOT-OPERATIONS-PACKET.md` and linked it from the Handoff-Planning index. The
packet pins the fork release URL, source ref, six filenames, normal CPU/Docker
path, sensitive-evidence restrictions, and feedback-gated cdcai adoption rule.
**Output**: Monday's pilot materials can be finalized by inserting the approved
support details; no cdcai or release-asset change is required.
**Validation**: The agent-work hygiene quick check passed;
`python .agent_work/scripts/validate_agent_work.py` passed; and
`git diff --check` passed.
**Next**: On 2026-07-13, insert and verify the owner-controlled feedback
destination and backup owner, check the final outbound material, and then send
the pilot.

### 2026-07-22 - Pilot Launch And Task Closeout Confirmed
**Objective**: Reconcile Task-088 with the completed pilot launch and confirmed
project extension.
**Context**: The pilot email was sent on 2026-07-13. The project lead maintains
feedback in a fillable Word document outside the repository, and the primary
and backup support contacts are confirmed with appropriate access. The project
now has a hard 2026-10-31 end date.
**Decision**: Close Task-088. Treat the public release, repository handoff docs,
and validation evidence as durable custody. Do not duplicate feedback intake or
tracking in `.agent_work`, and do not select subsequent implementation work as
part of this closeout.
**Execution**: Updated the canonical plan, pilot record, current-task state,
backlog state, handoff guide, and agent context. Converted the pilot operations
packet from a pre-send template into a completed launch and custody record.
**Output**: All Task-088 acceptance criteria are satisfied; Task-089 remains
owner-gated and cdcai remains unchanged.
**Validation**: Agent-work quick check passed;
`python .agent_work/scripts/validate_agent_work.py` passed; `git diff --check`
passed; no runtime or test files changed; and the Flask docs/route contract
suite passed (`57 passed`).
**Next**: Merge the documentation branch through review, then begin a separate
planning iteration without presuming which backlog work will be selected.

---

## Validation Results

### Test Summary
**Test Date**: 2026-07-08 through 2026-07-09
**Test Environment**: GitHub Actions image publish runs, local Windows
tagged-worktree package assembly, package-focused validation, final `v0.1.2`
package runtime validation, and full validation workstation matrix over Docker
29.6.1, Podman 5.8.x, and NVIDIA T1000 8GB.
**Test Status**: PASS for stable package validation and fork-side stable
publication.

### Acceptance Criteria Validation
- [x] **Task tracking created**: Completed 2026-07-08
- [x] **Pre-merge cleanup dispositioned**: Completed 2026-07-08
- [x] **Task-088 entered from merged main baseline**: Completed 2026-07-08
- [x] **Pre-tag cleanup completed**: Completed 2026-07-08
- [x] **Stable package validation recorded**: Completed 2026-07-09 with
      full-matrix PASS evidence under
      `.agent_work/context/status/Handoff-Planning/v0.1.2-Validation-Evidence/`
- [x] **Release-path guidance finalized**: Completed 2026-07-08 for the
      fork-side release and package path
- [x] **Pilot-facing guidance finalized**: Pilot email sent 2026-07-13; external
      Word feedback method and primary/backup support coverage confirmed
- [x] **Residual decisions closed or delegated**: Historical `v0.1.0` /
      `v0.1.1` disposition delegated to TASK-089, and non-blocking v0.1.2
      findings recorded for release notes/backlog follow-up
- [x] **Final fork-side publication**: Completed 2026-07-09 at
      `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.2`
- [x] **Durable evidence and support custody**: Public release assets and
      repository validation/handoff records are durable; confirmed support
      contacts have appropriate access
- [x] **cdcai feedback hold**: The official cdcai repository remains unchanged
      until feedback review and explicit owner adoption approval

### Issues Identified

- Full D4/full-matrix validation is no longer blocked; the validation
  workstation completed it against the exact `Validation v0.1.2-1` assets.
- The current `v0.1.0` and `v0.1.1` tags remain historical identities with
  published images but no GitHub Release assets. The active publication line is
  `v0.1.2`.
- Product finding, non-blocking: Google-mode "Find towers" without a drawn or
  search-defined boundary sends a degenerate bounds sentinel and is rejected by
  server-side validation with a generic client error. Normal documented
  detection/export flows with an explicit AOI passed; Azure's no-boundary
  fallback also passed. Track under TASK-027 for clearer client handling and a
  small bounds-scope fix.
- Product finding, non-blocking: `/favicon.ico` returns 404 because no favicon
  is packaged.
- Product finding, non-blocking: export/status notifications use blocking
  `alert()` dialogs. Human workflows pass, but automation must dismiss them.
- Product finding, non-blocking: shared per-IP rate limiting can 429 rapid
  automated save/config sequences; user-paced interaction is unaffected.
- Local `test_config.py` runs can fail if the shell carries TLS-bundle
  environment state; unsetting `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` before
  that slice restores the expected local baseline.
- Pilot distribution, external feedback handling, and backup support coverage
  are complete. Contact details and the fillable Word document remain outside
  this public repository.
- The documentation closeout branch is based on the `v0.1.2`
  `origin/main@718a564` baseline and is prepared for normal PR review.

### Sign-off

Stable package validation is signed off by the 2026-07-09 full-matrix PASS, the
fork-side `v0.1.2` stable release is published as latest, and the pilot was sent
on 2026-07-13. Support coverage and durable custody are confirmed. Task-088 is
complete pending normal review and merge of this documentation record.

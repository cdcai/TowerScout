# TASK-082: RC4 Documentation And Package Organization

**Status**: COMPLETED - landed on `main` as `v0.1.0-rc4` in commit `32074a7`; stable docs naming, package docs, app docs links, and repo-organization triage are validated for the rc4 baseline
**Priority**: HIGH  
**Type**: B/C (Documentation / Release UX / Package Organization)  
**Estimated Effort**: 1-2 days (8-16 hours), plus optional package-smoke validation  
**Target Sprint**: Sprint 06 V1 RC1 / post-rc3 to rc4 readiness  

## Objective

Make the TowerScout user-facing documentation and release-package documentation
structure ready for the next `rc4` package without leaving stale `rc1`, `rc2`,
or repo-state-specific guidance in the path a non-technical pilot user is asked
to follow.

This task should convert the current docs from release-candidate-specific file
names and mixed audience placement into stable, package-safe docs with explicit
metadata for release applicability, last review date, audience, and support
scope. It should also separate end-user, support/release-engineering, internal,
and legacy material so the running app and release package surface only what a
pilot user can reasonably act on.

## Background

The current docs are technically close to the validated package path, but they
now carry confusing naming and audience drift:

- `README.md` still points users at `docs/v1-rc1-quick-start.md` and
  `docs/v1-rc1-package-guide.md`.
- The primary package docs have `v1-rc1` in filenames and headings even though
  the next package/image is expected to be `rc4`.
- Several user-facing examples still show concrete `v0.1.0-rc2` filenames.
- Settings Resource Links open static HTML docs, while the Markdown docs are
  the easier-to-review source. That creates ongoing parity risk.
- `scripts/package-release.ps1` copies docs by explicit filename, so any rename
  must update package assembly.
- `webapp/towerscout.py` uses an explicit public-doc allowlist, so any rename
  must update the allowlist and route tests.
- `docs/` mixes end-user docs, support/operator docs, release-engineering
  contracts, Codex-agent material, and legacy notes.
- The repo root contains a mix of current release files, package helpers,
  compliance templates, local ignored build outputs, and legacy/reference
  folders. Some look removable at first glance but still serve package,
  compliance, research, or runtime purposes.

The end-user goal is simple: a pilot user should know what to download, what to
extract, what command to run, what success looks like, what not to share, and
where to get help. They should not need to infer whether a document named
`v1-rc1` still applies to `rc4`.

## Requirements (EARS Notation)

**R-082-001**: WHEN a user or support lead opens the package documentation,
THE DOCUMENTATION SHALL use stable filenames and links that do not become stale
when the release candidate changes from `rc3` to `rc4` or later.

**R-082-002**: WHEN a documentation file describes release applicability,
THE DOCUMENTATION SHALL include a visible metadata block with at least
`Applies to`, `Last reviewed`, `Audience`, and `Runtime scope`.

**R-082-003**: WHEN example package filenames are shown, THE DOCUMENTATION
SHALL either use neutral placeholders such as `<release-version>` or the current
target release version, and SHALL NOT use stale `rc1`, `rc2`, or `rc3` examples
unless explicitly labeled as historical validation evidence.

**R-082-004**: WHEN a pilot user reads the Quick Start, THE DOCUMENTATION SHALL
make the normal flow unambiguous: download the Application Package ZIP, its
checksum, the Model & Data Package ZIP, and its checksum; extract only the
Application Package ZIP; keep the Model & Data Package ZIP beside the extracted
folder; run `setup-towerscout.cmd`.

**R-082-005**: WHEN documentation describes runtime choices, THE DOCUMENTATION
SHALL align with the current support boundary: Docker Desktop CPU is the
primary pilot path, Podman CPU is support-assigned and qualified, Docker GPU is
support-assigned after NVIDIA Docker validation, and Podman GPU is not
validated.

**R-082-006**: WHEN documentation describes provider keys, THE DOCUMENTATION
SHALL state that browser map SDK keys are client-visible and that pilot users
must use site/user-owned restricted provider keys, not unrestricted shared
TowerScout project keys.

**R-082-007**: WHEN documentation asks users to report a problem, THE
DOCUMENTATION SHALL request support-safe details and SHALL NOT ask users to send
provider keys, full `.env` files, raw logs, raw screenshots, raw browser
network traces, tile/map URLs, private AOIs, cached provider responses, or
exported datasets without an approved handling procedure.

**R-082-008**: WHEN Settings Resource Links, `/docs/`, or package-local links
open documentation, THE APPLICATION SHALL serve stable current docs and SHALL
not send users to stale `v1-rc1-*` primary docs.

**R-082-009**: WHEN Markdown user docs are updated, THE HTML docs used by
Settings Resource Links SHALL be regenerated, synchronized, or intentionally
replaced by a documented single-source route so the visible app links do not
lag behind the source Markdown.

**R-082-010**: WHEN release-package assembly runs, THE PACKAGE SHALL include
the current user-facing docs, support docs, source/license notices, and release
contracts needed for `rc4`, and SHALL exclude internal-only or legacy materials
unless they are intentionally included with a clear audience label.

**R-082-011**: WHEN `docs/` contains internal, agent, legacy, or
release-engineering material, THE REPO SHALL classify that material by audience
and SHALL move, rename, or label it so pilot users do not confuse it for the
normal package workflow.

**R-082-012**: WHEN doc files are renamed or moved, THE IMPLEMENTATION SHALL
update `README.md`, Settings Resource Links, Flask public-doc allowlists,
package assembly, tests, and any local docs index in the same change.

**R-082-013**: WHEN repo-root cleanup is considered, THE TASK SHALL distinguish
tracked release/compliance/source files from ignored local build outputs and
SHALL NOT delete package helpers, compliance templates, source notices,
research assets, served site assets, or legacy operator references without an
explicit owner-approved decision.

**R-082-014**: WHEN support or release-engineering docs mention current
validation, THE DOCUMENTATION SHALL distinguish current support claims from
historical `rc2`/`rc3` validation evidence.

**R-082-015**: WHEN docs include command examples, THE DOCUMENTATION SHALL use
current commands and paths: `setup-towerscout.cmd`, `start.bat`,
`scripts\status.cmd`, `scripts\logs.cmd`, `scripts\stop.cmd`, and
`scripts\import-assets.cmd` with explicit `-Engine` guidance where needed.

**R-082-016**: WHEN this task completes, THE PROJECT SHALL have validation
evidence that docs routes, package inclusion, command/path scans, and
`.agent_work` structure are current.

## Acceptance Criteria

- [x] A complete docs inventory exists in this task or a task-local support
      note, classifying every tracked `docs/` file as end-user, support,
      release-engineering, internal/agent, legacy, generated, or archive.
- [x] Stable primary filenames are selected and implemented for the user-facing
      docs, such as `quick-start.md`, `package-guide.md`, `user-guide.md`, and
      `project-overview.md`.
- [x] `v1-rc1-*` filenames are no longer the primary package docs. If retained,
      they are compatibility stubs or redirects only and clearly point to the
      stable current docs.
- [x] The primary user-facing docs include release metadata blocks with
      `Applies to`, `Last reviewed`, `Audience`, and `Runtime scope`.
- [x] Stale `v0.1.0-rc2` and `v0.1.0-rc3` examples are replaced with neutral
      placeholders or explicitly labeled historical evidence.
- [x] The Quick Start remains plain-language and tells users exactly what to
      download, what to extract, where files should be placed, what command to
      run, what success looks like, and when to stop and contact support.
- [x] Runtime support language matches the current `TASK-081` boundary:
      Docker CPU primary, Podman CPU support-assigned and qualified, Docker GPU
      support-assigned, Podman GPU not validated.
- [x] Provider-key language remains clear that browser SDK keys are visible to
      the local browser app and must be restricted.
- [x] User-facing troubleshooting requests support-safe evidence only.
- [x] Settings Resource Links and `/docs/` use stable current docs.
- [x] `webapp/towerscout.py` public docs allowlist is updated for any renamed
      docs and route tests cover allowed docs plus traversal rejection.
- [x] `scripts/package-release.ps1` includes the renamed/current docs and does
      not package internal-only docs accidentally.
- [x] HTML docs are synchronized with Markdown, generated from Markdown, or
      replaced by a single-source serving approach with tests.
- [x] `README.md` points users to the stable docs and no longer presents the
      package path as tied to `V1 RC1` filenames.
- [x] Support/release-engineering docs are separated or labeled so end users
      are not expected to read implementation contracts to install TowerScout.
- [x] Root-folder organization recommendations are recorded, but destructive or
      broad file moves are limited to owner-approved, low-risk changes.
- [x] Focused tests or checks pass for docs routes, package-release file
      inclusion, docs command/path scanning, `.agent_work` validation, and
      whitespace.
- [x] Any remaining docs warnings, stale references, or intentionally retained
      legacy paths are recorded before building the next package.

## Dependencies

- `TASK-071`: current package-local user docs and Resource Links baseline.
- `TASK-073`: UAT execution plan and support-safe evidence boundaries.
- `TASK-074`: `setup-towerscout.cmd`, bootstrap/preflight, and first-run package
  flow.
- `TASK-075`: GPU support boundary and readiness diagnostics.
- `TASK-080`: first-cohort Word guide, simplified setup process, and `rc3`
  release validation history.
- `TASK-081`: `rc3` runtime hardening, `latest-cpu` defaults, Podman CPU
  validation, and Podman GPU caveat.
- `TASK-076`: provider-key policy if owner/legal asks for stronger wording.
- Current package integration points:
  - `README.md`
  - `docs/`
  - `scripts/package-release.ps1`
  - `webapp/towerscout.py`
  - `webapp/templates/towerscout.html`
  - `tests/unit/test_flask_routes.py`
  - `tests/unit/test_release_package_script.py`

## Proposed Documentation Shape

The implementation should confirm or adjust this shape before editing:

```text
docs/
  quick-start.md                  # primary pilot setup path
  quick-start.html                # Settings/app-visible HTML, if retained
  package-guide.md                # fuller support/tester package guide
  user-guide.md                   # normal app workflow after setup
  user-guide.html                 # Settings/app-visible HTML, if retained
  project-overview.md             # short package-local overview
  project-overview.html           # Settings/app-visible HTML, if retained
  towerscout-docs.css             # shared docs styling
  support/
    oci-quick-start.md
    oci-runtime-contract.md
  release/
    release-asset-bundle-contract.md
  legacy/
    LEGACY-LICENSE-NOTICE.md
  internal/
    codex-skills/
```

This proposed shape is not approval to move every file. It is the starting
taxonomy to validate during Phase 0 and Phase 1.

## Docs Inventory And Repository Triage

### Docs Inventory

| Path | Classification | Package/App Handling | Notes |
| --- | --- | --- | --- |
| `docs/quick-start.md` | End-user primary | Packaged; stable source doc | Normal first-run setup path. |
| `docs/quick-start.html` | End-user primary / app-visible | Packaged; served by `/docs/` | Static browser page kept in sync with `quick-start.md` for app Resource Links. |
| `docs/package-guide.md` | Support/tester guide | Packaged; served by explicit `/docs/package-guide.md` link | Fuller support and validation details; not the first screen for normal users. |
| `docs/user-guide.md` | End-user primary | Packaged; stable source doc | Normal app workflow after setup. |
| `docs/user-guide.html` | End-user primary / app-visible | Packaged; served by Resource Links | Static browser page kept in sync with `user-guide.md`. |
| `docs/project-overview.md` | End-user/support overview | Packaged; stable source doc | Short package-local overview and release boundary summary. |
| `docs/project-overview.html` | End-user/support overview / app-visible | Packaged; served by Resource Links | Static browser page kept in sync with `project-overview.md`. |
| `docs/towerscout-docs.css` | App-visible docs styling | Packaged; served by `/docs/` | Shared styling for app-visible HTML docs and compatibility stubs. |
| `docs/v1-rc1-quick-start.md` | Compatibility stub | Packaged; served by `/docs/` | Retained only to point older links to `docs/quick-start.md`. |
| `docs/v1-rc1-quick-start.html` | Compatibility stub | Packaged; served by `/docs/` | Redirect-style page pointing to `/docs/quick-start.html`. |
| `docs/v1-rc1-package-guide.md` | Compatibility stub | Packaged; served by `/docs/` | Retained only to point older links to `docs/package-guide.md`. |
| `docs/towerscout-user-guide.md` | Compatibility stub | Packaged; served by `/docs/` | Retained only to point older links to `docs/user-guide.md`. |
| `docs/towerscout-user-guide.html` | Compatibility stub | Packaged; served by `/docs/` | Redirect-style page pointing to `/docs/user-guide.html`. |
| `docs/support/oci-quick-start.md` | Support/operator detail | Packaged; not app-served | Engine-level support detail. |
| `docs/support/oci-runtime-contract.md` | Support/runtime contract | Packaged; not app-served | Runtime persistence/readiness contract. |
| `docs/release/release-asset-bundle-contract.md` | Release-engineering contract | Packaged; not app-served | Asset bundle and release matching contract. |
| `docs/legacy/LEGACY-LICENSE-NOTICE.md` | Legacy/compliance reference | Repo-only unless separately packaged | Kept for historical notice context. |
| `docs/internal/codex-skills/*` | Internal/agent material | Repo-only; not packaged | Moved out of the package-facing docs root. |

### Root-Folder Triage

| Root Item | Classification | Task-082 Handling |
| --- | --- | --- |
| `README.md` | Public/repo entry point | Update links and release-package wording. |
| `docs/` | User/support/release docs | Reorganized by audience with stable user-facing filenames. |
| `scripts/`, `setup-towerscout.cmd`, `bootstrap.cmd`, `start.bat` | Release package helpers | Keep in root/package; update docs references only. |
| `compose.yaml`, `compose.gpu.yaml`, `compose.build.yaml`, `Dockerfile`, `.dockerignore`, `.env.example` | Runtime/package source | Keep; no cleanup in Task-082. |
| `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `MODEL_LICENSES.md`, `DATA_LICENSES.md`, `PROVIDER_TERMS.md`, `SOURCE.txt`, `SBOM.txt`, `release-manifest.v1.json` | Compliance/release control files | Keep in root; they may look duplicative but are release-critical templates/notices. |
| `webapp/` | Application source | Keep; update docs allowlist/routes only. |
| `tests/`, `pytest.ini`, `requirements-dev.txt`, `package.json`, `package-lock.json` | Developer/test infrastructure | Keep; update focused tests only. |
| `.github/`, `.agents/`, `.agent_work/` | Workflow/agent/review context | Keep; update Task-082 evidence and current task state. |
| `Model/`, `SyntheticData/` | Research/training/reference assets | No move/delete without owner-approved follow-up. |
| `TowerScoutSite/`, `hosting/` | Legacy/site/operator references | No move/delete without owner-approved follow-up. |
| `dist/`, `.venv/`, `node_modules/`, `.pytest_cache/`, `.coverage`, `.env`, `logs/` | Local ignored outputs/config | Leave local workspace cleanup out of tracked Task-082 changes. |

## Implementation Plan

1. **Phase 0 - Inventory And Source-Of-Truth Check**
   - List all tracked docs and classify them by audience.
   - Search `README.md`, `docs/`, `scripts/package-release.ps1`,
     `webapp/towerscout.py`, templates, and route/package tests for
     `v1-rc1`, `V1 RC1`, `rc1`, `rc2`, `rc3`, `rc4`, and old doc paths.
   - Identify which docs are served by the running app, copied into the
     release package, or useful only to maintainers.
   - Decide whether HTML should remain hand-authored, generated from Markdown,
     or replaced by serving Markdown/converted HTML dynamically.

2. **Phase 1 - Naming And Audience Decision**
   - Select stable doc filenames and folders.
   - Decide whether to keep compatibility stubs for old `v1-rc1-*` links.
   - Define a standard metadata block for docs.
   - Confirm which support/release docs belong in the user package and which
     should remain repo-only.

3. **Phase 2 - User-Facing Content Rewrite**
   - Update Quick Start for the `rc4` package path without hard-coding stale
     examples.
   - Update Package Guide for support/tester detail without forcing end users
     to read engineering contracts.
   - Update User Guide and Project Overview with stable links and current
     runtime/provider/license language.
   - Preserve the plain-language setup model from `TASK-080`.

4. **Phase 3 - App And Package Wiring**
   - Update Settings Resource Links.
   - Update `/docs/` default route and public-doc allowlist.
   - Update package-release file list.
   - Update Docker/runtime package inclusion only if needed.
   - Update route, package, and docs tests for renamed files and link behavior.

5. **Phase 4 - Repo Organization Triage**
   - Record current root-folder classification: release-critical, compliance,
     developer/test, local ignored output, research/training, served site, and
     legacy/operator reference.
   - Make only low-risk approved moves or labels in this task.
   - Defer larger moves such as `Model/`, `SyntheticData/`, `TowerScoutSite/`,
     or `hosting/` unless owner explicitly approves them after the inventory.

6. **Phase 5 - Validation**
   - Run docs command/path checks.
   - Run focused Flask docs-route tests and release-package script tests.
   - Run `.agent_work` validation.
   - Run whitespace checks.
   - If package generation is in scope, inspect a local validation package to
     confirm expected docs are included and stale docs are absent.

7. **Phase 6 - Handoff**
   - Summarize remaining docs caveats before `rc4` image/package creation.
   - Record reviewer focus areas: stable naming, user clarity, package
     inclusion, HTML/Markdown parity, and support-safe evidence language.

## Validation Strategy

- `python .agent_work/scripts/validate_agent_work.py`
- `python .agents/skills/towerscout-end-user-docs-check/scripts/check_doc_commands.py . docs README.md`
- Focused route tests for `/docs/`, public docs allowlist, Settings Resource
  Links, and traversal rejection.
- Focused release-package tests for included docs and removed/compatibility
  docs.
- `git diff --check`
- Optional local validation package inspection if owner approves package
  generation before `rc4` release work begins.

## Non-Goals

- Do not build or publish the `rc4` image/package in this task unless the owner
  explicitly expands scope.
- Do not change runtime launch behavior except for docs routing/linking needed
  by the documentation rename.
- Do not change provider-key architecture or proxy behavior; this task only
  documents the current support boundary.
- Do not claim Podman GPU support.
- Do not remove or relocate `Model/`, `SyntheticData/`, `TowerScoutSite/`, or
  `hosting/` without a specific owner-approved decision.
- Do not delete ignored local outputs such as `dist/`, `.venv/`,
  `node_modules/`, `.pytest_cache/`, `.coverage`, or `logs/` as part of the
  tracked task unless the owner requests local workspace cleanup.
- Do not weaken source/license/model/data/provider notice availability.

## Risks And Open Questions

- Stable doc names are better for future releases, but old links may exist in
  package zips, screenshots, or handoff material. Compatibility stubs may be
  safer than immediate deletion.
- Hand-authored HTML docs are easy to drift from Markdown. A generation step or
  single-source route may be worth adding before future release candidates.
- Over-separating docs could hide support information that first-line support
  needs inside the package. The taxonomy needs to preserve support access while
  keeping the normal user path short.
- Moving internal docs out of `docs/` could affect existing references or
  developer expectations.
- Root-level `SOURCE.txt`, `SBOM.txt`, and `release-manifest.v1.json` may look
  redundant but are intentional compliance templates; they should remain unless
  release-compliance review says otherwise.
- `hosting/` appears superseded by Compose for the pilot path, but older
  analysis classified it as a legacy/operator reference. Treat movement or
  deletion as a separate repo-organization decision unless the owner approves a
  narrow change.

## Evidence Handling

Do not add raw logs, screenshots, browser-network captures, provider responses,
private AOIs, `.env` files, API keys, release-owner credentials, or
unredacted support artifacts to this task or project-wide context files. If
evidence is needed, record sanitized command summaries and non-secret file/path
checks only.

---

## Implementation Log

### 2026-06-12 - Task Documentation Created
**Objective**: Create an active Sprint 06 task for RC4 documentation and package organization cleanup before the next image/package build.  
**Context**: Review of the current user-facing docs found that the package flow is mostly current, but stable naming, stale `rc2` examples, `v1-rc1` filenames, HTML/Markdown drift risk, mixed-audience `docs/` organization, and root-folder cleanup questions could confuse pilot users before `rc4`.  
**Decision**: Track this as `TASK-082` rather than expanding `TASK-081`. Runtime hardening remains in PR #31, while this task covers release-doc clarity, package docs naming, app docs routes, and repo organization triage.  
**Execution**: Created this task file with requirements, acceptance criteria, dependencies, proposed doc taxonomy, implementation phases, validation plan, non-goals, risks, and evidence handling.  
**Output**: `TASK-082` is ready for owner review and implementation approval.  
**Validation**: `python .agent_work/scripts/validate_agent_work.py` passed; `python .agents/skills/towerscout-agent-work-hygiene/scripts/check_agent_work_quick.py .` passed.  
**Next**: Wait for approval before editing docs/routes/package assembly.

### 2026-06-12 - Stable Docs Naming And Package Wiring
**Objective**: Implement the approved Task-082 docs cleanup without adding changes to PR #31.  
**Context**: PR #31 is under review for Task-081 runtime hardening. Task-082 work needs the latest Task-081 support boundary, but should remain separate from the PR #31 branch.  
**Decision**: Create a separate stacked branch, `docs/task-082-rc4-docs-package-organization`, from the Task-081 branch. Rebase or retarget after PR #31 lands. Keep compatibility stubs for older `v1-rc1-*` and `towerscout-user-guide.*` links to avoid breaking existing handoff material. Do not delete broad repo-root folders or local ignored outputs.  
**Execution**: Renamed primary user docs to stable filenames, moved support/release/internal docs under audience-specific folders, added metadata blocks, replaced stale rc2/rc3 examples with placeholders, updated Settings Resource Links, updated `/docs/` route behavior and allowlist, updated release-package doc inclusion, added focused tests for stable docs and compatibility stubs, and recorded docs/root inventory in this task.  
**Output**: Primary package docs now use `quick-start`, `package-guide`, `user-guide`, and `project-overview` names. Old paths are compatibility stubs. Internal Codex docs are no longer package-facing. The app opens stable Resource Links, and package assembly includes stable docs plus support/release contracts while excluding `docs/internal`.  
**Validation**: Focused docs route/package/UAT tests passed, docs command scan passed without warnings, `.agent_work` validators passed, `python -m py_compile webapp\towerscout.py` passed, and `git diff --check` passed.  
**Next**: Rebase/retarget Task-082 onto `main` after PR #31 lands and decide whether to open a draft PR or continue with any reviewer-requested doc refinements.

### 2026-06-12 - Rebased After PR #31 Merge
**Objective**: Unstack Task-082 after PR #31 landed and the Task-081 branch was deleted.
**Context**: PR #31 was squash-merged to `main` as `da3aa79`; the local Task-082 branch still sat on the pre-merge Task-081 commit chain.
**Decision**: Preserve the focused Task-082 commit, rebase only that commit onto updated `origin/main`, and leave the imported reviewer-feedback context folder untracked.
**Execution**: Fetched `origin/main`, committed the Task-082 docs/package changes, and rebased the single Task-082 commit onto `origin/main` with autostash.
**Output**: `docs/task-082-rc4-docs-package-organization` is now based directly on `origin/main` with one Task-082 commit.
**Validation**: Re-ran the focused docs route/package/UAT tests, docs command scan, `.agent_work` validators, `py_compile`, and `git diff --check`; all passed.
**Next**: Push the standalone Task-082 branch and open a focused docs/package organization PR when ready.

### 2026-06-12 - PR #32 Reviewer Fixes
**Objective**: Address PR #32 review feedback before merge.
**Context**: Reviewer found visible README mojibake in three user-facing strings and suggested Markdown compatibility stubs should use clickable links.
**Decision**: Treat the README encoding regression as merge-blocking, apply the compatibility-stub link polish in the same narrow docs update, and keep the PR as a standalone Task-082 branch.
**Execution**: Restored the intended README characters for the manual-tower badge, tile-estimation approximation symbol, and Legionnaires' disease citation apostrophe. Updated the Markdown compatibility stubs to link directly to the stable docs. Corrected Task-082 tracker status now that PR #31 has landed and PR #32 is standalone.
**Output**: README user-facing text is restored, compatibility stubs are easier to click from rendered Markdown, and Task-082 state matches the current branch/PR reality.
**Validation**: Mojibake scan returned no matches in `README.md`, `docs/`, or the Task-082 task file. Focused docs route/package/UAT tests passed with 49 tests, docs command scan passed, `.agent_work` validators passed, `py_compile` passed, and whitespace check was rerun after trailing-space cleanup.
**Next**: Commit and push the focused reviewer-fix update to PR #32, then request re-review.

### 2026-06-15 - Landed In RC4 Baseline
**Objective**: Record Task-082 landing status after the rc4 image/package baseline was rebuilt.
**Context**: Local `main`, `origin/main`, and tag `v0.1.0-rc4` all point to `32074a7 docs(task-082): stabilize RC package documentation`.
**Decision**: Mark Task-082 as completed/landed while leaving this task file in `tasks/active/` until Sprint 06 closeout.
**Execution**: Verified git history and updated Task-082 status language in this task file and `current-tasks.md`.
**Output**: Task-082 status now reflects the landed rc4 baseline instead of the prior PR #32 review state.
**Validation**: Planning/status validation rerun under the Task-083 checkpoint.
**Next**: Continue Task-083 from the rc4 `main` baseline.

---

## Validation Results

### Implementation Validation
**Test Date**: 2026-06-12  
**Test Environment**: Local TowerScout workspace on Windows  
**Test Status**: PASS for focused Task-082 validation  

### Acceptance Criteria Validation

- [x] **Task tracker synchronization**: `current-tasks.md` includes `TASK-082`
      and points to this active task file.
- [x] **Agent-work structure validation**: `python .agent_work/scripts/validate_agent_work.py`
      passes after task creation.
- [x] **Stable docs naming**: Primary docs use `quick-start`, `package-guide`,
      `user-guide`, and `project-overview` names; old paths are compatibility
      stubs.
- [x] **App docs links**: Settings Resource Links and `/docs/` default route
      use stable current docs.
- [x] **Package inclusion**: Release package tests verify stable docs,
      compatibility stubs, support/release docs, and exclusion of
      `docs/internal`.

### Test Results

- [x] `.venv\Scripts\python.exe -m pytest tests\unit\test_flask_routes.py tests\unit\test_release_package_script.py tests\unit\test_task_080_uat_followups.py -q -p no:cacheprovider` - PASS, 49 tests.
- [x] `python .agents\skills\towerscout-end-user-docs-check\scripts\check_doc_commands.py . docs README.md` - PASS, no warnings after numeric-loopback support wording was rephrased.
- [x] `python .agent_work\scripts\validate_agent_work.py` - PASS.
- [x] `python .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .` - PASS.
- [x] `python -m py_compile webapp\towerscout.py` - PASS.
- [x] `git diff --check` - PASS.

### Issues Identified

- Static HTML remains manually maintained. It was synchronized in this task and
  covered by focused route tests, but no Markdown-to-HTML generator was added.
- Historical `v1-rc1-*` and `towerscout-user-guide.*` files remain as explicit
  compatibility stubs.
- The Word UAT guide filename still contains `V1_RC1` because it is a separate
  Task-080 artifact and not part of package-facing docs routing.
- The Task-081 runtime-hardening tests still contain `v0.1.0-rc3` as historical
  runtime test data; it is not user-facing package documentation.

### Remediation Actions

- Reworded the support doc numeric-loopback guidance to prefer `localhost`
  without triggering the docs scanner warning.
- Tightened `/docs/<path>` handling so trailing-slash and nested path variants
  are rejected even when the basename is public.

### Sign-off

Task implementation landed in `v0.1.0-rc4` (`32074a7`) and remains in
`tasks/active/` until Sprint 06 closeout.

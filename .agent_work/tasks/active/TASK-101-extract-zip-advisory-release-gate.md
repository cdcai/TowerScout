# TASK-101: extract-zip Advisory Assessment And Release-Gate Disposition

**Status**: IN_PROGRESS - PR #72 squash-merged as `0cc189c`, alert `#76` closed
as fixed without dismissal, and exact-main CI passed August 19, 2026; PR #67
semantic integration and exact-head validation remain open
**Priority**: HIGH
**Type**: C (Security Remediation / CI And Release Gate)
**Estimated Effort**: 1-2 days plus CI rerun timing
**Target Sprint**: Sprint 09 immediate gate before Task-087 resumes
**Owner**: TowerScout release owner / active agent support
**Created**: August 19, 2026
**Selected**: August 19, 2026

## Objective

Remove or otherwise safely disposition the high-severity development-only
`extract-zip==2.0.1` path, restore TowerScout's deliberately blocking frontend
dependency-security gate, and provide the compatibility evidence required for
Task-087 implementation, PR #67 merge, and candidate-package work to resume.

## Triggering Baseline And Boundary

- Dependabot alert `#76` maps to `GHSA-jmr9-qjv8-65gv` /
  `CVE-2026-56876`. GitHub currently lists `extract-zip<=2.0.1` as affected
  and lists no patched `extract-zip` release.
- The triggering lock graph was
  `puppeteer@24.19.0 -> @puppeteer/browsers@2.10.8 -> extract-zip@2.0.1`.
- The dependency is development-only. It is not copied into the TowerScout
  Python runtime image or normal-user Windows release ZIP.
- The main `frontend-test` job installs the dependency with
  `PUPPETEER_SKIP_DOWNLOAD=true`, so that failing job does not run browser ZIP
  extraction. Its blocking `npm audit --audit-level=high` correctly stops the
  job before bundle and frontend contract tests.
- The Task-087 Puppeteer jobs could exercise the browser-install path while
  also installing a separately pinned Playwright Chromium. Task-101 replaces
  their historical `PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=false` setting with the
  supported skip-download configuration so browser acquisition is explicit
  and non-redundant.
- PR #67 review may continue. New Task-087 implementation, package integration,
  merge, and candidate publication wait for this task. No evidence indicates
  exploitation, and no end-user runtime vulnerability is claimed.

## Requirements (EARS Notation)

- WHEN a blocking high-severity npm advisory affects a supported development or
  CI path, THE PROJECT SHALL remove the vulnerable path or document an approved
  time-bounded residual-risk disposition before merge or publication.
- WHEN remediation crosses a Node or Puppeteer major-version boundary, THE
  PROJECT SHALL update every maintained build/test baseline consistently and
  run proportionate frontend, browser, container-build, and lock-graph
  regression validation.
- WHEN TowerScout supplies a browser executable separately, THE CI WORKFLOW
  SHALL avoid an unnecessary second Puppeteer-managed browser download.
- WHEN Task-101 passes its acceptance gates, THE PROJECT SHALL record the
  evidence and explicitly resume Task-087 without rewriting Task-099's dated
  completion history.

## Acceptance Criteria

- [x] The advisory, exact dependency graph, fixed-version availability,
  supported-path reachability, and end-user runtime boundary are documented.
- [x] The maintained baseline is Node 22.12+ across CI, the frontend Docker
  build stage, and `package.json`, and is compatible with the selected exact
  Puppeteer 25.x release.
- [x] The exact Puppeteer/lockfile update removes vulnerable `extract-zip` from
  the installed dependency graph; no broad override or forced downgrade masks
  the advisory.
- [x] Task-087 browser workflows use one intentional browser-install source and
  do not execute a redundant Puppeteer download path.
- [x] A clean lockfile install and blocking `npm audit --audit-level=high` pass.
- [x] Frontend bundle reproducibility, setup-wizard contracts, and provider-
  state regression tests pass.
- [x] The existing CommonJS Puppeteer consumers still load successfully after
  the major-version update.
- [x] Task-087 production-controller, simulated-helper browser, and Windows
  host-helper jobs pass after the dependency change in run `32300398377` at
  PR #72 implementation head `a87ab53`.
- [x] The Docker frontend stage builds successfully with the selected Node
  baseline and still produces the expected committed bundle.
- [x] GitHub alert `#76` closed as fixed through default-branch dependency
  reconciliation after squash commit `0cc189c`, with no dismissal or
  residual-high exception.
- [ ] Task-087's tracker and task file are changed from paused to resumed only
  after the accepted change is semantically integrated into PR #67 and that
  branch's required exact-head matrix passes.

## Dependencies

- Completed Tasks 098 and 099 and their preserved dated security baselines
- Dependabot alert `#76` and the current `package-lock.json` dependency graph
- A supported Puppeteer 25.x release using `@puppeteer/browsers` 3.x, whose
  upstream implementation no longer depends on vulnerable `extract-zip`
- A Node 22.12+ maintained baseline across CI and the Docker build stage
- PR #67 and Task-087 browser-contract workflows for regression validation

## Implementation Plan

1. Reproduce and record the exact npm audit and lock-graph result without
   mutating dependencies.
2. Trial an exact supported Puppeteer 25.x release with Node 22.12+, then
   update the maintained Node build baseline, exact Puppeteer pin, and lockfile
   together without `npm audit fix --force`.
3. Make Task-087 browser acquisition explicit by skipping Puppeteer's
   redundant download and retaining the one pinned browser source used by the
   tests.
4. Run the clean-install, audit, graph, bundle, frontend contract, browser,
   Windows helper, and Docker build validation matrix.
5. Land the remediation as a focused Task-101 change from current `main`,
   pass its exact-head checks, merge it, and reconcile the GitHub alert without
   dismissal. Then bring the accepted change into PR #67, pass that branch's
   required exact-head matrix, and only then resume Task-087.

---

## Implementation Log

### 2026-08-20 - PR #72 Merge And Default-Branch Reconciliation

**Objective**: Record the stable default-branch security result and narrow the
remaining Task-101 gate without prematurely resuming Task-087.

**Context**: Final PR #72 head `820b649` passed CI/CD run `32308971393` and
Task-087 run `32308971392`. GitHub squash-merged the PR as `0cc189c` at
`2026-08-19T22:45:32Z`.

**Decision**: Accept the PR #72 and default-branch gates as complete. Keep
Task-101 active and Task-087 paused until current `main` is semantically
integrated into Draft PR #67, the branch preserves ADR-019 and its recorded
evidence, and its required exact-head matrix passes.

**Execution**: Confirmed exact-main CI/CD run `32310281115` and Task-087 run
`32310281051` passed at `0cc189c`. Dependabot alert `#76` changed to `fixed` at
`2026-08-19T22:45:36Z`; all dismissal fields are null.

**Validation**: PASS for PR #72 merge and default-branch reconciliation. The
final PR and post-merge workflows cover the blocking frontend audit, Docker
frontend stage, Python matrix, security job, full main image build, production
controller, simulated helper, and Windows host-helper contracts.

**Next**: Merge current `main` normally into PR #67, resolve shared governance
files semantically, and require the reconciled branch's exact-head matrix before
closing Task-101 or resuming Task-087.

### 2026-08-19 - Selected As Immediate Security Gate

**Objective**: Activate the newly disclosed dependency follow-up before more
Task-087 implementation or release-package work proceeds.

**Context**: PR #67's `frontend-test` job failed after dependency installation
because the intentionally blocking npm audit found high-severity alert `#76`.
The finding opened after Task-099's August 11 closeout and therefore requires a
unique follow-up rather than rewriting that completed task.

**Decision**: Select Task-101 as the immediate Sprint 09 implementation lane.
Pause new Task-087 implementation and candidate-package integration while
keeping PR #67 open for reviewer input. Prefer a focused, validated
Node/Puppeteer upgrade that removes the vulnerable dependency path; do not use
`npm audit fix --force`, weaken the blocking threshold, or dismiss the alert.

**Execution**: Created this active Type C task record and reconciled Task-087
plus the current roadmap and handoff sources to the paused dependency-gate
state. No dependency, workflow, runtime, package, or release state changed by
this documentation-only transition.

**Output**: Task-101 is the sole immediate implementation gate. Task-087's
accepted evidence and Draft PR remain preserved and reviewable, but new
implementation/package work waits for Task-101 acceptance.

**Validation**: PASS for the lifecycle transition on August 19, 2026. The
TowerScout quick workspace checker and canonical `.agent_work` validator
passed, and `git diff --check` found no whitespace errors. Dependency
remediation validation remains open.

**Next**: Implement the focused Node/Puppeteer remediation, execute the full
compatibility matrix, and resume Task-087 only after the blocking gate passes.

---

### 2026-08-19 - Focused Remediation And Local Validation

**Objective**: Remove the vulnerable transitive path without an override,
forced downgrade, audit weakening, or alert dismissal, then validate the
Puppeteer major and Node baseline change before publishing it for exact-head
CI.

**Decision**: Adopt ADR-020: Node `>=22.12.0`, exact
`puppeteer@25.8.0`, locked `puppeteer-core@25.8.0`, and locked
`@puppeteer/browsers@3.2.1`. Use maintained Node 22 aliases in CI and the
Docker frontend stage. Retain exact `playwright@1.62.0` Chromium as the single
Task-087 browser source while setting `PUPPETEER_SKIP_DOWNLOAD=true` for both
lockfile installs.

**Execution**: Updated `package.json`, `package-lock.json`, the main frontend
CI job, both Task-087 Puppeteer jobs, the Docker frontend stage, and focused
dependency/CI regression contracts. The lock graph removes `extract-zip`,
`basic-ftp`, `ip-address`, and `js-yaml`; its remaining `ws` dependency advances
to `8.21.3`. Added an explicit CommonJS `launch` assertion and global lockfile
checks that reject nested `extract-zip` paths or dependency edges.

**Local evidence** (workspace based on branch head `4499456`; exact pushed
head and GitHub run identifiers remain pending):

- Host Node `22.16.0` / npm `10.9.2`; Docker frontend resolved Node `22.23.2`
  / npm `10.9.8`.
- A clean isolated `npm ci --no-audit --no-fund` with Puppeteer download
  skipped installed 27 packages. Blocking `npm audit --audit-level=high`
  reported zero vulnerabilities.
- `npm ls` resolved `puppeteer@25.8.0`, `puppeteer-core@25.8.0`, and
  `@puppeteer/browsers@3.2.1`; `extract-zip` had no installed path.
- CommonJS loading returned Puppeteer `25.8.0` with `launch` as a function.
  All five maintained CommonJS consumer files passed `node --check`.
- The focused dependency/CI suite passed `11` tests. The broader unit suite,
  excluding only the workstation-blocked Task-087 host-helper file, passed
  `329` tests with `74` environment/asset skips. Setup Wizard,
  ProviderStateManager, global-contract, and debug-logging JavaScript contracts
  passed.
- The frontend stage and complete runtime image built successfully on Docker
  Desktop. The committed, frontend-stage, and full-image bundles shared
  normalized SHA-256
  `c7502f30539041011ad8571f3d7458b6086636cb0de26d5d6323c1d312185589`
  after replacing the bytes from `Build Date: ` through, but not including,
  the first CR/LF with `Build Date: normalized`, preserving every other byte.

**Boundaries**: The legacy `npm run test:stage-0` Bash wrapper was evaluated
inside Node 22 and remains red because its mutation-count assertions are stale
against `webapp/js/towerscout.js`; both the wrapper and bundle are identical to
`main`, and this check is not a Task-101 or maintained CI gate. The broader
local Task-087 host-helper test remains non-authoritative on this workstation:
17 tests passed and 19 were blocked by the existing Windows security scanner's
`ScriptContainedMaliciousContent` response. No security bypass was attempted.
The three exact Task-087 GitHub jobs remain required evidence.

**Result**: PASS for implementation and local Task-101 validation. Alert `#76`
must remain open and undismissed until the accepted graph reaches the default
branch. Task-087 remains paused until exact-head CI, alert reconciliation, and
semantic integration with PR #67.

**Next**: Commit and push the focused change to Draft PR #72, require the main
CI and all three Task-087 jobs at its exact head, then obtain merge approval.
After default-branch alert reconciliation, merge Task-101 semantically into PR
#67 and rerun that branch's required matrix before resuming Task-087.

---

### 2026-08-19 - Quality Review Remediation And Evidence Reconciliation

**Objective**: Resolve the independent PR #72 quality-review findings without
weakening the focused security remediation or prematurely resuming Task-087.

**Context**: The review found no dependency, CommonJS, browser, or runtime
defect. It identified stale committed implementation-head evidence, an
inconsistent sequence that could resume Task-087 before PR #67 validation, and
the absence of an automated pull-request build for the changed Docker frontend
stage.

**Decision**: Preserve CI/CD run `32300398378` and Task-087 compatibility run
`32300398377` as the green evidence for implementation head `a87ab53`. Use one
ordered downstream gate everywhere: final PR #72 checks, PR #72 merge, alert
`#76` closure without dismissal, semantic integration into PR #67, green PR
#67 exact-head checks, and only then Task-087 resumption. Add a dedicated,
blocking `Docker frontend stage` job while leaving the full runtime-image build
as the existing main-branch advisory check.

**Execution**: Reconciled the current task, roadmap, requirement, design,
decision, handoff, and agent-guidance sources. Added the CI job plus a semantic
YAML regression contract that rejects a conditional or advisory version of the
new gate.

**Validation**: The focused dependency/CI suite passed `12` tests. The CI
workflow summary found the new job and all action references remained pinned.
An uncached Docker frontend-stage build using the CI command with `--no-cache`
installed `27` packages, reported zero vulnerabilities, and built the bundle
successfully. The quick and canonical agent-work validators and
`git diff --check` passed.

**Result**: PASS locally for the review remediation. Task-101 remains
`IN_PROGRESS`, alert `#76` remains open and undismissed until the accepted graph
reaches the default branch, and Task-087 remains paused through the PR #67
exact-head gate. The PR description remains the final no-later-commit evidence
source for checks triggered by this review commit.

**Next**: Push the focused review remediation, require all checks at its exact
head, and obtain merge approval before default-branch reconciliation.

---

## Validation Results

### Task Activation - August 19, 2026

**Test Status**: PASS for task activation; implementation validation remains
open

- [x] Active task membership matches `current-tasks.md`.
- [x] Task-101 is represented only as selected active work, not future backlog
  work.
- [x] Task-087 is consistently paused on Task-101 without changing completed
  implementation evidence.
- [x] Quick workspace checker, canonical validator, and `git diff --check`
  pass.
- [x] No provider key, certificate detail, browser artifact, raw support log,
  dependency secret, or package output was added.

### Focused Remediation - August 19, 2026

**Test Status**: PASS locally and at PR #72 implementation head `a87ab53`;
default-branch and PR #67 gates remain open

- [x] Exact Node/Puppeteer/lock graph and no-override contracts pass.
- [x] Clean isolated install and blocking high-severity audit pass.
- [x] CommonJS consumers and maintained frontend contracts pass.
- [x] Docker frontend and full builds pass with equivalent generated bundles.
- [x] A dedicated blocking PR job covers the Docker frontend-stage build, its
  semantic workflow contract passes, and an uncached local execution succeeds.
- [x] Main CI run `32300398378` and all three jobs in Task-087 run
  `32300398377` pass at PR #72 implementation head `a87ab53`.
- [x] Alert `#76` closed as fixed through default-branch reconciliation without
  dismissal after PR #72 squash commit `0cc189c`.
- [ ] The accepted change is semantically reconciled into PR #67 and validated
  at its new exact head before Task-087 resumes.

### Post-Merge Gate - August 20, 2026

**Test Status**: PASS for PR #72 and default-branch reconciliation; PR #67 gate
remains open

- [x] Final PR #72 CI/CD run `32308971393` and Task-087 run `32308971392`
  passed at exact head `820b649`.
- [x] PR #72 squash-merged as exact-main commit `0cc189c`.
- [x] Exact-main CI/CD run `32310281115` and Task-087 run `32310281051` passed.
- [x] Alert `#76` is fixed and every dismissal field is null.
- [ ] PR #67 contains the semantically reconciled accepted change and passes
  its required exact-head matrix before Task-087 resumes.

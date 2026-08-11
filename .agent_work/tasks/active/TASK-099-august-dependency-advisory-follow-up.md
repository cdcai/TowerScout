# TASK-099: August Dependency Advisory Follow-Up

**Status**: IN_PROGRESS
**Priority**: HIGH
**Type**: C (Security Remediation / Release Gate)
**Estimated Effort**: 0.5-1.5 days plus CI and Dependabot reconciliation
**Authorized**: August 6, 2026
**Started**: August 6, 2026

## Objective

Remediate the dependency advisories disclosed after Task-098 closed and while
this follow-up remains active,
validate the affected Python provider-client and frontend-development paths,
and restore the critical/high dependency release gate without reopening or
rewriting the completed Task-090 and Task-098 evidence.

Task-087 implementation and non-release validation may continue in parallel.
Signed-build, candidate-inclusion, and final-release qualification remain
blocked until this task passes.

## Trigger And Current Baseline

Task-098 closed on July 27 with exactly eight documented non-blocking torch
advisories: three medium and five low. GitHub disclosed four additional
Dependabot alerts on August 4-5. The August 6 repository inventory therefore
contains 12 open alerts: two high, five medium, and five low. On August 7, the
blocking npm audit also began reporting reviewed advisory
`GHSA-5p4m-2wfm-xmqj` against transitive development dependency
`js-yaml==4.3.0`. GitHub had not assigned that finding a repository Dependabot
alert number when the live inventory was reconciled, so it is tracked here by
GHSA identity without changing the 12-alert repository count.

| Alert | Package and scope | Severity | Advisory | Current | Minimum fixed | Selected target |
| ---: | --- | --- | --- | --- | --- | --- |
| `#72` | `ip-address`, npm development transitive | Medium | `CVE-2026-54272` / `GHSA-22jq-vg5j-6vgg` | `10.2.0` | `10.2.1` | `10.3.1` |
| `#73` | `ip-address`, npm development transitive | Medium | `CVE-2026-69198` / `GHSA-4xrf-jv44-h6hh` | `10.2.0` | `10.2.2` | `10.3.1` |
| `#74` | `aiohttp`, Python runtime | High | `CVE-2026-69244` / `GHSA-cq5v-8q36-5273` | `3.14.2` | `3.14.3` | `3.14.3` |
| `#75` | `ip-address`, npm development transitive | High | `CVE-2026-69192` / `GHSA-mwp4-54f8-5fhr` | `10.2.0` | `10.3.1` | `10.3.1` |
| Pending repository alert ID | `js-yaml`, npm development transitive | High | `GHSA-5p4m-2wfm-xmqj` | `4.3.0` | `4.3.1` | `4.3.1` |

The affected pins already exist on `main`. Task-087 changed neither
`webapp/requirements.txt` nor `package.json`/`package-lock.json`; its PR
surfaced the new disclosures because the Task-098 security and frontend audit
ratchets operated as designed.

## Requirements

- WHEN a new critical/high dependency advisory is disclosed after a completed
  remediation baseline, THE PROJECT SHALL track it under a new task rather
  than rewriting the completed baseline.
- WHEN `aiohttp` is updated, THE PROJECT SHALL preserve Google/Azure provider
  download, redirect, retry/timeout, cancellation, TLS, and sanitized-error
  behavior.
- WHEN the transitive `ip-address` package is updated, THE PROJECT SHALL retain
  the direct Puppeteer pin and update only the required npm lockfile graph.
- WHEN a new advisory is detected while Task-099 remains active, THE PROJECT
  SHALL add the narrow fixed dependency to Task-099 without inventing a
  repository alert ID or rewriting the completed Task-098 baseline.
- AFTER each dependency change, THE PROJECT SHALL run clean resolution,
  focused affected-path tests, and the existing critical/high CI gates.
- WHILE Task-099 is active, THE PROJECT SHALL NOT change torch, torchvision,
  ML behavior, the frozen `v0.1.2` release, or `cdcai/TowerScout`.
- AFTER the fix reaches `main`, THE PROJECT SHALL reconcile Dependabot without
  manually dismissing alerts and preserve the eight documented torch
  residuals for their future coordinated ML qualification cycle.

## Scope

Included:

- Pin `aiohttp==3.14.3` in `webapp/requirements.txt`.
- Refresh the npm lockfile so transitive development dependency
  `ip-address` resolves to `10.3.1` while Puppeteer remains unchanged.
- Resolve transitive development dependency `js-yaml` to `4.3.1` within the
  existing `cosmiconfig` range while Puppeteer remains unchanged.
- Run the maintained provider-client/TLS/sanitization and frontend contracts.
- Confirm the Python and npm critical/high security gates pass.
- Reconcile the post-merge GitHub dependency inventory and current planning
  sources.

Excluded:

- torch/torchvision or other ML dependency changes
- application feature or provider-policy changes
- Task-087 launcher/TLS-repair implementation changes
- release publication, signing, or changes to `cdcai/TowerScout`
- alert dismissal or residual-risk acceptance

## Acceptance Criteria

- [x] `aiohttp` resolves to `3.14.3` on supported Python 3.11 and 3.12 paths,
  and dependency checks report no broken requirements.
- [x] Focused aiohttp/provider/TLS/sanitized-error contracts pass without an
  application-code change.
- [x] `ip-address` resolves to `10.3.1` in `package-lock.json` without changing
  the direct Puppeteer version or adding a production dependency.
- [x] `js-yaml` resolves to `4.3.1` in `package-lock.json` without changing the
  direct Puppeteer version or adding a production dependency.
- [x] A clean npm install, blocking high-severity audit, and maintained
  frontend contracts pass.
- [x] Required Python, frontend, and security CI jobs pass at the reviewed
  Task-099 head.
- [ ] After the default-branch dependency graph refreshes, alerts `#72-#75`
  and `GHSA-5p4m-2wfm-xmqj` are fixed, no critical/high alert remains, and the
  open inventory returns to the eight documented torch residuals without
  manual dismissal.
- [x] Task tracking distinguishes the July Task-098 closeout from this August
  follow-up and passes both agent-work validators plus `git diff --check`.

## Dependencies And Boundaries

- Completed Task-090 July 23 investigation and classification.
- Completed Task-098 July 27 remediation, CI ratchet, and closeout evidence.
- GitHub Actions and Dependabot access for final default-branch
  reconciliation.
- No running Docker or Podman engine is required for planning or static
  dependency validation. Any later runtime validation must follow the normal
  runtime-startup coordination rule.

## Implementation Plan

1. Preserve the exact August 6 advisory inventory and unchanged-manifest
   provenance.
2. Apply the narrow aiohttp pin and npm transitive lockfile updates, including
   later disclosures detected before Task-099 closes.
3. Run clean Python 3.11/3.12 resolution, focused provider-client tests, clean
   npm installation/audit, and frontend contracts.
4. Run the repository quality and security gates and review the complete diff.
5. Push the isolated Task-099 branch, obtain required CI/review evidence, and
   merge only after the critical/high gates pass.
6. Reconcile post-merge Dependabot state and close Task-099 only when the
   eight-alert torch residual baseline is restored.

---

## Implementation Log

### 2026-08-06 - Task Authorized And Baseline Recorded

**Objective**: Open a separately governed follow-up for the newly disclosed
August advisories.

**Context**: Task-098 closed accurately on July 27. During Task-087 validation,
the blocking Python and npm security gates detected four advisories disclosed
August 4-5 against dependency versions already present on `main`.

**Decision**: Use the next unique task number, keep Tasks 090/098 historical,
and limit remediation to `aiohttp==3.14.3` plus transitive
`ip-address==10.3.1`. Preserve the qualified torch/torchvision pair and all
application behavior.

**Execution**: Recorded alert IDs, severities, scopes, installed versions,
fixed-version directions, task boundaries, validation obligations, and the
post-merge reconciliation gate.

**Output**: Active Task-099 control record. No dependency, code, release,
alert state, or external repository has been changed by this planning step.

**Validation**: Pending implementation, CI, and post-merge Dependabot
reconciliation.

**Next**: Apply and validate the two narrow dependency updates.

---

### 2026-08-06 - Narrow Updates Applied And Local Compatibility Gate Passed

**Objective**: Apply only the two fixed-version changes and prove that the
affected provider-client and frontend-development paths remain compatible.

**Context**: The local workstation has Python 3.12.5, Node 24.14.0, and npm
11.10.1. Python 3.11 is not installed locally. Endpoint antivirus continues
to block direct execution of the dormant Task-087 PowerShell helper, which is
unrelated to either dependency change.

**Decision**: Pin `aiohttp==3.14.3` exactly. Update only the existing
development-only `node_modules/ip-address` lock entry to `10.3.1`, using the
published npm tarball URL and integrity value; leave `package.json`,
Puppeteer, the `socks` dependency range, application code, and the qualified
ML pair unchanged.

**Execution**:

- Updated `webapp/requirements.txt`, the two maintained dependency-contract
  tests, and the single `package-lock.json` package record.
- Installed `aiohttp 3.14.3` into a temporary isolated target and ran the
  provider/TLS/runtime contracts with that target first on `PYTHONPATH`.
- Ran an exact `npm ci` with the Puppeteer browser download disabled, rebuilt
  the frontend bundle, and ran the maintained Setup Wizard and
  ProviderStateManager contracts.
- Ran the complete unit suite once, then reran it excluding only the known
  antivirus-blocked Task-087 helper module so the unaffected baseline had a
  clean exit status.

**Output**:

- `aiohttp` import from the isolated target: `3.14.3`.
- Focused Python dependency/provider/TLS/runtime set: 25 passed.
- Adjacent Azure provider integration set: 8 passed.
- Unit suite excluding the antivirus-blocked helper module: 326 passed and
  74 skipped.
- Full unit attempt: 332 passed, 74 skipped, and 19 failures; every failure
  is in `tests/unit/test_task_087_host_helper.py` and reports the existing
  endpoint `ScriptContainedMaliciousContent` block.
- `npm ci`: 98 packages installed; npm's install-time audit reported zero
  vulnerabilities.
- Lock graph: `puppeteer 24.19.0` -> `socks 2.8.7` ->
  `ip-address 10.3.1`; the direct manifest is unchanged.
- Frontend bundle reproducibility, Setup Wizard contract, and
  ProviderStateManager regression contract: PASS. The generated bundle was
  restored byte-for-byte after the build check.
- Both agent-work validators and `git diff --check`: PASS.

**Validation**: Local affected-surface and broad non-helper regression gates
pass. The explicit local npm audit endpoint was not used because the managed
execution policy rejected transmitting the repository manifest; the existing
GitHub Actions audit remains the authoritative blocking verification. Python
3.11/3.12 resolution, flake8, Trivy, and the explicit npm audit remain pending
in CI.

**Next**: Complete repository-hygiene checks, publish the isolated branch, and
require green Python, frontend, and security CI before review or merge.

---

### 2026-08-07 - Late Advisory Added Without Broad Dependency Churn

**Objective**: Restore the newly failing frontend high-severity audit while
preserving the already reviewed Task-099 dependency boundary.

**Context**: Exact-head PR #67 CI reported `GHSA-5p4m-2wfm-xmqj` after the
advisory entered GitHub's reviewed database on August 6. PR #68 still resolved
transitive `js-yaml` to affected version `4.3.0`; the existing `cosmiconfig`
range `^4.1.0` accepts patched version `4.3.1`. The August 7 live Dependabot
inventory still contained alerts `#72-#75` plus the eight torch residuals and
had not assigned the js-yaml finding a repository alert number.

**Decision**: Extend the still-active Task-099 follow-up rather than create a
second overlapping security task. Update only the existing js-yaml lock record
and its dependency contract; do not move Puppeteer, cosmiconfig, application
code, the ML pair, the frozen pilot, or cdcai.

**Execution**: Verified the npm audit record, GitHub reviewed advisory, fixed
version, registry tarball/integrity metadata, accepted cosmiconfig range, and
live repository alert inventory before editing the lockfile.

**Output**: `package-lock.json` and the maintained transitive dependency
contract now select `js-yaml==4.3.1`. Current task sources distinguish the
12-alert Dependabot inventory from the additional npm audit finding whose
repository alert ID is still pending.

**Validation**:

- Exact `npm ci`: 98 packages installed; zero vulnerabilities.
- Blocking `npm audit --audit-level=high`: zero findings.
- Resolved tree: Puppeteer `24.19.0` -> cosmiconfig `9.0.1` -> js-yaml
  `4.3.1`; Puppeteer -> socks `2.8.7` -> ip-address `10.3.1`.
- Python dependency/provider contracts: 9 passed.
- Setup Wizard and ProviderStateManager frontend contracts: passed.
- Package-lock JSON parse, both agent-work validators, CI workflow summaries,
  and `git diff --check`: passed.
- GitHub Actions at the new reviewed head: pending.

**Next**: Obtain the required review and merge PR #68 only while its exact-head
checks remain green, then reconcile the refreshed default-branch dependency
inventory.

---

### 2026-08-07 - Exact-Head CI Gate Passed

**Objective**: Prove the complete Task-099 change set, including the late
js-yaml fix, on the repository-supported CI matrix before review.

**Execution**: Published commit `84c0db2` to PR #68 and ran the standard CI/CD
and Task-087 production SetupWizard/Puppeteer workflows against that exact
head.

**Validation**:

- CI/CD run `31199160859`: Python 3.11, Python 3.12, frontend, security, and
  Trivy checks passed. The release build correctly skipped on a pull request.
- Task-087 run `31199160770`: production controller contracts, simulated-helper
  end-to-end coverage, and Windows host-helper contracts passed.
- PR #68 remained draft and unmerged; no release, signing, candidate, alert,
  or cdcai state changed.

**Next**: Record this evidence in the reviewed change set, obtain the required
review, merge only with a green final head, and reconcile Dependabot on
`main`.

---

### 2026-08-11 - Stale Root Dependency Snapshot Isolated

**Objective**: Reconcile alert `#74` without dismissal or dependency churn
after the patched Task-099 change merged to `main`.

**Context**: PR #68 merged as `f460445`, and the latest `webapp` dependency
submission records `aiohttp==3.14.3`. Alert `#74` nevertheless remains open
and undismissed because the repository SBOM also retains `aiohttp==3.14.2`
from an older root scan. Run `30285836402` submitted root correlator
`dependabot-pip` after scanning both `/requirements-dev.txt` and
`/webapp/requirements.txt`; the successful August 7 dynamic run
`31200874742` refreshed only correlator `dependabot-pip-webapp` with the
patched runtime version.

**Decision**: Make a comment-only update to the root development manifest so
a merge to the default branch triggers GitHub's native root dependency-graph
submission and replaces the stale `dependabot-pip` snapshot. Do not create a
custom higher-priority detector, dismiss the alert, or change dependency
versions, application code, ML assets, pilot packages, release state, or
`cdcai/TowerScout`.

**Execution**: GitHub rejected rerunning the dynamic workflow because dynamic
runs are not retryable, and the workflow has no `workflow_dispatch` trigger.
A corrective manual submission using the reserved `dependabot` detector name
was also rejected before any graph state changed. The root manifest now
clarifies that runtime dependencies remain in `webapp/requirements.txt`.

**Validation**:

- Focused aiohttp/provider/TLS/sanitized-error contracts: 7 passed on Python
  3.12.
- Both agent-work validators, CI workflow summary, and `git diff --check`:
  passed.
- The diff changes no dependency specifier, lockfile, workflow, application
  code, ML asset, provider behavior, or release artifact.

**Next**: Require green PR checks, merge the focused manifest refresh, then
verify the root graph no longer reports `aiohttp==3.14.2`, alert `#74` closes
without dismissal, and only the eight documented torch residuals remain.

---

## Validation Results

**Status**: REMEDIATION MERGED AND POST-MERGE CI PASS / ROOT GRAPH REFRESH AND
ALERT RECONCILIATION PENDING

Task-099 remains `IN_PROGRESS` until the focused root-manifest refresh lands
on `main` and the refreshed dependency graph confirms that only the eight
previously documented torch residuals remain open.

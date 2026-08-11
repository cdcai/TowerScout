# TASK-090: Runtime, Custom-Image, And Dependency Security Investigation

**Status**: COMPLETED
**Priority**: HIGH
**Type**: C (Security Investigation)
**Estimated Effort**: 1-3 days for investigation and classification only
**Authorized**: July 23, 2026
**Started**: July 23, 2026

## Objective

Determine whether TowerScout's local-only runtime, supported provider and
upload paths, and custom-image/model behavior make the Trivy dependency
findings actionable release risks. Record an evidence-backed disposition for
every alert in the July 23 GitHub code-scanning baseline and define, without
implementing, the separate Task-098 remediation and regression scope.

## Requirements

- WHEN GitHub reports a dependency alert in the Task-090 baseline, THE PROJECT
  SHALL record its alert number, package, vulnerability identifier, installed
  version, fixed-version direction, call-path reachability, supported-runtime
  impact, and release classification.
- WHEN a finding is reachable or affects a supported runtime boundary, THE
  PROJECT SHALL classify it as release-blocking or required hardening and
  propose remediation under Task-098.
- WHEN a critical or high finding cannot be remediated safely, THE PROJECT
  SHALL prepare an owner decision packet with compensating controls and a
  follow-up disposition.
- WHEN a finding is not reachable or is scanner/version ambiguity, THE PROJECT
  SHALL retain function-level or packaging evidence rather than equating an
  alert dismissal with proof.
- WHILE Task-090 is active, THE PROJECT SHALL NOT change dependency pins,
  dismiss alerts, modify the frozen `v0.1.2` release, or mutate
  `cdcai/TowerScout`.
- AFTER the baseline is classified, THE PROJECT SHALL recommend a reversible
  CI ratchet that prevents new critical/high findings without making the
  unremediated historical baseline immediately merge-blocking.

## Acceptance Criteria

- [x] Record the exact baseline query, source commit/ref, retrieval time, and
  count reconciliation against the July 23 62-alert assessment.
- [x] Produce a disposition table keyed by every GitHub alert number in scope.
- [x] Record package- and function-level reachability evidence.
- [x] Distinguish application dependency alerts from container-image/OS
  findings.
- [x] Propose a Task-098 patch/upgrade matrix with compatible target
  directions, estimates, dependencies, and approval gates.
- [x] Define regression requirements for Google/Azure provider downloads,
  uploads, model loading, CPU/GPU, Docker, and Podman.
- [x] Prepare an owner decision packet for any residual critical/high risk.
- [x] Recommend the post-remediation CI policy and exception process.
- [x] Pass the agent-work quick check, canonical validator, Markdown reference
  checks, and `git diff --check`.

## Dependencies

- Task-095 Phase A rebaseline: complete.
- GitHub code-scanning read access to `J-Schulein/TowerScout`: confirmed
  July 23, 2026.
- Existing assessment:
  [`GITHUB-CODE-SCANNING-READINESS-ASSESSMENT-2026-07-23.md`](../../context/analysis/GITHUB-CODE-SCANNING-READINESS-ASSESSMENT-2026-07-23.md).
- Project-lead/cdcai-owner approval is required for Task-098 implementation and
  for acceptance of any residual critical/high risk.

## Investigation Plan

1. Retrieve and normalize the live open Trivy alerts on `refs/heads/main`.
2. Reconcile the live inventory with the 62-alert July 23 baseline and its
   recorded source commit.
3. Trace each affected package and vulnerable API through TowerScout source,
   packaging, uploads, assets, and runtime boundaries.
4. Assign one release classification to every in-scope alert.
5. Define Task-098 remediation slices, validation cost, residual-risk
   decisions, and the post-baseline CI ratchet.
6. Validate the task records and present the investigation for approval.

## Investigation Outputs

- [62-record alert disposition](./TASK-090/alert-disposition.md)
- [Proposed Task-098 scope and release gate](./TASK-090/remediation-scope.md)

## Classification Vocabulary

- `RELEASE_BLOCKING`: exploitable or materially exposed on a supported path;
  remediation is mandatory before later runtime work.
- `REQUIRED_HARDENING`: a supported-path weakness with a safe available
  remediation; include it in Task-098 before final-candidate qualification.
- `ACCEPTED_RISK_CANDIDATE`: residual risk may be tolerable only with written
  owner approval, compensating controls, and follow-up.
- `NOT_REACHABLE`: the vulnerable API or input boundary is absent from
  TowerScout's supported product path, with evidence.
- `SCANNER_VERSION_FALSE_POSITIVE`: the reported installed/fixed-version
  relationship is demonstrably inapplicable or ambiguous, with evidence.

---

## Implementation Log

### 2026-07-23 - Task Start And Control-Plane Setup

**Objective**: Start the authorized investigation without crossing into
dependency remediation.

**Context**: Task-095 Phase A selected Task-090 as Sprint 08's next work item.
The repository assessment records 62 open Trivy dependency alerts on `main`
and requires alert-number-level disposition before Task-098 or Task-087.

**Decision**: Keep agent-work hygiene as the primary discipline and use the CI
quality-ratchet guidance only for the final policy recommendation. Store
sanitized Markdown evidence with this task; do not store credentials, raw
runtime captures, or provider data.

**Execution**:

- Confirmed the local branch is `chore/task-090-security-investigation`, clean,
  and aligned with `origin/main`.
- Confirmed authenticated GitHub API access can read TowerScout code-scanning
  alerts.
- Promoted Task-090 to `IN_PROGRESS` in the Sprint 08 source.
- Created this Type-C task file and fixed the investigation/remediation
  boundary.

**Output**: Active Task-090 control record.

**Validation**: Pending inventory and agent-work validation.

**Next**: Retrieve the live alert set, reconcile it to the July 23 baseline,
and begin package/API reachability mapping.

---

### 2026-07-23 - Inventory, Reachability, And Remediation Scope

**Objective**: Complete the bounded investigation and prepare the separate
Task-098 approval decision.

**Context**: The live GitHub inventory contains 62 Trivy dependency alerts
against `webapp/requirements.txt`. The source tree uses only a subset of the
named vulnerable APIs.

**Decision**:

- Classify five alerts as `RELEASE_BLOCKING`, one as
  `REQUIRED_HARDENING`, and 56 as `NOT_REACHABLE`.
- Treat the current all-interface Compose publication as a mandatory runtime
  hardening prerequisite because it contradicts the local-only product
  boundary.
- Propose Task-098 slices instead of changing pins or runtime files under this
  investigation.

**Execution**:

- Retrieved the authenticated live alert set and its rule, package, installed
  version, fixed-version direction, severity, ref, and source-commit metadata.
- Reconciled all 62 live alert numbers to the Markdown disposition table:
  zero missing, zero extra, zero duplicates.
- Traced aiohttp, Pillow, PyTorch/torchvision, Fiona/GeoPandas, Waitress,
  python-dotenv, and Flask APIs through application, vendored inference,
  upload, asset, package, and Compose paths.
- Verified relevant runtime defaults and provenance, including Pillow decoder
  registration, JPEG2000 support, Waitress lookahead `0`, Fiona GDAL `3.6.4`,
  Ultralytics full-object torch loading, and the model-upload-off default.
- Produced the Task-098 target/estimate matrix, regression plan, residual-risk
  owner packet, and CI-ratchet recommendation.

**Output**:

- [`alert-disposition.md`](./TASK-090/alert-disposition.md)
- [`remediation-scope.md`](./TASK-090/remediation-scope.md)

**Validation**:

- Live/documented alert comparison: 62/62; zero missing/extra.
- Disposition counts: five release-blocking, one required hardening, 56 not
  reachable.
- Agent-work quick check: pass.
- Canonical agent-work validator: pass.
- CI workflow summary: pass; security scan and SARIF upload remain advisory as
  intended during baseline remediation.
- Markdown task references: resolved.
- `git diff --check`: pass.

**Next**: Begin Task-098 with its pre-change baseline and maintained-test gate.
No cdcai-owner confirmation is required for fork-side remediation. Do not
resume Task-087 before the Task-098 release gate passes.

---

## Validation Results

**Status**: PASS - investigation complete and Task-098 scope approved

### Acceptance Summary

- [x] Exact 62-alert GitHub baseline reconciled.
- [x] Every alert has a package, API/call-path, fixed-version direction, and
  release classification.
- [x] Application dependency and container/OS scope distinguished.
- [x] Task-098 remediation, regression, owner-decision, and CI scopes proposed.
- [x] Repository hygiene validation passed.

No dependency pins, alert states, release assets, runtime configuration, or
external repositories have been changed.

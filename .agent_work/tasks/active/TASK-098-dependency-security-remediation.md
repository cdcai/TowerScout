# TASK-098: Dependency Security Remediation And Release Gate

**Status**: COMPLETED - PR #51 MERGED AS `e499b50`; POST-MERGE CI PASSED;
DEPENDABOT RECONCILED TO EIGHT DOCUMENTED NON-BLOCKING TORCH ADVISORIES
**Priority**: HIGH
**Type**: C (Security Remediation / Runtime Qualification)
**Estimated Effort**: Mandatory slices 4-8 days; full coordinated hardening
6-11 days, plus required GPU/runtime host availability
**Selected For Planning**: July 23, 2026

**Post-Closeout Follow-Up**: This task's eight-alert/no-high result is the
exact July 27 closeout state and remains complete. GitHub disclosed alerts
`#72-#75` on August 4-5; the separately governed
[Task-099 follow-up](./TASK-099-august-dependency-advisory-follow-up.md) owns
their narrow remediation and current release gate. Task-099 blocks signing and
candidate inclusion, not ongoing Task-087 non-release work. Do not reopen or
rewrite Task-098's checked acceptance evidence for those later disclosures.

## Objective

Implement and qualify the dependency, local-runtime, custom-image, and model
trust remediations approved from Task-090. Close every release-blocking
critical/high finding before Task-087 resumes, or obtain the explicit,
time-bounded project-lead/cdcai-owner residual-risk decision required by
`SEC-001`.

This file preserves Task-098 as a separately governed implementation and
validation task. Creating the task record does not authorize dependency or
runtime changes.

## Task-090 Inputs

- [Task-090 control record](./TASK-090-runtime-custom-image-dependency-security.md)
- [62-alert disposition](./TASK-090/alert-disposition.md)
- [Proposed remediation scope and release gate](./TASK-090/remediation-scope.md)
- [July 23 readiness assessment](../../context/analysis/GITHUB-CODE-SCANNING-READINESS-ASSESSMENT-2026-07-23.md)

Task-090 identified five release-blocking alerts, one required-hardening alert,
and an all-interface Compose port publication that conflicts with the
single-user local-runtime boundary. The exact target directions, estimates,
and work slices are preserved below as the approved implementation baseline.
Exact resolved versions and the final ML pair remain subject to the
compatibility evidence required by each slice.

## Approval Record

Complete this record when the scope decision is made. Approval authorizes only
the selected slices and candidate evaluation described here; it does not
pre-approve a residual risk or the final ML pair before compatibility evidence
exists.

| Decision field | Current value |
| --- | --- |
| Scope decision | APPROVED by the project lead on 2026-07-23, subject to the non-regression contract below |
| Approved mandatory slices | A-D and G |
| Approved coordinated-hardening slices | E and F, only when compatibility and non-regression gates pass |
| Fixed dependency targets | Target directions for A-C approved; exact resolved versions must be recorded |
| ML candidates and selection criteria | Approved as proposed; final pair/wheel flavor is selected during Slice D |
| Residual-risk path | None granted; use the decision packet below only if required |
| Project-lead approval/date | APPROVED in project chat, 2026-07-23, with explicit non-regression caveat |
| cdcai-owner boundary | Not required to start fork-side remediation; required for residual critical/high acceptance, changes to `cdcai/TowerScout`, or official cdcai adoption |

## Requirements

- WHILE Task-098 approval is pending, THE PROJECT SHALL NOT change dependency
  pins, dismiss alerts, start runtime qualification, modify the frozen
  `v0.1.2` release, or mutate `cdcai/TowerScout` under this task.
- WHEN the project lead approves the Task-098 scope, THE PROJECT SHALL
  implement only the approved remediation slices and record any later scope
  change before execution.
- WHEN the normal TowerScout package publishes its application port, THE
  PACKAGE SHALL bind the host port to loopback unless a separately approved
  deployment profile explicitly requires broader exposure.
- WHEN TowerScout accepts a custom image, THE SYSTEM SHALL verify that its
  content is an approved JPEG, PNG, or TIFF format before Pillow selects a
  decoder.
- WHEN Pillow, Waitress, or aiohttp is upgraded, THE PROJECT SHALL validate
  custom-image parsing, WSGI startup/readiness, and Google/Azure provider
  downloads against the approved target versions.
- WHEN PyTorch or torchvision is changed, THE PROJECT SHALL treat the package
  pair, CPU/CUDA wheel flavor, Docker image, release scripts, model loading,
  and CPU/GPU inference as one coordinated compatibility decision.
- WHEN release models are imported or loaded, THE SYSTEM SHALL enforce the
  approved checksum/trusted-model controls by default and keep model upload
  disabled by default.
- BEFORE the first Task-098 implementation change, THE PROJECT SHALL capture a
  reproducible functional, detection-output, startup, and performance baseline
  using the same trusted fixtures, models, host, and runtime profiles that will
  be used for comparison.
- AFTER each remediation slice, THE PROJECT SHALL run its focused tests and
  the shared production-critical workflow gate before stacking another slice.
- IF a candidate changes a user-visible workflow, detection/export result,
  supported runtime behavior, or exceeds the predeclared performance tolerance,
  THEN THE PROJECT SHALL stop, isolate or revert the slice, and investigate
  before continuing.
- IF a mandatory critical/high remediation cannot be qualified safely, THEN
  THE PROJECT SHALL stop later runtime work and obtain the written
  project-lead/cdcai-owner decision defined by Task-090.
- AFTER mandatory remediation is qualified, THE PROJECT SHALL reconcile the
  GitHub alert baseline, preserve all-severity SARIF reporting, and add the
  approved blocking CI control for new critical/high findings or unexpired,
  narrowly scoped exceptions.

## Approved Work Slices

The following baseline comes from Task-090 and is authorized by the approval
record above, subject to the non-regression contract and slice stop rules:

| Slice | Current baseline | Proposed target direction | Estimate | Gate |
| --- | --- | --- | ---: | --- |
| A: Local and input boundary | All-interface Compose publish; extension-only image validation | Bind the normal package to `127.0.0.1`; enforce JPEG/PNG/TIFF content signatures before Pillow; retain the 50 MiB cap and rate limit | 0.5-1 day | Mandatory |
| B: Narrow runtime patches | Pillow 12.2.0; Waitress 3.0.0 | Pillow 12.3.0; Waitress >=3.0.1 | 0.5-1 day | Mandatory |
| C: Provider client | aiohttp 3.9.3 | aiohttp 3.14.2; minimum alert fixes converge at 3.14.1 | 0.5-1 day | Mandatory |
| D: ML runtime | torch 2.2.1; torchvision 0.17.1; CPU/CUDA 12.1 package paths | Evaluate at least torch 2.6.0 + torchvision 0.21.0 and a currently supported pair; select one pair and its CPU/CUDA wheel flavors from compatibility evidence | 2-4 days plus GPU hosts | Mandatory or explicit residual-risk decision |
| E: Geospatial | Fiona 1.9.6/GDAL 3.6.4; GeoPandas 0.14.3 | Select stable Fiona >=1.10.1 and GeoPandas >=1.1.2 together | 1-2 days | Required hardening if compatibility passes |
| F: Config/web framework | python-dotenv 1.0.0; Flask 3.0.2 | python-dotenv 1.2.2; Flask 3.1.3 | 0.5-1 day | Required hardening if compatibility passes |
| G: Model trust | Runtime hash verification defaults off; model upload defaults off | Verify release-model hashes by default; preserve upload-off default; constrain any trusted-model override to loopback and trusted files | 0.5-1 day | Mandatory with the ML decision |

Approval must record the selected slices and fixed targets for Slices A-C.
For Slice D, approval records the candidate set and selection criteria; the
final torch/torchvision pair, CUDA flavor, and affected package-script changes
are recorded after the compatibility spike and before migration. Slices E-F
may be approved conditionally rather than forcing incompatible upgrades.

## Required Regression Matrix

| Surface | Required evidence |
| --- | --- |
| Static dependency resolution | Clean Python 3.11 and 3.12 installs; exact resolved versions; no incompatible wheel or unintended source-build fallback |
| Google provider | TLS-verified tile and metadata downloads; header parsing; redirect; retry/timeout; cancellation; sanitized errors |
| Azure provider | TLS-verified tile and attribution/metadata downloads; header parsing; redirect; retry/timeout; cancellation; sanitized errors |
| Custom image | Valid JPEG/PNG/TIFF; renamed EPS/JPEG2000/McIdas rejection before Pillow; malformed and oversized rejection; output drawing |
| Waitress | Startup/readiness; loopback-binding contract; request-size cap; malformed and disconnected-client regression where practical |
| EfficientNet | Known-checksum model loads with `weights_only=True`; representative-crop inference on CPU and CUDA |
| YOLO | Vendored full-object checkpoint loads only from a trusted, checksummed path; representative inference parity on CPU and CUDA |
| Model upload | Disabled by default; constrained trusted-local override only; filename/type/size validation; no non-loopback exposure |
| Geospatial | Packaged ZIP-code shapefile loads and returns representative geometry on Python 3.11 and 3.12 |
| Configuration/session | Setup/settings config read/write; secret persistence; filesystem-session routes; cache headers |
| Production-critical workflows | Setup/settings; estimate/detect/cancel; review/list/map; manual tower; CSV/KML/dataset export; restore; ZIP search; health/readiness |
| Performance | Same-host three-run warmed medians for startup, YOLO/EfficientNet inference, total local detection, and peak memory; investigate >10% degradation |
| Package/runtime | Rebuilt image plus Docker CPU, Docker GPU, Podman CPU, and Podman GPU before final-candidate qualification |

Unit, static, and compatibility-spike work does not require a running
container engine. Before rebuilt-image or four-profile validation, ask the
user to start the exact Docker Desktop and/or Podman profiles required.

## Non-Regression Contract

No engineering process can guarantee that an undiscovered regression is
impossible. Task-098 therefore uses prevention, early detection, rollback, and
final runtime qualification as independent safeguards. A security fix is not
accepted merely because the vulnerability scan clears.

### Baseline Before Change

Before changing a pin or runtime boundary:

1. Record the source commit, resolved dependencies, model and asset checksums,
   Python version, engine/profile, GPU/driver where applicable, and safe test
   fixture identity.
2. Run the blocking unit and affected integration suites on Python 3.11 and
   3.12.
3. Capture same-fixture Google and Azure estimate/detect/cancel results,
   detection/list/map counts, export/restore state, startup/readiness timing,
   YOLO/EfficientNet phase timing, total detection timing, and peak memory.
4. Use at least three warmed runs on the same host for local compute timing.
   Network timing is recorded but excluded from a strict percentage comparison
   because provider/network variance is not controlled.
5. Declare numeric detection-output tolerances before evaluating an ML
   candidate. Exact workflow state, counts, schemas, and manual/export/restore
   semantics remain mandatory; tolerances may not be widened after candidate
   results are known.

### Slice Isolation And Rollback

- Implement A, B, C, D/G, E, and F as independently reviewable changes with a
  known-good rollback point.
- Do not stack the next slice over a failing focused or shared regression gate.
- Keep confidence thresholds, tiling, NMS, coordinate precision, provider
  semantics, export schemas, and frontend behavior unchanged unless a
  separately approved change is required.
- A dependency upgrade that requires unrelated feature redesign is a stop
  condition, not an implicit expansion of Task-098.

### Blocking Comparison Gates

The following must pass before Task-098 sign-off:

- all existing blocking CI checks on Python 3.11 and 3.12
- new focused tests for image signatures/decoder rejection, loopback publish,
  Waitress request behavior, aiohttp provider behavior, model trust, and every
  upgraded optional package path
- the affected integration tests as a blocking Task-098 gate even while the
  repository's broad historical integration job remains advisory
- setup/settings, Google/Azure estimate/detect/cancel, detection review/list/map,
  custom-image success, manual tower, CSV/KML/dataset export, restore,
  ZIP-code search, session persistence/reset, health/readiness, and model-upload
  default-off workflows
- trusted-model YOLO and EfficientNet output parity on CPU and CUDA
- a rebuilt CPU image plus Docker CPU and Docker GPU dependency-compatibility
  evidence before Task-098 sign-off
- Docker CPU, Docker GPU, Podman CPU, and Podman GPU operational package
  qualification under Task-097/Task-091 before final-candidate sign-off

The current browser harness records durations but does not enforce a
performance budget. Task-098 therefore adds an explicit comparison:

- more than 10% degradation in the median of same-host warmed startup,
  YOLO/EfficientNet inference, total local detection time, or peak memory is a
  blocking investigation threshold
- any clear user-visible slowdown or timeout regression is blocking even when
  the measured change is below 10%
- a different threshold may be approved only before the candidate comparison,
  with a written reason; a measured regression is never silently accepted

### CI And Final-Qualification Boundary

Hosted CI can block deterministic unit, integration, dependency-resolution,
CPU image-build, and security checks. It cannot prove provider, Windows
launcher, Podman, or physical-GPU behavior. Those checks require sanitized
manual/runtime evidence and remain hard Task-098 completion gates rather than
being mislabeled as automated CI coverage.

## Residual Critical/High Decision Packet

Use this packet only if a mandatory upgrade cannot be qualified safely. It
does not constitute advance acceptance.

The owners must choose one:

1. Delay later runtime work and complete a compatible upgrade.
2. Accept a time-bounded residual risk through the final candidate.
3. Remove or disable the affected capability from the supported release.

Option 2 requires all of the following:

- exact unresolved alert IDs and vulnerable versions
- failed upgrade candidates and reproducible compatibility evidence
- proof that normal release model upload remains disabled
- loopback-only package binding
- release and individual model checksum enforcement enabled by default
- explicit trusted-model-only documentation
- expiration no later than the October 9 freeze unless renewed
- named owner and follow-up task
- written project-lead and cdcai-owner approval

## CI Ratchet

Keep the existing all-severity Trivy SARIF path advisory while Task-098 is
remediating the known baseline. After mandatory remediation:

1. Preserve all-severity SARIF generation/upload with `if: always()`.
2. Add a separate filesystem gate for `CRITICAL,HIGH` with `exit-code: 1`.
3. Do not use blanket `ignore-unfixed`; every direct critical/high finding
   still requires a reachability decision.
4. Represent any owner-approved residual finding with a narrow
   `.trivyignore.yaml` entry scoped to the vulnerability and package path,
   including a written statement and `expired_at`.
5. Pin the action and Trivy versions, record the baseline database/version,
   and add a scheduled scan.
6. Fail every new critical/high finding not covered by an unexpired approved
   exception.

Validate the exact pinned action behavior before making the new gate blocking.

## Acceptance Criteria

### Approval And Traceability

- [x] The Task-090 alert inventory and reachability classifications are final.
- [x] This task's proposed slices, targets, estimates, regression matrix,
  residual-decision packet, and CI ratchet align with Task-090.
- [x] The project lead approves the Task-098 implementation scope with the
  explicit non-regression caveat recorded above.
- [x] Fork-side implementation requires no separate cdcai-owner confirmation.
  Residual critical/high acceptance, changes to `cdcai/TowerScout`, and
  official cdcai adoption retain their explicit owner gates.
- [x] Every Task-098 change maps to an approved alert, runtime boundary, or
  compensating control.

### Non-Regression Gate

- [x] A pre-change baseline records dependencies, fixtures, model/assets,
  output parity, workflow results, timings, and peak memory.
- [x] Each mandatory slice passes focused tests and the shared workflow gate
  before the next slice begins.
- [x] Dedicated maintained tests replace reliance on the skipped legacy
  validation and image-processing contracts for every touched path.
- [x] Detection state/counts, review/map/list behavior, manual tower semantics,
  and export/restore schemas are unchanged; numeric ML tolerances were declared
  before candidate evaluation and pass.
- [x] Same-host warmed median startup, inference, local detection time, and
  peak memory remain within the 10% investigation threshold unless a different
  threshold was approved before comparison.
- [x] Live Google and Azure workflows plus Docker CPU/GPU dependency
  compatibility pass before Task-098 sign-off; Task-097/Task-091 retain the
  final four-profile operational package matrix.

### Mandatory Remediation

- [x] The normal release package binds TowerScout to loopback and a contract
  test prevents regression to an all-interface default.
- [x] Custom-image validation rejects content-sniffed EPS, JPEG2000, McIdas,
  malformed, and oversized inputs before vulnerable Pillow decoding; valid
  JPEG/PNG/TIFF behavior, the 50 MiB cap, and rate limiting remain intact.
- [x] Approved Pillow, Waitress, and aiohttp targets are pinned consistently
  and pass their focused image, WSGI, and provider regression suites.
- [x] The approved torch/torchvision CPU/CUDA pair passes clean dependency
  resolution, trusted model loading, and representative YOLO/EfficientNet
  inference.
- [x] Release-model checksum enforcement is enabled by default and model
  upload remains disabled by default; any enabled override is loopback-bound
  and restricted to trusted files.

### Compatibility And Runtime Qualification

- [x] Clean Python 3.11 and 3.12 dependency installs resolve without
  incompatible wheels or unintended source-build fallback.
- [x] Google and Azure provider downloads pass TLS-verified header parsing,
  redirect, timeout/retry, cancellation, and sanitized-error tests.
- [x] ZIP-code shapefile behavior and setup/settings/session behavior pass for
  every approved geospatial or web-framework hardening change.
- [x] Rebuilt images pass dependency-focused Docker CPU and Docker GPU
  validation for the Task-098 changes. Task-097/Task-091 retain Podman CPU/GPU
  and the final four-profile operational package matrix.
- [x] Before each Task-098 runtime stage, the user is asked to start the exact
  Docker Desktop profile needed and confirms it is running.

### Release Gate And Handoff

- [x] No release-blocking critical/high finding remains unresolved.
- [x] The residual-risk decision packet was not invoked: the eight remaining
  torch advisories are classified as non-reachable and non-release-blocking
  for the supported runtime, with a future coordinated ML requalification
  disposition rather than accepted residual product risk.
- [x] GitHub code-scanning state is reconciled without treating raw alert
  count alone as proof of safety.
- [x] The approved CI ratchet fails new critical/high findings unless covered
  by a narrow, unexpired exception.
- [x] Task-098-specific requirements, design, task status, dependency notices,
  package manifests, and owner-maintenance guidance reflect the merged result.
  Task-098 produced no release artifact; final-candidate release notes and the
  detailed administrator Model Upload Key instructions remain assigned to
  Task-092 and `DOC-001`.
- [x] Task-087 remains paused until this release gate is signed off.

## Dependencies

- Completed Task-090 evidence-backed classification.
- Project-lead approval of the implementation scope.
- Approved dependency target pairs and wheel/runtime strategy.
- Existing CPU/GPU test hosts and managed Windows Docker/Podman environments.
- Model and data assets with known checksums.
- GitHub code-scanning and Actions access for final reconciliation.

## Stop Rules

- Stop if a dependency target would require an unplanned package-format,
  supported-profile, model-format, or provider-behavior change.
- Stop if a clean CPU/CUDA wheel set cannot be produced for the approved
  Python and container baseline.
- Stop if model-load or inference parity cannot be demonstrated with trusted
  release assets.
- Stop and isolate or revert the current slice if a blocking test, production-
  critical workflow, output-parity comparison, or performance threshold fails.
- Stop if the only evidence for a touched validation or image path is an
  intentionally skipped legacy test; add a maintained focused test first.
- Stop before accepting or dismissing any residual critical/high alert without
  the required written owner decision.
- Stop before runtime validation until the user confirms the required runtime
  is running.
- Do not publish `v0.1.3` final or change `cdcai/TowerScout` as part of this
  task.

## Implementation Plan

1. Record the approved Task-090-to-Task-098 scope, exact targets, validation
   matrix, same-fixture functional/output/performance baseline, and rollback
   points; for ML, record the approved candidate set and selection criteria.
2. Add or update maintained focused regression tests before changing the
   behavior they protect.
3. Implement the loopback, custom-image, and model-trust boundaries with
   focused tests.
4. Apply and validate the narrow Pillow, Waitress, and aiohttp upgrades.
5. Complete the coordinated ML compatibility spike, record the selected
   torch/torchvision/wheel pair, and then perform the approved migration.
6. Apply approved geospatial and config/web-framework hardening only after
   clean compatibility proof.
7. Run blocking Python, provider, workflow, output-parity, performance, upload,
   WSGI, model, package, Docker, and Podman regression in staged gates.
8. Reconcile every affected alert, document residual decisions, and ratchet CI
   for new critical/high findings.
9. Obtain Task-098 sign-off before Task-087 resumes.

---

## Implementation Log

### 2026-07-23 - Planning Record Created

**Objective**: Preserve Task-098 as a visible, separately governed follow-on
to Task-090.

**Context**: Task-098 existed in the backlog, requirements, design, roadmap,
and Task-090 proposed scope, but did not yet have an individual task file. The
project lead requested a durable task record so mandatory remediation is not
lost after Task-090.

**Decision**: Create the Type-C task file in the current Sprint 08 task area
with a planned/pending-approval status. Carry forward Task-090's proposed
slices while making the approval and no-implementation boundary explicit.

**Execution**: Created this task control record and linked it to the Task-090
disposition and remediation-scope documents.

**Output**: A durable Task-098 plan that can be finalized without renumbering
or recreating the task.

**Validation**: Agent-work structure, references, and Markdown validation are
required after task-state alignment.

**Next**: Obtain project-lead/cdcai-owner approval, replace proposed target
directions with the approved matrix, and then mark Task-098 `IN_PROGRESS`.

---

### 2026-07-23 - Task-090 Scope Alignment Review

**Objective**: Confirm that the Task-098 task record is sufficiently complete
to begin once its implementation scope is approved.

**Context**: The initial Task-098 record preserved the intended slices and
release gate but summarized several execution-critical details from Task-090.
It also required a final ML pair before the compatibility spike intended to
select that pair.

**Decision**: Preserve the proposed target versions, estimates, full regression
matrix, residual-decision evidence, and CI ratchet directly in this task.
Approve an ML candidate set and selection criteria at the start gate, then
record the final pair after the spike and before migration.

**Execution**: Reconciled this task against Task-090's alert disposition and
proposed remediation scope, `SEC-001`, the dependency-security design
boundary, the current dependency pins, Compose exposure, PyTorch package
surfaces, and the current advisory Trivy workflow.

**Output**: The Task-098 record now has an approval form, traceable target
matrix, complete validation obligations, explicit residual-risk choices, and
an executable CI ratchet without granting implementation authority.

**Validation**: Agent-work structure, local Markdown links, and whitespace
validation passed after this update.

**Next**: Record the owner scope decision. If approved, mark Task-098
`IN_PROGRESS` and begin Slice A plus fixed-target compatibility checks; select
the final ML pair only after Slice D evidence exists.

---

### 2026-07-23 - Scope Approval With Non-Regression Caveat

**Objective**: Record the project lead's approval while ensuring dependency
security work cannot silently trade away application behavior or performance.

**Context**: The project lead approved the proposed scope and asked for
confirmation that regressions would be prevented or caught before later
discovery. Existing tests provide meaningful coverage, but the broad
integration job and image build are advisory in current CI, live provider
smokes require a managed runtime, and legacy validation/image-processing test
modules are intentionally skipped.

**Decision**: Accept the scope approval with a binding non-regression contract.
Require pre-change baselines, maintained focused tests, slice-level rollback
points, blocking affected integration checks, production-critical workflow and
output parity, a 10% same-host performance investigation threshold, and final
Google/Azure four-profile qualification.

**Execution**: Reviewed current CI, 33 unit-test files, seven integration-test
files, the browser detection harness, ML/model tests, upload/config/assets
tests, runtime/package tests, and performance instrumentation. Ran the
available non-runtime baseline described below.

**Output**: Project-lead scope approval is recorded. Task-098 is ready to begin
with the pre-change baseline and maintained-test gates; no separate cdcai-owner
confirmation is required for fork-side remediation.

**Validation**: Agent-work structure, local Markdown links, and whitespace
validation passed after this update.

**Next**: When Task-098 starts, capture clean Python 3.11/3.12 non-runtime
baselines and add maintained focused tests. Request the exact container
runtimes only when reaching container-dependent baseline or validation stages.

---

### 2026-07-24 - Execution Started And Baseline Gate Opened

**Objective**: Begin the approved Task-098 work without changing dependencies
or runtime behavior before the non-regression baseline is recorded.

**Context**: Task-090 and the Task-098 approval record were preserved in commit
`d336686`. Task-098 is being executed on the short-lived child branch
`fix/task-098-dependency-security` because it depends on that unmerged planning
checkpoint.

**Decision**: Move Task-098 to `IN_PROGRESS`, treat baseline capture as the
only active implementation phase, and defer dependency/runtime mutations until
the available Python 3.11/3.12, model, workflow, and performance evidence is
recorded.

**Execution**: Corrected stale pending-approval wording, opened the task-local
baseline record, and began environment and maintained-test discovery.

**Output**: Task state now matches execution reality, with a known planning
checkpoint and isolated implementation branch.

**Validation**: Agent-work validation and whitespace checks are required after
the task-state update. Baseline commands and results are recorded in
[`TASK-098/baseline.md`](./TASK-098/baseline.md).

**Next**: Complete the non-runtime baseline, identify unavailable external
runtime evidence explicitly, and only then begin Slice A.

---

### 2026-07-24 - Local Python 3.12 Baseline Completed

**Objective**: Capture the locally available clean-resolution, maintained-test,
trusted-model, deterministic-output, and same-host performance evidence.

**Context**: The host provides Python 3.12 and 3.13 but not the supported
Python 3.11 baseline required by the non-regression contract.

**Decision**: Complete and preserve the full local Python 3.12 baseline, record
the broad integration failures as pre-change drift, and stop before Slice A
until Docker Desktop CPU can provide the clean Python 3.11 environment.

**Execution**: Built an isolated Python 3.12 CPU environment in ignored task
scratch, reproduced the Docker dependency order, ran unit/integration and
frontend contracts, verified trusted asset hashes, and ran the maintained
three-sample CPU model/startup probe.

**Output**: Unit, ML-focused, frontend-contract, flake8, dependency, asset, and
deterministic CPU model baselines are recorded. The broad integration suite
has four pre-existing geocoding failures and is not represented as clean.

**Validation**: See [`TASK-098/baseline.md`](./TASK-098/baseline.md) for exact
versions, counts, hashes, timings, outputs, and unresolved external gates.

**Next**: Ask the user to start Docker Desktop for the exact Docker CPU /
Python 3.11 baseline. Do not begin Slice A until that gate is recorded.

---

### 2026-07-24 - Docker CPU Python 3.11 Baseline Completed

**Objective**: Close the required pre-change baseline gate without allowing
pre-existing Docker state to influence Task-098.

**Context**: Docker Desktop was available, while a healthy older TowerScout
container and several unrelated local images and volumes already existed.

**Decision**: Build a uniquely tagged CPU image from the recorded source
checkpoint with fresh base pulls and no build cache. Run tests with no Compose
project or published ports, mount repository source and trusted models
read-only, and place every writable path on disposable tmpfs.

**Execution**: Built the Python 3.11 image, verified its OCI source/flavor
labels, ran dependency checks, unit and broad integration suites, the focused
ML gate, and the maintained three-sample CPU model/performance probe. Removed
all Task-098 test containers and disposable storage while retaining the unique
baseline image for after-change comparison.

**Output**: Python 3.11 dependency resolution and `pip check` passed. Unit tests
reported 212 passed and 121 platform/feature skips. The broad integration suite
reproduced the same 20-pass, 2-skip, 4-failure geocoding drift recorded on
Python 3.12. The focused ML gate passed 8 tests, and deterministic YOLO and
EfficientNet outputs matched the host baseline.

**Validation**: The pre-existing RC7.1 container remained healthy on its
existing port. No Task-098 test container remains, no existing application
image was used, and the image/test identities, exact counts, timings, and
isolation controls are recorded in
[`TASK-098/baseline.md`](./TASK-098/baseline.md).

**Next**: Begin Slice A by adding maintained focused tests for loopback
publication and content-signature image rejection before changing behavior.

---

### 2026-07-24 - Slice A Local And Input Boundary Completed

**Objective**: Remove the normal package's all-interface publication and
prevent unsupported custom-image content from selecting vulnerable Pillow
decoders.

**Context**: Compose published `${TOWERSCOUT_PORT}` on every host interface,
and custom-image validation trusted an allowed filename extension before the
route saved the upload and called Pillow.

**Decision**: Add maintained regression tests before behavior changes. Bind the
normal Compose package explicitly to `127.0.0.1`. Allowlist JPEG, PNG, and TIFF
magic bytes before Pillow is called, require extension/content agreement, then
use Pillow's `verify()` only through the selected approved decoder to reject
malformed supported files.

**Execution**: Added `tests/unit/test_task_098_slice_a.py`; changed
`compose.yaml`; and extended `TowerScoutValidator.validate_image_file`.
Preserved the existing 50 MiB size gate, upload rate limit, sanitized filename,
valid-image detection path, and result drawing.

**Output**: The test-first gate initially reported 9 expected failures and 7
preservation passes. After implementation, the Slice A and current route
hardening set passed 23 tests. Docker Compose resolved the published mapping as
host `127.0.0.1`, port 5000, target 5000.

**Validation**:

- Python 3.12 full unit suite: PASS, 275 passed and 74 legacy skips.
- Python 3.11 Docker CPU full unit suite: PASS, 228 passed and 121
  Linux/platform-feature skips.
- Python 3.12 broad integration: unchanged baseline drift, 20 passed, 2
  skipped, and the same 4 geocoding failures.
- Setup Wizard and ProviderStateManager JavaScript contracts: PASS; the forced
  Azure failure output remained the expected negative-path assertion.
- Blocking Flake8 and targeted Bandit: PASS.
- Black under Python 3.11: PASS for the new maintained test file. The existing
  whole-file `ts_validation.py` formatting drift remains the repository's
  advisory baseline and was not expanded into an unrelated reformat.
- Docker isolation: no Task-098 container remains; the pre-existing RC7.1
  container remained healthy and was not changed.

**Next**: Create a Slice A commit checkpoint, then begin Slice B's narrow
Pillow/Waitress patch with clean-resolution and focused image/WSGI tests.

---

### 2026-07-24 - Slice B Pillow And Waitress Patch Completed

**Objective**: Apply the approved narrow Pillow and Waitress security patches
without changing supported image behavior, WSGI readiness, model output, or
runtime performance beyond the declared investigation threshold.

**Context**: The approved Slice B baseline pinned Pillow 12.2.0 and Waitress
3.0.0. Pillow 12.3.0 is the approved July 2026 security release, and Waitress
3.0.2 includes the 3.0.1 half-open/request-smuggling fixes plus the subsequent
trusted-proxy-header correction. Upstream references:
[Pillow 12.3.0 release notes](https://pillow.readthedocs.io/en/stable/releasenotes/12.3.0.html)
and [Waitress 3.0.2 project history](https://pypi.org/project/waitress/).

**Decision**: Pin Pillow 12.3.0 and Waitress 3.0.2 exactly. Keep the existing
torch 2.2.1+cpu / torchvision 0.17.1+cpu pair unchanged, align the YOLO runtime
minimum with the Pillow pin, and add a maintained loopback WSGI contract before
accepting the new versions.

**Execution**: Added `tests/unit/test_task_098_slice_b.py`; updated
`webapp/requirements.txt`, the Pillow minimum in `webapp/ts_yolov5.py`, and
the local-loader dependency fixture. The maintained Waitress contract covers
readiness, the request-body cap, malformed headers, a half-open client
disconnect followed by readiness recovery, and clean server shutdown.

**Output**: Clean Python 3.12 resolution selected Pillow 12.3.0 and Waitress
3.0.2 with no broken requirements. Runtime dependencies resolved from wheels
except the repository's pre-existing, source-only pure-Python
`efficientnet-pytorch==0.7.1`; this was an intentional known exception rather
than a new native source-build fallback. The disposable Python 3.11 container
upgraded only Pillow and Waitress over the isolated clean baseline layer and
retained the pinned CPU torch pair.

**Validation**:

- Focused Slice A/B, route, and YOLO loader gate: PASS, 31 tests on both
  Python 3.12 and containerized Python 3.11.
- Python 3.12 full unit suite: PASS, 277 passed and 74 legacy skips.
- Python 3.11 Docker CPU full unit suite: PASS, 230 passed and 121
  Linux/platform-feature skips.
- Broad integration on both versions: unchanged baseline drift, 20 passed, 2
  skipped, and the same 4 pre-existing geocoding failures.
- Setup Wizard and ProviderStateManager JavaScript contracts: PASS; the forced
  Azure failure output remained the expected negative-path assertion.
- Python 3.11 `pip check`, targeted Black, and blocking Flake8: PASS.
- Deterministic CPU model output: PASS; YOLO counts remained `[0, 0, 0]` and
  EfficientNet scores remained `[0.8266443, 0.8266443, 0.8266443]`.
- Same-host container comparison: startup and both inference medians improved;
  peak RSS changed from 1,385,152,512 to 1,459,650,560 bytes, a 5.38% increase
  below the 10% investigation threshold.
- Docker isolation: the disposable Slice B container was removed, the unique
  baseline image was retained for later comparison, and the pre-existing
  RC7.1 container was not reused or changed.

**Next**: Create a Slice B commit checkpoint, then begin Slice C's approved
aiohttp 3.14.2 provider-client patch with maintained Google/Azure download,
redirect, timeout/retry, cancellation, and sanitized-error tests.

---

### 2026-07-24 - Slice C aiohttp Provider Client Patch Completed

**Objective**: Remove the release-blocking aiohttp response-header parser
baseline while preserving Google/Azure download, retry, cancellation, TLS,
and sanitized-error behavior.

**Context**: TowerScout's live aiohttp surface is the fixed-host map-provider
client in `webapp/ts_maps.py`. The approved target is aiohttp 3.14.2, whose
official release history records the 3.14.1 cancellation/connector fixes and
the July 20, 2026 3.14.2 patch:
[aiohttp changelog](https://docs.aiohttp.org/en/stable/changes.html).

**Decision**: Pin aiohttp 3.14.2 exactly without changing provider application
code. Add maintained client tests that exercise the real aiohttp response
parser against a loopback fixture and retain the existing shared provider TLS
connector contract.

**Execution**: Added `tests/unit/test_task_098_slice_c.py` and updated the
aiohttp pin in `webapp/requirements.txt`. The new contracts cover Google and
Azure redirect-following and file writes, `Retry-After` parsing and retry,
timeout categorization, cancellation propagation, and credential redaction.
The test-first run on aiohttp 3.9.3 produced the single expected pin failure
while all six behavior-preservation tests passed.

**Output**: Python 3.12 and Python 3.11 selected the platform wheel for aiohttp
3.14.2, added `aiohappyeyeballs`, and passed `pip check`. No provider runtime
code, concurrency limit, timeout, retry count, TLS policy, URL construction,
or output file behavior changed.

**Validation**:

- Focused aiohttp/provider/TLS-runtime/Azure integration gate: PASS, 31 tests
  on both Python 3.12 and containerized Python 3.11.
- Python 3.12 full unit suite: PASS, 284 passed and 74 legacy skips.
- Python 3.11 Docker CPU full unit suite: PASS, 237 passed and 121
  Linux/platform-feature skips.
- Broad integration on both versions: unchanged baseline drift, 20 passed, 2
  skipped, and the same 4 pre-existing geocoding failures.
- Setup Wizard and ProviderStateManager JavaScript contracts: PASS; the forced
  Azure failure output remained the expected negative-path assertion.
- Targeted Black and blocking Flake8: PASS.
- Deterministic CPU model output: PASS; YOLO counts remained `[0, 0, 0]` and
  EfficientNet scores remained `[0.8266443, 0.8266443, 0.8266443]`.
- Same-host container comparison: startup and both inference medians improved;
  peak RSS changed from 1,385,152,512 to 1,457,643,520 bytes, a 5.23% increase
  below the 10% investigation threshold.
- Docker isolation: the disposable Slice C container was removed, the unique
  baseline image was retained, and the pre-existing RC7.1 container was not
  reused or changed.

**Next**: Create a Slice C commit checkpoint. Begin the Slice D/G coordinated
ML compatibility spike only after confirming the exact Docker GPU profile
needed for CPU/CUDA pair selection and model-trust qualification.

---

### 2026-07-24 - Slice D/G CPU Selection And GPU Handoff Prepared

**Objective**: Select the coordinated torch/torchvision CPU and CUDA pair,
enforce trusted-model loading, and make the remaining physical-GPU
qualification reproducible on another device.

**Candidate decision**: Evaluated the approved minimum pair
`torch==2.6.0` / `torchvision==0.21.0` and the current stable pair
`torch==2.13.0` / `torchvision==0.28.0`. PyTorch's official
[previous-version instructions](https://docs.pytorch.org/get-started/previous-versions/)
identify the 2.6 pair, and the official
[2.13 general-availability announcement](https://dev-discuss.pytorch.org/t/pytorch-2-13-0-general-availability/3412)
identifies torchvision 0.28.0 as its paired release. Both pairs resolved from
official CPU wheels and passed trusted YOLO/EfficientNet loading and exact
deterministic output checks.

The 2.13 pair was rejected under the predeclared performance stop rule:
process RSS after both model probes was 1,586,032,640 bytes versus the
1,385,152,512-byte Docker baseline, a 14.50% increase. The selected 2.6 pair
used 1,388,580,864 bytes, a 0.25% increase. No threshold was widened after
observing the result.

**Selected package**:

- `torch==2.6.0`
- `torchvision==0.21.0`
- CPU wheels from `https://download.pytorch.org/whl/cpu`
- CUDA 12.6 wheels from `https://download.pytorch.org/whl/cu126`
- package flavor identity `cuda126`

**Model trust**: Release-model SHA-256 and byte-size checks now run by default
in readiness and immediately before either checkpoint is deserialized. Broad
ZIP-code/data hashing remains opt-in, preventing every readiness request from
rehashing the 822 MiB shapefile. The model hash cache is invalidated by file
identity, size, modification time, and change time. At this checkpoint, the
model-upload route remained disabled by default and an enabled override
attempted to authorize the request's loopback peer before applying the
local-admin SHA-256 allowlist. The July 27 PR review found that Docker host
forwarding does not preserve that loopback peer address; the later review
remediation replaced the unreliable peer test with an administrator key while
retaining the trusted-hash requirement.

**Package alignment**: Requirements, Docker build arguments, Compose build
defaults, container publishing, Windows launcher selection, release packaging,
release-manifest contracts, package naming, and active CPU/GPU documentation
now use the selected pair and CUDA 12.6 flavor consistently.

**CPU evidence**:

- Clean Python 3.12 selected-pair resolution and `pip check`: PASS; official
  `2.6.0+cpu` / `0.21.0+cpu` wheels selected with no broken requirements.
- Python 3.12 selected-pair unit gate: PASS, 292 passed and 74
  legacy/platform skips.
- Python 3.12 selected-pair model probe: PASS; exact fixture outputs,
  1,343,508,480-byte RSS, and trusted release hashes.
- Python 3.11 selected-image unit gate: PASS, 245 passed and 121
  Linux/platform skips; `pip check` reported no broken requirements.
- Broad integration on both versions: unchanged baseline drift, 20 passed,
  2 skipped, and the same 4 pre-existing geocoding failures.
- Selected-image model probe: PASS; YOLO counts `[0, 0, 0]`, EfficientNet
  scores `[0.82664418, 0.82664418, 0.82664418]`, trusted release hashes exact.
- Selected-image warmed medians: startup 4.497028 seconds, YOLO inference
  2.268855 seconds, EfficientNet inference 0.657228 seconds.
- Selected-image process RSS: 1,388,580,864 bytes, 0.25% above baseline.
- Packaged loopback startup: health `ok`, readiness `setup_required`, assets
  `ok`, release-model hashing enabled, selected device `cpu`, torch
  `2.6.0+cpu`.
- Docker isolation: both candidate images used `--pull --no-cache`; every
  Task-098 container was disposable and removed. The pre-existing RC7.1
  container remained healthy and unchanged on port 5005.

**External GPU handoff**: Added
`scripts/task098-qualify-ml.ps1` and
`scripts/task098_ml_qualification.py`. The wrapper refuses a dirty tracked
worktree, records the checked-out source commit, builds a unique no-cache
CUDA 12.6 image, publishes no port, runs the qualification container
read-only with disposable writable paths, mounts only trusted model assets,
and writes one sanitized JSON result under ignored `.agent_work/tmp/`.
CUDA output parity, selected-device enforcement, model hashes, warmed
timings, RSS, and peak allocated VRAM are blocking fields.

**External GPU gate**: The Slice D/G commit was checked out on a validated
NVIDIA Docker host and the unmodified qualification wrapper was run:

```powershell
.\scripts\task098-qualify-ml.ps1 -Profile cuda
```

The returned `qualification.json` reports `passed: true` for source commit
`675bd8fabc27765522906957524d2027d931f6a1`, image
`towerscout:task098-675bd8fabc27-cuda126-torch2-6-0`, Python `3.11.15`,
torch `2.6.0+cu126`, and torchvision `0.21.0+cu126`. YOLO and EfficientNet
both selected CUDA on an NVIDIA T1000 8GB (compute capability 7.5); output
parity, declared tolerances, release-manifest model hashes, and version checks
all passed. Peak allocated CUDA memory was 811,165,696 bytes and process RSS
was 1,535,275,008 bytes.

The companion sanitized context records a clean detached checkout, no modified
harness/source/threshold/evidence files, a disposable read-only qualification
container with no published ports, and no change to pre-existing containers or
images. Raw artifacts remain in external Task-098 evidence custody rather than
the repository:

- `qualification.json` SHA-256:
  `3D3F6D8510520593DE7276788E4DE95B7EA68BDF08246B04632A85914C407690`
- `GPU-Device Evidence Context.docx` SHA-256:
  `2D9AB4EDA877658C1607F2C5E358B6141E137680A4D1218D78CEF9A9C98DF0D5`

**Boundary**: This closes the Task-098 physical Docker GPU dependency and
model-compatibility gate. Task-097/Task-091 retain Podman CPU/GPU and the final
four-profile operational package matrix. Live-provider smoke, branch alert
reconciliation/CI ratchet, and any conditionally approved Slices E/F are not
marked complete.

### 2026-07-24 - GPU Evidence Accepted And Live Alert Baseline Reconciled

**Objective**: Accept the returned sanitized CUDA evidence, reconcile current
GitHub state, and make the Task-098 versus Task-097 runtime boundary explicit.

**Evidence review**: The JSON schema and companion context agree on the exact
qualified commit, selected package versions, CUDA wheel family, device
selection, deterministic model results, trusted hashes, and runtime-resource
fields. The evidence is sufficient for the external Slice D/G CUDA handoff.
Raw logs were not returned, so driver and container-hygiene details remain
sanitized operator attestations in the companion context rather than
independently replayable log evidence.

**GitHub reconciliation**: A read-only authenticated query of open Trivy
code-scanning alerts on `refs/heads/main` returned the unchanged Task-090
baseline: 62 alerts (`4` critical, `16` high, `25` medium, `17` low), alert
numbers `1`, `6-29`, `31-35`, and `41-72`. This proves the baseline has not
drifted on `main`; it does not prove the Task-098 branch result because the
branch has not yet run the pull-request security workflow.

**CI ratchet decision**: Do not activate a blanket critical/high blocking gate
until the Task-098 branch scan is available. The unchanged Fiona/GeoPandas
pins are expected to retain classified high findings. Task-098 grants neither
a blanket ignore nor owner approval for residual critical/high exceptions.
The safe choices are a separately qualified Slice E upgrade or an explicit
time-bounded owner decision with narrow expiring entries. The all-severity
SARIF path remains advisory until that decision is resolved.

**CI evidence phase**: Updated `.github/workflows/ci.yml` to pin both the
Trivy action commit and Trivy `v0.69.3`, restrict these scans to vulnerability
findings, preserve all-severity SARIF generation/upload, record the Trivy and
database versions, add a separate `CRITICAL,HIGH` scan with `exit-code: 1`,
and add a weekly scheduled scan. The new critical/high step remains
`continue-on-error: true` only for the branch-evidence phase described above.
`tests/unit/test_task_098_ci_ratchet.py` prevents loss of the action/binary
pins, SARIF path, separate severity gate, no-blanket-ignore rule, and schedule.

**Runtime boundary**: Task-098 owns dependency compatibility and Docker CPU/GPU
proof for the changed runtime. Task-097/Task-091 own the later operational
Docker/Podman four-profile final-package matrix, avoiding a circular dependency
where Task-097 would otherwise depend on a Task-098 gate that itself required
Task-097.

**Local validation**:

- focused Task-098, configuration, sanitization, and Flask-route contracts:
  PASS, 107 tests
- CI-ratchet plus Task-098 slice contracts: PASS, 37 tests
- CI workflow structural summary: PASS; both Trivy calls use the pinned action
  commit
- agent-work quick validator: PASS
- agent-work full validator: PASS
- sensitive-term scan: zero matches
- `git diff --check`: PASS

**Live-provider boundary**: An isolated current Task-098 CPU container started
on `127.0.0.1:5006` with the existing provider config, models, and ZIP data
mounted read-only and all session/cache/log/temp paths disposable. Startup
confirmed torch `2.6.0+cpu`, both providers configured, assets present, and
release-model hashes enabled. Readiness was intentionally fatal because the
diagnostic mounts made config/model/data unwritable; the production package
uses writable named volumes. No provider request was sent. The maintained
browser smoke was stopped before execution because sending the configured
credential and local AOI fixture to Google/Azure requires explicit external
request authorization. The disposable container was removed; the pre-existing
RC7.1 container remained healthy and unchanged on port 5005.

### 2026-07-24 - Live Google And Azure Provider Gate Passed

**Objective**: Exercise the maintained estimate, detection, list/map rendering,
progress, cancellation, and post-cancel recovery paths against both supported
providers using the Task-098 candidate runtime.

**Authorization and fixture custody**: The project lead explicitly authorized
the configured Google/Azure requests and local AOI use before execution. The
400-byte ignored fixture contains a five-point polygon and expected minimum of
one detection; its SHA-256 is
`EC2F0E45C0484384BA02F685C19578F4E16045EB3D1BD2D696D6F78EF0AE69F9`.
Raw coordinates, provider URLs, response payloads, screenshots, and browser
artifacts remain local and ignored.

**Runtime isolation**: Ran
`towerscout:task098-candidate-torch260-cpu` on `127.0.0.1:5006`. Existing
provider configuration, model assets, ZIP data, and managed-network CA files
were mounted read-only. Session, cache, log, temp, upload, and `/tmp` paths
were disposable tmpfs mounts. The first Google attempt correctly failed TLS
verification because the ad hoc `docker run` omitted the package's
`SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE` environment variables. After applying
the existing non-secret CA path
`/app/webapp/config/certs/towerscout-ca-bundle.pem`, the unchanged candidate
passed both providers. This was a test-launch correction, not a source,
credential, fixture, or trust-bundle change.

**Sanitized results**:

| Run | Estimate | Detection/recovery | Cancel | Result |
| --- | --- | --- | --- | --- |
| Google detect `20260724-161116-google` | 1 tile, HTTP 200, 232 ms | 8 detections; 8 selected/listed; 5 map-visible; 18.690 s | Not requested | PASS |
| Azure detect `20260724-161151-azure` | 1 tile, HTTP 200, 78 ms | 14 detections; 14 selected/listed; 9 map-visible; 19.586 s | Not requested | PASS |
| Google cancel `20260724-161329-google-cancel` | 1 tile, HTTP 200, 66 ms | Recovery rerun: 8 detections; 8 selected/listed; 5 map-visible; 15.116 s | HTTP 200 in 655 ms; 0 detections after cancel | PASS |
| Azure cancel `20260724-161402-azure-cancel` | 1 tile, HTTP 200, 49 ms | Recovery rerun: 14 detections; 14 selected/listed; 9 map-visible; 10.946 s | HTTP 200 in 298 ms; 0 detections after cancel | PASS |

All runs displayed progress and reported zero page errors. The only non-2xx
network item was the existing harmless `GET /favicon.ico` HTTP 404. The
cancel runs recorded the expected client abort message and then completed
their recovery detection successfully.

**Cleanup**: The isolated container was stopped and removed. No Task-098
container remains; the pre-existing RC7.1 container remained healthy and
unchanged on port 5005.

### 2026-07-24 - Conditional Slice E Compatibility Gate Passed

**Objective**: Remove the three residual critical/high Fiona and GeoPandas
findings without changing TowerScout's qualified packaged-ZCTA reader
behavior.

**Selected pair**: Upgraded Fiona from `1.9.6` to `1.10.1` and GeoPandas from
`0.14.3` to `1.1.2`. Because GeoPandas 1.x prefers Pyogrio when available,
`Zipcode_Provider` now selects `engine='fiona'` explicitly. This preserves the
existing I/O backend while adopting the fixed package pair.

**Compatibility evidence**:

- isolated Python 3.12 environment: Fiona `1.10.1`, GeoPandas `1.1.2`,
  pandas `2.3.3`, Shapely `2.0.3`, and PyProj `3.7.2`; `pip check` PASS
- focused runtime and Slice E contracts: PASS, 6 tests
- fresh `--pull --no-cache` Linux/Python 3.11 image:
  `towerscout:task098-slice-e-fiona1101-cpu`, image ID
  `sha256:5dc120a32bc5b606d9653dd6a8fc218e702812d72814985e2e29321d1cc9aae1`
- disposable read-only image validation: `pip check` PASS; the real packaged
  ZCTA shapefile loaded through `Zipcode_Provider` with 33,791 rows, 11
  columns, CRS `EPSG:4269`, and non-empty Polygon geometry
- existing Docker state remained isolated: only the pre-existing RC7.1
  container continued running and healthy on port 5005

**Test-environment note**: A combined 63-test Python 3.12 run reached 57
passes, then six Flask-route cases failed during `tmp_path` setup because the
managed Windows host denied access to pytest's temp directory. The failure
occurred before those test bodies and is not a Slice E application failure;
the same route coverage had already passed before this geospatial-only change.

**GPU evidence boundary**: The accepted CUDA evidence remains bound to commit
`675bd8fabc27765522906957524d2027d931f6a1`. Slice E changes only geospatial
pins, the ZIP-code reader's explicit backend selection, and maintained
contracts; it does not change torch, torchvision, model loading, device
selection, hashes, or inference code. The evidence therefore continues to
qualify the unchanged ML slice, but it is not described as an exact-final-HEAD
GPU image qualification.

**Branch security result**: Draft PR #51 workflow run `30124897804`, security
job `89585967042`, scanned the Slice E commit `09cac7e`. The pinned Trivy
`v0.69.3` `CRITICAL,HIGH` report listed `webapp/requirements.txt` with `0`
vulnerabilities. With the classified residual findings removed, the separate
critical/high gate is now merge-blocking; the all-severity SARIF generation
and upload path remains advisory.

**Blocking-ratchet verification**: Draft PR #51 workflow run `30125209209`
validated ratchet commit `634439f`. Python 3.11, Python 3.12, frontend,
security, standalone Trivy, and both Task-087 Puppeteer jobs passed. The
merge-blocking critical/high step itself concluded `success` and again listed
`webapp/requirements.txt` with `0` vulnerabilities. The Docker build job was
correctly skipped under its existing main-branch-only condition.

### 2026-07-24 - Independent Closeout Audit

**Objective**: Re-review every Task-098 commit and affected runtime, security,
container, frontend, documentation, and task-tracking surface before adding
the newly available Dependabot evidence.

**Result**: This audit found no application regression, unintended ML/runtime
change, stale CUDA 12.1 package reference, source/bundle mismatch, or
credential exposure. The later PR review did identify stale CUDA 12.1 wording
outside the audit's effective search and a Docker-forwarding flaw in the
loopback-peer upload check; both are corrected in the July 27 entry below. The
exact pre-closeout head passed 117 focused Task-098, configuration,
sanitization, Flask-route, and runtime-contract tests under Python 3.12. The
`pip check` result, CI workflow summary, frontend bundle consistency,
agent-work quick/full validation, and `git diff --check` passed. The only
credential-shaped value in the branch diff is an intentionally fake Google
key used by the provider-error redaction test.

**Corrections found and addressed**:

- The runtime documentation still described all SHA-256 verification as
  opt-in. It now distinguishes always-on model verification during readiness
  and immediately before deserialization from optional full-asset hashing of
  the large ZIP-code data.
- Task tracking still described the already-passing branch critical/high gate
  as pending. The active task and backlog now identify project-lead checkout
  and sign-off as the remaining Task-098 gate.
- Trivy had passed while newly published high-severity npm advisories remained
  open. A lockfile remediation and blocking high-severity npm audit were added
  as a complementary frontend gate.

**Docker isolation**: Before the final build, the only running container was
the pre-existing healthy RC7.1 instance
`extracted-cpu-towerscout-1` using
`ghcr.io/j-schulein/towerscout:v0.1.0-rc7.1-cpu` on port 5005. Every Task-098
image had a distinct local-only tag. Final validation uses a new image tag,
container name, and port 5006; it does not stop, replace, retag, mount into, or
otherwise mutate the RC7.1 instance.

### 2026-07-24 - Dependabot Reconciliation And Slice F Qualification

**Dependabot inventory**: The 68 open alerts consist of 62 Python runtime
alerts in `webapp/requirements.txt` and six npm development-only transitive
alerts in `package-lock.json`. All 62 Python advisory IDs duplicate the
Task-090 Trivy inventory, although seven GitHub severity labels differ. The
six npm alerts are complementary findings that the existing Trivy branch gate
did not report.

**Python disposition**:

- The previously qualified Slices B-E resolve 52 of the 62 Python alerts.
- Slice F upgrades Flask `3.0.2` to `3.1.3` and python-dotenv `1.0.0` to
  `1.2.2`, resolving two more alerts. The isolated Python 3.12 environment
  passed `pip check` and 101 focused configuration, error-sanitization,
  Flask-route, runtime, input-boundary, and provider-client tests.
- The eight remaining Python alerts are the already documented,
  non-reachable torch advisories. Their available fixes require a new
  torch/torchvision compatibility and CPU/CUDA qualification cycle, while the
  accepted Task-098 GPU evidence is bound to torch `2.6.0` and torchvision
  `0.21.0`. They remain an explicit residual rather than being silently
  upgraded beyond the qualified ML pair.

**npm disposition**: `npm audit fix --package-lock-only` retained the direct
Puppeteer `24.19.0` pin and upgraded only its transitive development
dependencies: basic-ftp `5.2.0` to `5.3.1`, ip-address `10.1.0` to `10.2.0`,
js-yaml `4.1.1` to `4.3.0`, and ws `8.20.0` to `8.21.1`. This resolves all six
open npm alerts and the three related npm advisories GitHub had already
auto-dismissed. A clean `npm ci` and `npm audit --audit-level=high` reported
zero vulnerabilities; the setup-wizard and ProviderStateManager contracts
passed, and a rebuilt bundle differed only by its generated timestamp.

**CI coverage correction**: The frontend job now runs blocking
`npm audit --audit-level=high` immediately after `npm ci`. This preserves the
existing critical/high merge policy, leaves moderate findings visible but
non-blocking, and prevents Dependabot-only high/critical npm findings from
escaping solely because Trivy's current database did not report them.
Maintained contracts pin the four transitive fixed versions, preserve the
direct Puppeteer pin, and prevent the npm audit step from becoming advisory.

**Final local validation**:

- full Python 3.12 unit suite: PASS, 303 passed and 74 intentional
  legacy/platform skips
- fresh `--pull --no-cache` Linux/Python 3.11 CPU image:
  `towerscout:task098-final-dependabot-slicef-cpu`, image ID
  `sha256:4f9a3741e210ce3ceff6e26b1075b19447a7258b3737e764d1a25f10ec298719`
- image dependency check: PASS; Flask `3.1.3`, python-dotenv `1.2.2`, torch
  `2.6.0+cpu`, torchvision `0.21.0+cpu`, and no broken requirements
- disposable read-only container on `127.0.0.1:5006`: root HTTP 200, one
  session cookie, health `ok`, and readiness HTTP 200 with expected
  `setup_required`/asset `degraded` state because the asset-light smoke
  intentionally supplied no models, ZIP data, or provider credentials
- the disposable container was removed; the pre-existing RC7.1 container
  remained the only running container and stayed healthy on port 5005

---

### 2026-07-27 - PR #51 Review Remediation And Final Local Recheck

**Review findings**: The PR review correctly identified two issues that the
July 24 closeout audit missed:

- Docker Desktop host forwarding presents the request to TowerScout through a
  bridge/proxy address, so `request.remote_addr` cannot reliably prove that a
  model upload originated from the host loopback interface.
- Active documentation and one maintained test fixture still referred to CUDA
  12.1 after the selected package moved to CUDA 12.6.

**Model-upload correction**: The upload feature remains disabled by default.
When an administrator explicitly enables it, TowerScout now fails closed
unless `TOWERSCOUT_MODEL_UPLOAD_KEY` contains a 32-512 character secret. The
browser asks for that key in a masked dialog and sends it only in the
`X-TowerScout-Model-Upload-Key` request header. The backend uses a constant-time
comparison, preserves the existing rate limit, and still requires the uploaded
file's SHA-256 digest to appear in `TOWERSCOUT_TRUSTED_MODEL_SHA256` before
installation. Missing or incorrect keys return HTTP 403; an enabled feature
without a valid configured key returns HTTP 503. Logging and structured-error
sanitizers redact both the header and environment-variable forms.

Compose, both environment templates, and the Windows Compose launcher now
carry the disabled-by-default switch, blank key, and blank trusted-hash
allowlist. No real credential is stored in the repository. The generated
frontend bundle was rebuilt from its source and the maintained source/bundle
contract passes.

**Docker Desktop topology evidence**: A fresh `--pull --no-cache` CPU build
produced `towerscout:task098-pr51-model-upload-key-cpu`, image ID
`sha256:d7b2de637b5a2d24f086a0412e6dfd16456a271101a7a7d70316c6a4a899bfc7`.
A disposable instance published only `127.0.0.1:5006`. Host-side probes
returned HTTP 403 for a missing key, HTTP 403 for an incorrect key, and HTTP
200 for the temporary correct key plus an approved dummy-file digest; the
installed dummy model then appeared in `/getengines`.

Docker Desktop also allowed a sibling local container to reach the host proxy
through `host.docker.internal`, even though the published binding was
loopback-only. Its upload attempt without the key returned HTTP 403. The
result sharpens the boundary: loopback publication prevents access from other
physical devices by default, while the Model Upload Key protects the endpoint
from other locally controlled containers on the same Docker Desktop host.

**CUDA correction**: All seven active Markdown references were changed from
CUDA 12.1 to the selected CUDA 12.6 wheel family, and the stale Task-075
fixture was corrected. A maintained multiline repository scan now fails if
CUDA 12.1 reappears in active runtime, script, documentation, or test surfaces.
Historical `.agent_work` evidence is intentionally excluded from that
current-runtime assertion.

**Validation**:

- disposable Linux/Python 3.11 full unit suite: PASS, 260 passed and 121
  intentional skips
- focused Python 3.12 review-remediation suite: PASS, 24 tests
- frontend source and bundle syntax: PASS
- frontend global, debug-logging, and ProviderStateManager contracts: PASS
- bundle guard: PASS; source and generated bundle both changed while module
  ordering remained intact
- Windows full-suite attempts were blocked only by the existing pytest
  temporary-directory ACL problem; the authoritative read-only Docker run
  completed the full suite
- `npm.cmd run test:stage-0` could not enter WSL because the repository path
  returned `E_ACCESSDENIED`; the directly affected JavaScript contracts above
  passed independently
- every disposable validation container was removed; the pre-existing
  `v0.1.0-rc7.1-cpu` container remained healthy and unchanged on port 5005

**Documentation follow-up**: Detailed operator guidance is assigned to
Task-092 and DOC-001. It must explain secure key generation, private storage,
rotation, enable/disable behavior, approved-hash onboarding for a new model,
normal-user impact, and troubleshooting without exposing a real key.
Task-098 closes with its security-specific documentation current; the
candidate release-note and administrator-instruction work remains a distinct
Task-092 final-documentation gate.

**Post-push CI correction**: PR #51 run `30278197559` passed the main
frontend, Python 3.11, Python 3.12, security, and Trivy jobs, but both Task-087
Puppeteer jobs failed before test execution. Their shared workflow selected
Node 18 and dynamically installed `playwright@latest`; the resolved Playwright
`1.62.0` requires Node 20 or newer. This is external toolchain drift in a
previously identified unpinned fallback, not a model-upload or application
regression. Both jobs now use supported Node 22 and exact Playwright `1.62.0`.
A maintained CI contract prevents either Node 18 or `playwright@latest` from
returning. The focused six-test contract, YAML parse, pinned CLI resolution
under local Node 24, both template-mode Puppeteer checks, the simulated-helper
POST/poll Puppeteer check, ProviderStateManager contract, agent-work
validators, CI workflow summary, and `git diff --check` pass. The browser tests
used installed headless Edge plus temporary local static/helper processes that
were removed immediately afterward. The new exact-head GitHub rerun remains
the authoritative Node 22 browser-install and job-execution proof.

---

### 2026-07-27 - Merge, Dependabot Reconciliation, And Task Sign-Off

**Objective**: Close Task-098 only after the reviewed implementation lands on
`main`, the post-merge workflow passes, and GitHub's dependency graph reports
the intended residual-alert state.

**Context**: The project lead confirmed the PR was ready, squash-merged PR #51,
deleted its remote branch, and refreshed Dependabot after the first
post-merge graph still contained both retired and replacement dependency
versions.

**Decision**: Treat the refreshed eight-alert torch inventory as the
authoritative residual. Preserve those alerts as visible, evidence-backed
future ML work; do not dismiss them or merge an uncoordinated standalone torch
upgrade.

**Execution**:

- PR #51 was squash-merged as commit
  `e499b50d285b775047fb6efadcec512f7753c859`.
- Main workflow run `30284846056` completed successfully: frontend, Python
  3.11, Python 3.12, security, and Docker image-build jobs all passed.
- The refreshed Dependabot inventory contains exactly alerts `17`, `18`, `44`,
  `45`, `46`, `47`, `48`, and `58`, all for torch: three medium and five low,
  with no open critical or high alert.
- Dependabot PR #60 was closed rather than merged because it changed torch to
  2.13.0 while leaving torchvision 0.21.0, which requires torch 2.6.0. Its
  disposition requires a future compatible pair and a repeated CPU/CUDA,
  trusted-model, output-parity, and performance qualification cycle.

**Output**: Task-098's release-blocking security gate is closed. No alert was
manually dismissed, the frozen `v0.1.2` release and `cdcai/TowerScout` remain
unchanged, and Task-087 is ready to resume after this documentation-only
closeout merges.

**Validation**: Live GitHub PR, Actions, and Dependabot API state were checked
after the refresh. The repository-native hygiene validators and Markdown link
checks are rerun on this closeout branch below.

**Next**: Merge this documentation-only closeout, then resume Task-087 from
current `main`.

---

## Validation Results

**Execution Status**: PASS / COMPLETED; PR #51 MERGED, MAIN CI PASSED,
DEPENDABOT RECONCILED, AND PROJECT-LEAD SIGN-OFF RECORDED

**Closeout Confidence**: The alert inventory, reachability decisions, selected
versions, regression obligations, CPU/GPU evidence boundaries, live-provider
results, npm complement, and blocking CI gates are traceable and internally
consistent. The eight residual torch advisories are explicitly documented as
non-reachable and remain tied to a future coordinated ML compatibility cycle,
not an unreviewed Task-098 omission.

**Documentation Validation**:

- `check_agent_work_quick.py`: PASS
- `.agent_work/scripts/validate_agent_work.py`: PASS
- Local Markdown links across Task-098 and its governing tracking sources:
  PASS
- `git diff --check`: PASS

**Current Baseline Review**:

- Python 3.12 affected-surface tests: 152 passed.
- Legacy validation and image-processing modules: 46 skipped by explicit
  repository-level markers; Task-098 must add maintained focused replacements
  for touched paths rather than count these skips as coverage.
- Setup Wizard validation contract: PASS.
- ProviderStateManager regression contract: PASS; its forced Azure failure
  messages are expected negative-path output and the command exited zero.
- Current CI reality: unit tests block; the broad integration job, container
  image build, and Trivy SARIF path are advisory; live Google/Azure browser
  smoke and four-profile package validation are external runtime gates.
- Branch security reconciliation and both blocking critical/high dependency
  gates are implemented. Final Docker/Podman CPU/GPU operational
  qualification remains assigned to Task-097/Task-091.

**Docker CPU Python 3.11 Baseline**:

- Fresh `--pull --no-cache` CPU image: PASS.
- Dependency resolution and `pip check`: PASS.
- Unit suite: PASS, 212 passed and 121 Linux/platform-feature skips.
- Broad integration: BASELINE DRIFT, 20 passed, 2 skipped, and the same 4
  pre-change geocoding failures seen on Python 3.12.
- ML-focused gate: PASS, 8 passed.
- Deterministic YOLO/EfficientNet output parity: PASS.
- Existing Docker state isolation: PASS; no pre-existing image, container,
  port, volume, or build-cache layer influenced the run.

Task-098 has changed only the approved Slice A runtime/input boundaries,
Slice B Pillow/Waitress pins, Slice C aiohttp pin, Slice D/G ML runtime pins
and safety boundaries, qualified Slice E geospatial pins/backend selection,
qualified Slice F Flask/python-dotenv pins, npm transitive lockfile fixes, the
CI security ratchet, corrected model-hash documentation, and maintained
regression/evidence records. No release asset, repository security setting, or
external repository was changed. GitHub's post-merge refresh marked the
remediation-covered Dependabot alerts fixed without any manual dismissal and
left the eight documented torch residuals open.

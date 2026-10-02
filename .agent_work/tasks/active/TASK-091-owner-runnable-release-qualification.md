# TASK-091: Owner-Runnable Release Qualification

**Status**: AT_RISK - local `rc4` CPU/CUDA W05, four-profile W09, and first-
host provider/cancel/error/review-export/relaunch/reboot cells pass. ADR-023
resolves policy/signing through an unsigned, narrower support boundary.
The preliminary `rc4` browser-download Docker CPU diagnostic passed and its
findings are dispositioned for Task-092; final documentation-aligned artifacts,
exact browser-download, and independent-host evidence remain
**Priority**: CRITICAL
**Type**: C (Release Qualification / Handoff)
**Owner**: Release owner; active agent executes bounded preparation and checks

## Objective

Produce a downloadable, owner-reproducible Windows 11 release qualification
record bound to exact source, CPU/CUDA images, control/asset ZIPs, fixtures,
and tools.

## Requirements

- WHEN a package is qualified, THE PROJECT SHALL prove actual YOLO and
  EfficientNet execution on the required device rather than infer it from
  readiness labels or mocked tests.
- WHEN the full release is claimed, THE PROJECT SHALL reproduce Docker CPU,
  Docker NVIDIA, Podman CPU, and Podman NVIDIA on independent suitable Windows
  computers.
- IF a required artifact, machine, account, policy decision, or test is
  unavailable, THEN THE PROJECT SHALL record the cell as blocked or not run.

## Current Work Packages

- W01: artifact/prerequisite inventory and early real-package installation.
- W05: truthful external combined-model qualification.
- W09: immutable candidate/package inventory and Windows checks.
- W10: four-profile independent reproduction and handoff.

## Acceptance Boundary

- Ordinary-account extraction includes a path with spaces.
- Setup imports the verified asset ZIP and uses pinned image digests.
- Google and Azure detection, review/export, cancellation/error recovery,
  next-request success, stop/relaunch, and reboot persistence are observed.
- CPU fallback does not pass a required-CUDA run.
- Evidence contains sanitized summaries and private raw-evidence references.
- A preliminary browser-download run against a superseded candidate may inform
  later work but does not satisfy final acceptance for different ZIP/image
  bytes.

## Implementation Log

### 2026-09-22 - Activation

Selected from the existing backlog under ADR-021. The accepted source is
`9276084d91807906c53e00060670692b27e38483`. Baseline artifact, runtime,
asset, fixture, account, signing/policy, and independent-host availability are
being inventoried before any readiness claim.

### 2026-09-22 - W01 First-Host Baseline Attempt

**Host**: `FIRST-HOST-LOCAL`; Windows 11 Enterprise build 26200; 31.5 GiB RAM;
266.4 GiB free; Windows PowerShell 5.1; NVIDIA RTX PRO 500 Blackwell Laptop GPU
(driver 596.71, 6113 MiB). Docker Desktop 29.7.2 and Podman 6.0.2 were running.

**Artifacts/prerequisites**:

- Accepted source: `9276084d91807906c53e00060670692b27e38483`.
- No accepted-main CPU/CUDA candidate image or control ZIP existed locally.
- Historical asset ZIP was present for internal reuse review:
  `towerscout-v0.1.2-assets-towerscout-v1-assets-2026-05-05.zip`, 800655295
  bytes, SHA-256
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`;
  its sidecar matched.
- No July qualification fixture directories were found at the assessed local
  paths. Fixture provenance/permission and positive EN coverage remain blocked.
- Podman's active Compose path delegated to Docker Desktop Compose v5.3.1;
  no standalone approved `podman-compose` command was found. Podman acceptance
  is blocked until an approved provider/target is installed and selected.
- Effective execution policy was `Restricted`; package PowerShell scripts were
  unsigned and CMD wrappers use process-level bypass. This host can support a
  permissive diagnostic run but cannot establish managed-endpoint policy or
  signing compatibility.
- Independent CPU/GPU hosts and approved Google/Azure accounts were not
  confirmed in this session.

**Attempt**: Started a real CPU image build tagged
`towerscout:main-9276084-cpu` with torch 2.6.0 / torchvision 0.21.0 and exact
source/release labels. Frontend install/build passed (27 packages, zero audit
findings, 30-module bundle). The Debian/GDAL layer then required 236 packages
(181 MB) and sustained very slow downloads; the bounded attempt was stopped
after roughly four minutes before image creation. No container, volume, ZIP,
or package install was created, and no inference was run.

**Forecast**: `at_risk`. Next action is to retry the cached CPU build on an
approved faster network or obtain an existing accepted-main CPU image, then
create a local-validation real ZIP and immediately run ordinary-account setup
from a spaced path with the verified asset ZIP. A digest-pinned published image
and clean-source ZIP are still required for release evidence.

### 2026-09-22 - W01 CPU Build Retry

Retried the same accepted-main CPU build after a short Docker network probe.
The Debian/GDAL layer resolved and installed successfully, but its 236 packages
and 181 MB download took 22 minutes 49 seconds at an average 132 kB/s. Several
individual requests paused for tens of seconds before apt recovered. In
contrast, pip downloaded the 178.7 MB CPU-only PyTorch wheel at about 15 MB/s,
and the complete Python dependency layer finished in 70 seconds. The observed
problem is therefore an oversized uncached Debian dependency layer amplified by
intermittent Docker proxy/mirror request latency, not a demonstrated CPU,
PyTorch-version, memory, disk, or dependency-resolution failure.

The build completed with exit 0 and created
`towerscout:main-9276084-cpu`, image ID/digest
`sha256:522541a6902381e16559e111cc3cab898bf109f99f97ea73a703239941301687`,
size 855191426 bytes. Labels report source
`9276084d91807906c53e00060670692b27e38483`, version
`main-baseline-20260922`, and flavor `cpu`. A no-data import/device smoke passed
for torch, torchvision, Fiona, GeoPandas, and OpenCV; torch reported
`2.6.0+cpu`, no CUDA build, and `cuda_available=False` as expected.

**Forecast remains**: `at_risk`. This proves image construction and basic CPU
runtime imports only. It does not prove control-ZIP installation, asset import,
application readiness, provider operation, model loading, or real YOLO and
EfficientNet inference. Next action is ordinary-account package installation
from a path containing spaces with the verified asset ZIP, followed by real CPU
inference. A bounded image-size/build-time experiment may remove or isolate
`libgdal-dev` only if geospatial runtime tests prove the wheel-based stack is
sufficient.

### 2026-09-22 - W01 Real Package And W02 Blocker Proof

Built a real local-validation CPU control ZIP from clean accepted source
`9276084d...` and image `towerscout:main-9276084-cpu`. The control ZIP SHA-256
was `ffa270727a090ad749128050605d819349ee1d3ffd885f60e6b9114ee3a7fe63`;
its adjacent sidecar matched, all 71 internal package checksums passed, and the
Windows package/manifest regression ring passed `7/7`. The manifest correctly
recorded a mutable local image, CPU flavor, the accepted source ref, and the
published v0.1.2 asset bundle SHA-256
`00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.

Extracted the exact ZIP under an ordinary user-writable Local AppData path
containing spaces. Setup verified both ZIP sidecars, staged the asset ZIP,
imported every manifest asset with hash verification, and reached
`post_import_health=ok`, but normal launch then failed because endpoint
antivirus blocked parsing the disabled `TowerScoutHostHelper.ps1` module. No
volume was deleted; the exact test project retained all eight named volumes.
This evidence selected Task-068 and W02 rather than weakening endpoint policy.

The bounded Task-068 fix at `08674db` gates helper import, profile persistence,
review-session initialization, and stop cleanup on explicit review enablement.
The changed-boundary Windows tests pass `2/2`, adjacent launcher/package tests
pass `9/9`, the blocking Flake8 profile passes, and editor/parser/diff checks
are clean. The broader legacy helper suite remains unexecutable on this host
because antivirus blocks the helper module itself; the explicitly enabled
review path therefore still requires independent CI/review evidence.

Built a separate dirty-source/mutable-image W02 probe ZIP, clearly unsuitable
for release, with SHA-256
`e5979d79482ea9a546b0bfe4d0b5ac6f5874f7e713dc21ac5751838cb864208a`.
Its packaged launch/stop scripts matched the tested sources byte-for-byte and
all 71 internal checksums passed. Normal Docker CPU setup then passed from a
new spaced path: verified asset import, eight named volumes, healthy container,
`setup_required`, `asset_status=ok`, torch `2.6.0+cpu`, CPU selection, packaged
stop, volume-preserving relaunch, and exact local image identity all passed.

The existing external Task-098 probe ran against that exact package image and
imported volumes. Its sanitized private report at
`%LOCALAPPDATA%\TowerScout Day1\evidence\w02-cpu-probe\qualification.json`
records `passed=true`, trusted YOLO and EfficientNet model hashes, both models
on CPU, torch/torchvision `2.6.0/0.21.0`, three YOLO runs, and three
EfficientNet runs with matching declared output tolerance. This is real
standalone model execution, not the required combined detector-secondary flow.

**Forecast remains**: `at_risk`. Docker CPU package mechanics, asset import,
standalone model execution, stop/relaunch, and persistence are now proven on
the first host. W01 still lacks a permitted fixed fixture with positive
combined-flow EfficientNet candidates/batches, approved provider-account live
workflows, CUDA and standalone-Podman artifacts, managed-endpoint signing
evidence, and independent hosts. Task-068 review/CI is also pending.

### 2026-09-22 - CUDA Assembly And Host Compatibility Boundary

The first clean accepted-main CUDA 12.6 build failed TLS verification when the
PyTorch dependency graph redirected to `pypi.nvidia.com`. TLS verification was
not disabled. The existing reviewed BuildKit-secret CA pattern was ported as
the bounded Task-091 commit `355ca4c`; it supplies `PIP_CERT` only for the pip
layer and copies no certificate into the image. Focused dependency/container
tests passed `14/14`, plus blocking Flake8, PowerShell parsing, Dockerfile
`--check`, and diff validation. PR #76 owns review and CI.

A private Windows trust bundle was built from public trusted root/intermediate
stores and retained under private Local AppData custody. Only its sanitized
identity is recorded: 104 deduplicated certificates, 195,990 bytes, SHA-256
`851e28ba743d1dd39fb3bacea5d3a64ccebc7cae844228c75daf19a6c692053d`.
Inside the Python base image it verified both PyTorch and NVIDIA package hosts
with HTTP 200. No certificate identity or content was committed.

The managed build produced image
`towerscout:task091-355ca4c-cuda126`, ID
`sha256:52bcbd32f58cfbdee29884cfd63c166c29203280176ed41ce8060419d24ff112`,
source `355ca4c...`, flavor `cuda126`, and no persisted CA path/secret marker.
Its local-validation control ZIP SHA-256 is
`293544c5235ed18a1a83b5b605a48c4317b7adae432edbc4842ee9c06a5e998b`;
the sidecar and all 71 internal checksums passed.

The explicit CUDA tensor probe failed closed on this workstation. The selected
torch `2.6.0+cu126` wheel reports kernels through `sm_90`; the RTX PRO 500
Blackwell GPU is `sm_120`, so CUDA raised `no kernel image is available`.
There was no CPU fallback. The image/package are ready for transfer to a
compatible NVIDIA host, but this host does not qualify the selected GPU profile.

### 2026-09-22 - Podman Provider And Target Inventory

Podman client/server `6.0.2` is present. The running default connection is the
rootful socket for `podman-machine-default`; the existing
`towerscout-task087-rootless` machine and rootless connection are stopped.
No container or volume was created for the Day-1 Podman project.

The package-local approved provider installer exposed an interpreter boundary:
system Python `3.14.7` passed the current `>=3.9` preflight but could not resolve
pinned `PyYAML==6.0.2`. Retrying with the approved repository Python `3.12.10`
verified the provider wheel SHA-256, installed pinned dependencies, wrote only
the package-local provider setting, and passed the catalog allowlist. The
wrapper reports `podman-compose 1.5.0` and Podman `6.0.2`. The allowlist check
used the shipped process-scoped PowerShell boundary because workstation policy
is `Restricted`; that result is diagnostic, not managed-endpoint policy proof.

### Day-1 Forecast

**Status**: `AT_RISK`.

| Blocker | Owner | Next check |
| --- | --- | --- |
| Positive combined-flow fixture and custody | Release/model owner | Provide a permitted fixed fixture that yields real candidates in the EN confidence band; hash it before W05 execution. |
| Approved Google/Azure accounts | Provider-account owner | Confirm accounts and enter keys directly through the package Setup Wizard; never send keys through task evidence or chat. |
| Compatible selected-profile NVIDIA host | Test owner | Run the exact CUDA image/ZIP on a supported pre-Blackwell or otherwise wheel-compatible NVIDIA host with no CPU fallback. |
| Rootless standalone Podman runtime | Workstation/test owner | Start the existing rootless validation machine and select its rootless connection; do not use the current rootful default as acceptance. |
| Podman Python support wording | Task-097 implementer | Reproduce and bound the supported interpreter range; current evidence passes 3.12 and fails 3.14. |
| Managed endpoint/signing decision | Endpoint/release owner | Historical Day-1 blocker; resolved on 2026-10-01 by ADR-023's unsigned, narrower support boundary. |
| Independent CPU/GPU hosts | Test owner | Reserve and inventory the required host allocation before W09 distribution. |
| PR #75/#76 acceptance | Reviewer | Complete exact-head CI/review before using either correction in a clean candidate. |

**Next**: Await or schedule the external inputs above while continuing safe W05
report-contract work and review/CI reconciliation. Do not begin a dependency
migration to make this Blackwell host pass.

### 2026-09-22 - Review And W05 Contract Checkpoint

PR #74 at governance head `f2cd068`, PR #75 at dormant-helper head `fa5ce83`,
and PR #76 at managed-build-CA head `355ca4c` all pass required CI/CD,
Windows host-helper, Task-087 controller, security, Docker frontend, and Trivy
checks. PR #76's first Windows helper run had one unchanged long-lived helper
readiness timeout; rerunning only the failed jobs passed without a code change.
No PR was merged.

The W05 combined-flow contract is checkpointed locally, not pushed, at
`be50246` on `feature/task-091-combined-fixture-probe`. It adds optional
manifest-driven production execution through `YOLOv5_Detector.detect` with a
real `EN_Classifier`, `ExitEvents`, and `PerformanceMetrics`, while retaining
legacy no-argument Task-098 behavior and skipping the extra startup subprocess
in combined mode. The fail-closed contract binds manifest-relative fixture
bytes by SHA-256 before and after inference, supports declared zero-detection
tiles, compares normalized outputs within declared tolerances, and requires
positive secondary candidates/batches, matching devices, and production phase
timings. Independent review findings were resolved. Contract and adjacent tests
pass `30/30`; final expanded validation passes `30/30` plus compilation,
blocking Flake8, diff checks, and editor diagnostics.

This checkpoint does not establish W05 runtime acceptance. Real execution is
blocked until the release/model owner provides a permitted, hashable fixture
set with positive detections in the EfficientNet confidence band and declares
expected outputs/tolerances before candidate results.

### 2026-09-23 - Day-2 Focused Corrections And Review Gates

**Objective**: Implement only the W03-W08 defects required by observed Day-1
evidence and prepare the Day-3 rehearsal without weakening acceptance.

**Execution**:

- PR #77 binds bounded runtime commands to the verified rootless Podman
  connection and approved package-local Compose provider.
- PR #78 propagates required secondary-classifier failures and prevents partial
  result publication; its local adjacent ring has zero failures.
- PR #79 creates the viewport boundary before reading first-use Google bounds,
  preserves Azure/explicit polygon behavior, and rebuilds the frontend bundle.
- PR #80 isolates operation-specific rate limits, serializes detection jobs,
  and closes the progress-before-cancel-event race.
- PR #81 preserves the scalar TLS importer exit status and visible diagnostics.
  Full candidate-bundle transaction work is deferred until PR #77 lands.
- PR #82 rejects excessive candidate grids and decoded-image dimensions before
  expensive allocation or model work.
- Draft PR #83 contains the rebased W05 combined-model fixture/report contract.

**Validation**: Local focused and adjacent results are PR #77 `63/63`, PR #78
`60` collected with `22` passed and `38` documented legacy skips, PR #79 all
five maintained frontend/bundle checks passed, PR #80 `96/96`, PR #81 `18/18`,
PR #82 `140` collected with `102` passed and `38` documented legacy skips, and
PR #83 focused `18/18`. PR #77's initial CI helper-sandbox failure was repaired
at `a4bf6e1`; its corrected Windows/helper/controller/frontend/Docker/security
checks pass and its Python matrix was still running when recorded. PR #78's
sole initial Docker-stage failure was a Docker Hub OAuth connection reset; the
unchanged rerun passed, and PRs #78-#83 are fully green. PR #84 records this
governance checkpoint and remains subject to its own exact-head checks.

**Blockers**: The authorized positive combined-flow fixture is not present;
CUDA qualification has no compatible host; managed-endpoint policy and
independent hosts remain unconfirmed. Google and Azure accounts are available,
but no keys or live-provider evidence were placed in repository records.

**Next**: Accept and merge the focused PRs after exact-head CI/review, rebase the
W05 draft on PR #77, add the exact-package runner, obtain and predeclare the
private fixture baseline, then run the Day-3 Docker/rootless-Podman rehearsal.

### 2026-09-24 - Focused Corrections Accepted And W05 Harness Landed

**Decision**: Accept the bounded W03-W08 corrections and the fail-closed W05
qualification harness without treating harness availability as runtime
acceptance.

**Execution**: PRs #77-#83 squash-merged to `main` as `99858c2`, `f51d401`,
`7160866`, `1b7336a`, `be1d74c`, `6046283`, and `3e7f78c`, respectively. Their
ordinary task branches and clean worktrees were retired after merge.

**Validation**: Every PR passed its exact-head GitHub matrix before merge.
Targeted local review additionally covered Windows runtime parsing, TLS status
propagation, ML failure/allocation behavior, 103 detection-admission Python
regressions, frontend/provider-state and bundle-source parity, and 66 W05
contract/adjacent ML tests. The W05 report contract verifies fixture hashes
before and after inference and fails closed on missing output, device, phase,
or secondary-classifier evidence.

**Boundary**: No real combined-model acceptance run occurred. The authorized
positive fixture, exact-package Docker/rootless-Podman runs, compatible CUDA
host, live-provider checks, managed-endpoint policy proof, and independent-host
reproduction remain release blockers or not-run gates.

**Next**: Obtain and predeclare the private fixture baseline, add the
exact-package invocation, and run the Day-3 Docker/rootless-Podman rehearsal
without weakening the W09/W10 identity and host requirements.

### 2026-09-24 - Task-103 Track L Unlock And Phase-2 Integration

Task-103 Track L passed on the Blackwell laptop with torch 2.10.0/cu128: both
models executed on `cuda:0`, output tolerances passed, the `sm_120` kernel
probe passed, and the explicit CPU profile of the same CUDA image passed. The
owner acknowledged Checkpoint 1 and authorized Phase 2, the feature-branch
push, and PR creation. ADR-022 now amends only the ML runtime baseline; this
task's package, provider, persistence, recovery, and independent-host gates
remain unchanged. The merged PR #83 combined-flow runner is the sole current
ML acceptance contract; the historical external HTTP detection harness is
retired for this purpose. Publication still waits for Task-103 Checkpoint 2.

### 2026-09-29 - Task-103 `rc3` W05 And Live-Provider Reconciliation

The exact replacement `rc3` CPU digest
`sha256:a84201cec5704e35e0e7e5e05ca96aebeebb976ddeb89c88ac3145776bc1ba88`
and CUDA digest
`sha256:6c54725b63cc8b66c996bc6d32d3e6714aada5fb51d07d840b7895dc70041fe5`
each passed all six W05 phases. Gates v3 passed every applicable absolute gate;
the CUDA combined phase observed both YOLO and EfficientNet on `cuda:0`, and
the CPU phase observed both on CPU. Exact run/verdict hashes and host-neutral
timestamped custody identifiers are recorded in the Task-103 W09 evidence
index.

The fresh Docker CPU package also passed managed-TLS repair, Google and Azure
normal detections, and Google cancel-then-next recovery without retaining
credential values, provider URLs, payloads, screenshots, or AOI coordinates.
The remaining release blockers are the other three profiles' provider/
recovery/review-export workflows, controlled-error checks in every profile,
Docker CPU review/export, managed-endpoint policy/signing, and independent-host
repetition. Package publication and `latest` promotion remain owner-gated.

### 2026-09-29 - First-host reboot persistence

Windows boot time established a real reboot boundary. Docker automatically
restored both exact-digest profiles; the retained rootless Podman machine was
running, while its two retained package containers required the documented
manual start. All four profiles returned healthy on loopback ports `5221`-
`5224`, retained exactly eight named volumes each, selected the required CPU or
CUDA device, and reported the expected immutable digest. Both CUDA profiles
then completed a real torch 2.10.0+cu128 `sm_120` kernel.

The configured Docker CPU profile retained both provider-configured flags,
default Google selection, assets, the repaired CA bundle, both CA environment
bindings, and enabled TLS verification. Keyless Google and Azure probes both
returned `tls_ok`. Sanitized post-reboot Google and Azure detections passed
with evidence hashes recorded in the W10 index. No credential value, provider
URL, request payload, response body, screenshot, AOI coordinate, local path,
or hostname is retained.

This closes the first-host reboot persistence subset only. It does not convert
the unconfigured Docker CUDA or Podman profiles' provider workflows into
passes, and it does not satisfy review/export, controlled-error, managed-
endpoint, or independent-host acceptance.

### 2026-09-30 - Final local `rc4` four-profile workflow matrix

The final local packages bind source
`541622556fb7999ee4e88fb1e44f7797b9da34f5`, CPU digest
`sha256:a3eeb77152577f3656a286777bd4c4312cecc311cb5a5cc1b132b459f1ecd18f`,
and CUDA digest
`sha256:61dab3b83e1be8e2cf955d9d7d2d9b997a207a4dcb76b20344a268a5690f654a`.
Docker CPU/CUDA and rootless Podman CPU/CUDA all passed live Google and Azure
detection, cancellation followed by an immediate successful request, a
controlled HTTP 400 validation error followed by HTTP 200 success, review,
result export, dataset ZIP export, and volume-preserving stop/relaunch. Both
CUDA profiles completed a real finite `sm_120` kernel after relaunch. All four
profiles simultaneously reported `ready`, exact digest, required device,
assets/config `ok`, both providers configured, and eight retained mounts.

Provider values, provider URLs, payloads, response bodies, screenshots, AOI
coordinates, certificate identities, local paths, and hostnames were not
retained. The Task-103 W09/W10 indexes contain the sanitized matrix and exact
artifact/tool hashes.

The exact `rc4` reboot now passes across all four profiles. Docker restored
automatically; retained Podman containers required the documented manual
start. Every profile then reported the exact digest, required device,
assets/config `ok`, both providers configured, eight mounts, and successful
Google/Azure detection plus controlled-error recovery and dataset ZIP export.
Both CUDA profiles completed finite `sm_120` kernels. That evidence predates
ADR-023 and remains valid local runtime evidence, but the documentation change
requires new documentation-aligned image and control-ZIP identities before
distribution because the image serves the repository `docs/`. ADR-023
resolves managed-policy/signing by limiting the standard support claim to
users/sites that permit the supplied unsigned wrapper path; it does not claim a
pass for signature-enforcing managed endpoints. Browser-download and
independent-host repetition remain open, and publication remains owner-gated.

### 2026-10-01 - Unsigned Windows package support decision

ADR-023 records the owner-approved path: ship unsigned PowerShell scripts,
retain the supported `.cmd`/`.bat` process-scoped wrapper entrypoints, and do
not claim compatibility with endpoints requiring a trusted Authenticode
publisher or organization-specific allowlisting. Final acceptance must compare
the exact control/asset ZIPs with SHA-256 values displayed in the authoritative
release record before extraction, then run the browser-downloaded package as an
ordinary user without weakening persistent policy or endpoint protection.

This closes the Day-1 policy decision by scope. It does not close independent-
host acceptance. The documentation edits are package and OCI-image bytes, so
the `rc4` artifacts remain historical local evidence and newly identified
documentation-aligned images/control packages must pass the affected W09/W10
checks before tester distribution.

### 2026-10-01 - Planned `rc4` browser-download shakedown before Task-092 implementation

The owner selected a bounded preliminary use of the preserved `rc4` CPU/CUDA
artifacts before the documentation/Wiki rewrite. The purpose is to find
download-marker, ordinary-user extraction, wrapper/policy, endpoint-protection,
prerequisite, setup, asset, and runtime issues that are likely to persist into
the next candidate. Use a supplemental ADR-023-safe procedure because the
packaged `rc4` manuals predate that decision. Label the result diagnostic, not
final acceptance, and do not publish or mutate external assets without owner
authorization.

Task-092 will consume applicable findings before its documentation freeze.
Final proof still requires the exact browser-downloaded documentation-aligned
ZIPs and images. `Dockerfile` copies `docs/` into the OCI image and the app
serves them through `/docs/`, so removing in-app/package drift requires new
image and control-package identities even when functional runtime code remains
unchanged.

### 2026-10-02 - `rc4` browser-download Docker CPU diagnostic

The owner downloaded all six assets from the authenticated GitHub draft release
through the normal browser flow. GitHub digests, downloaded ZIP hashes,
sidecars, and frozen originals agreed, and Windows download markers were
present. File Explorer extraction to a user-writable path containing spaces and
the supplied ordinary-user process-scoped wrapper both worked without changing
persistent execution policy or endpoint-protection settings.

Fresh Docker CPU setup verified/imported the exact downloaded CPU and asset
ZIPs, created eight named volumes, matched the pinned CPU image digest, and
bound only to loopback. After private Azure configuration, a sanitized browser
run passed estimate, controlled HTTP 400 then HTTP 200 recovery, 14-detection
review/navigation, and valid nonempty dataset export. Package stop/relaunch
retained Azure configuration, assets, digest, CPU selection, and all eight
volumes. In-app Help returned HTTP 200.

No larger blocker was found in this bounded subset. The run is diagnostic, not
final acceptance: it did not repeat CUDA, Podman, Google, cancellation, reboot,
managed-signing-policy, public unauthenticated download, or independent-host
cells. The draft remains non-public. Full evidence and Task-092 dispositions
are in
[the rc4 diagnostic record](./TASK-092/RC4-BROWSER-DOWNLOAD-DIAGNOSTIC-2026-10-02.md).

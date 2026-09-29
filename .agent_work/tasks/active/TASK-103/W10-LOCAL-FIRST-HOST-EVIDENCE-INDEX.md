# Task-103 W10 Local First-Host Evidence Index

**Recorded**: 2026-09-28
**Host ID**: `FIRST-HOST-LOCAL`
**Scope**: Same-machine first-host rehearsal only; this is not the independent
host required for full W10 acceptance.
**Verdict**: `FAIL` for the frozen candidate because cancellation did not
recover to a successful next request without relaunch. The qualified subset is
recorded below.
**Publication state**: No package was published and no `latest` tag was
promoted.

## Frozen Inputs

- CPU control ZIP SHA-256:
  `02f191eade141ad06251f2611892fe12064eb84601ebd39010aedf8115d98c79`
- Shared asset ZIP SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`
- CPU image digest:
  `sha256:4d673a8ca0b3c221899062769f28adc8825e96af7413573ab31ba62d198b6a0a`
- Sanitized local smoke tool SHA-256:
  `815ef4266f10cf610e54304b22b1a014d7342dd4f8fd62e6b54e35eb5cc866ea`
- Safe committed fixture SHA-256:
  `fd6771ed3aa30a44c5bedb7575ed7f164896e496292fae29ac1da4bb9638d715`

The smoke tool recorded provider names, status codes, timings, counts, and
boolean UI state only. It did not retain provider URLs, request bodies,
screenshots, console text, response bodies, credentials, local Windows paths,
or machine hostnames.

## Docker CPU Fresh Install

The exact CPU ZIP was extracted under the spaced-path placeholder
`<W10-STAGING>/Docker CPU Fresh`. The shipped setup command used Docker,
`-Gpu off`, port `5211`, the exact control ZIP, and the exact asset ZIP.

- Outer package and asset sidecars: `PASS`.
- Release manifest and staged asset manifest/hash verification: `PASS`.
- Eight fresh named volumes: `PASS`; retained throughout testing.
- Readiness: `ready`; assets `ok`; config `ok`.
- Runtime: engine `docker`, policy `cpu`, selected device `cpu`, PyTorch
  flavor `cpu`.
- Exact CPU digest: `PASS`.
- Google and Azure configured flags: `true`; no credential value was read or
  recorded.

## Managed-Network TLS Repair

Google validation initially returned `tls_ca_untrusted`; Azure was already
configured and ready.

- Packaged repair dry-run found one unambiguous non-leaf CA candidate: `PASS`.
- Certificate subjects, issuers, and thumbprints were suppressed from the
  transcript and are not evidence.
- Apply imported and verified the combined CA bundle, kept TLS verification
  enabled, updated the package `.env`, and produced no obvious credential
  pattern in the recent application log check: `PASS`.
- A subsequent explicit package relaunch activated both
  `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` at the persistent in-container
  bundle path: `PASS`.

### Finding W10-DCPU-001 - non-default port not preserved by TLS helper

**Severity**: release-support defect; bounded correction required before a
replacement candidate can be frozen.

The repair helper's internal `compose up` recreated the profile on default
port `5000` rather than preserving the active `5211` launch. It also correctly
instructed the operator to restart after updating `.env`; running the shipped
`start.bat -Engine docker -Gpu off -Port 5211` restored the intended port and
activated the repaired bundle. This is a real observed lifecycle failure, so
the previously optional saved-port convenience behavior is now evidence-
selected.

## Live Provider Results

| Provider/run | Result | Safe observations | Evidence SHA-256 |
| --- | --- | --- | --- |
| Azure normal | `PASS` | Estimate HTTP 200, one tile, 14 detections, 14 list entries, six address groups, nine visible map overlays | `d0a8c036bb13fda1f44ffa62a327098323261efd6609a05d6881935bb08c1e6f` |
| Google normal | `PASS` | Estimate HTTP 200, one tile, eight detections, eight list entries, four address groups, five visible map overlays | `706f689ff594c802c7cf555bd50bfa4eba2e6e994f0a29b069f2ffab78c32559` |
| Google after stop/relaunch | `PASS` | Both providers, assets, CA bundle, port, and digest persisted; estimate HTTP 200 and eight detections rendered | `60fc61fb58ef88d74a64980db6e96f0125d55fe414aaaa0e8f1bf43b3b68d394` |

## Cancellation And Recovery

### Finding W10-DCPU-002 - cancellation does not recover to next request

**Severity**: release blocker under W07/W10 acceptance.

The corrected cancel reproducer observed a real `/getobjects` request, issued
cancel, received abort HTTP `200`, observed populated progress text, and
confirmed that the overlay closed. The next Google request in the same browser
session did not complete within the declared 180-second timeout. Evidence
SHA-256:
`e3757b13547b0ae26c582f8cbaa46d362ee1f8e4994fe4ed8c826ade703b0e92`.

Source inspection bounds the likely race: `/abort` marks cancellation and
signals the run, but returns before the process-wide detection lock is
necessarily released; the frontend hides progress immediately when the abort
request returns. The required next-request success was therefore not
demonstrated. Two bounded corrected attempts were allowed; further repetition
stopped per the work plan.

A volume-preserving package stop and fresh-shell relaunch recovered normally.
Both provider settings, the repaired CA bundle, assets, port, and image digest
persisted, and the following normal Google detection passed. Relaunch recovery
does not satisfy the cancel-then-next-request gate.

## Evidence Hygiene Double Check

Eight local tool/result files were scanned before this index was written:

- Google-key patterns: `0`
- credential query/value patterns: `0`
- user-specific Windows paths: `0`
- machine-hostname labels: `0`

Only the accepted sanitized summaries and their hashes are referenced here.
Diagnostic runs that exercised a runner timing mistake are not acceptance
evidence and are not used to strengthen or weaken the candidate verdict.

## Remaining W10 Cells

- Docker CUDA live-provider/recovery: `not_run`.
- Podman CPU live-provider/recovery: `not_run`.
- Podman CUDA live-provider/recovery: `not_run`.
- Reboot persistence: `not_run`.
- Managed endpoint policy/signing: `blocked` pending the actual policy/decision.
- Independent-host repetition: `blocked` pending an independent computer.

The current immutable candidate must not be described as W10-qualified. The
smallest forward path is to add focused regressions for the two reproduced
lifecycle defects, implement bounded fixes, rebuild new immutable image/package
identities as affected, and repeat the impacted W09/W10 gates before resuming
the remaining matrix.

## Bounded Lifecycle Fix Validation

**Recorded**: 2026-09-28
**Scope**: Local source and local-only Docker CPU validation overlay; this is
not a replacement candidate identity and does not change the frozen-candidate
`FAIL` verdict above.

### W10-DCPU-001 port preservation

- The provider repair command now derives and validates
  `TOWERSCOUT_HOST_PORT`, falling back safely to `5000`, and emits an explicit
  `-Port` argument.
- `repair-provider-tls.ps1` forwards the port through its dry-run/apply command
  and lower-level importer invocation.
- `import-tls-ca.ps1` sets `TOWERSCOUT_PORT` before its internal Compose start.
- The focused Windows wrapper regression proved `-Port 5211` reaches the
  importer for both success and nonzero child exit paths.
- The live validation container emitted
  `repair-provider-tls.cmd ... -Port 5211` while remaining healthy on port
  `5211`.

Verdict for the reproduced mechanism: `PASS`. A replacement package must still
repeat the actual managed-network dry-run/apply path before candidate freeze.

### W10-DCPU-002 cancellation readiness

- `/abort` now signals cancellation and waits up to 60 seconds for the shared
  detection slot. It returns HTTP `200` with `retryReady=true` only after the
  slot is released; a bounded timeout returns HTTP `202` with
  `retryReady=false`.
- The frontend keeps the progress overlay and next-run guard active until the
  backend reports retry readiness. A pending or unreadable response no longer
  enables an unsafe retry.
- Deterministic thread/event tests prove the abort response cannot report
  readiness while `/getobjects` owns the slot, prove the bounded `202` path,
  and prove a next request succeeds after the ready response.
- A real Google cancel-and-next smoke on the local validation overlay observed
  `/getobjects`, received abort HTTP `200` after 7.77 seconds, hid the overlay,
  and completed the immediate next request in 2.87 seconds with eight
  detections, eight list entries, four address groups, and five visible map
  overlays. Sanitized evidence SHA-256:
  `36f59d6ccf7b1e97e1ab45f2775e86432c19a1f0555c1061880e214c51dca04d`.

Verdict for the reproduced mechanism: `PASS`.

### Validation and restoration

- Focused Python regressions: `108 passed`.
- Package/documentation regressions: `9 passed`.
- Complete in-scope unit suite with the explicitly deferred Task-087 host-
  helper file excluded: `585 passed, 74 skipped`.
- The unfiltered unit run reached `593 passed, 74 skipped`; 19 tests in the
  unchanged deferred Task-087 host-helper file failed because Windows
  antivirus blocked `TowerScoutHostHelper.ps1` as malicious content. This is
  an environmental/deferred-path result, not a lifecycle-fix pass, and no
  Task-087 work was resumed.
- Frontend cancellation contract, generated-bundle syntax, source syntax, and
  global contract: `PASS`.
- Evidence credential/path/hostname scan: zero matches for Google-key patterns,
  credential query/value patterns, user-specific Windows paths, and the prior
  hardware-derived host label.
- After live validation, the Docker CPU profile was restored to the original
  exact digest on port `5211`; health returned `healthy` and all eight named
  volumes remained attached.

The bounded fixes resolve both observed lifecycle mechanisms. Forward work is
to build new immutable CPU/CUDA image and control-package identities and repeat
affected W09/W10 cells. Publication and `latest` promotion remain owner-gated.

## Post-PR #89 Replacement Dispatch

PR [#89](https://github.com/J-Schulein/TowerScout/pull/89) merged as
`95a3ccce01fcbaf7f36c8de6fe9e2c6a5ca86833`. The owner then authorized the
next-step immutable image dispatch with `push_latest=false`.

Both `v0.1.3-rc2` builds, exact-digest scans, SBOM generation, and artifact
uploads completed. The accepted-baseline G10 delta gate correctly blocked both
jobs, so neither image is a replacement candidate and package assembly did not
use either digest.

| Flavor | Run | Published digest | G10 delta | Scan SHA-256 | SBOM SHA-256 |
| --- | --- | --- | --- | --- | --- |
| CPU | [36480293923](https://github.com/J-Schulein/TowerScout/actions/runs/36480293923) | `sha256:d5139aaffd8adbc040cf65411ec33f4344d40aa6180b1bb07dce311e674f3f7b` | BLOCK: 2 new, 1 resolved | `c1517fe2b6a16db6e6dde6156d04d39f190de4d0e08040d1da126ce129259be1` | `60224786c91d2f5bf3e603d5ff529395e176f982cc2573308fbc1828df617fc5` |
| CUDA 12.8 | [36480297059](https://github.com/J-Schulein/TowerScout/actions/runs/36480297059) | `sha256:a038823ff2d638edeabff617d94f0de6b86f3915cf13499b57f5dce35fc8abfc` | BLOCK: 2 new, 1 resolved | `d0f1b02d4d19dd54ee69b2c06c76397840c77ecdf9dbed44ca7ed32ae3309d2d` | `af38d6ee4c75116da016e7135f2fd4df19da664c07c2474f28b16caea572822b` |

The two new findings are `CVE-2026-80521` and `CVE-2026-97417`, both reported
as HIGH against `linux-libc-dev` 6.1.187-1 with no fixed version listed. The
SBOM dependency graph shows that the top-level `libgdal-dev` installation is
the sole path through `libc6-dev` to `linux-libc-dev`; the application uses
runtime wheels and `gdal-bin`, not the development headers.

A focused regression failed before the correction and passes after removing
only `libgdal-dev` from the runtime apt list. The surrounding ML/publish
contract ring passes 33 tests. A production-argument local CPU image builds,
contains neither `libgdal-dev` nor `linux-libc-dev`, reports GDAL 3.6.2, and
imports Fiona 1.10.1, GeoPandas 1.1.2, Pyogrio 0.13.0, and Shapely 2.0.3.
Its live `/api/health` response is `ok`; asset-light readiness is the expected
`setup_required` state. The test-owned container was stopped after validation.
The correction still requires reviewed merge and new immutable tags; the
blocked `rc2` tags must never be packaged or promoted.

## Post-PR #90 `rc3` Replacement Qualification

**Recorded**: 2026-09-28
**Scope**: Replacement images and exact control packages on
`FIRST-HOST-LOCAL`; first-host Docker CPU live-provider repetition is complete.
**Interim verdict**: `PASS` for image security, package integrity, four-profile
startup, exact identity, device selection, volume-preserving relaunch, managed
TLS repair, live Google/Azure detection, and Google cancel-then-next recovery.
This is not a complete W10 or release-ready verdict.

PR [#90](https://github.com/J-Schulein/TowerScout/pull/90) removed only the
unnecessary runtime `libgdal-dev` dependency and merged as
`7a5eedd8c6d3d6f300f320de69646f61da64c7ae`. Focused release/runtime tests,
strict agent-work validation, a production-argument CPU build, live health,
geospatial imports, and package exclusion of both `libgdal-dev` and
`linux-libc-dev` passed before merge. Exact-head CI and the automated review
were green.

### Immutable images and G10

| Flavor | Run | Exact digest | G10 result |
| --- | --- | --- | --- |
| CPU | [36483117066](https://github.com/J-Schulein/TowerScout/actions/runs/36483117066) | `sha256:a84201cec5704e35e0e7e5e05ca96aebeebb976ddeb89c88ac3145776bc1ba88` | PASS: 0 new, 245 resolved |
| CUDA 12.8 | [36483119457](https://github.com/J-Schulein/TowerScout/actions/runs/36483119457) | `sha256:6c54725b63cc8b66c996bc6d32d3e6714aada5fb51d07d840b7895dc70041fe5` | PASS: 0 new, 245 resolved |

Both dispatches used `push_latest=false`; exact-digest scan, SBOM, delta, and
written-disposition artifacts completed successfully. The scan artifact hashes
match those declared in the delta reports.

### Replacement control packages

- CPU control ZIP SHA-256:
  `0845a71a4b71ada66d9ba0be0ea71c500c1b0127317beff73af3e38ffbc2576b`
- CUDA control ZIP SHA-256:
  `d558db674c964c3a7cf47e661725157e59e7442a96e442ed02e9ff849ee5dcab`
- Shared asset ZIP SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`
- Shared asset ZIP length: `800655295` bytes.

Outer sidecars, all internal checksums, manifest identities, required
documentation/notices/helpers, and forbidden-content checks passed. No package
was published.

### First-host four-profile results

| Engine/profile | Port | Result |
| --- | ---: | --- |
| Docker CPU | 5221 | PASS: healthy, assets `ok`, device `cpu`, exact CPU digest, eight volumes retained across stop/relaunch |
| Docker CUDA | 5222 | PASS: healthy, assets `ok`, device `cuda`, exact CUDA digest, real `sm_120` CUDA kernel, eight volumes retained across stop/relaunch |
| Podman CPU | 5223 | PASS: rootless Podman 6.0.2, approved relative provider from a spaced path, device `cpu`, exact CPU digest, eight volumes retained across stop/relaunch |
| Podman CUDA | 5224 | PASS: rootless Podman 6.0.2 with NVIDIA CDI, device `cuda`, exact CUDA digest, real `sm_120` CUDA kernel, eight volumes retained across stop/relaunch |

Readiness is `setup_required` only because the fresh replacement volumes have
no provider credentials. The Docker CPU session on port 5221 is reserved for
interactive Google/Azure configuration and managed-TLS repetition. Credentials
will not be read, copied from the superseded volume, or retained in evidence.

### Replacement managed-network TLS repetition

- Keyless Google TLS probe before repair: `tls_ca_untrusted`; Azure: `tls_ok`.
- The generated Google repair command included the active `-Port 5221`.
- Sanitized dry-run: three CA candidates, one unambiguous top candidate, no
  mutation, and the emitted apply command retained port 5221.
- Apply: PASS; the helper verified Google with the imported bundle, retained
  port 5221, and did not enable insecure TLS.
- The documented explicit stop/start activated the persistent combined bundle
  at `/app/webapp/config/certs/towerscout-ca-bundle.pem` for both Requests and
  OpenSSL. Subsequent keyless Google and Azure probes both returned `tls_ok`.
- Container health, exact CPU digest, port 5221, assets, and all eight named
  volumes remained intact.

Verdict for W10-DCPU-001 on the replacement package: `PASS`. As accepted in
PR #89 review, an explicit launch port is process-scoped rather than persisted
to the package `.env`; lifecycle commands must continue to include `-Port 5221`.

### Replacement live-provider repetition

**Recorded**: 2026-09-29

The fresh Docker CPU package remained on port `5221`, exact CPU digest
`sha256:a84201cec5704e35e0e7e5e05ca96aebeebb976ddeb89c88ac3145776bc1ba88`,
with assets `ok`, readiness `ready`, repaired TLS verification enabled, and all
eight named volumes attached. Both providers were configured through the UI;
no credential value was read or retained.

| Provider/run | Result | Safe observations | Evidence SHA-256 |
| --- | --- | --- | --- |
| Google normal | `PASS` | Estimate HTTP 200, one tile, eight detections and addresses, eight list entries, four address groups, five visible overlays | `b863a1bba2da1be8450cc8e6a29e1a5ebb8ee27a4fb9cfa85475587096f36ae6` |
| Google cancel then immediate next request | `PASS` | Cancel returned HTTP 202 while readiness was pending; progress was populated before cancel and hidden only after readiness; zero post-cancel detections; the immediate next request completed in 3.36 seconds with the same eight-detection result | `4a1629023c312b4d9645a4d951e823fb97f4b19e3dc028e0f57840426bf898f2` |
| Azure normal | `PASS` | Estimate HTTP 200, one tile, 14 detections and addresses, 14 list entries, six address groups, nine visible overlays; all Azure initialization milestones true | `02644704c62375f9cb7bf71ba16041d345530f9c81e4bc4d96b820fa0fe07aa9` |

The accepted fixture SHA-256 remained
`fd6771ed3aa30a44c5bedb7575ed7f164896e496292fae29ac1da4bb9638d715`.
The final ignored sanitized-runner SHA-256 was
`ac8fa29d19225b1428477c1e9f402841daf0076e9f2f966b25d0ede4909e2ca7`.
The runner retained only status/timing/count/boolean fields and coarse error
categories; it disabled screenshots and omitted provider URLs, payloads,
response bodies, console text, credentials, AOI coordinates, local paths, and
machine hostnames.

Two initial Azure attempts timed out before provider initialization and are not
acceptance evidence. Investigation showed the stock smoke harness considered
the provider-radio insertion sufficient for readiness even though default-
provider startup and switch-handler attachment were still in progress. The
ignored wrapper was corrected to wait for a settled, fully initialized default
provider and an idle switch manager before selecting Azure. Azure then passed
twice; the second passing run above is the accepted double-check.

The accepted Azure run recorded no page, authentication, rate-limit,
initialization, drawing, search, or geocoding errors. Its only HTTP failure was
the same-origin missing favicon (`404`). Three provider-labelled browser-console
events remained unclassified external SDK noise; they had no matching network
failure or functional effect and are retained as a visible residual rather
than suppressed.

Verdict for W10-DCPU-002 on the replacement package: `PASS`. The real Google
cancel path did not expose an unsafe retry, and the immediate next request
succeeded without relaunch.

### Remaining replacement cells

- Fresh-`rc3` managed TLS repair: `PASS`.
- Fresh-`rc3` Google normal, Google cancel-then-next, and Azure normal: `PASS`.
- Reboot persistence: `not_run`.
- Managed endpoint policy/signing: `blocked` pending the actual policy and
  owner decision.
- Independent-host repetition: `blocked` pending an independent computer.
- Package publication and `latest` promotion: owner-gated and not performed.

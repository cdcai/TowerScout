# Task-103 W10 Local First-Host Evidence Index

## Current interpretation - October 20, 2026

This index retains the previously local RC9-era record below in full.
Its results concern the exact historical artifacts named there, not new
official cdcai bytes. No runtime tests or security scans were repeated during
this reconciliation.

The current accepted fork candidate is `v0.1.3-rc5`, governed by
[ADR-026](../../../decisions/026-rc5-bounded-candidate-acceptance.md) and the
[RC5 closeout](../TASK-105/RC5-QUALIFICATION-CLOSEOUT-2026-10-19.md).
[ADR-025](../../../decisions/025-two-host-final-candidate-qualification.md)
replaced the earlier CPU-only/Podman-without-Docker allocation with two
Windows NVIDIA hosts; the excluded environments remain unqualified.

Below, phrases such as "current candidate", "still open", "remaining", and
"required" describe the historical checkpoint date. They are not today's
release requirements or publication status. RC9 independent-host findings
led to TASK-105 corrections and subsequent RC5 acceptance; do not reopen
resolved items solely because their earlier status is retained here.

## Historical evidence snapshot - retained from local working copy

**Recorded**: 2026-09-28; updated 2026-10-14
**Host ID**: `FIRST-HOST-LOCAL`
**Scope**: Same-machine first-host rehearsal only; this is not the independent
host required for full W10 acceptance.
**Verdict**: `INCOMPLETE` for full W10, with the final local `rc4` first-host
four-profile workflow subset now `PASS`. Every profile passes live Google and
Azure detection, cancellation/next-request recovery, a controlled recoverable
error followed by success, review/export, provider/TLS persistence,
volume-preserving stop/relaunch and reboot, exact digest, and required CPU/CUDA
device selection. ADR-023 resolves policy/signing by narrowing the standard
support claim. The preliminary `rc4` browser-download Docker CPU diagnostic
passed. Documentation-aligned RC9 CPU/CUDA images and control ZIPs are now
published in the non-Latest validation prerelease. All four exact browser-
downloaded RC9 first-host profiles and Docker/Podman reboot persistence pass.
One independent NVIDIA host also passed all four profiles, with the findings,
deviations, and remaining host allocation transferred to TASK-105.
**Publication state**: The old `rc4` diagnostic assets remain historical. The
six exact RC9 assets are published in non-draft GitHub prerelease
`v0.1.0-rc9`; stable `v0.1.2` remains Latest and no GHCR `latest` image tag was
promoted.

## Superseded Pre-`rc3` Frozen Inputs

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
- Managed endpoint policy/signing: `blocked` at this historical checkpoint;
  later resolved by scope through ADR-023 on 2026-10-01.
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

**Historical mechanism note**: This subsection records an interim local
validation overlay that was not merged. It used a bounded server-side wait and
therefore observed abort HTTP `200` after the slot was released. PR #93,
subsequently merged as `fba9dcb`, supersedes that mechanism with a non-blocking
HTTP `202` response while the slot is held and progress polling tied to the
actual admission lock. The evidence below qualifies only the interim
reproduction; the merged behavior requires repetition on new immutable images
and replacement packages.

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

### Replacement post-reboot persistence

**Recorded**: 2026-09-29

Windows last-boot time was `2026-09-29T09:00:02.5000000-04:00`, establishing a
real reboot boundary. Docker Desktop was available after boot and
automatically restored the Docker CPU and CUDA containers. The retained
rootless Podman machine was running, but both retained Podman package
containers were stopped and required an explicit manual start; no container or
volume was recreated or removed.

| Engine/profile | Post-boot observation | Result |
| --- | --- | --- |
| Docker CPU / `5221` | Auto-restored healthy; exact CPU digest; assets/config `ok`; selected CPU; both providers configured; default Google; zero recovery items | `PASS` |
| Docker CUDA / `5222` | Auto-restored healthy; exact CUDA digest; assets `ok`; selected CUDA; setup remains required only because this isolated profile has no provider credentials | `PASS` for infrastructure persistence |
| Podman CPU / `5223` | Existing container manually started healthy on the retained rootless machine; exact CPU digest; assets `ok`; selected CPU; setup remains required only because this isolated profile has no provider credentials | `PASS` for documented manual recovery |
| Podman CUDA / `5224` | Existing container manually started healthy on the retained rootless machine; exact CUDA digest; assets `ok`; selected CUDA; setup remains required only because this isolated profile has no provider credentials | `PASS` for documented manual recovery |

All four ports remained loopback-bound and each profile retained exactly eight
named volumes. Docker and Podman CUDA each completed a real matrix kernel with
torch `2.10.0+cu128`, CUDA build `12.8`, capability `sm_120`, and finite output.

On Docker CPU, the persistent combined CA bundle remained present at the
package path, `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` both selected it, and no
checked verification-disable flag was active. Keyless Google and Azure probes
both returned `tls_ok` (Azure's expected unauthenticated HTTP `401` still
establishes trusted TLS reachability).

| Post-reboot provider run | Result | Safe observations | Evidence SHA-256 |
| --- | --- | --- | --- |
| Google normal | `PASS` | Estimate HTTP 200, one tile, eight detections and addresses, eight list entries, four address groups, five visible overlays | `811db8a3fc24ba13dd2a65db715f48aefe8b0a0970e118017c9dadeeed7b7b17` |
| Azure normal | `PASS` | Estimate HTTP 200, one tile, 14 detections and addresses, 14 list entries, six address groups, nine visible overlays; all Azure initialization milestones true | `65ba9b9b966cdffa8be2fbdc009ce5078958375a05fae7f52540bab179e7c1fc` |

The known-good ignored sanitized runner remained byte-identical at SHA-256
`ac8fa29d19225b1428477c1e9f402841daf0076e9f2f966b25d0ede4909e2ca7`.
An optional attempt to extend it for review/export and controlled-error proof
produced no acceptance artifact and left two test-owned Node runners; both
runners were stopped, the known-good runner bytes were restored, and no result
from that attempt is claimed. Those cells remain `not_run` below.

### Remaining replacement cells

- Fresh-`rc3` managed TLS repair: `PASS`.
- Fresh-`rc3` Google normal, Google cancel-then-next, and Azure normal: `PASS`.
- First-host reboot infrastructure persistence: `PASS` for all four profiles;
  Docker auto-restored and Podman used the documented manual container start.
- Docker CPU post-reboot Google and Azure normal requests: `PASS`.
- Docker CPU review/export and controlled recoverable error: `not_run`.
- Docker CUDA Google/Azure, review/export, cancellation, controlled recoverable
  error, and next-request success: `not_run`; its isolated volume has no
  provider credentials.
- Podman CPU Google/Azure, review/export, cancellation, controlled recoverable
  error, and next-request success: `not_run`; its isolated volume has no
  provider credentials.
- Podman CUDA Google/Azure, review/export, cancellation, controlled recoverable
  error, and next-request success: `not_run`; its isolated volume has no
  provider credentials.
- Managed endpoint policy/signing: `blocked` at this historical checkpoint;
  later resolved by scope through ADR-023 on 2026-10-01.
- Independent-host repetition: `blocked` pending an independent computer.
- Package publication and `latest` promotion: owner-gated and not performed.

The bounded cleanup inventory and preservation decision are recorded in
[RC4-CLEANUP-INVENTORY-2026-10-02.md](./RC4-CLEANUP-INVENTORY-2026-10-02.md).

## Final Local `rc4` Four-Profile Repetition

**Recorded**: 2026-09-29 through 2026-09-30
**Scope**: Exact locally assembled `rc4` control packages and owner-confirmed
immutable image digests on `FIRST-HOST-LOCAL`. This closes the first-host live
workflow cells but not the independent-host or managed-policy gates.

### Bound identities

- Source: `541622556fb7999ee4e88fb1e44f7797b9da34f5`.
- CPU image digest:
  `sha256:a3eeb77152577f3656a286777bd4c4312cecc311cb5a5cc1b132b459f1ecd18f`.
- CUDA image digest:
  `sha256:61dab3b83e1be8e2cf955d9d7d2d9b997a207a4dcb76b20344a268a5690f654a`.
- CPU control ZIP SHA-256:
  `1cf763b6184bb96dfe976f41f56a4aa5b8eeeea51a8de59830a9bf7fb9784a55`.
- CUDA control ZIP SHA-256:
  `02ec76b93bea28417b7ea4b086f23148b57b34c33823ce2f113da7147165915f`.
- Shared asset ZIP SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- Safe committed fixture SHA-256:
  `fd6771ed3aa30a44c5bedb7575ed7f164896e496292fae29ac1da4bb9638d715`.
- Ignored sanitized qualification runner SHA-256:
  `0ee0a785cf90bbf96dad45451dd5d00c34368d809a6ff207ab9670b37359070d`.

The runner and retained summaries expose only provider labels, status codes,
counts, and boolean UI/runtime state. Raw URLs, request/response bodies,
credentials, AOI coordinates, screenshots, console text, local paths, and host
names were not retained. Stock smoke artifacts were reduced to safe facts and
their raw run directories were removed immediately after each run.

### Profile matrix

| Profile | Port | Live-provider and recovery result | Review/export result | Lifecycle/device result |
| --- | ---: | --- | --- | --- |
| Docker CPU | 5231 | PASS: Google 8 and Azure 14 detections; cancel HTTP 202, overlay cleared, immediate next request passed; controlled HTTP 400 followed by HTTP 200 | PASS: review navigation; nonempty CSV/KML; dataset HTTP 200, eight selected inputs, nonempty valid ZIP | PASS: repaired Google TLS and both provider settings survived stop/relaunch; exact CPU digest, assets/config `ok`, CPU selected, eight mounts |
| Docker CUDA | 5232 | PASS: Google 8 and Azure 14 detections; cancel HTTP 202, overlay cleared, immediate next request passed; controlled HTTP 400 followed by HTTP 200 | PASS: review navigation; nonempty CSV; dataset HTTP 200, eight selected inputs, nonempty valid ZIP | PASS: repaired Google TLS and both provider settings survived stop/relaunch; exact CUDA digest, assets/config `ok`, real finite `sm_120` CUDA kernel, eight mounts |
| Podman CPU | 5233 | PASS: Google 8 and Azure 14 detections; cancel HTTP 202, overlay cleared, immediate next request passed; controlled HTTP 400 followed by HTTP 200 | PASS: review navigation; nonempty CSV/KML; dataset HTTP 200, eight selected inputs, nonempty valid ZIP | PASS: repaired Google TLS and both provider settings survived package-pinned Podman stop/relaunch; exact CPU digest, assets/config `ok`, CPU selected, eight mounts |
| Podman CUDA | 5234 | PASS: Google 8 and Azure 14 detections; cancel HTTP 202, overlay cleared, immediate next request passed; controlled HTTP 400 followed by HTTP 200 | PASS: review navigation; nonempty CSV/KML; dataset HTTP 200, eight selected inputs, nonempty valid ZIP | PASS: repaired Google TLS and both provider settings survived package-pinned Podman stop/relaunch; exact CUDA digest, assets/config `ok`, real finite `sm_120` CUDA kernel, eight mounts |

Every estimate returned HTTP 200 with one tile. The controlled error was the
documented validation path: an intentionally empty estimate request returned
HTTP 400, after which the same browser session completed a real provider-backed
detection with HTTP 200. Post-relaunch Google detections passed in every
profile. No credential value was read or copied between isolated volumes.

Two Docker CUDA Azure attempts using the stock harness timed out before
detection because it switched as soon as provider radios appeared. The
previously documented harness correction—wait for the default provider to be
fully initialized, for `getIsInitializing()` to be false, and for the provider
switch queue to be idle—then produced the accepted Azure pass. Several
review/export diagnostics also exposed Chrome's suppression of simultaneous
downloads; isolated CSV/KML sessions and an in-memory dataset ZIP check passed.
No failed diagnostic is counted as acceptance evidence.

### Exact-`rc4` post-reboot persistence

**Recorded**: 2026-09-30

Windows Event Log service start at `2026-09-30T17:36:44.6273762Z` established
a new reboot boundary after the final local matrix. Docker Desktop
automatically restored both `rc4` containers healthy. The retained rootless
Podman machine was running, while its CPU and CUDA containers remained stopped
until the documented explicit manual start. Those existing containers were
started in place; no container, image, network, or named volume was recreated
or deleted.

| Profile | Restoration and identity | Post-reboot provider result |
| --- | --- | --- |
| Docker CPU / 5231 | Auto-restored; healthy; exact CPU digest; assets/config `ok`; CPU selected; eight mounts | Google and Azure each returned estimate HTTP 200, one tile, detection HTTP 200, review navigation, controlled HTTP 400 then HTTP 200 recovery, and a nonempty valid dataset ZIP |
| Docker CUDA / 5232 | Auto-restored; healthy; exact CUDA digest; assets/config `ok`; CUDA selected; eight mounts; finite `sm_120` kernel on `cuda:0` | Same Google/Azure pass; eight Google and 14 Azure detections; zero page errors |
| Podman CPU / 5233 | Existing retained container manually started; healthy; exact CPU digest; assets/config `ok`; CPU selected; eight mounts | Same Google/Azure pass; eight Google and 14 Azure detections; zero page errors |
| Podman CUDA / 5234 | Existing retained container manually started; healthy; exact CUDA digest; assets/config `ok`; CUDA selected; eight mounts; finite `sm_120` kernel on `cuda:0` | Same Google/Azure pass; eight Google and 14 Azure detections; zero page errors |

Both providers remained configured in all four isolated configuration volumes.
Keyless Google and Azure probes returned `tls_ok` on every profile. The
post-reboot smoke runner and fixture remained byte-identical to the hashes
recorded above; every run reported `sensitiveArtifactsRetained=false`. No raw
browser-run directory or temporary download directory remained.

### Final local double check and open gates

All four profiles simultaneously reported `ready`, assets/config `ok`, the
required CPU or CUDA device, both providers configured, the exact expected
digest, and exactly eight mounts. Zero raw browser-run directories, temporary
export directories, or task-owned browser automation processes remained.

The remaining gates are explicit:

- Exact-`rc4` reboot persistence: `PASS` for all four profiles. Docker
  auto-restored; Podman required the documented manual retained-container
  start. Provider/TLS state, exact digests, devices, and eight mounts per
  profile persisted, and all eight post-reboot Google/Azure workflow runs
  passed.
- Managed endpoint policy/signing: `resolved by scope` under ADR-023. The
  package remains unsigned; signature-enforcing managed endpoints are outside
  the standard support claim and are not recorded as passes.
- Preliminary `rc4` browser download: `PASS` for the bounded Docker CPU subset;
  see the
  [diagnostic record](../TASK-092/RC4-BROWSER-DOWNLOAD-DIAGNOSTIC-2026-10-02.md).
  It is diagnostic only.
- Replacement package/browser download: `IN_PROGRESS`. Exact browser-
  downloaded RC9 Docker CPU/CUDA and Podman CPU/CUDA first-host acceptance
  and reboot persistence pass; independent-host RC9 cells remain.
- Independent-host four-profile repetition: `blocked` pending an independent
  Windows computer.
- RC9 prerelease publication: `PASS` for the non-Latest validation prerelease.
  `latest` promotion and stable/general release remain owner-gated and were not
  performed.

## Exact Browser-Downloaded RC9 Podman CPU Acceptance

**Recorded**: 2026-10-13
**Scope**: `FIRST-HOST-LOCAL`, rootless Podman CPU only. This closes the RC8
affected-profile repetition but does not establish full W10 or independent-host
acceptance.

### Bound identities and setup

- CPU control ZIP SHA-256:
  `66e674ef28d98835a981bd731bc7a86e7c6bdd07cb9ea964d47e4e9c63cfacfc`.
- Shared asset ZIP SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- CPU image digest:
  `sha256:9d24cc71724953fba7e062b6ee71dac38f2ec413716a9b60bfaf8ad0be20c950`.
- Source revision label:
  `b3431cf86d8a000462df487685104558ac7becd3`.
- All six browser downloads retained their Windows Internet-zone marker. The
  CPU ZIP sidecar, all 73 internal checksum entries, manifest identities, and
  the asset sidecar passed before setup.
- Docker Desktop was closed. Rootless Podman 6.0.2 used the approved
  package-local `podman-compose==1.5.0` provider installed with Python 3.12.
- A stopped RC8 evidence container still reserved port 5000, so the supported
  explicit port 5235 was used without deleting or modifying the RC8 container.

### Runtime and workflow result

- Setup imported and hash-verified both models and packaged ZCTA data. The
  running container was healthy, loopback-bound to `127.0.0.1:5235`, selected
  CPU with `torch==2.10.0+cpu`, used the exact RC9 digest, and retained exactly
  eight mounts.
- Azure configuration reached readiness `ready`. A real one-tile CPU workflow
  returned 14 detections with both models exercised and zero page errors.
- The affected cancellation test returned abort HTTP 200, zero cancelled-run
  detections, a hidden progress overlay after cancellation, and an immediate
  successful 14-detection retry. No `DETECTION_BUSY` response occurred.
- Google initially reproduced the documented certificate-verification error.
  The packaged dry-run selected one unambiguous trusted Windows CA, and the
  packaged `-Apply` repair returned `google_tls_status=200` and
  `google_tls_category=tls_ok`. Certificate subjects and thumbprints are not
  retained. A volume-preserving stop/start kept Azure configuration and the
  repaired trust bundle.
- Google then saved successfully. A real one-tile CPU workflow returned eight
  detections, used Google imagery/geocoding, exercised both models, and
  reported zero page errors.
- ZIP code `10038` returned HTTP 200 with nonempty polygon geometry from the
  packaged ZCTA data.
- The sanitized qualification runner retained SHA-256
  `0ee0a785cf90bbf96dad45451dd5d00c34368d809a6ff207ab9670b37359070d`.
  An intentional empty estimate returned HTTP 400, followed in the same
  browser session by a real HTTP 200 detection. Review mode exposed detection
  and tile navigation. Separate sessions produced nonempty CSV and KML
  downloads plus a nonempty valid dataset ZIP containing all eight selected
  Google detections.
- The running `/docs/user-guide.html` returned HTTP 200 and matched the
  package copy byte-for-byte at SHA-256
  `3cf40281a8b1f771784e1e047e45390260ece37d63973a2d4e8487eadf8dc576`.
  Its four internal links all returned HTTP 200.

### Evidence safety and remaining gates

Only sanitized status codes, counts, booleans, public artifact identities, and
non-sensitive runtime facts are recorded here. Provider keys, certificate
identities, AOI coordinates, raw browser/network logs, screenshots, and
temporary export files were not retained. The two stock harness run folders
were deleted after their safe facts were reduced into this record; the
sanitized export runner removed its own temporary downloads.

Verdict for exact-browser-downloaded RC9 Podman CPU first-host acceptance:
`PASS`. Still open: RC9 Docker CPU, Docker CUDA, reboot persistence as required
for the final candidate, and independent-host four-profile reproduction.

## Exact Browser-Downloaded RC9 Podman CUDA Acceptance

**Recorded**: 2026-10-13
**Scope**: `FIRST-HOST-LOCAL`, rootless Podman CUDA 12.8. This completes the
exact-browser-downloaded RC9 Podman CUDA first-host profile but does not
establish Docker, reboot, or independent-host acceptance.

### Bound identities and setup

- CUDA control ZIP SHA-256:
  `5157a3a396502e524b16dd5eda6cf46aa80521ba4409546af8625f1ca43cad10`.
- Shared asset ZIP SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- CUDA image digest:
  `sha256:c2d99f178465a8cdc83430092554d98aeb181797ff330fba2661bc95a45d8287`.
- Source revision label:
  `b3431cf86d8a000462df487685104558ac7becd3`.
- The downloaded ZIP sidecar, all 73 internal checksum entries, manifest
  identities, and shared-asset sidecar passed before setup.
- Rootless Podman 6.0.2 used the approved package-local
  `podman-compose==1.5.0` provider. The package GPU helper provisioned and
  verified NVIDIA CDI only in `podman-machine-default`; its exact-image
  transient GPU smoke passed after the immutable image pull completed.
- The supported explicit port 5236 was free and used without altering the
  retained CPU or RC8 containers and volumes.

### Runtime and workflow result

- Setup imported and hash-verified both models and packaged ZCTA data. The
  container is healthy and loopback-bound to `127.0.0.1:5236` at the exact RC9
  digest.
- Readiness reports `torch==2.10.0+cu128`, CUDA build `12.8`, cuDNN `91002`,
  capability `sm_120`, the NVIDIA RTX PRO 500 Blackwell Generation Laptop GPU,
  a successful CUDA kernel probe, and no fallback reason.
- Azure configuration reached readiness `ready`. The affected cancellation
  test returned abort HTTP 200 after 50 ms, produced zero cancelled-run
  detections, hid the progress overlay, and immediately retried successfully.
- The one-tile retry completed in 11.14 seconds with 14 detections, 14 selected
  results, 14 addresses, six address groups, nine visible overlays, zero page
  errors, and no `DETECTION_BUSY` marker.
- Runtime logs bind this accepted request to `CUDA enabled` for YOLOv5 and
  `EfficientNet loaded on cuda (policy=cuda, fallback=None)`. GPU memory was
  allocated during the run; no CPU fallback message was present.
- Google configuration first reproduced the documented `tls_ca_untrusted`
  result. The packaged dry-run found three chain candidates with one uniquely
  highest-ranked trusted Windows CA; no tie or manual selection was required.
  The packaged `-Apply` path returned `google_tls_status=200` and
  `google_tls_category=tls_ok` without retaining certificate identity.
- As instructed by the helper, a package-pinned, volume-preserving Podman stop
  and relaunch was then completed. The recreated app process selected
  `/app/webapp/config/certs/towerscout-ca-bundle.pem` through both TLS bundle
  environment variables, a keyless Google probe returned HTTP 200, Azure
  configuration persisted, and the exact image digest, port, assets, and CUDA
  device remained unchanged. A premature retry before this required relaunch
  is not counted as acceptance evidence.
- Google then saved successfully. A real one-tile Google workflow completed in
  11.41 seconds with estimate HTTP 200, eight detections, eight selected
  results, eight addresses, four address groups, five visible overlays, and
  zero page errors. Runtime logs again bound both YOLOv5 and EfficientNet to
  CUDA with no CPU fallback.
- ZIP code `10038` returned HTTP 200 with a nonempty GeoJSON polygon from the
  packaged ZCTA data.
- The sanitized qualification runner remained byte-identical at SHA-256
  `0ee0a785cf90bbf96dad45451dd5d00c34368d809a6ff207ab9670b37359070d`.
  In three isolated sessions, an intentional empty estimate returned HTTP 400
  and the immediate real request returned HTTP 200 with eight detections.
  Review mode exposed detection and tile navigation. CSV and KML downloads were
  nonempty, and the dataset response was a nonempty ZIP with a valid signature
  and all eight selected inputs. Every session reported zero page errors and
  removed its temporary download directory.
- The running `/docs/user-guide.html` matched the extracted package copy
  byte-for-byte at SHA-256
  `3cf40281a8b1f771784e1e047e45390260ece37d63973a2d4e8487eadf8dc576`.
  Its four internal targets - Quick Start, Local IT Administrator Guide,
  Package Guide, and the documentation stylesheetâ€”all returned HTTP 200.
- The final package-pinned stop/relaunch recreated only the container while
  preserving the same eight named volumes. Both providers, the combined CA
  paths, asset/config status, CUDA selection and kernel probe, exact image
  digest, and `127.0.0.1:5236` binding persisted. A real post-relaunch Google
  request again returned estimate HTTP 200, one tile, eight detections and
  addresses, and zero page errors.

### Evidence safety and remaining gates

Only the safe facts above are retained. Provider keys, request URLs and bodies,
AOI coordinates, console text, screenshots, certificate identities, and export
payloads are not acceptance evidence. All three stock browser-run directories
were removed after their safe facts were reduced into this record, and the
sanitized runner removed its own temporary downloads.

Verdict for exact-browser-downloaded RC9 Podman CUDA first-host acceptance:
`PASS`. Still open: RC9 Docker CPU, Docker CUDA, reboot persistence as required
for the final candidate, and independent-host four-profile reproduction.

## Exact Browser-Downloaded RC9 Docker CPU Acceptance

**Recorded**: 2026-10-13
**Scope**: `FIRST-HOST-LOCAL`, Docker Desktop CPU. This completes the
exact-browser-downloaded RC9 Docker CPU first-host profile but does not
establish Docker CUDA, reboot, or independent-host acceptance.

### Bound identities and setup

- A fresh Docker-only extraction used CPU control ZIP SHA-256
  `66e674ef28d98835a981bd731bc7a86e7c6bdd07cb9ea964d47e4e9c63cfacfc`;
  all 73 internal checksum entries passed and no inherited `.env` existed.
- The shared asset ZIP remained SHA-256
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
  Setup imported and hash-verified both real models and packaged ZCTA data.
- The healthy container uses exact image digest
  `sha256:9d24cc71724953fba7e062b6ee71dac38f2ec413716a9b60bfaf8ad0be20c950`,
  is loopback-bound to `127.0.0.1:5237`, selects the CPU-only torch flavor,
  and has exactly eight named mounts.

### Azure result

- Azure configuration reached readiness `ready`. The cancellation test
  returned abort HTTP 202, produced zero cancelled-run detections, hid the
  progress overlay, and immediately retried successfully.
- The one-tile retry completed in 2.67 seconds with 14 detections, 14 selected
  results, 14 addresses, zero page errors, and no `DETECTION_BUSY` marker.
- Runtime logs bind this accepted request to `YOLOv5 using CPU` and
  `EfficientNet loaded on cpu`, both with `policy=cpu` and `fallback=None`.
  No CUDA-selection message was present.

### Google TLS and provider result

- Google configuration first reproduced the documented `tls_ca_untrusted`
  result. The packaged dry-run found three chain candidates with one uniquely
  highest-ranked trusted Windows CA; no tie or manual selection was required.
- The packaged `-Apply` repair returned `google_tls_status=200` and
  `google_tls_category=tls_ok`, rebuilt the combined bundle, and updated the
  package `.env` without retaining certificate identity.
- As required by the helper, a package-pinned Docker stop and relaunch then
  recreated the container while preserving its volumes. Both TLS environment
  variables selected `/app/webapp/config/certs/towerscout-ca-bundle.pem`; a
  keyless Google probe returned HTTP 200, Azure configuration persisted, and
  the exact image digest, CPU selection, and port remained unchanged.
- Google then saved successfully. A real one-tile Google workflow completed
  in 18.29 seconds with one estimate request, one detection request, eight
  detections, eight selected results, eight addresses, five visible overlays,
  and zero page errors. Runtime logs again bound both YOLOv5 and EfficientNet
  to CPU with no CUDA-selection marker.

### Functional, recovery, export, and Help result

- ZIP code `10038` returned HTTP 200 with one nonempty GeoJSON feature and
  polygon geometry from the packaged ZCTA data. An initial 30-second client
  timeout was inconclusive; the immediate isolated retry completed normally
  and is the accepted result.
- The sanitized qualification runner remained byte-identical at SHA-256
  `0ee0a785cf90bbf96dad45451dd5d00c34368d809a6ff207ab9670b37359070d`.
  In three isolated sessions, an intentional empty estimate returned HTTP 400
  and the immediate real request returned HTTP 200 with eight detections.
  Review mode exposed detection and tile navigation. CSV and KML downloads
  were nonempty, and the dataset response was a nonempty ZIP with a valid
  signature and all eight selected inputs. Every session reported zero page
  errors and removed its temporary download directory.
- The running `/docs/user-guide.html` matched the extracted package copy
  byte-for-byte at SHA-256
  `3cf40281a8b1f771784e1e047e45390260ece37d63973a2d4e8487eadf8dc576`.
  Quick Start, Local IT Administrator Guide, Package Guide, and the
  documentation stylesheet all returned HTTP 200.

### Stop/relaunch persistence result

- The final package-pinned stop/relaunch recreated only the container while
  preserving the same eight named volumes. Both providers, both combined-CA
  environment paths, the exact image digest, CPU selection, readiness, and
  `127.0.0.1:5237` binding persisted.
- After Docker health returned to `healthy`, a real Google request again
  completed one estimate request and one detection request with eight
  detections, eight selected results, eight addresses, five visible overlays,
  and zero page errors.

Only safe status codes, counts, public identities, and runtime facts are
retained. Provider keys, request URLs/bodies, AOI coordinates, console text,
and screenshots are not acceptance evidence; the stock browser-run directory
is removed after this record is written.

Verdict for exact-browser-downloaded RC9 Docker CPU first-host acceptance:
`PASS`. Still open at this point in the sequence: RC9 Docker CUDA, reboot
persistence as required for the final candidate, and independent-host four-
profile reproduction.

## Exact Browser-Downloaded RC9 Docker CUDA Acceptance

**Recorded**: 2026-10-13
**Scope**: `FIRST-HOST-LOCAL`, Docker Desktop CUDA 12.8. This completes the
exact-browser-downloaded RC9 Docker CUDA first-host profile but does not
establish reboot or independent-host acceptance.

### Bound identities and setup

- A fresh Docker-only extraction used CUDA control ZIP SHA-256
  `5157a3a396502e524b16dd5eda6cf46aa80521ba4409546af8625f1ca43cad10`;
  its published sidecar and all 73 internal checksum entries passed, and no
  inherited `.env` existed.
- The shared asset ZIP remained SHA-256
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
  Setup imported and hash-verified the real models and packaged ZCTA data.
- The healthy container uses exact image digest
  `sha256:c2d99f178465a8cdc83430092554d98aeb181797ff330fba2661bc95a45d8287`
  from source revision `b3431cf86d8a000462df487685104558ac7becd3`, is
  loopback-bound to `127.0.0.1:5238`, and has exactly eight named mounts.

### Device result

- Readiness reports `torch==2.10.0+cu128`, CUDA build `12.8`, cuDNN `91002`,
  capability `sm_120`, and the NVIDIA RTX PRO 500 Blackwell Generation Laptop
  GPU.
- CUDA architecture, kernel, matrix, convolution, and precision probes all
  pass. Device policy and selected device are both `cuda`, with no fallback or
  probe error. Readiness is correctly `setup_required` until a provider is
  configured.

### Azure result

- Azure configuration reached readiness `ready`. The cancellation test
  returned abort HTTP 202, produced zero cancelled-run detections, hid the
  progress overlay, and immediately retried successfully.
- The one-tile retry completed in 2.27 seconds with 14 detections, 14 selected
  results, 14 addresses, nine visible overlays, zero page errors, and no
  `DETECTION_BUSY` marker.
- Runtime logs bind this accepted request to `CUDA enabled` for YOLOv5 and
  `EfficientNet loaded on cuda (policy=cuda, fallback=None)`. No CPU fallback
  marker was present.

### Google TLS and provider result

- Google configuration first reproduced the documented `tls_ca_untrusted`
  result. The packaged dry-run found three chain candidates with one uniquely
  highest-ranked trusted Windows CA; no tie or manual selection was required.
- The packaged `-Apply` repair returned `google_tls_status=200` and
  `google_tls_category=tls_ok`, rebuilt the combined bundle, and updated the
  package `.env` without retaining certificate identity.
- A package-pinned Docker stop and relaunch recreated the container while
  preserving all eight volumes. Both TLS environment variables selected
  `/app/webapp/config/certs/towerscout-ca-bundle.pem`; a keyless Google probe
  returned HTTP 200, Azure configuration persisted, and the exact image
  digest, CUDA 12.8 selection/kernel probe, local port, and no-fallback state
  remained unchanged.
- Google then saved successfully. A real one-tile Google workflow completed
  in 9.37 seconds with one estimate request, one detection request, eight
  detections, eight selected results, eight addresses, five visible overlays,
  and zero page errors. Runtime logs again bound YOLOv5 and EfficientNet to
  CUDA with no CPU fallback marker.

### Functional, recovery, export, and Help result

- ZIP code `10038` returned HTTP 200 with one nonempty GeoJSON feature and
  polygon geometry from the packaged ZCTA data. The first client invocation
  did not return a usable result to the orchestrator; the immediate isolated
  bounded request completed normally and is the accepted result.
- The sanitized qualification runner remained byte-identical at SHA-256
  `0ee0a785cf90bbf96dad45451dd5d00c34368d809a6ff207ab9670b37359070d`.
  In three isolated sessions, an intentional empty estimate returned HTTP 400
  and the immediate real request returned HTTP 200 with eight detections.
  Review mode exposed detection and tile navigation. CSV and KML downloads
  were nonempty, and the dataset response was a nonempty ZIP with a valid
  signature and all eight selected inputs. Every session reported zero page
  errors and removed its temporary download directory.
- The running `/docs/user-guide.html` matched the extracted package copy
  byte-for-byte at SHA-256
  `3cf40281a8b1f771784e1e047e45390260ece37d63973a2d4e8487eadf8dc576`.
  Quick Start, Local IT Administrator Guide, Package Guide, and the
  documentation stylesheet all returned HTTP 200.

### Stop/relaunch persistence result

- The final package-pinned stop/relaunch recreated only the container while
  preserving the same eight named volumes. Both providers, both combined-CA
  environment paths, the exact image digest, CUDA 12.8 selection/kernel probe,
  readiness, no-fallback state, and `127.0.0.1:5238` binding persisted.
- After Docker health returned to `healthy`, a real Google request completed
  one estimate request and one detection request in 9.28 seconds with eight
  detections, eight selected results, eight addresses, five visible overlays,
  and zero page errors. Runtime logs again bound both models to CUDA with no
  CPU fallback marker.

Only safe status codes, counts, public identities, and runtime facts are
retained. Provider keys, request URLs/bodies, AOI coordinates, console text,
certificate identities, screenshots, and export payloads are not acceptance
evidence. All stock browser-run directories were removed after their safe
facts were reduced into this record, and the sanitized runner removed its own
temporary downloads.

Verdict for exact-browser-downloaded RC9 Docker CUDA first-host acceptance:
`PASS`. All four exact-browser-downloaded RC9 first-host profiles now pass.
Still open: final-candidate reboot persistence and independent-host four-
profile reproduction.

## Exact Browser-Downloaded RC9 Docker Reboot Persistence

**Recorded**: 2026-10-13
**Scope**: `FIRST-HOST-LOCAL`, Windows reboot with both exact RC9 Docker
profiles active. This closes the Docker half of final-candidate reboot proof;
Podman reboot persistence and independent-host reproduction remain.

### Automatic restore result

- Windows rebooted at approximately 13:54 local time. Docker Desktop restored
  both package containers automatically after startup; neither package start
  wrapper was rerun.
- CPU and CUDA containers returned `healthy` and readiness `ready` with exact
  image digests, source revision
  `b3431cf86d8a000462df487685104558ac7becd3`, assets `ok`, both providers,
  both combined-CA environment paths, loopback-only ports `5237` and `5238`,
  and exactly eight named volumes per profile.
- CPU again selected CPU with no fallback. CUDA again selected CUDA 12.8 on
  `sm_120`, passed its CUDA kernel probe, and reported no fallback reason.

### Post-reboot live-provider result

- Docker CPU Google returned eight detections, eight selected results, eight
  addresses, and five visible overlays; Azure returned 14 detections, 14
  selected results, 14 addresses, and nine visible overlays.
- Docker CUDA repeated the same Google and Azure result counts. All four runs
  completed one estimate request and one detection request with zero page
  errors.
- Runtime logs bound CPU YOLOv5 and EfficientNet to CPU with no CUDA marker,
  and bound CUDA YOLOv5 and EfficientNet to CUDA with no CPU fallback marker.

Only the safe facts above are retained. Provider keys, request URLs and
bodies, AOI coordinates, console text, screenshots, and raw browser/network
artifacts are not acceptance evidence. All four post-reboot stock browser-run
directories were deleted after reduction into this record.

Verdict for exact-browser-downloaded RC9 Docker reboot persistence: `PASS`.

## Exact Browser-Downloaded RC9 Podman Reboot Persistence

**Recorded**: 2026-10-13
**Scope**: `FIRST-HOST-LOCAL`, Windows reboot with both exact RC9 Podman
containers retained in the documented stopped state. This closes the first-
host final-candidate reboot matrix; independent-host reproduction remains.

### Retention and manual restore result

- Before reboot, the exact CPU and CUDA application containers were stopped
  directly without removal. All 16 named volumes and both container identities
  were retained; Docker Desktop remained closed.
- Windows rebooted at approximately 14:36 local time. The default
  `podman-machine-default` machine returned to `running`; Docker remained
  unavailable. Both original application container IDs remained present and
  stopped with eight volumes each.
- The two exact RC9 pods were started manually with `podman pod start`; no
  package setup, image pull, container recreation, or volume import occurred.
  The unrelated `towerscout-task103` machine and older RC8 pod were untouched.
- Both containers returned `healthy` and readiness `ready` with exact image
  digests, assets `ok`, both providers, both combined-CA environment paths,
  and their original CPU/CUDA device selections. CUDA 12.8 again passed its
  kernel probe with no fallback reason.

### Post-reboot live-provider result

- Podman CPU Google returned eight detections, eight selected results, eight
  addresses, and five visible overlays; Azure returned 14 detections, 14
  selected results, 14 addresses, and nine visible overlays.
- Podman CUDA repeated the same Google and Azure result counts. All four runs
  completed one estimate request and one detection request with zero page
  errors.
- Runtime logs bound CPU YOLOv5 and EfficientNet to CPU with no CUDA marker,
  and bound CUDA YOLOv5 and EfficientNet to CUDA with no CPU fallback marker.

Only the safe facts above are retained. Provider keys, request URLs and
bodies, AOI coordinates, console text, screenshots, and raw browser/network
artifacts are not acceptance evidence. All four post-reboot stock browser-run
directories were deleted after reduction into this record.

Verdict for exact-browser-downloaded RC9 Podman reboot persistence: `PASS`.
All first-host browser-download and reboot-persistence cells now pass; only
independent-host four-profile reproduction remains open.

## RC9 Independent NVIDIA Host Intake

**Recorded**: 2026-10-14
**Host ID**: `INDEP-HOST-01`
**Verdict**: `PASS_WITH_RELEASE_BLOCKERS`

The independently supplied report and sanitized extracts substantiate Docker
CPU/CUDA and Podman CPU/CUDA setup, real model/device execution, Azure/Google
workflows with matching detection fingerprints, cancellation/retry,
controlled recovery, exports, stop/relaunch, and reboot against the exact RC9
public identities.

The sanitized evidence ZIP remains outside the repository. Its SHA-256 is
`39a4052a5ac2bb99ba994453b39980b5688ecb0d8586e1827e811fb92c588145`.
All 80 entries were readable, all 42 JSON files parsed, and all 78 index
manifest rows matched byte lengths and hashes. A redacting scan found no
provider keys, tokens, private keys, unredacted Windows user paths, or
coordinate pairs.

The run also reproduced a fresh Podman GPU image-pull timeout, a Docker/Podman
login race, a PowerShell 7 provider-installer hashing failure, unsafe partial
retry behavior, a misleading global provider check, browser multiple-download
blocking, and smaller wording/reproducibility findings. Complete click-by-click
UI execution was limited to Docker CPU. A CPU-only host, second NVIDIA host,
and Podman installation without Docker Desktop remain required.

The full sanitized intake, ten finding dispositions, correction plan, and
next `v0.1.3-rc.N` candidate acceptance gates are recorded in
`../TASK-105/RC9-INDEPENDENT-HOST-EVIDENCE-INTAKE-2026-10-14.md` and
`../TASK-105-final-release-correction-and-qualification.md`. RC9 remains an
immutable validation prerelease and is not eligible for stable/Latest
promotion.

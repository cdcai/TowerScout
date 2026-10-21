# RC9 Independent-Host Evidence Intake

**Recorded**: October 14, 2026
**Owning task**: TASK-105
**Evidence host**: `INDEP-HOST-01`
**Custody**: Source report, raw evidence, and sanitized evidence ZIP remain
outside the repository under the release owner's custody.

## Evidence identities

- Report filename: `RC9-INDEPENDENT-HOST-REPORT-2026-10-13.md`
- Sanitized ZIP filename:
  `RC9-INDEPENDENT-HOST-SANITIZED-EXTRACTS-2026-10-13.zip`
- Sanitized ZIP SHA-256:
  `39a4052a5ac2bb99ba994453b39980b5688ecb0d8586e1827e811fb92c588145`
- ZIP inventory: 80 readable entries consisting of 78 sanitized extracts,
  one index, and one report copy.
- JSON validation: all 42 JSON entries parsed successfully.
- Internal evidence manifest: all 78 rows matched their recorded byte lengths
  and SHA-256 values.
- The report copy inside the ZIP matched the separately supplied report.

## Bound release identities confirmed in the extracts

- Accepted RC9 source:
  `b3431cf86d8a000462df487685104558ac7becd3`
- CPU image:
  `sha256:9d24cc71724953fba7e062b6ee71dac38f2ec413716a9b60bfaf8ad0be20c950`
- CUDA 12.8 image:
  `sha256:c2d99f178465a8cdc83430092554d98aeb181797ff330fba2661bc95a45d8287`
- CPU control ZIP SHA-256:
  `66e674ef28d98835a981bd731bc7a86e7c6bdd07cb9ea964d47e4e9c63cfacfc`
- CUDA 12.8 control ZIP SHA-256:
  `5157a3a396502e524b16dd5eda6cf46aa80521ba4409546af8625f1ca43cad10`
- Shared asset ZIP SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`

## Sanitization review

The read-only review found zero matches for Google key patterns, explicit
provider-key assignments, bearer/GitHub tokens, private keys, key-bearing URL
parameters, unredacted Windows user paths, or coordinate pairs. Apparent IPv4
matches were dotted software/kernel version strings rather than host network
addresses. The archive intentionally omits `.env` contents, provider
responses, screenshots, exports, raw container logs, raw GPU sample CSVs, and
the reviewer's working run log.

No binary evidence ZIP, raw log, credential, certificate identity, private
AOI, screenshot, or provider response is committed with this intake.

## Supported result

The extracts materially substantiate a four-profile pass on one independent
NVIDIA Windows host:

- Docker CPU, Docker CUDA, Podman CPU, and Podman CUDA completed shipped-wrapper
  setup against the exact RC9 identities.
- CPU profiles ran YOLO and EfficientNet on CPU with no fallback.
- CUDA profiles ran YOLO and EfficientNet on CUDA 12.8/`sm_75` with no fallback;
  GPU sampling recorded real utilization and memory growth.
- Fixed-area Azure and Google detection counts/fingerprints matched across
  profiles and after relaunch/reboot.
- Provider configured-state booleans persisted without retained key values.
- Cancellation/retry, controlled recovery, exports, stop/relaunch, and reboot
  were exercised, subject to the deviations below.
- The frontend normalized fingerprint matched across CPU/CUDA after removing
  the generated bundle build-date line.

This is supporting evidence, not the complete v2 independent-host gate.

## Deviations and remaining gaps

- Complete click-by-click UI execution was performed only for Docker CPU;
  several workflow steps for the other profiles used a reviewer-side HTTP
  driver against the same served frontend/runtime.
- The reviewer used Python 3.13.6 rather than the documented tested Python 3.12.
- The tester switched Podman from rootful onboarding state to the supported
  rootless path before profile testing.
- Provider installation required an undocumented `-Force` retry after the
  PowerShell/module-path failure.
- Docker required manual host-runtime recovery after the Podman/Docker login
  race.
- The Task-098 fixed combined probe, injected fault set, explicit
  CUDA-unavailable negative, managed-network TLS repair, dataset restore/manual
  additions, and warm-median performance were not completed by this run.
- A CPU-only host, a second NVIDIA host, and a Podman installation without
  Docker Desktop remain required by the v2 allocation.

## Confirmed findings owned by TASK-105

1. Fresh Podman GPU provisioning reports failure when the large image pull
   exceeds the fixed 60-second container-smoke timeout.
2. Docker Desktop and Podman Desktop can race for the Docker pipe at login;
   factory reset would risk named-volume loss.
3. A PowerShell 7 parent can cause the Windows PowerShell child to miss
   `Get-FileHash` through inherited module lookup.
4. The failed provider install leaves partial package-local state that blocks
   an ordinary documented retry.
5. A global `podman compose version` check can report Docker Desktop Compose
   even though TowerScout correctly selects its package-local provider.
6. A late GPU cancellation can finish server-side; source inspection indicates
   the frontend discards cancelled/stale results, which still needs a focused
   regression.
7. Edge can block the second automatic results download, while the application
   reports success; KML is emitted with a CSV media type.
8. Geocoding-limit wording can imply the wrong provider and does not explain
   coordinate-only results clearly.
9. Rootful Podman/Python 3.13 observations and the missing release-notes GPU
   list require support-boundary clarification, not automatic support expansion.
10. CPU/CUDA bundles differ in generated build-date metadata; ZIP entry names
    use Windows separators.

## Intake verdict

`PASS_WITH_RELEASE_BLOCKERS`:

- Accept the four-profile result for this one independent NVIDIA host.
- Preserve RC9 as an immutable validation prerelease.
- Do not promote RC9 to stable/Latest.
- Resolve or explicitly accept every finding under TASK-105, rebuild under a
  new intended final identity, and complete the remaining host allocation
  before the final release claim.

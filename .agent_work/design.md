# TowerScout Current Technical Design

**Last Updated**: October 8, 2026
**Scope**: Main-based Windows deployment delivery, four-profile runtime
qualification, and cdcai handoff through October 2026
**Archived Pre-Rebaseline Design**:
[`2026-07-23-pre-rebaseline-design.md`](./context/archive/2026-07/2026-07-23-pre-rebaseline-design.md)

## Current Architecture

TowerScout is a Flask web application packaged as an OCI-compatible local
application for Windows 11 AMD64. The normal user path is a GitHub Release
control package plus a digest-pinned GHCR image and a shared checksummed Model &
Data Package.

The application includes:

- Flask routes, filesystem-backed sessions, setup/settings, provider
  validation, detection, progress/cancel, export, restore, and readiness.
- Google Maps and Azure Maps frontend/backend provider paths.
- YOLOv5 primary detection plus EfficientNet secondary classification.
- Named volumes for configuration, model/data assets, logs, sessions, uploads,
  cache, and working data.
- Windows launch/setup/status/log/stop/import/TLS support scripts.
- Docker- and Podman-compatible Compose execution.

## Release And Repository Topology

### During Candidate Development

- `J-Schulein/TowerScout` hosts the immutable `v0.1.2` pilot.
- The same fork is the development and validation surface for
  `v0.1.3-rc.N` candidates.
- `cdcai/TowerScout` remains unchanged.

### At Final Adoption

- The cdcai owner and project lead select the official tag and display title.
- The official image, package, manifests, checksums, and documentation are
  built consistently for that identity.
- The official release is published from cdcai only after qualification and
  explicit adoption approval.
- The fork remains available as pilot and provenance history.

## Windows Host-Script Trust Boundary

ADR-023 selects an unsigned Windows control package. The supported user path is
the supplied `.cmd` and `.bat` entrypoints, which invoke Windows PowerShell 5.1
with a process-scoped execution-policy setting. That setting does not change
persistent machine policy and does not override WDAC, AppLocker,
constrained-language, antivirus/EDR, or organization-specific allowlisting.

The standard package therefore supports only endpoints where the user and
organization already permit that wrapper path. Signature-enforcing managed
endpoints require site approval, allowlisting, or internal signing and are not
part of the standard support claim. Artifact trust is anchored in the
authoritative release record, exact SHA-256 values, internal checksums, source
identity, and digest-pinned OCI images. Clean-machine validation begins with a
real browser download and verifies the official hash before extraction or
unblocking.

## Runtime Profiles

The final supported matrix contains four profiles:

| Engine | Compute | Required qualification |
| --- | --- | --- |
| Docker | CPU | Normal CPU package setup, readiness, provider, detection, persistence, and stop |
| Docker | GPU | CUDA package plus selected-engine NVIDIA validation and CUDA readiness |
| Podman | CPU | Running Podman machine plus approved non-Docker-Desktop Compose provider |
| Podman | GPU | Podman WSL2 machine, NVIDIA host support, CDI, approved Compose provider, and CUDA readiness |

The profiles are equally supported once their documented prerequisites are met.
This final-candidate target does not retroactively change the narrower support
wording of the frozen `v0.1.2` pilot.

## Provider TLS Design Boundary

The current release uses the existing command-based provider TLS workflow.
W04 may repair only reproduced transactional defects: capture scalar child
status, build a unique candidate bundle, verify it before configuration
promotion, preserve prior trust and unrelated environment bytes on failure,
and exclude concurrent repair. The PR #67 launcher/helper design remains
preserved and deferred. Podman-machine image-pull/build TLS remains a separate
runtime/organization concern owned by Task-097 qualification.

## Exit/Stop Design Boundary

The current release uses the package's command-based stop/start/status/logs
workflow for Docker and Podman. It must address the selected installation,
preserve all named volumes, and report failure truthfully. Task-096's browser
Exit/helper design remains deferred with no automatic restart date.

## Detection Cancellation Readiness Boundary

The process-wide detection lock is the authoritative next-request readiness
boundary. `/abort` signals the active run and returns promptly. HTTP `200` with
`retryReady=true` means the slot is already free; HTTP `202` with
`retryReady=false` means the current model step still owns it. The frontend
then polls `/api/detection/progress`, whose `retryReady` value is derived from
the same lock, and keeps its progress overlay and cancellation-pending
admission guard active until the run is terminal and the slot is free. This is
bounded hardening of the existing synchronous detection path, not the deferred
Task-058 background-job architecture.

Each browser detection request also carries a short-lived, per-page request
identity on both `/getobjects` and `/abort`. If cancellation arrives before
the matching run is registered, the progress tracker retains a bounded
cancellation tombstone for that request only. A delayed matching request is
then rejected before provider or model work, while a retry with a new identity
can proceed. The identity is internal correlation metadata and is not exposed
in the public progress response.

## Podman Qualification Boundary

Task-097 owns:

- CPU and GPU/CDI qualification.
- Docker-Desktop-free Compose-provider selection and installer fallback.
- Setup, launch, stop, status, logs, asset import, persistence, provider TLS,
  and Exit/Stop checks.
- Managed-network image-pull and source-build TLS investigation.
- A pass/fix/documented-limitation decision before final freeze.

Task-097 must not silently expand the product UI to install Compose providers
or modify Podman-machine trust.

## Dependency Security Boundary

Task-090 and Task-098 completed the 62-alert Trivy baseline classification,
approved remediation, and affected-runtime qualification. PR #51 merged as
`e499b50`. That July 27 closeout remains historical and complete.

GitHub disclosed four additional Dependabot advisories on August 4-5, followed
by reviewed npm advisory `GHSA-5p4m-2wfm-xmqj` entering the blocking audit on
August 7. Task-099 is the separate, narrow release-gate follow-up; it does not
reopen Task-098 or expand into the qualified ML runtime.

The current security boundary is:

1. Loopback publication and content-sniffed custom-image validation protect
   the normal local runtime.
2. Release-model hashes are enforced by default; model upload remains disabled
   by default and requires both an administrator key and approved SHA-256 hash
   when enabled.
3. ADR-022 selects `torch==2.10.0` / `torchvision==0.25.0` for distinct `cpu`
   and `cuda128` images. Task-103 has qualified the pair locally on CPU,
   Turing, and Blackwell; the documentation-aligned rebuild and final
   independent-host release evidence remain open.
4. The prior `torch==2.6.0` / `torchvision==0.21.0` Task-098 pair and its
   July advisory disposition remain historical evidence, not the current
   candidate runtime. Future upgrades must continue to move torch and
   torchvision together and repeat CPU/CUDA, model-load, output-parity, and
   performance validation.
5. Task-099 updated runtime `aiohttp` from `3.14.2` to `3.14.3` for alert
   `#74` and development-only transitive `ip-address` from `10.2.0` to
   `10.3.1` for alerts `#72`, `#73`, and `#75`.
6. Task-099 also updated development-only transitive `js-yaml` from `4.3.0`
   to `4.3.1` for `GHSA-5p4m-2wfm-xmqj`; the repository inventory had not
   assigned that new audit finding an alert number at the August 7 check.
7. PR #68 merged the narrow fixes as `f460445`; PR #69 merged the root graph
   refresh as `0133b50`. Graph run `31510493332` removed stale
   `aiohttp==3.14.2`, alert `#74` closed without dismissal, and the repository
   returned at its August 11 closeout to the eight documented medium/low torch
   residuals with no open critical/high alert.
8. All-severity SARIF reporting remains advisory, while new or reintroduced
   critical/high dependency findings are blocking unless covered by a narrow,
   unexpired exception. The Task-099 discovery confirms that ratchet is
   operating as designed.
9. Dependabot alert `#76` opened after Task-099 for high-severity
   development-transitive `extract-zip==2.0.1` through
   `puppeteer@24.19.0 -> @puppeteer/browsers@2.10.8 -> extract-zip`.
   It is not present in the shipped Python runtime image or normal-user Windows
   package, but the maintained browser-install path can execute it.
10. Task-101 established Node `>=22.12.0`, exact
    `puppeteer@25.8.0`, and `@puppeteer/browsers@3.2.1`. The resulting lock
    and installed graphs contain no `extract-zip`, and the blocking audit is
    clean. Final PR #72 CI/CD run `32308971393` and Task-087 run `32308971392`
    passed at `820b649`; PR #72 squash-merged as `0cc189c`. Exact-main CI/CD
   run `32310281115` and Task-087 run `32310281051` passed, and alert `#76`
   closed as fixed without dismissal. ADR-021 supersedes the former downstream
   PR #67 integration gate; no PR #67 reconciliation is required for the
   main-based delivery, and Task-087 remains preserved and deferred.
11. ADR-024/TASK-104 preserve the 396-key image baseline unchanged while
    removing unused Debian `gdal-bin` and accepting only five exact,
    version/class/type/flavor-bound residuals through October 31, 2026. The
    comparator rejects incomplete scans, identity mismatches, severity
    escalation, unknown policy fields, duplicates, expired/mismatched/unused
    residuals, and any other new HIGH/CRITICAL key. The container workflow
    builds and scans locally before registry authentication or push, verifies
    the published manifest's config digest against the scanned local image ID,
    rescans the exact published digest, and promotes `latest` only after that
    confirmation and separate owner authorization.

## Task Dependency Flow

```text
TASK-095 Phase A rebaseline
        |
        v
TASK-090 bounded security investigation [COMPLETE]
        |
        v
TASK-098 dependency-security remediation/disposition gate [COMPLETE]
        |
        v
TASK-099 August advisory follow-up [COMPLETE]
        |
        v
TASK-101 extract-zip advisory gate [COMPLETE ON ACCEPTED MAIN]
        |
        v
ADR-021 / W00 main-based direction
        |
        +--> TASK-087 / PR #67 and TASK-096 [PRESERVED, DEFERRED]
        |
        v
ADR-022 / TASK-103 torch 2.10.0 cpu + cuda128 bridge
        |
        v
ADR-024 / TASK-104 bounded RC5 security correction
        |
        v
TASK-091 + TASK-097 early package and Podman qualification
        |
        v
ADR-023 unsigned package boundary
        |
        v
TASK-091/092/093 qualification, packaged docs, and recovery
        |
        +--> TASK-094 only if pilot/support evidence justifies it
        |
        v
Final candidate freeze -> owner qualification -> TASK-089 adoption/handoff
```

Task-095 Phase B spans the remaining work to keep governance, backlog, and
handoff material current. Task-098 is separately scoped from Task-090 so the
investigation cannot hide dependency upgrades, CPU/CUDA compatibility work, or
four-profile regression effort. Task-099 preserved the same governance
principle for post-closeout disclosures and cleared its scoped dependency-
security gate on August 11. Task-101 closed alert `#76` through the accepted
default-branch graph and is complete. ADR-021 supersedes its former downstream
PR #67 gate. Task-087 and PR #67 remain preserved historical work outside this
delivery window. Task-058 and Task-059 are also deferred beyond W00-W10 and may
enter a future dependency flow only under separately authorized owner planning.

## Validation Strategy

Automated validation covers unit, route, frontend contract, packaging, and
security checks where practical. Manual evidence remains required for:

- Windows package behavior
- Docker and Podman runtime behavior
- CPU/GPU execution
- managed-network provider TLS
- live-provider browser behavior
- asset-backed package smoke
- owner-operated release and recovery rehearsal
- browser-downloaded unsigned ZIP behavior, downloaded-file marking, official
  hash verification, and ordinary-user wrapper execution

State the selected engine/profile before runtime-dependent validation and
verify actual availability. When the current session grants W00-W10
implementation scope, routine checks may continue without repeated approval;
unavailable engines or restart requirements are recorded as blockers while safe
non-runtime work continues.

## Safety Boundaries

- Do not mount Docker or Podman control sockets into the application container.
- Do not accept browser-supplied command text or executable paths.
- Do not record provider keys, helper tokens, local certificate details, raw
  browser traces, private AOIs, or unsanitized logs in repository evidence.
- Do not delete named volumes during normal stop, upgrade, or container
  replacement.
- Do not mutate `v0.1.2` or publish `v0.1.3` final prematurely.
- Do not change cdcai before explicit owner authorization.
- Do not instruct users to disable endpoint protection, weaken persistent
  execution policy, or override an organizational application-control rule.

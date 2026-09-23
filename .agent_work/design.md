# TowerScout Current Technical Design

**Last Updated**: September 22, 2026
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
3. The selected `torch==2.6.0` / `torchvision==0.21.0` pair is qualified for
   the Task-098 CPU/CUDA boundary.
4. The July 27 closeout left eight medium/low torch advisories visible and
   non-reachable on supported paths. A future upgrade must move torch and
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
TASK-091 + TASK-097 early package and Podman qualification
        |
        v
TASK-091/092/093 qualification, docs, and recovery
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

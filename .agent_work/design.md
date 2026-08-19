# TowerScout Current Technical Design

**Last Updated**: August 19, 2026
**Scope**: Fix-first candidate development, four-profile runtime qualification,
and cdcai handoff through October 2026
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

Task-087 owns guided repair for application-provider TLS:

1. Setup/Settings classifies a repairable Google or Azure certificate trust
   failure.
2. The browser may request only an allowlisted repair operation.
3. A package-local Windows helper binds to loopback and validates origin,
   short-lived credentials, provider, engine, GPU mode, and confirmation.
4. The helper calls TowerScout-owned scripts with fixed argument arrays.
5. The selected engine's persistent config volume receives the combined CA
   bundle.
6. TowerScout restarts with the captured runtime profile.
7. The command-based Task-086 repair remains available.

Podman-machine image-pull/build TLS is outside this application-provider flow
and belongs to Task-097.

## Exit/Stop Design Boundary

Task-096 will reuse the secured host-control pattern without exposing Docker or
Podman sockets to the application container.

Expected sequence:

1. User selects Exit/Stop TowerScout.
2. UI explains that TowerScout will stop while saved data remains.
3. User confirms.
4. The host helper validates the request and captured runtime profile.
5. The package-local stop path runs for Docker or Podman.
6. The container is removed without deleting named volumes.
7. The browser shows a final status or manual fallback when the helper cannot
   complete.

Exact endpoint and lifecycle details remain Task-096 design work.

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
10. Active Task-101 has locally validated Node `>=22.12.0`, exact
    `puppeteer@25.8.0`, and `@puppeteer/browsers@3.2.1`. The resulting lock
    and installed graphs contain no `extract-zip`, and the blocking audit is
    clean. PR #72 CI/CD run `32300398378` and Task-087 compatibility run
    `32300398377` pass at implementation head `a87ab53`. Any later PR #72 head
    still requires final checks before merge. Default-branch alert
    reconciliation and PR #67 integration/exact-head validation remain open;
    Task-087 stays preserved and paused until those gates pass.

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
TASK-101 extract-zip advisory gate [IN PROGRESS]
        |
        v
TASK-087 universal provider TLS repair [PAUSED]
        |
        v
TASK-096 user Exit/Stop
        |
        v
TASK-097 Podman CPU/GPU qualification
        |
        +--> TASK-058 only if schedule and risk gates pass
        |          |
        |          +--> TASK-059 only if remaining margin is safe
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
security gate on August 11. Task-101 now owns alert `#76`; Task-087 remains
reviewable but paused until Task-101 restores the blocking frontend gate.

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

No runtime-dependent validation should begin until the user has been told which
runtime is needed and has confirmed Docker Desktop and/or Podman is running.

## Safety Boundaries

- Do not mount Docker or Podman control sockets into the application container.
- Do not accept browser-supplied command text or executable paths.
- Do not record provider keys, helper tokens, local certificate details, raw
  browser traces, private AOIs, or unsanitized logs in repository evidence.
- Do not delete named volumes during normal stop, upgrade, or container
  replacement.
- Do not mutate `v0.1.2` or publish `v0.1.3` final prematurely.
- Do not change cdcai before explicit owner authorization.

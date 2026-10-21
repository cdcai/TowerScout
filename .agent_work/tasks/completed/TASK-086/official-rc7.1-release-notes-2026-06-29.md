# TowerScout v0.1.0-rc7.1

This prerelease replaces `v0.1.0-rc7` for tester-facing RC7 validation. Use
this package set instead of the original `v0.1.0-rc7` artifacts.

## Assets

- `towerscout-v0.1.0-rc7.1-cpu.zip`
- `towerscout-v0.1.0-rc7.1-cpu.zip.sha256`
- `towerscout-v0.1.0-rc7.1-cuda121.zip`
- `towerscout-v0.1.0-rc7.1-cuda121.zip.sha256`
- `towerscout-v0.1.0-rc7.1-assets-towerscout-v1-assets-2026-05-05.zip`
- `towerscout-v0.1.0-rc7.1-assets-towerscout-v1-assets-2026-05-05.zip.sha256`

## What Changed Since v0.1.0-rc7

- Fixed the Podman TLS CA import fallback so it reuses the shared Compose
  container lookup helper and honors `COMPOSE_PROJECT_NAME` from the environment
  or package `.env`.
- Fixed Azure keyless TLS status probing so Azure HTTP 400 responses from the
  attribution endpoint are treated as TLS-reachable, matching the TLS import
  verifier.
- Fixed managed-network imagery download errors so TLS CA repair details and
  the provider repair command are preserved instead of being reduced to a
  generic missing-imagery message.

## Artifact Identity

| Artifact | SHA-256 / Digest |
| --- | --- |
| CPU package ZIP | `bf104a1136722eee971302ce4bdc2ebc02ebb21031ee4d911dea908155336228` |
| CUDA 12.1 package ZIP | `507ca553aebf797218fccba61d821e262f06eb2e3801f0a73ef54230af524935` |
| Shared asset ZIP | `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb` |
| CPU image | `ghcr.io/j-schulein/towerscout:v0.1.0-rc7.1-cpu@sha256:14b6ef523f93a91bbcceef4163b2d100a3b8c3f0b32bfdc6b91c362694ae3d09` |
| CUDA 12.1 image | `ghcr.io/j-schulein/towerscout:v0.1.0-rc7.1-cuda121@sha256:95f1f3967294957543ed0c40e11531a5af2d56f2beb7723973596b952fc39ffd` |
| Source ref | `1152c16fede6e852e37603a90d4ec9d9626c0e71` |

## Validation

- Main CI for `1152c16fede6e852e37603a90d4ec9d9626c0e71` passed.
- CPU and CUDA 12.1 GHCR image publish workflows passed.
- Control ZIP structure checks passed for CPU and CUDA packages.
- Release manifest checks passed for CPU and CUDA packages.
- Internal package `SHA256SUMS.txt` validation passed for CPU and CUDA packages.
- External `.sha256` sidecar validation passed for CPU, CUDA, and shared asset
  ZIPs.
- Package hygiene scan found no blocked runtime, support, secret, certificate,
  cache, session, log, upload, or temp artifacts.
- Post-publication downloaded-artifact validation passed on Docker CPU by the
  release owner and on Docker GPU by a teammate. Evidence is recorded as a
  support-safe summary only.

## Support Notes

- The CPU package remains the default tester path.
- The CUDA 12.1 package remains a support-assigned path for validated NVIDIA
  hosts.
- If Google or Azure provider validation fails on a managed network, use the
  package TLS repair command shown by TowerScout or the relevant user guide.

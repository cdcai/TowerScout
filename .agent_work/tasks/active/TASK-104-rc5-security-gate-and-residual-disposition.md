# TASK-104: RC5 Security Gate And Residual Disposition

**Status**: IN_PROGRESS - owner selected the fastest safe path on October 7,
2026; implementation is active on `fix/rc5-fast-safe-security-gate`
**Priority**: CRITICAL
**Type**: C (Release Security / Container Publication)
**Owner**: `J-Schulein` until handoff; `cdcai` thereafter
**Decision**: [ADR-024](../../decisions/024-rc5-security-gate-and-residual-boundary.md)
**Depends on**: TASK-103, PR #96 merge `b0725e750c1541e7cb60df881d3906f761657089`

## Objective

Remove the unused Debian GDAL dependency, enforce exact time-bounded residual
matching, and prevent an unqualified image from being pushed before the local
security gate passes. Preserve the accepted 396-key baseline unchanged.

## Required Outcome

- CPU and CUDA 12.8 images contain neither Debian GDAL/libheif nor the
  transitively installed Debian Python packages.
- Fiona loads the packaged ZCTA shapefile through its bundled GDAL library.
- The application imports `urllib3==2.8.0`; only pip's private 2.7.0 inventory
  may match the two approved urllib3 residuals.
- Only the exact two urllib3 and two OpenSSL package keys in the residual file
  may pass, and only through October 31, 2026.
- Missing/empty scans, wrong image/source/flavor identity, severity escalation,
  unknown fields, expiry, duplicates, mismatches, and unused exceptions fail
  closed.
- The workflow scans locally before GHCR login/push, proves registry config
  identity after the immutable push, rescans the exact digest, and promotes
  `latest` only after confirmation.

## Execution Checklist

- [x] Record ADR-024 and the exact residual schema/entries.
- [x] Pin base-image indexes and pip; remove `gdal-bin`.
- [x] Implement the fail-closed comparator and regression coverage.
- [x] Reorder the publish workflow and add parsed workflow ratchets.
- [ ] Pass focused tests, full required CI, `git diff --check`, and strict
  `.agent_work` validation.
- [ ] Build local CPU and CUDA 12.8 images from one exact source revision.
- [ ] Verify package inventory, Fiona linkage, ZCTA lookup, real model/device
  work, and retained scan/SBOM evidence for both flavors.
- [ ] Obtain reviewed merge and green exact-head/post-merge CI.
- [ ] After separate owner dispatch authorization, publish immutable versioned
  images with `push_latest=false` and confirm exact-digest G10 evidence.
- [ ] Assemble digest-pinned packages and complete the final browser-download
  and independent-host four-profile matrix under Tasks 091/092/093/097/103.

## Stop Conditions

- Any new unaccepted HIGH/CRITICAL key or severity escalation.
- A residual package/version/identity mismatch or expired/unused entry.
- Fiona resolves to system GDAL, ZCTA lookup fails, or model/device behavior
  changes.
- A local scan and registry config/image identity cannot be reconciled.
- A required host, provider account, frozen asset, or exact artifact identity
  is unavailable; record `blocked`, never `pass`.

## Publication Boundary

Implementation, local builds, and local validation are authorized. GHCR
dispatch, package/release publication, and `latest` promotion remain separate
owner actions. The full support claim still requires all four profiles and
independent-host reproduction.

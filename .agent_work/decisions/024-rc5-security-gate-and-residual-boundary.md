# ADR-024: RC5 Security Gate And Time-Bounded Residual Boundary

**Status**: Accepted
**Date**: October 7, 2026
**Owner**: `J-Schulein` until project handoff; `cdcai` thereafter
**Scope**: RC5 runtime dependencies, Task-103 Trivy enforcement, GHCR publish
ordering, and final release qualification

## Decision

1. Remove the unused Debian `gdal-bin` package from the runtime image. This is
   an approved, security-driven exception to Task-103's prior image-slimming
   exclusion. Keep the Fiona/GeoPandas ZIP-code path and prove it uses Fiona's
   bundled GDAL library with the packaged ZCTA shapefile.
2. Keep pip in the RC5 image and pin the build-installed version to `26.2.1`.
   TowerScout's application dependency remains `urllib3==2.8.0`.
3. Keep the committed 396-key Task-103 baseline unchanged. Do not regenerate
   or broaden it to make RC5 pass.
4. Accept only four exact HIGH residual keys through
   `.github/security/task103-accepted-residuals.v1.json`: the two pip-private
   `urllib3==2.7.0` keys and the `libssl3`/`openssl`
   `3.0.22-1~deb12u1` keys for `CVE-2026-84782`.
5. Every residual expires at `2026-10-31T23:59:59Z`. A changed package ID,
   installed version, package class/type, severity, flavor, missing match, or
   expiry blocks publication. `J-Schulein` owns the current disposition;
   maintenance ownership transfers to `cdcai` at handoff.
6. The comparator must fail closed on degraded scans, wrong image/source/flavor
   identity, unknown policy fields, duplicate or unused residuals, and baseline
   severity escalation.
7. Build and scan the local candidate before GHCR login or push. Push the
   immutable versioned tag only after the local gate passes, verify that the
   registry manifest references the same config/image ID, then rescan the exact
   published digest. Promote `latest` only after that confirmation passes and
   the owner separately authorizes it.

## Rationale

The active TowerScout interpreter is CPython 3.11.17, which includes fixes for
`CVE-2026-19445` and `CVE-2026-19553`. The scanner's eight Python package keys
belong to a second Debian Python installation pulled in by `gdal-bin`.
Fiona 1.10.1 carries its own GDAL library and TowerScout does not invoke Debian
GDAL command-line tools, so removing that package eliminates unnecessary code
instead of accepting it.

The two `urllib3` keys identify pip's private 2.7.0 copy; TowerScout imports the
separately pinned 2.8.0 distribution. The remaining OpenSSL key affects DTLS
retransmission, while TowerScout exposes supported HTTPS client workflows and
no DTLS workflow. Debian Bookworm has no fixed package for this candidate.
Those four records therefore receive a narrow, expiring acceptance rather than
becoming permanent baseline entries.

## Consequences

- Task-104 is the unique SEC-001 follow-up and owns implementation/evidence.
- Existing exact-image Task-103 and Task-097 results remain historical. New
  CPU/CUDA images and all final package identities require qualification.
- A new HIGH/CRITICAL key, severity increase, incomplete scan, or identity
  mismatch remains a release blocker even when the four residuals match.
- If a fixed pip or Debian package appears before dispatch, remove the matching
  residual and rebuild; do not retain an unused exception.
- Pip-free images, a Debian distribution migration, and general image slimming
  remain outside this release path.

## Publication Boundary

This decision authorizes implementation and local validation. It does not
authorize GHCR dispatch, package/release publication, `latest` promotion, or a
full readiness claim. Those actions remain separately owner-gated and depend
on the exact browser-download and independent-host acceptance matrix.

## Review Triggers

Review immediately if any residual becomes CRITICAL, changes package/version,
gains a supported-path call chain, obtains an upstream fix, or reaches its
expiry. Any publication after October 31, 2026 requires a new written owner
decision.

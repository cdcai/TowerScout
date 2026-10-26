# Release notes and qualification boundary

Use the authoritative release record and the included `release-manifest.v1.json` for the exact version,
source revision, CPU/CUDA flavor, image digest, package hashes and qualification results.
This source document does not declare a new official artifact qualified or published.

## Changes prepared for this release

- Retain Windows Docker/Podman CPU and NVIDIA CUDA 12.8 profiles with separate digest-pinned packages.
- Remove the unsafe file-deletion endpoint and its active frontend caller; constrain Host to localhost/IPv4 loopback and reject foreign-Origin, cross-site and same-site browser requests. These controls are not authentication or an XSS defense.
- Preserve files in the uploads volume when the application starts or its container is replaced; startup no longer clears that durable directory.
- Align KML and dataset selection with the UI's primary/secondary confidence threshold; keep CSV's boundary flag factual.
- Protect spreadsheet text, emit UTF-8 CSV, preserve valid XML text and release temporary download URLs.
- Bound dataset restore to 1,000 members, 64 MiB per member and 512 MiB total expanded size; preserve the current session on failed restore.
- Validate publication inputs and exact source, and require the protected release environment before building or registry login.
- Automatic TLS repair selects only signing CA certificates already present in a Windows Root store; other CAs require explicit Local IT approval and selection.

## Installation restrictions

The package is unsigned. Use the supplied wrappers only where the user and organization permit them;
signature-enforcing or organization-allowlisted endpoints are outside the standard support claim.
Compare authoritative hashes before extracting browser-downloaded bytes.
Podman requires a short extraction path (package root at most 80 characters), rootless operation,
and explicitly selected 64-bit Python 3.12. Quit Docker Desktop before Podman runs; preserve volumes during recovery.
CPU-only hardware and Podman without Docker Desktop installed remain unqualified.

Historical tests exercised RTX PRO 500 Blackwell Laptop GPU (`sm_120`) and T1000 (`sm_75`).
Newly built artifacts still require the two-host qualification recorded for their exact identities.
No GPU model name alone qualifies every driver, Windows, WSL, engine or toolkit version.

CSV retains all detection rows with selection/threshold flags; KML exports selected visible results; training datasets retain selected above-threshold labels across full images, including outside-boundary results.
Text beginning with a spreadsheet formula marker is prefixed with an apostrophe for safe opening in spreadsheet software.
Dataset export/restore preserves review data, not the full configuration or container volumes.

Read the [package guide](../package-guide.md), [maintenance boundaries](../maintenance.md),
and [dependency security disposition](../security/dependency-security-disposition.md).

## Review corrections in this source revision

- Preserve repeated dataset export/restore and accept historical re-exports with
  duplicate README copies, while retaining archive path, collision and size checks.
- Generate XML annotations using actual image dimensions, independent of legacy
  metadata flags; decode the stored flag correctly during restore.
- Keep Azure's unconfirmed-boundary warning visible after adding manual towers.
- Update Puppeteer and its locked development graph; retain blocking audit.
- Remove the Windows host-helper listener/worker/entrypoints and their test suite
  from proposed source. The historically named required Windows job continues
  supported package/provider/runtime contracts. No endpoint protection bypass.
- Custom images use session-owned generated URLs. Missing/invalid URLs and upload
  failures now explain retry; GET navigation preserves map export inputs.
- Cancellation uses POST only, with the existing request identity/recovery guard.
- Reject ZIP64 before directory allocation, bound metadata to 8 MiB, normalize
  known cdcai legacy tile ids and label whitespace, project fields and redact
  provider URLs before restore response/persistence. Discard consumed restore ZIPs.
- Manual additions use the completed run boundary; selected manual towers stay
  visible in both modes. Restored datasets lack original polygons, so new manual
  membership is warned as unconfirmed/false. Training export warns about hidden
  selected ML labels. KML uses stored membership/review mode, not current drawings.
- Preserve historical team acknowledgment and dataset paper citation; reconcile
  upstream modification notices and supporting-material AGPL scope.
- Validate restored image/output mappings and image structure before replacing
  a review; reject missing images, conflicting targets and reserved paths.
- Export YOLO/XML labels by stable tile/detection identity, including duplicate
  label text and empty ML selections, with matching contents.txt selection flags.

See maintenance guidance for retention and legacy export limitations. These
changes do not qualify a new image, publish artifacts or execute the cdcai About
description/homepage correction.

# TowerScout Release Asset Bundle Contract

This document defines the V1 RC1 contract for TowerScout runtime assets that are too large or policy-sensitive to keep in git. It is the handoff point between release packaging, end-user package documentation, and clean-machine validation.

## Scope

The V1 RC1 asset bundle covers:

- YOLOv5 detector weights.
- EfficientNet-B5 secondary classifier weights.
- US Census 2025 ZCTA ZIP-code boundary shapefile data.
- A copy of the TowerScout asset manifest used to identify and verify the bundle.

The GitHub Release control package, GHCR image digest, and asset bundle are separate release artifacts. The control package contains the launcher, Compose files, helper scripts, docs, and `webapp/asset_manifest.v1.json`. The asset bundle contains the large runtime files named by that manifest.

Hosted asset download, automated asset bootstrap, bundled OCI image archives, and air-gapped/offline release packages are out of scope for the V1 RC1 normal path. Restricted-network support remains a support-managed image preload plus local asset import unless a later task expands that contract.

## Release Artifacts

For a release version such as `v0.1.0-rc1`, the expected artifacts are:

| Artifact | Example | Purpose |
| --- | --- | --- |
| Control ZIP | `towerscout-v0.1.0-rc1.zip` | User-facing package with launcher, Compose, scripts, docs, manifest, and pinned image metadata. |
| Control ZIP checksum | `towerscout-v0.1.0-rc1.zip.sha256` | SHA-256 checksum for the full control ZIP. |
| GHCR image digest | `ghcr.io/j-schulein/towerscout@sha256:<digest>` | Immutable Linux/AMD64 runtime image referenced by the control ZIP. |
| Asset ZIP | `towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip` | Restricted-pilot or support-supplied local bundle containing model weights, ZIP-code data, and the asset manifest copy. |
| Asset ZIP checksum | `towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip.sha256` | SHA-256 checksum for the full asset ZIP. |

The release version in the control ZIP and asset ZIP names must match. The manifest version in the asset ZIP name must match the `manifest_version` in `webapp/asset_manifest.v1.json`.

Under the AGPL-compliant YOLO release direction, the asset ZIP may move forward for a YOLO-enabled `agpl-yolo` release only when the release manifest, model notices, and source offer clearly identify the YOLO detector weights as YOLO-derived/AGPL-governed unless separate written model terms say otherwise. If reviewers reject the AGPL release posture or the model terms cannot be documented, external publication falls back to a restricted-pilot or bring-your-own-assets path.

## Canonical Layouts

The asset ZIP root must contain these entries directly:

```text
model_params/
data/
asset_manifest.v1.json
```

Do not put an extra top-level `assets/` directory inside the asset ZIP.

After a user extracts the asset ZIP into the release package's `assets/` directory, the staged source layout must be:

```text
assets/
  model_params/
    yolov5/
      newest.pt
    EN/
      b5_unweighted_best.pt
  data/
    tl_2025_us_zcta520/
      tl_2025_us_zcta520.cpg
      tl_2025_us_zcta520.dbf
      tl_2025_us_zcta520.prj
      tl_2025_us_zcta520.shp
      tl_2025_us_zcta520.shp.ea.iso.xml
      tl_2025_us_zcta520.shp.iso.xml
      tl_2025_us_zcta520.shx
  asset_manifest.v1.json
```

The Windows import helper treats the `-Source` path as the source root and expects `model_params/` and `data/` directly below it:

```powershell
.\scripts\import-assets.cmd -Source assets
```

The importer copies the staged source into the selected container engine's named volumes. The runtime destination layout inside the container is:

```text
/app/webapp/model_params/
/app/webapp/data/
```

The importer does not copy assets into another local package directory.

## Manifest Authority

The control package copy at `webapp/asset_manifest.v1.json` is the authoritative manifest for the TowerScout release. The asset ZIP must include a root-level `asset_manifest.v1.json` copy for identity and support validation.

Release/support validation must compare:

- Control ZIP release version and asset ZIP release version.
- Control manifest `manifest_version` and asset ZIP manifest `manifest_version`.
- Control manifest file hash and asset ZIP manifest file hash.

Current import automation verifies required asset presence and byte sizes, and verifies asset SHA-256 hashes when requested. Release-version mismatch, manifest-version mismatch, and control/asset manifest file-hash mismatch are release/support validation failures, but they are not currently enforced directly by `scripts/import-assets.cmd`.

## Required Assets

The current manifest is `towerscout-v1-assets-2026-05-05`.

| ID | Path | Required | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| `yolo-newest` | `model_params/yolov5/newest.pt` | Yes | 175084429 | `27315E156D8370D51D9C2A3C047C4BF5CC0C8AE1521036BDF800B7A8A81554E6` |
| `efficientnet-b5-project-weights` | `model_params/EN/b5_unweighted_best.pt` | Yes | 118567303 | `645113BADFCD17A1F9B451AABB54BF80E115A4FAACEB65E0CE3FC8DBFB108A5D` |
| `zcta-2025-cpg` | `data/tl_2025_us_zcta520/tl_2025_us_zcta520.cpg` | Yes | 5 | `3AD3031F5503A4404AF825262EE8232CC04D4EA6683D42C5DD0A2F2A27AC9824` |
| `zcta-2025-dbf` | `data/tl_2025_us_zcta520/tl_2025_us_zcta520.dbf` | Yes | 2838798 | `FB1CD7305831772FD375607A0561D9A7C9F126ED665D10D2D51E9A9772853D06` |
| `zcta-2025-prj` | `data/tl_2025_us_zcta520/tl_2025_us_zcta520.prj` | Yes | 165 | `0B9041E921D9EBB43247D314608FE9E38A0B008EE793067FC1806199EA1FB9DD` |
| `zcta-2025-shp` | `data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp` | Yes | 822559684 | `3A701EEBDF9982269F87AA19C49CCC6596CA303126E4901DD2EE814F22A591B4` |
| `zcta-2025-shx` | `data/tl_2025_us_zcta520/tl_2025_us_zcta520.shx` | Yes | 270428 | `804A57259FC72A56E04FAE9B02617814E5C8F9853B353134FEF418973A227775` |

## Optional Assets

Optional assets should be included in the release asset ZIP when available. Missing optional files are reported as `optional_missing` and do not block import or readiness when all required assets pass.

| ID | Path | Required | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| `zcta-2025-shp-ea-metadata` | `data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp.ea.iso.xml` | No | 17697 | `648571DEA5799CF2011781635FD20AE7DEBD23DF34DA09CE37519F4202B166EA` |
| `zcta-2025-shp-metadata` | `data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp.iso.xml` | No | 50682 | `AEA0E75009756CA5B6FFF899C5053D8CBB91E5EBC17A67938B01977404CBE9F0` |

## Checksum Policy

The asset ZIP checksum sidecar must use this line format:

```text
<lowercase-sha256-hex>  towerscout-<release-version>-assets-<manifest-version>.zip
```

Example:

```text
<sha256>  towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip
```

Normal end-user import:

```powershell
.\scripts\import-assets.cmd -Source assets
```

Release-candidate and support validation import:

```powershell
.\scripts\import-assets.cmd -Source assets -VerifyHashes
```

Runtime/readiness hash verification is validation/support-only:

```powershell
$env:TOWERSCOUT_VERIFY_ASSET_HASHES = "1"
.\scripts\status.cmd
```

Routine first run and launcher polling should not enable runtime hash verification because the ZIP-code geometry file is large.

## Failure Contract

| Condition | Current behavior | Release/support expectation |
| --- | --- | --- |
| Required file missing | Import/readiness reports missing asset and non-ok asset status. | User imports the correct asset bundle and restarts/checks status. |
| Required file byte size mismatch | Import/readiness reports corrupt asset and non-ok asset status. | Treat as wrong, incomplete, or damaged asset bundle. |
| Required file SHA-256 mismatch with hash verification enabled | Import/readiness reports corrupt asset and non-ok asset status. | Treat as wrong or damaged asset bundle; do not continue validation. |
| Optional file missing | Import/readiness reports `optional_missing`. | Does not block when required assets pass. |
| Asset ZIP release version does not match control ZIP release version | Not directly enforced by importer. | Release/support validation failure. |
| Asset ZIP manifest version does not match control manifest version | Not directly enforced by importer. | Release/support validation failure. |
| Asset ZIP manifest file hash differs from control manifest file hash | Not directly enforced by importer. | Release/support validation failure unless intentionally approved as a manifest update. |

## Provenance And Distribution Gate

Model assets are TowerScout release assets derived from the project model pipeline, but they are not treated as Apache-2.0-only application source. For the YOLO-enabled `agpl-yolo` release, `model_params/yolov5/newest.pt` must be labeled as YOLO-derived/AGPL-governed unless a separate written model license or permission record says otherwise. EfficientNet classifier weights require separate project distribution authority. ZIP-code data is based on US Census ZCTA release data. The manifest records these source labels per file.

External publication of the asset ZIP is no longer blocked solely by the old YOLO redistribution uncertainty if reviewers accept the AGPL-compliant release posture and the required model/data terms are packaged. If AGPL is not accepted as the release posture, end-user documentation must describe the approved source and local staging process instead of promising a TowerScout-hosted asset ZIP.

## Follow-Up Boundaries

Typed importer exit codes are follow-up work unless `TASK-072` is explicitly expanded into importer behavior.

The current importer accepts an already-extracted source directory. If future work accepts ZIP files directly, it must reject unsafe archive entries such as `..\`, absolute paths, and paths escaping the extraction root.

Public-release asset import still needs a stronger staged activation model than the V1 RC1 helper currently provides. Follow-up work must stage candidate assets, verify the manifest allowlist, byte sizes, and SHA-256 hashes before activation, and preserve the previous active asset set if validation fails unless `TASK-066` shows this is release-critical for RC1.

A narrow release-manifest and compliance-payload slice is in scope for the AGPL-compliant RC path: the control package must include `release-manifest.v1.json`, `SOURCE.txt`, `SBOM.txt`, checksums, image digest metadata, model/data terms, provider terms, and revocation notes. Stronger staged allowlist-only asset activation remains follow-up unless `TASK-066` shows it is release-critical.

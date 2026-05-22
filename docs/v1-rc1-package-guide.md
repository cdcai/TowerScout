# TowerScout V1 RC1 Package Guide

This guide is for first-line support, internal release-candidate validation,
and pilot testers using the TowerScout V1 RC1 Windows package path. It is the
preferred pilot path. Older source, virtual environment, and Conda tester guides
are legacy source-install guidance and are not the preferred V1 RC1 package
path.

## Supported Target

V1 RC1 supports:

- Windows 11 on AMD64.
- Single-user local use.
- CPU baseline.
- Normal outbound internet access for GHCR image pulls and map providers.
- A Docker-compatible or OCI-compatible container engine with Compose support.
- One valid Google Maps or Azure Maps provider key.

Out of scope for this release path:

- macOS.
- ARM64.
- Air-gapped or fully offline installs.
- VDI.
- Shared multi-user hosting.
- Managed remote deployment.
- Native Windows installer behavior.
- Bundled OCI image archive workflow.

Podman is the preferred open-source Windows runtime target when the Podman
machine is running and an approved Compose provider is installed. Docker
compatibility remains useful where Docker Desktop is licensed, approved, and
available.

## Prerequisite Software Checklist

Before a pilot user starts the package, confirm the workstation has:

- Windows 11 AMD64 with virtualization/WSL2 support enabled according to local
  IT policy.
- Windows PowerShell. The package helper scripts use `.cmd` wrappers and
  PowerShell scripts.
- A modern browser such as Microsoft Edge or Google Chrome.
- A ZIP extraction path that preserves the package folder structure.
- Normal outbound internet access to GHCR and the selected map provider.
- Several GB of free disk space for the control package, asset bundle,
  container image, and engine volumes. CUDA-capable images require more disk
  space than CPU-only images.
- One approved container engine path:
  - Podman CLI or Podman Desktop, a created and running Podman machine, and an
    approved Compose provider such as `podman-compose`.
  - Docker Desktop, where licensing, procurement, endpoint policy, and local
    installation approval allow it.
- One valid site/user-owned restricted Google Maps or Azure Maps provider key.

The package path does not require Git, Python, Conda, Node.js, VS Code, or a
source-code checkout on the pilot user's computer.

Useful support checks before launch:

```powershell
docker --version
docker compose version
podman --version
podman machine list
podman compose version
```

Only the selected engine needs to pass its checks. If both Docker and Podman
are installed, automatic engine selection can choose Docker first. Use
`-Engine podman` consistently when validating the Podman path.

## Release Artifacts

A normal V1 RC1 handoff has two artifact groups.

Control package:

- `towerscout-v0.1.0-rc1.zip`
- `towerscout-v0.1.0-rc1.zip.sha256`

Asset package:

- `towerscout-v0.1.0-rc1-assets-<asset-version>.zip`
- `towerscout-v0.1.0-rc1-assets-<asset-version>.zip.sha256`

The exact asset filename can change by release. The control ZIP, asset ZIP,
`IMAGE.txt`, `release-manifest.v1.json`, and `webapp/asset_manifest.v1.json`
must agree about the release handoff.

The control package contains launch scripts, Compose files, docs, compliance
files, `IMAGE.txt`, `SHA256SUMS.txt`, `release-manifest.v1.json`, and the asset
manifest. It does not contain the large model and ZIP-code data files.

The asset package contains the large runtime files required for detection and
ZIP-code search.

## Verify Downloads Before Extracting

Before extracting either ZIP, compare each artifact to its matching `.sha256`
file in PowerShell:

```powershell
Get-FileHash .\towerscout-v0.1.0-rc1.zip -Algorithm SHA256
Get-Content .\towerscout-v0.1.0-rc1.zip.sha256
Get-FileHash .\towerscout-v0.1.0-rc1-assets-*.zip -Algorithm SHA256
Get-Content .\towerscout-v0.1.0-rc1-assets-*.zip.sha256
```

The `Hash` value from `Get-FileHash` must match the SHA-256 value in the
corresponding `.sha256` file. If the values do not match, stop validation and
obtain a fresh copy of the affected release artifact.

## Control Package Layout

After extracting the control ZIP, the package root should include:

```text
start.bat
compose.yaml
compose.gpu.yaml
.env.example
scripts\
docs\
assets\
LICENSE
NOTICE
THIRD_PARTY_NOTICES.md
MODEL_LICENSES.md
DATA_LICENSES.md
PROVIDER_TERMS.md
SOURCE.txt
SBOM.txt
IMAGE.txt
SHA256SUMS.txt
release-manifest.v1.json
webapp\asset_manifest.v1.json
```

The package `.env.example` should pin `TOWERSCOUT_IMAGE` to an immutable GHCR
digest reference such as:

```text
ghcr.io/j-schulein/towerscout:v0.1.0-rc1-cuda121@sha256:<digest>
```

`IMAGE.txt`, `.env.example`, and `release-manifest.v1.json` record the selected
PyTorch flavor, either `cpu` or `cuda121`.

## Initialize Package Configuration

Run the launcher once from the package root before importing assets:

```powershell
.\start.bat
```

The launcher creates `.env` from `.env.example` when `.env` is missing, starts
the selected engine, polls `/api/readiness`, and opens `http://localhost:5000`
after the application shell is reachable. Release packages should already pin
`TOWERSCOUT_IMAGE` to an immutable digest in `.env.example`; the first launcher
run copies that pinned value into `.env`.

Readiness may report `setup_required` before provider keys are saved and
`degraded` before assets are imported. Those states are normal during setup.

If validation or support chooses a specific engine, use the same `-Engine`
value on every helper command because Docker and Podman use separate named
volumes:

```powershell
.\start.bat -Engine podman
.\scripts\import-assets.cmd -Engine podman -Source assets
.\scripts\status.cmd -Engine podman
.\scripts\logs.cmd -Engine podman -Tail 200
.\scripts\stop.cmd -Engine podman
```

## Asset Staging And Import

The asset ZIP root must contain these entries directly:

```text
model_params\
data\
asset_manifest.v1.json
```

Do not add an extra nested `assets\` directory inside the asset ZIP.

Extract the asset ZIP contents into the release package `assets\` folder. The
staged source should be:

```text
assets\
  model_params\
    yolov5\
      newest.pt
    EN\
      b5_unweighted_best.pt
  data\
    tl_2025_us_zcta520\
      tl_2025_us_zcta520.cpg
      tl_2025_us_zcta520.dbf
      tl_2025_us_zcta520.prj
      tl_2025_us_zcta520.shp
      tl_2025_us_zcta520.shp.ea.iso.xml
      tl_2025_us_zcta520.shp.iso.xml
      tl_2025_us_zcta520.shx
  asset_manifest.v1.json
```

Normal import:

```powershell
.\scripts\import-assets.cmd -Source assets
```

Release-candidate or support validation import:

```powershell
.\scripts\import-assets.cmd -Source assets -VerifyHashes
```

If the launcher was started with a non-default port, pass the same `-Port`
value to the asset importer:

```powershell
.\scripts\import-assets.cmd -Source assets -Port 5001 -VerifyHashes
```

The importer copies assets into the selected engine's named volumes. It does
not copy assets into another local package folder. The importer starts the
container if needed so the named volumes are available, then restarts TowerScout
after the copy so the running application discovers the imported model files.
Run the launcher once first so `.env` exists and the selected release image is
pinned.

## Starting Or Reopening TowerScout

From the package root:

```powershell
.\start.bat
```

The launcher:

- Starts the selected container engine and Compose stack.
- Uses CPU-safe GPU mode `off` unless another mode is explicitly requested.
- Polls `/api/readiness`.
- Opens `http://localhost:5000` after the application shell is reachable.

Use `localhost` for browser access. The Azure Maps browser SDK passed release
validation from the `localhost` origin and may reject some `127.0.0.1` browser
requests.

To force an engine:

```powershell
.\start.bat -Engine podman
.\start.bat -Engine docker
```

For support checks without opening the browser:

```powershell
.\start.bat -NoBrowser
```

For a non-default port:

```powershell
.\start.bat -Port 5001
```

## Optional GPU Launch Boundary

The V1 RC1 package can carry a CPU or CUDA-capable PyTorch image. The default
launch path is CPU-safe either way:

```powershell
.\start.bat -Gpu off
```

Docker GPU launch is optional and must be validated on the workstation before
it is treated as supported:

```powershell
.\start.bat -Engine docker -Gpu auto
.\start.bat -Engine docker -Gpu on
```

- `-Gpu off` uses the default Compose file and sets `TOWERSCOUT_DEVICE=cpu`.
- `-Gpu auto` sets `TOWERSCOUT_DEVICE=auto` and starts without the GPU overlay
  unless `TOWERSCOUT_GPU_AUTO_OVERLAY=1` has been set in the shell or `.env`
  after Docker GPU validation on that workstation.
- `-Gpu on` adds `compose.gpu.yaml`, sets `TOWERSCOUT_DEVICE=cuda`, and fails
  readiness if CUDA is unavailable to the container.

GPU launch requires a CUDA-capable TowerScout image plus a Docker host with
NVIDIA GPU support available to containers. A host `nvidia-smi` result alone is
not enough; Docker must be able to pass the GPU into the container. Podman GPU
launch is not validated for this release path.

For optional GPU validation, the workstation also needs an NVIDIA GPU, current
NVIDIA host drivers, Docker Desktop configured for GPU-capable Linux
containers, and site-approved proof that Docker can expose the GPU to a test
container. Do not set `TOWERSCOUT_GPU_AUTO_OVERLAY=1` until that validation has
passed on the workstation.

`/api/readiness` includes non-secret `ml_runtime` diagnostics that support can
use to distinguish CPU-wheel images, CUDA runtime probe failures, and normal CPU
fallback.

## Readiness States

Check status:

```powershell
.\scripts\status.cmd
```

TowerScout readiness states:

| State | Meaning | User action |
| --- | --- | --- |
| `setup_required` | TowerScout is running, but no valid provider key is configured. | Open the browser and complete Setup Wizard or Settings. |
| `degraded` | TowerScout is running, but assets or another recoverable capability are missing. | Import assets or follow the recovery hints. |
| `ready` | Provider setup and required assets are present. | Use TowerScout. |
| `fatal` | TowerScout cannot safely serve normal or recovery workflows. | Collect support evidence and stop validation. |

`/api/readiness` returns HTTP 503 only for `fatal`. Other readiness states
return HTTP 200 with machine-readable details.

## Provider Key Setup

TowerScout can run with one valid Google Maps key or one valid Azure Maps key.
Use Setup Wizard on first run, or Settings later, to save keys into the
persistent configuration volume.

V1 RC1 provider-key policy:

- Browser map SDK keys are client-visible to someone with access to the running
  browser app.
- Pilot keys must be site/user-owned unless a separate owner-approved exception
  is recorded.
- Unrestricted shared TowerScout project keys are unsupported.
- Users/sites should apply provider-side restrictions, API scoping, quotas,
  billing alerts, usage monitoring, and key rotation according to local policy.
- Do not paste provider keys into issue reports, screenshots, raw browser
  network traces, or support messages.

Google Maps keys must support TowerScout's use of:

- Maps JavaScript API.
- Places or Places API (New) features needed for autocomplete/search.
- Maps Static API for imagery.
- Geocoding API.

Where practical, use separate restricted Google keys for browser and server
use. Apply website/application restrictions and API restrictions for the APIs
TowerScout uses. Google publishes current API-key guidance at:

```text
https://developers.google.com/maps/api-security-best-practices
```

Azure Maps subscription keys must support TowerScout's use of:

- Azure Maps Web SDK.
- Imagery/tiles.
- Search and geocoding.

For the local V1 RC1 pilot, Azure shared-key authentication is acceptable only
with site/user-owned keys, monitoring, quota controls, and rotation according
to local policy. Broader or hosted distribution should revisit Microsoft Entra
ID or SAS-token authentication. Microsoft publishes current Azure Maps
authentication guidance at:

```text
https://learn.microsoft.com/en-us/azure/azure-maps/authentication-best-practices
```

## Basic User Validation

After readiness is `ready`:

1. Open `http://localhost:5000`.
2. Confirm the expected provider is selected.
3. Search for an approved pilot location or navigate the map manually.
4. Define a small search area with a circle or custom shape.
5. Select `Estimate tiles`.
6. Confirm the tile count and expected time are reasonable.
7. Select `Find towers`.
8. Review results in the detection list and map.
9. Export CSV/KML or dataset results only if allowed by the pilot workflow.

Use small search areas for release-candidate smoke checks. Do not use sensitive
AOIs in broad screenshots or public issue reports.

## Troubleshooting

### Launcher Timeout

Run:

```powershell
.\scripts\status.cmd
.\scripts\logs.cmd -Tail 200
```

Common causes:

- Selected engine is not installed, running, licensed, or approved.
- Podman machine is not created or running.
- Compose provider is missing or points to the wrong executable.
- The configured port is already in use.
- The pinned image cannot be pulled from GHCR.
- Required assets are missing or corrupt.
- No provider key is configured.

### Podman

For Podman, confirm:

- Podman machine is created and running.
- `podman compose` can use an approved Compose provider such as
  `podman-compose`.
- If needed, `PODMAN_COMPOSE_PROVIDER` points to the approved provider.

The launcher reports Compose-provider information before startup and validates
a `PODMAN_COMPOSE_PROVIDER` override before Compose is invoked.

### Docker

Docker Desktop use depends on local license, procurement, endpoint policy, and
installation approval. If Docker is blocked or unavailable, use the validated
Podman CPU path when allowed by local policy.

### Assets Missing Or Corrupt

Recheck the asset ZIP version and layout, then run:

```powershell
.\scripts\import-assets.cmd -Source assets -VerifyHashes
.\scripts\status.cmd
```

Do not continue release-candidate validation if required asset hashes fail.

### Provider-Key Validation Or TLS Failure

If key validation says TowerScout could not reach the provider validation
service and logs mention `CERTIFICATE_VERIFY_FAILED`, the container may not
trust the local network inspection certificate.

Import a local CA bundle for the selected engine:

```powershell
.\scripts\import-tls-ca.cmd -Thumbprint <windows-certificate-thumbprint>
```

For Podman:

```powershell
.\scripts\import-tls-ca.cmd -Engine podman -Thumbprint <windows-certificate-thumbprint>
```

If the site blocks Google but uses Azure, choose Azure verification:

```powershell
.\scripts\import-tls-ca.cmd -Engine podman -Thumbprint <windows-certificate-thumbprint> -VerifyProvider azure
```

`TOWERSCOUT_ALLOW_INSECURE_TLS=1` is a last-resort validation-only workaround.
Do not use it as normal release configuration.

### Restricted Networks

The V1 RC1 normal path expects the selected engine to pull the pinned image from
GHCR. A bundled OCI image archive is not part of the supported V1 RC1 control
package.

For restricted-network sites, the supported fallback is a support-managed
preload of the pinned image into the selected Docker or Podman image store,
then normal package startup and local asset import.

## Support Evidence

Useful evidence:

- Release version and package filename.
- `IMAGE.txt`.
- `SHA256SUMS.txt`.
- `release-manifest.v1.json`.
- `SOURCE.txt`.
- `SBOM.txt`.
- `webapp\asset_manifest.v1.json`.
- `scripts\status.cmd` output.
- A reviewed and redacted summary of `scripts\logs.cmd -Tail 200`.
- Which engine was selected: Docker or Podman.
- For Podman, the selected Compose provider.
- Readiness state and recovery hints.
- For GPU validation, the requested `-Gpu` mode and non-secret `ml_runtime`
  readiness diagnostics.

Do not share unless a site-specific support procedure explicitly approves:

- `.env`.
- Provider keys.
- Raw logs.
- Raw screenshots.
- Browser network traces.
- Cached provider responses.
- Uploaded files.
- Exported datasets.
- Named-volume contents.
- Sensitive addresses, coordinates, or local AOIs.

## Source, License, And Terms

The YOLO-enabled V1 RC1 package/image is distributed with AGPL-3.0 obligations
and is not Apache-2.0-only. The release control ZIP is authoritative for
release-specific source, image digest, checksum, SBOM, and manifest metadata.

Package files:

- `LICENSE`
- `NOTICE`
- `THIRD_PARTY_NOTICES.md`
- `MODEL_LICENSES.md`
- `DATA_LICENSES.md`
- `PROVIDER_TERMS.md`
- `SOURCE.txt`
- `SBOM.txt`
- `IMAGE.txt`
- `release-manifest.v1.json`

Running app notices:

```text
http://localhost:5000/license      formatted browser page
http://localhost:5000/license.txt  plain-text combined notices
```

Use `/license.txt` when support needs text for scripts, copy/paste, or archival
records.

Provider services are not included with TowerScout. Users are responsible for
provider terms, billing, allowed use, quota controls, monitoring, and key
rotation.

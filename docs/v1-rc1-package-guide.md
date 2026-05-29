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
- Docker Desktop as the primary controlled RC1 pilot engine.
- Podman as a qualified package-runtime option only when a running Podman
  machine and approved Compose provider are already available.
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

Docker Desktop is the default pilot support path because that is the path most
external testers will be asked to exercise first. Podman remains a qualified
support path for sites that explicitly choose it and can provide a working
Podman machine plus Compose provider.

## Prerequisite Software Checklist

Before a pilot user starts the package, confirm the workstation has:

- Windows 11 AMD64 with virtualization/WSL2 support enabled according to local
  IT policy.
- Windows PowerShell. The package helper scripts use `.cmd` wrappers and
  PowerShell scripts.
- A modern browser such as Microsoft Edge or Google Chrome.
- A ZIP extraction path that preserves the package folder structure.
- Normal outbound internet access to GHCR and the selected map provider.
- Several GB of free disk space for the Application Package, Model & Data
  Package, container image, and engine volumes. CUDA-capable images require
  more disk space than CPU-only images. Use `15 GB` free as a minimum and
  `25 GB` free as the recommended first-setup target.
- One approved container engine path:
  - Docker Desktop with the WSL 2 backend is the primary V1 RC1 pilot path.
    Docker's current Windows requirements include WSL `2.1.5` or later, 8 GB
    RAM, and hardware virtualization enabled in BIOS/UEFI.
  - Podman CLI or Podman Desktop is a qualified support path only when the
    Podman machine is created and running and an approved Compose provider such
    as `podman-compose` is installed.
- One valid site/user-owned restricted Google Maps or Azure Maps provider key.

The package path does not require Git, Python, Conda, Node.js, VS Code, or a
source-code checkout on the pilot user's computer.

For users who do not normally use the command line, open commands from Windows
PowerShell in the extracted TowerScout package folder. In File Explorer, open
the package folder, click the address bar, type `powershell`, and press Enter.
Commands beginning with `.\` run scripts from that folder.

Useful Docker Desktop checks before launch:

```powershell
wsl --status
wsl --list --verbose
docker --version
docker compose version
```

Expected result: WSL is installed, any listed Linux distribution uses version
`2`, and Docker commands print version information while Docker Desktop is
running. If WSL is not installed and local policy allows installation,
Microsoft's current install path is `wsl --install` from an Administrator
PowerShell window, followed by a restart when Windows asks.

Useful Podman checks when support explicitly chooses Podman:

```powershell
podman --version
podman machine list
podman compose version
```

Only the selected engine needs to pass its checks. If both Docker and Podman
are installed, automatic engine selection can choose Docker first. Use
`-Engine podman` consistently when validating the Podman path.

## Stop And Contact Support

Stop validation and contact support if:

- Docker Desktop is not installed, not approved, or cannot start on the primary
  pilot path, unless support explicitly assigned the Podman path.
- WSL is unavailable, or `wsl --list --verbose` shows version `1` and the user
  does not have administrator approval to update it.
- An Application Package or Model & Data Package checksum does not match.
- The Application Package and Model & Data Package release versions do not
  match.
- Asset import reports missing, corrupt, or hash-failed files.
- TowerScout readiness state is `fatal`.
- Provider validation repeatedly fails after the key value and provider setup
  have been checked.

Do not ask users to send provider keys, full `.env` files, raw screenshots,
browser traces, cached provider responses, named-volume contents, exported
datasets, or unredacted raw logs unless the site has an approved handling
procedure.

## Release Artifacts

A normal V1 RC1 handoff has two artifact groups. Open the TowerScout releases
page and use the exact release that support selected:

```text
https://github.com/J-Schulein/TowerScout/releases
```

If support provides a direct release URL, use that link. On GitHub Releases,
download these files from the release `Assets` section, not from the green
GitHub `Code` button and not from GitHub's automatic `Source code (zip)` or
`Source code (tar.gz)` links.

Application Package:

- `towerscout-v0.1.0-rc1.zip`
- `towerscout-v0.1.0-rc1.zip.sha256`

Model & Data Package:

- `towerscout-v0.1.0-rc1-assets-<asset-version>.zip`
- `towerscout-v0.1.0-rc1-assets-<asset-version>.zip.sha256`

The exact asset filename can change by release. The Application Package ZIP,
Model & Data Package ZIP, `IMAGE.txt`, `release-manifest.v1.json`, and
`webapp/asset_manifest.v1.json` must agree about the release handoff.

Do not ask users to type the angle brackets from `<asset-version>`. They should
copy the exact Model & Data Package filename from the release or Downloads
folder. Example only:

```text
towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip
```

Download all four files into a new empty local folder before verification. The
release version in the Application Package and Model & Data Package filenames
must match, for example `v0.1.0-rc1`.

The Application Package contains launch scripts, Compose files, docs,
compliance files, `IMAGE.txt`, `SHA256SUMS.txt`, `release-manifest.v1.json`,
and the asset manifest. It does not contain the large model and ZIP-code data
files.

The Model & Data Package contains the large runtime files required for
detection and ZIP-code search.

## Verify Downloads Before Extracting

Before extracting either ZIP, compare each artifact to its matching `.sha256`
file in PowerShell. Run these commands from the new folder that contains only
the four downloaded release files:

```powershell
Get-FileHash .\towerscout-v0.1.0-rc1.zip -Algorithm SHA256
Get-Content .\towerscout-v0.1.0-rc1.zip.sha256
Get-FileHash .\towerscout-v0.1.0-rc1-assets-*.zip -Algorithm SHA256
Get-Content .\towerscout-v0.1.0-rc1-assets-*.zip.sha256
```

The `Hash` value from `Get-FileHash` must match the SHA-256 value in the
corresponding `.sha256` file. If the values do not match, stop validation and
obtain a fresh copy of the affected release artifact.

The `*` wildcard should match exactly one Model & Data Package ZIP and exactly
one matching `.sha256` file. If PowerShell prints more than one asset ZIP or
checksum file, move old TowerScout downloads out of the folder and run the
commands again.

Example: these values match:

```text
Get-FileHash output:
HASH      0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF

.sha256 file:
0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef  towerscout-v0.1.0-rc1.zip
```

Uppercase and lowercase letters are not important. The letters and numbers
must otherwise be identical.

## Application Package Layout

After extracting the Application Package ZIP, the package root should include:

```text
bootstrap.cmd
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

## Guided Bootstrap Path

For first setup, prefer the top-level bootstrap entry point:

```powershell
.\bootstrap.cmd -Engine docker -Gpu off -AssetZip .\towerscout-v0.1.0-rc1-assets-<asset-version>.zip
```

Replace `<asset-version>` with the exact filename value from the Model & Data
Package ZIP. Do not type the angle brackets.

Bootstrap performs the checks that users most often miss:

- Docker or Podman CLI, daemon/machine, and Compose-provider readiness.
- WSL 2 hint for Docker Desktop on Windows.
- Local port availability.
- Minimum free disk space.
- Release manifest and control asset-manifest presence.
- Optional Application Package and Model & Data Package checksum verification
  when `-PackageZip` and `-AssetZip` paths are provided.
- Asset ZIP safety, direct-root layout, and control/asset manifest matching.
- Existing named-volume asset import through `scripts\import-assets.ps1` with
  hash verification enabled.
- Existing startup through `scripts\launch.ps1`.

If the release ZIPs are outside the package folder, pass full paths:

```powershell
.\bootstrap.cmd -Engine docker -Gpu off -PackageZip C:\Users\<you>\Downloads\towerscout-v0.1.0-rc1.zip -AssetZip C:\Users\<you>\Downloads\towerscout-v0.1.0-rc1-assets-<asset-version>.zip
```

Useful bootstrap options:

- `-VerifyOnly`: run prerequisite, checksum, release, and asset-layout checks
  without importing assets or starting TowerScout.
- `-SkipAssetImport`: run preflight and launch while leaving already-staged
  assets untouched.
- `-Port <port>`: use the same non-default port that support selected.
- `-Engine podman`: use the qualified Podman path when support selected
  Podman and the Podman machine plus Compose provider are already ready.

Expected result: bootstrap prints clear checks, rejects mismatched checksums or
unsafe asset ZIPs before mutating package assets, imports valid staged assets,
starts TowerScout, and explains readiness state. It is meant for first setup
and support validation. `start.bat` remains the normal direct launch path after
setup is complete.

Abbreviated successful first-run output should look similar to:

```text
TowerScout bootstrap preflight
[OK] Engine docker is available
[OK] Compose is available
[OK] Model & Data Package checksum matched
[OK] Asset import completed with hash verification
[OK] TowerScout responded at http://localhost:5000
readiness: setup_required
```

## Direct Launcher Path

The direct launcher remains supported and is useful when assets are already
imported, when reopening TowerScout after setup is complete, or when support
wants to isolate launch behavior. Do not run this as an extra first-setup step
after bootstrap has already opened TowerScout.

Run the launcher from the package root:

```powershell
.\start.bat -Engine docker -Gpu off
```

The launcher creates `.env` from `.env.example` when `.env` is missing, starts
the selected engine, polls `/api/readiness`, and opens `http://localhost:5000`
after the application shell is reachable. Release packages should already pin
`TOWERSCOUT_IMAGE` to an immutable digest in `.env.example`; the first launcher
run copies that pinned value into `.env`.

Readiness may report `setup_required` before provider keys are saved and
`degraded` before assets are imported. Those states are normal during setup.

Expected result: PowerShell prints that TowerScout is starting with Docker,
then reports a readiness state. A browser window should open to
`http://localhost:5000`. If the browser does not open, leave PowerShell open
and manually open that URL.

If validation or support chooses a specific engine, use the same `-Engine`
value on every helper command because Docker and Podman use separate named
volumes:

```powershell
.\start.bat -Engine podman -Gpu off
.\scripts\import-assets.cmd -Engine podman -Source assets
.\scripts\status.cmd -Engine podman
.\scripts\logs.cmd -Engine podman -Tail 200
.\scripts\stop.cmd -Engine podman
```

## Manual Asset Staging And Import

Use this manual fallback when bootstrap is not being used for asset ZIP
staging. The Model & Data Package ZIP root must contain these entries directly:

```text
model_params\
data\
asset_manifest.v1.json
```

Do not add an extra nested `assets\` directory inside the Model & Data Package
ZIP.

Extract the Model & Data Package ZIP contents into the release package
`assets\` folder. The staged source should be:

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

If extraction creates this layout, it is wrong:

```text
assets\
  assets\
    model_params\
    data\
    asset_manifest.v1.json
```

Move the inner `model_params`, `data`, and `asset_manifest.v1.json` entries up
one level so they sit directly inside the package `assets\` folder. If the
outer `assets\` folder already contains other files and a nested `assets\`
folder, treat the layout as ambiguous and ask support before continuing.

Normal import:

```powershell
.\scripts\import-assets.cmd -Engine docker -Source assets
```

Release-candidate or support validation import:

```powershell
.\scripts\import-assets.cmd -Engine docker -Source assets -VerifyHashes -RestartWaitSeconds 180
```

If the launcher was started with a non-default port, pass the same `-Port`
value to the asset importer:

```powershell
.\scripts\import-assets.cmd -Engine docker -Source assets -Port 5001 -VerifyHashes -RestartWaitSeconds 180
```

The importer copies assets into the selected engine's named volumes. It does
not copy assets into another local package folder. The importer starts the
container if needed so the named volumes are available, then restarts TowerScout
after the copy so the running application discovers the imported model files.
If `.env` is missing, the importer initializes it from the package
`.env.example` before starting the selected container stack so fresh packages
still use the pinned release image.

Expected result: the importer completes without missing/corrupt asset errors,
restarts TowerScout, and waits for readiness after restart. If hash verification
fails, stop validation and obtain the correct Model & Data Package.

## Starting Or Reopening TowerScout

From the package root:

```powershell
.\start.bat -Engine docker -Gpu off
```

The launcher:

- Starts the selected container engine and Compose stack.
- Uses CPU-safe GPU mode `off` unless another mode is explicitly requested.
- Polls `/api/readiness`.
- Opens `http://localhost:5000` after the application shell is reachable.

The first launch may need to pull the pinned TowerScout image from GHCR. This
can take several minutes, especially on first setup or slower networks. Keep
PowerShell open until the launcher reports readiness or a clear failure.

Use `localhost` for browser access. The Azure Maps browser SDK passed release
validation from the `localhost` origin and may reject some `127.0.0.1` browser
requests.

To force an engine:

```powershell
.\start.bat -Engine podman -Gpu off
.\start.bat -Engine docker -Gpu off
```

For support checks without opening the browser:

```powershell
.\start.bat -Engine docker -Gpu off -NoBrowser
```

For a non-default port:

```powershell
.\start.bat -Engine docker -Gpu off -Port 5001
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
.\scripts\status.cmd -Engine docker
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

Use the owner-provided public fixture when available. If a fixture has not been
provided, use a non-sensitive approved area and keep the first run small,
preferably `1-6` tiles. A successful smoke check means the detection workflow
completes without crashing and the map/review panel update, even if the result
count is zero for the selected area.

Do not use sensitive AOIs in broad screenshots or public issue reports.

## Troubleshooting

### Launcher Timeout

Run:

```powershell
.\scripts\status.cmd -Engine docker
.\scripts\logs.cmd -Engine docker -Tail 200
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

The selected Compose provider must be explicitly validated in the target
environment. If Docker Desktop is uninstalled, ensure `podman-compose` or
another approved provider is installed and set through `PODMAN_COMPOSE_PROVIDER`
when support needs to force that provider. The launcher reports
Compose-provider information before startup and validates a
`PODMAN_COMPOSE_PROVIDER` override before Compose is invoked.

If Podman reports `rootlessport listen ... bind: address already in use` even
when Windows shows the port as free, retry with a non-default package port and
use that same port on status/log/import commands:

```powershell
.\bootstrap.cmd -Engine podman -Gpu off -Port 5009 -AssetZip .\towerscout-v0.1.0-rc1-assets-<asset-version>.zip
.\scripts\status.cmd -Engine podman -Port 5009
```

If the error follows the same port after retry, ask support to inspect and
clear local Podman container/port state before continuing.

### Docker Desktop

Docker Desktop use depends on local license, procurement, endpoint policy, and
installation approval. For the primary pilot path, Docker Desktop should be
open from the Start menu, the WSL 2 backend should be selected when the option
is visible, and these commands should print version information:

```powershell
docker --version
docker compose version
```

If Docker is blocked or unavailable, use the qualified Podman CPU path only
when allowed by local policy and support has confirmed the Podman prerequisites.

### Assets Missing Or Corrupt

Recheck the Model & Data Package ZIP version and layout, then run:

```powershell
.\scripts\import-assets.cmd -Engine docker -Source assets -VerifyHashes -RestartWaitSeconds 180
.\scripts\status.cmd -Engine docker
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
- `scripts\status.cmd -Engine docker` output, or the same command with the
  explicitly selected engine.
- A reviewed and redacted summary of `scripts\logs.cmd -Engine docker -Tail
  200`, or the same command with the explicitly selected engine.
- Which engine was selected: Docker or Podman.
- For Podman, the selected Compose provider.
- Readiness state and recovery hints.
- For GPU validation, the requested `-Gpu` mode and non-secret `ml_runtime`
  readiness diagnostics.

Simple metadata commands for first-line support:

```powershell
Get-Content .\IMAGE.txt
Get-Content .\SHA256SUMS.txt
```

Ask users to send the package folder name and copied command output, not the
full `.env` file or raw named-volume contents.

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
and is not Apache-2.0-only. The release Application Package ZIP is
authoritative for release-specific source, image digest, checksum, SBOM, and
manifest metadata.

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

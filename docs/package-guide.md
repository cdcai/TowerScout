# TowerScout Package Guide

This guide is for first-line support, internal release-candidate validation,
and users of the TowerScout Windows package path.

**Applies to**: The exact documentation-aligned Windows release package named
by the authoritative release record
**Last reviewed**: 2026-10-02
**Audience**: First-line support, release validation, and package users
**Runtime scope**: Users independently choose Docker or Podman, CPU or a
compatible NVIDIA GPU, and Google Maps or Azure Maps. Each choice must meet
the requirements and tested combinations in the final release notes.

The package path is the preferred user path. Older source, virtual
environment, and Conda tester guides are legacy source-install guidance and are
not the preferred package path.

## Supported Target

The current release-candidate package supports:

- Windows 11 on AMD64.
- Single-user local use.
- User-selected CPU or compatible NVIDIA GPU processing.
- Two digest-pinned Application Package variants:
  - `cpu` for CPU processing.
  - `cuda128` for release-listed NVIDIA GPU workstations.
- One shared Model & Data Package ZIP for both Application Package variants.
- Normal outbound internet access for GHCR image pulls and map providers.
- User-selected Docker Desktop or Podman. Podman requires a running rootless
  WSL 2 machine, 64-bit Python 3.12, and the verified package-local Compose
  provider.
- Optional Docker GPU or Podman GPU after the selected engine's NVIDIA
  container path passes the documented checks.
- One valid Google Maps or Azure Maps provider key.
- Unsigned PowerShell host scripts invoked through the supplied `.cmd`/`.bat`
  wrappers on a workstation where the user and organization permit that path.

Out of scope for this release path:

- macOS.
- ARM64.
- Air-gapped or fully offline installs.
- VDI.
- Shared multi-user hosting.
- Managed remote deployment.
- Native Windows installer behavior.
- Bundled OCI image archive workflow.
- Signature-enforcing managed endpoints unless the site administrator
  separately approves, allowlists, or internally signs the package.

## Unsigned Windows Package And Execution Policy

TowerScout's packaged PowerShell scripts are intentionally not Authenticode-
signed. The supported user entrypoints are the provided `.cmd` and `.bat`
wrappers. They invoke Windows PowerShell 5.1 with a process-scoped
`-ExecutionPolicy Bypass`; this does not change the computer's persistent
execution-policy configuration.

That wrapper behavior is part of the standard unsigned support profile. It
does not override or qualify WDAC, AppLocker, constrained-language,
antivirus/EDR, SmartScreen, or organization-specific allowlisting. If any of
those controls requires administrator or trusted-publisher approval, stop and
use the site's approval process. Do not change persistent execution policy,
disable endpoint protection, or tell a user to select `Run anyway` for an
unverified file.

An organization may review and internally sign or allowlist TowerScout, but it
then owns the modified bytes and new checksums. Project qualification applies
only to the original published artifacts.

Docker CPU is the simplest starting point, not an assigned pathway. Users may
choose any supported combination whose prerequisites they can meet.

## Prerequisite Software Checklist

Before a package user starts, confirm the workstation has:

- Windows 11 AMD64 with virtualization/WSL2 support enabled according to local
  IT policy.
- Windows PowerShell. The package helper scripts use `.cmd` wrappers and
  PowerShell scripts.
- A modern browser such as Microsoft Edge or Google Chrome.
- A ZIP extraction path that preserves the package folder structure.
- Normal outbound internet access to GHCR and the selected map provider.
- Free disk space for the Application Package, Model & Data Package, container
  image, and engine volumes. Plan at least `15 GB` for CPU (`25 GB` is a better
  first-setup target) or at least `35 GB` for the CUDA package, plus room for
  exports. The final release note controls if it requires more.
- One chosen container engine path:
  - Docker Desktop with the WSL 2 backend.
    Docker's current Windows requirements include WSL `2.1.5` or later, 8 GB
    RAM, and hardware virtualization enabled in BIOS/UEFI.
  - Podman Desktop with a created and running rootless WSL 2 machine, 64-bit
    Python 3.12, and the package-local non-Docker-Desktop Compose provider.
  - Podman GPU additionally requires Windows NVIDIA drivers, WSL2 Podman, and
    a validated NVIDIA CDI device inside the Podman machine.
- One valid site/user-owned restricted Google Maps or Azure Maps provider key.

Docker does not require Git, Python, Conda, Node.js, VS Code, or a source-code
checkout. Podman requires 64-bit Python 3.12 only for the package-local Compose
provider installer.

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

Useful Podman checks when you choose Podman:

```powershell
podman --version
podman machine list
podman compose version
```

Only the selected engine needs to pass its checks. If both Docker and Podman
are installed, automatic engine selection can choose Docker first. Use
`-Engine podman` consistently when validating the Podman path.

## When To Stop And Where To Ask

Stop if:

- The chosen engine is not installed, not allowed, or cannot start.
- WSL is unavailable, or `wsl --list --verbose` shows version `1` and the user
  does not have administrator approval to update it.
- An Application Package or Model & Data Package checksum does not match.
- The Application Package and Model & Data Package release versions do not
  match.
- Asset import reports missing, corrupt, or hash-failed files.
- TowerScout readiness state is `fatal`.
- Provider validation repeatedly fails after the key value and provider setup
  have been checked.
- Windows, SmartScreen, Defender/EDR, or an organization policy blocks the
  package or requires administrator/trusted-publisher approval.

Do not ask users to send provider keys, full `.env` files, raw screenshots,
browser traces, cached provider responses, named-volume contents, exported
datasets, or unredacted raw logs unless the site has an approved handling
procedure.

Ask Local IT about installation permission, WSL, endpoint policy, proxies,
TLS inspection, certificates, drivers, or firewall rules. Report a
non-sensitive TowerScout product defect at
`https://github.com/J-Schulein/TowerScout/issues`. The issue tracker is public
and is not a private or guaranteed-response help desk.

## Release Artifacts

Use the release entry whose notes identify it as the current supported final
Windows release. A draft, prerelease, source archive, branch name, or
numerically newer tag is not supported unless the authoritative release record
explicitly says otherwise.

A normal final release has two artifact groups. Open the TowerScout Releases
page and choose the identified final release:

```text
https://github.com/J-Schulein/TowerScout/releases
```

On GitHub Releases, download these files from the release `Assets` section,
not from the green
GitHub `Code` button and not from GitHub's automatic `Source code (zip)` or
`Source code (tar.gz)` links.

Application Package, choose exactly one variant:

- CPU package for normal/non-GPU users:
  - `towerscout-<release-version>-cpu.zip`
  - `towerscout-<release-version>-cpu.zip.sha256`
- CUDA 12.8 package for release-listed NVIDIA GPU workstations:
  - `towerscout-<release-version>-cuda128.zip`
  - `towerscout-<release-version>-cuda128.zip.sha256`

Do not put both Application Package variants in the same working folder. The
setup helper expects one matching Application Package.

Model & Data Package:

- `towerscout-<release-version>-assets-<asset-version>.zip`
- `towerscout-<release-version>-assets-<asset-version>.zip.sha256`

The exact asset filename can change by release. The Application Package ZIP,
Model & Data Package ZIP, `IMAGE.txt`, `release-manifest.v1.json`, and
`webapp/asset_manifest.v1.json` must agree about the release handoff.
Both CPU and CUDA Application Package manifests should name the same Model &
Data Package filename and SHA-256 unless a release note explicitly says assets
changed by variant.

Do not ask users to type the angle brackets from `<release-version>` or
`<asset-version>`. They should copy the exact Application Package and Model &
Data Package filenames from the release or Downloads folder. Example only:

```text
towerscout-<release-version>-assets-towerscout-v1-assets-2026-05-05.zip
```

After browser download, copy all four files from the user's `Downloads` folder
into a new empty working folder before setup or manual verification. The
recommended first-cohort working folder is:

```text
C:\Users\<you>\Documents\TowerScoutUAT
```

The release version in the Application Package and Model & Data Package
filenames must match. The Application Package will include `-cpu` or
`-cuda128`; the shared Model & Data Package filename does not include an image
flavor.

The Application Package contains launch scripts, Compose files, docs,
compliance files, `IMAGE.txt`, `SHA256SUMS.txt`, `release-manifest.v1.json`,
and the asset manifest. It does not contain the large model and ZIP-code data
files.

The Model & Data Package contains the large runtime files required for
detection and ZIP-code search.

Keep all four downloaded files together. For the normal setup path, extract
only the Application Package ZIP. Leave the Model & Data Package ZIP
unextracted beside the extracted application folder. `setup-towerscout.cmd`
discovers it and verifies the matching `.sha256` sidecar.

## Required Download Verification For The Unsigned Package

The authoritative release page or release notes must display the SHA-256 for
the exact Application Package and Model & Data Package ZIPs. Before extraction
or unblocking, compare those values with the matching `.sha256` sidecars and
locally calculated hashes. A sidecar downloaded beside a ZIP is not by itself
proof of who published both files. Run these commands from the `TowerScoutUAT`
working folder that contains only the four copied release files:

```powershell
$appZip = Get-ChildItem -File "*-cpu.zip"
$assetZip = Get-ChildItem -File "*-assets-*.zip"
Get-FileHash -Algorithm SHA256 -LiteralPath $appZip.FullName
Get-Content -LiteralPath ($appZip.FullName + ".sha256")
Get-FileHash -Algorithm SHA256 -LiteralPath $assetZip.FullName
Get-Content -LiteralPath ($assetZip.FullName + ".sha256")
```

The `Hash` value from `Get-FileHash` must match the SHA-256 value in the
corresponding `.sha256` file. If the values do not match, stop validation and
obtain a fresh copy of the affected release artifact.

The calculated value and sidecar must also match the value displayed in the
authoritative release record. If that value is missing, stop and contact the
release owner rather than treating the sidecar alone as release authentication.

If PowerShell says `Get-FileHash` is not recognized, use Windows `certutil`
instead and compare the printed SHA-256 value to the matching `.sha256` file:

```powershell
certutil -hashfile .\towerscout-<release-version>-cpu.zip SHA256
Get-Content .\towerscout-<release-version>-cpu.zip.sha256
certutil -hashfile .\towerscout-<release-version>-assets-<asset-version>.zip SHA256
Get-Content .\towerscout-<release-version>-assets-<asset-version>.zip.sha256
```

The `*` wildcard should match exactly one Model & Data Package ZIP and exactly
one matching `.sha256` file. If PowerShell prints more than one asset ZIP or
checksum file, move old TowerScout downloads out of the folder and run the
commands again.

Example: these values match:

```text
Get-FileHash output:
HASH      0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF

.sha256 file:
0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef  towerscout-<release-version>-cpu.zip
```

Uppercase and lowercase letters are not important. The letters and numbers
must otherwise be identical.

After all three sources agree, use the Application Package ZIP's Windows
Properties dialog to select `Unblock` only if Windows displays that option,
then use File Explorer's `Extract All`. Do not unblock or run a file whose hash
has not been verified.

## Application Package Layout

After extracting only the Application Package ZIP, the package root should include:

```text
setup-towerscout.cmd
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
ghcr.io/j-schulein/towerscout:<release-version>-cpu@sha256:<digest>
```

`IMAGE.txt`, `.env.example`, and `release-manifest.v1.json` record the selected
PyTorch flavor, either `cpu` or `cuda128`.
The CPU package rejects `-Gpu on`. The CUDA package still requires GPU
readiness evidence before it is treated as a valid GPU launch.

Source-checkout or local-validation defaults use the explicit `latest-cpu`
tag when no package digest is present. Do not use a bare `latest` image tag for
release or package instructions.

## Guided Setup Path

For first setup, prefer the top-level setup entry point:

```powershell
.\setup-towerscout.cmd
```

The expected first-cohort folder layout is:

```text
C:\Users\<you>\Documents\TowerScoutUAT\
  towerscout-<release-version>-cpu.zip
  towerscout-<release-version>-cpu.zip.sha256
  towerscout-<release-version>-assets-<asset-version>.zip
  towerscout-<release-version>-assets-<asset-version>.zip.sha256
  towerscout-<release-version>-cpu\
    setup-towerscout.cmd
```

The setup wrapper defaults to Docker Desktop and `-Gpu off`. It searches the
extracted application folder and its parent folder for one matching Model &
Data Package ZIP, requires the matching `.sha256` sidecar, then delegates to
the validated bootstrap path.

Setup performs the checks that users most often miss:

- Docker or Podman CLI, daemon/machine, and Compose-provider readiness.
- Automatic engine selection prefers a reachable engine over an installed but
  stopped engine.
- WSL 2 hint for Docker Desktop on Windows.
- Local port availability.
- Minimum free disk space.
- Release manifest and control asset-manifest presence.
- Application Package checksum verification when the original Application
  Package ZIP is still beside the extracted folder.
- Model & Data Package checksum verification.
- Asset ZIP safety, direct-root layout, and control/asset manifest matching.
- Named-volume asset import through `scripts\import-assets.ps1` with hash
  verification enabled; Podman can fall back to direct `podman cp` when the
  selected Compose provider cannot copy files.
- Startup through `scripts\launch.ps1`.

If automatic ZIP discovery is ambiguous, move old ZIPs out of the UAT folder or
pass explicit paths:

```powershell
.\setup-towerscout.cmd -PackageZip "C:\Users\<you>\Documents\TowerScoutUAT\towerscout-<release-version>-cpu.zip" -AssetZip "C:\Users\<you>\Documents\TowerScoutUAT\towerscout-<release-version>-assets-<asset-version>.zip"
```

Useful setup options:

- `-VerifyOnly`: run prerequisite, checksum, release, and asset-layout checks
  without importing assets or starting TowerScout.
- `-SkipAssetImport`: run preflight and launch while leaving already-staged
  assets untouched.
- `-Port <port>`: choose an unused non-default port and then use it on every
  later command.
- `-Engine podman`: use the Podman path after its machine and package-local
  Compose provider are ready.
- `-Gpu auto` or `-Gpu on`: use the CUDA package on a release-listed NVIDIA
  workstation after the selected engine's GPU checks pass.

Expected result: setup prints clear checks, rejects mismatched checksums or
unsafe asset ZIPs before mutating package assets, imports valid staged assets,
starts TowerScout, and explains readiness state. It is meant for first setup
and support validation. `start.bat` remains the normal direct launch path after
setup is complete.

Abbreviated successful first-run output should look similar to:

```text
TowerScout setup
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
after setup has already opened TowerScout.

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

Use this manual fallback when setup is not being used for asset ZIP staging.
The Model & Data Package ZIP root must contain these entries directly:

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
folder, treat the layout as ambiguous and stop before continuing.

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

The release path now has separate CPU and CUDA Application Packages. The CPU
package is the normal package for non-GPU users. The CUDA package is for
support-validated NVIDIA GPU workstations. The default launch path is CPU-safe
for either package:

```powershell
.\start.bat -Gpu off
```

GPU launch is optional and must be validated on the workstation before it is
treated as supported:

```powershell
.\start.bat -Engine docker -Gpu auto
.\start.bat -Engine docker -Gpu on
.\start.bat -Engine podman -Gpu on
```

- `-Gpu off` uses the default Compose file and sets `TOWERSCOUT_DEVICE=cpu`.
- `-Gpu auto` sets `TOWERSCOUT_DEVICE=auto` and starts without the selected
  engine's GPU overlay unless support has set the matching overlay validation
  gate in the shell or `.env`.
- `-Gpu on` adds the selected engine's GPU overlay, sets
  `TOWERSCOUT_DEVICE=cuda`, and fails readiness if CUDA is unavailable to the
  container.

`-Gpu on` is rejected in the CPU package with package-aware guidance to use the
CUDA package. GPU launch requires the CUDA package plus engine-specific NVIDIA
container support. A host `nvidia-smi` result alone is not enough; Docker or
Podman must be able to pass the GPU into the TowerScout container. Podman GPU
requires the CDI path: approved non-Docker-Desktop Compose provider,
WSL2-backed Podman machine, NVIDIA Container Toolkit/CDI registration, and a
readiness result with `selected_device=cuda`.

For optional GPU validation, the workstation also needs an NVIDIA GPU, a
current NVIDIA or OEM production Windows driver that lists the exact GPU,
selected-engine GPU validation, and site-approved proof
that the engine can expose the GPU to a test container. Do not set
`TOWERSCOUT_GPU_AUTO_OVERLAY=1` or `TOWERSCOUT_PODMAN_GPU_OVERLAY=1` until that
validation has passed on the workstation.

**GPU and driver boundary**: The CUDA 12.8 Application Package has a
Volta-or-newer architecture expectation, but only exact GPU/driver/Windows/WSL/
engine/toolkit combinations in the release notes are qualified. Maxwell and
Pascal are unsupported by the CUDA package; use the CPU package or `-Gpu off`.
Never install a Linux display driver inside WSL. Refresh Podman CDI after a
Windows driver update. A newer/older architecture mismatch requires the
correct package or CPU path, never a forced architecture override.

The measured CUDA image is `14.4 GB`. Plan at least `35 GB` free for normal
pull/unpack plus assets and volumes and at least `60 GB` for one support source
build. A full three-stage A/B/C qualification grew Docker's virtual disk
by about `120 GB`; a full comparative build should budget `150 GB`.

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

Provider-key policy:

- Browser map SDK keys are client-visible to someone with access to the running
  browser app.
- Provider keys must be site/user-owned unless a separate owner-approved exception
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

TowerScout currently accepts one Google key and uses it for both browser and
application requests. The browser can see that key. Do not create separate
browser/server keys for TowerScout because there is only one Google field.
Use a dedicated limited project, API restrictions, quotas, alerts, monitoring,
and rotation. Google publishes current API-key guidance at:

```text
https://developers.google.com/maps/api-security-best-practices
```

Azure Maps subscription keys must support TowerScout's use of:

- Azure Maps Web SDK.
- Imagery/tiles.
- Search and geocoding.

For the local package deployment, Azure shared-key authentication is acceptable only
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
3. Search for an approved public/non-sensitive location or navigate the map manually.
4. Define a small search area with a circle or custom shape.
5. Select `Estimate tiles`.
6. Confirm the tile count and expected time are reasonable.
7. Select `Find towers`.
8. Review results in the detection list and map.
9. Export CSV/KML or dataset results only if allowed by the site workflow.

Use the owner-provided public fixture when available. If a fixture has not been
provided, use a non-sensitive approved area and keep the first run small,
preferably `1-6` tiles. A successful smoke check means the detection workflow
completes without crashing and the map/review panel update, even if the result
count is zero for the selected area.

The UAT package defaults to a `TOWERSCOUT_PILOT_MAX_TILES=100` guard. If a
tester selects a larger area, TowerScout stops before imagery download or model
inference and asks the user to choose a smaller area.

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
- `podman compose` can use an approved non-Docker-Desktop Compose provider.
- If needed, `PODMAN_COMPOSE_PROVIDER` points to the approved provider.

The selected Compose provider must be explicitly validated in the target
environment and match the provider/version named by the authoritative release
record. The launcher reports Compose-provider information before startup,
rejects Docker Desktop provider paths for the Podman path, and validates a
`PODMAN_COMPOSE_PROVIDER` override before Compose is invoked.

If no approved provider is present, the package includes the connected helper:

```powershell
.\scripts\install-podman-compose-provider.cmd -Apply
```

The helper installs the approved `podman-compose` provider into a package-local
isolated Python environment, verifies pinned package hashes, backs up `.env`,
and updates only `PODMAN_COMPOSE_PROVIDER`. Running the helper without
`-Apply` prints the recommended `.env` setting without changing `.env`.

If Podman reports `rootlessport listen ... bind: address already in use` even
when Windows shows the port as free, retry with a non-default package port and
use that same port on status/log/import commands:

```powershell
.\setup-towerscout.cmd -Engine podman -Gpu off -Port 5009
.\scripts\status.cmd -Engine podman -Port 5009
```

If the error follows the same port after retry, ask Local IT to inspect and
clear local Podman container/port state before continuing.

### Docker Desktop

Docker Desktop use depends on local license, procurement, endpoint policy, and
installation approval. For the primary package path, Docker Desktop should be
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

Run the guided TLS repair helper for the selected engine. The dry run inspects
the provider TLS chain as Windows sees it, avoids selecting the provider leaf
certificate, and prints the exact apply command when it finds one safe CA
candidate. The helper copies the CA into the selected engine's persistent
`towerscout_config` volume, builds a combined CA bundle, verifies provider TLS
with an invalid test key, and updates the local `.env` so future TowerScout
starts use the bundle automatically.

Use the repair command shown by TowerScout; it includes the active `-Port`.
If entering commands manually, use the same `-Port` on every repair and
`start.bat` command. The examples below use port 5000 explicitly; replace every
`-Port 5000` with the active port (for example, `-Port 5211`) when needed.

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off -Port 5000
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off -Port 5000 -Apply
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu off -Port 5000
```

For Podman:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine podman -Gpu off -Port 5000
.\scripts\repair-provider-tls.cmd -Provider google -Engine podman -Gpu off -Port 5000 -Apply
.\scripts\stop.cmd -Engine podman
.\start.bat -Engine podman -Gpu off -Port 5000
```

For GPU use, preserve the chosen GPU mode in the
repair and restart commands, such as `-Gpu auto` or `-Gpu on`.

If the site blocks Google but uses Azure, choose Azure verification:

```powershell
.\scripts\repair-provider-tls.cmd -Provider azure -Engine docker -Gpu off -Port 5000
```

Do not paste dry-run certificate subjects, issuer details, or thumbprints into
public issue comments or release evidence. If Local IT knows the correct
Windows certificate thumbprint or has an exported PEM/CER/CRT file, pass
`-Thumbprint` or `-CertificatePath` to `scripts\repair-provider-tls.cmd`. A
website leaf/server certificate is not sufficient. If automatic discovery is
ambiguous or unavailable, Local IT may use the lower-level
`scripts\import-tls-ca.cmd` command with the known CA thumbprint or file.

The final package requires normal TLS verification. Use the CA import workflow
with Local IT or stop; do not disable certificate verification.

The current provider TLS repair path is the guided script workflow above. The
package now ships host-helper scaffolding for a future browser-triggered repair
flow, but that control plane remains disabled in the current release baseline;
see [docs/support/host-helper.md](support/host-helper.md).

### Restricted Networks

The normal path expects the selected engine to pull the pinned image from
GHCR. A bundled OCI image archive is not part of the supported control
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
  readiness diagnostics. `-Gpu on` must report `selected_device=cuda` before it
  is treated as a valid GPU launch.

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

The YOLO-enabled package/image is distributed with AGPL-3.0 obligations
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

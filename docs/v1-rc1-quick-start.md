# TowerScout V1 RC1 Quick Start

This is the short Windows pilot path for the TowerScout V1 RC1 `agpl-yolo`
release package. It assumes a Windows 11 AMD64 workstation, Docker Desktop as
the primary pilot engine, normal outbound internet access, and one approved
Google Maps or Azure Maps provider key.

For detailed support guidance, see `docs/v1-rc1-package-guide.md`.

Terms used in this guide:

- **Application Package**: the smaller TowerScout app/control ZIP that contains
  scripts, docs, Compose files, and release metadata.
- **Model & Data Package**: the larger asset ZIP, also called the asset bundle,
  that contains model weights and ZIP-code data.

## Before You Start

Install or confirm these prerequisites before opening the TowerScout package.
If your workstation is managed by IT, ask your site administrator before
installing WSL, Docker Desktop, Podman, or provider credentials.

- Windows 11 on AMD64.
- Windows PowerShell. This is included with Windows.
- A modern browser such as Microsoft Edge or Google Chrome.
- WSL 2 and hardware virtualization support for Docker Desktop's normal Windows
  Linux-container backend. Docker's current Windows requirements include WSL
  `2.1.5` or later, virtualization enabled in BIOS/UEFI, and at least 8 GB RAM.
- Normal outbound internet access so the container engine can pull the pinned
  TowerScout image from GHCR and TowerScout can reach the selected map provider.
- Enough local disk space for the Application Package, Model & Data Package,
  container image, and Docker or Podman volumes. Plan for at least `15 GB`
  free; `25 GB` free is a better target for first setup. CUDA-capable images use
  substantially more space than CPU-only images.
- One container engine, selected as follows:
  - Docker Desktop is the primary V1 RC1 pilot path. During Docker Desktop
    installation, keep the WSL 2 backend selected when prompted, start Docker
    Desktop from the Windows Start menu, and wait until Docker Desktop reports
    that it is running.
  - Podman is a qualified package-runtime option only when support tells you to
    use it and the workstation already has a running Podman machine plus a
    working Compose provider such as `podman-compose`.
- One valid site/user-owned Google Maps or Azure Maps provider key.

You do not need Git, Python, Conda, Node.js, VS Code, or a source-code checkout
for the normal V1 RC1 package path.

Unless support has explicitly assigned you the Podman path, stop here and
contact your site administrator or support lead if Docker Desktop is not
already installed and approved on your workstation. Also stop if you do not
already have a valid restricted provider key.

If both Docker and Podman are installed, the launcher's automatic engine
selection can choose Docker first. If support or local policy tells you to use
Podman, pass `-Engine podman` on every helper command.

### If Docker Desktop Or WSL 2 Is Not Ready

If support asks you to check WSL 2, open PowerShell as Administrator and run:

```powershell
wsl --status
wsl --list --verbose
```

Expected result: WSL is installed, and any listed Linux distribution uses
version `2`. If WSL is not installed and your site allows you to install it,
Microsoft's current install path is:

```powershell
wsl --install
```

Restart the computer after installation if Windows asks. The first Linux
distribution launch may ask you to create a Linux username and password; that
is normal WSL setup and is separate from your Windows password.

After Docker Desktop is installed, open Docker Desktop from the Start menu. In
Docker Desktop Settings, the WSL 2 based engine should be selected when the
option is visible. Then open a normal PowerShell window and run:

```powershell
docker --version
docker compose version
```

Expected result: both commands print version information. If either command is
not recognized or says Docker is not running, keep Docker Desktop open and ask
support before continuing.

### How To Run The Commands In This Guide

Use Windows PowerShell, not the WSL/Ubuntu terminal, for the package commands.

To open PowerShell in a folder:

1. Open File Explorer.
2. Open the folder that contains the downloaded release files or extracted
   TowerScout package.
3. Click the address bar at the top of File Explorer.
4. Type `powershell` and press Enter.

Expected result: a blue or black PowerShell window opens, and the prompt shows
the folder path. Copy one command at a time from this guide, paste it into
PowerShell, and press Enter. Commands that start with `.\` run a script from
the current folder.

## Stop And Contact Support

Stop before continuing and contact your support lead if any of these happen:

- Unless support explicitly assigned you the Podman path, Docker Desktop is not
  installed, not approved, or cannot start.
- WSL is not installed, or `wsl --list --verbose` shows version `1` and you do
  not have administrator approval to update it.
- A downloaded file checksum does not match its `.sha256` file.
- The asset import reports missing, corrupt, or hash-failed files.
- TowerScout reports readiness state `fatal`.
- Provider validation repeatedly fails after you confirm the key is correct.

Do not troubleshoot by sharing provider keys, full `.env` files, raw logs, raw
screenshots, private AOIs, browser network traces, cached provider responses,
or exported datasets unless your site has an approved handling procedure.

## 1. Get The Release Files From GitHub Releases

In your browser, open the TowerScout GitHub repository release page:

```text
https://github.com/J-Schulein/TowerScout/releases
```

Open the exact release that support told you to use, such as `v0.1.0-rc1`. If
support provides a direct release URL, use that link.

In the release `Assets` section, download all four TowerScout release files
into a new empty local folder, such as:

```text
C:\Users\<you>\Downloads\TowerScout-v0.1.0-rc1
```

Download these files from the same release:

- Application Package ZIP: `towerscout-v0.1.0-rc1.zip`
- Application Package checksum: `towerscout-v0.1.0-rc1.zip.sha256`
- Model & Data Package ZIP: `towerscout-v0.1.0-rc1-assets-<asset-version>.zip`
- Model & Data Package checksum:
  `towerscout-v0.1.0-rc1-assets-<asset-version>.zip.sha256`

Do not use GitHub's automatic `Source code (zip)` or `Source code (tar.gz)`
downloads for normal pilot setup. Those files are source snapshots, not the
TowerScout release package. Do not use the green GitHub `Code` button for the
normal pilot install.

## 2. Confirm The Release Files Match

Confirm you downloaded or received the Application Package ZIP and Model & Data
Package ZIP for the same release version:

- `towerscout-v0.1.0-rc1.zip`
- `towerscout-v0.1.0-rc1.zip.sha256`
- `towerscout-v0.1.0-rc1-assets-<asset-version>.zip`
- `towerscout-v0.1.0-rc1-assets-<asset-version>.zip.sha256`

The exact Model & Data Package filename can change by release. The Application
Package, Model & Data Package, `IMAGE.txt`, `release-manifest.v1.json`, and
`webapp/asset_manifest.v1.json` must describe the same release handoff.

Do not type the angle brackets from `<asset-version>` into PowerShell. Replace
the placeholder with the exact filename text from the Model & Data Package ZIP
you downloaded. Example only:

```text
towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip
```

The release version must match between the Application Package and the Model &
Data Package. For example, both should include `v0.1.0-rc1` in the filename. If
the versions differ, stop and download the matching files from the same GitHub
release.

## 3. Verify The Downloads Before Extracting

In PowerShell, compare each downloaded ZIP to its matching `.sha256` file before
extracting either package. Run these commands from the new folder that contains
only the four downloaded release files:

```powershell
Get-FileHash .\towerscout-v0.1.0-rc1.zip -Algorithm SHA256
Get-Content .\towerscout-v0.1.0-rc1.zip.sha256
Get-FileHash .\towerscout-v0.1.0-rc1-assets-*.zip -Algorithm SHA256
Get-Content .\towerscout-v0.1.0-rc1-assets-*.zip.sha256
```

The `Hash` value from `Get-FileHash` must match the SHA-256 value in the
corresponding `.sha256` file. If either value does not match, stop and obtain a
fresh copy of the release artifact before continuing.

The `*` wildcard should match exactly one Model & Data Package ZIP and exactly
one matching `.sha256` file. If PowerShell prints more than one asset ZIP or
checksum file, move old TowerScout downloads out of the folder and run the
commands again.

Example: these two values match, so the ZIP is valid:

```text
Get-FileHash output:
HASH      0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF

.sha256 file:
0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef  towerscout-v0.1.0-rc1.zip
```

Uppercase and lowercase letters are not important. The letters and numbers
must otherwise be the same.

## 4. Extract The Application Package

Extract the Application Package ZIP to a normal local folder such as:

```text
C:\Users\<you>\TowerScout-v0.1.0-rc1
```

After extraction, the folder should contain `bootstrap.cmd`, `start.bat`,
`compose.yaml`, `compose.gpu.yaml`, `scripts\`, `docs\`, compliance files,
`IMAGE.txt`, `SHA256SUMS.txt`, and an empty `assets\` folder.

## 5. Run The Guided Bootstrap

The recommended first setup path is `bootstrap.cmd`. It checks prerequisites,
verifies Application Package checksums only when `-PackageZip` is provided,
verifies Model & Data Package checksums only when `-AssetZip` is provided,
rejects unsafe or nested asset ZIP layouts, imports staged assets with hash
verification, starts TowerScout, and explains readiness in plain language.

If the Model & Data Package ZIP and its `.sha256` file are in the package
folder, run this from PowerShell in the package folder. Replace
`<asset-version>` with the exact filename value from the release. Do not type
the angle brackets:

```powershell
.\bootstrap.cmd -Engine docker -Gpu off -AssetZip .\towerscout-v0.1.0-rc1-assets-<asset-version>.zip
```

If the ZIP files are still in your Downloads folder or another folder, either
copy the Model & Data Package ZIP and its `.sha256` file into the package
folder, or pass the full path to `-AssetZip`.

To have bootstrap recheck both release ZIP checksums, pass both ZIP paths:

```powershell
.\bootstrap.cmd -Engine docker -Gpu off -PackageZip C:\Users\<you>\Downloads\towerscout-v0.1.0-rc1.zip -AssetZip C:\Users\<you>\Downloads\towerscout-v0.1.0-rc1-assets-<asset-version>.zip
```

Expected result: PowerShell prints `TowerScout bootstrap preflight`, reports
disk, port, engine, Compose, and WSL/Podman checks, verifies Application
Package and Model & Data Package checksums only for the ZIP paths passed with
`-PackageZip` and/or `-AssetZip`, imports assets if present, starts TowerScout,
and opens:

```text
http://localhost:5000
```

A successful first-run output will look similar to this abbreviated example:

```text
TowerScout bootstrap preflight
[OK] Engine docker is available
[OK] Compose is available
[OK] Model & Data Package checksum matched
[OK] Asset import completed with hash verification
[OK] TowerScout responded at http://localhost:5000
readiness: setup_required
```

`setup_required` is normal before provider setup is complete. After provider
setup and asset import are complete, readiness should become `ready`.

The first launch may download the TowerScout container image from GHCR. This
can take several minutes on first run. Keep the PowerShell window open while
Docker downloads and starts the image.

Readiness may be `setup_required` because provider setup is not complete, or
`degraded` because assets are not imported yet. That is expected during first
setup.

If the browser does not open, leave PowerShell open and manually open
`http://localhost:5000`.

If support tells you to use a specific engine, keep using the same `-Engine`
value for every helper command because Docker and Podman use separate named
volumes:

```powershell
.\bootstrap.cmd -Engine podman -Gpu off -AssetZip .\towerscout-v0.1.0-rc1-assets-<asset-version>.zip
```

If bootstrap cannot find or start a container engine, confirm the selected
engine is installed and running before continuing. For Podman, confirm the
Podman machine is started and a Compose provider is available. For Docker,
confirm Docker Desktop is running.

## 6. Manual Asset Staging And Import Fallback

Use this section only if support tells you not to use `bootstrap.cmd
-AssetZip`, or if you already extracted the Model & Data Package manually.

Open the Model & Data Package ZIP. Its root should contain:

```text
model_params\
data\
asset_manifest.v1.json
```

Extract those entries into the package `assets\` folder so the result is:

```text
assets\
  model_params\
  data\
  asset_manifest.v1.json
```

After extraction, open the package `assets\` folder and confirm you see
`model_params`, `data`, and `asset_manifest.v1.json` directly inside it.

If you see this layout, it is wrong:

```text
assets\
  assets\
    model_params\
    data\
    asset_manifest.v1.json
```

Move the inner `model_params`, `data`, and `asset_manifest.v1.json` entries up
one level so they sit directly inside the package `assets\` folder. If you are
unsure, stop and ask support before importing assets.

From PowerShell in the package folder, import the assets:

```powershell
.\scripts\import-assets.cmd -Engine docker -Source assets -VerifyHashes -RestartWaitSeconds 180
```

If you started with an explicit engine, use that same engine here:

```powershell
.\scripts\import-assets.cmd -Engine podman -Source assets
```

If you started TowerScout on a non-default port, use that same `-Port` value
when importing assets so the helper recreates the Compose service with the same
port binding:

```powershell
.\scripts\import-assets.cmd -Engine docker -Source assets -Port 5001 -RestartWaitSeconds 180
```

For release-candidate or support validation, verify hashes during import:

```powershell
.\scripts\import-assets.cmd -Engine docker -Source assets -VerifyHashes -RestartWaitSeconds 180
```

Or, with an explicit engine:

```powershell
.\scripts\import-assets.cmd -Engine podman -Source assets -VerifyHashes
```

The import helper uses the selected engine's named volumes. If `.env` is
missing, the helper initializes it from the package `.env.example` before
starting the selected container stack. After copying assets, the helper restarts
TowerScout so the running application discovers the imported model files before
the first detection run.

Expected result: the command finishes without missing or corrupt asset errors,
then waits for TowerScout to respond after restart. If hash verification fails,
stop and ask support for the correct Model & Data Package.

## 7. Start TowerScout Later

Skip this section during first setup if bootstrap already opened TowerScout.
Use this command when reopening TowerScout after setup is complete, or when
support asks you to isolate direct launch behavior. From the package folder,
run:

```powershell
.\start.bat -Engine docker -Gpu off
```

The default launch path is CPU-safe. It sets `TOWERSCOUT_DEVICE=cpu` for the
launch and does not request GPU devices.

Use `localhost`, not `127.0.0.1`, for normal browser use:

```text
http://localhost:5000
```

## 8. Optional GPU Launch

GPU launch is optional and Docker-first. Do not use it as the normal first-run
path unless support is validating a workstation with NVIDIA Docker GPU access.

CPU-safe default:

```powershell
.\start.bat -Gpu off
```

Optional Docker GPU modes:

```powershell
.\start.bat -Engine docker -Gpu auto
.\start.bat -Engine docker -Gpu on
```

- `-Gpu off` forces CPU execution.
- `-Gpu auto` uses CPU fallback unless `TOWERSCOUT_GPU_AUTO_OVERLAY=1` has been
  set after workstation-specific Docker GPU validation.
- `-Gpu on` requests the Docker GPU overlay and fails readiness if CUDA is not
  available to the container.

Podman GPU launch is not validated for V1 RC1. Use the CPU-safe Podman launch
unless support provides a site-specific GPU procedure.

## 9. Complete Setup

When the browser opens, use Setup Wizard or Settings to configure one provider:

- Google Maps, or
- Azure Maps.

One valid provider key is enough to start. Provider keys for the V1 RC1 pilot
must be site/user-owned and restricted. Browser map SDK keys are visible to
someone who can access the running browser app, so do not use an unrestricted
shared TowerScout project key.

Google keys must support TowerScout's Maps JavaScript, Places/autocomplete,
Static Maps imagery, and Geocoding usage. Azure Maps subscription keys must
support TowerScout's Web SDK, imagery, search, and geocoding usage.

Expected result: Setup Wizard saves the provider settings and TowerScout reloads
or reports that setup is complete. Do not paste the provider key into issue
reports, screenshots, or support chat.

## 10. Confirm Success

Run:

```powershell
.\scripts\status.cmd -Engine docker
```

If you started with an explicit engine, use the same engine:

```powershell
.\scripts\status.cmd -Engine podman
```

Expected readiness states:

- `setup_required`: TowerScout is running, but provider setup is not complete.
- `degraded`: TowerScout is running, but assets or another recoverable
  capability are missing.
- `ready`: provider setup and required assets are present.
- `fatal`: TowerScout cannot safely serve the app; collect support evidence.

For a small smoke check, open TowerScout, choose a provider, and use the
owner-provided public test area or another non-sensitive approved area. Support
should provide the smoke-test fixture before UAT starts: provider,
public/non-sensitive location name, expected tile range, and whether zero
detections is an acceptable result. Do not choose a private investigation AOI
for the first smoke test. Keep the first run small, preferably `1-6` tiles.

Suggested smoke flow:

1. Search for or navigate to the approved test location.
2. Draw a small circle or custom shape.
3. Select `Estimate tiles`.
4. Confirm the tile count is small enough for the pilot.
5. Select `Find towers`.
6. Confirm the run completes and the review panel updates.

Expected result: status is `ready` before the detection smoke, and the detection
workflow completes without crashing. Results may be zero or more detections
depending on the approved area and provider imagery, but the map and right-hand
review panel should update consistently.

## 11. Stop Or Restart

Stop TowerScout:

```powershell
.\scripts\stop.cmd -Engine docker
```

Start again:

```powershell
.\start.bat -Engine docker -Gpu off
```

Provider setup and imported assets are stored in named volumes and should
survive container restarts and replacement.

Important: always use the same `-Engine` value you used during setup. Docker
Desktop and Podman use separate local storage. If you switch engines, provider
setup or imported assets may appear to be missing because they are stored under
the other engine.

## 12. Source, Licenses, And Help

The YOLO-enabled V1 RC1 package/image is not Apache-2.0-only. It is distributed
with AGPL-3.0 obligations because it includes Ultralytics YOLOv5 runtime source
and YOLO-derived detector weights.

Find release notices in the package:

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

When TowerScout is running, Settings includes Resource Links for Project
Overview, User Guide, Source/licenses, Video Guides, and the research article.
The source/license notice is also available from these local routes:

```text
http://localhost:5000/license      formatted browser page
http://localhost:5000/license.txt  plain-text combined notices
```

Use `/license.txt` when support needs plain text for scripts, copy/paste, or
archival use.

## 13. If Something Fails

Run:

```powershell
.\scripts\status.cmd -Engine docker
.\scripts\logs.cmd -Engine docker -Tail 200
```

Use the same `-Engine` value on status/log commands if support asked you to
start with a specific engine.

For package/image metadata, support may ask you to copy the package folder name
and the contents of `IMAGE.txt`:

```powershell
Get-Content .\IMAGE.txt
```

If PowerShell says a command is not recognized, confirm the PowerShell prompt is
open in the extracted TowerScout package folder and that the command starts
with `.\`. If Docker commands are not recognized, open Docker Desktop from the
Start menu and wait until it reports that it is running.

Do not share `.env`, provider keys, raw screenshots, raw browser network
traces, cached provider responses, uploaded investigation files, exported
datasets, named-volume contents, or unreviewed raw logs unless your site has an
approved support-handling procedure.

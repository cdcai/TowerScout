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
- TowerScout setup reports that a ZIP checksum does not match its `.sha256`
  file.
- The asset import reports missing, corrupt, or hash-failed files.
- TowerScout reports readiness state `fatal`.
- Provider validation repeatedly fails after you confirm the key is correct.
  On managed networks, this may mean the container does not trust the local
  TLS inspection certificate; support can import the site CA without needing
  your provider key.

Do not troubleshoot by sharing provider keys, full `.env` files, raw logs, raw
screenshots, private AOIs, browser network traces, cached provider responses,
or exported datasets unless your site has an approved handling procedure.

## 1. Get The Release Files From GitHub Releases

In your browser, open the TowerScout GitHub repository release page:

```text
https://github.com/J-Schulein/TowerScout/releases
```

Open the exact release that support told you to use, such as `v0.1.0-rc2`. If
support provides a direct release URL, use that link.

In the release `Assets` section, download all four TowerScout release files.
Most browsers save downloaded files to your Windows `Downloads` folder.

After the downloads finish, create a new empty working folder, such as:

```text
C:\Users\<you>\Documents\TowerScoutUAT
```

Copy the four downloaded TowerScout files from your `Downloads` folder and
paste them into this `TowerScoutUAT` working folder.

Download these files from the same release:

- Application Package ZIP: `towerscout-v0.1.0-rc2.zip`
- Application Package checksum: `towerscout-v0.1.0-rc2.zip.sha256`
- Model & Data Package ZIP: `towerscout-v0.1.0-rc2-assets-<asset-version>.zip`
- Model & Data Package checksum:
  `towerscout-v0.1.0-rc2-assets-<asset-version>.zip.sha256`

Keep these four files together in the `TowerScoutUAT` working folder. Only the
Application Package ZIP is extracted in the normal setup path. Leave the Model
& Data Package ZIP and both `.sha256` files as files; do not extract or move
them into the `assets\` folder.

Do not use GitHub's automatic `Source code (zip)` or `Source code (tar.gz)`
downloads for normal pilot setup. Those files are source snapshots, not the
TowerScout release package. Do not use the green GitHub `Code` button for the
normal pilot install.

## 2. Confirm The Release Files Match

Before extracting anything, confirm the folder contains these four files from
the same release:

- `towerscout-v0.1.0-rc2.zip`
- `towerscout-v0.1.0-rc2.zip.sha256`
- `towerscout-v0.1.0-rc2-assets-<asset-version>.zip`
- `towerscout-v0.1.0-rc2-assets-<asset-version>.zip.sha256`

The exact Model & Data Package filename can change by release. The release
version must match between the Application Package and the Model & Data
Package. For example, both should include `v0.1.0-rc2` in the filename. If the
versions differ, stop and download the matching files from the same GitHub
release.

Do not type the angle brackets from `<asset-version>` into PowerShell. Replace
the placeholder with the exact filename text from the Model & Data Package ZIP
you downloaded. Example only:

```text
towerscout-v0.1.0-rc2-assets-towerscout-v1-assets-2026-05-05.zip
```

## 3. Extract Only The Application Package

In the `TowerScoutUAT` folder, extract only the Application Package ZIP:

```text
towerscout-v0.1.0-rc2.zip
```

Extract it inside the `TowerScoutUAT` folder. Most Windows ZIP tools will
create an extracted folder named:

```text
C:\Users\<you>\Documents\TowerScoutUAT\towerscout-v0.1.0-rc2
```

Do not extract the Model & Data Package ZIP for the normal setup path. After
extracting only the Application Package ZIP, the working folder should look
like this:

```text
TowerScoutUAT\
  towerscout-v0.1.0-rc2.zip
  towerscout-v0.1.0-rc2.zip.sha256
  towerscout-v0.1.0-rc2-assets-<asset-version>.zip
  towerscout-v0.1.0-rc2-assets-<asset-version>.zip.sha256
  towerscout-v0.1.0-rc2\
    setup-towerscout.cmd
    bootstrap.cmd
    start.bat
    scripts\
    docs\
    assets\
```

The `assets\` folder starts empty. Do not put the Model & Data Package ZIP
inside `assets\`.

## 4. Run TowerScout Setup

Open PowerShell in the extracted application folder that contains
`setup-towerscout.cmd`, then run:

Before running setup, confirm Docker Desktop is open and running. If support
assigned the Podman path, confirm the Podman machine is running and the Compose
provider is available. For Docker GPU setup, see the optional Docker GPU track
below for the GPU setup command.

```powershell
.\setup-towerscout.cmd
```

The setup command checks prerequisites, finds the Model & Data Package ZIP in
the extracted folder or parent `TowerScoutUAT` folder, verifies the matching
`.sha256` files, rejects unsafe or nested asset ZIP layouts, imports the
assets with hash verification, starts TowerScout, and explains readiness in
plain language.

Expected result: PowerShell prints `TowerScout setup`, reports disk, port,
engine, Compose, and WSL/Podman checks, verifies the ZIP checksums, imports
assets, starts TowerScout, and opens:

```text
http://localhost:5000
```

A successful first-run output will look similar to this abbreviated example:

```text
TowerScout setup
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

If TowerScout finds an older UAT container from a previous session, setup starts
a fresh container while keeping saved setup, imported assets, and support logs
in named volumes.

Readiness may be `setup_required` because provider setup is not complete, or
`degraded` because assets are not imported yet. That is expected during first
setup.

If the browser does not open, leave PowerShell open and manually open
`http://localhost:5000`.

If setup reports that more than one Model & Data Package ZIP was found, move
old TowerScout ZIPs out of the folder and run setup again. If support asks you
to pass an explicit ZIP path, use:

```powershell
.\setup-towerscout.cmd -AssetZip C:\Users\<you>\Documents\TowerScoutUAT\towerscout-v0.1.0-rc2-assets-<asset-version>.zip
```

Do not type the angle brackets in `<asset-version>`. Use the exact Model &
Data Package filename.

If setup cannot find or start a container engine, confirm the selected
engine is installed and running before continuing. For Podman, confirm the
Podman machine is started and a Compose provider is available. For Docker,
confirm Docker Desktop is running.

## 5. Optional Runtime Validation Tracks

Run the default Docker CPU setup first unless support assigned a different
track. If support asks you to validate Podman, run setup with Podman and keep
using `-Engine podman` on later status, logs, import, stop, and start commands:

```powershell
.\setup-towerscout.cmd -Engine podman
```

If support asks you to validate Docker GPU behavior on a workstation with
NVIDIA Docker GPU support, use one of these setup commands:

```powershell
.\setup-towerscout.cmd -Engine docker -Gpu auto
.\setup-towerscout.cmd -Engine docker -Gpu on
```

Use `-Gpu auto` for exploratory GPU validation with CPU fallback. Use `-Gpu on`
only when support expects CUDA to be available inside the container.

## 6. Manual Asset Staging And Import Fallback

Use this section only if support tells you not to use `setup-towerscout.cmd`,
or if you already extracted the Model & Data Package manually.

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

Skip this section during first setup if setup already opened TowerScout.
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

Managed-network note: if Google or Azure provider validation fails even though
the key is correct, and support sees `CERTIFICATE_VERIFY_FAILED` in container
logs, the problem is usually local TLS inspection. Support should import the
site CA for the selected engine, then restart TowerScout:

```powershell
.\scripts\import-tls-ca.cmd -Engine docker -Thumbprint <windows-certificate-thumbprint> -VerifyProvider google
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu off
```

The TLS helper stores the combined CA bundle in the selected engine's
`towerscout_config` volume and updates the local `.env` so future starts use
that bundle automatically. Do not send provider keys, full `.env` files, raw
logs, or browser network traces when reporting this issue.

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
for the first smoke test. Keep the first run small. The default RC1 Azure
smoke fixture is about `8` tiles.

Suggested smoke flow:

1. Search for or navigate to the approved test location.
2. Draw a small circle or custom shape.
3. Select `Estimate tiles`.
4. Confirm the tile count is small enough for the pilot.
5. Select `Find towers`.
6. Confirm the run completes and the review panel updates.

Expected result: status is `ready` before the detection smoke, and the detection
workflow completes without crashing. For the default RC1 Azure fixture, expect a
non-zero tower result. Exact counts may vary, but zero towers, no review-panel
update, or a crash should be reported as `BLOCKED` or `FAIL`. For any future
support-approved fixture, follow the zero-detection rule support provided for
that fixture.

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

TowerScout treats a healthy container that is less than 12 hours old as the
current UAT session. If a container is stopped, unhealthy, or older than 12
hours, the launcher starts a fresh container and keeps named volumes by
default. Support can change the session lifetime with `-SessionMaxHours` when a
longer validation session is approved.

Important: always use the same `-Engine` value you used during setup. Docker
Desktop and Podman use separate local storage. If you switch engines, provider
setup or imported assets may appear to be missing because they are stored under
the other engine.

## Appendix: Command Reference

Run commands from the extracted TowerScout application folder, such as
`C:\Users\<you>\Documents\TowerScoutUAT\towerscout-v0.1.0-rc2`.

| Purpose | Docker CPU/default | Docker GPU support-assigned | Podman CPU support-assigned |
|---|---|---|---|
| First setup | `.\setup-towerscout.cmd` | `.\setup-towerscout.cmd -Engine docker -Gpu auto` or `.\setup-towerscout.cmd -Engine docker -Gpu on` | `.\setup-towerscout.cmd -Engine podman` |
| Start or reopen | `.\start.bat -Engine docker -Gpu off` | `.\start.bat -Engine docker -Gpu auto` or `.\start.bat -Engine docker -Gpu on` | `.\start.bat -Engine podman -Gpu off` |
| Stop | `.\scripts\stop.cmd -Engine docker` | `.\scripts\stop.cmd -Engine docker` | `.\scripts\stop.cmd -Engine podman` |
| Restart | `.\scripts\stop.cmd -Engine docker`, then `.\start.bat -Engine docker -Gpu off` | `.\scripts\stop.cmd -Engine docker`, then the assigned Docker GPU start command | `.\scripts\stop.cmd -Engine podman`, then `.\start.bat -Engine podman -Gpu off` |
| Status | `.\scripts\status.cmd -Engine docker` | `.\scripts\status.cmd -Engine docker` | `.\scripts\status.cmd -Engine podman` |
| Logs if support asks | `.\scripts\logs.cmd -Engine docker -Tail 200` | `.\scripts\logs.cmd -Engine docker -Tail 200` | `.\scripts\logs.cmd -Engine podman -Tail 200` |
| TLS CA import if support asks | `.\scripts\import-tls-ca.cmd -Engine docker -Thumbprint <windows-certificate-thumbprint> -VerifyProvider google` | `.\scripts\import-tls-ca.cmd -Engine docker -Thumbprint <windows-certificate-thumbprint> -VerifyProvider google` | `.\scripts\import-tls-ca.cmd -Engine podman -Thumbprint <windows-certificate-thumbprint> -VerifyProvider google` |
| Manual asset import fallback | `.\scripts\import-assets.cmd -Engine docker -Source assets -VerifyHashes -RestartWaitSeconds 180` | `.\scripts\import-assets.cmd -Engine docker -Source assets -VerifyHashes -RestartWaitSeconds 180` | `.\scripts\import-assets.cmd -Engine podman -Source assets -VerifyHashes` |
| Longer support session | Add `-SessionMaxHours 24` to setup, start, or import commands when support approves it. | Add `-SessionMaxHours 24` to the assigned Docker GPU command when support approves it. | Add `-SessionMaxHours 24` to setup, start, or import commands when support approves it. |

Use `-Gpu auto` for exploratory Docker GPU validation with CPU fallback. Use
`-Gpu on` only when support expects CUDA to be available inside the container.
Podman GPU launch is not validated for V1 RC1.

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

Send only support-requested, reviewed/redacted excerpts from log output. Do not
send raw logs unless your site has an approved handling procedure.

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

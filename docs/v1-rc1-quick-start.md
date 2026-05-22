# TowerScout V1 RC1 Quick Start

This is the short Windows pilot path for the TowerScout V1 RC1 `agpl-yolo`
release package. It assumes a Windows 11 AMD64 workstation, a supported
container engine, normal outbound internet access, and one approved Google Maps
or Azure Maps provider key.

For detailed support guidance, see `docs/v1-rc1-package-guide.md`.

## Before You Start

Install or confirm these prerequisites before opening the TowerScout package:

- Windows 11 on AMD64.
- Windows PowerShell. This is included with Windows.
- A modern browser such as Microsoft Edge or Google Chrome.
- Normal outbound internet access so the container engine can pull the pinned
  TowerScout image from GHCR and TowerScout can reach the selected map provider.
- Enough local disk space for the control package, asset bundle, container
  image, and Docker or Podman volumes. Plan for several GB; CUDA-capable images
  use substantially more space than CPU-only images.
- One supported container engine:
  - Podman with a running Podman machine and a working Compose provider such as
    `podman-compose`.
  - Docker Desktop, if it is licensed, approved, installed, and running on the
    workstation.
- One valid site/user-owned Google Maps or Azure Maps provider key.

You do not need Git, Python, Conda, Node.js, VS Code, or a source-code checkout
for the normal V1 RC1 package path.

If Docker Desktop or Podman is not already installed and approved on your
workstation, or if you do not already have a valid restricted provider key,
stop here and contact your site administrator or support lead before continuing.

If both Docker and Podman are installed, the launcher's automatic engine
selection can choose Docker first. If support or local policy tells you to use
Podman, pass `-Engine podman` on every helper command.

## 1. Download The Release Files

Download or receive the control ZIP and asset ZIP for the same release version:

- `towerscout-v0.1.0-rc1.zip`
- `towerscout-v0.1.0-rc1.zip.sha256`
- `towerscout-v0.1.0-rc1-assets-<asset-version>.zip`
- `towerscout-v0.1.0-rc1-assets-<asset-version>.zip.sha256`

The exact asset filename can change by release. The control package, asset
bundle, `IMAGE.txt`, `release-manifest.v1.json`, and `webapp/asset_manifest.v1.json`
must describe the same release handoff.

## 2. Verify The Downloads Before Extracting

In PowerShell, compare each downloaded ZIP to its matching `.sha256` file before
extracting either package:

```powershell
Get-FileHash .\towerscout-v0.1.0-rc1.zip -Algorithm SHA256
Get-Content .\towerscout-v0.1.0-rc1.zip.sha256
Get-FileHash .\towerscout-v0.1.0-rc1-assets-*.zip -Algorithm SHA256
Get-Content .\towerscout-v0.1.0-rc1-assets-*.zip.sha256
```

The `Hash` value from `Get-FileHash` must match the SHA-256 value in the
corresponding `.sha256` file. If either value does not match, stop and obtain a
fresh copy of the release artifact before continuing.

## 3. Extract The Control Package

Extract the control ZIP to a normal local folder such as:

```text
C:\Users\<you>\TowerScout-v0.1.0-rc1
```

After extraction, the folder should contain `start.bat`, `compose.yaml`,
`compose.gpu.yaml`, `scripts\`, `docs\`, compliance files, `IMAGE.txt`,
`SHA256SUMS.txt`, and an empty `assets\` folder.

## 4. Initialize The Package

From PowerShell in the package folder, run:

```powershell
.\start.bat
```

The first launcher run creates `.env` from `.env.example`, starts the selected
container engine, polls TowerScout readiness, and opens:

```text
http://localhost:5000
```

Readiness may be `setup_required` because provider setup is not complete,
`degraded` because assets are not imported yet, or both through recovery hints.
That is expected during first setup.

If support tells you to use a specific engine, keep using the same `-Engine`
value for every helper command because Docker and Podman use separate named
volumes:

```powershell
.\start.bat -Engine podman
```

If the launcher cannot find or start a container engine, confirm the selected
engine is installed and running before continuing. For Podman, confirm the
Podman machine is started. For Docker, confirm Docker Desktop is running.

## 5. Stage And Import Assets

Open the asset ZIP. Its root should contain:

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

From PowerShell in the package folder, import the assets:

```powershell
.\scripts\import-assets.cmd -Source assets
```

If you started with an explicit engine, use that same engine here:

```powershell
.\scripts\import-assets.cmd -Engine podman -Source assets
```

If you started TowerScout on a non-default port, use that same `-Port` value
when importing assets so the helper recreates the Compose service with the same
port binding:

```powershell
.\scripts\import-assets.cmd -Source assets -Port 5001
```

For release-candidate or support validation, verify hashes during import:

```powershell
.\scripts\import-assets.cmd -Source assets -VerifyHashes
```

Or, with an explicit engine:

```powershell
.\scripts\import-assets.cmd -Engine podman -Source assets -VerifyHashes
```

The import helper uses the selected engine's named volumes. It should run after
`.env` has been created by the launcher. After copying assets, the helper
restarts TowerScout so the running application discovers the imported model
files before the first detection run.

## 6. Start Or Reopen TowerScout

From the package folder, run:

```powershell
.\start.bat
```

The default launch path is CPU-safe. It sets `TOWERSCOUT_DEVICE=cpu` for the
launch and does not request GPU devices.

Use `localhost`, not `127.0.0.1`, for normal browser use:

```text
http://localhost:5000
```

## 7. Optional GPU Launch

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

## 8. Complete Setup

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

## 9. Confirm Success

Run:

```powershell
.\scripts\status.cmd
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

For a small smoke check, open TowerScout, choose a provider, define a small
approved search area, select `Estimate tiles`, then run `Find towers` only for
a small area appropriate for the pilot.

## 10. Stop Or Restart

Stop TowerScout:

```powershell
.\scripts\stop.cmd
```

Start again:

```powershell
.\start.bat
```

Provider setup and imported assets are stored in named volumes and should
survive container restarts and replacement.

## 11. Source, Licenses, And Help

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

## 12. If Something Fails

Run:

```powershell
.\scripts\status.cmd
.\scripts\logs.cmd -Tail 200
```

Use the same `-Engine` value on status/log commands if support asked you to
start with a specific engine.

Do not share `.env`, provider keys, raw screenshots, raw browser network
traces, cached provider responses, uploaded investigation files, exported
datasets, named-volume contents, or unreviewed raw logs unless your site has an
approved support-handling procedure.

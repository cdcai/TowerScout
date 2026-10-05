# TowerScout User Guide

**Applies to**: The exact documentation-aligned Windows release package named
by the authoritative release record
**Last reviewed**: 2026-10-05
**Audience**: Package users after first setup.

**Runtime scope**: Docker CPU, Docker GPU, Podman CPU, and Podman GPU are
user-selected supported options when their documented prerequisites and the
final release's tested-support boundary are satisfied.

This guide explains the normal TowerScout workflow after the package is
installed, assets are imported, and at least one map provider key is configured.

Use the clickable [Quick Start](quick-start.md) for first-run package setup and
the [Package Guide](package-guide.md) for advanced troubleshooting.

## Before Using This Guide

This guide assumes the package setup work is already complete:

- The Docker or Podman engine you chose is installed, permitted, and running.
- Required model and ZIP-code assets are imported.
- TowerScout opens at `http://localhost:5000`.
- At least one provider key is configured through Setup Wizard or Settings.

If any of those are not true, start with the [Quick Start](quick-start.md).

TowerScout's Windows host scripts are intentionally unsigned. Use the supplied
`.cmd` and `.bat` entrypoints from a workstation where you and your organization
are permitted to run them. Do not weaken persistent execution policy or disable
endpoint protection. If Windows or an organization control requires a trusted
publisher or administrator approval, stop and use the site approval process.

GPU use is qualified only for the exact combinations named in the release
notes. A host `nvidia-smi` result alone is not acceptance; readiness must show
`selected_device=cuda`. Architecture mismatch messages require the correct
CUDA package or the CPU path, not a forced override. After a Windows NVIDIA
driver update, Podman GPU users must refresh and reverify CDI. Never install a
Linux display driver inside WSL.

When this guide shows package commands, run them from Windows PowerShell opened
in the extracted TowerScout package folder. Commands that begin with `.\` run a
script from that folder.

## What TowerScout Does

TowerScout helps identify likely cooling towers from satellite or aerial
imagery. A typical session is:

1. Choose a map provider.
2. Define a search area.
3. Estimate tile count.
4. Run detection.
5. Review likely towers.
6. Add manual corrections if needed.
7. Export or restore results.

TowerScout supports investigation and registry-building workflows. It does not
replace field confirmation, environmental assessment, or local public-health
judgment.

## Choose A Provider

TowerScout currently supports:

- Google Maps.
- Azure Maps.

Only one valid provider key is required to start. If both are configured, use
the provider selector to choose the imagery source for the current workflow.

Provider key reminders:

- Browser map SDK keys are visible to someone who can access the running app.
- The package assumes site/user-owned restricted keys.
- Unrestricted shared TowerScout project keys are unsupported.
- Do not share keys, `.env`, browser network traces, screenshots that reveal
  keys, cached provider responses, or raw logs unless your site has approved
  handling for that material.

## Search Or Navigate

You can move the map manually or use search.

Common search choices:

- Street address.
- City or neighborhood.
- ZIP code.
- Manual pan and zoom.

For ZIP code search, the ZIP-code asset data must be imported and readiness
must not report missing ZIP-code assets.

## Define A Search Area

TowerScout detects towers inside a selected search area. Keep first searches
small so tile counts and processing time stay manageable.

### Circle Search

1. Search for or navigate to the location.
2. Enter a radius in meters.
3. Select `Circle`.
4. Select `Estimate tiles`.

### Custom Search Area

Custom search areas are polygons used to tell TowerScout where to run
detection. They are different from manual tower polygons.

Before detection, `Custom shape` starts search-area drawing.

Provider-specific completion:

- Azure Maps: double-click to complete the polygon.
- Google Maps: right-click outside to complete the polygon.

After the polygon is complete, use it as the search area and estimate tiles.

## Estimate Tiles

Select `Estimate tiles` before `Find towers`.

The estimate tells you:

- How many imagery tiles TowerScout expects to process.
- Rough expected processing time.

If the tile count is larger than you intended, clear the search area or draw a
smaller one. Estimating first avoids starting a long detection run by accident.

## Run Detection

Select `Find towers` after the search area is set.

During detection:

- A progress overlay shows current phase and detail.
- TowerScout downloads imagery, runs the detector, applies secondary
  classification where configured, removes duplicates, and geocodes results.
- You can cancel an active run if needed.

If a run is cancelled, wait for the app to return to an idle state before
starting another run.

## Review Results

Results appear on the map and in the detection list.

Use the detection list to:

- Select a detection and center or highlight it on the map.
- Uncheck likely false positives before export.
- Adjust the minimum confidence slider.
- Switch between `Find` and `Label` review mode when appropriate.
- Step through detections and tiles with the review controls.

The confidence slider controls what is visible and exported. A higher threshold
shows fewer detections. A lower threshold shows more detections and may include
more false positives.

## Add Manual Tower Detections

Manual tower detections are corrections you add after a detection run. They are
not the same as custom search-area polygons.

Use manual tower drawing when:

- A visible tower was missed.
- You need to add a confirmed tower to the result set.

Workflow:

1. Run detection first.
2. Select `Add Towers`.
3. Draw around the tower.
4. Complete the polygon:
   - Azure Maps: double-click.
   - Google Maps: right-click outside.
5. Select `Save Towers`.

Manual towers are shown distinctly from model detections and are included in
CSV, KML, and dataset exports when saved.

To remove unsaved manual drawing shapes, use `Clear`. To remove all manual
tower detections, use `Clear all`. To exclude an individual saved detection
from exports, uncheck it in the detection list.

## Export Results

TowerScout supports several export paths.

### CSV And KML

Confirm that the results and their locations may be stored in the destination
folder before exporting them.

Use `Download results` to download:

- `detections.csv`
- `detections.kml`

These exports are useful for review, mapping, and sharing approved result
summaries according to your site policy.

### Dataset ZIP

Dataset ZIPs may contain sensitive locations, investigation context, imagery
tiles, and manual corrections. Confirm the approved storage and sharing path
before selecting the download action.

Use `Download dataset` to save the current tiles, labels, metadata, and manual
additions as `dataset.zip`.

## Restore A Dataset

Use `Restore dataset` to reload a previously exported `dataset.zip` into the
current session.

After restore:

- Review the provider selection and map framing.
- Confirm detections and manual towers appear as expected.
- Re-export only if the restored dataset is approved for the intended use.

## Stop When Finished Or Resume Later

Use the engine and processing mode in your non-secret setup record.

### Stop When Finished

Run only the line for your engine:

```powershell
.\scripts\stop.cmd -Engine docker
.\scripts\stop.cmd -Engine podman
```

### Start Or Resume Later

For Podman only, first run `podman machine list`. Run the following command
only when the recorded machine is stopped:

```powershell
podman machine start podman-machine-default
```

Then run only the command matching your setup.

#### Docker CPU

```powershell
.\start.bat -Engine docker -Gpu off
```

#### Docker NVIDIA GPU

```powershell
.\start.bat -Engine docker -Gpu on
```

#### Podman CPU

```powershell
.\start.bat -Engine podman -Gpu off
```

#### Podman NVIDIA GPU

```powershell
.\start.bat -Engine podman -Gpu on
```

`stop.cmd` does not take a port. If you selected another port, use it on setup,
start, and status and in the browser address.

The selected engine stores provider configuration, assets, logs, sessions,
temporary review data, uploads, and caches in **named volumes**, engine-managed
storage areas that remain when the TowerScout container stops. Normal
stop/start and reboot preserve them. Docker and Podman have separate stores,
and switching engines does not migrate data. The Podman machine may need to be
started after Windows restarts.

Export important results before stopping. A browser tab or internal session is
not a backup. Treat all local stores and exports as sensitive. Do not use
volume deletion, prune, or Podman machine reset as routine recovery.

## Setup And Resource Links

Open Settings to:

- Update Google Maps or Azure Maps keys.
- Change the default provider.
- View performance summary.
- Enable debug mode only for a bounded diagnostic and review its output before
  sharing anything.
- Clear cache.
- Open Resource Links.

Settings Resource Links include:

- Project Overview.
- User Guide.
- Source/licenses.
- Video Guides.
- TowerScout Research Article.

The running source/license notice is available from these local routes:

```text
http://localhost:5000/license      formatted browser page
http://localhost:5000/license.txt  plain-text combined notices
```

Use `/license.txt` when support needs text for scripts, copy/paste, or archival
records.

## Getting Help

For Windows policy, software installation, proxy, TLS, or managed-device
problems, contact Local IT. For a reproducible TowerScout defect that contains
no sensitive data, use the public
[TowerScout issue tracker](https://github.com/J-Schulein/TowerScout/issues).
It is not a private or guaranteed-response help desk.

Include:

- What you were trying to do.
- The release package version.
- Whether you used Docker or Podman, CPU or GPU, and which port.
- The sanitized readiness state from `scripts\status.cmd` with your selected
  engine and port.
- A short reviewed/redacted excerpt only when it contains no sensitive data.

Never post provider keys, `.env`, raw logs, raw screenshots, browser network
traces, cached provider responses, certificate details, uploaded investigation
files, exported datasets, named-volume contents, or sensitive AOIs in a public
record.

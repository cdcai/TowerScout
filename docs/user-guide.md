# TowerScout User Guide

**Applies to**: Current V1 package path through the stable `v0.1.0` closeout,
unless release notes say otherwise
**Last reviewed**: 2026-07-08
**Audience**: Pilot users after first setup
**Runtime scope**: The CPU Application Package is the primary path; the CUDA
12.6 Application Package, Podman CPU, Docker GPU, and Podman GPU are
support-assigned paths after workstation-specific engine, Compose-provider,
and NVIDIA validation.

This guide explains the normal TowerScout workflow after the package is
installed, assets are imported, and at least one map provider key is configured.

Use `docs/quick-start.md` for first-run package setup and
`docs/package-guide.md` for support troubleshooting.

## Before Using This Guide

This guide assumes the package setup work is already complete:

- Docker Desktop is installed, approved, and running for the primary pilot
  path, or support has explicitly directed you to a qualified Podman path.
- Required model and ZIP-code assets are imported.
- TowerScout opens at `http://localhost:5000`.
- At least one provider key is configured through Setup Wizard or Settings.

If any of those are not true, start with `docs/quick-start.md`.

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

If the tile count is too large for the pilot workflow, clear the search area or
draw a smaller one. Estimating first avoids starting a long detection run by
accident.

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

Use `Download results` to download:

- `detections.csv`
- `detections.kml`

These exports are useful for review, mapping, and sharing approved result
summaries according to your site policy.

### Dataset ZIP

Use `Download dataset` to save the current tiles, labels, metadata, and manual
additions as `dataset.zip`.

Dataset ZIPs may contain sensitive locations, investigation context, imagery
tiles, and manual corrections. Treat them as sensitive local data.

## Restore A Dataset

Use `Restore dataset` to reload a previously exported `dataset.zip` into the
current session.

After restore:

- Review the provider selection and map framing.
- Confirm detections and manual towers appear as expected.
- Re-export only if the restored dataset is approved for the intended use.

## Stop And Resume Later

Use:

```powershell
.\scripts\stop.cmd -Engine docker
```

Restart later with:

```powershell
.\start.bat -Engine docker -Gpu off
```

The package stores provider configuration, assets, logs, sessions,
uploads, and caches in named volumes. Treat all of those local stores as
sensitive.

If support asked you to run TowerScout with a specific engine, use the same
`-Engine` value on start, stop, status, logs, and asset-import commands because
Docker and Podman use separate named volumes.

## Setup And Resource Links

Open Settings to:

- Update Google Maps or Azure Maps keys.
- Change the default provider.
- View performance summary.
- Enable debug mode when support asks for it.
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

When reporting a problem, include:

- What you were trying to do.
- The release package version.
- Whether you used Docker Desktop or support-directed Podman.
- The readiness state from `scripts\status.cmd -Engine docker`, or the same
  command with the explicitly selected engine.
- A reviewed and redacted summary of recent logs if support asks for it.

Do not share provider keys, `.env`, raw logs, raw screenshots, browser network
traces, cached provider responses, uploaded investigation files, exported
datasets, named-volume contents, or sensitive AOIs unless your site has an
approved support-handling procedure.

# Everyday Commands

> **Applies to:** [supported release v0.1.3-rc.1](https://github.com/cdcai/TowerScout/releases/tag/v0.1.3-rc.1). **Guide updated:** 2026-10-28.

Run these commands from the extracted application folder. To open PowerShell
there, open the folder in File Explorer, click the address bar, type
`powershell`, and press Enter.

## Keep A Non-Secret Setup Record

Store this near the application folder. Never write the provider key in it.

| Item | Your value |
| --- | --- |
| Application folder | Record the full extracted folder path shown by File Explorer, inside `Documents\TowerScout` |
| Engine | Docker or Podman |
| Processing | CPU or NVIDIA GPU |
| Provider | Google Maps or Azure Maps |
| Port | 5000 unless changed |
| Browser address | `http://localhost:5000` unless the port changed |

## Start Or Reopen TowerScout

First start your chosen engine. For Docker, open Docker Desktop and wait
until it reports that the engine is running. For Podman, follow the machine
check below and keep Docker Desktop closed. If switching engines, first follow
[Switch Between Docker And Podman](Podman-Guidance#switch-between-docker-and-podman).

Run only the command matching the engine and processing mode in your setup
record.

### Docker CPU

```powershell
.\start.bat -Engine docker -Gpu off
```

### Docker NVIDIA GPU

```powershell
.\start.bat -Engine docker -Gpu on
```

Before either Podman command, run `podman machine list`. Run
`podman machine start podman-machine-default` only if the recorded machine is
stopped.

### Podman CPU

```powershell
.\start.bat -Engine podman -Gpu off
```

### Podman NVIDIA GPU

```powershell
.\start.bat -Engine podman -Gpu on
```

## Check Status

Run only the line for your engine:

### Docker

```powershell
.\scripts\status.cmd -Engine docker -Port 5000
```

### Podman

```powershell
.\scripts\status.cmd -Engine podman -Port 5000
```

For an NVIDIA GPU setup, status must show `selected_device=cuda`. General
`ready` status alone does not prove GPU processing.

## Save Results And Restore A Review

After reviewing the detections:

1. Select **Download CSV**, complete any save prompt, and confirm the CSV file
   appears in your approved folder.
2. Select **Download KML** separately and confirm that file appears too.
3. Select **Download dataset** and save `dataset.zip` for later restoration.
   CSV and KML are result exports; the dataset preserves imagery tiles,
   labels, metadata, and manual additions needed to restore a review.

Keep these files in approved storage because they may contain sensitive
locations or imagery. A dataset is not a backup of provider configuration or
the engine's named volumes.

To reopen saved work, start TowerScout with the same engine and processing
mode. Save any current review before loading another dataset. Select
**Restore dataset**, choose the saved `dataset.zip`, and wait for restoration
to finish. Check that the expected detections and manual additions appear,
then review the provider selection and map framing.

See the versioned [export instructions](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/docs/user-guide.md#export-results)
and [dataset restoration instructions](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/docs/user-guide.md#restore-a-dataset).

## Stop When Finished

Run only the line for your engine:

### Docker

```powershell
.\scripts\stop.cmd -Engine docker
```

### Podman

```powershell
.\scripts\stop.cmd -Engine podman
```

If you deliberately use another port, add `-Port 5001` to setup, start, and
status, then open `http://localhost:5001`. `stop.cmd` does not accept a port;
it stops the selected engine's TowerScout project.

## What Survives A Normal Stop

A normal stop or computer restart keeps the selected engine's **named
volumes**, engine-managed storage areas containing saved provider
configuration, imported model/data assets, Flask session files, temporary
review/export inputs, cache, uploads, and logs. The Podman machine may need a
manual start after Windows restarts.

Your browser tab is not a backup. Export any important CSV, KML, or dataset ZIP
to a controlled folder before stopping. Reset and uninstall procedures are
different from a normal stop and can remove data; do not run volume-deletion or
cleanup commands as routine troubleshooting.

If you switch between Docker and Podman, TowerScout uses different storage and
may appear unconfigured. Re-run setup/import for the new engine or return to
the original engine. Data is not migrated automatically.

Export a dataset ZIP before stopping and restore it if live results do not reappear; retained named volumes are not a substitute for a saved review.

# Everyday Commands

> **Audience:** TowerScout users. **Applies to:** The next final Windows
> release. **Last reviewed:** 2026-10-05. **Publication state:** Local draft.

Run these commands from the extracted application folder. To open PowerShell
there, open the folder in File Explorer, click the address bar, type
`powershell`, and press Enter.

## Keep A Non-Secret Setup Record

Store this near the application folder. Never write the provider key in it.

| Item | Your value |
| --- | --- |
| Application folder | Example: `C:\Users\me\Documents\TowerScout\towerscout-version-cpu` |
| Engine | Docker or Podman |
| Processing | CPU or NVIDIA GPU |
| Provider | Google Maps or Azure Maps |
| Port | 5000 unless changed |
| Browser address | `http://localhost:5000` unless the port changed |

## Start Or Reopen TowerScout

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

### Podman CPU

First run `podman machine list`. Run
`podman machine start podman-machine-default` only if the recorded machine is
stopped.

```powershell
.\start.bat -Engine podman -Gpu off
```

### Podman NVIDIA GPU

```powershell
.\start.bat -Engine podman -Gpu on
```

## Check Status

Run only the line for your engine:

```powershell
.\scripts\status.cmd -Engine docker -Port 5000
.\scripts\status.cmd -Engine podman -Port 5000
```

For an NVIDIA GPU setup, status must show `selected_device=cuda`. General
`ready` status alone does not prove GPU processing.

## Stop When Finished

Run only the line for your engine:

```powershell
.\scripts\stop.cmd -Engine docker
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

# TASK-065 Podman Compose Provider Validation

**Date**: 2026-05-08
**Host**: Windows 11 / AMD64 with Podman WSL machine
**Objective**: Validate a Docker-Desktop-free Podman Compose provider path for TowerScout release support.

## Provider Selection

- Installed `podman-compose==1.5.0` into the project virtual environment for validation.
- Verified local provider:
  - `podman version 5.8.2`
  - `podman-compose version 1.5.0`
- Verified `podman compose` can select the local provider with `PODMAN_COMPOSE_PROVIDER`.
- `podman compose version` reported external provider:
  - `<repo-root>\.venv\Scripts\podman-compose.exe`

## Docker Availability During Validation

`docker version` failed to reach the Docker Desktop daemon:

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
```

This confirms the validation did not depend on a running Docker Desktop engine.

## Launcher Validation

Command shape:

```powershell
$env:PODMAN_COMPOSE_PROVIDER=(Resolve-Path .\.venv\Scripts\podman-compose.exe).Path
$env:TOWERSCOUT_IMAGE='towerscout:local'
$env:TOWERSCOUT_CONTAINER_ENGINE='podman'
.\start.bat -Engine podman -Port 5001 -NoBrowser -TimeoutSeconds 180
```

Result:

- `start.bat` used the release launcher path.
- `podman compose` selected the local `podman-compose.exe` provider.
- TowerScout started on `http://127.0.0.1:5001`.
- `/api/readiness` reached `setup_required`.
- Asset status was `ok`.
- Config status was `setup_required`.
- Readiness runtime reported `container_engine: podman`.

## Status And Smoke Validation

Follow-up checks:

- `scripts/status.cmd -Engine podman -Port 5001` returned the running container and readiness payload.
- `GET /api/health` returned `{"service":"towerscout","status":"ok"}`.
- `GET /api/readiness` returned `state: setup_required`, assets `ok`, writable paths `true`, and runtime `container_engine: podman`.
- Containerized `TASK-052` smoke passed:

```text
container_task052_smoke=pass
engine_id=newest
model_path=/app/webapp/model_params/yolov5/newest.pt
response_status=502
progress_title=Imagery download failed
```

## Cleanup

`scripts/stop.cmd -Engine podman` stopped the validation service. A final `podman ps` showed no running Podman containers.

## Support Decision

The validated Podman support path is:

- Podman WSL machine running.
- A Docker-Desktop-free Compose provider available, validated here with `podman-compose 1.5.0`.
- `podman compose` selecting that provider, either automatically on hosts without Docker Compose earlier in provider precedence or explicitly through `PODMAN_COMPOSE_PROVIDER`.

This evidence supports removing the prior blanket caveat that Docker-Desktop-free Compose-provider validation is still pending. Release docs should still name the Compose-provider prerequisite explicitly.

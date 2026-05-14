---
name: towerscout-container-windows-runtime
description: 'Primary skill for TowerScout container and Windows runtime changes:
  Dockerfile, compose files, Podman/Docker support, PowerShell/CMD launch scripts,
  GHCR publish, TLS CA import, asset import, and runtime docs. For release package
  validation, use release-candidate-gate first.'
---

# TowerScout Container Windows Runtime

Use this skill when a task touches `Dockerfile`, Compose files, GHCR publishing, Podman/Docker runtime support, Windows launch scripts, PowerShell/CMD helpers, readiness endpoints, TLS CA import, asset import, or runtime docs.

## Goal

Review container and Windows launcher changes for release supportability and runtime persistence.

## Routing rule

Use exactly one TowerScout skill as the primary skill for a task. Add secondary skills only when their specific files or risk surfaces are touched. If the task spans several areas and the primary skill is not obvious, use `$towerscout-skill-router` first.

## Primary versus secondary

Use this as the primary skill for runtime/container/launcher changes. For full release package validation, use `towerscout-release-candidate-gate` first and this only as a focused secondary check when runtime files changed.

## First read

- `Dockerfile`
- `compose.yaml`
- `compose.build.yaml`
- `.dockerignore`
- `.env.example`
- `scripts/launch.ps1`
- `scripts/lib/TowerScoutCompose.ps1`
- `scripts/*.cmd`
- `.github/workflows/container-publish.yml`
- runtime/OCI docs if present

## Review checklist

1. Persistent volumes preserve config, model params, data, logs, filesystem sessions, temp/session, uploads, and cache.
2. `FLASK_SECRET_KEY`, setup/settings config persistence, and filesystem sessions remain durable across container replacement.
3. `/api/health` and `/api/readiness` remain compatible with launchers and support scripts.
4. Podman support language requires a running Podman machine and approved Compose provider.
5. Browser launch uses `localhost` unless a provider-specific reason supports a change.
6. TLS CA import and provider-key validation errors remain actionable and sanitized.
7. Release docs avoid Docker Desktop-only assumptions.

## Inspect commands (read-only)

```bash
git diff -- Dockerfile compose.yaml compose.build.yaml .dockerignore .env.example scripts .github/workflows/container-publish.yml docs
python .agents/skills/towerscout-ci-quality-ratchet/scripts/summarize_ci_workflow.py .github/workflows/container-publish.yml
```

## Build/update generated files (mutating)

Run only when building or testing runtime images is part of the task.

```bash
docker build -t towerscout:test .
```

## Validation commands

```bash
docker compose -f compose.yaml -f compose.build.yaml up -d --build
curl -f http://localhost:5000/api/health
curl -f http://localhost:5000/api/readiness
docker compose -f compose.yaml -f compose.build.yaml down
python -m pytest tests/unit/test_flask_routes.py tests/unit/test_config.py tests/unit/test_container_publish_workflow.py -q -p no:cacheprovider
```

If any Compose validation command fails, still run the `docker compose ... down` cleanup command before ending the task.

Windows validation host commands:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/launch.ps1 -Engine podman -Port 5000 -NoBrowser -TimeoutSeconds 180
scripts\status.cmd -Engine podman -Port 5000
scripts\logs.cmd -Engine podman -Tail 200
scripts\stop.cmd -Engine podman -Port 5000
```

## Output format

Return files changed, persistence/readiness findings, Podman/Docker compatibility findings, TLS/asset import notes, commands run, and release-support risks.

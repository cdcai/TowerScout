---
name: towerscout-release-candidate-gate
description: 'Primary skill for TowerScout release-candidate or pilot package validation:
  release manifests, checksums, asset bundle, pinned image digest, health/readiness
  checks, and RC evidence. Use compliance/docs/container skills only as secondary
  checks when those files are specifically changed.'
---

# TowerScout Release Candidate Gate

Use this skill when a task touches release packaging, asset bundle contracts, release manifests, checksums, pinned image digests, RC validation evidence, or full clean-machine release validation.

## Goal

Prove that the current branch can produce a TowerScout V1 RC or pilot release package that is usable, supportable, and internally consistent with the current release posture.

## Routing rule

Use exactly one TowerScout skill as the primary skill for a task. Add secondary skills only when their specific files or risk surfaces are touched. If the task spans several areas and the primary skill is not obvious, use `$towerscout-skill-router` first.

## Primary versus secondary

This is the primary skill for whole-package release validation. Use the compliance, docs, container runtime, secret safety, and agent-work hygiene skills as secondary checks only when their specific files or evidence surfaces are changed.

## First read

Read these files when they exist:

- `.agent_work/current-tasks.md`
- `.agent_work/task-backlog.md`
- `docs/release-asset-bundle-contract.md`
- `Dockerfile`
- `compose.yaml`
- `compose.build.yaml`
- `scripts/launch.ps1`
- `scripts/lib/TowerScoutCompose.ps1`
- `scripts/package-release.*`
- `release-manifest.v1.json`
- `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `MODEL_LICENSES.md`, `DATA_LICENSES.md`, `PROVIDER_TERMS.md`, `SOURCE.txt`, `SBOM.txt`

## Required review areas

1. Release package shape: confirm package docs, Compose files, launch scripts, `.env.example`, manifest, checksums, and license/source notices are included or intentionally omitted.
2. Image identity: confirm release use references a pinned GHCR digest, not only a mutable tag.
3. Asset bundle contract: confirm asset docs match actual runtime paths for `model_params/`, `data/`, `asset_manifest.v1.json`, and import helpers.
4. Runtime readiness: confirm `/api/health` and `/api/readiness` remain compatible with launchers and support scripts.
5. Setup and validation path: confirm Setup Wizard, provider key validation, restart persistence, and a bounded detection path can be validated.
6. Evidence hygiene: summarize evidence with commands, timestamps, environment, pass/fail, and redacted excerpts.

## Inspect commands (read-only)

Identify the current release package directory or ZIP before summarizing it; do not assume a fixed RC folder name.

```bash
git diff --check
python .agents/skills/towerscout-release-candidate-gate/scripts/summarize_release_package.py dist/<package-dir-or-zip>
python .agents/skills/towerscout-release-candidate-gate/scripts/check_release_manifest.py release-manifest.v1.json .
```

## Build/update generated files (mutating)

Run only when the task is to assemble or refresh a release package.

```bash
scripts/package-release.cmd -Version <version> -OutputDir dist -NoZip -Force
```

## Validation commands

```bash
python .agent_work/scripts/validate_agent_work.py
python -m pytest tests/unit/test_release_package_script.py tests/unit/test_release_manifest_schema.py tests/unit/test_flask_routes.py -q -p no:cacheprovider
python -m pytest tests/unit/test_license_notices.py tests/unit/test_container_publish_workflow.py -q -p no:cacheprovider
```

## Runtime validation commands

Run only in an environment where Docker/Podman service startup is intended.

```bash
docker build -t towerscout:test .
docker compose -f compose.yaml -f compose.build.yaml up -d --build
curl -f http://localhost:5000/api/health
curl -f http://localhost:5000/api/readiness
docker compose -f compose.yaml -f compose.build.yaml down
```

If any Compose validation command fails, still run the `docker compose ... down` cleanup command before ending the task.

On Windows or a Windows validation host:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/launch.ps1 -Engine podman -Port 5000 -NoBrowser -TimeoutSeconds 180
scripts\status.cmd -Engine podman -Port 5000
scripts\logs.cmd -Engine podman -Tail 200
scripts\stop.cmd -Engine podman -Port 5000
```

## Output format

Return a short RC gate report with overall status, commands run, release-blocking findings, non-blocking follow-ups, files inspected, evidence summary, and validation gaps.

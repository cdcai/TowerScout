---
name: towerscout-end-user-docs-check
description: 'Primary skill for TowerScout user-facing documentation: quick start,
  release notes, Windows pilot instructions, troubleshooting, UAT docs, and support
  handoff material. For broader release validation, use release-candidate-gate first
  and this as a secondary docs check.'
---

# TowerScout End User Docs Check

Use this skill when a task touches user docs, quick start, release notes, Windows pilot instructions, troubleshooting, UAT docs, or support handoff material.

## Goal

Review docs from a non-technical pilot-user perspective and check that commands, paths, setup steps, success criteria, and support evidence are clear.

## Routing rule

Use exactly one TowerScout skill as the primary skill for a task. Add secondary skills only when their specific files or risk surfaces are touched. If the task spans several areas and the primary skill is not obvious, use `$towerscout-skill-router` first.

## Primary versus secondary

Use this as the primary skill for end-user documentation changes. For whole release-candidate validation, use `towerscout-release-candidate-gate` first and this only as a focused secondary docs check.

## First read

Read relevant files that exist among:

- `README.md`
- `docs/`
- release package quick start and user guide files
- `docs/release-asset-bundle-contract.md`
- `scripts/launch.ps1`
- `scripts/*.cmd`
- `compose.yaml`
- `.env.example`
- `.agent_work/current-tasks.md`

## Review checklist

1. The user can tell what to download and where to extract it.
2. Asset placement paths are explicit and match the release asset bundle contract.
3. Launch instructions use current `start.bat` or script behavior.
4. Setup Wizard/provider key steps are clear and do not imply keys are hidden from browser SDKs when they are not.
5. Success criteria are concrete: readiness state, setup completed, provider available, small AOI detection path.
6. Troubleshooting includes Podman/Docker/Compose, ports, Podman machine, TLS CA, provider-key validation, missing assets, and logs/status commands.
7. Support instructions collect useful evidence without secrets, raw logs, raw screenshots, or sensitive locations.
8. License/source/provider/model/data notice locations are described.

## Inspect commands (read-only)

```bash
git diff -- README.md docs scripts compose.yaml .env.example
python .agents/skills/towerscout-end-user-docs-check/scripts/check_doc_commands.py . docs README.md
```

## Build/update generated files (mutating)

No standard mutating command. Do not regenerate release packages while doing a docs-only review unless the task explicitly requires validating docs against a fresh package.

## Validation commands

When docs are being validated against a runtime, choose only the relevant checks.

```bash
scripts\status.cmd -Engine podman -Port 5000
scripts\logs.cmd -Engine podman -Tail 200
curl -f http://localhost:5000/api/readiness
```

## Output format

Return unclear user steps, commands/paths that appear stale, screenshots/evidence users should or should not collect, support-safe troubleshooting gaps, and any docs that should be verified by clean-machine validation.

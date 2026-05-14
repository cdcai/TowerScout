---
name: towerscout-skill-router
description: Use first when a TowerScout task spans multiple skill areas or you are
  unsure which TowerScout skill should be primary. Select one primary skill plus optional
  secondary checks; do not run every skill.
---

# TowerScout Skill Router

Use this skill first when a TowerScout task spans several domains, when Codex appears likely to load several release-adjacent skills, or when you want a primary-skill recommendation before work starts.

## Goal

Pick one primary TowerScout skill and at most a small number of optional secondary checks. Do not run every skill.

## Routing process

1. Identify the main artifact being changed or reviewed.
2. Select exactly one primary skill from the matrix below.
3. Add secondary skills only for concrete risk surfaces that are actually touched.
4. If the task is a release candidate validation, use `towerscout-release-candidate-gate` as primary and treat docs, compliance, container runtime, secret safety, and agent-work hygiene as optional focused secondary checks.
5. If the task is a normal feature or bug fix, avoid release skills unless release packaging, manifests, user docs, runtime scripts, or compliance artifacts changed.

## Routing matrix

| Task shape | Primary skill | Optional secondary checks |
|---|---|---|
| Release candidate or package validation | `towerscout-release-candidate-gate` | Compliance, container runtime, docs, secret safety, agent-work hygiene only if touched. |
| Browser smoke failure or Google/Azure workflow | `towerscout-browser-provider-smoke-triage` | Provider state review for code-level race/cleanup concerns. |
| JavaScript source or generated bundle | `towerscout-frontend-bundle-guard` | Provider state review if ProviderStateManager or map state changed. |
| Provider switching or state/race behavior | `towerscout-provider-state-review` | Browser smoke triage for live smoke execution or artifacts. |
| ML detection, inference, model loading, tiling | `towerscout-ml-runtime-safety` | Release gate only if model assets/package behavior changed. |
| License, notices, AGPL/YOLO, source/SBOM | `towerscout-release-compliance-review` | Release gate for full RC package validation. |
| Docker/Podman/Windows launcher/runtime | `towerscout-container-windows-runtime` | Release gate if validating a packaged release. |
| CI workflows or quality gates | `towerscout-ci-quality-ratchet` | Secret safety if artifacts/logs are changed. |
| Secrets, provider keys, logs, artifacts | `towerscout-secret-and-provider-key-safety` | Use as a focused secondary safety check in PRs. |
| `.agent_work` task tracking or evidence | `towerscout-agent-work-hygiene` | Use as a focused secondary hygiene check in PRs. |
| End-user quick start, release notes, UAT docs | `towerscout-end-user-docs-check` | Release gate if validating docs against a package. |

## Output format

Return:

- Primary skill.
- Optional secondary skills, if any.
- Why each secondary skill is necessary.
- Skills intentionally not used.
- First three files or commands to inspect.

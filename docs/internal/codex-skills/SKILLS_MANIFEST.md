# TowerScout Codex Skills Manifest

This manifest summarizes the updated skills and their primary routing purpose.

| Skill | Role | Short use case | Typical prompt |
|---|---|---|---|
| `towerscout-skill-router` | Primary router when unsure | Skill routing | `Use $towerscout-skill-router to choose the primary skill and optional secondary checks for this task.` |
| `towerscout-release-candidate-gate` | Primary for RC/package validation | Release validation | `Use $towerscout-release-candidate-gate to validate the current branch as a release candidate.` |
| `towerscout-browser-provider-smoke-triage` | Primary for browser/provider smoke failures | Browser smoke triage | `Use $towerscout-browser-provider-smoke-triage to interpret this browser smoke failure.` |
| `towerscout-frontend-bundle-guard` | Primary for JS source/bundle changes | Frontend bundle safety | `Use $towerscout-frontend-bundle-guard after these JS changes.` |
| `towerscout-provider-state-review` | Primary for provider/state race-risk changes | Provider state review | `Use $towerscout-provider-state-review to review this provider-switching change.` |
| `towerscout-ml-runtime-safety` | Primary for ML/inference changes | ML runtime safety | `Use $towerscout-ml-runtime-safety to review this EfficientNet change.` |
| `towerscout-release-compliance-review` | Primary for license/compliance files; secondary for RCs | Release compliance | `Use $towerscout-release-compliance-review to check these release notice changes.` |
| `towerscout-container-windows-runtime` | Primary for container/launcher changes; secondary for RCs | Container runtime review | `Use $towerscout-container-windows-runtime to review this launcher update.` |
| `towerscout-ci-quality-ratchet` | Primary for CI/gate policy changes | CI quality tightening | `Use $towerscout-ci-quality-ratchet to suggest a safe CI tightening plan.` |
| `towerscout-secret-and-provider-key-safety` | Primary for secret/config/log changes; common PR secondary | Secret safety scan | `Use $towerscout-secret-and-provider-key-safety before I commit these artifacts.` |
| `towerscout-agent-work-hygiene` | Primary for .agent_work changes; common PR secondary | Task tracking hygiene | `Use $towerscout-agent-work-hygiene to check these task-tracking updates.` |
| `towerscout-end-user-docs-check` | Primary for user-facing docs; secondary for RCs | User docs review | `Use $towerscout-end-user-docs-check to review this pilot quick start.` |

## Command category convention

Each skill separates commands into:

- Inspect commands: read-only review and summaries.
- Build/update generated files: mutating commands that should run only when the task requires generated artifacts to change.
- Validation commands: tests, service checks, or runtime checks that may take longer or require local services.

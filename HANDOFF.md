# TowerScout Handoff Guide

This file is the short operational handoff for the validated `v0.1.2` pilot
release and the associated `.agent_work/` history. `v0.1.0` and `v0.1.1`
remain historical fork-side tag/image identities with no final GitHub Release
assets. The fork-side pilot release is published at
`https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.2`.

## Current Pilot And Adoption Decision

The `cdcai/TowerScout` owner has requested that the existing official
repository remain unchanged until pilot users provide feedback. Therefore:

- `J-Schulein/TowerScout` is the temporary pilot download, development, and
  validation surface.
- `cdcai/TowerScout` continues to represent the currently adopted application
  and must not be presented as the source of the `v0.1.2` pilot.
- The six validated `v0.1.2` release assets are frozen. Any fix uses a new
  version identity.
- Migration preparation may continue, but source, tags, releases, images,
  issues, and repository banners must not be changed in cdcai until the owner
  reviews feedback and approves an adoption baseline.
- Pilot feedback is maintained by the project lead in a fillable Word document
  outside the repository. The confirmed primary and backup support contacts
  have appropriate access.

The canonical plan for the confirmed extension through 2026-10-31 is:

- `.agent_work/context/status/Handoff-Planning/PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md`

## Reading `.agent_work`

Use this order:

1. `.agent_work/current-tasks.md`
2. `.agent_work/task-backlog.md`
3. `.agent_work/completed-tasks.md`
4. `.agent_work/tasks/active/` and `.agent_work/tasks/completed/`
5. `.agent_work/decisions/`
6. `.agent_work/context/status/`, `.agent_work/context/analysis/`, and `.agent_work/context/guides/`

Current release-transition work is tracked in:

- `.agent_work/tasks/active/TASK-088-stable-release-and-handoff-closeout.md`
- `.agent_work/tasks/active/TASK-089-cdcai-migration-execution.md`

Earlier Handoff-Planning strategies, checklists, and external reviews document
how the release was produced and validated. Their immediate-migration dates and
`v0.1.0`/`v0.1.1` commands are historical, not current execution instructions.

## CI Gates

CI green does not mean every check is merge-blocking.

Merge-relevant automated checks currently include:

- `flake8` syntax/undefined-name gate
- `pytest tests/unit/`
- frontend bundle rebuild and regression checks
- the Task-087 frontend contract workflow

Advisory CI steps currently include:

- `black --check`
- `mypy`
- `bandit`
- `pytest tests/integration/`
- Codecov upload
- Docker image build job
- Trivy filesystem scan
- SARIF upload

Treat those advisory results as useful signals, not as proof that the release
package is production-ready.

## Automated Vs Manual Validation

Automated coverage currently proves the Python webapp core, route/config and
provider-contract behavior, selected frontend contract shapes, and source-text
contracts over the PowerShell/release surfaces.

The following still rely on human-validated evidence rather than CI:

- Windows PowerShell behavioral tests
- package generation and package smoke validation
- asset-bundle import and checksum workflow in real package context
- Docker/Desktop and Podman runtime validation
- GPU validation
- live-provider browser smoke with real keys
- end-to-end release-package readiness

The release package itself is certified by the manual RC validation evidence,
not by CI alone. For the current fork-side stable line, the authoritative
validation record is the `v0.1.2` full-matrix evidence under
`.agent_work/context/status/Handoff-Planning/v0.1.2-Validation-Evidence/`.

## Asset Bundle Custody

The shared Model & Data Package ZIP is not reproducible from this repository
alone. The exact released asset bundle is distributed through release assets and
is pinned by SHA-256 `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.

The authoritative per-file asset contract lives in:

- `webapp/asset_manifest.v1.json`
- `docs/release/release-asset-bundle-contract.md`

Do not assume the model/data bundle can be rebuilt locally from source-only
history.

## Known Accepted Risks

- `torch==2.2.1` remains in the validated release baseline even though
  `CVE-2025-32434` affects the `torch.load` boundary. Current mitigation is the
  release asset-bundle SHA-256 contract and fixed trusted asset path. A torch
  bump is a follow-up item because it would invalidate the validated CPU/GPU
  parity evidence.
- The YOLO vendor path still uses a `weights_only=False` load path, so a torch
  upgrade alone does not fully change the trust model.
- The Dockerfile frontend build stage still uses `node:18`; the next maintained
  update target is `node:22`, not `node:20`.
- The repository license posture remains composite and GitHub reports
  `NOASSERTION`; `TASK-069` carries the open Apache-2.0 relicensing authority
  question.
- Google-mode detection without a defined search area or drawn boundary fails
  with a generic client error. Server-side bounds validation contains the bad
  request, documented workflows with an explicit AOI pass, and the issue is
  tracked as a non-blocking post-release UX/error-handling follow-up.
- `/favicon.ico` is not packaged, and export/status notifications still use
  blocking browser alerts. Both are cosmetic/UX follow-ups, not release
  blockers.

## Deferred cdcai Adoption

Nothing should migrate into cdcai during the owner-approved feedback hold. When
adoption is later approved, the following still require explicit transfer or
recreation rather than a normal git push:

- GitHub Actions run history and logs
- pull request discussion history
- GitHub Releases and release assets
- Issues, unless recreated separately
- repository settings such as homepage metadata and branch protection
- collaborators and permissions
- package visibility settings in GHCR

The project ends 2026-10-31, with 2026-10-30 used as the operational closeout
date. Before closeout, give the owner the release assets/checksums, validation
summary, known findings, backlog, and prepared migration runbook. The external
feedback document remains under the project lead's custody. Do not change cdcai
without the owner's adoption approval.

Keep the fork available as the pilot/provenance archive even after a later
cdcai release path and package runtime are confirmed.

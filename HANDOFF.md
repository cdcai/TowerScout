# TowerScout Handoff Guide

This file is the short operational handoff for the maintained `v0.1.0` release
line and the associated `.agent_work/` history.

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
not by CI alone.

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

## What Did Not Migrate Automatically

The following do not move with a git push and should be treated as explicit
handoff items:

- GitHub Actions run history and logs
- pull request discussion history
- GitHub Releases and release assets
- Issues, unless recreated separately
- repository settings such as homepage metadata and branch protection
- collaborators and permissions
- package visibility settings in GHCR

Keep the fork available until the recreated cdcai release path and package
runtime validation are confirmed.
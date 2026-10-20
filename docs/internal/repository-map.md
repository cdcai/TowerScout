# Where to find TowerScout information

## Start here

- [README](../../README.md): project overview and user entry point.
- [HANDOFF](../../HANDOFF.md): delivery and ownership context.
- [Owner maintenance](owner-maintenance.md): maintenance prompts and review steps.
- [CONTRIBUTING](../../CONTRIBUTING.md): development workflow.
- [AGENTS](../../AGENTS.md): current instructions for coding agents.

## Document groups

| Location | Purpose |
| --- | --- |
| `docs/` | Versioned user and local IT manuals; paired HTML provides served Help. |
| `docs/release/` | Artifact contract, candidate identities, operating supplement, and release handoff. |
| `docs/support/` | Runtime and support procedures. |
| `docs/internal/` | Maintainer guidance and repository skill inventory. |
| `wiki/` | Reviewable wiki drafts; a separate publication step makes them live. |
| `.agent_work/` | Current tasks, prioritized backlog, decisions, and retained evidence/history. |
| `.agents/skills/` | Repository-maintained procedures used by coding agents. |
| `.github/` | CI/publishing workflows, review guidance, templates, and security policies. |

## Files intentionally kept in the root

`LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `MODEL_LICENSES.md`,
`DATA_LICENSES.md`, `PROVIDER_TERMS.md`, `SOURCE.txt`, and `SBOM.txt`
remain together at the root. Packaging, image construction, tests, and links
depend on their locations. `SBOM.txt` is a pointer, not a complete inventory.

Launchers, Compose files, Dockerfile, dependency manifests, and tool
configuration also remain at their established paths. Moving them requires
an explicit compatibility change and appropriate tests.

Organize by navigation first. A cleaner root is not worth breaking a user's
launch command, package allowlist, license link, or build context.

### Root-file groups

All 31 tracked root files were reviewed on October 20. Keep their paths for
this handoff; no remaining root-file relocation is proposed.

| Group | Files | Reason to retain location |
| --- | --- | --- |
| Entry points | `README.md`, `HANDOFF.md`, `CONTRIBUTING.md`, `AGENTS.md` | Starting points for users, maintainers and agents. |
| Notices and provenance | `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `MODEL_LICENSES.md`, `DATA_LICENSES.md`, `PROVIDER_TERMS.md`, `SOURCE.txt`, `SBOM.txt` | Dockerfile copies these paths; packaging and notice tests depend on them. Generated release source/SBOM references are release-specific. |
| Startup | `bootstrap.cmd`, `setup-towerscout.cmd`, `start.bat` | Existing setup and launch entry points. |
| Container configuration | `Dockerfile`, `compose.yaml`, `compose.build.yaml`, `compose.gpu.yaml`, `compose.gpu.podman.yaml` | Build context and script/Compose consumers use established paths. |
| Dependency and release metadata | `package.json`, `package-lock.json`, `requirements-dev.txt`, `release-manifest.v1.json` | Dependency tools, CI and release construction consume these paths. |
| Tool configuration | `.dockerignore`, `.editorconfig`, `.env.example`, `.gitattributes`, `.gitignore`, `pytest.ini` | Location-based tool configuration and setup template. |
| Frontend check entry point | `validate_stage_0.sh` | Referenced by the root package's `test:stage-0` command. |

Local `.env` and `debug.log` files are private working material, not handoff
documents. Do not add them to the public repository. Place new maintainer
guidance in `docs/internal/`, release guidance in `docs/release/`, and private
reports/recordings in the agreed private delivery location.

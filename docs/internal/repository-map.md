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

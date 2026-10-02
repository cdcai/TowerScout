# Releases And Supported Versions

> **Audience:** All readers and support. **Last reviewed:** 2026-10-02.
> **Publication state:** Local draft.

The [TowerScout Releases page](https://github.com/J-Schulein/TowerScout/releases)
is authoritative. A package is current only when its release record names exact
downloads, public SHA-256 values, image digests, qualified environments, and
known limitations.

| Release state | Status | Guidance |
| --- | --- | --- |
| `v0.1.2` | Historical published pilot | Preserve for users explicitly assigned that release; use its own documentation and hashes. |
| Documentation-aligned successor | Not yet publicly frozen/published | Do not distribute or infer support until the final record, hashes, and acceptance evidence exist. |
| Draft/prerelease diagnostics | Test-only unless the release owner explicitly assigns them | Never present as final acceptance or a supported public release. |

## Selection Rules

- Use the exact release URL or tag provided by the release owner/support.
- Download package assets from `Assets`, not generated source archives.
- Do not mix Application Package, Model & Data Package, or sidecars across
  releases.
- CPU is the default. CUDA and Podman require explicit release-specific support
  assignment.
- Verify final public links and hashes without a privileged GitHub session
  before broad distribution.

Historical instructions remain historical. Do not silently update an old
release page to imply it has the behavior or evidence of a newer package.

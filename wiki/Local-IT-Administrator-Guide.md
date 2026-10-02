# Local IT Administrator Guide

> **Audience:** Local IT, security, endpoint-management, and support staff.
> **Applies to:** The exact assigned release. **Last reviewed:** 2026-10-02.
> **Publication state:** Local draft.

The authoritative offline guide is shipped as:

- `docs\local-it-administrator-guide.html`
- `docs\local-it-administrator-guide.md`

It is also available from TowerScout Settings under **Resource Links** when the
running image matches the downloaded release.

## What Local IT Reviews

1. Windows 11 AMD64, WSL 2/virtualization, engine approval, browser, disk, and
   outbound network prerequisites.
2. The default Docker CPU path versus explicitly assigned Podman/GPU paths.
3. ADR-023's unsigned wrapper boundary and any site signing/allowlisting
   decision. The project does not advise disabling controls.
4. Exact release-page SHA-256 verification before extraction or unblocking.
5. GHCR/provider connectivity, proxy/TLS inspection, site CA handling, and
   loopback-only exposure.
6. Site-owned provider accounts, billing, restrictions, and monitoring.
7. Named-volume custody for configuration, logs, sessions, uploads, caches,
   assets, and investigation data.
8. Safe support evidence, private escalation paths, retention, backup,
   rollback, upgrade, and secure disposal.

## Supported Boundary

The standard package supports the supplied process-scoped wrappers only where
the organization permits them. An endpoint requiring a trusted Authenticode
publisher, WDAC/AppLocker approval, constrained-language approval, or an
organization-specific allowlist is not a standard-package pass without the
site's separate approval.

Open the shipped guide for the complete checklist and exact references. If the
Wiki differs from the shipped guide, the exact package/release documentation
controls.

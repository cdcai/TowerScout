# Local IT Administrator Guide

> **Audience:** Local IT, security, and workstation administrators. **Applies
> to:** The next final Windows release. **Last reviewed:** 2026-10-02.
> **Publication state:** Local draft.

The end user chooses Docker or Podman, CPU or a compatible NVIDIA GPU, and
Google Maps or Azure Maps. Local IT confirms that the chosen prerequisites,
network access, credential model, and unsigned-script boundary are permitted.

## Approval Checklist

1. Windows 11 x64, supported build, RAM, disk, hardware virtualization, and
   WSL 2 meet the final release and selected engine requirements.
2. The organization permits either Docker Desktop under its applicable license
   or Podman Desktop with a rootless WSL 2 machine.
3. For Podman, Python 3.12 and the package-local pinned Compose-provider helper
   are permitted.
4. For NVIDIA GPU use, the exact GPU/driver appears in the release's tested
   matrix. Podman GPU additionally uses NVIDIA Container Toolkit/CDI inside the
   intended machine.
5. Outbound HTTPS is allowed to the exact GitHub release, GHCR, and selected
   map-provider endpoints. Proxy or TLS inspection is documented.
6. The site accepts TowerScout's one-credential-per-provider model and the fact
   that the browser receives that credential. Provider billing, restrictions,
   quotas, monitoring, and rotation have an owner.
7. Sensitive provider configuration, sessions, uploads, caches, logs, and
   exported investigation data have an approved local custody plan.

## Unsigned Windows Boundary

TowerScout's PowerShell scripts are intentionally unsigned. Supported `.cmd`
and `.bat` wrappers launch Windows PowerShell 5.1 using a process-scoped
`-ExecutionPolicy Bypass`; they do not modify persistent execution policy.

The standard release does not claim compatibility with endpoints that require
a trusted Authenticode publisher, WDAC/AppLocker approval, constrained-
language approval, antivirus/EDR exceptions, or organization-specific
allowlisting. Do not disable those controls. Internally signed or repackaged
bytes are owned by the site and require new checksums and site qualification.

Before extraction, compare each browser-downloaded ZIP's local SHA-256 with
both its sidecar and the value displayed in the authoritative GitHub release
record. Preserve the Windows downloaded-file marker through that check.

## Network And TLS Inspection

TowerScout binds the browser service to loopback. The engine pulls a digest-
pinned GHCR image, and the running application contacts the selected provider.
Use the exact final release's endpoint list rather than a guessed wildcard.

If provider validation reports a TLS trust error, separate diagnosis from
change:

1. run the release-specific repair helper without `-Apply`;
2. review the selected engine, provider, port, certificate identity, and
   proposed trust bundle locally;
3. obtain the required organizational approval; and
4. run the separate `-Apply` form only when the proposal is correct.

The helper imports an approved site CA into TowerScout's engine-specific
configuration volume. It cannot repair registry-pull trust or a blocked WSL
VM. Do not use an insecure-TLS environment setting.

## Persistence And Recovery

Docker and Podman each use eight named TowerScout volumes for configuration,
models, data, logs, Flask sessions, session temporary data, uploads, and cache.
Normal stop/start and reboot preserve them. Do not use `down -v`, volume prune,
machine reset, or blanket container cleanup as ordinary recovery. Switching
engines does not migrate data.

Users should export important work before stopping. Internal session storage
is not a managed backup. Establish retention and deletion procedures for
provider configuration, private locations, uploads, logs, caches, and exports.

## Safe Escalation

Public issue reports may contain package/image identity, versions, a sanitized
readiness state, and a non-secret error category. They must not contain keys,
`.env`, raw logs/screenshots, browser traces, private AOIs, provider responses,
certificate details, uploaded files, datasets, or volume contents.

The current public route is the
[TowerScout issue tracker](https://github.com/J-Schulein/TowerScout/issues).
It is not a private or guaranteed-response service. Local IT retains
responsibility for organization-managed controls and sensitive evidence.

For exact commands and data boundaries, use the version-matched
[packaged Local IT guide](https://github.com/J-Schulein/TowerScout/blob/main/docs/local-it-administrator-guide.md).

# Local IT Administrator Guide

> **Applies to:** [supported release v0.1.3-rc.1](https://github.com/cdcai/TowerScout/releases/tag/v0.1.3-rc.1). **Guide updated:** 2026-10-28.

The user chooses among the Docker/Podman, CPU/NVIDIA GPU, and Google/Azure
options permitted by the organization. Local IT may prescribe an engine or
provider and confirms the prerequisites, network access, credential model,
and unsigned-script boundary for the chosen configuration.

For Docker, host Python is not required. The current tested Podman provider
setup requires explicitly selected **64-bit Python 3.12** and a package-root
path of **80 characters or fewer**. Follow [Podman Guidance](Podman-Guidance)
for the short-folder check, Python selection, and selected-provider verification.
These restrictions do not authorize moving an existing configured installation.

## Approval Checklist

1. Windows 11 x64, the Windows build, RAM, virtualization, and WSL 2 meet the
   selected engine's current requirements. Use [Before You Install](Before-You-Install)
   for the vendor links and disk guidance. TowerScout does not publish a
   separately validated RAM minimum.
2. The organization permits either Docker Desktop under its applicable license
   or Podman Desktop with a rootless WSL 2 machine.
3. For Podman, Python 3.12 and the package-local pinned Compose-provider helper
   are permitted.
4. For NVIDIA GPU use, follow [NVIDIA GPU Setup](NVIDIA-GPU-Setup) for
   architecture, approved Windows driver, WSL, and container checks. The
   release's [tested configurations](Releases-And-Supported-Versions#tested-configurations)
   define the qualification scope; no complete GPU/driver matrix is published.
   Podman GPU also uses NVIDIA Container Toolkit/CDI inside the intended machine.
5. Outbound HTTPS permits the downloads and services listed below. Record the
   required destinations, redirects, proxy, and TLS-inspection arrangements
   for the chosen installation.
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

TowerScout binds the browser service to loopback. Prepare network access for
both installation and ordinary use:

| Purpose | Destinations to review |
| --- | --- |
| Application and Model & Data downloads | The exact GitHub release asset URLs and their download redirects. |
| Runtime image download | `ghcr.io` and the registry's required authentication/download destinations for the pinned image. |
| Podman Compose-provider installation | The selected package URLs, including `files.pythonhosted.org`, and Python package-index access at `pypi.org` where used by installation. |
| Podman NVIDIA provisioning | `nvidia.github.io` and the package repositories configured inside the intended Podman machine. |
| Browser maps, imagery, search, and geocoding | The Google or Azure service/SDK destinations used by the chosen configuration; include any separately configured address-provider fallback. |
| Prerequisite installation or updates | The approved vendor destinations for Windows/WSL, the engine, Python, and NVIDIA software as applicable. |

This is a preparation checklist, not a complete firewall allowlist. The release
page does not supply a ready-made endpoint list. Use the package's pinned
download references and current vendor documentation, then record the actual
redirects and service destinations during approved setup. Approve only the
destinations needed by that configuration.

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
[TowerScout issue tracker](https://github.com/cdcai/TowerScout/issues).
It is not a private or guaranteed-response service. Local IT retains
responsibility for organization-managed controls and sensitive evidence.

For exact commands and data boundaries, use the version-matched
[packaged Local IT guide](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/docs/local-it-administrator-guide.md).

Export a dataset ZIP before stopping and restore it if live results do not reappear; retained named volumes are not a substitute for a saved review.

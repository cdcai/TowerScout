# TowerScout Local IT Administrator Guide

**Applies to**: The next documentation-aligned Windows release package unless
its release notes state otherwise
**Last reviewed**: 2026-10-05
**Audience**: Local IT, security, and endpoint-management staff.

**Runtime scope**: Windows 11 x64. The end user may choose Docker or Podman and
CPU or a compatible NVIDIA GPU. Local IT confirms that the prerequisites and
security boundary for that choice are permitted. The authoritative release
record limits support to exact tested combinations.

This guide describes the approval and support boundary around TowerScout. The
versioned `docs/quick-start.md` and `docs/package-guide.md` files shipped in the
Application Package remain authoritative for exact user commands. The GitHub
release record remains authoritative for exact downloads, public SHA-256
values, image digests, qualified environments, and known limitations.

## Decision Summary

- TowerScout is a local browser application served from a digest-pinned Linux
  container on the Windows workstation. The normal URL is
  `http://localhost:5000`; package defaults bind the host port to loopback.
- Docker CPU, Docker GPU, Podman CPU, and Podman GPU are supported user choices
  when the exact workstation, engine, Compose provider, NVIDIA driver, device,
  and final-release requirements for that path are satisfied.
- The Windows PowerShell scripts are intentionally unsigned. Supported user
  entrypoints are the supplied `.cmd` and `.bat` wrappers, which use a
  process-scoped execution-policy setting and do not change persistent policy.
- The standard package is supported only where the user and organization
  permit those wrappers. Endpoints requiring trusted Authenticode signatures,
  WDAC/AppLocker approval, constrained-language approval, or organization-
  specific allowlisting need a site-owned approval path and are outside the
  standard support claim.
- Do not solve a policy block by disabling Defender/EDR, selecting `Run anyway`
  for unverified files, weakening machine-wide policy, or changing persistent
  execution policy.

## Runtime And Data Shape

| Component | Purpose | Custody consideration |
| --- | --- | --- |
| Application Package ZIP | Small control package with wrappers, Compose files, documentation, manifests, and notices | Verify against the authoritative release SHA-256 before extraction. |
| Model & Data Package ZIP | Model weights, ZIP-code data, and asset manifest | Verify separately; it is large and normally remains unextracted beside the Application Package. |
| Digest-pinned OCI image | TowerScout application and ML runtime | Pulled from GHCR by Docker or Podman; exact digest is release-specific. |
| Browser UI | Local workflow and Google/Azure map SDK | Provider browser keys are visible to someone with access to the running browser and must be restricted accordingly. |
| Named volumes | Configuration, model assets, data, sessions, logs, uploads, caches, and temporary workflow state | May contain sensitive configuration or investigation material; preserve through normal stop/relaunch and govern backup/removal locally. |

TowerScout results are candidates for human review, not a substitute for field
verification, epidemiologic judgment, or the site's data-governance process.

## Prerequisite Approval Checklist

Confirm the exact release notes before approving the user's chosen path.

- Windows 11 on AMD64 with hardware virtualization and WSL 2 allowed by local
  policy.
- A modern supported browser.
- Normal outbound HTTPS access to the exact GitHub release, GHCR, and the
  selected map provider. Proxy or TLS-inspection requirements must be known.
- Enough disk for the two ZIPs, pulled image, extraction, and persistent
  volumes. Follow the release-specific minimum; CUDA images require materially
  more space than CPU images.
- For Docker: Docker Desktop installed, licensed, approved, and running with
  its supported WSL 2 Linux-container backend.
- For Podman: the rootless `podman-machine-default`, approved package-local
  Compose provider, and tested Python 3.12 prerequisite.
- For GPU: an eligible NVIDIA GPU, current Windows/OEM
  driver, WSL integration, and the exact Docker NVIDIA or Podman CDI checks in
  the release notes. A CPU fallback does not pass a required-GPU run.
- A site/user-owned Google Maps or Azure Maps key with billing, API, referrer,
  and usage restrictions appropriate to the deployment.

Normal package use does not require a source checkout, Git, Conda, Node.js, or
VS Code. Host Python 3.12 is required only to install the tested package-local
Podman Compose provider.

## Required Download And Integrity Flow

Use a normal browser and the public
[TowerScout Releases page](https://github.com/J-Schulein/TowerScout/releases).
Select only the entry whose notes identify it as the current supported final
Windows release.

1. Download exactly one Application Package variant, its `.sha256` sidecar,
   the shared Model & Data Package, and its sidecar from the release `Assets`
   section. Do not use GitHub's generated source archives or the green `Code`
   button for the package workflow.
2. Before extraction or unblocking, calculate SHA-256 for both ZIPs. Compare
   each local value with its sidecar and the value displayed in the
   authoritative release record. All three sources must agree.
3. Use Windows File Explorer `Extract All` on only the verified Application
   Package ZIP in a user-writable folder. Spaces in the path are supported.
4. Keep the Application Package ZIP, Model & Data Package ZIP, and both
   sidecars together beside the extracted package folder so setup can discover
   and verify them.
5. Start first setup with the supplied wrapper. Do not invoke the `.ps1` file
   directly as the normal user path.

If the ZIPs cannot remain beside the extracted folder, copy their full paths
from File Explorer and quote both. The example below is for Docker CPU. Keep
the user's chosen `-Engine` and `-Gpu` values when adapting it, replace the
bracketed descriptions, and do not type the brackets:

```powershell
.\setup-towerscout.cmd -Engine docker -Gpu off `
  -PackageZip "[full path copied from the Application Package ZIP]" `
  -AssetZip "[full path copied from the Model & Data Package ZIP]"
```

The backtick continues the command on the next line. Copy the whole block and
retain double quotes around paths containing spaces.

## First Run And Readiness

Setup performs prerequisite, free-space, port, engine, Compose, manifest,
outer-ZIP checksum, asset-layout, and asset-content checks before launch. A
first start can legitimately report `setup_required` because no provider key
has been saved yet. The user should enter the approved key privately through
Setup Wizard or Settings. After a provider validates and assets are present,
readiness should become `ready`.

Do not request the user's key, `.env`, browser network trace, or a screenshot
that exposes a key. Safe readiness evidence consists of state, component
status, configured/not-configured booleans, engine, device policy, selected
device, image digest, loopback binding, and volume count.

## Provider Accounts And Restrictions

TowerScout supports Google Maps and Azure Maps. The organization or user owns
provider enrollment, billing, quotas, API restrictions, monitoring, and
incident response. Browser SDK keys are client-visible by provider design;
they are not secret from someone who can inspect the running browser.

TowerScout currently accepts one credential per provider and uses it for both
browser and application requests. It cannot use separate browser/server Google
keys or Microsoft Entra ID for Azure Maps. If site policy requires either, the
current release is not eligible. Otherwise use a dedicated limited provider
project/account, API restrictions, quotas, alerts, monitoring, and rotation.
Never commit a key, place it in a release package, paste it into an issue, or
publish it in screenshots, logs, browser traces, or support evidence. See the
clickable [provider credential walkthrough](quick-start.md#prepare-one-map-provider-credential)
and `PROVIDER_TERMS.md`.

## Network And TLS Inspection

Allow only the destinations needed for the selected release and provider. The
container engine must reach GHCR for the pinned image; TowerScout and its
browser must reach the selected map provider. Record site proxy and TLS-
inspection requirements before user testing.

If provider validation reports an untrusted CA, run the package's documented
TLS diagnostic without `-Apply`, review the proposed certificate and target
privately, and obtain the required site approval. Run the separate `-Apply`
form only after that review. Import only the site-approved CA and preserve
certificate details as sensitive evidence. Do not disable certificate
verification or set an insecure TLS override. Docker and Podman use separate
configuration volumes, so repair the selected engine only.

Use the version-matched
[Provider-Key Validation Or TLS Failure procedure](package-guide.md#provider-key-validation-or-tls-failure).
It separates **Diagnostic only**, **Review and obtain approval**, and **Apply
the approved change**. Preserve the user's recorded provider, engine, GPU mode,
and port; run only one matching alternative rather than pasting every example.

## Persistent Volumes, Backup, And Removal

Normal `scripts\stop.cmd` followed by `start.bat` removes/recreates the
container and network while preserving named volumes. That is the supported
restart path. Provider configuration, imported assets, and applicable runtime
state should survive.

Named volumes can include provider configuration, CA bundles, logs, sessions,
uploads, cached map responses, model/data assets, and exported or temporary
investigation data. Apply the site's retention, backup, access-control, and
secure-disposal policy. Do not run a broad Docker/Podman prune or remove named
volumes during ordinary troubleshooting, upgrade, rollback, or evidence
collection.

An uninstall or reset that deletes volumes is destructive and must be a
separate, explicitly approved procedure after required data and evidence are
backed up.

## Safe Support Evidence

A public issue or approved maintainer may request:

- exact release URL/tag and filenames;
- local SHA-256 values and whether they match the published record;
- Windows version, engine version, Compose-provider identity, and available
  disk;
- readiness state and redacted component status;
- engine, device policy, selected device, PyTorch flavor, and image digest;
- loopback port, container health, and named-volume count; and
- a short sanitized error category and the command that produced it.

Do not send provider keys, `.env`, raw logs, raw screenshots, private AOIs,
provider URLs or response bodies, browser console/network traces, certificate
thumbprints/issuer details, cached imagery, exported datasets, volume contents,
or local user/host identifiers through public channels. Use an approved private
handling path when deeper investigation is necessary. The current public route
is the [TowerScout issue tracker](https://github.com/J-Schulein/TowerScout/issues),
which is not a private or guaranteed-response help desk.

## Stop And Escalate

Stop the package workflow and use the site's normal approval/support process
when:

- a published hash is absent or any of the three hash sources differs;
- Windows, SmartScreen, Defender/EDR, WDAC/AppLocker, constrained language, or
  another organization control blocks the package;
- the required engine, WSL 2, virtualization, Compose provider, disk, network,
  or GPU prerequisite is unavailable;
- setup reports an unsafe/mismatched ZIP, missing/corrupt assets, or `fatal`;
- the requested GPU path selects CPU or reports an architecture mismatch;
- provider validation fails after the correct restricted key is entered; or
- the selected port cannot remain loopback-only.

Record the exact supported subset. Do not reinterpret an untested or blocked
environment as passed.

## Upgrade And Handoff Checklist

- Use a new empty working folder and the exact next-release bytes; do not mix
  ZIPs or sidecars across releases.
- Preserve existing volumes until the release-specific upgrade or rollback
  procedure and data owner approve a change.
- Confirm the running app's `/docs/` Help content matches the package and
  release being installed.
- Reverify hashes, image digest, engine/device selection, provider readiness,
  stop/relaunch persistence, and the release's required smoke workflow.
- Keep the source, SBOM reference, license/model/data/provider notices, and
  release manifest with the handoff.
- Before broad distribution, verify the public release links and displayed
  hashes without a privileged GitHub session.

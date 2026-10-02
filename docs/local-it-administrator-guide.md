# TowerScout Local IT Administrator Guide

**Applies to**: The next documentation-aligned Windows release package unless
its release notes state otherwise
**Last reviewed**: 2026-10-02
**Audience**: Local IT, security, endpoint-management, and support staff
**Runtime scope**: Windows 11 AMD64; Docker CPU is the default path. Docker GPU,
Podman CPU, and Podman GPU are support-assigned paths that require the exact
release-specific qualification named in the authoritative release record.

This guide describes the approval and support boundary around TowerScout. The
versioned `docs/quick-start.md` and `docs/package-guide.md` files shipped in the
Application Package remain authoritative for exact user commands. The GitHub
release record remains authoritative for exact downloads, public SHA-256
values, image digests, qualified environments, and known limitations.

## Decision Summary

- TowerScout is a local browser application served from a digest-pinned Linux
  container on the Windows workstation. The normal URL is
  `http://localhost:5000`; package defaults bind the host port to loopback.
- The CPU Application Package on Docker Desktop is the normal user path.
  CUDA and Podman paths are assigned only after support validates the exact
  workstation, engine, Compose provider, NVIDIA driver, and device path.
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

Confirm the exact release notes before assigning a path.

- Windows 11 on AMD64 with hardware virtualization and WSL 2 allowed by local
  policy.
- A modern supported browser.
- Normal outbound HTTPS access to the exact GitHub release, GHCR, and the
  selected map provider. Proxy or TLS-inspection requirements must be known.
- Enough disk for the two ZIPs, pulled image, extraction, and persistent
  volumes. Follow the release-specific minimum; CUDA images require materially
  more space than CPU images.
- Docker Desktop installed, licensed, approved, and running for the default
  path.
- For a support-assigned Podman path: the named Podman machine, approved
  package-local Compose provider, and its documented Python prerequisite.
- For a support-assigned GPU path: an eligible NVIDIA GPU, current Windows/OEM
  driver, WSL integration, and the exact Docker NVIDIA or Podman CDI checks in
  the release notes. A CPU fallback does not pass a required-GPU run.
- A site/user-owned Google Maps or Azure Maps key with billing, API, referrer,
  and usage restrictions appropriate to the deployment.

Normal package use does not require a source checkout, Git, Conda, Node.js,
VS Code, or a host Python environment. The approved Podman Compose-provider
installer is the exception when that support-assigned path is selected.

## Required Download And Integrity Flow

Use a normal browser and the exact GitHub release link supplied by the release
owner or support team.

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

If the ZIPs cannot remain beside the extracted folder, quote both exact paths:

```powershell
.\setup-towerscout.cmd -Engine docker -Gpu off `
  -PackageZip "C:\Approved Path\towerscout-<release-version>-cpu.zip" `
  -AssetZip "C:\Approved Path\towerscout-<release-version>-assets-<asset-version>.zip"
```

Do not type the angle-bracket placeholders. Copy exact filenames from the
release `Assets` section or the download folder.

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

Use the narrowest practical provider restrictions and separate browser/server
credentials where the provider supports that model. Never commit a key, place
it in a release package, paste it into an issue, or publish it in screenshots,
logs, browser traces, or support evidence. See `PROVIDER_TERMS.md` in the
package for the release boundary.

## Network And TLS Inspection

Allow only the destinations needed for the selected release and provider. The
container engine must reach GHCR for the pinned image; TowerScout and its
browser must reach the selected map provider. Record site proxy and TLS-
inspection requirements before user testing.

If provider validation reports an untrusted CA, use the package's documented
TLS diagnostic and support-directed CA import path. Review the dry-run output
privately, import only the site-approved CA, and preserve certificate details
as support-sensitive evidence. Do not disable certificate verification or set
an insecure TLS override. Docker and Podman use separate configuration volumes,
so repair the selected engine only.

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

Support may request:

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
handling path when deeper investigation is necessary.

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

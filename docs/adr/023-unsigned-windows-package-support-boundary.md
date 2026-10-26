# ADR-023: Unsigned Windows Package Support Boundary

**Status**: Accepted
**Date**: October 1, 2026
**Scope**: Windows host scripts, execution policy, download verification,
managed-endpoint claims, release documentation, and clean-machine acceptance

## Decision

1. TowerScout will release the Windows control package without Authenticode
   signatures on its PowerShell scripts. The project will not obtain or
   maintain a project code-signing certificate for this release line.
2. The supported Windows environment is one where the user and organization
   permit the provided TowerScout `.cmd` and `.bat` entrypoints to run. Those
   wrappers invoke Windows PowerShell 5.1 with process-scoped
   `-ExecutionPolicy Bypass`; they do not change the machine's persistent
   execution-policy settings.
3. The standard package does not claim compatibility with endpoints that
   require a trusted Authenticode publisher or organization-specific WDAC,
   AppLocker, constrained-language, antivirus/EDR, or application-allowlisting
   approval. Those environments require their administrator to approve,
   allowlist, or internally sign the package.
4. Release identity and integrity rely on the authoritative release page,
   immutable versioned assets, published SHA-256 values, internal
   `SHA256SUMS.txt`, source references, and digest-pinned OCI images. Users
   verify the official hash before extracting or unblocking a downloaded ZIP.
5. TowerScout documentation will not instruct users to weaken persistent
   execution policy, disable Defender/EDR, or bypass an organizational control.
   An unexpected publisher, SmartScreen, antivirus, or policy block is a stop
   condition until the package source and site approval are confirmed.
6. Final clean-machine acceptance must exercise the exact browser-downloaded
   unsigned ZIP as an ordinary user, including the Windows downloaded-file
   marker and the documented extraction path. A locally built or copied ZIP
   without that marker is not sufficient evidence for this boundary.

## Context

The current TowerScout Windows package uses PowerShell scripts behind `.cmd`
and `.bat` wrappers. Representative package scripts are unsigned, and the
wrappers already use a process-scoped bypass. Local `rc4` execution proves that
this wrapper path functions on the first host; it does not prove compatibility
with an organization that requires signed code.

Project-owned Authenticode signing would require certificate procurement,
private-key custody, timestamping, renewal, incident handling, signed-byte
packaging order, and target-organization trust validation. The future owner
does not want to accept that continuing obligation. The release therefore
narrows its supported environment instead of implying universal managed-
endpoint compatibility.

## Consequences

- The execution-policy/signing decision is resolved for the claimed unsigned
  support profile. Signature-enforcing managed endpoints are out of scope, not
  passed.
- The supplied `.cmd` and `.bat` files are the supported entrypoints. Direct
  invocation of internal `.ps1` files is a support/developer path unless a
  guide explicitly says otherwise.
- Checksum authenticity depends on obtaining the hash from the authoritative
  release record, not solely from a sidecar downloaded beside the ZIP.
- Sites that internally sign or repackage TowerScout own the modified bytes
  and must issue new checksums. The project qualifies only its original
  published artifacts.
- User manuals, release notes, support instructions, and agent guidance must
  disclose this boundary before a control ZIP is frozen for independent use.
- Documentation changes included in the package change the control ZIP bytes.
  The existing local `rc4` ZIPs remain historical qualification evidence but
  cannot be the final distributed packages after this documentation update.

## Required Validation

- Compare the downloaded control and asset ZIP hashes with values displayed in
  the authoritative release record before extraction.
- Use the supported Windows/File Explorer extraction path from a user-writable
  directory containing spaces.
- Run the provided wrapper entrypoints as an ordinary user without changing
  persistent execution policy or disabling endpoint protection.
- Record any SmartScreen, publisher, antivirus/EDR, or policy prompt and stop
  rather than claiming success if organizational approval is required.
- Repeat the required Docker/Podman CPU/NVIDIA acceptance against the newly
  identified package bytes on the required independent hosts.

## Review Triggers

Revisit this decision if a future owner chooses to support signature-enforcing
enterprise endpoints, an actual supported-site policy rejects the wrapper
path, Microsoft materially changes downloaded-script behavior, or TowerScout
adopts a native installer or another host-launch mechanism.

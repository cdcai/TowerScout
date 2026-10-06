# TASK-097: Podman CPU/GPU Final Path Qualification

**Status**: AT_RISK - final `rc4` Podman CPU/GPU package paths pass on the
first host, including provider workflows, TLS repair, cancellation recovery,
exports, persistence, reboot restoration, and real CUDA execution;
independent-host proof remains
**Priority**: HIGH
**Type**: C (Runtime Qualification)

## Objective

Qualify the exact release package on Podman CPU and NVIDIA GPU without Docker
Desktop, using the approved Compose provider and intended Podman target.

## Requirements

- WHEN Podman is selected, THE PACKAGE SHALL use the intended machine,
  connection, and rootful/rootless mode or fail before mutation.
- WHEN Podman GPU is qualified, THE SYSTEM SHALL execute both models on CUDA
  through the intended WSL2/NVIDIA CDI path with no CPU fallback.
- WHEN the approved Compose provider is installed, THE USER SHALL need Python
  but not Git, Node, a source checkout, or a development environment.

## Acceptance Boundary

W01 records actual machine/provider/Python/CDI availability. W03 addresses only
reproduced targeting/process-boundary defects. W09/W10 qualify the exact ZIPs,
digests, asset bundle, providers, persistence, recovery, and independent host.

## Implementation Log

### 2026-09-22 - W01 Provider And Machine Inventory

**Objective**: Establish whether the first host has an approved standalone
Compose provider and an acceptable Podman target.

**Context**: Podman `6.0.2` is installed. `podman-machine-default` is running,
but the selected default connection is rootful. The existing
`towerscout-task087-rootless` machine and rootless connection are stopped.

**Decision**: Do not start or modify a Podman machine automatically and do not
count the rootful default as rootless acceptance. Continue package-local
provider preparation because it does not change machine state.

**Execution**: The first installer attempt used system Python `3.14.7` and
failed resolving pinned `PyYAML==6.0.2` after its broad `>=3.9` preflight.
The package-managed partial directory was replaced with `-Force` under its
validated cache boundary, using repository Python `3.12.10`. The provider wheel
hash and pinned dependencies verified, the wrapper was written under package
`tools/`, and the package-local `.env` was updated.

**Output**: The wrapper reports `podman-compose 1.5.0` and Podman `6.0.2`; the
package catalog reports provider `podman-compose-pypi-1.5.0` accepted. No
Podman container, volume, network, machine, or connection was changed.

**Validation**: PARTIAL PASS. Provider installation and allowlist validation
pass with Python 3.12. Rootless runtime execution, target binding, CPU inference,
and Docker-Desktop-free proof remain not run. Process-scoped PowerShell was
used only for the catalog diagnostic under this workstation's `Restricted`
policy and is not endpoint-policy acceptance.

**Next**: Have the workstation owner start the existing rootless machine and
select its rootless connection, then run package `VerifyOnly` before any asset
or runtime mutation. Bound the supported provider-installer Python range from
the pinned dependency wheel matrix.

### 2026-09-23 - W03 Rootless Target And Process Boundary Checkpoint

**Objective**: Prevent runtime commands from hanging or silently targeting the
root-owned default Podman connection.

**Decision**: Use the already-running `podman-machine-default` normal-user
connection. Do not change the workstation's global default and do not create a
new machine.

**Execution**: PR #77 at head `a4bf6e1` adds bounded concurrent output draining,
exact Windows argument handling, owned process-tree timeout cleanup, explicit
rootless connection verification, and target-bound Compose/direct operations.
The approved package-local `podman-compose 1.5.0` provider resolves through
Podman `6.0.2` without the Docker Desktop provider.

**Validation**: Local W03 focused/adjacent ring passes `63/63`. The two exact
CI sandbox failures from the first PR head pass after adding the shared
bootstrap dependency to the helperless fixture; the full enabled-helper module
remains locally blocked by endpoint antivirus and is delegated to CI. Read-only
real target/provider probes passed. PR #77's corrected head has green Windows
host-helper, controller, frontend, Docker, security, and Trivy checks; its
Python matrix was still running when recorded. No container, image, volume,
network, machine, or connection state was changed.

**Next**: Use merged commit `99858c2` to perform package `VerifyOnly` and the
CPU rehearsal against the same explicit rootless connection.

### 2026-09-30 - Final `rc4` Podman CPU/GPU Qualification

**Objective**: Repeat the advertised Podman paths with the exact final local
candidate packages and published image digests.

**Execution**: Qualified the Podman CPU package on port 5233 and Podman CUDA
package on port 5234 from source
`541622556fb7999ee4e88fb1e44f7797b9da34f5`. Both used the package-pinned
Compose provider and explicit normal-user Podman connection. Provider
credentials were entered by the workstation owner; no secret value was read,
copied, logged, or retained in evidence.

**Validation**: PASS for the first-host local matrix. Both profiles reached
`ready`, reported the exact pinned image digest, retained all eight named
mounts through stop/relaunch, and preserved configured Google and Azure
providers. Google and Azure each completed real estimate and detection work;
controlled validation failure recovered in the same browser; cancellation
returned HTTP 202 while the slot was held, the frontend waited for
`retryReady`, and the immediate next detection passed. CSV/KML and dataset ZIP
exports were nonempty and structurally valid. Provider TLS repair passed dry
run, apply, fresh-process relaunch, and keyless provider probes. The CUDA
profile executed a finite real kernel on `cuda` with capability 12.0 and no CPU
fallback. No Docker Desktop Compose provider or volume-deleting operation was
used.

### 2026-09-30 - Exact-`rc4` Reboot Restoration

**Validation**: PASS on the first host. The rootless Podman WSL machine was
running after reboot; the retained CPU and CUDA containers were stopped, as
expected, and were manually started in place without recreation. Both returned
healthy on ports 5233/5234 with exact digests, assets/config `ok`, configured
Google and Azure providers, keyless `tls_ok` for both providers, and eight
mounts each. Google and Azure detection plus controlled-error recovery, review
navigation, and valid dataset ZIP export passed on both profiles with zero page
errors. Podman CUDA completed a finite capability-12.0 kernel on `cuda:0`.

**Remaining**: Repeat the final package matrix on the independent Windows
host.

# TASK-097: Podman CPU/GPU Final Path Qualification

**Status**: AT_RISK - approved provider passes with Python 3.12; the running
machine's explicit normal-user connection is verified rootless and the W03
target-binding fix is merged; exact-package CPU/GPU and independent-host proof
remain
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

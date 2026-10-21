# Podman GPU Implementation Review

**Date:** 2026-06-15
**Reviewed inputs:** `.agent_work/context/analysis/Podman-GPU-Implementation-Reference/`,
current `main` checkout at `v0.1.0-rc4`, NVIDIA CDI documentation, Podman
Compose documentation

## Verdict

The reference packet is sufficient for me to implement Podman GPU independence
successfully. It gives the needed architecture, exact file-level changes,
decision tree, provisioner behavior, validation ladder, test strategy, and live
hardware evidence.

It is not sufficient by itself to approve a merge because the actual code diff is
not present in this checkout. The current repo still hard-blocks Podman GPU and
does not include the new overlay, provisioner, runbook, or unit tests described
by the implementation report.

## Evidence Strengths

- The validation transcript proves the expected failure path before
  provisioning: WSL2 machine and host GPU are visible, but CDI is missing.
- `enable-podman-gpu.ps1 -DryRun` and `-VerifyOnly` are specified and validated
  as non-mutating checks, which makes the workflow support-safe.
- Provisioning installed or verified NVIDIA Container Toolkit, generated a CDI
  spec, and produced `nvidia.com/gpu=all`.
- Container-level smokes passed with `podman run --device nvidia.com/gpu=all
  --security-opt=label=disable`.
- TowerScout's own device diagnostic reported `selected_device=cuda` in the GPU
  container, which is the right product-level assertion.
- Full launcher validation reached `selected_device=cuda` through the real
  `launch.ps1 -Engine podman -Gpu on` path.
- The report calls out a real Windows PowerShell 5.1 JSON parsing bug found by
  tests, which increases confidence that the implementation was tested in the
  actual user shell, not only PowerShell 7.

## Implementation Sufficiency

I would have enough information to implement the change from the reference:

- Add `compose.gpu.podman.yaml` with CDI device injection and SELinux label
  disablement.
- Add `scripts/enable-podman-gpu.ps1` and
  `scripts/lib/TowerScoutPodmanGpu.ps1`.
- Replace the current Podman GPU throws in `scripts/lib/TowerScoutCompose.ps1`
  with per-engine overlay resolution.
- Add `TOWERSCOUT_PODMAN_GPU_OVERLAY` and keep `-Gpu on` fail-closed on
  readiness `selected_device=cuda`.
- Add the Podman machine/CDI preflight ladder.
- Add or finish the vendored/provider resolver for `PODMAN_COMPOSE_PROVIDER`.
- Add Windows PowerShell unit coverage for overlay decisions, preflight rungs,
  provisioner scenarios, stale-CDI self-heal, image-reference splitting, and
  provider resolution.
- Update support docs only after live GPU evidence is attached.

The current app/Python runtime does not need a GPU-specific change for this
feature. `ts_device` and readiness already expose the selected device and CUDA
failure reason. The work is in PowerShell orchestration, Compose YAML, docs, and
tests.

## Blocking Gaps Before Claiming Support

1. **Actual code diff is absent here.** The reference describes files and tests,
   but this checkout does not contain them. Either provide the implementation
   branch or implement from the spec.
2. **Docker-Desktop-free Podman remains unproven in the GPU launch evidence.**
   The headline run used Docker Desktop's `docker-compose.exe` as the external
   provider over the Podman socket. That proves Podman engine GPU support, but
   not independence from Docker Desktop installation.
3. **The approved Compose provider lifecycle needs an owner decision.** If a
   standalone provider is bundled or blessed, the package needs version,
   checksum, license, and CVE-update handling.
4. **WSL2 resource guidance needs correction.** Podman docs list
   `podman machine set --memory` as QEMU-only, so WSL2-specific memory guidance
   should be validated before publishing that command.
5. **Post-reboot and stale-CDI drills are still valuable.** The implementation
   handles stale CDI by design, but support confidence would improve with a
   machine restart and, if practical, a driver-update or forced-regeneration
   drill.
6. **Overlay details should be locked by evidence.** The short CDI `devices:`
   form worked in the reported run. Keep the long `driver: cdi` form as a
   fallback, but ship one selected form with evidence. Keep or remove
   `security_opt: label=disable` based on validation; do not guess.

## Recommended Merge Gate

Before merging Podman GPU support into the release path:

- Run focused unit tests under Windows PowerShell 5.1.
- Run `compose config` against base, Docker GPU, and Podman GPU overlay
  combinations.
- Run a true Docker-Desktop-free Podman CPU setup/import/status smoke with the
  approved provider.
- Run the Podman GPU ladder on the GPU machine from a clean or documented state:
  negative `-Gpu on`, dry run, verify-only, provisioning, verify-only again,
  container smoke, TowerScout launch, readiness capture.
- Preserve `runtime-versions.json`, launch logs, `nvidia-smi`, `cdi list`, and
  readiness JSON in a task-local evidence folder.
- Run fixed-fixture parity, or explicitly mark parity as the remaining support
  gate if it cannot be run in the same sitting.

## Documentation Position

The right support language after implementation is:

- Podman CPU is supported only with an approved Compose provider.
- Podman GPU is supported only on validated WSL2 Podman machines with NVIDIA
  Toolkit/CDI provisioned by the TowerScout script.
- `-Gpu on` is fail-closed and only succeeds when TowerScout readiness reports
  `selected_device=cuda`.
- `-Gpu auto` remains CPU-safe when the Podman GPU gate is not ready.

Do not state "no Docker Desktop reliance" until the approved provider path is
validated on a host where Docker Desktop is not installed or is unavailable and
not selected by `podman compose`.

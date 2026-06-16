# RC4 Application Follow-ups

**Date:** 2026-06-15
**Sources:** `Podman-GPU-Implementation-Reference/podman-gpu-validation-evidence/rc4-uat/UAT-REPORT-rc4.md`, `Podman-GPU-Implementation-Reference/podman-gpu-validation-evidence/VALIDATION-EVIDENCE.md`, `Podman-GPU-Implementation-Reference/podman-gpu-validation-evidence/audit-docs/podman-gpu-cdi-implementation-report-2026-06-14.md`, current `main` checkout at `v0.1.0-rc4`

## Summary

RC4 passed the release validation matrix. The application changes still worth
incorporating are not model fixes; they are runtime/setup supportability fixes:

1. Make rerun setup reuse valid staged assets instead of failing on auto-discovered asset ZIPs.
2. Make Podman CPU genuinely Docker-Desktop-free by blessing or packaging a Compose provider.
3. Lift Podman GPU only through the CDI-gated implementation path validated in the reference packet.
4. Preserve fixed replay fixtures for future RC comparisons.
5. Clean up release manifest checksum metadata so the package checker can pass without recommended-field warnings.
6. Keep several reviewer-audit hardening items on the backlog for self-serve or broader release posture.

The current checkout still hard-blocks Podman GPU in `scripts/lib/TowerScoutCompose.ps1`
and does not include `compose.gpu.podman.yaml`, `scripts/enable-podman-gpu.ps1`,
`scripts/lib/TowerScoutPodmanGpu.ps1`, or `tests/unit/test_podman_gpu_enablement.py`.
Treat the reference folder as validated design/evidence, not code already merged here.

## Follow-ups To Incorporate

### RC4-F1: Reuse Valid Staged Assets On Re-setup

**Priority:** High for UAT/support UX.
**Current behavior:** `setup-towerscout.ps1` auto-discovers an asset ZIP unless
`-SkipAssetImport` is passed. If `assets/model_params`, `assets/data`, or
`assets/asset_manifest.v1.json` already exist, `Expand-TowerScoutAssetZip`
throws and suggests omitting `-AssetZip`, but the normal setup path auto-finds
the ZIP again. `-SkipAssetImport` also skips the volume import needed by a fresh
engine.

**Required behavior:** if staged assets already validate against the control
manifest, setup should reuse them and still import them into the selected engine.
Only fail when staged assets are incomplete, corrupt, or manifest-incompatible.

**Implementation notes:**

- In `scripts/bootstrap.ps1`, evaluate `Test-TowerScoutStagedAssets` before
  calling `Expand-TowerScoutAssetZip`.
- If valid staged assets exist and a ZIP is auto-discovered, skip extraction and
  continue to import.
- Keep explicit invalid-staging failures strict; do not silently delete or
  overwrite user assets.
- Update the misleading "omit -AssetZip" guidance for the auto-discovery path.

**Acceptance checks:**

- Rerunning `setup-towerscout.cmd` with an auto-discovered asset ZIP and valid
  existing staged assets succeeds.
- The same rerun imports assets into a fresh Docker or Podman volume.
- Invalid staged assets still fail before launch/import with actionable guidance.
- Focused unit coverage exercises valid staged reuse, invalid staged failure,
  and `-SkipAssetImport` behavior.

### RC4-F2: Docker-Desktop-Free Podman Compose Provider

**Priority:** High for the "no Docker Desktop reliance" requirement.
**Current behavior:** RC4 Podman CPU is independent of the Docker engine, but
the UAT run selected Docker Desktop's bundled `docker-compose.exe` as the
external provider for `podman compose`.

**Required behavior:** the supported Podman path must work on a machine with
Podman installed and Docker Desktop absent.

**Implementation notes:**

- Define the approved provider strategy: bundled provider, support-installed
  standalone provider, or documented download with checksum.
- Use `PODMAN_COMPOSE_PROVIDER` to force the approved provider and fail early if
  the path or command is missing.
- Keep `compose cp` support in the provider decision because asset import
  depends on it before the direct `podman cp` fallback is needed.
- Surface the selected provider path/version in setup, launch, status, and
  support evidence.

**Acceptance checks:**

- On a host without Docker Desktop installed, `setup-towerscout.cmd -Engine podman -Gpu off`
  reaches readiness with the approved provider.
- `scripts/import-assets.cmd -Engine podman ...` works on that same host.
- Logs/evidence prove the selected provider is not under Docker Desktop.
- Tests cover missing provider, invalid provider override, and provider override
  success.

### RC4-F3: Podman GPU CDI Enablement

**Priority:** High if Podman GPU is in scope for the next package.
**Current behavior:** current `main` blocks Podman GPU by design. The reference
packet shows a validated implementation path on NVIDIA T1000 hardware.

**Required behavior:** Podman GPU must remain gated until WSL2, Podman version,
host GPU visibility, machine GPU visibility, CDI device registration, container
smoke, and TowerScout readiness all pass.

**Implementation notes from the reference packet:**

- Add `compose.gpu.podman.yaml` using CDI `devices: [nvidia.com/gpu=all]` and
  `security_opt: label=disable`.
- Add `scripts/enable-podman-gpu.ps1` plus a testable
  `scripts/lib/TowerScoutPodmanGpu.ps1` provisioner.
- Add a Podman GPU preflight ladder and route all podman calls through one
  mockable command seam.
- Gate overlay selection with a Podman-specific opt-in such as
  `TOWERSCOUT_PODMAN_GPU_OVERLAY`.
- Preserve fail-closed launch semantics: `-Gpu on` is not successful unless
  readiness reports `selected_device=cuda`.
- Keep `auto` CPU-safe when the Podman GPU gate is not ready.

**Acceptance checks:**

- `enable-podman-gpu.ps1 -DryRun` executes no mutations and prints the plan.
- `enable-podman-gpu.ps1 -VerifyOnly` fails read-only when CDI is missing.
- Full provisioning installs or verifies NVIDIA Container Toolkit, verifies CDI,
  runs `podman run --device nvidia.com/gpu=all --security-opt=label=disable ...`,
  and records runtime versions.
- `launch.ps1 -Engine podman -Gpu on` reaches readiness with
  `selected_device=cuda`.
- Unit tests pass under Windows PowerShell 5.1, including machine-list JSON
  parsing.
- Package docs clearly require a CUDA image digest for Podman GPU.

### RC4-F4: Podman Machine Resource Guidance

**Priority:** Medium.
**Current behavior:** RC4 evidence shows Podman CPU was much slower than Docker
CPU on the same workload, and the tested Podman machine had a 2 GiB memory cap.

**Required behavior:** docs and preflight output should warn when the Podman
machine is materially under-resourced.

**Implementation notes:**

- Report machine memory/CPU allocation when available.
- Avoid publishing `podman machine set --memory 8192` as universal guidance
  until the WSL2 behavior is confirmed; current Podman docs list `--memory` for
  QEMU machines.
- Prefer wording such as "increase the Podman/WSL2 machine memory allocation per
  your installed Podman version" unless live WSL2 commands are validated.

**Acceptance checks:**

- Support docs state a minimum/recommended memory posture without overclaiming a
  command that does not apply to WSL2.
- Preflight output highlights low-memory Podman machines as a performance risk,
  not a correctness failure.

### RC4-F5: Preserve Fixed Replay Fixtures

**Priority:** Medium for release validation quality.
**Current behavior:** RC4 replay compared cleanly across engines/devices, but
RC3 and RC4 counts could not be fully compared because the RC3 fixture tiles
were not preserved.

**Required behavior:** every release-candidate parity baseline should preserve
the exact fixed tile fixture or a support-safe equivalent.

**Implementation notes:**

- Store fixture tiles and replay scripts under task-local evidence, not general
  status docs.
- Keep provider keys, tile URLs, private coordinates, and raw private imagery
  out of committed evidence.
- Add a small parity-summary artifact that records tile count, detection count,
  selection flips, max coordinate/confidence deltas, image digest, model
  manifest hash, provider, engine, and selected device.

**Acceptance checks:**

- Future RC evidence can rerun CPU/GPU and Docker/Podman comparisons against the
  exact same fixture.
- A reviewer can distinguish imagery/provider drift from model/runtime drift.

### RC4-F6: Release Manifest Checksum Metadata

**Priority:** Medium/low.
**Current behavior:** the rc4 package was digest-pinned and checksum sidecars
matched, but manifest validation still warns about recommended fields and blank
artifact checksum values.

**Required behavior:** generated release manifests should carry the package ZIP
hash, asset ZIP hash, release version/posture, and source ref using the schema
keys expected by the checker.

**Acceptance checks:**

- `check_release_manifest.py` runs cleanly against the packaged manifest or the
  checker is updated to accept the canonical key names.
- `release-manifest.v1.json`, `IMAGE.txt`, `SOURCE.txt`, and sidecars all agree.

## Carry-forward Reviewer-Audit Hardening

These items did not block RC4 but still matter before a broader or less guided
release:

- Raw provider-key endpoints `/getgooglekey` and `/getazurekey` still exist.
  Browser map SDK keys are client-visible by design, but the endpoints should be
  reviewed before self-serve deployment. Prefer server-side proxy paths where
  practical and gate raw-key responses to configured/setup-safe states.
- `webapp/templates/towerscout.html` still uses a static bundle query token
  ending in `WIDTH`; replace it with a build hash/date or remove the manual
  cache token.
- Bing remains partially wired in configuration/provider discovery without a
  complete supported map implementation. Either finish the provider or remove
  visible/support-facing scaffolding.
- Keep `/debug-azure-maps` gated by `TOWERSCOUT_ENABLE_DEBUG_AZURE_MAPS`; do not
  expose debug-only routes in external UAT packages.

## Not Recommended

- Do not make TF32, model, or threshold changes as the response to the RC4 GPU
  evidence. The fixed-fixture runs support runtime parity; the remaining work is
  orchestration and evidence discipline.
- Do not claim Podman GPU support merely because CDI provisioning worked once.
  It should be shipped only with the gate, provisioner, docs, test coverage, and
  post-start CUDA assertion.
- Do not claim Docker-Desktop-free Podman support until the Compose provider path
  is proven without Docker Desktop installed.

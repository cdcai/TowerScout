# TowerScout OCI Quick Start

**Applies to**: Current V1 release-candidate package support path
**Last reviewed**: 2026-06-15
**Audience**: Release/support users who need engine-level detail
**Runtime scope**: Docker Desktop CPU is the primary path; Podman CPU, Docker
GPU, and Podman GPU are support-assigned RC5 paths after workstation-specific
engine, Compose-provider, and NVIDIA validation.

This guide covers the v1 local container package shape for TowerScout for
release/support users who need engine-level detail. External pilot users
should start with `docs/quick-start.md` instead.

The primary pilot path is Docker Desktop with the WSL 2 backend, launched
with CPU-safe `-Gpu off`. Podman remains a qualified support-directed package
runtime path only when the workstation has a running Podman machine and an
approved non-Docker-Desktop Compose provider.

## Supported V1 Target

- Windows 11 on AMD64
- Single-user local use
- CPU baseline
- Normal outbound internet access for GHCR image pulls and map providers
- Docker Desktop with WSL 2 backend for the primary pilot path, or a
  support-approved Podman machine and Compose provider for the qualified Podman
  path
- Optional Docker GPU and Podman GPU launch after support validates the selected
  engine's NVIDIA container path

Out of scope for v1: Mac, ARM64, air-gapped/offline installs, VDI, shared multi-user hosting, native installer behavior, and managed remote deployment.

## Prerequisite Software

The normal pilot package path expects Windows PowerShell, a modern browser,
normal outbound internet access, and Docker Desktop with the WSL 2 backend
licensed, approved, installed, and running. The Podman path requires support
direction, a created and running Podman machine, and an approved Compose
provider. The RC5 Podman GPU path additionally requires WSL2 Podman, NVIDIA
host drivers, NVIDIA Container Toolkit/CDI inside the Podman machine, and a
readiness result with `selected_device=cuda`.

Pilot users do not need Git, Python, Conda, Node.js, VS Code, or a source-code
checkout for the package path. If both Docker and Podman are installed, the
launcher can choose Docker first. Use `-Engine podman` consistently only when
validating a support-directed Podman path.

## Package Contents

The release package is expected to include:

- `compose.yaml`
- `compose.gpu.yaml`
- `compose.gpu.podman.yaml`
- `.env.example`
- `setup-towerscout.cmd`
- `scripts/setup-towerscout.ps1`
- `bootstrap.cmd`
- `scripts/bootstrap.ps1`
- `scripts/lib/TowerScoutBootstrap.ps1`
- `start.bat`
- `scripts/launch.ps1`
- `scripts/start.cmd` / `scripts/start.ps1`
- `scripts/stop.cmd` / `scripts/stop.ps1`
- `scripts/logs.cmd` / `scripts/logs.ps1`
- `scripts/status.cmd` / `scripts/status.ps1`
- `scripts/import-assets.cmd` / `scripts/import-assets.ps1`
- `scripts/import-tls-ca.cmd` / `scripts/import-tls-ca.ps1`
- `scripts/enable-podman-gpu.ps1`
- `LICENSE`
- `NOTICE`
- `THIRD_PARTY_NOTICES.md`
- `MODEL_LICENSES.md`
- `DATA_LICENSES.md`
- `PROVIDER_TERMS.md`
- `SOURCE.txt`
- `SBOM.txt`
- `release-manifest.v1.json`
- `webapp/asset_manifest.v1.json`
- `IMAGE.txt`
- `SHA256SUMS.txt`
- Quick Start, Package Guide, User Guide, Project Overview, and runtime-contract documentation
- release asset bundle contract documentation
- a pinned GHCR image reference by digest

Large model and ZIP-code assets are not stored in git and are not expected to be baked into the default source checkout.

## Source And License Notices

The YOLO-enabled package is the `agpl-yolo` release track. TowerScout-authored code may be Apache-2.0 where ownership and relicensing authority are confirmed, but the package and image are not Apache-2.0-only because they include Ultralytics YOLOv5 AGPL-3.0 runtime source and YOLO-derived detector weights.

Users can review the source and license notice from the running app at:

```text
http://localhost:5000/license
```

Release packages include `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `MODEL_LICENSES.md`, `DATA_LICENSES.md`, `PROVIDER_TERMS.md`, `SOURCE.txt`, `SBOM.txt`, and `release-manifest.v1.json`. Do not remove these files from a release package or image.

The release control ZIP is authoritative for release-specific metadata such as
source ref, image digest, checksums, SBOM reference, and release manifest. The
container image carries generic notices and OCI labels; it should be matched to
the control ZIP by the pinned image digest in `IMAGE.txt`.

## Creating A Release Package

Release maintainers can assemble the control package from a source checkout:

```powershell
.\scripts\package-release.cmd -Version v0.1.0 -Image ghcr.io/j-schulein/towerscout:v0.1.0-cuda121 -ImageDigest sha256:<digest> -PytorchFlavor cuda121
```

This creates `dist\towerscout-v0.1.0\`, `dist\towerscout-v0.1.0.zip`, and `dist\towerscout-v0.1.0.zip.sha256`. The package includes `IMAGE.txt` for the release image reference and `SHA256SUMS.txt` for the files inside the package.

Release package generation requires `-ImageDigest` with an immutable `sha256:<digest>` reference, a git source ref, a clean working tree, and an explicit or inferred PyTorch flavor (`cpu` or `cuda121`). For developer-only local validation with a mutable image tag, pass `-AllowMutableImage` explicitly. For local validation packages only, `-AllowMissingSourceRef` and `-AllowDirtySource` can bypass source-ref and clean-tree enforcement.

## Publishing The GHCR Image

The manual GitHub Actions workflow `.github/workflows/container-publish.yml` publishes the Linux/AMD64 image to:

```text
ghcr.io/j-schulein/towerscout
```

Run the workflow manually with a release tag such as `<release-version>`. The workflow summary reports the immutable digest reference:

```text
ghcr.io/j-schulein/towerscout@sha256:<digest>
```

Use that digest reference when generating the release package.

The publish workflow has an explicit PyTorch wheel flavor input:

- `cpu`: publishes the smaller CPU-wheel image.
- `cuda121`: publishes the CUDA 12.1 PyTorch image for the single GPU-capable package path.

The workflow publishes flavor-specific tags. For example, a workflow tag input of `<release-version>` with `cuda121` publishes `<release-version>-cuda121`; `push_latest` publishes `latest-cpu` or `latest-cuda121`, not an ambiguous `latest`.

Source-checkout and local-validation defaults use `latest-cpu` when no package
digest is present. Release packages should still pin `TOWERSCOUT_IMAGE` to the
exact digest recorded in the release handoff.

For each release candidate, record the chosen flavor with the image digest in
the release package. A CUDA-capable image remains CPU-safe when launched with
`-Gpu off`. GPU execution is supportable only after selected-engine NVIDIA
container validation, readiness evidence, and fixed-fixture parity are captured.

## First Run

1. For a release package first setup, run setup from the extracted package
   directory. Keep the Model & Data Package ZIP and matching `.sha256` file in
   the extracted package directory or its parent UAT folder:

```cmd
setup-towerscout.cmd
```

Setup checks disk space, port availability, engine readiness, Compose
availability, release metadata, asset ZIP checksum/layout, imports assets with
hash verification when assets are available, then starts TowerScout. Automatic
engine selection prefers a reachable engine over an installed but stopped
engine. Use
`setup-towerscout.cmd -Engine podman` only for the support-directed Podman
path, and use `setup-towerscout.cmd -Engine docker -Gpu auto|on` only for
support-directed Docker GPU validation.

2. For later direct launches after setup, start TowerScout from the package
   directory:

```cmd
start.bat -Engine docker -Gpu off
```

3. Wait for the launcher to report readiness.
4. Use the Setup Wizard to configure Google Maps or Azure Maps after the browser opens.

The launcher creates `.env` from `.env.example` when `.env` is missing, starts the selected container engine, polls `/api/readiness`, and opens `http://localhost:5000` only after the application shell is reachable. Release packages should already pin `TOWERSCOUT_IMAGE` to an immutable digest in `.env.example`.

If you open the browser manually, use `http://localhost:<port>` rather than
the numeric loopback host. The Azure Maps browser SDK passed release
validation from the `localhost` origin and may reject some numeric-loopback
browser requests due provider CORS behavior.

Provider keys are normally saved through Setup Wizard or Settings into the persistent `towerscout_config` volume. Do not put provider secrets in `.env` unless a site-specific support procedure requires it.

## Local Developer Build

For developer/support use from a source checkout:

```powershell
.\start.bat -Build
```

This uses `compose.build.yaml` and builds `towerscout:local` from the local Dockerfile.

For developer/support validation of the CUDA-capable image path:

```powershell
.\start.bat -Engine docker -Build -Gpu auto
```

The GPU build path switches `PYTORCH_INDEX_URL` to the CUDA 12.1 PyTorch wheel index for `-Gpu auto` or `-Gpu on`. `-Gpu off -Build` always uses the CPU PyTorch wheel index so local support builds do not accidentally inherit a CUDA index from the shell.

## Optional GPU Launch

The default launcher mode is CPU-safe:

```powershell
.\start.bat -Engine docker -Gpu off
```

GPU launch is opt-in and support-assigned:

```powershell
.\start.bat -Engine docker -Gpu auto
.\start.bat -Engine docker -Gpu on
.\start.bat -Engine podman -Gpu on
```

- `-Gpu off` uses the default Compose file and sets `TOWERSCOUT_DEVICE=cpu`.
- `-Gpu auto` sets `TOWERSCOUT_DEVICE=auto` and starts without the selected
  engine's GPU overlay unless the matching overlay gate has been set after
  support validation. Without that explicit override, it uses CPU fallback.
- `-Gpu on` adds the selected engine's GPU overlay, sets
  `TOWERSCOUT_DEVICE=cuda`, and fails readiness if CUDA is unavailable.

GPU launch requires a CUDA-capable TowerScout image plus selected-engine NVIDIA
GPU support available to containers. Docker GPU uses `compose.gpu.yaml`.
Podman GPU uses `compose.gpu.podman.yaml` and NVIDIA CDI
`nvidia.com/gpu=all` after `scripts\enable-podman-gpu.ps1` validates or
provisions CDI.

Before setting `TOWERSCOUT_GPU_AUTO_OVERLAY=1` or
`TOWERSCOUT_PODMAN_GPU_OVERLAY=1`, validate GPU access with the site-approved
NVIDIA container procedure. A host `nvidia-smi` result alone is not enough
because the selected engine may still be unable to pass the GPU into the
container.

## Engine Selection

Scripts auto-detect the engine. To force one:

```powershell
.\start.bat -Engine docker
.\scripts\status.cmd -Engine podman
```

Docker Desktop use depends on license, procurement, endpoint policy, and local
installation approval. It is the primary pilot runtime path. Podman is a
qualified support path when Podman and a working Compose provider are
installed, approved on the workstation, and explicitly selected by support.

On Windows, `podman compose` is a wrapper around an external Compose provider
such as standalone Docker Compose or `podman-compose`. The TowerScout scripts
call `podman compose` for the Podman path, and RC5 validation confirmed the
package can run with standalone Docker Compose v5.1.4 selected explicitly
through `PODMAN_COMPOSE_PROVIDER` rather than Docker Desktop's bundled
provider.

Validated Podman checks on the current host:

- Podman WSL engine startup, named volumes, asset import, readiness, and containerized smoke behavior.
- Podman CPU startup through an approved non-Docker-Desktop Compose provider.
- Podman GPU CDI startup on Windows 11 WSL2 with Podman 5.8.2, NVIDIA T1000
  hardware, standalone Docker Compose v5.1.4 selected through
  `PODMAN_COMPOSE_PROVIDER`, readiness `selected_device=cuda`, and fixed-fixture
  parity against Docker CPU/GPU and Podman CPU.

Podman support prerequisites:

- Podman machine is created and running.
- An approved non-Docker-Desktop Compose provider is installed and can talk to
  the Podman socket.
- If Docker Desktop's bundled Compose provider might be selected, set
  `PODMAN_COMPOSE_PROVIDER` to the approved provider path before running
  TowerScout.

The launcher prints the selected Compose-provider information during startup. For Podman, it also validates that a `PODMAN_COMPOSE_PROVIDER` override points to an existing file or command before starting the application.

## Status And Logs

```powershell
.\scripts\status.cmd -Engine docker
.\scripts\logs.cmd -Engine docker
.\scripts\logs.cmd -Engine docker -Follow
```

`status.ps1` calls Compose `ps` and then polls `/api/readiness`. A `fatal` readiness state returns a nonzero exit code.

The launcher accepts `-NoBrowser` for support checks, `-TimeoutSeconds <seconds>` for slow starts, and `-Port <port>` when `TOWERSCOUT_PORT` is changed.

## Support Diagnostics

For first-line support, collect:

- `scripts\status.cmd -Engine docker` output, or the same command with the
  explicitly selected engine
- `scripts\logs.cmd -Engine docker -Tail 200` output, or the same command with
  the explicitly selected engine
- `IMAGE.txt`
- `webapp\asset_manifest.v1.json`
- `SHA256SUMS.txt`
- `release-manifest.v1.json`
- `SOURCE.txt`
- `SBOM.txt`
- `THIRD_PARTY_NOTICES.md`

The readiness payload includes the app version, image digest, asset manifest version, selected container engine, provider configuration status, asset status, and writable-path checks. The default log volume is `towerscout_logs`, mounted in the container at `/app/webapp/logs`.

Do not share `.env`, provider keys, local CA bundles, uploaded investigation files, exported datasets, cached provider responses, or named-volume contents unless a site-specific support procedure explicitly approves that handling.

## TLS Inspection

If provider key validation fails with "Could not reach the provider validation service" while the container logs show `CERTIFICATE_VERIFY_FAILED`, the container does not trust the certificate authority used by the local network, proxy, or endpoint inspection tool.

If provider key validation returns an internal error and the logs mention an invalid or missing `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` path, the selected runtime volume does not contain the CA bundle named in `.env`. This can happen when switching between Docker and Podman because each engine has its own named volumes. Re-run the CA import helper for the selected engine.

Preferred fix: import the local root/intermediate CA into the persistent config volume and use a combined bundle that keeps the container's normal Debian CA roots. The helper updates the local `.env` after a successful import so future starts use the combined bundle automatically:

```powershell
.\scripts\import-tls-ca.cmd -Thumbprint <windows-certificate-thumbprint>
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu off
```

For Podman:

```powershell
.\scripts\import-tls-ca.cmd -Engine podman -Thumbprint <windows-certificate-thumbprint>
.\scripts\stop.cmd -Engine podman
.\start.bat -Engine podman -Gpu off
```

The helper verifies the combined CA bundle by making a provider request with an invalid test key. It uses `-VerifyProvider auto` by default, which follows `DEFAULT_MAP_PROVIDER` when available and otherwise uses Google. For Azure-first or Google-blocked sites, choose the provider explicitly or skip remote verification:

```powershell
.\scripts\import-tls-ca.cmd -Engine podman -Thumbprint <windows-certificate-thumbprint> -VerifyProvider azure
.\scripts\import-tls-ca.cmd -Engine podman -Thumbprint <windows-certificate-thumbprint> -VerifyProvider none
```

The helper can also import an exported PEM/CER/CRT file:

```powershell
.\scripts\import-tls-ca.cmd -CertificatePath C:\path\to\local-ca.pem
```

After import, `.env` should contain both combined-bundle variables:

```powershell
REQUESTS_CA_BUNDLE=/app/webapp/config/certs/towerscout-ca-bundle.pem
SSL_CERT_FILE=/app/webapp/config/certs/towerscout-ca-bundle.pem
```

The helper writes these values automatically. Restart TowerScout after the helper completes.

The helper verifies Google TLS with an invalid test key. A successful TLS fix returns a normal provider invalid-key response instead of a certificate verification error.

Last-resort validation-only workaround:

```powershell
TOWERSCOUT_ALLOW_INSECURE_TLS=1
```

Do not use the insecure setting as the normal release configuration.

## Persistent Data

The default profile uses named volumes:

- `towerscout_config`: provider config and generated `FLASK_SECRET_KEY`
- `towerscout_model_params`: model weights
- `towerscout_data`: ZIP-code shapefile data
- `towerscout_logs`: app and performance logs
- `towerscout_flask_session`: filesystem sessions
- `towerscout_session_temp`: detection/export/restore working files
- `towerscout_uploads`: uploads and optional debug images
- `towerscout_cache`: map and geocoding cache

These volumes can contain provider keys, addresses, coordinates, uploaded files, logs, cached provider responses, and investigation data. Treat them as sensitive local data.

## Assets

TowerScout readiness reports missing or corrupt required assets as `degraded`. Import or set up assets into the named volumes according to the release asset instructions, then restart TowerScout.

The v1 release package does not implement hosted asset download. Assets are expected to be supplied as a release asset bundle, site-provided bundle, or support-provided bundle and imported with `setup-towerscout.cmd` or `scripts\import-assets.cmd`. For the YOLO-enabled `agpl-yolo` release track, YOLO detector weights must stay labeled as YOLO-derived/AGPL-governed unless separate written model terms say otherwise. A hosted downloader can be added later after the asset host, checksum policy, retry behavior, proxy/TLS handling, and restricted-network fallback are designed and validated.

For a GitHub Release package, keep the Model & Data Package ZIP and matching
`.sha256` file beside the extracted package folder and run
`setup-towerscout.cmd`. Manual fallback only: extract the asset ZIP root entries
into the package's existing `assets\` folder with this layout:

```text
assets/
  asset_manifest.v1.json
  model_params/
    yolov5/
    EN/
  data/
    tl_2025_us_zcta520/
```

Then import and verify it:

```powershell
.\scripts\import-assets.cmd -Engine docker -Source assets
```

The asset ZIP itself should not contain a top-level `assets/` directory. Its
root should contain `model_params/`, `data/`, and `asset_manifest.v1.json`;
extract those entries into the package's existing `assets/` directory. See
`docs/release/release-asset-bundle-contract.md` for the release-matching,
checksum, manifest-copy, and redistribution rules.

For release-candidate or support validation, enable SHA-256 verification during import:

```powershell
.\scripts\import-assets.cmd -Engine docker -Source assets -VerifyHashes -RestartWaitSeconds 180
```

For a source checkout that already has local assets under `webapp/`, use:

```powershell
.\scripts\import-assets.cmd -Source webapp -Engine docker -Build -VerifyHashes
```

For Podman, asset import first uses the selected Compose provider's `cp`
support. If that provider cannot copy files, the helper falls back to direct
`podman cp` against the running TowerScout service container.

Release-candidate validation should enable SHA-256 checks:

```powershell
$env:TOWERSCOUT_VERIFY_ASSET_HASHES = "1"
.\scripts\status.cmd -Engine docker
```

Routine CI and first-run setup should not hash large assets on every readiness poll.

## Restricted Networks

The v1 control package expects the selected engine to pull the pinned `TOWERSCOUT_IMAGE` digest from GHCR unless the image is already present in the local engine image store. A bundled OCI image archive is not part of the supported v1 release package.

For restricted-network sites, the supported v1 fallback is a support-managed preload of the pinned image into the selected Docker or Podman image store, followed by normal package startup and asset import. A first-class OCI archive workflow should be treated as follow-on release engineering work and validated separately before it is promised in user-facing instructions.

## Stop

```powershell
.\scripts\stop.cmd -Engine docker
```

This stops the container but keeps named volumes intact.

## Launcher Troubleshooting

If `start.bat` times out, run:

```powershell
.\scripts\status.cmd -Engine docker
.\scripts\logs.cmd -Engine docker -Tail 200
```

Common causes:

- Selected engine is not installed, not running, or blocked by local endpoint policy.
- WSL2, Hyper-V, virtualization, or Compose provider is not ready or approved on the workstation.
- Podman machine is not created or running; check `podman machine list`.
- Docker Desktop is unavailable, unlicensed for the site, or blocked by procurement or endpoint policy.
- The configured port is already in use; set `TOWERSCOUT_PORT` in `.env` or pass `-Port <port>`.
- Required runtime assets are missing or corrupt; import the asset bundle with `scripts\import-assets.cmd`.
- Restricted network, proxy, or TLS inspection blocks provider-key validation or image pulls.
- No provider key is configured yet; open Setup Wizard when readiness reports `setup_required`.

On Windows startup failures, the launcher prints lightweight host diagnostics. It checks whether `wsl.exe` is available, prints `wsl --status` when possible, and prints `podman machine list` for Podman failures. Treat these as support hints; the selected Docker or Podman engine remains the source of truth for whether TowerScout can start.

# TowerScout OCI Quick Start

This guide covers the v1 local container package shape for TowerScout. It is engine-aware: the same Compose files are intended to work with a validated Docker or Podman host. The current Windows Podman validation covers the Podman engine path, including while Docker Desktop's engine is unavailable, and a Docker-Desktop-free Compose-provider path using `podman-compose`.

## Supported V1 Target

- Windows 11 on AMD64
- Single-user local use
- CPU baseline
- Normal outbound internet access for map providers and asset/bootstrap workflows
- Docker-compatible or OCI-compatible container engine with Compose support

Out of scope for v1: Mac, ARM64, air-gapped/offline installs, VDI, shared multi-user hosting, native installer behavior, and managed remote deployment.

## Package Contents

The release package is expected to include:

- `compose.yaml`
- `.env.example`
- `start.bat`
- `scripts/launch.ps1`
- `scripts/start.cmd` / `scripts/start.ps1`
- `scripts/stop.cmd` / `scripts/stop.ps1`
- `scripts/logs.cmd` / `scripts/logs.ps1`
- `scripts/status.cmd` / `scripts/status.ps1`
- `scripts/import-assets.cmd` / `scripts/import-assets.ps1`
- `scripts/import-tls-ca.cmd` / `scripts/import-tls-ca.ps1`
- `webapp/asset_manifest.v1.json`
- `IMAGE.txt`
- `SHA256SUMS.txt`
- quick-start and runtime-contract documentation
- a pinned GHCR image reference by digest

Large model and ZIP-code assets are not stored in git and are not expected to be baked into the default source checkout.

## Creating A Release Package

Release maintainers can assemble the control package from a source checkout:

```powershell
.\scripts\package-release.cmd -Version v0.1.0 -Image ghcr.io/j-schulein/towerscout -ImageDigest sha256:<digest>
```

This creates `dist\towerscout-v0.1.0\`, `dist\towerscout-v0.1.0.zip`, and `dist\towerscout-v0.1.0.zip.sha256`. The package includes `IMAGE.txt` for the release image reference and `SHA256SUMS.txt` for the files inside the package.

Release package generation requires `-ImageDigest` with an immutable `sha256:<digest>` reference. For developer-only local validation with a mutable image tag, pass `-AllowMutableImage` explicitly.

## Publishing The GHCR Image

The manual GitHub Actions workflow `.github/workflows/container-publish.yml` publishes the Linux/AMD64 image to:

```text
ghcr.io/j-schulein/towerscout
```

Run the workflow manually with a release tag such as `v0.1.0-rc1`. The workflow summary reports the immutable digest reference:

```text
ghcr.io/j-schulein/towerscout@sha256:<digest>
```

Use that digest reference when generating the release package.

## First Run

1. Start TowerScout from the package directory:

```cmd
start.bat
```

2. Wait for the launcher to report readiness.
3. Use the Setup Wizard to configure Google Maps or Azure Maps after the browser opens.

The launcher creates `.env` from `.env.example` when `.env` is missing, starts the selected container engine, polls `/api/readiness`, and opens `http://localhost:5000` only after the application shell is reachable. Release packages should already pin `TOWERSCOUT_IMAGE` to an immutable digest in `.env.example`.

If you open the browser manually, use `http://localhost:<port>` rather than `http://127.0.0.1:<port>`. The Azure Maps browser SDK passed release validation from the `localhost` origin and may reject some `127.0.0.1` browser requests due provider CORS behavior.

Provider keys are normally saved through Setup Wizard or Settings into the persistent `towerscout_config` volume. Do not put provider secrets in `.env` unless a site-specific support procedure requires it.

## Local Developer Build

For developer/support use from a source checkout:

```powershell
.\start.bat -Build
```

This uses `compose.build.yaml` and builds `towerscout:local` from the local Dockerfile.

## Engine Selection

Scripts auto-detect the engine. To force one:

```powershell
.\start.bat -Engine docker
.\scripts\status.cmd -Engine podman
```

Docker Desktop use depends on license, procurement, endpoint policy, and local installation approval. Podman is the preferred open-source runtime target for V1 when Podman and a working Compose provider are installed and approved on the workstation.

On Windows, `podman compose` is a wrapper around an external Compose provider such as `docker-compose` or `podman-compose`. The TowerScout scripts call `podman compose` for the Podman path, and release validation has confirmed the package can run with `podman-compose` selected explicitly through `PODMAN_COMPOSE_PROVIDER` while the Docker Desktop daemon is unavailable.

Validated Podman checks on the current host:

- Podman WSL engine startup, named volumes, asset import, readiness, and containerized smoke behavior.
- Podman startup and containerized smoke while Docker Desktop is fully quit and the Docker daemon is unreachable.
- Podman startup, readiness, status, and containerized smoke through `podman-compose 1.5.0` selected as the external Compose provider instead of Docker Desktop's bundled `docker-compose.exe`.

Podman support prerequisites:

- Podman machine is created and running.
- A Compose provider such as `podman-compose` or another approved provider is installed and can talk to the Podman socket.
- If Docker Compose is installed but should not be used, set `PODMAN_COMPOSE_PROVIDER` to the approved provider path before running TowerScout.

The launcher prints the selected Compose-provider information during startup. For Podman, it also validates that a `PODMAN_COMPOSE_PROVIDER` override points to an existing file or command before starting the application.

## Status And Logs

```powershell
.\scripts\status.cmd
.\scripts\logs.cmd
.\scripts\logs.cmd -Follow
```

`status.ps1` calls Compose `ps` and then polls `/api/readiness`. A `fatal` readiness state returns a nonzero exit code.

The launcher accepts `-NoBrowser` for support checks, `-TimeoutSeconds <seconds>` for slow starts, and `-Port <port>` when `TOWERSCOUT_PORT` is changed.

## Support Diagnostics

For first-line support, collect:

- `scripts\status.cmd` output
- `scripts\logs.cmd -Tail 200` output
- `IMAGE.txt`
- `webapp\asset_manifest.v1.json`
- `SHA256SUMS.txt`

The readiness payload includes the app version, image digest, asset manifest version, selected container engine, provider configuration status, asset status, and writable-path checks. The default log volume is `towerscout_logs`, mounted in the container at `/app/webapp/logs`.

Do not share `.env`, provider keys, local CA bundles, uploaded investigation files, exported datasets, cached provider responses, or named-volume contents unless a site-specific support procedure explicitly approves that handling.

## TLS Inspection

If provider key validation fails with "Could not reach the provider validation service" while the container logs show `CERTIFICATE_VERIFY_FAILED`, the container does not trust the certificate authority used by the local network, proxy, or endpoint inspection tool.

If provider key validation returns an internal error and the logs mention an invalid or missing `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` path, the selected runtime volume does not contain the CA bundle named in `.env`. This can happen when switching between Docker and Podman because each engine has its own named volumes. Re-run the CA import helper for the selected engine.

Preferred fix: import the local root/intermediate CA into the persistent config volume and use a combined bundle that keeps the container's normal Debian CA roots:

```powershell
.\scripts\import-tls-ca.cmd -Thumbprint <windows-certificate-thumbprint>
```

For Podman:

```powershell
.\scripts\import-tls-ca.cmd -Engine podman -Thumbprint <windows-certificate-thumbprint>
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

After import, set both variables in `.env` and recreate the container:

```powershell
REQUESTS_CA_BUNDLE=/app/webapp/config/certs/towerscout-ca-bundle.pem
SSL_CERT_FILE=/app/webapp/config/certs/towerscout-ca-bundle.pem
.\start.bat
```

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

TowerScout readiness reports missing or corrupt required assets as `degraded`. Import or bootstrap assets into the named volumes according to the release asset instructions, then restart TowerScout.

The v1 release package does not implement hosted asset download/bootstrap. Assets are expected to be supplied as a release asset bundle, site-provided bundle, or support-provided bundle and imported with `scripts\import-assets.cmd`. A hosted downloader can be added later after the asset host, checksum policy, retry behavior, proxy/TLS handling, and restricted-network fallback are designed and validated.

For a GitHub Release package, place the asset bundle next to the scripts with this layout:

```text
assets/
  model_params/
    yolov5/
    EN/
  data/
    tl_2025_us_zcta520/
```

Then import and verify it:

```powershell
.\scripts\import-assets.cmd -Source assets
```

For release-candidate or support validation, enable SHA-256 verification during import:

```powershell
.\scripts\import-assets.cmd -Source assets -VerifyHashes
```

For a source checkout that already has local assets under `webapp/`, use:

```powershell
.\scripts\import-assets.cmd -Source webapp -Engine docker -Build -VerifyHashes
```

Release-candidate validation should enable SHA-256 checks:

```powershell
$env:TOWERSCOUT_VERIFY_ASSET_HASHES = "1"
.\scripts\status.cmd
```

Routine CI and first-run setup should not hash large assets on every readiness poll.

## Restricted Networks

The v1 control package expects the selected engine to pull the pinned `TOWERSCOUT_IMAGE` digest from GHCR unless the image is already present in the local engine image store. A bundled OCI image archive is not part of the supported v1 release package.

For restricted-network sites, the supported v1 fallback is a support-managed preload of the pinned image into the selected Docker or Podman image store, followed by normal package startup and asset import. A first-class OCI archive workflow should be treated as follow-on release engineering work and validated separately before it is promised in user-facing instructions.

## Stop

```powershell
.\scripts\stop.cmd
```

This stops the container but keeps named volumes intact.

## Launcher Troubleshooting

If `start.bat` times out, run:

```powershell
.\scripts\status.cmd
.\scripts\logs.cmd -Tail 200
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

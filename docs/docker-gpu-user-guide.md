# TowerScout Docker GPU User Guide

**Applies to**: Current V1 release-candidate package path through the RC7
provider TLS repair baseline, unless release notes say otherwise
**Last reviewed**: 2026-06-29
**Audience**: Windows users assigned Docker Desktop NVIDIA GPU validation
**Runtime scope**: Docker Desktop, CUDA 12.1 Application Package, GPU launch
mode

Use this guide only when support assigns a workstation to the Docker GPU path.
The normal user path is Docker CPU. Docker GPU requires the CUDA Application
Package and workstation-specific NVIDIA container validation.

## Before You Start

Install or confirm these items before running TowerScout.

- Windows 11 on AMD64.
- Windows PowerShell. Use PowerShell from Windows, not a WSL or Ubuntu
  terminal.
- A modern browser such as Microsoft Edge or Google Chrome.
- Normal outbound internet access to GitHub Releases, GHCR, NVIDIA/Docker
  dependencies allowed by local policy, and the selected map provider.
- At least `25 GB` free disk space. CUDA images are larger than CPU images.
- One approved Google Maps or Azure Maps provider key.
- An NVIDIA GPU supported by the current Windows NVIDIA driver.
- Windows Subsystem for Linux 2.
  - Install guide:
    `https://learn.microsoft.com/en-us/windows/wsl/install#install-wsl-command`
  - Note: Admin rights and/or helpdesk support may be required to install this
    software. Check with your local IT support if you encounter problems
    installing this software.
- Docker Desktop.
  - Download page: `https://www.docker.com/products/docker-desktop/`
  - Note: Docker Desktop is free to download. A Docker account is not required
    to run the TowerScout local package, but local license, procurement, and
    endpoint-management rules still apply.

Docker Desktop must be installed, open, and running before entering the
`.\setup-towerscout.cmd` command.

Useful checks from PowerShell:

```powershell
wsl --status
wsl --list --verbose
nvidia-smi
docker --version
docker compose version
```

Expected result: WSL is installed, any listed Linux distribution uses version
`2`, `nvidia-smi` shows the NVIDIA GPU, Docker Desktop is running, and Docker
commands print version information.

Important GPU boundary: a successful host `nvidia-smi` result is not enough by
itself. Docker must also be able to expose the GPU to the TowerScout container.
With `-Gpu on`, TowerScout fails closed unless readiness reports
`selected_device=cuda`.

## Install TowerScout

1. Create a new working folder, for example:

   ```text
   C:\Users\<you>\Documents\TowerScout
   ```

2. Open the TowerScout GitHub Releases page and use the exact release that
   support selected:

   ```text
   https://github.com/J-Schulein/TowerScout/releases
   ```

3. Download these four files from the release `Assets` section into the new
   TowerScout folder:

   ```text
   towerscout-<release-version>-cuda121.zip
   towerscout-<release-version>-cuda121.zip.sha256
   towerscout-<release-version>-assets-<asset-version>.zip
   towerscout-<release-version>-assets-<asset-version>.zip.sha256
   ```

   Do not use the CPU Application Package for this guide. The CPU package
   rejects `-Gpu on`.

4. Extract only the CUDA 12.1 Application Package ZIP:

   ```text
   towerscout-<release-version>-cuda121.zip
   ```

   Leave the Model & Data Package ZIP and both `.sha256` files beside the
   extracted folder. Do not extract the assets ZIP for the normal setup path.

5. Open the extracted application folder in File Explorer. It should contain
   `setup-towerscout.cmd`, `start.bat`, `compose.gpu.yaml`, `scripts\`,
   `docs\`, and `assets\`.

6. In Windows File Explorer, click the address bar, type `powershell`, and
   press Enter.

7. In the PowerShell window, run the support-assigned setup command:

   ```powershell
   .\setup-towerscout.cmd -Engine docker -Gpu on
   ```

   If support is still checking workstation GPU readiness and wants CPU
   fallback allowed during the first pass, they may assign:

   ```powershell
   .\setup-towerscout.cmd -Engine docker -Gpu auto
   ```

8. Keep the PowerShell window open while Docker Desktop downloads and starts
   the CUDA image. The first image pull can take several minutes.

9. When TowerScout opens in the browser, use Setup Wizard or Settings to
   configure one approved provider key. One valid Google Maps or Azure Maps key
   is enough to start.

Setup verifies the package checksum sidecars, imports the Model & Data Package
into Docker named volumes, starts TowerScout, and opens:

```text
http://localhost:5000
```

For a valid Docker GPU launch, status output must show `selected_device=cuda`.
If it shows `cpu`, you are not running the GPU path.

## Stop, Restart, Status, And Logs

Run these commands from the extracted TowerScout application folder.

Stop TowerScout:

```powershell
.\scripts\stop.cmd -Engine docker
```

Start again with required CUDA:

```powershell
.\start.bat -Engine docker -Gpu on
```

Start again with support-approved CPU fallback:

```powershell
.\start.bat -Engine docker -Gpu auto
```

Restart:

```powershell
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu on
```

Check status:

```powershell
.\scripts\status.cmd -Engine docker
```

Show recent logs if support asks:

```powershell
.\scripts\logs.cmd -Engine docker -Tail 200
```

Use the same `-Engine docker` and support-assigned `-Gpu` value on setup,
start, stop, status, logs, asset import, and TLS commands. Docker and Podman
use separate storage.

## Troubleshooting

If setup says the CPU package does not support `-Gpu on`, you extracted the
wrong Application Package. Stop and use the `-cuda121` ZIP from the same
release as the Model & Data Package.

If GPU mode is on but readiness does not report `selected_device=cuda`, stop
validation. Common causes are an outdated NVIDIA driver, Docker Desktop not
using the WSL 2 backend, Docker GPU support blocked by local policy, or using
the CPU package by mistake.

If setup cannot find Docker, open Docker Desktop from the Windows Start menu and
wait until it says the engine is running. Then rerun:

```powershell
docker --version
docker compose version
nvidia-smi
```

If the browser does not open, leave PowerShell open and manually open:

```text
http://localhost:5000
```

If setup reports multiple asset ZIPs, move old TowerScout ZIPs out of the
working folder and rerun setup.

If status is `degraded`, required assets may be missing or corrupt. Ask support
before manually importing assets. A support-directed import command is:

```powershell
.\scripts\import-assets.cmd -Engine docker -Source assets -VerifyHashes -RestartWaitSeconds 180
```

If status is `fatal`, stop validation and send support the release version,
package filename, requested GPU mode, status output, and a reviewed summary of
recent logs. Do not send provider secrets, `.env`, raw screenshots, browser
network traces, exported datasets, or unreviewed raw logs unless your site has
an approved handling procedure.

### Provider TLS Inspection CA

Use this only when Google Maps or Azure Maps key validation fails even though
the key is correct and support sees `CERTIFICATE_VERIFY_FAILED` in container
logs. This
usually means the container does not trust a local TLS inspection root or
intermediate certificate.

Run the guided dry run from the extracted TowerScout application folder:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu on
```

Review the local support-sensitive output with support. Do not paste
certificate subjects, issuer details, or thumbprints into public issue comments
or public release evidence. If the helper identifies a safe CA candidate, it
prints the exact apply command. With support approval, apply the repair and
restart TowerScout:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu on -Apply
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu on
```

If support assigned `-Gpu auto`, use `-Gpu auto` on the repair and restart
commands instead.

If support already knows the correct Windows certificate thumbprint or has an
exported CA file, they can bypass automatic selection:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu on -Thumbprint <windows-certificate-thumbprint> -Apply
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu on -CertificatePath C:\path\to\local-ca.pem -Apply
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu on
```

Do not paste the placeholder text. Replace it with the actual support-provided
thumbprint or certificate path. The helper copies the CA chain into Docker's
persistent TowerScout config volume, builds a combined CA bundle, updates
`.env`, and verifies that selected provider TLS reaches the normal invalid-key
response instead of a certificate error.

If your site uses Azure Maps instead of Google Maps for validation, support may
use `-Provider azure`. If automatic discovery is ambiguous or unavailable,
support may still use the lower-level `scripts\import-tls-ca.cmd` command with a
known `-Thumbprint` or `-CertificatePath`.

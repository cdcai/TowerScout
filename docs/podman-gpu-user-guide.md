# TowerScout Podman GPU User Guide

**Applies to**: The exact documentation-aligned Windows release package named
by the authoritative release record
**Last reviewed**: 2026-10-05
**Audience**: Windows users who choose Podman with NVIDIA GPU processing
**Runtime scope**: Podman, CUDA 12.8 Application Package, GPU launch mode

Use this guide when you choose Podman with a compatible NVIDIA GPU. This path
requires a rootless WSL 2 Podman machine, 64-bit Python 3.12, the package-local
Compose provider, NVIDIA GPU access inside the machine, and NVIDIA CDI.

**Unsigned package boundary**: TowerScout's PowerShell scripts are unsigned.
Use the supplied `.cmd`/`.bat` wrappers only where you and your organization
permit them. They use a process-scoped execution-policy setting and do not
change persistent machine policy. Do not disable endpoint protection or weaken
machine-wide policy; signature-enforcing or organization-allowlisted endpoints
require site-administrator approval.

The documented `enable-podman-gpu.ps1` command below is the one explicit
`.ps1` exception. Its command line applies `Bypass` only to
that PowerShell process; it does not change persistent machine policy.

## Before You Start

Install or confirm these items before running TowerScout.

- Windows 11 on AMD64.
- Windows PowerShell. Use PowerShell from Windows, not a WSL or Ubuntu
  terminal.
- A modern browser such as Microsoft Edge or Google Chrome.
- Normal outbound internet access to GitHub Releases, GHCR, the approved
  Compose provider source if installation is needed, NVIDIA Container Toolkit
  sources if CDI installation is needed, and the selected map provider.
- At least `35 GB` free for package download, image pull/unpack, assets, and
  volumes. The measured CUDA image is `14.4 GB`.
- One user- or organization-owned Google Maps or Azure Maps provider key.
- An NVIDIA GPU supported by the current Windows NVIDIA driver.
- Windows Subsystem for Linux 2.
  - [Microsoft WSL installation guide](https://learn.microsoft.com/en-us/windows/wsl/install#install-wsl-command)
  - Note: Admin rights and/or helpdesk support may be required to install this
    software. Check with your local IT support if you encounter problems
    installing this software.
- Podman Desktop.
  - [Podman Desktop Windows installation guide](https://podman-desktop.io/docs/installation/windows-install)
  - Note: Podman Desktop is free and open source. A Red Hat account is not
    required for the TowerScout local package, but local IT policy still
    controls installation and support.
- 64-bit Python 3.12 from the official
  [Python Windows downloads](https://www.python.org/downloads/windows/).
- The verified package-local Podman Compose provider.
  - TowerScout rejects Docker Desktop's bundled `docker-compose.exe` for the
    Podman path.
  - Install it with the package helper shown below.
- NVIDIA CDI registered inside the Podman machine.
  - CDI validation must show `nvidia.com/gpu=all`.
  - TowerScout readiness must report `selected_device=cuda` after launch.

**GPU and driver boundary**: The CUDA 12.8 Application Package has a
Volta-or-newer architecture expectation. Only GPU, driver, Windows, WSL,
Podman, Compose-provider, toolkit, and CDI combinations explicitly listed in
the release notes are qualified. Maxwell and Pascal are unsupported by the
CUDA package; use the CPU Application Package or `-Gpu off`. Use the current
NVIDIA or OEM production Windows driver that lists your exact GPU. Never
install a Linux display driver inside WSL.

Podman must be installed, the Podman machine must be running, the Compose
provider must be available, and NVIDIA CDI must be validated before entering
the `.\setup-towerscout.cmd` GPU command.

Useful checks from PowerShell:

```powershell
wsl --status
wsl --list --verbose
nvidia-smi
podman --version
podman machine list
podman compose version
```

If the Podman machine exists but is stopped, start it:

```powershell
podman machine start
```

If no machine exists, create and start the default rootless machine:

```powershell
podman machine init --now podman-machine-default
```

Do not initialize it again if it already exists. The package-local Compose and
GPU helpers are run only after download, verification, and extraction in step
8 below; those files do not exist before the package is extracted. Step 8 also
shows the `-VerifyOnly` CDI check. Refresh and reverify CDI after every Windows
NVIDIA driver update. The final release notes control the tested NVIDIA
Container Toolkit version.

Important GPU boundary: a successful host `nvidia-smi` result is not enough by
itself. The Podman machine and the TowerScout container must also be able to
use the GPU through CDI.

If readiness says the GPU is newer than the package build, obtain the current
CUDA 12.8 package. If it says the GPU generation is older than the build, use
the CPU package or `-Gpu off`; do not force an architecture list.

## Install TowerScout

1. Create a new working folder, for example:

   ```text
   C:\Users\<you>\Documents\TowerScout
   ```

2. Open the [TowerScout GitHub Releases page](https://github.com/J-Schulein/TowerScout/releases)
   and select the entry whose notes identify it as the current supported final
   Windows release.

3. Download these four files from the release `Assets` section into the new
   TowerScout folder:

   ```text
   towerscout-<release-version>-cuda128.zip
   towerscout-<release-version>-cuda128.zip.sha256
   towerscout-<release-version>-assets-<asset-version>.zip
   towerscout-<release-version>-assets-<asset-version>.zip.sha256
   ```

   Do not use the CPU Application Package for this guide. The CPU package
   rejects `-Gpu on`.

4. Before extracting anything, calculate the SHA-256 of both ZIPs and compare
   each result with both its downloaded `.sha256` file and the authoritative
   value printed in the final release notes:

   Open the working folder containing the four downloads in File Explorer,
   click the address bar, type `powershell`, and press Enter. Run the following
   commands in that new window:

   ```powershell
   $appZip = Get-ChildItem -File "*-cuda128.zip"
   $assetZip = Get-ChildItem -File "*-assets-*.zip"
   Get-FileHash -Algorithm SHA256 -LiteralPath $appZip.FullName
   Get-Content -LiteralPath ($appZip.FullName + ".sha256")
   Get-FileHash -Algorithm SHA256 -LiteralPath $assetZip.FullName
   Get-Content -LiteralPath ($assetZip.FullName + ".sha256")
   ```

   Stop if PowerShell finds zero or multiple matches, the release notes omit
   the authoritative values, or any value differs.

5. Extract only the verified CUDA 12.8 Application Package ZIP:

   ```text
   towerscout-<release-version>-cuda128.zip
   ```

   Leave the Model & Data Package ZIP and both `.sha256` files beside the
   extracted folder. Do not extract the assets ZIP for the normal setup path.

6. Open the extracted application folder in File Explorer. It should contain
   `setup-towerscout.cmd`, `start.bat`, `compose.gpu.podman.yaml`,
   `scripts\`, `docs\`, and `assets\`.

7. In Windows File Explorer, click the address bar, type `powershell`, and
   press Enter.

8. Install the package-local Compose provider and confirm Podman. Then run the
   non-changing CDI check:

   ```powershell
   .\scripts\install-podman-compose-provider.cmd -Apply
   podman machine list
   podman compose version
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\enable-podman-gpu.ps1 -VerifyOnly
   ```

   If `-VerifyOnly` says CDI must be provisioned or refreshed, review its
   message and run the package helper without `-VerifyOnly` only when local
   policy permits it:

   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\enable-podman-gpu.ps1
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\enable-podman-gpu.ps1 -VerifyOnly
   ```

   Continue only when the final check shows `nvidia.com/gpu=all`. Record
   `nvidia-ctk --version` inside the Podman machine if support later asks for
   the sanitized version information.

9. In the PowerShell window, run:

   ```powershell
   .\setup-towerscout.cmd -Engine podman -Gpu on
   ```

10. Keep the PowerShell window open while Podman downloads and starts the CUDA
   image. The first image pull can take several minutes.

11. When TowerScout opens in the browser, use Setup Wizard or Settings to
    configure the provider key you prepared. One valid Google Maps or Azure Maps
    key is enough to start.

Setup verifies the package checksum sidecars, imports the Model & Data Package
into Podman named volumes, starts TowerScout, and opens:

```text
http://localhost:5000
```

For a valid Podman GPU launch, status output must show `selected_device=cuda`.
If it shows `cpu`, you are not running the GPU path.

## Podman GPU Runtime Notes

TowerScout uses `podman compose` plus the Podman GPU overlay
`compose.gpu.podman.yaml`. On Windows, `podman compose` delegates to an
external Compose provider. Keep these rules in mind:

- Use `-Engine podman -Gpu on` on every TowerScout setup/start command for this
  guide.
- Do not mix Docker and Podman for the same setup. They use separate named
  volumes, so provider setup and imported assets will not appear in the other
  engine.
- `PODMAN_COMPOSE_PROVIDER` must point to an approved non-Docker-Desktop
  provider.
- CDI must expose `nvidia.com/gpu=all` inside the Podman machine.
- If Podman reports a port bind conflict even though Windows shows the port as
  free, choose another unused port and use it consistently:

  ```powershell
  .\setup-towerscout.cmd -Engine podman -Gpu on -Port 5009
  .\scripts\status.cmd -Engine podman -Port 5009
  ```

## Stop, Restart, Status, And Logs

Run these commands from the extracted TowerScout application folder.

Stop TowerScout:

```powershell
.\scripts\stop.cmd -Engine podman
```

Start again:

```powershell
.\start.bat -Engine podman -Gpu on
```

Restart:

```powershell
.\scripts\stop.cmd -Engine podman
.\start.bat -Engine podman -Gpu on
```

Check status:

```powershell
.\scripts\status.cmd -Engine podman
```

Show recent logs for troubleshooting:

```powershell
.\scripts\logs.cmd -Engine podman -Tail 200
```

If you chose a non-default port, add the recorded `-Port` value to setup,
`start.bat`, status, TLS-repair, and asset-import commands and use that port in
the browser address. Preserve `-Gpu on` on setup, `start.bat`, TLS-repair, and
asset-import commands. Stop, status, and logs do not take a GPU flag;
`stop.cmd` and `logs.cmd` do not take a port.

## Troubleshooting

If setup says the CPU package does not support `-Gpu on`, you extracted the
wrong Application Package. Stop and use the `-cuda128` ZIP from the same
release as the Model & Data Package.

If setup says no approved Podman Compose provider was found, run the verified
package installer:

```powershell
.\scripts\install-podman-compose-provider.cmd -Apply
```

If setup says the Podman machine is not running:

```powershell
podman machine start
podman machine list
```

If CDI validation fails, stop and ask Local IT to inspect the Podman machine,
NVIDIA driver, WSL GPU visibility, NVIDIA Container Toolkit install, and CDI
registration. You may choose Docker or CPU instead after stopping this setup.

If GPU mode is on but readiness does not report `selected_device=cuda`, stop
validation. Common causes are an outdated NVIDIA driver, a non-WSL Podman
machine, stale CDI registration, a blocked NVIDIA Container Toolkit install, an
unapproved Compose provider, or using the CPU package by mistake.

If the browser does not open, leave PowerShell open and manually open:

```text
http://localhost:5000
```

If status is `degraded`, required assets may be missing or corrupt. Retry the
verified import command. The example below uses the default port. If your setup
record uses another port, substitute that recorded value:

```powershell
.\scripts\import-assets.cmd -Engine podman -Gpu on -Port 5000 -Source assets -VerifyHashes
```

If status is `fatal`, stop. Record the release version, package filename,
selected Compose provider, GPU/CDI result, status output, and a reviewed
summary of recent logs. Ask Local IT about local policy, network, driver, or
certificate problems. Report a non-sensitive product defect at
[TowerScout issue tracker](https://github.com/J-Schulein/TowerScout/issues).
That tracker is public and
does not promise a response. Never post provider secrets, `.env`, raw
screenshots, browser traces, exported datasets, certificate details, or
unreviewed raw logs.

### Provider TLS Inspection CA

Use this only when Google Maps or Azure Maps key validation fails even though
the key is correct and logs show `CERTIFICATE_VERIFY_FAILED`. This
usually means the container does not trust a local TLS inspection root or
intermediate certificate.

Use the repair command shown by TowerScout; it includes the active `-Port`.
If entering commands manually, use the same `-Port` on every repair and
`start.bat` command. The examples below use port 5000 explicitly; replace every
`-Port 5000` with the active port (for example, `-Port 5211`) when needed.

Run the guided dry run from the extracted TowerScout application folder:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine podman -Gpu on -Port 5000
```

Review the locally sensitive output with Local IT. Do not paste
certificate subjects, issuer details, or thumbprints into public issue comments
or public release evidence. If the helper identifies a safe CA candidate, it
prints the exact apply command. With Local IT approval, apply the repair and
restart TowerScout:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine podman -Gpu on -Port 5000 -Apply
.\scripts\stop.cmd -Engine podman
.\start.bat -Engine podman -Gpu on -Port 5000
```

If Local IT knows the correct Windows certificate thumbprint or has an
exported CA file, it can bypass automatic selection:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine podman -Gpu on -Port 5000 -Thumbprint <windows-certificate-thumbprint> -Apply
.\scripts\repair-provider-tls.cmd -Provider google -Engine podman -Gpu on -Port 5000 -CertificatePath C:\path\to\local-ca.pem -Apply
.\scripts\stop.cmd -Engine podman
.\start.bat -Engine podman -Gpu on -Port 5000
```

Do not paste the placeholder text. Replace it with the actual Local IT-provided
thumbprint or certificate path. The helper copies the CA chain into Podman's
persistent TowerScout config volume, builds a combined CA bundle, updates
`.env`, and verifies that selected provider TLS reaches the normal invalid-key
response instead of a certificate error.

Docker and Podman use separate TowerScout config volumes. If you previously
imported the CA for Docker, repeat the import for Podman.

If your site uses Azure Maps instead of Google Maps for validation, use
`-Provider azure`. If automatic discovery is ambiguous or unavailable, Local
IT may use the lower-level `scripts\import-tls-ca.cmd` command with a
known `-Thumbprint` or `-CertificatePath`.

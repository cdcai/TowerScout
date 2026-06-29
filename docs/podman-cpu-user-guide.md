# TowerScout Podman CPU User Guide

**Applies to**: Current V1 release-candidate package path through the RC7
provider TLS repair baseline, unless release notes say otherwise
**Last reviewed**: 2026-06-29
**Audience**: Windows users assigned the Podman CPU path
**Runtime scope**: Podman, CPU Application Package, CPU launch mode

Use this guide only when support tells you to run TowerScout with Podman. The
normal pilot path is Docker Desktop CPU. Podman requires a running Podman
machine and an approved non-Docker-Desktop Compose provider.

## Before You Start

Install or confirm these items before running TowerScout.

- Windows 11 on AMD64.
- Windows PowerShell. Use PowerShell from Windows, not a WSL or Ubuntu
  terminal.
- A modern browser such as Microsoft Edge or Google Chrome.
- Normal outbound internet access to GitHub Releases, GHCR, the approved
  Compose provider source if installation is needed, and the selected map
  provider.
- At least `15 GB` free disk space. `25 GB` is a better first-setup target.
- One approved Google Maps or Azure Maps provider key.
- Windows Subsystem for Linux 2.
  - Install guide:
    `https://learn.microsoft.com/en-us/windows/wsl/install#install-wsl-command`
  - Note: Admin rights and/or helpdesk support may be required to install this
    software. Check with your local IT support if you encounter problems
    installing this software.
- Podman or Podman Desktop.
  - Red Hat overview and download entry point:
    `https://www.redhat.com/en/topics/containers/what-is-podman-desktop`
  - Podman Desktop product/download page:
    `https://developers.redhat.com/products/podman-desktop`
  - Note: Podman Desktop is free and open source. A Red Hat account is not
    required for the TowerScout local package, but local IT policy still
    controls installation and support.
- An approved Podman Compose provider.
  - TowerScout rejects Docker Desktop's bundled `docker-compose.exe` for the
    Podman path.
  - If no approved provider is present, support can run the package helper
    shown below.

Podman must be installed, the Podman machine must be running, and the Compose
provider must be available before entering the `.\setup-towerscout.cmd`
command.

Useful checks from PowerShell:

```powershell
wsl --status
wsl --list --verbose
podman --version
podman machine list
podman compose version
```

If the Podman machine exists but is stopped, start it:

```powershell
podman machine start
```

If `podman compose version` reports no approved provider, run this from the
extracted TowerScout application folder only when support approves connected
provider installation:

```powershell
.\scripts\install-podman-compose-provider.cmd -Apply
```

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
   towerscout-<release-version>-cpu.zip
   towerscout-<release-version>-cpu.zip.sha256
   towerscout-<release-version>-assets-<asset-version>.zip
   towerscout-<release-version>-assets-<asset-version>.zip.sha256
   ```

   Do not use GitHub's automatic source-code ZIP or the green `Code` button.

4. Extract only the CPU Application Package ZIP:

   ```text
   towerscout-<release-version>-cpu.zip
   ```

   Leave the Model & Data Package ZIP and both `.sha256` files beside the
   extracted folder. Do not extract the assets ZIP for the normal setup path.

5. Open the extracted application folder in File Explorer. It should contain
   `setup-towerscout.cmd`, `start.bat`, `scripts\`, `docs\`, and `assets\`.

6. In Windows File Explorer, click the address bar, type `powershell`, and
   press Enter.

7. Confirm Podman is ready:

   ```powershell
   podman machine list
   podman compose version
   ```

8. In the PowerShell window, run:

   ```powershell
   .\setup-towerscout.cmd -Engine podman -Gpu off
   ```

9. Keep the PowerShell window open while Podman downloads and starts the
   TowerScout image. The first image pull can take several minutes.

10. When TowerScout opens in the browser, use Setup Wizard or Settings to
    configure one approved provider key. One valid Google Maps or Azure Maps
    key is enough to start.

Setup verifies the package checksum sidecars, imports the Model & Data Package
into Podman named volumes, starts TowerScout, and opens:

```text
http://localhost:5000
```

`setup_required` is normal before provider setup is complete. After assets and
one provider key are configured, status should become `ready`.

## Podman Runtime Notes

TowerScout uses `podman compose` for the Podman path. On Windows, that command
delegates to an external Compose provider. Keep these rules in mind:

- Use `-Engine podman` on every TowerScout helper command.
- Do not mix Docker and Podman for the same setup. They use separate named
  volumes, so provider setup and imported assets will not appear in the other
  engine.
- If `PODMAN_COMPOSE_PROVIDER` is set, it must point to an approved
  non-Docker-Desktop provider.
- If Podman reports a port bind conflict even though Windows shows the port as
  free, retry with a support-assigned port and use it consistently:

  ```powershell
  .\setup-towerscout.cmd -Engine podman -Gpu off -Port 5009
  .\scripts\status.cmd -Engine podman -Port 5009
  ```

## Stop, Restart, Status, And Logs

Run these commands from the extracted TowerScout application folder.

Stop TowerScout:

```powershell
.\scripts\stop.cmd -Engine podman
```

Start again after setup:

```powershell
.\start.bat -Engine podman -Gpu off
```

Restart:

```powershell
.\scripts\stop.cmd -Engine podman
.\start.bat -Engine podman -Gpu off
```

Check status:

```powershell
.\scripts\status.cmd -Engine podman
```

Show recent logs if support asks:

```powershell
.\scripts\logs.cmd -Engine podman -Tail 200
```

## Troubleshooting

If setup says no approved Podman Compose provider was found, run the provider
installer only when support approves:

```powershell
.\scripts\install-podman-compose-provider.cmd -Apply
```

If setup says the Podman machine is not running:

```powershell
podman machine start
podman machine list
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
.\scripts\import-assets.cmd -Engine podman -Source assets -VerifyHashes
```

If status is `fatal`, stop validation and send support the release version,
package filename, selected Compose provider, status output, and a reviewed
summary of recent logs. Do not send provider secrets, `.env`, raw screenshots,
browser network traces, exported datasets, or unreviewed raw logs unless your
site has an approved handling procedure.

### Provider TLS Inspection CA

Use this only when Google Maps or Azure Maps key validation fails even though
the key is correct and support sees `CERTIFICATE_VERIFY_FAILED` in container
logs. This
usually means the container does not trust a local TLS inspection root or
intermediate certificate.

Run the guided dry run from the extracted TowerScout application folder:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine podman -Gpu off
```

Review the local support-sensitive output with support. Do not paste
certificate subjects, issuer details, or thumbprints into public issue comments
or public release evidence. If the helper identifies a safe CA candidate, it
prints the exact apply command. With support approval, apply the repair and
restart TowerScout:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine podman -Gpu off -Apply
.\scripts\stop.cmd -Engine podman
.\start.bat -Engine podman -Gpu off
```

If support already knows the correct Windows certificate thumbprint or has an
exported CA file, they can bypass automatic selection:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine podman -Gpu off -Thumbprint <windows-certificate-thumbprint> -Apply
.\scripts\repair-provider-tls.cmd -Provider google -Engine podman -Gpu off -CertificatePath C:\path\to\local-ca.pem -Apply
.\scripts\stop.cmd -Engine podman
.\start.bat -Engine podman -Gpu off
```

Do not paste the placeholder text. Replace it with the actual support-provided
thumbprint or certificate path. The helper copies the CA chain into Podman's
persistent TowerScout config volume, builds a combined CA bundle, updates
`.env`, and verifies that selected provider TLS reaches the normal invalid-key
response instead of a certificate error.

Docker and Podman use separate TowerScout config volumes. If you previously
imported the CA for Docker, repeat the import for Podman.

If your site uses Azure Maps instead of Google Maps for validation, support may
use `-Provider azure`. If automatic discovery is ambiguous or unavailable,
support may still use the lower-level `scripts\import-tls-ca.cmd` command with a
known `-Thumbprint` or `-CertificatePath`.

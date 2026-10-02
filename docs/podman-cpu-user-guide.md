# TowerScout Podman CPU User Guide

**Applies to**: The exact documentation-aligned Windows release package named
by the authoritative release record
**Last reviewed**: 2026-10-02
**Audience**: Windows users who choose Podman Desktop with CPU processing
**Runtime scope**: Podman, CPU Application Package, CPU launch mode

Use this guide when you choose Podman without GPU acceleration. Podman requires
a running rootless WSL 2 machine, 64-bit Python 3.12, and the package-local
Compose provider.

**Unsigned package boundary**: TowerScout's PowerShell scripts are unsigned.
Use the supplied `.cmd`/`.bat` wrappers only where you and your organization
permit them. They use a process-scoped execution-policy setting and do not
change persistent machine policy. Do not disable endpoint protection or weaken
machine-wide policy; signature-enforcing or organization-allowlisted endpoints
require site-administrator approval.

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
- One user- or organization-owned Google Maps or Azure Maps provider key.
- Windows Subsystem for Linux 2.
  - Install guide:
    `https://learn.microsoft.com/en-us/windows/wsl/install#install-wsl-command`
  - Note: Admin rights and/or helpdesk support may be required to install this
    software. Check with your local IT support if you encounter problems
    installing this software.
- Podman Desktop.
  - Installation guide:
    `https://podman-desktop.io/docs/installation/windows-install`
  - Note: Podman Desktop is free and open source. A Red Hat account is not
    required for the TowerScout local package, but local IT policy still
    controls installation and support.
- 64-bit Python 3.12 from `https://www.python.org/downloads/windows/`. It is
  used to install TowerScout's pinned package-local Compose provider.

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

If no Podman machine exists, create and start the default rootless machine:

```powershell
podman machine init --now podman-machine-default
```

Do not run `machine init` if the machine already exists. After extracting the
TowerScout Application Package, install its verified Compose provider:

```powershell
.\scripts\install-podman-compose-provider.cmd -Apply
```

## Install TowerScout

1. Create a new working folder, for example:

   ```text
   C:\Users\<you>\Documents\TowerScout
   ```

2. Open the TowerScout GitHub Releases page and select the entry whose notes
   identify it as the current supported final Windows release:

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

4. Before extracting anything, calculate the SHA-256 of both ZIPs and compare
   each result with both its downloaded `.sha256` file and the authoritative
   value printed in the final release notes:

   ```powershell
   $appZip = Get-ChildItem -File "*-cpu.zip"
   $assetZip = Get-ChildItem -File "*-assets-*.zip"
   Get-FileHash -Algorithm SHA256 -LiteralPath $appZip.FullName
   Get-Content -LiteralPath ($appZip.FullName + ".sha256")
   Get-FileHash -Algorithm SHA256 -LiteralPath $assetZip.FullName
   Get-Content -LiteralPath ($assetZip.FullName + ".sha256")
   ```

   Stop if PowerShell finds zero or multiple matches, the release notes omit
   the authoritative values, or any value differs.

5. Extract only the verified CPU Application Package ZIP:

   ```text
   towerscout-<release-version>-cpu.zip
   ```

   Leave the Model & Data Package ZIP and both `.sha256` files beside the
   extracted folder. Do not extract the assets ZIP for the normal setup path.

6. Open the extracted application folder in File Explorer. It should contain
   `setup-towerscout.cmd`, `start.bat`, `scripts\`, `docs\`, and `assets\`.

7. In Windows File Explorer, click the address bar, type `powershell`, and
   press Enter.

8. Install and confirm the package-local Compose provider, then confirm Podman
   is ready:

   ```powershell
   .\scripts\install-podman-compose-provider.cmd -Apply
   podman machine list
   podman compose version
   ```

9. In the PowerShell window, run:

   ```powershell
   .\setup-towerscout.cmd -Engine podman -Gpu off
   ```

10. Keep the PowerShell window open while Podman downloads and starts the
   TowerScout image. The first image pull can take several minutes.

11. When TowerScout opens in the browser, use Setup Wizard or Settings to
    configure the provider key you prepared. One valid Google Maps or Azure Maps
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
  free, choose another unused port and use it consistently:

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

Show recent logs for troubleshooting:

```powershell
.\scripts\logs.cmd -Engine podman -Tail 200
```

If you chose a non-default port, add the recorded `-Port` value to setup,
`start.bat`, status, and TLS-repair commands and use that port in the browser
address. `stop.cmd` and `logs.cmd` do not take a port.

## Troubleshooting

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

If the browser does not open, leave PowerShell open and manually open:

```text
http://localhost:5000
```

If setup reports multiple asset ZIPs, move old TowerScout ZIPs out of the
working folder and rerun setup.

If status is `degraded`, required assets may be missing or corrupt. Retry the
verified import command:

```powershell
.\scripts\import-assets.cmd -Engine podman -Source assets -VerifyHashes
```

If status is `fatal`, stop. Record the release version, package filename,
selected Compose provider, status output, and a reviewed summary of recent
logs. Ask Local IT about local policy, network, or certificate problems.
Report a non-sensitive product defect at
`https://github.com/J-Schulein/TowerScout/issues`. That tracker is public and
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
.\scripts\repair-provider-tls.cmd -Provider google -Engine podman -Gpu off -Port 5000
```

Review the locally sensitive output with Local IT. Do not paste
certificate subjects, issuer details, or thumbprints into public issue comments
or public release evidence. If the helper identifies a safe CA candidate, it
prints the exact apply command. With Local IT approval, apply the repair and
restart TowerScout:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine podman -Gpu off -Port 5000 -Apply
.\scripts\stop.cmd -Engine podman
.\start.bat -Engine podman -Gpu off -Port 5000
```

If Local IT knows the correct Windows certificate thumbprint or has an
exported CA file, it can bypass automatic selection:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine podman -Gpu off -Port 5000 -Thumbprint <windows-certificate-thumbprint> -Apply
.\scripts\repair-provider-tls.cmd -Provider google -Engine podman -Gpu off -Port 5000 -CertificatePath C:\path\to\local-ca.pem -Apply
.\scripts\stop.cmd -Engine podman
.\start.bat -Engine podman -Gpu off -Port 5000
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

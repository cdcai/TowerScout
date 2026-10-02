# TowerScout Docker CPU User Guide

**Applies to**: The exact documentation-aligned Windows release package named
by the authoritative release record
**Last reviewed**: 2026-10-02
**Audience**: Windows users who choose Docker Desktop with CPU processing
**Runtime scope**: Docker Desktop, CPU Application Package, CPU launch mode

Use this guide when you choose Docker Desktop without GPU acceleration. CPU is
the simplest option and does not require an NVIDIA GPU.

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
- Normal outbound internet access to GitHub Releases, GHCR, and the selected
  map provider.
- At least `15 GB` free disk space. `25 GB` is a better first-setup target.
- One user- or organization-owned Google Maps or Azure Maps provider key.
- Windows Subsystem for Linux 2.
  - Install guide:
    `https://learn.microsoft.com/en-us/windows/wsl/install#install-wsl-command`
  - Note: Admin rights and/or helpdesk support may be required to install this
    software. Check with your local IT support if you encounter problems
    installing this software.
- Docker Desktop.
  - Installation guide:
    `https://docs.docker.com/desktop/setup/install/windows-install/`
  - Note: Docker Desktop is free to download. A Docker account is not required
    to run the TowerScout local package, but local license, procurement, and
    endpoint-management rules still apply.

Docker Desktop must be installed, open, and running before entering the
`.\setup-towerscout.cmd` command.

Useful checks from PowerShell:

```powershell
wsl --status
wsl --list --verbose
docker --version
docker compose version
```

Expected result: WSL is installed, any listed Linux distribution uses version
`2`, Docker Desktop is running, and both Docker commands print version
information.

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

8. In the PowerShell window, run:

   ```powershell
   .\setup-towerscout.cmd -Engine docker -Gpu off
   ```

9. Keep the PowerShell window open while Docker Desktop downloads and starts
   the TowerScout image. The first image pull can take several minutes.

10. When TowerScout opens in the browser, use Setup Wizard or Settings to
   configure the provider key you prepared. One valid Google Maps or Azure Maps key
   is enough to start.

Setup verifies the package checksum sidecars, imports the Model & Data Package
into Docker named volumes, starts TowerScout, and opens:

```text
http://localhost:5000
```

`setup_required` is normal before provider setup is complete. After assets and
one provider key are configured, status should become `ready`.

## Stop, Restart, Status, And Logs

Run these commands from the extracted TowerScout application folder.

Stop TowerScout:

```powershell
.\scripts\stop.cmd -Engine docker
```

Start again after setup:

```powershell
.\start.bat -Engine docker -Gpu off
```

Restart:

```powershell
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu off
```

Check status:

```powershell
.\scripts\status.cmd -Engine docker
```

Show recent logs for troubleshooting:

```powershell
.\scripts\logs.cmd -Engine docker -Tail 200
```

Use the same `-Engine docker` value on setup, start, stop, status, logs, asset
import, and TLS commands. Docker and Podman use separate storage.

If you chose a non-default port, add the recorded `-Port` value to setup,
`start.bat`, status, and TLS-repair commands and use that port in the browser
address. `stop.cmd` and `logs.cmd` do not take a port.

## Troubleshooting

If setup cannot find Docker, open Docker Desktop from the Windows Start menu and
wait until it says the engine is running. Then rerun:

```powershell
docker --version
docker compose version
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
.\scripts\import-assets.cmd -Engine docker -Source assets -VerifyHashes -RestartWaitSeconds 180
```

If status is `fatal`, stop. Record the release version, package filename,
`IMAGE.txt`, status output, and a reviewed summary of recent logs. Ask Local IT
about local policy, network, or certificate problems. For a non-sensitive
TowerScout defect, open `https://github.com/J-Schulein/TowerScout/issues`.
That public issue tracker is not a private or guaranteed-response support
service. Never post provider secrets, `.env`, raw screenshots, browser network
traces, exported datasets, certificate details, or unreviewed raw logs.

### Provider TLS Inspection CA

Use this only when Google Maps or Azure Maps key validation fails even though
the key is correct and the logs show `CERTIFICATE_VERIFY_FAILED`. This
usually means the container does not trust a local TLS inspection root or
intermediate certificate.

Use the repair command shown by TowerScout; it includes the active `-Port`.
If entering commands manually, use the same `-Port` on every repair and
`start.bat` command. The examples below use port 5000 explicitly; replace every
`-Port 5000` with the active port (for example, `-Port 5211`) when needed.

Run the guided dry run from the extracted TowerScout application folder:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off -Port 5000
```

Review the locally sensitive output with Local IT. Do not paste
certificate subjects, issuer details, or thumbprints into public issue comments
or public release evidence. If the helper identifies a safe CA candidate, it
prints the exact apply command. With Local IT approval, apply the repair and
restart TowerScout:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off -Port 5000 -Apply
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu off -Port 5000
```

If Local IT knows the correct Windows certificate thumbprint or has an
exported CA file, it can bypass automatic selection:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off -Port 5000 -Thumbprint <windows-certificate-thumbprint> -Apply
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off -Port 5000 -CertificatePath C:\path\to\local-ca.pem -Apply
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu off -Port 5000
```

Do not paste the placeholder text. Replace it with the actual Local IT-provided
thumbprint or certificate path. The helper copies the CA chain into Docker's
persistent TowerScout config volume, builds a combined CA bundle, updates
`.env`, and verifies that selected provider TLS reaches the normal invalid-key
response instead of a certificate error.

If your site uses Azure Maps instead of Google Maps for validation, use
`-Provider azure`. If automatic discovery is ambiguous or unavailable, Local
IT may use the lower-level `scripts\import-tls-ca.cmd` command with a
known `-Thumbprint` or `-CertificatePath`.

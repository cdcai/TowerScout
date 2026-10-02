# TowerScout Quick Start

**Applies to**: The next documentation-aligned Windows release identified by
the authoritative GitHub release record.

**Last reviewed**: 2026-10-02.

**Audience**: People using TowerScout for the first time, including people who
have not previously used PowerShell, Docker, Podman, GitHub Releases, container
images, API keys, or SHA-256 checks.

**Release state**: Draft. Final filenames, hashes, tested combinations, and
known limitations must be inserted in the release record before publication.
That authoritative release record controls which package is supported.

TowerScout is a local Windows application that helps a person review aerial or
satellite images for possible cooling towers. Its results require human review.

## The Three Independent Choices

You choose each item independently. These options are not assigned by project
support.

1. **Docker Desktop or Podman Desktop** runs TowerScout in a Linux container.
2. **CPU or a compatible NVIDIA GPU** processes the images. CPU is simpler;
   GPU can be faster when the exact hardware and engine path are supported.
3. **Google Maps or Azure Maps** supplies the map and imagery. You need a
   usable credential for only one provider.

If you are unsure, start with Docker CPU and the provider account you can
properly own and secure. You may instead choose any other supported combination
when its requirements are met.

## Before You Start

### Check The Computer

1. Open **Settings > System > About**.
2. Confirm the computer runs Windows 11 and says **64-bit operating system,
   x64-based processor**. ARM64, macOS, and Windows Server are not supported by
   this package.
3. Record **Installed RAM** and compare it with the final release's tested
   minimum.
4. Open File Explorer, select **This PC**, and check free disk space. Plan at
   least 15 GB for the CPU package or 35 GB for the CUDA package, plus room for
   your exports. The final release note controls if it requires more.
5. Open ordinary Windows PowerShell and run:

   ```powershell
   wsl --status
   ```

   If WSL is missing, follow Microsoft's
   [WSL installation guide](https://learn.microsoft.com/windows/wsl/install).
   Enabling Windows features or restarting may require administrator or Local
   IT approval.

### Choose And Prepare One Engine

You do not need both.

#### Docker Desktop

Follow Docker's current
[Windows installation instructions](https://docs.docker.com/desktop/setup/install/windows-install/).
Confirm your organization's Docker Desktop licensing and installation policy.
Use the supported WSL 2 Linux-container backend, start Docker Desktop, and wait
until it reports that it is running.

```powershell
docker --version
docker compose version
```

Both commands must print version information.

#### Podman Desktop

Follow Podman Desktop's current
[Windows installation instructions](https://podman-desktop.io/docs/installation/windows-install).
During onboarding, install Podman and create the default WSL 2 machine. In
Podman Desktop this is under **Settings > Resources**.

If Podman is installed but no machine exists, ordinary PowerShell can create
and start the rootless default machine:

```powershell
podman machine init --now podman-machine-default
```

Do not run that command if the machine already exists. Check it with:

```powershell
podman --version
podman machine list
podman system connection list
```

The tested TowerScout path also needs 64-bit Python 3.12 to install its pinned
package-local Compose provider. Install Python 3.12 from the official
[Python Windows downloads](https://www.python.org/downloads/windows/) if your
organization permits it, then confirm:

```powershell
python --version
```

The package-local Compose provider is installed after the TowerScout
Application Package is downloaded, verified, and extracted.

### Optional NVIDIA GPU

You may use CPU even if the computer has a GPU. For GPU processing:

1. open Task Manager or Device Manager and record the exact NVIDIA GPU;
2. run `nvidia-smi` in ordinary PowerShell;
3. confirm the exact GPU, Windows driver, WSL, and engine combination appears
   in the final release's tested-support list; and
4. use the `-cuda128` Application Package.

The CUDA 12.8 package expects Volta-or-newer NVIDIA hardware, but only listed
combinations are qualified. Maxwell and Pascal must use the CPU package. Use a
current Windows NVIDIA/OEM driver. NVIDIA states that the Windows driver
supplies CUDA to WSL; never install a Linux NVIDIA display driver inside WSL.

Podman GPU additionally requires NVIDIA Container Toolkit/CDI inside the
intended rootless machine. Follow the version-matched
[Podman GPU guide](podman-gpu-user-guide.md) before setup.

### Prepare One Map Provider Credential

You need one Google Maps API key or one Azure Maps subscription key. Provider
accounts, billing, charges, quotas, and usage rights are separate from
TowerScout.

TowerScout currently uses one credential per provider for both browser and
application requests. Do not create separate browser/server keys for
TowerScout; there is only one field for each provider, and the browser can see
that key. Use a dedicated limited project/account, API restrictions, quotas,
alerts, monitoring, and a rotation plan. If your organization requires a
browser-secret credential, split credentials, or Microsoft Entra ID, this
release does not meet that requirement.

Choose one of these paths.

#### Google Maps

1. Sign in to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project owned by you or your organization and attach an
   approved billing account. Review current pricing and set budget alerts.
3. Enable **Maps JavaScript API**, **Maps Static API**, **Geocoding API**, and
   the **Places API** used by the Maps JavaScript Places library.
4. Open **Google Maps Platform > Credentials**, select **Create credentials >
   API key**, and give the key a TowerScout-specific name.
5. Apply API restrictions for only those APIs. The current one-key design makes
   browser-referrer and server-side restrictions difficult to combine, so use
   only an application restriction your organization has verified works for
   both paths.
6. Set quotas, alerts, monitoring, and a rotation plan. Temporarily keep the key
   somewhere private until you enter it in TowerScout.

Google's official references are its
[getting-started guide](https://developers.google.com/maps/get-started),
[key-creation guide](https://developers.google.com/maps/documentation/javascript/get-api-key),
and [API-key security guidance](https://developers.google.com/maps/api-security-best-practices).

#### Azure Maps

1. Sign in to the [Azure portal](https://portal.azure.com/).
2. Use a subscription and resource group owned by you or your organization.
   Review current pricing and approval requirements.
3. Search for **Azure Maps**, select **Create**, create an Azure Maps account,
   and accept its terms. Use the current Gen2 pricing tier unless your
   organization directs otherwise.
4. Open the Azure Maps account and then **Settings > Authentication**.
5. Copy the **Primary Key** to a temporary private location. Keep the Secondary
   Key available for controlled rotation.
6. Configure the budgets, alerts, monitoring, and rotation required by your
   organization.

TowerScout uses Azure Maps Web SDK, imagery/tile, search, and geocoding
requests. It currently supports the shared subscription-key method, not
Microsoft Entra ID. See Microsoft's official
[account-and-key walkthrough](https://learn.microsoft.com/azure/azure-maps/quick-demo-map-app)
and [authentication guidance](https://learn.microsoft.com/azure/azure-maps/authentication-best-practices).

## Unsigned Windows Package

TowerScout's packaged PowerShell scripts are intentionally unsigned. Use the
supplied `.cmd` and `.bat` entrypoints. They start Windows PowerShell 5.1 with
a temporary, process-scoped execution-policy setting and do not change the
computer's permanent policy.

The standard package does not support an endpoint that requires a trusted
Authenticode publisher, WDAC/AppLocker approval, constrained-language
approval, antivirus/EDR exceptions, or organization-specific allowlisting.
If Windows or organizational policy blocks the package, stop and ask Local IT
whether it is allowed. Do not change persistent execution policy, select **Run
anyway** for an unverified file, disable endpoint protection, or disable TLS
verification.

## Step 1: Create A Download Folder

1. Open **File Explorer**.
2. Open **Documents**.
3. Create a folder named `TowerScout`.
4. Open it. The address bar should end in `Documents\TowerScout`.

Do not run commands from inside a ZIP preview. You will first use PowerShell in
this download folder and later open it in the extracted application folder.

## Step 2: Download The Four Files

Open the
[TowerScout GitHub Releases page](https://github.com/J-Schulein/TowerScout/releases).
Select the entry whose notes identify it as the current supported final Windows
release. If none does, stop. A draft, prerelease, source archive, branch, or
numerically newer tag is not automatically supported.

GitHub labels its download list **Assets**. From that list, download exactly:

1. one Application Package ZIP:
   - choose the filename ending in `-cpu.zip` for CPU; or
   - choose the filename ending in `-cuda128.zip` for NVIDIA GPU;
2. the matching Application Package `.zip.sha256` file;
3. the shared Model & Data Package ZIP whose name contains `-assets-`; and
4. the matching Model & Data `.zip.sha256` file.

Move all four files from Downloads into `Documents\TowerScout`.

The terms are easy to confuse:

- **GitHub Assets** is the list of downloadable release files.
- **Application Package** is the smaller CPU or CUDA control ZIP containing
  scripts, docs, Compose files, and release metadata.
- **Model & Data Package** is the larger shared ZIP containing model weights,
  ZIP-code data, and an asset manifest.
- **Container image** is the application runtime that Docker or Podman
  downloads from GHCR during setup. You do not download it manually.
- **Local `assets` folder** appears inside the extracted Application Package.
- **`dataset.zip`** is output you may export later; it is not an installer.

Do not use GitHub's green **Code** button or its automatic **Source code
(zip)** / **Source code (tar.gz)** files for package installation.

## Step 3: Verify Both ZIPs Before Extraction

SHA-256 is a long check value for a file. Each ZIP must have the same value in
three places:

1. the value printed in the public final release notes;
2. the value in the downloaded `.sha256` text file; and
3. the value calculated on this computer.

Open `Documents\TowerScout` in File Explorer. Click the address bar, type
`powershell`, and press Enter. This opens a normal PowerShell window in the
correct folder. Paste one complete block and press Enter.

CPU Application Package:

```powershell
$appZip = Get-ChildItem -File "*-cpu.zip"
$assetZip = Get-ChildItem -File "*-assets-*.zip"
Get-FileHash -Algorithm SHA256 -LiteralPath $appZip.FullName
Get-Content -LiteralPath ($appZip.FullName + ".sha256")
Get-FileHash -Algorithm SHA256 -LiteralPath $assetZip.FullName
Get-Content -LiteralPath ($assetZip.FullName + ".sha256")
```

NVIDIA GPU Application Package: use the same block but replace its first line
with:

```powershell
$appZip = Get-ChildItem -File "*-cuda128.zip"
```

Expected result: two calculated hash values and two sidecar lines appear.
Compare all 64 characters for each ZIP with the matching value displayed on
the final release page. Letter case does not matter; every character does.

Stop if:

- PowerShell finds no matching ZIP or more than one matching ZIP;
- the release page does not display the two authoritative values;
- a sidecar names a different file; or
- any value differs.

Do not extract, unblock, or run a failed or unverifiable download. Download
that file again from the same final release and repeat the comparison.

Only after both ZIPs pass, you may right-click the Application Package ZIP,
open **Properties**, and select **Unblock** if Windows shows that checkbox.

## Step 4: Extract The Application Package

In File Explorer, right-click only the verified `-cpu.zip` or
`-cuda128.zip`, select **Extract All**, and extract it inside the
`Documents\TowerScout` folder.

Do not extract the Model & Data Package ZIP. Leave it and both `.sha256` files
beside the new extracted folder.

Open the extracted folder. It should contain:

```text
setup-towerscout.cmd
start.bat
scripts\
docs\
assets\
compose.yaml
```

The `assets` folder starts empty. Do not put the Model & Data ZIP inside it;
setup finds the ZIP in the parent download folder.

## Step 5: Finish Podman Preparation, If Chosen

Skip this section for Docker.

With the rootless `podman-machine-default` running and Python 3.12 available,
open PowerShell in the extracted Application Package folder and run:

```powershell
.\scripts\install-podman-compose-provider.cmd -Apply
podman compose version
```

The helper downloads a pinned provider, verifies its SHA-256, and installs it
under the extracted package. Ready means the version command succeeds using
that approved provider. TowerScout rejects Docker Desktop's Compose executable
for Podman.

For Podman GPU, now follow the CDI preparation and `-VerifyOnly` procedure in
[Podman GPU User Guide](podman-gpu-user-guide.md).

## Step 6: Run One Setup Command

Open the extracted Application Package folder in File Explorer. Click the
address bar, type `powershell`, and press Enter. A prompt ending in the package
folder means you are in the right place. `.\` means "run this file from the
current folder."

Make sure Docker Desktop is running or the intended Podman machine is running.
Copy only one command:

### Docker CPU

```powershell
.\setup-towerscout.cmd -Engine docker -Gpu off
```

### Docker NVIDIA GPU

```powershell
.\setup-towerscout.cmd -Engine docker -Gpu on
```

### Podman CPU

```powershell
.\setup-towerscout.cmd -Engine podman -Gpu off
```

### Podman NVIDIA GPU

```powershell
.\setup-towerscout.cmd -Engine podman -Gpu on
```

Keep PowerShell open. Setup checks the engine, disk, port, package metadata,
checksums, and Model & Data ZIP; imports hash-verified assets; downloads the
digest-pinned container image; starts TowerScout; and normally opens
`http://localhost:5000`.

The first image pull can take several minutes. Do not close the window while
it is working.

Expected milestones include:

```text
TowerScout setup
Engine: docker or podman
GPU: off or on
Model & Data Package checksum matched
Asset import completed with hash verification
TowerScout responded at http://localhost:5000
readiness: setup_required
```

`setup_required` is normal before a provider credential is saved.

If setup cannot uniquely find the two ZIPs because they are stored elsewhere,
use the complete quoted paths copied from File Explorer. Replace the example
text with the actual paths; do not type square brackets literally:

```powershell
.\setup-towerscout.cmd `
  -Engine docker `
  -Gpu off `
  -PackageZip "[full path copied from the Application Package ZIP]" `
  -AssetZip "[full path copied from the Model & Data Package ZIP]"
```

The backtick at the end of a line tells PowerShell that the command continues
on the next line. Copy the entire block. Keep paths in double quotes because
Windows folder names can contain spaces.

## Step 7: Configure One Provider

When TowerScout opens, Setup Wizard shows Google and Azure credential fields.

1. Paste only the credential for the provider you prepared.
2. Select **Validate** for that provider.
3. Select it as the default map provider.
4. Save setup.

One valid provider is enough. Do not show the key in a screenshot, issue,
email, chat, log excerpt, or browser trace.

Readiness should change to `ready` after a valid provider and required assets
are present. You can check from PowerShell:

```powershell
.\scripts\status.cmd -Engine docker -Port 5000
```

Use `podman` instead of `docker` if that is your engine. `degraded` means a
recoverable capability is missing; follow its message. `fatal` means stop and
use the troubleshooting guide.

## Step 8: Try A Small First Search

1. Search for a familiar public, non-sensitive place or move the map there.
2. To draw a circle, enter a small radius, choose **Circle**, and click the
   map. To draw a polygon, choose **Custom shape**, click each corner, and
   complete the shape using the visible map control.
3. Select **Estimate tiles**. Start with only a few tiles.
4. Select **Find towers** and wait for the progress display to finish.
5. Review the map and detection list. A zero-detection result can be valid and
   does not by itself mean installation failed.
6. Export important results before closing or stopping.

A successful first run means readiness is `ready`, the chosen map loads, the
small request reaches a completed state without an error, and the review panel
updates. Maintainer fixtures, expected detection counts, and formal PASS/FAIL
rules are not end-user setup requirements.

## Step 9: Save Your Setup Record

Do not record a provider key.

| Item | Your value |
| --- | --- |
| Application folder |  |
| Engine | Docker / Podman |
| Processing | CPU / NVIDIA GPU |
| Provider | Google / Azure |
| Port | 5000 unless changed |
| Browser address | `http://localhost:5000` unless changed |

## Step 10: Stop And Reopen

Use the same engine you recorded.

### Docker CPU

```powershell
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu off
```

### Docker NVIDIA GPU

```powershell
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu on
```

### Podman CPU

```powershell
.\scripts\stop.cmd -Engine podman
podman machine start podman-machine-default
.\start.bat -Engine podman -Gpu off
```

### Podman NVIDIA GPU

```powershell
.\scripts\stop.cmd -Engine podman
podman machine start podman-machine-default
.\start.bat -Engine podman -Gpu on
```

`stop.cmd` does not accept a port. If you intentionally used port 5001, add
`-Port 5001` to setup, start, and status, and open
`http://localhost:5001`.

Normal stop/start and reboot preserve the selected engine's TowerScout named
volumes: provider configuration, imported assets, sessions, temporary review
data, uploads, cache, and logs. Docker and Podman use separate stores. An
engine switch does not migrate them. The Podman machine may require a manual
start after reboot.

Internal session storage is not a backup. Export important CSV, KML, or
dataset ZIP files to an approved folder before stopping. Do not use `down -v`,
volume prune, Podman machine reset, or blanket cleanup as routine recovery.

## Troubleshooting And Help

Start with the same engine and port from your setup record:

```powershell
.\scripts\status.cmd -Engine docker -Port 5000
.\scripts\logs.cmd -Engine docker -Tail 200
```

For Podman, replace `docker` with `podman`. Review logs locally. Do not post raw
logs.

Common safe actions:

- **Command not recognized:** reopen PowerShell from the extracted folder.
- **Engine unavailable:** start Docker Desktop or the intended Podman machine.
- **Browser unavailable:** confirm the recorded port and status.
- **Provider invalid/unauthorized:** review billing, enabled APIs, and API
  restrictions without sharing the key.
- **TLS/certificate error:** ask Local IT to follow the separate dry-run and
  approved apply procedure in the
  [Local IT Administrator Guide](local-it-administrator-guide.md). Do not
  disable TLS verification.
- **GPU does not report CUDA:** correct the package/driver/engine/CDI
  prerequisite or use CPU; do not count fallback as GPU success.

For Windows policy, software installation, proxy, TLS, or managed-device
issues, contact Local IT. For a reproducible non-sensitive TowerScout defect,
use the public
[TowerScout issue tracker](https://github.com/J-Schulein/TowerScout/issues).
It is not a private or guaranteed-response help desk.

Include only release/package name, selected engine/mode/port, versions,
sanitized readiness, failed step, and a non-secret error category. Never post
provider keys, `.env`, raw logs/screenshots, browser traces, private AOIs,
provider responses, certificate details, uploaded files, exports, or named-
volume contents.

## More Information

- [Project Overview](project-overview.md)
- [User Guide](user-guide.md)
- [Package And Advanced Troubleshooting Guide](package-guide.md)
- [Local IT Administrator Guide](local-it-administrator-guide.md)
- [Docker CPU Guide](docker-cpu-user-guide.md)
- [Docker GPU Guide](docker-gpu-user-guide.md)
- [Podman CPU Guide](podman-cpu-user-guide.md)
- [Podman GPU Guide](podman-gpu-user-guide.md)

The running application exposes version-matched formatted notices at
`/license` and plain-text notices at `/license.txt` on its local address.

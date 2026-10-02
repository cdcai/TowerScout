# Install And First Run

> **Audience:** New Windows users. **Applies to:** The next final Windows
> release. **Last reviewed:** 2026-10-02. **Publication state:** Local draft;
> final filenames and hashes will appear in the authoritative release record.

This page keeps the first-use path continuous: prepare, download, verify,
extract, start, configure one provider, try a small search, and stop safely.

## 1. Prepare A Working Folder

1. Open **File Explorer**.
2. Open **Documents**.
3. Create a folder named `TowerScout`.
4. Open that folder. Do not work inside a ZIP preview window.

The File Explorer address bar shows the folder you are in. You will first use
PowerShell in this download folder. After extraction, you will open PowerShell
again in the new application folder.

## 2. Download Four Files

Open the [TowerScout Releases page](https://github.com/J-Schulein/TowerScout/releases)
and select the release whose notes identify it as the current supported final
Windows release. If no release says that, stop; a draft, prerelease, source
archive, or numerically newer tag is not automatically the supported release.

In GitHub's **Assets** list, download exactly four files:

1. one Application Package ZIP: choose `-cpu.zip` or `-cuda128.zip`;
2. the matching Application Package `.zip.sha256` text file;
3. the shared Model & Data Package ZIP containing `-assets-`; and
4. its matching `.zip.sha256` text file.

GitHub's word **Assets** means its download list. The Model & Data Package is a
specific ZIP in that list. The local `assets` folder appears only after you
extract the Application Package. The container image is downloaded later by
Docker or Podman. A `dataset.zip` created by TowerScout is your export, not an
installation file.

Move the four downloads into the `Documents\TowerScout` folder. Do not use the
green **Code** button or GitHub's automatic **Source code** archives.

## 3. Verify Both ZIPs Before Extraction

SHA-256 is a file's check value. Each ZIP must have the same value in three
places: the public release notes, its `.sha256` text file, and the value your
computer calculates.

In File Explorer, open `Documents\TowerScout`, click the address bar, type
`powershell`, and press **Enter**. A normal, non-administrator PowerShell
window opens in that folder. Paste the block for your package and press Enter.

For the CPU package:

```powershell
$appZip = Get-ChildItem -File "*-cpu.zip"
$assetZip = Get-ChildItem -File "*-assets-*.zip"
Get-FileHash -Algorithm SHA256 -LiteralPath $appZip.FullName
Get-Content -LiteralPath ($appZip.FullName + ".sha256")
Get-FileHash -Algorithm SHA256 -LiteralPath $assetZip.FullName
Get-Content -LiteralPath ($assetZip.FullName + ".sha256")
```

For the NVIDIA GPU package, change only the first line to:

```powershell
$appZip = Get-ChildItem -File "*-cuda128.zip"
```

Compare every displayed hash character-for-character with the matching value
shown on the release page. Stop if a value is missing, more than one ZIP
matches, or any value differs. Do not extract, unblock, or run that file.

After all three values match for both ZIPs, you may use **Properties > Unblock**
on the Application Package ZIP if Windows shows that checkbox. Do not use
**Run anyway** on an unverified download or disable endpoint protection.

## 4. Extract The Application Package

In File Explorer, right-click only the verified `-cpu.zip` or
`-cuda128.zip`, select **Extract All**, and extract it inside
`Documents\TowerScout`. Do not extract the Model & Data ZIP.

Open the new extracted folder. You should see `setup-towerscout.cmd`,
`start.bat`, `scripts`, `docs`, Compose files, and an empty `assets` folder.
The four downloaded files remain one folder above it.

## 5. Run Setup For Your Choice

Make sure Docker Desktop is running, or your Podman machine and package-local
Compose provider are ready. In the extracted folder, click the File Explorer
address bar, type `powershell`, and press **Enter**. Commands beginning with
`.\` mean "run this file from the folder I am currently in."

Paste exactly one setup command:

```powershell
# Docker CPU
.\setup-towerscout.cmd -Engine docker -Gpu off

# Docker NVIDIA GPU
.\setup-towerscout.cmd -Engine docker -Gpu on

# Podman CPU
.\setup-towerscout.cmd -Engine podman -Gpu off

# Podman NVIDIA GPU, after the CDI check passes
.\setup-towerscout.cmd -Engine podman -Gpu on
```

The lines beginning with `#` are labels, not commands. Copy only the command
under your choice. Keep the window open. Setup verifies package information,
imports the Model & Data ZIP, downloads the digest-pinned container image,
starts TowerScout, and normally opens `http://localhost:5000`.

The first image download can take several minutes. `setup_required` is normal
until you save a valid map-provider credential. `ready` means provider setup
and required model/data assets are available. `fatal` means stop and use the
troubleshooting page.

## 6. Configure One Map Provider

In the Setup Wizard:

1. paste the Google or Azure credential you prepared;
2. validate it;
3. select that provider as the default; and
4. save setup.

Do not include the key in a screenshot or support message. If validation
reports a certificate or TLS problem, use Local IT guidance rather than
turning off certificate checking.

## 7. Try A Small Search

1. Search for a familiar, public, non-sensitive place or move the map there.
2. Choose **Circle**, enter a small radius, and place the circle; or choose
   **Custom shape** and click points to draw a small polygon.
3. Select **Estimate tiles**. Start with an area that estimates only a few
   tiles.
4. Select **Find towers** and wait for the progress display to finish.
5. Review the map and detection list. Zero detections can be a valid result; it
   does not by itself mean installation failed.
6. If the result matters, export it before closing the browser or stopping the
   application.

A successful first use means TowerScout reaches `ready`, the map loads, the
small detection request finishes without an error, and the review area updates.
Formal release fixtures, expected counts, and PASS/FAIL rules are maintainer
qualification work, not an end-user prerequisite.

## 8. Stop And Reopen

From PowerShell in the extracted application folder, stop with the engine you
chose:

```powershell
.\scripts\stop.cmd -Engine docker
.\scripts\stop.cmd -Engine podman
```

Use only one line. Normal stop keeps engine-specific named volumes containing
configuration, imported assets, sessions, temporary review data, caches, and
logs. Docker and Podman have separate storage. Export important results before
stopping; do not treat internal session storage as a backup.

See [Everyday Commands](Everyday-Commands) for the matching reopen command and
for a simple record of your choices.

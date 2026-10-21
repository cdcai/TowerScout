# RC1 Pilot / UAT Checklist

Use this checklist for controlled V1 RC1 package-path pilot testing.

## Supported Pilot Path

- Windows 11 AMD64.
- Docker Desktop as the primary runtime engine.
- CPU Application Package as the default package variant.
- CPU-default launch with `-Gpu off`.
- CUDA 12.1 Application Package only when support explicitly assigns GPU
  validation.
- Azure Maps or Google Maps provider key.
- `setup-towerscout.cmd` first-run setup with package-local assets imported
  with hash verification.
- Bounded public/non-sensitive detection area, preferably small and
  support-provided; the default RC1 smoke fixture is about 8 tiles.

Do not use the default checklist result to claim GPU acceleration,
Docker-Desktop-free Podman support, source-build support,
restricted-network/offline support, or large-AOI performance. The CPU
Application Package is expected to reject `-Gpu on`. If support assigns an
optional Podman or GPU validation track, use the assigned package variant and
record that track separately.

## Before You Start

Confirm you have:

- Exact GitHub release URL or release tag from support.
- Exact Model & Data Package filename from support.
- Smoke-test fixture from support: provider, public/non-sensitive location,
  expected tile range, and whether zero detections is acceptable.
- TowerScout CPU Application Package ZIP
  `towerscout-<release-version>-cpu.zip` and matching `.sha256` checksum file
  from the GitHub Release `Assets` section, unless support explicitly assigned
  the CUDA 12.1 Application Package.
- TowerScout CUDA 12.1 Application Package ZIP
  `towerscout-<release-version>-cuda121.zip` and matching `.sha256` checksum
  file only when support explicitly assigned GPU validation.
- TowerScout Model & Data Package ZIP and matching `.sha256` checksum file from
  the same GitHub Release `Assets` section.
- A provider key from the release owner or your organization.
- Docker Desktop installed and running.
- WSL 2 enabled for Docker Desktop's normal Windows Linux-container backend.
- PowerShell access.
- A modern browser.
- Outbound internet access for the container image, map provider, and geocoding provider.
- At least `15 GB` free disk space; `25 GB` is a better first-setup target.

Use the release page at `https://github.com/J-Schulein/TowerScout/releases`,
or the direct release URL support provides. Do not use GitHub's automatic
`Source code (zip)` or `Source code (tar.gz)` downloads for normal pilot setup.
Those are source snapshots, not a TowerScout Application Package. Do not use
the green GitHub `Code` button for the normal pilot install.

Do not send API keys, full `.env` files, private AOI screenshots, unredacted
logs, raw detection API responses, tile/map URLs, browser network traces, or
raw provider responses.

If you do not normally use PowerShell:

1. Open File Explorer.
2. Open the extracted TowerScout package folder.
3. Click the address bar, type `powershell`, and press Enter.
4. Paste one command at a time and press Enter.

Commands beginning with `.\` run scripts from the current folder.

Before launch, Docker Desktop should be open from the Windows Start menu and
show that it is running. If support asks you to check WSL/Docker readiness, run:

```powershell
wsl --status
wsl --list --verbose
docker --version
docker compose version
```

Expected result: WSL is installed, any listed Linux distribution uses version
`2`, and Docker commands print version information.

## Test Steps

1. Confirm the selected Application Package and Model & Data Package filenames
   are from the same release version. Create a new empty working folder, such
   as `C:\Users\<you>\Documents\TowerScoutUAT`, then copy the four downloaded
   release files from your `Downloads` folder into it. Normal testers should
   have the CPU Application Package. GPU testers should have the CUDA 12.1
   Application Package instead. Do not place both Application Package variants
   in the same UAT working folder unless support asks for comparison testing.
2. Extract only the TowerScout Application Package ZIP. Do not manually extract
   the Model & Data Package ZIP for the normal setup path. Extract the
   Application Package ZIP inside the `TowerScoutUAT` working folder.
3. Confirm the folder layout looks like this:

   ```text
   C:\Users\<you>\Documents\TowerScoutUAT\
     towerscout-<release-version>-cpu.zip
     towerscout-<release-version>-cpu.zip.sha256
     towerscout-<release-version>-assets-<asset-version>.zip
     towerscout-<release-version>-assets-<asset-version>.zip.sha256
     towerscout-<release-version>-cpu\
       setup-towerscout.cmd
   ```

   Expected result: the Model & Data Package ZIP and both `.sha256` files stay
   beside the extracted application folder or inside it. Do not put the Model &
   Data Package ZIP inside `assets\`.
4. Open PowerShell in the extracted package folder that contains
   `setup-towerscout.cmd`.
5. Run the guided setup:

   ```powershell
   .\setup-towerscout.cmd
   ```

   Expected result: setup reports disk, port, engine, Compose, checksum, and
   asset-layout checks; imports assets with hash verification; starts
   TowerScout; and opens `http://localhost:5000` or allows you to open that
   address manually. On the first launch, Docker may download the pinned
   TowerScout image from GHCR. This can take several minutes.

   If setup reports that more than one Model & Data Package ZIP was found,
   move old TowerScout ZIPs out of the folder and run setup again. If support
   asks for an explicit ZIP path, use the exact Model & Data Package filename:

   ```powershell
   .\setup-towerscout.cmd -AssetZip C:\Users\<you>\Documents\TowerScoutUAT\towerscout-<release-version>-assets-<asset-version>.zip
   ```

   Do not type the angle brackets from `<release-version>` or
   `<asset-version>`.

   Optional validation tracks only when assigned by support:

   ```powershell
   .\setup-towerscout.cmd -Engine podman
   .\setup-towerscout.cmd -Engine docker -Gpu auto
   .\setup-towerscout.cmd -Engine docker -Gpu on
   ```

   GPU validation requires the CUDA 12.1 Application Package. The CPU
   Application Package is expected to reject `-Gpu on`. If the CUDA package
   still reports `runtime.selected_device=cpu` during a GPU track, record the
   result as blocked and send the issue report form.

   If support assigned Podman and setup reports that no approved Compose
   provider is available, run the connected-host helper and retry setup:

   ```powershell
   .\scripts\install-podman-compose-provider.cmd -Apply
   ```

   If you use `-Engine podman`, keep using `-Engine podman` on later status,
   logs, stop, start, and import commands.

6. If support tells you to use the manual fallback instead of setup,
   extract the Model & Data Package into the package `assets/` folder.
   Expected layout:

   ```text
   assets\
     model_params\
     data\
     asset_manifest.v1.json
   ```

   If you see `assets\assets\model_params`, the files are nested one level too
   deep. Move the inner `model_params`, `data`, and `asset_manifest.v1.json`
   entries up one level before importing. If you are unsure, stop and ask
   support.

7. Manual fallback only: start TowerScout:

   ```powershell
   .\start.bat -Engine docker -Gpu off
   ```

   Expected result: PowerShell prints that TowerScout is starting with Docker,
   reports a readiness state, and opens `http://localhost:5000` or allows you
   to open that address manually. On the first launch, Docker may download the
   pinned TowerScout image from GHCR. This can take several minutes.

8. Manual fallback only: import assets:

   ```powershell
   .\scripts\import-assets.cmd -Engine docker -Source assets -VerifyHashes -RestartWaitSeconds 180
   ```

   Expected result: the import finishes without missing/corrupt asset errors
   and waits for TowerScout to respond after restart.

9. Open TowerScout in the browser if it does not open automatically.
10. Complete Setup Wizard with Azure Maps or Google Maps.
11. Open Settings Resource Links and confirm the package-local docs and source/license page load.
12. Run the owner-provided public bounded detection smoke. Use the provider,
    public/non-sensitive location, expected tile range, and zero-detection
    acceptability rule support provided before UAT starts. For the default RC1
    smoke fixture, use Azure Maps, search for `200 west st, New York, NY
    10282`, draw a `150 meter` circle, and expect about `8` tiles. Towers
    should be detected for this fixture. If no fixture was provided, stop and
    ask support before choosing your own area.
13. Confirm the detection workflow completes without a crash. For the default
    RC1 Azure fixture, expect a non-zero tower result. Exact counts may vary,
    but zero towers, no review-panel update, or a crash should be reported as
    `BLOCKED` or `FAIL`. For any future support-approved fixture, follow the
    zero-detection rule support provided for that fixture.
14. Confirm addresses/provider metadata appear when geocoding succeeds, or that a clear fallback appears when unavailable.
15. If requested, export CSV or KML.
16. Stop TowerScout through the package stop script or documented shutdown path.

   ```powershell
   .\scripts\stop.cmd -Engine docker
   ```

## Record The Result

Record:

- Date/time and time zone.
- Windows version.
- Runtime engine and version.
- Package version/folder name.
- Application Package variant: CPU or CUDA 12.1.
- Image digest shown by package metadata or launch output.
- Asset import result.
- Provider used.
- Detection fixture/AOI name.
- Tile count estimate if shown.
- Final result: `PASS`, `PASS_WITH_NOTES`, `BLOCKED`, or `FAIL`.

## If Something Fails

Use `TESTER-ISSUE-REPORT-CHECKLIST.txt` as the email/Teams issue report form.

Stop and contact support if Docker Desktop is not installed/approved/running
unless support explicitly assigned you the Podman path, WSL is unavailable or
reports version `1`, a checksum does not match, asset import reports
missing/corrupt/hash-failed files, readiness reports `fatal`, or provider
validation repeatedly fails after the key value has been checked. For a GPU
track, also stop and report the issue if support assigned the CUDA package but
readiness never reports `runtime.selected_device=cuda`.

Capture exact error text and the step where it failed. Screenshots are useful
only when they do not reveal API keys, private locations, tile/map URLs, raw
provider responses, or sensitive data.

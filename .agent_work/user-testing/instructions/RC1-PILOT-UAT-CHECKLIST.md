# RC1 Pilot / UAT Checklist

Use this checklist for controlled V1 RC1 package-path pilot testing.

## Supported Pilot Path

- Windows 11 AMD64.
- Docker Desktop as the primary runtime engine.
- CPU-default launch with `-Gpu off`.
- Azure Maps or Google Maps provider key.
- Package-local assets imported with hash verification.
- Bounded public/non-sensitive detection area, preferably 1-6 tiles.

Do not use this checklist to claim GPU acceleration, Docker-Desktop-free Podman support, source-build support, restricted-network/offline support, or large-AOI performance.

## Before You Start

Confirm you have:

- TowerScout Application Package ZIP and matching `.sha256` checksum file from
  the GitHub Release `Assets` section.
- TowerScout Model & Data Package ZIP and matching `.sha256` checksum file from
  the same GitHub Release `Assets` section.
- A provider key from the release owner or your organization.
- Docker Desktop installed and running.
- WSL 2 enabled for Docker Desktop's normal Windows Linux-container backend.
- PowerShell access.
- A modern browser.
- Outbound internet access for the container image, map provider, and geocoding provider.
- At least `15 GB` free disk space; `25 GB` is a better first-setup target.

Do not use GitHub's automatic `Source code (zip)` or `Source code (tar.gz)`
downloads for normal pilot setup. Those are source snapshots, not the RC1
Application Package.

Do not send API keys, full `.env` files, private AOI screenshots, or unredacted logs.

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

1. Confirm the Application Package and Model & Data Package filenames are from
   the same release version.
2. Compare each ZIP to its matching `.sha256` file before extracting it.
   Expected result: the SHA-256 hash printed by PowerShell matches the value in
   the matching checksum file. Uppercase/lowercase differences are okay.
3. Extract the TowerScout Application Package ZIP to a local folder.
4. Extract the Model & Data Package into the package `assets/` folder.
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
5. Open PowerShell in the package folder.
6. Start TowerScout:

   ```powershell
   .\start.bat -Engine docker -Gpu off
   ```

   Expected result: PowerShell prints that TowerScout is starting with Docker,
   reports a readiness state, and opens `http://localhost:5000` or allows you
   to open that address manually. On the first launch, Docker may download the
   pinned TowerScout image from GHCR. This can take several minutes.

7. Import assets:

   ```powershell
   .\scripts\import-assets.cmd -Engine docker -Source assets -VerifyHashes -RestartWaitSeconds 180
   ```

   Expected result: the import finishes without missing/corrupt asset errors
   and waits for TowerScout to respond after restart.

8. Open TowerScout in the browser if it does not open automatically.
9. Complete Setup Wizard with Azure Maps or Google Maps.
10. Open Settings Resource Links and confirm the package-local docs and source/license page load.
11. Run the owner-provided public bounded detection smoke. If one was not
    provided, use a non-sensitive approved area and keep the run small,
    preferably `1-6` tiles.
12. Confirm the detection workflow completes without a crash. Results may be
    zero or more detections, but the map and right-hand review panel should
    update consistently.
13. Confirm addresses/provider metadata appear when geocoding succeeds, or that a clear fallback appears when unavailable.
14. If requested, export CSV or KML.
15. Stop TowerScout through the package stop script or documented shutdown path.

   ```powershell
   .\scripts\stop.cmd -Engine docker
   ```

## Record The Result

Record:

- Date/time and time zone.
- Windows version.
- Runtime engine and version.
- Package version/folder name.
- Image digest shown by package metadata or launch output.
- Asset import result.
- Provider used.
- Detection fixture/AOI name.
- Tile count estimate if shown.
- Final result: `PASS`, `PASS_WITH_NOTES`, `BLOCKED`, or `FAIL`.

## If Something Fails

Use `TESTER-ISSUE-REPORT-CHECKLIST.txt`.

Stop and contact support if Docker Desktop is not installed/approved/running,
WSL is unavailable or reports version `1`, a checksum does not match, asset
import reports missing/corrupt/hash-failed files, readiness reports `fatal`, or
provider validation repeatedly fails after the key value has been checked.

Capture exact error text and the step where it failed. Screenshots are useful
only when they do not reveal API keys, private locations, or sensitive data.

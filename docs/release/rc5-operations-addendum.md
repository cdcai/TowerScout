# RC5 Operations Addendum

**Prepared for review**: October 19, 2026
**Candidate restrictions accepted**: October 19, 2026, under ADR-026
**Applies to**: `v0.1.3-rc5` Windows CPU and CUDA 12.8 packages

Read this with the Quick Start included in your download. It adds the short
Podman folder layout and Python selection steps established during testing.
The owner accepted these restrictions; distribution through fork review is
authorized and draft-PR review remains pending. This file
is a separate supplement; it is not inside the published RC5 ZIPs or their
in-app Help. See the [candidate notes](task105-candidate-notes.md) for exact
package hashes, image digests, tested scope, and qualification status.

## Before installation

Download the CPU or CUDA Application Package, shared Model & Data ZIP, and
their SHA-256 sidecars from the `v0.1.3-rc5` release. Verify every ZIP against
the release page and its sidecar before extraction. Preserve the original
downloads and their Windows downloaded-file markers. Use File Explorer
**Extract All**; keep the shared Model & Data ZIP unextracted beside the
application's extraction folder, as the shipped Quick Start describes.

These packages use unsigned PowerShell scripts behind supplied CMD/BAT
wrappers. Use them where your organization permits that path. Endpoints
requiring trusted signatures or organization allowlisting need their
administrator's approval. Follow the wrapper instructions; do not change
persistent execution policy or disable endpoint protection.

## Use a short local folder for Podman

RC5's provider installer can fail in a deeply nested folder with a generic
virtual-environment error. On the independent test computer, package paths
of 57 and 61 characters worked; a 108-character path failed. The exact
Windows/Python limit varies, so use a short local path.

For a new installation, choose a local folder such as
`C:\Users\<you>\Documents\TS`. Keep the original ZIPs and shared asset ZIP
there. Extract the selected Application Package into a short child folder
such as `PC` for Podman CPU or `PG` for Podman CUDA. The child folder must
contain `setup-towerscout.cmd` directly. If keeping Docker copies too, use
separate folders such as `DC` and `DG`.

The accepted RC5 support restriction is a package-root path of **80 characters
or fewer**. This is a conservative operating restriction, not a guarantee for
every Windows configuration. Avoid extra layers from synchronized or redirected
Documents folders. Use a permitted local folder and check its actual full path.
Open PowerShell in the extracted package folder and run:

```powershell
$PWD.Path
($PWD.Path).Length
```

If that length exceeds 80, choose a shorter folder and extract again before
installing the provider. If provider creation still fails, stop and contact
support. A machine-wide long-path setting change is not part of this procedure.

Keep an existing configured installation's folder and project identity stable.
Moving or renaming it can select different named volumes. For an existing
installation that needs relocation, export a dataset first and arrange the
move with support; retain the old volumes and configuration.

## Select Python 3.12 explicitly for Podman

The tested provider prerequisite is **64-bit Python 3.12**. Installing it does
not necessarily change what the command `python` selects. Docker does not
need this provider installation step.

If the Windows Python launcher is installed, run these commands from the
extracted package folder:

```powershell
py -3.12 --version
$tsPython312 = (& py -3.12 -c "import sys; print(sys.executable)").Trim()
& $tsPython312 --version
.\scripts\install-podman-compose-provider.cmd -Apply -Python "$tsPython312"
```

Confirm the version is 3.12 and the selected installation is 64-bit. If the
launcher cannot find 3.12, install the approved prerequisite or ask support
for its full executable path. The shipped helper accepts that full path as
the value of `-Python`; quote paths containing spaces. Do not substitute a
different Python version merely because it is first on PATH.

The installer verifies its pinned download and prints its selected provider.
A normal retry uses the same command without `-Force`. An interrupted attempt
can leave an unused staging folder; support can assess that folder separately.
After setup, use `status.cmd` to see TowerScout's selected provider. The global
`podman compose version` can report Docker Desktop's different provider.

## Run one selected engine

Quit the other desktop engine before starting the selected one. For Docker,
quit Podman Desktop and ensure its machine is stopped, then start Docker
Desktop and wait until ready. For Podman, quit Docker Desktop, then start the
recorded rootless Podman machine. The tested default machine can be started
with:

```powershell
podman machine start podman-machine-default
```

Run setup from the corresponding extracted package folder. Use only the row
matching your package, engine, and intended device:

| Profile | Setup command |
| --- | --- |
| Docker CPU | `.\setup-towerscout.cmd -Engine docker -Gpu off -Port 5000` |
| Docker CUDA | `.\setup-towerscout.cmd -Engine docker -Gpu on -Port 5000` |
| Podman CPU | `.\setup-towerscout.cmd -Engine podman -Gpu off -Port 5000` |
| Podman CUDA | `.\setup-towerscout.cmd -Engine podman -Gpu on -Port 5000` |

Follow the shipped GPU/CDI preparation for Podman CUDA before its setup row.
Each GPU profile must select CUDA; CPU fallback does not qualify it. If using
another port, repeat the same port in setup, start, status, TLS repair, and the
browser URL. Configure your approved Google/Azure keys through the app.

For example, daily Podman CPU use from its original package folder is:

```powershell
.\start.bat -Engine podman -Gpu off -Port 5000
.\scripts\status.cmd -Engine podman -Port 5000
.\scripts\stop.cmd -Engine podman
```

Use `-Engine docker` for Docker and `-Gpu on` for a CUDA start. Stop has no
GPU or port argument. Confirm readiness, assets, configured providers, pinned
digest, and the intended device before normal use.

## Recovery and saved work

- If desktop engines collide after login, quit both, then start only the
  selected engine. A normal Podman machine stop/start or Windows restart can
  restore its client connection. Preserve the recorded machine and volumes.
- Use shipped stop/start for application recovery. Do not use factory reset,
  volume pruning, machine deletion, or `compose down -v` as routine recovery.
- For provider certificate errors, follow the shipped guided TLS repair with
  an approved certificate and the same engine/device/port. Keep normal TLS
  verification enabled. The [package guide](../package-guide.md) describes it.
- Download a dataset before ending or changing a review session. After refresh
  or restart, the in-memory result view can be empty. Use **Restore Dataset**
  to reopen saved results and continue reviewing. Dataset export is not a full
  backup of API credentials, engine volumes, or installed model assets.
- Keep CSV/KML/dataset files under your organization's data-handling rules.
  Provider keys belong in the application setup, not chat or support reports.

## Known RC5 limitations

- The geocoding-limit warning is not displayed in the active workflow.
  Some detections can have coordinates without a street address.
- After ML detection, **Clear all** clears manual towers but may leave provider
  switching locked. Export current work before refreshing to switch providers;
  restore a saved dataset when returning to that work.
- Cancellation or an over-cap search may display misleading Network error
  wording. Wait until cancellation finishes before retrying. Cancelled results
  were excluded from the map/list in the tested browser flows.
- A late-cancelled server run can continue geocoding and use provider requests
  while its results are discarded by the browser.
- Separate **CSV**, **KML**, and **dataset** buttons were tested. Some window
  sizes clip the dataset label; map/search-box cosmetics and console warnings
  are also retained as known issues.
- On the independent host, large Podman downloads through a connection-closing
  scripted HTTP client were truncated by a transport path also reproduced with
  plain files. The same large dataset downloaded intact in Edge. Prefer the
  tested browser controls and report incomplete files to support.
- GPU free-memory telemetry contains a misleading label; it is not an actual
  free-device-memory measurement. Podman may also show a transient machine-state
  warning or write an internal diagnostic file under the package folder.

## Support and notices

Provide the candidate version, CPU/CUDA flavor, engine/provider versions,
readiness state, intended/selected device, and a short redacted error summary.
Keep raw logs, screenshots, exported data, provider responses, certificate
identities, and keys in approved private custody.

The package includes `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`,
`MODEL_LICENSES.md`, `DATA_LICENSES.md`, `PROVIDER_TERMS.md`, `SOURCE.txt`,
`SBOM.txt`, and its release manifest/checksums. Retain those notices with the
package and consult them for code, model, data, and provider terms.

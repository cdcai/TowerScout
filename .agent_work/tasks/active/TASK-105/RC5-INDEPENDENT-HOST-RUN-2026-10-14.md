# RC5 Independent-Host Run Sheet

**Task**: TASK-105

**Host**: `INDEP-HOST-01`, the separate Windows 11 NVIDIA machine used for the RC9 review

**Status**: Report and extracts reviewed; owner clarification received October 16.
See the [evidence intake](./RC5-INDEPENDENT-HOST-EVIDENCE-INTAKE-2026-10-16.md)
for credited results, methods, and unresolved dispositions. The checklist below
preserves the requested procedure; it is not a claim that every listed method
has an accompanying report.
The [October 19 closeout](RC5-QUALIFICATION-CLOSEOUT-2026-10-19.md) records
evidence reuse and known-limitations acceptance approved by the owner on
October 19 under ADR-026 in reviewed commit `33bd3a3`. The original procedure
below remains historical requested scope.
**Candidate**: immutable, non-Latest `v0.1.3-rc5` from accepted `main` `835cbb910573a931350c5b704d14496952d7ef87`

This sheet is for the independent validator. Follow the shipped Quick Start and
package guide for the actual install. Record deviations and failures; do not
convert an unavailable profile into a pass. Do not include provider keys,
locations, export contents, certificate identities, or raw logs in repository
evidence.

## Exact public inputs

Use a browser to download the six files from the fork's `v0.1.3-rc5` GitHub
prerelease: CPU and CUDA control ZIPs, their `.sha256` sidecars, the shared asset
ZIP, and its sidecar. Compare the downloaded files with the release page and
sidecars **before extraction**. Keep the original downloaded files and their
Mark-of-the-Web markers. Use File Explorer **Extract All** into distinct folders
with spaces in their paths; do not use a repository checkout or rebuilt ZIP as
the package under test.

| Input | Published SHA-256 |
| --- | --- |
| `towerscout-v0.1.3-rc5-cpu.zip` | `dfcc653eef4d0c9666604d6455797c123b757d92d4507ad1d451032f5cdd7a8f` |
| `towerscout-v0.1.3-rc5-cuda128.zip` | `c418e1948ed2719cd8c3678b612addccf468a139aafc97f99d3f4bd7676974d0` |
| `towerscout-v0.1.3-rc5-assets-towerscout-v1-assets-2026-05-05.zip` | `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb` |

The control packages must pin the CPU image digest
`sha256:833dbe0d0097ffcc9e52dcf39d64f25cf503c3c9ffc806f55c42b60e452845d5`
and CUDA image digest
`sha256:df0f30ac1bed4514d50c5b11eeac4ea64e38e6575bb209448fea4c53e5347890`.
Check each extracted package's release manifest and internal SHA256SUMS before
setup. Record hashes and pass/fail; retain raw files privately.

## Host and prerequisites

Record Windows build, GPU model, NVIDIA driver, Docker Desktop, Podman,
rootless machine/WSL, Windows PowerShell, PowerShell 7 if installed, and Python
versions. The claimed Podman path uses **64-bit Python 3.12** and the verified
package-local Compose provider. Check what `python` actually resolves to before
running the provider installer. If another Python is the default, use the
shipped helper's `-Python` option to select the installed Python 3.12 executable
and record that deviation. A Python 3.14 provider install is outside this
candidate's tested prerequisite; do not treat its failure as a profile pass.

The Windows package is unsigned. Use only the supplied process-scoped CMD
wrappers where local policy permits them; do not disable protection or change
persistent execution policy. Record any managed endpoint that requires a trusted
signature or organization allowlisting as outside the support claim.

## Four profile matrix

Run Docker first, then quit Docker Desktop before Podman. Never select **Reset
to factory defaults**, delete named volumes, or use a cleanup command that
could remove another installation. Use separate extractions, ports, project
names, and named volumes for each profile. Record the actual package-selected
Compose provider; a global `podman compose version` is not sufficient.

| Profile | Required device | Evidence to record |
| --- | --- | --- |
| Docker CPU | YOLO and EfficientNet on CPU | Fresh pull, asset import, pinned digest, readiness, model and browser workflow |
| Docker CUDA 12.8 | YOLO and EfficientNet on CUDA | Fresh or verified pull, CUDA kernel/architecture, pinned digest, readiness, model and browser workflow |
| Podman CPU | YOLO and EfficientNet on CPU | Rootless machine, Python 3.12, selected provider, asset import, digest, readiness, model and browser workflow |
| Podman CUDA 12.8 | YOLO and EfficientNet on CUDA | Absent-image first pull separated from CDI smoke, selected provider, digest, readiness, model and browser workflow |

For **each** profile, configure approved Google and Azure credentials through
Setup Wizard or Settings without recording the values. Prove normal TLS, map
load, a small bounded tile estimate and real detection with **each** provider,
result list/map review, public ZIP lookup, cancellation while running, then a
successful retry. Use the direct browser controls to download CSV, KML, and
dataset ZIP separately; verify the files exist and parse. Zero detections are
acceptable when the model run and UI behavior are otherwise proven. Download a
dataset, stop and relaunch through the shipped scripts, then verify both keys,
assets, selected device, named volumes, results/review state, another download,
and dataset restore. Reboot the host and repeat persistence/readiness checks
for all four profiles, with Docker Desktop closed when Podman runs.

Run the fixed 12-tile combined YOLO/EfficientNet fixture for both CPU and CUDA
images, confirm both models' selected devices and expected normalized outputs,
and record one warm-up plus three measured runs. Include the CPU image's
CUDA-required/unavailable negative and the controlled CUDA classifier failure
followed by a clean run. For F3/F4, exercise the shipped provider installer
from Windows PowerShell 5.1 and PowerShell 7 if available, including a safe
first failure and ordinary retry without `-Force` or manual directory deletion.
Record absent PowerShell 7 as a gap.

## Evidence and decision

For each cell record start/end UTC, exact downloaded hashes, image digest,
runtime/device, provider/TLS and asset status, model counts and fixture verdict,
browser result, export counts and validity, cancel/retry, ZIP lookup,
stop/relaunch, reboot, and any recovery needed. Keep detailed logs and exports
under the owner's private evidence custody. Publish only anonymous host ID,
versions, hashes, counts, sanitized pass/fail, and unresolved gaps. The RC9 run
does not qualify RC5. Any failed or missing required cell blocks Task-105 final
candidate acceptance until corrected and rerun.

# Releases And Supported Versions

> **Applies to:** [supported release v0.1.3-rc.1](https://github.com/cdcai/TowerScout/releases/tag/v0.1.3-rc.1). **Guide updated:** 2026-10-28.

The [official release record](https://github.com/cdcai/TowerScout/releases/tag/v0.1.3-rc.1)
identifies `v0.1.3-rc.1` as the supported Windows release. The original tag and
filenames identify the exact tested downloads. The `rc` name does not override
that support statement; keep downloaded filenames unchanged.

## What To Download

Download one CPU or CUDA 12.8 Application Package ZIP, the shared Model & Data
ZIP, and both checksum files. Before extraction, compare each ZIP's calculated
SHA-256 with its sidecar and the value displayed in the official release notes.

GitHub's automatic source archives and the optional source/license materials
are for source review and license obligations. They are not installation packages.

## Tested Configurations

**Both Docker and Podman are qualified and supported**, with CPU and NVIDIA
CUDA execution, for the tested Windows 11 configurations. The release reports
validation on two NVIDIA-equipped hosts covering both imagery providers,
exports, recovery, and restart persistence.

The scope of those results has these limits:

- CPU mode was tested explicitly on the two NVIDIA-equipped computers.
  CPU-only hardware was not separately qualified.
- Podman was tested on computers that also had Docker Desktop installed.
  A Podman installation without Docker Desktop installed was not separately
  qualified. Docker Desktop is closed while Podman runs; it is not the engine
  used for that TowerScout session.
- Signature-enforcing endpoints are outside the unsigned package's standard
  qualification.

These are limits of the recorded test coverage. See [Before You Install](Before-You-Install)
and the engine/GPU pages for preparation and checks. Export a dataset before
stopping; [restore it](Everyday-Commands#save-results-and-restore-a-review) if
live results do not reappear.

## Previous Versions And Future Updates

Earlier pilots remain historical. Use the supported release record to choose
installation files and to find exact source, image, checksum, and support
information.

New installation packages or container images need their own identities and
affected qualification. The support statement for these downloads does not
automatically apply to a new build.

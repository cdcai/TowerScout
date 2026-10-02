# Choose Your Setup

> **Audience:** End users and support. **Applies to:** The assigned release's
> support matrix. **Last reviewed:** 2026-10-02. **Publication state:** Local
> draft.

| Path | Who should use it | Required assignment |
| --- | --- | --- |
| Docker CPU | Most users; normal/default path | CPU Application Package; Docker Desktop/WSL 2 approved and running |
| Docker GPU | Eligible NVIDIA workstation where faster inference is required | CUDA 12.8 Application Package plus exact release-qualified driver/WSL/Docker NVIDIA validation |
| Podman CPU | Sites that explicitly choose Podman | CPU Application Package plus named rootless Podman machine and approved Compose provider |
| Podman GPU | Eligible NVIDIA workstation at a Podman site | CUDA 12.8 Application Package plus all Podman CPU prerequisites and release-qualified NVIDIA CDI validation |

## Selection Rules

- Choose Docker CPU unless support explicitly assigns something else.
- Use exactly one Application Package variant in the normal working folder.
- The CPU package rejects required GPU mode.
- A CUDA package selecting CPU does not pass a required-GPU test.
- Do not infer support from hardware capability alone. The authoritative
  release record must name the qualified combination.
- Docker and Podman use separate named volumes. Provider setup and imported
  assets do not automatically move between engines.

Next: [Install And First Run](Install-And-First-Run). For prerequisites, return
to [Before You Install](Before-You-Install).

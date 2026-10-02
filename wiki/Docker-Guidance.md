# Docker Guidance

> **Audience:** Docker users and Local IT. **Applies to:** Docker paths named in
> the assigned release. **Last reviewed:** 2026-10-02. **Publication state:**
> Local draft.

Docker Desktop with its WSL 2 Linux-container backend is TowerScout's default
Windows engine. The CPU Application Package with GPU mode off is the normal
path.

## Before Setup

- Confirm Docker Desktop is installed, approved/licensed for the site, open,
  and reports that its engine is running.
- Confirm WSL 2 and hardware virtualization meet the current Docker Desktop and
  local IT requirements.
- Confirm the release-specific free-disk and outbound-network requirements.
- Use the CPU package unless support assigned the Docker GPU path.

Follow `docs\docker-cpu-user-guide.md` or
`docs\docker-gpu-user-guide.md` in the exact package for commands.

## Lifecycle

First setup imports assets and creates persistent named volumes. Normal stop
and start may recreate the container/network while preserving those volumes.
Do not delete volumes during routine troubleshooting or upgrade preparation.

TowerScout should remain loopback-bound. If a port is in use, select an
approved alternative and pass it consistently to setup, start, import, TLS,
status, and stop helpers as documented by the release.

## Common Docker Stops

Stop and ask Local IT/support if Docker cannot start, WSL reports an unsupported
state, the image digest differs, the host port is not loopback-only, setup
reports missing/corrupt assets, or the selected device does not match the
assigned CPU/GPU path.

For NVIDIA use, continue with [NVIDIA GPU Setup](NVIDIA-GPU-Setup).

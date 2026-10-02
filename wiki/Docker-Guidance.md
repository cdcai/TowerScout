# Docker Guidance

> **Audience:** Users who choose Docker and their Local IT staff. **Applies
> to:** The next final Windows release. **Last reviewed:** 2026-10-02.
> **Publication state:** Local draft.

Docker Desktop is one supported way to run TowerScout. You may use CPU or a
compatible NVIDIA GPU.

## Install And Check Docker Desktop

1. Review Docker's current [Windows installation requirements and instructions](https://docs.docker.com/desktop/setup/install/windows-install/).
2. Confirm your organization's Docker Desktop licensing and installation
   policy. A managed computer may require Local IT approval.
3. Install Docker Desktop for Windows using its supported WSL 2 backend.
4. Restart Windows if the installer or WSL setup requests it.
5. Open Docker Desktop and wait until it reports that the engine is running.
6. Open ordinary Windows PowerShell and run:

```powershell
wsl --status
docker --version
docker compose version
```

Ready means all three commands succeed and Docker Desktop reports it is
running. TowerScout uses Linux containers; do not switch Docker to Windows
containers.

## Choose CPU Or GPU

- CPU: download the `-cpu` Application Package and use `-Gpu off`.
- NVIDIA GPU: first complete [NVIDIA GPU Setup](NVIDIA-GPU-Setup), download the
  `-cuda128` Application Package, and use `-Gpu on`.

Then follow [Install And First Run](Install-And-First-Run) or the complete
[Docker CPU guide](https://github.com/J-Schulein/TowerScout/blob/main/docs/docker-cpu-user-guide.md) / [Docker GPU guide](https://github.com/J-Schulein/TowerScout/blob/main/docs/docker-gpu-user-guide.md).

## Common Docker Symptoms

- **`docker` is not recognized:** close and reopen PowerShell after installing
  Docker Desktop. Confirm Docker Desktop is open.
- **Engine is unavailable:** start Docker Desktop and wait for it to finish
  starting.
- **WSL error:** follow Docker's WSL guidance and ask Local IT before changing
  Windows features.
- **Port 5000 is busy:** choose another port and record it; use that port on
  setup, start, status, and the browser address.
- **Organization blocks Docker Desktop:** do not bypass the policy. You may
  choose Podman only if that engine is permitted and its prerequisites can be
  met.

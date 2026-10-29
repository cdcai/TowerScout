# Docker Guidance

> **Applies to:** [supported release v0.1.3-rc.1](https://github.com/cdcai/TowerScout/releases/tag/v0.1.3-rc.1). **Guide updated:** 2026-10-28.

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
[Docker CPU guide](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/docs/docker-cpu-user-guide.md) / [Docker GPU guide](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/docs/docker-gpu-user-guide.md).

## Switch Between Docker And Podman

Run only the engine selected for the current TowerScout installation. Stop
TowerScout using that engine before switching. Follow the
[switching and recovery steps](Podman-Guidance#switch-between-docker-and-podman),
which preserve the separate named volumes used by each engine.

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
  choose Podman if it is permitted and its prerequisites can be met. Check
  the [qualification scope](Releases-And-Supported-Versions#tested-configurations)
  before treating a different installation layout as qualified.

# Choose Your Setup

> **Applies to:** [supported release v0.1.3-rc.1](https://github.com/cdcai/TowerScout/releases/tag/v0.1.3-rc.1). **Guide updated:** 2026-10-28.

Make three separate choices. Choosing one item does not choose the others.

For Docker, host Python is not required. The current tested Podman provider
setup requires explicitly selected **64-bit Python 3.12** and a package-root
path of **80 characters or fewer**. Follow [Podman Guidance](Podman-Guidance)
for the short-folder check, Python selection, and selected-provider verification.
These restrictions do not authorize moving an existing configured installation.

## 1. Choose Docker Or Podman

- **Docker Desktop:** Choose this if you want the shortest setup path or
  already use Docker Desktop. It runs in the background and provides the
  `docker` and `docker compose` commands.
- **Podman Desktop:** Choose this if it suits your workflow and is permitted
  by your organization. On Windows, Podman runs Linux containers inside a
  named virtual machine. TowerScout uses **rootless** Podman: the container
  engine runs as an ordinary Linux user inside that machine. A package-local
  **Compose provider** reads TowerScout's container configuration; its
  installer needs Python 3.12 for the tested path.

Run one engine at a time. Both are supported in CPU and NVIDIA GPU modes
within the [tested configurations](Releases-And-Supported-Versions#tested-configurations).
Docker and Podman keep separate TowerScout data. If you change engines later,
your settings and imported assets do not move automatically. Follow the
[switching guidance](Podman-Guidance#switch-between-docker-and-podman).

## 2. Choose CPU Or NVIDIA GPU

- **CPU:** Works without an NVIDIA GPU and uses the smaller `-cpu` Application
  Package. Choose CPU when you are unsure or prefer simpler setup.
- **NVIDIA GPU:** Uses the `-cuda128` Application Package and can be faster.
  Complete [NVIDIA GPU Setup](NVIDIA-GPU-Setup) to check the GPU architecture,
  Windows driver, WSL, and engine integration. Those checks do not qualify
  every untested hardware combination. GPU mode must report
  `selected_device=cuda`; silently using the CPU is not a successful GPU run.

The four valid combinations are Docker CPU, Docker GPU, Podman CPU, and Podman
GPU. Follow the matching package guide:

- [Docker CPU](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/docs/docker-cpu-user-guide.md)
- [Docker GPU](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/docs/docker-gpu-user-guide.md)
- [Podman CPU](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/docs/podman-cpu-user-guide.md)
- [Podman GPU](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/docs/podman-gpu-user-guide.md)

## 3. Choose Google Maps Or Azure Maps

- **Google Maps:** Requires a Google Cloud project, billing account, enabled
  Maps APIs, and one TowerScout-compatible API key.
- **Azure Maps:** Requires an Azure subscription, Azure Maps account, and one
  shared subscription key. TowerScout's current local package does not support
  Microsoft Entra ID authentication.

One provider is enough. You may configure both and switch between them later,
but each has separate billing, terms, quotas, and credential risks. Follow
[Google And Azure API Credentials](Google-And-Azure-API-Credentials) before
first use.

## Write Down Your Choice

Do not write a credential here.

| Item | Your choice |
| --- | --- |
| Container engine | Docker / Podman |
| Processing | CPU / NVIDIA GPU |
| Application Package | `-cpu` / `-cuda128` |
| Map provider | Google Maps / Azure Maps |
| Port | 5000 unless you intentionally choose another |

Next, follow [Google And Azure API Credentials](Google-And-Azure-API-Credentials).
If you already have a credential that meets the documented limitations, you
may continue directly to [Install And First Run](Install-And-First-Run).

# Choose Your Setup

> **Audience:** New users and Local IT. **Applies to:** The next final Windows
> release. **Last reviewed:** 2026-10-05. **Publication state:** Local draft.

Make three separate choices. Choosing one item does not choose the others.

## 1. Choose Docker Or Podman

- **Docker Desktop:** Choose this if you want the shortest setup path or
  already use Docker Desktop. It runs in the background and provides the
  `docker` and `docker compose` commands.
- **Podman Desktop:** Choose this if you prefer Podman or your organization
  permits Podman instead of Docker Desktop. On Windows it uses a named Linux
  virtual machine running without the Linux root administrator account
  (called **rootless**) and needs a package-local **Compose provider**, the
  helper that reads TowerScout's container configuration. The provider
  installer also needs Python 3.12 for the tested path.

You need only one engine. Docker and Podman keep separate TowerScout data. If
you change engines later, your settings and imported assets do not move
automatically.

## 2. Choose CPU Or NVIDIA GPU

- **CPU:** Works without an NVIDIA GPU and uses the smaller `-cpu` Application
  Package. Choose CPU when you are unsure or prefer simpler setup.
- **NVIDIA GPU:** Uses the `-cuda128` Application Package and can be faster.
  Choose it only when the exact GPU, Windows driver, WSL, and engine path meet
  the final release's tested requirements. GPU mode must report
  `selected_device=cuda`; silently using the CPU is not a successful GPU run.

The four valid combinations are Docker CPU, Docker GPU, Podman CPU, and Podman
GPU. Follow the matching package guide:

- [Docker CPU](https://github.com/J-Schulein/TowerScout/blob/main/docs/docker-cpu-user-guide.md)
- [Docker GPU](https://github.com/J-Schulein/TowerScout/blob/main/docs/docker-gpu-user-guide.md)
- [Podman CPU](https://github.com/J-Schulein/TowerScout/blob/main/docs/podman-cpu-user-guide.md)
- [Podman GPU](https://github.com/J-Schulein/TowerScout/blob/main/docs/podman-gpu-user-guide.md)

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

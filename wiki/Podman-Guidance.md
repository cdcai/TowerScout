# Podman Guidance

> **Audience:** Users who choose Podman and their Local IT staff. **Applies
> to:** The next final Windows release. **Last reviewed:** 2026-10-05.
> **Publication state:** Local draft.

Podman is one supported way to run TowerScout. On Windows it runs Linux
containers inside a named Podman machine. TowerScout's tested path uses the
rootless `podman-machine-default` connection and a package-local Compose
provider.

## Prepare Podman Before TowerScout Setup

1. Follow Podman Desktop's current [Windows installation instructions](https://podman-desktop.io/docs/installation/windows-install).
2. During onboarding, install Podman and create the default WSL 2 Podman
   machine. In Podman Desktop, this is under **Settings > Resources**.
3. If you use the command line instead, first run `podman machine list`. Only
   when no machine exists, open ordinary PowerShell and run:

   ```powershell
   podman machine init --now podman-machine-default
   ```

   Do not run `machine init` when that machine already exists.
4. Check the intended rootless machine and connection:

   ```powershell
   podman --version
   podman machine list
   podman system connection list
   ```

5. Install 64-bit Python 3.12 for the tested package-local Compose-provider
   path. Confirm `python --version` reports Python 3.12. Python is needed only
   by this provider installer, not by TowerScout inside its container.
6. Download and verify TowerScout, extract the Application Package, and then
   run this from that extracted folder:

   ```powershell
   .\scripts\install-podman-compose-provider.cmd -Apply
   podman compose version
   ```

The helper downloads a pinned, hash-checked provider into the package's tools
folder. TowerScout rejects Docker Desktop's bundled Compose executable for the
Podman path.

Ready means the intended machine is running, the selected connection is its
rootless user connection, and `podman compose version` succeeds with the
approved provider. TowerScout checks this target before changing containers.

## CPU Or NVIDIA GPU

- CPU: use the `-cpu` Application Package and `-Gpu off`.
- NVIDIA GPU: complete [NVIDIA GPU Setup](NVIDIA-GPU-Setup), including the CDI
  checks, then use the `-cuda128` package and `-Gpu on`.

Follow [Install And First Run](Install-And-First-Run) or the complete
[Podman CPU guide](https://github.com/J-Schulein/TowerScout/blob/main/docs/podman-cpu-user-guide.md) / [Podman GPU guide](https://github.com/J-Schulein/TowerScout/blob/main/docs/podman-gpu-user-guide.md).

After Windows restarts, Podman containers may remain stopped. Start the
machine, then use the matching TowerScout start command. Do not change the
global default connection or use a rootful connection merely to make an error
disappear.

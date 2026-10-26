# Podman Guidance

> **Audience:** Users who choose Podman and their Local IT staff. **Applies
> to:** The next final Windows release. **Last reviewed:** 2026-10-20.
> **Publication state:** Source-contained guidance; GitHub wiki publication is separate.

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

5. Arrange **64-bit Python 3.12** for the package-local Compose provider.
   TowerScout's application Python is inside its container; this host Python
   prerequisite is specific to the current Podman provider setup. Docker users
   do not need it. Installing 3.12 does not change which version `python` selects.
6. Download and verify the Application Package and shared Model & Data ZIP,
   then follow the short-folder and explicit Python steps below before setup.

## Use A Short Package Folder

For a new installation, keep the verified ZIPs in a short permitted local
folder such as `C:\Users\<you>\Documents\TS`. Extract the application into
`PC` (CPU) or `PG` (CUDA), with `setup-towerscout.cmd` directly in that child
folder. Leave the Model & Data ZIP unextracted one folder above it.

The full package-root path must be **80 characters or fewer**. This is an
accepted operating restriction, not a universal Windows limit or a guarantee.
Check the actual path, especially for redirected or synchronized folders.
Open PowerShell in the extracted package folder and run:

```powershell
$PWD.Path
($PWD.Path).Length
```

If it exceeds 80, extract into a shorter folder before installing the provider.
If provider installation still fails, stop and contact support. Do not change
machine-wide long-path or security settings. Keep configured installation
folders and project identities stable: relocation can select different named
volumes. Export a dataset and arrange a move with support; retain old volumes
and configuration.

## Select Python And Install The Provider

Run these commands **one at a time** from the extracted package folder. Stop
on any error or unless the version is 3.12 and bitness is 64 before running
the installer:

```powershell
py -3.12 --version
$tsPython312 = (& py -3.12 -c "import sys; print(sys.executable)").Trim()
& $tsPython312 -c "import sys, struct; print(sys.version); print(struct.calcsize('P') * 8)"
.\scripts\install-podman-compose-provider.cmd -Apply -Python "$tsPython312"
```

If `py -3.12` is unavailable, obtain the approved Python executable's full path
from Local IT, assign it to `$tsPython312`, and verify it with the same
version/bitness command. Quote paths containing spaces. Do not substitute a
different Python version. A normal retry uses the same command without `-Force`.

The helper downloads a pinned, hash-checked provider into the package's tools
folder. TowerScout rejects Docker Desktop's bundled Compose executable for
this path. After setup, check the provider TowerScout actually selected:

```powershell
.\scripts\status.cmd -Engine podman -Port 5000
```

Use your chosen port if different. Global `podman compose version` can report
a different provider and is not TowerScout's readiness check. Confirm the
intended rootless machine/connection, selected provider, assets and readiness;
for GPU, also confirm the intended CUDA device. These checks do not replace
a successful small detection workflow.

## CPU Or NVIDIA GPU

- CPU: use the `-cpu` Application Package and `-Gpu off`.
- NVIDIA GPU: complete [NVIDIA GPU Setup](NVIDIA-GPU-Setup), including the CDI
  checks, then use the `-cuda128` package and `-Gpu on`.

Follow [Install And First Run](Install-And-First-Run) or the complete
[Podman CPU guide](https://github.com/cdcai/TowerScout/blob/main/docs/podman-cpu-user-guide.md) / [Podman GPU guide](https://github.com/cdcai/TowerScout/blob/main/docs/podman-gpu-user-guide.md).

After Windows restarts, Podman containers may remain stopped. Start the
machine, then use the matching TowerScout start command. Do not change the
global default connection or use a rootful connection merely to make an error
disappear.

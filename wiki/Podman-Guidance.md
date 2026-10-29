# Podman Guidance

> **Applies to:** [supported release v0.1.3-rc.1](https://github.com/cdcai/TowerScout/releases/tag/v0.1.3-rc.1). **Guide updated:** 2026-10-28.

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

   Do not run `machine init` when that machine already exists. If the existing
   `podman-machine-default` is stopped, start it:

   ```powershell
   podman machine start podman-machine-default
   ```

   If it is already running, continue without starting it again. If a different
   machine exists, confirm the intended target with support before creating or
   switching anything.
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

For a new installation, keep the verified ZIPs in `Documents\TowerScout`.
Extract the application into `Documents\TowerScout\PC` (CPU) or
`Documents\TowerScout\PG` (CUDA), with `setup-towerscout.cmd` directly in
that child folder. Leave the Model & Data ZIP unextracted in
`Documents\TowerScout`, one folder above it. Use File Explorer's actual
Documents location, which may be redirected by your organization.

The full package-root path must be **80 characters or fewer**. This is an
accepted operating restriction, not a universal Windows limit or a guarantee.
Check the actual path, especially for redirected or synchronized folders.
Open PowerShell in the extracted package folder and run:

```powershell
$PWD.Path
($PWD.Path).Length
```

If it exceeds 80, stop before installing the provider and ask Local IT or
support to help select a permitted shorter location for the new installation.
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
[Podman CPU guide](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/docs/podman-cpu-user-guide.md) / [Podman GPU guide](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/docs/podman-gpu-user-guide.md).

After Windows restarts, Podman containers may remain stopped. Start the
machine, then use the matching TowerScout start command. Do not change the
global default connection or use a rootful connection merely to make an error
disappear.


## Switch Between Docker And Podman

Both engines are supported. Run only the one selected for the current
TowerScout session:

1. Save important results and a dataset, then stop TowerScout with its current
   engine using the matching command in [Everyday Commands](Everyday-Commands#stop-when-finished).
2. If switching from Docker to Podman, wait for Docker Desktop to finish any
   startup, then quit Docker Desktop before starting Podman Desktop.
3. Start the chosen engine and confirm its engine or intended machine is
   running before retrying TowerScout.
4. If both applications collide at Windows sign-in, quit both, then start the
   chosen one. If needed, restart Windows; do not reset either application.

Keep each engine's named volumes. **Reset to factory defaults**, machine reset,
and volume deletion can remove TowerScout data. Switching engines does not
migrate provider settings, imported assets, or reviews.

Use the versioned [Docker And Podman Coexistence procedure](https://github.com/cdcai/TowerScout/blob/412411786f24b3dddda02506ca44bf9b77f9874d/docs/package-guide.md#docker-and-podman-coexistence)
for volume-preserving recovery. See [tested configurations](Releases-And-Supported-Versions#tested-configurations)
for the scope of the two-host qualification.

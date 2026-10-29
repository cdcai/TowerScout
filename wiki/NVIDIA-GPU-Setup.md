# NVIDIA GPU Setup

> **Applies to:** [supported release v0.1.3-rc.1](https://github.com/cdcai/TowerScout/releases/tag/v0.1.3-rc.1). **Guide updated:** 2026-10-28.

GPU processing is optional. CPU mode remains a supported option
within the [tested configurations](Releases-And-Supported-Versions#tested-configurations).
Use the GPU path after checking the architecture, approved Windows driver,
WSL, and container integration below.

## Check Eligibility

1. Open **Task Manager > Performance** or **Device Manager > Display
   adapters** and record the exact NVIDIA GPU model.
2. In ordinary Windows PowerShell, run `nvidia-smi` and record the displayed
   driver version. Do not post its full output if it includes local machine
   details.
3. Confirm that your organization's approved Windows driver supports that GPU
   and CUDA on WSL 2. The release reports two-host qualification; it does not
   publish a complete GPU/driver compatibility matrix. Ask support about a
   different configuration rather than treating the architecture name as proof
   of qualification.

The CUDA 12.8 Application Package has a Volta-or-newer architecture
expectation. Maxwell and Pascal are unsupported and must use the CPU package.
An architecture expectation is not proof that every GPU/driver/engine
combination was tested.

## Windows And WSL Driver Rule

Install a current NVIDIA or computer-manufacturer Windows driver that supports
the exact GPU. NVIDIA documents that the Windows driver supplies CUDA to WSL.
Do not install a Linux NVIDIA display driver inside WSL; it can overwrite the
WSL-provided driver and break GPU access.

Official reference: [NVIDIA CUDA on WSL guidance](https://docs.nvidia.com/cuda/wsl-user-guide/index.html).

## Docker GPU

Start Docker Desktop and confirm `nvidia-smi` works on Windows. TowerScout's
`-Gpu on` setup performs the container check and must reach readiness with
`selected_device=cuda`. A host-only `nvidia-smi` result or CPU fallback is not
enough.

## Podman GPU And CDI

Prepare the rootless Podman machine and package-local Compose provider first.
From the extracted TowerScout Application Package, the documented GPU helper
is the one direct PowerShell-script exception:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\enable-podman-gpu.ps1 -VerifyOnly
```

If verification says CDI must be provisioned or refreshed, display the planned
commands without applying them:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\enable-podman-gpu.ps1 -DryRun
```

Review that plan with Local IT or support. Only after approval to install the
NVIDIA Container Toolkit and update CDI inside the intended Podman machine,
run the apply form:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\enable-podman-gpu.ps1
```

Then repeat `-VerifyOnly`. The check must expose `nvidia.com/gpu=all`. NVIDIA's
[CDI documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/cdi-support.html)
explains this device interface. Refresh and verify CDI again after a Windows
NVIDIA driver update.

The final TowerScout check is still `selected_device=cuda` from the running
application. If any rung fails, use the CPU package or resolve the stated
prerequisite; do not force a GPU architecture list or count CPU fallback as a
GPU success.

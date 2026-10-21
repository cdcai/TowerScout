# NVIDIA GPU Setup

> **Audience:** Users choosing GPU processing and their Local IT staff.
> **Applies to:** The next final Windows release. **Last reviewed:**
> 2026-10-02. **Publication state:** Local draft; the final tested GPU matrix
> belongs in the release record.

GPU processing is optional. CPU remains a supported choice on any otherwise
eligible computer. Use the GPU path only when the exact computer meets the
final release's tested requirements.

## Check Eligibility

1. Open **Task Manager > Performance** or **Device Manager > Display
   adapters** and record the exact NVIDIA GPU model.
2. In ordinary Windows PowerShell, run `nvidia-smi` and record the displayed
   driver version. Do not post its full output if it includes local machine
   details.
3. Compare the GPU and driver with the final TowerScout release's tested-
   support list.

The CUDA 12.8 Application Package has a Volta-or-newer architecture
expectation. Maxwell and Pascal are unsupported and must use the CPU package.
An architecture expectation is not proof that an unlisted GPU/driver/engine
combination was tested.

## Windows And WSL Driver Rule

Install a current NVIDIA or computer-manufacturer Windows driver that supports
the exact GPU. NVIDIA documents that the Windows driver supplies CUDA to WSL.
Do not install a Linux NVIDIA display driver inside WSL; it can overwrite the
WSL-provided driver and break GPU access.

Official reference: [NVIDIA CUDA on WSL guidance](https://docs.nvidia.com/cuda/cuda-quick-start-guide/).

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

If verification says CDI must be provisioned or refreshed, review the planned
change and run the apply form only on a computer where you are allowed to
install the NVIDIA Container Toolkit inside the Podman machine:

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

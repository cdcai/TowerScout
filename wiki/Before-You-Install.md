# Before You Install

> **Audience:** New users and Local IT. **Applies to:** The next final Windows
> release. **Last reviewed:** 2026-10-02. **Publication state:** Local draft.

Use this page to decide whether the computer is ready and what to do when a
requirement is missing. You do not need Docker and Podman; install one. You do
not need both map providers; prepare one.

## Computer Checklist

| Check | How to check | What to do if missing | Ready when |
| --- | --- | --- | --- |
| Windows 11, 64-bit x64 processor | Open **Settings > System > About**. Look for Windows 11 and **64-bit operating system, x64-based processor**. | TowerScout's final package does not support Windows on ARM, macOS, or Windows Server. Use a supported computer. | Windows reports Windows 11 and x64. |
| Memory | On the same About page, find **Installed RAM**. | The final release notes will state the tested minimum. Close other large applications or use another computer if the requirement is not met. | RAM meets the release note. |
| Free disk space | Open File Explorer, select **This PC**, and check the free space on the drive where the container engine stores data. | Free space or choose the CPU package. | Plan at least 15 GB for CPU or 35 GB for the CUDA package, plus room for exports. Use the final release note if it requires more. |
| Hardware virtualization and WSL 2 | Open ordinary Windows PowerShell and run `wsl --status`. | Follow Microsoft's [WSL installation guide](https://learn.microsoft.com/windows/wsl/install). Enabling Windows features or restarting may require Local IT or administrator approval. | `wsl --status` succeeds and the selected engine can start. |
| One container engine | Choose Docker or Podman on the next page. | Install only the engine you choose by following [Docker Guidance](Docker-Guidance) or [Podman Guidance](Podman-Guidance). | Its version command succeeds and its service or machine is running. |
| Internet access | TowerScout must reach GitHub Releases, GHCR, and the selected map provider. | Ask Local IT about proxy, firewall, or TLS-inspection requirements. Fully offline installation is not part of the standard release. | Downloads and provider validation are allowed. |
| One provider credential | Choose Google Maps or Azure Maps. | Follow [Google And Azure API Credentials](Google-And-Azure-API-Credentials). | You have one dedicated credential and understand its billing, restriction, and monitoring responsibilities. |

Docker's current Windows documentation lists WSL 2, 8 GB RAM, supported
Windows builds, and hardware virtualization among its requirements. Podman
Desktop also uses a Linux virtual machine on Windows. Always check the linked
vendor page because those requirements can change.

## Optional NVIDIA GPU Check

You may use CPU even when the computer has a GPU. Choose the GPU path only if:

- Windows Device Manager or Task Manager identifies a compatible NVIDIA GPU;
- `nvidia-smi` succeeds in PowerShell;
- the GPU and driver combination appears in the final TowerScout release's
  tested-support list; and
- the chosen engine passes its container GPU check.

The CUDA 12.8 package expects Volta-or-newer NVIDIA hardware, but architecture
alone is not a support claim. Maxwell and Pascal GPUs must use the CPU package.
If you are unsure, choose CPU. See [NVIDIA GPU Setup](NVIDIA-GPU-Setup).

## Unsigned Package And Managed Computers

The final package is intentionally unsigned. Its `.cmd` and `.bat` wrappers
start Windows PowerShell with a process-only execution-policy setting. They do
not change the permanent machine or user policy.

Stop before download or installation when:

- your organization does not permit the supplied unsigned wrappers;
- policy requires a trusted publisher, WDAC/AppLocker approval, or a separate
  allowlisting process;
- Local IT does not permit WSL, virtualization, the selected engine, or the
  required network destinations; or
- the Releases page does not yet identify a final supported version and its
  authoritative SHA-256 values.

Do not work around these conditions by changing permanent execution policy,
disabling endpoint protection, or turning off TLS verification.

Continue with [Choose Your Setup](Choose-Your-Setup).

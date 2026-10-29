# Before You Install

> **Applies to:** [supported release v0.1.3-rc.1](https://github.com/cdcai/TowerScout/releases/tag/v0.1.3-rc.1). **Guide updated:** 2026-10-28.

Use this page to decide whether the computer is ready and what to do when a
requirement is missing. Both Docker and Podman are supported; choose one
engine for each TowerScout run. Prepare a credential for one map provider.
The [tested configurations](Releases-And-Supported-Versions#tested-configurations)
explain the qualification scope, including the computers used for CPU and
Podman testing.

When this checklist says to open ordinary Windows PowerShell, select the
Windows **Start** button, type `Windows PowerShell`, and open **Windows
PowerShell**. Use the normal window; do not select **Run as administrator**
unless a later step explicitly requires it.

For Docker, host Python is not required. The current tested Podman provider
setup requires explicitly selected **64-bit Python 3.12** and a package-root
path of **80 characters or fewer**. Follow [Podman Guidance](Podman-Guidance)
for the short-folder check, Python selection, and selected-provider verification.
These restrictions do not authorize moving an existing configured installation.

## Computer Checklist

| Check | How to check | What to do if missing | Ready when |
| --- | --- | --- | --- |
| Windows 11, 64-bit x64 processor | Open **Settings > System > About**. Look for Windows 11 and **64-bit operating system, x64-based processor**. | TowerScout's final package does not support Windows on ARM, macOS, or Windows Server. Use a supported computer. | Windows reports Windows 11 and x64. |
| Memory | On the same About page, find **Installed RAM**. Compare it with the current [Docker](https://docs.docker.com/desktop/setup/install/windows-install/) or [Podman](https://podman-desktop.io/docs/installation/windows-install) requirements. | Ask Local IT or support if the computer cannot meet the chosen engine's requirements. TowerScout does not publish a separately validated RAM minimum; search size and processing mode affect memory use. | The engine's memory requirements are met; after installation, a small first search completes successfully. |
| Free disk space | Open File Explorer, select **This PC**, and check the free space on the drive where the container engine stores data. | Free space or choose the CPU package. | Plan at least 15 GB for CPU or 35 GB for the CUDA package, plus room for exports. Use the final release note if it requires more. |
| Hardware virtualization and Windows Subsystem for Linux 2 (WSL 2), which lets the engine run Linux containers | Open ordinary Windows PowerShell and run `wsl --status`. | Follow Microsoft's [WSL installation guide](https://learn.microsoft.com/windows/wsl/install). Enabling Windows features or restarting may require Local IT or administrator approval. | `wsl --status` succeeds and the selected engine can start. |
| One container engine | Choose Docker or Podman on the next page. | Prepare the chosen engine by following [Docker Guidance](Docker-Guidance) or [Podman Guidance](Podman-Guidance). | Its version command succeeds and its service or machine is running. |
| Internet access | Downloads use GitHub Releases and GitHub Container Registry (GHCR); the app and browser contact map services. Podman provider installation and GPU provisioning may need additional download sites. | Give Local IT the [network preparation checklist](Local-IT-Administrator-Guide#network-and-tls-inspection). Fully offline installation is not part of the standard release. | Required setup downloads and provider validation are allowed. |
| One provider credential | Choose Google Maps or Azure Maps. | Follow [Google And Azure API Credentials](Google-And-Azure-API-Credentials). | You have one dedicated credential and understand its billing, restriction, and monitoring responsibilities. |

Check the linked current vendor requirements for Windows builds, WSL, RAM, disk and virtualization. The supported TowerScout release record defines the tested application configurations; vendor support and application qualification are separate.

## Optional NVIDIA GPU Check

You may use CPU even when the computer has a GPU. Choose the GPU path only if:

- Windows Device Manager or Task Manager identifies a compatible NVIDIA GPU;
- `nvidia-smi` succeeds in PowerShell;
- an approved NVIDIA Windows driver supports the exact GPU and WSL 2; and
- the chosen engine passes the container GPU check described in
  [NVIDIA GPU Setup](NVIDIA-GPU-Setup).

The CUDA 12.8 package expects Volta-or-newer NVIDIA hardware, but architecture
alone does not extend the release's qualification to every GPU or driver.
Maxwell and Pascal GPUs must use the CPU package.
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
- the Releases page does not yet identify the supported version and its
  authoritative SHA-256 values.

Do not work around these conditions by changing permanent execution policy,
disabling endpoint protection, or turning off TLS verification.

Continue with [Choose Your Setup](Choose-Your-Setup).

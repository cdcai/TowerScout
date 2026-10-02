# TowerScout: Start Here

> **Audience:** New users and Local IT. **Applies to:** The next final Windows
> release. **Last reviewed:** 2026-10-02. **Publication state:** Local draft;
> do not treat this page as a published release announcement.

TowerScout is a local Windows application that helps a person review aerial or
satellite images for possible cooling towers. Its results are suggestions for
human review, not confirmed cooling-tower locations.

You make three independent choices:

1. **Docker or Podman** runs TowerScout in a protected container environment.
2. **CPU or a compatible NVIDIA GPU** performs image processing. CPU is the
   simplest choice. A supported GPU can be faster.
3. **Google Maps or Azure Maps** supplies the map and imagery. You need an
   account and usable credential for only one provider.

These are supported options, not paths assigned by the project team. Your
computer must meet the requirements for the options you choose. On a managed
computer, your organization may require Local IT approval before you install
software, enable Windows features, create cloud resources, or run unsigned
scripts.

## Recommended Reading Order

Follow these pages in order. You do not need to read every advanced page.

1. [Before You Install](Before-You-Install) — check the computer and learn
   what you may need to install.
2. [Choose Your Setup](Choose-Your-Setup) — choose an engine, processing mode,
   and map provider.
3. [Google And Azure API Credentials](Google-And-Azure-API-Credentials) — get
   one provider credential before first use.
4. [Install And First Run](Install-And-First-Run) — download, verify, extract,
   start, configure, and try TowerScout.
5. [Everyday Commands](Everyday-Commands) — save your choices and reopen or
   stop TowerScout later.
6. [Troubleshooting And Safe Support](Troubleshooting-And-Safe-Support) — use
   symptom-based help without sharing private data.

If your organization manages the computer, give Local IT the
[Local IT Administrator Guide](Local-IT-Administrator-Guide). Local IT approves
workstation and security changes; it does not choose Docker versus Podman, CPU
versus GPU, or Google versus Azure for you.

## Where Exact Release Information Lives

The [GitHub Releases page](https://github.com/J-Schulein/TowerScout/releases)
is the public download location. Its authoritative release record will identify the
supported version, exact files, SHA-256 values, tested configurations, and
known limitations.

The versioned `docs` folder included with the Application Package contains the
complete offline instructions. In-app Help comes from the same documentation
built into the matching container image. This Wiki helps you find the right
path, but the package must remain usable without the Wiki or a video.

## Important Safety Boundary

TowerScout's Windows PowerShell scripts are intentionally unsigned. Use the
supplied `.cmd` and `.bat` entrypoints. They use a temporary, process-only
PowerShell setting and do not change the computer's permanent execution
policy.

Do not disable Defender, antivirus/EDR, SmartScreen, WDAC, AppLocker, TLS
verification, or another organizational control. If policy blocks the
package, stop and ask Local IT whether this unsigned package is allowed. A
computer that requires trusted Authenticode signatures or organization-
specific allowlisting is outside the standard package's supported boundary.

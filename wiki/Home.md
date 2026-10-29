# TowerScout: Start Here

> **Applies to:** [supported release v0.1.3-rc.1](https://github.com/cdcai/TowerScout/releases/tag/v0.1.3-rc.1). **Guide updated:** 2026-10-28.

TowerScout is a local Windows application that helps a person review aerial or
satellite images for possible cooling towers. Its results are suggestions for
human review, not confirmed cooling-tower locations.

## Watch The Demo

**[Watch the TowerScout demo (about 6 minutes)](Demo-Video-And-Written-Walkthrough#watch-the-demo)**

See TowerScout in use, then follow the setup pages below. The demo page also
includes a written walkthrough.

## Choose Your Setup

You make three independent choices:

1. **Docker or Podman** runs TowerScout in a Linux container.
2. **CPU or a compatible NVIDIA GPU** performs image processing. CPU is the
   simplest choice. A supported GPU can be faster.
3. **Google Maps or Azure Maps** supplies the map and imagery. You need an
   account and usable credential for only one provider.

Choose among the options permitted by your organization and suitable for your
computer. On a managed computer, Local IT may prescribe an engine or provider
and may need to approve software installation, Windows features, cloud
resources, or unsigned scripts. See [Releases And Supported Versions](Releases-And-Supported-Versions#tested-configurations)
for the scope of the completed qualification.

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
[Local IT Administrator Guide](Local-IT-Administrator-Guide). Local IT confirms
which choices and workstation or security changes the organization permits.

## Where Exact Release Information Lives

The [GitHub Releases page](https://github.com/cdcai/TowerScout/releases)
is the public download location. The [supported v0.1.3-rc.1 record](https://github.com/cdcai/TowerScout/releases/tag/v0.1.3-rc.1) identifies the exact files, SHA-256 values, tested configurations and known limitations. Its original tag and filenames are retained to identify the tested downloads.

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

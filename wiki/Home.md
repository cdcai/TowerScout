# TowerScout Documentation: Start Here

> **Applies to:** The exact TowerScout release your release owner or support
> team assigns. **Last reviewed:** 2026-10-02. **Publication state:** Local
> draft; not yet published to the GitHub Wiki.

TowerScout is a local Windows browser application that helps identify likely
cooling towers in aerial and satellite imagery. Results require human review
and do not replace field verification or epidemiologic judgment.

## Choose Your Path

- **I am installing TowerScout:** start with [Before You Install](Before-You-Install),
  then [Choose Your Setup](Choose-Your-Setup) and
  [Install And First Run](Install-And-First-Run).
- **I already have TowerScout running:** use
  [Everyday Commands](Everyday-Commands) and the package's in-app User Guide.
- **I manage the workstation or security controls:** use the
  [Local IT Administrator Guide](Local-IT-Administrator-Guide).
- **I am troubleshooting with a user:** use
  [Troubleshooting And Safe Support](Troubleshooting-And-Safe-Support).
- **I maintain or hand off releases:** use
  [Releases And Supported Versions](Releases-And-Supported-Versions) and the
  release package's manifests/notices.

## Documentation Authority

This Wiki is the online navigation and evergreen guidance layer. It does not
replace the exact release materials:

1. The [GitHub release record](https://github.com/J-Schulein/TowerScout/releases)
   owns exact downloads, public SHA-256 values, image digests, qualified
   environments, and known limitations.
2. The `docs\` files inside the downloaded Application Package own exact
   install, setup, start, stop, recovery, and verification commands.
3. In-app Help is baked into the exact container image and must match the
   package/release guidance.
4. Package notices own license, source, model, data, and provider obligations.

If the Wiki and downloaded package disagree, stop and use the package/release
record for that exact version. Report the mismatch to the release owner.

## Default Support Path

The default path is Windows 11 AMD64, the CPU Application Package, Docker
Desktop with WSL 2, normal outbound internet access, and one site/user-owned
restricted Google Maps or Azure Maps key. GPU and Podman paths are assigned by
support only after release-specific workstation validation.

TowerScout's Windows PowerShell scripts are intentionally unsigned. Use the
supplied `.cmd`/`.bat` wrappers only where the user and organization permit
them. Do not disable protection or weaken persistent execution policy.

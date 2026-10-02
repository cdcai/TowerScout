# Troubleshooting And Safe Support

> **Audience:** End users and support. **Applies to:** The exact assigned
> release. **Last reviewed:** 2026-10-02. **Publication state:** Local draft.

Start with the shipped `docs\package-guide.md`; it owns release-specific
commands and recovery messages.

## Triage By State

| Observation | Meaning | Safe next step |
| --- | --- | --- |
| Not reachable | Engine/container may not be running or port may differ | Check package status, assigned engine, and exact port. |
| `setup_required` | App is running but no valid provider is configured | Complete Setup Wizard privately. |
| `degraded` | App can run but required assets or another component need attention | Use readiness component status and shipped recovery guidance. |
| `fatal` | A required path, manifest, asset, or ML runtime condition failed | Stop validation and contact support. |
| Provider TLS error | Container may not trust a site inspection CA | Use the support-directed dry-run/import path; never disable verification. |
| Required GPU selected CPU | GPU qualification failed closed or fell back | Stop; use the correct package/runtime or CPU path. |

## Common Safe Checks

- exact release tag/URL, filenames, local SHA-256, and published SHA-256;
- free disk and whether Docker/Podman plus its Compose provider are reachable;
- readiness state and redacted component status;
- engine, device policy, selected device, PyTorch flavor, and image digest;
- loopback binding, container health, and named-volume count; and
- whether normal stop/relaunch preserves readiness and volumes.

## Never Share Publicly

Provider keys, `.env`, raw logs, raw screenshots, private AOIs, provider URLs
or response bodies, browser console/network traces, certificate identities,
cached imagery, exported datasets, named-volume contents, and local user/host
identifiers require an approved private handling path.

## Do Not Use Destructive Recovery First

Normal stop/start preserves named volumes. Do not run broad engine prune,
remove volumes, delete Podman machines, or reset the package until evidence and
required data are backed up and the data owner explicitly approves the action.

If Windows security policy blocks the unsigned package, stop and contact Local
IT. Do not weaken protection or persistent execution policy.

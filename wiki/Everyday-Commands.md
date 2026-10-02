# Everyday Commands

> **Audience:** End users and first-line support. **Applies to:** The exact
> downloaded package. **Last reviewed:** 2026-10-02. **Publication state:**
> Local draft.

Run package commands from Windows PowerShell in the extracted Application
Package folder. Use the exact commands in that package's `docs\quick-start.md`
and `docs\package-guide.md`; options can differ by release.

| Task | Package entrypoint | Notes |
| --- | --- | --- |
| First setup | `setup-towerscout.cmd` | Verifies ZIPs/prerequisites, imports assets, and starts TowerScout. |
| Start/reopen | `start.bat` | Use after setup. Preserve the assigned engine, GPU mode, and non-default port. |
| Stop safely | `scripts\stop.cmd` | Removes the current container/network but preserves named volumes. |
| Status/readiness | `scripts\status.cmd` | Share only redacted state/component facts. |
| Logs | `scripts\logs.cmd` | Review privately and sanitize before sharing. |
| Asset import | `scripts\import-assets.cmd` | Use only with the verified Model & Data Package and release instructions. |
| TLS diagnosis/repair | Package TLS helper wrappers | Support-directed; preserve engine/GPU/port and never disable verification. |

## Normal Restart

Use the package stop wrapper, then start with the same explicit engine, GPU
mode, and port that support assigned. Named volumes preserve configuration,
assets, and applicable workflow state. Do not use engine-wide prune or volume
removal as a restart method.

## Keep Runtime Identity Consistent

- Use `-Engine podman` on every helper when support assigned Podman.
- Use the same non-default `-Port` on later helpers and launch commands.
- Use `-Gpu off` for the CPU path.
- Required GPU validation must report CUDA; silent CPU fallback is not a pass.

For a failure, see
[Troubleshooting And Safe Support](Troubleshooting-And-Safe-Support).

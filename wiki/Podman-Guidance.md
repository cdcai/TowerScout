# Podman Guidance

> **Audience:** Podman users and Local IT. **Applies to:** Support-assigned
> Podman paths named in the assigned release. **Last reviewed:** 2026-10-02.
> **Publication state:** Local draft.

Podman is a qualified alternative only when support assigns it. It is not an
automatic fallback for an unavailable Docker Desktop installation.

## Required Shape

- A named rootless Podman machine that is created and running.
- The package-approved, package-local Compose provider. Do not allow `podman
  compose` to delegate unintentionally to Docker Desktop Compose.
- The provider's documented Python prerequisite when installation is needed.
- Explicit target selection so commands cannot mutate the wrong machine or
  connection.
- For GPU, a release-qualified NVIDIA CDI device inside the selected machine.

Use the exact package's `docs\podman-cpu-user-guide.md` or
`docs\podman-gpu-user-guide.md`. Keep `-Engine podman` and the assigned machine
and Compose-provider settings consistent across setup, start, stop, status,
logs, import, and TLS helpers.

## Safety Rules

- Verify the selected connection is rootless and points to the intended
  machine before mutation.
- Treat Docker and Podman volumes as separate; do not assume provider config or
  assets exist in both.
- Do not start, delete, or recreate a different Podman machine to bypass a
  failed prerequisite.
- Preserve volumes across normal stop/relaunch.
- If the selected connection is unavailable or ambiguous, stop before setup.

For GPU prerequisites, see [NVIDIA GPU Setup](NVIDIA-GPU-Setup).

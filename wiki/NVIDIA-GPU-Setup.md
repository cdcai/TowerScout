# NVIDIA GPU Setup

> **Audience:** GPU users, Local IT, and support. **Applies to:** Only exact GPU
> combinations named in the assigned release record. **Last reviewed:**
> 2026-10-02. **Publication state:** Local draft.

GPU use is optional and support-assigned. Hardware capability alone does not
establish support.

## Eligibility

- Use the CUDA 12.8 Application Package, not the CPU package.
- The release record must name the exact GPU/driver/WSL/engine/toolkit support
  boundary. Follow any architecture exclusions.
- Install a current NVIDIA or OEM Windows production driver that supports the
  exact GPU. Do not install a Linux display driver inside WSL.
- Docker GPU requires the release-qualified Docker Desktop NVIDIA path.
- Podman GPU additionally requires a valid NVIDIA CDI device in the intended
  rootless Podman machine and the approved Compose provider.
- Plan the release-specific CUDA disk requirement; GPU images are materially
  larger than CPU images.

## Fail-Closed Rule

Readiness and independent inspection must report the assigned CUDA device and
exact digest. A CUDA launch that selects CPU, silently falls back, or reports an
unsupported compiled architecture is not a pass. Use the correct image or the
CPU package; do not mask the mismatch with environment overrides.

After a Windows NVIDIA driver update, revalidate Docker integration or refresh
and reverify Podman CDI as directed by the shipped guide before GPU launch.

The release's qualification procedure—not this Wiki page—owns exact commands
and the real CUDA kernel/model proof.
